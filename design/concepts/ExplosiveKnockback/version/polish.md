# Explosive Knockback: Polish list

Polish improves play but is not part of passing 0.1.0. Each entry is moved here only with his confirmation, marked in the decision (owner, by card 2026-11-13).

*Empty at entry on 2026-11-13: no open judge gap sorted as Polish.*

## Not worth the touch (ticket sweep 2026-11-22)

This section is a record, not the Polish list above: nothing here was moved by his confirmation. Each line is a dropped ticket that fails test 1 of `standing_rulings.md` §Touching code has a cost. Nobody fixes these lines.

- RIMMANDRAKE_CLEAR_KNOCKBACK_HAUL_MEMORY_STATIC_OUTLIVES_GAME: `RM_PawnFlyerPatches.Hauling` is a static Dictionary<Pawn,Job>. An entry outlives a pawn that dies mid-flight, and a save taken mid-flight loses the haul resume. A landing removes the entry (ResumeHaul), so ordinary play leaves none. No failure is on record.
- RIMMANDRAKE_SHOVE_PAWNS_STANDING_ON_COVERS_IN_BURNING_GAS: a person standing on a covered superdeep cell is skipped `in_pit` by a burning-gas shove (KbPlanner.PawnSkipReason). It needs gas over a pit cover with a person on it. A blast still breaks the cover. No failure is on record.
- RIMMANDRAKE_STOP_KNOCKBACK_HIT_ACROSS_SANDBAG_NO_CONTACT: `RM_KnockbackMath.Resolve` backs a pawn off a sandbag (lane 4 | sandbag 5 | pawn 6) and still reports the hit, a small impact on a pawn it never touched. The blind cycle 4 judge sorted it Polish (a design call). No failure in play is on record.
- RIMMANDRAKE_TEST_JOLT_DECAY_DOC_PROMISES_UNTESTED: the doc of `RM_KnockbackMath.JoltOffset` promises a decaying shake, and only the bound is tested. No bar requires decay.
- RIMMANDRAKE_RETAKE_KNOCKBACK_EXAM_NO_SCENARIO_READS_LEAF: the Designer's stage 4 Cold Reader exam is frozen against the tree from before the barrage p99 rewording. No exam scenario reads that leaf, and nothing refuses on it (`maturation.py next`, 2026-11-22). Retake it when the next version's Designer pass opens.
- RIMMANDRAKE_FIND_DARK_HAZE_EAST_OF_GAS_CHAIN: the dark blotches are explosion smoke that clears (visit 3: gone 1500 ticks later, measured), plus Extra Explosion Effects' Fleck_EEE_Soot and crater flecks (about 20 s, measured on his Gimme Some Slack walk of 2026-11-20). This mod does not draw them. His art bar on them sits on RIMMANDRAKE_ABSORB_EXTRA_EXPLOSION_EFFECTS_OWN_FLECKS (next version).
- RIMMANDRAKE_NOTE_KNOCKBACK_FIRE_SWITCH_MISSES_UNPATCHED_FIRE: "Fire throws at half strength" off zeroes only a fire type our patch tunes (Flame and its children). Another mod's fire type with no extension and no Flame parent throws at the other-mods percent and ignores the switch. No such type is known, so nothing failed (blind cycle 6, lane 1 row L1_FIRE_SWITCH_ON_UNPATCHED_FIRE_TYPE).
- RIMMANDRAKE_NOTE_KNOCKBACK_GAS_SKIPS_PAWN_ON_INTACT_COVER: a burning gas clump does not shove a pawn that stands on an intact pit cover, because the plan skips any pawn on a superdeep cell as `in_pit`, covered or not. A blast breaks that cover, so only gas differs. Nothing failed (blind cycle 6, lane 1 row L1_GAS_SHOVE_PAWN_ON_INTACT_COVER).
- walk_storeroom_raid, small list only (2026-11-23): C_OFF_IMPACTS_NO_THROWS counts a stack dropped by its own destroyed vanilla shelf as moved (0 of 11 on every full-list run, so no bar needs the touch; `ev.off_moved` now names it).
- walk_storeroom_raid (2026-11-23): GAS_CLUMP_BY_CLUMP's mean-distance order FAILs on one late straggler cell (1 of 8 orders on the small list, 0 of 18 on the full list); not touched.
- 2026-11-24, steward reading after in-game visit 6: the rebound keeps 70% of the cells left, while its bar speaks of speed. Polish, by the Conductor's call; no bar moves and no ticket is filed.

## Judged for 0.2.0 by the Conductor (2026-11-24)

His words, 2026-11-24 (OWNER:1795565769863524396): *"Include all polish items too, but judge each of them first as relevant or not (or card me if you don't want the responsibility)"*. The Conductor judged each line above. This section is the record of that call; the lines above stay as they were written.

- **Work of 0.2.0** (bars in `../record.json`): the burning-gas shove of a person on an intact pit cover (`gas_shoves_pawn_on_pit_cover`; both lines above that name it); the hit across a sandbag (`no_impact_without_contact`); the rebound bar's sentence (`rebound_goes_shorter`); the haul-memory static, only if the carried-thing work changes that code (`carried_thing_own_arc`); the Cold Reader exam retake (RIMMANDRAKE_REWORD_KNOCKBACK_REBOUND_LEAF_THEN_RETAKE_WHOLE_EXAM); the dark haze line is answered by our own blast show (the `blast_show_*` bars).
- **Not relevant, left as they are:** the jolt-decay doc line; the fire switch on another mod's fire type; the two storeroom-raid check nits (raid tests are paused; his word: *"Drop one gas check."*).
- **Dropped on his word:** a check that throws with an Outer Rim weapon (*"Drop No check throws thing... we will own all our own weapons."*).
- 2026-11-24 (RIMMANDRAKE_AUTOBUILD_EXPLOSIVEKNOCKBACK_FOURTEEN_BARS_LEFT): `selftest_explosiveknockback_blind_cycle1.py` (T_BLIND_CYCLE1_OFFLINE, decides no bar) is red: it reads `version/blind_challenge/cycle_1/`, which the 0.2.0 opening (a691b05c15) moved to `version/previous/0.1.0/blind_challenge/cycle_1/`. Repoint it or drop it from the table.
- 2026-11-24 (art judge, blast show renders, `version/art/blast_show_art_verdict_2026-11-24.json`): glowing specks baked into the crater scars; scorch_1 has a pale dusty rim; scorch_2 and scorch_3 lean to ink splatter; the dirt bits are brownish, not neutral grey; smoke_f has a weaker pale edge and smoke_e_r2 a weaker dark-base shading; the soot tiles stop short of their edges, so the repeat may show when tiled; soot_c is grey rather than black.
- 2026-11-25 (RIMMANDRAKE_DECIDE_KNOCKBACK_FRAME_ROW_HIS_CARD_SET_IT): `testq_blocks.py check` skips a mod that is not past blind, so three hand-copied testq blocks (sc_storeroom_bomb_pit, sc_save_in_air, sc_walk_frames) went unseen until selftest_stage6_checks; no route reads scene_save_in_air.py or a `--frames-only` walk, so SteveDesktop cannot take those two.

## Blind challenge 0.2.0, cycle 1 (2026-11-25)

- RIMMANDRAKE_CHECK_KNOCKBACK_RULES_MAPPING_OFFLINE_LIKE_KERNEL: the offline settings sweep checks every `Kernel()` field against its own setting but not the `Rules()` fields beyond the three sheet switches; a `Rules()` that fixes `goodsReboundKeepPercent` at 100 stays green offline (planted, blind cycle 1). The live `sc_settings_sweep` and `sc_storeroom_mortar_rebound_legs` decide it.
- RIMMANDRAKE_CROSSCHECK_KNOCKBACK_REBOUND_LEFT_FLYER_GRADES_ITSELF: `V_SHORTER` of `sc_storeroom_mortar_rebound_legs` compares each rebound with the flyer's own journal `left`; a flyer that counted the whole throw as left would pass it (planted, blind cycle 1). The shipped flyer logs the true cells left.
- RIMMANDRAKE_SAVE_KNOCKBACK_LANDING_IMPACT_FACTOR_ACROSS_RELOAD: `landingImpactFactor` is not saved, so a factor-0 throw saved in mid-flight bruises a walked-in pawn at factor 1 after a reload.

## Scene runner live proof (2026-11-26)

- `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackScenes.cs` header says "NOT YET RUN LIVE"; the suite ran live on ArchSmall 2026-11-26 with the same rows as knockback_runner.py. Drop that sentence at the next EK source change (a comment edit alone moves the DLL srchash).

## Scene rows read by the judge (2026-11-26)

- `src/RimMandrake/ExplosiveKnockback/proof/scene_storeroom_mortar_rebound_legs.py` row "V_SHORTER all ... UNLAID (the scene made no rebound to compare)" is `row(False, ...)`, so the judge now reads it MOD FAILURE; its own words say the opportunity was not laid (INVALID, APPARATUS FAULT). risk: a run whose staging made no rebound counts against the mod. The call moves how the rebound bar is decided, so it waits for the rebound bar ruling (RIMMANDRAKE_RULE_REBOUND_NEAR_WALL_OUTFLIES_FIRST_LEG).
