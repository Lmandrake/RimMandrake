"""Stillsand's site preconditions for the northstar driver.
`preflight(s) -> [str]`: every failed precondition, empty = clean. Dev tooling, never deployed.
Built only from northstar_driver.site primitives and existing bridge tools.

The suite's first chain (`site`) turns the quicktest world's current tile into a Stillsand map by
itself (world_tile_set + world_commit + Regenerate Current Map: the recipe proven live 2026-10-01), so
this pre-flight only proves the world is up and every settings field the suite flips is present at its
shipped default. It does NOT regenerate anything."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from northstar_driver import site                         # noqa: E402


def _validation():
    import importlib.util
    spec = importlib.util.spec_from_file_location("stillsand_validation_defaults",
                                                  os.path.join(HERE, "validation.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


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
    if mm.get("tile") is None:
        bad.append("quicktest_world: jawa/map_info reports no tile (start one: rimworld/start_debug_game_ready)")
    try:
        site.dlc_status(s)
    except Exception as ex:
        bad.append("dlc_status: %s" % ex)
    try:
        v = _validation()
        wrong = {}
        for field, want in sorted(v.DEFAULTS.items()):
            r = s.call("jawa/mod_settings_field", typeName=v.FIELD_TYPE[field], action="get", field=field) or {}
            if r.get("success") is False or not _same(r.get("value"), want):
                wrong[field] = r.get("value", r.get("message"))
        if wrong:
            bad.append("settings_defaults: not at shipped defaults (or missing): %s" % wrong)
    except Exception as ex:
        bad.append("settings_defaults: %s" % ex)
    return bad
