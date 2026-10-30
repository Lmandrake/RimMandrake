#!/usr/bin/env python3
r"""testpilot.py — the `trio` TestPilot (harness step 13; build ticket ARENA_TESTPILOT_BUILD_RELOAD_SCALED_BY_COST).

Design: design/RimMandrake/testpilot_merged_2026-10-29.md §2.1 L6-L13 (machine-owned game, fresh pilot passes, script
canary, keyed evidence, L9a affected-scenario re-test, fix-now by class, what needs what), §2.2 M1 (the reload rule
scaled by measured reload cost), M5 (crashes); architecture_switch_harness_2026-10-29.md §6
step 13 and §7 (the live-resource handoff, modelled in src/RimMandrake/arena/models/LiveHandoff.tla: this is the
FIXED protocol of that model: hand off only at a test boundary, a durable queue, a rule logged before every reload,
no C# deploy while the game runs, a verdict only for the sha that is loaded, no act from a context after its switch).
The owner's return to the machine is NOT an event here (owner 2026-10-30: strip it): no presence probe, no yield.

Every live act goes through arena_lane.Lane (bridge take/release, profile, deploy, reload, canary). This module
decides WHEN, and logs WHY. A pilot agent drives it through the CLI; the decisions are code, not the agent's opinion.

THE RELOAD RULE (M1), checked in this order by decide(); the numbers live in testpilot_reload_rule.json:
  ladder   a red canary on a live process: reconnect, then reload a fixture save, then restage. Not a reload.
  R0       no game in this lane's session (cold start).
  R1       the process is dead, or the canary is still red after every ladder rung.
  R2       no valuable valid test remains on the loaded artifact and a queued candidate needs a reload. A test blocked
           only by a taint note or a hot-fix is restored by a state reset (ladder `reload_save`), not by R2.
  R3       a sealed repair that is not hot-loadable is waiting and its DRAIN is spent. The drain is set by the
           profile's MEASURED launch-to-ready time (arena_lane load_times, median of the newest N ok rows):
             cheap (<= cheap_max_launch_to_ready_s): spent after cheap_extra_tests more tests since it was sealed;
             expensive, or UNMEASURED (never the 22 s figure): spent only when nothing valuable remains (= R2);
             either: spent once max_acceptance_delay_s[class] has passed since it was sealed.
  "Valuable" = a scenario of the loaded (or hot-appliable) candidate with no pass/fail/carried evidence at its
  fingerprint and not blocked. A scenario carried by L9a is never valuable, so it never delays a reload.
  Every reload writes a decision record (rule, reason, cost used, basis, threshold, class, rule-file sha) to
  decisions.jsonl BEFORE Lane.reload runs, and the lane's `reload` event carries the decision id in its `why`.
  `Pilot.reload()` refuses a decision without a rule: no reload is ever logged without one.

HOT-LOAD CLASSES (L11, S3). A candidate's class is the highest its changed files need:
  cs      .cs/.csproj/.dll or anything under Assemblies/: close, deploy, relaunch (the DLL is locked).
  reload  XML, textures, sounds, About/, Languages/: a restart on the profile.
  live    nothing a mod loads (a fixture save, a scenario script, bridge staging): applied to the running game.
A declared class may raise this, never lower it. Only a `live` candidate whose mod set equals the loaded one (its
parent is loaded, or it deploys no mods on the same profile) is applied to the running game; every other one,
including a fix subagent's repair that is not hot-loadable, waits sealed for the next load and an R3 (L10: a MOD
repair also needs its blind diff review, `--review`, before it is even queued). A HARNESS/SITE repair applied hot gives a hot-fixed PASS, which counts only after the
scenario passes once more after a state reset.

L9a. Each scenario in a candidate's plan declares its footprint {files: [globs], defs: [defNames]}. When a candidate
is a rebuild of an earlier attempt, a scenario that passed (or was carried) at the parent's fingerprint and that the
rebuild does not touch is recorded `carried` with the source fingerprint, and is not re-run. Touched = no footprint;
a changed file matches a glob; a changed def is named; the scenario's own argv file or plan entry changed; the mods,
profile or tier changed; a harness file changed; the changed-file list is unknown; or the parent's taint note names
it (or says `uncertain`).

THE SESSION AND THE HANDOFF (L7). <arena>/trio/pilot/<lane>/session.json holds the lane's game (launch time, loaded
candidate, deployed sha and mods, profile, epoch) and which pilot drives it. A pass ends at a test boundary with
handoff(): the bridge is released WITHOUT restoring the owner's list (the swap marker keeps the restore owed) and the
session says `handoff` with a cursor into state.jsonl. A fresh pilot's wake() takes the bridge, rebuilds the Lane
from the session, and reads the queue from disk: candidates queued before or after the cursor are all there (the
queue is never in memory). A retired or superseded pilot is refused every act (StalePilot). close() is the full
release with the owner's list restored.

    python3 src/RimMandrake/Utils/arena/testpilot.py enqueue --item X --sha S --builder B --plan plan.json \
            --profile minimal [--mod M ...] [--has-dll] [--parent CAND] [--changed-file F ...] [--changed-def D ...] \
            [--kind repair --fault MOD|HARNESS|SITE --review PATH] [--fix-class live|reload|cs]
    python3 src/RimMandrake/Utils/arena/testpilot.py pass   --lane steve --pilot P --clone DIR [--close]
    python3 src/RimMandrake/Utils/arena/testpilot.py decide --lane steve        (dry run: what the rule says now)
    python3 src/RimMandrake/Utils/arena/testpilot.py taint  --cand C --scenario S --names a,b|uncertain
    python3 src/RimMandrake/Utils/arena/testpilot.py status [--lane steve]

plan.json: {"scenarios": [{"id": "s1", "argv": ["python3", "proof.py", "--case", "a"], "footprint": {"files":
["src/RimMandrake/Foo/Defs/*.xml"], "defs": ["RM_Foo"]}, "taints": ["s2"], "fail_rc": 1},
{"id": "s2", "argv": ["python3", "proof.py", "--case", "b"]}], "fixture_save": "name"}
(taints name scenarios of the same plan: check_live_plan refuses an unknown id, which would silently block nothing)
Files (under <arena> = arena_tasks.arena_root(), outside git; written only by this code):
  trio/pilot/queue.jsonl (candidates, append-only), state.jsonl (transitions), evidence.jsonl (keyed, append-only),
  decisions.jsonl (every decision that moved the game), <lane>/session.json, logs/<run>.log
"""
from __future__ import annotations

import argparse
import contextlib
import fcntl
import fnmatch
import hashlib
import json
import os
import statistics
import signal
import subprocess
import sys
import time
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arena_lane as L  # noqa: E402
import ralph_c_runner as RC  # noqa: E402  (RunnerDriver: checkout in the pilot's own clone)

ARM = "trio"
RULE_FILE = HERE / "testpilot_reload_rule.json"
HARNESS_FILES = ("src/RimMandrake/Utils/arena/testpilot.py", "src/RimMandrake/Utils/arena/testpilot_reload_rule.json",
                 "src/RimMandrake/Utils/arena/arena_lane.py", "src/RimMandrake/Utils/arena/arena_lane_probe.py")
CLASSES = ("live", "reload", "cs")
FAULTS = ("MOD", "HARNESS", "SITE")
TERMINAL = ("resolved", "parked", "quarantined", "superseded")
COUNTED = ("pass", "fail", "carried")


class PilotRefused(Exception):
    """A refusal. Nothing was touched."""


class StalePilot(PilotRefused):
    """This pilot no longer drives the lane (it handed off, aborted, or another pilot woke): S6."""


class CheckoutFailed(RuntimeError):
    """The clone could not be put at the candidate's revision. Raised inside an act (after its decision was logged),
    so it is an act failure, not a refusal: the step aborts and the candidate spends its requeue budget, then parks
    (TESTPILOT_FIX_CHECKOUT_REFUSAL_LOOPS)."""


# ---------------------------------------------------------------- paths, files, rule

def ppaths(root: Path | None = None) -> dict:
    p = L.lane_paths(root)
    d = p["root"] / "trio" / "pilot"
    p.update({"dir": d, "queue": d / "queue.jsonl", "state": d / "state.jsonl", "evidence": d / "evidence.jsonl",
              "decisions": d / "decisions.jsonl", "lock": d / ".lock", "logs": d / "logs"})
    return p


def session_path(p: dict, lane: str) -> Path:
    return p["dir"] / lane / "session.json"


@contextlib.contextmanager
def locked(p: dict):
    p["dir"].mkdir(parents=True, exist_ok=True)
    with open(p["lock"], "a+") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)


def _read(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    txt = path.read_text(encoding="utf-8")
    lines = txt.split("\n")
    if lines and lines[-1].strip():     # an unterminated tail is a write still in progress: not yet a record
        lines = lines[:-1]
    return [json.loads(x) for x in lines if x.strip()]


def _append(path: Path, rec: dict) -> dict:
    L._append_jsonl(path, [rec])
    return rec


def load_rule(path: Path | None = None) -> dict:
    raw = Path(path or RULE_FILE).read_bytes()
    rule = json.loads(raw)
    rule["_sha"] = hashlib.sha256(raw).hexdigest()[:16]
    for k in ("cheap_max_launch_to_ready_s", "cheap_extra_tests", "max_acceptance_delay_s", "ladder"):
        if k not in rule:
            raise PilotRefused("reload rule file %s has no %r" % (path or RULE_FILE, k))
    return rule


def read_session(p: dict, lane: str) -> dict | None:
    sp = session_path(p, lane)
    return json.loads(sp.read_text(encoding="utf-8")) if sp.is_file() else None


def write_session(p: dict, lane: str, sess: dict):
    sp = session_path(p, lane)
    sp.parent.mkdir(parents=True, exist_ok=True)
    tmp = sp.with_suffix(".tmp")
    tmp.write_text(json.dumps(sess, sort_keys=True, indent=1) + "\n", encoding="utf-8")
    os.replace(tmp, sp)


# ---------------------------------------------------------------- candidates and their state

def classify(changed_files, has_dll: bool, mods) -> str:
    """The hot-load class the change needs (L11). Unknown changes (None) are `reload` when any mod is loaded and
    `live` only when there are no mods (nothing loaded to reload)."""
    if has_dll:
        return "cs"
    if changed_files is None:
        return "reload" if mods else "live"
    cls = "live"
    for f in changed_files:
        low = f.replace("\\", "/").lower()
        if low.endswith((".cs", ".csproj", ".dll", ".sln")) or "/assemblies/" in low:
            return "cs"
        if (low.endswith((".xml", ".png", ".ogg", ".wav", ".dds", ".psd")) or
                any(s in low for s in ("/defs/", "/patches/", "/about/", "/languages/", "/textures/", "/sounds/"))):
            if not low.startswith(tuple(h.lower() for h in HARNESS_FILES)):
                cls = "reload"
    return cls


def fingerprint(sha, mods, has_dll, profile, tier) -> str:
    """L9: the candidate's loaded artifact (sha, mods, DLL, profile, tier) plus the harness that judges it."""
    h = hashlib.sha256()
    for f in HARNESS_FILES:
        fp = L.REPO / f
        h.update(fp.read_bytes() if fp.is_file() else b"missing")
    harness = h.hexdigest()[:16]
    blob = json.dumps({"sha": sha, "mods": sorted(mods), "dll": bool(has_dll), "profile": profile, "tier": tier,
                       "harness": harness}, sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()[:20]


def candidates(p: dict) -> list[dict]:
    return _read(p["queue"])


def cand_by_id(p: dict) -> dict:
    return {c["cand"]: c for c in candidates(p)}


def states(p: dict) -> dict:
    """cand -> its current transition record. The baseline comes from the queue, so enqueue is ONE record
    (TESTPILOT_FIX_CRASH_WINDOWS_IN_LEDGER_WRITES, F4): every sealed candidate starts `queued`, and the prior attempts a
    queue record `supersedes` are `superseded` by it. The state records fold on top, terminal-sticky (the rule
    set_state enforces on write), so a crash can never leave half an enqueue. Files from before the change (explicit
    queued/superseded state records, no `supersedes`) fold to the same states."""
    out = {}
    for c in candidates(p):
        out[c["cand"]] = {"cand": c["cand"], "state": "queued", "ts": c.get("sealed_at")}
        for o in c.get("supersedes") or ():
            if out.get(o, {}).get("state") not in TERMINAL:
                out[o] = {"cand": o, "state": "superseded", "by": c["cand"], "ts": c.get("sealed_at")}
    for r in _read(p["state"]):
        if out.get(r["cand"], {}).get("state") in TERMINAL:
            continue
        out[r["cand"]] = r
    return out


def _requeues(p: dict, cand: str) -> int:
    """Requeues already spent on this candidate (a dead pilot, a failed act): the retry budget."""
    return sum(1 for r in _read(p["state"]) if r["cand"] == cand and r.get("requeued"))


def set_state(p: dict, cand: str, state: str, nolock: bool = False, only_from=None, **kw) -> dict | None:
    """One transition, checked and appended under the lock. A terminal state is never left (a superseded attempt is
    not resurrected by a late requeue); `only_from` limits the transition further. None = not applied."""
    with (contextlib.nullcontext() if nolock else locked(p)):
        cur = states(p).get(cand, {}).get("state")
        if cur in TERMINAL or (only_from is not None and cur not in only_from):
            return None
        return _append(p["state"], dict(cand=cand, state=state, ts=L._now_iso(), **kw))


def queued(p: dict) -> list[dict]:
    st = states(p)
    return [c for c in candidates(p) if st.get(c["cand"], {}).get("state") in ("queued", "testing")]


def item_parked(p: dict, item: str) -> bool:
    return any(r.get("item_parked") == item for r in _read(p["state"]))


def _check_plan(plan: dict) -> dict:
    scns = plan.get("scenarios") if isinstance(plan, dict) else None
    if not isinstance(scns, list) or not scns:
        raise PilotRefused("plan has no scenarios: the test plan is written before the build (L3)")
    ids = [s.get("id") for s in scns]
    if any(not isinstance(i, str) or not i for i in ids) or len(set(ids)) != len(ids):
        raise PilotRefused("plan scenario ids must be unique non-empty strings: %r" % ids)
    for s in scns:
        if not isinstance(s.get("argv"), list) or not s["argv"]:
            raise PilotRefused("scenario %s has no argv" % s["id"])
    return plan


# The plan keys this module reads, and nothing else (a frozen task's `live_plan` is checked against these, so a
# misspelt or invented key is refused instead of silently ignored): plan.fixture_save (the reload_save rung),
# scenario id/argv (run_scenario), footprint{files,defs} (L9a touched), taints (L8, a list of ids or "uncertain"),
# fail_rc (the exit code that means FAIL; 0 is a PASS, so it is never 0).
PLAN_KEYS = ("scenarios", "fixture_save")
SCENARIO_KEYS = ("id", "argv", "footprint", "taints", "fail_rc")
FOOTPRINT_KEYS = ("files", "defs")


def check_live_plan(plan) -> dict:
    """The strict shape of a plan as a FROZEN task carries it (`live_plan`, L3): everything _check_plan demands, plus
    only keys this module reads, every argv token a string (the program non-empty), footprint lists of strings, taints naming
    scenarios of this plan (or "uncertain"), fail_rc a non-zero int, fixture_save a non-empty string.
    PilotRefused names the first fault."""
    if not isinstance(plan, dict):
        raise PilotRefused("live_plan is %s, not a plan object" % type(plan).__name__)
    extra = sorted(set(plan) - set(PLAN_KEYS))
    if extra:
        raise PilotRefused("live_plan has keys testpilot does not read: %s" % extra)
    if isinstance(plan.get("scenarios"), list):
        for s in plan["scenarios"]:
            if not isinstance(s, dict):     # before _check_plan, whose s.get() would raise AttributeError
                raise PilotRefused("a live_plan scenario is not an object: %r" % (s,))
    _check_plan(plan)
    if "fixture_save" in plan and not (isinstance(plan["fixture_save"], str) and plan["fixture_save"].strip()):
        raise PilotRefused("live_plan fixture_save must be a non-empty string: %r" % (plan["fixture_save"],))
    ids = {s["id"] for s in plan["scenarios"]}
    for s in plan["scenarios"]:
        sid = s["id"]
        if any(c in sid for c in "/\\\0") or sid in (".", ".."):   # the id is part of the scenario's log file name
            raise PilotRefused("scenario id %r cannot name a log file (path separator, NUL or dot name)" % sid)
        extra = sorted(set(s) - set(SCENARIO_KEYS))
        if extra:
            raise PilotRefused("scenario %s has keys testpilot does not read: %s" % (sid, extra))
        if not all(isinstance(a, str) and "\0" not in a for a in s["argv"]) or not s["argv"][0]:   # "" is an argument
            raise PilotRefused("scenario %s argv must be NUL-free strings with a non-empty program: %r"
                               % (sid, s["argv"]))
        if "footprint" in s:
            fp = s["footprint"]
            if not isinstance(fp, dict) or set(fp) - set(FOOTPRINT_KEYS):
                raise PilotRefused("scenario %s footprint must be {files: [...], defs: [...]}: %r" % (sid, fp))
            for k in FOOTPRINT_KEYS:
                v = fp.get(k, [])
                if not isinstance(v, list) or not all(isinstance(x, str) and x for x in v):
                    raise PilotRefused("scenario %s footprint.%s must be a list of non-empty strings: %r"
                                       % (sid, k, v))
        if "taints" in s:
            t = s["taints"]
            if t != "uncertain" and not (isinstance(t, list) and all(isinstance(x, str) and x in ids for x in t)):
                raise PilotRefused("scenario %s taints must be \"uncertain\" or a list of this plan's scenario "
                                   "ids: %r" % (sid, t))
        if "fail_rc" in s:
            rc = s["fail_rc"]
            if isinstance(rc, bool) or not isinstance(rc, int) or rc == 0:
                raise PilotRefused("scenario %s fail_rc must be a non-zero int: %r" % (sid, rc))
    return plan


def enqueue(p: dict, item: str, sha: str, builder: str, plan: dict, mods=(), has_dll=False, profile="minimal",
            tier=None, parent=None, changed_files=None, changed_defs=None, kind="build", fault=None, review=None,
            fix_class=None, now: float | None = None) -> dict:
    """Seal a candidate into the durable queue. A newer attempt of the item supersedes its older open ones."""
    if profile == "full" or profile not in L.PROFILES:
        raise PilotRefused("profile %r refused: the trial runs minimal or minimal+deps only (owner 2026-10-29)"
                           % profile)
    if not L.same_sha(sha, sha):
        raise PilotRefused("sha %r is not a commit sha (>= 10 hex)" % sha)
    _check_plan(plan)
    if kind not in ("build", "repair"):
        raise PilotRefused("kind %r is not build|repair" % kind)
    if kind == "repair":
        if fault not in FAULTS:
            raise PilotRefused("a repair names its fault class (%s), got %r" % ("|".join(FAULTS), fault))
        if not parent:
            raise PilotRefused("a repair names the candidate it repairs (--parent)")
        if fault == "MOD" and not review:
            raise PilotRefused("a MOD repair is built by a fix subagent through its own gate AND a small blind diff "
                               "review (L10): --review names that review's record")
    mods = list(mods)
    cls = classify(changed_files, has_dll, mods)
    if fix_class:
        if fix_class not in CLASSES:
            raise PilotRefused("fix class %r is not %s" % (fix_class, "|".join(CLASSES)))
        if CLASSES.index(fix_class) < CLASSES.index(cls):
            raise PilotRefused("declared class %s is lower than the change needs (%s): a class may be raised, "
                               "never lowered" % (fix_class, cls))
        cls = fix_class
    with locked(p):
        if item_parked(p, item):
            raise PilotRefused("item %s is parked with its evidence (3 live failures or 2 crashes): the Conductor "
                               "owns it now (M6)" % item)
        byid = cand_by_id(p)
        if parent and parent not in byid:
            raise PilotRefused("parent %s is not a known candidate" % parent)
        if parent and byid[parent]["item"] != item:
            raise PilotRefused("parent %s is a candidate of %s, not %s" % (parent, byid[parent]["item"], item))
        prior = [c for c in byid.values() if c["item"] == item]
        if parent is None and prior:
            parent = prior[-1]["cand"]          # a rebuild's parent is the item's newest attempt unless named
        attempt = len(prior) + 1
        rec = {"cand": "%s@%d" % (item, attempt), "item": item, "attempt": attempt, "sha": sha, "builder": builder,
               "mods": mods, "has_dll": bool(has_dll), "profile": profile, "tier": tier, "plan": plan,
               "parent": parent, "changed_files": None if changed_files is None else list(changed_files),
               "changed_defs": list(changed_defs or []), "kind": kind, "fault": fault, "review": review,
               "class": cls, "fingerprint": fingerprint(sha, mods, has_dll, profile, tier),
               "sealed_at": L._now_iso(), "sealed_t": time.time() if now is None else float(now)}
        st = states(p)
        rec["supersedes"] = [c["cand"] for c in prior if st.get(c["cand"], {}).get("state") == "queued"]
        _append(p["queue"], rec)        # the ONE record: the candidate, its `queued` state and its supersessions (F4)
    return rec


# ---------------------------------------------------------------- evidence (L9) and the affected re-test (L9a)

def evidence(p: dict) -> list[dict]:
    return _read(p["evidence"])


def scn_hash(cand: dict, scenario: str) -> str:
    """The identity of one scenario's plan entry (argv, footprint, taints, fail_rc...): a changed entry is a new test."""
    e = next((x for x in cand["plan"]["scenarios"] if x["id"] == scenario), None)
    return hashlib.sha256(json.dumps(e, sort_keys=True).encode()).hexdigest()[:12]


def add_evidence(p: dict, cand: dict, scenario: str, status: str, lane: str, pilot: str, t: float | None = None,
                 nolock: bool = False, **kw) -> dict:
    """Append one immutable record keyed (item, fingerprint, scenario, plan entry, tier, rep); rep counts up."""
    if status not in ("pass", "fail", "invalid", "carried", "note"):
        raise ValueError("evidence status %r" % status)
    sh = scn_hash(cand, scenario)
    with (contextlib.nullcontext() if nolock else locked(p)):
        rep = 1 + sum(1 for e in evidence(p) if not _is_note(e) and
                      (e["item"], e["fingerprint"], e["scenario"], e.get("scn_hash"), e.get("tier")) ==
                      (cand["item"], cand["fingerprint"], scenario, sh, cand["tier"]))
        rec = dict(item=cand["item"], cand=cand["cand"], fingerprint=cand["fingerprint"], scenario=scenario,
                   scn_hash=sh,
                   tier=cand["tier"], profile=cand["profile"], rep=rep, status=status, lane=lane, pilot=pilot,
                   sha=cand["sha"], ts=L._now_iso(), t=time.time() if t is None else float(t), **kw)
        return _append(p["evidence"], rec)


def _is_note(e: dict) -> bool:
    """A taint note (the `taint` CLI) is an annotation, not a result. `why == "taint note"` reads the old records."""
    return e.get("status") == "note" or e.get("why") == "taint note"


def scenario_status(p: dict, cand: dict) -> dict:
    """scenario id -> its newest evidence record at this candidate's fingerprint AND this plan entry (a changed
    argv or footprint at the same sha is a new test: old results do not count for it). A taint note never
    replaces a result: it sets the taint of the FAIL/invalid result it follows."""
    out = {}
    hs = {x["id"]: scn_hash(cand, x["id"]) for x in cand["plan"]["scenarios"]}
    for e in evidence(p):
        if e["item"] == cand["item"] and e["fingerprint"] == cand["fingerprint"] and \
                e.get("scn_hash") == hs.get(e["scenario"]):
            if _is_note(e):
                prev = out.get(e["scenario"])
                if prev is not None and prev["status"] in ("fail", "invalid"):
                    out[e["scenario"]] = dict(prev, taint=e.get("taint"), taint_note=e.get("ts"))
                continue
            out[e["scenario"]] = e
    return out


def taint_note(p: dict, cand: dict, scenario: str, names, pilot: str = "pilot-note") -> dict:
    """The pilot's written taint note on a FAIL/invalid result (L8). Refused on a scenario with no such result."""
    with locked(p):                     # the check and the note: one critical section, bound to the checked result
        cur = scenario_status(p, cand).get(scenario)
        if cur is None or cur["status"] not in ("fail", "invalid"):
            raise PilotRefused("taint note on %s %s: its newest result is %s, not a FAIL or invalid"
                               % (cand["cand"], scenario, cur and cur["status"]))
        return add_evidence(p, cand, scenario, "note", "-", pilot, nolock=True, why="taint note", taint=names,
                            note_on=cur["ts"])


SCRIPT_EXT = (".py", ".sh", ".ps1", ".json", ".xml", ".txt", ".yaml", ".yml", ".toml")


def _argv_files(scn: dict) -> set:
    """Every argv token that names a file: a path, or a bare name with a script/data extension."""
    return {(a[2:] if a.startswith("./") else a).replace("\\", "/")
            for a in scn.get("argv", [])
            if isinstance(a, str) and not a.startswith("-") and ("/" in a or "\\" in a or a.lower().endswith(SCRIPT_EXT))}


def _names_file(changed: str, argf: str) -> bool:
    """A changed repo path is the argv file: equal, or the argv token is a relative tail of it (bare name or
    cwd-relative path; the proof's cwd is unknown, so a tail match errs toward re-running)."""
    return changed == argf or changed.endswith("/" + argf)


def touched(scn: dict, parent_scn: dict | None, cand: dict, parent: dict, taint_named) -> str | None:
    """Why a rebuild must re-run this scenario, or None if its parent PASS may be carried (L9a)."""
    if parent_scn is None:
        return "new scenario"
    if json.dumps(scn, sort_keys=True) != json.dumps(parent_scn, sort_keys=True):
        return "its plan entry changed"
    if taint_named == "uncertain":
        return "the parent's taint note is uncertain"
    if scn["id"] in (taint_named or ()):
        return "named by the parent's taint note"
    if cand["changed_files"] is None:
        return "the rebuild's changed files are unknown"
    for k in ("mods", "profile", "tier", "has_dll"):
        if cand[k] != parent[k]:
            return "%s changed" % k
    changed = [f.replace("\\", "/") for f in cand["changed_files"]]
    h = [f for f in changed if f in HARNESS_FILES]
    if h:
        return "harness file changed: %s" % h[0]
    fp = scn.get("footprint") or {}
    globs, defs = fp.get("files") or [], fp.get("defs") or []
    if not globs and not defs:
        return "no declared footprint"
    for f in changed:
        if any(_names_file(f, a) for a in _argv_files(scn)):
            return "its proof file changed: %s" % f
        g = next((g for g in globs if fnmatch.fnmatchcase(f, g)), None)
        if g:
            return "changed file %s matches footprint %s" % (f, g)
    d = sorted(set(cand.get("changed_defs") or []) & set(defs))
    if d:
        return "changed def %s is in its footprint" % d[0]
    return None


def parent_taint(p: dict, parent: dict):
    """The union of taint notes on the parent's failed/invalid evidence; 'uncertain' wins."""
    names = set()
    for e in scenario_status(p, parent).values():
        t = e.get("taint")
        if e["status"] in ("fail", "invalid") and t is not None:
            if t == "uncertain":
                return "uncertain"
            names |= set(t)
    return names


def plan_retest(p: dict, cand: dict, pilot: str = "plan", lane: str = "-", write: bool = True,
                t: float | None = None, nolock: bool = False) -> dict:
    """L9a. Carry every untouched parent PASS (one `carried` record each) and list what must run. Idempotent."""
    byid = cand_by_id(p)
    parent = byid.get(cand.get("parent") or "")
    scns = cand["plan"]["scenarios"]
    have = scenario_status(p, cand)
    out = {"cand": cand["cand"], "parent": cand.get("parent"), "run": {}, "carried": {}}
    if parent is None:
        out["run"] = {s["id"]: "first attempt" for s in scns if s["id"] not in have}
        return out
    pstat = scenario_status(p, parent)
    pscn = {s["id"]: s for s in parent["plan"]["scenarios"]}
    taint = parent_taint(p, parent)
    for s in scns:
        if s["id"] in have and have[s["id"]]["status"] in COUNTED:
            if have[s["id"]]["status"] == "carried":
                out["carried"][s["id"]] = have[s["id"]]["source_fingerprint"]
            continue
        pe = pstat.get(s["id"])
        if pe is None or pe["status"] not in ("pass", "carried") or pe.get("hotfix"):
            out["run"][s["id"]] = "the parent has no clean PASS for it"
            continue
        why = touched(s, pscn.get(s["id"]), cand, parent, taint)
        if why:
            out["run"][s["id"]] = why
            continue
        src = pe.get("source_fingerprint") or parent["fingerprint"]
        out["carried"][s["id"]] = src
        if write:
            add_evidence(p, cand, s["id"], "carried", lane, pilot, t=t, nolock=nolock, source_fingerprint=src,
                         source_cand=pe.get("source_cand") or parent["cand"])
    return out


# ---------------------------------------------------------------- the reload rule (M1)

def reload_cost(p: dict, rule: dict, lane: str, profile: str, tier) -> dict:
    """The MEASURED launch-to-ready cost of this lane+profile+tier: median of the newest N ok rows. Never a default."""
    rows = [r for r in L.load_times(p, lane) if r.get("profile") == profile and r.get("tier") == tier]
    rows = rows[-int(rule.get("load_time_samples", 5)):]
    thr = rule["cheap_max_launch_to_ready_s"]
    if not rows:
        cls = rule.get("unmeasured_cost_class", "expensive")
        return {"cost_s": None, "basis": "UNMEASURED (no ok load_times row for %s %s %s)" % (lane, profile, tier),
                "class": cls, "threshold_s": thr}
    med = statistics.median(float(r["launch_to_ready_s"]) for r in rows)
    return {"cost_s": round(med, 1), "basis": "measured median of %d" % len(rows),
            "class": "cheap" if med <= thr else "expensive", "threshold_s": thr}


def hot_appliable(cand: dict, game: dict | None, byid: dict) -> bool:
    """Only a `live` candidate whose mod set is the one loaded may change the running game (S3, L10)."""
    if not game or cand["class"] != "live":
        return False
    loaded = byid.get(game.get("cand") or "")
    same = (cand["profile"], cand["tier"]) == (game.get("profile"), game.get("tier"))
    if not same:
        return False
    if not cand["mods"]:
        return not game.get("mods")
    return loaded is not None and cand.get("parent") == loaded["cand"] and cand["mods"] == loaded["mods"]


def _pending(p: dict, cand: dict, sess: dict) -> tuple[list, list]:
    """(valuable scenario ids, blocked ones) of a candidate on the current state. Blocked = named by a taint note or
    hot-fixed since the last state reset: a reset (fixture reload or reload) restores them. A scenario whose
    pre-canary was red is blocked only until a green canary (M1: a red canary is re-checked, not reloaded); red again
    on that re-check, it stays blocked until a reset."""
    have = scenario_status(p, cand)
    reset_t = (sess.get("game") or {}).get("reset_t", 0)
    red = (sess.get("game") or {}).get("canary_red") or {}
    taint, uncertain = set(), False
    for e in have.values():
        if e["status"] in ("fail", "invalid") and e.get("t", 0) > reset_t and e.get("taint") is not None:
            if e["taint"] == "uncertain":
                uncertain = True
            else:
                taint |= set(e["taint"])
    val, blocked = [], []
    for s in cand["plan"]["scenarios"]:
        e = have.get(s["id"])
        if e and e["status"] in COUNTED and not e.get("hotfix"):
            continue
        if e and e.get("hotfix") and e.get("t", 0) > reset_t:
            blocked.append(s["id"])
        elif (uncertain or s["id"] in taint) and not (e and e["status"] in ("fail", "invalid")):
            blocked.append(s["id"])
        elif e and e["status"] == "invalid" and e.get("why") == "canary red" and \
                red.get(_red_key(cand, s["id"])) in ("red", "stuck"):
            blocked.append(s["id"])
        else:
            val.append(s["id"])
    return val, blocked


def carry_why(p: dict, c: dict) -> str | None:
    """L9a: why the rebuild `c` resolves by carry with no reload and no test, else None. The one predicate: decide
    and the wake's reconcile both route a carry-ready rebuild through Pilot.carry."""
    if not c.get("parent"):
        return None
    pre = plan_retest(p, c, write=False)
    have = scenario_status(p, c)
    ids = {s["id"] for s in c["plan"]["scenarios"]}
    # F1: a FAIL at this fingerprint is as final as a pass: a rebuild whose every scenario is counted (pass,
    # fail or carried) resolves to its verdict without a reload, never re-runs the failing scenario
    counted = {i for i in ids if have.get(i, {}).get("status") in COUNTED and not have[i].get("hotfix")}
    if not pre["run"] and (set(pre["carried"]) == ids or counted == ids):
        return ("every scenario of %s is carried from %s or already counted (pass/fail) at its fingerprint (L9a): "
                "it resolves with no reload and no test" % (c["cand"], c["parent"]))
    return None


def decide(p: dict, lane: str, sess: dict | None, facts: dict, rule: dict, now: float) -> dict:
    """The one decision function. facts: process_alive, canary_ok (None = not run)."""
    sess = sess or {}
    game = sess.get("game")
    byid = cand_by_id(p)
    q = queued(p)
    base = {"rule": None, "lane": lane}
    for c in q:                         # L9a: a rebuild that carries every scenario needs no game at all
        why = carry_why(p, c)
        if why:
            return dict(base, action="carry", cand=c["cand"], why=why)
    if game and facts.get("process_alive") and facts.get("canary_ok") is False:
        tried = set(sess.get("ladder_tried") or [])
        spent = int(sess.get("red_rungs") or 0)       # survive a green blip and a reload: only a finished test clears
        max_rungs = int(rule.get("max_red_rungs", 6))
        if spent >= max_rungs:
            return dict(base, action="park", cand=(_target(q, game, byid) or {}).get("cand"),
                        why="the canary keeps flapping: %d recovery rungs spent without one finished test "
                            "(max %d): parked for escalation, no further ladder (M1)" % (spent, max_rungs))
        for rung in rule["ladder"]:
            if rung != "hold" and rung not in tried:
                return dict(base, action="ladder", rung=rung, why="canary red on a live process: recovery ladder "
                            "before any reload (a red canary alone is no restart)")
        if int(sess.get("red_reloads") or 0) >= int(rule.get("max_red_reloads", 1)):
            return dict(base, action="park", cand=(_target(q, game, byid) or {}).get("cand"),
                        why="the canary is red again after the ladder and %d reload(s) spent on a red canary "
                            "(max %d): parked for escalation, not reloaded again (M1)"
                            % (int(sess.get("red_reloads") or 0), int(rule.get("max_red_reloads", 1))))
        return _reload(p, rule, lane, base, "R1", _target(q, game, byid), now, sess,
                       "the canary is still red after every ladder rung (%s)" % ", ".join(sorted(tried)),
                       red=True)
    if not game:
        if not q:
            return dict(base, action="idle", why="no game and nothing queued")
        return _reload(p, rule, lane, base, "R0", q[0], now, sess, "cold start: no game in this lane's session")
    if not facts.get("process_alive"):
        t = _target(q, game, byid)
        if t is None:
            return dict(base, action="idle", why="the game is down and nothing is queued")
        return _reload(p, rule, lane, base, "R1", t, now, sess, "the game process is dead")
    loaded = byid.get(game.get("cand") or "")
    st = states(p)
    valuable, blocked = [], []
    if loaded is not None and st.get(loaded["cand"], {}).get("state") in ("queued", "testing"):
        v, b = _pending(p, loaded, sess)
        valuable += [(loaded, s) for s in v]
        blocked += [(loaded, s) for s in b]
    for c in q:
        if c is not loaded and (loaded is None or c["cand"] != loaded["cand"]) and hot_appliable(c, game, byid):
            v, b = _pending(p, c, sess)
            valuable += [(c, s) for s in v]
            blocked += [(c, s) for s in b]
    need = [c for c in q if (loaded is None or c["cand"] != loaded["cand"]) and not hot_appliable(c, game, byid)]
    sealed = [c for c in need if c["kind"] == "repair"]
    if valuable:
        if sealed:                      # F8: every sealed repair's drain is checked, not only the first queued
            ev_all = evidence(p)
            overdue, cheap_spent = [], None
            for rep in sealed:
                cost = reload_cost(p, rule, lane, rep["profile"], rep["tier"])
                age = now - rep["sealed_t"]
                max_delay = rule["max_acceptance_delay_s"][cost["class"]]
                since = sum(1 for e in ev_all if e.get("lane") == lane and e["status"] in ("pass", "fail")
                            and e.get("t", 0) > rep["sealed_t"])
                drain = {"class": cost["class"], "age_s": round(age, 1), "max_delay_s": max_delay,
                         "tests_since_sealed": since, "extra_tests": rule["cheap_extra_tests"],
                         "valuable_left": len(valuable)}
                if age >= max_delay:
                    overdue.append((age - max_delay, rep, drain, "the maximum acceptance delay (%ss, %s) has passed"
                                    % (max_delay, cost["class"])))
                elif cheap_spent is None and cost["class"] == "cheap" and since >= rule["cheap_extra_tests"]:
                    cheap_spent = (rep, drain, "cheap reload: %d more tests run since the repair was sealed" % since)
            pick = None
            if overdue:                 # the most overdue first; else the first cheap one whose test count is spent
                _, rep, drain, spent = max(overdue, key=lambda x: x[0])
                pick = (rep, drain, spent)
            elif cheap_spent:
                pick = cheap_spent
            if pick:
                rep, drain, spent = pick
                return _reload(p, rule, lane, base, "R3", rep, now, sess, "sealed %s repair %s is waiting; %s"
                               % (rep["class"], rep["cand"], spent), drain=drain)
        c, s = valuable[0]
        act = "test" if loaded is not None and c["cand"] == loaded["cand"] else "hot_apply"
        return dict(base, action=act, cand=c["cand"], scenario=s,
                    why="a valuable test remains on the loaded artifact" if act == "test"
                    else "a live-class candidate applies to the running game without a reload")
    if blocked:
        tried = set(sess.get("ladder_tried") or [])
        if "reload_save" not in tried:
            return dict(base, action="ladder", rung="reload_save",
                        why="only tests blocked by a taint note or a hot-fix remain: a state reset restores them")
    if blocked and not need:
        stuck = [c for c, _ in blocked if st.get(c["cand"], {}).get("state") in ("queued", "testing")]
        if stuck:                       # the save reset was tried and could not restore them: only a reload can
            return _reload(p, rule, lane, base, "R2", stuck[0], now, sess,
                           "no valuable valid test remains, %d blocked and the state reset (reload_save) did not "
                           "restore them: a reload of %s does" % (len(blocked), stuck[0]["cand"]))
    if need:
        tgt = (sealed or need)[0]
        r = "R3" if sealed else "R2"
        if sealed:
            cost = reload_cost(p, rule, lane, tgt["profile"], tgt["tier"])
            drain = {"class": cost["class"], "age_s": round(now - tgt["sealed_t"], 1), "valuable_left": 0}
        else:
            drain = None
        return _reload(p, rule, lane, base, r, tgt, now, sess,
                       "no valuable valid test remains on the loaded artifact (%d blocked) and %s %s needs a reload%s"
                       % (len(blocked), "sealed repair" if sealed else "candidate", tgt["cand"],
                          ": the drain is spent" if sealed else ""), drain=drain)
    return dict(base, action="idle", why="nothing valuable left and nothing queued that needs a reload")


def _inf_key(inf: dict) -> str:
    """The identity of one in-flight test: its id, or (records from before ids) cand|scenario|start time."""
    return inf.get("id") or "%s|%s|%s" % (inf.get("cand"), inf.get("scenario"), inf.get("t"))


def _red_key(cand: dict, sid: str) -> str:
    return "%s|%s" % (cand["cand"], sid)


def _canary_green(sess: dict):
    """A green canary: every scenario blocked by a red pre-canary gets its one re-check."""
    red = (sess.get("game") or {}).get("canary_red") or {}
    for k, v in red.items():
        if v == "red":
            red[k] = "recheck"


def _target(q, game, byid):
    loaded = byid.get((game or {}).get("cand") or "")
    if loaded is not None and any(c["cand"] == loaded["cand"] for c in q):
        return loaded
    return q[0] if q else None


def _reload(p, rule, lane, base, r, cand, now, sess, why, drain=None, red=False):
    if cand is None:
        return dict(base, action="idle", why="%s would apply but no candidate is queued" % r)
    cost = reload_cost(p, rule, lane, cand["profile"], cand["tier"])
    started = (sess or {}).get("started_t")
    churn = bool(started and now - started > rule.get("churn_alarm_session_age_s", 2700))
    return dict(base, action="reload", rule=r, cand=cand["cand"], why=why, cost=cost, drain=drain, red=red,
                rule_sha=rule["_sha"], churn_alarm=churn)


# ---------------------------------------------------------------- the pilot

class Pilot:
    """One fresh pilot pass. wake() -> step()* -> handoff() | close(). Every act re-checks it still drives the lane."""

    def __init__(self, lane: str, driver, pilot_id: str, clone: str | None = None, root: Path | None = None,
                 rule: dict | None = None):
        if lane not in L.LANES:
            raise PilotRefused("unknown lane %r" % lane)
        self.lane_name, self.d, self.id, self.clone = lane, driver, pilot_id, clone
        self.p = ppaths(root)
        self.root = root
        self.rule = rule or load_rule()
        self.lane = None
        self.epoch = None
        self.gen = None                 # the session generation this pilot woke into: its ownership token
        self._canary_ctx = None         # F2: the periodic in-proof canary of the running test, else None
        self.retired = False
        self._ev0 = None                # evidence length at the start of the current step (abort reads past it)

    # -- logging
    def _ev(self, event, **kw):
        return L.emit(self.p, dict(arm=ARM, lane=self.lane_name, run_id=self.lane.run_id if self.lane else self.id,
                                   event=event, **kw))

    def _decision(self, rec: dict) -> dict:
        rec = dict(rec, id="d-%s" % uuid.uuid4().hex[:10], pilot=self.id, ts=L._now_iso(), t=self.d.clock())
        return _append(self.p["decisions"], rec)

    # -- session
    def _sess(self) -> dict:
        return read_session(self.p, self.lane_name) or {}

    def _save(self, sess: dict):
        write_session(self.p, self.lane_name, sess)

    def _check_live(self) -> dict:
        """S6: refuse every act once this pilot no longer drives the lane."""
        if self.retired:
            raise StalePilot("pilot %s has handed off or aborted: no further act" % self.id)
        s = self._sess()
        if s.get("pilot") != self.id or s.get("status") != "live":
            raise StalePilot("pilot %s does not drive lane %s (session: pilot %s, %s)"
                             % (self.id, self.lane_name, s.get("pilot"), s.get("status")))
        if s.get("generation") != self.gen:
            raise StalePilot("pilot %s woke as generation %s, the session is at %s: another wake took the lane"
                             % (self.id, self.gen, s.get("generation")))
        if s.get("epoch") != self.epoch:
            raise StalePilot("pilot %s holds epoch %s, the game is at %s" % (self.id, self.epoch, s.get("epoch")))
        return s

    def wake(self, takeover_dead: bool = False) -> dict:
        """Take the lane from the session file. Refused while another pilot is live unless it is known dead."""
        with locked(self.p):
            s = self._sess()
            prev = s.get("pilot")
            if s.get("status") == "live" and not takeover_dead:     # even under the same id: one live pilot
                raise PilotRefused("pilot %s is live on %s: it hands off at a test boundary first" % (prev,
                                                                                                    self.lane_name))
            interrupted = s.get("in_flight") if s.get("status") == "live" else None
            # F6: the interruption moves to a durable `recovering` list in the same write that clears in_flight, and
            # leaves it only once processed: a replacement pilot dying in this wake leaves it for the next one
            recovering = list(s.get("recovering") or [])
            if interrupted and _inf_key(interrupted) not in {_inf_key(x) for x in recovering}:
                # an in_flight from before ids gets one here, so two interruptions never share a key
                recovering.append(dict(interrupted, why="pilot %s died mid-test" % prev,
                                       id=interrupted.get("id") or "f-%s" % uuid.uuid4().hex[:10]))
            s.update({"lane": self.lane_name, "pilot": self.id, "status": "live",
                      "generation": int(s.get("generation") or 0) + 1, "woken_at": L._now_iso()})
            s.setdefault("epoch", 0)
            s.setdefault("started_t", self.d.clock())
            s["in_flight"] = None
            s["recovering"] = recovering
            pend = s.get("pending_reload")
            if pend:                    # F7: the outcome of that reload is unknown, so the session game is not adopted
                rec = self._decision({"kind": "reconcile", "pending_reload": pend, "was_game": (s.get("game") or {})
                                      .get("cand"), "why": "pilot %s died during reload decision %s of %s: what the "
                                      "game runs is unknown (the canary's sha check reads the session, not the "
                                      "game), so the session game is dropped and the next load is a ruled R0"
                                      % (prev, pend.get("decision"), pend.get("cand"))})
                s["game"], s["pending_reload"] = None, None
                s["epoch"] = int(s.get("epoch") or 0) + 1
                s["reconciled_reload"] = rec["id"]
            self._save(s)
        self.epoch, self.gen = s["epoch"], s["generation"]
        for inf in recovering:          # the old pilot died mid-test (M5): invalid, requeued once, crash kept
            self._interrupted(inf, inf.get("why") or "pilot %s died mid-test" % prev)
            with locked(self.p):
                s2 = self._sess()
                if s2.get("generation") == self.gen:
                    s2["recovering"] = [x for x in (s2.get("recovering") or []) if _inf_key(x) != _inf_key(inf)]
                    self._save(s2)
        self._reconcile()               # F5: durable evidence -> candidate state, before any scheduling
        self.lane = L.Lane(self.lane_name, ARM, self.d, "trio pilot %s" % self.id, task=None, root=self.root)
        try:
            self.lane.take()
        except L.LaneRefused:
            self._retire("take refused")
            raise
        g = s.get("game")
        if g:                           # the game stayed up: rebuild the Lane from the session, not from memory
            self.lane.launched_at = g.get("launched_at")
            self.lane.deployed = {"sha": g.get("deployed_sha"), "mods": g.get("mods") or [],
                                  "package_ids": g.get("package_ids") or []}
            self.lane.profile = {"profile": g.get("profile"), "tier": g.get("tier")}
            ea = g.get("expected_active")
            self.lane.expected_active = set(ea) if ea is not None else None
            self.lane.loaded_save = g.get("loaded_save")
        q = queued(self.p)
        cursor = s.get("cursor")
        self._ev("pass_start", detail={"pilot": self.id, "adopted_from": prev, "generation": s["generation"],
                                       "cursor": cursor, "queued": [c["cand"] for c in q],
                                       "game_up": bool(g), "interrupted": interrupted})
        return {"queued": [c["cand"] for c in q], "adopted_from": prev, "cursor": cursor, "session": s}

    def _retire(self, why):
        with locked(self.p):
            s = self._sess()
            if s.get("pilot") == self.id:
                s["status"] = "handoff"
                self._save(s)
        self.retired = True

    def handoff(self, why: str = "pass end") -> dict:
        """End this pass at a test boundary; the game stays up; the next pilot reads the session file."""
        s = self._check_live()
        if s.get("in_flight"):
            raise PilotRefused("handoff only at a test boundary: %s is in flight" % s["in_flight"])
        with locked(self.p):            # no wake can read the session between the release and the publish
            s = self._check_live()
            ok, out = self.d.bridge_release(self.lane.host)   # NOT Lane.release: the list stays swapped, the game up
            if not ok:
                raise PilotRefused("handoff: the bridge release failed, the lane stays this pilot's: %s"
                                   % (out or "")[-200:])
            s.update({"status": "handoff", "handed_by": self.id, "handoff_at": L._now_iso(),
                      "cursor": len(_read(self.p["state"]))})
            self._save(s)
        self.lane.held = False
        self.lane._ev("live_release", verdict="ok" if ok else "error",
                      detail={"handoff": True, "game_left_up": True, "list_restore": "owed (swap marker kept)",
                              "out": (out or "")[-200:]})
        self._ev("pass_end", detail={"pilot": self.id, "handoff": True, "why": why, "cursor": s["cursor"],
                                     "queued": [c["cand"] for c in queued(self.p)], "bridge_release_ok": ok})
        self.retired = True
        return s

    def close(self, why: str = "lane closed") -> dict:
        """Full release: the owner's list and main's mod files are restored (Lane.release)."""
        self._check_live()
        with locked(self.p):            # released before published: no wake sees the lane free while we restore
            s = self._check_live()
            self.lane.release(aborted=False, why=why)
            s.update({"status": "closed", "game": None, "closed_by": self.id, "in_flight": None})
            self._save(s)
        self.retired = True
        self._ev("pass_end", detail={"pilot": self.id, "closed": True, "why": why})
        return s

    def _interrupted(self, inflight: dict, why: str):
        """Idempotent per interruption (F6): its invalid record and its requeue/park carry the in_flight key, and a
        step already recorded is not recorded again by a later wake."""
        byid = cand_by_id(self.p)
        c = byid.get(inflight.get("cand"))
        if c is None:
            return
        key = _inf_key(inflight)
        if not any(e.get("interrupt") == key for e in evidence(self.p)):
            add_evidence(self.p, c, inflight["scenario"], "invalid", self.lane_name, self.id, t=self.d.clock(),
                         why=why, crash=True, taint=None, interrupt=key)
        self._crashed(c)                # a second crash on the item quarantines it, whichever way it crashed (M5)
        if any(r.get("interrupt") == key for r in _read(self.p["state"])):
            return
        if _requeues(self.p, c["cand"]) >= int(self.rule.get("max_interrupt_requeues", 1)):
            set_state(self.p, c["cand"], "parked", why="interrupted again: %s" % why, interrupt=key)
        else:
            set_state(self.p, c["cand"], "queued", requeued=True, why=why, interrupt=key)

    def _reconcile(self):
        """F5: a pilot that died between saving a result and _crashed/_resolve left the candidate open with the
        evidence that decides it. Both are idempotent (a terminal state is never left): re-run them for every open
        candidate, so a wake after a clean pass changes nothing. A carry-ready rebuild (L9a) goes through carry() --
        its decision, its carried records, the supersede of older attempts -- never through a bare _resolve on its
        parent's evidence (TESTPILOT_FIX_WAKE_RECONCILE_SKIPS_CARRY)."""
        for c in queued(self.p):
            why = carry_why(self.p, c)
            if why:
                try:
                    self.carry({"action": "carry", "cand": c["cand"], "why": why})
                except PilotRefused:    # changed under us (superseded, closed): left to the scheduler, not resolved
                    pass
                continue
            self._crashed(c)
            self._resolve(c)

    # -- facts, the loop
    def facts(self, canary_ok=None) -> dict:
        return {"process_alive": bool(self.d.game_running()), "canary_ok": canary_ok}

    def decide(self, canary_ok=None) -> dict:
        s = self._check_live()
        return decide(self.p, self.lane_name, s, self.facts(canary_ok), self.rule, self.d.clock())

    def step(self, canary_ok=None) -> dict:
        """One decision and its act. Returns {decision, result}."""
        self._ev0 = len(evidence(self.p))  # abort reads only what this step recorded
        try:
            dec = self.decide(canary_ok)
            if dec["action"] == "reload":
                return {"decision": dec, "result": self.reload(dec)}
            if dec["action"] == "carry":
                return {"decision": dec, "result": self.carry(dec)}
            if dec["action"] == "park":
                return {"decision": dec, "result": self.park(dec)}
            if dec["action"] == "ladder":
                return {"decision": dec, "result": self.ladder(dec)}
            if dec["action"] in ("test", "hot_apply"):
                return {"decision": dec, "result": self.test(dec)}
            return {"decision": dec, "result": None}
        except (StalePilot, PilotRefused):
            raise                       # not this pilot's lane (or refused before any act): nothing of ours to release
        except Exception as e:  # noqa: BLE001 - a launch failure/timeout or any act failing: end the pass cleanly
            return {"decision": locals().get("dec") or {"action": "abort"}, "result": self.abort(e, locals().get("dec"))}

    def abort(self, exc, dec: dict | None = None) -> dict:
        """An act failed (launch failure or timeout, a failed stop...): his list and files are restored, the bridge
        released, the session ended and the step recorded (invalid evidence, the candidate requeued once then parked).
        Reuses Lane.release (the one restore-and-release path). Never raises for a failure of its own."""
        why = "%s: %s" % (type(exc).__name__, str(exc)[-300:])
        if self.retired:
            return {"abort": why, "released": False}
        s = self._sess()
        inf = s.get("in_flight") if s.get("pilot") == self.id and s.get("generation") == self.gen else None
        c = cand_by_id(self.p).get((inf or {}).get("cand") or (dec or {}).get("cand"))
        if c is not None:
            # the invalid record goes on the scenario that was running (in_flight), else the one this decision
            # chose, else (a reload/launch failure) the one the next test would run -- never "the first with no
            # evidence", which is a different scenario once any result exists (TESTPILOT_FIX_ABORT_WRONG_SCENARIO)
            if inf and inf.get("cand") == c["cand"]:
                scn = inf.get("scenario")
            elif (dec or {}).get("scenario") and (dec or {}).get("cand") == c["cand"]:
                scn = dec["scenario"]
                if any(e["scenario"] == scn and e.get("pilot") == self.id and e.get("cand") == c["cand"]
                       and not _is_note(e) for e in (evidence(self.p)[self._ev0:] if self._ev0 is not None else [])):
                    scn = None          # this act already recorded its result: the failure came after it
            else:
                v, _b = _pending(self.p, c, s)
                scn = v[0] if v else None
            if scn:
                add_evidence(self.p, c, scn, "invalid", self.lane_name, self.id, t=self.d.clock(), why=why,
                             crash=False, taint=None)
            n = _requeues(self.p, c["cand"])
            if n >= int(self.rule.get("max_interrupt_requeues", 1)):
                set_state(self.p, c["cand"], "parked", why="act failed again: %s" % why)
            else:
                set_state(self.p, c["cand"], "queued", requeued=True, why=why)
        err = None
        with locked(self.p):
            s = self._sess()
            mine = s.get("pilot") == self.id and s.get("generation") == self.gen
            if mine:
                try:
                    self.lane.release(aborted=True, why="act failed: %s" % why)
                except Exception as e:  # noqa: BLE001 - RestoreFailed or worse: logged, the session still ends
                    err = str(e)
                s.update({"status": "aborted", "game": None, "in_flight": None, "aborted_by": self.id,
                          "pending_reload": None})
                self._save(s)
        self.retired = True
        rec = self._decision({"kind": "abort", "why": why, "cand": (dec or {}).get("cand"), "restore_error": err})
        self._ev("pass_end", detail={"pilot": self.id, "abort": True, "decision": rec["id"], "why": why})
        return rec

    def run_pass(self, max_steps: int = 50) -> list[dict]:
        """Steps until idle, an abort, or the first candidate it tested resolves (one item per pass, L7)."""
        out, first, canary_ok = [], None, None
        for _ in range(max_steps):
            r = self.step(canary_ok)
            out.append(r)
            a = r["decision"]["action"]
            if a == "idle":
                break
            res = r.get("result") or {}
            if _aborted(res):           # abort ended the session and retired this pilot: no further step
                break
            canary_ok = res.get("canary_ok") if isinstance(res, dict) else None
            if a in ("test", "hot_apply"):
                first = first or r["decision"]["cand"]
                if states(self.p).get(first, {}).get("state") in TERMINAL:
                    break
        return out

    # -- acts
    def park(self, dec: dict) -> dict:
        """M1: a canary that will not stay green is escalated, not looped: the target is parked, the decision logged."""
        self._check_live()
        rec = self._decision({"kind": "park", "cand": dec.get("cand"), "why": dec["why"]})
        if dec.get("cand"):
            set_state(self.p, dec["cand"], "parked", why=dec["why"])
        with locked(self.p):
            s = self._check_live()
            s["red_rungs"], s["red_reloads"], s["ladder_tried"] = 0, 0, []
            self._save(s)
        return {"decision": rec, "parked": dec.get("cand")}

    def carry(self, dec: dict) -> dict:
        """L9a: an all-carried rebuild writes its carried records and resolves; the game is not touched."""
        self._check_live()
        c = cand_by_id(self.p)[dec["cand"]]
        rec = self._decision({"kind": "carry", "cand": c["cand"], "why": dec["why"]})
        with locked(self.p):            # ownership, the target's state, the carried records and the verdict: one
            self._check_live()          # critical section, so a stale pilot or a superseded target publishes nothing
            cur = states(self.p).get(c["cand"], {}).get("state")
            if cur not in ("queued", "testing"):
                raise PilotRefused("%s is %s (changed since the decision): not carried" % (c["cand"], cur))
            retest = plan_retest(self.p, c, pilot=self.id, lane=self.lane_name, t=self.d.clock(), nolock=True)
            if retest["run"]:
                raise PilotRefused("carry of %s: %s must run" % (c["cand"], sorted(retest["run"])))
            self._resolve(c, nolock=True)   # an all-carried rebuild resolves here: no test would ever run for it
            st = states(self.p).get(c["cand"], {})
            if st.get("state") not in TERMINAL:
                raise PilotRefused("carry of %s did not resolve it (%s)" % (c["cand"], st.get("state")))
        self._supersede_older(c)
        return {"decision": rec, "retest": retest, "state": st}

    def reload(self, dec: dict) -> dict:
        """The one way this pilot reloads. Refused without a rule (S4). The decision is logged before the reload."""
        if not dec.get("rule") or dec.get("rule") not in L.RELOAD_RULES:
            raise PilotRefused("no reload without a rule (M1, S4): decision %r" % dec)
        self._check_live()
        c = cand_by_id(self.p).get(dec.get("cand"))
        if c is None:
            raise PilotRefused("reload target %r is not a known candidate" % dec.get("cand"))
        if not self.clone:
            raise PilotRefused("candidate %s: the pilot needs its own clone (--clone): its proofs run from the "
                               "candidate's revision" % c["cand"])
        cost = dec.get("cost") or {}
        rec = self._decision({"kind": "reload", "rule": dec["rule"], "cand": c["cand"], "class": c["class"],
                              "why": dec["why"], "cost": cost, "drain": dec.get("drain"),
                              "rule_sha": dec.get("rule_sha"), "churn_alarm": dec.get("churn_alarm")})
        self._at_rev(c)
        why = ("decision=%s rule=%s %s; cost_used=%s s (%s) class=%s threshold=%s s rule_sha=%s"
               % (rec["id"], dec["rule"], dec["why"], cost.get("cost_s"), cost.get("basis"), cost.get("class"),
                  cost.get("threshold_s"), dec.get("rule_sha")))
        with locked(self.p):            # F7: the reload is recorded pending BEFORE the game is touched
            s = self._check_live()      # S6: last check before touching the game (a takeover is of a DEAD pilot only)
            s["pending_reload"] = {"decision": rec["id"], "cand": c["cand"], "sha": c["sha"], "t": self.d.clock()}
            self._save(s)
        ev = self.lane.reload(c["profile"], c["tier"], rule=dec["rule"], mods=c["mods"], has_dll=c["has_dll"],
                              clone=self.clone if c["mods"] else None, sha=c["sha"] if c["mods"] else None, why=why)
        now = self.d.clock()
        with locked(self.p):
            s = self._check_live()   # S6: a takeover during the act wins
            s["epoch"] = int(s.get("epoch") or 0) + 1
            s["game"] = {"cand": c["cand"], "fingerprint": c["fingerprint"], "launched_at": self.lane.launched_at,
                         "deployed_sha": self.lane.deployed.get("sha"), "mods": list(c["mods"]),
                         "package_ids": list(self.lane.deployed.get("package_ids") or []),
                         "profile": c["profile"], "tier": c["tier"], "reset_t": now,
                         "expected_active": sorted(self.lane.expected_active)
                         if self.lane.expected_active is not None else None,
                         "loaded_save": None, "hot_applied_t": None, "reload_decision": rec["id"]}
            s["pending_reload"] = None  # F7: published in the same write that clears the pending marker
            s["ladder_tried"] = []
            if dec.get("red"):
                s["red_reloads"] = int(s.get("red_reloads") or 0) + 1   # a reload does not forgive a red canary
            self._save(s)
        self.epoch = s["epoch"]
        self._supersede_older(c)
        retest = plan_retest(self.p, c, pilot=self.id, lane=self.lane_name, t=self.d.clock())
        self._resolve(c)
        return {"reload_event": ev, "decision": rec, "retest": retest}

    def ladder(self, dec: dict) -> dict:
        s = self._check_live()
        rung = dec["rung"]
        ok, out = False, ""
        if rung == "reconnect":
            ok, out = self.d.reconnect()
        elif rung == "reload_save":
            g = s.get("game") or {}
            c = cand_by_id(self.p).get(g.get("cand") or "")
            fx = (c or {}).get("plan", {}).get("fixture_save")
            if fx:
                try:
                    self.lane.load_save(fx)
                    ok, out = True, "loaded fixture %s" % fx
                except L.LaneRefused as e:
                    ok, out = False, str(e)
            else:
                ok, out = False, "no fixture_save in the loaded candidate's plan"
        elif rung == "restage":
            ok, out = self.d.restage()
        with locked(self.p):
            s = self._check_live()
            s["ladder_tried"] = sorted(set(s.get("ladder_tried") or []) | {rung})
            s["red_rungs"] = int(s.get("red_rungs") or 0) + 1
            if ok and rung == "reload_save" and s.get("game"):
                s["game"]["reset_t"] = self.d.clock()
                s["game"]["loaded_save"] = self.lane.loaded_save
                s["game"]["canary_red"] = {}
            self._save(s)
        self._decision({"kind": "ladder", "rung": rung, "ok": ok, "out": (out or "")[-200:], "why": dec["why"]})
        if rung == "reload_save" and not ok:   # its blocked scenarios cannot be restored: a failed one resolves
            lc = cand_by_id(self.p).get((s.get("game") or {}).get("cand") or "")
            if lc is not None:
                self._resolve(lc)
        can = self.lane.canary(self._expect_sha(s))
        if can["ok"]:
            with locked(self.p):
                s = self._check_live()
                s["ladder_tried"] = [] if rung != "reload_save" else s.get("ladder_tried", [])
                _canary_green(s)
                self._save(s)
        return {"rung": rung, "ok": ok, "canary_ok": can["ok"]}

    def _supersede_older(self, c):
        """A newer attempt is on the game (reloaded or hot-applied): the item's older open attempts are done."""
        st = states(self.p)
        for o in candidates(self.p):
            if o["item"] == c["item"] and o["attempt"] < c["attempt"] and \
                    st.get(o["cand"], {}).get("state") in ("queued", "testing"):
                set_state(self.p, o["cand"], "superseded", only_from=("queued", "testing"), by=c["cand"],
                          why="a newer attempt is on the game")

    def _at_rev(self, c) -> str:
        """The clone is at the candidate's revision (its proofs and its mods come from there), checked out if not."""
        if not self.clone:
            raise PilotRefused("candidate %s: no clone to run its proofs from (--clone)" % c["cand"])

        def at(h):
            return bool(h) and (h.startswith(c["sha"]) or c["sha"].startswith(h))
        head = self.d.clone_head(self.clone)
        if not at(head):
            ok, out = self.d.checkout(self.clone, c["sha"])
            if not ok:
                raise CheckoutFailed("checkout of %s failed: %s" % (c["sha"], (out or "")[-200:]))
            head = self.d.clone_head(self.clone)
            if not at(head):
                raise CheckoutFailed("clone %s is at %s after checking out %s" % (self.clone, head, c["sha"]))
        return head

    def _poll(self):
        """Polled while a proof runs: this pilot still owns the lane (S6), and (F2, L8) the canary runs every
        scenario_canary_every_s, so a game that breaks and recovers inside a long proof does not read green at both
        ends. The first red is kept and makes the result invalid; the proof itself is not stopped."""
        self._check_live()
        every = float(self.rule.get("scenario_canary_every_s", 120))
        if every <= 0 or self._canary_ctx is None or self.d.clock() - self._canary_ctx["last"] < every:
            return
        self._canary_ctx["last"] = self.d.clock()
        can = self.lane.canary(self._canary_ctx["sha"])
        self._canary_ctx["runs"] += 1
        if not can["ok"] and self._canary_ctx["red"] is None:
            self._canary_ctx["red"] = {"t": self.d.clock(), "problems": list(can.get("problems") or [])[:5]}

    def _expect_sha(self, s):
        g = s.get("game") or {}
        return g.get("deployed_sha") if g.get("mods") else None

    def test(self, dec: dict) -> dict:
        """Run one scenario: canary, in-flight record, the proof (ownership polled), canary, one evidence record."""
        s = self._check_live()
        byid = cand_by_id(self.p)
        c = byid[dec["cand"]]
        g = s["game"]
        hot = False
        if dec["action"] == "hot_apply" or g.get("cand") != c["cand"]:
            if not hot_appliable(c, g, byid):
                raise PilotRefused("%s (class %s) is not hot-loadable onto %s: it waits sealed for a reload (S3)"
                                   % (c["cand"], c["class"], g.get("cand")))
            self._at_rev(c)
            with locked(self.p):
                s = self._check_live()
                s["game"]["cand"], s["game"]["fingerprint"] = c["cand"], c["fingerprint"]
                if c["kind"] == "repair" and c["fault"] in ("HARNESS", "SITE"):
                    s["game"]["hot_applied_t"] = self.d.clock()
                self._save(s)
            self._decision({"kind": "hot_apply", "cand": c["cand"], "class": c["class"], "why": dec["why"]})
            self._supersede_older(c)
            rt = plan_retest(self.p, c, pilot=self.id, lane=self.lane_name, t=self.d.clock())
            g = s["game"]
            if dec["scenario"] in rt["carried"]:   # L9a: a carried PASS is never re-run
                self._resolve(c)
                return {"canary_ok": None, "status": "carried", "carried": sorted(rt["carried"])}
        hot = bool(g.get("hot_applied_t") and g["hot_applied_t"] > g.get("reset_t", 0))
        scn = next(x for x in c["plan"]["scenarios"] if x["id"] == dec["scenario"])
        self._at_rev(c)
        can = self.lane.canary(self._expect_sha(s))
        if not can["ok"]:
            with locked(self.p):        # re-checked once after a green canary; red again, blocked until a reset
                s = self._check_live()
                red = s["game"].setdefault("canary_red", {})
                k = _red_key(c, scn["id"])
                red[k] = "stuck" if red.get(k) == "recheck" else "red"
                self._save(s)
                add_evidence(self.p, c, scn["id"], "invalid", self.lane_name, self.id, t=self.d.clock(),
                             nolock=True, why="canary red", problems=can["problems"][:5], taint=None)
            return {"canary_ok": False, "status": "invalid"}
        with locked(self.p):            # the open-state check, the transition and in_flight: one critical section
            s = self._check_live()
            cur = states(self.p).get(c["cand"], {}).get("state")
            if cur not in ("queued", "testing"):
                raise PilotRefused("%s is %s (changed since the decision): not tested" % (c["cand"], cur))
            if cur == "queued":
                set_state(self.p, c["cand"], "testing", nolock=True, pilot=self.id)
            s["in_flight"] = {"cand": c["cand"], "scenario": scn["id"], "t": self.d.clock(),
                              "id": "f-%s" % uuid.uuid4().hex[:10]}
            s["ladder_tried"] = []
            _canary_green(s)
            s["game"].get("canary_red", {}).pop(_red_key(c, scn["id"]), None)   # green and running: the blip is over
            self._save(s)
        self._ev("test_start", task=c["item"], sha=c["sha"],
                 detail={"tester": self.id, "builder": c["builder"], "cand": c["cand"], "scenario": scn["id"]})
        self._check_live()
        timed_out = False
        self._canary_ctx = {"last": self.d.clock(), "sha": self._expect_sha(s), "red": None, "runs": 0}
        try:
            rc, txt = self.d.run_scenario(scn["argv"], self.clone, self._poll,
                                          float(self.rule.get("scenario_poll_s", 5)))
        except TimeoutError as e:   # the driver already killed the proof's group: a hang is a logged result, not a crash
            rc, txt, timed_out = None, "TIMEOUT: %s" % e, True
        finally:
            mid, self._canary_ctx = self._canary_ctx, None
        self._check_live()              # S6: a pilot taken over mid-proof records nothing; the taker logged it
        self.p["logs"].mkdir(parents=True, exist_ok=True)
        log = self.p["logs"] / ("%s-%s-%s.log" % (c["cand"].replace("@", "_"), scn["id"], uuid.uuid4().hex[:6]))
        log.write_text(txt or "", encoding="utf-8")
        alive = self.d.game_running()
        after = self.lane.canary(self._expect_sha(s)) if alive else {"ok": False, "problems": ["process dead"]}
        fail_rc = scn.get("fail_rc", 1)
        taint = scn.get("taints", "uncertain")
        crash = False
        if not alive:
            status, why, crash = "invalid", "the game died during the scenario", True
        elif timed_out:
            status, why = "invalid", "the proof timed out (%s): killed, not judged" % txt
        elif not after["ok"]:
            status, why = "invalid", "canary red after the scenario"
        elif mid["red"] is not None:
            status, why = "invalid", "canary red during the scenario at t=%s (%s): the endpoints were green" % (
                mid["red"]["t"], "; ".join(mid["red"]["problems"]) or "no problem text")
        elif rc == 0:
            status, why = "pass", None
        elif rc == fail_rc and RC._crashed(txt):
            status, why = "invalid", "the proof crashed (traceback), it did not judge"
        elif rc == fail_rc:
            status, why = "fail", None
        else:
            status, why = "invalid", "proof exit %r is neither 0 nor %r" % (rc, fail_rc)
        with locked(self.p):            # ownership re-checked under the lock that guards the session
            s = self._check_live()
            ev = add_evidence(self.p, c, scn["id"], status, self.lane_name, self.id, t=self.d.clock(), why=why,
                              rc=rc, log=str(log), crash=crash, hotfix=hot and status == "pass",
                              taint=taint if status in ("fail", "invalid") else None, nolock=True)
            s["in_flight"] = None
            if status in ("pass", "fail"):      # a finished, judging test is the proof the game is usable again
                s["red_rungs"], s["red_reloads"] = 0, 0
            self._save(s)
        self._ev("test_end", task=c["item"], sha=c["sha"], verdict=status,
                 detail={"tester": self.id, "cand": c["cand"], "scenario": scn["id"], "why": why})
        if crash:
            self._crashed(c)
        self._resolve(c)
        return {"canary_ok": bool(after["ok"]) if alive else None, "status": status, "evidence": ev}

    def _crashed(self, c):
        n = sum(1 for e in evidence(self.p) if e["item"] == c["item"] and e.get("crash"))
        if n >= int(self.rule.get("max_item_crashes", 2)):
            set_state(self.p, c["cand"], "quarantined", why="%d crashes on %s (M5)" % (n, c["item"]),
                      item_parked=c["item"])
            self._close_item(c, "quarantined", "%d crashes on %s (M5)" % (n, c["item"]))

    def _close_item(self, c, state, why, nolock: bool = False):
        """A quarantine or a live-fail park is of the ITEM (M5, L10): its other open candidates close with it. The
        item_parked record is written first, so an enqueue racing this sweep is refused or already in the queue."""
        st = states(self.p)
        for o in candidates(self.p):
            if o["item"] == c["item"] and o["cand"] != c["cand"] and \
                    st.get(o["cand"], {}).get("state") in ("queued", "testing"):
                set_state(self.p, o["cand"], state, nolock=nolock, only_from=("queued", "testing"), by=c["cand"],
                          item_parked=c["item"], why="the item is %s with %s: %s" % (state, c["cand"], why))

    def _resolve(self, c, nolock: bool = False):
        """A candidate resolves when every scenario has a counted, non-hot-fixed result at its fingerprint."""
        if states(self.p).get(c["cand"], {}).get("state") in TERMINAL:
            return
        have = scenario_status(self.p, c)
        ids = [x["id"] for x in c["plan"]["scenarios"]]
        if any(have.get(i, {}).get("status") == "fail" for i in ids):
            fails = len({e["cand"] for e in evidence(self.p) if e["item"] == c["item"] and e["status"] == "fail"})
            if fails >= int(self.rule.get("max_live_fails", 3)):
                set_state(self.p, c["cand"], "parked", nolock=nolock, why="%d live failures (L10)" % fails,
                          item_parked=c["item"])
                self._close_item(c, "parked", "%d live failures (L10)" % fails, nolock=nolock)
                return
            s = self._sess()
            valuable, blocked = _pending(self.p, c, s)
            restorable = bool(blocked) and bool(c["plan"].get("fixture_save")) and \
                "reload_save" not in (s.get("ladder_tried") or [])
            if not valuable and not restorable:   # a failed candidate keeps its other scenarios while any can run
                set_state(self.p, c["cand"], "resolved", nolock=nolock, verdict="fail",
                          **({"unrun_blocked": blocked} if blocked else {}))
        elif all(have.get(i, {}).get("status") in COUNTED and not have[i].get("hotfix") for i in ids):
            set_state(self.p, c["cand"], "resolved", nolock=nolock, verdict="pass")


# ---------------------------------------------------------------- the real driver (live only)

class PilotDriver(RC.RunnerDriver):
    """RunnerDriver plus the pilot's acts. run_scenario polls `poll` (the S6 ownership check) while the proof runs."""

    LIMIT_S = 1800

    def run_scenario(self, argv, clone, poll, poll_s):
        try:
            proc = subprocess.Popen(list(argv), cwd=clone or str(L.REPO), stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace",
                                    start_new_session=True)     # its own group: a kill reaches every child too
        except OSError as e:
            return 99, "%s: %s" % (type(e).__name__, e)
        t0 = time.time()
        while True:
            try:
                out, _ = proc.communicate(timeout=poll_s)
                return proc.returncode, out
            except subprocess.TimeoutExpired:
                pass
            try:
                poll()
                if time.time() - t0 > self.LIMIT_S:
                    raise TimeoutError("scenario over %g s" % self.LIMIT_S)
            except BaseException:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except OSError:
                    proc.kill()
                try:
                    proc.communicate(timeout=10)    # a grandchild holding the pipe cannot stall the kill
                except subprocess.TimeoutExpired:
                    pass
                raise

    def reconnect(self):
        rc, out = L._sh(["python3", str(L.RIMFLOW), "bridge", "who"], timeout=60)
        return rc == 0, out

    def restage(self):
        return False, "restage is not wired in the real driver (no scenario declares a restage yet)"


# ---------------------------------------------------------------- CLI

def _status(p, lane):
    st = states(p)
    out = {"queue": [{"cand": c["cand"], "class": c["class"], "kind": c["kind"],
                      "state": st.get(c["cand"], {}).get("state")} for c in candidates(p)]}
    for ln in ([lane] if lane else list(L.LANES)):
        out[ln] = read_session(p, ln)
    return out


def _aborted(res) -> bool:
    """True when a step's result is the abort record (or the retired pilot's abort stub)."""
    return isinstance(res, dict) and (res.get("kind") == "abort" or "abort" in res)


def run_pass_guarded(pilot, max_steps: int = 50) -> list[dict]:
    """The pass with one try/finally: whatever escapes, his list is restored and the bridge released."""
    try:
        return pilot.run_pass(max_steps)
    except BaseException as e:
        if not pilot.retired:
            try:
                pilot.abort(e)
            except Exception:  # noqa: BLE001 - the abort logs its own failures; the original error still raises
                pass
        raise


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("enqueue")
    e.add_argument("--item", required=True)
    e.add_argument("--sha", required=True)
    e.add_argument("--builder", required=True)
    e.add_argument("--plan", required=True)
    e.add_argument("--profile", default="minimal")
    e.add_argument("--tier")
    e.add_argument("--mod", action="append", default=[])
    e.add_argument("--has-dll", action="store_true")
    e.add_argument("--parent")
    e.add_argument("--changed-file", action="append")
    e.add_argument("--changed-def", action="append")
    e.add_argument("--kind", default="build")
    e.add_argument("--fault")
    e.add_argument("--review")
    e.add_argument("--fix-class")
    ps = sub.add_parser("pass")
    ps.add_argument("--lane", required=True)
    ps.add_argument("--pilot", required=True)
    ps.add_argument("--clone")
    ps.add_argument("--close", action="store_true")
    ps.add_argument("--takeover-dead", action="store_true")
    ps.add_argument("--max-steps", type=int, default=50)
    d = sub.add_parser("decide")
    d.add_argument("--lane", required=True)
    t = sub.add_parser("taint")
    t.add_argument("--cand", required=True)
    t.add_argument("--scenario", required=True)
    t.add_argument("--names", required=True)
    t.add_argument("--pilot", default="pilot-note")
    s = sub.add_parser("status")
    s.add_argument("--lane")
    a = ap.parse_args(argv)
    p = ppaths()
    if a.cmd == "enqueue":
        plan = json.loads(Path(a.plan).read_text(encoding="utf-8"))
        rec = enqueue(p, a.item, a.sha, a.builder, plan, a.mod, a.has_dll, a.profile, a.tier, a.parent,
                      a.changed_file, a.changed_def, a.kind, a.fault, a.review, a.fix_class)
        print(json.dumps({"cand": rec["cand"], "class": rec["class"], "fingerprint": rec["fingerprint"]}))
        return 0
    if a.cmd == "status":
        print(json.dumps(_status(p, a.lane), indent=1, default=str))
        return 0
    if a.cmd == "decide":
        dr = PilotDriver()
        sess = read_session(p, a.lane)
        facts = {"process_alive": bool(dr.game_running()), "canary_ok": None}
        print(json.dumps(decide(p, a.lane, sess, facts, load_rule(), dr.clock()), indent=1, default=str))
        return 0
    if a.cmd == "taint":
        c = cand_by_id(p).get(a.cand)
        if c is None:
            raise SystemExit("unknown candidate %s" % a.cand)
        names = "uncertain" if a.names == "uncertain" else [x for x in a.names.split(",") if x]
        try:
            taint_note(p, c, a.scenario, names, a.pilot)
        except PilotRefused as e:
            raise SystemExit(str(e))
        return 0
    pilot = Pilot(a.lane, PilotDriver(), a.pilot, clone=a.clone)
    pilot.wake(takeover_dead=a.takeover_dead)
    steps = run_pass_guarded(pilot, a.max_steps)
    for r in steps:
        dec = r["decision"]
        print(json.dumps({k: dec.get(k) for k in ("action", "rule", "cand", "scenario", "rung", "why")},
                         default=str))
    ab = next((r.get("result") for r in steps if _aborted(r.get("result"))), None)
    if ab:
        print("PASS ABORTED: %s (abort decision %s)" % (ab.get("why") or ab.get("abort"), ab.get("id")),
              file=sys.stderr)
        return 1
    if not pilot.retired:
        if a.close:
            pilot.close()
        else:
            pilot.handoff()
    return 0


if __name__ == "__main__":
    sys.exit(main())
