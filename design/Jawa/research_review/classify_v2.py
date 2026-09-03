#!/usr/bin/env python3
"""Twelve-trees regroup — Fable design pass 2026-09-03 (PROPOSAL, owner reviews).

v2 of classify.py: splits the six trees into thirteen, applies the owner's
aggressive-filter direction (new cuts, each with a recover? line), derives tier
FROM the ruled cost bands (tier2 = band(cost2)) so band conformance is real, and
carries an explicit re-cost table for rows whose felt-tier disagrees with cost.

Reads  design/Jawa/research_review/restructured_model.json (the 522-row v1)
Writes design/Jawa/research_review/restructured_model_v2.json
Run from repo root.
"""
import json
import re
from collections import Counter

M = json.load(open("design/Jawa/research_review/restructured_model.json"))

TREES = [
    "Scavenger", "The Hearth", "The Refinery", "The Workshop",
    "Powder & Slug", "Blasterworks", "The Strange Schools", "The Shell",
    "Droidsmith", "The Waking Mind", "THE SHIP", "The Reach", "The Rites",
]

# ── new cuts (owner 2026-09-03 direction: aggressive thematic filtering) ─────
# defName: (reason, recover-line)
NEW_CUTS = {
    "Deathrest": (
        "sanguophage/vampire mechanic — the register the owner named as the type case for 'truly bizarre'",
        "dead for v1; the gameplay (a dormancy chamber granting waking buffs) could return v2 as a ship 'long-sleep cradle' if wanted"),
    "GR_GeneticAlteration": ("VGE gene-splicing lab register — 'strange genetic stuff the players won't even care about'",
        "the GAMEPLAY (custom creatures) could return v2 as an Oomo-sanctioned beast-breeding rite — hatchery, not laboratory"),
    "GR_HybridImplantology": ("VGE hybrid implant lab register, same cut", "see GR_GeneticAlteration recover line"),
    "GR_GeneticCompatibility": ("VGE splicing register, same cut", "see GR_GeneticAlteration recover line"),
    "GR_GeneticEngineering": ("VGE splicing register, same cut", "see GR_GeneticAlteration recover line"),
    "GR_GeneticDuplication": ("VGE clone-duplication register, same cut", "dead — duplication adds nothing the growth vat doesn't"),
    "GR_GeneticMechahybridization": ("VGE mecha-hybrid register, same cut", "dead — machine-flesh hybrids collide with the Ohm/Oomo axis rather than playing it"),
    "TormentMaster_CranialPinResearch": ("torture-dungeon register (Torment Master) — off the campaign's tone entirely",
        "dead, nothing worth recovering"),
    "OilPourCageResearch": ("torture-dungeon register (Torment Master), same cut", "dead, nothing worth recovering"),
    "DA_BloodflameCatacomb": ("gothic crypt register (Dark Ages) on a desert world", "dead, nothing worth recovering"),
    "DA_Catacombs": ("gothic crypt register (Dark Ages)",
        "the burial gameplay (mass interment structures) could return v2 as sand-tomb vaults in the Jawa idiom"),
    "RimFridge_PowerFactorSetting": ("internal dev-only row: cost 0, unlocks nothing, and it is the dump's one measured self-loop (requires itself)",
        "dead, nothing worth recovering"),
    "guy762_ResearchKotOR_uncraftable": ("author-flagged debug row ('Hey! You're not supposed to unlock this one!'), cost 100,000,000, 117 uncraftable hero items",
        "items stay as loot; the best of them belong in Memory-Core quest rewards, not research"),
}
_COMPANIONS = {
    "guy762_ResearchKotOR_bastila": "Bastila Shan", "guy762_ResearchKotOR_handmaiden": "Brianna",
    "guy762_ResearchKotOR_canderous": "Canderous Ordo", "guy762_ResearchKotOR_carth": "Carth Onasi",
    "guy762_ResearchKotOR_goto": "G0-T0", "guy762_ResearchKotOR_hkequipment": "HK-47",
    "guy762_ResearchKotOR_jolee": "Jolee Bindo", "guy762_ResearchKotOR_juhani": "Juhani",
    "guy762_ResearchKotOR_kreia": "Kreia", "guy762_ResearchKotOR_luxa": "Luxa",
    "guy762_ResearchKotOR_malak": "Malak", "guy762_ResearchKotOR_vao": "Mission Vao",
    "guy762_ResearchKotOR_nihilus": "Nihilus", "guy762_ResearchKotOR_sion": "Sion",
    "guy762_ResearchKotOR_teethree": "T3-M4", "guy762_ResearchKotOR_visas": "Visas Marr",
    "guy762_ResearchKotOR_bigZ": "Zaalbar",
}
for dn, who in _COMPANIONS.items():
    NEW_CUTS[dn] = (
        f"named-hero relic catalog ({who}) at cost 100,000,000 — unreachable by design, and a 4,000-years-off-era name in a Jawa clan story",
        "the items survive as loot; hero relics belong to Memory-Core quest rewards / trade finds, not the bench")

# ── explicit re-costs (PROPOSED — every one is a real balance change) ────────
# defName: (new_cost, why)
RECOST = {
    # RimAI ladder spread across tiers (owner: 'all smashed into the same tech tier, oddly')
    "RimAI_AI_Level1": (2500, "AI ladder spreads T2→T4 instead of stacking in T3"),
    "RimAI_AI_Level2": (4000, "AI ladder spread"),
    "RimAI_AI_Level3": (8000, "AI ladder spread"),
    # THE SHIP becomes the exotic, deeply-rewarding tree — VGE rows priced 100-400 read as afterthoughts
    "VGE_GravshipLiving": (3200, "ship systems are the endgame grind, not 100-point freebies"),
    "VGE_GravshipPower": (3200, "ship endgame pricing"),
    "VGE_OxygenNetwork": (3200, "ship endgame pricing"),
    "VGE_GravshipWeaponry": (4200, "ship guns are a payoff"),
    "VGE_AstrofuelRefining": (3200, "ship endgame pricing"),
    "VGE_CompactWorkspaces": (3200, "ship endgame pricing"),
    "VGE_HeatDissipation": (3200, "ship endgame pricing"),
    "StandardGravtech": (3400, "mid-ship milestone"),
    "AdvancedGravtech": (6000, "the deep ship milestone"),
    "GravForge": (5500, "exotic grav industry"),
    "GravTuning": (6000, "exotic grav industry"),
    "AdvShipParts": (6500, "exotic grav industry"),
    "BlackHole_GT": (9000, "taming a black hole is the tree's crown"),
    "GTbc_BigCannons": (7000, "the ship's big guns are a late payoff"),
    "GravWeapon": (6000, "gravitic personal weapons — Rakatan relic school, priced as relics"),
    "GravBionics": (6000, "grav bionics are Reach-grade flesh-tech"),
    # Alpha Mechs ultra rows at 500 read as typos next to their Ultra techLevel
    "AM_Cryptoharmonization": (5500, "ultra mech capstones priced as capstones"),
    "AM_MechanoidBeamcasting": (5500, "ultra mech capstone"),
    "AM_QuantumPulseMessaging": (5500, "ultra mech capstone"),
    "AM_VoidLinkConnectivity": (5500, "ultra mech capstone"),
    # KotOR inversions the cost-band tiering would otherwise enshrine
    "guy762_ResearchKotOR_workbench": (1600, "'basic upgrading' at 8000 vs 'expert' at 6000 is inverted; basic opens the bench"),
    "guy762_ResearchKotOR_droidsimple": (2500, "'simple droids' at 7500 above 'adv. droids' at 2500 is inverted"),
    # lightsabers kept as the Strange Schools' deep temptation (owner may still cut — trade-off #5)
    "guy762_ResearchKotOR_lightsabers": (6000, "a Jawa building a lightsaber is endgame hubris, not an 800-point stop"),
    "guy762_ResearchKotOR_advsabers": (8000, "deeper still"),
    "guy762_ResearchKotOR_jedi": (3000, "Jedi apparel above mid-game"),
}

# ── tier from the ruled cost bands ───────────────────────────────────────────
def band(cost):
    c = int(cost)
    if c <= 600: return "T0"
    if c <= 1600: return "T1"
    if c <= 3000: return "T2"
    if c <= 5000: return "T3"
    return "T4"

# ── tree assignment: explicit defName table first, then mod/regex fallback ───
A = {}
def put(tree, *dns):
    for dn in dns: A[dn] = tree

put("THE SHIP",
    "BasicGravtech", "StandardGravtech", "AdvancedGravtech",
    "VGE_GravshipLiving", "VGE_GravshipPower", "VGE_OxygenNetwork", "VGE_GravshipWeaponry",
    "VGE_AstrofuelRefining", "VGE_CompactWorkspaces", "VGE_HeatDissipation",
    "GravForge", "GravTuning", "AdvShipParts", "BlackHole_GT", "GTbc_BigCannons",
    "ShipReactor", "MM_Research_AncientShipDesigns", "MM_Research_CWShipDesigns", "MM_Research_EmpireShipDesigns",
    "ResearchDrillTurret", "ResearchDrillTurretEfficientDrilling",   # ruled: the ancient ship mining laser
    "VFE_Manufacturing",                                             # ruled: the factory node couples in
    "ShipBasics", "ShipSensorCluster", "ShipEngine", "ShipCryptosleep", "ShipComputerCore",
    "Shuttles", "OrbitalTech")
put("The Strange Schools",
    "RSW_JawaIon_Weaponry", "RR_EMP", "guy762_ResearchKotOR_sonic", "guy762_ResearchKotOR_vibroweapons",
    "guy762_ResearchKotOR_bluntmelee", "KOTOR_Research_cloaking", "VFES_EMPCannon", "GravWeapon",
    "guy762_ResearchKotOR_lightsabers", "guy762_ResearchKotOR_saberparts", "guy762_ResearchKotOR_advsabers")
put("Blasterworks",
    "guy762_ResearchKotOR_blasters", "guy762_ResearchKotOR_miniblasters", "guy762_ResearchKotOR_hvyblasters",
    "guy762_ResearchKotOR_disruptor", "KOTOR_Research_plasmaApplications", "KOTOR_Research_plasma",
    "BeamWeapons", "ChargedShot", "RR_IncendiaryWeapons",
    "OuterRim_LightTurrets", "OuterRim_MediumTurrets", "OuterRim_HeavyTurrets",
    "OuterRim_LightInstallations", "OuterRim_MediumInstallations", "OuterRim_HeavyInstallations",
    "OuterRim_HeavyWeaponry")
put("Powder & Slug",
    "Gunsmithing", "BlowbackOperation", "GasOperation", "PrecisionRifling", "GunTurrets",
    "HeavyTurrets", "SniperTurret", "FoamTurret", "Mortars", "MultibarrelWeapons",
    "RocketswarmLauncher", "IEDs", "VWE_HeavyWeapons", "VWE_TrenchWarfare",
    "FT_IndustrialCannon", "FT_HeavyArtillery", "VFES_SiegeEquipment", "VFES_Railgun",
    "DedicatedDefenceSystems", "VFES_ConcealedDefenses", "OuterRim_Explosives",
    "KOTOR_Research_Baradium", "KOTOR_Research_AdvMunitions", "guy762_ResearchKotOR_lgtcannons",
    "DetColumnRes", "CGT_WeaponizedGasIEDs", "CGT_WeaponizedGasShells",
    "LongBlades", "ProjectHeron_BlastDoors",
    # the Watch — surveillance is rampart work, not bench work
    "SpacerCCTV", "IndustrialCCTV", "TribalCCTV", "CameraSecurity", "CameraSecurityAdvanced",
    "ResearchAlertSpeaker", "WatchTelescope")
put("The Shell",
    "PlateArmor", "FlakArmor", "ReconArmor", "PoweredArmor", "SmokepopBelt", "ShieldBelt",
    "guy762_ResearchKotOR_lgtarmor", "guy762_ResearchKotOR_midarmor", "guy762_ResearchKotOR_hvyarmor",
    "guy762_ResearchKotOR_eshields", "guy762_ResearchKotOR_echanishields",
    "guy762_ResearchKotOR_deflectors", "guy762_ResearchKotOR_hvyshields",
    "ShieldGen_BasicShieldTech", "ShieldGen_AdvancedShieldTech", "ShieldGen_PortableShieldTech",
    "VFEP_Warcaskets", "VFEP_AdvancedWarcaskets", "VFEP_SpecialisedWarcaskets", "VFEP_WarcasketWeaponry",
    "VFEP_WarcasketRemoval", "VFEP_SpacerWarcaskets", "VFEP_SpacerWarcasketWeaponry",
    "OuterRim_Armoursmithing", "OuterRim_HeavyArmour", "OuterRim_Jetpacks",
    "OuterRim_StimBelts", "OuterRim_TechBelts", "OuterRim_Vambraces",
    # maker doctrines — salvage catalogs of the galaxy's makers (sub-chain; trade-off #6)
    "guy762_ResearchKotOR_czerka", "guy762_ResearchKotOR_exchange", "guy762_ResearchKotOR_republic",
    "guy762_ResearchKotOR_sith", "guy762_ResearchKotOR_mando", "guy762_ResearchKotOR_hutts",
    "guy762_ResearchKotOR_tusken", "guy762_ResearchKotOR_wookiee", "guy762_ResearchKotOR_jawa",
    "guy762_ResearchKotOR_jedi")
put("Droidsmith",
    "guy762_ResearchKotOR_droidsimple", "guy762_ResearchKotOR_droidlabor", "guy762_ResearchKotOR_droidlaboradv",
    "guy762_ResearchKotOR_droidutility", "guy762_ResearchKotOR_droidutilityadv",
    "guy762_ResearchKotOR_droidtech", "guy762_ResearchKotOR_droidarmor", "guy762_ResearchKotOR_droidshields",
    "OuterRim_LaborDroids", "OuterRim_MaintenanceDroids", "OuterRim_MedicalDroids", "OuterRim_PowerDroids",
    "OuterRim_ProtocolDroids", "OuterRim_AstromechDroids", "OuterRim_DroidReplacementParts",
    "OuterRim_DroidReplacementPartsAdv", "OuterRim_DroidReplacementPartsOver", "OuterRim_DroidAdvancedSys",
    "OuterRim_DroidEngineering", "OuterRim_DroidEnergySys",
    "BasicMechtech", "StandardMechtech",
    "AM_WorkerStandardMechtech", "AM_StandardMechtech", "AM_HeavyMechtech",
    "ABF_ResearchProject_Synstruct_InterchangeableParts", "ABF_ResearchProject_Synstruct_Infrastructure",
    "ABF_ResearchProject_Synstruct_Stimulators", "Asimov_WirelessCharging", "HunterDrones", "MechUtility")
put("The Waking Mind",
    "RimAI_AI_Level1", "RimAI_AI_Level2", "RimAI_AI_Level3",
    "RimAI_Subspace_Gravitic_Penetration", "RimAI_GW_Communication",
    "KOTOR_Research_Lobot",
    "guy762_ResearchKotOR_droidcombatadv", "guy762_ResearchKotOR_droidassassin", "guy762_ResearchKotOR_droidassault",
    "guy762_ResearchKotOR_droidsith", "guy762_ResearchKotOR_droidintel", "guy762_ResearchKotOR_hk",
    "guy762_ResearchKotOR_droidblasters",
    "OuterRim_BattleDroids", "OuterRim_AssassinDroids", "OuterRim_SecurityDroids", "OuterRim_DroidWeaponSys",
    "HighMechtech", "UltraMechtech", "AM_UltraHeavyMechtech",
    "AM_Cryptoharmonization", "AM_MechanoidBeamcasting", "AM_QuantumPulseMessaging", "AM_VoidLinkConnectivity",
    "ABF_ResearchProject_Synstruct_CoreAssistants", "ABF_ResearchProject_Synstruct_Optimization",
    "ABF_ResearchProject_Synstruct_Ultraparts")
put("The Reach",
    "Bionics", "Biosculpting", "Bioregeneration", "GrowthVats", "FertilityProcedures",
    "Xenogermination", "GeneProcessor", "Archogenetics", "NeuralSupercharger", "Cryptosleep",
    "KOTOR_Research_AdvPhysiology", "KOTOR_Research_Implants", "KOTOR_Research_AdvImplants",
    "GravBionics", "ScuttlebugsBiology", "Prosthetics")
put("The Refinery",
    "PsychiteRefining", "PsychoidBrewing", "DrugProduction", "GoJuiceProduction", "WakeUpProduction",
    "PenoxycylineProduction", "MedicineProduction", "SterileMaterials", "BiofuelRefining",
    "KOTOR_Research_Spice", "KOTOR_Research_Kolto", "KOTOR_Research_FuelProcessing",
    "KOTOR_Research_Durasteel", "KOTOR_Research_AdvMaterials", "KOTOR_Research_UltraComponent",
    "BoneRefine", "BoneRefineII", "DeepDrilling", "LongRangeMineralScanner", "GroundPenetratingScanner",
    "BreadMoAM_AncientMiningTechniques", "MinesAutomated_ResearchProjectDef_minecraft", "MushroomSoil",
    "BMT_CrystalIncubator",
    "ResearchMobileMineralSonar", "ResearchMobileMineralSonarEnhancedScan",
    "ToxGas", "ToxFiltration", "WastepackAtomizer", "ToxifierGenerator",
    "CGT_MustardGasProduction", "CGT_N2OGasProduction", "CGT_TearGasProduction",
    "CGT_VXGasProduction", "CGT_HalothaneGasProduction",
    "VHGE_GasExtraction", "OilDrilling", "DeepOilWells", "ChemfuelRefining", "Napalm",
    "SynthyleneProduction", "SynthyleneComponents", "SynthyleneAdvComponents",
    "SynthamideProduction", "SynthamideCompositeProduction", "SynthreadProduction",
    "NeutroamineProduction", "HyperweaveProduction", "PlasteelProduction", "ArtificialFloors",
    "FT_Chemistry", "Paleontology" if False else "BMT_Paleontology")
put("The Workshop",
    "Smithing", "Machining", "Electricity", "RR_ElectricityBasics", "Batteries", "SolarPanels",
    "WatermillGenerator", "RR_PowerGenerators", "GeothermalPower", "VFE_IndustrialGenerators",
    "VFE_TidalPower", "VFE_AdvancedBatteries", "VFE_AdvancedPowerSources", "VFE_NuclearPower",
    "TubeTelevision", "FlatscreenTelevision", "MicroelectronicsBasics", "Fabrication",
    "AdvancedFabrication", "MultiAnalyzer", "SpacerElectronics",
    "VFE_BasicFactories", "VFE_ComplexFactories", "FT_Lathe", "FT_Concrete", "FT_ENIAC",
    "Tinkering", "Biohacking", "AM_RecyclingAssembly", "RM_WM_AutomatedSmelterRestoration",
    "OuterRim_HypertechFabrication", "VFES_RepulsorTechnology",
    "guy762_ResearchKotOR_workbench", "guy762_ResearchKotOR_advupgrade", "guy762_ResearchKotOR_exupgrade",
    "VVE_BasicVehicles", "VVE_ComplexVehicles", "VVE_CombatVehicles", "VVE_AerialVehicles",
    "TransportPod", "Stonecutting", "VitalsMonitor", "HospitalBed",
    "OrbitalTradeColumnRes", "UtilityPanelsRes",
    "Res_Projectors", "SpaceBase_Explorer_Furniture", "LaserSculpting", "HeavyBridges",
    "MoisturePump", "Hydroponics", "VFE_Res_Sprinkler", "VFE_Res_AdvancedHydroponics",
    "VFE_Res_FarmingTechniques")
put("The Hearth",
    "ComplexFurniture", "MF_BasicFurniture", "MF_ModernFurniture", "MF_RoyalFurniture", "MF_WasteDisposal",
    "RR_Furniture", "VFET_Furniture", "SpacerFurniture", "Brewing", "VBE_LiquorBrewing", "VBE_MixologyResearch",
    "VCE_Canning", "VCE_CheeseMaking", "VCE_DeepFrying", "VCE_CondimentsResearch", "VCE_Grilling",
    "VCE_SoupCooking", "VCE_StewCooking", "NutrientPaste", "PackagedSurvivalMeal",
    "VFE_Res_ArtfulDisplay", "VFE_Res_WallCarvings", "VFE_Res_Monuments", "VFE_Res_Obelisk",
    "VFE_Res_Pottery", "VFE_Res_Rugs", "VFE_Res_Statues", "VFE_Res_Wallpapers", "VFE_Res_Holograms",
    "ModernFixtures", "Saunas", "AdvancedShowers", "AdvancedToilets", "HotTubs",
    "Jewelry", "KOTOR_Research_Instruments", "KOTOR_Research_TableRec", "KOTOR_Research_HoloRec",
    "CarpetMaking", "ColoredLights", "Cocoa", "VFET_Culture", "VAE_CasualWear", "VAE_FormalWear",
    "VAE_WorkAttire", "VAE_MilitaryClothing", "ComplexClothing", "Devilstrand", "TreeSowing")
put("Scavenger",
    "KOTOR_Research_MoistureVaporator")   # atmospheric moisture on a desert world is the MOST Jawa row in the game

def fallback(m):
    mod = m["mod"].lower()
    h = (m["defName"] + " " + m["label"]).lower()
    if "tribals" in mod or "roots of rimworld" in mod or "hunting" in mod: return "Scavenger"
    if any(k in mod for k in ("cooking", "brewing", "jewelry", "furniture expanded")): return "The Hearth"
    if any(k in mod for k in ("rimefeller", "gas", "mining", "biomes!", "regrowth", "plants", "tunneler")):
        return "The Refinery" if re.search(r"refin|gas|oil|mine|drill|fuel|chem", h) else "Scavenger"
    if "doors" in mod: return "Scavenger"
    if re.search(r"turret|cannon|artillery", h): return "Powder & Slug"
    return "Scavenger"

# ── apply ────────────────────────────────────────────────────────────────────
for m in M:
    dn = m["defName"]
    m["fate2"] = m["fate"]
    m["reason2"] = m.get("reason", "")
    m["recover"] = ""
    m["cost2"] = None
    m["recost_why"] = ""
    if m["fate"] in ("cut", "merge"):
        m["tab2"] = None; m["tier2"] = None
        continue
    if dn in NEW_CUTS:
        m["fate2"] = "cut"
        m["reason2"], m["recover"] = NEW_CUTS[dn]
        m["tab2"] = None; m["tier2"] = None
        continue
    cost = int(m["cost"])
    if dn in RECOST:
        m["cost2"], m["recost_why"] = RECOST[dn]
        cost = m["cost2"]
    m["tab2"] = A.get(dn) or fallback(m)
    m["tier2"] = band(cost)

# ── coverage assertion: 522 in, 522 accounted ────────────────────────────────
total = len(M)
v1cut = sum(1 for m in M if m["fate"] == "cut")
v1merge = sum(1 for m in M if m["fate"] == "merge")
newcut = sum(1 for m in M if m["fate2"] == "cut" and m["fate"] != "cut")
surv = [m for m in M if m["tab2"]]
assert total == v1cut + v1merge + newcut + len(surv), "coverage broken"
unplaced = [m for m in surv if m["tab2"] not in TREES]
assert not unplaced, f"unplaced: {[m['defName'] for m in unplaced]}"
print(f"COVERAGE OK: {total} rows = {v1cut} v1-cut + {v1merge} merge + {newcut} new-cut + {len(surv)} in trees")

json.dump(M, open("design/Jawa/research_review/restructured_model_v2.json", "w"), indent=1)

print("\n=== v2 distribution ===")
for t in TREES:
    rows = [m for m in surv if m["tab2"] == t]
    tiers = Counter(m["tier2"] for m in rows)
    print(f"  {t:20} {len(rows):4}   {dict(sorted(tiers.items()))}")
print(f"  {'(survivors)':20} {len(surv):4}")
print(f"\nre-costs proposed: {sum(1 for m in M if m['cost2'] is not None)}")
print("\n=== fallback-assigned rows (hand-check these) ===")
for m in surv:
    if m["defName"] not in A:
        print(f"  {m['tab2']:>16} <- {m['tier2']} {m['cost']:>6} {m['label'][:40]:40} {m['defName']:36} {m['mod'][:28]}")
