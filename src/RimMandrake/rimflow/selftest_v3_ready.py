#!/usr/bin/env python3
"""Selftest for v3_ready.py, the read-only GO/NO-GO checker for the RimFlow v3 trial night (2026-10-28).

Every case builds a fixture tree (schedule, dispatcher state, ops_watch status, unit file, sessions, a fake /proc)
and a fake command runner, so nothing here touches the live system. What must hold:
  R1  a healthy fixture reads GO overall, and every blocking row is GO.
  R2  a dry-run unit (ExecStart without --apply) is NO-GO for "Dispatcher live".
  R3  a stale last_ok_tick is NO-GO; an unreadable state.json is UNMEASURED (never GO).
  R4  a PAUSE file is NO-GO.
  R5  a deadman command that cannot run is UNMEASURED; one that names a dead arm is NO-GO.
  R6  doorbell: no hook in the seat's settings.local.json is NO-GO; an unwakeable:<SEAT> alarm is NO-GO;
      no armed file, no alarm and no recent ring is UNMEASURED.
  R7  a role whose instructions file is missing is NO-GO.
  R8  a role's last run over its cap is NO-GO; an errored run is NO-GO; a role never run is UNMEASURED;
      a trial run that exists only as an out file in the roles dir is weighed (role_launch.run_tokens).
  R9  a FAIL line for one of a role's selftests is NO-GO for that role only; --no-selftests is UNMEASURED.
  R10 the account HOLD file missing is NO-GO; account-plan.timer active is NO-GO.
  R11 the goals file missing is NO-GO.
  R12 runway: a stale ops_watch status is UNMEASURED; an UNMEASURED point is UNMEASURED; week left under 10 % is
      NO-GO; runway under 0.8 is WARN (not blocking).
  R13 --expect-account names an account that is not live: NO-GO.
  R14 the cutover tool not on origin/main (untracked or differing) is NO-GO.
  R15 FOUNDRY's shard last published 10 h ago is NO-GO; a git error is UNMEASURED.
  R16 overall: any blocking NO-GO -> NO-GO; else any blocking UNMEASURED -> UNMEASURED; WARN/INFO never block.
  R19 (review 2026-10-28) an unreadable or empty dispatch-clone schedule is UNMEASURED and never replaced by the repo
      copy; a fresh tick with apply=false is NO-GO; a NaN or future ops_watch timestamp is UNMEASURED; a week-left under
      10 % is NO-GO even when the runway point is missing; a claude-account failure is UNMEASURED; a systemctl
      error text is UNMEASURED, not GO; a hook that only echoes 'doorbell.py' is NO-GO; an armed pid whose window is
      not a live registered session is not GO; a mapped selftest missing on disk is UNMEASURED; importing writes no
      __pycache__.
  R17 a window whose session pid is dead (or whose start time differs) is NO-GO.
      The Conductor's tile is seat BENCH's session_name (AGENT BENCH; CONDUCTOR.md "You absorb Bench"); the role's
      window_name (AGENT CONDUCTOR) only HOLDS headless runs while live (role_launch), so its absence is INFO, never a block.
  R18 read-only: running the checker over the fixture changes no file in it.
"""
import copy
import hashlib
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import v3_ready as V  # noqa: E402

FAILS = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


NOW = 1793232000.0  # 2026-10-29T00:00:00Z
ROLES = ["Conductor", "Arbiter", "Auditor", "Operations", "Producer", "Innovator"]
GOOD_USAGE = {"input_tokens": 10, "cache_creation_input_tokens": 1000, "cache_read_input_tokens": 10000,
              "output_tokens": 1000,
              "cache_creation": {"ephemeral_1h_input_tokens": 1000, "ephemeral_5m_input_tokens": 0}}


def iso(t):
    return V.iso(t)


def wjson(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f)


def wtext(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)


def schedule(root):
    roles = []
    for n in ROLES:
        r = {"name": n, "enabled": n in ("Conductor", "Operations"),
             "instructions": "src/RimMandrake/rimflow/roles/%s.md" % n.lower(),
             "off_file": os.path.join(root, "offs", n.upper() + "_OFF"), "run_token_cap": 450000}
        if n == "Conductor":
            r["window_name"] = "AGENT CONDUCTOR"
            r["quick_token_cap"] = 450000
            del r["run_token_cap"]
        if n == "Operations":
            r["economy_token_cap"] = 550000
        roles.append(r)
    return {"seats": {"FOUNDRY": {"enabled": True, "wake": True, "session_name": "AGENT FOUNDRY",
                                  "clone": os.path.join(root, "foundry")},
                      "BENCH": {"enabled": True, "wake": False, "session_name": "AGENT BENCH",
                                "clone": os.path.join(root, "repo")}},
            "seat_restart": {"enabled": False}, "roles": roles}


class Fake:
    """Fake runner: first rule whose every token is in argv wins; unmatched -> (None, 'no rule')."""

    def __init__(self, rules):
        self.rules = list(rules)
        self.calls = []

    def __call__(self, argv, timeout=60, cwd=None):
        self.calls.append(list(argv))
        joined = " ".join(argv)
        for keys, res in self.rules:
            if all(k in joined for k in keys):
                return res(argv) if callable(res) else res
        return (None, "no rule for " + joined)

    def put(self, keys, res):
        self.rules.insert(0, (keys, res))


def selftest_files(repo):
    out = []
    for comp, files in V.SELFTESTS.items():
        for f in files:
            p = os.path.join(repo, f)
            if not os.path.exists(p):
                wtext(p, "# fixture\n")
            out.append(f)
    return out


def st_ok(argv):
    files = [a for a in argv if a.endswith(".py") and "selftest" in os.path.basename(a)]
    body = "\n".join("PASS          0.1s  %s" % f for f in files)
    return (0, body + "\n\nPASS %d/%d  FAIL 0/%d\nRESULT: GREEN\n" % (len(files), len(files), len(files)))


def build(root):
    repo = os.path.join(root, "repo")
    dispatch = os.path.join(root, "dispatch")
    S = os.path.join(root, "S")
    O = os.path.join(root, "O")
    plan = os.path.join(root, "plan")
    sessions = os.path.join(root, "sessions")
    proc = os.path.join(root, "proc")
    foundry = os.path.join(root, "foundry")
    sch = schedule(root)
    for c in (repo, dispatch):
        wjson(os.path.join(c, V.SCHEDULE_REL), sch)
    for n in ROLES:
        wtext(os.path.join(repo, "src/RimMandrake/rimflow/roles/%s.md" % n.lower()), "# role\n" + "x" * 400)
    wtext(os.path.join(repo, V.GOALS_REL), "# goals\n" + "g" * 400)
    wtext(os.path.join(repo, V.CUTOVER_REL), "# tool\n")
    wjson(os.path.join(foundry, ".claude/settings.local.json"),
          {"hooks": {"Stop": [{"hooks": [{"type": "command", "asyncRewake": True, "timeout": 86400,
                                          "command": "python3 \"${CLAUDE_PROJECT_DIR:-.}/src/RimMandrake/rimflow/doorbell.py\""}]}]}})
    wtext(os.path.join(foundry, "src/RimMandrake/rimflow/doorbell.py"), "# doorbell\n")
    unit = os.path.join(root, "rm-dispatcher.service")
    wtext(unit, "[Service]\nExecStart=/usr/bin/python3 /x/dispatcher.py tick --apply\n")
    runs = {n: {"runs": [{"at": NOW - 3600, "state": "done", "mode": "scheduled", "tokens": 200000,
                          "unit": "rm-role-%s-1" % n.lower()}]} for n in ROLES}
    runs["Operations"]["runs"][0]["mode"] = "economy"
    wjson(os.path.join(S, "state.json"), {"apply": True, "last_ok_tick": iso(NOW - 100), "alarms": {},
                                          "roles": runs, "seats": {}})
    wtext(os.path.join(S, "journal.jsonl"), "")
    # FOUNDRY armed now, pid 4242 alive with start 777
    wjson(os.path.join(S, "armed", "FOUNDRY.json"), {"pid": 4242, "armed_at": iso(NOW - 60), "session_id": "s",
                                                     "owner_pid": 5001})
    for pid, start in ((4242, "777"), (5001, "888"), (5002, "999")):
        fields = ["S"] + ["0"] * 18 + [start] + ["0"] * 5
        wtext(os.path.join(proc, str(pid), "stat"), "%d (claude) %s\n" % (pid, " ".join(fields)))
    wjson(os.path.join(sessions, "5001.json"), {"pid": 5001, "procStart": "888", "name": "AGENT FOUNDRY",
                                                "status": "busy"})
    wjson(os.path.join(sessions, "5002.json"), {"pid": 5002, "procStart": "999", "name": "AGENT BENCH",
                                                "status": "idle"})
    wtext(os.path.join(plan, "HOLD"), "HOLD: passive\n")
    pts = {"accounts.acct_a.runway": {"m": "MEASURED", "v": 1.5},
           "accounts.acct_a.week_left_pct": {"m": "MEASURED", "v": 80.0},
           "codex.runway": {"m": "MEASURED", "v": 1.2}, "codex.week_used_pct": {"m": "MEASURED", "v": 30.0}}
    wjson(os.path.join(O, "status.json"), {"t": NOW - 300, "at": iso(NOW - 300), "points": pts})
    selftest_files(repo)
    fake = Fake([
        (("run_selftests.py",), st_ok),  # first: its argv also names selftest_deadman_check.py
        (("is-active", "account-plan.timer"), (3, "inactive")),
        (("is-active",), (0, "active")),
        (("deadman_check.py", "run"), (0, "deadman: all arms alive\n")),
        (("claude-account", "status"), (0, json.dumps({"ok": True, "live": "acct_a", "accounts": [
            {"name": "acct_a", "state": "ok"}]}))),
        (("log", "-1", "--format=%ct", "FOUNDRY.jsonl"), (0, "%d\n" % int(NOW - 1800))),
        (("diff", "--numstat"), (0, "")),
        (("cat-file", "-e"), (0, "")),
        (("diff", "--quiet", "origin/main"), (0, "")),
        (("rev-parse", "HEAD"), (0, "abc\n")),
        (("rev-parse", "origin/main"), (0, "abc\n")),
    ])
    ctx = V.Ctx(repo=repo, dispatch=dispatch, S=S, O=O, unit=unit, plan_dir=plan, sessions=sessions, proc=proc,
                run=fake, now=NOW, selftests=True, expect_account=None)
    return ctx, fake


def rows_of(ctx):
    return V.collect(ctx)


def find(rows, comp, chk):
    hits = [r for r in rows if r.comp == comp and r.check == chk]
    return hits[0] if hits else None


def verdict(rows, comp, chk):
    r = find(rows, comp, chk)
    return r.verdict if r else "MISSING(%s/%s)" % (comp, chk)


def fresh():
    root = tempfile.mkdtemp(prefix="v3ready_")
    ctx, fake = build(root)
    return root, ctx, fake


def snapshot(root):
    out = {}
    for d, _, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f)
            with open(p, "rb") as fh:
                out[p] = (os.path.getmtime(p), hashlib.sha256(fh.read()).hexdigest())
    return out


roots = []
try:
    # R1 + R18
    root, ctx, fake = fresh(); roots.append(root)
    before = snapshot(root)
    rows = rows_of(ctx)
    after = snapshot(root)
    bad = [(r.comp, r.check, r.verdict, r.evidence) for r in rows if r.blocking and r.verdict != "GO"]
    check(not bad, "R1 healthy fixture: every blocking row GO (got %r)" % bad[:4])
    check(V.overall(rows) == "GO", "R1 healthy fixture overall GO (got %s)" % V.overall(rows))
    for comp in ("Dispatcher", "Deadman", "Doorbell FOUNDRY", "Window FOUNDRY", "Window CONDUCTOR",
                 "FOUNDRY ledger", "Cutover", "Goals", "Account HOLD", "Runway") + tuple(ROLES):
        check(any(r.comp == comp for r in rows), "R1 a row for %s exists" % comp)
    check(before == after, "R18 the checker wrote nothing in the fixture tree")
    check(V.render(rows).count("\n") >= len(rows), "R1 render prints one line per row")

    # R2
    root, ctx, fake = fresh(); roots.append(root)
    wtext(ctx.unit, "[Service]\nExecStart=/usr/bin/python3 /x/dispatcher.py tick\n")
    rows = rows_of(ctx)
    check(verdict(rows, "Dispatcher", "live (--apply)") == "NO-GO", "R2 dry-run unit is NO-GO")
    check(V.overall(rows) == "NO-GO", "R2 overall NO-GO")

    # R3
    root, ctx, fake = fresh(); roots.append(root)
    st = json.load(open(os.path.join(ctx.S, "state.json")))
    st["last_ok_tick"] = iso(NOW - 3600)
    wjson(os.path.join(ctx.S, "state.json"), st)
    check(verdict(rows_of(ctx), "Dispatcher", "ticking") == "NO-GO", "R3 stale last_ok_tick is NO-GO")
    wtext(os.path.join(ctx.S, "state.json"), "{torn")
    check(verdict(rows_of(ctx), "Dispatcher", "ticking") == "UNMEASURED", "R3 torn state.json is UNMEASURED")

    # R4
    root, ctx, fake = fresh(); roots.append(root)
    wtext(os.path.join(ctx.S, "PAUSE"), "wave1 rollback: test\n")
    check(verdict(rows_of(ctx), "Dispatcher", "no PAUSE") == "NO-GO", "R4 PAUSE file is NO-GO")

    # R5
    root, ctx, fake = fresh(); roots.append(root)
    fake.put(("deadman_check.py",), (None, "timeout"))
    check(verdict(rows_of(ctx), "Deadman", "all arms alive") == "UNMEASURED", "R5 deadman not runnable: UNMEASURED")
    fake.put(("deadman_check.py",), (0, "deadman: DEAD arm dispatcher (stamp 40 min)\n"))
    check(verdict(rows_of(ctx), "Deadman", "all arms alive") == "NO-GO", "R5 deadman dead arm: NO-GO")

    # R6
    root, ctx, fake = fresh(); roots.append(root)
    wjson(os.path.join(root, "foundry", ".claude/settings.local.json"), {"permissions": {}})
    check(verdict(rows_of(ctx), "Doorbell FOUNDRY", "hook installed") == "NO-GO", "R6 no hook: NO-GO")
    root, ctx, fake = fresh(); roots.append(root)
    os.remove(os.path.join(ctx.S, "armed", "FOUNDRY.json"))
    st = json.load(open(os.path.join(ctx.S, "state.json")))
    st["alarms"] = {"unwakeable:FOUNDRY": NOW - 50}
    wjson(os.path.join(ctx.S, "state.json"), st)
    check(verdict(rows_of(ctx), "Doorbell FOUNDRY", "armed or rung") == "NO-GO", "R6 unwakeable alarm: NO-GO")
    st["alarms"] = {}
    wjson(os.path.join(ctx.S, "state.json"), st)
    check(verdict(rows_of(ctx), "Doorbell FOUNDRY", "armed or rung") == "UNMEASURED",
          "R6 no armed file, no alarm, no ring: UNMEASURED")
    wtext(os.path.join(ctx.S, "journal.jsonl"), json.dumps({"at": iso(NOW - 600), "do": "ring", "seat": "FOUNDRY",
                                                           "result": "rung"}) + "\n")
    check(verdict(rows_of(ctx), "Doorbell FOUNDRY", "armed or rung") == "GO", "R6 rung 10 min ago: GO")
    wjson(os.path.join(ctx.S, "armed", "FOUNDRY.json"), {"pid": 99999, "armed_at": iso(NOW - 60)})
    wtext(os.path.join(ctx.S, "journal.jsonl"), "")
    check(verdict(rows_of(ctx), "Doorbell FOUNDRY", "armed or rung") == "UNMEASURED",
          "R6 armed file whose pid is dead does not read GO")

    # R7
    root, ctx, fake = fresh(); roots.append(root)
    os.remove(os.path.join(ctx.repo, "src/RimMandrake/rimflow/roles/producer.md"))
    rows = rows_of(ctx)
    check(verdict(rows, "Producer", "instructions") == "NO-GO", "R7 missing instructions: NO-GO")
    check(verdict(rows, "Arbiter", "instructions") == "GO", "R7 other roles unaffected")

    # R8
    root, ctx, fake = fresh(); roots.append(root)
    st = json.load(open(os.path.join(ctx.S, "state.json")))
    st["roles"]["Arbiter"]["runs"][0]["tokens"] = 600000
    st["roles"]["Auditor"]["runs"][0]["state"] = "failed"
    st["roles"]["Innovator"]["runs"] = []
    st["roles"]["Operations"]["runs"][0]["tokens"] = 500000  # economy cap 550k: under
    del st["roles"]["Producer"]
    wjson(os.path.join(ctx.S, "state.json"), st)
    wjson(os.path.join(ctx.S, "roles", "rm-role-producer-1793230000.json"),
          {"subtype": "success", "is_error": False, "usage": GOOD_USAGE})
    rows = rows_of(ctx)
    check(verdict(rows, "Arbiter", "last run under cap") == "NO-GO", "R8 over cap: NO-GO")
    check(verdict(rows, "Auditor", "last run under cap") == "NO-GO", "R8 failed run: NO-GO")
    check(verdict(rows, "Innovator", "last run under cap") == "UNMEASURED", "R8 never run: UNMEASURED")
    check(verdict(rows, "Operations", "last run under cap") == "GO", "R8 economy run under economy cap: GO")
    r = find(rows, "Producer", "last run under cap")
    check(r is not None and r.verdict == "GO" and "trial" in r.evidence,
          "R8 an out-file-only trial run is weighed and GO (got %r)" % ((r and (r.verdict, r.evidence)),))
    wjson(os.path.join(ctx.S, "roles", "rm-role-producer-1793231000.json"),
          {"subtype": "error_max_turns", "is_error": True, "usage": GOOD_USAGE})
    check(verdict(rows_of(ctx), "Producer", "last run under cap") == "NO-GO", "R8 latest trial errored: NO-GO")

    # R9
    root, ctx, fake = fresh(); roots.append(root)
    victim = V.SELFTESTS["Auditor"][0]

    def st_one_fail(argv):
        rc, out = st_ok(argv)
        return (1, out.replace("PASS          0.1s  %s" % victim, "FAIL          0.1s  %s" % victim))
    fake.put(("run_selftests.py",), st_one_fail)
    rows = rows_of(ctx)
    check(verdict(rows, "Auditor", "selftests") == "NO-GO", "R9 FAIL line: that role NO-GO")
    shared = set(V.SELFTESTS["Auditor"])
    clean = [n for n in ("Conductor", "Operations") if not shared & set(V.SELFTESTS.get(n, []))]
    check(all(verdict(rows, n, "selftests") == "GO" for n in clean), "R9 roles not sharing the file stay GO")
    root, ctx, fake = fresh(); roots.append(root)
    ctx.selftests = False
    rows = rows_of(ctx)
    check(verdict(rows, "Conductor", "selftests") == "UNMEASURED", "R9 --no-selftests: UNMEASURED")
    check(not any("run_selftests.py" in " ".join(c) for c in fake.calls), "R9 --no-selftests runs none")
    fake.put(("run_selftests.py",), (None, "timeout"))
    ctx.selftests = True
    check(verdict(rows_of(ctx), "Conductor", "selftests") == "UNMEASURED", "R9 selftest runner timeout: UNMEASURED")

    # R10
    root, ctx, fake = fresh(); roots.append(root)
    os.remove(os.path.join(ctx.plan_dir, "HOLD"))
    check(verdict(rows_of(ctx), "Account HOLD", "HOLD file present") == "NO-GO", "R10 HOLD missing: NO-GO")
    fake.put(("is-active", "account-plan.timer"), (0, "active"))
    check(verdict(rows_of(ctx), "Account HOLD", "account-plan.timer off") == "NO-GO",
          "R10 account-plan.timer active: NO-GO")

    # R11
    root, ctx, fake = fresh(); roots.append(root)
    os.remove(os.path.join(ctx.repo, V.GOALS_REL))
    check(verdict(rows_of(ctx), "Goals", "present") == "NO-GO", "R11 goals missing: NO-GO")

    # R12
    root, ctx, fake = fresh(); roots.append(root)
    o = json.load(open(os.path.join(ctx.O, "status.json")))
    o2 = copy.deepcopy(o)
    o2["t"] = NOW - 7200
    wjson(os.path.join(ctx.O, "status.json"), o2)
    rows = rows_of(ctx)
    check(verdict(rows, "Runway", "Claude (acct_a)") == "UNMEASURED", "R12 stale status: Claude UNMEASURED")
    check(verdict(rows, "Runway", "Codex") == "UNMEASURED", "R12 stale status: Codex UNMEASURED")
    o2 = copy.deepcopy(o)
    o2["points"]["accounts.acct_a.runway"] = {"m": "UNMEASURED", "v": None}
    wjson(os.path.join(ctx.O, "status.json"), o2)
    check(verdict(rows_of(ctx), "Runway", "Claude (acct_a)") == "UNMEASURED", "R12 UNMEASURED point: UNMEASURED")
    o2 = copy.deepcopy(o)
    o2["points"]["accounts.acct_a.week_left_pct"] = {"m": "MEASURED", "v": 5.0}
    wjson(os.path.join(ctx.O, "status.json"), o2)
    check(verdict(rows_of(ctx), "Runway", "Claude (acct_a)") == "NO-GO", "R12 week left 5 %: NO-GO")
    o2 = copy.deepcopy(o)
    o2["points"]["codex.runway"] = {"m": "MEASURED", "v": 0.14}
    wjson(os.path.join(ctx.O, "status.json"), o2)
    rows = rows_of(ctx)
    check(verdict(rows, "Runway", "Codex") == "WARN", "R12 codex runway 0.14: WARN")
    check(V.overall(rows) == "GO", "R12 WARN does not block")

    # R13
    root, ctx, fake = fresh(); roots.append(root)
    ctx.expect_account = "acct_b"
    check(verdict(rows_of(ctx), "Account", "live account") == "NO-GO", "R13 expected acct_b, live acct_a: NO-GO")
    ctx.expect_account = "acct_a"
    check(verdict(rows_of(ctx), "Account", "live account") == "GO", "R13 expected acct_a, live acct_a: GO")

    # R14
    root, ctx, fake = fresh(); roots.append(root)
    fake.put(("cat-file", "-e", V.CUTOVER_REL), (128, "fatal: path not in origin/main"))
    check(verdict(rows_of(ctx), "Cutover", "tool on origin/main") == "NO-GO", "R14 cutover untracked: NO-GO")
    root, ctx, fake = fresh(); roots.append(root)
    fake.put(("diff", "--quiet", "origin/main", V.CUTOVER_REL), (1, ""))
    check(verdict(rows_of(ctx), "Cutover", "tool on origin/main") == "NO-GO", "R14 cutover differs from origin: NO-GO")

    # R15
    root, ctx, fake = fresh(); roots.append(root)
    fake.put(("log", "-1", "--format=%ct", "FOUNDRY.jsonl"), (0, "%d\n" % int(NOW - 36000)))
    check(verdict(rows_of(ctx), "FOUNDRY ledger", "published recently") == "NO-GO", "R15 10 h old: NO-GO")
    fake.put(("log", "-1", "--format=%ct", "FOUNDRY.jsonl"), (128, "fatal"))
    check(verdict(rows_of(ctx), "FOUNDRY ledger", "published recently") == "UNMEASURED", "R15 git error: UNMEASURED")

    # R16
    R = V.Row
    check(V.overall([R("a", "b", "GO", "", True), R("a", "c", "UNMEASURED", "", True)]) == "UNMEASURED",
          "R16 blocking UNMEASURED -> UNMEASURED")
    check(V.overall([R("a", "b", "NO-GO", "", True), R("a", "c", "UNMEASURED", "", True)]) == "NO-GO",
          "R16 NO-GO beats UNMEASURED")
    check(V.overall([R("a", "b", "GO", "", True), R("a", "c", "WARN", "", False),
                     R("a", "d", "INFO", "", False)]) == "GO", "R16 WARN/INFO never block")
    check(V.overall([]) == "UNMEASURED", "R16 no rows at all is UNMEASURED, not GO")

    # R17
    root, ctx, fake = fresh(); roots.append(root)
    shutil.rmtree(os.path.join(ctx.proc, "5002"))
    check(verdict(rows_of(ctx), "Window CONDUCTOR", "live session") == "NO-GO", "R17 dead pid: NO-GO")
    root, ctx, fake = fresh(); roots.append(root)
    wjson(os.path.join(ctx.sessions, "5001.json"), {"pid": 5001, "procStart": "1", "name": "AGENT FOUNDRY"})
    check(verdict(rows_of(ctx), "Window FOUNDRY", "live session") == "NO-GO", "R17 reused pid (start differs): NO-GO")
    root, ctx, fake = fresh(); roots.append(root)
    rows = rows_of(ctx)
    r = find(rows, "Conductor", "hold window")
    check(r is not None and r.verdict == "INFO" and not r.blocking,
          "R17 role window_name absent is INFO (headless runs launch), got %r" % ((r and (r.verdict, r.evidence)),))
    check(verdict(rows, "Window CONDUCTOR", "live session") == "GO", "R17 Conductor tile is the AGENT BENCH session")
    # R19
    root, ctx, fake = fresh(); roots.append(root)
    os.remove(os.path.join(ctx.dispatch, V.SCHEDULE_REL))
    rows = rows_of(ctx)
    check(verdict(rows, "Schedule", "dispatch clone readable") == "UNMEASURED" and V.overall(rows) != "GO",
          "R19 dispatch schedule missing: UNMEASURED, overall not GO")
    root, ctx, fake = fresh(); roots.append(root)
    wjson(os.path.join(ctx.dispatch, V.SCHEDULE_REL), {})
    check(V.overall(rows_of(ctx)) != "GO", "R19 empty dispatch schedule is not GO")
    root, ctx, fake = fresh(); roots.append(root)
    st = json.load(open(os.path.join(ctx.S, "state.json"))); st["apply"] = False
    wjson(os.path.join(ctx.S, "state.json"), st)
    check(verdict(rows_of(ctx), "Dispatcher", "ticking") == "NO-GO", "R19 fresh tick with apply=false: NO-GO")
    root, ctx, fake = fresh(); roots.append(root)
    sp = os.path.join(ctx.O, "status.json")
    d = json.load(open(sp)); d["t"] = NOW + 7200
    wjson(sp, d)
    check(verdict(rows_of(ctx), "Runway", "Codex") == "UNMEASURED", "R19 future ops timestamp: UNMEASURED")
    with open(sp, "w") as f:
        f.write(json.dumps(dict(d, t=0)).replace('"t": 0', '"t": NaN'))
    check(verdict(rows_of(ctx), "Runway", "Codex") == "UNMEASURED", "R19 NaN ops timestamp: UNMEASURED")
    d["t"] = NOW - 60
    d["points"].pop("accounts.acct_a.runway", None)
    d["points"]["accounts.acct_a.week_left_pct"] = {"m": "MEASURED", "v": 5, "unit": "%"}
    wjson(sp, d)
    check(verdict(rows_of(ctx), "Runway", "Claude (acct_a)") == "NO-GO", "R19 week left 5 %, runway missing: NO-GO")
    root, ctx, fake = fresh(); roots.append(root)
    fake.put(("claude-account", "status"), (1, json.dumps({"ok": False, "live": "acct_a", "accounts": []})))
    check(verdict(rows_of(ctx), "Account", "live account") == "UNMEASURED", "R19 claude-account rc 1: UNMEASURED")
    root, ctx, fake = fresh(); roots.append(root)
    fake.put(("is-active", "account-plan.timer"), (1, "Failed to connect to bus"))
    check(verdict(rows_of(ctx), "Account HOLD", "account-plan.timer off") == "UNMEASURED",
          "R19 systemctl bus error: UNMEASURED, not GO")
    root, ctx, fake = fresh(); roots.append(root)
    wjson(os.path.join(root, "foundry", ".claude/settings.local.json"),
          {"hooks": {"Stop": [{"hooks": [{"type": "command", "asyncRewake": True, "command": "echo doorbell.py"}]}]}})
    check(verdict(rows_of(ctx), "Doorbell FOUNDRY", "hook installed") == "NO-GO", "R19 echo-only hook: NO-GO")
    root, ctx, fake = fresh(); roots.append(root)
    wjson(os.path.join(ctx.S, "armed", "FOUNDRY.json"), {"pid": 4242, "armed_at": iso(NOW - 60), "owner_pid": 7777})
    check(verdict(rows_of(ctx), "Doorbell FOUNDRY", "armed or rung") != "GO",
          "R19 armed pid alive but its window is not a live session: not GO")
    root, ctx, fake = fresh(); roots.append(root)
    os.remove(os.path.join(ctx.repo, V.SELFTESTS["Auditor"][0]))
    check(verdict(rows_of(ctx), "Auditor", "selftests") == "UNMEASURED", "R19 a mapped selftest missing: UNMEASURED")
    check(sys.dont_write_bytecode, "R19 importing v3_ready turns bytecode writing off")
finally:
    for r in roots:
        shutil.rmtree(r, ignore_errors=True)

print("\n%s: %d failure(s)" % ("RED" if FAILS else "GREEN", len(FAILS)))
sys.exit(1 if FAILS else 0)
