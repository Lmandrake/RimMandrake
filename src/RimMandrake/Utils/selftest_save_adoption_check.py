#!/usr/bin/env python3
"""selftest_save_adoption_check.py -- a synthetic save and synthetic def dumps; each planted defect must be found."""
import base64
import os
import struct
import sys
import tempfile
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import defindex as D  # noqa: E402
import save_adoption_check as S  # noqa: E402

FAILS = []
N = [0]


def check(cond, what, extra=None):
    N[0] += 1
    print(("ok   " if cond else "FAIL ") + what + ("" if cond or extra is None else "  %s" % (extra,)))
    if not cond:
        FAILS.append(what)


def grid(hashes):
    c = zlib.compressobj(9, zlib.DEFLATED, -15)
    return base64.b64encode(c.compress(struct.pack("<%dH" % len(hashes), *hashes)) + c.flush()).decode()


SAVE = """<?xml version="1.0" encoding="utf-8"?>
<savegame><meta><modIds><li>ludeon.rimworld</li></modIds></meta><game>
<world><landmarks><landmarks><keys><li>2540,0</li><li>7,0</li></keys>
<values><li><def>AB_MagmaticQuagmire</def><name>Leneunt</name></li><li><def>AncientHeatVent</def><name>ok</name></li></values>
</landmarks></landmarks><tileBiomeDeflate>{tb}</tileBiomeDeflate>
<worldPawns><pawnsAlive><li><def>AA_Ghostling</def><kindDef>AA_Ghostling</kindDef><id>AA_Ghostling1</id></li></pawnsAlive></worldPawns>
</world>
<maps><li><things>
<thing Class="Pawn"><def>Human</def><kindDef>Colonist</kindDef><id>Human470530</id><name Class="NameTriple"><first>Yeku</first></name>
 <social><directRelations><li><def>Bond</def><otherPawn>Thing_AA_Eyeling669122</otherPawn></li></directRelations></social></thing>
<thing Class="Pawn"><def>AA_Eyeling</def><kindDef>AA_Eyeling</kindDef><id>AA_Eyeling669122</id><pos>(175, 0, 134)</pos>
 <faction>Faction_21</faction><name Class="NameSingle"><name>Marquee</name></name></thing>
<thing Class="Building"><def>AB_Mech_RuinedCell</def><id>AB_Mech_RuinedCell1</id><pos>(1, 0, 2)</pos></thing>
<thing Class="Building"><def>AB_Mech_RuinedCell</def><id>AB_Mech_RuinedCell2</id><pos>(3, 0, 4)</pos></thing>
<thing><def>Steel</def><stuff>RSW_NoSuchChitin</stuff><faction>Faction_21</faction></thing>
</things><terrainGrid><topGridDeflate>{tg}</topGridDeflate></terrainGrid></li></maps></game></savegame>
"""


def main():
    U = D.Index({"capture": "U", "mods": ["ludeon.rimworld", "sarg.alphabiomes", "sarg.alphaanimals",
                                          "sarg.alphamemes"],
                 "defs": [["ThingDef_AlienRace", "Human", 1, "ludeon.rimworld"], ["PawnKindDef", "Colonist", 2,
                                                                                  "ludeon.rimworld"],
                          ["ThingDef", "Steel", 3, "ludeon.rimworld"], ["PawnRelationDef", "Bond", 4,
                                                                         "ludeon.rimworld"],
                          ["LandmarkDef", "AncientHeatVent", 5, "ludeon.rimworld"],
                          ["LandmarkDef", "AB_MagmaticQuagmire", 6, "sarg.alphabiomes"],
                          ["ThingDef", "AB_Mech_RuinedCell", 7, "sarg.alphabiomes"],
                          ["ThingDef", "AA_Eyeling", 8, "sarg.alphaanimals"],
                          ["PawnKindDef", "AA_Eyeling", 8, "sarg.alphaanimals"],
                          ["ThingDef", "AA_Ghostling", 9, "sarg.alphaanimals"],
                          ["PawnKindDef", "AA_Ghostling", 9, "sarg.alphaanimals"],
                          ["TerrainDef", "Sand", 100, "ludeon.rimworld"], ["TerrainDef", "AB_Ash", 101,
                                                                           "sarg.alphabiomes"],
                          ["BiomeDef", "Desert", 200, "ludeon.rimworld"], ["BiomeDef", "AB_Fungal", 201,
                                                                           "sarg.alphabiomes"]]})
    pk = ["ludeon.rimworld", "sarg.alphamemes"]
    L = D.Index({"capture": "L", "mods": pk,
                 "defs": [r for r in U.raw["defs"] if r[3] == "ludeon.rimworld"] +
                         [["ThingDef", "AA_Eyeling", 8, "sarg.alphamemes"],
                          ["PawnKindDef", "AA_Eyeling", 8, "sarg.alphamemes"]]})
    d = tempfile.mkdtemp()
    p = os.path.join(d, "s.rws")
    open(p, "w").write(SAVE.format(tb=grid([200, 200, 201]), tg=grid([100, 101, 101, 0])))
    R = S.Resolver(U, L, pk, {})
    root, refs, unknown, control, things, rels, lms, kinds = S.scan(p, R)
    check(control == 1, "control <def>Human</def> is seen", control)
    check("AB_Mech_RuinedCell" in refs and refs["AB_Mech_RuinedCell"]["n"] == 2,
          "PLANTED: a retired-donor building is unresolved, both instances", dict(refs))
    check([lm["def"] for lm in lms] == ["AB_MagmaticQuagmire"], "PLANTED: a retired landmark is found by tile; the "
                                                                 "vanilla one is not", lms)
    eye = [t for t in things if t["id"] == "AA_Eyeling669122"]
    check(eye and eye[0]["rehomed"] and eye[0]["nowFrom"] == ["sarg.alphamemes"],
          "PLANTED: a donor def another list mod ships is RE-HOMED, not dropped", eye)
    ghost = [t for t in things if t["id"] == "AA_Ghostling1"]
    check(ghost and not ghost[0]["rehomed"], "PLANTED: a donor pawn nobody ships is unresolved (dropped)", ghost)
    check(any(r["other"] == "AA_Eyeling669122" and r["relation"] == "Bond" for r in rels),
          "the bond is matched through the Thing_ reference prefix", rels)
    check("RSW_NoSuchChitin @ li/thing/stuff" in " ".join(unknown) or any("RSW_NoSuchChitin" in k for k in unknown),
          "PLANTED: a stuff name no source knows is UNKNOWN (UNMEASURED), not silently fine", dict(unknown))
    check(not any("Faction_21" in k for k in unknown), "a <faction> load ID is not mistaken for a def", dict(unknown))
    text = open(p).read()
    G = {g["grid"]: g for g in S.grids(text, L, U, R)}
    check(G["map terrain"]["lostOnLoad"] == {"hash:101": 2} or "AB_Ash" in str(G["map terrain"]["lostOnLoad"]),
          "PLANTED: a terrain hash the live table lacks is lost on load (2 cells)", G["map terrain"])
    check(G["world tileBiome"]["lostOnLoad"] and G["world tileBiome"]["cells"] == 3,
          "PLANTED: a biome hash the live table lacks is lost on load", G["world tileBiome"])
    W = S.worklist(things, rels, lms, kinds, refs)
    w = "\n".join(W)
    check("Marquee" in w and "Bond with Yeku" in w and "RM_Ikee" in w, "the worklist names the ikee swap and the "
                                                                          "bond to re-create", w)
    check("AB_Mech_RuinedCell x2" in w, "the worklist counts the buildings by def", w)
    blind = os.path.join(d, "blind.rws")
    open(blind, "w").write(SAVE.replace("<def>Human</def>", "<def>Humanish</def>").format(tb=grid([200]),
                                                                                          tg=grid([100])))
    check(S.scan(blind, R)[3] == 0, "BROKEN: a save without the control reads 0, which main() turns into exit 3")
    print("\n%d checks, %d failed" % (N[0], len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
