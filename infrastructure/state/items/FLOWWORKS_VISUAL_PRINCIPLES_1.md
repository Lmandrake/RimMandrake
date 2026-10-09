# FLOWWORKS_VISUAL_PRINCIPLES_1 — the owner's five visual rules for pits and liquids

Owner, 2026-10-05 (verbatim): *"Principle 1: The canals, when dug deep enough to hold a man, should have the
same perspective appearance as the walls do when viewed from above (tall enough to stop a man). The deeper
canals should be even more extended in appearance. 2: the walls should look like either dirt or stone,
depending on the terrain beside them. 3: When filled with water it should move and act like water (ripples,
V waves, etc.) not just be solid coloration. 4) Tar should not simply be solid black, because that just looks
like the burned surface after a fire. It should look like black liquid. 5) The burned pit must look like an
empty pit that is scorched, not just a black surface or a normal pit."*

## spec

Drawing only — no flow, fire or pit mechanic changes. Every feature has a Mod Setting; off = the flat look.

1. **Depth perspective** — `RM_WallFaceMath.NorthByDrop` D1 0.10 / D2 0.18 / D3 0.30 / D4 0.50 cells,
   side faces 0.04/0.07/0.12/0.18; lit face + dark rim + contact shadow (`SectionLayer_RMExcavationWalls`).
   Near-lip occluder `RM_PitLipOcclusion` hides the part of a sunk pawn below the near bank.
2. **Material** — `RM_FaceMaterial`: the face is the neighbour ground's own terrain material; stone when a
   natural-rock ThingDef names that terrain (or a rock building stands beside), else dirt; strata vs joints.
3. **Water** — `RM_LiquidSurface`: animated two-layer ripple overlay + V-wake flecks.
4. **Tar & others** — per-liquid `surfaceLook` DATA: `LiquidDef.surfaceLook` from
   `Tools/generate_liquid_suite.py` `SURFACE_LOOKS`; `FluidDef.surfaceLook` for oil/poison.
5. **Burned pit** — `RM_PitScorch` (postfix on `RM_LiquidFire.Extinguish(spent)`): ash floor, sooted faces,
   scorch ring; same faces/depth as an unburned pit.

## assumptions (PROVISIONAL, chosen so as not to stall — owner judges on the sheet/map)

- A1 D3 face = vanilla wall face height (MEASURED ~0.25 cell from Wall_Atlas_Smooth/Rock_Atlas), D4 taller.
- A2 Pawn sink unchanged (0.3/level); the near lip hides 85% of a sunk pawn's sides, but a 1-cell window (PROVISIONAL, Mod Setting) is cut through the cover at the occupant at every depth so it stays visible (owner ruling 2026-10-09, `FLOWWORKS_PIT_OCCUPANT_LIP_CUT_1`).
- A3 Face material = ground beside the face, not the rock under the soil.
- A4 No flow direction in the ripples (the canal engine keeps no per-cell flow vector).
- A5 Scorch persists until refilled/filled in, else fades over 20 days (x3 in rain, unroofed); 0 = never.

## verify

- Offline: mockups + review sheet `src/RimMandrake/FlowWorks/art_source/visual_principles_2026-10-05/`
  (before/after; decisions file `visual_principles_decisions.json`, prefill only until he rules).
- Live: the review map (built by the map agent) from `src/RimMandrake/FlowWorks/review_map_stations_visuals.json`;
  state-read rows for the extensions suite are listed in `Transient/belt_fwvisuals_20261005.md` "NEW ROWS NEEDED".
- Owed: deploy the DLL and look; a live capture of all five rules has not happened.
