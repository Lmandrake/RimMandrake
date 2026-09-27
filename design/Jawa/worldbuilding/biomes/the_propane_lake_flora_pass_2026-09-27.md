# The Chill (ex-Propane Lake) — underwater flora design pass (2026-09-27)

Item: `PROPANELAKE_FLORA_PASS_1`; the build rides `CHILL_FLORA_BUILD_1`. Design prose
only — nothing here is built. **The biome is the Chill** (owner, sitting of 2026-09-27:
*"Let's call it the Chill"*). defNames below are written as they stand today; the RM
tier is being renamed wholesale to `RM_TheChill*` under `CHILL_RENAME_FULL_1`.

## Commission

Owner, by question card 2026-09-26 (the Scald flora pass's ruled question 1): **every sea
floor gets its own strange-flora design pass, each in its own register, nothing shared** —
and he specifically flagged the Chill's register as **not water-chemistry at all**.
This is a cryogenic liquid-propane sea. Whatever grows here is not plant biochemistry as
Earth knows it: solvent chemistry in liquid hydrocarbon, around −80 °C, anoxic, and
flammable the moment it meets air. That inversion is the register; every twist below is
derived from it, and none is shared with the Scald, the Grey Sea or the Twilight Sea.

Sibling pass (shape imitated, content disjoint):
`design/Jawa/worldbuilding/biomes/the_scald_underwater_flora_pass_2026-09-27.md` — whose
ruled section carries the standing lesson: a novelty plant borrowed from another biome's
register ("No, this is silly. No cold.") gets cut. Every twist must belong to THIS
biome's chemistry.

## Sources read

- `design/Jawa/worldbuilding/biomes/the_propane_lakes.md` — the frozen definition sheet
  (Umbra, the aurora and electrojet, fuel snow, the ten hard bans, the war lab, the donor
  crystal flora, the rime nodule).
- `src/RimMandrake/TerminalBiomes/Defs/BiomeDefs/RM_PropaneLake.xml` — the live RM-tier
  BiomeDef: 10-row `wildAnimals` (incl. the six 2026-09-26 floor residents), `fishTypes`,
  `animalDensity` 0.08 (set 2026-09-26 under `PROPANELAKE_ANIMALDENSITY_ZERO_1`), and —
  the gap this pass fills — **no `plantDensity`, no `wildPlants` at all**.
- `src/RimMandrake/TerminalBiomes/Defs/TerrainDefs/RM_PropaneLakeTerrains.xml` —
  `RM_PropaneLakeDeep` (the liquid, impassable) and `RM_SolidPropane` (the standable
  crust); both currently carry only the `Water` terrain tag.
- `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Items/RM_PropaneLakeCatch.xml` — the
  heemin/oovanam catch items; plus the biome def's RUT catch rows (fessu, krellik, oddu,
  oovu, iliss, tarnn, zhiil).
- `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Races/RM_PropaneLakeFloorLife.xml` and
  `RM_PropaneLakeFauna.xml` — the living cast's descriptions (the crystal-plate fessu,
  the frost-plated krellik "picking at the crystal flora's fallen fragments", the sessile
  propane-drawing oddu, the snow-catching oovu, the current-fed iliss, the half-crystal
  tarnn colony; heemin, oovanam, hoolen, vaunoom). The ecology section wires every plant
  to this cast.
- The Scald sibling pass (structure and def-shape conventions: `completelyIgnoreFertility`
  + `wildTerrainTags`, shorthand `wildPlants` rows, route split).

## The register

Water here is a mineral, not a solvent. At −80 °C the lake's working fluid is liquid
propane — nonpolar, anoxic, thin, and cheap — and everything alive in it is built the way
that solvent allows: waxes and oils where water-life uses gels, dissolved tars where
water-life uses pigments, frozen gases where water-life uses membranes of lipid in water.
Four physical facts do all the design work below, and every plant is one of them made
into a survival trick:

1. **Phase inversion.** Substances that are rock on the dayside are workable here, and
   vice versa. Paraffin wax softens and part-dissolves in liquid propane — supple,
   living material at −80°, stone the instant it meets air. Water ice at −80 °C is
   granite-hard and utterly insoluble: the local bedrock mineral. Gases (methane, the
   aurora's own chemistry products) freeze into panes and cages that never melt here —
   they *sublime* if warmed, skipping liquid entirely.
2. **No fire below, only fire above.** Propane cannot burn without an oxidizer, and the
   lake carries essentially none — so the fuel sea is, from inside, the most
   fireproof place on the planet. Everything soaked in it is a torch the moment it
   surfaces. The one native exception is radiolysis: the aurora's particle rain, working
   on trace water ice, manufactures peroxides — tiny hoards of the rarest chemical in
   the biome, the only oxidizer for a thousand kilometres.
3. **The only energy is the sky and the snow.** No sun, ever. Income is the aurora's
   light and charge (the same electrojet the iliss feeds on) and the nightly fuel snow
   carrying tholins and heavier hydrocarbons down onto the floor. Everything eats one of
   those two flows or eats something that does.
4. **Stillness is structure.** Nothing stirs this sea but the vaunoom and the pumps. In
   a solvent this cold and this quiet, dissolved things stay dissolved for centuries and
   crystals grow undisturbed for longer. Slowness is not a hardship here; it is a
   building material.

What this register bans by itself: nothing photosynthesizes green, nothing has sap,
leaves, cellulose or chlorophyll analogues, nothing needs liquid water, and nothing would
survive five minutes in any other sea — the Scald would boil it, the Grey would dissolve
its wax, and air alone sets half this roster on fire or into stone.

## The roster

Ten flora. The organizing law, inherited from the Scald pass and re-derived from this
biome's own chemistry: **each plant's way of being alive in liquid propane IS its alien
twist, and no two twists repeat.** Named up front so distinctness is checkable:
*phase inversion* (living wax that stones in air), *sublimation* (membranes of frozen gas
that vanish rather than melt), *patience* (crystal growth on a scale of centuries),
*fractionation* (a living chromatogram sorting the fuel), *inversion of down* (rooted in
the ceiling), *water-as-mineral* (a skeleton of ice, the local granite), *hoarded fire*
(radiolytic peroxide — the only oxidizer in the biome), *resonance* (feeding on the
aurora's specific lines), *solution-phase life* (a plant that is dissolved, and only
sometimes a thing), and *condensation* (ripening the snow's heavy tars into beads).
None overlaps the Scald's ten tricks, and nothing here could live one day in hot water.

All names are invented and franchise-free (`RM_` tier, per Q11a). All ten defNames
collision-checked against `src/` and `design/` (recursive grep, 2026-09-27): every one
FREE.

### 1. RM_Slackwax — wax kelp, shallow floor

The lake's pasture and its founding joke: a kelp whose flesh is paraffin — rock on any
dayside shelf, but down here, part-dissolved in the cold fuel, as supple as anything that
ever waved in a sea. Slackwax stands in slow ribbons off the shallow floor, growing by
pulling wax-weight hydrocarbons out of solution and losing it again wherever the fuel
runs momentarily warmer, so a bed of it records every current that ever passed as a
thickening or a thinning. Hauled into air it does not die so much as *set*: rigid in
seconds, stone-hard in a minute, holding whatever curve it drowned in. The scrapers'
shacks along the crust are furnished with it — chairs, hafts, window-lattices — all of
it furniture that was briefly an organism, and all of it burning like a torch if anyone
is fool enough to bring it near flame.

- **Twist:** phase inversion — alive as a liquid-phase wax; its corpse is a building
  material shaped by its life.
- **Art:** broad slow ribbons, ivory-amber, faint internal cloudiness like candle wax
  held to light; drawSize 1.2–1.5; no glow.
- **Harvest:** cut wax, usable as a WoodLog-register material (the biome's only
  "timber") — and the offcuts render as **hydrocarbon flesh** at the harvest bench,
  the first rung of the ruled fuel chain (see the fuel-chain section).
- **Numbers:** growDays 10, commonality 0.9 — the common carpet-layer.

### 2. RM_Ghostpane — frozen-gas membrane, shallow floor and crust edge

A colony that builds in a material no dayside chemistry can keep: panes of frozen gas —
methane and the aurora's lighter manufacture, laid down molecule by molecule into sheets
a hand wide and a hair thick, joined at angles like a shattered window reassembled by
something that never saw the original. The panes are its leaves, its ribs and its whole
estate. Warmed even slightly they do not melt; they *sublime*, the pane un-existing
edge-inward with a hiss and a shiver of fumes, which is why a ghostpane stand near a
grounded ship's pipe run simply erases itself over an hour, and why no one has ever
brought one anywhere. The hoolen lick the crust-edge panes for the frost that condenses
on them, and the panes grow back by morning.

- **Twist:** sublimation — membranes of frozen gas; it can vanish but it cannot wilt.
- **Art:** clusters of thin translucent panes at broken angles, near-invisible except
  where aurora light catches an edge in green or violet; drawSize 0.9; no glow of its
  own — it is made of edges for other light.
- **Harvest:** none possible, structurally — anything warm enough to hold it is warm
  enough to erase it. Beauty small positive.
- **Numbers:** growDays 3 (panes re-lay fast; the material is cheap where cold is
  free), commonality 0.7.

### 3. RM_Eldspar — slow crystal garden, deep floor

Ashore, the donor crystal flora regrows overnight from the fuel snow — a cheap trick in
a place where the snow is food. The eldspar is the opposite proposition: a crystal garden
on the deep floor that grows *a finger's width in a decade*, in the one place on the
planet still enough to permit it. Each spar is optically perfect, grown molecule by
molecule from the stillest solution in the world, and a mature garden — chest-high,
centuries deep — is the oldest living structure anyone on Ash'karr can visit. The
krellik pick at its base for the microscopic spall its growing edges shed (the "fallen
fragments of crystal flora" the shore-folk already know them for), and the tarnn colonies
grow in and among the gardens so thoroughly that nobody has settled which lattices are
eldspar and which are tarnn — the lake floor's standing dispute about where its flora
ends and its fauna begins.

- **Twist:** patience — stillness as a building material; growth on a timescale that
  makes it the floor's monument rather than its vegetation.
- **Art:** upright clustered prisms, glass-clear with a smoke-grey heart, aurora
  refracting through the tips; drawSize 1.4 at max growth; faint refracted glint, no
  emitted glow.
- **Harvest:** destroying one yields a single flawless spar (a high-Beauty keepsake
  item, market value modest) — and its smoke-grey heart yields **AuroraGlass**: the
  planet's prettiest treasure lives inside the oldest living thing. (By card, sitting
  of 2026-09-27: AuroraGlass moves into the garden — it comes OFF the RM-tier
  rare-catch fishing table, and it also appears as a rare vein find on the war-lab
  drill shafts, item `CHILL_WARLAB_ROUTES_1`.) The description should say plainly what
  the harvest costs: the regrow is measured in lifetimes.
- **Numbers:** growDays 60 — RULED (the owner declined never-regrows; the regrowing
  stand-in for "decades" stands) — commonality 0.25, deep floor only.

### 4. RM_Tarspool — living chromatogram, deep floor

The nightly fuel snow carries down everything the aurora manufactures — tholins, tars,
the heavy ends of a sky-wide refinery — and the tarspool farms the fall by *sorting* it.
A squat spindle wound in pale absorbent floss, it wicks the settled slush up its length,
and the mixture separates as it climbs: heavy black tars barely leave the base, ambers
ride to mid-height, and the lightest violet organics reach the crown, so every tarspool
wears its diet as bands of colour in strict molecular order — a chromatography column
that is also an organism, reading the sky's chemistry and publishing the result. Scrapers
read tarspool bands the way farmers read clouds: a broad violet crown means the
reconnection storms have been rich, and the oddu-fishing will be good.

- **Twist:** fractionation — it does not eat the snow, it *resolves* it, and wears the
  analysis.
- **Art:** squat banded spindle, black base through amber to violet crown — the banding
  IS the mechanism made visible; drawSize 1.0; no glow.
- **Harvest:** scraping the crown yields the rime-nodule euphoric's raw material —
  **the same item**, ruled (Q4, by question card, sitting of 2026-09-27): the violet
  fraction IS the compound the nodule sacs hold, and the floor is wired into the
  economy the nodule already established ashore. The heavy black tars at the base —
  the fraction the spool itself never spends — render as **hydrocarbon flesh** at the
  harvest bench (see the fuel-chain section).
- **Numbers:** growDays 8, commonality 0.6, deep floor where the snow settles.

### 5. RM_Keelgrass — ceiling-rooted fringe, shallow floor under the crust edge

Down is negotiable in a sea lighter than everything that falls into it. The keelgrass
roots in the *underside of the frozen crust* and grows downward into the black, long
blades hanging keel-wise into the liquid, combing the top layer where the heemin swim.
It is the lake's only canopy, and it grows from the sky of its own world: anchored in
solid propane, fed by the frost that migrates through the crust, tips reaching toward
the floor it will never touch. Heemin shoal into keelgrass fringes when a vaunoom's wake
crosses the mirror above — the one shelter in the top layer — and the crews who lower
ships through the crust learn to cut their entry hole clear of the fringes, because a
curtain of keelgrass across a descending hull reads, for one bad moment, exactly like
something reaching up.

- **Twist:** inversion of down — rooted in the ceiling; the crust is its ground and the
  floor is its sky.
- **Art:** long trailing blades hanging from above the frame's top edge where terrain
  adjacency allows, else tall and current-bent; deep grey-green-black, edges catching
  aurora light; drawSize 1.3; no glow. (Mechanically it stands on shallow cells at the
  crust boundary — the ceiling-rooting is description and art, not a render mechanism.)
- **Harvest:** none — it is shelter and hazard-dressing, the top layer's furniture.
- **Numbers:** growDays 7, commonality 0.6, shallow floor adjacent to crust.

### 6. RM_Stonewater — ice-boned brake, deep floor

In this register water is not the medium of life; it is the hardest mineral the biome
owns. The stonewater brake mines it — scavenging the trace ice that arrives in the snow
and the dust, molecule by molecule, and building it into a skeleton: white branching
bones of pure water ice, granite-hard at −80°, dressed in a thin living felt of wax
chemistry that does the actual living. It is the inversion that names the biome's whole
chemistry, standing in plain sight: a plant whose *stone is water*, in a sea whose
*water is fuel*. Old brakes are the deep floor's reefs — the iliss thread their bones,
and what the frost-plated krellik cannot crack, it leaves alone.

- **Twist:** water-as-mineral — its skeleton is ice because ice is the local granite.
- **Art:** white coral-like branching bone under a dark oily felt, unmistakably skeletal;
  drawSize 1.2–1.5; no glow — the whitest thing on a black floor.
- **Harvest:** chipping a brake yields its bones — water ice, a real harvest item and
  a generic cooking and hydration input, the only water source on the lake floor.
  RULED (Q3, owner typed: *"Cooking + real water source w/ power"*): a powered
  extractor placed on a brake is also a genuine water source — melting the local
  granite costs watts, so even drinking here feeds the thermal economy. Never fuel.
- **Numbers:** growDays 20, commonality 0.4, deep floor.

### 7. RM_Fuselight — peroxide lamp, deep floor

The only fire in the fireproof sea, and it grows on a stalk. The aurora's particle rain,
working for centuries on the floor's trace ice, manufactures peroxides — the rarest
substance in the biome, the only oxidizer for a thousand kilometres — and the fuselight
hoards them: a dark stalk crowned with a row of small sealed ampoules, each holding a
bead of oxidizer beside a bead of fuel, and a membrane between them that the plant opens
*on purpose*, one flash at a time. The flashes are its voice — signalling across the
black to its own kind in the one wavelength nothing else down here can fake — and its
defence, and the reason the floor is not wholly dark between auroras. Every scraper is
told the same thing in the same words before their first dive: the pretty one is a
grenade. A fuselight brought up soaked in propane, warming, its ampoules unclenching in
air, is a device; no one who harvests one does it twice.

- **Twist:** hoarded fire — it farms the aurora's radiolysis for oxidizer and spends it
  in controlled cold flashes; the sea's one native ignition, kept underwater where
  ignition cannot spread (hard ban 4 untouched: its flash is a chemical source inside
  sealed ampoules, never a fiat ignition of the lake).
- **Art:** dark slender stalk, crown of 5–7 pale ampoules, one picked out mid-flash in
  actinic blue-white; drawSize 1.0; a real but tiny glow (radius 2, the floor's only
  light between auroras).
- **Harvest:** technically yes, lethally priced. No yield worth a def; attempting it
  should read as a mistake, not an economy. RULED (Q5, sitting of 2026-09-27): the
  explosion is **real** — small radius, one comp — not reputation. Fire is otherwise
  totally banned on the Chill floor (no oxygen — owner physics ruling); the fuselight's
  peroxide is self-oxidizing, which makes it the only thing at the bottom of the world
  that truly burns.
- **Numbers:** growDays 15, commonality 0.3, deep floor, biased toward where the
  currents cross (the iliss's own ground — see ecology).

### 8. RM_Skyharp — aurora-resonance filaments, shallow floor

No sun has ever reached this floor and none ever will; the only light income is the
aurora, and the skyharp is strung for it. A fan of vertical filaments rises off the
shallow floor like the instrument it is named for, each string a different length and a
different chemistry, each tuned — genuinely, physically tuned — to one of the aurora's
emission lines: the long strings drink the green, the short ones the violet, and a
skyharp under a full reconnection storm lights up string by string as the sky runs
through its registers. It is photosynthesis rebuilt for a black sky by way of an
antenna array, and it is the base of the floor's whole energy economy: what the harp
fixes, the snow does not have to carry.

- **Twist:** resonance — it feeds on specific lines of the aurora's light; an antenna
  farm pretending to be a plant.
- **Art:** upright fan of fine filaments, graded heights, each faintly fluorescing green
  through violet along the fan — the gradient IS the tuning; drawSize 1.2; glow none
  (its light is re-emission, description-level, not a light source).
- **Harvest:** none — pasture-layer. Beauty moderate positive.
- **Numbers:** growDays 6, commonality 0.8 — the shallow floor's co-dominant beside
  slackwax.

### 9. RM_Stillbloom — solution-phase flower, deep floor

Mostly, a stillbloom is not a thing; it is a region. Its whole chemistry rides dissolved
in the fuel — a plant-sized volume of the lake that is *organized* without being solid,
held together by nothing but cold and perfect stillness — and only where the sea is
coldest and quietest does it precipitate: over hours, a pale flower crystallizing out of
clear liquid, petal by petal, out of nothing at all. Any disturbance — a wake, a step, a
pump's thrum through the floor, the touch of a curious hand — and it un-happens,
redissolving in seconds, leaving liquid indistinguishable from any other. It cannot be
harvested, collected, carried or kept; it can only be *found blooming*, which the
scrapers say is the lake deciding whether you were quiet enough to deserve it. The
stillest hollows of the deep floor, on the stillest nights, bloom by the dozen.

And heat, which un-happens most of this biome, makes stillbloom happen: **warm bloom,
both edges** (ruled by card, sitting of 2026-09-27). Around a heat plume the stillbloom
and its kin flower in the plume's *outer ring* — warmth driving the dissolved chemistry
out of solution faster than stillness ever could — while the innermost cells boil bare,
too hot for anything to hold together. A parked ship therefore wears a halo of bloom
around a ring of harm: the prettiest thing a crew will see down here is the ring their
own engines painted, and the bare scald inside it is the same signature.

- **Twist:** solution-phase life — dissolved as its default state; solidity is a mood
  the sea has to be calm enough to permit.
- **Art:** a pale many-petaled bloom, half-transparent, clearly mid-precipitation —
  edges resolving, centre already glassy; drawSize 0.8; no glow.
- **Harvest:** none, *constitutively* — the un-harvestable plant (see next section).
  High Beauty; the reward for finding one is having seen it.
- **Numbers:** growDays 2 (precipitation is fast once permitted), commonality 0.35,
  deep floor.

### 10. RM_Pitchpearl — tar-fruit shrub, shallow and deep floor

The snow's heaviest fractions — the black tars even the tarspool leaves at its base —
have one farmer. The pitchpearl is a low, wiry shrub that gathers them and ripens them:
rolling the tar slowly around a grit of ice the way an oyster coats an irritant, laying
it up in glossy black beads that hang off its branches in clusters, each pearl a
season's worth of the sky's darkest manufacture, smoothed and sealed. The beads are the
floor's staple forage — the krellik crack them, the oovanam dredge the fallen ones out
of the dust, and half of what a dredge-line hauls up in the catch came fattened on
pitchpearl windfall. To a colony they are a modest, oily animal feed — until the colony
owns a refinery, at which point the same sealed black beads are also the tidiest
package of hydrocarbon flesh on the floor.

- **Twist:** condensation — it ripens the snowfall's dregs into the floor's one fruit.
- **Art:** low dark wiry shrub hung with clusters of glossy black beads catching aurora
  light in points; drawSize 0.9; no glow.
- **Harvest:** pitch pearls — a low-nutrition raw food eaten mainly by animals (kibble
  input register) — and the beads render as **hydrocarbon flesh** at the harvest
  bench: sealed, portable, exactly what the refinery chain wants (see the fuel-chain
  section).
- **Numbers:** growDays 9, commonality 0.7, shallow and deep floor both — the roster's
  one two-terrain plant, because the fall it farms lands everywhere.

## The fuel chain — hydrocarbon flesh, and the refinery that gates it

Ruled at the sitting of 2026-09-27, owner verbatim: *"it's ok to harvest them for fuel.
This is very late gme"* — and, on the shape: *"Just have it result at the harvest bench
(hydrocarbon flesh) that can then be converted at the refinery."*

So the lake's fatty flora feed one chain, in two steps. Harvesting the fat-bearing
plants yields a single raw item, **hydrocarbon flesh** — the wax, tar and pitch of the
floor's living chemistry, cut and stacked, inert on its own — and a **refinery**
converts hydrocarbon flesh to chemfuel. The gate is the refinery itself and its
research: this is very-late-game economy, reached only by a colony that already flies a
gravship to the floor and back, and until that bench exists the flesh is just the
strangest meat in the larder. The pipes remain the campaign's founding fuel story; the
flora are its endgame supplement, priced in ship time, harvest work and refinery watts.

Who feeds the chain, in character:

- **Slackwax** — the timber stays the point: the wax is worth more set than burned,
  and the WoodLog-register material is the harvest. The offcuts and trimmings render
  as hydrocarbon flesh; a slackwax bed is furniture first and fuel from its scraps.
- **Tarspool** — the violet crown scrape stays the euphoric (the rime-nodule item,
  Q4). The heavy black tars at the base — the fraction the spool sorts and never
  spends — are the purest hydrocarbon flesh on the floor.
- **Pitchpearl** — the beads are dual-register: low-grade animal forage in the pen,
  hydrocarbon flesh at the bench. A shrub that ripens the snowfall's dregs into sealed
  black beads was always going to be the fuel farmer's crop.

And what still yields nothing, by mechanism rather than by rule: **ghostpane** cannot
be harvested at all (the harvesting temperature is the destroying temperature),
**stillbloom** dissolves at the touch (some of what grows here is not for you),
**keelgrass** and **skyharp** are shelter and pasture, **eldspar** pays in one spar and
its AuroraGlass heart, **stonewater** pays in water and only water, and **fuselight**
pays in a small real explosion (Q5). The chain runs on the fat plants alone.

## plantDensity and the unset-field trap — the exact fields the build must set

🔴 **The same trap that killed the fauna applies verbatim to this pass.**
`PROPANELAKE_ANIMALDENSITY_ZERO_1` (FOUNDRY's) exists because `animalDensity` was left
unset, defaulted to `0f`, and a six-animal roster was dead content that could never
spawn. `plantDensity` defaults the same way, and `wildPlants` rows without it are the
same dead letter. This pass therefore states its numbers and names every field:

**In `src/RimMandrake/TerminalBiomes/Defs/BiomeDefs/RM_PropaneLake.xml`:**

1. `<plantDensity>0.18</plantDensity>` — explicit, never omitted, and **RULED** (Q1,
   accepted at the earlier sitting of 2026-09-27). Calibration: vanilla desert 0.05,
   arid shrubland ~0.17, the Scald pass proposes 0.30. The Chill is the sparsest of
   the four seas by ruling-in-effect (`animalDensity` 0.08 was chosen "a hair below
   the Grey Sea's 0.1... matching the fiction"); 0.18 keeps the same relative
   position — alive, unmistakably, but a floor whose register is stillness and black
   mirror, not meadow. The single knob if the first live look reads wrong.
2. The `<wildPlants>` block — **shorthand form, `<DefName>commonality</DefName>`, never
   `<li>` wrappers** (the same custom-loader trap as `wildAnimals`; an `<li>` here
   silently discards the row):
   - `RM_Slackwax` 0.9, `RM_Skyharp` 0.8, `RM_Ghostpane` 0.7, `RM_Pitchpearl` 0.7,
     `RM_Keelgrass` 0.6, `RM_Tarspool` 0.6, `RM_Stonewater` 0.4, `RM_Stillbloom` 0.35,
     `RM_Fuselight` 0.3, `RM_Eldspar` 0.25.
3. Note `hasVirtualPlants` is already `false` on this def and stays false — these are
   real defs, not virtual-plant colour.

**Terrain tags (the plants' `wildTerrainTags` need something to match — today every
relevant terrain carries only `Water`/`dbh_water`):**

4. In `src/RimMandrake/FlowWorks/Defs/LiquidTypes/TerrainDefs/RM_Propane.xml` — the
   dive-layer terrains the gravship floor map actually uses (they are what
   `RM_PropaneLake.xml`'s `RM_SeaShoreExtension` names as `deepTerrain`/
   `shallowTerrain`): add `<li>RM_PropaneLakeBed</li>` to `RM_PropaneDeep`'s `<tags>`
   and `<li>RM_PropaneLakeShelf</li>` to `RM_PropaneShallow`'s `<tags>`.
   - Deep-floor flora (`RM_Eldspar`, `RM_Tarspool`, `RM_Stonewater`, `RM_Fuselight`,
     `RM_Stillbloom`) tag `RM_PropaneLakeBed`.
   - Shallow flora (`RM_Slackwax`, `RM_Skyharp`, `RM_Ghostpane`, `RM_Keelgrass`) tag
     `RM_PropaneLakeShelf`.
   - `RM_Pitchpearl` tags both.
5. Every plant def follows the established water-flora shape
   (`RM_Crowncarpet`/Scald convention): `completelyIgnoreFertility` true +
   `wildTerrainTags` — fertility on these cells is not a number the engine will read.

**The twin, for Phase B (not this build's scope, but stated so nobody rediscovers it):**

6. `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_PropaneLake.xml` — MEASURED
   2026-09-27 (grep, this pass): the frozen twin still has **no `animalDensity` and no
   `plantDensity` line at all.** Its animalDensity is `PROPANELAKE_ANIMALDENSITY_ZERO_1`'s
   business; whoever executes Phase B must carry BOTH density fields and the
   `wildPlants` block across, or the twin ships the same dead-content defect twice over.

**No GenStep route needed.** The Scald needed one for vent-adjacency; nothing in this
roster places by adjacency to a building. Keelgrass's crust-edge bias and fuselight's
current-crossing bias are description and (at most) commonality tuning, not placement
law — Route A (`wildPlants`) carries the whole roster, which also satisfies the seabed
constraint below with no machinery at all.

**Seabed-layer constraint (owner ruling, honoured):** ship-only access; the seabed
planet layer is coming; nothing here depends on pocket-map persistence. Every plant
regenerates fresh from `wildPlants` on any floor-map generation and loses nothing by
being forgotten — including the eldspar: a centuries-old garden that re-rolls between
dives is the same geology-grade dressing the Scald's glass forest was ruled to be
(that re-roll acceptance is cited as precedent, not re-asked). The stillbloom's
appear/dissolve life is description on an ordinary short-growDays plant, not a live
simulation.

## Ecology — flora and fauna as one system

The fauna were authored first (2026-09-26) and several of them already reach toward
flora that did not exist yet. This roster closes those loops rather than inventing new
ones:

- **The energy base.** Two income streams, two pastures: the **skyharp** fixes the
  aurora's light on the shallows, the **tarspool** and **pitchpearl** farm the nightly
  snowfall on the deep floor. Everything else eats one of those flows or eats something
  that does — the floor's economy now has a bottom rung.
- **The krellik's grocery, named at last.** Its def already says it walks the floor
  *"picking at the crystal flora's fallen fragments."* Those fragments now exist: the
  microscopic spall an **eldspar**'s growing edges shed, and cracked **pitchpearl**
  windfall. The krellik's own nightly-regrown crystal plates are built from eldspar
  spall — the garden is the crab's quarry.
- **The tarnn dispute, sharpened — and RULED unsettled** (Q7, sitting of 2026-09-27).
  The tarnn is "a colony, not a creature — or a creature that grew like a colony," and
  it grows in and among the **eldspar** gardens. Which lattices are garden and which
  are animal is the lake floor's standing argument, and the two defs' disagreement is
  **canon, kept on purpose** — flora def and fauna def, side by side, contradicting
  each other. That is the biome's joke about its own admission test. **Do not fix it**:
  no future consistency pass, census or review sheet reconciles these two descriptions.
- **The snow column feeds in order.** The **oovu** bells catch the fall at the surface;
  what they miss, the **fessu** grow their plates from mid-water; what reaches the floor,
  the **tarspool** resolves and the **pitchpearl** ripens; what even they leave, the
  **oovanam** sifts out of the tholin dust. Four trophic stations on one snowflake's
  fall — the description registers already agree on this; the flora complete the column.
- **The current-line pair.** The **iliss** lives where the electrojet's ground currents
  cross the bed, feeding "on the charge, or on what the charge kills." The **fuselight**
  concentrates in the same crossings — radiolysis is richest where the sky's charge
  works hardest — and its flashes stun and kill the small things it seals against, so
  the iliss patrols the fuselight stands as its scavenging round. The floor's only
  light and the floor's only shock, same address, for the same reason.
- **The shelter layer.** **Keelgrass** fringes under the crust edge are where the
  heemin shoal when a vaunoom's wake crosses the mirror — the top layer's one refuge,
  which also puts the heemin catch where the crews already work. **Slackwax** beds
  shelter the sessile **oddu** (a shell-thing drawing propane into its jelly sac, now
  sitting in a wax kelp bed like an oyster in eelgrass), and the **hoolen** licks
  condensed frost off the crust-edge **ghostpanes** — its existing "licks fuel frost
  off the crust" line, given a plant to point at.
- **The catch, fattened.** The dredge economy (fessu, krellik, oddu, oovu, iliss,
  tarnn, zhiil, heemin, oovanam) now has a food web under it: pitchpearl windfall
  fattens the krellik and oovanam the dredge-lines haul; skyharp pasture underwrites
  the heemin shoals. A fishery with a floor under it instead of a roster suspended in
  nothing.
- **The stillbloom stands alone**, wired to nothing living — deliberately. In an
  ecology where every other plant is a rung, the lake keeps one thing that is only
  itself. Its one wire runs to the visitors: a parked ship's heat plume blooms the
  outer ring and boils the inner one bare, so the colony's own presence is written on
  the floor as a halo of flowers around a ring of harm.

Nothing in the roster adds a predator, ignites anything (hard ban 4 audited: the
fuselight's flash — and its ruled small real explosion in air — is a contained
chemical mechanism inside sealed ampoules, its own hoarded oxidizer, never a fiat
ignition of the lake; fire remains impossible everywhere else on the floor, because
nothing else down here has oxygen), darkens the sky (ban 3), carries kyber (ban 2), or
is an icy dayside analog (ban 1 — every twist is solvent chemistry no dayside plant
shares). The fuel chain touches the fuel economy on the owner's own ruling and on his
terms: hydrocarbon flesh, refinery-gated, very late game.
Nothing survives transport dayside in spirit (R-H10): slackwax sets, ghostpane
sublimes, stillbloom dissolves, fuselight detonates — the roster enforces
untransportability by chemistry.

## Art direction summary table

| plant | silhouette | palette | glow | drawSize |
|---|---|---|---|---|
| RM_Slackwax | slow broad ribbons | ivory-amber, waxen cloudiness | none | 1.2–1.5 |
| RM_Ghostpane | thin panes at broken angles | near-invisible, aurora edge-glints | none | 0.9 |
| RM_Eldspar | upright clustered prisms | glass-clear, smoke-grey heart | refracted glint only | 1.4 |
| RM_Tarspool | squat banded spindle | black→amber→violet bands | none | 1.0 |
| RM_Keelgrass | hanging/current-bent blades | grey-green-black, lit edges | none | 1.3 |
| RM_Stonewater | white branching bone under dark felt | bone-white + oil-dark | none | 1.2–1.5 |
| RM_Fuselight | dark stalk, ampoule crown | charcoal + pale ampoules, one blue-white flash | radius 2, the floor's only light | 1.0 |
| RM_Skyharp | vertical filament fan, graded heights | green→violet gradient | none (re-emission is art, not light) | 1.2 |
| RM_Stillbloom | half-precipitated flower | pale, semi-transparent | none | 0.8 |
| RM_Pitchpearl | low wiry shrub, bead clusters | matte black, glossy black beads | none | 0.9 |

Palette check against the sheet's §9 (black mirror, aurora green/violet, crystal-clear,
frost-white, running-flame blue): the flora add wax-ivory, band-amber, bone-white and
glossy black, and the only new light source is the fuselight's flash — one tiny actinic
blue-white point, which is the Burners' flame-blue register deliberately quoted at
candle scale. Nothing competes with the aurora, which stays the biome's protagonist.

**The floor's light is layered** (ruled by card, sitting of 2026-09-27): a **drowned
aurora** above — dim shifting curtains falling through the clear liquid, rising and
dying with the aurora weather overhead, so the whole floor breathes with the sky it
cannot see — over the **constant bioluminescent points** below: the fuselight's tiny
glow and the ghostpane's aurora-caught edges, fixed stars under a moving sky. That is
the register every render answers to, in the owner's own words: the bottom of the
world is *"eerily beautiful, alien and strange and mildly wonderful"* —
*"delicate, entrancing, precious"* — *"totally unlike the dayside."*

## Rulings (sittings of 2026-09-27)

All seven questions this pass raised are ruled, plus four rulings the pass did not ask
for. The build rides `CHILL_FLORA_BUILD_1`.

1. **plantDensity 0.18 — ACCEPTED** (earlier sitting, decision taken by question card).
2. **The no-chemfuel hard law — REVERSED.** Owner typed, verbatim: *"it's ok to
   harvest them for fuel. This is very late gme"* and, on shape: *"Just have it result
   at the harvest bench (hydrocarbon flesh) that can then be converted at the
   refinery."* The fuel-chain section above is the ruled design.
3. **Stonewater — RULED.** Owner typed: *"Cooking + real water source w/ power"*. The
   ice is a real harvest item (generic cooking/hydration input) and a powered
   extractor on a brake is a genuine water source; melting costs watts. Never fuel.
4. **Tarspool crown scrape — RULED same-item** as the rime-nodule euphoric (earlier
   sitting, decision taken by question card).
5. **Fuselight — RULED real explosion**, small radius, one comp — and fire is
   otherwise totally banned on the Chill floor (no oxygen — owner physics ruling); the
   fuselight's self-oxidizing peroxide is the only true fire at the bottom of the world.
6. **Eldspar — RULED growDays 60** (the regrowing stand-in; never-regrows declined).
7. **Tarnn/eldspar boundary — RULED kept unsettled on purpose.** The two defs'
   disagreement is canon; do not fix it.

And from the same sittings:

- **The biome is renamed the Chill** (owner typed: *"Let's call it the Chill"*); the
  RM tier renames wholesale to `RM_TheChill*` under `CHILL_RENAME_FULL_1`.
- **AuroraGlass moves into the garden** (decision taken by question card): eldspar
  hearts yield it, it comes off the RM-tier rare-catch fishing table, and it appears
  as a rare vein find on the war-lab drill shafts (`CHILL_WARLAB_ROUTES_1`).
- **Warm bloom, both edges** (decision taken by question card): stillbloom and kin
  flower in a heat plume's outer ring while the innermost cells boil bare.
- **Layered floor light** (decision taken by question card): drowned aurora curtains
  over constant bioluminescent points — the art-direction paragraph above carries the
  owner's typed aesthetic brief verbatim.
