# Harness fixes 2 (2026-10-07) - offline, unrun live, uncommitted

- `src/RimMandrake/WreckedMachines/validation.py`
  - allowDonorSmelter / allowFullRestoration: `_def_field(null_ok=True)` reads an omitted field in get_defs `fields` as "(null)" (the LuminousPigment `_designation` rule) instead of unreadable; the check still demands the Factories category appear after the toggle. A def that resolves to no row stays UNMEASURED.
  - wreckedRatio: no longer reads vanilla `idlePowerDraw`. Spawns RM_WM_PowerCell_Wrecked, waits 250 ticks, reads `jawa/power_net` `energyOutputPerTick` from the Thing's CompPowerTrader before/after (0.001 -> 0.01) and requires a 10x ratio; restore arm re-reads the same. Unreadable/zero reads give UNMEASURED.
- `src/RimStarWars/Droidworks/validation.py` protocol_droid_shifts_prices
  - Real cause: `jawa/fire_incident` dryRun DEFAULTS TO TRUE and the first call omitted dryRun=False (canFireNow=True, fired=False). Now fires for real, then retries factions OutlanderRough, TribeCivil, TribeRough, OutlanderCivil. If none fires but canFireNow=True it reports UNMEASURED (list) with the factions tried, never FAIL/PASS.
- Checks: py_compile both OK; WreckedMachines/validation.py static run PASS (0 findings); lint_calls: no new problems (one pre-existing UNCHECKED at Droidworks line 169).
- Caveat: wreckedRatio power read assumes CompPowerPlant reports a nonzero EnergyOutputPerTick after ticks without a net; if live reads 0, it will say UNMEASURED, not FAIL.
