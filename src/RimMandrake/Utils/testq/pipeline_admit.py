"""testq/pipeline_admit.py - SteveDesktop runs pipeline tests only. The owner by card, 2026-11-14 (spec question 18c,
design/specs/2026-11-13-maturation-pipeline.md section 8): "What may be queued on SteveDesktop -> Pipeline tests only".
No load-check exception. Item RIMMANDRAKE_DESIGN_MATURATION_PIPELINE_WHOLE_MOD_IS_THE_UNIT; one more condition in the
admission checks of RIMMANDRAKE_STOP_STEVEDESKTOP_INVALID_RUNS_REPEATING_UNFIXED (repeat_guard.py), not a second design.

  refusal(mod, selector, requested_by) -> None (admitted) or a refusal record, checked by testq submit before anything
  else, and by fill, sweep and the fault-window rerun (fault_monitor.rerun_job).

A test job is admitted only when its mod version stands past the blind offline challenge in the pipeline record
(design/concepts/<Mod>/version/stage_record.json, written by rimflow/maturation.py: stage in PAST_BLIND), that version is
locked (VERSION.json state "locked") and is the one the record is for, and every chain, row and proof the job selects
is named by a stage-6 entry of that version's test_table.json in its `testq` block:

    "sc_bar": {"stage": "6", ..., "testq": {"chains": [...], "rows": [...], "proofs": [...]}}

A whole sweep (--full) or an --item selection is never one bar's check, so it is refused. Ops jobs are not tests and are
never refused: the requesters in OPS_REQUESTERS (the brake-release canary, the steward's repair wake). Reading the
record is blind-safe: an unreadable file makes that mod not qualify, and the refusal says which file.

TESTQ_PIPELINE_ADMIT=open admits everything for the older testq selftests (their mock mods have no pipeline record),
and only on a queue that is not the real one (TESTQ_QUEUE set elsewhere): it can never open the lane SteveDesktop runs.
"""
import json
import os

PAST_BLIND = ("in_game", "pre_human", "his_walk", "passed")    # maturation.STAGES after blind_challenge
BAR_STAGES = ("6",)                                            # a test-table entry the game decides (spec Stage 6)
KINDS = ("chains", "rows", "proofs")
OPS_REQUESTERS = ("Operations.canary", "BENCH.steward-wake")   # brake_release.BY; steward.py's repair wake
CLAUSE = "pipeline_tests_only"
CRITERION = ("only a locked bar's in-game check, for a mod version the pipeline record shows past the blind offline "
             "challenge, may be queued on SteveDesktop (owner by card 2026-11-14, spec question 18c)")


REAL_QUEUE = "/mnt/d/ClaudeWork/rimmandrake/testq"     # testq.QHOME's default: the lane SteveDesktop runs


def open_for_selftest(qhome=None):
    """QHOME: the queue the caller runs (testq passes its QHOME, which a selftest may set in-process)."""
    q = qhome or os.environ.get("TESTQ_QUEUE") or REAL_QUEUE
    return os.environ.get("TESTQ_PIPELINE_ADMIT") == "open" and os.path.realpath(q) != os.path.realpath(REAL_QUEUE)


def repo_root():
    return os.environ.get("TESTQ_PIPELINE_ROOT") or os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))


def _vdir(root, mod):
    return os.path.join(root, "design", "concepts", mod, "version")


def _read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f), None
    except OSError:
        return None, "no file"
    except ValueError:
        return None, "unreadable JSON"


def standing(mod, root=None):
    """-> (entry or None, why not): entry = {"version", "stage", "chains", "rows", "proofs"} when MOD qualifies."""
    root = root or repo_root()
    d = _vdir(root, mod)
    rel = "design/concepts/%s/version/" % mod
    rec, err = _read(os.path.join(d, "stage_record.json"))
    if rec is None:
        return None, "%sstage_record.json: %s (the mod has no pipeline record)" % (rel, err)
    ver, err = _read(os.path.join(d, "VERSION.json"))
    if ver is None:
        return None, "%sVERSION.json: %s" % (rel, err)
    stage, v = rec.get("stage"), ver.get("version")
    if stage not in PAST_BLIND:
        return None, "%s %s stands at %s, not past the blind offline challenge" % (mod, rec.get("version"), stage)
    if ver.get("state") != "locked":
        return None, "%s %s is not locked (VERSION.json state %s)" % (mod, v, ver.get("state"))
    if rec.get("version") != v:
        return None, "the stage record is for %s, VERSION.json names %s" % (rec.get("version"), v)
    tt, err = _read(os.path.join(d, "test_table.json"))
    if tt is None:
        return None, "%stest_table.json: %s" % (rel, err)
    if tt.get("version") not in (None, v):
        return None, "test_table.json is for %s, not %s" % (tt.get("version"), v)
    out = {"version": v, "stage": stage}
    for k in KINDS:
        out[k] = set()
    for t in (tt.get("tests") or {}).values():
        if isinstance(t, dict) and str(t.get("stage")) in BAR_STAGES:
            for k in KINDS:
                out[k] |= set((t.get("testq") or {}).get(k) or [])
    return out, None


def qualifying(root=None):
    """-> {mod: entry} for every mod version the pipeline record shows past the blind challenge (see standing)."""
    root = root or repo_root()
    base = os.path.join(root, "design", "concepts")
    try:
        mods = sorted(os.listdir(base))
    except OSError:
        return {}
    out = {}
    for m in mods:
        e, _ = standing(m, root)
        if e:
            out[m] = e
    return out


def _refuse(mod, observed, would_pass, fix, cost="edit"):
    r = {"clause": CLAUSE, "criterion": CRITERION, "mod": mod, "observed": observed, "would_pass": would_pass,
         "smallest_fix": {"what": fix, "attainable": "yes", "cost": cost}, "criterion_verdict": "sound",
         "criterion_why": "his card answer of 2026-11-14 (18c), recorded on the ledger by OWNER"}
    r["text"] = "not a pipeline test (18c, pipeline tests only): %s; it runs once %s (smallest fix: %s)" % (
        observed, would_pass, fix)
    return r


def refusal(mod, sel, by, root=None):
    """-> None when the job may be queued, else a refusal record (fields of the refusal contract, plus `text`)."""
    if by in OPS_REQUESTERS or open_for_selftest():
        return None
    sel = sel or {}
    if sel.get("full") or sel.get("item"):
        return _refuse(mod, "a %s selection is not one bar's check" % ("--full" if sel.get("full") else "--item"),
                       "the job names the chains, rows or proofs of locked bars' in-game checks",
                       "submit --chains/--rows/--proofs taken from the stage-6 entries' testq blocks in "
                       "design/concepts/%s/version/test_table.json" % mod)
    e, why = standing(mod, root)
    if e is None:
        return _refuse(mod, why, "the pipeline record shows %s past the blind offline challenge (stage in_game or "
                       "later) on a locked version" % mod,
                       "finish Stages 4 and 5, then `python3 src/RimMandrake/rimflow/maturation.py advance %s --to in_game "
                       "--by SEAT --why ...`" % mod, cost="rerun")
    extra = ["%s %s" % (k[:-1], x) for k in KINDS for x in (sel.get(k) or []) if x not in e[k]]
    if extra or not any(sel.get(k) for k in KINDS):
        return _refuse(mod, "%s %s at %s: %s" % (mod, e["version"], e["stage"], "; ".join(extra[:4]) + (
            " (and %d more)" % (len(extra) - 4) if len(extra) > 4 else "") + " named by no locked bar's in-game check"
            if extra else "the job selects nothing"),
            "every chain, row and proof it selects is in a stage-6 entry's testq block of its test_table.json",
            "drop the unnamed selection, or name it in the bar's testq block (an edit at Stage 3, so it goes through "
            "Stages 4 and 5 again)")
    return None
