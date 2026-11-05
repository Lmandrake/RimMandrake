#!/usr/bin/env python3
"""selftest_biomes_port_prune_42.py -- the Biomes! port's buckets A and B stay deleted, and nothing kept broke.

BIOMES_PORT_PRUNE_FORTY_TWO_HITCHHIKERS (owner card 2026-11-04, "Creatures: what do you want queued? -> Drop 42,
cancel Thrumbungus"; survey UNUSED_PORTS_MEASURE_WHAT_NOBODY_NEEDS). ROOTS are the 42 bucket-A/B creatures plus
RSW_ThrumbungusShroom; CLOSURE is every BiomesTeamPort def that only they referenced (eggs, bodies, sounds, damage,
the hornet faction, the shroom's projectile), computed once when they were deleted. This test holds that state:

  1. no def anywhere under src/ is named (defName or Name) in CLOSURE;
  2. no XML under src/ (defs and patches, comments stripped) names a CLOSURE def in a tag, attribute or text;
  3. the tool data that listed them (flyer census/gate, leather lint, pack overlay json, design rosters) do not, and
     the retired generator TheRot/port_fauna.py and the patch RotFauna_KinWiring.xml are gone;
  4. what the item said stays does: RM_Brullith, RM_ThrumbungusShroom, the 18 bucket C/D creatures, the support defs
     used outside the port and every def the closure shared with a kept one;
  5. every RSW_ token left in the BiomesTeamPort files resolves to a def (no egg hatches a deleted larva), apart from
     the tag/need names listed in NOT_DEFS; every texPath left there reaches a picture, and every SoundDef's clip
     folder is on disk;
  6. the redraw item THRUMBUNGUS_ART_REDRAW_CARTOON_NO_MORE is dropped on the ledger;
  7. sanity: the scans find kept names they must see, and a planted row of a dropped creature reads red.
    python3 src/RimStarWars/SWBestiary/selftest_biomes_port_prune_42.py
Exit 0 pass, 1 fail.
"""
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
PORT = SRC / "RimStarWars" / "SWBestiary" / "Defs" / "BiomesTeamPort"
ROOTS = (
    "RSW_AaroxisDendoriaLarvae", "RSW_AaroxisDendoriaPupa", "RSW_AcidSlug", "RSW_Basilisk", "RSW_BloodropLarvae",
    "RSW_BloodropPupa", "RSW_BovineBeetleLarvae", "RSW_BovineBeetlePupa", "RSW_ColonyPustuleHornet",
    "RSW_ColonyPustuleHornetQueen", "RSW_CrystalCrab", "RSW_FacetMoth", "RSW_FacetMothPupa", "RSW_FleeceSpider",
    "RSW_FoundryBeetleLarvae", "RSW_FoundryBeetlePupa", "RSW_FungalMantis", "RSW_FungalWeevil", "RSW_GastroToad",
    "RSW_Glowtail", "RSW_JewelBeetle", "RSW_JewelBeetleLarvae", "RSW_JewelBeetlePupa", "RSW_Maxolotl",
    "RSW_Megakrill", "RSW_Megaphorid", "RSW_MossBeetlePupa", "RSW_MutatingTumorfishAdult",
    "RSW_MutatingTumorfishFry", "RSW_MutatingTumorfishSpawn", "RSW_Polluwog", "RSW_PustuleHornet",
    "RSW_PustuleHornetQueen", "RSW_PustuleHornetSpawned", "RSW_RoyalRhino", "RSW_RoyalRhinoLarvae",
    "RSW_RoyalRhinoPupa", "RSW_SmogMoth", "RSW_SmogMothLarvae", "RSW_SmogPupa", "RSW_Thrumbungus", "RSW_Yooka",
    "RSW_ThrumbungusShroom",
)
CLOSURE = (
    "RSW_AaroxisDendoriaLarvae", "RSW_AaroxisDendoriaPupa", "RSW_AcidSlug", "RSW_AteRawFish", "RSW_Basilisk",
    "RSW_BeetleLikeWithHorn", "RSW_BeetleLikeWithStinger", "RSW_BileHigh", "RSW_BiomesCore_CrabShell",
    "RSW_BiomesCore_CrabThingBase", "RSW_BiomesCore_GreenChitin", "RSW_BiomesCore_Slug", "RSW_BiomesCore_SnailFoot",
    "RSW_BiomesCore_SnailMouth", "RSW_Biomes_BovineBeetle_Angry", "RSW_Biomes_BovineBeetle_Call",
    "RSW_Biomes_BovineBeetle_Death", "RSW_Biomes_BovineBeetle_Wounded", "RSW_Biomes_GiantSnail_Angry",
    "RSW_Biomes_GiantSnail_Call", "RSW_Biomes_GiantSnail_Death", "RSW_Biomes_GiantSnail_Wounded",
    "RSW_Biomes_NamerCrab", "RSW_Biomes_RoyalRhino_Angry", "RSW_Biomes_RoyalRhino_Call",
    "RSW_Biomes_RoyalRhino_Death", "RSW_Biomes_RoyalRhino_Wounded", "RSW_Biomes_Yooka_Angry",
    "RSW_Biomes_Yooka_Call", "RSW_Biomes_Yooka_Death", "RSW_Biomes_Yooka_Wounded", "RSW_BloodSuck",
    "RSW_BloodropLarvae", "RSW_BloodropPupa", "RSW_BluntToxicAttackBase", "RSW_BovineBeetleLarvae",
    "RSW_BovineBeetlePupa", "RSW_BufoBile", "RSW_ColonyPustuleHornet", "RSW_ColonyPustuleHornetQueen",
    "RSW_CrystalCrab", "RSW_EggAcidSlugFertilized", "RSW_EggAcidSlugUnfertilized", "RSW_EggBasiliskFertilized",
    "RSW_EggBasiliskUnfertilized", "RSW_EggFacetMothFertilized", "RSW_EggFacetMothUnfertilized",
    "RSW_EggFleeceSpiderFertilized", "RSW_EggFleeceSpiderUnfertilized", "RSW_EggFungalMantisFertilized",
    "RSW_EggFungalMantisUnfertilized", "RSW_EggFungalWeevilFertilized", "RSW_EggFungalWeevilUnfertilized",
    "RSW_EggGastroToadFertilized", "RSW_EggGastroToadUnfertilized", "RSW_EggGlowtailFertilized",
    "RSW_EggGlowtailUnfertilized", "RSW_EggJewelBeetleFertilized", "RSW_EggJewelBeetleUnfertilized",
    "RSW_EggMaxolotlFertilized", "RSW_EggMaxolotlUnfertilized", "RSW_EggMegakrillFertilized",
    "RSW_EggMegakrillUnfertilized", "RSW_EggMutatingTumorfishFertilized", "RSW_EggMutatingTumorfishUnfertilized",
    "RSW_EggRoyalRhinoFertilized", "RSW_EggRoyalRhinoUnfertilized", "RSW_FacetMoth", "RSW_FacetMothPupa", "RSW_Fin",
    "RSW_FishBody", "RSW_FishGill", "RSW_FishMeatCore", "RSW_FishTail", "RSW_FleeceSpider",
    "RSW_FoundryBeetleLarvae", "RSW_FoundryBeetlePupa", "RSW_FungalMantis", "RSW_FungalWeevil", "RSW_GastroToad",
    "RSW_Glowtail", "RSW_HermaphroditicAnimal", "RSW_HunchedBipedWithTail", "RSW_JewelBeetle",
    "RSW_JewelBeetleLarvae", "RSW_JewelBeetlePupa", "RSW_Leather_Amphibian", "RSW_Leather_Gastropoda",
    "RSW_Maxolotl", "RSW_Megakrill", "RSW_Megaphorid", "RSW_MegaphoridParasiticLarvae", "RSW_MossBeetlePupa",
    "RSW_MothLike", "RSW_MothWing", "RSW_MutatingTumorfishAdult", "RSW_MutatingTumorfishFry",
    "RSW_MutatingTumorfishSpawn", "RSW_Neurotoxin", "RSW_Pawn_Mantis_Call", "RSW_PhoridSting", "RSW_Polluwog",
    "RSW_Proj_ThrumbungusShroom", "RSW_Pupa", "RSW_PupaeThinkTree", "RSW_PustuleHornet", "RSW_PustuleHornetQueen",
    "RSW_PustuleHornetRaidLootMaker", "RSW_PustuleHornetSpawned", "RSW_PustuleHornetStinger", "RSW_PustuleHornets",
    "RSW_RWBLeftEyeStalk", "RSW_RWBRightEyeStalk", "RSW_RoyalRhino", "RSW_RoyalRhinoHorn", "RSW_RoyalRhinoLarvae",
    "RSW_RoyalRhinoPupa", "RSW_SharpToxicAttackBase", "RSW_SmogMoth", "RSW_SmogMothEggFertilized",
    "RSW_SmogMothEggUnfertilized", "RSW_SmogMothLarvae", "RSW_SmogPupa", "RSW_Stinger", "RSW_StingerGroup",
    "RSW_Thrumbungus", "RSW_ThrumbungusShroom", "RSW_ToxicBite", "RSW_ToxicHeadbutt", "RSW_ToxicScratch",
    "RSW_Yooka",
)
SHARED_KEPT = (
    "RSW_BC_StuffPower_FlammabilityOffset", "RSW_BiomesCore_ChitinBase", "RSW_CrimsonSilk", "RSW_DeepChitin",
    "RSW_EusocialInsectNymphFirst", "RSW_EusocialInsectNymphSecond", "RSW_FrontLeftScythe", "RSW_FrontRightScythe",
    "RSW_FungalMantisClaw", "RSW_InsectLarvalFirst", "RSW_InsectLarvalSecound", "RSW_InsectLarvalThird",
    "RSW_LarvaLike", "RSW_MantisLike", "RSW_Paralysis", "RSW_PollutedLands_AnimalThingBase",
    "RSW_PollutedLands_BaseInsect", "RSW_ResourceBlueCrystal", "RSW_RoyalChitin", "RSW_StunningSpores",
    "RSW_ToxicSpores",
)
KEEP = (
    "RM_Brullith", "RM_ThrumbungusShroom", "RM_Grellik", "RM_Skerrith",
    # bucket C and D of the Biomes! RSW_ port: the item leaves them alone
    "RSW_AaroxisDendoria", "RSW_BloodletterPetrel", "RSW_BunkerBug", "RSW_CaveLemming", "RSW_Creature_Mantrap",
    "RSW_CrestedDragon", "RSW_Diggerpede", "RSW_FoundryBeetle", "RSW_Maguana", "RSW_Maligoat", "RSW_MegaphoridLarva",
    "RSW_MossBeetle", "RSW_MutagenicNorphea", "RSW_PodWorm", "RSW_Sacapillar", "RSW_SandLeaper", "RSW_SandPillar",
    "RSW_Screecher",
    # support defs used outside the port (survey: must stay or be rehomed)
    "RSW_FungalMantisClaw", "RSW_ResourceBlueCrystal", "RSW_Rocktooth", "RSW_Boneblade",
)
# RSW_ tokens in the port files that are tags or need/hediff names of a donor, not defs here (present before the prune)
NOT_DEFS = {"RSW_Need_ToxinDependence", "RSW_Hediff_ToxinDependence", "RSW_PollutedAnimalCommon",
            "RSW_PollutedAnimalUncommon", "RSW_PollutedAnimalFighter", "RSW_PollutedAnimalInsect"}
TOOL_FILES = ("src/RimMandrake/Utils/art/flyer_census.py", "src/RimMandrake/Utils/art/flyer_gate.py",
              "src/RimMandrake/Utils/leather_amount_lint.py", "src/RimStarWars/SWBestiary/art/pack_overlay_groups.json",
              "src/RimStarWars/SWBestiary/art/pack_overlay_installed.json")
ROSTERS = ROOT / "design" / "Jawa" / "worldbuilding" / "biomes" / "rosters"
GONE = ("src/RimMandrake/TheRot/port_fauna.py", "src/RimUtinni/UtinniPatches/Patches/RotFauna_KinWiring.xml")
REDRAW = "THRUMBUNGUS_ART_REDRAW_CARTOON_NO_MORE"
DROPPED = set(CLOSURE)
TOK = re.compile(r"(?<![A-Za-z0-9])(?:RSW|RM|RUT)_[A-Za-z0-9_]+")
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append(bool(ok))
    print("%s  %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else "  -> %s" % (str(detail)[:600],)))


def parse(path):
    try:
        return ET.parse(path).getroot()      # ElementTree drops comments
    except ET.ParseError:
        return None


def tokens(root):
    """Every prefixed token in tags, attributes and text of an XML tree (comments are not in it)."""
    out = set()
    for e in root.iter():
        if not isinstance(e.tag, str):
            continue
        out.update(TOK.findall(e.tag))
        for v in e.attrib.values():
            out.update(TOK.findall(v))
        out.update(TOK.findall(e.text or ""))
    return out


def xml_files():
    return [p for p in SRC.rglob("*.xml") if "/Textures/" not in p.as_posix() and "/Sounds/" not in p.as_posix()]


def main():
    defined, refs, named_dropped = set(), {}, []
    for p in xml_files():
        r = parse(p)
        if r is None:
            continue
        if r.tag == "Defs":
            for e in r:
                for n in ((e.findtext("defName") or "").strip(), e.get("Name") or ""):
                    if n:
                        defined.add(n)
                        if n in DROPPED:
                            named_dropped.append("%s %s" % (p.relative_to(ROOT), n))
        for t in tokens(r) & DROPPED:
            refs.setdefault(t, []).append(str(p.relative_to(ROOT)))
    check("closure is %d defs, %d roots inside it" % (len(CLOSURE), len(ROOTS)), set(ROOTS) <= DROPPED
          and len(ROOTS) == 43, sorted(set(ROOTS) - DROPPED))
    check("1. no def under src/ is named in the closure", not named_dropped, named_dropped)
    check("2. no XML under src/ names a closure def (comments stripped)", not refs, refs)
    tool_hits = {}
    for rel in TOOL_FILES:
        hit = set(TOK.findall((ROOT / rel).read_text(encoding="utf-8"))) & DROPPED
        if hit:
            tool_hits[rel] = sorted(hit)
    for p in sorted(ROSTERS.glob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        rows = []

        def walk(x):
            if isinstance(x, dict):
                if x.get("def") in DROPPED:
                    rows.append(x["def"])
                for v in x.values():
                    walk(v)
            elif isinstance(x, list):
                for v in x:
                    walk(v)
        walk(d)
        if rows:
            tool_hits[str(p.relative_to(ROOT))] = rows
    check("3. tool data and design roster rows name no closure def", not tool_hits, tool_hits)
    gone = [g for g in GONE if (ROOT / g).exists()]
    check("3. the retired generator and kin-wiring patch are gone", not gone, gone)
    missing = sorted(set(KEEP) - defined)
    check("4. kept defs still defined (%d)" % len(KEEP), not missing, missing)
    lost = sorted(set(SHARED_KEPT) - defined)
    check("4. defs the closure shared with kept ones still defined (%d)" % len(SHARED_KEPT), not lost, lost)
    dangling, notex, nosnd, port_tex = {}, [], [], 0
    tex_roots = [p for p in SRC.glob("*/*/Textures") if p.is_dir()]
    snd_roots = [p for p in SRC.glob("*/*/Sounds") if p.is_dir()]
    for p in sorted(PORT.rglob("*.xml")):
        r = parse(p)
        if r is None:
            dangling["<unparsable>"] = p.name
            continue
        for t in tokens(r):
            if t.startswith("RSW_") and t not in defined and t not in NOT_DEFS:
                dangling.setdefault(t, p.name)
        for e in r.iter("texPath"):
            tp = (e.text or "").strip()
            if not tp or tp.startswith("Things/"):      # Things/... are the base game's own pictures
                continue
            port_tex += 1
            if not any((x / (tp + ".png")).is_file() or (x / (tp + "_south.png")).is_file()
                       or (x / (tp + "_east.png")).is_file() or ((x / tp).is_dir() and any((x / tp).glob("*.png")))
                       for x in tex_roots):
                notex.append(tp)
        for e in r.iter("clipFolderPath"):
            cp = (e.text or "").strip()
            if cp and not any((x / cp).is_dir() and any((x / cp).iterdir()) for x in snd_roots):
                nosnd.append(cp)
    check("5. every RSW_ token in the port files resolves to a def", not dangling, dangling)
    check("5. every port texPath reaches a picture (%d read)" % port_tex, not notex and port_tex >= 50, notex)
    check("5. every port SoundDef clip folder is on disk", not nosnd, nosnd)
    drops = []
    for shard in sorted((ROOT / "infrastructure" / "state" / "ledger" / "events").glob("*.jsonl")):
        for line in shard.read_text(encoding="utf-8").splitlines():
            if REDRAW in line:
                try:
                    ev = json.loads(line)
                except ValueError:
                    continue
                if ev.get("id") == REDRAW and ev.get("event") == "drop":
                    drops.append(shard.name)
    check("6. %s is dropped on the ledger" % REDRAW, drops, "no drop event")
    # 7. sanity: the instruments can see
    seen = set()
    for p in xml_files():
        r = parse(p)
        if r is not None:
            seen |= tokens(r) & {"RSW_Sacapillar", "RSW_Screecher", "RM_Brullith"}
    check("7. sanity: the XML scan sees kept rows (RSW_Sacapillar, RSW_Screecher, RM_Brullith)",
          seen == {"RSW_Sacapillar", "RSW_Screecher", "RM_Brullith"}, seen)
    planted = ET.fromstring('<Defs><BiomeDef><defName>X</defName><wildAnimals><RSW_Yooka>0.5</RSW_Yooka>'
                            '</wildAnimals></BiomeDef><Patch><xpath>Defs/ThingDef[defName="RSW_EggGlowtailFertilized"]'
                            '</xpath></Patch></Defs>')
    check("7. planted: a roster row and an xpath naming dropped defs read red",
          tokens(planted) & DROPPED == {"RSW_Yooka", "RSW_EggGlowtailFertilized"}, tokens(planted) & DROPPED)
    check("7. sanity: the def census is not blind (%d defs)" % len(defined), len(defined) > 5000)
    print("selftest_biomes_port_prune_42: %s (%d/%d)" % ("PASS" if all(RESULTS) else "FAIL", sum(RESULTS), len(RESULTS)))
    return 0 if all(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
