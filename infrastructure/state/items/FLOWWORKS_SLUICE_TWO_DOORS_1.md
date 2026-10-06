# FLOWWORKS_SLUICE_TWO_DOORS_1 — a sealed sluice gate and a liquid-passing grate gate

## ruling (owner, 2026-10-06, typed on a question card)

*"There are sealed sluice gates (standard) and the ones made of metal grates that always allow liquid (this is just a gate, not a sluice gate then). Yes, both, two kinds of door."*

## what

- **Sluice gate (standard):** sealed. Shut holds liquid; open lets it through.
- **Grate gate:** metal grate, always passes liquid; it is just a gate (pawn barrier), not a sluice.

Today the code passes liquid through every flow door even when shut (`src/RimMandrake/FlowWorks/Source/Superdeep/RM_FlowDoors.cs:13-15`, `Flood_FlowWorks.cs:295-300`; the pulse donor picker has no door-state gate). The review key sheet (`northstar/review/map/KEYSHEET.md:277-281`) already describes the sealed behaviour. Reconcile with `FLOWWORKS_DOOR_FAMILY_1` (two stuffable defs) before building.

Found by the 2026-10-06 GPT playtest review, finding #9 (`design/RimMandrake/flowworks_playtest_automation_2026-10-06.md`).
