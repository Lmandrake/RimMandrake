## spec
found-by: BENCH bridge run (2026-10-23, run 1 driver 4, HEAD 39ec8aac5e deployed, 14-mod fw_gss_sitting).
Class: SITE. Row 3.3 of BRIDGE_RUN_1 is UNMEASURED: no dry golden site passes preflight on the 14-mod list.

Route 1 is the run sheet's: `test_site_saves.py load calm` (CLEAN), then `prep_site.py --seat BENCH`, then
`preflight_flowworks.py live`. prep_site laid 11 plots and classified 4 bodies (steps 1-7). It refused at step 8 because
NS_FlowWorks_TrialSite_v1.rws exists and golden saves are never overwritten. Preflight then read DIRTY SITE (5 FAIL, 3
UNMEASURED):
- P-B2: tile 112579 != sidecar 73698. The sidecar describes the 10-05 golden save, not calm.
- P-S1: plot cells carry grass, cactus, gravel and sand.
- P-S2: the bodies are unclassified.
- P-E4: autosave 0.25 days.
- P-E8: the screen is 3467x1826, not 2516x1252.

Route 2 loads NS_FlowWorks_TrialSite_v1 directly. It loads with missing classes: RimMandrake.Pyrelands.WorldObject_RM_FurnaceHerd,
WorldComponent_RM_FurnaceHerdSeeder and 4 abstract MapComponents. It does not storm. Preflight then read DIRTY SITE
(6 FAIL):
- P-L1/P-E6: the running list is not tier flowworks (+VFE core, luminouspigment, biomes).
- P-S2: pond capacity is 2/cell; the sidecar wants 5/cell (D_pond 50 vs 125).
- P-E3: a VEF.Factions.Dialog_NewFactionSpawning modal is open.
- P-E4: autosave.
- P-E8: screen size.

Evidence: Transient/bridge_run_1_20261023/s33_prep.log, s33_preflight.log, s33_preflight2.log, s33_load_golden.log.
Harness side note: from a git-archive export, preflight needs infrastructure/state/BRIDGE and
infrastructure/state/facts/retired_mods.json. Both were copied in by hand.

Fix: rebuild the dry golden site and its sidecar on the list the dry half runs on. Use `prep_site.py --rebuild`, which
moves the old save aside. That moves an owner-facing golden save, so whoever does it must hold the bridge. Separately,
decide whether P-E8's screen size and P-E4's autosave are real site gates on this machine. Until then, the dry half of
FLOWWORKS_CHECKOUT_SCOPE_1 A2, plus PIT_TEMPERATURE_SOFTENING_1, FLOWWORKS_CONTAINER_MATERIALS_1 and LIQUID_BOTTLE_LOOP_1,
stay owed. Related: RIVER_SITE_REBUILD_FOR_FOURTEEN_MODS (the river half).
