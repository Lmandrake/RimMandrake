"""LeaningScrub's site preconditions for the northstar driver.
`preflight(s) -> [str]`: every failed precondition, empty = clean. Dev tooling, never deployed.
Built only from northstar_driver.site primitives (existing bridge tools).

The quicktest map the baroque_wave0 tier starts on is enough: every mechanic this suite drives
is keyed on a def or a weather, not on the map's biome. (The Lean is the one exception and is
not driven: see validation.py's docstring.) The suite builds and clears its own pads."""
import contextlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from northstar_driver import site                         # noqa: E402

SETTINGS = "RimMandrake.LeaningScrub.RM_LeaningScrubSettings"


def _defaults():
    """The shipped defaults, single-sourced from validation.py (never copied here)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("lscrub_validation_defaults",
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
        bad.append("map_size: both axes must be >= 150 (pads sit 45 cells from the centre), got "
                   "%sx%s" % (mm.get("sizeX"), mm.get("sizeZ")))
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
    try:
        with contextlib.suppress(Exception):
            s.call("jawa/weather_set", unlock=True)
        s.call("jawa/weather_get")
    except Exception as ex:
        bad.append("weather: %s" % ex)
    return bad
