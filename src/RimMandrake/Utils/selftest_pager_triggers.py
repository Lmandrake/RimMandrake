#!/usr/bin/env python3
"""selftest_pager_triggers.py — the promises of pager_triggers.py
(design/specs/2026-11-19-pushover-critical-alerts/triggers_boundary.md). Offline: a temp data root and a fake sender.
`--plants` plants each fault of PLANTS in a copy of pager_triggers.py and wants this selftest red on it.
"""
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import tempfile

TMP = tempfile.mkdtemp(prefix="selftest_pager_triggers_")
os.environ["RM_PAGER_DIR"] = os.path.join(TMP, "pager")
os.environ["RM_PAGER_CONDUCTOR_LOG"] = os.path.join(TMP, "conductor_log.md")
os.environ["RM_PAGER_CREDENTIALS"] = os.path.join(TMP, "none.env")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pager as P  # noqa: E402
import pager_triggers as T  # noqa: E402

FAILS = []
NOW = dt.datetime(2026, 11, 24, 20, 0, tzinfo=dt.timezone.utc)
COND = ({"AGENT_SEAT": "BENCH"}, "0::/claude-seat-BENCH-77.scope/seat\n")
HELPER = ({"AGENT_SEAT": "BENCH", "RM_ROLE_UNIT": "rm-detached-bench-x-1"}, "0::/claude-seat-BENCH-rm-detached-x.scope\n")


def check(ok, what):
    if not ok:
        FAILS.append(what)
        print("FAIL:", what)


def ago(minutes):
    return (NOW - dt.timedelta(minutes=minutes)).strftime("%Y-%m-%dT%H:%M:%SZ")


def root(**kw):
    """A data root where every trigger is CLEAR, then changed by kw."""
    r = tempfile.mkdtemp(dir=TMP)

    def put(rel, obj):
        p = os.path.join(r, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            f.write(obj if isinstance(obj, str) else json.dumps(obj))
    mark = kw.get("mark", "MEASURED")
    pt = lambda v: {"v": v, "m": mark, "x": {"observed_at": ago(kw.get("age", 5))}}  # noqa: E731
    put("ops_watch/status.json", kw.get("status", {"at": ago(1), "points": {
        "disk.whea_severe_24h": pt(kw.get("whea", 0)), "disk.root_free_gb": pt(kw.get("gb", 450)),
        "disk.c_free_gb": pt(kw.get("gb", 450)), "disk.d_free_gb": pt(kw.get("gb", 450))}}))
    put("testq/fault_state.json", {"at": ago(kw.get("age", 5)), "phase": kw.get("phase", "CLEAN")})
    put("switching_plan/state.json", kw.get("state", {"last_poll": ago(5)}))
    os.makedirs(os.path.join(r, "switching_plan", "markers"))
    for n, m in kw.get("markers", {"use_a_to_b_20261125": {"phase": "done", "at": ago(9000)}}).items():
        put("switching_plan/markers/%s.json" % n, m)
    return r


def v(name, r):
    return T.read(name, r, NOW)[0]


def switch(*names):
    shutil.rmtree(P.pager_dir(), ignore_errors=True)
    for n in names:
        T.set_switch(n, True, "the test switches it on", NOW, *COND)


class Sender:
    def __init__(self, outcome=None):
        self.calls, self.outcome = [], outcome or P.SENT

    def __call__(self, cls, cause, reading, why, dry_run=False):
        self.calls.append((cls, cause, reading, why))
        return self.outcome, {"class": cls, "cause": cause, "detail": ""}


def t_each_trigger_fires_on_its_line():
    for n in T.TRIGGERS:
        check(v(n, root()) == T.CLEAR, "%s is CLEAR on a quiet estate: %r" % (n, T.read(n, root(), NOW)))
    check(v("whea_severe", root(whea=1)) == T.FIRES, "one fatal WHEA event fires")
    check(v("steve_stuck", root(phase="STUCK")) == T.FIRES, "phase STUCK fires")
    for n in ("disk_root", "disk_c", "disk_d"):
        check(v(n, root(gb=49.9)) == T.FIRES and v(n, root(gb=50)) == T.CLEAR, "%s fires under 50 GB only" % n)
    f = {"use_a_to_b_20261125": {"phase": "failed", "at": ago(30)}}
    check(v("switch_failed", root(markers=f)) == T.FIRES, "a fresh failed marker fires")
    check(v("switch_failed", root(markers={})) == T.CLEAR, "an empty markers folder is CLEAR: looked and found none")
    check(v("switch_failed", root(markers=dict(f, use_b_to_c_20261125={"phase": "done", "at": ago(5)}))) == T.CLEAR,
          "a good switch after the failure clears it")
    check(v("switch_failed", root(markers=dict(f, use_b_to_c_20261125={"phase": "done", "at": ago(60)}))) == T.FIRES,
          "a good switch before the failure does not clear it")
    check(v("switch_failed", root(markers={"m": {"phase": "failed", "at": ago(7 * 60)}})) == T.CLEAR,
          "a failure that the plan stopped retrying over 6 h ago does not page")
    check(v("switch_failed", root(markers={"m": {"phase": "lapsed", "at": ago(5)}})) == T.CLEAR, "lapsed is not failed")
    check(v("fleet_stop", root(state={"stopped": {"account": "a", "at": "2026-11-24T11:00:00-08:00"}})) == T.FIRES,
          "a stopped fleet fires")


def t_could_not_look_is_never_clear():
    for n in ("whea_severe", "disk_root", "disk_c", "disk_d"):
        check(v(n, root(mark="UNMEASURED")) == T.COULD_NOT_LOOK, "%s UNMEASURED could not look" % n)
        check(v(n, root(mark="ESTIMATE", whea=3, gb=1)) == T.COULD_NOT_LOOK, "%s ESTIMATE never pages" % n)
        check(v(n, root(age=46)) == T.COULD_NOT_LOOK, "%s stale could not look" % n)
        check(v(n, root(age=46, whea=3, gb=1)) == T.COULD_NOT_LOOK, "%s stale never pages" % n)
        check(v(n, root(status='{"torn')) == T.COULD_NOT_LOOK, "%s torn status could not look" % n)
        check(v(n, root(status={"points": {}})) == T.COULD_NOT_LOOK, "%s missing could not look" % n)
        check(v(n, root(status=[])) == T.COULD_NOT_LOOK, "%s wrong shape could not look" % n)
        check(v(n, os.path.join(TMP, "nowhere")) == T.COULD_NOT_LOOK, "%s no file could not look" % n)
    check(v("steve_stuck", root(phase="PASSIVE")) == T.COULD_NOT_LOOK, "a passive monitor cannot see STUCK")
    check(v("steve_stuck", root(phase="STUCK", age=46)) == T.COULD_NOT_LOOK, "a stale phase could not look")
    check(v("fleet_stop", root(state='{"torn')) == T.COULD_NOT_LOOK, "a torn plan state could not look")
    check(v("switch_failed", root(markers={"m": '{"torn'})) == T.COULD_NOT_LOOK, "a torn marker could not look")
    check(v("switch_failed", root(markers={"m": {"phase": "failed", "at": None}})) == T.COULD_NOT_LOOK, "a failed marker with no time")
    for n in ("steve_stuck", "switch_failed", "fleet_stop"):
        check(v(n, os.path.join(TMP, "nowhere")) == T.COULD_NOT_LOOK, "%s no file could not look" % n)


def t_off_until_switched_on():
    switch()
    s = Sender()
    rc, lines = T.run(root(whea=2, gb=1), NOW, s)
    check(rc == 4 and not s.calls, "none on: exit 4, no page (%s)" % lines)
    switch("disk_d")
    rc, lines = T.run(root(whea=2, gb=1), NOW, s)
    check([c[1] for c in s.calls] == ["disk.d_free_gb"] and rc == 0, "only the ON trigger pages: %r" % s.calls)
    check([ln for ln in T.status(root(), NOW)[1] if " ON " in ln][0].startswith("disk_d"), "status names the ON one")


def t_only_the_conductor_switches():
    switch()
    ok, line = T.set_switch("disk_d", True, "the test switches it on", NOW, *HELPER)
    check(not ok and "REFUSED" in line and T.switches() == {}, "a helper is refused and nothing is on")
    ok, _ = T.set_switch("no_such", True, "the test switches it on", NOW, *COND)
    check(not ok, "an unknown trigger is refused")
    ok, _ = T.set_switch("disk_d", True, "short", NOW, *COND)
    check(not ok, "a thin why is refused")
    switch("disk_d")
    check("disk_d switched ON" in open(os.environ["RM_PAGER_CONDUCTOR_LOG"]).read(), "the switch is in the Conductor log")
    T.set_switch("disk_d", False, "the test switches it off", NOW, *COND)
    check(T.switches() == {}, "off removes it")


def t_torn_switch_file_is_not_all_off():
    switch("disk_d")
    with open(T.switch_path(), "w") as f:
        f.write('{"disk')
    s = Sender()
    rc, lines = T.run(root(gb=1), NOW, s)
    check(rc == 3 and not s.calls and "COULD NOT LOOK" in lines[0], "a torn switch file exits 3: %s" % lines)
    check(T.status(root(), NOW)[0] == 3, "status too")


def t_run_exits_tell_outcomes_apart():
    switch("whea_severe", "disk_d")
    check(T.run(root(), NOW, Sender())[0] == 0, "all clear is 0")
    check(T.run(root(gb=1), NOW, Sender(P.REPEAT))[0] == 0, "a repeat is 0")
    check(T.run(root(gb=1), NOW, Sender(P.REFUSED))[0] == 1, "a refused page is 1")
    check(T.run(root(gb=1), NOW, Sender(P.COULD_NOT_SEND))[0] == 1, "a page that did not leave is 1")
    check(T.run(root(age=99), NOW, Sender())[0] == 3, "an unread trigger is 3")


def t_a_fired_page_passes_the_pager():
    """The real pager.send takes every trigger's class, cause, reading and why (dry run, an Operations caller)."""
    u = "rm-role-operations-1795138643"
    env, cg = {"AGENT_SEAT": "BENCH", "RM_ROLE_UNIT": u}, "0::/%s.service\n" % u
    r = root(whea=2, gb=1, phase="STUCK", markers={"use_a_to_b_20261125": {"phase": "failed", "at": ago(3)}},
             state={"stopped": {"account": "a", "at": ago(3)}})
    switch(*T.TRIGGERS)
    seen = []

    def send(*a, **k):
        o, rec = P.send(*a, env=env, cgroup=cg, **k)
        seen.append((o, rec.get("detail")))
        return o, rec
    rc, _ = T.run(r, NOW, send, dry_run=True)
    check(rc == 0 and len(seen) == len(T.TRIGGERS) and all(o == P.DRY_RUN for o, _ in seen), "each is accepted: %r" % seen)


PLANTS = [
    ("stale is trusted", "if age > MAX_AGE_MIN:", "if False:"),
    ("UNMEASURED is read", 'if p.get("m") != "MEASURED" or', "if"),
    ("whea never fires", "FIRES if v > 0 else CLEAR", "CLEAR"),
    ("disk line at 5", "DISK_FLOOR_GB = 50 ", "DISK_FLOOR_GB = 5 "),
    ("PASSIVE reads clear", 'if ph == "PASSIVE":', "if False:"),
    ("old failure pages for days", "if (now - failed[0]).total_seconds() > FAILED_FRESH_H * 3600:", "if False:"),
    ("any done clears", "done > failed[0])", "True)"),
    ("a stop is missed", "    if not s:\n", "    if True:\n"),
    ("off triggers page", "        if name not in on:\n            continue\n", ""),
    ("any caller switches", 'if who != "conductor":', "if False:"),
    ("a torn switch file is all off", "    d = _load(switch_path())\n", "    try:\n        d = _load(switch_path())\n    except CannotLook:\n        return {}\n"),
    ("a lost page exits 0", "unsent += 1", "unsent += 0"),
    ("a blind trigger exits 0", "blind += verdict == COULD_NOT_LOOK", "blind += 0"),
    ("a cause the pager refuses", '"switching_plan:" + failed[1]', '"Switching Plan " + failed[1]'),
    ("a reading the pager refuses", '"disk %s free = %g GB (line %d)"', '"disk %s/ free = %g GB (line %d)"'),
]


def plants():
    missed = 0
    src = open(os.path.join(HERE, "pager_triggers.py"), encoding="utf-8").read()
    for name, a, b in PLANTS:
        if src.count(a) != 1:
            print("BROKEN: plant %r: anchor found %d times" % (name, src.count(a)))
            return 3
        u = tempfile.mkdtemp(dir=TMP)
        for f in ("pager.py", "pager_classes.json", "rmpaths.py", "selftest_pager_triggers.py"):
            shutil.copy(os.path.join(HERE, f), u)
        with open(os.path.join(u, "pager_triggers.py"), "w", encoding="utf-8") as f:
            f.write(src.replace(a, b))
        r = subprocess.run([sys.executable, "-B", os.path.join(u, "selftest_pager_triggers.py")], capture_output=True, text=True)
        ok = r.returncode == 1 and "FAIL:" in r.stdout
        missed += not ok
        print("%s  %s" % ("caught    " if ok else "NOT CAUGHT", name))
    print("CAUGHT %d of %d" % (len(PLANTS) - missed, len(PLANTS)))
    return 1 if missed else 0


def main():
    for t in (t_each_trigger_fires_on_its_line, t_could_not_look_is_never_clear, t_off_until_switched_on,
              t_only_the_conductor_switches, t_torn_switch_file_is_not_all_off, t_run_exits_tell_outcomes_apart,
              t_a_fired_page_passes_the_pager):
        try:
            t()
        except Exception as e:  # noqa: BLE001
            check(False, "%s raised %s: %s" % (t.__name__, type(e).__name__, e))
    print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    try:
        rc = plants() if "--plants" in sys.argv else main()
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    sys.exit(rc)
