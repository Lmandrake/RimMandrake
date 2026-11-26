# RIMMANDRAKE_RESTAGE_SKINFLAPS_ON_OPEN_GROUND_EIGHT_NEVER_MOVED — stage eight walking RM_Skinflap for the joint flight session

## spec
In joint run 1 (9:10 AM PST 2026-11-26, ArchSmall) eight wild `RM_Skinflap` spawned on one cell (125,125) of the
FlowWorks review map never left that cell in 2,500 ticks; their only jobs were `Wait_Wander` and
`Wait_MaintainPosture`, so no job that can start a flight began. Name the cause with evidence, stage eight birds again
on open, unroofed, walkable ground spread over several cells, show that they walk, pause, and save the scene as
`FLYER_JOINT_SESSION_SKINFLAPS_20261126`. No flight is started by us and no image of a bird is taken.

## verify
Two state reads of the birds (`jawa/pawn_flight` action `report`) a short game-time apart: at least four of the eight
changed cell, and at least one bird had a job other than `Wait_Wander` and `Wait_MaintainPosture`. The save exists in
ArchSmall's Saves folder.

## criteria
- The cause of run 1 is named with its evidence.
- Eight birds walk on open ground (the two reads above).
- The game is paused on the birds and the save is written.
- A note starting `READY TO SHOW:` (or `NOT STAGED:`) is on FLYERFRAMES_PROVE_JOINT_SESSION.

## refs
def: ThingDef/RM_Skinflap
file: src/RimMandrake/Contagion/Defs/ThingDefs_Races/RM_ContagionFauna.xml
