#!/usr/bin/env python3
"""selftest_save_uncompress -- offline checks of modcheck/save_uncompress.py on a small fake save (no game)."""
import atexit
import json
import os
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET

tempfile.tempdir = os.environ["TMPDIR"] = tempfile.mkdtemp(prefix="st_selftest_save_uncompress_")
atexit.register(shutil.rmtree, tempfile.tempdir, True)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import save_uncompress as U  # noqa: E402
import prove_chunks_v2_control as C  # noqa: E402
import test_site_saves as T  # noqa: E402

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "rimflow"))
import relentless_live_round as LR  # noqa: E402

FAILS = []


def check(name, ok, detail=""):
    print("%s %s %s" % ("ok  " if ok else "FAIL", name, detail if not ok else ""))
    if not ok:
        FAILS.append(name)


# 1. the hash is the engine's. Each value is a cell or a log line of the real fixture and session
#    (RM_TestSite_calm_v2 + Player_ee0fbaa8.log), so a wrong port cannot pass by agreeing with itself.
for name, want in (("ChunkMarble", 45390), ("ChunkLimestone", 11383), ("ChunkSlate", 62054), ("Limestone", 64138),
                   ("Slate", 54213), ("Marble", 64468), ("MineableComponentsIndustrial", 43357),
                   ("MineableUranium", 7015), ("KotORBlasterBolt_ioncharger", 7015)):
    check("1 raw hash %s" % name, U.raw_hash(name) == want, U.raw_hash(name))

# 2. every hash the real fixture holds names the def the session's counts say it is; MineableSteel sits one above its raw
#    hash (Meat_Squirrel took 27292); RaisedRocks at 8309 must not contest MineableJade at 8319
REAL = {45390: "ChunkMarble", 64138: "Limestone", 11383: "ChunkLimestone", 62054: "ChunkSlate", 27293: "MineableSteel",
        54213: "Slate", 64468: "Marble", 43357: "MineableComponentsIndustrial", 7015: "MineableUranium", 8319: "MineableJade"}
check("2 the real fixture's hashes resolve", U.resolve(set(REAL), U.COMPRESSIBLE) == REAL)
for bad_vals, why in (({1}, "no known"), ({45390, 45391}, "two values")):
    try:
        U.resolve(bad_vals, U.COMPRESSIBLE)
        check("2 refuses %s" % why, False)
    except ValueError as e:
        check("2 refuses %s" % why, why in str(e), e)

# 3. expand
W = 4
CELLS = [0] * (W * W)
CELLS[1] = U.raw_hash("ChunkMarble")       # (1, 0)
CELLS[6] = U.raw_hash("MineableUranium")   # (2, 1)
CELLS[15] = 27293                          # (3, 3) MineableSteel, probed
SLAG = ("<thing>\n<def>ChunkMechanoidSlag</def>\n<id>ChunkMechanoidSlag10</id>\n<map>0</map>\n<pos>(0, 0, 0)</pos>\n"
        "<health>300</health>\n</thing>")
BLOCK = ('<thing Class="ThingWithComps">\n<def>Techprint_JumpPack</def>\n<id>Techprint_JumpPack11</id>\n<map>0</map>\n'
         "<stackCount>1</stackCount>\n</thing>")
SAVE = ("<savegame><game><uniqueIDsManager><nextThingID>100</nextThingID></uniqueIDsManager><maps><li>"
        "<mapInfo><size>(%d, 1, %d)</size></mapInfo><compressedThingMapDeflate>%s</compressedThingMapDeflate>"
        "<things>%s%s</things></li></maps></game></savegame>") % (W, W, U.write_grid(CELLS), SLAG, BLOCK)
new, census, stacks = U.expand_text(SAVE)
root = ET.fromstring(new)
rows = {t.find("def").text: t for t in root.iter("thing")}
check("3 parses and holds every thing", len(list(root.iter("thing"))) == 5, list(rows))
check("3 census", census == {"ChunkMarble": 1, "MineableUranium": 1, "MineableSteel": 1}, census)
check("3 grid emptied", not any(U.read_grid(next(root.iter("compressedThingMapDeflate")).text)))
check("3 cell index is x + z*width", rows["ChunkMarble"].find("pos").text == "(1, 0, 0)"
      and rows["MineableUranium"].find("pos").text == "(2, 0, 1)" and rows["MineableSteel"].find("pos").text == "(3, 0, 3)")
check("3 rock is a Mineable at full health", rows["MineableUranium"].get("Class") == "Mineable"
      and rows["MineableUranium"].find("health").text == "4000")
check("3 a chunk is a bare Thing with a stack", rows["ChunkMarble"].get("Class") is None
      and rows["ChunkMarble"].find("stackCount").text == "1")
check("3 rock takes no stackCount", rows["MineableUranium"].find("stackCount") is None)
check("3 an old full chunk gains a stackCount", stacks == 1 and rows["ChunkMechanoidSlag"].find("stackCount").text == "1")
check("3 ids are fresh and the counter moved", rows["ChunkMarble"].find("id").text == "ChunkMarble100"
      and next(root.iter("nextThingID")).text == "103")

# 4. check: passes the expansion, and fails each thing that broke the real load
bad, seen = U.problems(new, {"ChunkMarble": 1, "MineableUranium": 1, "ChunkMechanoidSlag": 1})
check("4 expansion is clean", not bad and seen["ChunkMarble"] == 1, bad)
bad, _ = U.problems(SAVE)
check("4 a compressed save fails", any("3 cells still compressed" in b for b in bad), bad)
check("4 a stackless chunk fails", any("no stackCount" in b for b in bad), bad)
bad, _ = U.problems(new, {"ChunkMarble": 2})
check("4 a wrong count fails", any("expected 2" in b for b in bad), bad)
bad, _ = U.problems(new.replace("<nextThingID>103<", "<nextThingID>50<"))
check("4 a stale id counter fails", any("nextThingID" in b for b in bad), bad)
bad, _ = U.problems(new.replace("ChunkMarble100", "ChunkMarble101"))
check("4 a duplicate id fails", any("duplicate" in b for b in bad), bad)
bad, _ = U.problems("<savegame/>")
check("4 no map is not a pass", any("no compressed" in b for b in bad), bad)

# 5. files: expand never overwrites; expand_fresh replaces, and deletes what it cannot name
d = tempfile.mkdtemp()
src, dst = os.path.join(d, "a.rws"), os.path.join(d, "b.rws")
with open(src, "w", encoding="utf-8") as f:
    f.write(SAVE)
r = U.expand(src, dst)
check("5 expand writes", os.path.isfile(dst) and r["stackCountsAdded"] == 1 and open(src, encoding="utf-8").read() == SAVE)
for a, b, why in ((src, dst, "exists"), (src, src, "same")):
    try:
        U.expand(a, b)
        check("5 refuses %s" % why, False)
    except ValueError as e:
        check("5 refuses %s" % why, why in str(e), e)
check("5 check exit 0", U.main(["check", dst, "--expect", "ChunkMarble=1"]) == 0)
check("5 check exit 1", U.main(["check", src]) == 1)
check("5 check exit 2 when absent", U.main(["check", os.path.join(d, "none.rws")]) == 2)
fresh = os.path.join(d, "fresh.rws")
shutil.copy(src, fresh)
check("5 fresh expands in place", U.expand_fresh(fresh)["cells"]["ChunkMarble"] == 1 and not U.problems(open(fresh, encoding="utf-8").read())[0])
with open(fresh, "w", encoding="utf-8") as f:
    f.write(SAVE.replace(U.write_grid(CELLS), U.write_grid([1] + CELLS[1:])))
try:
    U.expand_fresh(fresh)
    check("5 fresh refuses an unknown hash", False)
except RuntimeError as e:
    check("5 fresh refuses an unknown hash", not os.path.exists(fresh) and "no known" in str(e), e)

# 6. the live verdicts
LINE = U.LOAD_LINE % "S"
check("6 no load line is unmeasured", U.log_verdict("nothing", "S")[0].startswith("UNMEASURED"))
check("6 a later load is unmeasured", U.log_verdict(LINE + "\nLoading game from file T with mods:\n", "S")[0].startswith("UNMEASURED"))
check("6 a clean load", U.log_verdict(LINE + "\nfine\n", "S") == (None, 0))
check("6 lines before the load do not count", U.log_verdict(U.BAD_LOG[0] + "\n" + LINE + "\n", "S")[1] == 0)
for s in U.BAD_LOG:
    check("6 counts: %s" % s[:24], U.log_verdict(LINE + "\n" + s + ": x\n", "S")[1] == 1)
check("6 things enough", U.things_verdict([{"defName": "A"}, {"defName": "A"}], {"A": 2}) == [])
check("6 things short", U.things_verdict([{"defName": "A"}], {"A": 2}) != [])

# 7. the repoint: every load of the calm site reads the expanded fixture, in the code and in the registry
check("7 SITES calm is v3", T.SITES["calm"]["save"] == "RM_TestSite_calm_v3", T.SITES["calm"]["save"])
with open(T.REGISTRY, encoding="utf-8") as f:
    REG = json.load(f)
check("7 the registry's calm is v3", REG["calm"]["save"] == "RM_TestSite_calm_v3", REG["calm"]["save"])

# 8. the game lines: A1 reads v3 and A2 reads v2, both on a list that holds what causes the fault
with open(os.path.join(REPO, LR.PROOFS_DIR, "CHUNKS_FIX_SAVE_ERRORS_NOT_DEAD_NAMES.txt"), encoding="utf-8") as f:
    LIVE = f.read()
MODS = LR.live_mods(LIVE)
check("8 the list holds the chunk patch", "Elshender.stackablechunks" in MODS, MODS)
check("8 the list holds the hash thief", "Armoury" in MODS, MODS)
for cid, save, tool in (("A1", "RM_TestSite_calm_v3", "save_uncompress.py live "), ("A2", "RM_TestSite_calm_v2", "prove_chunks_v2_control.py live ")):
    check("8 %s stages %s" % (cid, save), LR.site_for(LIVE, cid).endswith("--save " + save), LR.site_for(LIVE, cid))
    check("8 %s reads %s" % (cid, save), tool + save + " " in LR.proof_lines(LIVE).get(cid, ""), LR.proof_lines(LIVE).get(cid))
ALLD = "ChunkMarble=589,ChunkLimestone=566,ChunkSlate=549,MineableUranium=34"
check("8 A2 asks after all four lost defs", LR.proof_lines(LIVE)["A2"].endswith("--lost " + ALLD), LR.proof_lines(LIVE)["A2"])
check("8 A1 still asks after them", ALLD in LR.proof_lines(LIVE)["A1"], LR.proof_lines(LIVE)["A1"])

# 9. the control's verdicts, on logs shaped like the two real ones
FULL = "  - elshender.stackablechunks\n  - mandrake.rsw.armoury\n"
TIER = "  - mandrake.rm.flowworks\n"
LOADV2 = U.LOAD_LINE % C.V2 + "\n"
RED = LOADV2 + FULL + (U.BAD_LOG[0] + ": x\n") * C.RED_LINES_AT_LEAST
CLEAN = LOADV2 + TIER + "fine\n"
check("9 mods are read under the load line only", C.mods_of(LOADV2 + TIER + "words\n  - not.amod\n") == {"mandrake.rm.flowworks"})
check("9 the slice stops at the next load", C.load_slice(RED + U.LOAD_LINE % "Z" + "\nzz", C.V2, "first") == RED)
check("9 the two records hold", C.offline_problems(RED, CLEAN) == [], C.offline_problems(RED, CLEAN))
check("9 a red log without the mods fails", any("lacks" in b for b in C.offline_problems(RED.replace(FULL, TIER), CLEAN)))
check("9 a red log gone quiet fails", any("bad lines" in b for b in C.offline_problems(LOADV2 + FULL, CLEAN)))
check("9 a later load's lines do not make the first red", any("bad lines" in b for b in
      C.offline_problems(LOADV2 + FULL + U.LOAD_LINE % "Z" + "\n" + (U.BAD_LOG[0] + "\n") * C.RED_LINES_AT_LEAST, CLEAN)))
check("9 a contrast with the mods fails", any("no contrast" in b for b in C.offline_problems(RED, CLEAN.replace(TIER, FULL))))
check("9 a contrast that is not clean fails", any("reads" in b for b in C.offline_problems(RED, CLEAN + U.BAD_LOG[0])))
check("9 a contrast with no list fails", any("no mods" in b for b in C.offline_problems(RED, LOADV2 + "fine\n")))
check("9 no load line is unmeasured", C.offline_problems("x", CLEAN)[0].startswith("UNMEASURED"))
RUN = set(C.FAULT_MODS)
LOST = {"ChunkMarble": 2, "MineableUranium": 1}
check("9 live: all lost is red", C.control_verdict([], LOST, RUN)[0] == "red")
check("9 live: too few of a def still counts as lost", C.control_verdict([{"defName": "ChunkMarble"}], LOST, RUN)[0] == "red")
check("9 live: a def that stood is blind", C.control_verdict([{"defName": "MineableUranium"}], LOST, RUN)[0] == "blind")
check("9 live: all stood is blind", C.control_verdict([{"defName": "ChunkMarble"}] * 2 + [{"defName": "MineableUranium"}], LOST, RUN)[0] == "blind")
for gone in C.FAULT_MODS:
    kind, lines = C.control_verdict([], LOST, RUN - {gone})
    check("9 live: %s absent asks for a reload" % gone, kind == "unmeasured" and lines[-1].startswith("reload needed:"), lines)
d = tempfile.mkdtemp()
red, clean = os.path.join(d, "r.log"), os.path.join(d, "c.log")
for path, text in ((red, RED), (clean, CLEAN)):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
check("9 offline exit 0", C.main(["offline", "--red", red, "--clean", clean]) == 0)
check("9 offline exit 1", C.main(["offline", "--red", clean, "--clean", clean]) == 1)
check("9 offline exit 2 when absent", C.main(["offline", "--red", red + "x", "--clean", clean]) == 2)

if FAILS:
    print("FAIL: %d: %s" % (len(FAILS), FAILS))
    sys.exit(1)
print("PASS")
