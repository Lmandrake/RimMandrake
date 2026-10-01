# Review request: Pyrelands north-star checklist (you are the owner's proxy reviewer)

You are reviewing, ON THE OWNER'S BEHALF, the north-star checklist for "the Pyrelands", a fire-ecology
desert biome in a RimWorld 1.6 mod (all five DLCs always present). The owner was asked to validate
these bars and replied, verbatim: "Use gpt to review instead." Your review stands in for his read.
Once validated, every `must show` line becomes a binding bar: the mod is refused until an automated
test component claims it and a screenshot judge (an LLM looking at an in-game image) answers YES to
the line's prose. A `cannot show` line is judged with opposite polarity: a YES means the mod is red.

Context the checklist author was bound by (owner rulings — do not argue against these):
- A bar is one observable, falsifiable sentence a PLAYER could check on a freshly generated Pyrelands
  map in ordinary play. It must be free of implementation detail (no code names, no def fields).
- The biome is extreme overhead-sun heat (~50–55 °C). Heat is vanilla heat only; no biome-specific
  heat bar exists until a planned planet-wide solar-heat mechanic lands — do NOT ask for one.
- The world map tile count of the biome is irrelevant (the planet is painted once at the end). Never a bar.
- The wild-animal roster is 15 kinds, all invented/fire-ecology creatures; vanilla Earth animals
  (hare, rat, gazelle …) appearing is a FAIL. The flora roster is exactly ember grass, quick grass and
  fire-born scorch-fruit.
- Flight of the fire-hawk must never be proved by watching it fly; behaviour bars are proven by
  state reads. The bar prose may still describe what a player sees.
- No animal or pawn ever vanishes without a readable sign.
- Two bars (plant and animal distribution) were validated by the owner himself on 2026-09-17; keep
  their intent.

## The checklist under review (the full `## north star` section)

```markdown
## north star
state: DRAFT
validated-hash:

Owner, 2026-09-17 (verbatim): *"Any wrong animals present? Btw these are two
validation script bars you should add for pyrelands. Correct animal and plant
distributions."* The remaining bars are distilled from the owner-ruled biome
sheet and the shipped mechanics; each is one thing a player can check on a
freshly generated Pyrelands map in ordinary play.

### must show

**The biome's own populations**
- [ ] `pyre_plant_distribution_correct` — every wild plant on a fresh Pyrelands
      map is one of the biome's own species (ember grass, quick grass, and
      scorch-fruit where fire has passed); no other mod's grasses, trees,
      bushes or fungi grow there.
- [ ] `pyre_animal_distribution_correct` — every wild animal on a fresh
      Pyrelands map belongs to the biome's fire-ecology cast; no foreign kind
      wanders in, and the small common grazers outnumber the big predators.
- [ ] `pyre_mapgen_log_clean` — generating a Pyrelands map raises no red error
      about its animals or plants; the only errors allowed are the known,
      documented scorchable-ground config warnings.

**The fire ecology**
- [ ] `pyre_ground_ash_ladder` — the ground is the biome's own scorchable soil,
      sand and gravel, and burned ground darkens through visible ash stages
      (trace, light, heavy, deep) as it burns again, never stock desert ground.
- [ ] `pyre_grass_chokes_ground` — unburned soil is carpeted densely in grass;
      there are no bare-dirt expanses where grass should carry the ground.
- [ ] `pyre_embergrass_regrows` — a burned patch visibly re-greens within days
      at the biome's own heat, so the burn-and-regrow cycle is readable in
      ordinary play.
- [ ] `pyre_burn_line_present` — somewhere on the map a standing line of fire
      is burning, and over the following days it moves across the land.
- [ ] `pyre_scorchfruit_fire_born` — scorch-fruit sprouts in freshly burned
      ground after a fire passes, and does not appear as ordinary wild growth
      on unburned land.
- [ ] `pyre_scorchfruit_produces` — a ripe scorch-fruit plant yields fruit a
      colonist can harvest and eat to fill hunger.
- [ ] `pyre_scorchfruit_spoils_fast` — that fruit rots within days once picked,
      and an unpicked fruit plant withers faster still, so it cannot be
      stockpiled and carried out of the biome.
- [ ] `pyre_ruins_scorched` — ruins on a fresh Pyrelands map stand blackened
      and fire-scarred, not pristine.
- [ ] `pyre_fulgurite_after_lightning` — dry lightning striking sandy ground
      sometimes leaves a lump of fulgurite glass where it hit.

**The fire cast at work**
- [ ] `pyre_firehawk_carries_ember` — a fire-hawk picks up a burning twig and
      a new fire starts where it drops it, ahead of the existing blaze.
- [ ] `pyre_furnacebeast_warmth` — a pawn standing in the open near a
      furnace-beast shows a warmth effect on its health tab that ends once it
      walks away, and a furnace-beast kept in an enclosed room heats that room.
- [ ] `pyre_burrowers_dive` — when fire nears a burrowing grazer it goes to
      ground, shows a readable burrowed status, and the fire passes over it
      unharmed; the same animal caught above ground burns like any other.

**The weather**
- [ ] `pyre_ashfall_darkens_drifts` — ash fall dims the map and lays visible
      loose-ash drifts that keep accumulating while it lasts.
- [ ] `pyre_cinderfall_distinct` — cinderfall is recognisable at a glance as
      its own weather, not ash fall renamed.
- [ ] `pyre_blackrain_reads` — black rain falls visibly dark, plainly
      different from ordinary blue-grey rain.

### cannot show
- [ ] `pyre_cannot_vanilla_fauna` — a hare, rat, gazelle or any other
      Earth-animal placeholder living wild on a Pyrelands map.
- [ ] `pyre_cannot_ordinary_rain` — ordinary rain falling on a Pyrelands map;
      its only wet weather is black rain.
```

## The test plan's bar table (how each original bar is planned to be tested)

### 2.2 The ten bars

| # | bar id | kind | assertion and route | PASS predicate | how it could false-pass / false-fail |
|---|---|---|---|---|---|
| 1 | `pyre_plant_distribution_correct` | L+V | On each fresh site, before any tick, census every `Plant`-category thing with `jawa/list_things` (`ThingRequestGroup` Plant, whole map, read `isCompleteList`). Take the allowed set from `jawa/get_def RM_Pyrelands` `wildPlants`, read back at run time, plus ScorchFruit. | **Hard:** foreign plant defs = 0 on all 3 sites. Total plants ≥ 0.85 × plantable cells (bar 4 shares the same census). ⚖ EmberGrass:Quickgrass ratio within 2× of 9.0:3.8 (≈2.4). | **False pass:** an empty or partial list (`isCompleteList` false, or `scanned` = 0). It must also be shown able to see a foreign plant: as a sanity probe, spawn one vanilla `Plant_Grass` and confirm it is counted, then destroy it. **False fail:** neighbour-biome bleed. The tier excludes `biometransitions`, but tile mutators still apply (MixedBiome hands patches to a secondary biome), so mutators must be stripped (§3.4). Edge band: report the four quadrants separately. |
| 2 | `pyre_animal_distribution_correct` | L+V | Same sites, at tick 0 after mapgen: census of factionless pawns with `jawa/list_pawns`. Take the allowed set from live `get_def … wildAnimals` keys. | **Hard:** foreign kinds = 0. Every live wildAnimals key resolves (no null `animal`). ≥ 12 wild animals per site. ⚖ Pooled over 3 sites: ≥ 7 distinct roster kinds seen, `RSW_Gizka` in the top 3 by count (ECOSYSTEM_PYRAMID_LAW_1, "grain = most-seen"), and Spearman ρ(commonality, count) ≥ 0.4. Report ρ, and gate on it only once ⚖ is ruled. | **False pass:** the census reads the colonists' faction or the quest pawns. Filter `faction == null && RaceProps.Animal`. **False fail:** a manhunter or visitor incident during the settle ticks. Disable the storyteller (§3.8). Big species are rare by design, so per-kind presence is never hard. |
| 3 | `pyre_ground_ash_ladder` | L+V | (a) Gen-time terrain census with `jawa/get_terrain_batch`, whole map: the RM_FE ground family is present, and Ash Trace/Light/Heavy are present from the patchmaker. (b) **Burn-down:** on a 20×20 grassed `RM_FE_Ground_Soil` patch, fire → wait for out → regrow → fire, 3 cycles. | **Hard:** (a) stock `Sand`/`Soil`/`Gravel` = 0 cells, RM_FE_Ground_* ≥ 60% of land cells, and at least 2 of the 3 ash rungs present. (b) After cycle 1, ≥ 50% of patch cells are on an ash rung. After cycle 3, ≥ 1 cell is `RM_FE_Ash_Deep`. The screenshot shows the gradient. | **False fail (seen 2026-09-13):** the old suite burned **bare sand with no fuel**. A fire with no fuel goes out and `TryBurnFloor` never fires. Burn **grass on ground**. **False pass:** none of note. |
| 4 | `pyre_grass_chokes_ground` | L+V | Shares bar 1's census. Plantable cells are land cells with fertility > 0, not water, not `RM_FE_Ash_Deep`, unroofed and not under a building. | **Hard:** covered/plantable ≥ 0.85 on every site (the def predicts ~0.96). Judge YES on "the ground is carpeted in grass with no bare-dirt expanses". | **False fail:** sampling after a burn. Census at tick 0. Map Designer is absent from the tier, but if it is present `RM_PyrelandsDensityEnforcer` must have run: read back `plantDensity` = 16 via get_def. |
| 5 | `pyre_embergrass_regrows` | L+V | Clear a 30×30 grassed patch by fire, record the plant count (≈0), then tick. | ⚖ Plant count in the patch ≥ 25% of its pre-burn count by **day 3** and ≥ 60% by **day 7** (`wildPlantRegrowDays` 9, `growDays` 0.8). | **False fail: TEMPERATURE.** Vanilla plant growth factor falls to 0 at about 58 °C and is about 0.3 near 54 °C (**UNMEASURED** for these defs, so read `PlantUtility` through RimSage before the run). The test runs at the **campaign-representative** temperature (§3.5). If grass does not regrow there, that is a **real finding about the shipped world**, never a reason to cool the test tile. Also run one control site at 30 °C so a temperature failure can be told apart from a spawner failure. |
| 6 | `pyre_scorchfruit_produces` | L+V | Spawn `RM_FE_Plant_ScorchFruit` (n = 10) at growth 1.0 with `jawa/set_plants`, designate harvest, and let 1 colonist work. | **Hard:** ≥ 1 `RM_FE_ScorchFruitYield` exists after harvest. When ordered to ingest one, the colonist's food need rises. Also prove the fire route (n ≥ 1 ScorchFruit spawned by a burn within 11,600 ticks, per the old suite, which passed). | **False fail:** at 53 °C the colonist gets heatstroke or an unrelated mental break. Give colonists heat-proof apparel, or time-box the run. The plant **rots in 1.1 days on the stalk** (`daysToRotStart` 1.1): spawn and harvest inside one day. |
| 7 | `pyre_scorchfruit_spoils_fast` | O+L | [O] `RM_FE_ScorchFruitYield` has `daysToRotStart` **4** and the plant has **1.1** (MEASURED from XML), so the plant is faster, as the bar says. [L] Spawn a yield stack outside, unrefrigerated, and tick. | **Hard:** the yield is rotted or destroyed by day 4.5. An unharvested plant is destroyed by day 1.5. | **False pass:** heat accelerates rot in vanilla, so at 53 °C it spoils even faster. That is fine, because the bar is "within days". **False fail:** spawning it inside a cooled room or a stockpile. |
| 8 | `pyre_ashfall_darkens_drifts` | L+V | `jawa/weather_set RM_FE_Weather_AshFall lockWeather`, settle for the weather transition (§3.6), then count `RM_FE_Filth_LooseAsh` over the **whole map** at t = 0, 2500, 5000 and 7500 ticks. Take a luminance screenshot pair: Clear versus AshFall, same camera, same hour. | **Hard:** the ash count increases monotonically and is ≥ 20 at 7500 ticks. Mean frame luminance under AshFall ≤ 0.85 × Clear. Judge YES on "visible ash drifts". | **False fail (seen 2026-09-13):** counting inside a 24×24 rect. Deposits land on `CellFinder.RandomCell(map)` across the whole map, so a 576-cell rect on a 62,500-cell map expects ≈0 hits. Roofed or water cells are skipped. **False pass:** a pre-existing fire dusting ash. No fires may burn during this step. |
| 9 | `pyre_cinderfall_distinct` | D+V | [D] Cinderfall's def differs from AshFall in at least one of: overlay classes, `skyColors*`, particle mote. [V] Screenshot pair AshFall vs Cinderfall under the same conditions. | **Hard:** [D] at least one rendering field differs. Judge YES on "cinderfall is visibly a different weather from the ash-fall frame beside it". **[H]** owner glance at the first GREEN. | **False pass:** two defs that differ only in label. [D] catches it. **False fail:** capturing before the 4000-ish-tick weather lerp has finished (§3.6). |
| 10 | `pyre_blackrain_reads` | D+V | Same as bar 9, for `RM_FE_BlackRain` versus vanilla `Rain`. | Same predicate. The judge statement is "rain that reads as black or dark, not ordinary blue-grey rain". | Same. |

### 2.4 Proposed bar-text changes (for the owner — the hashed section is not edited here)

None of the ten needs rewording to be testable. The predicates above quantify "within days" and
"densely" without touching the prose. Proposed **additions**, all owner-ruled content already in
code:

- `pyre_mapgen_log_clean` — generating a Pyrelands map logs no `CommonalityOfAnimal` NRE and no
  unresolved cross-reference. Its only allowed errors are the 4 documented `burnedDef is flammable`
  config errors. *(This is walk step 1, promoted.)*
- `pyre_burn_line_present` — somewhere on a Pyrelands map a standing burn line exists and moves
  (sheet §5 "the burn exists somewhere, always"; `MapComponent_BurnLine`).
- `pyre_firehawk_carries_ember` — fire-hawks carry burning twigs ahead of the fire and start new
  fires (`CompFireHawkSpread`, `JobDriver_RUT_FireHawkCarryEmber`). ⚠️ Prove it by a **job/state
  read**: a `JobDef` of `RUT_FireHawkCarryEmber` observed, and a new Fire within N cells. **Never**
  by a flight or screenshot hunt (flyer ruling, said three times).
- `pyre_furnacebeast_warmth` — a furnace-beast warms the cells and pawns near it (`CompFurnaceWarmthAura`,
  hediff `RM_FurnaceWarmth`).
- `pyre_burrowers_dive` — burrow-on-fire animals go under ahead of the flame (`RM_Burrowed`).
- `pyre_no_ordinary_rain` — the weather table holds no ordinary rain ([O]/[D]; sheet §6 ban 2).

Also propose **one `### cannot show`** line: `pyre_cannot_vanilla_fauna` — "a hare, rat, gazelle or
any other vanilla-Earth animal on a Pyrelands map". This catches the Replace op silently failing.

---


Bars added by the checklist author beyond that plan: `pyre_scorchfruit_fire_born`, `pyre_ruins_scorched`,
`pyre_fulgurite_after_lightning` (each backed by a shipped, owner-ruled mechanic), and the plan's
`pyre_no_ordinary_rain` was recast as the cannot-show `pyre_cannot_ordinary_rain`.

## What to answer

For EACH bar id, give one line: `id — OK` or `id — <problem> — <concrete replacement sentence>`, judging:
1. observable by a player / a screenshot (or, where inherently non-visual, by plain in-game evidence);
2. falsifiable — a clear way it could fail;
3. non-overlapping with another bar (name the overlap);
4. free of implementation detail;
5. meetable — not impossible or self-contradictory given the context above.
Then: (a) anything a player would plainly expect of this biome that is MISSING (only things this
context shows the biome already promises — do not invent new features); (b) any bar you would CUT;
(c) a one-line verdict: "validate as is", "validate with the listed edits", or "do not validate".
Number every finding. Be terse.
