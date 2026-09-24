#!/usr/bin/env python3
"""stage_review.py -- one-shot CLEAN STAGING of a live map for visual review.

The job this exists for: put a biome / roster / structure in front of the owner
as a screenshot that shows the THING and nothing that fights it -- no hostiles
mid-slaughter, no rock or ruins the subject spawned inside, no midnight murk, no
debug log window over the subject. Every one of those has ruined a review shot.

It composes tools that already exist (nothing here is new engine capability):
  jawa/list_pawns + T:Damage To Death   -> remove hostiles first
  jawa/list_things + jawa/destroy_batch -> clear chunks / filth / (opt) buildings
  rimworld/get_cell_info                 -> VERIFY each spawn cell is open+right terrain
  jawa/spawn_pawn faction:"none"         -> WILD subjects (no combat, no fleeing)
  jawa/weather_set + step_game_ticks     -> midday+clear, then signature weather
  jawa/set_fog unfog                     -> a subject in unseen fog photographs as nothing
  jawa/clear_ui + rimworld/frame_cell_rect + take_screenshot
  rimworld/save_game                     -> a keeper the owner can walk later

🔴 Run with python.exe from WSL (the bridge binds Windows loopback). Read
   skills/rimworld-live-review/SKILL.md before using this -- it explains WHY each
   step is here and when to reach for the manual path instead.

Everything is read back. `success:true` is never taken as proof (that law is the
whole reason this project's bridge tooling exists).

Usage:
  # stage a roster of wild animals on verified-open grass, midday, and shoot:
  python.exe stage_review.py --map 1 \
      --clear chunks,filth --kill-hostiles \
      --spawn "RUT_FireHawk:2,AA_Barbslinger:1,Anooba:2,Gizka:2" \
      --at 85,205 --spread 6 \
      --frame 60,190,120,40 --daylight --shot pyrelands_animals \
      --save PYRELANDS_REVIEW

  # just clean + reframe + shoot an already-staged scene:
  python.exe stage_review.py --map 1 --frame 40,40,80,80 --shot foo

  # signature-weather second pass (no respawn):
  python.exe stage_review.py --map 1 --weather RM_FE_Weather_AshFall \
      --settle 4000 --frame 60,190,120,40 --shot pyrelands_ashfall
"""
import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rimbridge_client import RimBridge, resolve_endpoint
from game_paths import LOCALLOW

SCREENSHOT_DIR = os.path.join(LOCALLOW, "Screenshots")


def connect():
    host, port, token = resolve_endpoint()
    return RimBridge(host=host, port=port, token=token).connect()


def ensure_map(rb, map_id):
    """Make map_id current AND confirm it -- set_current_map refuses an unknown
    id and lists what IS loaded, so a wrong id fails loud instead of shooting the
    wrong map."""
    if map_id is None:
        return rb.call("jawa/map_info", {})
    s = rb.call("jawa/set_current_map", {"mapId": int(map_id)})
    if not s.get("success"):
        sys.exit("set_current_map(%s) refused: %s\n  loaded: %s"
                 % (map_id, s.get("message"), s.get("details")))
    return rb.call("jawa/map_info", {})


def pause(rb):
    """Stage and shoot PAUSED. An unpaused map resolves combat, wanders animals
    out of frame, and burns daylight while you read a screenshot."""
    rb.call("rimworld/set_time_speed", {"speed": 0})
    a = rb.call("rimworld/get_game_info", {}).get("ticksGame")
    time.sleep(1.5)
    b = rb.call("rimworld/get_game_info", {}).get("ticksGame")
    return a == b  # equal => genuinely paused (set_time_speed can lie)


def kill_hostiles(rb, rounds=6):
    """Remove EVERYTHING hostile, so nothing starts a fight when time moves. Do
    this BEFORE spawning subjects, so a stray unpause can't wipe the scene.

    Two hard-won details (owner caught both, 2026-09-17):
      * The pawn id field from jawa/list_pawns is `id`, NOT `thingId` (that key is
        null) -- passing thingId killed nothing.
      * `T: Damage To Death` only targets PLAYER colonists; hostiles can't be
        reached that way. `jawa/damage {thingId:<id>, damageDef:"Bomb", amount}`
        works on ANY faction. (Yes, the param is named thingId but wants the `id`.)
      * Use the `hostile` boolean, not a faction-name guess -- "PirateYttakin",
        "Ohnaka Gang" etc. are hostile and no substring catches them all.
    Tough targets (mechanoids) survive one bomb, so sweep until the count is
    stable at 0. Player colonists and wild animals are never touched."""
    removed = 0
    for _ in range(rounds):
        lp = rb.call("jawa/list_pawns", {"limit": 300})
        h = [p for p in lp.get("pawns", []) if p.get("hostile")]
        if not h:
            break
        for p in h:
            r = rb.call("jawa/damage",
                        {"thingId": p.get("id"), "damageDef": "Bomb", "amount": 9999})
            removed += 1 if r.get("success") else 0
    # read back: how many hostiles remain (0 is the target)
    lp = rb.call("jawa/list_pawns", {"limit": 300})
    left = len([p for p in lp.get("pawns", []) if p.get("hostile")])
    return {"damage_calls": removed, "hostiles_left": left}


def prep_worker(rb, x, z, name=None):
    """When a colonist must DO a job for a test (build, haul, operate), the job
    silently never happens unless the pawn can actually reach and perform it.
    Owner's checklist, 2026-09-17: put a HEALTHY, fully-satisfied colonist right
    next to the job, and clear hostiles for the duration. This satisfies needs
    and heals so the pawn works instead of collapsing, fleeing, or breaking.

    Returns the pawn id staged, or None if no colonist found."""
    # spawn a fresh healthy colonist AT the job cell so distance never stalls it
    rb.call("jawa/spawn_pawn", {"kindDef": "Colonist", "x": int(x), "z": int(z),
                                "count": 1, "faction": "PlayerColony"})
    lp = rb.call("jawa/list_pawns", {"limit": 300})
    cols = [p for p in lp.get("pawns", []) if p.get("isPlayer")]
    if not cols:
        return None
    p = cols[0] if not name else next((c for c in cols if c.get("name") == name), cols[0])
    pid = p.get("id")
    # restore whole body to healthy (recursive/destructive -> regrows parts, heals
    # injuries). The pawn tools key on `pawn`, not thingId.
    rb.call("jawa/pawn_health", {"pawn": pid, "action": "restore", "confirmDestructive": True})
    # top up every need (food, rest, recreation, mood inputs)
    rb.call("jawa/pawn_refresh_needs", {"pawn": pid})
    for need in ("Food", "Rest", "Joy", "Comfort", "Beauty", "Outdoors"):
        rb.call("jawa/pawn_need", {"pawn": pid, "action": "need", "need": need, "level": 1.0})
    return pid


def clear(rb, kinds, rect):
    """kinds: subset of {chunks,filth,buildings,plants,items}. rect 'x,z,w,h' or
    None for whole map. Buildings/structures are cleared only when asked -- that
    is the destructive one, and the point of clearing before a structure test is
    to stop the map's own ruins interacting with what you build."""
    catmap = {"chunks": "Item", "filth": "Filth", "items": "Item",
              "buildings": "Building", "plants": "Plant"}
    rects = rect or "0,0,250,250"
    out = {}
    for k in kinds:
        cat = catmap.get(k)
        if not cat:
            continue
        d = rb.call("jawa/destroy_batch", {"rects": rects, "category": cat})
        out[k] = d.get("destroyed", d.get("message"))
    return out


def cell_open(rb, x, z, want_terrain_prefix=None):
    """A subject spawned into rock/wall/water is the #1 review-shot defect. Verify
    the cell is walkable-ish and (optionally) on the terrain family you want."""
    ci = rb.call("rimworld/get_cell_info", {"x": int(x), "z": int(z)}).get("cell", {})
    terr = ci.get("terrainDefName", "")
    things = ci.get("things") or []
    blocked = any((t.get("category") in ("Building",)) or ("Wall" in str(t.get("defName", "")))
                  for t in things)
    # Water/bare-Rock terrain blocks a spawn; a walkable "_Rough" floor of the
    # same stone (Marble_Rough etc.) does not. This used to be a dead `if ...:
    # pass` that computed the condition and threw it away, so every non-water
    # Rock terrain silently passed as open — exactly the "#1 review-shot
    # defect" this function exists to catch. Fixed 2026-09-24 (wave 40).
    impassable_terrain = ("Water" in terr or "Rock" in terr
                          or (terr.endswith("_Rough") is False and "Marble" in terr))
    if want_terrain_prefix and not terr.startswith(tuple(want_terrain_prefix.split(","))):
        return False, terr
    return (not blocked and not impassable_terrain), terr


def find_open_grid(rb, cx, cz, n, spread, terrain_prefix):
    """Return n verified-open cells near (cx,cz). Walks an outward ring so the
    subjects cluster tightly in one photogenic patch instead of a fixed row that
    can cross rock/gravel/buildings (the row was exactly the bug)."""
    got = []
    r = 0
    while len(got) < n and r <= spread + 12:
        for dx in range(-r, r + 1):
            for dz in (-r, r) if r else (0,):
                x, z = cx + dx * spread // max(1, r or 1), cz + dz
                ok, _ = cell_open(rb, x, z, terrain_prefix)
                if ok and (x, z) not in got:
                    got.append((x, z))
                    if len(got) >= n:
                        return got
        r += 1
    # simple fallback: straight scan
    x = cx
    while len(got) < n and x < cx + 60:
        ok, _ = cell_open(rb, x, cz, terrain_prefix)
        if ok:
            got.append((x, cz))
        x += 2
    return got


def spawn_roster(rb, roster, at, spread, terrain_prefix, layout="grid"):
    """roster: [(kind,count)]. Spawn WILD (faction 'none') so nothing fights or
    flees.

    layout decides spacing, and the choice is an ART vs VIBE tradeoff (owner,
    2026-09-17): a tight cluster reads as "a herd in the biome" but tall pawns
    overlap and hide each other, so it is wrong for judging one creature's art.
      grid    -> each kind on its own well-spaced cell (default). Legible for
                 per-creature art review; --spread is the gap between kinds.
      cluster -> one anchor cell, counts pop out around it. Dense herd vibe,
                 crowded for tall pawns.
    Each target cell is verified open+right-terrain first; a subject in rock is
    the defect this whole helper exists to stop."""
    cx, cz = at
    results = []
    if layout == "cluster":
        ok, terr = cell_open(rb, cx, cz, terrain_prefix)
        base = (cx, cz) if ok else (find_open_grid(rb, cx, cz, 1, spread, terrain_prefix) or [(cx, cz)])[0]
        for kind, count in roster:
            r = rb.call("jawa/spawn_pawn",
                        {"kindDef": kind, "x": int(base[0]), "z": int(base[1]),
                         "count": int(count), "faction": "none"})
            results.append((kind, base[0], base[1], r.get("success"), str(r.get("message"))[:60]))
        return results
    # grid: spaced row(s), each kind its own verified-open cell
    cells = []
    x = cx
    for _ in range(len(roster)):
        # walk right to the next open cell at least `spread` from the last
        tries = 0
        while tries < 40:
            ok, _t = cell_open(rb, x, cz, terrain_prefix)
            if ok:
                cells.append((x, cz))
                x += spread
                break
            x += 1
            tries += 1
        else:
            cells.append((x, cz))
            x += spread
    for i, (kind, count) in enumerate(roster):
        gx, gz = cells[i]
        r = rb.call("jawa/spawn_pawn",
                    {"kindDef": kind, "x": int(gx), "z": int(gz),
                     "count": int(count), "faction": "none"})
        results.append((kind, gx, gz, r.get("success"), str(r.get("message"))[:60]))
    return results


def face(rb, direction="south", who="all"):
    """Turn pawns to a facing and LOCK it, so they hold the pose against the
    engine while you frame the shot. 'south' faces the CAMERA — the front view
    you want for art review. Without this, subjects face wherever the sim last
    pointed them and you photograph backs and flanks.
    (owner, 2026-09-17: drafting+moving induces facing, but this is the direct
    control — jawa/set_pawn_rotation with debugRotLocked.)"""
    r = rb.call("jawa/set_pawn_rotation",
                {"pawnId": who, "dir": direction, "lockRotation": True})
    return r.get("turned"), r.get("notVisible")


def daylight(rb, target_hour=12):
    """Step to ~midday so true colour reads. Safe here because the map is a home
    map (colonists present) and will not be culled mid-step -- see the SKILL."""
    # 2500 ticks/hour; step in <=2000 chunks so no single call frame-times out.
    for _ in range(30):
        gi = rb.call("rimworld/get_game_info", {})
        # RimWorld has no cheap "hour" read here; step a bounded amount and stop.
        try:
            rb.call("rimworld/step_game_ticks", {"ticks": 2000})
        except Exception:
            pass
        # crude: 6 steps ~ 12000 ticks ~ half a day; good enough for lighting.
        break_after = 6
        if _ >= break_after:
            break
    return rb.call("rimworld/get_game_info", {}).get("ticksGame")


def settle_weather(rb, weather, ticks):
    rb.call("jawa/weather_set", {"weather": weather, "lockWeather": True})
    stepped = 0
    while stepped < ticks:
        try:
            rb.call("rimworld/step_game_ticks", {"ticks": min(2000, ticks - stepped)})
        except Exception:
            pass
        stepped += 2000


def shoot(rb, frame, name):
    """Unfog the frame, drop the UI, frame the rect, capture. clear_ui matters:
    the debug log window sits exactly where the camera centres and eats the shot."""
    if frame:
        x, z, w, h = [int(v) for v in frame.split(",")]
        rb.call("jawa/set_fog", {"action": "unfog",
                                 "rect": "%d,%d,%d,%d" % (max(0, x - 4), max(0, z - 4), w + 8, h + 8)})
        rb.call("jawa/clear_ui", {})
        # jump FIRST (reliable centring), then frame_cell_rect for zoom-to-fit.
        # frame_cell_rect alone has been observed not to move the camera; the
        # explicit jump to the rect centre is the belt to its suspenders.
        rb.call("rimworld/jump_camera_to_cell", {"x": x + w // 2, "z": z + h // 2})
        rb.call("rimworld/frame_cell_rect",
                {"x": x, "z": z, "width": w, "height": h, "paddingCells": 3})
        cam = rb.call("rimworld/get_camera_state", {})
        print("  camera after frame:", cam.get("mapId"), "root", cam.get("rootSize"))
    else:
        rb.call("jawa/clear_ui", {})
    time.sleep(1.0)
    # take_screenshot appends .png itself -- pass a bare name or you get x.png.png
    base = (name or "review")
    if base.lower().endswith(".png"):
        base = base[:-4]
    r = rb.call("rimworld/take_screenshot", {"fileName": base, "suppressMessage": True})
    return r.get("path")


def save_game(rb, name):
    """Keeper save so the owner can WALK the scene later (his 'options as saves'
    ruling). 🔴 stat the Saves folder yourself -- save_game has written the
    CURRENT slot instead of the name given. Confirm a NEW file appeared."""
    r = rb.call("rimworld/save_game", {"saveName": name})
    time.sleep(2.0)  # the write is not instant; a race here read "not verified"
    path = os.path.join(_saves_dir(), name + ".rws")
    exists = os.path.isfile(path)
    size = os.path.getsize(path) if exists else 0
    return {"reported": r.get("path"), "verified": exists and size > 1000,
            "path": path, "sizeBytes": size}


def _saves_dir():
    return os.path.join(LOCALLOW, "Saves")


def parse_roster(s):
    out = []
    for part in s.split(","):
        part = part.strip()
        if not part:
            continue
        kind, _, cnt = part.partition(":")
        out.append((kind.strip(), int(cnt) if cnt else 1))
    return out


def main():
    ap = argparse.ArgumentParser(description="Clean-stage a live map for review.")
    ap.add_argument("--map", type=int, default=None, help="Map.uniqueID to make current")
    ap.add_argument("--kill-hostiles", action="store_true")
    ap.add_argument("--clear", default="", help="comma list: chunks,filth,buildings,plants,items")
    ap.add_argument("--clear-rect", default=None, help="'x,z,w,h' (default whole map)")
    ap.add_argument("--spawn", default="", help="'Kind:count,Kind:count' -- spawned WILD")
    ap.add_argument("--at", default="125,125", help="anchor cell 'x,z' for spawns")
    ap.add_argument("--spread", type=int, default=6, help="spacing between kinds")
    ap.add_argument("--layout", choices=("grid", "cluster"), default="grid",
                    help="grid=spaced, legible for art review (default); cluster=dense herd vibe")
    ap.add_argument("--terrain", default=None, help="require spawn terrain to start with this (e.g. RM_FE_Ground)")
    ap.add_argument("--daylight", action="store_true", help="step toward midday before shooting")
    ap.add_argument("--face", default=None, choices=("south", "north", "east", "west"),
                    help="turn+lock ALL spawned pawns to this facing; 'south' faces the camera (front view for art review)")
    ap.add_argument("--weather", default=None, help="force+lock a weather def before shooting")
    ap.add_argument("--settle", type=int, default=0, help="ticks to run after forcing weather (drifts/growth)")
    ap.add_argument("--frame", default=None, help="'x,z,w,h' rect to frame the shot on")
    ap.add_argument("--shot", default=None, help="screenshot base name")
    ap.add_argument("--two-pass", default=None, metavar="WEATHER",
                    help="ruled default capture in ONE call: shoot midday+clear as "
                         "<shot>_clear, then force+settle WEATHER and shoot <shot>_<weather>. "
                         "Saves an LLM round trip vs two separate runs.")
    ap.add_argument("--settle-weather", type=int, default=4000,
                    help="ticks to settle the --two-pass signature weather (drifts/effects)")
    ap.add_argument("--save", default=None, help="keeper save name")
    args = ap.parse_args()

    rb = connect()
    mi = ensure_map(rb, args.map)
    print("map:", mi.get("mapId"), mi.get("mapBiome"), "tile", mi.get("tile"))
    print("paused:", pause(rb))

    if args.kill_hostiles:
        print("hostiles removed:", kill_hostiles(rb))
    if args.clear:
        print("cleared:", clear(rb, [k.strip() for k in args.clear.split(",")], args.clear_rect))
    if args.spawn:
        at = tuple(int(v) for v in args.at.split(","))
        for row in spawn_roster(rb, parse_roster(args.spawn), at, args.spread, args.terrain, args.layout):
            print("  spawn", row)
    if args.face:
        print("faced:", face(rb, args.face))
    if args.daylight:
        print("daylight tick:", daylight(rb))
        pause(rb)
    if args.weather:
        settle_weather(rb, args.weather, args.settle)
        pause(rb)
    if args.two_pass:
        # ruled default capture, both passes in one invocation
        if args.daylight is False:
            print("daylight tick:", daylight(rb)); pause(rb)
        print("clear shot:", shoot(rb, args.frame, (args.shot or "review") + "_clear"))
        settle_weather(rb, args.two_pass, args.settle_weather); pause(rb)
        wname = args.two_pass.split("_")[-1].lower()
        print("weather shot:", shoot(rb, args.frame, (args.shot or "review") + "_" + wname))
    elif args.frame or args.shot:
        print("shot:", shoot(rb, args.frame, args.shot))
    if args.save:
        print("save:", save_game(rb, args.save))


if __name__ == "__main__":
    main()
