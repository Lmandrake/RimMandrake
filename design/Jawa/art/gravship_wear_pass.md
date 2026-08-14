# gravship_wear_pass.md — making the Kolyska read "old, rusty brown, and terrible"

_CREATE, 2026-08-13. **This is a proposal. Nothing here has been deployed and no shipping
texture or def has been changed.** Every claim is evidenced from the live `DefDump/`, the
shipped XML, or a rendered offline preview whose script is committed beside this file._

Owner's brief: the Jawa gravship should look _"old, rusty brown, and terrible — just like
Jawa like."_ Beyond that: what to replace with twisted metal, and what to put on the floor
to reward a closer look.

---

## 0. The verdict, up front

> **Colour is free. Damage is not. Iconography is nearly free, because the system already
> ships.**
>
> **Roughly 90% of "old, rusty brown" is reachable by tint alone** — as a def patch, with
> zero pixels authored. **Roughly 0% of "terrible" is** — dents, tears, holes and twisted
> plating are silhouette, and a colour multiply cannot move a silhouette.
>
> _Where the 90% comes from:_ **944 of 945** buildable defs in ship-relevant categories
> accept a colour without new art (§1.2) — but that is the def count, not the look. The
> discount is the one real limit: `<color>` multiplies, so it can only darken (§1.3), and
> a handful of pieces are already too dark to move much. Call it nine parts in ten of the
> *perceived* colour change, for one XML file.
>
> But "terrible" does not need new art either, because **RimWorld already ships ~170
> pre-rusted wreck props** and the only thing missing is permission to place them.

The three questions therefore have three different answers, and conflating them is what
would waste an art pass:

| what the owner asked for | is it colour or shape? | cost |
|---|---|---|
| **rusty brown** | colour | **free** — one `<color>` node per def |
| **old / worn** | mostly colour, some shape | **cheap** — tint + shipped grime/filth + prop dressing |
| **terrible / twisted** | shape | **free by SUBSTITUTION**, expensive by drawing |
| **floor designs** | new shape, tiny | **cheap** — 8 lines of XML + one greyscale PNG each |

---

## 1. How much is reachable by tint — the mechanism, and the evidence

### 1.1 The finding that decides the cost of everything else

**A mask is NOT required to tint a RimWorld building.** This is the load-bearing fact and
it is the opposite of what the dog-sled precedent might suggest.

The default `Cutout` shader honours `graphicData/color` and multiplies it over the whole
sprite. Ludeon relies on this itself. Two defs, **one atlas**, differing only by that node:

```
Data/Odyssey/Defs/ThingDefs_Buildings/Buildings_Misc.xml:161
    AncientFortifiedWall          <color>(127,135,127)</color>   "Colored for planetside maps"
Data/Odyssey/Defs/ThingDefs_Buildings/Buildings_Misc.xml:186
    OrbitalAncientFortifiedWall   <color>(132,140,140)</color>   "Colored for space maps"
```

Both point at `Things/Building/Linked/AncientFortifiedWall_Atlas`. Neither declares a
`shaderType`. Neither has a mask. Ludeon shipped a second wall for the price of one RGB
triple.

The engine-level confirmation is the opt-out: exactly **two** buildings in the entire
shipped game set `<ignoreThingDrawColor>true</ignoreThingDrawColor>` — `GrayDoor`
(Anomaly) and `AncientBlastDoor` (Odyssey, `Buildings_Misc.xml:199`). An opt-out only
exists because the default is opt-in. ⚠️ **`AncientBlastDoor` will silently ignore a
`<color>` patch** — do not waste a patch on it.

### 1.2 The census, from the live def dump

Method: `design/Jawa/art/scan_graphics.py` streams the ~850 MB
`DefDump/defs/ThingDef.json` — the **merged, post-patch** state the running game actually
holds — and emits one row per building with `texPath`, `shaderType`, `color`, `colorTwo`,
`colorThree`, `stuffCategories`, `drawSize`. Regenerate with `python3
design/Jawa/art/scan_graphics.py`.

⚠️ **Use the dump, not the shipped XML, for this question.** They disagree, and the dump is
right. Example measured today: Odyssey's `GravEngine` ships with
`texPath Things/Building/GravEngine/GravEngine`, but the live dump holds
`Things/Structures/GravEngines/GravEngine/GravEngine` — **Vanilla Gravship Expanded
retextures the entire vanilla gravship set out from under the DLC.** Any plan written off
the raw Odyssey XML is planning against art the game is not drawing.

Over the **945 buildable defs in ship-relevant designation categories**:

| bucket | count | share |
|---|---:|---:|
| **B — stuffable** (material choice colours it, no patch at all) | 407 | 43.1% |
| **A3 — plain `Cutout`** (one global `<color>` node works) | 501 | 53.0% |
| **A1 — `CutoutComplex` + mask** (two independent regions) | 36 | 3.8% |
| **C — other shader, needs a look** | 1 | 0.1% |

Narrowed to the **core gravship platform / fuel / vacuum set — 38 defs — 37 are plain
`Cutout` and 1 is stuffable.** Not one has a mask. So on the ship proper the lever is the
crude one, and that is fine, because the crude one is the one that makes things rusty.

### 1.3 The one honest limit: `<color>` multiplies, so it can only darken

This is measured, not assumed. `preview_gravship_rust.py` reports the mean of every source
before tinting:

```
GravshipStructuralBeam_Atlas   mean (54, 53, 54)     <- already almost black
BrokenSubstructure             mean (81, 82, 86)
GravEngine (VGE retexture)     mean (113,130,135)
KT-400 hull, masked RED region mean (119,119,119)
DreadnaughtWallA, RED region   mean (171,171,171)
```

Solving `color = 255 * target / source` for a mid rust-brown target of `(124,88,58)` clips
to `(255,255,255)` on the first three — **no `<color>` value exists that lifts them to a mid
brown.** You cannot brighten by multiplying.

What you *can* do to a dark source is bleed the cold blue-grey out of it and leave oxide.
A wash whose max channel is 255 preserves luminance and shifts hue:

```
<color>(255,150,96)</color>
  GravshipStructuralBeam  (54,53,54)    -> (54,31,20)    dark rust
  BrokenSubstructure      (81,82,86)    -> (81,48,32)    rusted deck
  GravEngine              (113,130,135) -> (113,76,50)   corroded copper housing
```

**That is exactly the requested look.** "Old, rusty brown and terrible" wants darker and
warmer. The multiply-only limit is not fighting the brief; it is aligned with it. It would
only bite if we ever wanted the ship to look *clean*.

### 1.4 Where a mask exists, you get two regions for free

36 ship-relevant defs are `CutoutComplex` with a real mask on disk. On those, `<color>`
paints the RED mask region and `<colorTwo>` the GREEN, independently. The strongest are the
KotOR gravship hull overlays, which are **whole-ship silhouettes at `drawSize (32,32)`**:

| def | file | today | mask |
|---|---|---|---|
| `guy762_SWGravshipOverlay_KT400Freighter` | `Gravship_KT400Freighter.xml` | `(215,240,255)` / `(255,240,125)` — cold white and yellow | 768², R+G |
| `guy762_SWGravshipOverlay_DynamicFreighter` | `Gravship_DynamicFreighter.xml` | `(135,90,50)` / `(225,225,225)` | 768², R+G |
| `guy762_PoweredWall_DreadnaughtA` | `Structure_SWWalls.xml:223` | `(140,65,65)` / `(165,165,180)` | 640², R+G |

All under `/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/3254370945/`
(Star Wars KotOR Resources and Materials — **verified ACTIVE** in `ModsConfig.xml` by
packageId `guy762.MM.KotORCore`).

Solved values that land plate `(118,74,45)` and trim `(132,116,87)`:

```
KT-400            <color>(252,158,96)</color>   <colorTwo>(185,162,122)</colorTwo>
Dynamic-class     <color>(160,100,61)</color>   <colorTwo>(243,213,160)</colorTwo>
DreadnaughtWallA  <color>(176,110,67)</color>   <colorTwo>(191,168,126)</colorTwo>
```

### 1.5 The sample images

Rendered offline by `design/Jawa/art/preview_gravship_rust.py` — the same method as
`src/Jawa/DesertVehicleReskin/Source/preview_tint.py`, with a **true-in-game-size strip on
every panel** at both max zoom (64 px/cell) and play zoom (~22 px/cell), per
`traps-art.md #45`.

| sheet | shows |
|---|---|
| `design/Jawa/art/REVIEW_gravship_rust_masked.png` | Three masked pieces, shipped colours vs solved rust. The KT-400 goes from cold white/blue/yellow to a genuinely rusted hull. **Zero pixels changed.** |
| `design/Jawa/art/REVIEW_gravship_rust_unmasked.png` | Three unmasked pieces under one global `<color>(255,150,96)`. GravEngine goes chrome-white to corroded copper; the beam atlas goes cold steel to dark rust. |
| `design/Jawa/art/REVIEW_gravship_deck_sigil.png` | A shipped floor decal composited on a rusted deck plate, in three paint colours — the finished look of the floor proposal. |

⚠️ **The PNGs are deliberately NOT committed.** `design/Jawa/art/.gitignore` already
excludes `*.png` there, with a stated licensing rationale: these sheets are recoloured
third-party mod textures, exactly the "borrowed pixels" that rule exists to keep out of the
repo. That rule also says _"derived art gets its own decision when it lands"_ — this is that
decision, and I have kept it out. **The scripts are committed and regenerate all three
sheets in about a minute**, which is what protects the work from the tmpfs scratchpad. If
the owner wants the sheets tracked anyway, that is a licensing call for them, not for me.

Regenerate:
```
/home/mandrake/.venvs/art/bin/python design/Jawa/art/preview_gravship_rust.py
```

---

## 2. Twisted metal — what replaces what

**Do not draw wreckage. RimWorld already shipped it, pre-rusted, and we are not using it.**

The live dump holds **~170 `Ancient*` building defs** across Core and the DLCs whose art is
already scorched, rusted, dented and broken. Every one of them has
**`designationCategory` = none** — they exist only for map generation, so the player cannot
place them and we have never seen most of them.

### 2.1 The ones that belong on a derelict Jawa deck

Grouped by what they say. All Core or Odyssey, all mapgen-only today.

**Structural failure — "this section is broken":**
`AncientDestroyedConsole`, `AncientDestroyedConsoleLarge`, `AncientCraneArm`,
`AncientCraneArmSmall`, `AncientCraneBase`, `AncientCraneColumn`, `AncientPipe`,
`AncientPipelineSection`, `AncientPipes`, `AncientHeatVent`, `AncientSmokeVent`,
`AncientToxVent`

**Dead ship systems — the fiction of a wreck being healed:**
`AncientGravEngine`, `AncientGravReactor`, `AncientTerraformer`, `AncientUplink`,
`AncientShipBeacon` ("ancient nav beacon"), `AncientMechDropBeacon`,
`AncientRustedDropship`, `AncientDropshipEngine`, `AncientJetEngine`,
`AncientTransportPod`, `AncientRustedEngineBlock`, `AncientLargeRustedEngineBlock`,
`AncientSecurityTerminal`

**Scavenger clutter — the hold, the aisles, the shrine approach:**
`AncientBox_SteelSlag`, `AncientPallet_SteelSlag` (literally "steel scrap"),
`AncientMetalCrate`, `AncientOpenContainer`, `AncientCratePallet`, `AncientChembarrel`,
`AncientChembarrelPallet`, `AncientChemfuelCanister`, `AncientBarrel`,
`AncientFilingCabinet`, `AncientLockers`, `AncientSafe`, `AncientShelf`,
`AncientIndustrialShelf`, `AncientWoodenCrate`, `AncientCardboardBox`

**Crew quarters that are already ruined** — and note these two carry a mask:
`AncientSingleBed` / `AncientDoubleBed` (Odyssey, `Buildings_Ancient.xml:722,742`,
`shaderType CutoutComplex`, texPaths `.../House/RustedSingleBed` and `RustedDoubleBed`).
The Jawa sleep among the machines (`ship_distinctive_features.md` §7) — a **rusted** bed is
the correct bed, and it is two-region tintable on top.

**Lighting, which doubles as the repair progress bar (§5 of that doc):**
`AncientEmergencyLight_Red`, `AncientEmergencyLight_Blue`, `AncientEmergencyLight_Green`,
`AncientLamp`, `AncientLamppost`

**Already-broken ship chunks, and the one gravship wreck we can already build:**
`ChunkSlagSteel` (`Things/Item/Chunk/ChunkSlag` — already used in our scrapfields),
`ChunkMechanoidSlag`, `ShipChunk`, `ShipChunk_Mech` (Odyssey, `Graphic_Random` — it draws a
*different* chunk each time, which is free variation), `BrokenGravEngine` (Gravship
Crashes, **active**), and `VGE_GravhulkEngine` — the **only wreck-looking def in the game
that is already player-buildable** (`designationCategory VGE_Platform`).

### 2.2 Broken deck terrain — already shipped, already ours

| TerrainDef | mod | texture |
|---|---|---|
| `BrokenSubstructure` | Odyssey, retextured by **Gravship Crashes** (active) | `Terrain/Surfaces/Substructure/BrokenSubstructure.png`, 2048² |
| `VGE_DamagedSubstructure` | Vanilla Gravship Expanded (active) | `Things/Terrain/Substructure/DamagedSubstructure.png`, 2048² |
| `VGE_GravshipSubscaffold` | VGE — **buildable**, `designationCategory VGE_Platform` | `Things/Terrain/Substructure/Subscaffolding` |

`VGE_GravshipSubscaffold` is bare structural ribbing with no deck plate over it. **That is
the "dead prong" (§4) and the un-repaired wing, for free, today, with no mod at all** — just
lay subscaffold instead of substructure where the ship is meant to be wounded.

### 2.3 The proposed mechanism, and the honest caveat

Turning the mapgen library into a Jawa decor set is **one `PatchOperationAdd` per def**,
adding `<designationCategory>` and a `<costList>` (steel + slag, which is what a Jawa would
pay). No new art, no C#.

⚠️ **Not verified: whether each of these defs is actually placeable once given a category.**
Some mapgen props may lack a `<building>` block, a blueprint, or a construction affordance,
and will error or place strangely. This needs a bench test on ~5 representative defs before
committing to 30. It does **not** need a game load — the rimbridge can spawn them live.

---

## 3. Floor designs — and this is the best idea in the document

### 3.1 The system already ships, and it is ours

**Outer Rim - Furniture & Decor** (`Neronix17.OuterRim.FurnitureAndDecor`, **verified
ACTIVE**) ships **234 floor decals** off a single abstract parent:

`/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/2919553599/1.6/Defs/ThingDefs_Buildings/Decals__Base.xml:4-47`

```xml
<ThingDef Abstract="True" ParentName="BuildingBase" Name="OuterRim_DecalBase">
  <graphicData>
    <graphicClass>Graphic_Single</graphicClass>
    <shaderType>Transparent</shaderType>
    <color>(255,255,255,160)</color>      <!-- painted-on, not printed-on -->
  </graphicData>
  <comps><li><compClass>CompColorable</compClass></li></comps>
  <altitudeLayer>Floor</altitudeLayer>
  <drawerType>MapMeshOnly</drawerType>
  <passability>Standable</passability>   <pathCost>0</pathCost>
  <fillPercent>0</fillPercent>
  <building><isEdifice>false</isEdifice><paintable>true</paintable></building>
  <clearBuildingArea>false</clearBuildingArea>
  <statBases><WorkToBuild>5</WorkToBuild><Beauty>1</Beauty></statBases>
  <costList><OuterRim_Durasteel>1</OuterRim_Durasteel></costList>
  <rotatable>true</rotatable>
</ThingDef>
```

Read what that buys:

- **It lies flat on the deck and blocks nothing** — `Floor` altitude, `Standable`,
  `pathCost 0`, `fillPercent 0`, `isEdifice false`, `clearBuildingArea false`. Pawns walk
  over it, you can build furniture on top of it, it never fights the layout.
- **`CompColorable` + `paintable true`** — the player repaints it **in game, with no
  reload**, in any of the **181 shipped `ColorDef`s**. One greyscale PNG becomes 181 looks.
- **A new decal is EIGHT LINES of XML.** Verbatim shape from `Decals_Misc.xml:14-22`:

```xml
<ThingDef ParentName="OuterRim_Decals_Misc">
  <defName>Jawa_Decal_Rekko</defName>
  <label>sigil (Rekko of the Second Hand)</label>
  <graphicData>
    <texPath>Jawa/Decals/Sigil_Rekko</texPath>
    <drawSize>(3, 3)</drawSize>
  </graphicData>
  <size>(3, 3)</size>
</ThingDef>
```

### 3.2 What to draw — VISION has already written the iconography

I am following the fiction, not inventing it. `jawa_xenotype_and_religion.md` §2.0b gives
each of the nine gods of **The Salvation** an explicit visual **form**. These are not my
inventions; they are quoted:

| god | the stated form | reads as a floor sigil? |
|---|---|---|
| ① **Ishko the Unmaskable** | "a pair of glowing orange eyes in the dark" | **yes** — two shapes, unmistakable at 192 px |
| ② **Ohm the All-Current** | "current in a wire; the spark that wakes a dead engine" | **yes** — a bolt through a broken line |
| ③ **Oomo the Unspilled** | "a single trembling droplet that never falls" | **yes** — one droplet, the simplest glyph of the nine |
| ④ **Mob'Unloo the Ever-Owed** | "two unblinking eyes above an endless tally" | **yes** — eyes over tally marks |
| ⑤ **Rekko of the Second Hand** | "a scarred hand rising from a scrap-heap" | **yes** — and it is the sect's own emblem |
| ⑥ **Ta'Baa the Unrooted** | "the receding dune-line; the engine-glow climbing away" | risky — a horizon is weak in a square |
| ⑦ **Zizzik the Spark-Maker** | "a rattle you can never locate; the errant spark in dry sand" | risky — "cannot be located" resists a fixed glyph |
| ⑧ **Sh'kaar the All-Searing** | "white glare and heat-shimmer" | **yes** — a burst; the closest to a classic sun-disc |
| ⑨ **Ozzik the Shamed** | "a tarnished crown half-buried in sand" | **yes** — a half-sunk crown |

**Seven of nine already have a drawable glyph.** Two (Ta'Baa, Zizzik) are described as
things that resist depiction, which is a fiction problem before it is an art problem — see
§6.

### 3.3 Where the sigils go, from the deck plan

The ship docs already say where devotion lives, so the decals have addresses:

- **The shrine-core at the true ring centre, tile (45,92), around the grav-engine**
  (`ship_distinctive_features.md` §1) — "the engine is literally the object of the faith".
  The largest sigil goes here. Rekko (restore the original) and Ohm (the resident of the
  ship) are the two whose claim on the engine is textual.
- **A shrine to what each pod once did** — §6, ACCEPTED: seven rim function-pods, each with
  "a small dedicated altar to its trade". **The skill-resonance grid (§2.0c) already maps
  every skill to a god**, so each pod's sigil is *derivable, not invented*: forge → Rekko,
  kitchen → Oomo, research → Ohm, cargo/trade → Mob'Unloo, and so on.
- **Airlocks** — §"Hull graffiti / clan glyphs", promoted to ACCEPTED: "Jawa territory
  markings + raid tally-marks near airlocks". Mob'Unloo is the god of the tally.
- **The belt-shrine tithe confluence**, where the seven belt trunks converge (§1.1 [IDEA]).

### 3.4 The finding that will save a redraw: paint the sigil LIGHT

Measured in `REVIEW_gravship_deck_sigil.png`. The decal draws at **alpha 160**, so it is
translucent by design — and on a deck we have just rusted brown, a **dark** paint is very
nearly invisible:

| paint | result on a rusted deck |
|---|---|
| white / bone `(255,255,255)` | **reads strongly** |
| `Structure_Limestone (158,153,135)` | **reads** |
| `Structure_UmberBurnt (90,58,32)` | **vanishes** |

So the sigil palette is the **opposite** of the hull palette: bone, limestone, sand,
sun-bleached white. Which is also the right fiction — a scavenger clan scratches its marks
in something pale onto dark metal, not in rust onto rust.

### 3.5 What floors themselves can and cannot do

I checked, because it would have been the obvious first idea and it is wrong:

- **1,239 `TerrainDef`s in the live dump. Not one buildable floor declares a `<color>`.**
  Floor colour is baked into the texture; a floor recolour is a new PNG, always.
- **233 of 944 buildable floors are `isPaintable: true`** — including **`Substructure`
  itself** (`Terrain_Foundation.xml:13`), the gravship deck. So the deck recolours for free
  through the in-game paint system, with no mod, no patch and no reload.
- Nearest shipped browns, RGB read from `Data/Core/Defs/ColorDefs/ColorDefs.xml`:
  `Structure_UmberBurnt (90,58,32)`, `Structure_BrownDark (90,69,38)`,
  `Structure_BrownDirt (119,91,50)`, `Structure_Sandstone (126,104,94)`,
  `Structure_Orange (167,96,39)`.

**Conclusion: do the deck with paint, and the iconography with decals.** Do not author
floor textures. A decal is a 1-cell-to-3-cell thing you place *on* a floor; it is
repositionable, repaintable, and costs 8 lines. A custom `TerrainDef` is a tiling atlas you
have to draw four edge cases for, and it cannot carry a one-off symbol at all.

---

## 4. Wear and age — what actually reads at RimWorld's sprite scale

The trap this section exists to avoid is `traps-art.md #45`: art correct at source and
broken at render. A muzzle drawn perfectly at 1934 px collapsed into a flat wall at the
104 px it drew at. **Everything below is stated in terms of the pixels the thing actually
occupies**, which the preview script now prints on every sheet.

The scales in play here, at max zoom (64 px per cell) and at ordinary play zoom (~22):

| thing | drawSize | max zoom | play zoom | source | downsample |
|---|---|---:|---:|---:|---:|
| KotOR hull overlay | 32×32 | 2048 px | 704 px | 768² | **upscaled — never shrinks** |
| `GravEngine` | 3×3 | 192 px | 66 px | 384² | 2× |
| floor decal | 3×3 | 192 px | 66 px | 512² | 2.7× |
| `GravshipHull` wall, deck tile | 1×1 | **64 px** | **22 px** | 640²–2048² | **10×–32×** |

### 4.1 What reads

- **Global hue and value.** A rust wash survives any downsample, because it is the mean.
  This is why tint is the highest-yield move: it is the *only* signal that is scale-proof.
- **Silhouette breaks.** A missing corner, a torn edge, a hole in a plate — these read at
  22 px because they change the shape, and shape is what survives.
- **One high-contrast mark per tile, not three.** A single dark streak across a deck plate
  reads at 22 px. Three fine scratches average into a slightly darker tile.
- **Value contrast at the boundary.** The bone-on-rust sigil reads; the umber-on-rust one
  does not. Same shape, same size — the only difference is contrast.
- **Repetition breaks.** `ShipChunk_Mech` is `Graphic_Random`. Variation between neighbours
  reads as age; a perfect grid reads as new, no matter how grubby each tile is.

### 4.2 What does not read, and is therefore wasted effort

- **Fine rust speckle, hairline cracks, bolt heads, panel-line detail.** At 22 px these
  average to a flat tone. Drawing them costs real hours and buys a slightly darker tile you
  could have got from one `<color>` node.
- **Gradients across a single tile.** Sub-cell gradients disappear; the tile averages.
- **Anything below ~3 px in the rendered sprite.** For a 1-cell wall at play zoom that is
  **anything under ~14% of the texture's width.**
- **Detail on the deck specifically.** The deck is the most-repeated, smallest-drawn surface
  on the ship. It is the *worst* place to spend pixels and the *best* place to spend paint.

### 4.3 The three age signals I would actually use, in order

1. **Warm-dark tint** (free) — the single largest perceived change per unit of effort.
2. **Irregularity** (free) — mismatched wall stuff between wings, subscaffold where the
   ship is wounded, `Graphic_Random` chunks. This is `ship_distinctive_features.md` §3
   "asymmetry as identity" made mechanical: **let the bolted-on Falcon arm be a different
   `<color>` from the ring hull.** One extra def, and the ship reads as assembled from
   salvage at a glance.
3. **Prop dressing with the pre-rusted Ancient library** (free once placeable) — clutter is
   read as age far more reliably than surface detail, and it survives every zoom because it
   is silhouette.

---

## 5. Ranked by value per effort — what I would do, in this order

| # | do this | effort | why it ranks here |
|---:|---|---|---|
| **1** | **Paint the deck.** `Substructure` is `isPaintable: true`. Pick `Structure_UmberBurnt` or `Structure_BrownDirt` and paint the whole ship. | **zero** — in game, no mod, no patch, no reload | Biggest surface on the ship, largest colour change available, and it costs one in-game action. Nothing else has this ratio. |
| **2** | **Nine god-sigil decals** on the existing `OuterRim_DecalBase`. | 9 PNGs + ~80 lines XML | This is the "reward a closer look" ask, answered exactly. The system, the placement doctrine and the iconography are all already written; only the pixels are missing. Paintable in game, so one draw serves every colour. |
| **3** | **Tint patch on the gravship set** — one `<color>` node per def across the ~38 core platform/fuel/vacuum defs, plus the two KotOR hull overlays with solved `<color>`/`<colorTwo>`. | one XML file, zero pixels | Turns the whole ship warm and corroded in a single patch. Values already solved in §1.3–1.4. Skip `AncientBlastDoor`. |
| **4** | **Unlock ~20 `Ancient*` wreck props** with a `PatchOperationAdd` of `designationCategory` + `costList`. | one XML file + a 5-def bench test | Converts ~170 pieces of shipped, pre-rusted art from invisible to placeable. The single largest art library gain available, and we do not draw any of it. Ranked below 3 only because it needs verification first. |
| **5** | **Subscaffold the dead prong.** Lay `VGE_GravshipSubscaffold` instead of `Substructure` on the un-repaired wing. | zero — in game | Delivers `ship_distinctive_features.md` §4 with a build choice. Exposed ribbing reads as a wound at every zoom. |
| **6** | **Differentiate the Falcon arm's `<color>`** from the ring hull. | ~6 lines | §3 "asymmetry as identity", made legible from orbit. Cheap, and it is the one thing that makes the ship read as *assembled* rather than merely dirty. |
| **7** | **Hand-drawn damage overlays** — torn plating, blown panels as placeable props. | real art, several pieces | Only worth starting after 1–6 land, because 1–6 may make it unnecessary. |

---

## 6. What I would NOT do, and why

- **I would not retexture the vanilla gravship set.** Odyssey ships **no `Textures/`
  directory at all** — art is packed in `AssetBundles/resources_odyssey` (74 MB). You cannot
  see what you are matching without extracting a Unity bundle, so you would be drawing
  blind against art the player already knows. And **VGE has already retextured that set**,
  so we would be overwriting a maintained mod's work with a worse guess. Tint it instead.
- **I would not author custom floor `TerrainDef`s for iconography.** A terrain is a tiling
  atlas with edge cases; it cannot carry a one-off symbol, cannot be repositioned, and
  cannot be repainted in game. The decal system does all three and costs 8 lines. This was
  the obvious first idea and it is the wrong one.
- **I would not draw rust speckle, panel lines or hairline cracks** on anything that draws
  at 1 cell. §4.2: they average to a flat tone at 22 px. This is the trap-#45 failure mode
  applied before the work rather than after.
- **I would not add masks to the unmasked gravship defs.** Patching in
  `<shaderType>CutoutComplex</shaderType>` requires authoring an `_m` sibling for **every**
  facing of **every** def, and buys a second tint region on sprites whose whole area is
  22–192 px. The global multiply already delivers the requested look.
- **I would not touch `AncientBlastDoor`.** `ignoreThingDrawColor` means a `<color>` patch
  silently does nothing — a bug that would cost a load to notice.
- **I would not use `[Odyssey] Necrotic Gravship Retextured`** (`Okagrim.NecroTexGrav`) as a
  reference. **Verified INACTIVE** in `ModsConfig.xml`. It ships a tempting 1024²
  `Substructure.png` and it is not what the game draws.
- **I would not spend the first art hours on hull overlays.** They are the only sprites
  here that are *upscaled* rather than downsampled — they already look sharp, and tint
  transforms them completely for free. The pixels are needed on the sigils, which are the
  only thing in this whole proposal that genuinely cannot be got for free.

---

## 7. Open questions the fiction does not yet decide — for VISION

These are places where I would be inventing lore if I proceeded, so I have stopped.

1. **Ta'Baa and Zizzik have no drawable form.** §2.0b gives Ta'Baa "the receding dune-line;
   the engine-glow climbing away" and Zizzik "a rattle you can never locate". Both are
   described as things that resist depiction — Zizzik's *whole point* is that he cannot be
   located. **Does the clan draw them anyway, and if so how?** Three routes, all needing a
   ruling: (a) an *empty* frame for Zizzik — the sigil is the absence, which is on-theme and
   would be striking on a deck; (b) an abstract mark unrelated to the god's form; (c) they
   have no sigil, and the shrine has seven marks and two blanks — also striking, and arguably
   truer. **I lean (a)/(c) but this is a doctrine call, not an art call.**

2. **Is Ishko's sigil allowed to glow?** His form is "a pair of glowing orange eyes in the
   dark", and the orange eyes are the xenotype's own (`Outland_Eye_Orange`). But **the clan
   is under a light-taboo** — §2.0b ⑧ says "to make a light in the dark is to do
   Sh'kaar's work". A glowing floor sigil may be blasphemy. Mechanically I can give a decal
   a `glowRadius`; I need to know whether I *should*.

3. **Is a god-sigil something the clan builds, or something it finds?** The decal has a
   `<costList>` and `WorkToBuild`, i.e. a colonist paints it. But Rekko's doctrine is that a
   salvaged thing "inherits its story" — a sigil that came *with* the wreck would be a
   different and richer object than one the crew painted. This changes whether the sigils are
   player-buildable at all or hand-placed at ship creation.

4. **Which god owns the grav-engine?** §1 of `ship_distinctive_features.md` says "the engine
   is literally the object of the faith", but §2.0b gives **Ohm** the ship's machine-spirit
   (he "possesses the Cradle-Mind") and **Rekko** the restoration imperative, and §2.0d names
   **Rekko ⇄ Ozzik** as "the sharpest internal war in the pantheon". The shrine-core sigil is
   a statement about which program is winning. **I should not pick that by accident with a
   texture.**

5. **Does the un-repaired dead prong get a sigil or a scar?** §4 keeps one mandible tip
   permanently broken. Ta'Baa reveres "old battlefields and lost settlements... holy ground
   of vindication", which suggests a wound could be *venerated* rather than merely left. That
   would make the dead prong a shrine, not an absence — a much better beat, but not one I can
   invent.

---

## 8. Provenance

- Live merged def state: `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\DefDump\defs\ThingDef.json` (849 MB) and `TerrainDef.json`, dumped 2026-08-13 17:45.
- Shipped XML: `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Odyssey\Defs\` and `...\Data\Core\Defs\`.
- Workshop mods: `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\` — `3254370945` (KotOR Resources and Materials), `3609835606` (Vanilla Gravship Expanded Ch.1), `3578515873` (Gravship Crashes), `2919553599` (Outer Rim Furniture & Decor). All four verified ACTIVE against `ModsConfig.xml` by packageId.
- Scripts, committed: `D:\Luke\dev\Rimworld\design\Jawa\art\scan_graphics.py`, `D:\Luke\dev\Rimworld\design\Jawa\art\preview_gravship_rust.py`.
- Fiction followed, not invented: `D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\jawa_xenotype_and_religion.md` §2.0b/§2.0c/§2.0d, `D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\ship_distinctive_features.md` §1/§3/§4/§5/§6/§7.
- Method precedent: `D:\Luke\dev\Rimworld\src\Jawa\DesertVehicleReskin\Source\preview_tint.py` and `...\Patches\DogSledTint_Brown.xml`.
- Scale discipline: `D:\Luke\dev\Rimworld\skills\rimworld-modding\references\traps-art.md` #45.

**Values caveat, per CLAUDE.md:** the dump is authoritative for *structure* (does this def
declare a shader, a colour, a stuff category). Where a specific RGB matters, it has been
read from the shipped XML and the path quoted. Nothing here has been confirmed in a running
game.
