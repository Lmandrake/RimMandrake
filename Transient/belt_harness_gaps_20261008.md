# Harness gaps 2026-10-08

(skeleton; steps appended below)
1 WreckedMachines: mod reads ratios via Settings.Ladder (normalised) and live def read-back PASSed; validator static lint grepped only raw field names -> taught it the Ladder property. no mod change/build needed
2 acc_harness tier += mandrake.rm.biomes + mandrake.rm.shipvermin (ShipVermin About depends on biomes)
3 Droidworks: test spawned fine; engine drops Pawn_TraderTracker unless mindState.wantsToTradeWithColony -> MakeTrader (mod proof helper) now sets it and creates tracker; building
3b Droidworks built OK. next: CB track_grid
4 CB track_grid: mod writer correct (gravel has no surface ext); counters global+unattributed so stray pawns inflate -> added RM_TrackGridDiag.PrintsBy(pawnId) + harness uses it; building
5 selftests ok (wm lint 16/16, droidworks); publishing
