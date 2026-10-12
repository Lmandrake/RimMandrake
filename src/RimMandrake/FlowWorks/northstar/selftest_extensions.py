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
    probs += _hose_rows_from_probs(vm)

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


def _hose_rows_from_probs(vm):
    """A certifiable proof_hose result whose FAIL sits OUTSIDE HOSE_LIVE_IDS (an MX_H05 matrix scene): the row must reach
    modcheck (hose_live_rows used to read only HOSE_LIVE_IDS, so the FAIL was invisible and the suite read green)."""
    first = vm.HOSE_LIVE_IDS[0]
    d = {"mode": "live", "certifiable": True, "rows": [{"id": first, "status": "PASS", "class": "MOD", "detail": "x"},
                                                       {"id": "MX_H05_probe", "status": "FAIL", "class": "MOD", "detail": "y"}]}
    rows = vm.hose_rows_from(("proof_hose_X.json", d))
    by = {r["id"]: r["status"] for r in rows}
    probs = []
    if [r["id"] for r in rows[:len(vm.HOSE_LIVE_IDS)]] != vm.HOSE_LIVE_IDS:
        probs.append("hose_rows_from: rows do not follow HOSE_LIVE_IDS")
    if by.get("MX_H05_probe") != "FAIL":
        probs.append("hose_rows_from: a FAIL row outside HOSE_LIVE_IDS was dropped")
    if by.get(first) != "PASS" or any(by.get(rid) != "UNMEASURED" for rid in vm.HOSE_LIVE_IDS[1:]):
        probs.append("hose_rows_from: an emitted row was lost or a missing id is not UNMEASURED")
    return probs


_PNG = []


def _tiny_png():
    """One 2x2 PNG in a temp dir, reused: enough for _diptych to compose, nothing written into the repo."""
    if not _PNG:
        import tempfile
        from PIL import Image
        p = os.path.join(tempfile.mkdtemp(prefix="selftest_ext_"), "frame.png")
        Image.new("RGB", (2, 2)).save(p)
        _PNG.append(p)
    return _PNG[0]


def _ext_run(EXT, chain, handler, keep=None):
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

        def screenshot(self, *a, **k):      # never the OS-desktop fallback (it wrote 4K .bmp files into Transient/)
            return _tiny_png()

    t = _T(_Sess())
    fn = dict(EXT.suite.chains)[chain]
    try:
        fn(t)
    except EXT.ExpectationFailed as e:          # outside any component: the runner records it FAIL
        return {"<setup>": "FAIL: %s" % e}
    if keep is not None:
        keep.extend(t.components)
    return {c.name: c.verdict for c in t.components}


def _things(rows):
    """jawa/list_things' REAL success shape (JawaBenchTerrainTools.cs ListThings): rows carry id/def and TOP-LEVEL x/z."""
    rows = [dict(id="T%d" % i, def_=None, **r) for i, r in enumerate(rows)]
    for r in rows:
        r["def"] = r.pop("def_") or r.get("def") or "RM_LiquidFlame"
    return {"success": True, "things": rows, "scanned": len(rows), "countReturned": len(rows), "countMatched": len(rows),
            "isCompleteList": True, "truncated": 0, "pawnsSkipped": 0, "perDef": {}, "ticksGame": 1}


def _rect_xz(p):
    x, z = str(p.get("rect", "")).split(",")[:2]
    return int(x), int(z)


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
    # liquid ignition: the OFF side counted vanilla Fire on a WATER fill, so an empty reply PASSed it (re-review
    # 2026-10-11); both sides are owed now and must never PASS
    got = _ext_run(EXT, "toggle_liquid_ignition", lambda tl, p: _things([]) if tl == "jawa/list_things" else base(tl, p))
    if got != {"liquid_ignition_off_default": "UNMEASURED", "liquid_ignition_on": "UNMEASURED"}:
        out.append("liquid ignition sides must both be owed (UNMEASURED): %s" % got)
    # placement checks: list_things finding nothing FAILs (was PASS)
    got = _ext_run(EXT, "toggle_trap_trigger", lambda tl, p: _things([]) if tl == "jawa/list_things" else base(tl, p))
    if got.get("trap_trigger_off") != "FAIL":
        out.append("trap_trigger_off with the cover gone: %s" % got)
    got = _ext_run(EXT, "toggle_trap_trigger", lambda tl, p: _things([{"x": 0, "z": 0}] * 9) if tl == "jawa/list_things" else base(tl, p))
    if got.get("trap_trigger_off") != "PASS":
        out.append("trap_trigger_off with the cover standing: %s" % got)
    # a spawn that returns no id is UNMEASURED, not a vacuous "not held"
    got = _ext_run(EXT, "toggle_trap_trigger", lambda tl, p: {"pawns": []} if tl == "jawa/spawn_pawn"
                   else (_things([{"x": 0, "z": 0}] * 9) if tl == "jawa/list_things" else base(tl, p)))
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
    comps = []
    got = _ext_run(RIV, "taken_by_land", lambda tl, p: {"success": True, "result": "TAKEN river=True traceSetting=True pending=0 gale=False"},
                   keep=comps)
    if got != {"service_has_river_policy_and_trace_setting": "PASS"}:
        out.append("rivers taken_by_land on a good reply: %s" % got)
    # ... and the note it leaves must RENDER: {"note","value"} evidence died in report._row with KeyError 'call'
    from modcheck import report as REPORT
    for c in comps:
        try:
            REPORT._row(c.as_dict())
        except Exception as e:              # noqa: BLE001
            out.append("rivers %s does not render in the modcheck sheet: %r" % (c.name, e))
    out += _new_probes(EXT, RIV, base)
    out += _repair_probes(EXT, base)
    # canal pathCost read as a number: the old substring probe `"pathCost":30` also matched 300
    for reply, want in (({"defs": [{"fields": {"pathCost": 300}}]}, 300), ({"defs": [{"fields": {"pathCost": 30}}]}, 30),
                        ({"success": False}, None)):
        if EXT._def_field(reply, "pathCost") != want:
            out.append("_def_field(%r, pathCost) != %r" % (reply, want))
    return out


def _declared_toggles(M, chain):
    from modcheck.suite import _DeclarationProbe
    p = _DeclarationProbe()
    dict(M.suite.chains)[chain](p)
    return {c.name: c.toggle for c in p.components}


FILLIN_OK = {"jawa/flowworks_job_probe": {"success": True, "pawn": {"id": "P1", "workTypeDisabled": False, "canReach": True},
                                           "workGiver": {"hasJobOnCell": True, "jobDef": "RM_FillInCanalJob"}},
             "jawa/ordered_job": {"accepted": True}}


def _repair_probes(EXT, base):
    """2026-10-11 live repairs (PIT_CHAINS_REPAIR_STALE_SINCE_RULING, EXT_FLUID_SET_REPAIR_ASKED_TOO_LATE,
    GOLDEN_SITE_REBUILD_RIVER_RUNS_DRY): each case is red on the code the live run used."""
    out = []

    # pits: an open pit is entered only by force (FLOWWORKS_PIT_FALL_ONLY_FORCED_1); no chain may order a pawn in
    def pit(launched=True, held=True):
        seen = {"order": 0, "fly": 0}

        def h(tl, p):
            if tl == "jawa/order_pawn":
                seen["order"] += 1
            if tl == "jawa/static_call" and p.get("method") == "ProofForcedFlyer":
                seen["fly"] += 1
                pid, x, z = p.get("args").split(",")
                return {"result": "FLYER id=%s from=0,0 to=%s,%s depth=4 launched=%s" % (pid, x, z, launched)}
            if tl == "jawa/flowworks_pit_report":
                return {"success": True, "pawns": [{"id": "P1", "held": held}]}
            return base(tl, p)
        return seen, h
    for chain, comp in (("plot_G_pit", "pit_captures_hostile"), ("toggle_superdeep_capture", "superdeep_capture_on"),
                        ("toggle_ladder_required", "ladder_required_on")):
        for launched, held, want in ((True, True, "PASS"), (True, False, "FAIL"), (False, True, "UNMEASURED")):
            seen, h = pit(launched, held)
            got = _ext_run(EXT, chain, h).get(comp)
            if got != want:
                out.append("%s/%s forced launched=%s held=%s: %s, want %s" % (chain, comp, launched, held, got, want))
            if seen["order"]:
                out.append("%s orders a pawn into an open pit (%d order_pawn): the path veto refuses it" % (chain, seen["order"]))
            if not seen["fly"]:
                out.append("%s never forces a pawn in (no ProofForcedFlyer)" % chain)
    seen, h = pit(True, True)       # ON: the first forced pirate is held; OFF: the second is not
    h1 = lambda tl, p: ({"success": True, "pawns": [{"id": "P1", "held": seen["fly"] < 2}]}  # noqa: E731
                        if tl == "jawa/flowworks_pit_report" else h(tl, p))
    got = _ext_run(EXT, "toggle_superdeep_capture", h1)
    if got.get("superdeep_capture_off") != "PASS":
        out.append("superdeep_capture_off: forced in, not held, capture OFF must PASS: %s" % got)
    seen, h = pit(True, True)
    h2 = lambda tl, p: {"success": True, "pawns": []} if tl == "jawa/flowworks_pit_report" else h(tl, p)  # noqa: E731
    if _ext_run(EXT, "toggle_superdeep_capture", h2).get("superdeep_capture_off") != "UNMEASURED":
        out.append("superdeep_capture_off: a pirate on no pit cell must be UNMEASURED, not a vacuous 'not held'")

    # tar: the body's fluid is its terrain's; read back fresh + tar, never via ActiveFluid (refused on a shared map)
    def tar(formed=True, fluid="RM_Fluid_Tar"):
        seen = {"active": 0}

        def h(tl, p):
            if tl == "jawa/flowworks_set_active_fluid":
                seen["active"] += 1
                return {"success": False, "message": "REFUSED: ActiveFluid must be set before first classification"}
            if tl == "jawa/flowworks_body_report":
                return {"success": True, "classified": True, "formedByThisCall": formed, "body": {"id": 7}}
            if tl == "jawa/static_call" and p.get("method") == "ProofCensus":
                return {"result": "FLUIDID wet 0 | recorded 0 | unrecorded 0 | fluids [] | bodies [3:RM_Fluid_Water,7:%s]" % fluid}
            return base(tl, p)
        return seen, h
    for formed, fluid, want in ((True, "RM_Fluid_Tar", "PASS"), (False, "RM_Fluid_Tar", "UNMEASURED"),
                                (True, "RM_Fluid_Water", "FAIL")):
        seen, h = tar(formed, fluid)
        got = _ext_run(EXT, "plot_C2_tar_and_fluids", h).get("tar_fluid_set")
        if got != want:
            out.append("tar_fluid_set formed=%s fluid=%s: %s, want %s" % (formed, fluid, got, want))
        if seen["active"]:
            out.append("plot_C2 still asks for an ActiveFluid switch (refused on any shared map)")
    # slime: each cell takes the NAMED fluid; a cell that reports another fluid FAILs
    for res, want in (("FILLED (1,1) F=3 fluid=RM_Fluid_SlimeGreen", "PASS"), ("FILLED (1,1) F=3 fluid=RM_Fluid_Water", "FAIL")):
        got = _ext_run(EXT, "plot_F_slime", lambda tl, p: {"result": res} if (
            tl == "jawa/static_call" and p.get("method") == "ProofFillWithFluid") else base(tl, p)).get("slime_fluid_set")
        if got != want:
            out.append("slime_fluid_set on %r: %s, want %s" % (res, got, want))

    # fill-in: a colonist that cannot mine is UNMEASURED; the WorkGiver refusing the designated cell is the mod's FAIL
    def fillin(probe, depth_after):
        def h(tl, p):
            if tl == "jawa/flowworks_job_probe":
                return probe
            if tl == "jawa/ordered_job":
                return {"accepted": True}
            if tl == "jawa/flowworks_excavation_report":
                return {"success": True, "depth": depth_after, "fill": 0}
            return base(tl, p)
        return _ext_run(EXT, "toggle_fill_in", h).get("fill_in_on")
    ok = FILLIN_OK["jawa/flowworks_job_probe"]
    for probe, d, want in ((ok, 0, "PASS"), (ok, 1, "FAIL"),
                           (dict(ok, pawn={"id": "P1", "workTypeDisabled": True}), 1, "UNMEASURED"),
                           (dict(ok, workGiver={"hasJobOnCell": False}), 1, "FAIL")):
        if fillin(probe, d) != want:
            out.append("fill_in_on probe=%r D=%d: %s, want %s" % (probe.get("pawn"), d, fillin(probe, d), want))
    # fill-in OFF: the mod must be ASKED with a capable pawn; a WorkGiver still handing the job with the setting off FAILs
    def fillin_off(has_job):
        def h(tl, p):
            if tl == "jawa/flowworks_job_probe":         # ON (first probe) hands the job; OFF answers `has_job`
                st_off["probes"] = st_off.get("probes", 0) + 1
                return dict(ok, workGiver={"hasJobOnCell": has_job or st_off["probes"] == 1,
                                           "jobDef": "RM_FillInCanalJob", "shouldSkip": False})
            if tl == "jawa/ordered_job":
                return {"accepted": True}
            if tl == "jawa/flowworks_excavation_report":    # the ON cell is read first and filled in; OFF's stays D=1
                st_off["n"] += 1
                return {"success": True, "depth": 0 if st_off["n"] == 1 else 1, "fill": 0}
            return base(tl, p)
        st_off = {"n": 0}
        return h
    for has_job, want in ((False, "PASS"), (True, "FAIL")):
        got = _ext_run(EXT, "toggle_fill_in", fillin_off(has_job))
        if got.get("fill_in_off") != want:
            out.append("fill_in_off with hasJobOnCell=%s: %s, want %s (%s)" % (has_job, got.get("fill_in_off"), want, got))
    # fire: an unlit run is UNMEASURED (the old vanilla-Fire light silently never took)
    for lit, flames, want in (("REFUSED", 1, "UNMEASURED"), ("LIT (1,1)", 0, "FAIL"), ("LIT (1,1)", 1, "PASS")):
        got = _ext_run(EXT, "plot_E_fire", lambda tl, p: {"result": lit} if (
            tl == "jawa/static_call" and p.get("method") == "ProofIgnite") else (
            _things([{"x": 0, "z": 0}] * flames) if tl == "jawa/list_things" else base(tl, p))).get("fire_reaches_reservoir")
        if got != want:
            out.append("fire_reaches_reservoir lit=%s flames=%d: %s, want %s" % (lit, flames, got, want))

    # pond: a pond with stock left is UNMEASURED; an empty pond whose channel still gains is FAIL
    def pond(stock, gain):
        st = {"n": None}          # reports counted from the first stock read: 12 for F before the wait, then after

        def h(tl, p):
            if tl == "jawa/flowworks_body_report":
                if p.get("classify") is False:      # _pond_stock's read, not pond_before_draw's classification
                    st["n"] = st["n"] or 0
                return {"success": True, "formedByThisCall": True, "body": {"id": 1, "stock": stock, "limitless": False}}
            if tl == "jawa/flowworks_excavation_report":
                after = st["n"] is not None and st["n"] >= 12
                if st["n"] is not None:
                    st["n"] += 1
                return {"success": True, "depth": 3, "fill": 2 if (gain and after) else 1, "isSourceCell": False}
            return base(tl, p)
        return _ext_run(EXT, "plot_D_limited_pond", h).get("pond_empty_stops_flow")
    for stock, gain, want in ((5.0, False, "UNMEASURED"), (0.0, False, "PASS"), (0.4, False, "PASS"), (0.0, True, "FAIL")):
        if pond(stock, gain) != want:
            out.append("pond_empty_stops_flow stock=%s gain=%s: %s, want %s" % (stock, gain, pond(stock, gain), want))
    # pond_recharge_visible reads the stock: flat FAILs (it used to claim refillEnabled with frames only), rising PASSes
    def recharge(rise):
        st = {"reads": 0}

        def h(tl, p):
            if tl == "jawa/flowworks_body_report":
                if p.get("classify") is False:
                    st["reads"] += 1
                return {"success": True, "formedByThisCall": True,
                        "body": {"id": 1, "limitless": False, "stock": 0.2 * st["reads"] if rise else 0.2}}
            if tl == "jawa/flowworks_excavation_report":
                return {"success": True, "depth": 3, "fill": 1, "isSourceCell": False}
            return base(tl, p)
        return _ext_run(EXT, "plot_D_limited_pond", h).get("pond_recharge_visible")
    for rise, want in ((False, "FAIL"), (True, "PASS")):
        if recharge(rise) != want:
            out.append("pond_recharge_visible rise=%s: %s, want %s" % (rise, recharge(rise), want))
    # dig_finds: the letter is owed only for a FIRST find (Scribed found-list); on a re-run save no letter is right
    def digs(first0, letter, finds=True):
        g = {"depth": 0, "finds": 0, "first": first0, "letters": 0, "cuts": 0}

        def h(tl, p):
            if tl == "jawa/ordered_job":
                g["depth"] += 1
                g["cuts"] += 1
                if g["cuts"] == 2 or (g["cuts"] == 3 and finds):   # cut 1 is the digFindsEnabled OFF side
                    g["finds"] += 1
                if g["cuts"] == 3 and letter:                       # the C# grows the found-list with the letter
                    g["first"] += 1
                    g["letters"] += 1
                return {"success": True, "accepted": True}
            if tl == "jawa/flowworks_excavation_report":
                return {"success": True, "depth": g["depth"], "fill": 0}
            if tl == "jawa/static_call" and p.get("method") == "ProofReport":
                return {"result": "DIGFINDS finds %d | budget 5 | first-found %d | last Steel" % (g["finds"], g["first"])}
            if tl == "jawa/letter_list":
                return {"letters": [{"label": {"RawText": "Found while digging: Steel"}}] * g["letters"]}
            return base(tl, p)
        return _ext_run(EXT, "dig_finds", h).get("first_find_sends_letter")
    for first0, letter, finds, want in ((0, True, True, "PASS"), (3, True, True, "PASS"), (0, False, True, "FAIL"),
                                        (3, False, True, "UNMEASURED"), (0, True, False, "UNMEASURED")):   # no find: rolledDepth, see _expect_cut_found
        got = digs(first0, letter, finds)
        if got != want:
            out.append("first_find_sends_letter first-found=%d letter=%s find=%s: %s, want %s" % (first0, letter, finds, got, want))
    # a sticky pond (classified by an earlier chain on this map) is UNMEASURED, never a draw/recession reading
    sticky = lambda tl, p: ({"success": True, "formedByThisCall": False, "body": {"id": 1, "stock": 0.0, "limitless": False}}  # noqa: E731
                            if tl == "jawa/flowworks_body_report" else base(tl, p))
    if _ext_run(EXT, "plot_D_limited_pond", sticky).get("pond_before_draw") != "UNMEASURED":
        out.append("pond_before_draw on an inherited body must be UNMEASURED")
    got = _ext_run(EXT, "toggle_recession", sticky)
    if got != {"recession_on": "UNMEASURED", "recession_off": "UNMEASURED"}:
        out.append("toggle_recession on inherited bodies must be UNMEASURED: %s" % got)

    # two sites: --merge joins a dry and a river half only when they are the same build and together run everything
    import extension_proof as EP
    dry_n = [n for n, _ in EP.site_chains("dry")]
    riv_n = [n for n, _ in EP.site_chains("river")]

    def half(site, names, **kw):
        h = dict(script="extension_proof", mode="live", mod="FlowWorks", site=site, mod_hash="H",
                 env={"running_sha256": "R", "assembly_sha256": "A"}, chains_run=list(names), all_green=True,
                 chains=[{"name": n, "components": []} for n in names])
        h.update(kw)
        return h
    m, ref = EP.merge(half("dry", dry_n), half("river", riv_n))
    if ref or set(m["chains_run"]) != set(dry_n + riv_n) or not m["all_green"]:
        out.append("merge of two clean halves refused or lost chains: %s" % ref)
    for why, d, r in (("different mod_hash", half("dry", dry_n), half("river", riv_n, mod_hash="H2")),
                      ("different assembly", half("dry", dry_n), half("river", riv_n, env={"running_sha256": "R", "assembly_sha256": "B"})),
                      ("dry half ran a river chain", half("dry", dry_n + riv_n[:1]), half("river", riv_n)),
                      ("a chain unrun", half("dry", dry_n[1:]), half("river", riv_n)),
                      ("halves swapped", half("river", riv_n), half("dry", dry_n))):
        if not EP.merge(d, r)[1]:
            out.append("merge accepted %s" % why)
    m, _ = EP.merge(half("dry", dry_n), half("river", riv_n, all_green=False))
    if m["all_green"]:
        out.append("merge: a red river half came out all_green")
    return out


def _new_probes(EXT, RIV, base):
    """Re-review 2026-10-11: one case per fixed check, each red on the old code."""
    out = []

    def run(M, chain, h):
        return _ext_run(M, chain, h)

    # owed rows declare NO toggle (a declared toggle on an UNMEASURED-by-construction row counted as floor coverage)
    dec = _declared_toggles(EXT, "machinery_found_works")
    if any(dec.get(n) for n in ("ruins_mapgen", "ruin_stock_mapgen", "pipe_adapters")):
        out.append("machinery owed rows still declare a toggle: %s" % dec)
    if _declared_toggles(EXT, "toggle_river_steam").get("river_steam"):
        out.append("river_steam still declares riverSteamEnabled")
    got = run(EXT, "toggle_river_steam", lambda tl, p: {"success": True, "value": "False"} if tl == "jawa/mod_settings_field" else base(tl, p))
    if got != {"river_steam": "UNMEASURED"}:
        out.append("river_steam (setting read-back only) must be owed: %s" % got)
    if _declared_toggles(RIV, "taken_by_land").get("service_has_river_policy_and_trace_setting"):
        out.append("taken_by_land still claims takenByLandTraceEnabled")
    if _declared_toggles(RIV, "placer").get("flood_refill"):
        out.append("flood_refill still claims placerFloodRefill")

    # fill-in displacement: no fill-in happened (D stays 1) used to PASS at after == before
    def disp(depth_after, fill=1, ov=0.0):
        st = {"designated": False}

        def h(tl, p):
            if tl == "jawa/designate_batch":
                st["designated"] = True
            if tl in ("jawa/flowworks_job_probe", "jawa/ordered_job"):
                return FILLIN_OK[tl]
            if tl == "jawa/flowworks_excavation_report":
                r = {"success": True, "depth": depth_after if st["designated"] else 1, "isSourceCell": False,
                     "overflowDestroyedTotal": ov if st["designated"] else 0.0}
                if not st["designated"]:
                    r["fill"] = 1               # the D=1 run brims before the fill-in
                elif fill is not None:
                    r["fill"] = fill
                return r
            return base(tl, p)
        return run(EXT, "toggle_fill_in_displacement", h).get("fill_in_displacement_on")
    for args, want in (((1,), "UNMEASURED"), ((0, None), "UNMEASURED"), ((0,), "PASS"), ((0, 0, 3.0), "PASS"),
                       ((0, 0, 0.0), "FAIL")):
        if disp(*args) != want:
            out.append("fill_in_displacement_on %s: %s, want %s" % (args, disp(*args), want))

    # refill reads the pond STOCK: ON must rise, OFF must not; a pond the channel never drew is UNMEASURED and a
    # static pond can no longer PASS ON (source-cell counts passed both sides on a pond that never changed)
    def refill(stocks, formed=True, cap=125.0):
        seq = list(stocks)

        def h(tl, p):
            if tl == "jawa/flowworks_body_report":
                if p.get("classify") is not False:
                    return {"success": True, "formedByThisCall": formed, "body": {"id": 1, "capacity": cap, "stock": cap}}
                return {"success": True, "body": {"id": 1, "stock": seq.pop(0) if len(seq) > 1 else seq[0]}}
            return base(tl, p)
        return run(EXT, "toggle_refill", h)
    for stocks, formed, want in (((119.0, 120.0, 120.0, 120.0), True, ("PASS", "PASS")),
                                 ((119.0, 119.0, 119.0, 119.0), True, ("FAIL", "UNMEASURED")),
                                 ((125.0, 125.0), True, ("UNMEASURED", "UNMEASURED")),
                                 ((119.0, 120.0, 120.0, 121.0), True, ("PASS", "FAIL")),
                                 ((119.0, 120.0), False, ("UNMEASURED", "UNMEASURED"))):
        got = refill(stocks, formed)
        if (got.get("refill_on"), got.get("refill_off")) != want:
            out.append("toggle_refill stocks=%s formed=%s: %s, want %s" % (stocks, formed, got, want))

    # recession: a fresh pond the channel drew down is measured; an undrawn one is UNMEASURED on the OFF side
    def recession(stock_after, far_source):
        def h(tl, p):
            if tl == "jawa/flowworks_body_report":
                if p.get("classify") is not False:
                    return {"success": True, "formedByThisCall": True, "body": {"id": 1, "capacity": 45.0, "stock": 45.0}}
                return {"success": True, "body": {"id": 1, "stock": stock_after}}
            if tl == "jawa/flowworks_excavation_report":
                return {"success": True, "depth": 0, "fill": 0, "isSourceCell": far_source}
            return base(tl, p)
        return run(EXT, "toggle_recession", h)
    got = recession(9.0, False)
    if got.get("recession_on") != "PASS":
        out.append("recession_on with the far cell dried: %s" % got)
    for st, far, want in ((9.0, True, "PASS"), (9.0, False, "FAIL"), (45.0, True, "UNMEASURED")):
        def h_on(tl, p, st=st, far=far):
            if tl == "jawa/flowworks_body_report":
                if p.get("classify") is not False:
                    return {"success": True, "formedByThisCall": True, "body": {"id": 1, "capacity": 45.0, "stock": 45.0}}
                return {"success": True, "body": {"id": 1, "stock": st}}
            if tl == "jawa/flowworks_excavation_report":
                # recession_on (first far read) sees a dried cell; recession_off's far cell answers `far`
                h_on.n = getattr(h_on, "n", 0) + 1
                return {"success": True, "depth": 0, "fill": 0, "isSourceCell": far if h_on.n > 1 else False}
            return base(tl, p)
        got = run(EXT, "toggle_recession", h_on).get("recession_off")
        if got != want:
            out.append("recession_off stock=%s far source=%s: %s, want %s" % (st, far, got, want))

    # list_things with no `success` used to read as "no flame" (canal_fire OFF, explosion OFF PASSed blind)
    def fire(chain, lit_cells, shape=True):
        def h(tl, p):
            if tl == "jawa/list_things":
                if not shape:
                    return {"things": []}
                return _things([{"x": _rect_xz(p)[0], "z": _rect_xz(p)[1]}] if _rect_xz(p) in lit_cells(p) else [])
            if tl == "jawa/static_call" and p.get("method") == "ProofIgnite":
                return {"success": True, "result": "LIT"}
            return base(tl, p)
        return run(EXT, chain, h)
    got = fire("toggle_canal_fire", lambda p: set(), shape=False)
    if got.get("canal_fire_off_is_inert") != "UNMEASURED":
        out.append("canal_fire_off on a reply with no success: %s" % got)
    got = fire("toggle_canal_fire", lambda p: set())
    if got.get("canal_fire_off_is_inert") != "PASS" or got.get("canal_fire_on_lights") != "FAIL":
        out.append("canal fire: an instrument that sees no flame when ON must FAIL the ON side: %s" % got)
    got = fire("fire_explosion", lambda p: set(), shape=False)
    if got.get("explosion_off_does_not_light") != "UNMEASURED":
        out.append("explosion_off on a reply with no success: %s" % got)
    # rain: the open row never lit, the roofed row did -> "fewer than 6 open lit" used to PASS without a douse
    roofed = set()

    def h_rain(tl, p):
        if tl == "jawa/set_roof_batch":
            for op in p["ops"].split(";"):
                x, z = op.split(":")[1].split(",")[:2]
                roofed.add((int(x), int(z)))
        if tl == "jawa/list_things":
            c = _rect_xz(p)
            return _things([{"x": c[0], "z": c[1]}] if c in roofed else [])
        if tl == "jawa/static_call" and p.get("method") == "ProofIgnite":
            return {"success": True, "result": "LIT"}
        return base(tl, p)
    got = run(EXT, "fire_rain", h_rain)
    if got.get("rain_douses_open_fire") != "FAIL":
        out.append("rain_douses_open_fire with the open row never lit: %s" % got)

    # tar front: a channel that took no liquid at all (wet 0) used to PASS as "viscosity lag" (the check alone: the
    # chain around it needs real screenshots for its diptych)
    class _TT(object):
        def __init__(self, fills):
            self.fills = list(fills)

        def _guard(self):
            return True

        def bridge_call(self, tool, **p):
            return {"success": True, "depth": 1, "fill": self.fills.pop(0)}
    cells = [(i, 0) for i in range(4)]
    for fills, want in (([0, 0, 0, 0], True), ([1, 1, 1, 1], True), ([1, 1, 0, 0], False)):
        try:
            EXT._expect_tar_lag(_TT(fills), cells)
            raised = False
        except EXT.ExpectationFailed:
            raised = True
        if raised != want:
            out.append("tar lag check on fills %s: raised=%s, want %s" % (fills, raised, want))

    # rivers: an empty swept book ("SWEPT pending=0", nobody washed away) used to PASS returns_home
    def swept(before):
        def h(tl, p):
            if p.get("method") == "ProofSwept":
                return {"success": True, "result": "SWEPT pending=0" if p.get("args") == "return" else "SWEPT pending=%d" % before}
            return {"success": True}
        return run(RIV, "swept", h).get("returns_home")
    if swept(0) != "UNMEASURED" or swept(2) != "PASS":
        out.append("returns_home: empty book %s (want UNMEASURED), two pending %s (want PASS)" % (swept(0), swept(2)))
    # placer: pan=nothing / stockspent / noroom used to PASS "panning draws stock"; flood_refill is owed
    def placer(pan):
        res = ("site=1,1 rot=0 poolCount=3 lane=1 before=10.0 after=7.0 got=3 drawMatches=True inPool=True "
               "off=sluice=off pan=%s washes=" % pan)
        return run(RIV, "placer", lambda tl, p: {"success": True, "result": res if p.get("args") == "selfcheck"
                                                 else "PLACER stock=5.0 cap=5.0"})
    for pan, want in (("pan=nothing", "UNMEASURED"), ("pan=stockspent", "UNMEASURED"), ("pan=noroom", "UNMEASURED"),
                      ("pan=off", "FAIL"), ("pan=RM_Goldx0", "FAIL"), ("pan=RM_Goldx3", "PASS")):
        got = placer(pan)
        if got.get("panning_draws_stock") != want:
            out.append("panning_draws_stock on %s: %s, want %s" % (pan, got.get("panning_draws_stock"), want))
    if placer("pan=RM_Goldx3").get("flood_refill") != "UNMEASURED":
        out.append("flood_refill (forced refill ignores the setting) must be owed: %s" % placer("pan=RM_Goldx3"))
    return out


if __name__ == "__main__":
    sys.exit(main())
