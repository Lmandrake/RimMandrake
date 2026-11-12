# Mineral x Baroque Biome matrix: design pass, 2026-10-28

## Inputs

**Data:**
- The def dump of 2026-10-28T22-17-04Z (game 1.6.4871). MEASURED: its 321 mods match the live ModsConfig, in the same order.
- The 10-03 registry design and its CSV.
- The 10-02 forms design (F1-F13).
- canon_materials section 0.
- The item history of MINERALS_WHERE_THEY_BELONG_1.
- Lessons and rulings: lessons.md.

**Files in this folder:**
- inventory.csv: 58 materials and 37 biome rows.
- draft_matrix.csv: 36 biome rows and 4 source rows, by 72 columns.
- reasons.csv: one row per nonzero cell.

**Generator:** the files are produced by a scratch script (gen_matrix.py). The values are a design draft, PROVISIONAL, and not owner-ruled.

## 1. Sheet structure

### Rows

**Biome rows (36):**
- the 28 RM_ Baroque Biomes, including the Lantern Deeps cave layer;
- the 4 seabed dive floors;
- 4 RUT land biomes: AridShrubland, Desert, ExtremeDesert, and Umbra (which stands for Fuel Snows; RUT_FuelSnows is absent from the 10-28 dump);
- one OTHER_vanilla row. Unregistered biomes keep vanilla behaviour (owner card, 10-03).

There are no tile counts anywhere. A biome on zero tiles is not a defect.

**Source rows (4).** These are where off-planet materials come from:

| Row | Unit |
|---|---|
| SRC_salvage_UPY | units offered per year |
| SRC_trade_UPY | units offered per year |
| SRC_meteorite_pct | share of a meteorite's metal |
| SRC_asteroid_map_DPM | deposits per Odyssey asteroid map |

### Column blocks

Each block has one unit throughout.

| Block | Cell meaning | What the player sees |
|---|---|---|
| Planet minerals (32 columns, steel ... bezoars) | **deposits per standard map** | lumps lying around, veins in the rock, and the local pool for the canal and quarry |
| DEEP_* (16) | % of deep-scanner finds; iron is the remainder | deep drill (Q3.4: iron everywhere, the rest only by home) |
| RIVER_* (2) | placer deposits per map | sluice box and panning (the rivers-carry card, 10-03) |
| OFF_* (14) | always 0 on biome rows; filled only on SRC rows | salvage, trade, meteorite, asteroid |

### Extra fields per biome

- mtn_pct_min and mtn_pct_max: section 5.
- hilliness_allowed.
- has_iron.
- signature_minerals_unique_here: computed.
- non_mineral_pull: flora, fauna or salvage that makes the biome worth visiting.
- mountain_reason.

### reasons.csv, per nonzero cell

- **Value and unit.**
- **Form**, an F-code from 10-02: F1 common vein, F2 biome vein, F3 nodule, F4 crystal, F5 crust, F6 vent, F7 organism, F8 sieve, F9 stratum, F10 salvage, F11 deep, F12 custom location.
- **Channels:**
  - S: lying on the surface;
  - V: vein in rock;
  - C: canal-dig and quarry draw;
  - D: deep drill;
  - P: placer.
- **Provenance:** RULED, BUILT, PROMISED with a document line, or PROPOSED-this-pass.
- **A one-line lore reason.**

### inventory.csv, per material

- defNames and mod.
- MEASURED, PROMISED_NO_DEF or INACTIVE status.
- Market value.
- Vanilla deep and scatter weights.
- **units_per_deposit, MEASURED from lump size times yield.** The 10-03 "1 lump = 1,200 units" held only for steel.
- Rarity tier.
- Sheet block.
- Lore source.
- Home.

### How the five questions map onto the sheet

1. **What lies around on the mountains?** The S and V planet cells. The surface placer (R3, RM_MineralSurface.cs) and the vein scatter read them.
2. **What does canal digging bring up?** A draw from the row's planet cells, weighted by deposits x units_per_deposit. Cuts at D>=3 also draw from the row's DEEP block. A row with no minerals gives local rock chunks (owner card, 10-03). The quarry uses the same draw, so a separate column would only duplicate the planet cells.
3. **What does the deep drill bring up?** The DEEP block.
4. **What do the rivers carry?** The RIVER block. This is the registry column that RM_PlacerDraw has been waiting for.
5. **Where does the rest come from?** The SRC rows.

## 2. The cell unit

**Proposal: deposits per map (DPM).** A deposit is one find: a vein lump, a nodule cluster, a crust patch, a crystal cluster or a seam. A map is a standard 250 x 250 map of that biome at its usual hilliness.

**Ladder for hand-tuning:**

| Value | Meaning |
|---|---|
| 0 | none |
| 0.03 | one map in 30 |
| 0.1 | one map in 10 |
| 0.3 | one map in 3 |
| 1 | one per map |
| 2-5 | a few |
| 10-25 | common, steel-like |
| 99 | terrain-scale, unlimited (sand, blue ice, lanternstone walls) |

Any number in between is valid.

### Comparison of units

| Unit | Example: gold on the Scald floor | Readable on a phone | Checkable by looking at a map | Converts to the engine | Weakness |
|---|---|---|---|---|---|
| **Deposits per map** (proposed; the owner's own settings unit, card 10-03) | 5 | yes | yes: count the lumps | EPM = DPM x units_per_deposit; scatter weight = DPM / expected lumps at the biome's hilliness | a deposit means different amounts for different minerals (shown in inventory) |
| EPM, units per map (the 10-03 storage unit) | 1,000 | poor (thousands) | no: you would have to sum stacks | direct | no one can reason about 34,000 vs 13,600 |
| Abundance class 0-5 | 4 | very | no | needs a table per class | coarse; hides 10x differences |
| Per 1,000 rock cells | 0.3 | no | no | direct | breaks for nodules and seabeds with no rock |
| Share % (used only for DEEP) | — | yes | no | direct for weighted draws | relative only; fine for the deep draw, where iron fills the rest |

EPM stays the storage unit in RM_MineralPolicy, so no code changes. The generator multiplies by units_per_deposit.

The **rarity tiers** map onto the ladder:

| Tier | Meaning | DPM in home |
|---|---|---|
| T0 | ubiquitous or terrain | 10-25, or 99 |
| T1 | common in its home | 2-5 |
| T2 | regional | 1-4 |
| T3 | rare signature | 0.5-5, home only |
| T4 | relic | 0.03-0.3 |
| X | never on the planet | — |

## 3. The orthogonalization rule

These rules are applied in draft_matrix.csv.

1. **One home per mineral.** A land home may share its mineral with its own dive floor or cave layer (Grey Sea with Grey Sea floor). A second home needs a written lore reason and at most half the primary's value. The draft has 31 non-steel planet minerals:
   - 23 have exactly one home;
   - the 8 that have two:
     - gold and silver: Blue Desert meteoritic plus Scald floor;
     - uranium: Wastes plus Scald floor;
     - obsidian: Forge plus Chill crater glass;
     - pyrinth: Deeps plus Scald floor (minor);
     - salts: the Grey Sea and its own floor;
     - sand: Stillsand plus ExtremeDesert, as ruled;
     - helixien: Chill crater plus Umbra.
2. **Steel is the only broadly present metal.** 13 rows have no iron: the seas and sea floors, the Stillsand dunes, the Greentide and Miasma silts, the Slime, the Sump tar, and the Lantern Deeps.
3. **The home holds across every channel.** Q3.1 ("ONLY in their home biomes") binds the surface, vein, canal, deep and river channels alike. The only channel free of homes is meteorites, and it carries metals and space ores only (card, 10-25).
4. **Off-planet materials are 0 in every biome cell:**
   - components, advanced components, plasteel, durasteel;
   - duranium, doonium, beskar;
   - cortosis, rhydonium, spice;
   - coaxium, phrik, gravitonium, tibanna.

   Their sources are the SRC rows.
5. **Organism materials are not cells.** Vexxith, gallium, char-lace, biosilica, glass pearl, ossrith crystal and glower crust belong to their flora or fauna. They appear only as a biome's non_mineral_pull, so the sheet does not double-count them. Brine plate and bezoars stay as cells because they are existing registry rows that lie loose.

**Sparsity achieved:** 35 of 1,116 non-steel planet cells are nonzero (3.1%). By comparison, vanilla effectively puts every scatter ore in every rocky biome.

Biomes with **no mineral and no other pull (15):**
- Abyss, Fever Wood, Slime, Greentide, Leaning Scrub, Long Shade, Miasma, Pyrelands, Rot, Webwork;
- the Scald and Twilight Sea surfaces;
- the Twilight and Chill floors;
- Arid Shrubland.

Their pull is climate, flora or fauna. Decision D4 covers them.

## 4. Balance logic

**Value per map in a home** (expected value = DPM x units_per_deposit x market value), to compare across homes:

| Material and home | DPM | Calculation | Silver per map |
|---|---|---|---|
| Steel, typical rocky biome | 10 | 10 x 1,400 x 1.9 | about 26,600 |
| Gold, Scald floor | 5 | 5 x 200 x 10 | about 10,000 |
| Uranium, Wastes | 3 | 3 x 360 x 6 | about 6,500 |
| Jade, Weeping Stones | 4 | 4 x 200 x 5 | about 4,000 |
| Ruby, Forge | 2 | 2 x 80 x 6 | about 960 |

Gems are cheap per map in silver, but they are the only source of their colour of art and jewellery, which is what pulls the player there.

**Must-visit pressure.** Every high-value or recipe-critical home is a place you have to travel to:
- The Lantern Deeps (diamond, pyrinth, kyber, stygium, mindstone) open only under maps at or below -40 C.
- The Scald floor needs a dive.
- Zersium needs the Forge.

That is the design: a home is a destination. It is safe only because of the next rule.

**No soft-locks.** Every material a recipe requires must have at least one route that needs no travel to its home: trade or salvage. The SRC rows give one for gold, silver, uranium, jade, the three gems, pyrinth and steel.

Materials that are home-only, with no trade route in the draft:
- zersium (Forge);
- phrikite (Stillsand; phrik itself is traded);
- kyber and stygium (Deeps);
- live pattern metal, dead smartsteel, deepchem and helixien.

**OWED (UNMEASURED):** a recipe-reachability check over the dump. For every RecipeDef ingredient and costList entry, it must find either a source with a nonzero cell in a biome painted on the world, or an SRC route. I did not run it. Until it runs, the zero trade values for those materials are provisional. Kyber and stygium are probably fine because they are rewards, not inputs to basic tools; zersium is the one to watch, since durasteel and the zersium rifle depend on it.

**Hilliness and veins.** V-form deposits need mountain cells. A biome whose maximum mountain share is 5% or less (the dunes, swamps and seas) carries only S-forms in the draft: nodules, crusts and sieve terrain. A lint (section 5) should flag any V-form cell above the biome's mountain capacity.

**Settings.** The existing veinMultiplier and per-row overrides (deposits on screen, EPM stored) remain the player's knobs. This sheet sets the defaults.

## 5. Min/max %mountainous per biome

**Definition:** the share of a biome's world tiles whose hilliness is Mountainous or Impassable (enum values 4-5 of the world grid's tileHilliness). hilliness_allowed adds the set of hilliness classes a tile of that biome may have.

The values are in draft_matrix.csv. The seas are 0/0; the Forge is 60-100; the Weeping Stones are 30-70; the Contagion is 30-60 (a valley under its peaks); the Sump is 0-2. The Lantern Deeps and the dive floors have no band because they are not painted tiles.

**Enforcement must not be worldgen.** BiomeDef has no hilliness field (MEASURED: its only related fields are extraRockTypes, forceRockTypes, hasBedrock and wildPlantsAreCavePlants). The game will never enforce these bands. Hilliness is design data in the hand-made world: the bundle's hilliness column, written by jawa/world_tile_import and the world/*_mountains_plan.json files.

So the enforcement is an **author-time lint**:
- It reads the frozen world bundle's biome and hilliness columns, or the live world through the read-only jawa/world_* tools.
- **Hard rule:** every tile's class must be in hilliness_allowed.
- **Soft rule:** each biome's share must sit inside its band, reported as a warning.
- It cannot alter tiles. A human fixes a tile by hand or through the mountain plan.
- A biome on zero tiles is SKIPPED, never failed.
- It runs at the paint-once step (BIOME_PAINT_ONCE_AT_THE_END_1) and as a selftest over the committed bundle.

It never generates or rerolls anything.

## 6. Shipping path (for the builder, after the owner rules)

1. Fold this sheet into design/RimMandrake/mineral_abundance_registry_2026-10-03.csv, or a successor CSV, as follows:
   - planet cells become EPM = DPM x units_per_deposit;
   - add a rivers-carry column and a deep-share column;
   - mark rows PROVISIONAL, which ships.

   GUESS blocked shipping before (lessons.md).
2. Extend R2 zeroing to the vanilla scatter and deep weights of gold, silver, uranium, jade and the gems outside their homes. Zero the deep weights of Gravitonium and RSW_ResourceBlueCrystal everywhere except their homes.
3. Swap the provisional pools in RM_DigDiscovery and RM_PlacerDraw to the registry draw (FLOWWORKS_QUARRY_DIGGING_1; BENCH owns FlowWorks).
4. Write the hilliness lint and the recipe-reachability check.

**UNMEASURED inputs the builder must measure first:**
- deposit sizes for obsidian, zersium, phrikite and pyrinth;
- the vanilla deep-lump count per map;
- the recipe ingredients of the T3/T4 materials.

## 7. Owner DECISIONS

Each decision has options and a recommendation (marked "Rec.").

**D1. Cell unit.**
- A. Deposits per map with the ladder above. You can count it on a map, and it is your own settings unit. **Rec.**
- B. EPM, units per map: exact, but not human-tunable.
- C. Abundance class 0-5: simplest, but too coarse to tell rare from very rare.
- D. Per 1,000 rock cells: fails for nodules and seabeds.

**D2. Steel level in rocky biomes.**
- A. About 10 deposits: roughly 40% of a vanilla large-hills map. Salvage (2,000 a year) and trade fill the gap, which fits the salvage-route loop. **Rec.**
- B. 15: gentler on early-game building.
- C. Vanilla, about 24: steel stops being a pressure.
- D. 5: harsh. It makes the Rust Cathedral and Warscar slag the steel destinations.

**D3. How sparse.**
- A. One home per mineral, plus its own floor or cave layer, as drafted (3.1% fill). **Rec.**
- B. A home plus one minor second biome per mineral. More forgiving, but blurs "must visit".
- C. Strict for precious minerals and gems, looser for commons (salts, obsidian, sand).

**D4. The 15 biomes with no mineral and no other pull.**
- A. Leave them. Their pull is climate, flora and fauna, and not every biome needs ore. **Rec.**
- B. Give each one an existing mineral with lore. For example, Long Shade silver ridges or Pyrelands fire-cracked obsidian. This costs orthogonality.
- C. Design new biome-native minerals. That needs defs, art and a later pass.

**D5. Review medium.** You are often on a browser or phone.
- A. A phone HTML sheet through the existing gated sheet server (src/RimMandrake/Utils/art/serve_gated.py; the 10-03 numbers sheet used it). One card per biome, with steppers on the ladder, pre-filled defaults, the reason under each cell, and an "accept all defaults" button. Decisions save as JSON, and no Excel is needed. **Rec.**
- B. A Google Sheet: familiar and good on a desktop, but needs an account bridge and is clumsy on a phone.
- C. An .xlsx on D:\ClaudeWork: true Excel, but desktop only.
- D. The raw CSV: no tooling, but unreadable on a phone.

The 10-03 sheet stalled at 37 pending rows. A should therefore open with the 48 cells marked PROPOSED-this-pass (MEASURED in reasons.csv), rather than all 1,100. It must pass the prereview gate before it reaches you.

**D6. Enforcing the %mountainous band.**
- A. An author-time lint: a hard rule that each tile's hilliness class is allowed, and a soft warning for each biome's share band. **Rec.**
- B. A share-band report only.
- C. No tooling; check by hand when painting.

There is no runtime or worldgen option, by ruling.

**D7. Phrikite home** (an open question since 10-10).
- A. The Stillsand, as BUILT. The dune sea becomes the desert-alloys place (glass sand plus phrikite). **Rec.**
- B. RUT_ExtremeDesert, which puts both transparisteel sand and phrikite in one Jawa desert.
- C. The Blue Desert.

**D8. Jade home.**
- A. The Weeping Stones: stone country, which gains a must-visit reason, with river cobbles there. **Rec.**
- B. The Cracked Lands, as in the 10-02 proposal.
- C. Both, at half each.

**D9. Meteorites.** This settles MINERAL_ROW_METEORITIC_DECIDE_FLAG.
- A. Steel, silver, gold, uranium and doonium ore only. Zersium and phrikite stay home-only. **Rec.**
- B. Add zersium and phrikite, as the 10-03 flags had it. This leaks two signature metals planet-wide.

**D10. Ship before review?**
- A. Ship the draft as PROVISIONAL defaults now, and treat the sheet as tuning. This gets Q3.1 enforced at runtime at last. **Rec.**
- B. Hold until you have reviewed it. This is what left Q3.1 unenforced for three weeks.
