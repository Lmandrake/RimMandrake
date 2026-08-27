# WORLDPAINT_REHEARSAL.md — paint the planet into a throwaway world, and LOOK at it

> moved there on 2026-08-23, byte-unchanged. **Nothing was deleted.** What moved: the superseded
> adoption/`remaking` banners, §1–§3 (what the run proves, the two shut gates, the preconditions),
> and §5, §6, §6b — the run sequence, the decision strings and the 25 ride-alongs.
>
> 🔴 **§5 and §6 were a LIVE HAZARD in this file and that is why they moved.** They walk a reader
> through generating a world and painting the 21,872-tile bundle onto it. `canon.yml` reads
> `planet.status: remaking`, `FINAL_WORLD_PREP_1` is BLOCKED by the owner because it *"would prep
> a dead map"*, and `W9` is `dropped`. **Do not execute them out of the archive either.**
>
> ⚠️ **The archived §2b is WRONG and is corrected in the archive's own header.** It says
> `OnlyOurFactions.xml` sets both `startingCountAtWorldCreation` and
> `maxConfigurableAtWorldCreation` to 0. Verified 2026-08-23: it zeroes only the first, on 48
> defs, and its header forbids ever touching the second again.
>
> ⚠️ **CORRECTED 2026-08-26 (WORLDGEN_CITATIONS_REPOINT_CHECK_1): "Nothing was deleted" is no
> longer true.** The archive file this header points at was deleted whole at `892beac2`
> (2026-08-26), with no successor file. The moved sections still exist only in git — read them
> with `git show 892beac2^:infrastructure/state/archive/WORLDPAINT_REHEARSAL_ARCHIVE.md`.

**What is LIVE below:** §4 — what the bundle actually carries, the eleven derived mutator rules
and the two engine facts they rest on — and §7, what must not happen.

## 4. What the bundle actually carries

`world/ASHKARR_WORLDMAP_tiles.csv` — 21,872 rows, 14 columns:
`tile,lat,lon,arc,bearing,elev_m,temp_c,rain_mm,biome,water,river_flow,region,hilliness,swampiness`

    24 biomes          largest: AB_RockyCrags 4440, ExtremeDesert 3581, AridShrubland 2401
    1,780 water tiles  three connected seas
    254 river tiles    1,075 links: 238 river (Creek 103 · HugeRiver 113 · LargeRiver 12 · River 10)
                                    837 road  (DirtRoad 509 · StoneRoad 328)
    72 settlements     12 factions, most: Homestead Defense League 13, Deep Desert Tribes 9
    23 named regions   imported as WB_MapLabelFeature

### ✅ The mutator and landmark layer — added 2026-08-21, on the owner's order

`src/RimMandrake/Utils/ashkarr_populate.py` authors two more files, and `w9_run.py` gained
three stages to place them. ⛔ It is not a generator: no seed, no knobs, no way to roll a
second planet — the rules are hand-authored decisions about Ash'karr, written as code so
they are reproducible instead of re-typed.

    world/ASHKARR_WORLDMAP_mutators.csv    8,569 tiles, 9,227 placements, 11 rules
    world/ASHKARR_WORLDMAP_landmarks.csv      16 tiles   the cap from the census

**Mutators are DERIVED** — each rule restates a column the map already carries, so a mutator
is never an opinion:

| rule | from | n |
|---|---|---|
| `Sandy` | `Desert`/`AridShrubland` at hilliness ≤2 — the arid belt | 3,663 |
| `Caves` | `AB_RockyCrags` at hilliness ≥3 — the nightside floor, where rock has relief | 1,540 |
| `Dunes` | `ExtremeDesert`, flat, rain <60 mm — the rainless heart of the dayside | 1,535 |
| `Mountain` | hilliness at the top two ordinals (4, 5) | 1,459 |
| `Coast` | a land tile with ≥1 water neighbour, over the real adjacency graph | 369 |
| `River` | `river_flow` >0 — what puts the river on the LOCAL map, not just the globe | 254 |
| `Oasis` | `ZBiome_DesertOasis` inside the def's own 20–60 °C gate (39 of 227 fall outside) | 188 |
| `Cliffs` | a neighbour more than 700 m above or below | 121 |
| `HotSprings` | land bordering the volcanic province | 65 |
| `LavaFlow` | `AB_PyroclasticConflagration` | 31 |
| `RiverDelta` | a river tile touching the sea — there are exactly two mouths | 2 |

⛔ **`Marshy`, `Wetland` and `WetClimate` are deliberately absent** even though the
swampiness column would support a derivation. The census ruled them out for a planet with
no seasons and no rain, and the inventory beats a clever rule.

⭐ **This is the fix for the defect the owner named on 2026-08-17.** The world carried 5,233
`Coast`, of which 4,831 were on non-water tiles and 2,116 were deep inland — placed for the
*original* sea layout, then stranded when the repaint moved the water. Stage 3 clears them
and stage 4b recomputes them from where the water actually is.

**Landmarks are HAND-PLACED**, all 16 out of the census §7 table — `AbandonedColonyOutlander`
at The Setdown (tile 2476), `AncientQuarry` at The Ore Moot, `Valley` at The Scald Gate,
`sw_Sarlacc` at Sarlacc Ground, `AncientLaunchSite` at the Rust Cathedral, `LavaCrater` +
`LavaLake` on the Scald rim, `AncientHeatVent` ×3 on the hottest ground, `Oasis` ×6 spread
across the wells. A named place stops being a place when there are 227.

⚠️ **The salt pans are deliberately empty.** `DryLake` / `VEE_SaltPlains` may not be legal on
`Wasteland`, and a landmark that cannot fire **logs nothing** — so nothing is placed on an
unverified legality.

🔴 **Two engine facts this rests on, and the run re-proves both rather than assuming them:**

1. `AddLandmark` **ignores** `IsValidTile`. Measured 2026-08-19: on a settlement tile the
   verdict was False and it added the landmark anyway. `ashkarr_populate.py` therefore
   refuses settlement tiles *and their neighbours* itself — the first legal ring is two out,
   not the "one tile adjacent" the census assumed — and stage 4 passes `checkValid: true` so
   the engine's own verdict is recorded beside ours.
2. `AddMutator` is **expected** to ignore `biomeWhitelist` the same way. That matters because
   the shipped `Oasis` mutator whitelists `Desert`/`ExtremeDesert` only and our oasis tiles
   are `ZBiome_DesertOasis`. **Expected, not proven** — stage 4b reads the count back and §6
   carries it as decision string 8. If it reads 0, the whitelist *is* enforced and the census's
   one-line `PatchOperationAdd` is needed after all.

## 7. What must not happen

- 🔴 **No map may be instantiated — and on 2026-08-21 we found out what it costs, because
  we did it anyway.** The paint ran with `--despite-map` against a live colony. Every stage
  succeeded and the planet was faithful (seven tiles read back exact, lint 3,529 → 86). Then
  the **colony was destroyed**, the game **could no longer create a new one**, the **UI lost
  its button icons and labels**, a world remade inside that session came up **without the
  Scale 7 / Coverage 100% preset**, and the owner took the game down.
  ⚠️ Everything measured AFTER the paint in that session is unattributable — a half-broken
  game answers the bridge normally. The log harvest and the def dump were taken BEFORE it
  and stand.
  ⚠️ **Painting under a colony destroys that colony and nothing else.** `w9_run.py` refuses on
  `mapCount > 0` so a colony is never lost unasked; `--despite-map` proceeds.
- ⛔ **Do not treat this world as the campaign start.** It has no scenario embedded and its
  faction roster is the slate's 13, not the checklist's. Saving it and keeping it would
  quietly become the shipped world with two gates skipped.
- ⛔ **Do not restart the game if the bridge stops answering.** It gets stuck, not broken,
  and recovers when the other caller finishes. A restart costs 25 minutes and fixes nothing.
- ⚠️ **Delete the throwaway saves while the game is still RUNNING.** With the game down,
  Steam Cloud restores them at the next launch, original mtimes and all.
