# The Twilight Deep — content drop, 2026-09-26

_The owner's Twilight Sea content drop, delivered at the bench 2026-09-26, captured and
designed-out by a BENCH design pass the same day. This document is a CAPTURE plus a
PROPOSAL: §1 is his, verbatim; §3–§9 answer his two direct requests (*"at least twelve
interesting analogs to real-world seaweed"* and *"really great unique contents here to
keep up with the Scald and Grey"*); §10–§11 sort every proposal against the frozen sheet
`design/Jawa/worldbuilding/biomes/the_twilight_deep.md` under that sheet's own rule —
**amendments add detail; they never change a ruling** — and flag what only he can settle.
Nothing here is filed as work; BENCH files with him after he reads it._

## 0. Provenance

| | |
|---|---|
| **author** | the owner, at the bench, 2026-09-26 |
| **captured by** | BENCH (design pass, same day) |
| **status** | additive amendment PROPOSED to the FROZEN Twilight Deep sheet; nothing here re-rules the sheet; §10.2 and §11 list what needs his word |
| **what is his** | every block quote and every *italic quoted phrase* — reproduced **verbatim, unedited** |
| **what is ours** | every species, plant, mechanism and name in §3–§9 (all marked **BENCH NOTE** or sitting under a heading that says "proposed"), the branch analysis in §2, §10–§12 entirely |

**Sibling documents, same day.** The sitting that produced the two rulings in §2 is
recorded on the ledger as a note on `TWILIGHTSEA_FLOOR_PASS_1` (BENCH shard, commit
`9c621ea15`). A second BENCH pass ran concurrently with this one and landed first:
`design/Jawa/worldbuilding/biomes/the_twilight_deep_bedazzle_2026-09-26.md` — *"the
marquee: rewards, experiences, interactions"*, seven ranked ideas (skylight tenancy, the
Compact's permits, the Ark Seed, living light, ride the dry river, the gardener's ways,
the charts and ledgers). The two were not written against each other. Where they overlap
they agree in direction — this document's §8.1 is that document's §3.1, §6.4/§8.4 its
§3.4, §8.2 its §3.5, §7.3 its §3.6, and the vaal-green/lamp-black pigments of §3.10 are
its §3.7 made of plants — and where one names a mechanism the other does not (its permits
and Ark Seed; this document's channel current costing, fish bodies, clinging layer and
the fourteen plants), read them as complementary. A single sitting should merge the two
into the frozen sheet; neither should be merged alone.

**Reading rule:** if a sentence is not in a block quote, not in quotation marks and not
inside a **BENCH NOTE**, it is connective prose written by BENCH from his words and
carries no more authority than a BENCH NOTE does. When in doubt, the quote wins. Unlike
the Grey Deep capture (which structured five full flora specs he wrote), **the twelve-plus
seaweeds here are BENCH inventions answering his request** — every one of them is a
proposal for him to keep, cut or rewrite, and none is canon until he says so.

**Where the Twilight Sea stands in the build, MEASURED by BENCH 2026-09-26** (do not
re-derive):

- The sea floor is a generated **pocket map** —
  `src/RimMandrake/DivingInteraction/Defs/MapGeneration/RM_SeaDiveGenerators.xml`,
  `RM_SeaDiveGenerator_TwilightSea` (`pocketMapProperties/biome` = `RM_TwilightSea`,
  temperature 8, mutator `RM_SeaFloorHabitat`; gensteps `ElevationFertility`,
  `RM_SeaFloorTerrain`, `RM_PlaceSeaDiveExit`, `RM_SeaFloorFauna`, `Animals`, `RockChunks`,
  `Fog`). **No `Plants` step, no scatter steps, no dressing step** — the Grey's generator
  gained nine such steps this week; the Twilight's is still the bare four-sea template.
- Access is **ship-only**: `RM_SeaDiveHatch` (`src/RimMandrake/DivingInteraction/Defs/ThingDefs_Buildings/RM_SeaDiveHatch.xml`,
  a `MapPortal` subclass gated by a `PlaceWorker_NeedsGravEngine`). The pawn-dive is
  retired and deleted; `design/RimMandrake/sea_dive_maps_spec.md` still describes it and
  was not used for anything here.
- The floor's one terrain is the shared `RM_SeaFloorGround` (`fertility 0`; the Grey wave
  had to set `completelyIgnoreFertility` on every plant because of it).
- The live def `src/RimMandrake/TerminalBiomes/Defs/BiomeDefs/RM_TwilightSea.xml`:
  **6 `wildAnimals`** (`AA_Aerofleet` 0.05 · `RM_Lanternwhale` 0.005 · `RM_Noolim` 0.8 ·
  `RM_Loohn` 0.01 · `RM_Weloon` 0.4 · `RM_Lunoowa` 0.3), `animalDensity` 0.1, **zero
  `wildPlants`**, **no `plantDensity`** (defaults to `0f` — the same silent kill the Grey
  wave hit), weather `Clear 12 / Fog 7 / Rain 4` (vanilla; the `Rain` is the same
  pre-existing defect against `terminator_sea.md` §6 the Grey removed at `31dbd962d`),
  `maxFishPopulation` 700, **12 `fishTypes`** (common: `RM_Niim` 1.5, `RM_Pallu` 1,
  `RM_Tikkarr` 0.8, `RM_Nuudal` 0.6, `RM_Aluun` 0.6, `RM_NoolimCatch` 0.8; uncommon:
  `RM_Kellu` 1, `RM_Murrol` 0.8, `RM_Hollu` 0.8, `RM_Oobo` 0.4, `RM_Liiru` 0.5,
  `RM_WeloonCatch` 0.4), rare table `RM_RareTwilightCatches` (headline `RUT_LampBlack`).
- Floor bodies BUILT (`RM_TwilightSeaFauna.xml`, `RM_SeaBeasts_Invented.xml`): `RM_Noolim`
  (the shoal, `herdAnimal`, `wildGroupSize 5~15` — the one legal school), `RM_Loohn` (the
  predator), `RM_Weloon` and `RM_Lunoowa` (detritivores), `RM_Lanternwhale` (the giant,
  *"moss-shrouded and trailing blue lantern tendrils"*).
- **Catch items with NO floor body: 10 of 12** — niim, pallu, tikkarr, nuudal, kellu,
  murrol, hollu, oobo, aluun, liiru. `SEA_FISHABLES_ALIVE_IN_DEPTHS_1` did the Grey's
  seven and left *"other three seas untouched."* Every one of those ten descriptions
  already contains its creature's design (§5).
- 🔑 **Bioluminescence is ALREADY shipped canon here**, before today's drop: `RM_Niim`
  (*"a dot-line of cold light along the flank"*), `RM_Liiru` (*"a single unbroken line of
  blue-white light"*), `RM_Aluun` (*"a mantle that lights — a steady pale gold … a column
  of small windows"*), `RM_Lanternwhale` (*"blue lantern tendrils"*). The catch file's own
  header records that *"the glow-phrase question (reword or art-only) is still with the
  owner"* — today's drop answers it: the glow is real (§6).
- **NOT built:** zero plants, zero own weather, zero own terrain, zero buildings, zero
  incidents, zero skylights (the word appears in four catch descriptions and no def), zero
  channels, zero Deepwater presence on the floor.
- The Inhabited system (`mandrake.rm.inhabited`, `src/RimMandrake/Inhabited/`) exists,
  has a **25-character Deepwater cast** (`Defs/CastRosters/CastRoster_DEEPWATER.xml`,
  generated from `design/Jawa/bridge/INHABITED_CAST_DEEPWATER.md`), a **Deepwater Hold**
  settlement manifest with four district templates, a `RM_InhabitedPlace_WaterHold`
  archetype, and the FactionDef `RUT_Jawa_DeepwaterCompact` (`raidsForbidden true`,
  xenotypeSet of eleven Star Wars amphibian-and-other races). What it does NOT have is any
  wiring to a pocket map (§9).

## 1. His words, verbatim

The whole drop, entire and unedited:

> "The skylights should show up as literal golden shafts of long beautiful light reaching down to the sea floor. I don't know what the "mold mats" are and I'm not sure we need them. We definitely want kelp analogs and many other kinds of seaweed, but each should be made wild and alien-looking. Colors should be lustrous green and blue-green. It's a pretty ocean. Creatures tend to have luminous balls, bladders, or patches of bioluminescent organisms within them, making the place dim but well populated by local illumination plus the moving patches from the shafts of golden light. The underwater rivers are just channel-patterns in the terrain, like riverbeds on the surface. Propose at least twelve interesting analogs to real-world seaweed, the more alien the better. There should be a lot of little creatures clinging around all those plants, a lot of fish analogs. Fishing here should be prolific and unlimited, and draw from these same populations in terms of type, name, and appearance. The only weather on the sea floor are lighting condition changes due to water opacity and occasional clouds/large creatures above you. The shadow of the great whale analog would be welcome. Now, we need some really great unique contents here to keep up with the Scald and Grey. What could be down here? I'm thinking it will be in the plants and animals that are present more than minerals. This is a settled sea by the Deepwater faction, so they would have cleaned up most of the scavenge and open mineral wealth lying about. There could even be inhabited-injected Deepwater faction houses here of the appropriate races (very cool!)."

The two direct requests this document answers:

> "Propose at least twelve interesting analogs to real-world seaweed, the more alien the better."

> "Now, we need some really great unique contents here to keep up with the Scald and Grey. What could be down here? I'm thinking it will be in the plants and animals that are present more than minerals."

*[Editorial, 2026-09-26: the "mold mats" in the quote above are the ceiling organism — kept
by ruling and named by him the same day: it is **the waveglass** (§2.1).]*

**BENCH NOTE — the eleven instructions inside the paragraph, so nothing gets lost.** (1)
skylights are *literal golden shafts* reaching the floor; (2) the ceiling organism is in
doubt (ruled: kept, as the waveglass — §2.1);
(3) kelp analogs and many seaweeds, *wild and alien-looking*; (4) *lustrous green and
blue-green*, *"It's a pretty ocean"*; (5) creatures carry *luminous balls, bladders, or
patches*; the place is *dim but well populated by local illumination* plus the *moving
patches* of the shafts; (6) rivers are *channel-patterns in the terrain, like riverbeds*;
(7) *a lot of little creatures clinging around all those plants*; (8) *a lot of fish
analogs*, and fishing is *prolific and unlimited* and *draws from these same populations
in type, name and appearance*; (9) the only weather is *lighting condition changes* —
opacity, clouds, large creatures above; (10) *the shadow of the great whale analog*; (11)
the Deepwater have *cleaned up most of the scavenge and open mineral wealth* — and could
have *inhabited-injected … houses … of the appropriate races*.

## 2. Two rulings that landed while this was being written

> "I don't know what the "mold mats" are and I'm not sure we need them."

*[Editorial, 2026-09-26: his "mold mats" = the ceiling organism of the frozen sheet; ruled kept
and, later the same day, named **the waveglass** — see §2.1.]*

> "The underwater rivers are just channel-patterns in the terrain, like riverbeds on the surface."

Both sentences were put to him at the bench the same day and **both were ruled — decision
taken by question card, 2026-09-26.** ⚠️ A question-card ruling is OUR sentence that he
clicked, not text he typed; nothing in this section is an owner quote, and nothing here
may be passed as `--owner-said`. The two rulings, as recorded:

### 2.1 RULED: the ceiling STAYS — it is THE WAVEGLASS

The ceiling mechanism is kept exactly as the frozen sheet has it: skylights remain holes
in it and so keep their source, their drift and their expiry (ban 5); the ceiling gardens
keep something to hang from; the gardener keeps its job (ban 2); all six hard bans hold;
the sheet's §0 physics (the roof blocks the drying wind, which is why the Twilight outlives
the Grey) stands. **What went was the word "mold."** The roof is living glass in lustrous
blue-green, to match *"It's a pretty ocean."*

**The name is his.** BENCH proposed *oolune*; the owner typed, 2026-09-26 (recorded on
`TWILIGHTSEA_FLOOR_PASS_1`): *"love what you made but just call it waveglass"*. ⇒ **The
waveglass.** The description below stands as agreed; only the word changed.

**The waveglass.** One organism, shore to shore, the same single monoculture the sheet always
said it was — and seen from far below it is a **living stained-glass ceiling**: a translucent
blue-green sheet, veined gold where the sunset light strikes it, thick and opaque where it
is old and thin and luminous where it is new. Its underside is fringed with the ceiling
gardens; its skylights are holes rimmed in bright pale new growth, the way a wound in kelp
is rimmed pale. The Deepwater call it *the lid*. What it sheds is **veil-fall** — whole
panes that let go and turn slowly down through the shafts catching gold, to settle on the
floor where the weloon eat them and the lunoowa pretend to be them. It is far overhead: a
sky, not a surface anyone works. What reaches the floor from it is light, shed panes and
falling things. The word the shipped prose reaches for is *veil*, never *mat* or *mold*.

**Consequential rewording — DONE 2026-09-26** (`Transient/waveglass_rename_2026-09-26.md`
holds the pass): `RM_TwilightSea`'s description, the four built creatures (`RM_Noolim`,
`RM_Loohn`, `RM_Weloon`, `RM_Lunoowa`), the twelve catch items, the frozen sheet's §0/§1/§3/
§4/§6/§8/§9 under the additive rule, `terminator_sea.md`, and the roster's `new_defs` row.
⚠️ The floor **plant** `RM_MoldMatRoof` was left as found: the owner ruled the same day that
the organism is not a plant on the floor at all but *"a big panel that occasionally floats
down and can be harvested"* — an event plus an item — so that def is being retired and
redesigned, not renamed.

### 2.2 RULED: the underwater rivers STILL CARRY YOU — ban 3 stays live as a real mechanism

His sentence read as retiring ban 3 (*"no swimmable river — entering a bottom channel
means sinking with it; harvest and travel happen on the banks"*). **He ruled the other
way**: the channels LOOK like riverbeds — banked, braided, mud-bedded, dry-looking — but
the denser water inside them **still moves a pawn along it**: a current you can be caught
in. Ban 3 stands as a mechanism, not as flavour.

**BENCH NOTE — what that mechanism actually costs.** This is new C# and a pawn-movement
system; the visual (a riverbed terrain strip) is cheap and the mechanism is not, and
this document does not pretend otherwise. What is owed, honestly:

1. **A channel generator with a flow field.** The Grey's `GenStep_GreySeaFloorDressing`
   already paints brine channels downhill along the map's elevation grid, so the *terrain
   line* is a solved shape. The Twilight's needs one more thing: a **direction per channel
   cell** (a stored `IntVec3` flow vector), braided and banked, kept clear of the dive-exit
   footprint (`RM_PlaceSeaDiveExit`) so the ship never lands astride one. Rough size: a
   genstep plus a per-map flow grid, persisted (`MapComponent` + `ExposeData`).
2. **The current itself.** A `MapComponent` that, every N ticks, moves every pawn standing
   on a channel cell one cell along the flow (`pawn.Position` step with
   `pather.StopDead()` and a position-changed notify — the shape mods use; no vanilla
   "conveyor for pawns" exists in the code read for this pass, and `CompPushable` on the
   nociosphere is a one-shot shove, not a flow). Strength by position: **the outer bank
   cells push weakly, the centre pushes hard** — so a colonist at the margin can walk out
   and one in the middle cannot. That gradient is the whole teaching mechanism (below).
3. **Where it takes you.** Downstream to the channel's sink — the sheet's *"sinking with
   it"*. **Position, his to set:** the sink is a basin cell cluster at the channel's low
   end where a carried pawn is dumped and takes a *sunk* hediff (a cold/drowning-style
   severity ramp, Moving reduced), recoverable by a rescue from the bank. Not death by
   default; a colonist *can* be lost if nobody comes. The Grey's encasement precedent
   (Q1(b) there) shows he prefers a recoverable, dangerous object state over an instant
   loss; this proposes the same posture and asks.
4. **Interactions that must be handled, or the mechanism lies:**
   - **Pathfinding** — the bed terrain is standable, so the pather will route THROUGH a
     channel to save two cells unless told otherwise. Give the bed terrain a high
     `pathCost` (the deep-water shape) so AI routing avoids it and a colonist enters only
     on a direct order or a job that targets the bed. Wandering colonists and animals
     otherwise walk in.
   - **Hauling** — an item dropped on the bed should drift too (the same tick moves
     `Thing`s in the item category), or the bed becomes a free conveyor for hauling;
     position: items drift, at half rate. A haul job whose target moves must fail
     gracefully (vanilla re-targets on `Thing` position change; worth a check).
   - **Downed pawns** — a downed pawn in the channel keeps drifting to the sink; the
     rescue job must target a moving pawn (vanilla `JobDriver_Rescue` re-paths to the
     pawn's current cell; verify).
   - **Animals** — channel-native species (`RM_Murrol` *"rides the invisible current along
     the channel banks"*, the nuudal on the bank silt) are exempt by a `modExtension` on
     the race; everything else drifts like a pawn. The loohn hunting into a channel is a
     lovely accident to allow.
   - **The gravship** — never generated over a channel (item 1); a ship-part placed on the
     bed later is the player's mistake and stays put (buildings don't drift).
   - **Fishing and harvest** — the banks, not the bed, per the ban; see §8.2.
   - **Save/load** — the flow grid and every drifting thing's state are `IExposable`.
5. **Mod Settings:** current on/off; current strength; sink outcome (hediff / none);
   first-entry warning on/off.

**How a player learns the edge before it costs a colonist** (design, not mechanism):

- **The floor looks dry, so the tell cannot be the floor.** Three tells, cheapest first:
  (a) **things move on it** — veil-fall flakes skate along the bed in an effecter that
  follows the flow vectors (a mote stream), and murrol ride it mouth-open: *you see the
  floor is a river because the litter on it is travelling*; (b) **the Compact has staked
  it** — bank-stakes with lamps (§9's `RM_BankStake`, gold-lit, every ~8 cells along
  both banks) mark exactly where the pushing starts, because people who have lived here
  for generations do not leave a river unmarked; (c) **the first step in is recoverable**
  — the margin cells push weakly with a one-time message (*"the ground is moving under
  {PAWN}"*) and a mood-free alert, so the first contact teaches at the cost of a few cells
  of drift, and only the centre takes you.
- **The banks are the reward for reading it** (§8.2): the fertile silt where the kelp
  farm goes and where the murrgrave lace and the nuudal are thickest sits *between* the
  stake-line and the bed. The richest ground is one careless step from the current, which
  is the sheet's *"the banks are the wealth"* with the danger live, as ruled.

Everything below is written for the ruled world: the waveglass stands, the channels carry.

## 3. The seaweed analogs — fourteen, proposed

> "We definitely want kelp analogs and many other kinds of seaweed, but each should be made wild and alien-looking. Colors should be lustrous green and blue-green. It's a pretty ocean."

> "Propose at least twelve interesting analogs to real-world seaweed, the more alien the better."

**BENCH NOTE — rules every entry obeys.** All names are **invented** and therefore
`RM_`-tier (Q11a: an invented exotic name is not IP; the free mod's floor must stand
alone). Every name was collision-checked against `src/` and `design/` 2026-09-26. Every
plant is green or blue-green with *lustre* — the art rule for this biome is the inverse
of the Grey's "marred, never manufactured": **wet, glossy, translucent where thin, catching
gold where a shaft touches it** — and none is an Earth seaweed by name or read (ban 6:
"kelp analog" is the register, never the label). The frozen sheet exempts the floor from
`terminator_sea.md`'s surface bans by its own scoping line (*"neither world leaks into the
other"*), so a plant here may be lush, may stand in forests, may open and close. Silhouette
spread, deliberately: **towers ×2, bladders ×2, fan ×1, drifters ×2, mats ×2, encruster ×1,
rope ×1, frond ×2, veil ×1.** Nine of fourteen are interactable beyond harvest. Engine
shape for all: vanilla `PlantBase`/`BushBase`/`TreeBase` with `completelyIgnoreFertility`
(the floor is fertility 0) and `growMinGlow` used as the skylight gate (§6.3) — the Lantern
Deeps' `RM_DeepFlora.xml` is the shipped pattern for a floor flora set with glowers.

| # | name | form | what it is for | his property carried | interactable |
|---|---|---|---|---|---|
| 3.1 | **oruvell** — vellum kelp | tower | food fronds · **lattice-timber** (sheet §4) · host of aluun and tikkarr · sowable | kelp analog; lustrous green; grows only in shafts | harvest, sow |
| 3.2 | **ghallowyn** — the hollow pillar | tower | the timber tree; dead stipes are the Compact's columns and chimneys | kelp analog; alien silhouette | fell |
| 3.3 | **hoolimbre** — lamp-bladder weed | bladders on ropes | **portable light** (harvested bladders glow for days) · home of the piip | *luminous bladders* | harvest |
| 3.4 | **noothelm** — sea-lantern | one bulb on a stalk | the standing lamp plant; **sowable light** around a house | *luminous balls* | sow |
| 3.5 | **sennefan** — sail-fan | fan | **fibre** (sea-silk cloth) · beauty · host of the skerrin | blue-green lustre; alien shape | harvest |
| 3.6 | **ummarel** — the sky-raft | drifter (under-canopy) | drifting rafts *under* the lid that sweep shadows across shafts; sunk rafts on the floor are harvestable | pretty ocean; moving light patches | harvest (sunk) |
| 3.7 | **waelune** — lantern-drift | drifter (ball) | rolling lit weed-balls; light and food; the thing children chase | *luminous balls*; moving illumination | pick up, keep (§6.4) |
| 3.8 | **thessmoss** — floor-felt | mat | grazing turf for nuudal and murrol; the bank's ground cover | lustrous green carpet | grazed |
| 3.9 | **murrgrave** — detritus lace | lace/mat | marks the **richest ground** (thickest veil-fall); food; the kiruun's home | blue-green; the banks are the wealth | harvest |
| 3.10 | **vaalstone** — glass-crust | encruster | the sheen on every rock and stone in a shaft; **green pigment** (pairs with lamp-black) | lustre itself | harvest |
| 3.11 | **skirroth** — throttle-rope | rope/tangle | **net cord** (the Compact's nets); a slow-you-down tangle | wild; alien; a lot of little creatures in it | harvest, hazard (soft) |
| 3.12 | **illuvane** — bruise-leaf | frond | **herbal medicine** analog; the hospital ward's plant | blue-green; pretty | harvest, sow |
| 3.13 | **sarrowhisk** — the shoal-lure | frond | **bait**; where it grows the fish are thickest | prolific fishing | harvest |
| 3.14 | **quellith** — the stinging veil | veil/curtain | the one plant that hurts; the vessik's shelter | wild and alien; a little danger in a pretty place | hazard (low) |

### 3.1 Oruvell — vellum kelp `RM_Oruvell`

**Look.** The kelp analog proper. A single glossy blue-green stipe as thick as an arm,
rising three to four cells' worth of drawn height, hung with long blade-fronds that unroll
from the tip like sheets of wet vellum and catch the gold of the shaft they stand in. New
fronds are near-transparent; old ones deepen to bottle-green. A stand of forty under one
skylight is the sheet's *"kelp forest."* **Behaviour.** Grows only where there is light
(`growMinGlow` ~0.5 — it stands in the shafts and nowhere else, which is the sheet's
*"the kelp reaches for the light-wells"* for free), and a skylight that closes kills its
stand over a season (no light, slow death). **Use.** Harvest gives **oruvell fronds** (raw
food, Nutrition ~0.25, the sea-farm's staple) and, from a mature stand, **lattice-timber**
(`RM_LatticeTimber`, a woody `StuffProps` — the sheet's *"wet lattice-timber"*; the
Compact's houses are built of it, §9). **Sowable** in a growing zone on bank silt (§8.2)
— the sheet's §7 *"kelp agriculture."* Host of the aluun (sessile on its stems) and the
tikkarr (which cuts it; *"cut kelp plots without tikkarr in them grow back slow"* — the
catch item already says so; BENCH position: a plot within radius of a tikkarr grows ~10%
faster, a small comp or nothing at all). **Roof-independent.**

### 3.2 Ghallowyn — the hollow pillar `RM_Ghallowyn`

**Look.** The other tower: a kelp analog whose stipe is a fluted column, blue-green
outside and pale within, that hollows as it ages until an old one is a standing pipe
crowned with a ragged tuft. Sparser than oruvell, taller-drawn, and it stands at the
*edge* of a shaft, not the centre (`growMinGlow` low, `growOptimalGlow` high). **Use.** The
timber tree — felling a mature one gives lattice-timber in quantity; a *dead* one (an aged
graphic) is what the Compact stands its lamps and chimneys in (§9's houses show ghallowyn
columns). Slow-growing (`growDays` long) so a stand of them is a generation's wealth,
which is how a bottom-family measures itself. **Roof-independent.**

### 3.3 Hoolimbre — lamp-bladder weed `RM_Hoolimbre`

**Look.** Ropes of green weed studded every hand-span with translucent bladders the size
of a fist, each holding a colony of luminous symbionts: pale gold, breathing slowly
brighter and dimmer. The bladders float the ropes upward so a hoolimbre bed is a hanging
curtain of soft lamps, and a shaft's edge is where they crowd. **Behaviour.**
`CompGlower` radius ~3, gold; the glow *breathes* by nudging `GlowRadius` (public setter,
§6.2). **Use.** Harvest gives **lamp-bladders** (`RM_LampBladder`, an item that carries its
own `CompGlower` and rots in ~6 days — a light you can carry and set down, the biome's
torch; §6.4). Home of the piip (§4). **Carries:** *"luminous … bladders."*
**Roof-independent.**

### 3.4 Noothelm — sea-lantern `RM_Noothelm`

**Look.** A squat rosette of blue-green leaves and, from its centre, one stalk carrying
one sphere — a lantern-bulb as big as a head, milk-green when dark and lit from within at
all hours, a steady cool green-gold. Standing alone on the floor it is the biome's street
lamp; in threes around a doorway it is the Compact's porch light. **Behaviour.**
`CompGlower` radius 4–5. **Use.** **Sowable** — a colonist can plant light (§6.4). A
harvested bulb is a one-day light and a poor meal. **Carries:** *"luminous balls."*
**Roof-independent.**

### 3.5 Sennefan — sail-fan `RM_Sennefan`

**Look.** A single broad fan on a short stalk, blade-thin, held edge-on to the current
like a sail on a mast: ribbed, blue-green, translucent enough that a shaft behind it
shows through as veins of gold. A field of them all facing the same way tells a diver
where the current runs — **which is the channel's fourth tell** (§2.2). **Use.** Harvest
gives **sea-silk** (`RM_SeaSilk`, a fabric stuff — the Compact's cloth, the wardens'
robes, `Beauty` high, insulation poor, which is right for a people who never leave the
water). Beauty plant (`purpose Beauty`). Host of the skerrin (§4). **Roof-independent.**

### 3.6 Ummarel — the sky-raft `RM_Ummarel`

**Look.** A free-floating weed that forms **buoyant blue-green rafts** hanging *just
under the lid*, drifting in the water between the waveglass and the floor, so that from
below a raft is a darker shape crossing a shaft. It is the *"moving patches"* of his
light made of a plant: a raft passing under a skylight sweeps a shadow across the floor.
**On the floor map** it appears as **sunk rafts** — waterlogged tangles that have lost
their buoyancy and settled, harvestable for raft-fibre (cordage and, dried, a poor fuel)
and thick with clinging things. **Engine:** the floating form is not a floor def; it is
one of the shadow-passing events (§7.2, the small sibling of the whale's shadow).
**Relation to the ruled canopy:** the waveglass is the roof; ummarel drifts *under* it and
never replaces it — it is the sheet's *"instruments moored to the ceiling"* made of
weed, the thing the Compact tethers buoys to.

### 3.7 Waelune — lantern-drift `RM_Waelune`

**Look.** A spherical weed-ball, lit from within pale green, from fist- to
cushion-sized, that rolls along the floor with the current and fetches up in drifts
against towers and house-walls. A floor with waelune on it has moving lights on it.
**Engine honesty:** a plant cannot move; the drift is either a plant a small map
component despawns and respawns a few cells downstream every few days, or a slow
harmless *creature* like the lunoowa. BENCH position: **creature**, `MoveSpeed` 0.5,
`Wildness` 0 — it makes the *"luminous balls"* line literal, it rides the channels (§2.2:
an exempt native), and it gives the Compact's children something to chase. **Use.**
Picked up, it is a light for a day and food for a meal; kept, it is a lamp that walks
(§6.4). **Carries:** *"luminous balls."* **Roof-independent.**

### 3.8 Thessmoss — floor-felt `RM_Thessmoss`

**Look.** A close, lustrous green turf, felted, that carpets the channel banks and the
floor under the busiest shafts, thicker where the veil-fall is thicker. **Use.** Grazing:
it has `Nutrition` and the nuudal and murrol eat it where it grows (vanilla herbivore
grazing), so the floor's herbivores have a real food chain rather than a hunger-rate
fiction. No harvest. Its edge is the first thing a diver reads: **thessmoss stops at the
stake-line** (§2.2) — it does not grow on the bed. **Roof-independent.**

### 3.9 Murrgrave — detritus lace `RM_Murrgrave`

**Look.** A pale blue-green lace, like frost on the silt, that grows only where the
veil-fall lies thickest — under the busiest skylights and on the channel banks. It is the
sheet's *"the richest ground in the sea is the mud under a busy skylight"* made visible:
where the lace is, the ground is rich. **Use.** Harvest gives **murrgrave** (raw food,
the floor's mushroom analog, filling and plain). Home of the kiruun (§4), which light it.
**Ruled canopy:** the veil-fall it needs is the waveglass's, so its map on the floor is the
map of the lid's gardens above — a diver reading murrgrave is reading the ceiling.

### 3.10 Vaalstone — glass-crust `RM_Vaalstone`

**Look.** An encrusting alga that grows over every rock chunk, stone and dead stipe in a
shaft as a hard, glassy, blue-green sheen — the reason the whole floor under a skylight
*glitters*. **Engine:** a plant scattered adjacent to `RockChunks` and formations (the
Grey's cluster-weight shape), `Beauty` positive. **Use.** Scraped, it gives **vaal-green**
(`RM_VaalGreen`, a pigment item) — the green in which the Compact's charts are drawn,
under kellu lamp-black: **black ink on green-tinted vellum**, the two pigments of one
sea. The dye-houses that already buy `RUT_LampBlack` buy this too. **Roof-independent.**

### 3.11 Skirroth — throttle-rope `RM_Skirroth`

**Look.** Long green cords strung between towers, knotted into tangles that hang across
the dark between shafts like rigging. **Behaviour.** A soft hazard: `pathCost` high, so
walking through a tangle is slow and the AI routes around it — the *"dark between
columns"* is hard going as well as dark. Not damaging. **Use.** Cut, it gives **net-cord**
(`RM_NetCord`) — the Compact's nets are woven from it, and the fishing-net building of
§8.2 costs it. Full of little things (the thurrim, §4). **Roof-independent.**

### 3.12 Illuvane — bruise-leaf `RM_Illuvane`

**Look.** A low blue-green frond-cluster with leaves that bruise purple where touched and
heal by the next day. **Use.** Harvest gives **illuvane**, the biome's **herbal medicine**
analog (a `MedicineHerbal`-class item with its own potency, the Compact hospital ward's
stock — `RM_InhabitedPlace_WaterHold` already larders `MedicineIndustrial`; the
bottom-house archetype larders this instead). **Sowable.** **Roof-independent.**

### 3.13 Sarrowhisk — the shoal-lure `RM_Sarrowhisk`

**Look.** A whisk of fine green filaments that exude a sweet mucus into the water; a
shaft with sarrowhisk in it is *visibly* thicker with niim, and the pallu stack above it.
**Engine:** two honest shapes, and which is buildable is UNMEASURED: (a) a comp that
raises the fish population of the water body its cell touches (§8.2 makes the shafts
water) — the Odyssey population model is per water body, so a per-plant bonus needs a
patch; (b) simpler and certain: **harvest gives bait** (`RM_SarrowBait`), an item that
raises fishing yield when carried by the fisher — vanilla has a `FishingSpeed` stat;
whether an equipped item can offset it is a def-level question, not C#. Position: (b)
first. **Carries:** *"prolific."* **Roof-independent.**

### 3.14 Quellith — the stinging veil `RM_Quellith`

**Look.** A hanging curtain of translucent blue-green tissue threaded with fine white
stinging lines, beautiful, and the one plant on the floor that hurts: brushing it is a
sting (the `RM_Venomvine` contact-damage shape from `mandrake.rm.environmentalhazards`,
**low** damage — the Twilight is not the Grey, and one hazard plant is enough for a
pretty ocean). **Use.** Shelter of the vessik (§4), a small fish-analog immune to it and
netted with it. Harvested carefully (`harvestMinGrowth` high, a skill gate) it gives a
numbing paste the hospital uses — a position, not a requirement. **Roof-independent.**

**BENCH NOTE — what is NOT here on purpose.** No crystal, no salt, no mineral-armoured
plant — the Grey owns that idea entirely (`RM_GlassVeilKelp`, `RM_BrineCrown`,
`RM_MosaicFanPalm`, `RM_CruciblePod`, `RM_SpherePlant`, `RM_CubicSculpture`,
`RM_SaltChimneyVine`). The Twilight's plants are **soft, wet, lit and alive**; the Grey's
are hard, dry-looking, dark and dead-looking. Where the Grey's flora *precipitates* the
sea onto itself, the Twilight's *drinks* the light. That contrast is the design.

## 4. The clinging layer — little creatures on the plants

> "There should be a lot of little creatures clinging around all those plants, a lot of fish analogs."

**BENCH NOTE.** This is a real layer with its own species, not a description detail: six
small creatures, each bound to a host plant, so that *every* plant in §3 that a diver
stands next to has something moving on it. They are what makes *"well populated"* true
at the scale of a single cell. Engine: each is an ordinary `AnimalThingBase` race with a
tiny `baseBodySize` (0.03–0.08, the Grey's `RM_Nissik` precedent at 0.08), `MoveSpeed`
low, and **placement beside its host** — vanilla has no "spawn animals near plant X",
so a Twilight variant of `GenStep_SeaFloorFauna` seeds each clinger adjacent to its
host def (one loop: for each clinger, for each host plant found, roll N and spawn beside
it). After generation they wander like any animal; low speed and a small wander radius
keep them *near* rather than *on*, which is honest and enough. Abundance is carried by
**commonality and per-host count, never by `wildGroupSize`** (the Grey wave's lesson);
none is a school. Four of six are catchable and owe the standing two-def shape (floor +
`*Catch`). Three names were renamed after collision hits (skerrit → skerrin, ollo → ulloo,
thrumm → thurrim); the renamed forms were not re-checked and should be before authoring.

| clinger | host | what it is | glow | catchable |
|---|---|---|---|---|
| **piip** `RM_Piip` | hoolimbre bladders | thumb-sized, round, translucent; clusters of them cling to the bladders and *are* half the bladder's light — a plucked bladder's piip scatter as sparks | yes, tiny (radius 1) | no — too small; they are the sparks |
| **skerrin** `RM_Skerrin` | sennefan fans | a spined little frond-hopper, blue-green, flat to the fan and invisible until it jumps | no | yes — a crunchy handful, the Twilight's small shrimp-analog (the Grey's is `RM_Nissik`; this one has spines and lives on a fan, never on the floor) |
| **ulloo** `RM_Ulloo` | vaalstone crusts | a glass-shelled snail-analog grazing the crust; its shell takes the sheen | no | yes — shellfish, the aluun's small cousin; shells are a bead |
| **thurrim** `RM_Thurrim` | skirroth tangles | a soft filter-worm knotted into the ropes; a tangle is a living thing when the thurrim feed | faint blue-white patch | no |
| **vessik** `RM_Vessik` | quellith veils | a finger-long fish-analog that lives *inside* the stinging veil, immune; netted with the veil | no | yes — "the veil's fish", a delicacy priced by the sting it took to get it |
| **kiruun** `RM_Kiruun` | murrgrave lace | glow-shrimp dust in the lace; the reason the richest ground *looks* rich — the floor there is faintly lit from below | yes, patches (radius 1.5, blue-white) | yes — netted from the silt, a spoonful of light and food |

**What this layer does in play.** It is the floor's first food (a diver who lands with
nothing can pick ulloo and skerrin by hand), it is the predators' prey (the kellu and the
loohn hunt among them, `maxPreyBodySize` set so the loohn will not bother with them and
the kellu will), and it is the texture of the place: **a plant with nothing on it reads
as dead**, and after this layer none is. Ban 6: none is an Earth creature by name or read
— the *shapes* are ordinary (a snail, a shrimp, a worm) because ordinary-in-shape is
exactly this biome's register (sheet ban 6, *"ordinary in shape is this biome's
register, never nameable"*). **Roof-independent**, all six.

## 5. The fish analogs — floor bodies for the twelve catches

> "Fishing here should be prolific and unlimited, and draw from these same populations in terms of type, name, and appearance."

**BENCH NOTE — the rule this section obeys is already standing:** *every fishable is also
a living creature on the floor, in every sea* (owner, 2026-09-26, `CLAUDE.md`), and the
Grey discharged it this week by giving each catch a body *from its own description*.
The Twilight owes the same for **ten** catch items, and every one of the ten descriptions
in `RUT_TwilightFish_Niim.xml` already contains its creature's design — read in full for
this pass; the body specs below are those descriptions turned into race fields, not
new invention. Name, type and appearance are shared by construction: the floor def and
the catch def carry the same label and the same art brief, per his sentence.

| catch (`fishTypes`) | floor body today | body proposed | groups | glow | notes from its own prose |
|---|---|---|---|---|---|
| `RM_Niim` 1.5 | **none** | `RM_Niim` race — the shoal fish, `herdAnimal`, bs 0.06, fast | 6~14 | dot-line, radius ~1.5 blue-white | *"schools in the light columns … make the column flash when they turn"* — a school of small glowers IS the flash. ⚠️ See flag §10.2-4: `RM_Noolim` already ships as *"the silver-shoal analog"* |
| `RM_Pallu` 1 | none | `RM_Pallu` — a slow drifter (spd 0.6) that stays in shaft cells; a green symbiont mat | 3~8 (a stack) | green patch, radius 1 | *"lives only in the light columns … The Compact counts them to price a skylight"* — spawn only on skylight cells (§6.3); their count is the §8.1 price |
| `RM_Tikkarr` 0.8 | none | `RM_Tikkarr` — long-legged kelp-crab, climbs oruvell; herbivore (eats the kelp) | 1~2 | no | *"lives up in the kelp forest … the sea-farm's pest and its pollinator"* — the flagship clinger on the flagship plant, at animal scale |
| `RM_Nuudal` 0.6 | none | `RM_Nuudal` — long soft floor grazer, spd 1.0, grazes thessmoss/murrgrave | 2~5 | no | *"moving through the fall like cattle through a snowfall"*; spawns on bank silt |
| `RM_Aluun` 0.6 | none | `RM_Aluun` — sessile (spd 0, `doesntMove`-style) on oruvell stems; the Grey's `RM_Hessal` bed shape | 1 (placed per stem) | **pale gold, radius 2** | *"a column of small windows"* — the aluun-hung kelp tower is the biome's postcard |
| `RM_NoolimCatch` 0.8 | `RM_Noolim` ✅ | (built) | 5~15 | none today | see §10.2-4 |
| `RM_Kellu` 1 | none | `RM_Kellu` — the kelp squid; predator, `maxPreyBodySize` 0.3 (the clinging layer and niim); hides in kelp | 1 | no — *"forest-dark"* | butchering gives `RUT_LampBlack` as well as meat (the rare table already gives it on the line) |
| `RM_Murrol` 0.8 | none | `RM_Murrol` — channel eel; spawns ON channel cells; current-exempt (§2.2); `Wildness` very low | 1~3 | no | *"so slow that bank-harvesters pick them up by hand"* — hunting it is trivial by design |
| `RM_Hollu` 0.8 | none | `RM_Hollu` — the bell; slow drifter, contact sting (the engine field for a melee-tool hediff is UNMEASURED here — check before authoring) | 1~4 | faint, radius 1 | *"forms on the underside of the mat, in the ceiling gardens, and lets go"* — the ruled canopy keeps its gardens, so the hollu keeps its birthplace; on the floor it is a fallen bell being eaten by nuudal, or a drifting one still stinging |
| `RM_Oobo` 0.4 | none | `RM_Oobo` — ambush predator; lives at oruvell tops; `maxPreyBodySize` 0.5 | 1 | no | *"hunts by letting go — a soft, wide-armed drop"*: on a 2-D floor the drop is an ambush from a kelp cell; its home is the ceiling gardens (kept by ruling) and the kelp crowns |
| `RM_Liiru` 0.5 | none | `RM_Liiru` — ribbon, slow (spd 1.2), upright S-curves | 1~2 | **continuous line, radius 2, blue-white** | *"as if someone had drawn on the water"* — tameable, the walking lamp of §6.4 |
| `RM_WeloonCatch` 0.4 | `RM_Weloon` ✅ | (built) | 1~3 | none | — |

**Plus the four new catchables from the clinging layer** (skerrin, ulloo, vessik, kiruun,
§4) — each owes a `*Catch` twin, which puts the Twilight at **16 catch entries**, the
richest table on the planet, which is what *"prolific"* asks for and what the sheet's §7
(*"the only ordinary fishing on the planet"*) promised.

**BENCH NOTE — "unlimited."** Odyssey fishing is a per-water-body population that regrows
toward `maxFishPopulation` (700 here, already the highest of the four seas). *"Unlimited"*
can mean (a) *never runs dry in practice* — a very high cap and fast regrowth, no C#; or
(b) *literally cannot be depleted* — a patch that pins the population. Position: (a),
with a Mod Setting for (b). Flagged (§10.2-5) because it touches sheet §7 and the
standing economy of the other seas, where the catch is finite by design.

**BENCH NOTE — where the fishing happens (engine, MEASURED this pass).** The floor pocket
map has **no water cells** — `RM_SeaFloorTerrain` paints `RM_SeaFloorGround` everywhere
and the standing note on the GravTide precedent says it outright: *"the water is the
ceiling, not part of the map."* Odyssey fishing zones need water cells. So today the
Twilight's twelve catches are reachable only from a coastal LAND tile's shore water,
where `mandrake.rm.seashores` (`RM_SeaShoresHarmony.RM_Patch_SetFishTypes`) hands the
sea's `fishTypes` to the shore's water body. **On the floor, nothing is fishable.** The
fix is the design, not a workaround: **make the skylight columns literal water** — a
shallow, walkable, saltwater terrain (`RM_ShaftWater`, the shape of vanilla
`WaterShallow` with `waterBodyType Saltwater`) painted under every skylight glower, so
that *"nets in the light columns"* (sheet §7) is exactly what the player does: a fishing
zone on the lit cells. `WaterBody.SetFishTypes` then reads `map.Biome.fishTypes`, which
on this map IS `RM_TwilightSea`'s table — no patch needed there (UNMEASURED whether a
pocket map's `WaterBodyTracker` builds bodies at all; it is a map component on every
map, so it should; verify in a quicktest before relying on it). The banks are harvest;
the shafts are fishing; the bed is the current. Three grounds, three verbs.

## 6. The bioluminescence system

> "Creatures tend to have luminous balls, bladders, or patches of bioluminescent organisms within them, making the place dim but well populated by local illumination plus the moving patches from the shafts of golden light."

### 6.1 The design language, shared across every species

**BENCH NOTE.** His sentence gives three *forms* and one *rule*, and both become the art
brief for every lit thing in this biome:

- **Three forms, each a shape on the silhouette, never a glow-outline:** a **ball** (one
  sphere — noothelm's bulb, the waelune, a pallu's mat, a piip); a **bladder** (a
  translucent sac on a stalk or rope — hoolimbre, the lanternwhale's *"blue lantern
  tendrils"* which are exactly this); a **patch or line** (an organ *inside* the body seen
  through skin — niim's dot-line, liiru's unbroken line, aluun's mantle, the kiruun's
  dust, the thurrim's faint patch). The light comes *from an organ with a place on the
  body*; a sprite that simply glows all over is wrong.
- **Three colours, and they mean something:** **pale gold** — the sessile and the
  harvestable and the Compact's own lamps (aluun, hoolimbre, noothelm, the lanternwhale's
  tendrils lean gold-blue, the skylights themselves); **blue-white** — the swimmers (niim,
  liiru, kiruun, thurrim); **green** — the plant symbionts (pallu's mat, waelune, the
  vaalstone sheen where a shaft hits it). A diver reads a light's colour before its
  shape: gold is home and harvest, blue-white is moving, green is growing.
- **The rule:** *dim but well populated by local illumination*. The base light is low
  (§7.1); everything a diver sees, they see because something alive is lighting it.
  Darkness here is *between* lights, never empty — the sheet's §9 *"darkness between,
  busy and alive"*. Sheet §9 names *"the two warm sources"* (skylights, Compact lamps);
  this drop adds a third — the creatures — as detail under the sheet's own "busy and
  alive." Flagged for the record (§10.2-6), position: additive.

### 6.2 What it means mechanically — MEASURED against the engine this pass

- **Plants glow for free.** `CompProperties_Glower` on a plant `ThingDef` is shipped
  practice in our own tree (`RM_DeepFlora.xml` carries three, radius 3–4). Hoolimbre,
  noothelm, and the vaalstone-in-light use it directly. **The glow can breathe:**
  `CompGlower.GlowRadius` has a public setter and `ForceRegister(map)` is public, so a
  tiny ticker on the plant can nudge radius ±0.5 over a minute and the light *pulses*
  the way a living lamp should. Cheap, and it is the whole difference between a lamp and
  an organism.
- **Creatures can glow, with one caveat.** `CompGlower.ShouldBeLitNow` (read in full,
  `Verse/CompGlower.cs`) requires only `parent.Spawned`, flick-state and any
  `IThingGlower` veto — nothing in it is building-specific, `PostSwapMap` handles map
  changes, and it guards `parent.BeingTransportedOnGravship`. So a `CompProperties_Glower`
  on an animal race is legal XML. ⚠️ **The caveat, from the same code: the comp registers
  its light at `parent.Position` when it turns on and nothing in the comp re-registers on
  movement.** A glowing pawn that walks will leave its light where it was lit unless
  something calls `ForceRegister` when its cell changes. That is one small C# tick (a
  `ThingComp` subclass of `CompGlower` that checks `parent.Position` against its last
  cell each rare tick) — owed once, in `mandrake.rm.terminalbiomes`, shared by every
  glowing creature on every sea. UNMEASURED whether any vanilla pawn already does this
  (no vanilla animal carries a glower in the defs read for this pass; the nociosphere
  does not). **Build the moving-glower comp before the first glowing creature, or the
  niim shoal will paint the floor with stranded lights.**
- **Performance is the real limit, and it is a setting.** A niim shoal of 14 glowers,
  three aluun per kelp stem across forty stems, piip by the dozen — the glow grid is
  recomputed per glower change. Position: creatures below bs 0.05 (piip, kiruun) glow as
  a *group light on their host* (the hoolimbre's radius already includes the piip; the
  murrgrave lace carries the kiruun's light as a plant glower), and only bs ≥ 0.06
  species carry their own comp. A Mod Setting **"creature bioluminescence"** (on / hosts
  only / off) is required by the standing Mod Settings rule, and "hosts only" is the
  safe default until measured.
- **Dark-adaptation** is not an engine thing and does not need to be: `growMinGlow`
  gates the plants to the shafts; pawn work speed and mood already respond to light
  level; the floor's *dimness* is a sky-colour choice (§7.1) and the *illumination* is
  the glow grid. The two compose without a new system.

### 6.3 The skylights — his strongest visual, and a glower thing, roof-mechanism unchanged

> "The skylights should show up as literal golden shafts of long beautiful light reaching down to the sea floor."

**BENCH NOTE.** A skylight is **a placed thing with a large golden `CompGlower`**
(`RM_Skylight`, an invisible or near-invisible 1×1 "building" the floor generator scatters
in three to six clusters, radius 8–12, colour the palette's lamp gold). That single
choice does most of the biome's work at once: the kelp grows only there (`growMinGlow`),
the pallu and niim spawn only there, the fishing water is painted there (§5), pawns'
light-based mood and work read it, and *"the moving patches from the shafts"* are the
glower's radius breathing (§6.2) plus its slow drift. **The shaft itself as ART** — a
tall golden column reaching down — is a separate render: a `Graphic` on the skylight
thing drawn at a high altitude layer with a long translucent gold texture (the vanilla
shaft-of-light idiom is a mote/overlay; the exact drawing route is UNMEASURED and is the
one art-engineering question in this drop, worth a mockup before a def). The fiction, by
the ruling in §2.1: a hole in the waveglass, rimmed pale with new growth. **Drift** (sheet
§3, ban 5): a `MapComponent` that, on a years-scale timer, despawns one skylight and
spawns another elsewhere — the kelp under the old one dies over a season, the Compact's
claim-buoy there expires (§8.1), and the *charts age*. Mat-stays makes this the
gardener's doing (§7.3).

### 6.4 What a colonist can harvest or tame for light

Light is the Twilight's export the way salt is the Grey's. Six routes, cheapest first:

1. **Lamp-bladders** (`RM_LampBladder`, from hoolimbre §3.3) — an item with its own
   `CompGlower`, radius 2–3, rots in ~6 days. Carry it, drop it, and the cell is lit: the
   biome's torch, and a trade good the surface has never seen.
2. **A sown sea-lantern** (noothelm §3.4) — plant light where you want it. Slow, permanent,
   and it is how the Compact lights a doorway.
3. **Aluun panes** — the catch item's own line: *"the valves, dried, are the lantern-panes
   in every deep dock."* A buildable `RM_AluunLantern` (a standing lamp costing aluun
   valves, no fuel — the pane holds a living mantle — `CompGlower` gold, radius 5). The
   Compact's lamp, buildable by the player once they have caught enough aluun.
4. **A tame liiru** (§5) — `Wildness` 0.3, trainability none: a ribbon of light that
   follows a handler. The one pet on the planet that is also a lamp.
5. **A kept waelune** (§3.7) — a rolling green light in the yard, the children's animal.
6. **Vaal-green and lamp-black** (§3.10) — not light, but the two pigments the Compact
   draws its lit world in; sold together.

**Tier note:** every item above is invented and `RM_`; none needs the Utinni layer.

## 7. Lighting-only weather, and the whale's shadow

> "The only weather on the sea floor are lighting condition changes due to water opacity and occasional clouds/large creatures above you. The shadow of the great whale analog would be welcome."

### 7.1 The weather set — four lighting states, nothing falls

**BENCH NOTE — engine, MEASURED.** A `WeatherDef` with `rainRate`/`snowRate` 0 and no
overlay changes nothing but the sky (`skyColorsDay/Dusk/NightEdge/NightMid`:
`sky`, `shadow`, `overlay`, `saturation` — vanilla `Fog` is the shipped example of a
weather that is mostly a sky change), and `SkyManager.CurrentSkyTarget` composes the
current weather's sky with game conditions and `CompAffectsSky` things (read in full,
`Verse/SkyManager.cs`). The floor pocket map's base sun glow comes from the parent tile's
longitude/latitude (`GenCelestial.CelestialSunGlow(map.Tile)`) — the terminator's fixed
sunset — and the biome does not set `disableSkyLighting`, so weather sky colours DO apply
on the floor. `WeatherDecider.CurrentWeatherCommonality` reads `map.Biome.baseWeatherCommonalities`
and, since `RM_TwilightSea` is impassable and background, **the only map carrying this
biome is the floor** — the Grey's `RM_GreySaltSnow` shipped on exactly that reasoning.
So: replace `Clear 12 / Fog 7 / Rain 4` with four `RM_` weathers, all lighting-only:

| weather | what it is | sky | other fields |
|---|---|---|---|
| **`RM_TwilightClearWater`** (common) | the water is clear; the shafts stand at full gold | sky dim green-gold, saturation ~1.0 | the default; skylight glowers at full radius |
| **`RM_TwilightSilt`** (common) | a silt load in the water — opacity up | sky darker, saturation 0.8, `accuracyMultiplier` 0.7 (fog's idiom) | the shafts shrink (a `GameCondition`-free hook: the skylight ticker reads the current weather and pulls radius to 60%) |
| **`RM_TwilightBloom`** (uncommon) | a plankton bloom under the lid — the water itself faintly luminous green | sky brighter, green-shifted, saturation 1.1 | the one *bright* weather; the pallu stack thick; a fishing bonus is a position, not a promise |
| **`RM_TwilightOvercast`** (uncommon) | *"occasional clouds … above you"*: cloud over the terminator dims every shaft at once | sky darker, gold gone grey-green | the shafts at 40%; the floor lit almost entirely by the creatures — the bioluminescence weather |

All four: `favorability Neutral` (the Grey's note: below Neutral is refused for the
first 8 days), `ambientSounds` the sheet's §9 water-noise. The `Rain` defect goes in the
same change, removed not annotated.

### 7.2 Passing shadows — the small event

*"large creatures above you"* and the ummarel rafts (§3.6) are the same mechanism at two
sizes: **a thing with `CompAffectsSky`.** MEASURED: `CompAffectsSky` (`Verse/CompAffectsSky.cs`)
exposes `StartFadeInHoldFadeOut(fadeIn, hold, fadeOut, target)` and the sky manager
lerps every such thing's `SkyTarget` into the current sky; vanilla uses it on the
orbital-strike ethereal things (`Defs/Core/ThingDefs_Misc/Ethereal_OrbitalStrikes.xml`)
to flash the whole map. Here the target is *darker*, not brighter: an invisible
`RM_PassingShadow` thing spawned by a small incident, fade in 200 ticks, hold 300–900,
fade out 200, sky darkened ~30%. A raft passing is small and frequent; a large creature
passing is bigger and rarer. **No C# beyond an IncidentWorker that spawns the thing and
calls the fade.** ⚠️ This darkens the *whole* map — it is *"a cloud over you"*, not a
shadow *moving across* you; the moving version is 7.3.

### 7.3 The whale's shadow — the marquee event

> "The shadow of the great whale analog would be welcome."

**BENCH NOTE.** The great whale analog is the **lanternwhale** (`RM_Lanternwhale`,
invented, already the sheet's gardener, already on the roster at 0.005 as a floor
resident). The shadow is the same creature seen the other way: *above* the map, passing
over the lid, tending it. Two grades, build the first now:

- **Grade A — the darkening (buildable from vanilla today).** An `IncidentDef`
  `RM_GardenerPasses`: the whole floor dims over ~10 seconds (7.2's mechanism at full
  strength, hold ~1500 ticks), the sheet's *"far slow calls through the roof"* play as a
  `SoundDef`, a letter says the gardener is overhead. Then — **because the waveglass stays by
  ruling, the gardener's passing does something:** on a fraction of passes, **a skylight
  moves** (§6.3's drift fires now rather than on its timer — the gardener *opened a well*
  or *let one close*). A diver who sees the shadow and then sees a shaft go dark has
  watched the roof being tended. That is the sheet's §4 gardener line as an event, and it
  is the one place in this drop where the ruled canopy earns its keep mechanically.
- **Grade B — the moving shadow (art + small C#).** A vast soft-edged dark shape that
  crosses the floor over ~30 seconds — a `MapComponent`-drawn overlay (a huge translucent
  texture at the weather-overlay altitude, moved each frame) or a chain of large
  shadow-motes. UNMEASURED which drawing route the engine makes cheap; the vanilla
  skyfaller shadow is the nearest idiom but is per-thing and small. Worth a mockup with
  the owner watching, since it is a *look* — and it is the moment the biome sells itself.
  When it exists, Grade A's dimming becomes its accompaniment rather than its substitute.

**Never true in either grade:** the whale is not *on* the floor during its shadow (the
floor-resident lanternwhale is a different encounter — the gardener come down to
graze, sheet §4), the shadow harms nothing, and it is never a raid or a threat letter.
Ban 2 is served, not touched: the shadow is the roof's keeper going about its work.

**Roof-independence of §7:** 7.1 and 7.2 need no roof at all; 7.3's skylight-move is the
ruled-canopy branch and is written for it.

## 8. Unique content — what makes the Twilight memorable

> "Now, we need some really great unique contents here to keep up with the Scald and Grey. What could be down here? I'm thinking it will be in the plants and animals that are present more than minerals. This is a settled sea by the Deepwater faction, so they would have cleaned up most of the scavenge and open mineral wealth lying about."

**BENCH NOTE — the one sentence.** The Scald's wealth is *heat and steam* (a walker's
chitin, a vent, a steam-devil); the Grey's is *dead and jacketed* (salt, crystal, statuary,
an Elder's hoard — everything valuable there has stopped moving and been sealed). **The
Twilight's wealth is alive and must be kept.** Nothing here can be dug up and carried
off; every valuable thing is a plant that must be grown, a creature that must be caught
or tamed, a light that must be fed, or a right that expires. The designed absence he
named — *"cleaned up most of the scavenge and open mineral wealth"* — is what makes
that true: the Compact took the dead wealth generations ago, and what is left is the
living kind, which cannot be taken, only tended. That is the biome's argument against the
Grey, and it is the argument the sheet already made (§8: *"an ark, kept"*). Six pieces
of content carry it, biased to flora and fauna as he asked; none is a mineral, and the one
"scavenge" entry is a picked-clean wreck that says so.

### 8.1 Skylight rights — light as expiring real estate

The sheet's §7 promised it; this is the mechanism. A skylight (§6.3) is the only place
kelp grows, pallu stack, niim school and nets work — it is the biome's arable land and
fishery in one, and **it moves** (ban 5). The Compact **claims** them: a `RM_ClaimBuoy`
(a small lit building the bottom-houses' cast places at each shaft they hold; Grade A of
§7.3 can retire one when the shaft moves). A player who sows or fishes inside a claimed
shaft without a right takes a **goodwill hit** with `RUT_Jawa_DeepwaterCompact` (their
one sanction — they never raid, ban 4); a player who **buys a right** (a `RM_SkylightRight`
item, sold by the bottom-house dealer, priced by the pallu count — *"The Compact counts
them to price a skylight"* — and **expiring when the shaft drifts**) farms and fishes it
freely. The player *can* place their own buoy on an unclaimed shaft and hold it. Engine:
a buoy is a building with a comp that tags the shaft's cells; the right is an item with a
`CompProperties_` expiry keyed to the skylight's id; the sanction is a goodwill change on
a job's completion inside a tagged cell. **Medium C#**, and the most "unique" mechanic in
the drop — nowhere else on the planet do you rent light.

### 8.2 The three grounds — bank, shaft, bed

The floor is legible as three kinds of ground and three verbs, which is the content of
his *"channel-patterns in the terrain"* now that ban 3 is ruled live (§2.2):

- **The bed** (`RM_ChannelBed` terrain) — mud-coloured, dry-looking, braided; the current
  runs in it (§2.2); murrol and waelune ride it; nothing grows on it. **Verb: avoid** —
  or cross at the marked fords the Compact keeps (a 1-cell `RM_FordStones` building that
  cancels the push on its cell: the houses' cast built them, and the player can build
  more from lattice-timber).
- **The bank** (`RM_BankSilt` terrain, **fertile**) — the strip between the stake-line and
  the bed: thessmoss turf, murrgrave lace, nuudal grazing, kiruun light in the silt, and
  the **only sowable ground on the floor** (oruvell, illuvane, noothelm plots). The sheet's
  *"the banks are the wealth"* made literal by a fertility number. **Verb: harvest, sow.**
- **The shaft** (`RM_ShaftWater` terrain under each skylight glower, §5) — shallow,
  walkable, fishable, lit gold; the oruvell towers stand in it hung with aluun; the niim
  flash through it. **Verb: fish.** The Compact's nets (`RM_FishingNet`, a building costing
  net-cord §3.11 that raises the zone's yield, if the engine allows; otherwise a
  `Zone_Fishing` and nothing more) stand at the shaft's edge.

Everywhere else is `RM_SeaFloorGround` in the dark between — skirroth tangles, kellu,
the loohn, and the slow lights of the hoolimbre at the shaft edges. **Generation:** one
Twilight dressing genstep (the Grey's `GenStep_GreySeaFloorDressing` is the precedent
and the scope lesson — listed on this generator only, refusing any map whose biome is not
`RM_TwilightSea`): elevation → channels with flow field (§2.2) → banks either side →
skylight clusters on the high, dry ground → shaft water under them → stake-line on the
banks → then the vanilla `Plants` step (which the generator does not list today and must).

### 8.3 The kelp farm — the sea-farm the dayside can never have

Sheet §7, *"kelp agriculture."* Bank silt (§8.2) is fertile; oruvell, illuvane, noothelm
and sarrowhisk are sowable (`sowTags` on a Twilight-only tag the bank terrain carries);
the tikkarr is the farm's pest-pollinator (§3.1); the aluun is the farm's second crop (it
grows on the kelp you plant — a sessile creature seeded beside a mature sown stand by the
same adjacency rule as the clingers, §4). A kelp farm, a lamp-bladder bed and a
fishing net in one rented shaft is a working colony on the sea floor with nothing dug
from the ground. The gravship makes it possible (ship-only access): the farm is where you
parked. **No new engine** beyond the bank terrain's fertility and sow tags.

### 8.4 The living light trade

§6.4 in one line: the Twilight exports light — lamp-bladders, aluun panes, sea-lanterns,
a tame liiru — and pigment (vaal-green with lamp-black). Trade tags on each so the
Compact's water-caravan (the FactionDef's `Trader` group already exists) carries them to
the surface, where a lamp that is alive has never been seen. **No new engine.** This is
the answer to *"what could be down here"* that is not a mineral: **the only light on the
planet that grows.**

### 8.5 The gardener's passing and the ark's keepers

§7.3 Grade A/B (the shadow, the well that moves) and §9 (the houses) are the two
set-pieces; together they are the sheet's reveal — *"the surface world knows them as
sellers of water; only those who dive learn what the water bought."* Content, not
mechanism: the bottom-house cast's hooks are written *about* the gardener and the wells
(§9.3), so a player who talks to them learns the roof is tended before they ever see the
shadow, and the shadow then means something.

### 8.6 The wrecks of the impatient — the designed absence, shown

Sheet §8 names *"the wrecks of the impatient"*; his drop says the Compact cleaned the
scavenge out. Both are true at once: **one or two `RM_PickedWreck` things per floor** —
a hull-rib or a stripped gravship spine, vaalstone-crusted, aluun growing on it, with a
Compact **salvage-mark** painted on it (a lamp-black glyph) and *nothing inside*. Its
inspect string says who took it and when. It is worth 0 silver and it is the most
eloquent object on the floor: the dead wealth was here, someone with a ledger got to it
first, and what is left is growing on it. **No engine** — a building with a description.
⚠️ Not a loot container, not a minable, not a quest hook; if it ever holds anything, the
absence stops being designed.

**What is deliberately NOT proposed:** no mineral node, no salt, no crystal, no
harvestable rock, no Elder, no hoard, no locked treasury. A player who wants to *mine* the
Twilight finds nothing, and the biome's whole personality is that they should stop
looking down and look at what is lit.

## 9. The Deepwater houses

> "There could even be inhabited-injected Deepwater faction houses here of the appropriate races (very cool!)."

### 9.1 What is ALREADY BUILT — MEASURED 2026-09-26 (he assumed some of this was new)

- **The Inhabited system exists and is v1 code**, `mandrake.rm.inhabited`
  (`src/RimMandrake/Inhabited/`): persistent rosters of real pawns on a `WorldObject`
  (`WorldObject_Inhabited.roster`, recalled on map removal via `Patch_MapRemoval`), a
  daily routine (`LordJob_Inhabited` / `LordToil_InhabitedRoutine`: home spot, work spot,
  sleep hours from the place def), a larder and a trade stock put on the ground as real
  things (`GenStep_InhabitedStock`), fates (`Resident` / `FleeIfThreatened` …), a
  gate-search hook, and a security profile. **Design authority:**
  `design/Jawa/bridge/INHABITED_DESIGN.md`.
- **A Deepwater cast of 25 characters exists** — `Defs/CastRosters/CastRoster_DEEPWATER.xml`,
  generated from `design/Jawa/bridge/INHABITED_CAST_DEEPWATER.md` by `cast_to_xml.py`
  (do not hand-edit the XML). Places: DEEPWATER HOLD (9), BUTORA (8), TIDEWATCH (8).
  Races, as the prose carries them: Mon Calamari, Quarren, Nautolan, Selkath, Gungan,
  Herglic, Chagrian, Bith, Duros, human. These are the *"appropriate races"* — and the
  FactionDef's `xenotypeSet` (`RUT_Jawa_DeepwaterCompact`: Mon Calamari / Nautolan /
  Quarren 0.222 each, Chagrian / Herglic / Selkath 0.074, five more at 0.022) is the
  same list with weights.
- **A Deepwater settlement manifest and its four district templates exist** —
  `SettlementManifestDefs_DeepwaterHold.xml` (cistern hall, gate bastion, hospital ward,
  hydroponics bay) with `Templates/deepwater_*.txt`, on **tile 2919, a surface
  AridShrubland shore tile** — the Hold is a *surface* seat and stays one.
- **A water-hold place archetype exists** — `RM_InhabitedPlace_WaterHold` (`Resident`,
  larder meals + medicine, stock silver + medicine + potatoes).
- **The faction never raids** — `raidsForbidden true`, *"IS THE FACTION"* in the def's own
  header. Ban 4 is engine-enforced already.

⇒ **The houses are mostly a WIRING job, with one real gap.** What exists: the people
machinery, the faction, the races, the archetype pattern, the template engine. What does
not: any of it reaching a **pocket map**.

### 9.2 The gap, precisely — and the two honest shapes

`GenStep_InhabitedCast.Generate` (read in full) finds its cast by
`Find.WorldObjects.WorldObjectAt<WorldObject_Inhabited>(map.Tile)` and does nothing if
none is there. The wilderness route reaches the genstep only through a `TileMutatorDef`'s
`extraGenSteps` (`RM_InhabitedPlace` names `Inhabited_Cast` + `RM_InhabitedStock`). The
floor generator already delivers mutators to the pocket map via
`pocketMapProperties/tileMutators` (`RM_SeaFloorHabitat` rides exactly that), so
**adding `RM_InhabitedPlace` there is one XML line** — ⚠️ UNMEASURED whether
`MapGenerator.GenerateMap` honours a *pocket-map* mutator's `extraGenSteps` the way it
honours a tile's (the shipped comment says it concatenates *every active mutator's*; a
quicktest settles it in a minute). Then the tile question:

- **Shape (a) — a `WorldObject_Inhabited` per Twilight tile the player can dive on.** The
  genstep works unmodified; the cast is per tile and persists per tile (dive the same
  tile, meet the same people — the *"wasn't that guy …"* test passes); but 479 sea tiles
  is not a hand-placement, so a `WorldComponent` that lazily creates the world object the
  first time a hatch opens on a tile, from a Twilight-floor manifest. Small C#.
- **Shape (b) — a biome-keyed lookup.** A subclass of the genstep that, when no world
  object sits on the tile and `map.Biome == RM_TwilightSea`, resolves a single
  planet-wide "the Bottom" place. One cast for the whole sea; simpler; but every dive
  anywhere meets the same eight people, which is either *the Compact's bottom-warden
  circuit* (fine fiction: they move between holdings) or a tell that the sea is one map.

**Position: (a)**, because persistence-per-place is the Inhabited system's entire point
and (b) throws it away to save a component. Either way, **the cast and stock machinery
run unchanged**. Q10 asks.

**Then the structures.** The settlement path composes districts from templates
(`GenStep_ComposeSettlementDistrict`); the wilderness path places *nothing* today — the
genstep's own header: *"A placeholder anchor until the PLACE layer — the tile mutator
that actually builds the refinery — can hand over the real one."* So the houses' fabric
is new either way: a **Twilight floor-house genstep** (or a district template the pocket
generator can run) placing **2–4 low domes** (sheet §9: *"low domed dwellings with lit
doorways"*) on a bank, of lattice-timber walls and aluun-pane windows (`CompGlower`
gold), a ghallowyn column or two, three noothelm at each door, a claim-buoy in the
nearest shaft (§8.1), a kelp plot on the bank (§8.3), bank-stakes along the channel
(§2.2), a ford. The Grey's dressing genstep is the placement precedent; the four
`deepwater_*.txt` templates are the fabric precedent (a fifth, `deepwater_bottom_house`,
is the natural addition to the same library). **Small-to-medium C#**, mostly placement.

### 9.3 The cast — proposed roles and hooks, in his prose's register

**BENCH NOTE.** The cast rosters are the owner's, written as prose in
`INHABITED_CAST_*.md` and generated from there; these are **proposals for a new section
of `INHABITED_CAST_DEEPWATER.md`** — place **THE BOTTOM** (or per-tile: *"the
Nine-Well Bank"*, *"Low Lantern"* — each holding's name is a chart name) — for him to keep,
cut or rewrite. Six to eight residents, `Resident` fate, of the amphibian races
(Mon Calamari, Quarren, Nautolan, Selkath, Gungan first; the others rarely — a Bith on
the bottom is a story). Roles the floor needs, each with a hook that teaches the biome:

- **the well-keeper** (Nautolan, f, 50s) — reads the skylights; keeps the chart of which
  wells are opening and which closing, in lamp-black on vaal-green vellum; has been wrong
  once in thirty years and it cost a family its plot. She prices rights (§8.1) and
  will not sell one on a well she thinks the gardener is closing, and will not say why.
- **the gardener-warden** (Selkath, m, 60s) — the one whose work is the roof: he watches
  the lanternwhale and logs its passes (§7.3); he has never touched it; the Compact's
  law about the gardener is his to keep and he has decided it is the only law that
  matters. He knows the shadow before it falls and stands outside to watch it every time.
- **the net-widow** (Quarren, f, 40s) — fishes the shaft alone since her partner walked
  into the channel to save a net; she keeps the ford stones (§8.2) repaired and adds one
  every year, and will tell a diver exactly where the edge is, once, and never again.
- **the lamp-wright** (Mon Calamari, m, 30s) — makes aluun-pane lanterns and lamp-bladder
  strings; the bottom's dealer (trade is a ROLE — `INHABITED_DESIGN.md` §1); sells light,
  pigment and, quietly, one skylight right the well-keeper does not know he holds.
- **the child** (Gungan, 9) — the waelune-chaser; the one who knows where the piip are
  thickest; the player's first sight of a Compact person on the floor should be a child
  with a light in each hand, because *"It's a pretty ocean."*
- **the bank-farmer** (Quarren, m, 60s) — the kelp plot; hates tikkarr and will not kill
  one; measures a good year in ghallowyn rings.
- *(optional)* **the diver who stayed** (human, f, 40s) — an outlander who came down on a
  ship years ago and never went back up; the bridge between the player and the cast, and
  the one who says out loud what the others will not: that the Compact keeps the last
  ordinary sea and the surface has no idea.

### 9.4 Tier and ownership

The **structures, the place archetype, the buoy, the stakes, the ford, the lanterns** are
invented and franchise-free — `RM_`, in `mandrake.rm.terminalbiomes` (or
`mandrake.rm.divinginteraction` where shared across seas). The **cast and the faction**
are campaign content — `RUT_Jawa_DeepwaterCompact`, Star Wars races (`RSW_`), the
`INHABITED_CAST_DEEPWATER.md` prose — and live in the Utinni layer, patched onto the
`RM_` place by `MayRequire`, exactly as the Hold does today. A free-tier player gets the
houses, lit and empty or with a generic `RM_` water-people cast; the campaign gets the
Compact. Ban 4 holds by the FactionDef; the houses are `Resident` and never a war camp.

## 10. Against the frozen sheet

`the_twilight_deep.md` is 🧊 FROZEN (`BIOME_FREEZE_FABLE_REVIEW_1`, 2026-09-07):
amendments add detail, never change a ruling; the unfreeze is his call at a sitting. Read
against every section of the sheet, and against `terminator_sea.md` where the sheet
inherits it (surface and shore only, by the sheet's own scoping line), the drop and this
document sort as follows. **BENCH does not resolve any FLAG below.** The two rulings of §2
are recorded where they land.

### 10.1 Additive — lands under the sheet as written

| item | sheet hook | why it is additive |
|---|---|---|
| the waveglass (§2.1) | §0 *"the waveglass is the mechanism"*, §1, §3, §4 | **RULED 2026-09-26 (card, then the name typed):** the roof stays, reskinned; every mechanism the sheet hangs on it is untouched; the word changes |
| fourteen seaweeds (§3) | §4 *"the kelp forests — real plant life … food, fiber, and the wet lattice-timber"*; §7 kelp agriculture | the sheet named kelp and promised three products; this supplies fourteen forms and the three products by name. Nothing here touches a ban: ban 6 holds (all invented), and the surface bans on lush/open-close flora are scoped away from the floor by the sheet itself |
| the clinging layer (§4) | §4 *"the abundance around them — the roster pass populates generously here"* and *"yes, and another"* | the sheet's one explicit license to be generous |
| fish bodies for ten catches (§5) | §4 the shoals, the river-fauna; §7 fishing | the standing every-fishable-lives rule, applied |
| bioluminescent creatures (§6) | §9 *"darkness between, busy and alive"*; already shipped in four catch descriptions | a third light beside the sheet's two (flag 6 for the record) |
| skylights as glower things (§6.3) | §3 ⭐ the skylights; ban 5 | the engine shape of a ruling already made; drift is kept |
| lighting-only weather (§7.1) | his drop; the sheet has no weather section | pure addition; removes a vanilla `Rain` that was against the surface ban anyway |
| the whale's shadow (§7.3) | §4 the gardener *"tends the roof"*; §9 *"the gardener's vast gentle bulk at the ceiling"* | the gardener's work as an event; ban 2 served |
| skylight rights (§8.1) | §7 *"skylight rights — bright columns as claimable, contestable, expiring real estate; the Compact meters them"* | the sheet's words, mechanised |
| bank / shaft / bed (§8.2) | §3 the rivers *"their banks are the richest ground"*; ban 3 | **RULED 2026-09-26 (card):** the current stays live; banks are harvest; the design is written to the ruling |
| the picked wreck (§8.6) | §8 *"the wrecks of the impatient"* | the sheet's object, with his "cleaned out" applied |
| the Deepwater houses (§9) | §8 ⭐ *"their inhabited dwellings stand on the bottom … v1: the dwellings, plots, moorings and lamplight EXIST and are inhabited"* | the sheet ruled v1; this is the build shape. The v2 *entire settlement* stays v2 |

### 10.2 FLAGGED — needs his word; BENCH position given, not taken

1. **The waveglass's name and look** (§2.1) — **RULED 2026-09-26, owner typed:** *"love what
   you made but just call it waveglass"*. The look stands as drawn; *the lid / veil-fall*
   stand; the description rewrites are done (§2.1).
2. **The sink's consequence** (§2.2 item 3). Ban 3 says *"sinking with it"*; the ruling
   says the current carries a pawn. What happens at the end — a recoverable *sunk* state
   on the bank, or a lost colonist? **Position:** recoverable and dangerous, the Grey's
   encasement posture; a Mod Setting for harsher.
3. **How much the mechanism costs** (§2.2). It is medium C# with five interaction
   surfaces (pathing, hauling, downed pawns, animals, save/load). **Position:** build the
   terrain, banks and tells first (they are the *look* he asked for), the current second,
   and never ship the bed without at least the stake-line tell.
4. **Two silver shoals.** `RM_Niim` (*"the silver of the Twilight — the shoal fish"*,
   catch-only, the older and richer prose) and `RM_Noolim` (*"the silver-shoal analog …
   seen as a shoal, never as an individual"*, built with a body 2026-09-24) occupy one
   niche. The sheet's *"yes, and another"* makes two legal; but they read as one creature
   under two names. **Position:** keep both and **split them by light** — niim is the
   *lit* shoal of the shafts (blue-white dot-line, the one that flashes), noolim the
   *dark* shoal of the between (dull silver, no glow, what the loohn hunts). Then niim's
   *"one fast ordinary thing nobody has a good name for"* is the loohn, and the two shoals
   are the two halves of the floor. If he would rather one, noolim's body becomes niim's.
5. **"Prolific and unlimited"** (§5) vs sheet §7 and the other seas' finite catch.
   **Position:** unlimited-in-practice (high cap, fast regrowth) by default; a literal
   no-depletion patch behind a Mod Setting. He may mean the literal one.
6. **A third light source** (§6.1) vs sheet §9 *"the two warm sources"*. **Position:**
   additive — the sheet's own *"busy and alive"* darkness; but §9 is the artistic-theme
   section and he wrote it, so a word. **ANSWERED by his second drop the same day
   (§13.2):** cultivated living light — *"sphere colonies of microorganisms bright enough
   to be like sunlight"* — is his own third source. Additive; no ruling needed.
7. **The skylight as a real light and the shafts as real water** (§5, §6.3). Both are
   engine shapes for rulings already made, but they change what the floor *is*: kelp
   grows only in shafts; fishing happens only in shafts. **Position:** yes to both — it is
   the sheet's *"the columns are the light"* made checkable.
8. **One hazard plant in a pretty ocean** (§3.14). **Position:** one, low damage; if he
   wants none, the vessik loses its shelter and moves into the skirroth.
9. **The lanternwhale's rename.** The roster's `new_defs` row asks for *"'Twilight
   Gardener' endemic label"*; the def ships as `RM_Lanternwhale`. Not this document's
   question, but §7.3 names it *the gardener* throughout; **position:** label stays
   *lanternwhale*, the Compact calls it *the gardener*, both in the description.
10. **Houses: per-tile world objects (a) or one biome-wide cast (b)** (§9.2).
    **Position:** (a). And whether the bottom cast is NEW prose (position: yes, six to
    eight, §9.3) or the Hold's people descending (position: no — the Hold is a surface
    seat and its cast has surface hooks).
11. **Ban 2's object under the reskin** — *"no roof without the gardener"* stands by the
    ruling; but the gardener's job is now to tend the *waveglass*, and §7.3 Grade A makes
    the gardener *move skylights*. Is that too much agency for a placid animal?
    **Position:** it is exactly the sheet's *"keeping skylights open"*; keep it.

### 10.3 Roster consequences

`rosters/the_twilight_sea.json` is the owner's via BENCH, edited at a sitting; BENCH did
not touch it. It is stale against this drop and against the live def in four places:
`"flora": []` is now false (fourteen forms are proposed and the sheet's kelp was always
commissioned); the `new_defs` row *"the Twilight Deep set, DEFERRED to diving mods"* has
expired — the diving mod shipped (`RM_SeaDiveHatch`, the generators) and the Grey has
already been dressed under the same expiry; the `new_defs` row now reads *"the waveglass
(Twilight monoculture, shore-to-shore)"* (renamed 2026-09-26 under the ruling, its
`kind: plant` now stale against the shed-panel redesign); and the `fauna` list still carries nine `RSW_`/donor
imports (`RSW_Laa`, `RSW_OpeeSeaKiller`, `Yobshrimp`, `AA_ColossalAerofleet`, three
tumorfish stages, `RSW_AbyssalColo`, `RSW_CrimsonOpee`, `RSW_Starmaw`, `RSW_StormSando`,
`StoneCrab`) that are **not on the live def** (MEASURED: 6 `wildAnimals`) — the
2026-09-25 cast sitting replaced them and the roster was not brought forward. Not this
document's to fix; a sheet edit on his word.

## 11. Questions for the owner

Each with a BENCH position so a sitting can say yes or no. None blocks the smallest
steps in §12. Numbering continues §10.2's flags where a flag is also a question.

- **Q1 — The waveglass.** ✅ RULED 2026-09-26 (owner typed *"love what you made but just
  call it waveglass"*); *veil / lid / veil-fall* stand; the rewrites landed as one pass (§2.1).
- **Q2 — The sink.** ✅ RULED 2026-09-26 (card, danger pass C1): recoverable *sunk*
  state by default, harsher Mod Setting ladder up to lost.
- **Q3 — Niim and noolim.** ✅ RULED 2026-09-26 (card): TWO, split by light — niim the
  lit shoal of the shafts, noolim the dark shoal of the between; disentangle their
  overlapping prose before the fish-body wave ships.
- **Q4 — Unlimited fishing.** ✅ MOOT 2026-09-26, owner typed: *"you don't fish at the
  bottom of the ocean, I had meant the shoreline fishing."* Fishing is the SHORELINE's
  verb (the surface biome's catch, per the standing floor-and-catch ruling); the floor
  has no fishing at all — its fish are hunted and its beds gathered.
- **Q5 — Fourteen seaweeds.** ✅ RULED 2026-09-26 (ledger, gating rows): KEEP ALL
  FOURTEEN — twelve was a floor, not a ceiling.
- **Q6 — The clinging layer at six species.** ✅ RULED 2026-09-26 (card): six stands —
  tiny, half invisible until they move, abundance is the license.
- **Q7 — The whale's shadow.** ✅ Settled in substance: the five-beat sequence ships
  (second drop supersedes plain Grade A); Grade B's moving-shadow art stays gated on a
  mockup with him watching — a joint session, not a card.
- **Q8 — Skylight rights.** ✅ Designed under the week-drift ruling (light economy pass
  §4): short-term leases, first-refusal renewal, goodwill/access sanction ladder,
  never force.
- **Q9 — The shafts as water.** ✅ MOOT with Q4 (same typed correction): no nets on the
  floor. The shafts' value is light — farming, the well economy, the living abundance
  hunted and gathered there — not a fishing zone.
- **Q10 — The houses.** ✅ RULED 2026-09-26 (card): yes to all three — per-tile world
  objects, a new bottom cast of 6–8, §9.3's roles as the starting sheet for his prose.
- **Q11 — Waelune: plant or creature?** Position taken (BENCH, reversible at the sheet
  sitting): creature — the danger pass already treats it as a kept pet (D2).
- **Q12 — Mod Settings.** Position taken (BENCH, standing MOD_OPTIONS pattern): the
  proposed set ships with defaults = shipped behaviour; "unlimited fishing" drops out
  of the panel (moot with Q4 — fishing is the shore's, not this map's).

## 12. Build-order suggestion, smallest first

**BENCH NOTE throughout.** Ordered so each step ships something visible on its own.
Everything lands in `mandrake.rm.terminalbiomes` unless it is a mechanism shared across
seas (then `mandrake.rm.divinginteraction`) or campaign cast (then the Utinni layer).
The Grey wave's three silent-kill facts apply to every plant step here: the floor is
`fertility 0` (`completelyIgnoreFertility`, or the bank terrain), `plantDensity` must be
set on `RM_TwilightSea`, and the vanilla `Plants` genstep must be listed on the
generator.

| # | step | new defs (rough) | C# | needs | unlocks |
|---|---|---|---|---|---|
| 1 | **Fix the surface defect** — drop vanilla `Rain` from `RM_TwilightSea`; set `plantDensity`; list `Plants` on the generator | 0 (edits) | none | nothing | honesty; every later plant can spawn |
| 2 | **The four lighting weathers** (§7.1) | 4 WeatherDefs | none | 1 | the floor has a sky |
| 3 | **Skylights as glower things + shaft water** (§6.3, §5) — scatter genstep, `RM_Skylight`, `RM_ShaftWater`; the breathing-radius ticker | 2 ThingDef/TerrainDef + 1 GenStep | tiny | 1 | kelp has a place to grow; fishing has water; the biome's image |
| 4 | **The eight roof-independent plants that need no comp** — oruvell, ghallowyn, sennefan, thessmoss, murrgrave, vaalstone, illuvane, skirroth; `<wildPlants>`; `RM_LatticeTimber`, `RM_SeaSilk`, `RM_VaalGreen`, `RM_NetCord` items | 8 plants + 4 items | none | 3 | the floor is a forest |
| 5 | **The lit plants** — hoolimbre, noothelm (+ `RM_LampBladder`); the moving-glower comp (§6.2) built here, before any glowing creature | 2 plants + 1 item | small (moving glower) | 4 | the place lights itself; the lamp trade |
| 6 | **Ten fish bodies** (§5) + the moving-glower comp on niim/liiru/aluun/kiruun; a Twilight `GenStep_SeaFloorFauna` variant that seeds clingers beside hosts | 10 races + PawnKinds | small (adjacency seeding) | 5 | every catch lives; Q3 settles niim/noolim |
| 7 | **The clinging layer** (§4) — six races, four `*Catch` twins | 6 + 6 + 4 | none (reuses 6) | 6 | *"a lot of little creatures"* |
| 8 | **Bed, bank, stakes, ford** (§8.2) — terrains, `RM_BankStake`, `RM_FordStones`, the Twilight dressing genstep with flow field | 2 TerrainDefs + 2 ThingDefs + 1 GenStep | medium (channel gen + flow grid) | 3 | the three grounds; the tells exist before the danger does |
| 9 | **The current** (§2.2) — the drift `MapComponent`, `pathCost`, exemption ext, sunk hediff, warning, settings | 1 HediffDef + 1 modExt | **medium** — the one genuinely new movement system | 8, Q2 | ban 3 is a mechanism |
| 10 | **Kelp farm** (§8.3) — sow tags on bank silt, sowable oruvell/illuvane/noothelm/sarrowhisk, aluun seeded on sown stands | 1 plant + tags | none | 8 | the sea-farm |
| 11 | **Passing shadows + the gardener's passing** (§7.2–7.3 Grade A) — `RM_PassingShadow`, two IncidentDefs, the skylight-move hook | 1 ThingDef + 2 IncidentDefs | tiny | 3 | the whale's shadow, first grade |
| 12 | **Skylight rights** (§8.1) — buoy, right item, goodwill sanction | 2 ThingDefs | medium | 3, 11 | the unique mechanic |
| 13 | **The Deepwater houses** (§9) — place archetype, bottom-house genstep/template, per-tile world object component, `RM_AluunLantern`, the picked wreck; cast prose in `INHABITED_CAST_DEEPWATER.md` then regenerated | 1 PlaceDef + 3–4 ThingDefs + 1 GenStep + cast | small–medium | 8, 10, Q10 | *"very cool!"* |
| 14 | **The whale's shadow, Grade B** (§7.3) — the moving overlay | art + 1 MapComponent | small, art-led | 11, a mockup with him | the marquee |
| 15 | **Quellith + waelune** (§3.14, §3.7) and the sarrowhisk bait | 2 defs + 1 item | none (reuses Venomvine) | 4, Q8, Q11 | the last two plants |
| 16 | **The rewording pass** (§2.1) — eleven descriptions, the sheet's mat language at a sitting, the roster rows | 0 (edits) | none | Q1 | the prose matches the ruling |

**Rough count of distinct new defs the drop implies:** ~75–85. By category: flora 14 ·
plant products/items ~8 · fish bodies 10 (+ PawnKinds) · clingers 6 (+ 4 catch twins) ·
weather 4 · terrain 3 · skylight/shadow/buoy/stake/ford/lantern/wreck ~8 buildings ·
incidents 2 · hediff 1 · place archetype 1 · cast 6–8 characters. Zero of these exist
today (MEASURED, §0). The Grey's equivalent count was ~35–45; the Twilight's is roughly
double because it was ruled *"rich and varied as the land"* and because every fishable
owes two defs.

**Items BENCH thinks should be filed** (names in the project's grammar; BENCH files with
him, not this pass — §13 adds to this list at its end): `TWILIGHT_FLOOR_LIGHTING_1` (steps 1–3, 11), `TWILIGHT_SEAWEED_FLORA_1`
(4, 5, 10, 15), `TWILIGHT_FISH_BODIES_1` (6 — the Twilight portion of
`SEA_FISHABLES_ALIVE_IN_DEPTHS_1`), `TWILIGHT_CLINGING_LAYER_1` (7),
`TWILIGHT_CHANNEL_CURRENT_1` (8–9, carries Q2 and the interaction list),
`TWILIGHT_SKYLIGHT_RIGHTS_1` (12), `TWILIGHT_DEEPWATER_HOUSES_1` (13, carries Q10),
`TWILIGHT_WHALE_SHADOW_1` (14, joint mockup), `TWILIGHT_CANOPY_REWORDING_1` (16, gated on
Q1) — and a roster amendment at the next Twilight sitting (§10.3), a sheet edit on his
word, not an item.

## 13. Second drop, same day — farming, living light, living decor, the whale sequence

_Captured 2026-09-26, later the same day, after §0–§12 were written and pushed. Same
discipline: his words in the block quote are the authority; everything under a
**BENCH NOTE** is ours. Most of this is new material; where it answers a flag above, the
flag is marked answered in place._

> "I love the idea that there is a rich opportunity to farm down here. Underwater plants in either on traditional grow zones on the sea floor or even tethered like floating cube cages or sphere cages with a chain leading down to its tether on the surface. Show case technology for the Deepwater faction. Unique plants and capabilities. Huge variety for starwars cuisine mod. The idea that you can grow sphere colonies of microorganisms bright enough to be like sunlight to grow plants is very cool. Luminous vines the players can lay around to decorate after they're grown and harvested. underwater plants have the unusual property of staying alive after you "pick" them, so you can then decorate with a living plant easily. I love the shadow of the whale-analog leads to eerie booming sounds and little light... animals freak out... and then it starts raining detritus, parasites, barnacle analogs with glowing bits in them like gems. and the whole ecosystem goes into overdrive and starts eating them at great speed. I love that the floating farming doesn't use up surface space because it floats above you."

### 13.1 Farming — two routes, both ship

> "Underwater plants in either on traditional grow zones on the sea floor or even tethered like floating cube cages or sphere cages …"

> "I love that the floating farming doesn't use up surface space because it floats above you."

**Route 1 — floor grow zones** are §8.3 unchanged: bank silt is fertile, the Twilight's
sowables carry a Twilight sow tag, an ordinary growing zone works. Nothing new.

**Route 2 — tethered cages.** **BENCH NOTE.** His stated reason is the design: growing
capacity that **costs no floor area**, unique on the planet to a biome whose ceiling is
water. What that is in a 2-D top-down game:

- **The reading.** *"a chain leading down to its tether"* reads two ways — a buoyant cage
  chained DOWN to an anchor on the floor, or a cage hung from a surface float. The first
  is the one that lets a cage sit *above* anything (the current, a channel, a kelp stand,
  a house) and is the one designed here; the picture is the same from above either way.
  Q13 asks which he meant.
- **The engine shape — a `Building_PlantGrower` you can walk under.** The GlowTank
  (`src/RimMandrake/LuminousPigment/Defs/ThingDefs_Buildings/RM_GlowTank.xml`, MEASURED)
  is already a 2×2 `Building_PlantGrower` on the vanilla hydroponics pattern, so the
  crop-in-a-building half is shipped practice. The cage adds the vertical trick:
  `passability PassThroughOnly`, `fillPercent 0`, drawn at an altitude layer **above
  pawns** (the cage seen from above, chain and anchor at one corner, the crop visible
  through the bars), so a pawn walks beneath it and the floor cell keeps every use except
  *another building*. **Sphere cage** (`RM_SphereCage`, 2×2, 4 grow cells, cheap) and
  **cube cage** (`RM_CubeCage`, 3×3, 9 grow cells, dear). Sow and harvest are the vanilla
  plant-grower jobs, done from the cells themselves — the pawn is *at the cage*, standing
  under it.
- **How it differs from a floor zone, in play:** (1) **placeable over the channel bed**
  — the one ground you cannot farm, farmed from above: the vertical payoff made legible
  in one placement; (2) **immune to floor hazards** — the current does not move it (it is
  chained), veil-fall does not bury it, nuudal do not graze it, tikkarr cannot reach it
  (so a caged oruvell plot loses the tikkarr's growth bonus, §3.1 — a real trade); (3)
  **its light is its own problem** — a cage in a shaft grows on skylight; a cage in the
  dark needs a grow-sphere (§13.2) beside it, which is the thing that makes the two
  ideas one system; (4) **no fertility** — it neither needs nor gets it; growth at the
  plant's own rate, so the cage's gain is space and safety, never speed; (5) **it costs
  Deepwater tech** (§13.5): a tether is not craftable from lattice-timber.
- **Mod Setting:** cages on/off; cages passable-beneath on/off (for players who find
  walking under a crop odd).

### 13.2 Grow-light you farm — the sun-sphere

> "The idea that you can grow sphere colonies of microorganisms bright enough to be like sunlight to grow plants is very cool."

**BENCH NOTE — checked against `src/RimMandrake/LuminousPigment/` first, as briefed.**
The **GlowTank** ships: a 2×2 `Building_PlantGrower` that cultures `RM_CrowncarpetCultured`
(a Scald shore mat) from one seed of `RM_CrowncarpetFresh`, on power, and dies if power
lapses; its `CompGlower` is radius 2.0, colour (200,220,255) — a *pigment* culture whose
glow is incidental, *"slow and low-yield"* by its own description. **This is its big
sibling, in the same family and the opposite purpose: cultured FOR light, and the light
is the crop.**

- **The organism: the ollumin** (`RM_OlluminCulture`, invented). A colony of luminous
  micro-organisms — the same symbionts that light a pallu's mat and a hoolimbre's bladder
  — grown in a glass sphere until it is bright enough to read as sun. Seed: a pallu (its
  green mat) or a harvested hoolimbre bladder; either is a thing a first-day diver can
  net or pick, so the technology is Deepwater but the *seed* is the sea's.
- **The building: the sun-sphere** (`RM_SunSphere`, 1×1 or 2×2). A `Building_PlantGrower`
  growing exactly one plant, the ollumin, whose `CompGlower` is the vanilla **sun lamp's
  shape** — an overbright glower (the sun lamp's colour values exceed 255 so the glow grid
  saturates to daylight; the exact values are UNMEASURED in this pass and must be read
  from `Data/Core` before authoring, never guessed). Growth stages ARE brightness stages:
  seeded (dark) → culturing (radius 3, dim gold-green) → mature (sun-strength, radius ~6):
  **you watch your light grow.** Unlike the GlowTank it wants **no power** — it is fed:
  `CompRefuelable` on a nutrient item (veil-fall gathered as filth-to-item, or kiruun, or
  any raw fish — position: any raw floor food, so the fishery feeds the light that feeds
  the farm). Starved, it dims over days and dies to a seedable husk; it does not
  explode, it does not go out at once. A Mod Setting for the grace period, the
  GlowTank's own `tankPowerGraceHours` idiom.
- **What it is for:** a cage or a floor plot *outside* a shaft grows under a sun-sphere as
  if under a skylight — farming freed from the skylight economy (§8.1), which is exactly
  why the Compact will sell you the cage and not the culture (§13.5). It also lights a
  house like day, which the Compact's own homes do (the manifest's *"growing beds under
  lamps"* were always this).
- **Reconciled with §3–§6:** noothelm and hoolimbre are *wild* light (radius 3–5, a lamp);
  the ollumin is *cultivated* light (sun-strength, a crop). Three scales of living light
  — a bladder you carry, a bulb you plant, a sphere you farm — and the GlowTank is the
  cousin that makes pigment instead.
- ✅ **Answers flag §10.2-6.** The sheet's §9 *"two warm sources"* was skylight and
  Compact lamp; this drop makes *cultivated living light* his own third source. Marked
  answered below; no further ruling needed.

### 13.3 Picked plants stay alive — living decor, the Twilight's take-home

> "Luminous vines the players can lay around to decorate after they're grown and harvested. underwater plants have the unusual property of staying alive after you "pick" them, so you can then decorate with a living plant easily."

**BENCH NOTE.** This is the Twilight's answer to the Grey's coloured-salt cuisine: the
Grey's take-home is eaten and gone; **the Twilight's is alive and kept.** The whole
family, designed:

- **The item class: a living cutting.** Harvesting a living-decor plant yields a
  **cutting** item (`RM_*Cutting`) that is itself alive — it carries `Beauty`, it does not
  rot, and the luminous ones carry `CompGlower` so a pile of hoolimbre cuttings on the
  floor already glows (MEASURED: `CompGlower.ShouldBeLitNow` needs only `Spawned`, so an
  item on the ground lights). **Laying it** is the vanilla build flow: a `Building` def
  per decor form, cost = 1 cutting, `minifiable` so it can be picked up and moved (the
  plant-pot idiom, pure XML). No new mechanism: a plant → an item → a building, all
  shipped verbs.
- **What stays alive** (each a decor building with its own look):
  - **luminous vine** — hoolimbre (§3.3): laid cell by cell in lines and loops along a
    wall or a path; `Graphic_Random` segments so a run reads as one vine; glower radius
    2, gold. *His headline.*
  - **living lamp** — a noothelm bulb on its stalk (§3.4): one cell, radius 4. Replaces
    the aluun-pane lantern of §6.4 as the *plant* lamp; the pane lantern stays as the
    *Compact-made* one.
  - **sail-fan** — sennefan (§3.5): wall-hung, Beauty high, no light; the wardens' art.
  - **glass-tile** — vaalstone (§3.10): a floor-crust tile, Beauty, catches light.
  - **living rug** — murrgrave lace (§3.9): a 2×2 floor piece, faintly lit blue-white
    (the kiruun in it), Beauty, and the one that *feeds* a kept waelune.
  - **lantern-stem** — a cut oruvell stem with its aluun still on it (§5): a column of
    small windows for a doorway; radius 3, gold.
  - **kept waelune** — a creature, not a cutting (§3.7): the pet that is a lamp.
  - **not** quellith (it stings), **not** skirroth (it tangles), **not** the sun-sphere
    (that is a crop, §13.2).
- **What it needs: nothing, by default.** His word is *easily*; a living cutting is alive
  the way the aluun pane is alive — a sealed organism that keeps. Position: living decor
  never dies from neglect; a Mod Setting *"living decor needs light"* (off) makes the
  luminous forms dim to plain green in a room with no light, for players who want the
  fiction stricter. Q15 asks.
- **What it gives a room:** Beauty (each piece), light (the luminous ones — a room lit
  entirely by living things is a room with no fuel bill), and **one thought**:
  `RM_Thought_LivingLight` — *"lit by living things"*, a small mood in any room whose
  light comes only from glowers of this family (a `ThoughtWorker` reading the room's
  glowers; the pigment mod already ships `ThoughtDefs` for the same shape). Kept
  *outside* the sea — on the surface, in a colony a thousand cells from any water — it
  is proof you went down and came back with something that is still breathing.
- **Propagation:** a mature living lamp or vine can be *harvested again* for one cutting
  every N days (the decor building is a `Building_PlantGrower`-free plant? — no: keep it
  a building; propagation is a `CompProperties_` on the building that spawns a cutting on
  a timer, small C#, optional; position: yes for the vine and the lamp only). The
  Twilight's take-home *multiplies*; the Grey's is consumed.

### 13.4 The whale's shadow — the full sequence, five beats

> "I love the shadow of the whale-analog leads to eerie booming sounds and little light... animals freak out... and then it starts raining detritus, parasites, barnacle analogs with glowing bits in them like gems. and the whole ecosystem goes into overdrive and starts eating them at great speed."

**BENCH NOTE.** This supersedes §7.3 Grade A's simpler form (dim + letter + maybe a
skylight moves) with an ordered event; Grade B (the moving shadow art) stays separate
and, when built, plays under beat 2. One `IncidentDef` `RM_GardenerPasses`, one
`IncidentWorker` that starts a `GameCondition` `RM_GardenerOverhead` (duration ~1 in-game
hour) whose ticks fire the beats; the darkening is the vanilla `CompAffectsSky` route
measured in §7.2. Timings are INVENTED placeholders to be judged by watching.

| beat | at (ticks) | what happens | engine |
|---|---|---|---|
| **1 — the booming** | 0 | *"eerie booming sounds"* — the sheet's *"far slow calls through the roof"*; a letter (neutral, not threat): *the gardener is overhead* | a `SoundDef` on the condition's start, repeating every ~400 ticks for the duration; `LetterDef` neutral |
| **2 — little light** | +300 | every skylight dims to ~20% (the skylight ticker reads the condition), the whole floor darkens 40% via `RM_PassingShadow`'s `CompAffectsSky` fade; the creatures' own light is suddenly all there is — §6.1's rule at full force | §6.3 ticker + §7.2 thing; Grade B overlay plays here when it exists |
| **3 — animals freak out** | +600 | shoals scatter, nuudal bolt, the loohn goes to ground, the clingers vanish into their hosts | every wild animal on the map starts `PanicFlee` (a mental state; one loop in the condition tick — mods do exactly this); shoals' `herdAnimal` keeps them together as they run; the Compact's cast stands outside and watches (§9.3, the gardener-warden) |
| **4 — the rain** | +900 → +2400 | *"it starts raining detritus, parasites, barnacle analogs with glowing bits in them like gems"* — over a minute and a half, things fall from the lid into the shafts and around them: **veil-fall** by the sheetful (a filth, `RM_Filth_VeilFall`, that the ecosystem eats — beat 5); **hullick** (`RM_Hullick`, invented: the gardener's parasite, a thumb-sized biter shaken loose, a short-lived nuisance animal that bites anything standing in the rain and dies within a day — a colonist bitten takes a minor *hullick bite* hediff, itch and a little pain, cured by any doctor; not lethal, not plot); and **orrilith** (`RM_Orrilith`, invented: the barnacle analog — a fist-sized shell that grew on the gardener's hide, with *"glowing bits in them like gems"* — an **item** with `CompGlower` radius 1.5 and `Beauty`, that falls and lies lit on the floor) | fall = the shipped skyfaller shape (a `Skyfaller` carrying a `ThingSetMaker`; the exact custom-def route is UNMEASURED here and must be read from `Data/Core`'s meteorite/drop-pod defs before authoring); density scaled by the map's skylight count — the rain comes *through the wells* |
| **5 — overdrive** | +2400 → +6000 | *"the whole ecosystem goes into overdrive and starts eating them at great speed"* — every floor animal takes `RM_Hediff_Frenzy` (hunger rate ×6, MoveSpeed +50%, duration ~1 hour) and, because orrilith and veil-fall are **ingestible items in animal food categories**, vanilla food-seeking sends every nuudal, weloon, tikkarr and clinger to eat them off the floor at speed — no C# for the eating, only for the hediff | the **race**: the player hauls orrilith before the ecosystem eats them. A frenzied **loohn** (or kellu) is the **danger** — `maxPreyBodySize` raised by the hediff for its duration, so for one hour the floor's predator hunts things it never would, colonists included if they stand in the dark between shafts. Ban 4 untouched (no Compact hostility); ban 2 served (the roof's keeper passing) |

**What orrilith is for.** Shelled (a `RecipeDef` at a crafting spot), an orrilith gives
**orrilith gems** (`RM_OrrilithGem`) — the biome's only "gem", **and it comes from an
animal, not a mine**: the designed absence of §8 held even here. A luminous stuff-less
item: high `Beauty`, `CompGlower` radius 1, trade tag Exotic; inlaid into living-decor
pieces (§13.3, a cost variant) or sold. Rarity is the rain's — one pass in a few days,
a dozen orrilith, most eaten. **The Compact's cast collects them too** (the child of
§9.3, for one).

**Mod Settings:** the whole sequence on/off; rain density; frenzy strength; parasites
bite colonists on/off.

### 13.5 Deepwater showcase tech — what you covet and must earn

> "Show case technology for the Deepwater faction."

**BENCH NOTE.** The cages, the tethers and the sun-sphere read as **Compact engineering**,
the thing a diver sees at the bottom-houses and cannot build. The mechanism is vanilla
Royalty's own: **techprints** (`ResearchProjectDef.techprintCount` + a techprint item),
which the player assumption of all DLC makes free to use (`CLAUDE.md`, 2026-09-25/26).

- **`RM_Research_DeepwaterTethering`** — unlocks `RM_SphereCage`, `RM_CubeCage`, the
  tether item `RM_TetherChain` (a build cost of every cage; uncraftable without the
  research; sold by the bottom-house dealer in the meantime). Needs **1 techprint**,
  `RM_Techprint_Tethering`, sold **only** by the Compact — the bottom-house lamp-wright
  and the surface water-caravan (`RUT_Jawa_DeepwaterCompact`'s `Trader` group) — or
  given with a permit (the bedazzle doc's §3.2 permits: dock, air, lamplight, charts;
  *tethering* is the fifth).
- **`RM_Research_OlluminCulture`** — unlocks `RM_SunSphere`; **2 techprints**, the dearer
  one, because it frees the player from the skylight economy (§8.1) and the Compact
  knows it. The *seed* is the sea's (§13.2); the *sphere* is theirs.
- **The bottom-houses show it working**: §9.2's house genstep places one sphere cage on
  a chain over the channel beside each house, a sun-sphere lighting its growing bed, and
  a tether-buoy in the shaft — so a diver's first sight of the technology is the
  Compact using it, which is what *showcase* means.
- **Tier:** all invented, `RM_`; the techprint's *seller* being the Compact is a Utinni
  patch on the trader stock (`MayRequire`), and a free-tier player finds the techprint in
  the bottom-house stock instead.

### 13.6 Star Wars cuisine — measured, and the pattern

> "Huge variety for starwars cuisine mod."

**BENCH NOTE — MEASURED 2026-09-26.** There is no third-party cuisine mod in any list.
The only `cuisine` packageId in both full-list snapshots
(`ModsConfig_full_plus_gelatinousslime_2026-09-21.xml`, 620 active;
`ModsConfig_full_plus_longhunger_2026-09-19.xml`, 621 active) is **ours**:
`mandrake.rsw.cuisine` (`src/RimStarWars/Cuisine/`, "RimStarWars: Cuisine"). The newest
snapshot by date (`ModsConfig.PRESWAP.20260926_144543.xml`) is a 12-mod test list with
no cuisine mod and proves nothing about the full list. So *"starwars cuisine mod"* IS
`mandrake.rsw.cuisine`, and the pattern is the Grey's (`RSW_GreySaltCuisine.xml`, shipped
this week): **ingredients `RM_` in `mandrake.rm.terminalbiomes`; recipes, dishes and
thoughts in `mandrake.rsw.cuisine` behind `MayRequire`; no hard dependency either way.**

**The variety, proposed** (ingredients already in this document; dishes are the
cuisine mod's to name at its own sitting): oruvell fronds (staple green) · murrgrave
(the floor's mushroom) · aluun (a coin of sweet white flesh) · niim (the fish that
tastes like fish) · kellu (with its ink) · hollu (*"a delicacy in exactly one dock"*) ·
vessik (*priced by the sting*) · kiruun (**a spoonful of light** — the one dish that
glows on the plate, a meal with `CompGlower`; the cuisine mod's marquee) · waelune ·
illuvane (a medicinal tea) · orrilith meat (once shelled) · and the Compact's own table:
Grand Tessek's **Accord dinner** (the Hold's cook, `CastRoster_DEEPWATER.xml`) as a
feast-class meal the campaign layer names. Twelve ingredients, and *"huge variety"* is
then a recipe count for the cuisine mod's owner to set — position: one dish per
ingredient plus three feasts, so the node you cut is a real decision, the Grey's own
rule.

### 13.7 What this drop answered, and what it opened

**Answered:** §10.2-6 (a third light source — his, cultivated); §11 Q7 in part (the
whale's shadow is now a specified five-beat sequence, Grade A; Grade B still a mockup).

**Opened — added to §11:**

- **Q13 — The cage's chain.** Buoyant cage chained down to a floor anchor (designed here),
  or hung from a surface float? **Position:** anchor; same picture, more placements.
- **Q14 — Walking under a cage.** The cage is passable-beneath so it costs no floor use;
  a pawn stands under the crop to tend it. Acceptable in a top-down game, or should the
  cage occupy its cells like hydroponics? **Position:** passable-beneath — it is the
  whole point of his sentence.
- **Q15 — Living decor neglect.** Never dies (default) with a stricter setting, or needs
  light/water by default? **Position:** never dies; *"easily"* is his word.
- **Q16 — The sun-sphere's feed.** Fed on raw floor food (no power), or powered like the
  GlowTank? **Position:** fed — a living thing, and the fishery then feeds the farm.
- **Q17 — The rain's parasites.** Do hullick bite colonists (minor hediff) or only
  animals? **Position:** colonists too, minor, curable; the rain should be something you
  stand out of.
- **Q18 — Orrilith gems.** The biome's only gem, from an animal — a trade good and a
  decor inlay, or a crafting material with more uses? **Position:** trade and inlay
  only; the moment it is a material, someone asks for a mine.
- **Q19 — Techprints.** Compact-only sellers for both prints, with the sun-sphere at two?
  **Position:** yes.

**Items BENCH thinks should be filed for this drop** (with him, not this pass):
`TWILIGHT_TETHERED_CAGES_1` (§13.1, §13.5 — carries Q13/Q14/Q19),
`TWILIGHT_SUN_SPHERE_1` (§13.2 — carries Q16; reads the GlowTank first),
`TWILIGHT_LIVING_DECOR_1` (§13.3 — carries Q15), `TWILIGHT_WHALE_SEQUENCE_1` (§13.4 —
absorbs `TWILIGHT_WHALE_SHADOW_1`'s Grade A; carries Q17/Q18), and a cuisine row on
`mandrake.rsw.cuisine`'s own next wave (§13.6).
