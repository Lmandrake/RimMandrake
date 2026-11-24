#!/usr/bin/env python3
"""coverage_judge.py - the Designer's stage-5 coverage signer: a fresh Opus run that did not make the tree judges whether
the frozen tree, sheet and scenes cover the concept, and this program signs on its verdict.

Item CONCEPT_LOCK_UNBLOCK_SIGNER_NEVER_CALLED (owner 2026-11-05, "Go ahead.", on the Conductor's proposal to retire the
Arbiter): the lock wanted an Arbiter signature and nothing ever started an Arbiter on a concept. Now the role launcher
runs `coverage_judge.py run <dir>` as the pre-launch step of every Designer run on a concept at stage 5
(role_launch.decide_roles), so the signature is there before the Designer's lock run starts, or its verdict says why not.

  run    <dir> [--timeout S]   at stage 5, exam passed (or waived in his words), no valid signature yet: launch the judge,
                               write coverage_verdict.json, and sign (`concept_tree.sign --by CoverageJudge`) when it
                               says covered and the tree and sheet are unchanged since it started. Otherwise a no-op.
  status <dir>                 what `run` would do, nothing launched

The judge reads roles/designer_scene_contract.md, roles/designer_lock.md and the concept folder; it never sees the
Designer's run transcripts, token figures or why the concept was picked. It answers through --json-schema, so a missing or
malformed verdict signs nothing. Its tokens are charged to the concept (designer_stage charge --kind review).

The first look lists every gap (DESIGNER_GAPJUDGE_FIX_ONE_BATCH_PER_ROUND: Pyrelands' judge named 8 gaps, then 6 different ones,
each batch costing a write, exam and judge cycle; 9.3M tokens, 8 chained runs in a day). The verdict carries a checklist
with a row for every inventory capability and tree leaf, each row naming every built part and the scene that tests it. A
missing row is re-asked once in the same session and still missing is kept in `unchecked` (a covered verdict with one
never signs); a failed part no gap names becomes a gap. The second look checks the repairs (owner by card 2026-11-17,
design/specs/2026-11-17-judge-flaws-not-polish/6_proposed_ruling_plain.md rule 2), by the same-problem rule
(7_same_problem_rule.md, settled 2026-11-18): every earlier gap is a numbered slot the judge answers in `repairs`; a slot
closes only when its answer says repaired, its rows this look read ok and no finding names it, and an open slot blocks as
it was first written. Any other new finding blocks only when it quotes a passage a repair changed (present in exactly one
of the entry's stored renderings, before and after), is a `problem` and the second reader confirms it; otherwise it is
advisory, on the owner's short list. A failed attempt keeps the last usable verdict as its `baseline`.

A passing bar is an experience (RIMMANDRAKE_TEACH_JUDGES_BARS_HOLD_NO_TUNING_NUMBERS, owner 2026-11-16; bar_rule.py):
every gap carries a `bar_kind`, and only an `experience` gap blocks. A gap that pins a tuning number, an asset-variant
count or a def's declared field (its own word, or the bar_rule detector's on its demand), and a `late` gap (new at a later
look) unless it quotes a passage a repair changed and is a serious Problem the second reader confirms (owner by card
2026-11-16, point 26, narrowed by his trial of 2026-11-17: a new gap on unchanged material never blocks), is moved to
`advisory_gaps`: stored and shown, blocking nothing; a look left with no blocking gap is `covered`. The open search for
gaps the artifacts do not cite is round 1's only (owner by card 2026-11-16, point 14, "Open search in round 1 only"): a
later look checks that named gaps were repaired and that no change opened one, so the loop ends. The judge does not grade its own criterion: its
`criterion_verdict` is kept as `judge_criterion_verdict`, and the binding one comes from a second reader that did not
judge (one fresh Opus call over the blocking records, `second_read`; `criterion_by` says which). With no second read the
refusal is stored and shown only, and the Designer is not sent back.

  release <dir> --why TEXT     a concept stopped by the loop limit gets one more judge look; its refusal stops it
                               again

The loop limit (RIMMANDRAKE_STOP_COVERAGE_LOOP_AT_THIRD_REFUSAL): every verdict is a round in stage.json coverage_rounds
(judges charged before the limit existed count from the budget charges; a second reader's charge is its judge's, never
a round). The second not_covered, a fourth judge run or
judge spend past JUDGE_SPEND_MAX stops judging: the concept is blocked on REFUSAL_NOTHING_COULD_EVER_PASS, the alarm row is
raised (refusal_contract.py) and `run` exits 3, so the Designer's run never starts.

Parked for him (RIMMANDRAKE_PARK_UNATTENDED_DESIGNER_LOOPS, RIMMANDRAKE_CEIL_JUDGE_LOOPS_AT_TWICE_CAP; designer_stage
park): when he is away (designer_stage.owner_away) the second not_covered parks a concept that needs his answer, and a
loop whose charges since the first judge reach twice the cap parks it whoever is there. A park writes
park_summary.md for him and sets waiting_owner; `run` exits 3 while it stands, `release` refuses it, and only his
word or the Conductor's act on the item lifts it.

Exit: 0 for a no-op, a verdict or a refusal the Designer reads (the pre-launch step must not stop the Designer's run: its
stage-5 gate refuses without the signature anyway); 3 when judging is stopped (the run must not start); 2 for an
unreadable concept.
What this cannot do, said plainly: a verdict of "covered" is one model's judgment, not proof; RM_ROLE_UNIT is an
environment variable, so a writer who sets it by hand forges the ledger note too (an attributable line in git).
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import concept_tree as CT  # noqa: E402
import designer_stage as DS  # noqa: E402
import refusal_contract as RC  # noqa: E402
import pipeline_control as PC  # noqa: E402  one-line overrides of every count here (`pipe`)
import control as C  # noqa: E402  the granted look's account: reserve, settle, void, grant (`pipe`)
import bar_rule as BR  # noqa: E402
import fulltext  # noqa: E402
import spend_watchdog  # noqa: E402  (the hard spend stop, from outside the agent; owner 2026-11-16)

CLAUDE = shutil.which("claude") or os.path.expanduser("~/.local/bin/claude")  # systemd's PATH lacks ~/.local/bin (OPS_TIMER_REPAIR_PRXC)

VERDICT_FILE = "coverage_verdict.json"
TIMEOUT_S = 1500        # the judge's own wall bound; the Designer schedule's pre_launch_max_s holds it plus slack
MODEL = "opus"
READER_BUDGET_USD = 2   # the second reader of the refusals' criteria (second_read)
READER_TIMEOUT_S = 600
BUDGET_USD = 8          # hard spend stop per judge call (spend_watchdog.py, from outside: the judge is never told its spend; owner 2026-11-12: "Don't let any burn go to 90M this time ok?")
REASK_MIN_S = 120       # less judge time than this left: no re-ask, the missing rows go on file as unchecked
ROW_REASK_MAX = 2       # re-asks of only the broken refusal records; one still broken is kept on file as malformed
# The loop limit (RIMMANDRAKE_STOP_COVERAGE_LOOP_AT_THIRD_REFUSAL, spec 2026-11-12 refusal contract §3; two looks since
# the owner's card of 2026-11-17, rule 2: one full inspection, then one check of the repairs). EK's judge said
# not_covered 9 times in 3 h. The second not_covered on one concept, a 4th judge run, or judge spend past 4x the measured
# p90 stops judging: the concept is blocked on the alarm and the Designer's run never starts. `release` grants one look.
NOT_COVERED_LIMIT = 2
JUDGE_RUNS_MAX = 4
# weighted_v2 (role_launch.MODEL_PRICES). Measured 2026-11-12 in weighted_v1: 12 judge runs (EK 8, GimmeSomeSlack 2,
# Pyrelands 2), p90 751,818, median 706,708; converted 2026-11-16 at x0.911, the median v2/v1 of 50 judge sessions'
# transcripts (all Opus 5.5; min 0.789, max 0.970; D:\ClaudeWork\rimmandrake\weighted_v2\judge_v2.txt), so the stop
# keeps meaning the same real spend (RIMMANDRAKE_WEIGH_TOKENS_BY_MODEL_OPUS_INPUT_UNIT).
JUDGE_P90_TOKENS = 684906
JUDGE_SPEND_MAX = 4 * JUDGE_P90_TOKENS   # an unmeasured judge run counts at the p90, never at 0
# RIMMANDRAKE_EXTEND_VOID_TO_JUDGE_DESIGNER_AND_PILOT_COUNTERS (run_void.py; owner 2026-11-18: "I will not accept ANY
# system that pointlessly expends such statistical measurements based on failed system calls or behavior"): a round whose
# judge call died (no answer, a timeout, output that is no result of its own) is void_system. It is no run, no look, no
# spend and no malformed verdict for the caps; it is counted apart, and JUDGE_FAULT_LIMIT of them since the last release
# stop judging as a system fault (a judge that only dies is not left looping), never as a spent look.
SYSTEM_ERROR_RX = re.compile(r"did not answer|not a JSON result|TimeoutExpired|timed out", re.I)  # a round from before
JUDGE_FAULT_LIMIT = 2 * JUDGE_RUNS_MAX                                                            # error_kind existed
STOP_EXIT = 3               # `run` exit when stopped: the pre-launch chain ends and the Designer's claude never starts
UNIT_PREFIX = "rm-coverage-judge-"
# how a later round's gap stands against the earlier verdicts: first (round 1 only), unfixed (named before, still open),
# changed (new because an artifact changed since; `since` names it), regression (passed before, broken by a change),
# late (it was there before and the earlier judge missed it). The program tags `late` itself when the ids are new and
# the judge claims no change: a judge miss, counted in the round.
TAGS = ("first", "unfixed", "changed", "regression", "late")
# how bad a gap is (owner by card 2026-11-16, point 26): only a late gap's severity decides anything (bar_rule.blocks)
SEVERITIES = ("problem", "polish")
SEVERITY_TEXT = ("`problem` (a defect, or an experience a player would reject as strange or disappointing) or `polish` "
                 "(anything less)")
# The refusal record (RIMMANDRAKE_EMIT_REFUSAL_RECORDS_FROM_JUDGE_BRIEFS, refusal contract section 1): every gap is a
# refusal naming its evidence, what that evidence shows, what would pass, the smallest attainable fix and a verdict on the
# criterion itself. `run` checks it with refusal_contract.check before the round counts.
RECORD_FIELDS = ("evidence", "observed", "would_pass", "smallest_fix", "criterion_verdict", "criterion_why")
RECORD_PROPS = {"evidence": {"type": "array", "items": {"type": "string"}},
                "observed": {"type": "string"}, "would_pass": {"type": "string"},
                "smallest_fix": {"type": "object", "additionalProperties": False,
                                 "required": ["what", "attainable", "cost"],
                                 "properties": {"what": {"type": "string"}, "attainable": {"enum": ["yes", "no"]},
                                                "cost": {"enum": list(RC.COSTS)}}},
                "criterion_verdict": {"enum": list(RC.VERDICTS)}, "criterion_why": {"type": "string"}}
CONTRACT_FAMILY = "coverage_judge"
INPUT_FILES = ("sheet.md", "tree.json", "scenes.json", "floor.json", "exam.json", "record.json")
REST_CLAUSE = "rest"     # a gap about no single row: a showcase's claims, the sheet
REST_TEXT = "the sheet a player reads says what the tree tests, and every showcase's claims are exercised by a scene"
CONTRACT = True          # off only in a selftest of another rule; selftest_coverage_refusal_record tests it
MALFORMED_LIMIT = RC.MALFORMED_ALARM_AT   # malformed verdicts on one concept that stop judging: the brief FAILED
# The four rules (owner by card 2026-11-17, "Judge ruling -> Adopt the four rules (Recommended)"; plain text in
# design/specs/2026-11-17-judge-flaws-not-polish/6_proposed_ruling_plain.md). Rules 1 and 4 in every prompt, rule 2's
# first-look line in round 1 only and its repair-check line in every later look, rule 3 in RECORD_TEXT.
RULES_TEXT = (
    "You may refuse for only three reasons: a promise is not kept (the bar says orange and the evidence shows it is "
    "not orange); nobody would notice if a promise were broken (there is no test for it, or the test cannot fail), "
    "and then you describe the broken mod that would get through; or the test or the paperwork is itself wrong (a "
    "test that would fail a correct mod, or a file that says something false). "
    "Every refusal quotes the promise it rests on. Anything else is advice and does not block: \"prove it more "
    "thoroughly\", \"test more cases\", \"it could be better\", polish, tuning. "
    "Only the owner's promises must be proven. A \"must not read as\" line the Designer added is a tip for thinking "
    "of broken mods, never a separate thing that needs its own test, unless it is the owner's own words or the plain "
    "opposite of the promise.")
FIRST_LOOK = ("This is the one full inspection: list every gap now. The second look only checks the repairs, and after "
              "it judging stops.")
REPAIR_LOOK = ("This is the check of the repairs: decide whether each listed problem was fixed by reading the fix itself, "
               "never by whether a form was filed. Raise something new only when a repair itself broke something, and "
               "quote the changed passage.")
# The same-problem rule (7_same_problem_rule.md): how the repair check answers, in every later look's prompt.
REPAIR_HOW = ("Answer `repairs` with one row for EVERY earlier gap listed, by its number: `gap` (g1, g2, ...), `repaired` "
              "true only when you read the fix and it closes that hole, false otherwise, and `evidence` (the file and place "
              "you read). A listed gap still open is that gap: answer it false; if you also write a gap for it, tag it "
              "`unfixed` and put its number in `since`; it blocks as it was first written, and your new wording is kept "
              "as a note. Any other gap is new. A new gap blocks only when `since` holds the changed entry's key (as "
              "listed, e.g. scene:sc_wall or sheet:<heading>), a newline, then a passage of that entry copied verbatim "
              "that the repair added, altered or removed; you give it `severity` `problem`; and a second reader who did "
              "not judge confirms it. Any other new gap, including one on unchanged material, is advisory: it goes to the "
              "owner's short list and blocks nothing.")
RECORD_TEXT = (
    "\n\nEvery gap is a refusal record, as detailed as the evidence it refuses, with a path to pass: `evidence` lists "
    "the concept files it rests on (sheet.md, tree.json, scenes.json, floor.json, exam.json, record.json; `file:line` "
    "where a line decides it); `observed` says what that evidence shows, quoting at least one of its words; `would_pass` "
    "is the concrete result that would pass, checkable by a script or a fresh judge (not the clause restated, never "
    "'insufficient' or 'needs more work'); `smallest_fix` is the smallest change that reaches it (`what` names the "
    "files, scenes or leaves; `attainable` yes/no; `cost` edit, rerun, new instrument or owner); `criterion_verdict` "
    "is your opinion of the criterion itself: `sound`, `flawed` (wrong or ambiguous) or `unattainable` (nothing could "
    "ever pass it), with `criterion_why`, a sentence, whatever the verdict; it is kept as your opinion and binds "
    "nothing: a second reader who did not judge grades every criterion you refuse on, and a flawed or unattainable "
    "one goes to a neutral fixer, not back to the Designer. `bar_kind` says what the gap is about (bar rule above); "
    "`severity` says how bad it is: " + SEVERITY_TEXT + ". Each checklist row's `evidence` names the files its parts rest on, so every file "
    "you were given is cited by some row or gap. A refusal without these is itself refused and re-asked (only the "
    "broken records, at most twice); one still broken is kept on file as malformed and counts for nothing.\n\n"
    "A refusal binds only \"close this hole\". The numbers, day counts, wind bearings and methods you suggest are one "
    "way to close it, never a bar; the builder may close it another way. A number binds only if the owner said it. "
    "The mod itself is never changed to hit a test's number. "
    "`promise` quotes the owner's promise the refusal rests on, and `owner_said` is true only when every number and "
    "line the refusal binds on is in the owner's own words.")
SCHEMA = {"type": "object", "additionalProperties": False,
          "required": ["verdict", "checklist", "gaps", "reasons", "repairs"],
          "properties": {"verdict": {"enum": ["covered", "not_covered"]},
                         "checklist": {"type": "array", "items": {
                             "type": "object", "additionalProperties": False,
                             "required": ["id", "evidence", "parts"],
                             "properties": {"id": {"type": "string"},
                                            "evidence": {"type": "array", "items": {"type": "string"}},
                                            "parts": {"type": "array", "items": {
                                                "type": "object", "additionalProperties": False,
                                                "required": ["what", "scene", "ok"],
                                                "properties": {"what": {"type": "string"},
                                                               "scene": {"type": "string"},
                                                               "ok": {"type": "boolean"}}}}}}},
                         "gaps": {"type": "array", "items": {"type": "object", "additionalProperties": False,
                                                             "required": ["what", "where", "return_to", "ids",
                                                                          "new_since", "bar_kind", "severity",
                                                                          "promise", "owner_said"]
                                                             + list(RECORD_FIELDS),
                                                             "properties": dict(RECORD_PROPS, **{
                                                                 "bar_kind": {"enum": list(BR.BAR_KINDS)},
                                                                 "severity": {"enum": list(SEVERITIES)},
                                                                 "what": {"type": "string"},
                                                                 "where": {"type": "string"},
                                                                 "return_to": {"enum": [2, 3]},
                                                                 "ids": {"type": "array", "items": {"type": "string"}},
                                                                 "new_since": {"enum": list(TAGS)},
                                                                 "since": {"type": "string"},
                                                                 "late_why": {"type": "string"},
                                                                 "promise": {"type": "string"},
                                                                 "owner_said": {"type": "boolean"}})}},
                         "reasons": {"type": "string"},
                         # the repair check's numbered slots (7_same_problem_rule.md); round 1 answers []
                         "repairs": {"type": "array", "items": {
                             "type": "object", "additionalProperties": False,
                             "required": ["gap", "repaired", "evidence"],
                             "properties": {"gap": {"type": "string"}, "repaired": {"type": "boolean"},
                                            "evidence": {"type": "string"}}}}}}
GAPS_SCHEMA = {"type": "object", "additionalProperties": False, "required": ["gaps"],
               "properties": {"gaps": SCHEMA["properties"]["gaps"]}}   # the row re-ask: the broken records only


def required_ids(d, tree):
    """Every id the checklist owes a row: record.json's inventory, then the tree's leaves, in order, no repeats."""
    rows = []
    try:
        rec = DS.read_json(os.path.join(d, "record.json"))
    except DS.Refused:  # the pre-launch step must not stop the run; the judge is told to read it and will say so
        rec = None
    if isinstance(rec, dict):
        rows += rec.get("inventory") or []
    rows += tree.get("leaves") or []
    ids = [x.get("id") for x in rows if isinstance(x, dict) and isinstance(x.get("id"), str)]
    return list(dict.fromkeys(ids))


def missing_rows(ids, checklist):
    """The owed ids with no row, or a row naming no part: a row that lists nothing checked nothing."""
    seen = {r.get("id") for r in checklist if isinstance(r, dict) and r.get("parts")}
    return [i for i in ids if i not in seen]


def failed_part_gaps(checklist, gaps):
    """-> a gap for each failed part whose row no gap names, so a judge's own finding cannot fall out of the list."""
    named = {i for g in gaps if isinstance(g, dict) for i in g.get("ids") or []}
    out = []
    for r in checklist:
        if not isinstance(r, dict) or r.get("id") in named:
            continue
        for part in r.get("parts") or []:
            if isinstance(part, dict) and part.get("ok") is not True:
                out.append({"what": "no passing scene for: %s" % part.get("what"), "where": "%s, scene %s" % (
                    r.get("id"), part.get("scene") or "none"), "return_to": 3, "ids": [r.get("id")]})
    return out


def shape_errors(so, gaps_only=False):
    """-> what in a structured answer the program cannot read ([] = readable): every gap an object with list `ids`, and
    (a whole verdict) every checklist row an object with list `parts`. `repairs` is not checked here: a value that is not
    a list answers no slot (take), so every slot stays open. An answer that breaks this is recorded, never a crash."""
    errs = []
    for k, g in enumerate(so.get("gaps") or []):
        if not isinstance(g, dict):
            errs.append("gap %d is not an object" % (k + 1))
        elif not (isinstance(g.get("ids", []), list) and all(isinstance(i, str) for i in g.get("ids") or [])):
            errs.append("gap %d's ids is not a list of strings" % (k + 1))
        elif not isinstance(g.get("evidence", []), list):
            errs.append("gap %d's evidence is not a list" % (k + 1))
    if gaps_only:
        return errs
    for k, r in enumerate(so.get("checklist") or []):
        if not isinstance(r, dict):
            errs.append("checklist row %d is not an object" % (k + 1))
        elif not isinstance(r.get("id"), str):
            errs.append("checklist row %d's id is not a string" % (k + 1))
        elif not (isinstance(r.get("parts", []), list) and all(
                isinstance(q, dict) and isinstance(q.get("ok"), bool) for q in r.get("parts") or [])):
            errs.append("checklist row %s's parts are not objects each with a true/false ok" % r["id"])
    return errs


def prior_slots(prior):
    """The earlier gaps a later look answers, by number (7_same_problem_rule.md rule 1). A record kept on file as
    malformed counts for nothing: it is no slot, never carried and never reopened (it stays as `prior_malformed`)."""
    return [g for g in (prior or {}).get("gaps") or [] if isinstance(g, dict) and g.get("gid") and not g.get("malformed")]


def _usable(rec):
    """A verdict a later look may check against: covered or not_covered with no error. A covered word the program
    refused (a row missing, an input moved, a sign refused) is a failed attempt and keeps the baseline (rule 6)."""
    return isinstance(rec, dict) and rec.get("verdict") in ("covered", "not_covered") and not rec.get("error")


def prior_verdict(d):
    """The verdict an earlier judge left here, when it reached one. A failed attempt (an error, a timeout, a malformed
    answer) keeps the last usable verdict as its `baseline` (7_same_problem_rule.md rule 6), so a retry checks the
    same numbered gaps against the same hashes and texts."""
    try:
        rec = DS.read_json(os.path.join(d, VERDICT_FILE))
    except DS.Refused:
        return None
    import run_void     # a VOID judge's verdict is evidence on file, never the look the next one checks
    void = run_void.active()
    if _usable(rec) and rec.get("judge") not in void:
        return rec
    base = rec.get("baseline") if isinstance(rec, dict) else None
    return base if _usable(base) and base.get("judge") not in void else None


# Re-judge only what changed (RIMMANDRAKE_REJUDGE_ONLY_CHANGED_GAPS, owner fix D, OWNER.jsonl:1794527688430451936).
# Every verdict keeps a hash per judged entry and numbers its gaps g1..gN. After round 1 the Designer names the gaps it
# fixed in coverage_fixes.json ({"against": <that verdict's judge>, "claims": [{"gap": "g3", "evidence": "..."}]}); the
# next judge is shown only those gaps with their evidence and the entries whose hash changed, whole. A gap not claimed
# stays open, carried. A new gap on material that did not change counts only tagged late with `late_why`. Nothing
# claimed and nothing changed: no judge runs at all. A prior verdict with no hashes (or one that errored, left rows
# unchecked, advisory or covered) gets a full judge, which leaves hashes for the next. An advisory verdict waits until
# the brief is calibrated, then receives a full review because its checklist cannot supply a trusted delta baseline.
FIXES_FILE = "coverage_fixes.json"
SCHEMA["properties"]["gaps"]["items"]["properties"]["late_why"] = {"type": "string"}
ROW_KINDS = ("inv", "leaf", "rest")   # entry kinds whose id is a checklist row


def _read_text(d, name):
    try:
        with open(os.path.join(d, name), encoding="utf-8") as f:
            return f.read()
    except OSError:
        return None


def entries(d, read=None):
    """-> {key: entry} for everything the judge judges: record.json's inventory (inv:), decisions (dec:) and scope,
    tree.json's leaves (leaf:) and the rest of the tree (tree:rest, without its signature stamp), scenes.json's scenes
    (scene:), showcases (showcase:) and coverage_rest (rest:), floor.json, and sheet.md by `## ` section (sheet:).
    `read(name)` -> text or None (default: the concept folder; the measurement reads a commit)."""
    read = read or (lambda name: _read_text(d, name))
    out = {}

    def js(name):
        try:
            return json.loads(read(name) or "null")
        except ValueError:
            return None

    def add(prefix, rows, key="id"):
        for x in rows or []:
            if isinstance(x, dict) and isinstance(x.get(key), str):
                out["%s:%s" % (prefix, x[key])] = x

    rec = js("record.json")
    if isinstance(rec, dict):
        add("inv", rec.get("inventory"))
        add("dec", rec.get("decisions"))
        out["record:scope"] = rec.get("scope")
    tree = js("tree.json")
    if isinstance(tree, dict):
        add("leaf", tree.get("leaves"))
        out["tree:rest"] = {k: v for k, v in tree.items() if k not in ("leaves", "coverage")}
    sc = js("scenes.json")
    if isinstance(sc, dict):
        add("scene", sc.get("scenes"))
        add("showcase", sc.get("showcases"))
        add("rest", sc.get("coverage_rest"), "capability")
    out["floor"] = js("floor.json")
    # the exam is judged material too: a changed exam is seen by the delta plan (RIMMANDRAKE_HASH_EXAM_IN_DELTA_ENTRIES_CHANGE_UNSEEN)
    out["exam"] = js("exam.json")
    text = read("sheet.md")
    if text is not None:
        head, body, seen = "", [], {}

        def put(h, lines):
            # a repeated heading is keyed by its occurrence (`#2`, ...): the second no longer hides the first
            # (RIMMANDRAKE_KEY_REPEATED_SHEET_HEADINGS_SECOND_HID_FIRST); a heading met once keeps its plain key
            # a key already taken (a literal `A#2` heading after two `A`s, or before) takes the next free number
            seen[h] = seen.get(h, 0) + 1
            key = "sheet:%s" % h if seen[h] == 1 else "sheet:%s#%d" % (h, seen[h])
            while key in out:
                seen[h] += 1
                key = "sheet:%s#%d" % (h, seen[h])
            out[key] = "\n".join(lines)
        for line in text.splitlines():
            if line.startswith("## "):
                put(head, body)
                head, body = line[3:].strip(), []
            body.append(line)
        put(head, body)
    return out


def flat(s):
    return " ".join(str(s).split())


def entry_texts(d, read=None):
    """-> {key: the entry as the program renders it to a judge (a sheet section's text, else json.dumps with
    ensure_ascii False, as delta_prompt shows it), whitespace collapsed}. Stored on every verdict as `entry_text`, so the
    next look can tell a passage a repair changed from one that only sits in a changed entry."""
    return {k: flat(v if isinstance(v, str) else json.dumps(v, ensure_ascii=False))
            for k, v in entries(d, read).items()}


def entry_hashes(d, read=None):
    import hashlib
    return {k: hashlib.sha256(json.dumps(v, sort_keys=True).encode()).hexdigest()[:16]
            for k, v in entries(d, read).items()}


def number_gaps(gaps):
    for k, g in enumerate(gaps, 1):
        g["gid"] = "g%d" % k
    return gaps


def fix_claims(d, prior):
    """-> (claims, refused): the claims in coverage_fixes.json made against this prior verdict, each naming one of its
    gaps with evidence; the rest are refused with a reason (a stale file names another judge)."""
    try:
        f = DS.read_json(os.path.join(d, FIXES_FILE))
    except DS.Refused as e:
        return [], ["%s unreadable: %s" % (FIXES_FILE, e)]
    if not isinstance(f, dict):
        return [], []
    if f.get("against") != prior.get("judge"):
        return [], ["%s is against %s, not the last verdict's %s" % (FIXES_FILE, f.get("against"), prior.get("judge"))]
    gids = {g.get("gid") for g in prior_slots(prior)}
    ok, refused, seen = [], [], set()
    for c in f.get("claims") or []:
        gap = c.get("gap") if isinstance(c, dict) else None
        if not isinstance(gap, str) or gap not in gids:
            refused.append("claim %r names no gap of %s" % (gap, prior.get("judge")))
        elif not CT.txt(c.get("evidence")):
            refused.append("claim on %s has no evidence" % gap)
        elif gap not in seen:
            seen.add(gap)
            ok.append({"gap": gap, "evidence": str(c["evidence"])})
    return ok, refused


def delta_plan(d, prior, read=None):
    """-> None for a full judge, else what a delta judge is shown: the claimed gaps, the changed entry keys and their
    current entries, the checklist rows to redo, and the gaps carried open."""
    if not (isinstance(prior, dict) and prior.get("verdict") == "not_covered" and isinstance(prior.get("hashes"), dict)
            and not prior.get("error") and not prior.get("unchecked")
            and not prior.get("advisory") and not (prior.get("contract") or {}).get("advisory")
            and all(isinstance(g, dict) and g.get("gid") for g in prior.get("gaps") or [])):
        return None
    now_ents = entries(d, read)
    now_h = entry_hashes(d, read)
    old_h = prior["hashes"]
    changed = sorted(k for k in set(old_h) | set(now_h) if old_h.get(k) != now_h.get(k))
    claims, refused = fix_claims(d, prior)
    claimed = {c["gap"] for c in claims}
    gaps = prior_slots(prior)
    rows = []
    for c in claims:
        rows += next((g.get("ids") or [] for g in gaps if g.get("gid") == c["gap"]), [])
    for k in changed:
        kind, _, ident = k.partition(":")
        if kind in ROW_KINDS:
            rows.append(ident)
        elif kind == "scene":
            rows += [r.get("id") for r in prior.get("checklist") or [] if isinstance(r, dict) and any(
                isinstance(p, dict) and p.get("scene") == ident for p in r.get("parts") or [])]
        elif kind == "showcase" and isinstance(now_ents.get(k), dict):
            rows += [x for x in now_ents[k].get("exercises") or [] if isinstance(x, str)]
    return {"claims": claims, "refused": refused, "changed": changed, "against": prior.get("judge"),
            "prior_checklist": [r for r in prior.get("checklist") or [] if isinstance(r, dict)],
            "entries": {k: now_ents.get(k) for k in changed},
            "ids": [i for i in dict.fromkeys(rows) if isinstance(i, str)],
            "claimed_gaps": [g for g in gaps if g.get("gid") in claimed],
            "carried": [g for g in gaps if g.get("gid") not in claimed],
            "loose": any(not (g.get("ids") or []) for g in gaps if g.get("gid") in claimed)
            or any(k.partition(":")[0] not in ROW_KINDS for k in changed)}


def delta_prompt(d, repo, dp, round_no):
    rel = CT.concept_rel(d, repo)
    claims = {c["gap"]: c["evidence"] for c in dp["claims"]}
    body = ["You are the coverage judge for the RimMandrake concept at %s, on a re-judge: round %d. A previous judge "
            "listed its gaps; the Designer says it fixed some of them. You judge ONLY what is below. Read "
            "src/RimMandrake/rimflow/roles/designer_scene_contract.md (the proof-scene contract) first. Do not reread the "
            "concept's files whole: everything to judge is quoted here, and you open a file only at the place a claim's "
            "evidence names, to check it. Do not read result.*.json, log.md, stage.json or any transcript, and edit "
            "nothing. The second not_covered verdict stops judging." % (rel, round_no),
            "", RULES_TEXT, "", REPAIR_LOOK + " " + REPAIR_HOW,
            "", "## Gaps the Designer claims fixed (check each and answer its `repairs` row)"]
    for g in dp["claimed_gaps"]:
        body.append("- %s (ids %s; was: %s; at %s)\n  evidence: %s" % (
            g.get("gid"), ", ".join(g.get("ids") or []) or "none", g.get("what"), g.get("where"), claims[g["gid"]]))
    if not dp["claimed_gaps"]:
        body.append("(none)")
    body += ["", "## Entries changed since that verdict, whole (a gap a change opens is tagged `changed`, `since` "
             "naming the entry; one that breaks what passed is `regression`)"]
    for k in dp["changed"]:
        v = dp["entries"].get(k)
        body.append("- %s: %s" % (k, "REMOVED" if v is None else json.dumps(v, ensure_ascii=False)))
    if not dp["changed"]:
        body.append("(none)")
    body += ["", "## Gaps still open, carried on file. A carried gap is closed only when you write a row for "
             "every one of its ids this look and each is all ok; one you find still open, write its row with the part not "
             "ok. It also needs its `repairs` row to say repaired."]
    body += ["- %s: %s" % (g.get("gid"), " ".join(str(g.get("what") or "").split())) for g in dp["carried"]] or ["(none)"]
    body += ["", "Write `checklist` with one row for each of these ids, none skipped: %s. This is a later round, and "
             "the open search was round 1's: do not hunt for new gaps elsewhere. Answer `covered` only when every gap "
             "listed above is repaired and no repair broke anything.\n\nThe bar rule: %s" % (
                 ", ".join(dp["ids"]) or "(none)", BR.RULE_TEXT)]
    return "\n".join(body) + RECORD_TEXT


# The same-problem rule (design/specs/2026-11-17-judge-flaws-not-polish/7_same_problem_rule.md, settled 2026-11-18 after
# four Codex build rounds each lost on matching a second-look gap to a first-look one by its wording). The program never
# matches text: each earlier gap is a numbered slot the judge answers in `repairs`, and identity is the slot's number
# and rows. Unsure = open.
GID = re.compile(r"\bg\d+\b")


ENTRY_KINDS = ("inv", "dec", "record", "leaf", "tree", "scene", "showcase", "rest", "floor", "exam", "sheet")


def named_slots(g, gids):
    """The slots a finding names by number: the gap numbers in its `since` before any newline. An entry key, a newline
    and a passage (rule 4 (a)) is a citation: neither the key (a heading may hold `g1`) nor the quotation names a slot."""
    head, sep, _q = str(g.get("since") or "").partition("\n")
    if sep and head.strip().strip("`'\"").partition(":")[0] in ENTRY_KINDS:
        return set()
    return set(GID.findall(head)) & set(gids)
QUOTE_MIN = 12     # characters: a changed passage shorter than this proves nothing (an id, a word)


def _slots(slots, rows, repairs, seen):
    """Rules 1-3. slots: the earlier gaps (each with its gid); rows: the judge's OWN checklist this look; repairs: its
    `repairs` answer, or None for an answer in the old form (read by its rows, RIMMANDRAKE_CLOSE_CARRIED_GAPS_REPAIRED_
    WITHOUT_CLAIM_FORM); seen: every finding this look, kept or dropped. A finding names a slot by its number in `since`,
    or (tagged `unfixed`, a failed part, or any finding in the old form) by sharing its rows. A slot closes only
    when its answer says repaired (old form: no answer needed), every one of its ids has a row this look and every row
    on its ids is all ok, and nothing names it (RIMMANDRAKE_REQUIRE_PASSING_ROW_TO_CLOSE_REPAIRED_SLOT: a repaired
    answer with no row on its ids closed the slot, and coverage could sign). -> (closed, still open (with `second_look` notes), the findings that named a slot)."""
    by_id = {}
    for r in rows or []:
        if isinstance(r, dict):
            by_id.setdefault(r.get("id"), []).append(r)   # two rows on one id: every one of them must read ok

    def ok(r):
        return bool(r.get("parts")) and all(isinstance(q, dict) and q.get("ok") is True for q in r["parts"])
    gids = {g.get("gid") for g in slots}
    said = None
    if repairs is not None:
        said = {}
        for a in repairs:
            if isinstance(a, dict) and isinstance(a.get("gap"), str):   # two answers on one slot: both must say repaired
                said[a["gap"]] = said.get(a["gap"], True) and a.get("repaired") is True
    notes, naming = {}, []
    for g in seen:
        if not isinstance(g, dict):
            continue
        ids = {i for i in g.get("ids") or [] if isinstance(i, str)}
        named = named_slots(g, gids)
        if repairs is None or g.get("from_rows") or g.get("new_since") == "unfixed":
            named |= {sl.get("gid") for sl in slots if ids & set(sl.get("ids") or [])}
        for gid in named:
            notes.setdefault(gid, []).append({k: g.get(k) for k in ("what", "where", "ids", "observed", "new_since",
                                                                    "since") if g.get(k) not in (None, "", [])})
        if named:
            g["names_slot"] = sorted(named)
            naming.append(g)
    closed, still = [], []
    for sl in slots:
        ids = list(sl.get("ids") or [])
        readable = all(isinstance(i, str) for i in ids)   # an id that is not a row name could not be read: open
        rows_ok = readable and all(by_id.get(i) for i in ids) and all(ok(r) for i in ids for r in by_id.get(i) or [])
        if said is None:
            good = bool(ids) and rows_ok
        else:   # a slot with no ids has no row to require: its answer alone closes it (boundary page)
            good = said.get(sl.get("gid")) is True and rows_ok
        if good and sl.get("gid") not in notes:
            closed.append(sl)
        else:
            still.append(dict(sl, second_look=notes[sl["gid"]]) if sl.get("gid") in notes else sl)
    return closed, still, naming


def _answered(closed):
    return [{"gid": g.get("gid"), "ids": list(g.get("ids") or []), "what": g.get("what")} for g in closed]


def changed_passage(g, before, after):
    """Rule 4 (a): -> (entry key, passage) when g's `since` is an entry key, a newline and a passage of at least
    QUOTE_MIN characters present in exactly one of that entry's renderings before and after (entry_texts), else None.
    before None: the prior verdict stored no renderings, so nothing can be shown to have changed."""
    if not isinstance(before, dict):
        return None
    key, sep, q = str(g.get("since") or "").partition("\n")
    key = key.strip().strip("`'\"")
    if not sep or key not in set(before) | set(after or {}):
        return None
    b, a = str(before.get(key) or ""), str((after or {}).get(key) or "")
    for f in (lambda t: t, _unescape):   # as the prompt showed it (JSON escapes kept), and as the file reads
        qq, bb, aa = f(flat(q)).strip("`'\""), f(b), f(a)
        if len(qq) >= QUOTE_MIN and (qq in bb) != (qq in aa):
            return key, qq
    return None


def _unescape(t):
    return flat(t.replace("\\n", " ").replace('\\"', '"').replace("\\\\", "\\"))


def passage_state(g, before, after):
    """Why a new finding quotes no changed passage (counted by round_counts): `no_baseline` (the prior verdict kept no
    renderings: could not look), `unchanged` (its quote is in the entry both before and after) or `unshown` (no entry
    key and quote of at least QUOTE_MIN characters found in either)."""
    if not isinstance(before, dict):
        return "no_baseline"
    key, sep, q = str(g.get("since") or "").partition("\n")
    key = key.strip().strip("`'\"")
    b, a = str(before.get(key) or ""), str((after or {}).get(key) or "")
    for f in (lambda t: t, _unescape):
        qq = f(flat(q)).strip("`'\"")
        if sep and len(qq) >= QUOTE_MIN and qq in f(b) and qq in f(a):
            return "unchanged"
    return "unshown"


def classify_new(rec, before, after, refuser):
    """Rule 4 over this look's findings that named no slot. One the judge tagged `unfixed` ("still open") that points at
    no slot is an unplaced repair report: it stays and blocks. Any other new finding stays only when it quotes a changed
    passage (then it is `late`, the miss_of the last refuser, and blocks only as a confirmed `problem`, bar_rule.blocks);
    the rest is advisory, on the owner's short list."""
    keep, adv = [], []
    for g in rec.get("gaps") or []:
        if not isinstance(g, dict) or g.get("carried"):
            keep.append(g)
            continue
        if g.get("new_since") == "unfixed" and not g.get("from_rows"):
            g.update(unplaced=True)
            keep.append(g)
            continue
        cp = changed_passage(g, before, after)
        if cp:
            if g.get("new_since") != "late":
                g["judge_said"] = g.get("new_since")
            g.update(new_since="late", miss_of=refuser, repair_passage={"entry": cp[0], "passage": cp[1]})
            keep.append(g)
        else:
            adv.append(dict(g, short_list=True, miss_of=refuser, new_since="late", judge_said=g.get("new_since"),
                            passage=passage_state(g, before, after), advisory_why=(
                "a new finding at the check of the repairs that quotes no passage a repair changed: advisory, for the "
                "owner's short list (owner, 2026-11-17 trial; 7_same_problem_rule.md rule 4)")))
    rec["gaps"] = keep
    if adv:
        rec["advisory_gaps"] = list(rec.get("advisory_gaps") or []) + adv
    # every new finding's ids, blocking or advisory: the judge's misses and the repairs' breaks, counted per round
    late = list(dict.fromkeys(i for g in keep + list(rec.get("advisory_gaps") or []) if g.get("miss_of")
                              for i in g.get("ids") or [REST_CLAUSE]))
    if late:
        rec["late"] = late
    else:
        rec.pop("late", None)
    return rec


def reopen_named(rec, new, slots):
    """A record re-asked after the slots were read (the broken-row re-ask) that names a slot is that slot's note, never
    its own refusal, and a slot it names that had closed opens again (rule 2: anything calling it open keeps it open)."""
    by_gid = {s.get("gid"): s for s in slots if isinstance(s, dict)}
    for g in new:
        ids = {i for i in g.get("ids") or [] if isinstance(i, str)}
        named = named_slots(g, by_gid)
        if g.get("new_since") == "unfixed":
            named |= {gid for gid, s in by_gid.items() if ids & set(s.get("ids") or [])}
        if not named:
            continue
        rec["gaps"] = [x for x in rec.get("gaps") or [] if x is not g]
        note = {k: g.get(k) for k in ("what", "where", "ids", "observed", "new_since", "since") if g.get(k) not in (None, "", [])}
        for gid in sorted(named):
            held = next((x for x in rec["gaps"] if x.get("carried") and x.get("gid") == gid), None)
            if held is None:   # it had closed: open again, as first written
                rec["answered"] = [a for a in rec.get("answered") or [] if a.get("gid") != gid]
                held = dict(by_gid[gid], carried=True, new_since="unfixed")
                rec["gaps"].append(held)
            held["second_look"] = list(held.get("second_look") or []) + [note]
    if any(x.get("carried") for x in rec.get("gaps") or []) and rec.get("verdict") == "covered":
        rec["verdict"] = "not_covered"
    return rec


def rejudge_slots(rec, prior, repairs):
    """A full re-judge on a refusing prior verdict: every earlier gap is a slot (rules 1-3)."""
    slots = prior_slots(prior)
    closed, still, naming = _slots(slots, rec.get("checklist"), repairs, rec.get("gaps") or [])
    rec["gaps"] = [g for g in rec.get("gaps") or [] if not any(g is x for x in naming)] + [
        dict(g, carried=True, new_since="unfixed") for g in still]
    rec["answered"] = _answered(closed)
    return rec


def delta_merge(rec, dp, repairs=None):
    """Fold a delta judge's answer into a whole verdict: the gaps it found within what it was shown (plus late gaps
    with a why), every earlier gap (claimed or carried) its slot did not close (`_slots`), and the prior rows it did not
    redo. A slot left open keeps a covered word from standing; a closed one is listed in rec["answered"]."""
    scope = set(dp["ids"])
    kept, dropped = [], []
    for g in rec.get("gaps") or []:
        ids = set(g.get("ids") or [])
        # a change to shared material (floor, sheet, scope: no row of its own) can open a gap on any row: kept when the
        # judge tags it changed or regression (RIMMANDRAKE_KEEP_GAPS_OPENED_BY_SHARED_MATERIAL_CHANGES)
        # an `unfixed` report is never dropped: it names a slot, or it is an unplaced repair report (_slots, classify_new)
        if (ids & scope) or (not ids and dp["loose"]) or (g.get("new_since") == "late" and CT.txt(g.get("late_why"))) \
                or (dp["loose"] and g.get("new_since") in ("changed", "regression")) or g.get("new_since") == "unfixed":
            kept.append(g)
        else:
            dropped.append(dict(g, dropped="a new gap on material that did not change, not tagged late with a why"))
    slots = list(dp.get("claimed_gaps") or []) + list(dp["carried"])   # a claim decides what is shown, never a closure
    answered, still_open, naming = _slots(slots, rec.get("checklist"), repairs, kept + dropped)
    kept = [g for g in kept if not any(g is x for x in naming)]
    carried = [dict(g, carried=True, new_since="unfixed") for g in still_open]
    redone = {r.get("id") for r in rec.get("checklist") or [] if isinstance(r, dict)}
    rec["checklist"] = list(rec.get("checklist") or []) + [
        r for r in dp.get("prior_checklist") or [] if isinstance(r, dict) and r.get("id") not in redone]
    rec["gaps"] = kept + carried
    if dropped:
        rec["dropped"] = dropped
    if slots:   # absent = nothing was carried to read; [] = they were read and none closed
        rec["answered"] = _answered(answered)
    else:
        rec.pop("answered", None)   # a second answer in one session replaces the first: never a stale closure
    if carried and rec.get("verdict") == "covered":
        rec["verdict"] = "not_covered"
    return rec


READER_SUFFIX = "-reader"    # llm_reader's charge ref: its judge's unit + this


def void_cause(r):
    """-> why round (or verdict record) r is void_system, or "": its judge call died of a system cause (error_kind
    "system", or, on a round written before error_kind, an error SYSTEM_ERROR_RX names) with no verdict, or a re-ask of
    its refusal records died and left the verdict malformed (`void_system`). A judge's own failure (an answer with no
    well-formed verdict, a runner exit, its cap) is not void: it counts."""
    if not isinstance(r, dict):
        return ""
    if r.get("void_system"):
        return str(r["void_system"])
    err = r.get("error")
    if r.get("verdict") is not None or not err:
        return ""
    kind = r.get("error_kind")
    return str(err) if kind == "system" or (kind is None and SYSTEM_ERROR_RX.search(str(err))) else ""


def is_cli_result(res):
    """True when a parsed JSON object is the claude CLI's result of its own (the envelope: type "result", or the
    fields a result carries). {} or another envelope ({"type": "error", ...}) is not: that call died
    (Codex review r2-3)."""
    if res.get("type") not in (None, "result"):
        return False
    return res.get("type") == "result" or any(k in res for k in (
        "subtype", "is_error", "structured_output", "usage", "session_id", "result", "modelUsage"))


def rounds(st, d=None, readers_as_rounds=False, voids=False):
    """-> every judge round on this concept, oldest first: stage.json's coverage_rounds, plus each earlier judge the
    budget charges name with no round on file (before the loop limit existed). An old round's verdict is known only when
    coverage_verdict.json is that judge's; its tokens are its charges, or the p90 when it was charged unmeasured.
    A void_system round (void_cause) is left out, its reader's spend with it; voids=True keeps it, marked
    `void_system`, for the fault count and the views that show it apart."""
    import run_void     # a VOID judge's charges build no round (its spend stays measured: run_void.sync_stage)
    recorded = [dict(r) for r in st.get("coverage_rounds") or [] if isinstance(r, dict)]
    known = {r.get("judge") for r in recorded} | run_void.stage_spend_refs(st)
    last = prior_verdict(d) if d else None
    legacy, reader, reader_at = {}, {}, {}
    for c in (st.get("budget") or {}).get("charges") or []:
        ref = c.get("ref") if isinstance(c, dict) else None
        if isinstance(ref, str) and ref.startswith(UNIT_PREFIX) and ref.endswith(READER_SUFFIX) and not readers_as_rounds:
            # a second reader's charge (llm_reader) is its judge's spend, never a round (it was, until 2026-11-18:
            # Graffiti and LeaningScrub each read one phantom round)
            j = ref[:-len(READER_SUFFIX)]
            reader[j] = reader.get(j, 0) + (JUDGE_P90_TOKENS if c.get("kind") == "unmeasured" else int(c.get("tokens") or 0))
            reader_at[j] = max(str(c.get("at") or ""), reader_at.get(j, ""))
            continue
        if isinstance(ref, str) and ref.startswith(UNIT_PREFIX) and ref not in known:
            r = legacy.setdefault(ref, {"judge": ref, "at": c.get("at"), "verdict": None, "tokens": None,
                                        "unmeasured_calls": 0, "legacy": True})
            if c.get("kind") == "unmeasured":
                r["unmeasured_calls"] += 1
            else:
                r["tokens"] = (r["tokens"] or 0) + int(c.get("tokens") or 0)
    for r in legacy.values():
        if last and last.get("judge") == r["judge"]:
            r["verdict"] = last.get("verdict")
        if r["judge"].endswith(READER_SUFFIX):
            r["reader_phantom"] = True    # only when readers_as_rounds: the count an old release was written against
    out = sorted(legacy.values(), key=lambda r: str(r.get("at"))) + recorded
    for r in out:
        if reader.get(r.get("judge")):
            if r.get("reader_void_system"):     # its second reader died: that charge is void spend, shown apart
                r["reader_void_tokens"] = reader.pop(r["judge"])
            else:
                r["reader_tokens"] = reader.pop(r["judge"])
    for j in sorted(reader):   # a reader whose judge has no round on file: its spend still counts, on a spend-only row
        out.append({"judge": None, "verdict": None, "tokens": reader[j], "reader_only": True, "reader_of": j,
                    "at": reader_at.get(j) or None})
    for r in out:
        why = void_cause(r)
        if why:
            r["void_system"] = why
    return out if voids else [r for r in out if not r.get("void_system")]


def _round_spend(r):
    """One round's spend: its measured tokens plus the p90 for each call that ran and could not be measured
    (`unmeasured_calls`: a judge that never launched spent 0). A round written before that count with no measured
    token is one unmeasured call."""
    t, u = r.get("tokens"), r.get("unmeasured_calls")
    if not isinstance(u, int) or u < 0:
        u = 1 if t is None else 0
    return int(t or 0) + JUDGE_P90_TOKENS * u + int(r.get("reader_tokens") or 0)


def spend(rs):
    return sum(_round_spend(r) for r in rs)


def _looks(rs):
    """The judge runs among rounds(): a spend-only reader row is not a run."""
    return [r for r in rs if not r.get("reader_only")]


def released_rounds(st, d, rs, rel):
    """-> the rounds since the release `rel` (a coverage_releases row): by its judges_at list, or (a release written
    before 2026-11-18) by its rounds_at count with the phantom reader rounds. Shared by stop_reason and `pipe show`."""
    def after(r):   # an orphan reader's spend counts from the release when it was charged after it (unknown time: kept)
        return not (r.get("at") and rel.get("at")) or str(r["at"]) > str(rel["at"])
    if isinstance(rel.get("judges_at"), list):
        before = set(rel["judges_at"])
        return [r for r in rs if (after(r) if r.get("reader_only") else r.get("judge") not in before)]
    old = rounds(st, d, readers_as_rounds=True, voids=True)[int(rel.get("rounds_at") or 0):]   # the count it was written on
    keep = {r.get("judge") for r in old if not r.get("reader_phantom")}   # a phantom is dropped, never promoted
    return [r for r in rs if (after(r) if r.get("reader_only") else r.get("judge") in keep)]


def look_balance(st, d=None, rs=None, mod=None):
    """-> None when no release stands, else the granted look's account: {"mod", "win" (the accounting window: the grant's
    time), "refused" (the refusing looks since the release that are not voided), "used" (their count plus any `pipe add`
    override), "lim" (the one look a release grants, or its `pipe limit`, plus every `pipe grant <Mod> look +N` in the
    window)}, or {"error": "CONTROL UNREADABLE: ..."} when the store cannot be read (judging stops: a look nobody can
    account for is not given)."""
    rel = [x for x in st.get("coverage_releases") or [] if isinstance(x, dict)]
    if not rel:
        return None
    rs = rounds(st, d) if rs is None else rs
    mod = mod or (DS.concept_of(st, d) or {}).get("mod") or (os.path.basename(os.path.abspath(d)) if d else "?")
    refused = [r for r in _looks(released_rounds(st, d, rs, rel[-1])) if is_refusal(r)]
    win = C.look_window(st)
    try:
        gone = C.voided([r.get("judge") for r in refused])
        granted = C.account(mod, C.LOOK, win, 0)["granted"]
    except C.Unreadable as e:
        return {"mod": mod, "error": "CONTROL UNREADABLE: the control store cannot be read (%s): no granted look is "
                                     "given on it" % e}
    refused = [r for r in refused if r.get("judge") not in gone]
    base = PC.limit(mod, "granted_look", 1)
    return {"mod": mod, "win": win, "refused": refused, "used": PC.used(mod, "granted_look", len(refused)),
            "base": base, "lim": base + granted}


def since_signoff(rs):
    """-> the rounds after the last `covered` verdict among rs, or rs when none reads covered. A sign-off ends a run of
    strikes, looks and spend: the next refusal starts a new count (RIMMANDRAKE_RESET_COVERAGE_STRIKES_AFTER_SIGNOFF_OLD_
    TWO_COUNTED; Graffiti, rounds nc, nc, covered, nc, stopped on its first refusal after passing)."""
    last = max((i for i, r in enumerate(rs) if not r.get("reader_only") and r.get("verdict") == "covered"), default=-1)
    return rs[last + 1:]


def counting_window(st, d, rs):
    """-> (the release still standing or None, the rounds the strike, run and spend caps count, their since-label, the
    rounds the malformed cap counts, its since-label). The window starts at the later of the last release and the last sign-off; a sign-off
    after a release ends that release's one look. The malformed count is the brief failing its contract, not a look at
    the design, so a sign-off does not reset it: it counts from the release, as before. Shared with `pipe show`."""
    rel = [x for x in st.get("coverage_releases") or [] if isinstance(x, dict)]
    after = released_rounds(st, d, rs, rel[-1]) if rel else rs
    tail = since_signoff(after)
    bad_since = " since the release" if rel else ""
    if len(tail) < len(after):
        return None, tail, " since the sign-off", after, bad_since
    if rel:
        return rel[-1], after, " since the release", after, bad_since
    return None, rs, "", rs, bad_since


def is_refusal(r):
    """A round that counts as a refusal (a strike toward NOT_COVERED_LIMIT, a granted look's refusal, a park's second
    refusal): a not_covered verdict judged on the inputs that are still there. A not_covered whose inputs changed while
    the judge read them (`stale_inputs`) judged material that is gone: it is stored and shown and counts as no refusal
    (RIMMANDRAKE_REVALIDATE_INPUTS_BEFORE_REFUSAL_STALE_THIRD_STRIKE). Its run and spend still count in the caps."""
    return isinstance(r, dict) and r.get("verdict") == "not_covered" and not r.get("stale_inputs")


def moved_inputs(d, before):
    """-> the inputs (INPUT_FILES, "tree.json" for the tree or the sheet) that differ from fresh_key `before` now; []
    when none moved. A tree that cannot be read now has moved."""
    try:
        now = fresh_key(d, CT.load(d))
    except (OSError, ValueError) as e:
        return ["tree.json (unreadable now: %s)" % type(e).__name__]
    if now == before:
        return []
    moved = [fn for fn, h in before[2].items() if now[2].get(fn) != h]
    moved += [fn for fn, i in (("tree.json", 0), ("sheet.md", 1)) if now[i] != before[i] and fn not in moved]
    return moved


def stop_reason(st, d=None):
    """-> why judging stops on this concept now, or None. After a release, one more look: its refusal stops again (an
    error, a timeout or a malformed round is no look; the caps count them). A sign-off resets the counts
    (counting_window)."""
    rs = rounds(st, d)
    mod = (DS.concept_of(st, d) or {}).get("mod") or "?"
    rel = [x for x in st.get("coverage_releases") or [] if isinstance(x, dict)]
    every = rounds(st, d, voids=True)
    dead = [r for r in (released_rounds(st, d, every, rel[-1]) if rel else every) if r.get("void_system")]
    if len(dead) >= JUDGE_FAULT_LIMIT:
        return ("%d judge rounds%s died of a system cause (limit %d; the last: %s): a system fault, no look, run or "
                "spend was counted for them" % (len(dead), " since the release" if rel else "", JUDGE_FAULT_LIMIT,
                                                  _clip(dead[-1]["void_system"], 120)))
    standing, win, since, bad_win, bad_since = counting_window(st, d, rs)
    if standing:
        after = win
        tail = _looks(after)
        # the one look is a well-formed answer: an error or a timeout is no look and a malformed round is not one
        # (the caps below still count them); its refusal stops judging again. The count of refusing looks and its
        # limit (1) are read through the control store: `pipe add <Mod> granted_look -1` gives a spent look back
        bal = look_balance(st, d, rs, mod)
        if bal.get("error"):
            return bal["error"]
        refused, used, lim = bal["refused"], bal["used"], bal["lim"]
        if refused and used >= lim:
            cross = refused[max(1, min(len(refused), len(refused) - (used - lim))) - 1]
            tail = tail[:tail.index(cross) + 1]
            at = len(_looks(rs)) - len(_looks(after)) + len(tail)
            if standing.get("final"):
                return ("the final look (granted %s, after %s) at round %d was %s: the owner's or the Conductor's to decide (its act "
                        "under RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS)" % (
                    standing.get("granted_at"), ", ".join(standing.get("after") or []) or "nothing",
                    at, tail[-1].get("verdict") or "no verdict"))
            return "released for one more look at round %d; that look was %s" % (
                at, tail[-1].get("verdict") or "no verdict")
        # RIMMANDRAKE_HASH_EVERY_COVERAGE_INPUT: the caps still bind after a release, counted from it
        return _caps(after, since, mod, bad_win, bad_since)
    nc = PC.used(mod, "coverage_not_covered", sum(1 for r in win if is_refusal(r)))
    lim = PC.limit(mod, "coverage_not_covered", NOT_COVERED_LIMIT)
    if nc >= lim:
        return "%d not_covered verdicts%s (limit %d)" % (nc, since, lim)
    return _caps(win, since, mod, bad_win, bad_since)


def _caps(rs, since, mod="?", bad_rs=None, bad_since=None):
    """The run, spend and malformed caps over rounds rs (the malformed cap over bad_rs when given: a sign-off does not
    reset it) -> why judging stops, or None. Each count and limit is read through pipeline_control (`pipe show <Mod>`),
    so a one-line act moves it."""
    bad_rs, bad_since = (rs, since) if bad_rs is None else (bad_rs, bad_since or "")
    bad = PC.used(mod, "coverage_malformed", sum(1 for r in bad_rs if r.get("verdict") == "malformed"))
    lim = PC.limit(mod, "coverage_malformed", MALFORMED_LIMIT)
    if bad >= lim:
        return "%d malformed verdicts%s (limit %d): the coverage brief FAILED its refusal contract" % (
            bad, bad_since, lim)
    runs, lim = PC.used(mod, "coverage_runs", len(_looks(rs))), PC.limit(mod, "coverage_runs", JUDGE_RUNS_MAX)
    if runs >= lim:
        return "%d judge runs%s (limit %d)" % (runs, since, lim)
    if spend(rs) >= JUDGE_SPEND_MAX:
        return "judge spend %d tokens%s (limit %d, 4x the p90)" % (spend(rs), since, JUDGE_SPEND_MAX)
    return None


def subject(d):
    return "concept:%s" % os.path.basename(os.path.abspath(d))


def hold(d, why, now=None):
    """Stop judging: the concept goes blocked on the alarm (designer_stage open_run refuses a blocked concept, so no
    Designer run opens; one already open never starts its claude, as `run` exits STOP_EXIT), and the alarm row is
    raised or updated. An open run is left for the launcher's close, which rejects it (no result) and keeps the block."""
    import refusal_contract as RC
    st = DS.load_state(d)
    rs = rounds(st, d)
    on = "%s: %s; judging stopped on %s (coverage_judge.py release <dir> --why ... grants one more look)" % (
        RC.ALARM_ID, why, os.path.basename(os.path.abspath(d)))
    if st.get("status") != "blocked" or st.get("blocked_on") != on:
        st["status"], st["blocked_on"] = "blocked", on
        st["coverage_stop"] = {"at": DS.now_iso(), "why": why}
        DS.hist(st, "coverage_stop", on)
        DS.write_json(DS.state_path(d), st)
    return RC.alarm(subject(d), why, now=now, family="coverage_judge", detail={
        "item": st.get("item"), "rounds": len(rs), "spend": spend(rs),
        "verdicts": [r.get("verdict") for r in rs], "late": sum(len(r.get("late") or []) for r in rs)})


def item_states(ids):
    """-> {id: ledger state, or None when never filed}, folded by model.replay over every shard."""
    import model
    w = model.replay(model.read())
    return {i: getattr(w.items.get(i), "state", None) for i in ids}


def grant_waits(st, item_state=None, d=None):
    """RIMMANDRAKE_GRANT_LOOK_AFTER_FIXES_CLOSE -> what the standing granted release still waits on ([] when due), or
    None when no grant stands. Due: every item it names is closed, and a locked_change (the re-pin) was written after
    the stop the grant lifts (RIMMANDRAKE_ACCEPT_REPIN_BEFORE_GRANT_RECORDED_FIVE_MINUTES_LATE: Pyrelands' re-pin
    landed five minutes before its grant was written, and "after the grant" kept the one look from ever applying).
    The re-pin is owed only by a LOCKED concept (RIMMANDRAKE_FREE_GRANT_FROM_REPIN_ON_UNLOCKED_CONCEPT, Contagion
    2026-11-16): `designer_stage.py repin` refuses an unlocked one, whose changed inputs reopen its stages instead, so
    with D given and its version file not locked the grant waits on its items only."""
    import model
    g = st.get("coverage_release_granted")
    if not isinstance(g, dict):
        return None
    after = [x for x in g.get("after") or [] if x]
    states = (item_state or item_states)(after) if after else {}
    waits = ["%s (%s)" % (i, states.get(i) or "never filed") for i in after if states.get(i) not in model.TERMINAL]
    hs = [h for h in st.get("history") or [] if isinstance(h, dict)]
    at = max((n for n, h in enumerate(hs) if h.get("what") == "coverage_release_granted"), default=-1)
    stop = max((n for n, h in enumerate(hs[:at + 1]) if h.get("what") == "coverage_stop"), default=at)
    unlocked = d is not None and (DS.read_json(os.path.join(d, DS.VERSION_FILE)) or {}).get("state") != "locked"
    if not unlocked and not any(h.get("what") == "locked_change" for h in hs[stop + 1:]):
        waits.append("the re-pin (a locked_change after the stop the grant at %s lifts: designer_stage.py repin)"
                     % g.get("at"))
    return waits


def release(d, why, now=None, after=None, item_state=None):
    """One more look, said with a reason: the block lifts and the next judge run counts as the last before a stop.
    With `after` (item ids), the release is GRANTED now and takes effect later (RIMMANDRAKE_GRANT_LOOK_AFTER_FIXES_CLOSE,
    "fix first, then exactly one more look"): the grant is recorded and the stop stands. A later plain release (the
    locked-change chain's) applies it once grant_waits is empty, as one final look; before that it is refused."""
    import refusal_contract as RC
    if not CT.txt(why):
        raise DS.Refused("a release says why")
    st = DS.load_state(d)
    if DS.standing_park(st, d):
        raise DS.Refused("parked for him (%s): only his word or the Conductor's act on %s lifts a park, not a release" % (
            st["park"].get("kind"), st.get("item")))
    g = st.get("coverage_release_granted")
    if after:
        after = list(dict.fromkeys(a.strip() for a in after if a and a.strip()))
        if isinstance(g, dict):
            raise DS.Refused("a granted release already stands (at %s, after %s): it is the one look" % (
                g.get("at"), ", ".join(g.get("after") or [])))
        if not st.get("coverage_stop"):
            raise DS.Refused("judging is not stopped on %s: a release after fixes is granted on a stop" %
                             os.path.basename(os.path.abspath(d)))
        states = (item_state or item_states)(after)
        unfiled = [a for a in after if not states.get(a)]
        if unfiled:
            raise DS.Refused("a grant waits on filed items; never filed: %s" % ", ".join(unfiled))
        st["coverage_release_granted"] = {"at": DS.now_iso(), "why": why, "after": after}
        DS.hist(st, "coverage_release_granted", "%s (takes effect after %s close and the re-pin lands)" % (
            why, ", ".join(after)))
        DS.write_json(DS.state_path(d), st)
        return st
    rs = rounds(st, d)
    rec = {"at": DS.now_iso(), "why": why, "rounds_at": len(rs),    # the boundary by judge, never by a count; a
           "judges_at": [r.get("judge") for r in _looks(rounds(st, d, voids=True))]}   # void one is before it too
    if isinstance(g, dict):
        waits = grant_waits(st, item_state, d)
        if waits:
            raise DS.Refused("the release granted at %s waits on: %s" % (g.get("at"), "; ".join(waits)))
        rec.update(granted_at=g.get("at"), granted_why=g.get("why"), after=list(g.get("after") or []), final=True)
        st.pop("coverage_release_granted", None)
    st.setdefault("coverage_releases", []).append(rec)
    st.pop("coverage_stop", None)
    if st.get("status") == "blocked" and str(st.get("blocked_on") or "").startswith(RC.ALARM_ID):
        DS.lift_block(st)   # the stop's reason leaves with it (the coverage_stop history row keeps it)
    DS.hist(st, "coverage_release", why)
    DS.write_json(DS.state_path(d), st)
    RC.clear(subject(d), why, now=now)
    return st


def tag_gaps(gaps, earlier):
    """Program-side tags: round 1's gaps are first; a later gap naming only ids no earlier gap named, that the judge
    does not say changed or regressed, is late. -> the late gaps' ids."""
    seen = {i for g in earlier for i in g.get("ids") or []}
    late = []
    for g in gaps:
        said = g.get("new_since")
        if not earlier:
            g["new_since"] = "first"
        elif said not in ("changed", "regression"):
            ids = list(g.get("ids") or [])
            if ids and not (set(ids) & seen):
                if said != "late":
                    g["judge_said"] = said
                g["new_since"] = "late"
                late += ids
            elif said not in TAGS or said == "first":
                g["judge_said"] = said
                g["new_since"] = "unfixed"
    return late


def changed_rows(prior, now_hashes):
    """-> (the checklist ids whose own entry changed since the prior verdict, whether anything changed at all), or
    (None, None) when the prior verdict kept no hashes."""
    old = (prior or {}).get("hashes")
    if not isinstance(old, dict):
        return None, None
    keys = {k for k in set(old) | set(now_hashes) if old.get(k) != now_hashes.get(k)}
    return {k.partition(":")[2] for k in keys if k.partition(":")[0] in ROW_KINDS}, bool(keys)


def retag_against_prior(gaps, prior, now_hashes):
    """A full re-judge's tags checked against the prior verdict's entry hashes: a `late` gap on a row whose own entry
    changed is `changed` (new material, not a miss); a `changed` or `regression` gap when nothing at all changed is
    `late` (the judge named a change there is none of)."""
    rows, anything = changed_rows(prior, now_hashes)
    if rows is None:
        return
    for g in gaps:
        ns, ids = g.get("new_since"), set(g.get("ids") or [])
        if ns == "late" and ids & rows:
            g.update(new_since="changed", since=g.get("since") or "entries %s changed since %s" % (
                ", ".join(sorted(ids & rows)), prior.get("judge")))
        elif ns in ("changed", "regression") and not anything:
            g.setdefault("judge_said", ns)
            g["new_since"] = "late"


def last_refuser(st, d):
    """The last earlier judge whose look was a well-formed not_covered (it had to list every gap), or None."""
    rs = [r for r in rounds(st, d) if r.get("verdict") == "not_covered"]
    return rs[-1].get("judge") if rs else None


def apply_bar_rule(rec):
    """Move every gap the bar rule does not let block (bar_rule.blocks) into rec["advisory_gaps"]; a not_covered look
    left with no blocking gap is covered (its advisory gaps stored and shown)."""
    keep, adv = BR.split(rec.get("gaps") or [])
    if not adv:
        return rec
    rec["gaps"] = keep
    rec["advisory_gaps"] = list(rec.get("advisory_gaps") or []) + adv
    if rec.get("verdict") == "not_covered" and not keep:
        rec["verdict"] = "covered"
        rec["covered_by_bar_rule"] = ("every gap is advisory under the bar rule (%d): a passing bar is an experience, "
                                      "never a tuning number, asset count, declared field or a later look's "
                                      "unconfirmed miss"
                                      % len(adv))
    return rec


READER_SCHEMA = {"type": "object", "additionalProperties": False, "required": ["grades"],
                 "properties": {"grades": {"type": "array", "items": {
                     "type": "object", "additionalProperties": False,
                     "required": ["criterion_verdict", "criterion_why", "bar_kind", "serious"],
                     "properties": {"criterion_verdict": {"enum": list(RC.VERDICTS)},
                                    "criterion_why": {"type": "string"},
                                    "bar_kind": {"enum": list(BR.BAR_KINDS)},
                                    "serious": {"type": "boolean"}}}}}}
PROGRAM_WHY = ("the program reader finds no tuning number, asset count or declared field in this demand; the neutral "
               "fixer reads the clause itself at its third refusal")


def _late(g):
    """A late gap after a refusing look: the kind whose blocking needs the second reader's confirmation."""
    return g.get("new_since") == "late" and bool(g.get("miss_of"))


NO_READ = "judge (no second read)"    # a gap's criterion_by when no second reader graded it


def never_read(g):
    """A carried gap whose criterion no second reader ever graded (the look that wrote it got no second read, so it
    was stored advisory): it is read on the look that carries it, before it binds
    (RIMMANDRAKE_READ_ADVISORY_PRIOR_GAP_BEFORE_IT_BINDS_UNREAD)."""
    return isinstance(g, dict) and bool(g.get("carried")) and g.get("criterion_by") == NO_READ and not g.get("malformed")


def carried_criteria(d, rec):
    """-> {id: criterion text} for the rows of the never-read carried gaps (contract_verdict leaves carried rows out of
    its criteria, so the reader would be shown an empty criterion for them)."""
    ids = {i for g in rec.get("gaps") or [] if never_read(g) for i in g.get("ids") or [REST_CLAUSE]}
    if not ids:
        return {}
    ent = entries(d)
    out = {}
    for c in ids:
        e = ent.get("inv:%s" % c) or ent.get("leaf:%s" % c)
        if c == REST_CLAUSE:
            out[c] = REST_TEXT
        elif e is not None:
            out[c] = json.dumps(e, sort_keys=True)
    return out


def reader_items(rec, crit):
    """-> (the blocking gaps a second reader grades, what it is shown for each: the criterion text and the demand,
    never the judge's own grade). A carried gap was graded when written and is not shown again, except one no reader
    ever graded (never_read)."""
    gaps = [g for g in rec.get("gaps") or [] if isinstance(g, dict) and not g.get("malformed")
            and (not g.get("carried") or never_read(g))]
    items = []
    for g in gaps:
        ids = list(g.get("ids") or []) or [REST_CLAUSE]
        item = {"clause": ids, "criterion": [fulltext.fit(crit.get(i) or "", 1500) for i in ids[:3]],
                "what": g.get("what"), "where": g.get("where"), "would_pass": g.get("would_pass"),
                "smallest_fix": g.get("smallest_fix")}
        if _late(g):   # the reader confirms a late gap's seriousness or not (bar_rule.blocks); the judge's own word is not shown
            item.update(late=True, late_why=g.get("late_why") or "")
            if g.get("repair_passage"):
                item["repair_passage"] = g["repair_passage"]
        items.append(item)
    return gaps, items


def reader_prompt(items):
    return ("You are a second reader of a RimMandrake coverage judge's refusals. You did not write the concept and you "
            "did not judge it. For each refusal below, in order, grade the CRITERION it applies, not whether the concept "
            "passes: `sound` (a fair bar a correct mod could pass, about something a player would notice), `flawed` "
            "(wrong, ambiguous, or not a bar under the rule below) or `unattainable` (nothing could ever pass it); give "
            "`criterion_why`, one sentence, and the refusal's `bar_kind`. A refusal marked `late` was found at a later "
            "look, after an earlier look refused; on the check of the repairs it quotes a passage a repair changed "
            "(`repair_passage`); it blocks only when you confirm it serious: `serious` true only when what it refuses is a Problem a player would reject (a defect, or an "
            "experience a player would reject as strange or disappointing), false for anything less; for a refusal not "
            "marked `late`, answer `serious` false (it is not read). Read no file and edit nothing.\n\nThe bar "
            "rule: %s\n\nThe refusals (JSON, in order):\n%s\n\nAnswer `grades`, exactly one per refusal, in order."
            % (BR.RULE_TEXT, json.dumps(items, ensure_ascii=False, indent=1)))


# The judge and its second reader read and never edit (item RIMMANDRAKE_RESUME_WRONG_CHECK_WORKER_WITH_MOD_FIX_EXTENSION:
# "do not let it edit files"); a gap is the Designer's to mend. Page: design/specs/2026-11-20-coverage-judge-reads-only/
READ_ONLY_DENY = "Edit,Write,NotebookEdit"


def judge_tail(name, schema):
    """-> the command-line tail a coverage judge or second reader starts with: its model, label, JSON answer and schema,
    and the editing tools denied."""
    return ["--model", MODEL, "--name", name, "--output-format", "json", "--json-schema",
            json.dumps(schema, separators=(",", ":")), "--disallowedTools", READ_ONLY_DENY,
            "--dangerously-skip-permissions"]


def llm_reader(d, repo, unit, charge=True, runner=None):
    """The default second reader: one fresh Opus call that did not judge. -> reader(items) -> [grade] or None."""
    def reader(items):
        argv = [CLAUDE, "-p", reader_prompt(items)] + judge_tail("COVERAGE SECOND READER %s" % unit, READER_SCHEMA)
        def bill(res):
            # measuring and charging are apart: a call that ran and cannot be measured is charged unmeasured
            if not charge:
                return
            tok = None
            if isinstance(res, dict):
                try:
                    import role_launch as RL
                    tok = RL.run_tokens(res, MODEL)     # modelUsage when the result has it; else usage as MODEL
                except Exception:  # noqa: BLE001 - an unknown model is unmeasured, never weighed as another
                    tok = None
            try:
                DS.charge(d, tok or 0, "review" if tok is not None else "unmeasured", unit + READER_SUFFIX)
            except Exception:  # noqa: BLE001 - a charge we cannot write never fails the read
                pass
        try:
            code, out = (runner or default_runner)(spend_watchdog.wrap(argv, READER_BUDGET_USD), repo,
                                                   dict(os.environ, RM_ROLE_UNIT=unit), READER_TIMEOUT_S)
        except OSError:          # never launched: nothing was spent
            return None
        except subprocess.SubprocessError as e:    # it ran (a timeout): its spend is unknown, and void
            bill(None)
            reader.dead = "the second reader did not answer: %s" % e    # its charge is no judge spend (rounds)
            return None
        try:
            res = json.loads(out or "null")
        except ValueError:
            res = None
        bill(res)
        if not isinstance(res, dict):
            return None
        so = res.get("structured_output")
        grades = so.get("grades") if code == 0 and isinstance(so, dict) else None
        ok = isinstance(grades, list) and len(grades) == len(items) and all(isinstance(g, dict) for g in grades)
        return grades if ok else None   # a grade that is not an object is no second read
    return reader


def second_read(rec, crit, reader):
    """The binding criterion verdicts, from a reader that did not judge (RIMMANDRAKE_TEACH_JUDGES_BARS_HOLD_NO_TUNING_
    NUMBERS (c)). The judge's own grade is kept as judge_criterion_verdict/why. reader None = the program reader (the
    bar rule only; selftests and runs with a stubbed judge). -> None, or why no second read was had (the refusal then
    binds nothing)."""
    gaps, items = reader_items(rec, crit)
    if not gaps:
        return None
    for g in gaps:
        if "judge_criterion_verdict" not in g:
            g["judge_criterion_verdict"] = g.get("criterion_verdict")
            g["judge_criterion_why"] = g.get("criterion_why")
    if reader is None:
        for g in gaps:
            if g.get("judge_criterion_verdict") not in ("flawed", "unattainable"):   # a confession stands
                g.update(criterion_verdict="sound", criterion_why=PROGRAM_WHY)
            g["criterion_by"] = "program"
            if _late(g):
                g["late_confirmed"] = False   # a program cannot tell a Problem a player would reject: no confirmation
        return None
    grades = reader(items)
    if not grades:
        for g in gaps:
            g["criterion_by"] = NO_READ
        return ("no second reader graded the refusals' criteria: this refusal is stored and shown, the Designer is "
                "not sent back")
    for g, gr in zip(gaps, grades):
        g.update(criterion_verdict=gr.get("criterion_verdict"), criterion_why=gr.get("criterion_why"),
                 criterion_by="second_reader")
        if gr.get("bar_kind") in BR.ADVISORY_KINDS:
            g["bar_kind"] = gr["bar_kind"]   # the second reader's word on the kind also counts (bar_rule.blocks)
        if _late(g):
            g["late_confirmed"] = gr.get("serious") is True   # point 26: a late gap blocks only when the reader agrees
    return None


def contract_verdict(d, rec, item):
    """-> (verdict, given): a coverage verdict in the refusal contract's form (refusal_contract.py). One clause per
    checklist id (its text is the inventory row or tree leaf it names) plus `rest` for a gap on no single row; every row
    no gap names is passed with its evidence; each gap the judge wrote this round is a refusal of each id it names (two
    gaps on one id are one record, and a refused row's evidence joins it). Carried gaps were checked when written and are left out, with their ids. A full
    judge is given the concept files; a delta judge is shown quoted entries, so its given inputs are the files it cites
    and `contract_errors` adds that each is a concept file."""
    ent = entries(d)
    gaps = [g for g in rec.get("gaps") or [] if isinstance(g, dict)]
    mine = [g for g in gaps if not g.get("carried") and not g.get("malformed")]
    # carried gaps were checked when written; a record kept on file as malformed is neither refused nor passed
    held = [g for g in gaps if g.get("carried") or g.get("malformed")]
    carried = {i for g in held for i in g.get("ids") or [REST_CLAUSE]}
    refused = {}
    for g in mine:
        for c in list(g.get("ids") or []) or [REST_CLAUSE]:
            r = refused.get(c)
            ns = str(g.get("new_since") or "")
            ns = "%s:%s" % (ns, g.get("since") or c) if ns in RC.NEW_SINCE else ns
            if r is None:
                refused[c] = {"clause": c, "evidence": list(g.get("evidence") or []), "observed": g.get("observed"),
                              "would_pass": g.get("would_pass"), "smallest_fix": g.get("smallest_fix"),
                              "criterion_verdict": g.get("criterion_verdict"), "criterion_why": g.get("criterion_why"),
                              "criterion_by": g.get("criterion_by") or "judge",
                              "new_since": ns, "gap": g.get("gid")}
                continue
            r["evidence"] += [e for e in g.get("evidence") or [] if e not in r["evidence"]]
            for k in ("observed", "would_pass", "criterion_why"):
                if g.get(k) and g[k] != r.get(k):
                    r[k] = "%s; %s" % (r[k], g[k]) if r.get(k) else g[k]
            if g.get("criterion_verdict") in ("flawed", "unattainable"):
                r["criterion_verdict"] = g["criterion_verdict"]
    crit = {}
    for c in refused:
        e = ent.get("inv:%s" % c) or ent.get("leaf:%s" % c)
        crit[c] = REST_TEXT if c == REST_CLAUSE else (json.dumps(e, sort_keys=True) if e is not None else None)
    passed = []
    for r in rec.get("checklist") or []:
        c = r.get("id") if isinstance(r, dict) else None
        if isinstance(c, str) and c in refused:   # a refused row's evidence is the refusal's too
            refused[c]["evidence"] += [str(e) for e in r.get("evidence") or [] if str(e) not in refused[c]["evidence"]]
        if not isinstance(c, str) or c in refused or c in carried:
            continue
        e = ent.get("inv:%s" % c) or ent.get("leaf:%s" % c)
        crit[c] = json.dumps(e, sort_keys=True) if e is not None else None
        passed.append({"clause": c, "evidence": [str(x) for x in r.get("evidence") or []]})
    if REST_CLAUSE not in refused and REST_CLAUSE not in carried:
        crit[REST_CLAUSE] = REST_TEXT
        passed.append({"clause": REST_CLAUSE, "evidence": []})
    crit = {c: t for c, t in crit.items() if t is not None}   # an id that is no row or leaf: check says so
    for r in refused.values():
        if r["clause"] in crit:
            r["criterion_hash"] = RC.criterion_hash(crit[r["clause"]])
    if rec.get("mode") == "delta":
        inputs = sorted({RC._split(e)[0] for r in list(refused.values()) + passed for e in r["evidence"]})
    else:
        inputs = [f for f in INPUT_FILES if os.path.exists(os.path.join(d, f))]
        # a file only a held malformed record (or its row) cites was read and cited: it is not an unread input
        cited = {RC._split(e)[0] for r in list(refused.values()) + passed for e in r["evidence"]}
        gone = {i for i in held_cites(rec, held) if i not in cited}
        inputs = [f for f in inputs if f not in gone]
    given = {"inputs": inputs, "criteria": crit, "root": d}
    verdict = {"item": str(item or os.path.basename(d)), "family": CONTRACT_FAMILY,
               "sha": str(rec.get("tree") or CT.tree_hash(CT.load(d))), "given": given,
               "passed": passed, "refusals": list(refused.values())}
    return verdict, given


def held_cites(rec, held):
    """The files the malformed gaps in `held`, and their checklist rows, cite."""
    bad = [g for g in held if g.get("malformed")]
    ids = {i for g in bad for i in g.get("ids") or []}
    evs = [e for g in bad for e in g.get("evidence") or []] + [
        e for r in rec.get("checklist") or [] if isinstance(r, dict) and r.get("id") in ids for e in r.get("evidence") or []]
    return {RC._split(str(e))[0] for e in evs}


def contract_errors(d, rec, item):
    """-> (verdict, given, errors): the contract form and why it is malformed ([] = well formed)."""
    v, given = contract_verdict(d, rec, item)
    errs = RC.check(v, given)
    if rec.get("mode") == "delta":
        errs += ["evidence %r is not a concept file (%s)" % (i, ", ".join(INPUT_FILES))
                 for i in given["inputs"] if i not in INPUT_FILES]
    return v, given, errs


ROW_ERR_RE = re.compile(r"^refusal \d+ \((?P<clause>[^)]*)\): ")


def row_errors(errs, cv):
    """-> ({clause: [its errors]}, [errors of no single refusal record]). A delta input that is no concept file is the
    error of every refusal record citing it; one only a passed row cites is the whole verdict's."""
    rows, glob = {}, []
    for e in errs:
        m = ROW_ERR_RE.match(e)
        if m:
            rows.setdefault(m.group("clause"), []).append(e)
            continue
        hit = [r["clause"] for r in cv.get("refusals") or [] for ev in r.get("evidence") or []
               if e.startswith("evidence %r is not a concept file" % RC._split(ev)[0])]
        for c in hit:
            rows.setdefault(c, []).append(e)
        if not hit:
            glob.append(e)
    return rows, glob


def gaps_of(rec, clauses):
    """The judge's own gaps (not carried, not already held as malformed) whose records make the given clauses."""
    return [g for g in rec.get("gaps") or [] if isinstance(g, dict) and not g.get("carried") and not g.get("malformed")
            and set(g.get("ids") or [REST_CLAUSE]) & set(clauses)]


def row_reask_text(rows, cv, given, gaps):
    """The row re-ask: only the broken records, each with the checker's exact words and the text its evidence cites."""
    out = ["These refusal records in your verdict still break the refusal contract; every other row and gap stands as "
           "you wrote it. For each, the checker's exact complaint and the text your evidence actually cites:"]
    by = {r["clause"]: r for r in cv.get("refusals") or []}
    for g in gaps:
        cs = [c for c in g.get("ids") or [REST_CLAUSE] if c in rows]
        out.append("- gap on %s (%s):" % (", ".join(g.get("ids") or [REST_CLAUSE]), CT.txt(g.get("what"))))
        out += ["  complaint: %s" % e for c in cs for e in rows[c]]
        for ev in (by.get(cs[0]) or {}).get("evidence") or [] if cs else []:
            ref, a, b = RC._split(ev)
            txt = RC._text_of(ref, given)
            if txt is None:
                continue
            if a is not None:
                txt = "\n".join(txt.splitlines()[a - 1:b])
            out.append("  %s reads: %s" % (ev, " ".join(txt.split()) or "(nothing: no such lines)"))
    out.append("Answer with `gaps`: one corrected record for each gap listed here, the same ids, nothing else. "
               "`observed` quotes words that stand in the lines its evidence cites; cite `file:a-b` spanning them.")
    return "\n".join(out)


def unproven_signatures(repo):
    """-> [{concept, signed_by, at, why}] for every concept whose coverage signature was made by a judge whose brief
    was not CALIBRATED when it signed (RIMMANDRAKE_EARN_CALIBRATION_BOTH_WAYS: flagged, never voided)."""
    out = []
    root = os.path.join(repo, "design", "concepts")
    for name in sorted(os.listdir(root)) if os.path.isdir(root) else []:
        d = os.path.join(root, name)
        tree = CT._read_json(os.path.join(d, "tree.json"))
        cov = (tree or {}).get("coverage") if isinstance((tree or {}).get("coverage"), dict) else {}
        by = cov.get("signed_by")
        if by in CT.LEGACY_SIGNERS:
            why = "legacy signer %s, before any calibration registry" % by
        elif by == CT.SIGNER:
            v = CT._read_json(os.path.join(d, VERDICT_FILE)) or {}
            cal = v.get("calibration") if v.get("signed") else None
            if cal == "CALIBRATED":
                continue
            why = "brief %s when it signed" % (cal or "UNTESTED (signed before covered read calibration)")
        else:
            continue
        out.append({"concept": "design/concepts/%s" % name, "signed_by": by, "at": cov.get("at"), "why": why})
    return out


def stop_exit(rec):
    """True when the pre-launch step must stop the Designer's run: judging stopped, parked, or the verdict refused
    itself (a malformed refusal never sends the Designer back to rework), or the refusal is advisory (an
    uncalibrated brief, T6)."""
    return isinstance(rec, dict) and bool(rec.get("stopped") or rec.get("parked") or rec.get("malformed")
                                          or rec.get("advisory") or (rec.get("contract") or {}).get("advisory"))


def record_round(d, rec):
    """stage.json coverage_rounds gets this round: verdict, gap count and ids, tags, late ids, tokens, tree."""
    st = DS.load_state(d)
    gaps = rec.get("gaps") or []
    st.setdefault("coverage_rounds", []).append({
        "judge": rec["judge"], "at": rec["at"], "verdict": rec.get("verdict"), "tree": rec.get("tree"),
        "tokens": rec.get("tokens"), "unmeasured_calls": int(rec.get("unmeasured_calls") or 0), "gaps": len(gaps),
        "ids": sorted({i for g in gaps for i in g.get("ids") or []}),
        "tags": {t: sum(1 for g in gaps if g.get("new_since") == t) for t in TAGS if any(
            g.get("new_since") == t for g in gaps)},
        "late": rec.get("late") or [], "error": rec.get("error"), "error_kind": rec.get("error_kind"),
        "void_system": void_cause(rec) or None, **round_counts(rec),
        # the detached run that asked for the Designer run this judge screens (role_launch.with_parent): run_void.children
        "parent": os.environ.get("RM_PARENT_UNIT") or None,
        "reader_void_system": rec.get("reader_void_system"), "stale_inputs": rec.get("stale_inputs") or None,
        "repair_blocks": repair_blocks(rec)})
    DS.write_json(DS.state_path(d), st)
    return st


# The four counts printed when a mod's coverage closes (owner by card 2026-11-17, 6_proposed_ruling_plain.md "How it is
# built" step 5; RIMMANDRAKE_PRINT_JUDGE_COUNTS_WHEN_COVERAGE_CLOSES), plus the count he added on that ticket, second-look
# blocks on a repaired passage (repair_blocks). Flaws found in play that the judge passed are counted after the played
# session, not here; his own overturns are outside the program's reach.
def round_counts(rec):
    """-> {new_on_unchanged, overturned, not_owner_said} for one round. new_on_unchanged: late gaps (blocking or
    advisory) that quote no changed passage, plus the dropped ones; overturned: gaps a second reader did not confirm, or
    whose criterion it called flawed or unattainable where the judge did not; not_owner_said: blocking gaps whose
    `owner_said` is False (a missing answer is not counted)."""
    every = [g for g in list(rec.get("gaps") or []) + list(rec.get("advisory_gaps") or []) if isinstance(g, dict)]
    new = [g for g in every if g.get("new_since") == "late" and not g.get("repair_passage")]
    # a reader that did read it, in this round: a carried gap's grade was counted by the round that graded it
    read = lambda g: g.get("criterion_by") not in ("program", NO_READ) and (
        not g.get("carried") or g.get("first_read_at") == rec.get("judge"))
    mine = [g for g in rec.get("gaps") or [] if isinstance(g, dict) and not g.get("carried")]
    return {"new_on_unchanged": sum(1 for g in new if g.get("passage") not in ("no_baseline", "unshown"))
            + sum(1 for g in rec.get("dropped") or [] if isinstance(g, dict) and not g.get("names_slot")),
            # a new finding whose material could not be shown changed or unchanged: neither count, named
            "new_unsettled": sum(1 for g in new if g.get("passage") in ("no_baseline", "unshown")),
            "unplaced": sum(1 for g in every if g.get("unplaced")),
            "overturned": sum(1 for g in every if read(g) and (g.get("late_confirmed") is False or (
                g.get("criterion_verdict") in ("flawed", "unattainable") and "judge_criterion_verdict" in g
                and g.get("judge_criterion_verdict") not in ("flawed", "unattainable")))),
            "not_owner_said": sum(1 for g in mine if g.get("owner_said") is False),
            "owner_said_unmeasured": sum(1 for g in mine if not isinstance(g.get("owner_said"), bool))}


def repair_blocks(rec):
    """The fifth count (owner, 2026-11-17 ~6:50 PM PST: "hopefully the judge doesn't just start polishing anything we
    repair"; RIMMANDRAKE_COUNT_REPAIR_PASSAGE_BLOCKS_FIFTH_MISSED_AT_CLOSE): this round's blocking late gaps that quote a
    passage a repair changed, each with that passage and the promise it says is not kept. [] = looked, none; a gap
    carried from an earlier round was that round's block."""
    out = []
    for g in rec.get("gaps") or []:
        rp = g.get("repair_passage") if isinstance(g, dict) else None
        if isinstance(rp, dict) and g.get("new_since") == "late" and not g.get("carried"):
            out.append({"gid": g.get("gid") or g.get("id") or ",".join(str(i) for i in g.get("ids") or []),
                        "entry": rp.get("entry"), "passage": rp.get("passage"), "promise": g.get("promise")})
    return out


def close_counts(st, d=None):
    """-> the four counts over a concept's coverage rounds: looks (covered or not_covered: a malformed round, or a
    covered word the program refused with an error, is not a look), refusals (not_covered), and the per-round counts summed (a round without one counts 0)."""
    rs = _looks(rounds(st, d))   # a legacy judge (charges only, verdict unknown) is a look its counts never saw
    looks = [r for r in rs if (r.get("verdict") in ("covered", "not_covered") and not r.get("error")) or r.get("legacy")]
    out = {"looks": len(looks), "refusals": sum(1 for r in looks if r.get("verdict") == "not_covered")}
    # counted: written by the counting build (it carries a count; one it lacks is 0, the case's rule); a round with no
    # count, or a null one, was never counted
    counted = [r for r in looks if any(k in r for k in COUNT_KEYS)
               and all(isinstance(r[k], int) for k in COUNT_KEYS if k in r)]
    for k in COUNT_KEYS + ("new_unsettled", "unplaced", "owner_said_unmeasured"):
        out[k] = sum(int(r.get(k) or 0) for r in counted)
    # a look recorded before the counts existed (2026-11-18), or with a count missing, could not be counted: named,
    # never read as a measured 0
    out["uncounted_looks"] = len(looks) - len(counted)
    # the fifth count: a look recorded before repair_blocks existed (2026-11-18) is UNMEASURED for it, never a 0
    out["repair_block_list"] = [dict(b, judge=r.get("judge")) for r in looks if isinstance(r.get("repair_blocks"), list)
                                for b in r["repair_blocks"] if isinstance(b, dict)]
    out["repair_blocks"] = len(out["repair_block_list"])
    out["repair_blocks_unmeasured"] = sum(1 for r in looks if not isinstance(r.get("repair_blocks"), list))
    return out


COUNT_KEYS = ("overturned", "new_on_unchanged", "not_owner_said")


def close_line(counts):
    c = dict({"new_unsettled": 0, "unplaced": 0, "owner_said_unmeasured": 0}, **counts)
    return ("coverage counts: looks %(looks)d, refusals %(refusals)d (looks), overturned %(overturned)d (refusal records "
            "the second reader overturned; owner overturns: not counted), new demands on unchanged material "
            "%(new_on_unchanged)d, not in the owner's words %(not_owner_said)d" % c) + "".join((
        "; %d new demand(s) whose material could not be shown changed or unchanged" % c["new_unsettled"]
        if c["new_unsettled"] else "",
        "; %d unplaced repair report(s)" % c["unplaced"] if c["unplaced"] else "",
        "; %d refusal record(s) gave no `owner_said`: UNMEASURED" % c["owner_said_unmeasured"]
        if c["owner_said_unmeasured"] else "",
        "; %d look(s) recorded before counting began: their three counts UNMEASURED, the figures above leave them out"
        % c["uncounted_looks"] if c.get("uncounted_looks") else "",
        "; second-look blocks on a repaired passage %d" % c.get("repair_blocks", 0) if "repair_blocks" in c else "",
        "".join(" [%s %s: quotes %s \"%s\"; promise \"%s\"]" % (
            b.get("judge") or "?", b.get("gid") or "?", b.get("entry") or "?", _clip(b.get("passage")),
            _clip(b.get("promise"))) for b in c.get("repair_block_list") or []),
        " (%d look(s) recorded before this count began: UNMEASURED for it)" % c["repair_blocks_unmeasured"]
        if c.get("repair_blocks_unmeasured") else ""))


def _clip(s, n=160):
    s = " ".join(str(s or "").split())
    return s if len(s) <= n else s[:n] + "..."


def earlier_gaps(st, d):
    """The gaps earlier looks named: the previous verdict's in full, and every recorded look's ids. A failed attempt
    (an error, a timeout, a malformed answer) is no look: a first real look after one is still the first."""
    out = [{"ids": r.get("ids") or []} for r in st.get("coverage_rounds") or [] if isinstance(r, dict)
           and r.get("verdict") in ("covered", "not_covered") and not r.get("error")]
    last = prior_verdict(d)
    if last:
        out += [g for g in last.get("gaps") or [] if isinstance(g, dict)]
    return out


# Open search in round 1 only (owner by card 2026-11-16 11:36 PM PST, point 14: "round 1 looks everywhere; later rounds
# only check that named gaps were repaired, so the loop ends"). Round 1 is the first look with no earlier verdict to
# check (a malformed or errored look left none); a delta look's prompt never had the open search.
OPEN_SEARCH = "Look for gaps the artifacts do not cite, not only the ones they do. "
LATER_SEARCH = ("This is a later round, and the open search was round 1's: now only check that each gap an earlier "
                "verdict named was repaired, and that no change since opened a gap or broke a passed row; a row that "
                "verdict passed and nothing changed stays passed unless you can quote a defect in its scene or code "
                "(that is a late gap). Do not hunt for new gaps elsewhere. ")


def prompt(d, repo, ids=(), prior=False, round_no=1):
    rel = CT.concept_rel(d, repo)
    slots = prior_slots(prior_verdict(d)) if prior else []
    again = ("A previous judge's verdict is in %s/%s. Check each of its gaps first. A part it passed whose scene has not "
             "changed since stays passed unless you can quote the defect in the scene or the code. Tag every gap's "
             "`new_since`: `unfixed` (that verdict named it and it is still open), `changed` (it is new because an "
             "artifact changed since that verdict; `since` names the file and what changed), `regression` (that verdict "
             "passed it and a change broke it; `since` names the change), or `late` (it was there then and that judge "
             "missed it: say so). Tag a newly discovered gap on unchanged material `late` and explain the earlier miss. "
             "The program determines its blocking status from the recorded history. " % (rel, VERDICT_FILE)
             + REPAIR_LOOK + " " + REPAIR_HOW + " The earlier gaps, by number: "
             + ("; ".join("%s (ids %s): %s" % (g.get("gid"), ", ".join(g.get("ids") or []) or "none",
                                               " ".join(str(g.get("what") or "").split())) for g in slots) or "(none)")
             + ". ") if prior else (
        FIRST_LOOK + " Tag every gap `new_since` `first`, and leave nothing for later: a gap a later judge finds on "
        "material that did not change is advisory, it goes to the owner's short list and cannot send the mod back, so a "
        "gap you hold back is a gap that is lost. ")
    again += ("This is judge round %d. The second not_covered verdict on a concept stops judging and blocks it for the "
              "Conductor. " % round_no)
    return ((
        "You are the coverage judge for the RimMandrake concept at %(rel)s. You did not write it and you sign nothing "
        "yourself: you return a verdict and a program signs on it. Read, in this order: "
        "src/RimMandrake/rimflow/roles/designer_scene_contract.md (the proof-scene contract), "
        "src/RimMandrake/rimflow/roles/designer_lock.md (what the lock means), then %(rel)s/sheet.md, tree.json, "
        "scenes.json, floor.json, exam.json and record.json (scope, inventory, decisions). Do not read result.*.json, "
        "log.md, stage.json or any transcript: judge the artifacts, not the maker's account of them. Do not edit any "
        "file. Judge COVERAGE: every in-scope capability in record.json's inventory and every leaf in tree.json is "
        "exercised by an acceptance or interaction scene that meets the contract (asserted start, a control that rules "
        "out the plausible alternative), or is waived/out in his words; no leaf is accepted only by an "
        "exploration or mock scene; the sheet a player reads says what the tree tests. Resetting or cleaning up a test "
        "scene is harness housekeeping (save before, reload after; owner 2026-11-17): it is never a coverage gap, a "
        "Problem or a Polish finding, so judge nothing about how a scene is reset.For a capability claiming "
        "behaviour across a range, identify the relevant inputs and situations from its words. A coverage gap names an "
        "in-scope case or behavioural regime that the scenes leave unexercised, and explains why their asserted starts "
        "and controls fail to cover it. Its `would_pass` names the additional inputs, assertions or controls needed. "
        "Judge the situations exercised and alternatives ruled out, rather than the number of seeds or scenes. Hunt "
        "parameter regimes and regions, not examples. %(search)sA gap that needs his answer returns to stage 2, one the "
        "Designer can fix returns to stage 3. Check every in-scope capability in the inventory, every tree leaf, the "
        "sheet's player-facing claims and every showcase claim. A blocking gap identifies an in-scope experience and "
        "the specific missing or defective coverage required by the proof-scene contract, or a mismatch between the "
        "sheet's claim and the tested experience. State the evidence and attainable repair. Finish when each required "
        "capability, leaf and claim has been assessed, every failed assessment has a refusal record, and every "
        "remaining assessment has supporting evidence. Return `covered` when that review leaves no blocking gap.\n\n"
        + RULES_TEXT + "\n\n" + ("" if prior else
        "This one pass must list EVERY gap: each round of gaps costs a full rewrite, exam and judge, so a gap held back "
        "for later is the failure this checklist exists to stop. Do not stop at the first few. ") + "Before you answer, write "
        "`checklist`, one row for each of these ids and none skipped: %(ids)s. In each row's `parts`, name every separate "
        "thing a player would notice that capability or leaf ships or tests (one effect among several, a creature that "
        "must appear, a control that must fail), each with the id of the scene that tests it ('' if none) and `ok`; a "
        "number, field or variant its text or impl_evidence lists is not a part (the bar rule below). Separate each "
        "row's stated player-facing experiences from its tuning data. Assess coverage of every stated experience. For "
        "a row containing only tuning data, mark it ok under the bar rule and quote the tuning-only wording in `what`. "
        "Add an advisory reason requesting an experience-based replacement. Quote any intended experience stated in "
        "the supplied artifacts. Where none is stated, write `intended experience unspecified in source`. A part waived or out in his words, or an offline leaf the contract exempts, is ok with the reason in "
        "`what`. Every part not ok must be in a gap, and the gap's `ids` names its rows; a gap about no single row "
        "(a showcase's claims, the sheet) has empty `ids`. %(again)s\n\nThe bar rule: %(rule)s") % {
            "rel": rel, "again": again, "ids": ", ".join(ids) or "(none)", "rule": BR.RULE_TEXT,
            "search": OPEN_SEARCH if not prior else LATER_SEARCH}
        + RECORD_TEXT)


def fresh_key(d, tree):
    """-> (tree hash, sheet hash, {input file: sha256}) of every concept file the judge reads (INPUT_FILES; the tree by
    its hash without the signature stamp). RIMMANDRAKE_HASH_EVERY_COVERAGE_INPUT: scenes.json edited mid-judge used
    to leave the signature standing."""
    import hashlib
    files = {}
    for fn in INPUT_FILES:
        if fn == "tree.json":
            continue
        try:
            with open(os.path.join(d, fn), "rb") as f:
                files[fn] = hashlib.sha256(f.read()).hexdigest()
        except OSError:
            files[fn] = None
    return CT.tree_hash(tree), CT.sheet_hash(d), files


def default_runner(argv, cwd, env, timeout):
    """-> (exit code, stdout). The judge is a plain `claude -p` in the concept's clone."""
    r = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout


# `status --would-judge`, a launch check's read of the judge's own plan: 0 it would judge, 1 it would not (the plan's
# reason printed), 126 it could not look (launch_checks.CANNOT_RUN: did not run, never a refusal). A plan value not
# named here is 126 too: an answer nobody classed is no answer.
WOULD_JUDGE_EXIT = {"judge": 0, "skip": 1, "stopped": 1, "parked": 1, "ceiling": 1, "error": 126}


def plan(d, repo=None):
    """-> (what, why): what `run` would do now: "judge", "skip", "stopped" (the loop limit), "parked" (waiting on
    his word), "ceiling" (the loop reached twice the cap: `run` parks it) or "error"."""
    repo = repo or DS.clone_of(d) or DS.REPO
    try:
        st = DS.load_state(d)
    except (DS.Refused, OSError, ValueError) as e:
        return "error", "unreadable concept: %s" % e
    if st.get("status") == "locked":
        return "skip", "locked"
    DS.lift_park(st, d, repo)   # in memory: `run` writes the lift, `status` only reads
    pk = DS.standing_park(st, d, repo)
    if pk:
        return "parked", "parked for him (%s): %s; only his word or the Conductor's act on %s lifts it" % (
            pk.get("kind"), pk.get("why"), st.get("item"))
    ceil = DS.loop_ceiling(st)
    if ceil:
        return "ceiling", ceil
    if st.get("stage") != 5:
        return "skip", "at stage %s, not 5" % st.get("stage")
    try:
        tree = CT.load(d)
    except (OSError, ValueError) as e:
        return "skip", "no readable tree.json: %s" % e
    if not isinstance(tree, dict) or tree.get("dry_walk") is True:
        return "skip", "no real tree"
    try:
        ex = DS.exam_errors(DS.read_json(os.path.join(d, "exam.json")), d, st, repo)
    except (DS.Refused, OSError, ValueError) as e:
        return "error", "unreadable exam.json: %s" % e
    if ex:
        return "skip", "the exam does not pass: %s" % "; ".join(ex)
    why = CT.coverage_problem(d, repo, tree)
    if not why:
        return "skip", "already signed at tree %s" % CT.tree_hash(tree)[:10]
    stop = stop_reason(st, d)
    if stop:
        return "stopped", stop
    prior = prior_verdict(d)
    if prior and not prior.get("stale_inputs") and (prior.get("advisory") or (prior.get("contract") or {}).get(
            "advisory")) and RC.status(CONTRACT_FAMILY) != "CALIBRATED":
        return "skip", "advisory verdict %s waits for a calibrated coverage brief" % prior.get("judge")
    dp = delta_plan(d, prior)
    if dp is not None and not dp["claims"] and not dp["changed"]:
        return "skip", "nothing claimed fixed in %s and nothing changed since %s: no judge%s" % (
            FIXES_FILE, dp["against"], "" if not dp["refused"] else " (%s)" % "; ".join(dp["refused"]))
    return "judge", why


def run(d, repo=None, runner=default_runner, timeout=TIMEOUT_S, now=None, charge=True, reader="auto"):
    """-> (verdict record or None, message). Signs only on a well-formed `covered` verdict over unchanged inputs.
    `reader` grades the refusals' criteria (second_read): "auto" is the fresh Opus reader when the judge is the real
    claude (runner is default_runner) and the program reader (None) when a selftest stubs the judge."""
    repo = repo or DS.clone_of(d) or DS.REPO
    try:
        st_l = DS.load_state(d)
        if DS.lift_park(st_l, d, repo):
            DS.write_json(DS.state_path(d), st_l)
    except (DS.Refused, OSError, ValueError):
        pass    # plan says why the concept is unreadable
    what, why = plan(d, repo)
    if what == "parked":
        return {"parked": why}, why
    if what == "ceiling":
        DS.park(d, "ceiling", why, repo)
        return {"parked": why}, "parked: %s" % why
    if what == "stopped":
        hold(d, why, now)
        try:
            counts = "; %s" % close_line(close_counts(DS.load_state(d), d))
        except (DS.Refused, OSError, ValueError) as e:
            counts = "; coverage counts UNMEASURED: %s" % e
        return {"stopped": why}, "stopped: %s%s" % (why, counts)
    if what != "judge":
        prior = prior_verdict(d)
        if prior and not prior.get("stale_inputs") and (prior.get("advisory") or (prior.get("contract") or {}).get(
                "advisory")):     # a stale refusal's advisory waits on no brief: it is no answer to hand back
            return prior, "%s: %s" % (what, why)
        return None, "%s: %s" % (what, why)
    unit = UNIT_PREFIX + "%d" % int(now or time.time())
    # the granted look is RESERVED before the judge runs and charged only at a validated settlement (control.py; spec
    # 03-merged.md "Allowances"): of two judges racing for one look, one runs; a run that dies or errs charges nothing
    lk = reserve_look(d, unit)
    if lk and not lk["ok"]:
        return None, "skip: %s" % lk["why"]
    try:
        rec, msg = _judge(d, repo, runner, timeout, now, charge, reader, unit)
    except BaseException as e:
        settle_look(lk, None, "the judge run raised %s" % type(e).__name__)
        raise
    settle_look(lk, rec, msg)
    return rec, msg


def reserve_look(d, unit):
    """-> None when no granted look stands on this concept, else {"ok", "why", "mod", "unit"}: the look reserved for
    `unit` in the control store (one transaction; a reservation whose holder died is released first). An unreadable
    store reserves nothing: ok False, and no judge runs on a look nobody can account for."""
    st = DS.load_state(d)
    bal = look_balance(st, d)
    if bal is None:
        return None
    mod = bal["mod"]
    if bal.get("error"):
        return {"ok": False, "why": bal["error"], "mod": mod, "unit": unit}
    try:
        ok, why = C.reserve(mod, C.LOOK, unit, bal["win"], base=bal["base"], used=bal["used"])    # grants: the store
    except C.Unreadable as e:
        return {"ok": False, "why": "CONTROL UNREADABLE: %s" % e, "mod": mod, "unit": unit}
    return {"ok": ok, "why": None if ok else why, "mod": mod, "unit": unit}


def settle_look(lk, rec, msg):
    """Settle the look exactly once: a well-formed verdict (covered or not_covered, no error) is a validated result and
    is charged; anything else (no answer, malformed, a runner fault, a raise) releases it as a system fault (fail_system,
    on the meter with its own alarm)."""
    if not lk or not lk.get("ok"):
        return
    valid = bool(rec) and rec.get("verdict") in ("covered", "not_covered") and not rec.get("error")
    try:
        C.settle(lk["unit"], valid, "verdict %s" % (rec or {}).get("verdict") if valid else
                 "%s" % ((rec or {}).get("error") or msg))
    except C.Unreadable as e:
        print("coverage_judge: the look's settlement could not be written (%s); its holder's death releases it" % e,
              file=sys.stderr)


def _judge(d, repo, runner, timeout, now, charge, reader, unit):
    """run()'s judging body, on the unit name run() reserved the look for."""
    tree = CT.load(d)
    before = fresh_key(d, tree)
    st0 = DS.load_state(d)
    earlier = earlier_gaps(st0, d)
    prior = prior_verdict(d)
    dp = delta_plan(d, prior)
    ids = dp["ids"] if dp is not None else required_ids(d, tree)
    hashes = entry_hashes(d)
    texts = entry_texts(d)
    # the repair check (7_same_problem_rule.md): every look on a refusing prior verdict whose gaps carry their numbers
    slotted = bool(prior and prior.get("verdict") == "not_covered" and all(
        isinstance(g, dict) and g.get("gid") for g in prior.get("gaps") or []))
    env = dict(os.environ, RM_ROLE_UNIT=unit)

    def tail_for(schema):
        return judge_tail("COVERAGE JUDGE %s" % unit, schema)
    tail = tail_for(SCHEMA)
    round_no = len(rounds(st0, d)) + 1
    text = delta_prompt(d, repo, dp, round_no) if dp is not None else prompt(d, repo, ids, prior is not None, round_no)
    argv = [CLAUDE, "-p", text] + tail
    rec = {"judge": unit, "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now or time.time())),
           "tree": before[0], "sheet": before[1], "inputs": before[2], "verdict": None, "signed": False, "hashes": hashes,
           "entry_text": texts,
           "mode": "full" if dp is None else "delta", "prompt_chars": len(text)}
    held_bad = [{k: g.get(k) for k in ("gid", "ids", "what", "malformed")} for g in (prior or {}).get("gaps") or []
                if isinstance(g, dict) and g.get("malformed")]
    if held_bad:   # evidence on file, never a slot (prior_slots)
        rec["prior_malformed"] = held_bad
    if dp is not None:
        rec.update(against=dp["against"], claims=dp["claims"], changed=dp["changed"])
        if dp["refused"]:
            rec["claims_refused"] = dp["refused"]

    calls = []      # each judge call's end, in order: "dead" (a system cause) or "answered"
    totals = {}     # session id -> the total its last answer reported: a --resume result is the whole session so far

    def ask(call, wall, gaps_only=False):
        """-> (exit code, the well-formed verdict (or, gaps_only, a {gaps} answer) or None, session id). Charges what
        the call spent."""
        def unmeasured(why):
            # the call ran and its spend cannot be read: counted at the p90 by spend(), charged unmeasured
            rec["unmeasured_calls"] = int(rec.get("unmeasured_calls") or 0) + 1
            rec.setdefault("unmeasured_why", why)
            if charge:
                try:
                    DS.charge(d, 0, "unmeasured", unit)
                except Exception as e:  # noqa: BLE001
                    rec["charge_error"] = str(e)
        try:
            code, out = runner(spend_watchdog.wrap(call, BUDGET_USD), repo, env, wall)   # the cap, from outside
        except OSError as e:     # never launched: nothing was spent
            rec["error"] = "the judge did not answer: %s" % e
            rec["error_kind"] = "system"     # a dead call: a timeout, no process, output that is no JSON
            rec.setdefault("dead_calls", []).append(rec["error"])
            calls.append("dead")
            return None, None, None
        except subprocess.SubprocessError as e:   # it ran (a timeout): its spend is unknown
            rec["error"] = "the judge did not answer: %s" % e
            rec["error_kind"] = "system"     # a dead call
            rec.setdefault("dead_calls", []).append(rec["error"])
            calls.append("dead")
            unmeasured("the call did not finish: %s" % e)
            return None, None, None
        try:
            res = json.loads(out or "null")
        except ValueError as e:
            res = None
            rec["error"] = "the judge did not answer: %s" % e
        if isinstance(res, dict) and not is_cli_result(res):
            res = None      # {} or another envelope: no result of its own (Codex review r2-3)
            rec["error"] = "the judge's output is a JSON object but no CLI result of its own (exit %s)" % code
        if not isinstance(res, dict):
            rec.setdefault("error", "the judge's output is not a JSON result (exit %s)" % code)
            rec["error_kind"] = "system"     # the CLI exited with no result of its own
            rec.setdefault("dead_calls", []).append(rec["error"])
            calls.append("dead")
            unmeasured("no JSON result to measure")
            return code, None, None
        calls.append("answered")
        tok = None
        try:
            import role_launch as RL
            tok = RL.run_tokens(res, MODEL)         # modelUsage when the result has it; else usage as MODEL
            rec["token_unit"] = RL.TOKEN_UNIT
        except Exception as e:  # noqa: BLE001 - a charge we cannot measure is recorded as unmeasured, never fatal
            tok = None
            rec["unmeasured_why"] = str(e)    # an unknown model is named here, never weighed as another
        total = tok
        if "--resume" in call:      # its own part (RIMMANDRAKE_COUNT_JUDGE_AND_ART_REASK_TOKENS_ONCE)
            import detached_helper as DH
            sid = call[call.index("--resume") + 1]
            tok, total = DH.session_part(tok, totals.get(sid), res.get("stopped_by") == "spend_watchdog")
            if tok is None and total is not None:
                rec["unmeasured_why"] = "a resume of session %s whose earlier total no ask recorded" % sid
        totals[res.get("session_id")] = total
        rec["tokens"] = (rec.get("tokens") or 0) + tok if tok is not None else rec.get("tokens")
        if tok is None:
            rec["unmeasured_calls"] = int(rec.get("unmeasured_calls") or 0) + 1
        if charge:
            try:
                DS.charge(d, tok or 0, "review" if tok is not None else "unmeasured", unit)
            except Exception as e:  # noqa: BLE001
                rec["charge_error"] = str(e)
        so = res.get("structured_output")
        ok = isinstance(so, dict) and isinstance(so.get("gaps"), list) and (gaps_only or (
            so.get("verdict") in ("covered", "not_covered") and isinstance(so.get("checklist"), list)))
        bad = shape_errors(so, gaps_only) if ok else []
        if not ok:
            rec["error"] = "no well-formed verdict (exit %s)" % code
            rec["error_kind"] = "judge"      # it answered: its own failure (a cap, a broken answer) counts
        elif bad:
            rec["error"] = "no well-formed verdict (exit %s): %s" % (code, "; ".join(bad))
            rec["error_kind"] = "judge"      # it answered, in a shape the program cannot read: its own failure
            ok = False
        elif code != 0:
            # RIMMANDRAKE_HASH_EVERY_COVERAGE_INPUT: a runner that failed is not trusted for its verdict, however well formed
            rec["error"] = "the judge's runner exited %s: its verdict is not taken" % code
            rec["error_kind"] = "judge"
            ok = False
        return code, so if ok else None, res.get("session_id")

    started = time.monotonic()
    _code, so, session = ask(argv, timeout)
    missing = missing_rows(ids, so["checklist"]) if so else []
    left = timeout - (time.monotonic() - started)
    if missing and session and left >= REASK_MIN_S:
        rec["reasked"] = list(missing)
        _code, so2, _s = ask([CLAUDE, "-p", "Your checklist has no row, or a row with no parts, for: %s. Check those now and "
                              "answer again with the whole verdict: every row, every gap." % ", ".join(missing),
                              "--resume", session] + tail, left)
        if so2:  # an answer that came back broken leaves the first one standing
            so, missing = so2, missing_rows(ids, so2["checklist"])
        rec.pop("error", None)
        rec.pop("error_kind", None)
    def take(so, missing):
        """Fold one well-formed answer into rec (a later answer in the same session replaces an earlier one)."""
        extra = [dict(g, from_rows=True) for g in failed_part_gaps(so["checklist"], so["gaps"])]
        rec.update(verdict=so["verdict"], checklist=so["checklist"], gaps=so["gaps"] + extra,
                   reasons=str(so.get("reasons") or ""))
        for k in ("unchecked", "late", "dropped", "advisory_gaps", "covered_by_bar_rule", "answered", "repairs",
                  "malformed"):
            rec.pop(k, None)
        if extra and rec["verdict"] == "covered" and not so["gaps"]:
            rec["verdict"] = "not_covered"  # its own rows failed: the rows outrank the word
        if missing:
            rec["unchecked"] = missing
        if slotted:
            # None (the key absent) is the old form, read by its rows; a value that is there but not a list answers
            # no slot, so every slot stays open
            repairs = None if "repairs" not in so else so["repairs"] if isinstance(so["repairs"], list) else []
            if repairs is not None:
                rec["repairs"] = repairs
            if dp is not None:
                delta_merge(rec, dp, repairs)
                # the delta's scope never decides a new finding: one it dropped that names no slot is judged by rule 4
                # like any other (a passage a repair changed blocks wherever its rows are)
                back = [g for g in rec.get("dropped") or [] if not g.get("names_slot")]
                rec["gaps"] = list(rec["gaps"]) + [{k: v for k, v in g.items() if k != "dropped"} for g in back]
                rec["dropped"] = [g for g in rec.get("dropped") or [] if g.get("names_slot")]
                if not rec["dropped"]:
                    rec.pop("dropped")
            else:
                rejudge_slots(rec, prior, repairs)
            classify_new(rec, prior.get("entry_text"), texts, prior.get("judge"))
            # the verdict is derived, never the word (rule 5); the bar rule may still move a gap to advisory
            rec["verdict"] = "not_covered" if rec["gaps"] else "covered"
            apply_bar_rule(rec)
            return
        if dp is not None:
            delta_merge(rec, dp)
        late = tag_gaps(rec["gaps"], earlier)
        if dp is None and prior is not None:
            retag_against_prior(rec["gaps"], prior, hashes)
            late = [i for g in rec["gaps"] if g.get("new_since") == "late" for i in g.get("ids") or []]
        if late:
            rec["late"] = late
        refuser = dp["against"] if dp is not None else last_refuser(st0, d)
        for g in rec["gaps"]:
            if g.get("new_since") == "late" and refuser:
                g["miss_of"] = refuser   # an earlier look refused and was told to list every gap: this is its miss
        if dp is not None and rec.get("dropped"):
            for g in rec["dropped"]:   # a dropped gap is shown too, never counted
                g.setdefault("advisory_why", g.get("dropped"))
        apply_bar_rule(rec)
        if rec["verdict"] == "not_covered" and not rec["gaps"]:
            # a refusal that names nothing to repair is no refusal (a look's verdict is its gaps, rule 5): malformed,
            # so it neither spends a refusal nor signs; rows it left unchecked are not a gap the Designer can fix
            rec.update(verdict="malformed", malformed=[
                "a not_covered verdict that names no gap and no failed part: nothing to repair"
                + (" (rows unchecked: %s)" % ", ".join(rec["unchecked"]) if rec.get("unchecked") else "")])

    if so:
        take(so, missing)
    if CONTRACT and rec.get("verdict") == "not_covered":
        # The refusal contract (RIMMANDRAKE_EMIT_REFUSAL_RECORDS_FROM_JUDGE_BRIEFS): a refusal that names no attainable
        # path to pass is refused itself, re-asked once in the same session, and if still malformed recorded as
        # `malformed`: it never counts as a not_covered round and never sends the Designer back.
        # A broken record must not void the look (RIMMANDRAKE_SPEND_PYRELANDS_LOOK_ON_MALFORMED_REFUSAL): when every
        # error is one record's, only those records are re-asked (at most ROW_REASK_MAX times); one still broken is
        # kept on file marked `malformed`, is not submitted, and the well-formed rows are the stored verdict.
        cv, given, errs = contract_errors(d, rec, st0.get("item"))
        dead0 = len(rec.get("dead_calls") or [])    # a re-ask below that dies leaves a malformed verdict nobody judged
        calls0 = len(calls)
        left = timeout - (time.monotonic() - started)
        if errs and session and left >= REASK_MIN_S and row_errors(errs, cv)[1]:
            rec["contract_reasked"] = errs
            _c, so3, _s = ask([CLAUDE, "-p", "Your verdict's refusal records do not meet the refusal contract:\n%s\n"
                               "Answer again with the whole verdict, every row and every gap, each gap a complete record."
                               % "\n".join("- %s" % e for e in errs), "--resume", session] + tail, left)
            if so3:  # an answer that came back broken leaves the first one standing
                missing = missing_rows(ids, so3["checklist"])
                take(so3, missing)
                errs = contract_errors(d, rec, st0.get("item"))[2] if rec["verdict"] == "not_covered" else []
                cv, given = contract_verdict(d, rec, st0.get("item"))
            rec.pop("error", None)
            rec.pop("error_kind", None)
        tries = 0
        while errs and rec.get("verdict") == "not_covered" and session and tries < ROW_REASK_MAX:
            rows, glob = row_errors(errs, cv)
            bad = gaps_of(rec, rows)
            if glob or not bad or timeout - (time.monotonic() - started) < REASK_MIN_S:
                break
            tries += 1
            rec.setdefault("rows_reasked", []).append(sorted(rows))
            _c, so4, _s = ask([CLAUDE, "-p", row_reask_text(rows, cv, given, bad), "--resume", session]
                              + tail_for(GAPS_SCHEMA), timeout - (time.monotonic() - started), gaps_only=True)
            rec.pop("error", None)
            rec.pop("error_kind", None)
            new = [g for g in (so4 or {}).get("gaps") or [] if isinstance(g, dict)]
            want = {i for g in bad for i in g.get("ids") or [REST_CLAUSE]}
            if not new or not want <= {i for g in new for i in g.get("ids") or [REST_CLAUSE]}:
                continue   # an answer that drops a refused id would lose a refusal: the old records stand
            at = rec["gaps"].index(bad[0])
            rest = [g for g in rec["gaps"] if not any(g is b for b in bad)]
            rec["gaps"] = rest[:at] + new + rest[at:]
            if slotted:
                reopen_named(rec, new, prior_slots(prior))
                classify_new(rec, prior.get("entry_text"), texts, prior.get("judge"))
                rec["verdict"] = "not_covered" if rec["gaps"] else "covered"
            else:
                late = tag_gaps(new, earlier)
                if late:
                    rec["late"] = sorted(set(rec.get("late") or []) | set(late))
            apply_bar_rule(rec)
            if rec.get("verdict") != "not_covered":
                errs = []
                break
            cv, given, errs = contract_errors(d, rec, st0.get("item"))
        if errs and rec.get("verdict") == "not_covered":
            rows, glob = row_errors(errs, cv)
            bad = gaps_of(rec, rows)
            if bad and not glob:
                for g in bad:
                    g["malformed"] = [e for c in g.get("ids") or [REST_CLAUSE] for e in rows.get(c, [])]
                cv2, given2, errs2 = contract_errors(d, rec, st0.get("item"))
                if cv2["refusals"] and not errs2:
                    rec["malformed_rows"] = [{"clause": c, "errors": rows[c]} for c in sorted(rows)]
                    cv, given, errs = cv2, given2, []
                else:   # nothing well formed is left to stand: the whole look is malformed, as before
                    for g in bad:
                        g.pop("malformed", None)
        unread = None
        if rec.get("verdict") == "not_covered" and not errs:
            # the judge does not grade its own criterion: a second reader does, and may file a gap's kind as advisory
            if reader == "auto":
                reader = llm_reader(d, repo, unit, charge) if runner is default_runner else None
            owed = [g for g in rec.get("gaps") or [] if never_read(g)]   # carried from a look no reader graded
            unread = second_read(rec, dict(cv["given"]["criteria"] if "given" in cv else given["criteria"],
                                           **carried_criteria(d, rec)), reader)
            for g in owed:
                if g.get("criterion_by") != NO_READ:
                    g["first_read_at"] = unit   # this look gave it the reading its own look never had
            if getattr(reader, "dead", None):
                rec["reader_void_system"] = reader.dead
            apply_bar_rule(rec)
            if rec.get("verdict") == "not_covered":
                cv, given, errs = contract_errors(d, rec, st0.get("item"))
        if rec.get("verdict") == "not_covered" and unread and not errs:
            rec["contract"] = {"ok": True, "submitted": False, "why": unread}
            rec["advisory"] = unread
        elif rec.get("verdict") == "not_covered":
            # void only when the LAST repair attempt died: a later re-ask that answered malformed is the judge's own
            dead = (rec.get("dead_calls") or [])[dead0:] if calls[calls0:] and calls[-1] == "dead" else []
            if errs and dead:
                # the re-ask that would have repaired the records died: the malformed verdict is the dead call's, so it
                # is not submitted (the refusal contract counts no malformed verdict for it) and the round is void_system
                rec["contract"] = {"ok": False, "submitted": False, "void_system": dead[-1]}
                rec["void_system"] = "a re-ask of its refusal records died (%s): its malformed verdict counts nothing" % (
                    _clip(dead[-1], 120))
            else:
                rec["contract"] = {k: v for k, v in RC.submit(cv, given).items() if k != "errors"}
            if errs:
                rec.update(verdict="malformed", malformed=errs)
            elif rec["contract"].get("advisory"):   # T6: only a CALIBRATED brief's refusal sends the Designer back
                rec["advisory"] = ("the coverage brief is %s: this refusal is stored and shown, the Designer is not "
                                   "sent back" % rec["contract"].get("calibration"))
            # the binding grade is the second reader's; a judge confessing its own criterion flawed is heard too
            bad_c = {i for g in rec.get("gaps") or [] if g.get("judge_criterion_verdict") in ("flawed", "unattainable")
                     for i in g.get("ids") or [REST_CLAUSE]}
            # a carried gap is in no refusal record (contract_verdict): its grade, from whichever look read it, is heard
            late_c = {i for g in rec.get("gaps") or [] if g.get("carried")
                      and g.get("criterion_verdict") in ("flawed", "unattainable") for i in g.get("ids") or [REST_CLAUSE]}
            suspect = [r["clause"] for r in cv["refusals"] if r.get("criterion_verdict") in ("flawed", "unattainable")
                       or r["clause"] in bad_c] + sorted(late_c - {r["clause"] for r in cv["refusals"]})
            if suspect and not errs:
                rec["criteria_suspect"] = suspect
    if rec.get("verdict") == "not_covered":
        stale = moved_inputs(d, before)
        if stale:
            # judged on inputs that changed under it: no strike, no park, no stop, and the Designer is not sent back
            # on it; the next look judges what is there now
            rec["stale_inputs"] = stale
            rec["advisory"] = ("the %s changed while the judge read it: this refusal judged inputs that are gone; it is "
                               "stored and shown and counts as no refusal" % ", ".join(stale))
    if rec["verdict"] == "covered":
        rec["calibration"] = RC.status(CONTRACT_FAMILY)
        try:
            tree2, tree_err = CT.load(d), None
        except (OSError, ValueError) as e:
            tree2, tree_err = None, e
        if tree_err is not None:
            rec["error"] = "tree.json could not be read when the judge answered (%s): not signed" % tree_err
        elif missing:
            rec["error"] = "a covered verdict with no row for %s is not a covered verdict: not signed" % ", ".join(missing)
        elif fresh_key(d, tree2) != before:
            moved = [fn for fn, h in before[2].items() if fresh_key(d, tree2)[2].get(fn) != h]
            rec["error"] = "the %s changed while the judge read it: not signed" % (
                ", ".join(moved) if moved else "tree or sheet")
        elif rec.get("gaps"):
            rec["error"] = "a covered verdict that lists gaps is not a covered verdict: not signed"
        elif rec["calibration"] != "CALIBRATED":
            # RIMMANDRAKE_EARN_CALIBRATION_BOTH_WAYS: a gate trusted one way only is no gate; covered signs only
            # under a CALIBRATED brief, as not_covered binds only under one
            rec["advisory"] = ("the coverage brief is %s: this covered verdict is stored and shown, nothing is signed"
                               % rec["calibration"])
        else:
            old = os.environ.get("RM_ROLE_UNIT")
            os.environ["RM_ROLE_UNIT"] = unit
            try:
                errs = CT.sign(d, CT.SIGNER, repo, expect=before[0])
            finally:
                if old is None:
                    os.environ.pop("RM_ROLE_UNIT", None)
                else:
                    os.environ["RM_ROLE_UNIT"] = old
            if errs:
                rec["error"] = "sign refused: %s" % "; ".join(errs)
            else:
                rec["signed"] = True
    number_gaps(rec.get("gaps") or [])
    if not _usable(rec) and prior:
        rec["baseline"] = {k: v for k, v in prior.items() if k != "baseline"}   # rule 6: the retry checks the same slots
    DS.write_json(os.path.join(d, VERDICT_FILE), rec)
    st = record_round(d, rec)
    msg = "signed" if rec["signed"] else "not signed: %s" % (rec.get("error") or "%d gap(s)" % len(rec.get("gaps") or []))
    parked = None
    if not rec["signed"]:
        parked = DS.loop_ceiling(st) and ("ceiling", DS.loop_ceiling(st))
        if not parked and is_refusal(rec) and DS.refusals_since_loop(st) >= 2 \
                and not DS.designer_can_fix(rec):   # gaps the Designer fixes alone are rework, not his question
            away, why_away = DS.owner_away()
            if away:    # the second refusal while he is away parks (RIMMANDRAKE_PARK_UNATTENDED_DESIGNER_LOOPS)
                parked = ("second_refusal", "the coverage judge refused %d times while you are away (%s)" % (
                    DS.refusals_since_loop(st), why_away))
    if parked:
        rec["parked"] = parked[1]
        DS.write_json(os.path.join(d, VERDICT_FILE), rec)
        DS.park(d, parked[0], parked[1], repo)
        return rec, msg + "; parked: %s" % parked[1]
    # a stale refusal stops nothing here: the next plan() reads the caps against the stage state then current, so
    # hold() never writes blocked over a state that moved while the judge read it
    stop = None if rec["signed"] or rec.get("stale_inputs") else stop_reason(st, d)
    if stop:
        rec["stopped"] = stop
        DS.write_json(os.path.join(d, VERDICT_FILE), rec)
        hold(d, stop, now)
        msg += "; stopped: %s" % stop
    if rec["signed"] or stop:   # the coverage stage closes, either way: its four counts
        msg += "; %s" % close_line(close_counts(DS.load_state(d), d))
    return rec, msg


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("dir")
    r.add_argument("--timeout", type=int, default=TIMEOUT_S)
    s = sub.add_parser("status")
    s.add_argument("dir")
    s.add_argument("--would-judge", action="store_true", help="exit 0 only when plan() says judge; skip, stopped, parked "
                   "and ceiling exit 1; error (could not look) exits 126 (RIMMANDRAKE_PREVIEW_THREE_GATES_READ_ONLY_FOR_"
                   "LAUNCH_CHECKS)")
    rl = sub.add_parser("release", help="one more judge look on a stopped concept")
    rl.add_argument("dir")
    rl.add_argument("--why", required=True)
    rl.add_argument("--after", action="append", default=[], metavar="ITEM",
                    help="grant the look now, taking effect after ITEM closes and the re-pin lands (repeatable)")
    a = ap.parse_args(argv)
    d = os.path.abspath(a.dir)
    if a.cmd == "status":
        what, why = plan(d)
        print("%s: %s" % (what, why))
        if a.would_judge:
            return WOULD_JUDGE_EXIT.get(what, 126)
        return 2 if what == "error" else 0
    if a.cmd == "release":
        try:
            st = release(d, a.why, after=a.after)
        except (DS.Refused, OSError, ValueError) as e:
            print("coverage_judge: release refused: %s" % e)
            return 2
        if a.after:
            print("coverage_judge: granted %s one final look, after %s close and the re-pin lands (status %s)" % (
                os.path.basename(d), ", ".join(a.after), st.get("status")))
            return 0
        print("coverage_judge: released %s for one %slook (status %s)" % (
            os.path.basename(d), "final " if (st.get("coverage_releases") or [{}])[-1].get("final") else "more ",
            st.get("status")))
        return 0
    what, why = plan(d)
    if what == "error":
        print("coverage_judge: %s" % why)
        return 2
    rec, msg = run(d, timeout=a.timeout)
    print("coverage_judge: %s" % msg)
    return STOP_EXIT if stop_exit(rec) else 0


if __name__ == "__main__":
    sys.exit(main())
