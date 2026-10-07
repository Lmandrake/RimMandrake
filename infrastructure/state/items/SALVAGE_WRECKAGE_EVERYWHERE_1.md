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
- Weathering rows Stripped, Irradiated, Sand-scoured, Sealed, Ice-locked, Eroded.
- Step 5 (`RM_WreckFall`, baseChance 0, debug-fire only; list is vanilla ShipChunk stand-ins).
All new children inherit vanilla ShipChunk art as a placeholder (Scald floor excepted) until own renders land.

Open:
- Owed sittings: Cauldron nightward edge, Propane Lake (The Chill) and Terminator Sea floors; Wasteland warcasket
  sarcophagus + radiation on deconstruct; Grey crystal jacket (mineable) + shard table; Blue Desert ice jacket.
- Steps 6-9: Moderate/Low/Eroded land biomes (Brined/Overgrown/Digested/Storm-torn/Forge-warm rows with them),
  Cleaned confirmation, art waves, RSW/RUT layers. Speeder/Carapace/Tread families still have no children.
- Live: L1/L2 passes (a floor map holds wrecks; lichen beside a Warscar wreck by state read).
Follow-ups: Cracked Lands recede -> read a list via `RM_WreckFall.Drop`; Fall Line `RUT_FallArrival` onto this worker.
