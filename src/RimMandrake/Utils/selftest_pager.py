#!/usr/bin/env python3
"""selftest_pager.py — the promises of pager.py (design/specs/2026-11-19-pushover-critical-alerts/boundary.md).

Offline: the transport is a fake, every path is a temp dir, and nothing reaches Pushover or the real Conductor log.
Each `t_<promise>` is one promise on the page (boundary_check.py checks the names).
    python3 src/RimMandrake/Utils/selftest_pager.py          ALL PASS / N FAIL
"""
import datetime as dt
import json
import os
import sys
import tempfile

TMP = tempfile.mkdtemp(prefix="selftest_pager_")
# before pager is imported, so no test can touch the live pager dir, credentials or Conductor log
os.environ["RM_PAGER_DIR"] = os.path.join(TMP, "pager")
os.environ["RM_PAGER_CONDUCTOR_LOG"] = os.path.join(TMP, "conductor_log.md")
os.environ["RM_PAGER_CREDENTIALS"] = os.path.join(TMP, "secrets", "pushover.env")
for k in ("PUSHOVER_USER_KEY", "PUSHOVER_APP_TOKEN"):
    os.environ.pop(k, None)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pager as P  # noqa: E402

FAILS = []
USER = "u" * 10 + "SECRETUSERKEY0123456789"[:20]     # 30 chars
TOKEN = "a" * 8 + "SECRETAPPTOKEN0123456789abc"[:22]  # 30 chars
assert len(USER) == 30 and len(TOKEN) == 30

CONDUCTOR_ENV = {"AGENT_SEAT": "BENCH"}
CONDUCTOR_CG = "0::/user.slice/user-1000.slice/user@1000.service/claude.slice/claude-seats.slice/claude-seat-BENCH-3395224.scope/seat\n"
OPS_UNIT = "rm-role-operations-1795138643"
OPS_ENV = {"AGENT_SEAT": "BENCH", "RM_ROLE_UNIT": OPS_UNIT}
OPS_CG = ("0::/user.slice/user-1000.slice/user@1000.service/claude.slice/claude-seats.slice/claude-seat-BENCH-%s.scope"
          "/seat\n" % OPS_UNIT)
HELPER_UNIT = "rm-detached-bench-rimmandrake-design-pushover-alerts-criti-1795143674"
HELPER_ENV = {"AGENT_SEAT": "BENCH", "RM_ROLE_UNIT": HELPER_UNIT}
HELPER_CG = ("0::/user.slice/user-1000.slice/user@1000.service/claude.slice/claude-seats.slice/claude-seat-BENCH-%s.scope"
             "/claude-code-bash\n" % HELPER_UNIT)
T0 = dt.datetime(2026, 11, 20, 3, 0, 0, tzinfo=dt.timezone.utc)
WHY = "disk whea severe reading above zero means a fatal error"


def check(ok, what):
    if not ok:
        FAILS.append(what)
        print("FAIL:", what)


class Fake:
    """A Pushover stand-in: records every call; answers with the queued (status, body, err) or a receipt."""

    def __init__(self, *answers):
        self.calls, self.answers = [], list(answers)

    def __call__(self, url, fields=None, timeout=None):
        self.calls.append((url, dict(fields or {})))
        if self.answers:
            return self.answers.pop(0)
        return 200, json.dumps({"status": 1, "request": "r1", "receipt": "R%03d" % len(self.calls)}), None


def fresh(creds=True):
    """A clean pager dir, Conductor log and credentials file."""
    import shutil
    shutil.rmtree(os.environ["RM_PAGER_DIR"], ignore_errors=True)
    for p in (os.environ["RM_PAGER_CONDUCTOR_LOG"], os.environ["RM_PAGER_CREDENTIALS"]):
        if os.path.exists(p):
            os.remove(p)
    if creds:
        os.makedirs(os.path.dirname(os.environ["RM_PAGER_CREDENTIALS"]), exist_ok=True)
        with open(os.environ["RM_PAGER_CREDENTIALS"], "w") as f:
            f.write("PUSHOVER_USER_KEY=%s\nPUSHOVER_APP_TOKEN=%s\n" % (USER, TOKEN))


def log_lines():
    p = os.path.join(os.environ["RM_PAGER_DIR"], "log.jsonl")
    return [json.loads(x) for x in open(p)] if os.path.exists(p) else []


def clog():
    p = os.environ["RM_PAGER_CONDUCTOR_LOG"]
    return open(p).read() if os.path.exists(p) else ""


def hw(fake, t=T0, cause="disk.whea_severe_24h", reading="whea_severe_24h = 2 (line 0)", env=None, cg=None, **kw):
    return P.send("HARDWARE_FAILURE", cause, reading, WHY, env=env or CONDUCTOR_ENV, cgroup=cg or CONDUCTOR_CG,
                  post=fake, t=t, **kw)


# ---------------------------------------------------------------- promises

def t_only_two_senders():
    check(P.caller(CONDUCTOR_ENV, CONDUCTOR_CG)[0] == "conductor", "the Conductor window is the conductor")
    check(P.caller(OPS_ENV, OPS_CG)[0] == "operations", "an Operations role run in its scope is operations")
    svc = "0::/user.slice/user-1000.slice/user@1000.service/app.slice/%s.service\n" % OPS_UNIT
    check(P.caller(OPS_ENV, svc)[0] == "operations", "an Operations pre-launch step in its service is operations")
    check(P.caller(HELPER_ENV, HELPER_CG)[0] is None, "a detached helper is refused")
    who, why = P.caller({"AGENT_SEAT": "BENCH"}, HELPER_CG)
    check(who is None and "inside a launched unit" in why and HELPER_UNIT in why,
          "a helper that unset RM_ROLE_UNIT is still refused by its cgroup, and told so: %s" % why)
    check(P.caller(OPS_ENV, HELPER_CG)[0] is None, "a helper that claims the Operations unit name is refused by its cgroup")
    check(P.caller({"AGENT_SEAT": "BENCH", "RM_ROLE_UNIT": "rm-role-producer-1795138643"},
                   "0::/x/claude-seat-BENCH-rm-role-producer-1795138643.scope/seat\n")[0] is None,
          "another role run (Producer) is refused")
    check(P.caller({"AGENT_SEAT": "BENCH", "RM_ROLE_UNIT": "rm-role-conductor-1795138643"},
                   "0::/x/claude-seat-BENCH-rm-role-conductor-1795138643.scope/seat\n")[0] is None,
          "the Conductor ROLE run (a launched run) is not the Conductor window")
    check(P.caller({"AGENT_SEAT": "LAPTOP"}, "0::/x/claude-seat-LAPTOP-123.scope/seat\n")[0] is None,
          "another seat is refused")
    check(P.caller({}, CONDUCTOR_CG)[0] is None, "an unset seat is refused")
    check(P.caller(CONDUCTOR_ENV, "0::/user.slice/user-1000.slice/session-3.scope\n")[0] is None,
          "a plain shell outside a window's scope is refused")
    orig = P._cgroup
    P._cgroup = lambda path="/proc/self/cgroup": (_ for _ in ()).throw(PermissionError("denied"))
    try:
        who, why = P.caller(CONDUCTOR_ENV)
        check(who is None and "could not be proved" in why, "an unreadable cgroup proves nothing")
    finally:
        P._cgroup = orig
    # what a refused helper sees
    fresh()
    f = Fake()
    out, rec = hw(f, env=HELPER_ENV, cg=HELPER_CG)
    line = P.verdict_line(out, rec)
    check(out == P.REFUSED and not f.calls, "a helper's send is refused before any network call")
    check(line.startswith("PAGER REFUSED") and HELPER_UNIT in line, "the helper's verdict names why: %s" % line)


def t_refusal_is_logged():
    fresh()
    f = Fake()
    hw(f, env=HELPER_ENV, cg=HELPER_CG)
    P.send("NOT_A_CLASS", "x.y", "a reading", WHY, env=CONDUCTOR_ENV, cgroup=CONDUCTOR_CG, post=f, t=T0)
    ls = log_lines()
    check(len(ls) == 2 and all(x["outcome"] == P.REFUSED for x in ls), "each refusal is one log.jsonl line")
    check(ls and ls[0]["caller"] == "refused" and "RM_ROLE_UNIT" in ls[0]["detail"], "the line names the cause")
    check(not f.calls and "PAGER" not in clog(), "a refusal sends nothing and writes no Conductor log line")


def t_closed_class_list():
    fresh()
    f = Fake()
    out, rec = P.send("DISK_LOW", "disk.d_free_gb", "d_free_gb = 150", WHY, env=CONDUCTOR_ENV, cgroup=CONDUCTOR_CG,
                      post=f, t=T0)
    check(out == P.REFUSED and "closed list" in rec["detail"], "a class not on the list is refused")
    out, _ = P.send("GOAL_SHOCK", "goal:x", "reading", WHY, goal="Cheap guards at every pipeline door", env=OPS_ENV,
                    cgroup=OPS_CG, post=f, t=T0)
    check(out == P.REFUSED, "Operations may not send GOAL_SHOCK (the Conductor's judgment)")
    out, _ = P.send("TEST", "drill:1", "reading", WHY, env=OPS_ENV, cgroup=OPS_CG, post=f, t=T0)
    check(out == P.REFUSED, "Operations may not send TEST")
    out, _ = hw(f, env=OPS_ENV, cg=OPS_CG)
    check(out == P.SENT, "Operations may send HARDWARE_FAILURE")
    bad = os.path.join(TMP, "bad_classes.json")
    for doc in ('{"classes": {}}', "{not json", '{"classes": {"X_Y": {"label": "x", "senders": ["helper"], '
                '"window_h": 1, "template": "{reading}", "means": "m", "added": {"by": "CONDUCTOR", "on": "d", "per": "p"}}}}',
                '{"classes": {"X_Y": {"label": "x", "senders": ["conductor"], "window_h": 1, "template": "{reading}", '
                '"means": "m", "added": {"by": "HELPER", "on": "d", "per": "p"}}}}'):
        with open(bad, "w") as fh:
            fh.write(doc)
        try:
            cl = P.load_classes(bad)
        except (ValueError, OSError):
            cl = None
        check(cl is None, "a malformed class list is refused: %s" % doc[:60])
    fresh()
    f = Fake()
    orig = P.CLASSES_FILE
    P.CLASSES_FILE = bad
    try:
        out, rec = hw(f)
        check(out == P.REFUSED and "could not be read" in rec["detail"] and not f.calls,
              "an unreadable class list pages nothing")
    finally:
        P.CLASSES_FILE = orig
    live = P.load_classes()
    check(set(live) == {"HARDWARE_FAILURE", "ACCOUNT_SWITCH_FAILURE", "GOAL_SHOCK", "TEST"},
          "the live list is exactly the four classes: %s" % sorted(live))


def t_fixed_template_text():
    fresh()
    f = Fake()
    for r in ("see /mnt/d/ClaudeWork/x", "mail lukas@example.com", "two\nlines", 'quote "x"', "C:\\Users", "",
              "x" * 201, "https://evil.example/a"):
        out, _ = hw(f, reading=r)
        check(out == P.REFUSED, "a reading that could carry a path, address, URL or newline is refused: %r" % r[:30])
    check(not f.calls, "none of them reached the transport")
    out, _ = hw(f, cause="Disk/WHEA")
    check(out == P.REFUSED, "a cause that is not a reading key is refused")
    out, _ = hw(f, item="lower_case_item")
    check(out == P.REFUSED, "an item that is not an item id is refused")
    out, _ = P.send("HARDWARE_FAILURE", "disk.whea_severe_24h", "whea = 1", "too short", env=CONDUCTOR_ENV,
                    cgroup=CONDUCTOR_CG, post=f, t=T0)
    check(out == P.REFUSED, "a why under four words is refused")
    out, _ = hw(f, item="OPS_WHEA_FATAL_DIAGNOSE_HW_QUIT")
    check(out == P.SENT and len(f.calls) == 1, "a clean page is sent")
    fields = f.calls[0][1]
    check(set(fields) == {"token", "user", "title", "message", "priority", "retry", "expire", "sound"},
          "only the fixed fields go to Pushover: %s" % sorted(fields))
    check(fields.get("sound") == "echo", "a real page rings with his long sound, echo: %r" % fields.get("sound"))
    f2 = FakePost() if "FakePost" in globals() else type(f)()
    out, _ = P.send("TEST", "drill:20261123t000000", "drill from the Conductor window",
                    "a drill to prove that a page reaches his phone", env=CONDUCTOR_ENV, cgroup=CONDUCTOR_CG,
                    post=f2, t=T0)
    check(out == P.SENT and "sound" not in f2.calls[0][1],
          "a TEST page keeps the brief default sound: %s" % (sorted(f2.calls[0][1]) if f2.calls else out))
    check(fields["message"] == "Hardware failure: whea_severe_24h = 2 (line 0) Item OPS_WHEA_FATAL_DIAGNOSE_HW_QUIT.",
          "the message is the template filled with the reading and item: %r" % fields["message"])
    check(fields["title"] == "RimMandrake CRITICAL: Hardware failure", "the title is fixed: %r" % fields["title"])
    check(WHY not in json.dumps(fields), "the why is logged, never sent")


def t_emergency_priority():
    fresh()
    f = Fake()
    hw(f)
    fl = f.calls[0][1]
    check(fl["priority"] == 2 and fl["retry"] == 120 and fl["expire"] == 3600,
          "emergency priority 2, retry 120 s, expire 3600 s: %s" % {k: fl[k] for k in ("priority", "retry", "expire")})
    check(30 <= P.RETRY_S and P.EXPIRE_S <= 10800 and P.EXPIRE_S // P.RETRY_S <= 50,
          "inside Pushover's bounds (retry >= 30, expire <= 10800, at most 50 retries)")
    check(f.calls[0][0] == "https://api.pushover.net/1/messages.json", "the messages endpoint")


def t_goal_must_be_stated():
    fresh()
    f = Fake()
    goals = os.path.join(TMP, "goals.md")
    with open(goals, "w") as fh:
        fh.write("# GOALS\n\nintro\n\n---\n\n## From today (block 2, on top)\n\n1. **Cheap guards at every pipeline door**:"
                 " x\n2. **No sleeper tickets**: y\n\n---\n\n## Older (block 1)\n\n1. **Relentless workers**: z\n")
    kw = dict(env=CONDUCTOR_ENV, cgroup=CONDUCTOR_CG, post=f, t=T0, goals_path=goals)
    out, rec = P.send("GOAL_SHOCK", "goal:guards", "guards cannot land: 3 of 3 doors broken", WHY,
                      goal="Some goal nobody stated", **kw)
    check(out == P.REFUSED and "top block" in rec["detail"], "a goal not stated is refused")
    out, _ = P.send("GOAL_SHOCK", "goal:relentless", "x = 1", WHY, goal="Relentless workers", **kw)
    check(out == P.REFUSED, "a goal from an older block is refused (only the newest block is current)")
    out, _ = P.send("GOAL_SHOCK", "goal:guards", "guards cannot land: 3 of 3 doors broken", WHY,
                    goal="Cheap guards at every pipeline door", **kw)
    check(out == P.SENT and f.calls[-1][1]["message"].startswith("Goal failed: Cheap guards at every pipeline door."),
          "a stated goal pages, its title in the text")
    out, _ = hw(f, goal="Cheap guards at every pipeline door")
    check(out == P.REFUSED, "--goal on another class is refused")
    kw["goals_path"] = os.path.join(TMP, "no_such_goals.md")
    out, rec = P.send("GOAL_SHOCK", "goal:guards2", "x = 1", WHY, goal="Cheap guards at every pipeline door", **kw)
    check(out == P.REFUSED and "could not be read" in rec["detail"], "an unreadable goals file refuses a goal page")
    check(P.goal_titles() != [], "the live CONDUCTOR_GOALS.md top block lists goals: %s" % P.goal_titles())


def t_one_fault_pages_once():
    fresh()
    f = Fake()
    out1, _ = hw(f)
    out2, rec2 = hw(f, t=T0 + dt.timedelta(hours=3), reading="whea_severe_24h = 5 (line 0)")
    check(out1 == P.SENT and out2 == P.REPEAT and len(f.calls) == 1, "a repeat inside 24 h does not ring: %s %s" % (out1, out2))
    st = P.read_state()["open"]["HARDWARE_FAILURE:disk.whea_severe_24h"]
    check(st["repeats"] == 1 and st["last_reading"] == "whea_severe_24h = 5 (line 0)",
          "the repeat updates the record: %s" % st)
    out3, _ = hw(f, cause="disk.d_free_gb", reading="d_free_gb = 40", t=T0 + dt.timedelta(hours=3))
    check(out3 == P.SENT and len(f.calls) == 2, "another cause is another fault: it rings")
    out4, _ = hw(f, t=T0 + dt.timedelta(hours=24, seconds=1))
    check(out4 == P.SENT and len(f.calls) == 3, "after the window the same fault rings again")
    out5, _ = P.send("ACCOUNT_SWITCH_FAILURE", "disk.whea_severe_24h", "x = 1", WHY, env=CONDUCTOR_ENV,
                     cgroup=CONDUCTOR_CG, post=f, t=T0 + dt.timedelta(hours=25))
    check(out5 == P.SENT, "the key is class plus cause: the same cause in another class is another fault")
    a, _ = P.send("TEST", "drill:a", "drill one", WHY, env=CONDUCTOR_ENV, cgroup=CONDUCTOR_CG, post=f, t=T0)
    b, _ = P.send("TEST", "drill:a", "drill one", WHY, env=CONDUCTOR_ENV, cgroup=CONDUCTOR_CG, post=f, t=T0)
    check(a == b == P.SENT, "a TEST page (window 0) never dedupes")


def t_failed_send_stays_pending():
    fresh()
    f = Fake((None, "", "URLError: <urlopen error [Errno -3] Temporary failure in name resolution>"),
             (None, "", "TimeoutError: timed out"))
    o1, _ = hw(f)
    o2, _ = hw(f, t=T0 + dt.timedelta(minutes=5))
    o3, r3 = hw(f, t=T0 + dt.timedelta(minutes=10))
    check((o1, o2, o3) == (P.COULD_NOT_SEND, P.COULD_NOT_SEND, P.SENT) and len(f.calls) == 3,
          "a failed page is retried by the next call, never marked sent: %s" % ((o1, o2, o3),))
    s = P.read_state()
    check(not s["failing"] and "HARDWARE_FAILURE:disk.whea_severe_24h" in s["open"], "the success clears the streak")


def t_four_outcomes_apart():
    check(len(set(P.EXIT.values())) == 5 and P.EXIT[P.SENT] == 0, "five outcomes, five exit codes, 0 only for SENT")
    cases = [
        ((200, json.dumps({"status": 1, "receipt": "Rabc"}), None), P.SENT, "sent"),
        ((200, json.dumps({"status": 1, "request": "r"}), None), P.COULD_NOT_SEND, "without status 1 and a receipt"),
        ((400, json.dumps({"status": 0, "errors": ["application token is invalid"]}), "HTTP 400"), P.COULD_NOT_SEND,
         "application token is invalid"),
        ((429, "", "HTTP 429"), P.COULD_NOT_SEND, "HTTP 429"),
        ((500, "<html>", "HTTP 500"), P.COULD_NOT_SEND, "HTTP 500"),
        ((None, "", "URLError: no route"), P.COULD_NOT_SEND, "unreachable"),
    ]
    for ans, want, word in cases:
        fresh()
        out, rec = hw(Fake(ans))
        check(out == want and word in rec["detail"], "answer %s -> %s naming %r (got %s: %s)" % (
            ans[0], want, word, out, rec["detail"]))
    fresh(creds=False)
    f = Fake()
    out, rec = hw(f)
    check(out == P.COULD_NOT_SEND and not f.calls and "PUSHOVER_USER_KEY" in rec["detail"]
          and "pushover.env" in rec["detail"], "no credentials: could not send, naming the variable and file")
    fresh()
    f = Fake()
    out, rec = hw(f, dry_run=True)
    check(out == P.DRY_RUN and not f.calls and not os.path.exists(os.path.join(os.environ["RM_PAGER_DIR"], "state.json")),
          "a dry run calls nothing and changes no state")
    check("would page" in rec["detail"] and "credentials present" in rec["detail"], "the dry run says what it would send")
    fresh(creds=False)
    out, rec = hw(Fake(), dry_run=True)
    check(out == P.DRY_RUN and "PUSHOVER_USER_KEY" in rec["detail"], "a dry run without credentials says they are missing")
    fresh()
    hw(Fake())
    out, rec = hw(Fake(), dry_run=True, t=T0 + dt.timedelta(hours=1))
    check(out == P.DRY_RUN and "REPEAT" in rec["detail"], "a dry run of a repeat says it would not ring")


def t_could_not_send_is_visible():
    fresh()
    f = Fake((None, "", "URLError: down"), (None, "", "URLError: down"))
    hw(f)
    hw(f, t=T0 + dt.timedelta(minutes=5))
    c = clog()
    check(c.count("COULD NOT SEND") == 1 and "did not reach his phone" in c,
          "one Conductor log line when a failing streak starts, not one per attempt")
    s = P.read_state()["failing"]["HARDWARE_FAILURE:disk.whea_severe_24h"]
    check(s["attempts"] == 2 and s["since"] == P.iso(T0), "the streak counts attempts from its start: %s" % s)
    check([x["outcome"] for x in log_lines()] == [P.COULD_NOT_SEND] * 2, "log.jsonl holds every attempt")
    hw(f, t=T0 + dt.timedelta(minutes=10))
    check("after 2 failed attempt(s)" in clog(), "the page that finally leaves says how many failed first")
    rc, lines = P.status_lines()
    check(rc == 0 and any("open faults" in x for x in lines), "status reads the state")
    fresh()
    f = Fake((None, "", "URLError: down"))
    hw(f)
    import ops_watch_pager
    pts = ops_watch_pager.points(os.environ["RM_PAGER_DIR"], T0 + dt.timedelta(minutes=1))
    check(pts["pager.could_not_send"]["v"] == 1 and pts["pager.could_not_send"]["m"] == "MEASURED",
          "the ops digest point reads the failing streak: %s" % pts["pager.could_not_send"])
    fresh()
    pts = ops_watch_pager.points(os.environ["RM_PAGER_DIR"], T0)
    check(pts["pager.could_not_send"]["v"] == 0 and pts["pager.could_not_send"]["m"] == "MEASURED",
          "no state yet is a measured 0 failing (nothing was ever attempted)")
    os.makedirs(os.environ["RM_PAGER_DIR"], exist_ok=True)
    with open(os.path.join(os.environ["RM_PAGER_DIR"], "state.json"), "w") as fh:
        fh.write("{torn")
    pts = ops_watch_pager.points(os.environ["RM_PAGER_DIR"], T0)
    check(pts["pager.could_not_send"]["m"] == "UNMEASURED", "a torn state is UNMEASURED, never 0")


def t_secrets_never_printed():
    fresh()
    outs = []
    for ans in ((200, json.dumps({"status": 1, "receipt": "Rok"}), None), (None, "", "URLError: down"),
                (400, json.dumps({"status": 0, "errors": ["user key is invalid"]}), "HTTP 400")):
        out, rec = hw(Fake(ans), cause="disk.c%d" % len(outs))
        outs.append(P.verdict_line(out, rec))
    out, rec = hw(Fake(), dry_run=True, cause="disk.dry")
    outs.append(P.verdict_line(out, rec))
    outs.append(P.check_credentials(post=Fake((200, json.dumps({"status": 1, "devices": ["iphone"]}), None)))[1])
    blob = "\n".join(outs) + clog() + json.dumps(log_lines()) + open(
        os.path.join(os.environ["RM_PAGER_DIR"], "state.json")).read()
    check(USER not in blob and TOKEN not in blob, "neither credential appears in a verdict, log, state or Conductor line")
    fresh(creds=False)
    os.makedirs(os.path.dirname(os.environ["RM_PAGER_CREDENTIALS"]), exist_ok=True)
    with open(os.environ["RM_PAGER_CREDENTIALS"], "w") as fh:
        fh.write("PUSHOVER_USER_KEY=short%s\nPUSHOVER_APP_TOKEN=%s\n" % (USER[:5], TOKEN))
    creds, why = P.read_credentials(env={})
    check(creds is None and "PUSHOVER_USER_KEY" in why and USER[:5] not in why and TOKEN not in why,
          "a misshapen value is named by variable, its value never printed: %s" % why)
    creds, why = P.read_credentials(env={"PUSHOVER_USER_KEY": USER, "PUSHOVER_APP_TOKEN": TOKEN})
    check(creds == {"user": USER, "token": TOKEN}, "the environment is read first")


def t_torn_state_not_read_as_empty():
    fresh()
    os.makedirs(os.environ["RM_PAGER_DIR"], exist_ok=True)
    sp = os.path.join(os.environ["RM_PAGER_DIR"], "state.json")
    with open(sp, "w") as fh:
        fh.write('{"open": {"HARDWARE_FAILURE:x": {}}, "fail')
    try:
        P.read_state()
        raised = False
    except ValueError:
        raised = True
    check(raised, "read_state raises on a torn file, never returns an empty state")
    for doc in ("[]", '{"open": [], "failing": {}}', '{"open": {}}'):
        with open(sp, "w") as fh:
            fh.write(doc)
        try:
            P.read_state()
            raised = False
        except ValueError:
            raised = True
        check(raised, "read_state raises on a wrong-shaped state %s, never returns an empty one" % doc)
    with open(sp, "w") as fh:
        fh.write('{"open": {"HARDWARE_FAILURE:x": {}}, "fail')
    rc, _ = P.status_lines()
    check(rc == 3, "status says UNREADABLE on a torn state")
    f = Fake()
    out, rec = hw(f)
    check(out == P.SENT and rec.get("state_aside") and os.path.exists(rec["state_aside"]),
          "a critical page still leaves, and the torn file is kept aside: %s" % rec.get("state_aside"))


def t_page_survives_a_bad_pager_dir():
    fresh()
    good = os.environ["RM_PAGER_DIR"]
    os.environ["RM_PAGER_DIR"] = "/dev/null/pager"     # cannot be created: no lock, no state, no log
    try:
        f = Fake()
        out, rec = hw(f)
        check(out == P.SENT and len(f.calls) == 1 and rec.get("lock_error") and rec.get("state_error"),
              "a pager dir that cannot be written still sends the page and says so: %s" % {
                  k: rec.get(k) for k in ("lock_error", "state_error")})
        check("SENT" in clog(), "the Conductor log still gets the SENT line")
    finally:
        os.environ["RM_PAGER_DIR"] = good
    orig = P.send
    P.send = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom"))
    try:
        import contextlib
        import io
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = P.main(["send", "--class", "TEST", "--cause", "x", "--reading", "y", "--why", "a b c d"])
        check(rc == 5 and buf.getvalue().startswith("PAGER ERROR RuntimeError"),
              "a crash claims no outcome: exit 5, PAGER ERROR (%s)" % buf.getvalue().strip())
    finally:
        P.send = orig


def t_check_credentials_rings_nothing():
    fresh()
    f = Fake((200, json.dumps({"status": 1, "devices": ["iphone182"]}), None))
    rc, line = P.check_credentials(post=f)
    check(rc == 0 and "iphone182" in line and f.calls[0][0].endswith("/users/validate.json"),
          "validate only, never messages: %s" % line)
    rc, _ = P.check_credentials(post=Fake((400, json.dumps({"status": 0, "errors": ["user key is invalid"]}), "x")))
    check(rc == 1, "Pushover's no is INVALID (1)")
    rc, _ = P.check_credentials(post=Fake((None, "", "URLError: down")))
    check(rc == 3, "unreachable is COULD NOT LOOK (3)")
    fresh(creds=False)
    rc, line = P.check_credentials(post=Fake())
    check(rc == 3 and "pushover.env" in line, "missing credentials is COULD NOT LOOK, naming the file")


def main():
    for t in (t_only_two_senders, t_refusal_is_logged, t_closed_class_list, t_fixed_template_text,
              t_emergency_priority, t_goal_must_be_stated, t_one_fault_pages_once, t_failed_send_stays_pending,
              t_four_outcomes_apart, t_could_not_send_is_visible, t_secrets_never_printed,
              t_torn_state_not_read_as_empty, t_page_survives_a_bad_pager_dir, t_check_credentials_rings_nothing):
        try:
            t()
        except Exception as e:  # noqa: BLE001
            check(False, "%s raised %s: %s" % (t.__name__, type(e).__name__, e))
    print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
