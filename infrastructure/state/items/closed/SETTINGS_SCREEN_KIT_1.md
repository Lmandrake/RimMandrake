# SETTINGS_SCREEN_KIT_1 — X-12: Shared settings-screen kit: collapsible sections, search box, per-section reset, and a "now / new maps only" tag per control

## spec

Filed from `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` row X-12 (belt hygiene pass 2 2026-10-09; items/ live+closed and src/ re-checked: not filed, not built). Scope: Build ONE helper under src/RimMandrake/_Shared/SettingsKit (linked <Compile Include>, like HarmonyResilience) that a mod calls from DoWindowContents. Adopt it first in FlowWorks, replacing the reflection-based DrawSectionReset added by FLOWWORKS_SETTINGS_SCOPE_RESET_1. Per-mod adoption is its own item each (CREATURE_BEHAVIORS_SETTINGS_SCREEN_1, ENVHAZARDS_SETTINGS_SCREEN_1). Do not rewrite any mod screen here beyond FlowWorks.

The row:

| X-12 | **One settings-screen kit for every mod**: collapsible sections, a search box, a reset per section, and a small "now / new maps only" tag on each control. CreatureBehaviors (~106 controls) and EnvironmentalHazards (~75) need it most. | shared UI helper, adopted mod by mod | M (kit) + S per mod | low | all; CB-5, EH-3, FL-5, LP-5 are the per-mod rows | MOD_OPTIONS_RETROFIT_1 asks for the scope wording but no shared kit, search or reset |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; PatchApplier for any Harmony.

## verify

- Offline: helper compiles into FlowWorks; a selftest asserts reset restores shipped defaults, search filters labels case-insensitively, and the scope tag never changes a stored value. FlowWorks screen shows collapsible sections, search, per-section reset.
