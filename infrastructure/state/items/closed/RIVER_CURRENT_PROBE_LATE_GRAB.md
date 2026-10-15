# RIVER_CURRENT_PROBE_LATE_GRAB

FlowWorks: 250-tick current acquisition gap; steam vents not revalidated

Source: FlowWorks pre-release GPT consult, BENCH 2026-10-15 — `Transient/release_push_2026-10-15/gpt_FlowWorks/TRIAGE.md` (full rows) and the `answer_<slice>.md` named by each finding id.

## findings

- **C6-F6** PLAUSIBLE LOW — New river entrants are registered only every 250 ticks, then wait a full cadence: short fast-lane crossings may finish unshoved. RM_MapComponent_RiverCurrent ScanIntervalTicks=250 + nextMoveTick = now + CadenceFor. Live: order a drafted pawn across a 4-cell fast lane right after a scan; read position/registration per tick.
- **C6-F10** CONFIRMED LOW — River steam vents keep puffing from cells that stopped being river. ManyWaters/RiverSteamHook.cs: vents chosen in FinalizeInit (:111-148), tick (:197) never rechecks IsRiver.

## criteria

- Each CONFIRMED finding: a SelfTest/python case (or a live state read where the row says so) that goes red on today's code, then green with the fix.
- Each PLAUSIBLE finding: run the check written in its row first; close it as not-a-bug with the evidence if it stays green.
