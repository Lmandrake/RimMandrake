# PYRE_BURN_LINE_PROVE_TWO_QUIET_DAYS (HARNESS, Pyrelands suite)

`pyre_burn_line_present` is UNMEASURED by construction on the site fixture: northstar_site.isolate holds burnLineEnabled OFF
through generation and settle (on purpose, for the gen census), so 0 fires is all the fixture can show.

The mechanism to prove: `MapComponent_BurnLine.TryReseedStandingBurn` lights ONE smoulder in open grass after
`StandingBurnQuietTicks` = 120,000 with no fire on the map (PyrelandsTuning.cs). An arm: burnLineEnabled ON, map
extinguished, wait 120,000 + a few BurnWatchIntervalTicks (60), count free-standing Fire (parent == null), screenshot the
front, extinguish, restore. ~10 min at the measured ~200 ticks/s Ultrafast; run it in the long split with
embergrass_regrow (`--chains embergrass_regrow,burn_line`), never in the main run.

Triage: `Transient/pyre_site_2026-10-12.md`.
