# The Nightside Ice — biome definition sheet

_First pass, 2026-09-05, to the grammar in `README_BIOME_GRAMMAR.md`._

> 🔑 **2026-09-06:** this sheet's def now RECEIVES the deep-night highland — the dissolved
> ring's sectors 1–3 and the former crystal caverns' high tiles (`the_lantern_deeps.md`
> §0, `HORRORWASTES_BIOME_DISSOLVE_1`) — as plateau lobes. Its distillation-column idea
> has since been made literal by the phase-line sheets (`the_blue_desert.md`,
> `the_propane_lakes.md`). **A second pass is owed** before the freeze review.

**The problem this sheet had to solve:** the deep nightside has no light and — since
cold gas venting is the poison forest's anomaly and may not be reused — no chemistry
coming up out of the ground either. Two of the three ways a biosphere is normally
powered are off the table. The way through is that the antistellar point is not
merely cold; it is the **drain of the planet's entire atmosphere**. Everything the
dayside evaporates, everything volcanism emits, everything anybody has ever burned,
travels aloft to the nightside, sinks, and freezes out **in order of its freezing
point**. The nightside is not a wasteland. It is a **fractional distillation column
the size of a hemisphere**, and it is the only place on Ash'karr where the energy
source is *delivered from somewhere else*.

## 1. What it is

Ice as hard as quartzite, black under a sky full of stars, absolutely still.

There is no wind — this is the bottom of the global circulation, where air arrives
and stops — and there is no snow underfoot, because at −80 °C water ice does not
behave like snow, it behaves like rock. The ground rings when you strike it and
fractures in slabs. It is not white. Deep ice over dark rock reads **blue-black**,
and the only white on the nightside is in the basins.

The basins are the point of the place. Every low spot is a **pan of frost that is not
water** — ammonia in one, carbon dioxide in the next, hydrocarbon slush in the
deepest and coldest — each one a different colour, each one sharply bounded, each one
a chemical warehouse with a floor and a rim. The Umbra Trap holds ammonia. The
propane lakes lie lower still, and they are liquid, and they are surrounded by
breathable oxygen, and **you are the only source of ignition on the hemisphere**.

Nothing moves. Not "nothing moved while you watched" — **nothing here moves on a
human timescale at all.** The hills have metabolisms. What you take for a boulder
field has been slowly eating the frost beneath it since before your species had
writing, and one of those boulders has been saving up, for two hundred years, to move
exactly once.

## 2. Planetary position

**Deep nightside (θ ≈ 140-180°), −58 °C at θ 150 falling to −80 °C at the
antistellar point.** `AB_RockyCrags` is the dominant terrain (canon: 2,828 of 3,916
tiles past θ 130), with `AB_PropaneLakes` in the basins and `BMT_CrystalCaverns` in
the highlands below −55 °C.

- **Energy regime:** none. No light, and — 🔴 explicitly — **no vents, no geothermal,
  no volcanism**. The only energy arriving is what the atmosphere carries in.
- **Temperature:** the coldest on the planet, and it is the *active* axis here. It
  does not merely slow chemistry down; it **removes species from the gas phase one by
  one**, which is the whole mechanism.
- **Anomaly:** ⭐ **the cold trap** — the antistellar point as the planet's
  condensation sink, sorting the atmosphere by freezing point into topographic pans.

### Why this is not a ring, and cannot be moved 🔴
Descending air spreads and deposits, but it does not deposit *evenly*: the volatiles
migrate downslope as frost and pool in **whatever the local topography holds**. So
the chemistry of a given place is set by **the depth and temperature of its basin**,
not by its arc from the antistellar point. Two pans at the same θ, one shallow and
one deep, hold entirely different inventories.

⇒ **The nightside is a scatter of chemically distinct pans separated by inert ice
uplands.** No band, no halo, no gradient you could draw with a compass — a
patchwork whose pattern is the *terrain map*, which is torn and irregular already.

⇒ And it exists only here. A cold trap needs a permanent atmospheric sink with a
temperature below the freezing points of the species being trapped. There is exactly
one on Ash'karr, and it is a point, not a band. Move this biome fifty degrees
dayward and the ammonia sublimes, the pans empty, and there is nothing left.

⚠️ **Not the Glowforest.** Canon places `Glowforest` as isolated points on the deep
night. Those are a *different anomaly* and get their own sheet: 🔴 bioluminescence is
banned in this biome (§6) on energetic grounds, and the Glowforest points are an
exception that must justify its own power source, not a licence to light this one up.

## 3. Driving forces

**A hemisphere-sized cold trap with no light, no wind and no heat from below, where
the only energy available is the chemical disequilibrium of an atmosphere that has
been frozen out in the wrong order.** Everything below follows.

## 4. How the biology adapted

**Life here does not grow. It catalyses, and it waits.**

- **The energy source is un-mixing.** The distillation stacks incompatible things in
  contact: reduced volatiles from the dayside and from volcanism land on top of, or
  underneath, oxidised frosts that came down at a different temperature. Those layers
  **should** react and release energy. At −80 °C they cannot — the activation barrier
  is insurmountable. ⇒ 🔑 **A nightside organism is a catalyst.** It sits on a
  chemical interface it did not create and lowers the barrier, taking a share of a
  reaction that the cold would otherwise forbid forever. It does not hunt, it does
  not photosynthesise, it does not mine. **It lives on a seam.**
- **Therefore everything is sessile, laminar, and enormous.** A catalyst wants
  maximum contact with an interface, so bodies are **sheets, crusts and plates
  pressed into a boundary layer** — and since the power density is absurdly low, the
  only way to accumulate a usable total is **area and time**. Nightside organisms are
  measured in hectares and centuries. ⇒ ⭐ **The largest living things on Ash'karr
  are here, and none of them looks alive.** A ridge is an organism. A boulder field
  is one organism. The owner's "truly huge creatures everywhere" is most defensible
  right here, because size is not a display or a defence — it is the *only* way to
  make the arithmetic work.
- ⭐ **The one-move animal.** Motion is the most expensive thing a body can do, and
  here it cannot be paid for out of income — only out of savings. So the nightside's
  only mobile life spends a century or more accumulating, and then **moves exactly
  once**: to reach a fresh seam, to reproduce, or to kill. It cannot do it twice.
  ⇒ Gameplay: it is indistinguishable from terrain until it commits, it commits
  suddenly and totally, and afterwards it is **inert forever** — a corpse that is
  still technically alive and will never move again. There is no fleeing from it and
  no fighting it twice.
- 🔴 **Sensing is thermal, and the player is the loudest thing on the hemisphere.**
  There is no light to see by, no wind to smell on, nothing that makes a sound on
  purpose, and — 🔴 pointedly — **no ground-hum to feel**, because that is the poison
  forest's vents and there are none here. The only gradient in the entire environment
  is **temperature**, and against a −80 °C background a heated wall, an engine, a
  campfire or a living human body is a beacon visible for kilometres in the far
  infrared. ⇒ Every nightside organism senses heat and only heat. ⇒ **Gameplay: your
  heating is your threat generator.** Insulate, run cold, and nothing comes. Heat the
  base to a comfortable temperature and you have lit a flare on a dark plain. That is
  a real strategic tension and it is not available anywhere else in the game.
- **Reproduction is by fragment and by contact, never by dispersal.** There is no
  wind to carry a spore, no water to float one, and no animal to move one. A new
  individual is a piece of an old one that reached a new seam — which is precisely
  what the one-move animal is *for*. ⇒ Populations are **clonal, ancient, and
  strictly local**: a pan's inhabitants are all one lineage and have been for a
  geological age.
- **Nothing here is warm-blooded and nothing here is fast.** A metabolism that could
  hold a body above ambient at −80 °C would need an energy budget hundreds of times
  what a seam provides. Anything warm on the nightside is a **visitor, a machine, or
  dying**.

## 5. Always true

- **It is dark.** Starlight only. Nothing is lit and nothing casts a shadow you
  could see without instruments.
- **It is still.** No wind, ever — this is the sink of the circulation.
- **The ground is hard.** Ice at −80 °C is a brittle rock; it fractures, it does not
  compress, and there is no snowpack to walk through.
- **Chemistry is sorted by basin.** What a pan holds is a function of its depth and
  temperature, and its boundary is sharp.
- **Everything alive is old, huge, stationary and unrecognisable as life.**
- **Anything left here is preserved perfectly and indefinitely** — bodies, machines,
  records, and mistakes.
- ⚠️ **Fire is possible and catastrophic.** Liquid hydrocarbon under an oxygen
  atmosphere is a fuel-air weapon waiting for the one thing the environment cannot
  supply. You are that thing.

## 6. Never true 🔴 (hard bans — checkable)

- ⛔ **No vents, no geysers, no geothermal, no volcanism, no hot springs, no
  fumaroles.** The nightside has no energy from below. (The cold vents belong to the
  poison forest and may not be reused here.)
- ⛔ **No bioluminescence, no glowing organisms, no light-producing flora or fauna.**
  A seam metabolism cannot afford photons. Any glow on the nightside is a machine, a
  fire, or `Glowforest`, which is a different biome with a different anomaly.
- ⛔ **No photosynthesis and no photosynthetic tissue of any kind.**
- ⛔ **No liquid water anywhere, in any form, ever.** The liquids here are
  hydrocarbons and the frosts are not water-dominated.
- ⛔ **No soft snow, snowdrifts, blizzards, snowfall or falling weather** on the
  uplands. Deposition happens in the pans and it is chemical frost, not weather.
- ⛔ **No wind, no storms, no dust.**
- ⛔ **No warm-blooded, fast, pursuing, fleeing or flocking fauna.** No pack hunters,
  no herds, no migration. Any creature def here with a normal move speed is a
  violation.
- ⛔ **No vision-based or sound-based sensing, and no vibration/ground-sense** (that
  is the poison forest's channel). **Thermal only.**
- ⛔ **No spores, seeds, pollen or airborne dispersal.**
- ⛔ **No farming, no soil, no arable ground.** 🔴 Canon: *the nightside must never
  become farmable.*
- ⛔ **No green and no instantly-nameable Earth organisms** (standing bans).
- ⛔ **No lush flora of the ordinary kind** — nothing leafy, nothing photosynthetic,
  nothing that reads as a plant. ⚠️ **This ban is about FORM, not density.** Under the
  owner's three-part lush rule the nightside is promised *"a very different definition
  of lush using very alien life forms"*, so density on the nightside is not forbidden
  — being a **plant** is. See §10.
- ⛔ **No ordinary animal silhouettes at all.** If a player can tell it is a creature
  before it acts, it is wrong for this biome.

## 7. Uniquely available

- ⭐ **Cryogenic feedstocks, sorted and pure, by the basin.** Ammonia (fertiliser,
  refrigerant, explosives precursor), CO₂ ice, and liquid hydrocarbons — the planet's
  chemical industry has exactly one raw source and this is it. 🔑 **Which pan you
  stand in decides which chemical you get**, so prospecting here is real and
  map-driven rather than generic mining.
- **Fuel** — the propane lakes are the only large-scale liquid fuel on Ash'karr, and
  extracting it in an oxygen atmosphere with heated equipment is the single most
  dangerous industrial act in the game.
- **Perfect, indefinite preservation.** The nightside is the planet's archive and its
  hiding place: nothing decays, nothing rusts, nothing is found. Canon puts four
  **Free Droid Enclave** seats out here — immune to the cold, invisible because they
  can run cold, and safe from organics who cannot.
- **Cold as a resource** — free superconduction, free refrigeration, free heat
  rejection for anything that needs it.
- ⚠️ **Not food, not water, not fuel-you-can-burn-indoors, not safety.** And ⛔ not
  farmland, permanently.

## 8. Inhabited objects

Whoever is out here is out here **to be un-findable**, and everything they build
fights the same fight: stay warm inside, be cold outside.

- **Buried and bermed structures**, walls thick with ice, exteriors deliberately at
  ambient — the architectural language is **thermal camouflage**, and it is unique to
  this hemisphere.
- **Droid enclaves** — canon: *The Trade Socket*, *Vent Nine*, *Coldfire*, *The
  Cracking Station*. Machines that need no heat build the only comfortable
  settlements on the nightside, and they build them **cold on purpose**.
- **Cracking and tap plant** on the pan margins: condenser trains, tank farms and
  pipe runs, standing in the open, uncorroded and perfect after centuries.
- **Everything that ever landed here is still exactly where it landed**, in the
  condition it landed in. The nightside does not bury, dissolve or overgrow. It is
  the fourth and last ruin-language on the planet: **untouched**.

## 9. Artistic theme

**"A chemistry set the size of a hemisphere, switched off, in the dark."**

Palette: **blue-black and slate** ice · **starlight grey**, the only ambient there is
· and then, in the pans and nowhere else, **shockingly clean saturated chemistry
colour** — ammonia's cold white-blue, CO₂ frost's flat matte white, hydrocarbon
slush's brown-amber and oily iridescence, and the odd sulfur-yellow rime. ⛔ **No
warm light anywhere except what the player brings**, which is why the player's own
lamp is the most emotionally loaded object in the biome.

Light: **no source.** Everything is ambient starlight — flat, blue, and just barely
enough. Objects are read by rim and by silhouette against the sky, not by their
faces. Any directional light in a nightside shot is artificial and belongs to
someone, and the player should read it that way instantly.

Silhouette language: **low, horizontal, geological.** Slabs, terraces, shelves,
rims, fracture lines. Living things are **indistinguishable from landform** — sheets,
crusts, lobes, mounds — and their scale is announced only by something small and
warm standing next to them. ⭐ The composition rule is that the viewer should not be
able to tell which part of a nightside picture is the creature until it is told.

Against the dune sea's glare and the terminator's stripes this must read as **the
place where the planet stops**: still, silent, enormous, patient, and entirely
uninterested in you until you turn the heating on.

## 10. ⭐ THE DOOR THIS SHEET LEAVES OPEN — nightside "lush" (owner, 2026-09-05)

> *"And then there will be a very different definition of lush using very alien life
> forms on the night side."*

🔑 **This is the owner's stated intent, and it is not this biome.** The sheet above
describes the nightside's *default* state — the inert ice uplands and the sorted pans,
sparse by construction, because a seam metabolism is a starvation metabolism. A
**dense** nightside biome needs a richer seam than an upland offers, and the mechanism
for one is already sitting in §2 waiting to be used:

- The **deepest, coldest pans** hold the largest and most reactive inventories:
  hydrocarbon slush lying against oxidised frost, metres thick, laid down over a
  geological age and still unreacted.
- A catalyst on *that* interface is not starving. It has real power density, and the
  constraint that keeps upland life flat and slow is lifted.
- ⇒ **Volume becomes worth building.** Sheets stack into masses, masses into
  structures, and a pan floor fills with something dense, three-dimensional, metres
  deep and packed — **lush by every measure except that no part of it is a plant, none
  of it is green, none of it photosynthesises, and none of it reads as life at all.**
  Crystalline, laminar, chemically vivid, and completely still.

⛔ **Do not build it inside this sheet.** It is a distinct biome with a distinct
anomaly — the deep pan, not the upland — and it needs its own definition sheet and its
own roster. What this sheet does is **reserve the ground for it** and record why the
mechanism is available. ⚠️ Its palette must stay in the nightside's register —
saturated chemistry colour under starlight — because if a nightside-lush biome ever
reads as *a forest in the dark*, both sheets have failed.

## Roster consequences (the sheet is the admission test)

**Wanted:** sessile catalytic sheets, crusts and lobes at landform scale · organisms
that are indistinguishable from terrain · the one-move animal · clonal colonial
forms · thermal-sensing predators that strike at heat sources · chemical-frost
formations that are ambiguously alive.
**Barred on sight:** anything that walks, runs, flies, flocks, herds or flees ·
anything warm-blooded · anything that glows · anything green or photosynthetic ·
anything with eyes · anything with a normal creature silhouette · anything that
disperses seeds or spores · anything instantly nameable.
🔴 **The hardest admission test on the planet.** Most creature defs in every donor
mod fail this sheet at the first line, and that is correct: the nightside's roster
should be **very short, very strange, and mostly not obviously fauna at all**. If a
candidate reads as an animal, it belongs at the terminator instead.
