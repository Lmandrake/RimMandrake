# BirthHatchDemo — validation walk
subject: src/RimUtinni/BirthHatchDemo
packageId: mandrake.rut.birthhatchdemo  (from About.xml, verbatim)
deps: Ludeon.RimWorld.Biotech (DLC required for CompProperties_Hatcher / EggFertBase; not a third-party mod)
list: minimal+biotech    # assumes the campaign's own Jawa pawnkind mod (RSW_Jawa) is already part of the minimal list, since that is the player's own clan kind
status-hint: DEMONSTRATION mod only (owner, 2026-09-02) — proves the bridge can drive pregnancy through egg-hatch into a live baby Jawa; not campaign content, delete once the answer is recorded (LIVE_BIRTH_AND_HATCH_DEMO_1).

## must be true
- `RUT_DemoEggJawa` (ThingDef, ParentName="EggFertBase") exists and carries exactly one `CompProperties_Hatcher` with `hatcherDaystoHatch=0.1` and `hatcherPawn=RSW_Jawa`.
- The egg is spawnable and, once enough real game ticks pass (0.1 day = 6000 ticks, GenDate.TicksPerDay=60000), CompHatcher hatches it into a new pawn of kind RSW_Jawa at DevelopmentalStage.Newborn (per CompHatcher.cs:85, quoted in the file's own header comment) — i.e. a baby Jawa, not an adult and not the egg surviving unhatched.
- The hatched pawn is a genuinely NEW pawn (a fresh ThingID never seen on the map before this call), not a recycled world pawn — CompHatcher.cs:85 passes `forceGenerateNewPawn: false`, the same defect class the file's own header warns was already found and fixed elsewhere (SPAWN_PAWN_SUBSTITUTES_VANILLA_KIND_1); this mod does NOT patch that, so the walk must check for it rather than assume it away.
- The egg thing itself is consumed/despawned once hatching completes (vanilla CompHatcher behavior — the egg does not linger post-hatch).

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rut.birthhatchdemo" and no XML error naming RUT_DemoEgg.xml
2. [D] def read-back: ThingDef RUT_DemoEggJawa; parent chain includes EggFertBase; comps include CompProperties_Hatcher with hatcherDaystoHatch=0.1, hatcherPawn=RSW_Jawa
3. [B] jawa/list_pawns → snapshot every pawn's ThingID on the map BEFORE hatching (baseline set, for the "genuinely new" check in step 7)
4. [B] rimworld/spawn_thing defName=RUT_DemoEggJawa x=X z=Z → egg spawns; note its ThingID
5. [B] jawa/list_things defName=RUT_DemoEggJawa → confirms exactly one egg present, isCompleteList=true
6. [B] rimworld/step_game_ticks ticks=6100 (0.1 day = 6000 ticks + margin) pauseFirst=true → advances real ticks so CompHatcher.CompTick actually runs (NOT jawa/time_set_ticks, which jumps the counter without simulating and would never fire the hatch)
7. [B] jawa/list_pawns → exactly one new pawn ThingID not in the step-3 baseline; its kindDef (via jawa/pawn_get) = RSW_Jawa and developmental stage = Newborn (baby, not adult)
8. [B] jawa/list_things defName=RUT_DemoEggJawa → 0 results (egg consumed by the hatch)
X. [S] (human pass) none — this is a mechanism-proof demo mod with no bespoke art (placeholder color tint only); no visual pass warranted
