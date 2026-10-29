# The best simple Ralph loop for RimMandrake (2026-10-29)

Item `RALPH_LOOP_DESIGN_ONE_PROMPT_FOREVER`. Status: DRAFT, revised after GPT's check (section 9). Nothing here is
live: no timer, role file, seat or config was changed to write it.

The owner asked (2026-10-29, verbatim): "I am also quite fascinated by studying the difference between this elborte
system and the much simpler implementation following the Ralph loop idea. Please do a deep design pass feeding the
whole spec for our goals and needs and past solutions and ask the question "what's the best simple Ralph loop to get
this done?" A variation might be to have a second Ralph loop running in Steve desktop. I'm interested to see what it
looks like. Then make a simulation to compare it to v2 and v3 estimates. Then have got check it."

Then (2026-10-29, verbatim): "What if we model two Ralph loops side by side, plus the ability to do live testing on
Steve desktop and archmagi. So that's four agents. Two live runners. Two ralphs. How might that do? I assume you're
modeling the likelihood of bugs, fix length, and other parameters we can measure form the past? How reliable are
these predictions?"

**Answer in one paragraph.** The simplest Ralph that is safe is a shell loop on Archmagi. Each pass starts a fresh
`claude -p` on a short prompt that picks one item from a plan file. Each item carries its own acceptance criteria
and proof command. After the agent exits, the loop itself re-runs the checks and publishes only if they pass. A
failed candidate is kept for the next fresh pass to repair, and after 3 failed tries the item is parked with its
evidence. On the same calibrated world as the v2/v3 estimates, **the four-agent version (variant C: two Ralph
builders split by mod area, plus live-test runners on SteveDesktop and Archmagi)** closes a median **31 sound
product tickets a day, against v2's 49 and v3.4's 40**. It spends **1.23G tokens a week against 1.9-2.0G**, and its
sound work per token sits between v3.4's and v2's (180 per G, against 139 and 182). It beats v3.4 on closes in only
9% of members, but on closes per token in 78% of them. **These are model numbers, not forecasts.** The ticket unit
they count failed the 10-27 backtest. The parameters that move them most are defect rates that the past data barely
constrain, and every Ralph-specific parameter is assumed. What is reliable is structural: fresh contexts, no
coordinating machinery, a serial loop trading capacity for spend, and a test runner adding evidence. Whether real
Ralph is a third, two thirds or as much as v3 is a question for the cheap controlled trial in section 8, not for
more simulation.

## 0. Sources

Fetched 2026-10-29. Copies are in `D:\ClaudeWork\rimmandrake\ralph_sim\web\`.

- Geoffrey Huntley, "Ralph Wiggum as a software engineer", https://ghuntley.com/ralph/ (14 Jul 2025). It gives the
  loop as `while :; do cat PROMPT.md | claude-code ; done` and says "One item per loop" twice. Its other rules:
  specs in `specs/*`, a `fix_plan.md` list, and `AGENT.md` for how to build and test. **Many subagents may search
  and write, but only one runs build and test**, and that one is the backpressure. So Ralph is not necessarily
  serial inside a pass; the sim's `+sub` variants model this (section 4). It names "placeholder and minimal
  implementations" and duplicate implementations as the failure modes. The human "sits on the loop" and tunes the
  prompt when it goes off the rails.
- Geoffrey Huntley, "loop", https://ghuntley.com/loop/ (17 Jan 2026). Ralph is deliberately monolithic: one process,
  one repo, one task per loop.
- repomirror report, https://raw.githubusercontent.com/repomirrorhq/repomirror/main/repomirror.md. Overnight Ralph
  loops cost "a little less than $800" in inference and made about 1,100 commits. One team found a prompt grown to
  1,500 words made the agent "slower and dumber" and went back to a short one. That is one anecdote about one
  bloated prompt. It is not a measured optimum, and this design does not rely on any word count.
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
- GPT's review of the first draft: `D:\ClaudeWork\rimmandrake\ralph_sim\gpt_check\review.md`. Section 9 lists what
  it changed.

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

The first draft ran its checks BEFORE the agent and published whatever the agent left, whether it passed or not.
GPT caught it, and this version fixes it. The loop judges the agent's result with its own post-change gate, and
only a candidate that passes is published.

```bash
#!/usr/bin/env bash
# One fresh claude -p per pass, one plan item per pass. The loop, not the agent, decides what is published.
set -uo pipefail
ROOT=/home/mandrake/rm/ralph                      # its own clone
CTL=/mnt/d/ClaudeWork/rimmandrake/ralph           # STOP, lock, status and logs live OUTSIDE git
LOG=$CTL/log; mkdir -p "$LOG"
exec 9>"$CTL/loop.lock"; flock -n 9 || { echo "another loop.sh is running"; exit 1; }
cd "$ROOT" && [ "$(git rev-parse --show-toplevel)" = "$ROOT" ] || { echo "not the ralph clone"; exit 1; }
MAX=${MAX:-0}; i=0                                # 0 = no cap; the supervisor owns restarts
status(){ printf '%s pass=%s %s\n' "$(date -u +%FT%TZ)" "$i" "$1" >"$CTL/status"; }
release(){ python3 src/RimMandrake/rimflow/cli.py bridge release --mine >/dev/null 2>&1 || true; }  # proposed flag
trap 'release; status exited' EXIT
while [ "$MAX" -eq 0 ] || [ "$i" -lt "$MAX" ]; do
  [ -e "$CTL/STOP" ] && { status STOP; break; }
  python3 src/RimMandrake/Utils/ops_watch.py --runway-ok 0.15 || { status "runway low"; break; }   # proposed flag
  for n in 1 2 3; do git pull --rebase -q && break; sleep $((n*30)); done || { status "pull failed"; break; }
  git switch -q ralph/wip 2>/dev/null || git switch -q -c ralph/wip
  git merge -q --ff-only main 2>/dev/null || true
  base=$(git rev-parse HEAD)
  # A red start is allowed ONLY when it is the known failed candidate the last pass left behind.
  if ! python3 src/RimMandrake/Utils/run_selftests.py --quick >"$LOG/pre.$i" 2>&1; then  # proposed flag
    [ -e "$CTL/last_failure.md" ] || { status "red start, unexplained"; touch "$CTL/STOP"; break; }
  fi
  status "agent running"
  prompt="$(cat ralph/PROMPT.md; [ -e "$CTL/last_failure.md" ] && cat "$CTL/last_failure.md")"
  timeout --kill-after=60 90m claude -p "$prompt" --output-format json >"$LOG/it.$i.jsonl" 2>&1
  rc=$?
  release                                          # whatever the agent did, the bridge is free again
  # The gate runs whatever the agent claimed: the item's own proof command, the tests for changed paths,
  # validate_patch for XML, winbuild for C#. It also refuses an empty or placeholder diff.
  item=$(python3 src/RimMandrake/Utils/ralph_gate.py --item-of "$base")              # proposed
  if [ "$rc" -eq 0 ] && python3 src/RimMandrake/Utils/ralph_gate.py --base "$base" >"$LOG/post.$i" 2>&1; then
    git switch -q main && git merge -q --ff-only ralph/wip && ./publish \
      && rm -f "$CTL/last_failure.md" "$CTL/tries.$item"
  else
    n=$(( $(cat "$CTL/tries.$item" 2>/dev/null || echo 0) + 1 )); echo "$n" >"$CTL/tries.$item"
    printf 'item %s try %s rc=%s base=%s head=%s\nlogs %s/it.%s.jsonl %s/post.%s\n' \
      "$item" "$n" "$rc" "$base" "$(git rev-parse HEAD)" "$LOG" "$i" "$LOG" "$i" >"$CTL/last_failure.md"
    # the candidate's commits stay on ralph/wip, unpublished, for the next pass to repair
    if [ "$n" -ge 3 ]; then                       # park with evidence, start the next item clean
      git branch -f "ralph/failed/$item" HEAD
      python3 src/RimMandrake/Utils/ralph_gate.py --park "$item" --evidence "ralph/failed/$item"
      git switch -q main && git branch -f ralph/wip main && rm -f "$CTL/tries.$item" "$CTL/last_failure.md"
    fi
  fi
  i=$((i+1))
done
```

What changed from the first draft, and why:

- **The agent's exit status is checked.** A non-zero exit, a timeout or a kill counts as a failed candidate.
- **The checks run AFTER the agent, and nothing is published unless they pass.** `ralph_gate.py` reads the
  plan line the pass worked on and re-runs that item's proof command itself. The agent's own report is not
  trusted.
- **A failed post-check does not kill the loop.** The candidate stays on `ralph/wip`, unpublished, with
  a `last_failure.md` (outside git) naming the item, the try number, both shas and the log paths. The loop
  appends that note to the next pass's prompt. That pass is a fresh context, and its only job is to repair the
  candidate. After 3 failed tries the candidate is
  kept on `ralph/failed/<item>` as evidence and the item is parked in the plan. That is the same attempt cap the
  sim uses.
- **The STOP rule is narrow.** The loop stops itself only on a red start that is NOT the known failed candidate,
  on a failed pull after 3 tries, on a low token runway, or on the STOP file. A known failed candidate is repaired,
  not stopped on.
- **Bounded recovery.** `timeout --kill-after` stops a hung agent. The EXIT trap and the release after each pass
  free the bridge. `flock` stops a second copy of the loop from starting. The working directory is checked before
  anything runs.
- **Control outside git.** STOP, the lock, the failure note, the try counters, the logs and the one-line `status` file live under
  `D:\ClaudeWork`, so neither an agent editing the repo nor a bad merge can delete the off switch.
- **MAX defaults to no cap.** A supervisor, a systemd user unit, restarts a dead loop and is the thing to stop.
  Touching STOP takes effect at the next pass. Stopping the unit stops a pass mid-run (SIGTERM, then the EXIT trap
  frees the bridge).
- **Spend cap per pass.** The 90-minute timeout is the only hard cap shown. A per-pass token cap with headroom
  should be added, either the CLI's own budget option if it has one (not checked) or a watcher killing the pass
  above a threshold. This is owed.

**Not yet built:** `ralph_gate.py`, `ops_watch.py --runway-ok`, `run_selftests.py --quick`,
`bridge release --mine`, the systemd supervisor and the deadman reading `status`. Each is small, but none exists.
The script reads the account, host and keys from the environment, as the project rule requires; none are named
here.

### 1.3 `ralph/PROMPT.md`

It stays short and focused, because every pass pays to read it. There is no target word count.

```
Read ralph/POLICY.md (owner rules; never edit it), ralph/AGENTS.md (how to build, test, deploy),
ralph/IMPLEMENTATION_PLAN.md and the answered cards in ralph/owner_inbox.md.
If a LAST FAILURE note follows this prompt, your one job is to repair that candidate so its proof passes.
Otherwise pick the single most important open item that has acceptance criteria and a proof command.
Search before you assume something is missing. Full implementations only, no placeholders.
Run the item's proof command. The loop runs it again after you exit and publishes only if it passes.
Live game: `rimflow bridge take --idle-ok`; if refused, pick another item. Never fly a flyer.
Owner-only acts (art he kept, scope, money, grants, anything he must see): write a card, pick another item.
Update the plan line (state, proof log path) and AGENTS.md if you learned how to build or test something.
Commit explicit paths. Exit 0 only if the item is done.
```

### 1.4 File layout (in a dedicated clone, `/home/mandrake/rm/ralph`)

| file | written by | read by | role |
|---|---|---|---|
| `ralph/PROMPT.md` | the owner, sitting on the loop | every pass | the instruction above |
| `ralph/POLICY.md` | the owner only | every pass, and the gate | grants, deletion, spending, owner-facing material, the standing rulings. The gate refuses any candidate that touches it |
| `ralph/AGENTS.md` | the loop, when it learns how to build or test something | every pass | build, test, deploy and live-test commands for each kind of item |
| `ralph/IMPLEMENTATION_PLAN.md` | the loop, plus a PLAN-mode run on demand | every pass, the gate | one ordered list, one line per item: id, state, acceptance criteria, proof command, note |
| `D:\ClaudeWork\rimmandrake\ralph\last_failure.md` | `loop.sh` | the next pass (appended to its prompt) | the failed candidate to repair |
| `ralph/owner_inbox.md` | the loop | the owner (on his phone through rm-pulse) | cards for owner-only acts and questions; he answers in place |
| `D:\ClaudeWork\rimmandrake\ralph\STOP` | the owner, or `loop.sh` on an unexplained red start | `loop.sh` | the off switch, outside git |
| `specs/` = a NARROW current spec | the owner | passes, read only | current requirements only. Historical design documents stay out, because a pass cannot tell a reversed ruling from a live one |

GPT's point 4 is the reason for `POLICY.md`. The rules on grants, deletion, spending and owner-facing material
must not sit in the same file the loop rewrites as it learns.

The rimflow ledger becomes optional. The plan file is the queue. If the ledger stays, the publishing step runs
`rimflow close --sha <real sha>` (simulated as `r_ledger_commits`).

### 1.5 Backpressure: what rejects bad work

`AGENTS.md` maps each kind of item to programs that already exist. `ralph_gate.py` runs the same list after the
agent exits:

| kind | backpressure, run by the pass AND again by the gate |
|---|---|
| any Python | `run_selftests.py --only <tests>`; `code_review_status.py check <path>` is recorded, not required (nobody reviews) |
| XML patch or def | `validate_patch.py --live --defs` |
| C# | `winbuild.py` (a build failure rejects the item) |
| mod content, live | deploy plan, then `--apply`; `modcheck` on a bridge run taken with `--idle-ok` |
| art | the art-eval pipeline (`rimworld-art-evaluation`); anything the owner must see goes to `owner_inbox.md` |
| every item | its own proof command from the plan line; an empty or placeholder diff is refused |

Ralph still has no independent judge. The gate re-runs the checks the item names, but if the item's criteria are
weak, the gate is weak. Section 3 counts this as the biggest loss.

### 1.6 How the owner talks to it

- **Steering:** he edits `PROMPT.md`, `POLICY.md`, `AGENTS.md` or the plan, and the next pass reads the change.
  This is Huntley's "tuning the guitar": a steer is an edit, not a conversation.
- **Answering:** he answers cards in `owner_inbox.md` (rm-pulse can show that file on his phone). The next pass
  that reads an answer acts on it.
- **Status:** the `status` file, the pass logs and `git log`. No seat answers "what is it doing?". How often he
  still asks is the one open assumption in the message numbers (`r_status_mult`, section 4).
- **Talking:** if he wants a conversation, he opens an ordinary Claude session. The loop does not hold one.

### 1.7 The live game, deploys and owner-only acts

- **Game:** the only route is `rimflow bridge take --idle-ok --for "<item>"`. The idle probe refuses when the
  owner is at the machine, when the state is UNMEASURED, or for any flyer or flight wording. A refusal means the
  pass takes a different item. An OWNER hold is never taken. Only one copy of the loop can run (flock), so variant
  A cannot hold the bridge twice.
- **Deploy:** plan first, then `--apply`, with `validate_patch.py --live --defs` after. No C# deploy while the
  game runs (the DLL is locked).
- **Owner-only acts:** never done. A card goes to `owner_inbox.md` and the item is parked with "waiting on owner"
  in the plan.
- **Standing rulings** live in `POLICY.md`: no worldgen, every DLC assumed, no flyer flights, wrong material
  deleted with every inbound reference fixed, nothing reaches the owner unread.

## 2. Variant B: a second agent on SteveDesktop

There are two shapes, and the sim runs both.

**AB_test: B tests fixed candidates.** GPT's protocol, adopted:

- **A alone writes source and candidate records.** When an item's gate passes and it needs a live test, A
  publishes it as a candidate: item id, the exact SHA, and the deploy plan.
- **B tests that fixed SHA and nothing else.** It checks out the SHA, deploys it to SteveDesktop's own game, runs
  the item's live proof and writes ONE result record: SHA, deploy contents, game and mod versions, save used,
  verdict and log paths. B never edits mod source. Results go to a results branch or store that only B writes.
- **An invalid environment is not a fail.** A dead colony, a stale log or a harness fault gives "test invalid",
  and the candidate is re-queued. It does not go back to A as rework.
- **A source change invalidates a result.** A result counts only for its SHA. If A changes the item again, the
  old result is void.
- **Required tests are a fixed property of an item.** An item that needs a live test cannot close without one.
  After 3 failed live rounds it is parked with its evidence; it is not closed untested. The first sim draft let a
  third attempt skip the test, and that is fixed.
- **Git races** are handled by the bounded fetch, rebase and push retry in `loop.sh`. A conflict that survives 3
  tries stops that loop, which is safe because each writer owns different files.
- **B may be a script, not an agent.** If an item's live proof is a fixed command, B is a scripted worker that
  runs it. Another coding agent is needed only where judging the run takes judgment (GPT's point 5).

**AB_build: B is a second builder** on the same plan. Tickets follow their usual route, and an idle loop takes
work from the other's list. Both write mod source, so two loops can pick the same item or touch the same def. The
sim charges that as a collision (`b_collide`, 0-8% of passes wasted).

**A separate clone does not isolate Ralph from v3.** The first draft said Ralph's own clone "cannot collide" with
the seats. That is false: both push to the same remote, deploy to the same game folders and take the same bridge.
A trial beside v3 needs exclusive source scope (one mod each) and its own deployment target (section 8).

## 3. Variant C: two builders and two live runners (the four agents)

### 3.1 Shape

- **Builders A1 and A2**, both on Archmagi, each running `loop.sh` in its own clone with its own plan file.
- **The work is split by area.** Every item has a home area: a mod, or a utility directory. A1 and A2 each own a
  fixed set of areas, following the FOUNDRY/BENCH routes the sim already uses. A builder takes an item outside its
  own areas only when its own list is empty (a "steal"). The gate refuses a candidate that edits a file outside
  the item's area, unless the plan line lists that file as shared.
- **Collisions** are rare on a builder's own area (`c_collide_area`, assumed 0-2% of passes) and as likely as in
  AB_build on a stolen item (`b_collide`, 0-8%). Each builder writes its own plan and notes file. The shared
  owner files (`POLICY.md`, the inbox) are written only by the owner and by the publishing step's append, never
  edited by a pass.
- **Builders never take the bridge.** Every live test goes through the runners.
- **Runner S, on SteveDesktop**, is always available. It follows section 2's fixed-SHA protocol.
- **Runner A, on Archmagi**, uses the owner's own game. It takes the bridge only through `bridge take --idle-ok`,
  and only after the owner has left the game for 20 minutes (the existing idle rule). When he comes back, it
  yields at once: it aborts the run, frees the bridge and puts the candidate back at the front of the queue. The
  next time it takes the game after he played, it pays a cold load (`c_cold_min`, 0.5-25 min). The endpoints are
  the measured 22 s for the 13-mod minimal list and about 25 min for his full list.
- **Both runners pull from one test queue**, oldest candidate first, and write results under the same rules.

### 3.2 The conflicts the owner's question raises

- **Runner A against the owner's play.** Runner A works only in hours when he is not at the game, plus the share of
  his present hours when he is at the machine but not playing (`c_a_present_ok`, 0-50%, assumed). Each return
  that interrupts a test is a "bump": the run is lost, he spends about 2 minutes, and with chance `c_bump_msg` he
  sends a message about it.
- **Runner A against the 20-minute idle rule.** The rule is kept exactly. The sim checks that runner A never starts
  while he holds the game or within 20 minutes after, using an independent clock. It also checks that every bump
  falls at the hour he takes the game back.
- **What the sim does NOT charge, and should be checked live:**
  - If runner A swaps to a minimal mod list, the owner's next session needs a cold load of his full list, about 25
    minutes of HIS time. Two fixes: runner A tests on his full list only, or it restores his list and relaunches
    as soon as it finishes. Either way it costs more of runner A's time than the sim charges.
  - The two builders and runner A share one machine's CPU and memory.
  - When the owner sits down, a game that is busy loading is in his way even when no test is running.

## 4. What it loses against v3, function by function

The F-numbers and v3 states are from `rimflow_v3_minimal_opus_2026-10-29.md` §1. Its own state column records
how far v3 actually got (YES, PART, NO, OFF, DES).

**Read the LOST rows with care (GPT).** Where v3's state is NO, OFF or DES, v3 never delivered that function either.
Losing it is a loss against v3 as designed, not against v3 as it runs. Those rows are marked *(v3 never had it)*.

| F | function | v3 state | Ralph A/B/C | what is lost, or why it is not needed |
|---|---|---|---|---|
| F1 | talk with the owner while present | YES | **LOST** | no conversation seat; he edits files or opens his own session |
| F2 | tell the owner things while away | PART | KEPT (rm-pulse) | the rm-pulse timers need no AI; they show the inbox, `status` and the git log |
| F3 | goals into ordered work | PART | REDUCED | one ordered plan file plus PLAN mode on demand; no weekly plan and no cut list |
| F4 | limit work in progress | NO | **GAINED** | WIP is exactly 1 per loop by construction. v3 never enforced it |
| F5 | track the day against the plan | DES | LOST *(v3 never had it)* | the plan diff in git is the only record |
| F6 | build | YES | KEPT | throughput in section 6 |
| F7 | wake an idle builder | YES | NOT NEEDED | the loop never idles; the next pass starts at once |
| F8 | keep the builder's context fresh | PART | **GAINED** | a fresh context every pass, by construction |
| F9 | recover a dead seat | OFF | REDUCED | the timeout kills a hung pass; a systemd supervisor restarts a dead loop (owed) |
| F10 | game tests on SteveDesktop | PART | KEPT (AB_test, C) | a runner on fixed SHAs, not testq: no admission or filler machinery |
| F11 | keep the test lane's evidence valid | NO | REDUCED | "test invalid" is a verdict; the runner's prompt or script is still the only enforcement |
| F12 | test results into item state | NO | KEPT (AB_test, C) | a fail sends the SHA back to the builder; a result is void once source changes |
| F13 | curate findings | PART | LOST | the plan's notes are the only findings store |
| F14 | "done" means done | NO | REDUCED | the post-change gate re-runs each item's proof before publishing; nobody checks the criteria themselves |
| F15 | independent judging | NO | **LOST** *(v3 never had it)* | the pass judges its own work; a runner's live run is a second check, not a blind one |
| F16 | check the judges | PART | LOST | |
| F17 | get review defects fixed | NO | REDUCED | a defect becomes a plan line like any other item |
| F18 | GPT review of components and the whole | NO | LOST *(v3 never had it)* | could return as a weekly cron job that writes plan lines (not designed) |
| F19 | measure machine, accounts, runway | YES | KEPT | ops_watch stays; loop.sh reads its runway |
| F20 | diagnose alarms, act on cost | PART | REDUCED | the only action is a stop on low runway |
| F21 | route every alarm to someone woken | NO | NOT NEEDED / LOST | there is nobody to route to; an alarm is an inbox card or a STOP |
| F22 | watch the watchers | PART | REDUCED | the deadman watches the `status` file's age |
| F23 | lessons into skills and memory | NO | REDUCED | the loop writes `AGENTS.md` itself; skills are not curated |
| F24 | propose process improvements | PART | LOST | the owner is the innovator (prompt tuning) |
| F25 | decide whether the new system beats v2 | OFF | KEPT | this sim, and the trial in section 8 |
| F26 | health check, planted faults, process model | DES | LOST *(v3 never had it)* | |
| F27 | spend control | PART | **GAINED** | the cost is passes × pass size, the runway stop is enforced, and a per-pass cap is owed |
| F28 | serialize the game, respect the owner | YES | KEPT | the same bridge lock and idle probe; in C, runner A yields when he returns |
| F29 | check the game grant before live work | NO | KEPT | a POLICY.md line, and the bridge refuses without the grant |
| F30 | one config truth | PART | **GAINED** | PROMPT, POLICY and AGENTS are the whole config |
| F31 | pause everything | YES | KEPT | the STOP file, outside git |
| F32 | publish, mirror, telemetry | PART | KEPT | `./publish` after every passing gate |

Tally:

- **Lost outright: 8** (F1, F5, F13, F15, F16, F18, F24, F26). Four of these (F5, F15, F18, F26) v3 never had.
- **Reduced: 10** (F3, F9, F11, F14, F17, F20, F22, F23, plus F2 and F10 kept only in narrower forms).
- **Gained by construction: 4** (F4, F8, F27, F30). v3 had these at NO or PART.
- **Not needed: 2** (F7, F21).

Against v3 as it runs today, the losses that matter are F1 (no live conversation) and F13/F16/F24 (no findings
store, no check on judges, no innovator). Against v3 as designed, F15 and F18 (independent judging) matter most.

**What Ralph does not need** (v3 parts deleted with no replacement): the Dispatcher with its doorbell, re-rings
and `dispatcher_schedule.json`; seat_restart; the Producer, Operations, Auditor, Innovator and Arbiter role
files with their timers; helper budgets and the helper hook; role-header drift checks; the alarm routing table;
and the Conductor's rituals. These are the parts the minimal-design inventory lists as unexercised, OFF or
drifting.

## 5. Simulation

### 5.1 What was simulated

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
of warm-up. Summaries are means over weeks 1-3, except the final backlog, which is read at the end of week 4.
Every comparison is **paired**: each member runs v2, v3.0, v3.4 and every Ralph variant on one seed, and the keyed
randomness gives them the same owner and the same arrivals. The selftest checks this.

Variants:

- **A:** one loop, one ticket per pass. A pass costs a restart, a stack load, and the SAME keyed helper work that
  v2's helpers drew for that ticket. That work is done back to back in one context and scaled by assumed duration
  and token multipliers. A ticket's hidden quality is drawn as in v2, then moved by Ralph's quality and
  backpressure assumptions. Process tickets (the ones filed about the factory itself) are partly never filed,
  because Ralph has no factory to file them about. A pass can go off track (the ticket goes back to the front of
  the plan) and can start a spiral. A spiral burns passes until the loop escapes by itself or the owner notices and
  steers it. A steer counts as an owner message plus 4 minutes of his attention. Status pings ("what is it
  doing?") are v2's rate times an assumed multiplier.
- **AB_test:** A, plus runner B on SteveDesktop. A product item that needs a live test (a fixed share,
  `b_p_test`) closes only after B passes it. A fail sends it back to A. After 3 failed live rounds it is parked,
  not closed. `accepted_prod` means "tested by a second agent", not "judged blind".
- **AB_build:** two builder loops on one plan, with stealing and collisions.
- **C:** two builders split by area (section 3) plus runners S and A. Runner A follows the owner's game hour by
  hour: it never starts while he holds the game or within 20 minutes after, it aborts when he takes it back, it
  pays a cold load after he played, and a share of its runs are void (`c_invalid`) and re-run. In C the old v2
  verify step is off; all live checking is done by the runners.
- **A+sub and C+sub:** the same, with Huntley's parallel subagents for search and writing inside a pass, and one
  worker running build and test. A pass runs `r_par` (1.2-2.5×) faster and costs `r_par_ite` (1.0-1.3×) more
  tokens. This answers GPT's point that Ralph is not necessarily serial.

What else changed in the sim after GPT's check:

- **A determinism bug is fixed.** The sim keyed some per-ticket sets by Python `id()`. A freed ticket's id could
  be reused, so AB_test gave slightly different answers on the same seed in one process. That is why GPT saw
  `b_collide`, which AB_test never uses, move AB_test's numbers. Tickets are now held as objects, and the
  selftest runs AB_test and C three times on one seed and requires identical results.
- **Outputs are fingerprinted.** Every result row carries a hash of the model code and parameters. A resumed run
  that finds rows with another fingerprint moves them aside instead of mixing them in.
- **Required tests are enforced.** An instrumented check counts any item that needed a test but closed without one.
  The count must be 0, and it is.
- **The report now carries** the true final backlog, owner minutes per week, and per-member sound closes per G
  tokens with paired win shares.

### 5.2 The parameters

Each member draws every Ralph parameter uniformly from its range, keyed by member id (seed 777). **All of them are
ASSUMED**; none was fitted to data, because no Ralph loop has run here.

| parameter | range | what it stands for |
|---|---|---|
| r_restart_s | 30-240 s | start-up of a fresh `claude -p` plus pull, pre-check and publish |
| r_ctx_ite | 60k-300k | tokens to load PROMPT, AGENTS, plan and the item's files each pass |
| r_dur_mult | 0.7-1.5 | one context doing v2's helper work serially, against v2's parallel helpers |
| r_ite_mult | 0.6-1.2 | tokens for that work against v2's helpers (no helper briefs and returns, but a longer context) |
| r_quick_ite | 50k-300k | tokens for a quick (bookkeeping) ticket |
| r_mu_mult | 0.8-1.6 | defects per ticket against v2 (above 1 = more defects with no reviewer; below 1 = a fresh context helps) |
| r_bp | 0-0.3 | extra share of defects caught by the mandatory gate |
| r_verify_mult | 0.6-1.1 | v2's verify-catch rate under self-verification (A, AB_build) |
| r_p_off | 0.03-0.20 | chance a pass goes off track and achieves nothing |
| r_p_spiral | 0.05-0.40 | chance an off-track pass starts a spiral |
| r_unstick_h | 0.2-2.0 per h | rate at which the loop escapes a spiral by itself |
| r_status_mult | 0.3-1.2 | owner status pings against v2 |
| r_proc_keep | 0.2-0.7 | share of v2's process tickets that still exist under Ralph |
| r_ledger_commits | 0-1 | ledger commits per close (0 = plan file only) |
| r_bg_mult | 0.4-1.0 | background token burn (timers, ops_watch) against v2 |
| b_test_min | 10-45 min | one live test |
| b_test_ite | 100k-600k | tokens per live test |
| b_p_test | 0.5-0.95 | share of product items that need a live test |
| b_s_mult | 0.8-1.3 | a runner's sensitivity against the v3 rig |
| b_blind | 0-0.3 | extra catch because the runner did not write the code |
| b_collide | 0-0.08 | AB_build, and stolen items in C: share of passes wasted on a collision |
| c_collide_area | 0-0.02 | C: collision on a builder's own area |
| c_a_present_ok | 0-0.5 | C: share of the owner's present hours in which Archmagi's game is still free |
| c_cold_min | 0.5-25 min | C: runner A's cold load after the owner used the game (endpoints measured: 22 s, ~25 min) |
| c_invalid | 0-0.3 | C: share of live runs whose evidence is void and must be re-run |
| c_bump_msg | 0-1 | C: chance he sends a message when he finds a test in his game |
| r_par | 1.2-2.5 | +sub: speed-up of a pass from parallel subagents |
| r_par_ite | 1.0-1.3 | +sub: token overhead of those subagents |

## 6. Results

Medians, with [p10/p90] where they matter. Park structure, today's quotas, n=240, unless stated. "Share higher"
is the share of the 240 members in which the variant beats the comparison system on that member's own world.
**These shares describe this ensemble under its assumptions; they are not probabilities that a real system wins.**

### 6.1 Work (read these first, with section 7's caveats)

| metric | v2 | v3.4 | A | A+sub | AB_test | AB_build | **C** | C+sub |
|---|---|---|---|---|---|---|---|---|
| tokens/week | 1.90G | 2.01G | 0.64G | 1.02G | 0.69G | 1.12G | **1.23G** [0.92/1.66] | 1.63G |
| sound product closes per G tokens | 182 [134/281] | 139 [103/214] | 191 [120/308] | 178 | 170 | 197 | **180** [111/275] | 160 |
| sound product closes/day | 49 [36/73] | 40 [29/60] | 17.5 [11/30] | 25.5 | 17.0 | 31.1 | **30.9** [21/50] | 34.5 |
| all closes/day | 129 | 106 | 38 | 55 | 35 | 67 | **64** | 74 |
| passes/day | - | - | 49 | 71 | 47 | 89 | **87** | 102 |
| wasted passes | - | - | 18% | 18% | 18% | 21% | **19%** | 19% |
| product backlog, end of week 4 | 232 [50/454] | 357 [210/621] | 558 [260/893] | 371 | 552 | 252 | **200** [2/541] | 60 |
| blocked hours/week | 21 | 62 | 0 | 0 | 0 | 0 | **0** | 0 |

v3.0 closes 48.6 sound/day (park) and 61.5 (pull).

Paired:

- **Sound closes/day:** every Ralph variant closes fewer than v2 in every member (C+sub beats v2 in 0.4%). Against
  v3.4, C is −9.3/day and higher in **9%** of members; AB_build is higher in 14%, C+sub in 23%, A+sub in 5% and A
  in 0%.
- **Sound closes per G tokens:** against v2, C is higher in 42% of members (median −8), A in 52% (+3) and AB_build
  in 58% (+9). Against v3.4, C is higher in **78%** (+35), A in 84% and C+sub in 63%.
- **Tokens:** C uses less than v2 in 98% of members and less than v3.4 in all of them. C+sub uses less than v2 in
  77%.

Pull structure, today's quotas: v2 61, v3.4 46.5, A 18.4, AB_build 34.4, **C 33.5**, C+sub 40.8 sound closes/day.
C beats v3.4 in 10% of members. Sound per G tokens: v2 210, v3.4 153, A 209, **C 178**. The ordering is the same as
park. With quotas unlimited the Ralph rows hardly move, because they never reach the quota. v2 rises to 54.5
(park) and 63.2 (pull), and v3.4 to 53.7 and 61.2, so the gap widens.

### 6.2 The four-agent version (C) in detail

- **The runners:** 29% [17/38] of live tests run on Archmagi and the rest on SteveDesktop. The owner's returns
  bump 21 [6/35] tests a week. 45 [8/100] runs a week are void and re-run. Runner A spends 5.9 [1.2/11.5] hours a
  week on cold loads. The selftest's independent clock found 0 starts inside the owner's time or his 20-minute
  window.
- **The test queue** ends week 4 with a median of 2.7 candidates waiting, but 154 at p90. In about one member in
  ten, two runners cannot keep up with two builders, and the testing becomes the bottleneck.
- **Parked items:** the median is 0 a week; a few members park one.
- **Two builders roughly double one.** C closes about 1.8× A's sound work. Splitting by area keeps collisions low,
  but the tornado (section 7.2) shows the gain depends on `r_dur_mult` as much as on the split.
- **Subagents (C+sub)** add another 3.6 closes/day for 0.4G more tokens a week, so sound per token falls from 180
  to 160. Whether `r_par` is 1.2 or 2.5 is unknown.

### 6.3 Quality and the owner (lower trust)

| metric | v2 | v3.4 | A | AB_test | AB_build | **C** |
|---|---|---|---|---|---|---|
| escapes/week | 281 | 210 | 90 | 71 | 155 | **137** |
| escape share (escapes / (escapes + sound closes)) | 0.45 | 0.44 | 0.43 | 0.39 | 0.42 | **0.39** |
| runner-accepted product/day | 0 | 58 (v3 Arbiter) | 0 | 17.3 | 0 | **33.4** |
| owner messages/day | 28.2 | 19.1 | 20.3 | 20.2 | 20.7 | **22.0** [12/33] |
| of which steers of a spiralling loop | - | - | 0.33 | 0.33 | 0.62 | 0.57 |
| owner minutes/week (as charged by the model) | 2064 | 2135 | 1903 | 1903 | 1930 | **1968** |
| owner cards waiting > 3 days | 5.8 | 8.8 | 3.1 | 3.0 | 3.4 | **3.3** |

How to read it:

- **Escape share** is escapes over escapes plus sound closes. Without matching cohorts and units it should not be
  read as "the fraction of defective tickets" (GPT). It falls in AB_test and C because a runner tests the item.
- **Owner messages mostly restate an assumption.** C's message count is v2's status rate times `r_status_mult`,
  plus steers and bumps. Against v3.4, C sends +2.8 a day (higher in 60% of members).
- **Owner minutes are partial.** The model charges fixed minutes per event (2 per new request, 1 per ping, 3 per
  card answered, 4 per steer, 2 per bump). Most of the roughly 2,000 a week are his own new requests, which are the
  same in every variant. It does NOT charge reading, reviewing, prompt tuning, repairing a stuck loop, or
  supervising. Those are exactly the costs Ralph shifts onto the owner. So C's 96 fewer minutes a week than v2
  is not a saving to bank; the costs left out could be larger.
- **"No blocked hours" does not mean no waiting.** A loop that never blocks can still fail pass after pass, spiral,
  or leave items waiting on a test queue (C's p90 above).

## 7. How reliable are these predictions?

### 7.1 Where each parameter comes from

The owner asked whether the model uses bug likelihood, fix length and other parameters measured from the past.
Some it does; most of what decides the Ralph answer it does not. The labels:

- **CALIBRATED:** measured directly from our own records, with the window stated.
- **ABC:** a prior range kept only where the v2/v3 model reproduced 7 days of observed counts. The spread figure
  is the kept p10-p90 width as a share of the prior range. A uniform prior gives 0.8, so a figure near 0.8 means
  the data did not narrow it at all.
- **CONFIG:** a setting, not a guess.
- **ASSUMED:** a range I chose; nothing measured narrows it.

| what the owner means | model parameter | label | source and spread |
|---|---|---|---|
| bug likelihood, product work | `mu_prod` (defects per product ticket) | ABC | spread 0.70: barely constrained |
| bug likelihood, process work | `mu_proc` | ABC | 0.85: not constrained |
| bug likelihood under Ralph | × `r_mu_mult` 0.8-1.6 | ASSUMED | no Ralph data |
| fix length (wall time) | helper duration quantiles | CALIBRATED | spend census, 1,271 helpers, 7 days |
| fix length under Ralph | × `r_dur_mult` 0.7-1.5 (and `r_par` for +sub) | ASSUMED | |
| fix cost (tokens) | helper ITE quantiles; seat ITE per close; background 146.8M/week | CALIBRATED | spend census, 7 days |
| fix cost under Ralph | `r_ite_mult`, `r_ctx_ite`, `r_quick_ite`, `b_test_ite` | ASSUMED | |
| a repair actually fixes it | `p_fix` | ABC | 0.83: not constrained |
| rework attempts | the cap of 3 | CONFIG | |
| verify catches a defect | `p_verify` 0.66 (v2 verify) | CALIBRATED | 615 of 928 runs, 7 days |
| live-test catch rate | `s_rig` × `b_s_mult`, plus `b_blind` | ABC × ASSUMED | `s_rig` spread 0.43: moderately constrained, p50 0.285 |
| invisible to every check | `b_shared` | ABC | |
| live test length | `b_test_min` 10-45 min | ASSUMED | |
| void test runs | `c_invalid` 0-0.3 | ASSUMED | |
| cold load | `c_cold_min` 0.5-25 min | ASSUMED, endpoints measured | 22 s minimal list, ~25 min full list |
| when the owner is present | presence by hour | CALIBRATED | 23 days, 1,638 owner messages |
| how fast he notices a stall | `notice_min` | ABC | 0.84: not constrained |
| how fast he answers a card | `q_card` | ABC | 0.13: well constrained |
| how much he asks for | `lam_ext_h`, `lam_status_h` | ABC | 0.29 and 0.25: well constrained |
| status questions under Ralph | × `r_status_mult` 0.3-1.2 | ASSUMED | |
| idle rule | 20 minutes | CONFIG | |
| loops off track, spirals | `r_p_off`, `r_p_spiral`, `r_unstick_h` | ASSUMED | |

So: the owner's appetite, presence and card speed are measured, and so are v2's helper durations and token costs.
The defect rates and the repair rate are hardly narrowed by the data. Everything that makes Ralph different from
v2 is assumed.

### 7.2 What moves the headline numbers (tornado)

Method: over the 240 park members, for each parameter, the mean result in the members with the top tenth of that
parameter minus the mean in the bottom tenth, with the Spearman rank correlation. Both the members' world
parameters (t) and the Ralph parameters (r) are included. With 24 members per tenth the swings are noisy; a
|rho| below about 0.13 is indistinguishable from zero.

| result (median) | top drivers: swing (rho) |
|---|---|
| C sound closes/day (30.9) | mu_prod t −25 (−.74); p_prod_ext t +16; mu_proc t +16; p_link t +15; p_fix t +14; r_dur_mult r −13; init_queue t +13 |
| C minus v2, sound closes/day (−18.3) | mu_prod t +15 (.54); s_rig t −10 (−.33); r_dur_mult r −10 (−.43); quick_min t −9; mu_proc t −9 (−.46); p_fix t −8; b_shared t −8 |
| C sound closes per G tokens (180) | mu_prod t −151 (−.66); p_fix t +87 (.15); mu_proc t +86 (.46); p_link t +77 (.32); p_prod_ext t +73 (.41); r_ite_mult r −70 (−.42); r_mu_mult r −69 (−.31) |
| C tokens/week (1.23G) | r_ite_mult r +0.48G (.64); r_dur_mult r −0.47G (−.49); r_mu_mult r +0.24G; p_quick t −0.24G; c_a_present_ok r +0.23G; b_test_ite r +0.21G |
| C owner messages/day (22.0) | r_status_mult r +24 (.95); nothing else above ±8 |

In pull, the top drivers of C's sound closes are r_dur_mult (−20), mu_prod (−18), p_owner_card (+15), p_prod_ext
(+14) and f_proc (−14).

One at a time, from all-midpoints (12 members; C sound closes mid 28.9/day): r_dur_mult +5.1/−5.0; r_mu_mult
+2.7/−4.9; r_p_off +1.7/−2.8; b_test_min −0.1/−3.8; r_bp −2.3/+1.2. Owner messages: r_status_mult ±11.2, then
c_bump_msg ±1.5.

**The top five sensitivities, for the comparison that matters (C against v2):**

1. **`mu_prod`, defects per product ticket** (ABC, barely constrained). More defects narrow the gap, probably
   because C's runners catch defects before close and v2 pays for them later as rework.
2. **`s_rig`, the live-test catch rate** (ABC, moderate). A better rig widens the gap: on balance it helps v2's
   verify step more than C's runners.
3. **`r_dur_mult`, how long one Ralph context takes to do a ticket** (ASSUMED). This is the biggest Ralph-specific
   lever, and the one the trial measures first.
4. **`quick_min`, seat minutes per bookkeeping close** (ABC, barely constrained). It decides how much of v2's
   count is cheap closes.
5. **`mu_proc`, defects per process ticket** (ABC, not constrained).

For C's tokens, the ASSUMED `r_ite_mult` and `r_dur_mult` lead. For owner messages, the ASSUMED `r_status_mult`
is the whole answer.

**The plain reading:** the absolute numbers swing mostly on defect rates that the past data do not pin down. The
gap to v2 swings on those and on one Ralph assumption (`r_dur_mult`) about equally.

### 7.3 What the failed 10-27 backtest implies, and how many days of measurement would settle it

The 2026-10-27 backtest failed on ticket counts. Over three v2 weeks, helpers per close went 5.2 → 3.3 → 1.5 while
the work stayed level, because the meaning of a ticket changed as the ledger was adopted (4% → 34% → 62% of
work). Ticket-count predictions missed by about 3×. Work, token and verify-fail metrics passed; owner wait
failed. For this comparison that means:

| metric | trust | why |
|---|---|---|
| tokens/week | medium, within the model | tokens passed the backtest; Ralph's draws are paired with v2's and scaled by an assumed range. It measures a week's spend, NOT the tokens to finish a fixed backlog (GPT): Ralph spends less partly because it does less |
| sound closes per G tokens | **low-medium, internal only** | a ratio cancels some of the unit problem but still counts closes. Splitting one task into ten tickets changes it without changing useful work (GPT) |
| blocked hours, process share | medium | structural |
| sound closes/day, all closes, backlog | **low** | the unit failed the backtest. Read them as relative capacity in this model, not as items per day |
| escapes, escape share | low | they ride on ticket counts and on `r_mu_mult` |
| owner messages/day | **low: one assumption** | rho 0.95 on `r_status_mult` |
| owner minutes, cards waiting | low | owner wait failed the backtest, and the minutes leave out supervision |

**How many days would settle it.** The model will not get better by being refined. Three kinds of measurement
would replace the assumptions:

- **A day: the screen.** The section 8 trial (8-12 matched tasks in one working day, with a 48-72 hour retest).
  It can show whether the predicted gap exists at all: one loop at about half of v3.4's capacity per day, and
  the four-agent version at about three quarters. It cannot estimate rare defects.
- **7 days: the throughput assumptions.** Seven days is the window the current model was calibrated on. One Ralph
  loop on one mod runs about 50 passes a day, so about 350 in a week. That is enough to measure `r_dur_mult`, the
  off-track rate and tokens per pass to within a few percent. At about 20 a day, status messages would be counted
  to about ±10%.
- **14 days: quality.** Escapes surface days after a close, so defect rates need 14 days, the second week to let
  the first week's escapes appear.

All three must count **accepted outcomes against criteria written before the work** (completed requirements, not
closes). Otherwise the measurement repeats the backtest's failure.

## 8. Recommended experiment: a controlled trial (GPT's, adopted)

This replaces the first draft's "run AB_test for a week beside v3".

1. **Choose 8-12 small real tasks** and group them into roughly matched pairs. Write the acceptance criteria and
   the proof command for each task BEFORE assigning it.
2. **Assign at random.** Flip a coin within each pair: one task goes to Ralph A, the other to v3 **as it actually
   runs today**, not as designed.
3. **Make it equal.** The same model where feasible, a small equal token allowance and a one-working-day limit.
   Each system gets exclusive source scope (different mods) and its own deployment target, because a separate clone
   does not isolate them (section 2).
4. **Exercise the failure paths on purpose.** Watch the first few Ralph passes. Plant one failing check and kill
   one pass mid-run. This shows that unchecked work is not published and that the next pass recovers (section 1.2).
5. **Judge both arms the same way.** One independent acceptance check, run identically on both arms. Count
   completed requirements, not commits or tickets.
6. **Record everything:** total tokens, elapsed time, **owner minutes** (including reading, tuning and fixing),
   interventions, failures, unfinished work, repairs and accepted outcomes. Retest at 48-72 hours, and keep
   watching for defects for a week.
7. **Then SteveDesktop.** Give it a handful of fixed candidate SHAs to test. Measure the defects it finds beyond
   A's checks, false failures, void runs, elapsed time, tokens and owner effort. B's fail rate alone cannot give
   A's defect rate, because it also depends on test sensitivity and on whether the environment was valid.

Only if B earns its keep is variant C worth building, and only after the Archmagi runner's cost to the owner's
next session (section 3.2) is measured.

## 9. What GPT's check changed

GPT reviewed the first draft (`gpt_check\review.md`). Changes made:

- The loop checks the agent's exit status, runs the post-change gate AFTER the agent, and publishes only on pass.
  A failed candidate goes to the next fresh pass, and it is parked after 3 tries (section 1.2).
- Supervision, flock, bridge release, the working-directory check and control files outside git are added.
- Owner policy is in `POLICY.md`, apart from the notes the loop learns (`AGENTS.md`).
- B tests fixed SHAs, writes only results, and has a "test invalid" verdict (section 2).
- Parallel subagents inside a pass are a sweep option (`+sub`).
- Nothing depends on the prompt's word count.
- The `id()` determinism bug that made `b_collide` appear to move AB_test is fixed; outputs are fingerprinted;
  required tests are enforced; the final backlog, owner minutes and per-member ratios are reported.
- The controlled trial (section 8) is the recommended next step.

**First-draft conclusions that do not survive**, kept here so nobody quotes them:

| first draft said | why it does not survive |
|---|---|
| Ralph does "about a third of v2's work" | true only of this serial model under its assumptions; with subagents or two builders the ratio is 0.5-0.7, and no Ralph has been measured |
| sound work per token is "about the same as v2" | internal to the model; it still counts closes, the unit that failed the backtest |
| Ralph sends fewer owner messages | it restates the `r_status_mult` assumption and leaves out supervision time |
| "no blocked hours" | does not mean no waiting: passes fail, loops spiral, tests queue |
| "product backlog at week 4" 136 / 274 / 402 | mislabelled: it was the mean of weekly ends. The true end-of-week-4 values are 232 / 357 / 558 |
| defect fraction v2 0.43, v3.4 0.35-0.40 | wrong numbers (the v3.4 range came from the unlimited-quota run). Park/today is 0.45 and 0.44, and it is an escape share, not a defect fraction |
| "0% / 14% / 52% / 100% of members" as odds | they are shares of this ensemble, not probabilities that a real system wins |
| a separate clone "cannot collide" with the seats | false: same remote, same game folders, same bridge |
| Ralph's losses on F5, F15, F18, F26 | v3 never delivered those either; they are losses against a design, not against what runs |
| AB_test sound per G 177; `b_collide` moves AB_test | the `id()` bug; corrected to 170, and `b_collide` no longer affects AB_test |

What survives, in GPT's words: "fresh contexts and fewer coordinating components are real architectural
differences; serial execution trades capacity for lower weekly consumption; and a separate test worker can add
evidence."

## 10. Verdict

- **Capacity (low trust):** in this model, one serial loop closes about a third of v2's sound work. Two builders
  with two runners (C) close about two thirds, and C+sub about 70%. All of them spend less per week. None beats v2
  on closes in any meaningful share of members. C beats v3.4 in about 1 member in 10.
- **Efficiency (low-medium trust, internal):** sound closes per token for C sit between v3.4's (beaten in 78% of
  members) and v2's (beaten in 42%). This does not show that Ralph would finish a fixed backlog for fewer tokens.
- **Simplicity (high trust; structural, not simulated):** WIP 1 per loop, a fresh context every pass, no wake
  path to fail, a gate the agent cannot skip, and one small config. Four inventory functions v3 never delivered
  come for free.
- **What it costs (high trust; structural):** no independent judging of finished work, no live conversation, a
  findings store reduced to one list, and owner supervision that the model does not charge.
- **Four agents (C):** the runner on Archmagi works within the 20-minute rule, and the sim confirms it never starts
  inside it. It is bumped about 3 times a day and pays nearly an hour a day in cold loads. Its cost to the owner's
  next session is not modelled. In about 1 member in 10, the test queue becomes the bottleneck.
- **What to do:** run the section 8 trial before building any variant. It costs one working day plus a retest, and
  it replaces `r_dur_mult`, `r_mu_mult` and `r_status_mult`, the three assumptions the answer rests on, with
  measurements.

Reproduce (outputs in `D:\ClaudeWork\rimmandrake\ralph_sim\`: `results.json`, `tables.md`, `ens_*.jsonl`,
`oat_park.jsonl`; model fingerprint `0986bbc0091d`):

```
python3 src/RimMandrake/Utils/sim/ralph_loop_sim.py --structure park ensemble --quota today
python3 src/RimMandrake/Utils/sim/ralph_loop_sim.py --structure park ensemble --quota unlimited
python3 src/RimMandrake/Utils/sim/ralph_loop_sim.py --structure pull ensemble --quota today
python3 src/RimMandrake/Utils/sim/ralph_loop_sim.py --structure pull ensemble --quota unlimited
python3 src/RimMandrake/Utils/sim/ralph_loop_sim.py --structure park oat --members 12
python3 src/RimMandrake/Utils/sim/ralph_loop_sim.py report
python3 src/RimMandrake/Utils/sim/selftest_ralph_loop_sim.py
```
