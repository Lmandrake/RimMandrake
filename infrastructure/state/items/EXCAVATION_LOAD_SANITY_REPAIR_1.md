# EXCAVATION_LOAD_SANITY_REPAIR_1 — FL-3: Excavation grid sanity repair on load and palette compaction

## spec

Filed from `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` row FL-3 (belt hygiene pass 2026-10-09; items/ live+closed and src/ re-checked: not filed, not built). The row is the spec:

| FL-3 | Robustness: on load, check that the dig map makes sense. Depth must be 0–4, liquid must not exceed depth, and each liquid must be a known one. Repair anything wrong with one logged line instead of silently zeroing a wrong-sized grid. Also drop removed liquids from the per-map liquid list, so a long campaign never runs out of its 254 slots. | PostLoadInit pass in RM_MapComponent_Excavation, plus palette compaction and remap. Add selftest cases with a corrupted grid. | S | low | FlowWorks | `EnsureGrids` (RM_MapComponent_Excavation.cs:210) silently reallocates a wrong-sized grid. `PaletteKey` (:253) returns 0 once 254 is reached and never compacts. There is no clamp or repair on load (grep sanit/clamp/repair). Not in EXCAVATION_LEGACY_MIGRATION_FLAG_1, which only covers legacy rehydration. |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; PatchApplier for any Harmony.

## verify

- Offline: Selftest with corrupted grid passes: depth clamped 0-4, liquid<=depth, unknown liquid repaired, one log line; palette compaction frees slots.
