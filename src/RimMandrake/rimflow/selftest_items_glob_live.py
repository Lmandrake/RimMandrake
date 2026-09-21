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
`<LIVE_ITEM_ID>.<suffix>.md` (e.g. `LANDMARK_NAMING_PASS_1.names.md`, a rename
table cited by the live `LANDMARK_NAMING_PASS_1.md`). It carries no ledger row of
its own and never will — the parent item's row covers it. Recognised generically
(prefix before the first `.` must itself be a live item), not by a hardcoded
filename, so a second such companion file does not need this test edited.
"""
import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from rimflow import model                                          # noqa: E402

TERMINAL = {"done", "dropped", "superseded"}


def check(items_dir=None):
    """-> (ok_ids, bad) where bad is [(filename, reason)]. `items_dir` overrides
    `model.ITEMS` for the self-check below — never for the real run."""
    items_dir = items_dir or model.ITEMS
    state = model.replay(model.read(model.EVENTS))
    files = sorted(glob.glob(os.path.join(items_dir, "*.md")))
    ok, bad = [], []
    for f in files:
        stem = os.path.basename(f)[:-3]
        it = state.items.get(stem)
        if it is not None and it.state not in TERMINAL:
            ok.append(stem)
            continue
        # companion-file exception: <live-item-id>.<suffix>.md
        prefix = stem.split(".", 1)[0]
        parent = state.items.get(prefix) if prefix != stem else None
        if parent is not None and parent.state not in TERMINAL:
            ok.append(stem)
            continue
        if it is None:
            bad.append((stem, "no ledger row at all"))
        else:
            bad.append((stem, "ledger state is %r (terminal) but prose is still "
                               "in items/, not items/closed/" % it.state))
    return ok, bad


def main():
    failed = []

    # --- the real repo, right now -------------------------------------------
    ok, bad = check()
    if bad:
        print("FAIL  live items/ glob has %d drifted file(s):" % len(bad))
        for stem, why in bad:
            print("        %s.md — %s" % (stem, why))
        failed.append("real_glob_is_clean")
    else:
        print("ok    live items/ glob is clean (%d live files, 0 drifted)" % len(ok))

    # --- the guard actually guards something: prove it on a deliberately ----
    # reintroduced drift, using the REAL ledger (read-only) but a THROWAWAY
    # items/ directory, so this never touches the real one.
    import tempfile
    with tempfile.TemporaryDirectory(prefix="rimflow_selftest_items_glob_") as tmp:
        state = model.replay(model.read(model.EVENTS))
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

    print()
    if failed:
        print("%d FAILED: %s" % (len(failed), ", ".join(failed)))
        sys.exit(1)
    print("3/3 passed" if len(failed) == 0 else "FAILED")


if __name__ == "__main__":
    main()
