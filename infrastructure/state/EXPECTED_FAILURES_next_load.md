# Decision strings — load of 2026-09-20, BENCH

Written BEFORE launch. A signature invented after reading the log is a story
that fits, not evidence.

**Item riding the load:** `DESERT_TABLES_DEPLOYED_AHEAD_OF_SPECIES_1` — deploy
SWBestiary (defs + `RimMandrakeBeastMechanicsRSW.dll`), lift both biome-table
holds, prove the 18 previously-dangling refs resolve.

**Tier:** `fish` (`modset_builder.py --tier fish`) — BRIDGE + `mandrake.rut.patches`
+ `mandrake.rsw.swbestiary`, dependency-closed, all five DLC per the 2026-09-19
ruling. Chosen because it is exactly the two mods whose interaction is in question.

**Baseline:** the pre-launch `Player.log` is copied to
`Transient/Player.log.pre_swbestiary_deploy_2026-09-20`. Every count below is
against that copy, not against memory.

## EXPECTED ABSENT — any hit is a failure

| string | means |
|---|---|
| `Could not resolve cross-reference` naming any of the 18 | the deploy did not fix it |
| `RSW_Sandstrider`, `RSW_Cindermite`, `RSW_Spineroller`, `RSW_Sandhorn`, `RSW_Dunestalker`, `RSW_Ferroclaw`, `RSW_Sandmaw`, `RSW_Tuskcoil`, `RSW_Stareling`, `RSW_Voltmaw`, `RSW_Dunegrass`, `RSW_Plant_Chakroot_Wild`, `RSW_Plant_HubbaGourd_Wild`, `RSW_VellaraBloom`, `RSW_SweetbarkTree`, `RSW_Plant_Bloddle` — in ANY error line | the 18 names, verbatim |
| `Recovered from incompatible or corrupted mods` | assembly load failed; see §10, relaunch via Steam |
| `TypeLoadException` | the new DLL collides with a Harmony/VEF version |
| `Could not find type` naming `RimMandrake.StarWars.SWBestiary.*` | the DLL did not deploy, or did not load |
| `defined more than once` | the dedup regressed |

## EXPECTED PRESENT — absence of these is ALSO a failure

🔑 A no-op logs nothing, so "zero errors" alone does not prove the deploy landed.

| string | means |
|---|---|
| `Bridge token:` | the load is up. **Poll THIS, never JawaBench's ready line** — that one is lazy and only appears on the first tool call |
| `RimMandrakeBeastMechanicsRSW` in the loaded-assemblies lines | the new DLL is actually in the game |

## POSITIVE CHECK — the thing the log cannot tell me

Via the bridge once up, `jawa/get_defs` (or equivalent) for **all 18 names**.
**All 18 must resolve.** This is the real verdict; the log only says nothing
screamed.

Second: `RSW_Ferroclaw`, `RSW_Voltmaw`, `RSW_Cindermite` must each still carry
their comp from the new assembly. A missing comp type discards the whole def
**silently** — so a def that resolves is not proof its comp did.

## Ride-along, free (config class, no attribution risk)

- `Config error in` sweep across the whole load — `Def.ConfigErrors()` catches
  dead pawnkinds, bad `forcedMiss` and out-of-order thought stages that offline
  `validate_patch.py` cannot see.
- Full `harvest_log.py` pass, not just my own strings.

## Restore

🔴 `modset_builder.py --restore` before the owner plays. Leaving his machine on
the `fish` tier is the one unacceptable outcome.
