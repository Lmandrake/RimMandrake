# RIMMANDRAKE_ADD_FLOWWORKS_CHOOSE_STYLE_TO_BUILT_BRIDGES

## spec

His words (walk 2026-11-20): "For the bridges, they have Styles like Industrial but no UI button to select it." Source: `design/RimMandrake/validation_holding/flowworks_walk_20261120.md` part 2 #22.
The suspension bridge parts carry `CompProperties_Styleable` only (`src/RimMandrake/FlowWorks/Defs/Pits/ThingDefs/RM_SuspensionBridges.xml`, e.g. :149), no
`CompProperties_PipeLook`/`CompProperties_TankLook`, so a built bridge has no Choose style button [measured]. The build button's look
menu exists in code: `Designator_Build.ProcessInput` postfix (`src/RimMandrake/FlowWorks/Source/Machinery/PipeLook.cs:268-271`) opens
`StylePickerCore.MenuFor` for registered defs, and the decks are registered (`Source/Pits/Suspension/RM_SuspensionPatches.cs:978-990`)
[measured]; why he did not see it is unread [guess ~50% it did not open]. Same family as RIMMANDRAKE_SPREAD_FLOWWORKS_LOOK_ALONG_LINE_NOT_PIPES_ONLY.

## verify

Live: select a built steel suspension bridge; read its gizmos; pick Industrial; read every part's style. Also click the steel suspension bridge build button and read whether a look menu opens.

## criteria

Acceptance test: a built bridge lists Choose style and its pick restyles every part of that bridge (deck, anchors, railings, towers); the build button opens its look menu. Red today by the defs; not yet watched red (no game in this run).
