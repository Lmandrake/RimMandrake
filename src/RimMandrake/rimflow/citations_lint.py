#!/usr/bin/env python3
"""rimflow.citations_lint -- DETERMINISM_ASSESSMENT.md SS8 (C6): a doc may not
cite a closed item as still live.

THE DEFECT
==========
An agent notices a stale gate one instance at a time, usually after acting on
it. `NAMING_SCHEME_EXECUTION_1` closed 2026-08-31 at `54a8e28d` and was still
cited as a live blocker 16 days later, which is why FlowWorks kept shipping
under its dead pre-rename packageId. Nothing walked the WHOLE repo joining
"every item id a doc names" against "what the ledger actually says that item
is" -- until now.

THE FIX
=======
`rimflow lint --citations` -- offline, reads `model.replay()` for item state
and `git ls-files` for the corpus. Two severities, per the spec:

  - STATE_LIE (red)  -- a line asserting a LIVE state for a TERMINAL item
    (`| open |`, `| doing |`, "still open", "open item"). High precision,
    cheap to fix. Gates the CLI's exit code.
  - STALE_GATE (orange) -- gate language ("blocked by", "waits on", "until",
    "do not", "ahead of", "pending", "gated on", "deferred to") within one
    line of a terminal-item citation, with no closure language ("closed",
    "done", "landed", "superseded", checkmark, a hex sha) nearby. Report
    only -- too noisy to gate, and "whether a gate is genuinely stale" is a
    judgement call `doctor.py`'s own precedent (SS8) says only reading
    settles.

Escape hatch, same shape as `walklint-ok` / `canon-ok`:

    <!-- citation-ok: reason -->

on the flagged line or the line immediately above suppresses BOTH classes
for that line -- a doc legitimately recording history ("X closed, replacing
the gate that used to block Y") would otherwise light up as its own subject.

WHAT THIS CANNOT CAPTURE (SS8's own list, restated so the CLI output can
point at it rather than silently doing less than it claims):
  - whether a gate is genuinely stale even after its item closed;
  - a gate cited by DESCRIPTION rather than by id;
  - whether the fix is deletion or a rewrite;
  - an item with no ledger entry at all (legacy B*/C*/W* ids) -- reported as
    UNKNOWN, never folded into "clean".
"""
import os
import re
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import model  # noqa: E402

ROOT = model.ROOT

TERMINAL = ("done", "dropped", "superseded")

# SS8: "every tracked .md|.txt|.yml file outside Transient/, state/ledger/ and
# state/queue/". Transient/ is gitignored (cmd_sweep's own note) so it never
# reaches `git ls-files` anyway; excluded here in words, not just by absence.
EXCLUDE_PREFIXES = (
    "Transient/",
    "infrastructure/state/ledger/",
    "infrastructure/state/queue/",
)
TEXT_EXTS = (".md", ".txt", ".yml")

# THREE_UPPER_SNAKE_WORDS_# (CLAUDE.md, "Queue items are NAMED, not numbered")
# -- at least two underscore-joined uppercase words then a trailing number.
_ID_RE = re.compile(r"\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+_\d+\b")

_STATE_LIE_RE = re.compile(r"\|\s*(?:open|doing)\s*\||still open|open item", re.I)

_GATE_RE = re.compile(
    r"blocked by|waits on|\buntil\b|\bdo not\b|ahead of|\bpending\b|"
    r"gated on|deferred to", re.I)
_CLOSURE_RE = re.compile(
    r"\bclosed\b|\bdone\b|\blanded\b|\bsuperseded\b|✅|`?[0-9a-f]{7,40}`?",
    re.I)

_ESCAPE_RE = re.compile(r"<!--\s*citation-ok:\s*.+?-->")


def tracked_files(root=None):
    """Every tracked .md|.txt|.yml path (repo-relative), minus the three
    excluded prefixes. Never raises: a `git` failure yields an empty corpus,
    which `main()` reports as UNMEASURED rather than a clean sweep."""
    root = root or ROOT
    try:
        out = subprocess.check_output(
            ("git", "-C", root, "ls-files"),
            stderr=subprocess.DEVNULL, timeout=30).decode("utf-8", "replace")
    except (subprocess.CalledProcessError, OSError, subprocess.TimeoutExpired):
        return []
    files = []
    for rel in out.splitlines():
        if not rel.endswith(TEXT_EXTS):
            continue
        if any(rel.startswith(p) for p in EXCLUDE_PREFIXES):
            continue
        files.append(rel)
    return files


def _escaped_lines(lines):
    escaped = set()
    for i, line in enumerate(lines, start=1):
        if _ESCAPE_RE.search(line):
            escaped.add(i)
            escaped.add(i + 1)
    return escaped


def scan(root=None, world=None, files=None):
    """The whole sweep. Returns (state_lies, stale_gates, unknown, counts).

    state_lies / stale_gates: [(file, line_no, item_id, line_text), ...]
    unknown: [(file, line_no, item_id)] -- a cited id absent from the ledger
    entirely (legacy pre-rimflow ids). Never folded into "clean" (SS8).
    counts: {"files", "items", "terminal_items", "citations"} -- the
    positive-count facts a selftest asserts, never a threshold on the finding
    counts themselves (same discipline as walklint/floor, CLAUDE.md's
    "a count that is conveniently round is a query bug until proven
    otherwise").
    """
    root = root or ROOT
    if world is None:
        world = model.replay()
    terminal_ids = {iid for iid, item in world.items.items()
                    if item.state in TERMINAL}
    known_ids = set(world.items.keys())

    if files is None:
        files = tracked_files(root)

    state_lies, stale_gates, unknown = [], [], []
    n_citations = 0
    for rel in files:
        full = os.path.join(root, rel)
        try:
            with open(full, "r", encoding="utf-8", errors="replace") as fh:
                lines = fh.read().splitlines()
        except OSError:
            continue
        escaped = _escaped_lines(lines)
        for i, line in enumerate(lines, start=1):
            if i in escaped:
                continue
            for m in _ID_RE.finditer(line):
                token = m.group(0)
                n_citations += 1
                if token not in known_ids:
                    # No ledger entry at all -- a legacy B*/C*/W* id, or a
                    # token that merely matches the shape. Never folded into
                    # "clean" (SS8's own instruction).
                    unknown.append((rel, i, token))
                    continue
                if token not in terminal_ids:
                    continue  # a live item cited live is correct, not a finding
                if _STATE_LIE_RE.search(line):
                    state_lies.append((rel, i, token, line.strip()))
                    continue
                window = "\n".join(lines[max(0, i - 2):i + 1])
                if _GATE_RE.search(window) and not _CLOSURE_RE.search(window):
                    stale_gates.append((rel, i, token, line.strip()))

    counts = {"files": len(files), "items": len(world.items),
             "terminal_items": len(terminal_ids), "citations": n_citations}
    return state_lies, stale_gates, unknown, counts


def main(argv=None):
    state_lies, stale_gates, unknown, counts = scan()
    print("rimflow lint --citations: %d files scanned, %d items known "
          "(%d terminal), %d citations found"
          % (counts["files"], counts["items"], counts["terminal_items"],
             counts["citations"]))
    if not counts["files"] or not counts["items"]:
        print("UNMEASURED: `git ls-files` or the ledger replay came back "
              "empty -- this is a query bug, not a clean repo. Refusing to "
              "report zero findings.")
        return 2

    if state_lies:
        print("\n\U0001F534 STATE_LIE -- asserts a LIVE state for a "
              "terminal item (%d):" % len(state_lies))
        for rel, ln, iid, text in state_lies:
            print("  %s:%d  %s\n    %s" % (rel, ln, iid, text))

    if stale_gates:
        print("\n\U0001F7E0 STALE_GATE -- gate language near a terminal "
              "item, no closure marker nearby (%d, report only):" % len(stale_gates))
        for rel, ln, iid, text in stale_gates:
            print("  %s:%d  %s\n    %s" % (rel, ln, iid, text))

    if unknown:
        print("\n❓ UNKNOWN -- cited id has no ledger entry at all "
              "(likely legacy B*/C*/W*; never counted as clean) (%d):"
              % len(unknown))
        for rel, ln, iid in unknown:
            print("  %s:%d  %s" % (rel, ln, iid))

    print("\n%d STATE_LIE (gates the exit code), %d STALE_GATE (report "
         "only), %d UNKNOWN." % (len(state_lies), len(stale_gates), len(unknown)))
    return 1 if state_lies else 0


if __name__ == "__main__":
    sys.exit(main())
