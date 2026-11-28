# Cuisine: next version (after the current build)

Divergent work: anything that extends the current vision of Cuisine. Each entry is a pre-written ticket with its acceptance test, who proposed it, when, and why it was not taken now. **Protected: append-only for agents; removing an entry is his call.** No version opens from this file: his review of the scope comes first.

## CUISINE_STICKS_BUILD_HUNGRY_SELF_ROAST: a hungry colonist roasts one roast-on-a-stick at a campfire instead of eating raw (moved from the ledger 2026-11-27)
- **Title (ledger):** "Self-serve roast: a hungry colonist with no meal in reach walks to a campfire, roasts one roast-on-a-stick (raw food + skewer) and eats it, instead of eating raw; new JobDriver + food-search rule; after CUISINE_STICKS_MERGE_SEVEN_INTO_ONE_ROAST".
- **Filed:** OWNER, 2026-10-27T01:00:30Z, kind design, for BENCH. Decided by his card: "Should roast on a stick become the meal anyone can make? -> Anyone roasts, then self-serve (Recommended)".
- **Prerequisite:** `CUISINE_STICKS_MERGE_SEVEN_INTO_ONE_ROAST` is done (closed at `140cb1d156`): one skewer and one ingredient-named roast-on-a-stick, two recipes.
- **Sweep:** home `mod:Cuisine`, group `roast-on-a-stick` (2026-11-24).
- **What is built:** none of the self-serve job. Cuisine has code (`src/RimStarWars/Cuisine/`). `git grep -il "selfroast\|self-serve\|SelfRoast" -- src` found no file (2026-11-27).
- **What it needs:** a new JobDriver (walk to a lit campfire, roast one stick from raw food and a skewer, eat it) and a food-search rule that picks it over raw food when no meal is in reach.
- **Acceptance test:** none here; when the version opens, the bar is a plain sentence such as "a hungry colonist with raw food, a skewer and a lit campfire, and no meal in reach, roasts and eats a stick instead of eating raw".
- **Moved whole from the ledger 2026-11-27** (Conductor call on the doubtful tickets of `design/pre_design_concepts/moved_2026-11-26.md`). The ticket had no prose file; its other events were the reassignments of the retired FOUNDRY seat and the Designer-bucket note.

