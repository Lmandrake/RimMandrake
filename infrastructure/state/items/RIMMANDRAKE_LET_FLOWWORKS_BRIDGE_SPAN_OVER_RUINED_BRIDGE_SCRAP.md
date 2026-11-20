# RIMMANDRAKE_LET_FLOWWORKS_BRIDGE_SPAN_OVER_RUINED_BRIDGE_SCRAP

## spec

His words (walk 2026-11-20): "Would not place over a pit that had the scrap of a ruined bridge in it, even though it likely still should." Source: `design/RimMandrake/validation_holding/flowworks_walk_20261120.md` part 2 #25.
`RM_SuspensionWreck` is an impassable `Building` lying in the pit (`src/RimMandrake/FlowWorks/Defs/Pits/ThingDefs/RM_SuspensionBridges.xml:700-708`, spawned by
`RM_MapComponent_SuspensionBridges.cs:289-307`); `Designator_SuspensionBridge` never mentions a wreck, so blueprint placement refuses the
square [measured that nothing handles it; the exact refusal text unread].

## verify

Live: collapse a bridge (or spawn RM_SuspensionWreck) in a 4 m pit; drag a new bridge over it.

## criteria

Acceptance test: the new bridge is placed over the wreck (the wreck stays below the deck, or is cleared with a readable sign). Red predicted, not yet watched.
