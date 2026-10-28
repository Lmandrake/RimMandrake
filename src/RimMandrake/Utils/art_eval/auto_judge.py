#!/usr/bin/env python3
"""Judge finished art-eval renders without an agent remembering to (ARTEVAL_FINISHED_RENDERS_WIRE_AUTO_JUDGE).

Before this, nothing chained a finished regen render to its judge: Surrik s2r1 waited 4 days and the facing-audit r3
renders 2 days, because each session that filed the renders ended before they landed. A timer
(src/RimMandrake/Utils/systemd/rm-arteval-autojudge.timer) runs `auto_judge.py run` every 30 min:

    auto_judge.py scan                 what is owed + the slot gate, no model call
    auto_judge.py run [--max-subjects 4] [--dry-run]
    auto_judge.py status               the last pass (status.json in the scratch dir)

Two sources of owed renders, each judged the way the rimworld-art-evaluation skill says:
  fauna   done artpipe jobs arteval_<DEF>_<s?r?>_<face> filed by the art-eval pipeline -> `fauna_drive.py candidates
          --auto` (round = the def's REGEN count, owner series stops refused, a candidate already judged skipped) ->
          `runner.py run --run-id fauna_auto_<stamp> --record --file-regens` (the next round files itself; round 3 caps)
  facing  the facing-audit batch driver's state.json (per-view subjects RM_Foo_n / RM_Foo__dessicated_n are its own
          keys, never a scan of names): a row whose jobs are all done and which no production decision judged under
          its artpipe job id -> `drv.py spec <group> <subject>` -> `runner.py run --run-id audit_auto_<stamp> --record`.
          drv.py regen / install stay owed follow-ups (listed in status.json), never done here.

Judging calls Claude, so a pass does nothing unless the slot allocator allows it (the same allowed_n as the Agent
spawn hook .claude/hooks/block_agent_over_slots.py): never in DARK, never while BENCH already runs N helpers. A tiny
quota probe runs before any judge call (subagent_budget.md); a failed probe or a HOLD_ERROR record (429, timeout)
backs the pass off for an hour and is never counted as a verdict (fauna_drive.judged_set). At most --max-subjects
subjects per pass. The pass commits only its own paths (its run dirs, the delegated verdicts it wrote,
regen_rounds.json) and never pushes.
"""
from __future__ import annotations

import argparse
import fcntl
import importlib.util
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
UTILS = HERE.parent
sys.path.insert(0, str(HERE))
import round_series as RS  # noqa: E402

STATE = ROOT / "infrastructure/state/art_eval"
DATA = Path(os.environ.get("RM_DATA_ROOT") or "/mnt/d/ClaudeWork/rimmandrake")
ART = Path(os.environ.get("ARTPIPE_STATE_DIR") or DATA / "artpipe")
SCRATCH = DATA / "arteval_autojudge"
STATUS = SCRATCH / "status.json"
DRV = Path(os.environ.get("ARTEVAL_FACING_DRV") or DATA / "facing_backlog_20261026/batch/drv.py")
SEAT = "BENCH"
FAUNA_ITEM = "ART_EVAL_PIPELINE_BUILD_OPUS_GRADES_FIRST"
FAUNA_JOB = re.compile(r"^arteval_(.+?)_((?:s\d+)?r\d+)_(south|east|north)\.json$")
BACKOFF_S = 3600
RUN_TIMEOUT = 900          # one runner call: CHUNK subjects, Opus ~40-70 s + GPT ~25-45 s each
CHUNK = 2


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


# ---------------------------------------------------------------- owed renders (pure parts)

def fauna_defs(done_dir: Path) -> list:
    """Defs with a finished pipeline regen job (arteval_<DEF>_<tag>_<face>, filed by the art-eval pipeline). Facing-
    audit rows share the id shape (arteval_RM_Shoal_r3_east), so the job's rimflow_item_id decides, not the name."""
    out = set()
    for p in done_dir.glob("arteval_*.json"):
        m = FAUNA_JOB.match(p.name)
        if not m or p.name.endswith(".manifest.json"):
            continue
        try:
            if json.loads(p.read_text()).get("rimflow_item_id") != FAUNA_ITEM:
                continue
        except (OSError, ValueError):
            continue
        out.add(m.group(1))
    return sorted(out)


def judged_jobs(recs) -> set:
    """artpipe job ids that have a verdict in a production run. HOLD_ERROR (429, timeout) is no verdict."""
    return {r.get("artpipe_job") for _, r in recs if r.get("artpipe_job") and r.get("decision") != "HOLD_ERROR"}


def unjudged_specs(spec_paths, judged: set) -> list:
    """Drop candidate specs whose artpipe job some production run already judged. fauna_drive's judged set is per
    (subject, candidate) over fauna runs only; the 10-26 facing audit judged arteval_RM_Fuzzrunner_s2r1 (ACCEPT,
    candidate r1, run audit_20261026_b1r1), which fauna_drive alone would propose again."""
    out = []
    for p in spec_paths:
        try:
            job = json.loads(Path(p).read_text()).get("artpipe_job")
        except (OSError, ValueError):
            continue
        if job not in judged:
            out.append(p)
    return out


def chunks(xs, n=CHUNK):
    return [xs[i:i + n] for i in range(0, len(xs), n)]


def facing_owed(state: dict, judged: set, job_ok, stopped) -> list:
    """(subject, group) for facing-audit rows whose renders are all done and not judged under that job id.
    job_ok(row) -> bool (every facing job done ok); stopped(def) -> truthy when the owner ended its series."""
    out = []
    for k, v in state.items():
        r = v.get("row") or {}
        if v.get("done") or not r.get("id") or r["id"] in judged:
            continue
        if stopped(k) or stopped(r.get("target_def") or k):
            continue
        if job_ok(r):
            out.append((k, v.get("group")))
    return out


def hold_errors(recs) -> list:
    return [r["subject"] for r in recs if r.get("decision") == "HOLD_ERROR"]


def own_paths(run_ids, recs, day: str) -> list:
    """The repo paths a pass wrote: its run dirs, a delegated verdict per record (runner.write_delegated), rounds."""
    import runner as RN
    p = [f"infrastructure/state/art_eval/runs/{r}" for r in run_ids]
    p += sorted({f"infrastructure/state/delegated/{day}/{RN.spec_key(r)}.json" for r in recs})
    return p + ["infrastructure/state/art_eval/regen_rounds.json"]


# ---------------------------------------------------------------- gate

def gate(now: float | None = None) -> dict:
    """The Agent spawn hook's own numbers: N for BENCH, the allocator mode, running helpers."""
    now = now or time.time()
    sys.path.insert(0, str(UTILS))
    import slot_allocator as SA
    spec = importlib.util.spec_from_file_location("block_agent_over_slots", ROOT / ".claude/hooks/block_agent_over_slots.py")
    hook = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hook)
    rules = SA.load_rules(os.environ.get("RM_SLOT_RULES") or UTILS / "slot_rules.json")
    n, mode, why, src = hook.allowed_n(SA, rules, SEAT, now)
    running = len(SA.running_helpers([SA.projects_dir() / SA.SEAT_PROJECT[SEAT]], now, rules))
    return {"n": n, "mode": mode, "running": running, "source": src, "why": why}


def gate_ok(g: dict) -> tuple:
    if g.get("mode") == "DARK":
        return False, "allocator DARK: no Claude use"
    if int(g.get("n") or 0) <= 0:
        return False, f"allocator N={g.get('n')}"
    if int(g.get("running") or 0) >= int(g["n"]):
        return False, f"{SEAT} already runs {g['running']} helper(s), N={g['n']}"
    return True, f"mode {g.get('mode')}, N={g['n']}, running {g.get('running')}"


def probe() -> tuple:
    """One tiny call on the judge's own model before any judge call (subagent_budget.md: probe quota first)."""
    import runner as RN
    try:
        r = subprocess.run(["claude", "-p", "--output-format", "json", "--model", RN.model_for("opus")],
                           input="Reply with the single word OK.", capture_output=True, text=True, timeout=120,
                           cwd=str(SCRATCH))
    except (subprocess.TimeoutExpired, OSError) as e:
        return False, f"probe failed: {type(e).__name__}"
    try:
        env = json.loads(r.stdout)
    except ValueError:
        env = {}
    if r.returncode != 0 or env.get("is_error") or "OK" not in str(env.get("result", "")):
        return False, f"probe rc {r.returncode}: {(str(env.get('result') or '') + r.stderr)[-200:]}"
    return True, "probe ok"


# ---------------------------------------------------------------- the pass

def load_drv():
    if not DRV.is_file():
        return None
    sys.path.insert(0, str(DRV.parent))
    spec = importlib.util.spec_from_file_location("facing_drv", DRV)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def scan() -> dict:
    import fauna_drive as FD
    recs = list(RS.production_decisions(STATE / "runs"))
    out = {"fauna_defs": [d for d in fauna_defs(ART / "done") if not RS.stopped(d)], "facing": []}
    drv = load_drv()
    if drv is not None:
        st = json.loads((DRV.parent / "state.json").read_text())
        out["facing"] = facing_owed(st, judged_jobs(recs), lambda r: all(drv.job_state(j) == "ok" for j in drv.jobs(r)),
                                    RS.stopped)
    out["fauna_judged"] = len(FD.judged_set(FD.production()))
    return out


def sh(cmd, cwd, log: Path, timeout=RUN_TIMEOUT) -> int:
    with log.open("a") as fh:
        fh.write(f"\n$ {' '.join(map(str, cmd))}  ({now_iso()})\n")
        fh.flush()
        try:
            return subprocess.run(list(map(str, cmd)), cwd=str(cwd), stdout=fh, stderr=subprocess.STDOUT,
                                  timeout=timeout).returncode
        except subprocess.TimeoutExpired:
            fh.write(f"TIMEOUT after {timeout}s\n")
            return 124


def run_records(run_id: str) -> list:
    f = STATE / "runs" / run_id / "decisions.jsonl"
    return [json.loads(x) for x in f.read_text().splitlines() if x.strip()] if f.is_file() else []


def commit(paths: list, msg: str, log: Path) -> str:
    """Commit only this pass's paths (pathspec on the commit: a peer's staged file can never ride along). No push."""
    paths = [p for p in paths if (ROOT / p).exists()]
    if not paths:
        return "nothing to commit"
    for _ in range(5):
        a = sh(["git", "add", "--", *paths], ROOT, log, timeout=120)
        c = sh(["git", "commit", "-q", "-m", msg, "--", *paths], ROOT, log, timeout=120) if a == 0 else a
        if c == 0:
            return subprocess.run(["git", "rev-parse", "--short=10", "HEAD"], cwd=ROOT, capture_output=True,
                                  text=True).stdout.strip()
        time.sleep(20)       # index.lock held by a peer
    return f"commit failed (git add rc {a}); paths left uncommitted: {paths}"


def write_status(st: dict):
    SCRATCH.mkdir(parents=True, exist_ok=True)
    tmp = STATUS.with_suffix(".tmp")
    tmp.write_text(json.dumps(st, indent=1))
    tmp.replace(STATUS)


def cmd_run(a) -> int:
    SCRATCH.mkdir(parents=True, exist_ok=True)
    lk = open(SCRATCH / "autojudge.lock", "w")
    try:
        fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        print("another pass holds the lock")
        return 0
    prev = json.loads(STATUS.read_text()) if STATUS.is_file() else {}
    st = {"at": now_iso(), "backoff_until": prev.get("backoff_until", 0), "follow_ups": prev.get("follow_ups", [])}
    if time.time() < float(st["backoff_until"] or 0):
        st["result"] = f"backing off until {datetime.fromtimestamp(st['backoff_until']).isoformat(timespec='minutes')}"
        write_status(st); print(st["result"])
        return 0
    owed = scan()
    st["owed"] = owed
    if not owed["fauna_defs"] and not owed["facing"]:
        st["result"] = "nothing owed"
        write_status(st); print(st["result"])
        return 0
    g = gate()
    ok, why = gate_ok(g)
    st["gate"] = dict(g, verdict=why)
    if not ok:
        st["result"] = f"gate closed: {why}"
        write_status(st); print(st["result"])
        return 0
    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    log = SCRATCH / "logs" / f"pass_{stamp}.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    # fauna: which defs have a ready, unjudged candidate (fauna_drive applies rounds, stops and judged)
    cand_dir = DATA / "art_eval/fauna_cands" / f"auto_{stamp}"
    ready = []
    if owed["fauna_defs"]:
        sh([sys.executable, HERE / "fauna_drive.py", "candidates", *owed["fauna_defs"], "--auto", "--out", cand_dir],
           HERE, log, timeout=300)
        rf = cand_dir / "ready.txt"
        ready = [x for x in rf.read_text().split() if x] if rf.is_file() else []
        ready = unjudged_specs(ready, judged_jobs(RS.production_decisions(STATE / "runs")))
    budget = a.max_subjects
    fauna_specs, facing = ready[:budget], owed["facing"][:max(0, budget - len(ready[:budget]))]
    st["picked"] = {"fauna": [Path(x).name for x in fauna_specs], "facing": [k for k, _ in facing]}
    if not fauna_specs and not facing:
        st["result"] = "renders done but no candidate ready (fauna_drive candidates: waiting/judged/stopped)"
        write_status(st); print(st["result"])
        return 0
    if a.dry_run:
        st["result"] = "dry run: would judge " + json.dumps(st["picked"])
        print(st["result"])
        return 0
    pok, pwhy = probe()
    st["probe"] = pwhy
    if not pok:
        st["backoff_until"] = time.time() + BACKOFF_S
        st["result"] = f"quota probe failed, backing off 1 h: {pwhy}"
        write_status(st); print(st["result"])
        return 0
    runs, recs = [], []
    if fauna_specs:
        rid = f"fauna_auto_{stamp}"
        for part in chunks(fauna_specs):        # one run id, resumable: a killed chunk is redone by the next pass
            sh([sys.executable, HERE / "runner.py", "run", "--spec", *part, "--run-id", rid, "--record",
                "--file-regens"], HERE, log)
        runs.append(rid); recs += run_records(rid)
    if facing:
        drv = load_drv()
        for k, grp in facing:
            sh([sys.executable, DRV, "spec", grp, k], DRV.parent, log, timeout=300)
        sts = json.loads((DRV.parent / "state.json").read_text())
        specs = [sts[k]["spec"] for k, _ in facing if (sts.get(k) or {}).get("spec") and Path(sts[k]["spec"]).is_file()]
        if drv is not None and specs:
            rid = f"audit_auto_{stamp}"
            for part in chunks(specs):
                sh([sys.executable, HERE / "runner.py", "run", "--spec", *part, "--run-id", rid, "--record"], HERE, log)
            runs.append(rid); recs += run_records(rid)
            for r in run_records(rid):
                if r["decision"] in ("ACCEPT", "REGEN", "ESCALATE"):
                    verb = {"ACCEPT": "install", "REGEN": f"regen {rid}", "ESCALATE": "escalate"}[r["decision"]]
                    st["follow_ups"].append({"at": now_iso(), "subject": r["subject"], "run": rid,
                                             "owed": f"drv.py {verb} {r['subject']}" if verb != "escalate"
                                             else "escalate to the owner (round cap)"})
    st["runs"] = runs
    st["decisions"] = {f"{r['subject']}:{r.get('candidate')}": r["decision"] for r in recs}
    errs = hold_errors(recs)
    if errs:
        st["backoff_until"] = time.time() + BACKOFF_S
        st["hold_errors"] = errs
    day = datetime.now().date().isoformat()
    st["commit"] = commit(own_paths(runs, [r for r in recs if r.get("decision") != "HOLD_ERROR"], day),
                          f"art_eval auto-judge pass {stamp}: {', '.join(runs)} "
                          f"({len(recs)} decision(s)) (ARTEVAL_FINISHED_RENDERS_WIRE_AUTO_JUDGE)", log)
    st["log"] = str(log)
    st["result"] = f"judged {len(recs)}: {st['decisions']}"
    write_status(st)
    print(st["result"])
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("scan")
    r = sub.add_parser("run")
    r.add_argument("--max-subjects", type=int, default=4)
    r.add_argument("--dry-run", action="store_true")
    sub.add_parser("status")
    a = ap.parse_args(argv)
    if a.cmd == "scan":
        o = scan()
        g = gate()
        print(json.dumps(dict(o, gate=dict(g, verdict=gate_ok(g)[1])), indent=1))
        return 0
    if a.cmd == "status":
        print(STATUS.read_text() if STATUS.is_file() else "no pass yet")
        return 0
    return cmd_run(a)


if __name__ == "__main__":
    sys.exit(main())
