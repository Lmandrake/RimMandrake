## spec

Design Version: FlowWorks 0.1.0 (current, a Problem against the locked bars). Filed by the FlowWorks ticket sweep of 2026-11-22
(RIMMANDRAKE_SWEEP_FLOWWORKS_TICKETS_MERGE_TO_MODERN_BUILD_THE_VALUABLE), which merged these older tickets into this one, one
cause or one file group. Each old ticket's prose is in `infrastructure/state/items/closed/<ID>.md` and its history in
`rimflow show <ID>`; read the one you work on to its end before you build.

FlowWorks: nine built behaviours still owe one live row each; run them in one in-game visit.

## merged tickets

- `RIMMANDRAKE_PROVE_FLOWWORKS_RAILINGS_HOLD_AGAINST_BLAST_THROWS` (proposed): Bridge railings exist to stop a pawn being blown off: a railing is a rail for blast throws (Building_SuspensionDeck.cs:417, RM_FallRails.cs:43) but no live row reads it. Acceptance test: live, ExplosiveKnockback loaded: a colonist on a railed suspension deck beside its rail, a knockback blast on the far side throwing toward the rail: lands on the deck, no descent; a twin on a railings-off deck is thrown into the pit (UNRUN: the game was his)
  - sweep reading: owner note on walk 2026-11-20 #20; rail logic exists (Pits/Suspension/Building_SuspensionDeck.cs:417, Superdeep/RM_FallRails.cs:43) but no live row reads blast throws against it; last rail commit b7989f6a3c covers walked steps only
  - its check: with ExplosiveKnockback loaded, a colonist on a railed deck beside its rail lands on the deck after a blast toward the rail; a twin on a railings-off deck falls into the pit
  - files: `src/RimMandrake/FlowWorks/Source/Pits/Suspension/Building_SuspensionDeck.cs`, `src/RimMandrake/FlowWorks/Source/Superdeep/RM_FallRails.cs`
- `UNDERPASS_REACH_VERIFY_WALK_UNDER_FOR_REAL` (built): Live row for a01c76fe25: CanReach and A* agree in game for a colonist in a trench walking under a surface suspension deck, and a colonist on a 4 m ledge crossing a sunken deck at ledge height (STATE reads: RelativeVeto, path found)
  - sweep reading: pawn reach under a suspension deck (0.1.0 bars inv_bridges / hung_bridge_spans); blocker PROOFREACH_FIX_PAWNLESS_READ_HAS_NO_WALKER done; latest live verify 2026-11-22 result=partial (FlowWorks_20261122T121858Z.html, 0e0ece4b32)
  - its check: testq FlowWorks row for UNDERPASS_REACH A1/A2 reads pass, not partial
  - files: `src/RimMandrake/FlowWorks/Assemblies/RimMandrakeFlowWorks.dll`
- `JAWA_DROWNING_PROVE_RAT_SIZED_IN_SHALLOWS` (built): Captain's 8 RM_PitDrowning downs on the GSS theft run: natural brine + Jawa H=0.5 m, not pit pathing; prove the cell live
  - sweep reading: a failure happened: 8 RM_PitDrowning downs of a 0.5 m Jawa in natural brine shallows (GSS theft run); live proof blocked because ProofDrown reads water=0.00 on natural cells (PROOFDROWN_FIX_NATURAL_WATER_READS_ZERO)
  - files: `src/RimMandrake/FlowWorks/Source/Swimming/RM_Swim.cs`
- `PROOFDROWN_FIX_NATURAL_WATER_READS_ZERO` (ready): RM_PitFillEffects.ProofDrown reads ex.WaterMetresAt (dug cells only) so it reports water=0.00 on natural brine where the RM_Swim tick reads RM_SwimWater.WaterMetresAt=2.00; switch the probe to the natural-aware reader
  - sweep reading: offline reader selftest GREEN 2026-11-17; its only acceptance is the A1 L2 live clause, unrun; it blocks JAWA_DROWNING_PROVE_RAT_SIZED_IN_SHALLOWS
  - its check: on a quicktest map ProofDrown on a standing Jawa mid-pool in natural water reads the same metres as RM_SwimWater.WaterMetresAt (jawa_shallows_proof JS1-JS4)
  - files: `src/RimMandrake/FlowWorks/Source/RM_PitFillEffects.cs`
- `RIMMANDRAKE_PROVE_FLOWWORKS_DRILL_SURVEY_ROLLS_PER_BIOME_LIVE` (proposed): FlowWorks 0.1.0 inv_drilling in game: the subsurface survey finds liquid on the biomes whose Def gives one and none elsewhere (cycle-4 DRILL_RIGHT_MAPS_NOT_KERNEL)
  - sweep reading: 0.1.0 bar inv_drilling row DRILL_RIGHT_MAPS_NOT_KERNEL left UNSETTLED by blind cycle 4 (lane1_rows_after_fix.jsonl); sc_garden sets the yield, so the per-biome survey roll is unproven; no commit since names the item
  - its check: live: concept_scenes row set on two biomes whose RM_SubsurfaceLiquidBiomeExtension differ; survey result matches each Def with no yield written
  - files: `src/RimMandrake/FlowWorks/northstar/concept_scenes.py`, `src/RimMandrake/FlowWorks/Source/Drilling/RM_MapComponent_SubsurfaceLiquid.cs`
- `RIMMANDRAKE_SHOW_SOAKER_IN_DEEP_POOL_FURR_VANISHED` (proposed): A colonist soaking in a 4 m geyser pool, and the geyser itself, are not drawn at all
  - sweep reading: no commit cites the item; related vent-centre fix 11cbfa650a does not touch the soaker's draw; live 2026-11-12 capture soak_furr_Gbrim.png showed a flat blue square (no pawn, no vent) and the job took a 4 m cell for a non-swimmer; inv_geyser_tub is a 0.1.0 bar (test_table.md:76) and sc_geyser_tub is not run
  - its check: a live state read of the soaker's drawn alpha shows the pawn at about half strength at 4 m; the soak job refuses a cell over a non-swimmer's head
  - files: `src/RimMandrake/FlowWorks/northstar/concept_scenes.py`
- `RIMMANDRAKE_PROVE_FLOWWORKS_SHEET_DROWNS_CROPS_LIVE` (proposed): FlowWorks 0.1.0 inv_overflow_sheet in game: crops in the overspill sheet die and each fluid soaks and dries at its def's rate on a live map (cycle-4 SHEET_GAME_SIDE_NOT_KERNEL)
  - sweep reading: no commit cites the item; evidence file flowworks_visit2/sheet_crops.json absent; visit_4 SUMMARY.md:77 leaves SHEET_GAME_SIDE_NOT_KERNEL unchanged and visits 5-7 never settle it; inv_overflow_sheet is a 0.1.0 bar (test_table.md:24)
  - its check: CROPS_IRRIGATE_THEN_DROWN PASS (crops in the sheet die; dry crops live) and each fluid's soak/drying row PASS on a live map
  - files: `src/RimMandrake/FlowWorks/northstar/sheet_overflow_proof.py`, `src/RimMandrake/FlowWorks/Source/Sheet/RM_MapComponent_Sheet.cs`
- `RIMMANDRAKE_PROVE_FLOWWORKS_BOTTLE_JOBS_MOVE_EXACT_LITRES` (proposed): FlowWorks 0.1.0 inv_bottles_thirst in game: a bottle fill takes exactly its litres from the source and emptying gives them back (cycle-4 THIRST_GAME_SIDE_NOT_KERNEL)
  - sweep reading: 0.1.0 bar inv_bottles_thirst: cycle-4 lane-1 row THIRST_GAME_SIDE_NOT_KERNEL UNSETTLED; only a live thirst_live.py row can show fill/empty move exact litres
  - its check: python.exe src\RimMandrake\FlowWorks\northstar\thirst_live.py (fill/empty delta row)
  - files: `src/RimMandrake/FlowWorks/northstar/thirst_live.py`, `src/RimMandrake/FlowWorks/Source/LiquidTypes/JobDriver_FillBottle.cs`, `src/RimMandrake/FlowWorks/Source/LiquidTypes/JobDriver_FillBottleFromTank.cs`, `src/RimMandrake/FlowWorks/Source/LiquidTypes/JobDriver_EmptyBottleIntoTank.cs`
- `WRECKED_LINKS_FIX_RUINS_SNUB_THEIR_PIPES` (ready): Every wrecked tier draws in pipes and conduit like its repaired tiers (RM_PumpingStation_Wrecked first)
  - sweep reading: Owner quote 2026-11-06; code landed b69a9aa0f1 (RM_LiquidJoins.cs, RM_IndustrialLiquidWorks.xml), selftest_wrecked_links_draw_in.py GREEN 2026-11-17; both acceptance clauses are L2 live net readings, still owed; mod ledger open problem
  - its check: live: a pipe and a conduit end beside each tagged ruin link/hook in as at its repaired tier; no net role or power gained
  - files: `src/RimMandrake/FlowWorks/Source/RM_LiquidJoins.cs`, `src/RimMandrake/FlowWorks/Defs/Machinery/RM_IndustrialLiquidWorks.xml`, `src/RimMandrake/FlowWorks/selftest_wrecked_links_draw_in.py`

## his words (as recorded on the merged tickets)

- on `RIMMANDRAKE_PROVE_FLOWWORKS_RAILINGS_HOLD_AGAINST_BLAST_THROWS`: NOTE: should check with explosive knockback to see if the railings on the bridge do indeed prevent you from getting blown over them: that's their entire reason for existence other than look.
- on `WRECKED_LINKS_FIX_RUINS_SNUB_THEIR_PIPES`: I can see in the current test that the very broken version of the wrecked pump does not count to pull in the piping underneath it like the more repaired versions do. For wrecked machines, they should ALL draw in the piping and conduit the same way, not only at a certain value of fixedness. Otherwise it produces gaps between pipes, conduit, and the unit that are not representative.

## verify

Acceptance test: none as one command, live only: nine rows on the next in-game visit (each merged ticket above names its check).

## criteria

- Each merged ticket above is fixed with its check passing (red first where it is a fix), or dropped with its evidence.
- No locked 0.1.0 bar is loosened or edited by this work.

## refs

item: RIMMANDRAKE_PROVE_FLOWWORKS_RAILINGS_HOLD_AGAINST_BLAST_THROWS
item: UNDERPASS_REACH_VERIFY_WALK_UNDER_FOR_REAL
item: JAWA_DROWNING_PROVE_RAT_SIZED_IN_SHALLOWS
item: PROOFDROWN_FIX_NATURAL_WATER_READS_ZERO
item: RIMMANDRAKE_PROVE_FLOWWORKS_DRILL_SURVEY_ROLLS_PER_BIOME_LIVE
item: RIMMANDRAKE_SHOW_SOAKER_IN_DEEP_POOL_FURR_VANISHED
item: RIMMANDRAKE_PROVE_FLOWWORKS_SHEET_DROWNS_CROPS_LIVE
item: RIMMANDRAKE_PROVE_FLOWWORKS_BOTTLE_JOBS_MOVE_EXACT_LITRES
item: WRECKED_LINKS_FIX_RUINS_SNUB_THEIR_PIPES
