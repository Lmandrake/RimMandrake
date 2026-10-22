# Tree shade model for Direct Sun: design pass, 2026-10-19

FOUNDRY design pass. No mod code or defs were changed. Parent design:
`design/RimMandrake/unified_direct_sun_heat_2026-10-19.md` (the ruled One Direct Sun model, DS1–DS8).
Build items filed by this pass: `TREE_SHADE_BUILD_CROWNS_ON_STILTS`,
`TREE_SHADE_SELFTEST_PROVE_FOREST_IS_SHADE`, and the owner decision
`TREE_SHADE_DECIDE_CROWNS_OR_LIGHTS_OUT`.

The owner, 2026-10-19, verbatim:

> "Only the day-side biomes with massive trees would have massive shade beneath them at a fixed
> angle, and we need to think about that. Most tree-dense maps will be mostly shade then (ambient heat
> yes, direct sun no). So that needs to be deeply thought though. If we have an excellent tree shade
> model working, then YES direct sun works the same everywhere on the day side. If we do not go that
> route, we may choose to turn it off on tree-heavy maps (this would be an inferior option)."

So **Direct Sun's all-day-side rollout (DS8) is conditional on this model.** Excellent tree shade →
Direct Sun runs the same everywhere on the day side. No excellent tree shade → the inferior option,
Direct Sun off on tree-heavy maps. §6 gives the test that decides which.

---

## 1. What exists today

### 1.1 Vanilla RimWorld 1.6 has no tree shade

Checked with RimSage against the 1.6 source and Core defs:

- **No mechanic reads a tree as cover from the sun.** Vanilla has no sun heat at all. Temperature is
  per-room or outdoor, and Heatstroke reads it. Nothing in it looks at plants.
- **Light.** `ThingDef.blockLight` is read only for **edifices** (`SectionLayer_Darkness`,
  `SectionLayer_LightingOverlay`, `Building.cs`). A tree is a `Plant`, never an edifice, so a forest
  floor is exactly as bright as a meadow. Only roofs dim sky light.
- **Rendered shadows.** Long sun shadows (`SectionLayer_SunShadows`) are drawn only for **buildings**
  with `staticSunShadowHeight > 0`. Pawns get a moving shadow (`HasSunShadows`). A tree gets only the
  small blob under its trunk from `graphicData.shadowData`. Oak: `volume (0.2, 0.35, 0.13)`. **So the
  player sees no tree shadow on the ground, at any sun angle.** This matters for §4.5.
- **What trees do carry:** `fillPercent 0.25` (cover from shots), `blockWind`,
  `passability PassThroughOnly`, `pathCost 42`, `plant.interferesWithRoof true` (no roof can be built
  over a tree), `plant.visualSizeRange` (oak `1.5~2.0`), and `treeCategory`.
- **Drawn size** is `Graphic.drawSize.x × visualSizeRange.LerpThroughRange(growth)` (`Plant.cs:863`,
  `:961`, `Blight.cs:182`). A seedling is drawn small and a mature tree large.
- **Leafless.** `Plant.LeaflessNow` exists: a tree drops its leaves in cold. On a tidally locked world
  that means only the cold tail of a biome.

### 1.2 What our shade grid already does with plants

`src/RimMandrake/CreatureBehaviors/Source/RM_MapComponent_ShadeGrid.cs` already treats big plants as
casters. That makes this pass an upgrade, not a new system.

- `Recompute()` runs every 2000 ticks (`RecomputeIntervalTicks`), or on request. It is a full-map scan
  (`map.AllCells`), not event-driven.
- **Roofs:** `roofShade = 1` under any roof, natural or built.
- **Casters:** `CasterHeight(cell)` returns:
  - for a building, `max(staticSunShadowHeight, fillPercent if ≥ 0.8)`;
  - for a plant with `visualSizeRange.max ≥ 1.5` (`ShadeCastingPlantVisualSize`), a height of
    `visualSizeRange.max × 0.5` (`PlantHeightPerVisualSize`).
- **Directional cast** (pinned sun, or the sun-heat extension's geometry): each caster throws a
  **one-cell-wide strip** down-sun of length `height × cot E`, capped at `MaxCastCells = 16`.
  `RM_SunHeatMath.CastInto` gives full shade along the body, easing to `ShadowTipShade 0.6` at the tip.
  **The caster's own cell is never shaded** ("a rock is not standing room").
- **Non-directional** (no sun vector): a radius-2 ring around any caster (`RingShadeAt`).
- **Moving casters** (`RM_MovingShadeLayer`, `RM_MovingShadeMath.CastBody`): a creature with
  `castShadeHeight` shades a square of `castShadeRadius` round its own cell (the overhead body) **plus**
  a directional strip from each cell of it. This is the same shape a tree crown needs (§3c), and it
  is already built and fuzzed offline.
- **Exposure** (`RM_SunHeatMath.Exposure`): `1 − max(roof, cast)`, and then gear cover. Under the
  ruled model (DS3) this becomes `max(roof, parasol, castShade)` at every E.
- **Not saved.** The component has no `ExposeData`. Every grid is derived and rebuilt on load.

**Three defects in today's plant handling**, all of which fall out of the ruled geometry:

1. **No crown.** A tree shades a one-cell strip, never the ground under its crown. At a high sun the
   strip is shorter than a cell. At E = 79° and h = 1 it is 0.19 cells, so **a forest under a high sun
   is unshaded today.** This is exactly the owner's worry, turned upside down.
2. **Growth is ignored.** It uses `visualSizeRange.max`, so a greatbole seedling (`12~16`) throws the
   capped 16-cell shadow of a mature giant.
3. **No tree is drawn with a shadow** (§1.1), so whatever the grid computes, the player cannot see it.

### 1.3 What Direct Sun's "covered" test reads under the ruled model (DS3)

Covered at every sun angle: any roof (built, a tent, overhead rock) and a parasol on its carrier. Cast
shade: structures, rock and big plants, down-sun, with length height / tan E. Enclosed rooms are never
exposed. Shade gear is only parasols and tents (`RM_ShadeTent` is a 3×3 roof structure). The Greentide's
living greatbole (`RM_GreatboleHeartwood`, placed by `RM_LivingBoleBiomeExtension`, radius 4–6) is
**rock under `RoofRockThick`**, so the ground inside it is already roofed and covered. The tree model
below is about the **open forest**: fellable trees, the `RM_Greatbole` among them.

## 2. Our tree-heavy biomes

### 2.1 How this was measured

- **Source:** the live def dump captured **2026-10-19T11:23:54Z** (542 active mods). `measure build`
  rebuilt `defs.sqlite` from it this pass: MEASURED 77754 defs, 145 BiomeDefs. Every BiomeDef
  `wildPlants` list is read **after patches**, so the `RUT_` twins' patch-added casts are included.
- **Caster:** today's rule, any plant whose `visualSizeRange.max ≥ 1.5`. The tree column is the vanilla
  tree test, `harvestTag == Wood`.
- **Def-expected caster-cell fraction** = `min(1, plantDensity) × (Σ commonality of casters / Σ
  commonality)`. This follows vanilla `GenStep_Plants`, which puts a plant on a plantable cell with a
  probability of about `plantDensity` and picks the species by commonality. It is an **upper bound on
  fertile ground**. Rock, water and low fertility lower it, and clustering (`wildClusterRadius`) does
  not change the mean.
- **Live tree-cell fraction on a generated map: UNMEASURED.** Method: generate one quicktest map per
  biome (bridge, ~90 s each), save it, and count cells holding a plant with `visualSizeRange.max ≥ 1.5`
  over the passable non-water cells with `src/RimMandrake/Utils/rimbench/savemap.py`. The def dump
  must be of the same mod set. That census is spec 1 of `TREE_SHADE_SELFTEST_PROVE_FOREST_IS_SHADE`, and
  its numbers replace the def-expected column.
- **Sun elevation E:** the median from each biome's sheet (`design/Jawa/worldbuilding/biomes/`): the
  Greentide +45°, the Fever Wood +43°, the Webwork +51° (arc 21–53), the Miasma +39° (arc 19–75, so
  E 15–71), the Contagion about +31°. The Rot, the Abyss and the Lantern Deeps are nightside, and the
  Cauldron and the Slime sit on the terminator (permanent twilight, E ≈ 0). Those five get **no Direct
  Sun** under DS1, so their canopy does not matter to it.
- **Shade fraction:** a seeded Monte-Carlo on a 200×200 grid, with casters placed at the def-expected
  density, species by commonality, and growth uniform in 0.3–1. The script is
  `design/RimMandrake/tree_shade_model_2026-10-19_estimate.py`. It is an estimate of the model, not a measurement
  of a map.

### 2.2 The table

Every number is an estimate except the first four columns, which are read from the defs.
"Today's strip, full shade" is the share of cells at full shade under today's code.
"Crown model, covered" is the share under the recommended model (§4) with the INVENTED crown factor 0.8.

| Biome | E (sheet) | plantDensity | Caster share of roster | **Def-expected caster cells** | Tallest casters (drawn max, cells) | Today's strip, full shade | Crown model, covered |
|---|---|---|---|---|---|---|---|
| `RM_Greentide` | +45° | 0.99 | 0.80 | **0.79** | `RM_Greatbole` 16, `RM_Veluthar` 11.5, `RM_Kaddrath` 11 | 0.91 | 0.99 |
| `RUT_Greentide` | +45° | 0.9 | 0.78 | **0.70** | `RM_JungleTree` 3.8 | 0.30 | 0.99 |
| `RM_Miasma` | +39° (15–71) | 0.7 | 0.64 | **0.45** | `RM_Nogtyl` 12, `RM_Thessamor` 6.5, `RM_Ollamane` 6.5 | 0.52 | 0.97 |
| `RUT_Miasma` | +39° | 0.7 | 1.00 | **0.70** | `RM_Nogtyl` 12, `RM_MangroveTree` 3.8 | 0.52 | 0.98 |
| `RM_FeverWood` | +43° | 0.7 | 0.56 | **0.39** | `RSW_Plant_HydenockTree_Wild` 12, `RM_CorriskTree` 11.5, `RM_Thulvane` 9.5 | 0.73 | 0.99 |
| `RUT_FeverWood` | +43° | 0.7 | 0.72 | **0.51** | `RM_KeeningCordax` 3 | 0.14 | 0.75 |
| `RM_Webwork` | +51° (37–69) | 0.9 | 0.39 | **0.35** | `RM_Kollavane` 7, `RM_Dulloth` 5.2 | 0.25 | 0.97 |
| `RUT_Webwork` | +51° | 0.9 | 0.71 | **0.64** | `RM_JungleTree` 3.8 | 0.28 | 0.99 |
| `RM_Contagion` | ~+31° | 0.35 | 0.54 | **0.19** | `RM_Eyebark` 6, `RM_HalfmadeTree` 4 | 0.29 | 0.76 |
| `RUT_Contagion` | ~+31° | 0.35 | 0.53 | **0.19** | `RM_AlienTree` 3.75 | 0.24 | 0.65 |
| `RM_TheForge` | +57° | 0.4 | 0.05 | 0.02 | `RM_FirevineTree` 3.8 | 0.00 | 0.11 |
| `RM_FloodedCanyon` (Cracked Lands) | +21° | 0.12 | 0.12 | 0.01 | `RM_CrackedThornwood` 4 | 0.05 | 0.06 |
| `RM_WeepingStones` | +31° | 0.4 | 0.03 | 0.01 | `RM_Rockfinger` 4.5 | 0.03 | 0.08 |
| `RM_Wastes` | ~+3° | 0.12 | 0.11 | 0.01 | `RM_VaultRoot` 5 | 0.16 | 0.03 |
| `RM_LongShade` | +14° | 0.05 | 0.08 | 0.004 | `RM_Shadespire` 4.5 | 0.01 | 0.01 |
| `RM_Stillsand` | +47° | 0.008 | 0.02 | 0.0003 | `RM_Ollim` 10.5 | 0.00 | 0.01 |
| `RM_LeaningScrub`, `RUT_AridShrubland`, `RM_TheScald` | day side | 0.3–0.35 | 0.05–0.13 | 0.02–0.04 | venomvine thickets 2.4, `RM_Vekkfan` 2 | not simulated | not simulated |
| `RM_Pyrelands`, `RM_Warscar`, `RM_BlueDesert`, `RM_TheSump` | day side | — | 0 | 0 | none | 0 | 0 |
| `RM_TheRot`, `RM_Abyss`, `RM_LanternDeeps` (nightside); `RM_Cauldron`, `RM_GelatinousSlime` (terminator) | E ≤ ~0 | 0.5–1 | 0.07–0.67 | 0.07–0.33 | `RM_AgariluxPrime` 20, `RM_TreeMushroom` 15.2 | no Direct Sun | no Direct Sun |

The full per-biome caster list (every caster, its drawn size, `treeCategory`, `harvestTag`,
passability) was printed from the same query. It is reproducible with the script above.

### 2.3 What the table says

- **Five day-side biomes are tree-heavy**: the Greentide, the Miasma, the Webwork, the Fever Wood and
  the Contagion, each with an `RM_` and a `RUT_` def. Their def-expected caster cells are 0.19–0.79.
  All five lie at E 31–51°.
- **Today's code is uneven across them, and for the wrong reason.** Where the roster has giants
  (`RM_Greentide` 0.91, `RM_FeverWood` 0.73), the one-cell strips are long enough to tile the floor,
  partly because the strip uses the giant's *maximum* size whatever its growth. Where the canopy is
  ordinary 3–4-cell trees (`RUT_Greentide` 0.30, `RUT_Webwork` 0.28, `RUT_FeverWood` 0.14), the floor
  is mostly sun. The same forest gets different shade depending on which twin is loaded. Under a
  higher sun every strip shortens, so the Webwork at the top of its range (69°) loses most of its shade.
- **The crown model makes every dense forest mostly shade** (0.97–0.99 covered in the Greentide, the
  Miasma, the Webwork and `RM_FeverWood`, 0.65–0.76 in the sparser Contagion and `RUT_FeverWood`),
  and it does so from geometry alone. That is the owner's "most tree-dense maps will be mostly shade",
  and the sheets' forests: the Webwork *"dim green gloom under total canopy; hard white blades of sun
  at clearings"*, and the Fever Wood's *"wood-roads twisting through a living crown"*. Sun then lives
  only in clearings, on causeways and water, and wherever the colony cuts. The 0.99 figures assume
  every tree is fully opaque and the crown factor is 0.8; both are §7 Q2 and tuning.
- **The giants.** `RM_Greatbole` (Greentide, drawn 12–16 cells, commonality 0.03, rare and solitary),
  `RM_Nogtyl` brommok timber (Miasma, 12), `RSW_Plant_HydenockTree_Wild` (Fever Wood, 12),
  `RM_CorriskTree` (Fever Wood, 11.5), `RM_Veluthar` and `RM_Kaddrath` (Greentide, 11–11.5). One mature
  greatbole crown under the model is a disc about 13 cells across, roughly 130 cells of shade.
- **Low-tree day-side biomes** (Forge, Cracked Lands, Weeping Stones, Wastes, Long Shade, Stillsand,
  Leaning Scrub, Pyrelands, Scarlands): under 2% caster cells, so canopy changes almost nothing there.
  Their shade stays structures, rock, roofs and parasols.
- The Fever Wood's and the Webwork's canopy trees carry `harvestTag Standard`, not `Wood`. A
  "trees only, by the vanilla tree test" rule would leave both shadeless. §7 Q4 asks about this.

## 3. Candidate models

All four keep the one ruled rule: **the same arithmetic on every map, with no biome field changing it.**
A tree's numbers come from its own ThingDef (drawn size, an optional crown extension), never from the
biome it stands in.

### (a) Per-tree projected shadow, rasterised and cached

Each tree is a **crown**, a disc of radius `r = k × drawnSize / 2` held up at crown height
`hc = drawnSize × 0.5` (today's height scale), on a trunk. The sun projects the crown onto the ground:
the disc is displaced down-sun by `hc × cot E`, and the trunk adds today's strip. The disc and strip are
rasterised into `castShade`, by max, as now.

- **Geometry:** high sun puts the crown's shadow straight under the tree. A low sun moves it down-sun
  and lengthens the trunk strip. This is the owner's "pure function of geometry" with nothing added: a
  tree is a parasol on a pole.
- **Cost:** per caster, πr² cells plus the strip. `RM_Greentide` at about 0.79 caster cells × 62,500
  cells (250²) is about 49,000 casters. Its roster is giant-heavy: a mature veluthar (drawn 11.5) has
  r ≈ 4.6, about 66 cells. So the worst case is of the order of 10⁶ float writes per recompute; the
  `RUT_` twins' 3–4-cell trees are 5–10 cells each. Estimate: under 10 ms per recompute, once per 2000
  ticks, so well under 0.01 ms per tick amortised. UNMEASURED until the selftest benchmark (§6, T5).
  If it is too slow, rasterise each species' disc once as a stamp and blit it.
- **Cache:** on a fixed-sun Utinni map the projection never moves, so the grid changes only when a
  tree, roof or building changes. The coarse 2000-tick recompute already covers growth. A felled or
  burned caster requests a recompute (`RequestRecompute`, the same hook gear uses), so a cleared
  opening shows sun on the next tick, not up to 33 s later.

### (b) Crown-cover density grid (no direction)

Shade = a blur of local caster density (for example the fraction of casters within radius 2, times a
canopy factor). There is no sun vector.

- **Cheapest** (one box blur), and smooth.
- **It breaks the ruled rule.** On the same map, buildings and rock cast down-sun and trees would
  not. At E = 14° (the Long Shade's sun) a tree's shade would sit under the tree while the wall next
  to it threw a four-height lee. It is a biome-shaped look-up, not geometry.
- **Useful only as a fallback for distant LOD,** which RimWorld does not need at these map sizes.

### (c) Trees as a roof-like canopy: full block overhead, shadow geometry under a low sun

The crown is treated as a roof when the sun is "overhead" and as a caster when it is low.

- **This needs a threshold** for "overhead". The ruling on 2026-10-19 deleted exactly that: no regime
  switch, no threshold T, no `KindFromElevation`.
- Read continuously, with no threshold, (c) **is** (a). The crown covers the ground under it at
  E = 90° and slides off down-sun as E falls. So (c) is kept as a description of (a)'s behaviour, not as
  a separate model.
- A literal roof (`RoofDef`) for canopy is ruled out separately. `interferesWithRoof` forbids roofs over
  trees, roofs change vanilla temperature and lighting, and roof collapse logic would run under every
  forest.

### (d) Direct Sun off on tree-heavy maps (the owner's inferior option)

- **Cheapest to build** (a gate), but **it reintroduces a per-biome or per-map exception**, which the
  ruling removed.
- If it is ever chosen, it should be keyed on **geometry, not biome**: Direct Sun is off on a map whose
  measured caster-cell fraction is above a threshold, for example 0.3. That keeps "no biome-specific
  sun" true in letter, but it is still a step function. A clearing in the Greentide would be as cool
  as the forest, and a Greentide map someone clear-cuts would stay sunless.
- It also loses gameplay the sheets want: the Webwork's *"hard white blades of sun at clearings"* and
  the Fever Wood's crown-versus-water frame both need a forest that is shaded where it stands and
  sunlit where it is cut.

### Comparison

| | (a) projected crown | (b) density | (c) canopy-as-roof | (d) off when tree-heavy |
|---|---|---|---|---|
| Obeys "pure function of geometry" | **yes** | no (no direction) | only if read as (a) | no (an exception) |
| Forest mostly shade, clearings sunlit | yes | yes, blurred | yes | no: all-or-nothing |
| Agrees with building and rock shadows on the same map | yes | no | yes | n/a |
| Per-recompute cost | a few ms (estimate) | under 1 ms | as (a) | none |
| Save compatibility | nothing saved; derived | same | same | a gate; nothing saved |
| Fixed sun (Utinni) | projection static; recompute on change | n/a | as (a) | n/a |
| Rotating sun (day/night world) | Direct Sun is off there (DS7); the projection would follow E if the clock option is ever built | n/a | needs a threshold | n/a |
| Readable sign | overlay, mouseover, ground tint (§4.5) | same | same | a letter line |
| Agent-days to build | ~3 | ~1.5 | ~3 | ~0.5 |

## 4. Recommended model: (a), the projected crown

### 4.1 The rule, stated once

A tree is a parasol on a pole. Its crown is a disc held at its crown height. The sun projects the disc
onto the ground down-sun by `crownHeight / tan E`, and the trunk casts today's strip. The ground under
the projection is shaded, and that shade enters Direct Sun's cover term like any other cast shade.
The same tree gives the same shade at the same E in every biome.

### 4.2 The numbers, per tree (from its ThingDef)

- **Drawn size** `s = Graphic.drawSize.x × visualSizeRange.LerpThroughRange(growth)`: what the
  player sees. This fixes defect 2 (growth).
- **Caster test:** `visualSizeRange.max ≥ 1.5`, as today, unless §7 Q4 rules otherwise.
- **Crown radius** `r = crownRadiusFactor × s / 2`, default factor 0.8 (the crown covers most of the
  sprite's width, less trunk and gaps).
- **Crown height** `hc = s × 0.5`, as today (`PlantHeightPerVisualSize`).
- **Crown opacity** `o`: default 1.0 (full shade). The alternative is dappled shade (§7 Q2).
- **Leafless:** while `Plant.LeaflessNow`, opacity × 0.3 (INVENTED).
- An optional `RM_TreeCrownExtension` (DefModExtension on the plant ThingDef) overrides `r`, `hc` and
  `o` for a species whose sprite misleads, such as a column with a raft on top (the greatbole) or a
  thin mast (`RM_Arpeau`). It is never on a BiomeDef.
- **Cap:** the projection offset and the strip share `MaxCastCells = 16`. At E = 2° a 16-cell giant's
  crown lands 16 cells away, not 230.

### 4.3 Where it plugs in

- `RM_MapComponent_ShadeGrid.Recompute`: `CasterHeight` returns the plant itself, and a new
  `CastCrown` rasterises the disc (reusing `RM_MovingShadeMath.CastBody`'s overhead-plus-strip shape,
  which is already fuzzed) into `castShade`.
- `RM_SunHeatMath`: a pure `CrownFootprint(cx, cz, r, hc, dir, cotE, cap)`, so the selftest can call it
  without the game.
- The non-directional ring path (`RingShadeAt`) gets the same disc with zero offset, so maps without a
  sun vector also show canopy shade for the shade-seeking animals that read the grid.
- A recompute is requested when a caster plant despawns (felled, burned, eaten, crushed).
- Nothing new is saved.

### 4.4 Fixed sun versus a rotating sun

- **Utinni (the shipped world):** time of day = location, so E and the sun's bearing are fixed per map
  (DS7). The projection never moves, the shadows are static, and the forest floor has the same shade
  map all game. That is the case the owner wrote about: "massive shade beneath them at a fixed
  angle".
- **A day/night world:** Direct Sun is off (DS7, the owner's allowed drop). The canopy grid still
  feeds shade-seeking animals through the non-directional disc. If the follow-the-clock option is
  ever built, the projection follows E at each recompute (every 2000 ticks is about 12° of sun), with
  no change to the model.

### 4.5 What the player sees (no shade without a readable sign)

Vanilla draws no tree shadow (§1.1), so the grid must be shown:

1. **A shade overlay toggle** in the bottom-right play-settings row, like vanilla's roof and fertility
   overlays (a `CellBoolDrawer`). It shades exactly the cells `ExposureAt` reads, from the same
   array, so what the player sees is what the pawn feels.
2. **Mouseover readout** (the lower-left cell readout): "Direct Sun: shaded (veluthar canopy)" or
   "Direct Sun: full sun, 39 °C felt". It names the cause: roof, canopy, a building's lee, a parasol.
3. **The sun-load gizmo line** (`RM_Gizmo_SunLoad`) already says what the sun adds where the pawn
   stands. It gains the cause word.
4. **Optional, needs the owner (§7 Q3):** a subtle always-on ground tint under canopy shade, drawn as a
   section layer with no new art. It makes a forest read as shaded at a glance. Rendered crown
   shadows that match the sun vector would be art and shader work, with more risk.

### 4.6 Mod Settings (superb settings rule)

These go in the existing Direct Sun group of `RM_CreatureBehaviorsMod`. Defaults equal the shipped
behaviour, and with everything off the game is vanilla.

- **Tree canopy shade** (on). Off: trees cast only today's trunk strip.
- **Canopy shade strength** (0–100%, default 100%): a multiplier on crown opacity.
- **Shade overlay button** (on): shows the toggle in the play-settings row.
- **Ground tint under canopy**: only if Q3 says yes.
- **No per-biome canopy switch** (owner, 2026-10-15: no new cross-biome switch).
- If (d) is ever chosen instead: **"Direct Sun under dense canopy"** (on), labelled with what it does.

### 4.7 Save compatibility

Nothing new is saved. The crown extension is def data. An existing save loads, the grid rebuilds on
the first recompute, and removing the feature leaves nothing behind.

## 5. Cost

| Piece | Agent-days |
|---|---|
| `CrownFootprint` math, `CastCrown`, growth-aware size, leafless factor, despawn recompute | 1.5 |
| Overlay toggle, mouseover readout, gizmo cause word | 1.0 |
| Settings and `RM_TreeCrownExtension` (plus overrides for the six giants) | 0.5 |
| Offline selftest and benchmark (`TREE_SHADE_SELFTEST_PROVE_FOREST_IS_SHADE`) | 1.0 |
| Live state reads, folded into `DIRECT_SUN_LIVE_VERIFY_ANGLE_NOT_BIOME` | 0.5 |
| **Total** | **about 4.5** (plus about 1 more if Q3 picks the ground tint) |

It builds on `DIRECT_SUN_UNIFY_GEOMETRY_ALONE_DECIDES`, since it uses the one E and the one cover rule.

## 6. The adopt-or-fall-back test: what "excellent" means

Adopt (a), and so run Direct Sun on every day-side map, only if **all** of these hold. If any of T1–T4
fails after one fix round, fall back to (d), keyed on the map's measured canopy fraction, not on the
biome.

- **T1, geometry (offline).** The same tree at the same E gives an identical footprint in every biome.
  At E = 90° the shade is the disc under the crown. At E = 14° the disc is offset by `hc × cot 14°`
  (capped at 16) and the trunk strip is about 4 × hc long. A seedling casts by its drawn size.
- **T2, forest is mostly shade (offline, then live).** On generated maps of the five tree-heavy
  biomes, the shaded share of open ground (unroofed, passable, non-water) is at least 60% in the
  Greentide and the Miasma. The live census (§2.1) must land within ±10 points of the §2.2 estimate.
  A 7×7 clearing cut in the middle shows full sun in its centre at E ≥ 30°.
- **T3, readable (live, owner-watched).** The overlay shows exactly the cells `ExposureAt` reads (the
  same array), the mouseover names the cause, and the owner can tell shade from sun at a glance on a
  Greentide map.
- **T4, responsive.** A felled or burned tree's shade is gone by the next tick (requested recompute),
  and a growing tree's shade grows with it.
- **T5, cheap.** `Recompute` on a 275×275 map at full Greentide density takes at most 15 ms
  (benchmark offline on a synthetic grid, then once live). That is under 0.01 ms per tick amortised.
- **T6, save-safe.** Loading a save made before the feature gives the same grid as a fresh map
  holding the same things.

## 7. Decisions the owner must make

- **Q1. Which model?**
  - (a) Projected crown (recommended): trees are parasols on poles, so forests are mostly shade and
    clearings are sunlit, all from geometry. About 4.5 agent-days.
  - (d) Direct Sun off on tree-heavy maps: about 0.5 days, but all-or-nothing, and it brings back an
    exception.
- **Q2. Full or dappled crown shade?**
  - Full (recommended): one number, and a forest is properly shaded.
  - Dappled, an opacity per species: richer, but every tree becomes a number to tune.
- **Q3. How does shade show?**
  - Overlay toggle plus mouseover (recommended, in the estimate).
  - Also a subtle always-on ground tint under canopy (about +1 day).
  - Also true rendered crown shadows (art and shader work, more risk).
- **Q4. Which plants are trees for shade?**
  - Anything drawn 1.5 cells or larger (today's rule): it includes giant mushrooms, thickets and
    pillars.
  - Only woody trees by the vanilla test: this would leave the Fever Wood and the Webwork shadeless,
    because their canopy trees are not tagged `Wood`.
  - A per-def crown extension list.
- **Still standing from the parent design:** the D5/D6 confirm (Direct Sun on the Scarlands, the
  Miasma and the `RUT_` twins, and sand glare keyed to sand terrain).

## 8. Ledger

- Filed: `TREE_SHADE_BUILD_CROWNS_ON_STILTS` (offline build, opus), `TREE_SHADE_SELFTEST_PROVE_FOREST_IS_SHADE`
  (offline selftest plus the live census in its spec), `TREE_SHADE_DECIDE_CROWNS_OR_LIGHTS_OUT` (needs
  owner: Q1–Q4).
- Noted on `DIRECT_SUN_UNIFY_GEOMETRY_ALONE_DECIDES`: the all-day-side rollout (DS8) is conditional on
  this model (owner's words above), and the D5/D6 confirm still stands.
