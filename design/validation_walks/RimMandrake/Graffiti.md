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
Whether the six shipped texture variants of `RM_Graffiti_Vandal` (Graffiti Mod (Continued)'s art) actually read as legible marks on a wall at normal zoom is a human-pass concern (MOD_HUMAN_EXPLORATION_PASS_1).
