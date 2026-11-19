# RIMMANDRAKE_RENAME_SEVEN_WORK_DIRS_STILL_NAMED_FOR_LOOPS

## spec

Kept in place on 2026-11-19 because live code reads them (the other 87 era-named entries moved to
`D:\ClaudeWork\retired-trees\rimmandrake_eras_20261119\`, see its MANIFEST.md): `ralph_graffiti` (Graffiti
`art_source/manifest.py`, `stage_colony.py`, `Utils/running_now.py`), `ralph_gss` (GSS `northstar/colony_scene.py`,
`gravship_scene.py`), `ralph_pyrelands` (`Pyrelands/play.py`), `ralph_sim` (`Utils/sim/loop_sim.py`, `RM_RALPH_SIM_OUT`),
`relentless_agent` (`rimflow/seed_trust.py` `RM_SEEDS_PRIVATE`, `rimflow/run_rules.json`), `relentless_progress`
(`run_rules.json`), `relentless` (`FlowWorks/art_source/PumpOblique/README.md`). Do: move each to a name for what it
holds and repoint its readers in the same commit (Pyrelands and GSS readers are mod code: Pyrelands is the advancing biome
mod, so its proof scripts must still find their shots).

Found by `RIMMANDRAKE_FINISH_RETIRED_ERA_REMAINS_TWENTY_ONE_NO_TICKETS` (2026-11-19, BENCH); index: `design/RimMandrake/retired_eras_index_2026-11-18.md`.

## verify

Acceptance test, run from the repo root:

    git grep -l -E 'rimmandrake(/|\\)+(ralph_(graffiti|gss|pyrelands|sim)|relentless_agent|relentless_progress|relentless)([/"\\ ]|$)' -- src

prints nothing and exits 1 once done. Watched failing 2026-11-19 BENCH at `fbdf50a5b2`: 7 files, exit 0.

## criteria

- A1: no file under src/ names one of the seven dirs (the grep above).
- A2: each moved dir exists under its new name with its contents, and the old name is absent.

## refs

file: src/RimMandrake/rimflow/seed_trust.py
file: src/RimMandrake/Utils/sim/loop_sim.py
file: src/RimMandrake/Pyrelands/play.py
