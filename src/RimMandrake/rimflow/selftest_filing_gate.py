#!/usr/bin/env python3
"""Selftest of filing_gate.py (RIMMANDRAKE_REFUSE_FILING_WITHOUT_EVIDENCE_WHY_NOT_FIX_IT_NOW). Each promise of
design/specs/2026-11-24-filing-gate/boundary.md has a test of its name. Offline: the gate is a pure function, and the
doors are driven through cli.py on a scratch ledger, a scratch state folder and a scratch git repository.

    python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/rimflow/selftest_filing_gate.py
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
import filing_gate as FG  # noqa: E402
import time_budget  # noqa: E402

FAILS = []
TMP = tempfile.mkdtemp(prefix="selftest_filing_gate.")
CLI = os.path.join(HERE, "cli.py")
HOOK = os.path.join(REPO, ".claude", "hooks", "filing_refusal_before_stop.py")
UNIT = "rm-detached-bench-some-run-1"
LIVE = {"rm-detached-bench-other-run-2"}


def check(what, ok, got=None):
    print("  %s  %s" % ("PASS" if ok else "FAIL", what) + ("" if ok else "  got: %r" % (got,)))
    if not ok:
        FAILS.append(what)


def gate(kind="bug", unit=UNIT, owner=False, program="", not_now=None, live=LIVE, mods=("FlowWorks",)):
    return FG.decide(kind=kind, unit=unit, owner=owner, program=program, not_now=not_now, live_units=live,
                     mod_exists=lambda m: m in mods)


def t_a_helper_work_ticket_with_no_evidence_is_refused():
    for kind in ("bug", "task", None):
        d = gate(kind=kind)
        check("kind %s, no flag: refused" % kind, not d.ok and "do the work now" in d.text.lower(), d)
    check("an empty flag is no evidence", not gate(not_now="  ").ok)


def t_the_refusal_is_a_path_to_pass():
    d = gate()
    check("names the flag and the form", "--not-now" in d.text and "<class>: <evidence>" in d.text, d.text)
    check("lists each class", all(c in d.text for c in FG.CLASSES), d.text)
    check("says test first", "test first" in d.text, d.text)


def t_evidence_of_a_known_class_files_the_ticket():
    d = gate(not_now="no-tool: the bridge DLL cannot be replaced while a game runs")
    check("filed", d.ok, d)
    check("class and evidence recorded", d.record == {"class": "no-tool",
          "evidence": "the bridge DLL cannot be replaced while a game runs"}, d.record)
    check("the class name again is not evidence", not gate(not_now="no-tool: no-tool no tool").ok)
    check("short evidence is refused", not gate(not_now="fix-unknown: busy").ok)
    check("a class with no colon is refused", not gate(not_now="no-tool the bridge cannot be replaced").ok)


def t_an_unknown_class_is_refused():
    for bad in ("large: the work has four parts and a live proof", "my work would not finish: three more parts",
                "later: the next run can do this part better"):
        d = gate(not_now=bad)
        check("refused: %s" % bad.split(":")[0], not d.ok and all(c in d.text for c in FG.CLASSES), d)


def t_files_held_names_a_live_run():
    check("a live unit passes", gate(not_now="files-held: rm-detached-bench-other-run-2 edits cli.py").ok)
    d = gate(not_now="files-held: rm-detached-bench-dead-run-9 edits cli.py")
    check("a unit that is not live is refused", not d.ok and "live" in d.text, d)
    check("no unit named is refused", not gate(not_now="files-held: somebody else has the files").ok)
    check("its own unit is not another run", not gate(not_now="files-held: %s edits cli.py" % UNIT, live=LIVE | {UNIT}).ok)


def t_other_mod_names_a_mod_folder():
    check("a mod folder passes", gate(not_now="other-mod: FlowWorks, the pit cover scene").ok)
    d = gate(not_now="other-mod: NoSuchMod, its walk scene needs work")
    check("an unknown mod is refused", not d.ok and "mod" in d.text, d)


def t_could_not_look_is_not_a_refusal():
    d = gate(not_now="files-held: rm-detached-bench-other-run-2 edits cli.py", live=None)
    check("filed", d.ok, d)
    check("the record says could not look", "could not look" in (d.record or {}).get("checked", ""), d.record)


def t_the_owner_and_the_conductor_are_never_refused():
    check("the owner's authority", gate(owner=True).ok)
    check("a window (no unit)", gate(unit="").ok and gate(unit=None).ok)
    check("neither records a class", gate(owner=True).record is None and gate(unit="").record is None)


def t_only_a_reminder_kind_passes_with_no_flag():
    for kind in FG.REMINDER_KINDS + ("Owed", " notice "):
        check("kind %r passes" % kind, gate(kind=kind).ok)
    for kind in ("bug", "task", None, "", "fix", "defect", "build", "problem", "Bug", "polish"):   # kinds of the ledger
        check("kind %r is work: refused" % kind, not gate(kind=kind).ok)
    check("the list is what passes", FG.REMINDER_KINDS == ("owed", "design", "notice", "alarm"), FG.REMINDER_KINDS)


def t_a_program_is_never_refused():
    d = gate(program="detached_helper.file_remainder")
    check("filed, and the name recorded", d.ok and d.record == {"program": "detached_helper.file_remainder"}, d)


def t_each_promise_of_the_page_has_its_test():
    page = open(os.path.join(REPO, "design/specs/2026-11-24-filing-gate/boundary.md"), encoding="utf-8").read()
    names = re.findall(r"^- \*\*([a-z0-9-]+)\.\*\*", page.split("## PROMISES")[1].split("## LIMITS")[0], re.M)
    check("the page has promises", len(names) >= 9, names)
    for n in names:
        check("test of %s" % n, ("t_" + n.replace("-", "_")) in globals())
    tests = [k for k in globals() if k.startswith("t_") and k != "t_each_promise_of_the_page_has_its_test"]
    run = set(re.findall(r"^        (t_\w+),$", open(__file__, encoding="utf-8").read(), re.M))
    check("main runs each test (%d of %d)" % (len(run & set(tests)), len(tests)), set(tests) <= run, set(tests) - run)
    orphans = [k for k in tests if k[2:].replace("_", "-") not in names]
    check("each test is of a promise of the page (%d tests, %d promises)" % (len(tests), len(names)), not orphans, orphans)


def _body(src, head):
    body = src[src.index(head) + (1 if head.startswith("\n") else 0):]
    return body[:body.index("\ndef ", 10)]


def t_the_door_calls_the_gate_before_it_writes():
    src = open(CLI, encoding="utf-8").read()
    for head in ("def _file(args, seat, w, pf):", "def cmd_spawn(args, seat):"):
        body = _body(src, head)
        at, emit = body.find("_filing_door("), body.find("_emit(ev")
        check("%s calls the gate before the event is written (%d < %d)" % (head[4:].split("(")[0], at, emit),
              0 <= at < emit, None)
        check("%s resolves a refusal after it writes" % head[4:].split("(")[0],
              emit < body.find("_filed_through_door(") , None)
    flags = _body(src, "def _filing_flags(s):")
    check("the three ways are on the parser", all(f in flags for f in ('"--not-now"', '"--did-it"', '"--not-worth-it"')))
    check("both doors take them", src.count("    _filing_flags(s)") == 2, src.count("    _filing_flags(s)"))


# ---- the record, the three ways ------------------------------------------------------------------------------------

def door(state, iid="RIMMANDRAKE_SOME_WORK_LEFT_HERE", kind="bug", unit=UNIT, owner=False, program="", not_now=None,
         did_it=None, not_worth_it=None, look=None, door_="file"):
    return FG.at_door(door_, iid, "some work left here", kind, unit=unit, owner=owner, program=program,
                      not_now=not_now, did_it=did_it, not_worth_it=not_worth_it, state_dir=state,
                      facts_fn=lambda: (LIVE, lambda m: m == "FlowWorks"),
                      look_sha=lambda sha: look or {"looked": True, "exists": True, "published": True,
                                                    "ledger_only": False, "sha": sha + "0" * (40 - len(sha))},
                      now="2026-11-24T00:00:00Z")


def scratch(name):
    d = os.path.join(TMP, name)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    return d


def lines_of(state, unit=UNIT):
    try:
        with open(FG.refusals_path(unit, state), encoding="utf-8") as f:
            return [json.loads(x) for x in f if x.strip()]
    except OSError:
        return []


def t_every_refusal_is_recorded():
    st = scratch("rec")
    d = door(st)
    rows = lines_of(st)
    check("refused, exit 6", not d.go and d.rc == 6, d)
    check("one line in <state>/filing_refusals/<unit>.jsonl", len(rows) == 1 and
          FG.refusals_path(UNIT, st) == os.path.join(st, "filing_refusals", UNIT + ".jsonl"), rows)
    want = {"at", "unit", "id", "title", "kind", "why"}
    check("the line holds at, unit, id, title, kind, why", rows and want <= set(rows[0]) and rows[0]["id"] ==
          "RIMMANDRAKE_SOME_WORK_LEFT_HERE" and rows[0]["unit"] == UNIT and rows[0]["why"], rows)
    check("the refusal text says it is recorded and the three ways", "recorded" in d.text and "--did-it" in d.text
          and "--not-worth-it" in d.text, d.text)
    check("a pass is not recorded", door(scratch("rec2"), kind="owed").go and lines_of(os.path.join(TMP, "rec2")) == [])


def t_a_record_that_cannot_be_written_never_changes_the_refusal():
    st = os.path.join(scratch("norec"), "a_file")
    open(st, "w").close()                      # the state folder is a file: no record can be written under it
    d = door(st)
    check("still refused, exit 6", not d.go and d.rc == 6, d)
    check("one stderr line says the record failed", d.err.startswith("filing_gate: the record could not be written")
          and "\n" not in d.err, d.err)
    ok = door(st, not_now="no-tool: the bridge DLL cannot be replaced while a game runs")
    check("a filing that passes still passes", ok.go, ok)


def t_filing_with_evidence_resolves_a_refusal():
    st = scratch("filed")
    door(st)
    check("one unresolved", [r["id"] for r in FG.unresolved(UNIT, st)] == ["RIMMANDRAKE_SOME_WORK_LEFT_HERE"])
    d = door(st, not_now="no-tool: the bridge DLL cannot be replaced while a game runs")
    check("filed", d.go, d)
    FG.after_filed(UNIT, st, "RIMMANDRAKE_SOME_WORK_LEFT_HERE", d.record)
    check("resolved: none left", FG.unresolved(UNIT, st) == [], FG.unresolved(UNIT, st))
    check("the resolution line says filed", lines_of(st)[-1].get("resolved") == "filed", lines_of(st))
    check("a filing with no refusal writes no line", FG.after_filed(UNIT, st, "RIMMANDRAKE_OTHER", None) == ""
          and len(lines_of(st)) == 2, lines_of(st))


def t_did_it_files_nothing_and_records_the_sha():
    st = scratch("did")
    door(st)
    d = door(st, did_it="abc1234")
    check("nothing filed, exit 0", not d.go and d.rc == 0, d)
    check("says it", d.text.startswith("nothing filed: RIMMANDRAKE_SOME_WORK_LEFT_HERE was done in this run at abc1234"),
          d.text)
    row = lines_of(st)[-1]
    check("records did with the sha", row.get("resolved") == "did" and row.get("sha", "").startswith("abc1234"), row)
    check("resolved", FG.unresolved(UNIT, st) == [])
    for look, word in (({"looked": True, "exists": False}, "does not exist"),
                       ({"looked": True, "exists": True, "published": False}, "not on origin/main"),
                       ({"looked": True, "exists": True, "published": True, "ledger_only": True}, "ledger")):
        r = door(scratch("did2"), did_it="abc1234", look=look)
        check("a sha that %s is refused, exit 6, nothing recorded" % word, not r.go and r.rc == 6 and word in r.text
              and lines_of(os.path.join(TMP, "did2")) == [], r)


def t_a_sha_git_cannot_read_is_accepted_and_says_so():
    st = scratch("blind")
    d = door(st, did_it="abc1234", look={"looked": False, "why": "no git repository at /x"})
    check("accepted, exit 0", not d.go and d.rc == 0 and "could not look" in d.text, d)
    check("the record says could not look", "could not look" in lines_of(st)[-1].get("checked", ""), lines_of(st))


def t_not_worth_it_files_nothing_and_records_why():
    st = scratch("drop")
    door(st)
    short = door(st, not_worth_it="meh, no")
    check("a why under 12 characters is refused, exit 6", not short.go and short.rc == 6, short)
    d = door(st, not_worth_it="a cosmetic typo in a log line nobody reads")
    check("nothing filed, exit 0, one line", not d.go and d.rc == 0 and "\n" not in d.text and "nothing filed" in d.text, d)
    row = lines_of(st)[-1]
    check("records dropped with the why", row.get("resolved") == "dropped" and "typo" in row.get("why", ""), row)
    check("resolved", FG.unresolved(UNIT, st) == [])


def t_one_way_at_a_time():
    d = door(scratch("two"), did_it="abc1234", not_worth_it="a cosmetic typo in a log line nobody reads")
    check("two ways: exit 2, nothing recorded", not d.go and d.rc == 2 and lines_of(os.path.join(TMP, "two")) == [], d)


def t_unresolved_says_could_not_look():
    st = scratch("look")
    check("no file: no refusal", FG.unresolved(UNIT, st) == [])
    door(st)
    with open(FG.refusals_path(UNIT, st), "a") as f:
        f.write("{not json\n")
    check("a bad line: None, never empty", FG.unresolved(UNIT, st) is None)
    check("the run-end line says could not look", FG.run_end_lines(UNIT, st)[0].startswith(
        "filing refusals: could not look ("), FG.run_end_lines(UNIT, st))
    st2 = scratch("look2")
    os.makedirs(FG.refusals_path(UNIT, st2))          # a folder where the file should be: cannot be read
    check("an unreadable file: None", FG.unresolved(UNIT, st2) is None)


def t_the_run_end_names_each_unresolved_refusal():
    st = scratch("end")
    door(st)
    door(st, iid="RIMMANDRAKE_SECOND_WORK_LEFT_HERE")
    door(st, iid="RIMMANDRAKE_SECOND_WORK_LEFT_HERE", not_worth_it="a cosmetic typo in a log line nobody reads")
    check("one line per refusal not resolved", FG.run_end_lines(UNIT, st) ==
          ["REFUSED FILING NOT RESOLVED: RIMMANDRAKE_SOME_WORK_LEFT_HERE: some work left here"],
          FG.run_end_lines(UNIT, st))
    os.environ["RM_DISPATCHER_STATE"] = st
    try:
        import detached_helper as DH
        check("detached_helper reads the same lines", DH.filing_refusal_lines(UNIT) == FG.run_end_lines(UNIT, st))
    finally:
        os.environ.pop("RM_DISPATCHER_STATE", None)
    src = open(os.path.join(HERE, "detached_helper.py"), encoding="utf-8").read()
    fin = _body(src, "\ndef finish(unit,")
    check("finish takes the lines into its steps and its wake", "filing_refusal_lines(unit)" in fin and
          "steps.extend(refused)" in fin and "wake_conductor(unit, st, rec[\"out\"], item, seat, waker, said)" in fin
          and "run_wakes(rec, said)" in fin, None)


def t_the_stop_hook_keeps_the_run_until_each_refusal_is_resolved():
    st, blocks = scratch("hook"), scratch("hookblocks")
    door(st)
    env = dict((k, v) for k, v in os.environ.items() if not k.startswith("RM_"))
    env.update(RM_ROLE_UNIT=UNIT, RM_DISPATCHER_STATE=st, RM_STOP_BLOCKS_DIR=blocks)
    r = subprocess.run([sys.executable, HOOK], input="{}", capture_output=True, text=True, env=env, timeout=time_budget.CALL_S)
    out = json.loads(r.stdout or "{}")
    check("blocks, exit 0, names the id and the three ways", r.returncode == 0 and out.get("decision") == "block" and
          "RIMMANDRAKE_SOME_WORK_LEFT_HERE" in out.get("reason", "") and all(
              w in out.get("reason", "") for w in ("--did-it", "--not-now", "--not-worth-it")), (r.returncode, r.stdout))
    door(st, did_it="abc1234")
    r = subprocess.run([sys.executable, HOOK], input="{}", capture_output=True, text=True, env=env, timeout=time_budget.CALL_S)
    check("resolved: silent", r.returncode == 0 and not r.stdout.strip(), r.stdout)


# ---- the doors, driven through cli.py ------------------------------------------------------------------------------

def cli_env(name, unit=UNIT, **over):
    d = os.path.join(TMP, "cli-" + name)
    e = {k: v for k, v in os.environ.items() if k not in ("RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID",
         "RM_ROLE_UNIT", "RM_FILING_PROGRAM", "RM_DETACHED_UNIT", "RM_DISPATCHER_STATE") and not k.startswith("GIT_")}
    e.update(RIMFLOW_LEDGER=os.path.join(d, "events.jsonl"), RIMFLOW_ITEMS=os.path.join(d, "items"),
             RIMFLOW_PROBE="no-reading", RIMFLOW_SCHEDULE=os.path.join(TMP, "no_schedule.json"), RIMFLOW_DRIVER_LOCK="",
             RIMFLOW_BRIDGE_LOCK=os.path.join(TMP, "bridge.lock"), RM_DISPATCHER_STATE=os.path.join(d, "state"),
             RIMFLOW_SEAT="BENCH")
    if unit:
        e["RM_ROLE_UNIT"] = unit
    e.update(over)
    return e, d


def fresh_cli(name):
    d = os.path.join(TMP, "cli-" + name)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(os.path.join(d, "items"))


def cli(env, *args):
    assert env["RIMFLOW_LEDGER"].startswith(TMP + os.sep) and env["RM_DISPATCHER_STATE"].startswith(TMP + os.sep)
    r = subprocess.run([sys.executable, CLI] + list(args), capture_output=True, text=True, env=env, cwd=REPO,
                       timeout=time_budget.RIMFLOW_S, stdin=subprocess.DEVNULL)
    return r.returncode, r.stdout + r.stderr


def events(env, iid):
    out = []
    led = env["RIMFLOW_LEDGER"]
    for path in [led] + [os.path.join(os.path.dirname(led), "events", n) for n in
                         (os.listdir(os.path.join(os.path.dirname(led), "events"))
                          if os.path.isdir(os.path.join(os.path.dirname(led), "events")) else ())]:
        if os.path.isfile(path):
            out += [e for e in (json.loads(x) for x in open(path, encoding="utf-8") if x.strip())
                    if iid in (e.get("id"), e.get("name"))]
    return out


ID = "RIMMANDRAKE_PROBE_FILING_GATE_DOOR_LEAVES_NO_EVENT"


def t_the_file_door_refuses_records_and_writes_nothing():
    fresh_cli("file")
    env, d = cli_env("file")
    rc, out = cli(env, "file", ID, "--for", "CONDUCTOR", "--kind", "bug", "--title", "probe")
    check("cli file: refused, exit 6", rc == 6 and "REFUSED" in out, (rc, out[-600:]))
    check("no ledger event", events(env, ID) == [], events(env, ID))
    check("the refusal is recorded", [r["id"] for r in FG.unresolved(UNIT, env["RM_DISPATCHER_STATE"])] == [ID])
    rc, out = cli(env, "file", ID, "--for", "CONDUCTOR", "--kind", "bug", "--title", "probe", "--not-now",
                  "no-tool: the bridge DLL cannot be replaced while a game runs")
    ev = events(env, ID)
    check("with evidence: filed, the class on the event", rc == 0 and len(ev) == 1 and
          ev[0].get("not_now", {}).get("class") == "no-tool", (rc, out[-600:], ev))
    check("and the refusal is resolved as filed", FG.unresolved(UNIT, env["RM_DISPATCHER_STATE"]) == [])
    rc, out = cli(env, "file", ID + "_TWO", "--for", "CONDUCTOR", "--title", "probe", "--not-worth-it",
                  "a cosmetic typo in a log line nobody reads")
    check("cli file --not-worth-it: exit 0, nothing filed", rc == 0 and "nothing filed" in out and
          events(env, ID + "_TWO") == [], (rc, out[-400:]))


def t_per_ruling_alone_is_not_the_owner():
    fresh_cli("ruling")
    win, _ = cli_env("ruling", unit="")
    rc, out = cli(win, "file", "RIMMANDRAKE_SOME_RULING_TO_CITE_HERE", "--for", "CONDUCTOR", "--title", "a ruling")
    check("a window files with no flag", rc == 0, (rc, out[-400:]))
    env, _ = cli_env("ruling")
    rc, out = cli(env, "file", ID, "--for", "CONDUCTOR", "--title", "probe", "--per-ruling",
                  "RIMMANDRAKE_SOME_RULING_TO_CITE_HERE")
    check("a helper with --per-ruling alone: refused, exit 6", rc == 6 and "REFUSED" in out and events(env, ID) == [],
          (rc, out[-600:]))
    src = _body(open(CLI, encoding="utf-8").read(), "def _filing_owner():")
    check("the owner is his words or his card", "OWNER_SAID" in src and "BY_CARD" in src and
          "PER_RULING" not in src.split('"""')[-1], src)


def t_the_spawn_door_has_the_same_gate():
    fresh_cli("spawn")
    win, _ = cli_env("spawn", unit="")
    cli(win, "file", "RIMMANDRAKE_SOME_CAUSE_TO_SPAWN_FROM", "--for", "CONDUCTOR", "--title", "a cause")
    env, _ = cli_env("spawn")
    rc, out = cli(env, "spawn", "--from", "RIMMANDRAKE_SOME_CAUSE_TO_SPAWN_FROM", "--for", "CONDUCTOR", "--name", ID)
    rows = FG.unresolved(UNIT, env["RM_DISPATCHER_STATE"]) or []
    check("cli spawn: refused, exit 6, no event", rc == 6 and events(env, ID) == [], (rc, out[-600:]))
    check("recorded, door spawn", [(r["id"], r.get("door")) for r in rows] == [(ID, "spawn")], rows)
    rc, out = cli(env, "spawn", "--from", "RIMMANDRAKE_SOME_CAUSE_TO_SPAWN_FROM", "--for", "CONDUCTOR", "--name", ID,
                  "--not-now", "fix-unknown: tried two hypotheses, the cause is still unknown")
    check("with evidence: spawned, resolved", rc == 0 and len(events(env, ID)) == 1 and
          FG.unresolved(UNIT, env["RM_DISPATCHER_STATE"]) == [], (rc, out[-600:]))
    rc, out = cli(env, "spawn", "--from", "RIMMANDRAKE_SOME_CAUSE_TO_SPAWN_FROM", "--for", "CONDUCTOR", "--name",
                  ID + "_TWO", "--kind", "alarm")
    check("a reminder kind spawns with no flag", rc == 0, (rc, out[-400:]))


def git(repo, *a):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false"] + list(a),
                          cwd=repo, capture_output=True, text=True, timeout=time_budget.CALL_S).stdout.strip()


def t_did_it_reads_git_at_the_door():
    repo = scratch("repo")
    git(repo, "init", "-q")
    for rel in ("src/x.py", "infrastructure/state/ledger/events/X.jsonl"):
        os.makedirs(os.path.dirname(os.path.join(repo, rel)), exist_ok=True)
        open(os.path.join(repo, rel), "w").write("x\n")
        git(repo, "add", rel)
        git(repo, "commit", "-q", "-m", rel)
    work, ledger = git(repo, "rev-parse", "HEAD~1"), git(repo, "rev-parse", "HEAD")
    git(repo, "update-ref", "refs/remotes/origin/main", ledger)
    open(os.path.join(repo, "src/x.py"), "w").write("y\n")
    git(repo, "commit", "-q", "-am", "local")
    local = git(repo, "rev-parse", "HEAD")
    fresh_cli("did")
    env, _ = cli_env("did", RIMFLOW_GIT_CWD=repo)
    for sha, rc_want, word in ((work[:10], 0, "was done in this run at " + work), (ledger[:10], 6, "ledger"),
                               (local[:10], 6, "origin/main"), ("0123456789abcdef", 6, "does not exist")):
        rc, out = cli(env, "file", ID, "--for", "CONDUCTOR", "--title", "probe", "--did-it", sha)
        check("--did-it %s: exit %d, says %r" % (sha, rc_want, word), rc == rc_want and word in out, (rc, out[-500:]))
    check("nothing filed", events(env, ID) == [])
    env2, _ = cli_env("did", RIMFLOW_GIT_CWD=scratch("nogit"))
    rc, out = cli(env2, "file", ID, "--for", "CONDUCTOR", "--title", "probe", "--did-it", work[:10])
    check("no git here: accepted, says could not look", rc == 0 and "could not look" in out, (rc, out[-500:]))


def t_each_program_that_files_names_itself():
    sites = {"src/RimMandrake/rimflow/detached_helper.py": 'RM_FILING_PROGRAM="detached_helper.file_remainder"',
             "src/RimMandrake/Utils/follow_through.py": 'RM_FILING_PROGRAM="follow_through._cli"',
             "src/RimMandrake/Utils/art_eval/auto_judge.py": 'RM_FILING_PROGRAM="auto_judge.file_item"',
             "src/RimMandrake/rimflow/dispatcher.py": 'RM_FILING_PROGRAM="dispatcher.ledger_structural"',
             "src/RimMandrake/Utils/testq/ingest.py": "RM_FILING_PROGRAM=filing_program()"}
    for path, needle in sites.items():
        check("%s names itself" % path, needle in open(os.path.join(REPO, path), encoding="utf-8").read())
    # every program that files through ingest.rimflow (ops_watch, deadman_check, maturation_dispatch, steward,
    # testq ingest) is named by its own module and function in the env of its own cli call
    sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils", "testq"))
    import ingest
    seen = {}

    class Run:
        returncode, stdout, stderr = 0, "", ""

    def fake(argv, env=None, **kw):
        seen["env"] = env
        return Run()
    real, ingest.own_cgroup.run = ingest.own_cgroup.run, fake
    try:
        def real_filer():
            return ingest.rimflow("spawn", "--from", "X")
        real_filer()
        check("ingest.rimflow names its caller", (seen.get("env") or {}).get("RM_FILING_PROGRAM") ==
              "selftest_filing_gate.real_filer", (seen.get("env") or {}).get("RM_FILING_PROGRAM"))
        check("the agent's own shell is not touched", "RM_FILING_PROGRAM" not in os.environ or
              os.environ.get("RM_FILING_PROGRAM") == seen["env"]["RM_FILING_PROGRAM"] is None)
    finally:
        ingest.own_cgroup.run = real


def t_a_test_with_the_real_state_files_as_no_run():
    real = "/mnt/d/ClaudeWork/rimmandrake/dispatcher"
    check("a test on the real state: no unit", FG.filing_unit(UNIT, real, True, real) == "")
    check("a test with its own state: its unit", FG.filing_unit(UNIT, os.path.join(TMP, "s"), True, real) == UNIT)
    check("a run that is no test: its unit", FG.filing_unit(UNIT, real, False, real) == UNIT)


PROBE_TEST = r'''import os, subprocess, sys
env = dict(os.environ)
if len(sys.argv) > 2:
    env["RM_ROLE_UNIT"] = sys.argv[2]          # the test names a unit of its own for the filing
r = subprocess.run([sys.executable, %(cli)r, "file", sys.argv[1], "--for", "CONDUCTOR", "--kind", "task",
                    "--title", "probe"], env=env, capture_output=True, text=True, timeout=%(budget)d, stdin=subprocess.DEVNULL)
sys.stdout.write(r.stdout + r.stderr)
sys.exit(r.returncode)
'''


def t_a_unit_a_test_inherited_from_its_run_is_no_run():
    """A selftest run inside a helper (RM_ROLE_UNIT) that brings its own state folder and files with the unit it was
    launched with: a window. The same test that sets a unit of its own for the filing: the whole gate."""
    real = "/mnt/d/ClaudeWork/rimmandrake/dispatcher"
    own = os.path.join(TMP, "s")
    check("a test, its own state, the unit of its run: no unit", FG.filing_unit(UNIT, own, True, real, UNIT) == "")
    check("a test, its own state, a unit of its own: its unit",
          FG.filing_unit(UNIT, own, True, real, "rm-detached-bench-the-run-9") == UNIT)
    check("a test whose run cannot be read: its unit", FG.filing_unit(UNIT, own, True, real, None) == UNIT)
    check("a run that is no test: its unit, whatever its launch", FG.filing_unit(UNIT, own, False, real, UNIT) == UNIT)
    probe = os.path.join(TMP, "selftest_inherit_probe.py")
    with open(probe, "w", encoding="utf-8") as f:
        f.write(PROBE_TEST % {"cli": CLI, "budget": time_budget.RIMFLOW_S})
    fresh_cli("inherit")
    env, d = cli_env("inherit")
    pid = "RIMMANDRAKE_PROBE_FILING_GATE_INHERITED_UNIT"
    r = subprocess.run([sys.executable, probe, pid], capture_output=True, text=True, env=env, cwd=REPO, timeout=2 * time_budget.RIMFLOW_S)
    check("through cli.py, the inherited unit: filed, no refusal", r.returncode == 0 and len(events(env, pid)) == 1
          and lines_of(env["RM_DISPATCHER_STATE"]) == [], (r.returncode, r.stdout[-600:]))
    r = subprocess.run([sys.executable, probe, pid + "_OWN", UNIT], capture_output=True, text=True,
                       env=dict(env, RM_ROLE_UNIT="rm-detached-bench-the-run-9"), cwd=REPO, timeout=2 * time_budget.RIMFLOW_S)
    check("through cli.py, a unit the test set: refused, exit 6, recorded", r.returncode == 6 and
          events(env, pid + "_OWN") == [] and [x["id"] for x in lines_of(env["RM_DISPATCHER_STATE"])] == [pid + "_OWN"],
          (r.returncode, r.stdout[-600:]))


def main():
    tests = (
        t_a_helper_work_ticket_with_no_evidence_is_refused,
        t_the_refusal_is_a_path_to_pass,
        t_evidence_of_a_known_class_files_the_ticket,
        t_an_unknown_class_is_refused,
        t_files_held_names_a_live_run,
        t_other_mod_names_a_mod_folder,
        t_could_not_look_is_not_a_refusal,
        t_the_owner_and_the_conductor_are_never_refused,
        t_only_a_reminder_kind_passes_with_no_flag,
        t_a_program_is_never_refused,
        t_each_promise_of_the_page_has_its_test,
        t_the_door_calls_the_gate_before_it_writes,
        t_every_refusal_is_recorded,
        t_a_record_that_cannot_be_written_never_changes_the_refusal,
        t_filing_with_evidence_resolves_a_refusal,
        t_did_it_files_nothing_and_records_the_sha,
        t_a_sha_git_cannot_read_is_accepted_and_says_so,
        t_not_worth_it_files_nothing_and_records_why,
        t_one_way_at_a_time,
        t_unresolved_says_could_not_look,
        t_the_run_end_names_each_unresolved_refusal,
        t_the_stop_hook_keeps_the_run_until_each_refusal_is_resolved,
        t_the_file_door_refuses_records_and_writes_nothing,
        t_per_ruling_alone_is_not_the_owner,
        t_the_spawn_door_has_the_same_gate,
        t_did_it_reads_git_at_the_door,
        t_each_program_that_files_names_itself,
        t_a_test_with_the_real_state_files_as_no_run,
        t_a_unit_a_test_inherited_from_its_run_is_no_run,
    )
    for fn in tests:
        print(fn.__name__)
        try:
            fn()
        except Exception as e:  # noqa: BLE001
            check("%s (raised %s: %s)" % (fn.__name__, type(e).__name__, str(e)[:300]), False)
    shutil.rmtree(TMP, ignore_errors=True)
    print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
