"""testq/pipeline_admit.py - what SteveDesktop's test queue refuses, and the pipeline record readers.

The owner, 2026-11-17 about 11:00 AM PST: "Drop 11-14 limits, old rule. Clear its limitations. We are remeasuring it for
a brand new pipeline." His card of 2026-11-14 (spec question 18c, "Pipeline tests only") is dropped (item
RIMMANDRAKE_DROP_STEVEDESKTOP_PIPELINE_ONLY_LIMIT): any mod's token-free test, proof chain, --full sweep or --item
selection may be submitted and filled whatever its pipeline stage.

  refusal(mod, selector, requested_by) -> None (admitted) or a refusal record, checked by testq submit before anything
  else, and by fill, sweep and the fault-window rerun (fault_monitor.rerun_job).

The host work switch (rimflow/host_work_switch.py) refuses a test job of a mod that is not live on SteveDesktop; a live
mod's job passes (owner, by card 2026-11-25 11:02 PM PST; live_mod, switch_refusal).

One refusal stays: a mod on the owner's hold (src/RimMandrake/rimflow/mod_owner_hold.json, his 2026-11-16 hold on the
biome mods other than Pyrelands; he or the Conductor lifts it, owner 2026-11-19). An unreadable hold list refuses every test: nothing is queued that
cannot be proved unheld. Ops jobs are not tests and are never refused: the requesters in OPS_REQUESTERS (the
brake-release canary, the steward's repair wake). The machine-safety brakes (fault_monitor, the outage pause,
brake_release) live in their own modules and are not this file's.

standing() / qualifying() only READ the pipeline record (design/concepts/<Mod>/version/stage_record.json, VERSION.json
and the `testq` blocks of test_table.json's stage-6 entries): testq_blocks.py and coverage.pipeline_mods use them to find
the chains a locked bar names. They admit and refuse nothing.
"""
import json
import os
import sys

PAST_BLIND = ("in_game", "pre_human", "his_walk", "passed")    # maturation.STAGES after blind_challenge
BAR_STAGES = ("6",)                                            # a test-table entry the game decides (spec Stage 6)
KINDS = ("chains", "rows", "proofs")
OPS_REQUESTERS = ("Operations.canary", "BENCH.steward-wake")   # brake_release.BY; steward.py's repair wake
CLAUSE = "owner_hold"
CRITERION = ("a mod on the owner's hold (rimflow/mod_owner_hold.json) is not tested on SteveDesktop until he or the "
             "Conductor lifts it (owner 2026-11-16, 2026-11-19)")


def repo_root():
    return os.environ.get("TESTQ_PIPELINE_ROOT") or os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))


def _moh():
    """rimflow/mod_owner_hold.py, loaded by its path. Never put rimflow on sys.path here: rimflow has its own
    repeat_guard.py, and testq's `import repeat_guard` then got it (no .hold), so the repeat guard failed open."""
    m = sys.modules.get("mod_owner_hold")
    if m is not None:
        return m
    import importlib.util
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "rimflow", "mod_owner_hold.py")
    spec = importlib.util.spec_from_file_location("mod_owner_hold", os.path.abspath(p))
    m = importlib.util.module_from_spec(spec)
    sys.modules["mod_owner_hold"] = m
    spec.loader.exec_module(m)
    return m


def _hws():
    """rimflow/host_work_switch.py, loaded by its path (the same rule as _moh: rimflow never goes on sys.path here)."""
    m = sys.modules.get("host_work_switch")
    if m is not None:
        return m
    import importlib.util
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "rimflow", "host_work_switch.py")
    spec = importlib.util.spec_from_file_location("host_work_switch", os.path.abspath(p))
    m = importlib.util.module_from_spec(spec)
    sys.modules["host_work_switch"] = m
    spec.loader.exec_module(m)
    return m


def steve_switched():
    """-> the text of the host work switch on SteveDesktop (Claude work is pipeline improvements only), or None."""
    return _hws().switched("SteveDesktop")


def _control():
    """rimflow/control.py, loaded by its path under the name `control` (mod_owner_hold.load imports it by that name)."""
    m = sys.modules.get("control")
    if m is not None:
        return m
    import importlib.util
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "rimflow", "control.py")
    spec = importlib.util.spec_from_file_location("control", os.path.abspath(p))
    m = importlib.util.module_from_spec(spec)
    sys.modules["control"] = m
    spec.loader.exec_module(m)
    return m


def live_mod(mod):
    """-> (True, None) when MOD is live, else (False, why). A live mod is in the Maturation Pipeline (the advancing list of
    rimflow/maturation_dispatch.json, as `./pipe show` lists it), is not on the owner's hold and is not switched off
    (`pipe off`): a mod `./pipe show` reads ON. Owner, by card 2026-11-25 11:02 PM PST: SteveDesktop's games take the test
    jobs of live mods. A state that cannot be read is not live, and the why says `could not look` with the cause."""
    if not (isinstance(mod, str) and mod.strip()):
        return False, "could not look: the job names no mod"
    moh = _moh()
    try:
        h = held_by_owner(mod)
    except moh.Unreadable as e:
        return False, "could not look: the owner-hold list or the control store cannot be read (%s)" % e
    if h:
        return False, "%s is not live: %s" % (mod, moh.status(h))
    try:
        listed = _control().known_mods(advancing_only=True)
    except Exception as e:      # noqa: BLE001 - a control.py that cannot load is could-not-look, never "not in the pipeline"
        return False, "could not look: the pipeline's mod list cannot be read (%s: %s)" % (type(e).__name__, e)
    if not listed:
        return False, "could not look: the pipeline's advancing list (rimflow/maturation_dispatch.json) is empty or unreadable"
    if _control().key(mod) not in listed:
        return False, "%s is not live: it is not in the Maturation Pipeline's advancing list" % mod
    return True, None


def switch_text_for(mod):
    """-> why SteveDesktop's switch keeps test jobs of MOD off its games, or None when MOD's tests are admitted: no switch,
    or a switch with MOD live. An unreadable switch is its own text (could not look): nothing is admitted that cannot be shown allowed."""
    sw = steve_switched()
    if not sw:
        return None
    if sw.startswith(_hws().UNREADABLE):
        return sw
    live, why = live_mod(mod)
    return None if live else "%s; %s" % (sw, why)


def switch_refusal(job):
    """-> a refusal record when JOB is a test job of a mod that is not live, bound for the SteveDesktop lane while
    SteveDesktop is switched (rimflow/host_work_switch.py), else None. A live mod's job passes: a commission, a fix, a guard
    (a pipeline run's or the idle filler's) and a stage-6 checks job. Also passing: a --proofs job (live-proof lines of a
    pipeline item), an Ops job, the Archmagi lane. A Claude run that builds or fixes a mod is not this file's: list_dispatch.switch_refuses."""
    job = job or {}
    if job.get("requested_by") in OPS_REQUESTERS or str(job.get("lane") or "stevedesktop") == "archmagi":
        return None     # lane "any" can land on SteveDesktop, so it is judged like the SteveDesktop lane
    if ((job.get("selector") or {}).get("proofs")):
        return None
    why = switch_text_for(job.get("mod"))
    if not why:
        return None
    r = _refuse(job.get("mod"), "test job of a mod that is not live, on SteveDesktop: " + why,
                "the switch is lifted or %s is live in the pipeline" % job.get("mod"),
                "submit it to the Archmagi lane (--lane archmagi), or as pipeline proof lines (--proofs)", "held")
    r["clause"] = "host_work_switch"
    return r


def _holds():
    """-> mod_owner_hold.load() (RM_OWNER_HOLD_FILE or the repo's list); raises mod_owner_hold.Unreadable."""
    return _moh().load()


def held_by_owner(mod):
    """-> the owner's hold on MOD (any path spelling), or None. Raises mod_owner_hold.Unreadable."""
    return _holds().get(_moh().key(mod))


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
    """-> (entry or None, why not): entry = {"version", "stage", "chains", "rows", "proofs"} when MOD's locked version
    stands past the blind challenge. A reader of the record; it decides no admission."""
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


def _refuse(mod, observed, would_pass, fix, why):
    r = {"clause": CLAUSE, "criterion": CRITERION, "mod": mod, "observed": observed, "would_pass": would_pass,
         "smallest_fix": {"what": fix, "attainable": "owner" if why == "held" else "yes", "cost": "owner"
                          if why == "held" else "edit"}, "criterion_verdict": "sound",
         "criterion_why": "the owner's hold of 2026-11-16 (design/RimMandrake/standing_rulings.md, Owner hold)"}
    r["text"] = "%s; it runs once %s (smallest fix: %s)" % (observed, would_pass, fix)
    return r


def raid_refusal(mod, sel):
    """-> a refusal record when every chain that SEL names is a paused raid chain (rimflow/raid_pause.py), else None."""
    names = (sel or {}).get("chains") if isinstance(sel, dict) else None
    if not names:
        return None
    d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "rimflow")
    if d not in sys.path:
        sys.path.append(d)
    import raid_pause as RP
    what = [RP.chain_paused(mod, c) for c in names]
    if not all(what):
        return None
    return _refuse(mod, "%s: each chain named stages a raid (%s)" % (RP.WORD, "; ".join(what)),
                   "the raid pause is lifted (%s)" % RP.switch()["why"], "queue a chain that stages no raid", "raid")


def refusal(mod, sel, by, root=None):
    """-> None when the job may be queued, else a refusal record (fields of the refusal contract, plus `text`).
    SEL and ROOT are accepted for the callers' signature; no selection and no pipeline stage is refused."""
    if by in OPS_REQUESTERS:
        return None
    moh = _moh()
    raid = raid_refusal(mod, sel)
    if raid:
        return raid
    try:
        h = held_by_owner(mod)
    except moh.Unreadable as e:
        return _refuse(mod, "the owner-hold list cannot be read (%s)" % e, "the hold list reads",
                       "repair src/RimMandrake/rimflow/mod_owner_hold.json", "unreadable")
    if h:
        return _refuse(mod, moh.status(h), "the hold on %s is lifted" % h["mod"],
                       "he or the Conductor lifts it: %s" % (moh.LIFT % h["mod"]), "held")
    return None
