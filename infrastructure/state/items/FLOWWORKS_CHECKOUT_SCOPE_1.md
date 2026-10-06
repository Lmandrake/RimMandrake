# FLOWWORKS_CHECKOUT_SCOPE_1 — ordinary FlowWorks features sit outside the basic checkout

Found by the 2026-10-06 northstar review (`design/RimMandrake/northstar_review_2026-10-06.md` finding 7, GPT action 7),
CONFIRMED by reading the walk:

1. **Scope.** The walk's step 4 puts doors, spikes, ladders OFF, the superdeep prison room + capture down + lip service,
   the pump, bottle revert, wall faces, dig finds, bottles/tanks/drilling, shores, river steam and fire extinguishing in
   `extension_proof.py` "on request, never by the core proof". The owner's 2026-10-04 ruling (debug_process §6b) reserves
   "extended" for mod-mod compatibility, declared incompatibilities and removal — not ordinary Utinni-play features. So a
   green core proof (59/59 PASS, `validation_v2_result_20261005T232201.json`) says nothing about those features.
2. **Coverage arrows.** The walk's five `## must be true` lines carry no `→` arrow (§2.3). Proposed mapping, from the
   59 row ids of tonight's result — UNVERIFIED, check each against the row's predicate before writing it:
   - designation + colonist digs → `E8_player_dig`, `J_workgiver_selection`, `J_orders_accepted`
   - D=1..4 terrains → `S1_dig_ladder`, `S1n_superdeep_is_max`
   - channel-constrained spread, default on → `E2_dry_ring`, `E2_channels_fill_every_direction`
   - underlying terrain recoverable after a flood → no matching row found (UNCOVERED, or the line describes the retired Flood engine)
   - flood expiry at 2×FloodingTicks → no matching row found (same question)

NEXT: decide per feature in step 4 whether it is basic (move its chain into the core proof) or extended (name the §6b reason on its E-line), then write the five arrows.
