# STILLSAND_SKELETONS_TRACKS_1 — huge skeletons on the sand, and the tracks the sand remembers

From `STILLSAND_BEDAZZLE_SITTING_1` (closed 2026-09-30). Design source:
`design/Jawa/worldbuilding/biomes/stillsand_turn3_development_2026-09-30.md` §3.1–3.3, with the
turn-4 rulings in `stillsand_bedazzle_cast_2026-09-30.md` §0. Owner, typed: *"This is THE poster
biome of the old tattoine. Huge skeletons on the sand. Barren tracks of apparent nothingness."*

## spec

1. **Giant skeleton buildings**, one per giant: multi-cell, `staticSunShadowHeight` per piece,
   deconstruct (slowly) for giant bone (one material waiting on `DESIGN_MATERIALS_REVIEW_1`; do not
   add a bone family). RM: oommok, muurrok, guzzka, vozzik. RSW: krayt, greater krayt, war wyrm. A
   krayt skeleton yields the skull (`ProcessKraytDragonSkull` exists) and sometimes a pearl.
   Build on the shipped `RM_TitanicCreatures` footprint plumbing. Art: cast bible §6.
2. **Shelter, striped:** ribs give lee stripes (partial cover about 0.5, glare-floored on sand);
   the skull is a cast-shade pocket that fully counts. A bone field can carry a tower ollim, kneel
   ollims and loomma tenants.
3. **Bone harps:** a wind sustainer on each skeleton, louder in the gale, so a skeleton can be found
   by ear (rides the sound bed in `STILLSAND_SAND_SWIM_KIT_1`).
4. **Placement:** a Stillsand genstep, **zero to two per map**, sparse, often with an ollim, partly
   under drift. The dunes engine buries and strips them.
5. **Your kills become the map's history:** a `ThingComp` on giant races' corpses converts the
   desiccated corpse into its skeleton building after about a season (nothing rots here).
6. **The krayt graveyard:** the unplaced `RSW_KraytGraveyard` mutator is upgraded from loose skulls
   to one real krayt skeleton plus scatter, and its `biomeWhitelist` (vanilla `ExtremeDesert`) adds
   `RM_Stillsand`.
7. **Tracks:** long-lived filths in this biome: footprints kept for days, crawler treads (RSW
   flavour), `RM_Filth_SandWake` (from the swim kit), drag marks, oommok prints (house-sized pits in
   a slow line), eruption scars, glasscrust scars that last years. **The dunes engine is the eraser**:
   a cell whose sand depth changes past a threshold clears its track filth (a small hook in the
   engine's deposit step, shared with the gale).
8. **Nothing hides, including you:** raids, caravans and wandering giants entering a Stillsand map
   are announced hours early by a dust plume on the edge and a letter with the bearing.
9. **Mod Settings:** toggle skeleton placement, corpse-to-skeleton, track persistence and horizon
   warnings; slider for skeletons per map.

## criteria

- A Stillsand quicktest map carries 0–2 skeletons; the skull's interior registers as full shade.
- A dev-killed oommok becomes its skeleton after the configured delay (state read).
- A wake filth on moving sand clears; one on still sand stays.
- A raid on a Stillsand map raises the horizon letter before arrival.
