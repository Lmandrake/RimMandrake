# Graffiti: where the last pass got to

Pass 9 was all offline: GSS held game B for the whole pass (ralph/b_held.py). Nothing below has run in the game yet. Steve's status at 19:42 PST read `bad_cpus=[0]` with GSS's game up, so restart B (down, up) once before trusting any surprising result. Weather this pass: no dead game, no dropped ssh (never drove it).

## Done this pass (offline, committed, built: 6b1e88936f)
- **Wall-art mood trimmed (owner card 7:27 PM: "about +2 to +3 total and cap it").** New `RM_GraffitiKernel.AmbientMoodBudget = 3` (times the pawn's good, so a sensitive pawn up to 4.5) inside the good budget, now 6 (was 8). Ambient = funny doodle, good/fine work, our sign, a friend's tag, a friend's piece, a tribute to someone else, insult enjoyed, defiant, left my mark (`GraffitiTemperament.IsAmbient`). Values cut: doodle 2→1 (stack 1), fine art 1/2/3/4 → 1/1.5/2/3, piece 3→2, our sign 2→1, left my mark 2→1, tribute to me 6→4 (3 days), stuck it to them 4→3, enjoyed it 3→2, answered 3→2, wiped it away 3→2.
- **Situational positives deleted**: `RM_Graffiti_NearOwnSign` and `RM_Graffiti_NearOurPiece` (+1 each, outside every cap) doubled the read memories. Their slots are gone from 31 mark defs. The uneasy ones (hostile mark, foreign creed, enemy claim) stay.
- **Memorial never a gain (Conductor 5:05, owner 7:27).** `Thought_GriefEase` (thoughtClass of `RM_Graffiti_GriefEased` and `RM_Graffiti_Mourning`): all comfort about one dead pawn adds up to at most half the grief still felt for them (`RM_GraffitiKernel.EaseShare`, `GriefEaseShare = 0.5`), read live, and the thought goes when the grief does. No grief, no memorial mood at all. Mourning 3→2. Fuzz checks it.
- **"Tribute from Lark +4"** is ours: `RM_Graffiti_Honored`, label "tribute from {0}" (lower case, so a search for "Tribute from" misses it), given when a pawn reads a tribute painted to them. Now base +4.
- **Vandal scrawl uglier, in stat and picture.** Six new sprites (sickly bile green, liver purple, dirty salmon, grimy olive; blotched, smeared, a handprint, overspray fog), prompts in `art_source/manifest.py`, the old set in `gen3/old_vandal_pass7/`. `CraftCeiling(Scrawl) = Poor`: a scrawl always draws with the poor mud and smear and counts -2.5 or -6, below any tally by the same hand (a steady hand's scrawl had been worth 0, the same as a tally). Makerless scrawls draw poor too, and saved marks clamp on load. Offline at 64 ppc (`gallery_sim.py`) they read as grubby clashing smears beside neat tallies. Unseen in the game with the mud tint, which could push them toward dirt: check `never_reads_as_dirt`.
- **Shot tools**: `st Name Faction/Settlement` names the colony (the naming dialog pops every 1000 ticks after day 4.3 until it is named) and closes the dialog. `st Beauty on|off` is the game's Beauty overlay (numbers around the hovered cell: hover with `rimworld/set_hover_target`; unproven that the virtual hover moves `UI.MouseCell`). `so Tally` now prints `name:+up/-down/|opinion|`.
- **Telemetry, game B, pass 8's sessions** (fetched `JawaBench/tps`): 10-mod Graffiti runs, 1.6M ticks in total, 0.46 to 0.90 ms per tick, map components 0.002 to 0.005 ms per tick (0.4 to 0.6%). The worst ticks (85 to 178 ms) are pawn ticks, world or "tickOther", never ours. MEASURED, pass 8 build.
- **GPT broaden (pass 9)**: asked the three LOOK_CURATED questions with the six shots, and which lines no shot proves. Answer: `/mnt/d/ClaudeWork/rimmandrake/ralph_graffiti/gpt_help_pass009.md`. In short: the mockery is noticeable but its meaning isn't readable without clicking (the owner already said it reads: keep). +3 is "reasonable to try, maybe still free mood". The scrawl is "louder, not uglier" (acted on, above). It names as unproven by any shot: making_a_mark_is_its_own_fun, rereads, raid retake, visitors, settings and save, stories over days, and art skill with Beauty numbers. Leads worth playing: (2) leave an ordinary colony alone for days and read the needs and the message log; (5) a messy, lived-in room comparing a poor and a skilled painter's work.

## Do next, in the game (first: `ralph/steve.sh tier`, `ralph/steve.sh deploy`, `ralph/steve.sh up`)
Load `graffiti_p8_busy3` (first colony) and `graffiti_p8_fresh2` (fresh colony); check they are still in game B's Saves (GSS shared it). Name them at once: `st Name Rustwall/Rustwall` (busy3) and `st Name Ashgate/Ashgate` (fresh2), and use those names in every caption.
1. **Retakes the Conductor asked for** (new LOOK page; leave LOOK_CURATED.md alone): Volatile Kinso with "Mocked on the wall by Brandt" visible and his trait shown (Character tab shot plus Needs shot, always pass a cell to `ui` so the virtual hover parks off the tabs); psychopath Cathryn the same way; the mockery wall pane with no naming dialog; the memorial mourner (caption only what is on screen, and the new cap should show the memorial at most half the grief); one Crafts row with all 7 in one frame and Beauty numbers on screen (`st Beauty on`, hover over the row).
2. **Vandal beside tallies on a lived-in colony wall**, play zoom, daylight (the owner wants to be asked again). Check it doesn't read as dirt.
3. **Mood after the trim**: `so Tally` across 2 to 3 unstaged days in Ashgate; the ambient plus should sit at about +3 or below for most pawns. Shot of one pawn's needs.
4. Shots for lines no shot proves yet: the maker's own "left my mark" and Recreation after a paint job; a reread a day later; a raid mark and its retake (recipe under Traps); `so Set paintingEnabled=False` then a day with no new marks; a save and reload.
5. Watch whether ugly own-faction marks pile up: they are protected from auto-clean by the owner's 2026-10-09 ruling (F7), so an untrained painter's poor scrawls stay until the player force-cleans each. If rooms go ugly over days, ask the owner (QUESTIONS.md) whether ugly own marks should lose the protection.
6. Then `DONE.md` (the broaden call is made: this pass).

## bars (north star, all 22; "unseen" = no shot on the current build)
- mark_actually_appears: true (lived_in_colony_bedrooms.png, unstaged)
- mark_reads_as_deliberate: true (lived_in_colony_bedrooms.png)
- mark_reads_at_play_zoom: true (variety_gallery_a..d.png)
- mark_sits_on_the_wall: true (perspective_sweep_*.png, optionD_close_granite_north.png)
- marks_visibly_various: true (variety_gallery_a..d.png)
- mark_register_is_punk_urban: true (variety_gallery_a..d.png)
- mark_carries_no_earth_signage: true (variety_gallery_a..d.png)
- mark_ugliness_is_visible: unseen (new vandal art and poor look not yet in the game; dirt_vs_paint_a/b.png show the old art, judged louder rather than uglier)
- mockery_changes_regard: true (social_mockery_victim_needs.png, social_mockery_victim_social.png)
- tribute_and_memorial_mean_it: unseen (memorial cap changed; jealousy never shot)
- pawns_answer_the_wall: true (social_fight_blows.png, personality_cleanfreak_scrubbing.png); a finished scrub or cross-out not in a shot
- raid_mark_troubles_until_retaken: unseen on this build
- visitors_read_without_recharging: unseen in a shot (trace in pass 8: goodwill -1 once, capped)
- stories_not_a_tax: unseen (mood trimmed this pass; measure in play)
- fights_have_people_and_reasons: true (social_fight_blows.png)
- stands_alone_and_obeys_settings: unseen on this build
- making_a_mark_is_its_own_fun: unseen
- rereads_affect_at_most_daily: unseen in a shot
- art_skill_goes_into_the_art: unseen (crafts shots lack Beauty numbers)
- each_takes_it_like_themselves: unseen (volatile and psychopath shots to retake; clean freak shot is good)
- never_real_world_english: true (variety_gallery_a..d.png)
- never_reads_as_dirt: unseen for the new vandal art (true for the rest: dirt_vs_paint_a/b.png)

## Traps
- The gate refuses Bash commands containing `rimbridge` and the like, even in heredocs: write bridge scripts with the Write tool. While GSS holds B it also refuses steve.sh up/down/deploy/tier/run; `status`, `sync` and `fetch` still work.
- `prove_quicktest_world.py` refuses to leave a colony past tick 120000: stage art (`st Sweep/Ladder/Compare/Gallery/Crafts`) in the corners of the colony map instead.
- `ralph/steve.sh run '...'`: the driver chains with ` @ `. Pass a value with `;` in single quotes inside double quotes. After editing `ralph/live/g.py`, run `ralph/steve.sh sync`.
- Joy pacing is real: a pawn with full joy, or one bored of painting, doesn't paint for days. `until` with a 100k+ budget, or wait.
- Raid: `kv jawa/lord_pawn_move action=list`, then `kv jawa/lord_set_job lordIndex=N lordJob=LordJob_AssaultColony args=...`, step 600 at a time, then `LordJob_ExitMapBest args=locomotion=Jog;canDig=false;canDefendSelf=true` at a wall.
- Art: `art_source/manifest.py gen` generates whatever is missing from `gen3`; `bake.py --only a,b` writes Textures (`--dry dir` to look first); `gallery_sim.py <dir> <prefix>` puts baked marks on walls at 64 ppc offline.
- Decompile: `/mnt/d/ClaudeWork/rimmandrake/decomp/rw16/all/{RimWorld,Verse}/`.
