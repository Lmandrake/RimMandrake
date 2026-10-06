# Belt batch C# review — 2026-10-06

Scope: new C# from 598dec613 + db013a05e. Full-file review, real bugs only. Engine facts checked in RimSage
(CompAnalyzable, CompStudiable, CompPowerTrader, PowerNet, FleeUtility, FloatMenuOptionProvider_FromThing).

| file | verdict | note |
|---|---|---|
| CreatureBehaviors/Source/RM_CompTetherPull.cs | FIXED | rescue pull yanked downed colonists out of beds |
| CreatureBehaviors/Source/RM_Building_TractionLance.cs | FIXED | boosted power draw stuck after a brownout mid-reel |
| CreatureBehaviors/Source/RM_CompResearchSpecimens.cs | CLEAN | |
| CreatureBehaviors/Source/RM_HediffComp_AggroSeverity.cs | CLEAN | |
| EnvironmentalHazards/Source/RM_FoundTechStudy.cs | CLEAN | Refresh overrides studyEnabled, but showToggleGizmo is off on both users, so no player toggle is overridden |
| Webwork/Source/RM_UrravethRemains.cs | CLEAN | |
| Webwork/Source/RM_UrravethProof.cs | CLEAN | |
| Greentide/Source/RM_StellockLace.cs | CLEAN | |
| Greentide/Source/RM_ThurrockAuraApplier.cs | CLEAN | aura comp reads Props.tickIntervalTicks at each reset, so live writes take effect |
| RustCathedral/Source/RustCathedral/RM_CompBorehulkDrill.cs | CLEAN | |
| RustCathedral/Source/RustCathedral/RM_GenStep_BorehulkPlacement.cs | CLEAN | |
| RustCathedral/Source/RustCathedral/RM_JobGiver_BorehulkBackAway.cs | CLEAN | |

## Findings

1. **RM_CompTetherPull.FindTarget — rescue pulls patients out of bed.** The rescue condition was
   `friendlyPull && Downed && same faction && Humanlike`. A colonist recovering in a hospital bed is Downed, so
   any bed within range and line of sight was a target: the line dragged the patient off the bed cell by cell.
   Shared with the capstan (TheSump). Fix: `&& !p.InBed()`.
2. **RM_Building_TractionLance.ResetPower — stuck boosted draw.** Reel steps raise `PowerOutput` with the target's
   body size; Release/Snap reset it only `if (Power.PowerOn)`. If the net browns out mid-reel (likely, since the
   boost is the extra load), CompTick releases with "off" while PowerOn is false, so the boost stays. PowerNet then
   restarts the trader only when it can cover that boosted `EnergyOutputPerTick` (PowerNet.cs:238), and once it is
   back on it keeps drawing the boost until the next tether event. Fix: reset unconditionally.

Rebuilt CreatureBehaviors (winbuild, 0 warnings). The two fixed files stay DIRTY until they are committed and
reviewed again. The other 10 are marked clean.
