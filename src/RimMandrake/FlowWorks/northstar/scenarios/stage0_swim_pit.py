"""stage0_swim_pit.py -- Stage 0 proof #3 of the composite design (§5.2 step 0; GPT #2, taken): a swimmer in a flooded
SHEER pit of C3's exact geometry rises and leaves.

C3 (the Labyrinth Rescue) bets its whole goal on this: Hobb in a 2x2, 4 m (8-level) machine-dug sheer pit is floated
out once the hose has put enough water in. No driver row measures that climb-out yet (R12 claims "deep water stops
being a barrier for pits"). If this FAILS live, C3 keeps its maze and hose but delivers into a rescue cistern beside the
pit (design §3 C3 "Prove first"), and the sheer-pit escape becomes a separately labelled experiment.

Rows (one JSON file per run):
  S0SWIM_site        the pit dug to 8 levels on all four cells; the colonist spawned inside (UNMEASURED if not)
  S0SWIM_dry_held    dry: ordered to the lip, he does NOT leave (a sheer 4 m pit holds: the control)
  S0SWIM_2m_out      water 4 levels (2 m) poured: ordered to the lip, he leaves      -> PASS / FAIL
  S0SWIM_brim_out    only if 2 m failed: water to the brim (8 levels): he leaves    -> PASS / FAIL
Verdict: PASS (out at 2 m: C3 as designed), PASS_AT_BRIM (C3's sign must say "fill to the brim"), FAIL (the cistern
fallback), UNMEASURED (the site or any position read failed: no claim).

    python.exe src/RimMandrake/FlowWorks/northstar/scenarios_map.py --stage0 | tr -d '\\r'       # LIVE (needs the bridge)
    python3    src/RimMandrake/FlowWorks/northstar/scenarios_map.py --stage0 --mock             # MOCK: harness only

MOCK runs prove the HARNESS (calls, geometry, verdict logic) against a simulated pawn; they prove nothing about the
game. The live run is owed.
"""
from .common import SWIM, FLUID, W

PIT = (2, 6, 2, 2, 8)               # same 2x2x8 as C3's HOBB_PIT, on the Stage 0 site (site-local cells)
LIP = (2, 9)                        # one cell north of the pit: firm ground, the order's target
START = (2, 6)
WAIT = 900                          # ticks per order (15 s game time): a swim + climb, generous


def kv(txt):
    out = {}
    for tok in str(txt or "").replace("|", " ").split():
        if "=" in tok:
            k, v = tok.split("=", 1)
            out[k] = v
    return out


def run(B, origin, rows=None):
    """Stage and read. B: a bridge (LiveBridge or MockBridge). origin: the site's south-west cell. -> (verdict, rows)."""
    rows = rows if rows is not None else []
    ox, oz = origin
    g = lambda c: (ox + c[0], oz + c[1])  # noqa: E731
    pit = [(PIT[0] + i, PIT[1] + j) for i in range(PIT[2]) for j in range(PIT[3])]

    def row(rid, status, data):
        rows.append(dict(row=rid, status=status, data=data))

    def pos(pid):
        r = B.call("jawa/pawn_get", pawn=pid) or {}
        p = (r.get("pawns") or [{}])[0]
        q = p.get("position") or {}
        return (q.get("x"), q.get("z"))

    def order(pid, c):
        return B.call("jawa/order_pawn", pawnId=pid, x=c[0], z=c[1], waitTicks=WAIT, draft=True) or {}

    def outside(p):
        return p != (None, None) and (p[0] - ox, p[1] - oz) not in pit

    B.call("jawa/destroy_batch", rects="%d,%d,8,12" % (ox, oz), categories="All")
    B.call("jawa/set_terrain_batch", ops="Soil:%d,%d,8,12" % (ox, oz))
    for c in pit:
        B.call("jawa/flowworks_excavation_drive", x=g(c)[0], z=g(c)[1], deepenLevels=PIT[4], setFill=0)
    ex = B.call("jawa/flowworks_excavation_rect", x=g(pit[0])[0], z=g(pit[0])[1], w=PIT[2], h=PIT[3]) or {}
    depths = sorted({r.get("d") for r in ex.get("rows") or []})
    r = B.call("jawa/spawn_pawn", kindDef="Colonist", x=g(START)[0], z=g(START)[1], faction="player", count=1) or {}
    pid = ((r.get("pawns") or [{}])[0]).get("id")
    if depths != [PIT[4]] or pid is None:
        row("S0SWIM_site", "UNMEASURED", dict(depths=depths, pawn=pid))
        return "UNMEASURED", rows
    pid = str(pid)
    row("S0SWIM_site", "PASS", dict(depths=depths, pawn=pid, pit=[g(c) for c in pit]))
    B.call("jawa/set_draft", pawnId=pid, drafted=True)
    o = order(pid, g(LIP))
    p0 = pos(pid)
    if p0 == (None, None):                       # an unread position is ignorance, never "he stayed" (PASS) nor "he failed"
        row("S0SWIM_dry_held", "UNMEASURED", dict(order=str(o)[:200], pos=p0))
        return "UNMEASURED", rows
    row("S0SWIM_dry_held", "PASS" if not outside(p0) else "FAIL",
        dict(order=str(o)[:200], pos=p0, swim=B.call("jawa/static_call", type=SWIM, method="ProofSwim",
                                                     args="%d,%d" % g(START)).get("result")))
    verdict = None
    for rid, level in (("S0SWIM_2m_out", 4), ("S0SWIM_brim_out", 8)):
        for c in pit:
            B.call("jawa/static_call", type=FLUID, method="ProofFillWithFluid", args="%d,%d,%d,%s" % (g(c) + (level, W)))
        B.call("rimworld/step_game_ticks", ticks=120, pauseFirst=True)
        here = pos(pid)
        sw = B.call("jawa/static_call", type=SWIM, method="ProofSwim", args="%d,%d" % here).get("result") \
            if here[0] is not None else ""
        o = order(pid, g(LIP))
        p1 = pos(pid)
        if p1 == (None, None):
            row(rid, "UNMEASURED", dict(level=level, swim=sw, order=str(o)[:200], pos=p1))
            return "UNMEASURED", rows
        ok = outside(p1)
        row(rid, "PASS" if ok else "FAIL", dict(level=level, metres=level * 0.5, swim=sw, swim_kv=kv(sw),
                                                order=str(o)[:200], pos=p1))
        if ok:
            verdict = "PASS" if level == 4 else "PASS_AT_BRIM"
            break
    return verdict or "FAIL", rows
