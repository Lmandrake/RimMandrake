"""testq/repeat_guard.py - no second run of a selection whose last run the TEST or the DELIVERY machinery killed, until
something it depends on changed (RIMMANDRAKE_STOP_STEVEDESKTOP_INVALID_RUNS_REPEATING_UNFIXED).

Owner, 2026-11-14: "So much waste. And it just keeps happening." Of 85 INVALID jobs 2026-11-06..14, 29 were the same
mod and selection run again with the mod's source and the harness unchanged, and 16 of those died again (census:
D:\\ClaudeWork\\rimmandrake\\conductor\\steve_invalids_20261114). The repair-item hold (gaps.harness_last) never formed:
ingest counted every run inside a fault window as ENVIRONMENT and filed nothing, and the windows have been back to back
since 2026-11-08.

  hold(mod, chains, recs, ...) -> {chain: reason}

A chain is HELD when the latest finished job of MOD that asked for it (by --chains, or --full) is INVALID and
  - its class (invalid_class.classify) is TEST or DELIVERY, or it is UNKNOWN for the second job in a row; and
  - none of the paths that class depends on changed between that job's source sha and origin/main (RELEVANT); and
  - no repair item for its cause (retest.repair_base of retest.job_cause) has closed since: a named fix landed.
A GAME/machine INVALID never holds: the lane brake (testq.brake_tail) and the periodic reboot own those, and 13 of the
29 unchanged repeats came back DONE. A sha this checkout cannot read, or a git error, holds nothing and says so
(blind): a hold nobody can explain would be a silent stop. The reason names what lets the chain run again.
"""
import os
import subprocess

import invalid_class as IC
import retest as R

HARNESS = ("src/RimMandrake/Utils/modcheck", "src/RimMandrake/Utils/testq", "infrastructure/stevedesktop",
           "src/RimMandrake/contracts", "src/RimMandrake/Utils/deploy_custom_mods.py",
           "src/RimMandrake/Utils/modset_builder.py")
TERMINAL = ("done", "dropped", "superseded")
TIERS = ("RimMandrake", "RimStarWars", "RimUtinni")
UNKNOWN_RUN = 2     # UNKNOWN INVALIDs in a row, at an unchanged fingerprint, before the chain is held


def repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))


def git(*args):
    """-> stdout stripped, or None on any failure (this checkout)."""
    try:
        r = subprocess.run(["git", "-C", repo_root()] + list(args), capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout.strip() if r.returncode == 0 else None


def relevant(mod, klass, root=None):
    """-> the repo paths whose change can cure a KLASS fault of MOD: the mod's own folder and validation walk always;
    a DELIVERY or UNKNOWN fault adds the delivery harness, a TEST fault the modcheck runner."""
    root = root or repo_root()
    own = []
    for t in TIERS:
        if os.path.isdir(os.path.join(root, "src", t, mod)):
            own.append("src/%s/%s" % (t, mod))
        own.append("design/validation_walks/%s/%s.md" % (t, mod))
    if klass == IC.TEST:
        return own + ["src/RimMandrake/Utils/modcheck"]
    return own + list(HARNESS)


def changed(sha, paths, g=git):
    """-> (True/False, what): did any of PATHS differ between SHA and origin/main; (None, why) when unknown."""
    if not sha or g("cat-file", "-e", "%s^{commit}" % sha) is None:
        return None, "source sha %s is not readable here" % sha
    head = g("rev-parse", "origin/main")
    if not head:
        return None, "no origin/main"
    out = g("diff", "--name-only", sha, head, "--", *paths)
    if out is None:
        return None, "git diff failed"
    moved = [f for f in out.split("\n") if f.strip() and not inert(f)]
    return bool(moved), (moved[0] if moved else "")


def inert(path):
    """A changed file that cannot cure a run: a selftest, or prose other than a validation walk (the walk holds the
    must-show lines modcheck refuses on)."""
    base = os.path.basename(path)
    return base.startswith("selftest") or (path.endswith(".md") and not path.startswith("design/validation_walks/"))


def _asked(job, chain):
    sel = (job or {}).get("selector") or {}
    return bool(sel.get("full")) or chain in (sel.get("chains") or [])


def _closed_since(items, cause, t):
    """True when a repair item for CAUSE exists and every generation of it is terminal: the fix was named and closed.
    (The ledger does not give a close time here; an item filed by this very INVALID and closed is a fix after it.)"""
    if not cause or items is None:
        return False
    names = R._generations(items, R.repair_base(cause))
    return bool(names) and all(getattr(items[n], "state", None) in TERMINAL for n in names)


def hold(mod, chains, recs, items=None, g=git, root=None):
    """-> {chain: reason} for the chains of CHAINS (None: every chain any job of MOD asked for) that must not run
    again yet. RECS: testq done records. ITEMS: the ledger's items (id -> .state), or None when unreadable."""
    mine = []
    for rec in recs or []:
        job, res = (rec or {}).get("job") or {}, (rec or {}).get("result") or {}
        if job.get("mod") != mod or not res.get("outcome"):
            continue
        t = IC.finished_of(rec)
        if t is not None:
            mine.append((t, job.get("id") or "", job, res))
    mine.sort(key=lambda x: x[:2])
    if chains is None:
        chains = sorted({c for _, _, j, _ in mine for c in ((j.get("selector") or {}).get("chains") or [])})
    memo, out = {}, {}
    for c in chains:
        runs = [(t, j, r) for t, _, j, r in mine if _asked(j, c)]
        if not runs or runs[-1][2].get("outcome") != "INVALID":
            continue
        t, job, res = runs[-1]
        klass, key = IC.classify(res)
        if klass == IC.GAME:
            continue
        since = job.get("source_sha")
        if klass == IC.UNKNOWN:
            tail = []
            for _, j, r in reversed(runs):
                if r.get("outcome") != "INVALID" or IC.classify(r)[0] != IC.UNKNOWN:
                    break
                tail.append(j)
            if len(tail) < UNKNOWN_RUN:
                continue
            since = tail[UNKNOWN_RUN - 1].get("source_sha")     # nothing moved from the older death to origin/main
        cause = R.job_cause(res)
        if _closed_since(items, cause, t):
            continue
        k = (since, klass)
        if k not in memo:
            memo[k] = changed(since, relevant(mod, klass, root), g)
        diff, what = memo[k]
        if diff is None:
            continue        # blind: never a silent hold
        if diff:
            continue
        name = R.repair_base(cause) if cause else None
        out[c] = ("%s's last run %s died INVALID (%s%s) and nothing it depends on changed since %s; it runs again "
                  "after a commit to %s, or once %s closes" % (
                      c, job.get("id"), klass, ": " + key if key else ", %d in a row" % UNKNOWN_RUN,
                      since, "src/<tier>/%s or its walk%s" % (
                          mod, ", modcheck" if klass == IC.TEST else ", the delivery harness"),
                      name or "its repair item"))
    return out
