#!/usr/bin/env python3
"""selftest_artpipe_state.py — state_dir resolver, collect and migrate, on temp dirs only."""
from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import artpipe_state as AS  # noqa: E402
import state_dir  # noqa: E402

FAILS = []


def check(name, cond):
    print(("PASS  " if cond else "FAIL  ") + name)
    if not cond:
        FAILS.append(name)


def test_resolver(tmp: Path):
    dflt = tmp / "dataroot" / "artpipe"
    check("env var wins", state_dir.resolve({state_dir.ENV_VAR: str(tmp / "x")}, dflt) == tmp / "x")
    check("no env -> the data-root default", state_dir.resolve({}, dflt) == dflt)
    check("blank env ignored", state_dir.resolve({state_dir.ENV_VAR: "  "}, dflt) == dflt)
    check("real default is rmpaths' artpipe, never under Luke/dev",
          state_dir.resolve({}) == state_dir.rmpaths.rm_path("artpipe")
          and "luke/dev" not in str(state_dir.resolve({})).replace("\\", "/").lower())
    try:
        state_dir.require(tmp / "nope")
        check("require refuses a missing state dir", False)
    except SystemExit:
        check("require refuses a missing state dir", True)


def _job(d: Path, jid: str, **extra):
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{jid}.json").write_text(json.dumps({"id": jid, **extra}))


def test_collect(tmp: Path):
    st = tmp / "state"
    repo = tmp / "repo"
    # the ledger refuses a mod that is not a real folder (Textures/ or About/About.xml): make src/M one
    (repo / "src" / "M" / "Textures").mkdir(parents=True)
    os.environ["ARTSTORE"] = str(tmp / "artstore")          # never the real store
    os.environ["ART_SRC_ROOT"] = str(repo / "src")
    os.environ["ART_LEDGER_DIR"] = str(repo / "infrastructure" / "state" / "art")
    os.environ["ART_SEAT"] = "BUILD"          # art ledger refuses to guess a seat
    _job(st / "done", "a1", install_to="src/M/Textures/a1.png")
    (st / "done" / "a1.manifest.json").write_text("{}")
    (st / "_artsrc" / "a1").mkdir(parents=True)
    (st / "_artsrc" / "a1" / "a1.png").write_bytes(b"\x89PNGfake")
    _job(st / "failed", "f1")
    (st / "_artsrc" / "f1").mkdir(parents=True)
    (st / "_artsrc" / "f1" / "f1.png").write_bytes(b"x")
    out = AS.collect_one(st, repo, "a1", "src/M/Textures/a1.png", dry_run=False)
    check("collect copies the PNG into src/", out.read_bytes() == b"\x89PNGfake")
    rec = json.loads((st / "collected.jsonl").read_text().splitlines()[0])
    check("collect records job + dest", rec["job_id"] == "a1" and rec["dest"] == "src/M/Textures/a1.png")
    check("collected set sees it", ("a1", "src/M/Textures/a1.png") in AS._collected(st))
    L = AS._artledger(repo)
    live = L.Index().live.get(("src/M", "a1.png"), {})
    check("collect goes through the art ledger (live event, reason artpipe-collect)",
          live.get("reason") == "artpipe-collect" and live.get("sha") == L.sha256_bytes(b"\x89PNGfake"))
    L.append({"type": "ruling", "id": "k1", "target": {"sha": live.get("sha")}, "verdict": "keep",
              "by": "owner", "trust": "ruled"})
    (st / "_artsrc" / "a1" / "a1.png").write_bytes(b"\x89PNGfake2")
    try:
        AS.collect_one(st, repo, "a1", "src/M/Textures/a1.png", dry_run=False)
        check("collect refuses to replace an owner-kept picture", False)
    except SystemExit:
        check("collect refuses to replace an owner-kept picture", out.read_bytes() == b"\x89PNGfake")
    (st / "_artsrc" / "a1" / "a1.png").write_bytes(b"\x89PNGfake")
    for name, args in (("refuses dest outside src/", ("a1", "Transient/a1.png")),
                       ("refuses ../ escape", ("a1", "src/../x.png")),
                       ("refuses a failed job", ("f1", "src/M/f1.png")),
                       ("refuses a missing PNG", ("zz", "src/M/zz.png"))):
        try:
            AS.collect_one(st, repo, *args, dry_run=False)
            check(name, False)
        except SystemExit:
            check(name, True)
    rc = AS.main(["--state", str(st), "collect", "--from-jobs", "--repo", str(repo)])
    check("--from-jobs skips already-collected", rc == 0 and
          len((st / "collected.jsonl").read_text().splitlines()) == 1)
    # a refused job (bad install_to) sorted BEFORE a good one: the good one still lands, rc says 1.
    # Before 2026-10-26 the first refusal aborted the batch, every run, forever.
    _job(st / "done", "b0", install_to="Transient/b0.png")
    _job(st / "done", "b1", install_to="src/M/Textures/b1.png")
    for j in ("b0", "b1"):
        (st / "done" / f"{j}.manifest.json").write_text("{}")
        (st / "_artsrc" / j).mkdir(parents=True)
        (st / "_artsrc" / j / f"{j}.png").write_bytes(b"\x89PNG" + j.encode())
    import contextlib
    import io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = AS.main(["--state", str(st), "collect", "--from-jobs", "--repo", str(repo)])
    check("--from-jobs: a refused job does not block the next one",
          rc == 1 and (repo / "src/M/Textures/b1.png").is_file() and "NOT COLLECTED" in buf.getvalue()
          and "b0" in buf.getvalue() and ("b1", "src/M/Textures/b1.png") in AS._collected(st))
    # an install_to with a leading '/' (review w94): collect_one records it stripped, so --from-jobs must compare it
    # stripped too, or the job is collected again on every run
    _job(st / "done", "c1", install_to="/src/M/Textures/c1.png")
    (st / "done" / "c1.manifest.json").write_text("{}")
    (st / "_artsrc" / "c1").mkdir(parents=True)
    (st / "_artsrc" / "c1" / "c1.png").write_bytes(b"\x89PNGc1")
    with contextlib.redirect_stdout(io.StringIO()):
        for _ in range(2):
            AS.main(["--state", str(st), "collect", "--from-jobs", "--repo", str(repo)])
    c1 = [r for r in (st / "collected.jsonl").read_text().splitlines() if '"c1"' in r]
    check("--from-jobs: a leading-'/' install_to is collected once, not on every run",
          len(c1) == 1 and (repo / "src/M/Textures/c1.png").is_file())


def test_find_legacy(tmp: Path):
    import contextlib
    import io
    st, old = tmp / "state", tmp / "old"
    (st / "_artsrc" / "korrum_v1").mkdir(parents=True)
    (st / "done").mkdir()
    (old / "_artsrc" / "miasma_nemreth").mkdir(parents=True)
    (old / "done").mkdir()
    (old / "done" / "nemreth_v0.json").write_text("{}")

    def run(*extra):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            AS.main(["--state", str(st), "find", "nemreth", "korrum", *extra])
        return buf.getvalue()
    out = run("--legacy", str(old))
    check("find sees the state dir (sanity probe)", "korrum: 1 raw text hit" in out)
    check("find sees a legacy _artsrc dir and done/ job by name",
          "nemreth: 2 raw text hit" in out and "LEGACY" in out and "miasma_nemreth/" in out)
    check("--no-legacy skips it", "nemreth: 0 raw text hit" in run("--no-legacy"))
    check("find resolves the term through subject.py, with the evidence of each hit",
          "korrum: resolves to korrum" in out and "name-matched" in out and "job id token 'korrum'" in out)
    check("--no-resolve gives the raw hits only", "resolves to" not in run("--no-legacy", "--no-resolve"))
    check("a missing legacy root is said, not silently empty",
          "MISSING" in run("--legacy", str(tmp / "absent")))


def test_migrate(tmp: Path):
    src, dst = tmp / "old", tmp / "new"
    _job(src / "done", "j1")                 # advanced past dst's pending copy
    _job(dst / "pending", "j1")
    _job(src / "pending", "j2")              # dst already has it done: never regress
    _job(dst / "done", "j2")
    _job(src / "failed", "j3")
    (src / "_artsrc" / "j1").mkdir(parents=True)
    (src / "_artsrc" / "j1" / "j1.png").write_bytes(b"p")
    (src / "registry.jsonl").write_text("a\nb\n")
    (dst / "registry.jsonl").write_text("a\nc\n")
    AS.migrate(src, dst, dry=False)
    check("job advanced to done and removed from pending",
          (dst / "done" / "j1.json").exists() and not (dst / "pending" / "j1.json").exists())
    check("job further along in dest is kept", (dst / "done" / "j2.json").exists()
          and not (dst / "pending" / "j2.json").exists())
    check("failed job copied", (dst / "failed" / "j3.json").exists())
    check("_artsrc copied", (dst / "_artsrc" / "j1" / "j1.png").read_bytes() == b"p")
    check("registry unioned by line, dest lines kept",
          (dst / "registry.jsonl").read_text().splitlines() == ["a", "c", "b"])
    check("source untouched", (src / "pending" / "j2.json").exists() and (src / "done" / "j1.json").exists())
    again = AS.migrate(src, dst, dry=False)
    check("re-run is a no-op", not {k: v for k, v in again.items() if k != "kept_further_along"})
    # the source job vanishes mid-copy (a live daemon moved it): dst's earlier-stage copy must survive
    _job(src / "done", "j4")
    _job(dst / "pending", "j4")
    import shutil
    real_copy2 = shutil.copy2

    def vanishing_copy2(a, b, *k, **kw):
        if Path(a).name == "j4.json":
            Path(a).unlink()
            raise FileNotFoundError(a)
        return real_copy2(a, b, *k, **kw)
    shutil.copy2 = vanishing_copy2
    try:
        st = AS.migrate(src, dst, dry=False)
    finally:
        shutil.copy2 = real_copy2
    check("a job that vanished mid-copy keeps dst's earlier copy (never lost from both stages)",
          st.get("vanished_mid_copy") == 1 and (dst / "pending" / "j4.json").exists()
          and not (dst / "done" / "j4.json").exists())
    # done and failed share a rank: a job dst already files in one terminal stage must not gain a twin in the other
    # (review w94: 4 of the live queue's 32 done/failed twins came from the legacy migrate)
    src2, dst2 = tmp / "old2", tmp / "new2"
    for d in ("done", "failed"):
        _job(src2 / d, "t1")                 # already a twin in the source: the first stage walked wins
        (src2 / d / "t1.manifest.json").write_text("{}")
    _job(src2 / "failed", "t2")              # dst re-ran it and filed it done since
    (src2 / "failed" / "t2.manifest.json").write_text("{}")
    _job(dst2 / "done", "t2")
    (dst2 / "done" / "t2.manifest.json").write_text("{}")
    _job(src2 / "failed", "t3")              # control: a failed job with no record in dst still arrives
    st2 = AS.migrate(src2, dst2, dry=False)
    check("migrate never files one job in both done/ and failed/",
          (dst2 / "done" / "t1.json").exists() and not (dst2 / "failed" / "t1.json").exists()
          and not (dst2 / "failed" / "t1.manifest.json").exists()
          and not (dst2 / "failed" / "t2.json").exists() and not (dst2 / "failed" / "t2.manifest.json").exists()
          and (dst2 / "failed" / "t3.json").exists() and st2.get("kept_other_terminal") == 4)


def test_requeue(tmp: Path):
    import requeue_quota_failures as RQ
    for d in ("done", "failed", "pending"):
        (tmp / d).mkdir()
    for jid, err in (("quota", "You've hit your usage limit, try again at 22:00"), ("reject", "validator REJECT")):
        (tmp / "failed" / f"{jid}.json").write_text("{}")
        (tmp / "failed" / f"{jid}.manifest.json").write_text(json.dumps({"worker_stderr_tail": err}))
    check("requeue dry-run moves nothing", RQ.one_pass(tmp, dry_run=True) == (1, 2)
          and (tmp / "failed" / "quota.json").exists())
    check("requeue sees both failed manifests, moves only the quota one", RQ.one_pass(tmp) == (1, 2))
    check("quota job is pending, its manifest parked in the state dir",
          (tmp / "pending" / "quota.json").exists() and len(list((tmp / "_requeued_manifests").iterdir())) == 1)
    check("rejected job stays failed", (tmp / "failed" / "reject.json").exists())


def test_owner_accepted(tmp: Path):
    for d in ("done", "failed"):
        (tmp / d).mkdir()
    (tmp / "failed" / "j.json").write_text(json.dumps({"id": "j"}))
    (tmp / "failed" / "j.manifest.json").write_text(json.dumps({"id": "j", "status": "failed",
                                                               "worker_status": "failed_canon", "note": "FAIL 4/5"}))
    AS.main(["--state", str(tmp), "owner-accepted", "j", "--note", "installed on his word"])
    m = json.loads((tmp / "done" / "j.manifest.json").read_text())
    check("owner-accepted: job + manifest moved to done/, nothing left in failed/",
          (tmp / "done" / "j.json").is_file() and not list((tmp / "failed").iterdir()))
    check("owner-accepted: ok/owner_accepted, failed record and note kept",
          m["status"] == "ok" and m["worker_status"] == "owner_accepted"
          and m["failed_record"]["worker_status"] == "failed_canon" and "his word" in m["owner_accepted"]["note"])
    try:
        AS.main(["--state", str(tmp), "owner-accepted", "j", "--note", "x"])
        check("owner-accepted: refuses a job not in failed/", False)
    except SystemExit:
        check("owner-accepted: refuses a job not in failed/", True)


def test_twins(tmp: Path):
    import contextlib
    import io
    st, bk = tmp / "st", tmp / "bk"
    for d in ("pending", "active", "done", "failed"):
        (st / d).mkdir(parents=True)
    old = time.time() - 3600

    def twin(jid, png=True, done_status="ok", png_late=False, done_json=True):
        if done_json:
            (st / "done" / f"{jid}.json").write_text(json.dumps({"id": jid}))
        dm = st / "done" / f"{jid}.manifest.json"
        dm.write_text(json.dumps({"id": jid, "status": done_status, "worker_status": "ok"}))
        os.utime(dm, (old, old))
        (st / "failed" / f"{jid}.json").write_text(json.dumps({"id": jid}))
        (st / "failed" / f"{jid}.manifest.json").write_text(json.dumps(
            {"id": jid, "status": "failed", "worker_status": "worker_error"}))
        if png:
            p = st / "_artsrc" / jid / f"{jid}.png"
            p.parent.mkdir(parents=True)
            p.write_bytes(b"png" + jid.encode())
            t = time.time() if png_late else old - 10
            os.utime(p, (t, t))

    twin("good")
    twin("stray")                                                     # + a misclaimed manifest's manifest
    (st / "failed" / "stray.json").unlink()
    (st / "failed" / "stray.manifest.manifest.json").write_text(json.dumps({"status": "failed"}))
    twin("nopng", png=False)
    # a lost _artsrc PNG is excused only by the art ledger + store holding EVERY ledgered picture of the job
    led, store = tmp / "twled", tmp / "twstore"
    os.environ["ART_LEDGER_DIR"], os.environ["ARTSTORE"] = str(led), str(store)
    (led / "events").mkdir(parents=True)
    held, lost = "a" * 64, "b" * 64
    (store / held[:2]).mkdir(parents=True)
    (store / held[:2] / f"{held}.png").write_bytes(b"png")
    (led / "events" / "BUILD.jsonl").write_text("".join(json.dumps(e) + "\n" for e in (
        {"id": "v1", "type": "variant", "kind": "artpipe", "job": "stored", "sha": held},
        {"id": "v2", "type": "variant", "kind": "artpipe", "job": "halfstored", "sha": held},
        {"id": "v3", "type": "variant", "kind": "artpipe", "job": "halfstored", "sha": lost},
        {"id": "v4", "type": "variant", "kind": "repo", "job": "repoonly", "sha": held})))
    twin("stored", png=False)
    twin("halfstored", png=False)
    twin("repoonly", png=False)
    twin("late", png_late=True)
    twin("badman", done_status="failed")
    twin("busy")
    (st / "pending" / "busy.json").write_text("{}")
    twin("running")
    (st / "active" / "running.manifest.json").write_text("{}")
    (st / "failed" / "onlyfailed.json").write_text("{}")             # not a twin
    (st / "registry.jsonl").write_text(json.dumps({"event": "validated", "job_id": "good", "ts": 5,
                                                   "verdict": "pass"}) + "\n")
    before = sorted(p.name for p in (st / "failed").iterdir())
    plan = {p["id"]: p for p in AS.twins_plan(st)}
    check("twins: only ids in both done/ and failed/", set(plan) == {"good", "stray", "nopng", "late", "badman",
                                                                     "busy", "running", "stored", "halfstored",
                                                                     "repoonly"})
    check("twins: no _artsrc PNG but the store holds the job's ledgered picture -> KEEP_DONE, sha as evidence",
          plan["stored"]["decision"] == "KEEP_DONE" and plan["stored"]["evidence"] == {"artstore": [held]})
    check("twins: a picture missing from the store, or a non-artpipe variant, excuses nothing",
          all(plan[j]["decision"] == "AMBIGUOUS" and not plan[j]["prune"] for j in ("halfstored", "repoonly")))
    check("twins: an explicit `stored` map is used as given",
          AS.twins_plan(st, stored={})[[p["id"] for p in AS.twins_plan(st, stored={})].index("stored")]["decision"]
          == "AMBIGUOUS")
    check("twins: done copy with its artifacts wins", plan["good"]["decision"] == "KEEP_DONE"
          and plan["good"]["prune"] == ["failed/good.json", "failed/good.manifest.json"]
          and plan["good"]["last_validated"] == (5, "pass"))
    check("twins: a stray <id>.manifest.manifest.json belongs to <id>", plan["stray"]["decision"] == "KEEP_DONE"
          and "failed/stray.manifest.manifest.json" in plan["stray"]["prune"])
    check("twins: no PNG / PNG newer than done / done not ok -> AMBIGUOUS, nothing to prune",
          all(plan[j]["decision"] == "AMBIGUOUS" and not plan[j]["prune"] for j in ("nopng", "late", "badman")))
    check("twins: a job in pending/ or active/ is REFUSED",
          plan["busy"]["decision"] == "REFUSED" and plan["running"]["decision"] == "REFUSED")
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = AS.main(["--state", str(st), "twins"])
    check("twins: dry run moves nothing, exits 2 on ambiguous/refused",
          rc == 2 and "DRY RUN" in buf.getvalue() and sorted(p.name for p in (st / "failed").iterdir()) == before)
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            AS.main(["--state", str(st), "twins", "--apply", "--backup-root", str(bk)])
        check("twins: --apply without --why refuses", False)
    except SystemExit:
        check("twins: --apply without --why refuses", sorted(p.name for p in (st / "failed").iterdir()) == before)
    try:
        AS.twins_apply(st, list(plan.values()), st / "inside", "x")
        check("twins: a backup root inside the state dir is refused", False)
    except SystemExit:
        check("twins: a backup root inside the state dir is refused", not (st / "inside").exists())
    with contextlib.redirect_stdout(io.StringIO()):
        rc = AS.main(["--state", str(st), "twins", "--apply", "--why", "selftest", "--backup-root", str(bk)])
    left = sorted(p.name for p in (st / "failed").iterdir())
    pruned = list((st / AS.PRUNED_DIR).glob("*/failed/*"))
    log = [json.loads(x) for x in next((st / AS.PRUNED_DIR).glob("*/PRUNED.jsonl")).read_text().splitlines()]
    check("twins: apply moves exactly the KEEP_DONE failed/ files", rc == 2 and sorted(p.name for p in pruned) ==
          ["good.json", "good.manifest.json", "stored.json", "stored.manifest.json", "stray.manifest.json",
           "stray.manifest.manifest.json"]
          and "good.json" not in left and "nopng.json" in left and "busy.json" in left and "onlyfailed.json" in left)
    check("twins: done/ copies and PNGs untouched", (st / "done" / "good.json").is_file()
          and (st / "_artsrc" / "good" / "good.png").is_file())
    check("twins: one provenance line per moved file, sha + why + backup",
          len(log) == 6 and all(r["why"] == "selftest" and len(r["sha256"]) == 64 and Path(r["backup"]).is_file()
                                for r in log)
          and {r["id"]: r["evidence"] for r in log}["stored"] == {"artstore": [held]})
    check("twins: backup holds the failed files and the kept done copy",
          all((Path(log[0]["backup"]).parents[1] / rel).is_file()
              for rel in ("failed/good.json", "done/good.json", "done/good.manifest.json")))
    check("twins: re-scan finds nothing left to prune",
          not [p for p in AS.twins_plan(st) if p["decision"] == "KEEP_DONE"])


def main() -> int:
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        for i, fn in enumerate((test_resolver, test_collect, test_find_legacy, test_migrate, test_requeue,
                                  test_owner_accepted, test_twins)):
            sub = tmp / str(i)
            sub.mkdir()
            fn(sub)
    print(f"{'FAIL' if FAILS else 'OK'}: {len(FAILS)} failure(s)")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
