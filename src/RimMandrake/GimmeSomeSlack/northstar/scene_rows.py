#!/usr/bin/env python3
"""The controls design/concepts/GimmeSomeSlack/scenes.json asks for that the proof's other blocks did not run: each row here is a real
case in a real site, where the mod has to behave differently from the case the older row measured. A control that needs a debug flag
in the mod only to prove the instrument is left out on purpose; see ralph/DONE.md for the per-scene call.

proof_all.py runs this as the "scenes" block. One site, west of everything else, reset per scene.
"""
import time

SC0 = (14, 165)                    # its own plot: the matrix REGION ends at z=112, style at x=98, aerial starts at x=88
SITE = (SC0[0] - 2, SC0[1] - 2, 66, 40)
ROWS = ["SC_doorway_run_is_one_cord", "SC_cut_never_powered_both_dead", "SC_cut_battery_each_side_both_live", "SC_bend_draws_no_joint_tee_draws_one", "SC_sparse_room_no_tangle",
        "SC_cords_all_slack", "SC_no_two_cords_alike", "SC_restring_drafted_no_job", "SC_restring_work_scheduler_takes_it",
        "SC_splicer_spared_bystander_shocked", "SC_dead_wire_shocks_nobody", "SC_dead_wire_lights_no_fuel"]


def _site(B, V):
    r = "%d,%d,%d,%d" % SITE
    B.call("jawa/destroy_batch", rects=r, categories="All")
    B.call("jawa/set_terrain_batch", ops="Soil:" + r, clearOverlays=True)
    B.call("jawa/set_fog", action="unfog", rect=r)
    B.call("jawa/set_roof_batch", ops="None:" + r)
    B.call("jawa/map_commit")


def _line(x0, z0, x1, z1):
    if x0 == x1:
        return [(x0, z) for z in range(min(z0, z1), max(z0, z1) + 1)]
    return [(x, z0) for x in range(min(x0, x1), max(x0, x1) + 1)]


def _rect(B, x, z, w, h):
    B.probe("rebuild")
    return B.probe("rect:%d,%d,%d,%d" % (x, z, w, h))


def _ends(c):
    return {tuple(e["cell"]): e for e in c.get("ends") or []}


def _fill(B, rect):
    for t in B.call("jawa/list_things", defName="Battery", rect="%d,%d,%d,%d" % rect, limit=20).get("things") or []:
        B.call("jawa/battery_set", thing=t.get("id") or t.get("thingId"), mode="setPct", value=1.0)


def doorway(B, V, rows):
    """Owner 2026-11-07, three cables out of a doorway to one conduit end: at the shipped settings one connection is one cord."""
    x, z = SC0
    _site(B, V)
    room = [c for c in _line(x + 8, z, x + 8, z + 10) + _line(x + 8, z, x + 18, z) + _line(x + 8, z + 10, x + 18, z + 10) + _line(x + 18, z, x + 18, z + 10) if c != (x + 8, z + 5)]
    B.call("jawa/build_batch", ops=V.ops("Wall", room), stuff="Steel", faction="player", wipeExisting=False)
    B.call("jawa/build_batch", ops="Door:%d,%d,1" % (x + 8, z + 5), stuff="Steel", faction="player", wipeExisting=False)
    B.call("jawa/build_batch", ops=V.ops("PowerConduit", _line(x, z + 5, x + 14, z + 5)), faction="player", wipeExisting=False)
    B.ticks(3)
    c = _rect(B, x - 2, z - 2, 24, 16)
    n, e = c.get("strands"), c.get("cordEdges")
    V.row(rows, "SC_doorway_run_is_one_cord", "PASS" if e and n == e else "FAIL", "MOD", {"strands": n, "cordEdges": e})


def cut_ends(B, V, rows):
    """sc_cut_ends: the row M8 only reads a line with one battery. Never powered: both dead. A battery each side: both live."""
    x, z = SC0
    _site(B, V)
    # never powered, cut in the middle
    B.call("jawa/build_batch", ops=V.ops("PowerConduit", _line(x, z, x + 12, z)), faction="player", wipeExisting=False)
    B.ticks(3)
    B.call("jawa/destroy_batch", rects="%d,%d,1,1" % (x + 6, z), categories="Building")
    B.ticks(2)
    B.probe("poll")
    ends = _ends(_rect(B, x - 1, z - 3, 15, 7))
    w, e = ends.get((x + 5, z)), ends.get((x + 7, z))
    ok = bool(w and e) and w.get("registryLive") is False and e.get("registryLive") is False
    V.row(rows, "SC_cut_never_powered_both_dead", "PASS" if ok else "FAIL", "MOD", {"west": w, "east": e})
    # a battery on each side, cut in the middle
    z2 = z + 12
    B.call("jawa/build_batch", ops=V.ops("PowerConduit", _line(x, z2, x + 12, z2)), faction="player", wipeExisting=False)
    B.call("jawa/build_batch", ops="Battery:%d,%d,0;Battery:%d,%d,0" % (x - 0, z2 + 1, x + 11, z2 + 1), faction="player", wipeExisting=False)
    B.ticks(3)
    _fill(B, (x - 2, z2 - 2, 18, 6))
    B.ticks(3)
    B.call("jawa/destroy_batch", rects="%d,%d,1,1" % (x + 6, z2), categories="Building")
    B.ticks(2)
    B.probe("poll")
    ends = _ends(_rect(B, x - 1, z2 - 3, 15, 7))
    w, e = ends.get((x + 5, z2)), ends.get((x + 7, z2))
    ok = bool(w and e) and w.get("registryLive") is True and e.get("registryLive") is True
    V.row(rows, "SC_cut_battery_each_side_both_live", "PASS" if ok else "FAIL", "MOD", {"west": w, "east": e})


def joints(B, V, rows):
    """sc_junction_strips and sc_dense_tangle's control, in the Modern look: a bend draws no joining piece, a tee one long strip; a
    sparse room no tangle, a block one."""
    x, z = SC0
    _site(B, V)
    B.ap("cclearpicks")

    def lay(cells):
        for c in cells:
            B.ap("cplace:PowerConduit:Modern_Multi:%d,%d:god" % c)
            B.ap("cprocess")
        B.ticks(3)

    def strips(c):
        d = c.get("decals") or {}
        return sum(v for k, v in d.items() if k.startswith("PowerStrip"))
    lay(_line(x, z, x + 8, z) + _line(x + 8, z, x + 8, z + 8))             # an L
    bend = _rect(B, x - 1, z - 2, 12, 12)
    z2, x2 = z + 14, x + 20
    lay(_line(x2, z2, x2 + 12, z2) + _line(x2 + 6, z2, x2 + 6, z2 + 7))     # a T
    tee = _rect(B, x2 - 1, z2 - 2, 15, 12)
    bend_n = [n["t"] for n in bend.get("nodes") or []]
    tee_n = [n["t"] for n in tee.get("nodes") or []]
    ok = strips(bend) == 0 and strips(tee) == 1 and not any("junction" in t.lower() for t in bend_n) and any("junction" in t.lower() for t in tee_n)
    V.row(rows, "SC_bend_draws_no_joint_tee_draws_one", "PASS" if ok else "FAIL", "MOD",
          {"bend": {"decals": bend.get("decals"), "nodes": bend_n}, "tee": {"decals": tee.get("decals"), "nodes": tee_n}})
    # the sparse room: three separated lines side by side; the block: 5 x 5
    tangles = lambda: B.probe("motion").get("tangles", 0)   # noqa: E731
    t0 = tangles()
    x3, z3 = x + 40, z
    B.call("jawa/build_batch", ops=V.ops("PowerConduit", _line(x3, z3, x3 + 10, z3) + _line(x3, z3 + 4, x3 + 10, z3 + 4) + _line(x3, z3 + 8, x3 + 10, z3 + 8)),
           faction="player", wipeExisting=False)
    B.ticks(3)
    B.probe("rebuild")
    t1 = tangles()
    B.call("jawa/build_batch", ops=V.ops("PowerConduit", [(x3 + i, z3 + 14 + j) for i in range(5) for j in range(5)]), faction="player", wipeExisting=False)
    B.ticks(3)
    B.probe("rebuild")
    t2 = tangles()
    V.row(rows, "SC_sparse_room_no_tangle", "PASS" if t1 == t0 and t2 == t1 + 1 else "FAIL", "MOD", {"before": t0, "afterSparse": t1, "afterBlock": t2})


def slack_and_shapes(B, V, rows):
    """never_taut_straight_cord and sc_no_repeat on everything now laid on the map, which by now is the matrix, core, style and aerial sites."""
    s = B.probe("slack")
    bad = s.get("under115")
    n = s.get("strands") or 0
    if not n:
        V.row(rows, "SC_cords_all_slack", "UNMEASURED", "HARNESS", s)
    else:
        V.row(rows, "SC_cords_all_slack", "PASS" if bad == 0 else "FAIL", "MOD", s)
    t = B.probe("shapetable")
    cl = t.get("classes") or []
    if not cl:
        V.row(rows, "SC_no_two_cords_alike", "UNMEASURED", "HARNESS", t)
    else:
        alike = sum(c.get("tooAlike") or 0 for c in cl)
        pairs = sum(c.get("pairs") or 0 for c in cl)
        V.row(rows, "SC_no_two_cords_alike", "UNMEASURED" if not pairs else ("PASS" if alike == 0 else "FAIL"), "MOD", {"tooAlike": alike, "pairs": pairs, "classes": cl})


def _span(B, V, a, b, batt):
    """Two masts (and a charged battery on conduit from the first, if asked), linked and then cut. -> (id a, id b, live half of a's fallen, its tip cell)"""
    from validation_aerial import anchors_by_pos
    B.call("jawa/build_batch", ops=V.ops("RM_AerialMast", [a, b]), faction="player", wipeExisting=False)
    if batt:
        B.call("jawa/build_batch", ops=V.ops("PowerConduit", _line(a[0], a[1] + 1, a[0], batt[1] - 1)), faction="player", wipeExisting=False)
        B.call("jawa/build_batch", ops="Battery:%d,%d,0" % batt, faction="player", wipeExisting=False)
    B.call("jawa/map_commit")
    B.ticks(3)
    if batt:
        _fill(B, (batt[0] - 2, batt[1] - 2, 5, 5))
        B.ticks(3)
    ap = anchors_by_pos(B.ap("census"))
    ia, ib = ap[a]["id"], ap[b]["id"]
    if not any(l.get("state") == "Up" for l in ap[a].get("links") or []):
        B.ap("link:%d,%d" % (ia, ib))
        B.ticks(2)
    B.ap("cut:%d,%d" % (ia, ib))
    B.ticks(3)
    B.ap("poll")
    f = anchors_by_pos(B.ap("census")).get(a) or {}
    half = next((q for q in f.get("fallen") or [] if q.get("cutPartner", -1) != -1), None)
    tip = (int(half["tip"][0] // 1), int(half["tip"][1] // 1)) if half else None
    return ia, ib, f.get("fallenLive"), tip


def restring(B, V, rows):
    """sc_restring's control, then the road M15e skips: the work scheduler itself gives a free colonist the job."""
    x, z = SC0
    _site(B, V)
    from validation_aerial import _wire_trial
    home = {p["id"]: p.get("pos") for p in B.probe("colonists").get("pawns") or []}
    ia, ib, live, tip = _span(B, V, (x + 2, z + 4), (x + 16, z + 4), None)
    for pid in home:
        B.probe("pawn:%d=draft" % pid)
    o = B.ap("restringorder:%d" % ia)
    B.ticks(600)
    st = B.ap("restringstate:%d" % ia)
    al = B.ap("alert")
    ok = o.get("designated") and st.get("cut", 0) >= 1 and al.get("down", 0) >= 1
    V.row(rows, "SC_restring_drafted_no_job", "PASS" if ok else "FAIL", "MOD", {"order": o, "after600": st, "alert": al.get("down"),
                                                                              "meaning": "PASS = every colonist drafted, the order stands and nobody splices"})
    # the builders free to work, standing by: which of them has Construction switched on is the quicktest's roll. The wire is dead for this, so a
    # free pawn who wanders across it is safe; the live wire comes next.
    def builds(i):
        sk = (B.call("jawa/pawn_get", pawn=i).get("pawns") or [{}])[0].get("skills") or []
        return any(q.get("skill") == "Construction" and not q.get("disabled") for q in sk)
    free = [i for i in home if builds(i)]
    B.hold_off = True
    for i in free:
        B.probe("pawn:%d=tp:%d,%d" % (i, x + 8, z + 12))
        B.probe("pawn:%d=undraft" % i)
        B.call("jawa/pawn_need", pawn=i, action="need", need="Rest", level=1.0)
        B.call("jawa/pawn_need", pawn=i, action="need", need="Food", level=1.0)
    played, st1 = 0, st
    while free and played < 3000 and st1.get("cut", 0) >= 1:
        B.ticks(250)
        played += 250
        st1 = B.ap("restringstate:%d" % ia)
    ok = st1.get("cut") == 0 and st1.get("jobsDone", 0) > st.get("jobsDone", 0)
    V.row(rows, "SC_restring_work_scheduler_takes_it", "UNMEASURED" if not free else ("PASS" if ok else "FAIL"), "MOD",
          {"freed": free, "played": played, "before": st, "after": st1})
    B.hold_off = False
    for p, pos in home.items():
        if pos:
            B.probe("pawn:%d=tp:%d,%d" % (p, pos[0], pos[1]))
        B.probe("pawn:%d=draft" % p)

    B.call("jawa/build_batch", ops=V.ops("PowerConduit", _line(x + 2, z + 5, x + 2, z + 7)), faction="player", wipeExisting=False)
    B.call("jawa/build_batch", ops="Battery:%d,%d,0" % (x + 2, z + 8), faction="player", wipeExisting=False)
    B.ticks(3)
    _fill(B, (x, z + 6, 5, 5))
    B.ticks(3)

    # sc_shock_restring: the splicer on the job stands on the live wire of that cut, unharmed; an animal on the same cell is down
    B.ap("cut:%d,%d" % (ia, ib))
    B.ticks(3)
    B.ap("poll")
    from validation_aerial import anchors_by_pos
    f = anchors_by_pos(B.ap("census")).get((x + 2, z + 4)) or {}
    half = next((q for q in f.get("fallen") or [] if q.get("cutPartner", -1) != -1), None)
    if not half or not f.get("fallenLive"):
        V.row(rows, "SC_splicer_spared_bystander_shocked", "UNMEASURED", "SITE", f)
    else:
        tp = (int(half["tip"][0] // 1), int(half["tip"][1] // 1))
        # stood on the wire FIRST: the tp verb stops all jobs. The job goes to whoever is nearest the anchor, now that colonist.
        moved = bool(free) and B.probe("pawn:%d=tp:%d,%d" % (free[0], tp[0], tp[1])).get("success")
        j = B.ap("restringjob:%d" % ia)
        by = "".join(ch for ch in str(j.get("by")) if ch.isdigit())
        moved = moved and by == str(free[0])
        a = _wire_trial(B, tp, settle=8)
        hed = (B.call("jawa/pawn_get", pawn=int(by)).get("pawns") or [{}])[0].get("hediffs") or [] if by else []
        spared = not any(h.get("def") == "RM_FallenWireShock" for h in hed)
        crossed = bool(moved)
        status = "UNMEASURED" if not (crossed and by) or a.get("error") else ("PASS" if spared and a.get("shocked") else "FAIL")
        V.row(rows, "SC_splicer_spared_bystander_shocked", status, "MOD", {"job": j, "stoodOnWire": moved, "tip": tp, "bystander": a, "splicerHediffs": [h.get("def") for h in hed]})
        for _ in range(8):
            B.ticks(100)
            if B.ap("restringstate:%d" % ia).get("cut", 1) == 0:
                break
        for p, pos in home.items():
            if pos:
                B.probe("pawn:%d=tp:%d,%d" % (p, pos[0], pos[1]))
            B.probe("pawn:%d=draft" % p)


def dead_wire(B, V, rows):
    """sc_shock and sc_fuel_ignition's control: the same wire, its source empty. The switches stay on: only the power differs."""
    x, z = SC0
    _site(B, V)
    from validation_aerial import _wire_trial
    for k, v in (("fallenWireShock", "True"), ("fallenWireIgnites", "True"), ("fallenWireKnockback", "0")):
        B.ap("set:%s=%s" % (k, v))
    batt = (x + 2, z + 8)
    _, _, live, tip = _span(B, V, (x + 2, z + 4), (x + 16, z + 4), batt)
    if not live or not tip:
        V.row(rows, "SC_dead_wire_shocks_nobody", "UNMEASURED", "SITE", {"live": live, "tip": tip})
        V.row(rows, "SC_dead_wire_lights_no_fuel", "UNMEASURED", "SITE", {"live": live, "tip": tip})
        B.ap("set:fallenWireKnockback=2")
        return
    B.ticks(250)
    hot = _wire_trial(B, tip)
    r = "%d,%d,%d,%d" % (batt[0] - 2, batt[1] - 2, 5, 5)
    for t in B.call("jawa/list_things", defName="Battery", rect=r, limit=5).get("things") or []:
        B.call("jawa/battery_set", thing=t.get("id") or t.get("thingId"), mode="setPct", value=0.0)
    B.ticks(260)
    B.ap("poll")
    cold = _wire_trial(B, tip)
    status = "UNMEASURED" if hot.get("error") or cold.get("error") else ("PASS" if hot.get("shocked") and cold.get("shocked") is False else "FAIL")
    V.row(rows, "SC_dead_wire_shocks_nobody", status, "MOD", {"live": hot, "dead": cold})
    B.call("jawa/destroy_batch", rects="%d,%d,1,1" % tip, categories="All")
    fires = 0
    for _ in range(12):
        B.call("rimworld/spawn_thing", defName="Filth_Fuel", stackCount=1, x=tip[0], z=tip[1])
        B.ticks(250)
        fires = max(fires, len(B.call("jawa/list_things", defName="Fire", rect="%d,%d,3,3" % (tip[0] - 1, tip[1] - 1), limit=5).get("things") or []))
    V.row(rows, "SC_dead_wire_lights_no_fuel", "PASS" if fires == 0 else "FAIL", "MOD", {"fires": fires, "sweeps": 12, "note": "live, M20c lights it; P(miss in 12) = 0.6%"})
    B.ap("set:fallenWireKnockback=2")


def run(B, V, rows):
    slack_and_shapes(B, V, rows)
    doorway(B, V, rows)
    cut_ends(B, V, rows)
    joints(B, V, rows)
    restring(B, V, rows)
    dead_wire(B, V, rows)
    B.call("jawa/destroy_batch", rects="%d,%d,%d,%d" % SITE, categories="All")
    time.sleep(0.2)


def statics_new_game(B, V, rows):
    """sc_statics_new_game, the last thing a run does because it ends the map: the session tables hold a pick, a second game starts, and they
    are empty. The filled read before it is the control: an empty table before the second game measures nothing."""
    x, z = SC0
    B.ap("cplace:PowerConduit:Industrial:%d,%d:god" % (x, z))
    before = B.probe("statics")
    B.call("rimworld/go_to_main_menu")
    B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    from await_lifecycle import await_lifecycle
    lc = await_lifecycle(B.call, "map_ready", 240, poll_s=0.5)
    if not lc.ok:
        V.row(rows, "SC_statics_clear_between_games", "UNMEASURED", "HARNESS", lc.reason)
        return
    after = B.probe("statics")
    if not before.get("conduitPick"):
        V.row(rows, "SC_statics_clear_between_games", "UNMEASURED", "HARNESS", {"before": before, "meaning": "the pick never filled"})
    else:
        ok = after.get("resets", 0) > before.get("resets", 0) and not after.get("conduitPick") and after.get("taps") == 0 and after.get("skipReseed") is False
        V.row(rows, "SC_statics_clear_between_games", "PASS" if ok else "FAIL", "MOD", {"before": before, "after": after})
