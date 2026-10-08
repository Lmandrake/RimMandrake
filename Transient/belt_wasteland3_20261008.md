# WASTELAND_LIVE_FIXTURE_FIXES_1 — offline pass 2026-10-08

## A3 tamed_gripper_never_steals
(pending)

## A4 Pusberry RawBerries
(pending)

## Log
- Read evidence 193257Z. Mechanism (RimSage 1.6): Harvest JobDef -> JobDriver_PlantHarvest, no RequiredDesignation; yield = YieldNow() (HarvestableNow && growth>minGrowth) -> TryPlaceThing near actor. RM_Pusberry is TreeBase -> inherits harvestFailable=false, so the fixture comment blaming a low-Plants roll for Pusberry was false. Def is fine (harvestYield 10, RawBerries, growth 1.0).
- jawa/destroy_batch NEVER destroys pawns (tool description); `_reset_pad`'s categories="Pawn" call is inert, so grippers (theft ON) + wild animals + earlier handlers survive into flora_harvest (log: "8 pawn(s) left alone"). Pusberry harvested 2nd and its berries lay ~3500 ticks before the read: stealable (gripper takes any unforbidden haulable), edible, haulable. Verdict A4: FIXTURE, not mod bug (unmeasured which pawn took them).
- A3: RM_JobDriver_GripperSteal has job-wide FailOn(pawn.Faction != null): an ordered steal on a tamed gripper is accepted then ends at once (afterJobDef GotoWander) -- that IS the property. Fixture mis-read success=False as a refusal. Verdict A3: FIXTURE.
- FIX (validation.py): tamed comp clears wild animals (destroy_bulk factionlessAnimals), treats accepted+ended-at-once as the FailOn behaviour (UNMEASURED only if not accepted), notes job shape + Gold left. Flora: destroy_bulk nonColonists, handler Hauling=0, harvest ONE plant at a time and read the product as soon as the plant is cut (UNMEASURED if never cut). Removed the inert destroy_batch categories="Pawn" calls and the false "pads empty of pawns" docstring; corrected the false low-skill explanation for Pusberry.
- FIX (selftest fake): destroy_batch no longer removes pawns (it lied vs live); destroy_bulk + set_work_priority added; tamed steal order returns the LIVE shape; new break tamed_steals; stray-thief model (wild gripper takes yield lying 1000+ ticks). Proof: OLD fixture against the new fake reproduces both live symptoms (tamed UNMEASURED same shape; all four yields lost); NEW fixture passes all.
