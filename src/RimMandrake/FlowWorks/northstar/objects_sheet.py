"""objects_sheet.py -- RUNBOOK: python.exe src/RimMandrake/FlowWorks/northstar/objects_sheet.py   (~6-8 min live; bridge held, a Playing map; river groups want a river map: river_site.py first)
   offline proof of the script itself: python3 src/RimMandrake/FlowWorks/northstar/objects_sheet.py --mock   (seconds, no game)
   options: --only ladders,styles,river  --no-shots  --mock-fail <group>

CANAL_OBJECTS_SHEET_BUILD_POSES_AND_STYLES. Stages and photographs, one labelled picture per group:
  ladders_lowered / ladders_raised   RM_Ladder on each of the four walls of a 3x3 pit (lowered, then slid up onto the rim)
  ladders_autoturn                   RM_Ladder PLACED facing away from its wall: the game turns it to the wall (RM_LadderWallMath)
  styles_<kind>                      tank, tall tank, hose reel, universal pipe: the default and Futuristic/Industrial/Modern/Scrapper
  river_weirs / river_fords          RM_BankWeir (default + four styles) on a river bank; RM_FordStones laid across shallow water
Every placed Thing's ROTATION IS READ BACK from the game (jawa/list_things) and printed beside the rotation we asked for; a
rotation the game does not report is UNMEASURED, never assumed. Words: MATCHES (the game reads what the doc/ask says), DIFFERS,
UNMEASURED (reason printed). Nothing here is a verdict on the art: the owner ticks 'looks right / looks wrong / note' per group in
Transient/fw_scenes/live/objects/index.html. A crash in a group is printed in full, kept in <group>_traceback_<stamp>.txt, and the
walk goes on. The things stay standing on the map afterwards so he can walk the camera over them.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import fw_walk_common as C  # noqa: E402

REPO = C.REPO
PROMO = "RimMandrake.FlowWorks.RM_PromotionProofs"
OUT_LIVE = os.path.join(REPO, "Transient", "fw_scenes", "live", "objects")
OUT_MOCK = os.path.join(REPO, "Transient", "fw_scenes", "mock", "objects")

X0, Z0 = 190, 150            # ladder site; styles sit west of it
PIT = 3
STYLE_SUFFIX = ("", "_Futuristic", "_Industrial", "_Modern", "_Scrapper")
STYLE_LABEL = ("default", "Futuristic", "Industrial", "Modern", "Scrapper")
KINDS = (("tank", "RM_LiquidTank", 2), ("tall tank", "RM_LiquidTankTall", 2),
         ("hose reel", "RM_HoseReel", 2), ("universal pipe", "RM_UniversalPipe", 1))
WEIR = "RM_BankWeir"
FORD = "RM_FordStones"


# ---------------------------------------------------------------- geometry (pure)
def wall_cell(pit, r):
    """The pit cell on wall `r` (0=N,1=E,2=S,3=W) where a ladder hangs, middle of that side of a 3x3 pit at origin `pit`."""
    px, pz = pit
    return {0: (px + 1, pz + 2), 1: (px + 2, pz + 1), 2: (px + 1, pz), 3: (px, pz + 1)}[r]


def pit_origin(row, col):
    return (X0 + col * 6, Z0 + row * 7)


def ford_line(terrain, size, n=4, margin=12):
    """n consecutive WaterMovingShallow cells in a straight line (east-west or north-south), nearest the map centre; [] if none."""
    w, h = size
    best, bd = [], None
    for (x, z), t in terrain.items():
        if t != "WaterMovingShallow" or not (margin <= x < w - margin and margin <= z < h - margin):
            continue
        for dx, dz in ((1, 0), (0, 1)):
            line = [(x + dx * k, z + dz * k) for k in range(n)]
            if all(terrain.get(c) == "WaterMovingShallow" for c in line):
                d = (x - w / 2.0) ** 2 + (z - h / 2.0) ** 2
                if bd is None or (d, x, z, dx) < bd:
                    bd, best = (d, x, z, dx), line
    return best


# ---------------------------------------------------------------- groups
def status(ok):
    return "UNMEASURED" if ok is None else ("MATCHES" if ok else "DIFFERS")


def dig_pit(w, pit):
    for i in range(PIT):
        for j in range(PIT):
            w.dig((pit[0] + i, pit[1] + j), 3, -1)


def ladder_group(w, gid, title, row, mode, out_dir):
    """mode: 'lowered' | 'raised' | 'autoturn'."""
    rect = (X0 - 2, Z0 + row * 7 - 2, 4 * 6 + 2, PIT + 4)
    caps, readings, notes = [], [], []
    for r in range(4):
        pit = pit_origin(row, r)
        dig_pit(w, pit)
        c = wall_cell(pit, r)
        asked = (r + 2) % 4 if mode == "autoturn" else r      # autoturn: faces INTO the pit, away from its wall
        res = C.place(w, "RM_Ladder", c, rot=asked)
        raised = None
        if res["survived"] and mode == "raised":
            ok, txt = w.proof(PROMO, "ProofLadder", "%d,%d,raise" % c)
            raised = ("raised=True" in txt) if ok else None
            notes.append("raise %s: %s" % (c, txt[:100]))
        name = C.ROT_NAMES[r]
        read = C.rot_text(res["rot_read"])
        if not res["survived"]:
            ok = None
        elif res["rot_read"] is None:
            ok = None
        else:
            ok = res["rot_read"] == r
        if mode == "raised" and ok and raised is not True:
            ok = None if raised is None else False
        caps.append("%s wall: asked %s, game reads %s%s" % (name, C.rot_text(asked), read,
                                                           ", raised=%s" % raised if mode == "raised" else ""))
        readings.append((status(ok), "%s wall (cell %d,%d): asked %s -> game reads %s%s%s" % (
            name, c[0], c[1], C.rot_text(asked), read, "; raised=%s" % raised if mode == "raised" else "",
            "; " + res["note"] if res["note"] else "")))
        w.rows.append(dict(id="%s.%s" % (gid, name), status=status(ok), game=readings[-1][1]))
    w.ticks(1)
    png = C.snap(w, gid, rect)
    img = []
    if png:
        dst = C.label_image(png, os.path.join(out_dir, gid + "_labelled.png"), title,
                            "Pits left to right: " + ", ".join(C.ROT_NAMES[r] + " wall" for r in range(4)), caps)
        img.append((os.path.basename(dst), title))
    for line in readings:
        w.say("  %-10s %s" % line)
    return dict(id=gid, title=title, readings=readings, images=img, notes=notes,
                looking_at={"lowered": "A 3x3 pit, 3 levels deep, per wall. A ladder hangs on the middle square of one wall, slid DOWN: drawn pressed against that wall.",
                            "raised": "The same four pits, ladders slid UP onto the rim: drawn lying on the rim beyond the wall.",
                            "autoturn": "A ladder placed with its facing pointing INTO the pit (away from any wall)."}[mode],
                check={"lowered": ["Each ladder is drawn against ITS wall (left to right: north, east, south, west).", "It points the same way the caption says the game read back."],
                       "raised": ["Each ladder lies on the rim beyond its wall, not inside the pit.", "Facing matches the caption."],
                       "autoturn": ["Each ladder turns itself to the wall; the caption 'game reads' equals the wall name, not what we asked."]}[mode],
                passif="Every picture shows the ladder on the wall the caption names.", fails="A ladder drawn on the wrong side, floating, or turned away from its wall.")


def _style_menu(w, cell):
    """Select the thing at `cell`, press its "Choose style" button, return (menuId, options) or (None, why)."""
    B = w.B
    B.call("rimworld/set_god_mode", enabled=True)
    B.call("rimworld/clear_selection")
    B.call("rimworld/click_cell", x=cell[0], z=cell[1])
    gz = (B.call("rimworld/list_selected_gizmos") or {}).get("gizmos") or []
    g = next((q for q in gz if str(q.get("label") or "").startswith("Choose style")), None)
    if g is None:
        return None, "no 'Choose style' button (have %s)" % [q.get("label") for q in gz][:6]
    B.call("rimworld/execute_gizmo", gizmoId=g.get("gizmoId") or g.get("id"))
    o = B.call("rimworld/get_context_menu_options") or {}
    return o.get("menuId"), o.get("options") or []


def current_look(w, cell):
    """The look the game says this thing wears now (the menu's "(current)" entry); None = UNMEASURED."""
    mid, opts = _style_menu(w, cell)
    w.B.call("rimworld/close_context_menu")
    w.B.call("rimworld/clear_selection")
    if mid is None:
        return None
    cur = [str(o.get("label")).split(" (current)")[0] for o in opts if "(current)" in str(o.get("label"))]
    return cur[0] if cur else None


def choose_look(w, cell, look, run=False):
    """Pick `look` for the thing at `cell` (the whole connected run for a pipe) and read the look back."""
    mid, opts = _style_menu(w, cell)
    if mid is None:
        return None
    # tanks/pipes read "<Look>: this tank" / "<Look>: whole connected run"; the reel's menu reads just "<Look>" (LIVE 2026-10-17)
    want = [o for o in opts if str(o.get("label")).split(" (current)")[0].split(":")[0] == look]
    pick = [o for o in want if ("whole connected run" in str(o.get("label"))) == run] or want
    if not pick:
        w.B.call("rimworld/close_context_menu")
        return None
    w.B.call("rimworld/execute_context_menu_option", optionIndex=pick[0].get("index"))
    w.B.call("rimworld/clear_selection")
    return current_look(w, cell)


def style_group(w, gid, kind_label, base, size_, row, out_dir):
    x1, z1 = 150, 150 + row * 6
    rect = (x1 - 2, z1 - 2, len(STYLE_SUFFIX) * 5 + 3, 6)
    caps, readings = [], []
    w.clear_site(rect)
    for k, suf in enumerate(STYLE_SUFFIX):
        # LIVE 2026-10-17: the _<Look> names are ThingStyleDefs, not ThingDefs (build_batch: "no ThingDef"). Build the BASE def
        # and pick the look through the game's own "Choose style" button; the look is read back from that menu's "(current)".
        d = base
        cells = [(x1 + k * 5 + i, z1) for i in range(3)] if base == "RM_UniversalPipe" else [(x1 + k * 5, z1)]
        res = [C.place(w, d, c, rot=0) for c in cells]
        placed = all(r["survived"] for r in res)
        look = STYLE_LABEL[k]
        if not placed:
            ok, got = False, "not placed"
        elif not suf:
            got = current_look(w, cells[0])
            ok = None if got is None else True
            got = "default look = %s" % got
        else:
            got = choose_look(w, cells[0], look, run=len(cells) > 1)
            ok = None if got is None else (got == look)
        caps.append("%s = %s (%s)" % (look, d, got))
        readings.append((status(ok), "%s %s: %d of %d placed; game reads look %s%s" % (
            d, look, sum(r["survived"] for r in res), len(res), got, "; " + res[0]["note"] if res[0]["note"] else "")))
        w.rows.append(dict(id="%s.%s" % (gid, STYLE_LABEL[k]), status=status(ok), game=readings[-1][1]))
    w.ticks(1)
    png = C.snap(w, gid, rect)
    img = []
    if png:
        dst = C.label_image(png, os.path.join(out_dir, gid + "_labelled.png"), "%s: five looks" % kind_label.capitalize(),
                            "Left to right: " + ", ".join(STYLE_LABEL), caps)
        img.append((os.path.basename(dst), kind_label))
    for line in readings:
        w.say("  %-10s %s" % line)
    return dict(id=gid, title="%s: default + Futuristic / Industrial / Modern / Scrapper" % kind_label.capitalize(),
                readings=readings, images=img,
                looking_at="Five %s, left to right: default, Futuristic, Industrial, Modern, Scrapper." % kind_label,
                check=["The four styles are plainly different from each other and from the default.", "Each reads as its style name (clean white-grey sci-fi, riveted plant, plain modern, scrap-built)."],
                passif="Five distinct, readable looks.", fails="Two styles look alike, a style shows the default, or a picture is missing/placeholder.")


def river_prereq(w):
    size = C.map_size(w)
    terr = C.read_terrain(w, size)
    if not terr:
        return size, None, "terrain unreadable"
    if not any(C.is_moving(t) for t in terr.values()):
        return size, terr, "this map has no moving river water (run river_site.py first)"
    return size, terr, None


def weirs_group(w, out_dir, size, terr, why):
    gid, title = "river_weirs", "Bank weirs: default + four styles on a river bank"
    base = dict(id=gid, title=title, looking_at="Five bank weirs standing on the river's bank edge, left to right in placing order: default, Futuristic, Industrial, Modern, Scrapper.",
                check=["Each weir is a wall across the bank edge facing the water, in its own style.", "The caption's rotation equals the way it faces the water."],
                passif="Five readable weirs on the bank, rotation as read.", fails="A weir floating in the river, facing land, or two styles alike.")
    if why:
        w.say("  UNMEASURED %s: %s" % (gid, why))
        w.rows.append(dict(id=gid, status="UNMEASURED", game=why))
        base["readings"] = [("UNMEASURED", why)]
        return base
    picks = C.spread(C.bank_cells(terr, size), len(STYLE_SUFFIX))
    if len(picks) < len(STYLE_SUFFIX):
        why = "only %d well-spaced bank cells found for 5 weirs" % len(picks)
        w.rows.append(dict(id=gid, status="UNMEASURED", game=why))
        base["readings"] = [("UNMEASURED", why)]
        return base
    readings, caps, cells = [], [], []
    for k, (c, r) in enumerate(picks):
        # LIVE 2026-10-17: RM_BankWeir_<Look> are ThingStyleDefs; build the base weir and pick the look by its own button
        d = WEIR
        res = C.place(w, d, c, rot=r, wipe=True)   # LIVE 2026-10-17: bank grass/reeds refused wipeExisting=false
        cells.append(c)
        look = None
        if res["survived"]:
            look = current_look(w, c) if not STYLE_SUFFIX[k] else choose_look(w, c, STYLE_LABEL[k])
        ok = None if (not res["survived"] or res["rot_read"] is None) else (res["rot_read"] == r)
        if ok and STYLE_SUFFIX[k]:
            ok = None if look is None else (look == STYLE_LABEL[k])
        caps.append("%s: asked %s, game reads %s, look %s" % (STYLE_LABEL[k], C.rot_text(r), C.rot_text(res["rot_read"]), look))
        readings.append((status(ok), "%s %s at %d,%d: asked %s -> reads %s; look %s%s" % (
            d, STYLE_LABEL[k], c[0], c[1], C.rot_text(r), C.rot_text(res["rot_read"]), look, "; " + res["note"] if res["note"] else "")))
        w.rows.append(dict(id="%s.%s" % (gid, STYLE_LABEL[k]), status=status(ok), game=readings[-1][1]))
    w.say("  note: placed with god-mode build_batch (no PlaceWorker); the bank-edge rule itself is the river suite's place_weir_bank_edge")
    xs, zs = [c[0] for c in cells], [c[1] for c in cells]
    rect = (max(0, min(xs) - 6), max(0, min(zs) - 6), max(xs) - min(xs) + 13, max(zs) - min(zs) + 13)
    rect = (rect[0], rect[1], min(rect[2], 60), min(rect[3], 40))
    w.ticks(1)
    png = C.snap(w, gid, rect)
    if png:
        dst = C.label_image(png, os.path.join(out_dir, gid + "_labelled.png"), title, "Placing order, west to east or as the camera frames them", caps)
        base["images"] = [(os.path.basename(dst), title)]
    base["readings"] = readings
    base["notes"] = ["Weirs are spread at least 7 cells apart, so the camera may frame them small."]
    for line in readings:
        w.say("  %-10s %s" % line)
    return base


def fords_group(w, out_dir, size, terr, why):
    gid, title = "river_fords", "Ford stones across shallow water"
    base = dict(id=gid, title=title, looking_at="RM_FordStones (needs the RM_Fordable affordance, which only shallow moving water has) laid as a 4-square line across the shallows.",
                check=["The stones read as a crossing over the water, not as land or as a bridge.", "The caption says what the game reads under each square."],
                passif="Four ford squares visible in the shallows.", fails="No stones drawn, stones over deep water, or the water vanishes.")
    if why:
        w.rows.append(dict(id=gid, status="UNMEASURED", game=why))
        base["readings"] = [("UNMEASURED", why)]
        w.say("  UNMEASURED %s: %s" % (gid, why))
        return base
    line = ford_line(terr, size)
    if not line:
        why = "no straight 4-cell run of WaterMovingShallow on this river"
        w.rows.append(dict(id=gid, status="UNMEASURED", game=why))
        base["readings"] = [("UNMEASURED", why)]
        return base
    w.call("jawa/set_terrain_batch", ops=";".join("%s:%d,%d,1,1" % (FORD, c[0], c[1]) for c in line))
    after = C.read_terrain(w, size)
    got = [(after or {}).get(c) for c in line]
    ok = None if after is None else all(g == FORD for g in got)
    rd = [(status(ok), "top terrain read back at %s: %s" % (line, got))]
    w.rows.append(dict(id=gid, status=status(ok), game=rd[0][1]))
    w.say("  %-10s %s" % rd[0])
    rect = C.centroid_rect(line, 30, 18, size)
    w.ticks(1)
    png = C.snap(w, gid, rect)
    if png:
        dst = C.label_image(png, os.path.join(out_dir, gid + "_labelled.png"), title, "Terrain read back: %s" % got[:1] + " x4", ["cells %s" % line])
        base["images"] = [(os.path.basename(dst), title)]
    base["readings"] = rd
    return base


ALL = ("ladders", "styles", "river")


def build_groups(w, only, out_dir):
    """Run the chosen group families, each group in its own crash guard. Returns the group dicts."""
    groups = []

    def guard(gid, fn):
        if getattr(w.args, "mock_fail", None) == gid:
            raise RuntimeError("injected by --mock-fail %s" % gid)
        return fn()

    def run(gid, fn):
        w.say("=" * 90)
        w.say(gid)
        try:
            groups.append(guard(gid, fn))
        except Exception:  # noqa: BLE001 - print it, keep it, go on
            tbp, last = C.keep_traceback(w, out_dir, gid)
            w.rows.append(dict(id=gid + ".crash", status="CRASHED", game=last, traceback=tbp))
            groups.append(dict(id=gid, title=gid + " (crashed)", readings=[("CRASHED", last)], pre=open(os.path.join(C.REPO, tbp), encoding="utf-8").read()))

    if "ladders" in only:
        w.clear_site((X0 - 2, Z0 - 2, 4 * 6 + 2, 3 * 7 + 2))
        run("ladders_lowered", lambda: ladder_group(w, "ladders_lowered", "Ladders, slid down: one per wall", 0, "lowered", out_dir))
        run("ladders_raised", lambda: ladder_group(w, "ladders_raised", "Ladders, slid up onto the rim: one per wall", 1, "raised", out_dir))
        run("ladders_autoturn", lambda: ladder_group(w, "ladders_autoturn", "Ladders placed facing away from the wall", 2, "autoturn", out_dir))
    if "styles" in only:
        for i, (label, base, sz) in enumerate(KINDS):
            run("styles_" + base, lambda i=i, label=label, base=base, sz=sz: style_group(w, "styles_" + base, label, base, sz, i, out_dir))
    if "river" in only:
        state = {}

        def pre():
            size, terr, why = river_prereq(w)
            state.update(size=size, terr=terr, why=why)
        run("river_prereq", lambda: (pre(), dict(id="river_prereq", title="River map check", readings=[("MATCHES" if not state.get("why") else "UNMEASURED", state.get("why") or "moving river water found")]))[1])
        run("river_weirs", lambda: weirs_group(w, out_dir, state.get("size") or (250, 250), state.get("terr") or {}, state.get("why") or ("" if state.get("terr") else "terrain unreadable")))
        run("river_fords", lambda: fords_group(w, out_dir, state.get("size") or (250, 250), state.get("terr") or {}, state.get("why") or ("" if state.get("terr") else "terrain unreadable")))
    return groups


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=",".join(ALL))
    ap.add_argument("--no-shots", action="store_true")
    ap.add_argument("--pace", type=float, default=0.0)
    ap.add_argument("--mock", action="store_true", help="offline fake game; proves this script's own paths only")
    ap.add_argument("--mock-fail", default=None, help="with --mock: raise inside this group id to prove a crash is kept and the walk goes on")
    ap.add_argument("--fresh-map", action="store_true", help=argparse.SUPPRESS)
    ap.add_argument("--reset-index", action="store_true", help="start index.html afresh (default: it accumulates every group run)")
    a = ap.parse_args(argv)
    only = [s.strip() for s in a.only.split(",") if s.strip()]
    out_dir = OUT_MOCK if a.mock else OUT_LIVE
    mf = a.mock_fail
    w = C.make_walk(a, out_dir)
    a.mock_fail = mf
    if not a.mock:
        st = (w.call("rimworld/get_ui_state") or {}).get("programState")
        if st != "Playing":
            w.say("No Playing game (state %s): start a quicktest map (river_site.py for the river groups) and rerun." % st)
            return 2
        w.call("rimworld/pause_game", paused=True)
        w.call("rimworld/set_god_mode", enabled=True)
    groups = build_groups(w, only, out_dir)
    idx = C.write_index(os.path.join(out_dir, "index.html"), "FlowWorks canal objects: poses and styles",
                        "One picture per group, rotations read back from the game. Tick your answer under each group; "
                        "'Copy my answers as JSON' puts them on the clipboard. Every group you have run stays on the "
                        "page; the newest run of a group replaces its older one.", groups, accumulate=not a.reset_index)
    with open(os.path.join(out_dir, "rows.json"), "w", encoding="utf-8") as f:
        json.dump(w.rows, f, indent=1)
    with open(os.path.join(out_dir, "log_%s.txt" % time.strftime("%Y%m%dT%H%M%S")), "w", encoding="utf-8") as f:
        f.write("\n".join(w.log_lines) + "\n")
    w.say("index: %s" % idx)
    return 1 if any(r.get("status") == "CRASHED" for r in w.rows) else 0


if __name__ == "__main__":
    sys.exit(main())
