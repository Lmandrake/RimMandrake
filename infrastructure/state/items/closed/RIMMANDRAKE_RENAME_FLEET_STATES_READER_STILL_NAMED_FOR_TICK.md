# RIMMANDRAKE_RENAME_FLEET_STATES_READER_STILL_NAMED_FOR_TICK

## spec

`src/RimMandrake/Utils/fleet_mods.py` `relentless_states` reads `store/items/*/state.json` and is called by
`ledger_state.py`, `maturation_now.py` and `fleet_mods.py`: live code, retired name. Rename it for what it reads (for
example `run_store_states`) with every caller and test in one commit.

Found by `RIMMANDRAKE_FINISH_RETIRED_ERA_REMAINS_TWENTY_ONE_NO_TICKETS` (2026-11-19, BENCH); index: `design/RimMandrake/retired_eras_index_2026-11-18.md`.

## verify

Acceptance test, run from the repo root:

    git grep -n relentless_states -- src

prints nothing and exits 1 once done. Watched failing 2026-11-19 BENCH at `fbdf50a5b2`: 6 files, exit 0. Plus the
callers' selftests green.

## criteria

- A1: no file under src/ names `relentless_states` (the grep above).
- A2: `maturation_now.py` still shows the same per-mod states (its selftest).

## refs

file: src/RimMandrake/Utils/fleet_mods.py
