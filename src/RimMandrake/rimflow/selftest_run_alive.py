#!/usr/bin/env python3
"""Selftest of run_alive.py (RIMMANDRAKE_TIE_LIFE_SIGN_TO_PROCESS_484_HAND_NOTES). Each promise of
design/specs/2026-11-23-run-alive/boundary.md has a test of its name (t_, and underscores for dashes). Offline: a temp state, a
temp clone, a fake systemd and /proc; the lease is renewed by the real modledger.py in the temp clone.

    python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/rimflow/selftest_run_alive.py
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
TMP = tempfile.mkdtemp(prefix="selftest_run_alive_")
STATE = os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "state")
os.environ["RM_CONDUCTOR_LOG"] = os.path.join(TMP, "conductor.md")
os.environ["RM_UNDER_SELFTEST"] = "1"
for _k in ("RM_MODLEDGER_WRITER", "RM_MODLEDGER_TOKEN", "RM_MODLEDGER_ROOT"):
    os.environ.pop(_k, None)
sys.path.insert(0, HERE)
import detached_helper as DH  # noqa: E402
import modledger as ML  # noqa: E402
import run_alive as RA  # noqa: E402

RESULTS = []
NOW = time.time()
PROJ = os.path.join(TMP, "projects")
MOD = "ExplosiveKnockback"


def check(what, ok, detail=""):
    RESULTS.append(bool(ok))
    print("%s  %s%s" % ("PASS" if ok else "FAIL", what, "" if ok else "  -- %s" % str(detail)[:400]))


def git(clone, *a):
    r = subprocess.run(["git", "-C", clone, "-c", "user.name=t", "-c", "user.email=t@example.invalid"] + list(a),
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return r.stdout


def new_clone(name, lease="run-A"):
    """A git tree whose src is this repo's, holding MOD's ledger with `lease` granted; origin/main stands at its commit."""
    c = os.path.join(TMP, name)
    os.makedirs(os.path.join(c, "design", "concepts", MOD))
    os.symlink(os.path.join(REPO, "src"), os.path.join(c, "src"))
    git(TMP, "init", "-q", "-b", "main", c)
    ML.append(c, MOD, "DISPATCH", "version.open", "version", body={"version": "0.1.0"}, version="0.1.0")
    tok = ML.grant(c, MOD, lease)
    to_origin(c, "the grant")
    return c, tok


def to_origin(c, subject):
    git(c, "add", "design")
    git(c, "commit", "-q", "-m", subject)
    git(c, "update-ref", "refs/remotes/origin/main", "HEAD")


def renewals(c, lease="run-A"):
    return [e for e in ML.read(c, MOD) if e.get("kind") == "lease.renew" and e["writer"] == "HOLDER." + lease]


N = [0]


def new_rec(clone, tok=None, mod=MOD, lease="run-A", at=None):
    N[0] += 1
    env = {"RM_MODLEDGER_WRITER": "HOLDER." + lease, "RM_MODLEDGER_TOKEN": str(tok)} if tok else {}
    if mod and tok:
        env["RM_CONTROL_MOD"] = mod
    rec = {"unit": "rm-detached-t-%d" % N[0], "seat": "BENCH", "item": "ITEM_%d" % N[0], "clone": clone, "model": "opus",
           "at": at or NOW - 20000, "state": STATE, "status": "running", "env": env,
           "out": os.path.join(TMP, "o%d" % N[0]), "err": os.path.join(TMP, "e%d" % N[0])}
    DH.write_record(rec)
    return rec


def say(clone, text="reading the log", age=30, name="11111111-aaaa", first="2026-11-23T01:00:00Z", raw=None):
    """The clone's transcript, its last growth `age` seconds ago."""
    d = DH.project_dir(clone, PROJ)
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, name + ".jsonl")
    rows = [{"type": "user", "timestamp": first, "message": {"content": "go"}}]
    if text:
        rows.append({"type": "assistant", "timestamp": first, "message": {"content": [{"type": "text", "text": text}]}})
    rows.append({"type": "user", "message": {"content": [{"type": "tool_result", "content": "ok"}]}})
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(raw if raw is not None else "".join(json.dumps(r) + "\n" for r in rows))
    os.utime(p, (NOW - age, NOW - age))
    return p


class Systemd:
    """A fake systemctl; git and the ledger run for real. procs: the pids a run's scope holds."""
    def __init__(self, state="active", procs=("claude",), blind=None, git_blind=False):
        self.state, self.procs, self.blind, self.git_blind, self.calls = state, procs, blind, git_blind, []

    def __call__(self, argv, **kw):
        self.calls.append(argv)
        if argv[0] != "systemctl":
            if self.git_blind and argv[0] == "git":
                return subprocess.CompletedProcess(argv, 128, "", "fatal: no git here")
            return subprocess.run(argv, **kw)
        if "ActiveState" in argv:
            if self.blind == "unit":
                return subprocess.CompletedProcess(argv, 1, "", "Failed to connect to bus")
            return subprocess.CompletedProcess(argv, 0, self.state + "\n", "")
        if "ControlGroup" in argv:
            if self.blind == "process":
                return subprocess.CompletedProcess(argv, 1, "", "Failed to connect to bus")
            return subprocess.CompletedProcess(argv, 0, "/scope\n" if argv[-1].endswith(".scope") else "", "")
        return subprocess.CompletedProcess(argv, 1, "", "")


TABLE = {"claude": {"argv": ["/home/x/.local/bin/claude", "-p"], "ppid": 1},
         "shell": {"argv": ["/bin/bash", "-c", "source /home/x/.claude/shell-snapshots/s.sh && ./game loading"], "ppid": 0},
         "mcp": {"argv": ["node", "server.js"], "ppid": 0},
         "zombie": {"argv": [], "ppid": 1},
         "orphan": {"argv": ["/bin/bash", "-c", "source /home/x/.claude/shell-snapshots/s.sh && nohup x"], "ppid": 1}}


def look(rec, sd=None, now=NOW, appender=None, **k):
    """RA.look with the fake /proc of `sd`."""
    sd = sd or Systemd()
    ids = {n: i for i, n in enumerate(sd.procs, 100)}
    table = {i: dict(TABLE[n], ppid=ids.get("claude", 1) if n in ("shell", "mcp") else TABLE[n]["ppid"])
             for n, i in ids.items()}
    keep = RA.cgroup_pids, RA.read_proc
    if sd.blind != "process":
        RA.cgroup_pids = lambda u, *a, **kw: list(table) if u.endswith(".scope") else []
        RA.read_proc = lambda p, **kw: table[p]
    try:
        return RA.look(rec, now, None, sd, PROJ, appender or (lambda r: RA.clone_append(r, sd, r["clone"])), **k)
    finally:
        RA.cgroup_pids, RA.read_proc = keep


def t_a_live_run_keeps_its_lease():
    c, tok = new_clone("live")
    say(c)
    rec = new_rec(c, tok)
    got = look(rec)
    check("a live run is renewed, with its own writer and token", got["renewal"] == "renewed" and len(renewals(c)) == 1 and
          renewals(c)[0]["token"] == tok, got)
    got = look(rec, now=NOW + 300)
    check("5 min later it is not due: wait, nothing appended", got["act"] == "wait" and len(renewals(c)) == 1, got)
    say(c, age=-1300)
    time.sleep(1.1)     # modledger keys a renewal by its second
    got = look(rec, now=NOW + 1300)
    check("the next beat renews again", got["renewal"] == "renewed" and len(renewals(c)) == 2, got)
    c2, tok2 = new_clone("nomod")
    say(c2)
    got = look(new_rec(c2, tok2, mod=None))
    check("a lease run whose env names no mod: the mod is the one that granted the lease", got["renewal"] == "renewed" and
          len(renewals(c2)) == 1, got)


def t_a_long_wait_is_not_hung():
    c, tok = new_clone("wait")
    say(c, age=9000)
    got = look(new_rec(c, tok), Systemd(procs=("claude", "shell")))
    check("silent 9000 s, its command runs: renewed", got["act"] == "renew" and got["renewal"] == "renewed" and
          "long wait" in got["why"], got)
    c, tok = new_clone("sub")
    p = say(c, age=9000)
    os.makedirs(p[:-6] + "/subagents")
    with open(p[:-6] + "/subagents/agent-1.jsonl", "w") as fh:
        fh.write("{}\n")
    os.utime(p[:-6] + "/subagents/agent-1.jsonl", (NOW - 20, NOW - 20))
    got = look(new_rec(c, tok))
    check("a subagent's transcript that grows is a sign of life", got["act"] == "renew", got)


def t_a_dead_run_loses_its_lease():
    c, tok = new_clone("dead")
    say(c)
    for name, sd in (("the unit is gone", Systemd(state="inactive")), ("the unit is not found", Systemd(state="not-found")),
                     ("the unit is up and claude is gone", Systemd(procs=())),
                     ("claude is a zombie", Systemd(procs=("zombie",)))):
        got = look(new_rec(c, tok), sd)
        check("%s: not renewed, reads gone" % name, got["act"] == "lapse" and "gone" in got["why"] and "hung" not in got["why"]
              and not renewals(c) and got["renewal"].startswith("not renewed"), got)
    got = look(new_rec(c, tok, at=NOW - 40), Systemd(procs=()))
    check("a run 40 s old with no claude yet is blind, not gone", got["act"] == "blind", got)
    old = ML.append
    got = {}
    try:        # the lapse itself: 46 minutes with no event, the ledger refuses the append
        ML.append(c, MOD, "HOLDER.run-A", "lease.renew", "lease", token=tok,
                  now=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() + 46 * 60)))
    except ML.ModLedgerError as e:
        got = str(e)
    check("a lease nobody renews lapses", "lapsed" in str(got) and old is ML.append, got)


def t_a_hung_run_loses_its_lease():
    c, tok = new_clone("hung")
    say(c, age=9000)
    for name, procs in (("nothing running", ("claude",)), ("only an MCP server", ("claude", "mcp")),
                        ("only a detached orphan", ("claude", "orphan"))):
        got = look(new_rec(c, tok), Systemd(procs=procs))
        check("silent 9000 s, %s: not renewed, reads hung" % name, got["act"] == "lapse" and "hung" in got["why"] and
              not renewals(c), got)


def t_a_blind_beat_changes_nothing():
    c, tok = new_clone("blind")
    p = say(c)
    rec = new_rec(c, tok)
    first = look(rec)
    later = NOW + 5000
    for fact in ("unit", "process"):
        got = look(rec, Systemd(blind=fact), now=later)
        check("%s unreadable: blind, named, nothing appended, the line and the beat kept" % fact, got["act"] == "blind" and
              fact in got["blind"] and "could not look" in got["why"] and len(renewals(c)) == 1 and
              got["line"] == first["line"] and got["beat_at"] == first["beat_at"], got)
    os.remove(p)
    got = look(rec, now=later)
    check("no transcript: blind", got["act"] == "blind" and "transcript" in got["blind"] and len(renewals(c)) == 1, got)

    def broken(pid, **kw):
        raise RA.CouldNotLook("process 7: permission denied")
    keep = RA.read_proc, RA.cgroup_pids
    RA.read_proc, RA.cgroup_pids = broken, lambda *a, **kw: [7]
    try:
        say(c)
        got = RA.look(rec, later, None, Systemd(), PROJ)
    finally:
        RA.read_proc, RA.cgroup_pids = keep
    check("a process that cannot be read: blind", got["act"] == "blind" and "permission denied" in got["why"], got)


def t_a_refused_renewal_reads_refused():
    c, tok = new_clone("fence")
    say(c)
    rec = new_rec(c, tok)
    ML.grant(c, MOD, "run-B")
    to_origin(c, "a rival")
    got = look(rec)
    check("fenced in the clone: refused, nothing appended", got["renewal"].startswith("refused: stale token") and
          "run-B" in got["renewal"] and not renewals(c), got)
    check("a refused renewal is due again at the next look", look(rec, now=NOW + 300)["act"] == "renew")
    c, tok = new_clone("fence_origin")
    say(c)
    git(c, "checkout", "-q", "-b", "peer")
    ML.grant(c, MOD, "run-B")
    to_origin(c, "a rival landed by a peer")
    git(c, "checkout", "-q", "main")
    check("the fixture: the clone does not hold the rival's grant", "run-B" not in ML.leases(ML.read(c, MOD))[0])
    got = look(new_rec(c, tok))
    check("fenced on origin/main only: refused", got["renewal"].startswith("refused") and "run-B" in got["renewal"] and
          not renewals(c), got)
    c, tok = new_clone("wrong")
    say(c)
    got = look(new_rec(c, 99))
    check("a wrong token: refused", got["renewal"].startswith("refused") and not renewals(c), got)
    got = look(new_rec(c, tok), Systemd(git_blind=True))
    check("origin's leases unreadable: refused with that cause", got["renewal"].startswith("refused: could not read origin's"),
          got)
    calls = []
    got = look(new_rec(c), appender=lambda r: lambda *a: calls.append(a))
    check("a run with no lease calls no append", got["renewal"] == "no lease" and not calls, got)
    rec = new_rec(c)
    rec["env"] = {"RM_MODLEDGER_WRITER": "JUDGE.judge-1", "RM_MODLEDGER_TOKEN": "1", "RM_CONTROL_MOD": MOD}
    check("a judge holds no lease", RA.renew(rec, lambda *a: calls.append(a)) == "no lease" and not calls)

    class NoTool(Systemd):
        def __call__(self, argv, **kw):
            if len(argv) > 1 and argv[1].endswith("modledger.py"):
                return subprocess.CompletedProcess(argv, 1, "", "lapsed: idle since 1")
            return Systemd.__call__(self, argv, **kw)
    got = look(new_rec(c, tok), NoTool())
    check("a failed append reads refused with its words", got["renewal"] == "refused: lapsed: idle since 1", got)


def t_the_alive_line_is_the_runs_own():
    c, tok = new_clone("line")
    rec = new_rec(c, tok)
    say(c, "I used $21.6 of the $30 budget. Reading the log.\nNow the lock.")
    with open(os.path.join(c, "design", "x"), "w") as fh:
        fh.write("x")
    git(c, "add", "design/x")
    git(c, "commit", "-q", "-m", "%s: fix the lock" % rec["item"])
    git(c, "commit", "-q", "--allow-empty", "-m", "ledger: %s claim" % rec["item"])
    git(c, "commit", "-q", "--allow-empty", "-m", "another item's work")
    ln = look(rec)["line"]
    check("the last message, less its spend sentence, and the item's commit", ln.startswith("ALIVE:") and
          "Reading the log." in ln and "$" not in ln and "budget" not in ln and "fix the lock" in ln and
          "another item" not in ln and "claim" not in ln and "\n" not in ln, ln)
    check("only spend words: said", "held only words" in RA.line("u", "I spent $4.", [], NOW))
    check("a commit subject that states spend keeps its sha only", "abc1234" in RA.line("u", "x", ["abc1234 cap at $40"], NOW)
          and "$" not in RA.line("u", "x", ["abc1234 cap at $40"], NOW))
    check("no commits (looked) and commits unread differ", "none (looked)" in RA.line("u", "x", [], NOW) and
          "its commits: could not look" in RA.line("u", "x", None, NOW))
    big = say(c, name="22222222-bbbb", raw=json.dumps({"type": "assistant", "message": {"content": [
        {"type": "text", "text": "the early words"}]}}) + "\n" + json.dumps({"type": "user", "pad": "x" * (RA.TAIL + 10)}) + "\n")
    check("a message older than the last MB is found", RA.last_message(big) == "the early words")
    check("a transcript with no message reads empty, not unreadable", RA.last_message(say(c, "", name="33333333-cccc")) == "")
    try:
        RA.last_message(os.path.join(TMP, "gone.jsonl"))
        ok = False
    except RA.CouldNotLook:
        ok = True
    check("an unreadable transcript could not be looked at", ok)
    c2, _ = new_clone("two")
    own = say(c2, "mine", age=50, name="44444444-dddd", first="2026-11-23T01:00:00Z")
    nested = say(c2, "a nested helper's", age=5, name="55555555-eeee", first="2026-11-23T02:00:00Z")
    rec2 = new_rec(c2)
    check("the first transcript begun is the run's; a nested claude's is not", RA.transcript(rec2, PROJ) == own)
    check("a resumed run's transcript is the session it resumes", RA.transcript(dict(
        rec2, resume_session="55555555-eeee"), PROJ) == nested)


def t_one_file_beside_the_record():
    c, tok = new_clone("file")
    say(c)
    rec = new_rec(c, tok)
    before = sorted(r["unit"] for r in DH.all_records())
    got = look(rec)
    with open(RA.alive_path(rec["unit"]), encoding="utf-8") as fh:
        check("the look is on file beside the record", json.load(fh) == got)
    check("no reader of run records takes it for one", sorted(r["unit"] for r in DH.all_records()) == before and
          not {"unit", "status", "item"} & set(got), got.keys())
    unread = []
    list(DH.all_records(unreadable=unread.append))
    check("no reader of run records reports it unreadable (list_dispatch counted no spare room: 123 such files)",
          not unread, unread)
    import stop_resume as SR
    check("stop_resume reads the same runs", not [r for r in SR.recent_records(None, NOW) if not r.get("unit")])
    check("no half-written file is left", not [n for n in os.listdir(DH.runs_dir()) if n.endswith(".tmp")])
    n = len(os.listdir(DH.runs_dir()))
    look(new_rec(c, tok), dry=True)
    check("--dry writes nothing but the record the test made", len(os.listdir(DH.runs_dir())) == n + 1)


def t_the_status_shows_it():
    c, tok = new_clone("status")
    say(c, "counting doors")
    rec = new_rec(c, tok)
    check("no look on file: said", RA.status_text(rec["unit"]) == "sign of life: no look on file")
    look(rec)
    text = DH.status(runner=Systemd())
    check("status shows the cause, the lease and the line", "alive: its transcript grew" in text and "lease: renewed" in text and
          "counting doors" in text, text)
    with open(RA.alive_path(rec["unit"]), "w") as fh:
        fh.write("{half")
    check("a file that cannot be read: could not look", "could not look" in RA.status_text(rec["unit"]))
    check("an unreadable earlier look does not stop the next one", "could not look" in look(rec).get("earlier_look", ""))


def t_the_ledger_gets_it_once():
    c, _ = new_clone("finish")
    say(c, "measuring the third door")
    keep = DH.PROJECTS
    DH.PROJECTS = PROJ
    notes = []

    def runner(argv, **kw):
        if "note" in argv:
            notes.append(argv[argv.index("--text") + 1])
        if argv[0] == "git":
            return subprocess.run(argv, **kw)
        return subprocess.CompletedProcess(argv, 0, "PUBLISHED abcdef1", "")

    def end(rec, env):
        return DH.finish(rec["unit"], now=NOW, env=env, runner=runner, log_path=os.path.join(TMP, "log.md"),
                         item_reader=lambda *a: None, waker=lambda *a: None)
    killed = {"SERVICE_RESULT": "timeout", "EXIT_CODE": "killed", "EXIT_STATUS": "KILL"}
    try:
        rec = new_rec(c)
        end(rec, killed)
        check("a stopped run's one note holds the ALIVE: line", len(notes) == 1 and "ALIVE: " in notes[0] and
              "measuring the third door" in notes[0], notes)
        end(rec, killed)
        check("a second finish writes no second note", len(notes) == 1, notes)
        rec = new_rec(c)
        with open(rec["out"], "w") as fh:
            json.dump({"type": "result", "subtype": "success", "result": "all done", "is_error": False, "session_id": "s"}, fh)
        end(rec, {"SERVICE_RESULT": "success", "EXIT_CODE": "exited", "EXIT_STATUS": "0"})
        check("a success note holds its result and no ALIVE: line", "all done" in notes[-1] and "ALIVE:" not in notes[-1], notes)
        was = RA.run_line
        RA.run_line = lambda *a, **k: 1 / 0
        try:
            rec = new_rec(c)
            end(rec, killed)
        finally:
            RA.run_line = was
        check("a line that cannot be made never stops finish", "ALIVE: could not look (ZeroDivisionError" in notes[-1] and
              DH.read_record(rec["unit"])["status"] == "finished", notes[-1:])
    finally:
        DH.PROJECTS = keep


def t_one_run_never_stops_the_others():
    c, tok = new_clone("many")
    a, b, done = new_rec(c), new_rec(c), dict(new_rec(c), status="finished")
    seen = []

    def one(rec, *k, **kw):
        seen.append(rec["unit"])
        if rec is a:
            raise RuntimeError("surprise")
        return {"of": rec["unit"], "act": "wait", "why": "alive", "renewal": None}
    was, RA.look = RA.look, one
    try:
        rc, text = RA.beat(now=NOW, records=lambda root: [a, b, done])
    finally:
        RA.look = was
    with open(RA.reading_path()) as fh:
        got = json.load(fh)
    check("a raising look reads blind with its cause; the next run is looked at; a finished one is not", rc == 0 and
          seen == [a["unit"], b["unit"]] and "surprise" in got["blind"][a["unit"]] and got["acts"]["wait"] == 1 and
          got["looked"] == 2, (rc, text, got))


def t_a_beat_that_could_not_look_writes_no_reading():
    with open(RA.reading_path(), "w") as fh:
        fh.write('{"at": 1}')

    def bad(root):
        raise OSError("the disk is gone")
    rc, text = RA.beat(now=NOW, records=bad)
    with open(RA.reading_path()) as fh:
        check("exit 1, the cause, the old reading stands", rc == 1 and "COULD NOT LOOK" in text and "disk is gone" in text and
              fh.read() == '{"at": 1}', text)
    rc, text = RA.beat(now=NOW, records=lambda root: [])
    with open(RA.reading_path()) as fh:
        check("no live run is an answer: exit 0, looked at 0", rc == 0 and json.load(fh)["looked"] == 0, text)


def t_the_brief_asks_only_while_no_timer_lives():
    import maturation_dispatch as MD
    p = RA.reading_path()
    for name, body, live in (("absent", None, False), ("unreadable", "{", False), ("two hours old", {"at": NOW - 7200}, False),
                             ("from the future", {"at": NOW + 7200}, False), ("with no time", {"looked": 1}, False),
                             ("five minutes old", {"at": NOW - 300}, True)):
        if os.path.exists(p):
            os.remove(p)
        if body is not None:
            with open(p, "w") as fh:
                fh.write(body if isinstance(body, str) else json.dumps(body))
        check("a reading %s: the timer %s" % (name, "lives" if live else "does not live"), RA.timer_live(NOW) is live)
        c, _ = new_clone("brief_" + name.replace(" ", "_"))
        led = MD.ledger_open(c, MOD, "builder", "stage brief", stage="offline_build", now=NOW + 50,
                             fx={"land_ledger": lambda paths: "landed"})
        asks = "--kind lease.renew" in led["brief"]
        check("a reading %s: the brief %s" % (name, "asks for no renewal" if live else "asks for renewals"), asks is not live and
              "stage brief" in led["brief"] and "session.checkpoint" in led["brief"] and
              ("A program renews your lease" in led["brief"]) is live, led["brief"][-900:])
    c, _ = new_clone("hand")
    check("a holder started by hand keeps the renewal lines, timer or not", "--kind lease.renew" in ML.launch(
        c, MOD, "run-hand", "builder", stage="offline_build")["brief"])
    check("the footer keeps PROGRESS: and the closing note, and asks for nothing by the clock", "After each experiment or step" in DH.FOOTER and
          "whose text starts\n  `PROGRESS:`" in DH.FOOTER and
          "Before you stop: write your state" in DH.FOOTER and "LEFT OPEN:" in DH.FOOTER and "20 minutes" not in DH.FOOTER)


def t_it_raises_no_alarm():
    c, tok = new_clone("quiet")
    say(c, age=9000)
    sd = Systemd()
    look(new_rec(c, tok), sd)
    look(new_rec(c, tok), Systemd(state="failed"))
    bad = [a for a in sd.calls if not (a[0] == "git" and a[3] in ("log", "fetch", "show") or a[0] == "systemctl" and a[2] == "show")]
    check("a hung look stops nothing and posts nothing", not bad and not os.path.exists(os.environ["RM_CONDUCTOR_LOG"]), bad)


def main():
    tests = (t_a_live_run_keeps_its_lease, t_a_long_wait_is_not_hung, t_a_dead_run_loses_its_lease,
             t_a_hung_run_loses_its_lease, t_a_blind_beat_changes_nothing, t_a_refused_renewal_reads_refused,
             t_the_alive_line_is_the_runs_own, t_one_file_beside_the_record, t_the_status_shows_it,
             t_the_ledger_gets_it_once, t_one_run_never_stops_the_others,
             t_a_beat_that_could_not_look_writes_no_reading, t_the_brief_asks_only_while_no_timer_lives,
             t_it_raises_no_alarm)
    for fn in tests:
        try:
            fn()
        except Exception as e:  # noqa: BLE001
            import traceback
            check("%s raised %s: %s" % (fn.__name__, type(e).__name__, e), False, traceback.format_exc()[-600:])
    with open(os.path.join(REPO, "design/specs/2026-11-23-run-alive/boundary.md"), encoding="utf-8") as fh:
        text = fh.read().split("## PROMISES")[1].split("## LIMITS")[0]
    named = set(re.findall(r"^- \*\*([a-z-]+)\.\*\*", text, re.M))
    mine = {f.__name__[2:].replace("_", "-") for f in tests}
    check("each promise of the page has its test", named == mine, named ^ mine)
    import shutil
    shutil.rmtree(TMP, ignore_errors=True)
    bad = RESULTS.count(False)
    print("%s %d/%d" % ("FAIL" if bad else "PASS", len(RESULTS) - bad, len(RESULTS)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
