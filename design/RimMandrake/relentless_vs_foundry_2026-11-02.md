# Relentless vs FOUNDRY: measured comparison (read-only, 2026-11-02)

Windows, all 29.82 h long:
- **R_win**: 2026-10-31T23:47:02Z to 2026-11-02T05:36Z. Relentless and FOUNDRY both ran.
- **F_pre**: 2026-10-30T17:58Z to 2026-10-31T23:47Z.
- **F_pre2**: 2026-10-29T12:09Z to 2026-10-30T17:58Z.

How I counted closes. A close is the first time an item reaches state `done` in a full `model.replay()` of the ledger. I recorded every state change with the `observe` hook, so `implemented`, `verify` and `live` count as closes when they finish an item. "Relentless" means the 100 items that have a `done` row in `journal.jsonl`. The ledger records all 100 of those closes under the BENCH seat.

Scripts and raw output are in this scratchpad: `trans.py`, `trans.jsonl`, `cls.py`, `rows.json`, `mix.json`, `usage.py`, `r1..r8.txt`, `u_*.txt`.

## Headline (M = measured, I = inferred)

| | Relentless (R_win) | FOUNDRY F_pre2 | FOUNDRY F_pre | FOUNDRY R_win |
|---|---|---|---|---|
| Closes | 100 (M) | 32 | 25 | 22 |
| Closes per hour | 3.35 (M) | 1.07 | 0.84 | 0.74 |
| Closes started by the seat (claim/start/lease) | 100 | 24 | 11 | 18 |
| Bulk closes (5 or more within 2 min) | 0 | 0 | 0 | 0 |
| Weighted tokens (weighted_v1) | 215.0M from spend files; 186.4M from transcripts | 78.9M | 127.6M | 81.2M |
| Tokens per close | 2.15M all-in; 1.59M counting only the 100 closed items | 2.47M | 5.10M | 3.69M |
| Independent pass before close | 100/100: closes need a blind checker pass | 1/32 | 0/25 | 0/22 |
| Reopened after close | 15 reopened by the RUNNER live sweep; 13 re-closed within about 1 h; 2 still open | 0 | 0 | 0 (the instrument cannot see these) |
| Agent-hours | 42.6 across 420 measured runs, so 1.43 workers on average (rules allow max_workers 10) | 1 seat | 1 seat | 1 seat |

Caveats on the table:
- **FOUNDRY tokens** are the weighted sum of its seat transcripts: `~/.claude/projects/-home-mandrake-rm-foundry` plus `-seat-tmp-FOUNDRY*`, de-duplicated by message id, using the same weights as `role_launch.TOKEN_WEIGHTS`.
  - The instrument is sound. Run on the Relentless clone transcripts it gives 186M. The spend files give 165M measured plus 50M of reserve estimates.
  - FOUNDRY's tokens also pay for work that is not closing: filing items, notes, and its arena/trio harness. Any trio helpers that run on non-Claude models (GPT/codex) are UNMEASURED.
- **Relentless overhead**: the BENCH conductor seat used 135.7M in R_win, against 101M in F_pre. Some of the roughly 35M extra may be conductor attention spent on Relentless. I cannot attribute it.
- **23% of Relentless spend is estimated, not measured.** 42 runs were charged the flat 1,200,000 reserve (50.4M of 215M) because no usage was captured: worker_full, lost and killed runs.
- **Relentless USD**: the 420 runs that report a cost total $541 at API-equivalent prices (work $392, check $146). The reserve-charged runs have no USD figure.
- **"Stuck"**:
  - Relentless: 98 of 100 items are still `done` at the end of the ledger (11:54Z on 11-02, 6 to 30 h after each close).
  - 13 of the 15 reopens were environmental, not item defects. Nine came in one sweep at 17:33Z on 11-01 ("rm-ops-watch.timer inactive") and all were re-closed at 18:33Z.
  - The 2 still open: PULSEUPDATE_FIX_DRVFS_PULL_TIMES_OUT (a staleness reading at 04:03Z, at the start of the outage) and OPS_NIGHTLY_RED_DIAGNOSE_LNTM (new selftest reds that were not listed).
  - FOUNDRY shows 0 reopens out of 968 October closes. That number does not show FOUNDRY closes held up. Rimflow only reopens a `done` item through a `live` reading or a fail recorded after the close (`afterClose`), and FOUNDRY's items mostly carry no live promise. **FOUNDRY's stuck rate is UNMEASURED.**
  - Follow-up items filed with `caused_by` pointing at a closed item: Relentless 1/100; FOUNDRY 3/32, 2/25 and 1/22. Too thin to use as evidence either way.

## Quality: how often workers overclaim (M)

- The blind checker started 198 checks.
  - 46 ended blind_fail and 33 ended proof_weak, so about 40% of checks rejected the candidate.
  - 38 of the 100 closed items were rejected at least once (28 blind_fail, 12 proof_weak). 61 passed with no blind_fail, proof_weak or bad_candidate.
- **So the worker's own "done" was wrong or under-proved on about 4 in 10 items.**
  - FOUNDRY closes almost entirely on its own evidence: 1 independent pass in 79 window closes. A few FOUNDRY item titles say "blind GPT review before close", but no `verify` event records those reviews.
  - Inferred: FOUNDRY's self-verified closes overclaim at a similar rate, because the kind of work and the kind of agent are the same. I have not measured this.
- **The brief's failure counts (blind_fail 37, proof_weak 16, ...) undercount.** The `failures` dict in each state.json loses history. For example, CLOSE_GATE ended 3 generations on blind_fail and its state still shows `blind_fail: 0`. The journal `acts` give the full counts: blind_fail 46, proof_weak 33, worker_full 9, worker_lost 4, close_refused 4, checker_lost 3, bad_candidate 2, live_broken 3.
- Returns among the 100 closed items: 0:52, 1:25, 2:13, 3:6, 4:4. This matches the brief.
- Median spend rises with returns: 0.66M, 1.76M, 2.76M, 3.26M, 3.59M.

## Item mix (M)

| | Relentless (100) | FOUNDRY (79 closes across the three windows) |
|---|---|---|
| Median files changed in the closing commit | 3 | 2 |
| Median lines changed | 63 | 47 |
| Tooling / mod / design / ledger-only commits | 84 / 8 / 5 / 3 | 61 / 10 / 1 / 7 |
| Needs the live game (`bridge`) | 0 | 10 |
| Median item age at close | 270 h (old backlog) | 2 to 8 h (mostly items FOUNDRY filed itself, often the arena/trio harness) |

How to read this:
- Both processes mostly closed tooling items, and the commits are about the same size. Relentless's are slightly bigger.
- Relentless took offline items only; FOUNDRY carried every live-game (bridge) item. Relentless enrolment excluded the hard live, owner and design items through `pool_ids_exclude`.
- A 10-item sample of each is in `sample.txt`. Relentless: ARMOURY retire of a dead ABF reference (13 lines), RESTART_JOIN build (748 lines), MISSION_PAGE build (176 lines), several OPS_* alarm diagnoses. FOUNDRY: ARENA_* harness steps (53 to 328 lines), two 1-line Contagion/WorldMap bridge tweaks, the TRIO critic fix.
- **Verdict on mix:** the work is comparable, but Relentless's pool was easier. It contained no live-game items, and the riskiest items (owner-gated, worldgen) were excluded.

## Waste in Relentless (M unless marked)

- **Repeated blockers.**
  - 8 items had 3 or 4 generations end on the same non-work cause, costing 16.0M tokens:
    - STONE_BUILDSTATS (blocked_by_predecessor x3; only 0.38M, because each pass was cheap)
    - SEKKULAATH (judge_needed x4, 3.7M)
    - WARLAB (judge_needed x3)
    - REPAINT_SAVES (blocked_on_dependency x3, 2.1M)
    - LIVE_PROOFS (contract_unprovable x3)
    - IDLE_SEAT (contract_missing_live x3)
    - WORLD_REMAKE (gate_not_met x3)
    - COMB_HOLDS (gate_unmet x3)
  - STONE's gen-5 worker wrote: "Fourth identical recheck: supervisor should gate restaffing on predecessor state." What finally worked was the gen-7 redesign, which delivered the item's own substance (a table plus a checker) without waiting for the predecessor.
- **Long chains.** Generation increments twice per attempt (once on lease, once on fail), so gen 20 means 10 worker attempts.
  - 25 items reached gen 6 or more. They spent 74.2M, 35% of all spend, and only 11 of them closed (37.3M).
  - CLOSE_GATE_ENFORCE_DONE_IS_EARNED reached gen 20 for 6.2M: 3 bad_candidate, 3 "au", 3 blind_fail, then parked_by_owner. It was still being staffed after the owner's block at 23:32Z; that gap is filed as RELENTLESS_FIX_PARKED_ITEM_STILL_STAFFED.
- **Spend on items that never closed:** 56.4M (26%) — held 17.7M, retired 13.4M, closing 12.2M, queued 8.7M.
- **Clone churn.**
  - 105 clones released and 413 clone attempts. One pool clone measured 3.6 GB, so roughly 378 GB was written and deleted in 30 h.
  - 99 `remove_failed` alarms: deleting the clone directory failed with ENOENT.
  - That this churn fragmented the sparse VHDX and broke the disk is INFERRED, not measured.
- **Machine limits.**
  - The supervisor stepped down 5 times on OOM kills, once on the day-spend jam (15:03Z on 11-01) and once on a breaker cool.
  - From 06:25Z to 13:31Z on 11-01 nothing closed for 7.1 h.
  - Waiting: 81 mod_busy waits, 63 closed_waiting_for_seat, 41 close_retry.
  - Average concurrency was 1.43 against a cap of 10. **Throughput was limited by the host, not by the loop.**
- **Lost runs:** 4 worker_lost, 3 checker_lost, 9 worker_full (context exhausted). These make up most of the 42 reserve-charged runs.
- **After the restart:** the journal keeps running to 11:32Z on 11-02. STONE gen 7 committed 8038889d89 at about 11:33Z on state that had survived the outage, with no integrity check first. This matches the brief; I did not audit the damage further.

## What FOUNDRY's notch-at-a-time style loses (M)

- **Parked inventory.** At R0, 581 open FOUNDRY-owned items had been touched by FOUNDRY (claim/start/note/implemented/verify/lease) and then put down.
  - Median age 23.4 days; median 21.4 days since FOUNDRY last touched them; 495 untouched for more than 7 days.
  - Their states: 281 built, 146 validated, 84 proposed, 52 doing, 18 ready.
- **Open FOUNDRY items today:** 1,484.
  - 517 are built or validated and need the live game (bridge). These are parked waiting for a live look.
  - 63 are `doing` and offline: picked up and never finished.
- **Pickups per close.** Of FOUNDRY's 439 October closes that had a start, the median took 2 pickups (mean 2.0; 18 took 3 or more). Median first-start-to-done was 0.1 h, but the 90th percentile was 14.7 h.
  - So most FOUNDRY closes are finished in a single sitting. The cost of putting items down shows up instead in the 581-item parked pile, which never closes.
- **Context reload cost per pickup: UNMEASURED.** No per-item token attribution exists for FOUNDRY.
- Relentless comparison: median enrol-to-done 1.8 h (90th percentile 8.5 h), and 0.33 h from the start of the final attempt.

## Improvements to Relentless, ranked by value for cost

1. **Hold an item on a blocker cause instead of restaffing it.** Applies to blocked_*, gate_*, judge_needed, contract_*, parked_by_owner and owner blocks. Hold until the named predecessor's ledger state, or the block, actually changes. Also make the supervisor read rimflow `block` before leasing. A small code change. It removes the 16M of repeated rechecks and the 6.2M CLOSE_GATE chain (the fix is filed as RELENTLESS_FIX_PARKED_ITEM_STILL_STAFFED).
2. **Reuse clones instead of creating and deleting 3.6 GB per item.** Keep a fixed pool of warm clones and reset each between items (fetch, detached switch to origin/main, `git clean -fdx`), or use shared-object clones. This cuts about 378 GB of churn to a constant pool and removes the remove_failed alarms. It probably also helps the OOM step-downs and the VHDX fragmentation (inferred).
3. **Run an integrity check at boot and after every step-down.** Parse every state.json, journal and spend file; scan for NUL bytes and zero-length files; check `git fsck` and the clone state; refuse to stage up on damage. Cheap. This is the failure that hit after the outage.
4. **Cap the escalation ladder.** After 2 rejections of the same class (blind_fail or proof_weak), the next generation must change approach (split, redesign, or deliver its substance standalone, as STONE gen 7 did) or hand the item to a person. Add a per-item token ceiling of about 3M before forced review. Items at gen 6 and above took 35% of spend for 11 closes.
5. **Measure every run.** Capture usage from partial or stream output for worker_full, lost and killed runs; 23% of spend is currently the flat 1.2M reserve. For worker_full (9 runs), checkpoint and hand off before the context fills.
6. **Fix memory headroom, then raise concurrency.** At 1.43 workers on average, the loop is idling on OOM and spend limits. With items 1 to 3 in place, 3 to 4 steady workers should roughly double closes per hour (inferred).
7. **Stop environmental flaps from reopening items.** When the live sweep sees one environmental cause (a timer inactive, a stale reading), raise one incident rather than reopening N done items. 13 of the 15 reopens were this.
8. **Give FOUNDRY closes the same blind checker,** or at least sample them. That would measure FOUNDRY's overclaim rate instead of inferring it, and make the comparison fair.
9. **Add a regression instrument for both processes.** Rimflow forbids reopen, so record "found broken after close" explicitly; at present FOUNDRY's stuck rate is invisible.
10. **Teach Relentless to lease the bridge** so it can take live-game items. Only after 1 to 3 are done; this is the largest change and the riskiest.

## Verdict

- **Measured:**
  - In the same 29.8 h, Relentless closed 100 items against FOUNDRY's 22 to 32, about 3 to 4 times as many. Tokens per close were the same or lower (2.15M all-in against 2.5M to 5.1M).
  - Every Relentless close passed an independent blind check, against roughly 0% for FOUNDRY.
  - That check rejected 38% of items at least once, so worker overclaim is real and common.
  - 98 of 100 Relentless closes still stand.
  - The two processes' items are comparable in kind (about 80% tooling) and in commit size.
- **Not measured, or tilting the comparison:**
  - Relentless's pool excluded live-game, owner-gated and design-heavy items, which are the work FOUNDRY carries.
  - FOUNDRY's stuck rate and its context-reload cost are unmeasured.
  - BENCH conductor overhead for Relentless cannot be separated out.
- **What actually failed was operations, not the loop:** clone churn, OOM, no integrity check at boot, and restaffing known blockers. All four have cheap fixes.
- **Recommendation: promising, and better than FOUNDRY for offline items.** Make Relentless the default for the offline queue once improvements 1 to 3 land. Keep FOUNDRY for bridge and live work until Relentless can lease the bridge, and sample FOUNDRY closes with the blind checker so the remaining gap is measured rather than assumed.
