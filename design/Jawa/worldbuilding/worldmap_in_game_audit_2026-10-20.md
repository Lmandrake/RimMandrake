# World map, in-game audit (2026-10-20)

Done after the owner's phone review (*"The in game worldmap looks very odd … The honeycomb looks
bizarre … water should look like water"*). The live game was the 324-mod list with the
`ASHKARR_DEV_START_2026-10-20_MOUNTAINS` world, viewed with `jawa/world_view` and
`jawa/take_screenshot`. Scratch and full-resolution images are in `D:\ClaudeWork\rimmandrake\scratch\worldlook2\`.

## Images for the owner

| question | image |
|---|---|
| seas, then and now | `D:\ClaudeWork\rimmandrake\scratch\worldlook2\CMP1_twilight_sea_before_after.png` (2026-09-11 beauty shot on the left, same region now on the right) |
| what the honeycomb is | `D:\ClaudeWork\rimmandrake\scratch\worldlook2\CMP2_honeycomb_is_seafloor_layer.png` |
| the whole globe now | `D:\ClaudeWork\rimmandrake\scratch\worldlook2\wl2_globe_800.png` |

## 1. The honeycomb and the "little hexagonal rings" come from the sea-floor layer drawing through the planet

**Mechanism (MEASURED).** `RM_SeabedLayer` (Diving Interaction, 2026-09-26) is a geometric twin
of the surface: same origin, same radius (100), same 21,872 tiles (`jawa/world_layers`). In 1.6,
`WorldDrawLayer.Visible` returns `VisibleWhenLayerNotSelected` for a layer that is not selected,
and `WorldDrawLayerBase` defaults that to **true**. Terrain and Hills keep the default, which is how
the orbit layer shows behind the planet. No vanilla layer shares the surface's radius, so this never
mattered until we added one. Ours does, so the game draws two terrain meshes on one sphere, and the
depth test picks a winner tile by tile:

- The grey hexes with rings are `RM_SeabedBedrock.png` (mean RGB 69,69,74, a pattern of circles), the
  floor's default biome `RM_SeabedUnavailable` under all land. The olive striped fields are
  `RM_SeabedFloor.png` (134,134,106). The tan hexes between them are the real surface (`RM_Stillsand`,
  188,167,125).
- The floor's own Hills layer adds a second set of hill blots.
- **Proof that the surface was hidden:** repainting surface tile 8024 and its 6 neighbours to
  `RM_Contagion` (red) and committing changed nothing on screen, while the hill blot did change when
  8024's hilliness changed. Temperature and elevation edits changed nothing either. All edits were
  reverted, and a re-export matched the original tile for tile.
- This also explains the 2026-10-20 note in `RM_WorldTerrainShader.cs` that blamed WorldIce for "dark
  hex plates" on Stillsand. The floor's biomes were WorldIce (no roads, no rivers) until that same
  commit, so what it saw was the floor, not Stillsand.
- The offline research note blamed vanilla hill decals for the honeycomb
  (`Transient/worldlook_research_2026-10-20.md`). The decals are real, but they are not what makes
  the honeycomb.

**Fix (built, not deployed).**
`src/RimMandrake/DivingInteraction/Source/Patch_SeabedLayerCoplanarHide.cs` adds a Harmony postfix
on the `WorldDrawLayer.Visible` getter. It hides a draw layer whenever another layer on the same
sphere is the selected one, so the surface view hides the floor and the floor view hides the surface.
The orbit layer is unaffected. Needs a restart.

## 2. The seas are grey because they are drawn as land

**Mechanism (MEASURED, source).** `BiomeDef.DrawMaterial` gives the WorldOcean shader only to
`BiomeDefOf.Ocean` and `BiomeDefOf.Lake`, which it matches by identity. Every water tile on this world is
one of ours (`RM_TwilightSea` 607, `RM_GreySea` 472, `RM_TheScald` 312, `RM_TheChill` 57; 0 vanilla Ocean
or Lake), so all of them get WorldTerrain. `WorldDrawLayer_Terrain.CalculateInterpolatedVerticesParams`
then clamps any non-ocean vertex below 0 m to 0 m, which throws the −350 m depth away. On top of that, the
sea faces were replaced on 2026-10-18 (`ede2336a5`) and 2026-10-20 (`7a0d4309f`) by muted grey-green
colour fields. Before then the seas pointed at `World/Biomes/Ocean`, which in September was World Map
Enhanced's navy override (that mod is no longer on the list).

**Fix (built, not deployed).** `RM_WorldTerrainShader.cs` now gives every `isWaterBiome` BiomeDef of
ours the WorldOcean material. The Grey Sea, Twilight Sea and Scald point back at vanilla
`World/Biomes/Ocean`, and the Chill points back at its pre-10-18 face `Jawa_SickWater` (our own art).
No donor art is copied. The unused `RM_GreySea` / `RM_TwilightSea` / `RM_Scald` / `RM_Chill` PNGs stay
on disk. Needs a restart.

## 3. Rivers and roads

**Mechanism (MEASURED).** The live world held 1,309 river links and 1,731 road links. The record
`world/paint_inputs_2026-10-20/ASHKARR_WORLDMAP_links.csv` holds 326 and 1,242. All 1,568 record
links were present, plus 983 river and 489 road links that were not in it, and no links were missing.
The extras are vanilla worldgen leftovers: `world_links_import clearFirst` clears **only the tiles
the file touches** (JawaBenchWorldTools.cs), so generated links on every other tile survived the
S8 import. The extra roads carry no `AncientAsphaltHighway`, which fits faction roads between the 18
generated settlements. The mountain doc's "1,309 links / 106 river sources" counted those leftovers.

**Fixed live.** I cleared every link with `world_links_clear` over range 0-21871, re-imported the
record CSV (326 / 1,242, 0 refused), then ran `world_commit` with `recalcPaths`. Validation: 0 asymmetric
and 0 non-adjacent links. `world_lint` findings went from 32 to 21. I saved the result as
**`ASHKARR_DEV_START_2026-10-20_RECORDLINKS.rws`** (13.6 MB, sha256 `104641ed18f38d0f…`,
TidallyLocked present). `…_MOUNTAINS` is untouched. The river heads that the mountain pass raised
for the leftover rivers are now hills with no stream.

**Still open: record roads that draw nothing.** 196 record road links (392 tile entries) lie on
`RM_Stillsand` and 49 entries on `RUT_Umbra`, and both biomes have `allowRoads=false`. They are stored
but never drawn, so the roads on screen stop dead at the edge of the substellar desert. The Umbra ban
is the owner's ruling (RUT_UMBRA_ROADS_RULING_1). Stillsand's ban came from its ExtremeDesert donor
("no roads through the deep dune"). Either flip `allowRoads` on Stillsand or re-route the record's
desert roads. That is his decision.

## 4. Looks that remain after the fixes

- **Biome faces are flat colour fields** (`af7d8b365`, `7a0d4309f`). In September the faces came from World
  Map Enhanced (`zal.worldmapenhanced`, Workshop 3599967849) and GRimTerra World Map. Both are on the
  retired lists, not the 324. Putting either back is a cosmetic mod change, which needs his card.
  Proposal: re-add WME alone, at the next consolidated cold load (+1 mod). Its hill decal sets would
  also replace the vanilla blots on 49% of tiles. The cost is donor art in the world look, so it must
  be his call.
- **Feature labels** are large at mid zoom (Glass Reach, Twilight Sea, Dew Horn and others overlap the
  globe), as in `wl2_sea_900.png`. Not investigated.
- **Icon clutter:** about 140 world objects, and Mutator World Icons draws an icon per mutated tile
  (14,397 tiles carry mutators).

## Next cold load (batch it)

Deploy at shutdown (DLLs cannot be written while the game runs):
`python3 src/RimMandrake/Utils/deploy_custom_mods.py --compose biomes --apply`. The plan also carries the
already-committed `RM_CombHolds.xml` and `RM_ScrubInjections_GenStep.xml` (banned factions, 58488adc0).
Then load `ASHKARR_DEV_START_2026-10-20_RECORDLINKS` and check three things in Player.log and on screen:
the line `[RimMandrake.Biomes] world ocean shader on N water biomes`, blue seas, and no grey-ring hexes.

## 5. After the restart (2026-10-20, two cold loads on the 325 list)

Images: `D:\ClaudeWork\rimmandrake\scratch\worldlook3\` (`F_globe.png`, `G_sea_mid.png`, `H_coast_close.png`,
`I_mountains.png`, `J_desert_roads.png`).

- **First load: the planet drew black and every world view sat ~10 min in "GeneratingPlanet".**
  Mechanism (source + live): `WorldRenderer.ShouldRegenerateDirtyLayersInLongEvent` checks only the PLANET
  layer's visibility and whether a terrain draw layer on it is Dirty; `RegenerateDirtyLayersNow_Async`
  skips draw layers whose `Visible` is false. The coplanar-hide postfix made the floor's terrain layer
  invisible, so it stayed dirty for ever and `DrawWorldLayers` queued a new long event each frame, returning
  before it rendered. Fixed by a postfix on that getter that ignores hidden coplanar terrain layers
  (`Patch_SeabedLayerCoplanarHide.cs`, `6a182f352`). Second load: the save is playable in ~1 min, a world view
  regenerates in seconds.
- **Honeycomb: gone.** No grey-ring hexes at globe, mid or close zoom.
- **Seas: read as water.** `world ocean shader on 8 water biomes` is in Player.log. Grey, Twilight and Scald
  seas are flat slate-navy with faint darker hexes at depth. They have no shoreline effect or sheen.
- **Roads: all 1,242 record links live.** `world_links_get`: 2,484 road entries, 2,416 drawn. The 68 not drawn
  are on `RUT_Umbra` (34 tiles, his ruling RUT_UMBRA_ROADS_RULING_1 stands) and `RM_GelatinousSlime`
  (9 tiles, `allowRoads=false` from the Slime spec). Stillsand now has `allowRoads=true` (`6d8692254`).
  Across the desert the Ancient Asphalt Highway shows as short grey dashes. That is the record itself:
  its 153 highway tiles form 46 pieces of 1-9 tiles. Dirt paths are tan on tan and hard to see.
- **Rings back** (RW - Planet Atmosphere after `mandrake.rut.empirepursuit`): the debris ring draws clear of the
  planet, using the debris texture, not the grey disk. One Player.log error: `Shader Planet/AtmosphereLUT shader is not
  supported on this GPU`, so the atmosphere scattering does not render. Memory on the 325 list with Rings:
  8.3 GB working set, 18.1 GB private. There is no reading from the same session without Rings yet.
- **Tidal lock held**: `PlanetTypeManager.Current` = `TidallyLocked`, `7f.alienworlds.tidallylocked` patches present.
- **Face rendering facts (source).** `WorldDrawLayer_Terrain` puts the tile ELEVATION in UV0 and builds one
  submesh per material. The face texture is projected in the shader, not by mesh UVs. On screen the pattern
  runs on across hexes of the same biome with no seams, and every border between two biomes is a hard hex
  edge with no blending. Loose PNGs load with a full mip chain, trilinear filtering and anisoLevel 2, and are
  DXT-compressed when the texture-compression pref is on and both sides divide by 4
  (`ModContentLoader.LoadTextureViaImageConversion`). The texture scale (how many hexes one face spans) lives
  in the compiled WorldTerrain shader and is UNMEASURED.
- **Log hygiene:** in the first load, 9,520 `null texture passed to GUI.DrawTexture` lines from the looping
  loading screen hit Verse's message cap. The second load has 77.
