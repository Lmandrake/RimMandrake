#!/usr/bin/env python3
"""whats_new.py — hand a seat the DELTA in its doctrine, not a re-read order.

WHY
===
A seat that has been running for hours has no idea that a peer appended a trap,
rewrote a rule in CLAUDE.md, or filed a new item at `infrastructure/state/queue/<SEAT>.md`. There is
no channel between the windows. The only remedy on offer used to be "go reread
the traps and the rules", which is a ~25k-token chore, so it gets skipped, and
the seat keeps acting on doctrine that moved underneath it.

This prints the DIFFERENCE instead: five-ish lines of added headings and commit
subjects, cheap enough that nothing is gained by skipping it. It is deliberately
NOT a diff viewer — a heading tells you *that* a rule moved and *where*, which
is all a decision to go read it needs.

INTERFACE
=========
    python3 src/RimMandrake/Utils/whats_new.py --seat CHECK                    # since CHECK last synced
    python3 src/RimMandrake/Utils/whats_new.py --seat CHECK --mark             # print, then record HEAD
    python3 src/RimMandrake/Utils/whats_new.py --seat CHECK --no-mark          # peek without advancing
    python3 src/RimMandrake/Utils/whats_new.py --seat CHECK --again            # re-show the last delta
    python3 src/RimMandrake/Utils/whats_new.py --all                         # every seat's staleness
    python3 src/RimMandrake/Utils/whats_new.py --seat CHECK --since <git-ref>  # override the marker

SYNC MARKER
===========
Per SEAT, never per session — sessions die every few hours, seats persist for the
life of the project. The marker is a commit SHA in

    .claude/session_roles/<SEAT>.sync

which is gitignored (see .gitignore), so it is machine-local like the role files
beside it. With no marker the tool falls back to a rolling 24-hour window and
says so, which is a useful default rather than an error: it self-freshens, so a
seat that never runs --mark still gets a sane answer forever.

Markers are per-seat PRECISELY SO THAT one seat reading a change does not consume
it for the other four. The failure this design avoids is the shared "news file"
that the first reader empties, leaving the other seats to find out from the
damage. Four readers, four bookmarks, one set of documents.

MARKER ADVANCE
==============
A delta that has been read should never be shown again — but a delta shown to a
seat that then DIED must be recoverable. Four seats were lost mid-turn on the
morning of 2026-08-13, so this is not hypothetical.

  * A `--seat` run ADVANCES the marker to HEAD by default. `--no-mark` peeks
    without advancing; `--mark` is the explicit synonym of the default.
  * The hook-injected delta advances too — injection into `additionalContext` is
    guaranteed delivery, so it genuinely has been read.
  * Every advance first copies the outgoing SHA to `<SEAT>.sync.prev`, and
    `--again` re-shows that delta. That is the escape hatch for a seat killed or
    compacted between seeing the delta and acting on it.
  * An "up to date" run does NOT advance — there is nothing to consume, and a
    no-op advance would overwrite `.sync.prev` and destroy the escape hatch.
  * `--all` NEVER advances anyone. It is REP observing other seats, not
    those seats reading anything.

EXIT CODE
=========
Always 0. This is informational and is wired into a session hook; it must never
gate anything or wedge a prompt.
"""
import argparse
import os
import re
import subprocess
import sys

# The doctrine set: files whose change a seat must not miss. Git pathspec magic
# `:(glob)` is required for `**` and to stop `*` crossing a `/`.
DOCTRINE = [
    "CLAUDE.md",
    ":(glob)infrastructure/agents/*.md",
    ":(glob)infrastructure/state/queue/*.md",
    ":(glob)skills/**/SKILL.md",
    ":(glob)skills/**/references/traps*.md",
    "infrastructure/state/V1.md",
    "infrastructure/state/V1_CHAIN.md",
    "infrastructure/DOC_BUDGET.md",
    # ⭐ Added 2026-08-21. A NEW TOOL was invisible here: this list watched only
    # prose, so `measure/` and its hook shipped in six commits and produced no
    # delta line for any seat. A capability nobody is told about loses to the
    # habit it was built to replace. BUILDABLE.md is where a seat publishes
    # "the stack can / cannot do X", so watching it announces new capability
    # generally, not just this one instance.
    "infrastructure/state/BUILDABLE.md",
]

EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
GIT_TIMEOUT = 8          # seconds; the hook cannot afford to hang on a slow mount
MAX_LINES = 25           # total output ceiling, per the tool's whole point
SEAT_RE = re.compile(r"[A-Z][A-Z0-9_]{1,15}")


def repo_root():
    """Walk up to the marker rather than counting directories.

    This counted two levels up, which was the repo root until the 2026-08-13
    restructure moved Utils/ to src/RimMandrake/Utils/. It then resolved to
    src/RimMandrake, the seat roster glob matched nothing, and `--all` printed a
    header with zero rows -- a missing input reported as an empty one. Anchor on a
    file that only the root has, so the next move cannot break it silently.
    """
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env:
        return env
    d = os.path.dirname(os.path.abspath(__file__))
    while True:
        if os.path.isfile(os.path.join(d, "CLAUDE.md")) and os.path.isdir(
            os.path.join(d, ".claude")
        ):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            raise SystemExit(
                "whats_new.py: could not locate the repo root (no CLAUDE.md + "
                ".claude above %s). Refusing to run rather than report an empty "
                "delta." % os.path.abspath(__file__)
            )
        d = parent


_GIT_CACHE = {}


def git(*args, timeout=GIT_TIMEOUT):
    """Run a git command. Returns stdout, or None on ANY failure. Never raises.

    Memoised for the life of the process. `--all` asks the same question once per
    seat, and four of five seats usually share a baseline, so the cache took that
    subcommand from 10.2s to about 3s on the WSL mount. Safe because the process
    is short-lived and nothing here writes to the repo.
    """
    if args in _GIT_CACHE:
        return _GIT_CACHE[args]
    try:
        proc = subprocess.run(
            ["git", "-C", repo_root(), *args],
            capture_output=True, text=True, timeout=timeout,
        )
    except (OSError, subprocess.SubprocessError):
        _GIT_CACHE[args] = None
        return None
    out = proc.stdout if proc.returncode == 0 else None
    _GIT_CACHE[args] = out
    return out


def resolve(ref):
    """Full SHA for `ref`, or None if it does not name a commit."""
    if not ref or not re.fullmatch(r"[A-Za-z0-9._/^~@{}-]{1,200}", ref):
        return None
    out = git("rev-parse", "--verify", "--quiet", ref + "^{commit}")
    return out.strip() if out and out.strip() else None


def marker_path(seat, prev=False):
    name = seat + (".sync.prev" if prev else ".sync")
    return os.path.join(repo_root(), ".claude", "session_roles", name)


def read_marker(seat, prev=False):
    try:
        with open(marker_path(seat, prev), "r", encoding="utf-8") as fh:
            return fh.read().strip().split()[0]
    except (OSError, IndexError):
        return None


def advance_marker(seat, sha):
    """Point <SEAT>.sync at `sha`, preserving the outgoing value in .sync.prev.

    The .prev write happens FIRST and its failure is not fatal: losing the escape
    hatch is worse than losing it silently, but far better than refusing to
    advance and re-showing the same delta forever.
    """
    old = read_marker(seat)
    try:
        os.makedirs(os.path.dirname(marker_path(seat)), exist_ok=True)
        if old:
            with open(marker_path(seat, prev=True), "w", encoding="utf-8") as fh:
                fh.write(old + "\n")
        with open(marker_path(seat), "w", encoding="utf-8") as fh:
            fh.write(sha + "\n")
        return True
    except OSError:
        return False


def day_ago_commit():
    """Last commit older than 24h — the fallback baseline when a seat has no marker."""
    out = git("rev-list", "-n", "1", "--before=24 hours ago", "HEAD")
    if out and out.strip():
        return out.strip()
    return EMPTY_TREE          # repo younger than a day: show everything


def short(sha):
    return "the beginning" if sha == EMPTY_TREE else sha[:7]


def changed_files(since):
    """Doctrine files touched in since..HEAD, as [(status, path)]."""
    out = git("diff", "--name-status", "--no-renames", f"{since}..HEAD", "--", *DOCTRINE)
    if not out:
        return []
    rows = []
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2:
            rows.append((parts[0][:1], parts[-1]))
    return rows


FENCE_RE = re.compile(r"^\s{0,3}(```|~~~)")
HEADING_RE = re.compile(r"^\s{0,3}(#{1,6})\s+(\S.*)$")

_BLOB_CACHE = {}


def prefetch_blobs(specs):
    """Load many `rev:path` blobs in ONE git process, into _BLOB_CACHE.

    Process spawns dominate on the WSL mount — roughly 0.15-0.3s each — and the
    naive shape here was two `git show`s per reported file, which put a seat's
    very first run (no marker, so a full 24h of a busy day) at ~6s and straight
    through the hook's timeout. `cat-file --batch` collapses those into one.

    Failure is not fatal: anything missing from the cache falls back to `git
    show` in headings_of, which is merely slower.
    """
    specs = [s for s in specs if s not in _BLOB_CACHE]
    if not specs:
        return
    try:
        proc = subprocess.run(
            ["git", "-C", repo_root(), "cat-file", "--batch"],
            input=("\n".join(specs) + "\n").encode(),   # binary: sizes are in BYTES
            capture_output=True, timeout=GIT_TIMEOUT,
        )
    except (OSError, subprocess.SubprocessError):
        return
    if proc.returncode != 0:
        return

    data, pos = proc.stdout, 0
    for spec in specs:
        nl = data.find(b"\n", pos)
        if nl < 0:
            return
        header = data[pos:nl].decode("utf-8", "replace").split()
        pos = nl + 1
        if len(header) < 3:                    # "<spec> missing"
            _BLOB_CACHE[spec] = None
            continue
        try:
            size = int(header[2])
        except ValueError:
            return
        _BLOB_CACHE[spec] = data[pos:pos + size].decode("utf-8", "replace")
        pos += size + 1                        # payload plus its trailing newline


def headings_of(rev, path):
    """Markdown headings in `path` at `rev`, in order. [] if it is not there.

    Fence-aware on purpose. These docs are full of shell blocks whose comments
    start with `#`, and a naive scan of the diff reported `# what is listed --
    activeMods ONLY` as a new rule. Parsing whole file versions rather than diff
    hunks is what makes the fence state knowable.
    """
    spec = f"{rev}:{path}"
    if spec in _BLOB_CACHE:
        out = _BLOB_CACHE[spec]
    else:
        out = git("show", spec)
    if not out:
        return []
    heads, in_fence = [], False
    for line in out.splitlines():
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = HEADING_RE.match(line)
        if m:
            heads.append(f"{m.group(1)} {re.sub(r'\s+', ' ', m.group(2)).strip()}")
    return heads


def added_headings(since, path):
    """Headings present at HEAD but not at `since` — added or reworded.

    A retitled heading reads as an addition, which is intended: either way the
    seat has to go look. A heading that merely MOVED is not reported, which is
    also intended — that is churn, not news.
    """
    before = set(headings_of(since, path))
    return [h for h in headings_of("HEAD", path) if h not in before]


def commit_subjects(since):
    out = git("log", "--format=%h %s", f"{since}..HEAD", "--", *DOCTRINE)
    return out.splitlines() if out else []


NOT_SEATS = {"POLICY", "HUMAN"}          # shared rules, and REP's inbox from everyone


def known_seats():
    """Seats are whatever has an identity file — the roster is the directory."""
    seats = set()
    for d in (os.path.join("infrastructure", "agents"),
              os.path.join("infrastructure", "state", "queue")):
        try:
            for name in os.listdir(os.path.join(repo_root(), d)):
                stem = name[:-3] if name.endswith(".md") else None
                if stem and SEAT_RE.fullmatch(stem) and stem not in NOT_SEATS:
                    seats.add(stem)
        except OSError:
            pass
    return sorted(seats)


def clip(text, width=88):
    return text if len(text) <= width else text[: width - 1] + "…"


def report(seat, since, note=None):
    """The seat-facing delta. Returns (lines, has_changes), capped at MAX_LINES.

    `has_changes` is what decides whether the marker advances: consuming a delta
    that does not exist would overwrite .sync.prev with the current SHA and throw
    away the only copy of the last real delta.
    """
    files = changed_files(since)
    subjects = commit_subjects(since)

    if not files and not subjects:
        # The note still prints here: "--again: no previous delta recorded"
        # explains an otherwise baffling "up to date" from an escape hatch.
        lines = [f"up to date ({short(since)})"]
        return (lines + ["   " + note] if note else lines), False

    mine = {f"infrastructure/state/queue/{seat}.md", f"infrastructure/agents/{seat}.md"}
    # A seat cares most about what was filed AT it, so its own queue and identity
    # sort first and carry the flag. Everything else keeps git's order.
    files.sort(key=lambda row: (row[1] not in mine, row[1]))

    head = [
        f"WHAT CHANGED for {seat} since {short(since)} "
        f"({len(subjects)} commit{'s' * (len(subjects) != 1)}, "
        f"{len(files)} doctrine file{'s' * (len(files) != 1)})"
    ]
    if note:
        head.append("   " + note)

    body, overflow = [], 0
    budget = MAX_LINES - len(head) - 2          # leave room for commits + tail note

    # Two lines is the cheapest a reported file can be, so nothing past
    # budget/2 files can possibly be printed and nothing past it is fetched.
    # "HEAD" literal, not a resolved sha: it must key the cache identically to
    # what headings_of() asks for, or every lookup misses and falls back.
    prefetch_blobs([f"{rev}:{path}"
                    for _, path in files[: max(1, budget // 2)]
                    for rev in (since, "HEAD")])
    for status, path in files:
        # Once the budget is spent, COUNT the rest without reading them. Heading
        # extraction is two `git show`s per file, and on the WSL mount a 28-file
        # day took 5.4s when every file was parsed and then thrown away.
        if len(body) >= budget:
            overflow += 1
            continue
        flag = "🔴 " if path in mine else "   "
        if status == "D":
            entry = [f"{flag}{path}  (DELETED)"]
        else:
            heads = added_headings(since, path)
            entry = [f"{flag}{path}"]
            entry += [f"      + {clip(h)}" for h in heads[:3]]
            if len(heads) > 3:
                entry.append(f"      + {len(heads) - 3} more headings")
            if not heads:
                entry[0] += "  (body changed, no new headings)"
        if len(body) + len(entry) <= budget:
            body += entry
        else:
            overflow += 1

    tail = []
    if subjects:
        tail.append("   commits: " + clip(" · ".join(s for s in subjects[:3]), 84))
    if overflow or len(subjects) > 3:
        tail.append(
            f"   +{overflow} more file{'s' * (overflow != 1)}, "
            f"see `git log --oneline {short(since)}..HEAD`"
        )
    return head + body + tail, True


def all_seats_report():
    lines = []
    head = resolve("HEAD")
    if not head:
        return ["whats_new: not a git repo (or git unavailable)"]
    lines.append(f"SEAT STALENESS at {short(head)}")
    for seat in known_seats():
        mark = read_marker(seat)
        sha = resolve(mark) if mark else None
        if not sha:
            state = "no marker (defaults to last 24h)" if not mark else f"BAD MARKER {mark[:12]}"
            sha = day_ago_commit()
        else:
            state = f"synced at {short(sha)}"
        n_commits = len(commit_subjects(sha))
        n_files = len(changed_files(sha))
        flag = "🔴" if n_files else "  "
        lines.append(
            f" {flag} {seat:<8} {state:<32} behind {n_commits} commit(s), {n_files} file(s)"
        )
    return lines


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="whats_new.py",
        description="Print the doctrine delta a seat has not seen yet.",
    )
    ap.add_argument("--seat", help="seat name, e.g. CHECK")
    ap.add_argument("--all", action="store_true",
                    help="every seat's staleness (for REP); advances nobody")

    advance = ap.add_mutually_exclusive_group()
    advance.add_argument("--mark", action="store_true",
                         help="record HEAD as this seat's sync point (the default)")
    advance.add_argument("--no-mark", dest="no_mark", action="store_true",
                         help="peek without advancing the sync marker")

    baseline = ap.add_mutually_exclusive_group()
    baseline.add_argument("--since", help="override the marker with any git ref")
    baseline.add_argument("--again", action="store_true",
                          help="re-show the last delta (from <SEAT>.sync.prev)")
    try:
        args = ap.parse_args(argv)
    except SystemExit:
        # argparse has already explained itself on stderr. Exit 0 regardless:
        # this tool is informational and must never be the thing that fails.
        return 0

    if args.all:
        print("\n".join(all_seats_report()))
        return 0

    if not args.seat:
        ap.print_usage(sys.stderr)
        print("whats_new: need --seat SEAT or --all", file=sys.stderr)
        return 0                                   # informational: never a gate

    seat = args.seat.strip().upper()
    if not SEAT_RE.fullmatch(seat):
        print(f"whats_new: '{args.seat}' is not a seat name", file=sys.stderr)
        return 0

    # Shape is not existence. --mark is the default, so a retired seat name
    # reaching this point writes it a fresh marker and the ghost comes back:
    # resuming any of the old session-role files used to do exactly that.
    roster = known_seats()
    if roster and seat not in roster:
        print(f"whats_new: '{seat}' is not a current seat ({', '.join(roster)})",
              file=sys.stderr)
        return 0

    head = resolve("HEAD")
    if not head:
        print("whats_new: not a git repo (or git unavailable)", file=sys.stderr)
        return 0

    # Baseline resolution, most specific first: --again, --since, then the seat's
    # marker, then a rolling 24h window. Anything unresolvable degrades to the
    # next rung with a note rather than an error — this never refuses to answer.
    note, since = None, None
    if args.again:
        prev = read_marker(seat, prev=True)
        since = resolve(prev) if prev else None
        if since:
            note = "--again: re-showing the delta from before the last advance"
        else:
            note = ("--again: no previous delta recorded" if not prev
                    else f"--again: {clip(prev, 12)} is not a ref")
    elif args.since:
        since = resolve(args.since)
        if not since:
            note = f"--since '{clip(args.since, 40)}' is not a ref"

    if since is None:
        mark = read_marker(seat)
        if mark:
            since = resolve(mark)
            if since is None:
                bad = f"sync marker {clip(mark, 12)} is not a ref"
                note = f"{note}; {bad}" if note else bad
            elif note:
                note += "; using this seat's sync marker"

    if since is None:
        since = day_ago_commit()
        note = (f"{note}; showing the last 24h" if note
                else "no sync marker — showing the last 24h")

    lines, has_changes = report(seat, since, note)
    print("\n".join(lines))

    # Advancing is the DEFAULT: a delta that has been printed has been read. The
    # three refusals are --no-mark (an explicit peek), --again (a re-read of an
    # already-consumed delta), and an empty delta (nothing to consume, and the
    # advance would destroy .sync.prev for no gain).
    if has_changes and not args.no_mark and not args.again and since != head:
        ok = advance_marker(seat, head)
        print(f"   marked {seat} synced at {short(head)} "
              f"(`--again` re-shows this)" if ok
              else "   could not write the sync marker")
    return 0


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:                       # noqa: BLE001 — deliberate
        # "Exit 0 always" is a contract, not an aspiration: this runs inside a
        # session hook, and a traceback here must not become the reason a seat
        # cannot start. Say what broke on stderr, then get out of the way.
        print(f"whats_new: {type(exc).__name__}: {exc}", file=sys.stderr)
    sys.exit(0)
