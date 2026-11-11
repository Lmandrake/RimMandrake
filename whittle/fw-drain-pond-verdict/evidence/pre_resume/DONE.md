# Claim against the frozen statement

- true: When the pond surface falls and its census still contains only deep water, pond_depth_verdict returns FAIL/MOD rather than accepting a partial-depth stage. | evidence: `whittle/fw-drain-pond-verdict/evidence/verdict_comparison.json` `whittle/fw-drain-pond-verdict/evidence/verification.json`
- true: Genuine chest-deep, shallow or thin stages remain acceptable when the existing stable-wet-count and falling-surface conditions hold; a mixed deep/partial census is also valid. | evidence: `whittle/fw-drain-pond-verdict/evidence/verdict_comparison.json` `whittle/fw-drain-pond-verdict/evidence/verification.json`
- true: Existing no-pump, nonapplicable-body, insufficient-reading and shrinking-from-the-rim classifications remain intact, and focused regression checks execute the production predicate and fail against the original false-safe implementation. | evidence: `whittle/fw-drain-pond-verdict/evidence/verdict_comparison.json` `whittle/fw-drain-pond-verdict/evidence/verification.json` `whittle/fw-drain-pond-verdict/evidence/selftest_stdout.txt`

Offline acceptance-instrument repair only. Production removes only the deep contribution to the partial-stage sum; no actual lake appearance is established. Parent retains publication, ledger and closure authority.
