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

## done (2026-10-11, offline, L0)
- **Scope decided by the §6b ruling itself, feature by feature:** every step-4 chain (fire reaching a reservoir, fire put out
  by explosion/foam/rain, doors, spikes, ladders OFF, prison room + capture down + lip service, pump, bottle revert, wall
  faces, dig finds, bottles/tanks/drilling, shores, river steam, swale, the visual-trial plots) is ordinary Utinni play, and
  none is mod-mod compatibility, a declared incompatibility or removal. So all are BASIC: the walk's step 4 now runs on
  every checkout after step 2, and a new `## extended` section holds the three real extended concerns (E1 removal, E2 the
  loadAfter mods alongside, E3 the older-GSS clash), all UNBUILT. The chains stay a separate run (`extension_proof.py`);
  they were not merged into `validation_v2.py`, which builds one fresh 250x250 map while the plots need the golden site.
- **Arrows, each checked against the row's predicate in `validation_v2.py`:** dig designation → `E8_player_dig`,
  `J_workgiver_selection`, `J_orders_accepted`; D=1..4 terrains → `S1_dig_ladder`, `S1n_superdeep_is_max`; channel-constrained
  → `E2_dry_ring`, `E2_channels_fill_every_direction`. Underlying-terrain recovery and flood expiry → UNCOVERED live (no row or
  chain spawns a `Flood_FlowWorks` release; `jawa/flowworks_spawn_flood` + `jawa/canal_cell_report` are the tools).
- **False claim corrected:** the walk said the flood "never" calls `SetTerrain`; `CoolFrontToGlass` does, by design, for
  `coolsToGlassEdge` fluids (tar glass).
- **Proof:** `selftest_extensions.py` check (7): every must-be-true line has an arrow and `## extended` lines are well formed,
  with planted-line probes. Red on the old walk (5 arrowless lines + no `## extended`), green on the new one.

`FLOWWORKS_CHECKOUT_SCOPE_1` — L0 done; NEXT: on the next bridge pass run step 4 (`extension_proof.py --live`) right after a
core run and record both results; `modcheck record` still stores only the core result, so wiring the step-4 result into it is
what makes the default checkout fail when a step-4 feature breaks.
