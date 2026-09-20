#!/usr/bin/env python3
"""Selftest for citations_lint.py (DETERMINISM_ASSESSMENT.md SS8, C6).

Deterministic and offline: builds a fixture doc corpus in a tempdir against a
fake, minimal World (never the real ledger, never `git ls-files`), matching
selftest_walklint.py's own fixture-not-real-repo discipline.

    python3 src/RimMandrake/Utils/../../rimflow/selftest_citations_lint.py
    python3 src/RimMandrake/rimflow/selftest_citations_lint.py
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import citations_lint  # noqa: E402

FAILED = []
TOTAL = [0]


def ok(cond, label, detail=""):
    TOTAL[0] += 1
    print("%-4s %s" % ("ok" if cond else "FAIL", label))
    if not cond:
        FAILED.append("%s  %s" % (label, detail))


class _FakeItem(object):
    def __init__(self, state):
        self.state = state


class _FakeWorld(object):
    def __init__(self, items):
        self.items = items


def _write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)


def _fixture():
    """Three items: one terminal (closed), one live, one referenced but never
    filed at all (legacy-shaped). Five docs, one per finding class plus a
    clean control and an escaped one."""
    world = _FakeWorld({
        "DONE_THING_1": _FakeItem("done"),
        "LIVE_THING_1": _FakeItem("doing"),
    })
    tmp = tempfile.mkdtemp()

    # STATE_LIE: a terminal item cited with a live-state table cell.
    _write(os.path.join(tmp, "state_lie.md"),
          "| `DONE_THING_1` | open | still needs a look |\n")

    # STALE_GATE: gate language near a terminal item, no closure marker.
    _write(os.path.join(tmp, "stale_gate.md"),
          "Do not touch this path until DONE_THING_1 lands.\n")

    # Legitimate provenance: a terminal item cited with closure language --
    # neither class should fire.
    _write(os.path.join(tmp, "clean_provenance.md"),
          "DONE_THING_1 closed at abc1234, see the commit for detail.\n")

    # A live item cited as open: correct, not a finding.
    _write(os.path.join(tmp, "live_ok.md"),
          "| `LIVE_THING_1` | open | still in flight |\n")

    # The escape hatch suppresses a real STATE_LIE line.
    _write(os.path.join(tmp, "escaped.md"),
          "<!-- citation-ok: recording history on purpose -->\n"
          "| `DONE_THING_1` | open | this used to be the state |\n")

    # A cited id with no ledger entry at all.
    _write(os.path.join(tmp, "unknown_id.md"),
          "See LEGACY_PRE_RIMFLOW_ID_9 for the old thread.\n")

    files = ["state_lie.md", "stale_gate.md", "clean_provenance.md",
            "live_ok.md", "escaped.md", "unknown_id.md"]
    return tmp, world, files


def main():
    tmp, world, files = _fixture()
    try:
        state_lies, stale_gates, unknown, counts = citations_lint.scan(
            root=tmp, world=world, files=files)

        ok(counts["files"] == len(files), "counts: files scanned matches the fixture",
          counts)
        ok(counts["items"] == 2, "counts: items known matches the fixture", counts)
        ok(counts["terminal_items"] == 1,
          "counts: exactly one terminal item in the fixture", counts)
        ok(counts["citations"] >= 1, "counts: at least one citation found (positive"
          " count, never a threshold)", counts)

        state_lie_files = {f for f, *_ in state_lies}
        ok(state_lie_files == {"state_lie.md"},
          "STATE_LIE fires on the live-state table cell, nowhere else",
          state_lie_files)

        stale_gate_files = {f for f, *_ in stale_gates}
        ok("stale_gate.md" in stale_gate_files,
          "STALE_GATE fires on gate language near a terminal citation",
          stale_gate_files)
        ok("clean_provenance.md" not in stale_gate_files,
          "STALE_GATE does not fire when closure language sits in the window",
          stale_gate_files)

        ok("live_ok.md" not in state_lie_files
          and "live_ok.md" not in stale_gate_files,
          "a LIVE item cited as open is not a finding at all")

        ok("escaped.md" not in state_lie_files,
          "the <!-- citation-ok: --> escape hatch suppresses a real finding")

        unknown_ids = {iid for _f, _ln, iid in unknown}
        ok("LEGACY_PRE_RIMFLOW_ID_9" in unknown_ids,
          "an id absent from the ledger is reported UNKNOWN, never folded "
          "into clean", unknown_ids)

        # The dangerous failure mode (SS8's own risk section, mirrored from
        # walklint): a corpus/ledger that comes back empty must never read
        # as a clean 0-finding sweep.
        empty_state_lies, empty_stale, empty_unknown, empty_counts = (
            citations_lint.scan(root=tmp, world=_FakeWorld({}), files=[]))
        ok(empty_counts["files"] == 0 and empty_counts["items"] == 0,
          "an empty corpus/ledger is visibly zero, not silently 'clean'",
          empty_counts)
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)

    passed = TOTAL[0] - len(FAILED)
    print("\nSELFTEST %s -- %d/%d passed"
         % ("FAILED" if FAILED else "OK", passed, TOTAL[0]))
    if FAILED:
        print("  failed: %s" % "; ".join(FAILED))
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
