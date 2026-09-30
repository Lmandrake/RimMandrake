# The Stillsand — volley turn 3: developing what the owner ruled

**Item:** `STILLSAND_BEDAZZLE_SITTING_1` · BENCH design agent · 2026-09-30
**Reads:** `stillsand_bedazzle_review_2026-09-29.md`, `stillsand_bedazzle_2026-09-27.md`,
`stillsand_roster_fillout_2026-09-27.md`, `dune_sea.md`, `deep_desert.md`,
`SOLAR_HEAT_EXPOSURE_1`, `SHADE_GEAR_FAMILY_1`, `longshade_shade_ideation_2026-09-29.md`.

## 0. The owner's words

Volley turn 2, typed (ledger note on `STILLSAND_BEDAZZLE_SITTING_1`, 2026-09-30T07:05Z), plus one
line relayed mid-turn. Nothing below re-argues any of it.

- *"The listening should focus on wind and sand Noises and then ominous rumbling as things swim
  through the sand or bury their way to the surface. The sand swimmer mod is. Major player here."*
- *"Stillsyork makes no sense as a name. Call it a dune gale."*
- *"I like your religious implication of a ritual here."*
- *"So it would be that the very fine sand of this region is extremely high quality and can be
  smelted into a fine glass fit for lenses. The lenses can be made into high performance solar
  stills and ovens."*
- *"The biome takes its sun angle from its latitude ok the planet not a region description."*
- *"This biome needs event level creatures. Attacks by the mighty krayt dragon. And others."*
- *"The rare rock should be celebrated and almost always featuring a precious cave."*
- *"Overheating here should be trivial and difficult to avoid."*
- *"Take all these ideas and beef them up. Expand them ronustify them and then suggest yet more.
  This is THE poster biome of the old tattoine. Huge skeletons on the sand. Barren tracks of
  apparent nothingness."*
- Relayed during this turn: *"And make sure to read the moving dune mod and the sand swimmer mod.
  This is where they shine."*

Standing law carried in: the admission test (*"if it makes the map busier it is wrong —
everything admitted is buried, dormant, giant, or a line"*, `stillsand_bedazzle_2026-09-27.md`
§1), and the Long Shade condition that **every loss of an animal or pawn leaves a readable sign**
(*"we can't have animals "disappear spontaneously." There needs to be SOME kind of indication of
what happened to them."*).

## 1. The Stillsand, one paragraph

You land on a plain that runs flat to every horizon, the colour of old bone under a white sky. The
sun has not moved since the world began. The only sound is the wind: one hiss, from one bearing,
that has never turned. Every dune crest runs the same way and every shadow points the same way,
so the whole landscape is a compass pointing at the star. A kilometre off, the ribcage of
something that died before your clan had a name stands out of a dune, and the wind moans through
it. There is a track across the flat, a trough in the sand that runs straight for a hundred cells
and then simply stops, at a patch of sand that is darker than the rest. Your colonists start
cooking the moment they step off the ramp. The nearest rock is a single outcrop on the horizon,
and everyone who has ever lived here knows there is a cave in it and something precious in the
cave. Then, under the hiss, a sound you feel in your teeth before you hear it: a long, low
rumble, moving. A line of sand lifts and falls, far out, travelling. **This is old Tatooine: the
place Jawas were made for, and the place that made the krayt.** It looks like nothing. It is
full, and all of it is underneath you.

## 2. The ruled ideas, developed

### 2.0 What the two sand mods actually are (the owner: "This is where they shine")

Everything here was MEASURED this turn (2026-09-30). I read the source, the About files and the
live `ModsConfig.xml`, and swept every installed About.xml by `<name>` AND `<description>` across
both roots, `...\common\RimWorld\Mods` and `...\workshop\content\294100` (2,818 About files).
**Sanity probe:** "gravship" found 41 mods. Neither mod has "dune" or "swimmer" in a way that
identifies it by name, and neither turned up under those words. Both are **our own**, and both
were found by their item ids inside other mods' descriptions.

#### The moving dune mod: `mandrake.rm.movingdunes`

- **Source:** `D:\Luke\dev\Rimworld\src\RimMandrake\MovingDunes\`. Spec:
  `D:\Luke\dev\Rimworld\design\MOVING_DUNES_DESIGN.md` (v2). Open item: `MOVING_DUNES_BUILD_1`.
- **Installed:** not as its own folder. It ships inside the unified biome mod, at
  `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\RimMandrake.Biomes\Biomes\MovingDunes`.
  That mod's `LoadFolders.xml` lists `Biomes/MovingDunes` beside `Biomes/Stillsand` and
  `Biomes/_Kits/CreatureBehaviors`, and `mandrake.rm.biomes` is **active** (612 active mods).
- **What it does:** real wind-driven sand on Odyssey's `Map.sandGrid`, using Werner slab
  transport. It erodes, hops 2–6 cells downwind, and prefers to deposit in low and sheltered
  cells. The upshot:
  - drifts bank behind walls and scour the lee;
  - dug pits refill;
  - a crest creeps about one cell per 2.5 days, and 4× that in a sandstorm;
  - the map edges work as source and sink, with an influx budget and a mass cap.

  It also ships:
  - `RM_Dunes_BuriedCache`, plus a public `BuryThingsAt(cell, things, depth)` API. Wild items
    under deep drift become sealed caches that do not deteriorate, and they come back out when
    erosion drops the cell below 0.25;
  - **plant choke**, which slowly kills plants on an advancing front;
  - a per-map tinted sand layer;
  - `RM_DuneMaterialDef` (every number is data);
  - `DuneFieldExtension`: biome opt-in, plus a per-weather storm-transport override.

  `RM_Stillsand` is bound (Q12, done).
- **What it cannot do (its own ruled cut):** bury pawns, corpses or turrets; turn sand into a
  haulable item ("dig vanishes", RULED); grow drifts taller than depth 1.0.
- **Honest state:** per its open item, transport, burial and reveal are *"built, not yet observed
  live"*, and the shader-tint gate is still owed. ⚠️ **One conflict with the sheet.** The engine's
  wind direction random-walks over days, while dune_sea §2 says the wind *"has never once changed
  its mind."* §2.7 below shows the sun-angle ruling settles this: pin the wind to the same bearing
  as the sun.

#### The sand swimmer mod: `SAND_SWIMMERS_MOD_1`

The owner named it himself on 2026-09-06: *"Part of the 'sand swimmers' mod we are going to
make."* It was never shipped as one package. It was built into three homes:

| piece | where it lives | installed at | what it is |
|---|---|---|---|
| `RM_DeepSand` terrain | FlowWorks (`src\RimMandrake\FlowWorks\Defs\ManyWaters\TerrainDefs\RM_DeepSand.xml`) | `...\Mods\FlowWorks` (active) | Walkable at pathCost 300, per the 2026-09-27 ruling. Tagged `Water`, which is the load-bearing trick: vanilla fishing works on it with no patch. Recreational swimming is blocked by `RM_NoRecreationalSwimExtension`. The Stillsand paints it "Muchly" (threshold 0.2, perlin 0.03, minSize 60) |
| the catch, the hunter, the prize | SWBestiary (`src\RimStarWars\SWBestiary\Defs\...`) | `...\Mods\SWBestiary` (active) | `RSW_DuneCrawler` is the fish-category catch, a many-legged sand filter-feeder. `RSW_SandStalker` (bs 1.1) waits under a pool for "the vibration of a dune crawler, or a boot" and spends its whole strike on one lunge. `RSW_GlassPearl` is the rare prize, *"a lens that grew a skin"*. `RSW_RareSandCatches` is parented on vanilla's `RareFishingCatchesBase` |
| the fishing hookup | UtinniPatches `SandFishing_CrackedLands.xml` | `...\Mods\UtinniPatches` (active) | `fishTypes` only on `RM_FloodedCanyon` (the Cracked Lands twin) |

🔴 **The sand swimmers are not wired into the Stillsand at all.** `RM_Stillsand` paints deep sand
across most of the map, but **carries no `fishTypes`** (grep of the def, this turn). A fishing
zone on it catches nothing, and the dune crawler, sand stalker and glass pearl never appear in the
biome the owner calls their major stage. Two more gaps:

- **Nothing actually swims.** No shared sub-sand movement exists anywhere in `src/`. The swimmers
  run on stock AI, with bodies walking in plain view on the surface: the vekka, the qorrax, the
  drazzik, the sarlacc swimmer (`CompSarlaccSwimmer` is a water-budget and rooting comp, not a
  swim), the stalker and the krayts. That covers the sheet's *"things swim beneath it"*, the canon
  greater krayt that *"literally swam through the shifting sands"*, and the owner's
  *"things swim through the sand"*.
- **Tier drift:** the crawler and the pearl are invented, so under Q11a they belong at `RM_`.

#### Related content that is also in play

| thing | where | state | what it gives the Stillsand |
|---|---|---|---|
| **LEVIATHANS:SANDWORM** (`chezhou.creature.sandworm`) | `...\workshop\content\294100\3713982815` | **active** | A third-party Dune worm, built as a 50,000-HP building-class entity with a 5×5 hit proxy. It crushes, shoves and head-kills; destroys buildings, removes roofs and converts terrain to sand (a toggle); brings an "abnormal sandstorm" weather and its own music. It is summoned by a **sand hammer**: 10 h of accumulated vibration at a quest site. Its C# (`SandWormLib.dll`) is closed. Our repo already names it the *architecture reference* for VAST creatures (`setting_physics.md` Part 5), never a dependency |
| **The Long Hunger** (`mandrake.rut.longhunger`) | `src\RimUtinni\LongHunger\`, `...\Mods\LongHunger` | **active**, never live-fired (per its item) | Our own original-code VAST dune leviathan: erupts, pulses tremor damage, submerges dropping salvage. It comes with the `RUT_Groundcaller` prop (flavour only in v1), a contract quest, and an unwired `RUT_DuneHaze` weather. Its v2 list names the build-then-activate vibration loop, which is §2.1's thumper |
| **The krayts** (`RSW_KraytDragon` bs 12 / `RSW_GreaterKraytDragon` bs 15) | SWBestiary, ported from `mlie.starwarsanimalcollection` | wired **as ordinary wild animals**: 0.15 / 0.001 in `WildAnimals_Stillsand.xml` | Canon egg layers with combatPower 750 / 2000. No incident, no approach and no swim. Around them, in the stack: `RSW_KraytDragonSkull` + `ProcessKraytDragonSkull`, `RSW_KraytPearl` (and the lightsaber-crystal parts built on it), krayt call/angry/death `SoundDef`s, and the **`RSW_KraytGraveyard` mutator**. That mutator is a 20×20 scatter of skulls, horns and pearls; it is whitelisted to vanilla `ExtremeDesert`, not `RM_Stillsand`, and is unplaced |
| **The sarlacc** (`mandrake.rsw.sarlacc`) | `src\RimStarWars\Sarlacc\` | built | The swimmer → anchored → cistern → throat stages. Its seep marker (`RSW_DeepDesertSeep`) and the kill-sign filths `RM_Filth_DisturbedSand` / `RM_Filth_DragMark` (CreatureBehaviors) are the ready-made "readable sign" vocabulary |

⇒ **"Where they shine" in one line:** the dunes engine is the Stillsand's **surface memory** (what
the wind hides and gives back), and the sand swimmers are its **subsurface life** (what moves
under the hiss). The package below gives each of them a job in every ruled idea. It starts with
the two things they lack: swimmers that actually swim, and a dune wind that keeps one bearing.

### 2.1 The Listening — wind, sand, then the rumble

pending

### 2.2 The dune gale (renamed from Stillstorm)

pending

### 2.3 The Return — the ritual

pending

### 2.4 Sand → glass → lens → solar still and solar oven

pending

### 2.5 The krayt dragon and the other event creatures

pending

### 2.6 The rare rock, and the precious cave under almost every one

pending

### 2.7 The heat: trivial to catch, hard to escape

pending

## 3. Huge skeletons and barren tracks

pending

## 4. More ideas

pending

## 5. Recommended package, ranked

pending
