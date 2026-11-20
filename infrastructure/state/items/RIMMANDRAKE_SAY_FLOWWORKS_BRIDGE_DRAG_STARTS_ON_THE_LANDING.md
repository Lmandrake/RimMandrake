# RIMMANDRAKE_SAY_FLOWWORKS_BRIDGE_DRAG_STARTS_ON_THE_LANDING

## spec

His words (walk 2026-11-20): "Selector tool worked to place it, but it should tell you that you start on the landing, not the span, in order to work." Source: `design/RimMandrake/validation_holding/flowworks_walk_20261120.md` part 2 #24.
The rule is written in the button description (`src/RimMandrake/FlowWorks/Source/Pits/Suspension/Designator_SuspensionBridge.cs:34`) and in the single-click
message (`:56`); the drag refusals come from `RM_SuspensionMath.ValidateDrag` (`Source/RM_SuspensionMath.cs:310-342`) [measured]. Which
message a drag started on the span shows is unread [unknown].

## verify

Live: drag the steel suspension bridge from a pit square to the far bank; read the message shown.

## criteria

Acceptance test: a drag started on the span either places the bridge or shows a refusal that says to start on solid ground beside the hole. Not yet watched red.
