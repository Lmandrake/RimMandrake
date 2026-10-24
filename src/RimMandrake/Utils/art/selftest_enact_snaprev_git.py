#!/usr/bin/env python3
"""selftest_enact_snaprev_git.py — enact reads the snapshot revisions of a sheet from a REAL git repository lazily,
bounded, and survives a bad revision (ENACT_SNAPREV_GIT_HARDEN_READS).

A temporary git repo under the scratch root holds one snapshot file committed three times: rev1 (built 2026-10-01),
rev2 (bytes that are not UTF-8 JSON — a corrupt or binary revision), rev3 (built 2026-10-05); the disk copy is built
2026-10-09 (a rebuild after every click below).

  1 a click after rev3 was built: git order is not build order (ENACT_KEYED_PICK_FIX_MOVED_LANE), so the whole bounded
    window is read for the newest build at or before the click — and unreadable rev2, whose build time is unknown, could
    be that build, so the answer is None with rev2 named (it used to stop at rev3, reading one revision);
  1b ...with the window bounded to rev3 alone (SNAP_REV_MAX=1) the same click resolves to rev3, one `git show`;
  2 a click between rev1 and rev3: the walk meets unreadable rev2 before it can reach rev1 — no exception, the answer is
    None and the reason names the revision (it may be the one he saw, so nothing older stands in for it);
  3 a click before every readable build: None, the reason naming the unreadable revision (it could be older still);
  4 SNAP_REV_MAX bounds the walk: with a bound of 1 only `git log -n 1` revisions exist, the click of case 2 finds no
    copy ("no copy … built at or before"), and no more than one `git show` runs;
  5 a git call that times out (SNAP_GIT_TIMEOUT tiny) is a reason, never a crash;
  6 a snapshot file outside the repository: disk copy only, no git call, no crash.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import selftest_enact as T  # noqa: E402

FAILS = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def git(root: Path, *args) -> str:
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True,
                          timeout=60).stdout


def main():
    import artledger as L
    import enact as E
    root = T.SCRATCH / f"enact_snaprev_git_{os.getpid()}"
    shutil.rmtree(root, ignore_errors=True)
    root.mkdir(parents=True)
    repo0, max0, to0 = L.REPO_ROOT, E.SNAP_REV_MAX, E.SNAP_GIT_TIMEOUT
    run0 = E.subprocess.run
    calls: list = []

    def counting_run(cmd, *a, **k):
        calls.append(list(cmd))
        return run0(cmd, *a, **k)
    try:
        git(root, "init", "-q")
        git(root, "config", "user.email", "selftest@example.invalid")
        git(root, "config", "user.name", "selftest")
        sp = root / "sheets" / "s.snapshot.json"
        sp.parent.mkdir()

        def doc(built, tag):
            return {"snapshotId": "SID", "built": built, "tag": tag, "rows": {}}
        for built, tag, raw in [("2026-10-01T00:00:00Z", "rev1", None), (None, "rev2", b"\xff\xfe{not json\x00"),
                                ("2026-10-05T00:00:00Z", "rev3", None)]:
            sp.write_bytes(raw if raw is not None else json.dumps(doc(built, tag)).encode())
            git(root, "add", str(sp))
            git(root, "commit", "-q", "-m", tag)
        sp.write_text(json.dumps(doc("2026-10-09T00:00:00Z", "disk")))
        cur = json.loads(sp.read_text())
        L.REPO_ROOT = root.resolve()
        E.subprocess.run = counting_run

        def ruled(at, path=sp):
            E.reset_caches()
            calls.clear()
            return E.ruled_snapshot(path, cur, at)

        def shows():
            return [c for c in calls if "show" in c]

        (s, why) = ruled("2026-10-06T00:00:00Z")
        h2 = git(root, "log", "--format=%H", "-n", "1", "--skip", "1").strip()
        check(s is None and h2[:10] in (why or "") and "unreadable" in (why or ""),
              f"1 a click after rev3, unreadable rev2 in the window: None, rev2 named ({s and s.get('tag')}, {why})")
        E.SNAP_REV_MAX = 1
        (s, why) = ruled("2026-10-06T00:00:00Z")
        check(bool(s) and s.get("tag") == "rev3" and len(shows()) == 1,
              f"1b ...a window of rev3 alone resolves to rev3, one git show ({s and s.get('tag')}, {len(shows())}, {why})")
        E.SNAP_REV_MAX = max0

        try:
            (s, why) = ruled("2026-10-03T00:00:00Z")
            ok = True
        except Exception as e:  # noqa: BLE001 — the point of the case
            ok, s, why = False, None, f"{type(e).__name__}: {e}"
        check(ok and s is None, f"2 a bad revision on the way to the answer: no crash, no stand-in ({s}, {why})")
        check(h2[:10] in (why or "") and "unreadable" in (why or ""),
              f"2 ...the reason names the unreadable revision {h2[:10]} ({why})")

        (s, why) = ruled("2026-09-01T00:00:00Z")
        check(s is None and "unreadable" in (why or ""),
              f"3 a click before every readable build: None — unreadable rev2 might be older still ({why})")

        E.SNAP_REV_MAX = 1
        (s, why) = ruled("2026-10-03T00:00:00Z")
        logs = [c for c in calls if "log" in c]
        check(s is None and len(shows()) <= 1 and logs and "-n" in logs[0] and logs[0][logs[0].index("-n") + 1] == "1",
              f"4 SNAP_REV_MAX=1 bounds the walk ({len(shows())} show, log {logs[:1]}, {why})")
        check("built at or before" in (why or ""), f"4 ...and says no copy that old was found ({why})")
        E.SNAP_REV_MAX = max0

        E.SNAP_GIT_TIMEOUT = 0.000001
        try:
            (s, why) = ruled("2026-10-06T00:00:00Z")
            ok = True
        except Exception as e:  # noqa: BLE001
            ok, s, why = False, None, f"{type(e).__name__}: {e}"
        check(ok and s is None and "git" in (why or ""), f"5 a timed-out git call is a reason, not a crash ({why})")
        E.SNAP_GIT_TIMEOUT = to0

        out = T.SCRATCH / f"enact_snaprev_outside_{os.getpid()}.snapshot.json"
        out.write_text(json.dumps(doc("2026-10-09T00:00:00Z", "disk")))
        L.REPO_ROOT = (root / "sheets").resolve() / "nowhere"
        try:
            (s, why) = ruled("2026-10-06T00:00:00Z", out)
            ok = True
        except Exception as e:  # noqa: BLE001
            ok, s, why = False, None, f"{type(e).__name__}: {e}"
        finally:
            out.unlink(missing_ok=True)
        check(ok and s is None and not calls, f"6 a snapshot outside the repo: no git call, no crash ({calls}, {why})")
    finally:
        L.REPO_ROOT, E.SNAP_REV_MAX, E.SNAP_GIT_TIMEOUT = repo0, max0, to0
        E.subprocess.run = run0
        E.reset_caches()
        shutil.rmtree(root, ignore_errors=True)
    print("\nALL PASS" if not FAILS else f"\n{len(FAILS)} FAILED")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
