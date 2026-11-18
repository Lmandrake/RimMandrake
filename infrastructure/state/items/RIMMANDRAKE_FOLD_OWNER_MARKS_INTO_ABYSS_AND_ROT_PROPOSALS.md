# RIMMANDRAKE_FOLD_OWNER_MARKS_INTO_ABYSS_AND_ROT_PROPOSALS

## spec

WHY: the owner approved the cleanse proposals as THE PLAN with five marks (2026-11-17; `design/concepts/CLEANSE_PLAN_OWNER_2026-11-17.md`, `design/concepts/Abyss/cleanse/owner_marks.md`, `design/concepts/TheRot/cleanse/owner_marks.md`). The proposals do not reflect them yet.

DO, as the cleanse author (brief: `src/RimMandrake/rimflow/roles/designer_cleanse.md`), editing ONLY files under `design/concepts/Abyss/cleanse/` and `design/concepts/TheRot/cleanse/` (never `owner_marks.md`):
- Abyss: `fold_lamp`, `vine_turning`, `glowberry_item` move from next version to 0.1.0. `heat_observation` stays next version (switched off; its own row says the observation is then granted on load, so the fold lamp must be usable in 0.1.0 without it: state how). Add a fishery of creepy dark creatures to 0.1.0 as a new capability (his words: "YES TO FISH (WEIRD CREATURES)!", "it's not that big of a deal to make some creepy dark critters to fish for"); the project rule for fishables applies: every catch has a living, moving counterpart in the biome. Invent the creatures in the franchise-free RM_ tier.
- TheRot: `pleasure_brew` moves from recommended-retire to 0.1.0.
- Every file the brief requires stays consistent: census fates, bars (a bar is an experience, never a tuning number), checks, next_version.md, tickets.md, owner_pages.md within its length, counts in result.json equal to the files. Change nothing he did not mark.

## verify

Acceptance test (fails on base 9ca1e4a2d1: the census fates differ from his marks): `python3 src/RimMandrake/rimflow/designer_cleanse.py check design/concepts/Abyss/cleanse` and the same for TheRot both pass, AND `python3 - <<'PY'` reading both `census.json` files shows fold_lamp, vine_turning, glowberry_item and pleasure_brew with a kept fate (not next_version, not recommend_retire), heat_observation still next_version, and at least one Abyss row whose `what` names a fishery or catch with a kept fate. Expected: 2 checks pass, 6 fate assertions true.
