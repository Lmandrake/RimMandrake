"""Offline selftest of liquid_checks.py's timing and verdict logic (WSL python3; no bridge). Each bar must be able to go red.
THEFT_ROW_REPAIR_WITNESS_WALKS_OFF: a FAIL needs a LIVE witness present at the theft check; a witness that walked off is
UNMEASURED (HARNESS), never FAIL."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import liquid_checks as LC  # noqa: E402

W = [{"id": 1, "x": 81, "z": 185, "downed": False, "dead": False}]
cases = []


def case(got, want, why):
    cases.append((got, want, why))


case([LC.ticks_until(t, LC.WITNESS_PHASE) for t in (4, 5, 254, 1000, 1003)], [0, 249, 0, 4, 1], "ticks_until wraps at 250")
case((1000 + LC.ticks_until(1000, LC.WITNESS_PHASE)) % 250, LC.WITNESS_PHASE, "step lands on the witness phase")
case(LC.WITNESS_PHASE < LC.CHECK_PHASE <= LC.WITNESS_PHASE + 5, True, "witness spawns just BEFORE the theft check")
case(LC.theft_verdict(40, 0, 1, 0, 1, W)[0], "PASS", "caught + letter + live witness")
case(LC.theft_verdict(40, 0, 0, 0, 0, W)[0], "FAIL", "live witness present, mod caught nothing")
case(LC.theft_verdict(40, 0, 0, 0, 0, [])[0], "UNMEASURED", "witness walked off / absent: harness, not mod")
case(LC.theft_verdict(40, 0, 0, 0, 0, [dict(W[0], downed=True)])[0], "UNMEASURED", "downed witness is not a witness")
case(LC.theft_verdict(40, 0, 0, 0, 0, [dict(W[0], dead=True)])[2].get("why", "")[:7], "no live", "reason names the lost witness")
case(LC.theft_verdict(0, 0, 0, 0, 0, W)[0], "UNMEASURED", "nothing drawn: no theft to spot")
case(LC.theft_verdict(40, 0, 1, 0, 0, W)[0], "FAIL", "caught rose but no letter")
case(LC.theft_verdict(40, 0, 1, 0, 1, W, "site")[0], "UNMEASURED", "precondition failed")
case(LC.theft_verdict(40, None, 1, 0, 1, W)[0], "UNMEASURED", "caught unreadable")
case(LC.goodwill_verdict(10, 8, 0, -2, 2, True)[0], "PASS", "goodwill fell by perDay")
case(LC.goodwill_verdict(10, 10, 0, 0, 2, True)[0], "FAIL", "caught but no charge")
case(LC.goodwill_verdict(10, 8, 0, -2, 2, False)[0], "UNMEASURED", "never caught")
case(LC.dump_no_pump_verdict([100, 98, 96], 0, 2)[0], "PASS", "slow drain wets the canal")
case(LC.dump_no_pump_verdict([100, 100], 0, 0)[0], "FAIL", "no drain")
case(LC.dump_no_pump_verdict([0, 0], 0, 0)[0], "UNMEASURED", "tank never held liquid")
case(LC.dump_pump_verdict([100, 50], 0, 5, 4)[0], "PASS", "pump faster than no-pump")
case(LC.dump_pump_verdict([100, 97], 0, 5, 4)[0], "FAIL", "pump not faster")
case(LC.dump_pump_verdict([100, 50], 0, 5, None)[0], "UNMEASURED", "no slow rate to compare")
L = LC.LEVEL
case(LC.ship_fill_verdict([[120000, 0], [100000, 19300]])[0], "PASS", "ship gains a level-scale amount, base falls")
case(LC.ship_fill_verdict([[100, 0], [0, 0]])[0], "FAIL", "base drained into the hose only: ship gained 0 (the 2026-10-16 trace)")
case(LC.ship_fill_verdict([[120000, 0], [119000, 700]])[0], "FAIL", "a hose prime is not a load (< half a level)")
case(LC.ship_fill_verdict([[120000, None], [0, 0]])[0], "UNMEASURED", "unreadable tank")
case(LC.ship_fill_verdict([[1, 0]], "lay failed")[0], "UNMEASURED", "precondition")
case(LC.ship_empty_verdict([[0, 40000], [20000, 20000]])[0], "PASS", "ship falls, base rises")
case(LC.ship_empty_verdict([[0, 0], [0, 0]])[0], "FAIL", "nothing unloads")
case(LC.spill_verdict(L, 0, L, 0, 3, 0, 0)[0], "PASS", "hose emptied and filth appeared")
v = LC.spill_verdict(L, 0, L, 0, 0, 0, 1)
case((v[0], "no cell" in v[2].get("why", "")), ("FAIL", True), "counted but unplaced spill is a FAIL that names Unplaced")
case(LC.spill_verdict(L, L, 0, 0, 0, 0, 0)[0], "FAIL", "hose kept its liquid after the cap")
case(LC.spill_verdict(0, 0, 0, 0, 0, 0, 0)[0], "UNMEASURED", "hose held nothing before the cap")
case(LC.spill_verdict(L, 0, L, None, 3, 0, 0)[0], "UNMEASURED", "filth unreadable")
case(LC.spill_verdict(L, 0, 10000, 1, 4, 0, 0, expected=3)[0], "PASS", "the 2026-10-16b trace: one filth thickened 1 -> 4 by 3 pieces")
case(LC.spill_verdict(L, 0, 10000, 1, 1, 0, 0, expected=3)[0], "FAIL", "spilled but the filth did not thicken")
case(LC.spill_verdict(L, 0, 10000, 1, 2, 0, 0, expected=3)[0], "FAIL", "fewer pieces than FilthCount")
# live_session 20261022T235239: drained 10,000, SpilledUnits flat, no filth -- where did it go? (the exits ledger)
_n0 = dict(spilledUnits=51345, placedInWaterUnits=0, placedNearbyUnits=0, returnedUnits=0, homedFarUnits=0, lostUnits=0)
_wet = dict(_n0, placedInWaterUnits=10000)
case(LC.spill_exits(_n0, _wet), dict(spilled=0, placedInWater=10000, placedNearby=0, returned=0, homedFar=0, lost=0), "exits are deltas")
case(LC.spill_exits(dict(spilledUnits=1), dict(spilledUnits=2)), None, "an old DLL without the exit counters reads None")
case(LC.spill_verdict(10000, 0, 10000, 0, 0, 0, 0, expected=0, exits=LC.spill_exits(_n0, _wet))[:2], ("UNMEASURED", "SITE"),
     "the 20261022 trace: the drain went into water beside the drain square -- the plot, not the mod")
case(LC.spill_verdict(10000, 0, 10000, 0, 0, 0, 0, expected=0, exits=LC.spill_exits(_n0, _n0))[:2], ("FAIL", "MOD"),
     "can-fail: drained units no exit counted are a ledger hole")
case(LC.spill_verdict(10000, 0, 10000, 0, 3, 0, 0, expected=3, exits=LC.spill_exits(_n0, dict(_n0, spilledUnits=61345)))[0], "PASS",
     "a dry-ground spill with its filth still PASSes with the exits read")
case(LC.spill_verdict(10000, 0, 10000, 0, 0, 0, 0, expected=0)[0], "FAIL", "without the exits read the old FAIL stands")
case(LC.filth_pieces(10000, 4000), 3, "1000 L at 400 L per piece = 3")
case(LC.filth_pieces(1, 4000), 1, "any spill shows")
case(LC.filth_thickness("Spilled liquid x4"), 4, "FilthLabel thickness")
case(LC.filth_thickness("Spilled liquid of hose x2"), 2, "FilthLabelWithSource thickness")
case(LC.filth_thickness("Spilled liquid"), None, "no thickness is unreadable, never 0")
case(LC.FILL_UNITS >= 4 * L, True, "staging is level-scale, not the pre-litres 100")


def _rows(fills, depth=2, z=0, x0=0, sink_upto=-1, source_at=None):
    out = [{"x": x0 + i, "z": z, "d": depth, "f": f, "isExcavated": True, "isSink": x0 + i <= sink_upto, "isSource": False}
           for i, f in enumerate(fills)]
    if source_at is not None:
        out.append({"x": source_at, "z": z, "d": 0, "f": 0, "isExcavated": False, "isSink": False, "isSource": True})
    return out


case(LC.levelset_verdict(_rows([1, 1, 1, 1, 0, 0]))[0], "PASS", "L7: one patch at depth 1, rest dry")
case(LC.levelset_verdict(_rows([1, 0, 1, 0, 1, 0]))[0], "FAIL", "L7: the walk save's 1,0,1,0 stripe")
case(LC.levelset_verdict(_rows([1, 0, 1, 0, 1, 0]))[2]["stripes"], 2, "L7: two stripes counted")
case(LC.levelset_verdict(_rows([0, 2, 2, 0]))[0], "FAIL", "L7: 0, deep, 0 (a brim blob beside dry D2)")
case(LC.levelset_verdict(_rows([2, 2, 2, 2]))[0], "PASS", "L7: brim-full canal")
case(LC.levelset_verdict(_rows([0, 0, 0]))[0], "UNMEASURED", "L7: no water is unreadable, not a pass")
case(LC.levelset_verdict(_rows([1, 0, 1, 1], sink_upto=1))[0], "PASS", "L7: sink-band squares are in flux and not read")
case(LC.levelset_verdict(_rows([2, 0, 0], x0=1, source_at=0))[0], "PASS", "L7: the mouth beside the pond is not a step")
case(LC.levelset_verdict(_rows([1, 1, 0, 1, 0, 0]), _rows([1, 0, 1, 1, 0, 0]))[0], "PASS", "L7: a gap that moved since the last pulse is flow in transit")
case(LC.levelset_verdict(_rows([1, 0, 1, 0, 1, 0]), _rows([1, 0, 1, 0, 1, 0]))[0], "FAIL", "L7: a stripe standing in both reads")
case(LC.levelset_verdict(_rows([1, 1, 0, 1, 0, 0]), _rows([1, 0, 1, 1, 0, 0]))[2]["movingStripes"], [(2, 0)], "L7: the moving gap is named")
# L8 (POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD): each bar can go red.
def _P(s_, r_, wet, applies=True, **cen):
    c = dict(deep=0, chest=0, shallow=0, thin=0, own=0, mud=0, lakebed=0, other=0)
    c.update(cen)
    return LC.parse_pond("POND id=1 pulse=9 model=1 applies=%s limitless=False stock=10.00 capacity=20.00 s=%d r=%d wet=%d census=%s"
                         % (applies, s_, r_, wet, ",".join("%s:%d" % kv for kv in c.items())))
case(LC.parse_pond("POND id=3 s=2 r=1 wet=7 applies=True census=deep:1,thin:2")["census"]["thin"], 2, "L8: the reply parses")
case(LC.parse_pond("REFUSED: no formed pond"), None, "L8: a refusal is no read")
case(LC.pond_depth_verdict([_P(0, 0, 100, own=100), _P(1, 0, 100, chest=64, thin=36)])[0], "PASS", "L8: one level down, nothing dried, stages show")
case(LC.pond_depth_verdict([_P(0, 0, 100, own=100), _P(1, 0, 64, own=64, mud=36)])[0], "FAIL", "L8: the old shrink-from-the-rim is a FAIL")
case(LC.pond_depth_verdict([_P(0, 0, 100, own=100), _P(1, 0, 100, own=100)])[0], "FAIL", "L8: s fell but no part-depth square")
case(LC.pond_depth_verdict([_P(0, 0, 100, own=100), _P(0, 0, 100, own=100)])[0], "UNMEASURED", "L8: the pump drew nothing is SITE")
case(LC.pond_depth_verdict([_P(0, 0, 9, False), _P(1, 0, 9, False)])[1], "SITE", "L8: model not applying is SITE")
case(LC.pond_depth_verdict([_P(0, 0, 9)])[0], "UNMEASURED", "L8: one read is not a trace")
case(LC.spill_verdict(None, 0, L, 0, 3, 0, 0)[:2], ("UNMEASURED", "HARNESS"), "held units unreadable is HARNESS, not 'held nothing'")
case(LC.clean_verdict("Human1", {"success": True}, 3, 9, 0, 750)[0], "PASS", "readBack 3 with manual priorities off is enabled")
case(LC.clean_verdict("Human1", {"success": True}, 0, 9, 0, 750)[0], "UNMEASURED", "Cleaning off is no test")
case(LC.clean_verdict("Human1", {"success": True}, 3, 9, 4, 3000)[0], "FAIL", "filth left after the wait")
case(LC.clean_verdict("Human1", {"success": True}, 3, 9, None, 250)[:2], ("UNMEASURED", "HARNESS"), "filth unreadable")
case(LC.clean_verdict(None, {"success": True}, 3, 9, 0, 750)[0], "UNMEASURED", "no cleaner spawned")
case(LC.free_end_verdict({}, "Ankor", True)[:2], ("UNMEASURED", "HARNESS"), "unread free end is not a MOD FAIL")
case(LC.free_end_verdict({"describe": "to Ankor's tank", "portFaction": "Ankor"}, "Ankor", True)[0], "PASS", "names them")
case(LC.free_end_verdict({"describe": "to a tank", "portFaction": None}, "Ankor", True)[0], "FAIL", "does not name them")
case(LC.goodwill_verdict(10, 8, None, None, 2, True)[0], "UNMEASURED", "charge unreadable is not 'no charge'")
case(LC.goodwill_verdict(10, 8, 0, -2, None, True)[0], "UNMEASURED", "per-day rate unread: never guessed")
case(LC.dump_no_pump_verdict([100, 98], None, None)[0], "UNMEASURED", "canal unreadable is not a dry canal")
case(LC.dump_pump_verdict([100, 50], None, None, 4)[0], "UNMEASURED", "reach unreadable is not a dry reach")
bad = [(g, w, y) for g, w, y in cases if g != w]
for g, w, y in bad:
    print("FAIL", y, "got", g, "want", w)
print("selftest_liquid_checks: %d/%d" % (len(cases) - len(bad), len(cases)))
sys.exit(1 if bad else 0)
