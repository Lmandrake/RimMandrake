# DROID_DONOR_SAVE_COMPAT_REGRESSION_1

Caused by `DROID_RETIRE_DEPOT_ASIMOV_1` (commit `f6116f97`), discovered live 2026-09-09 ~20:20Z.
Sibling regression to `DOORSEXPANDED_SAVE_COMPAT_REGRESSION_1` — same root cause class,
different donors.

## spec
`DROID_RETIRE_DEPOT_ASIMOV_1` retired `Neronix17.Asimov`, `Neronix17.OuterRim.DroidDepot`,
and our own `mandrake.rsw.msedroidfix` after a correct, thorough whole-active-modlist
dependency check (0 other mods depended on them). `CANONICAL_ASHKARR_2026-09-09.rws` still
holds placed droid Things built from at least one of these donors' ThingDefs — a
Scribe-level (save-content) reference invisible to that check, same failure shape as the
doorsexpanded regression discovered ~10 minutes earlier tonight.

`rimworld/load_game` on the canonical save refused (`missing_mods`, 589→587 active,
all three confirmed genuinely absent from ModsConfig and the whole Workshop/local Mods
tree). The agent that found this correctly declined to force-load past it (unlike the
doorsexpanded case, which did force-load and killed the whole RimWorld process) —
no crash was reproduced for this one.

**Reverted in full** (~20:20-20:25Z): `src/RimStarWars/MSEDroidFix/*`,
`DroidFemaleTexture_Fix.xml`, `NoDroidManufacture.xml`, and the `DroidsAreMachines.xml`
Asimov half restored via git and redeployed; all three packageIds restored to
`ModsConfig.xml`. A real restart (process kill + Steam relaunch) is in progress to pick
up both this fix and the doorsexpanded one together.

## verify
```
PROVE   grep the canonical save's XML (rimworld-savegame skill tooling) for any
        Asimov/DroidDepot/MSEDroidFix-authored defName actually placed on the
        map/world
EXPECT  either zero placed instances (safe to re-attempt retirement, this time
        also checking the save) or a nonzero list of thing IDs/positions
        needing a real migration
LIES    "the mod-dependency check passed" says nothing about the save; only
        reading the save's own Scribe data settles this
```

## criteria
Either (a) the placed droid content in the canonical save is migrated to a surviving
def (Droidworks' own races, per the repointing this item's own C1/C2 predecessor work
already did for most kinds) and these three donors are retired for real with a clean
load proof, or (b) the owner rules they stay permanently. Either way,
`DROID_RETIRE_DEPOT_ASIMOV_1`'s own record should stop implying the retirement is
standing until one of these actually happens.

## Broader pattern worth an owner ruling
Two donor retirements tonight, both independently checked clean against the whole mod
stack, both broke the same live canonical save because of placed-object references no
mod-stack check can see. Before any further "retire this donor" item executes against
a save that has ever been played (not just a quicktest), it needs a save-content check
added to the standard discipline, not just the modlist dependency sweep. See
`[[donor-retirement-mod-check-not-save-check]]` memory for the generalized lesson.
