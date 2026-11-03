## spec
Re-filed from UNPROVEN_LIVE_LEGS_TRIAGE_1 (triage of CAULDRON_ENRICHMENT_LIVE_PROOF_1 A4, verdict NEEDS A TOOL).
A4 is "all three toggles off: none of the assay string, letter or nettle spawning happens". Two of the three
OFF arms already have live components in `src/RimMandrake/Cauldron/validation.py` and read PASS in the bench live
run of 2026-10-19 (`flora.assay_toggle_off`, `water.water_letter_toggle_off`, `water.water_poison_toggle_off`).
The third, the condensate gardens (raven nettles colonising toxic shores, `RM_MapComponent_CondensateGardens`,
setting `condensateGardensEnabled`), has only a settings round-trip and the `nettle_habitat_wired` def read: no
component measures that nettle spawning STOPS with the toggle off.

Build: a component in validation.py (water or flora chain), e.g. `gardens_off_no_nettles`, toggle=condensateGardensEnabled:
stage toxic water with nettle-eligible bank cells (as A3's live proof did), set the toggle off, drive the hourly
sampling (`RM_MapComponent_CondensateGardens` spread: 40 random cells per 2500 ticks) for N sample periods, and read
the RM_RavenNettle count on the banks unchanged; with the toggle on the same staging adds nettles (the ON control,
so a blind instrument cannot pass). Plant ticks only TickLong; the map component ticks normally.

## criteria
A1 L0: the new component is in validation.py with toggle=condensateGardensEnabled and an ON control; the mock suite run lists it; selftest_cauldron green.
A2 L2: live, the component reads PASS on a Cauldron map (bar `<chain>.gardens_off_no_nettles`), closing CAULDRON_ENRICHMENT_LIVE_PROOF_1 A4's third arm.
