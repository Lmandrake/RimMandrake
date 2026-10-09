# GREYSEA_FLOOR_WALKABLE_CHECK_1 — DI-6: final walkability pass after Grey Sea floor decoration

## spec

Filed from `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` (remaining rows, helper pass 2026-10-09; owner 'Queue all' card 2026-10-08). Row DI-6 there is the spec; its 'Checked' column says what was read to confirm it is unbuilt. Re-check src before building.

| DI-6 | *(robustness)* The Grey Sea floor stays walkable after decoration. A final check after the pillar, dome, chimney, statuary and crystal scatters opens a path from the landing area to the wrecks and Elders, or removes the blocking piece. | One last GenStep running a reachability flood from the landing zone. | S–M | low | DivingInteraction, TerminalBiomes (`RM_GreySeaFloorScatter.xml`) | the connectivity test (`GenStep_SeaFloorTerrain.cs:176`, `minConnectedShare`) runs on terrain only; `RM_SeabedGenerators.xml` Grey Sea runs 8 scatter steps plus a wreck field after it, with no later reach check |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; names follow the three-tier scheme.

## verify

Record each owed criterion with `rimflow verify GREYSEA_FLOOR_WALKABLE_CHECK_1 --criterion <ID> --result pass|fail|partial --config <list> --evidence <path>`:
- A1 (L1): on a generated Grey Sea floor, flooding from the map centre reaches a cell beside every Brine Elder and grey-f
Evidence is the Player.log line or bridge state read the criterion names.
