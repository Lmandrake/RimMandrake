# WARSCAR_BIOME_CHECKLIST_1 — SC-2: Warscar cross-biome list as a checklist

## spec

Filed from `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` row SC-2 (belt hygiene pass 2026-10-09; items/ live+closed and src/ re-checked: not filed, not built). The row is the spec:

| SC-2 | The "spread the war's leavings to other biomes" setting lets you tick biomes from a list instead of typing their internal names into a text box, where a typo silently matches nothing. | copy LanternDeeps' existing biome checklist widget | S | none | Scarlands | `RM_WarscarMod.cs:133,475-478` free-text `crossBiomeBiomeList`; `LanternDeeps/Source/LanternDeepsMod.cs:462-505` already has a sorted biome checklist; DEAD_OR_INERT_SETTINGS_1 covers rarity, not this |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; PatchApplier for any Harmony.

## verify

- Offline: RM_WarscarMod settings show a sorted biome checklist (LanternDeeps widget pattern) writing the same crossBiomeBiomeList storage.
