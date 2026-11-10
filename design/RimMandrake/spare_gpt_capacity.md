# Spare GPT capacity before its refresh

A standing brainstorm: what to point GPT (Codex) at when its weekly allowance will reset unspent and Claude's is
tight. General ideas first; each gets refined into a concrete runner or item later.

Started 2026-11-09 8:40 PM PST. Measured then (from Codex's own session logs, `ops_watch.c_codex`): 50% of the
weekly Codex quota used, reset in 26.1 h (Tue 2026-11-10 ~10:40 PM PST). Claude: nearly out. Owner, verbatim:
*"Please switch to as much of the work as possible done by GPT. We are nearly out."* and *"what can we use all that
CODEX capacity for? Any build items we could have it knock out? Art reviews?"*

## The constraint that shapes everything

Every GPT job today still has a Claude agent around it: a thin Sonnet helper that applies GPT's SEARCH/REPLACE,
builds, runs the selftests and lands the work (tonight's GSS cleanup: 9 GPT rounds, 10 items closed, about 70k Claude
tokens). So "spare GPT" is only spare while the Claude wrapper stays thin. The biggest win is whatever lets Codex
run **without** a Claude wrapper.

## Ideas (Conductor's seed list)

1. **A Codex-only runner.** `codex exec` in a pooled scratch clone, given one item and its acceptance check. A plain
   script (not an agent) runs the build and selftests and lands only on green. Claude is not involved at all. This is
   the enabler for most of what follows.
2. **Burn down the offline backlog.** About 1,100 open items need only offline work. Start with the well-specified
   ones: those with a named selftest, validator or compiler outcome.
3. **Clear the code-review debt.** Every file is DIRTY until a full-file review says CLEAN. Run Codex reviews across
   the DIRTY set, starting with the most-used mods, and mark files clean on Codex receipts. Findings become items.
4. **Settle reconcile items.** The top of the Conductor's queue is RECONCILE items: commits already exist, and someone
   has to rule whether they complete the item. GPT can judge commit against item text and return the verdict line.
5. **Art pre-review.** GPT reviews art sheets well (owner, 2026-10-23). Use it for art-eval second looks,
   `prereview.json` for pending sheets, and facing/scale checks, so nothing reaches the owner unread.
6. **Draft the designer first-touch passes.** About 60 items need the owner to sign off a mod's expanded spec. GPT
   can draft the spec expansions and validation strategies, so his sittings are spent judging, not waiting.
7. **Audit the checkers.** Mutate selftests to prove they can fail (mutate-your-checker). Tonight two GSS fixes landed
   without that proof.
8. **The log junk.** Work the fixes in `D:\ClaudeWork\rimmandrake\logspam\REPORT.md`
   (`RIMMASTER_TRACE_FULL_LIST_LOG_CRUD_SIX_OFFENDERS`): silencing patches, the Beer guard, the unattributed
   "non-compressible thing" line.
9. **Doc truth sweep.** Find statements in design docs and skills that the code now contradicts, and propose
   deletions (wrong material is deleted, never superseded).
10. **Prep for Wednesday.** Pre-chew the four items set for Wednesday (phone alerts, Artisan part B, Pyrelands
    footprints, the Pocock skills trial), so each arrives as a one-page brief with the decision isolated.

## Guard rails

- No owner-only decisions (delegation_policy section 2) and no live game: Codex cannot drive the bridge.
- A close needs a test that was shown failing without the fix. A "GPT reread it and found no defect" close is weak,
  and is marked so on the item (five such closes on 2026-11-09).
- If Codex reports exhausted, stop; never move the work to Claude.

## GPT's own answer


GPT via `gpt_consult.py --round spare_gpt_brainstorm`, 2026-11-09 ~8:50 PM PST, given CLAUDE.md, this seed list and
delegation_policy.md. Kept verbatim. Its cost figures are its own planning guesses, not measurements, and the CLI
flags and URL it cites have not been checked.

- **Ranked uses.** Cost ranges below are planning estimates of total model tokens per unit, including review—not measured weekly-quota percentages. Calibrate them against `ops_watch.c_codex`; quota conversion is currently **UNMEASURED**.

1. **Remove the Claude wrapper.**
   - **Run:** Add a script-driven Codex worker to `rimflow/relentless.py` and its existing Builder/Test-builder/Judge flow. Reuse `scratch_clone.py`, `winbuild.py`, `run_selftests.py` and `./publish`.
   - **Accept:** Canary jobs prove that a valid fix lands, a bad fix fails, weakened assertions are rejected, interrupted jobs recover, and publication failure never closes an item. An operational item additionally needs a running timer/service and a successful `rimflow close --live …`.
   - **Cost:** 150–350k for a bounded first implementation.
   - **Guard:** Accidentally creating another builder beside Relentless, or trusting the worker’s own “green” report.

2. **Prove the acceptance checkers catch defects.**
   - **Run:** For one selftest, seed realistic faults in disposable copies: reverse a guard, omit a patch, corrupt a receipt, break `.srchash`, substitute stale evidence. Start with the GSS checks mentioned in the seed.
   - **Accept:** The unchanged implementation passes; each specified mutant fails for the intended assertion. The controller reproduces those results.
   - **Cost:** 30–90k per checker.
   - **Guard:** Counting syntax errors, missing imports or timeouts as successful mutation detection. Mutate the subject being checked, not merely the assertion.

3. **Fix bounded offline defects.**
   - **Run:** Claim one eligible item; add its regression; run `winbuild.py <Mod|csproj>` where relevant and `run_selftests.py --only <tests>`. Include locally reproducible causes from `logspam/REPORT.md`.
   - **Accept:** The same regression fails on the unfixed revision and passes with the fix; affected checks pass; required full-file reviews are CLEAN.
   - **Cost:** 40–130k per item.
   - **Guard:** Treating compilation as proof of gameplay, suppressing symptoms, or bypassing first-touch certification.

4. **Resolve RECONCILE items with evidence.**
   - **Run:** Map every item criterion to the existing commits and replay its named acceptance checks against the relevant revisions.
   - **Accept:** Every criterion has current, hash-bound evidence. Where applicable, the regression fails before the existing fix and passes after it.
   - **Cost:** 15–50k per item.
   - **Guard:** Closing because the commit message sounds right. Missing live evidence means the item remains open with that precise dependency.

5. **Check effective XML, packaging and dependency contracts.**
   - **Run:** Parse defs and patch-added rosters; run `skills/rimworld-modding/scripts/validate_patch.py <path> --defs …`. Add fixtures for missing patch targets, ignored top-level `MayRequire`, unset `animalDensity`, naming and texture-reference failures.
   - **Accept:** Valid fixtures pass; deliberately broken fixtures fail; actual patches match their intended targets against the fingerprinted design inputs.
   - **Cost:** 30–100k per mod or patch family.
   - **Guard:** Reading only BiomeDefs, counting `<li>`, reporting zero-tile biomes, or inventing DLC-absent test tiers.

6. **Review reachable, consequential DIRTY code.**
   - **Run:** Start with shared utilities, persistence, patching and frequently used mods. Check reachability, read the whole file, then use `code_review_status.py check <path>` and its documented `mark-clean` procedure.
   - **Accept:** A complete review receipt identifies the content hash, callers, invariants and examined failure paths. Concrete findings receive reproducers where possible; fixed files are reviewed again.
   - **Cost:** 15–60k per modest file.
   - **Guard:** Mass-marking CLEAN from spot checks. A legitimate “no findings” review can earn CLEAN; it cannot substitute for an item’s acceptance proof.

7. **Fault-test the operational machinery.**
   - **Run:** Exercise `rimflow`/deadman behavior with expired readings, duplicate alarms, interrupted publishes, stranded clones and missing promises. Use isolated fixtures rather than disrupting running services.
   - **Accept:** Broken promises reopen the **same item**; duplicate alarms remain deduplicated; recovery preserves work. Operational installation closes only after its actual `--live` check passes.
   - **Cost:** 40–110k per failure family.
   - **Guard:** A mock-only success being reported as a running operational fix.

8. **Perform independent art pre-review and measured geometric checks.**
   - **Run:** Search `artpipe_state.py find` and `.decisions.json` first. Give a fresh reviewer the actual images, `art_judge_brief.md`, canon constraints, true-scale views and facings.
   - **Accept:** Per-artifact `KEEP`/`REDO`/`UNSURE` receipts and valid prereview metadata. Geometric corrections additionally require measured before/after improvement, independent judgment, archived bytes and ledger installation.
   - **Cost:** 15–60k per bounded batch; calibrate image-heavy jobs separately.
   - **Guard:** GPT silently replacing a required judge. `Agent_Policy.md` still controls; unavailable required judges leave candidates pending. No flyer screenshot experiments.

9. **Keep documentation true through executable claims.**
   - **Run:** Take one document, extract factual claims and check them against code, executable help and authoritative rulings. Correct provably false text; add repeatable checks for mechanical claims.
   - **Accept:** Each correction cites a counterexample or authoritative source; applicable documentation checks pass. Skill edits happen only in the required fresh-context curation sessions.
   - **Cost:** 20–70k per document.
   - **Guard:** Treating unimplemented design intent as false documentation, deleting owner rulings, or editing hash-bound north-star prose without the required revalidation path.

10. **Prepare first-touch Designer and owner sittings.**
    - **Run:** For one `<FOLDER>_DESIGN_FIRST_TOUCH`, read the code/spec, expand requirements and validation strategies, and isolate unresolved decisions. Apply the same approach to Wednesday’s four named topics.
    - **Accept:** A fresh reviewer checks source references, requirement coverage and ruling compliance. Accept the **draft brief**, while leaving certification and reserved decisions open.
    - **Cost:** 50–150k per mod; 15–40k per narrow sitting brief.
    - **Guard:** Producing polished speculation or silently converting a draft into certification.

- **Runner design: no Claude orchestration.**
  - **Placement:** A proposed `src/RimMandrake/rimflow/codex_runner.py`, used by Relentless’s existing places. Direct readings and already-approved one-off work remain helper jobs, consistent with the November 6 narrowing. Read `CHARTER.md`, `GIT_WORKFLOW.md`, `Agent_Policy.md` and relevant trap files before implementation; their interfaces are not established by these attachments.
  - **Selection:** Obtain authoritative queue state through `rimflow`, not prose greps. Require: unclaimed/unblocked item, permitted authority, certified first touch or system exemption, offline acceptance, bounded scope, and available policy-required judge. Rank by downstream items unblocked, recurring impact and reproducibility, divided by measured cost; oldest wins ties. Claim atomically and coordinate file ownership with existing workers.
  - **Isolation:** Lease an idle, pushed clone through `scratch_clone.py`; respect the 16-clone/70-GB limits. No worktrees, mirror writes, deployment or bridge access. Start with one worker. Serialize Windows builds until staging isolation is demonstrated.
  - **Invocation:** Use an argument array with `shell=False`, stdin for the prompt, and Windows paths visible to `codex.exe`. A startup canary must verify that Windows and WSL see the same clone, SHA and edits. The invocation shape is:

    ```text
    codex.exe -a never exec --sandbox workspace-write --json
      --output-schema <receipt-schema> -o <receipt> -C <clone> -
    ```

    These structured-output and sandbox options are documented in the [official CLI reference](https://learn.chatgpt.com/docs/cli/reference). Pin and verify the installed CLI; resolve model settings from `Agent_Policy.md`.

  - **Prompt shape:**

    ```text
    Item ID and exact criteria; base SHA; permitted paths.
    Governing rules and required reading.
    Frozen acceptance commands and expected failure.
    Implement the smallest complete change and regression.
    Do not publish, close, edit ledger files, loosen bars,
    alter acceptance gates, deploy, or use the bridge.
    Return: candidate / no-change / blocked, changed paths,
    criterion-to-evidence map, remaining requirements.
    ```

  - **Independent gate:** The controller owns the acceptance plan outside worker-writable files. It checks the diff, reproduces red/green evidence, builds, runs affected selftests and invokes a fresh policy-compliant reviewer. Changed test coverage cannot erase the original acceptance requirement. Receipts contain source hashes, commands, exit statuses and expected assertions; the controller verifies them rather than accepting claimed results.
  - **Landing:** Review changed files fully; commit explicit paths in separate calls from writes; retain DLL `.srchash` pairs. Run `./publish`, require `PUBLISHED <sha>` and verify that published content matches the checked candidate. Changed integration content requires rechecking. Only then use `rimflow close`; incomplete live criteria remain open. All ledger mutations go through `rimflow`; add missing receipt-ingestion support rather than writing around it.
  - **Weak-close prevention:** `no-change` is an observation, never an automatic close. Reconciliation needs proof; test-building needs demonstrated defect detection; art needs the prescribed verdict. After two bounded repair attempts, record the concrete blocker and return the item without pretending completion.
  - **Recovery:** Persist the phase and candidate SHA so restart can distinguish “published but not closed” from “never published.” Preserve partial work promptly under the clone policy; never discard or reuse a clone containing unlanded work.
  - **Quota stop:** Read fresh short-window and weekly limits from the existing `ops_watch.c_codex` instrumentation. Initially reserve 10 percentage points; later reserve at least one measured high-cost job plus recovery. Launch only when estimated builder **and judge** cost fits both windows. Unknown/stale readings stop launches. Exhaustion stops the pool without Claude fallback; finish deterministic preservation steps. Re-enable only after observing refreshed quota, not merely reaching the predicted reset time.

- **Additional uses where independence matters.**
  - **Blind specification tests:** Give a fresh Codex session the approved contract without the implementation; compare its tests with implementation-derived tests. Disagreements expose assumptions shared by maker and checker.
  - **Review the five weak closes:** Attempt to falsify each completion claim. Reopen the same item when acceptance is missing; add reproducers instead of another reassuring review.
  - **Incident replay corpus:** Turn `instrument_traps.md` and `tool_traps.md` incidents into fixtures: `id` versus `item`, missing-directory counts, CRLF, stale fingerprints and wrong first-exception attribution.
  - **Metamorphic tests:** Reorder independent XML entries, translate identical shade geometry, rotate directional assets, and vary serialization round trips. Equivalent inputs should preserve specified behavior; these avoid duplicating implementation formulas.
  - **Research with expiring assumptions:** Investigate one disputed engine behavior using inspected assemblies, official inputs or minimal reproducible experiments. Record version/fingerprint, evidence and uncertainty. Never re-freeze `official`.
  - **Art reference retrieval and reuse:** Find existing approved candidates, duplicate redraw requests and missing facings; produce constraint-specific briefs before spending generation capacity.
  - **Documentation archaeology:** Find contradictory instructions that would send a fresh agent toward retired FOUNDRY ownership, rename gates or alternative-world generation. Correct clear contradictions; route ambiguity without inventing a ruling.
  - **Acceptance economics:** Measure quota, retries, judge rejection and owner reversals by job class. Optimize reliable completed work and removed blockers—not tokens consumed or ticket count.

- **Seed ideas to reject or narrow.**
  - **“Burn down the offline backlog” indiscriminately:** “Offline” is insufficient; require a trustworthy oracle, authority and first-touch eligibility. Do not treat the seed’s approximate counts as current measurements.
  - **Blanket CLEAN and RECONCILE sweeps:** They can manufacture confidence without reducing defects. Prioritize consequential files and require evidence appropriate to the claim.
  - **“Silencing patches” as a log-cleanup objective:** Repair invalid behavior first. Suppression is acceptable only for proven redundant diagnostics, with important errors still observable.
  - **Automatic art approval from GPT receipts:** Useful second looks do not override the judge ladder, owner-kept protections, bans or installation guards.
  - **Broad doc/skill rewriting:** High churn can erase intent and authority. Prefer narrow corrections backed by executable evidence.
  - **Quota burning itself:** Start with the runner and checker proofs, then spend the remaining window on bounded fixes and evidence-backed reconciliations. Do not begin large speculative features merely because capacity expires.