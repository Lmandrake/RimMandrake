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

Lane 1 after the fixes (same file, two rows added red-first, one re-scoped; see tests_edited.json): 44 rows, 34 PASS,
2 INFO, 8 UNSETTLED, 0 FAIL; about 324 000 cases [measured, lane1/lane1_rows.jsonl].

## Lane 2 (challenge)
Opened after lane 1 was published (bbad998788): test_table.json, the game-side code, the builder's offline tests, and the
journal's open questions 10 to 14 only (to avoid judging them).

- **Reruns** (lane2/reruns.jsonl, before any change): 16 of 16 offline tests give the recorded verdict; 14 of 16 give the
  recorded last line, the other two differ only in how the line was recorded (T_FW_COVER truncated at 200 characters,
  T_RESTORE's recorded line is a SyntaxWarning from stderr) [measured]. After the fixes (reruns_after_fix.jsonl): 16 of
  16 same verdict [measured].
- **Planted faults** (lane2/planted_results.jsonl): 43 one-line faults, each planted, run, removed, tree proven equal to
  HEAD after (`tree_clean_after: true`) [measured]. The builder's offline tests caught **39 of 43**; all 31 kernel faults
  were caught (T_KERNEL or T_FUZZ). Missed: the closed-container guard switched off, the container mass limit ignored,
  goods on a pit floor thrown (all game code, decided only by Stage 6 scenes), and Flame's force 1.0 in the def patch
  (an offline lint could pin it). Lane 1 caught 30 of 31 kernel faults (missed banker's rounding) [measured].
- **Faults** (lane2/faults.json, refusal records): **Problems 3** (2 in code, both fixed red-first; 1 in a scene
  criterion, for the Conductor), **Polish 6**.
  - Problem, fixed: goods never flew wild. No 1.6x factor existed anywhere; a 60 kg corpse beside a mortar flew 3 cells,
    like the living colonist. Now 5 [measured].
  - Problem, fixed: the gas burst's goods cap (2 cells) was rescaled by the per-weapon cap-scale setting (4 cells at 2.0,
    1 at 0.25) [measured]. Now exact.
  - Problem in a criterion, not fixed (bar text): sc_storeroom_mortar wants every good's wild-to-kernel ratio within
    1.3 to 2.0; whole cells make that impossible for short throws and at the cap (kernel 2 and wild 2 at 1.5 raw cells).
  - Polish: the wild factor ships as a constant, because a new Mod Setting turns T_STAGE3_SCENES red until the locked
    sc_settings_sweep action names it (for the Conductor); a false "always runs out" comment (fixed); the unused kernel
    ContainerShove (tied to question 12); the kernel selftest copies into shared staging outside its lock; the recorded
    last lines; the scene reads wild cells off the request line, which is written before the throw is known.
- Questions 10, 12 and 14 were met (no closed-guard-off setting; container thrown whole versus slid; no fire-half
  setting). Noted once; no verdict was built on them.

## Fixes (red first)
`81392aea38`: RM_KnockbackMath.WildCells + GoodsThrowWild 1.6 (items and corpses, both where the throw is made and where
the blast decides a stack will be thrown; item_move journals kernelCells and wildCells); KbConfig.scaleOwnCap, false on
the gas burst; the rebound comment. Red on 8292600eec, green on 81392aea38: lane2/fixes.jsonl, red_*.txt, green_*.txt
[measured]. Release DLL and proof build both compile with 0 errors; T_PROOFGATE still passes [measured].

## Tests edited
tests_edited.json: the builder's RM_KnockbackProof.cs, 3 goods expectations (ThrowCells to WildCells, live, UNRUN);
my own lane 1, 2 rows re-scoped. Added: 2 lane 1 rows, lane2/check_fix_wiring.py, and
src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_blind_cycle1.py so the nightly sweep runs them.

## Not settled
- Everything live: the wild goods are proven in the kernel and by static wiring, not in a game (offline only, by brief).
- Whether 1.6 should be a Mod Setting (Conductor; bar text).
- The 8 lane-1 rows the kernel cannot decide (flight, hose, gas clumps in play, covers, fetching, hook scope, trace, walk).

## Exit condition
**Not met** [measured]. (1) The offline bar `inv_proof_scenes` is not green: T_RESTORE is known red
(RIMMANDRAKE_RESTORE_ON_THROW_IN_KNOCKBACK_PROOF_TWO_LEAKS); `inv_kernel` is green. (2) This judge found Problems; they
are fixed, so by the road back the mod goes to a new blind judge (cycle 2) reading the changed files: RM_KnockbackMath.cs,
RM_KnockbackMod.cs, RM_MapComponent_Knockback.cs, RM_KnockbackProof.cs, and the tests in tests_edited.json. Cycle 2 is
not started here.
