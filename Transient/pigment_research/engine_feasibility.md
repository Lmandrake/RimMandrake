# Rainbow pigment — engine feasibility (RimWorld 1.6)

Evidence tags: MEASURED (class/method read via RimSage decompile) or UNMEASURED.

## 1. Luminous dye

**Verdict: buildings/furniture — FEASIBLE, cheap-ish (a CompGlower subclass + a ColorDef tag). Worn apparel — EXPENSIVE (no vanilla path; needs a moving-light system).**

### How 1.6 dyeing works (MEASURED)
- **Two unrelated systems.**
  - *Apparel* — `CompColorable` (`desiredColor`, `color`, `active`; `Recolor()` applies desiredColor → `SetColor` → `parent.Notify_ColorChanged()`). The job is `JobDriver_RecolorApparel` at a `Building_StylingStation` (Ideology-gated: `ModLister.CheckIdeology("Apparel recoloring")`), 1000 ticks, consumes 1 dye per garment, then `TryGetComp<CompColorable>().Recolor()`. Also queued autonomously by `JobGiver_OptimizeApparel`. Picked in `Dialog_StylingStation`.
  - *Buildings* — no comp: `Building.paintColorDef` (a `ColorDef`, Scribed via `Scribe_Defs`), set by `Building.ChangePaint(ColorDef)` which calls `Notify_ColorChanged` and dirties the Buildings map mesh. Flow: `Designator_PaintBuilding` (paint designation carries `colorDef`) → `WorkGiver_PaintBuilding` → `JobDriver_PaintBuilding` (1 s of work × WorkSpeedGlobal, Artistic XP, consumes 1 dye, `building.ChangePaint(designation.colorDef)`; non-Building targets get `Thing.SetColor(color)`). Gate: `def.building.paintable`. No `ModLister` check in the job driver (DLC ownership of the designator UNMEASURED).
  - `ColorDef` = `color`, `colorType` (Structure etc.), `displayOrder`, `displayInStylingStationUI`, `randomlyPickable`. No extension point, but it is a Def, so a `DefModExtension` can tag one.
- **The dye item is hard-coded**: `WorkGiver_PaintBuilding.ShouldPaintThing` checks `listerThings.ThingsOfDef(ThingDefOf.Dye)`; `JobOnThing` uses `PaintUtility.FindNearbyDyes`. A separate "rainbow pigment" ThingDef would need Harmony on those two (or: luminous colour = a special ColorDef that still costs ordinary Dye, plus a pigment cost charged some other way).

### Can dyed things glow? (MEASURED)
- `CompGlower.ShouldBeLitNow` returns false unless `parent.Spawned`. **Worn apparel is not spawned → a CompGlower on apparel never lights.** Items lying on the ground are spawned and CAN glow (any ThingWithComps, not only Buildings — glow grid registration is `map.glowGrid.RegisterGlower(CompGlower)`, not building-specific).
- `GlowLight` (ctor from `CompGlower`) snapshots `position = glower.parent.Position`, radius and colour **at registration**. The only callers of Register/DeRegister are inside `CompGlower` itself. So **nothing in vanilla supports a moving light** (no pawn-carried lights); a luminous-garment effect would need re-registering on every cell move (`DeRegisterGlower`+`RegisterGlower` → dirties the whole `AffectedRect`, ~(2r+1)² cells, plus a `ComputeGlowGridsJob` for that light) — per moving pawn, per step. Expensive-but-bounded; for small r (1.5–2.5) it is 16–36 cells/step. The honest cheaper fake for apparel is a sparkle fleck (§3), not light.
- Per-instance runtime toggle: YES. `ShouldBeLitNow` ANDs every `IThingGlower` on the parent and every comp implementing `IThingGlower` — so a tiny comp implementing `IThingGlower.ShouldBeLitNow()` (e.g. "paint is luminous") gates an existing glower, and `UpdateLit(map)` flips registration. `GlowColor` setter → `SetGlowColorInternal` re-registers. **Trap: the `GlowRadius` setter only writes `glowRadiusOverride` and does NOT re-register**, and `glowRadiusOverride` is **not Scribed** (`PostExposeData` saves only `glowOn` + `glowColorOverride`). Vanilla `CompDisruptorFlare.CompTick` changes radius and relies on the subsequent `GlowColor =` to re-register; `Building_VoidMonolith` sets radius then calls `ForceRegister(map)`. So: set radius, then `ForceRegister`, and re-derive radius on load.
- `CompProperties_Glower`: `glowRadius` (default 14, ConfigError above 40), `glowColor`, `overlightRadius`, `colorPickerEnabled` (needs ColoredLights research), `darklightToggle`, `overrideIsCavePlant`.
- Terrain can glow too (`GlowGrid.RegisterTerrain`, `TerrainDef.glowRadius/glowColor`) — relevant only for painted floors (`Designator_PaintFloor`/`JobDriver_PaintFloor` exist; whether floor paint can carry glow UNMEASURED).

### Cheapest build for "make it luminous" (design inference from the above)
1. XML-patch a `CompProperties_Glower` subclass (small radius, e.g. 2–3, colour from paint) onto paintable buildings — or a narrower set (furniture). Inactive by default via an `IThingGlower` comp that returns false.
2. A luminous `ColorDef` (or a `DefModExtension` on chosen ColorDefs). Harmony postfix on `Building.ChangePaint`: if tagged, set `GlowColor` from `colorDef.color` (this re-registers) and `UpdateLit`; else de-light. Persist: paintColorDef is already Scribed, so the glow re-derives on `PostSpawnSetup` — no new save data.
3. No new job needed; the existing paint designator/job does the work. Charging the rainbow pigment instead of Dye = Harmony on `WorkGiver_PaintBuilding`/`PaintUtility.FindNearbyDyes` (two methods).

### Cost (MEASURED shape, UNMEASURED numbers)
Unlit glowers are not in `lights` — zero cost. Each lit glower is a static `GlowLight`; recalcs happen only when a light or a blocker near it is dirtied (`anyDirtyLight`/`anyDirtyCell`, per-light `dirty`, `DirtyLightsAround` on blocker change), in Burst jobs (`ComputeGlowGridsJob`, `CombineColorsJob`). Static luminous furniture is cheap. `CombineColorsJob` runs over all `NumGridCells` when any cell is dirty (it takes `dirtyCells`, so per-cell work is skipped cheaply — per-frame ms UNMEASURED).

## 2. Quality bump

**Verdict: post-hoc raise — FEASIBLE, trivial (one public call). At-creation ingredient shift — FEASIBLE, cheap (one Harmony pair). Legendary is a hard cap (enum max 6).**

### Post-construction (MEASURED)
- `CompQuality.SetQuality(QualityCategory q, ArtGenerationContext? source)` is **public**: writes `qualityInt`, calls `CompArt.InitializeArt(source)` if a CompArt exists and source is non-null, then `parent.PostQualitySet()` (virtual on `Thing`; `Book` overrides) and `CompFacilityQualityBased.PostQualitySet()`. Scribed as `quality`. So "apply pigment to a finished item → +1 tier" is one call.
- **Art trap:** `CompArt.InitializeArtInternal` returns immediately if `titleInt` is already set. So bumping an item that already had art keeps its old title and tale; only an item that was *below* `CompProperties_Art.minQualityForArtistic` (`CompArt.CanShowArt` = quality ≥ that) gets fresh art on the bump. Regenerating art on an already-artful item means clearing private `titleInt`/`taleRef` (reflection / Traverse) before the call.
- Vanilla precedent for a post-hoc set: `TaleData_Thing` raises quality to `minQualityForArtistic`; `JobDriver_BuildCubeSculpture` sets quality after the fact.
- Stacking: `CompQuality.AllowStackWith` requires equal quality — bumping one item of a stack must split it first.

### During creation (MEASURED)
- Quality is rolled in exactly two places: `GenRecipe.PostProcessProduct` (crafted: `GenerateQualityCreatedByPawn(worker, recipeDef.workSkill)`) and `Frame.CompleteConstruction` (built: `…(worker, SkillDefOf.Construction)`), both followed by `SetQuality(q, ArtGenerationContext.Colony)`.
- `QualityUtility.GenerateQualityCreatedByPawn(int skill, bool inspired)`: skill 0–20 maps to a mean 0.7–4.2, `Rand.GaussianAsymmetric(mean, 0.6, 0.8)` clamped **0..5 (Masterwork)**; a rolled 5 is re-rolled 50% of the time. Legendary (6) only via `AddLevels`: Inspired_Creativity (+2) or Ideology `RoleEffect_ProductionQualityOffset`. `AddLevels` = `Mathf.Min(q + levels, 6)` — **Legendary is the cap**.
- **No ingredient hook exists.** `PostProcessProduct` receives no ingredient list; the ingredients are only in its caller `GenRecipe.MakeRecipeProducts(recipeDef, worker, ingredients, dominantIngredient, …)`. `Frame` has its `resourceContainer`. Cheapest mod path: Harmony prefix on `MakeRecipeProducts` that notes "a pigment is among `ingredients`" in a `[ThreadStatic]`, and a postfix on `GenerateQualityCreatedByPawn(Pawn, SkillDef, bool)` that adds a level (or re-rolls with a higher skill) when the flag is set; clear in a finalizer. For construction, a postfix on `Frame.CompleteConstruction` reading what the frame consumed (or re-rolling via `SetQuality`). Alternative with zero Harmony: the pigment is a separate "apply to item" job that calls `SetQuality` after creation (then the art trap above applies).
- Crafting products with quality need `recipeDef.workSkill` or `PostProcessProduct` logs an error.

## 3. Permanent sparkle

**Verdict: CHEAP — XML-only for placed things (`CompFleckEmitterLongTerm` or `CompFleckEmitter` + an existing or new FleckDef). Worn apparel: cheap C# (a ~30-line comp).**

### Periodic flecks (MEASURED)
- `CompFleckEmitter` (Props: `fleck`, `emissionInterval`, `offset`, `soundOnEmission`, `saveKeysPrefix`): `CompTick` counts to `emissionInterval`, then `FleckMaker.Static(parent.DrawPos + offset, MapHeld, fleck)`. Skips if a `CompPowerTrader` is off. No camera culling.
- `CompFleckEmitterLongTerm` (Props: `fleckDef`, `spawnChance`, `spawnRadius`, `spawnOffsetFromCenter`, rotation/velocity ranges, `prewarmCycles`, `forceEnabled`; runtime `Enabled` bool): per-tick `Rand.Value < spawnChance`, random point in `spawnRadius`, gated by `ShouldSpawnMotesAt(map)` → **false on any map that is not `Find.CurrentMap`**, so off-map-view cost is one random roll. **`Enabled` is a public per-instance switch but not Scribed** — a luminous/sparkle flag must be re-applied on load (or use `forceEnabled` in XML for always-on).
- Both need the parent def to tick (`tickerType` Normal). Many furniture defs are `tickerType` Never → the patch must change tickerType too, which adds a per-thing tick cost; a custom comp using `CompTickRare`/`CompTickInterval` is the cheaper shape. Flecks themselves are pooled structs in `FleckSystem`s (`FleckManager.CreateFleck`), not Things — cheap; per-frame cost UNMEASURED.
- Worn apparel: `Apparel.DrawWornExtras` → each comp's `CompDrawWornExtras()` runs every frame while worn (vanilla `CompShield` draws its bubble here) — a place to draw a small additive twinkle mesh with no ticking at all. Worn apparel comps also tick (`CompShield.CompTick` branches on `PawnOwner != null`); the exact tick path for worn apparel is UNMEASURED.

### Vanilla sparkly assets to reuse (MEASURED)
- `Fleck_RadialSparks` (Core `Fleck_Visual.xml`): `Graphic_FleckPulse`, shader **`MoteCircularSparks`** with two scrolling textures `Things/Mote/Sparks_Radial_A/_B` — the closest vanilla "glitter" look; scale down via `drawSize`/fleck scale.
- **`AdditiveChangeHue`** (Core ShaderTypeDef) with `_ChangeSpeed` — **a built-in rainbow hue-cycling additive shader**, used by Ideology's `Mote_LightBallLights` (lightball) and `Mote_LoudspeakerLights`. A rainbow shimmer overlay is one MoteDef (or a Graphic on a comp) with this shader: no C# for the colour cycling.
- `GlowAnimated` (`_NumFrames`, `_FramesPerSec` — flip-book additive glow, e.g. `Mote_PowerCellBurning`), `MoteGlowPulse`/`MoteGlowPulseLow`/`MotePulse` (breathing), `TransparentAnimatedColorLerp` (Anomaly; frame sheet + `_ColorLerp` ramp texture).
- No def in the index is named sparkle/glint/glitter (search_defs returned zero; `shimmer` only hits `AncientVentHeatShimmer`, a heat-haze fleck). So "sparkle effecter" must be assembled, not borrowed.

### ShaderTypeDefs that exist (MEASURED, from the ShaderTypes.xml of Core/Royalty/Ideology/Biotech/Anomaly/Odyssey)
Glow/additive family: `MoteGlow`, `MoteGlowPulse`, `MoteGlowPulseLow`, `MoteGlowPulseLink`, `MoteGlowDistorted`, `MoteGlowDistortBackground`, `MoteGlowCircularScrolling`, `GlowAnimated`, `AdditiveChangeHue`, `MoteCircularSparks`, `EmberGlow`, `RitualGlow`, `RitualGlowSingleRay`, `PawnSilhouetteStencilGlow`, Biotech `MoteMechGestatorGlow`/`MoteSoftScannerGlow`/`MotePawnBodyGlow`/`MoteGlowParentRotation`, Odyssey `MoteGlowMasked`. Transparent family: `Transparent`, **`TransparentPostLight`** (drawn after lighting — i.e. ignores darkness; the cheapest "self-lit" look for a static overlay), `TransparentAnimated`, `TransparentColorLerp`, `TransparentAnimatedColorLerp`, `TransparentShaking`, `TransparentColoredMask`. Cutout family: `Cutout`, `CutoutComplex`, `CutoutAnimated`, `CutoutWithOverlay`, etc. Full list: 122 ShaderTypeDefs.

### Cheapest designs, ranked (inference)
1. Static self-lit overlay: an extra Graphic drawn with `TransparentPostLight` or `MoteGlow` (reads as glowing in the dark, zero ticks) — needs a comp `PostDraw`/`CompDrawWornExtras` or a MoteAttached.
2. Rainbow shimmer: a maintained `MoteAttached` with `AdditiveChangeHue` (the lightball pattern: `CompLightball` makes the mote once and maintains it).
3. Twinkles: `CompFleckEmitterLongTerm` with a tiny `MoteGlow` star FleckDef, `spawnChance` ~0.01–0.02.

## 4. Shine / glint

**Verdict: IMPOSSIBLE natively (no specular in the lighting model); EXPENSIVE via a custom Unity shader in an AssetBundle; CHEAP to fake.**

- MEASURED: lighting is a per-cell colour grid (`GlowGrid.accumulatedGlow` `Color32` per cell, combined in `CombineColorsJob`) plus sky glow; there are no normals, no light direction, no view vector — nothing a specular term could use. `GlowLight` carries only position, radius, colour, overlight radius.
- MEASURED: `ShaderDatabase` lists no metallic/specular/reflective shader (fields: Cutout*, Transparent*, Mote*, Terrain*, World*, Metalblood, Silhouette, SolidColor, VertexColor, masks). `Metalblood` (Anomaly, `Misc/Metalblood`) is the only "metal" shader; it is a pawn overlay effect — whether it reads as sheen is UNMEASURED (needs a look in game).
- MEASURED: `ShaderDatabase.TryLoadShader` falls back to `ContentFinder<Shader>.TryFindAssetInModBundles(shaderPath)`, so **a mod may ship its own shader in an AssetBundle** and reference it from a ShaderTypeDef `shaderPath`. That is the only route to a real animated glint (e.g. a time-scrolling highlight band). Cost: authoring a Unity shader against RimWorld's Unity version and per-platform bundles — expensive, and it still would not respond to lights.
- Closest fakes, cheapest first: (a) bake a highlight into the texture; (b) an overlay with `MoteGlowCircularScrolling` / `MoteMultiplyAddScroll` (scrolling-texture shaders exist) to sweep a highlight band; (c) sparse additive glint flecks (§3) — the eye reads a brief bright star as "glint"; (d) `AdditiveChangeHue` overlay for iridescence.

## 5. Oscillating shipboard lighting

**Verdict: it is OUR design, not vanilla, and partly OUR code.**

- MEASURED (vanilla): nothing in the decompiled engine animates a `CompGlower`'s colour over time. Every `GlowColor =` writer is: the colour-picker/darklight gizmos, `Dialog_GlowerColorPicker`, `CompVoidStructure` (one-off), `CompDisruptorFlare` (fade-out), `Frame`/`Designator_Build` (copy override), a back-compat converter. Odyssey adds no glow-animating code (search hit nothing). The only vanilla hue-cycling light is **visual only**: Ideology's lightball/loudspeaker motes using the `AdditiveChangeHue` shader (`CompLightball` spawns `Mote_LightBallLights`); the actual glow-grid light stays static.
- MEASURED (design): `design/Jawa/worldbuilding/ship_distinctive_features.md` §9 "The ship RESONATES with the gods' moods" [ACCEPTED 2026-08-08] — shipboard lighting changes colour and intensity with the pantheon's standing (Oomo blue, Sh'kaar white/red glare, Ishko dimming, Ohm cyan pulse, Rekko amber, Ta'Baa rising glow, Zizzik erratic flicker, Ozzik gold), plus the standalone "Responsive Status Lighting" mod idea (time-driven blinking/strobing, or bound to a game variable). §5 "Running lights as a repair progress bar" is the other shipboard light tell. No source under `src/` implements §9 (grep for resonance/status-light code found only unrelated `RustCathedralHum` "ResonantDance") — **unbuilt**.
- MEASURED (our code that already oscillates a real light): `src/RimMandrake/EnvironmentalHazards/Source/RM_Comp_WarblingGlow.cs` (`SUMP_GASLIGHT_1`) — every `updateIntervalTicks` (10–12) it rewrites `CompGlower.GlowColor` (hue ± `hueRangeDegrees`, value pulse) and `GlowRadius` + `ForceRegister`. Used by `RUT_GaslightLamp` (hue ±18°, 211-tick period) and `RM_FlameStatuary` (±22°, 179-tick, quality-scaled). Note it re-registers the glower ~every 10 ticks, i.e. a full light recompute each time — the cost model a colour-cycling pigment light would share.
- Clash implication: the ship's hue language is a *signal channel* (colour = which god). A rainbow-cycling luminous pigment on shipboard furniture would put arbitrary hues in the same rooms and muddy that read. A static, low-radius, player-chosen luminous colour (or a non-light sparkle) does not compete.

## 6. High-art line

**Verdict: skill gate — FEASIBLE, XML-only. Ingredient gate on *which piece can be made* — FEASIBLE, XML-only. Ingredient gate on *what quality tier comes out* — needs the §2 Harmony pair.**

- MEASURED: two independent gates exist.
  - *Crafted art* (sculptures are crafted at `TableSculpting` via `recipeMaker`, `workSkill` Artistic, `UnfinishedSculpture`): `RecipeMakerProperties.skillRequirements` → copied by `RecipeDefGenerator` into `RecipeDef.skillRequirements` (`List<SkillRequirement>`; `SkillRequirement` = `skill` + `minLevel`, XML form `<Artistic>4</Artistic>`, checked by `RecipeDef.PawnSatisfiesSkillRequirements` / `FirstSkillRequirementPawnDoesntSatisfy`; mechs pass via `mechFixedSkillLevel`). Vanilla use: Odyssey `Statue` has `<skillRequirements><Artistic>4</Artistic></skillRequirements>`. `SculptureSmall` (merged) and `SculptureGrand` carry none.
  - *Built art/buildings*: `BuildableDef.artisticSkillPrerequisite` and `constructionSkillPrerequisite`, enforced in `GenConstruct` (≈ line 305–323) and shown in `Designator_Build`.
- MEASURED: `RecipeDefGenerator` turns a def's `CostList` into fixed ingredients (lines 105–109) and `CostStuffCount` into the stuff ingredient. So a "prismatic" art ThingDef with `<costList><RM_RainbowPigment>N</RM_RainbowPigment></costList>` + `recipeMaker.skillRequirements` (e.g. Artistic 10+) is a pure-XML high-art line: no pigment → bill cannot start; low skill → pawn cannot take it. (`defaultIngredientFilter` only filters stuff; it cannot demand an extra item.)
- MEASURED: quality is rolled from skill alone (§2) — neither the ingredient nor `skillRequirements` shifts the roll. A higher `minLevel` only raises the floor indirectly (a skill-12 artist averages ~3.4, i.e. Good–Excellent). To make pigment raise the *tier*, add the §2 hook; to guarantee a floor, `CompProperties_Art.minQualityForArtistic` is only an art-display threshold, not a quality floor (vanilla `TaleData_Thing` is the one place that forces quality up to it).
- Research gate as a third lever: `recipeMaker.researchPrerequisite` (standard field; whether sculptures use one UNMEASURED — none appears in `Buildings_Art.xml`).
