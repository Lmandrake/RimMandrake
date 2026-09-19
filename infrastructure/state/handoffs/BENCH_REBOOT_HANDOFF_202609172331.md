# BENCH_REBOOT_HANDOFF_202609172331 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609172203`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

**The game is mid-COLD-LOAD on the full 634-mod list (launched ~23:31Z, ~15 min).**
Do not touch the bridge or deploy anything until `Bridge token:` appears in
Player.log. This load is the FIRST TEST of two unverified changes — FireHawk
wing-flap (new custom BodyDef, could break FireHawk pawn-gen) and Pyrelands
density 1.55. Watch the log on arrival: `harvest_log.py`, and specifically that
FireHawk spawns without a BodyDef/RenderTree error. If it errors, rollback is in
the flapping section below.

Also new this session and load-bearing: the **`rimworld-live-review` skill +
`src/RimMandrake/Utils/stage_review.py`** — one Python call clean-stages a biome
for screenshots (kill hostiles, clear, verified-open spaced spawn, face-camera,
midday+signature-weather, save). USE IT for the flapping/density check instead of
hand-driving the bridge. The colony-home-map trick (spawn PlayerColony colonists
on a generated map so it isn't culled when you step time) is what makes stepping
for daylight/drifts possible.

## What the owner should see

- **Pyrelands is NOT check-off-ready for playtest yet.** The blocker: the campaign
  save's Pyrelands tiles are still the donor `ZBiome_Grasslands`, not
  `RM_FE_Pyrelands` (`PYRELANDS_WORLD_SWITCH_1`, still open) — so loading the
  canonical save shows the donor biome, not ours. Everything checked this session
  was on throwaway quicktest maps. The world switch on the campaign save is the
  gate to real playtesting.
- **Density 1.55** — he saw 1.55 look much better ("choked") but never explicitly
  ratified it as final. Awaiting his word.
- **FireHawk flap shipped UNVERIFIED, by BENCH, on his authorization** ("just do
  it yourself, I authorize it") after we found FOUNDRY never actually did it (no
  commit/file/ledger event — that's why the item never closed). He can veto.
- **Barbslinger** — scorpion art approved+wired; the ruled MECHANICS (twin venom
  missiles every few rounds, then pincer assault) are still UNBUILT.

## What is half-done, and where it stops

- **FIREHAWK_FLIGHT_BEHAVIOR_1** (doing) — flap wired + deployed + pushed
  (`4d1f89181`), UNVERIFIED. Files: `UtinniPatches/Defs/ThingDefs_Races/RUT_FireHawkRenderTree.xml`
  (BodyPartGroupDef RUT_FireHawkWing + BodyDef RUT_FireHawkBody + PawnRenderTreeDef
  RUT_FireHawk) and 6 `FireHawk_Body_*`/`FireHawk_Wing_*` textures; RUT_FireHawk
  ThingDef repointed to the new body+renderTree. NEXT: on the live load, confirm
  FireHawk spawns and the wings flap. Known v1 gap: wing drawSize fixed 0.85, so
  baby/juvenile wings render adult-scaled. 🔴 ROLLBACK if FireHawk fails to spawn:
  in `RUT_PyrelandsFauna.xml` revert `<race><body>` to `Bird` and delete the
  `<race><renderTree>` line — back to the static sprite. Then close or re-verify.
- **PYRELANDS_WORLD_SWITCH_1** (ready) — switch the campaign save's Pyrelands
  tiles donor→RM_FE_Pyrelands. NEXT: load canonical save, `jawa/world_tile_set`
  the Pyrelands tiles + `world_commit`, verify read-back. The real playtest gate.
- **PYRELANDS_FAUNA_WIRING_1** (ready) — live def-read of RM_FE_Pyrelands
  wildAnimals should be exactly 13 entries; never confirmed live. NEXT: bridge
  def-read on the running game.
- **PYRELANDS_MECHANICS_1** (done) — burn-line/fire-hawk/furnace-beast behaviour
  never watched running; worth an eyes-on pass.
- **BARBSLINGER_SCORPION_REDESIGN_1** (proposed) — def mechanics unbuilt (see above).
- **PYRELANDS_SOUTH_TOPDOWN_REGEN_1 / PYRELANDS_CREATURE_RERENDER_1** — art done+
  wired+deployed; open pending in-game verify + close.
- **Ashfall "gathers into drifts"** — weather fires + dark overlay confirmed;
  accumulation (RM_FE_Filth_LooseAsh) never proven. NEXT: on a colony-home
  Pyrelands map, force ashfall, step ticks, look for drifts.
- **Config errors** to triage on the load: `RM_FE_Ground_Sand/Gravel/Soil:
  burnedDef is flammable` (biome's own terrain) — cosmetic or broken? unexamined.

## Traps learned

- **Null-workerClass biomes crash ALL worldgen.** 7 RUT biomes shipped
  `implemented=true`+`generatesNaturally=true`+null workerClass → per-tile throw
  in `WorldGenStep_Terrain.BiomeFrom`. Fixed (`generatesNaturally=false`). This
  was likely the long-standing full-list quicktest crash too.
- **A bridge-generated Settlement map is CULLED once you step time** — spawn
  PlayerColony colonists on it (home map) or it vanishes and set_current_map
  refuses "No loaded map has uniqueID N".
- **`jawa/list_pawns` returns `id`, not `thingId`** (thingId is null). Kill
  hostiles via `jawa/damage {thingId:<the id>, damageDef:"Bomb", amount:9999}` —
  `T: Damage To Death` is player-colonist-only. Select by the `hostile` flag, not
  a faction-name guess; sweep to 0 (mechs survive one bomb).
- **`take_screenshot` appends `.png`** (pass a bare name); **`frame_cell_rect`
  alone may not move the camera** (jump first); **a Settlement quicktest arrives
  mid-raid** with 100+ hostiles.
- **`jawa/set_pawn_rotation dir:south lockRotation:true`** faces pawns at the
  camera — essential for art shots.
- **The GeneticRim/VGE worldgen NRE**: on the trimmed 51-mod list, mapgen threw
  `GeneticRim.Core` TypeInitializationException during worldgen; I dropped VGE to
  get a quicktest. UNCERTAIN whether the full 634-list hits it — WATCH THIS LOAD.
All also going to LESSONS_INBOX.md.

## Closed since the last handoff (0)

Nothing closed in this window.

## Filed and still open (0) — the next seat's queue

Nothing filed in this window.

## Commits

```
fc9d9c62c rimflow: sync ledger (VALIDATION_SCRIPT_BACKFILL_1 FOUNDRY note)
4d1f89181 FireHawk: wire wing-flap animation via PawnRenderNodeProperties_Spastic (FIREHAWK_FLIGHT_BEHAVIOR_1)
ccf5d0285 StructureInjectionsSW: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
087b556fa rimflow: sync ledger (VALIDATION_SCRIPT_BACKFILL_1 FOUNDRY note)
c57b3b03a StructureInjectionsRUT: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
a250251ef StarWarsPatches: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
535840f2b rimflow: sync ledger (VALIDATION_SCRIPT_BACKFILL_1 wave note)
aef515fdd SacredGraffiti: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
e1f053fb4 Cuisine: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
36e27e912 RaidRedesigner: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
89b8439e3 UtinniPatches: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
f1dfdf882 SWBestiary: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
b7cacb9e9 LongHunger: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
3c416d58b DesertVehicleReskin: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
7bbf3391c PlantGrowth: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
8690a8bcd rimflow: sync ledger (VALIDATION_SCRIPT_BACKFILL_1 FOUNDRY note)
df99a89e3 BirthHatchDemo: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
aa8ee4e3a WeatherSuite: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
40ce13844 Rites: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
b8ea593a5 LoadTracer: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
c4fa7f413 AshkarrWeatherSuite: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
be2852a6f Doctrine: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
8a88fc66d RimDefDump: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
1c06dcf5c Visibility: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
4696bd32c AshkarrLandmarkArt: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
c19799667 PlanetPresetPrime: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
8738e2eb9 rimflow: sync ledger/queue for MODCHECK_STATUS_ORPHANED_BY_RENAME_1, VALIDATION_SCRIPT_BACKFILL_1, GRAFFITI_VARIANT_COUNTS_1
817cdb37d LanternDeeps: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
f05a72988 Graffiti: add one new Scratches/TallyMarks variant, two new WarningGlyph variants
d0b02d0be Oracle: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
74130acaf EmpirePursuit: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
9f23d9845 AshkarrInhabited: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
1c3fcf7d3 RestrainingBolts: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
df0d9d1b4 StrandedQuest: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
1d49ca2fa JawaRules: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
33d5d1ece KotORBandolierNorthFix: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
f145b6587 AshkarrFlora: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
bfadfd5b9 MenuShell: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
14a8a0080 AftermathRites: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
61141c531 JawaVoice: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
868452fa4 MandrakePatches: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
e6ae928f5 IshkoDarkLandmarks: add validation.py (VALIDATION_SCRIPT_BACKFILL_1)
1e30d7d1d New skill: rimworld-live-review + stage_review.py helper
e4481b066 modcheck: add validation.py for RustChrome (first slice of the 63-mod backfill)
b110a7a2d modcheck: add rename-key/forget-key verbs; retire dead FluidCanals key
363098d4d rimflow: sync queue views
b003ac6ef rimflow: sync ledger (DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave note)
058e113c2 review: mark 9 unreviewed validation.py suites CLEAN (wave)
d28bf3edf rimflow: sync ledger/queue views
8dac88fec Merge remote-tracking branch 'origin/main'
08cf0cc10 chore(sync): FOUNDRY 2026-09-17 — codebase_health.html, codebase_health.json, codebase_health_artifact.html and 2 more
ce29736c5 artpipe: terminate all Pyrelands jobs from failed/
b765afbfb chore(sync): laptop 2026-09-17T15:21:32-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
fc16d5507 Twi'lek: remove the 3 trope genes from the species (first slice)
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running; BRIDGE NOT PROBED — no port found in the environment or in Player.log, so LOADING here is a DEFAULT, not a reading.)
- recorded  : LOADING
- Bridge: FREE    since 2026-09-17T23:31:00Z

Uncommitted (say for each whether it is yours or another seat's):

```
M Transient/codebase_health.html
 M Transient/codebase_health.json
 M Transient/codebase_health_artifact.html
 M infrastructure/dashboards/hub/data/health.json
 M infrastructure/state/codebase_health_last.json
 M infrastructure/state/ledger/events.jsonl
 M infrastructure/state/queue/BENCH.md
 M infrastructure/state/queue/FOUNDRY.md
?? defs.sqlite
?? deployed/config/ModsConfig.before-tier-oracle.xml
?? deployed/config/ModsConfig.before-tier-stagedlore.xml
?? deployed/config/ModsConfig.before-tier-warlab.xml
?? infrastructure/artpipe/active/rotscythe_v1_south.json
?? infrastructure/artpipe/active/twistingthornweed_v1.json
?? infrastructure/artpipe/active/wastewing_v1_north.json
?? infrastructure/artpipe/daemon_run_20260916_bench_restart.log
?? infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_closed.json
?? infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_closed.manifest.json
?? infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_open.json
?? infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_open.manifest.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_east.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_east.manifest.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_north.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_north.manifest.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_south.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v3_south.manifest.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_east.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_east.manifest.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_north.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_north.manifest.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_south.json
?? infrastructure/artpipe/done/pyrelands_barbslinger_v4_south.manifest.json
?? infrastructure/artpipe/done/pyrelands_boomsnake_v3_north.json
?? infrastructure/artpipe/done/pyrelands_boomsnake_v3_north.manifest.json
?? infrastructure/artpipe/done/pyrelands_gizka_dino_v5_north.json
?? infrastructure/artpipe/done/pyrelands_gizka_dino_v5_north.manifest.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v3_north.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v3_north.manifest.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v3_south.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v3_south.manifest.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_east.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_east.manifest.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_north.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_north.manifest.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_south.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4_south.manifest.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4b_east.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4b_east.manifest.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4b_south.json
?? infrastructure/artpipe/done/pyrelands_mantistanis_v4b_south.manifest.json
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_east.json
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_east.manifest.json
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_north.json
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_north.manifest.json
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_south.json
?? infrastructure/artpipe/done/pyrelands_nuna_female_v1_south.manifest.json
?? infrastructure/artpipe/failed/anooba_toyfig_b_east.manifest.json
?? infrastructure/artpipe/failed/dragonsnake_toyfig_b_east.manifest.json
?? infrastructure/artpipe/failed/tentacular_toyfig_b_east.manifest.json
?? infrastructure/artpipe/failed/terramorph_toyfig_b_east.manifest.json
?? infrastructure/artpipe/failed/wyyyschokk_toyfig_b_east.manifest.json
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml
?? src/RimStarWars/MSEDroidFix/validation.py
```

