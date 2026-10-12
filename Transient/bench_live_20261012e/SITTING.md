# BENCH live sitting 2026-10-12e: CANAL_FRONT_FIX_WRONG_END_WETS_FIRST live check (fix 4de309155e)

Harness: `git archive` of src/ + infrastructure + Transient/modcheck + Transient/northstar from HEAD c930e6d40b at
`D:\Luke\dev\_rmscratch\bench_live_20261012e`. Owner list md5 ee01dae9e30d121c78d88e474dacd8e8 backed up (ModsConfig.owner_before.xml).
Deployed FlowWorks (DLL + srchash only; deploy_plan/apply_FlowWorks.txt). Tier: ModsConfig.ratchet_pilot_plus_patches.xml (23), Steam launch,
fresh quicktest (fresh_qt.py), tile 73171 AridShrubland.

## Results
- **extension_proof --live --site dry --chains plot_C_limitless_canal: 5/5 PASS incl. canal_fill_front** (ext_dry.json, 52.6 s).
- **validation_v2 --live --fresh-map --reset-settings: NOT GREEN, 49 PASS / 12 FAIL / 0 UNMEASURED** (v2_20261012e.json). Class **HARNESS**
  (stale oracle): the python pulse oracle in validation_v2.py models viscosity strides only (comment at ~line 173), not
  waterFrontCreepEnabled (now default True, 4de309155e), so every row that compares a kernel vector or a pulse count with the oracle
  disagrees: E2_channels_fill_every_direction (first-full pulse 7 per direction vs bound n*D=4), E2_rerun_determinism, E3, E3n, E3b, E4, E5,
  E5n, E5_sinks_back_on, E6, E6n, G_every_cell_vs_oracle. Not re-run with the toggle off (not measured: that the oracle alone is at fault).
  Prior baseline 61/61 (20261012b/d).

## State left
Game DOWN, ModsConfig restored to owner list, bridge released.
