# Golden-canon cleanup of three biome sheets — 2026-09-08

Sheets: `design/Jawa/worldbuilding/biomes/nightside_ice.md`, `the_blue_desert.md`,
`the_propane_lakes.md`. Owner: "make sure those sheets are golden and correct, with no
provenance muddying them." Not committed; README_BIOME_GRAMMAR.md untouched.

## How the numbers were verified

`world/ASHKARR_WORLDMAP_tiles.csv` (21,872 tiles) with these plans overlaid in order
(`to` wins): backside_reband_full → pf_terminator_plan → wasteland_reclaim_plan →
crag_meander_plan → pf_meander_plan → graycrags_coldonly_plan. Summer max =
temp_c + curve(|sin lat|), curve linear through (0,3),(0.1,4),(1,28). Sectors =
floor(bearing/30). Script: scratchpad `recon.py` (throwaway).

| def | tiles | arc p10/med/p90 (min–max) | temp p10/med/p90 (min–max) | elev med | max<0 |
|---|---|---|---|---|---|
| RUT_NightsideIce | 1,406 | 117.0/124.9/134.7 (111.3–139.1) | −45.1/−32.4/−22.1 (−49.0…−14.1) | 748 (max 1,884) | all |
| BiomeGRimond | 1,029 | 124.6/134.7/143.2 (118.0–149.0) | −55.1/−42.6/−30.2 (−58.0…−19.4) | 640 | all |
| AB_PropaneLakes | 2,531 | 139.3/151.3/166.0 (132.4–178.8) | −73.0/−62.2/−47.8 (−81.7…−42.1) | 670 | all; all mean < −42 |
| RUT_PropaneLake | 57 | 171.9/175.4/178.0 (169.6–179.2) | −81.0/−79.0/−76.3 (−82.0…−74.7) | −120 | all |

Other numbers used: AB_MycoticJungle (the Rot) temp median −19.0; AB_RockyCrags arc
p10 100.2 / p90 115.6 / max 121.5; planet's coldest tile is 18991 (RUT_PropaneLake,
−82.0); every tile at arc ≥165 is AB_PropaneLakes (303) or RUT_PropaneLake (57).
Region and hilliness tallies as written into the sheets came from the same run.

Bearing sectors 0–11:
- NightsideIce 136/115/116/72/289/81/137/105/105/44/41/165 — all 12 present (min 2.9%)
- BiomeGRimond 120/71/78/77/56/87/83/49/45/113/149/101 — all 12 present; 7 and 8 under 5%
- AB_PropaneLakes 279/214/191/195/159/131/142/169/242/311/263/235 — all 12 ≥ 5.2%

Caveat: the CSV's own `biome` column is the pre-plan paint; a reader re-measuring from the
CSV alone will not reproduce these counts without the overlays.

## What changed

### nightside_ice.md
- §0 rewritten as current-state only: dropped IceSheet-49 / 802-tile / sector-1–3 /
  crystal-caverns history, the plan-file overlay list and per-plan contributions, the
  dated MEASURED tags. Added |lat| median, zero-water, summer-max<0.
- §0 "Sectors 0–5 and 7–10" → all twelve sectors present, unevenly (41–289); the
  highland-lobes ruling sentence kept verbatim.
- §2 arc 128–159 → 111–139; V18 amendment card deleted.
- §2 struck-claim paragraph: crags "arc 103–121" → "100–116 at p10–p90, tailing to 121".
- Owed: "paint the 802 tiles" → "paint its 1,406 tiles".

### the_blue_desert.md
- §0 rewritten to BiomeGRimond as painted (1,029; arc/temp/elev/hilliness/regions);
  the 1,711-tile HorrorWastes inheritance stats dropped; ladder → −19 / −42.6 / −62.2.
- Ring ruling paragraph kept; its premise restated in one sentence (the inherited ground
  was a perfect ring) without the dead def's statistics.
- Both V18 amendment cards deleted; the second collapsed into a one-sentence current
  sector census after the mosaic table.

### the_propane_lakes.md
- §0 rewritten: 987 → 2,531 and all dependent stats; "sun 45°–76°" → 49°–76°; "coldest
  tiles on the planet (−80.8)" → −81.7 land, −82.0 lake; "three-lobed, sectors 4,5,8 weak
  at 59/68/51; CrystalCaverns holds them" → lobed, thinnest through 4–6 (159/131/142);
  "Older docs say 554" line and the V18 card deleted; RUT_PropaneLake arc/temp added.
- §3 "The largest region is the nightside's chemical oasis" → "The Flats — 692 tiles of
  this def — are…" (Deadstone 861 and Umbra 773 are now larger).

## Left for the parent (not deleted)
See the return message: sector-census lines added under frozen anti-bullseye rulings;
Blue Desert ban #4 and the Propane "never a ring" wording now measure marginal/false;
Propane Owed still says nobody has painted RUT_PropaneLake though §0 measures 57 tiles;
"rendered for the owner before painting" process line left in Blue Desert §0.
