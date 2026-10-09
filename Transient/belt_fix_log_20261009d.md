# belt fix log 20261009d
- implemented STILLSAND_SETTINGS_SCROLL_1, PRECIOUS_CAVE_PRESERVATION_EDGES_1, GALE_CARRIED_RETURN_HARDENING_1 at c3030ac5d (Stillsand: scroll views on 3 panels; frozenVanish dict restores corpse vanish clock; gale return spawns dead pawn's body; sea-floor home-map half was already fixed via AnyPlayerSurfaceHomeMap). selftest 108/108.
- implemented DEEPFIRE_SETTINGS_MISSING_CONTROLS_1 at 2af11345f (5 sliders added; selftest ALL OK)
- partial (left open) VALIDATION_SETTINGS_SNAPSHOT_1: snapshot/restore-prior/fail-on-restore-error landed d0d520735+4f90ad25d; settings ExposeData round trip still owed
- implemented HAZARD_MULTIPLIER_COVERAGE_1, SCRIPTED_DIEOFF_GENERATION_BOUND_1 at 2249ef960 (CompTickLong half was already fixed)
- implemented GALE_STRUCTURE_WEAR_RATE_1 at d99755c03 (per-building MTB roll). Skipped as design/owner/live: FEVERWOOD_NATURAL_TOGGLE_1, HEDIFF_GLOW_TARGETING_PULSE_1 (delete-vs-wire call), CONTACT_VENOM_NONLETHAL_ORDER_1 (live proof), HUGETHINGS_* (translation-key scope), most others need ruling
