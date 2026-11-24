#!/usr/bin/env python3
"""sc_save_reload_wire_down (bar walk_scavenger_base, its script half): a save with a wire down, loaded, still tells the truth about the grid.

Design: design/specs/2026-11-24-oversized-scenes/table.md, the sc_walk row. proof_all's ONE save and load (block save_load) carries it:
  1. stage()   on its own plot: a floor run from a charged battery to a lamp; a pole fed by a second charged battery, strung to a far
               pole that feeds another lamp. Read (uncut), and save that game as <name>_uncut: the control.
  2. wire_down() one floor cell removed and the span cut: a live and a dead floor end, a live and a dead fallen half. Read (before).
  3. proof_all saves, loads, and the same read is made (after).
Rows:
  WD_save_before_cut_refused      the control: the uncut read is refused as not mid-way, and the uncut save file holds no cut span of the
                                  two the wire-down save adds (the saved links are read from the two files, no load is spent)
  WD_reload_true_to_grid          after the load: the same cords as before it, none joining two nets, none without a net, none in a wall
  WD_reload_live_dead_ends_equal  after the load: every floor end, span, fallen half and lamp reads live or dead as before it
A week of play, the second order and the switch by hand are his walk (LOOK_STAGE8). Offline: selftest_gss_small_scenes.py.
"""
import time

PLOT = (60, 212)                    # north of the aerial and scenes plots, east of tap_goodwill's
RECT = (PLOT[0] - 2, PLOT[1] - 2, 36, 20)
FLOOR = [(PLOT[0] + i, PLOT[1]) for i in range(13)]
FLOOR_CUT = FLOOR[6]
FLOOR_BATT = (PLOT[0], PLOT[1] + 1)
FLOOR_LAMP = (PLOT[0] + 12, PLOT[1] + 1)
POLE_A, POLE_B = (PLOT[0] + 4, PLOT[1] + 9), (PLOT[0] + 14, PLOT[1] + 9)
FEED_A = [(PLOT[0] + i, PLOT[1] + 9) for i in range(4)]
FEED_B = [(PLOT[0] + 15 + i, PLOT[1] + 9) for i in range(4)]
SPAN_BATT = (PLOT[0], PLOT[1] + 10)
SPAN_LAMP = (PLOT[0] + 18, PLOT[1] + 10)
ROWS = ["WD_save_before_cut_refused", "WD_reload_true_to_grid", "WD_reload_live_dead_ends_equal"]
CUT_MARK = b"<state>Cut</state>"     # SpanLink.ExposeData: the state is written when it is not Up; a cut span is written at both poles


# LIMIT: danger, vanilla's power net switches a new lamp on some ticks after it is built (dark at 8 ticks, lit at 258, seen live
# 2026-11-24), so a short wait read the uncut scene as unlit. A lamp with no power stays dark to the end of the wait and refuses the row.
LIT_WAIT = (20, 50)


def lamp_on(B, at):
    t = [x for x in B.ap("net:%d,%d" % at).get("things") or [] if x.get("def") == "StandingLamp"]
    return t[0].get("powerOn") if t else None


def stage(B, V):
    r = "%d,%d,%d,%d" % RECT
    B.call("jawa/destroy_batch", rects=r, categories="All")
    B.call("jawa/set_terrain_batch", ops="Soil:" + r, clearOverlays=True)
    B.call("jawa/set_fog", action="unfog", rect=r)
    B.call("jawa/set_roof_batch", ops="None:" + r)
    B.call("jawa/build_batch", ops=V.ops("PowerConduit", FLOOR + FEED_A + FEED_B), faction="player", wipeExisting=False)
    B.call("jawa/build_batch", ops="Battery:%d,%d,0;Battery:%d,%d,0;StandingLamp:%d,%d;StandingLamp:%d,%d;RM_AerialMast:%d,%d;RM_AerialMast:%d,%d"
           % (FLOOR_BATT + SPAN_BATT + FLOOR_LAMP + SPAN_LAMP + POLE_A + POLE_B), faction="player", wipeExisting=False)
    B.call("jawa/map_commit")
    B.ticks(3)
    for t in B.call("jawa/list_things", defName="Battery", rect=r, limit=20).get("things") or []:
        B.call("jawa/battery_set", thing=t.get("id") or t.get("thingId"), mode="setPct", value=1.0)
    pos = {(a["x"], a["z"]): a for a in B.ap("census").get("anchors") or []}
    if POLE_A in pos and POLE_B in pos and not any(q.get("other") == pos[POLE_B]["id"] for q in pos[POLE_A].get("links") or []):
        B.ap("link:%d,%d" % (pos[POLE_A]["id"], pos[POLE_B]["id"]))
    for _ in range(LIT_WAIT[0]):
        B.ticks(LIT_WAIT[1])
        if all(lamp_on(B, at) is True for at in (FLOOR_LAMP, SPAN_LAMP)):
            break


def wire_down(B):
    """One floor cell out, the poles' span cut."""
    B.call("jawa/destroy_batch", rects="%d,%d,1,1" % FLOOR_CUT, categories="Building")
    pos = {(a["x"], a["z"]): a["id"] for a in B.ap("census").get("anchors") or []}
    done = B.ap("cut:%d,%d" % (pos[POLE_A], pos[POLE_B])).get("done") if POLE_A in pos and POLE_B in pos else False
    B.ticks(3)
    return done


def read(B, sleep=time.sleep, ticks=0):
    """One read of the plot: the cords' rect census, the poles, the two lamps. {} of any part that could not be read is kept as None."""
    B.call("rimworld/frame_cell_rect", x=RECT[0], z=RECT[1], width=RECT[2], height=RECT[3], paddingCells=1)
    sleep(1.0)
    if ticks:
        B.ticks(ticks)
    B.probe("rebuild")
    B.probe("poll")
    B.ap("poll")
    c, a = B.probe("rect:%d,%d,%d,%d" % RECT), B.ap("census")
    if not c.get("success") or not a.get("success") or "cordEdges" not in c:
        return None
    here = {q["id"]: (q["x"], q["z"]) for q in a.get("anchors") or []}
    poles = {}
    for q in a.get("anchors") or []:
        if here[q["id"]] in (POLE_A, POLE_B):
            poles[here[q["id"]]] = {"netLive": q.get("netLive"), "fallenLive": q.get("fallenLive"), "fallen": len(q.get("fallen") or []),
                                    "links": sorted((here.get(k.get("other"), (-1, -1)), k.get("state")) for k in q.get("links") or [])}
    lamps = {}
    for at in (FLOOR_LAMP, SPAN_LAMP):
        lamps[at] = lamp_on(B, at)
    return {"cords": sorted(c.get("edgeHashes") or {}), "across": c.get("cordsAcrossNets"), "noNet": c.get("cordEndsWithoutNet"),
            "inWall": c.get("verticesInUnwalkable"), "edges": c.get("cordEdges"),
            "ends": sorted((tuple(e["cell"]), e.get("registryLive"), e.get("netLive")) for e in c.get("ends") or []),
            "poles": poles, "lamps": lamps}


def whole(r):
    """Why the uncut scene does not stand as staged ([] = it stands): the span up, both lamps lit, cords laid."""
    if r is None:
        return ["the plot could not be read"]
    out = []
    if not r["edges"]:
        out.append("no cord on the plot")
    if not (r["poles"].get(POLE_A) or {}).get("links") or any(s != "Up" for q in r["poles"].values() for _, s in q["links"]):
        out.append("the span is not up")
    out += ["the lamp at %s is not lit" % (k,) for k, v in sorted(r["lamps"].items()) if v is not True]
    return out


def midway(r):
    """Why a read is not of a game with a wire down ([] = it is mid-way): a cut span with a live and a dead half, a cut floor run with a
    live and a dead end."""
    if r is None:
        return ["the plot could not be read"]
    out = []
    if not any(s == "Cut" for q in r["poles"].values() for _, s in q["links"]):
        out.append("no cut span")
    if sorted(str((r["poles"].get(p) or {}).get("fallenLive")) for p in (POLE_A, POLE_B)) != ["False", "True"]:
        out.append("no live and dead fallen half")
    ends = {c: live for c, live, _ in r["ends"]}
    if ends.get(FLOOR[5]) is not True or ends.get(FLOOR[7]) is not False:
        out.append("no live and dead floor end beside the cut cell")
    return out


def compare(before, after):
    """-> {"refused": [why], "grid": [faults], "ends": [faults]}; refused is not empty when `before` is not mid-way."""
    why = midway(before)
    if why:
        return {"refused": why, "grid": [], "ends": []}
    if after is None:
        return {"refused": ["the plot could not be read after the load"], "grid": [], "ends": []}
    grid = ["%s=%s" % (k, after[k]) for k in ("across", "noNet", "inWall") if after[k] != 0]
    grid += ["cord %s: gone after the load" % k for k in before["cords"] if k not in after["cords"]]
    grid += ["cord %s: not there before the save" % k for k in after["cords"] if k not in before["cords"]]
    ends = ["floor end %s" % (e,) for e in sorted(set(map(str, before["ends"])) ^ set(map(str, after["ends"])))]
    ends += ["pole %s: %s, was %s" % (p, after["poles"].get(p), before["poles"].get(p)) for p in (POLE_A, POLE_B)
             if after["poles"].get(p) != before["poles"].get(p)]
    ends += ["lamp %s: %s, was %s" % (p, after["lamps"].get(p), v) for p, v in sorted(before["lamps"].items()) if after["lamps"].get(p) != v]
    return {"refused": [], "grid": grid, "ends": ends}


def control_row(uncut, uncut_blob, cut_blob):
    """-> (status, class, detail) of WD_save_before_cut_refused. The two saves differ by the plot's one cut span (two link records) or more:
    proof_all cuts a second span between them."""
    stood = whole(uncut)
    n = None if uncut_blob is None or cut_blob is None else (uncut_blob.count(CUT_MARK), cut_blob.count(CUT_MARK))
    d = {"uncutScene": stood or "stands", "refused": compare(uncut, uncut)["refused"], "cutLinksInSave": n}
    if stood or n is None:
        return "UNMEASURED", "SITE", d
    return ("PASS" if d["refused"] and n[1] >= n[0] + 2 else "FAIL"), "HARNESS", d


def reload_rows(before, after):
    """-> [(row id, status, class, detail)] of the two reload rows."""
    c = compare(before, after)
    if c["refused"]:
        return [(r, "UNMEASURED", "SITE", {"refused": c["refused"]}) for r in ROWS[1:]]
    size = {"cords": len(before["cords"]), "ends": len(before["ends"]), "poles": len(before["poles"])}
    return [(ROWS[1], "FAIL" if c["grid"] else "PASS", "MOD", dict(size, faults=c["grid"][:8])),
            (ROWS[2], "FAIL" if c["ends"] else "PASS", "MOD", dict(size, faults=c["ends"][:8]))]


def read_after_load(B, before, sleep=time.sleep, clock=time.monotonic):
    """The read after the load, again until the plot's cords and poles are laid as before, or 20 s. LIMIT: danger, anchors and cords
    register a little after a load (validation_aerial LEARNED, up to 12 s in proof_all's own waits), so a first read can be short; a load
    that really lost a cord reads the same at the end of the wait and FAILs."""
    t0 = clock()
    r = read(B, sleep, ticks=10)
    while clock() - t0 < 20.0 and before is not None and (r is None or len(r["cords"]) < len(before["cords"]) or r["poles"] != before["poles"]):
        sleep(1.0)
        r = read(B, sleep, ticks=10)
    return r
