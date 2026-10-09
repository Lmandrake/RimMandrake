# HERD_FEAR_TICK_OFFSET_1 — EH-7: Offset herd fear scan by thingIDNumber

## spec

Filed from `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` row EH-7 (belt hygiene pass 2026-10-09; items/ live+closed and src/ re-checked: not filed, not built). The row is the spec:

| EH-7 | **Spread out the herd fear checks (hygiene).** Every calm-gated herd animal scans for threats on the same tick (`TicksGame % 250`). Offset each animal by its ID so a large herd does not cause a hitch every 250 ticks. | one-line change | S | none | EnvironmentalHazards | `RM_CompGatherableCalmGated.cs:106`; `THORNBUG_FEAR_SCOPE_1` covers how far the fear reaches, not when it is checked |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; PatchApplier for any Harmony.

## verify

- Offline: RM_CompGatherableCalmGated scan uses (TicksGame + thingIDNumber) % 250; build clean.
