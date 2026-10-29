# The best simple Ralph loop for RimMandrake (2026-10-29)

Item `RALPH_LOOP_DESIGN_ONE_PROMPT_FOREVER`. Status: DRAFT, waiting for GPT's check. Nothing here is live: no
timer, role file, seat or config was changed to write it.

The owner asked (2026-10-29, verbatim): "I am also quite fascinated by studying the difference between this elborte
system and the much simpler implementation following the Ralph loop idea. Please do a deep design pass feeding the
whole spec for our goals and needs and past solutions and ask the question "what's the best simple Ralph loop to get
this done?" A variation might be to have a second Ralph loop running in Steve desktop. I'm interested to see what it
looks like. Then make a simulation to compare it to v2 and v3 estimates. Then have got check it."

**Answer in one paragraph.** The best simple Ralph loop is a 40-line shell loop on Archmagi. Each pass starts a
fresh `claude -p` on a 100-word prompt that picks one item from `IMPLEMENTATION_PLAN.md`. Programs it already has
push back on bad work: selftests, `validate_patch.py`, `winbuild.py`, `modcheck`, and the bridge lock with
`--idle-ok`. Owner-only acts go to an inbox file and are never done by the loop. It stops on a STOP file, a red tree
or a low token runway. On the same calibrated world as the v2 and v3 estimates, it closes about **a third as much
sound product work as v2** (median 17.5 against 49 per day; 0% of the 240 members do better). It spends about **a
third of the tokens** (0.64G against 1.9G a week). Sound work per token comes out about the same as v2 (52-53% of
members do better). It runs with **no blocked hours** and its backlog keeps growing. Two builder loops (variant
AB_build) close about two thirds as much as v2. Whether the owner sends fewer messages depends on one assumption:
how often he asks "what is it doing?". The model cannot settle that. Ralph gives up most of what v3 was built to
add: independent judging, getting defects fixed, alarm routing, and planning beyond one list. It also needs none
of the machinery whose failures took up most of v3's first week.

## 0. Sources

Fetched 2026-10-29. Copies are in `D:\ClaudeWork\rimmandrake\ralph_sim\web\`.

- Geoffrey Huntley, "Ralph Wiggum as a software engineer", https://ghuntley.com/ralph/ (14 Jul 2025). It gives the
  loop as `while :; do cat PROMPT.md | claude-code ; done` and says "One item per loop" twice. Its other rules:
  specs in `specs/*`, a `fix_plan.md` list, and `AGENT.md` for how to build and test. Many subagents may search,
  but only one runs build and test, and that one is the backpressure. It names "placeholder and minimal
  implementations" and duplicate implementations as the failure modes. The human "sits on the loop" and tunes the
  prompt when it goes off the rails.
- Geoffrey Huntley, "loop", https://ghuntley.com/loop/ (17 Jan 2026). Ralph is deliberately monolithic: one process,
  one repo, one task per loop.
- repomirror report, https://raw.githubusercontent.com/repomirrorhq/repomirror/main/repomirror.md. Overnight Ralph
  loops cost "a little less than $800" in inference and made about 1,100 commits. A prompt "improved" to 1,500
  words made the agent "slower and dumber"; going back to 103 words fixed it.
- Clayton Farr, ralph-playbook, https://github.com/ClaytonFarr/ralph-playbook (mirrored by
  https://github.com/ghuntley/how-to-ralph-wiggum). It splits the loop into PLANNING and BUILDING modes over
  `IMPLEMENTATION_PLAN.md` and `AGENTS.md`. Its `loop.sh` has a max-iterations argument and runs `git push` after
  every iteration. Its backpressure is acceptance-driven: "tests, typechecks, lints, builds" reject bad work.
- Anthropic, ralph-loop plugin, https://github.com/anthropics/claude-plugins-official/tree/main/plugins/ralph-loop.
  It runs the loop inside one session: a Stop hook feeds the same prompt back, and the options are
  `--max-iterations` and `--completion-promise`. Its README says it is not good for tasks that need human judgment
  or design decisions.
- From memory, not re-fetched: Huntley also described running Ralph for months to build the CURSED language, and a
  "Ralph-on-Ralph" pattern of several loops on one repo. I use neither as evidence here.

Our side: `rimflow_v3_minimal_opus_2026-10-29.md` (the F1-F32 function inventory),
`rimflow_v3_collapse_compare_2026-10-29.md`, `process_model_explainer_2026-10-29.md` (the calibrated v2/v3 model
and why its backtest failed), `rimflow_v3_sim_findings_2026-10-27.md`, and `operating_modes_2026-10-26.md`.

## 1. Ralph A: one loop on Archmagi

### 1.1 What it has to get done

The goals behind v2 and v3, written as plainly as possible:

- Build and fix the mods.
- Keep the live game safe: one bridge holder at a time, never while the owner plays, never a flyer flight.
- Never show the owner unread material.
- Never do an owner-only act on its own: deleting art he kept, ruling on scope, spending money, granting the game.
- Use the token quota well and do not run out mid-week.
- Leave a record a later reader can trust: real shas, criteria met or not.

Ralph's design question is the smallest loop that meets these without a Dispatcher, roles, helpers or an
orchestrating seat.

### 1.2 The loop script (`ralph/loop.sh`, proposed, not written to the repo)

```bash
#!/usr/bin/env bash
# One fresh claude -p per iteration, one plan item per iteration. Stops itself; never needs a nudge.
set -uo pipefail
cd /home/mandrake/rm/ralph            # its own clone; never the BENCH or FOUNDRY clone
MAX=${MAX:-200}; i=0
LOG=/mnt/d/ClaudeWork/rimmandrake/ralph/log; mkdir -p "$LOG"
while [ $i -lt "$MAX" ]; do
  [ -e ralph/STOP ] && { echo "STOP file"; break; }                # owner's off switch (and the PAUSE file)
  python3 src/RimMandrake/Utils/ops_watch.py --runway-ok 0.15 || { echo "token runway low"; break; }
  git pull --rebase -q || { echo "pull failed"; break; }
  python3 src/RimMandrake/Utils/run_selftests.py --quick >"$LOG/pre.$i" 2>&1 \
    || { echo "tree red before iteration $i"; touch ralph/STOP; break; }   # never build on red
  timeout 90m claude -p "$(cat ralph/PROMPT.md)" --output-format json >"$LOG/it.$i.jsonl" 2>&1
  ./publish || echo "publish failed at $i" >>ralph/owner_inbox.md
  i=$((i+1))
done
```

The script reads the account, host and keys from the environment, as the project rule requires; none are named
here. `ops_watch.py --runway-ok` and `run_selftests.py --quick` are proposed flags that do not exist yet. Each
needs a few lines added.

The loop stops on six things, all mechanical:

1. The STOP file, written by the owner or by the loop itself.
2. `MAX` iterations.
3. A token runway under 15%.
4. A red tree before an iteration.
5. A failed pull.
6. The 90-minute timeout on a single iteration (the iteration fails, the next one starts).

It never waits to be told to keep going.

### 1.3 `ralph/PROMPT.md` (103 words; short on purpose, per the repomirror finding)

```
Study ralph/AGENTS.md (how to build, test, deploy here) and ralph/IMPLEMENTATION_PLAN.md.
Pick the single most important open item. Search before you assume it is missing. Do ONLY that item.
Prove it with its backpressure (AGENTS.md lists which). Full implementations only, no placeholders.
If it needs the live game, take the bridge with `rimflow bridge take --idle-ok`; if refused, pick another item.
If it needs the owner (art he kept, scope, money, grant, anything he must see), write a card to
ralph/owner_inbox.md and pick another item. Never fly a flyer.
Update the plan (done, or why not, plus anything you learned), commit explicit paths, exit.
```

### 1.4 File layout (in a dedicated clone, `/home/mandrake/rm/ralph`)

| file | written by | read by | role |
|---|---|---|---|
| `ralph/PROMPT.md` | owner, the person sitting on the loop | every iteration | the 100-word instruction above |
| `ralph/AGENTS.md` | the loop (only when it learns how to build or test something) | every iteration | the build, test, deploy and live-test commands for each kind of item, and what proves each kind |
| `ralph/IMPLEMENTATION_PLAN.md` | the loop, plus a PLAN-mode run on demand | every iteration | one ordered list, one line per item: id, state, proof owed, note |
| `ralph/owner_inbox.md` | the loop | the owner (on his phone through rm-pulse) | cards for owner-only acts and questions; he answers in place |
| `ralph/STOP` | the owner, or the loop on a red tree | `loop.sh` | the off switch |
| `specs/` = existing `design/` | owner, earlier work | iterations, read only | the goals; nothing is copied |

The rimflow ledger becomes optional. The plan file is the queue. If the ledger stays, one iteration's commit runs
`rimflow close --sha <real sha>` (simulated as `r_ledger_commits`).

### 1.5 Backpressure: what rejects bad work

`AGENTS.md` maps each kind of item to the programs that already exist:

| kind | backpressure, run by the iteration before it may mark the item done |
|---|---|
| any Python | `run_selftests.py --only <tests>`; `code_review_status.py check <path>` must say CLEAN |
| XML patch or def | `validate_patch.py --live --defs` |
| C# | `winbuild.py` (a build failure rejects the item) |
| mod content, live | deploy plan, then `--apply`; `modcheck` on a bridge run taken with `--idle-ok` |
| art | the art-eval pipeline (`rimworld-art-evaluation`); anything the owner must see goes to `owner_inbox.md` |
| SteveDesktop runs | variant B only (section 2) |

The loop script itself checks one more thing: the tree must be green at the start of every iteration. Ralph has
no independent judge, so a check the iteration skips is simply skipped. Section 3 counts this as the biggest loss.

### 1.6 How the owner talks to it

- **Steering:** he edits `PROMPT.md`, `AGENTS.md` or the plan, and the next iteration reads the change. This is
  Huntley's "tuning the guitar": a steer is an edit, not a conversation.
- **Answering:** he answers cards in `owner_inbox.md` (rm-pulse can show that file on his phone). The next
  iteration that reads an answer acts on it.
- **Status:** the iteration logs plus `git log`. No seat answers "what is it doing?". That question is the one
  open assumption in the nudge numbers (`r_status_mult`, section 4).
- **Talking:** if he wants a conversation, he opens an ordinary Claude session. The loop does not hold one.

### 1.7 The live game, deploys and owner-only acts

- **Game:** the only route is `rimflow bridge take --idle-ok --for "<item>"`. The idle probe refuses when the
  owner is at the machine, when the state is UNMEASURED, or for any flyer or flight wording. A refusal means the
  iteration takes a different item. An OWNER hold is never taken. A loop runs one iteration at a time, so variant
  A cannot hold the bridge twice.
- **Deploy:** plan first, then `--apply`, with `validate_patch.py --live --defs` after. No C# deploy while the
  game runs (the DLL is locked).
- **Owner-only acts:** never done. A card goes to `owner_inbox.md` and the item is parked with "waiting on owner"
  in the plan.
- **Standing rulings** go into `AGENTS.md` as five lines: no worldgen, every DLC assumed, no flyer flights, wrong
  material deleted with every inbound reference fixed, nothing reaches the owner unread.

## 2. Variant B: a second loop on SteveDesktop

There are two shapes, and the sim runs both.

**AB_test (recommended): B owns live testing.** B runs the same `loop.sh` on SteveDesktop, which has its own game
and its own bridge. Its prompt:

```
Study ralph/AGENTS.md and ralph/TEST_PLAN.md. Pick the oldest item marked "built, untested".
Deploy it to this machine's game (plan, then --apply), run its live proof, record modcheck.
PASS: mark it "tested <sha>" in TEST_PLAN.md. FAIL: write the failure and the log path under the item
and mark it "rework". Never edit mod source. Never fly a flyer. Commit explicit paths, exit.
```

**AB_build: B is a second builder** on the same plan. Tickets follow their usual route, and an idle loop takes
work from the other's list.

**Sharing git without colliding.** The two loops never write the same file:

- A owns `IMPLEMENTATION_PLAN.md` and all mod source.
- B owns `TEST_PLAN.md` and `ralph/test_results/`.
- A reads B's results at the start of every iteration.

Each loop runs `git pull --rebase` before an iteration and `./publish` after. A rebase conflict can only happen on
a shared file, and there are none, so a conflict stops that loop (STOP file plus an inbox card) rather than
merging by hand. In AB_build both loops write mod source, so this guarantee is lost. Two loops can pick the same
item or touch the same def. The sim charges that as a collision (`b_collide`, 0-8% of iterations wasted).

## 3. What it loses against v3, function by function

The F-numbers and v3 states are from `rimflow_v3_minimal_opus_2026-10-29.md` §1. Its own state column records
how far v3 actually got (YES, PART, NO, OFF, DES).

| F | function | v3 state | Ralph A/B | what is lost, or why it is not needed |
|---|---|---|---|---|
| F1 | talk with the owner while present | YES | **LOST** | no conversation seat; he edits files or opens his own session |
| F2 | tell the owner things while away | PART | KEPT (rm-pulse) | the rm-pulse timers need no AI; they show the inbox and the git log |
| F3 | goals into ordered work | PART | REDUCED | one ordered plan file plus PLAN mode on demand; no weekly plan and no cut list |
| F4 | limit work in progress | NO | **GAINED** | WIP is exactly 1 by construction. v3 never enforced it |
| F5 | track the day against the plan | DES | LOST | the plan diff in git is the only record |
| F6 | build | YES | KEPT | at roughly a third of v2's sound throughput (section 5) |
| F7 | wake an idle builder | YES | NOT NEEDED | the loop never idles; the next iteration starts at once |
| F8 | keep the builder's context fresh | PART | **GAINED** | a fresh context every iteration, by construction |
| F9 | recover a dead seat | OFF | REDUCED | `timeout 90m` kills a hung iteration; nothing restarts a dead loop.sh except a systemd unit (owed) |
| F10 | game tests on SteveDesktop | PART | AB_test: KEPT | B is a loop, not testq: no admission or filler machinery |
| F11 | keep the test lane's evidence valid | NO | REDUCED | B's prompt must check the colony is alive; the prompt is the only enforcement |
| F12 | test results into item state | NO | KEPT (AB_test) | a FAIL marks the item "rework" in the plan; a fail does demote it |
| F13 | curate findings | PART | LOST | the plan's notes are the only findings store |
| F14 | "done" means done | NO | REDUCED | backpressure inside the iteration; no program checks the close afterwards |
| F15 | independent judging | NO | **LOST** | the iteration judges its own work; in AB_test, B's live run is a second check, not a blind one |
| F16 | check the judges | PART | LOST | |
| F17 | get review defects fixed | NO | REDUCED | a defect becomes a plan line like any other item |
| F18 | GPT review of components and the whole | NO | LOST | could return as a weekly cron job that writes plan lines (not designed) |
| F19 | measure machine, accounts, runway | YES | KEPT | ops_watch stays; loop.sh reads its runway |
| F20 | diagnose alarms, act on cost | PART | REDUCED | the only action is a stop on low runway |
| F21 | route every alarm to someone woken | NO | **NOT NEEDED / LOST** | there is nobody to route to; an alarm is either an inbox card or a STOP |
| F22 | watch the watchers | PART | REDUCED | the deadman watches loop.sh's heartbeat (one file) |
| F23 | lessons into skills and memory | NO | REDUCED | the loop writes `AGENTS.md` itself; skills are not curated |
| F24 | propose process improvements | PART | LOST | the owner is the innovator (prompt tuning) |
| F25 | decide whether the new system beats v2 | OFF | KEPT | this sim; a live comparison would read the same counters |
| F26 | health check, planted faults, process model | DES | LOST | |
| F27 | spend control | PART | **GAINED** | one process; the cost is iterations × iteration size, and the runway stop is enforced |
| F28 | serialize the game, respect the owner | YES | KEPT | the same bridge lock and idle probe |
| F29 | check the game grant before live work | NO | KEPT | an AGENTS.md line, and the bridge refuses without the grant |
| F30 | one config truth | PART | **GAINED** | the prompt plus AGENTS.md is the whole config |
| F31 | pause everything | YES | KEPT | the STOP file |
| F32 | publish, mirror, telemetry | PART | KEPT | `./publish` after every iteration |

Tally:

- **Lost outright: 8** (F1, F5, F13, F15, F16, F18, F24, F26).
- **Reduced: 10** (F3, F9, F11, F14, F17, F20, F22, F23, plus F2 and F10 kept only in narrower forms).
- **Gained by construction: 4** (F4, F8, F27, F30). v3 had these at NO or PART.
- **Not needed: 2** (F7, F21).

The losses that matter most are F15 and F18 (nobody independent checks finished work) and F1 (no live
conversation).

**What Ralph does not need** (v3 parts deleted with no replacement): the Dispatcher with its doorbell, re-rings
and `dispatcher_schedule.json`; seat_restart; the Producer, Operations, Auditor, Innovator and Arbiter role
files with their timers; helper budgets and the helper hook; role-header drift checks; the alarm routing table;
and the Conductor's rituals. These are the parts the minimal-design inventory lists as unexercised, OFF or
drifting.

## 4. Simulation

### 4.1 What was simulated

`src/RimMandrake/Utils/sim/ralph_loop_sim.py` imports the v2/v3 model (`rimflow_v3_sim.py`) and keeps its
calibrated outside world unchanged:

- owner presence and arrivals
- ticket classes and hidden defects
- discovery of escapes
- question cards
- the test rig
- token quotas

It replaces only the factory. The ensemble is the same 240 ABC-kept members per structure (park and pull) as the
v2/v3 estimates. Each member runs once at today's quotas and once with quotas unlimited, for 4 weeks with 1 week
of warm-up. Summaries are means over weeks 1-3. Every comparison is **paired**: each member runs v2, v3.0, v3.4
and the three Ralph variants on one seed, and the keyed randomness gives them the same owner and the same
arrivals. The selftest checks this.

Variants:

- **A:** one loop, serial, one ticket per iteration. An iteration costs a restart, a stack load, and the SAME
  keyed helper work v2's helpers drew for that ticket, run back to back in one context and scaled by assumed
  duration and token multipliers. A ticket's hidden quality is drawn as in v2, then moved by Ralph's quality and
  backpressure assumptions. Process tickets (the ones the owner or an agent files about the factory itself) are
  partly never filed, because Ralph has no factory to file them about. An iteration can go off track (the ticket
  goes back to the front of the plan) and can start a spiral. A spiral burns iterations until the loop escapes by
  itself or the owner notices and steers it (a steer counts as an owner nudge, plus 4 minutes of his attention).
  Status pings ("what is it doing?") are v2's rate times an assumed multiplier.
- **AB_test:** A, plus loop B. A product close waits for B's live test on a single lane. A pass closes it as
  `accepted_prod`; read that as "tested by a second loop", not "judged blind". A fail returns the ticket to A.
- **AB_build:** two builder loops on one plan, with stealing and collisions.

### 4.2 Every Ralph parameter is ASSUMED

Each member draws every parameter uniformly from its range, keyed by member id (seed 777).

| parameter | range | what it stands for |
|---|---|---|
| r_restart_s | 30-240 s | start-up of a fresh `claude -p` plus pull, pre-check and publish |
| r_ctx_ite | 60k-300k | tokens to load PROMPT, AGENTS, plan and the item's files each iteration |
| r_dur_mult | 0.7-1.5 | one context doing v2's helper work serially, against v2's parallel helpers (0.7 = read-only subagents help a lot; 1.5 = context fill slows it) |
| r_ite_mult | 0.6-1.2 | tokens for that work against v2's helpers (no helper briefs and returns, but a longer context) |
| r_quick_ite | 50k-300k | tokens for a quick (bookkeeping) ticket |
| r_mu_mult | 0.8-1.6 | defects per ticket against v2 (above 1 = more defects with no reviewer; below 1 = a fresh context and a short prompt help) |
| r_bp | 0-0.3 | extra share of defects caught by in-iteration backpressure |
| r_verify_mult | 0.6-1.1 | v2's verify-catch rate under self-verification |
| r_p_off | 0.03-0.20 | chance an iteration goes off track and achieves nothing |
| r_p_spiral | 0.05-0.40 | chance an off-track iteration starts a spiral |
| r_unstick_h | 0.2-2.0 per h | rate at which the loop escapes a spiral by itself |
| r_status_mult | 0.3-1.2 | owner status pings against v2 (no seat to ask, but no seat reporting either) |
| r_proc_keep | 0.2-0.7 | share of v2's process tickets that still exist under Ralph |
| r_ledger_commits | 0-1 | ledger commits per close (0 = plan file only) |
| r_bg_mult | 0.4-1.0 | background token burn (timers, ops_watch) against v2 |
| b_test_min | 10-45 min | one live test on SteveDesktop |
| b_test_ite | 100k-600k | tokens per live test |
| b_p_test | 0.5-0.95 | share of product tickets that need a live test |
| b_s_mult | 0.8-1.3 | B's sensitivity against the v3 rig |
| b_blind | 0-0.3 | extra catch because B did not write the code |
| b_collide | 0-0.08 | AB_build: share of iterations wasted on a collision |

There is a one-at-a-time sweep (40 members, each parameter at lo and hi, the others at their midpoints) and
Spearman splits over the full ensemble. Both are reported in `tables.md`.

### 4.3 Which metrics to trust (work first)

The 2026-10-27 backtest FAILED on ticket counts. Helpers per close went 5.2 → 3.3 → 1.5 over three v2 weeks while
the work stayed level, because the meaning of a ticket changed. Metrics that count work or ratios passed. So:

| metric | trust | why |
|---|---|---|
| ite_week (tokens) | **medium** | tokens passed the backtest; Ralph's token draws are paired with v2's helper draws and scaled by an assumed range |
| sound product per G tokens | **medium** | a ratio of work; mostly insensitive to how big a ticket is |
| blocked_h, proc_share | medium | structural: a loop that never waits cannot block |
| sound_prod_d, done_d (ticket counts) | **low** | the unit failed the backtest; read them as relative capacity, not as items per day |
| escapes_wk, defect_frac, rework | low | they ride on ticket counts plus r_mu_mult, which is a guess |
| nudges_d (owner messages) | **low; a single assumption** | Spearman +0.99 on r_status_mult; the model cannot tell the variants apart |
| cards_waiting_3d, owner wait | low | owner wait failed the backtest |
| accepted_prod_d (AB_test) | low | "tested by a second loop", not the same acceptance as v3.4's |

## 5. Results

Medians, with p10/p50/p90 in brackets where they matter. Park structure, today's quotas, n=240, unless stated.
Paired: "share higher" is the share of members where the variant beats the comparison system on that member's own
world.

### 5.1 Work (read these first)

| metric | v2 | v3.0 | v3.4 | Ralph A | AB_test | AB_build |
|---|---|---|---|---|---|---|
| tokens/week (ITE) | 1.90G | - | 2.01G | **0.64G** [0.48/0.87] | 0.67G | 1.12G [0.84/1.59] |
| sound product closes per G tokens | 182 [133/287] | - | 139 [102/214] | **191** [117/314] | 177 | 197 [120/309] |
| sound product closes/day | 49 | 48.6 | 40 | **17.5** [10.7/29.5] | 17.3 | 31.1 [20.8/49.6] |
| all closes/day | 129 | - | 106 | 38 | 36 | 67 |
| iterations/day | - | - | - | 48.6 | 48 | 88.7 |
| wasted iterations | - | - | - | 18% [8/28] | 18% | 21% [11/31] |
| product backlog at week 4 | 136 | - | 274 | **402** [184/646] | 398 | 158 |
| blocked hours/week | 21 | - | 62 | **0** | 0 | 0 |
| process share of closes | 0.67 | - | 0.70 | 0.44 | 0.44 | 0.42 |

Paired against v2:

- Ralph A has −31.7 sound closes/day; **0%** of members do better.
- AB_build has −18; 0% do better.
- Against v3.4, AB_build has −9; **14%** of members do better.
- Sound per token: A beats v2 in 52% of members (median +3.1 per G). AB_build beats v2 in 58% (+9.5).
- Tokens: every variant uses fewer than v2 in 100% of members.

Pull structure, today's quotas: v2 61, v3.4 46.5, A 18.4, AB_build 34.4 sound closes/day. Sound per G tokens: v2
210, v3.4 153, A 209, AB_build 207. The ordering is the same as park.

With quotas unlimited the Ralph rows hardly move, because they never reach the quota. v2 rises to 54.5 (park) and
63.2 (pull), so the gap widens.

### 5.2 Quality and the owner (lower trust)

| metric | v2 | v3.4 | Ralph A | AB_test | AB_build |
|---|---|---|---|---|---|
| escapes/week | 281 | 210 | 90 | 77 | 155 |
| escapes per sound close | 0.8 | 0.8 | 0.8 | 0.7 | 0.7 |
| defect fraction | 0.43 | 0.35-0.40 | 0.43 | 0.40 | 0.41 |
| accepted product/day | 0 | 58 | 0 | 10.8 (B-tested) | 0 |
| owner messages/day (nudges + steers) | 28.2 | 19.1 | 20.3 [10.1/30.5] | 20.4 | 20.7 |
| of which steers of a spiralling loop | - | - | 0.33 | 0.33 | 0.62 |
| owner cards waiting > 3 days | 5.8 | 8.8 | 3.1 | 3.1 | 3.4 |

Three findings:

- **Escapes fall only because work falls.** Escapes per sound close are the same as v2's. The model has no
  reason to expect fewer defects per item, because r_mu_mult's range runs both ways.
- **Owner messages are an assumption, not a result.** A sends fewer messages than v2 in 84% of members only
  because r_status_mult has a median of 0.75. Against v3.4, A sends about the same (+1, 55% higher).
- **The card count is lower because less work reaches the owner**, not because the owner is served better. The
  median owner resolve time is the same as v2's.

### 5.3 Sensitivity (one at a time, park, from the all-midpoints run)

- **Sound closes/day (mid 15.3):** r_dur_mult swings +6.8 at lo and −3.7 at hi; r_mu_mult +3.8/−2.9; r_p_off
  +1.7/−2.0; r_proc_keep +1.6/−1.4; r_bp −1.5/+1.3. No single parameter at its best value brings A within 20 of
  v2's 49. A gets close only with two loops and every throughput assumption at its best end.
- **Owner messages/day (mid 19.6):** r_status_mult swings −11.4/+11.6. Every other parameter moves it by less than
  0.4.
- **Tokens/week (mid 0.65G):** r_dur_mult +0.28G/−0.14G; r_ite_mult ±0.15G. Every parameter set stays under half
  of v2's burn.

### 5.4 What the model cannot see (and so cannot credit or charge)

- Ralph's quality claims (a fresh context, a short prompt, no handoff loss) enter only as r_mu_mult and r_bp. If
  they were large, they would show up as escapes per close going down. They do not, because the range was set
  both ways on purpose.
- Read-only subagents inside an iteration are folded into r_dur_mult. They are not modelled.
- The v3 build failures (an alarm routed to a seat that never wakes, a Dispatcher that never fires) are not in
  the v3.x rows. Those rows model v3 as designed, not as it ran on day one. Ralph has almost none of those parts,
  so this bias favours v3.
- A ticket in the model is a fixed unit of work. Under Ralph the unit is an iteration, and there are no
  file-and-close bookkeeping tickets. That is the same weakness that failed the backtest, which is why ticket
  counts are trusted least.

## 6. Verdict and how far to trust it

- **Capacity (medium-low trust):** one Ralph loop is a serial builder. It does about a third of v2's work for
  about a third of the tokens. Its sound work per token is no better than v2's (a coin flip across members) and
  better than v3.4's. It does not keep up with today's arrival rate: the backlog grows by about 100 items a week.
  Two loops (AB_build) reach about two thirds of v2's sound throughput and beat v3.4 in 14% of members.
- **Simplicity (high trust; structural, not simulated):** WIP is 1, context is always fresh, there are no blocked
  hours, no idle seats, no wake path to fail, and one config file. Four of v3's inventory functions that never
  worked come for free.
- **What it costs (high trust; structural):** nobody independent checks finished work (F15, F18), there is no
  live conversation (F1), and findings and planning are reduced to one list.
- **Owner messages (low trust):** the result depends on a single unmeasured assumption. Measuring it would take
  one week of Ralph A on a narrow slice, counting "what is it doing?" messages.
- **If the owner wants to try it:** run variant **AB_test** on one mod for one week, beside v3, not instead of it.
  Its own clone and its own plan file mean it cannot collide with the seats. Watch three numbers: sound closes
  per G tokens, B's fail rate, and owner messages about the loop. That would replace the three weakest
  assumptions (r_dur_mult, r_mu_mult, r_status_mult) with measurements.

Reproduce:

```
python3 src/RimMandrake/Utils/sim/ralph_loop_sim.py --structure park ensemble --quota today
python3 src/RimMandrake/Utils/sim/ralph_loop_sim.py --structure park oat
python3 src/RimMandrake/Utils/sim/ralph_loop_sim.py report
python3 src/RimMandrake/Utils/sim/selftest_ralph_loop_sim.py
```

Outputs are in `D:\ClaudeWork\rimmandrake\ralph_sim\` (`results.json`, `tables.md`, `ens_*.jsonl`, `oat_park.jsonl`).
