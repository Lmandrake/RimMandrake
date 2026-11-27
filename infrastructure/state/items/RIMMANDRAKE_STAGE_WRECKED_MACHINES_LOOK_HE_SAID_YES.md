# RIMMANDRAKE_STAGE_WRECKED_MACHINES_LOOK_HE_SAID_YES

## spec

`design/concepts/WreckedMachines/look_01.md` is the whole spec: the six stations, the grid key, the named cheats, and
what the look does not settle. His word for it is OWNER event 1795760440829904733 (2026-11-26, 10:20 PM PST): "Yes I
will look at the existing wrecked machines." The mod is as built today; nothing of the 0.1.0 design is built first.

The live mechanism never seen running: none is claimed. This is not a live check of the mod. It is a save that he
looks at, so it needs a game.

## refs

file: design/concepts/WreckedMachines/look_01.md
file: design/concepts/WreckedMachines/version/small_list.json
file: src/RimMandrake/WreckedMachines/Defs/ThingDefs_Buildings/Buildings_WreckedMachines_AutomatedSmelter.xml
file: src/RimMandrake/WreckedMachines/Defs/ThingDefs_Buildings/Buildings_WreckedMachines_Mobile.xml

## verify

Acceptance test: none, a save staged for his eyes on a live game. The stager reads back, through the bridge, that each
station's things stand at their grid cells in the saved game, and writes the save's name and the game's name
(ArchBig or ArchSmall) on this item.

## criteria

- The save loads on the mod's small list with no red error from Wrecked Machines.
- Stations A to F of `look_01.md` are present, in rows, with the grid key.
- The save is paused on load, and the save is still there until he says delete.
- He is told the save's name and which game holds it.
