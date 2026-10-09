
## spec

Owner answered 'Queue all' on a question card 2026-10-08 (decision taken by question card) for the remaining work of `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md`. Row X-11 there is the spec:

| X-11 | **A particulate screen stops spore clouds** as well as aerosol. Plausible and cheap, and it makes the Scarlands screen useful in the rot groves. | `Gas_Damaging` damage path asks `RM_CompAerosolScreen.IsPositionScreened` | S | low | Scarlands, TheRot, EnvironmentalHazards | the screen registry is static and public. The spore gas never asks it |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; names follow the three-tier scheme.

## verify

Record each owed criterion with `rimflow verify SCREEN_STOPS_SPORES_1 --criterion <ID> --result pass|fail|partial --config <list> --evidence <path>`:
- A1 (L1): screenStopsSporesEnabled readable and Gas_Damaging branches on it (map_mechanics.gas_screened_by_aerosol_scree
- A2 (L2): a spore cloud next to a built Scarlands aerosol screen does nothing inside the dome and still hurts outside it
Evidence is the Player.log line or bridge state read the criterion names.
