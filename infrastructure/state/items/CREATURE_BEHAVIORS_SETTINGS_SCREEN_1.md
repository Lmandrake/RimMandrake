# CREATURE_BEHAVIORS_SETTINGS_SCREEN_1 — CB-5: CreatureBehaviors settings screen usable: group ~106 controls by mechanic, search, reset per group, which creatures use each mechanic, and whether off removes effects in play or only stops new ones

## spec

Filed from `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` row CB-5 (belt hygiene pass 2 2026-10-09; items/ live+closed and src/ re-checked: not filed, not built). Scope: Adopt the shared SettingsKit (SETTINGS_SCREEN_KIT_1; if it is not built yet, build only after it lands) in RM_CreatureBehaviorsMod.DoWindowContents (1019 lines, 106 Checkbox/Slider calls, one scroll list, no search, no reset). Tooltips gain the in-play / new-only wording; the creature list per mechanic is read from loaded defs, never hand-kept.

The row:

| CB-5 | Make the settings screen usable. Group the ~106 controls by mechanic, add a search box and a "reset this group" button, show which loaded creatures use each mechanic, and have each tooltip say whether turning it off removes effects already in play or only stops new ones. | UI work in DoWindowContents. Text is drawn from the existing toggles. | M | low | CreatureBehaviors | `RM_CreatureBehaviorsMod.cs` (1019 lines, 106 Checkbox/Slider calls, one scroll list with GapLines, no search and no reset); other mods already ship reset buttons (e.g. `EnvironmentalHazards/Source/RM_EnvironmentalHazardsMod.cs`); `MOD_OPTIONS_RETROFIT_1` asks for toggles but not search/reset |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; PatchApplier for any Harmony.

## verify

- Offline: CreatureBehaviors builds clean; every control sits in a named group with a reset; search narrows the list; each toggle tooltip states in-play vs new-only.
