# Agent_Policy — which model does which work

**Binds the Conductor and Relentless.** Read with `CHARTER.md`. This is the ONLY file that
says which model does what *for this repo's seats*; every other doc in RimMandrake
points here. The routing axis is measured, not argued.

🔴 **FOR WHAT THE FLEET CAN ACTUALLY REACH, ASK `~/dev/Dispatch/bin/delegate`.**
A census on 2026-10-01 found six files across `~/dev` restating a model ladder in prose,
three of them naming a model the gateway does not serve. `bin/delegate where` reports
reachability and `bin/delegate route <kind>` picks a destination from published figures;
a `PreToolUse` hook on `Agent|Task` now refuses an unservable model at the spawn instead
of letting it 400 afterwards. **What stays here is the SEAT policy** — which of this
repo's jobs is design and which is grind — because that is a judgement about RimMandrake
and not a fact about the gateway. Anything in this file that is a claim about model
*availability* is subordinate to `bin/delegate`, which measures it.

## 🔴 The seat models — fleet ladder updated by the owner, 2026-10-20

> `opus` for design work and complex code generation; `sonnet` for everything else, including
> mechanical bulk work with a checkable outcome (OS-level searches, greps, globs, inventories,
> file sweeps, extraction, classification, dedup pre-screens). **Sonnet is the lowest rung; no
> Haiku, no Fable.** Pass `model` on every spawn. Owner, 2026-10-31: "Please do not use Haiku for
> RimMandrake. Sonnet 5.5 is the lowest model to consider, due to Haiku's error rate. That is a
> project-wide setting." Read the environment (`ANTHROPIC_DEFAULT_*_MODEL`) before trusting a rung;
> name no account. Ladder source of truth: `~/dev/Lodestar/claude/global/45-subagents.md`.

`fable` is the name that genuinely 400s (the harness expands it to a literal id).

The Conductor runs on Opus 5.5 and orchestrates. It does not do design in-window and does not grind:
it holds the owner's attention, backgrounds design to an **Opus** subagent, and keeps the
conclusion. Relentless's workers (Sonnet 5.5) classify each item by the
rule below and hand Opus-class items to an `rm-builder` (Opus) subagent; an item `rimflow next` routes to a Test Pilot goes to an
`rm-testpilot` (Opus) subagent instead (owner 2026-10-31).

## The one question

Tier does **not** follow how hard the task looks. It follows:

> ## 🔑 If this goes wrong, WHO CATCHES IT?

Our register of failures is not bad code — it is **plausible answers nobody
disbelieved**: seven instruments returning confident wrong counts in one session;
~40 bridge calls reporting success and changing nothing; an `<li>` discarding a
whole def and costing 26 biomes. Cheap models are safe exactly where failure is
loud, and dangerous exactly where it is silent.

| Who catches a wrong answer | Use |
|---|---|
| It is an **OS-level search** (grep, glob, file inventory) whose result is re-checked | **sonnet** |
| A **compiler, selftest, validator or hook**, before anyone reads it | **sonnet** |
| **Another agent**, who will re-derive it before acting | **sonnet** |
| **Nobody** — it becomes a recorded fact other work cites | **opus** |
| **Only taste** — art, the world, prose he reads | **opus** judge agent (not the maker), then his curated review — `design/RimMandrake/delegation_policy.md`; the naive pre-review of anything shown to him is this row (`standing_rulings.md` §Nothing reaches the owner unread) |

⛔ If you cannot name the catcher, you are on row 3. "It'll be obvious" is not a catcher.

## The ladder

| | Alias | For |
|---|---|---|
| **Opus 5.5** (+fast mode) | `opus` | **Design** — design judgment, decision drafting, synthesis across contradictory evidence, rosters, specs, skill curation — always as a backgrounded subagent from the Conductor. **Complex code generation** — Harmony/C#, new systems, multi-file forensics, bridge writes, the frozen world. **the Conductor's window**, the orchestrator |
| **Sonnet 5.5** | `sonnet` | **Well-defined coding with a checkable outcome** — patches, defs, deploys, quicktests, fixes a selftest or validator proves. Log triage, interpretive sweeps, first drafts. **OS-level searches** — greps, globs, censuses, existence checks, inventories (folded in 2026-10-01; see below). FOUNDRY's default |

Fable is not on the ladder (owner, 2026-09-29). Pass `opus` or `sonnet`; read the environment
(`ANTHROPIC_DEFAULT_*_MODEL`) before trusting any alias.

### 🔴 Sonnet vs Opus — owner ruling, 2026-10-29 (replaces "Sonnet default, self-escalate after one failed attempt")

> "Sonnet for building code that can easily be checked right via tests and output. Opus for code
> that is challenging to validate directly, has no valid tests for much of its function, or
> knowledge work where quality is subjective."

The test is whether a test or output can say the work is right, not how hard it feels.

- **Opus:** C#/Harmony behaviour with no selftest; concurrency and restart code (seat restarts,
  leases, locks); orchestration and dispatcher logic (`rimflow`, `dispatcher_schedule`); design;
  art judgment; specs, rosters, taxonomies; triage or verification judgment with nobody to catch it.
- **Sonnet:** XML defs and patches that `validate_patch` checks; fixes a selftest proves; deploys;
  quicktests; greps, censuses and searches.
- **Unsure: Opus.** Put `model: opus` on the spawn. Escalate the model, never the ceremony: the same short leash.

External free workers (nemotron):
candidate narrowing only, never conclusions, never writing —
`research/FANOUT_WORKER_EVALUATION.md`.

## Helpers in this repo

The method is the `efficient-subagents` skill (and `agent-fanout-research` for a fan); this adds what's true here.

- **Spawn only the `rm-*` definitions** (`.claude/agents/`, enforced by `.claude/hooks/block_unbounded_agent.py`):

  | type | use | model |
  |---|---|---|
  | `rm-fixer` | well-defined fix a selftest/validator proves | sonnet |
  | `rm-builder` | complex code or design, one item | opus |
  | `rm-bridge` | live-game section run by script | opus |
  | `rm-judge` | art/taste judging of work it did not make | opus |

- **Unattended seats: at most 3 helpers per seat** (the allocator's limit). In the Conductor window there is no limit only for work started within
  20 min of the owner's last typed message; after that two helpers, and one running over an hour raises an alarm (owner: "...only for work started within
  20 mins of the last time the user typed to conductor. After that it should relax to two subagents only."). Measure:
  `python3 src/RimMandrake/Utils/token_census.py --since <UTC>`.
- **Worktrees are OFF:** never pass `isolation: "worktree"` (`block_worktrees.py` refuses it). A writing helper edits in the window's own clone and the window
  commits its paths with `./publish`. A helper that needs its own clone gets
  `python3 src/RimMandrake/Utils/scratch_clone.py clone "<purpose>" --fetch --sparse <the dirs it will touch>`, never `--checkout` (the whole ~4 GB tree).
- **Cutting claims from a doc:** the two-blind-arms method in `efficient-subagents`, with `src/RimMandrake/Utils/doc_claims.py` numbering the claims.
- **Cheap read-only fan-out:** `src/RimMandrake/Utils/nemotron_fanout.py` and `nemotron_ceiling.py`; the measured pool, its ranking and the abstention clause are in
  `research/FANOUT_WORKER_EVALUATION.md`.
- **One live-game lane at a time.** Several helper lanes that each need the running game starve one another (one lane waited 45 minutes and tested nothing): run at most one live-game lane, and batch the live checks. A bridge hold goes stale after 45 idle minutes and another window can then take the bridge, killing a helper's live session: keep the hold fresh with an event inside every 45 minutes during long helper runs.
- **Split art redraws one agent per subject.** An art-regeneration agent works one picture at a time (eight redraws took ~20 min in one agent); launch them in parallel, one agent per subject.
- **Briefs for helpers that edit a previously clean file say: 'mark-clean only after reading every line'.** Helpers tend to re-mark such a file clean after reading only their own hunks. The orchestrator checks each report for 'hunk' or 'diff only' wording and reopens the file with `python3 src/RimMandrake/Utils/code_review_status.py reopen`.
- **`infrastructure/state/code_review/<SEAT>.jsonl` is one shared file per seat, and parallel helpers collide on it.** Helper A's mark-clean lines sit uncommitted beside helper B's, and the commit hook forces a pathspec commit, which takes the whole working-tree file, so neither can commit its own marks without sweeping the other's (staging a HEAD-plus-your-lines blob with `update-index` is refused too, because a pathspec-less commit is refused). Commit mark-clean lines in the same Bash turn as the mark, or let the last helper of the wave (or the parent) commit the shard once all are done. Open fix: one shard per helper, or a `code_review_status.py` verb that commits only the caller's tagged records.
- **Grep memory before relaying a fact about factions, biomes or rulings to the owner.** A subagent's unverified fact reached the owner wrong (a DLC's empire named as the wrong faction) when a memory file held the right answer.
- **Debugging is script-first (`design/RimMandrake/debug_process.md`).** A live poke that ends without its lesson committed as a check (plus the informative false theories) is lost work: the `ns_probe_*` scratch files vanished and survived only in commit messages.
- **The Conductor stays conversational.** Never block the owner's window on long foreground waits (sleep/until loops, multi-minute checks) or chain hidden steps; push waits to background and answer him in plain words first. Owner: "Conductor is supposed to be someone I can easily chat with about how it's going... Almost the opposite of the design intention" and "This procedure is opaque. What are you even doing?"
- **Before drafting from an item's text, check it against later rulings.** A brief can carry a mechanism a later owner ruling voided (TWILIGHT_BOTTOM_CAST_1 still named 'lease practice' after "The Compact does NOT sell light... Remove." (owner)). Grep the item's design dir for an existing draft and read the later sibling passes' 'Ruled' headers first.
- **Say what happened and how you know in the first clause of a status line.** 'No longer in the running list' reads as lost or dropped to the owner; v3 had simply finished.
- **More than ~10 concurrent helpers closes the fewest items per token.** Burn days with 10-22 helpers spent 99.5M cache-read tokens per closed item (30 closes), against 5.2M on the framework-guided day at 4-7 concurrent and 11.2M in ALMOST_OUT. Spend surplus tokens on durable no-review work (harnesses, instruments, wiring), not on more parallel helpers or review waves.
- **Delegation did not stop the owner's card load.** After `delegation_policy.md` he still answered 207 card questions in 4.1 days (~50/day vs ~76/day before); 144 were in classes already delegated (design 57, process 58, art picks 29). Agreement with the agent's Recommended option there was only 50-61%, so most were real choices; ordering/helper-count cards (81% agree) and twin-apply cards (86%) are pure leak. On his own sheet marks, agents' 'wait/keep' recommendations matched him 39%, while a 'newest mark wins, x acts now' rule predicts 83%.
- **No subagent type can reach Artifact/ArtifactData** (rm-fixer lacks ToolSearch; rm-builder's ToolSearch finds neither; general-purpose is hook-blocked). A helper gathers the data into a file and the write goes through a headless `claude -p` with `CLAUDE_CODE_ARTIFACT=1` (`src/RimMandrake/Utils/fleet_refresh.py`). Helper types need `SendMessage` in their tools list to report mid-run (added to rm-builder, rm-fixer, rm-bridge): a brief must not tell a running helper to message anyone unless its type has the tool.

## Subagents — this is where the saving is

🔴 **Every `Agent` call takes `model`. Pass it, every time**
(`block_agent_without_model.py` refuses otherwise; it also blocks named agent types such as `Explore` called without an explicit `model`, despite the hook text exempting named types).

| Job | Model |
|---|---|
| OS-level search: grep, glob, inventory, "does X exist", fixed-shape census; extraction/classification with a checkable result | **sonnet** |
| Well-defined coding a compiler, selftest or validator will check | **sonnet** |
| Sweep where the agent must interpret or classify | **sonnet** |
| Fan-out whose returns will contradict; adversarial refutation | **sonnet** |
| **Design** — a spec, a roster, a taxonomy, anything the owner reads as design | **opus**, backgrounded |
| **Complex code generation** — a new system, Harmony/C#, cross-file changes with no test to catch them | **opus** |
| Anything acted on **without re-deriving it** | **opus** — and ask why it is a subagent |

A subagent's return is EVIDENCE, never a finding — it carries CONFIRMED/UNCERTAIN
and the window decides what is true. Never spawn a duplicate for "reliability".
- **A subagent report ending `HANDOFF READY` is the agent's own artifact, not a handoff.** Only the seat's handoff ritual (`handoff.py --check`) licenses that line. Parallel helpers must not share one stage folder: `selftest_winstage` once staged every clone in one shared folder so agents tested each other's source (now a per-clone hash).
- **Never run heavy ML from a subagent inside a seat.** Model downloads, torch, ComfyUI, mesh generators and big numpy rasterizers inherit the seat's cgroup; one 7 GB child pushed the 10 GB scope to its limit with swap full, the kernel killed it, and the window died anyway (`OOMPolicy=continue` only stops systemd tearing the scope down). Run such a job in its own bounded systemd scope so a balloon kills only itself. Local generation is parked; do not relaunch it without the owner's word.

## Four places a cheaper tier is forbidden outright

1. **Deciding whether an instrument told the truth** (`BUILDABLE.md` exists because they lie).
2. **Live bridge writes** — the world is frozen and hand-authored, no regenerate behind it.
3. **The world, and art** — *"iterate by LOOKING"*; realism is not scoreable.
4. **Text the owner reads as a conclusion** — above all a number.
   ↳ 🔴 **One carve-out, owner ruling 2026-09-16: north-star `must read` verdicts.**
   Verbatim: *"Let a model YES green a line."* A model judging a mod's letter or
   flavour prose against a `must read` line MAY return a pass, and that pass greens
   the line — it is not routed to him. The tier floor still applies (opus), and
   `cannot read` lines stay absolute. Rationale and the residual risk are in
   `design/RimMandrake/north_star_validation_spec.md` §10.4: the rule it replaced
   would have made any text-first mod permanently ungreenable unattended, and an
   off-register letter is a bounded, recoverable failure. **This carve-out is
   read-verdict-only** — a number, a count, or a finding he will act on still lands
   on row 3 and still comes to him.

## The escalation clause every cheap-worker prompt carries

> Escalate instead of guessing if: the criteria do not decide the case · the change
> reaches files outside the ones named · a measurement disagrees with the item · a
> tool returns success and you cannot see the effect · you would have to invent a
> defName, field or namespace.

Escalating is a success; record it. Stamp the model on closes (`model=sonnet-5.5` in
the `note`) so the ledger can answer accepted-work rate per model.

## Hooks and Claude Code session quirks
- **A `PreToolUse` hook added to `.claude/settings.json` mid-session does not fire** — not for this window's Bash calls and not for its subagents' — until a new session starts; a hook already present at session start does fire for subagents. Test a new hook in a fresh window, never by exercising it in the one that added it.
- **A Claude Code hook marked `asyncRewake` survives its session's kill** (re-parented to /init, would wait its full 23 h timeout; measured on Claude Code 2.1.308). Any long-waiting async hook must find its claude ancestor at start and exit when that pid dies (`doorbell.claude_ancestor` + `owner_pid` guard).
- **A Claude Code transcript (`~/.claude/projects/<cwd>/<session>.jsonl`) logs one line per content block of an API message, each repeating the SAME usage:** sum usage once per `message.id` (last line wins) or a run is overcounted 2-3x; deduped it reproduces the `claude -p` result json exactly. A role run's `--name` is not in the jsonl: find it by session id (pin with `--session-id`) or by the "role launch <unit>" text in the first user line (`role_launch.transcript_usage`).
- **The Claude Code `WorktreeCreate` hook's real stdin is `cwd, name, prompt_id, session_id, transcript_path`** (the docs say `base_path`/`worktree_name`, which is wrong). `WorktreeRemove` never fires (0 of 11 runs). The hook's parent pid is a dying `sh -c`: walk `/proc` up to the `claude` process to find the session.
- **A PreToolUse Bash hook matches its trigger word anywhere in the command text, even inside a heredoc that only mentions it,** and a refusal rejects the whole compound command so its other steps do not run. Two seen: the art-push hook refuses any command containing the repo's push-script word while HEAD carries art events whose PNGs are not committed (for example after a sibling helper swept your art-shard lines into its commit); the registry-write hook refuses a heredoc patch that merely names the modcheck status file. Keep the word out of the command: write prose with Write/Edit, put the patch in a scratch file, and run it.
- **Replaying hook payloads is not read-only:** an allowed `Agent` call makes `block_agent_over_slots.py` reserve a real helper slot for 90 s (`spawn_reservations.json`). Any tool that feeds hooks synthetic Agent calls must set `RM_SPAWN_RESERVE_S=0`, as `hook_latency.py` does.

## Hooks that route or refuse
- **A hook whose refusal text names a route must be tested against that route.** `block_shared_tree_merge.py` sent merges to a scratch clone and then refused them there, because it treated every clone as shared.
