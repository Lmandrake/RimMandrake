# Agent_Policy — which model does which work

**Binds the Conductor and every helper it launches.** Read it with `CHARTER.md`. `Agent_Policy.md` is the ONLY file that says
which model does what *for this repo's seats*. Every other doc in RimMandrake points here. The routing axis (the one
question below: if this goes wrong, who catches it?) is measured, not argued.

🔴 **FOR WHAT THE FLEET CAN ACTUALLY REACH, ASK `~/dev/Dispatch/bin/delegate`.**

- A census on 2026-10-01 found six files across `~/dev` that restated a model ladder in prose. Three of them named a
  model that the gateway does not serve.
- `bin/delegate where` reports reachability. `bin/delegate route <kind>` picks a destination from published figures.
- A `PreToolUse` hook on `Agent|Task` now refuses an unservable model at the spawn. Before the hook, such a spawn
  failed with a 400 afterwards.
- **What stays here is the SEAT policy**: which of this repo's jobs is design and which is grind. That policy is a
  judgement about RimMandrake, not a fact about the gateway.
- A claim in this file about model *availability* is subordinate to `bin/delegate`, which measures it.

## 🔴 The seat models — fleet ladder updated by the owner, 2026-10-20

> `fable` for the Conductor's window and for single-agent whole-mod or blank-page design work under a
> hard budget; `opus` for bounded tickets, complex code generation and judging; `sonnet` for
> everything else with a checkable outcome. **Sonnet is the lowest rung; no Haiku** (owner,
> 2026-10-31). Fable is on the ladder from 2026-11-12 (owner: "It only said no fable because Opus 5.5
> was outperforming Fable 5.1."). Never Fable for fan-out helpers, reruns, fleets, unvetted tickets,
> game-waiting or fast mode. A Fable helper is allowed for design work or for an extremely difficult problem (owner
> 2026-11-26, the Fable row below). Pass `model` on every spawn. Read the environment
> (`ANTHROPIC_DEFAULT_*_MODEL`) before trusting a rung; name no account. Ladder source of truth:
> `~/dev/Lodestar/claude/global/45-subagents.md`.

The rule "never Fable for game-waiting" has one exception. The Test Pilot runs on Fable 5.2 (owner 2026-11-16; the
Fable row below).

Lodestar's file holds the ladder of the whole fleet. This file is the only home of that ladder's application in this
repo: which of this repo's jobs goes to which rung.

The Conductor window runs on Fable 5.2 and orchestrates. The headless quick checks of the Conductor role run on Opus
(`model` in `src/RimMandrake/rimflow/dispatcher_schedule.json`).

- The Conductor does not do design in-window, and it does not grind.
- The Conductor holds the owner's attention. The Conductor backgrounds design to an **Opus** helper, or to a **Fable** helper
  (owner 2026-11-26, the Fable row below), and keeps the conclusion.
  Design of a whole mod from a blank page goes to a detached Fable run (`detached_helper.py --model fable`), one run
  that owns the whole design, never an `rm-*` helper.
- Each item is classified by the rule below. Opus-class items go to an `rm-builder` (Opus) subagent.
- When `rimflow next` routes an item to a Test Pilot, the item goes to an `rm-testpilot` subagent instead (owner
  2026-10-31). `rm-testpilot` runs on Fable 5.2 (owner 2026-11-16).

## The one question

Tier does **not** follow how hard the task looks. It follows:

> ## 🔑 If this goes wrong, WHO CATCHES IT?

Our register of failures is not bad code. Our failures are **plausible answers nobody disbelieved**:

- seven instruments returning confident wrong counts in one session;
- ~40 bridge calls reporting success and changing nothing;
- an `<li>` discarding a whole def and costing 26 biomes.

Cheap models are safe exactly where failure is loud, and dangerous exactly where it is silent.

| Who catches a wrong answer | Use |
|---|---|
| It is an **OS-level search** (grep, glob, file inventory) whose result is re-checked | **sonnet** |
| A **compiler, selftest, validator or hook**, before anyone reads it | **sonnet** |
| **Another agent**, who will re-derive it before acting | **sonnet** |
| **Nobody** — it becomes a recorded fact other work cites | **opus** |
| **Only taste** — art, the world, prose he reads | **opus** judge agent (not the maker), then his curated review — `design/RimMandrake/delegation_policy.md`. The naive pre-review of anything shown to him is this row (`standing_rulings.md` §Nothing reaches the owner unread) |

⛔ If you cannot name the catcher, you are on the **Nobody** row (opus). "It'll be obvious" is not a catcher.

## The ladder

| | Alias | For |
|---|---|---|
| **Fable 5.2** | `fable` | **The Conductor's window.** One agent finishing a whole mod against its checklist. Design from a blank page. One escalation attempt, at high effort, on a clean ticket that Opus failed at xhigh (the stuck-worker ladder below). Every run has a hard dollar budget, enforced from outside by `spend_watchdog.py`. Never use `--max-budget-usd`, and no agent is told its spend (owner 2026-11-16). A helper only for design work or for an extremely difficult problem (owner, 2026-11-26: "Fable absolutely can be a helper for Design purposes or extremely difficult problems."). Never a rerun, a fleet worker or a game-waiter. **Exception, the Test Pilot (`rm-testpilot`): Fable 5.2,** although a sitting waits on a live game. Owner, 2026-11-16 10:13 PM PST: "Test Pilot should also run as Fable 5.2 when it's called. For obvious reasons." Do not move the Test Pilot back to Opus under the game-waiter rule. Price: 2× Opus fresh, 1× cached. |
| **Opus 5.5** (+fast mode) | `opus` | **Design** that is not a blank page, always as a backgrounded subagent from the Conductor: design judgment, decision drafting, synthesis across contradictory evidence, rosters, specs, skill curation. **Complex code generation**: Harmony/C#, new systems, multi-file forensics, bridge writes, the frozen world. |
| **Sonnet 5.5** | `sonnet` | **Well-defined coding with a checkable outcome**: patches, defs, deploys, quicktests, fixes that a selftest or validator proves. Log triage, interpretive sweeps, first drafts. **OS-level searches**: greps, globs, censuses, existence checks, inventories (folded in 2026-10-01 when Haiku was struck from the ladder). The default for helpers that build. |

### 🔴 Effort: the floor is high; a stuck worker climbs effort, then model — owner by card, 2026-11-25

Owner, by card: "No medium anywhere"; a stuck worker: "Effort up, then model up"; a Fable run on stuck work: "High".
Page: `design/specs/2026-11-25-effort-ladder/boundary.md`.

- **Every launch states its effort.** The level comes from the one table, `EFFORT` in `src/RimMandrake/rimflow/effort.py`.
  Every model reads high. No run of ours uses low or medium. `effort.py` refuses a level under high.
- A launch passes `EF.effort_args(model)`. `detached_helper.py launch --effort xhigh` sets a run's level, and the run
  record keeps it. `claude_bounded.sh` adds the table's level when its caller gave none.
- `launch_permissions.py effort` reads every launch in the tree. The reader is red on a launch with no `--effort`. The
  remote-control server takes no `--effort`; its sessions read the machine's settings file (`effortLevel`).
- **A worker is stuck** in two cases. Case one: the worker filed a ticket to set its work down (`rimflow file --not-now`), the ticket filer
  (`filing_gate.py`) refused that filing, and the run ended without resolving the refusal (`refused_why`). Case two: the run ends success with its item open and a
  `LEFT OPEN:` note that says its test is still red, or that names no cause outside the work (`stuck_why`). A cause
  outside the work is the owner or the Conductor, a held or paused game, lane or account, a wait, another run, or a task
  that is not a helper's. `left_open_continue.py` reads both cases.
- **The ladder** (`left_open_continue.ladder_step`):
  1. Same model, same session, one level up: high to xhigh. The resume keeps the prompt cache while the cache lives
     (1 hour). The ladder stops at xhigh: max effort rarely pays.
  2. At xhigh, the next model starts FRESH at high, from the worker's PROGRESS: notes: Sonnet to Opus, Opus to Fable
     5.2. A model change writes the whole context again, so a fresh start is cheaper than a resume.
  3. A stuck Fable run launches nothing. A `RAISE FIRST` line goes to the Conductor log, with the note. Nothing files a
     ticket before this step.
- A ladder step is a continuation (`continued_from`). A ladder step spends no counted run of a mod stage and no slot of
  `MAX_PER_DAY`. A ladder step writes no failed run on the ticket. The ladder's end guards the danger of a run that climbs without
  end on a fault that needs the owner.

### 🔴 Sonnet vs Opus — owner ruling, 2026-10-29 (replaces "Sonnet default, self-escalate after one failed attempt")

> "Sonnet for building code that can easily be checked right via tests and output. Opus for code
> that is challenging to validate directly, has no valid tests for much of its function, or
> knowledge work where quality is subjective."

The test is whether a test or output can say the work is right. The test is not how hard the work feels.

- **Opus:** C#/Harmony behaviour with no selftest; concurrency and restart code (seat restarts, leases, locks);
  orchestration and dispatcher logic (`rimflow`, `dispatcher_schedule`); design; art judgment; specs, rosters,
  taxonomies; triage or verification judgment with nobody to catch it.
- **Sonnet:** XML defs and patches that `validate_patch` checks; fixes that a selftest proves; deploys; quicktests;
  greps, censuses and searches.
- **Unsure: Opus.** Put `model: opus` on the spawn. Escalate the model, never the ceremony: keep the
  same short leash. That is, a hard problem gets a smarter model on the same short brief, not more spec sections.

External free workers (nemotron) do candidate narrowing only. They never give conclusions and never write. See
`research/FANOUT_WORKER_EVALUATION.md`.

## Helpers in this repo

The method is the `efficient-subagents` skill (and `agent-fanout-research` for a fan). This section adds what is true
here.

- **Spawn only the `rm-*` definitions** (`.claude/agents/`, enforced by `.claude/hooks/block_unbounded_agent.py`):

  | type | use | model |
  |---|---|---|
  | `rm-fixer` | well-defined fix a selftest/validator proves | sonnet |
  | `rm-builder` | complex code or design, one item | opus |
  | `rm-bridge` | live-game section run by script | opus |
  | `rm-judge` | art/taste judging of work it did not make | opus |
  | `rm-testpilot` | one live sitting on one item (`rimflow pilot`) | fable (the exception in the Fable row) |

- **Unattended runs: the spawn hook holds the limit** (`.claude/hooks/block_agent_over_slots.py`). The numbers are in
  `src/RimMandrake/Utils/slot_rules.json`.
- **The Conductor window has no helper limit only for work started within 20 min of the owner's last typed message.**
  After that, the limit is two helpers, and a helper that runs over an hour raises an alarm. Detached runs are not counted
  (`roles/conductor.md` §Session mode). Owner, 2026-10-29: "...only for work
  started within 20 mins of the last time the user typed to conductor. After that it should relax to two subagents
  only." To measure helper use, run `python3 src/RimMandrake/Utils/token_census.py --since <UTC>`.
- **Worktrees are OFF:** never pass `isolation: "worktree"` (`block_worktrees.py` refuses it).
  - A writing helper edits in the window's own clone. The window commits the helper's paths with `./publish`.
  - A helper that needs its own clone gets `python3 src/RimMandrake/Utils/scratch_clone.py clone "<purpose>" --fetch
    --sparse <the dirs it will touch>`. Never use `--checkout`, which takes the whole ~4 GB tree.
- **Cutting claims from a doc:** use the two-blind-arms method in `efficient-subagents`.
  `src/RimMandrake/Utils/doc_claims.py` numbers the claims.
- **Cheap read-only fan-out:** `src/RimMandrake/Utils/nemotron_fanout.py` and `nemotron_ceiling.py`. The measured
  pool, its ranking and the abstention clause are in `research/FANOUT_WORKER_EVALUATION.md`.
- **One live-game lane for each game.**
  - Several helper lanes that need the same running game starve one another. One lane waited 45 minutes and tested
    nothing. So run at most one lane on each game, and batch the live checks.
  - The holder of a game is a process. The hold lasts while that process lives (`CLAUDE.md` §The bridge is passed through
    one file).
- **Split art redraws one agent per subject.** An art-regeneration agent works one picture at a time. Eight redraws
  took ~20 min in one agent. So launch the redraws in parallel, one agent per subject.
- **`infrastructure/state/code_review/<SEAT>.jsonl` is one shared file per seat, and parallel helpers collide on it.**
  - Helper A's mark-clean lines sit uncommitted beside helper B's lines in the same file.
  - The commit hook forces a pathspec commit, which takes the whole working-tree file. So neither helper can commit
    its own marks without sweeping in the other helper's marks.
  - Staging a HEAD-plus-your-lines blob with `update-index` is refused too, because a pathspec-less commit is refused.
  - So commit mark-clean lines in the same Bash turn as the mark. Or let the last helper of the wave (or the parent)
    commit the shard once all helpers are done.
  - Open fix: one shard per helper, or a `code_review_status.py` verb that commits only the caller's tagged records.
- **Grep memory before relaying a fact about factions, biomes or rulings to the owner.** A subagent's unverified fact
  reached the owner wrong (a DLC's empire named as the wrong faction). A memory file held the right answer.
- **Debugging is script-first (`design/RimMandrake/debug_process.md`).** A live poke can end without its lesson
  committed as a check (plus the informative false theories). Then nothing keeps the work of the poke. The `ns_probe_*` scratch
  files vanished and survived only in commit messages.
- **The Conductor stays conversational.**
  - Never block the owner's window on long foreground waits (sleep/until loops, multi-minute checks).
  - Never chain hidden steps.
  - Push waits to background, and answer him in plain words first.
  - Owner: "Conductor is supposed to be someone I can easily chat with about how it's going... Almost the opposite of
    the design intention" and "This procedure is opaque. What are you even doing?"
- **Before drafting from an item's text, check it against later rulings.**
  - A brief can carry a mechanism that a later owner ruling voided. Example: TWILIGHT_BOTTOM_CAST_1 (the Deepwater
    bottom cast) still named 'lease practice' after "The Compact does NOT sell light... Remove." (owner).
  - Grep the item's design dir for an existing draft. Read the 'Ruled' headers of the later sibling passes first.
- **Say what happened and how you know in the first clause of a status line.** 'No longer in the running list' reads
  as lost or dropped to the owner. In that case, the trial run `v3` (one arm of a comparison of orchestrators) had
  simply finished.
- **More than ~10 concurrent helpers closes the fewest items per token.**
  - Burn days (days of high spend) with 10-22 helpers spent 99.5M cache-read tokens per closed item (30 closes).
  - The framework-guided day (the day after a weekly reset, run by the rules of
    `design/RimMandrake/work_allocation_framework_2026-10-26.md`) at 4-7 concurrent spent 5.2M per closed item. ALMOST_OUT (the "nearly out, only vital
    work" operating mode, `design/RimMandrake/operating_modes_2026-10-26.md`) spent 11.2M per closed item.
  - Spend surplus tokens on durable no-review work (harnesses, instruments, wiring). Do not spend them on more
    parallel helpers or review waves.
- **Delegation did not stop the owner's card load.**
  - After `delegation_policy.md`, he still answered 207 card questions in 4.1 days (~50/day vs ~76/day before).
  - 144 of them were in classes already delegated (design 57, process 58, art picks 29).
  - In those classes, his agreement with the agent's Recommended option was only 50-61%. So most were real choices.
  - Ordering/helper-count cards (81% agree) and twin-apply cards (86%) are pure leak: cards that reach him although
    the call is already delegated and he nearly always agrees with the recommendation.
  - On his own sheet marks, agents' 'wait/keep' recommendations matched him 39%. A 'newest mark wins, x acts now' rule
    predicts 83%.
- **No subagent type can reach Artifact/ArtifactData.** rm-fixer lacks ToolSearch. rm-builder's ToolSearch finds
  neither tool. general-purpose is hook-blocked.
  - A helper gathers the data into a file. The write goes through a headless `claude -p` with `CLAUDE_CODE_ARTIFACT=1`
    (`src/RimMandrake/Utils/fleet_refresh.py`).
  - A helper type needs `SendMessage` in its tools list to report mid-run. rm-builder, rm-fixer and rm-bridge now
    have `SendMessage`.
  - A brief must not tell a running helper to message anyone unless its type has the tool.
- **`code_review_status.py list` (bare) lists only the files with a review record; `--show-untracked` adds the files
  with none.**
  - A loop run without `--show-untracked` reported "0 DIRTY" for 43 waves while 346 files were invisible.
  - Neither list is the CLEAN set. Since 2026-11-19, `code_review_status.py check` measures CLEAN against the boundary
    pages, and `list` shows only whether a review round was recorded on today's bytes.

## Subagents — this is where the saving is

🔴 **Every `Agent` call takes `model`. Pass it, every time.** `block_agent_without_model.py` refuses a call without it.
The hook also blocks a named agent type, such as `Explore`, called without an explicit `model`. The hook text exempts
named types, but the hook blocks them.

| Job | Model |
|---|---|
| OS-level search: grep, glob, inventory, "does X exist", fixed-shape census; extraction/classification with a checkable result | **sonnet** |
| Well-defined coding a compiler, selftest or validator will check | **sonnet** |
| Sweep where the agent must interpret or classify | **sonnet** |
| Fan-out whose returns will contradict; adversarial refutation | **sonnet** |
| **Design** — a spec, a roster, a taxonomy, anything the owner reads as design | **opus**, backgrounded, or a **fable** helper (owner 2026-11-26); a whole mod's design from a blank page: a detached **fable** run |
| **Complex code generation** — a new system, Harmony/C#, cross-file changes with no test to catch them | **opus** |
| Anything acted on **without re-deriving it** | **opus** — and ask why it is a subagent |

A subagent's return is EVIDENCE, never a finding. The return carries CONFIRMED/UNCERTAIN, and the window decides what
is true. Never spawn a duplicate for "reliability".

- **A subagent report ending `HANDOFF READY` is the agent's own artifact, not a handoff.** Only the seat's handoff
  ritual (`handoff.py --check`) licenses that line.
- Parallel helpers must not share one stage folder. `selftest_winstage` once staged every clone in one shared folder,
  so agents tested each other's source. The stage folder is now a per-clone hash.
- **Never run heavy ML from a subagent inside a seat.**
  - Model downloads, torch, ComfyUI, mesh generators and big numpy rasterizers inherit the seat's cgroup.
  - One 7 GB child pushed the 10 GB scope to its limit with swap full. The kernel killed the child, and the window died
    anyway. `OOMPolicy=continue` only stops systemd tearing the scope down.
  - Run such a job in its own bounded systemd scope, so that a balloon kills only itself.
  - Local generation is parked. Do not relaunch it without the owner's word.
- **A backgrounded `Agent` dies at 600 s of silence and leaves NOTHING on disk.**
  - One case left a clean tree, and a whole run was lost. The survivors had streamed output by 385 to 575 s.
  - Brief every writing subagent to create its output file as a skeleton FIRST, and to fill it section by section. A
    file write emits progress and persists partial work.
  - A long read-then-write brief is the shape that trips the 600 s limit.
  - For a **mechanical** census (glob, parse, count, tabulate), write the script inline. That costs less than a brief
    that survives the watchdog. Reserve subagents for work that needs judgement.

## Four places a cheaper tier is forbidden outright

1. **Deciding whether an instrument told the truth** (`BUILDABLE.md` exists because they lie).
2. **Live bridge writes** — the world is frozen and hand-authored, no regenerate behind it.
3. **The world, and art** — *"iterate by LOOKING"*; realism is not scoreable.
4. **Text the owner reads as a conclusion** — above all a number.
   ↳ 🔴 **One carve-out, owner ruling 2026-09-16: north-star `must read` verdicts.**
   Verbatim: *"Let a model YES green a line."*
   - A model can judge a mod's letter or flavour prose against a `must read` line. That model MAY return a pass. The
     pass greens the line; it is not routed to him.
   - The tier floor still applies (opus). `cannot read` lines stay absolute.
   - Rationale and the residual risk: `design/RimMandrake/north_star_validation_spec.md` §10.4. The rule that the
     carve-out replaced would have made any text-first mod permanently ungreenable unattended. An off-register letter
     is a bounded, recoverable failure.
   - **This carve-out is read-verdict-only.** A number, a count, or a finding he will act on still lands on the
     **Nobody** row and still comes to him.

## The escalation clause every cheap-worker prompt carries

> Escalate instead of guessing if: the criteria do not decide the case · the change
> reaches files outside the ones named · a measurement disagrees with the item · a
> tool returns success and you cannot see the effect · you would have to invent a
> defName, field or namespace.

The clauses "the criteria do not decide the case" and "the change reaches files outside the ones named" guard
against a worker that widens its task. A run fixes inside its own mod or subsystem. A run names in
its close each file that it changed outside the files that its brief named.

An escalation that names what you tried and what would settle the question is a success. An escalation in place of an
attempt is not. Record each escalation as a note on its item. Stamp the model on closes (`model=sonnet-5.5` in the `note`). Then the ledger can
answer the accepted-work rate per model.

## Hooks and Claude Code session quirks
- **A `PreToolUse` hook added to `.claude/settings.json` mid-session does not fire** until a new session starts. The new
  hook does not fire for this window's Bash calls, and not for its subagents' calls. A hook already present at session start does fire
  for subagents. Test a new hook in a fresh window, never by exercising it in the window that added it.
- **A Claude Code hook marked `asyncRewake` survives its session's kill.** The hook is re-parented to /init and would
  wait its full 23 h timeout (measured on Claude Code 2.1.308). Any long-waiting async hook must find its claude
  ancestor at start and exit when that pid dies (`doorbell.claude_ancestor` + `owner_pid` guard).
- **A Claude Code transcript (`~/.claude/projects/<cwd>/<session>.jsonl`) logs one line per content block of an API
  message, each repeating the SAME usage.**
  - Sum usage once per `message.id` (last line wins). Otherwise the sum overcounts a run 2-3x.
  - Deduped, the sum reproduces the `claude -p` result json exactly.
  - A role run's `--name` is not in the jsonl. Find the run by session id (pin with `--session-id`). Or find the run by the
    "role launch <unit>" text in the first user line (`role_launch.transcript_usage`).
- **The Claude Code `WorktreeCreate` hook's real stdin is `cwd, name, prompt_id, session_id, transcript_path`.** The
  docs say `base_path`/`worktree_name`, which is wrong. `WorktreeRemove` never fires (0 of 11 runs). The hook's parent
  pid is a dying `sh -c`. To find the session, walk `/proc` up to the `claude` process.
- **A PreToolUse Bash hook matches its trigger word anywhere in the command text, even inside a heredoc that only
  mentions it.** A refusal rejects the whole compound command, so its other steps do not run. We saw two cases:
  - The art-push hook acts while HEAD carries art events whose PNGs are not committed. Then the hook refuses any
    command that contains the repo's push-script word. This happens, for example, after a sibling helper swept your art-shard lines into its
    commit.
  - The registry-write hook refuses a heredoc patch that merely names the modcheck status file.
  - Keep the word out of the command. Write prose with Write/Edit. Put the patch in a scratch file, and run it.
- **Replaying hook payloads is not read-only.** An allowed `Agent` call makes `block_agent_over_slots.py` reserve a
  real helper slot for 90 s (`spawn_reservations.json`). Any tool that feeds hooks synthetic Agent calls must set
  `RM_SPAWN_RESERVE_S=0`, as `hook_latency.py` does.
- **`AskUserQuestion` is validated by `validate-question-card.py`.** Two faults refuse the **whole card**: a `header`
  longer than **12 characters**, or a question that does not end in `?`. Count the header before the call. (The
  `Agent` tool likewise refuses a call without an explicit `model`; see the ladder above.)
- **`claude -p --json-schema` takes the schema TEXT, not a file path** (`claude -p --help`). With `--output-format
  json`, the validated object is the top-level key `structured_output`. `result` also holds it as a string. A schema
  that uses `/pattern/` and `anyOf` is accepted.
- **Headless `claude -p` CAN use ArtifactData (measured).**
  - Set `CLAUDE_CODE_ARTIFACT=1`, and unset the inherited `CLAUDE_CODE_ENTRYPOINT=sdk-cli` (CLI gate
    `sdk_default_off`).
  - Keep the Artifact tool enabled. ArtifactData vanishes without it.
  - A parts write by `file_path` is a Read, so allow `Read(//<dir>/**)`.
  - To overwrite an existing doc, pass `if_version`.
  - `CLAUDE_CODE_DISABLE_CLAUDE_MDS=1` + `--disable-slash-commands` cut ~8k uncached tokens/run.
  - Working example: `src/RimMandrake/Utils/fleet_refresh.py`.
- **A `claude -p` loop launched with `--setting-sources project` or `--setting-sources ""` skips the user's effort
  setting and runs at medium with no warning.** So every launch passes `--effort` from the table (§Effort above). A
  running pass does not take a changed settings file; its next pass does.

## Hooks that route or refuse
- **A hook whose refusal text names a route must be tested against that route.** `block_shared_tree_merge.py` sent
  merges to a scratch clone. Then the hook refused the merges there, because it treated every clone as shared.
