"""The Contagion's site preconditions for the northstar driver.
`preflight(s) -> [str]`: every failed precondition, empty = clean. Dev tooling, never deployed.
Built only from northstar_driver.site primitives (existing bridge tools).

Two starts are both valid (validation.py, TWO STARTS): a stock map (quicktest or the `calm` saved site), or the
saved Contagion site (`test_site_saves.py load contagion`), already RM_Contagion. The suite takes a sick start
off the Contagion itself for the two components that need a stock map, re-tiles to RM_Contagion (chain `site`)
and puts the START biome back (chain `site_restore`). So an RM_Contagion map is NOT refused here (it was, until
CONTAGION_ARMS_UNTANGLE_SITE_ALREADY_SICK). What must hold BEFORE the run: a map >= 150 cells on both axes (pads
sit 45 cells from the centre), a real world tile (the retiles need one), all five DLCs, and the settings at their
shipped defaults (a leftover value would make the first arm mean something else)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from northstar_driver import site                         # noqa: E402

SETTINGS = "RimMandrake.Contagion.RM_ContagionSettings"


def _defaults():
    """The shipped defaults, single-sourced from validation.py (never copied here)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("contagion_validation_defaults",
                                                  os.path.join(HERE, "validation.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.DEFAULTS


def _same(got, want):
    if isinstance(want, bool):
        return str(got).strip().lower() == str(want).lower()
    try:
        return abs(float(str(got).replace(",", ".")) - float(want)) < 1e-6
    except (TypeError, ValueError):
        return False


def preflight(s):
    bad = []
    mm = s.call("jawa/map_info") or {}
    if min(mm.get("sizeX") or 0, mm.get("sizeZ") or 0) < 150:
        bad.append("map_size: both axes must be >= 150, got %sx%s" % (mm.get("sizeX"), mm.get("sizeZ")))
    if mm.get("tileValid") is False:
        bad.append("map_tile: a pocket map has no world tile to re-tile")
    try:
        site.dlc_status(s)
    except Exception as ex:
        bad.append("dlc_status: %s" % ex)
    try:
        wrong = {}
        for field, want in sorted(_defaults().items()):
            r = s.call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field=field) or {}
            if r.get("success") is False or not _same(r.get("value"), want):
                wrong[field] = r.get("value", r.get("message"))
        if wrong:
            bad.append("settings_defaults: not at shipped defaults (or missing): %s" % wrong)
    except Exception as ex:
        bad.append("settings_defaults: %s" % ex)
    return bad
