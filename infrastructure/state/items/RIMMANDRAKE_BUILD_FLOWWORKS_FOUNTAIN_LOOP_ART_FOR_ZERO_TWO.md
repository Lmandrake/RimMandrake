## spec

Design Version: FlowWorks 0.2.0 (next, Divergent or Polish; moves no 0.1.0 bar). Filed by the FlowWorks ticket sweep of 2026-11-22
(RIMMANDRAKE_SWEEP_FLOWWORKS_TICKETS_MERGE_TO_MODERN_BUILD_THE_VALUABLE), which merged these older tickets into this one, one
cause or one file group. Each old ticket's prose is in `infrastructure/state/items/closed/<ID>.md` and its history in
`rimflow show <ID>`; read the one you work on to its end before you build.

FlowWorks 0.2.0: the fountain that pumps its own rain, and its art pick.

## merged tickets

- `FOUNTAIN_LOOP_BUILD_PUMPS_ITS_OWN_RAIN` (proposed): FlowWorks v1: simple fountain whose water falls out and flows over the ground (overspill), caught in a surrounding ditch and pumped back — full flow-cycle proof + art piece; commission art, stage a review scene to watch it work
  - sweep reading: RM_Fountain never built (no Defs/Fountains); no 0.1.0 bar names a fountain, so a new building is Divergent
  - its check: src/RimMandrake/FlowWorks/northstar/fountain_loop_proof.py (to be written) F1-F8
  - files: `src/RimMandrake/FlowWorks/Defs/Fountains/RM_Fountain.xml`, `src/RimMandrake/FlowWorks/review_map.py`
- `FOUNTAIN_ART_FINISH_WAITS_FOR_A_FAVOURITE` (proposed): Fountain art: once a design is picked on Transient/fountain_20261023 (judge or owner), draw its DRY variant + 3 falling-water/jet overlay frames, then install with the RM_Fountain build
  - sweep reading: three v1 candidates drawn (9e6e61f529); no design picked and no RM_Fountain def exists in FlowWorks Defs; fountain is not a 0.1.0 bar
  - files: `src/RimMandrake/FlowWorks/art_source/Fountain/ship.py`

## his words (as recorded on the merged tickets)

- on `FOUNTAIN_LOOP_BUILD_PUMPS_ITS_OWN_RAIN`: Now that we're building the ability for water to flow over the ground (overspill), We can do some really neat stuff fairly cheaply! We can make fountains! ... In the meantime, we can do a small simple version in FlowWorks itself: simple fountains that allow their water to fall out and flow over the ground. The water can be captured in a surrounding ditch then pumped back to the fountain as a proof-of-principle of the entire flow cycle as well as a neat artistic piece. Please commission that as art and as a review sheet item to watch work. (owner, 2026-10-23)

## verify

Acceptance test: none as one command, 0.2.0 work: fountain_loop_proof.py is still to be written; the art pick is a judge's.

## criteria

- Each merged ticket above is fixed with its check passing (red first where it is a fix), or dropped with its evidence.
- No locked 0.1.0 bar is loosened or edited by this work.

## refs

item: FOUNTAIN_LOOP_BUILD_PUMPS_ITS_OWN_RAIN
item: FOUNTAIN_ART_FINISH_WAITS_FOR_A_FAVOURITE
