# Northstar review — 2026-10-06 (BENCH + GPT)

Asked by the owner, 2026-10-05, typed: *"do a review of the northstar skill, the lessons learned in the two mods
we've done it in, Claude.md, the handoff files from foundry… all of it. Ask gpt for a review of northstar and the
skill and rimworld debugging for tips on faster and deeper validation strategies so we can have excellent
automated validation checkouts."*

**Inputs.** `debug_process.md`, `north_star_validation_spec.md`, `northstar_densification_lessons.md`,
`northstar_time_ledger_2026-10-01.md`, `northstar_human_review.md`, the GimmeSomeSlack consolidation,
`flowworks_remaining_2026-10-05.md`, both walks, `GimmeSomeSlack/proof_all.py`, `skills/rimworld-debug-testing`,
CLAUDE.md's debug and instrument sections, 23 lessons, and the last 20 FOUNDRY handoffs (validation lines).
GPT (gpt-6.1-sol, high effort) read the same bundle: prompt and full answer in
`Transient/northstar_review_2026-10-06/` (14-day shelf; this file is the durable copy of what survived).

GPT's answer is a list of hypotheses, not a verdict (debug_process §5). Each claim below is marked **CONFIRMED**
(tested tonight, the test named), or **HYPOTHESIS** (not tested yet).

## The short version

Checkouts work: Gimme Some Slack went from 15 live runs and ~30 min to one 10-minute proof. What fails is
**evidence**. The proofs that ran are invisible to the project's own scoreboard. Runs keep testing a different
build than the one in the repo. Random test setups waste whole runs, and the docs disagree with each other. The
next gains come from making every run's result durable, attributable and counted, not from more checks.

## Findings

1. **The scoreboard cannot see the two finished checkouts. CONFIRMED.**
   `required_checks_report.py` read "proven 0 of 1543" and listed neither mod. It reads only
   `Transient/modcheck/live_queue/*_summary.json`. `proof_all.py` and FlowWorks' `validation_v2.py` write their own
   JSON beside the mod, which nothing reads. The manifest counts each mod's `validation.py` components, while the
   proofs emit different row ids, so they could not be joined even if read. Wider than the two mods: **108 of
   148 manifest mods (1,783 required checks) have no record the report reads at all**, so "1543" covered only 40
   mods. The report now prints that instead of leaving it out. Owed: `NORTHSTAR_RESULTS_JOIN_1`.
2. **A run's build changes under it. CONFIRMED tonight in one instance.** `selftest_tool_metadata.py` fails because the
   companion DLL lacks 9 tools its source declares (`jawa/static_call`, `jawa/comp_read`, five `flowworks_*`…).
   FOUNDRY's 2026-10-04 handoff names stale deploys as a top cause of taint, and the lessons record
   ModsConfig races under a held bridge lock. HYPOTHESIS (GPT): preflight records hashes but never REFUSES on a
   mismatch between the running DLL and the repo's `.srchash`.
3. **Random fixtures waste whole runs.** 84.7 of 210 minutes in the 2026-10-01 ledger went to runs failing their own
   setup gate (MEASURED there). HYPOTHESIS: GSS's SL4 still depends on how many free colonists a quicktest happens to give.
4. **Live time is mostly harness, not RimWorld.** A clean 13-suite pass was 16.4 min out of 210 (ledger,
   MEASURED). Antiquities waits a fixed 95,000 ticks; 600-tick sweeps make 17–20 calls at ~48 ms each.
5. **Defects are found by looking, not by checks.** FOUNDRY's GSS handoff: *"Every defect this round came from the
   owner LOOKING at the review map, not from a check."* Same pattern tonight: on the Pyrelands sheet, Fire Hawk
   flight frames were offered as walking-art candidates, and the owner wrote *"I don't clearly see those
   options here."* Fixed tonight in the sheet tool (frames now show as one wing-beat set).
6. **`proof_all.py` can lose or overstate evidence. CONFIRMED by reading it:** the result JSON is written only
   after `P.run()` returns, so an exception mid-run loses every row (`main`, l. 701–711); `w.get("success") is
   not False` treats a missing field as success (l. 299); `--only` drops the preflight block unless named.
7. **"Basic checkout" can quietly shrink.** HYPOTHESIS: FlowWorks puts ordinary features (doors, pumps, prison
   rooms) behind the on-request extension proof. Its walk has must-be-true lines without the `→ chain` coverage
   arrow that §2.3 requires.
8. **The docs contradict each other, and there is no single northstar skill.** The guidance is split across five
   documents (~150 KB). Examples: §2 mandates a modcheck `Suite` while both real checkouts are custom
   orchestrators; the review-sheet location is `Transient/` in one doc and the mod's `review/` in another; the
   skill gives both 22 s and 23–30 min as "cold load". "Keep the bridge busy" rewards activity, so a run that
   proves nothing still scores.

## What to do, in order (GPT's top 10, re-ranked by what tonight confirmed)

| # | Action | Cheapest test that proves it worked |
|---|---|---|
| 1 | One result contract: every checkout finalizes a record the scoreboard reads (`NORTHSTAR_RESULTS_JOIN_1`) | GSS and FlowWorks appear with accepted/rejected reasons; a stale synthetic run does not count |
| 2 | Preflight refuses when the running DLL ≠ repo `.srchash` / deployed files; one lock over deploy+ModsConfig+launch+bridge | Deploy an old DLL on purpose: refused before any site is built |
| 3 | Write results as they happen; refuse to certify a run with missing rows, unknown statuses or a skipped preflight | Inject a crash in the last block: the partial JSON survives and is marked not certifiable |
| 4 | Fixed test fixtures with exact prerequisites (pawn count, roles, terrain, incidents off) | Build it 3× from the recipe: identical fingerprint; remove one pawn: refused at once |
| 5 | Batch observations per tick-chunk; bounded `wait_until` instead of fixed waits (Antiquities 95k) | Same faults detected, fewer calls and wall time on a replayed wait |
| 6 | Audit shipped features vs. default checkout scope, FlowWorks first | Disable a shipped mechanic: the default checkout goes red |
| 7 | Extract GSS's one-session orchestration into the shared harness; rerun only what an edit touches | A second multi-script mod converts without copying code; editing review text does not invalidate behaviour proof |
| 8 | Mutation pilot: break the mod on purpose (no-op job, dropped saved field, stale mesh) and require the check to go red | Each named fault is caught by its intended check |
| 9 | Property/metamorphic tests on GSS conduit graphs and FlowWorks liquid accounting; save→load→continue compared against an uninterrupted branch | A seeded failure shrinks to a small reproducible case |
| 10 | One short current "checkout" skill; history moves to an appendix; doc traps become lint | A fresh agent checks out one small mod using only that skill |

Lead metric: replace "bridge utilization" with **accepted required checks per live minute** and **invalid-run
minutes**. Utilization stays a diagnostic.

## Standard checkout recipe (GPT §5, kept as the target shape)

Declare (requirements with stable ids) → offline gate (≤60 s) → identity/preflight (refuse on mismatch) →
fixture (one verified bland map, exact pawns, disjoint sites) → behaviour (positive + negative + toggle) →
one save/load with continuation → experience bars (judge; insufficient evidence is not PASS) → close (log budget,
final identity, expected-row reconciliation, automatic record). Row kinds kept distinct: ENV, SITE, BEHAVIOR,
NEGATIVE, PROPERTY, PERSISTENCE, EXPERIENCE, LOG/PERF.

## Not adopted

- A general headless RimWorld or fake game: GPT itself rates it uncertain; only the narrow fakes that exist stay.
- Anything reopening the owner's whole-section north-star hash ruling (2026-09-17): unchanged.
