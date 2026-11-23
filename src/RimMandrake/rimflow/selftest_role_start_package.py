#!/usr/bin/env python3
"""selftest_role_start_package.py — an Operations run starts with only what Operations needs
(RIMMANDRAKE_SLIM_OPERATIONS_START_PACKAGE_HALF_IS_UNRELATED; owner by card 2026-11-19, "Slim the start package" and
"Trim waste inside a run").

Covered, all offline (no claude, no unit, nothing written outside a temp dir):
  flags     the Operations schedule row carries the three narrowing launch flags (the item's acceptance line) and
            slim_start; launch_argv puts them on the claude argv
  settings  a slim_start run's --settings exclude the owner's personal CLAUDE.md and turn auto-memory off, and still
            carry the stop-channel PostToolUse hook; a role without slim_start gets the hook only
  hooks     each seat hook (SessionStart set_session_title; UserPromptSubmit set_session_title,
            conductor_goodbye) prints nothing for a launched run (RM_ROLE_UNIT set) and still prints for the
            Conductor window (no RM_ROLE_UNIT): no CONDUCTOR title, no OWED line, no identity in a role run
  inline    every inline_by_mode heading of every role resolves to exactly one section of its instructions; an alarm
            run and an incident-only run get their own sections and are told not to open the file; a full run is
            told to read it; a heading the file lacks reads INLINE INSTRUCTIONS UNAVAILABLE, never a silent drop
  scope     launch_scope: an incident-only run is "incident", one that covers a slot is that slot's mode
  owed      the Conductor window's OWED line with no ledger to read says "did not run", never "OWED 0" (owed.py)
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import role_launch as RL  # noqa: E402

FAILS = []
COUNT = [0]
FLAGS = ("--exclude-dynamic-system-prompt-sections", "--disable-slash-commands", "--strict-mcp-config")
HOOKS = os.path.join(ROOT, ".claude", "hooks")
UNIT = "rm-role-operations-probe-1"


def check(ok, what):
    COUNT[0] += 1
    print(("PASS  " if ok else "FAIL  ") + what)
    if not ok:
        FAILS.append(what)


def schedule():
    with open(os.path.join(HERE, "dispatcher_schedule.json"), encoding="utf-8") as fh:
        return json.load(fh)


def ops():
    return [r for r in schedule()["roles"] if r.get("name") == "Operations"][0]


def test_flags():
    op = ops()
    n = sum(f in op.get("launch_args", []) for f in FLAGS)
    check(n == 3, "Operations launch_args carry %d of 3 launch flags" % n)
    check(op.get("slim_start") is True, "Operations sets slim_start true")
    RL.validate_role(dict(op, clone="/tmp/x"))
    argv = RL.launch_argv(dict(op, clone=ROOT), UNIT, "msg", "/tmp/o", "/tmp/e", "/usr/bin/claude")
    check(all(f in argv for f in FLAGS), "launch_argv puts all three flags on the claude argv")


def _settings(role):
    argv = RL.launch_argv(dict(role, clone=ROOT), UNIT, "msg", "/tmp/o", "/tmp/e", "/usr/bin/claude")
    return json.loads(argv[argv.index("--settings") + 1])


def test_settings():
    s = _settings(ops())
    user_md = os.path.join(os.path.expanduser("~"), ".claude", "CLAUDE.md")
    check(user_md in (s.get("claudeMdExcludes") or []), "a slim run excludes %s" % user_md)
    check(s.get("autoMemoryEnabled") is False, "a slim run turns auto-memory off")
    check(bool((s.get("hooks") or {}).get("PostToolUse")), "a slim run keeps the stop-channel PostToolUse hook")
    check(not any(os.path.basename(p) == "CLAUDE.md" and os.path.dirname(p) == ROOT for p in s["claudeMdExcludes"]),
          "the project CLAUDE.md is not excluded")
    plain = _settings(dict(ops(), slim_start=False))
    check("claudeMdExcludes" not in plain and "autoMemoryEnabled" not in plain and plain.get("hooks"),
          "a role without slim_start gets the stop-channel hook only")
    try:
        RL.validate_role(dict(ops(), clone="/tmp/x", slim_start="yes"))
        check(False, "validate_role refuses a non-bool slim_start")
    except ValueError:
        check(True, "validate_role refuses a non-bool slim_start")


def _hook(script, event, prompt, launched, tmp):
    env = {k: v for k, v in os.environ.items() if k != "RM_ROLE_UNIT"}
    env.update(CLAUDE_PROJECT_DIR=tmp, AGENT_SEAT="BENCH")
    if launched:
        env["RM_ROLE_UNIT"] = UNIT
    payload = {"hook_event_name": event, "session_id": "probe-start-package-0001", "cwd": tmp,
               "prompt": prompt, "source": "startup"}
    r = subprocess.run([sys.executable, os.path.join(HOOKS, script)], input=json.dumps(payload),
                       capture_output=True, text=True, env=env, timeout=90)
    return r.returncode, r.stdout


def test_hooks():
    """Every seat hook named in the item's spec step 2, both ways. set_session_title writes its role file into
    CLAUDE_PROJECT_DIR, so the hooks run against a temp project holding a copy of infrastructure/agents."""
    tmp = tempfile.mkdtemp(prefix="rsp-")
    try:
        shutil.copytree(os.path.join(ROOT, "infrastructure", "agents"), os.path.join(tmp, "infrastructure", "agents"))
        os.makedirs(os.path.join(tmp, ".claude", "session_roles"))
        cases = [("set_session_title.py", "SessionStart", "", "CONDUCTOR"),
                 ("set_session_title.py", "UserPromptSubmit", "check the alarms", "CONDUCTOR"),
                 ("conductor_goodbye.py", "UserPromptSubmit", "check the alarms", "OWED")]
        for script, event, prompt, mark in cases:
            rc, out = _hook(script, event, prompt, True, tmp)
            check(rc == 0 and out.strip() == "", "%s %s prints nothing for a launched run (%r)" % (script, event, out[:80]))
            role_files = os.listdir(os.path.join(tmp, ".claude", "session_roles"))
            check(role_files == [], "%s %s writes no role file for a launched run (%r)" % (script, event, role_files))
        for script, event, prompt, mark in cases:
            rc, out = _hook(script, event, prompt, False, tmp)
            check(rc == 0 and mark in out, "%s %s still prints %s for the Conductor window (%r)" % (
                script, event, mark, out[:80]))
        print("hooks covered: %d (set_session_title x2 events, conductor_goodbye), both ways" % len(cases))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


READING = {"runway": 2.0, "runway_m": "MEASURED", "week_left": 50.0, "week_left_m": "MEASURED", "at": "now"}


def _prompt(role, mode, scope, root=None):
    return RL.prompt(role, mode, "t", READING, 0, 0, 0, UNIT, rows=["- row"], scope=scope, root=root)


def test_inline():
    for r in schedule()["roles"]:
        for scope, heads in (r.get("inline_by_mode") or {}).items():
            text, cause = RL.inline_instructions(r, scope)
            check(text and cause is None, "%s inline_by_mode[%s]: all %d headings resolve in %s (%s)" % (
                r.get("name"), scope, len(heads), r.get("instructions"), cause))
    op = ops()
    alarm = _prompt(op, "alarm", "alarm")
    check("Do not open that file" in alarm and "## Alarm runs" in alarm and "## Run hygiene" in alarm
          and "## The economy pass" not in alarm and "## The running check" not in alarm,
          "an alarm run gets its own sections inline and is told not to open the file")
    inc = _prompt(op, "run", "incident")
    check("Do not open that file" in inc and "## The running check" in inc and "**Incident runs.**" in inc
          and "## Alarm runs" not in inc and "## The economy pass" not in inc,
          "an incident-only run gets the running check (step 0, Incident runs) inline, not the alarm or economy text")
    full = _prompt(op, "run", "run")
    check("Read %s and do what it says" % op["instructions"] in full and "## Run hygiene" not in full,
          "a full run is told to read the file, nothing inlined")
    tmp = tempfile.mkdtemp(prefix="rsp-")
    try:
        os.makedirs(os.path.join(tmp, os.path.dirname(op["instructions"])))
        with open(os.path.join(tmp, op["instructions"]), "w", encoding="utf-8") as fh:
            fh.write("# x\n\n## Split of work\n\nonly this\n")
        broken = _prompt(op, "alarm", "alarm", root=tmp)
        check("INLINE INSTRUCTIONS UNAVAILABLE" in broken and "matches 0 sections" in broken
              and "Read %s and do what it says" % op["instructions"] in broken,
              "a missing heading reads INLINE INSTRUCTIONS UNAVAILABLE, names it, and sends the run to the file")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    try:
        RL.validate_role(dict(op, clone="/tmp/x", inline_by_mode={"alarm": []}))
        check(False, "validate_role refuses an empty inline heading list")
    except ValueError:
        check(True, "validate_role refuses an empty inline heading list")


def test_scope():
    check(RL.launch_scope({"mode": "run", "incident": {"cap": 1}}) == "incident", "an incident-only run is scope incident")
    check(RL.launch_scope({"mode": "economy", "incident": {"cap": 1}, "covers": "07:30"}) == "economy",
          "an incident run that covers a slot takes that slot's mode")
    check(RL.launch_scope({"mode": "alarm"}) == "alarm", "an alarm run is scope alarm")


def test_owed_blind():
    """The Conductor window's OWED line, run where there is no ledger, says it could not look; never OWED 0."""
    P = json.dumps({"hook_event_name": "UserPromptSubmit", "prompt": "x", "session_id": "s"})
    env = {k: v for k, v in os.environ.items() if k not in ("RM_ROLE_UNIT", "RIMFLOW_LEDGER")}
    tmp = tempfile.mkdtemp(prefix="rsp-")
    try:
        r = subprocess.run([sys.executable, os.path.join(HOOKS, "conductor_goodbye.py")], input=P, capture_output=True,
                           text=True, env=dict(env, CLAUDE_PROJECT_DIR=tmp, AGENT_SEAT="BENCH"), timeout=90)
        check("did not run" in r.stdout and "no ledger at" in r.stdout and "OWED 0" not in r.stdout,
              "no ledger reads 'OWED view did not run (no ledger at ...)', not OWED 0 (%r)" % r.stdout[:90])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    r = subprocess.run([sys.executable, os.path.join(HOOKS, "conductor_goodbye.py")], input=P, capture_output=True,
                       text=True, env=dict(env, CLAUDE_PROJECT_DIR=ROOT, AGENT_SEAT="BENCH"), timeout=90)
    check(r.stdout.startswith("OWED ") and "did not run" not in r.stdout,
          "the real ledger still reads an OWED count (%r)" % r.stdout[:60])


def main():
    for t in (test_flags, test_settings, test_hooks, test_inline, test_scope, test_owed_blind):
        try:
            t()
        except Exception as e:  # noqa: BLE001 - a crash is a failure with its cause, never a pass
            check(False, "%s crashed: %s: %s" % (t.__name__, type(e).__name__, e))
    print("%s %d of %d checks" % ("FAIL" if FAILS else "PASS", COUNT[0] - len(FAILS), COUNT[0]))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
