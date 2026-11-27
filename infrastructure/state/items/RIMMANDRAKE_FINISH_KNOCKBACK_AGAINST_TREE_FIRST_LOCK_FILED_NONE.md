# RIMMANDRAKE_FINISH_KNOCKBACK_AGAINST_TREE_FIRST_LOCK_FILED_NONE

## spec

Explosive Knockback (mandrake.rm.explosiveknockback) was built before the Designer argued it. Its concept tree is
locked: coverage passed on the owner's word past coverage judge rm-coverage-judge-1794599960 (not_covered, 6 gaps, all
claimed fixed in `coverage_fixes.json`), certificate OWNER:1794836946186553250, carried to the current tree by
OWNER:1795575170763326637. The stage 5 lock of 2026-11-13 (run bench-ek-owner-lock-st5-20261113) filed no mod item; this
item is that mod item. It carries the tree to the Maturation Pipeline: every leaf of `tree.json` and every record.json
inventory bar of Design Version 0.2.0 is decided by the mod's own script and its scenes. The mod's open work stays in
`design/concepts/ExplosiveKnockback/version/` (its bars, gaps and polish list); the pipeline works it there.

Spec of record: `design/concepts/ExplosiveKnockback/sheet.md`, `scenes.json` (two showcases: storeroom_bomb_pit,
blast_show), `floor.json`, `version/VERSION.json` (0.2.0, locked 2026-11-24).

Build items filed before this one, each named as a scene's `entry_point_item` in `scenes.json`:
RIMMANDRAKE_ABSORB_EXTRA_EXPLOSION_EFFECTS_OWN_FLECKS, RIMMANDRAKE_BRUISE_KNOCKBACK_LANDING_ON_PAWN,
RIMMANDRAKE_BUILD_KNOCKBACK_CREATURE_MASS_AND_BLAST_POWER, RIMMANDRAKE_CHAIN_FLAMMABLE_GAS_CLUMPS,
RIMMANDRAKE_COVER_KNOCKBACK_BAR_HALVES_NO_LIVE_CHECK_SEES, RIMMANDRAKE_FLING_KNOCKBACK_CARRY_ON_OWN_ARC,
RIMMANDRAKE_FLY_KNOCKBACK_GOODS_WILD, RIMMANDRAKE_FOLD_KNOCKBACK_POLISH_LINES_INTO_ZERO_TWO_THREE_JUDGED_IN,
RIMMANDRAKE_KNOCK_PEOPLE_HEAVY_GOODS, RIMMANDRAKE_LIMIT_KNOCKBACK_STORAGE_CLOSED, RIMMANDRAKE_PROVE_KNOCKBACK_ALL_FLY_PERF,
RIMMANDRAKE_PROVE_PIT_GOODS_RETRIEVABLE, RIMMANDRAKE_REWRITE_KNOCKBACK_PROOFS_REAL_CONTROLS,
RIMMANDRAKE_RULE_REBOUND_NEAR_WALL_OUTFLIES_FIRST_LEG, RIMMANDRAKE_SHRINK_KNOCKBACK_SCENES_ONE_SAVE_IN_AIR,
RIMMANDRAKE_THROW_ALL_HARMFUL_BLASTS.

## verify

design/concepts/ExplosiveKnockback/tree.json

Accepted tree hash 2f443fba60ab70c63c687ce3fc5265c4fe4729e8e526650d80e60672e5e9e810 (`concept_tree.py hash`), sheet hash
22a3215f5781450b7b0d8c4325cbe252d4acbc40e69b17f82360fbd000acd086. Coverage: passed on the owner's word
(OWNER:1794836946186553250), never a judge pass; last judge verdict rm-coverage-judge-1794599960 not_covered.
`python3 src/RimMandrake/rimflow/concept_tree.py gate design/concepts/ExplosiveKnockback` must pass.

## criteria

A1: `concept_tree.py gate design/concepts/ExplosiveKnockback` passes on the hash above (a changed tree needs a new
certificate).
A2: `designer_stage.py showcases design/concepts/ExplosiveKnockback` prints `showcase set accepted`.

Acceptance test: `python3 src/RimMandrake/rimflow/concept_tree.py gate design/concepts/ExplosiveKnockback && python3 src/RimMandrake/rimflow/concept_tree.py hash design/concepts/ExplosiveKnockback | grep -qx 2f443fba60ab70c63c687ce3fc5265c4fe4729e8e526650d80e60672e5e9e810` (1 check; it passes today, because this item records a lock, not a fix).

## refs
file: src/RimMandrake/ExplosiveKnockback/Source/RM_MapComponent_Knockback.cs
file: design/concepts/ExplosiveKnockback/tree.json
file: design/concepts/ExplosiveKnockback/scenes.json
