#!/usr/bin/env python3
"""Selftest for remake/checkpoint.py on a fake LocalLow (never touches the real one)."""
import contextlib
import io
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import checkpoint as C  # noqa: E402


def run(*argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = C.main(list(argv))
    return rc, buf.getvalue()


def w(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w").write(s)


def main():
    t = tempfile.mkdtemp(prefix="cp_selftest_")
    ll, root = os.path.join(t, "LocalLow"), os.path.join(t, "out")
    cfg = os.path.join(ll, "Config")
    w(os.path.join(cfg, "ModsConfig.xml"), "<ModsConfigData><activeMods><li>ludeon.rimworld</li></activeMods></ModsConfigData>")
    w(os.path.join(cfg, "Mod_1_A.xml"), "a")
    w(os.path.join(cfg, C.CHERRY), "<keys/>")
    w(os.path.join(cfg, "Mod_2_B.xml.bak-old"), "backup, not a setting")
    w(os.path.join(cfg, "Mod_3_Dir", "inner.xml"), "inner")
    w(os.path.join(cfg, "GravshipExport", "ship.xml"), "ship")
    w(os.path.join(cfg, "Prefs.xml"), "prefs")
    w(os.path.join(cfg, "KeyPrefs.xml"), "not copied")
    w(os.path.join(ll, "Saves", "a.rws"), "save a")
    fails = []

    def check(cond, msg):
        if not cond:
            fails.append(msg)

    rc, out = run("make", "--ids", "C1,C2,C3", "--root", root, "--date", "D", "--locallow", ll)
    check(rc == 0, "make rc %s %s" % (rc, out))
    c3 = os.path.join(root, "D", "C3")
    man = C._load(c3)
    rels = {x["rel"] for x in man["files"]}
    check("Config/Mod_1_A.xml" in rels and "Config/" + C.CHERRY in rels, "C3 misses Mod_*.xml / cherry picker")
    check("Config/Mod_3_Dir/inner.xml" in rels and "Config/GravshipExport/ship.xml" in rels, "C3 misses dir/gravship")
    check("Config/Mod_2_B.xml.bak-old" not in rels and "Config/KeyPrefs.xml" not in rels, "C3 copied a backup/non-setting")
    check(any(x["role"] == "cherry picker" for x in man["files"]), "cherry picker role not tagged")
    check(os.path.isfile(os.path.join(c3, "SHA256SUMS")), "no SHA256SUMS")
    # refuse overwrite
    rc, out = run("make", "--ids", "C3", "--root", root, "--date", "D", "--locallow", ll)
    check(rc == 3 and "REFUSED" in out, "overwrite not refused: %s" % out)
    # verify copy + live clean
    check(run("verify", c3)[0] == 0, "copy verify not clean")
    check(run("verify", c3, "--against-live", "--locallow", ll)[0] == 0, "live verify not clean")
    check(run("status", "--root", root, "--date", "D")[0] == 0, "status not PASS")
    # drift: change a setting, add a new mod settings file
    w(os.path.join(cfg, "Mod_1_A.xml"), "a changed")
    w(os.path.join(cfg, "Mod_9_New.xml"), "new")
    rc, out = run("verify", c3, "--against-live", "--locallow", ll)
    check(rc == 1 and "CHANGED" in out and "Mod_9_New.xml" in out, "drift not caught: %s" % out)
    # corrupt the copy
    w(os.path.join(c3, "Config", "Mod_1_A.xml"), "tampered")
    rc, out = run("verify", c3)
    check(rc == 1 and "CORRUPT" in out, "corruption not caught")
    check(run("status", "--root", root, "--date", "D")[0] == 1, "status not FAIL after corruption")
    # missing checkpoint dir => FAIL; missing manifest => UNMEASURED
    check(run("status", "--root", root, "--date", "nope")[0] == 1, "absent checkpoints not FAIL")
    os.makedirs(os.path.join(t, "empty"))
    check(run("verify", os.path.join(t, "empty"))[0] == 2, "no manifest not UNMEASURED")
    # restore: dry run writes nothing; apply without --game-is-down refused
    c2 = os.path.join(root, "D", "C2")
    w(os.path.join(cfg, "ModsConfig.xml"), "edited live")
    check(run("restore", c2)[0] == 0 and open(os.path.join(cfg, "ModsConfig.xml")).read() == "edited live",
          "dry-run restore wrote")
    check(run("restore", c2, "--apply", "--locallow", ll)[0] == 3, "apply without --game-is-down not refused")
    check(run("restore", c2, "--apply", "--game-is-down", "--locallow", ll)[0] == 0
          and "ludeon.rimworld" in open(os.path.join(cfg, "ModsConfig.xml")).read(), "restore did not restore")
    # missing source root => UNMEASURED
    rc, out = run("make", "--ids", "C1", "--root", root, "--date", "E", "--locallow", os.path.join(t, "nolocallow"))
    check(rc == 2, "missing Saves not UNMEASURED")
    if fails:
        print("FAIL selftest_checkpoint:", *fails, sep="\n  ")
        return 1
    print("PASS selftest_checkpoint (%d checks)" % 17)
    return 0


if __name__ == "__main__":
    sys.exit(main())
