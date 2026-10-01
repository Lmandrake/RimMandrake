# worker notes PYRELANDS_SITE_PREP_1

## status
reading done; building.

## findings
- Worldgen ban check: §3.4 re-tiles a 2-ring patch on a THROWAWAY vanilla debug quicktest world
  (rimworld/start_debug_game_ready), never Ash'karr, never saved as a world for players, no seed
  choice/sweep (seedString only recorded). Judged NOT a conflict with the ban: it produces a test
  fixture, not an alternative planet. Proceeding.
- `RM_BiomesSettings.Enabled("Pyrelands")` is a static METHOD over an instance dict `enabled`;
  `jawa/mod_settings_field` reads fields, so the check reads `RM_BiomesSettings.Instance.enabled`
  (absent key = ON).
- `jawa/time_clock` has NO `hour` field (its ResultDescription), so Graffiti's `site.pin_time`
  will read UNMEASURED live. Pyrelands uses `jawa/map_info` / `time_date_at` instead.
- Tile choice uses `jawa/world_tile_export extended=true` CSV (raw fields incl. waterCovered,
  roadCount, riverCount, mutatorCount, lat) + `jawa/world_neighbors` CSV for rings / distance.

- 🔴 PLAN §3.1 CONFLICT (not worldgen): `sarg.alphabiomes` is listed to EXCLUDE, but the composed
  `mandrake.rm.biomes` About.xml hard-depends on it (MEASURED via modset_builder.scan/close_over on
  the installed set, 2026-10-01: closure = 20 mods incl. sarg.alphabiomes, sarg.alphaanimals,
  VEF, vfe.insectoid2, mlie.starwarsanimalcollection, flowworks, luminouspigment, weathersuite).
  Excluding it is impossible; tier keeps it and relies on WildPlantAllowlist + bar 1 purity.
  The other four exclusions (geologicallandforms, biometransitions, mapdesigner,
  biomecompatibilityproject) are NOT in the closure -> guard holds.
- modset_builder.order() already warns: biomes forced with unmet order on rut.patches (cycle);
  pre-existing, not this item's.
- `rimworld/load_game_ready` is a PRE-condition check (traps.md); fixture reload uses
  `rimworld/load_game saveName` + poll `get_ui_state.programState == Playing`.

- `RM_BiomesSettings.enabled` is a Dictionary<string,bool>; `jawa/mod_settings_field` coerces only
  bool/int/float/double/string/enum, so it CANNOT read it. Pre-flight reads the per-biome toggle
  from the Config `Mod_*RM_BiomesMod*.xml` on disk (absent key/file = ON) and says so.

- §3.4 step 7 "temperature matches the target within ±3" cannot be literal for a cell read: the
  seasonal + daily cycle moves outdoor temp several °C around the tile mean. Implemented as:
  tile RAW temperature == written target ±0.5 (hard) + ≥20 unroofed non-burning cells within ±3
  of map outdoorTempNow (hard, uniformity) + cell median vs target recorded as CALIBRATING (not
  gating) until the owner rules.

## built
- `modset_builder.py`: TIERS["pyrelands"] (its `forbid` list rides FlowWorks' `tier_guard`) + `resolve_tier()`.
- `src/RimMandrake/Pyrelands/preflight_pyrelands.py`: gates A/B/C, row ids = plan §3.8/§3.2/§3.3.
- `src/RimMandrake/Pyrelands/northstar_site.py`: §3.4 recipe (fresh quicktest -> raw-field tile pick
  -> re-tile 2 rings -> strip mutators -> isolate -> generate -> home -> census hook -> midsummer
  noon -> save+stat -> restore toggles (finally) -> load_game reload). `--plan` prints it offline.
- `src/RimMandrake/Pyrelands/selftest_pyrelands_site.py`: 117 checks vs FakeGame/FakeEnv; every
  gate-A/B row refuses its dirty case by row id; UNMEASURED refuses; manifests == validation.py;
  DEFAULTS == C# initialisers; site recipe end-to-end + finally-restore + no overwrite + no resend.
  Falsification probe (mutated DEFAULTS / LOG_FATAL / LAT_MAX) -> 5 failures, as it should.
- run_selftests.py: 81/83, the 1 FAIL is pre-existing selftest_sound_paths (TheForge/Wasteland).
- Plan §3.1 corrected: sarg.alphabiomes cannot be excluded (hard dep of the composed mod).

## status
DONE offline. Nothing here touched the game, bridge or ModsConfig.

## needs bridge
