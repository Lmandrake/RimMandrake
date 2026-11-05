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

Exit: 0 always for a no-op, a verdict or a refusal the Designer reads (the pre-launch step must not stop the Designer's
run: its stage-5 gate refuses without the signature anyway); 2 for an unreadable concept.
What this cannot do, said plainly: a verdict of "covered" is one model's judgment, not proof; RM_ROLE_UNIT is an
environment variable, so a writer who sets it by hand forges the ledger note too (an attributable line in git).
"""
import argparse
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import concept_tree as CT  # noqa: E402
import designer_stage as DS  # noqa: E402

VERDICT_FILE = "coverage_verdict.json"
TIMEOUT_S = 1500        # the judge's own wall bound; the Designer schedule's pre_launch_max_s holds it plus slack
MODEL = "opus"
SCHEMA = {"type": "object", "additionalProperties": False, "required": ["verdict", "gaps", "reasons"],
          "properties": {"verdict": {"enum": ["covered", "not_covered"]},
                         "gaps": {"type": "array", "items": {"type": "object", "additionalProperties": False,
                                                             "required": ["what", "where", "return_to"],
                                                             "properties": {"what": {"type": "string"},
                                                                            "where": {"type": "string"},
                                                                            "return_to": {"enum": [2, 3]}}}},
                         "reasons": {"type": "string"}}}


def prompt(d, repo):
    rel = CT.concept_rel(d, repo)
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
        "returns to stage 3. Answer `covered` only when you found no gap." % {"rel": rel})


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
    unit = "rm-coverage-judge-%d" % int(now or time.time())
    env = dict(os.environ, RM_ROLE_UNIT=unit)
    argv = ["claude", "-p", prompt(d, repo), "--model", MODEL, "--name", "COVERAGE JUDGE %s" % unit,
            "--output-format", "json", "--json-schema", json.dumps(SCHEMA, separators=(",", ":")),
            "--dangerously-skip-permissions"]
    rec = {"judge": unit, "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now or time.time())),
           "tree": before[0], "sheet": before[1], "verdict": None, "signed": False}
    try:
        code, out = runner(argv, repo, env, timeout)
        res = json.loads(out or "null")
    except (OSError, subprocess.SubprocessError, ValueError) as e:
        code, res, rec["error"] = None, None, "the judge did not answer: %s" % e
    if isinstance(res, dict):
        tok = None
        try:
            import role_launch as RL
            tok = RL.run_tokens(res)
        except Exception:  # noqa: BLE001 - a charge we cannot measure is recorded as unmeasured, never fatal
            tok = None
        rec["tokens"] = tok
        if charge:
            try:
                DS.charge(d, tok or 0, "review" if tok is not None else "unmeasured", unit)
            except Exception as e:  # noqa: BLE001
                rec["charge_error"] = str(e)[:200]
        so = res.get("structured_output")
        if isinstance(so, dict) and so.get("verdict") in ("covered", "not_covered") and isinstance(so.get("gaps"), list):
            rec.update(verdict=so["verdict"], gaps=so["gaps"], reasons=str(so.get("reasons") or ""))
        else:
            rec.setdefault("error", "no well-formed verdict (exit %s)" % code)
    elif "error" not in rec:
        rec["error"] = "the judge's output is not a JSON result (exit %s)" % code
    tree2 = CT.load(d)
    if rec["verdict"] == "covered":
        if (CT.tree_hash(tree2), CT.sheet_hash(d)) != before:
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
