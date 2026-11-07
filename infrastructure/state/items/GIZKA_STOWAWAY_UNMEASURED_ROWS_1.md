# GIZKA_STOWAWAY_UNMEASURED_ROWS_1 - GizkaStowaway unmeasured rows

Filed 2026-10-07 from the GREEN-MIN / L2 sweeps (Transient/*_20261007.md).

## spec
GizkaStowaway modcheck status is RED because 10 rows read UNMEASURED (27 PASS / 0 FAIL / 10 UNMEASURED, Transient/modcheck/GizkaStowaway_20261007T191543Z.json (gone from disk; last copy in git at 1731f06619)). For each: either add the capability (bridge tool / fixture) so it measures, or reword the bar if it is unmeasurable by design, or classify it in the script as a documented gap. Parent: GIZKA_STOWAWAY_FIRST_SCRIPT_1 (owes A1/A3 GREEN-MIN).

## verify
python.exe northstar_driver run for GizkaStowaway; modcheck status.

## criteria
A1: a table of the 10 rows with cause and chosen resolution is on the item.
A2: modcheck status GizkaStowaway reads GREEN with current hash, or each remaining UNMEASURED is an explicit by-design row accepted by the status rule.

## live check
New mechanism never seen: the 10 UNMEASURED GizkaStowaway behaviours have never been observed running.

NEXT: claim this item and start with criterion A1.

## resolution (A1) — 2026-11-02, relentless gen 1
The 2026-10-07 results JSON is gone (Transient is untracked). The script at that run (21be0cf7e3..e0da98a2f8) hard-wired
8 rows UNMEASURED in chain `mechanics_unmeasured`; the other 2 came from the 3 rows that need a gizka creature loaded.
The status rule (`modcheck/runner.py`, all_green) accepts NO by-design UNMEASURED, so every row now measures.
Instrument: `RSW_GizkaProbe` (public static class in the mod, reached by `jawa/static_call`), which drives the mod's
REAL entry points with the dice forced (a chance of 0 still delivers nothing).

| old row | cause | resolution (new rows in `validation.py`) |
|---|---|---|
| gravship_landing_delivers_one_tame_gizka | needs a gravship landing + 35 % roll | capability: `discovery_triggers/gravship_landing_delivers_one_tame_gizka` fires the Harmony postfix, dice forced; `cooldown_blocks_a_second_discovery` |
| salvage_trade_quest_hooks_deliver | needs a wreck deconstruction, trade, quest + rolls | capability: `salvage_deconstruction_…` (ShipChunk via real `Thing.Destroy(Deconstruct)`, slag control), `trade_delivers_one_and_an_empty_trade_none`, `quest_success_delivers_one_and_failure_none`, `every_off_switch_silences_its_trigger` |
| fecundity_replicates_while_fed_and_warm | ~4 game days of ticks | capability: `fecundity_live/…` runs the hediff comp's own `CompPostTickInterval` with the fuse set |
| population_cap_stops_breeding | colony grown to cap 22 | capability: `fecundity_live/population_cap_stops_breeding` sets populationCap to the live count |
| infestation_stage_chews_powered_buildings | Infestation stage + powered building | capability: `chewing_live/…` (3 adults in a room, heater forced powered, real check `CheckNow`), off arms: chewing off, unpowered, Underfoot |
| cold_below_breeding_gate_stalls_replication | "no verb sets a room temperature" (stale) | capability: probe `SetRoomTemp` on a staged room; `fecundity_live/cold_…` + `hunger_stalls_the_fuse` |
| cull_weighs_on_watching_colonists | needs a witnessed slaughter | capability: `cull_guilt_live/…` kills via real `Pawn.Kill`; off arms: setting off, 16 cells away, non-lineage gizka |
| global_breeding_slider_rescales_donor_fields | Apply runs only on WriteSettings | capability: `global_breeding_slider/…` calls `RSW_GizkaDonorTuning.Apply` via static_call, reads live egg/mate fields, restores |
| fecundity_state, bait_poison/poison_hediff_advances_on_a_gizka, donor_patch (2 of 3) | no gizka creature on the run's list: modcheck composed MINIMAL + hard deps only, and the mod's creature is a soft dependency | fixture: modset tier `gizkastowaway` (+gimmesomeslack, biomes, swbestiary) with new opt-in key `modcheck_closure`, honoured by `runner.closure_ids` |

Offline proof: `python3 src/RimStarWars/GizkaStowaway/validation.py` (STATIC PASS), `selftest_gizkastowaway.py`,
`selftest_gizka_validation_chains.py` (a toy mod: every new row PASSes right, FAILs on a planted defect, reads
UNMEASURED with no creature). A2 is live: `infrastructure/state/live_proofs/GIZKA_STOWAWAY_UNMEASURED_ROWS_1.txt`.

Gen 8 (2026-11-05): no code change; rebuilt on current origin/main because 576c7659a1 (GOLD_PANNING) changed `modcheck/required_checks.json` after the gen-6 build, which the live preflight refuses as stale. Offline proof re-run green at b1a54262e4.
