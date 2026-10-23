# Trickle vs batch — measured from the logs (2026-10-22)

Item: `HARNESS_BOTTLENECK_MEASURE_WHO_WAITS_ON_WHOM`. Owner, by card, 2026-10-22 21:46 PDT: *"This afternoon's log study
found that a second test PC wouldn't have helped today … 'Trickle-fed' means each feature lands small, is proven live and
pre-checked by an agent right away … What next?"* → **"Measure trickle vs batch"**. Companion to `bottleneck_measure.md`.

**Short answer.** Batch hid defects for days and spent the owner as the first real inspector: the walkthrough save he
walked at 18:41 carried hose faults **5.3 to 18.1 days old**, and his ~18-minute walk surfaced 5 problem areas that the
audit then counted as **39 hose defects of 12 kinds**. The walk's own pre-review (19 captures, "all looked at") had caught
**0** of them, because it checked framing, light and fog only. Tonight's trickle turned each owner-found defect around in a
median **54 min to built and 101 min to live-proven**, and agents, naive judges and tests caught **at least 25 defects
before the owner saw them**, against 0 in the batch. Owner time moved from defect-spotting to taste choices: 7 cards
blocked the orchestrator 36.9 min, 31 of them two art picks. **Verdict: trickle wins on defect age and on what reaches the
owner. Evidence: medium on the timings, weak on the end result,** because the owner has not yet looked at tonight's
output, so the number of escapes that matters most is still UNMEASURED.

## Method
- **Transcripts**, stream-parsed and never read whole, from the orchestrator `5453bc27-….jsonl` and its `subagents/`
  (all under `/home/mandrake/.claude/projects/-home-mandrake-rm-bench/5453bc27-3eb8-4e2e-b5ef-b3cc25266b27/`).
  Measured: owner messages, card asked → answered (orchestrator blocked time), helper spawn and last-record times,
  helper briefs and final reports.
- **Ledger** `infrastructure/state/ledger/events/{BENCH,FOUNDRY,OWNER}.jsonl`: per item `file` → `start` →
  `implemented` → `verify`/`close`. `ts` is UTC and converted to PDT.
- **Git**: the commits that introduced each fault, as named by the audit (`Transient/pile_2026-10-22/hose_audit.md` §4)
  and the fix reports, with author dates.
- **Owner screenshots**: Steam captures `20261022184157` … `20261022184658` (six, 18:41:57–18:46:58).
- **Scripts** (scratch, not committed), next to the earlier ones:
  `/home/mandrake/.seat-tmp/BENCH/claude-1000/-home-mandrake-rm-bench/5453bc27-3eb8-4e2e-b5ef-b3cc25266b27/scratchpad/{tvb_agents,tvb_owner,tvb_orch,tvb_last}.py`.
- **Definitions.** *Found* = the first time any finder named the defect (an owner message, or an agent's ledger `file`
  or report). *Built* = ledger `implemented` or install commit. *Live-proven* = ledger `verify`, or a live look that
  passed. *Owner minutes* = orchestrator time blocked inside a card, an UPPER bound: it includes his reading time and
  any time he was away. The time he spent typing messages is UNMEASURED.
- **Sanity probes.** The screenshot folder holds 6 captures today, matching the "(screenshot)" ×5 in his 18:48 message
  plus one. The ledger shows 4 `verify` events at 20:29 for the 4 hose items, matching the 20:30 report. The audit's 39
  is the audit's own tally (CODE 13 + ART 15 + SITE 11), re-added here: 13+15+11 = 39.

## 1. BATCH — walkthrough save b, shown ~18:40

**How it was built.** Save `RM_fw_walkthrough_20261022b` came from a 167-min live helper (15:17–18:04). That helper
deployed 7 fixer DLLs that had landed over the day, re-saving after each, and then previewed the walk: "All 11 stops
walked, 19 captures … all looked at. Each lands on its subject, lit, nothing dead or fogged." The game was handed over at
18:04:57.

**The owner's look.** He was in chat about compaction until 18:30:36. His screenshots run 18:41:57–18:46:58, and his
verdict landed at 18:48:30: *"you obviously didn't check any graphics for connectors … Obviously not even checked before
showing us."*

| what he named (18:48) | audit finding (19:08) | introduced by | age when he saw it |
|---|---|---|---|
| hose through the wall | D1, wall-seam hole in `HoseMath.Clear` | `9e9f153d4e` 2026-10-04 16:55 (GSS round 4) | **18.1 days** |
| hose under the battery | D2, walk-over buildings priced as bare ground | older than `86e8a90bfe` (10-20); the loops that expose it, see D10 | ≥2 days (lower bound) |
| connectors / collars "everywhere" | D3, D5–D9: 15 of 15 laid reels with collars short of the nozzle, plus stubs in mid-air | coupling art `2e22f30e3c` 2026-10-17 11:12; made twice as visible by `f256450686` 10-22 00:17 | **5.3 days** (18.4 h at double visibility) |
| reels lower left, U-turns | D10 ×10 | straight lead-out `0476fadd29` 10-05 + `b59ebcfec1` 10-06; reels staged facing west by `0ab8470911` 10-22 09:10 | 16.8 days (loops); 9.5 h (the staging that kept them) |
| ladder "much more vertical" | — (art) | UNMEASURED | UNMEASURED |
| Vicky's dark square on the pit lid | — (render code) | UNMEASURED | UNMEASURED |
| "modern" tank and reel = primary-colour paint | — (art brief) | UNMEASURED | UNMEASURED |
| (not in his shots) | D4, D5, D7, D8, D11, D12: 6 more kinds the audit found | | |

- **Owner found:** 5 problem areas (hose joints, hose routing, ladder, pit lid, modern art). On hoses alone that came
  to **12 kinds and 39 instances** (CODE 13, ART/offset 15, SITE 11). His screenshots directly show 6 of the 12 kinds; the
  audit found the other 6.
- **Caught by the batch's own pre-review:** **0.** The preview's criteria were framing, light, fog and dead pawns. No
  close-up of any joint was taken.
- **Owner minutes:** **6.5–17.9 min** of walking, from his first screenshot (lower bound) or his last chat turn (upper
  bound) to his 18:48 message. He stopped early: *"That's it for now, I'm done with this walkthrough map."*
- **Fault age at detection** (the four dated faults): median **~11 days**, range 0.4–18.1 days. Those faults sat in
  shipped code through every proof belt in between, because no proof row looked at a joint (the GSS joint test measured
  an art file that was never drawn; see the 19:44 connector report).

## 2. TRICKLE — 18:50 to ~22:00

**Shape of the evening.** 29 helpers spawned between 18:49 and 21:56: 1 audit, 5 live, 9 naive judges or judges, and the
rest fixers, art and harness. Over the 187 minutes, mean concurrency was **2.6** (max 7), and no minute ran without a
helper. Some live helper held the game **104 of 187 min (56%)**. The game was not the bottleneck tonight; the art and
judge loops and the dispatch queue were.

### 2a. Owner-found defects (found at 18:48:30)
| defect | helpers | built | live-proven | found → built | found → live | owner cards |
|---|---|---|---|---|---|---|
| hose through walls / under the battery (D1, D2) | audit + walls fixer + live prover | 19:41:01 `849b1674ea` | 20:29:26 HW1 PASS, maps C and R and save c | **53 min** | **101 min** | 1 (19:11, 1.9 min) |
| connectors / collars (D3, D5–D9) | audit + connector fixer (+ joint gate) + live prover | 19:42:59 `34559c60d9` | 20:29:23 joint_check PASS; all 8 audit defects re-captured | **54 min** | **101 min** | shared with the row above |
| reels facing west, U-turns (D10) | connector fixer + prover | 19:43:00 | 20:29:29 | **55 min** | **101 min** | — |
| pit lid (Vicky) | 1 fixer + 1 live check | 19:03:11 `1a7072d6b6` | 19:27:54 (by eye, save b) | **15 min** | **39 min** | 0 |
| portable ladder | 4 drawers, 8 redraws, 1 judge, 6 naive looks, 1 GPT experiment | 19:41:01 `41c06f6a2b` | 21:27:39 live art look | **53 min** | **159 min** | 3 (19:08 1.1, 19:15 1.7, 19:38 0.8) |
| modern tank and reel art | 1 artist + 2 naive judges + live look | tanks 19:49 `fb34c9bc2d`; fire reel 20:14 `cfcdb0cbaf`; joint fix 20:37 `5bed576967` | 21:28:46 live look: passes as art, but **found coupler gaps**; fixed 21:49, live look owed | **61–86 min** | **160 min** to the first live look; final proof owed | 2 (19:35 **14.3**, 20:06 **16.5**) |

- **Medians:** found → built **53.5 min**; found → live-proven **101 min** (6 rows).
- **Batch comparison:** those same faults went 5.3–18.1 days from introduction to detection.

### 2b. Agent-found defects tonight (nothing for the owner to find)
| defect | finder | found | built | found → built | dispatch wait |
|---|---|---|---|---|---|
| tank flange drawn mid-pipe | live check after joint fittings switched on | 19:28:11 | 21:39:56 | 132 min | **114 min** (dispatched 21:21:57) |
| D4 tank stub to nowhere | audit | 19:41:34 (filed) | 21:40:24 | 119 min | 100 min |
| fire reel joint 255/256 | test (C# joints row) | 20:28:20 | 20:37:24 | 9 min | 0 |
| joint_check `--all-maps` saw only one map | live prover (HARNESS) | 20:28:23 | 20:29:21 | 1 min | 0 |
| map R builder refused 40 banks | live prover | 20:28:21 | 21:08:10 (map built live) | 40 min | 2 min |
| C1 cord into the river, C1 tank stub, creek fords along a puddle, proof sweep ate the zoo, mock overwrites the key sheet | map R helper | 21:07:34–41 | 21:32:58–21:48:01 | 25–41 min | 15 min |
| 3 modern tanks with couplers off the wall, oversized reel shadow | live art look | 21:27:19–22 | 21:49:48/51 | 22 min | 0 |
| hose laid to a tank ends on its lid | joint check (live) | 21:27:19 | 21:56:05 | 29 min | 14 min |
| ford stones read as a smudge | creek fixer | 21:39:35 | 21:56:07 | 17 min | 2 min |

- **Median found → built:** ~29 min.
- **The one long wait was dispatch:** two items sat 100–114 min until the 21:21 batch dispatch. That is the afternoon's
  "waiting on a fixer" pattern again, at a smaller scale.

### 2c. Owner minutes tonight
- **7 cards** on trickle work (19:02–20:06), blocking the orchestrator **36.9 min** in total. Two art-pick cards took
  30.8 of those minutes: the modern set (14.3) and the fire reel (16.5). The other five took 0.6–1.9 min each.
- **5 typed messages:** the 18:58 pre-review rule, 3 short questions, and the 19:12 GSS hint.
- Helpers kept running during every card (notifications arrived mid-card), unlike the afternoon's 321-min freeze.
- **Of the owner's time:** none went to finding a mechanical defect tonight. All of it went to direction (ladder, hoses
  under or over) and taste (art picks).

## 3. Caught before the owner vs reached the owner

| caught before he saw it (tonight) | by |
|---|---|
| ladder options B and C (single stick; painted shadow floats), A too thin | judge 18:55 |
| ladder A3–A8: west wall reads as lying flat, backwards perspective, pale stripe at play zoom (6 rounds) | 6 naive looks, 19:04–19:37 |
| tank comparison sheets showed only the old red tank (×4) | orchestrator's own look 19:16 |
| reel B looks like a generator, reel C is a recolour; no short tank passed | naive judge 19:16–19:17 |
| fire reel FA: 4 side mismatches (drum colour, pedestal, drum shape, footprint) | naive judge 19:49 |
| white short tank had no end fittings | hose-port test, before 20:14 |
| fire reel joint 255/256 | joints test 20:28 |
| tank flange mid-pipe; D4 stub | live check 19:28; audit |
| 3 tanks with floating couplers; reel shadow | live art look 21:27 |
| map R builder, C1 cord, C1 stub, creek fords, ford stones, hose on the lid, zoo sweep, mock key sheet | live and map helpers 20:28–21:39 |

**At least 25 defects** were caught before the owner, counting the 4 tank sheets as one and each judge round as one.
The count is a floor: helpers fixed some faults inside their own runs without filing them.

**What still reached him tonight:**
- **One taste miss.** The judge's best reel (A, resin cart) went to card; he rejected all three (*"Try looking up firehose
  reel"*), at a cost of one 14.3-min card plus a 16.5-min re-pick. Naive-judge agreement with the owner on taste: 3 of 4
  modern picks matched his "(Recommended)" choice, and 0 of 1 reel sets did.
- **Three ladder cards** carried a disclosed, unresolved flaw: the west wall read as propped only 30–55% of the time.
  That was a direction question, not an escaped defect.
- **Unflagged mechanical defects shown to him tonight: 0.** But he has not walked or looked at tonight's build in game
  (no owner screenshot after 18:46:58), so **the escape rate of trickle is UNMEASURED**.

## 4. Verdict

| measure | batch (save b) | trickle (tonight) |
|---|---|---|
| fault age when first found | 5.3–18.1 days (median ~11 d, 4 dated faults) | minutes: found at landing by a test, judge or live look |
| defects found first by the owner | 5 areas → 12 kinds / 39 instances on hoses | 0 mechanical; 1 taste rejection |
| defects caught by agent pre-review | 0 (wrong criteria) | ≥25 |
| found → built / → live-proven | n/a (they sat unseen) | median 53.5 / 101 min (owner-found); ~29 min built (agent-found) |
| owner minutes | 6.5–17.9 walking, all spent finding faults | ≤36.9 card-blocked, spent on direction and taste |
| helpers | 1 live helper, 167 min | 29 spawned, mean 2.6 running, game busy 56% |

**Plain verdict.** For defects, trickle with mandatory pre-review beats batch: faults are found within minutes of landing
instead of after days, and the owner stops being the first inspector. It costs helpers (29 tonight, 9 of them judges)
and some owner taste time, which is the trade he asked for. Two caveats limit the evidence:
1. **The proof that counts is missing.** He has not looked at the trickle output, so escapes per owner look are
   unknown.
2. **Tonight was confounded.** It was a repair sprint on defects he had just named, not new features landing small. The
   new pre-review rule (18:58, `4845fc61fe`) and the restored joint gate arrived at the same time, so "trickle" and
   "pre-review" are not separated.

**Evidence strength:** **strong** for batch fault ages (git dates) and the batch pre-review catching 0 (helper report);
**medium** for trickle timings (ledger, one evening, n = 6 owner-found rows); **weak** for the overall claim until the
owner's next look is counted.

**The residual bottleneck is still dispatch.** Two agent-found items waited 100–114 min for a fixer while no live helper
held the game for 44% of the evening. Auto-dispatch on `file` (the afternoon's recommendation) would have cut the tank flange from
132 to ~20 min.

## 5. What to measure tomorrow (the no-blocking day)
This extends the item's NEXT: *"on 2026-10-23 run a no-blocking day (auto-dispatch helpers, delegated calls, cards only
for the short list), then rerun the bottleneck measurement and compare with bottleneck_measure.md"*.

1. **Escapes per owner look, the deciding number.** At every owner look (walk, screenshot, card), count each defect he
   names that no agent, judge or test had flagged first. File each with `--why "escape: owner-found"`. Confirms trickle
   if escapes are ≤1 kind per look, against today's 5 areas / 12 hose kinds.
2. **Finder on every `file` event:** `--why "found-by: owner|prereview|judge|test|live"`. Today this had to be
   reconstructed from prose.
3. **Defect age:** for each MOD/ART finding, the introducing sha (from the fix report), and its age at detection.
   Target: median under 1 day.
4. **Dispatch wait** (`file` → `start`) and **found → live-proven** per item, from the ledger. Targets: dispatch median
   under 10 min, and found → live-proven median ≤ 2 h (today 101 min for owner-found).
5. **Owner minutes split** into taste, direction and defect-finding, from card blocked time plus typed turns. Trickle
   should push defect-finding toward 0.
6. **Judge-vs-owner agreement on taste picks.** Today 3/4 on tanks and 0/1 on reels. If it stays under ~75%, show him
   two options instead of one recommendation.
7. **Bridge busy share and helper concurrency** (`tvb_agents.py` and `share.py`). If the game stays below ~60% busy, a
   second test PC is still not the answer.
8. **Land features small:** at most one feature per DLL deploy and a live look within the hour. Log the land → first
   live look gap, so trickle is measured as trickle and not as a repair sprint.
