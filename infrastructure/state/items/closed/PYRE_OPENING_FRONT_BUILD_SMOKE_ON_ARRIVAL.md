# PYRE_OPENING_FRONT_BUILD_SMOKE_ON_ARRIVAL

Owner, by card 2026-10-22: "GPT review Q7 → Pyrelands fresh map starts with a smouldering front"
(`design/RimMandrake/gpt_review_findings_2026-10-22.md`, Q7 and "Owner answers").

## spec
The walk bar `pyre_burn_line_present` (`design/validation_walks/RimMandrake/Pyrelands.md`) says a fresh map shows an
active line of fire with a scorched trail; the scheduled front (`PyrelandsFireFront`) is only armed 2-4 days in.
Every fresh Pyrelands map now lights one small front (`OpeningFrontWidthCells` 5 cells, `OpeningFrontFireSize` 0.35,
null instigator, no letter) on its first watch interval, retrying each interval inside `OpeningFrontWindowTicks`
(2500) of map generation. Gated by the mechanics gate and `fireClockEnabled` (off drops it for good). Saved flag
`fireFrontOpeningDone` defaults TRUE, so a pre-change save never bursts into an "opening" fire; a map that gains the
component late is past the window. Decision: `RM_BurnKernel.OpeningFront`. Probes: `MapComponent_BurnLine.ProbeOpeningFront`,
`RearmOpeningFront` (test drive). Not touched: the special-mechanics review's Pyrelands fluff candidates.

## verify
Offline: `selftest_pyrelands_fuzz.py` (units: OpeningFront corners, lights-at-most-once replay, tuning sanity),
`selftest_pyrelands_lint.py`. Live: Pyrelands chain `opening_front` (`src/RimMandrake/Pyrelands/validation.py`).

## criteria
- A1 L0: Pyrelands fuzz OK incl. the OpeningFront units; Pyrelands lint selftest PASS; FireEcologyHook.dll builds.
- A2 L1: deploy: `deploy_custom_mods.py --compose biomes --apply` carries the new FireEcologyHook.dll.
- A3 L2: live: chain `opening_front` PASS: after RearmOpeningFront with fireClockEnabled ON, ProbeOpeningFront reads done=True, lit>0, and free-standing Fire is on the map.
- A4 L2: live: a newly generated Pyrelands map (not a fixture reload) has free-standing Fire within its first in-game hour, and ProbeOpeningFront there reads done=True with lit>0; an old save loaded reads done=True, lit=0 and gains no fire from it.
- A5 L4: walk: on arrival at a fresh Pyrelands map the owner sees an active line of fire with a scorched trail behind it (pyre_burn_line_present).
