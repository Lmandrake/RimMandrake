# Graffiti: done (2026-11-08 ~06:10 PST)

Closed by the Conductor on the owner's order, 2026-11-08 ~1:20 AM PST: "I don't need the Judge to say it's ok. I just need it to be provably OK... if you have that evidence, call it, stop the spend, close the mod." Item `GRAFFITI_FINISH_RALPH_LOOP_PLAYS_FIRST`.

What this rests on: the ratchet (`ralph/RATCHET.md`), 22 bars (20 must-show, 2 cannot-show), all in Proven, each with the evidence below. Behaviour bars are proven by what the game measured (trace lines, message counts, mood and opinion reads on a real map); look bars by shots, the last two by a blind judge who did not make the work. Build: branch `ralph/graffiti`, game B on SteveDesktop, the `graffiti_solo` list (Graffiti, bridge, every DLC); `93d8b15` unless a bar names a later build; the last two bars on pass 19's build `1ab58b79d6`. Raw output and shots: `D:\ClaudeWork\rimmandrake\ralph_graffiti\` (`p13\`..`p19\`, `shots\`; 64 px per cell is play zoom, `_128` twice that).

## The 22 bars and their evidence

1. mark_actually_appears: trace `1094343 Vex painted IdeoSigil_StencilBox@(127,0,113) (poor)`, visible in `lived_in_south_wall_day19_playzoom.png`.
2. mark_reads_as_deliberate: `lived_in_south_wall_day19_playzoom.png`, `lived_in_corridor_day18_playzoom.png`.
3. mark_reads_at_play_zoom: true for every face-on mark (option D; side faces are scraps by the owner's choice). See caveat 3.
4. mark_sits_on_the_wall: `optionD_materials_close128.png`, `perspective_sweep_wood.png`.
5. marks_visibly_various: 70 marks of 20 kinds at load (`p13/01a_load.txt`); 34 of 12 kinds in `p13/04a_brk.txt`; skew fixed by 38601eb797.
6. mark_carries_no_earth_signage: `warn_0..3.png` (crossed eye, arrows to a splat, skull, maw); no hazard triangle.
7. never_real_world_english: `vandal_0..5.png` illegible scrawl, no "TARTE".
8. mockery_changes_regard: `social_regard_brick_on_karen.png` ("Painted me on the wall x2: -38"), `p13_wall_inspect_mockery.png` ("(5 angered)"), `p13_mocked_needs.png` ("Mocked on the wall by Lark -5").
9. tribute_and_memorial_mean_it: pass 7 tribute +6.6 mood / +22 opinion, jealous -3.7 / -14; `memorial_lark_grief_half.png`; trace `1134188 Karen found the tribute Vex painted for them and stood looking at it`.
10. pawns_answer_the_wall: traces `1094143 Lark painted a mockery of Karen...`, `1115046 Brick confronted Karen...`; `scrub_order_done.png`.
11. raid_mark_troubles_until_retaken: `p13/02*`: Gaup painted IdeoSigil_StencilBox@(149,119) at 1272646; Karen "Enemy marks on our walls -1" at 1284266; Fringe scrubbed it at 1286157, "Reclaimed +4.5", penalty gone; `p13_raid_mark_playzoom.png`, `p13_raid_mark_needs.png`, `p13_raid_retaken.png`. Raider exit forced with lord_set_job (the sequence is proved; natural tagging on exit is not).
12. visitors_read_without_recharging: `p13/03d_caravan2.txt`: insult cost -11, reached the 12-per-visit cap, "read the insult" x1, Hatlencaora -4 to -16.
13. fights_have_people_and_reasons: `social_fight_blows.png`; drafted pawns excluded in code; trace "fight chance 0.39 (a fight too recent) -> words". Thin.
14. stands_alone_and_obeys_settings: classic mode spree of 18 marks, none IdeoSigil/Glyph; painting off for 19,000 ticks gave 0 marks and save/reload kept 60 marks with every total identical (pass 12); social off sent wall mood to 0 (pass 7).
15. making_a_mark_is_its_own_fun: pass 7 joy 0.56 to 0.63 over one paint; "Left my mark" in traces, passes 7-13. Thin.
16. rereads_affect_at_most_daily: 401 reads over 222 pairs, 103 pairs read twice or more, shortest gap 60120 ticks; positive control Karen "Lark's tag on the wall (age 52500)".
17. art_skill_goes_into_the_art: `old/pass11/art_skill_crafts_ladder_beauty.png` Beauty -6..+30; FineArt +0.9 / UglyMark -0.9.
18. each_takes_it_like_themselves: `personality_psychopath_cathryn_needs.png`, `personality_sensitive_kinso_needs.png` (-13); clean freak Mo scrubbed 6 marks in a fit, ticks 1402000-1404290, `p13_cleanfreak_fit.png`.
19. stories_not_a_tax (pass 15, c18c28b): `p15/01_stories_3days.txt`: 180000 ticks unstaged on `graffiti_p12_ash_day18`, 9 messages in 3 days each naming who and why, wall mood per colonist within +6.3 / -10.8; after a death 4 messages in the next day (`p15/04*`, `05*`).
20. mark_ugliness_is_visible (pass 15, re-checked passes 16 and 17): blind judge "Does the worst-made one look worse than a plain row of tally marks? Yes." (`p16/blind_judge_p16.md`, `p17/blind_judge_p17.md`).
21. never_reads_as_dirt (pass 19, 1ab58b79d6): blind judge PASS, `D:\ClaudeWork\rimmandrake\ralph_graffiti\blind_judge_verdict_pass19.md`, on `p19_dirt_left.png`, `p19_dirt_right.png`, `p19_storeroom.png`, `p19_south_wall_east.png`: vanilla filth directly under the marks at 64 ppc; the four weakest candidates each "reads as made by a hand. None reads as a mess."
22. mark_register_is_punk_urban (pass 19, 1ab58b79d6): blind judge PASS, same file: about 40 marks of about 15 kinds across the 7 play-zoom `p19_*` frames, layered like a tagged wall, no modern signage; the nearest thing to clip-art (grey stencil fist, `p19_south_wall_east.png` x~585-635) "ordinary street-art vocabulary. Not a FAIL."

Fix checks seen (they reopen no bar): tribute to someone since dead counts as a memorial; memorials kept across save and reload (`p15/05_brick_day_after.txt`); sensitive temperament x1.5 (`p15/03_ledger_temperament.txt`); a door into a painted wall (`p14_door_into_painted_wall_128.png`); ordered go-over costs the maker their work and no grudge (`p19/01_ordered_goover.txt`: Vex "Karen painted over my work -4", Vex->Karen 67 before and after, "Karen painted over Vex's work, on orders.").

## Caveats, plainly

1. The daylight reshot was not taken. Bars 21 and 22 were judged on night or overcast frames (sleeping colonists, rain, ground mean RGB ~45 against 60-80 earlier). Darkness only makes marks harder to read, so the passes hold a fortiori, but the one shot that would settle it, `p19_dirt_left.png` framing at 64 ppc, game hour ~12, clear, unroofed, does not exist.
2. The owed fix check "confront over painted-out work" is still unseen. Only a spree or an unordered go-over can raise it now; no run produced one.
3. The owner owes one wording line: mark_reads_at_play_zoom says "every mark"; what is proven is "every face-on mark" (side faces are scraps by his choice). Not loop work.
4. Thin bars: fights_have_people_and_reasons and making_a_mark_is_its_own_fun rest on one or few observations each.
5. Everything above was seen on the `graffiti_solo` list, not the owner's full mod list.
