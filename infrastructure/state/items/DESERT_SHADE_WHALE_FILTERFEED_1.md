# DESERT_SHADE_WHALE_FILTERFEED_1 — sand filter-feeding + dung-seeding for the shade whale

## what is wrong

desert.md §4c/§10 describes the shade whale megafauna's two defining
mechanics — it "filter-feeds through the sand, straining the buried canopy
and the small life grazing it," and "leaves massive dung at shade patches"
that "immediately seeds young plants and young creatures around it," making
it the desert's only long-distance vector between otherwise-sealed
patch-networks. Neither exists. `RSW_ShadeWhale`
(`src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_ShadeWhale.xml`,
COMMISSION_LEDGER_CLEANUP_1) landed the def itself — body, stats, herbivore
profile, real shade-seeking wander via the existing
`RM_ShadeSeekingWanderExtension` — but eats like an ordinary grazer today,
via plain `VegetarianRoughAnimal`. §10's own implementation table names the
reason: `FoodTypeFlags` is a closed enum with no terrain member, so "grazes
buried sand-canopy" has no native route.

## why it matters

Without the filter-feeding/dung-seeding pair, the shade whale is cosmetically
a megafauna but mechanically inert — it doesn't fertilise the harbours it
stops at, and the desert's "circulatory system" (§4c: the only vector
carrying seeds, riders and parasites between sealed patch-networks) is prose
with nothing behind it. The def landing without this is the sheet's own
explicitly sanctioned order, not an oversight — `rosters/desert.json`'s
`new_defs` entry for this slug says "def can land first."

## the work

Two mechanisms, same shape as `DESERT_SHADE_GRID_KEYSTONE_1`'s own table
entry ("megafauna heat | C#, modelled on the pawn, driven by `ShadeAt`, not
by map temperature") — this item is the sibling row, "filter-feeding sand":

- **Sand filter-feeding.** A `ThingComp` (or `CompProperties_Grazer`-style
  hediff-free hunger satisfaction) that lets `RSW_ShadeWhale` feed while
  standing on sand terrain, independent of `FoodTypeFlags`/nutrition-seeking
  job — needs a design decision on trigger (a JobGiver like vanilla grazing,
  or a passive hunger-rate reduction while on Sand terrain) and whether it
  reads `RM_MapComponent_ShadeGrid` at all (it doesn't need to — filter-feed
  is terrain-keyed, not shade-keyed) or is a wholly separate, simpler comp.
- **Dung-seeding.** On defecation (or a periodic tick while resting in
  shade), spawn/boost nearby wild plant growth and a small chance of new
  wildlife at the whale's current shade patch — likely a
  `CompProperties_ProducesDung`-style periodic effect keyed to `ShadeAt`
  (only fires meaningfully while shaded, matching "leaves massive dung at
  shade patches"), scoped small enough not to need a new DamageDef/Hediff.

## Watch out

Do not block the def's existence on this — `RSW_ShadeWhale` is already live
and eats fine as a generic grazer; this item only closes the mechanical gap
between "a big animal exists" and "the biome's circulatory system is real."

## verify

`RSW_ShadeWhale` gains a real filter-feeding behaviour (feeds correctly on
sand independent of `FoodTypeFlags`) and a dung-seeding effect that measurably
boosts nearby wild plant growth at a shade patch after it rests there.

## criteria

The shade whale's two named ecological mechanics from desert.md §4c both
exist as working C#, not just as its stat block.
