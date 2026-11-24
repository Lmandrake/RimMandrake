# RIMMANDRAKE_SWEEP_STEVEDESKTOP_CLONES_CARRYING_LOOP_TREES

## spec

Read 2026-11-19 over ssh (BENCH): SteveDesktop's only era unit is `whittle-claude@.service`, masked (keep the mask); no
Windows scheduled task carries an era name. But its WSL home holds at least 20 era-named dirs: `~/.local/share/whittle-claude`
and `ralph/` and `whittle/` trees inside old clones (`~/rm/gameb`, `~/rm/flowworks`, `~/rm/gss`, `~/rm/claude-offline1..6`,
`~/rm/claude-fwlive`, `~/rm/codex-ht`). Those trees were deleted on main 2026-11-18; a clone that still has them is
behind or carries unlanded work. Do: for each clone, check for unpushed commits and dirty files (land or bundle any
work first, never discard it), then bring it to origin/main or retire the clone; move `~/.local/share/whittle-claude`
to a retired-trees folder on that machine with a manifest. A soak may be running there: check before touching its clone.

Found by `RIMMANDRAKE_FINISH_RETIRED_ERA_REMAINS_TWENTY_ONE_NO_TICKETS` (2026-11-19, BENCH); index: `design/RimMandrake/retired_eras_index_2026-11-18.md`.

## verify

Acceptance test, run from the repo root:

    ssh stevedesktop "wsl.exe -e bash -lc 'find ~ -maxdepth 3 -type d \( -iname \"*whittle*\" -o -iname \"ralph\" \) 2>/dev/null | wc -l'"

prints 0 once done. Watched failing 2026-11-19 BENCH: 20 or more (the listing was cut at 20).

## criteria

- A1: no clone on SteveDesktop carries a ralph/ or whittle/ tree, and whittle-claude state is moved (the count above is 0).
- A2: no unpushed work was lost: each clone's unpushed commits were landed or bundled first (listed on this item).

## refs

none: SteveDesktop disk, outside the repo
