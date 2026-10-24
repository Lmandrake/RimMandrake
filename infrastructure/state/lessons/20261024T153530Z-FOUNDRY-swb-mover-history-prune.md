A defName rename sweep (RSW_X -> RM_X) also rewrites history comments ('Moved here from ...', 'defName A -> B'), which then lie; restore them by hand after the sweep. And a def that moves between mods leaves the old file in the game's Mods copy until deploy runs with --prune, which loads as a duplicate creature.
home: skills/rimworld-deploy
