## spec

Design Version: FlowWorks 0.1.0 (current, a Problem against the locked bars). Filed by the FlowWorks ticket sweep of 2026-11-22
(RIMMANDRAKE_SWEEP_FLOWWORKS_TICKETS_MERGE_TO_MODERN_BUILD_THE_VALUABLE), which merged these older tickets into this one, one
cause or one file group. Each old ticket's prose is in `infrastructure/state/items/closed/<ID>.md` and its history in
`rimflow show <ID>`; read the one you work on to its end before you build.

FlowWorks drawbridges: carry out his 2026-11-03 rulings (one leaf only, no plank stack, see-through gate) and the four old drawbridge faults.

## merged tickets

- `DRAWBRIDGE_LEAF_PRUNE_NO_TWINS_NO_PILE` (proposed): Drawbridge build spec 2026-11-04, part 2: remove two-leaf drawbridges (SplitLeaves to one leaf; a span over the max leaf is not a drawbridge, ordinary bridges still allowed), cut the plank stack (RM_DrawbridgeArt.DrawPlanks, its art and pad; raid planks untouched), retire the no-longer-drawn LeafUp Edge/Underside art and RM_DrawbridgeCableMath.LeafEdgeBody (DRAWBRIDGE_UP_FIX_RAISED_LOOKS_LOWERED stopped drawing them).
  - sweep reading: HEAD still splits two leaves (RM_DrawbridgeMath.SplitLeaves; DrawbridgeChecks.cs:75-83 assert two-leaf spans) and still draws the plank stack (RM_DrawbridgeArt.cs:205 DrawPlanks); owner stopped the 2026-11-05 sitting because the build ignored his 11-03 rulings (plank pile, upright leaves)
  - its check: one leaf only (span over max leaf is not a drawbridge); no plank stack drawn; Edge/Underside art retired
  - files: `src/RimMandrake/FlowWorks/Source/RM_DrawbridgeMath.cs`, `src/RimMandrake/FlowWorks/Source/Pits/Drawbridge/RM_DrawbridgeArt.cs`, `src/RimMandrake/FlowWorks/Source/SelfTest/DrawbridgeChecks.cs`
- `DRAWBRIDGE_GATE_BUILD_SEE_THROUGH_DOOR` (proposed): Drawbridge build spec 2026-11-04, part 3: option B gate frame (posts + lintel, all widths); interior transparent like a doorway, not black; winch and hinge on the friendly bank; near-side lines taut from leaf tip over the lintel to the winch, far side slack or disconnected, nothing crosses the gap; rewrite design R12 and the art contract (design/RimMandrake/flowworks_drawbridge_design_2026-10-20.md lines 168-197). Ref v3 notes D:\ClaudeWork\rimmandrake\conductor\session_2026-11-03\06_DRAWBRIDGE\mockups\v3\notes.md.
  - sweep reading: owner-filed build spec 2026-11-04 part 3 (option B gate frame, see-through interior, winch/hinge on friendly bank); no commit names it; his drawbridge look waits on the 11-04 spec
  - its check: gate frame posts+lintel at all widths; interior transparent like a doorway; winch and hinge on the friendly bank
  - files: `src/RimMandrake/FlowWorks/Source/Pits/Drawbridge/RM_DrawbridgeArt.cs`
- `DRAWBRIDGE_LOWER_FIX_LIFTS_OCCUPANTS_BENEATH` (proposed): [MINOR] Lowering a drawbridge promotes occupants beneath it onto the deck
  - sweep reading: GPT-review MINOR, but ordinary play reaches it in the vision.md raid: raiders swim the moat under a raised leaf, then lowering it promotes them onto the deck (draw height, load, immersion, movement band); proposed, no fix commit
  - its check: a selftest: pawn in the moat under a raised leaf stays in the floor band after the leaf lowers
  - files: `src/RimMandrake/FlowWorks/Source/Pits/Drawbridge/RM_Drawbridges.cs`
- `DRAWBRIDGE_BUTTON_FIX_CLICK_SEEMS_DEAD` (proposed): Clicking the raise/lower button appeared to do nothing for the owner in game 2026-11-03. Code reads as an order waiting for a colonist at the winch (RM_DrawbridgeMath OrderRaise/OrderLower); not yet confirmed live. At minimum the player gets no visible feedback.
  - sweep reading: owner saw it in play 2026-11-03; TESTPILOT_SAT measured at 16eff7aa52: order is taken and waits for a colonist at the winch with almost no feedback ('the design is the defect')
  - its check: after a raise/lower click the gizmo and leaf show the pending order and who will work the winch until it is done
- `TIMBER_WINCH_FIX_POWERS_STEEL_BRIDGE` (proposed): [MINOR] A timber winch powers a steel drawbridge without electricity
  - sweep reading: breaks the ruled promise 'steel powered' (design R-rows, live row STEEL_UNPOWERED_FREEZES): movement uses the record's steel tier while power is read from the timber winch, so a steel leaf moves with no electricity; proposed, no fix commit
  - its check: a steel drawbridge does not move without power whatever winch is built; a selftest covers the timber-winch case
  - files: `src/RimMandrake/FlowWorks/Defs/Pits/ThingDefs/RM_Drawbridge.xml`

## his words (as recorded on the merged tickets)

- on `DRAWBRIDGE_LEAF_PRUNE_NO_TWINS_NO_PILE`: owner stopped the 2026-11-05 sitting: the staged build ignored his 11-03 rulings (plank pile, upright leaves)

## what blocks his in-game look (offline check of each 2026-11-03 ruling, 2026-11-23, HEAD be6f6ba0e3)

Not built, and each one is visible in the picture, so `DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS` was not staged:
1. The option B gate frame (posts and lintel as one frame, all widths 1 to 4). The gate is still one door picture per lane
   (`RM_DrawbridgeArt.DrawGate`); no frame code exists.
2. The near-side lines, taut from the leaf to the winch (his words: "The NEAR (friendly) side stays taut"). No code draws a
   line from a raised leaf. `Building_SuspensionAnchor.Print` lays BOTH banks' ropes slack when the deck square ahead is raised
   (`AnchorPrint.slack = deck.leafRaised`), so the friendly bank is slack too.
3. The far side slack or disconnected on STEEL. `RM_DrawbridgeCableMath.Art` has 0 Steel rows since b7e8e8f1cc, so
   `AnchorPrintFor` returns null and a steel drawbridge prints the suspension tower with its painted cables on both banks,
   raised or lowered. Those cables point at the open gap.
4. The steel leaf changes picture at the first tick: the lowered deck is tan planks (`RM_SuspensionDeck_Steel`), the raised
   leaf is grey plate (`RM_DrawbridgeLeafUp_Steel_Face`). The build spec asks for no pop at angle 0.

Acceptance test for 2 and 3 (write it first; it must be red on be6f6ba0e3): a Verse-free selftest that gives, for both materials,
all 4 directions, widths 1 to 4 and leaf lengths 1 to the maximum, at the hold: each near line runs from a point on the drawn tip edge
to the winch; no line piece on the far bank reaches past its own anchor square; Steel and Timber give the same answer.
Plant a fault (near line slack; a steel taut far cable) and see the selftest fail. For 1 the test is the same geometry on the frame:
two posts outside lanes 0 and width-1, one lintel, and an interior with no drawn pixel. The look itself is judged on captures.

## verify

Acceptance test (the one-leaf and no-plank-stack half, built at 5d9004b9ce by the sweep): `python3 src/RimMandrake/Utils/selftest_flowworks_stock.py --only 'Drawbridge*'`
reads 50/50. Seen red on the base source (HEAD 3efc3c7ed8 versions of RM_DrawbridgeMath.cs, RM_DrawbridgeArt.cs, RM_Drawbridges.cs): 48/50,
FAIL `Drawbridge_P1_one_leaf_on_the_colony_bank_never_two` ("5 squares of timber is longer than one leaf") and FAIL
`Drawbridge_Looks_wired_at_the_draw_sites` ("no plank stack is drawn"); evidence
`D:\ClaudeWork\rimmandrake\conductor\ticket_sweep_20261122\FlowWorks\drawbridge_red_on_base.txt`.
Live row (repaired in this run): `drawbridge_proof.py` row `LONG_SPAN_NOT_A_DRAWBRIDGE` replaces `TWO_LEAF_TIPS_OWN_HINGE` (a 6-square
timber drawbridge drag is refused with a too-long reason). Mock: `python3 src/RimMandrake/FlowWorks/northstar/selftest_drawbridge_proof.py`
passes and its planted fault `two_leaf_allowed` turns the row FAIL. Live: UNRUN; command
`python.exe src\RimMandrake\FlowWorks\northstar\drawbridge_proof.py --only LONG_SPAN_NOT_A_DRAWBRIDGE` on a FlowWorks tier game.

Still open in this ticket: the see-through gate, the lowered leaf lifting occupants, the button feedback and the timber winch on a
steel bridge (the merged tickets above, each with its own check); the plank-stack PNGs (`Textures/Things/Building/FlowWorks/Drawbridge/RM_DrawbridgePlanks_*.png`)
and `DrawbridgeArtPaths.Planks` are no longer drawn and wait for the art ledger to retire them; the Edge/Underside raised-leaf art and
`RM_DrawbridgeCableMath.LeafEdgeBody` are left as they are (not worth the touch: art and a table nothing draws, no effect in play).
A two-leaf drawbridge in an older save keeps its two leaves and works as built (no migration).

## criteria

- Each merged ticket above is fixed with its check passing (red first where it is a fix), or dropped with its evidence.
- No locked 0.1.0 bar is loosened or edited by this work.

## refs

item: DRAWBRIDGE_LEAF_PRUNE_NO_TWINS_NO_PILE
item: DRAWBRIDGE_GATE_BUILD_SEE_THROUGH_DOOR
item: DRAWBRIDGE_LOWER_FIX_LIFTS_OCCUPANTS_BENEATH
item: DRAWBRIDGE_BUTTON_FIX_CLICK_SEEMS_DEAD
item: TIMBER_WINCH_FIX_POWERS_STEEL_BRIDGE
