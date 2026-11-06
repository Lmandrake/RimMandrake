#!/usr/bin/env python3
"""live_site.py -- make the running game show the scene a live proof reads: a map of one biome, or a named save.

    python.exe src/RimMandrake/Utils/live_site.py --biome RM_Stillsand [--temperature 30]
    python.exe src/RimMandrake/Utils/live_site.py --not-biome RM_LeaningScrub --biome RM_BlueDesert
    python.exe src/RimMandrake/Utils/live_site.py --save rm_proof_atmosphere
    python.exe src/RimMandrake/Utils/live_site.py --menu-dwell 20
    python.exe src/RimMandrake/Utils/live_site.py --without oblitus.mylittleplanet --needs 7f.alienworlds --save NAME --ignore-missing-mods
    python.exe src/RimMandrake/Utils/live_site.py --save rm_proof_atmosphere --restage-with AtmosphericBase

RELENTLESS_LIVE_FIX_GAME_UP_NOTHING_MEASURED: the live stage ran HORIZON_CARAVAN_VANILLA_REFUSES_1's Stillsand probe on a
Leaning Scrub map eight times and LEANINGSCRUB_STALL_SHARED_MOVE_1's proof on the very biome its criteria exclude, while
nothing ever set the map up. A live_proofs/<ID>.txt line `live-site A1: <this command>` makes relentless_live run it,
bridge held, before the proof; a non-zero exit here is UNMEASURED ("site not prepared"), and the proof does not run.

--biome: the recipe proven live 2026-10-01 (Stillsand/validation.py site chain): jawa/world_tile_set on the current
tile, jawa/world_commit, the vanilla debug action `Actions\\Regenerate Current Map` (it honours the tile's CURRENT
biome), poll until a map is ready, read jawa/map_info back. A map already of that biome is left alone (no regen).
Regenerating wipes the map's colonists, so three are spawned at the centre and hostiles destroyed, as the site chain does.
The quicktest world is scaffolding (CLAUDE.md worldgen ban: nothing here makes a planet a player receives), and a game
past --max-ticks (default two in-game days) is refused: that is someone's colony, not a test map.

--save: rimworld/load_game, then wait for Playing with a map (validation_core._wait_playing's rule). Canonical saves
(infrastructure/state/canon.yml) load read-only by definition: this tool never saves.

--menu-dwell N (WORLD_NULLTEX_FLOOD_HUNT_STACKLESS_SO_FAR): for a proof of what the MAIN MENU draws, which a game staged
on a map never shows. One jawa/ call first (the companion installs its probes on first contact, JawaBenchInit), then
rimworld/go_to_main_menu, N seconds in the Entry scene, and rimworld/start_debug_game_ready so the game is back on a
quicktest map for the proofs after it. Same --max-ticks refusal: the map it drops is a test map, never a colony.

--needs / --without PKG (repeatable; GENERATOR_MODS_PROVE_INERT_AFTER_CREATION): checked first, against the RUNNING
load (jawa/running_mods, never ModsConfig.xml, which names the NEXT load). A load that lacks a --needs id or holds a
--without one cannot be made right without a restart, so the site ends on a `reload needed: ...` line (exit 2), which
relentless_live carries as the row's why and the game phase restages; nothing is loaded on the wrong list.
--ignore-missing-mods (with --save): load_game with ignoreModCompatibility, for a proof whose experiment IS loading a save
without some of the mods it recorded (pair it with --without, so the running list is checked first).

--restage-with MOD (with --save rm_proof_*): when the load is refused (the fixture recorded mods the running list lacks,
or it is gone), src/RimMandrake/<MOD>/stage_proof_site.py re-makes it on the CURRENT map and list, then it is loaded.
Only a rm_proof_* fixture: a canonical or player save is never re-made.

Exit 0 the scene is up (read back), 2 it could not be made (UNMEASURED; never 1: a site is not a verdict).
Runs under Windows Python: RimBridge binds Windows loopback.
"""
import argparse
import json
import os
import sys
import time

READY, NOT_READY = 0, 2
REGEN = "Actions\\Regenerate Current Map"


def need_regen(info, biome, not_biome):
    """map_info -> (verdict, why): "ok" the map already serves, "regen" make `biome`, "no" cannot. Pure."""
    have = info.get("mapBiome")
    if biome and have == biome:
        return "ok", "the current map is already %s" % biome
    if not biome and have and have not in not_biome:
        return "ok", "the current map is %s, not %s" % (have, "/".join(not_biome))
    if not biome:
        return "no", "the map is %s and no --biome names what to make instead" % have
    return "regen", "the current map is %s, %s wanted" % (have, biome)


def _lc_call(rb):
    """rb.call takes a params dict; await_lifecycle calls call(tool, **params)."""
    return lambda tool, **p: rb.call(tool, p)


def _lc_clock():
    return time.time()          # read at call time: the selftest swaps this module's `time` for a fake clock


def _lc_sleep(s):
    time.sleep(s)


def wait_ready(rb, budget_s=300, step_s=5):
    """Poll the bridge until a map is up and the bridge settled (await_lifecycle settle=True: no `currentMapReady`
    key exists, measured 2026-10-07). The first poll waits step_s: a regen leaves the old map readable at first."""
    from await_lifecycle import await_lifecycle
    _lc_sleep(step_s)
    return await_lifecycle(_lc_call(rb), "map_ready", deadline_s=budget_s, poll_s=step_s, settle=True,
                           clock=_lc_clock, sleep=_lc_sleep).ok


def reply(r):
    """A tool reply -> its dict: an MCP-style {"content": [{"text": json}]} envelope is opened, anything else is {}."""
    if isinstance(r, dict) and isinstance(r.get("content"), list) and r["content"]:
        try:
            r = json.loads(r["content"][0].get("text") or "")
        except (ValueError, AttributeError, TypeError):
            return {}
    return r if isinstance(r, dict) else {}


def load_gap(needs, without, running, alias):
    """-> None when the running load fits, else the lines to print, the last a `reload needed:` line when the running
    list was read (an unread one is plain NOT READY: a restart is not known to help). Pure."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import live_def_check
    code, lines = live_def_check.condition(needs, without, running, alias)
    if code is None:
        return None
    if running is None or (alias is None and without):
        return lines + ["NOT READY: the running load could not be checked"]
    return lines + ["reload needed: restart on a list (all five DLC) that %s" % "; ".join(
        (["holds %s" % ", ".join(needs)] if needs else []) + (["lacks %s" % ", ".join(without)] if without else []))]


def check_load(a):
    """--needs/--without against the running load -> None, or the exit code after printing why."""
    if not a.needs and not a.without:
        return None
    import live_def_check
    with connect(60) as rb:
        running = live_def_check.running_ids(reply(rb.call("jawa/running_mods", {"details": False, "assembly": ""})))
    lines = load_gap(a.needs, a.without, running, live_def_check.aliases())
    if lines is None:
        print("load condition met: %s" % ", ".join(["has %s" % p for p in a.needs] + ["lacks %s" % p for p in a.without]))
        return None
    for ln in lines:
        print(ln)
    return NOT_READY


def connect(timeout):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import rimbridge_client as rc
    host, port, token = rc.resolve_endpoint(None, None, None, None)
    if not token:
        raise RuntimeError("no bridge token")
    return rc.RimBridge(host, port, token, timeout=timeout)


def biome_site(a):
    # 300 s: a timed-out mutation leaves an UNKNOWN-outcome marker that refuses every later write (the client's
    # guard), and Regenerate Current Map is the one call here slow enough to hit a short timeout.
    with connect(300) as rb:
        info = rb.call("jawa/map_info", {})
        if not isinstance(info, dict) or info.get("success") is False or info.get("tile") is None:
            print("NOT READY: no current map to make a site on (%s)" % str(info)[:200])
            return NOT_READY
        verdict, why = need_regen(info, a.biome, a.not_biome)
        if verdict != "regen":
            print(("READY: " if verdict == "ok" else "NOT READY: ") + why)
            return READY if verdict == "ok" else NOT_READY
        target = a.biome
        ticks = int((rb.call("jawa/time_clock", {}) or {}).get("ticksGame") or 0)
        if ticks > a.max_ticks:
            print("NOT READY: the game is at tick %d (> %d): a colony, not a test map; no regen" % (ticks, a.max_ticks))
            return NOT_READY
        print("site: %s; tile %s" % (why, info["tile"]))
        args = {"tiles": str(info["tile"]), "biome": target}
        if a.temperature is not None:
            args["temperature"] = a.temperature
        r = rb.call("jawa/world_tile_set", args)
        if not isinstance(r, dict) or r.get("success") is False:
            print("NOT READY: world_tile_set refused: %s" % str(r)[:300])
            return NOT_READY
        r = rb.call("jawa/world_commit", {})
        if not isinstance(r, dict) or r.get("success") is False:
            print("NOT READY: world_commit refused: %s" % str(r)[:300])
            return NOT_READY
        try:
            rb.call("rimworld/execute_debug_action", {"path": REGEN})
        except Exception as e:      # noqa: BLE001  the connection may drop while the map rebuilds
            print("regen call ended: %s" % str(e)[:200])
    with connect(60) as rb:
        if not wait_ready(rb, a.budget):
            print("NOT READY: no map %ds after %s" % (a.budget, REGEN))
            return NOT_READY
        info = rb.call("jawa/map_info", {})
        if info.get("mapBiome") != target:
            print("NOT READY: the regenerated map is %r, not %s" % (info.get("mapBiome"), target))
            return NOT_READY
        cx, cz = (info.get("sizeX") or 0) // 2, (info.get("sizeZ") or 0) // 2
        try:     # the regenerated map has no colonists; a proof that wants them says so, the site is up either way
            rb.call("jawa/spawn_pawn", {"kindDef": "Colonist", "x": cx, "z": cz, "faction": "player", "count": 3})
            rb.call("rimworld/execute_debug_action", {"path": "Actions\\Destroy hostile pawns"})
        except Exception as e:      # noqa: BLE001
            print("colonists not spawned: %s" % str(e)[:200])
        print("READY: map %s on tile %s, %sx%s, 3 colonists at %d,%d" % (target, info.get("tile"), info.get("sizeX"),
                                                                        info.get("sizeZ"), cx, cz))
        return READY


RESTAGE_PREFIX = "rm_proof_"     # only a proof fixture save is ever re-made; a canonical or player save never is


def stager_path(mod):
    """--restage-with MOD -> src/RimMandrake/<MOD>/stage_proof_site.py (absolute), or None when MOD is not a plain
    folder name or holds no stager."""
    if not mod or not mod.replace("_", "").isalnum():
        return None
    p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), mod, "stage_proof_site.py")
    return p if os.path.isfile(p) else None


def run_stager(path, save):
    """The mod's stager on the CURRENT map, saving as `save` -> its exit code (it refuses a colony itself)."""
    import subprocess
    r = subprocess.run([sys.executable, path, "--save", save], capture_output=True, text=True, timeout=900)
    print(((r.stdout or "") + (r.stderr or "")).strip()[-800:])
    return r.returncode


def load_save(a):
    """-> the load_game reply. --ignore-missing-mods passes ignoreModCompatibility (GENERATOR_MODS_PROVE_INERT_AFTER_
    CREATION: the save records mods the experiment deliberately runs without, so the bridge's save.missing_mods
    pre-check would refuse the very load the proof is about)."""
    params = {"saveName": a.save}
    if a.ignore_missing_mods:
        params["ignoreModCompatibility"] = True
    with connect(120) as rb:
        return rb.call("rimworld/load_game", params)


def save_site(a):
    r = load_save(a)
    if (not isinstance(r, dict) or r.get("success") is False) and a.restage_with:
        # ATMOSBASE_PROOF_FIX_UNLIT_LEAVES_DARK_LAMP: the fixture save recorded 6 mods the current list lacks
        # (save.missing_mods on every game). A proof fixture is re-made on the running list by its own stager, then
        # loaded, so the fixture can never age out of the load again.
        print("site: load_game %s refused (%s); re-staging it on the running list with %s"
              % (a.save, str((r or {}).get("code") if isinstance(r, dict) else r)[:80], a.restage_with))
        rc = run_stager(stager_path(a.restage_with), a.save)
        if rc != 0:
            print("NOT READY: the %s stager could not re-make %s (exit %s)" % (a.restage_with, a.save, rc))
            return NOT_READY
        r = load_save(a)
    if not isinstance(r, dict) or r.get("success") is False:
        print("NOT READY: load_game %s refused: %s" % (a.save, str(r)[:300]))
        return NOT_READY
    with connect(60) as rb:
        if not wait_ready(rb, a.budget):
            print("NOT READY: %s did not reach Playing with a map in %ds" % (a.save, a.budget))
            return NOT_READY
        info = rb.call("jawa/map_info", {})
        print("READY: %s loaded, map %s tick %s" % (a.save, info.get("mapBiome"), info.get("ticksGame")))
        return READY


def wait_state(rb, want, budget_s, step_s=2):
    """Wait until programState == want: "Entry" (the menu, as perf/vitals_overhead.py reads it) or "Playing"."""
    from await_lifecycle import await_lifecycle
    state = {"Entry": "menu", "Playing": "playing"}[want]
    return await_lifecycle(_lc_call(rb), state, deadline_s=budget_s, poll_s=step_s, clock=_lc_clock,
                           sleep=_lc_sleep).ok


def menu_site(a):
    with connect(120) as rb:
        try:        # first jawa/ contact: the companion arms its probes here, whatever this call answers
            info = rb.call("jawa/map_info", {})
        except Exception as e:      # noqa: BLE001  at the menu already there is no map to describe
            info = {"error": str(e)[:200]}
        ticks = int((rb.call("jawa/time_clock", {}) or {}).get("ticksGame") or 0) \
            if isinstance(info, dict) and info.get("tile") is not None else 0
        if ticks > a.max_ticks:
            print("NOT READY: the game is at tick %d (> %d): a colony, not a test map; not leaving it" % (ticks, a.max_ticks))
            return NOT_READY
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import bridge_concurrency_guard as guard
        guard.refuse_if_foreign_activity("rimworld/go_to_main_menu")
        rb.call("rimworld/go_to_main_menu", {})
        if not wait_state(rb, "Entry", 120):
            print("NOT READY: never reached the main menu in 120 s")
            return NOT_READY
        print("site: main menu reached; dwelling %ds" % a.menu_dwell)
        time.sleep(a.menu_dwell)
    with connect(900) as rb:
        try:
            rb.call("rimworld/start_debug_game_ready", {"timeoutMs": 900000, "readiness": "mapData", "pauseIfNeeded": True})
        except Exception as e:      # noqa: BLE001  the connection may drop while the map generates
            print("quicktest call ended: %s" % str(e)[:200])
    with connect(60) as rb:
        if not wait_ready(rb, a.budget):
            print("NOT READY: the quicktest after the menu dwell did not reach Playing with a map in %ds" % a.budget)
            return NOT_READY
        info = rb.call("jawa/map_info", {})
        print("READY: %ds at the main menu, then a quicktest map %s" % (a.menu_dwell, info.get("mapBiome")))
        return READY


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--biome", help="BiomeDef the current map must be")
    ap.add_argument("--not-biome", action="append", default=[], help="a BiomeDef the map must not be (repeatable)")
    ap.add_argument("--temperature", type=float)
    ap.add_argument("--save", help="a save name to load (no .rws)")
    ap.add_argument("--menu-dwell", type=int, help="seconds at the main menu, then a quicktest map back")
    ap.add_argument("--max-ticks", type=int, default=120000)
    ap.add_argument("--budget", type=int, default=300)
    ap.add_argument("--needs", action="append", default=[], help="a packageId the RUNNING load must hold (repeatable)")
    ap.add_argument("--without", action="append", default=[], help="a packageId it must not hold (repeatable)")
    ap.add_argument("--ignore-missing-mods", action="store_true",
                    help="--save: load even though the save records mods the running list lacks (ignoreModCompatibility)")
    ap.add_argument("--restage-with", metavar="MOD",
                    help="--save of a %s* fixture: when the load is refused, re-make the save on the running list with "
                         "src/RimMandrake/<MOD>/stage_proof_site.py, then load it" % RESTAGE_PREFIX)
    a = ap.parse_args(argv)
    if (a.ignore_missing_mods or a.restage_with) and not a.save:
        ap.error("--ignore-missing-mods and --restage-with need --save")
    if a.restage_with and not a.save.startswith(RESTAGE_PREFIX):
        ap.error("--restage-with re-makes only a %s* proof fixture, never %s" % (RESTAGE_PREFIX, a.save))
    if a.restage_with and not stager_path(a.restage_with):
        ap.error("--restage-with %s: no src/RimMandrake/%s/stage_proof_site.py" % (a.restage_with, a.restage_with))
    if sum((bool(a.save), bool(a.biome or a.not_biome), a.menu_dwell is not None)) != 1:
        ap.error("give one of --save, --biome / --not-biome, --menu-dwell")
    if a.menu_dwell is not None and not 1 <= a.menu_dwell <= 300:
        ap.error("--menu-dwell is 1..300 seconds")
    try:
        gap = check_load(a)
        if gap is not None:
            return gap
        if a.menu_dwell is not None:
            return menu_site(a)
        return save_site(a) if a.save else biome_site(a)
    except Exception as e:      # noqa: BLE001  any bridge failure is a site not made, never a verdict
        print("NOT READY: %s: %s" % (type(e).__name__, str(e)[:300]))
        return NOT_READY


if __name__ == "__main__":
    sys.exit(main())
