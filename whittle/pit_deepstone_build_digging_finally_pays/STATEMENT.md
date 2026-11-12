# PIT_DEEPSTONE_BUILD_DIGGING_FINALLY_PAYS — done statement

Item: "Superdeep pit cells reach a deeper stone stratum" (built e9c39356b256; A1 L0 already met at build). Owed: A2 L2.

- **A2 L2 — DS_map_has_deep_stone PASS.** `python.exe src/RimMandrake/FlowWorks/northstar/deep_stone_live.py <out.json> --fresh-map`
  on SteveDesktop game A (FlowWorks tier, current build deployed): the `RM_DigDiscoveryProof.ProofReport("deepstone")` read names
  a deep rock and its chunk. Evidence: that row in the run's JSON under `whittle/pit_deepstone_build_digging_finally_pays/evidence/`.
- **A2 L2 — DS_superdeep_cut_turns_up_deep_stone PASS.** Same run: a colonist's D3 -> D4 cut takes the square to depth 4, a chunk
  of the named deep stone appears within 6 squares of the cut, the proof report's last find reads "D=4 (deep stone)", and a new
  letter starting "Deep stone" arrives. Evidence: the same JSON row, PASS, with its detail (depth before/after, chunk thing id,
  letter label).
