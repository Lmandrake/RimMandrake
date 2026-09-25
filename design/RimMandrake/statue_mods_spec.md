# Statue mods spec — Utinni statues (RUT_) and Flame statues (RM_)

Item: `STATUE_ART_EXPANSION_1`. Owner ruling 2026-09-25 (typed): *"Let's focus on the two new
things: Utinni-related statues, and then the Flame statues. Just two mods for now."*
Decorative art for vanilla sculpture folders is DEFERRED and not designed here.
Research basis: `design/RimMandrake/statue_expansion_assessment.md` (donor mods, vanilla style
route, placeholder `RM_FlameStatuary`, fuel routes). Engine facts below are marked MEASURED
(read from the decompiled engine via RimSage this pass, 2026-09-25) or UNMEASURED.

## 0. Scope and non-goals

- Two mods, shippable independently: **Mod 1** `mandrake.rut.utinnistatues` (folder
  `src/RimUtinni/UtinniStatues/`), **Mod 2** `mandrake.rm.flamestatues` (folder
  `src/RimMandrake/FlameStatues/`). Neither depends on the other. Mod 1 patches onto Mod 2 only
  behind `PatchOperationFindMod` (Q11/Q11a additive-layer shape, as `SUMP_UTINNI_LAYER_1`).
- Not here: new decorative variants for vanilla `SculptureSmall/Large/Grand` folders (deferred);
  the "holy act to the evil sun god" ritual/precept (`SUMP_UTINNI_LAYER_1` §2 owns it; §2.5 below
  only leaves it a hook); forking either Workshop statue mod.
- Naming is tier-grammar (`design/NAMING_SCHEME_PLAN.md`). The gods' names are OURS (invented,
  Q11a): they live in the campaign tier because they are campaign culture, not because they are IP.

## 1. Mod 1 — Utinni culture statues (`mandrake.rut.utinnistatues`)

### 1.1 Sources read

- Pantheon of record: `design/Jawa/divine_satiation_engine.md` ("The Pantheon — canon of record",
  names LOCKED) and the figure law + per-god motifs in
  `design/Jawa/art/gods/god_render_prompt_spec.md` (owner, 2026-09-05). Bust/full-figure renders of
  all nine already exist in `design/Jawa/art/gods/{busts,fullfigure}/` — these are the style
  references for the statues, NOT the statue art (they are paintings of living gods, not stone).
- The faith is **The Salvation**; the Nine now run as personas inside the Cradle-Mind (the ship is
  their body, `the_forgotten_war.md` R-W6). Cultural specifics with a physical shape: the sand
  crawler, the salvaged droid, the bandolier-and-buckle robe, scavenged tokens/tallies, the
  hoarded droplet, the hull-shrine.
- Live ideoligion wiring: the player faction's culture is `RUT_Jawa_Culture_TradeMoot`
  (`src/RimUtinni/UtinniPatches/Defs/CultureDefs/JawaLeaderTitles.xml`, `thingStyleCategories`
  = Totemic priority 2). Our own worked precedent for a new style category is
  `src/RimMandrake/SacredGraffiti/Defs/StyleCategoryDefs_Salvation.xml` (`RM_SalvationDialect`).

### 1.2 Roster of subjects

Sizes follow vanilla exactly (MEASURED, `Core/ThingDefs_Buildings/Buildings_Art.xml`):
**small** = 1×1, drawSize 1; **large** = 1×1, drawSize (3,3); **grand** = 2×2, drawSize (4,4).
One subject = one carved figure, always hooded and robed, eyes as the only lit feature (the Jawa
visual law). Every god gets a large; the three "front" gods of the campaign arc also get a grand;
the small tier is votive objects rather than figures.

| # | Subject | Depicts | Size |
|---|---|---|---|
| 1 | Ishko the Unmaskable | robe dissolving into the plinth, only two low eyes lit, half-sunk as if in a hatch | large |
| 2 | Ohm the All-Current | arms raised, too-long gnarled hands reaching; a dormant droid head at the base | large + grand |
| 3 | Oomo the Unspilled | hunched, both hands cupping a single carved droplet; hem sagging | large |
| 4 | Mob'Unloo the Ever-Owed | seated on a ledger-stone, scales in one hand, tally-scratches down the robe | large |
| 5 | Rekko of the Second Hand | kneeling, mending a broken droid in his lap; robe patched from salvage | large + grand |
| 6 | Ta'Baa the Unrooted | mid-stride off the plinth edge, robe wind-caught, face turned away | large |
| 7 | Zizzik the Spark-Maker | crouched, slanted delighted eyes, one hand on a cracked machine part | large |
| 8 | Sh'kaar the All-Searing | tall, rigid, hood thrown back into a sun-disc; the eyes are the widest and hottest | large + grand |
| 9 | Ozzik the Shamed | grand robe, torn; a broken salvaged crown; eyes proud and grieving | large |
| 10 | The Bandolier | a votive: buckle and strap coiled on a stone, the mark of the clan | small |
| 11 | The Droplet | a votive: a single carved drop on a cracked dish (Oomo's tithe) | small |
| 12 | The Tally | a votive: a stack of scavenged tokens under a scratched slab (Mob'Unloo's ledger) | small |
| 13 | The Crawler | a sand crawler as a relief-block, treads and hull, the clan's ark before the ship | grand |

Thirteen subjects, sixteen textures (9 large + 4 grand + 3 small). Every subject is a distinct
carving, never a resized copy across tiers.

### 1.3 Attachment — how Utinni colonies get these looks

Vanilla's own culture-driven reskin, zero C# for the core (MEASURED):

- `StyleCategoryDef RUT_UtinniStatuary` with `thingDefStyles` rows for `SculptureSmall`,
  `SculptureLarge`, `SculptureGrand`, each pointing at one `ThingStyleDef`
  (`RUT_UtinniStatuary_SculptureSmall/Large/Grand`) whose `graphicData` is `Graphic_Random`
  over a folder holding that tier's subjects, `drawSize` copied from the vanilla tier. This is
  exactly the shape of `Christian_SculptureGrand` (assessment §2). `ThingStyleDef` carries only
  `graphicData`, `uiIconPath/Scale`, `overrideLabel`, `color` — it cannot change comps or stats
  (MEASURED, `Verse/ThingStyleDef.cs`), so this layer is look-only.
- Hook into the Utinni ideoligion: a `PatchOperationAdd` on
  `Defs/CultureDef[defName="RUT_Jawa_Culture_TradeMoot"]/thingStyleCategories` adding
  `<li><category>RUT_UtinniStatuary</category><priority>3</priority></li>`, gated
  `PatchOperationFindMod` on `mandrake.rut.patches`. `IdeoFoundation.RandomizeStyles` gathers
  culture + meme categories, sorts by priority, keeps up to 3 (MEASURED) — priority 3 beats the
  culture's Totemic 2, so every Utinni-culture ideo carries it. Player ideos can also pick it by
  hand in the ideo editor because `fixedIdeoOnly` stays false (MEASURED, `IdeoUIUtility`).
- Placement: `Designator_Build` resolves `PrimaryIdeo.GetStyleCategoryFor(thingDef)` at build
  time (MEASURED, line 594), so a sculpture built by an Utinni colony takes the Utinni style and a
  random subject from that tier's folder. Choosing a specific god: with
  `lc.tammybee.selectablesculpturegraphic` present, its existing `PatchOperationAdd` of
  `CompSculpture` onto `SculptureBase` already covers vanilla sculptures — nothing to add. The
  gizmo cycling the style's `Graphic_Random` pool is UNMEASURED (DLL unreadable); verify on the
  Desktop before promising "pick your god" in owner-facing text. (Owner question Q1.)
- Save/back-compat: adds a category and styles only; nothing renamed, nothing removed.
- No new ThingDefs in v1. A per-god buildable ("idol of Sh'kaar") is the flame-variant route
  in §2.5 and is not needed for the look.

### 1.4 Art brief per subject

- **Register**: our painterly high-res art (`generating-rimworld-sprites`), stone/salvage
  material reading as CARVED — the god as a statue, not the god. Base stone is desert
  sandstone/bone; per-god accent from the render spec as a mineral vein or inlaid metal (Ohm
  arc-blue, Sh'kaar white-gold, Ozzik purple/gold …). Eyes: two inlaid amber-glass stones,
  slightly uneven — the one non-stone highlight. Hands over-sized and gnarled. Hood always up
  (Sh'kaar's thrown back INTO a carved sun-disc is the one exception and the reason he reads evil).
  No spaceships, no gravship; sand crawlers, droids and scavenged tech welcome. Top-down-oblique
  RimWorld building angle, drop shadow off, alpha background.
- **Canvas (drawSize×128, authored at 2× for the painterly register; enhanced-zoom mods void
  the 256 ceiling)**: small 256 → ships 128; large 768 → ships 384; grand 1024 → ships 512.
  Grand is a 2×2 footprint so the figure must sit inside the central ~75% (vanilla grand art
  overhangs the footprint slightly, ours may too but never past the drawSize box).
- **Folder layout**: `Textures/Things/Building/Art/RUT_UtinniStatuary/{Small,Large,Grand}/` with
  one PNG per subject named for it (`Large_Rekko.png`). Random pool per tier = the folder.
- **Per-subject one-liners** are the "Depicts" column above; the render spec's motif column is
  the authority when they disagree. Sh'kaar's grand is the campaign's flame-statue candidate
  (§2.5) so its silhouette should leave a clear crown and two open palms as future flame points.
- Check `infrastructure/artpipe/done/`, `_artsrc/` and any review sheet before queuing: the
  bust/full-figure god paintings exist; NO statue art exists (grep of artpipe done/registry for
  statue/sculpt returns only unrelated jobs, 2026-09-25).

### 1.5 Mod Settings

Mod 1 is XML except for a minimal settings class (the every-mod rule): **(a)** "Utinni looks on
sculptures" on/off — when off, a `StaticConstructorOnStartup` removes `RUT_UtinniStatuary`
from every `CultureDef.thingStyleCategories` before ideo generation (worldgen-affecting, labelled
as such); **(b)** "Sumpgas fuels flame statues" on/off (only shown when Mod 2 is loaded; see
§2.3). Defaults on. All-off = a mod that does nothing, and nothing breaks.

## 2. Mod 2 — Flame statues (`mandrake.rm.flamestatues`)

### 2.1 What replaces RM_FlameStatuary

`RM_FlameStatuary` (EnvironmentalHazards, placeholder art, one warbling glow, no fuel) is
**deleted from EnvironmentalHazards** and replaced by three defs in Mod 2, all
`thingClass Building_Art` with the full sculpture comp/recipe block copied explicitly from
`SculptureBase` (not inherited — the def's own header explains the `<comps>` replacement trap):

| defName | label | footprint / drawSize | flame points | stuff |
|---|---|---|---|---|
| `RM_FlameStatue_Ember` | ember idol | 1×1 / 1.5 | 1 (crown) | Stony, Metallic |
| `RM_FlameStatue_Dancer` | flame dancer | 1×1 / 3 | 3 (two palms, crown) | Stony, Metallic |
| `RM_FlameStatue_Colossus` | pyre colossus | 2×2 / 4 | 5 (palms, crown, two shoulder vents) | Stony, Metallic |

Woody is dropped (a burning wooden statue is a joke the fiction does not make). Beauty, work and
cost copy the matching vanilla tier; the flame is the differentiator, not the beauty stat.
Before deleting the old def: grep keeper saves for `<def>RM_FlameStatuary</def>` — a placed
instance would fail to load (`rimworld-savegame`); if any exists, keep a one-line
`RM_FlameStatuary` def in Mod 2 marked `<designationCategory>` null so it loads but is not
buildable, and record it for removal after the next world remake.

### 2.2 Flame-point mechanism

**MEASURED and why vanilla alone does not do it.** Vanilla's positioned flame is
`CompProperties_FireOverlay` (`offset`, per-facing offsets, `fireSize`, growth), drawn by
`CompFireOverlay.PostDraw` through `Graphic_Flicker` — the torch lamp is the model
(`fireSize 0.4`, `offset (0,0,0.2)`), and it already respects a sibling `CompRefuelable`
(`HasFuel`, `RimWorld/CompFireOverlay.cs`). But `Graphic_Flicker.DrawWorker` fetches the flame's
size and offset with `thing.TryGetComp<CompFireOverlayBase>()` — the FIRST such comp on the thing
(MEASURED, `Verse/Graphic_Flicker.cs`). Stacking several `CompProperties_FireOverlay` on one def
therefore draws every flame at the first comp's offset. One flame point per statue is free; a
flame SET needs our own comp.

**The comp (new C#, small, Mod 2's own assembly `RM_FlameStatues.dll`).**

```xml
<li Class="RimMandrake.FlameStatues.RM_CompProperties_FlamePoints">
  <points>
    <li><offset>(0.32,0,0.61)</offset><size>0.35</size></li>   <!-- right palm -->
    <li><offset>(-0.30,0,0.63)</offset><size>0.35</size></li>  <!-- left palm -->
    <li><offset>(0,0,1.15)</offset><size>0.55</size></li>      <!-- crown -->
  </points>
  <qualityScalingEnabled>true</qualityScalingEnabled>
  <fireGlowFleckIntervalTicks>90</fireGlowFleckIntervalTicks>  <!-- 0 = no flecks -->
</li>
```

- `RM_FlamePoint { Vector3 offset; float size; }` — offsets in cells from `parent.DrawPos`, the
  same convention as `CompProperties_FireOverlay.offset`, authored per def beside the art (the
  art brief §2.6 names each point). Statues are `rotatable false`, so no per-facing offsets.
- `RM_CompFlamePoints.PostDraw`: for every point, draw a vanilla fire frame with
  `Graphics.DrawMesh(MeshPool.plane10, TRS(pos+jitter, identity, size), mat, 0)` at
  `DrawPos.y + 0.0366` — the same math as `Graphic_Flicker.DrawWorker`, with the frame index and
  radial jitter seeded by `(thingIDNumber, pointIndex, TicksGame/15)` so the points flicker out
  of phase. Frame materials come from the vanilla fire texture set under `Things/Special/Fire`
  (the path `CompFireOverlay.FireGraphic` loads; the per-frame file names/count are UNMEASURED —
  FOUNDRY resolves them with `reading-rimworld-graphics`, or simply instantiates its own
  `Graphic_Flicker` per point via `GraphicDatabase.Get<Graphic_Flicker>` and drives it with a
  per-point dummy offset, whichever compiles cleanest).
- Lit test: `refuelable == null || refuelable.HasFuel` (same as vanilla), AND'd with the
  Helixien state in §2.3 when that patch is present, AND'd with the Mod Settings gates.
- Quality: reads the sibling `CompQuality` and scales every point's size and the fleck rate on
  the same 0.5× (Awful) … 2× (Legendary) curve `RM_Comp_WarblingGlow` uses — copied as numbers,
  not as a dependency on EnvironmentalHazards.
- Flecks: `FleckMaker.ThrowFireGlow(Vector3 c, Map map, float size)` (MEASURED signature) at
  each point every `fireGlowFleckIntervalTicks`, jittered per point.
- Glow: the def carries a plain `CompProperties_Glower` (hot orange-red as today). It goes dark
  without fuel by itself: `CompGlower.ShouldBeLitNow` polls every sibling comp implementing
  `IThingGlower` (MEASURED, `Verse/CompGlower.cs` line 84), which is how the torch lamp darkens.
  `RM_CompFlamePoints` implements `IThingGlower` too, so "flame points off" in settings also
  turns the glow off. The colour/radius warble of the old placeholder is re-implemented inside
  this comp (a 3-line sine on the glower's radius each `updateIntervalTicks`), so Mod 2 does not
  load EnvironmentalHazards.
- Ghost/blueprint: draw nothing (vanilla's `DrawGhost` draws one flame; ours draws none — the
  art already implies the points).

### 2.3 Fuel

- **Manual refuel — the working route, ships first.** `CompProperties_Refuelable` copied from
  `RUT_GaslightLamp` (`fuelCapacity`, `autoRefuelPercent 0.35`, `targetFuelLevelConfigurable`,
  `drawOutOfFuelOverlay true`). RM-tier default `fuelFilter`: `Chemfuel` only (a flame that
  burns anything a base game has). Consumption: Ember 0.12/day, Dancer 0.28, Colossus 0.5 —
  numbers, tune in settings.
- **Sumpgas (`RUT_Sumpgas`) — the campaign's fuel.** `RUT_Sumpgas` is a RUT-tier item in
  `UtinniPatches`, so Mod 2 never names it. **Mod 1** carries
  `Patches/FlameStatues_SumpgasFuel.xml`, gated `PatchOperationFindMod` on
  `mandrake.rm.flamestatues`, replacing each statue's `fuelFilter` with `RUT_Sumpgas` and the
  `fuelLabel`/`fuelGizmoLabel` with "Sumpgas" — the gaslight-lamp pattern, already live. Caveat
  carried from the assessment: Sumpgas's tar-scrub byproduct spawn fails live; crafting works.
  Not a blocker for the statue; it is `SUMP_GASLIGHT_1`'s defect.
- **Helixien pipenet — optional, gated, last.** `vanillaexpanded.helixiengas` is on the live
  list (621-mod snapshot 2026-09-19). Its consumers use
  `PipeSystem.CompProperties_ResourceTrader { pipeNet VHGE_HelixienNet, consumptionPerTick }`
  (MEASURED from `VHGE_GasSunLamp` in the mod's own defs). Mod 2 ships
  `Patches/Helixien_Pipenet.xml` under `PatchOperationFindMod vanillaexpanded.helixiengas`
  adding that comp to the three defs. The comp then reads the trader's on/off by reflection on
  the runtime type `PipeSystem.CompResourceTrader` (member name UNMEASURED — read the VE
  Framework source on the Desktop before wiring; never guess it). Lit = refuelable has fuel OR
  pipenet trader is receiving; a statue on a live pipe stops consuming its tank. If the reflection
  lookup fails, the comp logs once and treats the pipenet as absent — manual refuel still works.

### 2.4 Mod Settings

`RM_FlameStatuesSettings`, defaults = shipped behaviour: flame points drawn (on); fire-glow
flecks (on); fuel consumption (on — off makes every statue burn free, shown as "statues never run
out"); quality scaling (on); glow (on); Helixien link (on; row visible only when the mod is
loaded); consumption multiplier 0.25–4×. All-off = plain sculptures with our art, nothing
errors. Every gate is read live by the comp each tick/draw, no restart.

### 2.5 Utinni flame variants later, without a hard dependency

Because `ThingStyleDef` cannot add comps (§1.3), a flaming god cannot be a style over Mod 2's
defs with its own flame points — but it does not need Mod 2 at all. A later Mod 1 step ships
its own `RUT_FlameIdol_Shkaar` (grand, Sh'kaar's silhouette from §1.4) built the same way as
§2.1 with: `CompProperties_Refuelable` on Sumpgas, `CompProperties_Glower`, and
**vanilla `CompProperties_FireOverlay` for ONE flame point** (the sun-disc crown) — all vanilla,
no C#. When Mod 2 is present, a `PatchOperationFindMod mandrake.rm.flamestatues` patch swaps
that single overlay for `RM_CompProperties_FlamePoints` with the full palms+crown set. So: one
flame without Mod 2, the whole show with it, and the holy-act precept
(`SUMP_UTINNI_LAYER_1` §2) targets the RUT def, never Mod 2's.

### 2.6 Art brief

- **NO fire in the sprite.** The engine draws every flame. Draw the vents: blackened,
  soot-fanned openings, a heat-dulled metal lip, glass-smooth stone where flame has licked —
  each point reads as "fire belongs here" while cold. The def's `points` list is authored FROM
  the finished art (measure the vent centres in the PNG, convert to cells: `x_cells =
  (px/ship_px − 0.5) × drawSize`), never the other way round.
- Register: painterly high-res, franchise-free, no hood-and-robe law here (that is Mod 1's).
  Ember idol: a squat brazier-figure, a single crown vent. Flame dancer: a lithe abstract figure,
  arms raised, palms cupped upward as vents, a crown vent. Pyre colossus: a seated giant, palms
  up, crown, two shoulder vents; the 2×2 base is a carved fire-pit ring.
- Canvas: Ember 384 authored → 192 shipped (drawSize 1.5); Dancer 768 → 384; Colossus
  1024 → 512. One PNG per def (`Graphic_Single`); a 2–3 variant `Graphic_Random` folder is
  welcome later but every variant must keep the SAME vent positions, since `points` is per def.
- Stuff colour: `useIngredientsForColor` stays, so the art is authored desaturated/grey-warm and
  the stuff tints it.

## 3. Build order (small shippable steps)

1. **Mod 2 skeleton** — folder, About.xml, three defs with `CompProperties_Refuelable`
   (Chemfuel) + `CompProperties_Glower` + ONE vanilla `CompProperties_FireOverlay` each, placeholder
   art; delete `RM_FlameStatuary` from EnvironmentalHazards after the keeper-save grep (§2.1).
   Ships: fuelled statues that burn one flame. Deploy, quicktest list + all DLC.
2. **Flame-point comp** — `RM_CompFlamePoints` + props, `IThingGlower`, quality scaling, flecks;
   swap step 1's overlay for point lists; Mod Settings §2.4. Ships: multi-point flames.
3. **Mod 2 art** — three sprites per §2.6, `points` measured from the PNGs.
4. **Mod 1 skeleton** — `RUT_UtinniStatuary` category + three styles over placeholder folders;
   CultureDef patch; settings §1.5; Sumpgas fuel patch onto Mod 2 (§2.3). Ships: Utinni colonies'
   sculptures take the Utinni pool; flame statues burn Sumpgas in the campaign.
5. **Mod 1 art** — sixteen statue textures per §1.2/§1.4, queued in three artpipe waves
   (large gods; grands; smalls), each wave wired into its folder as it lands.
6. **Selector verification** — with LC on the Desktop list, confirm the gizmo cycles our pool;
   record MEASURED either way.
7. **Helixien link** — §2.3 last paragraph, only after the reflection member is read from source.
8. **Sh'kaar flame idol** (§2.5) — opens the holy-act work in `SUMP_UTINNI_LAYER_1`.

## 4. Owner questions

- Q1. Should a colonist be able to pick WHICH god a sculpture shows (needs the LC selector mod or
  our own small gizmo), or is a random god from the Utinni pool fine?
- Q2. Are the four votive/cultural subjects (Bandolier, Droplet, Tally, Crawler) wanted in the
  first wave, or gods only?
- Q3. Outside the campaign, should flame statues burn Chemfuel by default, or wood too?
- Q4. Should Sh'kaar be the only god who gets a flaming idol first, or all three grands (Ohm,
  Rekko, Sh'kaar)?
