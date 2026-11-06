#!/usr/bin/env python3
"""Selftest for targeted runs (owner 2026-10-25, "Live runs are TARGETED") and the seat-less run record
(MODCHECK_VERIFY_FIX_SEAT_LOST_ON_WINDOWS, MODCHECK_SEAT_FIX_DETACHED_RUN_NO_RECORD) and the --policy guard
(MODCHECK_POLICY_FIX_RECORD_NEEDS_SITUATIONAL). Offline: no game, no bridge, no ledger write, no status write."""
import contextlib
import io
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import cli  # noqa: E402
import runner  # noqa: E402
import status  # noqa: E402
import targeting  # noqa: E402
from suite import Suite  # noqa: E402

FAILS = []


def ok(cond, what, got=None):
    print(("PASS  " if cond else "FAIL  ") + what + ("" if cond or got is None else "   got: %r" % (got,)))
    if not cond:
        FAILS.append(what)


CALLS = []
UNSTUB = set()          # --unstub NAME: leave runner.NAME real in stubbed_run (replays a missed-stub instance)
BRIDGE_REACHES = []     # every rimbridge_client reach any stubbed run made, by runner caller


def make_suite():
    s = Suite("ToyMod")
    s.toggles = ["T1"]

    @s.chain("lines")
    def lines(t):
        CALLS.append("lines")
        with t.component("lines_drawn_ok"):
            pass

    @s.chain("pump_ports", tick_cap=9000)
    def pump_ports(t):
        """PUMP_PORTS_FIX_WEST_SIDE_1 wrote this row."""
        CALLS.append("pump_ports")
        with t.component("pump_west_port"):
            pass
        with t.component("pump_east_port"):
            pass

    @s.chain("thirst")
    def thirst(t):
        CALLS.append("thirst")
        with t.component("thirst_drinks"):
            pass
    return s


def t_resolve():
    s = make_suite()
    sel = targeting.resolve(s, chains=["thirst", "lines"])
    ok(sel["chains"] == ["lines", "thirst"], "chains: --chains selects exactly those, in suite order", sel["chains"])
    sel = targeting.resolve(s, rows=["pump_east_port"])
    ok(sel["chains"] == ["pump_ports"] and sel["rows"] == ["pump_east_port"]
       and sel["rows_run"] == ["pump_west_port", "pump_east_port"],
       "rows: a row selects its whole chain; requested rows and rows run are recorded apart", sel)
    sel = targeting.resolve(s, item="PUMP_PORTS_FIX_WEST_SIDE_1", text="title only")
    ok(sel["chains"] == ["pump_ports"], "item: a chain whose source names the item is selected", sel["chains"])
    try:
        targeting.resolve(s, item="PUMP_PORTS_FIX_WEST", text="")
        ok(False, "item: a prefix of a cited id (PUMP_PORTS_FIX_WEST in ..._WEST_SIDE_1) must not map")
    except targeting.TargetError:
        ok(True, "item: a prefix of a cited id does not map")
    sel = targeting.resolve(s, item="SOME_ITEM", text="ToyMod: the `thirst` chain and row lines_drawn_ok; lines and thirst")
    ok(sel["chains"] == ["lines", "thirst"], "item: ledger text naming a backticked chain / an underscored row id",
       sel["chains"])
    # TESTQ_ITEMOWED_FIX_DEFS_CHAIN_ADOPTS_ALL: a text link needs the item to name the mod; a stranger's item naming a
    # generic chain/row is refused (GREENTIDE_ANTS_MIGRATE_NO_ANT_LEFT_BEHIND was adopted by every biome's `defs`)
    for t in ("a Stillsand item: the `thirst` chain", "Stillsand: row lines_drawn_ok fails"):
        try:
            sel = targeting.resolve(s, item="STILLSAND_DEFS_FIX", text=t)
            ok(False, "item: text naming a chain/row but not the mod does not link", sel["chains"])
        except targeting.TargetError as ex:
            ok("of a mod it names" in str(ex), "item: text naming a chain/row but not the mod does not link: %r" % t,
               str(ex))
    sel = targeting.resolve(s, item="TOY_MOD_THIRST_FIX", text="the `thirst` chain")
    ok(sel["chains"] == ["thirst"], "item: an id naming the mod (underscores ignored) keeps the text link", sel["chains"])
    sel = targeting.resolve(s, item="PUMP_PORTS_FIX_WEST_SIDE_1", text="a Stillsand note naming `thirst`")
    ok(sel["chains"] == ["pump_ports"], "item: a source link stands without the mod named; the stranger text adds none",
       sel["chains"])
    ok(targeting.names_mod("FlowWorks", "FLOW_WORKS_X", "") and targeting.names_mod("FlowWorks", "Y", "see flowworks")
       and not targeting.names_mod("FlowWorks", "GREENTIDE_ANTS_X", "the `defs` chain") and not targeting.names_mod("", "A", "a"),
       "names_mod: folder name in text (case-blind) or in the id, underscores ignored; nothing else")
    for kw, what in ((dict(item="SOME_ITEM", text="thirst lines everywhere, no ids"),
                      "item with no link (bare common words do not count) is refused"),
                     (dict(chains=["nope"]), "unknown chain is refused"),
                     (dict(rows=["nope_row"]), "unknown row is refused")):
        try:
            targeting.resolve(s, **kw)
            ok(False, what)
        except targeting.TargetError as ex:
            ok(True, what)
            if "item" in kw:
                ok("--chains" in str(ex) and "--rows" in str(ex) and "full suite" in str(ex),
                   "the item refusal names --chains/--rows and refuses the full suite", str(ex))
    f = targeting.filtered(s, ["thirst", "pump_ports"])
    ok([n for n, _ in f.chains] == ["pump_ports", "thirst"] and f.toggles == ["T1"] and f.chain_caps == {"pump_ports": 9000}
       and len(s.chains) == 3, "filtered: suite order, attributes kept, original untouched")
    ok(targeting.config_tag(None) == "full" and targeting.config_tag(
        {"chains": ["a", "b"], "rows": ["r"]}) == "TARGETED chains=a,b rows=r", "config tag names scope")


def t_targeted_suite_keeps_site_hold():
    """A targeted run goes through the same run_suite: the bland-map hold before EVERY selected chain, none run for
    the rest."""
    import helpers as H
    seen = []

    class Rep(object):
        problems = []

        def as_dict(self):
            return {"bland": True, "problems": [], "notes": [], "steps": []}

    class Tx(object):
        def __init__(self, session):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            pass

    class Res(object):
        def as_dict(self):
            return {}

    real = (H.prepare_bland_map, H.SettingsTransaction, H.kill_hostiles, runner.load_fixtures, runner.save_fixtures)
    H.prepare_bland_map = lambda *a, **k: seen.append("hold") or Rep()
    H.SettingsTransaction, H.kill_hostiles = Tx, (lambda *a, **k: Res())
    runner.load_fixtures = lambda *a, **k: set()
    runner.save_fixtures = lambda *a, **k: None
    from selftest import _fake_session
    del CALLS[:]
    try:
        s = make_suite()
        runner.run_suite(targeting.filtered(s, ["thirst"]), _fake_session(), hold_site=True, floor_suite=s)
    finally:
        (H.prepare_bland_map, H.SettingsTransaction, H.kill_hostiles, runner.load_fixtures,
         runner.save_fixtures) = real
    ok(CALLS == ["thirst"] and seen == ["hold"], "targeted: only the selected chain runs, after its site hold",
       (CALLS, seen))


def t_emit_verify_seat():
    real_run, ran = subprocess.run, []
    subprocess.run = lambda *a, **k: ran.append(a) or real_run(["true"])
    env = {k: os.environ.pop(k) for k in ("RIMFLOW_SEAT", "AGENT_SEAT") if k in os.environ}
    summ = {"chains": [], "all_green": False}
    try:
        v = runner.emit_verify("X_ITEM", "ToyMod", "min+ToyMod full", summ, "/tmp/s.html")
        ok(v.get("seat") == "UNKNOWN" and not ran and "--seat <SEAT>" in v.get("skipped", "")
           and "'min+ToyMod full'" in v["skipped"],
           "verify: no seat -> UNKNOWN, rimflow not called, the hand command is returned", v)
        ok(runner.file_findings("X_ITEM", "ToyMod", [object()]) == [] and not ran,
           "findings: no seat -> not attempted, no crash")
        v = runner.emit_verify("X_ITEM", "ToyMod", "c", summ, "/tmp/s.html", dry_run=True, seat="BENCH")
        ok(v["cmd"][-2:] == ["--seat", "BENCH"], "verify: an explicit seat is spelled out on the command", v)
    finally:
        subprocess.run = real_run
        os.environ.update(env)


@contextlib.contextmanager
def stubbed_run():
    """runner.run() with every side effect stubbed: returns the record_run/emit_verify calls it made."""
    seen = {"record": [], "verify": [], "suite": []}
    names = ("swap_to_test_list", "restore_full", "compose_test_list", "find_mod_dir", "load_validation",
             "northstar_for", "visual_floor", "ensure_playing_map", "ensure_test_profile", "run_suite",
             "write_sheet", "mod_dependency_ids", "composed_into", "mod_package_id", "verify_loaded_list")
    real = {n: getattr(runner, n) for n in names}
    real_rec, real_sub, real_env = status.record_run, subprocess.run, os.environ.get("MODCHECK_SKIP_DEPLOY")
    env = {k: os.environ.pop(k) for k in ("RIMFLOW_SEAT", "AGENT_SEAT") if k in os.environ}
    fake_rimdrive = type(sys)("rimdrive")

    class Session(object):
        def __init__(self, **k):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            pass
    fake_rimdrive.Session = Session
    real_rd = sys.modules.get("rimdrive")
    sys.modules["rimdrive"] = fake_rimdrive
    # NIGHTLY_COP_FIX_RED_OIMKSA_WDRT: fence the bridge. runner imports rimbridge_client lazily, so a new bridge read
    # (the 11-04 instance: verify_loaded_list -> jawa/running_mods) left unstubbed reached the REAL bridge: it failed
    # from WSL and would drive the live game from Windows Python. Every reach is recorded with its caller and refused.
    seen["bridge"] = []
    fake_rb = type(sys)("rimbridge_client")

    def _reach(*a, **k):
        import traceback
        callers = [f.name for f in traceback.extract_stack()[:-1] if f.filename.endswith("runner.py")]
        seen["bridge"].append(callers[-1] if callers else "?")
        raise ConnectionError("HERMETIC: the stubbed run reached rimbridge_client")

    class _FencedBridge(object):
        def __init__(self, *a, **k):
            _reach()
    fake_rb.resolve_endpoint, fake_rb.RimBridge = _reach, _FencedBridge
    real_rbm = sys.modules.get("rimbridge_client")
    sys.modules["rimbridge_client"] = fake_rb

    def fake_suite(s, sess, **k):
        seen["suite"].append(([n for n, _ in s.chains], k.get("hold_site"), k.get("floor_suite")))
        return {"chains": [], "all_green": True, "findings": [], "refused": ""}
    runner.swap_to_test_list = runner.restore_full = runner.compose_test_list = lambda *a, **k: None
    runner.find_mod_dir = lambda m: "/nonexistent/" + m
    runner.load_validation = lambda d: make_suite()
    runner.northstar_for = lambda m: (None, None)
    runner.visual_floor = lambda s, ns: {"bar": [], "uncovered": [], "orphans": []}
    runner.ensure_playing_map = runner.ensure_test_profile = lambda *a, **k: None
    runner.verify_loaded_list = lambda *a, **k: []      # the running load is the composed list: no bridge read
    runner.run_suite = fake_suite
    runner.write_sheet = lambda m, s: "/tmp/ToyMod_sheet.html"
    runner.mod_dependency_ids, runner.composed_into, runner.mod_package_id = (lambda d: []), (lambda m: None), (lambda d: "x.y")
    if UNSTUB - set(names):     # an unknown name would replay nothing and pass vacuously
        raise SystemExit("--unstub: %s is not a stubbed runner name (%s)" % (sorted(UNSTUB - set(names)), names))
    for n in UNSTUB:
        setattr(runner, n, real[n])
    status.record_run = lambda *a, **k: seen["record"].append(a[0])
    def fake_sub(cmd, **k):     # rimflow's real behaviour with no seat in reach: refuse
        seen["verify"].append(cmd)
        if "--seat" not in cmd:
            return subprocess.CompletedProcess(cmd, 1, "", "REFUSED: I cannot tell which seat I am")
        return subprocess.CompletedProcess(cmd, 0, "", "")
    subprocess.run = fake_sub
    os.environ["MODCHECK_SKIP_DEPLOY"] = "1"
    try:
        yield seen
    finally:
        for n, f in real.items():
            setattr(runner, n, f)
        status.record_run, subprocess.run = real_rec, real_sub
        if real_env is None:
            os.environ.pop("MODCHECK_SKIP_DEPLOY", None)
        else:
            os.environ["MODCHECK_SKIP_DEPLOY"] = real_env
        os.environ.update(env)
        if real_rd is None:
            sys.modules.pop("rimdrive", None)
        else:
            sys.modules["rimdrive"] = real_rd
        if real_rbm is None:
            sys.modules.pop("rimbridge_client", None)
        else:
            sys.modules["rimbridge_client"] = real_rbm
        BRIDGE_REACHES.extend(seen["bridge"])


def t_run_records_without_seat():
    with stubbed_run() as seen:
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            try:
                runner.run([("ToyMod", "X_ITEM")])
            except RuntimeError as ex:
                ok(False, "run: no seat must not raise", str(ex)[:120])
    ok(seen["record"] == ["ToyMod"], "run: the status record is written with no seat (no crash)", seen)
    ok(not seen["verify"] and "seat UNKNOWN" in err.getvalue(), "run: seat UNKNOWN is said, rimflow never called",
       err.getvalue()[-300:])


def t_run_targeted():
    s = make_suite()
    sel = targeting.resolve(s, chains=["thirst"])
    with stubbed_run() as seen:
        with contextlib.redirect_stderr(io.StringIO()):
            res = runner.run([("ToyMod", "X_ITEM")], targets={"ToyMod": sel}, seat="BENCH")
    ok([c[0] for c in seen["suite"]] == [["thirst"]] and seen["suite"][0][1] is True
       and len(seen["suite"][0][2].chains) == 3,
       "run: targeted runs only its chains, site hold on, floor from the full suite", seen["suite"])
    ok(res["ToyMod"].get("targeted", {}).get("chains") == ["thirst"] and res["ToyMod"]["targeted"]["of_chains"] == 3,
       "run: the summary (sheet JSON) records the chains covered", res["ToyMod"].get("targeted"))
    ok(not seen["record"], "run: a targeted run never overwrites the full-suite status entry", seen["record"])
    with stubbed_run() as seen2:
        runner.visual_floor = lambda s, ns: {"bar": ["x"], "uncovered": ["x"], "orphans": []}
        with contextlib.redirect_stderr(io.StringIO()):
            res2 = runner.run([("ToyMod", "X_ITEM")], targets={"ToyMod": sel}, seat="BENCH")
    ok(res2["ToyMod"].get("refused") and not seen2["record"],
       "run: a REFUSED targeted run does not write the full-suite status entry either", seen2["record"])
    cfg = [c[c.index("--config") + 1] for c in seen["verify"] if "verify" in c]
    ok(cfg == ["min+ToyMod TARGETED chains=thirst"], "run: the ledger verify config names the scope", cfg)
    ok(cli._verdict_line(res["ToyMod"]).startswith("TARGETED 1/3 chains (thirst) GREEN"),
       "cli: the verdict line never reads as a bare full-suite GREEN", cli._verdict_line(res["ToyMod"]))


def t_cli_refusals():
    real_run, got = runner.run, []
    runner.run = lambda *a, **k: got.append(k) or {}
    try:
        for argv, what in ((["run", "FlowWorks"], "cli: an untargeted run without --full is refused"),
                           (["run", "FlowWorks", "--full", "--chains", "lines"], "cli: --full plus a target is refused"),
                           (["run", "FlowWorks", "--full", "--policy", "record"],
                            "cli: --policy record without --situational is refused"),
                           (["run", "FlowWorks", "--chains", "no_such_chain_xyz"], "cli: an unknown chain is refused"),
                           (["run", "FlowWorks", "Pits", "--chains", "lines"], "cli: a target names one mod")):
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = cli.main(argv)
            ok(code == 2 and "REFUSED" in out.getvalue() and not got, what, (code, out.getvalue()[-200:]))
        with contextlib.redirect_stdout(io.StringIO()):
            cli.main(["run", "FlowWorks", "--chains", "lines", "--dry-run", "--seat", "BENCH"])
        ok(got and got[0]["targets"]["FlowWorks"]["chains"] == ["lines"] and got[0]["seat"] == "BENCH",
           "cli: --chains on the real FlowWorks suite resolves offline and reaches run()", got)
        del got[:]
        with contextlib.redirect_stdout(io.StringIO()):
            cli.main(["run", "FlowWorks", "--full", "--dry-run"])
        ok(got and got[0]["targets"] == {}, "cli: --full runs the whole suite", got)
    finally:
        runner.run = real_run


TRACE = []


def make_option_a_suite(incomplete=False):
    """Option A fixtures: a four-row chain with raw calls / a teardown between rows, an offline one; incomplete=True
    adds two chains the declaration probe cannot list fully (a raise outside / inside a component)."""
    s = Suite("ToyA")

    @s.chain("big")
    def big(t):
        try:
            with t.component("big_a"):
                if getattr(t, "fail_a", False):
                    raise AssertionError("a is red")
            try:
                with t.component("big_b"):          # the stop is raised as this row records ...
                    pass
            except Exception:                       # noqa: BLE001 - ... so this handler must NOT eat it
                TRACE.append("swallowed")
            if t.session is not None:               # (the declaration probe has no session)
                t.session.call("raw_after_b")       # a raw session.call between rows: must NOT run after a stop
                TRACE.append("subprocess_after_b")  # stands for a subprocess launch outside any component
            with t.component("big_c"):
                pass
            with t.component("big_d"):
                pass
        finally:
            TRACE.append("teardown")

    if incomplete:
        @s.chain("partial")
        def partial(t):
            with t.component("partial_first"):
                pass
            if t.session is None:                   # the probe walks with no session: this chain cannot be fully listed
                raise RuntimeError("needs a session to declare the rest")
            with t.component("partial_hidden"):
                pass

        @s.chain("swallowed")
        def swallowed(t):
            with t.component("swallowed_outer"):    # a raw session call INSIDE a row: the row swallows the raise ...
                t.session.call("raw")
                with t.component("swallowed_nested"):   # ... and this nested row is never declared
                    pass
            with t.component("swallowed_tail"):
                pass

    @s.chain("nest")
    def nest(t):
        with t.component("nest_outer"):
            with t.component("nest_inner"):
                pass
        with t.component("nest_tail"):
            pass

    @s.chain("offline_tier", offline=True)
    def offline_tier(t):
        with t.component("offline_row"):
            pass
    return s


def t_scope_and_preview():
    s = make_option_a_suite()
    sel = targeting.resolve(s, rows=["big_b"])
    sc = sel["scope"]["big"]
    ok(sc["mode"] == "prefix" and sc["requested_rows"] == ["big_b"] and sc["executed"] == ["big_a", "big_b"]
       and sc["skipped"] == ["big_c", "big_d"], "scope: --rows makes a PREFIX scope; executed up to the row, tail skipped",
       sc)
    ok(sel["rows_run"] == ["big_a", "big_b"], "scope: rows_run is what executes, not the whole chain", sel["rows_run"])
    text = "\n".join(targeting.preview(sel))
    ok("big" in text and "prefix" in text and "requested big_b" in text and "prerequisites big_a" in text
       and "NOT_RUN big_c, big_d" in text, "preview: requested -> prerequisites -> executed -> skipped, per chain", text)
    sel = targeting.resolve(s, chains=["big"], rows=["big_b"])
    ok(sel["scope"]["big"]["mode"] == "full" and sel["scope"]["big"]["skipped"] == [],
       "scope: a chain named whole by --chains overrides a row cutoff", sel["scope"]["big"])


def t_incomplete_catalogue_refused():
    s = make_option_a_suite(incomplete=True)
    rows, incomplete = targeting.catalogue(s)
    ok(rows["partial"] == ["partial_first"] and "partial" in incomplete and "big" not in incomplete,
       "catalogue: a chain the probe cannot walk is flagged incomplete, its partial list kept apart", (rows, incomplete))
    ok("swallowed" in incomplete and "swallowed_nested" not in rows["swallowed"],
       "catalogue: a raise swallowed INSIDE a probe row still flags the chain incomplete (codex r3)", (rows, incomplete))
    for kw, what in ((dict(rows=["partial_first"]), "a row in an incomplete chain is refused (stop point unknowable)"),
                     (dict(rows=["partial_hidden"]), "an unknown row while a chain is incomplete is refused, naming it"),
                     (dict(rows=["big_b"]), "a known row is refused while another chain's list is incomplete (codex r3)")):
        try:
            targeting.resolve(s, **kw)
            ok(False, "incomplete: " + what)
        except targeting.TargetError as ex:
            ok("incomplete" in str(ex) and "partial" in str(ex) and "--chains" in str(ex), "incomplete: " + what, str(ex))
    sel = targeting.resolve(s, chains=["partial"])
    ok(sel["scope"]["partial"]["mode"] == "full", "incomplete: the whole chain by --chains still runs", sel["scope"])
    sel = targeting.resolve(s, chains=["partial", "swallowed"], rows=["partial_first"])
    ok(sel["scope"]["partial"]["mode"] == "full" and sel["scope"]["partial"]["requested_rows"] == ["partial_first"],
       "incomplete: a row in a chain ALSO named whole is not refused (the whole chain runs)", sel["scope"])
    sel = targeting.resolve(s, item="X_ITEM", text="ToyA: the `partial` and `swallowed` chains, row partial_first")
    ok(sel["scope"]["partial"]["mode"] == "full", "incomplete: item text naming the chain AND its row runs it whole",
       sel["scope"])
    try:
        targeting.resolve(s, item="X_ITEM", text="ToyA: see row big_b")
        ok(False, "incomplete: a row found in ITEM TEXT gets the same hidden-owner refusal as --rows (codex r4)")
    except targeting.TargetError as ex:
        ok("incomplete" in str(ex) and "swallowed" in str(ex),
           "incomplete: a row found in ITEM TEXT gets the same hidden-owner refusal as --rows (codex r4)", str(ex))
    sel = targeting.resolve(s, rows=["big_b"], item="X_ITEM", text="ToyA: the `partial` and `swallowed` chains")
    ok(sel["scope"]["big"]["mode"] == "prefix" and sel["scope"]["partial"]["mode"] == "full",
       "incomplete: --rows is judged AFTER --item names the incomplete chains whole (codex r4)", sel["scope"])


def t_offline_chains_out_of_live():
    s = make_option_a_suite()
    ok(s.offline_chains == {"offline_tier"}, "suite: chain(offline=True) is recorded", s.offline_chains)
    s2 = make_option_a_suite()

    @s2.chain("offline_partial", offline=True)
    def offline_partial(t):
        if t.session is None:
            raise RuntimeError("cannot be listed without a session")
        with t.component("offline_partial_row"):
            pass
    try:
        sel = targeting.resolve(s2, rows=["big_b"])
        ok(sel["chains"] == ["big"], "offline: an INCOMPLETE offline chain does not block live row targeting (codex r5)",
           sel["chains"])
    except targeting.TargetError as ex:
        ok(False, "offline: an INCOMPLETE offline chain does not block live row targeting (codex r5)", str(ex))
    sel = targeting.resolve(s, chains=["big", "offline_tier"])
    ok(sel["chains"] == ["big"] and "offline_tier" in sel["offline_skipped"]
       and "offline_tier" not in sel["scope"], "offline: a targeted live run leaves an offline chain out", sel)
    ok("offline_tier" in "\n".join(targeting.preview(sel)), "offline: the preview names the skipped offline chain")
    try:
        targeting.resolve(s, rows=["offline_row"])
        ok(False, "offline: a selection of only offline chains is refused")
    except targeting.TargetError as ex:
        ok("offline" in str(ex) and "--full" in str(ex), "offline: a selection of only offline chains is refused", str(ex))


def _recording_session(calls):
    from selftest import _fake_session
    sess = _fake_session()
    sess.call = lambda tool, **p: calls.append((tool, p)) or {"success": True, "sizeX": 50, "sizeZ": 50}
    return sess


def t_stop_after_runtime():
    s = make_option_a_suite()
    for fail_a in (False, True):
        sel = targeting.resolve(s, rows=["big_b"])
        calls = []
        del TRACE[:]
        sess = _recording_session(calls)
        import suite as _S
        orig_init = _S.TestContext.__init__

        def init(self, *a, **k):
            orig_init(self, *a, **k)
            self.fail_a = fail_a
        _S.TestContext.__init__ = init
        try:
            with contextlib.redirect_stderr(io.StringIO()):
                res = runner.run_suite(targeting.filtered(s, sel["chains"]), sess, scope=sel["scope"])
        finally:
            _S.TestContext.__init__ = orig_init
        comps = res["chains"][0]["components"]
        got = [(c["name"], c["verdict"], c.get("execution")) for c in comps]
        want_b = "UNMEASURED" if fail_a else "PASS"
        ok(got[1:] == [("big_b", want_b, "ran"), ("big_c", "NOT_RUN", "not_run"), ("big_d", "NOT_RUN", "not_run")],
           "stop-after (a %s): the tail is NOT_RUN from the catalogue, never UNMEASURED" % ("red" if fail_a else "green"), got)
        ok(not any(c[0] == "raw_after_b" for c in calls) and "subprocess_after_b" not in TRACE
           and "swallowed" not in TRACE, "stop-after: no raw call or subprocess after the last requested row; "
           "`except Exception` cannot swallow the stop", (calls, TRACE))
        ok(TRACE == ["teardown"], "stop-after: the chain's own teardown (finally) still runs", TRACE)
        ok(res["all_green"] is (not fail_a), "stop-after: NOT_RUN rows neither redden nor green the run", res["all_green"])
    sel = targeting.resolve(s, rows=["nest_inner"])
    with contextlib.redirect_stderr(io.StringIO()):
        nres = runner.run_suite(targeting.filtered(s, sel["chains"]), _recording_session([]), scope=sel["scope"])
    got = [(c["name"], c["verdict"]) for c in nres["chains"][0]["components"]]
    ok(got == [("nest_inner", "PASS"), ("nest_outer", "NOT_RUN"), ("nest_tail", "NOT_RUN")] and not nres["findings"],
       "stop-after: an outer row interrupted by its nested requested row is NOT_RUN, never a FAIL", got)
    v = runner.emit_verify("X", "ToyA", "c", res, "/tmp/s", dry_run=True, seat="BENCH")
    ok(v["n_total"] == 2, "verify: NOT_RUN rows are not counted as measured", v)


def t_hold_contract_every_run():
    """MODCHECK_HOLD_FIX_SITUATIONAL_ONLY_ROOF: Log reset, weather lock, unroof and gas clear ran only under --situational."""
    import helpers as H

    class Rep(object):
        problems = []

        def as_dict(self):
            return {"bland": True, "problems": [], "notes": [], "steps": []}

    class Tx(object):
        def __init__(self, session):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            pass

    class Res(object):
        def as_dict(self):
            return {}
    real = (H.prepare_bland_map, H.SettingsTransaction, H.kill_hostiles, runner.load_fixtures, runner.save_fixtures)
    H.prepare_bland_map = lambda *a, **k: Rep()
    H.SettingsTransaction, H.kill_hostiles = Tx, (lambda *a, **k: Res())
    runner.load_fixtures = lambda *a, **k: set()
    runner.save_fixtures = lambda *a, **k: None
    calls = []
    try:
        s = make_suite()
        with contextlib.redirect_stderr(io.StringIO()):
            res = runner.run_suite(targeting.filtered(s, ["lines", "thirst"]), _recording_session(calls), hold_site=True)
    finally:
        (H.prepare_bland_map, H.SettingsTransaction, H.kill_hostiles, runner.load_fixtures,
         runner.save_fixtures) = real
    tools = [c[0] for c in calls]
    resets = [i for i, c in enumerate(calls) if c[1].get("method") == "ResetMessageCount"]
    marks = [i for i, t in enumerate(tools) if t == "jawa/drain_log"]
    ok(len(resets) == 2 and tools.count("jawa/weather_set") == 2 and tools.count("jawa/set_roof_batch") == 2
       and tools.count("jawa/set_gas") >= 2, "hold: Log reset, weather lock, unroof, gas clear before EVERY chain "
       "on the default (non-situational) path", tools)
    ok(len(marks) == 2 and all(r < m for r, m in zip(resets, marks)), "hold: the Log reset stays before mark_log",
       (resets, marks))
    env = res["chains"][0].get("env_reset") or {}
    ok(env.get("unroof") == "ok" and env.get("log_reset") == "ok", "hold: each step's outcome is recorded", env)
    ph = res["chains"][0].get("phase_s") or {}
    ok(set(ph) == {"hold", "body", "teardown"} and all(isinstance(v, float) and v >= 0 for v in ph.values()),
       "timing: hold / body / teardown seconds per chain (monotonic)", ph)
    doc = targeting.__doc__
    ok("on every live path" in doc and "only under --situational" not in doc,
       "docstring: states the hold the default path now really runs", doc[-400:])


def t_cli_preview():
    real = (runner.run, runner.find_mod_dir, runner.load_validation)
    got = []
    runner.run = lambda *a, **k: got.append(k) or {}
    runner.find_mod_dir = lambda m: "/nonexistent/" + m
    runner.load_validation = lambda d: make_option_a_suite()
    try:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = cli.main(["run", "ToyA", "--rows", "big_b", "--preview"])
        ok(code == 0 and not got and "PREVIEW" in out.getvalue() and "NOT_RUN big_c, big_d" in out.getvalue(),
           "cli: --preview prints the per-chain plan and never starts a run", (code, out.getvalue()[-300:]))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            cli.main(["run", "ToyA", "--rows", "big_b", "--dry-run", "--seat", "BENCH"])
        ok(got and "PREVIEW" in out.getvalue() and got[0]["targets"]["ToyA"]["scope"]["big"]["mode"] == "prefix",
           "cli: a launched targeted run prints the same preview first and hands run() the scope", out.getvalue()[-300:])
    finally:
        runner.run, runner.find_mod_dir, runner.load_validation = real


def t_nested_evidence_stays_on_outer():
    """Codex review r2: an inner component used to clear ctx._current, so evidence the OUTER row gathered after
    its inner row closed was dropped (and its UNVERIFIED receipts never counted)."""
    from suite import TestContext
    t = TestContext(None, anchor=(100, 100))
    with t.component("outer"):
        with t.component("inner"):
            t._record("in", {"ok": 1})
        t._record("after_inner", {"ok": 2})
    outer = [c for c in t.components if c.name == "outer"][0]
    ok([e["call"] for e in outer.evidence] == ["after_inner"] and t._current is None,
       "nested: evidence after an inner row lands on the outer row; _current restored to None at the end",
       [e["call"] for e in outer.evidence])


def t_item_text_utf8_under_cp1252():
    """MODCHECK_FIX_ITEMTEXT_CP1252_CRASH: under python.exe the locale codec is cp1252; rimflow's UTF-8 output holds
    byte 0x9d (the tail of a right double quote), undefined in cp1252. item_text must decode it as UTF-8."""
    class FakeRunner:
        ROOT = HERE
        RIMFLOW_CLI = "unused"

        @staticmethod
        def py_cmd(script, *args):
            return [sys.executable, "-c",
                    "import sys; sys.stdout.buffer.write('ITEM_X \u201dquoted\u201d \u2014 chain_a\\n'.encode('utf-8'))"]
    real_run = subprocess.run

    def windows_run(*a, **k):       # python.exe: text mode with no encoding given decodes with cp1252
        if (k.get("text") or k.get("universal_newlines")) and not k.get("encoding"):
            k["encoding"] = "cp1252"
        return real_run(*a, **k)
    ok(b"\x9d" in "\u201d".encode("utf-8"), "instance: the UTF-8 right double quote carries byte 0x9d")
    subprocess.run = windows_run
    try:
        text = targeting.item_text("ITEM_X", runner_mod=FakeRunner)
    except Exception as ex:          # noqa: BLE001 - the crash itself is the failure being tested
        text = "%s: %s" % (type(ex).__name__, ex)
    finally:
        subprocess.run = real_run
    ok(text == "ITEM_X \u201dquoted\u201d \u2014 chain_a\n",
       "item_text decodes rimflow output as UTF-8 under a cp1252 default (byte 0x9d does not crash it)", repr(text))


def t_item_text_retries_wsl_hiccup():
    """MODCHECK_ITEMTEXT_RETRY_WSL_HICCUP_FAILS_RUN: one wsl.exe callback failing with Wsl/Service/0x8007274c refused
    a whole live run. item_text retries a WSL hiccup, never an unknown item, and still refuses a hiccup that lasts."""
    import tempfile
    def fake(script_body):
        class FakeRunner:
            ROOT = HERE
            RIMFLOW_CLI = "unused"

            @staticmethod
            def py_cmd(script, *args):
                return [sys.executable, "-c", script_body]
        return FakeRunner
    counter = os.path.join(tempfile.mkdtemp(prefix="selftest_itemtext_"), "n")
    flaky = ("import os,sys; p=%r; n=int(open(p).read()) if os.path.exists(p) else 0; open(p,'w').write(str(n+1))\n"
             "if n < 2: sys.stderr.write('Error code: Wsl/Service/0x8007274c\\n'); sys.exit(1)\n"
             "print('ITEM_X chain_a')" % counter)
    waits = []
    text = targeting.item_text("ITEM_X", runner_mod=fake(flaky), _sleep=waits.append)
    ok(text.strip() == "ITEM_X chain_a" and waits == list(targeting.ITEM_TEXT_WAITS_S),
       "two Wsl/Service/0x8007274c hiccups then an answer: item_text returns the text after retrying", (text, waits))
    waits = []
    unknown = "import sys; print('ITEM_Y has never been filed.'); sys.exit(2)"
    try:
        targeting.item_text("ITEM_Y", runner_mod=fake(unknown), _sleep=waits.append)
        got = "no raise"
    except targeting.TargetError as ex:
        got = str(ex)
    ok("never been filed" in got and waits == [], "an unknown item is refused at once, never retried", (got, waits))
    waits = []
    dead = "import sys; sys.stderr.write('Error code: Wsl/Service/0x8007274c\\n'); sys.exit(1)"
    try:
        targeting.item_text("ITEM_Z", runner_mod=fake(dead), _sleep=waits.append)
        got = "no raise"
    except targeting.TargetError as ex:
        got = str(ex)
    ok("0x8007274c" in got and len(waits) == len(targeting.ITEM_TEXT_WAITS_S),
       "a hiccup that outlasts every retry still refuses, naming the WSL error", (got, waits))


def _git_repo():
    """A throwaway repo under the system temp dir with a mod folder; -> (root, mod_dir, git)."""
    import tempfile
    root = tempfile.mkdtemp(prefix="selftest_targeting_")
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
               GIT_COMMITTER_EMAIL="t@t", GIT_CONFIG_NOSYSTEM="1", HOME=root)

    def git(*a):
        subprocess.run(["git"] + list(a), cwd=root, check=True, capture_output=True, env=env)
    git("init", "-q", "-b", "main")
    git("config", "core.quotepath", "true")      # git's default: non-ASCII paths come back C-quoted without -z
    mod = os.path.join(root, "Mod")
    os.makedirs(os.path.join(mod, "Defs"))
    return root, mod, git


def _w(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def t_changed_files_every_spec():
    """MODCHECK_CHANGEDFILES_FIX_FIRST_DIFF_WINS: every diff spec counts, paths are read raw, renames and a staged
    change restored in the worktree are seen."""
    import shutil
    root, mod, git = _git_repo()
    try:
        a = os.path.join(mod, "Defs", "a.xml")
        _w(a, "<defName>RM_Base</defName>\n")
        _w(os.path.join(mod, "Defs", "old.xml"), "<defName>RM_Moved</defName>\n")
        _w(os.path.join(mod, "Defs", "staged.xml"), "<defName>RM_Staged</defName>\n")
        git("add", "-A")
        git("commit", "-q", "-m", "base")
        _w(a, "<defName>RM_Base</defName>\n<defName>RM_Committed</defName>\n")
        u = os.path.join(mod, "Defs", "\u00fcber.xml")
        _w(u, "<defName>RM_Uber</defName>\n")
        git("add", "-A")
        git("mv", "Mod/Defs/old.xml", "Mod/Defs/new.xml")
        git("commit", "-q", "-m", "range")
        _w(a, "<defName>RM_Base</defName>\n<defName>RM_Committed</defName>\n<defName>RM_Uncommitted</defName>\n")
        st = os.path.join(mod, "Defs", "staged.xml")
        _w(st, "<defName>RM_StagedEdit</defName>\n")
        git("add", "Mod/Defs/staged.xml")
        _w(st, "<defName>RM_Staged</defName>\n")         # worktree back to HEAD; the index still differs
        got = dict(targeting.changed_files(mod, "HEAD~1..HEAD", root=root))
        ta = got.get("Defs/a.xml") or ""
        ok("RM_Committed" in ta and "RM_Uncommitted" in ta,
           "a file changed both uncommitted and in --range keeps both specs' lines", ta)
        ok("Defs/\u00fcber.xml" in got and "RM_Uber" in (got["Defs/\u00fcber.xml"] or ""),
           "a non-ASCII path is read raw (-z), not git's C-quoted form", sorted(got))
        ok("Defs/old.xml" in got and "Defs/new.xml" in got, "a rename lists its source path too", sorted(got))
        ok("RM_StagedEdit" in (got.get("Defs/staged.xml") or ""),
           "a staged change whose worktree was restored to HEAD is still seen", got.get("Defs/staged.xml"))
        wt = dict(targeting.changed_files(mod, "WORKTREE", root=root))
        ok("RM_Uncommitted" in (wt.get("Defs/a.xml") or "") and "RM_Committed" not in (wt.get("Defs/a.xml") or ""),
           "WORKTREE alone carries only the uncommitted lines", wt.get("Defs/a.xml"))
    finally:
        shutil.rmtree(root, ignore_errors=True)


def t_changed_stem_whole_token():
    s = Suite("X")

    @s.chain("pumps")
    def pumps(t):
        """drives WaterPump through its ports"""
        return t
    res = targeting.changed(s, [("Source/WaterPump.cs", "x"), ("Source/Unrelated.cs", "y")])
    ok("pumps" in res["suggest"] and res["unknown"] == ["Source/Unrelated.cs"],
       "an underscore-free stem (WaterPump.cs) maps by whole-token match", res)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    while "--unstub" in argv:
        i = argv.index("--unstub")
        UNSTUB.add(argv[i + 1])
        del argv[i:i + 2]
    for t in (t_resolve, t_targeted_suite_keeps_site_hold, t_emit_verify_seat, t_run_records_without_seat,
              t_run_targeted, t_cli_refusals, t_scope_and_preview, t_incomplete_catalogue_refused,
              t_offline_chains_out_of_live, t_stop_after_runtime, t_hold_contract_every_run, t_cli_preview,
              t_nested_evidence_stays_on_outer, t_item_text_utf8_under_cp1252, t_item_text_retries_wsl_hiccup,
              t_changed_files_every_spec,
              t_changed_stem_whole_token):
        try:
            t()
        except Exception as ex:     # noqa: BLE001 - one broken test must not hide the others
            ok(False, "%s raised %s: %s" % (t.__name__, type(ex).__name__, ex))
    ok(not BRIDGE_REACHES, "hermetic: the stubbed run never reaches the bridge (stub the runner caller named)",
       sorted(set(BRIDGE_REACHES)))
    print("\nSELFTEST %s -- %d failed" % ("FAILED" if FAILS else "OK", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
