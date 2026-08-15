#!/usr/bin/env python3
"""import_gravship.py - stamp an exported gravship onto the LIVE map.

WHY THIS EXISTS
===============
`jawa/import_gravship` sat in the [v2] backlog because the tidy version calls
`ShipSketchBuilder.BuildFromLayout` inside the companion — and a companion can
only be deployed with the game CLOSED, which is the one thing we never have when
someone wants to look at the ship. This does the same job from OUTSIDE, using
only tools that are already deployed:

    jawa/destroy_batch      clear the ground first
    jawa/set_terrain_batch  layer=foundation, then layer=top
    jawa/spawn_batch        the things, batched by (defName, stuff, rot)

⚠️ It is NOT the same as the engine's own import. A real Sketch spawn runs the
mod's Harmony hooks; this replays cells. Known differences are called out below.

ORDER IS NOT NEGOTIABLE
=======================
    1. destroy   2. foundation   3. terrain   4. things

🔴 Foundation can only be laid on BARE ground — a floor blocks it PERMANENTLY,
and the refusal is silent. That single trap is why destroy runs first and why
foundation precedes terrain. Getting this order wrong does not error; it leaves
a ship with no substructure and every substructure-needing building refusing to
be placed, hours later, for no visible reason.

BATCHING
========
`spawn_batch` takes ONE `stuff` and ONE `rot` per call, so things are grouped by
(defName, stuff, rot) — the tool's own description says to batch that way and it
is not a suggestion, it is the shape of the API. A 1,052-thing ship comes out as
a few dozen calls instead of 1,052.

USAGE
    python.exe src/RimMandrake/bridgetools/import_gravship.py <layout.xml> \
        [--origin X,Z] [--clear-margin N] [--dry-run] [--no-clear]

Default origin CENTRES the ship on the map.
"""

import argparse
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src" / "RimMandrake" / "Utils"))
CLIENT = REPO / "src" / "RimMandrake" / "Utils" / "rimbridge_client.py"

# python.exe, not python3 — the bridge binds Windows loopback and WSL2 is
# NAT-mode, so a WSL interpreter has no route. Network half of the
# per-script interpreter rule.
PY = "python.exe"

from gravship_layout import Layout  # noqa: E402


def call(tool, params, timeout=240):
    cmd = [PY, str(CLIENT), "--timeout", str(timeout - 40), "--call", tool,
           "--json", json.dumps(params), "--yes-i-know-this-is-live"]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True,
                             timeout=timeout, cwd=str(REPO)).stdout
    except subprocess.TimeoutExpired:
        return {"success": False, "message": "client timeout"}
    i = out.find("{")
    if i < 0:
        return {"success": False, "message": out.strip()[:200]}
    try:
        return json.loads(out[i:])
    except json.JSONDecodeError:
        return {"success": False, "message": "unparseable reply"}


def map_size():
    """Bounds by probing. get_cell_info refuses out-of-bounds, which is the
    only bounds oracle the bridge exposes."""
    lo, hi = 1, 1000
    while lo < hi:
        mid = (lo + hi + 1) // 2
        r = call("rimworld/get_cell_info", {"x": mid - 1, "z": mid - 1}, timeout=90)
        if r.get("success"):
            lo = mid
        else:
            hi = mid - 1
    return lo


def chunks(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("layout")
    ap.add_argument("--origin", default=None, help="X,Z of the layout's (0,0). Default: centred.")
    ap.add_argument("--clear-margin", type=int, default=2,
                    help="Extra cells cleared around the footprint.")
    ap.add_argument("--no-clear", action="store_true")
    ap.add_argument("--wipe-map", action="store_true",
                    help="Strip the WHOLE map first: roofs, rock, plants, items, "
                         "buildings, filth, and every pawn. Leaves bare ground.")
    ap.add_argument("--terrain-only", action="store_true",
                    help="Lay foundation and terrain, spawn nothing. Repair pass "
                         "for a run whose floors came out short.")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--ops-per-call", type=int, default=220)
    args = ap.parse_args()

    lay = Layout.load(args.layout)
    print(f"layout {lay.width}x{lay.height} from {args.layout}")

    if args.origin:
        ox, oz = (int(v) for v in args.origin.split(","))
        size = map_size() if not args.dry_run else 250
    else:
        size = map_size() if not args.dry_run else 250
        ox = (size - lay.width) // 2
        oz = (size - lay.height) // 2
    print(f"map {size}x{size}; origin ({ox},{oz}) "
          f"=> footprint x{ox}..{ox + lay.width - 1} z{oz}..{oz + lay.height - 1}")

    if ox < 0 or oz < 0 or ox + lay.width > size or oz + lay.height > size:
        sys.exit("REFUSING: the ship does not fit on this map at that origin. "
                 "Nothing has been touched.")

    # ---- collect ------------------------------------------------------
    foundation = defaultdict(list)   # def -> ["x,z"]
    terrain = defaultdict(list)
    things = defaultdict(list)       # (def, stuff, rot) -> ["x,z"]

    for z in range(lay.height):
        for x in range(lay.width):
            c = lay.cell(x, z)
            if c is None or c.empty():
                continue
            wx, wz = ox + x, oz + z
            if c.foundationDef:
                foundation[c.foundationDef].append(f"{wx},{wz}")
            if c.terrainDef:
                terrain[c.terrainDef].append(f"{wx},{wz}")
            for t in (c.things or []):
                things[(t.defName, t.stuffDef, t.rot or 0)].append(f"{wx},{wz}")

    nf = sum(len(v) for v in foundation.values())
    nt = sum(len(v) for v in terrain.values())
    nth = sum(len(v) for v in things.values())
    print(f"collected: foundation {nf}, terrain {nt}, things {nth} "
          f"in {len(things)} (def,stuff,rot) groups")

    if args.dry_run:
        for (d, s, r), cells in sorted(things.items(), key=lambda kv: -len(kv[1]))[:15]:
            print(f"   {d:36s} stuff={s or '-':8s} rot={r}  x{len(cells)}")
        print("dry run - nothing sent")
        return

    # ---- 0. optional whole-map wipe -----------------------------------
    # Order here is its own small trap: ROOFS FIRST. Destroying the rock
    # that holds a mountain roof does not remove the roof — it leaves a
    # floating overhead that still blocks light, weather and drop pods, and
    # nothing about the map's appearance says so.
    if args.wipe_map:
        BAND = 25  # rows per call; the whole map in one op string is a livelock risk
        print(f"wipe: stripping roofs over {size}x{size}...")
        cleared = 0
        for z0 in range(0, size, BAND):
            h = min(BAND, size - z0)
            r = call("jawa/set_roof_batch",
                     {"ops": f"None:0,{z0},{size},{h}", "refresh": False}, timeout=300)
            cleared += r.get("cellsChanged", 0)
        print(f"wipe: roofs removed from {cleared} cell(s)")

        print("wipe: destroying rock, plants, items, buildings, filth...")
        destroyed = 0
        for z0 in range(0, size, BAND):
            h = min(BAND, size - z0)
            r = call("jawa/destroy_batch",
                     {"rects": f"0,{z0},{size},{h}", "categories": "All"}, timeout=300)
            destroyed += r.get("destroyed", 0) or 0
        print(f"wipe: destroyed {destroyed} thing(s)")

        # 🔴 destroy_batch NEVER destroys pawns, by design — killing a
        # colonist by fat-fingering a rect is not something it will make
        # possible. So pawns need an explicit, deliberate pass, which is
        # exactly the friction that guard exists to create.
        pawns = call("jawa/list_pawns", {}, timeout=180)
        ids = [p.get("id") for p in (pawns.get("pawns") or []) if p.get("id")]
        print(f"wipe: {len(ids)} pawn(s) to remove")
        killed = 0
        for pid in ids:
            # ⚠️ `damageDef`, NOT `damage` — an unknown parameter name is
            # dropped silently before the tool runs, so the wrong spelling
            # reports success and does nothing. And `allowColonists` is a
            # deliberate safety rail that must be switched off on purpose.
            r = call("jawa/damage",
                     {"thingId": pid, "damageDef": "Bomb", "amount": 9999,
                      "allowColonists": True}, timeout=120)
            if r.get("success"):
                killed += 1
        print(f"wipe: {killed}/{len(ids)} pawn(s) removed")
        # Corpses are Items; sweep once more so the map is genuinely bare.
        for z0 in range(0, size, BAND):
            h = min(BAND, size - z0)
            call("jawa/destroy_batch",
                 {"rects": f"0,{z0},{size},{h}", "categories": "All"}, timeout=300)
        left = call("jawa/list_pawns", {}, timeout=180)
        print(f"wipe: read-back -> {left.get('message')}")

    # ---- 1. clear -----------------------------------------------------
    # 🔴 Buildings and items are cleared; PAWNS ARE NOT — 'All' would be a
    # trivial way to kill colonists standing on the site, and destroy_batch
    # has no undo.
    if not args.no_clear:
        m = args.clear_margin
        rect = f"{ox - m},{oz - m},{lay.width + 2 * m},{lay.height + 2 * m}"
        r = call("jawa/destroy_batch",
                 {"rects": rect, "categories": "Plant,Item,Filth,Building"}, timeout=300)
        print(f"clear: {r.get('message')}")
        if not r.get("success"):
            sys.exit("clear failed - stopping before foundation")

    # ---- 2. foundation, then 3. terrain -------------------------------
    # 🔴 DO NOT BREAK ON success:false HERE, and this cost a whole run.
    # set_terrain_batch returns success:false when ANY cell fails to read
    # back — but it still applied every op in the call. Treating that as
    # fatal aborted after the first 220-cell batch and produced a ship with
    # 1,052 objects standing on 220 cells of substructure.
    # ⇒ a partial-verification warning is a WARNING. Keep going, count what
    #   actually changed, and report the shortfall at the end.
    for layer, table in (("foundation", foundation), ("top", terrain)):
        for tdef, cells in table.items():
            done = warned = 0
            for batch in chunks(cells, args.ops_per_call):
                ops = ";".join(f"{tdef}:{c},1,1" for c in batch)
                r = call("jawa/set_terrain_batch",
                         {"ops": ops, "layer": layer, "refresh": False}, timeout=300)
                done += r.get("cellsChanged", 0)
                if not r.get("success"):
                    warned += 1
            print(f"{layer}: {tdef} -> {done}/{len(cells)} cells changed"
                  + (f"  ({warned} batch(es) reported a read-back warning)" if warned else ""))

    # ---- 4. things ----------------------------------------------------
    if args.terrain_only:
        print("terrain-only: skipping things")
        call("jawa/refresh_rect",
             {"rect": f"{ox},{oz},{lay.width},{lay.height}"}, timeout=120)
        return

    placed = failed = 0
    for (d, s, rot), cells in sorted(things.items(), key=lambda kv: -len(kv[1])):
        for batch in chunks(cells, args.ops_per_call):
            p = {"ops": ";".join(f"{d}:{c},1" for c in batch), "rot": rot}
            if s:
                p["stuff"] = s
            r = call("jawa/spawn_batch", p, timeout=300)
            placed += r.get("spawned", 0)
            failed += r.get("failed", 0)
            if not r.get("success"):
                print(f"  !! {d} stuff={s} rot={rot}: {str(r.get('message'))[:140]}")
    print(f"things: {placed} spawned, {failed} failed (of {nth})")

    # One refresh at the end rather than per call.
    call("jawa/refresh_rect",
         {"rect": f"{ox},{oz},{lay.width},{lay.height}"}, timeout=120)

    # 🔴 Assert on a READ-BACK, never on the spawn calls' own success.
    check = call("jawa/list_things",
                 {"defName": "GravshipHull",
                  "rect": f"{ox},{oz},{lay.width},{lay.height}"}, timeout=180)
    print(f"read-back: {check.get('message')}")


if __name__ == "__main__":
    main()
