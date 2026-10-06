# FlowWorks machinery art commission — 2026-10-05 (FOUNDRY agent A)

Owner 2026-10-05: *"commission all needed art so we can start reviewing more"*.

## Status
- ALL 23 jobs FILED (waves 1-3). The daemon HOLDS a derive_from job in pending/ until its parent has a verdict (artpiped `_derive_master_resolved`), so waves 2-3 run themselves as parents finish. If a parent FAILS, its child is released anyway and will need re-filing after a fixed parent.
- Art lists: `infrastructure/artpipe/art_lists/flowworks_machinery_art_wave{1,2,3}_2026-10-05.json`

## Existing art found (searched `artpipe_state.py find` x17 terms, done/_artsrc/pending/active/failed listings, Transient/*.decisions.json, art_lists)
- Nothing for any machinery subject. Sanity probe: the listing did see `RM_SolarStill` (Stillsand's item-tray still, a different machine) and `RM_AttarStill`.
- Hose: GimmeSomeSlack already ships the brass/canvas hose family (`GimmeSomeSlack/Textures/RimMandrake/GimmeSomeSlack/Hose/Strand_Plump.png`, `Coupling_Brass.png`, `Reel_*`). Used as the hose source, see Deferred.
- FlowWorks bottles `RM_Bottle/RM_Bucket/RM_Barrel` and `RM_LiquidTank` already have own art (not borrowed).

## Tier chain (WreckedMachines convention, MACHINES.md)
wrecked → kludged (derive_from wrecked) → repaired (derive_from kludged), so damage persists across one object.
Applies to RM_DesalPlant, RM_DetoxWorks, RM_TarRefinery, RM_PumpingStation, RM_WM_Distillation.

## Jobs queued
| wave | job id | def(s) | canvas | state |
|---|---|---|---|---|
| 1 | RM_DesalPlant_Wrecked_v1 | RM_DesalPlant_Wrecked | 768x512 | filed |
| 1 | RM_DetoxWorks_Wrecked_v1 | RM_DetoxWorks_Wrecked | 768x512 | filed |
| 1 | RM_TarRefinery_Wrecked_v1 | RM_TarRefinery_Wrecked | 768x512 | filed |
| 1 | RM_PumpingStation_Wrecked_v1 | RM_PumpingStation_Wrecked | 768x512 | filed |
| 1 | RM_WM_Distillation_Wrecked_v1 | RM_WM_Distillation_Wrecked | 512x512 | filed |
| 1 | RM_SunPanStill_v1 | RM_SunPanStill | 512x512 | filed |
| 1 | RM_DripFilter_v1 | RM_DripFilter | 256x256 | filed |
| 1 | RM_FueledStill_v1 | RM_FueledStill | 512x512 | filed |
| 1 | RM_LiquidPump_v1 | RM_LiquidPump | 256x256 | filed |
| 1 | RM_UniversalCargoTank_v1 | RM_UniversalCargoTank | 512x512 | filed |
| 1 | RM_PipeAdapter_Chemfuel_v1 | RM_PipeAdapter_Chemfuel | 256x256 | filed |
| 1 | RM_WaterBottle_Tintable_v1 | RM_WaterBottle_{Rust,Verdigris,Amber,Violet,Chalk} | 256x256 | filed |
| 2 | <X>_Kludged_v1 (x5) + RM_PipeAdapter_Propane_v1 | kludged tiers; propane adapter | as wave 1 | filed, held by daemon until parent done |
| 3 | <X>_Repaired_v1 (x5) | repaired tiers | as wave 1 | filed, held by daemon until parent done |


## Deferred
- **RM_LiquidHose** (Graphic_Linked, vanilla PowerConduit_Atlas): an image model cannot draw a 16-cell linked atlas reliably, and the brief wants the GimmeSomeSlack hose look. Owed: a deterministic atlas build from GSS `Hose/Strand_Plump.png` + `Coupling_Brass.png` (script under FlowWorks/Tools, installed via `art install --reason script:<path>`). No job filed.
- **Pit fittings / terrain looks on the M board** (ladder borrows spike trap, gates borrow vanilla door, spike art, slime, burning liquid/scorch, swale): not machinery; outside agent A's scope.
- **River items** (sluice box, panning, silt trap etc.): builder Y / merge agent still building; re-read at end below.

## texPath (and graphicClass) changes owed at install
| defName | new texPath | graphicClass change |
|---|---|---|
| RM_DesalPlant_{Wrecked,Kludged,Repaired} | Things/Building/FlowWorks/Machinery/RM_DesalPlant_{Wrecked,Kludged,Repaired} | Graphic_Multi → Graphic_Single |
| RM_DetoxWorks_{…} | Things/Building/FlowWorks/Machinery/RM_DetoxWorks_{…} | Graphic_Random → Graphic_Single |
| RM_TarRefinery_{…} | Things/Building/FlowWorks/Machinery/RM_TarRefinery_{…} | Graphic_Multi → Graphic_Single |
| RM_PumpingStation_{…} | Things/Building/FlowWorks/Machinery/RM_PumpingStation_{…} | (Single already) |
| RM_WM_Distillation_{Wrecked,Kludged,Repaired} (WreckedMachines patch) | WreckedMachines/Modules/Distillation/{Wrecked,Kludged,Repaired}/RM_WM_Distillation | Wrecked: Graphic_Random → Graphic_Single |
| RM_SunPanStill | Things/Building/FlowWorks/Machinery/RM_SunPanStill | — |
| RM_DripFilter | Things/Building/FlowWorks/Machinery/RM_DripFilter | Graphic_Multi → Graphic_Single |
| RM_FueledStill | Things/Building/FlowWorks/Machinery/RM_FueledStill | — |
| RM_LiquidPump | Things/Building/FlowWorks/RM_LiquidPump | — |
| RM_UniversalCargoTank | Things/Building/FlowWorks/Machinery/RM_UniversalCargoTank | — |
| RM_PipeAdapter_Chemfuel / _Propane | Things/Building/FlowWorks/Machinery/RM_PipeAdapter_{Chemfuel,Propane} | Graphic_Random → Graphic_Single |
| RM_WaterBottle_{Rust,Verdigris,Amber,Violet,Chalk} | Things/Item/Resource/FlowWorks/RM_WaterBottle | DubsBadHygiene.Graphic_StackCountTech → Graphic_Single (keep each def's color) |
| RM_LiquidHose | (derived atlas, see Deferred) | — |

Every row carries `install_to` (repo PNG path), so install is `artpipe_state.py collect --from-jobs` (rewired to `art install --reason artpipe-collect`), then the def edits above.

## Install follow-up (offered)
A later agent: once each job is done and passes review, run the collect/install, apply the texPath/graphicClass table above, deploy, and add the stations to the FlowWorks review map. Not done here (no defs edited, nothing installed).

## Builder X/Y re-reads
(pending)
