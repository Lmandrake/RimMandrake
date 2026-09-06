# The Dune Sea — biome definition sheet

_First pass, 2026-09-05, to the grammar in `README_BIOME_GRAMMAR.md`._

**The design problem this sheet had to solve:** the owner ruled that *emptiness is a
texture* and that most of the dayside should be vast unbroken dune. So this sheet is
forbidden the usual escape — it may not make the deep dayside interesting by putting
things in it. It has to make the **absence** load-bearing. The way through is that
the deep dayside is not merely hot and dry; it is the only place on Ash'karr where
**time does not pass**. Nothing here has ever experienced a night, a dawn, a season,
or a moving shadow. That single fact does more damage to biology than the heat does.

## 1. What it is

A corrugated ochre plain that goes on past every horizon, under a star that has not
moved in the history of the world.

Every dune runs the same way. Every crest is the same distance from the next. The
grain of the sand-sheet is so regular that from a ridge it reads as a machined
surface, and it holds that regularity for a thousand kilometres in every direction —
the largest single texture on the planet and very nearly the only one.

Your shadow is short, hard-edged, black, and **it never changes length**. Set a
stone down and the shadow it throws will be exactly that shadow when your
great-grandchildren find it. There is no morning here, no evening, no cool hour to
wait for. The light is a fixed condition, like the pressure at the bottom of a sea.

It looks dead, and it very nearly is — the standing crop of this biome would fit in
a bucket. But walk it and you find the sand is **dotted with glass**: small
water-clear nubs flush with the surface, one every few paces, catching the sun.
They are the only visible part of almost everything alive here. And every few days'
travel there is a **shape on the horizon large enough to be mistaken for terrain**,
moving at the speed of a shadow on a sundial, carrying its own weather underneath it.

It ends the way an ocean ends. Somewhere out at the edge of the tract there is a
**line of green a hundred metres wide** — a river, or the Scald's shore — with jungle
on it so thick you cannot walk into it, and desert on both sides of that within a
stone's throw. ⭐ There is no gradient. The dune sea does not thin out, fade, or
become scrubland. It simply **stops at a green line**, and that single hard edge is
the most dramatic thing on the dayside.

## 2. Planetary position

**Deep dayside (θ ≈ 0-40°), +70 °C at the substellar point falling to about +52 °C
at the outer edge.** `ExtremeDesert` unbroken below θ 30, `ExtremeDesert` with
`Desert` on the high-noise ground out to θ 40 (`ASHKARR_WORLD_DEFINITION.md` §5b).

- **Energy regime:** eternal noon. The photon budget is not merely adequate, it is
  **in ruinous surplus** — the limiting resource is water and the limiting *danger*
  is the light itself.
- **Temperature:** lethally hot and, crucially, **absolutely constant**. No diurnal
  swing, no seasonal swing, no relief. This is the axis that bans small bodies.
- **Anomaly:** ⭐ **the permanent unidirectional wind** — and the total absence of a
  day-night cycle that creates it.

### Why the wind never turns — the mechanism 🔴
The substellar point is a permanent low-pressure cell: air is heated there, rises,
and is replaced by surface air flowing **inward from every bearing**. On Earth, dune
fields get their disorder from wind reversal — a sea breeze that swings, a monsoon
that turns, a winter that comes. Ash'karr's dayside has **no reversal of any kind**,
because it has no clock to drive one. The surface wind at any point in the dune sea
has blown from the same bearing, at roughly the same strength, since the planet
locked.

⇒ **The dunes are pure transverse ridges** — parallel, evenly spaced, all facing the
same way, migrating slowly toward the substellar point. ⛔ No star dunes (they need
three wind directions). ⛔ No barchan swarms, no reversing crests, no dune chaos.
The dune sea is *ordered*, and that order is the texture that carries the emptiness.

⇒ And it is a **compass**. Dune crests run perpendicular to the wind, and the wind
runs toward the sun. A traveller who can see one ridge knows which way the star is
without looking up. This is how the Deep Desert Tribes navigate a landscape with no
landmarks — 🔑 and it is why they can live where nobody can build a road.

⇒ This biome cannot occur anywhere else. Past θ ≈ 45° the wind field begins to be
disturbed by terrain and by the terminator's convection, and the grain breaks up.
The perfect corrugation is a signature of the deep dayside and nothing else.

### Where the dune sea ENDS — the lush rule, and it is a LINE 🔴
Owner, 2026-09-05: *"The rivers and coasts are the only lush areas on the dayside."*

⇒ 🔑 **Dayside lush is a line on the map, never a region**, and this biome is what
the line is drawn against. The mechanism is already canon: rain on Ash'karr condenses
only at altitude, so a dayside river is a **thin thread of moving fresh water crossing
a landscape that gets none** — and at +55 °C under unlimited light, water is the
*only* missing input. Put it back and productivity goes vertical within metres of the
bank. Take it away and there is nothing.

- The **Scald's rivers** carry the planet's only true jungle (canon:
  `AB_FeraliskInfestedJungle`, `COMIGO_GreaterSwamp_Tropical`), and the **Scald's own
  coast** is the one dayside shoreline that behaves like a shore.
- ⛔ **Everything more than a short walk from flowing water or that coast is dune
  sea**, and the transition has no middle. A riparian tile and an `ExtremeDesert` tile
  can be neighbours.
- ⚠️ **Not the terminator.** The terminator's coast is saturated brine under a low
  sun, and it is salt and solitude, not green (`terminator_sea.md` §2).

⇒ The dune sea's job in the composition is to make that line *mean* something. A
green ribbon is only staggering if it is one ribbon in an ocean of nothing, and the
ocean of nothing is this sheet.

## 3. Driving forces

**Unlimited light, no water, no night, and a wind that has never once changed its
mind.** Everything below follows from those four.

## 4. How the biology adapted

**Nothing here tracks the sun, because the sun does not go anywhere. Everything here
owns a shadow instead.**

- **The flora is buried; only its optics are above ground.** With light in surplus
  and water absent, a leaf is a catastrophe — surface area is where you lose water
  and where you cook. So the photosynthetic tissue sits **one to three metres down**,
  in sand cool enough and damp enough to work in, and the plant's entire above-ground
  investment is a **light-pipe**: a glassy, silica-cemented nub, flush with the
  surface, that admits a metered fraction of the light and rejects the rest. The
  visible biome is a scatter of glints. The actual biome is underneath you.
  ⇒ 🔴 **Nothing here is green and nothing here has leaves.** The rejecting surfaces
  are white, mirror-bright, or clear. **Bright white is the dayside's pigment** in
  the same way black is the terminator's.
- **Every organism is polarised on the sun-axis, and nothing is radially
  symmetrical.** A shadow that never moves means the shaded face of a body is a
  permanent, addressable microclimate — tens of degrees cooler, forever. So bodies
  differentiate into a **sun-face and a shade-face** that are not variations of the
  same tissue: the sun-face is mirror, ceramic, ablative armour, and carries nothing
  soft; the shade-face carries **every opening the organism has** — gas exchange,
  sensory pits, reproductive structures, young. In silhouette everything looks like
  it is leaning away from something, or like half a creature glued to a shield.
- **There is no circadian clock anywhere in this biome**, because there has never
  been anything to entrain one to. The consequence is that life here is not
  *rhythmic*, it is **event-driven**. The default state of the dune sea is
  **dormancy**, measured in years. What ends dormancy is not a time of day; it is a
  trigger — free water, a vibration, a temperature anomaly, blood. The biome does
  not wake up on a schedule. It wakes up because **something did something**.
  ⇒ 🔑 This is the answer to the emptiness. The dune sea is not lifeless, it is
  **latent**, and it is armed. It looks the same whether it is empty or loaded, and
  the player is the detonator.
- **Bodies are either enormous or microscopic. There is nothing in between.** At a
  constant +60 °C a small body equilibrates with the air within minutes and has no
  way to shed heat except water it does not have. The only passive defences are
  **mass** (thermal inertia — a large enough animal simply never reaches ambient) and
  **depth** (a small enough animal never leaves the cool sand). Both work; the middle
  does not. ⇒ Fauna is bimodal: **giants on the surface, and grain-scale life below
  it**, with a hard gap where every ordinary animal would be.
- ⭐ **The giants carry the only moving shadows on the planet, and there is an
  ecology living in them.** A hundred-tonne walker throws a patch of shade that is
  cooler than anything else for a hundred kilometres, and it moves — so commensals
  ride it, shelter under it, and follow it, and its underside is wetter, cooler and
  busier than the entire landscape it crosses. ⇒ Gameplay: **following a giant is
  how you cross the dune sea.** A caravan that stays in the shade of a walking
  mountain travels; a caravan that does not, does not.
- **Predation cannot work by ambush, because there is no cover.** With visibility
  to the horizon in every direction, hunting is either **subsurface** (something
  comes up through the sand under you — the sand is the only cover there is) or
  **attritional** (something follows you at your own speed and waits for you to run
  out of water). Nothing here charges out of a bush; there is no bush.

## 5. Always true

- The light is **hard, white, unmoving and directly overhead-ish**, and every shadow
  in the biome points the same way and is the same length.
- **The dune grain is parallel and regular**, and its bearing points to the star.
- **There is no water of any kind** — no standing water, no ice, no fog, no
  condensate. What water exists is inside living things, which is why they are hunted.
- **Nothing is dormant-looking; everything is actually dormant.** Absence of visible
  activity is the normal state and proves nothing.
- Surfaces are **dry, matte, dusty or mirror-bright** — never wet, never slick,
  never encrusted.
- **Anything buried is perfectly preserved.** Dry, hot, sterile sand is the best
  archive on the planet.
- The density of everything is **absurdly low**. A correct dune sea map is mostly
  nothing, and a reviewer's instinct to add one more thing is the defect.
- **The tract ends at a hard edge or not at all.** Where it meets a river or the
  Scald's coast the boundary is metres wide; everywhere else it simply continues.

## 6. Never true 🔴 (hard bans — checkable)

- ⛔ **No day-night cycle, no dawn/dusk lighting, no moving shadows, no nocturnal or
  diurnal behaviour, no sleep cycle, no circadian anything.** A def with a nocturnal
  activity pattern is a violation on sight.
- ⛔ **No star dunes, barchan swarms, reversing crests or crossed dune bearings.**
  Every dune in a dune-sea tile runs parallel to every other one.
- ⛔ **No green, no leaves, no above-ground foliage of any kind.** Above-ground plant
  parts are glassy, white or mirrored, and small.
- ⛔ **No radially symmetric organisms** — everything is sun-axis polarised.
- ⛔ **No standing water, no ice, no fog, no rain, no potable source.**
- ⛔ **No fire.** There is no fuel; a wildfire in the dune sea is a rendering error.
- ⛔ **No medium-sized fauna.** Body sizes are giant or grain-scale, nothing between.
- ⛔ **No ambush-from-cover predators and no cover.** Subsurface strikes only.
- ⛔ **No lush flora anywhere in the tract, and no gradient toward it.** 🔴 Dayside
  lush is confined to the river and coast LINES (owner's three-part lush rule, §2):
  checkable as a maximum distance from flowing water or the Scald shore, outside which
  no lush plant def may be placed. ⛔ And no scrubland, semi-arid or shrub transition
  band may be painted between them — the edge is hard.
- ⛔ **No instantly-nameable Earth organisms** (standing recognizability ban — and
  🔴 doubly strict here, because everything the player *does* see is huge, and a
  recognisable giant is the worst offence there is).
- ⛔ **No corroded ruins.** Nothing rusts without an electrolyte; dayside wreckage is
  **sand-scoured bright and half-buried**, never brown.
- ⛔ **No roads through the deep dune** (owner's ruling on the Deep Desert Tribes),
  and ⛔ no permanent structure not either buried or actively dug out.

## 7. Uniquely available

- ⭐ **Solar power at 100 % uptime, forever.** This is the only place in the game
  where a solar array has no night, no season and no weather. It is the single
  strongest reason to plant anything here at all, and it is a genuine strategic
  offer: infinite power in exchange for infinite logistics.
- **Optical-grade biosilica** — the light-pipe nubs are real lenses, harvested by the
  handful, and the only natural glass on the planet that is not volcanic.
- **Giant mass** — hide, plate, tallow and bone at a scale nothing else on Ash'karr
  provides, from animals that cannot be ambushed and cannot be outrun, only outlasted.
- **Perfect preservation.** Anything the sand has taken comes back intact — the
  dayside's ruins are *pristine and buried*, where the poison forest's are *corroded
  and standing*. Two utterly different salvage games, and a Jawa clan wants both.
- **Sightlines.** You can see anything coming from an hour away. So can it.
- ⚠️ **Not water, not shade, not cover, not food.** The deep dune kills by absence,
  exactly as the map doc says, and it is the only biome where the *terrain itself* is
  the antagonist.

## 8. Inhabited objects

Nothing stands still here, because the sand is always moving one way: a structure is
**buried on its windward face and undercut on its lee**, so it walks itself out of
the ground over centuries and then back in. ⇒ The characteristic sight is a **hull,
mast or wall emerging from a dune face** — half in, half out, and bright.

- **Sandcrawler tracks and wallows** — the Jawa Trade Moot's circuit is here, and
  crawler-scale machines are the only settlements that make sense in a landscape that
  buries fixed ones.
- **Deep Desert Tribe holdings** — canyon lips, rock islands, and dug-in shelters far
  from everything including each other, with **no roads leading anywhere** (owner's
  ruling). A tribal camp is reached across open sand or not at all.
- **Buried finds** — the dayside's great salvage prize: sealed, dry, uncorroded,
  and only findable when the dune moves off it or a giant's foot breaks the crust.
- **Toward θ 0**: the Rust Cathedral and the Rust Flats. 🔑 Everything the wind
  carries goes inward, so the substellar point is where the whole dayside's dust
  eventually arrives — the Cathedral sits at the bottom of a planet-sized drain.

## 9. Artistic theme

**"A machined ochre surface under a star that has not moved since the world began."**

Palette: ochre, bone, rust-tan and pale gold in the sand · **bleached white sky**,
not blue — the glare washes the colour out near the sun · **hard black shadow** with
no penumbra and no colour in it · mirror-white and clear glass on every living
surface. The palette is deliberately **narrow and hot**, and the only strong
contrast in the entire biome is the black of the shadows.

Light: **one source, hard, high, unmoving, and cruel.** Everything has a bright top
and a black underside and there is no gradient between them. Nothing is backlit,
nothing is dappled, nothing glows.

⭐ **And the one colour absent from this palette is the point.** Where the tract meets
a river or the Scald's coast, a **hard green line** arrives with no warning and no
transition — the most saturated thing on the dayside, made staggering by the two
hundred kilometres of ochre either side of it. Draw the desert so the line lands like
a shout.

Silhouette language: **long horizontals and one vertical.** The horizon line and the
dune grain do all the work; verticals are rare enough that a single one is an event —
a shard, a mast, a stopped machine, a leg. Living things read as **half-shapes**:
armoured, leaning, one-sided, with everything soft hidden on the dark face. Giants
are drawn at a scale that breaks the composition on purpose.

Against the terminator's striped black-green and the nightside's blue-black stillness
this must read as **the planet's default state** — the thing every other biome is an
exception to. It is not a place you visit. It is the distance between places.

## Roster consequences (the sheet is the admission test)

**Wanted:** subsurface glass-nub flora · mirror/ceramic-plated surface megafauna ·
sun-axis-asymmetric bodies · sand-burrowing strike predators · grain-scale
subsurface micro-fauna · dormant forms that trigger on water, blood or vibration ·
commensals that live under a walking giant.
**Barred on sight:** anything green · anything leafy · anything nocturnal or
sleeping · anything medium-sized · anything radially symmetric · anything wet ·
anything that ambushes from cover · anything lush or riparian (that belongs to the
river line, a different sheet) · anything instantly nameable — 🔴 and the size rule
makes a recognisable giant the single worst admission this sheet can make.
**Population target:** ⭐ *sparse to the point of discomfort.* The correct number of
distinct creature defs in the deep dune is small and the correct spacing is
enormous. If the dune sea's roster looks healthy, it is wrong.
