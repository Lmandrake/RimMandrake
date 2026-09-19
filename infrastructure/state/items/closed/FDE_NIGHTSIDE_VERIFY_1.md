## Spec (as filed, reconstructed from the ruling it verifies)
`infrastructure/state/canon.yml` `free_droid_enclaves.geography_src` (owner,
2026-08-30): "there are the droids who fled deep into the cold dark of the
nightside. I believe there are two settlements already there. They suffer
from very low power... burn the strange materials around them for dirty
power... so cold that it can freeze their servo's... generate fuel they sell
to the Junkers via long-distance pipes." VERIFY owed (`reconciled_lore/GAPS.md`
line 19): two nightside settlements on the frozen map.

## Method
`measure csv world/ASHKARR_WORLDMAP_settlements.csv --where "faction=Free Droid
Enclaves"` — MEASURED 12 (sha256:c142435a38d3138a). Read all 12 rows' `arc`
column (0 = substellar/dayside, 90 = terminator, >90 = nightside per the
corrected axis in `tidally_locked_world.md`) plus their `why` text.

## Finding — CONFIRMED, and the two are identifiable, not just countable
Four of the 12 FDE settlements sit at nightside arc, but only two match the
owner's fuel-refugee description; the other two are nightside for an
unrelated reason:

| settlement | arc | biome | why |
|---|---|---|---|
| **The Cracking Station** | 178.01 | AB_RockyCrags | "on the propane lakes of the Ammonia Flats — 554 tiles of liquid fuel at -80 C that only a droid can work, and the reason there is a road out here" |
| **Coldfire** | 149.27 | AB_RockyCrags | same Ammonia Flats propane-lake text |
| The Trade Socket | 113.93 | BMT_FungalForest | "relocated: a neutral droid enclave belongs far from civilisation, not on the Scald[ing dayside]" — a *different* siting reason (neutrality), coincidentally also nightside-arc |
| Vent Nine | 138.02 | HorrorWastes | same relocated/neutrality text as Trade Socket |

**The Cracking Station + Coldfire are the owner's two nightside refugee
settlements**: both on the Ammonia Flats' 554-tile liquid-fuel propane lakes
at -80 C (matches "servo-freezing cold" + "burn the strange materials...
for dirty power"), both deep nightside (arc 149-178, well past the arc-90
terminator), both explaining the road that would carry the long-distance
fuel pipes to the Junkers. The Trade Socket/Vent Nine pair is a distinct,
already-authored siting decision (civilisational neutrality) that should not
be double-counted as the refugee pair.

## criteria
- [x] Two nightside FDE settlements exist on the frozen map — MEASURED, named:
      The Cracking Station, Coldfire.
- [x] Their siting matches the owner's description (cold, fuel-burning,
      propane/liquid-fuel terrain, isolated enough to need a long road/pipe
      route) rather than merely satisfying the arc threshold.

## Not touched
The Rust Cathedral congregation grouping (the other half of the 2026-08-30
ruling) is a separate, unverified claim — out of scope for this item.
