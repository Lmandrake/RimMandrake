#!/usr/bin/env python3
"""selftest_logon_shortcut.py: one test per promise in design/specs/2026-11-19-logon-tabs-shortcut/boundary.md.
Nothing touches Windows: the PowerShell runner and the Startup lookup are recorders."""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pages_logon_shortcut as P  # noqa: E402

START = "C:\\Fake\\Startup"


def repo(with_pages=True):
    d = tempfile.mkdtemp(prefix="lg_")
    if with_pages:
        p = os.path.join(d, "pages")
        open(p, "w").write("#!/bin/sh\n")
        os.chmod(p, 0o755)
    return d


def run(*argv):
    calls = []

    def runner(script):
        calls.append(script)
        return 0, "removed" if "Remove-Item" in script else "", ""
    rc = P.main(list(argv), runner=runner, startup=lambda: START)
    return rc, calls


def t_shortcut_runs_pages_minimized():
    d = repo()
    rc, calls = run("--repo", d)
    assert rc == 0 and len(calls) == 1
    s = calls[0]
    assert "TargetPath='wsl.exe'" in s and d + "/pages" in s and "WindowStyle=7" in s and P.NAME in s


def t_no_fullscreen_no_focus():
    d = repo()
    _, calls = run("--repo", d)
    for bad in ("--show", "kiosk", "--app", "fullscreen"):
        assert bad not in calls[0]


def t_uninstall_removes_only_ours():
    rc, calls = run("--uninstall")
    assert rc == 0 and len(calls) == 1 and calls[0].count(P.NAME) == 2 and "Remove-Item -LiteralPath" in calls[0]
    assert "*" not in calls[0]


def t_dry_run_writes_nothing():
    d = repo()
    assert run("--repo", d, "--dry-run") == (0, [])
    assert run("--uninstall", "--dry-run") == (0, [])


def t_missing_pages_refused():
    rc, calls = run("--repo", repo(False))
    assert rc == 3 and calls == []


def main():
    tests = [t_shortcut_runs_pages_minimized, t_no_fullscreen_no_focus, t_uninstall_removes_only_ours,
             t_dry_run_writes_nothing, t_missing_pages_refused]
    failed = 0
    for t in tests:
        try:
            t()
            print("PASS", t.__name__)
        except Exception as e:  # noqa: BLE001
            failed += 1
            print("FAIL", t.__name__, "%s: %s" % (type(e).__name__, e))
    print("FAILED %d of %d" % (failed, len(tests)) if failed else "ALL PASS (%d)" % len(tests))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
