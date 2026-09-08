# Planet Preset Prime (local) — validation walk
subject: src/RimMandrake/PlanetPresetPrime  (packageId `mandrake.rm.planetpresetprime`)
deps: `oblitus.mylittleplanet` (My Little Planet, third-party, loadAfter only — NOT a hard modDependency; the mod degrades gracefully to vanilla-only priming when absent)
list: minimal+mylittleplanet
status-hint: dev ergonomics fix, not player-facing — a Harmony postfix on `Page_CreateWorldParams.Reset()` primes `planetCoverage=1.0` and My Little Planet's subdivision slider to 7, so opening the world-creation page defaults to Ash'karr's own 21,872-tile size (coverage 1.0 / subcount 7) instead of RimWorld's hardcoded default (119,904 tiles). It PRIMES, not LOCKS — a slider/button drag still overrides it.

## must be true
- On EVERY load (not gated on the page ever opening), `PlanetPresetPrimeMod`'s static constructor logs `"[RimMandrake.PlanetPresetPrime] loaded: will prime coverage 1, subdivisions 7. MLP type <found|ABSENT>."` — its absence means the mod failed to load at all (the mod's own comment names this exact silent-failure trap, JAWABENCH_HAS_NO_INIT_LINE_1).
- Opening `Page_CreateWorldParams` (the world-creation page) exactly once sets `planetCoverage` (private field, set reflectively) to `1.0` and logs `"[RimMandrake.PlanetPresetPrime] ready: coverage 1, subdivisions 7, MLP slider <primed|ABSENT (vanilla subdivisions set anyway)>"`.
- `PlanetLayerSettingsDefOf.Surface.settings.subdivisions` is set to 7 regardless of whether My Little Planet is present.
- If My Little Planet IS present, `WorldGenRules.WorldGenRules.subcount` (reflectively) is ALSO set to 7, and set BEFORE the vanilla field — so MLP's own slider-draw transpiler reads 7 back and does not stamp its own default (10) over the vanilla value on the first drawn frame.
- If the `planetCoverage` field is ever renamed by a game update, the mod must log a WARNING (`"...planetCoverage not found; coverage not primed. The field was renamed by a game update."`) rather than crash or silently do nothing.

## the walk
1. [L] Player.log after load contains `"[RimMandrake.PlanetPresetPrime] loaded: will prime coverage 1, subdivisions 7. MLP type "` — check this on EVERY load regardless of whether the world-creation page is ever opened this session, since the page may never open   # load-time
2. [B] rimworld/execute_debug_action or a direct UI-open route to `Page_CreateWorldParams` (confirm the correct trigger — likely reachable only via the main-menu "Create world" flow, which may need `rimworld/start_debug_game`-adjacent navigation; pin the exact call before running) → Player.log line `"[RimMandrake.PlanetPresetPrime] ready: coverage 1, subdivisions 7, MLP slider "`
3. [D] after step 2, read back the opened page's `planetCoverage` field value (reflection, since it is private — use whatever bridge accessor reads arbitrary fields, or confirm via `jawa/world_info_get`/`jawa/world_stats` once a world is actually generated from that page) → expect `1.0`, and expect `PlanetLayerSettingsDefOf.Surface.settings.subdivisions` = 7
4. [B] generate a world from the primed page with no slider touched → `jawa/world_stats` (or `jawa/world_info_get`) tile count = 21872 (coverage 1.0 at subdivisions 7) — this is the actual end-to-end proof the priming worked, more concrete than reading the page's private fields
5. [L] confirm the log line from step 2 appears only ONCE per session even if the page is closed and reopened (the `reported` bool guard in `Patch_Page_CreateWorldParams_Reset`) — reopening should still show the primed values but should not re-log "ready"

## anti-guessing notes
- This mod ships no XML defs; every string above is quoted verbatim from `src/RimMandrake/PlanetPresetPrime/Source/PlanetPresetPrime.cs`.
- `src/RimMandrake/Utils/w9_run.py` independently refuses to import a world whose tile count is not 21872 — that guard is a SEPARATE defence layer from this mod and is out of scope for this walk (it lives in Utils/, not this mod), but step 4's expected count is the same number both layers agree on.
- No [S] line: purely a numeric-default fix, nothing visual.
