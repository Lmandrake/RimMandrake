## Verdict — ship with changes

The recurring problem warrants a pre-load check. The proposed automatic inference, mutation and tier machinery need substantial cuts. Census conclusions below are internal-consistency checks against the supplied evidence.

## Findings, ranked by severity

### 1. High — “single owner” does not establish a required mod

A reference can occur in an absence assertion, optional branch, diagnostic, unused function or offline inspection. The existing proof example explicitly checks `--absent RUT_PaleMoss`. Inferring its owner as required would reverse the proof’s intent. Script location and CLI arguments have the same contextual problem. A save header records historical membership, which does not establish that every recorded mod remains necessary. (`relentless_live_round.py:14`)

Consequently, a false positive can add dependencies, trigger deployment holds, or change PASS/FAIL. The claim that false positives only warn contradicts auto-writing “sure” hits.

False negatives also extend beyond dynamic strings. Wrapper scripts, generated commands, helper imports, external fixtures and incomplete deployment indexes can hide needs. Uniqueness within an incomplete index gives misleading confidence.

**Change** — keep inferred requirements advisory until source-specific rules demonstrate necessity.

### 2. High — automatic mutation lacks a validity and persistence protocol

History keys decisions by item, criterion and build SHA. Terminal outcomes stand across subsequent proof edits. Auto-writing requirements into the current books copy therefore needs explicit rules for invalidating prior decisions and recording which proof and environment produced each result. (`relentless_live_round.py:166`, `relentless_live_round.py:193`)

The design also leaves concurrent edits, atomic writes, retries, idempotence and pre-slot commit ownership unspecified.

If `# auto: evidence` is appended inline, the existing parser treats `#`, `auto:` and evidence words as mod names. Require standalone comments or change the grammar with compatibility tests. (`relentless_live_round.py:108`)

### 3. High — exact tiers and absence constitute a separate scheduling feature

These declarations are legitimate requirements, but they expand this work into environment construction and batch compatibility.

Partitioning only by tier misses two default-tier riders where one requires X and another forbids X. Checking inferred needs against an exact tier also fails to establish that the **actual running load** matches that tier.

The semantics remain unsettled. A named tier permits additions, while additions that “turn the tier into something else” are refused without a decision rule. Exactness needs a pinned baseline, dependency policy, mandatory-mod policy and actual-load comparison. `modlist_swap` itself injects a zoom mod. (`modlist_swap.py:247`)

**Change** — move tier construction, absence enforcement and compatible batching into the whole-list lane.

### 4. Medium — the problem is real, but the claimed savings do not follow

The census contains concrete repair cases, but several totals need correction.

- State subtotals sum to **920**, leaving **21** of the claimed 941 unexplained.
- Listed R1–R7 cases deduplicate to **29 IDs**, including two ops IDs, versus the claimed 31.
- Explicit category totals sum to **58** item-games.
- The **34 pre-fix games are not 34 additional masked games**. Their definition includes explicit failures. RAIL_WALK’s explicit game also appears in its pre-fix count.

The 35/38 figure includes any non-PASS row from affected items, so it cannot attribute those loads to missing declarations. The assumed batching shares do not establish 10–15 avoidable loads. Moreover, detecting 17/20 items does not imply saving 85% of cost, especially when some detections only warn.

The 20 repairs, repair durations, sub-second runtime and 300–400-line implementation estimate lack supporting measurements here.

### 5. Medium — several premises understate existing code or depend on unavailable machinery

Proof-only builds already have a cited-build fallback through `build_shas`. The blanket premise that they derive no subject mod requires case-level verification against that path. The helper implementation was not supplied. (`relentless_live_round.py:277`)

Dotted-folder recognition already exists in staging name splitting. (`modlist_swap.py:232`)

Conversely, folder enabling does not implement general recursive dependency closure. It adds immediate dependencies and treats membership in LIVE/FULL as sufficient knowledge. Package-ID closure delegates to a separate, unsupplied helper. (`modlist_swap.py:269`)

`about()` returns package IDs and dependencies, without identifying a canonical composed folder, and prefers deployed metadata. The proposed canonical resolver needs additional discovery and freshness rules. (`modlist_swap.py:177`)

### 6. Medium — verification mostly checks agreement with historical repairs

Human additions are useful labels, but can over-declare requirements. Replaying old proof text against current scripts, DLLs or ownership dumps introduces hindsight leakage.

Add these tests.

- A uniquely owned defName appears only in an absence assertion or optional probe. Expect zero additions and successful execution.
- Remove one genuine declaration from an otherwise complete proof. Verify recovery using matching historical scripts and metadata.
- Batch a leader, a valid rider and an invalid rider. Preserve both valid items.
- Edit requirements after a terminal verdict. Verify decision invalidation and provenance.
- Exercise missing indexes, transitive dependencies and repeated writes.

A controlled live differential run is needed to test whether an inferred addition changes the observation.

## Recommended minimal scope

Ship shared name resolution, verified alias normalization, actionable unknown-name errors, and per-rider validation before unioning batches. Reuse that validation at filing and staging. Keep inference advisory with explicit evidence.

Defer automatic requirement writes, broad namespace/defName indexing, save-header mandates, post-failure writes and tier declarations. Measure recovered failures and marginal reloads before expanding scope.