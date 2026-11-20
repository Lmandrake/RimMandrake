#!/usr/bin/env python3
"""selftest_standing_tabs.py: one test per promise on design/specs/2026-11-19-standing-status-tabs/boundary.md.

    python3 src/RimMandrake/Utils/selftest_standing_tabs.py      exit 0 all pass, 1 a test failed
Nothing here opens a window: the launcher is replaced by a recorder.
"""
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
NAMES = ["CODEBASE_NOW.html", "STATUS_BOARD.html", "MATURATION_NOW.html"]


def run_pages(root, *args, env_extra=None):
    env = dict(os.environ, RM_DATA_ROOT=root)
    env.update(env_extra or {})
    return subprocess.run([sys.executable, os.path.join(HERE, "pages_open.py"), "--dry-run", *args],
                          capture_output=True, text=True, env=env, timeout=60)


def folder(present):
    root = tempfile.mkdtemp(prefix="tabs_")
    os.makedirs(os.path.join(root, "conductor"))
    for n in present:
        open(os.path.join(root, "conductor", n), "w").write("<html></html>")
    return root


def urls(out):
    return re.findall(r"file:///\S+", out)


def t_three_tabs_in_order():
    r = run_pages(folder(NAMES))
    u = urls(r.stdout)
    assert r.returncode == 0, (r.returncode, r.stderr[-300:])
    assert [x.rsplit("/", 1)[1] for x in u] == NAMES, u
    assert len(r.stdout.splitlines()) >= 3 and sum(1 for l in r.stdout.splitlines() if "file:///" in l) == 3
    assert "--new-window" in r.stdout
    assert "chrome" in r.stdout.lower() and "edge" not in r.stdout.lower(), r.stdout


def t_missing_page_named_others_open():
    r = run_pages(folder([NAMES[0], NAMES[2]]))
    assert r.returncode == 2, r.returncode
    assert "MISSING" in r.stdout and "STATUS_BOARD.html" in r.stdout.split("MISSING", 1)[1], r.stdout
    assert [x.rsplit("/", 1)[1] for x in urls(r.stdout)] == [NAMES[0], NAMES[2]], r.stdout


def t_folder_from_rmpaths():
    a, b = folder(NAMES), folder(NAMES)
    ua, ub = urls(run_pages(a).stdout), urls(run_pages(b).stdout)
    assert ua and ub and ua != ub and all(os.path.basename(a) in x for x in ua), (ua, ub)
    src = open(os.path.join(HERE, "pages_open.py")).read()
    assert not re.search(r"(?<![A-Za-z])[A-Za-z]:[\\/]|/mnt/[a-z]/", src), "a drive path is hard-wired"


def t_never_fullscreen_never_steal_focus():
    r = run_pages(folder(NAMES))
    cmd = " ".join(l for l in r.stdout.splitlines() if "file:///" not in l).lower()
    assert "/min" in cmd, cmd
    for bad in ("fullscreen", "kiosk", "--app", "/max"):
        assert bad not in cmd, (bad, cmd)
    shown = run_pages(folder(NAMES), "--show").stdout.lower()
    assert "/min" not in shown and "fullscreen" not in shown, shown


def t_dry_run_opens_nothing():
    import pages_open
    called = []
    root = folder(NAMES)
    os.environ["RM_DATA_ROOT"] = root
    rc = pages_open.main(["--dry-run"], launcher=lambda cmd: called.append(cmd) or 0)
    assert rc == 0 and not called, (rc, called)
    rc = pages_open.main([], launcher=lambda cmd: called.append(cmd) or 0)
    assert rc == 0 and len(called) == 1, (rc, called)
    rc = pages_open.main([], launcher=lambda cmd: 1)
    assert rc == 3, rc


def t_maturation_page_reloads_and_shows_build_time():
    out = tempfile.mkdtemp(prefix="mat_")
    r = subprocess.run([sys.executable, os.path.join(HERE, "maturation_now.py"), "--no-live", "--no-phone",
                        "--out", out], capture_output=True, text=True, timeout=300, cwd=REPO)
    assert r.returncode == 0, r.stderr[-400:]
    html = open(os.path.join(out, "MATURATION_NOW.html"), encoding="utf-8").read()
    assert '<meta http-equiv="refresh" content="300">' in html, "no 300 s reload line"
    assert re.search(r'id="built"[^>]*>[^<]*Built [^<]*\d', html[:6000]), "no visible build time near the top"


def main():
    tests = [t_three_tabs_in_order, t_missing_page_named_others_open, t_folder_from_rmpaths,
             t_never_fullscreen_never_steal_focus, t_dry_run_opens_nothing,
             t_maturation_page_reloads_and_shows_build_time]
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
