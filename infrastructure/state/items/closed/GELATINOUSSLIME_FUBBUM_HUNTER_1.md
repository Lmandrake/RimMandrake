# GELATINOUSSLIME_FUBBUM_HUNTER_1 — the fubbum: the body's one hunter of the little herds

**Free tier**, `mandrake.rm.gelatinousslime`. Design: `design/Jawa/worldbuilding/biomes/gelatinousslime_bedazzle_review_2026-10-02.md` §3 (conventional munchers row), §4 row 0a, §8.
Caused by `GELATINOUSSLIME_SCORING_SITTING_1` (turn 1). Ruling: build first, land what was decided (decision taken by question card 2026-10-02 ~14:25 PDT). Underlying rulings: sheet `the_slime.md` §4 (owner's rulings on the filter-feeder family, the flying aristocracy, the resistant characters), Q14 of `design/RimMandrake/biome_mod_architecture.md` §7 (by card 2026-09-23: the free def stays donor-free, holes filled with creatures of ours), Q11a (every `RM_` roster rich enough to stand alone). Sheet §4: *"browse the pseudo-plants and hunt the pseudo-herds"*.

## spec

1. `RM_Fubbum`: a low, leathery, wide-footed stalker, resistant by its hide, that hunts gelatid herds at their
   night pooling. Rare (about 0.15, `// INVENTED`); never hunts a pawn first (`manhunterOnTameFailChance` and
   predator prey limits set so colonists are not its prey).
2. Wire inline on `RM_GelatinousSlime/wildAnimals`.
3. Check for an existing behaviour before writing C# (night pooling is the visitors'/gelatid's; reuse it).

## criteria

- `jawa/get_defs` `ThingDef/RM_Fubbum` `foundCount` 1; it is a predator whose prey list includes `RM_Gelatid`.
- Art from `gelatinousslime_turn1_2026-10-02.csv`.
