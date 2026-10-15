# BENCH live round 7 — testenv hardening proofs, 2026-10-15

ROUND HEAD **0207ac8fc2** (= origin/main; includes 0c3ffd17d0 hardening + FlowWorks DLL 06faddba44). git archive -> `/home/mandrake/.seat-tmp/BENCH/r7_export`,
copied (minus Transient, conversations) to `D:\Luke\dev\_rmscratch\bench_live_20261015_r7`; every bridge run is from that export.

## 0. Bridge + export
`rimflow bridge take --for "BENCH live round 7: testenv hardening proofs"` (BENCH). Export as above.

## 1. Deploy + launch (ratchet_pilot tier)
Plans from the export (`deploy/plan_*.txt`): GSS, LuminousPigment, UtinniPatches, WeatherSuite, MandrakePatches, PyrelandsMechanics in
sync; SWBestiary 3 `-` only; composed biomes 0 `~`/`+` (1 `-`). FlowWorks `~` RimMandrakeFlowWorks.dll + srchash -> applied, md5 repo =
game be192d9c27cc; re-plan 0 `~`/`+`. `dll_source_stamp.py check` (bench clone at HEAD): 0 non-MATCH (FlowWorks, GSS, FireEcologyHook,
PyrelandsMechanics MATCH). Companion `build.py --gm --apply`: identical to deployed.
Owner list md5 ee01dae9 (550 active) copied to `cfgsafe/ModsConfig.owner_pre_r7.xml`; `modset_builder --tier ratchet_pilot --apply` ->
22 active. Previous Player.log kept as `Player.prev_session.log`.
`launch_ready.py` (Steam) READY pid 30928, 22 mods, 86 s, first_exception none (`launch.txt`). Census 399/400 jawa tools: `jawa/revoke`
MISSING (same as r6, unused here).

## 2. TESTENV_FOGGED_MECH_HARDEN_WOKE_ON_REVEAL + TESTENV_CONTROL_NOISE_HARDEN_SPIDER_AT_ARM (GSS proof_all x3) + criterion 1 record
`proof_all.py --live --no-shots` (item command; `live/gss/run_gss.sh`), fresh quicktests. Vitals per map via `vitals_events.py`
(events are in `triggers`; r6's printed count read 0 from the wrong key) and `vitals_read.py`.
| attempt | result |
|---|---|
| **map 1** | 110/110. p2c calm: 2 triggers, 20 non-colonists, EggSac/GlowPod/Hive destroyed, 2909 fogged -> 0. P3 PASS, mapFogCleared verified foggedNow 0, hostilePawnsLeft []. Vitals after P3: muffalo test subjects only, 0 hostile_arrival / letter |
| 2a, 2b | preflight GovernorStop: Anomaly fleshbeasts (Trispike/Toughspike; 2 Fingerspike + 2 Toughspike + Bulbfreak) present at arm in p2c's advance, AFTER p2c's calm read back calm |
| 2c | same, mechs: RM_Borehulk x4, Mech_Pikeman x2, Mech_Scorcher, RM_LivingBolt |
| 2d | NOT COUNTED: JawaBench test profile expired 12:00Z mid-run (`companion_profile.json`), Z_log_budget UNMEASURED (static_call refused as CAMPAIGN); 7 hostiles (3 HullBolt, CathedralRoach, 3 fleshbeasts) present through the p2c advance without a stop, swept by P3. Profile renewed to 20:00Z, same keys |
| **map 2** (2e) | 110/110. p2c calm: 17 non-colonists, EggSac/GlowPod/Hive, 8480 fogged -> 0. P3 PASS (same readback). 0 hostile_arrival / letter after P3 |
| 3a, 3b | preflight GovernorStop: fleshbeasts present at arm (as 2a) |
| **map 3** (3c) | 110/110. p2c calm: 3 non-colonists, 1159 fogged -> 0. P3 PASS (same readback). 0 hostile_arrival / letter after P3 |

**Probe** (`live/probes/calm_probe.py`, fresh maps, no tick moved; `calm_probe_1.json`, `calm_probe_2.json`): 0 hostiles after
disarm + hostile buildings + `destroy_bulk nonColonists` (which walks AllPawnsSpawned, fogged included); **4 fleshbeasts right after
`clear_map_fog`** at the same tick, map-gen ids, no pawn_origin row, no incident, no letter; they survive save/load. So the whole-map
unfog RELEASES unspawned holders' pawns (fleshbeasts and, on 2c, mechs, which is r6 map 3's residual class), after the guard's own
hostile check. Vanilla `FogGrid.Unfog` spawns nothing (rimsage: only Pawn overrides Notify_Unfogged; only PathFinderMapData listens
to CellFogChanged), so the spawner is presumably a tier mod or an Anomaly comp: presumed, unproven. Filed
**TESTENV_FLESHBEAST_HARDEN_FREED_BY_UNFOG** (re-sweep after the unfog until no hostile).
- FOGGED_MECH bar (P3 PASS, mapFogCleared verified, foggedNow 0, control_noise_calm.calm true, no "Area revealed" / hostile_arrival
  after P3 on any map): **MET on 3/3 complete maps** -> verify pass, closed. (The mechs now surface at p2c, where the unfog releases
  them, and never after P3.)
- CONTROL_NOISE bar ("no preflight abort on a GovernorStop"): **NOT MET**, 5 of 8 counted attempts aborted at arm on hostiles the calm's
  own unfog released. The original cause is fixed (map-gen hostiles and hives swept before the advance: 20/17/3 non-colonists,
  hives on 2 maps) -> verify partial, kept open, NEXT on TESTENV_FLESHBEAST_HARDEN_FREED_BY_UNFOG.
- Criterion 1 at 0207ac8fc2: 3 x 110/110 (maps 1-3). `modcheck record GimmeSomeSlack --tier ratchet_pilot` x3 -> DRAFT-CHECKLIST at
  fa3a10f36596 (latest `proof_all_map3.json`).

## 3. TESTENV_STORM_FIRES_HARDEN_DECOY_BURN (Pyrelands p4 chain order)
Item commands verbatim, from the export. The fixture `NS_Pyrelands_site_1_417df172fdb5_r6` reloads clean (map 1, tile 5, 56.7 C,
`live/pyre/site_reload.log`). Then I ran p4: `burrowers,fulgurite,ullai_and_giant,sand_shovel,lightning_breaker` (`pyre_p4.log`, `.json`).
It came out **PASS=8 FAIL=0** and 10/10 components PASS. The rest are UNMEASURED only because those chains were not selected, as in r6.
`herd_follows_two_day_old_burn` **PASSes in the same run as fulgurite**, which had 20 DryThunderstorm windows and fires in 10 of them.
The note "sky calmed before the burns" reads: weather Clear x2 ok, extinguished 0, **strayFires 0**, verified.
The burn line read the right burns: burn A was at newest 29,99 and burn B at newest 219,99. No `teardown` FAIL component.
-> bar met, verify pass, closed.

## 4. TESTENV_SWEPT_BRUISE_HARDEN_OWN_HAZARD (swept x3)
- **Site 1.** `river_site.py` ran on the Pyrelands fixture's world (`river_site.log`). It reported tile 60146, but the map it made
  current is uid 9 = tile **60145**: it passes mapIndex to `set_current_map(mapId=uniqueID)` (`probes/maps_probe.py`).
  Swept x3 (`ext_swept_site1_{1,2,3}`) gave:
  - run 1: GOVERNOR_STOP `hostile_arrival: arrived: AA_Bumbledrone (animal)`, no damage. Not counted; filed
    **TESTENV_BUMBLEDRONE_HARDEN_UNINVITED_BUZZ**.
  - runs 2-3: UNMEASURED, "5 colonists ... 1500 ticks, none washed away". `probes/edge_probe.py` shows moving water on the north
    edge only (14 cells). The river ends in the sea, so there is no downstream edge. SITE; filed
    **TESTENV_RIVERSITE_HARDEN_RIVER_ENDS_AT_SEA** (with the mapIndex bug).
- **Driver error, mine.** `edge_probe.py fresh` returned before the quicktest map was ready. river_site then generated
  concurrently: GenStep "Collection was modified", MapInitializing stuck (`river_site_2_concurrent_mapgen.log`).
  `extension_proof`'s `ensure_playing_map` started `prove_quicktest_world.py`, which hung; I killed it by PID 33504.
- **Site 2.** I redid it properly (`probes/fresh_map.py`: wait for Playing + map_info), then ran `river_site.py`
  (`river_site_3.log`): tile 248, map uid 1, GRID current=8660 fast=3175. It has moving water on 3 edges (N 12, W 29, E 31).
- `extension_proof --live --site river --chains swept` x3 (`ext_swept_{1,2,3}.json`, `.log`): **returns_home PASS 3/3, no restart,
  no GOVERNOR_STOP**. Each run washed 4 of 12 staged colonists off the map.
- Run 2 bruised one: component note "declared river bruises resumed past (the hazard working as shipped)": 82035 health 1 -> 0.94,
  Bruise/Head.
- So the bar is met, with a bruise actually seen and resumed past -> verify pass, closed.

## 5. Restore + teardown
Tier list saved (`ModsConfig.tier_at_teardown.xml`, md5 b1064499); `Player.0207ac8fc2.log` kept. Game killed by PID 30928 (taskkill),
gone. `modset_builder --restore` -> **ee01dae9, 550 active, verified** (`restore.txt`). `./game --why ... down`; bridge released.
JawaBench `companion_profile.json` left as renewed (test, expires 2026-10-15T20:00Z, same campaignSaves).

## 6. Ledger
(pending)
