# The validation ladder — how mass-built content gets checked

The owner made these rulings on 2026-09-01. Each `##` heading below, down to the criteria, is
one tier of the ladder. The cheapest tier is first.

- Check content in batches, never per item.
- The cheapest tier that can answer a question owns that question.
- **A question never rises a tier while a lower one can answer it.**

> "Don't use humans where a screenshot will do." · "Anytime you can review
> something, just go ahead and do so." · "Efficiently and in batches, not
> endless V&V runs."

## L0 — Offline (free, every commit)

- This tier is the XML lint, `validate_patch.py --live --defs`, the selftests and the texture validators.
- These checks already exist. They run before anything touches the game.

## L1 — Resolved-live (the workhorse; ~22 s per cycle for XML)

1. Deploy the XML.
2. **Restart on the minimal list** (`modlist_swap.py --minimal`; 22 s on the 13-mod list of 2026-08-19).
3. Read the resolved defs in batches with `jawa/get_defs`.

- A script proves each live criterion. The item's `live-proof` line names that script
  (`infrastructure/state/live_proofs/<ID>.txt`).
- There is no shared manifest format. The owner's pick of 2026-11-12 deleted the expectations-manifest runner.
- The canonical cycle is in `skills/rimworld-modding/SKILL.md` §2.
- The default read of `jawa/get_defs` is scalar-only. Its deep-serialize upgrade is built (read in the code
  2026-11-23). With `deep=true`, the read also returns nested fields, to 3 levels.

> ⛔ **The `jawa/hot_reload_defs` step is DEAD.** The owner retired the step on 2026-09-03
> as unstable.
>
> - The step hung a 589-mod game for 5 minutes. After that, the game was unable to generate any pawn (`HairDef` was
>   absent from a Type-keyed index). The game reported healthy all the time:
>   `infrastructure/state/items/closed/HOT_RELOAD_DEFS_BREAKS_PAWNGEN_1.md`.
> - L1 loses no ground. A minimal-list restart is 22 seconds, so "zero restarts" was worth less
>   than it sounded.

## L2 — Behavior gauntlet (batched per bridge sitting)

- Use one quicktest map for each batch. Spawn everything new. Step ticks once. Harvest the log once. Take one
  screenshot.
- This tier catches an NRE (a null reference exception), missing or magenta art, and eaten defs (a def that a load error, a patch or a duplicate defName removes from the game, so a spawn of it finds
  nothing: `expectations_l2.py` reads it as NOT-SPAWNED).
- **Art presence is proven HERE, by machine.** Use pixel checks against the screenshot or the atlas, per
  `prove-art-missing-before-generating`.
- A human never hunts magenta squares.

## L3 — Opus evaluation (new class of testing; reserved for Opus-grade judgment)

- This tier judges art quality, style coherence with the shipping game, and thematic concepts. The builder's grade (the model class that
  built the work) is not enough for these calls, but they still need no human.
- **This is an AUTOMATED cycle with the bridge in the evaluator's own hands** (owner, 2026-09-01). An Opus agent does
  the cycle:
  1. The agent takes the bridge (`rimflow bridge take`/`release`, like anyone).
  2. The agent stages the scene on a throwaway map.
  3. The agent runs `jawa/clear_ui` and takes a screenshot.
  4. The agent judges, and returns graded verdicts as data.
- No human is in the loop. There are no hand-built inputs.
- If a request for this tier also holds something mechanical, push that part back down to L2.
- **L3 is also the default pre-human gate:** content reaches L4 only after an Opus pass.
- The exception: **unless the owner is asking to help**. If he asks to help, he is never gated out. His offer of eyes
  beats the ladder.

## L4 — Human (the owner) — reserved, and staged as REVIEW ENVIRONMENTS

Reserved for what absolutely needs him: **gameplay, fun, overall thematic
coherence, UI questions.**

When he reviews, he gets a **review environment**, not a grid. A review environment holds related content, composed in
context on a staged map. His words: "Make the animals be in a
mock-up biome just like they should be, so the human can review the entire
ecosystem all together. Put two little homes nearby, of two different faction
styles, so they can be reviewed as well as the race that shows up within and
their equipment. Then put a tile augmentor relevant to that biome together so
that it too can be reviewed... Grids are ok, but they don't really get at the
interactions that need to be studied."

So a sitting of this tier is one staged scene for each content cluster.

- The scene holds the biome, its ecosystem, the factions' dwellings, the resident race, the equipment and the
  tile mutators that are relevant to the biome. A tile mutator is the game's world-tile feature that changes how a
  map on that tile generates (a river, a coast, a cave system, an ancient ruin). His "tile augmentor" means a tile
  mutator.
- Build the scene through the bridge on a throwaway map.
- A machine has already passed everything in the scene at L0–L3.

## Criteria (for MASS_VALIDATION_LADDER_1)

`MASS_VALIDATION_LADDER_1` (the batched validation ladder) reads done in the ledger (2026-11-23).

- A batch of builds validates through L2 in one bridge sitting, with zero restarts.
- `jawa/get_defs` reads nested fields (stages etc.) after its upgrade.
- ~~One measured `hot_reload_defs` trial on the full list, owner-blessed.~~
  - ⛔ **VOID — the trial ran 2026-09-03 and the capability was retired on its result.**
  - The retirement is the owner's ruling (`skills/rimworld-modding/SKILL.md` §2).
  - Nothing is owed here.
- First review environment staged and reviewed by the owner.
