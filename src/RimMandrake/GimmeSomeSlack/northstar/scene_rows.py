#!/usr/bin/env python3
"""The controls design/concepts/GimmeSomeSlack/scenes.json asks for that the proof's other blocks did not run: each row here is a real
case in a real site, where the mod has to behave differently from the case the older row measured. A control that needs a debug flag
in the mod only to prove the instrument is left out on purpose; see ralph/DONE.md for the per-scene call.

proof_all.py runs this as the "scenes" block. One site, west of everything else, reset per scene.
"""
import time

SC0 = (14, 165)                    # its own plot: the matrix REGION ends at z=112, style at x=98, aerial starts at x=88
SITE = (SC0[0] - 2, SC0[1] - 2, 66, 40)
SC_ALIKE_MIN_CELLS = 3             # SC_no_two_cords_alike judges length classes of 3 cells and up (owner, by card 2026-11-13)
ROWS = ["SC_doorway_run_is_one_cord", "SC_cut_never_powered_both_dead", "SC_cut_battery_each_side_both_live", "SC_bend_draws_no_joint_tee_draws_one", "SC_sparse_room_no_tangle",
        "SC_cords_all_slack", "SC_no_two_cords_alike", "SC_restring_drafted_no_job", "SC_restring_work_scheduler_takes_it",
        "SC_splicer_spared_bystander_shocked", "SC_dead_wire_shocks_nobody", "SC_dead_wire_lights_no_fuel",
        # sc_floor_end_shock and sc_shock_reach (RIMMANDRAKE_BUILD_GSS_FLOOR_END_SHOCK_ANSWERED_WEEK_AGO, Stage 3 2026-11-14)
        "SC_floor_end_live_shocks", "SC_floor_end_dead_spares", "SC_floor_end_cord_behind_spares", "SC_floor_end_unfinished_run_bites",
        "SC_floor_end_bites_aerial_master_off", "SC_floor_end_every_end_over_spark_budget", "SC_floor_end_fixer_spared_other_builder_shocked",
        "SC_shock_reach_default_all", "SC_shock_reach_three_values", "SC_shock_reach_deck_cord_per_value",
        # sc_cords_under_items (bar cords_draw_under_things, owner by card 2026-11-14)
        "SC_under_battery_dry", "SC_under_item_stack_dry", "SC_under_furniture_dry", "SC_under_junction_piece_dry", "SC_under_liquid_pit",
        # end_kind_and_slope (RIMMANDRAKE_FIX_SLACK_CORD_ENDS_OWNER_CAUGHT_TWO, owner look 2026-11-16)
        "SC_cord_end_one_kind", "SC_box_stub_slope"]


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
        # owner, by card 2026-11-13: cords shorter than 3 cells are exempt (little room for two short cords to differ);
        # `length` is the C# length class (CordShape.Table), so a class below 3 is skipped. selftest_gss_no_two_alike_short.py
        judged = [c for c in cl if (c.get("length") or 0) >= SC_ALIKE_MIN_CELLS]
        alike = sum(c.get("tooAlike") or 0 for c in judged)
        pairs = sum(c.get("pairs") or 0 for c in judged)
        V.row(rows, "SC_no_two_cords_alike", "UNMEASURED" if not pairs else ("PASS" if alike == 0 else "FAIL"), "MOD",
              {"tooAlike": alike, "pairs": pairs, "classes": judged, "exemptShorterThan": SC_ALIKE_MIN_CELLS,
               "exempt": [c for c in cl if c not in judged]})


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


def drafted_control_observed(roster, replies):
    pawns = roster.get("pawns")
    return (roster.get("success") is True and isinstance(pawns, list) and bool(pawns)
            and all(isinstance(p, dict) and p.get("id") is not None
                    and replies.get(p["id"], {}).get("success") is True
                    and replies[p["id"]].get("pawn", {}).get("id") == p["id"]
                    and replies[p["id"]].get("pawn", {}).get("drafted") is True for p in pawns))


def restring(B, V, rows):
    """sc_restring's control, then the road M15e skips: the work scheduler itself gives a free colonist the job."""
    x, z = SC0
    _site(B, V)
    from validation_aerial import _wire_trial
    roster = B.probe("colonists")
    home = {p["id"]: p.get("pos") for p in roster.get("pawns") or [] if isinstance(p, dict) and p.get("id") is not None}
    ia, ib, live, tip = _span(B, V, (x + 2, z + 4), (x + 16, z + 4), None)
    drafts = {pid: B.probe("pawn:%d=draft" % pid) for pid in home}
    o = B.ap("restringorder:%d" % ia)
    B.ticks(600)
    st = B.ap("restringstate:%d" % ia)
    al = B.ap("alert")
    ok = o.get("designated") and st.get("cut", 0) >= 1 and al.get("down", 0) >= 1
    measured = drafted_control_observed(roster, drafts)
    V.row(rows, "SC_restring_drafted_no_job", ("PASS" if ok else "FAIL") if measured else "UNMEASURED", "MOD" if measured else "HARNESS",
          {"order": o, "after600": st, "alert": al.get("down"), "roster": roster, "drafts": drafts,
                                                                              "meaning": "PASS = every colonist drafted, the order stands and nobody splices"})
    # the builders free to work, standing by: which of them has Construction switched on is the quicktest's roll. The wire is dead for this, so a
    # free pawn who wanders across it is safe; the live wire comes next.
    def builds(i):
        sk = (B.call("jawa/pawn_get", pawn=i).get("pawns") or [{}])[0].get("skills") or []
        return any(q.get("skill") == "Construction" and not q.get("disabled") for q in sk)
    free = [i for i in home if builds(i)]
    previous_hold_off = B.hold_off
    try:
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
        why = None if ok else B.ap("restringwhy:%d" % ia)
        V.row(rows, "SC_restring_work_scheduler_takes_it", "UNMEASURED" if not free else ("PASS" if ok else "FAIL"), "MOD",
              {"freed": free, "played": played, "before": st, "after": st1, "why": why})
    finally:
        B.hold_off = previous_hold_off
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
        pg = B.call("jawa/pawn_get", pawn=int(by)) if by else {}
        pawns = pg.get("pawns") or []
        seen = bool(pawns) and isinstance(pawns[0].get("hediffs"), list)   # a failed read is no health observed, not "spared"
        hed = pawns[0].get("hediffs") if seen else []
        spared = not any(h.get("def") == "RM_FallenWireShock" for h in hed)
        crossed = bool(moved)
        status = "UNMEASURED" if not (crossed and by and seen) or a.get("error") else ("PASS" if spared and a.get("shocked") else "FAIL")
        V.row(rows, "SC_splicer_spared_bystander_shocked", status, "MOD", {"job": j, "stoodOnWire": moved, "tip": tp, "bystander": a, "splicerHediffs": [h.get("def") for h in hed]})
        for _ in range(8):
            B.ticks(100)
            if B.ap("restringstate:%d" % ia).get("cut", 1) == 0:
                break
        for p, pos in home.items():
            if pos:
                B.probe("pawn:%d=tp:%d,%d" % (p, pos[0], pos[1]))
            B.probe("pawn:%d=draft" % p)


def ignition_control(B, tip, sweeps=12, stop_on_fire=False):
    """A missing fuel placement or fire observation measures no ignition control."""
    fires, observations = 0, []
    for _ in range(sweeps):
        fuel = B.call("rimworld/spawn_thing", defName="Filth_Fuel", stackCount=1, x=tip[0], z=tip[1])
        B.ticks(250)
        query = B.call("jawa/list_things", defName="Fire", rect="%d,%d,3,3" % (tip[0] - 1, tip[1] - 1), limit=5)
        seen = query.get("success") is True and isinstance(query.get("things"), list)
        count = len(query["things"]) if seen else None
        observations.append({"fuel": fuel.get("success") is True, "fires": count})
        if seen:
            fires = max(fires, count)
            if fires and stop_on_fire:
                break
    measured = bool(observations) and all(o["fuel"] and o["fires"] is not None for o in observations)
    return ("PASS" if fires == 0 else "FAIL") if measured else "UNMEASURED", {"fires": fires, "sweeps": len(observations), "observations": observations}


def dead_wire(B, V, rows):
    """sc_shock and sc_fuel_ignition's control: the same wire, its source empty. The switches stay on: only the power differs."""
    x, z = SC0
    _site(B, V)
    from validation_aerial import _wire_trial
    for k, v in (("shockReach", "All"), ("fallenWireIgnites", "True"), ("fallenWireKnockback", "0")):
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
    status, observed = ignition_control(B, tip)
    V.row(rows, "SC_dead_wire_lights_no_fuel", status, "HARNESS" if status == "UNMEASURED" else "MOD",
          dict(observed, note="live, M20c lights it; P(miss in 12) = 0.6%"))
    B.ap("set:fallenWireKnockback=2")


def _trial(B, cell):
    """A downed animal on `cell` (validation_aerial._wire_trial): {"shocked": bool, ...}, or {"error": ...} when it never ran."""
    from validation_aerial import _wire_trial
    return _wire_trial(B, cell)


def _verdict(trials, want):
    """PASS when every trial ran and read `want` shocked-ness; UNMEASURED HARNESS when one never ran."""
    if any("error" in t for t in trials):
        return "UNMEASURED", "HARNESS"
    return ("PASS" if all(t.get("shocked") is want for t in trials) else "FAIL"), "MOD"


def _cut_run(B, V, z, cut=True):
    """A battery-fed floor run on row z, west to east, x..x+12: cut at x+6 (live end x+5, dead end x+7, a lamp past the cut keeps
    the east half a real run) or, with cut=False, simply stopped at x+8 (its loose end live). -> the probe's ends by cell."""
    x = SC0[0]
    B.call("jawa/build_batch", ops=V.ops("PowerConduit", _line(x, z, x + (12 if cut else 8), z)), faction="player", wipeExisting=False)
    B.call("jawa/build_batch", ops="Battery:%d,%d,0" % (x, z + 1), faction="player", wipeExisting=False)
    if cut:
        B.call("jawa/build_batch", ops="StandingLamp:%d,%d,0" % (x + 12, z + 1), faction="player", wipeExisting=False)
    B.ticks(3)
    _fill(B, (x - 2, z - 2, 18, 6))
    B.ticks(3)
    if cut:
        B.call("jawa/destroy_batch", rects="%d,%d,1,1" % (x + 6, z), categories="Building")
        B.ticks(2)
    B.probe("poll")
    B.ticks(8)                     # FloorEndShock rebuilds its contacts after the poll, on its next 4-tick check
    return _ends(_rect(B, x - 1, z - 3, 15, 7))


def fixer_verdict(fixer, other):
    """SC_floor_end_fixer_spared_other_builder_shocked from the two trials -> status. Each trial: {"onEnd": the colonist stood on the
    live end's cell, "job": his job's def, "target": the cell of the blueprint the job delivers to, "shocked": bool}. PASS when the one
    whose job targets the blueprint on the cut cell stood on the live end unharmed and the one whose job targets a blueprint elsewhere
    was shocked there. A trial that did not put the man on the cell with the job, or did not read his health, measures nothing."""
    def ran(t):
        return isinstance(t, dict) and t.get("onEnd") is True and bool(t.get("job")) and isinstance(t.get("shocked"), bool) and t.get("target")
    if not (ran(fixer) and ran(other)):
        return "UNMEASURED"
    return "PASS" if fixer["shocked"] is False and other["shocked"] is True else "FAIL"


def fixer_and_other_builder(B, V, end, cut, far):
    """The live floor end at `end` faces the destroyed cell `cut`. A conduit blueprint goes on `cut` and another on `far` (six cells
    off), steel beside each. A colonist is put on the end's cell and ordered to deliver steel to the blueprint on the cut cell (the
    job the game gives a constructor: HaulToContainer, the blueprint its target B): he is the fixer of THIS end and must not be shocked
    (FloorEndShock.FixingThisEnd). A second is put on the same cell with the same job to the far blueprint: a builder like him, of
    something else, and is shocked. Both are read over the ticks their order waits, before they have walked off the cell."""
    roster = B.probe("colonists")
    ids = [p["id"] for p in roster.get("pawns") or [] if isinstance(p, dict) and p.get("id") is not None]

    def hauls(i):
        sk = (B.call("jawa/pawn_get", pawn=i).get("pawns") or [{}])[0].get("skills") or []
        return any(q.get("skill") == "Construction" and not q.get("disabled") for q in sk)
    free = [i for i in ids if hauls(i)]
    if len(free) < 2:
        return "UNMEASURED", "SITE", {"why": "fewer than two colonists who can do Construction on this map", "roster": roster}
    home = {p["id"]: p.get("pos") for p in roster.get("pawns") or [] if isinstance(p, dict) and p.get("id") in free[:2]}
    placed = {}
    for name, c in (("cut", cut), ("far", far)):
        r = B.call("jawa/blueprint_place", **{"def": "PowerConduit", "x": c[0], "z": c[1], "faction": "Player"}) or {}
        placed[name] = {"cell": list(c), "id": (r.get("blueprint") or {}).get("id") or r.get("thingId") or r.get("id"),
                        "raw": {k: r.get(k) for k in ("success", "error", "message", "placementCheck")}}
    steel = {}
    for name, c in (("cut", (end[0], end[1] + 1)), ("far", (end[0], end[1] - 1))):
        r = B.call("rimworld/spawn_thing", defName="Steel", stackCount=5, x=c[0], z=c[1]) or {}
        # rimworld/spawn_thing names the stack "Thing_Steel123"; the job tool takes the game's own ThingID, "Steel123"
        steel[name] = str(r.get("thingId") or r.get("id") or (r.get("thing") or {}).get("id") or "").replace("Thing_", "", 1) or None
    B.probe("poll")
    B.ticks(8)
    if not (placed["cut"]["id"] and placed["far"]["id"] and steel["cut"] and steel["far"]):
        return "UNMEASURED", "HARNESS", {"why": "a blueprint or its steel was not placed (or its id not returned)", "placed": placed, "steel": steel}
    trials = {}
    previous_hold_off = getattr(B, "hold_off", False)
    try:
        B.hold_off = True
        for who, pid, name in (("fixer", free[0], "cut"), ("other", free[1], "far")):
            B.probe("pawn:%d=undraft" % pid)
            moved = B.probe("pawn:%d=tp:%d,%d" % (pid, end[0], end[1]))
            # the order is given with the game paused (the bridge holds it), then six ticks are played: one of the shock's 4-tick
            # checks falls inside them, the man one step at most off the cell he was put on
            j = B.call("jawa/ordered_job", pawnId=str(pid), jobDef="HaulToContainer", targetAId=str(steel[name]), targetBId=str(placed[name]["id"]),
                       count=1, waitTicks=0) or {}
            running = j.get("success") is True and j.get("nowRunningRequested") is True
            stop = None
            try:
                B.ticks(6)
            except Exception as ex:      # the tick governor stops the clock when a colonist goes down: here that is the shock itself
                stop = repr(ex)[:200]
            pg = (B.call("jawa/pawn_get", pawn=pid).get("pawns") or [{}])[0]
            hed = pg.get("hediffs")
            # stood up again before anything else ticks (the governor refuses to run a clock over a downed colonist)
            healed = B.call("jawa/pawn_health", pawn=str(pid), action="healAll", confirmDestructive=True) or {}
            trials[who] = {"pawn": pid, "onEnd": bool(moved.get("success")), "job": j.get("afterJobDef") if running else None,
                           "target": placed[name]["cell"], "accepted": j.get("success"),
                           "order": {k: j.get(k) for k in ("success", "accepted", "message", "afterJobDef", "nowRunningRequested")},
                           "shocked": ("RM_FallenWireShock" in [h.get("def") for h in hed]) if isinstance(hed, list) else None, "posAfter": pg.get("pos"),
                           "clockStopped": stop, "healed": healed.get("success")}
            B.probe("pawn:%d=tp:%d,%d" % (pid, end[0] - 3, end[1] + 4))      # off the end before the next man stands on it
    finally:
        B.hold_off = previous_hold_off
        for pid, pos in home.items():
            if pos:
                B.probe("pawn:%d=tp:%d,%d" % (pid, pos[0], pos[1]))
            B.probe("pawn:%d=draft" % pid)
    st = fixer_verdict(trials.get("fixer"), trials.get("other"))
    return st, ("MOD" if st != "UNMEASURED" else "HARNESS"), {"end": list(end), "blueprints": placed, "steel": steel, "trials": trials,
                                                                "meaning": "PASS = the man fixing this end stood on it unharmed; the man building elsewhere was shocked on it"}


def floor_end_shock(B, V, rows):
    """sc_floor_end_shock (leaves floor_end_shocks_crossers, inventory floor_end_shock): only the live end cell bites, every live end
    bites whatever the spark budget, the overhead-lines master does not gate it, and the constructor joining THIS end is spared.
    The crossers are downed animals put on the cell (no path to assert: the pawn is on the cell or the trial errs)."""
    x, z = SC0
    _site(B, V)
    B.ap("set:shockReach=All")
    B.ap("set:fallenWireKnockback=0")             # a thrown pawn would leave the cell the next trial reads
    ends = _cut_run(B, V, z)
    w, e = ends.get((x + 5, z)), ends.get((x + 7, z))
    if not (w and e and w.get("registryLive") is True and e.get("registryLive") is False):
        for r in ("SC_floor_end_live_shocks", "SC_floor_end_dead_spares", "SC_floor_end_cord_behind_spares", "SC_floor_end_bites_aerial_master_off"):
            V.row(rows, r, "UNMEASURED", "SITE", {"west": w, "east": e, "why": "the cut did not leave a live west end and a dead east end"})
    else:
        t = _trial(B, (x + 5, z))
        V.row(rows, "SC_floor_end_live_shocks", *_verdict([t], True), {"trial": t})
        t = _trial(B, (x + 7, z))
        V.row(rows, "SC_floor_end_dead_spares", *_verdict([t], False), {"trial": t})
        t = _trial(B, (x + 3, z))
        V.row(rows, "SC_floor_end_cord_behind_spares", *_verdict([t], False), {"trial": t, "cell": "two back from the live end"})
        B.ap("set:enabled=False")
        B.ticks(8)
        t = _trial(B, (x + 5, z))
        B.ap("set:enabled=True")
        V.row(rows, "SC_floor_end_bites_aerial_master_off", *_verdict([t], True), {"trial": t})
    # a run the player stopped laying: its loose end is live and bites the same way
    ends = _cut_run(B, V, z + 8, cut=False)
    loose = ends.get((x + 8, z + 8))
    if not (loose and loose.get("registryLive") is True):
        V.row(rows, "SC_floor_end_unfinished_run_bites", "UNMEASURED", "SITE", {"end": loose})
        V.row(rows, "SC_floor_end_every_end_over_spark_budget", "UNMEASURED", "SITE", {"end": loose})
    else:
        t = _trial(B, (x + 8, z + 8))
        V.row(rows, "SC_floor_end_unfinished_run_bites", *_verdict([t], True), {"trial": t})
        # two live ends, the spark budget at 1: both still bite (the shock reads every end, not the spark set)
        B.probe("set:maxSparkingEnds=1")
        B.ticks(8)
        ts = [_trial(B, (x + 5, z)), _trial(B, (x + 8, z + 8))]
        B.probe("set:maxSparkingEnds=24")
        V.row(rows, "SC_floor_end_every_end_over_spark_budget", *_verdict(ts, True), {"trials": ts})
    # the fixer: a colonist whose job delivers to the conduit blueprint on the destroyed cell, and one delivering to a blueprint elsewhere
    st, cause, detail = fixer_and_other_builder(B, V, (x + 5, z), (x + 6, z), (x + 6, z - 6))
    V.row(rows, "SC_floor_end_fixer_spared_other_builder_shocked", st, cause, detail)
    B.ap("set:fallenWireKnockback=2")


DECK_WANT = {"All": True, "OnlyDownedLines": True, "None": False}


def _colonists(B):
    """id -> position of every colonist on the map (the probe's roster); {} when the roster cannot be read."""
    ro = B.probe("colonists") if hasattr(B, "probe") else {}
    return {p["id"]: p.get("pos") for p in (ro or {}).get("pawns") or [] if isinstance(p, dict) and p.get("id") is not None}


def _rescue(B, before):
    """The colonist a collapse trial spawned on the fallen deck is healed, walked off the wire and drafted beside the colony's own:
    left lying on a live cord he goes down again, and the tick governor then stops every later clock (first run of this row,
    2026-11-17: three trial colonists down, the next scene's 8 ticks refused)."""
    if not before:
        return
    hx, hz = next((p for p in before.values() if p), (5, 5))
    for k, pid in enumerate(sorted(set(_colonists(B)) - set(before))):
        B.call("jawa/pawn_health", pawn=str(pid), action="healAll", confirmDestructive=True)
        B.probe("pawn:%d=tp:%d,%d" % (pid, hx + 2 + k, hz + 2))
        B.probe("pawn:%d=draft" % pid)


def deck_verdict(seen):
    """SC_shock_reach_deck_cord_per_value from one collapse per value -> status. seen[value] = {"fell": the deck's live cord really
    fell (FlowWorks dropped its cords and the net split once), "shocked": the colonist standing on a fallen square carries the shock}.
    The cord a collapsed deck drops is a downed line: it bites under All and Only downed lines, never under None. A value whose
    collapse did not drop a live cord measures nothing."""
    if set(seen) != set(DECK_WANT) or any(not isinstance(v, dict) or v.get("fell") is not True or not isinstance(v.get("shocked"), bool) for v in seen.values()):
        return "UNMEASURED"
    return "PASS" if all(seen[v]["shocked"] is w for v, w in DECK_WANT.items()) else "FAIL"


def deck_cord_per_value(B, V, run_collapse=None):
    """The FlowWorks half of sc_shock_reach, on tier gimmesomeslack_flowworks: FlowWorks' own lines_proof row COLLAPSE_CORD_SHOCKS_ONCE
    (a powered cord across a timber deck, the span collapsed by the production CollapseSpan, a colonist on a fallen square) run once
    per shockReach value on its own plot, read by its counters and the colonist's health, not by that row's own verdict (which
    expects a shock, the default). Without FlowWorks the row is UNMEASURED SITE with this driver named."""
    probe = B.call("jawa/flowworks_excavation_drive", x=2, z=2, deepenLevels=0, setBodyWaterM=-1) or {}
    if probe.get("success") is False or "error" in probe:
        return "UNMEASURED", "SITE", {"why": "FlowWorks is not loaded (jawa/flowworks_excavation_drive refused): run on tier gimmesomeslack_flowworks, "
                                             "`proof_all.py --live --skip-offline --only scenes`", "read": probe}
    if run_collapse is None:
        def run_collapse(origin):
            import json
            import os
            import sys
            import tempfile
            fw = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "FlowWorks", "northstar")
            if fw not in sys.path:
                sys.path.insert(0, fw)
            import lines_proof as LP
            out = os.path.join(tempfile.gettempdir(), "gss_deck_cord_%d_%d.json" % origin)
            LP.main([out, "--only", "COLLAPSE_CORD_SHOCKS_ONCE", "--origin", "%d,%d" % origin])
            with open(out, encoding="utf-8") as f:
                rws = json.load(f).get("rows") or []
            return next((r for r in rws if r.get("id") == "COLLAPSE_CORD_SHOCKS_ONCE"), None)
    seen, raw = {}, {}
    before = _colonists(B)
    try:
        for i, v in enumerate(DECK_WANT):
            B.ap("set:shockReach=%s" % v)
            B.ticks(8)
            r = run_collapse((150 + 25 * i, 120)) or {}
            _rescue(B, before)
            d = r.get("detail") if isinstance(r.get("detail"), dict) else {}
            raw[v] = {"status": r.get("status"), "class": r.get("class"), "detail": d}
            fell = (d.get("cordsDropped") or 0) >= 4 and d.get("liveFalls60") == 1 and (d.get("liveHalves") or 0) >= 1
            hed = d.get("hediffs")
            seen[v] = {"fell": bool(fell), "shocked": ("RM_FallenWireShock" in hed) if isinstance(hed, list) else None, "shocks": d.get("shocks")}
    finally:
        B.ap("set:shockReach=All")
    st = deck_verdict(seen)
    return st, ("MOD" if st != "UNMEASURED" else "SITE"), {"seen": seen, "want": DECK_WANT, "collapseRows": raw}


def shock_reach(B, V, rows):
    """sc_shock_reach (leaf shock_reach_setting): the default is All; per value, the floor end bites only under All, a live fallen
    wire under All and Only downed lines, nothing under None; no restart between values. The FlowWorks deck cord half runs on
    the gimmesomeslack_flowworks tier (FlowWorks' lines_proof collapse row, under each value)."""
    x, z = SC0
    got = B.call("jawa/mod_settings_field", typeName="RimMandrake.GimmeSomeSlack.Aerial.AerialSettings", action="get", field="shockReach") or {}
    V.row(rows, "SC_shock_reach_default_all", "PASS" if str(got.get("value")) == "All" else "FAIL" if got.get("value") else "UNMEASURED",
          "MOD" if got.get("value") else "HARNESS", {"read": got, "note": "read before any poke; a fresh settings file is a SITE fact"})
    _site(B, V)
    B.ap("set:fallenWireKnockback=0")
    ends = _cut_run(B, V, z)
    _, _, live, tip = _span(B, V, (x + 2, z + 14), (x + 16, z + 14), (x + 2, z + 20))
    if not ((ends.get((x + 5, z)) or {}).get("registryLive") is True and live and tip):
        V.row(rows, "SC_shock_reach_three_values", "UNMEASURED", "SITE", {"floorEnd": ends.get((x + 5, z)), "wireLive": live, "tip": tip})
    else:
        want = {"All": (True, True), "OnlyDownedLines": (False, True), "None": (False, False)}
        seen, ran = {}, True
        for v, (floor, wire) in want.items():
            B.ap("set:shockReach=%s" % v)
            B.ticks(8)
            tf, tw = _trial(B, (x + 5, z)), _trial(B, tip)
            ran = ran and "error" not in tf and "error" not in tw
            seen[v] = {"floorEnd": tf.get("shocked"), "fallenWire": tw.get("shocked")}
        ok = all(seen[v] == {"floorEnd": f, "fallenWire": w} for v, (f, w) in want.items())
        V.row(rows, "SC_shock_reach_three_values", ("PASS" if ok else "FAIL") if ran else "UNMEASURED", "MOD" if ran else "HARNESS",
              {"seen": seen, "want": {v: {"floorEnd": f, "fallenWire": w} for v, (f, w) in want.items()}})
    B.ap("set:shockReach=All")
    B.ap("set:fallenWireKnockback=2")
    st, cause, detail = deck_cord_per_value(B, V)
    V.row(rows, "SC_shock_reach_deck_cord_per_value", st, cause, detail)


UNDER_ROWS = ["SC_under_battery_dry", "SC_under_item_stack_dry", "SC_under_furniture_dry", "SC_under_junction_piece_dry", "SC_under_liquid_pit"]


def under_verdict(read, want_piece=False):
    """One cell of the probe's `under:x,z` read -> (status, cause, detail). PASS when a cord lies there (a junction piece, if
    `want_piece`) and every thing standing on the cell draws above it: the cord's altitude below the thing's, and, for a thing
    that writes no depth, its queue (the piece's for a junction) no later than the thing's. UNMEASURED SITE when the cell holds no cord or no thing; FAIL otherwise."""
    if not read or not read.get("success"):
        return "UNMEASURED", "HARNESS", {"read": read, "why": "the probe's under: verb gave no reading"}
    cord, things = read.get("cord") or {}, [t for t in read.get("things") or [] if t.get("def") != "PowerConduit"]
    have = cord.get("pieces", 0) > 0 if want_piece else cord.get("strands", 0) + cord.get("pieces", 0) > 0
    if not have or not things:
        return "UNMEASURED", "SITE", {"read": read, "why": "no %s on the cell, or nothing standing on it" % ("junction piece" if want_piece else "cord")}
    q = cord.get("pieceQueue") if want_piece else max(cord.get("strandQueue", -1), cord.get("pieceQueue", -1) if cord.get("pieces") else -1)
    # a thing that writes depth (a Cutout thing: a stack of steel, a table, a battery) hides the cord under it whichever is queued
    # first, the cord lying at the lower altitude: the queue clause is for things that write none (Transparent). In-game visit 1 failed
    # a junction piece queued 2901 under steel queued 2900 on the queues alone, while its own pictures (stackz, tablez, junctionz)
    # show the cord passing under the steel and the table: RIMMANDRAKE_RULE_SLACK_UNDER_CHECK_IGNORES_DEPTH_WRITE.
    over = [t for t in things if not (cord.get("altitude", 99) < t.get("altitude", -99)
                                      and (t.get("queue", -1) < 0 or q <= t["queue"] or t.get("depth") is True))]
    return ("FAIL" if over else "PASS"), "MOD", {"cord": cord, "things": things, "drawnUnderCord": [t["def"] for t in over]}


def pit_verdict(dry, wet, deep, under_battery, water_stubs):
    """SC_under_liquid_pit from its readings -> (status, detail). A cord on dry ground shows whole (seen 1). The same run on the floor
    of a pit under wadeable liquid (1 m) still lies there and shows through it, less than whole (seen < 1), and the battery standing
    on that floor draws above it (under_verdict). Under 2 m or more (FlowWorks' "deep water") no cord lies on the water at all: the
    run dives at the banks (two water stubs) as it does under vanilla deep water (a cord drawn across deep pit water was
    RIMMANDRAKE_BURY_GSS_CORDS_IN_FW_SUPERDEEP_PIT_WATER)."""
    def seen(r):
        return ((r or {}).get("cord") or {}).get("seen")

    def strands(r):
        return ((r or {}).get("cord") or {}).get("strands")
    d = {"seen": {"dry": seen(dry), "underLiquid": seen(wet)}, "strands": {"dry": strands(dry), "underLiquid": strands(wet), "underDeep": strands(deep)},
         "battery": under_battery, "waterStubs": water_stubs}
    if None in d["seen"].values() or None in d["strands"].values() or not isinstance(water_stubs, int) or not d["strands"]["dry"]:
        return "UNMEASURED", dict(d, why="a reading is missing, or no cord lies on the dry cell")
    if not d["strands"]["underLiquid"]:
        return "UNMEASURED", dict(d, why="no cord lies on the floor of the wadeable pit: the site did not stage the case (the pit read as deep, or the run went round)")
    ok = d["seen"]["dry"] == 1 and d["seen"]["underLiquid"] < 1 and under_battery == "PASS" and d["strands"]["underDeep"] == 0 and water_stubs >= 2
    return ("PASS" if ok else "FAIL"), d


def under_liquid_pit(B, V, at):
    """The pit half of sc_cords_under_items, on a tier with FlowWorks (gimmesomeslack_flowworks): a battery-fed run crosses two pits
    dug five levels down, the first filled 1 m (wadeable) with a battery standing on its floor on the run, the second 2 m (FlowWorks'
    "deep water (2 m or more)"); the probe's under: read at a dry cell, a cell of each pit and the pit battery's, and the census's
    water stubs. Two pits, three cells of ground between them: one body of liquid has one level. Without FlowWorks the row is
    UNMEASURED SITE with this driver named."""
    x, z = at
    probe = B.call("jawa/flowworks_excavation_drive", x=x + 3, z=z, deepenLevels=0, setBodyWaterM=-1) or {}
    if probe.get("success") is False or "error" in probe:
        return "UNMEASURED", "SITE", {"why": "FlowWorks is not loaded (jawa/flowworks_excavation_drive refused): run on tier gimmesomeslack_flowworks, "
                                             "`proof_all.py --live --skip-offline --only scenes`", "read": probe}
    stubs0 = ((B.probe("census") or {}).get("nodeTypes") or {}).get("stub_water", 0)
    shallow = [(x + i, z + j) for i in range(3, 6) for j in (-1, 0, 1)]
    deep = [(x + i, z + j) for i in range(9, 12) for j in (-1, 0, 1)]
    built = {"dug": 0}
    for c in shallow + deep:
        r = B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=5, setBodyWaterM=-1) or {}
        built["dug"] += 1 if r.get("success") is not False else 0
    built["pitBattery"] = B.call("jawa/build_batch", ops="Battery:%d,%d,0" % (x + 4, z), faction="player", wipeExisting=False).get("placed")
    built["battery"] = B.call("jawa/build_batch", ops="Battery:%d,%d,0" % (x, z), faction="player", wipeExisting=False).get("placed")
    built["conduit"] = B.call("jawa/build_batch", ops=V.ops("PowerConduit", _line(x, z, x + 14, z)), faction="player", wipeExisting=False).get("placed")
    B.call("jawa/build_batch", ops="StandingLamp:%d,%d,0" % (x + 14, z + 1), faction="player", wipeExisting=False)
    fill = {"shallow": B.call("jawa/flowworks_excavation_drive", x=shallow[0][0], z=shallow[0][1], setBodyWaterM=1.0),
            "deep": B.call("jawa/flowworks_excavation_drive", x=deep[0][0], z=deep[0][1], setBodyWaterM=2.0)}
    B.ticks(3)
    _fill(B, (x - 1, z - 2, 17, 5))
    B.probe("rebuild")
    B.ticks(8)
    dry, wet, dp = (B.probe("under:%d,%d" % c) for c in ((x + 1, z), (x + 3, z), (x + 10, z)))
    bat = under_verdict(B.probe("under:%d,%d" % (x + 4, z)))
    stubs = ((B.probe("census") or {}).get("nodeTypes") or {}).get("stub_water", 0) - stubs0
    st, detail = pit_verdict(dry, wet, dp, bat[0], stubs)
    detail.update(built=built, cells={"dry": [x + 1, z], "underLiquid": [x + 3, z], "underDeep": [x + 10, z], "battery": [x + 4, z]},
                  fill={k: {q: (v or {}).get(q) for q in ("success", "error", "bodyWaterM", "waterM")} for k, v in fill.items()},
                  reads={"dry": dry, "underLiquid": wet, "underDeep": dp, "battery": bat[2]})
    return st, ("MOD" if st != "UNMEASURED" else "SITE"), detail


def cords_under_items(B, V, rows):
    """sc_cords_under_items (bar cords_draw_under_things): a battery-fed floor run with a battery standing on it, a stack of steel and a
    bed lying across it and a three-way junction with steel on the joint; at each such cell the probe's under: read must show the
    thing drawn above the cord (under_verdict). The pit half needs FlowWorks: on any other tier it is UNMEASURED with its driver."""
    # Stage 6 visit 1 (2026-11-16, SITE): a cord routes AROUND a table or a stack lying on a straight run (measured: no strand
    # under a 3x3 table on the run, and the stack on the run was missed in one of two lays), and build_batch refuses a battery
    # on a conduit cell (wipeExisting=false). So the battery goes down first, and the stack and the table each sit on a
    # conduit dead end, a cell the cord's end must reach: branch (x+3, z-1..z-3) ends under the stack, (x+8, z+1..z+3) under
    # the table centred one cell past its tip.
    x, z = SC0
    _site(B, V)
    run = _line(x, z, x + 12, z)
    built = {"battery": B.call("jawa/build_batch", ops="Battery:%d,%d,0" % (x, z), faction="player", wipeExisting=False).get("placed")}
    built["conduit"] = B.call("jawa/build_batch", ops=V.ops("PowerConduit", run + _line(x + 8, z + 1, x + 8, z + 3) + _line(x + 3, z - 3, x + 3, z - 1)),
                              faction="player", wipeExisting=False).get("placed")
    B.call("jawa/build_batch", ops="StandingLamp:%d,%d,0" % (x + 12, z + 1), faction="player", wipeExisting=False)
    built["table"] = B.call("jawa/build_batch", ops="Table3x3c:%d,%d,0" % (x + 8, z + 4), stuff="WoodLog", faction="player",
                            wipeExisting=False).get("placed")
    B.call("rimworld/spawn_thing", defName="Steel", stackCount=75, x=x + 3, z=z - 3)
    B.call("rimworld/spawn_thing", defName="Steel", stackCount=40, x=x + 8, z=z)
    B.ticks(3)
    _fill(B, (x - 2, z - 5, 18, 12))
    B.probe("rebuild")
    B.ticks(8)
    for rid, cell, piece in (("SC_under_battery_dry", (x, z), False), ("SC_under_item_stack_dry", (x + 3, z - 3), False),
                             ("SC_under_furniture_dry", (x + 8, z + 3), False), ("SC_under_junction_piece_dry", (x + 8, z), True)):
        st, cause, detail = under_verdict(B.probe("under:%d,%d" % cell), want_piece=piece)
        detail["cell"] = list(cell)
        detail["built"] = built
        V.row(rows, rid, st, cause, detail)
    st, cause, detail = under_liquid_pit(B, V, (x + 16, z - 3))
    V.row(rows, "SC_under_liquid_pit", st, cause, detail)
    B.call("jawa/destroy_batch", rects="%d,%d,%d,%d" % SITE, categories="All")


def end_kind_and_slope(B, V, rows):
    """RIMMANDRAKE_FIX_SLACK_CORD_ENDS_OWNER_CAUGHT_TWO (owner, live look 2026-11-16 ~5:46 AM PST): "both a hanging out sparking end as well
    as the wire plugging into the same point on the wall. That's not ok" and "wires coming out of a junction box not honoring the "preserve
    the right slope" rule". One powered network: a run through a wall, a live run and a dead run each ENDING inside a wall, a power switch
    with three cords coming at it from bends, a + box and a T box; the probe's "endkind:" runs the offline instrument (Core/CordEndAudit,
    SelfTest/CordEndKindChecks) on the live pieces. Rows: SC_cord_end_one_kind, SC_box_stub_slope."""
    x, z = SC0
    _site(B, V)
    walls = (_line(x + 20, z + 4, x + 20, z + 10) + _line(x + 6, z, x + 14, z) + _line(x + 37, z + 1, x + 37, z + 5))
    B.call("jawa/build_batch", ops=V.ops("Wall", walls), stuff="Steel", faction="player", wipeExisting=False)
    B.call("jawa/build_batch", ops="Battery:%d,%d,0;Battery:%d,%d,0" % (x + 2, z + 7, x + 43, z + 2), faction="player", wipeExisting=False)
    B.call("jawa/build_batch", ops="PowerSwitch:%d,%d,0" % (x + 44, z + 10), faction="player", wipeExisting=False)
    runs = (_line(x + 3, z + 7, x + 22, z + 7)                                   # east through the wall at x+20 (a through entry)
            + _line(x + 10, z + 1, x + 10, z + 6) + [(x + 10, z)]                 # south, ENDING inside the wall at z (live)
            + _line(x + 30, z + 3, x + 37, z + 3)                                 # no battery, ENDING inside the wall at x+37 (dead)
            + _line(x + 43, z + 4, x + 43, z + 10)                                # the switch's west stub, from the battery (1x2 at z+2)
            + _line(x + 45, z + 10, x + 47, z + 10) + _line(x + 47, z + 11, x + 47, z + 14)   # its east stub, then a bend
            + _line(x + 44, z + 11, x + 44, z + 13) + _line(x + 41, z + 13, x + 43, z + 13)   # its north stub, then a bend
            + _line(x + 50, z + 20, x + 58, z + 20) + _line(x + 54, z + 16, x + 54, z + 24)   # a + box at (x+54, z+20)
            + _line(x + 50, z + 30, x + 58, z + 30) + _line(x + 54, z + 26, x + 54, z + 29)   # a T box at (x+54, z+30)
            + [(x + 22, z + 8), (x + 22, z + 9), (x + 23, z + 9), (x + 24, z + 9)]   # on inside the wall, round a bend
            + _line(x + 48, z + 14, x + 50, z + 14) + _line(x + 50, z + 15, x + 50, z + 20)   # the switch's east run feeds the + box
            + _line(x + 58, z + 21, x + 58, z + 30))                              # and the + box feeds the T box
    B.call("jawa/build_batch", ops=V.ops("PowerConduit", sorted(set(runs))), faction="player", wipeExisting=False)
    B.ticks(3)
    _fill(B, (x, z, 50, 12))
    B.ticks(3)
    B.probe("poll")
    B.probe("rebuild")
    r = B.probe("endkind:%d,%d,%d,%d" % (x - 1, z - 2, 62, 36))
    ends_ok = bool(r.get("success")) and (r.get("ends") or 0) >= 6 and r.get("both") == 0 and r.get("fitSparks") == 0 and r.get("none") == 0 \
        and r.get("wallTerminalsLoose") == 0 and r.get("terminalsFitted") == 0 and r.get("stubsLoose") == 0
    V.row(rows, "SC_cord_end_one_kind", "PASS" if ends_ok else "FAIL", "MOD",
          {k: r.get(k) for k in ("ends", "both", "fitSparks", "none", "terminalsFitted", "wallTerminalsLoose", "stubsLoose", "bad", "error")})
    slope_ok = bool(r.get("success")) and (r.get("taken") or 0) >= 10 and r.get("offLine") == 0 and r.get("offSlope") == 0 \
        and r.get("short") == 0 and r.get("empty") == 0
    V.row(rows, "SC_box_stub_slope", "PASS" if slope_ok else "FAIL", "MOD",
          {k: r.get(k) for k in ("arms", "taken", "offLine", "offSlope", "short", "empty", "emptyAllowed", "worstDeg", "worstPos", "bad", "error")})


def run(B, V, rows):
    slack_and_shapes(B, V, rows)
    doorway(B, V, rows)
    cut_ends(B, V, rows)
    joints(B, V, rows)
    restring(B, V, rows)
    dead_wire(B, V, rows)
    floor_end_shock(B, V, rows)
    shock_reach(B, V, rows)
    cords_under_items(B, V, rows)
    end_kind_and_slope(B, V, rows)
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
