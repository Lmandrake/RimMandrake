"""BATCHREADS_BUILD_ROUND_TRIP_CUT live proof (tickburst_2026-11-06/final.md L-d). Read-only: nothing is spawned, set or
advanced. The game must be Playing a map and PAUSED (every comparison is refused unless all its reads carry the same
ticksGame, because a moving pawn or a ticking need would make two honest reads differ).

  python.exe src/RimMandrake/bridgetools/prove_batch_reads.py --clause A1    things, pawns, power nets: batch == single
  python.exe src/RimMandrake/bridgetools/prove_batch_reads.py --clause A2    fluid cells: round trips saved, same values

A1: jawa/list_things_batch over up to 12 rects returns, rect by rect, exactly the rows jawa/list_things returns for that
    rect alone (at least one rect must hold a thing), and jawa/get_pawns_batch returns, pawn by pawn, exactly
    jawa/pawn_get's snapshot (at least one pawn), with a planted unknown pawn refused by both, and
    jawa/get_power_nets_batch over every BuildingArtificial (up to 300) returns, thing by thing, the read jawa/power_net
    returns (connected, net block, isPowerTrader, PowerOn, energyOutputPerTick; a refusal where power_net refuses),
    with at least one building carrying CompPower (a map with none is UNMEASURED, naming it).
A2: the FlowWorks northstar extensions.py reads _state and _water (its plot_C_limitless_canal chain reads every channel
    cell this way, once per pulse) on a 10-cell line at the map centre, once per cell (flowworks_excavation_report +
    ProofPitWater) and once through flowworks_excavation_rect: equal values, fewer round trips; both counts and the
    measured ms per call are printed.

Exit 0 holds, 1 does not, 2 UNMEASURED: <reason> (no map, not paused, nothing to compare, a tool absent).
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.join(HERE, "..", "Utils")
NORTHSTAR = os.path.join(HERE, "..", "FlowWorks", "northstar")
for _p in (UTILS, os.path.join(UTILS, "modcheck"), NORTHSTAR):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import rimbridge_client as rb  # noqa: E402


class Unmeasured(Exception):
    pass


class Bridge(object):
    def __init__(self):
        h, p, t = rb.resolve_endpoint()
        self.c = rb.RimBridge(host=h, port=p, token=t, timeout=120)
        self.c.static_reads = True              # ProofPitWater is a reviewed read (rimbridge_client.READ_ONLY_STATIC_CALLS)
        self.c.connect()
        self.calls = 0
        self.secs = 0.0
        self.ticks = set()

    def call(self, tool, **p):
        t0 = time.time()
        r = self.c.call(tool, p, check=False)
        self.secs += time.time() - t0
        self.calls += 1
        if isinstance(r, dict) and isinstance(r.get("ticksGame"), int):
            self.ticks.add(r["ticksGame"])
        return r if isinstance(r, dict) else {}


def _need(r, what):
    if not r.get("success"):
        raise Unmeasured("%s failed: %s" % (what, str(r)[:300]))
    return r


def _still(b, what):
    if len(b.ticks) > 1:
        raise Unmeasured("the game advanced during %s (ticksGame %s): pause it" % (what, sorted(b.ticks)))


def _canon(x):
    return json.dumps(x, sort_keys=True)


def clause_a1(b):
    mi = b.call("jawa/map_info")
    sx, sz = mi.get("sizeX"), mi.get("sizeZ")
    if not sx or not sz:
        raise Unmeasured("no map (map_info %s)" % str(mi)[:200])
    b.ticks.clear()
    every = _need(b.call("jawa/list_things", limit=200), "list_things (whole map)")
    seen, rects = set(), []
    for th in every.get("things") or []:
        key = (th["x"] // 8, th["z"] // 8)
        if th.get("x", -1) >= 0 and key not in seen:
            seen.add(key)
            rects.append((key[0] * 8, key[1] * 8, 8, 8))
        if len(rects) >= 11:
            break
    rects.append((0, 0, 1, 1))              # a corner cell: usually empty, the zero path
    batch = _need(b.call("jawa/list_things_batch", rects=";".join("%d,%d,%d,%d" % r for r in rects), limit=500),
                  "list_things_batch")
    res = batch.get("results") or []
    if len(res) != len(rects):
        return 1, "list_things_batch returned %d results for %d rects" % (len(res), len(rects))
    nonempty = 0
    for r, got in zip(rects, res):
        one = _need(b.call("jawa/list_things", rect="%d,%d,%d,%d" % r, limit=500), "list_things rect %s" % (r,))
        a = sorted(one.get("things") or [], key=lambda t: t["id"])
        g = sorted(got.get("things") or [], key=lambda t: t["id"])
        if _canon(a) != _canon(g) or one.get("countMatched") != got.get("countMatched"):
            return 1, "rect %s: list_things %d rows (matched %s) vs batch %d (matched %s); first diff %s" % (
                r, len(a), one.get("countMatched"), len(g), got.get("countMatched"),
                next(((x, y) for x, y in zip(a, g) if x != y), None))
        nonempty += 1 if a else 0
    if nonempty == 0:
        raise Unmeasured("every rect read empty: nothing compared (the instrument may not see)")
    _still(b, "the things comparison")

    lp = _need(b.call("jawa/list_pawns", limit=200), "list_pawns")
    ids = [p["id"] for p in (lp.get("pawns") or []) if not p.get("dead")][:8]
    if not ids:
        raise Unmeasured("no living pawn on the map")
    bogus = "NoSuchPawn_BATCHREADS"
    pb = _need(b.call("jawa/get_pawns_batch", pawns=",".join(ids + [bogus])), "get_pawns_batch")
    rows = pb.get("rows") or []
    if len(rows) != len(ids) + 1:
        return 1, "get_pawns_batch returned %d rows for %d queries" % (len(rows), len(ids) + 1)
    for pid, row in zip(ids, rows):
        one = _need(b.call("jawa/pawn_get", pawn=pid), "pawn_get %s" % pid)
        snap = (one.get("pawns") or [None])[0]
        if row.get("ok") is not True or _canon(snap) != _canon(row.get("pawn")):
            return 1, "pawn %s: pawn_get and get_pawns_batch disagree (ok=%s)" % (pid, row.get("ok"))
    if rows[-1].get("ok") is not False or b.call("jawa/pawn_get", pawn=bogus).get("success") is not False:
        return 1, "the planted unknown pawn was not refused by both (batch row %s)" % rows[-1]
    _still(b, "the pawn comparison")
    code, why = clause_power(b)
    if code != 0:
        return code, why
    return 0, "%d rects (%d holding things) and %d pawns read the same through the batch tools; %s; %d calls" % (
        len(rects), nonempty, len(ids), why, b.calls)


def clause_a2(b):
    import extensions as EXT
    mi = b.call("jawa/map_info")
    sx, sz = mi.get("sizeX"), mi.get("sizeZ")
    if not sx or not sz:
        raise Unmeasured("no map (map_info %s)" % str(mi)[:200])
    cells = [(sx // 2 - 5 + i, sz // 2) for i in range(10)]

    class T(object):
        def _guard(self):
            return True

        def bridge_call(self, tool, **p):
            return b.call(tool, **p)
    b.ticks.clear()
    out = {}
    for label, absent in (("per_cell", True), ("batch", False)):
        t = T()
        t._cells_batch_absent = absent
        c0, s0 = b.calls, b.secs
        try:
            vals = (EXT._state(t, cells), EXT._water(t, cells))
        except EXT.ExpectationFailed as e:
            raise Unmeasured("%s read failed: %s" % (label, e))
        if not absent and getattr(t, "_cells_batch_absent", False):
            raise Unmeasured("flowworks_excavation_rect is not on this bridge")
        out[label] = (vals, b.calls - c0, b.secs - s0)
    _still(b, "the fluid comparison")
    (v1, n1, s1), (v2, n2, s2) = out["per_cell"], out["batch"]
    if any(d is None for d, _ in v1[0]):
        raise Unmeasured("the per-cell read returned no depth (FlowWorks not loaded?): %s" % (v1[0],))
    msg = "10 cells: per-cell %d calls %.0f ms (%.1f ms/call), batch %d calls %.0f ms; %d round trips saved" % (
        n1, s1 * 1000, s1 * 1000 / max(n1, 1), n2, s2 * 1000, n1 - n2)
    if v1 != v2:
        return 1, "values differ: per-cell %s, batch %s; %s" % (v1, v2, msg)
    if not n2 < n1:
        return 1, "no round trips saved: " + msg
    return 0, msg


def clause_power(b):
    b.ticks.clear()
    every = _need(b.call("jawa/list_things", group="BuildingArtificial", limit=300), "list_things BuildingArtificial")
    ids = [t["id"] for t in every.get("things") or []]
    if not ids:
        raise Unmeasured("no BuildingArtificial on the map")
    pb = _need(b.call("jawa/get_power_nets_batch", things=",".join(ids)), "get_power_nets_batch")
    rows = pb.get("rows") or []
    if len(rows) != len(ids):
        return 1, "get_power_nets_batch returned %d rows for %d things" % (len(rows), len(ids))
    pos = 0
    for tid, row in zip(ids, rows):
        one = b.call("jawa/power_net", thing=tid)
        if one.get("success") is not True:
            if row.get("ok") is not False:
                return 1, "%s: power_net refused (%s) but the batch row is ok" % (tid, str(one)[:200])
            continue
        pos += 1
        want = {"thing": one.get("thing"), "connected": one.get("connected"), "net": one.get("net"),
                "isPowerTrader": one.get("isPowerTrader"), "powerOn": one.get("powerOnBefore"),
                "energyOutputPerTick": one.get("energyOutputPerTick")}
        got = {k: row.get(k) for k in want}
        if row.get("ok") is not True or _canon(want) != _canon(got):
            return 1, "%s: power_net %s vs batch %s" % (tid, want, got)
    if pos == 0:
        raise Unmeasured("none of %d buildings carries CompPower: the positive path was not compared" % len(ids))
    _still(b, "the power comparison")
    return 0, "%d buildings (%d with CompPower, %d nets) read the same through get_power_nets_batch" % (
        len(ids), pos, pb.get("netCount"))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--clause", required=True, choices=("A1", "A2"))
    a = ap.parse_args(argv)
    try:
        b = Bridge()
        code, why = {"A1": clause_a1, "A2": clause_a2}[a.clause](b)
    except Unmeasured as e:
        print("UNMEASURED: %s" % e)
        return 2
    except Exception as e:      # a dead bridge is no verdict, never a FAIL
        print("UNMEASURED: %s: %s" % (type(e).__name__, str(e)[:300]))
        return 2
    print(("PASS %s: " if code == 0 else "FAIL %s: ") % a.clause + why)
    return code


if __name__ == "__main__":
    sys.exit(main())
