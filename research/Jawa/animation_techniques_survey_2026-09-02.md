# RimWorld 1.6 animation techniques survey — 2026-09-02

Web + local research answering the owner's ruling: study how mods actually animate
things, then map our seven live animation needs to the cheapest adequate technique.
Read-only research; nothing deployed or committed by this pass.

## 1. Vanilla primitives

| Primitive | What it achieves | XML-only? | Notes |
|---|---|---|---|
| **FleckDef** + `FleckMaker`/`FleckMaker.Throw` | Short-lived particle: texture, `fadeInTime`/`solidTime`/`fadeOutTime`, `growthRate`, `rotationRate`, `speedPerTime`, `altitudeLayer`. Drawn via `FleckDrawer_Basic` (free-floating) or `FleckDrawer_Attached` (tracks a Thing/position). | Visual **is** XML-only. The spawn *call* (deciding when/where to throw one) needs one line of C# somewhere with a tick — a comp, a WeatherEvent, a JobDriver. | This is the cheapest lever in the whole survey: define the look in XML, write ~10–30 lines of C# to call it on a cadence. |
| **MoteDef / `MoteThrown` / `MoteAttached`** | Thing-derived mote; `MoteAttached.Attach(Thing)` makes it follow a moving pawn every frame. Same fade/grow/solid timing fields as flecks, interpolated per-tick in C#. | Same split as flecks — XML defines the curve, a C# call spawns/attaches it. | No multi-frame "flipbook" motes exist; apparent animation is scale/alpha/rotation interpolation only. |
| **WeatherDef.overlayClasses** | Names a C# `SkyOverlay` subclass (`WeatherOverlay_Rain`, `_Snow`, `_Fog`) to render as a full-screen scrolling layer. | Reusing a shipped overlay class is XML-only (cite the class). **No vanilla ash/ember/dust overlay class exists**, and there is no `worldOverlayPanSpeed` field on WeatherDef — pan speed is hardcoded per-class in C#. | A genuinely new panning/wind-reactive overlay needs a new C# `SkyOverlay` subclass — the expensive route. |
| **Graphic_Flicker** | Vanilla's only true per-tick "animated" Graphic — randomly swaps between two textures at an interval (torches/braziers). | **XML-only to use** (`graphicClass: Graphic_Flicker`, two texture variants) — the flicker logic already ships in the class. | No shipped `Graphic_Animated`/flipbook class exists; anything beyond 2-state flicker needs a custom `Graphic` subclass. |
| **ShaderTypeDef** | `Cutout`, `CutoutComplex`, `Transparent`, `TransparentPostLight` (ignores map light — self-illuminating, used for the Doomsday rocket glow), `Mote`, `MoteGlow` (additive glow, standard for particles). | XML field (`shaderType`) — zero C#. | **None of the vanilla shaders scroll/pan a UV.** A scrolling-texture look has to be faked with fleck/mote motion, not a shader trick, unless you write custom HLSL (see PixelWizardry below). |
| Pawn render-offset by terrain | No confirmed vanilla mechanism for a pawn's `drawPos.y` progressively changing while standing still on one tile. The closest real thing is deep-water rendering, which is fragile (a known 1.3 bug had pawn heads float separately from bodies after leaving deep water) — evidence the render tree *can* be split/offset per body part, but nothing ships a "sink over time" curve. | — | **This appears to be a genuine gap in the entire ecosystem**, confirmed below under item 5 of the table. |

Sources: rimworldwiki.com/wiki/Modding_Tutorials, rimworldmodding.wiki.gg, RW-Decompile mirror (`Verse/WeatherDef.cs`, `Verse/GraphicData.cs`, `Verse/PawnRenderer.cs` — josh-m/RW-Decompile), Scurvyez/PixelWizardry (custom HLSL blend-mode shaders — confirms new shaders are a C#-assembly undertaking, not XML).

## 2. Notable mods, verified against source where possible

- **Dubs Bad Hygiene — steam is pure XML, zero C#.** Pulled `1.6/Defs/Effects/Mote_Visual.xml` directly from `github.com/Dubwise56/Dubs-Bad-Hygiene`:
  ```xml
  <FleckDef ParentName="FleckBase_Thrown">
    <defName>Fleck_SteamRoom</defName>
    <graphicData><texPath>DBH/Things/Mote/steam2</texPath></graphicData>
    <altitudeLayer>MoteOverhead</altitudeLayer>
    <fadeInTime>2</fadeInTime><solidTime>2</solidTime><fadeOutTime>5</fadeOutTime>
  </FleckDef>
  <FleckDef ParentName="FleckBase_Thrown">
    <defName>Mote_WashSteam</defName>
    <graphicData><texPath>DBH/Things/Mote/steam1</texPath></graphicData>
    <altitudeLayer>MoteOverhead</altitudeLayer>
    <fadeInTime>1</fadeInTime><solidTime>0</solidTime><fadeOutTime>2</fadeOutTime>
    <growthRate>0.12</growthRate>
  </FleckDef>
  ```
  This is the exact recipe for river steam: a `FleckBase_Thrown`-derived def, a soft steam PNG, `growthRate` to billow it as it rises. The only C# needed is a periodic spawn call over river-edge cells (a MapComponent tick, ~20 lines).

- **VEF AnimalBehaviours (`Vanilla-Expanded/VanillaExpandedFramework`, `Source/VEF/AnimalBehaviours/`)** — confirmed via source, not just search snippets:
  - `CompFloating`/`HediffComp_Floating` + `StaticCollectionsClass.floating_animals` — **this is NOT a render-offset/bobbing effect.** Pulled the consumer (`Pawn_PathFollower_CostToMoveIntoCell_Patch.cs`, the only other file referencing `floating_animals`): it's a **pathfinding-cost exemption** (ignore terrain move-cost, vacuum-survival flag), same family as a "waterstriding" stat. An earlier pass of this research flagged it as a sink/bob precedent — that's wrong, verified and corrected here (no visual effect touches this list at all).
  - `CompGraphicByTerrain` + `PawnRenderNode_GraphicByTerrain` (pulled both files) — this **is** a real, shipped visual-state mechanism: a `PawnRenderNode` subclass whose `GraphicFor()` swaps to `graphic.path + comp.Props.waterSuffix` (or `lowTemperatureSuffix`/`snowySuffix`/a generic `suffix[]` array indexed by `indexTerrain`) when the pawn's tile terrain matches a tracked state (`Water`/`Cold`/`Snowy`/custom), re-dirtying the render cache on transition. Confirmed hardcoded to those three named states plus one generic custom-suffix slot — extending it to a new state name is a small C# edit, not zero-code, but the pattern (discrete sprite-swap keyed to terrain, done through a real `PawnRenderNode`) is proven and already shipped if VEF is a dependency.
  - PipeSystem (`Source/PipeSystem/PipeSystem/Graphic/`) pipe visuals are static auto-linked mesh sprites (`Graphic_LinkedPipe`, baked via `Printer_Plane` into the map's `SectionLayer_Resource`) — **no animated flow-along-pipe or flicker/pulse visual exists in PipeSystem.** Not a source for a "flowing resource" look.
  - `[NL] Facial Animation` — confirmed Harmony-dependent (listed dependency), swaps facial-expression textures by pawn mood/action state; source is not public (no GitHub found), so the exact render hook (RenderNode vs raw Draw patch) is unconfirmed. Not directly relevant to our 7 needs (facial state, not one of them).

- **RJW Animation Framework** (`rjw.miraheze.org/wiki/RJW_Animation_Framework`, source `gitgud.io/c0ffeeeeeeee/rimworld-animations`) — the **one genuine keyframed-animation engine** found in the whole ecosystem: XML defines animations as ordered **keyframes** with a `tick` value (strictly increasing), a `Root` node for whole-body transform plus independently-movable child parts, first/last keyframe matched for seamless looping. Built for the RJW adult-content ecosystem, but the underlying technique (per-part position+rotation keyframes on a tick timeline, played back by a small C# player) is transferable to a squirming-creature or tentacle-sway look. **Caveat:** direct fetch of the wiki was blocked (403); field names above come from search-result excerpts only and must be re-verified against the actual GitLab source before any field name is quoted in a build spec.

- **Save Our Ship 2** (`KentHaeger/SaveOurShip2`) — confirmed to exist, heavy C#/Harmony, but the specific classes driving thruster motes / starfield parallax / hull-breach fire could not be located via search alone. **Mechanism unconfirmed** — would need a direct source pull to use as a citable precedent.

- **"Moyo" water shader** — dead lead. No RimWorld water-shader mod by this name found; "Moyo" hits were a swimming-pet creature mod using the vanilla move-speed-stat approach, not a shader.

- **"Vanilla Effects"** — does not exist as a distinct Vanilla Expanded submodule. Not found.

- **Giddy-Up** (`rheirman/GiddyUpCore`) — confirmed mechanism: per-facing (N/S/E/W) `offsetDefault`/`offsetFemale`/`offsetMale` x/y/z triples place the rider as an extra render layer at a fixed offset from the mount's root. **Positional layering, not gait/limb animation** — no leg-sync found.

- **Aquarium (Continued)** (Workshop 2194463553) — places real pawns (fish) inside a bounded room/container with tuned movement smoothing. This is full pawn AI in a box, not a lightweight "squirming contents" trick — not a cheap precedent for a tank visual.

- **Submerged directional wake** — no mod precedent found anywhere (searched swimming mods, "Some Things Float", aquatic-creature mods). This is a build-it-yourself construction from vanilla flecks, not a copied technique.

## 3. Mapping: our 7 items → cheapest adequate technique

| # | Need | Cheapest adequate technique | XML / C# split |
|---|---|---|---|
| 1 | Pawn visibly sinking into tar tile-by-tile | No real precedent exists (VEF's `CompFloating` looked like one but is a pathfinding-cost flag, verified NOT visual). Cheapest adequate: reuse VEF's **`CompGraphicByTerrain` + `PawnRenderNode_GraphicByTerrain` pattern** — 3–4 discrete "sink depth" sprite-suffix variants swapped as a timer-on-tile hediff/comp advances, giving a staged sinking read without a continuous offset. True continuous per-tick `drawPos.y` sink needs a **new** Harmony patch on `PawnRenderer`/`Pawn_DrawTracker` — nothing ships this today. | Staged version: XML art (3-4 sprite states) + small C# comp extending the VEF pattern (or a standalone equivalent, ~80-150 lines). Continuous version: new C# render patch, larger and untested territory. |
| 2 | Animated steam rising from rivers (`RIVER_STEAM_ANIMATION_1`) | Direct, verified precedent: **Dubs Bad Hygiene's `Fleck_SteamRoom`/`Mote_WashSteam`** recipe — `FleckBase_Thrown` + soft steam texture + `growthRate`/`fadeInTime`/`fadeOutTime`. | XML-only for the look; ~20 lines of C# (a MapComponent ticking over river-edge cells) for the spawn cadence. Cheapest item on this whole list. |
| 3 | Ember-swarm weather, drifting glowing particles | `FleckDef` with `shaderType: MoteGlow` (or `TransparentPostLight` for a self-illuminating look ignoring map light) thrown across the map on a wind-biased cadence by a small custom `WeatherEvent`. No vanilla ember overlay exists, so skip the `SkyOverlay` route — flecks are cheaper and already support glow shaders. | XML for the glow-particle look; a small C# `WeatherEvent` tick-spawner (reads `Map.weatherManager`/wind) for cadence and screen coverage. |
| 4 | Ash blowing / vortexing in wind | Same family as embers: `FleckDef` with `rotationRate` + `speedPerTime`, thrown with an angle biased by the map's wind vector; vortex read comes from per-fleck randomized rotation, not a new mechanic. No vanilla ash/dust weather overlay confirmed to exist. | XML for the sprite/rotation curve; the same small wind-reading `WeatherEvent` as #3 (can likely share one C# class with different FleckDef parameters). |
| 5 | Submerged V-shaped wake around a propane lake | No mod precedent found anywhere — genuinely build-it-yourself. Two mirrored `FleckDef` ripple sprites (angled via `rotationOffset`) spawned each tick at the mover's position, offset left/right of heading. | XML for the ripple sprite/fade curve (reuses standard fleck fields entirely); a short C# comp (~30-50 lines) on the mover to compute heading and spawn point each tick — same complexity class as the river-steam spawner. |
| 6 | Live-ingredient tanks with squirming creatures | No clean precedent (Aquarium mod is full pawn AI, too heavy). Cheapest adequate: **`Graphic_Flicker`** (vanilla, ships the flicker logic) swapping between 2 "squirm pose" textures for the contents, layered inside the tank building's graphic — reads as idle motion with zero C#. If more organic motion is wanted later, RJW Animation Framework's keyframe technique is the upgrade path (needs re-verification of its schema first, see caveat above). | XML-only (two texture variants + `graphicClass: Graphic_Flicker`) for the cheap version; no C# needed at all. |
| 7 | "Study other mods that make custom animations to inspire ourselves" | Satisfied by this survey. The one finding worth deeper study later: **RJW Animation Framework** is the only real keyframed per-part animation engine in the RimWorld modding ecosystem (tick-indexed keyframes, a `Root` transform node, child parts, loop via matched first/last keyframe) — the technique to reach for if we ever want true skeletal-style motion beyond sprite-swap/render-offset tricks. Its exact field schema is UNVERIFIED (source fetch blocked 403) and needs a direct pull from `gitgud.io/c0ffeeeeeeee/rimworld-animations` before quoting it in a build spec. | — |

## 4. What's UNKNOWN / needs a second look before building

- **Item 1 (tar sink)** is the one real gap in the survey — no mod anywhere does continuous per-tick render-offset sinking. The staged-sprite-swap fallback is proven-cheap but not the same visual as the owner asked for ("tile-by-tile" reads as continuous or near-continuous). Confirming feasibility of a `PawnRenderer` Harmony patch (and its interaction with the apparel/equipment render tree) needs a short spike before committing art or a queue item to the continuous version.
- **RJW Animation Framework's exact XML schema** (keyframe field names, `ExtendedKeyframe` shape) is UNVERIFIED — search-excerpt only, direct fetch 403'd. Do not cite specific field names from it in a build ticket without pulling the GitLab source directly first.
- **SOS2's thruster/starfield/breach effect classes** are UNCONFIRMED — known to exist, mechanism not located.
- **Whether a vanilla "Dust Storm"/ash weather overlay class exists at all in 1.6** was not conclusively ruled in or out (search for "Vanilla Weather Expanded" specifically came back empty — likely a misremembered mod name, not confirmation of absence). Worth one direct check against the live def dump before assuming ember/ash weather needs a from-scratch `WeatherEvent`.

File: `/mnt/d/Luke/dev/Rimworld/research/Jawa/animation_techniques_survey_2026-09-02.md`

## UNKNOWN resolved (BENCH, 2026-09-02, MEASURED against shipped Data XML)

Vanilla 1.6 DOES ship a blowing-particulate weather overlay:
`WeatherOverlay_SandHard` (plus Rain/TorrentialRain/ToxRain/Fog/Snow variants,
14 overlayClasses blocks total in Data). ⇒ ember-swarm and blowing-ash weather
start as a retexture/subclass of `WeatherOverlay_SandHard` — not a
from-scratch WeatherEvent; the fleck spawner is only needed for the localized
vortex/glow accents.
