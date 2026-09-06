# The Rot — definition sheet

_Owner + BENCH, 2026-09-06, written in conversation over three passes. Defines
`AB_MycoticJungle` (Alpha Biomes' "Mycotic Jungle" — donor content incorporated wholesale,
then bent). **The biome's name is THE ROT** (owner's pick). Thematic handle: **the
planet's gut** — and its image: **a pale forest with a heartbeat of rot.**_

## 0. The measurements everything rests on

MEASURED 2026-09-05 off `world/ASHKARR_WORLDMAP_tiles.csv`: **1,939 tiles** — the largest
biome defined since the dryland ladder. Arc 89→130: from touching the terminator down to
sun 40° below the horizon. Temp median −19.3 °C, spread −54.3 to +23.8 — and the spread is
not noise, it is the map of digestion (§3). Elev median 703 m, flat-to-rolling. **Zero
water tiles, zero rivers.** Regions: Nightspill (368), Frostcaps (224), Sporefields (170),
Blindwood (135), Mould Marches (121), Hanging Wood (118).

Donor inventory taken in: the twelve-species fungal flora suite (Bryolux carpet,
Glowstools, the Agarilux family), the two spore-allergy diseases and the mod's fastest
disease clock (mtb 35), and the fungus/animal hybrid natives (Agaripawn, Agaripod,
Wildpawn, Wildpod, Mycoid Colossus, Swarmlings). 🔴 The donor def's vanilla `wildAnimals`
zoo (rat, boar, alpaca, cassowary, chinchilla, raccoon, cobra, warg) is **evicted
wholesale** (owner's ruling).

## 1. What it is

A pale fungal continent on the night shoulder of the stormwall — bone-white and lilac
towers under a black sky, a glow-moss floor that is warm to lie on while the air above it
would kill you, milky ponds that are not water, and a fine wet gloss on every surface that
is the jungle deciding whether you belong to it yet. Nothing here is a plant. Nothing here
is quite an animal. Everything here is connected, everything is warm from the inside, and
everything — including what you take away with you — is still alive.

## 2. Planetary position

**Night-shoulder regime × the fallout anomaly: the planet's gut.**

Your Hadley ruling built the organism: the dayside photosynthesizes, the stormwall shreds
and exports, and the wet-toxin fraction falls on the wall's night shoulder — this biome's
entire energy budget. **The dayside is the planet's leaf, the stormwall is its throat, and
The Rot is its gut** — a continent-scale decomposer eating the sky's export, forever.
Fungi are the one metabolism that never noticed the sun is gone.

This is the nightside's lush (lush rule #3, honored to the letter): dense beyond anything
dayside, and built of nothing a colonist would call a plant — the dayside's lush is a thin
green line; the nightside's is a thick pale sprawl.

## 3. Driving forces

### The gut, and the war it digested

🔴 **The Rot is Assailant-bioweapon-ADJACENT, and disarmed** (owner's ruling): the war's
biological material arrived as **lateral gene transfer** and drove the fungi to extreme
behaviors — but a thousand years of layered ecological stability broke the donor material
down and kept only what earned its place. **Nature won here.** HorrorWastes is what that
material does unstabilized; The Rot is what a gut does to a weapon: it composts it.

🔴 **Consequence for genes (owner, 2026-09-06):** genepack extraction here yields ONLY
genes beneficial to the local fungus and hybrids — the competitive survivors. **The
living-gene-reactor mechanic — the place that memorizes and hashes the war's genetic
information — is RESERVED for `AB_GelatinousSuperorganism`** and must not be built here.
(The plunder review of the two new donor mods rides `GENEPACK_MODS_PLUNDER_1`.)

### Thermogenesis — the warmth is metabolic

Decomposition is exothermic (real reference: compost cores run 60–70 °C; fungal
thermogenesis is documented biology). The mycelial mat is a heated floor the jungle makes
for itself: on the mat, damp and workable; off it, nightside cold. **Frostcaps is where
the heat fails** — the starved, freezing edge. Warm ground = actively feeding; cold ground
= starving or dead. ⭐ Lean-in (owner's ruling): some mushrooms give off heat *palpably*
and can be **cultivated as living heaters** — the grown furnace, wired to the
heat-generating gene mechanic (exact gene def owed — never guess a defName).

### The Sheen — the jungle exhales

The fungi own all the moisture they need; what falls here is **emitted, not received**.
🔴 **The Sheen** (owner-named): a reproductive sleet flung outward to colonize — a fog
that cloys and sticks to things, and its coating carries the same name. Breathing it
without a compatible immune system virtually guarantees disease: **the biome's border is
enforced by its own breath.** R-H1 never blinks — this is fungal emission, not weather in
the meteorological sense, though the player meets it as weather.

⭐ **The milk** (owner-authored): the Sheen runs back down into milky-white ponds and
streams of *not-water* — the jungle reclaiming its own exhalation. A closed loop you can
see: the only "surface water" on the night shoulder, and none of it is water.

### The rot clock

🔴 Everything decays MUCH faster than normal here — raw meat left exposed is **gone within
a day, for certain**. The gut digests whatever is set down in it.

## 4. How the biology adapted

- 🔴 **All-fungus flora** (owner's ruling): no conventional plants, none. The donor's
  twelve-species suite is the base — glow-carpet, food-caps, the giant Agarilux
  wood-substitutes.
- 🔴 **Hybrid-or-out fauna** (owner's ruling): the few animals that dwell here are
  fungus/animal hybrids — the donor natives mostly already are (Agari/Wild pawns and pods,
  the Mycoid Colossus, Swarmlings). The admission test at the assignment sitting is
  literal: no hybrid nature, no residence.
- 🔴 **Health-sharing — everything here is unusually connected** (owner's ruling): when a
  creature is badly hurt, others rush to it and *share* its wounds, splitting the injuries
  between bodies until the load is survivable. **Both variants exist, on different
  species**: (a) true wound-splitting, (b) the softer tend-aura (nearby kin accelerate
  healing). ⭐ **Works on tamed creatures** — your herd bleeds as one.
- **Guardianship is a law of potency** (owner's ruling, §7): anything worth taking defends
  itself richly. The tea-source mushrooms are the biome's armed nobility.

## 4b. Weather

- **Sheen-fall** (re-skin of the donor's "very common rains"): the reproductive sleet —
  cloying, coating, disease-certain for the unadapted. The common state.
- **Spore events** (donor mechanic kept): the biggest fungi vent suffocation clouds.
- 🔴 **No water rain, ever** (R-H1) — every falling thing here is the jungle's own making.

## 5. Always true

- The warmth is metabolic: the mat is a heated floor; air temperature is a lie about the
  ground.
- The Sheen coats everything, and everything sheened is being considered for colonization.
- Raw organics decay within a day; the gut is always digesting.
- **What you harvest is still alive**: produce keeps metabolizing after harvest, pushing
  heat — it will wreck any freezer that is not overbuilt.
- 🔴 **The live preparations cannot be stored** (owner's ruling): teas and symbionts must
  be kept alive like an egg — refrigeration kills them, delay kills them. *You want some
  of this, you come to the biome and prepare it in your vessel, right now.*
- All useful light is biological.
- The connected biology defends itself and repairs itself collectively.

## 6. Never true — 🔴 HARD BANS (linter-checkable)

1. 🔴 **No conventional plants** — a non-fungal flora def resident here is a violation.
2. 🔴 **No pure-animal residents** — resident fauna must be fungus/animal hybrid.
3. 🔴 **No water rain** (R-H1) — the Sheen is emission; a water-rain weather def here is a
   violation.
4. 🔴 **No stockpilable teas or symbionts** — a shelf-stable, refrigerable, or exportable
   version of a live preparation is a violation of the come-here-and-brew ruling.
5. 🔴 **No general gene bank** — extractable genepacks carry locally-beneficial genes
   only; the gene-reactor mechanic belongs to `AB_GelatinousSuperorganism` alone.
6. 🔴 **No psycast economy** — the anima-analog grants only a few vanilla, Light-side-
   fitting powers (§7); Vanilla Psycasts Expanded content here is a violation.
7. 🔴 **No active bioweapon-class content** — The Rot is bioweapon-*adjacent* and
   disarmed (war-legacy split); an engineered weapon-organism def here is a violation.
8. 🔴 **No undefended prizes** — a high-value harvestable without a guardian mechanism is
   a violation of the potency-implies-guardianship law.
9. 🔴 **The recognizability rule applies**; the Star Wars icon carve-out protects icons.

## 7. Uniquely available

- ⭐ **The teas — biosculpting in a cup, EARNED** (owner's ruling): age-reversal,
  bioregeneration, the pleasure brew — each carrying a biosculpter cycle's effect, each
  brewed live on-site or never. **Their source mushrooms defend themselves richly** —
  guardianship expands to a real defense repertoire (to concretize with the roster):
  suffocating spore bursts, hybrid defenders summoned through the mycelial network, the
  mat itself grasping, false fruiting bodies. Getting a tea is an expedition, not a
  harvest.
- ⭐ **Symbiont parasites — luciferium pulled apart** (owner's ruling): beneficial tenants,
  each a bargain with teeth. The ratified pairs: **accelerated healing / massively
  increased metabolism** · **sleep abolished / always a little psychotic** · **Sheen
  immunity without gear / intolerance of the sun**. All live preparations (ban 4); the
  Sheen-immunity symbiont is how you *join* the biome instead of resisting it.
- **Local genepacks** — the competitive survivors of the digested war: heat generation,
  Sheen compatibility, hybrid vigor. Beneficial-to-here only (ban 5).
- **The gourmet line** — powerhouse chemistry as Star Wars cuisine: named delicacies,
  lavish-meal multipliers, trade goods the galaxy pays for. (Ruling covers the Forsaken
  Crags too — retrofitted into that sheet's §7.)
- **Grown heaters** — the palpably-warm mushrooms, cultivated for it.
- ⭐ **The pale tree** (owner's ruling, lightest touch): a reskinned mushroom-based
  anima-analog, **sacred to Wildsteam, aligned with the Light side of the Force**. It
  grants only a few very light vanilla psypowers fitting a Light-side initiate — and the
  distinct sensation that **you really should find someone to train you.** No economy, no
  ladder, a door ajar.
- **Instant composting** — the rot clock as a service: corpses, filth, and mistakes
  disappear here faster than anywhere on the planet.

## 8. Inhabited objects

- **Wildsteam sacred groves** — the pale trees and their tended approaches; the wild's
  partisans finally somewhere they are not preaching to deaf ears. Pilgrim paths worn
  through Hanging Wood.
- **Brewing stations** — semi-permanent vessels and shrines-of-use near the guarded tea
  groves, maintained by whoever came last, per the come-here-and-brew law.
- **Digestion sites** — where Assailant material fell and was tamed: ruins the jungle has
  grown through, deniable, quietly warm, richer in genepacks than anywhere else.
- **Guardian thickets** — the armed nobility's ground; the map's marked danger and marked
  treasure, one and the same.

## 9. Artistic theme

**"A pale forest with a heartbeat of rot."**

- **Light:** glow-moss carpet and glowstool constellations; black sky; the milk ponds
  catching and returning the biolight; breath-fog where the mat vents heat into freezing
  air — the biome visibly *exhaling*.
- **Palette:** bone white, lilac, milk white, glow-blue and lantern-gold against wet
  black soil.
- **Silhouette language:** towers and caps and gills — architecture that grew; nothing
  angular, nothing dead; the Colossus as a walking piece of the forest.
- **Surface:** everything gloss-coated — the Sheen reads as a wet shine on creatures,
  ruins and visitors alike; the longer you stay, the more you shine.
- **Sound:** the donor's insect hum day and night; wet settling; the hiss of Sheen-fall;
  warmth you can hear as slow subterranean movement.

---

## Owed

- **The heat-generating gene** — MEASURED (`genepack_mods_plunder.md`, 2026-09-06):
  neither new mod ships any GeneDef, so the gene must be AUTHORED; closest ready-made
  numbers are the consumables mod's `IgniFurnace`/`IgniWarm` hediffs.
- **Guardian repertoire concretized** per tea species at the assignment sitting (owner
  asked for this portion expanded — the menu in §7 is the seed).
- **Engine feasibility pass:** health-share comp (C#, two variants); the live-item
  viability clock (dies refrigerated, dies delayed); heat-pushing produce comp; the milk
  ponds as terrain (donor Marsh patches re-skinned to not-water milk); Sheen weather def +
  compatibility hediff; the rot-rate map condition; the pale tree as a Royalty anima
  reskin with a restricted vanilla psycast set (audit which vanilla powers read
  Light-side).
- **Roster admission tests** at `BIOME_FAUNA_ASSIGNMENT_SITTING_1`: hybrid-or-out; the
  donor exotics tail (trace-commonality non-hybrids) judged there.
- **Wildsteam wiring** — the sacred-grove relationship into `FACTION_SPEC.md`.
- **Def tails check** — arc-89 edge tiles vs the terminator families; fold any strays into
  `WORLDMAP_DESERT_BAND_REPAIR_1` (not yet measured for this def).
