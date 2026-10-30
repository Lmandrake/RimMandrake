#!/usr/bin/env python3
r"""ralph_c_runner.py — the `ralph_c` fixed-SHA live runner (harness step 12; Ralph design §2 AB_test and §3.1).

Design: design/RimMandrake/ralph_loop_design_2026-10-29.md §2 ("B tests that fixed SHA and nothing else") and §3.1
(runner S on SteveDesktop, runner A on Archmagi behind the idle rule, one queue, oldest first);
architecture_switch_harness_2026-10-29.md §1.5 and §1.2 step 8. Build ticket ARENA_LANE_BUILD_MINIMAL_LIST_ONLY.
Every live act goes through arena_lane.Lane, which logs it and enforces the lane rules.

THE PROTOCOL
  * A builder publishes a CANDIDATE: item, the exact sha, the mods to deploy, whether it carries C#, the profile
    (minimal | minimal+deps with a modset_builder tier) and the proof argv. Publishing again for the same item
    REPLACES the candidate: the old sha is stale from that moment.
  * The runner takes the OLDEST pending candidate, checks its clone out at that sha, and under one lane hold:
    reload (profile, deploy), canary, proof, one RESULT record, release with the owner's list restored.
  * Verdicts: pass | fail from the proof's exit code (0 / the candidate's fail_rc, default 1). A red canary
    before OR after the proof, any other exit code, a Python traceback with the fail code (the harness crashed, it
    did not judge), or a harness fault is `invalid`: never a fail, and the candidate stays pending (re-queued).
    The owner coming back to the machine is not an event: nothing checks for it and nothing aborts on it (owner
    2026-10-30: "I really, really need you to strip "when I come back to the machine" as an event for anything
    changing.").
  * A result counts only for its sha AND its publication (`cand`): republishing an old sha after another is a new
    candidate and is tested again. `record_result` refuses a result that is not the item's CURRENT candidate (a
    stale sha), and `lane_record` (what arena_gate reads, §1.2 step 8) refuses one whose sha is not the gate's
    head. An item with 3 failed live rounds is parked, never closed untested; a candidate with 3 invalid rounds
    is STUCK (out of the queue so it cannot starve the items behind it, never counted as a fail).
  * Two runners (S and A) share one queue: a runner CLAIMS a candidate (claims/<cand>, O_EXCL) before testing it;
    a claim older than CLAIM_TTL_S is a dead runner's and is taken over.

    python3 src/RimMandrake/Utils/arena/ralph_c_runner.py queue
    python3 src/RimMandrake/Utils/arena/ralph_c_runner.py publish --item X --sha S --builder A1 --mod M \
            [--has-dll] --profile minimal|minimal+deps [--tier T] -- <proof argv...>
    python3 src/RimMandrake/Utils/arena/ralph_c_runner.py run-one --lane steve|archmagi --clone DIR
    python3 src/RimMandrake/Utils/arena/ralph_c_runner.py record --item X --head S     (the gate's read)

Files: <arena>/ralph_c/candidates.jsonl (append-only), <arena>/ralph_c/results/<run_id>.json,
<arena>/ralph_c/logs/<run_id>.log. Written only by this harness code, never by an agent.
"""
from __future__ import annotations

import argparse
import contextlib
import fcntl
import json
import os
import re
import subprocess
import sys
import time
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arena_lane as L  # noqa: E402
import arena_safe_git as SG  # noqa: E402

ARM = "ralph_c"
MAX_FAIL_ROUNDS = 3
MAX_INVALID_ROUNDS = 3
CLAIM_TTL_S = 6 * 3600     # > the worst single run (deploys + 1800 s proof + quicktest + 2 probes + restore)
COUNTED = ("pass", "fail")


class StaleResult(Exception):
    """A result whose sha is not the item's current candidate, or not the head asked about. Refused, never counted."""


class CandidateRefused(Exception):
    pass


def rpaths(root: Path | None = None) -> dict:
    p = L.lane_paths(root)
    base = p["root"] / "ralph_c"
    p.update(rc=base, candidates=base / "candidates.jsonl", results=base / "results", logs=base / "logs",
             claims=base / "claims", lock=base / ".lock")
    return p


@contextlib.contextmanager
def _locked(p: dict):
    """One lock over publish and record_result, so no publish lands between a result's check and its write."""
    p["rc"].mkdir(parents=True, exist_ok=True)
    with open(p["lock"], "a") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)


def _read_jsonl(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def candidates(p: dict) -> list[dict]:
    return _read_jsonl(p["candidates"])


def current(p: dict) -> dict:
    """item -> its CURRENT candidate (the last one published; the file is append-only under a lock)."""
    out = {}
    for n, c in enumerate(candidates(p)):
        out[c["item"]] = dict(c, _n=n)        # file position = publish order (flock'd appends), not the 1 s ts
    return out


def results(p: dict) -> list[dict]:
    if not p["results"].is_dir():
        return []
    rows = [json.loads(f.read_text(encoding="utf-8")) for f in sorted(p["results"].glob("*.json"))]
    return sorted(rows, key=lambda r: (r.get("t_ns", 0), r.get("run_id", "")))


def publish(p: dict, item: str, sha: str, builder: str, mods: list[str], has_dll: bool, profile: str,
            tier: str | None, proof: list[str], flyer_flight: bool = False, trial: bool = True,
            fail_rc: int = 1, known_tiers=None) -> dict:
    if not item or not builder:
        raise CandidateRefused("item and builder are required")
    sha = (sha or "").strip().lower()
    if not L.same_sha(sha, sha):
        raise CandidateRefused("sha %r is not a commit sha (>= 10 hex)" % sha)
    if not mods:
        raise CandidateRefused("%s: no mod to deploy, so the canary can never see the candidate sha deployed" % item)
    if fail_rc in (0, None) or not isinstance(fail_rc, int):
        raise CandidateRefused("%s: fail_rc must be a non-zero int (0 is pass)" % item)
    if flyer_flight:
        raise CandidateRefused("%s: a flyer's flight is never live-tested (standing ruling)" % item)
    if profile not in L.PROFILES:
        raise CandidateRefused("%s: profile %r refused%s; allowed %s" % (
            item, profile, " in trial mode (owner 2026-10-29: minimal list only)" if trial else "",
            ", ".join(L.PROFILES)))
    if (profile == "minimal+deps") != bool(tier):
        raise CandidateRefused("%s: minimal+deps needs a --tier, minimal takes none" % item)
    if tier and known_tiers is not None and tier not in known_tiers:
        raise CandidateRefused("%s: tier %r is not a modset_builder tier" % (item, tier))
    if not isinstance(proof, list) or not proof or not all(isinstance(a, str) and a for a in proof):
        raise CandidateRefused("%s: proof must be a non-empty argv list" % item)
    with _locked(p):
        cur = current(p).get(item)
        if cur and L.same_sha(cur["sha"], sha) and cur["cand"] not in {x["cand"] for x in stuck(p)}:
            return cur                  # republishing the CURRENT sha is a no-op ...
        # ... unless it is STUCK: republishing it after the lane is fixed is the way back into the queue
        c = {"item": item, "sha": sha, "builder": builder, "mods": list(mods), "has_dll": bool(has_dll),
             "profile": profile, "tier": tier, "proof": list(proof), "fail_rc": fail_rc, "ts": L._now_iso(),
             "cand": uuid.uuid4().hex[:12]}
        L._append_jsonl(p["candidates"], [c])
    return c


def fail_rounds(p: dict, item: str) -> int:
    return sum(1 for r in results(p) if r["item"] == item and r["verdict"] == "fail")


def invalid_rounds(p: dict, cand: str) -> int:
    return sum(1 for r in results(p) if r.get("cand") == cand and r["verdict"] == "invalid")


def stuck(p: dict) -> list[dict]:
    """Current candidates with MAX_INVALID_ROUNDS invalid runs and no counted result: out of the queue."""
    done = {r.get("cand") for r in results(p) if r["verdict"] in COUNTED}
    return [c for c in current(p).values() if c["cand"] not in done and invalid_rounds(p, c["cand"]) >= MAX_INVALID_ROUNDS]


def pending(p: dict) -> list[dict]:
    """Current candidates with no counted (pass/fail) result for THIS publication, not parked, not stuck;
    oldest first (publish order = file position)."""
    done = {r.get("cand") for r in results(p) if r["verdict"] in COUNTED}
    out = [c for c in current(p).values()
           if c["cand"] not in done and fail_rounds(p, c["item"]) < MAX_FAIL_ROUNDS
           and invalid_rounds(p, c["cand"]) < MAX_INVALID_ROUNDS]
    return sorted(out, key=lambda c: c["_n"])


def claim(p: dict, cand: str, run_id: str) -> bool:
    """Take a candidate for one run (O_EXCL). A claim older than CLAIM_TTL_S belongs to a dead runner."""
    p["claims"].mkdir(parents=True, exist_ok=True)
    f = p["claims"] / cand
    for _ in range(2):
        try:
            fd = os.open(f, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, run_id.encode())
            os.close(fd)
            return True
        except FileExistsError:
            try:
                if time.time() - f.stat().st_mtime < CLAIM_TTL_S:
                    return False
                f.unlink()
            except FileNotFoundError:
                pass
    return False


def unclaim(p: dict, cand: str, run_id: str):
    """Drop OUR claim only: a claim another runner took over after the TTL is theirs."""
    f = p["claims"] / cand
    try:
        if f.read_text() == run_id:
            f.unlink()
    except FileNotFoundError:
        pass


def parked(p: dict) -> list[str]:
    return sorted(i for i in current(p) if fail_rounds(p, i) >= MAX_FAIL_ROUNDS)


def record_result(p: dict, res: dict) -> dict:
    """Write one result. Refuses (StaleResult) a sha that is not the item's current candidate."""
    if res.get("verdict") not in ("pass", "fail", "invalid"):
        raise ValueError("verdict %r" % res.get("verdict"))
    with _locked(p):
        cur = current(p).get(res.get("item"))
        if cur is None:
            raise StaleResult("no candidate was ever published for item %r" % res.get("item"))
        if not L.same_sha(res.get("sha"), cur["sha"]) or res.get("cand") != cur["cand"]:
            raise StaleResult("stale sha: result for %s at %s (publication %s), but the current candidate is %s (%s)"
                              % (res["item"], res.get("sha"), res.get("cand"), cur["sha"], cur["cand"]))
        res = dict(res, t_ns=time.time_ns())
        p["results"].mkdir(parents=True, exist_ok=True)
        f = p["results"] / ("%s.json" % res["run_id"])
        if f.exists():
            raise ValueError("result %s already written" % res["run_id"])
        tmp = f.with_suffix(".tmp")
        tmp.write_text(json.dumps(res, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        os.replace(tmp, f)
    return res


def lane_record(p: dict, item: str, head: str) -> dict:
    """What arena_gate reads (§1.2 step 8): the latest COUNTED result for `item` at exactly `head`.
    Raises StaleResult when the latest counted result is for another sha, or when `head` is not the current
    candidate; LookupError when there is none."""
    cur = current(p).get(item)
    if cur is None or not L.same_sha(cur["sha"], head):
        raise StaleResult("head %s is not %s's current live candidate (%s)" % (head, item, cur and cur["sha"]))
    counted = [r for r in results(p) if r["item"] == item and r["verdict"] in COUNTED]
    if not counted:
        raise LookupError("no counted live result for %s" % item)
    last = counted[-1]
    if not L.same_sha(last["sha"], head) or last.get("cand") != cur["cand"]:
        raise StaleResult("the latest live result for %s is for %s (publication %s), not head %s (%s)"
                          % (item, last["sha"], last.get("cand"), head, cur["cand"]))
    if not (last.get("canary") or {}).get("ok"):
        raise StaleResult("result %s has no green canary" % last["run_id"])
    return last


# ---------------------------------------------------------------- the run

def _crashed(txt) -> bool:
    """rc == fail_rc counts as a CRASH, not a fail, when the output ends in an uncaught Python exception that is not an
    assertion: the last `Traceback` block's final line names a non-AssertionError, and no unittest/pytest failure
    summary ("FAILED (" / "N failed") follows it. A proof that wants no guessing publishes its own --fail-rc."""
    t = txt or ""
    i = t.rfind("Traceback (most recent call last)")
    if i < 0:
        return False
    tail = t[i:]
    if "FAILED (" in tail or re.search(r"\b\d+ failed\b", tail):
        return False
    lines = [x for x in tail.splitlines() if x.strip()]
    exc = next((x for x in lines[1:] if re.match(r"^[A-Za-z_][\w.]*(Error|Exception|Exit|Interrupt)\b", x)), "")
    return bool(exc) and not exc.startswith(("AssertionError", "unittest."))


def run_one(p: dict, lane: str, driver, clone: str, runner_id: str | None = None) -> dict | None:
    """Test the oldest unclaimed pending candidate once. Returns the result written, or a dict with verdict
    `refused` / `stale` and nothing counted, or None when nothing is free to test."""
    run_id = "%s-%s-%s" % (ARM, lane, uuid.uuid4().hex[:10])
    c = next((x for x in pending(p) if claim(p, x["cand"], run_id)), None)
    if c is None:
        return None
    try:
        return _run_claimed(p, lane, driver, clone, c, run_id, runner_id or "ralph_c_runner@%s" % lane)
    finally:
        unclaim(p, c["cand"], run_id)


def _run_claimed(p, lane, driver, clone, c, run_id, runner_id):
    def ev(event, **kw):
        L.emit(p, dict(arm=ARM, lane=lane, run_id=run_id, task=c["item"], event=event, sha=c["sha"], **kw))

    def invalid(why):
        res["verdict"], res["why"] = "invalid", why
        if not res.get("_invalid_logged"):
            ev("invalid", detail={"why": why[:300]})
            res["_invalid_logged"] = True

    res = {"run_id": run_id, "item": c["item"], "sha": c["sha"], "cand": c["cand"], "lane": lane,
           "tester": runner_id, "builder": c["builder"], "profile": c["profile"], "tier": c["tier"],
           "mods": c["mods"], "has_dll": c["has_dll"], "proof": c["proof"], "canary": None, "verdict": "invalid",
           "logs": []}
    ev("test_start", detail={"tester": runner_id, "builder": c["builder"]})
    outcome = None                      # refused: nothing recorded
    try:
        ok, out = driver.checkout(clone, c["sha"])
        if not ok:
            raise L.LaneRefused("checkout of %s failed: %s" % (c["sha"], (out or "")[-200:]))
        # M1: a new fixed sha leaves no useful valid test on whatever is loaded (R2); a game that is down is a cold
        # start (R0). R1/R3 are the builder's loop's rules, not a fixed-sha runner's.
        rule = "R2" if driver.game_running() else "R0"
        with L.Lane(lane, ARM, driver, "fixed-sha test of %s@%s" % (c["item"], c["sha"][:10]), task=c["item"],
                    run_id=run_id, root=p["root"]) as lane_h:
            rev = lane_h.reload(c["profile"], c["tier"], rule=rule, mods=c["mods"], has_dll=c["has_dll"],
                                clone=clone, sha=c["sha"], why="new fixed sha: nothing valid left on the old deploy")
            res["launch_to_ready_s"] = rev["detail"]["launch_to_ready_s"]
            res["deploy"] = lane_h.deployed
            can = lane_h.canary(c["sha"])
            res["canary"] = {"ok": can["ok"], "problems": can["problems"]}
            res["game_version"] = can["facts"].get("game_version")
            res["save"] = lane_h.loaded_save or "quicktest"
            if not can["ok"]:
                res["verdict"], res["why"], res["_invalid_logged"] = "invalid", "canary red", True   # canary logged it
            else:
                rc, txt = driver.run_proof(c["proof"], clone)
                p["logs"].mkdir(parents=True, exist_ok=True)
                log = p["logs"] / ("%s.log" % run_id)
                log.write_text(txt or "", encoding="utf-8")
                res["logs"].append(str(log))
                res["proof_rc"] = rc
                after = lane_h.canary(c["sha"])   # the world the proof ran in must still be valid when it ends
                res["canary_after"] = {"ok": after["ok"], "problems": after["problems"]}
                fail_rc = c.get("fail_rc", 1)
                if not after["ok"]:
                    res["verdict"], res["why"], res["_invalid_logged"] = "invalid", "canary red after the proof", True
                elif rc == 0:
                    res["verdict"] = "pass"
                elif rc == fail_rc and _crashed(txt):
                    invalid("proof exit %d after an uncaught non-assertion exception: the harness crashed, it did "
                            "not judge" % rc)
                elif rc == fail_rc:
                    res["verdict"] = "fail"
                else:
                    invalid("proof exit %r is neither pass (0) nor fail (%r)" % (rc, fail_rc))
    except L.RestoreFailed as e:
        res["restore_failed"] = str(e)          # the verdict stands; the lane is flagged (the live_release says error)
        if isinstance(e.__context__, Exception) and res["verdict"] == "invalid":
            invalid("%s (and the restore failed)" % e.__context__)
    except L.LaneRefused as e:
        if res["canary"] is None and "take refused" in str(e):
            outcome = {"verdict": "refused", "why": str(e)}       # the lane was busy: not this candidate's round
        else:
            invalid(str(e))
    except (Exception, SystemExit) as e:  # noqa: BLE001 - a harness fault is an invalid round, never a lost run
        invalid("harness fault: %s: %s" % (type(e).__name__, e))
    res.pop("_invalid_logged", None)
    if outcome is not None:
        ev("test_end", verdict=outcome["verdict"], detail={"tester": runner_id, "builder": c["builder"],
                                                           "why": outcome["why"][:300]})
        return dict(outcome, item=c["item"], sha=c["sha"], restore_failed=res.get("restore_failed"))
    res["ts"] = L._now_iso()
    try:
        record_result(p, res)
    except StaleResult as e:
        ev("invalid", detail={"why": "stale sha, result refused: %s" % e})
        ev("test_end", verdict="stale", detail={"tester": runner_id, "builder": c["builder"]})
        return dict(res, verdict="stale", why=str(e))
    ev("test_end", verdict=res["verdict"], detail={"tester": runner_id, "builder": c["builder"],
                                                   "canary_ok": bool(res["canary"] and res["canary"]["ok"])})
    return res


def _safe(clone, args, timeout, transport=False):
    """-> (returncode, stdout+stderr) like L._sh, through arena_safe_git."""
    try:
        p = SG.git_run(clone, *args, transport=transport, capture_output=True, text=True, timeout=timeout,
                       encoding="utf-8", errors="replace")
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except (OSError, subprocess.SubprocessError) as e:
        return 99, "%s: %s" % (type(e).__name__, e)


class RunnerDriver(L.RealDriver):
    """RealDriver plus the two runner-only acts. UNPROVEN LIVE (owed)."""

    def checkout(self, clone, sha):
        """Fetch, detach at sha, then remove untracked files a previous proof left (git clean -fd: untracked only,
        ignored build output stays). Refused on a seat's own clone: the runner tests in a clone of its own."""
        if Path(clone).resolve() == L.REPO.resolve() or Path(clone).name in ("bench", "foundry"):
            return False, "clone %s is a seat clone; ralph_c tests only in its own clone" % clone
        # the clone's .git is written by the build helper that works in it: every git call here ignores replace refs and
        # grafts and runs none of its hooks / filters / fsmonitor / ssh command (arena_safe_git)
        attr = Path(clone) / ".git" / "info" / "attributes"
        if attr.exists() and attr.stat().st_size:
            return False, "refused: %s is non-empty (it changes what a checkout writes)" % attr
        rc, out = _safe(clone, ["fetch", "-q", "--upload-pack=git-upload-pack", "origin"], 300, transport=True)  # option beats a repo-local remote.origin.uploadpack
        if rc != 0:
            return False, out
        rc, out2 = _safe(clone, ["checkout", "-q", "--detach", sha], 120)
        if rc != 0:
            return False, out + out2
        rc, out3 = _safe(clone, ["clean", "-fdq"], 120)
        return rc == 0, out + out2 + out3

    def run_proof(self, argv, clone):
        rc, out = L._sh(list(argv), timeout=1800, cwd=clone)
        return rc, out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("queue")
    pb = sub.add_parser("publish")
    pb.add_argument("--item", required=True)
    pb.add_argument("--sha", required=True)
    pb.add_argument("--builder", required=True)
    pb.add_argument("--mod", action="append", default=[])
    pb.add_argument("--has-dll", action="store_true")
    pb.add_argument("--profile", required=True)
    pb.add_argument("--tier")
    pb.add_argument("--flyer-flight", action="store_true")
    pb.add_argument("--fail-rc", type=int, default=1, help="the proof's FAIL exit code (default 1)")
    pb.add_argument("proof", nargs=argparse.REMAINDER)
    ro = sub.add_parser("run-one")
    ro.add_argument("--lane", required=True, choices=sorted(L.LANES))
    ro.add_argument("--clone", required=True)
    rc = sub.add_parser("record")
    rc.add_argument("--item", required=True)
    rc.add_argument("--head", required=True)
    a = ap.parse_args(argv)
    p = rpaths()
    try:
        if a.cmd == "queue":
            for c in pending(p):
                print("%s  %s  %s  %s%s" % (c["ts"], c["item"], c["sha"][:10], c["profile"],
                                            " " + c["tier"] if c["tier"] else ""))
            for i in parked(p):
                print("PARKED (%d failed live rounds)  %s" % (MAX_FAIL_ROUNDS, i))
            for c in stuck(p):
                print("STUCK (%d invalid rounds)  %s  %s" % (MAX_INVALID_ROUNDS, c["item"], c["sha"][:10]))
        elif a.cmd == "publish":
            proof = a.proof[1:] if a.proof[:1] == ["--"] else a.proof
            print(json.dumps(publish(p, a.item, a.sha, a.builder, a.mod, a.has_dll, a.profile, a.tier, proof,
                                     a.flyer_flight, fail_rc=a.fail_rc,
                                     known_tiers=RunnerDriver().known_tiers() if a.tier else None), sort_keys=True))
        elif a.cmd == "run-one":
            print(json.dumps(run_one(p, a.lane, RunnerDriver(), a.clone), sort_keys=True, default=str))
        elif a.cmd == "record":
            print(json.dumps(lane_record(p, a.item, a.head), sort_keys=True))
    except (CandidateRefused, StaleResult, LookupError, L.LaneRefused) as e:
        print("REFUSED: %s" % e, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
