"""BlueDesert's site preconditions for the northstar driver.
`preflight(s) -> [str]`: every failed precondition, empty = clean. Dev tooling, never deployed.
Built only from northstar_driver.site primitives (existing bridge tools).

The quicktest map the baroque_wave0 tier starts on is enough: every mechanic this suite drives is keyed on a
def, a weather or a setting, not on the map's biome. (The ablation incident, murrek re-seed and the biome's own
Haze carrier are keyed on the biome and are not driven: see validation.py's docstring, BLUE_DESERT_SITE_1.)
The suite builds and clears its own pads. It also wants a FRESH map: a map where an earlier run left fires, a
half-eaten flora field or a vhaulk wandering will read noise, and a quicktest map is cheap (~90 s)."""
import contextlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from northstar_driver import site                         # noqa: E402

SETTINGS = "RimMandrake.BlueDesert.RM_BlueDesertSettings"
TOOLS_NEEDED = (
    "jawa/biome_probe", "jawa/cell_temperature", "jawa/damage", "jawa/destroy_batch", "jawa/drain_log",
    "jawa/fire_incident", "jawa/game_condition", "jawa/get_def", "jawa/get_defs", "jawa/get_roof_batch",
    "jawa/get_terrain_layers", "jawa/inspect_string", "jawa/letter_list", "jawa/list_pawns",
    "jawa/list_things", "jawa/make_empty_room", "jawa/map_info", "jawa/mod_settings_field",
    "jawa/ordered_job", "jawa/pawn_flight", "jawa/pawn_need", "jawa/room_heat", "jawa/set_draft",
    "jawa/designate_batch", "jawa/set_thing_props",
    "jawa/set_pawn_skill", "jawa/set_plants", "jawa/set_terrain_batch", "jawa/spawn_batch",
    "jawa/spawn_pawn", "jawa/weather_get", "jawa/weather_set", "jawa/window_list_close",
    "rimworld/open_mod_settings", "rimworld/set_time_speed")


def _defaults():
    """The shipped defaults, single-sourced from validation.py (never copied here)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("bdesert_validation_defaults",
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
        bad.append("map_size: both axes must be >= 150 (pads sit up to 62 cells from the centre), got "
                   "%sx%s" % (mm.get("sizeX"), mm.get("sizeZ")))
    try:
        site.dlc_status(s)
    except Exception as ex:
        bad.append("dlc_status: %s" % ex)
    have = getattr(s, "tools", None) or set()
    missing = [t for t in TOOLS_NEEDED if t not in have]
    if missing:
        bad.append("tools_missing: the live bridge does not declare %s (companion DLL not deployed?)" % missing)
    try:
        wrong = {}
        for field, want in sorted(_defaults().items()):
            r = s.call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field=field) or {}
            if r.get("success") is False or not _same(r.get("value"), want):
                wrong[field] = r.get("value", r.get("message"))
        if wrong:
            bad.append("settings_defaults: not at shipped defaults (a previous run left them?): %s" % wrong)
    except Exception as ex:
        bad.append("settings_defaults: %s" % ex)
    try:
        with contextlib.suppress(Exception):
            s.call("jawa/weather_set", unlock=True)
        s.call("jawa/weather_get")
    except Exception as ex:
        bad.append("weather: %s" % ex)
    return bad
