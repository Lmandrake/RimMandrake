#!/usr/bin/env python3
"""selftest_pool_floor.py -- the clone pool's disk floor, count line and shed step
(design/specs/2026-11-22-clone-pool-disk-floor/boundary.md). Hermetic: a temp pool root, fake clones, the free space
and the clone sizes stubbed; the shed test uses a real git repo in a temp dir."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import scratch_clone as sc  # noqa: E402

GB = 10**9
FAILS: list[str] = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def pool_of(n: int, size_gb: float) -> Path:
    root = Path(tempfile.mkdtemp(prefix="pool_floor_")) / "clones"
    for i in range(n):
        (root / f"c{i}" / ".git").mkdir(parents=True)
    os.environ["RM_POOL_ROOT"] = str(root)
    sc.clone_bytes = lambda c, _b=int(size_gb * GB): _b
    return root


def free_is(gb: float):
    sc.root_free_bytes = lambda path=None, _b=int(gb * GB): _b


for k in ("RM_POOL_MAX_CLONES", "RM_POOL_MAX_BYTES", "RM_POOL_FLOOR_GB"):
    os.environ.pop(k, None)
REAL_RULES = getattr(sc, "SLOT_RULES", HERE / "slot_rules.json")


def t_a_pool_of_normal_clones_with_free_disk_is_admitted():
    root = pool_of(12, 10)
    free_is(451)
    why = sc.pool_admit(root / "new")
    check(why is None, f"a-pool-of-normal-clones-with-free-disk-is-admitted: 12 x 10 GB, 451 GB free -> {why!r}")


def t_a_near_full_disk_refuses_a_new_clone():
    root = pool_of(12, 10)
    free_is(215)
    why = sc.pool_admit(root / "new") or ""
    check("215" in why and "210" in why and "disk_brake_free_gb" in why,
          f"a-near-full-disk-refuses-a-new-clone: 215 GB free, largest clone 10 GB -> {why!r}")
    free_is(221)
    check(sc.pool_admit(root / "new") is None, "a-near-full-disk-refuses-a-new-clone: 221 GB free less 10 is admitted")


def t_the_clone_count_limit_still_refuses():
    root = pool_of(16, 1)
    free_is(900)
    why = sc.pool_admit(root / "new") or ""
    check("16 clones" in why, f"the-clone-count-limit-still-refuses: 16 clones, 900 GB free -> {why!r}")


def t_the_floor_is_the_disk_low_line():
    sc.SLOT_RULES = REAL_RULES
    floor = sc.pool_floor_bytes()
    slot = json.loads(REAL_RULES.read_text())["ops"]["disk_brake_free_gb"]
    rules = json.loads((HERE / "ops_watch_rules.json").read_text())

    def walk(x):
        if isinstance(x, dict):
            yield x
            for v in x.values():
                yield from walk(v)
        elif isinstance(x, list):
            for v in x:
                yield from walk(v)
    low = [d.get("value") for d in walk(rules) if d.get("key") == "disk.root_free_gb" and d.get("tag") == "DISK_LOW"]
    check(floor == slot * GB and low == [slot], f"the-floor-is-the-disk-low-line: floor {floor / GB} GB, slot {slot}, DISK_LOW {low}")


def t_an_unreadable_floor_refuses_by_name():
    root = pool_of(1, 5)
    free_is(900)
    bad = Path(tempfile.mkdtemp(prefix="pool_floor_rules_")) / "slot_rules.json"
    bad.write_text('{"ops": {"other": 1}}')
    sc.SLOT_RULES = bad
    try:
        why = sc.pool_admit(root / "new") or ""
        check("disk_brake_free_gb" in why and str(bad) in why, f"an-unreadable-floor-refuses-by-name: key missing -> {why!r}")
        bad.unlink()
        why = sc.pool_admit(root / "new") or ""
        check(str(bad) in why, f"an-unreadable-floor-refuses-by-name: file missing -> {why!r}")
    finally:
        sc.SLOT_RULES = REAL_RULES


def t_a_reading_under_the_floor_is_a_breach():
    pool_of(3, 10)
    free_is(215)
    r = sc.pool_reading(risk=False)
    check(r["breach"] == 1 and r["root_free_gb"] == 215 and r["floor_gb"] == 210 and r["margin_gb"] == -5,
          f"a-reading-under-the-floor-is-a-breach: {({k: r.get(k) for k in ('breach', 'root_free_gb', 'floor_gb', 'margin_gb')})}")
    free_is(451)
    r = sc.pool_reading(risk=False)
    check(r["breach"] == 0 and r["margin_gb"] == 231, f"a-reading-under-the-floor-is-a-breach: none at 451 GB -> {r['breach']}")


def git(c, *a):
    return subprocess.run(["git", "-C", str(c), *a], capture_output=True, text=True, check=True).stdout.strip()


def shed_fixture() -> Path:
    c = Path(tempfile.mkdtemp(prefix="pool_shed_")) / "c"
    c.mkdir()
    git(c, "init", "-q", "-b", "main")
    git(c, "config", "user.email", "t@example.invalid")
    git(c, "config", "user.name", "t")
    (c / "Transient").mkdir()
    (c / "Transient" / ".gitignore").write_text("*\n!.gitignore\n!pin.txt\n")
    (c / "Transient" / "pin.txt").write_text("pinned\n")
    (c / "ledger.jsonl").write_text("one\n")
    git(c, "add", "-A")
    git(c, "commit", "-q", "-m", "one")
    (c / "ledger.jsonl").write_text("one\ntwo\n")
    git(c, "commit", "-q", "-am", "two")
    git(c, "repack", "-a", "-q")          # packed, and the loose copies stay: what a clone's ledger blobs look like
    (c / "Transient" / "modcheck").mkdir()
    (c / "Transient" / "modcheck" / "saves_backup_1.rws").write_bytes(b"x" * 4096)
    (c / "stray.txt").write_text("untracked\n")
    (c / ".git" / "rm-treecheck-abc123" / "src").mkdir(parents=True)
    (c / ".git" / "rm-treecheck-abc123" / "src" / "f").write_text("a full checkout\n")
    return c


def loose(c: Path) -> int:
    return int(dict(ln.split(": ") for ln in git(c, "count-objects", "-v").splitlines())["count"])


def t_a_reused_clone_sheds_what_the_last_run_left():
    c = shed_fixture()
    head, before = git(c, "rev-parse", "HEAD"), loose(c)
    said = sc.shed(c)
    check(not (c / "Transient" / "modcheck").exists() and not (c / "stray.txt").exists(),
          "a-reused-clone-sheds-what-the-last-run-left: ignored and untracked files are gone")
    check(not list((c / ".git").glob("rm-treecheck-*")), "a-reused-clone-sheds-what-the-last-run-left: the treecheck is gone")
    check(before > 0 and loose(c) == 0, f"a-reused-clone-sheds-what-the-last-run-left: loose objects {before} -> {loose(c)}")
    check((c / "Transient" / "pin.txt").read_text() == "pinned\n" and git(c, "rev-parse", "HEAD") == head
          and git(c, "show", "HEAD:ledger.jsonl") == "one\ntwo", f"a-reused-clone-sheds-what-the-last-run-left: tracked work stays ({said})")


def t_pool_reuse_sheds_the_clone():
    import inspect
    src = inspect.getsource(sc.pool_reuse)
    check("shed(dest)" in src, "pool-reuse-sheds-the-clone: pool_reuse calls shed on the clone it gives")


def main() -> int:
    for t in (t_a_pool_of_normal_clones_with_free_disk_is_admitted, t_a_near_full_disk_refuses_a_new_clone,
              t_the_clone_count_limit_still_refuses, t_the_floor_is_the_disk_low_line,
              t_an_unreadable_floor_refuses_by_name, t_a_reading_under_the_floor_is_a_breach,
              t_a_reused_clone_sheds_what_the_last_run_left, t_pool_reuse_sheds_the_clone):
        try:
            t()
        except Exception as e:  # noqa: BLE001  a test that raises is a red, named
            check(False, f"{t.__name__} raised {type(e).__name__}: {e}")
    print(f"selftest_pool_floor: {'FAIL ' + str(len(FAILS)) if FAILS else 'PASS'}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
