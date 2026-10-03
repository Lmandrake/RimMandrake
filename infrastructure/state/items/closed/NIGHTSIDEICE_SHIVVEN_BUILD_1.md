# NIGHTSIDEICE_SHIVVEN_BUILD_1 — the shivven: heat-seeking tunnelers in the ice

Split from `NIGHTSIDEICE_HEAT_DIAL_BUILD_1` item 2. Design:
`design/Jawa/worldbuilding/biomes/nightsideice_bedazzle_review_2026-10-01.md` §1 (ruled natives) and §4 row 1.

## spec

1. `RM_Shivven` (RM tier, `mandrake.rm.nightsideice`): blind, thermal, colonial tunnelers that travel
   **inside the ice**. Body and stats are a design call at build; no art exists (commission it, slate row 8;
   "the tell graphic matters more than the body").
2. Movement is a retune of `RM_CompSandSwim` (`CreatureBehaviors`): submerged travel with the per-tick
   **rumble** sustainer as the tell, breach-to-strike and resurface. They track **heat** (the hottest
   source near the colony, read from `RM_HeatDial` and the source it measured), never footfall, and move
   only through ice terrain. Do not copy the Stillsand's voice: own sounds.
3. Mod Settings for every behaviour; first-script chain in `NightsideIce/validation.py`.

## criteria

- A submerged shivven on an ice map heads for a working heater rather than a walking pawn, with the
  rumble audible, and surfaces to strike.
- It never travels through non-ice terrain or through a floor (the hull rule).
