#!/usr/bin/env python3
"""relentless_live_round.py -- one game-up sitting of the live tier: every built item that has a written proof for a
live criterion it owes gets relentless_live.run(), several per sitting (RA_S09_LIVE_WIRE_ONE_REAL_LEAF).

    python3 src/RimMandrake/rimflow/relentless_live_round.py eligible        # what a round would try, and why not the rest
    python3 src/RimMandrake/rimflow/relentless_live_round.py round [--max 6]

The supervisor (relentless.py tick, live_tick) starts `round` detached, at most one at a time, every live.round_every_s.

WHERE A PROOF COMES FROM: a line in the item's prose (infrastructure/state/items/<ID>.md), one per criterion:

    live-proof A2: python3 src/RimMandrake/Utils/live_log_check.py --absent RUT_PaleMoss

Nothing here turns a criterion's English into a proof: a guessed proof would pass criteria nobody proved. A criterion with
no line is counted as `no proof` in `eligible` and waits for one.

A round, in order:
  1. no running game -> one rounds.jsonl row and nothing else (no bridge, no plan);
  2. candidates: built/validated, built sha, an owed criterion at a live level with a live-proof line; FlowWorks and Gimme
     Some Slack items are FOUNDRY's (flowworks_lane.json, or a FlowWorks/GimmeSomeSlack game file) and are skipped;
  3. history (live/runs.jsonl): a criterion already PASS, FAIL or REFUSED on the same built sha is not run again (a FAIL
     stands until a new build); UNMEASURED retries after live.unmeasured_retry_s;
  4. each run is relentless_live.run(): flyer and forbidden-proof refusal, files changed since the build, the deploy plan
     (args derived from the item's own mods, one plan per args per round), the game started after the deploy, the bridge
     taken with --idle-ok and released at once after each proof, the verdict a `rimflow verify` on the built sha;
  5. the round stops early when the game went away or the bridge is held by someone else.
"""
import argparse
import fcntl
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless_live as L     # noqa: E402

PROOF_LINE = re.compile(r"^\s*(?:[-*]\s+)?`?live-proof\s+(?P<cid>[A-Z]{1,3}\d{1,3})\s*:\s*(?P<cmd>\S.*?)`?\s*$")
FOUNDRY_MODS = ("FlowWorks", "GimmeSomeSlack")
DEFAULTS = {"round_max": 6, "unmeasured_retry_s": 6 * 3600, "round_every_s": 1800}
STOP = ("no running game to test", "bridge not taken")


def rules(r):
    out = dict(DEFAULTS)
    out.update((r or {}).get("live") or {})
    return out


def proof_lines(prose):
    """An item's prose -> {criterion id: proof command}. A second line for the same criterion is ignored (first wins)."""
    out = {}
    for line in (prose or "").splitlines():
        m = PROOF_LINE.match(line)
        if m and m.group("cid") not in out:
            out[m.group("cid")] = m.group("cmd").strip()
    return out


def history(rows):
    """runs.jsonl rows -> {(item, criterion): the newest row}."""
    out = {}
    for row in rows:
        if row.get("item") and row.get("criterion"):
            out[(row["item"], row["criterion"])] = row
    return out


def due(last, sha, now, retry_s):
    """-> None when this criterion may run now, else why not. `last` is its newest runs.jsonl row or None."""
    if not last or last.get("sha") != sha:
        return None
    if last.get("outcome") in ("PASS", "FAIL", "REFUSED"):
        return "judged on this build"
    try:
        at = time.mktime(time.strptime(last.get("at", ""), "%Y-%m-%dT%H:%M:%SZ")) - time.timezone
    except ValueError:
        return None
    if now - at < retry_s:
        return "unmeasured lately"
    return None


def candidates(items, prose_of, foundry_seat, hist, now, retry_s):
    """-> (todo [(item id, criterion, proof, built sha)], counts {why skipped: n}). Pure apart from prose_of/foundry_seat.
    `items` are ledger items in relentless_live.Fx.item's shape (criteria already whole or marked cut)."""
    todo, counts = [], {}

    def skip(why):
        counts[why] = counts.get(why, 0) + 1

    for it in items:
        if it["state"] not in L.TESTABLE or not it.get("built_sha"):
            continue
        crit = {c["id"]: c for c in it.get("criteria") or []}
        owed = [c for c in it.get("outstanding") or [] if c in crit and crit[c]["level"] in L.LIVE_LEVELS]
        if not owed:
            continue
        if foundry_seat(it["id"]):
            skip("FOUNDRY's lane")
            continue
        proofs = proof_lines(prose_of(it["id"]))
        for cid in owed:
            if cid not in proofs:
                skip("no proof")
                continue
            why = due(hist.get((it["id"], cid)), it["built_sha"], now, retry_s)
            if why:
                skip(why)
                continue
            todo.append((it["id"], cid, proofs[cid], it["built_sha"]))
    return todo, counts


def deploy_args(mods, folded):
    """The item's mod folders -> deploy_custom_mods.py plan arguments covering each. A folder folded into the composed
    biomes mod is planned through --compose biomes, the rest beside it with --with, or alone with --mod."""
    mods = sorted(set(mods))
    if any(m in folded for m in mods):
        return " ".join(["--compose biomes"] + ["--with %s" % m for m in mods if m not in folded])
    return " ".join("--mod %s" % m for m in mods)


class RoundFx(L.Fx):
    """relentless_live.Fx plus what a round needs: every item, one plan per args, the lane and the compose manifest."""

    def __init__(self, *a, **kw):
        L.Fx.__init__(self, *a, **kw)
        self._plans = {}

    def items(self):
        import model
        out = []
        for it in model.replay(model.read()).items.values():
            if it.state not in L.TESTABLE:
                continue
            out.append({"id": it.id, "state": it.state, "built_sha": it.built_sha, "title": it.title or "",
                        "criteria": [L.whole_criterion(c, self.prose(it.id)) for c in it.criteria or []],
                        "outstanding": list(it.outstanding or [])})
        return out

    def deploy_plan(self, args, timeout):
        if args not in self._plans:
            self._plans[args] = L.Fx.deploy_plan(self, args, timeout)
        return self._plans[args]

    def foundry_seat(self, item_id):
        if not hasattr(self, "_lane"):    # priority uses relative imports: load it as the package does, read the lane once
            import importlib
            sys.path.insert(0, os.path.dirname(HERE))
            self._prio = importlib.import_module("rimflow.priority")
            self._lane = self._prio.flowworks_lane()
        return self._prio.flowworks_seat(item_id, self._lane)

    def folded(self):
        sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
        import deploy_custom_mods
        return deploy_custom_mods.folded()

    def mods_of(self, sha):
        return sorted({m for m, _ in L.game_files(self.touched(sha), self.shippable)})


def read_rows(path):
    rows = []
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    rows.append(json.loads(line))
                except ValueError:
                    continue
    return rows


def plan(fx, root, r, now):
    """-> (todo, counts) for this moment. Read-only."""
    lr = rules(r)
    hist = history(read_rows(os.path.join(root, "live", "runs.jsonl")))
    return candidates(fx.items(), fx.prose, fx.foundry_seat, hist, now, lr["unmeasured_retry_s"])


def run_round(fx, root, r, now=None, max_items=None, run=L.run):
    """One sitting. -> the round's summary row (also appended to <root>/live/rounds.jsonl)."""
    now = time.time() if now is None else now
    lr = rules(r)
    os.makedirs(os.path.join(root, "live"), exist_ok=True)
    summary = {"at": L.iso(now), "runs": []}

    def done(why):
        summary["why"] = why
        with open(os.path.join(root, "live", "rounds.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(summary, sort_keys=True) + "\n")
        return summary

    if fx.game_started() is None:
        return done("no running game")
    todo, counts = plan(fx, root, r, now)
    summary.update(eligible=len(todo), skipped=counts)
    folded = None
    for item_id, cid, proof, sha in todo[:max_items or lr["round_max"]]:
        try:
            mods = fx.mods_of(sha)
        except ValueError as e:
            summary["runs"].append({"item": item_id, "criterion": cid, "outcome": "UNMEASURED", "why": str(e)[:200]})
            continue
        if any(m in FOUNDRY_MODS for m in mods):
            summary["runs"].append({"item": item_id, "criterion": cid, "outcome": "SKIPPED",
                                    "why": "FOUNDRY's lane: %s" % ", ".join(m for m in mods if m in FOUNDRY_MODS)})
            continue
        if folded is None:
            folded = fx.folded()
        row = run(fx, root, item_id, cid, proof, deploy_args(mods, folded), r, now=time.time())
        summary["runs"].append({k: row.get(k) for k in ("item", "criterion", "outcome", "why", "sha")})
        if row["outcome"] == "UNMEASURED" and any(row.get("why", "").startswith(s) for s in STOP):
            return done("stopped: %s" % row["why"][:200])
    return done("done")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("eligible", help="what a round would try now, and the counts of what it would skip")
    p = sub.add_parser("round", help="one sitting: run every due criterion that has a proof, up to --max")
    p.add_argument("--max", type=int, default=None)
    a = ap.parse_args(argv)
    with open(os.environ.get("RELENTLESS_RULES") or L.RULES, encoding="utf-8") as f:
        r = json.load(f)
    root = os.environ.get("RELENTLESS_ROOT") or "/home/mandrake/rm/relentless"
    fx = RoundFx(seat=r.get("seat") or "BENCH")
    if a.cmd == "eligible":
        todo, counts = plan(fx, root, r, time.time())
        print(json.dumps({"eligible": [list(t[:3]) for t in todo], "skipped": counts}, indent=1, sort_keys=True))
        return 0
    os.makedirs(os.path.join(root, "live"), exist_ok=True)
    with open(os.path.join(root, "live", "round.lock"), "w") as lk:
        try:
            fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print("a round is running")
            return 0
        print(json.dumps(run_round(fx, root, r, max_items=a.max), indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
