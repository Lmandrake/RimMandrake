# RIMMANDRAKE_REREAD_SCRUB_PINS_AFTER_PYRELANDS_GIANTS_MOVED

Found by the Stage 2 preflight of LeaningScrub 0.1.0 (steward run RIMMANDRAKE_STEWARD_LEANINGSCRUB_PREFLIGHT_STAGE, 2026-11-16); table `design/concepts/LeaningScrub/version/test_table.json` (test T_WILDLIFE_ZERO_PATHS, supports bar `settings`), record `design/concepts/LeaningScrub/version/preflight.json` check C16. Offline-build (Stage 3) work, not a spec fault.

## spec
`src/RimMandrake/LeaningScrub/selftest_scrub_wildlife_zero_paths.py` pins a review fingerprint of every code file that can zero the scrub's wildlife. Its row Z5 is red: `RimMandrake/Pyrelands/Source/RM_PyrelandsGiants.cs changed since review (fingerprint ba4ab711d3e3291a, reviewed a243636a2b2fc529): re-read it`. Re-read the changed file for any new path that zeroes LeaningScrub's wildlife; fix the path if one exists, then re-pin the reviewed fingerprint. Never re-pin without the read.

## criteria
- The read of RM_PyrelandsGiants.cs at its current fingerprint is written down (what changed, whether it can zero scrub wildlife).
- Z5 is green with the new fingerprint, and every other row stays green.

## verify
Acceptance test: `python3 src/RimMandrake/LeaningScrub/selftest_scrub_wildlife_zero_paths.py` exits 0. Watched failing 2026-11-16 (rc 1, `FAIL (1)`, row Z5). Expected: 0 failures.

## refs
file: src/RimMandrake/LeaningScrub/selftest_scrub_wildlife_zero_paths.py
file: src/RimMandrake/Pyrelands/Source/RM_PyrelandsGiants.cs
