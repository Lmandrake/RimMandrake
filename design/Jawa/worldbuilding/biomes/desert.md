# The Desert — definition sheet

_Owner + BENCH, 2026-09-05, in conversation. The livable one: the largest biome on Ash'karr
(`Desert`, 4,151 tiles, 19%) and the first on the dryness ladder with a real food web._

🔑 **The pair to read this against is `deep_desert.md`.** Deep desert is `ExtremeDesert`;
this is `Desert`. They share regions and grade into each other — Kiln and Glare hold both —
so **the biome def is the boundary, not the region name.**

## 0. The one measurement everything rests on

| | sun above horizon | shadow length | hilliness | temp |
|---|---|---|---|---|
| `ExtremeDesert` — deep desert | 47.4° | 0.9× height | 1.0 | 48.3 °C |
| **`Desert` — here** | **14.4°** | **3.9× height** | **2.0** | **24.5 °C** |

Sun elevation is `90 − arc`, and this biome sits at **arc 68–82°**, so the sun hangs a hand's
width above the horizon and never moves. **Four times longer shadows, cast by twice as many
objects, at half the temperature.**

⚠️ The def also has outliers at both ends — Kiln and Glare tiles at arc 53 (sun 37°, 41 °C)
and Sinkground/Sunreach tiles at arc 94–105, where **the sun is below the horizon entirely**.
The low-sun reasoning below defines the core; the outliers are flagged in §Owed.

## 1. What it is

The one place on the dayside where the land makes its own night.

The sun sits so low that every ridge, boulder and scarp throws a shadow four times its own
height, and those shadows are long enough to **touch each other**. What that produces is not
patches of shade but a **network** — ribbons of permanent dark running across the country,
joining up, branching, and going somewhere. An animal here does not hide in a shadow. It
**travels** in one.

So this is the desert that can be lived in. Cooler, shaded, rocky, with enough vegetation to
carry meagre but *regular* populations — and regularity is the whole gift. The Pyrelands boom
and burn; the deep desert holds almost nothing; here the numbers are small and **steady**,
which makes it the only ground on the planet a colony can actually live off.

## 2. Planetary position

**Outer dayside (arc 68–82°) × the anomaly of LOW SUN.** Not distance from water like the
deep desert, and not water itself like the river country. The anomaly is **geometry**: an
angle of illumination that turns ordinary terrain into continuous shelter.

## 3. Driving forces

**The sun is fixed and low, so shadow is permanent, long, and connected.** Everything
follows: where life can be, where it can go, when it is safe, and where it dies.

Second engine, and it comes from somewhere else entirely: **the fertility here is imported.**
Ash and smoke wander in from Pyreland fires beyond the horizon. This biome is fed by burning
it never sees.

## 4. How the biology adapted

### Night is a network, and the danger is the gaps

Because the sun never moves, **the ribbons never move either** — and neither do the places
where two ribbons fail to meet. There are permanent, known **crossings**: stretches of open
light that everything must sprint across.

- 🔑 **Prey use the same ribbons for generations, so the ribbons are trails.** Predators do
  not hunt in the dark; they **wait at the crossings**. The entire predator strategy of this
  biome is ambush at a fixed, well-known place.
- This is the biome's signature tactical fact and it applies to the player identically: a
  caravan moving in shade is safe and fast, and every raider on the planet knows exactly
  where it must come into the light.
- ⇒ Contrast with the deep desert, and state it that way: **there a shadow is property**, held
  for life and fought over. **Here a shadow is a road.** Territorial versus migratory, out of
  the same fact about the sun.

### Everything is lit from one side, forever

At 14° elevation the light rakes in sideways and never rotates. So:

- **Countershading runs on the wrong axis** — dark on the sunward flank, pale on the shadow
  flank. Left-and-right, not back-and-belly. Every animal here is asymmetric in a way that
  reads instantly wrong to a human eye and is exactly correct.
- **Plants grow one-faced**, all structure on a single side, permanently leaning.
- Anything that wants to disappear becomes **flat and oriented**, presenting an edge to the
  sun and no shadow of its own.

### A herd is a mobile shade structure

Tall and thin casts a great deal of shade for very little mass when the sun is this low, so
body plans run **leggy** — the animals carry their own shade with them. And standing close
together, **they stand in each other's shadows**.

🔑 **This is why herds work here and are banned in the deep desert.** A herd is not just
safety in numbers, it is *infrastructure*. Break it up and you have not merely scattered the
animals, you have destroyed the shade they were making.

### Activity is spatial, not temporal

Nothing here is nocturnal, because there is no night to be nocturnal in. Instead an animal is
"night-active" **where it is standing** — busy inside the ribbon, dormant fifty metres away in
the light. The biome has no daily rhythm at all; it has a **map** of activity.

### The soft ground and the hard ground are opposite bargains

Wind strips the sand away in places and leaves **cracked pavement and hardpan plains**.

- **Soft sand:** burrowers can reach you, but it holds the shade-casting terrain.
- 🔑 **Hard pavement: nothing can swim up at you** — the deep desert's sand-swimming ambush
  simply does not work on stone. But pavement is stripped flat, so it has **no shade either**.
- ⇒ **Safety and shelter are on opposite ground**, and every crossing of this biome is a
  choice between the two. That dilemma is produced entirely by the physics, not designed on
  top of it.

Cracked plains also hold water briefly after a rare flood, and bloom.

### The smoke is a gift

Ash and haze drifting in from Pyreland fires **dim the sun and lengthen the shade** — a smoke
event is shade for everybody at once, and the whole biome moves, feeds and breeds while it
lasts. The ash that settles fertilises, giving a growth pulse.

🔑 **The calendar of this biome is set by fires it cannot see.** Its fertility and its
breeding season both arrive on the wind from somewhere else.

### Life closer to what we know

This is where recognisable *architecture* returns — four limbs, real eyes, hide and coat — on
animals that are still not anything a player can name. Familiar engineering, alien detail.
It is the workaday biome: the game a colony hunts, and the beasts a Jawa clan actually herds.

## 5. Always true

- The sun is low, fixed, and lights everything from one side.
- Shadows are long, connected, and permanent — and so are the gaps between them.
- Predators wait at crossings; they do not pursue through open light.
- Activity is a matter of *where*, never *when*.
- Populations are small and **steady** — never boom-and-bust.
- The fertility arrives as ash from fires beyond the horizon.

## 6. Never true — 🔴 HARD BANS (linter-checkable)

1. 🔴 **No day/night cycle, and no content that depends on one.** Nothing is nocturnal,
   crepuscular, or dawn/dusk-triggered. A def keyed to time-of-day behaviour is a violation;
   the analogous behaviour must be keyed to shade instead.
2. 🔴 **No rain.** Planet-wide rule (R-H1) — the peaks and the river margin are the only
   exceptions, and this is neither.
3. 🔴 **No sand-swimming or burrow-ambush on pavement/hardpan.** That is the deep desert's
   mechanic and the hard ground is defined by its absence.
4. 🔴 **No boom-and-bust populations.** Explosive growth belongs to the Pyrelands. Steadiness
   is this biome's entire identity.
5. 🔴 **No local fire ecology.** Ash and smoke ARRIVE here; they do not originate here. A
   burn scar generated on these tiles is a violation.
6. 🔴 **No lush**, under all three parts of the lush rule — vegetation is meagre and never
   green in quantity.
7. 🔴 **The recognizability rule applies.** Familiar body architecture is permitted and
   wanted; a nameable terrestrial animal is not. The Star Wars icon carve-out still protects
   icons.

## 7. Uniquely available

- 🔑 **Reliable game.** The only ground on Ash'karr with a food web steady enough to hunt as
  a livelihood rather than a windfall.
- **Herd beasts** — the pack and draught animals the campaign runs on.
- **The shade ribbons as travel infrastructure** — routes that are faster and safer than open
  ground, for the player exactly as for the animals.
- **Ash-pulse harvests** after a smoke event.
- **Desert pavement stone**, wind-stripped and flat.
- **Crevice shelter** — buildable ground with cover already present, which almost nowhere
  else on the dayside offers.

## 8. Inhabited objects

- **Settlements at ribbon junctions.** Where several shadow corridors meet is a natural
  crossroads, and it is where anything sane builds. Roads follow the ribbons because
  everything always has.
- 🔑 **The crossings are named places.** A stretch of open light every caravan must run is a
  landmark, a toll point, an ambush, and a story. These should be authored, named, and
  reused — they are this biome's equivalent of a bridge.
- **Rock shelters and crevice dwellings** in the hills.
- **Deep Desert Tribe holdings** — canyons, caves and isolated ridges, never near water, and
  **no roads** (canon, `ASHKARR_WORLD_DEFINITION.md` §7). Their fire doctrine is set out in
  `deep_desert.md`.
- **Herder camps** following the ribbons seasonally — where "seasonally" means *by smoke*,
  not by calendar.
- **Ash middens** — drifted accumulations at the downwind foot of ridges, worth digging.

## 9. Artistic theme

**"Permanent golden hour, and the shadows go somewhere."**

- **Light:** the defining quality, and the exact opposite of the deep desert's flat vertical
  glare. Here it **rakes in sideways and never changes** — long, warm, low, with every
  surface half-lit and half-dark. This is the most straightforwardly *beautiful* ground on
  the planet, and it looks like a sunset that has been going on for a million years.
- **Palette:** hot low sun on the lit faces — amber, ochre, rust — against **long cool blue
  shadows**. That warm/cool split across every single object is the biome's signature, and it
  is worth a lot of care, because it is what will read on screen the moment the fixed sun is
  rendering real shade.
- **Silhouette language:** verticals that matter — standing rocks, scarps, leggy animals —
  because every vertical is a shade-maker and therefore a landmark. The ground alternates
  between **soft sand sheets** and **cracked hardpan pavement**, in patches, visibly.
- **Weather:** the smoke haze, arriving from over the horizon, turning everything orange and
  flattening the distance. It should read as **relief**, not as threat.
- **Motion:** herds moving along the ribbons, and the pause before something breaks cover at
  a crossing.

---

## Owed

- ⚠️ **The `Desert` def's outliers.** Tiles at arc 53 (Kiln/Glare, sun 37°, 41 °C) are too
  hot and too high-sun for this reasoning; tiles at arc 94–105 (Sinkground, Sunreach) have
  **the sun below the horizon** and sit at 6 °C and −1.9 °C. Neither end fits the sheet. Owner
  call: retune the placement, or accept that the def spans more than this definition covers.
- The **crossings** want authoring as named world features.
- A name. "The Desert" is what the engine calls it; the thematic handle running through this
  sheet is **the long shade**.
