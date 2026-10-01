# RIMPLACE_GENSTEP_NRE_1 — GenStep_RimplacePlan throws during map generation

Found 2026-10-01, FOUNDRY live session. Regenerating a quicktest map as RM_Stillsand (tile 97517, full list,
deployed commit `cc4bc992243`) logged `Error in GenStep: System.NullReferenceException` at
`RimMandrake.StructureInjections.GenStep_RimplacePlan.Generate` (IL offset 0x35), reached through
`GenStep_RandomSelector`. Map generation continued. The log is at
`Transient/livesession_20261001/Player.session.log`.

## criteria
- Regenerating a map on a biome that selects this genstep logs no exception from `GenStep_RimplacePlan`.
