# Review batch 10 — 2026-10-06 (offline, full-file)

Status checked first. Already CLEAN, skipped: RM_Building_TractionLance.cs (81162be4a), RM_WebworkMod.cs (5840198a0).
No significant findings; no source edited, no rebuild. All nine marked clean at fe6140ff4
(records in infrastructure/state/code_review/FOUNDRY.jsonl, uncommitted).

| file | verdict | notes |
|---|---|---|
| CreatureBehaviors/Source/RM_MapComponent_ShadeGrid.cs | CLEAN | light layer cleared each rebuild, gear cover kept after light; NativeArray customizers retired one rebuild late; moving-shade clear-then-recast intact |
| CreatureBehaviors/Source/RM_CompTetherPull.cs | CLEAN | reel arrival checked before step; Full-fillage / unwalkable stop; save keys match capstan |
| Watchers/Source/RM_WatcherUtility.cs | CLEAN | hiddenHediff/signDef null caught by ConfigErrors; Flush's only caller passes a non-null flusher |
| Watchers/Source/RM_JobGiver_Watch.cs | CLEAN | |
| Scarlands/Source/RM_WarscarMod.cs | CLEAN | BiomeDef.wildAnimals / cachedAnimalCommonalities names match 1.6 (RimSage); cache nulled before first read |
| ScarlandsLadder/Source/PilgrimCamps.cs | CLEAN | bedroll North covers bedCell+N (journal cell), clear of the campfire; all camp cells inside the CampFits 3x3 |
| RustCathedral/Source/RustCathedral/RM_RustCathedralMod.cs | CLEAN | single ModSettings; fixed section heights hold the Hum (~380px of 430) and Walls (~215 of 240) content |
| TerminalBiomes/Source/RM_TerminalBiomesMod.cs | CLEAN | |
| UnfinishedLine/Source/UnfinishedLineTithe.cs | CLEAN | see below |
| Cauldron/Source | NOT REVIEWED | only change is untracked RM_VexxissPrints.cs (another agent's work in progress; cannot be marked clean while uncommitted) |

## UnfinishedLineTithe.cs, checked against decompiled 1.6 (RimSage)
- Target `CompShuttle.IsAllowed(Thing)`: public virtual, single overload, no vanilla override. Every load route goes through it:
  TransporterUtility (`IsRequired || IsAllowed`), IsAllowedNow (carry float menus, CompShuttle gizmos), and JobDriver_EnterTransporter's FailOn.
- Postfix only narrows `true` to `false`, never widens. IsRequired for a pawn is only `requiredPawns`, so the `!IsRequired` exemption cannot bypass the gate.
- Scope: Enclave-owned shuttle (XML `owningFaction $enclaveFaction`) AND a QuestPart_RUT_TitheShuttle in an Ongoing quest naming that exact Thing. Any other shuttle gets min 0, so it is unaffected.
- `$pickupShipThing` is in the slate after Util_TransportShip_Pickup (no prefix), so the gate node reads it at gen time.
- Lend part fields and `TendPawnsWithMedicine` signature match 1.6. outSignalsCompleted fires in base.Complete while lentColonists is still populated, so the XP gift sees the pawns.
- Save/load: shuttle by reference, the lend found on the quest (not Scribed), and `given` stops a double gift. A null lend or a null completeSignal makes the gift a no-op.
