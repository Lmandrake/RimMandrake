#!/usr/bin/env python3
"""selftest_sync_test_mods.py - sync_test_mods.py never reads an unmeasured target or an absent source as 'same'.

Offline: no ssh (SSH is swapped for a local python stub), no Workshop, temp dirs only. DIRTY_CODE_REVIEW_STANDING_LOOP_1
wave 10 found: remote_tally read a failed ssh as an empty folder (0, 0); a missing local JawaBench tallied (0, 0) against an
absent target and printed 'same' with exit 0; wanted() grepped every <li> in the modlist, commented-out ones included.
"""
import contextlib
import io
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sync_test_mods as S  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print(("ok   " if cond else "FAIL ") + name + ("" if cond else " | %s" % (detail,)))
    if not cond:
        FAILS.append(name)


def stub(code):
    return [sys.executable, "-c", code]


tmp = tempfile.mkdtemp(prefix="st_sync_test_mods_")
try:
    # wanted(): activeMods only, parsed, lowercased, deduplicated, ours and Ludeon dropped
    cfg = os.path.join(tmp, "ModsConfig.xml")
    with open(cfg, "w", encoding="utf-8") as f:
        f.write("<ModsConfigData><version>1.6</version><activeMods>"
                "<li>brrainz.harmony</li><li>ludeon.rimworld</li><li>mandrake.rm.x</li>"
                "<!-- <li>old.commented</li> --><li>Some.Mod</li><li>some.mod</li></activeMods>"
                "<knownExpansions><li>ludeon.rimworld.biotech</li><li>stray.known</li></knownExpansions></ModsConfigData>")
    w = S.wanted(cfg)
    check("wanted: activeMods third-party ids, lowercased, once", w == ["brrainz.harmony", "some.mod"], w)
    check("sanity: the real MINIMAL list yields ids", len(S.wanted()) > 0, S.wanted())

    # remote_tally(): a failed or garbled ssh is None, not (0, 0)
    S.SSH = stub("print('3 40')")
    check("sanity: a readable target tallies", S.remote_tally("/x") == (3, 40), S.remote_tally("/x"))
    S.SSH = stub("print('0 0')")
    check("an absent target folder is (0, 0)", S.remote_tally("/x") == (0, 0), S.remote_tally("/x"))
    S.SSH = stub("import sys; sys.exit(255)")
    check("ssh exit 255 is None (unread is not empty)", S.remote_tally("/x") is None, S.remote_tally("/x"))
    S.SSH = stub("print('Warning: something')")
    check("non-tally output is None", S.remote_tally("/x") is None, S.remote_tally("/x"))

    # main(): an absent source and an unreadable target both exit 1 and push nothing
    game = os.path.join(tmp, "game")
    os.makedirs(game)
    mod = os.path.join(tmp, "ws", "123")
    os.makedirs(mod)
    with open(os.path.join(mod, "a.txt"), "w") as f:
        f.write("abc")
    S.gp.GAME_DIR = game                         # no BridgeTools/JawaBench here
    S.wanted = lambda path=None: ["some.mod"]
    S.locate = lambda ids: {"some.mod": mod}
    pushed = []
    S.push = lambda *a: pushed.append(a)

    def run(remote, argv):
        S.remote_tally = remote
        sys.argv = ["sync_test_mods.py"] + argv
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = S.main()
        return rc, out.getvalue()

    rc, out = run(lambda p: (1, 3) if p.endswith("/123") else (0, 0), [])
    check("a missing local JawaBench is MISSING, exit 1 (not 'same 0 files')",
          rc == 1 and "MISSING JawaBench companion" in out and "same JawaBench" not in out, (rc, out))
    os.makedirs(os.path.join(game, "BridgeTools", "JawaBench"))
    with open(os.path.join(game, "BridgeTools", "JawaBench", "j.dll"), "w") as f:
        f.write("j")
    rc, out = run(lambda p: (1, 3) if p.endswith("/123") else (1, 1), [])
    check("sanity: both present and equal -> exit 0", rc == 0 and out.count("same") == 2, (rc, out))
    rc, out = run(lambda p: None, ["--apply"])
    check("an unreadable target is UNMEASURED, exit 1, nothing pushed",
          rc == 1 and out.count("UNMEASURED") == 2 and pushed == [], (rc, out, pushed))
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print("ALL PASS" if not FAILS else "FAILED: %s" % FAILS)
sys.exit(1 if FAILS else 0)
