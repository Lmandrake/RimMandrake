#!/usr/bin/env python3
"""Stage a naked-races grid: one pawn per XenotypeDef, stripped, facing south.

This is the capture the owner ordered for XENOTYPE_CANON_CORRECTION_1, verbatim
(2026-09-17): *"generate an in-game grid of those naked races facing south as a
screenshot"* -- the instrument for judging a skin-colour pass, and again later for
head shapes.

🔴 RUN IT WITH `python.exe`, NOT `python3`. The bridge binds Windows loopback, so
from WSL only the Windows interpreter can reach it.

Why a script and not hand-driven bridge calls: this is ~60 calls. Each one issued
by a model is a slow round trip; the bridge answers Python in milliseconds. Per
skills/rimworld-live-review, the sequence goes in here and the model spends its
turn LOOKING at the result.

WHAT IT DOES, in the order the traps demand
    1. pause, and VERIFY the pause by reading ticksGame twice -- set_time_speed
       can report a speed and leave the game running;
    2. clear hostiles BEFORE spawning, or a Crashlanded quicktest's raiders kill
       the subjects between two calls;
    3. place each xenotype on a cell VERIFIED open and walkable, never on a fixed
       row that can cross rock or water -- a subject drawn inside rock is the
       number-one review defect;
    4. STRIP apparel, because a clothed pawn shows no skin and this is a skin
       review;
    5. remove every stray pawn in the frame, name each subject by its RACE, and
       DRAFT them -- drafted pawns hold still and face south (toward the camera);
       a rotation lock froze mid-walk facings and the 2026-10-06 grid faced away;
       a standard human (Baseliner) stands first, for comparison;
    6. unfog, clear the UI, frame the rect, shoot.

⚠️ The screenshot is a CACHE, not an observation. Nobody has reviewed anything
until a human or the model has actually looked at the PNG.

Usage:
    python.exe src/RimMandrake/Utils/stage_xenotype_grid.py --shot xeno_grid
    python.exe ... --at 125,125 --spread 7 --cols 5 --dry-run
"""

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rimbridge_client as rc  # noqa: E402

# Windows' console codec is cp1252 and raises UnicodeEncodeError on the emoji this
# repo uses throughout -- which kills the run AFTER the live writes have happened,
# the worst possible place to die. Force UTF-8 on both streams.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                  # noqa: BLE001
        pass

# The thirteen species of the appearance pass. Order is the grid's reading order,
# so keep it stable: the owner reads the shot against a key printed by this script.
DEFAULT_XENOTYPES = [
    "Baseliner",                       # a standard human, for scale and colour (owner 2026-10-06)
    "RSW_RimMandrakeIthorian",
    "RSW_RimMandrakeBith",
    "RSW_RimMandrakeZygerrian",
    "RSW_RimMandrakeChadraFan",
    "RSW_RimMandrakeAbednedo",
    "RSW_RimMandrakeEwok",
    "RSW_RimMandrakeLasat",
    "RSW_RimMandrakeOrtolan",
    "RSW_RimMandrakeMimbanese",
    "RSW_RimMandrakeUgnaught",
    "RSW_RimMandrakeChagrian",
    "RSW_RimMandrakeNelvaanian",
    "RSW_RimMandrakeUmbaran",
]


def ok(res):
    """True when the bridge says the call actually worked.

    🔑 `success` is nested differently across tool families and a missing key
    must NOT read as success -- that is how a silent failure becomes a green log.
    """
    if not isinstance(res, dict):
        return False
    if "success" in res:
        return bool(res["success"])
    return False


def race_label(xeno):
    """The name the owner RECOGNISES -- the race, never the pawn's random name.

    Owner, 2026-10-06: *"you should have labeled each of them by the Race I'm supposed
    to recognize, not by random names."*
    """
    if xeno == "Baseliner":
        return "Human"
    name = xeno.replace("RSW_RimMandrake", "")
    return {"ChadraFan": "Chadra-Fan"}.get(name, name)


class Stage(object):
    def __init__(self, bridge, verbose=True):
        self.b = bridge
        self.verbose = verbose
        self.notes = []

    def say(self, line):
        self.notes.append(line)
        if self.verbose:
            print(line)
            sys.stdout.flush()

    def call(self, tool, params=None, check=True):
        try:
            return self.b.call(tool, params or {}, check=check)
        except Exception as exc:                      # noqa: BLE001
            return {"success": False, "message": "%s: %s" % (type(exc).__name__, exc)}

    # --- 1. pause, and prove it ------------------------------------------
    def pause(self):
        self.call("rimworld/set_time_speed", {"speed": 0})
        t1 = self.call("jawa/map_info", {}).get("ticksGame")
        time.sleep(1.2)
        t2 = self.call("jawa/map_info", {}).get("ticksGame")
        held = (t1 is not None and t1 == t2)
        self.say("pause: ticks %s -> %s  %s" % (t1, t2, "HELD" if held else "STILL RUNNING"))
        return held

    # --- 2. hostiles out before anything is spawned -----------------------
    def kill_hostiles(self, sweeps=3):
        total = 0
        for n in range(sweeps):
            res = self.call("jawa/list_pawns", {})
            pawns = res.get("pawns") or []
            # Select by the hostile BOOLEAN, never a faction-name guess -- no
            # substring catches Pirate and PirateYttakin and a named gang.
            hostiles = [p for p in pawns if p.get("hostile")]
            if not hostiles:
                self.say("hostiles: 0 after %d sweep(s)" % n)
                return total
            for p in hostiles:
                # The id field is `id`; `thingId` comes back null. The damage
                # tool's param is CALLED thingId but wants the `id`.
                pid = p.get("id")
                if pid is None:
                    continue
                self.call("jawa/damage",
                          {"thingId": pid, "damageDef": "Bomb", "amount": 9999})
                total += 1
        left = [p for p in (self.call("jawa/list_pawns", {}).get("pawns") or [])
                if p.get("hostile")]
        self.say("hostiles: bombed %d, %d still standing" % (total, len(left)))
        return total

    # --- 3. cells that are actually open ---------------------------------
    def open_cells(self, x0, z0, w, h):
        """Set of open (x,z) in a rect, from ONE batch call.

        🔴 The tool is `rimworld/get_cells_info` -- NOT `jawa/get_cell_info`, which
        does not exist. A call to a missing tool returns an error, every cell read
        as blocked, and the grid silently placed nobody. The batch form caps at
        1024 cells, so the rect is walked in bands.
        """
        openc = set()
        band = max(1, 1024 // max(1, w))
        z = z0
        while z < z0 + h:
            hh = min(band, z0 + h - z)
            res = self.call("rimworld/get_cells_info",
                            {"x": x0, "z": z, "width": w, "height": hh})
            for c in (res.get("cells") or []):
                if c.get("walkable") is False:
                    continue
                terr = (c.get("terrain") or c.get("terrainDef") or "")
                if any(k in terr for k in ("Water", "Marsh", "Lake", "Ocean")):
                    continue
                blocked = False
                for t in (c.get("things") or []):
                    d = (t.get("defName") or "") + (t.get("className") or "")
                    if any(k in d for k in ("Wall", "Rock", "Mineable", "Building",
                                            "Tree", "Door")):
                        blocked = True
                        break
                if not blocked:
                    openc.add((c.get("x"), c.get("z")))
            z += hh
        return openc

    def grid_cells(self, cx, cz, count, spread, cols):
        """`count` verified-open cells on a grid, nudging off any blocked one."""
        rows = (count + cols - 1) // cols
        x0 = cx - (cols - 1) * spread // 2
        z0 = cz + (rows - 1) * spread // 2
        pad = 4
        rx = x0 - pad
        rz = z0 - (rows - 1) * spread - pad
        rw = (cols - 1) * spread + 2 * pad + 1
        rh = (rows - 1) * spread + 2 * pad + 1
        openc = self.open_cells(rx, rz, rw, rh)
        self.say("open cells in staging rect: %d of %d" % (len(openc), rw * rh))

        cells, used = [], set()
        for k in range(count):
            bx = x0 + (k % cols) * spread
            bz = z0 - (k // cols) * spread
            placed = None
            for dx, dz in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1),
                           (-1, -1), (2, 0), (-2, 0), (0, 2), (0, -2),
                           (2, 2), (-2, -2), (3, 0), (-3, 0)):
                c = (bx + dx, bz + dz)
                if c in openc and c not in used:
                    placed = c
                    used.add(c)
                    break
            cells.append(placed)     # None is recorded as a hole, never hidden
        return cells


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--at", default="125,125", help="grid centre cell x,z")
    ap.add_argument("--spread", type=int, default=9, help="cells between subjects")
    ap.add_argument("--cols", type=int, default=5)
    ap.add_argument("--shot", default="xeno_grid", help="screenshot name (no .png)")
    ap.add_argument("--kind", default="Colonist", help="PawnKindDef to carry the xenotype")
    ap.add_argument("--xenotypes", default="", help="comma list; default is the 13")
    ap.add_argument("--per", type=int, default=3,
                    help="pawns per race, side by side (skill §8c: one pawn is one skin roll)")
    ap.add_argument("--no-strip", action="store_true",
                    help="keep apparel (default strips it -- this is a SKIN review)")
    ap.add_argument("--dry-run", action="store_true", help="plan only, no writes")
    args = ap.parse_args()

    cx, cz = (int(v) for v in args.at.split(","))
    xenos = [x for x in (args.xenotypes.split(",") if args.xenotypes
                         else DEFAULT_XENOTYPES) if x.strip()]

    host, port, token = rc.resolve_endpoint()
    with rc.RimBridge(host=host, port=port, token=token) as b:
        st = Stage(b)

        info = st.call("jawa/map_info", {})
        if not ok(info):
            print("NO MAP: %s" % info.get("message"))
            return 2
        st.say("map %s  %sx%s  %s" % (info.get("mapId"), info.get("sizeX"),
                                      info.get("sizeZ"), info.get("mapBiome")))

        st.pause()
        st.kill_hostiles()

        cells = st.grid_cells(cx, cz, len(xenos), args.spread, args.cols)
        holes = [x for x, c in zip(xenos, cells) if c is None]
        if holes:
            st.say("⚠️ no open cell found for: %s" % ", ".join(holes))

        print("\n--- GRID KEY (reading order, left->right, top->bottom) ---")
        for x, c in zip(xenos, cells):
            print("  %-30s %s" % (x.replace("RSW_RimMandrake", ""),
                                  ("%d,%d" % c) if c else "NO CELL"))
        print("")

        if args.dry_run:
            st.say("dry run: nothing written")
            return 0

        # Every pawn already on the map is NOT a subject. Record them now so the grid
        # can be cleared of strays after spawning (owner, 2026-10-06: "there are at
        # least two or three individuals not part of this set that should have been
        # removed first").
        before = {p.get("id") for p in
                  (st.call("jawa/list_pawns", {}).get("pawns") or [])}

        spawned = []
        for xeno, cell in zip(xenos, cells):
            if cell is None:
                continue
            x, z = cell
            # §8c: one pawn is one random skin roll, not the species. `--per` copies
            # stand side by side, 2 cells apart, under one race label.
            for k in range(args.per):
                dx = (k - (args.per - 1) // 2) * 2
                res = st.call("jawa/spawn_pawn", {
                    "kindDef": args.kind, "x": x + dx, "z": z,
                    "faction": "player", "count": 1, "xenotype": xeno})
                if not ok(res):
                    st.say("SPAWN FAILED %s #%d: %s" % (xeno, k, res.get("message")))
                    continue
                spawned.append((xeno, (x + dx, z)))

        st.say("spawned %d of %d" % (len(spawned), len(xenos)))

        # Ours = whatever is new since `before`. Matching on xenotype alone misses the
        # Baseliner (it reads null) and catches any stray that shares a race.
        pawns = st.call("jawa/list_pawns", {}).get("pawns") or []
        mine = [p for p in pawns if p.get("id") not in before]
        st.say("verified on map: %d new pawns" % len(mine))

        rows = (len(xenos) + args.cols - 1) // args.cols
        rw = (args.cols + 1) * args.spread
        rh = (rows + 1) * args.spread
        rx, rz = cx - rw // 2, cz - rh // 2

        # Strays inside the shot: bomb them, then clear their corpses and our
        # subjects' stripped apparel with one Item sweep below.
        mine_ids = {p.get("id") for p in mine}
        strays = [p for p in pawns if p.get("id") not in mine_ids and not p.get("dead")
                  and p.get("x") is not None
                  and rx - 3 <= p["x"] < rx + rw + 3 and rz - 3 <= p["z"] < rz + rh + 3]
        for p in strays:
            st.call("jawa/damage", {"thingId": p.get("id"), "damageDef": "Bomb",
                                    "amount": 9999})
        st.say("strays removed from the frame: %d" % len(strays))

        label_ops, labelled = [], set()
        for p in mine:
            pid = p.get("id")
            if pid is None:
                continue
            xeno = p.get("xenotype") or "Baseliner"
            label = race_label(xeno)
            if not args.no_strip:
                st.call("jawa/pawn_gear",
                        {"pawn": str(pid), "action": "clear", "clearWhat": "apparel"})
            st.call("jawa/set_pawn_identity", {"pawn": str(pid), "single": label})
            # DRAFTED, not rotation-locked: a drafted pawn stands still AND the engine
            # turns it to South (toward the camera) every tick. The old lock froze
            # whatever facing a pawn had mid-walk -- the 2026-10-06 grid faced AWAY.
            st.call("jawa/set_draft", {"pawnId": str(pid), "drafted": True})
            if label not in labelled:
                labelled.add(label)
                cell = dict(zip(xenos, cells)).get(xeno if xeno in xenos else "Baseliner")
                lx, lz = cell if cell else (p["x"], p["z"])
                label_ops.append("%d|%d|%s" % (lx, lz + 2, label))

        st.call("jawa/destroy_batch", {"rects": "%d,%d,%d,%d" % (rx - 3, rz - 3, rw + 6, rh + 6),
                                       "categories": "Item"})
        st.call("jawa/review_label", {"action": "clear", "tag": "xeno_grid"})
        st.call("jawa/review_label", {"action": "add", "tag": "xeno_grid",
                                      "ops": "\n".join(label_ops)})

        # Prove it: every subject drafted, nobody else in frame.
        time.sleep(0.5)
        after = st.call("jawa/list_pawns", {}).get("pawns") or []
        inframe = [p for p in after if not p.get("dead") and p.get("x") is not None
                   and rx - 3 <= p["x"] < rx + rw + 3 and rz - 3 <= p["z"] < rz + rh + 3]
        extra = [p.get("name") for p in inframe if p.get("id") not in mine_ids]
        st.say("in frame: %d pawns, %d not subjects %s"
               % (len(inframe), len(extra), extra if extra else ""))

        st.call("jawa/set_fog", {"mode": "unfog", "x": rx, "z": rz,
                                 "width": rw, "height": rh})
        st.call("rimworld/jump_camera_to_cell", {"x": cx, "z": cz})
        st.call("rimworld/frame_cell_rect", {"x": rx, "z": rz, "width": rw,
                                             "height": rh, "paddingCells": 3})
        st.call("jawa/clear_ui", {})
        time.sleep(0.8)

        # The param is `fileName`, NOT `name` -- the unknown-param guard caught that live,
        # and the bridge would otherwise have DISCARDED it and shot to a default name.
        # take_screenshot appends .png itself; a name ending in .png yields x.png.png
        shot = st.call("jawa/take_screenshot", {"fileName": args.shot})
        st.say("screenshot: %s" % json.dumps(shot.get("path") or shot.get("message")))

        cam = st.call("rimworld/get_camera_state", {})
        st.say("camera map=%s zoom=%s" % (cam.get("mapId"), cam.get("zoom")))
        print("\n🔑 The PNG is a cache, not an observation. Go and LOOK at it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
