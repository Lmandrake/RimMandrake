# The Cracked Lands — flora expansion pitch (2026-10-02)

**Item:** `BEDAZZLE_FLORA_EXPANSION_1` (owner, 2026-09-29, typed on the art sheet: *"Need more
plant-like members of this biome"*). **Status:** pitch only. Nothing here is ruled, built or
queued for art. The owner rules on these rows at the biome's own sitting.
**Biome:** `RM_FloodedCanyon`, labelled "the Cracked Lands" (the rename is
`CRACKEDLANDS_FULL_RENAME_1`'s job).

## What already exists (read before inventing)

- **Live RM flora:** `RM_FloodedCanyon_Biome.xml` `<wildPlants>` holds one row,
  `RM_Veqma` 0.15 (the dowsing plant; it still uses a vanilla Bush placeholder texture).
- **Utinni patch** (`WildAnimals_CrackedLands.xml` Op 3) replaces that list with: `AB_HardyGrass`,
  `GRimMoss`, `RUT_TwistingThorngrass`, `RUT_TwistingThornweed`, `RUT_TwistingThornwood`,
  `AB_GargantuanLithops`, and `RM_Veqma`. Two of those are donor plants, and the three twisting
  thorns are also on the Cauldron's roster. So the biome has **no tree and no food plant of its
  own**.
- **`RUT_BloomCrop`** is already the flood-week boom-and-bust crop (§10b), and it is the flagship
  of the explosive-growth roster. None of these pitches competes with it.
- **Already pitched and not built:** `CRACKEDLANDS_THREE_HEIGHT_FLORA_1` has the red-brown
  **qirra mats** (open on clay a flood has just wetted) and the pale **talus clasps** (rooted on walls
  beside fossil rock). None of the pitches below grows on wetted open clay or on wall faces.
- **Laws that bind every pitch:**
  - Ban 2: no green outside the shade line. The enrichment pick goes further: *"Only the Veqma
    shows green."* So **none of these plants is green.** Each one gets its colour from somewhere
    else in the spectrum, which also answers the owner's 2026-09-29 ruling against uniform palettes.
  - §4: terrestrial-analog shapes are allowed, but nothing can be nameable. The owner just rejected a
    saguaro-like column as too Terran, so there are no columns, no cacti and no Earth trees here.
  - One biome, one home. Every pitch is new to this biome only.
- **Hooks that already exist:** `RM_MapComponent_RecedeAftermath.OnRecede(wetted)`, the survey
  component's hidden-water score (Veqma's tint reads it), `RM_FossilStrata`, the explosive-growth
  roster, and vanilla `CompGlower` on plants (Core `Plants_Cave.xml`, Glowstool). Core `Dye` is in
  `Plants_Special.xml` (1.6).

**Accent.** The biome's invented words are muttavaq, uttaqar, irqit, tarruq, veqma and qirra: a
doubled consonant, a hard *q*, and endings in -aq, -it or -ma. Qattora, qetta, saqqat and luttaq
are reserved batch-4h drafts, so I avoided them.

---

## 1. Nabbuq — the ink-bladder (FOOD)

- **Role:** food. This is the biome's first year-round staple, a contrast to the bloom crop's
  boom and bust.
- **Look:** a low clutch of glossy **indigo-violet** bladders, each about the size of a fist, half
  sunk in dark shade soil. Above them sits a crown of papery **lavender** bracts that rattle when dry.
  When a bladder is full it goes taut and shows ink-blue veins.
- **Where and how:** it grows only on shade-line soil and swells after each flood. It is the plant
  form of the water the Farmers dig for. A full bladder means water is stored underneath.
- **Harvest and yield:** a new raw-food item, *nabbuq bladder* (RawVegetable class, a moderate
  stack). A Farmer staple you can find in the wild. It could also be sown, since this is the one
  dryland biome with real soil.
- **Why here:** it is the plant that most directly says *"soil in the shade"* (§3), and the biome
  has no food plant of its own.
- **Mechanism and cost:** vanilla PlantDef fields, plus one new ThingDef for the raw food
  (`harvestedThingDef`, `sowTags`, `fertilityMin`). The shade-line law uses whatever Veqma ends up
  using (open question 3 on `CRACKEDLANDS_THREE_HEIGHT_FLORA_1`). Optional garnish: add it to the
  explosive-growth roster with a "Flush" top. **Cost: S.**
- **Collision:** 0 substring hits in `src/` and `design/`. It was renamed from *huvvaq*, which
  embedded the Greentide fish `RM_Uvva`, which is also a food item. The only near miss left is the
  4-letter label token "nabb", which is weak.

## 2. Ruqqal — the rope reed (MATERIAL)

- **Role:** material (textile).
- **Look:** a dense tuft of twisted **coral-salmon** stalks spiralling like wrung rope. Flood mud
  dries **chalk-white** in the spiral grooves, so the stalks look striped.
- **Where and how:** it grows in the *flood-cut channels* on the canyon floor, which the flood
  re-scours. The flood flattens it and it springs back. It never grows on the flats.
- **Harvest and yield:** a new textile stuff, *ruqqal fibre*. It is coarse and hard-wearing, with a
  moderate insulation stat, and it gives garments a coral tint. Devilstrand and Devilstrand cloth are
  the model.
- **Why here:** it ties to the flood's channel cutting (the muttavaq's trail and the Swale family),
  and the Farmers' clothes end up the colour of their canyon.
- **Mechanism and cost:** vanilla only, with `harvestedThingDef` pointing at a new
  `stuffProps`/Fabric ThingDef. Placement in the channels can start as plain shade-band commonality.
  Rooting it on exact channel terrain would need a small placement check. **Cost: S** (M if it is
  pinned to channel terrain).
- **Collision:** 0 substring hits, no defName, label or accent near-miss. "Rope reed" also scores 0.

## 3. Sevvuq — the sulfur globe (MATERIAL)

- **Role:** material (dye).
- **Look:** a cluster of brain-folded globes the size of a skull, coloured **saffron to sulfur
  yellow**, with tight ridges like coral. Old globes crack open and show a **burnt-orange** pith that
  stains anything it touches.
- **Where and how:** it grows on the flood *high-water line* in the shade. Each flood wets that band
  and then leaves it to dry, and the globes sit there at the tidemark.
- **Harvest and yield:** vanilla **Dye**. Every DLC is assumed, so Ideology dyeing works. It could
  optionally also drop a little raw plant matter.
- **Why here:** this biome is the only place on the planet that draws its own flood line, and the
  sevvuq marks that line in yellow. A player reads it as *"the water reaches here."*
- **Mechanism and cost:** vanilla PlantDef with `harvestedThingDef` set to `Dye`, so no new item is
  needed. To favour the high-water band, reuse the recede component's wetted-cell list as a seeding
  hint, or ship it as plain shade-band commonality. **Cost: S.**
- **Collision:** 0 substring hits, no near-miss. "Sulfur globe" also scores 0.

## 4. Zennaq — the copper broom (HAZARD)

- **Role:** hazard.
- **Look:** a waist-high explosion of stiff, wire-thin filaments that splay out like a frayed broom,
  **verdigris-copper** at the base and **burnished silver** at the tips. It hums faintly before dry
  lightning. It is not a column and has no trunk. It is a burst of wire.
- **Where and how:** it grows on mesa-tops and benches at the edge of the shade, where the
  Contagion's dry lightning lands (§4b; `DryThunderstorm` is 3 in the weather table). It **draws
  lightning strikes** and burns hot, so a stand next to a homestead is a fire risk. Cut it, or
  harvest it, before you build on that bench.
- **Harvest and yield:** cutting it gives a few *zennaq filaments*: a small conductive material
  item, or simply a few Steel/Silver units. That makes clearing it worthwhile.
- **Why here:** dry lightning off the ridge is this biome's own weather, and benches are where the
  structures must go (ban 8: never on the canyon floor). So the hazard sits exactly where the player
  has to build.
- **Mechanism and cost:** the PlantDef and its high flammability are vanilla. **Drawing strikes
  needs C#**: a Harmony postfix on the lightning target choice (`WeatherEvent_LightningStrike`) that
  biases the strike toward a zennaq within range. RimSage must confirm the exact method before
  anyone builds it. **Cost: M.** A fallback with no C# is just high flammability plus a description,
  which is S but turns it mostly into flavour.
- **Collision:** 0 substring hits, no near-miss. It was renamed from *zirraq*, which scored 0.73
  against **qirra**, a flora name already pitched for this biome. "Copper broom" scores 0.

## 5. Luqqim — the lantern cup (BEAUTY)

- **Role:** beauty.
- **Look:** clusters of translucent cups shaped like tulips, **magenta to amethyst**, with a
  **cyan** rim. Inside the deep slot-canyon dark they glow softly, magenta inside and cyan at the
  lip. In daylight they look like stained glass.
- **Where and how:** it grows in the *deepest slot shade*, where even the Veqma thins out. The glow
  makes the slots readable at night and lights the refuge ledges along the roads.
- **Harvest and yield:** cut, it gives a small amount of plant matter. The value is the Beauty it
  adds where it stands. Farmers leave it in place by their ledge stairs.
- **Why here:** the sheet's light law is *"the hardest contrast on the planet"* (§9), and this plant
  is colour inside the dark half of that contrast. It is the visual twin of the water chimes: the
  biome you hear in the stone, and the biome you see in the slot.
- **Mechanism and cost:** vanilla PlantDef with a Beauty statBase and `CompGlower` (Glowstool
  pattern, magenta `glowColor`), plus `cavePlant`-style low-glow growth so it stays in shade.
  **Cost: S.**
- **Collision:** 0 substring hits, no near-miss. "Lantern cup" scores 0.

## 6. Harrovaq — the bone tree (MATERIAL / wood)

- **Role:** material (wood). This is the biome's own *"occasional twisted tree"* (§4), so the
  biome no longer has to borrow the Cauldron's thornwood.
- **Look:** a low, wide tree that leans hard toward the canyon wall. The bark is **slate-blue** and
  the branches are **bone-white** and leafless, twisted in tight corkscrews. From the tips hang
  **burgundy** seed tassels. It is not an Earth tree: it has no canopy and no leaves.
- **Where and how:** it is rare and anchored in the shade at the foot of the canyon walls, with
  roots wedged into the talus. It survives floods by bending flat and righting itself afterwards.
  Old ones lean almost horizontal.
- **Harvest and yield:** wood (vanilla WoodLog), at a lower yield than a temperate tree. Wood is
  scarce on the dryland ladder, so a stand is a real resource.
- **Why here:** it is the vertical silhouette the sheet asks for (*"twisted trees against the sky"*,
  §9), and it is the only owned tree in the one dryland biome with soil.
- **Mechanism and cost:** vanilla tree PlantDef (`harvestTag Wood`, `harvestedThingDef WoodLog`,
  `blockAdjacentSow`). The leaning silhouette is art only. Unlike the talus clasp, it roots in floor
  soil beside a wall and not on the wall face, so the two do not overlap. **Cost: S.**
- **Collision:** 0 substring hits, no near-miss. It was renamed from *vossit* (label near-miss
  "voss", which is a JawaFactionRoster leader's name, and close to `RSW_Vosska`) and from
  *vettarq* (0.67 against the reserved draft *qetta*). "Bone tree" scores 0.

---

## Collision sweep — method and result

Script: `/tmp/claude-1000/-home-mandrake-rm-bench/54206aec-dbd7-405b-aae8-2f9e4a917f31/scratchpad/cl_flora_sweep.py`.
It is a throwaway script and was not committed. It walks every `.xml/.md/.json/.cs/.csv/.py/.txt/.html`
under `src/` and `design/` (this file excluded) and checks three things:

1. Each name and English label as a case-insensitive substring.
2. Near misses against all **7,101** XML defNames (prefix stripped, ratio ≥ 0.75) and **15,878**
   `<label>`/`<description>` words (ratio ≥ 0.8).
3. Near misses against the biome's own accent words (ratio ≥ 0.6).

- **Sanity probe:** `korrum` gives **132 hits in 48 files**, so the sweep can find things.
- **Final six:** 0 substring hits each. The near-miss results that remain are trivial: the label
  token "nabb" against nabbuq, and `rm_ladder`/"bladder" against the English label "inkbladder".
  That label is not used; the English label is "ink-bladder".
- **Rejected during the sweep:**

  | name | collided with | why it was rejected |
  |---|---|---|
  | huvvaq | `RM_Uvva` | Greentide fish, also a food |
  | ittaqa | sandpillar alternate-name draft | 0.77 against uttaqar |
  | zirraq | qirra (0.73) | same biome's flora |
  | vettarq | qetta (0.67) | reserved draft |
  | vossit | "Voss" / `RSW_Vosska` | |

## Card draft

1. **Ink-bladder:** a violet tuber in shade soil and the biome's first everyday food. The cost is
   that it competes with sown crops for the scarce shade soil.
2. **Rope reed:** a coral twisted reed in the flood channels that gives tough cloth. The flood
   flattens it, so harvests are lumpy.
3. **Sulfur globe:** yellow brain-globes that mark the flood's high-water line and give dye. They
   are useful but minor, mostly a sign that tells you where the water reaches.
4. **Copper broom:** a wire-bristle plant that attracts lightning to the building ledges. It is the
   best hazard, but it needs new code to work.
5. **Lantern cup:** magenta glowing cups in the darkest slots. They are pure beauty and cheap to
   build, but give almost no harvest.
6. **Bone tree:** a leaning, leafless slate-and-bone tree and the biome's own wood. It is rare and
   slow-growing, so it gives little wood per tree.
