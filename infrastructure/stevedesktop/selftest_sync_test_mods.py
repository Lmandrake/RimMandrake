#!/usr/bin/env python3
"""selftest_sync_test_mods.py - sync_test_mods.py never reads an unmeasured target or an absent source as 'same'.

Offline: no ssh (SSH is swapped for a local python stub), no Workshop, temp dirs only. DIRTY_CODE_REVIEW_STANDING_LOOP_1
wave 10 found: remote_tally read a failed ssh as an empty folder (0, 0); a missing local JawaBench tallied (0, 0) against an
absent target and printed 'same' with exit 0; wanted() grepped every <li> in the modlist, commented-out ones included.
STEVE_COMPANION_FIX_DLL_STALE_NO_PRIORITIES: the companion is this clone's FRESH build (embedded source hash ==
the sources at HEAD), staged in the worker inbox and compared by sha256, never by file count + byte total.
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

    # remote_sha(): a sha, "" for absent, None for an unreadable or garbled target
    S.SSH = stub("print('%s')" % ("ab" * 32))
    check("sanity: a readable target file hashes", S.remote_sha("/x") == "ab" * 32, S.remote_sha("/x"))
    S.SSH = stub("print('absent')")
    check("an absent target file is ''", S.remote_sha("/x") == "", S.remote_sha("/x"))
    for code in ("import sys; sys.exit(255)", "print('Warning: something')"):
        S.SSH = stub(code)
        check("ssh failure / garble is None: %s" % code, S.remote_sha("/x") is None, S.remote_sha("/x"))

    # main(): the companion is this clone's FRESH build, compared by sha256; an absent or stale build, or an
    # unreadable target, exits 1 and pushes nothing
    mod = os.path.join(tmp, "ws", "123")
    os.makedirs(mod)
    with open(os.path.join(mod, "a.txt"), "w") as f:
        f.write("abc")
    S.ARTIFACT = os.path.join(tmp, "artifact")                 # no build here yet
    S.wanted = lambda path=None: ["some.mod"]
    S.locate = lambda ids: {"some.mod": mod}
    pushed = []
    S.push = lambda *a: pushed.append(a)
    S.push_file = lambda *a: pushed.append(a)

    def run(remote, rsha, argv):
        S.remote_tally, S.remote_sha = remote, rsha
        sys.argv = ["sync_test_mods.py"] + argv
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = S.main()
        return rc, out.getvalue()

    mods_same = lambda p: (1, 3)
    rc, out = run(mods_same, lambda p: "", ["--apply"])
    check("a missing companion build is MISSING, exit 1, nothing pushed",
          rc == 1 and "MISSING JawaBench companion" in out and not any(S.CI.DLL_NAME in str(x) for x in pushed),
          (rc, out, pushed))
    dll = os.path.join(S.ARTIFACT, S.CI.DLL_NAME)
    S.CI.write_fixture(dll, "f" * 64)
    rc, out = run(mods_same, lambda p: "", ["--apply"])
    check("a STALE companion build (other sources) is refused, exit 1, nothing pushed",
          rc == 1 and "STALE JawaBench companion" in out and pushed == [], (rc, out, pushed))
    S.CI.write_fixture(dll, None)
    rc, out = run(mods_same, lambda p: "", ["--apply"])
    check("an UNSTAMPED (pre-stamp) build is refused, exit 1", rc == 1 and "UNSTAMPED JawaBench" in out, (rc, out))
    S.CI.write_fixture(dll, S.CI.srchash_at(S.REPO, "HEAD"))
    import hashlib
    sha = hashlib.sha256(open(dll, "rb").read()).hexdigest()
    rc, out = run(mods_same, lambda p: sha, [])
    check("sanity: a FRESH build already in the inbox, mods equal -> exit 0", rc == 0 and out.count("same") == 2
          and S.INBOX in out, (rc, out))
    same_size = "0" * 64                                       # the old trap: same size, different bytes
    rc, out = run(mods_same, lambda p: same_size if p.endswith(S.CI.DLL_NAME) else sha, [])
    check("a different companion in the inbox is 'copy' whatever its size", rc == 0 and "copy JawaBench" in out, (rc, out))
    state = {"n": 0}

    def after_push(p):
        state["n"] += 1
        return same_size if state["n"] == 1 else sha
    rc, out = run(mods_same, after_push, ["--apply"])
    check("--apply streams the FRESH build into the worker inbox and re-reads its sha",
          rc == 0 and pushed == [(dll, S.INBOX)] and " ok " in out, (rc, out, pushed))
    pushed.clear()
    rc, out = run(lambda p: None, lambda p: None, ["--apply"])
    check("an unreadable target is UNMEASURED, exit 1, nothing pushed",
          rc == 1 and out.count("UNMEASURED") == 2 and pushed == [], (rc, out, pushed))
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print("ALL PASS" if not FAILS else "FAILED: %s" % FAILS)
sys.exit(1 if FAILS else 0)
