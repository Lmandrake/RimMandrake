#!/usr/bin/env python3
"""Selftest of role_launch.py's own behaviour (ROLE_LAUNCH_HARDEN_MUTATION_SURVIVORS): each check below kills named
surviving mutants of the mutmut run 20261028f (stop path, unit/scope queries, launch result, schedule validation,
the ops reading and throttle band). Pure: fake runners, no systemd, no clock."""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import role_launch as RL  # noqa: E402

FAILS = []


def check(ok, msg):
    if not ok:
        FAILS.append(msg)
        print("FAIL:", msg)


def cp(rc=0, out="", err=""):
    return subprocess.CompletedProcess([], rc, out, err)


def raises(fn, text=None):
    try:
        fn()
    except ValueError as e:
        return text is None or text in str(e)
    return False


# ---------------------------------------------------------------- _stop_call / stop: a failed stop is not a success
def test_stop_call_failed_is_not_ok():
    seen = {}

    def run(argv, **kw):
        seen.update(kw)
        return cp(5, "boom-out", "boom-err")
    line = RL._stop_call(run, ["systemctl", "--user", "stop", "--no-block", "U"], 30)
    check("exit 5" in line and "ok" not in line.split("U", 1)[1].split(":")[0], "failed stop reads as failure: %r" % line)
    check(line.startswith("stop U exit 5: ") and "boom-outboom-err" in line, "stdout+stderr tail kept: %r" % line)
    check(seen.get("capture_output") is True and seen.get("text") is True and seen.get("timeout") == 30,
          "stop call captures text output with its timeout: %r" % seen)
    for rc in (1, 2, 255):      # every non-zero code is a failure, not only 1
        check("exit %d" % rc in RL._stop_call(lambda a, **k: cp(rc), ["systemctl", "--user", "stop", "--no-block", "U"], 30),
              "exit %d is a failure" % rc)
    ok = RL._stop_call(lambda a, **k: cp(0), ["systemctl", "--user", "kill", "--signal=SIGKILL", "S.scope"], 30)
    check(ok == "kill S.scope ok", "success line: %r" % ok)
    long = RL._stop_call(lambda a, **k: cp(1, "x" * 200, "y" * 200), ["systemctl", "--user", "stop", "U"], 30)
    check(long.split(": ", 1)[1] == "y" * 120, "tail is the last 120 chars: %r" % long[-130:])
    check(RL._stop_call(lambda a, **k: cp(1, None, None), ["systemctl", "--user", "stop", "U"], 30) == "stop U exit 1: ",
          "None output tolerated")

    def boom(argv, **kw):
        raise RuntimeError("z" * 200)
    r = RL._stop_call(boom, ["systemctl", "--user", "stop", "--no-block", "U"], 30)
    check(r == "stop U raised RuntimeError: " + "z" * 80, "raise line names verb, unit, type, 80 chars: %r" % r)


def test_stop_reports_each_failure():
    calls = []

    def run(argv, **kw):
        calls.append(argv)
        return cp(1 if argv[-1] == "S.scope" else 0, "", "nope")
    out = RL.stop("U", "S.scope", runner=run)
    check("stop S.scope exit 1" in out and "stop U ok" in out, "scope failure and unit success both reported: %r" % out)
    check(RL.stop("U", None, unit_gone=True) == "nothing to stop (no scope, unit gone, no marker)", "nothing-to-stop line")


# ---------------------------------------------------------------- a failed stop is re-issued every tick (supervise)
def test_failed_stop_reissued_each_tick():
    acts = []

    def act(**kw):
        acts.append(kw)
    obs = {"unit_state": lambda u: "active", "result": lambda r: {}}
    cfg = {"run_max_s": 100, "seat": "S"}
    rs = {"runs": [{"state": "running", "unit": "U", "at": 0, "scope": "U.scope", "marker": "U", "item": "I"}]}
    busy = set()
    for tick in range(4):
        acts.clear()
        RL._supervise_one("r", rs, cfg, obs, 1000 + tick * 120, act, busy)
        stops = [a for a in acts if a["do"] == "role_stop"]
        check(len(stops) == 1, "tick %d: the stop is issued again" % tick)
        check(stops and stops[0]["force"] is (tick >= 2), "tick %d: KILL from the third stop on" % tick)
        kinds = [a["kind"] for a in acts if a["do"] == "alarm"]
        check(kinds == (["role:r:overtime"] if tick == 0 else ["role:r:stop_failed"]), "tick %d alarm kinds %r" % (tick, kinds))
    run = rs["runs"][0]
    check(run["state"] == "running" and run["stop_tries"] == 4 and "r" in busy, "run stays running and busy while stops fail")
    acts.clear()      # inside run_max_s: no stop
    rs2 = {"runs": [{"state": "running", "unit": "U", "at": 950, "scope": "U.scope"}]}
    RL._supervise_one("r", rs2, cfg, obs, 1000, act, set())
    check(not [a for a in acts if a["do"] == "role_stop"], "no stop before run_max_s")
    acts.clear()      # exactly at run_max_s counts as over
    rs3 = {"runs": [{"state": "running", "unit": "U", "at": 900, "scope": "U.scope"}]}
    RL._supervise_one("r", rs3, cfg, obs, 1000, act, set())
    check([a for a in acts if a["do"] == "role_stop"], "a stop at exactly run_max_s")


# ---------------------------------------------------------------- unit_state / scope_of
def test_unit_state_and_scope_of():
    seen = {}

    def run(argv, **kw):
        seen["argv"], seen["kw"] = argv, kw
        return cp(0, " active \n")
    check(RL.unit_state("U", run) == "active", "state stripped")
    check(seen["kw"].get("capture_output") is True and seen["kw"].get("text") is True and seen["kw"].get("timeout") == 30,
          "unit_state call args %r" % seen["kw"])
    check(RL.unit_state("U", lambda a, **k: cp(0, "")) == "unknown", "empty -> unknown")
    check(RL.unit_state("U", lambda a, **k: cp(0, None)) == "unknown", "None -> unknown")
    check(RL.unit_state("U", lambda a, **k: cp(3, "active")) == "unknown", "non-zero exit -> unknown")

    def boom(a, **k):
        raise OSError("x")
    check(RL.unit_state("U", boom) == "unknown", "raise -> unknown")
    check(RL.scope_of("U", "S", lambda a, **k: cp(0, "1234\n")) == "claude-seat-S-1234.scope", "scope from MainPID")
    check(RL.scope_of("U", "S", lambda a, **k: cp(0, "0\n")) is None, "MainPID 0 -> None")
    check(RL.scope_of("U", "S", lambda a, **k: cp(0, "abc\n")) is None, "non-digit MainPID -> None (digit AND not 0)")
    check(RL.scope_of("U", "S", lambda a, **k: cp(0, "")) is None, "empty MainPID -> None")
    check(RL.scope_of("U", "S", lambda a, **k: cp(1, "1234")) is None, "failed query -> None")
    check(RL.scope_of("U", "S", boom) is None, "raise -> None")
    kw = {}

    def run2(a, **k):
        kw.update(k)
        return cp(0, "7")
    RL.scope_of("U", "S", run2)
    check(kw.get("capture_output") is True and kw.get("text") is True and kw.get("timeout") == 30, "scope_of call args %r" % kw)


# ---------------------------------------------------------------- launch
def test_launch_result():
    role = {"name": "r", "seat": "SEAT", "clone": "/tmp/clone", "model": "sonnet"}
    import tempfile
    root = tempfile.mkdtemp(prefix="selftest_role_launch_")
    kw = {}

    def bad(argv, **k):
        kw.update(k)
        return cp(7, "o" * 300, "e" * 10)
    ok, out, rec = RL.launch(role, "rm-role-r-1", "msg", root, "/usr/bin/claude", runner=bad)
    check(ok is False and rec == {} and out.startswith("systemd-run exit 7: ") and out.endswith("o" * 190 + "e" * 10),
          "failed systemd-run -> (False, tail of 200 chars, {}): %r" % out[-30:])
    check(len(out.split(": ", 1)[1]) == 200, "tail is exactly 200 chars")
    check(kw.get("capture_output") is True and kw.get("text") is True and kw.get("timeout") == 60, "launch call args %r" % kw)
    ok, out, rec = RL.launch(role, "rm-role-r-1", "msg", root, "/usr/bin/claude", runner=lambda a, **k: cp(0))
    check(ok is True and rec["marker"] == "rm-role-r-1" and rec["scope"] == "claude-seat-SEAT-rm-role-r-1.scope"
          and rec["out"].endswith("rm-role-r-1.json") and rec["err"].endswith("rm-role-r-1.err"), "good launch record %r" % rec)


def test_launch_argv_shape():
    role = {"name": "r", "seat": "SEAT", "clone": "/c", "model": "opus", "run_max_s": 1000}
    a = RL.launch_argv(role, "U", "MSG", "/o.json", "/e.err", "/bin/claude")
    check(a[:4] == ["systemd-run", "--user", "--quiet", "--collect"] and a[4:6] == ["--unit", "U"], "head %r" % a[:6])
    check("StandardOutput=file:/o.json" in a and "StandardError=file:/e.err" in a, "out/err files")
    check("--working-directory" in a and a[a.index("--working-directory") + 1] == "/c", "working dir is the clone")
    for e in ("AGENT_SEAT=SEAT", "RIMFLOW_SEAT=SEAT", "CLAUDE_SCOPE_UNIT=claude-seat-SEAT-U", "RM_ROLE_UNIT=U",
              "CLAUDE_SCOPE_RUNTIME_MAX=1600"):
        check(e in a and a[a.index(e) - 1] == "--setenv", "setenv %s" % e)
    check("RuntimeMaxSec=1600" in a and "TimeoutStopSec=30" in a, "unit bound is run_max_s + grace")
    check(any(x.startswith("PATH=/bin:") for x in a), "claude's dir leads PATH")
    i = a.index("--")
    check(a[i + 1].endswith("claude_bounded.sh") and a[i + 2:i + 4] == ["-p", "MSG"]
          and a[a.index("--model") + 1] == "opus" and a[-3:] == ["--output-format", "json", "--dangerously-skip-permissions"],
          "claude_bounded argv %r" % a[i:])
    check(RL.scope_bound_s(role) == 1600 and RL.scope_bound_s(None) == 1800 + 600 and RL.scope_bound_s({}) == 2400, "scope bound")
    role["pre_launch"] = [["a", "b c"], ["d"]]
    a = RL.launch_argv(role, "U", "MSG", "/o", "/e", "/bin/claude")
    j = a.index("/bin/sh")
    check(a[j + 2] == "a 'b c' 1>&2 && d 1>&2 && exec \"$@\"", "pre-steps quoted and chained: %r" % a[j + 2])
    role["pre_launch"] = ["a", ""]
    check(raises(lambda: RL.launch_argv(role, "U", "M", "/o", "/e", "/c/claude"), "pre_launch"), "bad pre_launch refused")


# ---------------------------------------------------------------- model_id
def test_model_id():
    check(RL.model_id("opus", {"ANTHROPIC_DEFAULT_OPUS_MODEL": " claude-x[1m] "}) == "claude-x", "env id, [1m] stripped")
    home = os.environ.get("HOME")
    import tempfile
    h = tempfile.mkdtemp(prefix="selftest_role_launch_home_")
    os.makedirs(os.path.join(h, ".claude"))
    with open(os.path.join(h, ".claude", "settings.json"), "w") as f:
        f.write('{"env": {"ANTHROPIC_DEFAULT_SONNET_MODEL": " from-settings "}}')
    os.environ["HOME"] = h
    try:
        check(RL.model_id("sonnet", {}) == "from-settings", "falls back to ~/.claude/settings.json env")
        check(RL.model_id("haiku", {}) is None, "no var anywhere -> None")
        check(RL.model_id("nosuch", {}) is None, "unknown alias -> None")
        check(RL.model_id("sonnet", {"ANTHROPIC_DEFAULT_SONNET_MODEL": "env-wins"}) == "env-wins", "env beats settings")
    finally:
        os.environ["HOME"] = home


# ---------------------------------------------------------------- ops_reading
def test_ops_reading():
    now = RL.utc_epoch("2026-10-27T12:00:00Z")
    pts = {"accounts.A.runway": {"m": "ESTIMATE", "v": 3}, "accounts.A.week_left_pct": {"m": "MEASURED", "v": 40}}

    def st(at, points=pts):
        return {"at": at, "points": points}
    r = RL.ops_reading(st("2026-10-27T12:00:00Z"), "A", now)
    check(r["state"] == "MEASURED" and r["runway"] == 3.0 and r["runway_m"] == "ESTIMATE" and r["week_left"] == 40.0
          and r["week_left_m"] == "MEASURED" and r["account"] == "A", "measured reading %r" % r)
    # future tolerance: exactly 300 s ahead is still fresh, 301 is a clock fault
    check(RL.ops_reading(st("2026-10-27T12:05:00Z"), "A", now)["state"] == "MEASURED", "300 s ahead is tolerated")
    f = RL.ops_reading(st("2026-10-27T12:06:00Z"), "A", now)
    check(f["state"] == "UNMEASURED" and "6 min in the FUTURE" in f["why"], "6 min ahead: %r" % f)
    f = RL.ops_reading(st("2026-10-27T13:00:00Z"), "A", now)
    check("60 min in the FUTURE" in f["why"], "future minutes are at-now over 60: %r" % f["why"])
    # staleness: exactly stale_s old is still fresh
    check(RL.ops_reading(st("2026-10-27T11:15:00Z"), "A", now)["state"] == "MEASURED", "exactly 45 min old is fresh")
    s = RL.ops_reading(st("2026-10-27T11:00:00Z"), "A", now)
    check(s["state"] == "UNMEASURED" and "STALE" in s["why"] and "60 min old (> 45)" in s["why"], "stale text %r" % s)
    s = RL.ops_reading(st("2026-10-27T11:00:00Z"), "A", now, stale_s=7200)
    check(s["state"] == "MEASURED", "stale_s is honoured")
    check(RL.ops_reading(None, "A", now)["state"] == "UNMEASURED", "no status")
    check(RL.ops_reading({"at": "junk"}, "A", now)["state"] == "UNMEASURED", "bad at")
    check(RL.ops_reading(st("2026-10-27T12:00:00Z"), None, now)["state"] == "UNMEASURED", "no account")
    bad = RL.ops_reading(st("2026-10-27T12:00:00Z", {"accounts.A.runway": {"m": "MEASURED", "v": float("nan")}}), "A", now)
    check(bad["state"] == "UNMEASURED" and "not a finite number" in bad["why"] and "accounts.A.runway is MEASURED" in bad["why"],
          "NaN refused with the value named: %r" % bad)
    bad = RL.ops_reading(st("2026-10-27T12:00:00Z", {"accounts.A.runway": {"m": "UNMEASURED", "why": "no data", "v": 2}}), "A", now)
    check("accounts.A.runway is UNMEASURED (no data)" in bad["why"] and "not a finite" not in bad["why"], "unmeasured point: %r" % bad["why"])
    bad = RL.ops_reading(st("2026-10-27T12:00:00Z", {}), "A", now)
    check("accounts.A.runway is absent" in bad["why"], "absent point: %r" % bad["why"])
    bad = RL.ops_reading(st("2026-10-27T12:00:00Z", {"accounts.A.runway": "junk"}), "A", now)
    check("is absent" in bad["why"], "non-dict point treated as absent: %r" % bad["why"])


# ---------------------------------------------------------------- band
def test_band():
    bands = {"FLOOR": {"week_left_pct_lt": 10, "slots": "none", "quick_cap_x": 0.0},
             "HIGH": {"runway_ge": 5, "slots": "all", "quick_cap_x": 1.0},
             "LOW": {"runway_ge": 2, "slots": "first", "quick_cap_x": 0.5}}
    role = {"throttle_bands": bands}
    check(RL.band({}, {}) == ("NONE", {"quick_cap_x": 1.0, "slots": "all"}), "no bands -> NONE x1.0")
    check(RL.band(role, {"week_left": 9.9, "runway": 9})[0] == "FLOOR", "below the floor line")
    check(RL.band(role, {"week_left": 10, "runway": 9})[0] == "HIGH", "exactly on the floor line is not floor")
    check(RL.band(role, {"week_left": 50, "runway": 5})[0] == "HIGH", "runway meeting the line")
    check(RL.band(role, {"week_left": 50, "runway": 4.9})[0] == "LOW", "next band down")
    check(RL.band(role, {"week_left": 50, "runway": 0.1})[0] == "LOW", "below every line -> the lowest runway band")
    check(raises(lambda: RL.band({"throttle_bands": {"F": {"week_left_pct_lt": 5}}}, {"week_left": 50, "runway": 1}), "runway_ge"),
          "no runway band -> ValueError")


# ---------------------------------------------------------------- validate_role
def good():
    return {"run_max_s": 60, "slot_late_s": 60}


def test_validate_role():
    RL.validate_role(good())
    check(raises(lambda: RL.validate_role(dict(good(), throttle_bands=[1])), "mapping"), "bands must be a mapping")
    check(raises(lambda: RL.validate_role(dict(good(), throttle_bands={"A": 1})), "throttle band A is not a mapping"), "band mapping")
    check(raises(lambda: RL.validate_role(dict(good(), throttle_bands={"A": {"runway_ge": "x"}})), "not a number"), "band number")
    check(raises(lambda: RL.validate_role(dict(good(), throttle_bands={"A": {"week_left_pct_lt": 5}})), "runway_ge"),
          "bands with no runway_ge refused")
    RL.validate_role(dict(good(), throttle_bands={"A": {"runway_ge": 1}, "B": {"week_left_pct_lt": 5}}))
    check(raises(lambda: RL.validate_role(dict(good(), slot_when="nope")), "slot_when 'nope'"), "slot_when")
    for sw in (None, "done_claims", "pending_work"):
        RL.validate_role(dict(good(), slot_when=sw))
    check(raises(lambda: RL.validate_role(dict(good(), pending_work=[])), "pending_work"), "empty pending_work")
    check(raises(lambda: RL.validate_role(dict(good(), pending_work=["zzz"])), "pending_work ['zzz']"), "unknown kind")
    check(raises(lambda: RL.validate_role(dict(good(), claim_window_days=3)), "retired"), "claim_window_days retired")
    check(raises(lambda: RL.validate_role(dict(good(), pre_launch_max_s=0)), "pre_launch_max_s 0 is not a number > 0"), "pre 0")
    RL.validate_role(dict(good(), pre_launch_max_s=1))
    RL.validate_role(dict(good(), pre_launch_max_s=0.5))
    RL.validate_role(dict(good(), event_runs_per_day=0))
    RL.validate_role(dict(good(), event_runs_per_day=1))
    for bad in (-1, 1.5, True, "1"):
        check(raises(lambda: RL.validate_role(dict(good(), event_runs_per_day=bad)), "event_runs_per_day"), "per_day %r" % (bad,))
    for k in ("run_token_cap", "quick_token_cap", "economy_token_cap", "daily_token_cap"):
        RL.validate_role(dict(good(), **{k: 0}))
        RL.validate_role(dict(good(), **{k: 0.5}))
        RL.validate_role(dict(good(), **{k: None}))
        check(raises(lambda: RL.validate_role(dict(good(), **{k: -1}), ) , "%s -1 is not a number >= 0" % k), "%s negative" % k)
    for k in ("slot_late_s", "run_max_s"):
        RL.validate_role(dict(good(), **{k: 1}))
        RL.validate_role(dict(good(), **{k: 0.5}))
        for bad in (0, -5, None, True, "9"):
            r = dict(good())
            r[k] = bad
            check(raises(lambda: RL.validate_role(r), "%s %r is not a number > 0" % (k, bad)), "%s=%r refused" % (k, bad))
    r = dict(good())
    del r["run_max_s"]
    check(raises(lambda: RL.validate_role(r), "run_max_s None"), "missing run_max_s refused")
    check(raises(lambda: RL.validate_role(dict(good(), event_runs="x")), "event_runs is not a list"), "event_runs list")


TESTS = (test_stop_call_failed_is_not_ok, test_stop_reports_each_failure, test_failed_stop_reissued_each_tick,
         test_unit_state_and_scope_of, test_launch_result, test_launch_argv_shape, test_model_id, test_ops_reading,
         test_band, test_validate_role)


def main():
    for t in TESTS:
        try:
            t()
        except Exception as e:  # noqa: BLE001
            import traceback
            traceback.print_exc()
            check(False, "%s crashed: %s" % (t.__name__, e))
    print("%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
