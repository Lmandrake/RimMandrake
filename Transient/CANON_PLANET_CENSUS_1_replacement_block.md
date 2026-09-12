# CANON_PLANET_CENSUS_1 — ready-to-land replacement for canon.yml `planet:`

PREP ONLY. Not applied. canon.yml is untouched. For a BENCH sitting with the owner.

Sourcing rule followed throughout: every replacement number is cited to
`world/_audit/post_freeze_2026-09-11.json` (the offline audit against
`CANONICAL_ASHKARR_2026-09-09.rws`). A number named in the item's own 2026-09-12
addendum but NOT present in that json (see PoisonForest below) was **not** used
as a replacement — it is marked UNMEASURED instead, per the item's own sourcing
rule, and flagged as a discrepancy for the owner.

---

## (a) Exact YAML block — paste over the current `planet:` block in canon.yml

RULED rows (acceptance, names, curve, habitable ring, named_regions, start-struck)
are reproduced **verbatim, byte-for-byte**, so the paste is a complete drop-in
replacement of the whole `planet:` key, not a fragment.

```yaml
planet:
  # 🔴 THERE IS NO FROZEN WORLD — owner, 2026-08-22: "I am working with DECIDE to remake
  # the planet an entirely different way, so there is no current frozen world."
  # ⇒ Every number under `planet:` below, plus `settlements.count` and `lake_biome`,
  # MEASURES A WORLD THAT IS BEING REPLACED. They are kept, not deleted: they are the
  # record of what Ash'karr-as-painted was, and the remake will want to compare.
  # 🔑 While this reads `remaking`, check_canon downgrades every planet-derived rule to
  # ADVISORY — it reports the difference and never blocks a write. Enforcement was
  # actively refusing DECIDE's remake at the write, using the dead world's numbers.
  # ✅ Set it back to `frozen` when a new world is frozen, and the rules bite again.
  # 🔴 `remaking` IS A FOUR-STEP SEQUENCE, NOT A MOOD — owner, 2026-08-22 10:57, to REP.
  # It was being read as the binary "adopt Ash'karr or redraw it". It is neither. His words:
  #   1. "DECIDE and I have an out of game map we are working on together. It is NOT
  #      frozen/finalized" — the new map exists, OUT OF GAME, and is in progress.
  #   2. "then we need to successfully show that it can survive a port into the game
  #      through the live bridge" — 🔑 A PORT-SURVIVAL PROOF IS A GATE. Until the map has
  #      been carried in through the bridge and read back, nothing downstream is real.
  #   3. "Simultaneously, we are working to define the factions, leadernames,
  #      ideoligions, etc. because those must be finalized and correct at game initiation
  #      it turns out." — ⛔ these do NOT wait for the map. They are baked at initiation and
  #      cannot be retrofitted, so they run in PARALLEL with steps 1-2.
  #   4. "Once all that is done, then we can finally save a game and meaningfully freeze
  #      it as the embodied world."
  # ⇒ 🔑 **THE FREEZE IS A SAVEGAME.** Not a CSV, not a definition doc, not an approval of a
  # render. Nothing is frozen until a game has been saved with the map ported, the factions
  # settled and the ideoligions correct. Any doc that calls an artifact short of that "the
  # frozen world" is wrong, and that is what this field exists to say.
  # ✅ Set it back to `frozen` when step 4 has happened — a saved game, on disk — and the
  # planet rules bite again.
  status: remaking
  # ⭐ THE MAP STANDS — owner, 2026-08-23, answering CANON_SUSPENDED_FOR_REMAKE_1.
  # Asked whether the hand-remake was still happening, he chose "the current map stands".
  # ⇒ 🔑 EVERY NUMBER UNDER `planet:` IS LIVE AGAIN. The comment above says they "MEASURE A
  # WORLD THAT IS BEING REPLACED" — that is NO LONGER TRUE and must not be quoted forward.
  # Ash'karr as painted, including the nightside layering of 2026-08-23
  # (ashkarr_layer_nightside.py), IS the v1 planet. Nothing here is a record of a dead world.
  # ⛔ BUT `status` STAYS `remaking`, and that is deliberate, not an oversight. The owner's
  # own four-step sequence above makes THE FREEZE A SAVEGAME: map -> port-survival proof
  # through the live bridge -> factions/leader names/ideoligions correct at initiation ->
  # save the game. Step 1 is now settled; steps 2-4 have not happened. Setting `frozen`
  # here would assert a saved world that does not exist.
  # ✅ What changed in practice: check_canon's planet rules stay ADVISORY, but their reports
  # are now MEANINGFUL rather than misleading — they compare against the live planet.
  # 🔑 Flip to `frozen` when a game has been SAVED with the map ported. Not before, and not
  # on the strength of a render or a CSV.
  status_src: >
    Owner, 2026-08-22, to REP. Supersedes WORLD_FROZEN_RETHINK_PLANET_1 and every doc
    saying the planet is frozen as-is for v1. The ACCEPTED_ON/ACCEPTED_BY fields below
    describe the superseded world and are left untouched for the same reason.
    Extended 2026-08-22 10:57 with the owner's own sequencing, quoted in the comment
    above: out-of-game map -> port-survival proof through the live bridge -> factions,
    leader names and ideoligions correct at initiation (in parallel) -> save the game,
    and THAT is the freeze.
  name: "Ash'karr — The Sundered"

  # ⭐ ACCEPTED FOR V1 — owner, 2026-08-20, after looking at the ortho globes.
  #   "Let's go with the globe map you made for v1. Map accepted."
  # 🔑 THE SHAPE OF THE PLANET IS SETTLED — and as of 2026-08-22 the map is ADOPTED.
  # Owner, on the four-globe sheet: "That world, upon examination, really isn't very bad at
  # all... we're thinking of trying to adopt it." ⇒ Ash'karr as it stands IS the v1 planet.
  # ✅ POPULATING IT IS OPEN AGAIN: landmarks, named places, settlements, terrain detail,
  # river and road continuity — edited DIRECTLY, in place, one map.
  # ⛔ Still closed: regenerating the bundle with ashkarr_paint.py, the reference-match
  # harness, and worldgen in any version. See ORTHO_GLOBE_MAP_ACCEPTED_1 below.
  # ⛔ Do not re-open geometry, water fraction, sea count or the temperature curve as
  # "improvements". They are accepted, not merely current.
  accepted_for_v1: true
  accepted_on: 2026-08-20
  accepted_by: owner
  accepted_evidence: "TRANSIENT_refmatch_globes.html — three ortho globes beside the two reference photographs"

  tiles: 21872
  tiles_src: >
    world/ASHKARR_WORLDMAP_tiles.csv has 21872 data rows; world/ASHKARR_WORLDMAP_meta.json
    "tiles": 21872. Measured 2026-08-20, the two agree.
    🔴 RECONFIRMED by world/_audit/post_freeze_2026-09-11.json verdict "total_world_tiles"
    (MEASURED-ok): 21872 in the save (tileBiomeDeflate 43744 bytes / 2), 21872 CSV rows,
    21872 here — three-way agreement against CANONICAL_ASHKARR_2026-09-09.rws. Unchanged.

  water_tiles: 1448
  water_src: >
    world/_audit/post_freeze_2026-09-11.json verdict "water_tiles" (MEASURED-ok vs CSV):
    1448 tiles at elev<=0 in CANONICAL_ASHKARR_2026-09-09.rws; 1448 in the frozen CSV by
    the same test; 1448 tiles carrying a water BiomeDef — three independent asks, one
    answer.
    🔴 SUPERSEDES the 2026-08-22/23 liquid/ice split entirely (water_tiles 1135 +
    water_ice_tiles 277 = 1412 = water_pct 5.19% / 6.46% incl-ice) — that whole framing is
    the deprecated 2026-08-23 painted-lineage capture and is DELETED, not kept alongside
    (see (c) below). The audit gives one unified count, not a liquid/ice split.
    ⚠️ water_pct is UNMEASURED — not in post-freeze audit: the audit states tile counts
    only, no percentage, and this task's sourcing rule does not permit back-computing one
    (1448/21872) as a "replacement number" not itself present in the cited json. Add it
    only as its own measured/cited row if the owner wants it re-derived properly.

  # The substellar point is the origin of everything: this world is tidally locked
  # and does not rotate, so there is no day, no season and no latitude gradient.
  # ⚠️ ARC — angular distance from the substellar point — IS THE AXIS, not latitude.
  # Correlation of temperature against arc is −0.98 on the painted world
  # (src/RimMandrake/Utils/ashkarr_paint.py:13). Any document reasoning from
  # latitude is reasoning about a planet that spins, and this one does not.
  substellar: [0.0, 0.0]
  axis: arc
  axis_src: "src/RimMandrake/Utils/ashkarr_paint.py:13 — corr −0.98 on the painted world"

  lapse_c_per_km: 5.5
  temp_curve_c: {0: 70, 30: 58, 60: 38, 90: 14, 120: -22, 150: -58, 180: -80}
  temp_curve_src: >
    src/RimMandrake/Utils/ashkarr_paint.py:796 `temperature_curve()`, whose docstring
    reads "Owner's ruled endpoints: +70 C at the substellar point, +14 C at the
    terminator, -80 C in deep night, minus an altitude lapse of 5.5 C/km." These are
    the RULED endpoints and they are what the painter interpolates. Not a target.
  temp_curve_realised_median_c: {0: 61.6, 30: 56.8, 60: 35.5, 90: 13.0, 120: -25.5, 150: -61.4, 180: -80.0}
  temp_curve_realised_src: >
    Median painted temp_c of every tile within ±2° of each anchor, 2026-08-20. It sits
    BELOW the ruled curve everywhere land rises, because the 5.5 °C/km lapse is
    subtracted per tile. 🔑 The ruled curve and the realised medians are not in
    conflict and neither supersedes the other — quote the ruled curve when stating
    design intent, the realised medians when predicting what a tile will feel like.
  terminator_c: 14
  terminator_src: "arc 90 on the ruled curve above; realised median +13.0 °C after lapse."

  seas: 3
  sea_names: ["The Scald", "The Twilight Sea", "The Gray Sea"]
  seas_src: >
    world/_audit/post_freeze_2026-09-11.json verdict "seas" (MEASURED-ok on count,
    MISMATCH on sizes): 3 named seas present and painted — RUT_TheScald 312,
    RUT_TwilightSea 607, RUT_GreySea 472. Satisfies the_one_map.md:100 "Exactly three
    connected bodies"; the count of 3 holds and is unchanged.
    🔴 SUPERSEDES the sizes "312, 851 and 617" sourced here since 2026-08-23 — those are
    the deprecated painted-lineage capture and are DELETED (see (c) below).
    ⭐ A fourth body, RUT_PropaneLake (57 tiles), is also on the map per the same audit
    but is not one of the three NAMED seas — see biome_tile_counts.
    Vanilla Ocean/Lake/SeaIce/IceSheet are all at 0 tiles per the same audit, "as the
    2026-09-07 rulings intended" — see biome_tile_counts.

  named_regions: 24
  named_regions_src: "meta.json regions[] — 24 names; 23 carry tiles, `The Ashteeth` carries ZERO."
  # ⚠️ world/_audit/post_freeze_2026-09-11.json verdict "named_regions" measured 71 WorldFeature
  # elements / 71 CSV region names, with 809 tiles carrying a renamed region (775 clean
  # 1:1 renames the CSV never received, plus a genuine 34-tile boundary change). The audit
  # itself says this is a DIFFERENT question from named_regions=24 here (meta.json design
  # regions, not save WorldFeatures) and NOT a mismatch against this row. Left untouched.

  rivers_tiles: 254
  rivers_tiles_src: >
    UNMEASURED — not in post-freeze audit. This row has carried NO citation since it was
    written (world/_audit/post_freeze_2026-09-11.json calls it out by name as "the only
    planet figure in the block with no provenance"). The audit tried three offline reads
    and none produced 254: 326 river edges over 217 distinct origin tiles (Creek 170,
    River 62, HugeRiver 51, LargeRiver 43); CSV river_flow non-zero on 298 tiles. The
    engine's "tiles with a river" needs the icosphere adjacency resolved at runtime via a
    jawa/world_* bridge read, which the audit says would finally give this row a citation.
    Not replaced here — no post-freeze number to cite. Flagged for the owner rather than
    forced; the existing 254 is neither confirmed nor contradicted, only unprovenanced.

  rain_mm: {min: 0, median: 0, max: 1529}
  rain_src: >
    world/_audit/post_freeze_2026-09-11.json verdict "biome_census_vs_canon": rain_mm.max
    1668 (here since 2026-08-21) vs measured 1529 — 1668 was a misread of the same,
    unchanged CSV data; 1529 is the correct figure. 🔴 SUPERSEDES the 1668 max only.
    ⚠️ min:0/median:0 are UNCONFIRMED by this audit (it does not restate them) but are
    NOT contradicted either — the audit's separate "temperature_rainfall_swampiness_per_tile"
    verdict (MEASURED-ok) found 0/21872 tiles differ on rainfall between the CSV and
    CANONICAL_ASHKARR_2026-09-09.rws, i.e. the same underlying data the 2026-08-21 pass
    read. That pass's other figures (over the 1,396 tiles that carry rain: min 18,
    median 60, max was misread as 1668) are carried forward unconfirmed, not re-verified
    row-by-row here.
    🔑 0 is not "very dry", it is BANNED: every rain WeatherDef's commonalityRainfallFactor
    curve starts at (0, 0), so at 0 the commonality is multiplied by exactly zero and the
    weather can never be selected. The 191 tiles at the old (wrong) ceiling sit at
    hilliness 4-5, which the 2026-08-21 ruling explicitly keeps; that ruling is unaffected
    by the max correction.

  start_tile: null          # ⛔ STRUCK 2026-08-24 - was 2476
  start_name: null          # ⛔ STRUCK 2026-08-24 - was "The Setdown"
  start_struck: >
    🔴 Owner, 2026-08-24: "There is no canon start colony for the player yet, strike that
    from the lore docs." The Setdown siting is WITHDRAWN, not merely superseded - nothing
    on the map is the player's home. ⚠️ ashkarr_paint.py still carries HOME_LATLON /
    HOME_NAME and ABORTS if that lat/lon stops being ExtremeDesert; ashkarr_populate.py
    and ashkarr_repair.py still place an AbandonedColonyOutlander landmark at/next to
    2476. Those are stale, not authoritative, and were left running rather than ripped out
    without a ruling. See ASHKARR_WORLD_DEFINITION.md §7b.
  start_src: >
    meta.json start{}; sited 2026-08-19 and argued at ashkarr_paint.py:74-95. arc 56.9,
    bearing 358.8, ExtremeDesert, 276 m, 38.6 °C, 18 mm, nearest standing water 26° away.

  habitable_ring_arc: [40, 57]
  habitable_ring_src: >
    🔴 OWNER RULING, 2026-08-21: "Select 40-57 habitable ring." Asked as
    needs_ruling.HABITABLE_RING_ARC_RULING_1, abstained on 2026-08-20, ruled the next
    day. This value is RULED, not measured — it does not need a citation behind it and
    nothing may reopen it on evidence.
    🔑 This band is a DESIGN band, not a settlement census: the settlements span far wider
    than it and always have. ⚠️ RE-MEASURED 2026-08-23 — **120** settlements spanning arc
    19 to 116 (median 69); the note used to read "72 settlements, arc 10.0 to 104.6" and
    that count is superseded. **The conclusion is unchanged and is the point of this note:
    do not "correct" the ruled band against the census, in either direction.**
    ⚠️ The arc-34–40 band, ~700 tiles, is MARGIN and not habitable. That is the whole
    practical consequence of the ruling.
    ✅ The Setdown does not move. It sits at arc 56.9 and is called "the outer edge of
    the habitable ring", which reads true under either arc — 56.9 is inside 57 both
    ways. A propagation edit that moves the start tile is wrong.
    Propagation into the files that still say 34–57 is HABITABLE_RING_IS_40_57_1.
  habitable_ring_superseded:
    - value: "[34, 57]"
      why: >
        Held as canon-provisional until 2026-08-21, on the strength of
        ashkarr_paint.py:76-77 ("the habitable ring is ~34-57 degrees of arc") and the
        siting argument built on it. ⛔ OVERRULED BY THE OWNER. It was the stronger
        EVIDENCE and it still lost, which is correct: this is a design decision about a
        hand-made world, not a finding. Still asserted at
        ASHKARR_WORLD_DEFINITION.md:237 and fauna_placement.md:13 until that item runs.

  biomes_on_map: 29
  biomes_on_map_src: >
    world/_audit/post_freeze_2026-09-11.json verdict "biome_per_tile" (MEASURED-ok): 0 of
    21872 tiles differ between the frozen CSV and CANONICAL_ASHKARR_2026-09-09.rws; 29
    distinct biome shortHashes, 0 unresolved against the def dump; biomes_on_map=29 both
    sides. 🔴 SUPERSEDES the 2026-08-23 DECIDE re-derivation (28) — the deprecated
    painted-lineage capture.
    ⚠️ UNRECONCILED, flagged rather than forced: biome_tile_counts below cannot be summed
    to 29 from this audit alone. The audit names fresh counts for only 9 nonzero biomes
    (Desert/ExtremeDesert/Wasteland plus the six new RUT_* rows) plus 4 vanilla water
    biomes now at 0 (no longer "on the map"); naively removing those 4 zeroed biomes from
    the old 28-row list and adding the 6 new RUT_* rows gives 30, not 29 — one short of
    reconciling. The other ~21 legacy biome rows (AB_RockyCrags, AB_MycoticJungle,
    AridShrubland, PoisonForest, AB_PropaneLakes, ZBiome_Badlands,
    AB_FeraliskInfestedJungle, HorrorWastes, BMT_FungalForest, AB_MechanoidIntrusion,
    ZBiome_Grasslands, ZBiome_DesertOasis, BMT_CrystalCaverns, AB_GelatinousSuperorganism,
    Scarlands, AB_MiasmicMangrove, AB_TarPits, AB_PyroclasticConflagration, Volcano,
    LavaField, AB_OcularForest) have no fresh count in this audit and are not carried
    forward as numbers (their old values are the same deprecated 2026-08-23 capture as
    everything else in this block) — see (b)/(c). A likely explanation for the off-by-one
    is a RUT_-tier rename of one legacy biome def, not resolvable from this audit; a full
    per-biome re-census against the frozen CSV would close it.

  biome_tile_counts:
    # 🔴 REBUILT from world/_audit/post_freeze_2026-09-11.json ONLY — every row below has
    # a citation in that json. The full 2026-08-23 table (28 rows) is DELETED outright,
    # not superseded-in-place (see (c)); it is the deprecated painted lineage the item
    # names. ~21 legacy biome names are known to still exist on the map (biomes_on_map=29
    # vs 13 rows below of which 4 are zero) but have no post-freeze count and are
    # deliberately NOT re-listed with stale numbers — see biomes_on_map_src above and the
    # delta table in (b). This table is INCOMPLETE by design pending that re-census.
    Desert: 2390
    ExtremeDesert: 3969
    Wasteland: 1853
    RUT_TheScald: 312
    RUT_TwilightSea: 607
    RUT_GreySea: 472
    RUT_BlueDesert: 1029
    RUT_NightsideIce: 1506
    RUT_PropaneLake: 57
    Ocean: 0
    Lake: 0
    SeaIce: 0
    IceSheet: 0
  biome_tile_counts_src: >
    world/_audit/post_freeze_2026-09-11.json verdict "biome_census_vs_canon": Desert
    2390 (was 4648), ExtremeDesert 3969 (was 3214), Wasteland 1853 (was 1721); "no row for
    RUT_TheScald 312, RUT_TwilightSea 607, RUT_GreySea 472, RUT_BlueDesert 1029,
    RUT_NightsideIce 1506, RUT_PropaneLake 57"; "carries Ocean 823/Lake 312/SeaIce
    277/IceSheet 80 which are all now 0" (verdict "seas": "as the 2026-09-07 rulings
    intended"). PoisonForest is deliberately NOT restated at its old value (604) — that
    number is the deprecated painted lineage per CANON_PLANET_CENSUS_1's 2026-09-12
    addendum, and the addendum's own replacement (546, "frozen CSV, 2026-09-11") is NOT
    present in this json, so it is not used here — see (b) discrepancy list.
```

---

## (b) Delta table — old → new, per row, with `_src`

| row | old (painted lineage / canon.yml today) | new | `_src` | status |
|---|---|---|---|---|
| `tiles` | 21872 | 21872 (unchanged) | post_freeze json `total_world_tiles` | RECONFIRMED |
| `water_tiles`+`water_ice_tiles` | 1135 + 277 = 1412 | 1448 (unified, split retired) | post_freeze json `water_tiles` | REPLACED |
| `water_pct` / `water_pct_incl_ice` | 5.19 / 6.46 | — | not in json | DELETE, mark UNMEASURED if wanted |
| `seas` sizes (in `seas_src`) | 312, 851, 617 | 312, 607, 472 | post_freeze json `seas` | REPLACED |
| `seas` count | 3 | 3 (unchanged) | post_freeze json `seas` | RECONFIRMED |
| `rivers_tiles` | 254 (no `_src` ever) | 254 (unchanged, now flagged) | none in json (UNMEASURED) | FLAGGED, not replaced |
| `rain_mm.max` | 1668 | 1529 | post_freeze json `biome_census_vs_canon` | REPLACED |
| `rain_mm.min` / `.median` | 0 / 0 | 0 / 0 (unchanged) | not restated in json; not contradicted | CARRIED FORWARD unconfirmed |
| `biomes_on_map` | 28 | 29 | post_freeze json `biome_per_tile` | REPLACED |
| `biome_tile_counts.Desert` | 4648 | 2390 | post_freeze json `biome_census_vs_canon` | REPLACED |
| `biome_tile_counts.ExtremeDesert` | 3214 | 3969 | post_freeze json `biome_census_vs_canon` | REPLACED |
| `biome_tile_counts.Wasteland` | 1721 | 1853 | post_freeze json `biome_census_vs_canon` | REPLACED |
| `biome_tile_counts.Ocean` | 823 | 0 | post_freeze json `seas` | REPLACED (effectively delete — no longer on map) |
| `biome_tile_counts.Lake` | 312 | 0 | post_freeze json `seas` | REPLACED (effectively delete) |
| `biome_tile_counts.SeaIce` | 277 | 0 | post_freeze json `seas` | REPLACED (effectively delete) |
| `biome_tile_counts.IceSheet` | 80 | 0 | post_freeze json `seas` | REPLACED (effectively delete) |
| `biome_tile_counts.RUT_TheScald` | (absent) | 312 | post_freeze json `seas` | ADDED |
| `biome_tile_counts.RUT_TwilightSea` | (absent) | 607 | post_freeze json `seas` | ADDED |
| `biome_tile_counts.RUT_GreySea` | (absent) | 472 | post_freeze json `seas` | ADDED |
| `biome_tile_counts.RUT_BlueDesert` | (absent) | 1029 | post_freeze json `biome_census_vs_canon` | ADDED |
| `biome_tile_counts.RUT_NightsideIce` | (absent) | 1506 | post_freeze json `biome_census_vs_canon` | ADDED |
| `biome_tile_counts.RUT_PropaneLake` | (absent) | 57 | post_freeze json `biome_census_vs_canon` | ADDED |
| `biome_tile_counts.PoisonForest` | 604 | — | addendum cites 546 but NOT in json | **DISCREPANCY — see below, marked UNMEASURED, not restated** |
| `biome_tile_counts.{other 20 rows}` | AB_RockyCrags 3816, AB_MycoticJungle 1939, AridShrubland 709, AB_PropaneLakes 554, ZBiome_Badlands 545, AB_FeraliskInfestedJungle 534, HorrorWastes 468, BMT_FungalForest 425, AB_MechanoidIntrusion 236, ZBiome_Grasslands 233, ZBiome_DesertOasis 227, BMT_CrystalCaverns 127, AB_GelatinousSuperorganism 96, Scarlands 90, AB_MiasmicMangrove 65, AB_TarPits 57, AB_PyroclasticConflagration 31, Volcano 23, LavaField 15, AB_OcularForest 3 | — | none in json | **UNMEASURED — not in post-freeze audit; not restated (all are the same deprecated 2026-08-23 capture); need a fresh per-biome re-census against the CSV** |

**20-row count, not counting PoisonForest separately**: 20 legacy biome rows carried NO replacement number (PoisonForest makes 21 total unresolved legacy rows).

---

## (c) Rows to DELETE outright (delete-don't-supersede)

- `water_pct: 5.19`
- `water_ice_tiles: 277`
- `water_pct_incl_ice: 6.46`
- `water_superseded:` (the whole 3-entry list — 25%/22-28%, 8.6%, 6.9% history)
- `seas_src`'s old sizes text "312, 851 and 617" (folded into the row's rewrite above, not left as a superseded-list entry)
- The entire old `biome_tile_counts:` block (28 rows: Desert 4648, AB_RockyCrags 3816, ExtremeDesert 3214, AB_MycoticJungle 1939, Wasteland 1721, Ocean 823, AridShrubland 709, PoisonForest 604, AB_PropaneLakes 554, ZBiome_Badlands 545, AB_FeraliskInfestedJungle 534, HorrorWastes 468, BMT_FungalForest 425, Lake 312, SeaIce 277, AB_MechanoidIntrusion 236, ZBiome_Grasslands 233, ZBiome_DesertOasis 227, BMT_CrystalCaverns 127, AB_GelatinousSuperorganism 96, Scarlands 90, IceSheet 80, AB_MiasmicMangrove 65, AB_TarPits 57, AB_PyroclasticConflagration 31, Volcano 23, LavaField 15, AB_OcularForest 3) — replaced by the rebuilt 13-row table in (a). Git carries the provenance; nothing here is "superseded-in-place".

Not deleted (RULED, unaffected, kept verbatim): `status`/`status_src`, `name`, `accepted_*`, `substellar`/`axis`/`axis_src`, the whole temperature-curve group (`lapse_c_per_km` through `terminator_src`), `named_regions`/`named_regions_src`, `start_*`, `habitable_ring_*`.

Not deleted but flagged, not replaced (no post-freeze number exists): `rivers_tiles` (254, unprovenanced).

---

## (d) One-line census-source ruling — draft, awaiting the owner's yes

> **RULING (draft):** `world/ASHKARR_WORLDMAP_tiles.csv` (frozen 2026-09-11, verified 0/21872 tiles differing from `CANONICAL_ASHKARR_2026-09-09.rws`) is the sole census source for the Ash'karr planet; the V26 live census (owner-accepted 2026-09-08, PoisonForest 557) and the 2026-08-23 painted-lineage counts (PoisonForest 604, and all other now-superseded `biome_tile_counts` rows) are both superseded — their numbers are **deleted**, not kept alongside, closing the three-way disagreement everywhere it appears.

---

## Discrepancies for the owner (do not force)

1. **PoisonForest**: the item's own 2026-09-12 addendum names 546 as the frozen-CSV figure ("PoisonForest is 546 (frozen CSV, 2026-09-11)"), but **546 does not appear anywhere in `world/_audit/post_freeze_2026-09-11.json`** — that json never mentions PoisonForest by name. Per this task's sourcing rule ("numbers you cannot find in that json are NOT invented"), 546 was not used as a replacement; the row is left out of the rebuilt table entirely rather than either keeping 604 (known-stale) or writing an uncited 546. The owner should say whether 546 gets its own citable audit entry before landing, or whether the addendum text itself is authorization enough to write it in.
2. **biomes_on_map=29 does not reconcile against biome_tile_counts**: the json directly confirms the total (29), but only 13 rows (9 nonzero + 4 now-zero) have post-freeze numbers. Naive arithmetic on the old 28-row table (−4 zeroed vanilla biomes, +6 new RUT_* rows) gives 30, not 29 — one short. ~21 legacy biome rows have no fresh count and were deliberately left out rather than restated stale. Likely cause: a RUT_-tier rename of one legacy biome def (see CLAUDE.md's three-tier naming migration), not resolvable from this audit alone.
3. **`rivers_tiles: 254`** has never carried a citation and the audit's three offline reads (326 edges / 217 origins / 298 CSV-nonzero tiles) don't match 254 or each other closely enough to replace it — flagged, not touched, per the audit's own recommendation that it needs a live `jawa/world_*` bridge read.
4. **`water_pct` / `water_pct_incl_ice`** have no post-freeze percentage figure (only tile counts); deleted rather than back-computed from 1448/21872, since that arithmetic isn't itself a number present in the cited json.
5. **`rain_mm.min`/`.median`** (0/0) are carried forward unconfirmed — not restated in the json, but not contradicted either (the audit's per-tile rainfall check found 0/21872 differences on the same underlying CSV).
