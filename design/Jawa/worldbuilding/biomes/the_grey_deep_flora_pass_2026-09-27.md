# The Grey Deep — underwater flora pass (2026-09-27)

Status: DESIGN DRAFT — written by a DESIGN subagent for BENCH, not yet ruled on.
Item: `GREYSEA_FLORA_PASS_1`. Commission: owner, by question card 2026-09-26 — every sea
floor gets its own strange-flora pass, in that sea's own register. The Grey's register:
**cold and pale — salt, crystal, brine, stillness.** Nothing shared with any other sea's
roster, and nothing duplicating the owner's own crystalline seven (sheet §4a), which are
built and untouched by this pass.

## Sources read

- `design/Jawa/worldbuilding/biomes/the_grey_deep.md` — the frozen sheet including the
  2026-09-26 additive merge: the six hard bans, §4a's SEVEN owner-specified crystalline
  flora, §4b's formations, §4c's salt snow, §4d's pools.
- `design/Jawa/worldbuilding/biomes/the_grey_deep_danger_floor_pass_2026-09-27.md` — the
  danger pass and its Ruled section: the giant breaks lamps, lit cells yield more, the
  fessk watches from the rim of the light; interior heat does nothing to crust (Ruled 3).
- `design/Jawa/worldbuilding/biomes/the_scald_underwater_flora_pass_2026-09-27.md` — the
  sibling pass, imitated for shape only. Its lesson taken: a twist must belong to ITS
  biome's chemistry (the Scald's cold plant was cut as "silly. No cold." — by symmetry,
  nothing warm grows here except at the one warm thing, and that spot is already taken).
- `src/RimMandrake/TerminalBiomes/Defs/BiomeDefs/RM_GreySea.xml` — live roster:
  `plantDensity 0.14` already set, eight `wildPlants` rows already shipped.
- `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Plants/RM_GreySeaFlora.xml` — the built
  crystalline seven and their three engine laws (`completelyIgnoreFertility`, biome
  plantDensity, the Plants genstep at 900 in `RM_SeaDiveGenerator_GreySea`).
- `src/RimMandrake/TerminalBiomes/Defs/TerrainDefs/RM_GreySeaTerrains.xml` — the five
  terrains and their tags (`RM_GreyBrineChannel`, `RM_GreyChimneySeep`, `RM_GreyBrinePool`).
- `src/RimMandrake/TerminalBiomes/Defs/MapGeneration/RM_GreySeaFloorScatter.xml` and
  `Defs/ThingDefs_Buildings/RM_GreySeaFormations.xml` — pillars, domes, chimneys, jacket,
  four great crystals; none duplicated below.
- `src/RimMandrake/DivingInteraction/Source/GenStep_GreySeaFloorDressing.cs` — BUILT (the
  terrain file's "not painted yet" warnings are stale): it carves the deepest pool, rings
  it with jacket, paints seep aprons and runs the channels. The adjacency placements below
  extend this worker rather than inventing a new one.
- `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Races/RM_GreySeaFauna.xml` and the danger
  pass's §3 table — the fauna the ecology section wires to (fessk, sorruth, essarn,
  otheska, the sessile three, the floor seven).

All ten proposed defNames collision-checked against `src/` (recursive grep with a sanity
probe — `RM_GlassVeilKelp` found in 3 files, proving the instrument sees): every one
FREE. (`Sweetwell`, an earlier candidate, collided with a settlement name in
`ashkarr_settle.py` and was renamed `RM_Milkwell`, which is free.)

## Current state, and what this pass is

**The Grey floor is not barren and this pass must not pretend it is.** The owner's seven
crystalline forms (`GREYSEA_CRYSTAL_FLORA_1`) are BUILT, wired, and density is set: the
architecture of the flora — the geometric solids, the kelp curtains, the vent vines, the
crowns that hurt — exists and is his verbatim design. ⛔ Nothing below touches, revises
or duplicates any of the seven, the salt blade, or the mineral formations.

What the floor still lacks is what the Scald commission named: the SMALL strange layer —
*"strings and filaments of bacterial colonies, sponges, soft corals, all with alien
twists."* The crystal seven are monuments; between the monuments the sediment itself is
bare. This pass is the understorey: hand-height and lower, colonial and soft, the things
a diver stops noticing until a lamp is lit. Where the Scald's understorey survives heat,
the Grey's survives salt — every twist below is an answer to hypersaline cold water, and
none repeats a Scald trick or a crystal-seven trick.

## Design register

Cold and pale — salt, crystal, brine, stillness. The rules the register imposes:

- **Grey wears grey.** The crystal seven own the floor's only colour (pink, violet,
  amber, mineral not glow); the giant's mark owns the only saturation. The understorey is
  bone, chalk, ash-grey, dirty white — with ONE deliberate exception that only exists
  when a player brings a lamp (RM_Murkblush, and lamps have a price here).
- **Nothing glows. Ever.** Ban 4 is absolute and the light-attraction economy makes it
  load-bearing: light in the Grey is the player's own, dangerous, and paid for.
- **Nothing hurries.** The Scald's understorey included the fastest-growing thing on the
  planet; the Grey's includes the slowest. growDays here run long; the fiction of every
  plant is patience.
- **The chemistry is the twist.** Osmosis, crystallisation and its refusal, density
  stratification, salt excretion, dissolution — the tricks of a supersaturated sea,
  never a tourist trick from a boiling one.
- **Marred, always** — his one aesthetic rule, verbatim, on every art brief: *"marred
  slightly, don't make them too perfect or they look manufactured."*

## The roster

Ten new flora. The organizing law, inherited from the sibling pass: **each plant's
survival trick in supersaturated cold brine IS its alien twist, and no two tricks
repeat** — nor repeat any of the Scald's ten, nor any of the crystal seven's. The
tricks, named up front so distinctness is checkable: *accretion* (it builds mineral),
*efflorescence* (it sweats its salt out), *tactile sorting* (it tells food from mineral
by touch), *osmosis* (it freshens the water around it), *self-ossification* (it lives on
the tip of its own dead centuries), *deliquescence* (it dissolves itself on purpose),
*density-surfing* (it rests on the killing interface), *gradient-eating* (it feeds on
the boundary between brines), *anticrystallisation* (salt cannot take it), *structural
colour* (its colour only exists when light is brought). The crystal seven own
*protein-aligned crystal armour* in all its forms — nothing below builds armour of salt,
which is exactly what keeps the two layers visually separate: the monuments are crystal,
the understorey is flesh and felt.

All names invented and franchise-free (`RM_` tier per Q11a); all ten grepped FREE
against `src/`.

### 1. RM_Masonmat — the pillar-mason's skirt; bacterial film, pillar feet and open floor

The Grey's monoculture, finally touchable. The pillar-mason is a crystal-binding film,
and where the film spills off a column's base and spreads across the sediment it is
this: a pale, faintly banded mat, firm as rind, growing outward a hair a year and
mineralising everything it crosses. A masonmat is the mason at pasture — the same
organism whose towers are the only landmarks in the murk, resting between projects.
The sorruth graze it in slow herds of one; a column with a wide skirt is an old column;
and divers walking pillar-to-pillar learn to feel for the rind through their boots,
because where the mat is, a pillar is near.

- **Twist:** *accretion* — the understorey's floor is the architect's skin.
- **Art:** flat ground-hugging mat, chalk-white with faint growth-bands like tree rings
  gone wrong, one edge always ragged (marred); drawSize ~1.0; no glow.
- **Harvest:** none — it is pasture (the sorruth's, see ecology), pathCost only.
- **Numbers:** growDays 18, commonality 1.0 in `wildPlants`, plus GenStep thickening at
  pillar and dome feet (route B). The commonest living thing on the floor.
- ⚠️ **Owner question 3:** this def makes a piece of the mason harvestable-adjacent and
  destructible. The mason stays fiction as a whole (no pawn, per
  `GREYSEA_ANCHOR_CREATURES_1`); the question is whether its skirt may be a plant.

### 2. RM_Rimebeard — filament colony on the formations

A beard of soft grey filaments hanging off pillar flanks and dome caps, each strand a
rope of colony-flesh that drinks the brine whole and sweats the salt back out as a rime
of needle crystals along its own length — an osmotic engine wearing its exhaust. The
beard grows heavy, whitens, and sheds: a pillar with fresh rimebeard is silver-grey and
soft; one overdue is white and bristling. The shed needles sift down and feed nothing —
they are the plant's grief, pure mineral — but under the beard the strand-flesh is the
only wet-soft thing in the biome, and the sallik shelter in it. Where the giant has
scraped, the beard regrows first: **a scrape scar with young rimebeard on it is an old
scar** — the diver's second tell, refining the sheet's first.

- **Twist:** *efflorescence* — it survives the salt by wearing it out, not keeping it
  out. (Not the Scald's ablation: nothing melts; this is osmotic waste disposal.)
- **Art:** hanging fringe silhouette against a formation's vertical, ash-grey strands
  tipped white, always asymmetric — heavier on one side (marred); drawSize ~0.9; no glow.
- **Harvest:** the shed rime — `RM_RawSalt` ×2 at low work; the one understorey plant a
  salt-hungry colony strips on purpose.
- **Numbers:** growDays 10, **not in `wildPlants`** — placed by formation-adjacency
  (route B), 2–5 per pillar/dome cluster.

### 3. RM_Mournweft — upright filament net, open sediment

Two snows fall on this floor: salt, and the slow organic rain from the living sea above.
The mournweft is a waist-high loom of grey threads strung between three or four stiff
spines, and it catches both — then tells them apart by touch, kneading what lands with
cilia too small to see, keeping what was alive and shrugging what was mineral off the
downwind side. After a salt-snow weather every weft on the floor is bowed white like a
widow, and over the following days it straightens, pale again, having eaten the food and
buried the salt in a little drift at its own foot. The nissik work those drifts; a
mournweft is a table set twice.

- **Twist:** *tactile sorting* — in a blind biome, the plant that reads by feel. (Not
  the Scald's filtration-hoarding: it keeps nothing mineral; it is a sieve, not a vault.)
- **Art:** small sail/net silhouette on spindle legs, warp visibly hand-loomed and
  slightly torn somewhere (marred); dirty white on grey; bowed variant is description,
  not a second graphic; drawSize ~1.1; no glow.
- **Harvest:** none — its economy is feeding the sessile layer (ecology).
- **Numbers:** growDays 8, commonality 0.5, open floor.

### 4. RM_Milkwell — the sponge equivalent, open sediment, solitary

A knee-high barrel of dense felt, dirty ivory, that does the one thing this sea has
forgotten: it makes the water gentler. A milkwell pumps brine through its body all its
slow life and holds the salt back cell by cell, exhaling water fresh enough that the
outflow shimmers above it like heat-haze — a well running upward, a spring at the bottom
of a sea. The halo is habitat: soft-bodied things that cannot live in the open brine
live in the yard of a milkwell, and an old one sits in a circle of company like a
chapel. It never stops. When it finally fouls and dies it goes to salt in a season,
becoming a white cast of itself — and the statuary gains one more figure that was never
alive in the usual way.

- **Twist:** *osmosis* — the hypersaline sea's own trick, run in reverse, for everyone's
  benefit but its own. (Not the Scald kettlewick's distillation: no heat, no drop, no
  drinkable — the product is a PLACE, not an item.)
- **Art:** squat barrel of layered felt rings, ivory over grey, lip chipped (marred);
  the haze-shimmer is description unless a cheap distortion mote exists; drawSize ~1.2;
  no glow.
- **Harvest:** none. Its yield is the yard (see ecology; and owner question 6).
- **Numbers:** growDays 25, commonality 0.25, open floor, `wildClusterRadius` unset —
  solitary by temperament like everything Grey.

### 5. RM_Hoarstock — the soft coral equivalent, near the statuary

A branching soft coral that ossifies from the base upward at a fixed, terrible pace: the
living tissue is only ever the last hand-span of each branch tip, riding a pedestal of
its own dead centuries, stone-grey below, felt-grey above, the boundary visible as a
waterline of texture. Nothing eats the stone; the otheska graze the boundary line where
the dying tissue softens. A tall hoarstock is old the way pillars are old, and divers
who cannot read pillar-bands read hoarstocks instead: the stone-to-flesh ratio is a
clock. When the last tip turns, the whole plant is furniture — and indistinguishable
from the statuary it always grew beside, which is why the statuary's census is never
finished.

- **Twist:** *self-ossification* — the maalu's half-turned-to-stone register, made
  botanical: it does not resist the mineral fate, it schedules it.
- **Art:** candelabra silhouette, hard-edged grey base grading to soft pale tips, one
  branch always already dead ahead of the others (marred); drawSize 1.3–1.6; no glow.
- **Harvest:** `RM_RawSalt` ×3 at high work (quarrying the dead base kills the plant —
  the yield is real and the price is written on it).
- **Numbers:** growDays 30 — the slowest growing plant we ship anywhere — commonality
  0.3, open floor, biased near statuary by prose (no placement code needed; the
  resemblance does the storytelling wherever it lands).

### 6. RM_Saltswoon — the plant that is sometimes a puddle, hollows in the sediment

Solid is a losing posture in water that wants to jacket everything. The saltswoon's
answer is to stop being solid: for most of its life it is a glossy grey syrup lying in a
hollow — flesh deliquesced by its own enzymes, too concentrated for the brine to
penetrate, too formless for crystal to grip. A few days a season it gathers itself,
raises one soft translucent stalk, seeds, and swoons back into its bowl. The floor's
oldest joke, to the extent the Grey jokes: the pools keep everything, and the saltswoon
is the one thing that keeps itself by imitating them. A diver who steps in one is
startled, unharmed, and faintly insulted.

- **Twist:** *deliquescence* — it survives crystallisation the only way possible: by
  never presenting a surface. (The inverse of the whole crystal seven, on purpose.)
- **Art:** a glossy dark-grey pool with a meniscus, one half-risen stalk on the mature
  graphic; the marring is the bowl's uneven rim; drawSize ~0.9; no glow.
- **Harvest:** none; pathCost trivial. Dressing with a personality.
- **Numbers:** growDays 12, commonality 0.35, open floor hollows.

### 7. RM_Stillbloom — the pool lily; brine-pool surfaces and margins

The pools have surfaces, and the surfaces have flowers. A stillbloom rests on the
density interface itself — root-threads hanging down into brine that kills everything,
bone-white bloom lying open on the skin of it, riding the boundary the way a leaf rides
a pond. It never breaks the surface; the tension of the interface is its whole floor and
its whole trick. It is the biome's warning made beautiful: a white flower seen through
the murk means a pool is there, before the pool's stillness can be read. Divers do not
pick them. Divers cannot pick them — every stillbloom grows exactly out of reach, which
the shore-camps have made into a proverb about everything else down here.

- **Twist:** *density-surfing* — it lives ON the deadliest thing in the biome by
  weighing precisely nothing to it. Ban 1 audit: nothing about it makes a pool
  enterable; it is unreachable by design, harvest is impossible, and its whole function
  is to mark the danger.
- **Art:** flat open bloom, bone-white with a grey heart, petals uneven in count
  (marred); root-threads visible as a smudge under the surface; drawSize ~0.8; no glow.
- **Harvest:** none, structurally (out of reach — see twist).
- **Numbers:** growDays 15; **not in `wildPlants`** — placed on pool-margin cells by the
  dressing worker (route B). 3–6 per pool. ⚠️ Build note: pool terrains are water; the
  placement must verify a plant can stand there or place on the last margin ring —
  design intent is "on the pool's skin", engine compromise is "at its lip".

### 8. RM_Brinecomb — gradient-eater, brine channel beds

The channels are rivers of heavier brine inside the sea, and every boundary between two
waters is a market: ions cross it, minerals precipitate along it, the essarn cruise it.
The brinecomb farms it. A row of grey teeth along the channel bed, each tooth a hollow
blade holding its root-water dense and its tip-water light, eating the exchange between
them — a plant whose food is the DIFFERENCE between two brines, starving anywhere the
water is all one thing. Combs grow in runs down a channel's length like the baleen of
something buried, and where the Glass Veil Kelp curtains hang above the trench, the
combs line the floor of it: the kelp takes the light, the comb takes the gradient,
and neither wants the other's living.

- **Twist:** *gradient-eating* — chemotrophy on the chemocline; the channel terrain's
  reason made flesh.
- **Art:** low run of blunt teeth, slate-grey with pale tips, gaps in the run (marred);
  reads as a contour along the channel like a seam of stitching; drawSize ~0.7; no glow.
- **Harvest:** none — dressing that makes the channels legible from further away
  (follow the stitching downhill and you arrive at what kills you).
- **Numbers:** growDays 9, commonality 1.5 **terrain-gated** — `wildTerrainTags
  RM_GreyBrineChannel`, high weight WITHIN the channel's few hundred cells, absent
  everywhere else (the kelp's own shipped pattern; ⛔ never remove the tag to "make it
  show up").

### 9. RM_Neverset — the sprig that salt cannot take; jacket rings and pool shores

Everything in the Grey ends in crystal except this. The neverset is a small ash-grey
sprig whose sap is packed with proteins that refuse nucleation — brine cannot seed a
crystal on it, in it, or against it; the jacket mineral grows around a neverset and
leaves a sprig-shaped void. So it grows precisely where nothing else dares: in the
jacket rings at the pool shores, among the statuary, in the chimneys' crystallising
plumes' outer reach — the most lethal ground on the floor, carpeted thinly with the one
thing the ground cannot keep. The otheska, which grazes jacket surfaces, ignores it
completely: to everything built for the Grey's chemistry, the neverset barely exists.

- **Twist:** *anticrystallisation* — the counter-thesis plant; the biome's one refusal.
- **Art:** sparse wiry sprig, ash-grey, a few swollen nodes; the marring is that half of
  every sprig looks winter-dead and is not; drawSize ~0.5; no glow.
- **Harvest:** a cut sprig — potentially the Grey's one plant ITEM (owner question 4:
  an anticrystallant with a real use against hull crust and encasement rescue, or pure
  dressing; Ruled 3 of the danger pass — "no fuel-for-time trade" — may already answer
  this in spirit, so nothing is designed onto it here).
- **Numbers:** growDays 14, commonality 0.15 in `wildPlants` (open floor, rare) PLUS
  seeded among the jacket rings by the dressing worker (route B), where it reads best.

### 10. RM_Murkblush — structural colour, everywhere and invisible

In the murk the murkblush is nothing: a low round cushion, grey as everything, beneath
notice. Bring a lamp and it answers — not with light of its own but with the lamp's,
returned through layered plates in its skin as a deep iridescent blush, oil-sheen blues
and greens the Grey otherwise does not contain. The colour is structural: it exists only
while the beam does, costs the plant nothing, and serves it nothing anyone has proven —
the shore-camps' naturalists argue about it the way the two faiths argue about the
Scald. What is certain is the price of looking: a floor of blushing cushions means a
lamp burning, and the sheet's economy says what a burning lamp eventually brings. The
prettiest thing in the biome is a countdown.

- **Twist:** *structural colour* — colour with no emission. Ban 4 audit: it produces no
  light and no glow comp, ever; it is a REFLECTOR, the immu's pink-in-a-lamp grammar
  made flora, and it makes the player complicit in every photon (danger pass §2's own
  principle).
- **Art:** low cushion, matte grey base graphic; the blush is the ART DIRECTION for its
  lit read (a subtle iridescent variant or shader tint under high light), never a
  glower; one bald patch per cushion (marred); drawSize ~0.7.
- **Harvest:** none. Beauty small positive — and only honestly earned when lit.
- **Numbers:** growDays 7, commonality 0.2, open floor everywhere.

## Density and routing

### The density

**Proposed `plantDensity`: 0.14 → 0.22.** The shipped 0.14 was set with seven plants
and a deliberate note: crowded with mineral forms, sparse with living ones. That
sparseness stays the law — the Grey must never read lush — but the understorey adds
seven `wildPlants` rows of small things, and at 0.14 the monuments would simply eat
most of the new layer's budget. 0.22 keeps the floor well under the Scald's proposed
0.30 (correct: the Grey is the stiller sea) and under arid-shrubland feel, while
letting the mats, wefts and cushions actually appear between the crystal forms. It is
the single knob; the roster works unchanged from 0.14 (very sparse) to 0.30. Owner
question 1.

### Route split

**Route A — `wildPlants` (density-driven).** Seven rows added beside the shipped
eight, in the shorthand `<DefName>commonality</DefName>` form (⚠️ never `<li>` —
the custom loader silently discards a wrapped entry):

```
RM_Masonmat 1.0 · RM_Mournweft 0.5 · RM_Saltswoon 0.35 · RM_Hoarstock 0.3 ·
RM_Milkwell 0.25 · RM_Murkblush 0.2 · RM_Neverset 0.15 · RM_Brinecomb 1.5 (terrain-gated)
```

Every def carries the three engine laws the built seven already prove out:
`completelyIgnoreFertility` true, `growMinGlow`/`growOptimalGlow` 0, `cavePlant` false.
Brinecomb alone is terrain-gated (`wildTerrainTags RM_GreyBrineChannel`), high weight
within its few hundred cells, following the kelp's shipped pattern exactly.

**Route B — the dressing worker (adjacency, which `wildPlants` cannot express).**
`GenStep_GreySeaFloorDressing` is BUILT and already knows every anchor this layer needs
(it carves the pool, rings the jacket, finds the chimneys). Extend it — or a small
sibling step at order ~905, after the vanilla Plants step so nothing overwrites it —
with three placements:

- **RM_Rimebeard** — 2–5 on standable cells adjacent to each `RM_SaltPillar` /
  `RM_SaltDome` cluster (the formations are the host; there is no apron terrain to
  lean on, so this is the one genuinely new placement rule).
- **RM_Stillbloom** — 3–6 on the pool-margin ring (`RM_BrinePoolShallow` cells, or the
  last floor ring if plants cannot stand on the water terrain — build note in its
  entry).
- **RM_Neverset** — a thin seeding among the jacket-ring cells the worker already
  places, plus **RM_Masonmat** thickening at pillar feet (both are wildPlants species
  too; route B only biases where they read best).

All of it regenerates fresh each floor visit — nothing here depends on pocket-map
persistence, per the seabed-layer constraint; a mat that re-rolls between dives is
geology-grade dressing.

**Route C — runtime coupling: not used.** No plant here needs live behaviour to ship.
The two candidates are explicitly optional flourishes: mournweft's post-snow bowing and
saltswoon's seasonal stalk are description on a static graphic unless a later pass
wants them, and the murkblush's lit read is art/shader work, not a comp. Zero C# beyond
the route-B placements.

### What changes in `RM_GreySea.xml`, summarized

One field (`plantDensity` 0.14 → 0.22, pending question 1), seven new `wildPlants`
rows (shorthand form) beside the shipped eight — nothing else. New defs live in
`TerminalBiomes/Defs/ThingDefs_Plants/` beside `RM_GreySeaFlora.xml` (suggest
`RM_GreySeaUnderstorey.xml`); route-B placements land in DivingInteraction beside the
dressing worker. No terrain edits, no formation edits, no touch on the crystal seven.

## Ecology — flora and fauna as one system

The fauna descriptions already name their food; this layer gives the food defs, so the
wiring is mostly the shipped cast's own sentences coming true:

- **The sorruth's pasture exists now.** Its description — *"grazes the film off the
  Grey Sea's pillar-mason columns"* — finally points at a def: **masonmat** is that film
  where it skirts the floor, and a sorruth working the edge of a mat is the biome's
  slowest pastoral. (The film ON the columns stays fiction; the def is the skirt.)
- **The essarn's feeding lanes.** The ribbon-swimmer *"cruises the density interface
  above the brine pools"* — which is exactly where the **stillblooms** rest and what the
  **brinecombs** farm in the channels. Essarn over bloom-marked pools and along
  comb-stitched channels: the three density-interface specialists of the Grey, animal,
  flower and comb, sharing one niche at three trophic angles.
- **The otheska's boundary line.** The statuary-grazer that *"leaves the shapes beneath
  untouched"* gains a second table: the **hoarstock's** stone-to-flesh waterline, grazed
  exactly at the softening boundary. And its perfect indifference to **neverset** — the
  one thing on the jacket it cannot use — is the roster's chemistry made visible.
- **The sessile three eat at the wefts and live in the yards.** The layer that *"picks
  through what organic matter rains down"* now has infrastructure: **mournweft** drifts
  are nissik feeding grounds; **milkwell** yards are where thollim beds thicken and
  grusk clusters hang lowest; the sallik shelter under **rimebeard** fringe. Abundance
  stays placement, never grouping — ban 2 untouched.
- **The floor seven get texture.** The oomal's pillar-foot silt is masonmat country; the
  maalu, half turned to stone, drifts over hoarstocks doing the same thing slower; the
  immu's pink-in-a-lamp and the **murkblush's** blush are one grammar — the Grey hides
  its colour and a lamp buys it, at the lamp's standing price.
- **The light economy gains its floor.** Ruled: lit cells yield more, the fessk watches,
  the giant answers. Murkblush makes the first clause visible (a blushing floor says
  which cells the lamp is paying for), rimebeard's regrowth-on-scrape sharpens the
  giant's tell, and stillbloom marks the pools no lamp should be parked beside.
- **The fessk loses nothing.** The undertaker's window — the fresh dead before the
  minerals take them — is untouched: nothing here decays, rots or hastens the jacket.
  Ban 5 stands; the statuary only grows (and milkwell corpses grow it by one).

Nothing in the roster adds a predator, a drinkable, a light source, or a pool entry.
The murk stays blind, the pools stay lethal, the six bans stand.

## Art direction summary table

| plant | silhouette | palette | glow | drawSize |
|---|---|---|---|---|
| RM_Masonmat | flat banded mat, ragged edge | chalk-white on grey | none | 1.0 |
| RM_Rimebeard | hanging fringe on formations | ash-grey, white tips | none | 0.9 |
| RM_Mournweft | upright net on spindle legs | dirty white | none | 1.1 |
| RM_Milkwell | squat felt barrel, chipped lip | ivory over grey | none | 1.2 |
| RM_Hoarstock | candelabra, stone base to felt tips | grey gradient | none | 1.3–1.6 |
| RM_Saltswoon | glossy pool, one soft stalk | dark grey | none | 0.9 |
| RM_Stillbloom | flat open bloom on the pool skin | bone-white, grey heart | none | 0.8 |
| RM_Brinecomb | low run of blunt teeth | slate, pale tips | none | 0.7 |
| RM_Neverset | wiry sprig, swollen nodes | ash-grey | none | 0.5 |
| RM_Murkblush | low cushion, one bald patch | grey; iridescent ONLY under a lamp | none — reflective | 0.7 |

Palette check against sheet §9: every grey, bone-pale, crystal white — held. The
crystal seven keep the floor's only mineral colour; the giant's mark keeps the only
saturation; the murkblush's blush exists only while a player's own lamp does. Marring
rule on every brief, verbatim.

## Questions for the owner

1. **plantDensity 0.14 → 0.22 — accept, or name a different number?** It is the single
   knob; the roster works unchanged from 0.14 (very sparse) to 0.30 (Scald-proposed
   level, which the Grey should probably stay under).
2. **May the murkblush's lamp-only structural colour ship?** It emits nothing — no
   glower, ever — but it is deliberate colour in a biome whose art law is grey, visible
   only under player light. If it reads as a ban-4 violation to you rather than a
   ban-4 tribute, it cuts cleanly (nothing else references it).
3. **May the pillar-mason's floor skirt be a plant def (RM_Masonmat)?** It gives the
   sorruth's shipped description a real pasture, but it makes a piece of the Grey's
   monoculture destructible and player-visible as "a plant". The mason as a whole stays
   def-less fiction either way.
4. **Neverset's cut sprig: a real anticrystallant item, or pure dressing?** A plant that
   crystal cannot take could plausibly slow hull crust or speed encasement rescue — but
   your danger-pass ruling 3 ("no fuel-for-time trade; the counters are chipping and
   leaving") may extend to plant-based counters too. Nothing is designed onto it until
   you rule; the plant works as dressing.
5. **Stillbloom rests ON the brine pools' surface, permanently out of reach — accept?**
   Ban 1 stays whole (nothing enters, nothing harvests, pools stay lethal); it is the
   warning made into a flower. If the engine cannot stand a plant on the pool terrain,
   the fallback is the pool's lip, which loses some of the image.
6. **Milkwell's fresher halo: prose only, or a small mechanic?** The cheap mechanical
   read would be a modest fishing/forage bonus on cells adjacent to a milkwell — a
   natural sibling of your "lit cells yield more" ruling, but one that competes with it
   (a free yield spot that needs no dangerous lamp). Prose-only is the default here.
