"""J0 preflight: is this game session the one the queue needs?

Checks (each can FAIL): a Playing map (starts the quicktest world if not); every bridge tool the queue drives
is in the live tool census; the companion answers (pawn_census) and its damage recorder is installed; every
suite mod J1 re-runs is in the live ModsConfig activeMods (parsed, never grepped).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import Unmeasurable, call, main, tool_present   # noqa: E402

REQUIRED_TOOLS = (
    "jawa/pawn_census", "jawa/pawn_roles", "jawa/damage_log", "jawa/incident_queue_peek",
    "jawa/incident_queue_clear", "jawa/incident_schedule", "jawa/pawn_force_mental_break", "jawa/ordered_job",
    "jawa/spawn_pawn", "jawa/map_fire", "jawa/pawn_force_incapacitate", "jawa/damage", "jawa/pawn_resurrect",
    "jawa/world_tile_export", "jawa/world_tile_get", "jawa/world_tile_map_generate", "jawa/colony_found",
    "jawa/set_current_map", "jawa/destroy_bulk", "jawa/list_things", "jawa/list_pawns",
    "rimworld/take_screenshot", "rimworld/step_game_ticks",
)


def active_package_ids():
    import xml.etree.ElementTree as ET
    from game_paths import MODS_CONFIG
    root = ET.parse(MODS_CONFIG).getroot()
    return {(li.text or "").strip().lower() for li in root.find("activeMods")}


def body(s, job):
    dry = job.dry_run
    if not dry:
        import runner
        state = runner.ensure_playing_map()
        job.note("map", state)
        job.check("a Playing map exists (or was started)", state in ("playing", "started"), state)
    missing = [t for t in REQUIRED_TOOLS if not tool_present(s, t)]
    job.check("every tool the queue drives is in the live census", not missing, "missing: %s" % missing)
    c = call(s, "jawa/pawn_census", limit=5)
    job.check("companion answers (jawa/pawn_census success)", c.get("success"), c.get("message"))
    d = call(s, "jawa/damage_log", action="status")
    inst = d.get("installed") or {}
    job.check("damage recorder installed (damage and kill hooks)", d.get("success") and inst.get("damage") and inst.get("kill"),
              d.get("message") or inst)
    if dry:
        job.note("mods", "dry run: ModsConfig not read")
        return
    import runner
    from jobs import suite_mods
    want = {}
    for m in suite_mods():
        try:
            want[m] = runner.mod_package_id(runner.find_mod_dir(m))
        except Exception as e:                                  # noqa: BLE001
            want[m] = "UNRESOLVED (%s)" % e
    try:
        live = active_package_ids()
    except Exception as e:                                      # noqa: BLE001
        raise Unmeasurable("cannot parse the live ModsConfig: %s" % e)
    absent = {m: p for m, p in want.items() if p not in live}
    job.note("active_count", len(live))
    job.check("every J1 suite mod is active in ModsConfig (prep_wsl.py composed them)", not absent, absent)


if __name__ == "__main__":
    sys.exit(main("J0_preflight", body))
