"""Offline checks for climb_proof.py's pure verdicts (PIT_POCKET_GRID_BUILD_SLOPES_NEVER_TRAP). No bridge."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import climb_proof as C  # noqa: E402

fails = []


def check(name, cond):
    print("%-4s  %s" % ("ok" if cond else "FAIL", name))
    if not cond:
        fails.append(name)


LINE = "CLIMB k=2 held=True trapped=True cell=11,3 | POCKET k=2 comp=7 pocket=True size=9 depth=3 gen=5 built=5 rebuilds=3"
kv = C.parse(LINE)
check("parse reads both halves", kv.get("held") == "True" and kv.get("pocket") == "True" and kv.get("size") == "9")
check("a fresh grid is evidence", C.fresh(kv))
check("trapped person: PASS", C.state_verdict(kv, want_held=True, want_trapped=True, want_pocket=True)[0] == "PASS")
check("can-fail: a free pawn read as trapped is FAIL", C.state_verdict(kv, want_held=False)[0] == "FAIL")
stale = C.parse(LINE.replace("built=5", "built=4"))
check("a stale grid is UNMEASURED, never PASS or FAIL", C.state_verdict(stale, want_held=True)[0] == "UNMEASURED")
check("no pawn line is UNMEASURED", C.state_verdict(C.parse("POCKET k=2 pocket=True gen=1 built=1"))[0] == "UNMEASURED")
check("REFUSED text parses to no verdict", C.state_verdict(C.parse("REFUSED: no spawned pawn 9"))[0] == "UNMEASURED")

R = (10, 10, 5, 5)
row_out = {"orderAccepted": True, "ticksElapsed": 900, "position": {"x": 12, "z": 17}}
row_in = {"orderAccepted": True, "ticksElapsed": 900, "position": [12, 12]}
check("walked out of the rect: PASS", C.walk_verdict(row_out, R, True)[0] == "PASS")
check("can-fail: stayed in when it should walk out", C.walk_verdict(row_in, R, True)[0] == "FAIL")
check("stayed in when held: PASS", C.walk_verdict(row_in, R, False)[0] == "PASS")
check("a game that never ticked is UNMEASURED", C.walk_verdict(dict(row_in, ticksElapsed=0), R, False)[0] == "UNMEASURED")
check("an unaccepted order is UNMEASURED", C.walk_verdict(dict(row_in, orderAccepted=False), R, False)[0] == "UNMEASURED")
check("one owed row left, pointing at live_session B7", list(C.OWED) == ["CLIMB_save_reload_pockets_identical"] and "B7" in C.OWED["CLIMB_save_reload_pockets_identical"])
check("the ramp rows are no longer owed", "CLIMB_raider_never_crosses_ramped_moat" not in C.OWED and "CLIMB_hauler_fetches_ramped_floor" not in C.OWED)

# PIT_CLIFF_MASK_BUILD_ASTAR_LEARNS_WALLS: the mask row
MP = C.parse("CLIFF k=2 bits=0xFB vanilla=0xFF derived=True derives=4 | POCKET k=2 comp=0 pocket=False")
MB = C.parse("CLIFF k=3 bits=0xFF vanilla=0xFF derived=True derives=4 | POCKET k=3 comp=0 pocket=False")
check("mask: person sealed east, muffalo open: PASS", C.mask_verdict(MP, MB) == "PASS")
check("can-fail: person still open east is FAIL", C.mask_verdict(MB, MB) == "FAIL")
check("masks not derived: UNMEASURED", C.mask_verdict(dict(MP, derived="False"), MB) == "UNMEASURED")
check("vanilla has no east step (a wall): UNMEASURED", C.mask_verdict(dict(MP, vanilla="0xFB"), MB) == "UNMEASURED")
check("a REFUSED read: UNMEASURED", C.mask_verdict(C.parse("REFUSED: no masks"), MB) == "UNMEASURED")

# PIT_RAMP_BUILD_STAIRS_BEAT_LADDERS: the ramp row
def pk(p, built=5):
    return C.parse("POCKET k=2 comp=3 pocket=%s size=9 depth=4 gen=%d built=%d rebuilds=2" % (p, built, built))
check("ramp: pocket, free, pocket again: PASS", C.ramp_verdict(pk("True"), pk("False"), pk("True")) == "PASS")
check("can-fail: ramp did not free: FAIL", C.ramp_verdict(pk("True"), pk("True"), pk("True")) == "FAIL")
check("can-fail: removal did not re-seal: FAIL", C.ramp_verdict(pk("True"), pk("False"), pk("False")) == "FAIL")
check("a stale grid read: UNMEASURED", C.ramp_verdict(pk("True"), C.parse("POCKET k=2 pocket=False gen=6 built=5"), pk("True")) == "UNMEASURED")

# PIT_CLIFF_MASK_BUILD_ASTAR_LEARNS_WALLS step cost: the CLIMB_step_cost_slow_at_K row (cost 45 x factor 2 = 90 slow)
def cs(cost, climb=45, k=2, mask="True", factor="2"):
    return C.parse("COST from=1,4 to=2,4 fromD=0 toD=2 k=%d mask=%s climb=%d factor=%s cost=%d" % (k, mask, climb, factor, cost))
check("step cost: slow 90, flat 0, plain 30: PASS", C.cost_verdict(cs(90), cs(0), cs(30, climb=30)) == "PASS")
check("can-fail: a step of K priced plain: FAIL", C.cost_verdict(cs(45), cs(0), cs(30, climb=30)) == "FAIL")
check("can-fail: walking the ring floor costs: FAIL", C.cost_verdict(cs(90), cs(45), cs(30, climb=30)) == "FAIL")
check("masks off (old pricing): UNMEASURED", C.cost_verdict(cs(90, mask="False"), cs(0), cs(30, climb=30)) == "UNMEASURED")
check("a REFUSED read: UNMEASURED", C.cost_verdict(C.parse("REFUSED: no pawn"), cs(0), cs(30)) == "UNMEASURED")

# CLIMB_RAMP_ROWS_BUILD_STAIRS_ARRIVED_EARLY: the moat row (F) and the haul row (G)
def raider(edge, pid="Thing_Human7", **kw):
    return dict(dict(id=pid, spawned=True, dead=False, downed=False, canReachMapEdge=edge), **kw)
def comp(n):
    return C.parse("POCKET k=2 comp=%d pocket=False size=9 depth=0 gen=5 built=5 rebuilds=2" % n)
check("pit_pawn finds a pawn with or without the Thing_ prefix", C.pit_pawn({"pawns": [raider(False)]}, "Human7") is not None)
check("pit_pawn: another pawn is not this one", C.pit_pawn({"pawns": [raider(False)]}, "Human8") is None)
check("moat: island cut off, moat out by the ramp, components apart: PASS", C.moat_verdict(raider(False), raider(True), comp(4), comp(1), comp(1))[0] == "PASS")
check("can-fail moat: the island raider reaches the edge: FAIL", C.moat_verdict(raider(True), raider(True), comp(4), comp(1), comp(1))[0] == "FAIL")
check("can-fail moat: the grid joins the island to the outside: FAIL", C.moat_verdict(raider(False), raider(True), comp(1), comp(1), comp(1))[0] == "FAIL")
check("moat control: a moat raider that cannot reach the edge voids the row (UNMEASURED)", C.moat_verdict(raider(False), raider(False), comp(4), comp(1), comp(1))[0] == "UNMEASURED")
check("moat: a downed raider is UNMEASURED", C.moat_verdict(raider(False, downed=True), raider(True), comp(4), comp(1), comp(1))[0] == "UNMEASURED")
check("moat: an unread raider is UNMEASURED", C.moat_verdict(None, raider(True), comp(4), comp(1), comp(1))[0] == "UNMEASURED")
check("moat: a stale grid read is UNMEASURED", C.moat_verdict(raider(False), raider(True), C.parse("POCKET k=2 comp=4 gen=6 built=5"), comp(1), comp(1))[0] == "UNMEASURED")
PIT, PILE = (138, 122, 3, 3), (143, 128, 2, 2)
jade = lambda x, z: [dict(def_="Jade", x=x, z=z)]   # noqa: E731
check("haul: sealed without the ramp, in the stockpile after: PASS", C.haul_verdict(jade(139, 123), jade(143, 128), PIT, PILE)[0] == "PASS")
check("can-fail haul: the Jade left a sheer D 4 floor with no ramp: FAIL", C.haul_verdict(jade(150, 130), jade(143, 128), PIT, PILE)[0] == "FAIL")
check("can-fail haul: never fetched with the ramp built: FAIL", C.haul_verdict(jade(139, 123), jade(139, 123), PIT, PILE)[0] == "FAIL")
check("haul: carried / unseen at the end is FAIL, not PASS", C.haul_verdict(jade(139, 123), [], PIT, PILE)[0] == "FAIL")
check("haul: the Jade never read back is UNMEASURED", C.haul_verdict([], jade(143, 128), PIT, PILE)[0] == "UNMEASURED")
check("site holds the new scenes: 46 x 12", (C.SITE_W, C.SITE_H) == (46, 12))

# LS_FULLREAD 2026-10-19: the digs are read back, and old digs are reset first (Deepen ADDS: a reused map doubled depths)
check("digs at the asked depth: no misses", C.dig_misses([((1, 1), 4, {"success": True, "depth": 4})]) == [])
check("can-fail: a doubled depth (cell never reset) is a miss",
      len(C.dig_misses([((1, 1), 4, {"success": True, "depth": 8}), ((2, 1), 2, {"success": False, "error": "no engine"})])) == 2)
check("reset read: left=0", C.reset_left("RESET cells=9 levels=36 rolled=0 left=0") == 0)
check("can-fail reset: left>0 or REFUSED is not 0", C.reset_left("RESET cells=9 levels=36 rolled=0 left=2") == 2
      and C.reset_left("REFUSED: no excavation engine on the current map") is None)

# PIT_CLIMB_PROVE_RAIDERS_VS_SHEER_TRENCH risk 2: the mask swap under queued path requests while the masks re-derive
H = (136, 127, 3, 3)
def ms(extra=(), n=40):
    s = [(k, "F", (137, 128)) for k in range(n)]
    s += [(k, "W", (134, 128) if (k // 10) % 2 == 0 else (140, 128)) for k in range(n)]
    return s + list(extra)
G = dict(rect=H, inside={"F"}, outside={"W"}, derives=(4, 64), orders=60, sealed=True)
check("maskswap: nobody crossed, masks churned, walkers went round: PASS", C.maskswap_verdict(ms(), **G)[0] == "PASS")
check("can-fail maskswap: the floor pawn sampled on the lip is FAIL", C.maskswap_verdict(ms([(41, "F", (135, 128))]), **G)[0] == "FAIL")
check("can-fail maskswap: a surface pawn sampled on the pit floor is FAIL", C.maskswap_verdict(ms([(41, "W", (137, 127))]), **G)[0] == "FAIL")
check("maskswap: masks never re-derived is UNMEASURED", C.maskswap_verdict(ms(), **dict(G, derives=(4, 6)))[0] == "UNMEASURED")
check("maskswap: unread derives is UNMEASURED", C.maskswap_verdict(ms(), **dict(G, derives=(None, 9)))[0] == "UNMEASURED")
check("maskswap: too few orders is UNMEASURED", C.maskswap_verdict(ms(), **dict(G, orders=3))[0] == "UNMEASURED")
check("maskswap: walkers that never changed side (no path served) is UNMEASURED", C.maskswap_verdict(
      [(k, p, (134, 128) if p == "W" else (137, 128)) for k in range(40) for p in ("F", "W")], **G)[0] == "UNMEASURED")
check("maskswap: an unsealed or unread wall is UNMEASURED", C.maskswap_verdict(ms(), **dict(G, sealed=None))[0] == "UNMEASURED"
      and C.maskswap_verdict(ms(), **dict(G, sealed=False))[0] == "UNMEASURED")
check("maskswap: a blind sample is UNMEASURED, a crossing still FAIL", C.maskswap_verdict(ms([(41, "W", None)]), **G)[0] == "UNMEASURED"
      and C.maskswap_verdict(ms([(41, "W", None), (42, "F", (139, 128))]), **G)[0] == "FAIL")

RR = [{"id": "A", "status": "PASS"}, {"id": "B", "status": "UNMEASURED"}]
check("--require: named rows all PASS exits 0", C.require_exit(RR, "A") == 0)
check("can-fail --require: an UNMEASURED or missing row exits 1", C.require_exit(RR, "A,B") == 1 and C.require_exit(RR, "Z") == 1
      and C.require_exit(RR, " , ") == 1)

# CLIMB_HAULER_FIX_BACKSTORY_NO_HAULING: a Hauling-disabled colonist is re-rolled, not reported as an unstaged site
REFUSE = {"success": False, "message": "SetPriority silently refuses: 'Hauling' is DISABLED for this pawn",
          "details": {"disabledWorkTypes": ["Hauling", "Cleaning"]}}
ids, parked = iter(["Human1", "Human2", "Human3"]), []
replies = {"Human1": REFUSE, "Human2": {"success": True, "priority": 1}}
pid, hp, ref = C.pick_hauler(lambda: next(ids), replies.get, parked.append)
check("hauler: a disabled pawn is skipped for the next one", pid == "Human2" and hp.get("success"))
check("hauler: the reject is drafted out of the job market", parked == ["Human1"])
check("hauler: the refusal message and disabled list are logged",
      len(ref) == 1 and "DISABLED" in ref[0]["message"] and ref[0]["disabled"] == ["Hauling", "Cleaning"])
parked = []
pid, hp, ref = C.pick_hauler(lambda: "HumanX", lambda p: REFUSE, parked.append, tries=3)
check("hauler: can-fail: every try refused -> no hauler, every refusal kept", pid is None and len(ref) == 3
      and len(parked) == 3 and hp.get("success") is False)
pid, hp, ref = C.pick_hauler(lambda: None, lambda p: {"success": True}, parked.append, tries=2)
check("hauler: a failed spawn is a logged refusal, never a hauler", pid is None and ref[0]["pawn"] is None
      and "no pawn" in ref[0]["message"])

# RIMMANDRAKE_FIX_CLIMB_SLOW_OUTLASTS_LADDER: span_verdict over synthetic per-tick ProofLadderClimbDraw reads
def lclimb(ticks, pa, pb, lo, hi, remap, walk=13, tail=3):
    """A ladder step (20,3) -> (19,3) on x drawn steadily (remap False) or walk pace off the span and slow on it."""
    n, out = abs(pb - pa), []
    u0, u1 = (min(max((lo - pa) / (pb - pa), 0), 1), min(max((hi - pa) / (pb - pa), 0), 1))
    u0, u1 = min(u0, u1), max(u0, u1)
    r = min(1.0, n * walk / float(ticks))
    m0, m1 = u0 * r, 1 - (1 - u1) * r
    for i in range(1, ticks + 1):
        m = i / float(ticks)
        if not remap:
            u = m
        elif m < m0:
            u = m / r
        elif m > m1:
            u = 1 - (1 - m) / r
        else:
            u = u0 + (u1 - u0) * (m - m0) / (m1 - m0)
        x = pa + (pb - pa) * u
        out.append(C.parse("LCLIMB id=H cell=20,3 next=19,3 moving=True m=%.3f cost=%d walk=%d drawX=%.4f drawZ=3.2 "
                           "ladder=RM_Ladder@20,3 axis=x lo=%.3f hi=%.3f onSpan=x" % (m, ticks, walk, x, lo, hi)))
    out += [C.parse("LCLIMB id=H cell=19,3 next=18,3 moving=True m=0.5 cost=13 walk=13 drawX=19.0 drawZ=3.5 ladder=none")] * tail
    return out


up_new = lclimb(450, 20.5, 19.5, 20.1, 20.4, True)
up_old = lclimb(450, 20.5, 19.5, 20.1, 20.4, False)
check("span: walk off the art, slow on it -> PASS", C.span_verdict(up_new, (20, 3), (19, 3))[0] == "PASS")
check("span: can-fail: the old steady tween -> FAIL", C.span_verdict(up_old, (20, 3), (19, 3))[0] == "FAIL")
d = C.span_verdict(up_new, (20, 3), (19, 3))[1]
check("span: enter/exit tick and position recorded", d["enterTick"] is not None and d["leaveTick"] > d["enterTick"]
      and 20.0 <= d["leaveAt"] <= 20.5 and 20.0 <= d["enterAt"] <= 20.5)
check("span: a step that never completes is UNMEASURED", C.span_verdict(up_new[:-3], (20, 3), (19, 3))[0] == "UNMEASURED")
check("span: no ladder step seen is UNMEASURED", C.span_verdict(up_new[-3:], (20, 3), (19, 3))[0] == "UNMEASURED")
check("span: the other direction's step is not this row's", C.span_verdict(up_new, (19, 3), (20, 3))[0] == "UNMEASURED")
gap = [dict(k) for k in up_new]
mid = len(gap) // 2
for k in gap[mid:mid + 5]:
    k["drawX"] = "21.5"                     # drawn off the art for 5 ticks in the middle of the climb
check("span: can-fail: an on-span run broken in two -> FAIL", C.span_verdict(gap, (20, 3), (19, 3))[0] == "FAIL")
stall = up_new[:447] + [dict(up_new[446]) for _ in range(6)] + up_new[447:]   # parked off the art below the span
check("span: can-fail: slow ticks off the art -> FAIL", C.span_verdict(stall, (20, 3), (19, 3))[0] == "FAIL")

print("%s: %d failure(s)" % ("PASS" if not fails else "FAIL", len(fails)))
sys.exit(1 if fails else 0)
