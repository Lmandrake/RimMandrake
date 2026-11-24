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
