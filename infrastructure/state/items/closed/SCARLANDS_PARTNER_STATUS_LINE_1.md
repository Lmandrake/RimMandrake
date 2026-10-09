# SCARLANDS_PARTNER_STATUS_LINE_1 — SC-3: Scarlands settings show partner-mod presence

## spec

Filed from `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` row SC-3 (belt hygiene pass 2026-10-09; items/ live+closed and src/ re-checked: not filed, not built). The row is the spec:

| SC-3 | The settings screen says whether its partner mods are actually loaded (FlowWorks for the reaction pools, the track grid for Settling footprints), so "why are there no pools?" answers itself. | one status line per optional partner | S | none | Scarlands | `RM_WarscarMod.cs:313` only says pools "need FlowWorks"; no presence check in the settings UI |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; PatchApplier for any Harmony.

## verify

- Offline: One status line each for FlowWorks and the track grid saying loaded or not.
