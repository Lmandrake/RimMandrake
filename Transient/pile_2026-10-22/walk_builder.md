# walk_builder — BENCH walkthrough builder progress (2026-10-22)
## 1. Map R builder (C1, C11) — DONE offline (pushed 7517bbf820)
- `scenarios_map.py --river --build --fresh-map` founds map R as a 2nd map (map C + colonists kept), builds C1+C11, 3 drafted colonists, labels+signs, writes review/scenarios/map_r_placed.json; `--river --goto C1|C11|R1..R8`, `--river --labels`; map-C goto/labels/save switch back to map C.
- Added DB drawbridge picture row on map C (timber/steel x lowered/raised + 2 closed gates) at (64,168); `--goto DB`.
- --mock: map C 10/10, map R C1 OK + C11 8/8, rc 0; selftest_scenarios_map ALL PASS. Live founding UNTESTED (needs the game).
## 2. Sign/keysheet truth pass — DONE (444af8cdea, be9b0277f3)
- common RULINGS/GIRTH_NOTE; C1 C3 C5 C6 C7 C12 texts; C2 via side clone (fixer B's moat edit left uncommitted in bench). C4/C10 untouched (fixer B). Keysheet regenerates at the live build.
## 3. Walk script + JSON — DONE
- Transient/pile_2026-10-22/walk_tonight.md + walk_tonight.json: 11 stops (1 conditional overflow), 27 decisions, ~44 min. Route C3 > C12 > C2 > DB > C5 > C7 > C4 > map R C1 > C11.
- C3 now stages three TURNED reels (N/E/S) for stop 1 (93d5343eab).
## 4. Rebuild procedure — DONE (top of walk_tonight.md, 11 steps)
## Commits — none yet

### 1 notes (13:xx)
- Existing: scenarios_map.py --river --build ran run_river on the CURRENT map only; map founding lived in river_site.py, which
  VANISHES map C's colonists + bland reset (unfit inside the walkthrough save). Also clear_plots painted Soil over C1's
  rect +6 rows north = the river intake row (would kill the bank). Map R labels: the sign sidecar holds ONE map's labels.
- Plan: --river --build --fresh-map founds map R as a 2nd map in the same game (river_site helpers, no vanish), builds C1+C11,
  writes review/scenarios/map_r_placed.json (map ids + C1 + stations); --river --goto/--labels; map-C --goto/--save switch back.
