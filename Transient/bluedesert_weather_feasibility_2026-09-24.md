# Blue Desert weather engine feasibility — 2026-09-24

Instrument: RimSage MCP (decompiled 1.6 engine + shipped defs) — every class/field below was read
from the decompiler this session, not from docs. Our own mod XML read from `src/`.
Sitting: BLUEDESERT_DESIGN_SITTING_1, engine-feasibility half. Design source:
`design/Jawa/worldbuilding/biomes/the_blue_desert.md` §4b.

Headline: **all three weathers are essentially pure XML.** Odyssey 1.6 shipped the exact
mechanisms we assumed would need C#: a full sand-accumulation grid driven by a
`WeatherDef.sandRate` field, a weapon **range cap** field (`maxRangeCap`, used by BlindFog),
and a weather **move-speed multiplier** consumed directly in `Pawn.TicksPerMove`.

## 1. Ice-sand drift — verdict: **pure XML to ride Odyssey sand; small C# only for the blue tint**

### Measured evidence

- `Verse.WeatherDef` (Verse/WeatherDef.cs:7–108) carries `public float sandRate;` alongside
  `rainRate`/`snowRate`. Odyssey's `Sandstorm` def sets `<sandRate>1.6</sandRate>`.
- `RimWorld.SteadyEnvironmentEffects.DoCellSteadyEffects` (read in full): for every unroofed
  outdoor cell, if `sandRate > 0.001` it calls `AddFallenSandAt(c, 0.046f * SandRate)` — Perlin-
  noised (freq 0.04, 5 octaves, floor 0.5×), so accumulation is naturally **patchy and drift-like**,
  identical in shape to snowfall. Gated `if (ModsConfig.OdysseyActive)` — we always ship all five
  expansions (owner ruling 2026-09-19), so this gate is open in every test list.
- **Erosion is built in**: when sandRate ≤ 0.001 (weather over) or the cell is indoors, the same
  tick does `map.sandGrid.AddDepth(c, -1f/180f)` (`SandDissipateRate`). Sand self-clears over
  in-game hours after the storm; snow does NOT (it only melts above 0 °C — `MeltAmountAt`
  returns 0 below freezing, so on a cryogenic map snow is permanent until shoveled).
- `Verse.SandGrid` (Verse/SandGrid.cs) is a byte-for-byte sibling of `SnowGrid`: per-cell float
  0–1, saved via `Scribe_Deep` on `Map` (Map.cs:137, 897), zeroed under `Fillage.Full` buildings
  (`CanCoexistWithSand`, Building.cs:148) — so it piles **around** structures and never on them —
  and requires `TerrainDef.holdSnowOrSand` (same field governs both grids).
- **Burying/gameplay**: `Verse.AI.PathGrid:169` adds `WeatherBuildupUtility.MovementTicksAddOn(map.sandGrid.GetCategory(c))`
  — deep sand slows movement exactly like deep snow. `JobDriver_ClearSnowAndSand` is one vanilla
  job clearing both grids together; construction/floor jobs zero it (JobDriver_ConstructFinishFrame:72).
- **Rendering**: `Verse.SectionLayer_Sand` draws it (`DebugViewSettings.drawSand = true` by
  default — DebugViewSettings.cs:11 — so it renders in normal play). Material is
  `MatBases.Sand = MatLoader.LoadMat("Misc/Sand")` — a **global engine Resources material**, tan,
  shared by every map. Vertex alpha = depth; Biotech pollution tints via a second texture channel.

### What needs C# vs XML

- **XML only**: a `RM_IceSandDrift` WeatherDef with `sandRate`, `WeatherOverlay_SandHard` (or a
  gentler custom overlay), cold `temperatureRange`, sky colors, thought. Accumulation, drifts,
  path-cost burying, auto-erosion, pawn clearing, save/load — all free.
- **Small C#** (optional, cosmetic): the drift will render **tan**, not blue-white ice. The sand
  material is global (`Misc/Sand` from engine Resources, not a moddable texPath), so an ice-blue
  tint needs a tiny Harmony patch — e.g. postfix `SectionLayer_Sand.Regenerate` to swap/tint the
  submesh material when `map.Biome == RM_BlueDesert` (instantiate the material once; do not touch
  the shared static). ~50 lines, EnvironmentalHazards-sized.
- **Real C#** (recommend DROP): wind-directional leeward drifting (piling on the downwind face
  only). Vanilla accumulation is isotropic Perlin. Nothing in the engine reads wind direction into
  either grid. The Perlin patchiness already reads as drifts; directional physics is a project.

### Def sketch

```xml
<WeatherDef>
  <defName>RM_IceSandDrift</defName>
  <label>ice-sand drift</label>
  <description>Wind-blown water-ice sand piles against everything standing.</description>
  <temperatureRange>-999~-20</temperatureRange>
  <sandRate>1.4</sandRate>                    <!-- accumulation + auto-erode after -->
  <windSpeedFactor>1.5</windSpeedFactor>
  <windSpeedOffset>1.25</windSpeedOffset>
  <accuracyMultiplier>0.8</accuracyMultiplier>
  <moveSpeedMultiplier>0.8</moveSpeedMultiplier>
  <preventSkygaze>true</preventSkygaze>
  <preventsShuttleLaunch>true</preventsShuttleLaunch>
  <weatherThought>BlowingSand</weatherThought>  <!-- or an RM_ thought -->
  <overlayClasses><li>WeatherOverlay_SandHard</li></overlayClasses>
  <!-- sky colors: pale blue-white, per Sandstorm's Overcast block re-hued -->
</WeatherDef>
```
Named C# piece (only if the tint is wanted): `RM_BlueDesert.SandTintPatch` — Harmony postfix on
`SectionLayer_Sand.Regenerate`, per-biome material tint. Terrain check owed at authoring time:
Blue Desert terrains set `holdSnowOrSand` (vanilla naturals default true; verify ours).

Alt considered: riding `snowRate` instead (snow is already blue-white, and below 0 °C it never
melts → permanent burial, shovel-only). That is a legitimate *harsher* design — permanent
accumulation, no auto-erosion — and is zero C# including color. A def could even carry both
rates. This is the one design question for the owner (see table).

## 2. The Haze — verdict: **pure XML; hediff (if wanted) reuses our own EnvironmentalHazards kit, zero new C#**

### Measured evidence

- Cosmetics are all stock `WeatherDef` fields: 4× `SkyColorSet` (day/dusk/nightEdge/nightMid, each
  sky/shadow/overlay/saturation — full re-hue to blue-white), `maxGlow` (dimming), `overlayClasses`,
  `ambientSounds`, `weatherThought` (mood), `windSpeedFactor`. `Verse.WeatherWorker` (read in full)
  instantiates overlays from `WeatherPartPool` and lerps sky colors; no worker subclass needed for
  a veil (the only vanilla worker subclass is `WeatherWorker_TorrentialRain`, for flooding).
- Vanilla overlay roster (search `class WeatherOverlay_`): Fog, FogBlind, Rain, ToxRain,
  TorrentialRain, SnowGentle, SnowHard, SnowBlizzard, SandHard, Fallout, NoxiousHaze, BloodFog,
  DeepBloodFog, DeathpallFog, GrayPallFog, GrayPallAsh, DeathpallAshes, UnnaturalDarkness,
  BloodRain, HateChant. Nearly all are `WeatherOverlayDualPanner` two-line subclasses (one
  material, two pan speeds) — a custom soft blue-white `RM_WeatherOverlay_Haze` with our own
  texture is a ~10-line class, and `WeatherOverlay_Fog`/`GrayPallFog` work as-is with zero C#.
- The ONLY vanilla weather→hediff route is `doToxicBuildup`: `WeatherWorker.WeatherTick:88` →
  every 3451 ticks, all spawned pawns (minus `immuneToGameConditionEffects`) get
  `ToxicUtility.DoAirbornePawnToxicDamage`. Hardwired to toxic buildup — not reusable for a
  custom cryo hediff.
- **Our precedent already solves this**: `src/RimMandrake/EnvironmentalHazards/Source/EnvironmentalWeatherExtension.cs`
  is a `DefModExtension` with `hediffToApply` + `hediffSeverityPerInterval` and a
  `carrierHediff` mode where `RM_HediffComp_EnvironmentalExposure` reads weather/roof state from
  inside the hediff (with `severityPerDayUnexposed` decay). Built to replace donor acid-rain;
  attaching it to a Haze WeatherDef is pure XML from here.

### Def sketch

```xml
<WeatherDef>
  <defName>RM_TheHaze</defName>
  <label>the haze</label>
  <description>A soft veil of cryogenic hydrocarbon mist descends.</description>
  <temperatureRange>-999~-40</temperatureRange>
  <favorability>Neutral</favorability>
  <maxGlow>0.85</maxGlow>
  <windSpeedFactor>0.5</windSpeedFactor>
  <weatherThought>RM_HazeThought</weatherThought>          <!-- new ThoughtDef, XML -->
  <overlayClasses><li>WeatherOverlay_Fog</li></overlayClasses> <!-- or RM_WeatherOverlay_Haze -->
  <!-- sky colors: blue-white, saturation ~0.8 -->
  <modExtensions>
    <li Class="RimMandrake.EnvironmentalHazards.EnvironmentalWeatherExtension">
      <carrierHediff>RM_HazeExposure</carrierHediff>       <!-- new HediffDef, XML -->
    </li>
  </modExtensions>
</WeatherDef>
```
Caveat on the modExtensions wiring: verify the exact hookup EnvironmentalHazards expects (it may
attach via its GameCondition rather than reading WeatherDef extensions directly) — that is a
read of our own source at build time, not an engine unknown.

## 3. Ice fog (diamond dust) — verdict: **pure XML — Odyssey's BlindFog IS this weather**

### Measured evidence

- **Accuracy**: `WeatherDef.accuracyMultiplier` confirmed (Core Fog = 0.5).
- **Range**: vanilla 1.6 HAS weapon range reduction — `public float maxRangeCap = -1f;`
  (WeatherDef.cs:51). Consumers measured: `VerbProperties.cs:318–320` clamps verb range to
  `weatherManager.CurWeatherMaxRangeCap`; `ThingDef.cs:2256` (stat display), `VerbTracker.cs:137`
  (UI warning on the gizmo), `Building_TurretGun.cs:614` (turrets below minRange go dark),
  `RoyalTitlePermitWorker_Targeted.cs:41` (orbital permits clamped). No Harmony, no stat part.
  Odyssey ships it live: `BlindFog` = `accuracyMultiplier 0.5` + `maxRangeCap 22.9` +
  `WeatherOverlay_FogBlind` + threat-small letter.
- **Movement**: weather CAN slow pawns in vanilla — `public float moveSpeedMultiplier = 1f;`
  consumed at `Pawn.cs:3247` (`num3 /= CurMoveSpeedMultiplier` in TicksPerMove), lerped across
  weather transitions (WeatherManager.cs:65). Nine shipped weathers use it (Blizzard 0.7,
  Sandstorm 0.8, Rain 0.9 …). No hediff, no stat patch.

### Def sketch — copy BlindFog, re-hue, add the slow

```xml
<WeatherDef>
  <defName>RM_IceFog</defName>
  <label>ice fog</label>
  <isBad>true</isBad>
  <description>Suspended ice crystals glitter in the air, blinding shooters and slowing everyone.</description>
  <temperatureRange>-999~-30</temperatureRange>
  <accuracyMultiplier>0.5</accuracyMultiplier>
  <maxRangeCap>22.9</maxRangeCap>
  <moveSpeedMultiplier>0.8</moveSpeedMultiplier>
  <windSpeedFactor>0.5</windSpeedFactor>
  <preventsShuttleLaunch>true</preventsShuttleLaunch>
  <letterDef>ThreatSmall</letterDef>
  <letterLabel>Ice fog</letterLabel>
  <overlayClasses><li>WeatherOverlay_FogBlind</li></overlayClasses>
  <!-- sky colors: bright glittering blue-white (diamond dust is BRIGHT, unlike gray fog) -->
</WeatherDef>
```
Zero C#. Optionally a custom sparkle overlay subclass (~10 lines) if FogBlind's gray reads wrong.

## Verdict table

| weather | verdict | cost | the one design question left |
|---|---|---|---|
| Ice-sand drift | XML rides Odyssey `sandRate`/SandGrid; +~50-line Harmony tint if blue is required | ~1 day (tint incl.) | Sand grid (tan-unless-tinted, auto-erodes) vs snow grid (blue-white free, but permanent below 0 °C — shovel-only)? |
| The Haze | pure XML; exposure hediff reuses our EnvironmentalHazards extension, zero new C# | hours | Mood-only, or an actual RM_HazeExposure hediff on unroofed pawns? |
| Ice fog | pure XML — Odyssey BlindFog + `moveSpeedMultiplier`, verbatim | hours | How harsh: BlindFog's 0.5 acc / 22.9 cap, or softer for a common weather? |

All three ride Odyssey-gated systems (sandGrid, maxRangeCap ships in an Odyssey def but the field
is Core `Verse.WeatherDef`); Odyssey is always in every test list per the 2026-09-19 ruling, and
the campaign requires it regardless.
