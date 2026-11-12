---
state: proposed
needs: offline
---

# CANAL_SPILL_WIRE_GARDEN_GROWS_DOWNHILL

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

Canal overflow (built 3cf4fdf12f, CANAL_OVERFLOW_BUILD_EVERY_PUDDLE_AUDITED) does not yet feed Explosive Growth or leave wet ground: (1) wire the sheet's Soaked dL into ExplosiveGrowthAPI.SoakCells (spec canal_overflow_flooding_2026-10-21.md lines ~182/321; CanyonFlood and SoakZone already call it); (2) leave visible wet ground where a sheet soaked or dried, fading over time (not a per-cell disc lattice: see WETSAND_STAIN_FIX_READS_AS_POLKA_DOTS); (3) a demo savegame for the owner: one map, an overfilled canal spilling downhill across bare ground, crops and wild plants, so he watches it run, soak, and the growth burst after; this is also that item's H1 L4 look. Not urgent: 'at some point'.

## what is left

- proposed: nothing recorded as owed beyond the title; read `rimflow show CANAL_SPILL_WIRE_GARDEN_GROWS_DOWNHILL` history before building.

## latest ledger notes

- 2026-11-04: Owner's wetting model (also for canal banks): wet ground is shared with Stillsand's spilled-water technique; see FLOWWORKS_SCRIPT_MEASURE_PREP_AND_CONTROLS

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify CANAL_SPILL_WIRE_GARDEN_GROWS_DOWNHILL --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=CANAL_SPILL_WIRE_GARDEN_GROWS_DOWNHILL` first: another commit may already do it.
