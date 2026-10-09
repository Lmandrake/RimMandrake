# ELDER_NOVELTY_KEY_ALIAS_1 — DI-5: Elder novelty keys follow RM_DefAliasDef renames

## spec

Filed from `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` row DI-5 (belt hygiene pass 2026-10-09; items/ live+closed and src/ re-checked: not filed, not built). The row is the spec:

| DI-5 | *(code hygiene)* A renamed creature or item is not "new" to the Elder again. When a def moves from RSW_ to RM_ in a biome sitting, the Elder's "seen it" ledger follows the rename instead of paying a second time. | Pass novelty keys through the existing `RM_DefAliasDef` table when the ledger loads. | S | none | DivingInteraction, EnvironmentalHazards (`RM_DefAliases.cs`) | `RM_ElderTradeUtility.NoveltyKey` builds raw `"Lifeform:"+kindDef.defName` strings that are saved in `seenKeys` (`RM_GameComponent_BrineElders.cs:114`); RSW_→RM_ renames are ongoing per the Q12–Q15 rulings; the alias table already exists and is data-driven |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; PatchApplier for any Harmony.

## verify

- Offline: DivingInteraction builds clean; a seenKeys entry using an old RSW_ defName counts as seen after alias remap; toggle in Mod Settings.
