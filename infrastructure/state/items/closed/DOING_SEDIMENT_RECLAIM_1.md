
## spec
DOING_ITEMS_RECONCILE_1's audit (2026-09-13) found these 21 FOUNDRY items in
`doing` with NO activity since 2026-09-06..10 — started by sessions that died,
never closed, and invisible to `next` while stuck in doing. BENCH cannot
reclaim another seat's items (guard verified, and the owner's audit request
was a question, not an authorization), so the reclaim is yours:

MASS_VALIDATION_LADDER_1 · DROID_TILES_SOURED_TERRAIN_1 ·
INHABITED_STOCK_ONTO_MAP_AND_FATE_1 · PLOT_MECHANISM_MODS_WAVE_1 ·
MACRO_GENERATOR_V0_1 · MAPGEN_PAINTER_V1_1 · MAPGEN_GL_SHEET_1 ·
UNUSED_MUTATORS_WORLD_ASSIGNMENT_1 · MAPGEN_CONVERGENCE_LOOP_1 ·
ANCIENT_WAR_LAB_1 · DROID_REPAIR_FOR_PROFIT_EVENTS_1 ·
ORACLE_CLIENT_CLAUDE_CODE_REWRITE_1 · PITCELL_PRISONER_BED_BRIDGE_GAP_1 ·
DROIDWORKS_FORMAT_TIERS_1 · CHRONICLE_NINEFOLD_DECOUPLE_1 ·
MANYWATERS_COLOR_SUPPORT_1 · MOVING_DUNES_BUILD_1 · LANDMARK_NAMING_PASS_1 ·
OASIS_LANDMARK_PLACEMENT_1 · FISH_BESTIARY_COMMISSION_1 ·
CRYPTOFORGE_HARVEST_RETIRE_1

`rimflow reclaim <ID>` each (progress notes on the item files survive; several
are part-done — e.g. CRYPTOFORGE_HARVEST_RETIRE_1 steps 2-3/5,
BAREHANDED-style live proofs owed on ORACLE_CLIENT / PITCELL / INHABITED_STOCK).
MACRO_GENERATOR_V0_1 is really awaiting the owner's grade — reclaim it and set
`needs owner` rather than re-working it. Per queue-items-decay, verify each
item's premise on claim, not on this list's word: full per-item evidence in
`Transient/doing_audit_2026-09-13.md`.

Do NOT touch the 19 in-progress items the audit confirmed live (touched
2026-09-11/12: MLIE_FAUNA_ABSORPTION_1, TILE_STRUCTURE_DESIGNS_1, the
settlement/vault/cathedral wave, etc.) or anything started <24h.

## verify
The doing projection shows every FOUNDRY doing item either touched <72h or on
a named hold; the 21 above are ready (or closed with a real sha where a claim
turns out to be already-done).

## criteria
`doing` on FOUNDRY means a live session is on it. Zero dead-session residents.
