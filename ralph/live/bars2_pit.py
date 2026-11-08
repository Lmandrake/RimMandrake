"""bars2_pit.py <part...> -- pass-2 pit bars on the story map, east of the compound (row z = 146..157).

parts: ladders portable gear climbout jump wall   (default: all)
  ladders  5x5 pit 2 m at (170,148): RM_Ladder on each wall's middle square (N,E,S,W), all lowered -> shot; all raised
           (ProofLadder raise, the gizmo's own writer) -> shot; N+E lowered again -> shot. Gizmo labels read from below.
  portable RM_LadderPortable in a 2 m pit (178,148) and a 4 m pit (182,148).
  gear     RM_ClimbingGear on the ground (187,149) and worn by a colonist standing at (189,149).
  climbout 4 m sheer pits: geared colonist (192,148) and ungeared control (197,148), both ordered to (195,152).
  jump     2 m pit (202,148); a colonist given Longjump at (203,153) jumps to the floor (203,149); hediffs before/after.
  wall     granite ring x 207..213, z 147..153; geared + ungeared colonist inside; RM_LadderParity climb over (213,150).
"""
import sys
from bars2_common import (bridge, shot, log, j, dig, square, depths, spawn, build, things, proof, census, where, hediffs,
                          play, tick, gizmos, num, PROMO, NSP, PARITY)

B = bridge()
parts = sys.argv[1:] or ["ladders", "portable", "gear", "climbout", "jump", "wall"]
TABLE = []


def row(line, status, note):
    TABLE.append((line, status, note))
    log("ROW", line, status, note)


B.call("jawa/kill_hostiles")
log("tick", tick(B), "settings", j(B.call("jawa/mod_settings_field", typeName="RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings",
                                          action="get", field="portableLadderMaxLevels"), 200))

if "ladders" in parts:
    pit = (170, 148)
    dig(B, square(pit[0], pit[1], 5, 5), 4)
    walls = {0: (172, 152), 1: (174, 150), 2: (172, 148), 3: (170, 150)}
    for r, c in walls.items():
        res = build(B, "RM_Ladder:%d,%d,%d" % (c[0], c[1], r), stuff="WoodLog")
        if not things(B, "RM_Ladder", (c[0], c[1], 1, 1)):
            build(B, "RM_Ladder:%d,%d,%d" % (c[0], c[1], r))
    got = things(B, "RM_Ladder", (170, 148, 5, 5))
    log("ladders on map", [(t.get("x"), t.get("z"), t.get("rot") or t.get("rotation")) for t in got])
    for c in walls.values():
        proof(B, PROMO, "ProofLadder", "%d,%d,lower" % c)
    B.call("rimworld/clear_selection")
    play(B, 700)
    rect = (168, 146, 9, 9)
    shot(B, "ladder_all_lowered", rect)
    if got:
        lid = got[0].get("id") or got[0].get("thingId")
        gz = gizmos(B, lid)
        log("ladder gizmos (selected", lid, "):", [(g.get("label"), g.get("disabled"), g.get("disabledReason")) for g in gz])
        B.call("rimworld/clear_selection")
    reads = [proof(B, PROMO, "ProofLadder", "%d,%d,raise" % c) for c in walls.values()]
    play(B, 700)
    shot(B, "ladder_all_raised", rect)
    for r in (0, 1):
        proof(B, PROMO, "ProofLadder", "%d,%d,lower" % walls[r])
    play(B, 700)
    shot(B, "ladder_NE_lowered_SW_raised", rect)
    shot(B, "ladder_close", rect, root=4.5)
    row("ladder_state_legible+rails", "STAGED" if len(got) == 4 else "PARTIAL", "ladders=%d raise reads=%s" % (len(got), [x[:60] for x in reads]))

if "portable" in parts:
    dig(B, square(178, 148, 3, 3), 4)
    dig(B, square(182, 148, 3, 3), 8)
    for c in ((179, 150), (183, 150)):
        build(B, "RM_LadderPortable:%d,%d,0" % c, stuff="WoodLog")
        if not things(B, "RM_LadderPortable", (c[0], c[1], 1, 1)):
            build(B, "RM_LadderPortable:%d,%d,0" % c)
    got = things(B, "RM_LadderPortable", (178, 148, 8, 3))
    log("portables", [(t.get("x"), t.get("z"), t.get("rot")) for t in got])
    B.call("rimworld/clear_selection")
    play(B, 700)
    shot(B, "portable_2m_and_4m", (176, 146, 10, 7))
    shot(B, "portable_close", (177, 147, 8, 5), root=4.5)
    row("portable_ladder_leans_on_its_wall", "STAGED" if len(got) == 2 else "PARTIAL", "portables=%d" % len(got))

if "gear" in parts:
    for c in ((187, 149), (189, 149), (188, 151)):
        dig(B, [c], 0)
    r = B.call("jawa/spawn_batch", ops="RM_ClimbingGear:187,149") or {}
    log("gear item", j(r, 300))
    pid = spawn(B, (189, 149))
    g = B.call("jawa/pawn_gear", pawn=pid, action="wear", **{"def": "RM_ClimbingGear"}) or {}
    log("wear", j(g, 300))
    ap = B.call("jawa/pawn_get", pawn=pid) or {}
    log("apparel", j(ap.get("apparel") or ap.get("pawn", {}).get("apparel"), 400))
    play(B, 700)
    shot(B, "gear_ground_and_worn", (185, 147, 7, 5))
    shot(B, "gear_close", (186, 148, 5, 3), root=3.0)
    row("climbing_gear_reads_as_kit", "STAGED" if g.get("success") else "PARTIAL", "wear=%s" % g.get("success"))

if "climbout" in parts:
    dig(B, square(192, 148, 3, 3), 8)
    dig(B, square(197, 148, 3, 3), 8)
    dig(B, [(195, 152)], 0)
    a = spawn(B, (193, 149))
    ga = B.call("jawa/pawn_gear", pawn=a, action="wear", **{"def": "RM_ClimbingGear"}) or {}
    b = spawn(B, (198, 149))
    log("geared wear", ga.get("success"))
    for p in (a, b):
        proof(B, NSP, "ProofClimb", "pawn:%d" % num(p))
    play(B, 700)
    rect = (190, 146, 11, 8)
    shot(B, "climbout_before", rect)
    t0 = tick(B)
    oa = B.call("jawa/order_pawn", pawnId=a, x=195, z=152, waitTicks=0, draft=True) or {}
    ob = B.call("jawa/order_pawn", pawnId=b, x=195, z=153, waitTicks=0, draft=True) or {}
    log("orders", j(oa, 300), "|", j(ob, 300))
    mid_shot = False
    for k in range(12):
        B.call("rimworld/step_game_ticks", ticks=100, pauseFirst=True)
        w = where(B, [a, b])
        log("t+%d" % ((tick(B) or 0) - (t0 or 0)), w)
        if not mid_shot and k == 1:
            play(B, 500)
            shot(B, "climbout_mid", rect)
            mid_shot = True
    play(B, 700)
    shot(B, "climbout_after", rect)
    for p in (a, b):
        proof(B, NSP, "ProofClimb", "pawn:%d" % num(p))
    d = depths(B, 190, 146, 11, 8)
    fin = {pid: (x, z, d.get((x, z), 0)) for pid, x, z, _, _ in where(B, [a, b])}
    log("final cells (x,z,depth)", fin)
    row("geared_pawn_climbs_out", "READ", "geared %s ungeared %s" % (fin.get(a), fin.get(b)))

if "jump" in parts:
    dig(B, square(202, 148, 3, 3), 4)
    dig(B, [(203, 153)], 0)
    p = spawn(B, (203, 153))
    log("grant", j(B.call("jawa/grant_ability", pawn=p, ability="Longjump"), 200))
    log("list", j(B.call("jawa/pawn_use_ability", pawn=p, action="list"), 600))
    h0 = hediffs(B, p)
    log("hediffs before", h0)
    rect = (200, 146, 7, 9)
    play(B, 500)
    shot(B, "jump_before", rect)
    r = B.call("jawa/pawn_use_ability", pawn=p, action="cast", ability="Longjump", x=203, z=149, mode="job") or {}
    log("cast", j(r, 800))
    if not r.get("success"):
        r = B.call("jawa/pawn_use_ability", pawn=p, action="cast", ability="Longjump", x=203, z=149, mode="job", force=True) or {}
        log("cast forced", j(r, 800))
    for k in range(8):
        B.call("rimworld/step_game_ticks", ticks=40, pauseFirst=True)
        log("jump t", k, where(B, [p]))
    play(B, 700)
    shot(B, "jump_after", rect)
    h1 = hediffs(B, p)
    d = depths(B, 202, 148, 3, 3)
    w = where(B, [p])
    log("hediffs after", h1, "at", w, "depth there", d.get((w[0][1], w[0][2])) if w else None)
    row("jump_into_pit_lands_unhurt", "READ", "at=%s before=%s after=%s" % (w, h0, h1))

if "wall" in parts:
    ring = [(x, z) for x in range(207, 214) for z in range(147, 154) if x in (207, 213) or z in (147, 153)]
    dig(B, square(207, 147, 7, 7), 0)
    build(B, ";".join("Wall:%d,%d" % c for c in ring), stuff="BlocksGranite")
    log("walls", len(things(B, "Wall", (207, 147, 7, 7))))
    a = spawn(B, (210, 150))
    ga = B.call("jawa/pawn_gear", pawn=a, action="wear", **{"def": "RM_ClimbingGear"}) or {}
    b = spawn(B, (210, 151))
    log("geared wear", ga.get("success"))
    rect = (205, 145, 11, 11)
    play(B, 700)
    shot(B, "wall_before", rect)
    ra = proof(B, PARITY, "ProofLadderParity", "climb:%d,213,150" % num(a))
    rb = proof(B, PARITY, "ProofLadderParity", "climb:%d,213,151" % num(b))
    t0 = tick(B)
    for k in range(10):
        if k == 1:
            play(B, 500)
            shot(B, "wall_mid", rect)
        else:
            B.call("rimworld/step_game_ticks", ticks=100, pauseFirst=True)
        log("t+%d" % ((tick(B) or 0) - (t0 or 0)), where(B, [a, b]))
    play(B, 700)
    shot(B, "wall_after", rect)
    w = where(B, [a, b])
    row("geared_pawn_scales_built_wall", "READ", "geared:%s ungeared:%s at=%s" % (ra[:80], rb[:80], w))

B.call("rimworld/clear_selection")
print("\n=== bars2_pit TABLE ===")
for line, st, note in TABLE:
    print("%-36s %-8s %s" % (line, st, note[:300]))
