# Graffiti: the ratchet (Conductor, 2026-11-08 ~02:00 AM PST)

Follows the audit (`/mnt/d/ClaudeWork/rimmandrake/conductor/apparatus_audit_graffiti_2026-11-08.md`) and the Conductor ruling 1:23 AM (OWNER_NOTE.delivered), which PROGRESS pass 13 already applied. 22 bars (20 must-show + 2 cannot-show): 18 proven, 4 remaining, plus owed fix checks that do not reopen a bar. Raw output `D:\ClaudeWork\rimmandrake\ralph_graffiti\p13\`, shots `...\shots\`. Build `93d8b15` = pass 13's first build (the later commits 38601eb797 and 9ab5c54cf7 are built, not yet seen live).

## Remaining (work only on these, in this order) — updated pass 16, 2026-11-08 ~04:45 PST
Build now: `f9a7afbb88` (pass 16 commits b723a6aaf1..f9a7afbb88), deployed and seen live on game B. Save `graffiti_p16_ash_lit` (game B Saves). Raw output `D:\ClaudeWork\rimmandrake\ralph_graffiti\p16\`, shots `shots\p16_*` (pass 15's in `shots\old\pass15\`).
1. never_reads_as_dirt: still FALSE on this build (blind judge pass 16, `p16/blind_judge_p16.md`). Gone from the list since pass 15: rock chunks, UI portraits, the olive Vandal, the invisible soot tally, the scorched-hole memorial. Still dirt: the awful HighLife glyph (olive and soot: "mould"), the poor wolf glyph (black with an ochre eye: "scorch"), a W3 magenta throw-up ("old grimy stain"), a poor pink-teal Vandal in the dim storeroom ("mouldy smear"), dark overspray and black blots in the warning glyph and the mockery's pointing hands ("soot or ash"), a pale weathered gear ("plaster patch"), a pale weathered scribble ("dead weed"), a faint W-smudge ("rust"), red and green TAGS drawn sideways on edge-on walls ("rust or blood runs", "moss"). The pattern: anything faint, thin, dark-edged or sideways reads as a stain. GPT `stuck` call made pass 16 (ask `ralph/live/stuck_ask_pass16.md`; answer path in PROGRESS).
2. mark_register_is_punk_urban: still MIXED (same judge). Badges now: every raised fist ("clean emoji-style fist icon", and five of them: repeats look stamped), the ideo icon in its sprayed halo ("emblem"; twice on one wall), the StencilBox sigil ("sticker decal"), the horns and the gallows mockeries ("skull-and-crossbones emblem"), the cog and hammer ("gear logo"), the crown tribute's ring and sparkles ("clip-art"), the warning glyph's arrows ("compass icon"), the wings memorial ("halo icon"). Street: throw-ups, wildstyle, tags, tallies, slashes, stick-figure doodles.
Owed fix checks (bar stays Proven; one line each): confront over painted-out work (built pass 15, deployed pass 16, still unseen in play); fitted marks at 80% (no FIT mark seen); wrong-faction visitor charge (`GoodwillOf`) not yet run.
Then: DONE.md (draft `ralph/history/DONE_draft_pass13.md`; broaden pass 14 acted on pass 15; stuck call pass 16).
Owner owes one line: reword mark_reads_at_play_zoom "every mark" -> "every face-on mark". Not loop work.

## Proven (locked), 20 (build 93d8b15 unless noted)
- mark_actually_appears: trace `1094343 Vex painted IdeoSigil_StencilBox@(127,0,113) (poor)`, visible in `lived_in_south_wall_day19_playzoom.png`.
- mark_reads_as_deliberate: `lived_in_south_wall_day19_playzoom.png`, `lived_in_corridor_day18_playzoom.png`.
- mark_reads_at_play_zoom: true for every face-on mark (option D, side faces are scraps by his choice). Wording owed to him (above).
- mark_sits_on_the_wall: `optionD_materials_close128.png`, `perspective_sweep_wood.png` (geometry unchanged since pass 11).
- marks_visibly_various: 70 marks of 20 kinds at load (`p13/01a_load.txt`); 34 of 12 kinds in `p13/04a_brk.txt`. Skew fixed by 38601eb797 (fix check above).
- mark_carries_no_earth_signage: `warn_0..3.png` (crossed eye, arrows to a splat, skull, maw); no hazard triangle.
- never_real_world_english: `vandal_0..5.png` illegible scrawl, no "TARTE".
- mockery_changes_regard: `social_regard_brick_on_karen.png` ("Painted me on the wall x2: -38"), `p13_wall_inspect_mockery.png` ("(5 angered)"), `p13_mocked_needs.png` ("Mocked on the wall by Lark -5").
- tribute_and_memorial_mean_it: pass 7 tribute +6.6 mood/+22 opinion, jealous -3.7/-14; `memorial_lark_grief_half.png`; Said `1134188 Karen found the tribute Vex painted for them and stood looking at it`.
- pawns_answer_the_wall: Said `1094143 Lark painted a mockery of Karen...`, `1115046 Brick confronted Karen...`; `scrub_order_done.png`.
- raid_mark_troubles_until_retaken: `p13/02*`: Gaup painted IdeoSigil_StencilBox@(149,119) at 1272646; Karen "Enemy marks on our walls -1" at 1284266; Fringe scrubbed it at 1286157, "Reclaimed +4.5", penalty gone; `p13_raid_mark_playzoom.png`, `p13_raid_mark_needs.png`, `p13_raid_retaken.png`. Exit forced with lord_set_job (sequence proved; natural tagging on exit not).
- visitors_read_without_recharging: `p13/03d_caravan2.txt`: insult cost -11, reached the 12-per-visit cap, "read the insult" x1, Hatlencaora -4 to -16.
- fights_have_people_and_reasons: `social_fight_blows.png`; drafted pawns excluded in code; trace "fight chance 0.39 (a fight too recent) -> words". Thin.
- stands_alone_and_obeys_settings: classic mode: Karen's spree painted 18 marks, none IdeoSigil/Glyph, no "Our sign" (helper item 5); painting off 19,000 ticks gave 0 marks and save/reload left 60 marks and every total identical (pass 12); social off sent wall mood to 0 (pass 7).
- making_a_mark_is_its_own_fun: pass 7 joy 0.56 to 0.63 over one paint; "Left my mark" in traces passes 7-13. Thin.
- rereads_affect_at_most_daily: helper item 6: 401 reads over 222 pairs, 103 pairs read twice or more, shortest gap 60120 ticks; positive control Karen "Lark's tag on the wall (age 52500)".
- art_skill_goes_into_the_art: `old/pass11/art_skill_crafts_ladder_beauty.png` Beauty -6..+30; FineArt +0.9 / UglyMark -0.9.
- each_takes_it_like_themselves: `personality_psychopath_cathryn_needs.png`, `personality_sensitive_kinso_needs.png` (-13); clean freak: Mo scrubbed 6 marks in a fit, ticks 1402000-1404290, `p13_cleanfreak_fit.png`.

- stories_not_a_tax (pass 15, c18c28b): `p15/01_stories_3days.txt`: the feud save `graffiti_p12_ash_day18`, 180000 ticks unstaged, Clear weather: 9 messages in 3 days (7 in the first 1.5 days, none on day 3), each naming who and why; Karen's mockery of Lark answered once by Lark's reply (LASTWORD), Karen answered with words, no paint-back or deface of Lark. Wall mood per colonist within +6.3/-10.8. After a death (`p15/04*`, `05*`): 4 messages in the next day, one mourning message (Karen at Mo's memorial for Brick). Clean-freak fit: 2 messages (pass 14).
- mark_ugliness_is_visible (pass 15, c18c28b): blind judge on `p15_dirt_vs_paint_left.png` / `_awful_tally_128.png`: "Does the worst-made one look worse than a plain row of tally marks? Yes." Caveat that ties it to item 1: it looked worse partly by reading as mould. Re-check if the awful hand's colour changes. Re-checked pass 16 after the colour change (no mud, new Vandals): "Yes. The tallies are crisp and clearly deliberate. The worst marks are smudges you can't read" (`p16/blind_judge_p16.md`, shots in `shots/p16_dirt_vs_paint_*`; pass 15's moved to `shots/old/pass15/`). Same caveat: the weak ones read as stains, not as clumsy paint.

- Fix checks confirmed pass 15 (bars unchanged): tribute to someone since dead shows "about Brick (dead since)" and counts as a memorial; memorials kept with their subject across save and reload (`p15/05_brick_day_after.txt`); sensitive Fringe (good x1.5) "Fine work on the wall +1.4" beside Karen's +0.9 (`p15/03_ledger_temperament.txt`; not the same mark, and the ambient budget clips); a door into a painted wall (`p14_door_into_painted_wall_128.png`); a mourning message with a reader seen once per death per day.

## Rules
1. A proven bar stays proven across rebuilds and is not re-tested unless a change touched the code or art it depends on; a pass does not re-prove Proven bars.
2. A bar moves back to Remaining only on a shown regression, with the evidence written beside it.
3. When a Remaining bar is proven, move it to Proven with its evidence and build in the same commit. When Remaining is empty, write DONE.md citing Proven ("I don't need the Judge to say it's ok. I just need it to be provably OK").
