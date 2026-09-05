#!/usr/bin/env python3
"""code_review_status.py — the "clean or dirty" ledger CLAUDE.md's
"Code isn't clean until a review says so" policy actually points at.

A file is CLEAN only if it has an entry here AND its content on disk is
byte-identical to what was recorded at the last `mark-clean`. Anything else
— no entry, or any edit since (committed or not) — is DIRTY. There is no
other way to earn CLEAN: fixing a finding does not clean a file, only a
full-file review returning zero significant findings does, recorded here
with `mark-clean`.

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
    python3 src/RimMandrake/Utils/code_review_status.py list --show-untracked  # + files never entered at all
    python3 src/RimMandrake/Utils/code_review_status.py migrate-hashes   # one-time, see below

The log (`infrastructure/state/CODE_REVIEW_STATUS.json`) is owned by this
script — do not hand-edit it, the same convention as the ledger.

🔴 SCALING REWRITE, owner ruling 2026-09-05 — "I think we need a different
implementation for the clean/dirty code database... this isn't scaling
properly, it's a bottleneck": the previous implementation answered every
`check`/`list` call by asking git (`git status --porcelain` PLUS `git log`
PER PATH). At 1 caller that's fine; with this repo's usual load — many
concurrent review agents, each walking dozens of paths — it fanned out into
hundreds of `git` subprocess spawns hammering one `.git` directory on a
WSL-over-Windows-drive mount, and a single `list` over ~800 recorded entries
alone was ~1,600 spawns. That is what a background agent was seen stuck on
for 10 minutes.

The fix: CLEAN/DIRTY is now answered by comparing a SHA-256 of the file's
current bytes against a hash recorded at `mark-clean` time — zero git calls,
zero subprocesses, for `check`/`list`/`reopen`. `mark-clean` still makes a
small, BEST-EFFORT, TIMEOUT-GUARDED git call or two (to check the file is
tracked, to refuse on uncommitted changes exactly as documented in CLAUDE.md,
and to record an informational commit sha/date) — but those calls happen
once per reviewed file, not once per file per query, and a hung/slow git can
never again hang this tool: every git() call has a hard timeout and a
failure path that still lets the hash-based core answer correctly.

`migrate-hashes` is the one-time backfill for entries recorded before this
rewrite (they carry {sha, date, cleanCount} but no {hash}): for each one it
reads the file's content AS IT WAS AT THE RECORDED SHA (`git show sha:path`)
and hashes that — not the current working-tree copy, which may already have
diverged — so a legacy CLEAN entry's true reviewed content is preserved
exactly, not silently reset to whatever happens to be on disk today. An
entry whose sha no longer resolves gets no hash and reads as DIRTY
("legacy entry, needs re-verification") — the same outcome the old
"recorded sha not found — log is stale" case produced.
"""
import argparse
import contextlib
import fcntl
import hashlib
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
# CODE_REVIEW_STATUS_ROOT redirects the whole tool at a throwaway repo, same
# discipline as rimflow's RIMFLOW_LEDGER/RIMFLOW_ITEMS — a selftest must never
# run mark-clean/reopen against this repo's own real ledger.
ROOT = os.environ.get("CODE_REVIEW_STATUS_ROOT") or os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
LOG_PATH = os.path.join(ROOT, "infrastructure", "state", "CODE_REVIEW_STATUS.json")
LOCK_PATH = LOG_PATH + ".lock"

GIT_TIMEOUT = 8  # seconds. A hung/contended git call fails fast, never hangs the caller.


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
    whichever save() runs last wins and the other's entry silently vanishes.

    Still held only around the tiny load/save below, never around any git
    call — that discipline predates this rewrite and stays: a lock held
    across a slow subprocess is exactly how one stuck caller would freeze
    out every other one."""
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
    """Run git with a hard timeout, decoding output as text. A
    `.git/index.lock` collision (many concurrent callers, exactly this
    repo's normal load) now fails fast with returncode -1 instead of
    hanging the caller — every use site below treats a git failure as
    "cannot tell, fall back / refuse", never as silent success, so a
    timeout is always safe, just less informative."""
    try:
        return subprocess.run(["git"] + args, cwd=ROOT, capture_output=True,
                               text=True, timeout=GIT_TIMEOUT)
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(args, -1, "", "git timed out after %ss" % GIT_TIMEOUT)


def git_bytes(args):
    """Same as git(), but returns raw bytes (stdout) instead of decoded
    text — `migrate-hashes` uses this for `git show sha:path`, and many of
    this repo's reviewed paths are PNGs, which are not valid UTF-8 and
    would crash a text-mode decode."""
    try:
        return subprocess.run(["git"] + args, cwd=ROOT, capture_output=True,
                               text=False, timeout=GIT_TIMEOUT)
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(args, -1, b"", b"git timed out after %ds" % GIT_TIMEOUT)


def file_hash(relpath):
    """SHA-256 of the file's current bytes on disk, or None if it doesn't
    exist / can't be read. This is the WHOLE clean/dirty answer now — no
    git call, no subprocess, safe to run thousands of times in a `list`."""
    try:
        with open(os.path.join(ROOT, relpath), "rb") as f:
            h = hashlib.sha256()
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
            return h.hexdigest()
    except OSError:
        return None


def clean_state(rel, entry):
    """Returns (state, detail) where state is CLEAN/DIRTY. `entry` may be
    None (never marked). Shared by `check` and `list` so the two commands
    cannot disagree about what CLEAN means. Pure Python, zero subprocess
    calls — this is the fix for the scaling bottleneck: the old version
    made two `git` spawns per path here."""
    if entry is None:
        return "DIRTY", "never marked clean"
    recorded_hash = entry.get("hash")
    if not recorded_hash:
        # A pre-rewrite entry that `migrate-hashes` couldn't backfill (its
        # sha no longer resolved) — same outcome as the old "log is stale".
        return "DIRTY", "legacy entry with no recorded hash — needs re-verification"
    current = file_hash(rel)
    if current is None:
        return "DIRTY", "file no longer exists on disk"
    if current != recorded_hash:
        return "DIRTY", "content changed since clean mark at %s on %s" % (
            entry.get("sha", "?"), entry.get("date", "?"))
    return "CLEAN", "clean at %s on %s" % (entry.get("sha", "?"), entry.get("date", "?"))


def cmd_check(paths):
    data = load()
    any_dirty = False
    for p in paths:
        rel = repo_rel(p)
        state, detail = clean_state(rel, data.get(rel))
        if state == "DIRTY":
            any_dirty = True
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
    current_hash = file_hash(rel)
    if current_hash is None:
        print(f"FAIL: could not read {rel} to hash it.", file=sys.stderr)
        return 2
    # A path git does not track has no commit to anchor a clean mark to.
    # Still enforced (policy, not a correctness need under hash-based
    # tracking): a clean mark should point at real, shippable, committed
    # content. `vendor/mod_sources/**` is ignored, and this tool's docstring
    # puts .cs mod source in scope.
    if git(["ls-files", "--error-unmatch", "--", rel]).returncode != 0:
        print(f"FAIL: {rel} is not tracked by git — commit it first, or it can "
              "never be measured dirty again.", file=sys.stderr)
        return 2
    # Uncommitted changes to this exact file mean HEAD is not what will
    # actually ship — refuse rather than record a clean mark whose
    # informational sha doesn't reflect what was reviewed. `diff --quiet`
    # is scoped to one path and skips the untracked-file directory walk
    # `git status` does, so it's the cheaper of the two for this check.
    diff = git(["diff", "--quiet", "HEAD", "--", rel])
    if diff.returncode not in (0, 1):
        print(f"FAIL: git could not report status for {rel} (index lock? bad path?). Try again.", file=sys.stderr)
        return 2
    if diff.returncode == 1:
        print(f"FAIL: {rel} has uncommitted changes. Commit first, then mark-clean.", file=sys.stderr)
        return 2
    if sha is None:
        r = git(["rev-parse", "--short", "HEAD"])
        sha = r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else "unknown"
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
    # sha/date below are informational display only — the hash is the real
    # clean/dirty mechanism, so a git failure here degrades the printout,
    # never the correctness of what gets recorded.
    date = "unknown"
    if sha != "unknown":
        r = git(["log", "-1", "--format=%ad", "--date=short", sha])
        if r.returncode == 0 and r.stdout.strip():
            date = r.stdout.strip()
    with locked():
        data = load()
        prior = data.get(rel) or {}
        # cleanCount: how many times THIS path has ever been marked clean. A
        # file already dirty again despite N prior clean marks is exactly the
        # "reviewed and it keeps coming back dirty" signal the health board
        # surfaces — see codebase_health.py's classify().
        clean_count = prior.get("cleanCount", 0) + 1
        data[rel] = {"hash": current_hash, "sha": sha, "date": date, "cleanCount": clean_count}
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


def cmd_prune(apply):
    """Drop entries whose path no longer exists on disk AT ALL - a file that was
    deleted or `git mv`'d to a new path with no entry ever written for the new
    path. Found 2026-09-05: three such orphans (two deleted score_*.py scripts,
    one file moved src/SPLIT_Phase3 -> src/RimUtinni) plus a whole 8-file block
    for a mod folder relocated wholesale (StickCuisine -> RimStarWars/Cuisine)
    sat in the ledger reading DIRTY forever, because nothing could ever mark a
    path CLEAN or re-review a path that isn't there to review. This is NOT the
    same question `check`/`list` answer (dirty vs clean); a missing path is
    neither - it is not reviewable at all, and its entry is pure noise.

    Deliberately narrow: only removes a path with ZERO bytes to hash (a real
    rename fix belongs at the NEW path via mark-clean, not here) - it does not
    try to guess where content moved to.
    """
    data = load()
    orphans = [rel for rel in data if not os.path.isfile(os.path.join(ROOT, rel))]
    if not orphans:
        print("(nothing to prune - every recorded path still exists on disk)")
        return 0
    for rel in sorted(orphans):
        print(("would drop" if not apply else "dropped") + f"  {rel}  (no longer exists on disk)")
    if not apply:
        print(f"\n{len(orphans)} orphaned entr{'y' if len(orphans) == 1 else 'ies'} - re-run with --apply to remove.")
        return 0
    with locked():
        data = load()
        for rel in orphans:
            data.pop(rel, None)
        save(data)
    print(f"\n{len(orphans)} orphaned entr{'y' if len(orphans) == 1 else 'ies'} removed.")
    return 0


# The three extensions CLAUDE.md's own docstring above names as in scope
# ("not a Python-only tool... .py tooling, .cs mod source, .xml Defs and
# Patches alike"). Scoped to src/ - "what the game actually loads" - not the
# whole repo (design docs, infrastructure/state's own JSON, etc. are not
# reviewable "code" in this sense).
UNTRACKED_SCAN_DIR = "src"
UNTRACKED_SCAN_EXTS = (".py", ".cs", ".xml")


def find_untracked(data):
    """-> sorted list of repo-relative paths under UNTRACKED_SCAN_DIR, of the
    scanned extensions, that are tracked by git but have NEVER been given an
    entry here at all.

    🔴 THIS IS A DIFFERENT QUESTION FROM DIRTY. `list`/`check` report DIRTY
    only for a path that already has an entry and no longer matches it -
    a path with NO entry at all does not appear there, and CLAUDE.md's own
    "no entry ... is DIRTY" rule means those files are dirty too, just
    invisible to a report that only ever iterates recorded entries. Found by
    the owner 2026-09-05, questioning a reported "0 DIRTY" that turned out to
    be true only for the ~917 paths ever entered here, out of 1,402 real
    .py/.cs/.xml files under src/ - the other ~485 were never tracked at all.
    """
    r = git(["ls-files", "--", UNTRACKED_SCAN_DIR])
    if r.returncode != 0:
        return None  # caller must not treat this as "no untracked files"
    tracked = [p for p in r.stdout.splitlines() if p.endswith(UNTRACKED_SCAN_EXTS)]
    return sorted(p for p in tracked if p not in data)


def cmd_list(show_untracked=False):
    data = load()
    if not data:
        print("(empty — nothing has ever been marked clean)")
    else:
        for rel in sorted(data):
            entry = data[rel]
            state, _ = clean_state(rel, entry)
            label = state if state == "CLEAN" else "DIRTY (edited since / uncommitted)"
            cc = entry.get("cleanCount", 1)
            streak = f"  [x{cc}]" if cc > 1 else ""
            print(f"{label:35s} {rel}  ({entry.get('sha', '?')}, {entry.get('date', '?')}){streak}")
    if show_untracked:
        untracked = find_untracked(data)
        print()
        if untracked is None:
            print("UNTRACKED scan skipped: git ls-files failed (timeout or not a git repo).")
        elif not untracked:
            print("UNTRACKED (never reviewed at all): none — every "
                  f"{'/'.join(UNTRACKED_SCAN_EXTS)} file under {UNTRACKED_SCAN_DIR}/ "
                  "has at least one entry here.")
        else:
            print(f"UNTRACKED (never reviewed at all) — {len(untracked)} file(s), "
                  "DIRTY by CLAUDE.md's own default, invisible to the report above "
                  "because no entry has ever been written for them:")
            for rel in untracked:
                print(f"  {rel}")
    return 0


def cmd_migrate_hashes():
    """One-time backfill for entries recorded before this rewrite (they have
    {sha, date, cleanCount} but no {hash}). For each, hash the file's
    content AS IT WAS AT THE RECORDED SHA (`git show sha:path`) — not the
    current working-tree copy, which may have already drifted since. An
    entry whose sha no longer resolves is left without a hash, which
    `clean_state` correctly reads as DIRTY ("needs re-verification"), the
    same outcome the pre-rewrite tool gave for "recorded sha not found".
    Safe to run more than once: an entry that already has a hash is
    skipped, never re-derived."""
    data = load()
    todo = {rel: entry for rel, entry in data.items() if not entry.get("hash")}
    if not todo:
        print("Nothing to migrate — every entry already carries a hash.")
        return 0
    print(f"Migrating {len(todo)} entr{'y' if len(todo) == 1 else 'ies'} without a recorded hash...")
    migrated, unresolvable = 0, 0
    for rel, entry in todo.items():
        sha = entry.get("sha")
        if not sha or sha == "unknown":
            unresolvable += 1
            continue
        r = git_bytes(["show", "%s:%s" % (sha, rel)])
        if r.returncode != 0:
            unresolvable += 1
            print(f"  UNRESOLVABLE  {rel}  (sha {sha} no longer resolves for this path — stays DIRTY until re-reviewed)")
            continue
        h = hashlib.sha256(r.stdout).hexdigest()
        entry["hash"] = h
        migrated += 1
    if migrated:
        with locked():
            # Reload under the lock in case another writer landed a change
            # while this ran (a bulk migration is the one case here slow
            # enough for that to matter) — merge our new hashes into
            # whatever is current rather than clobbering it.
            fresh = load()
            for rel, entry in todo.items():
                if entry.get("hash") and rel in fresh and not fresh[rel].get("hash"):
                    fresh[rel]["hash"] = entry["hash"]
            save(fresh)
    print(f"Migrated {migrated}, left {unresolvable} unresolvable (will read DIRTY until re-reviewed).")
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

    p_list = sub.add_parser("list", help="show every recorded entry and its current state")
    p_list.add_argument("--show-untracked", action="store_true",
                        help="also list src/*.py|.cs|.xml files with NO entry at all - "
                             "DIRTY by default but invisible to the recorded-entries report")
    sub.add_parser("migrate-hashes", help="one-time backfill of {hash} onto pre-rewrite entries")

    p_prune = sub.add_parser("prune", help="drop entries for paths deleted or moved with no new entry")
    p_prune.add_argument("--apply", action="store_true", help="without this, only reports what would be dropped")

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
        sys.exit(cmd_list(args.show_untracked))
    elif args.cmd == "migrate-hashes":
        sys.exit(cmd_migrate_hashes())
    elif args.cmd == "prune":
        rc = cmd_prune(args.apply)
        if rc == 0 and args.apply:
            _trigger_health_rebuild()
        sys.exit(rc)


if __name__ == "__main__":
    main()
