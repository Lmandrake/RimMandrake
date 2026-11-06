#!/usr/bin/env python3
"""The generalization check's cadence and its revert (design/RimMandrake/daily_agent_improvement_2026-11-02.md 4.2, 4.3;
item AGENT_IMPROVE_WIRE_GENCHECK_HAND_RUN_ONLY). agent_improve.run_pass calls run_due after an --apply pass.

Cadence, read from the change records, so a crashed check or a refused publish simply leaves the check due (a kill in
the moment between writing the entry and publishing it leaves a dirty record, reported as a row when next due):
    L0   nothing (the design's cost bound: the check runs only at L1 and L2)
    L1   every fifth change of a target (reverts are not changes here) with no measured check yet
    L2   every change is gated before apply (agent_improve.general_gate); nothing more here
    L1, L2  weekly per target, its newest version, when no version of it was measured in the last WEEK_DAYS
At most MAX_CHECKS a pass; the longest since an attempt go first, ties rotating daily, so a check that keeps failing
never starves the others; the rest stay due. An `unmeasured` entry is no check. A revert version is never checked: judged
against the text it undid, a verdict of harm would revert the revert. A refused revert is reported on its row and comes
round again with the target's next weekly check.

A check is published as evidence plus the appended entry on the change record. keep=False publishes a revert version:
a NEW version (tag, change record with revert_of) whose diff undoes the old one's; nothing is deleted. no_signal has
keep=None and reverts nothing. Only a fresh verdict from this pass is enacted, never an entry already on a record: one
written before the noise floor (AGENT_IMPROVE_HARDEN_NOISE_CALLED_OVERFIT) had none.
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import agent_improve as A  # noqa: E402
import agent_improve_general as G  # noqa: E402
import delegated_digest as D  # noqa: E402  (agent_improve put rimflow on the path)

ITEM = "AGENT_IMPROVE_WIRE_GENCHECK_HAND_RUN_ONLY"
FIFTH, WEEK_DAYS, MAX_CHECKS = 5, 7, 3


def records(changes_dir=None):
    """-> {target: {version: record}}; the file name is the identity (<target>_v<N>.json), as everywhere else."""
    out = {}
    d = changes_dir or A.CHANGES
    for name in sorted(os.listdir(d)) if os.path.isdir(d) else ():
        if name.endswith(".json"):
            try:
                t, n = name[:-len(".json")].rsplit("_v", 1)
                rec = json.load(open(os.path.join(d, name), encoding="utf-8"))
                if isinstance(rec, dict):
                    out.setdefault(t, {})[int(n)] = rec
            except (OSError, ValueError):
                continue
    return out


def _times(rec, measured_only):
    ts = [A.epoch(g.get("at")) for g in rec.get("generalization") or ()
          if not measured_only or g.get("verdict") != "unmeasured"]
    return [t for t in ts if t is not None]


def due_checks(level, now=None, changes_dir=None):
    """-> [{target, version, why}] due at this level, longest since an attempt first (see the module docstring)."""
    if not level:
        return []
    now = time.time() if now is None else now
    due, recs = {}, records(changes_dir)
    for t, versions in recs.items():
        if not A.resolve_target(t):
            continue
        changes = sorted(n for n, rec in versions.items() if not rec.get("revert_of"))
        for k, n in enumerate(changes, 1):
            rec = versions[n]
            if level == 1 and k % FIFTH == 0 and not rec.get("reverted_by") and not _times(rec, True):
                due[(t, n)] = "every fifth change"
        newest = max(versions)
        if not versions[newest].get("revert_of") and not versions[newest].get("reverted_by"):
            seen = [x for rec in versions.values() for x in _times(rec, True)]
            if not seen or now // 86400 - max(seen) // 86400 >= WEEK_DAYS:   # by UTC day: a timer drifts by minutes
                due.setdefault((t, newest), "weekly, newest version")

    def rank(kv):
        (t, n), _why = kv
        tried = _times(recs[t][n], False)
        return max(tried, default=0), hashlib.sha256(("%d %s %d" % (now // 86400, t, n)).encode()).hexdigest()
    return [{"target": t, "version": n, "why": why} for (t, n), why in sorted(due.items(), key=rank)]


def narrow_line(counts):
    """The packet's line; the owner's digest shows the same counts in its own section."""
    if counts is None:
        return "Narrow changes per target: UNMEASURED (the change records did not read)"
    shown = ", ".join("%s %d" % kv for kv in sorted(counts.items()) if kv[1])
    return "Narrow changes per target: %s" % (shown or "none")


def _dirty(paths, repo):
    return A.git("status", "--porcelain", "--", *paths, cwd=repo, check=False).strip()


def _rel(path, repo):
    return os.path.relpath(path, repo)


def _publish_check(row, epath, cpath, before, repo, publish):
    """The check's evidence and appended entry, published by explicit path. A refusal puts both back so it stays due."""
    head = A.git("rev-parse", "HEAD", cwd=repo).strip()
    rel = [_rel(epath, repo), _rel(cpath, repo)]
    msg = "%s: generalization check %s v%d reads %s" % (ITEM, row["target"], row["version"], row["verdict"])
    try:
        ok, detail = (publish or A.publish_paths)(msg, rel, repo)
    except Exception as e:
        ok, detail = False, "crashed: %s" % str(e)[:300]
    if not ok and A.git("rev-parse", "HEAD", cwd=repo).strip() == head:
        A.git("reset", "-q", "--", *rel, cwd=repo, check=False)
        os.remove(epath)
        with open(cpath, "w", encoding="utf-8") as f:
            f.write(before)
    return ok, detail


def enact_revert(row, rec, cpath, day, repo, changes_dir, publish):
    """Publish a new version undoing rec's diff. -> (ok, detail); any refusal leaves the tree as it found it."""
    t, n = row["target"], row["version"]
    res = A.resolve_target(t)
    if not res:
        return False, "%s is no longer an editable target" % t
    if _dirty([res["path"]], repo):
        return False, "%s has uncommitted edits; refusing to mix" % res["path"]
    fd, dpath = tempfile.mkstemp(suffix=".diff")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(rec.get("diff") or "")
    try:
        r = subprocess.run(["git", "apply", "-R", "--check", dpath], cwd=repo, capture_output=True, text=True,
                           timeout=60)
        if r.returncode != 0:
            return False, "v%d does not reverse-apply on today's text: %s" % (n, r.stderr[-200:])
        A.git("apply", "-R", dpath, cwd=repo)
        try:
            probs = A.run_checks(res, repo)
        except Exception as e:   # a timeout or crash must not leave the revert applied
            probs = ["checks crashed: %s" % str(e)[:300]]
        if probs:
            A.git("apply", dpath, cwd=repo)
            return False, "; ".join(probs)
        return _publish_revert(row, rec, cpath, res, dpath, day, repo, changes_dir, publish)
    finally:
        os.remove(dpath)


def _publish_revert(row, rec, cpath, res, dpath, day, repo, changes_dir, publish):
    t, n = row["target"], row["version"]
    m = A.next_version(t, changes_dir, cwd=repo)
    tag, new_path = "agent/%s/v%d" % (t, m), os.path.join(changes_dir, "%s_v%d.json" % (t, m))
    before = open(cpath, encoding="utf-8").read()
    head = A.git("rev-parse", "HEAD", cwd=repo).strip()

    def undo():
        A.git("reset", "-q", "--", res["path"], _rel(new_path, repo), _rel(cpath, repo), cwd=repo, check=False)
        A.git("apply", dpath, cwd=repo)
        if os.path.exists(new_path) and made:
            os.remove(new_path)
        with open(cpath, "w", encoding="utf-8") as f:
            f.write(before)
    made = False
    change = {"target": t, "version": m, "tag": tag, "day": day, "path": res["path"], "revert_of": n,
              "revert_verdict": row["verdict"], "revert_evidence": row["evidence"], "pieces": [],
              "source_kinds": rec.get("source_kinds") or [], "diff": A.git("diff", "--", res["path"], cwd=repo),
              "verdict": None, "recheck": "Undoes v%d, which the generalization check read as %s." % (n, row["verdict"]),
              "recheck_result": None, "rechecks": [], "generalization": []}
    try:
        with open(new_path, "x", encoding="utf-8") as f:   # never over a record someone left
            made = True
            json.dump(change, f, indent=1)
        with open(cpath, "w", encoding="utf-8") as f:
            json.dump(dict(rec, reverted_by=m), f, indent=1)
    except Exception as e:   # nothing may stay applied or half-written before publish
        undo()
        return False, "preparing the revert record failed: %s" % str(e)[:300]
    msg = ("%s: revert %s v%d as v%d, generalization check reads %s\n\n"
           "Delegated: technical — agent improvement %s revert\nEvidence: %s\nChange record: %s\n"
           % (ITEM, t, n, m, row["verdict"], t, row["evidence"], _rel(new_path, repo)))
    paths = [res["path"], _rel(new_path, repo), _rel(cpath, repo)]
    try:
        ok, sha = (publish or A.publish_paths)(msg, paths, repo)
    except Exception as e:
        ok, sha = False, "crashed: %s" % str(e)[:300]
    if not ok:
        if A.git("rev-parse", "HEAD", cwd=repo).strip() != head:
            return False, "publish: %s (its commit is left on HEAD for a human)" % sha
        undo()
        return False, "publish: %s" % sha
    A.git("tag", tag, sha, cwd=repo, check=False)
    tagged = A.git("rev-parse", "-q", "--verify", "refs/tags/%s^{commit}" % tag, cwd=repo, check=False).strip()
    if not sha or not tagged.startswith(sha):
        return True, "%s published, but tag %s resolves to %r, not it" % (sha, tag, tagged)
    try:
        pushed = subprocess.run(["git", "push", "origin", "refs/tags/%s" % tag], cwd=repo, capture_output=True,
                                text=True, timeout=300).returncode == 0
    except (OSError, subprocess.SubprocessError):   # the revert IS published: a late tag never reads as a refusal
        pushed = False
    return True, "%s %s%s" % (tag, sha, "" if pushed else " (tag push FAILED; local tag only)")


def run_one(item, day, repo, changes_dir, general_dir, check_version, publish, now):
    """One due check, recorded and published, then its revert if it reads one. -> the pass's row."""
    t, n = item["target"], item["version"]
    row = dict(item)
    cpath = os.path.join(changes_dir, "%s_v%d.json" % (t, n))
    if _dirty([_rel(cpath, repo)], repo):
        return dict(row, verdict=None, detail="the change record has uncommitted edits; left due")
    try:
        before = open(cpath, encoding="utf-8").read()
        result, (epath, cpath) = check_version(t, "v%d" % n, repo=repo, changes_dir=changes_dir,
                                               general_dir=general_dir, now=now)
    except Exception as e:   # a crashed check is no verdict, and it stays due
        return dict(row, verdict=None, detail="check crashed: %s" % str(e)[:300])
    row.update(verdict=result["verdict"], keep=result["keep"], evidence=_rel(epath, repo))
    ok, detail = _publish_check(row, epath, cpath, before, repo, publish)
    row.update(published=bool(ok), detail=str(detail))
    if not ok or result["keep"] is not False:
        return row
    try:
        rec = json.load(open(cpath, encoding="utf-8"))
        done, why = enact_revert(row, rec, cpath, day, repo, changes_dir, publish)
    except Exception as e:
        done, why = False, "crashed: %s" % str(e)[:300]
    return dict(row, revert="published" if done else "refused", revert_detail=why)


def run_due(day, level, repo=None, changes_dir=None, check_version=None, publish=None, now=None):
    """The pass's generalization step -> its rows. Runs on committed change records only."""
    repo, changes_dir = repo or A.REPO, changes_dir or A.CHANGES
    general_dir = os.path.join(os.path.dirname(os.path.abspath(changes_dir)), "general")
    due = due_checks(level, now, changes_dir)
    rows = []
    for item in due[:MAX_CHECKS]:
        try:
            rows.append(run_one(item, day, repo, changes_dir, general_dir, check_version or G.run_for_version, publish,
                                now))
        except Exception as e:   # one target's fault (a git failure, a bad record) never costs the others or the pass
            rows.append(dict(item, verdict=None, detail="crashed: %s" % str(e)[:300]))
    return rows


def narrow_counts(changes_dir=None):
    return D.narrow_counts(changes_dir or A.CHANGES)
