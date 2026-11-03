#!/usr/bin/env python3
"""Offline selftest of taozin_nest_live.py (TAOZIN_SPLIT_BUILD_ONE_WORM_BECOMES_TWO L2/L3): the verdict logic on canned
bridge rows, every mutant the checker named goes red, and the script's constants are pinned to the shipped defs.

    python3 src/RimStarWars/SWBestiary/selftest_taozin_nest_live.py    (exit 0 = clean)
"""
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import taozin_nest_live as L  # noqa: E402

FAILS = []


def check(ok, what):
    print(("ok   " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


def thing(d, i, x, z, **kw):
    t = {"def": d, "id": i, "position": {"x": x, "z": z}}
    t.update(kw)
    return t


GOOD = [thing(L.GRUB, "G1", 100, 100), thing(L.GRUB, "G2", 102, 101), thing(L.GRUB, "G3", 99, 103),
        thing(L.SILK, "S1", 101, 99, stackCount=20), thing(L.SILK, "S2", 98, 101, stackCount=17),
        thing(L.ADULT, "A1", 104, 104),
        thing(L.ADULT, "A9", 10, 10)]          # a roster-row wild adult far off: allowed, not the guard
rc, lines, ids = L.nest(GOOD)
check(rc == 0, "L2 healthy nest holds: %s" % lines)
check(ids == ["G1", "G2", "G3", "A1"], "L2 picks the near adult as the guard: %s" % ids)


def mutant(name, things):
    r = L.nest(things)[0]
    check(r == 1, "L2 mutant goes red: %s (rc %s)" % (name, r))


mutant("no nest at all (patch matched nothing / GenStep never ran)", [GOOD[-1]])
mutant("no grubs, adult and silk only", [t for t in GOOD if t["def"] != L.GRUB])
mutant("one grub", [t for t in GOOD if t["id"] not in ("G2", "G3")])
mutant("five grubs (a grub spawned outside the nest)", GOOD + [thing(L.GRUB, "G4", 101, 100),
                                                               thing(L.GRUB, "G5", 150, 150)])
mutant("no silk", [t for t in GOOD if t["def"] != L.SILK])
mutant("four silk stacks", GOOD + [thing(L.SILK, "S3", 100, 101), thing(L.SILK, "S4", 101, 101)])
mutant("silk far from the nest", [t for t in GOOD if t["id"] != "S2"] + [thing(L.SILK, "S2", 160, 40)])
mutant("no guarding adult", [t for t in GOOD if t["def"] != L.ADULT])
mutant("only a far adult", [t for t in GOOD if t["id"] != "A1"])
mutant("the near adult is owned", [t for t in GOOD if t["id"] != "A1"] + [thing(L.ADULT, "A1", 104, 104,
                                                                               faction="PlayerColony")])
mutant("the near adult is dead", [t for t in GOOD if t["id"] != "A1"] + [thing(L.ADULT, "A1", 104, 104, dead=True)])

# L3 art
BY_ID = {t["id"]: t["def"] for t in GOOD}
HOLD = ["mandrake.rsw.swbestiary"]


def ex_ok(pid):
    return {"success": True, "appearance": {"paths": [
        {"role": "body", "texPath": L.EXPECTED_BODY[BY_ID[pid]], "packsHoldingPath": HOLD},
        {"role": "body (female)", "texPath": "x", "packsHoldingPath": []}]}}


r, lines = L.art(ids, BY_ID, ex_ok)
check(r == 0, "L3 healthy art holds: %s" % lines)


def art_mutant(name, fn, want=1, use=None):
    r = L.art(ids if use is None else use, BY_ID, fn)[0]
    check(r == want, "L3 mutant -> %d: %s (rc %s)" % (want, name, r))


def wrong_path(pid):
    e = ex_ok(pid)
    if BY_ID[pid] == L.ADULT:
        e["appearance"]["paths"][0]["texPath"] = "swanimals/Taozin/Taozin"   # the art the owner removed
    return e


def unheld(pid):
    e = ex_ok(pid)
    if BY_ID[pid] == L.GRUB:
        e["appearance"]["paths"][0]["packsHoldingPath"] = []                  # texture missing: BadTex
    return e


art_mutant("adult draws the old donor art", wrong_path)
art_mutant("grub texture held by no pack", unheld)
art_mutant("no body row", lambda pid: {"success": True, "appearance": {"paths": [{"role": "head", "texPath": "x"}]}})
art_mutant("appearance unread", lambda pid: {"success": False}, want=2)
art_mutant("no nest pawns to read", ex_ok, want=2, use=[])
art_mutant("grubs only, no guard", ex_ok, want=2, use=["G1", "G2"])

# Constants pinned to the shipped defs.
nest = ET.parse(os.path.join(HERE, "Defs", "MapGeneration", "RSW_TaozinNest.xml")).getroot()
pw = [e for e in nest.iter("li") if e.findtext("kind") == L.GRUB]
th = [e for e in nest.iter("li") if e.findtext("thing") == L.SILK]
check(pw and pw[0].findtext("count") == "%d~%d" % (L.GRUB_MIN, L.GRUB_MAX), "GRUB_MIN..MAX = nest count")
check(th and th[0].findtext("stacks") == "%d~%d" % (L.SILK_MIN, L.SILK_MAX), "SILK_MIN..MAX = nest stacks")
an = [e for e in nest.iter("li") if (e.get("Class") or "").endswith("AnchoredPawn")]
check(an and an[0].findtext("pawnKind") == L.ADULT, "the anchored pawn is L.ADULT")
for d in (L.ADULT, L.GRUB):
    root = ET.parse(os.path.join(HERE, "Defs", "ThingDefs_Races", d + ".xml")).getroot()
    kinds = [k for k in root if k.tag == "PawnKindDef" and k.findtext("defName") == d]
    tps = [k.findtext("lifeStages/li/bodyGraphicData/texPath") for k in kinds]
    check(tps == [L.EXPECTED_BODY[d]], "EXPECTED_BODY[%s] = the kind's body texPath %s" % (d, tps))
check(L.SPEC.BIOME == "RM_Abyss" and set(L.SPEC.TILE) >= {"temperature", "rainfall", "elevation", "hilliness",
                                                          "swampiness"}, "SPEC carries what biome_site reads")
check(L.SPEC.TILE["hilliness"] in ("Flat", "SmallHills", "LargeHills", "Mountainous"), "SPEC hilliness is settleable")

# L4: the proof file's own L4 line, run against synthetic logs, goes red on a texture error naming either creature.
import shlex, subprocess, tempfile  # noqa: E401,E402
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
with open(os.path.join(REPO, "infrastructure", "state", "live_proofs",
                       "TAOZIN_SPLIT_BUILD_ONE_WORM_BECOMES_TWO.txt"), encoding="utf-8") as fh:
    l4 = [ln.split(":", 1)[1].strip() for ln in fh if ln.startswith("live-proof L4:")]
check(len(l4) == 1, "the proof file has one L4 line")
for tex, want in (("Things/Pawn/Animal/RSW_Taozin/RSW_Taozin", 1), ("Things/Pawn/Animal/RSW_TaozinGrub/RSW_TaozinGrub", 1),
                  (None, 0)):
    with tempfile.NamedTemporaryFile("w", suffix=".log", delete=False) as fh:
        fh.write("Bridge token: x\n")
        fh.write("Failed to find any textures at %s while constructing Multi(initPath=%s)\n" % (tex, tex) if tex
                 else "Loaded RSW_Taozin and RSW_TaozinGrub\n")
    argv = shlex.split(l4[0]) + ["--log", fh.name] if l4 else ["false"]
    rc = subprocess.run(argv, cwd=REPO, capture_output=True, timeout=60).returncode
    os.unlink(fh.name)
    check(rc == want, "L4 on a log %s exits %d (got %d)" % ("naming " + tex if tex else "with no texture error", want, rc))

print("FAILS: %d" % len(FAILS))
sys.exit(1 if FAILS else 0)
