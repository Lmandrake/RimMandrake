"""Warcasket's site preconditions for the northstar driver.
`preflight(s) -> [str]`: every failed precondition, empty = clean. Dev tooling, never deployed.
Built only from northstar_driver.site primitives (existing bridge tools)."""
from northstar_driver import site

SETTINGS = "RimMandrake.Warcasket.RM_WarcasketSettings"
DEFAULTS = {"masterEnabled": True, "compoundFailureEnabled": True, "terrainImmersionEnabled": True,
            "sarcophagiEnabled": True, "caskBayShieldingEnabled": True, "coreDoseEnabled": True}


def preflight(s):
    bad = []
    mm = s.call("jawa/map_info") or {}
    # compound_failure builds two 13x13 rooms 46 cells apart and clears a 100-cell square
    if min(mm.get("sizeX") or 0, mm.get("sizeZ") or 0) < 150:
        bad.append("map_size: both axes must be >= 150, got %sx%s" % (mm.get("sizeX"), mm.get("sizeZ")))
    try:
        site.dlc_status(s)          # Biotech (pollution, toxic buildup) and Odyssey (vacuum) are load-bearing
    except Exception as ex:
        bad.append("dlc_status: %s" % ex)
    try:
        wrong = site.read_settings(s, SETTINGS, DEFAULTS)
        if wrong:
            bad.append("settings_defaults: not at shipped defaults: %s" % wrong)
    except Exception as ex:
        bad.append("settings_defaults: %s" % ex)
    try:
        site.weather_lock(s, "Clear")
    except Exception as ex:
        bad.append("weather: %s" % ex)
    return bad
