# Code review batch 3 — 2026-10-06 (FOUNDRY helper, offline)

Status: DONE. Engine facts checked with RimSage (decompiled 1.6). Nothing committed.

## RM_CompSillochAmbush.cs — CLEAN (marked)
CompTick is right for a Pawn comp (Pawn.Tick -> ThingWithComps.Tick loops CompTick). lastVictim
Scribe_References: a destroyed/GC'd victim saves as null (CheckSaveReferenceToDestroyedThing), so no
dangling ref. A tame silloch never clears a dead lastVictim — harmless (only read by the wild-only eat path
and by a target-equality check). Diet CarnivoreAnimal, so the Ingest-corpse job is legal.

## RM_BrathekBoring.cs — CLEAN (marked)
Startup + settings-close both call ApplySettings; flag add/strip is idempotent.

## RM_WreckWeathering.cs — CLEAN (marked)
Def.ResolveReferences calls extension.ResolveReferences(this) after cross-refs resolve; tier is read lazily
by name, and ConfigErrors run after, so a shifted tier is still validated. `applied` guards re-resolve.

## Antiquities (CompAntiquity, AntiquityUtility, WorkGiver_ExamineAntiquity, JobDriver_ExamineAntiquity) — CLEAN (marked)
Listener fires once (catalogued flag set first, reservation 1 per piece) -> no double credit. FailOn with a
null target returns fail, not NRE. Finish-action ticksLeftThisToil gate still correct.
FINDING (minor, not fixed): a journal already `read` via the old CompUsable route but not `catalogued` is
still offered after VOICE (HasCatalogueListener is true) — a pawn spends a day, Read() returns ALREADY READ
silently, no letter. Pre-update saves only.

## PilgrimCamps.cs — FIXED (not marked; uncommitted)
BUG: bedroll (1x2) spawned at c+West with Rot4.East occupies c+West AND c (GenAdj.AdjustForRotation), and
GenSpawn.SpawningWipes edifice-over-edifice wiped the campfire placed at c: every camp lost its cold fire.
Fix: Rot4.North (covers c+West and c+NW, the journal's cell — "journal on the bedroll"), inside CampFits' 3x3.
FINDING (minor, not fixed): a save taken mid old UseItem read on a journal: JobDriver_UseItem's FailOn
derefs TryGetComp<CompUsable>() (now absent) -> one red error, error-recover job; journal remains readable at
the station. No double credit.
Rebuilt: RimMandrake.Utinni.ScarlandsLadder.dll + .srchash.

## RM_RustCathedralMod.cs — FIXED (not marked; uncommitted)
BUG: the settings body (~570px) was split into equal thirds (~190px each), and Listing_Standard.Begin is a
clipping BeginGroup. The own section needs ~400px, so the borehulk rows and cross-biome toggle were clipped
out of reach (and the tail of the Hum block too). Fix: fixed section heights (470/430/240) inside
Widgets.BeginScrollView. Rebuilt: RimMandrake.RustCathedral.dll + .srchash.
