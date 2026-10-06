Read every attached file as UTF-8.

You are reviewing the automated validation system ("Northstar") of a large RimWorld 1.6 modding project
(~160 mods, ~630-mod full load list, a 15-minute cold load, a ~22-second minimal-list load, and a live
"bridge" (RimBridge/GABP + a companion C# tool DLL) that lets Python drive a running game: spawn things,
step ticks, read state, save/load, screenshot). Agents (LLMs) author and run the checks; the owner wants
EXCELLENT AUTOMATED VALIDATION CHECKOUTS: fast, deep, trustworthy, and able to say "this mod works" without him.

Two mods have been taken through a full checkout so far: Gimme Some Slack (was MessyConduit: power poles,
conduit styles, colonist-carried hoses; densified from 15 live runs/259 rows/~30 min to ONE proof_all.py run,
144 rows, ~10 min) and FlowWorks (liquids/canals/pits; validation_v2.py + extensions). The attached files are:
the process doc (debug_process.md), the validation spec, the densification lessons, a time ledger of where live
time went, the human-review principles, both mods' walks (must-be-true lines + coverage arrows) and the GSS
proof_all.py, the project's general debug-testing skill, CLAUDE.md excerpts (instruments that lie, traps),
the project's lessons file extract, and FOUNDRY (the autonomous build seat) handoff extracts across ~20 sessions.

One fresh measurement taken tonight (2026-10-06 ~00:00): the project's own lead metric,
required_checks_report.py, prints "TOTAL proven 0 of 1543 required (owner bars 0 of 0)" and its table does not
list FlowWorks or Gimme Some Slack at all (most rows say tainted: stale-deploy / run-identity-unknown).
Treat that as a fact to explain, not as proof nothing works.

Produce a review in Markdown with these sections:
1. **Diagnosis** — the 5-8 biggest structural reasons validation is slow, shallow, or untrustworthy here,
   each tied to specific evidence in the files (quote/cite file + line or phrase). Separate HARNESS cost from
   MOD defects. Include the metric gap above.
2. **Faster** — concrete strategies, ranked by (live minutes saved x mods affected) / build cost. Think:
   what can move offline (def-graph checks, patch application in a headless loader, C# unit tests against
   decompiled types, a fake game), snapshot/fork of a warmed game state instead of rebuilding sites, batching
   many mods per load, tick-budgeting, parallel sites on one map, fewer save/load cycles, incremental reruns
   keyed on what changed, caching bridge discovery, avoiding cold loads.
3. **Deeper** — strategies that catch defect classes the current checks miss: property-based / metamorphic
   tests, invariants run over long simulated time, save/load round-trip diffs of the whole object graph,
   mutation testing of the checks themselves ("a check never seen red proves nothing"), differential runs
   (mod on vs off), log budgets, fuzzing def values, cross-mod interference sweeps, determinism/seed control,
   performance regressions (tick time).
4. **Trustworthy** — how to stop "success: true and nothing happened", UNMEASURED-read-as-pass, stale
   deploys, and run-identity confusion; what the run record must bind (mod hash, deploy hash, DLL srchash,
   mod list fingerprint, harness version) so a metric like the one above cannot read 0 or a false green.
5. **A standard checkout recipe** — the minimal template every mod's checkout should follow (phases, row
   kinds, time budget), generalized from GSS proof_all, plus what the shared harness must provide so each new
   mod's checkout is cheap to write.
6. **Critique of the skill and docs** — what in debug_process.md / the skill / CLAUDE.md is wrong, stale,
   contradictory, missing, or too long to be followed; concrete edits.
7. **Top 10 actions** — ordered, each with: what, why (evidence), estimated build cost, and the cheapest test
   that proves it worked.

Be specific to THIS codebase; generic testing advice without a tie to the files is worth little. Where you are
guessing, say so. Your answer is a hypothesis list that will be tested, not a verdict.
