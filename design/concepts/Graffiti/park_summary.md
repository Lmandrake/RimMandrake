# Graffiti: parked for you (second_refusal)

the coverage judge refused 2 times while you are away (no sitting: the owner has not interacted for 45+ min (last: 2026-11-15T08:37:31Z (chat prompt, 54 min ago))). Nothing runs on it, no Designer run and no judge, until your word on RIMMANDRAKE_SEED_GRAFFITI_INTO_MATURATION_ADVANCED_BUT_UNLISTED. Item RIMMANDRAKE_SEED_GRAFFITI_INTO_MATURATION_ADVANCED_BUT_UNLISTED, stage 5 (Lock).

## QUICK LOOK OFFERED

Enough code exists (18 built capabilities: inv_mark_on_wall, inv_mark_art_set, inv_beauty_and_craft, inv_ideo_sigils, inv_spree, inv_joy_and_idle_tag, inv_player_orders, inv_viewer_mood, inv_social_layer, inv_visitors, inv_raid_marks, inv_breach_bias, inv_scrub_protection, inv_temperament, inv_wall_loss, inv_settings, inv_standalone, inv_weathering). A short look in game could settle these 2 gaps at once.

## Settled

- Stages accepted: 0 Read, 1 Argue the idea, 2 Argue the edge, 3 Write, 4 Exam.
- Root: Graffiti turns a colony's walls into a record of its people: punk tags and ideoligion sigils whose quality comes from the painter's art skill; marks about people (mockery, tribute, memorials, insults) that move mood, opinion and now and then a confrontation; and raiders who oppress the colony with threats and marks they leave behind for future attacks; all readable at play zoom in any RimWorld game.
- 10 decisions on record, 28 tree leaves, 19 inventory capabilities.

## Refused, and why

The coverage judge (rm-coverage-judge-1794734941) says not covered: 22 of the 24 claimed fixes hold: g2–g17 and g19–g24. Two are still open. g1: the flagship's 'designated piece' uses the player paint order, so after_the_raid newly exercises only 2 capabilities (rule: at least 3), and its overlap of 0.33 exceeds the 0.25 limit with no overlap_why. g18: the edge-on control and the option-D assertion were added, but the far-side clause has no control. The live paint paths refuse only edge-on faces and NoWall, and the renderer draws a hidden-face mark, so a south-only cell may take paint. Two inconsistencies are not raised as gaps because they decide nothing: tree.json answer_wall.scenario still says 'run until an answer completes' while its oracle and sc_answer_wall require all four answers; and sc_breach_bias_raid cites requirement stands_alone_settings although it tests the lure, not a switch (breach bias has no leaf of its own, and coverage_rest binds it correctly).
1. after_the_raid still fails the showcase rules: sc_spree_corridor's designated piece uses the player paint order, so inv_player_orders is not new in after_the_raid (scenes.json showcases spree_corridor and after_the_raid; sc_spree_corridor start and control; ids inv_player_orders; returns to stage 3)
2. The far-side clause of inv_mark_on_wall and sits_on_wall ('a wall's far side take no paint') has no live control, and the live code that refuses paint would not refuse it (scenes.json sc_wall_closeup start and control; record.json inv_mark_on_wall; tree.json sits_on_wall; ids inv_mark_on_wall, sits_on_wall; returns to stage 3)

## Smallest fixes

- The Designer can fix 2 gap(s) at stage 3 without you: 1, 2.

## What you must decide

- Then one note on RIMMANDRAKE_SEED_GRAFFITI_INTO_MATURATION_ADVANCED_BUT_UNLISTED (your words, or a card): rework it, certify it as it stands, waive a gap, or stop.
