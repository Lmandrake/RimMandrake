# STILLSAND_FIXES_LIVE_PROOF_1 — live proof for the five 2026-10-01 live-session fixes

The five defects from the 2026-10-01 FOUNDRY live session (`Transient/LIVE_SESSION_2026-10-01.md`)
were fixed from source and the decompiled engine, with no game running. Each fix was closed on its
commit. This item holds the live proof. Deploy `mandrake.rm.biomes` (Stillsand, Contagion, Cauldron,
CreatureBehaviors) and `StructureInjections` first, then load the full list.

## What decides each one (Player.log strings, load and session)

1. **STILLSAND_LOAD_DEF_ERRORS_1.** None of these appears on a full-list load:
   `Exception parsing RimWorld.TreeCategory from "Standard"`, `doesn't correspond to any field in type
   StartingHediff`, `animal has trainability = null`, `tries to use meat from Megascarab`,
   `No Verse.BodyPartGroupDef named FrontLegs`, `No textures found at path Things/Plant/RM_` (Contagion's
   six single-file plants are now `Graphic_Single`). `jawa/get_defs ThingDef/RM_KneelOllim` is found.
2. **OORRIK_PAWNGEN_NRE_1.** The load no longer logs `No Verse.BodyDef named Rat`.
   `jawa/spawn_pawn kindDef=RM_Oorrik` spawns, and no `Error while generating pawn` names RM_Oorrik.
3. **SANDSWIM_TAKE_FUNNEL_NEVER_PLACED_1.** After a swimmer kill on Sand,
   `jawa/list_things defName=RM_Filth_DisturbedSand` is 1 or more at the victim's cell. The letter reads
   "struck it down". The corpse staying is intended: it is the predator's meal.
4. **SOORRAK_FLIGHT_JOBSTART_NRE_1.** A wild RM_Soorrak runs 5,000 ticks with zero
   `Exception ticking RM_Soorrak`. Check by log and `jawa/pawn_flight action=report` state read only.
   No flight watching without the owner (CLAUDE.md flyer rule). The fix is a prefix guard
   (`RM_FlightJobStartGuard`). Which job ends in its first toil is still unknown. While the soorrak runs,
   note its job list, because a job that ends instantly every think cycle is a separate defect.
5. **RIMPLACE_GENSTEP_NRE_1.** Regenerating a map that rolls `RSW_GenStep_WhisperSarlaccSign` (or any
   RUT whisper selector carrying a `GenStep_RimplacePlan`) logs no
   `Error in GenStep: System.NullReferenceException` at `GenStep_RimplacePlan.Generate`. It also logs no
   `not found under any running mod`.

## criteria
- All five checks above pass on one full-list session. Record the session as a `rimflow verify` run.
