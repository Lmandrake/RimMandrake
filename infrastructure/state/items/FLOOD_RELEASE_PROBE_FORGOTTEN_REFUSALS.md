# FLOOD_RELEASE_PROBE_FORGOTTEN_REFUSALS

FlowWorks: flood driver inputs/refusals lost on reload; IsWater gate rejects wet inlets

Source: FlowWorks pre-release GPT consult, BENCH 2026-10-15 — `Transient/release_push_2026-10-15/gpt_FlowWorks/TRIAGE.md` (full rows) and the `answer_<slice>.md` named by each finding id.

## findings

- **C5-F1** PLAUSIBLE LOW — Flood-fed driver inputs are not saved and a flood never re-marks them. RM_MapComponent_Excavation.cs:2104-2106 'Not saved: a driver re-marks its cell on its next write' - true for pumps, not for a one-shot Flood_FlowWorks (placed cells never rewritten). Offline: kernel scene with/without the flood's driver inputs, compare 3 pulses.
- **C5-F2** PLAUSIBLE LOW — A flood's refused/hands-off cells are forgotten on reload. Flood_FlowWorks.cs: refusals go only into placedLookup; load rebuilds it from placedCells. Offline round-trip of a release with a refused cell.
- **C5-F11** PLAUSIBLE LOW — Flood eligibility rejects partly filled (IsWater) channel cells and anything beyond a wet inlet. Flood_FlowWorks.cs:290-294 'if (t == null || t.IsWater) return false' before engine ownership. Offline/live: release beside a 1-level water inlet vs a dry inlet; compare reach.

## criteria

- Each CONFIRMED finding: a SelfTest/python case (or a live state read where the row says so) that goes red on today's code, then green with the fix.
- Each PLAUSIBLE finding: run the check written in its row first; close it as not-a-bug with the evidence if it stays green.
