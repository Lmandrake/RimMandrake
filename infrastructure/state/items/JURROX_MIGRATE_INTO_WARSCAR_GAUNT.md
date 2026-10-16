# JURROX_MIGRATE_INTO_WARSCAR_GAUNT

Owner, art sheet 2026-10-16 (RM_Jurrox, pick A): *"Wonderfully grotesque. Add it to the Warscar and make a new name and description for it based on its ultra-gaunt appearance."*

## Done
- New creature **RM_Rakeshank** ("rakeshank": lean as a rake, all shank), free RM_ tier, one home: the Warscar.
  Def: `src/RimMandrake/Scarlands/Defs/ThingDefs_Races/RM_Rakeshank.xml` (non-predator CarnivoreAnimal carrion gleaner, body size 0.6, adult drawSize 1.1; numbers PROVISIONAL).
- Roster row `RM_Rakeshank 0.12` in `RM_Warscar.xml` (animalDensity already 1.0).
- Art: the jurrox A pick installed through the art ledger at `Scarlands/Textures/Things/Pawn/Animal/RM_Rakeshank/` (east/north/south).
- `Scarlands/validation.py` static checks cover def, row and textures.

## Left behind
- The original candidate PNGs at `TheForge/Textures/Things/Pawn/Animal/RM_Jurrox/` stay (no def uses them); retiring them is an art-ledger purge, not done here.
