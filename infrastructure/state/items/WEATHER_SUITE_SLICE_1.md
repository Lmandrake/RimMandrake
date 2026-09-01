# WEATHER_SUITE_SLICE_1 — tidally-locked weather, v1 slice

Green-lit slice of `design/Jawa/proposals/weather_suite_deep_design.md` (owner,
2026-09-01). Glass storms, static seasons, spore blooms, pressure tides,
mirages all WAIT for PROPOSAL_SUITE_REVIEW_1 — build ONLY the v1 ladder.

## spec

Per the doc's §1, §5, §8:
1. **Terminator storms**: the permanent weather WALL where dayside heat meets
   nightside cold — a fixed-geometry band (arc-distance from the substellar
   point decides membership; the world is frozen so the band is authorable
   as data, no simulation). Maps inside the band get the storm-wall weather
   set; crossing the band with the gravship is a felt event (warning letter +
   condition on the traverse). Nearly free once the arc-distance test exists.
2. **Dark-side auroras**: nightside-band WeatherDef, visual + mood event,
   almost no C#. The one beauty of the dark.
3. **Tier 0–1 forecasting**: folk signs (inspect-string tells on existing
   weather) + the instrument building that reads upcoming weather — every
   later weather system needs this reader; build it first.

## verify

(a) A map inside the terminator band draws from the storm-wall weather set and
one outside it never does — MEASURED by forcing weather rolls on both via dev
tools/bridge; (b) auroras occur only on nightside-band maps; (c) the forecast
building's prediction matches the actual next weather in a logged multi-roll
test; (d) validate_patch + clean Player.log.

## criteria

Band membership driven by authored data (tile list or arc test) with the SAME
fingerprint discipline as other derived artifacts; auroras and forecasts
observed live in a quicktest; no per-tick C# in any weather path.

## Watch out

- Biome weather commonalities interact with FIRE_ECOLOGY_LOOP_1's table edits —
  the two items patch NEIGHBORING data; coordinate xpaths so neither clobbers
  the other (both anchor on distinct `<li>` keys, never whole-node replace).
- The world map is FROZEN: the band is authored once against the real planet;
  never compute it from worldgen parameters (there is no worldgen).
- WeatherDefs with `isBad` affect caravan/incident logic globally — check what
  vanilla reads before flagging.

## 2026-09-01 — offline build, all three units, not deployed

No concurrent-attempt collision found before starting: `git log --oneline |
grep -i weather` showed only the design-doc and green-light commits, and
`git status` had no stray weather files. Built solo, no fork.

**Tier decision** (`design/NAMING_SCHEME_PLAN.md`'s own tests, same split
FIRE_ECOLOGY_LOOP_1 used). `mandrake.rsw.weathersuite`
(`src/RimStarWars/WeatherSuite/`) carries the mechanism only: a
`PlanetGeometryDef` type (substellar lat/lon + two band-arc pairs) and the
great-circle arc test any tidally-locked SW planet could reuse unchanged, a
`MapComponent_TerminatorBand` that starts the front and sends the crossing
letter, an `IncidentWorker_NightsideAurora` gate, and the forecast-instrument
comp. No Ash'karr numbers, no clan/story references — passes the RSW test.
`mandrake.rut.weathersuite` (`src/RimUtinni/AshkarrWeatherSuite/`) ships the ONE
`PlanetGeometryDef` instance with Ash'karr's real substellar point and band
arcs, plus the folk-sign flavor patch — passes the RUT test (names this
planet, this biome's neighbor data, this clan's register).

**Band data, not invented.** Substellar point (0,0) and the terminator band
(arc 63–117) are NOT new numbers — they're the exact figures
`the_one_map.md` already reconciled and the exact arc range the Twilight Sea
(63→120) and Grey Sea (70–108) already sit in
(`ASHKARR_WORLD_DEFINITION.md`). The nightside-aurora band starts exactly
where the terminator band ends (117), so no map ever carries both at once —
a design choice, not a second measurement. Checked directly against
`world/ASHKARR_WORLDMAP_tiles.csv` (21,872 rows, `measure csv` fingerprint
`sha256:b38fd68569237c96`): the substellar-point formula reproduces the
CSV's own `arc` column exactly on tile 0 (lat 58.2787, lon -90 → arc 90.0,
both ways), and **only 5 of the Pyrelands' (`ZBiome_Grasslands`) 227 tiles
fall inside the terminator band** (arc 63.81–68.82, its extreme edge) — the
two items' geography barely touches, confirmed rather than assumed.

**Coordination with FIRE_ECOLOGY_LOOP_1.** Read
`src/RimUtinni/PyrelandsFireEcology/Patches/PyrelandsWeather_Stage0.xml` and
`PyrelandsWeather_BlackRain.xml` before writing anything. Their patches
touch `BiomeDef[defName="ZBiome_Grasslands"]/baseWeatherCommonalities` — a
per-BIOME commonality table. This item's terminator-storm/aurora bands are
per-MAP-TILE geometry (a `MapComponent` checking the map's own `Tile.arc`),
not a biome-weather-table edit at all, so there is **no shared xpath and no
biome-table touch of ZBiome_Grasslands anywhere in this build**. The one
place this item DOES touch a weather table is the Tier-0 folk-sign patch,
which replaces `description` only on five GLOBAL vanilla `WeatherDef`s
(Clear, Fog, DryThunderstorm, SnowGentle, SnowHard) — a different def type,
a different field, from FIRE_ECOLOGY_LOOP_1's `BiomeDef`/
`baseWeatherCommonalities` edits. No collision possible; verified by
xpath, not assumed.

**What got built, all three units:**

1. **Terminator storms.** `RSW_WS_TerminatorFront` `GameConditionDef`
   reuses vanilla `GameCondition_Flashstorm` UNCHANGED (RimSage-verified:
   periodic above-ambient lightning) — zero new C# for the mechanical
   payload. The one new C# (`MapComponent_TerminatorBand`, auto-registered
   by RimWorld's own `typeof(MapComponent).AllSubclassesNonAbstract()`
   scan — no Harmony needed) starts it PERMANENT
   (`GameConditionMaker.MakeConditionPermanent`) on any map whose tile
   arc falls in the geometry def's terminator band, idempotently (checks
   `GetActiveCondition` first, safe across save/load), and sends a
   one-time neutral letter on first arrival (any arrival — settling,
   caravan or gravship; the letter is not gravship-specific, since there
   is no existing gravship-flight-plan hook in this repo to intercept a
   mid-flight crossing without building one, and the item's own "do not
   overbuild" line rules that out for v1). **Deferred, not built**: the
   literal two-toned dust/haze curtain render doc §1 describes, and any
   navigation-penalty/mishap/electronics-risk mechanic during an actual
   gravship flight — both are v2 polish, not required by this item's
   verify (a) or (d).
2. **Dark-side auroras.** `RSW_WS_DarkAurora` `GameConditionDef` reuses
   vanilla `GameCondition_Aurora` UNCHANGED (mood-buff sky brightening,
   floor glow 0.73 — doubles as the doc's "partial sight-range
   restoration" for free, RimWorld's own visibility math already scales
   off ambient glow). `RSW_WS_DarkAurora` `ThoughtDef` reuses vanilla
   `ThoughtWorker_Aurora` UNCHANGED — it already reads its OWN def's
   `gameCondition` field rather than hardcoding vanilla's defName, so this
   needed no C# at all. The only new C#:
   `IncidentWorker_NightsideAurora`, a one-method subclass of vanilla
   `IncidentWorker_Aurora` adding "at least one player-home map is in the
   nightside band" on top of everything vanilla's own worker already
   checks. Vanilla's own `Aurora` incident/condition/thought are untouched
   and still fire everywhere, unmodified — this is purely additive.
3. **Tier 0–1 forecasting.** Tier 0: `AshkarrWeather_FolkSigns.xml`
   replaces `description` on 5 vanilla `WeatherDef`s with folk-sign flavor
   text, each wrapped in `PatchOperationConditional` (validator advisory,
   addressed). Deliberately does not reference static seasons or glass
   storms (v2, not built). Tier 1: `RSW_WS_WeatherInstrument`
   (`ParentName="BuildingBase"`, 20 Steel, reuses vanilla's own
   `Things/Building/Misc/DropBeacon` texPath rather than shipping a
   placeholder — confirmed via RimSage against `OrbitalTradeBeacon`, a
   currently-loading def using that same path) carries
   `CompForecaster.CompInspectStringExtra()`, which replicates
   `WeatherDecider.CurrentWeatherCommonality`'s PUBLIC surface (biome
   table, temperature range, favorability, rain gates, active-condition
   factors, tile mutators) read-only — never touches `Rand`, so it can
   never desync from the roll it reports on. It cannot see the one
   PRIVATE gate (`ticksWhenRainAllowedAgain`) — a deliberate, named gap,
   not an oversight, and exactly the Tier-1 "crude, imprecise" register
   the doc's own §8 asks for.

**Validation.** `dotnet build WeatherSuiteHook.csproj -c Release` — 0
warnings, 0 errors. `validate_patch.py` run against the REAL live load set
(`--defs` on RimWorld's `Data`, `Mods` AND the Steam Workshop content
folder, `--mods-config` on the live `ModsConfig.xml`): **589/589 active
mods found on disk, 9,113 def files, 0 errors, 1 advisory warning** (the
`DropBeacon` texPath — expected and explained above; vanilla's own textures
live in asset bundles the validator cannot scan). The folk-sign patch's 5
xpaths each show exactly 1 live match in `Core: Weathers.xml`, confirmed
against the running mod list, not guessed. No live def dump
(`DefDump/captures/...`) was found on disk this session to cross-check
against — pointing `--defs` at the raw mod folders instead gave full
589/589 resolution, a stronger check than the dump would have been for
structural (`ParentName`/`Class`) validation, though it cannot see
resolved/patched XML the way a live dump can.

**What a live quicktest needs to check**, per this item's own verify list:
(a) force weather rolls on a terminator-band map (arc 63–117, e.g. near the
Twilight Sea or Grey Sea) and a control map outside it — the band map
should carry `RSW_WS_TerminatorFront` permanently (`Info` panel/dev tool),
the control never should; (b) force/roll `RSW_WS_DarkAurora` and confirm it
never fires with no player-home map in the nightside band (arc ≥ 117), and
does fire when one exists; (c) read `RSW_WS_WeatherInstrument`'s inspect
string next to several actual `StartNextWeather()` rolls (dev tool) and log
predicted-top-candidate vs. actual outcome across a batch — expect the
predicted top pick to win at roughly its reported percentage rate, not
every single time (this is a probabilistic Tier-1 reading, not a
deterministic peek — see the "what got built" note above for why); also
confirm the crossing letter fires once on first map-in-band and not again
on reload. (d) already run above, clean.

Not deployed, not committed, per scope: this is FOUNDRY's offline build for
the owner's live pass.
