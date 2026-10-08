# Solar Mirrors — full design pass (SOLAR_MIRRORS_MOD_DESIGN_1)

## 0. Ruling and scope

Owner, typed 2026-10-04, on the Long Shade mirror field (`design/Jawa/worldbuilding/biomes/longshade_shade_ideation_2026-09-29.md` N6 and W3): *"I like this. Should be its own RimMandrake mod. Solar Mirrors. Heliostats. Static mirrors. We should do a full design pass on this mod to make sure it's feasible in the current engine, both Claude and GPT. Then propose fun extensions to make it full and rich."* He chose the **full puzzle-map version** (W3), not the single set-piece (N6).

This document is the design pass. Item: `SOLAR_MIRRORS_MOD_DESIGN_1`. The mod is `src/RimMandrake/SolarMirrors/`; what is built per phase is the **Status** column of §6.1, and the remainder is `SOLAR_MIRRORS_BUILD_1`.

## 1. What exists

### 1.1 Our shade/sun stack (all in `src/RimMandrake/CreatureBehaviors/Source/`, packageId of that assembly's mod)

The mirror mod is almost entirely a **consumer and one new layer** on machinery that already ships. Read before designing (CLAUDE.md "this project keeps having already built it"):

| File | Lines | What it gives a mirror mod |
|---|---|---|
| `RM_MapComponent_ShadeGrid.cs` | 1018 | The keystone. `ShadeAt(cell)` 0..1, `ExposureAt(cell)` 0..1 by heat kind, `ExposureFor(pawn)`. Layers: `roofShade`, `castShade` (directional strips along the sun vector), `gearShade` (tents/shield lees), `parasolShade` (refreshed every 250 ticks), `movingShade` (gloomcast; dirty-rect: old rect cleared, new rect written, every 60 ticks), `glareFloor` (sand). Full-map `Recompute()` every **2000 ticks** or on `recomputeRequested`. **Not saved** — rebuilt on `FinalizeInit`. `GridVersion` bumps on each recompute. |
| `RM_SunHeatMath.cs` | ~340 | Pure math, self-tested: `Exposure(kind, outdoors, roof, thickRoof, cast, gear)`, `WithCover`, `WithGlareFloor`, `CastInto` (ray-strip rasteriser along a direction), `FillRect`, `PathCost`, `KindFromElevation`. |
| `RM_MapComponent_PinnedSun.cs` | 292 | Golden-hour pinned sun on biomes with `RM_PinnedSunExtension` (**the Long Shade carries it**, `src/RimMandrake/LongShade/Defs/BiomeDefs/RM_LongShade.xml:271`). Never-expiring `WeatherEvent` overriding sky glow, colour and the **shadow vector**; public `ShadowDirection`, `SunElevationDegrees`, `ShadowLengthPerHeight`. |
| `RM_SunHeatExtension.cs`, `RM_SunHeatPatches.cs` | 161, 241 | The one-kind-of-heat implementation: exposure feeds a **vanilla** temperature offset per pawn (heatstroke), and a sun **path-cost grid** handed to vanilla pathing via `PathRequest.IPathGridCustomizer` (`RM_SunPathCustomizer`; a NEW customizer object per rebuild, because PathFinder caches by identity). |
| `RM_ShadePatchGraph.cs`, `RM_ShadeHop.cs`, `RM_JobGiver_WanderInShadeGrid.cs`, `RM_JobGiver_FollowShadowCaster.cs` | — | The herd behaviour: shade patches (8-connected), a distance field across open sun, patch-to-patch hop edges; animals hop shade to shade and dash across sun. Rebuilt lazily when `GridVersion` moved. **This is what "herds re-route live" rides on — for free, if the mirror layer feeds exposure.** |
| `RM_GlareBlind.cs` | 102 | Glare-blind hediff on vanilla Sight, gene/apparel immunity (`RM_GlareProtectionExtension`, `RM_SunGoggles`). Already a "blinding" mechanic keyed on exposure+glare floor. |
| `RM_ShadeGear.cs` + `EnvironmentalHazards/Defs/ThingDefs_Buildings/RM_ShadeGear.xml` | 168 | SHADE_GEAR_FAMILY_1: shade per heat kind. Mirrors are its exact inverse (anti-shade). |
| `RM_Mirage.cs`, `RM_CompFalseShadeAmbusher.cs` (mirrak) | — | Things that already lie about shade. |

**There is no `RM_JobGiver_Dash` class** — the dash is part of `RM_ShadeHop.cs` / the patch graph's §6 ring. The brief's name was a paraphrase.

Two facts that shape the whole design:

1. **On the Long Shade the sun is pinned.** A frozen mirror under a frozen sun throws a **fixed** beam. That is why the ruin's lock is solvable and stable — it is physically coherent, not a contrivance. Off the Long Shade the sun moves, so a fixed mirror's beam **sweeps** through the day, and that is the job a powered heliostat does: hold a target while the sun moves.
2. **The engine has no per-cell sun.** The feasibility doc the shade grid cites (`design/Jawa/worldbuilding/desert_ecology_feasibility.md` §2): GlowGrid's sky term and outdoor temperature are map-wide scalars. "Lit by a mirror" must therefore be **our own grid**, exactly like shade — confirmed for 1.6 in §2.

### 1.2 Related items (live)

`SOLAR_HEAT_EXPOSURE_1`, `LONGSHADE_BEDAZZLE_MECHANICS_1` (pinned sun), `LONGSHADE_BEDAZZLE_CONTENT_1`, `LONGSHADE_SHADE_EXTRAS_1`, `LONG_SHADE_FIRST_SCRIPT_1`, `STILLSAND_SOLAR_STILL_1` (a solar still — a concentrator neighbour; check before building the furnace extension), `SHADECRAFT_LESSONS_DESIGN_1`.

### 1.3 Installed mods (MEASURED 2026-10-04)

Swept every `About.xml` `<name>`+`<description>` across both roots (`…/common/RimWorld/Mods`, `…/workshop/content/294100`; 1,419 unique files — drvfs globbed each twice by case) for `mirror|heliostat|solar concentrat/furnace/oven/tower/reflect|reflector|heliograph|sunlight|light beam|spotlight|lens`. **Sanity probe:** "gravship" hits 43 mods, so the sweep can see.

**No mirror, heliostat, reflector, heliograph or solar-concentrator mod is installed.** Every "mirror" hit is texture mirroring or the verb ("mirroring the shape of"). The two relevant neighbours:

- **Dubs Skylights** (`Dubwise.DubsSkylights`, workshop 833899765, has a 1.6 assembly) — a roof tile that lets sky glow through. Precedent that a building can feed the vanilla glow grid per cell; read its approach before writing our glow path.
- **Alien Worlds – Tidally Locked** (`7f.alienworlds.tidallylocked`) — sunlight-locked world; relevant to the nightside/Terminator extension only.

## 2. Engine feasibility (measured)

Engine facts below are from RimSage against the decompiled 1.6 source, 2026-10-04, unless marked as our code.

### 2.1 Verdict

**Feasible, with no engine wall.** Every piece is a standard extension point or a layer on our own shade grid. Nothing needs a transpiler. The one real risk is **visual legibility of a lit patch inside a rendered shadow**. That needs the owner's eyes and cannot be measured offline (§2.8).

### 2.2 Projecting a beam onto distant cells

- **Line of sight is vanilla and cheap.** `GenSight.PointsOnLineOfSight(IntVec3 start, IntVec3 end, Action<IntVec3> visitor)` (`Verse/GenSight.cs:161`) is a non-allocating Bresenham visitor. **It skips the END cell**: its loop runs `while (num5 > 1)`, so the target cell is never visited, while the `IEnumerable` overload yields it (`Verse/GenSight.cs:127-192`). The blocker test must check the target separately. *(Found by the GPT consult, confirmed in RimSage.)* The allocating `IEnumerable` overload must not be used per recompute.
- **What blocks the beam (v1, conservative):** a wall-like edifice (`fillPercent ≥ 0.8` or impassable, which is the shade grid's caster threshold), natural rock, a **closed** door, and **any roof, along the path or over the target**. The only exceptions are explicit aperture and receiver defs (§5 E1/E2). The mirror's own footprint is excluded, and each spot cell is tested separately, so a spot can be partly clipped. Pawns never block a beam, and an open door never blocks. A big plant halves the beam (optional). *(The first draft let beams fly over roofs but not walls. GPT called that inconsistent, and it was. Taken.)*
- **Spot shape.** The target is a cell the player picks, not an angle. The lit spot is the mirror's footprint, centred on the target (1×1 for a hand mirror, 2×2 static, 3×3 heliostat). A flat mirror throws a spot its own size. Real sun divergence adds about 0.01 cells per cell of range, which is ignored.
- **Efficiency is the cosine law, in 3D.** Light delivered = `η = sqrt((1 + dot(s, t)) / 2)`. Here `s` is the unit vector from the mirror toward the sun, built from the azimuth (the pinned sun's `ShadowDirection`, negated; check the sign convention in the selftest) **and** `SunElevationDegrees`. `t` is the unit vector from a mirror face at a fixed nominal height (1.5 cells) to the target on the ground. *(The first draft used a 2D `cos(θ/2)` on bearings only. GPT showed that under an overhead sun that gives 0–1 by azimuth where the truth is ~0.71 in every direction. Taken.)* On the Long Shade (elevation 2–30°) azimuth still dominates, so the puzzle geometry survives: Throwing light back toward the sun side scores 100%. Throwing it sideways scores ~71%. Throwing it straight downsun falls toward 0. That is real heliostat physics, and it creates the puzzle geometry for free: a mirror lights the shadow of a rock best when it stands downsun of the rock and faces back at it.
- **Collectors and relays are different things.** A *collector* reads the **mirror-free** sun at its own face: its footprint's mean source exposure, from a query that excludes the mirror layer, because reading the composed `ExposureAt` while building that same layer would feed it back into itself. A *relay* is a mirror whose input is **another mirror's beam**. It reflects that beam's incoming direction and **consumes** its energy, attenuated by its own reflectivity, so a barely lit relay throws a barely lit beam and no loop can manufacture light. The relay graph is built from zero every pass and is **acyclic** (a mirror appears once per path), with a depth cap of 4. *(The first draft let any mirror whose cell was lit fire a full-strength beam. GPT showed that this lets loops create energy and hold stale light. Taken in full.)*

### 2.3 Subtracting from the shade grid (our code)

`RM_MapComponent_ShadeGrid` (`src/RimMandrake/CreatureBehaviors/Source/RM_MapComponent_ShadeGrid.cs`) already composes layers: roof, cast, gear, parasol, moving, glare floor. Light is a new **`mirrorLight[]`** layer (0..N, where N > 1 means concentration) with a defined place in the order:

```
base exposure  = Exposure(kind, roof, thickRoof, cast, gear)        (unchanged; this is also the mirror-free source query)
lit exposure   = max(base, min(1, mirrorLight))                      (NEW: light un-shades)
cover          = parasol / moving shade / worn gear, applied AFTER   (a parasol still shades you in a beam)
glare floor    = unchanged
ShadeAt        = 1 − lit exposure, for every consumer that means "is this shade"   (NEW: ONE source of truth)
irradiance[]   = raw mirrorLight, unclamped, kept separately           (concentration > 1 for receivers only)
```

*(The first draft had `ShadeAt = shade × (1 − light)` beside `max(...)` for exposure. GPT showed that the two disagree: base 0.3 with light 0.6 gives exposure 0.6 but implied shade 0.28. Shade is now derived from the final exposure the pathing and patch graph already read. Taken.)* Only the cached layers apply the light: `ExposureAt` must not apply it a second time over a cache that already holds it.

It is applied in `RebuildHeatLayers` (so the **path-cost grid and the shade-patch graph both see it**) and live in `ExposureAt`/`ShadeAt`.

**Coupling choice — the one structural decision.** Solar Mirrors is its own mod (`mandrake.rm.solarmirrors`). It reaches the grid through a **small public hook added to CreatureBehaviors**: `RM_MapComponent_ShadeGrid.RegisterLightSource(IRM_LightLayer)`, which is a provider that fills a float[] on request. **Contract (per GPT):** register in `PostSpawnSetup` and unregister in `PostDeSpawn`. The grid owns the buffers. The grid exposes `SourceExposureAt` (mirror-free) for providers. The rebuild order is explicit (baseline → light providers → composed exposure → path costs → patch graph), and `GridVersion` bumps once for all of them, so glow, exposure, path cost and graph never disagree. CreatureBehaviors stays mirror-agnostic, and SolarMirrors declares a hard dependency on it. That is the same shape as `RegisterGear` / `RegisterMovingCaster`. Rejected: a Harmony postfix from SolarMirrors onto `ExposureAt`. It works, but it misses the cached exposure array that pathing and the patch graph read, which is exactly the half the herd re-route needs.

### 2.4 Visible light: the glow grid

- **`GlowGrid.GroundGlowAt(c, ignoreCavePlants, ignoreSky)` is the single funnel** (`Verse/GlowGrid.cs:244`). It feeds plant growth (`Plant.cs:220,245,356`), `StatPart_Glow` (work and move speed in the dark), `WorkGiver_GrowerSow` (is this cell sowable), `ThoughtWorker_SwallowedByDarkness`, `SectionLayer_Darkness` and the mouseover readout. The logic: unroofed returns `CurSkyGlow`, and if that is below 1 it returns `max(sky, min(0.5, glowers))`, **unless the accumulated glow's alpha is 1 ("overlit"), which returns 1.0.** Overlit comes from `CompProperties_Glower.overlightRadius` (`Verse/GlowGrid.cs:129-151`, the sun lamp's mechanism). So a vanilla glower *can* reach 1.0 within its overlight radius, but it is a circle around the glower, never a spot half a map away, and re-flooding glowers on every aim change is the expensive path. The postfix stays the mechanism. *(Corrected after the GPT consult. The first draft said glowers were hard-capped at 0.5.)*
- **Mechanism:** a Harmony **postfix on `GroundGlowAt`** returning `max(__result, mirrorGlow[i])`, guarded by a null array and the setting. It costs one array read on a hot path, the same cost profile as Dubs Skylights (installed, 1.6), which proves the pattern lives on real lists.
- **What it buys, by biome.** In normal daylight the sky glow is already 1 outdoors, so mirror glow changes nothing mechanically, and that is correct. **On the Long Shade the pinned sky glow is 0.8** (`src/RimMandrake/LongShade/Defs/BiomeDefs/RM_LongShade.xml`, `RM_PinnedSunExtension.glow`), so a mirror-lit patch reads **1.0**, and vanilla plant growth (growMinGlow 0.51 → optimal 1.0) rises measurably there. On the Terminator / low-sun biomes and at dusk the effect is larger. At night there is no sun to reflect, so mirrors give nothing. That is honest.
- **Dirtying:** when the mirror layer changes, call `map.mapDrawer.MapMeshDirty(cell, MapMeshFlagDefOf.GroundGlow)` **and `map.events.Notify_GlowChanged(cell)`** (GPT; `GlowGrid.DirtyCell` does both) on the changed cells. Gameplay glow is not visual glow: `SectionLayer_LightingOverlay` reads `VisualGlowAt`, so the postfix never brightens the rendered ground, and that is why §2.5 has its own layer. **Crop caveat (MEASURED):** `Plant.Resting` is a clock test (`DayPercent < 0.25 || > 0.8`, `RimWorld/Plant.cs:277`), so crops rest 45% of the day under the pinned sun, mirrors or not. That is a Long Shade fact, not a mirror one, and it bounds the crop benefit (`GlowGrid.DirtyCell` does the same plus `Roofs`). Do not call `GlowGrid.DirtyCell`, because that would also re-flood vanilla glowers for nothing.

### 2.5 Rendering the beam and the spot

- **Spot:** *(revised after GPT: `CellBoolDrawer` scans the whole map on regen and draws at `AltitudeLayer.MapDataOverlay`, which paints over things and looks like a zone. It is kept for the **aim preview and the debug overlay only**.)* Persistent light is our own `SectionLayer` with explicit altitude, additive blend and fog masking. The original note was: a `CellBoolDrawer` (`Verse/CellBoolDrawer.cs`; the constructor takes `extraColorGetter` per cell, so intensity can vary) owned by the mirror map component and `MarkForDraw`n each frame, with `SetDirty()` on layer change. It costs one mesh per map. Alternative: our own `SectionLayer` subclass, which `Section`'s constructor auto-instantiates for every subclass (`Verse/Section.cs:48`), with a custom `MapMeshFlagDef` (it is a Def in 1.6, `RimWorld/MapMeshFlagDef.cs`) for per-section regen. Start with the CellBoolDrawer (≈30 lines) and move to a SectionLayer only if the alpha-blended wash reads as fog rather than light.
- **Beam:** drawn **centrally from the map component's `MapComponentUpdate`**, not from the mirror's `PostDraw`, because a mirror off-screen is culled while its beam crosses the screen (GPT). It is one stretched quad per active mirror with an additive mote-glow material (`ShaderDatabase.MoteGlow`) along mirror → target. A dozen draw calls per frame is trivial. Add a faint dust shimmer only if it reads well.
- **Vanilla shadows do not know about the light.** `SectionLayer_SunShadows` still draws the rock's shadow over a lit patch. The overlay must visibly **beat** the shadow, and that is the legibility risk (§2.8).

### 2.6 Heat, under "one kind of heat"

- **Outdoors, mirror light raises exposure and nothing else.** Exposure already drives the per-pawn vanilla temperature offset (heatstroke) through `RM_SunHeatPatches`. A lit patch is simply "sun" again, which satisfies the ruling with no new hediff.
- **Concentration (light > 1, several beams on one cell)** scales exposure past 1 into the same offset, capped by the extension's existing `maxOffsetC`. It is still vanilla heat. Any burn or ignite effect (a weapon extension) must go through vanilla fire (`FireUtility.TryStartFireIn`) and vanilla heatstroke, never a new "solar burn" hediff.
- **Outdoor cell temperature cannot be raised.** MEASURED: `GenTemperature.PushHeat` → `Room.PushHeat` returns false and does nothing when `UsesOutdoorTemperature` (`Verse/Room.cs:635`). **Indoors it works**: a beam into a roofed room through an open door or a glazed opening (§5 greenhouse/furnace) can `PushHeat` at a receiver building. So the solar furnace is a **receiver building**, never a hot cell.
- **Heat kinds:** under `ambient` heat (steam/volcanic), shade does nothing, and **light does nothing either**. Mirrors are inert on ambient biomes for heat but still give glow. Under `lowSun`/`overhead`, they work as specified.

### 2.7 Update cost, rotation and save/load

- **Layer recompute:** dozens of mirrors × a Bresenham walk of up to ~500 cells (the walk visits about |dx|+|dz| cells, per GPT, not the diagonal's 355) is ~25k cell reads, plus spots, ×≤4 relay depths. That is **estimated** at about a millisecond, **UNMEASURED** until P1 profiles it at 1× and 3× speed, including the path-cache and patch-graph work it triggers. It is small enough that so no dirty-rect bookkeeping is needed for the mirror layer itself.
- **Cadence (revised after GPT: a scheduler, not just a hash).** Cheap light/exposure updates are separated from the expensive caster rebuild. Changes are compared **quantised** (light to 0.05), never as exact floats. Expensive work is coalesced with a **maximum latency** of 250 ticks, and removals publish at once. The original rule: the mirror layer recomputes every **250 ticks** and on any mirror event (rotate, build, destroy, repair, power change), with **change detection** (hash the layer). Only when it actually changed does it set the shade grid's `recomputeRequested`. The expensive part is that full grid rebuild (62,500 cells for casters, a new path customizer, then the lazy patch graph), and it already runs every 2000 ticks today. A rotation therefore costs **one extra grid rebuild**, the same as the existing parasol/gear events. A wall built across a beam is caught within 250 ticks.
- **Heliostats under a moving sun** (any biome without a pinned sun) re-aim on the 250-tick cadence. Their spot does not move, but its **intensity** does (sun angle, weather, partial shadow), so quantised change detection decides whether that is a rebuild. *(The first draft claimed tracking heliostats never change the layer, and GPT showed that this was false.)* Only *static* mirrors under a *moving* sun sweep. Their sweep is quantised by the scheduler (light to 0.05, max latency 250 ticks): they step, and do not glide.
- **Save/load (revised after GPT):** each mirror saves its **actual orientation (the surface normal)**, not just a target. A static mirror commits the normal its re-aim job computed under that moment's sun, and the spot then follows the sun from that normal; obeying a saved target forever would make it a heliostat. It also saves the requested target, pending re-aim, condition and owner-lock, and the puzzle saves its identity and an **unlock latch**. This state lives in a `ThingComp.PostExposeData`. The light layer is **not saved** and is rebuilt on `FinalizeInit`, exactly like the shade grid (which has no `ExposeData` at all). Removing the mod leaves ordinary buildings that fail to load, the standard RimWorld mod-removal cost, and no map component state is orphaned.
- **Budget on a 250×250 map with 48 mirrors (estimates, to be profiled):** mirror layer ~1 ms per 250 ticks, one array read per `GroundGlowAt` call (unmeasured; cache the map lookup and allocate nothing), render ~50 extra draw calls. The only material cost is the existing full shade rebuild, which mirror events can trigger at most once per 250 ticks (throttle).

### 2.8 Risks, ranked

1. **Legibility.** A lit patch must read as *light*, inside a shadow the vanilla renderer still draws. This is UNMEASURABLE offline and needs an owner-watched sitting (§6).
2. **Rebuild storms.** A player spinning mirrors could trigger a full shade rebuild every 250 ticks. The throttle caps it. If profiling shows a hitch, add a real dirty-rect pass to the shade grid's cast layer, which is the one place dirty-rect work would pay.
3. **Patch-graph churn on herds.** Re-routing is what the owner wants, but animals mid-hop toward a patch that just vanished must fail gracefully. The existing `GridVersion` staleness check is designed for exactly this. Confirm it in the first script.
4. **Cross-mod hook.** It needs a small public API added to CreatureBehaviors (§2.3). That is a two-mod change, and CreatureBehaviors' files go DIRTY for code review.

## 3. Mod scope

### 3.1 Identity (tier grammar, `design/NAMING_SCHEME_PLAN.md`)

- Folder `src/RimMandrake/SolarMirrors/`, packageId **`mandrake.rm.solarmirrors`**, name "RimMandrake: Solar Mirrors", namespace **`RimMandrake.SolarMirrors`**, def prefix **`RM_`**. It is franchise-free, so no Star Wars name is needed. Invented flavour names are allowed in RM (Q11a).
- Hard dependency: `mandrake.rm.creaturebehaviors` (the shade grid, pinned sun, sun heat). The Long Shade set-piece is **inside this mod**, gated on the biome carrying a new `RM_MirrorFieldExtension`, which the Long Shade's BiomeDef gets by a `MayRequire="mandrake.rm.solarmirrors"` `<li>` in its `modExtensions` (the existing pattern on that file). Solar Mirrors therefore works on every map, and the puzzle appears where a biome asks for it.

### 3.2 The buildings (v1)

| Def | What | Aim | Power | Size | Research |
|---|---|---|---|---|---|
| `RM_SignalMirror` | hand-sized mirror on a post; the cheap one | target cell, set by a **re-aim job** (Construction, ~600 ticks) | none | 1×1, 1×1 spot | none (neolithic) |
| `RM_StaticMirror` | stuffable framed mirror (steel/silver/gold/plasteel; stuff sets reflectivity 0.6–0.95) | target cell by re-aim job; **does not track**, so under a moving sun its spot sweeps | none | 2×2, 2×2 spot | Smithing |
| `RM_Heliostat` | powered two-axis tracker | target cell set **instantly by gizmo**; holds the target as the sun moves | 150 W while tracking; unpowered it freezes in place and becomes a static mirror | 3×3, 3×3 spot | Electricity |
| `RM_SunStone` (receiver plate) | a floor-flush plate that reads "lit / unlit" | — | — | 1×1 | — |

- **Aiming UI:** a gizmo "Aim at…" opens a cell targeter that shows a **live preview**: the beam line, the spot, the efficiency %, and red where the line is blocked. For a static mirror, confirming designates a re-aim job and a pawn walks over. The heliostat applies at once.
- **Inspect string:** target, efficiency, delivered light, what blocks it, "in shadow — dark" when the mirror itself is unlit (§2.2).
- **Sun-stones** emit a signal (lit/unlit) usable by the puzzle and by players' own builds, for example a sun-stone that toggles a door or a turret through a `CompFlickable`-style hook. This is optional in v1.
- **Mirrors degrade:** dust/sand storms (the existing weather) add a "dusty" condition that cuts reflectivity until a cleaning job runs (a Cleaning work type job on the mirror). It is cheap, gives the mirror a maintenance loop, and costs nothing new in the engine.

### 3.3 Mechanics a mirror drives (all through existing systems)

1. **Shade off / sun on** in its spot: shade grid exposure (heat via vanilla offset), sun path costs, the shade-patch graph (herds), the heat soundscape (lit bed), glare blind (sand glare floor plus light).
2. **Glow on**: the `GroundGlowAt` postfix. Plants grow faster where the sky is dim (Long Shade 0.8 → 1.0), sowing is allowed where it was dark, and work speed improves at dusk.
3. **Concentration**: several spots on one cell sum. Light > 1 matters only to receivers (§5 solar furnace) and to heat (capped), never as a new heat kind.

### 3.4 The frozen array: the Long Shade puzzle-map (the W3 version he chose)

- **Set-piece:** a mapgen step (in Solar Mirrors, gated on `RM_MirrorFieldExtension`) places an **ancient mirror field** of **4–6** `RM_AncientHeliostat`s: unpowered, seized, each with **3 marked aim detents** (cut from 6–10 × 4–6 per GPT, for a smaller, fully validated and readable state space; the difficulty setting can raise it) (old brass target-pins on the ground the player can see), plus 2–4 **sun-stones** at a sealed objective and around it.
- **What the lock guards — ruled (a), the sealed vault (§7):** (a) a **sealed vault** whose door opens when all its sun-stones are lit, (b) a **shade road**: the right configuration carves a chain of shade patches across a sun gap that is otherwise impassable to a dashing colonist (the inverse use: mirrors kill the light that *other* mirrors throw by re-aiming them, so shade appears), (c) a **herd gate**: the configuration decides which way the giant herds migrate through the map: past the colony, through the colony, or into the canyon where the hunter waits.
- **Repair is the cost per move.** Each ancient heliostat must be repaired (components + Construction) before it can be re-aimed, and every re-aim costs a job. The puzzle is therefore a resource and time puzzle, not a slider. A repaired one can be powered and becomes a real heliostat, which is the reward.
- **Solvable, by construction.** The state space is small (6 mirrors × 3 detents = 729 configurations; exhaustive search with action-sequence checks is well under a second at mapgen). Mapgen **solves it before placing it**, and per GPT it validates **reachable action sequences**, not only a solved end state. Every ancient mirror's interaction cell must be reachable along a route a colonist can survive, given the shade the current configuration leaves, at each step. It keeps a layout only if (1) ≥ 1 reachable solution exists, (2) the start is unsolved, (3) the shortest solution needs ≥ 3 re-aims, (4) no chain exceeds 4, and (5) a reset path exists (re-aiming back is always possible). The sun-stones use **hysteresis**, and the vault's opening is **latched**, so a dust storm cannot shut it again. Escalating hints (missing input → first blocker → a useful next detent) appear in the inspect pane. Mapgen already has a `Survey` (`src/RimMandrake/LongShade/Source/RM_LongShadeMapgen.cs`) that builds the shade grid and patch graph on the generated map, so the solver uses the real grid rather than a model of it.
- **Readable:** detents are visible ground objects. Selecting an ancient mirror ghosts **every detent's spot** at once, so the player can see the options before paying for a job. Sun-stones glow when lit. The vault's inspect pane lists its stones lit/unlit. No hidden state.
- **Herds re-route live** with no new AI: the moment the layer changes, the shade grid rebuilds, the patch graph is stale by `GridVersion`, and the shade-hop AI re-plans. This is the payoff the owner named, and it is the first thing the debug script proves.

### 3.5 Mod Settings (superb, per CLAUDE.md)

Master toggles: **Mirrors affect shade/heat** · **Mirrors add light (glow)** · **Beam rendering** (off / spot only / spot + beam) · **Static mirrors sweep with the sun** (off = static mirrors behave as if the sun stood still) · **Ancient mirror fields on maps whose biome asks for them** (labelled *affects map generation*) · **Puzzle difficulty** (minimum re-aims 2/3/4; detents 4/5/6) · **Dust on mirrors** · Tuning: reflectivity multiplier, heliostat power draw, re-aim work amount, layer recompute interval (125–1000 ticks), max chain length. Defaults = shipped behaviour. All-off leaves inert decorative buildings.

### 3.6 What is NOT in scope

No new heat kind, no new hediff for light. No worldgen. No DLC-less path. No "laser" damage beam in v1 (it is a §5 option with its own costs).

## 4. GPT consult

One consult: `src/RimMandrake/Utils/gpt_consult.py`, model `gpt-6.1-sol`, effort high, 250 s, 2026-10-04. Sections 1–2 were inlined, and it was asked to critique feasibility and propose extensions. GPT's verdict: *"Feasible, but revise the optics, chain solver and invalidation contract before implementation."* Its engine claims cite the public decompile (Chillu1/RimWorldDecompiled, which is older than 1.6). **Every engine claim adopted below was re-checked in RimSage against 1.6.**

**Taken (and folded into §2–§3 in place, each marked):**

1. **3D efficiency** `sqrt((1+dot(s,t))/2)` with sun elevation, replacing a 2D bearing rule that was wrong under an overhead sun (§2.2).
2. **The roof rule was inconsistent.** Roofs now block along the path too, with explicit aperture exceptions (§2.2).
3. **`PointsOnLineOfSight`'s visitor skips the end cell** and walks ~|dx|+|dz| cells (CONFIRMED in RimSage, `Verse/GenSight.cs:161-192`) (§2.2, §2.7).
4. **Chains were physically incoherent.** They are now collectors vs relays, consume input energy, are acyclic, rebuilt from zero, and the collector reads a mirror-free source query (§2.2, §2.3).
5. **The shade and exposure formulas disagreed.** Shade is now derived from the final exposure, and raw irradiance > 1 is kept separately (§2.3).
6. **Glowers can reach 1.0 via `overlightRadius`** (CONFIRMED, `Verse/GlowGrid.cs:129-151`). The first draft's "capped at 0.5" was wrong (§2.4).
7. **Gameplay glow ≠ visual glow** (`SectionLayer_LightingOverlay` reads `VisualGlowAt`, CONFIRMED), plus `Notify_GlowChanged` on dirtying (§2.4).
8. **`CellBoolDrawer` is for previews and debugging only.** Persistent light uses a section layer, and beams are drawn centrally, not in `PostDraw` (§2.5).
9. **A scheduler with quantised change detection and max latency.** Heliostats *do* change intensity (§2.7).
10. **Static mirrors save orientation (the normal), not a target.** Save pending work and the puzzle latch, and give comps a register/unregister lifetime (§2.7, §2.3).
11. **Puzzle:** fewer mirrors and detents (4–6 × 3), validate reachable *action sequences* with a reset path, hysteresis and a latched unlock, escalating hints, and herds as live evidence rather than a requirement (§3.4).
12. **`Plant.Resting` is clock-based** (CONFIRMED, `RimWorld/Plant.cs:277`). That bounds the crop benefit on the pinned-sun biome (§2.4).
13. Extensions taken into §5: aiming planner (preview of shade/herd change before committing), raid sabotage of collectors, power-loss shutter, crop light allocation, local heliograph signalling (beam-driven switches), ruin restoration choices, anomaly containment lighting.

**Rejected:**

- **"Respect no worldgen: activate the array through a quest; no map-generation scattering."** This misreads the ruling. CLAUDE.md's ban is on **planet** generation (alternative worlds, worldgen as a capability). Map generation on landing is how every map exists, and the Long Shade already places mapgen set-pieces (the crawler road, `src/RimMandrake/LongShade/Source/RM_LongShadeMapgen.cs`). The field stays a **mapgen** set-piece gated on the biome. A quest-delivered variant is offered as an extension (§5 E8), not a replacement.
- **"Pathfinder customizer lifetime: verify old NativeArrays are released before disposal."** This is not rejected as false. It is out of scope here, because `RM_SunPathCustomizer` already retires customizers through `retiredCustomizers` (`RM_MapComponent_ShadeGrid.cs`). Mirrors raise how often that path runs, so the first script's rebuild-storm check covers it rather than this design re-deriving it.
- **Raid-role sabotage as a v1 feature.** GPT itself rates it L with a "distorts every raid" risk. It stays a §5 option.

Raw answer: kept in this session's scratchpad only. Everything load-bearing is above.

## 5. Extensions (options with costs)

Each is an independent add-on to the v1 in §3. Costs: **S** ≤ 1 day / ≤ 200 lines, **M** 1–3 days, **L** a week or more. Each says what it **buys** and what it **costs**. Rows marked *GPT* came from or were reshaped by the consult (§4).

| # | Extension | Buys | Costs / risk | Size |
|---|---|---|---|---|
| E1 | **Solar furnace / concentrator receiver.** A receiver building that counts light > 1 at its cells; above thresholds it runs smelting/glassmaking/cooking bills with no fuel (vanilla `CompRefuelable` replaced by `CompPowerTrader`-like "solar power" from concentrated light), and indoors it `PushHeat`s its room. Reuses `RM_PearlLens` (`STILLSAND_GLASS_LENS_CHAIN_1`) as a lens upgrade. | The reason to build a mirror *field* rather than one mirror: a fuel-free industry on the dayside; a deep Long Shade economy | Needs balancing against vanilla fuel; `RM_SolarStill` already ships as defs (`src/RimMandrake/Stillsand/Defs/ThingDefs_Buildings/RM_SolarStill.xml`); read it first so the still and the furnace share one receiver comp | M |
| E2 | **Mirror-lit greenhouse / crop light.** Beams into a glazed room (a glass-roof or glazed-wall def) raise glow inside and `PushHeat` it | Farming in dim biomes (Long Shade 0.8 glow, dusk/terminator), a sun-powered winter greenhouse | Needs a glazed roof or opening that lets a beam into a roofed room, which is the one real engine change (beam vs roof rule) | M |
| E3 | **Heliograph / signal mirror.** A colonist with a hand mirror flashes a friendly settlement or caravan on the world map: summon traders, call allies, coordinate a caravan rendezvous; on a map, flash a downed ally's position | A sun-gated comms system for pre-industrial colonies; ties to the "sun angle" play (works only by day, better at low latitude) | Comms-console overlap; needs a world-map range rule; vanilla `CommsConsole` callables can be reused | M |
| E4 | **Blinding defence.** A mirror aimed at a cell glare-blinds hostile pawns standing in its spot (uses existing `RM_GlareBlind` on vanilla Sight; goggles and the gene protect), and a **dazzle** accuracy penalty (`StatPart`) for shooters looking into a beam | A non-lethal, sun-gated defence and a reason for raiders to bring goggles; synergy with an existing mechanic | Must not become a free kill-box: raid AI never paths around it unless we add path cost for hostiles too (that is cheap: the sun path customizer already exists) | S–M |
| E5 | **Burning glass (weapon).** A concentrated spot (≥ 3 beams) ignites flammables (`FireUtility.TryStartFireIn`) and raises vanilla heat on pawns in it | Archimedes' death ray; a dramatic late-game trap | Exploit-prone, griefs own colony; needs strict concentration threshold and a setting; still one kind of heat (fire + vanilla heatstroke) | M |
| E6 | **Sun-angle play across biomes.** Mirror output scales with the tile's sun elevation (already computed: `STILLSAND_SUN_FROM_LATITUDE_1`), overhead sun makes mirrors weak (low cosine on a flat ground target), low sun makes them strong | A reason to care where on the planet you settle; Long Shade and Terminator become the mirror biomes | Pure maths on existing geometry; risks confusing players without a readout | S |
| E7 | **Terminator/nightside light relay.** On a tile at the terminator, a ridge-top heliostat catches the horizon sun and relays it down into the dark via a chain | Light in a dark biome, the only source of real daylight there; plants grow under it | Depends on the nightside/terminator biome content and its glow; chain length rules matter | M |
| E8 | **Ruins puzzles beyond the Long Shade.** The same lock (mirrors + sun-stones + detents) as a reusable ruin kit: tomb doors, a sun-dial vault, a "light the altar" ritual (Ideology `RitualBehaviorWorker` reward), and a **quest-delivered** field on any sunlit map (GPT's idea, taken as an extension rather than a replacement) | Turns one set-piece into a reusable content kit for any sunlit biome | Each new ruin is authored content; the solver generalises, but the art does not | M per ruin |
| E9 | **Mirror-herding (ranching).** Deliberately aim mirrors to drive a herd into a pen or onto a kill-route; tame animals that follow shade | The owner's "herds re-route live" turned into a player verb | Needs nothing new in AI; only design and a tutorial message. Risk: animals behaving oddly near the colony | S |
| E11 *GPT* | **Aiming planner.** Paused preview of what a re-aim does before it is ordered: "West becomes exposed; East becomes safe", beam strength, first blocker, the herd route change | Makes every mirror decision legible; the puzzle's main UI | Preview and committed simulation must be the same code path | M |
| E12 *GPT* | **Raid counterplay.** Some raiders target exposed collectors and receivers; mirrors are fragile (low HP, glass) | Mirror fields become something to defend | A broad targeting patch distorts every raid; gate it to a raid role | L |
| E13 *GPT* | **Power-loss shutter.** A heliostat on blackout freezes at its last actual orientation (becomes a static mirror that then sweeps); an optional shutter closes it | Makes power matter honestly; a blackout visibly changes the map | None beyond the orientation-save rule already adopted | S |
| E14 *GPT* | **Crop light allocation.** Prioritise limited light across growing zones; inspect "light-hours delivered" | Farming decisions in dim biomes | Concentration must never push vanilla growth past its optimum; bounded by `Plant.Resting` | M |
| E15 *GPT* | **Local heliograph switches.** A beam landing on a sun-stone drives a door, shutter, alarm or turret, with no wiring | A light-logic toybox; reuses the puzzle's sun-stone | Feedback circuits; propagation must stay bounded (relay graph is already acyclic) | M |
| E16 *GPT* | **Ruin restoration choices.** Repair the field's bearings, recover calibration clues, or dismantle it for parts (a breach outcome) | Player agency over the set-piece | Salvage must never leave a required objective impossible; the solver checks it | M |
| E17 *GPT* | **Anomaly containment lighting.** Route light into containment or work areas (Anomaly is assumed present) | A use in the darkness entities' game | Entity-specific behaviour must be read from source; brightness is not universal protection | M |
| E10 | **Sun-Debt rites (RUT tier, lore).** A Utinni ideoligion precept around light given and light taken; returning a mirror field's light to the herds as a ritual | Lore depth for the campaign | Campaign-only, sits in RimUtinni patches, never in this RM mod | S |

## 6. Build plan, sizes, first debug script

### 6.1 Phases (each lands and is pushed on its own)

| Phase | Work | Where | Size | Status (measured 2026-10-08) |
|---|---|---|---|---|
| P0 | **Hook in CreatureBehaviors:** `IRM_LightLayer` + `RegisterLightSource`, `mirrorLight[]` folded into `RebuildHeatLayers`, `ShadeAt`, `ExposureAt` in the §2.3 order; `RM_SunHeatMath.WithLight` (pure, selftested in `Source/SelfTest/Program.cs`) | `src/RimMandrake/CreatureBehaviors/Source/` | ~120 lines | Built (`99b61e39b`). |
| P1 | **Mod skeleton:** About.xml, csproj (`EnableDefaultCompileItems` explicit list if copying CreatureBehaviors' pattern), settings class, `RM_MapComponent_MirrorLight` (layer, 250-tick cadence, change hash, chain passes, throttle), `RM_CompMirror` (aim, efficiency, ExposeData), `RM_MirrorMath` (pure: Bresenham visitor, cosine efficiency, spot raster, blocker rule) with an offline selftest | `src/RimMandrake/SolarMirrors/` | ~600 lines C# | Built (`7c05c83da`; Verse-free kernel + seeded fuzz + mutation set `df37296d5`). |
| P2 | **Defs:** `RM_SignalMirror`, `RM_StaticMirror`, `RM_Heliostat`, `RM_SunStone`, re-aim and clean JobDefs + drivers, research, placeholder art (artpipe check first: `artpipe_state.py find mirror heliostat`) | same | ~250 lines XML + ~150 C# | Built except the clean job (dust); research uses vanilla Smithing/Electricity; art is placeholder. Remainder: `SOLAR_MIRRORS_BUILD_1`. |
| P3 | **Render:** light `SectionLayer` (additive, fog-masked), central beam drawing from the map component, CellBoolDrawer aim preview; `GroundGlowAt` postfix + `Notify_GlowChanged` | same | ~350 lines | Built, with the spot drawn per lit cell from the map component (additive, fog-masked) rather than a `SectionLayer`, and the aim preview as field edges rather than a `CellBoolDrawer`. |
| P4 | **Ancient field:** `RM_MirrorFieldExtension`, mapgen step, solver, detents, sun-stones, vault objective (ruled 2026-10-04) | same; reaches the Long Shade by a patch in this mod | ~700 lines | `SOLAR_MIRRORS_BUILD_1`. |
| P5 | Owner-watched sitting: legibility of the lit patch inside a shadow, beam look, the herd re-route | live, with him | — | Owed (needs the owner). |

**v1 total ≈ 2,100 lines plus defs and art; P0–P3 is a playable mod; P4 is the puzzle.**

### 6.2 First debug script (contract: `design/RimMandrake/debug_process.md` §2)

`src/RimMandrake/SolarMirrors/validation.py` (a modcheck `Suite`), plus the walk `design/validation_walks/RimMandrake/SolarMirrors.md` with `## must be true` lines, each ending `→ <chain>.<component>`:

1. Every SolarMirrors def is loaded with its comp and the extension resolves on `RM_LongShade` → `defs.present`
2. A static mirror aimed at a shaded cell lowers `ShadeAt` and raises `ExposureAt` there; un-aimed, it restores them → `light.unshade` (needs a bridge `[Tool]` reading the shade grid at a cell: `RM_ShadeProbe`, filed if absent)
3. A wall built on the beam line blocks it within 250 ticks → `light.blocked`
4. A roof over the target takes the light, and so does a roof along the path (§2.2) → `light.roof`
5. A mirror standing in shadow throws nothing; lit by a second mirror, it fires (chain) → `light.chain`
6. Light reaches the glow grid: `GroundGlowAt` at a lit cell on a Long Shade map reads 1.0 vs 0.8 → `glow.postfix`
7. Re-aiming bumps the shade grid's `GridVersion` and changes the patch-graph patch count → `herd.patchgraph`
8. Save → load keeps every mirror's target and rebuilds the same layer (hash equal) → `save.roundtrip`
9. Each Mod Settings toggle off removes its effect (`suite.toggles`) → `toggles.*`
10. A generated ancient field has ≥ 1 solution, an unsolved start and a minimum of ≥ 3 re-aims (the solver's own report, read back) → `field.solvable`
11. Herd visibly re-routes → `UNCOVERED: needs owner eyes (§2.8 risk 1); the state half is line 7`

Selftest offline first (`--mock`), then a minimal load round (the CreatureBehaviors + LongShade + SolarMirrors cluster, all five DLCs per the 2026-09-19 ruling).

## 7. Open questions (cards)

All four were answered by the owner on 2026-10-04 (question cards; ledger note on `SOLAR_MIRRORS_MOD_DESIGN_1`):

- **The frozen field's lock opens a sealed vault** holding loot and a repaired heliostat (not the shade road or the herd gate).
- **Static mirrors sweep under a moving sun;** only a powered heliostat holds its target.
- **The beam shows as a warm spot plus a faint shaft.**
- **Extensions after the core, typed:** *"I like all four"* — E1 solar furnace, E4 blinding defence, E3 heliograph signals and E2 mirror greenhouse are all in scope.

Everything else in this document is a proposal that stands unless he overrides it.
