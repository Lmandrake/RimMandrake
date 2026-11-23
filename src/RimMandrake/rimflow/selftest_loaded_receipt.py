#!/usr/bin/env python3
"""Selftest: the receipt of what a running game has loaded. Page: design/specs/2026-11-23-loaded-receipt/boundary.md; one test
per promise. The C# half (JawaBenchReceiptCore.cs) is built and run offline; the Python half (loaded_build.py) reads made
receipts and made folders. No game, no bridge. Without dotnet.exe the C# tests FAIL as UNMEASURED.
Run: python3 src/RimMandrake/rimflow/selftest_loaded_receipt.py"""
import contextlib
import copy
import io
import json
import os
import sys
import tempfile
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
import build_match as B        # noqa: E402
import live_tools_units as L   # noqa: E402
import loaded_build as LB      # noqa: E402

GOOD, BAD = uuid.uuid4(), uuid.uuid4()
IDS = ["Ludeon.RimWorld", "brrainz.harmony_steam", "mandrake.rm.testmod"]


def say(ok, what):
    print("%s  %s" % ("ok  " if ok else "FAIL", what))
    return bool(ok)


def dll_bytes(mvid):
    return b"MZ" + os.urandom(300) + mvid.bytes_le + os.urandom(50)


def write(p, raw):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as f:
        f.write(raw)
    return p


def reply(mvid=GOOD, **over):
    r = {"success": True, "packageIds": list(IDS), "ticksGame": 4711, "loaded": {
        "gameKey": "archmagi.b", "listFingerprint": LB.fingerprint(IDS), "mods": [{
            "packageId": "mandrake.rm.testmod", "state": "LOADED", "why": None, "assemblies": [
                {"name": "TestMod", "location": "C:\\Mods\\TestMod\\Assemblies\\TestMod.dll", "mvid": str(mvid),
                 "fileHoldsLoadedCode": True}]}]}}
    r.update(over)
    return r


class Case(object):
    """A deployed and a committed DLL, and judge() on them."""

    def __init__(self, dep=GOOD, src=GOOD):
        d = tempfile.mkdtemp(prefix="loaded_receipt_")
        self.dep = {"testmod.dll": [write(os.path.join(d, "dep", "Assemblies", "TestMod.dll"), dll_bytes(dep))]}
        self.src = {"testmod.dll": [write(os.path.join(d, "src", "Assemblies", "TestMod.dll"), dll_bytes(src))]}

    def verdict(self, r, ids=IDS, **kw):
        out = LB.judge(r, "mandrake.rm.testmod", kw.pop("dep", self.dep), kw.pop("src", self.src), ids, **kw)
        self.out = out
        return out["verdict"]


def t_the_fingerprint_is_the_same_in_game_and_in_python():
    good = True
    lists = [IDS, list(reversed(IDS)), IDS[:2], [], ["A_STEAM", "a"], ["mandrake.rm.x"]]
    for ids in lists:
        got = L.run("fingerprint", ",".join(ids)).stdout.strip()
        good &= say(got == LB.fingerprint(ids), "C# and Python agree on %d ids (%s)" % (len(ids), got[:20]))
    f = LB.fingerprint
    good &= say(f(IDS) == f(["ludeon.rimworld", "BRRAINZ.harmony", "mandrake.rm.testmod"]), "case and _steam do not change it")
    good &= say(len({f(x) for x in lists}) == len(lists), "a swap, a missing mod and an empty list each change it")
    return good


def t_the_game_key_is_read_from_the_games_own_folders():
    return L.group("gamekey", [])


def t_a_dll_holds_its_own_mvid_and_no_other():
    good = L.group("mvid", ["mvid"])
    raw = dll_bytes(GOOD)
    good &= say(LB.holds_mvid(raw, str(GOOD)) is True and LB.holds_mvid(raw, str(BAD)) is False, "Python: own id yes, another no")
    good &= say(all(LB.holds_mvid(*a) is None for a in ((b"", GOOD), (None, GOOD), (raw, None), (raw, "x"), (raw, uuid.UUID(int=0)))),
                "Python: no bytes or no id is could-not-read, never no")
    return good


def t_a_mod_state_names_the_first_fault():
    return L.group("modstate", ["filechanged"])


def t_a_wrong_build_is_red_and_the_right_one_is_green():
    good = say(Case().verdict(reply()) == LB.MATCH, "the loaded id in both files: MATCH")
    for dep, src, word in ((BAD, GOOD, "deployed"), (GOOD, BAD, "committed"), (BAD, BAD, "deployed or the committed")):
        c = Case(dep, src)
        good &= say(c.verdict(reply()) == LB.WRONG_BUILD and word in " ".join(c.out["why"]), "not in the %s file: WRONG_BUILD (%s)" % (word, c.out["why"]))
    r = reply()
    r["loaded"]["mods"][0]["assemblies"][0]["fileHoldsLoadedCode"] = False
    good &= say(Case().verdict(r) == LB.WRONG_BUILD, "the file changed after the load: WRONG_BUILD")
    r = reply()
    r["loaded"]["mods"][0]["assemblies"] = []
    good &= say(Case().verdict(r) == LB.NOT_LOADED, "a DLL that is not loaded: NOT_LOADED")
    r = reply()
    r["loaded"]["mods"][0].update(state="FOREIGN_COPY", why="TestMod was loaded from C:\\Mods\\Other")
    good &= say(Case().verdict(r) == LB.FOREIGN, "loaded from another mod's folder: FOREIGN_COPY")
    c = Case()
    good &= say(c.verdict(reply(), src={}) == LB.WRONG_BUILD, "a deployed DLL the commit does not have: WRONG_BUILD")
    two = dict(c.dep, **{"b.dll": c.dep["testmod.dll"]})
    good &= say(c.verdict(reply(), dep=two) == LB.NOT_LOADED, "a second deployed DLL that is not loaded: NOT_LOADED")
    good &= say(Case().verdict(reply(BAD)) == LB.WRONG_BUILD, "an older build is loaded: WRONG_BUILD")
    return good


def t_a_wrong_list_is_red():
    good = True
    for want, what in ((IDS[:2], "one fewer"), (IDS[::-1], "reordered"), (IDS + ["x.y"], "one more"), ([], "empty")):
        c = Case()
        good &= say(c.verdict(reply(), ids=want) == LB.WRONG_LIST and "first difference" in " ".join(c.out["why"]), "%s: WRONG_LIST %s" % (what, c.out["why"]))
    good &= say(Case().verdict(reply(), ids=["ludeon.rimworld", "brrainz.harmony", "Mandrake.RM.TestMod"]) == LB.MATCH, "case and _steam only: MATCH")
    good &= say(Case().verdict(reply(), ids=None) == LB.BLIND, "no expected list: COULD_NOT_LOOK")
    r = reply()
    r["packageIds"] = IDS[:1] + IDS[2:]
    good &= say(Case().verdict(r, ids=r["packageIds"]) == LB.BLIND, "a list that is not the fingerprint's: COULD_NOT_LOOK")
    return good


def t_a_wrong_game_is_red():
    good = say(Case().verdict(reply(), expected_game="archmagi.b") == LB.MATCH, "the expected game: MATCH")
    c = Case()
    good &= say(c.verdict(reply(), expected_game="archmagi") == LB.WRONG_GAME and "archmagi.b" in c.out["why"][0], "another game: WRONG_GAME")
    r = reply()
    r["loaded"]["gameKey"] = None
    good &= say(Case().verdict(r, expected_game="archmagi.b") == LB.BLIND, "no game key: COULD_NOT_LOOK")
    good &= say(Case().verdict(r) == LB.MATCH, "no game asked for: the key does not decide")
    return good


def t_could_not_look_is_never_match():
    good = True
    for r, what in ((None, "no reply"), ({"success": False, "message": "x"}, "a failed reply"), ("text", "not a reply"),
                    ({"success": True, "packageIds": IDS}, "no loaded part (an older companion)"),
                    (reply(packageIds=[]), "an empty running list"), ({}, "an empty reply")):
        c = Case()
        v = c.verdict(r)
        good &= say(v == LB.BLIND and c.out["why"] and LB.EXIT.get(v, 1) == 2, "%s: %s %s" % (what, v, c.out["why"]))
    r = reply()
    r["loaded"]["mods"] = []
    good &= say(Case().verdict(r) == LB.BLIND, "in the running list and not in the receipt: COULD_NOT_LOOK")
    r2 = copy.deepcopy(r)
    r2["packageIds"] = IDS[:2]
    r2["loaded"]["listFingerprint"] = LB.fingerprint(IDS[:2])
    good &= say(Case().verdict(r2, ids=IDS[:2]) == LB.NOT_LOADED, "the mod is not in the running list: NOT_LOADED")
    c = Case()
    good &= say(c.verdict(reply(), dep=None) == LB.BLIND and c.verdict(reply(), src=None) == LB.BLIND, "a folder that cannot be read: COULD_NOT_LOOK")
    good &= say(c.verdict(reply(), dep={"testmod.dll": ["/nonexistent/x.dll"]}) == LB.BLIND, "an unreadable DLL: COULD_NOT_LOOK")
    v = c.verdict(reply(), dep={}, src={})
    good &= say(v == LB.NO_ASM and LB.EXIT[v] == 4, "a mod with no DLL: NO_ASSEMBLY, exit 4, never MATCH")
    r = reply()
    r["loaded"]["mods"][0]["state"] = "COULD_NOT_READ"
    good &= say(Case().verdict(r) == LB.BLIND, "the game could not read the mod: COULD_NOT_LOOK")
    good &= say(LB.EXIT.get(LB.WRONG_BUILD, 1) == 1 and LB.EXIT[LB.MATCH] == 0, "exit codes: fault 1, match 0")
    # the command line, end to end on a file, against a made install
    d = tempfile.mkdtemp(prefix="loaded_receipt_cli_")
    about = "<ModMetaData><packageId>mandrake.rm.testmod</packageId></ModMetaData>"
    for base in (os.path.join(d, "root", "src", "RimMandrake", "TestMod"), os.path.join(d, "Mods", "TestMod")):
        write(os.path.join(base, "About", "About.xml"), about.encode())
        write(os.path.join(base, "Assemblies", "TestMod.dll"), dll_bytes(GOOD))
    cfg = os.path.join(d, "ModsConfig.xml")
    write(cfg, ("<c><activeMods>%s</activeMods></c>" % "".join("<li>%s</li>" % i for i in IDS)).encode())
    real, inst = B._paths, B._installed_only
    B._paths = lambda: (os.path.join(d, "Mods"), cfg, None)
    B._installed_only = lambda am, m, scan=None: (am, [], [])
    try:
        for mvid, want in ((GOOD, 0), (BAD, 1)):
            f = write(os.path.join(d, "r.json"), json.dumps({"content": [{"text": json.dumps(reply(mvid))}]}).encode())
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = B.main(["loaded", "--mod", "TestMod", "--receipt", f, "--game", "ArchSmall", "--root", os.path.join(d, "root")])
            good &= say(rc == want, "build_match.py loaded exits %d: %s" % (rc, buf.getvalue()[:120]))
        with contextlib.redirect_stdout(io.StringIO()):
            rc = B.main(["loaded", "--mod", "TestMod", "--receipt", os.path.join(d, "absent.json"), "--root", os.path.join(d, "root")])
        good &= say(rc == 2, "a receipt file that is not there: exit %d" % rc)
    finally:
        B._paths, B._installed_only = real, inst
    return good


def main():
    try:
        res = [t_the_fingerprint_is_the_same_in_game_and_in_python(), t_the_game_key_is_read_from_the_games_own_folders(),
               t_a_dll_holds_its_own_mvid_and_no_other(), t_a_mod_state_names_the_first_fault(),
               t_a_wrong_build_is_red_and_the_right_one_is_green(), t_a_wrong_list_is_red(), t_a_wrong_game_is_red(),
               t_could_not_look_is_never_match()]
    except L.Unmeasured as e:
        print("FAIL loaded receipt UNMEASURED: %s" % e)
        return 1
    print("loaded receipt: %d of %d promises hold" % (sum(res), len(res)))
    return 0 if all(res) else 1


if __name__ == "__main__":
    sys.exit(main())
