# The Contagion — definition sheet

_Owner + BENCH, 2026-09-06, written in conversation over three passes. Defines
`AB_OcularForest` (Alpha Biomes' "Ocular Forest" — donor content incorporated wholesale,
then bent). **The biome's name is THE CONTAGION** (owner's pick; the earlier working name
"the Overdrive" is superseded). Thematic handle: **the weapon at open throttle** — and its
image: **a red valley under a storm that never stops, where the clear sky is the thing to
fear.**_

🔑 **Read against `assailant_weapon_remnants.md` and its siblings.** The Assailant
bioweapon's fourth end: here it **malfunctioned yet again — so aggressive it is in its own
way.** Mutation upon mutation, it changes forms faster than it can finish the last one.
Ferociously effective at infecting, hopeless at holding. Hydrology canon already on record
binds it: **R-H1** (rain falls only at the greatest altitudes), **R-H7** (the ocular
forests are the one large organism with unlimited water, excreting red-flowing water
loaded with reproductive spores and alien toxins that leave the stream before the
lowlands — the rivers arrive clean), **R-H8** ("genetically wrong on purpose," "rare and
horrible," Ascendant Helix territory and a live bioweapon test ground).

## 0. The measurements everything rests on

MEASURED 2026-09-06 off `world/ASHKARR_WORLDMAP_tiles.csv`. The planet's median rainfall
is **0 mm**; one region rains prolifically — **Scald Spine**: 174 tiles, rain median 973 mm
(max 1,529), 73 river tiles, elevation to 2,001 m, 41 °C, arc 48. The donor's current 3
tiles sit in the Ashfall Range (8/4/271 mm, no rivers) — the wrong home; they move.

🔴 **Placement ruling (owner):** the Contagion lives on the **peaks above the green** and
**takes NO green squares** — the jungle/oasis defs below (CypreJungle, Feralisk jungle,
Desert Oasis) are precious and get their own definition. Candidate set (MEASURED,
non-green only): Scald Spine's 38 high tiles (Volcano 18, Badlands 13, LavaField 7; elev
median 1,170 m), plus — for presence, at the owner's option — the neighboring ranges'
tops: Ashfall Range 35 tiles ≥1,200 m, Dew Horn 137 tiles ≥1,200 m (70 at ≥1,500). Exact
list ruled in `CONTAGION_BIOME_PLACEMENT_1`.

Donor inventory taken in: `AB_RedFog` (commonality 17 vs Clear 8; **ranged accuracy
×0.4** plus a mood hit), animal density 3, plant density 0.35, **forage 0.1** (nothing
here feeds you), the ocular flora and fauna (§4), the `GU_RedWater*` terrain overrides
(🔴 do-not-touch per the boiling-lift spec), and the scald-weather assignment
(`Jawa_ScaldDrizzle/Rain/Fog`) already made for this def. Vanilla tail (rat, hare,
iguana) **evicted**.

## 1. What it is

A red valley on a scalded mountain, roofed by a thunderstorm that has not stopped in a
thousand years. Under the cloud everything is wet, warm, and *unfinished*: trees half-way
to being something else, animals with one design completed and two abandoned, ground that
is itself an organism budding new attempts every hour. And then the cloud tears — and the
sun comes through like a sterilizing lamp, and everything alive dives for cover, because
here the clear sky is the killer. The rivers that leave this place arrive in the lowlands
clean. What they carried died in the light on the way down, and became the fertilizer of
every green valley beneath.

## 2. Planetary position

**Mid-dayside regime (arc ~48, abundant energy) × the altitude-rain anomaly (R-H1).**
The only place on the dayside where energy AND water are unlimited — and so the only
place the weapon's mutation engine ever runs without a governor. **Rings never form
because this is a point on the peaks, not a band.**

## 3. Driving forces

### Open throttle

Everywhere else the weapon is water-limited. Here it isn't, so it runs open-loop:
mutation faster than completion, each form abandoned mid-build. Very effective at
infecting; incapable of consolidating. **It is in its own way** (owner's ruling).

### The UV cage (owner-ratified mechanism)

The volatilization R-H7 describes is **sunlight**: the dayside's intense UV sterilizes
the red water before it reaches the basins — strong enough to break even the Contagion's
spores. That is what keeps it trapped beneath the perpetual churning thunderstorm over the
scald mountains: the cloud is the one thing between the weapon and the light. The dry,
bright edge is its quarantine; the desert does not fight it, the desert just stops
shielding it.

### The Burn and the Bloom — inverted weather (owner-ratified)

The storm is never uniform; it tears and heals. Every tear is a **Burn**: raw UV lances
the valley floor for minutes — **radiation counts go up, the air becomes a sterilizing
chamber** — and everything native dives: into the red water, under the canopy, into the
goo. Anything caught in the open scorches. Then the cloud closes and the **Bloom** follows:
the goo, fed on what the Burn killed, buds furiously. 🔑 **Clear weather is the terrifying
weather here.** It is also the player's window: during a Burn the red fog lifts, ranged
weapons work, and the natives are hiding. Move in the Burn; hide in the Bloom.

### Downstream: the planet drinks from it

The red water sterilizes on the way down (R-H7), so **every dayside river the shrubland
and desert depend on rises in the Contagion's valleys** — and the dead organic matter it
sheds fertilizes the green jungles below (owner's ruling). The spore blooms downwind are
where the poison went instead.

## 4. How the biology adapted

**The admission test: UV-shy or UV-armored.** Every native either dives at the Burn or is
plated against it. What they do all day is *read the sky*.

| creature | role | all day |
|---|---|---|
| **Red Goo** (donor 0.75) | the body | The weapon's tissue, "an extension of the terrain itself" — creeps uphill to the rain line and downhill to the river, eats everything dead, **buds new forms every Bloom** and reabsorbs the failures. Never the same shape twice. |
| ⭐ **the Unfinished** (authored line) | the experiments | What the goo buds: chimeras with one design finished and two abandoned — three good legs and a stump, one wing, a jaw on a thing that cannot eat. Days-long lives, then dissolution back to goo. **Random-stat, short-lived spawns; the most numerous creature and the least permanent.** 🔴 **They can become dangerous** (owner's ruling): most are nuisances, some roll a monster. Random limbs ride the engine's own mechanism — `Hediff_AddedPart` grants with melee verbs, the pattern the consumables plunder already found. |
| **Ocular Jelly** (2.0) | the eyes | Drifts at canopy height watching the cloud — the Contagion's sensory organ. **Sinks seconds before a Burn**; the natives watch the jellies, and so can a player who learns the tell. |
| **Infected Aerofleet** (0.5) | the sower | Rides the storm updraft with spore-loaded gas, drifts over the ridge — and **pops in the sunlight**, spores dead before they land. The escape attempt, failing a hundred times a day; the rim is littered with husks. |
| **Red Spore** (0.85) | the leaker | Gallium-based, not carbon — walks a few meters into the light. Carries live tissue in its shell toward the valley mouth and almost always cooks first. The rare one that doesn't seeds a spore bloom downwind. |
| **Blood Shrimp** | the drinker | Water is everywhere, nutrients are not — it hunts warm blood at the red pools. **The reason visitors die at the water's edge.** |
| **Helixien slug** | the undertaker | Corrosive disposal of the Unfinished, faster than the goo reabsorbs. |
| **Drainer + larva** | the thieves | Tap the ocular trees; ruinous to anything a visitor tries to grow. |
| **Rough-plated monitor** | the basker | UV-armored — comes OUT in the Burn to eat scorched Unfinished in the open. Predator-of-the-window. |
| **Razorjack, Swarmling** | the pickers | Fast omnivores on the carcass economy. |

**Flora — the infection front, walkable.** Peaks: ocular trees, ocular grass, the
aberrations — "not even 100% carbon based." Downslope: the **half-transformed trees**
(donor lore verbatim: "a strange infection transforming this regular oak") — the front
line, advancing in Blooms, burned back in Burns. Below: the burn line of sterilized
matter; below that, the green. **Tentacular aberrations rattle before a Burn** (a second
tell). **Globular aberrations drip red sap** that keeps insects off. The **blood
bouquet**'s spine-armored seed rolls to the burn line and dies there as fertilizer.

## 4b. Weather — inverted

- **The Bloom** (the storm; donor red fog re-skinned): the standing state — wet, fogged,
  accuracy ×0.4, everything budding.
- 🔴 **The Burn** (the Clear): rare tears in the cloud — UV sterilization, radiation up,
  natives hidden, fog lifted. The only weather here that kills, and the only one that lets
  you shoot.
- **Scald rain** (`Jawa_ScaldDrizzle/Rain/Fog`, already assigned): the near-perpetual
  high-valley rain — R-H1's one legitimate rain on the dayside.
- **Spore blooms** downwind (weather-suite §6) are this biome's export event.

## 5. Always true

- Nothing native is finished; forms are mid-sentence and reabsorbed within days.
- The cloud is the cage; the clear sky is lethal to everything native and hostile to
  visitors (dose, burn).
- The red water is poison until the sun has had it — a day in the open sterilizes a tank.
- Forage is nil: **nothing here feeds you.**
- Ranged fire is near-useless in the Bloom; knife country.
- The rivers leave clean; the dead matter feeds the green below.
- **The Ascendant Helix watch** (owner's ruling): they love the genetic diversity of the
  out-of-control weapon's creativity; observation posts at the valley mouths.

## 6. Never true — 🔴 HARD BANS (linter-checkable)

1. 🔴 **No green squares taken** — the jungle/oasis defs below are never re-biomed into
   the Contagion; a Contagion tile on a former green tile is a violation.
2. 🔴 **No Contagion life outside the storm shadow** — native defs cannot persist under
   open sky; a UV-immune native (other than the ruled leakers/armored) is a violation.
3. 🔴 **No finished natives beyond the ruled table** — a long-lived, stable new resident
   def contradicts open-throttle; the Unfinished are short-lived by law.
4. 🔴 **No edible forage** — the biome never feeds a visitor.
5. 🔴 **No ranged-accuracy exemption in the Bloom** — red fog's ×0.4 stands.
6. 🔴 **Contagion-touched never upgrades you** (owner's ruling, §7) — a net-positive
   mutation outcome is a violation.
7. 🔴 **The war-legacy split holds** — this is Assailant arsenal, never Wasteland content.
8. 🔴 **The recognizability rule applies**; the icon carve-out protects in-universe
   references.

## 7. Uniquely available

- ⭐ **Water — the only unlimited water on the dayside**, red and lethal until sunned:
  fill at the pools (past the shrimp), purify at the valley mouth by the planet's own
  method. Rides the water taxonomy (`WATER_KINDS_TAXONOMY_1`): *red water → sunned →
  potable* is one transmutation of many.
- ⭐ **Contagion mulch — the best fertilizer on Ash'karr.** Sterilized dead goo is what
  makes the green squares green. Sunned, super-compost; un-sunned, it infects your field
  and ocular grass takes the farm.
- **The genetic lottery** — every Unfinished corpse is novel tissue; the Helix pay for
  samples; it rots to goo in hours.
- **Gallium** off Red Spore shells — electronics feedstock, Jawa tinkering gold.
- **Red sap** — insect repellent and wound-sealant.
- **Knife country** — pursuit with blasters means nothing under the Bloom; refuge priced
  in biology.
- 🔴 **Contagion-touched** (owner's ruling): spore exposure starts **much larger, more
  random mutations** — not merely genetic shuffling: the survey of the stack's OTHER
  mutation systems (`MUTATION_MODIFIERS_SURVEY_1`) feeds it — with the bad genes
  definitely in the deck (genetic instability and kin). **It never just upgrades you. You
  do not want this.** Cure: unruled — lean is *arrest, not reversal* (sun/purge stops
  progression; what already changed stays).

## 8. Inhabited objects

- ⭐ **The Ashfall Research Base** (owner-named; the custom dungeon, `OCULAR_OVERDRIVE_SITE_1`
  carries it): the Helix's live study of the weapon. One line of plot only, by the owner's
  instruction — the base's datafiles reveal the Helix–Assailant relationship and their
  active attempts to make the Contagion more robust and productive, at the risk of
  unleashing it planet-wide. Everything else about it is that item's.
- **Helix observation posts** at the valley mouths — watchers, buyers of samples.
- **The Rust Cathedral's enmity** — ideological, carried from the remnants ruling.
- **Burn shelters** — natural and built: the overhangs and goo-pockets every native
  knows; the ruins of visitors who learned the clock too late.

## 9. Artistic theme

**"A red valley under a storm that never stops, where the clear sky is the thing to fear."**

- **Light:** storm-dark red under the Bloom; then the Burn — a white shaft of sterilizing
  sun, the valley suddenly, horribly bright, everything scattering.
- **Palette:** red water, red fog, pink-and-blue aberrations, the grey-white of husks and
  sterilized matter at the burn line, green far below.
- **Silhouette language:** the unfinished — asymmetry everywhere; trees half-converted;
  creatures that read as drafts.
- **Motion:** budding, dissolving, diving; the jellies sinking as one before the light.
- **Sound:** endless rain and thunder as the baseline; the tentacular rattle; silence in
  the Burn.

---

## Owed

- `CONTAGION_BIOME_PLACEMENT_1` — 🔴 **widened (owner, 2026-09-06, Badlands sitting): put
  the Contagion everywhere it reasonably can go, as a world presence — every rain-receiving
  non-green high on the dayside — so long as there is an excuse it is sterilized before
  flowing down** (the UV cage on the descent). A tall mountain stays its host biome's
  ONLY if it gets no rain from the Scald's storms; a peak that rains and stayed clean would
  "seem odd that it couldn't infect downstream." The 3 Ashfall Range strays fold in; the
  green below defined separately.
- **Art: the half-transformed tree** (owner's player note): redo it so it does not say or
  look like a "half oak" — a **"half plant"**, alien on both halves. NEW-ART ledger; rides
  the tree-ownership work (`TREE_GRAPHICS_OWNERSHIP_1`).
- `WATER_KINDS_TAXONOMY_1` — the owner's cross-cutting call: many kinds of water, by
  content, and the transmutations between them.
- `MUTATION_MODIFIERS_SURVEY_1` — survey every mutation-type system in the stack before
  authoring Contagion-touched.
- **The Unfinished** — art line (NEW-ART ledger) and the C# spawner (random stats,
  random `Hediff_AddedPart` limbs, short lifespan, goo-corpse).
- **Engine feasibility pass:** the Burn as a weather with radiation + UV damage to
  natives; the jelly/rattle tells; the sun-sterilization of hauled water and mulch
  (a timed item transformation in sunlight); mulch that infects fields.
- **The green below** — CypreJungle / Feralisk jungle / Desert Oasis want their own
  short definitions (owner: "precious, just need some more definition").
- **Contagion-touched cure ruling.**
- Doc hygiene: the wasteland sheet's "no rain planet-wide" paraphrase corrected to R-H1's
  actual text this commit; the primary R-H rule list was not located this session
  (cited via the weather/shields/boiling-lift specs) — find and link it.
