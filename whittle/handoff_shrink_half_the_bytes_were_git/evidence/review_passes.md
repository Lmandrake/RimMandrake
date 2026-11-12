# Full-file reviews of the item's code, 2026-11-11 (round 3 of this Whittle)

The last judge wrote that all four files were DIRTY under `code_review_status.py`: no full-file review had passed them.
This round ran the reviews. Each one was a fresh Opus subagent (rm-builder, briefed read-only) that had not written the
code. It read the files in full, ran the selftests, and probed the live ledger and the handoff corpus. Every finding
below was fixed, and each fix has a selftest check that the matching mutation turns red (`mutations.txt`).

## Pass 1, at 71d5e39efb: `ledger_state.py` + `selftest_ledger_state.py`
- **An owner `rimflow wait --until` was never shown.** A waiting item read as plain `doing` under an earlier NEXT.
  Fixed: rows say `WAITS until <date>: <reason>`.
- **The selftest had a date bomb.** It hard-wired `(NEXT 11-`, so it would fail from 2026-12-01. Fixed: the month is read from today.
- **A trailing empty NEXT threw the real one away.** `NEXT: x. Then a NEXT time:` gave no NEXT. Fixed: the last non-empty match is kept.
- **A lease end showed no date.** `lease to 02:00 PST` was really tomorrow. Fixed: it reads `lease to 11-12 02:00 PST`.
- **Width was counted in characters.** A CJK line ran to about 240 columns. Fixed: width is counted in terminal columns.
- **A comment was false.** It claimed RELENTLESS folds to BENCH. Fixed: the comment now says only CONDUCTOR does.

## Pass 1, at 71d5e39efb: `handoff.py`
- **POINTER STATUS took an item's last state verb as its state.** I compared it with `model.replay` over the live ledger:
  - 132 open items were shown as "CLOSED -- do NOT act", e.g. one reopened by `live --result broken`.
  - 744 done items were shown as open, e.g. ones ended by `implemented` plus a `verify` pass.
  - 24 unblocked items were shown as BLOCKED.

  Fixed: it now reads `model.replay`. Lesson filed: `infrastructure/state/lessons/20261112T064015Z-*`.
- **`since_handoff` imported `ledger_state` unguarded,** so the wake crashed if it could not load. Fixed: the pointers
  print UNMEASURED and the wake still finishes.
- **The wake view lost real text in three ways.** Fixed: sections are kept by keyword, fence-aware, and the uncommitted
  cut applies only in the game section.
  - It matched headings by exact prefix, so it dropped `## Half-done` and `## Game and bridge state` (both in the corpus).
  - It cut at any `Uncommitted` line in any section.
  - It split sections on a `## ` line inside a code fence.

## Pass 2, at b3d2584b66: all four files
- **Pointer ids were read from the whole handoff, including the filed and closed lists the view hides.**
  - On `BENCH_REBOOT_HANDOFF_202611111141.md` this printed "open pointers: 7 — pick each up" for items the reader
    could not see, one of them another seat's.
  - Fixed: ids come from the printed view only, and an open pointer owned by another seat says so (`open (built, CODEX_…'s)`).
- **`CONDUCTOR_HANDOFF_*` files were invisible to a BENCH wake.** Fixed: `handoff_files` folds the alias.
- **A superseded pointer did not name its successor.** Fixed.
- `ledger_state.py`: no significant findings. Marked CLEAN at 83657d580e.

## Pass 3, at 83657d580e: `handoff.py` + both selftests
- **`seat()` did not fold `RIMFLOW_SEAT=Conductor` to BENCH,** as rimflow does. A handoff written that way found 0 of
  BENCH's 235 started items and never matched the bridge holder. Fixed, with a selftest.
- **A supersede chain was followed only one link.** It said "B is SUPERSEDED too, do NOT act" when C at the end was open.
  Fixed: the chain is walked to its end, with a loop guard.
- **One UNMEASURED check could not fail** (the id was in the view anyway). Fixed: it reads the UNMEASURED line itself.

## Pass 4, at ea37fc5d2c: the seat fold's reach across every `seat()` caller, and the chain walk
NO SIGNIFICANT FINDINGS. It checked every `seat()` caller:
- the handoff filename and `follows` link;
- the window and emptiness checks, and `open_this_window`;
- the bridge check `own_hold`, which the fold now lets fire;
- `--check`, `--wake`, `ledger_state.write`, and `require_worker_seat` (BENCH is still refused);
- `--harvest` and `--cull`, which never call `seat()`.

It also found that `_canonical` cannot recurse and does not crash on a temp or missing ledger, and that `_successor`
stops on A→B→A, on A→A and on a missing id.

`ledger_state.py` is CLEAN at 83657d580e. `handoff.py` and the two selftests changed after pass 2. Pass 3 found the
two defects above, and pass 4, on the code after their fix, found nothing more. The files are not yet marked clean:
that is a `code_review_status.py mark-clean` act, owed with the close.

## Pass 5, at ea37fc5d2c: a full-file review of `handoff.py`, `selftest_handoff.py` and `selftest_ledger_state.py`
The blind judge asked for this: a full-file review at the current content, since pass 4 had been a focused one.
- **`selftest_handoff.py` and `selftest_ledger_state.py`: CLEAN.**
- **`handoff.py`: one finding, the same cause on the write side.**
  - `open_this_window`, the `--check` gate ("started this window and still open"), read an item's last lifecycle verb.
  - The "Closed since" and "Filed and still open" lists in `build()` did the same.
  - Measured for BENCH since 2026-11-01: the gate listed 146 items, 63 of them already done by `implemented` + `verify`
    with no `close`. An item unblocked with no fresh `start` escaped the gate.
  - Fixed at 7149527f48: both read `model.replay`. The gate now lists 30 items, none of them done.
  - Selftest cases cover "done by implemented + verify pass", "unblocked with no restart" and "a plain claim", and the
    matching mutation (the gate ignores state) turns red.
