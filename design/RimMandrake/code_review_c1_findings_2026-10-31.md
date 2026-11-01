# Code review lane C1 findings, 2026-10-31 (item specs)

## FUZZ_CHECKS_FIX_VACUOUS_TAUTOLOGIES

Found by independent code review (lane C1, DIRTY_CODE_REVIEW_LOOP_CONTINUE_NOT_DONE, 2026-10-31, at 8e211541d7).
Fuzz checks that can never fail, so the property they name is untested:

- src/RimMandrake/CrackedLands/Source/SelfTest/CrackedLandsFuzz.cs
  - L178 `Check(s.HeraldBeat > 3 || true, "")` and L179 `Check(rung.Count == 0 || true, "")`: `|| true`, empty messages.
  - L447: another `|| true` check.
  - L316: `soiled.Count == ledger.Active.Count + soiled.Count - ledger.Active.Count` is an identity.
- src/RimMandrake/Wreckage/Source/SelfTest/WreckageFuzz.cs
  - L47 `if (SpecRank(got) != SpecRank(t)) Check(got != t, ...)`: different ranks imply different values, so it cannot fail (L40/L43 already cover the intent; delete or replace). L203 message "x" is uninformative.

Fix: replace each with the real property it meant, or delete it; give each a message. Files stay DIRTY until re-reviewed.
Already fixed in review (trivial, comment only): GravshipLandingFuzz.cs L8 header claimed failures print `| detail`; they do not.

## FUZZ_SHRINKER_FIX_DEAD_ON_THROW

Found by independent code review (lane C1, DIRTY_CODE_REVIEW_LOOP_CONTINUE_NOT_DONE, 2026-10-31, at 8e211541d7).

The fuzz kits' Drive/Shrink only shrinks when the case runner RETURNS a non-null failure string. Most runners fail by
THROWING from `Check()` and always return null, so a failing case is reported unshrunk and the shrinker is dead code.
CrackedLandsFuzz.cs (RunFlood, RunPan) also states in its header that failures print "shrunk ... | actions" — false.

Same pattern seen (by grep, not each read in full) in the BlueDesert, Greentide, LuminousPigment, Oracle (OracleFuzzKit),
TerminalBiomes, MovingDunes, SolarMirrors (FuzzKit), GelatinousSlime, LeaningScrub and Wastes fuzzers; Contagion and
WeepingStones return strings only on some paths.

Fix (one place per kit): have Drive catch the Check exception and treat its message as the failure string, so shrinking
runs; or make runners return the message. Then correct the header claims. Verify by planting a failing check and seeing a
shrunk case printed. Audit each fuzzer before claiming coverage.
