## spec
Road back from FlowWorks 0.1.0 in-game visit 5 (`design/concepts/FlowWorks/version/in_game/visit_5/SUMMARY.md`). Takes over
`GRATE_FIRE_FIX_SOLID_DECK_BURNS_TOO` (filed 2026-10-23, BLOCKED since 2026-10-29 on "a design ruling is needed"), which
the visit's driver cited but which is not caused by any road-back item, so the Dispatch tick would never wait on it.

Check `sc_hung_bridge`, row `GRATE_fire_burns_people_above` (bar `hung_bridge_spans`): PASS needs grate riders burnt
(g >= 1) and more than the solid-deck control (g > s). Readings [measured]:
- visit 5 (build bdd56c6ff6, game a, flowworks tier): grate 5, solid 13, FAIL.
  Evidence `design/concepts/FlowWorks/version/in_game/visit_5/evidence/sc_hung_bridge_20261121T193008.json`.
- visit 3: solid 10, 6 and 8 over three runs; FAIL once, PASS twice. The verdict is a coin flip.
- 2026-10-29 live rerun: grate 5, solid 5; fuel spread ruled out (solid scene alone 3, grate alone 5).

Class MOD. The design already rules, so no owner card is needed:
`design/RimMandrake/flowworks_bridges_design_2026-10-17.md` §4.1 says that a SOLID deck over burning liquid gives the
people above a LOW chance (the onCover chance), and a GRATED deck a HIGH one (open-pit × 0.75). The item
`SUSPENSION_GRATE_BUILD_LET_THE_FIRE_UP` verify L2 says the solid scene burns "fewer".

The code that breaks it: `src/RimMandrake/FlowWorks/Source/RM_LiquidFire.cs` `ApplyInfernoEffects` (chemfuel is an
inferno):
- in-cell attach: a rider on an intact solid deck gets `RM_FuelFireMath.InfernoAttachInCell` (0.9), the same as a grated
  rider (`Max(0.9, 0.75 × 1)`). So the deck gives no protection and grated equals solid by design of the code.
- beside attach: `InfernoAttachBeside` (0.3) reaches every pawn in the 8 neighbours, deck riders included, with no deck
  read.
- halo: `FireUtility.TryStartFireIn` in the radius; check whether it lands fires on deck cells.
- Unexplained: why solid riders burn MORE than grate riders (13 vs 5). Read where each solid rider's Burn came from
  (in-cell, beside, halo, a fire on the deck) in one live run before the fix.
The ordinary `ApplyEffects` path already uses `RM_FireMath.AttachChance(held, onDeck && !held, flying, grated)`, which
keeps grated > solid; the inferno path should follow the same rule.

Stage: game-only (`--needs bridge`). The inferno code is Verse-bound; the cause of 13 vs 5 is unknown until a live read.
A pure chance function (an `InfernoAttachChance(held, onSolidDeck, grated)` in `RM_FuelFireMath`, with a selftest that
grated > solid deck and solid deck = the design's low chance) is welcome as the offline half, red on a copy of today's
rule.

## verify
- Offline: the new chance function's selftest is red on today's rule and green on the fix.
- In-game check (Stage 6 id `sc_hung_bridge`), exact command as visit 5 ran it:
  `python.exe -u src/RimMandrake/FlowWorks/northstar/suspension_bridge_proof.py <out.json>` on the flowworks tier, calm site
  verified first.
- Acceptance test: `GRATE_fire_burns_people_above` PASS on three runs in a row on the fixed build, and every other row of
  the proof as before. Red now: visit 5 FAIL (5 vs 13) on bdd56c6ff6.
- Never loosen the row (g > s stays). A change to the bar's words is his card.

## criteria
- A1 L0: the fix builds; the inferno chance selftest is red on today's rule and green on the fix (grated > solid deck).
- A2 L2: `sc_hung_bridge` row `GRATE_fire_burns_people_above` PASS on three runs in a row on the fixed build.

## refs
file: src/RimMandrake/FlowWorks/Source/RM_LiquidFire.cs
file: src/RimMandrake/FlowWorks/Source/RM_FuelFireMath.cs
file: src/RimMandrake/FlowWorks/Source/RM_FireMath.cs
file: src/RimMandrake/FlowWorks/northstar/suspension_bridge_proof.py
