#!/usr/bin/env python3
"""stage_map.py - make the stage of a test game: the green room and one stage map, kept as a fixture save
(RIMMANDRAKE_BUILD_STAGE_MAP_CAST_ONLY_NO_BYSTANDERS; 05_build_design.md §Decision 7: the station fence).

    python3 src/RimMandrake/Utils/stage_map.py make <game> --kind settlement|pocket [--size 100] [--save NAME]
    python3 src/RimMandrake/Utils/stage_map.py census <game>
    python3 src/RimMandrake/Utils/stage_map.py register <game> --save NAME     (a colony map: the walk save is its own stage)

The green room is the map that the game holds when `make` starts (a quicktest colony when the game stands at the menu): it
keeps the free colonists that the engine needs. `make` adds the stage map, empties it (every pawn vanished, every destroyable
thing and roof cleared, one terrain of fertility 0 over every cell, fog lifted), makes it the current map, saves the game as
the fixture save and writes the stage file (scene_world.py stage_made) that gives `s.stage(station=dict(...))` its
allocator. Kinds: `settlement` an ordinary player settlement map on a flat world tile, with edges, a home status and
incident targets; `pocket` a pocket map from the game's own debug action "Generate Pocket Map" (no edge, no home, no
incident, a fixed outdoor temperature). `register` writes a `colony` stage file for a save that is already a colony.

Plants: the terrain has fertility 0, so the wild plant spawner finds no cell (WildPlantSpawner reads fertility). Wild
animals: the calm of a scene holds the wild spawner (jawa/quiet_site calm), and `census` names any pawn on the stage.
WSL runs the outer part (the driver lock: game_lock.py run); python.exe runs the part that talks to the game.
Exit 0 = done, 1 = the game refused a step (named), 2 = could not look (no bridge, no map, the lock is held)."""
import argparse
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
TERRAIN = "Granite_Rough"     # natural, fertility 0, takes heavy builds (RimSage: TerrainDef Granite_Rough)
POCKET_GENS = ("MetalHell", "Undercave", "Labyrinth")   # the first that the debug action lists is used
ITEM = "RIMMANDRAKE_BUILD_STAGE_MAP_CAST_ONLY_NO_BYSTANDERS"
MEAL_STACKS = 3               # stacks of 10 survival meals per colonist: about 15 days of food for a scene session


class Stop(Exception):
    def __init__(self, code, why):
        super().__init__(why)
        self.code, self.why = code, why


# ------------------------------------------------------------------ the outer part (WSL): the lock, then python.exe
def outer(argv):
    a = argv[:]
    if len(a) < 2 or a[0] not in ("make", "census", "register"):
        print(__doc__)
        return 2
    game = a[1]
    # A wsl.exe child of a Windows python gets each name in WSLENV that the parent did not set as "" (measured 2026-11-24):
    # RIMFLOW_DRIVER_LOCK="" then reads as "no lock path", and ArchBig's make could not take its lock. Drop such empty names.
    for k in [w.split("/")[0] for w in os.environ.get("WSLENV", "").split(":") if w]:
        if os.environ.get(k) == "":
            del os.environ[k]
    # budget: danger=a hung game_instance.py holds the make; evidence=none seen, a hang guard; longest=1s (one measured run, 2026-11-24)
    env = subprocess.run([sys.executable, os.path.join(HERE, "game_instance.py"), "env", game], capture_output=True, text=True, timeout=60)
    if env.returncode != 0:
        print("stage_map: no game %r: %s" % (game, env.stderr.strip() or env.stdout.strip()))
        return 2
    e = dict(os.environ)
    for ln in env.stdout.splitlines():
        if ln.startswith("export ") and "=" in ln:
            k, v = ln[7:].split("=", 1)
            e[k] = v
    e["PYTHONIOENCODING"] = "utf-8"
    e["WSLENV"] = e.get("WSLENV", "") + ":PYTHONIOENCODING"
    # budget: danger=a hung wslpath holds the make; evidence=none seen, a hang guard; longest=1s (one measured run, 2026-11-24)
    win = lambda p: subprocess.run(["wslpath", "-w", p], capture_output=True, text=True, timeout=60).stdout.strip()  # noqa: E731
    cmd = [sys.executable, os.path.join(REPO, "src", "RimMandrake", "rimflow", "game_lock.py"), "run", game,
           "--for", "%s: stage_map %s" % (ITEM, " ".join(a)), "--", "python.exe", win(os.path.abspath(__file__)), "--inner"] + a
    try:
        # budget: danger=a make whose game never answers holds the driver lock; evidence=none seen, a hang guard; longest=53s (prove_stage_map.py make pocket, 2026-11-24)
        return subprocess.run(cmd, env=e, stdin=subprocess.DEVNULL, timeout=1800).returncode
    except subprocess.TimeoutExpired:
        print("stage_map: COULD NOT FINISH: the make passed its 1800 s hang guard; the game is in an unknown state")
        return 2


# ------------------------------------------------------------------ the inner part (python.exe): the game
def connect():
    sys.path.insert(0, HERE)
    import rimbridge_client as rb
    h, p, tok = rb.resolve_endpoint()
    # budget: danger=a bridge call that never answers holds the make and its game; evidence=none seen, a hang guard; longest=8s (a save load, bridge split of prove_stage_map.py, 2026-11-24)
    c = rb.RimBridge(host=h, port=p, token=tok, timeout=600)
    c.connect()
    return c


def call(c, tool, **args):
    r = c.call(tool, args, check=False)
    return r if isinstance(r, dict) else {"success": False, "raw": str(r)[:300]}


def must(r, what):
    if r.get("success") is False or r.get("error"):
        raise Stop(1, "%s: %s" % (what, str(r.get("message") or r.get("error") or r)[:400]))
    return r


def maps(c):
    """-> [{mapId, tile, biome}] of the loaded maps (set_current_map lists them on a refusal)."""
    r = call(c, "jawa/set_current_map", mapId=-987654)
    ms = r.get("loadedMaps") or (r.get("details") or {}).get("loadedMaps")
    if not isinstance(ms, list):
        raise Stop(2, "the loaded maps could not be read: %s" % str(r)[:300])
    return ms


def current(c):
    mi = call(c, "jawa/map_info")
    if mi.get("success") is not True:
        raise Stop(2, "no current map: %s" % str(mi)[:300])
    return mi


def pawns_on(c, rect=None):
    r = call(c, "jawa/list_pawns", **({"rect": rect} if rect else {}))
    if r.get("success") is False or not isinstance(r.get("pawns"), list):
        raise Stop(2, "the pawns of the map could not be read: %s" % str(r)[:300])
    return r["pawns"]


def empty_map(c, sx, sz, say):
    """Vanish every pawn, clear every destroyable thing and roof, lay one terrain, lift the fog. -> the census after."""
    t0 = time.time()
    gone = 0
    for p in pawns_on(c):
        if isinstance(p, dict) and p.get("id"):
            must(call(c, "jawa/pawn_force_incapacitate", pawn=p["id"], action="vanish"), "vanish %s" % p["id"])
            gone += 1
    cl = must(call(c, "jawa/clear_area", rect="0,0,%d,%d" % (sx, sz), dryRun=False), "clear_area")
    te = must(call(c, "jawa/set_terrain_batch", ops="%s:0,0,%d,%d" % (TERRAIN, sx, sz)), "set_terrain_batch")
    fog = call(c, "jawa/set_fog", action="unfogAll")
    left = pawns_on(c)
    say("emptied: %d pawn(s) vanished, %s thing(s) cleared, terrain %s on %s cell(s) (read-back ok=%s), fog %s, %d pawn(s) left, %.1f s"
        % (gone, cl.get("destroyedCount"), TERRAIN, (te.get("readBack") or {}).get("rows"), (te.get("readBack") or {}).get("ok"),
           "lifted" if fog.get("success") is not False else "NOT lifted: %s" % str(fog)[:120], len(left), time.time() - t0))
    return left


def provision(c, say):
    """Feed the green room: MEALS survival meals beside each colonist, and each colonist's food need full. A quicktest colony
    has no food (measured 2026-11-24: a colonist was malnourished after 60,000 idle ticks), and a stage scene must not end
    in a hunger the stage made."""
    r = call(c, "jawa/pawn_census", faction="player")
    col = [p for p in r.get("pawns") or [] if p.get("isColonist")]
    if not col:
        raise Stop(2, "the green room's colonists could not be read: %s" % str(r)[:300])
    meals = 0
    for p in col:
        for dx in range(MEAL_STACKS):
            s = call(c, "rimworld/spawn_thing", defName="MealSurvivalPack", x=int(p["x"]) + dx, z=int(p["z"]) + 1, stackCount=10)
            meals += 10 if s.get("success") is not False else 0
        must(call(c, "jawa/pawn_need", pawn=p["id"], action="need", need="Food", level=1.0), "food need of %s" % p["id"])
    say("green room fed: %d meal(s) beside %d colonist(s), food need full" % (meals, len(col)))


def pick_tile(c, home):
    """A flat, settleable tile near the green room's, with no map on it."""
    taken = {m.get("tile") for m in maps(c)}
    for lo in range(home - 60, home - 2000, -60):
        r = call(c, "jawa/world_tile_get", range="%d-%d" % (max(0, lo), lo + 59), limit=60)
        flat = [t["tile"] for t in (r.get("tiles") or []) if t.get("hilliness") == "Flat" and t["tile"] not in taken]
        if not flat:
            continue
        s = call(c, "jawa/tile_settleable", tiles=",".join(str(t) for t in flat))
        for row in s.get("tiles") or s.get("rows") or []:
            if row.get("settleable") is True or row.get("ok") is True:
                return int(row.get("tile"))
    raise Stop(1, "no flat settleable tile was found below tile %d" % home)


def make(c, kind, size, save, say):
    sys.path.insert(0, HERE)
    import scene_stations as ST
    import scene_world
    st = call(c, "rimworld/get_game_info")
    if (st.get("state") or {}).get("programState") == "Playing" and len(maps(c)) != 1:
        say("the game holds %d maps: leaving it for the main menu (a test game is disposable)" % len(maps(c)))
        must(call(c, "rimworld/go_to_main_menu"), "go_to_main_menu")
        for _ in range(120):            # the menu comes in seconds; 120 polls of 1 s guard a menu that never comes
            st = call(c, "rimworld/get_game_info")
            if (st.get("state") or {}).get("programState") == "Entry":
                break
            time.sleep(1)
    if (st.get("state") or {}).get("programState") != "Playing":
        say("the game stands at %s: starting a quicktest for the green room" % (st.get("state") or {}).get("programState"))
        # budget: danger=a quicktest start that never answers holds the make; evidence=none seen, a hang guard; longest=8s (bridge split load, prove_stage_map.py, 2026-11-24)
        must(call(c, "rimworld/start_debug_game_ready", timeoutMs=280000, readiness="mapData", pauseIfNeeded=True), "quicktest")
        for _ in range(600):            # a quicktest is ready in about 90 s; 600 polls of 1 s guard a start that never ends
            s2 = (call(c, "rimworld/get_game_info").get("state") or {})
            if s2.get("programState") == "Playing" and s2.get("automationReady") is not False and not s2.get("longEventPending"):
                break
            time.sleep(1)
        else:
            raise Stop(1, "the quicktest did not reach Playing in 600 s: %s" % s2)
        call(c, "rimworld/pause_game", pause=True)
    green = current(c)
    if len(maps(c)) != 1:
        raise Stop(1, "the game holds %d maps; a stage is made from a game that holds only the green room" % len(maps(c)))
    colonists = [p for p in pawns_on(c) if isinstance(p, dict) and str(p.get("faction")).lower() in ("playercolony", "player", "ofplayer")]
    say("green room: map %s, tile %s, %s, %d colonist(s)" % (green.get("mapId"), green.get("tile"), green.get("mapBiome"), len(colonists)))
    provision(c, say)
    t0 = time.time()
    if kind == "settlement":
        tile = pick_tile(c, int(green["tile"]))
        g = must(call(c, "jawa/world_tile_map_generate", tile=tile, suggestedMapParent="Settlement", sizeX=size, sizeZ=size,
                      faction="Player"), "world_tile_map_generate")
        new = [m for m in maps(c) if m.get("tile") == tile]
        what = "settlement map on tile %d (%s)" % (tile, g.get("biome"))
    else:
        kids = call(c, "rimworld/list_debug_action_children", path="Actions\\Generate Pocket Map...")
        labels = [k.get("label") for k in kids.get("children") or []]
        gen = next((x for x in POCKET_GENS if x in labels), None)
        if gen is None:
            raise Stop(1, "the debug action lists no pocket generator of %s: %s" % (POCKET_GENS, labels[:20]))
        must(call(c, "rimworld/execute_debug_action", path="Actions\\Generate Pocket Map...\\" + gen), "Generate Pocket Map " + gen)
        new = [m for m in maps(c) if m.get("mapId") != green.get("mapId")]
        what = "pocket map (%s, 100x100: the debug action's size)" % gen
        size = None
    if len(new) != 1:
        raise Stop(1, "after the make, %d new map(s) are loaded: %s" % (len(new), maps(c)))
    must(call(c, "jawa/set_current_map", mapId=new[0]["mapId"]), "set_current_map")
    mi = current(c)
    if mi.get("mapId") != new[0]["mapId"]:       # a switch can reply success and not take (measured 2026-11-24): never empty the green room
        raise Stop(1, "the stage map %s did not become current (current: %s)" % (new[0]["mapId"], mi.get("mapId")))
    sx, sz = int(mi["sizeX"]), int(mi["sizeZ"])
    made_s = time.time() - t0
    say("made the %s: map %s, %dx%d, %.1f s" % (what, mi.get("mapId"), sx, sz, made_s))
    left = empty_map(c, sx, sz, say)
    if left:
        raise Stop(1, "the stage still holds %d pawn(s) after the empty: %s" % (len(left), left[:3]))
    must(call(c, "rimworld/pause_game", pause=True), "pause")
    must(call(c, "rimworld/save_game", saveName=save), "save_game")
    path = scene_world.RealWorld().stage_made(save, ST.Stage(save, kind, (sx, sz)).to_json())
    say("MADE %s stage %s: %dx%d, map %s current, green room map %s; make %.1f s, total %.1f s; stage file %s"
        % (kind, save, sx, sz, mi.get("mapId"), green.get("mapId"), made_s, time.time() - t0, path))
    return 0


def census(c, say):
    mi = current(c)
    ps = pawns_on(c)
    say("stage map %s (%sx%s): %d pawn(s)%s" % (mi.get("mapId"), mi.get("sizeX"), mi.get("sizeZ"), len(ps),
                                                 "".join("\n  %s %s %s at %s" % (p.get("id"), p.get("kind") or p.get("def"), p.get("faction"),
                                                                                p.get("position") or p.get("cell")) for p in ps[:40])))
    return 0


def register(c, save, say):
    sys.path.insert(0, HERE)
    import scene_stations as ST
    import scene_world
    mi = current(c)
    path = scene_world.RealWorld().stage_made(save, ST.Stage(save, "colony", (int(mi["sizeX"]), int(mi["sizeZ"]))).to_json())
    say("REGISTERED colony stage %s: %sx%s; stations on it are shared map; stage file %s" % (save, mi["sizeX"], mi["sizeZ"], path))
    return 0


def inner(argv):
    ap = argparse.ArgumentParser(prog="stage_map.py")
    ap.add_argument("verb", choices=("make", "census", "register"))
    ap.add_argument("game")
    ap.add_argument("--kind", choices=("settlement", "pocket"), default="settlement")
    ap.add_argument("--size", type=int, default=100)
    ap.add_argument("--save")
    a = ap.parse_args(argv)
    say = lambda s: print(s, flush=True)  # noqa: E731
    try:
        c = connect()
    except Exception as e:  # noqa: BLE001 - no bridge is could-not-look, named
        say("COULD NOT LOOK: no bridge: %s: %s" % (type(e).__name__, e))
        return 2
    try:
        if a.verb == "make":
            return make(c, a.kind, a.size, a.save or "RM_Stage_%s_%s" % (a.game, a.kind), say)
        if a.verb == "register":
            if not a.save:
                raise Stop(2, "register names the colony save: --save NAME")
            return register(c, a.save, say)
        return census(c, say)
    except Stop as e:
        say("%s: %s" % ("REFUSED" if e.code == 1 else "COULD NOT LOOK", e.why))
        return e.code


if __name__ == "__main__":
    if sys.argv[1:2] == ["--inner"]:
        sys.exit(inner(sys.argv[2:]))
    sys.exit(outer(sys.argv[1:]))
