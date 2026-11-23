## spec

Design Version: FlowWorks 0.1.0 (current, a Problem against the locked bars). Filed by the FlowWorks ticket sweep of 2026-11-22
(RIMMANDRAKE_SWEEP_FLOWWORKS_TICKETS_MERGE_TO_MODERN_BUILD_THE_VALUABLE), which merged these older tickets into this one, one
cause or one file group. Each old ticket's prose is in `infrastructure/state/items/closed/<ID>.md` and its history in
`rimflow show <ID>`; read the one you work on to its end before you build.

FlowWorks rivers and placers: eight old tickets (swept pawn stuck mid-river, river colours, weir catch and look, panning, placer refill, sluice box wash and its sideways art).

## merged tickets

- `RIMMANDRAKE_RESUME_SWEPT_PAWN_STUCK_MID_RIVER` (proposed): A pawn shoved by the river current never resumes walking its job
  - sweep reading: Still present: RM_MapComponent_RiverCurrent.cs:576-578 StopDead + Notify_Teleported(false) without ending or restarting the job (file unchanged since 669564da55, 2026-10-26); breaks design §3.1 'dragged and re-path, repeatedly'; live 2026-11-12 Fuego ordered west went 58 cells south and froze until drafted; inv_rivers is a 0.1.0 bar
  - its check: live: a colonist ordered across a river is shoved and re-paths; an edge-lane pawn wades out; no pawn stands frozen in its job after the carry ends
  - files: `src/RimMandrake/FlowWorks/Source/Rivers/RM_MapComponent_RiverCurrent.cs`
- `RIVER_COLORS_WIDEN_RED_BLUE_GREEN_DEATH` (proposed): FlowWorks river colours: any colour per tile, plus the source ramp red (mountains) -> bluish -> quick fade to thick green -> dies; realizable as per-tile steps
  - sweep reading: Owner card 2026-10-24; mod ledger v0.1.0 open problem (state.md:113); not built: RM_RiverColors.cs still a biome switch, no ramp/override (last real change c435ca7a7a)
  - its check: per-tile colour override plus a red->bluish->thick green->fade ramp keyed by steps from each river head, toggle in River colours settings; offline render along a real river at three zooms, then the owner look
  - files: `src/RimMandrake/FlowWorks/Source/RiverColors/RM_RiverColors.cs`
- `WEIR_CATCH_FIX_NO_FREE_FISH` (built): Weirs must not generate fish; they only capture whatever floats downstream
  - sweep reading: built ecea5beaa7 (L0); A3 ProofWeirCapture (created=0, units conserved) never run live; testq runs on 2026-11-05 read 'partial'; weir is in 0.1.0 bar inv_rivers (PY_WEIR_INSTALLED, sc_river) and sc_river is 'not run (offline only)' (test_table.md:183)
  - its check: ProofWeirCapture on a live river: lifted=1 onDry=True created=0 unitsAfter=unitsBefore
  - files: `src/RimMandrake/FlowWorks/Source/Rivers/RM_Weir.cs`, `src/RimMandrake/FlowWorks/northstar/river_scenes_walk.py`
- `WEIR_LOOK_REDESIGN_WHITEWATER_FROZEN_SOLID` (built): Complete weir review: static white water that matches nothing (must be an animated effect), a single flat blue tint above it, unclear how it works (Steam screenshots 20261023064608_1.jpg, 20261023064706_1.jpg)
  - sweep reading: his weir complaint 2026-10-23; redesign built offline (ecea5beaa7, L0: flat tint gone, foam only on the spill cell) but never seen live; weir sits in 0.1.0 bar inv_rivers (PY_WEIR_INSTALLED, sc_river); open question: refuse a weir laid along the current
  - its check: sc_river capture: white water animates on the downstream cell only, no tint upstream; then his walk reads it
  - files: `src/RimMandrake/FlowWorks/Source/RM_PlaceWorker_RiverWeir.cs`
- `GOLD_PANNING_PROVE_THE_COLONIST_STAYS` (built): Split from FLOWWORKS_QUARRY_DIGGING_1 (owner 2026-10-31, split so each can be checked and debugged alone). Gold panning (RM_PanningSpot + RM_PanForPlacerJob, Mining skill). Check alone: chain placer component panning_draws_stock (A2, passed 2026-10-15) plus A4: a colonist with Mining takes the pan job and stays on the bank cell for the session (never read; needs a live job-driver check).
  - sweep reading: Built b6932d7995c3; A2 passed 2026-10-15 but A4 (miner takes RM_PanForPlacerJob and stays on the bank for the session) was never read live; latest testq run 2026-11-22 partial; inv_quarry is a 0.1.0 bar (bars.md:83) whose row (T_QUARRY, sc_dig_finds) does not name panning
  - its check: placer chain row panning_job_colonist_stays PASSes live (with --drivers so a river site is staged)
  - files: `src/RimMandrake/FlowWorks/Source/Quarry/RM_PlacerMath.cs`
- `PLACER_STOCK_PROVE_FLOOD_REFILL` (proposed): Split from FLOWWORKS_QUARRY_DIGGING_1 (owner 2026-10-31, split so each can be checked and debugged alone). Shared per-map placer stock behind sluice and panning (A3): drain then refill via RM_PlacerProof leaves stock equal to cap. Check alone: chain placer component flood_refill (UNMEASURED: no flood edge staged; placerFloodRefill setting is in validation.RIVER_TOGGLES_OWED). Never read.
  - sweep reading: Still unmeasured: extensions_rivers.py:659 '_owed(t, "flood_refill", ...no flood edge staged; the forced refill ignores the setting)'; placerFloodRefill is a shipped toggle whose OFF case is unproven (a promise nobody would notice broken); inv_quarry is a 0.1.0 bar
  - its check: live pair: placerFloodRefill ON, drain, real flood edge -> stock at cap and Refills+1; OFF -> stock stays 0, Refills unchanged; the _owed stub is replaced and placerFloodRefill leaves RIVER_TOGGLES_OWED
  - files: `src/RimMandrake/FlowWorks/northstar/extensions_rivers.py`, `src/RimMandrake/FlowWorks/Source/Quarry/RM_PlacerWorks.cs`, `src/RimMandrake/FlowWorks/validation.py`
- `SLUICE_BOX_PROVE_THE_DAILY_WASH` (built): Split from FLOWWORKS_QUARRY_DIGGING_1 (owner 2026-10-31, split so each can be checked and debugged alone). Sluice box (RM_SluiceBox, daily wash from the placer stock). Check alone: chain placer component sluice_washes_pool_from_stock in northstar/extensions_rivers.py plus RM_PlacerProof selfcheck (A1+A2). PASSED L2 at 695812d5ec 2026-10-15; no open findings; only needs a re-run on current head to close.
  - sweep reading: Built b5fce31a7a01 (2026-11-07); its A2 live row never got a verdict: three testq runs quarantined in the Steve SIMD fault window (2026-11-10), none after; last PASS of the row was before the rebuild (2026-10-15, 695812d5ec); inv_quarry is a 0.1.0 bar
  - its check: on a FlowWorks river site at current head, modcheck placer row sluice_washes_pool_from_stock reads PASS (stock falls by exactly what lands)
  - files: `src/RimMandrake/FlowWorks/northstar/extensions_rivers.py`, `src/RimMandrake/FlowWorks/Source/Quarry/RM_PlacerWorks.cs`
- `GRAVSHIP_SPUN_ART_REDRAW_LYING_SIDEWAYS` (proposed): 10 rotatable non-square buildings draw one side-on picture (Graphic_Single), so on a turned gravship (or any east/west placement) the sprite is spun and lies on its side: RM_AttarStill, RM_DeepfirePress, RM_HospiceCradle, RM_LensBench, RM_SluiceBox, RM_SummGreatBone (gravship bait, side-on skeleton), RM_WringingStill, RUT_AncientWargamingTable, RUT_RuinedHospitalBed, kotor_PlasmaFurnace. Draw _south/_east/_north and switch to Graphic_Multi. Done when gravship_rotation_audit.py --check shows none as PICTURE_SPIN.
  - sweep reading: RM_SluiceBox (FlowWorks Defs/Rivers/RM_PlacerWorks.xml) is still Graphic_Single, rotatable, size (1,2): lies on its side on any east/west placement; other 9 defs are other mods
  - its check: python3 src/RimMandrake/Utils/gravship_rotation_audit.py --check
  - files: `src/RimMandrake/FlowWorks/Defs/Rivers/RM_PlacerWorks.xml`, `src/RimMandrake/FlowWorks/Textures/Things/Building/FlowWorks/Rivers`

## his words (as recorded on the merged tickets)

- on `RIVER_COLORS_WIDEN_RED_BLUE_GREEN_DEATH`: FlowWorks is supposed to allow world rivers to be in any color as well. We have need for that in some places.
- on `WEIR_LOOK_REDESIGN_WHITEWATER_FROZEN_SOLID`: "Static white water that doesn't match anything. (needs to be an animated effect). A single blue tint above it. How does this even work? I think we need a weir review, completely." (owner, 2026-10-23)
- on `GOLD_PANNING_PROVE_THE_COLONIST_STAYS`: panning for gold in a river

## verify

Acceptance test: none as one command, mostly live rows on a river site (each merged ticket above names its check); the sideways sluice box has an offline audit.

## criteria

- Each merged ticket above is fixed with its check passing (red first where it is a fix), or dropped with its evidence.
- No locked 0.1.0 bar is loosened or edited by this work.

## refs

item: RIMMANDRAKE_RESUME_SWEPT_PAWN_STUCK_MID_RIVER
item: RIVER_COLORS_WIDEN_RED_BLUE_GREEN_DEATH
item: WEIR_CATCH_FIX_NO_FREE_FISH
item: WEIR_LOOK_REDESIGN_WHITEWATER_FROZEN_SOLID
item: GOLD_PANNING_PROVE_THE_COLONIST_STAYS
item: PLACER_STOCK_PROVE_FLOOD_REFILL
item: SLUICE_BOX_PROVE_THE_DAILY_WASH
item: GRAVSHIP_SPUN_ART_REDRAW_LYING_SIDEWAYS
