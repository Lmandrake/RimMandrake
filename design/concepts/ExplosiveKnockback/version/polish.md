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
