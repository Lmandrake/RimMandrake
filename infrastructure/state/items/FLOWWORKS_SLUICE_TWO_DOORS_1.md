# FLOWWORKS_SLUICE_TWO_DOORS_1 — a sealed sluice gate and a liquid-passing grate gate

## ruling (owner, 2026-10-06, typed on a question card)

*"There are sealed sluice gates (standard) and the ones made of metal grates that always allow liquid (this is just a gate, not a sluice gate then). Yes, both, two kinds of door."*

## what

- **Sluice gate (standard):** sealed. Shut holds liquid; open lets it through.
- **Grate gate:** metal grate, always passes liquid; it is just a gate (pawn barrier), not a sluice.

Today the code passes liquid through every flow door even when shut (`src/RimMandrake/FlowWorks/Source/Superdeep/RM_FlowDoors.cs:13-15`, `Flood_FlowWorks.cs:295-300`; the pulse donor picker has no door-state gate). The review key sheet (`northstar/review/map/KEYSHEET.md:277-281`) already describes the sealed behaviour. Reconcile with `FLOWWORKS_DOOR_FAMILY_1` (two stuffable defs) before building.

Found by the 2026-10-06 GPT playtest review, finding #9 (`design/RimMandrake/flowworks_playtest_automation_2026-10-06.md`).

## built

No new def and no new setting: `RM_Sluice` is the sealed sluice gate, `RM_SecurityGrateDoor` the grate gate. A SHUT sluice
seals its cell (`RM_PitTrapMath.FlowDoorSeals`, `RM_FlowDoorRules.SealsLiquid`): the depth engine moves no liquid into or out
of it and walks no flow order through it (`RM_FlowKernel.sealedCell`, fed per cell from the edifice grid), and the legacy
`Flood_FlowWorks.CanFloodInto` refuses it. Open (a pawn passing, or held open) it passes; the grate always passes.
`RM_Sluice`'s description no longer says liquid flows through it shut. Extension chain `flow_doors` now asserts
`grate_passes_sluice_seals`; JawaBench playtest `ScnSluice` (written against this ruling, expected-fail until built) is the
live check of all three cases.

## criteria
- A1 L0: C# selftest `Sluice_shut_seals_grate_passes` — FlowDoorSeals truth table, and the production kernel holds a limitless pond's level at a shut sluice (F=2,2,2,0,0,0,0), fills past it once opened, fills past a grate, ledger balanced.
- A2 L0: run_selftests 221/222 (utinnipatches_dump env failure only); selftest_extensions / selftest_flowworks_northstar / selftest_human_review PASS; validate_patch clean on FlowWorks_Doors.xml.
- A3 L2: JawaBench playtest ScnSluice passes all three cases (grate_closed passes, sluice_shut holds, sluice_open passes) — flips from expected-fail to XPASS.
- A4 L2: extension chain flow_doors component grate_passes_sluice_seals PASS on the trial site.
