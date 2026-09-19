# MODLIST_INACTIVE_CUSTOM_MODS_SWEEP_1 — full custom-mod activation sweep, 2026-09-19

Fresh full sweep (FOUNDRY BELT, 2026-09-19), offline diff only, bridge never touched.
Parsed every `mandrake.*` mod's own `About.xml` direct-child `<packageId>` (141 found
under the deployed `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods`) against
the live `ModsConfig.xml` (620 `activeMods`). **112 ACTIVE, 29 INACTIVE** — far more than
prior passes tracked (those only ever named 4: injections / environmentalhazards /
utinnipatches-phantom / weathersuite, all already resolved — not re-flagged here).

Nothing was flipped on this pass. Every one of the 29 carries genuine doubt (blocked /
mid-dev / dormant-by-design / unverified-live / unclear-scope), so none matches the
`injections` precedent (byte-identical deployed + an explicit owner enable ruling)
closely enough for unilateral action.

## Deliberately off — explicit reason found in ledger history

- `mandrake.rm.pyrinth` (Pyrinth) — `CRYSTAL_INGEST_EXECUTION_1`'s close note says
  explicitly "dormant pending future donor retirement."
- `mandrake.rm.raidredesigner` (RaidRedesigner) — its Oracle calls are blocked pending
  the OracleClient HTTP→subprocess rewrite (CLAUDE.md 2026-09-05 ruling;
  `PLOT_MECHANISM_MODS_WAVE_1`).
- `mandrake.rm.liquidtypes` (LiquidTypes) — stale SPIKE-stage mod (`LIQUID_TYPES_SPIKES_1`,
  2026-09-12), superseded by the LiquidDef registry now built inside FlowWorks
  (`LIQUID_REGISTRY_CORE_1`) — `src/RimMandrake/LiquidTypes` no longer exists in the repo
  at all, only this deployed leftover remains. Cleanup/retire candidate, not an
  activation gap.
- `mandrake.rm.divinginteraction` (DivingInteraction) — `SCALD_DIVING_MOD_1` BLOCKED
  2026-09-12, never unblocked.
- `mandrake.rut.kybertradeplot` (KyberTradePlot) — `KYBER_TRADE_PLOT_1` BLOCKED.
- `mandrake.rsw.sarlacc` (Sarlacc) — `SARLACC_HABITAT_BUILD_1` BLOCKED 2026-09-12, never
  unblocked or closed.
- `mandrake.rut.rustcathedralhum` + `mandrake.rut.rustcathedralwalls` — `RUST_CATHEDRAL_MECHANICS_1`
  still `doing`; today's (2026-09-19 06:45Z) note stages a controlled quicktest-map
  enable+verify recipe (`COLD_LOAD_RUN_SHEET_4` ENTRY 8) rather than a blind flip — leave
  for whoever runs that recipe.
- `mandrake.rut.ashkarrflora` (AshkarrFlora) — known unresolved defect,
  `ASHKARR_FLORA_SWEETLINE_ART_UNWIRED_1` (empty texture folder, art not wired).

## Mid-development — claimed/started, not closed, live churn

- `mandrake.rm.bazaar` (TheBazaar) — `BAZAAR_WINDOW_GRID_1`, slice 1 of a larger build only.
- `mandrake.rm.manywaters` (ManyWaters) — `MANYWATERS_COLOR_SUPPORT_1` blocked, plus heavy
  same-mod churn today (`MANY_WATERS_DRILL_BUILDINGS_1`, `RIVER_STEAM_ANIMATION_1`).
- `mandrake.rm.gelatinousslime` (GelatinousSlime) — active today via `SLIME_STREAM_ROWS_1`
  / liquids-framework work.
- `mandrake.rsw.bacta` (Bacta) — `BACTA_TANK_CORE_1` filed+claimed 2026-09-14, never started.
- `mandrake.rsw.trophycraft` (TrophyCraft) — `WYYYSCHOKK_FANG_PENDANT_1` built 2026-09-18,
  no close event yet.
- `mandrake.rut.scarlandsladder` (ScarlandsLadder) — `SCARLANDS_MECHANICS_2` claimed/started
  2026-09-14, stalled since, not closed.
- `mandrake.rut.shipshields` (ShipShields) — `SHIELD_MODS_LEVERAGE_1` claimed/started
  2026-09-18, not closed.

## Genuine activation-gap candidates — item CLOSED, content built, no live verification on record

Unlike `injections`, these lack a BENCH-confirmed "byte-identical proven" measurement
plus an owner enable ruling, so none were enabled this pass. Recommend an owner ruling
plus a live-load pass, the same track `mandrake.rm.weathersuite` took.

- `mandrake.rm.titaniccreatures` (TitanicCreatures) — `TITANIC_CREATURES_MOD_1` closed
  2026-09-09.
- `mandrake.rsw.brainworms` (BrainWorms) — `BRAINWORM_MOD_BUILD_1` closed 2026-09-11.
- `mandrake.rm.floodedcanyon` (FloodedCanyon) — `FLOOD_CANYON_BIOME_1` closed 2026-09-12;
  its own file note says "the campaign's flood-witness plot beat consumes it as a
  dependency" — check that plot beat's status alongside any enable.
- `mandrake.rut.restrainingbolts` (RestrainingBolts) — `DROID_FDE_GOODWILL_CAP_1` closed
  2026-09-09 explicitly on OFFLINE criteria only ("live-observed goodwill-cap-in-effect
  test stays owed").
- `mandrake.rut.longhunger` (LongHunger) — **HIGHEST PRIORITY OF THE SWEEP.**
  `SANDWORM_MYTHOS_BUILD_1` closed 2026-09-09 carrying an explicit OWNER RULING
  (2026-09-05): *"keep BOTH chezhou.creature.sandworm AND RUT_LongHunger active side by
  side."* A 2026-09-12 review wave logged it as "not currently enabled in the minimal
  ModsConfig, which is expected for un-quicktested content" — deliberately gated on a
  live/quicktest pass, not forgotten. Owner already wants this active; next bridge
  session should quicktest then flip it on.

## Unclear — no dedicated build-or-close item found

Only generic dirty-code-review or `validation.py`-backfill touches turned up. Leaving
off, flagging for whoever next has bridge/research time.

- `mandrake.rm.lorestages` (LoreStages) — likely the vehicle for the closed
  `STAGED_LORE_PROOF_SPIKE_1` tech-demo experiment; unclear if meant to ship on the real
  campaign.
- `mandrake.rm.rustchrome` (RustChrome)
- `mandrake.rut.aftermath` (AftermathRites)
- `mandrake.rut.fungalsoiltrade` (FungalSoilTrade)
- `mandrake.rut.rivercolors` (RiverColors)
- `mandrake.rsw.kotorbandoliernorthfix` (KotORBandolierNorthFix) and
  `mandrake.rsw.msedroidfix` (MSEDroidFix) — both donor-art-fix mods entangled in the
  2026-09-09/10 droid-donor-retirement saga (`DROID_DONOR_SAVE_COMPAT_REGRESSION_1` /
  `DROID_RETIRE_DEPOT_ASIMOV_1`); check whether their target donor content is even still
  active before enabling either.
- `mandrake.rut.weathersuite` (AshkarrWeatherSuite) — a SEPARATE mod from the already-active
  `mandrake.rm.weathersuite` (WeatherSuite); both carry maintained `validation.py` as of
  2026-09-17 so neither is obviously stale, but no item distinguishes its role from the
  RM-tier one.

## Not re-flagged (resolved by prior passes)

`mandrake.rut.injections`, `mandrake.rm.environmentalhazards`, `mandrake.rm.weathersuite`
all ACTIVE. `mandrake.rut.utinnipatches` is a phantom id — real id is
`mandrake.rut.patches` (folder `UtinniPatches`), already active. Do not re-add it.
