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
    sel = targeting.resolve(s, item="SOME_ITEM", text="the `thirst` chain and row lines_drawn_ok; lines and thirst")
    ok(sel["chains"] == ["lines", "thirst"], "item: ledger text naming a backticked chain / an underscored row id",
       sel["chains"])
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
             "write_sheet", "mod_dependency_ids", "composed_into", "mod_package_id")
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

    def fake_suite(s, sess, **k):
        seen["suite"].append(([n for n, _ in s.chains], k.get("hold_site"), k.get("floor_suite")))
        return {"chains": [], "all_green": True, "findings": [], "refused": ""}
    runner.swap_to_test_list = runner.restore_full = runner.compose_test_list = lambda *a, **k: None
    runner.find_mod_dir = lambda m: "/nonexistent/" + m
    runner.load_validation = lambda d: make_suite()
    runner.northstar_for = lambda m: (None, None)
    runner.visual_floor = lambda s, ns: {"bar": [], "uncovered": [], "orphans": []}
    runner.ensure_playing_map = runner.ensure_test_profile = lambda *a, **k: None
    runner.run_suite = fake_suite
    runner.write_sheet = lambda m, s: "/tmp/ToyMod_sheet.html"
    runner.mod_dependency_ids, runner.composed_into, runner.mod_package_id = (lambda d: []), (lambda m: None), (lambda d: "x.y")
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


def main():
    for t in (t_resolve, t_targeted_suite_keeps_site_hold, t_emit_verify_seat, t_run_records_without_seat,
              t_run_targeted, t_cli_refusals):
        try:
            t()
        except Exception as ex:     # noqa: BLE001 - one broken test must not hide the others
            ok(False, "%s raised %s: %s" % (t.__name__, type(ex).__name__, ex))
    print("\nSELFTEST %s -- %d failed" % ("FAILED" if FAILS else "OK", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
