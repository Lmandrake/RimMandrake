#!/usr/bin/env python3
"""selftest_heap_bisect.py - heap_bisect.py reads a ladder, a series and C# statics correctly. Synthetic inputs, offline, no game."""
import argparse
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import heap_bisect as H  # noqa: E402
import modset_builder as MB  # noqa: E402

FAILS = []


def check(name, got, want):
    if got != want:
        FAILS.append("%s: got %r, wanted %r" % (name, got, want))


def rung(tier, mods, mb):
    return {"tier": tier, "mods": mods, "mbPerLoad": mb, "pctPerLoad": None if mb is None else mb / 10.0}


def test_per_load():
    # the finding's own numbers: 3024 to 3321 over 5 loads is 59.4 MB, 2.0 percent of the first floor
    check("per_load", H.per_load([3024, 3022, 3130, 3200, 3258, 3321]), (59.4, 1.964))
    check("per_load one value", H.per_load([3024]), (None, None))
    check("per_load skips an unread load", H.per_load([100, None, 110]), (10.0, 10.0))


def test_ladder():
    smooth = [rung("a", 10, 8), rung("b", 50, 18), rung("c", 150, 38), rung("d", 316, 60)]
    check("a rise spread with the mods is smooth", H.ladder_verdict(smooth), ("smooth", None))
    jump = [rung("a", 10, 8), rung("b", 14, 9), rung("c", 20, 55), rung("d", 316, 60)]
    v, step = H.ladder_verdict(jump)
    check("one small step holding the rise is a jump", (v, step["from"], step["to"]), ("jump", "b", "c"))
    wide = [rung("a", 10, 8), rung("b", 300, 50), rung("c", 316, 60)]
    check("a step that adds most of the mods is no jump", H.ladder_verdict(wide), ("smooth", None))
    check("a flat ladder is flat", H.ladder_verdict([rung("a", 10, 8), rung("b", 50, 9), rung("c", 316, 10)]), ("flat", None))
    check("two rungs say nothing", H.ladder_verdict([rung("a", 10, 8), rung("b", 316, 60)]), ("UNMEASURED", None))
    check("an unread rung does not count", H.ladder_verdict([rung("a", 10, 8), rung("b", 50, None), rung("c", 316, 60)]),
          ("UNMEASURED", None))


def census(**fields):
    return {"rows": [{"field": k, "n": v, "gameObj": 0, "asm": "m"} for k, v in fields.items()]}


def test_growers():
    series = [census(A_leak=100 + 50 * i, B_flat=900, C_oneFill=(10 if i == 0 else 500), D_wobble=[5, 9, 4, 8, 3, 7][i]) for i in range(6)]
    got = H.growers(series)
    check("a steady climb is the only grower, at its own rate", [(g["field"], g["perLoad"]) for g in got][0], ("A_leak", 50.0))
    check("flat, one-fill and wobbling fields are no growers", sorted(g["field"] for g in got if g["field"] != "A_leak"), [])
    # a field under the census's row cap at first counts from where it appears, over the loads it spans
    late = [census(), census(), census(X=10), census(X=20), census(X=30), census(X=40)]
    check("a late field's rate spans its own loads", [g["perLoad"] for g in H.growers(late)], [10.0])


def good_sanity():
    return {"heldMB": 64.0, "releasedMB": 63.5, "unheldAliveOf1000": 3}


def test_sanity():
    ok = {"canarySeen": 64}
    check("instruments that see pass", H.sanity_problem(good_sanity(), ok), None)
    blind = dict(good_sanity(), heldMB=0.1)
    check("a floor that misses 64 MB is refused", "canary" in (H.sanity_problem(blind, ok) or ""), True)
    keep = dict(good_sanity(), unheldAliveOf1000=1000)
    check("weak references that never die are refused", "unheld" in (H.sanity_problem(keep, ok) or ""), True)
    check("a census blind to its own field is refused", "canary field" in (H.sanity_problem(good_sanity(), {"canarySeen": -1}) or ""), True)


def series(floors=(3000, 3060, 3120, 3180, 3240, 3300), games=(2, 3, 4, 5, 6, 7), tps=([3010, 3070, 3130], 60.0, "reload_ratchet")):
    n = len(floors)
    return {"ids": ["m%d" % i for i in range(14)], "save": "s", "session": "abcd1234ef", "floors": list(floors), "reserved": [4000] * n,
            "oldGames": [0] * n, "oldMaps": [0] * n, "games": list(games), "sanity": good_sanity(), "tps": tps,
            "censuses": [census(L=i * 10) for i in range(n)]}


def test_judge():
    a = argparse.Namespace(tier="t")
    row = H.reading_row(a, series())
    check("a real series measures", H.judge(row)[0], 0)
    check("its rate", row["mbPerLoad"], 60.0)
    check("its list size", row["mods"], 14)
    check("no new Game: the series is not reloads", H.judge(H.reading_row(a, series(games=(2, 2, 2, 2, 2, 2))))[0], 1)
    check("a load with no floor is UNMEASURED", H.judge(H.reading_row(a, series(floors=(3000, None, 3120, 3180, 3240, 3300))))[0], 2)
    check("five reloads are under the item's floor", H.judge(H.reading_row(a, series(floors=(1, 2, 3, 4, 5), games=(1, 2, 3, 4, 5))))[0], 2)
    check("no TPS floors is UNMEASURED", H.judge(H.reading_row(a, series(tps=(None, None, None))))[0], 2)


def test_rows_in():
    row = {"tier": "bridge", "mods": 9, "mbPerLoad": 3.0}
    text = "noise\nexit 0: " + H.ROW + json.dumps(row) + "\n" + H.ROW + '{"torn'
    check("a row is found mid-line and a torn one skipped", H.rows_in(text), [row])


CS = """
class C {
    private static readonly Dictionary<Map, int> ByMap = new Dictionary<Map, int>();
    static List<Thing> scratch;
    internal static readonly List<KeyValuePair<RM_Comp_Lure, Pawn>> Pending = new List<KeyValuePair<RM_Comp_Lure, Pawn>>();
    private static Dictionary<ThingDef, int> ByDef = new Dictionary<ThingDef, int>();
    private static readonly Dictionary<FactionDef, Faction> Cache = new Dictionary<FactionDef, Faction>();
    private static HashSet<Pawn> Seen;
    void Reset() { ByMap.Clear(); Seen = new HashSet<Pawn>(); Pending.RemoveAll(x => true); }
    void Fill() { Cache[null] = null; scratch.Add(null); }
}
"""


def test_scan():
    rows = {r["field"]: r["cleared"] for r in H.scan_text(CS)}
    check("a def-keyed table holds no game object", "ByDef" in rows, False)
    check("Clear counts", rows.get("ByMap"), ["Clear"])
    check("reassigning counts", rows.get("Seen"), ["assigned"])
    check("removal counts", rows.get("Pending"), ["Remove"])
    check("a never-emptied cache is the suspect", rows.get("Cache"), [])
    check("a declaration alone is no assignment", rows.get("scratch"), [])


def test_read_cli():
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "out.txt")
        with open(p, "w") as fh:
            fh.write("nothing here\n")
        check("no rows reads UNMEASURED", H.main(["read", p]), 2)
        with open(p, "w") as fh:
            for r in (rung("a", 10, 8), rung("b", 50, 18), rung("c", 316, 60)):
                fh.write(H.ROW + json.dumps(r) + "\n")
        check("rows read", H.main(["read", p]), 0)


def test_tiers():
    # the ladder's own rungs exist and nest, and the half is a prefix in the full list's order
    full, half = MB.TIERS["heap_full_on_steve"]["want"], MB.TIERS["heap_full_on_steve_half"]["want"]
    check("half is inside the whole", set(half) - set(full), set())
    check("both carry the bridge", (MB.BRIDGE in full, MB.BRIDGE in half), (True, True))
    with open(MB.FULL_BACKUP, encoding="utf-8") as fh:
        text = fh.read().lower()
    check("every rung's mod is on the full list", [p for p in full if "<li>%s</li>" % p not in text], [])
    with open(os.path.join(H.REPO, "infrastructure", "state", "live_proofs", "HEAP_BISECT_RELOAD_RETAINERS_59_MB_SLOPE.txt")) as fh:
        proofs = fh.read()
    for t in ("bridge", "fw_gss_sitting", "pyrelands", "heap_full_on_steve_half", "heap_full_on_steve"):
        check("rung %s is a tier" % t, t in MB.TIERS, True)
        check("rung %s is proved" % t, "--tier %s <" % t in proofs, True)


def main():
    for t in (test_per_load, test_ladder, test_growers, test_sanity, test_judge, test_rows_in, test_scan, test_read_cli, test_tiers):
        t()
    for f in FAILS:
        print("FAIL " + f)
    print("selftest_heap_bisect: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
