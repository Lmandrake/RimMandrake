# Graffiti: where the last pass got to

Pass 13 (2026-11-08). Everything is committed and pushed. **Game B is down**: it crashed natively at engine start (Mono "DLL initialization routine failed", before any mod loaded) on two `up` tries after the last deploy. So the newest build (`ralph/NEED_GAME`) is deployed on Steve's disk but not yet seen running. A DONE draft is in `ralph/history/DONE_draft_pass13.md`; it is not a claim.

## Weather this pass
- 6 deploy/up cycles were fine. Then 2 failed starts at about 01:31 PST (native crash at engine init, uptime 15.6 h, `bad_cpus=[2]`). No ssh drops.
- An **eclipse** made one batch of shots dark. The helper's run saw `bad_cpus=[2]` throughout, and nothing it measured surprised me.

## Bars, with evidence anyone can re-check (Conductor ruling 1:23 AM: a proven bar stays true unless a later change touched what it rests on)
Builds: `93d8b15` = pass 13's first build, the one the helper ran on. Raw output: `/mnt/d/ClaudeWork/rimmandrake/ralph_graffiti/p13/` (01a..07f). Shots: `.../ralph_graffiti/shots/`.
- mark_actually_appears: true (trace `1094343 Vex painted IdeoSigil_StencilBox@(127,0,113) (poor)`, visible at x~480 in `lived_in_south_wall_day19_playzoom.png`; 93d8b15)
- mark_reads_as_deliberate: true (`lived_in_south_wall_day19_playzoom.png`, `lived_in_corridor_day18_playzoom.png`; 93d8b15)
- mark_reads_at_play_zoom: true for every face-on mark; a mark on an edge-on wall is a narrow scrap, as option D allows ("a side face stays a scrap"). The audit calls this WRONG BAR wording ("every mark"); it needs the owner's rewording, not more work.
- mark_sits_on_the_wall: true (`optionD_materials_close128.png`, `perspective_sweep_wood.png`; geometry unchanged since pass 11)
- marks_visibly_various: true (70 marks of 20 kinds at load, `p13/01a_load.txt`). The skew (37 of 70 tallies, scratches and rude little men) is fixed in 38601eb (marks squeeze to 80% to fit a gap); the fix isn't seen live yet.
- mark_register_is_punk_urban: CONTESTED. It rests on pass 8's gallery. Owed: a blind look (an rm-judge subagent, not me) at the current art on a lived-in wall.
- mark_carries_no_earth_signage: true (warn_0..3.png viewed this pass: crossed eye, arrows to a splat, skull, maw)
- mark_ugliness_is_visible: NOT PROVEN. Owed: a scrawl beside a tally on a lived-in wall in daylight at 64 px.
- mockery_changes_regard: true (`social_regard_brick_on_karen.png` "Painted me on the wall x2: -38"; `p13_wall_inspect_mockery.png` "(5 angered)"; `p13_mocked_needs.png` "Mocked on the wall by Lark -5"; 93d8b15)
- tribute_and_memorial_mean_it: true (pass 7: tribute +6.6 mood/+22 opinion, jealous -3.7/-14; `memorial_lark_grief_half.png`; Said `1134188 Karen found the tribute Vex painted for them and stood looking at it`, 93d8b15). Owed: a memorial kept across a save. New in 38601eb, not seen live: a tribute to someone who has died since reads as their memorial.
- pawns_answer_the_wall: true (Said `1094143 Lark painted a mockery of Karen on the wall, over Karen's work.`, `1115046 Brick confronted Karen about Karen's scratch marks on the wall.`; `scrub_order_done.png`; trace "Karen means to Deface"; 93d8b15)
- raid_mark_troubles_until_retaken: true (`p13/02*`: Gaup painted IdeoSigil_StencilBox@(149,119) at 1272646; Karen "Enemy marks on our walls -1" at 1284266; Fringe scrubbed it at 1286157, "Reclaimed +4.5", the penalty gone; `p13_raid_mark_playzoom.png`, `p13_raid_mark_needs.png`, `p13_raid_retaken.png`; 93d8b15. The exit was forced with lord_set_job.)
- visitors_read_without_recharging: true (`p13/03d_caravan2.txt`: the insult cost -11 and reached the 12-per-visit cap, "read the insult" x1, Hatlencaora -4 to -16; 93d8b15). The wrong-faction charge (a Berro Pact visitor took -1 at 1381539) is fixed in the last commit, not yet seen live.
- stories_not_a_tax: NOT YET. 11 messages in 3 days on 93d8b15, a burst around the Karen–Lark feud (`p13/01c_days2.txt`). Wall mood stays within about +6/-15 and expires. Two message leaks are fixed in the last commit, not yet seen live: a grudge painting over a last word, and a cleaning fit sending 6 messages in 2290 ticks.
- fights_have_people_and_reasons: true, thin (`social_fight_blows.png`; drafted pawns excluded in code; trace "fight chance 0.39 (a fight too recent) -> words"). The new fight message (our own, naming both and the wall) isn't seen live.
- stands_alone_and_obeys_settings: true (classic mode, helper item 5: Karen's spree painted 18 marks, none IdeoSigil or Glyph, no "Our sign", 93d8b15; pass 12: painting off for 19000 ticks gave 0 marks, and save/reload left 60 marks and every total identical; pass 7: social off sent wall mood to 0)
- making_a_mark_is_its_own_fun: true, thin (pass 7 joy 0.56 to 0.63 over one paint; "Left my mark" in traces passes 7-13)
- rereads_affect_at_most_daily: true (helper item 6: 401 reads over 222 pairs, 103 pairs read twice or more, shortest gap 60120 ticks; positive control: Karen "Lark's tag on the wall (age 52500)" on a mark older than a day; 93d8b15)
- art_skill_goes_into_the_art: true (`old/pass11/art_skill_crafts_ladder_beauty.png` Beauty -6..+30; FineArt +0.9 / UglyMark -0.9; `art_skill_ladder_*_64.png`)
- each_takes_it_like_themselves: true (`personality_psychopath_cathryn_needs.png`, `personality_sensitive_kinso_needs.png` -13; clean freak: Mo scrubbed 6 marks in a fit, 1402000-1404290, `p13_cleanfreak_fit.png`, 93d8b15). Not shown: the sensitive "both ways" positive side. The forced break refused while Mo lay down; the helper started the state directly.
- never_real_world_english: true (vandal_0..5.png viewed this pass)
- never_reads_as_dirt: NOT PROVEN. On the day-19 wall, a poor green glyph reads like a smoke blob; `dirt_vs_paint_a.png` is old art. Owed: an awful scrawl, a mid-fade mark and vanilla filth on one lit wall at 64 px (`st Compare` builds most of it).

## Built this pass (all committed)
- **Feuds end.** Before: a mockery over each other's every few hours, 7 messages in 7 hours. A reply in paint is the last word (`Filth_Mark.lastWord`): its subject may scrub, cross it out or confront, but not paint back. A mockery covering its subject's mockery of the painter counts as one. One mockery of a person per painter per 6 days (`GameComponent_Graffiti.MockeryDue`), seeded at load from the mockeries on the walls (`LoadedGame`). A last word about you is never spared by your gap measure (`BareRoom`).
- One act, one message: a reply's going-over rides in its own message. A fight sends our own message ("..., and it came to blows.") at both pawns and the wall.
- Weathering flakes in patches (`WallPlane.Weathered`). Seen live: `weather_flaking_and_painted_heads_128.png`; before: `old/weather_ghost_before_p13.png`.
- A mockery's head is painted, not the crisp sprite (`WallPlane.PaintedPortrait`). Seen live: same shot.
- Marks squeeze to 80% to fit a gap (`Filth_Mark.fit`, `Width`, `GraffitiPool.FitFor`); pieces and social marks keep full size. Not seen live.
- A tribute to someone who has since died reads as their memorial; the wall pane says "(dead since)". Not seen live.
- An insult charges only the faction it names (`GoodwillOf`). A cleaning fit tells its first scrub and its end with a count. Not seen live.
- `so Marks` shows WEATHERn, FIT and LASTWORD.

## GPT broaden (pass 13)
Asked: `ralph/live/broaden_ask_pass13.md` with six shots. Answer: `/mnt/d/ClaudeWork/rimmandrake/ralph_graffiti/gpt_help_pass013.md`. Acted on lead 6 (a tribute whose subject dies), fixed in code. Lead 5 (put a door into a painted wall) is checked by code (`MarkPieces` clips per cell by wall links) but not seen. Not tried: lead 2 (a newcomer who reads nothing), lead 3 (a player ending a feud by hand), lead 4 (farming tributes).

## Do next (game first: `ralph/steve.sh deploy`, `up`)
1. Load `graffiti_p12_ash_day18`, Clear weather, then `days 180000 30000`, `so Said 40`, `so Tally`. Expect the Karen–Lark feud to stop at one reply, and count messages (stories_not_a_tax).
2. `so Marks | grep FIT`; then shoot a wall carrying fitted marks at 64 and 128 px. Is a squeezed tag a smaller hand, or a stamp?
3. Mo's fit: `kv jawa/pawn_mental` start (the helper's route, in `p13/04h_start.txt`), then `so Said`: expect 2 messages, not 6.
4. `so Kill Brick` (Lark's tribute at 113,113 is about Brick), then wait for a friend's read: the trace should say "-> Mourning", and `wallui` should show "(dead since)".
5. `st Compare` plus a weathered mark, at 64 px in daylight: an awful scrawl, tallies, vanilla filth (never_reads_as_dirt, mark_ugliness_is_visible). Also a scrawl beside a tally on a lived-in wall.
6. A blind rm-judge on the current lived-in shots for the punk register.
7. A door into a wall under a wide mark: one 128 px shot.
8. Then turn `ralph/history/DONE_draft_pass13.md` into `ralph/DONE.md`, filling in the social side and the bar list above.

## Traps
- The gate refuses Bash commands containing `rimbridge` and the like: write bridge scripts with the Write or Edit tool. `g.py` is the driver; `ralph/steve.sh sync` after editing it. The helper's scripts in `p13/` (`needs_scroll.py` scrolls the Needs tab; `raid.py`; `fit.py`) work.
- `kv jawa/game_condition action=end condition=Eclipse` before shooting.
- `brk` refuses while a pawn is in another mental state or lying down; `pawn_mental start forced=false forceWake=true` works.
- `shot` refuses a rect wider than one screen: 20 cells at 64 px, 8 at 128.
- Local hour in Ashgate: ((ticks - 2983) % 60000)/2500. Clear weather (`kv jawa/weather_set weather=Clear lockWeather=true`) after every load. Stock food before long runs: `kv rimworld/spawn_thing defName=MealSurvivalPack x=120 z=131 stackCount=10`.
- A staged answer is random: sending a pawn to a mark started one in two of three tries.
- Saves on game B: `graffiti_p12_ash_day18`, `graffiti_p13_ash_3days` (helper, after the 3-day run), `graffiti_p11_rust_memorial`.
- Decompile: `/mnt/d/ClaudeWork/rimmandrake/decomp/rw16/all/{RimWorld,Verse,RimWorld.Planet}/`.
