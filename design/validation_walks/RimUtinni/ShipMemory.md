# ShipMemory — validation walk
subject: src/RimUtinni/ShipMemory
deps: Ludeon.RimWorld.Anomaly (official DLC, loadAfter)
list: minimal+Anomaly
status-hint: ANOMALY_EXCEPTION_ACCESS_1 — gates 7 vanilla Anomaly buildables (6 ThingDefs + BioferritePlate TerrainDef) behind a `discoveryPrerequisites` reveal instead of research; a GameComponent reveals them the moment the clan first holds a live beast, stockpiles 50+ Bioferrite, or the Assailant dungeon signals it.

## must be true
- With Anomaly active, `HoldingPlatform`, `ElectricInhibitor`, `ShardInhibitor`, `BioferriteHarvester`, `Electroharvester`, `BioferriteGenerator` (ThingDefs) and `BioferritePlate` (TerrainDef) each have their vanilla `researchPrerequisites` removed and a `discoveryPrerequisites` pointing at `RUT_ShipMemory_Containment` added.
- `RUT_ShipMemory_Containment` (ThingDef) exists with `hiddenWhileUndiscovered=true`, `category=Item`, `tradeability=None`, `selectable=false`, `destroyOnDrop=true` — it is never spawned, only used as a HiddenItemsManager key.
- Sending a signal whose tag ends in `RUT_ShipMemory_Containment` (the Assailant dungeon's own route, per `Notify_SignalReceived`'s `EndsWith` match) calls `Find.HiddenItemsManager.SetDiscovered` and posts a `PositiveEvent` letter labelled "She remembers the chains", hyperlinked to the six ThingDefs (not the TerrainDef).
- The reveal is one-shot: once `HiddenItemsManager.Hidden(Gate)` is false, `GameComponentTick` and `Notify_SignalReceived` both no-op on every subsequent check — no duplicate letters.
- Without `ModsConfig.AnomalyActive`, the patch (`PatchOperationFindMod` on "Anomaly") is a silent no-op — nothing patched, no error.

## the walk
1. [L] Player.log after load (Anomaly active) contains no "Config error in mandrake.rut.shipmemory" and no XML error naming RUT_ShipMemory_ContainmentGate.xml or RUT_ShipMemory.xml
2. [D] def read-back: ThingDef `RUT_ShipMemory_Containment` exists; `hiddenWhileUndiscovered` = True; `tradeability` = None; `selectable` = false
3. [D] def read-back: ThingDef `HoldingPlatform` has no `researchPrerequisites`; `discoveryPrerequisites` contains `RUT_ShipMemory_Containment`
4. [D] def read-back: TerrainDef `BioferritePlate` has no `researchPrerequisites`; `discoveryPrerequisites` contains `RUT_ShipMemory_Containment`
5. [B] `jawa/signal_send` {tag: "test.RUT_ShipMemory_Containment"} → `jawa/letter_list` shows a new letter with label "She remembers the chains"
6. [S] (human pass) confirm the letter's hyperlinked-things list shows the six buildings (not BioferritePlate) and that all seven are now buildable/paintable in the architect menu
