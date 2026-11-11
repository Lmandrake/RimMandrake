**Assessment: fw-drain-hose-fuzz (zero-lay false PASS)**

I'd show this to the parent. I read the source and raw evidence first, then DONE.md. The repair is a small, correct change confined to the selftest. The raw evidence supports each bullet, and the remaining limits are disclosed. None of them needs a repair before parent review.

## The source

The diff touches only `Source/SelfTest/HoseFuzz.cs` (`source_diff.patch`, +19/−1).

- **When it runs:** at any positive scale, when `--fuzz-seed` is not given (`HoseFuzz.cs:488-502`).
- **What it checks:** it runs seed 2 through the real `RunHose` once in outlet mode and once in free mode. Each mode counts as a witness only if all three hold:
  - `MakeHose(2).Reel.Outward.HasValue`. `Outward` is null unless the reel has a nozzle (`HoseMath.cs:2794`), so a 1×1 reel can't satisfy it.
  - `msg == null`: every `RunHose` assertion passed, including the install check against an unbounded route.
  - `ok == 1 && f == 0`: the lay succeeded and did not fall back. This forces the checks that only run on non-fallback lays: the G2 lead-out bend, the bend floor and the outlet-has-lead-out check.
- **Where failures go:** a failed witness adds to `t.Failures` and to `fails`. So it reaches the family's existing `Program.Check(t.Failures == 0, …)` in `Report` and the grouped diagnostics. A refusal in either mode alone is caught.
- **Summary honesty:** witnesses are kept out of `Cases`, `Steps` and `laid`. The label now reads "random laid", and the summary prints `N/2 successful checked coverage witnesses (seed 2, outlet/free)`.
- **Debug mode:** in single-seed debug the summary says `single-seed debug; successful lay coverage not required`.
- **Unchanged paths:** `--fuzz-scale <= 0` still returns early. `--fuzz-only trail` still skips the hose family. Individual refusals still return null and are tallied in `RefuseWhy`.
- **Entry points:** `HoseChecks.cs` shows that `RunHoseFuzzOnly` (`--hose-fuzz`) and `RunHoseSuites` (the ordinary run, `Program.cs:2274`) both call `HoseFuzz.Run(args)`. The wrapper passes no fuzz arguments, so the ordinary run uses scale 1 and the witnesses always execute.

## Raw execution evidence

**Original false pass.** `fast_original_total_full/stdout.txt` shows `PASS fuzz hose: 2798 cases, 8200 steps, 0 failure(s)` with `(0 laid …)`, and refusal tallies of 1445 outlet and 1250 free. The staged kernel diff is a single injected `if (p != null) return new HoseLay{…}` in `Lay`. The staged HoseFuzz hash is the original (62b6…).

**Repaired failure with the same mutant.** `fast_final_total_full` uses a byte-identical mutated kernel (`check_proof.py` asserts this). It shows `FAIL … 2 failure(s)`, `0/2 … witnesses`, and grouped `hose coverage [outlet]` and `[free] seed 2` lines.

**Mode-only refusal.**
- `fast_final_refuse_outlet` (mutant condition `startOutward.HasValue`): 1/2 witnesses, only the outlet coverage line fails.
- `fast_final_refuse_free` (`!startOutward.HasValue`): 1/2 witnesses, only free fails.

**Positive and legitimate-refusal controls.**
- Tiny scale (0.0001), g2 and g2off all PASS with 2/2.
- Seed 18 is an install-stage refusal: 2 cases, 2 steps, PASS.
- Seed 7 is a real production lay refusal ("no room for the straight lead-out"), with free mode laid: PASS.
- In the full wrapper run, 286 legitimate production lay refusals (191 + 95) coexist with PASS.

**Debug exception.** `fast_final_debug_mutant` (`--fuzz-seed 2` with the total-refusal mutant) PASSes and prints the stated limitation. This is what the user asked for: refusal-only single-seed debugging is kept, and the output says so.

**Actual C# entry point.** These controls compiled the real csproj and `Program.cs`; the build warnings carry the stage paths.
- `entry_total`: rc 1, `HoseFuzz: 2/3`.
- `entry_g2_retry` and `entry_g2off`: 3/3 with 2/2.
- `entry_refusal`: single-seed debug, 3/3.

**Full wrapper.** `csharp_stdout.txt` was decoded from the wrapper PID's own writes in the preserved trace (hash recorded in `output_extraction.json`). It shows:
- 1240/1240 cases.
- `2798 cases … (2409 random laid, 0 via fallback, 1 known-gap class …; 2/2 successful checked coverage witnesses)`.
- `HoseFuzz: 4/4` and `hose: 457/457`.
- No `FAIL` lines.

`selftest_stdout.txt` reads GREEN, rc 0.

**Identities and timing.**
- `integrity_original` (t = …005.9) already holds the final hash 577c…. Every `fast_final_*` run started at …007 or later, so all final evidence postdates the final edit.
- `integrity_before`, `after_test`, `before_review` and `after_review` all hold 577c….
- `stage_identity` reports `missing: []` and `mismatch: []`, with only HoseFuzz.cs dirty.
- `git diff` across FlowWorks, GSS, `_Shared` and Utils lists only HoseFuzz.cs.
- The shipping DLL hash is unchanged.
- The engine reference hashes were re-measured and match their provenance.

**Instrument failures kept and labelled correctly.**
- `entry_g2_console.txt` is a Python `FileNotFoundError` on the literal `$(MSBuildProjectDirectory)…ReleaseRect.g.cs`. It is correctly diagnosed as an instrument fault before compilation, and the retry used a new label.
- The runner's "not recordable" refusal (`cache_record_refusal.json`) came from absent-input folder mtimes (`/etc`, `/home/mandrake`), a wall-clock read and the Windows dotnet path. It was not a source change, and it is disclosed.
- No instrument fault was reported as a mod failure or as a PASS.

**Control overlap.** Three entry controls ran during the first ~20 s of the wrapper run and bypassed `dotnet_lock`. That was a process deviation, and DONE discloses it. It does not touch the result:
- The controls used separate scratch stages.
- The last one ended at …141, while the wrapper's stage DLL/EXE/PDB were written at …270.
- The stage hashes match the final source.
- The wrapper's 2409 random lays and 2/2 witnesses could not happen under the mutant.

**Broaden.** The broaden call was a separate fresh process (`--no-session-persistence`, Read/Glob/Grep only, neutral cwd). Its relevant suggestions show up in the final code: the nozzle requirement, `fellBack == 0`, witnesses kept out of the case/step counts, and the full-scale and actual-entry controls. The one suggestion declined (running witnesses in single-seed debug) was declined to honour the user's instruction.

## Each frozen bullet

1. **Coverage, and cannot pass when every generated lay refuses: met.** Total refusal fails at both tiny and full scale. Either mode refusing alone also fails. The witness goes through every asserted `RunHose` invariant, including the non-fallback ones.
2. **Controls, legitimate refusals, debug modes, selftest pass: met.** There are production-linked false-pass and repaired-fail pairs on the same mutant, from both the probe and the actual entry point. Legitimate refusals and the debug, disabled and trail-only modes are shown working. The final wrapper passes, and the coverage line appears in the raw C# output.
3. **Exact tested source, limits, shipping/GSS unchanged: met.** The hashes tie every final control and the wrapper stage to 577c…. Shipping, GSS and art bytes are unchanged. The limits are disclosed: no random-success floor, no live/visual check.

## Limits that remain (not blocking)

- **Random coverage is printed but not asserted.** A regression that refused nearly all random lays, or every one except seed 2, would still pass. The prompt explicitly accepts a deterministic witness, and DONE/BROADEN state this limit.
- **The witness depends on the generator's RNG.** If `MakeHose` changes, seed 2 may stop being a nozzled 2×2 reel. The guard then fails loudly rather than passing.
- **Cosmetic:** the failure count can now exceed the case count ("1 cases … 2 failure(s)"). The grouped line explains it.
- **The fast probe uses a stub `Program.Check`.** The actual-entry controls cover that gap.
- **The ShippedMatrixProbe (VV_HOSE) path was not executed.** From reading the code, witness failures would appear there as counted "N x" lines.
- **The lock bypass during the wrapper run** shouldn't be repeated. The timing evidence shows it didn't contaminate the result.

would show: yes