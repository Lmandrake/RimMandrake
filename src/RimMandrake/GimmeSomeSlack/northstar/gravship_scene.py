#!/usr/bin/env python3
"""gravship_scene.py -- does a span strung on a gravship stay up through the flight, and do its cords come with it? (sc_gravship,
keepWiresOnGravship; a live launch on a scratch quicktest, the origin map is destroyed.)

    python.exe src/RimMandrake/GimmeSomeSlack/northstar/gravship_scene.py on|off|off_autolink [--shot NAME] [--out RESULT.json]

Flies bridgetools/prove_gravship.py's own ship (its recipe knows every engine gate), staged as scenes.json sc_gravship asks: two wall
brackets on walls aboard joined by a span, a battery and two consumers (lamps) on one floor run (one net, asserted before the launch),
and a pole aboard strung to a pole left on the ground. off_autolink is the off flight with the auto-link setting at its default (on) from
take-off to the read: landing must not string the wires again (f6be36c45e).
Reads, after landing: the bracket span up (on) or taken down (off, off_autolink), the ground span gone, the battery and both consumers
still one net, and every cord true to the landed grid: each end on a net of this map, both ends on the same one (true_to_grid, worked out
here from the map's own nets, not from the cord census's counters). The planted control, every flight: the cord set read BEFORE the launch
goes through the same read against the landed map and must fail by name. Exit 0/1/2: PASS/FAIL/UNMEASURED.
--out writes two rows of a result JSON (script/started/mode/rows, the shape mod_completion.py folds): the flight's row (ROW_IDS[mode], class
MOD when measured, HARNESS when the scene could not ask) and the control's (ROW_IDS["control"]).
"""
import argparse
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
PROVE = os.path.join(REPO, "src", "RimMandrake", "bridgetools", "prove_gravship.py")
sys.path.insert(0, os.path.join(HERE, "..", "northstar_matrix"))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
sys.path.insert(0, os.path.dirname(PROVE))
SHOTS = r"D:\ClaudeWork\rimmandrake\ralph_gss\shots"
ROW_IDS = {"on": "GS1_keep_wires_on_gravship_on_aboard_span_flies", "off": "GS1_keep_wires_on_gravship_off_aboard_span_taken_down",
           "off_autolink": "GS3_auto_link_on_keep_wires_off_span_stays_down", "control": "GS2_prelaunch_cords_fail_on_landed_map"}


def cord_edges(census):
    """[(name, (x, z), (x, z))] of a cord census: the edge names carry their end cells ("bend:12,40|end:19,40")."""
    out = []
    for name in sorted((census or {}).get("edgeHashes") or {}):
        cells = []
        for end in name.split("|"):
            try:
                x, z = end.rsplit(":", 1)[1].split(",")
                cells.append((int(x), int(z)))
            except (IndexError, ValueError):
                pass
        out.append((name, cells[0] if len(cells) == 2 else None, cells[1] if len(cells) == 2 else None))
    return out


def true_to_grid(edges, net_of):
    """The true-to-grid read of a cord set against a map: [(cord name, fault)]. net_of(cell) -> the net id there, or None for no net."""
    bad = []
    for name, a, b in edges:
        if a is None:
            bad.append((name, "its end cells could not be read from its name"))
            continue
        na, nb = net_of(a), net_of(b)
        out = [c for c, n in ((a, na), (b, nb)) if n is None]
        if out:
            bad.append((name, "ends outside the landed net: %s" % (out,)))
        elif na != nb:
            bad.append((name, "joins two nets"))
    return bad


def cell_net(n):
    """The net of one cell of AerialProbe's net: read: the transmitted net there, else the net of the device that stands there (a lamp
    wired to a battery by vanilla's own link stands on no transmitted net: seen live 2026-11-24). None: no net, or no read."""
    if not n.get("success"):
        return None
    got = [n.get("net")] + [t.get("net") for t in n.get("things") or []]
    return next((v for v in got if v not in (None, -1)), None)


def in_other_walls(total, own):
    """Cord vertices in a wall that is not a bracket's own: the census total less the count read in each aboard bracket's home wall cell
    (the cord of a wall bracket ends at its foot on that wall, under the bracket). None: a count could not be read."""
    if total is None or any(v is None for v in own):
        return None
    return total - sum(own)


def control_verdict(before_edges, net_of):
    """-> (status, class, detail): the pre-launch cord set against the landed map must fail by name on an end outside the landed net."""
    bad = true_to_grid(before_edges, net_of)
    outside = [x for x in bad if "outside the landed net" in x[1]]
    d = {"prelaunchCords": len(before_edges), "failByName": outside[:4], "faults": len(bad)}
    if not before_edges:
        return "UNMEASURED", "HARNESS", dict(d, why="no cord was read before the launch")
    if not outside and not bad:
        return "UNMEASURED", "SITE", dict(d, why="every pre-launch cord end stands on a net of the landed map: the ship came down on the cells it left")
    return ("PASS" if outside else "FAIL"), "HARNESS", d


def one_net(reads, consumers=2):
    """(True/False/None, detail): the battery and every consumer are on one net. `reads`: [(name, net id or None)], battery first."""
    if len(reads) != 1 + consumers or any(n is None for _, n in reads):
        return None, reads
    return len({n for _, n in reads}) == 1 and reads[0][1] != -1, reads


def flight_verdict(mode, up_aboard, to_ground, spans_up, grid, edges, net_ok, unwalkable):
    """-> [why not] of a measured landing ([] = PASS)."""
    out = []
    if up_aboard != (mode == "on"):
        out.append("the bracket span is %s after the landing" % ("up" if up_aboard else "down"))
    if to_ground:
        out.append("a link to the pole left on the ground is kept")
    if mode != "on" and spans_up:
        out.append("%s span(s) up after a landing with keep wires off" % spans_up)
    if not edges:
        out.append("no cord on the landed map")
    out += ["%s: %s" % x for x in grid[:6]]
    if net_ok is False:
        out.append("the battery and the consumers are not one net after the landing")
    if unwalkable:
        out.append("%s cord vertices in a wall" % unwalkable)
    return out


SNAP_ROW = "GS4_ground_wire_snaps_at_launch"     # bar ship_to_ground_wire_snaps (0.2.0); its own row, beside ROW_IDS: no other check reads it


def fallen_of(census, aid):
    """How many fallen wires hang from one anchor in an aerial census. None: the census did not answer or does not hold the anchor."""
    if not (census or {}).get("success"):
        return None
    got = [q for q in census.get("anchors") or [] if q.get("id") == aid]
    return len(got[0].get("fallen") or []) if got else None


def snap_verdict(before, left_behind, stump):
    """-> (status, class, detail). before: fallen wires at (ground anchor, ship pole) before the launch; left_behind: at the ground anchor
    right after the ship's things lifted, None when it could not be read; stump: at the ship's pole after the landing. The wire from the
    ship to the ground snaps: one half lies at the ground anchor, the other hangs from the ship's pole where the ship lands."""
    d = {"fallenBefore": before, "groundAnchorAfterLaunch": left_behind, "shipPoleAfterLanding": stump}
    if None in before or left_behind is None or stump is None:
        return "UNMEASURED", "HARNESS", dict(d, why="a fallen-wire count could not be read")
    if before != (0, 0):
        return "UNMEASURED", "SITE", dict(d, why="a fallen wire hung there before the launch")
    return ("PASS" if left_behind == 1 and stump == 1 else "FAIL"), "MOD", d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("on", "off", "off_autolink"))
    ap.add_argument("--shot", default=None)
    ap.add_argument("--out", default=None, help="write the verdict row as a result JSON here")
    a = ap.parse_args()
    started = time.strftime("%Y-%m-%dT%H:%M:%S")
    det = {"setting": "keepWiresOnGravship", "value": a.mode == "on"}
    rc = None
    try:
        rc = scene(a, det)
    except SystemExit as e:  # prove_gravship's need() refused the staging: the scene could not ask (visit 2, 2026-11-19: no row at all)
        det["error"] = "staging refused (prove_gravship need() exit %s): see the FAIL: line above" % (e.code,)
        rc = 2
    except Exception as e:   # noqa: BLE001  (a crash is a verdict too: written, then raised)
        det["error"] = "%s: %s" % (type(e).__name__, e)
        rc = None
        raise
    finally:
        if a.out:
            st, cl = {0: ("PASS", "MOD"), 1: ("FAIL", "MOD")}.get(rc, ("UNMEASURED", "HARNESS"))
            c_st, c_cl, c_det = det.pop("control", None) or ("UNMEASURED", "HARNESS", "the flight did not reach its landed read")
            s_st, s_cl, s_det = det.pop("snap", None) or ("UNMEASURED", "HARNESS", "the flight did not reach its landed read")
            with open(a.out, "w", encoding="utf-8") as f:
                json.dump({"mod": "GimmeSomeSlack", "script": "gravship_scene.py", "mode": "live", "started": started,
                           "rows": [{"id": ROW_IDS[a.mode], "status": st, "class": cl, "detail": det}, {"id": ROW_IDS["control"], "status": c_st, "class": c_cl, "detail": c_det},
                                    {"id": SNAP_ROW, "status": s_st, "class": s_cl, "detail": s_det}]},
                          f, indent=1, default=str)
            print("wrote", a.out)
    return rc


def scene(a, det):
    src = open(PROVE, encoding="utf-8").read()
    head, rest = src.split("# -- 5. launch", 1)
    g = {"__file__": PROVE, "__name__": "prove_gravship_scene"}
    exec(compile(head, PROVE, "exec"), g)                    # authors the ship, refuels, walks the colonists aboard
    import run_live as RL
    B = RL.LiveBridge()
    X, Z = g["X"], g["Z"]
    st = {"B": B}   # the bridge in use: the land step makes a new one
    try:
        B.call("rimworld/set_god_mode", enabled=True)
        B.ap("set:keepWiresOnGravship=%s" % ("True" if a.mode == "on" else "False"))
        B.ap("set:autoLink=False")
        brackets = [(X + 3, Z + 17), (X + 16, Z + 17)]           # each on the south face of its own wall
        pole, ground = (X + 1, Z + 14), (X + 1, Z + 24)
        B.call("jawa/destroy_batch", rects="%d,%d,3,3" % (ground[0] - 1, ground[1] - 1), categories="Plant,Item,Filth,Building")
        B.call("jawa/set_terrain_batch", ops="Soil:%d,%d,3,3" % (ground[0] - 1, ground[1] - 1))
        B.call("jawa/build_batch", ops=";".join("Wall:%d,%d" % (x, z + 1) for x, z in brackets), stuff="Steel", faction="player", wipeExisting=False)
        for c in brackets:
            B.ap("place:RM_AerialWallBracket:Industrial:%d,%d:0:god" % c)
        for c in (pole, ground):
            B.ap("place:RM_AerialMast:Industrial:%d,%d:god" % c)
        for x in range(X + 3, X + 11):
            B.ap("cplace:PowerConduit:Industrial:%d,%d:god" % (x, Z + 16))
        B.ap("cprocess")
        consumers = [(X + 9, Z + 15), (X + 12, Z + 15)]
        B.call("jawa/build_batch", ops="Battery:%d,%d,0;" % (X + 6, Z + 14) + ";".join("StandingLamp:%d,%d" % c for c in consumers), faction="player", wipeExisting=False)
        B.ticks(3)
        pad = "%d,%d,20,20" % (X, Z)
        for t in B.call("jawa/list_things", defName="Battery", rect=pad, limit=20).get("things") or []:
            B.call("jawa/battery_set", thing=t.get("id") or t.get("thingId"), mode="setPct", value=1.0)
        B.ticks(3)

        def devices(ids=None):
            """[(ThingID, (x, z))] of the battery and the consumers: on the pad before the launch, by id anywhere after it."""
            out = []
            for d in ("Battery", "StandingLamp"):
                kw = {"rect": pad} if ids is None else {}
                out += [(t.get("id") or t.get("thingId"), (t["x"], t["z"])) for t in B.call("jawa/list_things", defName=d, limit=200, **kw).get("things") or []
                        if ids is None or (t.get("id") or t.get("thingId")) in ids]
            return out

        def nets(devs):
            out = []
            for tid, (x, z) in devs:
                got = [t for t in B.ap("net:%d,%d" % (x, z)).get("things") or [] if str(tid).endswith(str(t.get("id")))]
                out.append((tid, got[0].get("net") if got else None))
            return out
        devs = devices()
        apos = {(q["x"], q["z"]): q["id"] for q in B.ap("census").get("anchors") or []}
        ids = [apos.get(c) for c in brackets + [pole, ground]]
        if None in ids:
            print("UNMEASURED: the brackets or poles did not build: %s %s" % (ids, sorted(apos)))
            det["unmeasured"] = "the brackets or poles did not build"
            return 2
        ok_net, reads = one_net(nets(devs))
        det["netBefore"] = reads
        if not ok_net:
            print("UNMEASURED: the battery and two consumers are not one net before the launch: %s" % (reads,))
            det["unmeasured"] = "the battery and two consumers are not one net before the launch"
            return 2
        print("links", B.ap("link:%d,%d" % (ids[0], ids[1])).get("verdict"), B.ap("link:%d,%d" % (ids[2], ids[3])).get("verdict"))
        B.call("rimworld/set_god_mode", enabled=False)
        B.ticks(2)
        B.probe("rebuild")
        before, cords_before = B.ap("census"), cord_edges(B.probe("census"))
        if a.mode == "off_autolink":
            B.ap("set:autoLink=True")
        g["call"]("rimworld/step_game_ticks", ticks=60)
        tail = "# -- 5. launch" + rest.split("# -- 6. land", 1)[0] + "# -- 6. land" + rest.split("# -- 6. land", 1)[1].split("for part in", 1)[0]
        lift, cut, travel = tail.partition("deadline = time.time()")
        exec(compile(lift, PROVE, "exec"), g)                    # launch: the cutscene starts; the ship's things despawn a few frames on
        left, t0, polls = {"success": False, "error": "the ship's pole never left the origin map in 60 s"}, time.time(), []
        while time.time() - t0 < 60:                             # a hang guard: the lift is a few seconds of wall clock
            try:
                c = B.ap("census")
            except Exception as e:   # noqa: BLE001  (the flight's own verdict does not rest on this read)
                c = {"success": False, "error": str(e)[:200]}
            polls.append((round(time.time() - t0, 1), fallen_of(c, ids[3]), fallen_of(c, ids[2])))
            if fallen_of(c, ids[3]) is not None and fallen_of(c, ids[2]) is None:
                left = c                                         # the ground anchor still stands, the ship's pole is gone
                break
            if fallen_of(c, ids[3]) is None:
                break                                            # the origin map is no longer the current map: not read
            time.sleep(0.5)
        print("snap polls (s, ground anchor, ship pole)", polls[:1] + polls[-3:], len(polls))
        exec(compile(cut + travel, PROVE, "exec"), g)            # travel, land
        B = st["B"] = RL.LiveBridge()
        B.ticks(30)
        B.probe("rebuild")
        after = B.ap("census")
        anchors = after.get("anchors") or []
        links = [(q["id"], l.get("other"), l.get("state")) for q in anchors for l in q.get("links") or []]
        up_aboard = any(i in ids[:2] and o in ids[:2] and st_ == "Up" for i, o, st_ in links)
        to_ground = any(ids[3] in (i, o) or o == -1 for i, o, _ in links)
        gr = B.probe("census")
        lay = {k: gr.get(k) for k in ("cordEdges", "cordsAcrossNets", "verticesInUnwalkable", "conduitCells")}
        # a failed census reads as no anchors and zero counters: measured only when both censuses answered and both spans
        # were up before the launch (Codex review 2026-11-09)
        measured = bool(after.get("success")) and bool(gr.get("success")) and before.get("spansUp") == 2 and len(anchors) >= 3
        if not measured:
            why = {"before": before.get("spansUp"), "after": after.get("success"), "graph": gr.get("success"), "anchors": len(anchors)}
            print("UNMEASURED: census failed or the spans were not up before launch: %s" % json.dumps(why))
            det["unmeasured"] = why
            return 2
        det["snap"] = snap_verdict((fallen_of(before, ids[3]), fallen_of(before, ids[2])), fallen_of(left, ids[3]), fallen_of(after, ids[2]))
        print("snap", json.dumps(det["snap"], default=str), {k: left.get(k) for k in ("error", "fallenCords")})
        cache = {}

        def net_of(c):
            if c not in cache:
                n = B.ap("net:%d,%d" % c)
                cache[c] = cell_net(n)
            return cache[c]
        edges = cord_edges(gr)
        grid = true_to_grid(edges, net_of)
        det["control"] = control_verdict(cords_before, net_of)
        net_ok, reads = one_net(nets(devices({t for t, _ in devs})))
        if net_ok is None:
            print("UNMEASURED: the battery or a consumer was not found on the landed map: %s" % (reads,))
            det["unmeasured"] = "the battery or a consumer was not found on the landed map: %s" % (reads,)
            return 2
        home = [(q["x"], q["z"] + 1) for q in anchors if q["id"] in ids[:2]]      # the walls of the two brackets, each on a south face
        own = [B.probe("rect:%d,%d,1,1" % c).get("verticesInUnwalkable") for c in home]
        walls = in_other_walls(gr.get("verticesInUnwalkable"), own)
        if walls is None or len(home) != 2:
            print("UNMEASURED: the cord vertices at the brackets' walls could not be read: %s %s" % (home, own))
            det["unmeasured"] = "the cord vertices at the brackets' walls could not be read"
            return 2
        lay["inBracketWalls"] = own
        why = flight_verdict(a.mode, up_aboard, to_ground, after.get("spansUp"), grid, edges, net_ok, walls)
        ok = not why
        det.update({"mode": a.mode, "before": {"spansUp": before.get("spansUp")}, "after": {"spansUp": after.get("spansUp"), "spansCut": after.get("spansCut")},
                    "aboardSpanUp": up_aboard, "groundLinkKept": to_ground, "cords": lay, "links": links, "ids": ids, "netAfter": reads,
                    "cordsRead": len(edges), "whyNot": why, "verdict": "PASS" if ok else "FAIL"})
        print(json.dumps(det, default=str))
        if a.shot:
            q = next((p for p in anchors if p["id"] == ids[0]), None)
            if q:
                res = B.call("rimworld/screenshot_cell_rect", x=q["x"] - 4, z=q["z"] - 6, width=24, height=14, paddingCells=1, fileName=a.shot)
                src_ = res.get("filePath") or res.get("path") or res.get("savedPath")
                for _ in range(30):
                    if src_ and os.path.exists(src_) and os.path.getsize(src_) > 0:
                        break
                    time.sleep(0.5)
                time.sleep(1)
                if src_ and os.path.exists(src_):
                    shutil.copyfile(src_, os.path.join(SHOTS, a.shot + ".png"))
                    print(os.path.join(SHOTS, a.shot + ".png"))
        if ok and det["control"][0] != "PASS":    # a pass the read could not have failed is no pass
            det["unmeasured"] = "the control did not fail by name on the landed map, so the read is not trusted: %s" % (det["control"][2],)
            return 2
        return 0 if ok else 1
    finally:   # every exit, the early UNMEASURED return and exceptions too, puts the settings back (Codex review 2026-11-09)
        for f in (lambda: st["B"].call("rimworld/set_god_mode", enabled=False),
                  lambda: st["B"].ap("set:keepWiresOnGravship=True"), lambda: st["B"].ap("set:autoLink=True")):
            try:
                f()
            except Exception as e:   # noqa: BLE001  (restore what can be restored)
                print("restore failed: %s" % e)


if __name__ == "__main__":
    sys.exit(main())
