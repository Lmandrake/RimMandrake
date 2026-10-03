#!/usr/bin/env python3
"""selftest_artpipe_state.py — state_dir resolver, collect and migrate, on temp dirs only."""
from __future__ import annotations

import json
import sys
import tempfile
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
    win = tmp / "winroot" / "_artpipe"
    repo = tmp / "clones" / "rm"
    check("env var wins", state_dir.resolve({state_dir.ENV_VAR: str(tmp / "x")}, win, repo) == tmp / "x")
    check("no /mnt/d parent -> sibling of clone",
          state_dir.resolve({}, win, repo) == tmp / "clones" / "_artpipe")
    win.parent.mkdir(parents=True)
    check("/mnt/d parent present -> windows default", state_dir.resolve({}, win, repo) == win)
    check("blank env ignored", state_dir.resolve({state_dir.ENV_VAR: "  "}, win, repo) == win)
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
    (repo / "src").mkdir(parents=True)
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


def main() -> int:
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        for i, fn in enumerate((test_resolver, test_collect, test_migrate, test_requeue)):
            sub = tmp / str(i)
            sub.mkdir()
            fn(sub)
    print(f"{'FAIL' if FAILS else 'OK'}: {len(FAILS)} failure(s)")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
