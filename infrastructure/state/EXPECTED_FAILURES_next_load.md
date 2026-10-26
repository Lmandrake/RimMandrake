# Decision strings — live round 6 (BENCH), 2026-10-26

Written BEFORE launch per `rimworld-load-round` §2/§3. Supersedes the Scald round's
strings (that load ran; its file is spent).

**List:** Archmagi full list, 321 active (live ModsConfig == `ModsConfig.FULL.LATEST.xml`,
parsed). Deployed from origin/main 423564d24a.

## Load verdict
- READY: `Bridge token:` in the NEW Player.log (launch_ready.py receipt).
- DEAD: `Resetting mods config and trying again`, `Recovered from incompatible or corrupted mods`,
  `Caught exception while loading play data`. On any of these, read the FIRST exception.

## Five assemblies ride this load — one signature each
| assembly | sha | expected-present | fails as |
|---|---|---|---|
| RimMandrakeFlowWorks.dll | d1430b9b46 | `[FlowWorks] hose essential patches:` | TypeLoad / Harmony error naming `RimMandrake.FlowWorks.Hose`; `HoseMath` / `RM_MapComponent_Hoses` in a stack |
| RimMandrakeGimmeSomeSlack.dll | 2987f99d6e | `[GimmeSomeSlack] targets:` | exception naming `RimMandrake.GimmeSomeSlack` (CordBuilder, SectionLayer_RM_MessyCords) |
| RimMandrakeColdStorage.dll | 287d027b9f | `[RimMandrake.ColdStorage] Harmony: patched N, missing 0` (N >= 10; round 5 read 10) | `missing` > 0, or `Could not find type named RimMandrake.ColdStorage.*` (CompEncased, RecipeWorker_Encase) |
| RimStarWarsCuisine.dll | 287d027b9f | no Config error for `RSW_Carbon*` defs | `Config error in RSW_Carbon*`, cross-ref errors from RSW_CarbonFreezing.xml / RSW_ColdStorageSeals.xml / RSW_RakatanStasisLadder.xml |
| RimMandrake.TheSump.dll (biomes compose) | origin HEAD | RM_TarSealing defs load with no Config error | exception naming `RimMandrake.TheSump`; `Config error in RM_Tar*` |

Silence is necessary, not sufficient: each row's expected-present string must be seen.
