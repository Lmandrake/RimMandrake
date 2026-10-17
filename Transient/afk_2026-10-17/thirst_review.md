# Thirst review (BENCH AFK, 2026-10-17)

## Code review status
- `src/RimMandrake/FlowWorks/northstar/thirst_live.py`: full read, fixed (below), marked CLEAN after commit.
- `src/RimMandrake/FlowWorks/Source/SelfTest/ThirstChecks.cs`: full read, no defect; stale header comment corrected
  ("live, owed" -> the live halves are thirst_live.py). SelfTest project only (not the mod DLL): mod hash unchanged.

## Findings / fixes (thirst_live.py)
- T25 melt predicate (HARNESS, the cause of the full-run FAIL): see below. Now follows the snow bucket(s) seen at the
  gather by ID; full melt trace kept (was last 5); warmTicks read from comp_read's `values` key.
- dry_all/WETS: canal fill water `RM_Fill_Water_{Trace,Half,Brim,Superdeep}` added (round 2's T25 replay ran
  RM_FillBottleJob on the "dried" map). LIES noted: the canal sim may repaint a cell it still holds depth for.
- T29: `f >= target` crashed on an unreadable RM_BottleStock.Have (None) -> guarded.
- T20 arm 2: `cur[0]` IndexError when no filled bucket remains -> break; the pour arm reads the absence.
- batch3 list: dead `(only or True)` clause removed.
- Offline: selftest_flowworks_driver_rows.py PASS. No live run (bridge is FOUNDRY's).

## T25 starvation analysis (code reading only)
Evidence: `src/RimMandrake/FlowWorks/northstar/thirst_live_result_20261017T145433.json` (full run 2) and the driver at
3b33f2bbfe. That driver laid ONE empty bucket and did not clear leftovers; T20/T23 left three -> four empties, all
gathered at staggered times. Trace: t=5000 three snow buckets on (205,145..147), fresh 1; t=6500 two, fresh 2.
So the first bucket melted on time (<= 5000) and the second by 6500. The test was `fresh > fresh0 AND no snow bucket
left`, i.e. it waited for the LAST-gathered bucket. **HARNESS, not MOD; the mod melted on schedule.** The two
isolated PASSes had a single snow bucket (the --t25-empties 3 replay's other empties were filled from canal water).

## False theories
- Temperature: bucket cell 24.9-26.3 C; CompRM_Melt counts any rare tick above 0 C. FALSE.
- An earlier row's stove/bill occupied: the only bill row (T26) runs after T25; the passive melt needs no bill. FALSE.
- Worker busy / bucket forbidden or reserved: all four buckets were gathered; the melt comp reads neither. FALSE.
- A carried bucket not ticking: all three stayed on their scoop cells through the trace. FALSE.
- 145433's `comp: None`: instrument, not mod: that driver read `fields`/`members`; comp_read answers `values`.

## Owed
- Live: rerun T25 (and the full thirst_live for credit at the current mod hash) when BENCH next holds the bridge.
