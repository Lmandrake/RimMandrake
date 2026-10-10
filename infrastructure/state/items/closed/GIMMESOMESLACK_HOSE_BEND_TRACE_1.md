# GIMMESOMESLACK_HOSE_BEND_TRACE_1 — trace the nine hose-test failures before he validates

Owner ruling by question card 2026-10-09: trace the nine failures first, then he validates. Evidence: `Transient/foundry_gss_proof_20261006.txt`.

## findings so far (offline read, unproven)
All nine MX_H00..H08 fail on ONE predicate only: `min_bend_radius_ge`, expected >= 0.95 x 1.2 = 1.14, got 0.16-0.68 (flat and plump), on straight, corner and water scenes alike. Straight runs failing at ~0.19 points at the metric (`HoseMath.MinBendRadius(lay.Flat, EndSkip)`, `src/RimMandrake/GimmeSomeSlack/Source/Hose/HoseMath.cs:591`) reading polyline noise or end curvature rather than the laid hose; predicate is `src/RimMandrake/GimmeSomeSlack/northstar_matrix/run_live.py:1015`.

## criteria
- [ ] Offline: reproduce MinBendRadius on the probe geometry; decide metric bug vs real layout under-radius.
- [ ] Fix or reclassify (harness/mod) with evidence; rerun H0-H8 when game is up; then owner validates.
