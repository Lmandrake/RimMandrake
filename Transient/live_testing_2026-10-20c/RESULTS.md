# Acceptance sweep on the live 374 list (FOUNDRY bridge helper, 2026-10-20c)

Game UP on 374 (1.6.4871), not restarted. Bridge taken 05:32Z "acceptance sweep 374", released ~05:55Z on the
coordinator's call (owner wants a restart for aurora light, rhossak fix, xenotype heads). Cut short: no L1 item sweep.
Prior state: `Transient/live_testing_2026-10-20b/RESULTS.md`.

## Status
- [x] bridge take; `belt_watchdog.py` 05:32Z: game healthy (its only DEAD row is a 328 h-old TerminalBiomes runner heartbeat)
- [x] fixture `RM_TestSite_calm_v1_AREAFIX2` loaded (12 s; the known site-tile "unverified" harness mismatch).
      Note: `load_areafix2.py calm` without a name picks a save that does not exist and waits 300 s silently; pass the name.
- [x] roster probe (biome_probe) + G13 mapgen dry run, 26 of 28 paint targets + vanilla control
- [x] screenshots
- [ ] acceptance L1/L2 item sweep: NOT DONE (stopped for the restart)

## Instruments and sanity probes
- `Verse.Log.Clear` before each map; then `Log.Error("SANITY_PROBE_20c…")` reached Player.log (1 hit): the log was live.
- Control `AridShrubland` at 20 C: 17 wild animals, 823 plants, 0 exceptions: the animal and plant counters can see.
- Maps: `jawa/world_tile_map_generate` with **suggestedMapParent=Camp** (not Settlement: no factionless-Settlement NREs),
  150x150, tile temperature forced to **20 C** for every biome, counted with no ticks, then `map_drop`, Camp removed, tile
  restored. Script `mapgen.py`, rows `mapgen.jsonl`. 0 Camps left on the planet afterwards (`world_objects_get def=Camp`).
- ⚠️ A Camp map with no colonists is culled on the first tick (my first Ummisk shots landed on the world view).

## Roster probe (L1, runtime caches; `roster_probe_all.json`, `roster_probe_explicit.json`)
All 27 `RM_` paint targets and `RUT_Umbra` resolve with a non-empty animal roster and `animalDensity` > 0.
Plant roster 0 for `RM_RustCathedral` and `RM_NightsideIce` (plantDensity 0: by design). `RM_FeverWood`,
`RM_WeepingStones`, `RM_Wasteland`, `RM_LanternDeeps` have generatesNaturally=false (hand-painted only).
Not found as BiomeDefs: RM_CrackedLands, RM_Slime, RM_Umbra (names do not exist; not paint targets).

## G13 mapgen dry run (runbook `design/RimMandrake/world_remake_2026-10-19/06_remake_runbook.md` §2 G13)
Bar: map biome == B, wild animals > 0 or plants > 0, no mapgen exception. All at 20 C.

| biome | map biome | wild animals | plants | exceptions | top kinds |
|---|---|---|---|---|---|
| `AridShrubland` (control) | AridShrubland | 17 | 823 | 0 | RSW_Anooba 6, Quail 2, Hare 2 |
| `RM_Abyss` | RM_Abyss | 7 | 1377 | 0 | RM_Sesserith 4, RSW_TaozinGrub 2, RSW_Taozin 1 |
| `RM_BlueDesert` | RM_BlueDesert | 2 | **0** | 0 | RSW_Vapaad 2 |
| `RM_Contagion` | RM_Contagion | 10 | 4129 | 0 | RM_Gawpsack 4, RM_Sparkleech 2, RM_Blisterfloat 2 |
| `RM_FeverWood` | RM_FeverWood | 7 | 9705 | 0 | RM_Thornbug 5, RM_Drommath 2 |
| `RM_FloodedCanyon` | RM_FloodedCanyon | 6 | 236 | 0 | RSW_MutagenicNorphea 3, RUT_SealedSleeper 2, RM_Ommok 1 |
| `RM_GelatinousSlime` | RM_GelatinousSlime | 5 | 8579 | 0 | **Megasloth 2, WasteRat 1, Elephant 1** (vanilla) |
| `RM_Greentide` | RM_Greentide | 24 | 13683 | 0 | RSW_Kinrath 6, RSW_Nuna 5, RSW_Clodhopper 4 |
| `RM_LeaningScrub` | RM_LeaningScrub | 5 | 5130 | 0 | RSW_Urusai 3, RM_Thornhold 2 |
| `RM_LongShade` | RM_LongShade | 3 | 108 | 0 | RSW_Sketto 2, RM_Vrekka 1 |
| `RM_Miasma` | RM_Miasma | 25 | 2691 | 0 | RSW_Bogwing 4, RSW_Vornskyr 4, RSW_CrestedDragon 3 |
| `RM_NightsideIce` | RM_NightsideIce | 1 | 0 | 0 | RM_Zhissa 1 |
| `RM_Pyrelands` | RM_Pyrelands | 8 | 19646 | 0 | RSW_Nuna 5, RM_Flamefang 2, RSW_Orray 1 |
| `RM_RustCathedral` | RM_RustCathedral | 1 | 0 | 0 | RM_CathedralRoach 1 |
| `RM_Stillsand` | RM_Stillsand | 3 | 17 | 0 | RM_Loomma 2, RM_Drazzik 1 |
| `RM_TheRot` | RM_TheRot | 7 | 2611 | 0 | RM_Grellik 2, RM_Agaripawn 2, RSW_ShiroTrap 1 |
| `RM_TheSump` | RM_TheSump | 8 | 3525 | 0 | RM_Skarrid 3, RM_Kethrel 2, RM_ThrummelWarden 1 |
| `RM_Warscar` | RM_Warscar | 15 | 183 | 0 | RSW_MegaphoridLarva 9, RM_Chotrix 2, RM_ElectricTick 2 |
| `RM_Webwork` | RM_Webwork | 13 | 7623 | 0 | RM_Cravvet 5, RM_Quarrok 4, RM_Ollathrix 3 |
| `RM_WeepingStones` | RM_WeepingStones | 6 | 722 | 0 | RSW_Eopie 3, RM_Sillik 1, RM_Karrek 1 |
| `RM_GreySea` | RM_GreySea | 4 | 266 | 0 | RM_Grusk 2, RM_Orruhmu 1, RM_Nissik 1 |
| `RM_TheChill` | RM_TheChill | **0** | **0** | 0 | — |
| `RM_TheScald` | RM_TheScald | 3 | 185 | 0 | RM_ScaldWalker 3 |
| `RM_TwilightSea` | RM_TwilightSea | 1 | 10563 | 0 | **Hare 1** (vanilla) |
| `RM_Cauldron` | RM_Cauldron | 6 | 6014 | 0 | RM_Suush 2, RSW_Neebray 1, RSW_Silooth 1 |
| `RM_TheForge` | RM_TheForge | 7 | 536 | 0 | RM_Dhoggur 3, RSW_Tibidee 3, RM_ColossalAerofleet 1 |
| `RM_Wasteland` | RM_Wasteland | 2 | 875 | 0 | RSW_Sacapillar 2 |

- **25 of 27 RM_ targets PASS the G13 bar at 20 C. `RM_TheChill` FAILS (0/0)**, though its roster resolves 10 animals and
  10 plants; 20 C is likely wrong for a cold sea, so re-run it at a Chill-typical temperature before calling it a mod defect.
- **UNMEASURED:** `RM_LanternDeeps` and `RUT_Umbra` (the scratch-tile list ran out at 12 in batch 2; nothing refused).
- Worth a look (not G13 failures): `RM_BlueDesert` 0 plants (plant roster 9, plantDensity 0.33); vanilla Megasloth/Elephant/
  WasteRat on `RM_GelatinousSlime` and a Hare on the `RM_TwilightSea` floor (biome-specific roster rule).
- Single map per biome, one temperature: animal counts are a draw, not a rate.

## Screenshots (D:\ClaudeWork\screenshots\2026-10-20\)
Fresh maps generated for the shot (Camp parent), no ticks run, dropped afterwards.
- `umbra_wide_20c.png`, `umbra_mid_20c.png`: RUT_Umbra at -60 C, permanent `RM_WS_DarkAurora` active (weather Clear, last
  RUT_PropaneRain). Ground reads dark grey with pale patches; aurora light on the ground is not visible (the deployed build
  still has the LerpDarken problem; the fix needs the coming restart).
- `ummisk_lava_wide_20c.png`: two RM_Ummisk at the edge of a painted 6x6 LavaDeep pool on an RM_TheForge map (small at this
  zoom; my close-up missed the subject and was deleted).

## Verifies recorded
- none (nothing measured here maps cleanly onto an item criterion: G13 is a runbook gate, not a ledger criterion).

## End state
Game UP on 374, home map = the AREAFIX2 fixture (not saved), bridge released. Pointers:
- G13 (runbook) — 25/27 PASS at 20 C, RM_TheChill FAIL, LanternDeeps + RUT_Umbra UNMEASURED; NEXT: re-run `mapgen.py RM_TheChill,RM_LanternDeeps,RUT_Umbra` with each biome's own temperature after the restart.
- Acceptance L1/L2 sweep — not started; NEXT: run it from `acceptance_list.txt` after the restart.
