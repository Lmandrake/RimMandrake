# The Weeping Stones — definition sheet

_Owner + BENCH, 2026-09-06, written in conversation over three passes. Defines
`ZBiome_DesertOasis` (More Vanilla Biomes, Zylleon — a thin donor whose one real gift is
mechanical: terrain patch-makers that paint genuine standing water into sand). **The
biome's name is THE WEEPING STONES** (owner's pick). Thematic handle: **tended water**
— and its image: **stone that sweats on its cold faces, and everything alive or built
crowding around to drink the wind.**_

🔑 **Read against `the_cracked_lands.md`** — the sharpest contrast on the map. Cracked
Lands green *hides* in canyon shade waiting for a rare flood; Weeping Stones green
*climbs* — it stands on the high cold faces and drinks the wind daily. Fugitive water
vs. tended water. Also read `sacred_sites_pass_1.md`: the oasis is the **Oomo**
water-archetype ground, and this sheet is that archetype made physical.

🔴 **Architecture ruling (owner, 2026-09-06): biome + landmarks.** The BiomeDef defines
the dew-country ground. Each actual pool is a hand-placed, hand-named vanilla **Oasis
LANDMARK** (Odyssey `LandmarkDef Oasis`, required `TileMutatorDef Oasis`) with a chosen
companion-mutator loadout — AnimalLife_Increased, AnimalHabitat, Stockpile,
AncientUplink, or none. Each oasis distinct, sacred, visible on the world map, placed
by us, never rolled.

## 0. The measurements everything rests on

MEASURED 2026-09-06 off `world/ASHKARR_WORLDMAP_tiles.csv` (21,872 rows,
sha256:b38fd68569237c96): **236 tiles**, scattered wide across the dayside — arc
26.3→79.9 (median 58.0 — the sun **32° above the horizon** at the median, but
individual tiles run from ~64° light down to ~10° near the terminator). Temp
p10-context median 35.5 °C (17.8..63.5). Elevation median **612 m** — this biome sits
high. Hilliness genuinely mixed: 81 small-hill, 56 flat, 48 large-hill, 50 mountainous,
1 impassable. **Water tiles 0, river tiles 1** — the biome named for water has almost
none at world scale; the pools are map-scale. Regions: **Dew Belt 92, Dew Horn 66**
(two-thirds of the biome — the map's own names voted for the engine), Dune Sea 36,
**Scald Spine 24, Anvil 11** (the hot aberrants, §2b), Hollow Verge 7.

Not a rung on the dryland ladder (ExtremeDesert 47° → Cracked Lands 22° → Desert 14° →
Shrubland 9° → Wasteland −10°): the arc spread 26→80 says *scatter*, not band. This is
an anomaly biome — it occurs wherever high stone stands in the moisture corridor.

Donor inventory (read from the mod XML, workshop 1931453053): **kept in spirit** — the
terrainPatchMakers (perlin 0.03/1.8) painting WaterShallow/Mud/SoilRich/Soil/Gravel
islands in Sand/SoftSand, and animalDensity 1.5 (accidentally right, §4). **Evicted** —
the vanilla fauna (iguana, dromedary, boomalope, ostrich, emu, gazelle, cougar,
fennec). **Replaced** — the vanilla flora (grass, cacti, palm, agave, drago, chokevine,
healroot…). **Stripped** — SnowGentle 4 / SnowHard 4 in baseWeatherCommonalities (a
donor absurdity at 35 °C), forageability re-pointed off RawAgave when the roster lands.

## 1. What it is

High pale stone standing in the path of the sea-wind. Most of this country is bright,
dry, wind-scoured ridge and shoulder — but every cold shaded face of it *weeps*: thin
black streaks of wet running down white rock, moss and mat-growth crowding the seep
lines, and here and there, where the catch is good enough, a true pool with a green
ring around it and a crowd at the water. An oasis here is never merely found water. It
is a *working thing* — part stone, part machine, part congregation of everything that
drinks — and every single one is different.

## 2. Planetary position

Mid-dayside scatter, arc 26–80, wherever **altitude intersects the moisture corridor**:
the day→night convection cell drives surface wind from the cold side toward the
substellar heat, and that wind crosses the torn seas on its way in — it arrives on the
dayside *wet*. Two-thirds of these tiles sit in the Dew Belt and Dew Horn because that
is the corridor. The anomaly is high stone (median 612 m) forcing the wet wind up.

**2b. The seep oases (owner, 2026-09-06).** The Scald Spine and Anvil tiles (35 of
236, up to 63 °C) are too hot for the dew engine. These — and others near vulcanism —
are **seep oases**: fed from *below*, groundwater and vent-warmed springs rising
through the rock, often on open flat ground with no adjacent stone at all. Especially
amazing, especially magical — a green eye in open nothing. **It is still the Weeping
Stones: the stones are beneath the oasis now.** Mineral-tasting water, the strangest
relic states, the ones travelers tell stories about. What feeds each of them is ruled
under `VAPOR_EMITTER_PLACEMENT_1` (steam sources radially decay from
mountains/vulcanism, zero before the terminator).

## 3. Driving forces

Damp sea-wind forced up over high stone drops its water on cold shaded faces — **water
is combed from moving air, never rained** — and every drop an oasis holds it is also
losing upward, so everything around a pool works to catch, keep, and re-catch it.

## 4. How the biology adapted

**The convergence (owner's commit, 2026-09-06): combing water from wind has one right
shape — a thin upright surface held into the airflow — and everything here uses it.**
The Earth proofs: fog-net harvesters (vertical mesh on ridgelines) and the Namib
beetle (tilts its ridged back into the fog wind and drinks with its back). So:

- **Plants grow as blades**, not bushes — upright fins of leaf facing the prevailing
  wind, drip-tips feeding their own roots. Mats on the stone are ridged like corduroy,
  every ridge square to the sea-wind.
- **Animals carry raisable crests and combs** — spine-fins fanned open when the wind
  runs, then licked dry; dew-grooves running to the mouth.
- Nothing here lives on soil; everything lives on **stone-shade real estate** — the
  cold faces, the overhangs, the seep lines. Fertility follows the patch-makers, but
  the *life* follows the shade.
- The pools are the only reliable standing fresh water on the dayside, so every big
  animal on the hot half of the world must come here. The donor's animalDensity 1.5
  was accidentally right — this is pilgrimage density, not abundance.

**The truce (owner, 2026-09-06, near-verbatim).** At the water, the truce holds —
completely. It is strangely sacred, especially for such a deeply dangerous world: it
radiates through all animals, and eventually all cultures respect it here, even those
from far away with very different ideas of morality. Even the Jawa — who specialize in
trade, profit, and salvaging things slightly before they were ready — feel it. **If
there is enough for all, you take what you need and you leave.** Only if the water were
drying up does the truce break — a sudden violent scuffle as the last of it is taken;
survival is survival. Among animals the truce is enforced as mutually assured
destruction: a herd of prey can harass a predator to death before it drinks, and the
predators can do the same back. Water is always MAD, or peace. This is **Oomo's lesson
in the hearts of the Jawa, radiating outward and made manifest everywhere.** And the
pools are more than drinking — they are places of romance, play, bonding, and breeding
rituals. It simply must be.

**The claim law.** Walling off access is valid — *if you settle it*. Building a
settlement on the water and defending it is legitimate to everyone, Jawa included; the
Jawa rarely settle, so they pay for access and understand this. But **making someone
pay for water you do NOT live on is forbidden, alien, even cruel. Barbaric.** No
toll-keepers, no absentee water-lords — the map and factions must never present one.

## 5. Always true

- Every cold shaded face weeps; the wet black streak on pale stone is the biome's
  signature mark at every scale.
- **Every native plant and animal carries the wind-comb shape** — an upright fin,
  crest, blade, or comb in its silhouette (hard rule; drives every sprite).
- Every oasis is *tended*: over time, no matter how wonderful, it accrues both
  biological adaptation around it AND intelligently designed systems — ancient and
  modern — working to capture, replenish, and grow it (owner's commit).
- **The recapture ladder** exists in some state at every developed oasis: an open pool
  radiates its water back up, so shields → overhangs → full enclosure is common, and
  the ultimate form is **servo-driven vents that open to accept water when the wind
  brings it and seal the moisture in otherwise** — the endgame of a large settlement
  built around a pool at the base of a rock.
- The truce holds while there is enough; the sea-wind always runs.
- Each oasis is individually different — its relic state, its ladder rung, its water
  source, its name. The landmark loadout is that difference made mechanical.

## 6. Never true — hard bans, written checkable

- ⛔ No vanilla-Earth flora or fauna in wildPlants/wildAnimals (all-alien;
  terrestrial-analog allowed, per the standing eviction precedent).
- ⛔ No snow: baseWeatherCommonalities carries no SnowGentle/SnowHard entry.
- ⛔ No rain-fed ecology: no native's water story is rainfall — a def or description
  that drinks rain here violates the sheet.
- ⛔ No native without the comb: a Weeping Stones sprite with no upright
  fin/crest/blade element fails art review for this biome.
- ⛔ No ambush-at-water predator: no roster entry whose hunting story is the pool
  margin — violence lives on the approaches and in scarcity, never at full water.
- ⛔ No toll on unsettled water: no faction, settlement, or story element charges for
  access to an oasis it does not physically inhabit.

## 7. Uniquely available

- The only reliable standing fresh water on the dayside — and under the truce, the one
  place a colonist can stand beside every dayside animal in peace: the best taming,
  bonding, and observation ground on the planet.
- Relic condenser tech: vane arrays and cistern shafts to salvage — or restore. A
  working ancient condenser is a water economy.
- The landmark loadouts: one oasis holds the **ancient uplink**, one is an animal
  haven, one hides a stockpile cache, one is a dead ring of bones around a silent
  machine.
- The recapture ladder as an aspiration: the enclosed, servo-vented oasis settlement
  is the visible endgame of desert wealth (structure/buildable work — future item).
- Romance and ritual: recreation, bonding, and breeding at the pools, for the wild and
  the tame alike.

## 8. Inhabited objects

The succession ladder, oldest to ultimate — and every oasis sits somewhere on it:

1. **The natural weep** — bare seep lines, mats, a catch-pool. No hand has touched it.
2. **The ancient vane arrays** — the ancients found the best traps and built on them:
   upright condenser fins facing the wind, water sheeting into sunk cistern shafts.
   Millennia on, each installation drifted into its own state: one still runs cold and
   true and holds a real pool; one leaks and made a hanging marsh; one runs half-wild
   and floods its canyon with fog; one died, and its oasis is a dry ring around a
   silent machine.
3. **Shields and overhangs** — modern hands catching the pool's own breath: stretched
   awnings, stone lids, walled windbreaks.
4. **Full enclosure** — the servo-vented dome or sealed grotto at the base of a rock,
   vents opening to the wet wind and sealing shut after it, a large settlement grown
   around it. Settling the water this way is a valid claim (§4); the unsettled version
   of the same wall is the one barbarism.

Between oases: caravan infrastructure — cairns, dry cisterns, camp rings. The oasis
string is the bead-chain the desert roads follow.

## 9. Artistic theme

**One silhouette rule: the upright comb.** Fins, vanes, crests, blades — machine,
plant, and beast all converge on it, and at a distance you cannot tell the relics from
the living. That ambiguity is the sacred register: is the machine alive? Was the plant
built? The biome radiates one shape.

Palette: **bone-white sunlit stone; wet black weep-streaks; green held in blue shade;
verdigris where metal meets moss.** Light: hard glare above, cool gloom under the
overhangs; enclosed oases glow at their vent-slits. The seep oases inverted: a green
eye ringed in open flat nothing, no shade at all, impossibly lush — read as magical
because the engine is hidden beneath.

The map-scale read is already ruled (`biome_and_fauna_roster.md`): **concentric
rings — water, then green, then scrub, then sand, in visible bands. The most legible
tile on the world, and it should look designed.** The comb rule nests inside it: the
rings are the plan view, the combs are the elevation.

---

# The enrichment pass — BENCH, 2026-09-06; the owner's pass is owed on all of it

_Beasts, items, furniture, structures, and the faction faces of the water. Sections
10–12 are proposals at sheet register; nothing below is a def yet._

## 10. The bestiary — who comes to the water

The concentric rings apply to the fauna too. Three rings: **residents** (live here,
comb-carrying natives), **pilgrims** (the neighboring biomes' animals, drawn in — the
"HIGHEST density on the planet" ruling is mostly *visitors*), and **the margin** (what
hunts the approaches, never the pool). The `ikee` is already placed here, uncommon
(`fauna_placement.md` — "near water and traffic"; an omen, never a herd).

**The standing cast must be reconciled first.** MEASURED 2026-09-06 off
`design/Jawa/fauna/cast_assignment.csv` (sha256:0331f6610967ba7f): **29 species are
already cast to this biome**, assigned before this sheet existed, and it shows — a
grab-bag of cave bats, polluted-lands toads, a Rancor, a mutating tumorfish. Graded
against the sheet: ⭐ **the Fanback** (Star Wars Animal Collection, large) is a gift —
a creature with a literal fan on its back, already here; **the comb convergence was
waiting for us.** Obvious keeps: Fanback, ColossusToad, Dactillion (the flier mount),
Ollopom, Boma. Obvious violations for `WEEPING_STONES_ROSTER_1` to evict or re-home:
every ambush predator (§6 ban — Narkospider, Razorjack as-flavored), anything whose
body is a pollution story (TumorfishAdult, TaintedTurtle — sacrilege in this water),
and the Rancor (a truce pool is the one place it cannot star). The cast file is
curated — nothing moves until the roster item, except that the eviction *criteria*
are now this sheet's §6.

Names below follow `Alien_Bestiary.md` §1 and the clade roots; every native carries
the comb (§5). Collision-checked against `creature_names_ashkarr.md` and the bestiary.

| name | clade | what it is |
|---|---|---|
| **dewback** | canon | 🔑 **Already LIVE in the mod set** (Star Wars Animal Collection) and mis-cast to `LavaField` (`cast_assignment.csv:769`) — the films' dew-drinking lizard, standing on lava. **Proposed: reassign here.** The archetype resident; its ridged back is the comb the whole biome converges on. |
| **tirbak** | mount `-bak` | The walking cistern. A placid colossus that drinks once per wind-cycle and carries it for days; dorsal rain-fins it fans to the wind. The caravan mount of the oasis string; replaces the donor's muffalo/dromedary/elephant pack list. Nickname: *tanker*. |
| **burrak** / **burradar** | heavy `-rak`/`-dar`, elder-form ladder | The well-digger. Wallows and digs catch-basins that outlive it — abandoned burrak digs are how new micro-oases start. The elder **burradar** digs the deep wells; a working oasis tolerates one the way a town tolerates its engineer. Claw-combs. Nickname: *well-digger*. |
| **sillik** | small-quick `-ik` | Lives on the vertical weep-faces themselves, licking the film; whisker-combs around the muzzle. The prey base. Nickname: *weep-mouse*. |
| **mirrik** | insectoid `-rrik` | The dew-smoke: swarms that mist-dance over the pools at wind-hour, combing water with mesh wings. Pollinator of the blade-flora; its cocoons are the **dewsilk** source (§11). Nickname: *dew-smoke*. |
| **ssurr** | reptile `ss-` | The fan-dancer. A crest-fan reptile whose breeding displays happen at the pools — the romance-and-ritual ruling (§4) made animal. Harmless, spectacular, beloved. Nickname: *fan-dancer*. |
| **vhakk** | apex `vh-` | The margin made flesh. It never hunts at water (§6's ban, by design, not restraint — it drinks in strict rotation like everything else) and owns the approaches instead; a low blade-crest along the spine. Its patrol is the oasis's outermost wall. Nickname: *the warden*. |

## 10b. Weather, and the sound of the place

Weather is the engine made visible. The base state is **clear and windy** — the
sea-wind always runs (§5). The signature weather is **fog at wind-hour**: when the
damp flow peaks, the high country goes into cloud at ground level, every comb in the
biome drinks at once, and the biome does its actual living — travel slows, the pools
rise, the mirrik swarms come out. Rain is rare and gentle when the fog oversaturates;
never storms, and **never snow** (§6 strips the donor's absurd SnowGentle/SnowHard).
Seep oases (§2b) add ground-steam instead of fog — their weather comes from below.

**Sound: an oasis is heard before it is seen.** Wind through the ancient vane arrays
makes aeolian tones — **each array is its own chord, so each oasis has a name in
sound before it has one in words**; pilgrims navigate the last miles by ear. Under
it: drip-echo in the cistern shafts, the fan-dancer's rattle, the crowd-noise of the
pools. A **dead oasis is silent** — the first thing a traveler notices, and the
worst. (Cheap to ship: ambient `soundsAmbient` per-biome plus the vanes' tones; the
donor's night-insects ambient is replaced by this.)

## 11. Unique items, furniture, structures

**Items.**

- **Dewsilk** — cloth woven from mirrik cocoon fiber; fiercely hydrophilic. The
  material of moisture cloaks and comb-sails; the biome's signature trade good.
- **Comb-vane segment** — salvage from the ancient condenser arrays;
  component-tier. Enough segments and a working shaft = a restored water economy (§7).
- **Bladder-fruit** — the water-hoarding blade-plant's harvest: food and drink in one
  object. Re-points the donor's `foragedFood` when the flora roster lands.
- **Seep-salt** — mineral crust from the seep oases (§2b); preservative and spice
  with the underworld's taste. Only source: the magical ones.
- **Oomo token** — the pilgrim's marker, left and taken at truce-stones; a social and
  ritual item, and the gate-token the Hutt palaces accept (§12).

**Furniture and structures — the recapture ladder (§8) made concrete.** Natural props:
weep-mats and drip-gardens on the cold faces; burrak wallows; the dead ring of bones.
Built, oldest to ultimate: **ancient vane array** (ruin, per-state: true-running /
leaking / fog-wild / dead) · **cistern shaft** (deep storage, ancient or re-cut) ·
**condenser fin** (buildable, wind-facing — the player's entry rung) · **shade-lid and
awning** (recapture) · **servo-vent segment** (the enclosure endgame) · **truce-stone**
(the pool's marker; ritual and recreation focus — where the tokens pile up) · between
oases, the **pilgrim ring**: cairns and camp hearths beading the caravan roads.
Map-gen placement rides `structure_injection_roster.md`; player buildables are their
own scoped item.

## 12. Faction expressions — one water, thirteen faces

Grounded in Global system 2 (`faction_roster_v2.md`, the water-and-thirst doctrine):
each faction's water *state* already decides its oasis face. The truce and claim law
(§4) grade them all: **settling the water is legal, charging for unsettled water is
the one barbarism.**

- **The Jawa** — pay-and-go, by doctrine and temperament. The crawler parks at the
  margin, unfurls its comb-sails, and market-day happens at the water's edge; nothing
  they raise claims the ground. They pay at settled oases and understand why. Rare
  settled exceptions exist and are notable *because* they are exceptions.
- **Hutt Cartel** — the enclosure endgame made gaudy. The **eight palaces**
  (`HUTT_LORDS_AND_POSTS_1`) are oasis-anchored seats: gilded vane arrays, perfumed
  pools, a servo-vented dome for a palace roof. Legal to the letter — the Hutt *lives*
  on the water — and worked as a racket: the gate has a price, the water inside is
  "free." A Hutt bathing in what others drink stays just inside the law, and every
  visitor feels exactly where the line is.
- **Deepwater Compact** — the stewards. Austere warden posts, ledgers of draw, the
  truce made institutional. The legitimate water-sellers: they live on every tile they
  charge for, which is the whole difference.
- **Wildsteam Clan** — the seep oases are theirs (§2b): boiler-works, bathhouses,
  steam-driven condensers on the hot mineral springs. Devastating at home, per
  doctrine — an attacked Wildsteam oasis is a kettle turned weapon.
- **Homestead Defense League** — vaporator farmers; they *manufacture* and don't need
  the pool. They come anyway — for market, marriage, and the rituals (§4's romance
  ruling); homesteads cluster near, never on. The neighborly face.
- **Deep Desert Tribes** — the taboo (Forbid): they never dwell, water in silence,
  and leave bone-and-vane chimes as offerings. The truce's zealots — the ones who
  execute toll-keepers. Their reverence is the fiercest and the least visible.
- **Geonosian Foundry Hive** — arid-adapted (Forbid): they don't stop. A Geonosian
  column marching past an oasis without drinking is the worst omen on any road — it
  means the one leash everything else wears isn't on them.
- **Free Droid Enclaves** — 🔴 **the legal sacrilege.** Their Deny state settles the
  water and *cracks it for fuel*: electrolysis stacks where vane arrays stood, lethal
  runoff pooling where the green ring is dying by inches, animals turned away from
  water that is technically claimed by the law and utterly damned by Oomo. Three
  enclaves — up to three dying oases on the map. The strongest quest seed this biome
  owns.
- **Galactic Empire** — supplied (Allow), needs nothing local — and meters the water
  anyway where it garrisons. Breaking the one law even enemies keep, *as policy*, is
  what makes the occupation legible at an oasis: the metering station near the
  spaceport is despised past politics.
- **Ascendant Helix** — buys its water in bulk and camps at a **dead ring**, trying
  to wake the silent machine. The only face more interested in the condenser than the
  pool; natural holder of the AncientUplink loadout's attention.
- **Blackstar Company** — water-clock hunters (Allow): oases are their rendezvous and
  their caches (the Stockpile loadout). Iron truce discipline — the kill happens on
  the road, never at the pool. A Blackstar team watering quietly means someone nearby
  is being hunted.

The landmark loadouts (architecture ruling, top) pair naturally with the faces:
AncientUplink draws the Helix; Stockpile is a Blackstar cache; AnimalHabitat sits
best near Compact stewardship; the dead rings belong to the Helix or the droids'
aftermath. Placement rides `OASIS_LANDMARK_PLACEMENT_1` when it files.

---

## Owed

- **The owner's pass** on §10–12 — none of it is ratified; the beasts, the dewback
  reassignment, the droid dying-oases and the Imperial metering are his to keep or
  cut.
- `OASIS_LANDMARK_PLACEMENT_1` (to file) — hand-place and hand-name the pools with
  per-site loadouts; seep-oasis siting waits on `VAPOR_EMITTER_PLACEMENT_1`.
- `OASIS_MUTATOR_PATCH_1` (to file) — whitelist `ZBiome_DesertOasis` into the vanilla
  Oasis mutator; strip snow weathers; re-point forage; alien-flora swap after the
  roster.
- `WEEPING_STONES_ROSTER_1` (to file) — flora and fauna to the sheet: reconcile the
  29 cast (§10), the dewback move from `LavaField`, the seven proposed natives, the
  blade-flora.
- **Engine feasibility pass** — the fog-at-wind-hour weather; the condenser fin as a
  buildable water source; the servo-vent enclosure; aeolian ambient per oasis state;
  the truce as animal behavior (or as flavor only — the cheap version is spawn
  suppression of predator-hunts near water, the honest version is a behavior mod).
- **Cross-flow ledger**: Cracked Lands fliers feed here and nest in the desert
  (ratified on that sheet); Desert/Badlands herds are the pilgrim ring; Wildsteam's
  seep claims tie to `the_seas.md` vent chemistry; Hutt palace interiors ride
  `HUTT_LORDS_AND_POSTS_1`.
- **Grammar backfill**: this enrichment step (bestiary · items/structures · faction
  faces · weather/sound) is owed to `README_BIOME_GRAMMAR.md` as standard fields, and
  **the Cracked Lands is owed the same pass** (owner, 2026-09-06: "I think we also
  skipped this step on the last biome").
