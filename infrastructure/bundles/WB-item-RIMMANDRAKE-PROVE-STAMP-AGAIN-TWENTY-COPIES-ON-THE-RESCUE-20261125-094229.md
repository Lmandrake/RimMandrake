# WB-item-RIMMANDRAKE-PROVE-STAMP-AGAIN-TWENTY-COPIES-ON-THE-RESCUE-20261125-094229

System: item:RIMMANDRAKE_PROVE_STAMP_AGAIN_TWENTY_COPIES_ON_THE_RESCUE (the live proof of stamp again, `src/RimMandrake/Utils/scene_repeats.py`).
State: ENDED, 2026-11-25 06:14 PST. Every member has an outcome.

## Members

| member | outcome | commit | live reading |
|---|---|---|---|
| `RIMMANDRAKE_PROVE_STAMP_AGAIN_TWENTY_COPIES_ON_THE_RESCUE` | done (list_effect tick, `c6d92875b3`) | `bc9ef8db56`, `4bf9ada762`, `8369f80e7a`, `caabdcd655` (fresh reader's R3 fix), `a0c64c660a` | ArchBig: R1 PASS (20 of 20, 90.5 s against 135.2 s for 3 singles), R2 PASS, R3 UNRUN (no mod has a digest hook) |

## Filed on the way

- `RIMMANDRAKE_GIVE_ONE_MOD_A_DIGEST_HOOK_SO_A_DIRTY_RESET_CAN_SHOW`: the remainder, row R3.
- `RIMMANDRAKE_FIX_STAGE_MAKE_WHEN_TERRAIN_DOES_NOT_READ_BACK_ON_NEW_TILE`: stage make refused on ArchSmall (619 cells did not read back).

## What the next context needs

- `DoctorRescue` is not directOrderable: the ordered rescue is `jawa/ordered_job Rescue` (victim, bed).
- Drafted rescuers stay on their stations; undrafted idle ones wandered 7 cells onto a neighbour's margin.
- A `jawa/set_work_priority` block in a copy's staging coincided with differing station digests (the line was not read).
- A claim from WSL is not seen across the python.exe to wsl.exe hop of `stage_map.py make`: hold the game with `game_lock.py run`.

## Context size

276k of a 1M window at the end (one group).
