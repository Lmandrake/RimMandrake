#!/usr/bin/env python3
"""preflight.py - refuse (or fix) what would make a testq job INVALID, before it takes the game.

RIMMANDRAKE_TESTQ_PREFLIGHT_REFUSE_BEFORE_THE_GAME. Of 86 jobs since 2026-11-06, 26 ended INVALID and made no rows. The worker's
cmd_start runs `check(job, ...)` after the source_sha test and before it spawns an attempt: a refusal is a finished
attempt, outcome REFUSED / cause PREFLIGHT, whose note names the check and the reason; no deploy, no load, no guard.

Only causes that HAPPENED have a check (the census is in design/RimMandrake/testq_preflight_2026-11-12.md):

  swap_marker   10 of 26: a stale ModsConfig.swap-active.json made `modset_builder --tier T --apply` refuse
                (marker's before-copy gone, or the live list neither its tier list nor its before-copy). The check runs
                modset_builder's own repair_game_reset + take_before_copy on a COPY of the marker, before-copy and live
                list, so it can never disagree with the real swap. On a refusal the marker is moved aside to
                `<marker>.stale-<UTC>` (the hand fix of 2026-11-12) and the move is logged in the result note; a fix
                that does not clear the refusal is a PREFLIGHT refusal. TESTQ_PREFLIGHT_MARKER_FIX=0 only reports.
  dll_current   a job whose mod's committed DLL no longer matches its committed C# (dll_source_stamp.py MISMATCH) runs
                the old code and reads as the mod's fault. Read from git blobs at the job's source_sha.
  proof_lines   a proofs job whose clause has no `live-proof X:` line at source_sha could only read UNMEASURED after a
                whole load (run_proofs). None happened as INVALID yet; the check is one blob read.

Opt-in (never the cause of an INVALID, and 10 s each): TESTQ_PREFLIGHT_TIER_BUILD=1 runs `modset_builder --tier T`
(its plan, no --apply) and refuses on an unknown tier or a REFUSING line - not on NOT INSTALLED, which the deploy that
follows may cure.

TESTQ_PREFLIGHT=0 turns the whole thing off. Every check that cannot read what it needs says so in `skipped` and lets the
job through: a preflight must never refuse on its own blindness.
"""
import datetime
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))


def load_modset_builder(runner):
    """-> the runner's modset_builder module, or None. Importing runs no scan (main() does)."""
    utils = os.path.join(runner, "src", "RimMandrake", "Utils")
    if not os.path.isfile(os.path.join(utils, "modset_builder.py")):
        return None
    if utils not in sys.path:
        sys.path.insert(0, utils)
    try:
        import modset_builder as MB
        return MB
    except Exception:       # noqa: BLE001 - an unimportable builder is a skipped check, not a refusal
        return None


def swap_refusal(MB, config, backups, tier):
    """-> the RestoreRefused text modset_builder.take_before_copy WOULD raise for this tier, else None.
    Runs the real functions on a temp copy of the marker, the before-copy it names and the live list."""
    marker = os.path.join(backups, MB.SWAP_MARKER)
    if not os.path.exists(marker) or not os.path.exists(config):
        return None
    tmp = tempfile.mkdtemp(prefix="preflight_swap_")
    try:
        tb = os.path.join(tmp, "backups")
        os.makedirs(tb)
        shutil.copy2(marker, os.path.join(tb, MB.SWAP_MARKER))
        try:
            with open(marker) as fh:
                before = json.load(fh).get("before")
        except (ValueError, OSError, AttributeError):
            before = None
        if isinstance(before, str) and os.path.exists(os.path.join(backups, os.path.basename(before))):
            shutil.copy2(os.path.join(backups, os.path.basename(before)), os.path.join(tb, os.path.basename(before)))
        tc = os.path.join(tmp, "ModsConfig.xml")
        shutil.copy2(config, tc)
        try:
            MB.take_before_copy(tc, tb, tier)
            return None
        except MB.RestoreRefused as e:
            return str(e).replace(tb, backups)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def move_marker_aside(MB, backups, now=None):
    """-> the new path of the stale marker (kept for the record, never deleted)."""
    marker = os.path.join(backups, MB.SWAP_MARKER)
    stamp = (now or datetime.datetime.now(datetime.timezone.utc)).strftime("%Y%m%dT%H%M%SZ")
    dst = "%s.stale-%s" % (marker, stamp)
    os.replace(marker, dst)
    return dst


def check_swap_marker(job, MB, config, backups, fix=True):
    """-> (refusal or None, fix note or None). Tier jobs only: the others never swap the list."""
    import schema as S
    tier = S.tier_of(job)
    if not tier or MB is None:
        return None, None
    why = swap_refusal(MB, config, backups, tier)
    if why is None:
        return None, None
    if not fix:
        return "swap marker blocks the tier switch: " + why[-300:], None
    moved = move_marker_aside(MB, backups)
    note = "stale swap marker moved aside to %s (it blocked tier %s: %s)" % (moved, tier, why[:160])
    again = swap_refusal(MB, config, backups, tier)
    if again is not None:
        return "swap marker moved aside but the tier switch is still refused: " + again[-300:], note
    return None, note


def _stamp_dirs(job, src_root):
    """-> the src/<tier>/<mod> directories (repo-relative) of the mods this job deploys."""
    import schema as S
    known, folded, composed = S.deploy_catalog(src_root)
    mods = ([] if S.is_proofs(job) else [job["mod"]]) + list(job.get("deploy") or [])
    out = []
    for m in mods:
        if m in folded or m in composed:
            continue
        for t in S._SRC_TIERS:
            if os.path.isdir(os.path.join(src_root, t, m)):
                out.append("src/%s/%s" % (t, m))
                break
    return out


def check_dll_current(job, clone):
    """-> (refusal or None, skipped reason or None): every *.dll.srchash under the job's mod dirs, at source_sha."""
    sys.path.insert(0, os.path.join(clone, "src", "RimMandrake", "Utils"))
    try:
        import dll_source_stamp as D
    except Exception as e:      # noqa: BLE001
        return None, "dll_source_stamp not importable (%s)" % type(e).__name__
    finally:
        sys.path.pop(0)
    dirs = _stamp_dirs(job, os.path.join(clone, "src"))
    rev = job["source_sha"]
    cat = D.BatchCat(clone)
    bad = []
    try:
        for d in dirs:
            for stamp in D.ls_tree(rev, d, clone):
                if not stamp.endswith(".dll.srchash"):
                    continue
                r = D.recompute_stamp(cat, rev, stamp, clone)
                if r.status in ("MISMATCH", "CSPROJ_MISSING", "MALFORMED"):
                    bad.append("%s %s: %s" % (r.status, stamp[:-len(".srchash")], "; ".join(r.detail[:2])))
    finally:
        cat.close()
    if bad:
        return "DLL older than its source at %s: %s" % (rev[:10], " | ".join(bad)[:400]), None
    return None, None


def check_proof_lines(job, clone, proofs_rel="infrastructure/state/live_proofs"):
    """-> refusal or None: each proofs clause must have its `live-proof X:` line in the item's file at source_sha."""
    import schema as S
    if not S.is_proofs(job):
        return None
    rel = "%s/%s.txt" % (proofs_rel, job["item"])
    r = subprocess.run(["git", "-C", clone, "show", "%s:%s" % (job["source_sha"], rel)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return "no proofs file %s at %s" % (rel, job["source_sha"][:10])
    lines = S.proof_lines(r.stdout)
    miss = [c for c in job["selector"]["proofs"] if c not in lines]
    return ("no `live-proof %s:` line in %s at %s" % (", ".join(miss), rel, job["source_sha"][:10])) if miss else None


def check_tier_build(job, runner):
    import schema as S
    tier = S.tier_of(job)
    if not tier:
        return None
    r = subprocess.run([sys.executable, os.path.join(runner, "src", "RimMandrake", "Utils", "modset_builder.py"),
                        "--tier", tier], cwd=runner, capture_output=True, text=True, timeout=180)
    text = (r.stdout or "") + (r.stderr or "")
    if "REFUSING tier" in text or (r.returncode != 0 and "NOT INSTALLED" not in text):
        return "modset_builder --tier %s (plan) failed, exit %d: %s" % (tier, r.returncode, text.strip()[-300:])
    return None


def check(job, runner, clone=None, config=None, backups=None, env=None):
    """-> {"refused": [(check, reason)], "fixed": [note], "skipped": [note]}. Never raises: a crashed check is skipped."""
    env = os.environ if env is None else env
    res = {"refused": [], "fixed": [], "skipped": []}
    if env.get("TESTQ_PREFLIGHT") == "0":
        res["skipped"].append("TESTQ_PREFLIGHT=0")
        return res
    clone = clone or runner

    def run(name, fn):
        try:
            return fn()
        except Exception as e:      # noqa: BLE001
            res["skipped"].append("%s: %s: %s" % (name, type(e).__name__, str(e)[:120]))
            return None

    import schema as S
    if S.tier_of(job):
        MB = load_modset_builder(runner)
        if MB is None:
            res["skipped"].append("swap_marker: modset_builder not importable")
        else:
            cfg = config or MB.CONFIG
            bk = backups or MB.BACKUPS
            r = run("swap_marker", lambda: check_swap_marker(job, MB, cfg, bk, env.get("TESTQ_PREFLIGHT_MARKER_FIX") != "0"))
            if r:
                if r[0]:
                    res["refused"].append(("swap_marker", r[0]))
                if r[1]:
                    res["fixed"].append(r[1])
        if env.get("TESTQ_PREFLIGHT_TIER_BUILD") == "1":
            why = run("tier_build", lambda: check_tier_build(job, runner))
            if why:
                res["refused"].append(("tier_build", why))
    r = run("dll_current", lambda: check_dll_current(job, clone))
    if r:
        if r[0]:
            res["refused"].append(("dll_current", r[0]))
        if r[1]:
            res["skipped"].append("dll_current: " + r[1])
    why = run("proof_lines", lambda: check_proof_lines(job, clone))
    if why:
        res["refused"].append(("proof_lines", why))
    return res


def note_of(res):
    """One line for the result's note."""
    parts = ["PREFLIGHT refused: " + "; ".join("%s: %s" % x for x in res["refused"])] if res["refused"] else []
    parts += res["fixed"]
    return " | ".join(parts)[-390:]


if __name__ == "__main__":
    j = json.load(open(sys.argv[1]))
    runner = os.path.abspath(os.path.join(HERE, "..", ".."))
    print(json.dumps(check(j, runner), indent=1))
