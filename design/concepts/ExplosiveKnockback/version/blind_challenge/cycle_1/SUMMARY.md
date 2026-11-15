# Explosive Knockback 0.1.0 — blind challenge, cycle 1 (pilot)

Item: RIMMANDRAKE_PILOT_BLIND_CHALLENGE_ON_KNOCKBACK_NEVER_RUN_BEFORE. Seat BENCH, detached helper, offline only.

## Lane 1 (game logic, from the bars alone)
Recorded before any code beyond the kernel and settings was opened (commit of this section). Inputs read: sheet.md,
tree.json (oracles, tiers), plan.md, VERSION.json, RM_KnockbackMath.cs (kernel), RM_KnockbackMod.cs (settings defaults,
slider ranges), Patches/RM_Knockback_DamageDefs.xml (per-type forces). Not read: scenes.json in full, test_table, the
builder's selftests, journal, exam, verdicts.

Tests: `lane1/BlindLane1.cs`, run by `python3 lane1/run_lane1.py [--kernel <file>]` (Windows dotnet, staged under
D:\ClaudeWork\scratch\ek_blind_lane1). Rows: `lane1/lane1_rows.jsonl`.

- 42 rows: 31 PASS, 1 FAIL, 2 INFO, 8 UNSETTLED (not decidable without the game) [measured]. Decided: 31 of 32 pass.
- Random cases: about 330 000 (50 000 random grids through Resolve with shrinking, 50 000 through Reflect, 20 000-case
  numeric properties); conservation: one cell per thing, on its own path or its start; no candidate lost under no cap;
  one request per (explosion, thing); shield charge never grows; rebound totals bounded.
- Shipped settings swept: strength, maximum, cap scale, other-mods percent, creature and goods mass limits, reference
  percent, impact per cell x impact factor, container limit, heavy threshold and damage, stagger, recovery, shield
  debit, rebound keep percent.
- FAIL `L1_sweep_rebound_keep_slider_chain_ends`: at goodsReboundKeepPercent 100 (the slider's top, shipped range
  0..100) `ReboundCells(n,100) = n`, so the kernel never ends a rebound chain. Whether the carrier bounds it is lane 2.
- Own test error, caught: the first `L1_twice_damage_strictly_farther_below_cap` demanded 2x damage throw strictly
  farther for every throw; it failed on 1-cell rim throws, which integer cells make unavoidable. Re-scoped to 2+ cells,
  the rim case kept as INFO. The bar text is not wrong; my reading was too literal.
- INFO `L1_kernel_alone_goods_vs_person_distance`: the kernel and the settings carry no goods-distance factor; a light
  good gets at most the mass-scale 2x, a 60 kg corpse flies as far as a colonist (3 vs 3). The sheet's "about 1.6 times
  as far as a person" must come from the game side; lane 2 checks.

## Lane 2 (challenge)
PENDING

## Fixes (red first)
PENDING

## Tests edited
PENDING

## Not settled
PENDING

## Exit condition
PENDING
