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


TIER = re.compile(r"^(?:RM|RSW|RUT)_")
CAND_ROUND = re.compile(r"^(?:s\d+)?r(\d+)$")
FAUNA_INSTALLS = STATE / "fauna_installs.jsonl"
ART_EVENTS = ROOT / "infrastructure/state/art/events" / f"{SEAT}.jsonl"
LEDGER = ROOT / "infrastructure/state/ledger/events" / f"{SEAT}.jsonl"
RIMFLOW = ROOT / "src/RimMandrake/rimflow/cli.py"
DEPLOY = UTILS / "deploy_custom_mods.py"
DEPLOY_TIMEOUT = 480


def slug(name: str) -> str:
    """RM_Foo__dessicated_n -> FOO_DESSICATED_N: the SUBJECT part of a rimflow id."""
    return re.sub(r"_+", "_", re.sub(r"[^A-Za-z0-9]", "_", TIER.sub("", str(name)))).strip("_").upper()


ARTPIPE_QUEUE = ART


def unfiled_rows(run_ids, state: Path | None = None, queue: Path | None = None) -> list:
    """Every REGEN row a run could not file (runner.file_regen_jobs wrote regen_filing.json), one entry per row; a
    filing that failed without saying which rows (fill_queue died or timed out, or a pre-verification record) is one
    entry with def None. A REGEN that files nothing must become an item, never just a log line."""
    out = []
    for rid in run_ids:
        d = Path(state or STATE) / "runs" / rid
        f = d / "regen_filing.json"
        if not f.is_file():
            continue
        fl = json.loads(f.read_text())
        if fl.get("ok"):
            continue
        jf = d / "regen_jobs.json"
        jobs = {j.get("id"): j for j in (json.loads(jf.read_text()) if jf.is_file() else [])}
        rows = fl.get("unfiled") or []
        if not rows and jobs:            # failed without naming rows (fill_queue died, or a pre-verification record)
            sys.path.insert(0, str(HERE))
            import runner as R
            rows = [jid for jid, j in jobs.items() if not R.in_queue(j, Path(queue or ARTPIPE_QUEUE))]
            if not rows:
                continue                 # every row reached the queue after all (filed by hand or a later pass)
        for jid in rows:
            out.append({"run": rid, "id": jid, "def": (jobs.get(jid) or {}).get("target_def"), "why": fl.get("why")})
        if not rows:
            out.append({"run": rid, "id": None, "def": None, "why": fl.get("why")})
    return out


def unfiled_item_id(u: dict) -> str:
    """One item per unfiled def (the name rules: <=44 chars, <=7 words, no trailing number); a filing whose jobs file is
    gone shares one item."""
    if not u.get("def"):
        return "ARTEVAL_REGEN_FILING_FIX_JOBS_LOST"
    word = re.sub(r"\d+$", "", slug(u["def"]).replace("_", ""))
    return "ARTEVAL_FIX_REGEN_UNFILED_" + word[:44 - 26]


def compare_done(f: Path) -> bool:
    """A head-to-head verdict exists (an errored or unreadable compare is no verdict: it is run again)."""
    try:
        d = json.loads(f.read_text())
    except (OSError, ValueError):
        return False
    return isinstance(d, dict) and not d.get("error") and "install_b" in d


def install_cmds(rec: dict, kind: str, spec=None, cmp_root: Path | None = None, drv: Path = DRV) -> list:
    """The commands that install an ACCEPTed candidate through its own installer (art ledger underneath; never a hand
    copy). fauna: the head-to-head compare fauna_drive install gates on (skipped when already paid for), then
    fauna_drive install of that round. facing: drv.py install <subject>."""
    if rec.get("decision") != "ACCEPT":
        return []
    if kind == "facing":
        return [["python3", drv, "install", rec["subject"]]]
    tag = str(rec.get("candidate") or "")
    m = CAND_ROUND.match(tag)
    if not m:
        return []
    out = []
    cmp_dir = Path(cmp_root) / f"{rec['subject']}_{tag}"
    if not compare_done(cmp_dir / "compare.json"):
        if not spec:
            return []
        out.append([sys.executable, HERE / "fauna_compare.py", rec["subject"], "--cand", spec, "--out", cmp_dir])
    out.append([sys.executable, HERE / "fauna_drive.py", "install", rec["subject"], "--round", m.group(1)])
    return out


def compare_veto(cmp) -> str | None:
    """The head-to-head compare's reason when it refuses to install the candidate (install_b false), else None. An
    errored or missing compare is no verdict (compare_done): it vetoes nothing, it is run again."""
    if not isinstance(cmp, dict) or cmp.get("error") or cmp.get("install_b") is not False:
        return None
    return str(cmp.get("reason") or "the head-to-head compare refused the candidate (no reason given)")


MAX_VETO_ROUNDS = 3        # policy.py max_regen_rounds


def veto_record(rec: dict, cmp: dict, base_prompt: str, nreg: int, max_rounds: int = MAX_VETO_ROUNDS) -> dict:
    """The decision record that replaces an ACCEPT the head-to-head compare refused (ARTEVAL_COMPARE_VETO_FIX_ACCEPT_LIMBO):
    a REGEN of the def's next round whose prompt is the candidate's own prompt plus the compare's reason, or an
    ESCALATE at the round cap. `nreg` = REGEN rounds the def's series already has."""
    reason = compare_veto(cmp) or "head-to-head compare refused the candidate"
    out = dict(rec, at=now_iso(), reasons=list(rec.get("reasons") or []) + [f"head-to-head compare refused the ACCEPT: {reason}"])
    if nreg + 1 > max_rounds:
        out.update(decision="ESCALATE", round=nreg)
        out["reasons"].append(f"still failing after {nreg} regen rounds - one line to the owner")
        out.pop("regen", None)
        return out
    prompt = (base_prompt.strip() + " " if base_prompt else "") + (
        "Correct what the previous attempt got wrong, found when it was compared with the installed art: " + reason)
    out.update(decision="REGEN", round=nreg + 1,
               regen={"findings": ["COMPARE_VETO"], "request": {"schema": "rm-art-eval/regen@v1", "subject": rec["subject"],
                                                              "prompt": prompt, "by": "compare_veto", "reference": "none"}})
    return out


def already_vetoed(run_recs: list, rec: dict) -> bool:
    """A later REGEN/ESCALATE of the same subject+candidate already replaced this ACCEPT in the run."""
    seen = False
    for r in run_recs:
        if r.get("subject") == rec.get("subject") and r.get("candidate") == rec.get("candidate"):
            if r.get("decision") == "ACCEPT" and r.get("at") == rec.get("at"):
                seen = True
            elif seen and r.get("decision") in ("REGEN", "ESCALATE"):
                return True
    return False


def veto_to_regen(rid: str, rec: dict, cmp: dict, st: dict) -> dict:
    """Turn the vetoed ACCEPT into its REGEN: append the record to the run's decisions (the next round counts it and
    fauna_drive reads it as the newest decision), file the next round with the compare's reason in the prompt, and
    make anything unfiled an item. Returns the new record."""
    import runner as R
    sub = rec["subject"]
    base = ""
    for f in sorted((STATE / "runs").glob("*/regen_jobs.json")):
        try:
            for j in json.loads(f.read_text()):
                if j.get("id", "").startswith(f"arteval_{sub}_") and j["id"].endswith(str(rec.get("candidate"))):
                    base = j.get("prompt") or base
        except (OSError, ValueError):
            pass
    nreg = RS.regen_counts(RS.production_decisions(STATE / "runs")).get(sub, 0)
    v = veto_record(rec, cmp, base, nreg)
    run_dir = STATE / "runs" / rid
    with (run_dir / "decisions.jsonl").open("a") as fh:
        fh.write(json.dumps(v) + "\n")
    if v["decision"] != "REGEN":
        st["follow_ups"].append({"at": now_iso(), "subject": sub, "run": rid,
                                 "owed": "escalate to the owner (round cap) after a compare veto"})
        return v
    jobs = R.regen_jobs([v], rid)
    jf = run_dir / f"regen_jobs_veto_{sub}_{rec.get('candidate')}.json"
    jf.write_text(json.dumps(jobs, indent=1))
    filing = R.file_regen_jobs(jf)
    (run_dir / f"regen_filing_veto_{sub}_{rec.get('candidate')}.json").write_text(json.dumps(filing, indent=1))
    if not filing.get("ok"):
        st["follow_ups"].append({"at": now_iso(), "subject": sub, "run": rid,
                                 "owed": f"compare-veto REGEN {jobs[0]['id']} not filed ({filing.get('why')}); rows in {jf}"})
    return v


def fauna_installed(lines, defname: str, tag: str) -> list:
    """Repo paths fauna_drive install wrote for <def> <tag>, from its own fauna_installs.jsonl records."""
    out = []
    for x in lines:
        if not str(x).strip():
            continue
        r = json.loads(x)
        if r.get("def") == defname and r.get("tag") == tag:
            out += [f"src/{f['mod']}/Textures/{f['rel']}" for f in r.get("files", []) if f.get("mod") and f.get("rel")]
    return list(dict.fromkeys(out))


def facing_installed(event_lines, prefix: str) -> list:
    """Repo paths the art ledger made live under a row's texPath (<prefix>_<facing>.png)."""
    pat = re.compile(re.escape(prefix) + r"_(south|east|north|west)\.png$")
    out = []
    for x in event_lines:
        if not str(x).strip():
            continue
        e = json.loads(x)
        if e.get("type") == "live" and pat.search(str(e.get("rel", ""))) and str(e.get("rel")).startswith(prefix):
            out.append(f"{e['mod']}/Textures/{e['rel']}")
    return list(dict.fromkeys(out))


def deploy_target(path: str, folded: dict) -> tuple:
    """(target key, deploy_custom_mods args) for a repo file: a folded biome deploys through the composite."""
    parts = Path(path).parts
    if len(parts) > 2 and parts[0] == "src" and parts[1] == "RimMandrake" and parts[2] in folded:
        return "compose:biomes", ["--compose", "biomes"]
    return str(Path(*parts[:3])), ["--mod", parts[2]]


def plan_resolver(target: str, folded: dict):
    """Map a plan drift path (relative to the deployed mod) back to the repo file it comes from, or None."""
    if target == "compose:biomes":
        def rs(rel: str):
            p = Path(rel).parts
            if len(p) > 2 and p[0] == "Biomes" and p[1] == "_Kits":
                p = ("Biomes",) + p[2:]
            if len(p) > 2 and p[0] == "Biomes" and p[1] in folded:
                return str(Path("src/RimMandrake", p[1], *p[2:]))
            return None
        return rs
    return lambda rel: str(Path(target, rel))


DRIFT = re.compile(r"^\s{2,}([+~\-H])\s{2}(\S.*?)(?:\s{3}\(.*)?$")


def deploy_verdict(plan_text: str, resolve, dirty) -> tuple:
    """(apply?, why, repo files) for a deploy plan. Apply only when every drift line is a + or ~ of a .png that
    resolves to a repo file git has committed (dirty(paths) -> the uncommitted ones), with no '-' (game-only file),
    no def-guard or refusal. H (held) lines are the tool's own business. An empty plan is the tool dying, not sync."""
    if not plan_text.strip():
        return False, "deploy plan printed nothing", []
    if "DEF GUARD" in plan_text or "! REFUS" in plan_text:
        return False, "the plan's own guard refuses --apply", []
    files, bad = [], []
    for ln in plan_text.splitlines():
        m = DRIFT.match(ln)
        if not m or m.group(1) == "H":
            continue
        op, rel = m.group(1), m.group(2).strip()
        if op == "-":
            bad.append(f"- {rel} (in game, not in repo)")
            continue
        src = resolve(rel)
        if not rel.lower().endswith(".png"):
            bad.append(f"{op} {rel} (not a texture)")
        elif not src:
            bad.append(f"{op} {rel} (no repo source)")
        else:
            files.append(src)
    if bad:
        return False, "held: " + "; ".join(bad[:6]), files
    if not files:
        return False, "in sync (no drift)", []
    unc = dirty(files)
    if unc:
        return False, "held: uncommitted " + ", ".join(unc[:6]), files
    return True, f"{len(files)} committed texture(s)", files


def git_dirty(paths) -> list:
    r = subprocess.run(["git", "status", "--porcelain", "--", *paths], cwd=ROOT, capture_output=True, text=True,
                       timeout=120)
    if r.returncode != 0:
        return list(paths)
    return [ln[3:].strip() for ln in r.stdout.splitlines() if ln.strip()]


def folded_sources() -> dict:
    sys.path.insert(0, str(UTILS))
    import biomes_compose
    return biomes_compose.folded_sources(ROOT / "src")


def file_item(iid: str, title: str, why: str, log: Path, caused_by: str = "ARTEVAL_FINISHED_RENDERS_WIRE_AUTO_JUDGE") -> str:
    """File a rimflow item once (an existing id is left alone: the next pass must not refile it)."""
    if sh([sys.executable, RIMFLOW, "show", iid], ROOT, log, timeout=120) == 0:
        return f"{iid} (already filed)"
    rc = sh([sys.executable, RIMFLOW, "file", iid, "--for", SEAT, "--title", title, "--kind", "bug", "--needs", "offline",
             "--target", "v1", "--caused-by", caused_by, "--why", why], ROOT, log, timeout=120)
    return iid if rc == 0 else f"{iid} (file failed rc {rc})"


def deploy(paths: list, log: Path) -> list:
    """Plan each deploy target the installed files belong to; --apply only when deploy_verdict says the plan is all
    committed textures (textures are safe to write while the game runs; DLLs are not and never pass the verdict)."""
    if not paths:
        return []
    fold = folded_sources()
    out = []
    targets = {}
    for p in paths:
        t, args = deploy_target(p, fold)
        targets.setdefault(t, args)
    for t, args in targets.items():
        plan = SCRATCH / "logs" / f"plan_{slug(t)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with plan.open("w") as fh:
            try:
                rc = subprocess.run([sys.executable, DEPLOY, *args], cwd=ROOT, stdout=fh, stderr=subprocess.STDOUT,
                                    timeout=DEPLOY_TIMEOUT).returncode
            except subprocess.TimeoutExpired:
                rc = 124
        ok, why, files = deploy_verdict(plan.read_text() if rc != 124 else "", plan_resolver(t, fold), git_dirty)
        row = {"target": t, "plan": str(plan), "verdict": why}
        if ok:
            row["apply_rc"] = sh([sys.executable, DEPLOY, *args, "--apply"], ROOT, log, timeout=DEPLOY_TIMEOUT)
        elif not why.startswith("in sync"):
            row["item"] = file_item(f"ARTEVAL_INSTALL_DEPLOY_HELD_{slug(t.split('/')[-1].replace('compose:', ''))}",
                                    f"Installed art not deployed to {t}: {why}"[:200],
                                    f"auto_judge deploy plan {plan} {why}"[:400], log)
        out.append(row)
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


def find_cand_spec(subject: str, cand: str, specs=()):
    """The candidate spec a fauna ACCEPT was judged from (fauna_compare needs it): this pass's own list first, then the
    newest auto_* candidates dir that holds it."""
    name = f"{subject}_{cand}.spec.json"
    for x in specs:
        if Path(x).name == name:
            return str(x)
    hits = sorted((DATA / "art_eval/fauna_cands").glob(f"*/{name}"), key=lambda q: q.parent.name)
    return str(hits[-1]) if hits else None


def lines_of(f: Path) -> list:
    return f.read_text().splitlines() if f.is_file() else []


def post_run(run_recs, specs, log: Path, st: dict) -> tuple:
    """After judging: every REGEN row a run could not file becomes an item; every ACCEPT is installed through its own
    installer. Returns (repo paths the installs changed - to commit, every installed path - to deploy)."""
    runs = list(dict.fromkeys(rid for rid, _ in run_recs))
    seen, items = set(), []
    for u in unfiled_rows(runs):
        iid = unfiled_item_id(u)
        if iid in seen:
            continue
        seen.add(iid)
        what = f"REGEN row {u['id']} ({u['def']})" if u["id"] else f"REGEN filing of run {u['run']}"
        items.append(file_item(iid, f"{what} was not filed to the artpipe queue: {u['why']}"[:200],
                               f"auto_judge: runs/{u['run']}/regen_filing.json says {what} is unfiled ({u['why']}); "
                               f"the next round is owed and nothing will render it", log,
                               caused_by="ARTEVAL_REGEN_ROWS_FIX_MISSING_TARGET"))
    if items:
        st["unfiled_items"] = items
    installs, every = [], []
    cmp_root = None
    for rid, r in run_recs:
        if r.get("decision") != "ACCEPT":
            continue
        kind = "facing" if rid.startswith("audit_") else "fauna"
        if kind == "fauna" and cmp_root is None:
            sys.path.insert(0, str(HERE))
            import runner as R
            cmp_root = R.storage_root() / "fauna_cands" / "cmp"
        spec = find_cand_spec(r["subject"], r.get("candidate"), specs) if kind == "fauna" else None
        cmds = install_cmds(r, kind, spec=spec, cmp_root=cmp_root)
        row = {"subject": r["subject"], "candidate": r.get("candidate"), "run": rid, "rc": []}
        if kind == "fauna" and already_vetoed(run_records(rid), r):
            continue
        if not cmds:
            row["result"] = "no installer command (no candidate spec / unparsable tag)"
        vetoed = False
        for c in cmds:
            if kind == "fauna" and Path(str(c[1])).name == "fauna_drive.py":
                cj = Path(cmp_root) / f"{r['subject']}_{r.get('candidate')}" / "compare.json"
                try:
                    reason = compare_veto(json.loads(cj.read_text()))
                except (OSError, ValueError):
                    reason = None
                if reason:        # the compare refused it: a REGEN carrying the reason, never limbo
                    v = veto_to_regen(rid, r, json.loads(cj.read_text()), st)
                    row["result"] = f"compare refused the ACCEPT -> {v['decision']} ({reason[:120]})"
                    vetoed = True
                    break
            rc = sh(c, ROOT if kind == "fauna" else DRV.parent, log, timeout=540)
            row["rc"].append(rc)
            if rc != 0:
                row["result"] = f"{Path(str(c[1])).name} rc {rc} (see log)"
                break
        if kind == "fauna":
            got = fauna_installed(lines_of(FAUNA_INSTALLS), r["subject"], r.get("candidate"))
        else:
            sts = json.loads((DRV.parent / "state.json").read_text()) if (DRV.parent / "state.json").is_file() else {}
            tp = (((sts.get(r["subject"]) or {}).get("row")) or {}).get("target_texpath")
            got = facing_installed(lines_of(ART_EVENTS), tp) if tp else []
        row["files"] = got
        row.setdefault("result", f"installed {len(got)} file(s)" if got else "installer ran, no file recorded")
        if vetoed:
            installs.append(row)
            continue
        if not got or any(row["rc"]) or not cmds:
            st["follow_ups"].append({"at": now_iso(), "subject": r["subject"], "run": rid,
                                     "owed": f"install of ACCEPT {r.get('candidate')}: {row['result']}"})
        installs.append(row)
        every += got
    st["installs"] = installs
    changed = git_dirty(every) if every else []
    return changed, every


def write_status(st: dict):
    SCRATCH.mkdir(parents=True, exist_ok=True)
    tmp = STATUS.with_suffix(".tmp")
    tmp.write_text(json.dumps(st, indent=1))
    tmp.replace(STATUS)


def cmd_run(a) -> int:
    SCRATCH.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("RIMFLOW_SEAT", SEAT)      # art.py install and rimflow file both need a seat
    os.environ.setdefault("ART_SEAT", SEAT)
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
                if r["decision"] in ("REGEN", "ESCALATE"):
                    st["follow_ups"].append({"at": now_iso(), "subject": r["subject"], "run": rid,
                                             "owed": f"drv.py regen {rid} {r['subject']}" if r["decision"] == "REGEN"
                                             else "escalate to the owner (round cap)"})
    st["runs"] = runs
    changed, installed = post_run([(rid, r) for rid in runs for r in run_records(rid)], fauna_specs, log, st)
    st["decisions"] = {f"{r['subject']}:{r.get('candidate')}": r["decision"] for r in recs}
    errs = hold_errors(recs)
    if errs:
        st["backoff_until"] = time.time() + BACKOFF_S
        st["hold_errors"] = errs
    day = datetime.now().date().isoformat()
    extra = changed + [str(x.relative_to(ROOT)) for x in (ART_EVENTS, FAUNA_INSTALLS, LEDGER)] if changed else \
        [str(LEDGER.relative_to(ROOT))] if st.get("unfiled_items") else []
    st["commit"] = commit(own_paths(runs, [r for r in recs if r.get("decision") != "HOLD_ERROR"], day) + extra,
                          f"art_eval auto-judge pass {stamp}: {', '.join(runs)} "
                          f"({len(recs)} decision(s), {len(changed)} installed file(s)) "
                          f"(ARTEVAL_FINISHED_RENDERS_WIRE_AUTO_JUDGE)", log)
    if installed:
        st["deploy"] = deploy(installed, log)
    st["log"] = str(log)
    st["result"] = f"judged {len(recs)}: {st['decisions']}"
    write_status(st)
    print(st["result"])
    return 0


def cmd_install(a) -> int:
    """Install (and deploy) the ACCEPTs of an already-judged run - the same steps a pass runs after judging, for an
    ACCEPT judged before installs were automated or whose install failed."""
    os.environ.setdefault("RIMFLOW_SEAT", SEAT)
    os.environ.setdefault("ART_SEAT", SEAT)
    log = SCRATCH / "logs" / f"install_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    recs = [r for r in run_records(a.run) if not a.subject or r["subject"] in a.subject]
    st = {"follow_ups": []}
    changed, installed = post_run([(a.run, r) for r in recs], [], log, st)
    if changed:
        st["commit"] = commit(changed + [str(x.relative_to(ROOT)) for x in (ART_EVENTS, FAUNA_INSTALLS)],
                              f"art_eval install of {a.run} ACCEPT(s) {', '.join(sorted({r['subject'] for r in recs}))}: "
                              f"{len(changed)} file(s) through the art ledger (ARTEVAL_FINISHED_RENDERS_WIRE_AUTO_JUDGE)", log)
    if installed and not a.no_deploy:
        st["deploy"] = deploy(installed, log)
    st["log"] = str(log)
    print(json.dumps(st, indent=1))
    return 0 if not st["follow_ups"] else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("scan")
    r = sub.add_parser("run")
    r.add_argument("--max-subjects", type=int, default=4)
    r.add_argument("--dry-run", action="store_true")
    sub.add_parser("status")
    i = sub.add_parser("install", help="install + deploy the ACCEPTs of a judged run")
    i.add_argument("--run", required=True)
    i.add_argument("--subject", nargs="*")
    i.add_argument("--no-deploy", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "install":
        return cmd_install(a)
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
