I wouldn't accept this yet. The probe parsing and the strengthened kinetic rows hold up, but the change breaks three of the four existing GimmeSomeSlack-only proof commands, which is the thing the parent asked about. Everything below comes from reading source and the retained raw outputs. I attached no game and made no live or appearance claim.

**Blocking: existing GSS-only proofs now fail on loads without KineticArms**
- `kinetic_sway_rows` (`validation_aerial.py:1065-1143`) always sends `explode:…,RM_Repulse_Palm`. No command-line flag selects the synthetic token or the real definition.
- It is called once, with no condition, from `_four_switches` (`:1249`). Both `--flips` (`run_flips`, `:1285`) and `--live` (`run_live`, `:787`) reach it, and so does `proof_all --live` through `VA.run_live` (`northstar/proof_all.py:987`).
- Without KineticArms loaded, the lookup at `AerialProbe.cs:154` returns null and the probe replies "unknown damage defName". The row's `read()` raises, so M22a and M22b both FAIL. `main` then exits 1 because there is a FAIL row (`:1861`).
- `relentless_live_round.py:18-22` says a `live-mods:` line lets a proof run on any game that holds those mods. So a GSS-only load is a valid place to run these files. The effect on each command:
  - **GSS_SWITCHES_PROVE_LAST_FOUR_STANDING A1** (`--flips`): needs exit 0 with no FAIL. **Breaks.**
  - **GSS_SWITCHES A2** (`proof_all --live`): needs zero FAIL rows. **Breaks.**
  - **GSS_RESTRING_FIX_STYLES_UNRECONCILED A1** (`restring_style_proof.py`, `--live`): `run_proof` requires the driver to return 0 (`restring_style_proof.py:62-63`). **Breaks.**
  - **GSS_RESTRING A2**: checks only the M15e row. Unaffected.
- The old `--flips`/`--live` rows used the synthetic `,kinetic` token and worked without KineticArms. The generic synthetic path is gone, and nothing replaced it.

**The new launcher has no explicit real-definition mode**
- `kinetic_sway_proof.py` runs the same `--flips --out` command as the generic callers, through `run_proof(mode="flips")`. `selftest_gss_kinetic_sway.py:264` pins exactly that invocation.
- So the real definition is never explicitly chosen; it is the default for every caller. The registered-definition evidence (`damageDef == RM_Repulse_Palm`, `synthetic is False`) is checked well in `check_result`. But generic callers can't opt out of it, so the parent's "explicit real-definition invocation from the new launcher" is not met.
- No test compares generic default mode with explicit real-definition mode. `test_production_wiring_and_existing_cleanup` asserts the call happens exactly once with no condition. `selftest_gss_proof_drivers.py` and `selftest_gss_restring_proof.py` say nothing about kinetic or M22. The green results in `tests_final2` therefore can't catch this regression.

**Frozen bullets, apart from the issue above**
1. **Probe parsing: met.**
   - The 4-part form still defaults to `Bomb`. The existing callers at `:580`, `:652` and `:914` use that form and still get `cuts`.
   - `kinetic` still maps to the synthetic copy of Bomb (`ExplodeWantsKinetic`), and `synthetic:true` is reported.
   - A registered name is looked up with `GetNamedSilentFail`. An unknown name fails before any explosion. Malformed names are rejected by `ExplodeDamageName` (`AerialMath.cs:1013-1027`): empty, leading digit, `-`, non-ASCII, a 6th part, padding.
   - Whitespace is kept for `explode:` requests, so a padded name can't trim into a valid one.
   - Offline harness: `parser_green` shows `failures=0`. The red runs against the original source (14 failures) and against the pre-fix dispatch (3 failures, whitespace cases) are kept.
   - Tightening: `,bomb` and extra fields used to fall back silently to Bomb and are now refused. No in-repo caller uses those forms.
2. **Real definition, on/off readback, census deltas, span survival: met in the rows themselves.**
   - Every reply must have `success is True`, the matching `cmd`, and a strictly rising `_probeSerial`.
   - The set echo is checked, and the census `kineticSway` must match before and after the blast.
   - Counters must be non-negative ints, not bools.
   - The census `kineticSways` delta must equal the blast's `sways`, be greater than 0 when on and equal 0 when off. The cut delta must equal the blast's `cuts` and be 0.
   - The span must be reciprocally Up, on the same net, with finite hp unchanged.
   - Each arm builds a fresh scene pair. Missing, failed or malformed data gives FAIL, never PASS; the mutation tests cover this.
   - Caveat: the offline double fakes `IsKineticBlast` by matching the defName. The real check goes through the extension type, and only the XML test is evidence for it.
3. **Launcher: met, apart from the issue above.**
   - The command file names both `GimmeSomeSlack, KineticArms`.
   - It requires a fresh output (mtime window), the right script and mode, no abort, no FAIL or UNMEASURED rows, exactly one MOD PASS for each M22 id with the full evidence schema, and a driver return of 0.
   - Every attempt keeps its stdout, stderr and receipt. The registered shell line is executed against a stub driver.

**Source and build identity**
- `build_final2` built `RimMandrakeGimmeSomeSlack.dll` from `0cd82b62db48+dirty`, with 0 warnings and 0 errors.
- The srchash entry for `AerialMath.cs` (`26f58f44…`) matches the `production_math_sha256` printed by the parse harness on the production source.
- I couldn't hash the `AerialProbe.cs` entry (`225a06d9…`) or the DLL itself (`ccb43bfa…`) with read-only tools.
- `parser_green` has no `production_normalization_sha256` line, so it predates the normalization change. The later `tests_final2` run passed the parse test, but the hashes it printed weren't kept.
- Commit `0cd82b6` has no Co-Authored-By trailer, as the parent already noted.

**What it needs:** keep `--flips` and `--live` on the synthetic `kinetic` token, still with the strengthened readback and census-delta checks. Add an explicit option for the real definition (for example `--kinetic-damage RM_Repulse_Palm`) that only `kinetic_sway_proof.py` passes. Make `check_result` require that the explicit mode ran. Add a regression test showing that a normal call with no option sends `,kinetic` and passes without KineticArms, while the explicit mode sends `RM_Repulse_Palm` and needs the registered-definition evidence.

would show: no