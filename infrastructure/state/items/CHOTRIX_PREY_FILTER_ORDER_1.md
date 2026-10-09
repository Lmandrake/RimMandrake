# CHOTRIX_PREY_FILTER_ORDER_1 — SC-4: Chotrix FindPrey checks distance before IsLone

## spec

Filed from `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` row SC-4 (belt hygiene pass 2026-10-09; items/ live+closed and src/ re-checked: not filed, not built). The row is the spec:

| SC-4 | *(hygiene/perf)* The chotrix's prey search checks "is this animal alone?" — itself a walk over every pawn — for every pawn on the map before checking distance, so a crowded map costs pawns². Check distance first, loneliness last. | reorder filters in FindPrey | S | low | Scarlands | `RM_Chotrix.cs:160-200` (IsLone inside the all-pawns loop, before the distance test); CHOTRIX_HUNT_TARGET_REVALIDATE_1 is about re-checking after selection, not this cost |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; PatchApplier for any Harmony.

## verify

- Offline: RM_Chotrix.FindPrey reorders filters; behaviour identical; build clean.
