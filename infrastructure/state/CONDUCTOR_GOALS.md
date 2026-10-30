# CONDUCTOR_GOALS — the Conductor's goals for the Producer

The Producer's only input (`src/RimMandrake/rimflow/roles/producer.md`). Newest block on top; within a block, goals in
his order of priority, highest first: the Producer cuts the lowest-ranked goal's work first and never a scenario a kept
goal needs. Written by the Conductor with him (`src/RimMandrake/rimflow/roles/conductor.md` "Down"); a goal he drops is
deleted, git holds the history. His words are cited from the ledger notes on `V3_ROLES_BUILD_EIGHT_CHAIRS_ONE_TABLE`
(`python3 src/RimMandrake/rimflow/cli.py show V3_ROLES_BUILD_EIGHT_CHAIRS_ONE_TABLE`) unless another item is named.

---

## From Fri 2026-10-30: the architecture trial (block 2, on top of block 1)

Set: 2026-10-30 00:40Z. His words (note on `TESTPILOT_DESIGN_PROOF_BEFORE_RELOAD`): *"Ok. You convinced me. Execute
the 3-day comparison please. Let me know when you need help."* · *"Of course build everything you need first, if that
isn't clear"*. The rank against block 1 is the Conductor's: the trial goes first because he made it the current act.
He can reorder it.

1. **Architecture trial**: build the whole harness (day 0: all 16 `ARENA_*` items, FOUNDRY), then run the 3 measuring
   days per `design/RimMandrake/architecture_switch_harness_2026-10-29.md` §4 at the 1.5x token allowance he gave.
   Rules decided before any data, which he accepted: (a) if day 2 shows the critic is unreliable, the simplest
   critic-free arm wins; (b) if nothing separates by the day-3 hard cap, the simplest arm wins by the §4.1 tie order
   and there is no further round; (c) after that, no architecture work for about a month, and the time goes to
   FlowWorks. Headline measure: accepted work per day per owner touch. Never cut.
2. Block 1 below continues in its order, under the trial. **Paused for new starts until trial prep is done** (his words, 2026-10-30: *"Don't interrupt the work that's started, but please don't start any more game dev while we are finishing trial prep."*); work already started finishes.

## Week of Wed 2026-10-28 → Wed 2026-11-04 (block 1)

Set: 2026-10-28, the weekly sit-down (his card, 23:19Z: *"Weekly sit-down, I draft"*). Rank 1-3 is his
(23:34Z): *"v3, then FlowWorks, then GSS. The goal is to get this completely done and moved on by next week. We HAVE
to be able to do this!"* Goals 4 and 5 are the Conductor's draft, below his three, in the draft's cut order (5 is cut
first, then 4). This ranking supersedes, for this week, any older standing order that ranks differently (his 10-11
order to put FlowWorks and GSS above all else now sits under v3). How to cut: when time is short, a lower goal's
"cut first" items go before anything of a higher goal; a goal's "never cut" or "stays" items go only after every
"cut first" item of every goal is gone, lowest goal first, and only as a question to the Conductor, never alone.

1. **RimFlow v3** — the whole v3 system trialing by the end of this week; done by Wed 11-04.
2. **FlowWorks** — fix the 14 broken parts first, then prove more; week of 10-28.
3. **Gimme Some Slack** — ready for him to call finished; week of 10-28.
4. **Minerals (sparser mineral map)** — the round-two sheet judged by him; nothing ships before his review; week of 10-28.
5. **SteveDesktop** — the test machine is never idle and runs only tests that pay; week of 10-28.

### 1. RimFlow v3 runs the shop — done by Wed 11-04
- **His words** (23:34Z): *"Producer, Operations, Foundry all full working in-game with proof reliably. Plus the thing
  that tests Foundry actually works (which one is that, Auditor or Arbiter, I don't remember). All other v3 parts
  trialed and bugs fixed, not broken, but not yet fully proven out (may need more time to evaluate), but evidence
  being gathered. Ask me questions if needed to refine this further. I would prefer to be trialing the entire system
  fully be the end of the week. I think this is doable."* The thing that tests Foundry's work is the **Arbiter** (it
  rules FOUNDRY's done claims; the Auditor re-checks the Arbiter).
- **Done means:**
  - **Proved, reliably:** Producer, Operations, FOUNDRY and the Arbiter each work live, with repeated real runs as
    evidence (not one lucky run): the Producer plans from this file (daily list, Wednesday weekly plan, replan on a
    request); Operations runs its clock and alarm runs; FOUNDRY works one ticket per fresh context
    (FOUNDRY_CONTEXT_BUILD_FRESH_PER_TICKET, his *"Yes we must solve foundry context right now."* 10-28); the Arbiter
    (advisory) rules FOUNDRY's done claims with evidence.
  - **Trialed, not broken:** Conductor (quick checks and session), Auditor, Innovator and the Dispatcher each have run
    for real, the bugs those runs found are fixed, and evidence is being gathered on them (not yet fully proven).
  - **Whole system trialing** by the end of this week (his preference, above).
  - The 11-04 keep-or-kill call has its numbers: the owed instruments (OPS_KPI_MEASURE_OWED_VTHREE) land so each of
    the v3-vs-v2 primaries reads a number or a named UNMEASURED (V3_VERSUS_V2_MEASURE_PROVE_IT_PAYS, his *"We MUST
    prove that it's superior"*, 10-27).
- **Cut first if short:** nothing in "proved, reliably". Within "trialed", the Innovator's and the Auditor's trial runs
  go last; the Dispatcher's dead-window recovery proof may slip to next week.

### 2. FlowWorks — fix the 14 broken, then prove more — week of 10-28
- **His words:** card 23:36Z, *"What should FlowWorks aim for this week? → Fix the 14 broken, then prove more"*: no
  percentage promise. Standing: *"Please ensure you are prioritizing any items about gimmesomeslack or flowworks above
  all else."* (10-11); FlowWorks is force-advanced to finished before art (standing ruling 10-18).
- **Done means:** the 14 broken parts in `mod_completion.py FlowWorks` are fixed, each proved in game. A broken part
  whose fix cannot land this week is filed with its cause and stays open: the goal is not done while it is. Then more
  parts move to verified-working, unverified parts on the critical FlowWorks systems first; "more" never takes the BENCH
  lane's last free slot from goal 3; `modcheck status FlowWorks`
  shows a north-star run on the current build (GREEN, or RED with every failing row named and filed); the two red hose
  source pins resolved.
- **Lane:** BENCH (FlowWorks + GSS are BENCH's, never FOUNDRY's: his 10-23 ruling).
- **Cut first if short:** speed and zero-allocation polish that does not move a broken or verified part. Never cut:
  the 14 broken, and the re-recorded north-star run.

### 3. Gimme Some Slack — ready for him to call finished — week of 10-28
- **His words:** rank 3 (above); the 10-11 standing order above.
- **Done means:** all 31 GSS parts proved working (24 today; open: RM_RestringSpan, kineticSway, theftGoodwill,
  keepWiresOnGravship, cutWiresOnOwnerChange, dripLoops, slideUnder; the list and the bug count come from `mod_completion.py GimmeSomeSlack`); its 4 open bugs closed; `proof_all` re-run on
  the current build with 0 FAIL and every UNMEASURED row measured or named; then one short look offered to him
  (phone, single images). Whether "finished" also needs his art acceptance is his call at the look.
- **Lane:** BENCH.
- **Cut first if short:** the look moves to next week; the proof re-run stays.

### 4. Minerals — the sparser mineral map judged by him — week of 10-28
- **His words:** *"Biome minerals should be orthogonalized (made sparse, unique)..."* (10-28 22:46Z); D10 on
  MINERAL_MATRIX_DESIGN_ROUND_TWO_SPARSER (card 23:13Z): *"Should the draft go into the game before you have
  reviewed it? → Hold until you've reviewed"*. Author-time content with a lint, never worldgen (D6).
- **Done means:** the round-two matrix sheet reviewed by an agent, then put in front of him this week. **Nothing ships
  to the game until his sheet review (D10 hold)**; after it, what he keeps is built, the lint passes, and the build is
  checked by `validate_patch.py` (both --live and --defs).
- **Cut first if short:** the build waits a week; the sheet still reaches him this week.

### 5. SteveDesktop — never idle, only tests that pay — week of 10-28
- **His words:** *"Keep SteveDesktop busy. Man I'm tired of saying that."* (10-28 22:50Z); *"Let's get smarter about
  the testing we do and only use appropriate kinds of testing when/where it will help us."* (10-28 23:08Z).
- **Done means:** SteveDesktop is busy every hour it is free, running only test kinds the testing policy
  (TESTING_POLICY_DESIGN_RIGHT_TOOL_RIGHT_TIME) says catch things; no AI session can commit into the runner's pinned
  clone and pause the lane (STEVE_RUNNER_CLONE_ENFORCE_NO_LLM_WRITES); the lane's idle share over the week is measured;
  the policy's skill follow-up folded in (SKILLS_TESTING_POLICY_ABSORB_INTO_CURATION).
- **Cut first if short:** the skill fold-in, then the idle measure; the never-idle lane and the no-AI-writes guard stay.

### Not this week
- New art of any kind and new owner-facing design (pay-down rule; biome art accepted as-is, 10-18).
- The other mods' open items: queue order continues in the background, no goal.
- RimFlow work beyond goal 1 (simulation twin, Pydantic contracts, one-page brief redesign).
- Any worldgen (never).
