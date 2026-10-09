# LUMINOUS_PIGMENT_SETTINGS_READOUTS_1 — LP-5: LuminousPigment settings show what numbers mean: glow-family odds at cook-skill levels, hours of light per coat, reset per section

## spec

Filed from `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` row LP-5 (belt hygiene pass 2 2026-10-09; items/ live+closed and src/ re-checked: not filed, not built). Scope: Read-only readouts from the existing steering kernel in LuminousPigmentMod.DoWindowContents plus per-section defaults (use the shared SettingsKit once SETTINGS_SCREEN_KIT_1 lands, or a local reset if first). No new numbers invented.

The row:

| LP-5 | Settings show what the numbers mean: each glow family's real odds at a few cook-skill levels, hours of light per coat, and a "reset this section" button. | read-only readouts from the existing steering kernel; per-section defaults | M | low | LuminousPigment | `DoWindowContents` has no reset/readout (grep reset/preset/search = none); MOD_OPTIONS_RETROFIT_1 has no LP rows |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; PatchApplier for any Harmony.

## verify

- Offline: LuminousPigment builds; readouts show odds at 3 cook-skill levels and hours per coat; each section has a reset to defaults.
