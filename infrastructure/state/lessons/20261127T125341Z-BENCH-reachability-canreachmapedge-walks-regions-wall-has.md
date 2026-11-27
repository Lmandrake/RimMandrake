Reachability.CanReachMapEdge walks regions, and a wall has no region, so no TraverseMode (PassAllDestroyableThings included) ever reads a walled-in cell as able to dig out. A bridge read that offers a digging mode answers 'cannot get out' for every walled cell: refuse that mode instead (jawa/reach_edge, measured on Steve1 J20261127T122224Z-2e3f85).
item: RIMMANDRAKE_SCRIPT_WRECKED_MACHINES_SCENES_EVERY_REPAIR_A_FOIL
home: skills/rimbridge-companion/references/traps.md
