#!/usr/bin/env python3
"""Offline selftest for the FlowWorks core/extension split (densification 2026-10-05). No game, no bridge.

Proves: (1) validation.CORE_LIVE_IDS is exactly a clean v2 --mock run's row ids, in order; (2) every ROW_SHOWS /
ROW_TOGGLES key is a real core row and every bar it names is in the walk's checklist; (3) the union of core + extension
claims covers every must-show and cannot-show bar and every Mod Settings toggle, and EXTENSION_ONLY_BARS is exactly
the bars no core row claims; (4) the seven deleted toggle chains are gone and their toggles are still claimed by a
core row; (5) no extension component id collides with a core row id; (6) the coverage join can FAIL (a planted
unclaimed bar comes back uncovered, a stripped toggle comes back uncovered) -- a check that cannot fail proves nothing.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(MOD)))
UTILS = os.path.join(ROOT, "src", "RimMandrake", "Utils")
for _p in (HERE, UTILS, os.path.join(UTILS, "modcheck")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from modcheck import northstar, floor  # noqa: E402

DELETED = {"toggle_depth_engine": "depthEngineEnabled", "toggle_dig_to_depth": "digToDepthEnabled",
           "toggle_edge_sinks": "edgeSinksEnabled", "toggle_source_budget": "sourceBudgetEnabled",
           "toggle_sticky_limitless": "stickyLimitlessEnabled", "toggle_rain_fills": "rainFillsExcavationsEnabled",
           "toggle_superdeep_own_faction": "superdeepCapturesOwnFaction"}


def main():
    probs = []
    import importlib.util
    spec = importlib.util.spec_from_file_location("fw_validation_selftest", os.path.join(MOD, "validation.py"))
    vm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vm)
    V = vm.suite
    import validation_v2 as V2
    import extensions as EXT

    class A(object):
        mock, fresh_map, reset_settings, progress, max_job_ticks, fault = True, False, False, None, 6000, []
    import io
    import contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        res = V2.run_live(A)
    ids = [r["id"] for r in res["rows"]]
    if ids != vm.CORE_LIVE_IDS:
        probs.append("CORE_LIVE_IDS != mock row ids: missing %s extra %s" % (
            [i for i in ids if i not in vm.CORE_LIVE_IDS][:5], [i for i in vm.CORE_LIVE_IDS if i not in ids][:5]))
    if not res["green"]:
        probs.append("clean mock run not green")

    ns = northstar.parse(os.path.join(ROOT, "design", "validation_walks", "RimMandrake", "FlowWorks.md"))
    bars = set(ns["must_show"]) | set(ns["cannot_show"])
    for rid, b in vm.ROW_SHOWS.items():
        if rid not in vm.CORE_LIVE_IDS:
            probs.append("ROW_SHOWS key %s is not a core row" % rid)
        probs += ["ROW_SHOWS %s names %s, not a checklist bar" % (rid, x) for x in b if x not in bars]
    for rid, tg in vm.ROW_TOGGLES.items():
        if rid not in vm.CORE_LIVE_IDS:
            probs.append("ROW_TOGGLES key %s is not a core row" % rid)
        if tg not in V.toggles:
            probs.append("ROW_TOGGLES %s names %s, not a suite toggle" % (rid, tg))

    comps = V.components_declared()
    unc = floor.uncovered_shows(ns["must_show"], comps)
    orph = floor.orphan_shows(ns["must_show"] + ns["cannot_show"], comps)
    claimed = {s for c in comps for s in c["shows"]}
    if unc or orph or bars - claimed:
        probs.append("coverage: uncovered %s orphans %s unclaimed %s" % (unc, orph, sorted(bars - claimed)))
    tog_unc = floor.uncovered(V.toggles, comps)
    if tog_unc:
        probs.append("toggles uncovered: %s" % tog_unc)
    core_bars = {b for v in vm.ROW_SHOWS.values() for b in v}
    if sorted(bars - core_bars) != sorted(vm.EXTENSION_ONLY_BARS):
        probs.append("EXTENSION_ONLY_BARS drifted: actual %s" % sorted(bars - core_bars))

    ext_names = {n for n, _ in EXT.suite.chains}
    probs += ["deleted chain %s is back" % n for n in DELETED if n in ext_names]
    probs += ["deleted chain %s's toggle %s has no core row" % (n, t) for n, t in DELETED.items()
              if t not in vm.ROW_TOGGLES.values()]
    from modcheck.suite import _DeclarationProbe
    ext_ids = set()
    for _, fn in EXT.suite.chains:
        p = _DeclarationProbe()
        fn(p)
        ext_ids |= {c.name for c in p.components}
    clash = ext_ids & (set(vm.CORE_LIVE_IDS) | set(vm.OFFLINE_IDS))
    if clash:
        probs.append("extension component ids collide with core rows: %s" % sorted(clash))

    # sanity probes: the join must be able to fail
    if floor.uncovered_shows(list(ns["must_show"]) + ["zz_planted_bar"], comps) != ["zz_planted_bar"]:
        probs.append("sanity: a planted unclaimed bar did not come back uncovered")
    stripped = [dict(c, toggle=None) if c["toggle"] == "viscosityEnabled" else c for c in comps]
    if floor.uncovered(V.toggles, stripped) != ["viscosityEnabled"]:
        probs.append("sanity: stripping viscosityEnabled claims did not uncover it")

    print("selftest_extensions: %s -- %d core rows, %d extension chains / %d components, %d bars (%d core, %d "
          "extension-only), %d toggles" % ("PASS" if not probs else "FAIL", len(ids), len(ext_names), len(ext_ids),
                                           len(bars), len(bars & core_bars), len(vm.EXTENSION_ONLY_BARS),
                                           len(V.toggles)))
    for p in probs:
        print("  - " + p)
    return 0 if not probs else 1


if __name__ == "__main__":
    sys.exit(main())
