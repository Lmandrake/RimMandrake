# Broaden review: HOSE_FUZZ_HARDEN_ZERO_LAID_PASSES (suggestions only, not a verdict)

**Where things stand.** `HoseFuzz.cs` in the tree hashes to `62b6ff…`, which matches the receipt. So no repair has been written yet, and these suggestions are for the guard before it goes in. The one control on record, `fast_original_total`, shows a false PASS: `fuzz hose: 1 cases … 0 failure(s)`, `(0 laid …)`, `refused … isolated refusal mutant: 1`, `FAILED checks: 0`. But it ran at `--fuzz-scale 0.0001`, which is a single case (seed 1, a 1x1 reel). A skeptic can call that a degenerate run. Repeat the original + total-mutant control at the default scale (2798 cases, 0 laid, PASS) so the false pass is shown on the real workload.

## Traps the maker could miss

1. **`[outlet]` does not always mean a nozzle lay.** `HoseReelRect.Outward` is null when there is no nozzle (`HoseMath.cs:2794`). Seeds with a 1x1 reel (about 15%, e.g. seeds 1, 5, 20, 23 in `inspect_console.txt`) run the `outlet=true` loop pass as a plain free lay. The existing `laidModes[outlet ? 0 : 1]` (`HoseFuzz.cs:466`) is keyed on the loop flag. A guard like `laidModes[0] > 0` would therefore still pass under the `startOutward.HasValue` (outlet-only) mutant, because the 1x1 reels keep "outlet" lays alive. Key the per-mode coverage on whether `MakeHose(seed).Reel.Outward.HasValue` (nozzle vs free), not on `outlet`. The `free` mutant (`!startOutward.HasValue`) refuses both the free passes and the 1x1 "[outlet]" passes. Run both mode mutants as controls.
2. **Sampled thresholds can't be checked on small samples.** `--fuzz-seed 18` refuses both modes in CheckInstall (steps=1), and `--fuzz-seed 7` legitimately refuses the outlet lay. A tiny scale is seed 1 alone, with no nozzle at all. `ShippedMatrixProbe.HoseFamily` runs at `scale = n/1500`. Any "laid > 0 / ratio" check on the sample therefore has to be switched off in exactly the modes where total refusal currently hides.
3. **The VV matrix doesn't see a `Program.Check` FAIL.** `ShippedMatrixProbe.cs:231` counts failures only from the grouped `^\s{4}N x ` lines. If the guard is a separate `Program.Check`, `vv_shipped_matrix.py` still reports 0 failures under total refusal. Fold the guard into `t.Failures` and the `fails` list (without the `KNOWNGAP ` prefix). Then the family's own `Report` check (`fuzz hose: … N failure(s)`) fails, which matches "cannot evade the family check" literally, and the VV probe counts it too.
4. **The real wrapper's `Check` prints only FAIL lines** (`HoseChecks.cs:24`), unlike the probe's `Check`, which prints PASS too. Print the guard result with `Console.WriteLine` on every run so the strace-captured stdout shows the guard ran. For failures: the wrapper's tail (`selftest_flowworks_stock.py:124-127`) echoes a `FAIL` line plus the next line only if that line starts with 4 spaces. Put the diagnostic on that next line.
5. **Fallback lays skip the bend checks.** Lays with `FellBack` skip all the G2/G3 checks (`HoseFuzz.cs:158`), and production has 0 fallbacks. Require the witness to be non-fallback, so it proves the bend/lead-out checks actually ran, not just that something was laid.
6. **The probe's handling of g2/g2off differs from the real entry.** The probe Program sets G2 if `g2off`/`g2` appears anywhere in the args. The real `--hose-fuzz` entry only checks `args[1]` (`Program.cs:221-222`). The stock wrapper passes no args at all: G2On stays true, scale is 1, both families run. Limit claims about `--hose-fuzz g2off --fuzz-seed N` to "`HoseFuzz.Run` behaviour under `G2On=false`". Neither the probe nor the wrapper proves the real CLI parse.

## Recommended guard (small)

**Primary: deterministic witnesses through the real `RunHose`.** Run them after the sampled loop, whenever the hose family runs and `scale > 0`, including under `--fuzz-seed` and tiny scales:
- Use a fixed small set of 2x2 seeds that lay in both modes in production. Candidates from inspect are 2, 3, 4 (also 6, 8, 9, 10). Re-verify them under `g2off`.
- Call `RunHose(seed, null, ref ws, out ok, out fb, outlet, gaps: null)` with `BendCollect` false, so `RefuseWhy`, `BendOutlet`, `BendFree` and the gap tallies stay untouched. Don't add the witness to `t.Cases`, `t.Steps` or `laid`. That keeps the printed `(N laid …)` meaning "the sample", and the baseline line `2798 cases … (2409 laid, 0 via fallback …)` stays byte-identical.
- Require at least one nozzle witness (precondition `Reel.Outward.HasValue`, which can itself fail) and at least one free witness, each with `msg == null && ok == 1 && fb == 0`. Any non-null `msg` from a witness is a real fault and should be reported as one.
- On failure, print each witness's seed, mode, CheckInstall verdict and `lay.Reason` (reproduce it via `MakeHose` + `HoseMath.Lay`, or expose the reason from `RunHose`). The message should say either the planner regressed or the generator moved the witness, and to pick another seed.
- An "any of the set" rule absorbs one witness turning into a legitimate refusal after a real planner change, and still catches total and mode-only refusal.

**Secondary, optional: a sampled floor.** Like the SleepingIce precedent (`SleepingIceFuzz.cs:534`), gate it on `one == null && scale >= 1`. Require nozzle-laid > 0 and free-laid > 0 among route-passed cases, keyed on the actual mode. Scale-1 seeds are fixed (1..1500), so a looser ratio floor (e.g. nozzle ≥ 25%) is deterministic, not flaky. It would also catch partial-refusal regressions, which the witness misses. Whether to add it is the maker's call. Don't make it the only guard: it has the small-sample hole from trap 2.

**Diagnostics.** Print the counts per actual mode: nozzle / free / 1x1 → cases, refused by CheckInstall, refused by Lay (by reason), laid, fallback. Mode-only refusal then shows up directly, not just as a smaller total.

**Scale and filter semantics.**
- `--fuzz-scale 0` or negative is an intended skip (Bazaar documents "0 skips"; the VV probe reads it as UNMEASURED). Keep it, but print `fuzz hose/trail SKIPPED (--fuzz-scale 0)` and run no witness.
- An unknown `--fuzz-only` (a typo like `hoses`) currently runs nothing and prints `0 cases` silently. Consider `FAIL unknown --fuzz-only family` (precedent `SleepingIceFuzz.cs:528`). It's a small scope extension, so state it as such.
- `--fuzz-only trail` must not run the hose witness.

**Sibling gap, out of scope.** The trail family declares `visited` (`HoseFuzz.cs:511`) but never fills it. A "Grab always fails" mutant leaves every trail case Stored and passing. File it separately; don't widen this item.

## Controls to run (fast probe, isolated mutants)

| # | Version / mutant | Args | Expect |
|---|---|---|---|
| 1 | original / total | default | PASS, 0 laid (false pass at full scale) |
| 2 | repaired / total | default; `--fuzz-seed 18`; `--fuzz-seed 2`; `--fuzz-scale 0.0001` | FAIL in the family line + diagnostic |
| 3 | repaired / outlet | default; `--fuzz-seed 1` (1x1) | FAIL; also show the loop-flag count >0 (proves trap 1) |
| 4 | repaired / free | default | FAIL |
| 5 | repaired / production | default, and default + `g2off` | PASS; sample line identical to original; witness line printed |
| 6 | repaired / production | `--fuzz-seed 18`, `7`, `1`; `--fuzz-scale 0.0001` | PASS (legitimate refusals still pass) |
| 7 | repaired / production | `--fuzz-scale 0`; `--fuzz-only trail` (also under the total mutant); `--fuzz-only hose` | skip with no FAIL; trail unaffected; PASS |
| 8 | repaired / a real-fault mutant (e.g. a displaced Flat endpoint) | default | the existing FAIL + shrink output unchanged (the guard doesn't mask it) |
| 9 | optional: repaired / production | `--fuzz-only bogus` | FAIL |

Then the single real wrapper run with the strace capture, checking that the witness line appears in the real C# stdout. Also record a hash check showing `HoseMath.cs` and the GSS sources are unchanged.

This is input for the maker and the separate judge call. It is not a finding that the item is complete or correct.