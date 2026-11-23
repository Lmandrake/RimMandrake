## spec
MOD finding, FlowWorks liquidIgnitionEnabled ON: testq J20261113T071831Z-eaaeff (SteveDesktop, tier mods__mandrake_rm_flowworks,
sha fd568d495b), row liquid_ignition_on FAIL: "a burning log beside RM_FuelSapShallow for 500 ticks lit no sap cell (map_fire
straight onto sap: firesStarted=0 cellsFailed=0)". The item RIMMANDRAKE_PROVE_FLOWWORKS_TOGGLES_DENSE predicted it: vanilla
FireUtility refuses terrain with 0 Flammability, so LiquidIgnition never lights sap terrain. The OFF control and the
corrosion rows passed in the same run.
## acceptance
Live: the same clause (live-proof A2 in infrastructure/state/live_proofs/RIMMANDRAKE_PROVE_FLOWWORKS_TOGGLES_DENSE.txt) reads
liquid_ignition_on PASS. Acceptance test (offline): none, the defect is a game-engine refusal that only a live fire shows.
