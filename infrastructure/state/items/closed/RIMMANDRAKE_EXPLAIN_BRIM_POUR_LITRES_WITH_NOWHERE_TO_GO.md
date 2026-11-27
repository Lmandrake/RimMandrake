# RIMMANDRAKE_EXPLAIN_BRIM_POUR_LITRES_WITH_NOWHERE_TO_GO

An overflow pour (the dev action's PourOverflow) into a brim-full pit with open dry ground round it replied
'spilled 0 L ... 1 kL had nowhere to go (walls, other liquids or the map's cap on wet squares)' (live 2026-11-12).

## spec
A pour that overflows onto open dry ground spills there. When some of it cannot be placed, the reply names the measured
cause (the map's wet-square cap full, with its count), not a list of three possible causes.

## verify
Live: on a map with open ground round a brimmed pit, PourOverflow 1 kL replies 'spilled 1 kL of 1 kL'. Offline: the
reply-reason rule picks the cap when the wet count is at the cap.

## criteria
- OL_pour_never_no_room FAILs a reply that spilled 0 L while the map's wet count is under its cap.
- A 'nowhere to go' reply names the cause it measured.

## refs
file: src/RimMandrake/FlowWorks/Source/Debug/RM_GodLiquid.cs
file: src/RimMandrake/FlowWorks/northstar/owner_look_regressions.py
tier: flowworks_list
