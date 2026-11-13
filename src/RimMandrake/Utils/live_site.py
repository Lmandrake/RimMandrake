#!/usr/bin/env python3
"""live_site.py -- make the running game show the scene a live proof reads: a map of one biome, or a named save.

    python.exe src/RimMandrake/Utils/live_site.py --biome RM_Stillsand [--temperature 30]
    python.exe src/RimMandrake/Utils/live_site.py --not-biome RM_LeaningScrub --biome RM_BlueDesert
    python.exe src/RimMandrake/Utils/live_site.py --save rm_proof_atmosphere
    python.exe src/RimMandrake/Utils/live_site.py --menu-dwell 20
    python.exe src/RimMandrake/Utils/live_site.py --game
    python.exe src/RimMandrake/Utils/live_site.py --without oblitus.mylittleplanet --needs 7f.alienworlds --save NAME --ignore-missing-mods
    python.exe src/RimMandrake/Utils/live_site.py --save rm_proof_atmosphere --restage-with AtmosphericBase
    python.exe src/RimMandrake/Utils/live_site.py --needs mandrake.rm.flowworks --game --stage-with FlowWorks --max-seconds 2100

--powered (GAMEENV_FIX_PROOFSITE_28883863_ITEMS_WAIT): after the site is made, the map holds at least one building of the
PowerTrader group. BATCHREADS_BUILD_ROUND_TRIP_CUT's power clause read the first 300 BuildingArtificial of a quicktest map
(ruin walls), found no CompPower and was UNMEASURED; a quicktest colony owns no powered building. A map that has one is
left alone; otherwise one vanilla SolarGenerator (Core, no stuff) is spawned near the centre and read back through the
PowerTrader group: a spawn that does not read back is NOT READY, never a site.

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
(infrastructure/state/canon.yml) load read-only by definition: this tool never saves. A game already on a map is first
seen to LEAVE Playing, since right after load_game the old map still reads Playing (skills/rimbridge/references/traps.md).
A load that DIES ends the wait at once (GAMEENV_FIX_HARNESS_47EE6093_ITEMS_WAIT: BENCH_r17_midrain threw
`Exception from asynchronous event: NullReferenceException` in WorldGrid.CreateRequiredLayers under World.ExposeData,
the game went back to the menu, and the site waited 300 s blind for a map that could never come, filed as a harness
fault): Player.log holding a long-event exception after its `Loading game from file <save>` line, or the menu holding
MENU_DEAD_S after the load answered. That ends on `NOT READY: site defect: the save X does not load on the running list:
...` naming the exception and its top frame, which relentless_envcause routes as a proof/site defect, not the harness's.

--menu-dwell N (WORLD_NULLTEX_FLOOD_HUNT_STACKLESS_SO_FAR): for a proof of what the MAIN MENU draws, which a game staged
on a map never shows. One jawa/ call first (the companion installs its probes on first contact, JawaBenchInit), then
rimworld/go_to_main_menu, N seconds in the Entry scene, and rimworld/start_debug_game_ready so the game is back on a
quicktest map for the proofs after it. Same --max-ticks refusal: the map it drops is a test map, never a colony.

--game (GAMEENV_FIX_PROOFSITE_528224CB_ITEMS_WAIT): a game with a map, whatever its biome, for a proof that stages its
own map (proof_scald_steam.setup generates a RM_TheScald map beside the home one). RINDCOAT's A1 proof met a game on the
main menu (get_game_info carries no ticksGame there) and read nothing. A map already up is left alone, so a proof
resuming a run across rounds keeps its map; only with no map (Entry, or Playing with mapCount 0) is
rimworld/start_debug_game_ready called. A game still loading is waited out first, never interrupted.

--needs / --without PKG (repeatable; GENERATOR_MODS_PROVE_INERT_AFTER_CREATION): checked first, against the RUNNING
load (jawa/running_mods, never ModsConfig.xml, which names the NEXT load). A load that lacks a --needs id or holds a
--without one cannot be made right without a restart, so the site ends on a `reload needed: ...` line (exit 2), which
relentless_live carries as the row's why and the game phase restages; nothing is loaded on the wrong list.
--ignore-missing-mods (with --save): load_game with ignoreModCompatibility, for a proof whose experiment IS loading a save
without some of the mods it recorded (pair it with --without, so the running list is checked first).

--restage-with MOD (with --save rm_proof_*): when the load is refused (the fixture recorded mods the running list lacks,
or it is gone), src/RimMandrake/<MOD>/stage_proof_site.py re-makes it on the CURRENT map and list, then it is loaded.
Only a rm_proof_* fixture: a canonical or player save is never re-made.

A plain --save refused save.missing_mods is retried with ignoreModCompatibility when every missing mod is RETIRED: on the
save's header, on neither the running load nor ModsConfig.FULL.LATEST.xml (GAMEENV_FIX_HARNESS_A412C1DF_ITEMS_WAIT: the
canonical start records 11 mods retired after it was saved, so no list could ever load it). A missing mod still on the
full list means the running load is short: that stays NOT READY, as does anything unread.

--stage-with MOD (GAMEENV_FIX_PROOFSITE_DFFDAFCB_ITEMS_WAIT; with a site that leaves a map): after the site is up,
src/RimMandrake/<MOD>/stage_proof_site.py builds its scene in the running game and saves nothing, for a scene a save cannot
carry (BENCH_r17_midrain reads at most 50 levelling links after a load; the 100 of record were never reloaded). Its last line
is the reason when it fails. --max-seconds N is its limit (default 900); relentless_live gives the whole site N + 120 s
(proof_budget), so a site line that needs more than site_max_s says so in the line.

Exit 0 the scene is up (read back), 2 it could not be made (UNMEASURED; never 1: a site is not a verdict).
Runs under Windows Python: RimBridge binds Windows loopback.
"""
import argparse
import json
import os
import re
import sys
import time
import xml.etree.ElementTree as ET

READY, NOT_READY = 0, 2
HEADER_BYTES = 1 << 20  # a save's <meta> sits at its top; the canonical start's modIds end well inside this
MENU_DEAD_S = 60        # the menu this long after load_game answered: the load never began, or it died and went back
LOAD_LINE = "Loading game from file %s with mods:"      # Verse.SavedGameLoaderNow, Player.log
DIED = ("Exception from asynchronous event:", "Exception from long event:")     # Verse.LongEventHandler
NO_LOAD = "site defect: the save %s does not load on the running list: %s"      # relentless_envcause.SITE_DEAD
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
            print("NOT READY: no current map to make a site on (%s)" % str(info))
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
            print("NOT READY: world_tile_set refused: %s" % str(r))
            return NOT_READY
        r = rb.call("jawa/world_commit", {})
        if not isinstance(r, dict) or r.get("success") is False:
            print("NOT READY: world_commit refused: %s" % str(r))
            return NOT_READY
        try:
            rb.call("rimworld/execute_debug_action", {"path": REGEN})
        except Exception as e:      # noqa: BLE001  the connection may drop while the map rebuilds
            print("regen call ended: %s" % str(e))
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
            print("colonists not spawned: %s" % str(e))
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
    print(((r.stdout or "") + (r.stderr or "")).strip())
    return r.returncode


def run_scene_stager(path, max_ticks, timeout_s):
    """--stage-with: the mod's stager builds its scene in the running game -> (exit code, its last line)."""
    import subprocess
    try:
        # it stops itself at timeout_s; the 60 s (inside the 120 relentless_live adds) is for its last calls, never a kill's
        r = subprocess.run([sys.executable, path, "--max-ticks", str(max_ticks), "--max-seconds", str(timeout_s)],
                           capture_output=True, text=True, timeout=timeout_s + 60, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        return NOT_READY, "ran past --max-seconds %d" % timeout_s
    print(((r.stderr or "") + (r.stdout or "")).strip())
    return r.returncode, ((r.stdout or "").strip().splitlines() or [(r.stderr or "").strip()])[-1]


def load_save(a):
    """-> the load_game reply. --ignore-missing-mods passes ignoreModCompatibility (GENERATOR_MODS_PROVE_INERT_AFTER_
    CREATION: the save records mods the experiment deliberately runs without, so the bridge's save.missing_mods
    pre-check would refuse the very load the proof is about)."""
    params = {"saveName": a.save}
    if a.ignore_missing_mods:
        params["ignoreModCompatibility"] = True
    with connect(120) as rb:
        return rb.call("rimworld/load_game", params)


def save_mod_ids(save):
    """-> the lowercased packageIds in `save`'s meta header, or None when the file or header cannot be read."""
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from game_paths import SAVES
        with open(os.path.join(SAVES, save + ".rws"), "rb") as f:
            head = f.read(HEADER_BYTES).decode("utf-8", "replace")
    except (OSError, ImportError):
        return None
    m = re.search(r"<modIds>(.*?)</modIds>", head, re.S)
    ids = re.findall(r"<li>\s*([^<\s]+)\s*</li>", m.group(1)) if m else []
    return [i.lower() for i in ids] or None


def full_list_ids(path=None):
    """-> the lowercased packageIds of the committed full list, or None when it cannot be read."""
    path = path or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "infrastructure", "state",
                                "modlists", "ModsConfig.FULL.LATEST.xml")
    try:
        ids = [(li.text or "").strip().lower() for li in ET.parse(path).getroot().find("activeMods")]
    except (OSError, ET.ParseError, TypeError):
        return None
    return [i for i in ids if i] or None


def retired_gap(recorded, running, full):
    """-> (retired, short): the mods the save records and the running load lacks, split by whether the full list still
    holds them. Pure. Any input None (unread) -> ([], None): nothing may be called retired on an unread list."""
    if recorded is None or running is None or full is None:
        return [], None
    missing = set(recorded) - set(running)
    return sorted(missing - set(full)), sorted(missing & set(full))


def load_past_retired(a, r):
    """A refused load -> the retried reply when every missing mod is retired, else `r` untouched (a why printed)."""
    if not isinstance(r, dict) or r.get("code") != "save.missing_mods" or a.ignore_missing_mods:
        return r
    import live_def_check
    with connect(60) as rb:
        running = live_def_check.running_ids(reply(rb.call("jawa/running_mods", {"details": False, "assembly": ""})))
    retired, short = retired_gap(save_mod_ids(a.save), running, full_list_ids())
    if short is None:
        print("site: %s's mods, the running load or the full list could not be read; no retired-mod retry" % a.save)
        return r
    if short or not retired:
        print("site: the running load lacks %s, still on the full list; a restart on that list is owed"
              % (", ".join(short) or "mods its header does not name"))
        return r
    print("site: %s records %d retired mod(s), on no list now; loading past them: %s"
          % (a.save, len(retired), ", ".join(retired)))
    with connect(120) as rb:
        return rb.call("rimworld/load_game", {"saveName": a.save, "ignoreModCompatibility": True})


def player_log_path():
    """-> RimWorld's Player.log, or None when this interpreter cannot see it (game_paths knows both spellings)."""
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from game_paths import PLAYER_LOG
        return PLAYER_LOG if os.path.isfile(PLAYER_LOG) else None
    except Exception:  # noqa: BLE001  no log is no evidence: the bridge phases still decide
        return None


def log_size():
    p = player_log_path()
    try:
        return os.path.getsize(p) if p else None
    except OSError:
        return None


def load_death(save, offset):
    """Player.log from byte `offset` (its size before load_game) -> 'Exception ... | <top frame>' when the load of `save`
    died there, else None. Only an exception AFTER that save's own load line counts: a game that was already up may
    have logged one of its own."""
    p = player_log_path()
    if p is None or offset is None:
        return None
    try:
        with open(p, "rb") as f:
            f.seek(offset)
            text = f.read().decode("utf-8", "replace")
    except OSError:
        return None
    i = text.find(LOAD_LINE % save)
    if i < 0:
        return None
    lines = text[i:].splitlines()
    for n, ln in enumerate(lines):
        if ln.startswith(DIED):
            frame = next((x.strip() for x in lines[n + 1:n + 6] if x.strip().startswith("at ")), "")
            return (ln.strip() + (" | " + frame if frame else ""))
    return None


def wait_loaded(rb, save, offset, budget_s, step_s=5):
    """-> (ok, why). Poll for a settled map (await_lifecycle.phase_of, settle=True), ending at once when the load died."""
    from await_lifecycle import phase_of
    t0, menu_from, phase, ui = time.time(), None, None, {}
    while True:
        time.sleep(step_s)
        phase, ui = phase_of(_lc_call(rb), settle=True)
        if phase == "map_ready":
            return True, "map_ready"
        waited = time.time() - t0
        died = load_death(save, offset)
        if died:
            return False, NO_LOAD % (save, "the load died after %.0fs; Player.log: %s" % (waited, died))
        if phase == "menu":
            menu_from = waited if menu_from is None else menu_from
            if waited - menu_from >= MENU_DEAD_S:
                return False, NO_LOAD % (save, "the game sat at the main menu %.0fs after load_game answered (read "
                                         "Player.log's FIRST exception after its load line)" % (waited - menu_from))
        else:
            menu_from = None
        if waited >= budget_s:
            return False, "%s did not reach Playing with a map in %ds (last phase %s: %s)" % (
                save, budget_s, phase, json.dumps(ui, default=str))


def on_a_map(rb):
    """True when a game is Playing with a map: then load_game's first Playing polls are the OLD map."""
    from await_lifecycle import phase_of
    return phase_of(_lc_call(rb))[0] == "map_ready"


def save_site(a):
    with connect(60) as rb:
        was_up = on_a_map(rb)
    offset = log_size()
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
    if isinstance(r, dict) and r.get("success") is False and not a.restage_with:
        r = load_past_retired(a, r)
    if not isinstance(r, dict) or r.get("success") is False:
        print("NOT READY: load_game %s refused: %s" % (a.save, str(r)))
        return NOT_READY
    with connect(60) as rb:
        if was_up:
            from await_lifecycle import await_leaving
            if not await_leaving(_lc_call(rb), "playing", deadline_s=MENU_DEAD_S, poll_s=1.0,
                                 clock=_lc_clock, sleep=_lc_sleep):
                print("NOT READY: load_game %s answered, but the old game never left Playing in %ds"
                      % (a.save, MENU_DEAD_S))
                return NOT_READY
        ok, why = wait_loaded(rb, a.save, offset, a.budget)
        if not ok:
            print("NOT READY: " + why)
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
            info = {"error": str(e)}
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
            print("quicktest call ended: %s" % str(e))
    with connect(60) as rb:
        if not wait_ready(rb, a.budget):
            print("NOT READY: the quicktest after the menu dwell did not reach Playing with a map in %ds" % a.budget)
            return NOT_READY
        info = rb.call("jawa/map_info", {})
        print("READY: %ds at the main menu, then a quicktest map %s" % (a.menu_dwell, info.get("mapBiome")))
        return READY


def game_site(a):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from await_lifecycle import phase_of
    with connect(120) as rb:
        phase, ui = phase_of(_lc_call(rb))
        if phase == "loading":          # a load in flight finishes before it is judged: never start a game over it
            ok = wait_ready(rb, a.budget)
            phase, ui = phase_of(_lc_call(rb)) if ok else (phase, ui)
        if phase == "map_ready":
            print("READY: a game with a map is up (left as it is)")
            return READY
        if phase not in ("menu", "missing_map"):
            print("NOT READY: the game reads %s (%s); no quicktest started" % (phase, str(ui)))
            return NOT_READY
        print("site: no map (%s); starting a quicktest" % phase)
    with connect(900) as rb:
        try:
            rb.call("rimworld/start_debug_game_ready", {"timeoutMs": 900000, "readiness": "mapData", "pauseIfNeeded": True})
        except Exception as e:      # noqa: BLE001  the connection may drop while the map generates
            print("quicktest call ended: %s" % str(e))
    with connect(60) as rb:
        if not wait_ready(rb, a.budget):
            print("NOT READY: the quicktest did not reach Playing with a map in %ds" % a.budget)
            return NOT_READY
        info = rb.call("jawa/map_info", {})
        print("READY: a quicktest map %s" % info.get("mapBiome"))
        return READY

POWERED_DEF = "SolarGenerator"      # vanilla Core, 4x4, CompPowerPlantSolar: a CompPowerTrader with no stuff to pick


def powered_things(rb):
    r = rb.call("jawa/list_things", {"group": "PowerTrader", "limit": 50})
    if not isinstance(r, dict) or r.get("success") is False:
        raise RuntimeError("list_things group=PowerTrader failed: %s" % str(r))
    return r.get("things") or []


def ensure_powered(rb):
    """--powered: READY when the map holds a PowerTrader building (one is spawned when none is), else NOT_READY."""
    have = powered_things(rb)
    if have:
        print("site: %d powered building(s) already on the map (left as they are)" % len(have))
        return READY
    info = rb.call("jawa/map_info", {}) or {}
    sx, sz = int(info.get("sizeX") or 0), int(info.get("sizeZ") or 0)
    if sx < 20 or sz < 20:
        print("NOT READY: --powered: map_info gave no usable size (%s)" % str(info))
        return NOT_READY
    tried = []
    for dx, dz in ((0, 0), (8, 0), (-8, 0), (0, 8), (0, -8), (8, 8), (-8, -8), (8, -8), (-8, 8)):
        x, z = sx // 2 + dx, sz // 2 + dz
        r = rb.call("rimworld/spawn_thing", {"defName": POWERED_DEF, "x": x, "z": z})
        tried.append("(%d,%d) %s" % (x, z, str((r or {}).get("message") or (r or {}).get("success"))[:60]))
        if isinstance(r, dict) and r.get("success") is not False:
            if powered_things(rb):
                print("site: spawned %s at (%d,%d) for --powered" % (POWERED_DEF, x, z))
                return READY
            print("NOT READY: --powered: %s at (%d,%d) answered %s but no PowerTrader reads back (one spawn, no more)"
                  % (POWERED_DEF, x, z, str(r)))
            return NOT_READY
    print("NOT READY: --powered: no %s read back as PowerTrader after %d tries: %s"
          % (POWERED_DEF, len(tried), "; ".join(tried)))
    return NOT_READY


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--biome", help="BiomeDef the current map must be")
    ap.add_argument("--not-biome", action="append", default=[], help="a BiomeDef the map must not be (repeatable)")
    ap.add_argument("--temperature", type=float)
    ap.add_argument("--save", help="a save name to load (no .rws)")
    ap.add_argument("--menu-dwell", type=int, help="seconds at the main menu, then a quicktest map back")
    ap.add_argument("--game", action="store_true", help="a game with any map: start a quicktest only when none is up")
    ap.add_argument("--powered", action="store_true",
                    help="then the map holds a PowerTrader building: a SolarGenerator is spawned when none is")
    ap.add_argument("--max-ticks", type=int, default=120000)
    ap.add_argument("--budget", type=int, default=300)
    ap.add_argument("--needs", action="append", default=[], help="a packageId the RUNNING load must hold (repeatable)")
    ap.add_argument("--without", action="append", default=[], help="a packageId it must not hold (repeatable)")
    ap.add_argument("--ignore-missing-mods", action="store_true",
                    help="--save: load even though the save records mods the running list lacks (ignoreModCompatibility)")
    ap.add_argument("--restage-with", metavar="MOD",
                    help="--save of a %s* fixture: when the load is refused, re-make the save on the running list with "
                         "src/RimMandrake/<MOD>/stage_proof_site.py, then load it" % RESTAGE_PREFIX)
    ap.add_argument("--stage-with", metavar="MOD",
                    help="then src/RimMandrake/<MOD>/stage_proof_site.py builds its scene in the running game; nothing is saved")
    ap.add_argument("--max-seconds", type=int, default=900, help="--stage-with: the stager's limit (relentless_live adds 120 s)")
    a = ap.parse_args(argv)
    if a.stage_with and not stager_path(a.stage_with):
        ap.error("--stage-with %s: no src/RimMandrake/%s/stage_proof_site.py" % (a.stage_with, a.stage_with))
    if a.stage_with and a.menu_dwell is not None:
        ap.error("--stage-with needs a map: not with --menu-dwell")
    if (a.ignore_missing_mods or a.restage_with) and not a.save:
        ap.error("--ignore-missing-mods and --restage-with need --save")
    if a.restage_with and not a.save.startswith(RESTAGE_PREFIX):
        ap.error("--restage-with re-makes only a %s* proof fixture, never %s" % (RESTAGE_PREFIX, a.save))
    if a.restage_with and not stager_path(a.restage_with):
        ap.error("--restage-with %s: no src/RimMandrake/%s/stage_proof_site.py" % (a.restage_with, a.restage_with))
    if sum((bool(a.save), bool(a.biome or a.not_biome), a.menu_dwell is not None, a.game)) != 1:
        ap.error("give one of --save, --biome / --not-biome, --menu-dwell, --game")
    if a.powered and a.menu_dwell is not None:
        ap.error("--powered needs a map: not with --menu-dwell")
    if a.menu_dwell is not None and not 1 <= a.menu_dwell <= 300:
        ap.error("--menu-dwell is 1..300 seconds")
    try:
        gap = check_load(a)
        if gap is not None:
            return gap
        if a.menu_dwell is not None:
            return menu_site(a)
        if a.game:
            rc = game_site(a)
        else:
            rc = save_site(a) if a.save else biome_site(a)
        if rc == READY and a.powered:
            with connect(60) as rb:
                rc = ensure_powered(rb)
        if rc == READY and a.stage_with:
            rc, line = run_scene_stager(stager_path(a.stage_with), a.max_ticks, a.max_seconds)
            if rc != 0:
                print("NOT READY: the %s stager could not make its scene (exit %s): %s" % (a.stage_with, rc, line))
                return NOT_READY
        return rc
    except Exception as e:      # noqa: BLE001  any bridge failure is a site not made, never a verdict
        print("NOT READY: %s: %s" % (type(e).__name__, str(e)))
        return NOT_READY


if __name__ == "__main__":
    sys.exit(main())
