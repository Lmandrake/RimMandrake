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

Exit: 0 always for a no-op, a verdict or a refusal the Designer reads (the pre-launch step must not stop the Designer's
run: its stage-5 gate refuses without the signature anyway); 2 for an unreadable concept.
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

CLAUDE = shutil.which("claude") or os.path.expanduser("~/.local/bin/claude")  # systemd's PATH lacks ~/.local/bin (OPS_TIMER_REPAIR_PRXC)

VERDICT_FILE = "coverage_verdict.json"
TIMEOUT_S = 1500        # the judge's own wall bound; the Designer schedule's pre_launch_max_s holds it plus slack
MODEL = "opus"
REASK_MIN_S = 120       # less judge time than this left: no re-ask, the missing rows go on file as unchecked
SCHEMA = {"type": "object", "additionalProperties": False, "required": ["verdict", "checklist", "gaps", "reasons"],
          "properties": {"verdict": {"enum": ["covered", "not_covered"]},
                         "checklist": {"type": "array", "items": {
                             "type": "object", "additionalProperties": False, "required": ["id", "parts"],
                             "properties": {"id": {"type": "string"},
                                            "parts": {"type": "array", "items": {
                                                "type": "object", "additionalProperties": False,
                                                "required": ["what", "scene", "ok"],
                                                "properties": {"what": {"type": "string"},
                                                               "scene": {"type": "string"},
                                                               "ok": {"type": "boolean"}}}}}}},
                         "gaps": {"type": "array", "items": {"type": "object", "additionalProperties": False,
                                                             "required": ["what", "where", "return_to", "ids"],
                                                             "properties": {"what": {"type": "string"},
                                                                            "where": {"type": "string"},
                                                                            "return_to": {"enum": [2, 3]},
                                                                            "ids": {"type": "array",
                                                                                    "items": {"type": "string"}}}}},
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


def prompt(d, repo, ids=(), prior=False):
    rel = CT.concept_rel(d, repo)
    again = ("A previous judge's verdict is in %s/%s. Check each of its gaps first. A part it passed whose scene has not "
             "changed since stays passed unless you can quote the defect in the scene or the code. " % (rel, VERDICT_FILE)
             ) if prior else ""
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
                                                                         "ids": ", ".join(ids) or "(none)"})


def default_runner(argv, cwd, env, timeout):
    """-> (exit code, stdout). The judge is a plain `claude -p` in the concept's clone."""
    r = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout


def plan(d, repo=None):
    """-> (what, why): what `run` would do now. what is "judge", "skip" or "error"."""
    repo = repo or DS.clone_of(d) or DS.REPO
    try:
        st = DS.load_state(d)
    except (DS.Refused, OSError, ValueError) as e:
        return "error", "unreadable concept: %s" % e
    if st.get("status") == "locked":
        return "skip", "locked"
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
    return "judge", why


def run(d, repo=None, runner=default_runner, timeout=TIMEOUT_S, now=None, charge=True):
    """-> (verdict record or None, message). Signs only on a well-formed `covered` verdict over unchanged inputs."""
    repo = repo or DS.clone_of(d) or DS.REPO
    what, why = plan(d, repo)
    if what != "judge":
        return None, "%s: %s" % (what, why)
    tree = CT.load(d)
    before = (CT.tree_hash(tree), CT.sheet_hash(d))
    ids = required_ids(d, tree)
    unit = "rm-coverage-judge-%d" % int(now or time.time())
    env = dict(os.environ, RM_ROLE_UNIT=unit)
    tail = ["--model", MODEL, "--name", "COVERAGE JUDGE %s" % unit, "--output-format", "json",
            "--json-schema", json.dumps(SCHEMA, separators=(",", ":")), "--dangerously-skip-permissions"]
    argv = [CLAUDE, "-p", prompt(d, repo, ids, prior_verdict(d) is not None)] + tail
    rec = {"judge": unit, "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now or time.time())),
           "tree": before[0], "sheet": before[1], "verdict": None, "signed": False}

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
    if so:
        extra = failed_part_gaps(so["checklist"], so["gaps"])
        rec.update(verdict=so["verdict"], checklist=so["checklist"], gaps=so["gaps"] + extra,
                   reasons=str(so.get("reasons") or ""))
        if extra and rec["verdict"] == "covered" and not so["gaps"]:
            rec["verdict"] = "not_covered"  # its own rows failed: the rows outrank the word
        if missing:
            rec["unchecked"] = missing
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
    DS.write_json(os.path.join(d, VERDICT_FILE), rec)
    return rec, ("signed" if rec["signed"] else "not signed: %s" % (rec.get("error") or
                                                                    "%d gap(s)" % len(rec.get("gaps") or [])))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("dir")
    r.add_argument("--timeout", type=int, default=TIMEOUT_S)
    s = sub.add_parser("status")
    s.add_argument("dir")
    a = ap.parse_args(argv)
    d = os.path.abspath(a.dir)
    if a.cmd == "status":
        what, why = plan(d)
        print("%s: %s" % (what, why))
        return 2 if what == "error" else 0
    what, why = plan(d)
    if what == "error":
        print("coverage_judge: %s" % why)
        return 2
    _rec, msg = run(d, timeout=a.timeout)
    print("coverage_judge: %s" % msg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
