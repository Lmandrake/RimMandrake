# RANKLESS_DLC_SETTING_REMOVE_1 — LP-3: Delete the no-Royalty/Ideology deepfire setting

## spec

Filed from `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` row LP-3 (belt hygiene pass 2026-10-09; items/ live+closed and src/ re-checked: not filed, not built). The row is the spec:

| LP-3 | Delete the "colonies with no Royalty or Ideology still enjoy it" setting — every player has every DLC, so it can never matter. | remove field, Scribe, checkbox; RanklessAllowed collapses to true | S | low | LuminousPigment | `LuminousPigmentMod.cs:414`, `RM_DeepfireRules.RanklessAllowed`, `SumptuaryEngine.cs:108`; owner DLC ruling (CLAUDE.md); not in DEAD_OR_INERT_SETTINGS_1 |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; PatchApplier for any Harmony.

## verify

- Offline: LuminousPigment builds clean; setting field, Scribe and checkbox gone; RanklessAllowed collapses to true.
