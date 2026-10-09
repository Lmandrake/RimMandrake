# STILLSAND_LOOKUP_CACHE_1 — SS-1: Cache loud-draw defs and sand-swim registry lookup

## spec

Filed from `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` row SS-1 (belt hygiene pass 2026-10-09; items/ live+closed and src/ re-checked: not filed, not built). The row is the spec:

| SS-1 | **(hygiene, perf)** Stop the sand leviathan's "what is loud nearby" check from reading every item type in the game each time it re-aims, and stop the sand-swim check doing a slow reflective call on every path cell; look both up once and cache them. | nothing | S | low | Stillsand | `RM_EventRemainder.cs:172` `RM_LoudDraws.First` loops `DefDatabase<ThingDef>.AllDefsListForReading` (~600-mod list) per call from `RM_SandLeviathan.cs:231`; `RM_SandSwimRemainder.cs:38` `registryGet.Invoke(null, new object[]{map})` inside a pathing postfix. No item names either (index grep LOUD/DRIFT_SWIM: none). |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; PatchApplier for any Harmony.

## verify

- Offline: RM_LoudDraws.First no longer scans all ThingDefs per call; registryGet resolved once; build clean.
