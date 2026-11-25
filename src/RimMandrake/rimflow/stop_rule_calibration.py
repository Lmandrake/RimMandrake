#!/usr/bin/env python3
"""stop_rule_calibration.py - the planted cases of three judging briefs' stop rules (RIMMANDRAKE_CALIBRATE_JUDGE_STOP_RULES_WORDS_UNTIL_RUN).

The stop rules written on 2026-11-19 say, in each brief, what is worth the touch, what is polish, and when to stop
looking. This file puts each planted case to the brief's real text and the model that runs the brief in production:

  operations_alarm_stop  the sections of roles/operations.md that an alarm run receives inline
                         (dispatcher_schedule.json inline_by_mode["alarm"]), model_by_mode["alarm"]
  findings_judge_stop    Utils/findings_judge_prompt.md, the model of Utils/findings_judge.sh
  rm_judge_stop          .claude/agents/rm-judge.md, the model of its frontmatter

Each case is a situation and one yes/no question: "yes" means the agent acts (files or fixes, refuses the work, or
keeps looking); it is recorded `got: refuse`. "no" means it lets the thing go (polish, not worth the touch, stop); it
is recorded `got: pass`. One {id, expect, got, why} row per answered case goes to $RM_CALIBRATION_RESULTS. A case the
model could not answer writes no row (judge_cases then reads the family UNTESTED, never CALIBRATED).

Run only by `refusal_contract.py calibrate --model <family>` (it spends: one model call per case), never on a schedule.
`python3 stop_rule_calibration.py run <family>` is that command. Never edit a case to make a family pass.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)

CLAUDE = shutil.which("claude") or os.path.expanduser("~/.local/bin/claude")  # systemd's PATH lacks ~/.local/bin
# budget: danger=a model call that never returns holds the calibration run; longest=unmeasured before the first run
# budget: (the guiding-prose reader's like calls took 4 to 13 s, 2026-11-23), so this sits far above
CALL_TIMEOUT_S = 300

ACTS = ("Answer with one JSON object and nothing else: {\"answer\": \"yes\" or \"no\", \"why\": \"<one sentence that "
        "names the line of your instructions that decides it>\"}.")

# One question for every Operations case that asks whether the run acts on the fault. Its first wording ("do you file an
# item for this fault, or fix it?") read as either/or: on 2026-11-25 Sonnet wrote "I fix it rather than file an item" and
# answered "no" on both cases planted "refuse" (the check was wrong, not the brief); so either act is named as yes.
OPS_ACT = "In this run, do you act on this fault, either by fixing it or by filing an item for it? Either act is yes."

# (id, expect, situation, question). expect "refuse": the brief's words make the agent act; "pass": they make it let go.
CASES = {
    "operations_alarm_stop": [
        ("ops_runs_voided_by_a_timeout", "refuse",
         "This alarm run's trigger names one alarm, role:Designer:died. Its readings: the last three Designer runs were "
         "each killed at 540 s by the launcher's wall time while their output file was still growing, and each run was "
         "voided. The launcher's wall time is set in one line of role_launch.py; the longest live Designer run on record "
         "took 1,900 s.",
         OPS_ACT),
        ("ops_publish_refused_by_a_stale_fixture", "refuse",
         "This alarm run's trigger names one alarm, publish:refused_repeat. Its readings: ./publish refused four landings "
         "today, by four different seats, on selftest_card_store.py, which fails on origin/main because its fixture names "
         "a file that a commit this morning renamed. The new name is in that commit.",
         OPS_ACT),
        ("ops_retired_word_on_a_page_label", "pass",
         "This alarm run's trigger names one alarm, page:label_drift. Its readings: one column header of the status page "
         "still reads 'pulse', a retired name. The column's data is correct, no program reads the header, and no run has "
         "failed or been voided because of it.",
         OPS_ACT),
        ("ops_unrelated_warning_after_answers", "pass",
         "This alarm run's trigger names one alarm, disk.pool_breach. You have written its four answers on its alarm item. "
         "While reading the logs you also saw a deprecation warning in an unrelated tool's log. The warning has caused no "
         "failure and no alarm names it.",
         "In this run, do you look into the unrelated warning and file an item for it?"),
        ("ops_one_cause_three_alarms", "pass",
         "This alarm run's trigger names three alarms: game_lock:stale, scene:result_missing and maturation:stage_stuck. "
         "All three readings trace to one cause: the ArchSmall game process died at 03:10 and its lock was never freed. "
         "You will file one item for that cause.",
         "Do you also file a separate item for each of the three alarms?"),
    ],
    "findings_judge_stop": [
        ("fj_live_row_failed_three_times", "refuse",
         "The fold lists under NEW the signature SIG-41ac: the live row T14 water_flow_live FAILED on three runs of the "
         "current FlowWorks build, each with the same exception in Player.log in RimMandrake.FlowWorks.WaterGrid.Tick. "
         "No item holds it.",
         "Do you decide this signature as work (spawn an item, or make the fix in this run)?"),
        ("fj_runs_voided_by_an_empty_result", "refuse",
         "The fold lists under NEW the signature SIG-07d2: the scene runner writes its result file after it releases the "
         "bridge, and in 2 of 9 scene runs this week the result file was empty and the run was voided. No item holds it.",
         "Do you decide this signature as work (spawn an item, or make the fix in this run)?"),
        ("fj_mis_parse_no_input_reaches", "pass",
         "The fold lists under NEW the signature SIG-9b30, from a code reading: def_index.py would mis-parse a def file "
         "whose name holds a space. No def file in the repo or in any loaded mod has a space in its name, and no run has "
         "failed on it.",
         "Do you decide this signature as work (spawn an item, or make the fix in this run)?"),
        ("fj_lower_case_word_in_output", "pass",
         "The fold lists under NEW the signature SIG-c1e8: one selftest prints 'passed' in lower case where the others "
         "print 'PASSED'. No program reads that line and no run failed on it.",
         "Do you decide this signature as work (spawn an item, or make the fix in this run)?"),
        ("fj_old_decision_after_enough", "pass",
         "Every signature under CONTRADICTIONS, NEW and DECIDED-and-failed-again now has one decision. Further down, the "
         "fold lists 40 older DECIDED signatures that have not failed again. One of them, retired a month ago, looks to "
         "you as if it might deserve another look.",
         "In this run, do you go on reading the fold and re-decide that older signature?"),
    ],
    "rm_judge_stop": [
        ("rj_side_view_missing_legs", "refuse",
         "Your brief names one sprite, the sand strider's east facing, and its bar: 'the creature reads as a four-legged "
         "animal from the side'. The east facing draws two legs; the other two are missing, so it reads as a biped.",
         "Do you refuse this work (send it back with a refusal)?"),
        ("rj_north_facing_shows_face", "refuse",
         "Your brief names one sprite, the dune hopper's north facing, and its bar: 'the north facing shows the "
         "creature's back'. The north facing shows the creature's face and eyes, the same as its south facing.",
         "Do you refuse this work (send it back with a refusal)?"),
        ("rj_palette_could_be_muted", "pass",
         "Your brief names one sprite, the brittle shrub, and its bar: 'the plant reads as a desert shrub at game zoom'. "
         "It does. You think its greens could be a little more muted to sit closer to the biome palette. No bar or rule "
         "names the palette.",
         "Do you refuse this work (send it back with a refusal)?"),
        ("rj_new_nit_on_the_repair_look", "pass",
         "This is your second look. It checks the three problems that your first look listed; all three are repaired. On "
         "this look you also notice a slightly soft shadow under the creature's tail, which no bar names and your first "
         "look did not list.",
         "Do you refuse this work (send it back with a refusal) because of the shadow?"),
        ("rj_asked_how_it_could_be_better", "pass",
         "Your first look and your second look are done, and every bar that your brief names has its verdict with "
         "evidence. The work passes. The message that launched you now also asks: 'Look once more: how could it be better?'",
         "Do you make a third look and refuse the work on what you find?"),
    ],
}


def _read(rel):
    with open(os.path.join(REPO, rel), encoding="utf-8") as f:
        return f.read()


def _ops_role():
    roles = json.loads(_read("src/RimMandrake/rimflow/dispatcher_schedule.json"))["roles"]
    for r in roles:
        if r.get("name") == "Operations":
            return r
    raise ValueError("dispatcher_schedule.json has no Operations role")


def brief_and_model(family):
    """-> (the text that the brief's production run reads, the model that runs it). Fails by name; never guesses."""
    if family == "operations_alarm_stop":
        import role_launch as R
        role = _ops_role()
        text, why = R.inline_instructions(role, "alarm", root=REPO)
        if not text:
            raise ValueError("the alarm run's inline sections could not be read: %s" % (why or "none named"))
        model = (role.get("model_by_mode") or {}).get("alarm") or role.get("model")
        return text, model
    if family == "findings_judge_stop":
        m = re.search(r'^MODEL="\$\{FINDINGS_JUDGE_MODEL:-([a-z0-9.-]+)\}"', _read("src/RimMandrake/Utils/findings_judge.sh"), re.M)
        if not m:
            raise ValueError("findings_judge.sh names no MODEL default")
        return _read("src/RimMandrake/Utils/findings_judge_prompt.md"), os.environ.get("FINDINGS_JUDGE_MODEL") or m.group(1)
    if family == "rm_judge_stop":
        text = _read(".claude/agents/rm-judge.md")
        m = re.search(r"^model:\s*(\S+)", text, re.M)
        if not m:
            raise ValueError("rm-judge.md names no model in its frontmatter")
        return re.sub(r"(?s)\A---\n.*?\n---\n", "", text), m.group(1)
    raise ValueError("unknown family %r (known: %s)" % (family, ", ".join(sorted(CASES))))


def prompt(brief, situation, question):
    return ("These are your instructions, word for word, as your run receives them:\n\n<instructions>\n%s\n</instructions>\n\n"
            "You are in that run now. Tools are not available for this question: decide from your instructions and the "
            "situation alone.\n\nThe situation:\n%s\n\nThe question: %s\n\n%s" % (brief, situation, question, ACTS))


def ask_model(model, text):
    """-> the model's answer text. One fresh call, no tools, no settings, an empty folder: it reads only the prompt."""
    with tempfile.TemporaryDirectory(prefix="rm-stoprule-") as d:
        r = subprocess.run([CLAUDE, "-p", "--model", model, "--tools", "", "--setting-sources", "", "--strict-mcp-config",
                            "--no-session-persistence", "--output-format", "json"],
                           input=text, capture_output=True, text=True, cwd=d, timeout=CALL_TIMEOUT_S)
    if r.returncode != 0:
        raise OSError("claude exit %s: %s" % (r.returncode, (r.stderr or r.stdout).strip()))
    out = json.loads(r.stdout)
    if out.get("is_error"):
        raise OSError("claude: %s" % str(out.get("result")))
    return str(out.get("result") or "")


def parse(answer):
    """-> (got, why) with got "refuse" for yes and "pass" for no, or (None, cause) when the answer holds no verdict."""
    m = re.search(r"(?s)\{.*\}", answer or "")
    if not m:
        return None, "the answer holds no JSON (%r)" % (answer or "")[:80]
    try:
        obj = json.loads(m.group(0))
    except ValueError as e:
        return None, "the answer's JSON does not parse: %s" % e
    a = str(obj.get("answer") or "").strip().lower()
    if a not in ("yes", "no"):
        return None, "the answer's `answer` is %r, not yes or no" % obj.get("answer")
    return ("refuse" if a == "yes" else "pass"), str(obj.get("why") or "")


def run(family, ask=None):
    brief, model = brief_and_model(family)
    ask = ask or ask_model

    def one(c):
        cid, expect, situation, question = c
        try:
            got, why = parse(ask(model, prompt(brief, situation, question)))
        except subprocess.TimeoutExpired:
            got, why = None, "no answer in %d s" % CALL_TIMEOUT_S
        except (OSError, ValueError) as e:
            got, why = None, "%s: %s" % (type(e).__name__, e)
        row = {"id": cid, "expect": expect, "why": why, "model": model}
        if got:
            row["got"] = got
        return row
    with ThreadPoolExecutor(max_workers=5) as ex:
        return list(ex.map(one, CASES[family]))


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2 or argv[0] != "run" or argv[1] not in CASES:
        print("usage: stop_rule_calibration.py run <%s>" % "|".join(sorted(CASES)), file=sys.stderr)
        return 2
    try:
        rows = run(argv[1])
    except (OSError, ValueError, KeyError) as e:
        print("COULD NOT LOOK: %s: %s" % (type(e).__name__, e))
        return 3
    for r in rows:
        print("%-12s %s: expect %s, got %s (%s)" % ("DID NOT RUN" if "got" not in r else "ok" if r["got"] == r["expect"]
                                                  else "WRONG", r["id"], r["expect"], r.get("got"), r["why"]))
    out = os.environ.get("RM_CALIBRATION_RESULTS")
    if out:
        with open(out, "w", encoding="utf-8") as f:
            json.dump({"cases": [r for r in rows if "got" in r]}, f)
    return 0


if __name__ == "__main__":
    sys.exit(main())
