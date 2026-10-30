#!/usr/bin/env python3
r"""arena_judge_calib.py — the arena JUDGE's false-reject and miss rates on the frozen planted-defect set.

Item ARENA_JUDGE_RATES_MEASURE_PLANTED (parent ARENA_CRITIC_MEASURE_PLANTED_DEFECTS_FIRST, whose criteria ask for the
judge's rates as well as the critic's).

    python3 src/RimMandrake/Utils/arena/arena_judge_calib.py run --run ID [--concurrency N] [--budget S] [--max N]
    python3 src/RimMandrake/Utils/arena/arena_judge_calib.py match --run ID [--budget S]
    python3 src/RimMandrake/Utils/arena/arena_judge_calib.py score --run ID [--baseline-run mut2-l4]

THE SET is the critic's (arena_critic_mutants: fixtures/critic_mutant_set.json, sha b54d2e85..., 56 candidates: 8
tier-A originals = labelled GOOD, 16 tier-B originals = UNLABELLED, 32 planted mutants = labelled DEFECT, m30 excluded
as equivalent by that scorer). Same runner (arena_critic_calib.run: fingerprinted, resumable, shuffled), same blind
reason matcher, same scorer. Only the reviewer differs.

THE REVIEWER is the judge through its real entry point, arena_judge.judge(), unchanged: neutraliser, leak scan,
sandbox, the Opus `claude -p` (no tools) and GPT gpt_consult votes on one prompt, an Opus tie-break on a split,
parse_answer and combine. The harness side (this module) gives it what a harness gives it:
  task   {"id": "CAL_<cid>", "criteria": <the item's criteria>, "area": <the candidate's changed TEXT files>}. No
         source_item, so it is not a replay: there are NO hidden checks (the calibration measures the model votes;
         a replay's hidden checks would only add rejects). The judge sees the criteria, not the item spec (the critic
         saw both): that is the judge as designed (PROMPT has only `Task criteria`).
  gate   {"verdict": "pass"}: the judge only ever runs after a passing gate. A test-detectable mutant might be stopped
         by a real gate first, so the miss rate is reported per detect class (test / read): `read` is the judge's
         operative miss rate, `test` is conditional on a gate that did not run that test.
  arm    a label drawn per candidate (seeded by cid) and written only to a PRIVATE arm map outside every judge root;
         the judge is blind to it by construction and the label means nothing here.
Each model call gets the judge's own timeout, shortened only to fit the invocation's wall budget; a call cut by the
budget marks the record budget_cut, so the runner retries it without counting a try (a cut is never a verdict).
The write-up the matcher reads is the reasons of the votes that agree with the final verdict (no judge names).

SCORING (score): the mutants scorer with this run as `critic` and a baseline run (default the L4 critic mut2-l4, same
set) for the paired comparison. Judge rates, all with exact Clopper-Pearson 95% intervals (never bootstrap):
  false reject = rejects / valid verdicts on the 8 tier-A originals
  miss         = 1 - catch on the planted mutants, verdict-only and reason-matched; by detect class
FAIL CLOSED: a run with no rows, more than C.MAX_INVALID_FRAC invalid, a mutant reject without a valid match, a
matcher decoy rate above M.MATCH_FP_MAX, or n=0 for a rate -> that rate is UNMEASURED, never a number.
SPEND: the judge's Opus runs with --output-format text (as designed), so its cost is ESTIMATED from prompt and answer
characters (chars/4 tokens); GPT tokens are codex's own `tokens used` from the call log when it prints one.

RESIDUAL (stated): the GPT judge is codex.exe, a Windows process the Linux sandbox does not confine; it could read the
repo (which holds fixtures/critic_mutants.json, the defect list) over \\wsl.localhost. The score scans GPT reasons
for set vocabulary (`leak_scan`) as a tripwire, not a proof.
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import random
import sys
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arena_critic_calib as C  # noqa: E402
import arena_critic_mutants as M  # noqa: E402
import arena_judge as J  # noqa: E402

A = C.A
MIN_START_S = 420        # a candidate starts only with this much wall budget left (opus + gpt high effort)
MIN_CALL_S = 60          # a model call is not started with less than this left
GPT_SLACK_S = 70         # GptConsult adds 60 s to its sandbox timeout; keep the whole call inside the budget
LEAK_WORDS = ("critic_mutant", "mutant_defect", "calibration", "planted", "fixtures/critic", "mutants.json")
OPUS_USD_PER_MTOK = (5.0, 25.0)   # input, output: ESTIMATE only (the judge's Opus call prints no cost)


def judge_root() -> Path:
    return A.arena_root() / "calibration" / "judge"


def private_root() -> Path:
    """The calibration's own arm map: outside every arm-readable and judge root (J.check_private_location)."""
    return Path(os.environ.get("ARENA_JUDGE_CALIB_PRIVATE") or
                Path.home() / ".local" / "state" / "rm_judge_calib_private")


_SET: dict = {}


def _by_cid() -> dict:
    if not _SET:
        doc = M.load_mutant_set()
        _SET.update({c["cid"]: c for c in doc["candidates"]})
    return _SET


class _Timed:
    """One judge model (OpusCLI or GptConsult) whose timeout is the judge's own, shortened only to the wall budget."""

    def __init__(self, kind: str, priv: Path, owner: "JudgeCritic", log: list):
        self.kind, self.priv, self.owner, self.log = kind, priv, owner, log

    def _cls(self):
        return J.GptConsult if self.kind == "gpt" else J.OpusCLI

    def preflight(self):
        self._cls()(priv=self.priv).preflight()

    def __call__(self, prompt: str, work: Path) -> str:
        cap = J.MODEL_TIMEOUT
        slack = GPT_SLACK_S if self.kind == "gpt" else 10
        t = cap
        if self.owner.deadline is not None:
            t = int(min(cap, self.owner.deadline - time.time() - slack))
        row = {"kind": self.kind, "prompt_chars": len(prompt), "timeout": t}
        self.log.append(row)
        if t < MIN_CALL_S:
            row["cut"] = True
            raise J.JudgeError("budget: no wall time left for the %s call" % self.kind)
        t0 = time.time()
        try:
            out = self._cls()(priv=self.priv, timeout=t)(prompt, work)
        except J.JudgeError:
            row["wall_s"] = round(time.time() - t0, 1)
            if t < cap and time.time() - t0 >= t - 5:
                row["cut"] = True       # killed by the budget-shortened timeout, not by the judge's own
            raise
        row["wall_s"] = round(time.time() - t0, 1)
        row["answer_chars"] = len(out)
        return out


class JudgeCritic:
    """The arena judge behind the Critic interface (arena_critic_calib), so the critic's runner and scorer apply."""
    name, needs_tree = "arena-judge", False

    def __init__(self):
        self.opus_model = J.opus_model()                      # refuses here, before any spend, when unset
        self.gpt_model = os.environ.get("CODEX_CONSULT_MODEL", "gpt-6.1-sol")
        self.model_timeout = J.MODEL_TIMEOUT
        self.judge_source = hashlib.sha256((HERE / "arena_judge.py").read_bytes()).hexdigest()
        self.consult_source = hashlib.sha256((J.UTILS / "gpt_consult.py").read_bytes()).hexdigest()
        self.arms = ",".join(J.arms())
        self.deadline: float | None = None
        self._lock = threading.Lock()

    def review(self, c: C.CriticInput) -> C.CriticVerdict:
        if self.deadline is not None and self.deadline - time.time() < MIN_START_S:
            return C.CriticVerdict("invalid", ["skipped: the invocation's wall budget is spent"], {"skipped": True})
        cand = _by_cid()[c.cid]
        text, binaries = C.text_area(A.REPO, cand)
        task = {"id": "CAL_" + c.cid, "criteria": cand["criteria"], "area": [glob.escape(p) for p in text]}
        arm = random.Random("judge-calib|" + c.cid).choice(J.arms())
        priv = private_root()
        log: list = []
        js = J.Judges(opus=_Timed("opus", priv, self, log), gpt=_Timed("gpt", priv, self, log),
                      tie=_Timed("opus", priv, self, log))
        t0 = time.time()
        rec = J.judge(task=task, hidden=None, clone=A.REPO, base=cand["base"], head=cand["head"], arm=arm,
                      gate={"verdict": "pass"}, judges=js, priv=priv)
        verdict = rec.get("verdict")
        votes = rec.get("votes") or []
        meta = {"judge_id": rec.get("judge_id"), "wall_s": round(time.time() - t0, 1), "calls": log,
                "votes": [{"judge": v.get("judge"), "verdict": v.get("verdict"), "why": v.get("why")} for v in votes],
                "binaries_not_shown": len(binaries), "opus_model": self.opus_model}
        if rec.get("why"):
            meta["why"] = rec["why"]
        if any(r.get("cut") for r in log):
            meta["budget_cut"] = True
        if verdict not in J.VERDICTS:
            return C.CriticVerdict("invalid", [str(rec.get("why") or "judge verdict %r" % verdict)[:300]], meta)
        # the write-up: reasons of the votes that agree with the final verdict, in vote order, no judge names
        reasons = [str(r) for v in votes if v.get("verdict") == verdict for r in (v.get("reasons") or [])]
        if not votes:                                          # decided before any model (gate/diff)
            reasons = [str(rec.get("why") or "")]
        meta["gpt_reasons"] = [str(r) for v in votes if v.get("judge") == "gpt" for r in (v.get("reasons") or [])]
        return C.CriticVerdict(verdict, reasons, meta)


# ---------------------------------------------------------------- scoring (fail closed, exact intervals)

def rate(k: int, n: int, *, unmeasured: str | None = None) -> dict:
    if unmeasured or not n:
        return {"status": "UNMEASURED", "why": unmeasured or "n = 0", "k": k, "n": n}
    lo, hi = M.cp(k, n)
    return {"status": "MEASURED", "k": k, "n": n, "rate": round(k / n, 3), "cp95": [round(lo, 3), round(hi, 3)],
            "beta_posterior_mean": round((k + 1) / (n + 2), 3)}


def judge_rates(sc: dict, role: str = "critic", missing: list | None = None) -> dict:
    """FR and miss for one reviewer block of an M.score() result. A whole-run or whole-set defect makes every rate
    UNMEASURED: no rows, ANY labelled candidate (tier-A original or scored mutant) without a valid verdict (stricter
    than the scorer's 20 % invalid allowance: a partial run is an unscored set), more than C.MAX_INVALID_FRAC invalid
    overall, no fingerprint, or an unproved mutant. A reason-matched rate is additionally UNMEASURED while a reject
    waits for its match or the decoy rate is too high. `missing` = labelled cids without a valid verdict (score_run
    computes it; None means not computed, which is itself UNMEASURED)."""
    blk = sc["reviewers"][role]
    run_bad = None
    if not blk["candidates"]:
        run_bad = "no rows"
    elif missing is None:
        run_bad = "labelled coverage not computed"
    elif missing:
        run_bad = "%d labelled candidates without a valid verdict" % len(missing)
    elif sc.get("detect", {}).get("unproved"):
        run_bad = "%d mutants unproved on these heads" % sc["detect"]["unproved"]
    elif blk["invalid"] > C.MAX_INVALID_FRAC * blk["candidates"]:
        run_bad = "%d/%d invalid" % (blk["invalid"], blk["candidates"])
    elif not blk.get("critic_fingerprint"):
        run_bad = "run records no fingerprint"
    k, n = blk["matcher_decoy_hits"]
    reason_bad = run_bad or (("matcher decoy hits %d/%d" % (k, n)) if n and k / n > M.MATCH_FP_MAX else None) or (
        ("%d mutant rejects without a valid match" % blk["rejects_without_valid_match"])
        if blk["rejects_without_valid_match"] else None)
    out = {"run": blk["run"], "invalid": [blk["invalid"], blk["candidates"]]}
    fr_k, fr_n = blk["verdict"]["false_reject"]
    out["false_reject_tierA"] = rate(fr_k, fr_n, unmeasured=run_bad)
    ub_k, ub_n = blk["verdict"]["unlabelled_reject"]
    out["unlabelled_reject_tierB_descriptive"] = rate(ub_k, ub_n, unmeasured=run_bad)
    for mode, bad in (("verdict", run_bad), ("reason", reason_bad)):
        ck, cn = blk[mode]["catch"]
        out["miss_" + mode] = rate(cn - ck, cn, unmeasured=bad)
    for det, d in blk["by_detect"].items():
        for mode, bad in (("verdict", run_bad), ("reason", reason_bad)):
            ck, cn = d[mode + "_catch"]
            out["miss_%s_detect_%s" % (mode, det)] = rate(cn - ck, cn, unmeasured=bad)
    return out


def leak_scan(recs: dict) -> list:
    """GPT reasons that use calibration vocabulary: a tripwire for the unconfined codex.exe reading the repo."""
    hits = []
    for cid, r in recs.items():
        for s in (r.get("meta") or {}).get("gpt_reasons") or []:
            low = s.lower()
            for w in LEAK_WORDS:
                if w in low:
                    hits.append({"cid": cid, "word": w, "text": s[:200]})
    return hits


def spend(recs_all: list, match_recs: list, gpt_log: Path) -> dict:
    calls = [c for r in recs_all for c in ((r.get("meta") or {}).get("calls") or [])]
    op = [c for c in calls if c["kind"] == "opus" and "answer_chars" in c]
    began = [c for c in calls if "wall_s" in c]                  # a call refused for budget never started
    started = [c for c in began if c["kind"] == "opus"]
    tin = sum(c["prompt_chars"] for c in started) / 4           # a failed call's input is billed too (its output
    tout = sum(c["answer_chars"] for c in op) / 4               # is unknown: a lower bound for those calls)
    est = tin / 1e6 * OPUS_USD_PER_MTOK[0] + tout / 1e6 * OPUS_USD_PER_MTOK[1]
    gpt_tok, gpt_n, gpt_tn = 0, 0, 0
    for g in C.read_results(gpt_log):
        gpt_n += 1
        if g.get("tokens_used") is not None:
            gpt_tn += 1
            gpt_tok += int(g["tokens_used"])
    mc = sum(float((m.get("meta") or {}).get("cost_usd") or 0) for m in match_recs)
    return {"judge_records": len(recs_all), "model_calls": len(began),
            "opus_calls_answered": len(op), "opus_cut_or_failed": sum(1 for c in started if "answer_chars" not in c),
            "gpt_calls": sum(1 for c in began if c["kind"] == "gpt"),
            "calls_refused_for_budget": len(calls) - len(began),
            "opus_tokens_est": {"in": int(tin), "out": int(tout)}, "opus_usd_est": round(est, 2),
            "opus_usd_basis": "chars/4 tokens at $%s/$%s per Mtok (ESTIMATE; the judge prints no cost); input of "
                              "every started call, output of answered calls only (failed calls' output unknown)"
                              % OPUS_USD_PER_MTOK,
            "gpt_calls_without_token_report": max(0, sum(1 for c in began if c["kind"] == "gpt") - gpt_tn),
            "gpt_log_records": gpt_n, "gpt_tokens_used_reported": gpt_tok,
            "matcher_usd_reported": round(mc, 2)}


def match_run(doc: dict, run_id: str, budget_s: float, concurrency: int = 8, call=None) -> dict:
    """M.match for a run under the judge root, appending to <run>/match.jsonl (never the critic's match file).
    Same jobs (M.match_jobs), same blind matcher with decoys (M.match_one), same keys, so M.score reads them."""
    import concurrent.futures as cf
    call = call or M.opus_call
    out = judge_root() / run_id / "match.jsonl"

    def todo():
        have = {r["key"] for r in C.read_results(out) if r.get("valid")}
        return [j for j in M.match_jobs(doc, {run_id: M.run_records(run_id, doc, judge_root())})
                if j["key"] not in have]
    t_end = time.time() + budget_s
    with cf.ThreadPoolExecutor(max_workers=concurrency) as ex:
        futs = [ex.submit(lambda j: None if time.time() > t_end - M.MATCH_TIMEOUT - 20 else M.match_one(j, call), j)
                for j in todo()]
        for f in cf.as_completed(futs):
            rec = f.result()
            if rec is not None:
                with open(out, "a") as fh:
                    fh.write(json.dumps(rec, sort_keys=True) + "\n")
    return {"jobs_left": len(todo()), "file": str(out)}


def score_run(run_id: str, baseline: str) -> dict:
    doc = M.load_mutant_set()
    root = judge_root()
    meta = json.loads((root / run_id / "run.json").read_text())
    bmeta = json.loads((C.calib_root() / baseline / "run.json").read_text())
    jrecs = M.run_records(run_id, doc, root)
    runs = {"critic": (run_id, jrecs, meta.get("critic_fingerprint")),
            "baseline": (baseline, M.run_records(baseline, doc), bmeta.get("critic_fingerprint"))}
    matches = C.read_results(M.evidence_root() / "match.jsonl") + C.read_results(root / run_id / "match.jsonl")
    pr = M.latest(C.read_results(M.evidence_root() / "proofs.jsonl"), doc)
    sc = M.score(doc, runs, matches, {r["mid"]: r for r in pr.values()})
    allrecs = C.read_results(root / run_id / "results.jsonl")
    eq = {c["cid"] for c in doc["candidates"] if c.get("mid") in M.EQUIVALENT}
    labelled = [c["cid"] for c in doc["candidates"] if c["cid"] not in eq and
                (c.get("role") == "mutant" or (c["cid"] in M.pairs(doc) and c.get("tier") == "A"))]

    def missing(recs):
        return [cid for cid in labelled if (recs.get(cid) or {}).get("verdict") not in J.VERDICTS]
    sc["judge"] = judge_rates(sc, "critic", missing(jrecs))
    sc["baseline_rates"] = judge_rates(sc, "baseline", missing(runs["baseline"][1]))
    sc["labelled_candidates"] = len(labelled)
    sc["judge_leak_scan"] = leak_scan(jrecs)
    sc["judge_spend"] = spend(allrecs, C.read_results(root / run_id / "match.jsonl"), root / run_id / "gpt_calls.jsonl")
    sc["roles"] = {"critic": "arena judge (this run)", "baseline": baseline}
    return sc


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sp = ap.add_subparsers(dest="cmd", required=True)
    r = sp.add_parser("run")
    r.add_argument("--run", required=True)
    r.add_argument("--concurrency", type=int, default=8)
    r.add_argument("--max", type=int)
    r.add_argument("--budget", type=float, default=480)
    m = sp.add_parser("match")
    m.add_argument("--run", required=True)
    m.add_argument("--budget", type=float, default=420)
    m.add_argument("--concurrency", type=int, default=8)
    s = sp.add_parser("score")
    s.add_argument("--run", required=True)
    s.add_argument("--baseline-run", default="mut2-l4")
    a = ap.parse_args(argv)
    doc = M.load_mutant_set()
    root = judge_root()
    if a.cmd == "run":
        (root / a.run).mkdir(parents=True, exist_ok=True)
        os.environ["RM_GPT_CALL_LOG"] = str(root / a.run / "gpt_calls.jsonl")   # GptConsult appends each call here
        critic = JudgeCritic()
        print(json.dumps(C.run(doc, critic, a.run, a.concurrency, a.max, root=root, budget_s=a.budget)))
        return 0
    if a.cmd == "match":
        print(json.dumps(match_run(doc, a.run, a.budget, a.concurrency)))
        return 0
    sc = score_run(a.run, a.baseline_run)
    out = root / a.run / "score.json"
    out.write_text(json.dumps(sc, indent=1) + "\n")
    print(json.dumps({"judge": sc["judge"], "verdict": sc["verdict"], "paired": sc.get("paired"),
                      "leaks": len(sc["judge_leak_scan"]), "spend": sc["judge_spend"]}, indent=1))
    print("score:", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
