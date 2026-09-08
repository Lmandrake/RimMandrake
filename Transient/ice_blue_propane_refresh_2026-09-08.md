# Ice/Blue/Propane biome sheet stat refresh — 2026-09-08

Reconstructed current biome-per-tile state from `world/ASHKARR_WORLDMAP_tiles.csv`
overlaid, in order, with `backside_reband_full.json` → `pf_terminator_plan.json` →
`wasteland_reclaim_plan.json` → `crag_meander_plan.json` → `pf_meander_plan.json` →
`graycrags_coldonly_plan.json` (last write wins on `to`/`biome`). Confirmed headline
counts before editing: RUT_NightsideIce 1,406, BiomeGRimond 1,029, AB_PropaneLakes
2,531, RUT_PropaneLake 57 (unchanged — 100% of its tiles trace to the raw CSV, none of
the six plans touch it). All four defs' tiles are max-temp < 0 °C (via the seasonal
curve); AB_PropaneLakes' mean temps are all < −42 °C. Confirmed all RUT_NightsideIce /
BiomeGRimond / AB_PropaneLakes tiles derive entirely from the overlay plans, none from
the raw CSV's own biome column (i.e. `backside_reband_full.json` is a full repaint of
those defs' current footprint, further edited by the later plans).

## nightside_ice.md
- §0 measurement paragraph rewritten: 802 → 1,406 tiles, with provenance by plan
  (`backside_reband_full` 1,044 + `wasteland_reclaim_plan` 243 + `pf_terminator_plan`
  98 + `crag_meander_plan` 21); arc 128→159 → 111→139; temp p10/median/p90
  −70/−56/−39 → −45/−32/−22 °C; elevation median 1,129 → 748 m (max unchanged, 1,884);
  region list fully replaced. MEASURED tag → 2026-09-08 (V18 canon). Old 802-tile
  breakdown sentence kept, past tense, as history.
- Contradiction-amendment added under §2's "arc 128–159" ruling claim (verbatim):
  > ⚠️ MEASURED 2026-09-08 (V18 canon): arc now 111→139 (was 128→159) — the highland's
  > lower bound has moved into ground §2 elsewhere calls twilight (the crags: arc
  > 103–121); amendment — ruling text stands.

## the_blue_desert.md
- The existing 2026-09-07 amendment card (BiomeGRimond painted-tile stats) refreshed
  in place: 1,328 → 1,029 tiles; region list recomputed (10 regions, was 8); arc
  p10/med/p90 126.7/137.1/148.8 → 124.6/134.7/143.2; temp med −45.3 → −42.6 °C; elev
  med 597 → 640 m. MEASURED tag → 2026-09-08 (V18 canon).
- Contradiction-amendment added under the "Nightside ladder: Rot −19 → Blue Desert
  −44 → PropaneLakes −64" ruling clause (verbatim):
  > ⚠️ MEASURED 2026-09-08 (V18 canon): current median temps on the ladder's lower two
  > rungs are **Blue Desert (`BiomeGRimond`) −42.6 °C → PropaneLakes (`AB_PropaneLakes`)
  > −62.2 °C** — the ordering holds, the exact figures have drifted with repainting;
  > amendment — ruling text stands.

## the_propane_lakes.md
- The existing 2026-09-07 amendment card (tile-count drop/region reshuffle)
  refreshed in place with a new 2026-09-08 card layered on top: AB_PropaneLakes
  987 → 2,531 tiles; arc p10/p90 135.2/165.5 → 139.3/166.0; temp p10/median/p90
  −72.0/−60.8/−44.8 → −73.0/−62.2/−47.8 °C; coldest tile −80.8 → −81.7 °C; elevation
  median 638 → 670 m; region list fully replaced (Deadstone now plurality at 861,
  ahead of Umbra 773 and Ammonia Flats 692 — a further rank swap vs the 2026-09-07
  card). No prose-ruling contradiction flagged beyond what the card itself states as
  amendment. RUT_PropaneLake re-verified at 57 tiles, water=1 all, Umbra 29/Ammonia
  Flats 28 — already correct, no numeric edit needed (noted in the new card as
  "re-verified unchanged").

## Verification
Re-ran the reconstruction script after editing and diffed every number written
against the script's output; all match exactly (temp/elevation figures rounded to
the same precision the sheets already used — whole °C / whole m, arc to 1 decimal
where the sheet already carried a decimal, integer tiles).

## UNKNOWN
None — all four headline counts and every stat line touched were independently
recomputable from the CSV + six overlay plans.
