"""GelatinousSlime site preconditions for the northstar driver. `preflight(s) -> [str]`, empty = clean.
The suite builds its own 40x40 site (slime half / concrete half) at the map centre, so this checks only
what it cannot build: a map big enough for it, and all five DLCs (genes need Biotech)."""
from northstar_driver import site


def preflight(s):
    bad = []
    mm = s.call("jawa/map_info") or {}
    if min(mm.get("sizeX") or 0, mm.get("sizeZ") or 0) < 100:
        bad.append("map_size: both axes must be >= 100, got %sx%s" % (mm.get("sizeX"), mm.get("sizeZ")))
    try:
        site.dlc_status(s)
    except Exception as ex:
        bad.append("dlc_status: %s" % ex)
    return bad
