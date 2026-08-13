#!/usr/bin/env python3
"""check_git_locks.py — is the tree blocked by a DEAD git, or a live peer?

WHY
===
Five seats share one working tree. When a git process dies mid-commit it leaves
`.git\\index.lock` behind, and every other seat then sees only

    fatal: Unable to create '.../.git/index.lock': File exists.

That message cannot distinguish "a peer is committing right now" from "a corpse
is holding the door". The safe reading — someone is mid-commit, wait — is also
the one that blocks forever. Five seats sat unable to commit for 19 minutes on
exactly that ambiguity, and nothing reported it.

So this tool does not guess. It gathers the four pieces of evidence that
separate the two cases and PRINTS them all, so the verdict can be checked
rather than trusted:

  * age      — a lock younger than STALE_AGE is plausibly a peer mid-commit
  * holders  — `fuser`; git holds its lock file OPEN for the whole operation,
               so a lock nobody has open is a lock nobody is using
  * git procs— any live `git` in `ps -ef`, the fallback when fuser is missing
  * size     — a 0-byte `index.lock` is the signature of a crashed start

NEVER DELETES
=============
It prints the `rm` for a lock it judges stale and stops there. Deleting a LIVE
lock corrupts a peer's commit, so the tool that reads the evidence is
deliberately not the tool that can act on it. A human or a seat runs the `rm`.

INTERFACE
=========
    python3 src/RimMandrake/Utils/check_git_locks.py            # evidence + verdicts
    python3 src/RimMandrake/Utils/check_git_locks.py --quiet     # silent unless something is there

EXIT CODES
==========
    0  clear — no lock files
    1  a stale lock exists; the printed `rm` is safe to run
    2  a lock exists and looks LIVE — wait, do not delete

1 beats 2 when both are present: a stale lock is the one with an action.
Indeterminate evidence resolves to LIVE, because the cost of the two mistakes
is not symmetric.
"""
import argparse
import os
import subprocess
import sys
import time

STALE_AGE = 120          # seconds; under this a peer is plausibly mid-commit
PROBE_TIMEOUT = 3        # seconds per external probe; this runs before a prompt

# The whole surface. refs/**/*.lock is walked; the rest are exact paths.
FIXED_LOCKS = ("index.lock", "HEAD.lock", "config.lock")


def git_dir():
    """The real .git, or None. `.git` is a FILE in a worktree, so ask git."""
    root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--absolute-git-dir"],
            cwd=root, capture_output=True, text=True, timeout=PROBE_TIMEOUT,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.strip() or None


def find_locks(gdir):
    found = []
    for name in FIXED_LOCKS:
        path = os.path.join(gdir, name)
        if os.path.exists(path):
            found.append(path)
    refs = os.path.join(gdir, "refs")
    for dirpath, _dirnames, filenames in os.walk(refs):
        for fn in filenames:
            if fn.endswith(".lock"):
                found.append(os.path.join(dirpath, fn))
    return sorted(found)


def git_processes():
    """PIDs of live git processes, or None if ps could not be read.

    Parsed straight out of `ps -ef` rather than piped through grep, so there is
    no grep line to exclude and no risk of matching this checker's own argv.
    """
    try:
        proc = subprocess.run(
            ["ps", "-ef"], capture_output=True, text=True, timeout=PROBE_TIMEOUT,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None

    me = os.getpid()
    hits = []
    for line in proc.stdout.splitlines()[1:]:
        fields = line.split(None, 7)
        if len(fields) < 8:
            continue
        pid, cmd = fields[1], fields[7]
        argv0 = os.path.basename(cmd.split()[0]) if cmd.split() else ""
        if argv0 != "git" and not argv0.startswith("git-"):
            continue
        if pid.isdigit() and int(pid) == me:
            continue
        hits.append((pid, cmd[:100]))
    return hits


def holders(path):
    """(pids, note) from fuser. pids is None when fuser cannot answer."""
    try:
        proc = subprocess.run(
            ["fuser", path], capture_output=True, text=True, timeout=PROBE_TIMEOUT,
        )
    except FileNotFoundError:
        return None, "unavailable (fuser not installed)"
    except (OSError, subprocess.SubprocessError):
        return None, "unavailable (fuser failed)"
    # GNU fuser: rc 0 = something holds it, rc 1 = nothing does. Anything else
    # is fuser declining to answer (drvfs mounts do this), not proof of absence.
    if proc.returncode == 0:
        pids = proc.stdout.split()
        if not pids:
            # Held, but the pid landed on stderr. Held is the load-bearing half,
            # so keep the truthy answer rather than degrading to indeterminate.
            return ["?"], "held (pid not reported)"
        return pids, "held by " + " ".join(pids)
    if proc.returncode == 1:
        return [], "nobody has it open"
    return None, "unavailable (fuser rc=%d)" % proc.returncode


def judge(age, size, pids, procs):
    """(verdict, reason). Indeterminate resolves to LIVE — see module docstring."""
    if pids:
        return "LIVE", "a process has it open"
    if age < STALE_AGE:
        return "LIVE", "younger than %ds; a peer may be mid-commit" % STALE_AGE
    if pids == []:
        extra = " (0 bytes — crashed start)" if size == 0 else ""
        return "STALE", "old and nobody has it open" + extra
    # fuser could not answer; fall back to whether any git is alive at all.
    if procs is None:
        return "LIVE", "old, but neither fuser nor ps could be read"
    if procs:
        return "LIVE", "old and unheld-unknown, but %d git process(es) running" % len(procs)
    extra = " (0 bytes — crashed start)" if size == 0 else ""
    return "STALE", "old, no git process running" + extra


def humanize(seconds):
    if seconds < 90:
        return "%ds" % int(seconds)
    if seconds < 5400:
        return "%dm %ds" % (int(seconds) // 60, int(seconds) % 60)
    return "%dh %dm" % (int(seconds) // 3600, (int(seconds) % 3600) // 60)


def main():
    ap = argparse.ArgumentParser(description="Report stale vs live git lock files.")
    ap.add_argument("--quiet", action="store_true",
                    help="print nothing when there are no locks")
    args = ap.parse_args()

    gdir = git_dir()
    if not gdir:
        if not args.quiet:
            print("check_git_locks: not a git repo (or git unavailable)")
        return 0                                   # fail open; not our problem

    locks = find_locks(gdir)
    if not locks:
        if not args.quiet:
            print("check_git_locks: clear — no lock files under %s" % gdir)
        return 0

    procs = git_processes()
    now = time.time()
    verdicts = []
    out = ["check_git_locks: %d lock file(s) under %s" % (len(locks), gdir), ""]

    for path in locks:
        try:
            st = os.stat(path)
        except OSError:
            continue                               # vanished mid-scan: a peer finished
        age = max(0.0, now - st.st_mtime)
        pids, note = holders(path)
        verdict, reason = judge(age, st.st_size, pids, procs)
        verdicts.append(verdict)

        out.append("  %s  %s" % (verdict, path))
        out.append("    age      %s (mtime %s)"
                   % (humanize(age), time.strftime("%H:%M:%S", time.localtime(st.st_mtime))))
        out.append("    size     %d bytes%s"
                   % (st.st_size, "  <- crashed start" if st.st_size == 0 else ""))
        out.append("    open by  %s" % note)
        if procs is None:
            out.append("    git ps   unavailable")
        elif procs:
            out.append("    git ps   %d running: %s"
                       % (len(procs), "; ".join("%s %s" % p for p in procs[:3])))
        else:
            out.append("    git ps   none running")
        out.append("    verdict  %s — %s" % (verdict, reason))
        if verdict == "STALE":
            out.append("    clear it rm -f '%s'" % path)
        else:
            out.append("    action   WAIT. Do not delete a live lock.")
        out.append("")

    if "STALE" in verdicts:
        out.append("Stale lock(s) found. Run the printed rm, then retry the commit.")
        rc = 1
    else:
        out.append("All locks look live. Wait and re-run; do not delete.")
        rc = 2

    print("\n".join(out))
    return rc


if __name__ == "__main__":
    sys.exit(main())
