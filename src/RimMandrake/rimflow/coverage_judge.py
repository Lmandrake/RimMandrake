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

One pass lists every gap (DESIGNER_GAPJUDGE_FIX_ONE_BATCH_PER_ROUND: Pyrelands' judge named 8 gaps, then 6 different ones,
each batch costing a write, exam and judge cycle; 9.3M tokens, 8 chained runs in a day). The verdict carries a checklist
with a row for every inventory capability and tree leaf, each row naming every built part and the scene that tests it. A
missing row is re-asked once in the same session and still missing is kept in `unchecked` (a covered verdict with one
never signs); a failed part no gap names becomes a gap. A re-judge reads the previous verdict, so a passed row whose scene
did not change reopens only for a defect it can quote.

  release <dir> --why TEXT     a concept stopped by the loop limit gets one more judge look; a look that does not cover
                               stops it again

The loop limit (RIMMANDRAKE_STOP_COVERAGE_LOOP_AT_THIRD_REFUSAL): every verdict is a round in stage.json coverage_rounds
(judges charged before the limit existed count from the budget charges). The third not_covered, a fourth judge run or
judge spend past JUDGE_SPEND_MAX stops judging: the concept is blocked on REFUSAL_NOTHING_COULD_EVER_PASS, the alarm row is
raised (refusal_contract.py) and `run` exits 3, so the Designer's run never starts. A later gap on ids no earlier verdict
named, that the judge does not tie to a change, is tagged late: the earlier pass missed it.

Parked for him (RIMMANDRAKE_PARK_UNATTENDED_DESIGNER_LOOPS, RIMMANDRAKE_CEIL_JUDGE_LOOPS_AT_TWICE_CAP; designer_stage
park): when he is away (designer_stage.owner_away) the SECOND not_covered parks the concept instead of waiting for the
third, and a loop whose charges since the first judge reach twice the cap parks it whoever is there. A park writes
park_summary.md for him and sets waiting_owner; `run` exits 3 while it stands, `release` refuses it, and only his own
word on the item lifts it.

Exit: 0 for a no-op, a verdict or a refusal the Designer reads (the pre-launch step must not stop the Designer's run: its
stage-5 gate refuses without the signature anyway); 3 when judging is stopped (the run must not start); 2 for an
unreadable concept.
What this cannot do, said plainly: a verdict of "covered" is one model's judgment, not proof; RM_ROLE_UNIT is an
environment variable, so a writer who sets it by hand forges the ledger note too (an attributable line in git).
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import concept_tree as CT  # noqa: E402
import designer_stage as DS  # noqa: E402
import refusal_contract as RC  # noqa: E402

CLAUDE = shutil.which("claude") or os.path.expanduser("~/.local/bin/claude")  # systemd's PATH lacks ~/.local/bin (OPS_TIMER_REPAIR_PRXC)

VERDICT_FILE = "coverage_verdict.json"
TIMEOUT_S = 1500        # the judge's own wall bound; the Designer schedule's pre_launch_max_s holds it plus slack
MODEL = "opus"
REASK_MIN_S = 120       # less judge time than this left: no re-ask, the missing rows go on file as unchecked
# The loop limit (RIMMANDRAKE_STOP_COVERAGE_LOOP_AT_THIRD_REFUSAL, spec 2026-11-12 refusal contract §3). EK's judge said
# not_covered 9 times in 3 h. The third not_covered on one concept, a 4th judge run, or judge spend past 4x the measured
# p90 stops judging: the concept is blocked on the alarm and the Designer's run never starts. `release` grants one look.
NOT_COVERED_LIMIT = 3
JUDGE_RUNS_MAX = 4
JUDGE_P90_TOKENS = 751818   # measured 2026-11-12: 12 measured judge runs (EK 8, GimmeSomeSlack 2, Pyrelands 2), median 706,708
JUDGE_SPEND_MAX = 4 * JUDGE_P90_TOKENS   # an unmeasured judge run counts at the p90, never at 0
STOP_EXIT = 3               # `run` exit when stopped: the pre-launch chain ends and the Designer's claude never starts
UNIT_PREFIX = "rm-coverage-judge-"
# how a later round's gap stands against the earlier verdicts: first (round 1 only), unfixed (named before, still open),
# changed (new because an artifact changed since; `since` names it), regression (passed before, broken by a change),
# late (it was there before and the earlier judge missed it). The program tags `late` itself when the ids are new and
# the judge claims no change: a judge miss, counted in the round.
TAGS = ("first", "unfixed", "changed", "regression", "late")
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
RECORD_TEXT = (
    "\n\nEvery gap is a refusal record, as detailed as the evidence it refuses, with a path to pass: `evidence` lists "
    "the concept files it rests on (sheet.md, tree.json, scenes.json, floor.json, exam.json, record.json; `file:line` "
    "where a line decides it); `observed` says what that evidence shows, quoting at least one of its words; `would_pass` "
    "is the concrete result that would pass, checkable by a script or a fresh judge (not the clause restated, never "
    "'insufficient' or 'needs more work'); `smallest_fix` is the smallest change that reaches it (`what` names the "
    "files, scenes or leaves; `attainable` yes/no; `cost` edit, rerun, new instrument or owner); `criterion_verdict` "
    "judges the criterion itself: `sound`, `flawed` (wrong or ambiguous) or `unattainable` (nothing could ever pass "
    "it), with `criterion_why`, a sentence, whatever the verdict. A flawed or unattainable criterion goes to a neutral "
    "fixer, not back to the Designer. Each checklist row's `evidence` names the files its parts rest on, so every file "
    "you were given is cited by some row or gap. A refusal without these is itself refused and re-asked once.")
SCHEMA = {"type": "object", "additionalProperties": False, "required": ["verdict", "checklist", "gaps", "reasons"],
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
                                                                          "new_since"] + list(RECORD_FIELDS),
                                                             "properties": dict(RECORD_PROPS, **{
                                                                 "what": {"type": "string"},
                                                                 "where": {"type": "string"},
                                                                 "return_to": {"enum": [2, 3]},
                                                                 "ids": {"type": "array", "items": {"type": "string"}},
                                                                 "new_since": {"enum": list(TAGS)},
                                                                 "since": {"type": "string"},
                                                                 "late_why": {"type": "string"}})}},
                         "reasons": {"type": "string"}}}


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


def prior_verdict(d):
    """The verdict an earlier judge left here, when it reached one (an errored run left nothing to carry on from)."""
    try:
        rec = DS.read_json(os.path.join(d, VERDICT_FILE))
    except DS.Refused:
        return None
    return rec if isinstance(rec, dict) and rec.get("verdict") in ("covered", "not_covered") else None


# Re-judge only what changed (RIMMANDRAKE_REJUDGE_ONLY_CHANGED_GAPS, owner fix D, OWNER.jsonl:1794527688430451936).
# Every verdict keeps a hash per judged entry and numbers its gaps g1..gN. After round 1 the Designer names the gaps it
# fixed in coverage_fixes.json ({"against": <that verdict's judge>, "claims": [{"gap": "g3", "evidence": "..."}]}); the
# next judge is shown only those gaps with their evidence and the entries whose hash changed, whole. A gap not claimed
# stays open, carried. A new gap on material that did not change counts only tagged late with `late_why`. Nothing
# claimed and nothing changed: no judge runs at all. A prior verdict with no hashes (or one that errored, left rows
# unchecked or covered) gets a full judge, which leaves hashes for the next.
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
    text = read("sheet.md")
    if text is not None:
        head, body = "", []
        for line in text.splitlines():
            if line.startswith("## "):
                out["sheet:%s" % head] = "\n".join(body)
                head, body = line[3:].strip(), []
            body.append(line)
        out["sheet:%s" % head] = "\n".join(body)
    return out


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
    gids = {g.get("gid") for g in prior.get("gaps") or [] if isinstance(g, dict)}
    ok, refused, seen = [], [], set()
    for c in f.get("claims") or []:
        gap = c.get("gap") if isinstance(c, dict) else None
        if gap not in gids:
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
            and all(isinstance(g, dict) and g.get("gid") for g in prior.get("gaps") or [])):
        return None
    now_ents = entries(d, read)
    now_h = entry_hashes(d, read)
    old_h = prior["hashes"]
    changed = sorted(k for k in set(old_h) | set(now_h) if old_h.get(k) != now_h.get(k))
    claims, refused = fix_claims(d, prior)
    claimed = {c["gap"] for c in claims}
    gaps = [g for g in prior.get("gaps") or [] if isinstance(g, dict)]
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
            "listed every gap; the Designer says it fixed some of them. You judge ONLY what is below. Read "
            "src/RimMandrake/rimflow/roles/designer_scene_contract.md (the proof-scene contract) first. Do not reread the "
            "concept's files whole: everything to judge is quoted here, and you open a file only at the place a claim's "
            "evidence names, to check it. Do not read result.*.json, log.md, stage.json or any transcript, and edit "
            "nothing. The third not_covered verdict stops judging, so be whole on what you are shown." % (rel, round_no),
            "", "## Gaps the Designer claims fixed (check each: still open -> a gap tagged `unfixed`)"]
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
    body += ["", "## Gaps still open, carried on file (do not repeat them)"]
    body += ["- %s: %s" % (g.get("gid"), " ".join(str(g.get("what") or "").split())) for g in dp["carried"]] or ["(none)"]
    body += ["", "Write `checklist` with one row for each of these ids, none skipped: %s. A gap on anything not shown "
             "above counts only tagged `late` with `late_why` saying why the earlier pass could not have seen it; "
             "otherwise it is dropped. Answer `covered` only when every claimed gap is fixed and no change opened one."
             % (", ".join(dp["ids"]) or "(none)")]
    return "\n".join(body) + RECORD_TEXT


def delta_merge(rec, dp):
    """Fold a delta judge's answer into a whole verdict: the gaps it found within what it was shown (plus late gaps
    with a why), every carried gap, and the prior rows it did not redo. Carried gaps keep a covered word from standing."""
    scope = set(dp["ids"])
    kept, dropped = [], []
    for g in rec.get("gaps") or []:
        ids = set(g.get("ids") or [])
        if (ids & scope) or (not ids and dp["loose"]) or (g.get("new_since") == "late" and CT.txt(g.get("late_why"))):
            kept.append(g)
        else:
            dropped.append(dict(g, dropped="a new gap on material that did not change, not tagged late with a why"))
    carried = [dict(g, carried=True, new_since="unfixed") for g in dp["carried"]]
    redone = {r.get("id") for r in rec.get("checklist") or [] if isinstance(r, dict)}
    rec["checklist"] = list(rec.get("checklist") or []) + [
        r for r in dp.get("prior_checklist") or [] if isinstance(r, dict) and r.get("id") not in redone]
    rec["gaps"] = kept + carried
    if dropped:
        rec["dropped"] = dropped
    if carried and rec.get("verdict") == "covered":
        rec["verdict"] = "not_covered"
    return rec


def rounds(st, d=None):
    """-> every judge round on this concept, oldest first: stage.json's coverage_rounds, plus each earlier judge the
    budget charges name with no round on file (before the loop limit existed). An old round's verdict is known only when
    coverage_verdict.json is that judge's; its tokens are its charges, or the p90 when it was charged unmeasured."""
    recorded = [r for r in st.get("coverage_rounds") or [] if isinstance(r, dict)]
    known = {r.get("judge") for r in recorded}
    last = prior_verdict(d) if d else None
    legacy = {}
    for c in (st.get("budget") or {}).get("charges") or []:
        ref = c.get("ref") if isinstance(c, dict) else None
        if isinstance(ref, str) and ref.startswith(UNIT_PREFIX) and ref not in known:
            r = legacy.setdefault(ref, {"judge": ref, "at": c.get("at"), "verdict": None, "tokens": 0, "legacy": True})
            if c.get("kind") == "unmeasured" or r["tokens"] is None:
                r["tokens"] = None
            else:
                r["tokens"] += int(c.get("tokens") or 0)
    for r in legacy.values():
        if last and last.get("judge") == r["judge"]:
            r["verdict"] = last.get("verdict")
    return sorted(legacy.values(), key=lambda r: str(r.get("at"))) + recorded


def spend(rs):
    return sum(JUDGE_P90_TOKENS if r.get("tokens") is None else int(r["tokens"]) for r in rs)


def stop_reason(st, d=None):
    """-> why judging stops on this concept now, or None. After a release, exactly one more look: a look that did
    not cover stops again."""
    rs = rounds(st, d)
    rel = [x for x in st.get("coverage_releases") or [] if isinstance(x, dict)]
    if rel:
        after = rs[int(rel[-1].get("rounds_at") or 0):]
        if after and after[-1].get("verdict") != "covered":
            return "released for one more look at round %d; that look was %s" % (
                len(rs) - len(after) + 1, after[-1].get("verdict") or "no verdict")
        return None
    nc = sum(1 for r in rs if r.get("verdict") == "not_covered")
    bad = sum(1 for r in rs if r.get("verdict") == "malformed")
    if bad >= MALFORMED_LIMIT:
        return "%d malformed verdicts (limit %d): the coverage brief FAILED its refusal contract" % (bad, MALFORMED_LIMIT)
    if nc >= NOT_COVERED_LIMIT:
        return "%d not_covered verdicts (limit %d)" % (nc, NOT_COVERED_LIMIT)
    if len(rs) >= JUDGE_RUNS_MAX:
        return "%d judge runs (limit %d)" % (len(rs), JUDGE_RUNS_MAX)
    if spend(rs) >= JUDGE_SPEND_MAX:
        return "judge spend %d tokens (limit %d, 4x the p90)" % (spend(rs), JUDGE_SPEND_MAX)
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


def release(d, why, now=None):
    """One more look, said with a reason: the block lifts and the next judge run counts as the last before a stop."""
    import refusal_contract as RC
    if not CT.txt(why):
        raise DS.Refused("a release says why")
    st = DS.load_state(d)
    if DS.standing_park(st, d):
        raise DS.Refused("parked for him (%s): only his word on %s lifts a park, not a release" % (
            st["park"].get("kind"), st.get("item")))
    st.setdefault("coverage_releases", []).append({"at": DS.now_iso(), "why": why, "rounds_at": len(rounds(st, d))})
    st.pop("coverage_stop", None)
    if st.get("status") == "blocked" and str(st.get("blocked_on") or "").startswith(RC.ALARM_ID):
        st["status"] = "ready"
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


def contract_verdict(d, rec, item):
    """-> (verdict, given): a coverage verdict in the refusal contract's form (refusal_contract.py). One clause per
    checklist id (its text is the inventory row or tree leaf it names) plus `rest` for a gap on no single row; every row
    no gap names is passed with its evidence; each gap the judge wrote this round is a refusal of each id it names (two
    gaps on one id are one record, and a refused row's evidence joins it). Carried gaps were checked when written and are left out, with their ids. A full
    judge is given the concept files; a delta judge is shown quoted entries, so its given inputs are the files it cites
    and `contract_errors` adds that each is a concept file."""
    ent = entries(d)
    gaps = [g for g in rec.get("gaps") or [] if isinstance(g, dict)]
    mine = [g for g in gaps if not g.get("carried")]
    carried = {i for g in gaps if g.get("carried") for i in g.get("ids") or []}
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
    if REST_CLAUSE not in refused:
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
    given = {"inputs": inputs, "criteria": crit, "root": d}
    verdict = {"item": str(item or os.path.basename(d)), "family": CONTRACT_FAMILY,
               "sha": str(rec.get("tree") or CT.tree_hash(CT.load(d))), "given": given,
               "passed": passed, "refusals": list(refused.values())}
    return verdict, given


def contract_errors(d, rec, item):
    """-> (verdict, given, errors): the contract form and why it is malformed ([] = well formed)."""
    v, given = contract_verdict(d, rec, item)
    errs = RC.check(v, given)
    if rec.get("mode") == "delta":
        errs += ["evidence %r is not a concept file (%s)" % (i, ", ".join(INPUT_FILES))
                 for i in given["inputs"] if i not in INPUT_FILES]
    return v, given, errs


def stop_exit(rec):
    """True when the pre-launch step must stop the Designer's run: judging stopped, parked, or the verdict refused
    itself (a malformed refusal never sends the Designer back to rework)."""
    return isinstance(rec, dict) and bool(rec.get("stopped") or rec.get("parked") or rec.get("malformed"))


def record_round(d, rec):
    """stage.json coverage_rounds gets this round: verdict, gap count and ids, tags, late ids, tokens, tree."""
    st = DS.load_state(d)
    gaps = rec.get("gaps") or []
    st.setdefault("coverage_rounds", []).append({
        "judge": rec["judge"], "at": rec["at"], "verdict": rec.get("verdict"), "tree": rec.get("tree"),
        "tokens": rec.get("tokens"), "gaps": len(gaps),
        "ids": sorted({i for g in gaps for i in g.get("ids") or []}),
        "tags": {t: sum(1 for g in gaps if g.get("new_since") == t) for t in TAGS if any(
            g.get("new_since") == t for g in gaps)},
        "late": rec.get("late") or [], "error": rec.get("error")})
    DS.write_json(DS.state_path(d), st)
    return st


def earlier_gaps(st, d):
    """The gaps earlier rounds named: the previous verdict's in full, and every recorded round's ids."""
    out = [{"ids": r.get("ids") or []} for r in st.get("coverage_rounds") or [] if isinstance(r, dict)]
    last = prior_verdict(d)
    if last:
        out += [g for g in last.get("gaps") or [] if isinstance(g, dict)]
    return out


def prompt(d, repo, ids=(), prior=False, round_no=1):
    rel = CT.concept_rel(d, repo)
    again = ("A previous judge's verdict is in %s/%s. Check each of its gaps first. A part it passed whose scene has not "
             "changed since stays passed unless you can quote the defect in the scene or the code. Tag every gap's "
             "`new_since`: `unfixed` (that verdict named it and it is still open), `changed` (it is new because an "
             "artifact changed since that verdict; `since` names the file and what changed), `regression` (that verdict "
             "passed it and a change broke it; `since` names the change), or `late` (it was there then and that judge "
             "missed it: say so). A gap on ids no earlier verdict named, with no change you can name, is recorded as "
             "late: a miss of the earlier pass. " % (rel, VERDICT_FILE)) if prior else (
        "This is the first verdict on this concept: tag every gap `new_since` `first`, and leave nothing for later: a gap "
        "a later judge finds that was already there is recorded as this pass's miss. ")
    again += ("This is judge round %d. The third not_covered verdict on a concept stops judging and blocks it for the "
              "Conductor, so the list must be whole now. " % round_no)
    return (
        "You are the coverage judge for the RimMandrake concept at %(rel)s. You did not write it and you sign nothing "
        "yourself: you return a verdict and a program signs on it. Read, in this order: "
        "src/RimMandrake/rimflow/roles/designer_scene_contract.md (the proof-scene contract), "
        "src/RimMandrake/rimflow/roles/designer_lock.md (what the lock means), then %(rel)s/sheet.md, tree.json, "
        "scenes.json, floor.json, exam.json and record.json (scope, inventory, decisions). Do not read result.*.json, "
        "log.md, stage.json or any transcript: judge the artifacts, not the maker's account of them. Do not edit any "
        "file. Judge COVERAGE: every in-scope capability in record.json's inventory and every leaf in tree.json is "
        "exercised by an acceptance or interaction scene that meets the contract (asserted start, a control that rules "
        "out the plausible alternative, restoration), or is waived/out in his words; no leaf is accepted only by an "
        "exploration or mock scene; the sheet a player reads says what the tree tests. Look for gaps the artifacts do "
        "not cite, not only the ones they do. A gap that needs his answer returns to stage 2, one the Designer can fix "
        "returns to stage 3. Answer `covered` only when you found no gap.\n\n"
        "This one pass must list EVERY gap: each round of gaps costs a full rewrite, exam and judge, so a gap held back "
        "for later is the failure this checklist exists to stop. Do not stop at the first few. Before you answer, write "
        "`checklist`, one row for each of these ids and none skipped: %(ids)s. In each row's `parts`, name every separate "
        "thing that capability or leaf says it ships or tests, reading its text and impl_evidence (a bite on an animal "
        "roster, a size claim, one effect among several), each with the id of the scene that tests it ('' if none) and "
        "`ok`. A part waived or out in his words, or an offline leaf the contract exempts, is ok with the reason in "
        "`what`. Every part not ok must be in a gap, and the gap's `ids` names its rows; a gap about no single row "
        "(a showcase's claims, the sheet) has empty `ids`. %(again)s" % {"rel": rel, "again": again,
                                                                         "ids": ", ".join(ids) or "(none)"}
        + RECORD_TEXT)


def default_runner(argv, cwd, env, timeout):
    """-> (exit code, stdout). The judge is a plain `claude -p` in the concept's clone."""
    r = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout


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
        return "parked", "parked for him (%s): %s; only his word on %s lifts it" % (
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
    ex = DS.exam_errors(DS.read_json(os.path.join(d, "exam.json")), d, st, repo)
    if ex:
        return "skip", "the exam does not pass: %s" % "; ".join(ex)[:300]
    why = CT.coverage_problem(d, repo, tree)
    if not why:
        return "skip", "already signed at tree %s" % CT.tree_hash(tree)[:10]
    stop = stop_reason(st, d)
    if stop:
        return "stopped", stop
    dp = delta_plan(d, prior_verdict(d))
    if dp is not None and not dp["claims"] and not dp["changed"]:
        return "skip", "nothing claimed fixed in %s and nothing changed since %s: no judge%s" % (
            FIXES_FILE, dp["against"], "" if not dp["refused"] else " (%s)" % "; ".join(dp["refused"]))
    return "judge", why


def run(d, repo=None, runner=default_runner, timeout=TIMEOUT_S, now=None, charge=True):
    """-> (verdict record or None, message). Signs only on a well-formed `covered` verdict over unchanged inputs."""
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
        return {"stopped": why}, "stopped: %s" % why
    if what != "judge":
        return None, "%s: %s" % (what, why)
    tree = CT.load(d)
    before = (CT.tree_hash(tree), CT.sheet_hash(d))
    st0 = DS.load_state(d)
    earlier = earlier_gaps(st0, d)
    prior = prior_verdict(d)
    dp = delta_plan(d, prior)
    ids = dp["ids"] if dp is not None else required_ids(d, tree)
    hashes = entry_hashes(d)
    unit = UNIT_PREFIX + "%d" % int(now or time.time())
    env = dict(os.environ, RM_ROLE_UNIT=unit)
    tail = ["--model", MODEL, "--name", "COVERAGE JUDGE %s" % unit, "--output-format", "json",
            "--json-schema", json.dumps(SCHEMA, separators=(",", ":")), "--dangerously-skip-permissions"]
    round_no = len(rounds(st0, d)) + 1
    text = delta_prompt(d, repo, dp, round_no) if dp is not None else prompt(d, repo, ids, prior is not None, round_no)
    argv = [CLAUDE, "-p", text] + tail
    rec = {"judge": unit, "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now or time.time())),
           "tree": before[0], "sheet": before[1], "verdict": None, "signed": False, "hashes": hashes,
           "mode": "full" if dp is None else "delta", "prompt_chars": len(text)}
    if dp is not None:
        rec.update(against=dp["against"], claims=dp["claims"], changed=dp["changed"])
        if dp["refused"]:
            rec["claims_refused"] = dp["refused"]

    def ask(call, wall):
        """-> (exit code, the well-formed verdict or None, session id). Charges what the call spent."""
        try:
            code, out = runner(call, repo, env, wall)
            res = json.loads(out or "null")
        except (OSError, subprocess.SubprocessError, ValueError) as e:
            rec["error"] = "the judge did not answer: %s" % e
            return None, None, None
        if not isinstance(res, dict):
            rec["error"] = "the judge's output is not a JSON result (exit %s)" % code
            return code, None, None
        tok = None
        try:
            import role_launch as RL
            tok = RL.run_tokens(res)
        except Exception:  # noqa: BLE001 - a charge we cannot measure is recorded as unmeasured, never fatal
            tok = None
        rec["tokens"] = (rec.get("tokens") or 0) + tok if tok is not None else rec.get("tokens")
        if charge:
            try:
                DS.charge(d, tok or 0, "review" if tok is not None else "unmeasured", unit)
            except Exception as e:  # noqa: BLE001
                rec["charge_error"] = str(e)[:200]
        so = res.get("structured_output")
        ok = (isinstance(so, dict) and so.get("verdict") in ("covered", "not_covered")
              and isinstance(so.get("gaps"), list) and isinstance(so.get("checklist"), list))
        if not ok:
            rec["error"] = "no well-formed verdict (exit %s)" % code
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
    def take(so, missing):
        """Fold one well-formed answer into rec (a later answer in the same session replaces an earlier one)."""
        extra = failed_part_gaps(so["checklist"], so["gaps"])
        rec.update(verdict=so["verdict"], checklist=so["checklist"], gaps=so["gaps"] + extra,
                   reasons=str(so.get("reasons") or ""))
        for k in ("unchecked", "late", "dropped"):
            rec.pop(k, None)
        if extra and rec["verdict"] == "covered" and not so["gaps"]:
            rec["verdict"] = "not_covered"  # its own rows failed: the rows outrank the word
        if missing:
            rec["unchecked"] = missing
        if dp is not None:
            delta_merge(rec, dp)
        late = tag_gaps(rec["gaps"], earlier)
        if late:
            rec["late"] = late

    if so:
        take(so, missing)
    if CONTRACT and rec.get("verdict") == "not_covered":
        # The refusal contract (RIMMANDRAKE_EMIT_REFUSAL_RECORDS_FROM_JUDGE_BRIEFS): a refusal that names no attainable
        # path to pass is refused itself, re-asked once in the same session, and if still malformed recorded as
        # `malformed`: it never counts as a not_covered round and never sends the Designer back.
        cv, given, errs = contract_errors(d, rec, st0.get("item"))
        left = timeout - (time.monotonic() - started)
        if errs and session and left >= REASK_MIN_S:
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
        if rec.get("verdict") == "not_covered":
            rec["contract"] = {k: v for k, v in RC.submit(cv, given).items() if k != "errors"}
            if errs:
                rec.update(verdict="malformed", malformed=errs)
            suspect = [r["clause"] for r in cv["refusals"] if r.get("criterion_verdict") in ("flawed", "unattainable")]
            if suspect and not errs:
                rec["criteria_suspect"] = suspect
    tree2 = CT.load(d)
    if rec["verdict"] == "covered":
        if missing:
            rec["error"] = "a covered verdict with no row for %s is not a covered verdict: not signed" % ", ".join(missing)
        elif (CT.tree_hash(tree2), CT.sheet_hash(d)) != before:
            rec["error"] = "the tree or sheet changed while the judge read it: not signed"
        elif rec.get("gaps"):
            rec["error"] = "a covered verdict that lists gaps is not a covered verdict: not signed"
        else:
            old = os.environ.get("RM_ROLE_UNIT")
            os.environ["RM_ROLE_UNIT"] = unit
            try:
                errs = CT.sign(d, CT.SIGNER, repo)
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
    DS.write_json(os.path.join(d, VERDICT_FILE), rec)
    st = record_round(d, rec)
    msg = "signed" if rec["signed"] else "not signed: %s" % (rec.get("error") or "%d gap(s)" % len(rec.get("gaps") or []))
    parked = None
    if not rec["signed"]:
        parked = DS.loop_ceiling(st) and ("ceiling", DS.loop_ceiling(st))
        if not parked and rec.get("verdict") == "not_covered" and DS.refusals_since_loop(st) >= 2:
            away, why_away = DS.owner_away()
            if away:    # the second refusal while he is away parks (RIMMANDRAKE_PARK_UNATTENDED_DESIGNER_LOOPS)
                parked = ("second_refusal", "the coverage judge refused %d times while you are away (%s)" % (
                    DS.refusals_since_loop(st), why_away))
    if parked:
        rec["parked"] = parked[1]
        DS.write_json(os.path.join(d, VERDICT_FILE), rec)
        DS.park(d, parked[0], parked[1], repo)
        return rec, msg + "; parked: %s" % parked[1]
    stop = None if rec["signed"] else stop_reason(st, d)
    if stop:
        rec["stopped"] = stop
        DS.write_json(os.path.join(d, VERDICT_FILE), rec)
        hold(d, stop, now)
        msg += "; stopped: %s" % stop
    return rec, msg


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("dir")
    r.add_argument("--timeout", type=int, default=TIMEOUT_S)
    s = sub.add_parser("status")
    s.add_argument("dir")
    rl = sub.add_parser("release", help="one more judge look on a stopped concept")
    rl.add_argument("dir")
    rl.add_argument("--why", required=True)
    a = ap.parse_args(argv)
    d = os.path.abspath(a.dir)
    if a.cmd == "status":
        what, why = plan(d)
        print("%s: %s" % (what, why))
        return 2 if what == "error" else 0
    if a.cmd == "release":
        try:
            st = release(d, a.why)
        except (DS.Refused, OSError, ValueError) as e:
            print("coverage_judge: release refused: %s" % e)
            return 2
        print("coverage_judge: released %s for one more look (status %s)" % (os.path.basename(d), st.get("status")))
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
