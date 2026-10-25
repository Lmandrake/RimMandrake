# Focused testing plan — 2026-10-25

Owner, 2026-10-25: *"Targeted runs should always have been policy."* and *"…focusing aggressive testing only on the
highest value informative tests not rerunning other tests that happen to be nearby or ahead of it."*
Ruling: `standing_rulings.md` §"Live runs are TARGETED". Tags: **[M]** = read in code or run artifacts (file named),
**[A]** = assumed. Policy: the catalogue of checks stays and keeps growing (`debug_process.md` §3, "ablation is later").
What shrinks is the work per change. A targeted green never counts as a suite-wide green; the scheduled sweep catches
anything that targeting missed.

## 0. What tonight cost (evidence: `D:\ClaudeWork\rimmandrake\live_20261025\`, `…\focused_testing_20261025\`)

- **[M] Full runs.** run5–run7 each ran 87 chains and 609–619 rows to prove 1–4 fixes. Chain time was 39.5 min (run6) and 48.3 min (run7), plus an ~11 min full-list load (run7 PROGRESS). Median chain-start interval: 11 s (`chain_minutes.txt`, START→next START, hold included).
- **[M] Offline work inside the live slot, ~15 min.** `core_offline` takes 10.7 min. `rivers_switch_flips` takes 4.5 min because `validation.py:_selftest_cases` shells to the C# SelfTest, which has no per-case filter (Program.cs). The game sits idle meanwhile.
- **[M] Most UNMEASURED rows are stale, not unmeasurable.** run7 had 242 UNMEASURED rows (`unmeasured_classes.txt`).
  - **159** read "no <runner> result at the current mod hash". `status.mod_hash` covers every mod file except validation.py, human_review.py and northstar/. Any Source/ or Defs/ edit voids core_live_rows (63), hose_live_rows (30), thirst (27), drawbridges (13), sprinklers (10), lines (7) and others.
  - **41** ended with their chain: `suite._ComponentCtx._exit` sets `upstream_failed` on any FAIL or UNMEASURED, and every later row records UNMEASURED.
  - **14** read "no predicate yet". **28** are other causes.
- **[M] The site hold is incomplete on the default path.** Unroof, gas clear, weather lock and `Verse.Log.ResetMessageCount` run only under `--situational` (runner.py ~566–608). The default `_hold_site` does kill_hostiles and prepare_bland_map, nothing else. run5's Crush deaths were roof collapses. The `targeting.py` docstring claims "unroof, gas, weather" for every chain, which is false on that path.
- **[M] Targeted runs already work.** run8 ran `extension_proof.py --chains canal_spikes --site-save calm` and got 3/3 PASS in about 1 min.

## 1. Tier ladder: measurement scope × environment profile

Choose two things separately: **scope**, which is the T-rung, and **profile**, which is the min+mod list (default) or the owner's full list (only when the claim is about interaction or the full stack: tile geometry, a foreign patch). On the full list, one probe at the right scope is enough. Never climb a min-list sweep first. Go up a rung only when the current rung **cannot** answer the named question.

| rung | what | exit (stop here when…) | minutes |
|---|---|---|---|
| **T0 offline** | the *relevant* Python mirror (`run_selftests.py --only`), C# SelfTest when C# changed, `validate_patch.py`, static detectors | the changed contract is wholly modelled offline and green, or red (fix offline) | 0.5–1 Python [A]; 4.3 C# [M 255 s] |
| **T1 quick probe** | min-list load (22 s) + quicktest map (~90 s) + one bridge read-back | the remaining uncertainty is one runtime quantity, and it is read | 2–4 |
| **T2 targeted chain prefix** | `modcheck run <Mod> --rows r` (today: whole owning chain [M]; after option A: stops after r) or a northstar runner `--chains x --site-save calm` | the requested rows have a *valid* PASS/FAIL | 3–6 [A, p90 unmeasured] |
| **T3 item chains** | `--item ID` / `--chains` | the item's declared acceptance rows are answered | 5–15 |
| **T4 sweep** | `--full` | diffed against the last sweep; at most daily, a ceiling, not a quota | 50–70 + load |

**Do not test live when:** the change is a refactor pinned by a mirror; it is doc, art or def text already read back statically; no outcome of the row would change the next action; the fix is to the harness (prove it on its selftest or `fakegame.py`, then run one canary); it concerns a flyer's flight.

**UNMEASURED routes; it is not retried blindly:**
- stale result → run that producer runner;
- no predicate → write the oracle;
- site/hold fault → fix the fixture, then **one** retry with the changed condition recorded;
- still impossible → record an open obligation with an owner and stop.

## 2. Picking the minimum row set

**Value of information.** Every selected row names the decision its outcome changes. Take, in order:
1. the reproducer: red before the fix, green after;
2. the discriminating sibling or negative path (the OFF twin, the other fluid);
3. a *small* guard set for the invariants the change could break. Select by changed contract and failure mode, not by mere file overlap, which can pull in a whole validation module;
4. new or materially changed oracles that need demonstrated sensitivity. That can come from a known-bad build, a negative fixture or offline fault injection; a live red is not required.

Optional guards rank by decision value ÷ **incremental** cost (shared setup is free). Drop rows that are adjacent, ahead of the target, or already validly measured.

**Item → rows [M].** `targeting.resolve` unions `--chains`, `--rows` (the owning chain) and `--item` (source or ledger text naming a chain or row). An unmapped item is refused; nothing falls back to the full suite. Two gaps:
- the result is a flat chain set plus prose reasons. **Add per-chain scope** (`{mode: full|prefix, requested_rows, reasons}`), so an explicitly named whole chain overrides a row cutoff, and **print a preview** before launch: requested → prerequisites → executed → skipped;
- `rows_by_chain` keeps a *partial* row list when the probe raises, and its comment says the opposite **[M]**. A chain whose catalogue is incomplete must refuse row targeting and say why.

**Changed files → chains** (`--changed <range>`, including uncommitted files) gives *suggestions* only. Shared helpers, inherited XML and patches are mapped through explicit `INPUTS` groups per chain or runner. When the impact is unknown, the run asks for an explicit selection with a reason.

**Dependency slicing.** A chain is the unit of isolation: the runner gives it a fresh session, a hold and a sweep [M]. Inside a chain, rows share state, but not every earlier row is staging for a later one. Three tools, cheapest first:
- **stop-after:** cut the tail. It must *not* reuse `_guard()`/`upstream_failed`. That latch records UNMEASURED and leaves raw `session.call`s and subprocesses running [M `suite.py` 201, 772]. Use a distinct `StopAfter` signal raised after the last requested component. The runner catches it, runs teardown, and writes trailing rows from the catalogue as `NOT_RUN` without executing their bodies;
- **named fixtures:** split the most expensive chain heads into a fixture builder plus assertions, so a late row runs fixture → row and skips the sibling assertions;
- **staged-site snapshots** (deferred): save at a fixture point and load to run one row. `test_site_saves.py` saves, loads and reads back clean maps [M], but it does not save per row. The key must cover the DLL, the test code, settings and the profile, and Python-side state (fixture ids, log mark, clock) must be re-registered after load.

**Reuse instead of re-run.** External-runner rows (v2, proof_hose, thirst_live, drawbridge_proof, sprinkler_live, lines_proof) should key on a versioned **manifest**: runtime DLL and defs, test/oracle code, fixtures, settings and profile. They should not key on `mod_hash`. A reused row carries `freshness=reused@<run>` as a separate field. It is neither a fresh PASS nor a new failure, and a newer invalidating result supersedes it.

## 3. Debug-resolution loop

1. **Validity before cause.** Each non-PASS row records:
   - *validity* (valid / invalid: the measurement could not be trusted);
   - *suspected cause* (MOD / SITE / HARNESS / UNKNOWN), with a confidence.

   Crush with no instigator, a hostile arrival, colonist count 0, a menu drop or a refused terrain read-back make the row **invalid**: it is re-run, not scored. The incident is still kept as a suspected-MOD lead when the mod could have caused it; it is never erased as noise. These checks extend the existing precondition and surprise paths at component finalization, before `_on_finding` publishes. They are not a new string classifier in the runner.
2. **Shrink** to the lowest rung that reproduces the fault: the T2 prefix alone, then T0 if a mirror can reproduce it.
3. **Bisect** inside the chain with checkpoints. Today `t.checkpoint()` works only in debug mode and before the failure latch, and reads only at the anchor [M]. Add a capture-on-fail before the latch.
4. **Hypothesis log:** `debug_process.md` §2.4 notes. One discriminating row per theory, and `RULED OUT: … — <check>` when a theory dies. For an intermittent fault, set the number of attempts in advance.
5. **Do not let the harness pose as the mod.**
   - **Session preflight:** launch gate, DLL/defs identity against the deploy, profile truth, test-profile grant.
   - **Canary chain:** a small vanilla-only chain, first in every live run. If it goes red, the session is HARNESS and no mod row runs.
   - **Hold as an environment contract:** unroof, gas, weather and Log reset on every path, with exceptions a chain declares, and read back. The Log reset stays before `mark_log()`.
6. Fix the fault, re-run only the step-2 rows plus the step-2.3 guards, and commit with the class and row id.

## 4. Options

**A. Cheap (~1 day): honest, previewed, tail-cut targeting.**
- Selection preview and per-chain scope in `targeting.resolve`.
- Incomplete-catalogue refusal in `rows_by_chain`.
- `StopAfter` plus catalogue-generated `NOT_RUN`.
- Chains tagged `offline=True` skipped live unless `--full` (T0 runs them before launch).
- The hold contract moved out of the `situational` block.
- Phase timing per chain (hold / body / teardown, monotonic).
- Fix the docstring.

Touchpoints: `targeting.py`, `suite.py` (`Suite.chain(offline=)`, `StopAfter`, an execution-state field beside `verdict` in `Component.as_dict`), `runner.py` (`_hold_site`, `run_suite` ~556–700), `FlowWorks/validation.py` tags, `cli.py`, `selftest_targeting.py`, `selftest.py`.
Gain: about 15 min off any run touching offline chains, the roof-collapse class closed, and no tail rows. Risk: medium-low; it changes control flow, so it needs a teardown test with raw calls and subprocesses.

**B. Medium (~2–3 days): A plus reuse and validity.**
- Run manifests and reuse for the six external-runner readers (`validation.py` 208–222, 350–365, ~492–530).
- A new `status.run_manifest()`, with `mod_hash` kept.
- `freshness` / `validity` fields in `record.py`.
- The canary chain.
- Validity checks at component finalization (`suite._ComponentCtx._exit`, `_withheld`).
- `--changed` suggestions.

First, **audit the 159 stale-hash rows** into: reusable / relevant change / never measured / no manifest. Begin capturing manifests at once; history is not reconstructed by assumption.
Gain: most stale-hash UNMEASURED rows become valid reused evidence after unrelated edits, so UNMEASURED comes to mean "could not ask". Risk: an under-declared manifest reuses a stale result. Mitigation: conservative artifact hashes (the DLL hash invalidates every C# row), a measured hit rate, and the sweep re-measuring.

**C. Ambitious (~5 days): B plus named fixtures for the costliest heads, staged-site snapshots, and a history-ranked row proposer.**
Gain: a late row in about 1 min. Risk: snapshot validity, fixture re-registration, upkeep.

**Recommendation: build A, then B.** A is shippable alone. B removes the largest measured UNMEASURED cause. C waits until A's phase timing shows that chain heads are the remaining cost.

**Expected saving per fix [A]:** today a fix costs a T4 run of 65–115 min. Under A+B it is T0 (1–5 min) plus T2 (3–6 min), so **~60–100 min per fix**, provided the rows sit in a few median-length chains. This is a hypothesis: after A ships, report the median and p90 over the first ten real fixes.

## 5. Metrics (from records; A adds the missing fields)

- **Live minutes to an actionable decision**, median and p90, unresolved attempts included. Sources: phase timing (A) and the run JSON `summary.targeted.item` [M field exists]. Ledger close times give the wall clock.
- **Requested measurements answered ÷ attempted**, with reason codes for the rest.
- **Non-essential execution:** minutes spent on prefix/tail rows and offline-in-live work.
- **Rows executed per resolved item**, a diagnostic only. Tonight ≈ 600 per fix.
- **UNMEASURED by cause**, with the run7 classifier as the baseline (159/41/14/28).
- **Reuse:** eligible, hits, and disagreements found by the sweep.
- **Misses:** sweep FAILs on rows that targeting omitted for a matched build.
- **Invalid attempts per live attempt.**

A `modcheck metrics` reader computes these. Runs shared by several items count once for each item, and that rule is stated in the output.

## GPT critique: adopted / rejected

Source: `D:\ClaudeWork\rimmandrake\focused_testing_20261025\gpt_critique.md` (26 points, checked against code).

**Adopted:**
- the StopAfter signal instead of the `upstream_failed` latch (#7, verified at `suite.py` 201/772);
- the incomplete-catalogue refusal (#6, verified: `rows_by_chain` keeps partial rows despite its comment);
- per-chain scope plus a preview, and T2 renamed "chain prefix" (#3, #5);
- execution state and freshness as fields, not verdict strings (#20, verified: `PASS(UNVERIFIED n)` already overloads `verdict`);
- validity separated from cause, with UNKNOWN kept as a lead (#15, #16);
- UNMEASURED routing with bounded retry (#17);
- a manifest key, and the 159-row audit before claiming reuse (#18, #19);
- environment profile kept separate from rung (#12);
- the hold as a declared, read-back contract (#14);
- checkpoint limits and capture-on-fail (#23, verified);
- decision-time and answered/attempted metrics, phase timing, and savings stated as a hypothesis (#24–#26);
- explicit-coverage policy wording (#2);
- "relevant" offline checks only (#4);
- named fixtures before snapshots (#8, #22).

**Rejected or narrowed:**
- #1: the [M] claims GPT could not check were read in `runner.py`, `status.py`, `validation.py` and the run logs, which were not attached. Each claim now names its file.
- #11: "a check never seen red proves nothing" is house doctrine (`debug_process.md` rung 3) and stays. Adopted only GPT's point that the red may come from a known-bad build, a negative fixture or offline injection, not necessarily a live run.
- #13: settings restoration is already a row (`Z_settings_restored`); only identity attestation was added to preflight.
- #21 (weak oracles): valid but outside this plan; it needs a separate oracle-strength audit item.
