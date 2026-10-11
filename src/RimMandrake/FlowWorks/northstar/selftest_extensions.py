#!/usr/bin/env python3
"""Offline selftest for the FlowWorks core/extension split (densification 2026-10-05). No game, no bridge.

Proves: (1) validation.CORE_LIVE_IDS is exactly a clean v2 --mock run's row ids, in order; (2) every ROW_SHOWS /
ROW_TOGGLES key is a real core row and every bar it names is in the walk's checklist; (3) the union of core + extension
claims covers every must-show and cannot-show bar and every Mod Settings toggle, and EXTENSION_ONLY_BARS is exactly
the bars no core row claims; (4) the seven deleted toggle chains are gone and their toggles are still claimed by a
core row; (5) no extension component id collides with a core row id; (6) the coverage join can FAIL (a planted
unclaimed bar comes back uncovered, a stripped toggle comes back uncovered) -- a check that cannot fail proves nothing;
(7) every walk `## must be true` line carries a coverage arrow and `## extended` holds only `- E<n>. ... -> ...` lines
(debug_process.md section 3 and 6b; FLOWWORKS_CHECKOUT_SCOPE_1), each with a planted-line sanity probe.
"""
import re
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
    owed = vm.RIVER_TOGGLES_OWED + vm.HOSE_TOGGLES_OWED + vm.EXTENSION_TOGGLES_OWED
    if sorted(tog_unc) != sorted(owed):
        probs.append("toggles uncovered %s != the named owed lists RIVER_ + HOSE_ + EXTENSION_TOGGLES_OWED %s" % (tog_unc, owed))
    # hose port G6.1: the harness covers exactly the switches the C# settings sections expose (typed registry)
    import settings_registry as REG
    reg = set(REG.toggles())
    if reg != set(V.toggles) | set(vm.TOGGLES_NOT_ON_FLOOR) or set(V.toggles) & set(vm.TOGGLES_NOT_ON_FLOOR):
        probs.append("toggle floor vs registry: registry only %s, harness only %s, on both lists %s" % (
            sorted(reg - set(V.toggles) - set(vm.TOGGLES_NOT_ON_FLOOR)), sorted((set(V.toggles) | set(vm.TOGGLES_NOT_ON_FLOOR)) - reg),
            sorted(set(V.toggles) & set(vm.TOGGLES_NOT_ON_FLOOR))))
    core_bars = {b for v in list(vm.ROW_SHOWS.values()) + list(vm.HOSE_ROW_SHOWS.values()) for b in v}
    # the hose rows (moved from Gimme Some Slack at the hose port): every bar they name is a checklist bar
    probs += ["HOSE_ROW_SHOWS %s names %s, not a checklist bar" % (rid, x) for rid, b in vm.HOSE_ROW_SHOWS.items() for x in b if x not in bars]
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
    clash = ext_ids & (set(vm.CORE_LIVE_IDS) | set(vm.OFFLINE_IDS) | set(vm.HOSE_ROW_SHOWS) | set(vm.HOFF.OFFLINE_IDS))
    if clash:
        probs.append("extension component ids collide with core rows: %s" % sorted(clash))

    # sanity probes: the join must be able to fail
    if floor.uncovered_shows(list(ns["must_show"]) + ["zz_planted_bar"], comps) != ["zz_planted_bar"]:
        probs.append("sanity: a planted unclaimed bar did not come back uncovered")
    stripped = [dict(c, toggle=None) if c["toggle"] == "viscosityEnabled" else c for c in comps]
    if "viscosityEnabled" not in floor.uncovered(V.toggles, stripped):
        probs.append("sanity: stripping viscosityEnabled claims did not uncover it")

    # (7) walk coverage arrows and the extended section (FLOWWORKS_CHECKOUT_SCOPE_1)
    walk_text = open(os.path.join(ROOT, "design", "validation_walks", "RimMandrake", "FlowWorks.md"), encoding="utf-8").read()
    probs += walk_shape_probs(walk_text)
    if not walk_shape_probs(walk_text.replace("## must be true\n", "## must be true\n- zz planted line\n", 1)):
        probs.append("sanity: a planted arrowless must-be-true line was not caught")
    if not walk_shape_probs(walk_text.replace("## extended\n", "## extended\n- zz planted line\n", 1)):
        probs.append("sanity: a planted malformed extended line was not caught")

    # P12 (hose port step 0): _report_rows never certifies a SKIP (or unknown) row; PASS stays PASS, FAIL stays FAIL
    probs += _report_rows_adapter_probs(vm)
    # (8) code review 2026-10-11: checks that could PASS without a reading now FAIL or record UNMEASURED
    probs += _vacuous_check_probs(EXT)

    # the offline tier's declared ids are the ids it really emits (a stale list declared 3 phantom components)
    with contextlib.redirect_stdout(io.StringIO()):
        off = [r["id"] for r in vm.offline_rows()]
    if off != vm.OFFLINE_IDS:
        probs.append("OFFLINE_IDS != offline_rows() ids: missing %s extra %s" % (
            [i for i in off if i not in vm.OFFLINE_IDS], [i for i in vm.OFFLINE_IDS if i not in off]))
    probs += _core_rows_from_probs(vm)

    print("selftest_extensions: %s -- %d core rows, %d extension chains / %d components, %d bars (%d core, %d "
          "extension-only), %d toggles" % ("PASS" if not probs else "FAIL", len(ids), len(ext_names), len(ext_ids),
                                           len(bars), len(bars & core_bars), len(vm.EXTENSION_ONLY_BARS),
                                           len(V.toggles)))
    for p in probs:
        print("  - " + p)
    return 0 if not probs else 1


def _section(text, head):
    if ("\n## %s\n" % head) not in text:
        return None
    return text.split("\n## %s\n" % head, 1)[1].split("\n## ", 1)[0]


def walk_shape_probs(text):
    """Every `- ` line under `## must be true` carries a coverage arrow; `## extended` exists and its `- ` lines are
    `- E<n>. <what> -> <flag or UNBUILT>; ...` (debug_process.md 6b)."""
    out = []
    mbt = _section(text, "must be true")
    if mbt is None:
        return ["walk has no ## must be true section"]
    out += ["walk line has no coverage arrow: %s" % ln[:70] for ln in mbt.splitlines()
            if ln.startswith("- ") and "\u2192" not in ln]
    ext = _section(text, "extended")
    if ext is None:
        return out + ["walk has no ## extended section"]
    out += ["extended line is not '- E<n>. ... -> ...': %s" % ln[:70] for ln in ext.splitlines()
            if ln.startswith("- ") and not re.match(r"- E\d+\. .+ -> \S", ln)]
    return out


def _report_rows_adapter_probs(vm):
    import contextlib

    class _C(object):
        def __init__(self, name):
            self.name, self.verdict, self.detail, self.evidence = name, "PASS", "", []

    class _T(object):
        def __init__(self):
            self.components, self.upstream_failed = [], False

        def _guard(self):
            return True

        @contextlib.contextmanager
        def component(self, rid, toggle=None, shows=None):
            c = _C(rid)
            self.components.append(c)
            try:
                yield c
            except vm.ExpectationFailed as e:
                c.verdict, c.detail = "FAIL", str(e)

    t = _T()
    rows = [{"id": "r_pass", "status": "PASS", "detail": "x"}, {"id": "r_skip", "status": "SKIP", "detail": "skipped"},
            {"id": "r_fail", "status": "FAIL", "cls": "MOD", "detail": "bad"},
            {"id": "r_unb", "status": "UNBUILT", "detail": "n"}, {"id": "r_odd", "status": "WEIRD", "detail": "n"}]
    vm._report_rows(t, rows)
    got = {c.name: c.verdict for c in t.components}
    want = {"r_pass": "PASS", "r_skip": "UNMEASURED", "r_fail": "FAIL", "r_unb": "UNMEASURED", "r_odd": "UNMEASURED"}
    return [] if got == want else ["_report_rows adapter: got %s want %s (a SKIP must never certify)" % (got, want)]


def _core_rows_from_probs(vm):
    """An aborted v2 result that never reached most rows: every CORE_LIVE_IDS id still comes back, the missing ones
    UNMEASURED (they used to be silently absent), and the ABORT row survives."""
    first = vm.CORE_LIVE_IDS[0]
    d = {"mode": "live", "aborted": "engine gone", "rows": [{"id": first, "status": "PASS", "detail": "x"},
                                                            {"id": "ABORT", "status": "FAIL", "detail": "engine gone"}]}
    rows = vm.core_rows_from(("validation_v2_result_X.json", d))
    by = {r["id"]: r["status"] for r in rows}
    probs = []
    if [r["id"] for r in rows[:len(vm.CORE_LIVE_IDS)]] != vm.CORE_LIVE_IDS:
        probs.append("core_rows_from: rows do not follow CORE_LIVE_IDS")
    if by.get(first) != "PASS" or by.get("ABORT") != "FAIL":
        probs.append("core_rows_from: a row the run did emit was lost")
    if any(by.get(rid) != "UNMEASURED" for rid in vm.CORE_LIVE_IDS[1:]):
        probs.append("core_rows_from: an id an aborted run never reached is not UNMEASURED")
    return probs


def _ext_run(EXT, chain, handler):
    """Run one extension chain against a scripted fake game: `handler(tool, params)` answers every bridge call.
    Returns {component name: verdict}."""
    from modcheck import TestContext      # the class modcheck.ExpectationFailed pairs with (top-level `suite`)

    class _Sess(object):
        def call(self, tool, **params):
            return {"success": True}

    class _T(TestContext):
        def bridge_call(self, tool, **params):
            if not self._guard():
                return None
            return handler(tool, params)

        def wait_ticks(self, n, _chunk=2000):
            return None

        def set_setting(self, type_name, values, persist=False):
            return None

    t = _T(_Sess())
    fn = dict(EXT.suite.chains)[chain]
    try:
        fn(t)
    except EXT.ExpectationFailed as e:          # outside any component: the runner records it FAIL
        return {"<setup>": "FAIL: %s" % e}
    return {c.name: c.verdict for c in t.components}


def _vacuous_check_probs(EXT):
    out = []
    # _expect: an empty list (list_things found nothing) used to PASS because only `is False` raised
    for cond, want in (([], True), ("", True), (0, True), (None, False), ([1], False), (True, False)):
        try:
            EXT._expect(cond, "x")
            raised = False
        except EXT.ExpectationFailed:
            raised = True
        if raised != want:
            out.append("_expect(%r) raised=%s, want %s" % (cond, raised, want))

    def base(tool, p):
        if tool == "jawa/static_call" and p.get("method") == "ProofResetRect":
            return {"result": "RESET x left=0"}
        if tool == "jawa/static_call" and p.get("method") == "ProofFillWithFluid":
            return {"result": "FILLED"}
        if tool == "jawa/flowworks_excavation_drive" or tool == "jawa/flowworks_excavation_report":
            return {"success": True, "depth": 4, "fill": 0}
        if tool == "jawa/spawn_pawn":
            return {"pawns": [{"id": "P1"}]}
        return {"success": True}

    # owed components record UNMEASURED (never PASS) and do not end the chain
    got = _ext_run(EXT, "toggle_fall_damage", base)
    if got != {"fall_damage_on": "UNMEASURED", "fall_damage_off": "UNMEASURED"}:
        out.append("owed fall_damage components: %s" % got)
    got = _ext_run(EXT, "toggle_liquid_ignition", lambda tl, p: {"things": []} if tl == "jawa/list_things" else base(tl, p))
    if got.get("liquid_ignition_off_default") != "PASS" or got.get("liquid_ignition_on") != "UNMEASURED":
        out.append("owed liquid_ignition_on must not end the chain or pass: %s" % got)
    # placement checks: list_things finding nothing FAILs (was PASS)
    got = _ext_run(EXT, "toggle_trap_trigger", lambda tl, p: {"countMatched": 0} if tl == "jawa/list_things" else base(tl, p))
    if got.get("trap_trigger_off") != "FAIL":
        out.append("trap_trigger_off with the cover gone: %s" % got)
    got = _ext_run(EXT, "toggle_trap_trigger", lambda tl, p: {"countMatched": 9} if tl == "jawa/list_things" else base(tl, p))
    if got.get("trap_trigger_off") != "PASS":
        out.append("trap_trigger_off with the cover standing: %s" % got)
    # a spawn that returns no id is UNMEASURED, not a vacuous "not held"
    got = _ext_run(EXT, "toggle_trap_trigger", lambda tl, p: {"pawns": []} if tl == "jawa/spawn_pawn"
                   else ({"countMatched": 9} if tl == "jawa/list_things" else base(tl, p)))
    if got.get("trap_trigger_off") != "UNMEASURED":
        out.append("trap_trigger_off with no pawn spawned: %s" % got)
    # pit fill OFF: a pirate missing from the census used to read drown 0 / tox 0 = PASS
    got = _ext_run(EXT, "toggle_pit_fill_effects", lambda tl, p: {"result": "FILLFX 0"} if (
        tl == "jawa/static_call" and p.get("method") == "ProofReport") else base(tl, p))
    if got.get("pit_drowning_off") != "FAIL":
        out.append("pit_drowning_off with no census row: %s" % got)
    got = _ext_run(EXT, "toggle_pit_fill_effects", lambda tl, p: {
        "result": "FILLFX 2 | P1@1,1 fluid=RM_Fluid_Water drown=0 tox=0"} if (
        tl == "jawa/static_call" and p.get("method") == "ProofReport") else base(tl, p))
    if got.get("pit_drowning_off") != "PASS":
        out.append("pit_drowning_off with a dry census row: %s" % got)
    # rivers: service_has_river_policy_and_trace_setting ended in NameError (_note undefined) after its checks passed
    import extensions_rivers as RIV
    got = _ext_run(RIV, "taken_by_land", lambda tl, p: {"success": True, "result": "TAKEN river=True traceSetting=True pending=0 gale=False"})
    if got != {"service_has_river_policy_and_trace_setting": "PASS"}:
        out.append("rivers taken_by_land on a good reply: %s" % got)
    # canal pathCost read as a number: the old substring probe `"pathCost":30` also matched 300
    for reply, want in (({"defs": [{"fields": {"pathCost": 300}}]}, 300), ({"defs": [{"fields": {"pathCost": 30}}]}, 30),
                        ({"success": False}, None)):
        if EXT._def_field(reply, "pathCost") != want:
            out.append("_def_field(%r, pathCost) != %r" % (reply, want))
    return out


if __name__ == "__main__":
    sys.exit(main())
