#!/usr/bin/env python3
"""RESEARCH_TREE_NORMALIZATION_1 — v4: the droid boundary and the saber cuts.

Reads  design/Jawa/research_review/restructured_model_v3.json  (522 rows)
Writes design/Jawa/research_review/restructured_model_v4.json  (522 rows, v4 fields)
       design/Jawa/research_review/v4_coverage_assertion.txt   (the printed block)

Owner rulings of 2026-09-03 executed here (see droid_and_saber_rulings.md):
  1. droid CONSTRUCTION is faction-owned by the Free Droid Enclaves (a locked tree)
  2. the Jawa keep only low-tier repair / reconstruction / maintenance (general)
  3. lightsaber construction is not tech in this scenario — the rows are CUT
  4. Force-user gear is not shared either — cut, unless a row is ordinary
     equipment wearing a Force name

v4 adds, per row:
  tab4       tree (None for cut/merge)
  tier4      T0..T4 = band(cost4)
  fate4      untouched | keep | reflavor | cut | merge
  access4    common | faction:<FactionDefName> | jawa-special | ship-only | n/a
  access4_tag  the FactionDef.categoryTag that keys the lock (None if unlocked)
  cost4      effective cost (cost2 re-cost if any, then v4 re-cost if any)
  prereqs4   prerequisites after v4 re-points
  boundary4  for the 56 droid rows: repair | gear | construction | weapon | mind | control
  reason4 / recover4  why (droid rows, cuts, moves) and how the player still meets the thing

A CUT REMOVES A ResearchProjectDef AND NOTHING ELSE (owner, 2026-09-03).
Nothing here executes. Coverage-or-refuse: assertions fail loudly rather than
writing a partial model. Run it and read the printed block.
"""
import json
import os
import sys
from collections import Counter, OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "restructured_model_v3.json")
DST = os.path.join(HERE, "restructured_model_v4.json")
TXT = os.path.join(HERE, "v4_coverage_assertion.txt")

BANDS = [(600, "T0"), (1600, "T1"), (3000, "T2"), (5000, "T3")]


def band(cost):
    c = float(cost)
    for ceiling, name in BANDS:
        if c <= ceiling:
            return name
    return "T4"


# --------------------------------------------------------------- the trees
GENERAL_DROID_TREE = "Droidsmith"          # repair / reconstruction / maintenance, tops out at T2
LOCKED_DROID_TREE = "The Unbolting"        # construction — Free Droid Enclaves
MIND_TREE = "The Waking Mind"              # minds you make and minds you bind (AI ladder + control gear)

LOCKED_TREES = OrderedDict([
    ("The Junker Yards", dict(faction="Jawa_Junkers", tag="Pirate", tag_new=False)),
    ("The Foundry Hive", dict(faction="Jawa_GeonosianFoundryHive", tag="GeonosianHive", tag_new=True)),
    ("The Ascendant Ladder", dict(faction="Jawa_AscendantHelix", tag="AscendantHelix", tag_new=True)),
    (LOCKED_DROID_TREE, dict(faction="Jawa_FreeDroidEnclaves", tag="FreeDroidEnclaves", tag_new=True,
                             route="the droid-liberation quest line (ThingSetMaker_Techprints keyed on "
                                   "makingFaction) + the very rare Enclave caravan (OutlanderFactionBase "
                                   "traders carry StockGenerator_Techprints; the def does not override them)")),
])

# ------------------------------------------ the droid boundary, row by row
# defName -> (boundary, destination tree, one-line reason)
# boundary: repair = fix/rebuild/power/keep running what exists      -> GENERAL
#           gear   = worn/bolted-on protection, packs                 -> GENERAL
#           weapon = a gun is a gun; by physics, not droid tech       -> Blasterworks / Powder & Slug
#           mind   = an AI that is not a droid; a human implant       -> The Waking Mind
#           control= the bolt's cousins: mechanitor command gear      -> The Waking Mind
#           construction = new chassis, new brain, a factory/cradle/gestator,
#                          or a part that makes a droid better than spec -> LOCKED
DROID = OrderedDict([
    # --- Biotech mechtech (the campaign's Imperial-pattern mechanoids)
    ("BasicMechtech",            ("repair", GENERAL_DROID_TREE, "T0/200: recharger, wall charger, band node, basic mechlink kit — the ONLY row that lets a salvaged or captured mech be recharged; bundled with two menial gestations (agrihand, cleansweeper). The one deliberate exception, argued in the doc")),
    ("StandardMechtech",         ("construction", LOCKED_DROID_TREE, "gestates scyther/pikeman/scorcher/tunneler/cyclops; softscanner subcores")),
    ("HighMechtech",             ("construction", LOCKED_DROID_TREE, "gestates centipedes/diabolus/lancer/paramedic; ripscanner subcores")),
    ("UltraMechtech",            ("construction", LOCKED_DROID_TREE, "gestates centurion/legionary/warqueen/tesseron; mechlord suit rides along")),
    # --- Alpha Mechs
    ("AM_WorkerStandardMechtech", ("construction", LOCKED_DROID_TREE, "seven new worker chassis")),
    ("AM_StandardMechtech",      ("construction", LOCKED_DROID_TREE, "nine new chassis")),
    ("AM_HeavyMechtech",         ("construction", LOCKED_DROID_TREE, "four heavy chassis")),
    ("AM_UltraHeavyMechtech",    ("construction", LOCKED_DROID_TREE, "seven ultra-heavy chassis")),
    ("AM_MechanoidBeamcasting",  ("control", MIND_TREE, "mech commander helm, disruptor, greater recharger — command gear, the bolt's cousin; the Jawa keep the bolt")),
    ("AM_VoidLinkConnectivity",  ("control", MIND_TREE, "beamcaster pack, commander suit, mech boosters — command gear")),
    ("AM_QuantumPulseMessaging", ("control", MIND_TREE, "mech breaker helm, voidlink pack — command gear")),
    ("AM_Cryptoharmonization",   ("control", MIND_TREE, "mech breaker armor, crypto pack — command gear")),
    # --- odds and ends
    ("HunterDrones",             ("weapon", "Powder & Slug", "a self-detonating drone is a mine that walks: explosive, MASS. Not a droid in the campaign's sense (no Droidworks race, no mind)")),
    ("Asimov_WirelessCharging",  ("repair", GENERAL_DROID_TREE, "a charger keeps a droid running — maintenance. RE-COST 8000 -> 1600: a charging building priced as archotech cannot sit in a low-tier tree")),
    ("MechUtility",              ("gear", GENERAL_DROID_TREE, "utility packs a mech wears — apparel, not construction")),
    # --- RimAI (a colony AI, not a droid)
    ("RimAI_GW_Communication",   ("mind", MIND_TREE, "AI antenna")),
    ("RimAI_AI_Level1",          ("mind", MIND_TREE, "AI server — a mind in a box, not a droid")),
    ("RimAI_Subspace_Gravitic_Penetration", ("mind", MIND_TREE, "AI ladder leaf")),
    ("RimAI_AI_Level2",          ("mind", MIND_TREE, "AI server")),
    ("RimAI_AI_Level3",          ("mind", MIND_TREE, "AI server")),
    ("KOTOR_Research_Lobot",     ("mind", MIND_TREE, "a human brain implant, Empire-held — unchanged")),
    # --- ABF Synstructs
    ("ABF_ResearchProject_Synstruct_Infrastructure", ("construction", LOCKED_DROID_TREE, "the CRADLE that produces synstructs (bundled with the part workbench; parts also craft at TableMachining, so repair survives without it)")),
    ("ABF_ResearchProject_Synstruct_InterchangeableParts", ("repair", GENERAL_DROID_TREE, "'a standard for repairing and restoring synstructs' — the mod's own words; frames, chassis plates, arms, restruct kit. Prereq re-pointed off the cradle")),
    ("ABF_ResearchProject_Synstruct_Stimulators", ("repair", GENERAL_DROID_TREE, "consumable, temporary, brewed under DrugProduction — Refinery chemistry applied to droids; no faction guards a stim recipe")),
    ("ABF_ResearchProject_Synstruct_Optimization", ("construction", LOCKED_DROID_TREE, "'assembling and upgrading synstructs with Ultratechnology' — beyond spec")),
    ("ABF_ResearchProject_Synstruct_Ultraparts", ("construction", LOCKED_DROID_TREE, "'replacement parts that enhance synstructs greatly' — an ultra part is an upgrade wearing a repair name")),
    ("ABF_ResearchProject_Synstruct_CoreAssistants", ("construction", LOCKED_DROID_TREE, "chips that make a synstruct better than it was — mind-side upgrade")),
    # --- Outer Rim Droid Depot
    ("OuterRim_DroidEngineering",        ("construction", LOCKED_DROID_TREE, "the DROID BRAIN and the DROID FACTORY — the root of construction")),
    ("OuterRim_DroidReplacementParts",   ("repair", GENERAL_DROID_TREE, "'baseline replacement parts' — arm, leg, hand, foot, sensors, reactor. Crafted at the Hypertech Fabricator, not the factory. RE-COST 2000 -> 1200: low-tier repair by ruling. Prereq re-pointed off the factory")),
    ("OuterRim_DroidReplacementPartsOver", ("construction", LOCKED_DROID_TREE, "overclocked parts make the droid better than spec — upgrade, not repair")),
    ("OuterRim_DroidReplacementPartsAdv", ("construction", LOCKED_DROID_TREE, "advanced parts — upgrade, not repair")),
    ("OuterRim_DroidEnergySys",          ("repair", GENERAL_DROID_TREE, "'energy modules for droids' — keeping it powered is maintenance (empty unlock cache in the dump; description is the evidence). Prereq re-pointed off the factory")),
    ("OuterRim_DroidWeaponSys",          ("weapon", "Blasterworks", "blaster cannon, wrist blasters, wrist rocket — implemented as held weapons (ThingDefs_Weapons, weaponTags); a blaster is a blaster whoever holds it. Prereq re-pointed off the factory")),
    ("OuterRim_DroidAdvancedSys",        ("construction", LOCKED_DROID_TREE, "'shielding modules' but the row bundles overclocked/advanced shielding and propulsion jets — beyond spec; cannot be split without a new def")),
    ("OuterRim_AssassinDroids",          ("construction", LOCKED_DROID_TREE, "a new chassis")),
    ("OuterRim_AstromechDroids",         ("construction", LOCKED_DROID_TREE, "a new chassis")),
    ("OuterRim_BattleDroids",            ("construction", LOCKED_DROID_TREE, "a new chassis. LEAVES The Foundry Hive (v3): ruling 1 read strictly — 'droid building tech is droid faction owned'. The Hive drops to four rows")),
    ("OuterRim_MaintenanceDroids",       ("construction", LOCKED_DROID_TREE, "a new chassis — the NAME is a trap: this builds maintenance droids, it does not maintain droids")),
    ("OuterRim_MedicalDroids",           ("construction", LOCKED_DROID_TREE, "a new chassis")),
    ("OuterRim_PowerDroids",             ("construction", LOCKED_DROID_TREE, "a new chassis")),
    ("OuterRim_ProtocolDroids",          ("construction", LOCKED_DROID_TREE, "a new chassis")),
    ("OuterRim_LaborDroids",             ("construction", LOCKED_DROID_TREE, "a new chassis")),
    ("OuterRim_SecurityDroids",          ("construction", LOCKED_DROID_TREE, "a new chassis")),
    # --- KotOR droids
    ("guy762_ResearchKotOR_droidsimple",     ("construction", LOCKED_DROID_TREE, "four droid generators — construction")),
    ("guy762_ResearchKotOR_droidutilityadv", ("construction", LOCKED_DROID_TREE, "droid generators")),
    ("guy762_ResearchKotOR_droidcombatadv",  ("construction", LOCKED_DROID_TREE, "droid generators")),
    ("guy762_ResearchKotOR_droidlaboradv",   ("construction", LOCKED_DROID_TREE, "droid generators")),
    ("guy762_ResearchKotOR_droidassault",    ("construction", LOCKED_DROID_TREE, "droid generators")),
    ("guy762_ResearchKotOR_droidassassin",   ("construction", LOCKED_DROID_TREE, "droid generators")),
    ("guy762_ResearchKotOR_droidintel",      ("construction", LOCKED_DROID_TREE, "droid generators")),
    ("guy762_ResearchKotOR_droidsith",       ("construction", LOCKED_DROID_TREE, "'Sith war droids' — a war droid wearing a Force name: ordinary droid construction, NOT Force gear; goes with construction, not with the saber cuts")),
    ("guy762_ResearchKotOR_hk",              ("construction", LOCKED_DROID_TREE, "HK-51 generator — the crown of construction")),
    ("guy762_ResearchKotOR_droidtech",       ("construction", LOCKED_DROID_TREE, "'droid upgrades' — agility/durability hardware, computer/security software, sensors: makes the droid better than spec. (One unlock is a REPAIR sensor; the row is still an upgrade row.)")),
    ("guy762_ResearchKotOR_droidarmor",      ("gear", GENERAL_DROID_TREE, "plating welded on — the scavenger's torch; protects, does not change what the droid is. Prereq re-pointed off the generators")),
    ("guy762_ResearchKotOR_droidshields",    ("gear", GENERAL_DROID_TREE, "T0/500 droid shields — worn protection. Prereq re-pointed off the generators")),
    ("guy762_ResearchKotOR_droidblasters",   ("weapon", "Blasterworks", "holdout, flamethrower, laser, sonic, rockets, firefoam — a held-weapon grab bag, majority HEAT; a gun is a gun. lgtcannons keeps its prereq")),
])
GENERAL_TIER_CEILING = "T2"   # 'low tier' made checkable: nothing general-droid may exceed this

# ----------------------------------------------------------- the saber cuts
# defName -> (reason, recover)
SABER_CUTS = OrderedDict([
    ("guy762_ResearchKotOR_lightsabers", (
        "ruling 3: lightsaber construction is not tech in this scenario; nobody teaches it",
        "the item stays: a hidden Jedi wanderer carries 'a custom lightsaber' (faction_roster_v2.md:311) and drops it; an Imperial Sith-escort carries a persona melee weapon (:321); the random-ruins ThingSetMaker leak and quest rewards are unaimed pity-drops; no trader stocks the Force_Lightsaber tradeTag today")),
    ("guy762_ResearchKotOR_advsabers", (
        "ruling 3: double-bladed and crossguard sabers are still sabers",
        "loot on the same Force-user pawns; the crossguard/dual items are rarer drops by weight, never a bench")),
    ("guy762_ResearchKotOR_saberparts", (
        "ruling 3: 'craft the individual pieces of a Lightsaber' — the parts row is the construction row",
        "emitter/lens/power-cell items stay as salvage from a broken saber and as relic-hunt quest rewards (v2's Memory-Core relic chain); useless without a bench, which is the point")),
    ("guy762_ResearchKotOR_jedi", (
        "ruling 4: 'craft the tunics and robes of the Jedi' — Force-user gear by its own description; a robe is cloth, but nobody teaches the Jedi's cut",
        "the sheltered Jedi among the moisture farmers (faction_roster_v2.md:314) wears one; strip it from a fallen wanderer, or take it from an Imperial confiscation cache (quest reward)")),
])

# Rows that WEAR a Force name and stay — judged ordinary equipment
FORCE_NAMED_KEPT = {
    "guy762_ResearchKotOR_sith": "reflavor",   # 19 of 22 unlocks are trooper/commando/officer kit of the Sith EMPIRE (a state); 3 Force-user tunics ride along
    "guy762_ResearchKotOR_droidsith": None,    # a war droid; handled in DROID
    "guy762_ResearchKotOR_disruptor": None,    # one Sith-named disruptor pistol among five
    "guy762_ResearchKotOR_eshields": None,     # one Sith-named energy shield among five
}

# ---------------------------------------------- prereq re-points, PROPOSED
# defName -> (expected old prereqs, new prereqs, why)
PREREQ_REPOINT = {
    "ABF_ResearchProject_Synstruct_InterchangeableParts": (
        ["ABF_ResearchProject_Synstruct_Infrastructure"], ["Fabrication"],
        "repair must not require the cradle (locked); Fabrication is the cradle's own prereq"),
    "OuterRim_DroidReplacementParts": (
        ["OuterRim_DroidEngineering"], ["MicroelectronicsBasics"],
        "repair must not require the factory (locked); parts craft at the Hypertech Fabricator, not the factory"),
    "OuterRim_DroidEnergySys": (
        ["OuterRim_DroidEngineering"], ["MicroelectronicsBasics"],
        "maintenance must not require the factory (locked)"),
    "OuterRim_DroidWeaponSys": (
        ["OuterRim_DroidEngineering"], ["guy762_ResearchKotOR_blasters"],
        "a weapon row hangs off the blaster spine, not the droid factory"),
    "guy762_ResearchKotOR_droidarmor": (
        ["guy762_ResearchKotOR_droidsimple"], ["Machining"],
        "plating must not require the generators (locked)"),
    "guy762_ResearchKotOR_droidshields": (
        ["guy762_ResearchKotOR_eshields", "guy762_ResearchKotOR_droidsimple"], ["guy762_ResearchKotOR_eshields"],
        "drop the generator prereq (locked); keep the shield-school prereq"),
    "AM_MechanoidBeamcasting": (
        ["UltraMechtech"], ["AdvancedFabrication"],
        "command gear must not require ultra gestation (locked); you may command what you salvaged"),
}

# ------------------------------------------------------ re-costs, PROPOSED
RECOST4 = {
    "OuterRim_DroidReplacementParts": (2000, 1200, "low-tier repair by ruling 2; T2 -> T1"),
    "Asimov_WirelessCharging": (8000, 1600, "a charging building is maintenance; 8000 is an archotech price; T4 -> T1"),
}

JAWA_SPECIAL = {"guy762_ResearchKotOR_jawa", "RSW_JawaIon_Weaponry"}
SHIP_ONLY = {"MM_Research_AncientShipDesigns", "MM_Research_CWShipDesigns", "MM_Research_EmpireShipDesigns"}
PRESENT = {"Empire", "Jawa_HuttCartel", "OutlanderCivil", "TribeCivil",
           "Jawa_FreeDroidEnclaves", "Jawa_WildsteamClan", "Jawa_DeepwaterCompact",
           "Jawa_GeonosianFoundryHive", "Jawa_AscendantHelix", "Pirate",
           "Jawa_IndigenousTribes", "Jawa_Junkers"}
PREEXISTING_ORPHANS = {"MM_Research_Repulsor", "VAE_SterileAttire"}   # v2/v3 defects, out of scope


def main():
    rows = json.load(open(SRC, encoding="utf-8"))
    by = {r["defName"]: r for r in rows}

    for name in list(DROID) + list(SABER_CUTS) + list(FORCE_NAMED_KEPT) + list(PREREQ_REPOINT) + list(RECOST4):
        if name not in by:
            sys.exit(f"REFUSE: {name} not in v3")

    # the v3 droid population must be exactly what DROID covers (plus BattleDroids from the Hive)
    v3_droid = {r["defName"] for r in rows if r["tab3"] in ("Droidsmith", "The Waking Mind")} | {"OuterRim_BattleDroids"}
    missing = sorted(v3_droid - set(DROID))
    extra = sorted(set(DROID) - v3_droid)
    if missing or extra:
        sys.exit(f"REFUSE: droid boundary incomplete. missing={missing} extra={extra}")

    for r in rows:
        dn = r["defName"]
        r["fate4"] = r["fate3"]
        r["reason4"] = ""
        r["recover4"] = r.get("recover", "")
        r["boundary4"] = None
        r["cost4"] = r["cost2"] if r.get("cost2") else float(r["cost"])
        r["recost4_why"] = ""
        r["prereqs4"] = list(r.get("prereqs3", r["prereqs"]))

        if dn in RECOST4:
            old, new, why = RECOST4[dn]
            if float(r["cost4"]) != old:
                sys.exit(f"REFUSE: {dn} cost is {r['cost4']}, expected {old}")
            r["cost4"], r["recost4_why"] = new, why

        if dn in PREREQ_REPOINT:
            old, new, why = PREREQ_REPOINT[dn]
            if r["prereqs4"] != old:
                sys.exit(f"REFUSE: {dn} prereqs are {r['prereqs4']}, expected {old}")
            r["prereqs4"] = new
            r["reason4"] = f"prereq re-point {old} -> {new}: {why}. "

        # ---- cuts (v3 cut/merge carried; saber cuts added)
        if r["tab3"] is None:
            r["tab4"], r["tier4"], r["access4"], r["access4_tag"] = None, None, "n/a", None
            continue
        if dn in SABER_CUTS:
            reason, recover = SABER_CUTS[dn]
            r["fate4"] = "cut"
            r["reason4"] += reason
            r["recover4"] = recover
            r["tab4"], r["tier4"], r["access4"], r["access4_tag"] = None, None, "n/a", None
            continue

        # ---- placed rows
        if dn in DROID:
            boundary, tree, why = DROID[dn]
            r["boundary4"] = boundary
            r["tab4"] = tree
            r["reason4"] += why
        else:
            r["tab4"] = r["tab3"]
        r["tier4"] = band(r["cost4"])

        if dn in FORCE_NAMED_KEPT and FORCE_NAMED_KEPT[dn]:
            r["fate4"] = FORCE_NAMED_KEPT[dn]
            r["reason4"] += ("ruling 4 judged: ordinary equipment wearing a Force name — 19 of 22 unlocks are Sith-EMPIRE "
                             "trooper/commando/officer kit; three Force-user tunics ride along. Reflavor label to "
                             "'Imperial Sith-escort kit'; stays Empire-held")

        # access
        if r["tab4"] in LOCKED_TREES:
            spec = LOCKED_TREES[r["tab4"]]
            r["access4"], r["access4_tag"] = "faction:" + spec["faction"], spec["tag"]
        elif dn in DROID and DROID[dn][0] != "mind":
            # every droid row that leaves a locked tree is common (its v3 lock, if any, was tree-borne)
            r["access4"], r["access4_tag"] = "common", None
        else:
            r["access4"], r["access4_tag"] = r["access3"], r.get("access3_tag")

    # --------------------------------------------------------- assertions
    out = []
    P = out.append
    P("=" * 72)
    P("RESEARCH_TREE_NORMALIZATION_1 — v4 coverage assertion")
    P("=" * 72)

    assert len(rows) == 522, f"row count {len(rows)} != 522"
    P(f"rows in  : {len(rows)}")
    assert len({r['defName'] for r in rows}) == 522, "duplicate defName"
    P("defNames : 522 unique, no duplicates")
    assert all(set(("tab4", "tier4", "fate4", "access4", "cost4", "prereqs4")) <= set(r) for r in rows)
    P("v4 fields: tab4/tier4/fate4/access4/cost4/prereqs4 present on all 522")

    fates = Counter(r["fate4"] for r in rows)
    P(f"fate4    : {dict(fates)}  (sum {sum(fates.values())})")
    assert sum(fates.values()) == 522
    newcuts = [r["defName"] for r in rows if r["fate4"] == "cut" and r["fate3"] != "cut"]
    assert set(newcuts) == set(SABER_CUTS), newcuts
    assert all(by[d]["recover4"] for d in newcuts), "a new cut lacks a recover line"
    P(f"new cuts : {len(newcuts)} (saber/Force), each with a recover line -> {newcuts}")

    placed = [r for r in rows if r["tab4"]]
    unplaced = [r for r in rows if not r["tab4"]]
    assert len(placed) + len(unplaced) == 522
    assert all(r["fate4"] in ("cut", "merge") for r in unplaced), "an unplaced row is not cut/merge"
    assert all(r["fate4"] not in ("cut", "merge") for r in placed), "a cut/merge row was placed"
    P(f"placed   : {len(placed)}   unplaced (cut/merge): {len(unplaced)}")

    trees = Counter(r["tab4"] for r in placed)
    assert sum(trees.values()) == len(placed)
    P(f"trees    : {len(trees)}   per-tree sum {sum(trees.values())} == placed {len(placed)}")
    for t, c in sorted(trees.items(), key=lambda kv: -kv[1]):
        lock = f"   [LOCKED -> {LOCKED_TREES[t]['faction']} / tag {LOCKED_TREES[t]['tag']}]" if t in LOCKED_TREES else ""
        flag = "   ⚠ below viability (<10)" if c < 10 else ""
        P(f"           {c:3d}  {t}{lock}{flag}")

    bad = [r["defName"] for r in placed if r["tier4"] != band(r["cost4"])]
    assert not bad, f"tier4 off band: {bad}"
    P(f"bands    : all {len(placed)} placed rows conform to T0<=600 T1<=1600 T2<=3000 T3<=5000 T4>5000")
    P(f"recosts  : {len(RECOST4)} PROPOSED in v4 -> " + ", ".join(f"{k} {v[0]}->{v[1]}" for k, v in RECOST4.items()))
    P(f"repoints : {len(PREREQ_REPOINT)} PROPOSED in v4 -> " + ", ".join(PREREQ_REPOINT))

    # the droid boundary
    dro = [r for r in rows if r["boundary4"]]
    assert len(dro) == len(DROID) == 56, len(dro)
    bcount = Counter(r["boundary4"] for r in dro)
    P(f"boundary : 56 droid rows -> {dict(bcount)}")
    dest = Counter(r["tab4"] for r in dro)
    P(f"           by tree -> {dict(dest)}")
    general = [r for r in dro if r["tab4"] == GENERAL_DROID_TREE]
    assert all(r["boundary4"] in ("repair", "gear") for r in general), "a non-repair row in the general droid tree"
    assert all(r["access4"] == "common" for r in general)
    too_high = [r["defName"] for r in general if r["tier4"] > GENERAL_TIER_CEILING]
    assert not too_high, f"general droid rows above {GENERAL_TIER_CEILING}: {too_high}"
    P(f"lowtier  : all {len(general)} general droid rows are 'repair' or 'gear', common, and <= {GENERAL_TIER_CEILING}")
    locked_d = [r for r in dro if r["tab4"] == LOCKED_DROID_TREE]
    assert all(r["boundary4"] == "construction" for r in locked_d), "a non-construction row in the locked droid tree"
    assert all(r["boundary4"] != "construction" or r["tab4"] == LOCKED_DROID_TREE for r in dro), \
        "a construction row outside the locked tree"
    P(f"locked   : all {len(locked_d)} rows in {LOCKED_DROID_TREE} are 'construction'; no construction row is anywhere else")
    P(f"           tier spread -> {dict(sorted(Counter(r['tier4'] for r in locked_d).items()))}")

    acc = Counter(r["access4"] for r in rows)
    P(f"access4  : {dict(acc)}  (sum {sum(acc.values())})")
    assert sum(acc.values()) == 522
    held = [r for r in rows if r["access4"].startswith("faction:")]
    ghosts = sorted({r["access4"].split(":", 1)[1] for r in held} - PRESENT)
    assert not ghosts, f"gated on faction(s) NOT on the planet: {ghosts}"
    P(f"holders  : {len(held)} faction-held rows, {len({r['access4'] for r in held})} distinct holders, all present on the planet")

    lockednames = {r["defName"] for r in held}
    leaks = [(r["defName"], p) for r in rows
             if r["fate4"] not in ("cut", "merge") and not r["access4"].startswith("faction:")
             for p in r["prereqs4"] if p in lockednames]
    assert not leaks, f"GATE LEAK: {leaks}"
    P("gateleak : 0  (no common/jawa-special/ship-only row requires a locked row)")
    cross = [(r["defName"], p) for r in held for p in r["prereqs4"]
             if p in lockednames and by[p]["access4"] != r["access4"]]
    assert not cross, f"CROSS-LOCK: {cross}"
    P("crosslock: 0  (no locked row depends on a differently-locked row)")

    survivors = {r["defName"] for r in rows if r["fate4"] not in ("cut", "merge")}
    orphan = sorted({p for r in rows if r["defName"] in survivors for p in r["prereqs4"] if p not in survivors})
    new_orphans = sorted(set(orphan) - PREEXISTING_ORPHANS)
    assert not new_orphans, f"NEW orphans created by v4: {new_orphans}"
    P(f"orphans  : {len(orphan)} prereq references to non-surviving rows -> {orphan}  (all pre-existing; 0 new)")

    # the Force-mod recipe leak, reported not asserted (a recipe is not a research row)
    leak_rows = [r["defName"] for r in rows if r["fate4"] not in ("cut", "merge")
                 and any(u.startswith("Force_") for u in r["unlocks"])]
    P(f"saberleak: {len(leak_rows)} surviving COMMON rows still unlock Force_ recipes -> {leak_rows}")
    P("           (lee.theforce.lightsaber's own RecipeDefs hang off MicroelectronicsBasics/Smithing;")
    P("            a RecipeDef edit, NOT a research cut — execution item, see the doc)")

    P("=" * 72)
    P("COVERAGE: 522 in, 522 accounted. ASSERTIONS PASSED.")
    P("=" * 72)

    block = "\n".join(out)
    print(block)
    with open(DST, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=1, ensure_ascii=False)
    print(f"\nwrote {DST}  ({len(rows)} rows)")
    with open(TXT, "w", encoding="utf-8") as fh:
        fh.write(block + "\n")


if __name__ == "__main__":
    main()
