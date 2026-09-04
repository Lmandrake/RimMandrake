#!/usr/bin/env python3
"""code_review_status.py — the "clean or dirty" ledger CLAUDE.md's
"Code isn't clean until a review says so" policy actually points at.

A file is CLEAN only if it has an entry here AND zero commits have
touched it since the recorded commit. Anything else — no entry, or any
commit since — is DIRTY. There is no other way to earn CLEAN: fixing a
finding does not clean a file, only a full-file review returning zero
significant findings does, recorded here with `mark-clean`.

🔴 This is not a Python-only tool. It covers ANY file that contributes to
what the game actually loads — .py tooling, .cs mod source, .xml Defs and
Patches alike. "Code isn't clean until a review says so" (CLAUDE.md) never
said Python; do not narrow it. Owner ruling 2026-09-03, after an agent was
told mid-review not to mark-clean a .cs file "because C# isn't in scope
yet" — it always was.

    python3 src/RimMandrake/Utils/code_review_status.py check <path> [<path> ...]
    python3 src/RimMandrake/Utils/code_review_status.py mark-clean <path> [--sha <sha>]
    python3 src/RimMandrake/Utils/code_review_status.py reopen <path> [<path> ...] --reason "…"
    python3 src/RimMandrake/Utils/code_review_status.py list

The log (`infrastructure/state/CODE_REVIEW_STATUS.json`) is owned by this
script — do not hand-edit it, the same convention as the ledger.
"""
import argparse
import contextlib
import fcntl
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
LOG_PATH = os.path.join(ROOT, "infrastructure", "state", "CODE_REVIEW_STATUS.json")
LOCK_PATH = LOG_PATH + ".lock"


def _trigger_health_rebuild():
    """Give the codebase-health map a heartbeat after a state change that isn't a
    git commit — mark-clean (dirty->green) and reopen (green->dirty) both flip a
    file's colour with no commit involved, so the git post-commit hook never fires
    for them. Same three rules as src/RimMandrake/Utils/git_hooks/post-commit:
    never block the caller, never fail the caller, never touch the index. The
    publisher itself decides whether a rebuild is actually due.

    Cheap precheck: a plain read of the publisher's own state file's `ts` — no
    subprocess — before spawning a python interpreter that would just re-derive
    "not due yet" via its own fingerprint check. Any read failure falls through
    to spawning, same as always; MIN_INTERVAL is mirrored from
    codebase_health_publish.py.
    """
    MIN_INTERVAL = 300
    try:
        with open(os.path.join(ROOT, "infrastructure", "state",
                                "codebase_health_last.json")) as fh:
            last_ts = json.load(fh).get("ts")
        if last_ts is not None and (time.time() - last_ts) < MIN_INTERVAL:
            return
    except (OSError, ValueError):
        pass
    log_path = os.path.join(ROOT, "Transient", "codebase_health_hook.log")
    try:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, "a") as fh:
            subprocess.Popen(
                [sys.executable, os.path.join(HERE, "codebase_health_publish.py")],
                cwd=ROOT, stdout=fh, stderr=fh, stdin=subprocess.DEVNULL,
                start_new_session=True,
            )
    except OSError:
        pass


@contextlib.contextmanager
def locked():
    """Exclusive lock across a load-mutate-save critical section. This repo
    is shared by two live agent windows (BENCH/FOUNDRY); without this, two
    concurrent mark-clean calls on different files is a lost-update race —
    whichever save() runs last wins and the other's entry silently vanishes."""
    os.makedirs(os.path.dirname(LOCK_PATH), exist_ok=True)
    fd = os.open(LOCK_PATH, os.O_WRONLY | os.O_CREAT, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def load():
    if not os.path.isfile(LOG_PATH):
        return {}
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save(data):
    # Per-call unique tmp name + lock + os.replace, same discipline as
    # rimflow.model.write_bridge_file / atomic_copy: a fixed "<path>.tmp"
    # truncates whatever a concurrent writer already put there (O_TRUNC
    # fires at open(), before any lock), and an interrupt mid-write must
    # never leave truncated/partial JSON where load() will raise on it.
    tmp = "%s.tmp.%d.%d" % (LOG_PATH, os.getpid(), time.time_ns())
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX)
            try:
                body = json.dumps(data, indent=2, sort_keys=True) + "\n"
                os.write(fd, body.encode("utf-8"))
                os.fsync(fd)
            finally:
                fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)
        os.replace(tmp, LOG_PATH)
    except BaseException:
        # The unique tmp name means a leaked file is never overwritten and so
        # never noticed — it just accumulates untracked next to the log, in a
        # directory `git add` is aimed at by hand. Take it with us on any
        # failure; os.replace has either happened (tmp gone) or has not.
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def repo_rel(path):
    return os.path.relpath(os.path.abspath(path), ROOT).replace(os.sep, "/")


def git(args):
    return subprocess.run(["git"] + args, cwd=ROOT, capture_output=True, text=True)


def commits_since(sha, relpath):
    r = git(["log", "--oneline", f"{sha}..HEAD", "--", relpath])
    if r.returncode != 0:
        return None  # sha doesn't exist / bad ref
    lines = [l for l in r.stdout.splitlines() if l.strip()]
    return lines


def commits_since_bulk(entries):
    """Same answer as calling `commits_since(sha, path)` once per (path, sha) in
    `entries` — {path: sha} — but with ONE git subprocess instead of one per path.

    🔴 THIS IS WHY THE HEALTH BOARD WAS SLOW. `codebase_health.py`'s `review_verdicts()`
    used to call `commits_since()` once per green-marked path — 526 separate `git log`
    spawns measured on 2026-09-04, each paying full git-process-start overhead on this
    WSL-mounted drive. One `git log --name-only` walk of the whole history, parsed once,
    answers all of them: for each path, find the index of its MOST RECENT commit (index 0
    = HEAD, since `git log`'s default order is newest-first); for each sha, find its own
    index the same way. `path` has commits since `sha` iff the path's most-recent index is
    STRICTLY LOWER (newer) than the sha's index — i.e. something touched it after that
    commit. A sha absent from the log (bad ref, or not an ancestor of HEAD) reproduces the
    old "unknown" outcome exactly, because `commits_since` also failed for such a sha.

    Returns {path: lines_or_None} — same per-path shape as `commits_since`: `None` means
    "sha doesn't resolve" (unknown), an empty list means clean, a non-empty list means
    dirty. The list itself is a placeholder (`["seen"]`), never real commit lines — nothing
    in this codebase reads more than truthiness off it, and reconstructing real `--oneline`
    text here would cost back the very git calls this function exists to avoid.
    """
    if not entries:
        return {}
    # Recorded shas are whatever length `git rev-parse --short` gave at mark-clean
    # time (this repo's history currently yields 8 hex chars, but that grows with
    # repo size) — never assume a fixed width, index every full hash at every
    # width actually in use so a lookup by any of them lands correctly.
    lengths = {len(s) for s in entries.values() if s}
    r = git(["log", "--name-only", "--format=C:%H"])
    if r.returncode != 0:
        return {p: None for p in entries}
    sha_index = {}
    path_newest_index = {}
    idx = -1
    for line in r.stdout.splitlines():
        if line.startswith("C:"):
            idx += 1
            full = line[2:]
            for length in lengths:
                sha_index.setdefault(full[:length], idx)
        elif line.strip() and line not in path_newest_index:
            path_newest_index[line] = idx          # first sighting is the newest (order is newest-first)
    result = {}
    for path, sha in entries.items():
        if sha not in sha_index:
            result[path] = None
            continue
        newest = path_newest_index.get(path)
        result[path] = ["seen"] if newest is not None and newest < sha_index[sha] else []
    return result


def working_tree_dirty(relpath):
    """True if `relpath` has any uncommitted change (staged, unstaged, or
    untracked). Returns None if git itself failed to answer (path outside
    the repo, index lock contention, ...) — the caller must treat that as
    "cannot prove clean", never as "no changes"."""
    r = git(["status", "--porcelain", "--", relpath])
    if r.returncode != 0:
        return None
    return bool(r.stdout.strip())


def clean_state(rel, entry):
    """Returns (state, detail) where state is CLEAN/DIRTY. `entry` may be
    None (never marked). Shared by `check` and `list` so the two commands
    cannot disagree about what CLEAN means."""
    if entry is None:
        return "DIRTY", "never marked clean"

    dirty = working_tree_dirty(rel)
    if dirty is None:
        return "DIRTY", "git could not report working-tree status (path outside repo, or a lock)"
    if dirty:
        return "DIRTY", "uncommitted changes since the clean mark"

    since = commits_since(entry["sha"], rel)
    if since is None:
        return "DIRTY", f"recorded sha {entry['sha']} not found — log is stale"
    if len(since) > 0:
        return "DIRTY", (f"{len(since)} commit(s) since clean at {entry['sha']} on {entry['date']}", since)
    return "CLEAN", f"clean at {entry['sha']} on {entry['date']}"


def cmd_check(paths):
    data = load()
    any_dirty = False
    for p in paths:
        rel = repo_rel(p)
        state, detail = clean_state(rel, data.get(rel))
        if state == "DIRTY":
            any_dirty = True
            if isinstance(detail, tuple):
                msg, lines = detail
                print(f"DIRTY  {rel}  ({msg}):")
                for line in lines:
                    print(f"         {line}")
            else:
                print(f"DIRTY  {rel}  ({detail})")
        else:
            print(f"CLEAN  {rel}  ({detail})")
    return 1 if any_dirty else 0


def cmd_mark_clean(path, sha):
    rel = repo_rel(path)
    if rel.startswith("../") or rel == "..":
        print(f"FAIL: {rel} is outside the repo root.", file=sys.stderr)
        return 2
    if not os.path.isfile(os.path.join(ROOT, rel)):
        print(f"FAIL: {rel} does not exist under the repo root.", file=sys.stderr)
        return 2
    # A path git does not track has no commit to anchor a clean mark to, and
    # the working-tree check below cannot see it either: `git status` stays
    # silent on an IGNORED file, so one would record CLEAN and then read CLEAN
    # for ever, no edit ever making it dirty again. (`vendor/mod_sources/**` is
    # ignored, and this tool's docstring puts .cs mod source in scope.)
    if git(["ls-files", "--error-unmatch", "--", rel]).returncode != 0:
        print(f"FAIL: {rel} is not tracked by git — commit it first, or it can "
              "never be measured dirty again.", file=sys.stderr)
        return 2
    if sha is None:
        r = git(["rev-parse", "--short", "HEAD"])
        if r.returncode != 0 or not r.stdout.strip():
            print("FAIL: could not resolve HEAD.", file=sys.stderr)
            return 2
        sha = r.stdout.strip()
    else:
        # An unvalidated --sha is recorded verbatim. A typo poisons the entry
        # permanently: every later `check` says "recorded sha not found — log is
        # stale", which reads as a repo fault rather than a bad argument, and the
        # bogus mark still burned a cleanCount increment on the health board.
        r = git(["rev-parse", "--verify", "--short", "%s^{commit}" % sha])
        if r.returncode != 0 or not r.stdout.strip():
            print(f"FAIL: --sha {sha} does not resolve to a commit.", file=sys.stderr)
            return 2
        sha = r.stdout.strip()
        # And it must be an ancestor of HEAD. `git log <sha>..HEAD` is empty for
        # any sha HEAD can already reach FROM, so a mark against a commit ahead
        # of HEAD would read CLEAN no matter what HEAD's copy of the file says.
        if git(["merge-base", "--is-ancestor", sha, "HEAD"]).returncode != 0:
            print(f"FAIL: --sha {sha} is not an ancestor of HEAD; a clean mark "
                  "there could never be measured dirty.", file=sys.stderr)
            return 2
    # Uncommitted changes to this exact file mean HEAD is not what will actually
    # ship - refuse rather than record a clean mark against a commit that
    # doesn't reflect what was reviewed. A git FAILURE (index lock, bad path)
    # must refuse too - empty stdout from a failed call is not proof of a
    # clean working tree, and treating it as one is how a lock collision
    # would have let a dirty file get marked clean.
    dirty = working_tree_dirty(rel)
    if dirty is None:
        print(f"FAIL: git could not report status for {rel} (index lock? bad path?). Try again.", file=sys.stderr)
        return 2
    if dirty:
        print(f"FAIL: {rel} has uncommitted changes. Commit first, then mark-clean.", file=sys.stderr)
        return 2
    r = git(["log", "-1", "--format=%ad", "--date=short", sha])
    date = r.stdout.strip() if r.returncode == 0 else "unknown"
    with locked():
        data = load()
        prior = data.get(rel) or {}
        # cleanCount: how many times THIS path has ever been marked clean. A
        # file already dirty again despite N prior clean marks is exactly the
        # "reviewed and it keeps coming back dirty" signal the health board
        # surfaces — see codebase_health.py's classify().
        clean_count = prior.get("cleanCount", 0) + 1
        data[rel] = {"sha": sha, "date": date, "cleanCount": clean_count}
        save(data)
    print(f"CLEAN  {rel}  recorded at {sha} ({date})"
          + (f"  [clean mark #{clean_count}]" if clean_count > 1 else ""))
    return 0


def cmd_reopen(paths, reason):
    """Undo a clean mark: a fix is not a review. Finding a bug and fixing it
    means the file was DIRTY and someone edited it - it does not mean a
    full-file review found nothing, which is the only thing mark-clean is
    allowed to certify. `reopen` puts a path back to "never marked clean" so
    it must survive a genuine follow-up review (only minor comments at most)
    before mark-clean can be called on it again. `--reason` is required and
    goes to stdout / the caller's commit message, not into the ledger itself
    - git history is this repo's provenance, not a second copy of it here."""
    if not reason or not reason.strip():
        print("FAIL: --reason is required - say why this is being reopened.", file=sys.stderr)
        return 2
    # Validate every path BEFORE touching the log. Without this a typo prints
    # the reassuring "(already not clean)" and exits 0 while the file the
    # operator meant to retract stays marked CLEAN — a silent no-op in the one
    # command whose entire job is undoing a wrong clean mark.
    rels = []
    for path in paths:
        rel = repo_rel(path)
        if rel.startswith("../") or rel == "..":
            print(f"FAIL: {rel} is outside the repo root.", file=sys.stderr)
            return 2
        if not os.path.isfile(os.path.join(ROOT, rel)):
            print(f"FAIL: {rel} does not exist under the repo root.", file=sys.stderr)
            return 2
        rels.append(rel)
    with locked():
        data = load()
        changed = []
        for rel in rels:
            if rel in data:
                # NOTE: this drops the entry's cleanCount with it, so a reopened
                # file's "reviewed, then dirty again" streak restarts at 1 on the
                # health board. Keeping the count would need a sha-less stub
                # entry, and codebase_health.review_verdicts() reads entry["sha"]
                # unguarded — not a change to make inside a review pass.
                del data[rel]
                changed.append(rel)
        if changed:
            save(data)
    for rel in changed:
        print(f"REOPENED  {rel}  ({reason})")
    for rel in rels:
        if rel not in changed:
            print(f"(already not clean)  {rel}")
    return 0


def cmd_list():
    data = load()
    if not data:
        print("(empty — nothing has ever been marked clean)")
        return 0
    for rel in sorted(data):
        entry = data[rel]
        state, _ = clean_state(rel, entry)
        label = state if state == "CLEAN" else "DIRTY (edited since / uncommitted)"
        cc = entry.get("cleanCount", 1)
        streak = f"  [x{cc}]" if cc > 1 else ""
        print(f"{label:35s} {rel}  ({entry['sha']}, {entry['date']}){streak}")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_check = sub.add_parser("check", help="report CLEAN/DIRTY for one or more paths")
    p_check.add_argument("paths", nargs="+")

    p_mark = sub.add_parser("mark-clean", help="record a path as reviewed clean at a commit")
    p_mark.add_argument("path")
    p_mark.add_argument("--sha", default=None, help="defaults to current HEAD")

    p_reopen = sub.add_parser("reopen", help="undo a clean mark - a fix is not a review")
    p_reopen.add_argument("paths", nargs="+")
    p_reopen.add_argument("--reason", required=True, help="why this is being reopened")

    sub.add_parser("list", help="show every recorded entry and its current state")

    args = ap.parse_args()
    if args.cmd == "check":
        sys.exit(cmd_check(args.paths))
    elif args.cmd == "reopen":
        rc = cmd_reopen(args.paths, args.reason)
        if rc == 0:
            _trigger_health_rebuild()
        sys.exit(rc)
    elif args.cmd == "mark-clean":
        rc = cmd_mark_clean(args.path, args.sha)
        if rc == 0:
            _trigger_health_rebuild()
        sys.exit(rc)
    elif args.cmd == "list":
        sys.exit(cmd_list())


if __name__ == "__main__":
    main()
