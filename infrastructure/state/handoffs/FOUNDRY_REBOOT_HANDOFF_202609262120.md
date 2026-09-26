# FOUNDRY_REBOOT_HANDOFF_202609262120 — READ FIRST on wake

Follows `FOUNDRY_REBOOT_HANDOFF_202609261128`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

Never assume bridge/game unavailability without checking. This whole wave ran on the
default assumption that live verification was off the table ("no bridge access this
pass"), stated to every subagent without once running `rimflow bridge who`. The owner
corrected it directly (*"Never assume you can't have Bridge. Always check for it before
assuming you can't."*), and the very next check found bridge FREE — the only real
blocker was the game being down, which is FOUNDRY's own to fix (a reboot needs no
asking). The correction paid off immediately: the live load caught a real defect
(`EXPLOSIVE_PLANT_GROWTH_1`'s charge clock never fired) and an undeployed GenStep
(Scarlands' grave-ward) that static verification alone would never have surfaced. Filed
to memory as `never-assume-bridge-unavailable`; check `rimflow bridge who` + `rimflow
game` before ANY brief says "no live verification this pass."

## What the owner should see

- **`ModsConfig.xml` (his live 629-mod list) was edited this window**: added the new
  `mandrake.rm.explosivegrowth` mod and reordered `mandrake.rut.plantgrowth` to load
  after it. Deliberate, load-order-only, no mod removed — flagging per standing
  practice on any live-list edit.
- **`EXPLOSIVE_PLANT_GROWTH_1` shipped real approximations he may want to weigh in on**,
  not just engineering placeholders: RUPTURE reuses vanilla toxic gas (no "red gas" exists)
  and spawns Alpha Animals' `AA_RedGoo`/`AA_OcularJelly` rather than bespoke creatures;
  mutation hediffs reuse the Contagion's `RM_Unfinished*` limbs. All numeric tuning
  (charge rates, radii, chances) is invented and Mod-Settings-adjustable, not ruled.
- **Two pre-existing bugs found, not fixed, correctly left alone as out of scope**: the
  `PlantGrowth` mod's slow-growth exemption list matches the bare name `PoisonForest`,
  never `RUT_PoisonForest`/`RM_PoisonForest`, so it silently does nothing; and
  `RUT_ExtremeDesert` (the deep desert) still gets ×4 ambient growth against its own
  frozen sheet's explicit "no fast growth" hard ban. Neither is this session's item to
  fix blind — flagging so they don't get re-discovered as a surprise.
- Everything else this wave (4 biome mechanics kits, the artpipe console redesign, the
  explosive-growth engine) is FOUNDRY-tier build/fix work within already-ruled specs —
  nothing here needed or got a design call that wasn't already his.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `EXPLOSIVE_PLANT_GROWTH_1` — doing; full engine built (soak tracker, ×10 wet-biome band,
  visual charge/tell system, all 6 terminal-moment handlers, 111/135 roster rows wired,
  Greentide M10 wired to a real grid), a live-test-found charge-clock bug fixed
  (`537bc7d26`) but not yet live-reconfirmed. NEXT: re-run the debug-action sequence
  (soak → wait >250 ticks → confirm `charging` climbs → fire each of the 6 terminal
  moments) on a warm/fertile map, not an ice biome, then test the ×10 wet-biome band on
  an actual Greentide/Miasma/FeverWood map.
- `SCARLANDS_MECHANICS_2` — doing; built the Sentinel grave-ward GenStep+placement
  (`f12a1387e`); live-verify found its def had never actually been deployed to the game
  despite the mod being active — deployed now (`0072794d4`). NEXT: restart to pick up the
  def, then confirm it scatters and faction-sets correctly on a `RUT_Scarlands` map.
- `MIASMA_MECHANICS_1` — doing; fixed a real save/load bug (salinity array never Scribed)
  and repaired a shared-tree DLL break another agent's commit caused. NEXT: a live
  save→reload cycle to confirm the salt-line position survives — not attempted, ran out
  of session budget.
- `GREENTIDE_MECHANICS_2` — doing; confirmed 11/12 mechanics already shipped, M10's
  grazing-suppression hook now wired to a real grid (via `EXPLOSIVE_PLANT_GROWTH_1`'s
  agent). NEXT: live-confirm a grazing pawn actually decrements suppression on a soaked,
  charging plant.
- `SUMP_MECHANICS_1` / `SUMP_TAR_NASTINESS_1` / `SUMP_WALKWAYS_1` — doing; built the
  lottery-trap disarm interaction (WorkGiver+JobDriver) and fixed 2 dangling recipe
  sources. NEXT: confirm the disarm job is actually offered and completable on a real
  lottery trap — live-test on the cold load found the defs correctly registered but did
  not run a full arm-to-trigger cycle (judged too expensive for the session).
- `MODCHECK_SUITE_CORRECTIONS_1` — doing; fixed a `wait_ticks()` root cause (trusted a
  bridge call that silently under-delivers), a bad faction assumption, a wrong C#
  parameter name, and a numeric/string comparison bug; filed `PRIMITIVEWELL_DEAD_DEFNAME_1`
  for a genuine content defect found along the way. NEXT: a modcheck re-run on the min16
  list covering Antiquities/ShipMemory/Aftermath/ResearchRetag/RimProperty/
  StructureInjections to confirm the fixes live.
- `COMMISSION_LEDGER_CLEANUP_1` — doing; resolved 15 of 22 previously-contended
  commission slugs (verified against live XML, not claims), filed
  `TERMINAL_SEAS_FLOOR_DRESSING_1` for 5 sea-floor flora slugs. NEXT: `nightside_ice` (6
  slugs) still needs real design/authoring, not just verification.
- `DIRTY_CODE_REVIEW_STANDING_LOOP_1` — doing (standing loop); wave 15 reviewed and
  marked clean 15 more files, CLEAN tally now 3159/188 dirty/635 never-entered. NEXT:
  continue the vein list left in the item's own note — RUT_CavernsFlora,
  RUT_PollutedFlora, RUT_ScarlandsFlora, RUT_Emberscythe, RUT_Karrathil, RUT_Karrobel,
  RUT_MortuaryCrawler, RUT_PropaneLakeFauna, RUT_FleetFlier, RUT_Tarred_Thoughts.
- `FEVERWOOD_TWO_FRONT_LURE_TUNING_1` — doing; built the threat-points Mod Settings
  sliders and a lock-once-triggered toggle. NEXT: get an owner ruling on the two
  explicitly-skipped points (the prey-quality gate, the free-tier second raider), then
  the item can close.
- `KYBER_TRADE_PLOT_1` — blocked, correctly (block reason itself was corrected this
  window — the old one cited infra that has since been built). NEXT: build the
  live-injection flip that actually fires the already-built quest incidents from real
  sales; needs bridge access a future pass should just check for, not assume absent.
- `MOD_OPTIONS_RETROFIT_1` — blocked; retrofitted 3 more mods (ShokkweaveEconomy,
  EggReckoning, WildsteamEggBounty) found missing Mod Settings, corrected 2 stale lines
  in the item's own file. NEXT: full live verification across the ~52-mod set — this
  window's cold load touched some of them incidentally but did not run the dedicated
  sweep.
- `SARLACC_HABITAT_BUILD_1` — blocked; built Fork 6's real breach-flood terrain effect.
  NEXT: live bridge verify, the pocket-map dungeon interior, world placement, and real
  art all remain, in that rough order.
- `CRYPTOFORGE_HARVEST_RETIRE_1` — blocked; confirmed step 5 (fauna ruling) already done,
  corrected the item's own prop-count claim (verified 21, not 18/22). NEXT: step 1 (a
  21-sprite art pass) and step 4 (needs a cold-load ModsConfig removal + resave) remain.
- `ASSAILANT_DUNGEON_BUILD_1` — blocked; re-verified the block is still real. NEXT:
  genuinely needs a joint BENCH+owner session (KCSG authoring, turret art, reveal
  dialogue) — not a solo FOUNDRY pass, don't re-attempt one blind.
- `PLOT_MECHANISM_MODS_WAVE_1` — blocked; re-verified, found a real fix for whoever
  builds it (seam B needs to retarget from `TryGenerateRaidInfo` to a postfix on
  `TryResolveRaidFaction`), confirmed `OracleClient`'s `claude -p` transport is already
  built. NEXT: still needs 13-faction lore content (design/Fable work) before Part 1 can
  be built at all.
- `FAUNA_TOLERANCE_NORMALIZATION_1` — doing, BLOCKED; fixed one real drift
  (`RSW_Korrum`'s comfy band), re-pinned 480 animals with zero regressions. NEXT: do NOT
  regenerate `cast_assignment.csv` yet — several biomes have moved to their `RM_` tier
  defName ahead of the frozen tiles CSV, so a regen now would misjoin them and silently
  drop their animals from Law 5. Wait for the biome-mod-split migration to settle first.

## Traps learned

- Never assume bridge/game unavailability — check `rimflow bridge who` / `rimflow game`
  before telling any subagent "no live verification this pass" (filed: memory
  `never-assume-bridge-unavailable`, see this handoff's top section).
- `TestContext.wait_ticks()` in the modcheck suite trusted `rimworld/step_game_ticks`'s
  own reported count, but that bridge call silently under-delivers ticks under load —
  caused two false suite FAILs. Fix loops in verified-clock chunks, never trust the
  call's self-report (see: `MODCHECK_SUITE_CORRECTIONS_1`, commit `8e4efd343`).
- Three sibling agents editing the same shared `RM_EnvironmentalHazards.csproj`/assembly
  concurrently produced two near-misses (a `.csproj` `<Compile>` entry committed without
  its source file) — both self-healed via the `DLL_SOURCE_STAMP_GUARD_1` push hook and a
  private detached worktree rebuild, no damage, but a real concurrency hotspot right now
  (see: Greentide/Miasma/Scarlands commits this window).
- A GenStepDef can be committed and its mod stay "active" while the def itself was never
  actually deployed to the live game — static/git state is not deploy state; a live load
  is the only way this surfaces (see: `SCARLANDS_MECHANICS_2` this handoff).
- A charge/state-machine bug (soaked-but-dormant plants falling into the decay branch)
  produced a symptom (`charging` stuck at 0) indistinguishable by inspection from several
  other plausible causes; only a live debug-action test with an explicit tick-count
  budget caught it (see: `EXPLOSIVE_PLANT_GROWTH_1`, commit `537bc7d26`).

## Closed since the last handoff (7)

- `GREYSEA_FLOOR_FORMATIONS_1` — 4b6e4c703a8e298bc9d6e70c1208a1701b6cc5f2
- `GREYSEA_SALT_SNOW_WEATHER_1` — 4b6e4c703a8e298bc9d6e70c1208a1701b6cc5f2
- `GREYSEA_CRYSTAL_FLORA_1` — 4b6e4c703a8e298bc9d6e70c1208a1701b6cc5f2
- `GREYSEA_SESSILE_LAYER_1` — 4b6e4c703a8e298bc9d6e70c1208a1701b6cc5f2
- `GREYSEA_SALT_CUISINE_1` — 4b6e4c703a8e298bc9d6e70c1208a1701b6cc5f2
- `GREYSEA_SHORE_MUTATOR_SPECIFICS_1` — 4b6e4c703a8e298bc9d6e70c1208a1701b6cc5f2
- `GREYSEA_BRINE_POOL_DEFENCE_1` — 4b6e4c703a8e298bc9d6e70c1208a1701b6cc5f2

## Filed and still open (14) — the next seat's queue

- `TERMINAL_SEAS_FLOOR_DRESSING_1` — 5 owed terminal-seas floor/flora slugs: Grey pillar-mason, both salt-rimed-blade-flora variants, Twilight mold-mat-roof, Twilight condensate-drinker
- `LANTERNDEEPS_TIER_COLLISION_1` — Live mandrake.rut.lanterndeeps exists ONLY in the game folder with no repo copy, and the RM successor deploys to the same folder name - deploying it w
- `PRIMITIVEWELL_DEAD_DEFNAME_1` — PrimitiveWell defName referenced by 4 Lua plan templates does not exist in any loaded mod or DLC
- `BIOME_DEFNAME_MIGRATION_WAVE_1` — Three biomes renamed 2026-09-26 carry defNames that no longer match their labels: RM_NightsideIce/RM_PoisonForest/RM_Wasteland move to Sleeping Ice, C
- `PROPANELAKE_ANIMALDENSITY_ZERO_1` — RM_PropaneLake and RUT_PropaneLake leave animalDensity UNSET so it defaults to 0f - their 6-animal floor roster can never spawn, proven from the decom
- `GREYSEA_ANCHOR_CREATURES_1` — Grey Deep's two unbuilt anchors (pillar-mason, ossuary shrimp) plus the AA_Aerofleet replacement - the sheet's whole image rests on creatures that hav
- `SUUSH_CAULDRON_DRIFTER_1` — The Suush: a docile tamable floating sphere with gathering tentacles that feeds on the Cauldron's roiling chemistry and detonates when shot
- `SEA_FISHABLES_ALIVE_IN_DEPTHS_1` — Every fishable in EVERY sea owes a living creature swimming the floor map, not just a catch item - owner ruling 2026-09-26
- `BIOME_CONFIG_ERROR_TRIAGE_1` — Triage the per-biome config errors the load-proof wave exposed against a zero baseline: floodedcanyon 53 distinct, webwork 30, thesump 14, contagion a
- `GREYSEA_BRINE_ELDERS_1` — The Brine Elders: colossal branching salt-crystal organisms with area discharges, geological memory, a novelty-only trade economy and one-of-each mill
- `SHARED_SYNC_DROPS_PEER_COMMITS_1` — shared_sync.py silently drops a peer commit made during its run: reset --keep moves HEAD past work that was never in its todo set, and origin/main..HE
- `ARTPIPE_DOWNSCALE_INSTEAD_OF_REJECT_1` — Downscale the 1254x1254 worker output instead of failing size_mismatch
- `ARTPIPE_METER_WINDOW_REMAP_1` — Detector.note_meters reads the wrong meter window since the plan upgrade — weekly backstop is dead
- `ARTPIPE_WORKER_AUTH_STALENESS_1` — Stale worker-home auth.json capped real artpipe concurrency at 3 via refresh-token races

## Commits

```
a8c975a3d EXPLOSIVE_PLANT_GROWTH_1: record the live verify, the charge-clock fix, owed re-verify
537bc7d26 ExplosiveGrowth: a soaked plant that cannot grow holds its charge, not loses it
0072794d4 Live-verify ExplosiveGrowth + Scarlands/Sump/Miasma fixes: soak/roster/biome-gate confirmed, charge-start not observed
4f841b309 Ledger: three artpipe concurrency items from the measurement pass
bef894a02 Measure artpipe concurrency on the new plan: 8 sustainable, not 3
f4d3f6e00 shared_sync.py can silently drop a peer's commit — record the race
22071205e Grey Sea offline build wave: the pass report
6a8e7ce1a Ledger: the Grey Sea offline build wave — six items closed, three noted partial
4b6e4c703 Grey Sea: touch a brine pool and the salt closes over you
6ab38fd77 Grey Sea: the kelp and the chimney vine can join the roster now their terrain exists
78097f340 Grey Sea: carve the pool, stand the Elder in it, and run the brine downhill
2df65888c Grey Sea coloured salts get something to be an ingredient for
511aaaccc Ledger: Scald art queue returned in-session; overlay tiles held
491f980ef Scald report: the art queue came back inside the session; overlay tiles held for a look
0c3af95ed The shulla catch's missing small-pile variant, refiled and landed
2b6ec6a30 Real art for the Scald's seven new floor residents
84a705e3a Grey Sea: ship the placeholder art so nothing in this wave renders magenta
468c0ec77 Ledger: Scald steam overlay + vent-flash build note
20fc0530b Scald offline build wave: the pass report
dd528abf4 Scald steam: custom overlay route and the map-wide vent flash
... 89 more: git log --oneline 3c62e16ba..HEAD
```

## Game / bridge / tree state at wrap

- running   : NOT RUNNING   (tasklist.exe lists no RimWorldWin64)
- recorded  : DOWN
- Bridge: for     Scald round: deploy TerminalBiomes+EnvironmentalHazards+LuminousPigment, minimal-list quicktest RM_TheScald, harvest

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/codebase_health.html   ambient -- code_review_status.py's automatic health-dashboard rebuild, triggered by this window's mark-clean/list calls; regenerable, not hand-authored
 M Transient/codebase_health.json   ambient -- code_review_status.py's automatic health-dashboard rebuild, triggered by this window's mark-clean/list calls; regenerable, not hand-authored
 M Transient/codebase_health_artifact.html   ambient -- code_review_status.py's automatic health-dashboard rebuild, triggered by this window's mark-clean/list calls; regenerable, not hand-authored
 M Transient/project_maturity_dashboard.html   ambient -- code_review_status.py's automatic health-dashboard rebuild, triggered by this window's mark-clean/list calls; regenerable, not hand-authored
 M Transient/project_maturity_dashboard.json   ambient -- code_review_status.py's automatic health-dashboard rebuild, triggered by this window's mark-clean/list calls; regenerable, not hand-authored
 M deployed/config/ModsConfig.before-tier-bridge.xml   BENCH -- backup snapshot from BENCH's live Scald-round deploy, in progress on the bridge at handoff time
 D infrastructure/artpipe/_artsrc/lockjaw_improve_a_r7/lockjaw_improve_a_r7.png   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/_artsrc/lockjaw_improve_b_r7/lockjaw_improve_b_r7.png   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/active/desertportb_feralgrazer_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/active/desertportb_feralnerf_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/active/desertportb_feralnerf_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/art_status.html   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/art_status.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_graniteslug_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_graniteslug_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_graniteslug_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_grank_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_grank_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_grank_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_greaterkraytdragon_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_greaterkraytdragon_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_horax_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_horax_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_horax_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_jakobeast_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_jakobeast_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_jakobeast_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_kowakianmonkeylizard_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_kraytdragon_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_kraytdragon_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_kraytdragon_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_krykna_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_krykna_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_krykna_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_mossbeetle_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_mossbeetle_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_mossbeetle_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_mossbeetlepupa_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_mossbeetlepupa_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_mossbeetlepupa_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_nerf_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_nerf_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_nerf_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_pikobis_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_pikobis_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/done/desertportb_plant_bloddle.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Brindeth_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Brommet_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Brommet_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Brommet_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Dorvel_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Dredgel_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Dredgel_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Dredgel_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Gulveth_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Gulveth_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Gulveth_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Korveth_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Mirrelin_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Pallick_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Skarrid_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Skarrid_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Skarrid_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Skellarn_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Skellarn_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Skellarn_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Skelver_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Soffeth_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_SumpMouse_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_SumpMouse_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_SumpMouse_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_ThrummelBroodmother_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_ThrummelBroodmother_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_ThrummelBroodmother_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_ThrummelWarden_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_ThrummelWarden_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_ThrummelWarden_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Thrummel_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Thrummel_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Thrummel_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Tolleth_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RM_Velloch_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RSW_Ashworm_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RSW_Ashworm_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RSW_Ashworm_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RSW_Barbthorn_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RSW_Barbthorn_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RSW_Barbthorn_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RSW_EmberCarpet.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RSW_Scrubgrass.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RSW_Spinerat_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RSW_Spinerat_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RSW_Spinerat_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RSW_Sporemass_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RSW_Sporemass_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RSW_Sporemass_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RSW_Sporepaw_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RSW_Sporepaw_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RSW_Sporepaw_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RSW_Starvine.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RSW_Stoneback_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RSW_Stoneback_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RSW_Stoneback_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/RSW_Whirlbloom.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/bluedesert_chimeglobe.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/bluedesert_chimeglobe_b.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/bluedesert_dorrak_dessicated.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/bluedesert_glassfern.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/bluedesert_glassfern_b.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/bluedesert_glassfern_c.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/bluedesert_krissek_dessicated.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/bluedesert_krissek_halo_mote.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/bluedesert_palefloss.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/bluedesert_palefloss_b.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/bluedesert_palefloss_c.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/deepfire_crowncarpet_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/deepfire_crowncarpet_b.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/deepfire_pigmentjar_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/deepfire_pigmentjar_b.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_graniteslug_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_graniteslug_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_graniteslug_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_grank_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_grank_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_grank_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_greaterkraytdragon_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_greaterkraytdragon_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_greaterkraytdragon_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_horax_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_horax_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_horax_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_jakobeast_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_jakobeast_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_jakobeast_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_kowakianmonkeylizard_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_kraytdragon_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_kraytdragon_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_kraytdragon_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_krykna_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_krykna_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_krykna_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_mossbeetle_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_mossbeetle_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_mossbeetle_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_mossbeetlepupa_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_mossbeetlepupa_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_mossbeetlepupa_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_nerf_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_nerf_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_nerf_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_pikobis_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_pikobis_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_pikobis_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_plant_bloddle.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_plant_chakroot_wild.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_plant_hubbagourd_wild.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_plant_nysyllin_wild.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_porg_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_porg_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_porg_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_qormot_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_qormot_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_qormot_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_runyip_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_runyip_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_runyip_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_shaak_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_shaak_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_shaak_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_strill_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_strill_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_strill_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_teemuss_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_teemuss_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_teemuss_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_uvak_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_uvak_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_uvak_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_varactyl_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_varactyl_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_varactyl_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_voorpak_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_voorpak_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_voorpak_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_vulptex_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_vulptex_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_vulptex_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_warwyrm_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_warwyrm_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_warwyrm_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_whisperbird_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_whisperbird_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_whisperbird_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_zeer_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_zeer_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/desertportb_zeer_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_brathek_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_brathek_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_brathek_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_chellow_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_chellow_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_chellow_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_drommath_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_drommath_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_drommath_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_gorrameth_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_gorrameth_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_gorrameth_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_grolth_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_grolth_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_grolth_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_lommerel_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_lommerel_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_lommerel_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_murrelith_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_murrelith_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_murrelith_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_nemmel_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_nemmel_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_nemmel_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_ollareth_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_ollareth_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_ollareth_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_plant_ammeth.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_plant_cistrel.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_plant_claithe.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_plant_corvath.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_plant_halquin.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_plant_maulith.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_plant_nubrith.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_plant_plennith.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_plant_seepril.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_plant_skethral.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_plant_skimmel.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_plant_sodderel.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_plant_thulvane.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_plant_tullick.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_plant_varnoth.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_plant_verrow.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_plant_wanlith.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_silloch_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_silloch_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_silloch_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_skellick_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_skellick_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_skellick_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_thavrik_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_thavrik_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_thavrik_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_vaulm_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_vaulm_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/feverwood_vaulm_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/glyph_animalpersonhood.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/glyph_blindsight.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/glyph_bloodfeeding.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/glyph_cannibal.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/glyph_collectivist.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/glyph_darkness.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/glyph_femalesupremacy.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/glyph_fleshpurity.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/glyph_guilty.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/glyph_highlife.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/glyph_humanprimacy.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/glyph_individualist.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/glyph_inhuman.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/glyph_loyalist.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/glyph_malesupremacy.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/glyph_natureprimacy.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/glyph_nudism.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/glyph_painisvirtue.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/glyph_proselytizer.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/glyph_raider.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/glyph_rancher.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/glyph_ritualist.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/glyph_shipborn.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/glyph_supremacist.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/glyph_transhumanist.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/glyph_treeconnection.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/glyph_tunneler.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/graffiti_crossout.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/graffiti_paste_flyer_p1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/graffiti_paste_flyer_p2.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/graffiti_paste_wanted_p1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/graffiti_paste_wanted_p2.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/graffiti_sigilframe_dripframe.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/graffiti_sigilframe_halo.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/graffiti_sigilframe_stencilbox.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/graffiti_stencil_crown.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/graffiti_stencil_fist.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/graffiti_stencil_gear.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/graffiti_tag_a_p1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/graffiti_tag_a_p2.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/graffiti_tag_b_p1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/graffiti_tag_b_p2.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/graffiti_tag_c_p1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/graffiti_tag_c_p2.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/graffiti_throwup_a_p1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/graffiti_throwup_a_p2.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/graffiti_throwup_b_p1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/graffiti_throwup_b_p2.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/miasma_aphreen.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/miasma_braskeen_closed.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/miasma_braskeen_open.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/miasma_brelloch.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/miasma_ilbareen_dead.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/miasma_ilbareen_live.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/miasma_immarel.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/miasma_ismerrow_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/miasma_ismerrow_b.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/miasma_ismerrow_c.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/miasma_ismerrow_d.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/miasma_nemreth.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/miasma_nyssolet.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/miasma_ollamane.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/miasma_ommolyn.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/miasma_pallasheen.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/miasma_quennath.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/miasma_sarrash.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/miasma_thessamor.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/miasma_thrannock.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/miasma_ullavess.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/miasma_vellamine.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/miasma_velluric.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/miasma_wessaline.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rm_brakkel_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rm_brunnock_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rm_cundral_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rm_gorbeleth_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rm_kaddrath_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rm_maddrick_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rm_mirrelbole_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rm_mourvel_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rm_phorrik_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rm_quathis_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rm_sarnstilt_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rm_sarquin_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rm_thalquith_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rm_tumbel_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rm_vurmeloth_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rm_wollick_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rm_zhorrel_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rmdusthusk_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rmdusthusk_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rmdusthusk_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rmleachmoss_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rmmirrorgiant_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rmmirrorgiant_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rmmirrorgiant_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rmtitanoslime_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rmtitanoslime_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rmtitanoslime_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rmvenomvine_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rot_brogg_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rot_brogg_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rot_brogg_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rot_brullith_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rot_brullith_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rot_brullith_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rot_illoth_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rot_illoth_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rot_illoth_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rot_skerrith_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rot_skerrith_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rot_skerrith_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rot_thozzik_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rot_thozzik_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rot_thozzik_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rot_thozzikqueen_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rot_thozzikqueen_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rot_thozzikqueen_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rsw_graffiti_stencil_imperialcog.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rsw_zakkro_dessicated_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rsw_zakkro_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rsw_zakkro_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rsw_zakkro_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rsw_zakkroegg_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rswrawultracactus_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rswultracactus_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rut_grellbush.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rut_grellspine.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rut_vhessk_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rut_vhessk_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rut_vhessk_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rut_wildhealroot.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutbloomcrop_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutbrinebattery_v2_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutbrinebattery_v2_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutbrinebattery_v2_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutdarkcrust_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutdeltaloam_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutemperorvulture_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutemperorvulture_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutemperorvulture_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutfleetflier_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutfleetflier_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutfleetflier_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutfuzz_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutglower_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutglowercrust_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutkarrathil_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutkarrobel_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutmortuarycrawler_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutmortuarycrawler_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutmortuarycrawler_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutradiothermal_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutradiothermal_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutradiothermal_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutsealedsleeper_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutsealedsleeper_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutsealedsleeper_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutslimegrazer_v2_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutslimegrazer_v2_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutslimegrazer_v2_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutstaggerseed_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutstaggerseeddish_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutvwake_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutvwake_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutvwake_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutwelcomeblanket_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/rutyearningfruit_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/webwork_anchor.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/webwork_gutter.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/webwork_plant_brennoth.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/webwork_plant_brimlock.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/webwork_plant_dulloth.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/webwork_plant_fellome.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/webwork_plant_grennick.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/webwork_plant_kessaroth.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/webwork_plant_kollavane.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/webwork_plant_norrveth.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/webwork_plant_pellareth.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/webwork_plant_ruddreth.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/webwork_plant_sellith.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/webwork_plant_sorrivel.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/webwork_plant_tavrosk.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/webwork_plant_threllick.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/webwork_plant_varrisk.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/webwork_plant_vessark.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/webwork_web.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones2_bladderfruit.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones2_bladderquill.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones2_burrak_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones2_burrak_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones2_burrak_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones2_dewblade.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones2_dewgourd.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones2_dewgourdfruit.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones2_dripfringe.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones2_gorrask_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones2_gorrask_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones2_gorrask_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones2_kirruk_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones2_kirruk_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones2_kirruk_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones2_mirrik_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones2_mirrik_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones2_mirrik_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones2_rockfinger.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones2_salvecomb.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones2_seepsalt.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones2_shadefern.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones2_sillik_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones2_sillik_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones2_sillik_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones2_ssurr_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones2_ssurr_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones2_ssurr_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones2_steamfrond.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones2_tirbak_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones2_tirbak_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones2_tirbak_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones2_vellak_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones2_vellak_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones2_vellak_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones2_verdimoss.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones2_vhakk_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones2_vhakk_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones2_vhakk_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones2_weepmat.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones_huldu_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones_huldu_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones_huldu_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones_ivvol_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones_ivvol_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones_ivvol_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones_karrek_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones_karrek_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones_karrek_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones_loomu_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones_loomu_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones_loomu_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones_murrin_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones_murrin_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones_murrin_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones_skarrin_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones_skarrin_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones_skarrin_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones_vhorrin_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones_vhorrin_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones_vhorrin_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones_vizhik_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones_vizhik_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 D infrastructure/artpipe/pending/weepingstones_vizhik_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/registry.jsonl   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/artpipe/throughput.jsonl   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
 M infrastructure/dashboards/hub/data/artsheets.json   ambient -- code_review_status.py's automatic health-dashboard rebuild, triggered by this window's mark-clean/list calls; regenerable, not hand-authored
 M infrastructure/dashboards/hub/data/health.json   ambient -- code_review_status.py's automatic health-dashboard rebuild, triggered by this window's mark-clean/list calls; regenerable, not hand-authored
 M infrastructure/dashboards/hub/data/maturity.json   ambient -- code_review_status.py's automatic health-dashboard rebuild, triggered by this window's mark-clean/list calls; regenerable, not hand-authored
 M infrastructure/dashboards/hub/data/publish_ready.json   ambient -- code_review_status.py's automatic health-dashboard rebuild, triggered by this window's mark-clean/list calls; regenerable, not hand-authored
 M infrastructure/state/codebase_health_last.json   ambient -- code_review_status.py's automatic health-dashboard rebuild, triggered by this window's mark-clean/list calls; regenerable, not hand-authored
 M infrastructure/state/ledger/events/BENCH.jsonl   unknown -- not traced this window; investigate before deploying or discarding
 M infrastructure/state/ledger/events/OWNER.jsonl   unknown -- not traced this window; investigate before deploying or discarding
 M infrastructure/state/queue/BENCH.md   ambient -- rimflow render's derived queue view, regenerated by this window's own rimflow calls; not hand-edited
 M infrastructure/state/queue/FOUNDRY.md   ambient -- rimflow render's derived queue view, regenerated by this window's own rimflow calls; not hand-edited
 M skills/rimworld-debug-testing/SKILL.md   unknown -- not touched by FOUNDRY this window; pre-existing dirty state or another session's skill-curation edit
 M skills/rimworld-sprite-facings/SKILL.md   unknown -- not touched by FOUNDRY this window; pre-existing dirty state or another session's skill-curation edit
 M src/RimMandrake/CreatureBehaviors/Assemblies/RimMandrake.CreatureBehaviors.dll   unknown -- not traced to a FOUNDRY commit this window; likely a concurrent agent's build/deploy byproduct -- verify dll_source_stamp before any deploy
 M src/RimMandrake/Greentide/Assemblies/RimMandrake.Greentide.dll   unknown -- not traced to a FOUNDRY commit this window; likely a concurrent agent's build/deploy byproduct -- verify dll_source_stamp before any deploy
?? "D:\\Luke\\dev\\Rimworld\\Transient\\eg_check_state.py"   unknown -- not traced this window; investigate before deploying or discarding
?? deployed/config/ModsConfig.before-tier-firehawk.xml   unknown -- not traced this window; investigate before deploying or discarding
?? deployed/config/ModsConfig.before-tier-leaningscrub.xml   unknown -- not traced this window; investigate before deploying or discarding
?? deployed/config/ModsConfig.before-tier-proof_bluedesert.xml   unknown -- not traced this window; investigate before deploying or discarding
?? deployed/config/ModsConfig.before-tier-proof_contagion.xml   unknown -- not traced this window; investigate before deploying or discarding
?? deployed/config/ModsConfig.before-tier-proof_feverwood.xml   unknown -- not traced this window; investigate before deploying or discarding
?? deployed/config/ModsConfig.before-tier-proof_floodedcanyon.xml   unknown -- not traced this window; investigate before deploying or discarding
?? deployed/config/ModsConfig.before-tier-proof_forsakencrags.xml   unknown -- not traced this window; investigate before deploying or discarding
?? deployed/config/ModsConfig.before-tier-proof_gelatinousslime.xml   unknown -- not traced this window; investigate before deploying or discarding
?? deployed/config/ModsConfig.before-tier-proof_greentide.xml   unknown -- not traced this window; investigate before deploying or discarding
?? deployed/config/ModsConfig.before-tier-proof_leaningscrub.xml   unknown -- not traced this window; investigate before deploying or discarding
?? deployed/config/ModsConfig.before-tier-proof_longshade.xml   unknown -- not traced this window; investigate before deploying or discarding
?? deployed/config/ModsConfig.before-tier-proof_miasma.xml   unknown -- not traced this window; investigate before deploying or discarding
?? deployed/config/ModsConfig.before-tier-proof_nightsideice.xml   unknown -- not traced this window; investigate before deploying or discarding
?? deployed/config/ModsConfig.before-tier-proof_poisonforest.xml   unknown -- not traced this window; investigate before deploying or discarding
?? deployed/config/ModsConfig.before-tier-proof_pyrelands.xml   unknown -- not traced this window; investigate before deploying or discarding
?? deployed/config/ModsConfig.before-tier-proof_rustcathedral.xml   unknown -- not traced this window; investigate before deploying or discarding
?? deployed/config/ModsConfig.before-tier-proof_stillsand.xml   unknown -- not traced this window; investigate before deploying or discarding
?? deployed/config/ModsConfig.before-tier-proof_terminalbiomes.xml   unknown -- not traced this window; investigate before deploying or discarding
?? deployed/config/ModsConfig.before-tier-proof_theforge.xml   unknown -- not traced this window; investigate before deploying or discarding
?? deployed/config/ModsConfig.before-tier-proof_therot.xml   unknown -- not traced this window; investigate before deploying or discarding
?? deployed/config/ModsConfig.before-tier-proof_thesump.xml   unknown -- not traced this window; investigate before deploying or discarding
?? deployed/config/ModsConfig.before-tier-proof_wasteland.xml   unknown -- not traced this window; investigate before deploying or discarding
?? deployed/config/ModsConfig.before-tier-proof_webwork.xml   unknown -- not traced this window; investigate before deploying or discarding
?? deployed/config/ModsConfig.before-tier-proof_weepingstones.xml   unknown -- not traced this window; investigate before deploying or discarding
?? deployed/config/ModsConfig.before-tier-weepingstones.xml   unknown -- not traced this window; investigate before deploying or discarding
?? infrastructure/artpipe/daemon_run_20260926_n8_measured.log   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Brindeth_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Brindeth_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Brommet_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Brommet_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Brommet_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Brommet_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Brommet_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Brommet_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Cravvet_v2_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Cravvet_v2_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Cravvet_v2_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Cravvet_v2_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Cravvet_v2_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Cravvet_v2_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Dorvel_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Dorvel_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Dredgel_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Dredgel_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Gulveth_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Gulveth_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Gulveth_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Gulveth_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Gulveth_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Gulveth_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Korveth_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Korveth_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Mirrelin_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Mirrelin_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Pallick_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Pallick_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Quarrok_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Quarrok_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Quarrok_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Quarrok_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Quarrok_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Quarrok_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Quarrok_v2_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Quarrok_v2_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Quarrok_v2_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Quarrok_v2_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Quarrok_v2_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Quarrok_v2_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Sivvern_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Sivvern_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Sivvern_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Sivvern_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Sivvern_v2_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Sivvern_v2_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Sivvern_v2_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Sivvern_v2_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Skelver_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Skelver_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Skennet_v2_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Skennet_v2_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Skennet_v2_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Skennet_v2_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Skennet_v2_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Skennet_v2_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Soffeth_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Soffeth_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Tolleth_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Tolleth_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Velloch_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Velloch_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Vennick_v2_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Vennick_v2_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Vennick_v2_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Vennick_v2_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Vennick_v2_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RM_Vennick_v2_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RSW_Ashworm_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RSW_Ashworm_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RSW_Ashworm_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RSW_Ashworm_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RSW_Ashworm_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RSW_Ashworm_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RSW_Barbthorn_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RSW_Barbthorn_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RSW_Barbthorn_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RSW_Barbthorn_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RSW_Barbthorn_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RSW_Barbthorn_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RSW_EmberCarpet.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RSW_EmberCarpet.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RSW_Scrubgrass.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RSW_Scrubgrass.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RSW_Spinerat_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RSW_Spinerat_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RSW_Spinerat_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RSW_Spinerat_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RSW_Spinerat_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RSW_Spinerat_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RSW_Sporemass_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RSW_Sporemass_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RSW_Sporemass_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RSW_Sporemass_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RSW_Sporemass_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RSW_Sporemass_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RSW_Sporepaw_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RSW_Sporepaw_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RSW_Sporepaw_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RSW_Sporepaw_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RSW_Sporepaw_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RSW_Sporepaw_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RSW_Starvine.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RSW_Starvine.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RSW_Stoneback_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RSW_Stoneback_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RSW_Stoneback_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RSW_Stoneback_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RSW_Stoneback_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RSW_Stoneback_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RSW_Whirlbloom.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/RSW_Whirlbloom.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_chimeglobe.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_chimeglobe.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_chimeglobe_b.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_chimeglobe_b.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_dorrak_dessicated.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_dorrak_dessicated.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_dovvik_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_dovvik_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_dovvik_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_dovvik_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_dovvik_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_dovvik_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_glassfern.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_glassfern.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_glassfern_b.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_glassfern_b.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_glassfern_c.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_glassfern_c.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_krissek_dessicated.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_krissek_dessicated.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_krissek_halo_mote.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_krissek_halo_mote.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_palefloss.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_palefloss.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_palefloss_b.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_palefloss_b.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_palefloss_c.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_palefloss_c.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_utikka_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_utikka_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_utikka_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_utikka_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_utikka_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_utikka_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_vrisk_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_vrisk_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_vrisk_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_vrisk_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_vrisk_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_vrisk_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_zhaaz_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_zhaaz_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_zhaaz_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_zhaaz_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_zhaaz_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/bluedesert_zhaaz_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/cauldron_suush_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/cauldron_suush_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/cauldron_suush_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/cauldron_suush_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/cauldron_suush_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/cauldron_suush_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_blisteredbulloo_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_blisteredbulloo_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_blisteredbulloo_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_blisteredbulloo_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_blisteredbulloo_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_blisteredbulloo_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_brossak_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_brossak_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_brossak_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_brossak_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_brossak_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_brossak_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_fezzira_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_fezzira_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_fezzira_larva_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_fezzira_larva_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_fezzira_larva_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_fezzira_larva_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_fezzira_larva_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_fezzira_larva_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_fezzira_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_fezzira_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_fezzira_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_fezzira_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_ghaaz_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_ghaaz_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_ghaaz_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_ghaaz_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_ghaaz_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_ghaaz_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_ghuvv_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_ghuvv_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_ghuvv_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_ghuvv_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_ghuvv_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_ghuvv_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_gollivra_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_gollivra_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_gollivra_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_gollivra_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_gollivra_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_gollivra_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_greaterbulloo_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_greaterbulloo_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_greaterbulloo_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_greaterbulloo_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_pellorax_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_pellorax_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_pellorax_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_pellorax_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_pibbo_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_pibbo_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_pibbo_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_pibbo_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_pibbo_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_pibbo_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_vezzok_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_vezzok_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_vezzok_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_vezzok_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_vezzok_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_vezzok_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_vulloth_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_vulloth_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_vulloth_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_vulloth_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_vulloth_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_vulloth_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_zhirrik_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_zhirrik_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_zhirrik_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_zhirrik_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_zhirrik_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_zhirrik_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_zhool_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_zhool_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_zhool_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/contagion_zhool_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_brekkugar_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_brekkugar_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_brekkugar_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_brekkugar_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_brekkugar_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_brekkugar_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_dhukk_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_dhukk_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_dhukk_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_dhukk_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_dhukk_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_dhukk_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_ghorrumak_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_ghorrumak_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_ghorrumak_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_ghorrumak_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_ghorrumak_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_ghorrumak_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_gruzz_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_gruzz_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_gruzz_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_gruzz_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_gruzz_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_gruzz_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_hulggarok_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_hulggarok_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_hulggarok_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_hulggarok_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_hulggarok_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_hulggarok_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_kessik_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_kessik_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_kessik_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_kessik_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_shekkur_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_shekkur_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_shekkur_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_shekkur_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_shekkur_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_shekkur_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_thrizzik_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_thrizzik_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_thrizzik_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_thrizzik_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_ulkhorr_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_ulkhorr_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_ulkhorr_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_ulkhorr_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_ulkhorr_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_ulkhorr_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_vrakk_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_vrakk_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_vrakk_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_vrakk_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_vrakk_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_vrakk_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_zekkra_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_zekkra_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_zekkra_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_zekkra_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_zekkra_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_zekkra_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_zhurrakor_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_zhurrakor_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_zhurrakor_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_zhurrakor_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_zhurrakor_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/crags_zhurrakor_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/deepfire_crowncarpet_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/deepfire_crowncarpet_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/deepfire_crowncarpet_b.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/deepfire_crowncarpet_b.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/deepfire_crowncarpet_c.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/deepfire_crowncarpet_c.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/deepfire_crowncarpet_d.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/deepfire_crowncarpet_d.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/deepfire_pigmentjar_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/deepfire_pigmentjar_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/deepfire_pigmentjar_b.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/deepfire_pigmentjar_b.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_plant_chakroot_wild.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_plant_chakroot_wild.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_plant_hubbagourd_wild.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_plant_hubbagourd_wild.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_plant_nysyllin_wild.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_plant_nysyllin_wild.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_porg_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_porg_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_porg_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_porg_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_porg_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_porg_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_qormot_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_qormot_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_qormot_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_qormot_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_qormot_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_qormot_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_runyip_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_runyip_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_runyip_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_runyip_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_runyip_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_runyip_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_shaak_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_shaak_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_shaak_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_shaak_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_shaak_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_shaak_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_strill_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_strill_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_strill_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_strill_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_strill_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_strill_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_teemuss_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_teemuss_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_teemuss_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_teemuss_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_teemuss_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_teemuss_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_uvak_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_uvak_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_uvak_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_uvak_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_uvak_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_uvak_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_varactyl_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_varactyl_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_varactyl_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_varactyl_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_varactyl_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_varactyl_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_voorpak_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_voorpak_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_voorpak_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_voorpak_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_voorpak_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_voorpak_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_vulptex_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_vulptex_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_vulptex_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_vulptex_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_vulptex_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_vulptex_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_warwyrm_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_warwyrm_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_warwyrm_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_warwyrm_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_warwyrm_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_warwyrm_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_whisperbird_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_whisperbird_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_whisperbird_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_whisperbird_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_whisperbird_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_whisperbird_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_zeer_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_zeer_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_zeer_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_zeer_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_zeer_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/desertportb_zeer_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_brathek_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_brathek_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_brathek_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_brathek_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_brathek_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_brathek_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_chellow_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_chellow_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_drommath_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_drommath_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_drommath_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_drommath_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_gorrameth_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_gorrameth_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_gorrameth_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_gorrameth_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_gorrameth_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_gorrameth_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_grolth_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_grolth_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_grolth_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_grolth_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_grolth_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_grolth_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_kurreth_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_kurreth_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_kurreth_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_kurreth_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_kurreth_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_kurreth_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_lommerel_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_lommerel_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_lommerel_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_lommerel_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_lommerel_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_lommerel_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_murrelith_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_murrelith_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_murrelith_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_murrelith_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_murrelith_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_murrelith_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_nemmel_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_nemmel_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_nemmel_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_nemmel_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_nemmel_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_nemmel_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_ollareth_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_ollareth_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_ollareth_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_ollareth_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_ollareth_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_ollareth_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_plant_ammeth.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_plant_ammeth.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_plant_cistrel.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_plant_cistrel.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_plant_claithe.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_plant_claithe.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_plant_corvath.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_plant_corvath.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_plant_halquin.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_plant_halquin.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_plant_maulith.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_plant_maulith.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_plant_nubrith.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_plant_nubrith.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_plant_ossagrel.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_plant_ossagrel.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_plant_plennith.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_plant_plennith.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_plant_seepril.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_plant_seepril.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_plant_skethral.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_plant_skethral.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_plant_skimmel.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_plant_skimmel.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_plant_sodderel.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_plant_sodderel.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_plant_thulvane.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_plant_thulvane.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_plant_tullick.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_plant_tullick.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_plant_varnoth.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_plant_varnoth.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_plant_verrow.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_plant_verrow.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_plant_wanlith.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_plant_wanlith.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_silloch_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_silloch_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_silloch_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_silloch_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_silloch_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_silloch_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_skellick_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_skellick_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_skellick_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_skellick_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_skellick_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_skellick_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_skreth_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_skreth_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_skreth_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_skreth_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_skreth_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_skreth_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_thavrik_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_thavrik_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_thavrik_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_thavrik_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_thavrik_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_thavrik_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_thornbug_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_thornbug_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_thornbug_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_thornbug_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_thornbug_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_thornbug_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_vaulm_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_vaulm_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_vaulm_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_vaulm_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_vaulm_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/feverwood_vaulm_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/glyph_animalpersonhood.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/glyph_animalpersonhood.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/glyph_blindsight.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/glyph_blindsight.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/glyph_cannibal.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/glyph_cannibal.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/glyph_collectivist.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/glyph_collectivist.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/glyph_darkness.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/glyph_darkness.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/glyph_fleshpurity.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/glyph_fleshpurity.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/glyph_guilty.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/glyph_guilty.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/glyph_highlife.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/glyph_highlife.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/glyph_humanprimacy.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/glyph_humanprimacy.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/glyph_inhuman.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/glyph_inhuman.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/glyph_loyalist.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/glyph_loyalist.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/glyph_malesupremacy.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/glyph_malesupremacy.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/glyph_natureprimacy.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/glyph_natureprimacy.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/glyph_nudism.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/glyph_nudism.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/glyph_painisvirtue.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/glyph_painisvirtue.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/glyph_proselytizer.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/glyph_proselytizer.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/glyph_raider.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/glyph_raider.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/glyph_rancher.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/glyph_rancher.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/glyph_ritualist.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/glyph_ritualist.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/glyph_shipborn.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/glyph_shipborn.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/glyph_supremacist.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/glyph_supremacist.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/glyph_transhumanist.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/glyph_transhumanist.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/glyph_treeconnection.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/glyph_treeconnection.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/glyph_tunneler.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/glyph_tunneler.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/graffiti_crossout.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/graffiti_crossout.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/graffiti_paste_flyer_p1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/graffiti_paste_flyer_p1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/graffiti_paste_flyer_p2.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/graffiti_paste_flyer_p2.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/graffiti_paste_wanted_p1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/graffiti_paste_wanted_p1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/graffiti_paste_wanted_p2.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/graffiti_paste_wanted_p2.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/graffiti_sigilframe_dripframe.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/graffiti_sigilframe_dripframe.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/graffiti_sigilframe_halo.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/graffiti_sigilframe_halo.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/graffiti_sigilframe_stencilbox.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/graffiti_sigilframe_stencilbox.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/graffiti_stencil_crown.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/graffiti_stencil_crown.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/graffiti_stencil_fist.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/graffiti_stencil_fist.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/graffiti_stencil_gear.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/graffiti_stencil_gear.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/graffiti_tag_a_p1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/graffiti_tag_a_p1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/graffiti_tag_a_p2.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/graffiti_tag_a_p2.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/graffiti_tag_b_p1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/graffiti_tag_b_p1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/graffiti_tag_b_p2.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/graffiti_tag_b_p2.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/graffiti_tag_c_p1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/graffiti_tag_c_p1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/graffiti_tag_c_p2.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/graffiti_tag_c_p2.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/graffiti_throwup_a_p1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/graffiti_throwup_a_p1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/graffiti_throwup_a_p2.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/graffiti_throwup_a_p2.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/graffiti_throwup_b_p1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/graffiti_throwup_b_p1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/graffiti_throwup_b_p2.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/graffiti_throwup_b_p2.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/greysea_essarn_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/greysea_essarn_v1_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/greysea_essarn_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/greysea_essarn_v1_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/greysea_essarn_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/greysea_essarn_v1_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/greysea_fessk_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/greysea_fessk_v1_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/greysea_fessk_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/greysea_fessk_v1_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/greysea_fessk_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/greysea_fessk_v1_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/greysea_otheska_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/greysea_otheska_v1_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/greysea_otheska_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/greysea_otheska_v1_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/greysea_otheska_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/greysea_otheska_v1_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/greysea_sorruth_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/greysea_sorruth_v1_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/greysea_sorruth_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/greysea_sorruth_v1_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/miasma_aphreen.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/miasma_aphreen.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/miasma_braskeen_open.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/miasma_braskeen_open.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/miasma_brelloch.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/miasma_brelloch.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/miasma_ilbareen_dead.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/miasma_ilbareen_dead.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/miasma_ilbareen_live.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/miasma_ilbareen_live.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/miasma_immarel.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/miasma_immarel.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/miasma_ismerrow_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/miasma_ismerrow_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/miasma_ismerrow_b.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/miasma_ismerrow_b.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/miasma_ismerrow_c.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/miasma_ismerrow_c.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/miasma_ismerrow_d.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/miasma_ismerrow_d.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/miasma_nemreth.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/miasma_nemreth.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/miasma_nyssolet.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/miasma_nyssolet.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/miasma_ollamane.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/miasma_ollamane.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/miasma_ommolyn.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/miasma_ommolyn.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/miasma_pallasheen.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/miasma_pallasheen.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/miasma_quennath.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/miasma_quennath.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/miasma_sarrash.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/miasma_sarrash.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/miasma_thessamor.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/miasma_thessamor.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/miasma_thrannock.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/miasma_thrannock.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/miasma_ullavess.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/miasma_ullavess.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/miasma_vellamine.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/miasma_vellamine.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/miasma_velluric.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/miasma_velluric.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/miasma_wessaline.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/miasma_wessaline.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/nightside_mahllik_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/nightside_mahllik_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/nightside_mahllik_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/nightside_mahllik_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/nightside_mahllik_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/nightside_mahllik_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/nightside_zhissa_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/nightside_zhissa_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/nightside_zhissa_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/nightside_zhissa_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/nightside_zhissa_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/nightside_zhissa_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/propanelake_heemin_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/propanelake_heemin_v1_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/propanelake_heemin_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/propanelake_heemin_v1_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/propanelake_heemin_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/propanelake_heemin_v1_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/propanelake_hoolen_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/propanelake_hoolen_v1_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/propanelake_hoolen_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/propanelake_hoolen_v1_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/propanelake_hoolen_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/propanelake_hoolen_v1_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/propanelake_oovanam_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/propanelake_oovanam_v1_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/propanelake_oovanam_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/propanelake_oovanam_v1_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/propanelake_oovanam_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/propanelake_oovanam_v1_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/propanelake_vaunoom_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/propanelake_vaunoom_v1_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/propanelake_vaunoom_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/propanelake_vaunoom_v1_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/propanelake_vaunoom_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/propanelake_vaunoom_v1_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/pyrelands_barbslinger_v5_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/pyrelands_barbslinger_v5_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/pyrelands_barbslinger_v5_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/pyrelands_barbslinger_v5_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_brakkel_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_brakkel_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_brunnock_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_brunnock_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_cundral_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_cundral_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_gorbeleth_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_gorbeleth_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_kaddrath_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_kaddrath_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_maddrick_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_maddrick_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_mirrelbole_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_mirrelbole_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_mourvel_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_mourvel_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_phorrik_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_phorrik_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_quathis_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_quathis_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_sarnstilt_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_sarnstilt_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_sarquin_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_sarquin_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_thalquith_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_thalquith_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_tumbel_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_tumbel_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_vurmeloth_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_vurmeloth_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_wollick_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_wollick_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_zhorrel_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rm_zhorrel_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rmdusthusk_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rmdusthusk_v1_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rmleachmoss_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rmleachmoss_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rmmirrorgiant_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rmmirrorgiant_v1_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rmmirrorgiant_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rmmirrorgiant_v1_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rmmirrorgiant_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rmmirrorgiant_v1_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rmtitanoslime_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rmtitanoslime_v1_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rmtitanoslime_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rmtitanoslime_v1_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rmtitanoslime_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rmtitanoslime_v1_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rmvenomvine_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rmvenomvine_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rot_brogg_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rot_brogg_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rot_brogg_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rot_brogg_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rot_brogg_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rot_brogg_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rot_brullith_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rot_brullith_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rot_brullith_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rot_brullith_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rot_brullith_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rot_brullith_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rot_illoth_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rot_illoth_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rot_illoth_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rot_illoth_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rot_illoth_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rot_illoth_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rot_skerrith_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rot_skerrith_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rot_skerrith_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rot_skerrith_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rot_skerrith_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rot_skerrith_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rot_thozzik_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rot_thozzik_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rot_thozzik_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rot_thozzik_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rot_thozzik_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rot_thozzik_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rot_thozzikqueen_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rot_thozzikqueen_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rot_thozzikqueen_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rot_thozzikqueen_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rot_thozzikqueen_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rot_thozzikqueen_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rsw_graffiti_stencil_imperialcog.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rsw_graffiti_stencil_imperialcog.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rsw_zakkro_dessicated_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rsw_zakkro_dessicated_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rsw_zakkro_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rsw_zakkro_v1_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rsw_zakkro_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rsw_zakkro_v1_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rsw_zakkro_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rsw_zakkro_v1_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rsw_zakkroegg_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rsw_zakkroegg_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rswrawultracactus_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rswrawultracactus_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rswultracactus_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rswultracactus_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_1_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_1_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_1_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_2_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_2_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_2_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_2_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_3_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_3_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_3_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_3_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_3_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_3_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_4_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_4_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_4_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_4_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_4_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_4_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_5_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_5_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_5_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_5_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_5_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_flying_v2_5_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_grounded_v3_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_grounded_v3_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_grounded_v3_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_grounded_v3_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_grounded_v3_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_firehawk_grounded_v3_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_greentideant_dessicated_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_greentideant_dessicated_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_grellbush.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_grellbush.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_grellspine.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_grellspine.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_vhessk_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_vhessk_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_vhessk_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_vhessk_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_wildhealroot.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rut_wildhealroot.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutbloomcrop_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutbloomcrop_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutbrinebattery_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutbrinebattery_v1_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutbrinebattery_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutbrinebattery_v1_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutbrinebattery_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutbrinebattery_v1_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutbrinebattery_v2_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutbrinebattery_v2_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutbrinebattery_v2_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutbrinebattery_v2_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutdarkcrust_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutdarkcrust_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutdeltaloam_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutdeltaloam_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutdosimeterlawn_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutdosimeterlawn_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutemperorvulture_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutemperorvulture_v1_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutemperorvulture_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutemperorvulture_v1_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutemperorvulture_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutemperorvulture_v1_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutfleetflier_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutfleetflier_v1_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutfleetflier_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutfleetflier_v1_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutfleetflier_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutfleetflier_v1_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutfuzz_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutfuzz_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutglower_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutglower_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutglowercrust_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutglowercrust_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutkarrathil_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutkarrathil_v1_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutkarrobel_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutkarrobel_v1_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutmortuarycrawler_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutmortuarycrawler_v1_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutmortuarycrawler_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutmortuarycrawler_v1_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutmortuarycrawler_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutmortuarycrawler_v1_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutradiothermal_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutradiothermal_v1_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutradiothermal_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutradiothermal_v1_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutradiothermal_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutradiothermal_v1_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutsealedsleeper_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutsealedsleeper_v1_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutsealedsleeper_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutsealedsleeper_v1_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutsealedsleeper_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutsealedsleeper_v1_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutslimegrazer_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutslimegrazer_v1_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutslimegrazer_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutslimegrazer_v1_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutslimegrazer_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutslimegrazer_v1_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutslimegrazer_v2_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutslimegrazer_v2_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutslimegrazer_v2_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutslimegrazer_v2_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutslimegrazer_v2_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutslimegrazer_v2_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutstaggerseed_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutstaggerseed_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutstaggerseeddish_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutstaggerseeddish_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutvaultroot_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutvaultroot_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutvwake_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutvwake_v1_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutvwake_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutvwake_v1_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutvwake_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutvwake_v1_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutwelcomeblanket_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutwelcomeblanket_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutyearningfruit_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/rutyearningfruit_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_bladderboilcatch_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_bladderboilcatch_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_bladderboilcatch_b.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_bladderboilcatch_b.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_bladderboilcatch_c.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_bladderboilcatch_c.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_dosscatch_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_dosscatch_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_dosscatch_b.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_dosscatch_b.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_dosscatch_c.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_dosscatch_c.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_eeshcatch_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_eeshcatch_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_eeshcatch_b.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_eeshcatch_b.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_eeshcatch_c.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_eeshcatch_c.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_ekkelcatch_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_ekkelcatch_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_ekkelcatch_b.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_ekkelcatch_b.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_ekkelcatch_c.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_ekkelcatch_c.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_karrashcatch_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_karrashcatch_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_karrashcatch_b.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_karrashcatch_b.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_karrashcatch_c.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_karrashcatch_c.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_muddalcatch_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_muddalcatch_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_muddalcatch_b.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_muddalcatch_b.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_muddalcatch_c.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_muddalcatch_c.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_rainbowpigment_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_rainbowpigment_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_rainbowpigment_b.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_rainbowpigment_b.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_rainbowpigment_c.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_rainbowpigment_c.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_saalcatch_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_saalcatch_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_saalcatch_b.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_saalcatch_b.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_saalcatch_c.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_saalcatch_c.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_shullacatch_b.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_shullacatch_b.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_shullacatch_c.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_shullacatch_c.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_steamcatchbuilding_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_steamcatchbuilding_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_thuumcatch_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_thuumcatch_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_thuumcatch_b.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_thuumcatch_b.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_thuumcatch_c.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_thuumcatch_c.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_ventbuilding_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_ventbuilding_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_ventbuilding_b.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_ventbuilding_b.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_wreckframe_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_wreckframe_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_wreckframe_b.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_wreckframe_b.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_wreckframe_c.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_wreckframe_c.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_wreckhull_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_wreckhull_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_wreckhull_b.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_wreckhull_b.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_wreckhull_c.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_wreckhull_c.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_wrecktank_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_wrecktank_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_wrecktank_b.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_wrecktank_b.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_wrecktank_c.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald2_wrecktank_c.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald3_shullacatch_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald3_shullacatch_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_bladderboilcatch_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_bladderboilcatch_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_noohm_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_noohm_v1_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_noohm_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_noohm_v1_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_noohm_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_noohm_v1_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_saalcatch_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_saalcatch_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_shulla_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_shulla_v1_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_shulla_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_shulla_v1_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_shulla_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_shulla_v1_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_shullacatch_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_shullacatch_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_steamcatchbuilding_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_steamcatchbuilding_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_ventbuilding_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_ventbuilding_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_wreckframe_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_wreckframe_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_wreckhull_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_wreckhull_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_wrecktank_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scald_wrecktank_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scaldfloor_bladderboil_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scaldfloor_bladderboil_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scaldfloor_bladderboil_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scaldfloor_bladderboil_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scaldfloor_bladderboil_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scaldfloor_bladderboil_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scaldfloor_doss_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scaldfloor_doss_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scaldfloor_doss_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scaldfloor_doss_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scaldfloor_doss_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scaldfloor_doss_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scaldfloor_eesh_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scaldfloor_eesh_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scaldfloor_eesh_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scaldfloor_eesh_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scaldfloor_eesh_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scaldfloor_eesh_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scaldfloor_ekkel_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scaldfloor_ekkel_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scaldfloor_ekkel_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scaldfloor_ekkel_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scaldfloor_ekkel_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scaldfloor_ekkel_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scaldfloor_karrash_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scaldfloor_karrash_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scaldfloor_karrash_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scaldfloor_karrash_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scaldfloor_karrash_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scaldfloor_karrash_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scaldfloor_muddal_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scaldfloor_muddal_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scaldfloor_muddal_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scaldfloor_muddal_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scaldfloor_muddal_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scaldfloor_muddal_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scaldfloor_thuum_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scaldfloor_thuum_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scaldfloor_thuum_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scaldfloor_thuum_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scaldfloor_thuum_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scaldfloor_thuum_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scaldsteam_overlay_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scaldsteam_overlay_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scaldsteam_overlay_b.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/scaldsteam_overlay_b.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_bezzul_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_bezzul_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_bezzul_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_bezzul_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_bezzul_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_bezzul_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_greateroomb_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_greateroomb_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_greateroomb_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_greateroomb_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_hennul_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_hennul_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_hennul_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_hennul_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_hennul_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_hennul_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_mubbaro_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_mubbaro_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_mubbaro_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_mubbaro_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_mubbaro_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_mubbaro_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_oomb_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_oomb_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_oomb_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_oomb_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_oomb_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_oomb_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_thummorak_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_thummorak_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_thummorak_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_thummorak_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_thummorak_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_thummorak_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_vohhm_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_vohhm_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_vohhm_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_vohhm_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_vohhm_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_vohhm_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_wuppik_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_wuppik_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_wuppik_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_wuppik_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_wuppik_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_wuppik_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_wuum_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_wuum_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_wuum_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_wuum_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_wuum_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_wuum_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_yollum_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_yollum_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_yollum_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_yollum_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_yollum_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/slime_yollum_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/twilightsea_loohn_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/twilightsea_loohn_v1_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/twilightsea_loohn_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/twilightsea_loohn_v1_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/twilightsea_lunoowa_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/twilightsea_lunoowa_v1_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/twilightsea_lunoowa_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/twilightsea_lunoowa_v1_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/twilightsea_lunoowa_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/twilightsea_lunoowa_v1_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/twilightsea_noolim_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/twilightsea_noolim_v1_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/twilightsea_noolim_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/twilightsea_noolim_v1_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/twilightsea_noolim_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/twilightsea_noolim_v1_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/twilightsea_weloon_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/twilightsea_weloon_v1_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/twilightsea_weloon_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/twilightsea_weloon_v1_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/twilightsea_weloon_v1_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/twilightsea_weloon_v1_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/webwork_anchor.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/webwork_anchor.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/webwork_gutter.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/webwork_gutter.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/webwork_plant_brennoth.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/webwork_plant_brennoth.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/webwork_plant_brimlock.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/webwork_plant_brimlock.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/webwork_plant_dulloth.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/webwork_plant_dulloth.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/webwork_plant_fellome.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/webwork_plant_fellome.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/webwork_plant_grennick.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/webwork_plant_grennick.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/webwork_plant_kessaroth.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/webwork_plant_kessaroth.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/webwork_plant_kollavane.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/webwork_plant_kollavane.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/webwork_plant_norrveth.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/webwork_plant_norrveth.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/webwork_plant_pellareth.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/webwork_plant_pellareth.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/webwork_plant_ruddreth.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/webwork_plant_ruddreth.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/webwork_plant_sellith.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/webwork_plant_sellith.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/webwork_plant_sorrivel.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/webwork_plant_sorrivel.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/webwork_plant_tavrosk.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/webwork_plant_tavrosk.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/webwork_plant_threllick.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/webwork_plant_threllick.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/webwork_plant_varrisk.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/webwork_plant_varrisk.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/webwork_plant_vessark.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/webwork_plant_vessark.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/webwork_web.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/webwork_web.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_bladderfruit.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_bladderfruit.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_bladderquill.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_bladderquill.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_burrak_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_burrak_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_burrak_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_burrak_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_burrak_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_burrak_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_dewblade.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_dewblade.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_dewgourd.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_dewgourd.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_dewgourdfruit.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_dewgourdfruit.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_dripfringe.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_dripfringe.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_kirruk_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_kirruk_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_kirruk_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_kirruk_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_kirruk_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_kirruk_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_mirrik_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_mirrik_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_rockfinger.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_rockfinger.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_salvecomb.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_salvecomb.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_seepsalt.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_seepsalt.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_shadefern.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_shadefern.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_ssurr_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_ssurr_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_ssurr_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_ssurr_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_steamfrond.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_steamfrond.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_tirbak_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_tirbak_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_tirbak_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_tirbak_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_vellak_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_vellak_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_vellak_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_vellak_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_verdimoss.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_verdimoss.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_vhakk_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_vhakk_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_vhakk_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_vhakk_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_weepmat.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones2_weepmat.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones_ivvol_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones_ivvol_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones_ivvol_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones_ivvol_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones_ivvol_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones_ivvol_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones_karrek_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones_karrek_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones_karrek_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones_karrek_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones_karrek_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones_karrek_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones_loomu_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones_loomu_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones_loomu_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones_loomu_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones_loomu_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones_loomu_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones_murrin_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones_murrin_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones_murrin_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones_murrin_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones_murrin_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones_murrin_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones_skarrin_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones_skarrin_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones_skarrin_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones_skarrin_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones_skarrin_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones_skarrin_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones_vhorrin_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones_vhorrin_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones_vhorrin_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones_vhorrin_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones_vhorrin_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones_vhorrin_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones_vizhik_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones_vizhik_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones_vizhik_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/done/weepingstones_vizhik_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Cravvet_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Cravvet_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Cravvet_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Cravvet_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Cravvet_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Cravvet_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Dredgel_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Dredgel_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Dredgel_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Dredgel_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Sivvern_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Sivvern_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Sivvern_v2_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Sivvern_v2_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Skarrid_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Skarrid_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Skarrid_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Skarrid_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Skarrid_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Skarrid_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Skellarn_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Skellarn_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Skellarn_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Skellarn_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Skellarn_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Skellarn_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Skennet_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Skennet_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Skennet_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Skennet_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Skennet_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Skennet_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_SumpMouse_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_SumpMouse_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_SumpMouse_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_SumpMouse_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_SumpMouse_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_SumpMouse_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_ThrummelBroodmother_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_ThrummelBroodmother_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_ThrummelBroodmother_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_ThrummelBroodmother_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_ThrummelBroodmother_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_ThrummelBroodmother_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_ThrummelWarden_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_ThrummelWarden_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_ThrummelWarden_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_ThrummelWarden_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_ThrummelWarden_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_ThrummelWarden_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Thrummel_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Thrummel_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Thrummel_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Thrummel_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Thrummel_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/RM_Thrummel_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/contagion_greaterbulloo_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/contagion_greaterbulloo_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/contagion_pellorax_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/contagion_pellorax_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/contagion_zhool_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/contagion_zhool_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/crags_kessik_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/crags_kessik_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/crags_thrizzik_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/crags_thrizzik_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/desertportb_greaterkraytdragon_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/desertportb_greaterkraytdragon_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/desertportb_greaterkraytdragon_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/desertportb_greaterkraytdragon_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/desertportb_kraytdragon_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/desertportb_kraytdragon_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/desertportb_pikobis_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/desertportb_pikobis_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/feverwood_chellow_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/feverwood_chellow_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/feverwood_chellow_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/feverwood_chellow_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/feverwood_drommath_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/feverwood_drommath_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/glyph_bloodfeeding.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/glyph_bloodfeeding.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/glyph_femalesupremacy.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/glyph_femalesupremacy.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/glyph_individualist.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/glyph_individualist.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/greysea_sorruth_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/greysea_sorruth_v1_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/miasma_braskeen_closed.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/miasma_braskeen_closed.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rmdusthusk_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rmdusthusk_v1_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rmdusthusk_v1_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rmdusthusk_v1_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rut_firehawk_flying_v2_2_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rut_firehawk_flying_v2_2_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rut_greentideant_body_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rut_greentideant_body_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rut_greentideant_body_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rut_greentideant_body_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rut_greentideant_body_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rut_greentideant_body_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rut_greentideant_carapacewall_atlas.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rut_greentideant_carapacewall_atlas.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rut_greentideant_carapacewall_menuicon.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rut_greentideant_carapacewall_menuicon.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rut_greentideant_dessicated_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rut_greentideant_dessicated_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rut_greentideant_dessicated_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rut_greentideant_dessicated_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rut_vhessk_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rut_vhessk_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rutbrinebattery_v2_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rutbrinebattery_v2_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rutglowercrust_v1.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/rutglowercrust_v1.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/scald2_shullacatch_a.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/scald2_shullacatch_a.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/slime_greateroomb_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/slime_greateroomb_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/twilightsea_loohn_v1_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/twilightsea_loohn_v1_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/weepingstones2_gorrask_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/weepingstones2_gorrask_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/weepingstones2_gorrask_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/weepingstones2_gorrask_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/weepingstones2_gorrask_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/weepingstones2_gorrask_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/weepingstones2_mirrik_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/weepingstones2_mirrik_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/weepingstones2_mirrik_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/weepingstones2_mirrik_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/weepingstones2_sillik_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/weepingstones2_sillik_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/weepingstones2_sillik_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/weepingstones2_sillik_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/weepingstones2_sillik_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/weepingstones2_sillik_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/weepingstones2_ssurr_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/weepingstones2_ssurr_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/weepingstones2_tirbak_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/weepingstones2_tirbak_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/weepingstones2_vellak_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/weepingstones2_vellak_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/weepingstones2_vhakk_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/weepingstones2_vhakk_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/weepingstones_huldu_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/weepingstones_huldu_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/weepingstones_huldu_north.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/weepingstones_huldu_north.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/weepingstones_huldu_south.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/weepingstones_huldu_south.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/weepingstones_vizhik_east.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/artpipe/failed/weepingstones_vizhik_east.manifest.json   ambient -- artpipe daemon (background, continuous), draining its own queue; not this window's
?? infrastructure/dashboards/hub/tabs/maturity.html   unknown -- not traced this window; investigate before deploying or discarding
?? infrastructure/dashboards/hub/utinni_control_room_standalone.html   unknown -- not traced this window; investigate before deploying or discarding
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   unknown -- not traced this window; investigate before deploying or discarding
?? infrastructure/state/modlists/ModsConfig.pre-floodedcanyon-quicktest-20260921T104640.xml   unknown -- not traced this window; investigate before deploying or discarding
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_COLD_LOAD_RUN_SHEET_4_2026-09-23.xml   unknown -- not traced this window; investigate before deploying or discarding
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_bacta_enable_2026-09-24T133247Z.xml   unknown -- not traced this window; investigate before deploying or discarding
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_restoring_seashores_bacta_2026-09-25T175356.xml   unknown -- not traced this window; investigate before deploying or discarding
?? infrastructure/state/modlists/ModsConfig_BACKUP_before_seashores_enable_2026-09-25T133443.xml   unknown -- not traced this window; investigate before deploying or discarding
?? infrastructure/state/modlists/ModsConfig_backup_before_rustcathedral_enable_2026-09-23T211528Z.xml   unknown -- not traced this window; investigate before deploying or discarding
?? infrastructure/state/rescued/LanternDeeps_RUT/Assemblies/   unknown -- not traced this window; investigate before deploying or discarding
?? src/RimMandrake/Utils/firehawk_flight_probe.py   unknown -- not traced this window; investigate before deploying or discarding
```

