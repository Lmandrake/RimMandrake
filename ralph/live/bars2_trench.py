"""bars2_trench.py <part...> -- pass-2 trench-cover and digging-time bars, story map row z = 102..114, x = 170..195.
  cover  3x3 pits dug 1 m (D2, waist) at x 172..174 z 104..106 and 1.5 m (D3, chest) at x 172..174 z 109..111; a colonist
         at each centre; a drafted player Mercenary_Gunner 8 squares east on the same row. Reads ProofTrenchCover and the
         game's own hit-chance text (TooltipUtility.ShotCalculationTipString with the gunner selected).
  dig    a colonist carrying a steel RM_Shovel ordered to cut RM_DigCanal at (190,106) from (191,106); ticks from the order
         to the cut (depth 0 -> 1); shots before / mid / after.
"""
import sys
from bars2_common import bridge, shot, log, j, dig, square, depths, spawn, proof, where, play, tick, num, TRENCH

B = bridge()
parts = sys.argv[1:] or ["cover", "dig"]
TABLE = []


def row(line, status, note):
    TABLE.append((line, status, note))
    log("ROW", line, status, note)


B.call("jawa/kill_hostiles")
if "cover" in parts:
    # Trench cover counts only from a wall square adjacent to the target on the shooter's side: the target stands on the
    # east edge of each pit, the gunner 8 squares east. One adult target (BodySize 1) and one gunner are moved between pits.
    out = {}
    # 1-wide N-S trenches (x = 180, fresh ground): every trench square is an edge square, so the east neighbour (ground) is the wall.
    X = int(sys.argv[3]) if len(sys.argv) > 3 else 200   # fresh ground each run (dig is idempotent, but a re-run must not inherit a deeper trench)
    pits = {"D2": (X, 104, 2), "D3": (X, 110, 3)}
    for name, (x0, z0, d) in pits.items():
        dig(B, [(x0, z0 + k) for k in range(3)], d)
    S = sys.argv[2] if len(sys.argv) > 2 else "Human43122"
    ge = B.call("jawa/pawn_get", pawn=S) or {}
    log("shooter equipment", j(ge.get("equipment") or (ge.get("pawn") or {}).get("equipment"), 300))

    def adult_at(cell):
        for k in range(6):
            t = spawn(B, cell)
            ps = (B.call("jawa/list_pawns") or {}).get("pawns") or []
            bs = next((q.get("bodySize") for q in ps if q.get("id") == t), None)
            log("target", t, "bodySize", bs)
            if bs in (1, 1.0):
                for _ in range(3):
                    B.call("jawa/order_pawn", pawnId=t, x=cell[0], z=cell[1], waitTicks=0, draft=True)
                    B.call("rimworld/step_game_ticks", ticks=5, pauseFirst=True)
                    c = (B.call("jawa/pawn_census", ids=t) or {}).get("pawns") or [{}]
                    log("target drafted?", t, c[0].get("drafted"), c[0].get("x"), c[0].get("z"), c[0].get("mentalState"))
                    if c[0].get("drafted") is not False:
                        break
                return t
            B.call("jawa/pawn_force_incapacitate", pawn=t, action="vanish", _answer=True)
        return t

    def readout(T):
        B.call("rimworld/clear_selection")
        B.call("jawa/select_things", ids=str(S), action="select")
        r = B.call("jawa/static_call", type="Verse.TooltipUtility", method="ShotCalculationTipString", args=str(T)) or {}
        B.call("rimworld/clear_selection")
        return " / ".join(ln.strip() for ln in str(r.get("result") or r.get("error") or "").splitlines() if ln.strip())

    # control on flat ground first: same shooter, same 8-square range
    F = adult_at((X, 116))
    B.call("jawa/order_pawn", pawnId=S, x=X + 8, z=116, waitTicks=600, draft=True)
    play(B, 300)
    log("CONTROL flat 8sq at", where(B, [F, S]), "->", readout(F))
    B.call("jawa/order_pawn", pawnId=S, x=X + 4, z=116, waitTicks=600, draft=True)
    log("CONTROL flat 4sq at", where(B, [F, S]), "->", readout(F))
    B.call("jawa/pawn_force_incapacitate", pawn=F, action="vanish", _answer=True)
    for name, (x0, z0, d) in pits.items():
        tc = (x0, z0 + 1)
        T = adult_at(tc)
        rd = {}
        for dist in (8, 4):
            B.call("jawa/order_pawn", pawnId=S, x=x0 + dist, z=z0 + 1, waitTicks=600, draft=True)
            play(B, 300)
            w = where(B, [T, S])
            if dist == 8:
                B.call("rimworld/clear_selection")
                shot(B, "trench_cover_%s" % name, (x0 - 3, z0 - 2, 13, 7))
                shot(B, "trench_cover_%s_close" % name, (x0 - 3, z0 - 2, 13, 7), root=7.2)
            pr = proof(B, TRENCH, "ProofTrenchCover", "%d;%d" % (num(T), num(S)))
            rd[dist] = (w, pr[:160], readout(T))
            log("READOUT", name, dist, rd[dist])
        out[name] = rd
        B.call("jawa/pawn_force_incapacitate", pawn=T, action="vanish", _answer=True)
    for name, rd in out.items():
        for dist, (w, pr, txt) in rd.items():
            row("trench_wall_cover_shown %s %dsq" % (name, dist), "READ", "at=%s proof=%s | text=%s" % (w, pr, txt))

if "dig" in parts:
    c = (190, 106)
    dig(B, square(188, 104, 5, 5), 0)
    B.call("jawa/set_terrain", terrainDef="Soil", x=c[0], z=c[1])
    p = spawn(B, (191, 106), draft=False)
    g = B.call("jawa/pawn_gear", pawn=p, action="inventory", **{"def": "RM_Shovel", "stuff": "Steel"}) or {}
    log("shovel", j(g, 300))
    B.call("jawa/designate_batch", action="add", designation="RM_DigCanal", rect="%d,%d,1,1" % c)
    rect = (186, 103, 9, 7)
    play(B, 300)
    shot(B, "dig_before", rect)
    d0 = depths(B, c[0], c[1], 1, 1).get(c, 0)
    t0 = tick(B)
    od = B.call("jawa/ordered_job", pawnId=p, jobDef="RM_DigCanalJob", targetAX=c[0], targetAZ=c[1], waitTicks=0) or {}
    log("order", j(od, 300), "d0", d0, "t0", t0)
    cut, mid = None, False
    jobseen = []
    for k in range(80):
        B.call("rimworld/step_game_ticks", ticks=250, pauseFirst=True)
        dt = (tick(B) or 0) - (t0 or 0)
        d = depths(B, c[0], c[1], 1, 1).get(c, 0)
        cen = (B.call("jawa/pawn_census", ids=p) or {}).get("pawns") or [{}]
        jb = cen[0].get("job") or cen[0].get("curJob") or cen[0].get("jobDef")
        if not jobseen or jobseen[-1][1] != jb:
            jobseen.append((dt, jb))
        if k % 4 == 0:
            log("t+%d depth %s job %s at %s" % (dt, d, jb, (cen[0].get("x"), cen[0].get("z"))))
        if not mid and dt >= 1000:
            play(B, 300)
            shot(B, "dig_mid", rect)
            mid = True
        if d != d0:
            cut = dt
            break
    play(B, 500)
    shot(B, "dig_after", rect)
    row("digging_takes_hours", "READ", "cut after %s ticks (%.2f in-game h) d %s->%s jobs=%s" % (
        cut, (cut or 0) / 2500.0, d0, depths(B, c[0], c[1], 1, 1).get(c, 0), jobseen[:6]))

B.call("rimworld/clear_selection")
print("\n=== bars2_trench TABLE ===")
for line, st, note in TABLE:
    print("%-36s %-8s %s" % (line, st, note[:500]))
