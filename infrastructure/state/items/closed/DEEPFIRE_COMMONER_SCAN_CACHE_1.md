# DEEPFIRE_COMMONER_SCAN_CACHE_1 — LP-7: Cache the saw-a-commoner-in-deepfire answer per map

## spec

Filed from `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` row LP-7 (belt hygiene pass 2026-10-09; items/ live+closed and src/ re-checked: not filed, not built). The row is the spec:

| LP-7 | *(hygiene/perf)* "Saw a commoner in deepfire" makes every titled pawn walk every pawn on the map and re-score their gear on each thought check. Cache one map-wide answer, like room scores already are. | per-map cached flag, refreshed on gear/role change or a short timer | S | low | LuminousPigment | `ThoughtWorkers_Sumptuary.cs:95-115`; `MapComponent_DeepfireStatus` caches room scores only |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; PatchApplier for any Harmony.

## verify

- Offline: ThoughtWorkers_Sumptuary no longer walks all pawns per check; per-map cached flag with short timer refresh; toggle/behaviour unchanged.
