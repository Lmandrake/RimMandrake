# RIMMANDRAKE_REFUSE_HIDDEN_FACE_PAINT_ORDER_OUTLIVED_ITS_WALL — a paint order whose wall is gone paints the far side

## the defect

Graffiti's rule (record.json `inv_mark_on_wall`, tree.json `sits_on_wall`): the far side of a wall takes no paint. The coverage
judge (rm-coverage-judge-1794734941, gap 18, `design/concepts/Graffiti/park_summary.md`) found no live control for it.

Read 2026-11-15 (by code, not live): every **picker** refuses a south-only cell: `GraffitiJobUtility.HasCardinalWall` tests
north, east and west only, and `OnFace` needs `FaceFront` (side 0). The **designated order** path does not re-check at the brush:

- `Designator_PaintGraffitiMark.cs:58` checks `HasCardinalWall` when the order is placed;
- `WorkGiver_PaintGraffitiDesignated.HasJobOnCell` checks only that the designation exists;
- `JobDriver_PaintGraffiti.ChooseMark` (line 136) refuses only `NoWall`;
- `Filth_Mark.MakeMark` and `GraffitiPool.WeightedPick` (line 163) refuse only edge-on faces.

So an order placed on a cell with a wall to its north, whose north wall is then deconstructed or destroyed while a wall stands
to its south, is painted on `FaceHidden` (side 2), which `WallPlane` draws only as a cap-edge scrap.

## spec

At the brush (`ChooseMark`, or `MakeMark` for every caller), refuse a cell whose `ReadWallSide` is not
`RM_GraffitiKernel.SidePaintable`, spending the order as the `NoWall` branch does, with the same trace line.

## verify

- **Offline: none**, the defect is in a Verse job driver no offline harness loads; the kernel half
  (`SidePaintable(2) == false`) is already in `Source/SelfTest/GraffitiFuzz.cs:358`.
- **Live (UNRUN, built with the fix per the owner's 2026-11-13 rule):** on a quicktest map, a 1x3 wall row north of a floor cell
  `c` and a wall row south of it; designate `c` (RM_PaintGraffitiHere); despawn the north wall cell; let one Artistic colonist
  take the job; read `Filth_Mark.ProbeWallFaces()` (jawa/static_call). Pass: `sides=…,s=0`, no Filth_Mark at `c`, the order
  spent. On base it reads `s=1`. Add it as a row of `src/RimMandrake/Graffiti/graffiti_v1_live_proof.py` and the concept's
  `sc_wall_closeup` control.
