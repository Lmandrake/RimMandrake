# Kernel extraction review (commit a4486ac02) - 2026-10-07
Status: DONE. Offline, no commit. Three fuzz wrappers pass after fixes; three mod DLLs rebuilt (uncommitted).

Method: `git show a4486ac02 -- <call-site>` read line by line against each kernel expression.

## Bazaar (RM_BazaarKernel.cs, RM_BazaarEconomy.cs): behaviour preserved, no findings
- Mathf.Clamp(float) == kernel Clamp (same `<`/`>` comparisons, NaN passes through both). Inclusive band edges unchanged.
- DriftStep: same order as the original (target from pre-decay nudge, noise, step, cap clamp, band clamp, nudge decay, dust 0.001 snap). Mathf.Abs == Math.Abs.
- ToUnit: identical `(uint)h / 4294967296f`. Hash combine/seed derivation stays in the Economy (Gen.HashCombineInt), kernel only receives the hash.
- Ring: RingPush / RingOldestFirst (still lazy, still an iterator) / RingRepair identical. RingRepair's `(int)Clamp(float head)` is exact for any head that matters (result range <= 31 < 2^24).
- Consts now alias the kernel; no Scribe change (history/head/nudge fields untouched).

## Rust Cathedral attitude (RM_AttitudeKernel.cs, RM_MapComponent_BiomeAttitude.cs): preserved, no findings
- Clamps/Max identical (Mathf.Max vs Math.Max differ only for -0, irrelevant). Pow: Mathf.Pow == (float)Math.Pow of the same float args.
- DroppedBand: def==null guard kept at the call site, rest identical. DesiredLayers, ClampToCeiling, Composite (int*float order kept), BandFor identical.
- Drain: original did the day roll, cap check, interval check, then `Notify_Standing(amount); drained += amount`. Kernel adds to drained before Notify_Standing; Notify_Standing touches only `standing`, so equal. intervalTicks (RoundToInt) now computed one step earlier, pure.
- All Scribe names/defaults unchanged (irritation, currentBand, standing, goodwillDrain*, ...).

## Ninefold (RM_NinefoldKernel.cs, GameComponent_Ninefold.cs)
- MoodStep/AddSatiation/ErodeSatiation/Loudness identical expressions and operand order; Rand.Value still read once per god per hour.
- LoudnessRank: sort comparison identical and a total order (ordinal tie-break), so unstable sort cannot change the result. satiation.Length == GodExtensions.Count == 9.
- TryFirstContact / MarkFired / PopDue / CountViolentDeath: same branch order and same side effects as the original blocks.
- FINDING 1 (fixed, perf not semantics): GameComponent_Ninefold.cs MaybeFlipFrontOnViolentSwing now called LoudestGod() (new List + Sort) on EVERY satiation add, before the not-reckoned / small-event early-outs the original ran first. Result identical (LoudestGod is pure) but a new per-event allocation+sort. Fix: kernel `IsViolentSwing(...)` (FrontAfterSwing now uses it) and the component returns on it before LoudestGod().
- Scribe fields untouched.

## Fuzz harness
- FINDING 2 (fixed) BazaarFuzz.cs:37 `Unit(int arg)`: `arg * 2654435761u` promotes int*uint to long, so Unit returned values up to ~6e4 instead of [0,1). NoiseU, Fraction and Level therefore fed the kernel out-of-contract inputs (noise way above +-DailyNoise, nudges and levels almost always saturated), so mid-range behaviour was barely exercised. Fix: `unchecked((uint)arg * 2654435761u) >> 8`. Re-run: still 0 failures.
- FINDING 3 (fixed) all three Run(): `--fuzz-scale 0`, or `--fuzz-only <typo>`, ran zero cases and printed "-> OK" with exit 0 (false green). Now both exit 1 with a FAIL line.
- Invariants are properties, not copies of the implementation: independent reference ring queue (Bazaar), independent drain-window sum and FIFO queue model (Attitude/Ninefold), exponential half-life law, monotonicity, ordinal tie-break, band bounds. Seeds are `new Random(seed...)` only; replays asserted equal; no clock/time source. Shrinking prints replayable `family seed N`.
- Residual (not fixed, by design): the harness drives the kernel, so it cannot prove the call sites in the components match it; that equivalence is the manual audit above. Bazaar drift determinism check is weak (pure function), harmless.
- Residual: Attitude fuzz tick advance per check (60-2500) vs drain interval is fine; edge `StandingAfter(100,int.MaxValue)` wraps to -100, unreachable (callers pass small deltas).

## Results after fixes
selftest_bazaar_fuzz 104511 cases OK; selftest_ninefold_fuzz 222000 OK; selftest_rustcathedral_attitude_fuzz 80000 OK.
winbuild: Ninefold, Bazaar, RustCathedral.Hum all 0 errors (DLLs + .srchash modified, uncommitted).

## mark-clean (run AFTER committing the edited files; mark-clean refuses uncommitted changes)
Zero remaining findings, unchanged since a4486ac02 (can be run now):
  python3 src/RimMandrake/Utils/code_review_status.py mark-clean src/RimMandrake/TheBazaar/Source/Economy/RM_BazaarKernel.cs src/RimMandrake/TheBazaar/Source/Economy/RM_BazaarEconomy.cs src/RimMandrake/RustCathedral/Source/Hum/RM_AttitudeKernel.cs src/RimMandrake/RustCathedral/Source/Hum/RM_MapComponent_BiomeAttitude.cs
After committing my edits (GameComponent_Ninefold.cs, RM_NinefoldKernel.cs, the three *Fuzz.cs):
  python3 src/RimMandrake/Utils/code_review_status.py mark-clean src/RimMandrake/Ninefold/Source/RM_NinefoldKernel.cs src/RimMandrake/Ninefold/Source/GameComponent_Ninefold.cs src/RimMandrake/TheBazaar/Source/SelfTest/BazaarFuzz.cs src/RimMandrake/RustCathedral/Source/SelfTest/AttitudeFuzz.cs src/RimMandrake/Ninefold/Source/SelfTest/NinefoldFuzz.cs
(Note: RM_MapComponent_BiomeAttitude.cs and GameComponent_Ninefold.cs are whole-file marks; this review covered only the extracted call sites in full, not every other method of those files, so mark them only if you accept that scope.)
