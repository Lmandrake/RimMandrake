# RIMMANDRAKE_WIRE_STREAMS_GAME_STATE_OFF_A_FROZEN_SNAPSHOT

## spec

`src/RimMandrake/Utils/ops_core/streams.py` (run every pass by `rm-streams-collect.service`) takes two inputs from
files only the retired RimPulse daemon wrote, in `~/.local/state/rm-dashboard/`:

- the game state (`UP` / `DOWN` / `DRIVING` / `BATCH`) from the "rimworld" chip of `pulse_now.json`, a snapshot last
  written 2026-11-03 14:06 PST. Until 2026-11-19 it therefore reported a 16-day-old game state with no age on it.
  `RIMMANDRAKE_FINISH_RETIRED_ERA_REMAINS_TWENTY_ONE_NO_TICKETS` moved the dead file to
  `D:\ClaudeWork\retired-trees\rimmandrake_eras_20261119\`, so the reading is now `UNKNOWN`, "no pulse snapshot":
  true, but nothing measures the game state any more.
- the budget from `usage.json` (no writer since 2026-11-03; it reads "usage.json empty or stale", UNMEASURED).

Do: read the game state from a live source (`./game` bare measure, the `infrastructure/state/BRIDGE` mirror, or the
game-state ledger events) with its age, and the budget from `src/RimMandrake/Utils/account_usage.py`, or drop the
two readings from streams with a note in its output. Never a reading without its age.

## verify

Acceptance test (watched failing 2026-11-19 BENCH on `ed3b6ca7a5`: it printed lines 448 and 463, rc 0). Passes when
it prints nothing and exits 1 (1 check):

    git grep -n -E 'pulse_now\.json|STATE_DIR / "usage\.json"' -- src/RimMandrake/Utils/ops_core/streams.py

plus `python3 src/RimMandrake/Utils/ops_core/selftest_streams.py` (or the streams selftest that exists) green.

## criteria

- A1: streams reads neither `pulse_now.json` nor `rm-dashboard/usage.json` (the grep above is empty).
- A2: the game-state reading carries its source and age, and reads UNMEASURED when the source is older than 15 min.

## refs

file: src/RimMandrake/Utils/ops_core/streams.py
