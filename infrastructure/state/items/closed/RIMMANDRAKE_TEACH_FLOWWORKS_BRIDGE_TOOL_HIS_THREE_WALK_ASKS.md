## spec

Design Version: FlowWorks 0.1.0 (current, a Problem against the locked bars). Filed by the FlowWorks ticket sweep of 2026-11-22
(RIMMANDRAKE_SWEEP_FLOWWORKS_TICKETS_MERGE_TO_MODERN_BUILD_THE_VALUABLE), which merged these older tickets into this one, one
cause or one file group. Each old ticket's prose is in `infrastructure/state/items/closed/<ID>.md` and its history in
`rimflow show <ID>`; read the one you work on to its end before you build.

FlowWorks suspension bridge tool: his three asks from the 2026-11-20 walk (Choose style on built bridges, span over ruined bridge scrap, say the drag starts on the landing).

## merged tickets

- `RIMMANDRAKE_ADD_FLOWWORKS_CHOOSE_STYLE_TO_BUILT_BRIDGES` (proposed): Suspension bridges carry four looks but a built bridge has no Choose style button: the bridge defs carry only CompProperties_Styleable (Defs/Pits/ThingDefs/RM_SuspensionBridges.xml), no CompProperties_PipeLook or TankLook. The build button's look menu exists in code (StylePickerCore.ProcessInputPostfix via Designator_Build.ProcessInput; decks registered in RM_SuspensionPatches.cs:978-990) but he did not find it. Acceptance test: live, a built steel suspension deck lists a Choose style gizmo whose pick restyles every part of that bridge; red today by the defs (not yet watched red: the game is offline to this run)
  - sweep reading: owner walk 2026-11-20 part 2 #22; RM_SuspensionBridges.xml carries CompProperties_Styleable only, no PipeLook/TankLook comp, so no Choose style gizmo [measured in item]
  - its check: a built bridge lists Choose style and its pick restyles every part (deck, anchors, railings, towers); the build button opens its look menu
  - files: `src/RimMandrake/FlowWorks/Defs/Pits/ThingDefs/RM_SuspensionBridges.xml`, `src/RimMandrake/FlowWorks/Source/Pits/Suspension/RM_SuspensionPatches.cs`, `src/RimMandrake/FlowWorks/Source/Machinery/PipeLook.cs`
- `RIMMANDRAKE_LET_FLOWWORKS_BRIDGE_SPAN_OVER_RUINED_BRIDGE_SCRAP` (proposed): A suspension bridge will not place over a pit that holds the scrap of a ruined bridge: RM_SuspensionWreck is an impassable Building on the pit floor (Defs/Pits/ThingDefs/RM_SuspensionBridges.xml:700-708) and the drag planner never mentions wrecks, so blueprint placement refuses the square. Acceptance test: live, a bridge dragged over a pit holding RM_SuspensionWreck is placed (the wreck stays under the deck or is cleared); red predicted, not yet watched
  - sweep reading: walk 2026-11-20 part 2 #25; RM_SuspensionWreck is an impassable Building (Defs/Pits/ThingDefs/RM_SuspensionBridges.xml:700-708) and Pits/Suspension/Designator_SuspensionBridge.cs has no 'wreck' mention, so placement still refuses
  - its check: a new bridge drag over a 4 m pit holding RM_SuspensionWreck places (wreck stays under the deck or is cleared with a readable sign)
  - files: `src/RimMandrake/FlowWorks/Source/Pits/Suspension/Designator_SuspensionBridge.cs`, `src/RimMandrake/FlowWorks/Source/Pits/Suspension/RM_MapComponent_SuspensionBridges.cs`, `src/RimMandrake/FlowWorks/Defs/Pits/ThingDefs/RM_SuspensionBridges.xml`
- `RIMMANDRAKE_SAY_FLOWWORKS_BRIDGE_DRAG_STARTS_ON_THE_LANDING` (proposed): The suspension bridge tool works only when the drag starts on the landing, and he was not told: the rule is in the button text (Designator_SuspensionBridge.cs:34) and in a single-click message (:56), but which refusal a drag started on the span gets is unread. Acceptance test: live, a drag started on the span shows a refusal that names starting on solid ground beside the hole (or the drag is accepted from either end); not yet watched red
  - sweep reading: his walk 2026-11-20 part 2 #24; drag refusals in RM_SuspensionMath.ValidateDrag do not say start on the landing
  - its check: live: drag the steel suspension bridge from a pit square to the far bank; the message says start on solid ground beside the hole
  - files: `src/RimMandrake/FlowWorks/Source/Pits/Suspension/Designator_SuspensionBridge.cs`, `src/RimMandrake/FlowWorks/Source/RM_SuspensionMath.cs`

## his words (as recorded on the merged tickets)

- on `RIMMANDRAKE_ADD_FLOWWORKS_CHOOSE_STYLE_TO_BUILT_BRIDGES`: For the bridges, they have Styles like Industrial but no UI button to select it.
- on `RIMMANDRAKE_LET_FLOWWORKS_BRIDGE_SPAN_OVER_RUINED_BRIDGE_SCRAP`: Would not place over a pit that had the scrap of a ruined bridge in it, even though it likely still should.
- on `RIMMANDRAKE_SAY_FLOWWORKS_BRIDGE_DRAG_STARTS_ON_THE_LANDING`: "Selector tool worked to place it, but it should tell you that you start on the landing, not the span, in order to work." (walk 2026-11-20)

## verify

Acceptance test: none as one command, two of the three asks are live-only (the message a drag shows, the restyle of a built bridge); the scrap span can take an offline case.

## criteria

- Each merged ticket above is fixed with its check passing (red first where it is a fix), or dropped with its evidence.
- No locked 0.1.0 bar is loosened or edited by this work.

## refs

item: RIMMANDRAKE_ADD_FLOWWORKS_CHOOSE_STYLE_TO_BUILT_BRIDGES
item: RIMMANDRAKE_LET_FLOWWORKS_BRIDGE_SPAN_OVER_RUINED_BRIDGE_SCRAP
item: RIMMANDRAKE_SAY_FLOWWORKS_BRIDGE_DRAG_STARTS_ON_THE_LANDING
