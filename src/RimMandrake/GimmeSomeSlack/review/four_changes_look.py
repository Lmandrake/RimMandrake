"""four_changes_look.py -- Gimme Some Slack 0.1.1: the owner's short look at the four changes since his walk of 2026-11-22
(item RIMMANDRAKE_STAGE_SLACK_SHORT_LOOK_AT_FOUR_CHANGES_THEN_HIS_PASS; his card "Short look at the four").

Run on his walk save GSS_011_VISIT2_WALK_20261121 (the 31-station review map built by human_review.py), loaded on his full
list with the 0.1.1 fix build deployed. It keeps three stations of that save exactly as built (so the cords he judged are
the same cords) and clears everything else the review map owns:

  A  KINKS ROUNDED      = walk station 3 (GROUND CORDS: Modern), kept as built: the pile cables at the two power strips
                          and the switch lead at the wall plate, where his three kinks were
  B  SWITCH LAMP        = new: three short runs, each battery > conduit > power switch > conduit > lamp:
                          closed + powered (green), open + powered (red), closed + unpowered (dark); the lamp at half size
  C  RESTYLE...         = walk station 10 (a Scrapper run: battery, conduit, switch, lamp, power mast, span, lamp mast),
                          kept, plus a new SECOND run that touches nothing of it (Industrial: conduit, switch, lamp,
                          power mast, lamp mast, wall bracket), so "This item / All connected / All on map" each repaint a
                          visibly different set
  D  GUST SWAY          = walk station 6 (OVERHEAD: FOUR LOOKS), kept; Gust is the shipped default (aerial.swayLook)

    python.exe src/RimMandrake/GimmeSomeSlack/review/four_changes_look.py --stage            # on the loaded walk save
    python.exe src/RimMandrake/GimmeSomeSlack/review/four_changes_look.py --shots <dir>      # one capture per station
    python.exe src/RimMandrake/GimmeSomeSlack/review/four_changes_look.py --save <NAME>      # keeper save + sign sidecar
    python3    src/RimMandrake/GimmeSomeSlack/review/four_changes_look.py --plan             # offline: rects and labels only

--stage reads back what it built and prints one JSON line (reads: switch lamps, the restyle runs, the sway look) and
exits 0 when every read matches, 1 when one does not, 2 when it could not run (no review map / probe dead).
Leaves the game PAUSED.
"""
import argparse
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
GSS = os.path.dirname(HERE)
for p in (GSS, os.path.join(GSS, "northstar_matrix")):
    if p not in sys.path:
        sys.path.insert(0, p)
import human_review as HR  # noqa: E402

RM = HR.RM
TAG = HR.TAG
KEEP = {3: "A", 10: "C", 6: "D"}            # walk station number -> its letter on this map
SW0 = (166, 37)                              # B: the switch-lamp trio (south of station 3's row, east of station 6)
SW_ROWS = [("GREEN", 17, "full", "on"), ("RED", 9, "full", "off"), ("DARK", 1, "empty", "on")]   # 8 apart: slack loops stay in their row   # (want, dz, battery, switch)
RB0 = (164, 84)                              # C: the second run, 9 cells south of station 10's run
RB_LOOK = "Industrial"
GOLD, CREAM, TEAL, RUST = HR.GOLD, HR.CREAM, HR.TEAL, HR.RUST
LABEL_UP = 5                                 # the card's lines draw below its title: start it 5 cells above the station
                                             # (D's card goes below station D: above it is B's bottom row)


def stations():
    S = {s["n"]: s for s in HR.station_list()}
    return {KEEP[n]: S[n] for n in KEEP}


def sw_cells(dz):
    x, z = SW0[0], SW0[1] + dz
    return dict(battery=(x, z - 1), conduit=[(x + i, z) for i in (1, 2, 3, 4)] + [(x + i, z) for i in (6, 7, 8, 9)],
                switch=(x + 5, z), lamp=(x + 10, z))


def rb_cells():
    x, z = RB0
    return dict(battery=(x, z + 2), conduit=[(x + i, z + 2) for i in range(2, 8)] + [(x + i, z + 2) for i in range(9, 15)],
                switch=(x + 8, z + 2), lamp=(x + 15, z + 2), mast=(x + 14, z + 3), lampmast=(x + 21, z + 3),
                bracket=(x + 26, z + 3), wall=[(x + 27, z + d) for d in (2, 3, 4)])


B_RECT = (SW0[0] - 1, SW0[1] - 1, 14, 21)
C2_RECT = (RB0[0] - 1, RB0[1] + 1, 30, 4)


def keep_rects(K):
    return [HR.rect_of(s, 1) for s in K.values()] + [B_RECT, C2_RECT]


def complement(region, keeps):
    """Rects covering every cell of region outside keeps (row runs, merged down while identical)."""
    x0, z0, w, h = region
    rows = []
    for z in range(z0, z0 + h):
        segs, x = [], x0
        while x < x0 + w:
            if any(k[0] <= x < k[0] + k[2] and k[1] <= z < k[1] + k[3] for k in keeps):
                x += 1
                continue
            s = x
            while x < x0 + w and not any(k[0] <= x < k[0] + k[2] and k[1] <= z < k[1] + k[3] for k in keeps):
                x += 1
            segs.append((s, x - s))
        rows.append((z, tuple(segs)))
    out, i = [], 0
    while i < len(rows):
        z, segs = rows[i]
        j = i
        while j + 1 < len(rows) and rows[j + 1][1] == segs:
            j += 1
        out += [(s, z, n, j - i + 1) for s, n in segs]
        i = j + 1
    return out


def cards(K):
    a, c, d = K["A"], K["C"], K["D"]
    return {
        "A": dict(rect=HR.rect_of(a, 0), title="A  KINKS ROUNDED (walk station 3)",
                  clause="the same Modern cords you judged; the three kinks were at the two power strips (pile cables) and the "
                         "switch lead at the steel wall's plate",
                  do="zoom in on the two power strips in the 3x3 pile and on the plate where the lead meets the wall",
                  decide="does every cord bend in a smooth curve, with no sharp hook at a strip, a socket or the plate?"),
        "B": dict(rect=(SW0[0], SW0[1], 12, 19), title="B  SWITCH LAMP: HALF SIZE",
                  clause="three runs, top to bottom: closed + powered = GREEN; open + powered = RED; closed, battery empty = DARK",
                  do="zoom in on each switch; flick one (select it > the toggle) and watch the lamp change",
                  decide="is the lamp the right size now (half the old lens and glow), and do the colours read at a glance?"),
        "C": dict(rect=(c["origin"][0], RB0[1], 30, c["origin"][1] + c["size"][1] - RB0[1]), title="C  RESTYLE...: THREE REACHES",
                  clause="upper run (Scrapper: conduit, switch, lamp, power mast, span, lamp mast) and lower run (Industrial: the "
                         "same plus a wall bracket) do not touch",
                  do="select any piece > Restyle... > This item, then All connected, then All on map (last: it repaints A, "
                     "B and D too; reload the save to undo)",
                  decide="can you read the menu, and does each reach change exactly the set it names?"),
        "D": dict(rect=HR.rect_of(d, 0), title="D  GUST SWAY (UNPAUSE TO SEE IT)",
                  clause="overhead lines in four looks; Gust is now the default way pole wires swing (Mod Settings > wire sway)",
                  do="UNPAUSE: the game is paused, and wires only sway while time runs; watch the spans for a minute",
                  decide="do the wires move like a hanging cable caught by gusts, and not too stiff?"),
    }


def label_ops(K):
    C = cards(K)
    L = []
    for k in "ABCD":
        x, z, w, h = C[k]["rect"]
        L.append(RM.label_line(x + w // 2, (z - 2) if k == "D" else (z + h + LABEL_UP), C[k]["title"], RM.sign_sub(C[k]["clause"], "", C[k]["do"], C[k]["decide"]),
                               GOLD, "medium", TAG))
    L.append(RM.label_line(185, 113, "GIMME SOME SLACK 0.1.1 - YOUR SHORT LOOK AT THE FOUR CHANGES",
                           "A kinks rounded (north-east)  |  B switch lamp half size  |  C Restyle... three reaches (north)  |  "
                           "D Gust sway (south; unpause)  |  the game is PAUSED", CREAM, "medium", TAG))
    for want, dz, _, _ in SW_ROWS:
        c = sw_cells(dz)
        L.append(RM.label_line(c["battery"][0] - 3, c["battery"][1], "switch lamp: " + want.lower(), "", RUST, "small", TAG))
    L.append(RM.label_line(RB0[0] + 13, RB0[1] + 1, "second run: touches nothing above", "", RUST, "small", TAG))
    return L


def sign_ops(K):
    C = cards(K)
    out = []
    for k in "ABCD":
        x, z, w, h = C[k]["rect"]
        out.append(RM.sign_book(x, z + h, k, C[k]["title"].split("  ", 1)[1], C[k]["clause"], "", C[k]["do"], C[k]["decide"],
                                more="Item RIMMANDRAKE_STAGE_SLACK_SHORT_LOOK_AT_FOUR_CHANGES_THEN_HIS_PASS."))
    return out


def clear_rest(B, K):
    keeps = keep_rects(K)
    rects = []
    for reg in (HR.REGION, HR.REGION2, HR.STALE_WEST):
        rects += complement(reg, keeps)
    for r in rects:
        rr = "%d,%d,%d,%d" % r
        B.call("jawa/destroy_batch", rects=rr, categories="All")
    ops = ";".join("Soil:%d,%d,%d,%d" % r for r in rects)
    B.call("jawa/set_terrain_batch", ops=ops)
    for r in rects:
        B.call("jawa/set_fog", action="unfog", rect="%d,%d,%d,%d" % r)
    B.call("jawa/set_roof_batch", ops=";".join("None:%d,%d,%d,%d" % r for r in rects))
    # the new builds' own ground
    for r in (B_RECT, C2_RECT):
        rr = "%d,%d,%d,%d" % r
        B.call("jawa/destroy_batch", rects=rr, categories="All")
        B.call("jawa/set_terrain_batch", ops="Soil:" + rr)
        B.call("jawa/set_roof_batch", ops="None:" + rr)
    B.call("jawa/map_commit")
    return len(rects)


def ops(d, cells, rot=None):
    return ";".join("%s:%d,%d%s" % (d, x, z, "" if rot is None else ",%d" % rot) for x, z in cells)


def build_switch_trio(B):
    for _, dz, _, _ in SW_ROWS:
        c = sw_cells(dz)
        B.call("jawa/build_batch", ops=ops("Battery", [c["battery"]], 0), faction="player", wipeExisting=False)
        B.call("jawa/build_batch", ops=ops("PowerConduit", c["conduit"]), faction="player", wipeExisting=False)
        B.call("jawa/build_batch", ops=ops("PowerSwitch", [c["switch"]], 0), faction="player", wipeExisting=False)
        B.call("jawa/build_batch", ops=ops("StandingLamp", [c["lamp"]]), faction="player", wipeExisting=False)
    B.ticks(3)
    for _, dz, bat, flick in SW_ROWS:
        c = sw_cells(dz)
        B.probe("battery:%d,%d=%s" % (c["battery"] + (bat,)))
        B.probe("flick:%d,%d=%s" % (c["switch"] + (flick,)))
    B.ticks(3)


def build_second_run(B):
    c = rb_cells()
    B.ap("set:autoLink=False")                      # the new masts must not link to station 10's (one run each)
    B.ap("clearpicks")
    B.ap("cclearpicks")
    B.call("jawa/build_batch", ops=ops("Wall", c["wall"]), stuff="Steel", faction="player", wipeExisting=False)
    B.call("jawa/build_batch", ops=ops("Battery", [c["battery"]], 1), faction="player", wipeExisting=False)
    fails = []
    for cell in c["conduit"][:6]:
        r = B.ap("cplace:PowerConduit:%s:%d,%d:god" % ((RB_LOOK,) + cell))
        fails += [] if r.get("success") else [("conduit", cell, r.get("error"))]
    r = B.ap("cplace:PowerSwitch:%s:%d,%d:god" % ((RB_LOOK,) + c["switch"]))
    fails += [] if r.get("success") else [("switch", c["switch"], r.get("error"))]
    for cell in c["conduit"][6:]:
        r = B.ap("cplace:PowerConduit:%s:%d,%d:god" % ((RB_LOOK,) + cell))
        fails += [] if r.get("success") else [("conduit", cell, r.get("error"))]
    r = B.ap("cplace:StandingLamp:%s:%d,%d:god" % ((RB_LOOK,) + c["lamp"]))
    fails += [] if r.get("success") else [("lamp", c["lamp"], r.get("error"))]
    for d, cell, rot in (("RM_AerialMast", c["mast"], ""), ("RM_AerialLampMast", c["lampmast"], ""),
                         ("RM_AerialWallBracket", c["bracket"], ":1")):
        r = B.ap("place:%s:%s:%d,%d%s:god" % (d, RB_LOOK, cell[0], cell[1], rot))
        fails += [] if r.get("success") else [(d, cell, r.get("error"))]
    B.ap("cprocess")
    B.ap("clearpicks")
    B.ap("cclearpicks")
    B.ticks(1)
    apos = {(a["x"], a["z"]): a["id"] for a in B.ap("census").get("anchors") or []}
    ids = [apos.get(c[k]) for k in ("mast", "lampmast", "bracket")]
    links = []
    if None not in ids:
        links = [B.ap("link:%d,%d" % (ids[0], ids[1])).get("verdict"), B.ap("link:%d,%d" % (ids[1], ids[2])).get("verdict")]
    else:
        fails.append(("anchors", ids, "missing"))
    bats = B.call("jawa/list_things", defName="Battery", rect="%d,%d,%d,%d" % C2_RECT, limit=10).get("things") or []
    for t in bats:
        B.call("jawa/battery_set", thing=t.get("id") or t.get("thingId"), mode="setPct", value=1.0)
    B.ticks(30)
    B.ap("set:autoLink=True")
    return dict(fails=fails, links=links, anchors=ids)


def reads(B, K):
    out, bad = {}, []
    sl = B.probe("switchlights")
    sw = {tuple(s.get("pos") or ()): s for s in sl.get("switches") or []}
    out["switch_lamps"] = {}
    for want, dz, _, _ in SW_ROWS:
        got = (sw.get(sw_cells(dz)["switch"]) or {}).get("lamp")
        out["switch_lamps"][want] = got
        if (got or "").lower() != want.lower():
            bad.append("switch row %s reads %s" % (want, got))
    c = K["C"]
    cx, cz, cw, ch = c["origin"][0], RB0[1], 30, c["origin"][1] + c["size"][1] - RB0[1]
    st = B.ap("cstyles:%d,%d,%d,%d" % (cx, cz, cw, ch))
    runs = {}
    for m in st.get("members") or []:
        runs.setdefault(m.get("run"), set()).add(m.get("rawStyle"))
    out["restyle_runs"] = {str(k): sorted(str(x) for x in v) for k, v in runs.items()}
    out["restyle_lamps"] = [(l.get("x"), l.get("z"), l.get("rawStyle") or l.get("look")) for l in st.get("lamps") or []]
    if len(runs) != 2:
        bad.append("restyle site holds %d runs, want 2" % len(runs))
    cen = B.ap("census")
    out["sway_look"] = cen.get("swayLook")
    out["sway"] = {k: cen.get(k) for k in ("swayReason", "swayDraws", "spanDraws")}
    if out["sway_look"] != "Gust":
        bad.append("sway look %s, want Gust" % out["sway_look"])
    return out, bad


def pause(B):
    B.call("rimworld/pause_game", pause=True)
    t1 = B.call("jawa/time_clock").get("ticksGame")
    time.sleep(1.5)
    t2 = B.call("jawa/time_clock").get("ticksGame")
    return t1 is not None and t1 == t2, t1


SHOTS = {  # name -> rect (x, z, w, h) on the map; filled from the cards
}


def shots(B, K, out):
    C = cards(K)
    os.makedirs(out, exist_ok=True)
    res = {}
    a = K["A"]
    plan = [("A_kinks_whole", C["A"]["rect"]), ("A_kinks_pile", (a["origin"][0] + 2, a["origin"][1] + 1, 8, 5)),
            ("B_switch_lamps", C["B"]["rect"])]
    for want, dz, _, _ in SW_ROWS:
        sx, sz = sw_cells(dz)["switch"]
        plan.append(("B_switch_%s_close" % want.lower(), (sx - 1, sz, 3, 1)))
    plan += [("C_restyle_runs", C["C"]["rect"]), ("D_gust_overhead", C["D"]["rect"])]
    B.call("jawa/clear_ui", all=True)
    time.sleep(1.5)
    for name, (x, z, w, h) in plan:
        # Camera+ on his list eases every camera move, and screenshot_cell_rect's own crop came out wrong while it moved
        # (2026-11-22): jump, zoom, wait until the view rect stops moving, then take the whole screen.
        B.call("rimworld/jump_camera_to_cell", x=x + w // 2, z=z + h // 2)
        B.call("rimworld/set_camera_zoom", rootSize=max(4.0, h + 2.0, (w + 2.0) / 1.55))   # Camera+: root 12 shows 19 x 13 cells
        last = None
        for _ in range(20):
            time.sleep(0.5)
            v = B.call("rimworld/get_camera_state").get("viewRect")
            if v and v == last:
                break
            last = v
        B.call("jawa/clear_ui", all=True)
        time.sleep(1.0)
        r = B.call("rimworld/take_screenshot", fileName=name, suppressMessage=True, includeTargets=False)
        src = r.get("filePath") or r.get("path") or r.get("savedPath")
        for _ in range(20):
            if src and os.path.exists(src):
                break
            time.sleep(0.5)
        dst = os.path.join(out, name + ".png")
        if src and os.path.exists(src):
            shutil.copyfile(src, dst)
            res[name] = dst
        else:
            res[name] = "FAILED %s" % json.dumps(r)[:200]
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--stage", action="store_true")
    ap.add_argument("--shots", default=None)
    ap.add_argument("--save", default=None)
    ap.add_argument("--labels", action="store_true", help="re-pin the labels and sign books only")
    a = ap.parse_args(argv)
    K = stations()
    if a.plan:
        rects = sum((complement(r, keep_rects(K)) for r in (HR.REGION, HR.REGION2, HR.STALE_WEST)), [])
        print(json.dumps({"keep": keep_rects(K), "clear_rects": len(rects), "labels": len(label_ops(K)),
                          "cards": {k: v["rect"] for k, v in cards(K).items()}}))
        return 0
    import run_live as RL  # noqa: E402  (python.exe)
    B = RL.LiveBridge()
    mi = B.call("jawa/map_info")
    if mi.get("sizeX") != 250:
        print(json.dumps({"error": "expected the 250x250 walk map", "map": {k: mi.get(k) for k in ("sizeX", "success")}}))
        return 2
    rc = 0
    if a.stage:
        B.call("rimworld/pause_game", pause=True)
        B.call("jawa/weather_set", weather="Clear", lockWeather=True)
        B.call("jawa/incident_queue_clear")
        swept = B.call("jawa/destroy_bulk", filter="nonColonists", dryRun=False).get("matchedCount")
        n = clear_rest(B, K)
        build_switch_trio(B)
        run2 = build_second_run(B)
        B.call("jawa/review_label", action="clear", tag=TAG)
        lab = B.call("jawa/review_label", action="add", ops="\n".join(label_ops(K)), tag=TAG)
        sg = RM.place_signs(B, sign_ops(K))
        B.ticks(600)                                  # every net finishes switching its consumers on (human_review T4)
        B.call("jawa/destroy_bulk", filter="nonColonists", dryRun=False)
        paused, tick = pause(B)
        rd, bad = reads(B, K)
        if run2["fails"]:
            bad.append("second run placements refused: %s" % run2["fails"][:4])
        if not paused:
            bad.append("game not paused")
        print(json.dumps({"cleared_rects": n, "swept_pawns": swept, "second_run": run2, "labels": lab.get("success"),
                          "signs": sg.get("count"), "paused": paused, "ticksGame": tick, "reads": rd, "bad": bad}, default=str))
        rc = 1 if bad else 0
    if a.labels:
        B.call("jawa/review_label", action="clear", tag=TAG)
        lab = B.call("jawa/review_label", action="add", ops="\n".join(label_ops(K)), tag=TAG)
        sg = RM.place_signs(B, sign_ops(K))
        print(json.dumps({"labels": lab.get("success"), "signs": sg.get("count")}))
    if a.shots:
        print(json.dumps({"shots": shots(B, K, a.shots)}))
    if a.save:
        r = RM.save_keeper(B, a.save, signs="\n".join(label_ops(K)))
        print(json.dumps({"save": r}, default=str))
        rc = rc or (0 if r.get("ok") else 1)
    return rc


if __name__ == "__main__":
    sys.exit(main())
