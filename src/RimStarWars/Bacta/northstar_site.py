"""Bacta's site preconditions for the northstar driver. `preflight(s) -> [str]`: every failed precondition, empty = clean.
Dev tooling, never deployed. Built only from existing bridge tools."""
SETTINGS = "RimMandrake.StarWars.Bacta.BactaSettings"


def preflight(s):
    bad = []
    mm = s.call("jawa/map_info") or {}
    if min(mm.get("sizeX") or 0, mm.get("sizeZ") or 0) < 80:
        bad.append("map_size: both axes must be >= 80 for the 40x40 site, got %sx%s" % (mm.get("sizeX"), mm.get("sizeZ")))
    r = s.call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field="healingEnabled") or {}
    if not r.get("success"):
        bad.append("settings_reachable: BactaSettings.healingEnabled unreadable (mandrake.rsw.bacta not loaded?): %s" % str(r)[:160])
    return bad
