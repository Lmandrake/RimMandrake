# DIG_FINDS_PROVE_NEVER_FINISHES_ON_STEVE

Split from FLOWWORKS_QUARRY_DIGGING_1 (superseded) by owner direction 2026-10-31 ("perhaps the digging finds, sluice mining, and gold panning can be broken down into smaller tickets that can be independently checked and debugged"). Owner 2026-10-31 then asked that each card be fully equipped with the parent's context. This is the FlowWorks half (canal-dig finds). It absorbs the tracking item QUARRY_DIG_FIX_VALIDATED_BUT_NEVER_FINISHES. Sibling tickets: SLUICE_BOX_PROVE_THE_DAILY_WASH, GOLD_PANNING_PROVE_THE_COLONIST_STAYS, PLACER_STOCK_PROVE_FLOOD_REFILL (river half; they do not share a failure with this one).

## why

What the feature is for the player. Owner request 2026-10-03: "digging a canal can discover materials like the quarry does, only from the local biome's availability by default (configuration-changeable)". Ruled by question card 2026-10-03: finds drop as a lump on the bank with a message, a letter on the first find of each material per map; deep and superdeep cuts can reach deep-drill minerals; in a mineral-less biome, digging yields chunks of local rock (consistent with quarries). Design: design/RimMandrake/flowworks_quarry_sluice_panning_design_2026-10-03.md section 2a.

Defaults (RimMandrakeFlowWorksMod.cs 485-489 settings digFinds*, 491-493 digRock*): 1.5% chance per cut (RM_DigDiscoveryMath.BaseChance 0.015), lump 10-25 units (LumpMin/LumpMax), per-map budget as a percent of the map's ore units, rolledDepth guard against re-cutting one cell, letter on first find per material per map. All PROVISIONAL. Pool is the MAP'S OWN ROCK until MINERALS_WHERE_THEY_BELONG_1's registry (QuarryDraw) exists.

## spec

### Current state (what is built)
Built by FOUNDRY c858125a8 (2026-10-06: five settings, rolledDepth guard, budget, letter, local-rock chunk fallback). Read from the code on 2026-10-31:
- Hook: JobDriver_DigCanal.cs line 134 calls the discovery OnCut after Deepen; RM_DigDiscovery.cs OnCut at 90; chance and lump numbers in RM_DigDiscoveryMath.cs.
- Cut price: RM_DigDepthMath.cs WorkPerNotch 3200 (line 44), DefaultLabourMultiplier 4 (line 56); setting digLabourMultiplier at RimMandrakeFlowWorksMod.cs 506 (settings UI 1049).
- Proof hook: RM_DigDiscoveryProof (ProofReport "force" arms a certain roll; ProofReport " " reads the report). Chain constant DIG_PROOF at northstar/extensions.py:2570.
- Chain: `dig_finds` at northstar/extensions.py:3331 with components finds_off_none, cut_turns_up_local_find, first_find_sends_letter; helpers _dig_by_hand 3302 (loop `range(16)` x `wait_ticks(500)` = 8,000 ticks, lines 3309-3310), _finds 3316, _expect_cut_found 3321; the failure text "the dig job never finished" is raised at 3325 and about 3357. The chain cuts ONE cell three times (notch 1, 2, 3). It does not set digLabourMultiplier.
- Standalone check: northstar/quarry_find_live.py (A5). Waits `while t < 4000: step(250)` (lines 108-109); row QUARRY_FIND_DROPS_ON_LIP; UNMEASURED text "no colonist cut the square in 4000 ticks" at line 122.

### Not built
Nothing in this half is unbuilt except what the registry swap (above) will change. first_find_sends_letter has never been read: a rock chunk sends no letter by design, so the row needs a forced non-chunk find through RM_DigDiscoveryProof.

### Leading hypothesis (DERIVED from code arithmetic, UNMEASURED on Steve)
Commit ac3aab2458 (2026-10-25) made the shipped digLabourMultiplier x4. Cut work then is notch 1 = 12,800, notch 2 = 25,600, notch 3 = 38,400 work units, which at MiningSpeed 1 is about 7,529 / 15,059 / 22,588 ticks. dig_finds reuses one cell for three cuts inside an 8,000-tick helper window, and quarry_find_live waits 4,000 ticks. Passes (2026-10-15, 10-22) predate the multiplier; failures start 2026-10-26, the day after. Same class of bug as lesson infrastructure/state/lessons/20261029T223804Z-FOUNDRY-dig-driver-labour-multiplier.md (droid_dig_live fixed with LABOUR = 0.25 and WAIT_TICKS = 15000; the lesson's commit hash 13ba79077b does not resolve in this clone) and commit c8a55ab0ed (fill-in). Mining skill 10 and MiningSpeed are not measured on Steve; do not treat the tick figures as measured until a run records them.

## verify

### Acceptance
Chain: `modcheck FlowWorks dig_finds` through the testq lane steve-targeted on SteveDesktop (dry site; the river map spoiled two runs, see history). Each row must PASS:
1. finds_off_none: with digFindsEnabled OFF three forced cuts finish and the finds counter is unchanged.
2. cut_turns_up_local_find: with digFindLetterEnabled OFF a forced cut finishes, the finds counter rises, the find is a local mineable or a chunk (never ComponentIndustrial / ComponentSpacer / Plasteel), and no letter arrives.
3. first_find_sends_letter: with the letter ON a forced non-chunk find sends a "Found while digging" letter. UNMEASURED so far (never read).
Standalone: quarry_find_live.py row QUARRY_FIND_DROPS_ON_LIP (A5), last PASS 2026-10-22 (evidence northstar/quarry_find_result_20261022T1340_belt.json, ledger sha ee9fa61fbc).

### Last tested code version and whether a run is owed (test once per code version)
Last Steve run: fail, FlowWorks sha 1d1d7396e8 (2026-10-31T05:20Z, J20261031T051153Z-d365b4.a1). `git log 1d1d7396e8..HEAD -- src/RimMandrake/FlowWorks` is empty (0 commits), so NO run is owed until a fix lands. Running the chain again at the same code is the waste that rule forbids. Passing history: A5 2026-10-22 (ee9fa61fbc, does not resolve here), dry-site dig_finds R4 2026-10-15 at ce40347df6 (finds_off_none PASS, cut_turns_up_local_find PASS, ChunkSlate at 87,89 D3).

### History (nothing here is a guess unless marked)
Parent ledger events, all read 2026-10-31: 109 verify (3 pass, 77 partial, 29 fail), 58 finding, 19 note.
- Passes: A1 and A2 on 2026-10-15 at 695812d5ec (river half, belong to the sibling tickets); A5 on 2026-10-22 at ee9fa61fbc (this ticket).
- 2026-10-15 R3: A5 dig_finds UNMEASURED twice on the river map (ToxicBuildup disturbance, item TESTENV_TOXIC_DIAGNOSE_RIVER_SITE_SNIFFLES); rerun on a dry site.
- 2026-10-15 R4 (ce40347df6): dry-site dig_finds finds_off_none PASS, cut_turns_up_local_find PASS (ChunkSlate @87,89 D3); first_find_sends_letter UNMEASURED by design (chunk sends no letter). Next was to force a non-chunk find with RM_DigDiscoveryProof; not done.
- 2026-10-26 to 2026-10-31 steve-targeted (RUNNER): 29 verify fail and 77 verify partial, all config steve-targeted, FlowWorks shas 70801f8f0e ... 1d1d7396e8. All 29 fails read "ExpectationFailed: the dig job never finished"; fails by day: 10-26 3, 10-27 13, 10-28 7, 10-29 4, 10-31 2 (10-30 none) = 29. What the 77 partials are (which row is not PASS) is UNMEASURED; the verify events carry only the modcheck sheet path, not the row.
- Findings fold 2026-10-29 (RUNNER): reopen by FLOWWORKS_FINDS_OFF_NONE_FAILS_8C513E (count 4, first 2026-10-27T21:37Z, last 2026-10-29T07:55Z); CONTRADICTION on the parent "validated" while the row still fails (count 23, first 2026-10-26T02:19Z, last 2026-10-29T10:52Z, 0 passes since). The fold's first-seen 02:19Z is earlier than any fail verify in the ledger (20:50Z); that discrepancy is UNMEASURED.
- 2026-10-29 findings curation design (design/RimMandrake/findings_curation_design_2026-10-29.md): pool of 127 findings, 50 distinct failures; the parent was "validated while failing 26 runs".
- INVALID / HARNESS runs, NOT feature failures, no verdict recorded: J20261027T022443Z-6675e4.a1 (modcheck exit 5, UNKNOWN-outcome marker), J20261027T024615Z-c14359.a1 (companion_handshake: earlier mutating call with UNKNOWN outcome), J20261029T133503Z-75c803.a1 (REFUSED/SYNC, runner pull failed on diverging branches; lane paused, finding STEVE_LANE_SYNC_REFUSED_75C803), J20261030T081048Z-5f50de.a1 and J20261030T081436Z-77e9fd.a1 (bridge programState error). Do not count these.
- False or unproven theories: (a) "the feature is broken": the same chain passed on a dry site 2026-10-15 and standalone A5 passed 2026-10-22; (b) "the river map is the cause": it spoiled R3 only, the failures are on the dry-site chain; (c) the A5 UNMEASURED text in quarry_find_live.py reads like the same bug, never confirmed. The labour-multiplier theory above is the only one with arithmetic behind it and is itself unmeasured.
- What was tried: nothing yet that changes the chain or its window. 29 identical re-runs queued; none gave a different result. Do not queue another at this code version.

### Findings sorted to this ticket
All 58 findings of the parent belong here: 29 distinct findings, each written twice (UNTRIAGED by RUNNER on its run date, retyped TRACKED by BENCH 2026-10-31T16:03 to 16:07 with "triage: tracked in QUARRY_DIG_FIX_VALIDATED_BUT_NEVER_FINISHES"). 24 are FLOWWORKS_CUT_TURNS_UP_LOCAL_FIND_FAILS_*, 5 are FLOWWORKS_FINDS_OFF_NONE_FAILS_*. 58 = 29 x 2. None belongs to SLUICE, PANNING or PLACER_STOCK; they are listed only here. (A 30th, FLOWWORKS_CUT_TURNS_UP_LOCAL_FIND_FAILS_6E5292 from KNOWN_GOOD_AUDIT_MEASURE_SWEEP_MISSES run-1, sits on QUARRY_DIG_FIX_VALIDATED_BUT_NEVER_FINISHES, not on the parent.)

| finding | component | first written (UTC) | run |
|---|---|---|---|
| FLOWWORKS_CUT_TURNS_UP_LOCAL_FIND_FAILS_B308B8 | cut_turns_up_local_find | 2026-10-26 20:50Z | run-2 |
| FLOWWORKS_CUT_TURNS_UP_LOCAL_FIND_FAILS_891D79 | cut_turns_up_local_find | 2026-10-26 21:50Z | run-4 |
| FLOWWORKS_CUT_TURNS_UP_LOCAL_FIND_FAILS_B8A647 | cut_turns_up_local_find | 2026-10-26 23:24Z | run-5 |
| FLOWWORKS_CUT_TURNS_UP_LOCAL_FIND_FAILS_F29476 | cut_turns_up_local_find | 2026-10-27 00:27Z | run-6 |
| FLOWWORKS_CUT_TURNS_UP_LOCAL_FIND_FAILS_12E15D | cut_turns_up_local_find | 2026-10-27 00:55Z | run-7 |
| FLOWWORKS_CUT_TURNS_UP_LOCAL_FIND_FAILS_F6E2C1 | cut_turns_up_local_find | 2026-10-27 02:07Z | run-8 |
| FLOWWORKS_CUT_TURNS_UP_LOCAL_FIND_FAILS_6384A1 | cut_turns_up_local_find | 2026-10-27 04:06Z | run-9 |
| FLOWWORKS_CUT_TURNS_UP_LOCAL_FIND_FAILS_D77D50 | cut_turns_up_local_find | 2026-10-27 04:41Z | run-10 |
| FLOWWORKS_CUT_TURNS_UP_LOCAL_FIND_FAILS_F0F999 | cut_turns_up_local_find | 2026-10-27 06:28Z | run-11 |
| FLOWWORKS_CUT_TURNS_UP_LOCAL_FIND_FAILS_A89C6D | cut_turns_up_local_find | 2026-10-27 07:36Z | run-12 |
| FLOWWORKS_CUT_TURNS_UP_LOCAL_FIND_FAILS_B0E7AE | cut_turns_up_local_find | 2026-10-27 08:19Z | run-13 |
| FLOWWORKS_CUT_TURNS_UP_LOCAL_FIND_FAILS_9A73AC | cut_turns_up_local_find | 2026-10-27 14:30Z | run-20 |
| FLOWWORKS_CUT_TURNS_UP_LOCAL_FIND_FAILS_1C556A | cut_turns_up_local_find | 2026-10-27 18:21Z | run-29 |
| FLOWWORKS_CUT_TURNS_UP_LOCAL_FIND_FAILS_D7324F | cut_turns_up_local_find | 2026-10-27 19:52Z | run-33 |
| FLOWWORKS_FINDS_OFF_NONE_FAILS_5BDB28 | finds_off_none | 2026-10-27 21:37Z | run-36 |
| FLOWWORKS_CUT_TURNS_UP_LOCAL_FIND_FAILS_954B7D | cut_turns_up_local_find | 2026-10-27 22:24Z | run-38 |
| FLOWWORKS_FINDS_OFF_NONE_FAILS_BD04B0 | finds_off_none | 2026-10-28 03:04Z | run-41 |
| FLOWWORKS_FINDS_OFF_NONE_FAILS_1AA5AF | finds_off_none | 2026-10-28 04:20Z | run-46 |
| FLOWWORKS_CUT_TURNS_UP_LOCAL_FIND_FAILS_216E2C | cut_turns_up_local_find | 2026-10-28 06:08Z | run-53 |
| FLOWWORKS_CUT_TURNS_UP_LOCAL_FIND_FAILS_5158A5 | cut_turns_up_local_find | 2026-10-28 07:01Z | run-55 |
| FLOWWORKS_CUT_TURNS_UP_LOCAL_FIND_FAILS_100A6C | cut_turns_up_local_find | 2026-10-28 11:41Z | run-59 |
| FLOWWORKS_CUT_TURNS_UP_LOCAL_FIND_FAILS_B0D6C8 | cut_turns_up_local_find | 2026-10-28 20:05Z | run-62 |
| FLOWWORKS_CUT_TURNS_UP_LOCAL_FIND_FAILS_FB772E | cut_turns_up_local_find | 2026-10-28 22:26Z | run-63 |
| FLOWWORKS_CUT_TURNS_UP_LOCAL_FIND_FAILS_9622DB | cut_turns_up_local_find | 2026-10-29 00:15Z | run-64 |
| FLOWWORKS_FINDS_OFF_NONE_FAILS_8C513E | finds_off_none | 2026-10-29 07:55Z | run-65 |
| FLOWWORKS_CUT_TURNS_UP_LOCAL_FIND_FAILS_17A1F5 | cut_turns_up_local_find | 2026-10-29 10:52Z | run-66 |
| FLOWWORKS_CUT_TURNS_UP_LOCAL_FIND_FAILS_EB209A | cut_turns_up_local_find | 2026-10-29 22:32Z | run-74 |
| FLOWWORKS_CUT_TURNS_UP_LOCAL_FIND_FAILS_F1DFC1 | cut_turns_up_local_find | 2026-10-31 01:43Z | run-102 |
| FLOWWORKS_FINDS_OFF_NONE_FAILS_D365B4 | finds_off_none | 2026-10-31 05:20Z | run-106 |

### Dependencies and do-not-touch
- Independent of the three river tickets: different chain (dig_finds vs placer) and code (JobDriver_DigCanal / RM_DigDiscovery vs RM_PlacerWorks).
- Do not touch shipped digLabourMultiplier (default x4, ac3aab2458). Fix the harness, not the price.
- Do not edit droid_dig_live.py (its LABOUR / WAIT_TICKS fix is the pattern, not the target).
- Do not queue further Steve runs at 1d1d7396e8. Do not call the hypothesis the cause until a run shows the cut finishing.

### NEXT action (one)
Make `dig_finds` (northstar/extensions.py:3331, helper _dig_by_hand 3302) and quarry_find_live.py hold digLabourMultiplier at 0.25 for the run (as droid_dig_live.py does, LABOUR = 0.25) and size their waits from the cut price (WAIT_TICKS = 15000 per cut as in droid_dig_live.py), restoring the setting afterwards; then run the dig_finds chain ONCE on SteveDesktop at the new code version and record the ticks the cut actually took. If it still never finishes, read the job state through the bridge before touching anything else.
