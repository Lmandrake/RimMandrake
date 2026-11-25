#!/usr/bin/env python3
"""Live proof of the canonical-save guard (design/specs/2026-11-23-canonical-save-guard/boundary.md): on the running game a
save with a canonical name reads CAMPAIGN and refuses a test tool; the same file under a test name, and a new game, read TEST.

Run under Windows python.exe on a game whose driver lock you hold, after its companion deploy and restart, on any tier list:

    python.exe prove_canonical_guard.py

It makes a quicktest map, saves it as rm_proof_canonical_guard, and copies that file to CANONICAL_rm_proof_guard_<pid>.rws in
the same Saves folder; it deletes both at the end. It never loads or writes a real canonical save.
Exit 0 = every row PASS, 1 = a FAIL, 2 = UNMEASURED."""
import os
import shutil
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prove_three_tools as P  # noqa: E402  connect, call, row, quicktest

FREE, CANON = "rm_proof_canonical_guard", "CANONICAL_rm_proof_guard_%d" % os.getpid()


def profile(name, save, want):
    """The handshake names the loaded save and the profile, and a test tool agrees."""
    for _ in range(60):  # just after a load the lifecycle may not have entered the game yet: CAMPAIGN by "unknown", not by the list
        h = P.call("jawa/companion_handshake")
        if "unknown" not in str(h.get("profileWhy")):
            break
        time.sleep(1)
    got, seen, why = h.get("effectiveProfile"), (h.get("game") or {}).get("save"), str(h.get("profileWhy"))
    if got not in ("test", "campaign") or (seen or "") != save or "unknown" in why:
        return P.row(name, None, "handshake save %r, profile %r (%s): %s" % (seen, got, why, h.get("_error")))
    r = P.call("jawa/quiet_site", action="read")
    refused = r.get("refused") is True or "REFUSED in the CAMPAIGN" in str(r)
    by_list = want != "campaign" or "is a listed canonical save" in why  # the row proves the LIST, not the unknown-save default
    return P.row(name, got == want and refused == (want == "campaign") and by_list, "%s (%s); quiet_site refused: %s" % (got, why, refused))


def load(name):
    before = (P.call("jawa/companion_handshake").get("game") or {}).get("epoch")
    r = P.call("rimworld/load_game", saveName=name)
    for _ in range(240):
        g = P.call("jawa/companion_handshake").get("game") or {}
        if g.get("programState") == "Playing" and g.get("epoch") != before and g.get("save") == name:
            return True
        time.sleep(1)
    return P.row("load_" + name, None, "not Playing after 240 s: %s" % str(r)[:200])


def main():
    P.connect()
    h = P.call("jawa/companion_handshake")
    print("companionSha: %s" % h.get("companionSha"), flush=True)  # the record names the build it proved
    print("profileFile: %s" % h.get("profileFile"), flush=True)
    path = h.get("profileFile")
    if not path:
        P.row("saves_folder", None, "the handshake gave no profileFile")
        return 2
    saves = os.path.join(os.path.dirname(os.path.dirname(path)), "Saves")
    files = [os.path.join(saves, n + ".rws") for n in (FREE, CANON)]
    try:
        if not P.quicktest():
            P.row("quicktest", None, "no map")
            return 2
        profile("a_new_game_is_test", "", "test")
        P.call("rimworld/save_game", saveName=FREE)
        if not os.path.isfile(files[0]):
            P.row("save", None, "no file %s" % files[0])
            return 2
        shutil.copyfile(files[0], files[1])
        if load(CANON):
            profile("a_canonical_name_is_campaign", CANON, "campaign")
        if load(FREE):
            profile("the_same_save_under_a_test_name_is_test", FREE, "test")
    finally:
        for f in files:
            if os.path.isfile(f):
                os.remove(f)
    got = [v for _, v in P.ROWS]
    return 1 if "FAIL" in got else 2 if "UNMEASURED" in got or len(got) < 3 else 0


if __name__ == "__main__":
    sys.exit(main())
