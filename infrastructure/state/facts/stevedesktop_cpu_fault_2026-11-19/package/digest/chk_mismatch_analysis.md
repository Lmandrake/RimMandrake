# What the wrong results look like: analysis of every MISMATCH line in watch-chk.log

Source: `raw/steve_logs/watch-chk.log` (copied off SteveDesktop 2026-11-20 07:53Z; 7,603,469 bytes; starts 2026-11-01 02:28:33Z,
lines carry HH:MM:SS only, dates reconstructed by counting midnight roll-overs). The checker is `findings/steve_diag/Program.cs`
(`stevecheck core <cpu> <secs>`): pinned to one logical CPU, it computes 8 reference results (one per fixed seed) at start, then
recomputes them round after round and counts a round "bad" when the result string differs from that run's own reference.
A result string is three 64-bit parts: `int` = an AVX2 integer multiply/shuffle/add pass over an 8 MB buffer; `fp` = an FMA /
divide / sqrt double-precision loop (20,000 reps over 64 doubles, IEEE exact, so bit-identical on healthy cores); `sha` = SHA-256
of the buffer after the int pass (.NET SHA256.HashData). Only the first 5 mismatches per run are logged, with want (= that run's
reference) and got.

All counts below are [measured] by the script in this conversation (method reproduced in `scripts/`), over 12,550 MISMATCH lines.

1. **The canonical (correct) reference is the majority value.** Taking the most common value of each part for each seed and
   hashing the 8 strings the way the checker does gives `E99EB79839CA4010`, the `ref=` the checker prints on clean runs.
   So the majority values are correct, and the `want` side is itself wrong in about half the mismatch lines: the fault also
   hits the reference computation at the start of a run.
2. **The `fp` part, when wrong, takes exactly ONE alternative value per seed** (2 distinct values per seed across 12,550 lines,
   e.g. seed 0: canonical `6e4ee38448abd217`, alternative `8e98483f88768b5f`). The same alternative appears on every logical
   CPU that faulted (CPUs 0-18) and on every day 2026-11-01..16. Errors in `fp` are therefore not random bit noise.
3. **The `int` and `sha` parts, when wrong, are mostly unique values** (int: 402-1,180 distinct wrong values per seed; sha:
   480-1,747), i.e. random-looking corruption. A wrong `int` always comes with a wrong `sha` (the sha hashes the buffer the int
   pass wrote), and about 9% of mismatches are `sha`-only (int and fp right, hash wrong).
4. A mismatch is wrong in ONE of three ways (int+sha, fp alone, sha alone); almost never two at once (43 of 12,550 lines have a side
   carrying both an fp alternative and a wrong sha).
5. **The fp alternative is exactly "lanes 2 and 3 became NaN".** Recomputing the fp loop in Python (`scripts/fp5.py`, which
   reproduces the canonical value bit for bit under round-to-nearest) and replacing the final values of the two UPPER lanes of the
   256-bit accumulator (lanes 2 and 3) with the x86 default NaN (0xFFF8000000000000), while lanes 0 and 1 keep their correct
   values, gives the observed alternative exactly for seed 0 (`8e98483f88768b5f`), seed 3 (`7ddb450510ba1a62`) and seed 7
   (`3546d6002e9d1a17`). [measured, 3 of 8 seeds tested, 3 of 3 match] That is the result you get if the upper 128 bits of the
   YMM registers that hold the loop's constants (a = 1.0000001, c = 0.9999999) are ZEROED at any moment during the loop: from then
   on the upper lanes compute 0/sqrt(0) = NaN, whatever the moment was. So the deterministic alternative is not a deterministic
   arithmetic defect; it is the timing-independent end state of one specific corruption: **loss (zeroing) of the upper 128-bit
   halves of the 256-bit vector registers.**
6. The int and sha parts are consistent with the same corruption: the int pass accumulates through 256-bit registers over an
   8 MB buffer, so zeroing at a random moment gives a random-looking wrong value (as observed: mostly unique values); the .NET
   SHA-256 uses vector code, so a sha-only error is the same loss hitting the hash. [guess ~75%: consistent, not proved]
7. Earlier tests that fit: 2026-10-26 on the bad CPU, AVX2-heavy hashes (openssl sha256, sha1, blake2b) gave varying digests
   while md5 and scalar HACL sha256 were stable (`findings/ledger_steve_fault_events.md`, STEVEDESKTOP_DIAGNOSE_CPU18_FLUNKS_MATH);
   Prime95 (FMA3/AVX2 FFTs) gave FATAL rounding errors on the bad CPU 2026-10-31. No scalar-only check has ever been run as a
   control in the 5-minute watch. [measured: the watch runs only the AVX2/FMA checker]
8. Model checks that ruled out other explanations of the fp alternative (before item 5 was found): other rounding modes, unfused
   FMA, reps 19,999 / 20,001 / 10,000, operand order, skipped store, d[] = 1.0, and single random bit flips (5 of 9 damped to the
   canonical value, 4 of 9 gave new random values) do not give it (`scripts/fp*.py`).

Per logical CPU (`watch_per_cpu_by_era.tsv`): logical CPU 2 carries 591 of 1,533 bad cycles in the turbo-off pre-raise era and
its hyper-thread sibling, logical CPU 3, carries 34; even-numbered logical CPUs fail far more than their odd siblings on every
core (cpu0 86 vs cpu1 66 is the closest pair). Two threads of one physical core share that core's vector units and register file.
[measured counts; the reading of them is for the assessor]
