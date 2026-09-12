# The Poison Forest — biome definition sheet

> 🧊 **FROZEN — `BIOME_FREEZE_FABLE_REVIEW_1`, 2026-09-07.** The rulings in this
> sheet are frozen: **amendments add detail; they never change a ruling.** The
> unfreeze path is an owner ruling at a sitting, recorded on the item that
> changes it; contradiction cards from the freeze review amend under this rule.


_Second pass, 2026-09-05, weaving the owner's refinements: terminator not deep
nightside · scattered twilight · chemical vents, **no volcanism or geysers, no heat
source at all** (R13) · photosynthesis possible but dominated · water non-potable ·
meat toxic but prized. Repass 2026-09-11 (`POISON_FOREST_REPASS_1`): §0 measurements,
§4b weather, R13's chemical venting written through._

**The original diagnosis stands:** it had no driving force. "Poison" was a label,
not a mechanism, so its trees defaulted to tree-shaped. Now it has three axes —
a twilight energy budget, a dead-stable temperature, and a chemical anomaly — and
everything else is forced.

## 0. The measurements everything rests on

Instruments named per line; MEASURED means read from the named instrument, this pass
(2026-09-11) unless dated.

- **Tiles: 546** (`world/ASHKARR_WORLDMAP_tiles.csv`, `biome == PoisonForest`).
  ⚠️ Instruments disagree: the live V26 census read **557** (owner accepted
  2026-09-08); `infrastructure/state/canon.yml` `biome_tile_counts` still carries
  **604** (2026-08 census). Carded; the CSV figure is quoted below because it is the
  instrument this block was measured from.
- **Arc envelope 56–114**, core p10/p90 **82–106**, median **91.3** (CSV). The tails
  stand ruled in-character (owner, 2026-09-08): ~15 tiles dayside of 75, ~75 tiles
  out past 105 toward 114.
- **Temperature: median +11.4 °C**, p10/p90 **−4.8 / +19.1 °C**, extremes −10.0 and
  +41.3 °C (CSV `temp_c`). Canon: the ruled curve puts **+14 °C at θ90**, realised
  median +13.0 °C after the altitude lapse (`canon.yml` `temp_curve_c`). The biome
  reads a shade colder than θ90 because its median tile sits nightside of the line.
- **Elevation: median 58 m**, p90 685 m, max 963 m (CSV) — low ground; the seam's
  condensation belt, not its peaks.
- **Rain: median 0 mm, max 16 mm** (CSV `rain_mm`) — R-H1/R-H2b realised: water
  arrives as condensation, never as rain.
- **Water tiles 0, river tiles 0** (CSV) — the non-potable rule has nothing to fight.
- **Hilliness:** flat 311 · small hills 190 · large 33 · mountainous 12 (CSV).
- **Spread:** 11 of 12 bearing sectors; largest region shares Dew Belt 69,
  Grinding Floor 67, Twilight Sea 56, Slough 55, Sunreach 49 (CSV `region`).
- **Def: `PoisonForest`** (Advanced Biomes (Continued), `mlie.advancedbiomes`) — cast
  onto our tiles via `BiomeCast_Ashkarr.xml`; no own def
  (`_def_bindings_2026-09-09.md`). Its one explicit weather record is
  `PoisonForestSpores` × 18 (`defs.sqlite`, DefDump capture 2026-09-11) — see §4b.
- **UNMEASURED:** vent placement/density on-map (a map-time question, no instrument
  yet); growing-season behaviour under the stunting exemption (R-H2b).

## 1. What it is

A low, wet-black forest standing in permanent dusk over ground that breathes.

The light never changes and never comes from anywhere. The star sits on the
horizon and its light arrives only as scatter, so the forest is lit like the inside
of an overcast dawn that will not resolve — dim, even, faintly brighter toward the
starward side, and casting nothing you could call a shadow. Your eyes never adapt
because there is nothing to adapt *to*.

The trunks are pale and slick and weep a grey metallic sweat that hardens into
scabs and crystal fans, so an old trunk is part tree, part slag heap. There is no
canopy — each trunk carries a crown of fine chemical fronds held out like filters,
and they stir constantly, because the ground exhales. Between them the ground is
stained in mineral rings and beaded with condensate you must not drink.

And it is *quiet* in a way that is wrong. Things live here in numbers, but almost
nothing here is fast, and almost nothing here makes noise on purpose.

## 2. Planetary position

**Terminator band (θ ≈ 75-105°), temperate and dead-stable** — measurements in §0;
the tails past the ≈ window stand, ruled in-character (owner, 2026-09-08) for a band
that straddles the terminator.
- **Energy regime:** permanent scattered twilight. A real photosynthetic budget
  exists — it is simply a *terrible* one.
- **Temperature:** the canon terminator **+14 °C at θ90** (realised +13.0;
  this biome's tiles measure +11.4 median, §0), and remarkably STABLE — no day-night
  swing exists to drive one, and no season ever arrives. Stability, not cold, is the
  axis: nothing here ever gets a reason to hurry (R13).
- **Anomaly:** **chemical venting** (R13).

### Why the vents are chemical — the mechanism that replaces volcanism 🔴
There is **no volcanism, no steam, and no heat source at all** (owner's rulings; R13:
*"It's all about the chemistry at the local site, not anything heat-based."*). The
vents are not driven by heat from below in any form; they are driven by **the
chemistry itself**. The terminator is where two crustal chemistries meet — the
dayside's scorched, oxidised regolith against the nightside's reduced,
volatile-hoarding ground — and where they touch, in the shallow crust, they react:
flowing complex chemistry, vapour formation, powerful reactions. The gas the ground
exhales (sulfides, metal-carbonyls, liberated volatiles) is **reaction product**,
pushed out by the pressure the reactions themselves generate — not exhaust from any
heat engine, and nothing seismic.

⇒ The vents *exist because the terminator exists* — only at the seam do the two
chemistries meet. This biome cannot occur anywhere else on the planet, which is
exactly what a good anomaly should buy.

## 3. Driving forces

**Weak scattered light, a dead-stable temperate ceiling, and a ground that exhales
metal-rich gas.** Chemistry is the abundant energy source; sunlight is the scarce one.

## 4. How the biology adapted

**Chemosynthesis wins, and photosynthesis survives as an underclass.**

The trees metabolise vent chemistry, drawing metal-rich fluid up from the ground.
They cannot excrete it into the soil they feed on, so they excrete it **outward,
into their own bark**. The poison is not a weapon. It is **metabolic waste**, and
the tree is slowly plating itself in its own tailings.

Photosynthesis *is* possible here — and it is comprehensively beaten. The
phototrophs are a **tiny, marginal, crowded-out minority**, and crucially they are
**not green**: in light this weak, green is the wrong pigment. Low-light life
absorbs across the whole spectrum, so the photosynthesizers here are **black, deep
purple and blood-red** — dark films and crusts on the starward faces of trunks and
stones, the ecological equivalent of moss on a north wall. They are never the
canopy. They are what grows *on* the winners.

**Seeing in permanent dusk.** There is light, so eyes are worth having — but barely.
Animals here go one of three ways, and all three should be visible on sight:
- **Huge eyes** — a face that is mostly pupil, gathering every scattered photon.
- **Many eyes** — banks and rings of small simple eyes, summing a dim signal rather
  than resolving a sharp one.
- **No eyes worth the name** — and instead **ground-sense**: the vents make the
  substrate hum constantly, so vibration is a *richer* channel here than light is.
  Feathered feet, drumming limbs, bodies pressed flat to listen.

**Everything alive is either sealed or poisoned.** Sealed (plated, waxed, shelled)
or it processes the load itself and becomes toxic. There is no third strategy.
And **nothing is fast**: a chemosynthetic budget is thin, so life is slow, patient
and heavy — this is a forest of ambushers and grazers-on-mineral, not of chases.

**No grazers in the ordinary sense.** There is no grass and no fodder. Herbivory
here means rasping crust off stone or drinking sap that would kill anything else.

## 4b. Weather

The def's one explicit weather record is `PoisonForestSpores` × 18 (§0); everything
else here is design register, def work owed. _Names drafted this pass — owner
ratification owed (carded)._

| what falls out of the sky | here |
|---|---|
| clear | **scatter-dusk** — the standing state: even, sourceless twilight; no weather ever brings direct sun, beams or shadows (§6) |
| donor `PoisonForestSpores` | ⭐ **vent bloom** — a venting surge: the ground exhales hard, the fronds shed, toxic buildup outdoors; the biome's signature hazard weather |
| fog | **vapour bank** — R13's vapour formation as weather: chemical fog off the vents, sightlines close, condensate beads on everything |
| rain | 🔴 **never** (R-H1: greatest altitudes only; measured 0 mm median, §0). Water arrives as **dewfall** — the R-H2b condensation: fog and dew, frost only out on the night tail |
| snow | does not lie (§5); the night tail may frost, never drift |

- Every "precipitation" here deposits the airborne load — dew is how the forest
  gets poisoned (R-H2b); a wet surface is a dosed surface.
- Vent weather hums: ground-sense fauna (§4) read a vent bloom coming before any
  colonist sees it.

## 5. Always true

- The light is **even, dim, sourceless and unchanging**; nothing casts a real shadow.
- The ground is **temperate, dead-stable and humming** — the hum is the vents'
  chemistry, not any heat (R13); snow does not lie here.
- Every plant surface is **wet or crystalline** — nothing is dry and matte.
- **Standing water is never potable.** It carries the metal load. Condensate,
  puddles, sap: all of it poisons.
- **All meat here is toxic** — and prized (see §7).
- Ore is present **in the organisms**, not only in the rock.
- Anything green is a visitor, a mistake, or dying.

## 6. Never true 🔴 (hard bans — checkable)

- ⛔ **No volcanism, lava, magma, steam or geysers.** The vents are CHEMICAL — no
  heat source of any kind, nothing seismic (R13).
- ⛔ **No green foliage.** Low-light phototrophs are black/purple/red; green here is
  a rendering error.
- ⛔ **No leaves, needles or broadleaf canopies** — nothing reading as a
  conventional tree crown.
- ⛔ **No direct sunlight cues** — no beams, no dappling, no cast shadows, no
  heliotropic forms. Scatter only.
- ⛔ **No potable water source.**
- ⛔ **No lush flora** (standing ban: lush belongs only to the water-high biomes).
- ⛔ **No instantly-nameable Earth organisms** (standing recognizability ban).
- ⛔ **No open grazing herbivore body plans** — there is nothing to graze.
- ⛔ **Nothing fast.** No sprinters, no pursuit predators.

## 7. Uniquely available

- **Bio-accumulated metal.** Old trunks assay richer than the rock. Harvesting is
  the biome's whole reason to exist for a scavenger clan — paid for in exposure.
- **Toxic exotic meat.** Every animal here is poisonous *and* a delicacy: these are
  the prestige ingredients for the Star Wars cuisine chain, the things a cook
  brags about surviving. Danger and value in the same carcass.
- **Vent gas** for chemistry, preservation, weapons and toxin stock.
- ⚠️ **Not water.** The one thing this wet-looking place cannot give you is a drink —
  which makes it a genuine logistics problem, and puts it in direct tension with
  Oomo, whose whole domain is the unspilled.

## 8. Inhabited objects

Whoever came before came for the metal and the gas, and had to bring their own
water. Expect **capped wellheads and gas-tap scaffolds**, **condenser stacks**
furred with crystal, **tap-lines** run tree to tank, and above all **sealed
shelters** — everything built to keep the air *out*. Ruins here are **corroded, not
sand-blasted**, which makes them read instantly differently from every dayside
wreck on the planet. The characteristic small find is a **spent filter cartridge**;
the characteristic large one is a **water tank hauled in from somewhere else**.

## 9. Artistic theme

**"A forest slowly turning into a smelter, lit like a dawn that never arrives."**

Palette: wet black and slate ground · bone-pale trunks streaked with grey metal
tears · crystal in bruised blue and sulfur yellow · the dark red-purple films of the
defeated phototrophs · and no warm light anywhere. Light is **flat, directionless
scatter**, marginally brighter toward the starward horizon — the one directional cue
in the whole biome, and it should be the only way the player can tell which way the
sun is. Silhouette language: **vertical, ragged, encrusted** — trunks widening
downward into scab and slag, crowns feathery rather than massed, animals low and
broad and eye-heavy. Against the ochre emptiness of the dayside this must read as
the planet's exact opposite: wet, dark, chemical, patient, and quietly busy.

## Roster consequences (the sheet is the admission test)

**Wanted:** chemosynthetic trunk-forms · filter-frond plants · crystal and mineral
growths · dark red/purple/black crust phototrophs · plated, shelled or waxed slow
animals · eye-heavy or eyeless vibration-sensing fauna · toxic-meat game.
**Barred on sight:** anything green · conventional trees · grazers · sprinters ·
anything volcanic · anything instantly nameable · lush water-lovers.
Alpha Biomes' chemical and fungal flora are the natural donor pool — every candidate
must clear §6 before admission.
