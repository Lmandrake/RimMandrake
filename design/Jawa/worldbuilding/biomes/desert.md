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

The one place on the dayside where there is enough shade to survive between — but never
enough to survive *in*.

The sun sits so low that every ridge, boulder and scarp throws a shadow four times its own
height. But those shadows are **patches, not cover**: discrete islands of survivable dark
scattered across ground that will kill you, with hard lethal light in between. Nothing here
lives in the open and nothing here stays put. Life is **a sprint between shelters**, and the
distance from one patch to the next is the single number that decides what can live where.

So this is the desert that can be lived in. Cooler, shaded, rocky, with enough vegetation to
carry meagre but *regular* populations — and regularity is the whole gift. The Pyrelands boom
and burn; the deep desert holds almost nothing; here the numbers are small and **steady**,
which makes it the only ground on the planet a colony can actually live off.

## 2. Planetary position

**Outer dayside (arc 68–82°) × the anomaly of LOW SUN.** Not distance from water like the
deep desert, and not water itself like the river country. The anomaly is **geometry**: an
angle of illumination that turns ordinary terrain into continuous shelter.

## 3. Driving forces

**The sun is fixed and low, so shade is permanent, long, and PATCHY.** The shadows never
move, so neither do the islands or the gaps — and the gap distance decides everything: what
can live here, how big it must be, where it can go, and where it dies.

Second engine, and it comes from somewhere else entirely: **the fertility here is imported.**
Ash and smoke wander in from Pyreland fires beyond the horizon. This biome is fed by burning
it never sees.

## 4. How the biology adapted

### The sprint economy

Shade is discrete, so the fundamental act of life here is **the dash** — rest in a shadow,
run to the next one, rest again. Everything is built for it:

- **Explosive acceleration and high burst speed, with almost no endurance.** Nothing here is
  a distance runner, because distance running is not what the terrain asks for. It asks for
  twenty seconds of everything you have, repeated for a lifetime.
- **Rest is thermal accounting, not fatigue.** An animal in shade is not recovering its
  breath, it is **dumping the heat it took crossing**. Time in shelter is set by how much
  heat it picked up, which is set by how far it ran.
- 🔑 **Body size maps directly to maximum dash distance.** Large animals hold heat longer and
  can cross wider gaps; small ones are confined to close-packed country and can never leave
  it. **The landscape is therefore sorted by size** — the rocky, dense-patch hills hold small
  life, and only big animals can be out on the open pavement at all. (Binds to
  `creature_normalization_doctrine.md`: mass becomes a readable statement about *which ground
  a creature is allowed to occupy*.)

### The shelter is the trap

Because every patch is a required destination, a predator does not need to hunt. **It can own
a shadow and wait for something to arrive needing it**, overheated and out of options. The
alternative strategy is to **intercept mid-dash**, when the prey is committed, in the open,
and physically cannot turn back.

⇒ Both strategies are ambush, and both are positional. **Nothing in this biome pursues.**
The chase does not exist here as a behaviour, because the terrain has already done the work.

⇒ And state the contrast with the deep desert plainly: **there a shadow is property**, held
for life. **Here a shadow is a staging post** — used by everything, owned by whatever is
strong enough to be sitting in it when you arrive.

### Connectivity is geography

Since neither the patches nor the gaps ever move, the country has a permanent, knowable
**map of what is reachable from what**. Some routes across it are viable and some are simply
not, and that is a fixed fact rather than a seasonal one. Animals inherit routes. So do
caravans. **A stretch where the patches thin out is a wall**, and it does not matter that you
can see straight across it.

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
- Shade is long, permanent and **patchy** — islands, never cover — and the gaps never move.
- Life is a sprint economy: rest, dash, rest. **Nothing pursues.**
- How far a creature can dash is a function of its size, and it decides where it may live.
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
- **Known viable routes** — the chains of shade patches close enough to be crossed, which are
  as fixed for a caravan as for an animal, and worth mapping.
- **Ash-pulse harvests** after a smoke event.
- **Desert pavement stone**, wind-stripped and flat.
- **Crevice shelter** — buildable ground with cover already present, which almost nowhere
  else on the dayside offers.

## 8. Inhabited objects

- **Settlements on the big patches.** A shadow large enough to hold more than one thing is
  the only place worth building, and roads run along the chains of them because nothing can
  travel any other way.
- 🔑 **The wide gaps are named places.** A stretch too broad for most things to cross is a
  landmark, a border, a toll point, an ambush and a story — this biome's equivalent of a
  river. Author them, name them, reuse them. **The last patch before a wide gap is the most
  contested real estate in the biome**, because everything must stage there.
- **Rock shelters and crevice dwellings** in the hills.
- **Deep Desert Tribe holdings** — canyons, caves and isolated ridges, never near water, and
  **no roads** (canon, `ASHKARR_WORLD_DEFINITION.md` §7). Their fire doctrine is set out in
  `deep_desert.md`.
- **Herder camps** working the patch chains seasonally — where "seasonally" means *by smoke*,
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
- **Motion:** stillness, then a sudden committed sprint across the light, then stillness
  again. The biome's signature image is **an animal at the edge of a shadow, deciding**.

---

## Owed

- ⚠️ **The `Desert` def's outliers.** Tiles at arc 53 (Kiln/Glare, sun 37°, 41 °C) are too
  hot and too high-sun for this reasoning; tiles at arc 94–105 (Sinkground, Sunreach) have
  **the sun below the horizon** and sit at 6 °C and −1.9 °C. Neither end fits the sheet. Owner
  call: retune the placement, or accept that the def spans more than this definition covers.
- The **wide gaps** want authoring as named world features, and the patch-chain connectivity
  wants to be a real thing the map generator lays down rather than an accident of scatter.
- A name. "The Desert" is what the engine calls it; the thematic handle running through this
  sheet is **the long shade**.
- ⚠️ An earlier draft of this sheet modelled the shade as a *connected network* travelled
  within. That was wrong (owner, 2026-09-05) and is superseded by the patch-and-dash model
  above: the shade is discrete and the gaps are lethal.
