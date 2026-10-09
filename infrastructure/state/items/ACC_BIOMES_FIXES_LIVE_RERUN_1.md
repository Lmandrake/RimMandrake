# ACC_BIOMES_FIXES_LIVE_RERUN_1 — re-run four acc_biomes fixes live

220d7a754 fixed GelatinousSlime seeker/injection marks, LeaningScrub bloom toggle-off, RustCathedral crossBiomeBiomeList round trip and Miasma mothers_price site handling; the originating items were marked implemented with a live re-run noted as owed but never recorded in the ledger. See Transient/belt_findings_batch2_20261009.md.

## criteria
- [ ] GelatinousSlime: seeker_loads_without_the_dialog and antidote_wins_the_race PASS.
- [ ] LeaningScrub: bloom_toggle_off_quiet PASS (no Flee with runwayBloomEnabled off).
- [ ] RustCathedral: settings_roundtrip crossBiomeBiomeList round-trips.
- [ ] Miasma: mothers_price/returning_a_young_wins_her_tolerance PASS, or UNMEASURED (never FAIL) when no warden mother/water cell exists.

## verify

Live modcheck per mod on acc_biomes (L2). Evidence: run reports. Origins: GELATINOUSSLIME_SEEKER_MARK_FAILS_1, LEANINGSCRUB_BLOOM_TOGGLE_OFF_STILL_FIRES_1, RUSTCATHEDRAL_SETTINGS_CROSSBIOME_ROUNDTRIP_1, MIASMA_MOTHERS_PRICE_RETURN_SITE_1.

## Watch out

Filed by the 2026-10-09 upkeep pass: the originating item was closed `implemented --none-owed` with only offline evidence. Mechanism-never-seen line: the offline fix changed the harness/mod code path itself, and that path has not been observed running since.
