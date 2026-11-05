## spec
found-by: Opus review of FROZEN_OVERFLOW_DIG_FIX_ICE_POURS_LIQUID (2026-11-05), unverified live.

`HandOverTakenCells` (`src/RimMandrake/FlowWorks/Source/Sheet/RM_MapComponent_Sheet.cs`) hands a wet square that became a
Receiver/Sink to the engine via `Credit`; whatever the channel refuses (full, or a different liquid's body) stays on the square.
On a dug/lake cell the sheet's evaporation and soak are 0 (`RM_MapComponent_Sheet.cs` ~:184; the setter ~:262 is only reached
for open ground) and every kernel flow pass skips non-HoldsSheet kinds, so that residue may sit there forever. Verify (offline
kernel read or a sheet selftest) and either let it dry/flow or document it as intended.
