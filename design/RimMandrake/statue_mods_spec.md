# Statue mods spec — Utinni statues (RUT_) and Flame statues (RM_)

Item: `STATUE_ART_EXPANSION_1`. Owner ruling 2026-09-25 (typed): *"Let's focus on the two new
things: Utinni-related statues, and then the Flame statues. Just two mods for now."*
Decorative art for vanilla sculpture folders is DEFERRED and not designed here. All seven
rulings on the item, with provenance, are tabled in §4; the 13-subject art queue is §5; what is
still undecided is §6.
Research basis: `design/RimMandrake/statue_expansion_assessment.md` (donor mods, vanilla style
route, placeholder `RM_FlameStatuary`, fuel routes). Engine facts below are marked MEASURED
(read from the decompiled engine via RimSage this pass, 2026-09-25) or UNMEASURED.

## 0. Scope and non-goals

- Two mods, shippable independently, **built in this order** (R1): **Mod 1**
  `mandrake.rut.utinnistatues` (folder `src/RimUtinni/UtinniStatues/`), then **Mod 2**
  `mandrake.rm.flamestatues` (folder `src/RimMandrake/FlameStatues/`). Neither depends on the
  other. Mod 1 patches onto Mod 2 only behind `PatchOperationFindMod` (Q11/Q11a additive-layer
  shape, as `SUMP_UTINNI_LAYER_1`).
- The player always chooses which god a statue honours (R2) — every Utinni subject is its own
  buildable (§1.3).
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

Thirteen subjects — **all of them in wave one** (R3: all nine gods AND the four votives) —
sixteen textures (9 large + 4 grand + 3 small). Every subject is a distinct carving, never a
resized copy across tiers.

### 1.3 Attachment — one buildable per subject; the player chooses who they honour

Owner ruling R2 (typed, 2026-09-25): *"Either player picks or they are all separate objects, but
it's important the player be able to choose who they are honoring."* A random god rolled from a
style pool is therefore NOT the mechanism. Of the two shapes he allowed, this spec takes
**separate objects** — it is all XML, deterministic, and it is already the shape §2.5 needs for
the flaming idol.

- **Thirteen ThingDefs**, one per subject in §1.2: `RUT_Idol_Ishko` … `RUT_Idol_Ozzik` (the
  nine gods), `RUT_Votive_Bandolier`, `RUT_Votive_Droplet`, `RUT_Votive_Tally`,
  `RUT_Relief_Crawler`. Each is `thingClass Building_Art` with the sculpture comp/recipe block
  copied explicitly from `SculptureBase` (never inherited — the `<comps>` replacement trap, same
  as §2.1), `Graphic_Single` on its own PNG, footprint/drawSize from its tier in §1.2,
  `rotatable false`. The three "front" gods (Ohm, Rekko, Sh'kaar) each get a second, grand-size
  def (`RUT_Idol_Ohm_Grand` …) — so 16 defs over 13 subjects.
- **Where they sit in the build menu**: their own `DesignationCategoryDef`-free route — a
  `designatorDropdown` group `RUT_UtinniIdols` inside vanilla `Misc` (where sculptures live), so
  the player opens one dropdown and picks the god by name and icon. Label form: *"idol of
  Sh'kaar"*, *"votive: the Droplet"*. Beauty, work, cost copy the matching vanilla tier; the
  subject is the differentiator, not the stat.
- **Ideoligion gating, none.** Any colony that has the mod can build them; the Utinni culture
  is the fiction, not a lock (a non-Utinni player honouring Rekko is a feature). The old
  `StyleCategoryDef` + `CultureDef` patch route is dropped: it can only roll a random subject
  from a folder, which is exactly what R2 rejects, and `ThingStyleDef` cannot carry a picker
  (it holds only `graphicData`, `uiIconPath/Scale`, `overrideLabel`, `color` — MEASURED,
  `Verse/ThingStyleDef.cs`).
- **Art description**: vanilla `CompProperties_Art` names the piece and writes its "depicts"
  text from a random tale via `nameMaker`/`descriptionMaker` (`NamerArtSculpture`,
  `ArtDescription_Sculpture` in `Buildings_Art.xml`). A fixed-subject idol should instead carry
  a per-god `RulePackDef` pair (name = the god's, description = one line of his tenet). Whether
  a custom `descriptionMaker` can bypass the tale entirely is UNMEASURED — FOUNDRY reads
  `CompArt.InitializeArt` before wiring; the fallback is the vanilla tale (a statue of Sh'kaar
  "depicting" a colonist's wedding is a tolerable v1 defect, not a blocker).
- Save/back-compat: adds defs only; nothing renamed, nothing removed.
- The picker-gizmo alternative (one `RUT_Idol` def, a gizmo cycling 13 graphics) is the other
  shape R2 permits. It costs a comp and a `Graphic` swap at draw time, and it is what the
  `lc.tammybee.selectablesculpturegraphic` mod does for vanilla sculptures (its DLL is
  unreadable, behaviour UNMEASURED). Not chosen; revisit only if 16 build-menu entries prove
  unwieldy in his hands (open question O1).

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
- **Folder layout**: `Textures/Things/Building/Art/RUT_UtinniIdols/<defName>.png`, one PNG per
  def, `Graphic_Single` (no pools — R2).
- **Per-subject briefs** are §5 below; the render spec's motif column is the authority when a
  brief and the §1.2 one-liner disagree. Sh'kaar's grand IS the flame idol's art (§2.5, R5), so
  its silhouette leaves a clear sun-disc crown and two open palms as flame points.
- Existing art was searched before briefing (§5, per subject): the bust/full-figure god
  paintings exist under `design/Jawa/art/gods/`; NO statue art exists anywhere in the artpipe.

### 1.5 Mod Settings

Mod 1 is XML except for a minimal settings class (the every-mod rule): **(a)** "Utinni idols in
the build menu" on/off — when off, a `StaticConstructorOnStartup` clears `designationCategory`
on the 16 defs so nothing new can be placed (already-placed idols stay; not worldgen-affecting);
**(b)** "Sumpgas fuels flame statues" on/off (only shown when Mod 2 is loaded; see §2.3);
**(c)** "Sh'kaar's idol burns" on/off (only shown once §2.5 ships). Defaults on. All-off = a mod
that does nothing, and nothing breaks.

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
  `drawOutOfFuelOverlay true`). RM-tier `fuelFilter`: **`Chemfuel` only, no wood** — ruling R4
  (question card, 2026-09-25). Consumption: Ember 0.12/day, Dancer 0.28, Colossus 0.5 —
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

**Sh'kaar is the first flaming idol** — ruling R5 (question card, 2026-09-25); Ohm's and
Rekko's grands stay cold until he says otherwise. Mod 1's idols are already separate defs
(§1.3), so the flaming one is just `RUT_Idol_Shkaar_Grand` gaining comps — no Mod 2 dependency:
`CompProperties_Refuelable` on Sumpgas, `CompProperties_Glower`, and **vanilla
`CompProperties_FireOverlay` for ONE flame point** (the sun-disc crown) — all vanilla, no C#.
When Mod 2 is present, a `PatchOperationFindMod mandrake.rm.flamestatues` patch swaps that single
overlay for `RM_CompProperties_FlamePoints` with the full palms+crown set. So: one flame without
Mod 2, the whole show with it, and the holy-act precept (`SUMP_UTINNI_LAYER_1` §2) targets
`RUT_Idol_Shkaar_Grand`, never a Mod 2 def. The art is one texture: the cold grand and the
burning grand are the same PNG (§2.6's "no fire in the sprite" law), so the idol is buildable
unfuelled in the base Mod 1 and simply burns once fuelled.

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

Order follows R1: **Mod 1 (Utinni statues) ships first, Mod 2 (flame statues) second.**

1. **Mod 1 skeleton** — folder, About.xml, 16 idol/votive defs (§1.3) over placeholder art (a
   grey silhouette per tier is enough), the `RUT_UtinniIdols` dropdown, settings §1.5(a).
   Ships: the player picks and builds any of the thirteen subjects. Deploy, quicktest list + all
   DLC.
2. **Mod 1 art** — the 13 subjects of §5 queued as one artpipe wave (R3: all nine gods AND the
   four votives), wired into `Textures/…/RUT_UtinniIdols/` as each lands; the three grands are
   a second short wave. Every landed PNG replaces its placeholder in the same commit.
3. **Sh'kaar flame idol** (§2.5, R5) — `RUT_Idol_Shkaar_Grand` gains Sumpgas refuel + glower +
   one vanilla fire overlay; settings §1.5(c). Opens the holy-act work in `SUMP_UTINNI_LAYER_1`.
4. **Mod 2 skeleton** — folder, About.xml, three defs with `CompProperties_Refuelable`
   (Chemfuel only, R4) + `CompProperties_Glower` + ONE vanilla `CompProperties_FireOverlay` each,
   placeholder art; delete `RM_FlameStatuary` from EnvironmentalHazards after the keeper-save
   grep (§2.1). Ships: fuelled statues that burn one flame.
5. **Flame-point comp** — `RM_CompFlamePoints` + props, `IThingGlower`, quality scaling, flecks;
   swap step 4's overlay for point lists; Mod Settings §2.4. Ships: multi-point flames. Mod 1's
   Sumpgas patch onto Mod 2 (§2.3) and the Sh'kaar palms+crown swap (§2.5) land here too.
6. **Mod 2 art** — three sprites per §2.6, `points` measured from the PNGs.
7. **Helixien link** — §2.3 last paragraph, only after the reflection member is read from source.

## 4. Owner rulings (ledger, `STATUE_ART_EXPANSION_1`)

Every ruling below is already folded into §§0–3; this list is the provenance.

| # | Ruling | Source |
|---|---|---|
| R1 | **Two mods, in order: Utinni statues first, then flame statues.** Decorative art for the vanilla sculpture folders is deferred. | Typed, 2026-09-25: *"Ok, let's wait on the "just more decorative art" for the vanilla folders. Let's focus on the two new things: Utinni-related statues, and then the Flame statues. Just two mods for now."* |
| R2 | **The player MUST choose which god a statue honours.** A random roll from the Utinni pool alone is rejected. Either a picker on the sculpture or one buildable per god. | Typed, 2026-09-25: *"Either player picks or they are all separate objects, but it's important the player be able to choose who they are honoring"* |
| R3 | **Wave one is all nine gods AND the four votives — 13 subjects.** | Decision taken by question card, 2026-09-25 (spec at `a2b5fe5c0`, old Q2). |
| R4 | **Outside the campaign, flame statues burn Chemfuel only.** Inside it, Sumpgas (§2.3). No wood. | Decision taken by question card, 2026-09-25 (old Q3). |
| R5 | **Sh'kaar is the first flaming idol.** Ohm's and Rekko's grands are not flame-variant candidates until he says so. | Decision taken by question card, 2026-09-25 (old Q4). |
| R6 | The fuel routes, in preference order: Sump gas, Helixien gas (if present instead or in addition), manual refuel otherwise. | Typed in the filing, 2026-09-25: *"Then we'd tie that in to the Sump mod, the Helixian gas mod (if that's present instead or in addition), or manual refueling if not."* |
| R7 | The Steel Flame statuary art is a placeholder to replace. | Filing title, 2026-09-25. |

## 5. Art queue — the 13 subjects

Thirteen artpipe jobs, **not yet queued** (this is the brief, `fill_queue.py` files them at
build step 2). Common job shape, per `infrastructure/artpipe/README.md`: `rimflow_item_id`
`STATUE_ART_EXPANSION_1`; `reference` **null** (new art — a `reference` would trigger
reskin-validate and always fail); `facing` `south` only (statues are `rotatable false`, one
texture); `background` `transparent`; `channel` codex; `priority` 40. Canvas per the
README's heuristic, erring generous: **small 256, large 512, grand 1024** (drawSize×128 rounded
up to a power of two; the enhanced-zoom stack voids the old 256 ceiling). Grand subjects sit in
the central ~75% of the canvas so a 2×2 footprint never overhangs past the drawSize box.

**Common prompt head (every job):** *"RimWorld building sprite, top-down-oblique vanilla
building angle, painterly vanilla-RimWorld art style: a carved stone statue on a low plinth,
desert sandstone and bone-pale stone reading as CARVED — a statue of the figure, not the
figure. Hooded and robed Jawa figure, hood up, face a black void with two inlaid amber-glass
eyes as the only lit feature, over-sized gnarled five-fingered hands from deep sleeves. [MOTIF].
[ACCENT] as a mineral vein or inlaid metal, never paint. No fire, no glow, no ground shadow, no
background scenery. Heavy, clean black outline around the whole silhouette and all major
internal linework, thick enough to read clearly at standard RimWorld zoom and below."*
Votives and the Crawler drop the hooded-figure clause. Art is authored grey-warm and
desaturated so stuff colour can tint it (`useIngredientsForColor`).

**Search done 2026-09-25 before briefing** (`infrastructure/artpipe/done/`, `_artsrc/` (1,407
entries), `registry.jsonl` (5,980 lines), `Transient/*.decisions.json`): **no statue, idol or
votive art exists for any of the 13.** Name-matches were all false positives — `graffiti_tally_*`
is the prisoner tally-mark graffiti icon (`GRAFFITI_VARIANT_COUNTS_1`), `scald_noohm_*` is a
Scald jelly creature, `rot_thozzik*` a Rot insect, `rutmortuarycrawler_*` a creature. The only
usable inputs are the god PAINTINGS (`design/Jawa/art/gods/god<N>_<name>.png` for all nine,
busts for all nine in `busts/`, full-figure for Ishko/Mob'Unloo/Ohm/Oomo only in `fullfigure/`)
— style references for pose and motif, never a `reference` field — and, for the Crawler, the
Armoury's `CrustySandcrawlerHull.png` / `Sandcrawler1x1DoorA.png` wall and door tiles as hull
texture reference.

| # | Job id | Def | Canvas | Visual brief (the `[MOTIF]` / `[ACCENT]` slots) | Existing art |
|---|---|---|---|---|---|
| 1 | `rut_idol_ishko_v1` | `RUT_Idol_Ishko` (large, 512) | 512 | The watcher half-sunk: the figure emerges only from the chest up out of the plinth, as if rising through a hatch; the robe's lower folds dissolve into the plinth's own stone so no hemline exists. Hood pulled low, the two eyes set LOW and small, the dimmest of the nine — barely-lit amber, watching. Hands flat on the hatch rim either side, fingers splayed. Accent near-black: a vein of obsidian running down the hood. The whole read is patience and ambush. | none; `god1_ishko.png`, `ishko_bust.png`, `ishko_fullfigure.png` as pose refs |
| 2 | `rut_idol_ohm_v1` | `RUT_Idol_Ohm` (large, 512) | 512 | Both arms raised high, too-long gnarled hands open and reaching upward as if toward hands he lost; the sleeves fall back to the elbow. At the plinth base a dormant droid head lies on its side, carved in the same stone, one eye-socket empty. Eyes warm and confident, wide. Accent arc-blue: a thin inlaid copper-blue line arcing from fingertip to fingertip across the hood. Also the base for #2g. | none; `god2_ohm.png`, `ohm_bust_A/B.png`, `ohm_fullfigure.png` |
| 2g | `rut_idol_ohm_grand_v1` | `RUT_Idol_Ohm_Grand` (grand, 1024) | 1024 | Same figure as #2 at 2×2, but the base widens into a heap of three dormant droids in carved stone leaning against the plinth as pilgrims; a cable-relief runs from the heap up the robe's back. A distinct carving, not a resize. | none |
| 3 | `rut_idol_oomo_v1` | `RUT_Idol_Oomo` (large, 512) | 512 | Hunched, shoulders forward, both cupped hands held close to the chest holding one single carved droplet the size of a fist; the hem of the robe sags and darkens (a darker stone band) as if damp. Eyes anxious, angled inward. Accent water-silver: the droplet is inlaid pale silver-grey stone, polished, the only smooth surface on the statue. | none; `god3_oomo.png`, `oomo_bust.png`, `oomo_fullfigure.png` |
| 4 | `rut_idol_mobunloo_v1` | `RUT_Idol_MobUnloo` (large, 512) | 512 | Seated on a squat ledger-stone, a hand-scale (two pans on a beam) held up in one hand, the other hand resting on a stack of scavenged tokens; five-bar tally scratches carved down the front of the robe in rows. Eyes level and appraising. Accent copper/green: the scale pans inlaid verdigris copper. | none; `god4_mobunloo.png`, `mobunloo_bust.png`, `mobunloo_fullfigure.raw.png` |
| 5 | `rut_idol_rekko_v1` | `RUT_Idol_Rekko` (large, 512) | 512 | Kneeling, a broken droid cradled across his lap, one hand inside its open chest cavity mending; the robe is carved as a patchwork of salvaged plates and stitched panels. Eyes the gentlest of the nine, half-closed, looking down at the droid. Accent salvage-bronze: the patch-seams inlaid dull bronze. Also the base for #5g. | none; `god5_rekko.png`, `rekko_bust.png` |
| 5g | `rut_idol_rekko_grand_v1` | `RUT_Idol_Rekko_Grand` (grand, 1024) | 1024 | Same figure at 2×2, the plinth now a workbench-slab strewn with carved parts (a limb, a head, coiled cable) and a second, already-mended droid standing at his shoulder with one hand raised. A distinct carving, not a resize. | none |
| 6 | `rut_idol_tabaa_v1` | `RUT_Idol_TaBaa` (large, 512) | 512 | Mid-stride, one foot already off the plinth's edge, the robe blown hard sideways as if wind-caught (carved folds streaming to one side), face turned away from the viewer toward the empty side of the plinth so only one eye is visible in profile. Accent wind-grey/gold: a thin gold line along the streaming hem. The plinth edge crumbles under the leading foot. | none; `god6_tabaa.png`, `tabaa_bust.png` |
| 7 | `rut_idol_zizzik_v1` | `RUT_Idol_Zizzik` (large, 512) | 512 | Crouched low on the balls of the feet, one hand pressed flat on a cracked machine part (a split housing with a coil spilling out), the other hand raised with two fingers pinched as if about to flick something. Eyes slanted upward in delight — the only smiling eyes among the nine. Accent spark-green: the crack in the housing inlaid pale green stone. | none; `god7_zizzik.png`, `zizzik_bust.png` |
| 8 | `rut_idol_shkaar_v1` | `RUT_Idol_Shkaar` (large, 512) | 512 | Tall, rigid, arms straight down and palms turned forward. **The one exception to hood-up:** the hood is thrown back and merges into a carved sun-disc behind the head, rays cut into the stone; the face is a void with the widest, hottest eyes of the nine, set high. Accent white-gold: the sun-disc's rays inlaid pale gold. Reads cruel and exposing, never heroic. | none; `god8_shkaar.png`, `shkaar_bust.png` |
| 8g | `rut_idol_shkaar_grand_v1` | `RUT_Idol_Shkaar_Grand` (grand, 1024) — **the flame idol, R5** | 1024 | Same figure at 2×2, but arms raised to shoulder height with **both palms cupped upward and open** and the sun-disc crown carved as a shallow **bowl** at its apex — three cold vents (§2.6 law: blackened, soot-fanned openings, no fire drawn) that the engine will light. The plinth is a carved ring of fire-pit stones. Silhouette must leave the two palms and the crown bowl unobstructed; §2.5's `points` are measured from this PNG. | none |
| 9 | `rut_idol_ozzik_v1` | `RUT_Idol_Ozzik` (large, 512) | 512 | Standing in a grand robe with a long trailing hem, but the robe is torn open down one side and a great rent crosses the chest; on the head, over the hood, a broken salvaged crown (a bent scrap-metal circlet missing a third of its ring). Eyes proud and grieving at once — wide but downcast. Accent purple/gold: the crown's surviving points inlaid gold, the tear's edges a dull purple vein. | none; `god9_ozzik.png`, `ozzik_bust.png` |
| 10 | `rut_votive_bandolier_v1` | `RUT_Votive_Bandolier` (small, 256) | 256 | No figure. A votive stone: a rough sandstone block, on top of it a carved bandolier strap coiled twice with its heavy square buckle centred and upright, the clan's mark scratched into the buckle face. Dull bronze inlay on the buckle only. | none (`KotORBandolierNorthFix` is apparel, unrelated) |
| 11 | `rut_votive_droplet_v1` | `RUT_Votive_Droplet` (small, 256) | 256 | No figure. A shallow carved dish, cracked across, on a sandstone block; in the dish's centre one single carved droplet, polished pale silver-grey, the only smooth surface — Oomo's tithe. The crack runs under the droplet and stops. | none |
| 12 | `rut_votive_tally_v1` | `RUT_Votive_Tally` (small, 256) | 256 | No figure. A stack of scavenged tokens (mismatched discs, washers, a bent coin) under a slab of scratched stone; five-bar tally marks cover the slab's face, several crossed out — Mob'Unloo's ledger. Verdigris copper on two of the tokens. | none (`graffiti_tally_*` is the prisoner-graffiti icon; motif reference only) |
| 13 | `rut_relief_crawler_v1` | `RUT_Relief_Crawler` (grand, 1024) | 1024 | No figure. A 2×2 relief-block: a sand crawler carved in high relief on a slab lying flat-ish on its plinth, seen from the oblique building angle — the wedge hull, the row of rusted plates, the great treads along both sides, the ramp lowered at the front. The clan's ark before the ship. Rust-red vein along the hull plates; hull texture after the Armoury's `CrustySandcrawlerHull.png`. | none; wall/door tiles above as hull texture refs only |

Sixteen jobs (13 subjects + 3 grands). The three Mod 2 flame statues (§2.6) are a separate,
later wave and are not briefed here.

## 6. Open questions (yes/no, for the owner)

- **O1.** Sixteen separate idols in one build-menu dropdown — is that acceptable, or do you want
  the single picker-gizmo object instead (§1.3's alternative)?
- **O2.** Should Ohm and Rekko also get grand-size (cold, non-flaming) idols in wave one, or do
  only Sh'kaar's grand and the Crawler ship at grand size?
- **O3.** Should the idols be buildable by ANY colony that has Mod 1, or only by colonies whose
  ideoligion carries the Utinni culture?
- **O4.** Does the Sh'kaar flame idol need to burn (Sumpgas refuel + flame) in Mod 1's first
  release, or is a cold Sh'kaar acceptable until Mod 2's flame comp exists?
