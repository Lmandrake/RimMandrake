# Acceptance progress 2026-10-09b (FOUNDRY helper)
Tier acc_20261009c. One line per item below.
- DUNES_TINT_GATE_PROOF_1.A1 L1 PASS: ProofTint returned shader=Custom/Snow hasColorProp=False defTintMode=MaterialColor.
- LASSO_CHERRYPICKER_REMOVAL_1.A2 L1 FAIL: Mod_2944488802_Core.xml has no LassoSpawnChance element; spawn chance still default.
- SWIM_HOOD_CANDRAW_PROOF_1.A1 L1 UNMEASURED: JawaRules proof type not loaded on tier acc_20261009c (Type not found).
- LIVE_ROUND2_FIXES_PROOF_1.A3 L1 UNMEASURED: needs run_genstep (high risk) on quicktest map; not yet run.
- WETBULB_FOLD_INTO_HEAT_1.A4: already passed in ledger; rerun on this tier agreed (+25.2) but nothing recorded.
- GLOW_TANK_LIQUID_FEED_1.A1 L1 PARTIAL: 'Dry: growth paused' line reads on a netless powered tank; the seed was not accepted (Refuel left fuel 0/1), so the seeded precondition is unproven.
- GLOW_TANK_LIQUID_FEED_1.A2 L2 PARTIAL: reserve line 'Ocean water: 6.0 h' appears and vanishes with tankNeedsWater=False; no drawdown or growth on the -22C Slime map (needs a warm biome map).
- WETBULB_FOLD_INTO_HEAT_1.A2 L2 UNMEASURED: log has 0 mentions of RM_WetBulbOverwhelm/RM_WetBulbProtection but tier is 67 mods, not the full tier the criterion names.
