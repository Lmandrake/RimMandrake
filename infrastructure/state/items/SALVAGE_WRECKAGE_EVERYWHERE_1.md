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

Wave 2 (2026-10-07, built offline, never loaded; 9c63abbb5 2d8bcc7c9 0b118fbb5 938558741 aebff1aac):
- Art: 41 renders installed through the art ledger; 24 children carry own texPath + measured shadow.
- Engine: weathering `extraLoot`, `salvageHediff`, `jacket`; child `extraTierShift`; "Wreck hazards" setting.
- Grey floor wrecks ringed in RM_BrineJacket + RM_SalvageLoot_GreyShards; Blue Desert in RM_BlueIceMineable.
- Wasteland: Irradiated doses ToxicBuildup 0.12 x (1-ToxicResistance); RM_WastelandWarcasketSarcophagus (Sealed).
- Long Shade road lays from RM_WreckList_CrawlerRoad (cart + RM_LongShadeWreckSpeeder; RSW adds skiff/tread rows).
- Forge: RUT_FoundrySalvageCache is a Carapace child, RUT_WreckWeathering_ForgeWarm + RUT_SalvageLoot_Foundry.
  Still DEPLOY_HOLD with the F4 tower chain (its art exists; lift with a load round).
- Step 9: RSW_FreshTIEPanelWreck / RSW_FreshLandspeederWreck; Star Wars droid parts patched onto the four rare
  tables; RUT_FallLineWreck{Hull,Carapace}, RUT_WreckWeathering_FallLine (+ RUT_SalvageLoot_Imperial),
  RUT_WreckList_FallLine, RUT_FallLineWreckFall (baseChance 0, debug-fire).

Open:
- Art: install when the daemon finishes: 10 requeued step 3-6 jobs (3 children still on the ShipChunk
  placeholder: RM_ContagionWreckFragment, RM_FeverWoodWreckCarapace, RM_StillsandWreckTread) and 12 wave-2 jobs
  (`design/RimMandrake/wreck_children_artlist_wave2_2026-10-07.json`). `artpipe_state.py collect <job> --to
  <install_to>`, then texPath + shadow (Scald ratio).
- Owed sittings: Cauldron nightward edge, Propane Lake (The Chill) and Terminator Sea floors; step 6 Pyrelands,
  Gelatinous Slime, Webwork, Weeping Stones (repair set-pieces).
- Not built: Fresh "live power on 1 in 10"; Fever Wood Overgrown vine blocker; Fall Line incident firing on Fall
  Line tiles.
- Live: L1/L2 passes (a floor map holds wrecks; jacket ring present; lichen beside a Warscar wreck by state read;
  a careful strip of a Wasteland wreck adds ToxicBuildup; the Long Shade road lays list rows).
Follow-ups: Cracked Lands recede -> read a list via `RM_WreckFall.Drop`; Fall Line `RUT_FallArrival` onto this worker.
