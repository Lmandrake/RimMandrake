
## spec

Owner answered 'Queue all' on a question card 2026-10-08 (decision taken by question card) for the remaining work of `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md`. Row X-10 there is the spec:

| X-10 | **"Taken by the land, comes back later" becomes one service.** The gale carry and FlowWorks' swept-away are the same mechanism built twice: a hold, a letter, a return. The spot where a pawn was taken gets a ground trace, so no one vanishes without a readable sign. | shared record + return + letter; a Traces prop when EVENT_TRACE_PROPS_LIBRARY_1 lands | M | low | Stillsand, FlowWorks, Traces | `RM_WorldComponent_SweptAway`, `RM_DuneGale`. Traces is still a spike |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; names follow the three-tier scheme.

## verify

Record each owed criterion with `rimflow verify TAKEN_BY_LAND_SERVICE_1 --criterion <ID> --result pass|fail|partial --config <list> --evidence <path>`:
- A2 (L1): taken_by_land.service_has_river_policy_and_trace_setting reads river policy registered and the trace setting;
- A3 (L2): a pawn swept off the river edge and a pawn carried off by a gale each get a letter, a drag mark where they sto
Evidence is the Player.log line or bridge state read the criterion names.
