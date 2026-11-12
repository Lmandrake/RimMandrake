<!-- Written by the session when it would show this to the owner. One verdict line per statement bullet, the
     bullet copied exactly. Verdicts: true, false, unseen, cannot tell. Only "true" passes the Stop hook, and a line
     you would caveat is not true yet. Evidence is one or more saved files, in backticks, made after your last
     change: screenshots, rendered output, logs, a recorded run. Paths relative to the project, inside it. -->
# Done claim

- unseen: Every sea describes BOTH its floor (animals you meet by diving) and its catch (fish from the shore): the floor half is unbuilt across all four seas is done as `infrastructure/state/items/SEA_FLOOR_AND_CATCH_PASS_1.md` says, shown by fresh evidence. | evidence: `whittle/sea_floor_and_catch_pass_1/evidence/per_sea_verdict.txt` `whittle/sea_floor_and_catch_pass_1/evidence/offline_checks.txt` `whittle/sea_floor_and_catch_pass_1/evidence/offline_chain_audit.md` `whittle/sea_floor_and_catch_pass_1/evidence/selftests_fresh_all.txt` `whittle/sea_floor_and_catch_pass_1/evidence/swim_shore_reach_direct.txt`

Why "unseen" and not "true": the item's verify asks, for each sea, for "a floor the gravship flies down to and that is populated". Its criteria are "Flying the gravship down to a sea's floor shows you the animals…". Neither has ever been seen in a game. This lane is offline and drives no game. SEABED_DESCENT_ASCENT_1, the flight itself, is `built` but BLOCKED on a harness fault (PROVEGRAVSHIP_FIX_PIPES_FOR_ABSENT_VGE: the proof lays a VGE pipe on a game without VGE). Everything that can be shown offline is shown, and it holds. In the item's own words, it is "authored, not live-proven".

Per sea, measured at the published HEAD (`evidence/per_sea_verdict.txt`):

| sea | shore verdict | floor | floor cast / catch rows / catch without a living floor body | catch-only, with its reason |
|---|---|---|---|---|
| RM_TheScald | RM_SeaShoreExtension: RM_ScaldWaterOceanDeep/Shallow laid by RM_SeaCoast on bordering land; freshwater bands served through the empty-band fallback | RM_SeabedFloor_TheScald, density 0.15×30 = 4.5, fauna genstep on | 10 / 9 / 0 | RM_Saal's body is RM_Noohm (written in RM_ScaldFish.xml; CATCH_BODY_ALIAS) |
| RM_GreySea | RM_WaterBrineDeep/Shallow and RM_SaltCrustShore | RM_SeabedFloor_GreySea, 0.1×30 = 3.0 | 9 / 4 / 0 | rare RM_SaltCameo and Silver are not species |
| RM_TwilightSea | vanilla ocean, resolved to this sea through PrimarySeaFor | RM_SeabedFloor_TwilightSea, 0.1×30 = 3.0 | 22 / 14 / 0 | rare RM_LampBlack is not a species; Corpse_RSW_ColoClawFish's body RSW_ColoClawFish is now cast live (0.03) |
| RM_TheChill (the Propane Lake) | RM_PropaneDeep/Shallow (Saltwater, providesCatch on): fishable | RM_SeabedFloor_TheChill, 0.08×30 = 2.4 | 10 / 9 / 0 | rare Chemfuel is not a species |

What this round changed (published `6039084c72`):
1. **The four sea descriptions now describe both halves.** Before this round, none of the four player-facing descriptions named one floor animal, one catch, the gravship or the shore. Each now has one sentence, written from the measured cast and catch. `validation.sea_description_checks()` guards it inside `selftest_sea_catch_alive.py`, and its 3 mutants go red.
2. **Stale floors are re-derived on load.** A save mirrored its floor only once, so a pre-wiring save, or a surface repainted on an existing save, kept an empty or impassable floor under our seas. Players receive a save, so that would have been their normal case. `RM_SeabedLayerUtility.ResyncStaleFloors` now re-derives every mismatched floor tile on load and skips any tile carrying a world object. The DLL was rebuilt with 0 errors and 0 warnings. The wiring selftest gained check 8 and 3 mutants, and its check 6 confirms the DLL stamp matches the source.
3. The stale "Propane Lake not wired" comment in RM_SeabedFloorBiomes.xml is corrected.

After the first judge (would show: no):
- Every sea selftest was rerun fresh, with `--no-cache`, 8/8 PASS (`evidence/selftests_fresh_all.txt`). That includes the compiled `selftest_seashores`, which now builds on this seat once the D:\SteamLibrary assembly paths are passed in. `swim_shore_reach` passes 3/3 when run directly (`evidence/swim_shore_reach_direct.txt`). The three fuzz selftests still crash on the missing `/mnt/d/Luke/dev` path on this seat and gave no verdict.
- The Chill as a fishable shore is the owner's call, not an assumption:
  - his brief to make at least seven catches in every sea, the Propane Lake included (`design/Jawa/worldbuilding/sea_catch_rosters_2026-09-24.md:8`);
  - his card of 2026-09-24 on FlowWorks' Saltwater propane shore (same file, `:127`).
- The 2026-11-03 OWNER note says this item, kind `design`, waits for the Designer. The design was decided long before that: the pairing rule ruled 2026-09-22, the gravship ruling 2026-09-26, the catch rosters ruled 2026-09-24. Nothing in this round invented design; it fixed load-time wiring and text.

## What I'm least sure about
- `ResyncStaleFloors` runs inside `WorldComponent.FinalizeInit`. I am assuming `Find.WorldObjects` is fully loaded by then, and that the floor layer's world drawer picks up the changed biomes without an explicit regenerate. Both are engine assumptions; RimSage was unavailable on this seat.
- The new description sentences are prose an agent wrote. They name only species measured in each sea's cast and catch, but nobody has judged their taste.
- Old dev saves may carry RUT_ seas on the planet. A RUT_ sea has no floorBiome, so the re-sync correctly gives it the generic floor until the repaint. The re-sync makes the repaint take effect on an existing save; it does not stand in for the repaint.

## What I did not test
- Any live game: the descent and return, animals spawning and being met on the floor map, a fishing zone on a coast beside each sea, and the re-sync's log line on a real save.
- `selftest_seashores` (the compiled one) and the three fuzz selftests did not reach a verdict on this seat. They need RimWorld assemblies at the C: path and `/mnt/d/Luke/dev`. I built the DLL by passing the D:\SteamLibrary assembly paths as MSBuild environment properties.
