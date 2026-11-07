#!/usr/bin/env python3
"""selftest_save_uncompress -- offline checks of modcheck/save_uncompress.py on a small fake save (no game)."""
import atexit
import os
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET

tempfile.tempdir = os.environ["TMPDIR"] = tempfile.mkdtemp(prefix="st_selftest_save_uncompress_")
atexit.register(shutil.rmtree, tempfile.tempdir, True)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import save_uncompress as U  # noqa: E402

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

if FAILS:
    print("FAIL: %d: %s" % (len(FAILS), FAILS))
    sys.exit(1)
print("PASS")
