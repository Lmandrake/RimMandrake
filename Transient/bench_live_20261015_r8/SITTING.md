# BENCH live round 8 — testenv proofs of 7c14f99a19, 2026-10-15

ROUND HEAD **22b596181b** (= origin/main; includes 7c14f99a19 testenv hardening 3). git archive -> `/home/mandrake/.seat-tmp/BENCH/r8_export`,
copied (minus Transient, conversations) to `D:\Luke\dev\_rmscratch\bench_live_20261015_r8`; every bridge run is from that export.

## 0. Bridge + export
`rimflow bridge take --for "BENCH live round 8: testenv proofs"` (BENCH, was FREE). Export as above.

## 1. Deploy + launch (ratchet_pilot tier)
src delta 0207ac8fc2..HEAD is northstar/ + Utils/modcheck only (no mod-folder file), so nothing to apply. Plans (`deploy/plan_*.txt`):
GSS, LuminousPigment, UtinniPatches, WeatherSuite, MandrakePatches, PyrelandsMechanics in sync; SWBestiary 3 `-`, FlowWorks 8 `-`
(old northstar result JSONs in the game copy), composed biomes 1 `-`; 0 `~`/`+` anywhere. `dll_source_stamp.py check`: 0 non-MATCH.
Companion `build.py --gm --apply` from the export: identical to deployed.
Owner list md5 ee01dae9 (550 active) copied to `cfgsafe/ModsConfig.owner_pre_r8.xml`; `modset_builder --tier ratchet_pilot --apply` ->
22 active (`deploy/modset_apply.txt`). Previous Player.log kept as `Player.prev_session.log`. JawaBench profile `test`, expires 20:00Z.
`launch_ready.py --profile minimal` (Steam) READY pid 28596, 22 mods, 86 s, first_exception null (`launch.txt`). Census 399/400:
`jawa/revoke` MISSING (same as r6/r7, unused here).

## 2. TESTENV_FLESHBEAST_HARDEN_FREED_BY_UNFOG + TESTENV_CONTROL_NOISE_HARDEN_SPIDER_AT_ARM (GSS proof_all x3+)
Item command (`live/gss/run_gss.sh <n>`, inner `timeout 570`, `--out proof_all_<n>.json`), fresh quicktest each, export at 22b596181b.
Tier truth: `len(env.running)` = 22 on all three. Summaries by `live/gss/summ.py`; vitals by `vitals_events.py` / `vitals_read.py`.
| map | result |
|---|---|
| **1** | 110/110, wall 410 s. calm true; triggers RectTrigger+Letter (a shrine), 16 non-colonists, GlowPod+Hive destroyed; 1809 fogged -> 0; **releasedByUnfog []**, sweepPasses 0, hostilesAfter []. P3 PASS, hostilePawnsLeft []. Vitals: 0 hostile triggers |
| **2** | 110/110, wall 402 s. calm true; shrine pair, 15 non-colonists; 2503 fogged -> 0; **releasedByUnfog 5 fleshbeasts** (2 Fingerspike, Toughspike, 2 Bulbfreak), sweepPasses 1, hostilesAfter [], verified. P3 PASS. Vitals: 0 hostile triggers |
| **3** | 110/110, wall 407 s. calm true; shrine pair, 22 non-colonists; 41677 fogged -> 0; **releasedByUnfog 5 mechs** (2 RM_HullBolt, Mech_Militor, RM_LivingBolt, Mech_Pikeman), sweepPasses 1, hostilesAfter [], verified. P3 PASS |

No attempt aborted: 3 of 3 attempts ran to 110/110 (r7: 5 of 8 aborted at arm). The guard swept the freed hostiles in one pass on
both maps that had them, and the run went on.
- FLESHBEAST bar (no preflight GovernorStop; mapFog.verified true with releasedByUnfog listed on a shrine map; hostilesAfter []):
  **MET 3/3** -> verify pass, close.
- CONTROL_NOISE bar (no preflight abort; calm true with nonColonistsDestroyed + hostileBuildingsDestroyed recorded; >1 map-gen
  hostile swept before p2c with the run going on): **MET 3/3** (16/15/22 non-colonists; Hive+GlowPod; 10 freed hostiles swept) -> pass, close.
- Criterion 1 at 22b596181b: `modcheck record GimmeSomeSlack --tier ratchet_pilot` x3 -> DRAFT-CHECKLIST at fa3a10f36596
  (`live/gss/modcheck_record_{1,2,3}.txt`).

**Spawner, cheap read** (`live/probes/spawner_probe.py`, 4 fresh maps, no tick moved, no sweep before the unfog; `spawner_probe_{1..4}.json`):
- 3 of 4 maps released hostiles at `jawa/set_fog unfogAll` (8 fleshbeasts / 2 mechs / 2 mechs; 0 on map 2), and each group sits in
  a shrine: `AncientCryptosleepCasket`, `AncientHermeticCrate`, `Urn`, `Column`, `Slate` within 3 cells, RectTrigger+SignalAction_Letter
  pair in or next to it.
- `jawa/pawn_origin` (same epoch, before any save): every one is `firstObservedSpawn` at **tick 0**, `spawnChain mapgen:Settlement#N`.
  No generation observation. Factions Entities / Mechanoid. Incident journal empty. Their thing ids sit next to the triggers' ids
  (e.g. RectTrigger12799 -> Bulbfreak12824..28), well below the map's wild animals (38533+).
- **Not seen before the unfog**: an UNFILTERED `jawa/list_pawns` (walks `AllPawnsSpawned`) at tick 1 lists 18-39 pawns and none of the
  ids that appear after the unfog.
- So the pawns are made by mapgen with the shrine and spawn-observed at tick 0, but are out of `AllPawnsSpawned` until the unfog. The
  unfog does not generate them. What holds them out of the spawned list is still UNPROVEN (the recorder shows no despawn/respawn).

## 3. TESTENV_RIVERSITE_HARDEN_RIVER_ENDS_AT_SEA (river_site + swept x3)
Fixture reloaded (`northstar_site.py --site 1 --fingerprint 417df172fdb5 --tag r6 --reload-only --tile 5`, `live/river/site_reload.log`:
map 1 tile 5 RM_Pyrelands). `river_site.py` (`live/river/river_site_1.log`):
- Every candidate printed with its own mapId (2..10, = uid). **tile 60145 mapId 9: `rejected: no downstream edge: moving water reaches
  only {'north': 14}`**. That is r7's real sea-ending site; r7 printed it as 60146 because of the mapIndex bug. The item's line
  "60146 must be rejected" carried that mis-numbering. The real 60146 (mapId 10) has moving water on south 15 + north 14 and was accepted.
- Final line `tile 60146 mapId 10 map_info tile 60146`: equal. Quiet site (map) receipt: 0 removed, problems [], error None.
- Loaded maps after the run, read independently (`live/probes/setmap_probe.txt`, `jawa/set_current_map(-1)` refusal):
  **only uid 1 (tile 5, home) and uid 10 (tile 60146, site)**. All 8 rejected candidates were removed.
- BUT river_site printed `site problems ['loaded maps unreadable after the site was chosen']` and no `loaded maps:` line. HARNESS,
  traced: the tool's refusal carries `loadedMaps` under `details` (`{"success": false, ..., "details": {"loadedMaps": [...]}}`), and
  `river_site.loaded_maps()` reads `r.get("loadedMaps")` at top level. `selftest_river_site`'s fake world puts it at top level
  (L138), so the offline check cannot see this. Effect: the leftover-candidate read-back is blind (it would not catch a leftover),
  the drop pass before it is skipped (`leftover_maps(None)` = []). The per-reject drops in the loop did the work this time.
- `extension_proof --live --site river --chains swept` x3 (`ext_swept_{1,2,3}.json`/`.log`, 16/14/14 s): **returns_home PASS 3/3**,
  run_validity CLEAN, 0 findings; each staged 5 on the edges (`SWEPT pending=5` -> `0`), tile 60146 by map_info. 3 declared river
  bruises (vitals seq 49, 50, 58, map 10; health >= 0.89).
-> bar met (sea tile rejected as no downstream edge, tiles equal, no other candidate loaded, swept 3/3) -> verify pass, close.
  The blind read-back goes to TESTENV_BUMBLEDRONE_HARDEN_UNINVITED_BUZZ, whose guard it is.

## 4. TESTENV_BUMBLEDRONE_HARDEN_UNINVITED_BUZZ (river_site + extension_proof river x2)
- A 2nd river_site on the fixture world found no free fast-lane tile (`river_site_2.log`, 9 tried, all rejected and removed: loaded
  maps after = home + 60146 only, `setmap_probe_2.txt`). It left home current, so I took a fresh quicktest (`probes/fresh_map.py`, tile
  50310, Playing + map_info) and ran `river_site.py` (`river_site_3.log`): **tile 1474 mapId 1** (current 8152, fast 3943, moving
  water W 32 / E 35), final tiles equal, quiet receipt clean (error None), same `loaded maps unreadable` site problem.
  Independent read (`setmap_probe_3.txt`): uid 0 (quicktest home, pre-existing) + uid 1 (site) only.
- `extension_proof --live --site river` x2 (`ext_river_{1,2}.json`/`.log`, 47 s each): **15 PASS / 6 UNMEASURED / 0 FAIL** both,
  aborted None, run_validity CLEAN, 0 findings, **no GOVERNOR_STOP / hostile_arrival**. Vitals over the whole session
  (`live/river/vitals_river.json`): 0 hostile triggers on any map; hurt = the 3 declared bruises above only.
- UNMEASURED: `works/ferry_rope` "could not find two banks across the current" (SITE: the wide 2.5-size river; the rest of `works`
  is skipped after it), and `placer/flood_refill` (owed, no predicate yet, by design). Not this item's bar.
-> no uninvited arrivals, no extra maps, quiet receipt clean: the threat half is met. The `loaded maps:` read-back the bar names is
  blind (section 3) -> **verify partial, kept open**, NEXT: read `details.loadedMaps` in `river_site.loaded_maps` and make the fake
  world in `selftest_river_site` nest it the way the tool does.

## 5. Restore + teardown
Tier list saved (`ModsConfig.tier_at_teardown.xml`, md5 b1064499); `Player.22b596181b.log` kept. Game killed by PID 28596 (taskkill),
gone. `modset_builder --restore` -> **ee01dae9, 550 active, verified** (`restore.txt`). `./game --why ... down`; bridge released.

## 6. Ledger
(pending)
