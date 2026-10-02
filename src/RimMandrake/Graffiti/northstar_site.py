"""Graffiti's site preconditions for the northstar driver (trial plan section 3.13).
`preflight(s) -> [str]`: every failed precondition, empty = clean. Dev tooling, never deployed.
Built only from northstar_driver.site primitives (existing bridge tools). Preconditions that need a
tool that does not exist yet are listed in northstar_driver.site.NEEDED_TOOLS, not faked here."""
from northstar_driver import site

SETTINGS = "RimMandrake.Graffiti.RM_GraffitiSettings"
DEFAULTS = {"paintingEnabled": True, "paintIntervalTicks": 250, "viewerReactionEnabled": True,
            "breachBiasEnabled": True, "raidExitTaggingEnabled": True, "autoCleanProtectionEnabled": True}
SITE = (60, 60, 80, 80)     # carved at the map centre by the suite; checked for filth here


def preflight(s):
    bad = []
    mm = s.call("jawa/map_info") or {}
    if min(mm.get("sizeX") or 0, mm.get("sizeZ") or 0) < 150:
        bad.append("map_size: both axes must be >= 150, got %sx%s" % (mm.get("sizeX"), mm.get("sizeZ")))
    try:
        site.dlc_status(s)
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
