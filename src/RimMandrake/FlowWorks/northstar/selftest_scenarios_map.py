"""selftest_scenarios_map.py -- offline proof that the thirteen composite scenarios are fit to build (no game).

    python3 src/RimMandrake/FlowWorks/northstar/selftest_scenarios_map.py

Checks (REVIEW_SCENARIOS_BUILD_ALL_TWELVE_AT_ONCE brief): the layout fits the map without overlap (plots, lanes,
edge-sink strip, def footprints read from the Defs' own <size>); every scenario has in-world signs (title label,
try lines, a sign book with DO/LOOK/DECIDE) and a DEFERRED label + book for every piece not built; every design piece
is staged (its ref resolves in the setup) or DEFERRED (with why and item); no defName is staged that src/ or the game's
Data does not define; every station of the old gallery and every north-star bar of design §4.2 lands in a scenario
(or its stated home); the MOCK build verifies all plots; the Stage 0 swim-out harness gives the right verdict for each
simulated outcome. Sanity probes first: each instrument is shown a planted fault and must see it.
MOCK results prove the staging data and harness, never the game.
"""
import copy
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.dirname(HERE), os.path.join(HERE, "..", "..", "Utils")]
import scenarios_map as M  # noqa: E402
import scenarios as SC  # noqa: E402
from scenarios import common as C  # noqa: E402
from scenarios import c03_labyrinth_rescue as C3  # noqa: E402
from scenarios import stage0_swim_pit as S0  # noqa: E402
from scenarios.mock_bridge import MockBridge  # noqa: E402

FAILS = []


def check(name, ok, detail=""):
    print("%s %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else "  -> %s" % str(detail)[:600]))
    if not ok:
        FAILS.append(name)


def main():
    names, cnt = C.def_index()
    facts = C.def_facts()
    check("def index sees src and the game (%d src, %d game files)" % (cnt["src"], cnt["game"]),
          cnt["src"] > 1000 and cnt["game"] > 1000 and "Wall" in names and "RM_HoseReel" in names, cnt)
    check("def facts read sizes (RM_HoseReel 2x2, Battery 1x2)",
          (C.fact(facts, "RM_HoseReel") or {}).get("size") == (2, 2) and (C.fact(facts, "Battery") or {}).get("size") == (1, 2))
    placed = M.placed_c()
    # ---------------------------------------------------------------- sanity probes: planted faults must be seen
    bad = copy.deepcopy(placed)
    bad[0]["sc"] = copy.deepcopy(bad[0]["sc"])
    u = bad[0]["sc"]["setup"]
    first = u["build"][0]
    u["build"] = u["build"] + [("RM_LiquidTank", first[1], first[2], None, None), ("RM_NoSuchDef_Zz", 1, 1, None, None)]
    bad[0]["sc"]["pieces"] = bad[0]["sc"]["pieces"] + [C.staged("ghost", "build", "RM_HoseReel", (0, 0)),
                                                      dict(C.deferred("no item", "why", "", (0, 0)))]
    probs = M.scenario_check(bad[0], facts, names)
    check("probe: an overlapping building is seen", any("overlaps" in p for p in probs), probs)
    check("probe: an unknown defName is seen", any("RM_NoSuchDef_Zz" in p for p in probs), probs)
    check("probe: an unresolvable staged piece is seen", any("'ghost'" in p for p in probs), probs)
    check("probe: a DEFERRED piece without its item is seen", any("without why/item" in p for p in probs), probs)
    moved = copy.deepcopy(placed)
    moved[1]["rect"] = moved[0]["rect"]
    check("probe: two plots on top of each other are seen", any("closer than" in p for p in M.layout_check(moved)))
    mb = MockBridge(defs={"Wall"})
    check("probe: the mock refuses an unknown def", mb.call("jawa/build_batch", ops="Bogus:1,1").get("survived") == 0)
    # ---------------------------------------------------------------- the real plan
    check("thirteen scenarios C1..C13 numbered 1..13",
          [s["id"] for s in SC.ALL] == ["C%d" % i for i in range(1, 14)] and [s["n"] for s in SC.ALL] == list(range(1, 14)))
    probs = M.layout_check(placed, facts, names)
    check("map-C layout fits: 11 plots, lanes, edge strip, footprints, defs, pieces", not probs, probs)
    river = M.synthetic_river()
    c1, plan, unplaced, notes = M.placed_r(river, (M.MAP_SIZE, M.MAP_SIZE))
    check("map R (synthetic river): C1 anchored and clean", c1 is not None and not M.scenario_check(c1, facts, names),
          (c1 and M.scenario_check(c1, facts, names), notes))
    check("map R: C11 places all eight creek stations clear of C1", len(plan) == 8 and not unplaced, unplaced)
    check("map R: no creek anchor inside C1's plot",
          all(not (c1["rect"][0] <= cr[0][0] < c1["rect"][0] + c1["rect"][2] and
                   c1["rect"][1] <= cr[0][1] < c1["rect"][1] + c1["rect"][3]) for _, cr, _ in plan))
    every = placed + [c1]
    # ---------------------------------------------------------------- signs
    labels = M.label_ops(every)
    books = M.sign_ops(every)
    for p in every:
        sc = p["sc"]
        sid = sc["id"]
        title = "%s  %s" % (sid, sc["name"].upper())
        check("%s: title label with number and name" % sid, title in labels)
        check("%s: try lines in the world" % sid, ("%s try 1:" % sid) in labels)
        bk = [b for b in books if b.split("|")[2].startswith("SIGN %s " % sid)]
        check("%s: sign book with DO, LOOK, DECIDE and START" % sid,
              bk and "DO:" in bk[0] and "LOOK:" in bk[0] and "DECIDE:" in bk[0] and "START:" in bk[0], bk[:1])
        defs = [pc for pc in sc["pieces"] if pc["status"] == "DEFERRED"]
        for k, pc in enumerate(defs, 1):
            check("%s: DEFERRED %r labelled and booked" % (sid, pc["name"][:40]),
                  ("DEFERRED: " + pc["name"]) in labels and any(b.split("|")[2].startswith("SIGN %s.D%d " % (sid, k))
                                                                 for b in books))
        check("%s: every piece staged or DEFERRED, at least one staged" % sid,
              all(pc["status"] in ("staged", "DEFERRED") for pc in sc["pieces"])
              and any(pc["status"] == "staged" for pc in sc["pieces"]))
    c11 = SC.BY_ID["C11"]
    check("C11: pieces are the eight R stations (+ control) or DEFERRED",
          {pc["d"] for pc in c11["pieces"] if pc.get("key") == "rv_station"} == set(SC.c11_prospectors_creek.STATION_IDS))
    check("S0 board label and book", "S0  FLOWWORKS COMPOSITE SCENARIOS" in labels and any("|SIGN S0 " in b for b in books))
    # ---------------------------------------------------------------- C3's goal read, offline
    short = C.route_len(C3.BLOCKED, C3.HOSE_START, C3.PIT_LIP, C3.SIZE)
    long_ = C.route_len(C3.BLOCKED | {C3.D1}, C3.HOSE_START, C3.PIT_LIP, C3.SIZE)
    check("C3: short way (d1 open) fits one 40-cell hose (route %s + 2 reel cells)" % short,
          short is not None and short + 2 <= C.HOSE_CELLS, short)
    check("C3: long way (d1 walled) needs the relay but fits two hoses (route %s)" % long_,
          long_ is not None and C.HOSE_CELLS < long_ + 2 <= 2 * C.HOSE_CELLS, long_)
    check("C3: the dead end does not lead to the pit",
          C.route_len(C3.BLOCKED | {C3.D1, (35, 26), (36, 26), (37, 26), (38, 26)}, C3.HOSE_START, C3.PIT_LIP, C3.SIZE) is None)
    # ---------------------------------------------------------------- coverage vs the old gallery and the bars
    import review_map as RVM
    import review_map_rivers as RV
    ex = set().union(*[set(s["exercises"]) for s in SC.ALL])
    stations = set(RVM.SETUPS) | {"river_ford", "river_works_looks"} | {s["id"] for s in RV.STATIONS}
    homes = {"land_liquids", "land_liquids_2", "land_liquids_3", "many_waters", "land_shores", "land_settings"}
    check("every old station lands in a scenario or its stated home (design §4.1)", stations - ex <= homes,
          sorted(stations - ex - homes))
    design = open(os.path.join(M.REPO, "design", "RimMandrake", "flowworks_composite_review_scenarios_2026-10-21.md"),
                  encoding="utf-8").read()
    bars = set(re.findall(r"^\| `([a-z_]+)` \|", design.split("### 4.2")[1].split("### 4.3")[0], re.M))
    check("every north-star bar of design §4.2 (%d) is exercised" % len(bars), len(bars) > 70 and bars <= ex,
          sorted(bars - ex))
    # ---------------------------------------------------------------- MOCK build + verify
    res, B = M.offline_build(names | C.RUNTIME_GENERATED, placed)
    check("MOCK: all eleven map-C plots verify as staged", all(v["ok"] for v in res["verify"].values()),
          {k: v for k, v in res["verify"].items() if not v["ok"]})
    check("MOCK: every sign book placed", res["signs"] == res["sign_ops"], (res["signs"], res["sign_ops"]))
    harm = [n for n in res["notes"] if "not loaded on this mod list" not in n]
    check("MOCK: no refusal notes", not harm, harm)
    check("MOCK: no screenshot was ever asked for", not any("screenshot" in t and "mode" not in t for t, _ in B.calls))
    rv, _ = M.offline_river(names | C.RUNTIME_GENERATED)
    check("MOCK map R: C1 verifies, C11 eight stations, books placed",
          rv["verify"].get("C1", {}).get("ok") and rv["c11"] == 8 and rv["signs"] == rv["sign_ops"], rv)
    # ---------------------------------------------------------------- C13: the overflow scenario (owner card 2026-10-22)
    c13 = SC.BY_ID["C13"]
    ox, oz = M.PLOTS_C["C13"]
    spills = [(t, kw) for t, kw in B.calls if t == "jawa/static_call" and kw.get("method") == "ProofSheetSpill"]
    check("C13: six spills offered, absolute cells, switch-ON setting set before the first", len(spills) == 6 and
          all(kw["args"].split(";")[0] == "%d,%d" % (ox + c["cells"][0][0], oz + c["cells"][0][1])
              for (t, kw), c in zip(spills, c13["setup"]["after_soak"])) and
          [i for i, (t, kw) in enumerate(B.calls) if t == "jawa/mod_settings_field" and kw.get("action") == "set"
           and kw.get("field") == "sheetOverflowEnabled" and kw.get("value") == "True"]
          and [i for i, (t, kw) in enumerate(B.calls) if t == "jawa/mod_settings_field" and kw.get("action") == "set"][0]
          < [i for i, (t, kw) in enumerate(B.calls) if kw is not None and kw.get("method") == "ProofSheetSpill"][0], spills[:1])
    soak_i = [i for i, (t, kw) in enumerate(B.calls) if t == "rimworld/step_game_ticks"]
    spill_i = [i for i, (t, kw) in enumerate(B.calls) if kw.get("method") == "ProofSheetSpill"]
    check("C13: spills are offered AFTER the soak, never before", soak_i and spill_i and min(spill_i) > max(soak_i),
          (soak_i, spill_i[:2]))
    check("C13: the chemfuel spill names a real fluid", "RM_Fluid_Chemfuel" in names and
          any("RM_Fluid_Chemfuel" in c["fmt"] for c in c13["setup"]["after_soak"]))
    twelve = [s_ for s_ in SC.ALL if s_["id"] != "C13"]
    ovf = [s_ for s_ in twelve if any("overflow" in (pc.get("why") or "") for pc in s_["pieces"])]
    check("C1-C12: every scenario that defers overflow says it ships OFF and points at C13",
          len(ovf) >= 5 and all("C13" in pc["why"] for s_ in ovf for pc in s_["pieces"] if "overflow" in (pc.get("why") or "")),
          [s_["id"] for s_ in ovf])
    bad13 = copy.deepcopy(placed[-1])
    check("probe: a spill outside the plot is seen", (lambda b_: any("outside" in q for q in M.scenario_check(b_, facts, names)))(
        dict(bad13, sc=dict(bad13["sc"], setup=dict(bad13["sc"]["setup"], after_soak=[dict(typ="T", method="M", fmt="{0}",
                                                                                           cells=[(99, 99)])])))))
    # ---------------------------------------------------------------- Stage 0 harness
    for label, rule, want in (("2 m", lambda f: f >= 4, "PASS"), ("brim", lambda f: f >= 8, "PASS_AT_BRIM"),
                              ("never", None, "FAIL")):
        v, rows = S0.run(MockBridge(swim_rule=rule), M.STAGE0["rect"][:2])
        check("Stage 0 harness (simulated swimmer gets out %s) -> %s" % (label, want), v == want, (v, rows[-1:]))
    v, rows = S0.run(MockBridge(swim_rule=None), M.STAGE0["rect"][:2])
    check("Stage 0: dry control holds (row S0SWIM_dry_held PASS)", any(r["row"] == "S0SWIM_dry_held" and r["status"] == "PASS"
                                                                       for r in rows))
    class Blind(MockBridge):                      # probe: a bridge that cannot read a pawn's position
        def call(self, tool, **kw):
            r = MockBridge.call(self, tool, **kw)
            return dict(r, pawns=[]) if tool == "jawa/pawn_get" else r
    vb, rb = S0.run(Blind(swim_rule=lambda f: True), M.STAGE0["rect"][:2])
    check("Stage 0: an unreadable position is UNMEASURED, never PASS or FAIL", vb == "UNMEASURED", (vb, rb[-1:]))
    check("Stage 0 site does not overlap any plot", not any(C_ov(M.STAGE0["rect"], p["rect"]) for p in placed))
    print("\n%d FAIL" % len(FAILS) if FAILS else "\nALL PASS")
    return 1 if FAILS else 0


def C_ov(a, b):
    return M.C_overlap(a, b, 0)


if __name__ == "__main__":
    sys.exit(main())
