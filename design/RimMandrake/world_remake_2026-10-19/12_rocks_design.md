# 12 — Rocks: a design pass, and the question cards (2026-10-19, FOUNDRY design helper)

Owner, 2026-10-19: *"Give me ideas that would motivate something new for rocks right now. Do a design
pass and give me question cards. I will rule, or select (2) or (1). Give me reasons to do 2 or 1 as well."*

Design only. Nothing here is built or filed. Scope: **building stone** (which natural rock walls a map
has). Ore, metal and gem abundance is not re-opened here: it belongs to the mineral abundance registry
(`design/RimMandrake/mineral_abundance_registry_design_2026-10-03.md`, item `MINERALS_WHERE_THEY_BELONG_1`,
partly built, waiting on his numbers sheet). Ideas below that touch metal say so and defer to it.

## 0. The finding that changes the question: the rock list is NOT painted into the world

The brief assumed per-tile rock lists must be settled before the paint. **Measured, they need not be.**
`World.NaturalRockTypesIn(tile)` (RimSage, decompiled 1.6, `RimWorld/Planet/World.cs` lines 391-417)
is computed **every time it is asked**, never saved:

1. if the tile's biome has `forceRockTypes`, return that list as-is;
2. otherwise seed the RNG with the tile's hash, draw `Rand.RangeInclusive(2, 3)`, and take that many
   distinct rocks from every loaded def that is `IsNonResourceNaturalRock`
   (`Verse/ThingDef.cs:1203-1207`: building, `isNaturalRock`, not `isResourceRock`, not
   `mineablePreventNaturalRockOnSurface`), filtered by `RockAllowedInBiome` (World.cs 419-430): a rock
   with `building.biomeSpecific` is allowed only where the biome lists it in `extraRockTypes`.

Consequences:

- **Everything about stone can land after the paint**, including option 1 vs option 2. The paint fixes
  which biome each tile is; any biome-keyed stone rule follows the paint automatically.
- Already-generated maps keep the stone they were made with (the home map in the start save); only maps
  generated afterwards change.
- Adding or removing **any** non-biome-specific rock def reshuffles every tile's draw. So any new stone
  we add must be `biomeSpecific` (or forced by a biome), or it leaks onto the whole planet.
- The one thing that IS coupled to the paint: geology that is not keyed on biome, i.e. painted world
  features (idea 7). That is the only decision owed before the paint.

## (a) What rocks are in our world now (measured)

Instruments: `measure` over `defs.sqlite`, rebuilt today from capture `DefDump/captures/2026-10-19T22-45-42Z`
(498 mods, game 1.6.4871; `MEASURED 68790 defs`). That capture predates the current list: the live
`ModsConfig.xml` (parsed with ElementTree) has **380** active mods and **0** `zacharyfoster.*`, so the
MineralsFramework set is already out (retired by `10_minerals_framework.md`). The dump is captured
before Cherry Picker; `CherryPicker.SHIP.xml` names none of the rocks below (grep, 0 hits). Sanity
probe: the same query sees all five vanilla stones and Odyssey's ice.

**The general pool (what an ordinary tile draws 2-3 from), after the MineralsFramework retirement:**

| rock | mod |
|---|---|
| Sandstone, Granite, Limestone, Slate, Marble | Core |

That is the whole planet: **five Earth stones**. `MR_BasaltBase` (Minerals Rock) was the sixth and left
with it; it was also the forced rock of `LavaField` (dump: `LavaField forceRockTypes ["MR_BasaltBase"]`,
a Minerals patch; vanilla LavaField has none). So today our volcanic biomes have no basalt, and the Forge
can roll marble and limestone. Vacstone and the GravTide outcrops carry `mineablePreventNaturalRockOnSurface`
(dump: 1) and never enter the pool.

**Biome-specific rocks (only where a biome names them):**

| rock | mod | used by |
|---|---|---|
| `SolidIce` | Odyssey | IceSheet, GlacialPlain `extraRockTypes` (vanilla biomes) |
| `VEE_DenseSnow` | VE Exploration | no biome of ours |
| `RM_LanternstoneWall` | ours | `RM_LanternDeeps` `extraRockTypes` (`src/RimMandrake/LanternDeeps/Defs/Biomes/RM_LanternDeeps.xml:196-198`; `biomeSpecific` at `.../ThingDefs_Natural/RM_LanternstoneWall.xml:37`) |
| `RM_BrineEncasement`, `RM_SaltDomeShore` | ours | no biome lists them; placed by GenSteps (`src/RimMandrake/DivingInteraction/Defs/ThingDefs_Buildings/RM_BrineEncasement.xml:64`) |

**Biomes that force their stone:** only one of our 28: `RM_RustCathedral` forces
`RM_CathedralDeckPlate` + `RM_MineableDeadSmartsteel` (`src/RimMandrake/RustCathedral/Defs/BiomeDefs/RM_RustCathedral_Biome.xml:128-131`),
a salvage-metal "rock" that yields Steel (`.../ThingDefs_Buildings/RM_CathedralDeckPlate.xml:55-60`).
The other 27 `RM_` biomes draw from the five Earth stones.

**Our code that reads the rock list** (consumers only; all take any count, per `10_minerals_framework.md:48-49`):
`src/RimMandrake/FlowWorks/Source/RM_DigDiscovery.cs:392` (what digging uncovers),
`src/RimMandrake/Stillsand/Source/RM_PreciousCaves.cs:763` and `:846`,
`src/RimMandrake/LanternDeeps/Source/GenStep_LanternstoneRock.cs:11`. Vanilla `GenStep_RockChunks.cs:48-49`
also reads it (the loose chunks on every map).

**Already rich, and not stone:** our mods ship many biome-placed resource rocks (salt crystals, brine
deposits, fossil seams, middenshell seams, greatbole heartwood, kyber formations, …; 60 rows in the dump
from `mandrake.*` + Ludeon with `isResourceRock`). Those are the registry's business.

## (b) Ideas — a Utinni rock system where geology matters for play

Costs are in plain terms. "After paint" = can land any time; "before paint" = must be decided first.

### 1. Every one of our biomes gets its own stone set  ⭐ the core idea
Each `RM_` biome names the stones its maps carry (`forceRockTypes`, vanilla field, already used by Rust
Cathedral). Volcanic biomes get basalt and obsidian; SleepingIce and The Chill get ice and dark slate;
the salt seas get salt rock; Stillsand gets sandstone only; Warscar gets scrap conglomerate (idea 3).
Biomes he does not rule on stay vanilla.
- **Buys:** the stone tells you where you are; building materials become a reason to settle somewhere;
  the Forge stops rolling marble. Uses only an engine field, so nothing to break.
- **Costs:** XML only, one list per biome, ~28 small edits inside the existing biome mods (0 new mods).
  A stone sheet per biome for him to rule (review work, one sitting). After paint. Mod Setting: "Biome
  stone sets" on/off (off = vanilla 2-3).
- **Risks:** a forced list means every map of that biome has the same stones (identity, but less
  surprise; idea 5 restores variety). The one-biome-per-ANIMAL rule does not cover stone; sharing a
  stone between biomes is allowed unless he says otherwise (ask; card 2).

### 2. Day side, twilight, night side: strata that follow the sun
Sun-baked, wind-polished stone on the day side; mixed in the twilight ring; frost-shattered dark stone
and ice on the night side.
- **Buys:** the tidal lock becomes something you can mine and build with, not just weather.
- **Costs:** if done THROUGH idea 1 (biomes are already painted by sun angle), it costs nothing extra:
  it is a theme for choosing the per-biome lists. Done as its own rule (rock weights computed from each
  tile's sun angle), a small C# patch.
- **Risks:** ⚠️ the standalone version is a programmatic per-tile assignment; that is close to the
  worldgen line (owner 2026-08-15) and invites "why is this stone hot". ⛔ No stone may change heat:
  Direct Sun is one geometric sun with vanilla heat (owner 2026-09-29 and 2026-10-19). Recommend: theme
  only, via idea 1.

### 3. Jawa salvage rock: wreck conglomerate
A natural rock of compacted wreckage (old hulls, droid scrap, fused sand) in the war and wreck biomes
(Warscar, Wasteland, Rust Cathedral already does a version). Mining it gives stone chunks plus a small
chance of scrap; smelting the chunk gives a little steel.
- **Buys:** the clan's whole identity (scavengers) in the ground itself; a reason Jawas want those
  regions; cheap early steel in a few places only.
- **Costs:** one new stone def + chunk + art (wall, chunk, blocks); precedent `RM_CathedralDeckPlate`.
  After paint. Settings: on/off, scrap chance.
- **Risks:** any metal it yields must be a row in the mineral registry (owner 2026-10-03: *"Each biome
  has carefully selected mineral abundances, period."*). New art passes the art judge (`delegation_policy.md`); no donor art kept.

### 4. Stones that play differently, not just look different
Give each Utinni stone a building identity: basalt heavy and tough but slow to cut; pumice/tuff light,
fast and weak; salt rock cheap but weathers in rain; obsidian beautiful and brittle; ice a wall that
melts above freezing.
- **Buys:** building choices tied to where you live; trading stone blocks between regions becomes real.
- **Costs:** stuff stats per stone (numbers, not code) plus balance passes; "weathers in rain" is small
  C#. Interacts with Stonecutting Extended (active). After paint. Settings: per-stone stat tuning.
- **Risks:** balance work for every stone; each one needs art. Ice that melts must read its temperature
  from vanilla air temperature, never a biome heat rule.

### 5. Rock richness as a biome trait (option 2, but per biome)
Instead of one planet-wide 1-4, each biome sets how many of its stones a map draws: Stillsand 1
(monolithic salt flat), the Forge 3-4 (shattered volcanic country), most biomes 2-3.
- **Buys:** everything option 2 promises, but meaningful: a one-rock map is a CHARACTER of that place,
  not a dice roll; keeps map-to-map variety inside a biome (fixes idea 1's sameness).
- **Costs:** one small Harmony patch on `NaturalRockTypesIn` reading a per-biome extension (palette +
  count range); one owned mod (e.g. inside the planned `mandrake.rm.minerals`, or a tiny `RM_Geology`).
  After paint. Settings: global fallback range (default 2-3), per-biome override on/off.
- **Risks:** a Harmony patch on a method other mods may also patch (which ones: UNMEASURED). Small.

### 6. Superdeep cells reach a deeper stratum
Digging a cell to superdeep (the pit/canal depth ladder) breaks through to a second, deep stone: basalt
under the Pyrelands, ice under the night side, wreck layers under Warscar. What digging uncovers already
reads the rock list (`RM_DigDiscovery.cs:392`).
- **Buys:** depth becomes a resource; a pit pays for itself in stone; the owner's quarry ruling
  (*"local materials only"*, 2026-10-03) gets a second local layer.
- **Costs:** C# in FlowWorks plus one "deep stone" field per biome. After paint. Depends on the pit work
  (`infrastructure/state/items/PIT_SUPERDEEP_COLLAPSE_1.md` is the authority). Setting: on/off.
- **Risks:** waits on pit code; more surface for FlowWorks, the current top priority stream.

### 7. Geological features painted on the world (the only before-paint idea)
A handful of hand-placed world features that override a tile's stones regardless of biome: a basalt
province, a salt dome field, a meteorite strewn field, an exposed wreck stratum. Vanilla carries these
as tile mutators (we already use mutators: `RSW_CrashedShip`, `RSW_MiningSite`, `RUT_GlassSea`).
- **Buys:** geology that crosses biome lines, like real planets; a few famous places worth travelling to.
- **Costs:** one mutator def + small worker per feature; and they must be **placed during the paint**
  (hand-authored, part of the one map). Settings: on/off per feature.
- **Risks:** adds work to the paint; Odyssey's mineral-rich mutator is not biome-aware either and must
  stay consistent with the registry. Hand placement is allowed (authoring THE map); anything that places
  them by rule is not.

## (c) Option 1 vs option 2, honestly

**For option 1 (vanilla 2-3):**
- Zero code, zero risk, and it is already the live state (MineralsFramework is out of the 380-mod list).
- Every other mod that reads or balances around the rock list expects 2-3.
- With only five general stones, the jump to 1-4 buys little: 2-3 of 5 already gives 20 different
  combinations; 1-4 gives 30.
- Leaves the door fully open for ideas 1 and 5 later; nothing is lost by waiting, because the list is
  not saved in the world.
- *Downsides:* the planet's stone is the same everywhere, Earth stone in an alien desert; volcanic
  biomes have no basalt; stone never influences where to settle.

**For option 2 (rebuild 1-4 with a setting):**
- Restores what the world had while the framework was loaded, so maps keep the spread players (and he)
  have seen; single-rock maps are striking (an all-marble map is beautiful, all-sandstone is weak walls).
- Small: one Harmony patch (~30 lines) plus a Mod Settings range, in an owned mod.
- Gives players a knob, in line with "every mod ships superb Mod Settings".
- *Downsides:* it is still a dice roll from five Earth stones: more variety, no more meaning; a 4-of-5
  map looks like any other; it answers "how many" but not "which", so the Forge still rolls marble; one
  more patch to maintain on a method other mods may touch. Idea 5 does the same job per biome for the
  same cost.

## (d) Recommendation

**Neither as asked: keep vanilla 2-3 as the default, and spend the effort on per-biome stone (ideas 1
+ 5), themed by the sun (idea 2 as a theme only).** Phase 1 is XML-only stone sets for our biomes from
stones that already exist (five vanilla, ice, lanternstone, salt); phase 2 adds a few new stones with
art, basalt first since the volcanic biomes lost it. Ideas 3, 4 and 6 follow on his rulings. Idea 7 is
the only one with a deadline: decide yes or no before the paint. If he wants the old spread anyway,
choose option 2 only as the global fallback inside idea 5, never alone.

## (e) Question cards (ready to put; add the `date` line at the moment of asking)

**Card 1 — How should a map's stones be chosen?**
*Note above the card:* "The stone list is worked out fresh each time a map is made; it is not stored in
the world, so this can be decided now or after the repaint."
1. **Leave it as vanilla (2-3 random stones from five)** — buys: no work, no risk, nothing other mods
   don't expect; costs: Earth stone everywhere, the Forge can still have marble.
2. **Bring back 1 to 4 random stones, with a slider** — buys: more spread, striking one-stone maps, a
   player knob, small patch; costs: still random, not geology; which stones you get still ignores the place.
3. **Each of our biomes picks its own stones** ← recommended — the stone says where you are, for a few
   lines of XML per biome and no new code. Costs: a stone list for you to rule per biome; every map of a
   biome has the same stones.
4. **Each biome picks its stones AND how many** — buys: identity plus variety (salt flats one stone, the
   Forge three or four); costs: a small code patch and a second number per biome to rule.

**Card 2 — Should we add new kinds of stone?**
1. **No, use only what exists** (five vanilla stones, ice, lanternstone, salt) — buys: no art, nothing to
   balance; costs: the volcanic and wreck biomes still have no stone of their own.
2. **A few new stones, basalt first** ← recommended — basalt, obsidian rock, salt rock, wreck
   conglomerate fill the obvious gaps. Costs: each needs wall, chunk and block art (your permission) and
   numbers.
3. **A full set, one or two per biome** — buys: every biome unmistakable; costs: dozens of art sets and a
   long balance tail.

*Follow-up only if he picks 2 or 3:* may a stone be shared between biomes, or does each belong to one?
(shared is cheaper; one home is stronger identity).

**Card 3 — Should stones behave differently when you build with them?**
1. **Looks only** — buys: no balance work; costs: stone choice is cosmetic.
2. **Different building numbers** (strength, work speed, beauty, weight) ← recommended — makes where you
   live shape what you build, using numbers only. Costs: a balance pass per stone.
3. **Numbers plus special behaviour** (salt rock weathers in rain, ice melts when warm, wreck rock gives
   scrap) — buys: the most play; costs: small code per behaviour and testing; scrap metal must go through
   the mineral spreadsheet.

**Card 4 — Before the repaint: do we place any geological landmarks on the world?** *(the only stone
question with a deadline)*
1. **No, biomes carry all the geology** ← recommended — keeps the repaint simple; per-biome stone already
   follows the paint. Costs: no geology that crosses biome lines.
2. **A handful of named landmarks** (a basalt province, a salt dome field, a meteorite field, an exposed
   wreck layer) placed by hand during the repaint — buys: a few famous places worth travelling to; costs:
   one small feature each plus placement work in the paint.
3. **Decide later** — buys: nothing to do now; costs: adding them after the paint means touching the
   frozen world again.

Later, not carded yet: idea 6 (superdeep cells reach a deeper stone), once the pit work lands.
