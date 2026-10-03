# GELATINOUSSLIME_GLURRO_SALVE_1 — the glurro and the resistance economy: milked and rendered for a slime-resistance salve

**Free tier**, `mandrake.rm.gelatinousslime`. Design: `design/Jawa/worldbuilding/biomes/gelatinousslime_bedazzle_review_2026-10-02.md` §1 (a) 3, §3 (resistant row), §4 row 0a, §8.
Caused by `GELATINOUSSLIME_SCORING_SITTING_1` (turn 1). Ruling: build first, land what was decided (decision taken by question card 2026-10-02 ~14:25 PDT). Underlying rulings: sheet `the_slime.md` §4 (owner's rulings on the filter-feeder family, the flying aristocracy, the resistant characters), Q14 of `design/RimMandrake/biome_mod_architecture.md` §7 (by card 2026-09-23: the free def stays donor-free, holes filled with creatures of ours), Q11a (every `RM_` roster rich enough to stand alone). Sheet §4: the resistant natives, *"rendered down or milked, … supply the resistance economy"*.

## What exists

The resistant characters exist only as `AA_` donors on the twin (oomb, vulloth, bezzul), barred from the free
def by Q14. Nothing is milked or rendered anywhere (searched `src/`, 2026-10-02). `HediffComp_Slimification`
and `SlimeUtility` are the reading clock any salve slows.

## spec

1. `RM_Glurro`: a solid-bodied, iron-crusted crawler that grazes the liquid channels and is never read.
2. Tamed: **milked** (`CompMilkable` shape) for `RM_GlurroSalve`, a salve that **slows** slimification while
   applied (it never stops it; the antidote stays the only cure). XML-first; a small hook into the
   slimification clock if no vanilla stat can carry the slowing.
3. **Rendered down** in the slime pit (pairs with `GELATINOUSSLIME_PIT_SOLVENT_1`): a glurro carcass part →
   the salve's concentrate (stronger, rarer).
4. Wire inline on `RM_GelatinousSlime/wildAnimals`. Numbers `// INVENTED`.

## criteria

- `jawa/get_defs` on the creature, the salve and the concentrate: `foundCount` 3.
- Live: a salved pawn on liquid slime advances slimification measurably slower than an unsalved control.
- Art from `gelatinousslime_turn1_2026-10-02.csv`.
