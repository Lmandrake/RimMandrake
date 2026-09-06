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
- **Sound:** wind in the slots; nothing; then the roar from upstream.

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
