#!/usr/bin/env python3
"""Judge finished art-eval renders without an agent remembering to (ARTEVAL_FINISHED_RENDERS_WIRE_AUTO_JUDGE).

Before this, nothing chained a finished regen render to its judge: Surrik s2r1 waited 4 days and the facing-audit r3
renders 2 days, because each session that filed the renders ended before they landed. A timer
(src/RimMandrake/Utils/systemd/rm-arteval-autojudge.timer) runs `auto_judge.py run` every 2 h:

    auto_judge.py scan                 what is owed + the slot gate, no model call
    auto_judge.py run [--max-subjects 4] [--dry-run]
    auto_judge.py status               the last pass (status.json in the scratch dir)
    auto_judge.py follow                       file the owed facing redraws and escalate the capped ones, no model call
    auto_judge.py due                          exit 0 nothing owed after a verdict, 1 owed, 2 could not look

Two sources of owed renders, each judged the way the rimworld-art-evaluation skill says:
  fauna   done artpipe jobs arteval_<DEF>_<s?r?>_<face> filed by the art-eval pipeline -> `fauna_drive.py candidates
          --auto` (round = the def's REGEN count, owner series stops refused, a candidate already judged skipped) ->
          `runner.py run --run-id fauna_auto_<stamp> --record --file-regens` (the next round files itself; round 3 caps)
  facing  the facing-audit batch driver's state.json (per-view subjects RM_Foo_n / RM_Foo__dessicated_n are its own
          keys, never a scan of names): a row whose jobs are all done and which no production decision judged under
          its artpipe job id -> `drv.py spec <group> <subject>` -> `runner.py run --run-id audit_auto_<stamp> --record`.
          A row judged REGEN below the round cap gets its next round (drv.py regen, then drv.py file); a row at the cap
          is noted on CAPPED_ITEM and closed in state.json. A follow-up in status.json leaves the list when its row is
          done, judged again or stopped.

Judging calls Claude, so a pass does nothing in allocator DARK, while the pipeline is paused or `./pipe off` holds
family:art_judge, or while the Dispatcher's account pick holds launches. The window's helper count N holds nothing here
(token limits are advisory, owner 2026-11-02; N=0 closed 80 of 170 passes while the account had room). A tiny
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
import shutil
import subprocess
import sys
import time
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "rimflow"))  # rimflow/effort.py, appended: shadows nothing
import effort as EF  # noqa: E402  the one effort table (RIMMANDRAKE_PASS_EFFORT_ON_EVERY_LAUNCH_STEVEDESKTOP_RAN_MEDIUM)
from datetime import datetime
from pathlib import Path

CLAUDE = shutil.which("claude") or os.path.expanduser("~/.local/bin/claude")  # systemd's PATH lacks ~/.local/bin (OPS_TIMER_REPAIR_PRXC)
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
ROUND_CAP = 3              # drv.py cmd_regen's own cap (policy.py max_regen_rounds): a 4th round is never filed
CAPPED_ITEM = "FACING_CAPPED_REDRAW_STUBBORN_NORTHS"     # the list item that holds every set the cap stopped


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
        out.add(m.group(1).removesuffix("__live"))      # a first pass's redraw: fauna_drive.job_stem
    return sorted(out)


NO_VERDICT = ("HOLD_ERROR",)
NO_VERDICT_FAUNA = ("HOLD_ERROR", "HOLD_CANVAS")     # a fauna candidate is fitted to its canvas (fauna_drive.shipping_png)


def judged_jobs(recs, no_verdict=NO_VERDICT) -> set:
    """artpipe job ids that have a verdict in a production run. HOLD_ERROR (429, timeout) is no verdict."""
    return {r.get("artpipe_job") for _, r in recs if r.get("artpipe_job") and r.get("decision") not in no_verdict}


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


def verdicts(recs) -> dict:
    """{artpipe job: (run, newest record)}. HOLD_ERROR is no verdict."""
    out = {}
    for rid, r in recs:
        j = r.get("artpipe_job")
        if j and r.get("decision") not in NO_VERDICT and (j not in out or RS._instant(r.get("at")) >= RS._instant(out[j][1].get("at"))):
            out[j] = (rid, r)
    return out


def facing_next(state: dict, judged: dict, stopped, exists, kept, queued) -> dict:
    """What each open facing row is owed after its verdict: {"regen": [(subject, group, run)], "refile": [(subject, group)],
    "capped": [(subject, run)], "unread": [subject]}. kept(row, at) -> the owner kept the installed art after that
    verdict (his newer word, so nothing is owed); None = could not look, so nothing is done and the row is named.
    refile: a later round whose jobs never reached the queue (drv.py file died after drv.py regen)."""
    out = {"regen": [], "refile": [], "capped": [], "unread": []}
    for k, v in state.items():
        r = v.get("row") or {}
        d = r.get("target_def") or k
        if v.get("done") or not r.get("id") or stopped(k) or stopped(d) or exists(d) is False:
            continue
        rid, rec = judged.get(r["id"]) or (None, {})
        if rid is None:
            if int(v.get("round") or 1) > 1 and not queued(r):
                out["refile"].append((k, v.get("group")))
            continue
        dec = rec.get("decision")
        if dec not in ("REGEN", "ESCALATE"):
            continue
        newer = kept(r, rec.get("at"))
        if newer is None:
            out["unread"].append(k)
        elif newer:
            continue
        elif dec == "ESCALATE" or int(v.get("round") or 1) >= ROUND_CAP:
            out["capped"].append((k, rid))
        else:
            out["regen"].append((k, v.get("group"), rid))
    return out


def open_follow_ups(fus, state: dict, recs, stopped) -> list:
    """The follow-ups still owed. Dropped: the row is done, its next render is filed (the row's job is not the one that run
    judged), the subject was judged again in a later run, or its series was stopped. An older entry of the same subject is dropped too."""
    newest, jobs = {}, {}
    for rid, r in recs:
        jobs[(rid, r.get("subject"))] = r.get("artpipe_job")
        if r.get("decision") not in NO_VERDICT:
            t = RS._instant(r.get("at"))
            if t >= newest.get(r.get("subject"), (0, None))[0]:
                newest[r.get("subject")] = (t, rid)
    out = {}
    for f in fus:
        k = f.get("subject")
        t, rid = newest.get(k, (0, None))
        row, was = (state.get(k) or {}).get("row") or {}, jobs.get((f.get("run"), k))
        if row.get("id") and was and row["id"] != was:
            continue
        if (state.get(k) or {}).get("done") or stopped(k) or (rid and rid != f.get("run") and t > RS._instant(f.get("at"))):
            continue
        out[k] = f
    return list(out.values())


def escalations(fus) -> list:
    """(subject, run) of the follow-ups that a compare veto left at the round cap (veto_to_regen)."""
    return [(f.get("subject"), f.get("run")) for f in fus if str(f.get("owed")).startswith("escalate")]


def kept_after(row: dict, at):
    """True | False: the owner kept a live facing of this row after AT. None: the art ledger or git could not be read."""
    try:
        sys.path.insert(0, str(UTILS / "art"))
        import artledger as AL
        pats = [f":(glob)src/**/Textures/{row['target_texpath']}_{f}.png" for f in row["facings"]]
        r = subprocess.run(["git", "ls-files", "--", *pats], cwd=ROOT, capture_output=True, text=True, timeout=300)     # hang guard
        if r.returncode != 0:
            return None
        ix = AL.cached_index()
        keeps = [k for x in r.stdout.splitlines() for k in ix.protected(AL.sha256_file(ROOT / x))]
        return bool(RS.keeps_after(keeps, at))
    except Exception:  # noqa: BLE001  could not look is its own answer: the row waits and is named
        return None


def in_queue(row: dict) -> bool:
    import runner as RN
    return RN.in_queue(row, ART)


def def_exists(d: str):
    """True | False: src holds <defName>d</defName>. None: git could not say (never read as gone)."""
    try:
        r = subprocess.run(["git", "grep", "-lF", f"<defName>{d}</defName>", "--", "src"], cwd=ROOT, capture_output=True,
                           text=True, timeout=300)       # hang guard
    except (OSError, subprocess.TimeoutExpired):
        return None
    return {0: True, 1: False}.get(r.returncode)


def split_gone(owed, state: dict, exists) -> tuple:
    """(owed rows, subjects whose def is gone). A renamed def leaves its old row behind for good: RSW_SmogMothLarvae,
    judged to round 3 as RM_IllothLarvae, was picked and failed at every pass from 11-07 on."""
    keep, gone = [], []
    for k, g in owed:
        d = ((state.get(k) or {}).get("row") or {}).get("target_def")
        if d and exists(d) is False:
            gone.append(k)
        else:
            keep.append((k, g))
    return keep, gone


def driver_env() -> dict:
    """The facing driver (D:, outside this repo) imports pnglib by name; the image skills moved on 2026-11-19."""
    sys.path.insert(0, str(UTILS))
    import image_skills
    scripts = str(image_skills.require(image_skills.GENERATING_SCRIPTS))
    # FAB_REPO: the driver reads a run's regen_jobs.json and files from the clone this pass judged in
    return dict(os.environ, FAB_REPO=str(ROOT),
                PYTHONPATH=os.pathsep.join(x for x in (scripts, os.environ.get("PYTHONPATH")) if x))


def hold_errors(recs) -> list:
    return [r["subject"] for r in recs if r.get("decision") == "HOLD_ERROR"]


def own_paths(run_ids, recs, day: str) -> list:
    """The repo paths a pass wrote: its run dirs, a delegated verdict per record (runner.write_delegated), the departures
    brief a spec build refreshed, rounds."""
    import runner as RN
    p = [f"infrastructure/state/art_eval/runs/{r}" for r in run_ids]
    p += sorted({f"infrastructure/state/delegated/{day}/{RN.spec_key(r)}.json" for r in recs})
    p += sorted({f"infrastructure/state/art_eval/briefs/{r['subject'].split('__')[0]}.json" for r in recs})
    return p + ["infrastructure/state/art_eval/regen_rounds.json"]


# ---------------------------------------------------------------- gate

def pipeline_hold(now: float):
    """Why the pipeline holds this pass, or None: its pause, `./pipe off family:art_judge`, the Dispatcher's account pick.
    A gate that cannot be read holds."""
    sys.path.insert(0, str(ROOT / "src/RimMandrake/rimflow"))
    try:
        import pipeline_pause as PP
        if PP.blocks(None, now):
            return "the pipeline is paused"
        import control as C
        b = C.blocked({"family": "art_judge", "item": "ARTEVAL_FINISHED_RENDERS_WIRE_AUTO_JUDGE"})
        if b:
            return f"pipe off: {b}"
        import maturation_dispatch as MD
        go, why = MD.account_gate()
        return None if go else why
    except Exception as e:  # noqa: BLE001
        return f"a gate could not be read ({type(e).__name__}: {e})"


def gate(now: float | None = None) -> dict:
    """The allocator's mode and N (as the Agent spawn hook reads them; N is recorded, it decides nothing) and the
    pipeline's hold."""
    now = now or time.time()
    sys.path.insert(0, str(UTILS))
    import slot_allocator as SA
    spec = importlib.util.spec_from_file_location("block_agent_over_slots", ROOT / ".claude/hooks/block_agent_over_slots.py")
    hook = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hook)
    rules = SA.load_rules(os.environ.get("RM_SLOT_RULES") or UTILS / "slot_rules.json")
    n, mode, why, src = hook.allowed_n(SA, rules, SEAT, now)
    return {"n": n, "mode": mode, "source": src, "why": why, "held": pipeline_hold(now)}


def gate_ok(g: dict) -> tuple:
    if g.get("mode") == "DARK":
        return False, "allocator DARK: no Claude use"
    if g.get("held"):
        return False, str(g["held"])
    return True, f"mode {g.get('mode')}, N={g.get('n')} (advisory)"


def probe() -> tuple:
    """One tiny call on the judge's own model before any judge call (subagent_budget.md: probe quota first)."""
    import runner as RN
    try:
        r = subprocess.run([CLAUDE, "-p", "--output-format", "json", "--model", RN.model_for("opus"),
                            "--dangerously-skip-permissions"] + EF.effort_args(RN.model_for("opus")),
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
    sys.path.insert(0, str(UTILS))
    import image_skills
    image_skills.add_to_path()
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
        owed = facing_owed(st, judged_jobs(recs), lambda r: all(drv.job_state(j) == "ok" for j in drv.jobs(r)), RS.stopped)
        out["facing"], out["gone"] = split_gone(owed, st, def_exists)
        out["next"] = facing_next(st, verdicts(recs), RS.stopped, def_exists, kept_after, in_queue)
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
    from fauna_drive import compare_dir
    out = []
    cmp_dir = compare_dir(cmp_root, rec)
    if not compare_done(cmp_dir / "compare.json"):
        spec = rec.get("facing_candidate_spec") or spec
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


_GATE_REWORD = ((re.compile(r"top[- ]down(?:\s+(?:plan|view|camera))?|overhead(?:\s+(?:plan|view|camera|shot))?", re.I), "seen from above"),
                (re.compile(r"\b(?:all|three|four)\s+facings\b", re.I), "every facing"))


def gate_safe_reason(reason: str) -> str:
    """The compare's reason in words artpipe's per-facing gate accepts. The reason is the redraw's whole point, and the
    gate refuses 'overhead' / 'top-down' (FireWasp r3: 'north is an overhead view' was dropped from the north prompt),
    so the defect is kept and said as 'seen from above' instead of being deleted."""
    for rx, sub in _GATE_REWORD:
        reason = rx.sub(sub, reason)
    return reason


def veto_record(rec: dict, cmp: dict, base_prompt: str, nreg: int, max_rounds: int = MAX_VETO_ROUNDS) -> dict:
    """The decision record that replaces an ACCEPT the head-to-head compare refused (ARTEVAL_COMPARE_VETO_FIX_ACCEPT_LIMBO):
    a REGEN of the def's next round whose prompt is the candidate's own prompt plus the compare's reason, or an
    ESCALATE at the round cap. `nreg` = REGEN rounds the def's series already has."""
    reason = compare_veto(cmp) or "head-to-head compare refused the candidate"
    out = dict(rec, at=now_iso(), reasons=list(rec.get("reasons") or []) + [f"head-to-head compare refused the ACCEPT: {reason}"])
    out.pop("master_job", None)   # a refused body is no master for wing layers (ARTEVAL_WIRE_FLYER_MASTER_NOBODY_WRITES_IT)
    if nreg + 1 > max_rounds:
        out.update(decision="ESCALATE", round=nreg)
        out["reasons"].append(f"still failing after {nreg} regen rounds - one line to the owner")
        out.pop("regen", None)
        return out
    fix = ("Correct what the previous attempt got wrong, found when it was compared with the installed art: "
           + gate_safe_reason(reason))
    prompt = (base_prompt.strip() + " " if base_prompt else "") + fix
    out.update(decision="REGEN", round=nreg + 1,
               regen={"findings": ["COMPARE_VETO"], "request": {"schema": "rm-art-eval/regen@v1", "subject": rec["subject"],
                                                              "prompt": prompt, "by": "compare_veto", "reference": "none", "keep": fix}})
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
                if j.get("id") == f"arteval_{sub}_{rec.get('candidate')}":   # exact: a '_<variant>_s1r2' id also ends with 'r2'
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
    jobs = R.regen_jobs([v], rid, masters=R.accepted_masters(STATE / "runs"))
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


PACK_FIT = ROOT / "src/RimStarWars/SWBestiary/art/pack_overlay_fit.py"


def pack_refit_cmd(tp: str) -> list:
    """A new body leaves the Pack overlay that pack_overlay_fit fitted to the old one off the body (Moravatha, then
    Fambaa at 1df326562e). Refit that one graphic; a body with no fitted Pack, or another's drawn Pack, is a no-op."""
    return [sys.executable, PACK_FIT, "--refit", "--tex", tp, "--apply"]


def pack_installed(event_lines, tp: str) -> list:
    """Repo paths the refit made live: <texPath>Pack_<facing>.png."""
    return facing_installed(event_lines, tp + "Pack")


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
             "--target", "v1", "--caused-by", caused_by, "--why", why], ROOT, log, timeout=120,
            env=dict(os.environ, RM_FILING_PROGRAM="auto_judge.file_item"))   # filing_gate.py: a program files it
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


def sh(cmd, cwd, log: Path, timeout=RUN_TIMEOUT, env=None) -> int:
    with log.open("a") as fh:
        fh.write(f"\n$ {' '.join(map(str, cmd))}  ({now_iso()})\n")
        fh.flush()
        try:
            return subprocess.run(list(map(str, cmd)), cwd=str(cwd), stdout=fh, stderr=subprocess.STDOUT,
                                  timeout=timeout, env=env).returncode
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
        dirty = subprocess.run(["git", "status", "--porcelain", "--", *paths], cwd=ROOT, capture_output=True,
                               text=True, timeout=300)      # hang guard
        if dirty.returncode == 0 and not dirty.stdout.strip():
            return "nothing to commit"
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
                from fauna_drive import compare_dir
                cj = compare_dir(cmp_root, r) / "compare.json"
                try:
                    reason = compare_veto(json.loads(cj.read_text()))
                except (OSError, ValueError):
                    reason = None
                if reason:        # the compare refused it: a REGEN carrying the reason, never limbo
                    v = veto_to_regen(rid, r, json.loads(cj.read_text()), st)
                    row["result"] = f"compare refused the ACCEPT -> {v['decision']} ({reason[:120]})"
                    vetoed = True
                    break
            rc = sh(c, ROOT if kind == "fauna" else DRV.parent, log, timeout=540, **({} if kind == "fauna" else {"env": driver_env()}))
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
            if got and not any(row["rc"]):
                row["rc"].append(sh(pack_refit_cmd(tp), ROOT, log, timeout=540))     # hang guard, far above a fit
                got += pack_installed(lines_of(ART_EVENTS), tp)
                if row["rc"][-1] != 0:
                    row["result"] = f"pack_overlay_fit.py rc {row['rc'][-1]} (see log)"
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


def drv_state() -> dict:
    f = DRV.parent / "state.json"
    return json.loads(f.read_text()) if f.is_file() else {}


def follow(nxt: dict, st: dict, log: Path) -> bool:
    """Do what facing_next says. Every act is read back: a regen counts when the driver's row moved to its next round and
    the round's jobs are in the queue; anything else becomes a list item. Returns True when the ledger was written."""
    wrote, filed = False, []

    def failed(k, owed):
        nonlocal wrote
        d = ((drv_state().get(k) or {}).get("row") or {}).get("target_def") or k
        st.setdefault("unfiled_items", []).append(
            file_item(unfiled_item_id({"def": d}), f"Facing redraw of {k} did not reach the artpipe queue: {owed}"[:200],
                      f"auto_judge follow: {owed}; log {log}"[:400], log, caused_by="ARTEVAL_REGEN_ROWS_FIX_MISSING_TARGET"))
        st["follow_ups"].append({"at": now_iso(), "subject": k, "run": None, "owed": owed})
        wrote = True

    todo = []
    for k, grp, rid in nxt.get("regen") or []:
        before = drv_state().get(k) or {}
        sh([sys.executable, DRV, "regen", rid, k], DRV.parent, log, timeout=300, env=driver_env())
        now = drv_state().get(k) or {}
        if now.get("done") or now.get("round") != (before.get("round") or 0) + 1 \
                or (now.get("row") or {}).get("id") == (before.get("row") or {}).get("id"):
            failed(k, f"drv.py regen {rid} {k} moved nothing")
            continue
        todo.append((k, grp))
    for k, grp in todo + list(nxt.get("refile") or []):
        sh([sys.executable, DRV, "file", grp, k], DRV.parent, log, timeout=600, env=driver_env())
        row = (drv_state().get(k) or {}).get("row") or {}
        if row and in_queue(row):
            filed.append(row["id"])
        else:
            failed(k, f"drv.py file {grp} {k}: no jobs in the queue")
    if filed:
        st["regens_filed"] = (st.get("regens_filed") or []) + filed
    esc = escalations(st["follow_ups"])
    capped = list(nxt.get("capped") or []) + esc
    if capped:
        text = ("at the round cap, still judged REGEN or ESCALATE: " + ", ".join(f"{k} (run {rid})" for k, rid in capped)
                + f". state.json done=ESCALATE ({DRV.parent}/state.json). Written by auto_judge.py follow.")
        rc = sh([sys.executable, RIMFLOW, "note", CAPPED_ITEM, "--text", text, "--seat", SEAT, "--why",
                 "auto_judge: round cap reached in the facing redraw batch"], ROOT, log, timeout=600)
        if rc == 0:
            wrote = True
            s = drv_state()
            st["follow_ups"] = [f for f in st["follow_ups"] if (f.get("subject"), f.get("run")) not in esc]
            for k, _ in capped[:len(capped) - len(esc)]:
                s[k].update(done="ESCALATE", escalated_to=CAPPED_ITEM)
            tmp = DRV.parent / "state.json.tmp"
            tmp.write_text(json.dumps(s, indent=1))
            tmp.replace(DRV.parent / "state.json")
            st["escalated"] = [k for k, _ in capped]
        else:
            st["follow_ups"] += [{"at": now_iso(), "subject": k, "run": rid, "owed": f"note on {CAPPED_ITEM} failed (rc {rc})"}
                                 for k, rid in capped[:len(capped) - len(esc)]]
    return wrote


def prune_follow_ups(st: dict):
    st["follow_ups"] = open_follow_ups(st["follow_ups"], drv_state(), list(RS.production_decisions(STATE / "runs")), RS.stopped)


def follow_pass(nxt: dict, st: dict, log: Path):
    log.parent.mkdir(parents=True, exist_ok=True)
    if follow(nxt, st, log):
        st["follow_commit"] = commit([str(LEDGER.relative_to(ROOT))], "art_eval follow-ups: ledger lines of capped or unfiled "
                                     "facing redraws (RIMMANDRAKE_RENDER_TWELVE_FACING_REDRAWS_JUDGED_REGEN_NOBODY_FILED)", log)
    prune_follow_ups(st)


def owed_next(nxt) -> bool:
    return any((nxt or {}).get(x) for x in ("regen", "refile", "capped"))


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
    prune_follow_ups(st)
    todo = owed_next(owed.get("next")) or bool(escalations(st["follow_ups"]))
    if not owed["fauna_defs"] and not owed["facing"] and not todo:
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
    if todo and not a.dry_run:
        follow_pass(owed.get("next") or {}, st, log)
        write_status(st)
    # fauna: which defs have a ready, unjudged candidate (fauna_drive applies rounds, stops and judged)
    cand_dir = DATA / "art_eval/fauna_cands" / f"auto_{stamp}"
    ready = []
    if owed["fauna_defs"]:
        sh([sys.executable, HERE / "fauna_drive.py", "candidates", *owed["fauna_defs"], "--auto", "--out", cand_dir],
           HERE, log, timeout=1800)     # hang guard: a def's first spec is built here (about 20 s each)
        rf = cand_dir / "ready.txt"
        ready = [x for x in rf.read_text().split() if x] if rf.is_file() else []
        ready = unjudged_specs(ready, judged_jobs(RS.production_decisions(STATE / "runs"), NO_VERDICT_FAUNA))
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
            sh([sys.executable, DRV, "spec", grp, k], DRV.parent, log, timeout=300, env=driver_env())
        sts = json.loads((DRV.parent / "state.json").read_text())
        specs = [sts[k]["spec"] for k, _ in facing if (sts.get(k) or {}).get("spec") and Path(sts[k]["spec"]).is_file()]
        st["spec_failed"] = [k for k, _ in facing if not ((sts.get(k) or {}).get("spec") and Path(sts[k]["spec"]).is_file())]
        if drv is not None and specs:
            rid = f"audit_auto_{stamp}"
            for part in chunks(specs):
                sh([sys.executable, HERE / "runner.py", "run", "--spec", *part, "--run-id", rid, "--record"], HERE, log)
            runs.append(rid); recs += run_records(rid)
            # the new verdicts' next rounds, in the same pass (only the rows this run judged)
            mine = {k for k, _ in facing}
            nxt = facing_next({k: v for k, v in drv_state().items() if k in mine},
                              verdicts(RS.production_decisions(STATE / "runs")), RS.stopped, def_exists, kept_after, in_queue)
            follow_pass(nxt, st, log)
    st["runs"] = runs
    changed, installed = post_run([(rid, r) for rid in runs for r in run_records(rid)], fauna_specs, log, st)
    st["decisions"] = {f"{r['subject']}:{r.get('candidate')}": r["decision"] for r in recs}
    errs = hold_errors(recs)
    if errs:
        st["backoff_until"] = time.time() + BACKOFF_S
        st["hold_errors"] = errs
    if runs:
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
    failed = st.get("spec_failed") or []
    if failed:
        st["result"] += f"; the driver made no spec for {', '.join(failed)} (see the log)"
    write_status(st)
    print(st["result"])
    return 1 if failed else 0       # a row that can never be judged is a failed unit, not a quiet "judged 0"


def cmd_follow(a) -> int:
    """The follow-up half of a pass, with no model call and no Claude gate: the redraws go to the Codex art queue."""
    SCRATCH.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("RIMFLOW_SEAT", SEAT)
    lk = open(SCRATCH / "autojudge.lock", "w")
    try:
        fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        print("COULD NOT LOOK: another pass holds the lock")
        return 2
    nxt = scan().get("next")
    if nxt is None:
        print(f"COULD NOT LOOK: no facing driver at {DRV}")
        return 2
    st = json.loads(STATUS.read_text()) if STATUS.is_file() else {}
    st.setdefault("follow_ups", [])
    for x in ("regens_filed", "escalated", "unfiled_items", "follow_commit"):
        st.pop(x, None)
    log = SCRATCH / "logs" / f"follow_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    follow_pass(nxt, st, log)
    write_status(st)
    print(json.dumps({x: st.get(x) for x in ("regens_filed", "escalated", "unfiled_items", "follow_commit", "follow_ups")}
                     | {"unread": nxt["unread"], "log": str(log)}, indent=1))
    return 1 if st.get("unfiled_items") or nxt["unread"] else 0


def cmd_due(a) -> int:
    nxt = scan().get("next")
    if nxt is None or not STATUS.is_file():
        print(f"COULD NOT LOOK: {DRV if nxt is None else STATUS} is not there")
        return 2
    if nxt["unread"]:
        print(f"COULD NOT LOOK: the owner's keeps of {', '.join(nxt['unread'])} could not be read")
        return 2
    fus = json.loads(STATUS.read_text()).get("follow_ups") or []
    live = open_follow_ups(fus, drv_state(), list(RS.production_decisions(STATE / "runs")), RS.stopped)
    print(f"regen owed {[x[0] for x in nxt['regen']]}; not in the queue {[x[0] for x in nxt['refile']]}; "
          f"capped and not escalated {[x[0] for x in nxt['capped']]}; escalations with no item {[k for k, _ in escalations(live)]}; discharged follow-ups still listed {len(fus) - len(live)} of {len(fus)}")
    return 1 if owed_next(nxt) or escalations(live) or len(live) != len(fus) else 0


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
    sub.add_parser("follow", help="file the owed facing redraws and escalate the capped ones; no model call")
    sub.add_parser("due", help="exit 0 nothing owed after a verdict, 1 owed, 2 could not look")
    i = sub.add_parser("install", help="install + deploy the ACCEPTs of a judged run")
    i.add_argument("--run", required=True)
    i.add_argument("--subject", nargs="*")
    i.add_argument("--no-deploy", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd in ("follow", "due"):
        return cmd_follow(a) if a.cmd == "follow" else cmd_due(a)
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
