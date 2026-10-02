# The Weeping Stones: bedazzle review (grandfathered sitting, turn 1 drafted)

Program: `BEDAZZLE_TOP_SHAPE_PROGRAM_1`, track (a), worst-first, sitting 10. Item to be filed by the
parent (`WEEPINGSTONES_SCORING_SITTING_1` shape).

_BENCH design pass, 2026-10-02. Tenth sitting of the grandfathered track, in the order of
`grandfathered_bedazzle_scores_2026-10-01.md` (§ Weeping Stones; sitting order row 10). The sheet
`weeping_stones.md` is frozen (`BIOME_FREEZE_FABLE_REVIEW_1`, 2026-09-07); its §10 to §12 enrichment was
never ratified as a block, but the 2026-09-24 design sitting (`WEEPING_STONES_DESIGN_SITTING_1`) ruled the
cast, and the shine sitting the same day ruled the mechanics. Already ruled and **not re-argued here**:
biome + hand-placed oasis landmarks (186 placed, `OASIS_LANDMARK_PLACEMENT_1`); the truce and the claim law;
the stocked pool (*"love it. Moisture farmers specializing in fish… Make the fish nasty and way too
active"*); animal retribution at the water; the oasis-maker machines (sold, very expensive; a separate mod);
the eight invented natives, the pilgrim strider and ridge-soarer; one-species burrak; truce v1 accepted
cheap; the gorrask (ruled at the Nightside Ice sitting). **Ruled DEAD and never revived here:** wind-hour
(*"nah"*) and the born-and-dying water (*"nah too much"*). The six hard bans of sheet §6 bind every slate
row; the ones that bite hardest: **no rain-fed anything**, **no ambush-at-water predator**, **no toll on
unsettled water**, **every native carries the comb**, **no Earth flora or fauna**._

Sources read, all in the BENCH clone: `src/RimMandrake/WeepingStones/` (BiomeDef
`Defs/BiomeDefs/RM_WeepingStones_Biome.xml`, every def file, `About.xml`, all 19 `Source/*.cs` by grep, the
settings and `RM_MapComponent_PoolStock.cs` read), `src/RimMandrake/OasisMaker/`,
`src/RimMandrake/EnvironmentalHazards/Source/RM_MapComponent_WaterTruce.cs` and its settings reader,
`RM_SunHeatExtension.cs`, the frozen twin `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_WeepingStones.xml`,
the cast patch `src/RimUtinni/UtinniPatches/Patches/WildAnimals_WeepingStones.xml` (its one op's xpath
resolved), every other file under `src/` naming the biome or its donor `ZBiome_DesertOasis`
(`OasisMutator_DesertOasis.xml`, `BiomeNames_Ashkarr.xml`, `BiomeDescriptions_Ashkarr.xml`,
`BiomeFlora_Ashkarr.xml`, `BiomeCastEvictions_WildBiomes.xml`), `Biomes.compose.json`, the sheet, the
fauna, flora, stocked-pool and shine-options docs of 2026-09-24, the closed items
(`OASIS_MAKER_MACHINES_1`, `OASIS_MAKER_BUILD_1`, `WATER_TRUCE_RETRIBUTION_1`, `STOCKED_POOL_BUILD_1`), the
register `design/Jawa/salvation_rites_2026-10-01.md`, the ledger's 2026-10-02 rulings (Webwork, Greentide,
Rust Cathedral, the Rot, the Fever Wood), and the Fever Wood review for shape. Rosters were parsed as XML
elements; the creature census reads descriptions.

## 0. The Weeping Stones in plain words (for the card)

The Weeping Stones is where water is combed out of the wind. High pale stone stands in the path of a wet
sea-wind on the hot side of the world, and every cold, shaded face of it sweats: black streaks of water
running down white rock, moss on the seep lines, and here and there a real pool with a green ring around
it and a crowd at the water. Everything alive here holds a fin, a crest or a comb up into the wind, and so
do the ancient condenser machines, so from a distance you cannot tell the old machines from the animals.
At the water a truce holds: strike first there and the animals turn on you. Moisture farmers here farm
fish in pens (nasty, far too lively fish, and things you are not sure you should eat), the hottest pools
are fed from below by vent-warmed springs, and somewhere a stone-crab bigger than a canyon sleeps. The sky
is ordinary (clear, fog, the odd sandstorm), the place makes no sound of its own, it does nothing to your
ship, nothing learned here travels, and its god, the water god, lives only in campaign prose.

## 1. What is there: ruled vs built

### The best-landed free kit of the grandfathered twelve, with its sky, sound and ship blank

`src/RimMandrake/WeepingStones/` (`mandrake.rm.weepingstones`, part of the Baroque Biomes compose,
`WEEPINGSTONES_RM_MOD_BUILD_1`, closed) ships: its own biome worker; the **stocked pool** whole
(`RM_Zone_PoolPen` and its designator, `RM_MapComponent_PoolStock` with the Healthy/Thin/Silent/Vhorrin
gauge, five work givers and job drivers for stock, feed, net, harvest and cull, the vhorrin emergence and
the vizhik escape, breeding-stock items, five recipes, the cuisine and eight eat-thoughts); the eight
invented natives and the gorrask; ten invented flora rows and their products (bladder-fruit, dewgourd,
seep-salt); the six-fish catch table and the rare-catch maker. **Animal retribution** at the water rides
`mandrake.rm.environmentalhazards` (`RM_WaterTruceExtension` on the `RM_` def, `RM_MapComponent_WaterTruce`,
the faction-aimed retribution mental state, gated by `waterTruceRetributionEnabled`). The **oasis-maker**
is its own mod (`src/RimMandrake/OasisMaker/`, `RM_CompOasisMaker`, the placement scorer and the green/red
place-worker), sold at a very high price by ruling. The campaign layer adds the eight-row canon cast patch
and the frozen twin.

### 🔴 The systemic defects of the last sittings: checked, and the Weeping Stones carries few

- **(a) Invented content stranded in the campaign tier: NO.** `WildAnimals_WeepingStones.xml` adds only
  `RSW_Ollopom` 1.3, `RSW_Fanback` 0.5, `RSW_Dewback` 0.4, `RSW_Boma` 0.15, `RSW_Dactillion` 0.15,
  `RSW_Bantha` 0.1, `RSW_Eopie` 0.1 and `RSW_Jamel` 0.1; all eight are genuine canon (each returns its own
  Wookieepedia page by the search API; seven have `canon_references/` entries, the jamel does not, which
  proves nothing). Every invented creature is inline on the `RM_` def. The cleanest of the twelve on this
  check.
- **(b) Campaign patches replacing an `RM_` list, or mechanics gated on the twin or a donor: the cast is
  clean; the oasis landmark itself is not.** The cast's one op is `PatchOperationConditional` →
  `PatchOperationAdd` onto `RM_WeepingStones/wildAnimals`; nothing replaced. No C# gates on
  `RUT_WeepingStones` or the donor (the pool kit gates on its own setting; the truce on the `RM_` def's
  extension). But the biome's **architecture** (sheet top: *"each actual pool is a hand-placed… vanilla
  Oasis LANDMARK… required TileMutatorDef Oasis"*) leans on `OasisMutator_DesertOasis.xml`, and that patch
  whitelists only the donor `ZBiome_DesertOasis` into the vanilla `Oasis` mutator's `biomeWhitelist` (vanilla
  ships `Desert`, `ExtremeDesert`). **Neither `RUT_WeepingStones` (which carries today's world) nor
  `RM_WeepingStones` is on it.** The 186 placed landmarks are saved world state and may not re-check the
  whitelist (UNMEASURED live; read from source), but anything that validates or re-rolls an Oasis mutator
  against the tile's biome (the terminal repaint, a quest site, a scenario) will refuse ours. Same family as
  the Fever Wood's donor-only ancient-danger DENY; here it is the biome's spine. The same patch's other two
  ops (snow strip, label) target only the donor too; the `RM_` def has neither problem itself.
- **(b′) The same mutator plants Earth palms at every pool, in both tiers.** The vanilla `Oasis` mutator's
  `additionalWildPlants` are `Plant_TreePalm`, `Plant_RatPalm`, `Plant_Grass`, `Plant_GrayGrass` and
  `Plant_Reeds` (the patch header's own RimSage read), and the campaign patch **adds** `TreePalma` 3 and
  `VEE_Plant_DatePalm` 2. Sheet §6 bans Earth flora, and the flora roster records the owner's 2026-09-09
  card **using the date palm as the very example** (*"No Earth-nameable flora… the date-palm example"*). So
  every oasis map, the biome's whole point, grows the one plant he named as banned. Read from source;
  UNMEASURED live (which rows the mutator actually spawns depends on the landmark's map generation).
- **(c) Ratified-but-unbuilt: yes, five, smaller than the Fever Wood's seven.**
  1. **The murrin is unobtainable.** The stocked line's *baseline* fish (*"A silent pool with no murrin
     rings is the first sign an oasis is dying"*) is on no `wildAnimals` and no `fishTypes`; its wiring is
     *"owed to FISH_BY_BIOME_1's successor"* (BiomeDef header), and **no item of that name exists in the
     ledger**. So the netting job has nothing to net, and the free stocked pool starts from its biters.
  2. **The truce's suppression half.** The roster ruling (*"predators never start hunts near full water…
     accepted for v1"*) is unbuilt: `RM_MapComponent_WaterTruce`'s own header says *"The SUPPRESSION half…
     is a separate owed build"*, and no item carries it. The vhakk's description promises *"It never hunts at
     water"*; nothing enforces it, so the §6 ambush ban is honoured by the vhakk's rarity only.
  3. **Dewsilk.** The mirrik row (ruled) makes its cocoons *"the dewsilk source (sheet §11 — the biome's
     signature trade good)"*; no `RM_Dewsilk` exists anywhere in `src/`. The mirrik's description still sells
     it.
  4. **The gorrask as a landform.** *"v1 ships as a real, legendary-rare single-tile creature; true
     multi-tile landform occupation is a follow-on mechanic"* (BiomeDef header). No item carries it, and the
     gorrask has no comps at all: a bs-15 crab with a beautiful sentence.
  5. **The oasis-maker's quests** (*"weave it into some quests to obtain or sabotage them"*): deferred
     *"to quest passes"* at `OASIS_MAKER_BUILD_1`'s close; no quest pass item names them.
- **(d) Mod Settings that do nothing: none.** `RM_WeepingStonesSettings` has one field,
  `stockedPoolsEnabled`, read by all five work givers, the designator's `Visible` and the PoolStock pulse.
  `waterTruceRetributionEnabled` is read by the truce component. Clean, but thin: one switch for the whole
  biome mod (no tuning slider on the vhorrin odds, the escape chance or the truce radius; the radius is an
  XML field). The Mod Settings law asks for more; listed, not slated on its own.
- **(e) Canon Star Wars names in free-tier text: none.** Every `RM_` description is franchise-free (the
  grep hits for "dewback", "Jawa" and the like are XML comments and doc paths).
- **(f) Missing heat kind: YES.** The biome runs median 35 °C, p90 57 °C, max 63.5 °C (sheet §0, the seep
  oases), and `RM_WeepingStones` carries no `RM_SunHeatExtension`. **BENCH's read: sun angle from latitude**
  (`overheadAboveElevationDegrees`: high-sun tiles overhead, near-terminator tiles low sun), because the
  sheet's whole ecology is *stone-shade real estate*: shade is the biome's property line, so shade must
  work. The seep oases are vent-heated and would read **ambient**, but one def carries one kind; the
  landmark is the only place they differ (noted for the build, not split).
- **One more, not on the list: a ruled-dead word in shipped text.** "Wind-hour" was ruled DEAD
  (*"nah"*, 2026-09-24) the same day the cast was written, and **12** def descriptions still name it (the
  mirrik's dance, the skarrin's arcs, the vizhik's escape, the murrin's rings and others), plus the vizhik
  escape's own code comment (*"One pulse is roughly a wind-hour's worth"*). The player reads about a daily
  event that never happens. Text-only fix.

### Fauna, merged (inline + patch-added), read as XML elements, census by description

**Free tier, `RM_WeepingStones/wildAnimals` (17 rows, `animalDensity 1.5`):** sillik 0.8 (*"lives ON the
vertical weep-faces"*), mirrik 0.6 (flies, `MaxFlightTime` 8; *"smoke rising off the water that flows the
wrong way"*), ssurr 0.35 (*"closed it is a blade, open it is a wheel"*), kirruk 0.2 (flies, 25; comb-slotted
wings), tirbak 0.15 (bs 3.5, the walking cistern), burrak 0.12 (bs 2.2, digs basins that outlive it), vhakk
0.08 (the warden), vellak 0.08 (sail-comb pilgrims), gorrask 0.02 (bs 15); the pool bestiary's floor half,
skarrin 0.6, karrek 0.6, vizhik 0.25, loomu 0.2 (*"repeats what it hears at the bank… its keeper's name for
it"*), huldu 0.2 (*"body-warm, with a pulse"*), ivvol 0.05 (*"the eyes count"*); and two ruled donor keeps,
`ColossusToad` 0.4 (Odyssey) and `AA_Eyeling` 0.1 (the ikee, the omen). The vhorrin is off-roster by design
(a mismanagement spawn), the murrin by omission (above). Every owned creature is alien in body and colour
(silver-grey, dove-grey, velvet, verdigris), none Earth-like, all carry the comb; the two donors do not
(the sheet's comb ban grades art, and both were kept by ruling). Both fliers fly.

**Campaign patch-adds to `RM_WeepingStones` (8 rows, `PatchOperationAdd`):** the eight canon desert beasts
above. Nothing invented, nothing replaced.

**Flora:** ten invented rows plus two ruled vanilla keeps (`Plant_Reeds`, `Plant_Ambrosia`). Not a gap,
apart from the mutator's palms (b′).

**Multi-homed species:** none of the owned cast is cast elsewhere (searched by defName). The canon
dewback's move here from the lava field was ruled 2026-09-06.

### Heat

See (f): an extreme-heat biome with **no heat kind declared**. Recommended: sun angle from latitude (the
tile's own latitude, never region prose), so shade under the overhangs is what keeps a colonist alive at
noon and is worthless near the terminator. Vanilla temperature only.

### Ruled mechanics, built and unbuilt

- **Built (free):** the stocked pool end to end (stock, feed, net, harvest, overdraw, cull, recapture),
  the vhorrin and the vizhik escape, the cuisine; animal retribution at the water; the eight natives and the
  gorrask (as an animal); the flora and its products; the fish tables; the oasis-maker (its own mod).
- **Built (campaign):** the eight canon beasts; the 186 placed and named oasis landmarks (world state).
- **Ruled, unbuilt (free):** the murrin's wiring; the truce suppression half; dewsilk; the gorrask as a
  landform; the heat kind; the oasis-maker quests (obtain, sabotage).
- **Sheet prose never ratified as a block** (sheet "Owed": *"none of it is ratified"*): the vane arrays as
  salvage, the comb-vane segment, the Oomo token and truce-stone, the condenser fin, the servo-vent
  enclosure, the aeolian chords (each array its own chord; a dead oasis silent), the faction faces.
- **Ruled dead:** wind-hour; the born-and-dying water.
- **Unruled marks:** a ship touch (6), a sound (7), weather (8), a god and a rite (9), a learned
  technology (2).

### Mechanisms already in `src/` that the slate can reuse (searched before proposing)

- `RM_MapComponent_WaterTruce.IsTruceWater` (the radius, public *"so that future work can read the
  identical radius"*) and `RM_MentalState_WaterTruceRetribution`: anything about who struck first at the
  water reads these; the suppression half is the inverse of `RM_MapComponent_DreadField` +
  `RM_JobGiver_DreadAvoidWander` (the roster's own note).
- `RM_MapComponent_PoolStock` (per-pool census, Silent state, pulses): anything that listens to a pool's
  health reads it.
- `RM_MapComponent_ShadeGrid` (`ShadeAt`), `RM_JobGiver_SeekShade`: shade as property already exists.
- `RM_CompOasisMaker` and `RM_OasisPlacementScorer`: anything that grows or judges a water site.
- `RM_MapComponent_ProximitySoundscape` (the Greentide's): a per-object sound that falls silent is wiring.
- `RM_CompTameSootheAura`: the ssurr's beloved register, if wanted mechanical.
- The Rites tab's found-rites row and `RUT_ResearchMod_GrantRite` (register §d).

## 2. Scorecard

Ruled counts as HIT; built is reported beside it. Marks come from the scores doc, re-read against the
sheet, the 2026-09-24 rulings and the source. No mark moves; one HIT is qualified (mark 5).

| # | Mark | Free (ruled) | Campaign (ruled) | Built today | Note |
|---|---|---|---|---|---|
| 1 | Unique mechanic | **HIT** | **HIT** | the stocked pool end to end; animal retribution at the water | the truce's suppression half is unbuilt |
| 2 | Discoverable technology | PARTIAL | PARTIAL | the oasis-maker (a separate mod, **sold**, not learned); no research project | pool husbandry is a zone, not a discovery; nothing learned here travels |
| 3 | Unique resources | **HIT** | **HIT** | seep-salt, bladder-fruit, dewgourd, pool-fry baskets, murrin broth, karrek paste, huldu fat, the cull feast | dewsilk, the signature trade good, is unbuilt |
| 4 | Surprising creatures | **HIT** | **HIT** | 15 owned creatures, all comb-carrying, alien-coloured, inline | the murrin, the baseline fish, is wired nowhere |
| 5 | GIANT beast | **HIT** (thin) | **HIT** (thin) | the gorrask, bs 15, as a legendary-rare animal with no comps | no story, no hook, the ruled landform behaviour unbuilt; every giant ruled today has a plot hook |
| 6 | Gravship touch | MISS | MISS | 0 | |
| 7 | Soundscape | MISS | MISS | no `soundsAmbient`, no SoundDef | the sheet's vane chords were never ratified; wind-hour, the obvious register, is dead |
| 8 | Interesting weather | MISS | MISS | `Clear` 70, `Fog` 25, `Sandstorm` 6, `DryThunderstorm` 1: all vanilla | no rain and no daily clock are both bans now |
| 9 | Relationship to the gods | MISS | PARTIAL | free 0; campaign: Oomo's water-ground in sheet prose and landmark whispers | no precept, shrine or rite |

**Free 5 HIT / 1 PARTIAL / 3 MISS. Campaign 5 HIT / 2 PARTIAL / 2 MISS.** The same as the scores doc.
Like the Fever Wood, the top problem is **missing marks**, not missing landings: the sky, the sound, the
ship and the gods are blank, and nothing learned here travels. The landing debt is the smallest of the
recent sittings (the murrin, the truce's other half, dewsilk, a heat kind, the gorrask's landform, twelve
"wind-hour" sentences), with one structural exception: **the oasis landmark's mutator names only the donor
biome and plants the banned date palm at every pool** (§1 b, b′).

**Rite: none today.** The register's B6 row (*"The pool rites | unassigned | PITCHED"*) is the only seed;
this sitting answers it (§6).

## 3. Roster fill

### The gaps, read from the sheet's rings (§10) and the ruled roster only

Ban 5 shapes every fill: violence lives on the approaches, never at full water. **Every ring the sheet and
the 2026-09-24 sitting opened is filled by a built, owned creature**; this sitting coins no new creature.

| ring (sheet §10, roster §1) | free tier today | campaign today | fill |
|---|---|---|---|
| The weep-faces (the prey base) | sillik | same | none: built |
| The pools: romance | ssurr | + fanback, dewback | none: built |
| The pools: the fish | skarrin, karrek, vizhik, loomu, huldu, ivvol (+ vhorrin by mismanagement) | same | **wire the murrin** (the baseline fish, owed to an item that does not exist) |
| The seep-throats (hot oases) | loomu (*"hangs in the warm seep-throat water"*), huldu, steamfrond | same | none: the loomu covers it |
| The approaches: the warden | vhakk (promises never to hunt at water; nothing enforces it) | same | **build the truce's suppression half** (ruled v1) |
| The approaches: the well-digger | burrak (elder = burradar, one def) | same | none: built |
| The pilgrims | vellak lines, tirbak caravans | + bantha, eopie, jamel, ollopom | none: built |
| The sky | mirrik (swarm, flies), kirruk (soarer, flies) | + dactillion | **build dewsilk** from the mirrik's cocoons (ruled) |
| The omen | `AA_Eyeling` (the ikee, donor body) | same | none owed; the roster ranks it first for a future `RM_` port (unruled) |
| The giant | gorrask (an animal with no story) | same | **the card asks which story it carries** (below) |

Every owned creature is one home (searched by defName across `src/`, zero hits outside the mod; probe
`RM_Fessk` 1), free tier, alien in colour, comb-carrying.

**The giant needs a story, not a body.** The gorrask's own sentence is already a plot seed (*"it moves
once, settles for a season, and the pool truce holds around it exactly as it holds around everything
smaller. Its shell is old enough that whole weep-mat colonies have taken root along the seams"*). He
rewrites giants into a specific creature with a hook tied to the ship, the gods or the trade. Three
stories, none sharing a neighbour's shape (the Rot's gut is a treasure map you kill; the Rust Cathedral's
borehulk is a machine you mend; the Fever Wood's deep is bargained with through its young; the Webwork's is
a skeleton read bone by bone; the Nightside's sohl and hessarund are quiet landforms that move once):

- **The Walking Array** (BENCH; recommended). The oldest gorrask settled under an ancient condenser vane
  array ages ago and the machine grew into its shell: it is the **last ancient condenser on the planet
  still running true, and it walks.** Wherever it settles for its season, the array combs water out of the
  wind and a pool forms round it, a moving oasis, and the truce comes with it. **The plot hook: three
  claimants.** The Ascendant Helix wants to wake the machine (they camp at dead rings for exactly this, sheet
  §12) and do not care what it costs the crab; a Hutt wants to wall it in as a palace pool (legal only if
  he lives on it, and it walks); the Deepwater Compact rules it water that belongs to no one. The clan, as
  brokers who rarely settle, can **guide it** onto its own map for a season (water, and a truce that
  protects the camp), **sell its next settling ground** to the highest bidder (the buyer comes to wall it,
  and the claim law decides whether that is legal), or **cut the array out**, which kills the moving oasis
  and yields the one working ancient condenser left: a **ship-grade water plant for the gravship**. Cutting
  at the water is the first strike the truce answers. Readable: the array's fins on the crab's back, the
  pool forming, three faction letters. **Reuses:** `RM_CompOasisMaker` ring growth (the pool round it),
  `RM_MapComponent_WaterTruce` (the truce travels with the pool), the faction faces of sheet §12. New: a
  comp on the elder gorrask, a three-claimant quest, the ship part. Size L.
- **The Crab on the Hatch** (BENCH; "squatter" is taken by the settlement templates). A gorrask arrives and settles for its season **on your pool**, or
  on your best ground. Under the truce you cannot strike it near water without the whole map turning on
  you; you can wait the season, or coax it on by feeding it from your pens (a culled vhorrin is the only
  meal big enough). When it moves, it uncovers what it was sitting on: a sealed **ancient cistern hatch**
  with one of the landmark loadouts below (a stockpile, an uplink). **The plot hook:** a Blackstar team has
  been watering quietly at your pool for days, which means they know what is under the crab too. Ties the
  stocked pool, the truce and the landmark loadouts together. Size M.
- **The Last Caravan** (GPT, §5 idea 1): the oldest gorrask wears a mineralised freight rack holding a
  whole lost merchant caravan; strip it now, or escort the crab through its one move and deliver it intact
  to a collector. On the card as the second option.

## 4. The slate

Proposed for owner turn 1. Row 0 executes existing rulings (the 2026-09-24 roster and shine verdicts, the
owner's 2026-09-09 date-palm card, the one-heat law, the wind-hour verdict); rows 1 onward need his word.
Nothing here touches tiles, rains, runs on a daily clock, or lets a predator hunt at full water.

**0. Land what was already ruled (free tier, plus one campaign patch).** In `mandrake.rm.weepingstones`
and `mandrake.rm.environmentalhazards`:
- **The murrin:** wire `RM_Murrin` inline on `RM_WeepingStones` (`wildAnimals`, plus the missing
  `RM_MurrinCatch` item into `fishTypes`: the two-def law; only the pawn and the meat exist) so the stocked line's baseline fish can be netted; drop the citation of the item that does
  not exist.
- **The truce's other half:** predators never start a hunt within the truce radius
  (`RM_MapComponent_WaterTruce.IsTruceWater`, the inverted dread-field shape the roster names), with the
  ruled side effect (your tamed predators also will not hunt there) and a Mod Settings toggle.
- **Dewsilk:** the mirrik's cocoon item, a tamed-swarm harvest, and the cloth (defs; the roster says no
  new C#).
- **The heat kind:** `RM_SunHeatExtension` on `RM_WeepingStones`, sun angle from latitude (§1 f).
- **The dead word:** the twelve "wind-hour" sentences and the vizhik escape's comment rewritten to what
  actually happens (or to the new weather, if row 3 is chosen; the vizhik's escape is the natural thing for
  it to trigger).
- **The oasis mutator (campaign patch):** whitelist `RUT_WeepingStones` and `RM_WeepingStones` beside the
  donor in `OasisMutator_DesertOasis.xml`, and remove `TreePalma` and `VEE_Plant_DatePalm` from the
  mutator's bonus flora; for the vanilla palms and grass, a free-tier patch that swaps the `Oasis`
  mutator's `additionalWildPlants` for the biome's own blade flora on our biome only (vanilla deserts keep
  theirs). (The donor-only snow and label ops are harmless and listed for `BIOME_TIER_CLEANUP_1`.)
- **Mod Settings:** a slider each for the truce radius, the vhorrin odds and the vizhik escape chance
  beside the master switch.
Size M (all names and rulings exist; the suppression half is the only real C#).

| order | package | marks | reuses | size |
|---:|---|---|---|---|
| 1 | **The giant's story** (§3): the Walking Array, the Last Caravan (§5 idea 1) or the Crab on the Hatch. Any of them also lands the ruled "gorrask as a landform" as far as its story needs. | 5 | `RM_CompOasisMaker` ring growth, the truce component, the faction faces, the pen's culled vhorrin | M to L |
| 2 | **The Pilgrim Passage** (ship; GPT's §5 idea 2 joined to BENCH's claim-law reading): at an oasis the practical landing shelf lies across the pilgrim approach. Land there and the pilgrims (vellak lines, tirbak caravans, travellers, water parties of factions you distrust) queue at your hull. Launch, or **grant the passage for good**: rebuild a real corridor through your ship, and for as long as the charter stands the truce holds round your hull (anyone who strikes first in the passage brings the wild herds down on their faction, raiders included). Close the passage on a later landing and the breach is recorded: fencing travellers off water you do not live on is the one barbarism (sheet §4), so the Deep Desert Tribes, *"the ones who execute toll-keepers"*, come for the ship. Landing alone is not settling; the charter is. | 6 | `IsTruceWater`, the retribution state, Odyssey's visitor-clearance launch flow, visitor `LordJob`s | L |
| 3 | **The Fish Walk** (BENCH, weather): a heavy dew-front (moving air, no rain, no clock: a random weather with a warning) sheets every cold face and rock shelf in running water. The pools brim, and for its duration the stocked fish leave the water: the vizhik pours out over the wet rock (the built escape, now with a real trigger), skarrin snap at anything crossing a wet path, karrek swarm the shallows and find any open cut. Netting doubles and the mirrik drop their cocoons; a colonist who walks the wet rock with a wound risks being stripped, and a raid that arrives in it fights among walking fish. The twelve "wind-hour" sentences get a true referent. ⚠ Not wind-hour: no daily clock, no ritual, no fog-hour choreography; the risk is the fish. **GPT's alternative, the Stone Lets Go** (§5 idea 4): saturated seams soften marked stone fins so mining, a blast or a blow drops the whole fin along a shown fall strip (shore it, or undercut it onto raiders). | 8 | `RM_MapComponent_PoolStock` (the vizhik escape), the pen fauna, `RM_CompVerminBreeder` (mirrik), the truce attribution for deliberate collapses | M |
| 4 | **The Dewsilk Casket** (§5 idea 5, GPT; technology): study of the mirrik's cocoon (its envelope holds the grub in arrested growth) plus seep-salt opens a research project; the casket seals a downed or willing pawn, or a captive animal, in biostasis as carryable freight, anywhere, and the clan buys and resells the membranes planet-wide. Lands the ruled dewsilk on the way. **BENCH's alternative, weeping masonry:** learned from the weep-faces, a cut-stone wall that sweats fed water on its shaded face and cools a room unpowered, anywhere (vanilla temperature only). | 2 | dewsilk (row 0), vanilla cryptosleep and the minified-container pattern | L (casket) / M (masonry) |
| 5 | **Teach the Fish to Lie** (§5 idea 3, GPT; sound): a stocked loomu learns an ancient vane array's chord, the maintenance credential of a sealed service lock; carried in a trough to a vault whose array fell silent, it gets one try. A clean echo opens it; a loomu that slips its keeper's name into the chord arms the sentries for good. The sound changes what opens. | 7 | the loomu (built), the trough as a breeding-stock item, a vault quest site | M |
| 6 | **A Salvation rite** (§6 R1 or R2). | 9 | found-rites row, `RUT_ResearchMod_GrantRite`, the truce component (R1) | M |
| 7 | **Art commission:** the walking array or the caravan rack (static overlay on the gorrask), the passage plate, the wet-rock and fish-on-land sprites, the casket, the trough, the rite's inscription; murrin catch item. Check the artpipe first (`artpipe_state.py find`). | all | artpipe | — |

🔴 **Sequencing:** row 0 first: the Fish Walk needs the murrin and the fixed text, the Passage and R1 need
the truce's both halves, and the casket needs dewsilk. `WEEPING_STONES_FIRST_SCRIPT_1` should be written
against row 0's state.

## 5. GPT consult: five ideas

Consult: `Transient/bedazzle_gpt_enrich_2026-10-02/weepingstones_gpt.md` (prompt beside it,
`weepingstones_gpt.prompt.md`), run 2026-10-02 under the standing rule (`BEDAZZLE_TOP_SHAPE_PROGRAM_1`,
ruling 2026-10-01): exactly five ideas, different from each other (GPT's own check: verbs escort / cede /
impersonate / undercut / encapsulate; systems contract delivery / gravship visitor access / acoustic
authentication / weather-driven structural failure / portable biostasis) and from every other biome's
signature, which the prompt listed in full, **including today's rulings for the Webwork, the Greentide, the
Rust Cathedral, the Rot and the Fever Wood** (urraveth, traction lance, Felled Noon; thurrock,
blood-stopping lace, Ceded Room, Open Boast; borehulk, stowaway spy bolts, Mending Weld, Stranger's
Overhaul; the gut that walks, Swallowed Navigator, Gut-Mother, Unjoining Draught, the Unjoining; the Brood
Ransom, the Oil Boil, rite none) and every pitch turned down there (the mooring, the pressure wedge, the
Gate Between, the Last Customer, Cutting the Stilts), plus the Weeping Stones' own dead verdicts (wind-hour,
the born-and-dying water). Model `gpt-6.1-sol`, high effort, via `gpt_consult.py`, answered first try
(started 12:12, written 12:24 PDT). GPT cites Death Stranding's deliveries and shared roads, VFE Settlers'
caravan raids, Odyssey's visitor clearance, Dredge's foghorn, VFE Ancients' vaults, Vintage Story's rock
collapse, Against the Storm's weather hazards, VFE Tribals and vanilla cryptosleep; its links are not
verified here. **GPT offered no rite** (all five aim at marks 2, 5, 6, 7, 8). On heat it read **overhead
sun, with ambient at the hot seep sites**, close to §1 (f).

**Names checked:** *last caravan*, *unspilling*, *stone lets go*, *dewsilk casket*, *refused toll* return
zero files in `src/`, `design/`, `infrastructure/state/items` (probe `korrum` 55 files). ⚠ GPT's name for
the old crab, **Korrav**, fails the stem rule: `korr` opens *korrum*, *Korrik*, *korrag*, *Korrak* and the
canon *Korriban*, and it rhymes with the gorrask itself; the card calls it "the oldest gorrask". *Pilgrim
road* hits `river_ledger.md`, so the ship idea is named **the Pilgrim Passage**; *squatter* is taken by the
settlement templates, so BENCH's giant option is **the Crab on the Hatch**.

| # | GPT's idea | mark | tier | size | BENCH read |
|---|---|---|---|---|---|
| 1 | **The Last Caravan:** the oldest gorrask wears a freight rack so mineralised its upright ribs look like a condenser; the manifest names a whole lost merchant caravan (sealed machine tools, trade bars, and the carrier itself), which a collector will buy intact across the canyon. Strip the rack now, or clear the old approach and escort the crab through its one move, guarding the cargo on the dry stretches; the contract closes for good. Campaign: the handlers were a lost Jawa clan. | 5 | free | L | **A real giant hook and the most Jawa of the five** (salvage now, or deliver and get paid). Close kin of BENCH's Walking Array (an ancient thing riding the crab); the Array ties the ship and three factions, the Caravan ties the trade. **On the card** as the second giant option. |
| 2 | **The Street Through Your Ship:** the landing shelf blocks the pilgrim approach; launch, or grant a permanent public passage, rebuilding a corridor through your ship where pilgrims and distrusted factions pass; closing it later is a recorded breach. | 6 | free | L | Bold and in the biome's voice (pilgrimage, the claim law), and nothing like any other ship mark. **Joined with BENCH's claim-law reading** (the truce holds round a chartered hull; a closed passage is the toll the Tribes punish) as **the Pilgrim Passage**, row 2. **On the card.** |
| 3 | **Teach the Fish to Lie:** a loomu learns a vane chord that is a lock's credential; one try at a silent vault; a slipped keeper's name arms the sentries forever. | 7 | free | M | **The only sound idea any sitting has offered that changes what opens**, built on a built creature's built line (*"repeats what it hears… its keeper's name"*), and a scavenger's break-in. Needs a vault site per array. **On the card.** |
| 4 | **The Stone Lets Go:** a saturated front softens marked stone fins; a blow drops the fin along a shown strip; shore it or drop it on raiders. | 8 | free | M | Strong and tactical (it changes what you dare mine or fight beside), GPT's first pick. Against BENCH's **Fish Walk**, which delivers his own stocked-pool words (*"Make the fish nasty and way too active"*), reuses the built escape and gives the twelve dead "wind-hour" sentences a referent. **Held in the doc as the weather alternative**; offered if he turns the Fish Walk down. |
| 5 | **The Unspilling Casket:** dewsilk plus seep-salt research; a portable biostasis casket for a downed pawn or a captive animal, carried as freight anywhere; membranes become a trade line. | 2 | free | L | **The strongest tech of the sitting**: learned here from a ruled creature, powerful (a rescue you can finish, animals carried without being released into another biome), balanced by research and membrane cost, and it lands the unbuilt dewsilk. Watch the build: an occupied, minifiable container through caravans, ships and saves is the real work. **On the card** as **the Dewsilk Casket**. |

GPT's ranking: the Stone Lets Go first, the Last Caravan second, the casket third.

## 6. Discoverable rites

Per `design/Jawa/salvation_rites_2026-10-01.md` (e): found at a site with a reason to be there,
learned through the Rites tab's found-rites row (`mandrake.rut.rites`), performable anywhere after.
Campaign tier. The binding rulings: **no god is evil**; **a rite gives cohesion, never a power**;
**favour shows only through events, world state and subtle odds**, voiced by the Narrator; a rite's
effect may be a dramatic, risky world event. Five-rite cap per god.

⚠ **He has answered "none" twice in a row** (the Fever Wood today: *"none, move on"*; the Sump, where
he declined all three and wrote his own). So this section offers only two, both built on a mechanic the
Weeping Stones already ships, and the card says plainly that "none" is a fine answer (by write-in; no
"none" option is printed).

**Cap count, by hand from the register's tables B2, B7 to B13 plus the ledger** (found rites only;
B4's controlled waking counted for Zizzik as the register does):

| God | Found rites | Count |
|---|---|---|
| Ishko | Dark Vigil (B2), Charged Reed, Stall-Hold (B7); the Sinking (Sump; Ishko's by question card 2026-10-02 06:24 PDT) | 4, one slot |
| Ohm | Engine Hour, Last Track, Deserter's Welcome (B7), the Answering (B8), the Stranger's Overhaul (B12) | **5, at cap** |
| Oomo | Sunning, Chime Vigil, Filtered Cup, Unspilled March (B7) (the Unlit Wedding is a variant, not counted) | 4, one slot |
| Mob'Unloo | Blind Offering (B2), Storm's Receipt, Cold Ledger (B7); Mob'Unloo's Price (Sump, ruled; not yet a register row) | 4, one slot |
| Sh'kaar | Snuffing (B2), Anvil Gift, Shade Tithe (B7), Felled Noon (B10) | 4, one slot |
| Ozzik | Lightless Burial (B2), Salted Keeping, Flawed Masterwork (B7), Ceded Room, Open Boast (B11) | **5, at cap** |
| Zizzik | Kept Mistake, Capping (B7), Nine Faults (B8), Struck Glass (B9), the controlled waking (B4) | **5, at cap** |
| Rekko | Unfinished Laid Down, Inherited Wreck, Mud Claim (B7), Mending Weld (B12) | 4, one slot |
| Ta'Baa | the Returned, Shadow Walk, Vindication Walk (B7), the Unjoining (B13) | 4, one slot |

The Fever Wood took none today, so nothing moved since the Rot. **Oomo is this biome's god by the sheet**
(*"the oasis is the Oomo water-archetype ground… this is Oomo's lesson in the hearts of the Jawa"*), and he
has exactly one slot: a rite here spends it, and the card says so.

**Not taken, and why:** an offering poured into the pool (offering water, taken); the first drink at a
pool (the Filtered Cup); a cup passed round (taken); carrying water past a mirage (the Unspilled March); the
dying oasis or a drought breaking the truce (the born-and-dying water is dead); anything at wind-hour
(dead); restoring a dead ring's silent machine (the Mending Weld's restore shape, and the Inherited Wreck);
a courtship at the pool (sentimental, and the ssurr already does it); an Oomo token left at a truce-stone
(a shrine of tokens is the Scrap Shrine's shape).

### R1. The Open Water, for Oomo: feeding, by carrying the truce to your own door (PITCHED)

- **Grounding:** Oomo is water, rationing and all the body's waters; *spilled blood offends him*. The
  truce is the sheet's own sentence for him: *"If there is enough for all, you take what you need and you
  leave."* The rite is that law, performed by the clan at its own water, wherever it is.
- **Found:** at a settled oasis (a Deepwater Compact post or a homestead pool), a truce-stone worn smooth
  at hand height, with a line cut round its base where generations of strangers stood; under it, a
  drinking-ladle chained to the stone, scratched *enough for all*.
- **Asks:** the participants declare the colony's water open for one day: wells, pools, the pump room. The
  rite **calls thirsty strangers** (traders, refugees, a wild herd, and, the point, at least one water
  party from a faction the colony is hostile to, warned a day ahead), and for that day the colony's water
  carries the Weeping Stones' truce: **the first guilty strike within the radius, by anyone, your own
  colonists included, turns the wild animals on the striker's faction** (the built retribution, carried
  off its biome by the rite).
- **Risk (the point):** armed enemies drinking inside your walls under a law that binds you; a colonist
  who loses their temper (a berserk, a grudge) breaks it and brings the herd down on the colony; an enemy
  party that breaks it is torn apart at your well. Success is that nobody strikes, everyone drinks, and
  everyone leaves.
- **Outcomes (cohesion only):** shared memories by quality; Oomo's favour told by the Narrator and shown
  only in his subtle odds. Whatever strangers leave behind is ordinary, never a reward.
- **Readable signs:** the warning letter, the strangers' parties marked as truce guests, the truce radius
  drawn round the water, the retribution letter if it breaks.
- **Collision check:** the Open Boast invites a challenge **against** you; the Gate Between (Fever Wood,
  not chosen) set two enemies on **each other**; the Last Customer and the Bought Quarrel (not chosen)
  invited enemies **to bargain**. The Open Water invites enemies **to drink and leave**, and the danger is
  the clan's own restraint. ⚠ It is still an invitation of enemies, the shape he passed on twice; said on
  the card.

### R2. The Refused Toll, for Mob'Unloo: feeding, by refusing a false debt in the open (PITCHED)

- **Grounding:** Mob'Unloo is debt and the sacred exchange; an exchange kept honest is his. The sheet's
  one barbarism is a toll on water the toll-keeper does not live on (*"forbidden, alien, even cruel.
  Barbaric"*), and the Empire's metering stations near its garrisons break it *as policy* (*"despised past
  politics"*). Paying it would be honouring a false debt.
- **Found:** at an oasis outside an Imperial garrison, a water meter torn off its post and laid face-down
  in the pool's ring, its dial jammed at zero, scratched *nothing owed*.
- **Asks:** the participants go to water that is metered by someone who does not live on it (an Imperial
  metering station, a new campaign quest site; or any faction post the claim law convicts), draw in the
  open, and walk away without paying, in sight of the meter.
- **Risk (the point):** the toll-keeper answers (an Imperial patrol, warned in a letter); and if a
  participant strikes first at that water, the truce, which binds the clan as much as anyone, turns the
  wild herds on the clan. The clan must refuse the debt and not start the fight.
- **Outcomes (cohesion only):** shared memories by quality; Mob'Unloo's favour told by the Narrator, shown
  only in his odds; the Deep Desert Tribes hear of it (world state, not a reward).
- **Collision check:** the Cold Ledger **pays** a real debt; Mob'Unloo's Price curses a hated faction; the
  Storm's Receipt and the Blind Offering are offerings. None **refuses** a debt. ⚠ It needs a metering
  station site that does not exist yet (campaign), and it spends Mob'Unloo's last slot.

GPT offered no rite; nothing from §5 is repeated here.

## 7. Draft turn-1 card

Plain language, no def names in option labels, headers 12 characters or fewer, every question ends in
"?", and no option is a "none" (the card's own write-in line covers that, and above question 4 say that
"none" is a fine answer there). Above the card, read him §0's description of the Weeping Stones, per the
standing rule that he is never assumed to remember. Say in one line above it that **the baseline pool fish
can't be caught anywhere, the truce only half works (predators can still hunt at the water), the dewsilk
cloth was never made, and every oasis grows Earth palms (including the date palm he banned) through a
landmark patch that only names the old donor biome**, while the Mod Settings screen is honest but thin.

**1. Build first** (header `Build first`) — *What should be built first for the Weeping Stones?*
- **Land what was already decided (recommended):** make the baseline pool fish catchable, finish the
  truce so predators never hunt at the water, make the dewsilk cloth from the dew-smoke swarm's cocoons,
  set its heat by the sun's height (shade under the overhangs is what saves you at noon), rewrite the
  twelve descriptions that still mention the cancelled wind-hour, take the palms out of every oasis and
  register the biome with the oasis landmark properly, and add real sliders to its settings. Buys: every
  promise in the September sitting comes true. Costs: a medium batch, no new mark this round. *Why: the
  weather, ship and rite ideas below all lean on the truce and the fish.*
- **Land it and add the giant's story together:** Buys: a hook on the crab now. Costs: a bigger first
  batch.
- **New ideas first, landing later:** Buys: new marks sooner. Costs: predators keep hunting at sacred
  water and the banned palms stay at every pool.

**2. The giant** (header `The giant`) — *Which story should the canyon-sized stone-crab carry?*
- **The walking condenser (recommended):** the oldest crab grew an ancient water machine into its shell
  and it still runs: wherever the crab settles for a season, a pool forms round it, truce and all. Three
  powers want it (cultists who want to wake the machine, a Hutt who wants it for a palace pool, and the
  water stewards who say it belongs to no one). The clan can guide it onto its own land for a season, sell
  where it will settle next to the highest bidder, or cut the machine out, ending the moving oasis but
  getting the last working ancient condenser as a water plant for your ship. Buys: a giant tied to the ship,
  the factions and the trade. Costs: a large build. *Why: it makes the crab the biome's own idea (stone,
  machine and animal you can't tell apart) and gives the clan a broker's choice.*
- **The last caravan:** the oldest crab carries a stone-crusted freight rack: a whole lost merchant
  caravan's cargo. Strip it for salvage now, or escort the crab on its one move across the canyon and
  deliver the caravan whole to a collector for a much bigger price; in the campaign, the lost traders were
  a Jawa clan. Buys: the most Jawa of the stories. Costs: a large escort-quest build.
- **The crab on the hatch:** a crab settles on your pool for its season and the truce protects it; wait,
  or coax it off with a culled tyrant fish from your pens. When it moves it uncovers a sealed ancient
  cistern hatch with a cache inside, and the bounty hunters who've been quietly drinking at your pool
  knew all along. Buys: ties the fish pens, the truce and the oasis caches together. Costs: a medium
  build.

**3. New marks** (header `New marks`) — *Which new ideas should be built (pick any)?*
- **The fish walk (recommended):** a heavy dew-front (no rain, no daily clock) sheets every rock in
  running water and the pool fish leave the water: eels pour over the wet rock, jumpers snap at anyone on
  a wet path, the swarm fish find any open cut. Netting doubles and the cocoons drop, but walking the wet
  rock wounded is dangerous, and a raid that comes in it fights among walking fish. Buys: weather that
  changes what you dare do, built on fish you asked to be "nasty and way too active". Costs: a medium
  build. *Why: it reuses the built pens and escape, and gives the cancelled wind-hour lines something true
  to describe.*
- **The pilgrim passage:** your best landing spot blocks the pilgrims' path to the water. Launch, or grant
  them a permanent passage: rebuild a real corridor through your ship that pilgrims and even distrusted
  factions walk, while the truce protects your hull from anyone who strikes first there. Close it on a
  later visit and the desert tribes treat you as a toll-keeper and come for the ship. Buys: the place
  acting on your ship in its own law. Costs: a large build.
- **The dewsilk casket:** learn from the swarm's cocoons and the seep-salt how to seal a dying pawn or a
  captive animal in a carryable sleep-casket, usable anywhere, and sell the membranes across the planet.
  Buys: a rescue you can finish and a trade line. Costs: a large build (research and membranes balance it).
- **The fish that lies:** teach a mimic fish an ancient machine's chord and carry it to a sealed vault
  whose own machine went silent: one try; a clean echo opens it, but if it slips in its keeper's name the
  guards arm for good. Buys: a sound that opens doors, a scavenger's break-in. Costs: a medium build.

**4. Rite** (header `Rite`) — *Which rite should the Salvation find at the Weeping Stones?*
- **The open water, for the water god (recommended):** the colony opens its water to every thirsty
  stranger for a day, enemy water parties included, and the oasis truce holds round your well: the first
  to strike, even one of your own, brings the wild animals down on their side. Success is that everyone
  drinks and leaves. Buys: the biome's own law made sacred, a tense and risky event. Costs: a medium build;
  armed enemies inside your walls; it is another invite-your-enemies shape like two you passed on; it uses
  the water god's last free rite. *Why: the sheet calls the truce this god's lesson, and it carries the
  built truce anywhere.*
- **The refused toll, for the god of debt and trade:** go to water metered by someone who doesn't live
  there (an Imperial metering station), draw in the open and walk away without paying; the toll-keeper
  answers, and if one of yours strikes first the truce turns on the clan. Buys: a bold trader's defiance
  of the Empire. Costs: a medium-to-large build (the station site is new); uses that god's last free rite.

Held off the card (in the doc only): the stone lets go (§5 idea 4, the weather alternative), weeping
masonry (§4 row 4, the tech alternative).
