# CANYON_FLOOD_ROAR_SILENT_1 — FloodedCanyon flood roar never plays

Found by the kernel extraction audit, `Transient/kernel_audit_20261008.md` (2026-10-08).

## spec
Before commit `3f5701d45`, `RM_MapComponent_CanyonFlood.MapComponentTick` called `MaintainRoar()` on
every `Phase.Flooding` tick (old line 285). After the extraction, `MaintainRoar()` is still defined
(`src/RimMandrake/FloodedCanyon/Source/RM_MapComponent_CanyonFlood.cs:341`) but nothing calls it —
neither the kernel step nor `MapComponentTick`. Beat 5 (the continuous flood roar sustainer) is
therefore never spawned; floods are silent. `roarCell` is still set and the recede still ends a
(null) sustainer.

Fix: call `MaintainRoar()` each tick while the kernel phase is Flooding, as before.

## verify
Offline: a grep shows a live caller in the Flooding branch; the debug readout's `roar=` field reads `on`
during a flood in a quicktest (with the owner, or via a state read — no screenshot hunt needed).

## criteria
`MaintainRoar()` runs every Flooding tick when `fiveBeatsEnabled` is on.
