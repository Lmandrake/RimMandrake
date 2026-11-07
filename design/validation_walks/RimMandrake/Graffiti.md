# RimMandrake: Graffiti Framework — validation walk
subject: src/RimMandrake/Graffiti  (packageId `mandrake.rm.graffiti`)
deps: none listed in modDependencies (loadAfter Ludeon.RimWorld only)
list: minimal
status-hint: engine for the graffiti program, superseding Mlie.GraffitiMod's vandal-spree mechanic — an idle/unhappy artistic pawn seeks the "paint graffiti" joy job or, on a mental break, is forced to paint repeatedly, spawning `RM_Graffiti_Vandal` filth on nearby walls

## must be true
- `RM_PaintGraffitiJob`/`RM_PaintGraffitiJoy` let a pawn walk to a nearby wall and paint `RM_Graffiti_Vandal` filth there as Meditative joy (`JobDriver_PaintGraffiti`, `JoyGiver_PaintGraffiti`).
- The forced mental break `RM_GraffitiPaintingSpreeBreak` (worker `MentalState_GraffitiSpree`, think tree `RM_GraffitiPaintingSpreeThinkTree`, state def `RM_GraffitiPaintingSpreeState`) drives repeated painting for a stretch rather than one job.
- `RM_Graffiti_Vandal` filth actually places — its `placementMask` requires the target terrain's own `filthAcceptanceMask` cover `Unnatural`; on a terrain that does NOT declare `Unnatural` acceptance, `TryMakeFilth` must legitimately produce nothing (that is not a bug, per the file's own comment about the prior all-sources regression).
- `ModExtension_Graffiti` is present on every mark def; `GraffitiPool` (form/poolWeight/meme/skill/hostility gates), `Filth_Mark` (sigil tier A), `RaidExitTagger` and `AutoCleanProtection` read it. The painted def is a weighted pick from the spree pool, not always `RM_Graffiti_Vandal`.
- `RM_BaseGraffiti` (abstract parent) is `thingClass RimMandrake.Graffiti.Filth_Mark` (a `Filth` subclass carrying maker/faction/ideo provenance), not the retired donor's Filth_Graffiti subclass.

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rm.graffiti" and no XML error naming `ThingDefs_Graffiti.xml`/`JobDefs_Graffiti.xml`/`MentalStateDefs_Graffiti.xml`   # load-time
2. [D] def read-back: `ThingDef` `RM_Graffiti_Vandal` exists; `ParentName` chain includes `RM_BaseGraffiti`; `thingClass` = `RimMandrake.Graffiti.Filth_Mark`; `filth/placementMask` contains `Unnatural`
3. [D] def read-back: `JobDef` `RM_PaintGraffitiJob` exists; `driverClass` = `RimMandrake.Graffiti.JobDriver_PaintGraffiti`
4. [D] def read-back: `JoyGiverDef`/joy-source `RM_PaintGraffitiJoy` exists and names `RM_PaintGraffitiJob`
5. [D] def read-back: `MentalBreakDef` `RM_GraffitiPaintingSpreeBreak` exists (state def `RM_GraffitiPaintingSpreeState`); its worker resolves to `RimMandrake.Graffiti.MentalState_GraffitiSpree`
6. [D] def read-back: `RM_Graffiti_Vandal` carries a `RimMandrake.Graffiti.ModExtension_Graffiti` modExtension (non-null `GetModExtension`)
7. [B] jawa/spawn_pawn a colonist onto a fresh player-faction map cell next to a wall with an `Unnatural`-accepting floor, `jawa/order_pawn` (or `jawa/pawn_force_mental_break` with `breakDef=RM_GraffitiPaintingSpreeBreak`) to force the paint job → expect the pawn's current job resolves to `RM_PaintGraffitiJob`/`RM_GraffitiPaintingSpreeBreak` state (jawa/pawn_get or jawa/pawn_mental)
8. [B] jawa/list_things for every `Filth_Mark`-derived def near the wall after the job/break runs some ticks → expect at least one mark to have spawned (the spree pool picks among Vandal, Tags, ThrowUps and Glyphs; counting Vandal alone false-fails)
9. [D] read the spawned `RM_Graffiti_Vandal` filth thing's Beauty stat (jawa/thing_stats) → expect negative, per "negative Beauty" in the mod's own description

## [S]
Whether the six shipped texture variants of `RM_Graffiti_Vandal` (Graffiti Mod (Continued)'s art) actually read as legible marks on a wall at normal zoom is a human-pass concern (MOD_HUMAN_EXPLORATION_PASS_1). ⬇️ **Superseded as the authority by the `## north star` section below** — that question is now a binding bar, not a deferred concern.

## anti-guessing notes
- RULED OUT: the spree mod fails to start. Live A2 2026-11-03T14:36Z: `jawa/pawn_force_mental_break` returned `mentalStateAfter` = `RM_GraffitiPaintingSpreeState`; the row's UNMEASURED was the harness (the companion latches the painter's own new mental state as a `threat` stop). validation.py now declares it with `_own_spree` (clockgate.expected_disturbance, painters only, spree state only); guard `src/RimMandrake/Graffiti/selftest_graffiti_spree_surprise.py`.
- UNTESTED (SITE theories, A2 2026-11-03): `forced_paint_job` stopped on `hostile_arrival: Toughspike` (a wild hostile not cleared before the wait); `spree_wall.spree_runs` stopped on `death: Crush` at 60 ticks (roof collapse after `clear_area`?). Neither is a mod fault until shown.
- RULED OUT (test pilot gen 19, live 2026-11-05, small list): the fresh-map step fails. `prove_quicktest_world.py` left a Playing test game (tick 15035) for the menu and started a fresh 250x250 quicktest, `success:true`, tick 1, one map, in 12 s. The suite then ran in full: every functional/state row PASS (spree rows included, so `_own_spree` holds live), judge 12 PASS / 2 FAIL / 7 UNMEASURED.
- HARNESS (gen 19): WSL lost 4 of 6 `python.exe` launches (rc 1 in 10 s, empty stdout, only `UtilAcceptVsock: accept4 failed 110`), and A2 stopped at `[0 needs]` with exit 2. `northstar_full._run` now retries a lost launch through `winbuild.run_interop_captured`; guard: `selftest_graffiti_fresh_quicktest.py` S8.
- HARNESS (gen 19, UNMEASURED bars): `rimworld/screenshot_cell_rect` captures at the CURRENT camera zoom (rootSize 24, which is about 20 px per cell in a 941-px viewport), while `mark_reads_at_play_zoom` asks for about 64 px. All 7 UNJUDGEABLE verdicts cite size (marks about 10 px, strips 432x59). The fix was measured live: `rootSize` 7.35 gave 450x321 px for a 7x5-cell rect (64.3 ppc). `suite.screenshot` passes no rootSize. Note: viewport height = 2 x rootSize x ppc.
- MOD (gen 19, the 2 FAILs): `RM_Graffiti_Vandal` variants `vandal_1.png` (a clean prohibition sign) and `vandal_0.png` (an electrical-hazard bolt) read as real-world signage, which breaks `mark_carries_no_earth_signage`; under the owner's 2026-09-16 ruling the glyph is replaced, never exempted. The two judge pages agreed independently. RULED OUT: the CrossOut or WarningGlyph art (both checked, neither holds those shapes).
- UNEXPLAINED (gen 19): in the run, colonists Alekey (tick 601, cell 125,125) and Stonejaw (tick 1501, cell 123,129) died by a direct Kill with 0 damage (`jawa/damage_log` kind kill, amount 0; vitals "died: unknown cause"), both on chain boundaries. Two Fingerspikes (ids 8592/8593) "arrived" and left in the same sample at tick 1501. RULED OUT: `_clear_pawns` vanish as the killer (each vanish reads as `departed`, never a death). The rows still PASS.
- HARNESS (test pilot gen 21, offline from the gen 19 live replies): the 7 UNJUDGEABLE judge rows were the capture, not the art. `rimworld/screenshot_cell_rect` with no `rootSize` shoots at the CURRENT zoom (rootSize 24 = 19.7 px per cell), and the bars are judged at ~64. Every judged shot now passes `ppc=PLAY_PPC` (64). `modcheck/play_zoom.py` learns K = px-per-cell × rootSize from the tool's own reply (clipRect ÷ paddedRect × appliedRootSize), shoots at K/64, and checks the PNG is within 5%. A gallery page (22×26 cells) is taller than one 64-ppc screen (~15.7 cells), so it is shot in bands and stitched into ONE image; `judge_cli` judges only a component's LAST shot. spree_variety stays at the current zoom: it is 44 cells wide and judged PASS. Guard: `selftest_graffiti_play_zoom.py` (red on the held code; S7 replays the live replies). RULED OUT: a fixed rootSize (7.35) as the fix, since K depends on the window (live K 472 to 474). RULED OUT: splitting the gallery into more components, which would rename the required checks' claimed_by rows. STILL OPEN: two UNJUDGEABLE reasons are not about zoom (beauty_pair: "nothing labels the Beauty value"; gallery_page_1: "no reference of known size"). The next live A2 shows whether they survive at 64 ppc.
- CHANGED (Ralph pass 1, 2026-11-06): a paint job now makes one finished mark, then moves down the wall (no longer one cell repainted every 250 ticks); marks draw on the wall cell itself and go with their wall; marks use shaderType Mote; idle colonists can tag (`JobGiver_IdleTag`). HARNESS: the screenshot tool writes asynchronously, so a reused filename copies the previous run's picture (`stage_colony.py` uses unique names). Colonists draw at their last on-screen spot after `safe_advance` with the camera elsewhere. See `ralph/PROGRESS.md`.

## north star
state: VALIDATED
validated-hash: 335bccf3b6cbda91ab995e52922ffd51ae11365b0652dc0481dc6bf8fc10693c

✅ **BINDING.** Every line below was ruled or accepted in the owner's sitting of
2026-09-16 and validated on his word — *"Validate now, all 10 lines"* — at the hash
above. 8 must-show + 2 cannot-show now refuse Graffiti until a component claims each
with `shows=` and a screenshot satisfies it. Any later edit to this section reverts
it to DRAFT by hash mismatch, so amend it only in another sitting with him.

(`state:` is kept as a single bare token because `modcheck/cli.py` parses that field.)

### the experience  (OWNER'S WORDS — verbatim)

2026-08-30, filing `GRAFFITI_MOD_EXPANSION_1`:

> *"Add a queue item to assess the graffiti mod and expand it to include sacred
> graffiti, socially infuriating graffiti or amusing graffiti, or even beautiful
> graffiti."*

2026-08-31, `GRAFFITI_FRAMEWORK_BUILD_1`:

> *"Fully flesh out the graffiti mod now for tremendous application in the Jawa
> game. Jawas love graffiti. All the various kinds. Go for it!"*

2026-09-09, `GRAFFITI_PUNK_IDEOLIGION_SCOPE_1`:

> *"we want the base Graffiti mod to have a wide variety of functionality within
> it, not just the base examples we've provided in vanilla. It should be a mod
> more aligned to punk style graffiti such as is seen in urban settlements, as
> well as ideoligion-inspired sigils taken from the Rimworld ideoligions as they
> exist in the game."*

🔑 The through-line in all three: **variety, and marks that read as punk/urban
graffiti.** *"All the various kinds"* is a demand about appearance, not mechanism.

### must show

**A mark on a wall**
- [ ] `mark_actually_appears` — after a paint job or spree completes, a mark is
      visibly on the wall. Not an empty wall with a clean job log. (This is in the
      checklist because it has already failed silently: a colonist painted for
      ~20000 ticks with dozens of `TryMakeFilth` calls and produced nothing,
      because `placementMask` was `Any`. Every state assertion passed at the time.)
- [ ] `mark_reads_as_deliberate` — a mark reads at play zoom as something a hand
      made on purpose, not as scattered dirt or a smudge.
- [ ] `mark_reads_at_play_zoom` — every mark reads AS A MARK at normal play zoom
      (~64px), not only when zoomed in. 🔴 **Owner ruling, 2026-09-16**: this
      replaces a drafted `mark_scale_consistent` line. Scale *uniformity* is the
      wrong bar — real graffiti varies wildly in scale and a big piece beside a
      small tag is correct. The real defect is a mark that cannot be read at the
      zoom the game is played at.
- [ ] `mark_sits_on_the_wall` — a mark reads as being *on* the wall face, aligned
      to it, not as a decal floating over the floor beside it.

**Variety — his "all the various kinds"**
- [ ] `marks_visibly_various` — several marks in one colony are visibly different
      kinds of mark, not recolours of one.

**Register — punk/urban, and this world**
- [ ] `mark_register_is_punk_urban` — the mark set reads as urban/punk graffiti,
      not as clip-art icons or modern signage.
- [ ] `mark_carries_no_earth_signage` — no mark reads as a contemporary real-world
      sign (road-hazard triangle, exit sign, traffic glyph). 🔴 **Owner ruling,
      2026-09-16**: kept at FULL scope covering symbols, not narrowed to lettering
      only. He chose to replace the offending glyph rather than exempt it.

**Beauty legibility**
- [ ] `mark_ugliness_is_visible` — a Beauty −15 vandal scrawl looks worse than a
      Beauty −3 tally at a glance. The stat and the picture agree.

### cannot show

- [ ] `never_real_world_english` — legible real-world English words, or a
      third-party author's tag, in a mark. 🔴 **`RM_Graffiti_Vandal` shows this
      today**: "TARTE" is plainly legible in `vandal_0.png` (the donor author's own
      tag — Tarte/emipa606, art copied under MIT per About.xml), alongside further
      English tags in yellow, red and blue. Confirmed by looking at the sprite
      composited on a wall, 2026-09-16. `GRAFFITI_PUNK_IDEOLIGION_SCOPE_1` already
      put English lettering out of scope; the shipping default violates it.
- [ ] `never_reads_as_dirt` — a mark indistinguishable from vanilla filth at play
      zoom. If graffiti reads as a mess rather than a message, the mod is doing
      nothing his three quotes asked for.

### what this checklist refuses today, and why that is correct

Two of the four shipped marks fail it as written, both confirmed by eye
2026-09-16 rather than inferred:

1. **`RM_Graffiti_Vandal`** fails `never_real_world_english` and
   `mark_reads_at_play_zoom`. It is a dozen tiny doodles scattered across a 640²
   canvas, so at ~64px each is a few pixels of mush — and it is the mod's ONLY
   spontaneously-spawned mark, so the one mark players see unprompted is the one
   that does not read. → `GRAFFITI_VANDAL_ART_REGEN_1`.
2. **`RM_Graffiti_WarningGlyph`** fails `mark_carries_no_earth_signage` — a modern
   ISO hazard triangle with an exclamation mark. In fairness the brushwork is
   genuinely rough and hand-painted; it is the *iconography* that is Earth.
   → `GRAFFITI_WARNGLYPH_INUNIVERSE_1`.

`RM_Graffiti_TallyMarks` and `RM_Graffiti_Scratches` pass, and are the mod's best
art. (Noted honestly: groups-of-five-with-a-slash is also an Earth convention, but
a far more universal one than ISO signage, and it was not ruled against.)

### deliberately NOT a line here
A drafted `mark_variants_do_not_repeat` line was **cut by owner ruling
2026-09-16**: adjacent repeats depend on `Graphic_Random`'s pick rather than on the
art, so a run would pass or fail by luck. The underlying 6:2:2:2 variant imbalance
is real and is content work — `GRAFFITI_VARIANT_COUNTS_1`, not a visual bar.
