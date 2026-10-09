"""L1 acceptance reads, 2026-10-09. Run under python.exe from the repo root:
    python.exe Transient/belt_acc_l1_probe_20261009.py
Writes Transient/belt_acc_l1_raw_20261009.json (raw replies, no judgement)."""
import json, os, re, sys, glob
sys.path.insert(0, os.path.join("src", "RimMandrake", "Utils"))
from scenes import scenelib as S

OUT = {}
def rec(k, **kw): OUT.setdefault(k, {}).update(kw)
def gd(defs, fields="defName"):
    r = S.call("jawa/get_defs", defs=defs, fields=fields)
    return {"success": r.get("success") if isinstance(r, dict) else None,
            "foundCount": r.get("foundCount") if isinstance(r, dict) else None,
            "notFound": r.get("notFound") if isinstance(r, dict) else None,
            "raw": (json.dumps(r, default=str)[:1500] if not (isinstance(r, dict) and r.get("success")) else None),
            "rows": [(x.get("defName") if isinstance(x, dict) else x) for x in (r.get("defs") or r.get("results") or [])][:60] if isinstance(r, dict) else None}
def tp(t):
    r = S.call("jawa/type_probe", typeName=t)
    return {"resolved": r.get("resolved") if isinstance(r, dict) else None, "success": r.get("success") if isinstance(r, dict) else None}
def msf(t, action, field=None, value=None):
    kw = dict(typeName=t, action=action)
    if field: kw["field"] = field
    if value is not None: kw["value"] = value
    r = S.call("jawa/mod_settings_field", **kw)
    return r if isinstance(r, dict) else {"raw": str(r)[:300]}
def toggle(t, field):
    a = msf(t, "get", field); b = msf(t, "set", field, "False"); c = msf(t, "get", field)
    d = msf(t, "set", field, str(a.get("value", a.get("current", "True")))); e = msf(t, "get", field)
    return {"get0": a, "set_false": b, "get1": c, "restore": d, "get2": e}
def drain():
    r = S.call("jawa/drain_log", limit=400, errorsOnly=True)
    return [m.get("text", "") for m in (r.get("messages") or [])] if isinstance(r, dict) else None
ERR = drain()
rec("_drain_errors", n=None if ERR is None else len(ERR), sample=(ERR or [])[:12])
def errs(*needles):
    if ERR is None: return None
    return [m[:200] for m in ERR if any(n in m for n in needles)]

CB = "RimMandrake.CreatureBehaviors."
# BAZAAR A1
rec("BAZAAR_PRICE_ENGINE_1.A1", defs=gd("ThingDef/RM_PriceAlmanac;ThingDef/RM_HagglerModule;ThingDef/RM_ManifestDecoder;ThingDef/RM_TransponderScanner;HediffDef/RM_PriceAlmanacFitted;HediffDef/RM_HagglerModuleFitted;HediffDef/RM_ManifestDecoderFitted;HediffDef/RM_TransponderScannerFitted"),
    seeds=gd("RM_BazaarSeedRuleDef/RM_BazaarSeed_DesertWater;RM_BazaarSeedRuleDef/RM_BazaarSeed_BrineSalt;RM_BazaarSeedRuleDef/RM_BazaarSeed_PropaneFuel;RM_BazaarSeedRuleDef/RM_BazaarSeed_BoilingSeaStill"),
    store=tp("RimMandrake.Bazaar.RM_BazaarEconomy"), settings=msf("RimMandrake.Bazaar.RM_BazaarSettings", "list"), errs=errs("Bazaar", "RM_Bazaar"))
# BLOWER A2
rec("BLOWER_ROOM_COOLER_1.A2", ctl=gd("ThingDef/RM_DryAirBlower"), errs=errs("RM_DryAirBlower", "CompProperties_BlowerRoomCooler", "CompProperties_TempControl"))
# CATHEDRAL A1
rec("CATHEDRAL_MECHANOID_PASS_VERBS_1.A1", defs=gd("HediffDef/RUT_CathedralPass;BiomeDef/RM_RustCathedral;BiomeDef/RUT_RustCathedral"),
    harm=S.call("jawa/harmony_patches", typeName="GenHostility", methodName="HostileTo"),
    setting=msf("RimMandrake.Utinni.CathedralPass.CathedralPassSettings", "get", "cathedralPassEnabled"))
# toggles
rec("DECOY_SHADE_TARP_1.A1", probes={n: tp(CB + n) for n in ("RM_CompDecoyShade", "RM_FalseShadeExtension", "RM_MapComponent_FalseShade")},
    defs=gd("ThingDef/RM_DecoyShadeTarp;ResearchProjectDef/RM_DecoyShadeResearch"), toggle=toggle(CB + "RM_CreatureBehaviorsSettings", "decoyShadeEnabled"))
rec("SHIP_TOW_LINE_1.A2", probes={n: tp(CB + n) for n in ("RM_CompSalvageWinch", "RM_CompProperties_SalvageWinch", "RM_SalvageWinchRules")},
    defs=gd("ThingDef/RM_SalvageWinch;ResearchProjectDef/RM_SalvageWinch"), toggle=toggle(CB + "RM_CreatureBehaviorsSettings", "salvageWinchEnabled"))
rec("VERMIN_EAT_BREEDING_FOOD_1.A2", probes={n: tp(CB + n) for n in ("RM_CompVerminBreeder", "RM_VerminFoodMath")},
    toggle=toggle(CB + "RM_CreatureBehaviorsSettings", "verminBreedingEatsFood"))
EH = "RimMandrake.EnvironmentalHazards.RM_EnvironmentalHazardsSettings"
rec("SCREEN_STOPS_SPORES_1.A1", toggle=toggle(EH, "screenStopsSporesEnabled"))
# empire
rec("EMPIRE_ESCALATION_LADDER_1.A4", defs=gd(";".join("RUT_EmpireRungDef/RUT_EmpireRung_" + n for n in ("Probe", "Spotter", "Strike", "Cordon", "Breach", "Bombardment")), "rungIndex,kind"), errs=errs("RUT_EmpireRung"))
# force
rec("FORCE_DISTURBANCE_REFLAVOR_1.A1", defs=gd("IncidentDef/PsychicDrone;IncidentDef/PsychicSoothe;GameConditionDef/PsychicDrone;GameConditionDef/PsychicSoothe;GameConditionDef/PsychicDroner;GameConditionDef/PsychicSuppression;IncidentDef/PsychicEmanatorShipPartCrash", "label,description,letterText"))
# harmony
rec("HARMONY_PATCH_RESILIENCE_1.A1", takedamage=S.call("jawa/harmony_patches", typeName="Thing", methodName="TakeDamage"))
rec("LAUNCH_HELD_COLONIST_WARNING_1.A2", harm=S.call("jawa/harmony_patches", typeName="GravshipUtility", methodName="PreLaunchConfirmation"))
# ninefold
src = open("src/RimMandrake/Ninefold/Defs/RM_GodFavourTilts.xml", encoding="utf-8").read()
tilts = re.findall(r"<defName>([^<]+)</defName>", src)
rec("NINEFOLD_FAVOUR_ODDS_BUILD_1.A1", ntilts=len(tilts),
    tilts=gd(";".join("RM_GodFavourTiltDef/" + t for t in tilts)),
    rites=gd("PreceptDef/RUT_Ritual_NineFaults;RitualPatternDef/RUT_NineFaultsPattern;RitualBehaviorDef/RUT_NineFaultsBehavior;RitualOutcomeEffectDef/RUT_NineFaultsOutcome;RitualObligationTargetFilterDef/RUT_FreshFind;TaleDef/RUT_GaveTheNineFaults;ThoughtDef/RUT_GaveTheFirstSpark"),
    setting=msf("RimMandrake.Ninefold.RM_NinefoldSettings", "get", "favourOddsEnabled"), errs=errs("RM_Tilt_", "RUT_NineFaults"))
# rakatan
rec("RAKATAN_ARCHOTECH_MACHINES_1.A1", defs=gd("ThingDef/RM_WM_AncientComponent;ThingDef/RM_WM_AutomatedSmelter_Wrecked;ThingDef/RM_WM_AutomatedSmelter_Kludged;ThingDef/RM_WM_AutomatedSmelter_Refurbished;ThingDef/RM_WM_AutomatedSmelter_Repaired;ThingDef/RM_WM_PowerCell_Wrecked;ThingDef/RM_WM_PowerCell_Kludged;ThingDef/RM_WM_PowerCell_Refurbished;ThingDef/RM_WM_PsychicEmanator_Wrecked;ThingDef/RM_WM_PsychicEmanator_Kludged;ThingDef/RM_WM_PsychicEmanator_Refurbished;ResearchProjectDef/RM_WM_AutomatedSmelterRestoration;ResearchProjectDef/RM_WM_PowerCellRestoration;ResearchProjectDef/RM_WM_EmanatorRestoration"), errs=errs("RM_WM_"))
# rustcathedral
rec("RUSTCATHEDRAL_BASE_FINISH_BUILD_1.A4", probe=S.call("jawa/biome_probe", biomes="RM_RustCathedral", find="RSW_Mynock,RM_CathedralRoach"))
# salvage
w = ["ThingDef/RUT_FoundrySalvageCache", "IncidentDef/RM_WreckFall", "IncidentDef/RUT_FallLineWreckFall", "ThingSetMakerDef/RUT_SalvageLoot_Foundry", "ThingSetMakerDef/RUT_SalvageLoot_Imperial",
     "RimMandrake.Wreckage.RM_WreckListDef/RUT_WreckList_FallLine", "RimMandrake.Wreckage.RM_WreckWeatheringDef/RUT_WreckWeathering_FallLine", "RimMandrake.Wreckage.RM_WreckWeatheringDef/RUT_WreckWeathering_ForgeWarm", "GenStepDef/RM_WreckField_Scald"]
tiers = ("Scrap", "Hull", "Tank", "Carapace", "Sealed")
loot = ["ThingSetMakerDef/RM_SalvageLoot_%s" % t for t in tiers] + ["ThingSetMakerDef/RM_SalvageLoot_%s_Rare" % t for t in tiers[1:]] + ["ThingSetMakerDef/RM_SalvageLoot_GreyShards"]
rec("SALVAGE_WRECKAGE_EVERYWHERE_1.A1", campaign=gd(";".join(w)), loot=gd(";".join(loot)), errs=errs("RM_Wreck", "RM_SalvageLoot", "[Wreckage]"))
# shipvermin
rec("SHIPVERMIN_FREE_TIER_BEASTS_1.A2", defs=gd("ThingDef/RM_Skivvik;ThingDef/RM_Rattagh;ThingDef/RM_Gorrud;ThingDef/RM_Fethrik;PawnKindDef/RM_Skivvik;PawnKindDef/RM_Rattagh;PawnKindDef/RM_Gorrud;PawnKindDef/RM_Fethrik;AbilityDef/RM_FethrikFuelSpew"), errs=errs("ShipVermin", "RM_Skivvik", "RM_Rattagh", "RM_Gorrud", "RM_Fethrik"))
# solar mirrors
sm = ["ThingDef/" + d for d in ("RM_SignalMirror", "RM_StaticMirror", "RM_Heliostat", "RM_AncientHeliostat", "RM_SunStone", "RM_SolarFurnace", "RM_MirrorDetent", "RM_SunVaultWall", "RM_SunVaultSeal", "RM_GlazedAperture")] + \
     ["JobDef/" + j for j in ("RM_ReAimMirror", "RM_CleanMirror", "RM_RepairAncientMirror", "RM_FlashHeliograph")] + ["WorkGiverDef/" + x for x in ("RM_ReAimMirror", "RM_CleanMirror", "RM_RepairAncientMirror")] + ["GenStepDef/RM_GenStep_AncientMirrorField"]
rec("SOLAR_MIRRORS_BUILD_1.A2", defs=gd(";".join(sm)), shade=S.call("jawa/shade_probe"),
    errs=errs("mandrake.rm.solarmirrors", "RimMandrake.SolarMirrors", "RM_CompMirror", "RM_MirrorLight", "RM_SolarFurnace", "RM_Heliostat", "RM_StaticMirror", "RM_SignalMirror", "RM_SunStone", "IRM_LightLayer", "RegisterLightSource"))
# taken by land
rec("TAKEN_BY_LAND_SERVICE_1.A2", proof=S.call("jawa/static_call", type="RimMandrake.FlowWorks.Rivers.RM_RiverWorksProof", method="ProofTaken", args="-"))
# warscar
rec("WARSCAR_AEROSOL_SCREEN_1.A1", defs=gd("ThingDef/RM_AerosolScreen;ResearchProjectDef/RM_AerosolScreenResearch;ThingDef/RM_GlowerCrust;ThingDef/RM_GlowerPlate;ThingDef/RM_GlowerShieldPanel;ThingDef/RM_ProjectorCore;GameConditionDef/RM_Settling;BiomeDef/RM_Warscar;ThingDef/RM_WarscarProjector_Salvaged"),
    t1=tp("RimMandrake.Scarlands.RM_CompAerosolScreen"), t2=tp("RimMandrake.Scarlands.RM_PollutionSense"), errs=errs("AerosolScreen", "PollutionSense"))
# gravship wires
rec("GRAVSHIP_WIRES_SURVIVE_LAUNCH_1.A2", setting=msf("RimMandrake.GimmeSomeSlack.Aerial.AerialSettings", "get", "keepWiresOnGravship"),
    toggle=toggle("RimMandrake.GimmeSomeSlack.Aerial.AerialSettings", "keepWiresOnGravship"))
# vexxith / ticker A4 / elder / etc controls
rec("VEXXITH_CLOSED_LOOP_BUILD_1.A2", takedamage=OUT["HARMONY_PATCH_RESILIENCE_1.A1"]["takedamage"])
rec("TICKER_NEVER_FIRES_FIX_1.A4", dryrooms=tp("RimMandrake.EnvironmentalHazards.RM_MapComponent_DryRooms"))
rec("ELDER_TREASURE_TAG_TABLE_1.A1", defs=gd("ThingDef/RM_ElderSealedRelic;ThingDef/RM_ElderUnknownWeapon"))
rec("MOVING_DUNES_BUILD_1.A3", defs=gd("RimMandrake.MovingDunes.RM_DuneMaterialDef/RM_Dunes_Sand;ThingDef/RM_Dunes_BuriedCache"))

# ---- log-only (no bridge)
L = glob.glob("/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Player.log") or [os.path.expandvars(r"%USERPROFILE%\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Player.log")]
rec("_log_path", p=L[0])
OUT["_note"] = "raw replies; judged by hand in belt_acc_sitting_20261009.md"
json.dump(OUT, open(os.path.join("Transient", "belt_acc_l1_raw_20261009.json"), "w"), indent=1, default=str)
print("wrote", len(OUT), "records")
