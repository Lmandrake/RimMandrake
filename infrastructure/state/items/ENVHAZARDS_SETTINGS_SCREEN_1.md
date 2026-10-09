# ENVHAZARDS_SETTINGS_SCREEN_1 — EH-3: EnvironmentalHazards settings screen: sections, search, per-section reset, "applies now / new maps only" tags on ~75 controls

## spec

Filed from `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` row EH-3 (belt hygiene pass 2 2026-10-09; items/ live+closed and src/ re-checked: not filed, not built). Scope: Adopt the shared SettingsKit (SETTINGS_SCREEN_KIT_1; build after it lands) in RM_EnvironmentalHazardsMod. The single truce-radius reset button becomes the per-section reset. FeverWood follows as its own pass.

The row:

| EH-3 | **A settings screen you can find things on.** Environmental Hazards has about 75 controls on one scrolling page. Add one shared helper used by every mod: collapsible sections, a reset button per section, a search box, and a small "applies now / new maps only" tag on each control. | shared UI helper, then mod-by-mod adoption | M | low (UI only) | EnvironmentalHazards, FeverWood, then all mods | `RM_EnvironmentalHazardsMod.cs` (75 Checkbox/Slider calls, a single reset button for the truce radius only); `MOD_OPTIONS_RETROFIT_1` requires the now/new-maps wording but specifies no shared helper; no item covers search, sections or per-section reset |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; PatchApplier for any Harmony.

## verify

- Offline: EnvironmentalHazards builds clean; sections collapse; search works; each section resets; each control carries its scope tag.
