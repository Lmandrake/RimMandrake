# Grey Sea floor live sitting — 2026-10-08 (GREYSEA_FLOOR_PASS_1)

## Staged
- **Map 4** (`mapId 4`) is the review map: `RM_SeabedFloor_GreySea` on the `RM_SeabedLayer`, tile 33, generator `RM_SeabedGenerator_GreySea`, parent `RM_SeabedSite`. 3 colonists (PlayerColony) so it stays a home map. 0 hostiles. Unfogged, 12 PM, game PAUSED.
- How it was reached: `jawa/world_tile_map_generate layer=RM_SeabedLayer biome=RM_SeabedFloor_GreySea` (the layer's own checkout; no ship flight). The planet has no Grey Sea tiles (painting is the last step), so two fixtures stand in: the SURFACE tile 33 (Coga Ocean, 6.9 C) was set to `RM_GreySea` with `jawa/world_tile_set`, and the floor tile's biome was set by the tool's `biome=` param. Both are needed: the floor's cast is read from the sea ABOVE (`RM_SeaFloorIdentity.SeaBiomeOf`), not from the floor biome.
- Camera parked on the feature window x121-165, z189-215 (two salt chimneys with seep aprons, pillars, crystals).
- **Flora is STAGED by hand, not grown**: 4 of each of the 17 ruled plants were spawned in that window, because the Plants step grows none (see Broken). Everything else on the map came from the generator.
- Weather: Clear shot, then `RM_GreySaltSnow` forced and held, then the lock released before the save, so salt snow is falling now and natural weather takes over from there.
- Keeper save: see the bottom of this file.
- Maps 1-3 are discarded test maps, not home maps, and get culled once time runs.

## Cast present on map 4 (`jawa/list_things`, ruled roster from RM_GreySea.xml)
12 of 16 species, 13 pawns, no outsiders: Essarn 1, Otheska 1, Sallik 1, Karrud 1, Hessal 1, Oomal 1, Maalu 1, Immu 1, Nissik 1, Thollim 1, Grusk 2, Corrik 1. Missing: Reefback (0.005), Fessk (0.01), Haarn (0.08), Orruhmu (0.05), the four rarest. All 13 came from `GenStep_SeaFloorFauna` (one group per species). The vanilla Animals step added nothing even at floor animalDensity 3.0, so the floor is thin: 13 animals on 250x250.

## Formations on map 4 (generator output)
RM_SaltPillar 81, RM_SaltDome 111, RM_SaltChimney 13, crystals White 11 / Pink 5 / Amber 5 / Violet 3, wreck hull 22 + spine 4. Terrain in the window: RM_SeaFloorGround, RM_BrineChannel (trails out of the chimneys), plus a seep apron around each chimney.

## Agenda he walks (from the item)
- [ ] Floor map is the Grey's OWN floor (RM_SeabedFloor_GreySea on RM_SeabedLayer), not the generic placeholder
- [ ] Pillars (GREYSEA_FLOOR_FORMATIONS_1) present and reading as the navigation system
- [ ] Ruled crystal flora present at real plantDensity
- [ ] Own terrain
- [ ] Weather: RM_GreySaltSnow falls and its overlay reads on a layer map
- [ ] Cast present (anchors RM_Reefback, RM_Fessk, pillar-mason, ossuary shrimp, sessiles)
- [ ] Brine pools / elders present
- [ ] Reconciliation row: RUT_Sallik-family fishTypes vs ruled sparse catch — coexist or cull
- [ ] Five content-drop contradictions (second colossal organism; abundant sessiles; retracting flora; salt snow; chemosynthesis) + §9 ten questions + 'Reshapers' exonym
- [ ] Roster JSON `flora: []` amendment
- [ ] Owner rules the floor done

## What the screenshots showed (read by the agent before handover)
Folder: `D:\Luke\dev\RimMandrake\Transient\greysea_sitting\shots\` (once the mirror syncs; the live copies are in the game's Screenshots folder).
- `greysea_floor_clear.png` (wide, midday, clear): plain warm-brown rippled sediment. White capped pillars cast long dark rectangular shadows. Two salt chimneys sit on pale crust aprons with dark brine-channel trails running south. The staged flora is tiny scattered dots at this zoom. It reads sparse and empty.
- `greysea_floor_clear_close.png` (rootSize 14): twin stacked white chimney columns on a grey cracked crust apron. ⚠️ The apron's outer halo is a hard square-stepped pixel ring, not a soft edge. The staged flora reads well up close (kelp curtains, dark blade crystals, fans, pods). The pillars' shadows are solid dark vertical blocks.
- `greysea_floor_saltsnow.png` (rootSize 18): the "Salt snow" label shows and the whole scene goes grey and desaturated. No falling particles can be seen in the still frame. ⚠️ Large dark blocky stepped regions appear top-right and as a band under the pillar row; these were not in the clear frame. Unexplained: `snowRate` is 0, so they are not snow cover. He should look at these.
- Camera trap seen: `frame_cell_rect` did not zoom. `set_camera_zoom` reports the new rootSize, but a screenshot taken 1.5 s later shows the old frame; at 5 s it is correct.

## Broken / notes (for FOUNDRY, not fixed here)
1. **No flora ever grows on the Grey floor.** Cause found from the decompiled `WildPlantSpawner.CalculatePlantsWhichCanGrowAt`: a plant above the biome's lowest `wildOrder` needs lower-order plants nearby. All three order-1 plants (`RM_GlassVeilKelp`, `RM_Brinecomb` on tag `RM_GreyBrineChannel`; `RM_SaltChimneyVine` on `RM_GreyChimneySeep`) are gated on terrain tags. Nothing on the generated floor carries those tags (the channel terrain painted is `RM_BrineChannel`), so no order-1 plant grows, and then none of the 14 order-2 plants can grow either. Matches the 2026-10-06 validator FAIL ("0 of 16 ruled Grey plants"). The Reassert density fix was necessary but was never the whole cause. Fix options: paint the tagged terrains in the generator, or give an ungated plant wildOrder 1.
2. **Map Designer resets the floor densities DURING generation**, after `RM_SeabedSiteParent.ChooseFor`'s Reassert has run ("[Map Designer] Applying settings" sits inside GetOrGenerateMap and writes back the 0 it snapshotted at startup). On the first map both densities read 0. Worked around live by calling `RM_SeabedFloorLife.ReassertAll` and then `MapDesigner.HelperMethods.InitBiomeDefaults` (re-snapshot); the densities then held through three generations. A durable fix belongs in code: Reassert after Map Designer's apply, or re-init its defaults.
3. **Geological Landforms BiomeTransitions runs on layer maps against the SURFACE tile id.** Under a grassland surface tile, the floor map got 679 land animals of 130 kinds (Rat, Muffalo, Elephant, Rancor…). Over open ocean it picks "Landforms: None". The ship path can only reach sea tiles, so this matters less there, but it is a stray-fauna route.
4. **The vanilla Animals step spawns nothing on the floor**, even at density 3.0. Likely cause, not yet proven: the cast are waterSeekers and the floor has no water cells (`CommonalityOfAnimalNow` returns 0). The whole population is GenStep_SeaFloorFauna's one-per-species, so the 4 rarest species are usually absent and 13 animals cover the map. The "Animal starvation" alert fires at once because there is nothing to graze (see 1).
5. **Salt snow can be picked naturally**: the live floor biome carries 2 weather records (Clear, RM_GreySaltSnow) and the WeatherDef is `isBad false, favorability Neutral, repeatable false`. It was not seen falling on its own in this sitting. The overlay itself shows only as a grey wash in a still frame.
6. Weather tooling: each `jawa/weather_set lockWeather` call adds another permanent "Forced weather" GameCondition. Four were stacked before the unlock.
7. Every staging script is in `Transient/greysea_sitting/` (gen*.py, census2.py, stage.py, shoot.py, save.py).

## Working log (agent, live)
- Map 1 (fixture floor biome under a GRASSLAND surface tile 49211): Map Designer's in-generation "Applying settings" reset floor densities to 0 after Reassert; Geological Landforms BiomeTransitions filled it with 679 land animals of 130 kinds; 0 plants. Discarded.
- Map Designer snapshot re-taken live (static_call MapDesigner.HelperMethods.InitBiomeDefaults after RM_SeabedFloorLife.ReassertAll) — densities then held 3.0/0.22 through later generations.
- Maps 2-3 (ocean tiles): SeaBiomeOf = Ocean, so GenStep_SeaFloorFauna seeded ocean canon strays (Blixus, Dianoga, Fanback, Mott), no Grey cast.
- Map 4: surface tile 33 painted RM_GreySea (fixture), floor biome fixture RM_SeabedFloor_GreySea -> SeaBiomeOf = RM_GreySea. Cast 12/16 species, 13 pawns, no strays. Pillars 81, domes 111, chimneys 13, crystals W11/P5/A5/V3, wreck 26. PLANTS 0.

## Keeper save — NOT LANDED (as of 19:40)
- The Saves folder's .rws files were backed up first to `D:\Luke\dev\_rmscratch\saves_backup_greysea_2026-10-08\` (129 files).
- `rimworld/save_game GreySeaFloor_Review_2026-10-08` never got to run. Right after the salt-snow shot (about 19:23) the bridge stopped answering: the first call of the save script timed out at 300 s. Player.log has had no new line since 19:23:18. The game process is up, reports Responding, and burns about 2 cores, so the main thread is busy with something long. Nothing new or changed in Saves since 12:27.
- The staged scene is still live on map 4 (if the game recovers): camera window x121-165 z189-215, salt snow falling.
