# ZUURRIK_OFF_FINISH_SWARM_1 — SS-2: Turning zuurrik off lets the current swarm bury itself

## spec

Filed from `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` row SS-2 (belt hygiene pass 2026-10-09; items/ live+closed and src/ re-checked: not filed, not built). The row is the spec:

| SS-2 | **(hygiene)** Turning the zuurrik off while a swarm is awake leaves that swarm up forever; switching off should stop NEW wakes but still let the current swarm bury itself. | nothing | S | low | Stillsand | `RM_MapComponent_Zuurrik.cs:84` returns on `!Active` before `TryBury`; `Active` includes `zuurrikEnabled`. VERDICTS #35/#36 cover burial watch + growth, not this. |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; PatchApplier for any Harmony.

## verify

- Offline: RM_MapComponent_Zuurrik: !zuurrikEnabled stops new wakes but TryBury still runs for an awake swarm.
