I'd show this to the parent. The fix does what the statement asks, and the raw evidence backs it up. I found no material flaw. There is one gap DONE.md doesn't mention, plus some limits the parent should see. I read the source and raw evidence directly. I did not recompute any sha256 values, so where I rely on hashes I'm trusting the receipts and the asserts in `check_proof.py`.

## The change

The only change is in `HoseFuzz.cs`, lines 485–501 and 521. On a normal run (no `--fuzz-seed`), after the random cases, it runs seed 2 through the real `RunHose` once in outlet mode and once in free mode. Each run counts as a witness only if:
- the reel has a nozzle (`Outward.HasValue`),
- `RunHose` reports no fault,
- the hose was actually laid (`ok == 1`),
- it did not fall back (`f == 0`).

Any other outcome adds to `t.Failures` and puts a `hose coverage [mode] seed 2: …` line in `fails`. The existing check in `Report` (`Program.Check(t.Failures == 0, …)`) and the grouped diagnostics then pick it up. Seed 2 is one of the generated cases, so "every generated lay refused" now always fails.

## Your questions

**Total, outlet-only and free-only refusal fail inside the family's own check.**
- Total refusal: `FAIL fuzz hose: 2798 cases, 8200 steps, 2 failure(s)`, with `0/2 … witnesses` and both mode lines (`fast_final_total_full`; the tiny-scale run `fast_final_repaired_total` matches).
- Outlet-only refusal: 1/2 witnesses, failing on `[outlet]` (`fast_final_refuse_outlet`).
- Free-only refusal: 1/2 witnesses, failing on `[free]` (`fast_final_refuse_free`).
- Under the real `Program.cs` entry, the total-refusal mutant gives `HoseFuzz: 2/3` and return code 1 (`fast_entry_total`).

**The witnesses go through the real checks, including the non-fallback ones.** Requiring `f == 0` forces the bend-radius block. A nozzled outlet lay also forces the lead-out checks (`LeadOutLen > 0` and the G2 lead-out bend). Endpoints, length (G1 and the "wildly over" check), plump vs flat, wall clearance, sample counts and joints all run. The witnesses are called with `gaps = null`, so they skip the known-gap tallies. Those never fail a run, so nothing that can fail is skipped.

**Summaries are mostly clear.** The label `laid` became `random laid`, and witness coverage gets its own clause, kept out of the random case/step/laid counts. One small wart: a witness failure gives lines like `1 cases, 3 steps, 2 failure(s)`, because cases exclude witnesses but failures include them. The diagnostic lines underneath explain it.

**Command-line modes:**
- `--fuzz-scale`: tiny scales still run both witnesses. Scale 0 keeps the existing early return and prints no hose line (`fast_final_disabled`).
- `--fuzz-only trail`: skips the hose family, as before.
- `g2` / `g2off`: witnesses pass in both, through the probe and the real `--hose-fuzz` entry.
- Legitimate individual refusals still pass. In the full wrapper run, 191 lays were refused for no lead-out room and 95 for route too long, and the run still passed. Seed 7 refuses one mode and passes (`fast_final_debug_partial_refusal`).

**Single-seed debugging.** `--fuzz-seed` skips the witnesses and prints `single-seed debug; successful lay coverage not required`. That keeps the refusal-only debugging you asked for: seed 18 refuses everything, including through the real entry, and passes. The cost is visible: total refusal with `--fuzz-seed 2` also passes (`fast_final_debug_mutant`). The output says this honestly, and the FlowWorks wrapper never passes fuzz arguments, so the normal path always runs the guard.

**The real wrapper runs the guard.** `selftest_flowworks_stock.py` passes only `--only`, so the normal run calls `RunHoseSuites`, which calls `HoseFuzz.Run` at scale 1. The C# output captured by the strace observer shows:
- `2409 random laid … 2/2 successful checked coverage witnesses`
- `HoseFuzz: 4/4`
- `hose: 457/457`
- `1240/1240 passed`

The wrapper returned 0.

**The evidence is enough:**
- **Old false pass:** the original source with the total-refusal mutant passes at full scale with 2798 cases and 0 lays.
- **Same mutant both times:** `check_proof.py` asserts the mutated `HoseMath.cs` is byte-identical between the old-pass and new-fail runs.
- **Untouched kernel:** the production runs assert their kernel matches the repo file.
- **Timing:** the final source hash (`577c…`) is the same in every snapshot from `integrity_original` (taken after the edit) through review. All final controls started after that snapshot.
- **Wrapper inputs:** the staged wrapper inputs show no missing or mismatched files.
- **Engine reference:** the reused reference's hashes were re-checked against its provenance.

**No instrument failure was relabelled.** The `entry_g2` staging crash (it tried to read the generated `ReleaseRect.g.cs` as a static file) is kept as-is and labelled INSTRUMENT, and the retry used a new label. The runner's refusal to cache the result comes from environmental reasons (`/etc` and `/home/mandrake` changing, a clock read, external `/mnt/c` paths). It is kept raw and kept separate from the PASS.

**No shipping, GSS or art changes.** The tracked diff against HEAD, across FlowWorks, GSS, `_Shared` and Utils, is only `HoseFuzz.cs`, and the full mod/tool/media snapshot stayed stable.

## Each statement bullet

1. **Coverage proof and total refusal can't pass: met**, with a limit. Only the two seed-2 witnesses are asserted. The 2409 random lays are printed but there is no minimum success rate. A regression that refuses almost everything but still lays seed 2 would pass. The task's wording explicitly accepts a single fixed witness, and DONE.md and BROADEN.md state this limit.
2. **Controls, refusals, debug modes and selftest pass: met.**
3. **Exact source, limits, and shipping/GSS preserved: met**, except for the concurrency gap below. Live gameplay and visuals are declared out of scope.

## Flaws and unverified limits

- **Not disclosed:** three of the real-entry controls ran while the one authorised wrapper run was in progress. The wrapper started at 1794395121; `entry_g2off`, `entry_refusal` and `entry_total` started at 125, 132 and 138. `entry_total` built the total-refusal mutant (in its own scratch directory) and bypassed the wrapper's `dotnet_lock`. The results rule out contamination: the wrapper output shows 2409 lays and 2/2 witnesses, its staged identity is clean, and the build directories were separate. DONE.md should still say the run wasn't isolated.
- The fixed seed is brittle on purpose. A legitimate future planner change that makes seed 2 refuse will fail with a clear message, and someone will have to pick a new seed.
- The original false pass was reproduced with the fast probe harness, not the real `Program.cs`. The probe calls the same `HoseFuzz.Run` and `Report`, and the real entry covered the repaired failure, so this matters little.

would show: yes