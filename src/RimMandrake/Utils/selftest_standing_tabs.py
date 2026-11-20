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
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
NAMES = ["CODEBASE_NOW.html", "FLEET_NOW.html", "MATURATION_NOW.html"]


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
    assert "MISSING" in r.stdout and "FLEET_NOW.html" in r.stdout.split("MISSING", 1)[1], r.stdout
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


def run_fleet(root, age_s=None, body="<b>live body</b>"):
    cond = os.path.join(root, "conductor")
    os.makedirs(cond, exist_ok=True)
    src = os.path.join(cond, "RELENTLESS_NOW.md")
    if age_s is not None:
        open(src, "w").write(body)
        t = time.time() - age_s
        os.utime(src, (t, t))
    r = subprocess.run([sys.executable, os.path.join(HERE, "fleet_now.py")], capture_output=True, text=True,
                       env=dict(os.environ, RM_DATA_ROOT=root), timeout=60)
    p = os.path.join(cond, "FLEET_NOW.html")
    return r, (open(p, encoding="utf-8").read() if os.path.exists(p) else None), cond


def t_fleet_page_wraps_fresh_source():
    r, html, _ = run_fleet(tempfile.mkdtemp(prefix="fl_"), age_s=30)
    assert r.returncode == 0, (r.returncode, r.stdout, r.stderr[-300:])
    assert "<b>live body</b>" in html and '<meta http-equiv="refresh" content="60">' in html
    assert re.search(r'id="built"[^>]*>[^<]*Built [^<]*\d', html), "no visible build time"
    r, html, _ = run_fleet(tempfile.mkdtemp(prefix="fl_"), age_s=590)
    assert r.returncode == 0, "590 s is inside the 600 s limit"


def t_fleet_page_typora_look():
    root = tempfile.mkdtemp(prefix="fl_")
    th = tempfile.mkdtemp(prefix="themes_")
    open(os.path.join(th, "blue-topaz.css"), "w").write("#write{max-width:777px}")
    open(os.path.join(th, "blue-topaz-dark.css"), "w").write('@import "blue-topaz.css";\n:root{--bg-color:#202020}')
    body = "# Head\n\n```\ntree  a\n  b\n```\n\n<b>live body</b>\n\n| a | b |\n|---|---|\n| 1 | 2 |\n"
    os.environ["TYPORA_THEMES_DIR"] = th
    try:
        r, html, _ = run_fleet(root, age_s=5, body=body)
    finally:
        del os.environ["TYPORA_THEMES_DIR"]
    assert r.returncode == 0, r.stderr[-300:]
    assert '<div id="write"' in html and "max-width:777px" in html and "--bg-color:#202020" in html, "theme css missing"
    assert "@import" not in html, "import left unresolved"
    assert "<h1" in html and "<pre><code>tree  a\n  b\n</code></pre>" in html and "<table>" in html, html[-700:]
    assert "<b>live body</b>" in html
    os.environ["TYPORA_THEMES_DIR"] = tempfile.mkdtemp(prefix="nothemes_")
    try:
        r, html, _ = run_fleet(tempfile.mkdtemp(prefix="fl_"), age_s=5, body=body)
    finally:
        del os.environ["TYPORA_THEMES_DIR"]
    assert r.returncode == 0 and "#14171c" in html and "#e8eaee" in html and "theme not found" in html, html[:500]


def t_fleet_page_could_not_read():
    for age, why in ((None, "missing"), (601, "old")):
        root = tempfile.mkdtemp(prefix="fl_")
        r, html, _ = run_fleet(root, age_s=age, body="<b>OLD BODY</b>")
        assert r.returncode == 3, (why, r.returncode)
        assert "COULD NOT READ" in html and "OLD BODY" not in html, (why, html[:300])
        assert '<meta http-equiv="refresh"' in html and 'id="built"' in html, why


def t_fleet_page_written_whole():
    r, html, cond = run_fleet(tempfile.mkdtemp(prefix="fl_"), age_s=5)
    assert html.rstrip().endswith("</html>"), html[-80:]
    assert not [f for f in os.listdir(cond) if "tmp" in f], os.listdir(cond)


def main():
    tests = [t_fleet_page_wraps_fresh_source, t_fleet_page_typora_look, t_fleet_page_could_not_read, t_fleet_page_written_whole, t_three_tabs_in_order, t_missing_page_named_others_open, t_folder_from_rmpaths,
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
