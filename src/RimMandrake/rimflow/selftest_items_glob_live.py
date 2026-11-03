#!/usr/bin/env python3
"""selftest_items_glob_live.py — `infrastructure/state/items/*.md` is the LIVE glob.

    python3 src/RimMandrake/rimflow/selftest_items_glob_live.py

LIVE_ITEM_GLOB_DRIFT_1 (2026-09-21): CHARTER.md documents "on close/drop/supersede
the prose moves to items/closed/<ID>.md" as an invariant every seat's sweep relies
on — but until this item, no code path actually did the move; `close`/`drop`/
`supersede` only ever wrote the ledger event. 79 of 270 files in `items/` had gone
terminal (done/dropped/superseded) with their prose never moved, plus 8 more with
no ledger row at all — 32% noise on the exact glob CLAUDE.md tells every seat to
walk for "what is still open".

`cli.py`'s `_move_prose_to_closed()` now performs the move on every close/drop/
supersede, which fixes the CAUSE. This test is the REGRESSION GUARD: it fails the
moment a file drifts back out of sync, whether the cause is a future code path
that skips the move, a hand `git mv` gone wrong, or a ledger event appended some
other way. It reads the REAL ledger and the REAL `items/` directory on purpose —
there is nothing to fake here, the invariant is about THIS repo's actual state,
not a fixture (compare selftest_cli.py's throwaway-ledger rule, which exists for
a different reason: not writing test noise into the real, append-only ledger).
This test never writes anything, so reading the real ledger is safe.

⚠️ One narrow, general exception: a COMPANION file for a still-live item, named
`<LIVE_ITEM_ID>.<suffix>.md` (e.g. a rename table
`<ID>.names.md` cited by the live `<ID>.md`). It carries no ledger row of
its own and never will — the parent item's row covers it. Recognised generically
(prefix before the first `.` must itself be a live item), not by a hardcoded
filename, so a second such companion file does not need this test edited.

⚠️ A glob of 0 files proves nothing. In a clone that is a FAIL. A blind checker's export has no .git and no items/
(walls.marker.tree_exclude): there the real-glob row reads UNMEASURED, never ok, and what still speaks for the night of
NIGHTLY_COP_FIX_RED_ATJKEB_FBYD is the ledger: both stems of 6489a12285 must keep a `file` row.
"""
import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from rimflow import model                                          # noqa: E402

TERMINAL = {"done", "dropped", "superseded"}
# 6489a12285 pushed these two with no row; the nightly of 2026-11-03T11:00Z went red on them
INCIDENT_STEMS = ("STATIC_CALL_THINGID_FIX_DIGIT_EATS_ITSELF", "TITAN_WALL_CRUSH_DIAGNOSE_WOOD_WALL_SHRUGS")


def verdict(stem, state):
    """-> None when items/<stem>.md belongs in the live glob of `state`, else why not.
    block_orphan_item_prose.py applies the same verdict at pre-push."""
    it = state.items.get(stem)
    if it is not None and it.state not in TERMINAL:
        return None
    # companion-file exception: <live-item-id>.<suffix>.md
    prefix = stem.split(".", 1)[0]
    parent = state.items.get(prefix) if prefix != stem and it is None else None
    if parent is not None and parent.state not in TERMINAL:
        return None
    if it is None:
        return "no ledger row at all"
    return "ledger state is %r (terminal) but prose is still in items/, not items/closed/" % it.state


def check(items_dir=None, events=None):
    """-> (ok_ids, bad) where bad is [(filename, reason)]. `items_dir` overrides
    `model.ITEMS` and `events` the ledger for the self-checks below — never for the real run."""
    items_dir = items_dir or model.ITEMS
    state = model.replay(model.read() if events is None else events)
    files = sorted(glob.glob(os.path.join(items_dir, "*.md")))
    ok, bad = [], []
    for f in files:
        stem = os.path.basename(f)[:-3]
        why = verdict(stem, state)
        if why:
            bad.append((stem, why))
        else:
            ok.append(stem)
    return ok, bad


def empty_glob_reading(items_dir, root):
    """-> what a glob of 0 files is worth: UNMEASURED only where items/ cannot be there at all, else FAIL."""
    if not os.path.isdir(items_dir) and not os.path.exists(os.path.join(root, ".git")):
        return "UNMEASURED"
    return "FAIL"


def rowless_stems(events):
    """-> the incident's stems with no `file` row among these events. A row outlives its item's close, so this holds for good."""
    filed = {e.get("id") for e in events if e.get("event") == "file"}
    return [s for s in INCIDENT_STEMS if s not in filed]


def main():
    failed = []
    rows = 3

    # --- the real repo, right now -------------------------------------------
    ok, bad = check()
    if bad:
        print("FAIL  live items/ glob has %d drifted file(s):" % len(bad))
        for stem, why in bad:
            print("        %s.md — %s" % (stem, why))
        failed.append("real_glob_is_clean")
    elif ok:
        print("ok    live items/ glob is clean (%d live files, 0 drifted)" % len(ok))
    elif empty_glob_reading(model.ITEMS, model.ROOT) == "UNMEASURED":
        print("UNMEASURED  real items/ glob: this export has no .git and no items/, so its 0 files say nothing")
        rows -= 1
    else:
        print("FAIL  live items/ glob has 0 files at %s: nothing was measured" % model.ITEMS)
        failed.append("real_glob_has_files")

    # --- the alarm's own red, read from the ledger: needs no items/ -----------
    events = model.read()
    missing = rowless_stems(events)
    rows += 1
    if missing:
        print("FAIL  the alarm's prose has no `file` row in the ledger: %s" % ", ".join(missing))
        failed.append("incident_stems_have_rows")
    else:
        print("ok    both stems of the alarm have a `file` row in the ledger")

    # --- the guard actually guards something: prove it on a deliberately ----
    # reintroduced drift, using the REAL ledger (read-only) but a THROWAWAY
    # items/ directory, so this never touches the real one.
    import tempfile
    with tempfile.TemporaryDirectory(prefix="rimflow_selftest_items_glob_") as tmp:
        state = model.replay(model.read())
        closed_id = next((iid for iid, it in state.items.items()
                           if it.state in TERMINAL), None)
        if closed_id is None:
            print("SKIP  no closed item exists in the real ledger to drift-test "
                  "with (should not happen — the ledger has thousands of events)")
        else:
            drifted = os.path.join(tmp, "%s.md" % closed_id)
            with open(drifted, "w", encoding="utf-8") as fh:
                fh.write("# %s\nreintroduced drift for a selftest\n" % closed_id)
            _, bad2 = check(items_dir=tmp)
            if bad2 and bad2[0][0] == closed_id:
                print("ok    a deliberately reintroduced drifted file (%s, "
                      "state=%s) is CAUGHT" % (closed_id, state.items[closed_id].state))
            else:
                print("FAIL  planting a closed item's prose (%s) in a fresh "
                      "items/ dir was NOT caught — the guard does not guard "
                      "anything" % closed_id)
                failed.append("guard_catches_reintroduced_drift")

        # and a clean file (a currently-live item) must NOT be flagged, in the
        # same throwaway dir, so the guard isn't just failing on everything.
        live_id = next((iid for iid, it in state.items.items()
                         if it.state not in TERMINAL), None)
        if live_id is not None:
            clean = os.path.join(tmp, "%s.md" % live_id)
            with open(clean, "w", encoding="utf-8") as fh:
                fh.write("# %s\n" % live_id)
            _, bad3 = check(items_dir=tmp)
            flagged = {stem for stem, _ in bad3}
            if live_id in flagged and live_id != closed_id:
                print("FAIL  a live item's own prose (%s) was wrongly flagged"
                      % live_id)
                failed.append("guard_does_not_false_positive_on_live_items")
            else:
                print("ok    a live item's prose is not falsely flagged")

    # --- the alarm's state replayed: its two files, with and without their rows ---
    rows += 3
    with tempfile.TemporaryDirectory(prefix="rimflow_selftest_items_incident_") as tmp:
        for stem in INCIDENT_STEMS:
            with open(os.path.join(tmp, "%s.md" % stem), "w", encoding="utf-8") as fh:
                fh.write("## spec\nx\n")
        rowless = [e for e in events if e.get("id") not in INCIDENT_STEMS]
        _, bad4 = check(items_dir=tmp, events=rowless)
        if sorted(bad4) == [(s, "no ledger row at all") for s in sorted(INCIDENT_STEMS)]:
            print("ok    with their rows gone, the alarm's two files are flagged, those two only")
        else:
            print("FAIL  the alarm's two files without rows were read as %s" % (bad4,))
            failed.append("incident_red_is_seen")
        state = model.replay(events)
        closed_since = sorted(s for s in INCIDENT_STEMS if s in state.items and state.items[s].state in TERMINAL)
        _, bad5 = check(items_dir=tmp, events=events)
        if sorted(stem for stem, _ in bad5) == closed_since:
            print("ok    with the real ledger, neither is flagged unless its item has since closed (%d closed)" % len(closed_since))
        else:
            print("FAIL  with the real ledger the alarm's two files read as %s" % (bad5,))
            failed.append("incident_green_on_real_ledger")

    # --- a glob of 0 files is never a clean glob ---------------------------------
    with tempfile.TemporaryDirectory(prefix="rimflow_selftest_items_empty_") as tmp:
        items = os.path.join(tmp, "items")
        export = empty_glob_reading(items, tmp)                  # no .git, no items/: the blind checker's box
        os.makedirs(items)
        export_with_dir = empty_glob_reading(items, tmp)
        os.makedirs(os.path.join(tmp, ".git"))
        clone = empty_glob_reading(items, tmp)
        os.rmdir(items)
        clone_no_dir = empty_glob_reading(items, tmp)
    if (export, export_with_dir, clone, clone_no_dir) == ("UNMEASURED", "FAIL", "FAIL", "FAIL"):
        print("ok    0 files is FAIL in a clone or beside an empty items/, UNMEASURED only in an export without it")
    else:
        print("FAIL  0 files read as %s" % ((export, export_with_dir, clone, clone_no_dir),))
        failed.append("empty_glob_is_never_ok")

    print()
    if failed:
        print("%d FAILED: %s" % (len(failed), ", ".join(failed)))
        sys.exit(1)
    print("%d/%d passed" % (rows, rows))


if __name__ == "__main__":
    main()
