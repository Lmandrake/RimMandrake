#!/usr/bin/env python3
"""deploy_update.py update -- fast-forward THIS checkout (the dedicated deploy checkout /home/mandrake/rm/pulse-deploy, never a
seat clone) to origin/main. Run every 10 min by rm-deploy-update.service; rm-streams-collect and ops_watch run from
that checkout.

RimPulse's `pulse.py update`, the one verb of that command still run (the dashboard retired 2026-11-03; the rest of
pulse.py went 2026-11-18 and this moved from Utils/pulse/, RIMMANDRAKE_SPLIT_LIVE_CODE_OUT_OF_RELENTLESS_NAMED_MODULES).
The checkout keeps its old name and its `.git/pulse_update_last_good` stamp, which ops_watch reads.
"""
from __future__ import annotations

import glob
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ops_ledger as pc  # noqa: E402

ROOT = Path(__file__).resolve().parents[4]   # the checkout this code runs from
# what the sparse deploy checkout holds: ops_core itself, rimflow's fold, and art/ for prereview.py (the "to look at"
# gate). Files directly in a parent dir (Utils/rmpaths.py, Utils/close_evidence.py) come free. Every dir the deploy's
# units reach must be here: selftest_deploy_sparse_dirs.py walks their imports (PULSEDEPLOY_FIX_SPARSE_LIST_FORGOT_CONTRACTS).
SPARSE_DIRS = ("src/RimMandrake/Utils/ops_core", "src/RimMandrake/rimflow", "src/RimMandrake/Utils/art",
               "src/RimMandrake/Utils/modcheck",    # modcheck/metrics.py: testing_metrics.py's owner-day + sheet loader
               "src/RimMandrake/Utils/northstar_driver",  # modcheck/test_site_saves.py imports its session
               "src/RimMandrake/Utils/rimdrive",    # northstar_driver/session.py and modcheck import it
               "src/RimMandrake/Utils/sim",         # sim/csuite_codex_limits.py: ops_watch.py's Codex reading
               "src/RimMandrake/contracts",         # close_evidence.py path-loads contracts/jsonl.py; rimflow imports it
               "src/RimMandrake/Utils/testq",       # ops_watch.py's brake reading; rimflow/dispatcher.py
               "src/RimMandrake/Utils/artpipe",     # art/enact.py's fill_queue
               "src/RimMandrake/Utils/systemd")     # the unit texts install_units writes (data, not imports)

# The unit gives a pass TimeoutStartSec=120 s; this budget stays under it.
UPDATE_BUDGET_S = 80
# A skip is a success for systemd, so nothing else would notice a deploy that has stopped updating.
UPDATE_SKIP_MAX_AGE_S = 3600
UPDATE_STAMP = "pulse_update_last_good"


def _git_err(p) -> str:
    """The end of git's complaint, without its progress lines: the 2026-11-03 rc 128 kept only
    'Updating files: 14% (1/7)…', and the reason was cut off (PULSE_DEPLOY_GUARD_SOMEONE_WALKED_IN)."""
    lines = [ln for ln in (p.stderr or p.stdout or "").replace("\r", "\n").splitlines()
             if ln.strip() and not ln.startswith(("Updating files:", "Checking out files:"))]
    return " | ".join(lines)[-300:]


def _clean_landed_dirt(git) -> bool:
    """A pull that dies mid-checkout leaves origin/main's blobs in the tree with HEAD unmoved, and every
    later --ff-only then refuses them as local changes (2026-11-03 12:38Z: rc 128 after 'Updating files
    7/7'; no writer had walked in, PULSE_DEPLOY_GUARD_SOMEONE_WALKED_IN). It can die after the index is
    written too, leaving the paths STAGED, renames included, and the next fetch moves origin/main past the
    commit it was checking out (2026-11-05 09:57Z: 13 staged paths, each a blob of some commit in
    HEAD..origin/main, none the tip's; OPS_DEPLOY_UPDATE_UNSTICK_RDHQ). So a dirty path is landed when its
    index AND worktree content equal that path in origin/main or in any commit of HEAD..origin/main (absent
    counts). When EVERY dirty path is landed, put them back to HEAD so the retry can fast-forward. Any path
    that is not is someone's real edit: leave it all and let the pull fail loud. True only when something
    was cleaned."""
    s = git("status", "--porcelain=v1", "-z", "--untracked-files=all")
    if s.returncode != 0 or not s.stdout:
        return False
    entries, recs = [], s.stdout.split("\0")
    i = 0
    while i < len(recs):
        rec = recs[i]
        i += 1
        if len(rec) < 4:
            continue
        code, path = rec[:2], rec[3:]
        if code in ("DD", "AU", "UD", "UA", "DU", "AA", "UU"):
            return False             # a merge conflict: not a half-done checkout
        if code[0] in "RC":          # the source path is the next record
            src = recs[i] if i < len(recs) else ""
            i += 1
            if code[0] == "C" or not src:
                return False
            entries.append(("D ", src))   # its source: staged as gone
        entries.append((code, path))
    if not entries:
        return False

    def blob(rev, path):
        return git("rev-parse", "-q", "--verify", f"{rev}:{path}").stdout.strip()

    def landed(path, *haves):
        """Every one of `haves` (blob or "" for absent) is this path's content on origin/main or at a
        commit between HEAD and it."""
        seen = {blob("origin/main", path)}
        if set(haves) <= seen:
            return True
        for c in git("rev-list", "HEAD..origin/main", "--", path).stdout.split():
            seen.add(blob(c, path))
            if set(haves) <= seen:
                return True
        return False

    root = Path(git("rev-parse", "--show-toplevel").stdout.strip())
    paths = []
    for code, path in entries:
        if code == "??" and not blob("origin/main", path) and not landed(path, git("hash-object", "--", path).stdout.strip()):
            continue                 # junk origin does not have (a __pycache__): it blocks no pull
        if code[0] in "MAR":
            index = (git("ls-files", "-s", "--", path).stdout.split() or ["", ""])[1]
        elif code[0] == "D":
            index = ""
        else:
            index = None             # untracked, or only the worktree changed: the index is HEAD's
        work = git("hash-object", "--", path).stdout.strip() if (root / path).is_file() else ""
        if not landed(path, *[h for h in (index, work) if h is not None]):
            return False
        paths.append(path)
    if not paths:
        return False
    in_head = [p for p in paths if blob("HEAD", p)]
    not_head = [p for p in paths if p not in in_head]
    if in_head and git("restore", "--source=HEAD", "--staged", "--worktree", "--", *in_head).returncode != 0:
        return False
    if not_head:
        git("rm", "-q", "--cached", "--ignore-unmatch", "--", *not_head)
        for path in not_head:
            (root / path).unlink(missing_ok=True)
    print(f"deploy update: put back {len(paths)} path(s) already on origin/main "
          f"(a half-done fast-forward): {', '.join(paths[:5])}", flush=True)
    return True


def _clear_stale_index_lock(lock: Path, timeout: float) -> float | None:
    """Clear an abandoned deploy index lock and return its age in seconds."""
    try:
        seen = lock.stat()
        age = time.time() - seen.st_mtime
        if age <= timeout or not Path("/proc/self/fd").is_dir():
            return None
        resolved = os.path.realpath(lock)
        for fd in glob.iglob("/proc/[0-9]*/fd/*"):
            try:
                if os.readlink(fd) == resolved:
                    return None
            except OSError:
                continue               # vanished process or a descriptor we cannot inspect
        current = lock.stat()
        if not os.path.samestat(seen, current) or seen.st_mtime_ns != current.st_mtime_ns:
            return None                # the lock changed during the scan
        lock.unlink()
        return age
    except FileNotFoundError:
        return None                    # already gone


def update_code(root: Path = ROOT, timeout: float = UPDATE_BUDGET_S, max_skip_age: float = UPDATE_SKIP_MAX_AGE_S) -> dict:
    """Fast-forward the deploy checkout to origin/main. Refuses a seat clone: pulling there would move
    another agent's working tree under it (RIMPULSE_DEPLOY_FIX_RUNS_THE_BENCH_CLONE).

    git on drvfs sometimes outruns the budget; that pass is a skip, not a failed unit (which would trip
    TIMER_FAILED), because the timer is the retry (PULSEUPDATE_FIX_DRVFS_PULL_TIMES_OUT). A skip with no
    good pass for max_skip_age raises instead. `timeout` is the whole pass, not one git call."""
    import subprocess
    if root in pc.CLONES:
        raise RuntimeError(f"{root} is a seat clone, not the deploy checkout; never pulled from here")
    stamp = root / ".git" / UPDATE_STAMP
    end = time.monotonic() + timeout
    cleared = _clear_stale_index_lock(root / ".git" / "index.lock", timeout)
    result = {"cleared_lock": cleared} if cleared is not None else {}

    def git(*a):
        left = end - time.monotonic()
        if left <= 0:
            raise subprocess.TimeoutExpired(["git", *a], timeout)
        return subprocess.run(["git", "-C", str(root), *a], capture_output=True, text=True, timeout=left)
    try:
        old = git("rev-parse", "HEAD").stdout.strip()
        have = set(git("sparse-checkout", "list").stdout.split())
        if have and not set(SPARSE_DIRS) <= have:   # a dir the deploy newly imports from (art/ for prereview.py, 2026-10-23)
            s = git("sparse-checkout", "set", *SPARSE_DIRS)
            if s.returncode != 0:
                raise RuntimeError(f"git sparse-checkout set: rc {s.returncode}: {(s.stderr or s.stdout).strip()[:200]}")
        p = git("pull", "--ff-only", "-q", "origin", "main")
        if p.returncode != 0 and _clean_landed_dirt(git):
            p = git("pull", "--ff-only", "-q", "origin", "main")
        if p.returncode != 0:
            raise RuntimeError(f"git pull --ff-only: rc {p.returncode}: {_git_err(p)}")
        new = git("rev-parse", "HEAD").stdout.strip()
    except subprocess.TimeoutExpired as e:
        try:
            age = time.time() - stamp.stat().st_mtime
        except OSError:
            raise RuntimeError(f"git timed out and {stamp} is missing, so the skip has no good pass to lean on") from e
        if age > max_skip_age:
            raise RuntimeError(f"git timed out and the last good pass is {age:.0f} s old (limit {max_skip_age:.0f} s)") from e
        return {**result, "skipped": True, "age": age}
    stamp.touch()
    return {**result, "old": old[:12], "new": new[:12], "changed": old != new}


def install_units(folder_dir=None, dest=None, sc=None) -> dict:
    """Write every folder unit file whose installed copy differs into ~/.config/systemd/user, then one daemon-reload
    (RIMMANDRAKE_INSTALL_UNIT_TEXTS_ON_DEPLOY_NOT_BY_HAND: before this, a landed unit change reached systemd only by a hand
    `ops_clocks.py install`). Never enables, starts or restarts a unit: a unit may launch Claude, and a changed text
    takes effect at that unit's next own start. A masked (retired) name is skipped and reported; the deadman's units arm
    names it. -> {"wrote": [names], "masked": [names]}; raises on a missing folder or a failed reload."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import ops_clocks as OC
    folder_dir = Path(folder_dir or ROOT / "src/RimMandrake/Utils/systemd")
    if not folder_dir.is_dir():
        raise RuntimeError(f"unit folder {folder_dir} is missing (is it in SPARSE_DIRS?), so no unit text was installed")
    folder = OC.folder_units(folder_dir)
    dest = Path(dest or OC.install_dir())
    inst = OC.installed_units(dest, globs=("*",)) or {}
    masked = sorted(n for n in folder if inst.get(n) is OC.MASK)
    todo = sorted(n for n in folder if inst.get(n) != folder[n] and n not in masked)
    if not todo:
        return {"wrote": [], "masked": masked}
    lines = []
    rc = OC.install(todo, apply=True, enable=False, folder_dir=folder_dir, dest=dest, sc=sc, out=lines.append)
    if rc:
        raise RuntimeError("ops_clocks install: exit %d: %s" % (rc, " | ".join(lines)[-400:]))
    return {"wrote": todo, "masked": masked}


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv != ["update"]:
        print("usage: deploy_update.py update", file=sys.stderr)
        return 2
    u = update_code()
    if u.get("skipped"):
        print(f"deploy update: git timed out, skipping this pass (last good pass {u['age']:.0f} s ago)")
        return 0
    print(f"deploy update: {ROOT} {u['old']} -> {u['new']}" + ("" if u["changed"] else " (already current)"))
    i = install_units()
    print("deploy update: units: wrote %d%s%s" % (len(i["wrote"]), " (%s)" % ", ".join(i["wrote"]) if i["wrote"] else "",
                                                   "; masked, skipped: " + ", ".join(i["masked"]) if i["masked"] else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
