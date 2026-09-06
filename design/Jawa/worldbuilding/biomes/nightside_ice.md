# The Nightside Ice — biome definition sheet

_First pass 2026-09-05 (the nightside as a whole); **second pass 2026-09-06, owner +
BENCH**, binding it to a def and reconciling it with the seven sheets that landed since.
The first pass's ecology (§4) stands **unchanged, word for word** — owner's ruling. Defines
**`RUT_NightsideIce`** (our own def, inheriting vanilla `IceSheet`'s shape — owner's
ruling: own def, not a patch; name owed if the dirty-ice plateau wants one). Thematic
handle: **the drain of the atmosphere** — and its image: **dirty white ice on the highest
ground of the night, under the aurora, with something moving inside it.**_

🔑 **Read against `the_blue_desert.md`, `the_propane_lakes.md`, `the_lantern_deeps.md`,
`forsaken_crags.md`.** This sheet is the deep night's **uplands**; the pans and lows are
theirs. The physics the first pass reasoned from — the antistellar point as the
**fractional distillation column the size of a hemisphere**, freezing the atmosphere out in
order of freezing point — has since been made literal by the phase-line sheets, and this
sheet is now the column's top.

## 0. The measurements everything rests on

MEASURED 2026-09-06 off `world/ASHKARR_WORLDMAP_tiles.csv`. Vanilla `IceSheet` holds 49
tiles today (Deadstone, −52 °C). After the ruled re-home (`HORRORWASTES_BIOME_DISSOLVE_1`;
`the_lantern_deeps.md` §0) the def holds **802 tiles**: the dissolved ring's highland
sectors 1–3 (337 tiles, elev median 1,271 m) + the former crystal caverns' high ground
(416 tiles ≥ 900 m) + its own 49. Arc 128→159; temp p10/median/p90 **−70 / −56 / −39 °C**;
**elevation median 1,129 m (max 1,884) — the deep night's mountains, under ice.** Regions
Deadstone 509, Umbra 158, Ammonia Flats 73, Rimewall 30. Sectors 0–5 and 7–10 —
**highland lobes, accepted as topography (owner's ruling), not a band**: chemistry here
follows basin depth and height, never arc, which is the sheet's own anti-bullseye argument.

🔴 **Own def, not a patch (owner's ruling).** Vanilla `IceSheet` carries an arctic zoo,
coastal walrus and penguin, salmon and cod, snow at commonality 60 with DLC-gated
blizzards, and a worldgen worker; patching all of it out across `MayRequire` branches is
silent-failure territory. `RUT_NightsideIce` inherits the shape (terrain `Ice`, no roads,
no rivers, `isExtremeBiome`) and overrides every list. Rides `NIGHTSIDE_ICE_DEF_1`.
Vanilla's one line survives as this sheet's epigraph: *"The only animals here are
migrating to somewhere else — or badly lost."*

## 1. What it is

Ice as hard as quartzite, **white**, on the highest ground of the night, under a sky of
stars and aurora, absolutely still at its heart.

Not blue: **dirty ice** (owner's ruling). Ice only turns blue when it is very pure, clean,
old and compressed; white ice holds impurities — bubbles, mineral dust, everything the
distillation column drops from the sky. So the highland is the **geologically active ice**
— still ancient, but *recent* as ice goes, not yet compressed to solid mineral crystal:
it flows, it fractures, it holds things, and things within it burst out more easily than
anywhere on the nightside. The interior has no wind — this is the bottom of the global
circulation, where air arrives and stops — and no snow underfoot, because at −60 °C
water ice does not behave like snow, it behaves like rock. The ground rings when you
strike it and fractures in slabs.

The basins below are the point of the place, and they belong to their own sheets now:
every low spot is a pan of frost that is not water — ammonia in one, hydrocarbon slush in
the deepest — and the propane lakes lie lower still, liquid, under breathable oxygen, and
**you are the only source of ignition on the hemisphere.**

Nothing moves on a human timescale — on the *surface*. The hills have metabolisms. What
you take for a boulder field has been slowly eating the frost beneath it since before
your species had writing, and one of those boulders has been saving up, for two hundred
years, to move exactly once. And inside the dirty ice, unseen, something is tunneling
toward the warmth of whatever just lay down to die.

## 2. Planetary position

**Deep nightside highland (arc 128–159; the coldest high ground on the planet) × the
cold-trap anomaly, upland half.** The antistellar point is the planet's condensation sink;
this sheet is the inert-ice top of that column, and the Blue Desert, the Ammonia Flats and
the propane sea are where the frost the uplands shed finally pools.

- **Energy regime:** none from the sun, none from below — 🔴 explicitly **no vents, no
  geothermal, no volcanism**. What arrives is what the atmosphere carries in, and (second
  pass) what the aurora's ground currents deliver.
- **Temperature:** the active axis — it removes species from the gas phase one by one.
- **Anomaly:** the cold trap. Sorting by freezing point into topographic pans.

### Why this is not a ring, and cannot be moved 🔴
Descending air deposits *downslope*, into whatever the local topography holds; the
chemistry of a place is set by the depth and temperature of its basin, not by arc.
⇒ A scatter of chemically distinct pans separated by inert ice uplands — the uplands are
this sheet. Move it fifty degrees dayward and the ice softens, the pans empty, and there
is nothing left.

⚠️ A first-pass claim is struck: *"`AB_RockyCrags` is the dominant terrain past θ 130"* —
the crags are twilight (arc 103–121, `forsaken_crags.md`); the deep night is the Blue
Desert, this highland, the caverns' former ground, and the propane country.

## 3. Driving forces

**A hemisphere-sized cold trap with no light from the sun, no wind at its heart and no
heat from below, where the only energy available is the chemical disequilibrium of an
atmosphere frozen out in the wrong order** — and, on the highland, the slow violence of
dirty ice.

### The six reconciliations (owner-ratified, 2026-09-06)

1. **Wind — the ice sheet is the SOURCE.** Cold air pools on the high plateau and drains
   off its edges: that *is* the katabatic wind that strips the Blue Desert bare. Interior:
   dead still, as the first pass wrote. Margins: the drainage. The ice sheet makes the
   wind it never feels.
2. **Light — aurora, not just starlight.** The propane sheet ruled aurora most of the clear
   time on the dark side; the highland adopts it. The first pass's real rule survives —
   *no warm light except what the player brings* — because aurora is cold light, and
   nothing native cares: nothing here sees.
3. **Glow — the ban stands for surface residents.** The Lantern Deeps beneath glow, and
   their emergences leak light at the surface: an injection, not a native (§6 marks the
   exception).
4. **Speed and warmth — partition by chemistry.** The water-ice uplands keep the starvation
   seam metabolism — slow, sessile, laminar. The hydrocarbon lows (Blue Desert, propane,
   Ammonia Flats) carry the fuel-life; the Burners cannot enter here — no fuel to burn,
   nothing to eat.
5. **Falling weather — none on the interior.** Deposition happens in the pans (fuel snow is
   the propane sheet's; drift is the Blue Desert's). Vanilla's snow and blizzards re-skin
   as **ablation at the margins**, not precipitation.
6. **The §10 door is now occupied** — by the Rot on the night shoulder and the Ammonia
   Flats' deep-pan life (`the_propane_lakes.md`); the reservation becomes pointers.

### Dirty ice — the second pass's physics (owner-ratified)

- **Ice flow and crevassing.** Young, impure ice creeps; the plateau is scored with
  crevasses that open and close over years — the ruled collapse hazard, in ice. The
  warning vocabulary: **frost-sift and rime-fall at a crevasse lip**, and the grumble.
- **Things burst out.** Impure ice holds inclusions, and flowing ice delivers them to the
  surface *violently* — pressure release, a slab calving — and whatever was frozen inside
  is suddenly in the open: pieces of the terramanufacture's collapsing machine, the war's
  cocoons where the highland meets Deadstone, the well-provisioned dead of failed Junker
  crystal expeditions, and the tunnelers.
- 🔑 **The thaw pulse is the disaster.** Vanilla's cold snap is meaningless at −56 °C; the
  *inverse* is the event: a warm intrusion — a reconnection storm dumping energy, a
  machine venting, **your own base** — softens dirty ice, and softened dirty ice slumps,
  calves, and releases what it held. Heating is the threat generator (§4); dirty ice gives
  it a second mechanism beyond thermal sensing.

## 4. How the biology adapted

_(First pass, verbatim — owner's ruling: unchanged.)_

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

### Second pass — the highland's additions (owner-ratified)

**Animals and plants are nearly nonexistent; the population is mostly corpses and dying
lost souls** (owner). Too hot for the truly icy beings of the propane country; too cold for
anything from the terminator — the plateau is the gap in both ranges.

- ⭐ **The tunnelers** — the naked-mole-rat analog: blind, thermal-sensing (§4), moving
  *within* the dirty ice where nothing on the surface ever sees it, feeding on what little
  arrives — which is the lost. A body dying on the plateau is a warm signal in the ice;
  the tunnelers come to it from below. **Surfacing is the burst.** Colonial, clonal, one
  warren per pan-margin. A threat to the dying, and — through a thaw pulse — to a camp
  that has made itself warm.
- **Icy insects** — the small life of the inclusions: things that live in the bubbles and
  mineral veins of dirty ice, active only in a thaw pulse, dormant otherwise. Harmless
  individually; a slumping slab full of them is not.
- **Corpses and the lost** — not fauna, the biome's real population: what wandered too
  far from the terminator, what came down from orbit, perfectly preserved. The lost-soul
  events (§4b) are how they arrive.

## 4b. Weather and events — the equivalence table (owner-accepted)

Vanilla ice-sheet incidents, and what happens here instead:

| vanilla ice sheet | here |
|---|---|
| cold snap | ⭐ **thaw pulse** — the inverse; the ice softens and releases |
| blizzard / hard snow | **rime-fall** off the crags' margin; ablation drift at the escarpment; never on the interior |
| aurora (cosmetic) | **reconnection storm** — radiation up, circuits surge, the electrojet tap over-produces, the tunnelers stir |
| meteorite / ship chunk | **calving delivery** — inclusions burst out: chunks, pods, a cocoon, a machine part |
| wanderer joins / refugee / traveler in need | **the lost soul** — a dying traveler on the plateau; save them or bury them; the tunnelers are already coming |
| animal migration passing | **the one-move animal commits** — once, ever; and Junker crystal expeditions crossing, failing |
| psychic drone / mech cluster | not here by default — the propane country and the Deeps (`MECHANOID_BIOME_PRESENCE_REVIEW_1`) |
| toxic fallout / volcanic winter | **the crags' Dark drifting over the plateau** — the tholin cloud, sensor loss |

Standing weather: **aurora-clear** (interior), ablation drift (margins), rime-fall
(the Rimewall edge). 🔴 No rain (R-H1). No precipitation on the interior.

## 5. Always true

- **The sky is bright and cold** — starlight and aurora; no warm light exists but yours.
- **The interior is still**; the margins drain — the wind starts here and leaves.
- **The ground is hard, white, and moving on a geological clock** — dirty ice: it
  fractures, it flows, it holds inclusions, and it gives them up.
- **Chemistry is sorted by basin** — and the basins are other sheets'.
- **Everything alive on the surface is old, huge, stationary and unrecognisable as
  life**; everything alive *inside* the ice is blind, slow, and coming toward warmth.
- **Anything left here is preserved perfectly and indefinitely** — bodies, machines,
  records, and mistakes — until the ice calves it back out.
- ⚠️ **Fire is possible and catastrophic** below, in the pans; **warmth is catastrophic**
  here, on the ice.

## 6. Never true 🔴 (hard bans — checkable)

- ⛔ **No vents, no geysers, no geothermal, no volcanism, no hot springs, no fumaroles.**
- ⛔ **No bioluminescence in surface residents** — a seam metabolism cannot afford photons.
  🔑 Exception by injection: Lantern Deeps emergences (`the_lantern_deeps.md`) leak the
  caverns' glow at the surface; they are not residents.
- ⛔ **No photosynthesis and no photosynthetic tissue of any kind.**
- ⛔ **No liquid water anywhere, in any form, ever.**
- ⛔ **No precipitation on the interior** — no snowfall, no drifts, no blizzards; ablation
  and rime-fall occur only at the margins. Deposition is the pans' business.
- ⛔ **No wind on the interior** — katabatic drainage exists only at the escarpment; a
  storm def resident on the plateau is a violation.
- ⛔ **No warm-blooded, fast, pursuing, fleeing or flocking fauna** on the surface; the
  tunnelers move only within the ice and surface only to feed or in a thaw pulse.
- ⛔ **No vision-based or sound-based sensing, and no vibration/ground-sense.** Thermal
  only.
- ⛔ **No spores, seeds, pollen or airborne dispersal.**
- ⛔ **No farming, no soil, no arable ground.** 🔴 Canon: *the nightside must never
  become farmable.*
- ⛔ **No icy dayside analogs and no instantly-nameable Earth organisms** — vanilla's
  arctic zoo is evicted with the def.
- ⛔ **No lush flora of the ordinary kind** — nothing leafy, nothing that reads as a plant
  (form, not density — see §10).
- ⛔ **No ordinary animal silhouettes at all.** If a player can tell it is a creature
  before it acts, it is wrong for this biome.
- ⛔ **No blue ice as the standing surface** — the highland is dirty white ice; pure blue
  ice is the Blue Desert's ancient compressed floor, not this.

## 7. Uniquely available

- **The ice itself, impure** — not the Blue Desert's distilled-purity blocks; dirty ice
  is water with everything the sky dropped in it (`WATER_KINDS_TAXONOMY_1` row: dirty ice
  → melt → filter).
- ⭐ **What the ice gives up** — calving delivers inclusions: machine parts of the
  terramanufacture, cocoons, pods, the well-provisioned dead. Prospecting here is waiting
  for the ice to move, or making it.
- **Perfect, indefinite preservation** — the planet's archive and hiding place; canon puts
  four **Free Droid Enclave** seats out here, cold on purpose.
- **Cold as a resource** — free superconduction, refrigeration, heat rejection.
- **The electrojet tap** works here too (`the_propane_lakes.md` §7), weaker than at the
  pole.
- ⚠️ **Not food, not water you can drink unfiltered, not fuel, not safety.** And ⛔ not
  farmland, permanently.

## 8. Inhabited objects

Whoever is out here is out here **to be un-findable**, and everything they build fights
the same fight: stay warm inside, be cold outside — and now, on dirty ice, *stay light*,
because a warm building softens its own foundation.

- **Buried and bermed structures**, exteriors at ambient — thermal camouflage, unique to
  this hemisphere.
- **Droid enclaves** — canon: *The Trade Socket*, *Vent Nine*, *Coldfire*, *The Cracking
  Station* — highland holdings, built cold on purpose, nothing organic climbs to −60 °C.
- **Cracking and tap plant** on the pan margins, uncorroded and perfect after centuries.
- **The failed Junker crystal expeditions** — crossing this ground toward the Deeps'
  mouths and preserved on it exactly as they died.
- **Everything that ever landed here is still exactly where it landed** — the fourth and
  last ruin-language on the planet: **untouched** — until the ice calves it out.

## 9. Artistic theme

**"A chemistry set the size of a hemisphere, switched off, under the aurora."**

Palette: **white dirty ice** over blue-black rock at the fractures · aurora green and
violet as the ambient · starlight grey · and then, in the pans and nowhere else, the
shockingly clean saturated chemistry colour of the other sheets. ⛔ **No warm light
anywhere except what the player brings** — which is why the player's own lamp is the most
emotionally loaded object in the biome.

Light: cold and *from above* — aurora and stars; objects read by rim and silhouette. Any
warm directional light in a nightside shot is artificial and belongs to someone.

Silhouette language: **low, horizontal, geological** — slabs, terraces, crevasse lines,
calving faces. Living things are indistinguishable from landform; ⭐ the viewer should not
be able to tell which part of the picture is the creature until told — and now, a second
tell: a fresh slab-fall with something in it.

## 10. The door — occupied (second pass)

The first pass reserved "a very different definition of lush using very alien life forms
on the night side." It has since been built: **the Rot** (`the_rot.md`, the night shoulder's
pale sprawl) and **the Ammonia Flats' deep-pan life** (`the_propane_lakes.md`). This sheet
stays the sparse default those two are exceptions to.

## Roster consequences (the sheet is the admission test)

**Wanted:** sessile catalytic sheets, crusts and lobes at landform scale · organisms
indistinguishable from terrain · the one-move animal · clonal colonial forms ·
thermal-sensing tunnelers within the ice · icy insects of the inclusions · chemical-frost
formations that are ambiguously alive · corpses and the lost.
**Barred on sight:** anything that walks, runs, flies, flocks, herds or flees on the
surface · anything warm-blooded · anything that glows (residents) · anything green or
photosynthetic · anything with eyes · anything with a normal creature silhouette ·
anything that disperses seeds or spores · anything instantly nameable · anything from the
propane country's fuel-life · anything from the terminator.
🔴 **The hardest admission test on the planet.** The roster should be very short, very
strange, and mostly not obviously fauna at all.

---

## Owed

- `NIGHTSIDE_ICE_DEF_1` — author `RUT_NightsideIce` (inherit vanilla's shape, override every
  list, no arctic zoo, no snow table); paint the 802 tiles under
  `HORRORWASTES_BIOME_DISSOLVE_1`; add it to the world tools' biome list.
- **Name** — owner's pick if the dirty-ice plateau wants one beyond "the Nightside Ice."
- **Tunnelers and icy insects** — authoring (art to the NEW-ART ledger; the within-ice
  movement and the thaw-pulse surfacing are C#), admission at the sitting.
- **Events** — the equivalence table as incident defs: thaw pulse, calving delivery, the
  lost soul, rime-fall/ablation, the Dark drifting over.
- **Engine feasibility pass:** crevasse/collapse in ice with the ruled warning tells; the
  thaw pulse as a temperature-driven map event; inclusions as a calving spawner.
- **Cross-flow ledger**: ice sheet → Blue Desert (katabatic wind); Umbra → here (aurora);
  crags → here (the Dark drifting; rime-fall at Rimewall); Deeps beneath (emergences).
