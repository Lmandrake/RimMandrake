# WasteRun, sitting 2 (throwaway TemperateForest map, tile 114480)
- get_defs: RUT_WasteRun quest, RUT_WasteRunOffer incident and the seven RUT_WasteRun* history events all found (9/9).
- RM_CaskBay spawned by spawn_batch has no faction, so WasteRunDisposal.CaskBays() (AllBuildingsColonistOfDef) reads bays=0 and the command never shows: jawa/set_thing_props faction=PlayerColony first (scene trap, not a mod defect; a player-built bay is player faction).
- ProofGizmo with bay+waste+accepted quest: master=True bays=1 waste=1 activeRun=0 state=Ongoing gizmos=1 label="Waste run: choose destination" plannerCompOnBay=True.
- ProofPress on all five destinations (a fresh Wastepack + forced RUT_WasteRunOffer + accept each time): signal=Quest<n>.WasteDest_<Dest>, stateBefore=Ongoing stateAfter=EndedSuccess, wasteBefore=1 wasteAfter=0 for DropOnEmpire, FreezeColdSide, EntombAssailants, IgnitePropaneLake, SlimeExperiment.
- NOT measured: that each destination records its own history event (no reader), and the natural (unforced) offer.
