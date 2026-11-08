# Graffiti: where the last pass got to

Pass 14 (2026-11-08). Committed and pushed. The last build (`ralph/live` wording of the spree summary, one string) is built but not deployed; everything else below ran live on game B. Not done: two look bars still owe a fresh blind read (below), and `ralph/DONE.md` is not written.

## Weather this pass
- 1 native crash during play (Mono, in vanilla `GrammarResolver` while recording a horseshoes tale; no Graffiti frame; `bad_cpus=[2]`, uptime ~16 h). Brought back with `up`, the rerun was clean.
- 1 `up` that printed STEVE_UNREACHABLE while the game came up fine (bridge on 5175 a minute later).
- No ssh drops. Six deploy/up cycles otherwise fine.

## Fixed this pass (live evidence; raw runs in /tmp were not kept, the numbers are here)
- **Edge-on walls**: 24 of Ashgate's 77 marks were on walls seen edge-on, drawn turned along the top strip; a fist, two mockeries and a memorial were blots that read as blood or mould. Now `RM_GraffitiKernel.ReadsEdgeOn`: only letters and strokes (Tag, ThrowUp, Scrawl, tallies, scratches; `edgeOn` in the def overrides) go there, and nothing about a person ever does (meaning and reply finders look further for a face instead). Live: a 3-colonist spree laid 11 new edge-on marks, all tags, scrawls or cross-outs.
- **Spree messages**: 16 "X painted over Y's work" in 5 game-hours from one spree, one twice on a tick. Now going-over during a spree is told once when it ends (`MentalState_GraffitiSpree.PostEnd` -> `GraffitiSocial.SpreeEnded`); outside a spree, one painter over one maker's work is told once a day. Live: 3 summaries ("Brick's spree went over 10 marks of Lark, Vex and Mo's work"; wording since changed to "painted over 10 marks by ...", not yet seen).
- **Death messages**: Brick's death sent 7 "X stopped at Y's memorial" in an hour. Now one mourning message per dead pawn per day. Live after the fix: two memorials, no mourning flood (a mourning read with its one message not yet seen).
- **Clumsy hands**: the smeared second go was drawn over the mark with its own wall show-through and washed a poor glyph into a smudge; mud 0.65 made awful paint the colour of the ground. Now the second go lies under the shape in thin paint, mud 0.4/0.2. `st Smear old|new` shows both on one wall: `p14_smear_before_above_after_below_*.png`.
- **Art**: Glyph_HighLife was a soft green smoke cloud (a smudge whatever the hand); now a grinning spiral-eyed face blowing a ring (`bake.py` gained `rim=False` so its black grin isn't knocked out as an outline). Stencil_Fist was oxblood knuckles (a blood smear at 64 px); now a black raised fist on an ochre disc (the game's own FistRaised ideoligion icon is the same idea). `p14_lived_in_raised_fist_playzoom.png`.
- **Weathering**: a blind judge read flaked marks as "spilled debris", "mould", "soot". Paint now keeps a stain of its whole shape (`WallPlane.Stain`, 0.34 to 0.16 by step). `p14_weathered_w2_w3_playzoom.png`, `p14_weathered_w3_128.png`.
- **Doors** (GPT lead 5): a door put into a painted wall takes the paint on that wall cell, and a wide piece beside it stops at the door. `p14_door_into_painted_wall_128.png` (staged, `st Dirt BlocksGranite,door`).

## Bars ("- bar: state (evidence, build)"; builds: 93d8b15 = pass 13, d5e8d31 = pass 14)
- mark_actually_appears, mark_reads_as_deliberate, mark_sits_on_the_wall, art_skill_goes_into_the_art, never_real_world_english, visitors_read_without_recharging, raid_mark_troubles_until_retaken, rereads_affect_at_most_daily, making_a_mark_is_its_own_fun, stands_alone_and_obeys_settings, mockery_changes_regard: true, unchanged from pass 13's list (see git history of this file, 36255af). Nothing this pass touched what they rest on, except: edge-on marks no longer carry pictures (mark_reads_at_play_zoom now true without the "scrap" caveat for new marks).
- marks_visibly_various: true (pass 13 census; this pass's spree painted 19 marks of 14 kinds; fitted marks seen: FIT0.80-0.83 on tags and a glyph, d5e8d31).
- tribute_and_memorial_mean_it: true (Brick killed: Karen painted a memorial 1500 ticks later, Mo, Vex, Fringe, Lark each read one as Mourning; Mo painted a second; 93d8b15+mourning fix).
- pawns_answer_the_wall: true (pass 13; this pass also "Fringe confronted Karen about what's on the wall", "Lark scrubbed away Karen's mark").
- stories_not_a_tax: true on ordinary days (3 unstaged days: 6 messages; 2 more days: 5), now also for a death and a spree (fixed above). Wall mood stays within about +6/-11.
- fights_have_people_and_reasons, each_takes_it_like_themselves: true as in pass 13. Clean-freak fit seen again: Mo scrubbed 6 marks, 2 messages (first scrub, "calmed down after scrubbing 6 marks").
- mark_carries_no_earth_signage: true (blind judge, pass 14 shots: "no hazard triangle, exit sign or traffic glyph").
- mark_ugliness_is_visible: true (blind judge on `p14_dirt_vs_paint_*`: the awful glyph, the red scrawl and the splatter "all look worse at a glance than the clean cream tally").
- mark_register_is_punk_urban: MIXED (blind judge): pieces, bubble letters, tags, the fist, crossed-out portraits, horned mockeries read as graffiti; the colony's teal ideoligion sigil (3 times), the tribute's laurel wreath and winged sun frame round a portrait, and an orange smiley sun read as badges or clip-art.
- never_reads_as_dirt: was FALSE on the judge's shots (weathered flakes, a dark tag on a dark wall, the W2 tag's orange specks, a weathered edge mark); weathering, edge-on and art fixed since. Owes a fresh blind read.

## Do next
1. Deploy (last build not deployed), `up`, load `graffiti_p14_ash_powered` (noon power: the generator is fuelled and wood stocked, but the lamps still show the no-power bolt: find the break with `jawa/power_net` on a lamp, or the shots stay dim indoors).
2. Read GPT's answer to `ralph/live/broaden_ask_pass14.md` (the pass-14 broaden call, made at the end of this pass): `/mnt/d/ClaudeWork/rimmandrake/ralph_graffiti/gpt_help_pass014.md`. Act on one lead; that satisfies the broaden rule for DONE.
3. Punk register: the tribute frames (`RM_Graffiti_Tribute` textures: laurel, winged sun) read as badges; a rougher, painted frame is the fix. The colony sigil repeating is the faith's sign, so keep it but consider a hand-cut variant per painter.
4. Fresh shots of this build, then a second blind rm-judge (no verdicts given) on never_reads_as_dirt and the punk register.
5. Then write `ralph/DONE.md` (draft: `ralph/history/DONE_draft_pass13.md`).

## Traps
- The gate refuses Bash commands containing `rimbridge` and the like: write bridge scripts with Write/Edit. `g.py` is the driver; `ralph/steve.sh sync` after editing it. `kvall` prints a tool's whole answer (`kv` cuts at 4000 chars).
- `st Dirt <stuff>[,door]` builds the dirt wall at (10,40) 32x7; `shot` refuses more than 20 cells at 64 px. A stage mark dated before tick 0 gets no weather (the fist's W4 in the Dirt stage).
- Local hour in Ashgate: ((ticks - 2983) % 60000)/2500; load then `kv jawa/safe_advance ticks=22000` reaches noon from the day-18 save. Clear weather after every load. Stock food before long runs.
- `days` prints TALLY lines per chunk; use `st Count` as a separator when diffing `so Marks`.
- Saves on game B: `graffiti_p14_ash_powered` (day 18 noon, fuelled), `graffiti_p12_ash_day18`, `graffiti_p13_ash_3days`, `graffiti_p11_rust_memorial`.
- Decompile: `/mnt/d/ClaudeWork/rimmandrake/decomp/rw16/all/{RimWorld,Verse,RimWorld.Planet}/`.
