"""LuminousPigment's site preconditions for the northstar driver. `preflight(s) -> [str]`: every failed
precondition, empty = clean. Dev tooling, never deployed. Built only from existing bridge tools.

Not checked here (the suite measures them itself and reads UNMEASURED when the site is wrong):
  - whether crowncarpet has already been seen in this game (GameComponent_Deepfire.matSeen persists, so
    research_gate.locked_before_sighting reads UNMEASURED on a used game: run on a FRESH quicktest game);
  - whether the pad terrain is walkable (a quicktest map is flat soil; a pad on water fails its own component).
"""
from northstar_driver import site

SETTINGS = "RimMandrake.LuminousPigment.LuminousPigmentSettings"
BOOLS = ("shoreMatsEnabled", "deepfireStackGlows", "glowTankEnabled", "paintingEnabled", "floorsPaintable",
         "wallsPaintable", "furniturePaintable", "apparelPaintable", "weaponsPaintable", "wornLightEnabled",
         "stylingStationLacquer", "combatPenaltiesEnabled", "artQualityBump", "cuisineEnabled",
         "hediffGlowEnabled", "godsReact", "ishkoIdolPaintable", "statusEnabled")
NUMBERS = {"matLifeDays": 1.0, "matChillKillTemp": 10.0, "deepfireMarketValue": 90.0, "maxCoats": 3.0,
           "tankPowerGraceHours": 6.0, "pressYield": 2.0, "pressPower": 150.0, "costWallCell": 1.0,
           "costApparel": 3.0, "godDeltaDiminishAfter": 10.0}
TOOLS_NEEDED = ("deepfire/glow_at", "deepfire/comp_coats", "deepfire/add_coat", "deepfire/remove_coats",
                "deepfire/designate", "deepfire/force_apply_job", "deepfire/debug_workgiver",
                "jawa/power_net", "jawa/research_availability", "jawa/inspect_string", "jawa/bill_add",
                "rimworld/execute_debug_action", "rimworld/list_debug_action_children",
                "rimworld/open_mod_settings", "jawa/window_list_close", "jawa/mod_settings_field")


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _get(s, field):
    return (s.call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field=field) or {}).get("value")


def preflight(s):
    bad = []
    mm = s.call("jawa/map_info") or {}
    if min(mm.get("sizeX") or 0, mm.get("sizeZ") or 0) < 150:
        bad.append("map_size: both axes must be >= 150 (the suite's pads sit up to 60 cells from the centre), got %sx%s"
                   % (mm.get("sizeX"), mm.get("sizeZ")))
    try:
        site.dlc_status(s)
    except Exception as ex:
        bad.append("dlc_status: %s" % ex)
    have = getattr(s, "tools", None) or set()
    missing = [t for t in TOOLS_NEEDED if t not in have]
    if missing:
        bad.append("tools_missing: the live bridge does not declare %s (companion DLL not deployed?)" % missing)
    wrong = {}
    try:
        for f in BOOLS:
            got = _get(s, f)
            if str(got) != "True":
                wrong[f] = got
        for f, want in NUMBERS.items():
            got = _get(s, f)
            v = _num(got)
            if v is None or abs(v - want) > 1e-6:
                wrong[f] = got
        got = _get(s, "pressGate")
        if str(got) != "Research":
            wrong["pressGate"] = got
    except Exception as ex:
        bad.append("settings_defaults: %s" % ex)
    if wrong:
        bad.append("settings_defaults: not at shipped defaults (a previous run left them?): %s" % wrong)
    return bad
