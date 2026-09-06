# The Desert — definition sheet

_Owner + BENCH, 2026-09-05, written in conversation. The livable one: the largest biome on
Ash'karr (`Desert`, 4,151 tiles, 19%) and the first on the dryness ladder with a real food
web. Thematic handle: **the long shade**._

🔑 **Read against `deep_desert.md`.** Deep desert is `ExtremeDesert`; this is `Desert`. They
share regions and grade into each other, so **the biome def is the boundary, not the region
name.** ⚠️ Only ~51% of the def's tiles currently fit this definition — see
`WORLDMAP_DESERT_BAND_REPAIR_1`.

## 0. The one measurement everything rests on

| | sun above horizon | shadow length | hilliness | temp |
|---|---|---|---|---|
| `ExtremeDesert` — deep desert | 47.4° | 0.9× height | 1.0 | 48.3 °C |
| **`Desert` — here** | **14.4°** | **3.9× height** | **2.0** | **24.5 °C** |

Sun elevation is `90 − arc`, and the core of this biome sits at **arc 60–88°**. **Four times
longer shadows, cast by twice as many objects, at half the temperature.**

## 1. What it is

The one place on the dayside with enough shade to survive *between* — but never enough to
survive *in*.

The sun sits a hand's width above the horizon and never moves, so every rock and scarp throws
a shadow four times its own height. But those shadows are **patches, not cover**: discrete
islands of survivable dark scattered across ground that will kill you, with lethal light in
between. Nothing lives in the open and nothing stays put. Life is **a sprint between
shelters**, and the distance from one patch to the next is the single number that decides
what can live where.

It is also the desert that can be *lived in*. Cooler, shaded, rocky, with enough vegetation
for meagre but **regular** populations — and the regularity is the gift. The Pyrelands boom
and burn; the deep desert holds almost nothing; here the numbers are small and steady, which
makes this the only ground on the planet a colony can live off.

## 2. Planetary position

**Outer dayside (arc 60–88°) × the anomaly of LOW SUN.** Not distance from water like the
deep desert, and not water itself like the river country. The anomaly is **geometry** — an
angle of illumination that turns ordinary terrain into scattered, permanent shelter.

## 3. Driving forces

**The sun is fixed and low, so shade is permanent, long, and PATCHY.** The shadows never
move, so neither do the islands or the gaps, and the gap distance decides everything.

**And the fertility is imported.** Ash and smoke wander in from Pyreland fires beyond the
horizon. This biome is fed by burning it never sees.

## 4. How the biology adapted

### The sprint economy

Rest in a shadow, run to the next, rest again.

- **Explosive acceleration and high burst speed, with almost no endurance.** Nothing here is
  a distance runner; the terrain asks for twenty seconds of everything you have, repeated for
  a lifetime.
- **Rest is thermal accounting, not fatigue.** An animal in shade is not catching its breath,
  it is **dumping the heat it took crossing**. Time in shelter is set by distance run.
- 🔑 **Body size maps directly to maximum dash distance.** Large animals hold heat longer and
  cross wider gaps; small ones are confined to close-packed country and can never leave it.
  **The landscape is sorted by size** — dense-patch hills hold small life, and only big
  animals can be on the open pavement at all. (Binds to
  `creature_normalization_doctrine.md`: mass becomes a statement about *which ground a
  creature may occupy*.)

### Predator and prey solve different problems

Not the same problem at different skill levels — **different problems**.

- 🔴 **The predator bursts out of shadow** at a speed nothing can evade, grabs, and **retreats
  to cool.** Its hunting radius is bounded by the trip **back**, not the trip out. That is an
  unusual constraint and it is the whole shape of the animal.
- 🔴 **The herbivore is a poor sprinter and a strong endurer.** It survives by reaching a
  shade patch **beyond the predator's return radius**. So prey does not flee — it
  **navigates**, and a herd that picks the wrong next patch dies as a unit.

### The shelter is the trap

Every patch is a required destination, so a predator need not hunt at all: **it can own a
shadow and wait for something to arrive overheated and out of options.** The alternative is
interception mid-dash, when the prey is committed and physically cannot turn back.

⇒ Both are positional. **Nothing in this biome pursues.** The chase does not exist as a
behaviour, because the terrain has already done the work.

⇒ Contrast, and state it that way: **in the deep desert a shadow is property**, held for
life. **Here a shadow is a staging post** — used by everything, owned by whatever is strong
enough to be sitting in it when you arrive.

### The patch is a commons, and it is stratified

There is no safety anywhere, so a patch holds predator and prey **at the same time**. This is
the biome's waterhole.

- 🔑 **The deep cool centre is held by whatever is strongest; everything else takes the rim,
  half-exposed.** The local hierarchy is legible at a glance from where things are standing —
  and the young are in the centre, which is what the hierarchy is protecting.
- 🔴 **The worst moment available here is arriving overheated at a shelter already full.**
  You cannot wait. Fight, take the rim, or push on to a patch you may not reach. This is a
  story engine, and it is exactly what a player caravan walks into.

### Nobody commits without asking

You cannot afford to cross and discover the far patch occupied, so **signalling is long-range
and happens before the run** — challenge and answer across open sightlines, at hundreds of
metres, deciding whether something crosses or turns back.

### Everything is lit from one side, forever

At 14° the light rakes in sideways and never rotates.

- **Countershading runs on the wrong axis** — dark on the sunward flank, pale on the shadow
  flank. Left-and-right, not back-and-belly. Every animal is asymmetric in a way that reads
  instantly wrong to a human eye and is exactly correct.
- **Plants grow one-faced**, all structure on a single side, permanently leaning.
- Anything hiding becomes **flat and oriented**, presenting an edge to the sun.

### A herd is a mobile shade structure

Tall and thin casts a great deal of shade for very little mass at this sun angle, so body
plans run **leggy** — animals carry their own shade. Standing close, **they stand in each
other's shadows**.

🔑 **This is why herds work here and are banned in the deep desert.** A herd is
infrastructure. Break it up and you have not scattered the animals, you have destroyed the
shade they were making.

### Activity is spatial, not temporal

Nothing is nocturnal, because there is no night. An animal is "night-active" **where it is
standing** — busy inside a patch, dormant fifty metres away in the light. The biome has no
daily rhythm; it has a **map** of activity.

### The soft ground and the hard ground are opposite bargains

Wind strips sand away in places, leaving **cracked pavement and hardpan**.

- **Soft sand:** burrowers can reach you, but it holds the shade-casting terrain — and **some
  sand burrowing is possible wherever sand exists.**
- 🔑 **Hard pavement: nothing can swim up at you.** But it is stripped flat, so **no shade
  either.**
- ⇒ **Safety and shelter are on opposite ground**, and every crossing is a choice between
  them. Produced by the physics, not designed on top of it.

### The smoke is a gift, and the ash changes the rules

Haze from Pyreland fires **dims the sun and lengthens the shade** — a smoke event is shade
for everybody at once, and the whole biome moves, feeds and breeds while it lasts. Settling
ash fertilises, giving a growth pulse.

Ash is also **grit**: it abrades, and it packs into the sand and hardens it, temporarily
**shutting down burrowing and flipping the tactical map**.

🔑 **The calendar of this biome is set by fires it cannot see.**

### Never a cold night

The sun is fixed, so — unlike every desert a player has ever known — **relief never arrives
on a schedule.** The heat does not break. It is only ever *somewhere else*.

### Dying in the open is the only privacy on this planet

Nothing can afford to walk out and retrieve a corpse, so a death mid-gap is simply **wasted**.
Scavengers here specialise exclusively in kills at a patch edge. Everywhere else on Ash'karr,
something eventually comes for you.

## 4b. The flora

### The buried canopy — the **ultracactus**

Broad, flat, **pale green**, and keeping **most of itself under the sand**, presenting its
surface flush with the ground to take the raking light. You would walk across a stand of them
and register nothing.

🔑 **It grows NEAR shade but does not require it** — and that is the point: it is
**outcompeted wherever the aggressive shade plants can reach.** So it holds the open ground
by tolerance rather than by strength, ringing every patch just beyond the reach of its
betters, and thinning out into the pavement.

⇒ **The open ground is therefore not empty. It is a roof over a living layer** — and that
layer is what the megafauna filter the sand for.

### The shade plants, which defend

Inside the patches, competition is fierce and physical.

- **Strange vines and thorny venom writhing around some areas** — plants that hold territory
  by injury. A patch that looks like the best shelter for a kilometre may be somebody's.
- **Mossy growth leaching nutrients as fast as it can** — fast, shallow, opportunistic, racing
  everything else to whatever the wind just delivered.

### 🔴 The seed that uses you — the cycle plant

_(Name owner's pick. Working: **staggerseed**.)_

An **edible-looking plant of the protected water pockets** whose fruit, eaten raw, **hatches
its seeds inside your belly**. It kills quickly, and the dying animal does what every dying
animal here does: **staggers toward the next shade** — and dies in it. The seeds germinate
there, in the one place they could not otherwise reach.

⇒ **It disperses by killing, and it aims at shade.** The jumping cholla's trick, run through a
corpse instead of a hitchhiking limb. This makes the plant an *active participant* in the
patch economy rather than scenery, and it means **a body in a shadow is how new patches get
colonised.**

⭐ **And the seeds are a delicacy.** Prepared correctly, the preparation lets them **begin to
grow and then perish before they can hurt you — producing euphoria.** A dish that is a
controlled near-miss with a lethal parasite. This is exactly the kind of exotic ingredient the
Star Wars cuisine track wants, and the margin for error is the flavour.

## 4c. The megafauna — harbours, vectors, and passengers

Whale-metaphor animals crossing between harbours of shadow.

- **They absorb enormous heat on the crossing and radiate it fiercely once shade is reached.**
  Thermal mass is the adaptation, and it lets them cross gaps nothing else can attempt.
- **They filter-feed through the sand**, straining the buried canopy and the small life
  grazing it. Anything that slow needs food that cannot run.
- 🔑 **A megafauna IS a mobile shade patch — the only one that exists.** So things travel
  *with* it: **tiny glittering bird-like creatures that live their entire lives in one
  animal's shadow**, never touching open ground. The herd-as-shade-structure idea at its
  limit.
- 🔑 **They leave massive dung at shade patches, and that dung immediately seeds young plants
  and young creatures around it.** So the megafauna are the biome's **circulatory system** —
  the only long-distance vector, carrying seeds, riders and parasites between patch-networks
  that are otherwise sealed from each other, and **fertilising every harbour they stop at.**
- 🔴 **Killing one strands its passengers** in the open, and starves the patch it was due to
  fertilise next.

## 5. Always true

- Shade is long, permanent and **patchy** — islands, never cover — and the gaps never move.
- Life is a sprint economy: rest, dash, rest. **Nothing pursues.**
- Dash range is a function of size, and it decides where a creature may live.
- A patch holds predator and prey together, stratified centre-to-rim.
- Populations are small and **steady** — never boom-and-bust.
- Fertility arrives as ash from fires beyond the horizon, and as dung from passing giants.
- **The heat never breaks.**

## 6. Never true — 🔴 HARD BANS (linter-checkable)

1. 🔴 **No day/night cycle, and no content depending on one.** Nothing nocturnal,
   crepuscular, or dawn/dusk-triggered. A def keyed to time-of-day behaviour is a violation;
   the analogous behaviour keys to **shade** instead.
2. 🔴 **No rain** (planet-wide, R-H1 — the peaks and the river margin are the only
   exceptions, and this is neither).
3. 🔴 **No pursuit predators.** Chasing does not exist here. A predator that runs prey down
   over distance is a violation.
4. 🔴 **No boom-and-bust populations.** Explosive growth belongs to the Pyrelands; steadiness
   is this biome's identity.
5. 🔴 **No local fire ecology.** Ash and smoke ARRIVE; they do not originate. A burn scar
   generated on these tiles is a violation.
6. 🔴 **No burrow-ambush on pavement/hardpan.** That ground is defined by its absence.
7. 🔴 **No unsheltered nests or safe young.** There is no safety anywhere; the deep centre of
   an occupied patch is the closest thing that exists.
8. 🔴 **No lush**, under all three parts of the lush rule — vegetation is meagre and never
   green in quantity. *(The ultracactus is pale green and mostly buried; that is the ceiling.)*
9. 🔴 **The recognizability rule applies.** Familiar body *architecture* is wanted here —
   four limbs, real eyes, hide — but a nameable terrestrial animal is not. The Star Wars icon
   carve-out still protects icons.

## 7. Uniquely available

- 🔑 **Reliable game.** The only ground on Ash'karr with a food web steady enough to hunt as a
  livelihood rather than a windfall.
- **Herd beasts** — the pack and draught animals the campaign runs on.
- ⭐ **The prepared cycle-seed** — a euphoric delicacy that is a controlled near-miss with a
  lethal parasite.
- **Ultracactus** — harvestable from open ground nothing else uses.
- **Ash-pulse harvests** after a smoke event; **dung-seeded growth** after a megafauna passes.
- **Known viable routes** — the chains of patches close enough to cross, as fixed for a
  caravan as for an animal, and worth mapping.
- **Desert pavement stone**, wind-stripped and flat.
- **Crevice shelter** — buildable ground with cover already present.

## 8. Inhabited objects

- **Settlements on the big patches.** A shadow large enough to hold more than one thing is
  the only place worth building, and roads run along the chains of them.
- 🔑 **The wide gaps are named places.** A stretch too broad for most things to cross is a
  landmark, a border, a toll point, an ambush and a story — this biome's equivalent of a
  river. Author them, name them, reuse them. **The last patch before a wide gap is the most
  contested real estate in the biome**, because everything must stage there.
- 🔑 **Shade patches are nutrient sinks, and therefore middens.** The wind never reverses, so
  sand and blown matter pile on the lee of every rock — which is also the shaded side.
  **Everything that blows across this desert ends up in a shadow**: nutrients, and also
  **bones, debris and wreckage.** The shadows are the planet's collection points, and
  archaeology accumulates in them. For a Jawa, the shade is the dig site.
- **The dew line.** Temperature drops sharply at the shadow boundary, so **dew forms at the
  shade line** — a thin band of moisture with the densest growth on it. Every patch wears a
  faint living halo, and **the most valuable ground in the biome is a rim, not an area.**
- **Rock shelters and crevice dwellings** in the hills.
- **Deep Desert Tribe holdings** — canyons, caves, isolated ridges, never near water, and
  **no roads** (canon, `ASHKARR_WORLD_DEFINITION.md` §7).
- **Herder camps** working the patch chains — "seasonally" meaning *by smoke*, not by calendar.

### 🔴 The player consequence the biome's gameplay is built on

**Building a roof is the most powerful act available here.** You are manufacturing the scarce
resource, and the moment you do, your base is the largest shade patch for miles.

⇒ **Every living thing in the region wants to be in it.** Your walls are not keeping out
raiders — they are keeping out an ecosystem that has correctly identified you as the best
harbour on the route. Including, eventually, something whale-sized that has walked this line
for a very long time and does not know you have moved in.

## 9. Artistic theme

**"Permanent golden hour, and everything is waiting at the edge of a shadow."**

- **Light:** the defining quality, and the exact opposite of the deep desert's flat vertical
  glare. It **rakes in sideways and never changes** — long, warm, low, every surface half-lit
  and half-dark. This is the most straightforwardly beautiful ground on the planet: a sunset
  that has been going on for a million years.
- **Palette:** hot low sun on lit faces — amber, ochre, rust — against **long cool blue
  shadows**. That warm/cool split across every object is the signature, and it is worth real
  care, because it is what will read the moment the fixed sun renders true shade. The only
  greens are the **pale ultracactus** flush with the ground and the **dew-line halo**.
- **Silhouette language:** verticals matter — standing rocks, scarps, leggy animals — because
  every vertical is a shade-maker and therefore a landmark. Ground alternates visibly between
  **soft sand sheets** and **cracked hardpan pavement**.
- **Weather:** smoke haze arriving from over the horizon, flattening distance to orange. It
  should read as **relief**, not threat.
- **Motion:** stillness, then a sudden committed sprint across the light, then stillness. The
  biome's signature image is **an animal at the edge of a shadow, deciding.**

## 10. Implementation — what the engine will and won't do

Full research: `design/Jawa/worldbuilding/desert_ecology_feasibility.md` (verified against
decompiled source, 2026-09-05).

🔴 **Two engine facts are load-bearing and both say no:**
- **Outdoor light does not vary spatially.** `GlowGrid.GroundGlowAt` returns
  `SkyManager.CurSkyGlow` — one float per map — for every unroofed cell. Walls and trees cast
  no shadow. The only per-cell term outdoors is the binary `RoofGrid.Roofed(c)`.
- **Outdoor temperature does not vary spatially.** `GenTemperature` resolves to
  `cell.GetRoom(map).Temperature`, and an open desert is one giant Room on one `OutdoorTemp`.

⇒ 🔑 **The shade grid is the keystone and we must build it.** One `MapComponent` computing
`ShadeAt(IntVec3)`; shade-seeking AI, the burst hediff, crossing heat load and megafauna
thermal mass all read from that one grid.

| behaviour | route |
|---|---|
| creatures prefer shade | small C# — vanilla ships the pattern in `JobGiver_WanderInRoofedCellsInPen`; insert with `insertTag = Animal_PreWander`, no Harmony |
| burst then recover | **nearly native** — staged `statFactors` with negative `severityPerDay`, exactly Anomaly's `GhoulFrenzy`; one C# line to fire it on the attack job |
| herbivore endurance | **native** — same machinery, different numbers |
| megafauna heat | C#, modelled **on the pawn**, driven by `ShadeAt`, not by map temperature |
| filter-feeding sand | C# — `FoodTypeFlags` is a closed enum with no terrain member |
| sand burrowing | **already solved** — Alpha Animals' Sand Prowler fakes it in pure XML via VEF's `CompProperties_GraphicByTerrain` |

⚠️ **Rendered shadow and mechanical shade are two different systems and will not agree unless
we make them.** If a pawn stands in a hard black rendered shadow and nothing happens, the
biome reads as arbitrary. `ShadeAt` must derive from the same geometry the renderer uses —
cheap to decide now, expensive to retrofit.

---

## Owed

- Names, owner's pick: the cycle plant (**staggerseed**?), the prepared seed dish, and the
  glitter-birds. **Ultracactus is the owner's own and stands.**
- ⚠️ **`WORLDMAP_DESERT_BAND_REPAIR_1`** — only ~51% of the `Desert` def sits in arc 60–88.
  19.5% is at arc <60 and 41 °C (deep desert mislabelled); 29.6% is at arc >88 where the sun
  is at or below the horizon.
- The **wide gaps** want authoring as named world features, and patch-chain connectivity wants
  to be something the map generator lays down rather than an accident of scatter — alongside
  the deep desert's wind grain.
- ⚠️ An earlier draft modelled the shade as a *connected network* travelled within. That was
  wrong (owner, 2026-09-05) and is superseded by the patch-and-dash model above.
