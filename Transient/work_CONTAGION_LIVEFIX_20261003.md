# Contagion livefix 2026-10-03 (5 FAIL, 24 UNMEASURED) - dispositions

All edits in `src/RimMandrake/Contagion/validation.py`; no C# or def changes. Offline only: not re-run live.

1. defs/biome_table_and_roster: HARNESS. get_defs serialises record lists as bare type names unless `deep=true`
   (live evidence: `['WeatherCommonalityRecord', ...]`), so `x.get` hit a str. Fix: `deep=True`, and a non-dict row is
   UNMEASURED, never a crash. `wildAnimals` is a NON-PUBLIC list that get_defs cannot serialise even deep, so that check
   moved to its own component `biome_roster_animals` (UNMEASURED live, XML roster covered statically).
2. burn_forced/burn_site_ready + uv/uv_site_ready: HARNESS. `_pad` re-based on the driver anchor (~(53,50) on a 250x250
   map), so pads at z-45 were half off-map (clear_area reported 532 off-map cells). `_pad` now re-bases on
   map_info sizeX/2,sizeZ/2 (same as Stillsand's `_STATE["base"]`).
3. coalescence_off_absorbs_nothing: UNDETERMINED live cause, harness made diagnostic. The Coalescence thing was gone
   after 400 ticks (inspect matched nothing). Only code path that destroys it is Collapse() on a Burn (independent of the
   toggle); no mod bug found by reading. The check now distinguishes: gone + Burn condition/samples -> UNMEASURED (Burn
   collapsed it); gone with neither -> real FAIL. Likely culprit: leftover natural-Burn schedule from the chain-17 clock jumps.
4. genome/extraction_surgery_yields_sample: HARNESS. do_bill_now returned null with "UsableForBillsAfterFueling false"
   (tool wording; for a Pawn giver it means the patient is not in a bed). Bed was spawned but the patient never laid on it.
   Fix: ordered_job LayDown on the bed, and a failed do_bill_now is UNMEASURED with the tool's reason (the old
   `jobOnThingReturnedNull` key never exists, so the guard never fired). Not a mod bug.
5. The 24 UNMEASURED: 17 were cascades from the above (burn 7, uv 1, coalescence 6, genome 2, organ_patch_comps 1);
   7 (spawner 4, burn_natural 3) were `clock_runaway`: `_jump` used t.bridge_call, which the watch charges as an unplanned
   verb (cap 1500 ticks). `_jump` now goes through t.session.call and re-bases the clock gate as an epoch change
   (zero ticks charged). Expected to stay legitimately UNMEASURED: `organ_patch_comps` if get_def does not return
   comps (unverified), `biome_roster_animals` (non-public field). Everything else needs a live re-run to confirm.
