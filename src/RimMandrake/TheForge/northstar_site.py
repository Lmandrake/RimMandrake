"""The Forge's site preconditions for the northstar driver. `preflight(s) -> [str]`: every failed precondition, empty
= clean. Dev tooling, never deployed. Built only from northstar_driver.site primitives (existing bridge tools) plus
one plan-only deploy check.

The mod ships COMPOSED inside mandrake.rm.biomes, and the driver's own deploy-fingerprint check skips folded sources,
so a run would otherwise test whatever composed copy the game folder happens to hold. `composed_deploy_drift` runs the
compose plan (read-only, never --apply) and refuses on any drift in this mod's files or the EnvironmentalHazards kit it
depends on.

Not checked here (the suite measures them itself and reads UNMEASURED when the site is wrong):
  - whether spunstone is already revealed / researched in this game (the `spunstone` chain needs a FRESH game);
  - whether the pad's lava square already carries temp terrain from an earlier run (`_reset_pad` refuses);
  - whether RimWorld's 10,000-message log cap was reached (the log chain and the debug-action reads say so)."""
import os
import re
import subprocess

from northstar_driver import site

SETTINGS = "RimMandrake.TheForge.RM_TheForgeSettings"
HAZ_SETTINGS = "RimMandrake.EnvironmentalHazards.RM_EnvironmentalHazardsSettings"
DEFAULTS = {"modEnabled": True, "weatherPulseEnabled": True, "grandCycleEnabled": True, "gasWashEnabled": True,
            "cycleFloodingEnabled": True, "lavaFreezeEnabled": True, "meltBackDestroys": True,
            "floatstoneBloomEnabled": True, "cycleDormancyEnabled": True, "cycleTelegraphLetters": True,
            "keelworkEnabled": True, "spunstoneStudyEnabled": True, "forgeVoicesEnabled": True,
            "forgeVoicesVisualCues": False, "dhuvvoxClockEnabled": True}
HAZ_DEFAULTS = {"environmentalDamageEnabled": True, "weatherPulseEnabled": True}
MIN_MAP = 160               # the pad sits 30 cells off the map centre and spans ~50 cells east of it
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DRIFT_NEEDLES = ("TheForge", "EnvironmentalHazards")
TOOLS_NEEDED = ("jawa/game_condition", "jawa/weather_get", "jawa/letter_list", "jawa/inspect_string",
                "jawa/research_availability", "jawa/get_terrain_layers", "jawa/time_set_ticks",
                "jawa/biome_probe", "jawa/get_defs", "jawa/mod_settings_field", "jawa/spawn_batch",
                "jawa/list_pawns", "jawa/set_plants", "rimworld/execute_debug_action",
                "rimworld/list_debug_action_children", "rimworld/list_messages", "rimworld/open_mod_settings",
                "jawa/window_list_close")


def composed_deploy_drift(root=ROOT, timeout=900):
    """Drift lines of `deploy_custom_mods.py --compose biomes` (plan only) naming this mod or its kit. Runs under WSL
    python3: the deploy tool is developed there and a Windows interpreter composes the same files with different line
    endings and reports drift. Raises on a plan that did not run."""
    p = subprocess.run(["wsl.exe", "--cd", root, "-e", "python3",
                        "src/RimMandrake/Utils/deploy_custom_mods.py", "--compose", "biomes"],
                       capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="replace")
    out = (p.stdout or "") + (p.stderr or "")
    if p.returncode not in (0, 1) or "Traceback" in out:
        raise RuntimeError("compose plan did not run (rc=%s): %s" % (p.returncode, out[-300:]))
    # `+`/`~` lines are drift; `-` lines are files only in the game folder (kept)
    return [ln.strip() for ln in out.splitlines()
            if re.match(r"\s+[+~]\s", ln) and any(n in ln for n in DRIFT_NEEDLES)]


def preflight(s):
    bad = []
    mm = s.call("jawa/map_info") or {}
    if min(mm.get("sizeX") or 0, mm.get("sizeZ") or 0) < MIN_MAP:
        bad.append("map_size: both axes must be >= %d, got %sx%s" % (MIN_MAP, mm.get("sizeX"), mm.get("sizeZ")))
    try:
        site.dlc_status(s)
    except Exception as ex:
        bad.append("dlc_status: %s" % ex)
    have = getattr(s, "tools", None) or set()
    missing = [t for t in TOOLS_NEEDED if t not in have]
    if missing:
        bad.append("tools_missing: the live bridge does not declare %s (companion DLL not deployed?)" % missing)
    for type_name, expect in ((SETTINGS, DEFAULTS), (HAZ_SETTINGS, HAZ_DEFAULTS)):
        try:
            wrong = site.read_settings(s, type_name, expect)
            if wrong:
                bad.append("settings_defaults: %s not at shipped defaults (a previous run left them?): %s" % (type_name, wrong))
        except Exception as ex:
            bad.append("settings_defaults(%s): %s" % (type_name, ex))
    try:
        drift = composed_deploy_drift()
        if drift:
            bad.append("composed_deploy: the game's mandrake.rm.biomes differs from source in %d file(s) "
                       "(deploy_custom_mods.py --compose biomes --apply, game closed): %s" % (len(drift), drift[:3]))
    except Exception as ex:
        bad.append("composed_deploy: could not check: %s" % ex)
    return bad
