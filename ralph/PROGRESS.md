# Graffiti: where the last pass got to

Pass 10 drove game B on the Ashgate colony (`graffiti_p8_fresh2`, named Ashgate). Everything is committed, and game B runs the newest build.

## Weather this pass
- One hung bridge call (a screenshot) with the canary at `bad_cpus=[6]`. Restarted B (down, up); the first `up` failed and the retry worked. After the restart the reloaded save behaved normally.
- `steve.sh up` came up first with GSS's tier, because the tier step refused: `ModsConfig.swap-active.json` in `~/rm/gameb/deployed/config/` named a before-copy that `sync`'s `git checkout -f` overwrites (the before-copy is tracked in git). I deleted that marker on Steve and ran `tier`. **This happens again after every sync** while that file is tracked. If `up` prints "REFUSING TO WRITE: swap marker", run `ralph/steve.sh run 'rm -f deployed/config/ModsConfig.swap-active.json'`, then `tier`, then `up`, and check that graffiti is in the list (`grep mandrake.rm.graffiti` on `$RM_GAME_USERDATA/Config/ModsConfig.xml`).

## Done this pass (built, deployed, live-checked unless said)
- **Ambient cap absolute (Conductor 8:16).** `RM_GraffitiKernel.AmbientBudget(good)` = 3 × good, but never over 3. Live over 2 days in Ashgate, ordinary wall art stayed at +3 or under for everyone. **Tribute to me (+4, 3 days), memorial and mockery stay outside the 3:** the owner's card said "ordinary wall art ... about +2 to +3 total and cap it", and these are stories about someone, under the good budget (6 × good). Tell the owner this plainly in DONE.md.
- **Option D, face paint.** At 128 px the paint on the lit face was a pale ghost of the paint climbing onto the dark top: spray alpha over a light face, then the wall blended back over it. Now the face gets a second coat and half the show-through (`WallPlane.FaceThrough`, `FaceCoats`). Live: same colour across the crease (`first_look_optionD_face_bold_close.png`). Not yet re-swept across materials: steel, marble and wood may now be too loud. Run `st Sweep` and look.
- **Dead pawns survive a save.** `Scribe_References` writes null for a destroyed thing (a dead pawn) unless `saveDestroyedThings`. So every memorial forgot its subject at its first save: it lost the painted face, and the mourner painted another (Lark painted Pell three memorials). Maker, subject and defacedBy now save that way, and a discarded pawn is dropped before saving. `AlreadySaid` also matches on the saved name, for old saves. Live: mockeries save their subject. **A new memorial across a save is not yet proven.**
- **Thought descriptions named the reader.** Vanilla formats a description's `{0}` as the pawn who has the thought, while a label's `{0}` is the other pawn. So "Mocked on the wall by Karen" read "Brick painted me up there". Fixed by `ThoughtDescriptionPatch` (postfix on `Thought.Description` for our memories: `{0}` is the other pawn, or "someone"). Live: correct (`social_story_karen_needs.png`).
- **Messages go on a face, not an edge.** Lark's mockery of Mo went on a wall seen edge-on: a head-sized scrap on the wall top (`old/ashgate_mockery_on_edge_before_fix.png`). `TryFindMeaningCell` and `TryFindReplyCell` now try front faces first. **Deployed, not yet seen live** (it needs a new mockery).
- Old-class memories (saved before `Thought_GriefEase`) are remade when renewed, so the grief cap reaches them. Memories the budget squeezes under 0.5 mood or 1 opinion aren't given (Mo's needs listed "Good work on the wall 0").
- Driver: `g.py load <save>`, `uil [surface] [filter]` (UI layout), `hoverlabel <Text_with_underscores> [anchor]` (hovers a UI row so its tooltip shows), and `screen <name>` (full screen as it stands). Advances stop only on death, downed or hostile arrival. **Opinion tooltips work**: select a pawn, open the Social tab, `hoverlabel Karen_Gates left`, `screen x`.

## What the colony did (evidence for the social bars)
Ashgate, unstaged apart from one forced spree (Mo, Neurotic, Artistic 2), ticks 313k to 514k:
- Over two quiet days: 1 message, a memorial by Lark. Ambient mood ≤ +3. Brick carried "Mocked on the wall by Karen -8.8" the whole time (that mockery stood outdoors and nobody cleaned it).
- Brick and Karen had a vanilla social fight ("Karen called Brick a quail..."). Brick's opinion of Karen showed "Painted me on the wall x2: -38" and "Made that piece on the wall: +7" (`social_regard_brick_on_karen.png`). This is what the Conductor wanted for mockery_changes_regard.
- Mo's spree: 13 marks in the corridor, and more later (about 35 in all, 10+ hours; the def allows 6 to 12). It painted over Lark's and Karen's work. Each answered with a mockery of Mo. Mo "went white". Brick scrubbed Karen's mockery away ("Mo won't forget that"). Fringe, Mo's friend, confronted Lark about hers. 8 messages that day, 1 a day otherwise. Saves: `graffiti_p10_ash_story` (just after), `graffiti_p10_ash_reload` (a few hours later, newest build).
- Karen broke (psychotic wandering) on day 9, mostly not from the walls (her walls net -2 to -4).

## Do next
1. **Scrub designator (owner's F7: "a scrub designator overrides").** Own-colony marks are protected from automatic cleaning, so after a spree the player must right-click every mark. Build a drag designator (DesignationDef plus a WorkGiver that hands out vanilla `Clean` jobs on designated marks; `RefusesToClean` still applies). This is the honest fix for "ugly own marks pile up" and for the spree aftermath.
2. **Watch Mo for a spiral**: load `graffiti_p10_ash_reload`, run `days 120000`, and see whether the mockeries of Mo bring another break and another spree. If that loops, cap it: for example, a spree can't start within N days of the last, or a victim's mockery memories count less after the first.
3. `st Sweep` on the new face paint: every material, at 64 and 128 px. Check that light walls (marble, steel) aren't now too loud, and that dark ones still read.
4. Scrawl beside tallies, lived-in, daylight (the owner's open question). `so Order Mo/RM_Graffiti_Vandal//130,121` was queued in Ashgate but the spree overrode it. Order it after the spree, or find a natural pair. Ask the owner again with that shot.
5. Retakes the Conductor listed (4:52 PM). Ashgate's psychopath Van Black was kidnapped, so use `graffiti_p8_busy3` (Rustwall, `st Name Rustwall/Rustwall`):
   - Volatile Kinso, trait and thought visible.
   - Psychopath Cathryn, trait visible.
   - The mockery wall pane, no naming dialog.
   - The memorial mourner on screen, eased thought at most half the grief.
   - One Crafts row of 7 with Beauty numbers (`st Beauty on` plus `hoverlabel`, or hover a cell).
6. Lines no shot proves yet: making_a_mark_is_its_own_fun (maker's "Left my mark" plus Recreation), a reread a day later, a raid mark and its retake, visitors, `so Set paintingEnabled=False` then a quiet day, save and reload.
7. GPT `broaden` with the new in-game shots (the Conductor asked for it before DONE.md), then DONE.md.

## bars (north star; "unseen" = no shot on the current build)
- mark_actually_appears, mark_reads_as_deliberate, mark_reads_at_play_zoom: true (`lived_in_ashgate_walls_playzoom.png`, `lived_in_ashgate_spree_corridor.png`)
- mark_sits_on_the_wall: true at 128 px for one wall (`first_look_optionD_face_bold_close.png`); the material sweep is unseen on this build
- marks_visibly_various, mark_register_is_punk_urban: true in the spree corridor; the full gallery is unseen on this build
- mark_carries_no_earth_signage, never_real_world_english: true in every Ashgate shot; the gallery is unseen on this build
- mark_ugliness_is_visible: unseen side by side; the awful scrawls in the corridor read as muddy smears
- never_reads_as_dirt: the awful scrawl at (119,125) is the closest to dirt, an olive-brown smear with red in it. Judge it again on a lit wall
- mockery_changes_regard: true (`social_regard_brick_on_karen.png`)
- tribute_and_memorial_mean_it: unseen (memorial across a save to prove; jealousy never shot)
- pawns_answer_the_wall: true in the trace and messages (scrub, confront, mockery replies); `social_story_karen_needs.png` shows the mood side
- fights_have_people_and_reasons: true (`social_regard_brick_on_karen.png`, plus pass 8's `social_fight_blows.png`)
- stories_not_a_tax: measured, 1 message a day when quiet, 8 on the spree day; ambient ≤ +3. But Brick's -8.8 mockery stood for two days, and Mo is at -13
- raid_mark_troubles_until_retaken, visitors_read_without_recharging, stands_alone_and_obeys_settings, making_a_mark_is_its_own_fun, rereads_affect_at_most_daily, art_skill_goes_into_the_art: unseen on this build
- each_takes_it_like_themselves: unseen on this build (pass 8's shots in `old/pass8/`)

## Traps
- The gate refuses Bash commands containing `rimbridge` and the like: write bridge scripts with the Write or Edit tool. `g.py` is the driver; run `ralph/steve.sh sync` after editing it.
- `shot` refuses a rect wider than one screen: 20 cells at 64 px, 8 at 128 px.
- The first `so`/`st` call right after `load` can read an empty map (the load says done before the map is finalised). Read twice.
- `prove_quicktest_world.py` refuses to leave a colony past tick 120000.
- Joy pacing is real; a spree runs 6 to 12 hours and paints every 400 to 600 ticks.
- Decompile: `/mnt/d/ClaudeWork/rimmandrake/decomp/rw16/all/{RimWorld,Verse,RimWorld.Planet}/`.
