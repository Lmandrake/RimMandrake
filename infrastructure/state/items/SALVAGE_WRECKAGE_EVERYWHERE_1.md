# SALVAGE_WRECKAGE_EVERYWHERE_1

Authority: `design/RimMandrake/salvage_wreckage_everywhere_design_2026-10-02.md` (§7 build plan, §8 owner rulings).
Walk: `design/validation_walks/RimMandrake/Wreckage.md`.

State at 2026-10-07 (later): engine (`src/RimMandrake/Wreckage`) slices 1-3, step 5 (wreck fall), and
steps 3-4 built offline; nothing new has run in game.

Built offline, never loaded:
- Step 3: Nightside Ice + Lantern Deeps (Riddled; `RM_NightsideWreck{Hull,Tank}`, `RM_NightsideExpeditionRig`, Frozen,
  shared by both fields); sea floors Grey (`RM_GreyFloorWreck{Hull,Spine}`, Crystal-jacketed), Twilight (`RM_PickedWreck`,
  Picked + new `noLoot`), Scald floor (`RM_ScaldFloorWreckHull`, Scald hull art). Floor fields are in BOTH
  `RM_SeabedGenerator_*` and `RM_SeaDiveGenerator_*`. Floor children set Light: `RM_SeaFloorGround` has no Walkable.
- Step 4: `RM_WreckSurface` building tag on `RM_WreckFamilyBase`; `MapComponent_WreckLichen` seeds beside it.
  Warscar `RM_WarscarWreck{Hull,Frame}` (Stripped), Wasteland `RM_WastelandWreck{Hull,Tank}` (Irradiated).
- Step 6: Blue Desert, Miasma, Flooded Canyon, Fever Wood (by patch), Rot (Light), Abyss, Stillsand, Contagion,
  17 children incl. the first Speeder/Carapace/Tread. Deep Desert has no owned BiomeDef, so no field.
- Step 7 (offline half): `validation.py` refuses a wreck field on any Cleaned biome; Long Shade's crawler road
  reading the family list is not built.
- Step 8: 54 art jobs queued (`design/RimMandrake/wreck_children_artlist{,_step6}_2026-10-07.json`), install_to set.
- Weathering rows Stripped, Irradiated, Sand-scoured, Sealed, Ice-locked, Eroded, Brined, Flood-buried, Overgrown,
  Digested, Storm-torn.
- Step 5 (`RM_WreckFall`, baseChance 0, debug-fire only; list is vanilla ShipChunk stand-ins).
All new children inherit vanilla ShipChunk art as a placeholder (Scald floor excepted) until own renders land.

Open:
- Owed sittings: Cauldron nightward edge, Propane Lake (The Chill) and Terminator Sea floors; Wasteland warcasket
  sarcophagus + radiation on deconstruct; Grey crystal jacket (mineable) + shard table; Blue Desert ice jacket.
- Pending sittings for step 6: Pyrelands, Gelatinous Slime, Webwork, Weeping Stones (repair set-pieces); Forge cache
  loot (RUT_FoundrySalvageCache, Forge-warm row). Art: install the 54 renders when done (swap texPath, re-measure
  shadow). Step 9: canon hulls, Star Wars loot rows, Fall Line Imperial register (RSW/RUT).
- Live: L1/L2 passes (a floor map holds wrecks; lichen beside a Warscar wreck by state read).
Follow-ups: Cracked Lands recede -> read a list via `RM_WreckFall.Drop`; Fall Line `RUT_FallArrival` onto this worker.
