# The Cracked Lands — definition sheet

_Owner + BENCH, 2026-09-06, written in conversation over three passes. Defines
`ZBiome_Badlands` (More Vanilla Biomes, Zylleon — a deliberately thin vanilla-friendly
donor: "rocky, dry and desolate… little life"; its only contribution is the shape). **The
biome's name is THE CRACKED LANDS** (owner's pick — "otherwise it sounds like drugs").
Thematic handle: **the flood** — and its image: **a thin line of green hiding in the shade,
right next to the razor's edge of barren nothingness in the open sun.**_

🔑 **Read against `desert.md`** (the rung below: the shade economy of a sun at 14°) and
`the_contagion.md` (the rung above, literally: the peaks that rain). The dryland ladder
now reads ExtremeDesert 47° → **Cracked Lands 22°** → Desert 14° → Shrubland 9° →
Wasteland −10°.

## 0. The measurements everything rests on

MEASURED 2026-09-06 off `world/ASHKARR_WORLDMAP_tiles.csv`: **1,086 tiles**, dayside, arc
53→102 (median 68 — the sun **22° above the horizon**). Temp p10/median/p90 1 / 27 / 41 °C.
Elevation median only 164 m but **max 2,101 m**, with the most mixed relief on the planet:
378 small-hill, **328 mountainous**, 197 large-hill, 182 flat. Water 27 tiles, 4 river
tiles; rain median 0, **max 1,132 mm** on the Dew Horn highs. Regions: **Dew Horn 353,
Cracklands 210**, Gray Crags 84, Salt 74, **Damp 74**, Dune Sea 62, Long Sand 29. Seven
sectors of twelve — lobed, not a ring.

🔴 **The peaks (owner, 2026-09-06):** the Contagion goes everywhere it reasonably can as a
world presence — every rain-receiving non-green high with a sterilization path downslope.
So the Dew Horn peaks that rain are **the Contagion's**, and their runoff is this biome's
flood; a tall mountain stays Cracked Lands **only if it gets no rain from the Scald's
storms** (`CONTAGION_BIOME_PLACEMENT_1`).

Donor inventory: nothing mechanical; the vanilla roster (rat, iguana, dromedary,
boomalope, boomrat, ostrich, donkey, fennec, warg, the insects) is **evicted** and the
vanilla flora (oak, berry, dandelion, grass) is **replaced** (§4 — all-alien, terrestrial-
analog allowed).

## 1. What it is

Canyon country below the only dayside mountains that rain. Most of the time it is dry,
cracked, shadowed and still — mesas, hoodoos, slot canyons, clay pans split into
polygons (*the Cracklands*). Then, rarely and without warning, the water comes down:
**violent downward floods of hot, crud-laden water that are fertilizer, life, death,
disaster and damage all rolled into one** (owner). It arrives red off the Contagion's
peaks and brown by the time it reaches the flats, sterilized by the sun on the way; it
tears the canyon, drowns whatever was in it, and leaves behind the one thing nowhere else
on the dryland ladder has: **actual soil**, in the shade. Thin lines of vegetation hide in
that shade, next to the razor's edge of barren nothingness in the open sun. This is where
the Moisture Farmers' cisterns are filled: they find where the water goes after it seeps
into the cracks to hide.

## 2. Planetary position

**Outer dayside (arc 53–102, sun ~22°) × the flash-flood anomaly** — dissected soft ground
directly below the dayside's rain peaks (R-H1: rain at the greatest altitudes; R-H7: the
ocular/Contagion valleys are where it lands and pools, and the rivers leave clean). Where
the Desert's anomaly is *geometry* (a sun low enough that hills shade), this one is
*hydrology*: a sun too high for hill-shade, and canyons cut deep enough to shade
themselves.

## 3. Driving forces

**The flood.** Rare, violent, downward, hot, crud-laden — the biome's clock, its disaster
and its fertilizer in one event. Everything alive here knows where the high ground is.

- **Shade is vertical.** Not hills but cuts: canyon walls make the shade the sun can't
  take away, and the life of the biome lives in the slots — the Desert's shade economy
  turned ninety degrees.
- 🔴 **Soil in the shade** (owner's ruling): actual soil, not just tough plants that grow
  in sand and shade. Not great soil — but soil, laid down by the flood, kept by the
  shade. **The only real soil on the dryland ladder.**
- **The water hides.** After the flood the water seeps into the cracks; the Farmers'
  whole craft is knowing where it went — **this is where the cisterns are filled.**
- **The flood is Contagion runoff, sterilized.** Red at the peaks, brown at the flats
  (`WORLD_RIVER_COLORS_1`'s gradient is this biome's river) — the crud is the Contagion's
  dead, which is why it fertilizes (`the_contagion.md` §3 "downstream").
- **Sandstorms** blow across the open flats (terrain palette, standing); the open sun is
  the other killer.

## 4. How the biology adapted

**The admission test: lives in the shade line, survives the flood, and is not a
terrestrial animal.**

- 🔴 **All-alien flora, terrestrial-analog allowed** (owner's ruling: "it's ok if it is
  more terrestrial-analog than other places simply to give a vague suggestion of home").
  **Grasses and mosses** first, **occasional twisted trees** — nothing nameable, but a
  shape the eye rests on. Authored under `TREE_GRAPHICS_OWNERSHIP_1` (our own vegetation,
  our own scales). The green is a *line*: the lush rule's thin dayside green, hugging the
  shade and the seep.
- ⭐ **The fliers live here** (owner's ruling): the chasms, the shade, the trees, and the
  ease of reaching the sky — this is the fliers' country. But **it is far too dangerous
  to nest here** (the flood), hence the fliers' *desert trips*: they nest out in the
  Desert and Dune Sea and commute to the canyons to feed — which is the Desert sheet's
  "vectors and passengers" (`desert.md` §4c) seen from the other end. Some, near the
  27 open-water tiles, **dip down to fish** (`FISH_BY_BIOME_1`).
- **Canyon-floor life** — what the shade soil supports: small browsers of the moss line,
  flood-timed breeders (spawn in the wet, dormant in the dry), the things that live in
  the cracks with the hidden water. Roster at the sitting; nothing from the vanilla zoo.
- **The open sun kills.** Nothing crosses the flats by day that can help it.

## 4b. Weather and events

- **Clear, hot, still** — the standing state; the open flats lethal by exposure.
- ⭐ **The flood** — the event: warning from the peaks (the Contagion's storm), then the
  wall of red-brown water down the canyon; death, then soil.
- **Sandstorms** across the flats and the pans.
- **Dry lightning** off the Contagion's storms at the ridge.
- 🔴 No rain here (R-H1 — it rains on the peaks, not in the canyons).

## 5. Always true

- The flood comes rarely and comes down; it is the only water delivery and it kills.
- Shade is in the cuts; the sun owns the flats.
- The soil is real and it is in the shade — the one dryland biome you can farm without
  fog or a river.
- The water hides after the flood; the cisterns are where somebody found it.
- The fliers feed here and nest elsewhere.
- Everyone travels the roads; only the Farmers stay.

## 6. Never true — 🔴 HARD BANS (linter-checkable)

1. 🔴 **No standing surface water beyond the measured 27 tiles** — no lakes, no permanent
   rivers; water arrives as flood and hides.
2. 🔴 **No green outside the shade line** — a flora def resident on open sun-flats is a
   violation; the lush rule's thin line, not a region.
3. 🔴 **No nameable terrestrial animals** — the vanilla zoo evicts; analog *shapes* are
   allowed (owner), names are not.
4. 🔴 **No flier nests** — fliers feed here, nest in the desert; a nesting def resident
   here violates the "too dangerous to nest" ruling.
5. 🔴 **No rain in the canyons** (R-H1); the peaks rain, and those peaks are the
   Contagion's where they do.
6. 🔴 **No resident faction but the Moisture Farmers** — Junkers, Hutts, Jawa and the deep
   desert tribes are road traffic, never settlements here.
7. 🔴 **The recognizability rule applies**; the icon carve-out protects icons.
8. 🔴 **No structure on the canyon bottom — higher tiers, NEVER the floor** (owner,
   2026-09-06, "NEVER" twice). A settlement or map template placing buildings on the
   canyon floor violates; the flood-marked ruins are what floor-building leaves.

## 7. Uniquely available

- ⭐ **Soil** — the only real farmland on the dryland ladder, in the shade; not great,
  but soil. (And the fungal-soil trade lands here: `FUNGAL_SOIL_TRADE_1` — the Rot's
  mycelial soil hauled by ship to the farms is how a Jawa makes early money.)
- ⭐ **Cistern water** — the hidden flood, found and held; the Farmers' economy and the
  planet's most defensible water.
- **Flood mulch** — the Contagion's sterilized dead, delivered free downstream.
- **Fish** — at the 27 open-water tiles, and the fliers' fishing (`FISH_BY_BIOME_1`).
- **Roads** — the Cracked Lands are *on the way*: Junker caravans, Hutt envoys, Jawa,
  and everything they sell or threaten.
- **Fortification** — canyon walls; the best natural defense on the dayside.

## 8. Inhabited objects

- 🔴 **The Moisture Farmers — the only residents** (owner's ruling): homesteads,
  vaporator fields, cistern heads, walled compounds, ruined farms — `MOISTURE_FARM_TEMPLATES_1`
  builds the family. Fields on the shade soil; walls facing the sun and the flood.
- **The roads, and who is on them** (owner): **Junker caravans** come through to sell
  things — or to threaten people; **envoys from the Hutts**; **Jawa**; and, rarely, only
  when desperate, **the deep desert tribes** trade a little. **Mostly they all stay to the
  roads.**
- **Cisterns** — the Farmers' found water; and the dry cistern that nobody found in
  time.
- **Flood-marked ruins** — high-water lines on canyon walls; the farm that was built one
  meter too low.
- **The fliers' feeding ledges** — droppings, bones, the fish-heads near water.

## 9. Artistic theme

**"A thin line of green in the shade, beside the razor's edge of the open sun."**

- **Light:** the hardest contrast on the planet — slot-canyon shadow against white-hot
  flats; the green only ever in the blue shade.
- **Palette:** cracked clay grey-white, red-brown flood stain on the walls, moss green in
  the slots, the red-to-brown of the water when it comes.
- **Silhouette language:** vertical — mesas, hoodoos, slot walls; twisted trees against
  the sky; fliers wheeling up out of the cuts.
- **Motion:** none, then the flood; fliers as the only daily movement.
- **Sound:** wind in the slots; nothing; then the roar from upstream — and the water
  chimes (§11) sounding up through the stone before it.
- **Smell:** the flood announces itself by nose first — wet clay on the wind off the
  peaks before any sound arrives, and the flats begin to *tick* as the Sealed wake
  (§10). An experienced Farmer trusts the ground before the chimes.

---

# The enrichment pass — Owner + BENCH, 2026-09-06 (backfilled; `CRACKED_LANDS_ENRICHMENT_1`)

_The layer the first sitting skipped: bestiary sorts, items, structures, faction
faces. Ruled in conversation; the sorts are the deliverable — per the standing
sequencing rule, actual animals are assigned in the full plant-and-animal pass._

## 10. The bestiary sorts — a fauna divided by TIME, not space

The Weeping Stones divide their animals in *space* — rings around a pool, everything
visible, congregated, at truce. The Cracked Lands are the deliberate inversion: the
fauna divides by **when it is alive**, and almost nothing is visible at all. **There
is no truce here and there cannot be** — the truce is a law of open water, and here
the water hides; the kill happens at the seep and the shade line (`weeping_stones.md`
§4 is the other pole). You see nothing all day, and are watched the whole time.

- **The Sealed** (plainly: creatures that sleep through the dry years). They survive
  the way Earth's lungfish does — sealed inside a wax-lined burrow under the cracked
  clay, metabolism banked to almost nothing, until water wakes them. The famous
  cracked-pan flats ARE a dormant fauna: walk them and you walk on sleeping animals.
  They cluster where moisture lingers, so **the Farmers read them as living dowsing
  rods** — where the sleepers lie thickest, the water hides nearest. Their shed
  burrow-lining is **crack-wax** (§11).
- **The Spenders** — everything that must live a whole life in the flood-weeks:
  mudflat breeders, bloom-followers, a sudden carpet of small frantic life between
  the roar and the dry. This is *why* the fliers commute in (§4's ruling): their
  feeding runs peak here. The flood also delivers its own drowned dead, so the
  carrion birds get two feasts — the drowned first, the dying carpet after.
- **The Patient** — the year-round shade-line residents: moss-browsers on the real
  soil, crack-dwellers at the seep, and the ambush predators the fauna doctrine
  already assigns this biome ("ambush country, scavengers"; the emperor vulture
  rides the flat's thermals as the sky's undertaker).

**The standing cast**: MEASURED 2026-09-06 off `design/Jawa/fauna/cast_assignment.csv`
(sha256:0331f6610967ba7f) — **29 species currently assigned**, pre-sheet; graded
against these sorts at the roster item.

## 10b. Explosive growth — 🔴 a WORLD mechanic, born here (owner, 2026-09-06)

The Spenders' flora half, and the owner took it planet-wide: **water-soaked plants
grow VISIBLY — actually getting bigger on screen, not animal-motion but growth the
player watches — and it is intimidating.** *"'OMG, what's going to happen?' should
be the feeling near any water-soaked plant."* It cannot grow forever, so **what DOES
happen at the top is a designed moment, meant to recur** — custom mod actions so
players experience and play with it (`EXPLOSIVE_PLANT_GROWTH_1`). The jungles should
visibly grow. In these canyons it is rare — most visits see the dry stillness — so
**the plot organizes a witnessed flood at least once**
(`FLOOD_WITNESS_EVENT_1`). Locally: the bloom is also an economy — a crop that
exists only in flood-weeks; when a canyon blooms the market drowns in it, then
nothing for years. Boom-bust on the flood's clock.

## 11. Items and structures

- ⭐ **Water chimes** (owner's pick, replacing the bell-line draft). Deep, resonant
  chimes seated down in the crack network beside the hidden water, rung not by wind
  but by water on the move; the seep-cracks fill before the surface wall arrives, so
  their tones roll up through the stone ahead of the roar. Tooltip, owner's words:
  *"Ancient water chimes: their tones ring not from wind but the tugs of water
  coursing down in the annual inundation, far overhead."* The Weeping Stones' vanes
  sing in the wind; the Cracked Lands ring in the water — the two biomes are a
  matched pair of instruments.
- ⭐ **Discovery surveys** (owner's correction of the "cistern chart" draft —
  everyone KNOWS where the known water went; *that's where they now live*). The
  valuable item is the survey of a **newly discovered** hidden water: a big,
  sparsely populated world still holds surprises, and fresh data on one is an
  exceptionally valuable thing to sell. Item-as-quest-seed.
- **Crack-wax** — the Sealed's shed burrow lining, gathered off the flats after a
  wake; the waterproofing the Farmers line their cisterns with. The biome's
  signature material.
- **The bloom harvest** — §10b's boom-bust crop.
- **Structures**: 🔴 **build on the higher tiers of the canyon, NEVER the bottom.
  NEVER** (owner, verbatim on the second word). Homesteads, vaporator fields and
  cistern heads occupy ledges and upper benches; the flood-marked ruins of §8 are
  the compounds built too low, and they are ruins. Plus refuge ledges cut along the
  roads (where travelers climb when the chimes sound), waymark cairns on the flats,
  and fields terraced into the shade line.

## 12. Faction faces — everyone on the roads, each for a different reason

§6's ban holds the frame: no resident but the Farmers, so every other face is a
*road* face.

- **The Moisture Farmers** — the only settled face: high-bench homesteads (never the
  floor), vaporators AND banked cisterns — the one place their Manufacture doctrine
  has a second source. Chime-lines, discovery surveys, walls facing sun and flood.
- **The Jawa** — road traffic with a rhythm: **a flood is a salvage strike.** The
  wall tears open ruins, washes buried tech from the banks, re-deals the board;
  crawler crews follow flood-news the way prospectors follow gold. The best
  scavenging on the dayside, for exactly as long as the mud is fresh.
- **The Hutt Cartel** — the deep-desert posts include *Tolls*, and a slot canyon is
  where a toll post actually works: one gate takes a cut of everything. Legal — the
  one barbarism is charging for unsettled *water*; a road is commerce. The Hutts
  know precisely where that line sits and stand on the correct side of it, smiling.
- **The Deep Desert Tribes** — rare desperate trade (§8), the short sharp raid on
  the road itself; the cisterns they never touch — settled water is legal water, and
  they are the law's zealots.
- **The Blackstar Company** — ambush country is contract country; hunts *end* here.
- **The Empire** — convoys must thread the slots and every officer hates it: no
  garrison (§6), just patrols through the best ambush terrain on the planet, where
  the locals hold the high benches.
- **The Geonosians** — they don't need the roads. A Foundry column crossing the open
  flats in full sun, off-road, unbothered, is the sight that empties a toll post.

---

## Owed

- **Roster** at the sitting: the fliers (with the Desert sheet's vector line — where they
  nest), the canyon-floor life, the fish.
- **Flora authoring** — grasses, mosses, twisted trees (`TREE_GRAPHICS_OWNERSHIP_1`).
- **The flood as an event** (engine): warning, the wall of water, drowning, deposition
  of soil; flood-marked terrain.
- **The Contagion peaks** ruled by rain (`CONTAGION_BIOME_PLACEMENT_1`); the river
  gradient (`WORLD_RIVER_COLORS_1`).
- **Fish** (`FISH_BY_BIOME_1`) and **sand fishing** (`SAND_SWIMMERS_MOD_1`) as the owner's
  new concepts.
- **Def label** → "the Cracked Lands" (rename on `ZBiome_Badlands` or our own def — the
  freeze review decides with the other donor-def renames).
- **Def-tails check** on the 1,086 tiles after the Contagion peaks are cut out.
- `EXPLOSIVE_PLANT_GROWTH_1` — the world mechanic born in §10b: visible growth,
  the designed terminal moment, custom mod actions.
- `FLOOD_WITNESS_EVENT_1` — the plot arranges a witnessed flood (and growth) at
  least once.
- **Roster grading** — the 29 cast (MEASURED §10) against the sorts, in the full
  assignment pass; water chimes, discovery surveys, crack-wax and the bloom as
  item defs.
