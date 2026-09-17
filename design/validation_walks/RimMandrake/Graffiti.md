# RimMandrake: Graffiti Framework — validation walk
subject: src/RimMandrake/Graffiti  (packageId `mandrake.rm.graffiti`)
deps: none listed in modDependencies (loadAfter Ludeon.RimWorld only)
list: minimal
status-hint: engine for the graffiti program, superseding Mlie.GraffitiMod's vandal-spree mechanic — an idle/unhappy artistic pawn seeks the "paint graffiti" joy job or, on a mental break, is forced to paint repeatedly, spawning `RM_Graffiti_Vandal` filth on nearby walls

## must be true
- `RM_PaintGraffitiJob`/`RM_PaintGraffitiJoy` let a pawn walk to a nearby wall and paint `RM_Graffiti_Vandal` filth there as Meditative joy (`JobDriver_PaintGraffiti`, `JoyGiver_PaintGraffiti`).
- The forced mental break `RM_GraffitiPaintingSpreeBreak` (worker `MentalState_GraffitiSpree`, think tree `RM_GraffitiPaintingSpreeThinkTree`, state def `RM_GraffitiPaintingSpreeState`) drives repeated painting for a stretch rather than one job.
- `RM_Graffiti_Vandal` filth actually places — its `placementMask` requires the target terrain's own `filthAcceptanceMask` cover `Unnatural`; on a terrain that does NOT declare `Unnatural` acceptance, `TryMakeFilth` must legitimately produce nothing (that is not a bug, per the file's own comment about the prior all-sources regression).
- `ModExtension_Graffiti` is present on `RM_Graffiti_Vandal` (category/quality/maker-subject/god-satiation-hook fields) but nothing reads it yet this pass — a check should confirm the extension is attached, not that anything consumes it.
- `RM_BaseGraffiti` (abstract parent) is `thingClass Filth`, not the retired donor's custom Filth_Graffiti subclass.

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rm.graffiti" and no XML error naming `ThingDefs_Graffiti.xml`/`JobDefs_Graffiti.xml`/`MentalStateDefs_Graffiti.xml`   # load-time
2. [D] def read-back: `ThingDef` `RM_Graffiti_Vandal` exists; `ParentName` chain includes `RM_BaseGraffiti`; `thingClass` = `Filth`; `filth/placementMask` contains `Unnatural`
3. [D] def read-back: `JobDef` `RM_PaintGraffitiJob` exists; `driverClass` = `RimMandrake.Graffiti.JobDriver_PaintGraffiti`
4. [D] def read-back: `JoyGiverDef`/joy-source `RM_PaintGraffitiJoy` exists and names `RM_PaintGraffitiJob`
5. [D] def read-back: `MentalStateDef` `RM_GraffitiPaintingSpreeBreak` exists; its worker resolves to `RimMandrake.Graffiti.MentalState_GraffitiSpree`
6. [D] def read-back: `RM_Graffiti_Vandal` carries a `RimMandrake.Graffiti.ModExtension_Graffiti` modExtension (non-null `GetModExtension`)
7. [B] jawa/spawn_pawn a colonist onto a fresh player-faction map cell next to a wall with an `Unnatural`-accepting floor, `jawa/order_pawn` (or `jawa/pawn_force_mental_break` with `breakDef=RM_GraffitiPaintingSpreeBreak`) to force the paint job → expect the pawn's current job resolves to `RM_PaintGraffitiJob`/`RM_GraffitiPaintingSpreeBreak` state (jawa/pawn_get or jawa/pawn_mental)
8. [B] jawa/list_things `defName=RM_Graffiti_Vandal` near the wall after the job/break runs some ticks → expect at least one `RM_Graffiti_Vandal` filth thing to have spawned
9. [D] read the spawned `RM_Graffiti_Vandal` filth thing's Beauty stat (jawa/thing_stats) → expect negative, per "negative Beauty" in the mod's own description

## [S]
Whether the six shipped texture variants of `RM_Graffiti_Vandal` (Graffiti Mod (Continued)'s art) actually read as legible marks on a wall at normal zoom is a human-pass concern (MOD_HUMAN_EXPLORATION_PASS_1). ⬇️ **Superseded as the authority by the `## north star` section below** — that question is now a binding bar, not a deferred concern.

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
