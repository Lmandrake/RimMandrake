# GPT review of design.md (verbatim)

Model: gpt-6.1-sol via src/RimMandrake/Utils/gpt_consult.py (effort high), 2026-11-04 22:29-22:35Z. Job dir: D:\ClaudeWork\rimmandrake\scratch\codex\consult-20261104-142934-164943. Prompt: D:\ClaudeWork\rimmandrake\agent_visibility\gpt_prompt.md, with design.md v1 and ten source files attached. The answer below is unedited.

---

## 1. Skeptical inquiry

**Keep the current headless workers during the first migration. Build the station window now. Reconsider the proposed steering mechanism before implementing F.**

The document’s strongest conclusion is that token recovery does not require visible terminals. Its weakest conclusion is that **F preserves the current engine’s cleanliness with a moderately sized handover feature**. F introduces a second execution mode, ownership transfer, interruption recovery, and additional accounting boundaries. It could be more difficult to make reliable than a carefully supervised interactive worker.

The owner requested a workstation interface: one window, recognizable stations, free observation, and occasional input. “Keep it headless” is an implementation decision, not an adequate answer to that request.

This is a review of the supplied evidence, not a machine audit. Current primary documentation helps identify supported mechanisms; behavior that matters must still be verified against the installed **2.1.311**.

### The weakest claims

| Claim or implication | Assessment |
|---|---|
| Approximately $4.4 of work could have been saved | **Wrong interpretation of the measurement.** The three results total **$4.41199 and 84 reported turns**. That is prior estimated consumption associated with interrupted conversations. It is neither the amount of work destroyed nor the amount a resume would save. Files, commits, logs, and test results may already survive. Conversely, recovering a difficult investigation may save more elapsed time than those dollars suggest. |
| Headless resume “works fine” | The PELICAN test proves basic conversation continuity and session-ID preservation. It does not prove recovery after an interrupted tool, compaction, changed checkout, stale game connection, or process collision. |
| The same cwd is required | Sensible operational policy; insufficiently established as a CLI restriction. Project-directory association, session discovery, and correct execution context are different matters. Keep the same validated cwd by policy even if the CLI can load a transcript elsewhere. |
| One final JSON object is what makes the pipeline trustworthy | **Overstated.** It is a convenient existing contract. Lifecycle control, ownership, validation, and accounting are what make it trustworthy. Streaming output can retain a terminal result event; an adapter can preserve the existing result-file interface. |
| Interactive workers lose determinism | Neither mode makes the model deterministic. Interactive input makes the task history variable. That can be recorded and governed. Schema validation checks output shape, not whether a verdict is correct. |
| Owner typing in B is poorly recorded, while F is clean | Both record user messages in the conversation. F adds an item-journal interval. B could add the same journal integration. This is an instrumentation difference, not an inherent advantage of F. |
| C can resume only through typing or WT keystroke injection | **False dichotomy.** A supervisor can restart a stopped conversation through a launcher running in the tab or behind its terminal connection. Windows UI automation is not required for every lifecycle operation. |
| Background sessions necessarily escape the unit’s cgroup | **Too categorical and contradicted by the wrapper’s own measured tree.** Children inherit cgroups unless moved. The real question is which process starts or reuses the daemon, where that daemon lives, and where it creates sessions. |
| Six dead fleet windows demonstrate WT unreliability | They demonstrate six terminal windows containing ended commands. They do not establish six WT failures. Keeping a shell or exit message open can be expected behavior. The weak component is the current screen-based lifecycle inference. |
| D gives one failure domain per window | A window is not necessarily a process or backend isolation boundary. All stations still share Windows, WSL, storage, the account, and possibly other host processes. |
| E1 failures are cosmetic | Usually harmless to execution, but potentially consequential to the owner: a stale display can falsely imply progress, completion, or that a note reached the correct worker. Display freshness and identity must be explicit. |
| The watchdog is unchanged | The code exposes an existing correctness problem, and takeover makes it worse. See below. |
| F costs M | **Unsupported.** “Stop at its next safe point” contains most of the difficult engineering. No safe-point protocol is supplied. |

The claim that every factual statement is measured or explicitly assumed also does not survive the comparison table. Several lifecycle, crash, memory, and implementation-cost judgments are architectural predictions presented with more confidence than their evidence supports.

### The watchdog evidence is worse than the prose suggests

`activity()` scans **every directory entry** under the clone’s transcript directory and takes the newest mtime. It does not select the recorded session, filter by this launch, or distinguish meaningful work from another conversation’s writes.

Consequences:

- A different session in the same clone can keep a stalled worker apparently active.
- An owner’s resumed conversation can mask the original worker’s silence.
- An actual long-running tool can be productive without writing transcript messages.
- Transcript freshness does not establish game-bridge progress.
- Read-only watching should not affect this timestamp; accidentally adding viewer-generated files there could.

Also, `run_max_s` is checked before silence in `overdue()`. Merely making transcript activity fresh cannot extend that wall.

Replace the single “activity” concept with separate facts: **process alive, model/message activity, tool running, tool progress, external operation pending, and owner-held state**.

### The document underweights the owner’s workflow

The owner has already expressed interest in steering. Deferring it until “if he finds he wants to type” reframes an existing requirement as an optional future discovery.

Three details matter:

1. **Recognizable stations reduce cognitive work.** “Builder 3” should remain Builder 3 through process restarts. The owner should not hunt for a UUID or determine which generation is current.
2. **Watching is an interaction, not just data availability.** A 197 KB status file and a raw transcript are both technically visible. Neither necessarily answers “What is this station doing, and is it stuck?”
3. **Occasional steering should be lightweight.** A note such as “Use the earlier texture; this version loses the silhouette” should not ordinarily require stopping a worker, acquiring ownership, reopening Claude, and handing it back.

The interface needs at least two distinct actions:

- **Send a note:** durable, queued, acknowledged, normally non-interrupting.
- **Take control:** stop or interrupt ongoing work and establish exclusive interactive ownership.

F conflates them.

### Do the visible options get a fair hearing?

**B, tmux: unfairly bundled with the worst supervision strategy.**  
`capture-pane` and `send-keys` are useful terminal operations. They need not be the authoritative liveness detector or verdict parser. Unit state, transcript events, hooks, explicit completion artifacts, and a controller can remain authoritative.

Its common-server failure domain is real. Independent tmux servers are supported through separate sockets, although they add management complexity. One shared server is a choice, not a defining requirement of tmux. [tmux 3.6 manual](https://github.com/tmux/tmux/blob/3.6/tmux.1)

**C, WT tabs: unfairly blamed for launcher shortcomings.**  
A stable named window with precreated tabs does not require opening a tab whenever a worker starts. Nor must terminal text establish worker health. Its fair disadvantages are desk dependence, terminal-close behavior for directly connected workers, and the loss of the existing final-result contract if all workers become ordinary TUIs.

**D, stacked windows: mostly fairly rejected.**  
It poorly matches “one window,” increases visual search, and consumes desktop space. Its legitimate advantages are simultaneous observation and potentially fewer accidental whole-fleet closes. Those advantages matter for two debugging stations, not twelve permanent windows.

**E1: gets too generous a hearing on fidelity and implementation cost.**  
A good viewer needs session identity, tool lifecycle rendering, truncation with expansion, compaction handling, reconnects, and explicit stale states. It is still a good first step.

### Is F sound?

**Sequentially resuming the same conversation across print and interactive modes is plausible. Treating that as transactional transfer of a worker is unsound.**

Current Claude documentation distinguishes interruption from termination: SIGTERM leaves a print turn unfinished and records no result for that turn; SIGINT or the SDK’s interrupt operation can end the turn before process shutdown. That behavior needs a local probe before becoming a safety assumption. [Programmatic execution documentation](https://code.claude.com/docs/en/headless)

F must address all of these:

| Boundary | What can break | Required protection |
|---|---|---|
| Model/tool boundary | Partial tool arguments, interrupted commands, missing terminal result, unresolved tool outcome | Explicit interruption and reconciliation; never assume replay is safe |
| Filesystem | Half-written files, dirty index, interrupted build, completed commit absent from the last visible message | Inspect actual repository state before continuing |
| External side effects | A game command succeeds after its client dies; deployment finishes without acknowledgement | Operation IDs and outcome queries where available; otherwise mark outcome uncertain |
| Process lifetime | Stopping the service leaves its separate scope or marked descendants alive | Verify service, scope, marked processes, and relevant external jobs have settled |
| Transcript | Two processes load and append to the same conversation | Exclusive session ownership enforced by the controller |
| Clone | A fresh worker or pool allocator claims the clone during takeover | Preserve the clone lease across the entire handover |
| Cleanup | `ExecStopPost` runs and releases resources or removes artifacts the interactive continuation needs | A deliberate handover termination reason understood by cleanup |
| Game bridge | The interactive launch lacks `RIMFLOW_BRIDGE_SEAT`, changes ownership identity, or inherits a stale lease | Recreate the approved environment and reacquire bridge ownership explicitly |
| Watchdog | Old supervisor ticks kill, requeue, or penalize the owner’s conversation | Durable state transition plus stale-generation rejection |
| Independent wall clock | Pausing supervisor checks does not pause systemd `RuntimeMaxSec` | A new bounded ownership interval or explicitly redesigned lifetime |
| Launch configuration | Interactive resume omits role, model, MCP configuration, walls, or tool permissions | A recorded launch contract; resume must not become an unrestricted escape hatch |
| Hand-back | “Hand back” is interpreted as ordinary chat; owner exits without completing transfer | A controller command with an acknowledged state transition |
| Recovery | Controller crashes between stop, ownership change, and interactive launch | Restart reconciliation for every intermediate state |

The bridge deserves particular attention. The launch excerpt assigns a shared bridge-holder identity. That identity alone cannot distinguish an obsolete worker from its replacement. Where the bridge supports it, use an ownership generation that rejects commands from an old holder.

**Do not use SIGSTOP as the safe-point mechanism.** It freezes arbitrary execution while retaining locks and leaving external work unresolved.

F also has no inherent cache advantage. A quick handover might reuse a matching cached prefix; a mode/configuration change might disturb it. After hours, a cold prefill is likely under ordinary API cache lifetimes. Neither “always uncached” nor “always cheaper than starting fresh” is established. API cache documentation describes five-minute and one-hour lifetimes; subscription behavior and this launcher still require measurement. [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)

**Verdict on F:** valid as a carefully engineered maintenance operation; a poor default mechanism for occasional helpful notes.

## 2. Expansion: missed or under-explored approaches

### Separate three choices the document couples together

The design should independently choose:

1. **Execution:** print CLI, interactive CLI, background CLI, or Agent SDK.
2. **Control:** systemd lifecycle, ownership, bounds, completion validation.
3. **Presentation:** WT tabs, tmux, or a web viewer.

A terminal can display a headless worker. An interactive worker can have systemd bounds. A streaming worker can emit structured results.

### Alternatives and whether they beat the recommendation

| Approach | Concrete design | Does it beat A + E1, then F? |
|---|---|---|
| **Stream output while retaining print execution** | Use `--output-format stream-json`; persist events independently of viewers; extract the terminal result into the existing result-file contract | **A strong improvement to investigate.** Better supported live event interface than depending exclusively on private transcript format. Requires an adapter and regression checks, not a wholesale engine rewrite |
| **B*: supervised interactive Claude in tmux** | A pane runs a foreground service/PTY connection or bounded scope; controller tracks the actual worker unit/scope; completion comes through explicit artifacts/events | **A credible steering contender.** Potentially simpler than repeated F transfers. Does not automatically preserve the existing JSON/schema workflow |
| **Agent SDK with streaming input** | One bounded controller/worker process per item; durable note queue; streamed events/results; explicit interrupt operation | **Best target to probe for watch plus steer.** More application code, but it addresses the interaction requirement directly |
| **`--bg` inside a verified cgroup arrangement** | Determine daemon placement and reuse; map background IDs to conversations, units, clones, and controller ownership; supervise actual descendants | **Could beat F and interactive tmux.** Native attach is attractive. Existing evidence does not justify either fleet adoption or categorical rejection |
| **E5: web transcript/event viewer** | One browser window with station tabs, overview, search, expandable tool output, and later a note box | **Can beat terminal rendering on usability.** More software to maintain. Start read-only and reuse the same event backend |
| **Persistent mailbox without live streaming input** | Owner notes are stored against item/run identity; a supported hook or the next controller-managed turn delivers them | **Often beats F for ordinary notes.** Lower interaction ambition; delivery latency must be honest |
| **`script`, asciinema, or tmux output recording** | Record a supervised interactive terminal for replay and debugging | **Useful supplement, not a control plane.** Preserves what appeared on screen; does not establish structured completion or external-operation success |
| **WT named-window presentation** | Create `Pipeline` once, populate stable station tabs, and reconnect viewers without creating new tabs per run | **Improves every terminal-based option.** It is a presentation solution, not a reason to change worker execution |

Streaming output ends with a structured result message containing session and cost metadata. Preserve the raw event file and make result extraction independent of whether a viewer is connected. A slow or dead viewer must never block the worker. [CLI streaming output](https://code.claude.com/docs/en/headless)

#### How B* should actually work

A crucial cgroup trap: starting a shared tmux server inside a unit does **not** ensure that later panes created through an existing server belong to the caller’s unit. The existing server creates those processes.

Instead, have the pane command explicitly enter its worker’s bounded scope, or connect through a foreground PTY client to a service that owns the worker. Verify `/proc/<pid>/cgroup` for Claude and representative tool descendants.

Systemd supports interactive services through `systemd-run --pty`. That establishes feasibility, not reconnectability or survival after every terminal failure. The PTY connection’s failure behavior still needs testing. [systemd-run documentation](https://freedesktop.org/software/systemd/man/latest/systemd-run.html)

B* still needs an answer to “the agent finished the item but the TUI remains alive.” **Process exit and task completion become separate events.** That is real work; it is not grounds for requiring screen scraping.

#### Why the SDK deserves an early probe

The SDK documents persistent streaming input, sequential queued messages, interruptions, and real-time output. This is much closer to the requested interaction than transferring a transcript between two processes. [Streaming input](https://code.claude.com/docs/en/agent-sdk/streaming-vs-single-mode)

Important qualifications:

- Persist notes before sending; an in-memory queue is insufficient.
- Separate “received by controller,” “sent to Claude,” and “acknowledged by the worker.”
- An interrupt leaves buffered messages, including the interrupted result. Drain and correlate those before interpreting the next response. [Python SDK interruption behavior](https://code.claude.com/docs/en/agent-sdk/python)
- Confirm configuration parity: role instructions, project settings, hooks, tools, model, bridge environment, and output validation.
- Do not silently change the account or charging path. Current Anthropic guidance says signed-in Agent SDK and `-p` usage can still draw from subscription limits; the SDK is not inherently an escape from those limits. [SDK plan usage](https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan)

#### Background sessions: test daemon ownership, not just launcher ownership

The supplied help explicitly warns that `--bg --resume` can start a **copy** when the session is already running. That is unacceptable as an unnoticed recovery fallback.

Probe these separately:

1. No daemon exists; start a bounded background session.
2. A daemon already exists under another seat.
3. Stop the launching service.
4. Stop the intended scope.
5. Kill the daemon.
6. Resume a conversation already running.
7. Attach, detach, and close WT.
8. Run `respawn` and observe whether work actually continues.

The wrapper’s measured background tree makes “background always escapes cgroups” untenable. It does not prove reliable per-worker isolation.

#### Windows Terminal names and focus

Microsoft documents `wt -w <name>` targeting an existing named window and creating it when absent. That is more useful here than repeated `-w new` plus title discovery. A window name is distinct from its displayed tab title. [WT command-line arguments](https://learn.microsoft.com/en-us/windows/terminal/command-line-arguments)

However:

- Targeting a named window does not establish that an invocation leaves foreground focus untouched.
- Selecting a tab and activating a Windows window are separate effects.
- `--focus` means Terminal’s focus display mode, not “launch without stealing focus.”
- The supplied script explicitly calls `SetForegroundWindow`.
- `FOUNDRY` is explicitly refused in the launch loop. Reusing its rectangle requires a new supported viewer seat/profile or a deliberate launcher change.

Precreate station tabs at fleet launch, then reconnect their contents. Test foreground HWND and selected-tab behavior on the installed WT version. Do not promise zero focus stealing from command syntax alone.

Also, choose one primary navigation scheme initially: actual WT station tabs **or** tmux station windows. The recommendation currently mixes both without explaining the interaction.

## 3. Improve the “resume from token loss” specification

Section 7 needs to describe **recovery of an interrupted logical attempt**, not just relaunching a remembered conversation.

### A. Separate account conditions

Do not classify every 429 or authentication error as a weekly token outage.

| Condition | Appropriate handling |
|---|---|
| Explicit account quota exhaustion | Suspend affected model/account lane until reset or successful eligibility check |
| Short-term rate/concurrency limit | Respect retry guidance; reduce admission; bounded backoff |
| Authentication failure | Separate auth state and recovery path; do not assume waiting until noon fixes it |
| Network/provider failure | Bounded infrastructure retry; preserve interruption state |
| Context-window/max-turn/budget limit | Separate task/session policy; account reset is irrelevant |
| Tool output quoting a limit message | Not evidence that the account failed |

Prefer structured error fields. Use narrowly matched top-level terminal errors as fallback. Do not search arbitrary tool output for “429” or “weekly limit.”

Preserve the raw error, classification version, and confidence. Missing or malformed final JSON must not become either success or “zero usage.”

The outage census also needs reconciliation: **51 result files, 45 account-loss journal events, 14 launch failures, and differing jam counts** are not one population. Deduplicate by run/session and document the observation windows before using them as denominators.

### B. Record identity before launch

Pin a session UUID for every new Claude run, including Relentless. The code already supports this for role launches.

Record:

- Logical item and attempt.
- Strategy/approach generation.
- Unique execution ID and resume index.
- Session ID and exact transcript location.
- Canonical cwd, repository/worktree identity, branch, base SHA.
- Last observed HEAD and dirty-state summary.
- Role, model, configuration fingerprints, output schema.
- Service, scope, process marker, clone ownership.
- Account/model lane.
- Active-time and consumption budgets.
- Latest checkpoint and unresolved external operation IDs.

**A resume needs a new execution/unit identity but normally the same logical attempt and strategy generation.** Reusing old output paths or ambiguous unit names invites overwrites and stale supervision.

Do not blindly combine the original new-session arguments with resume arguments. Build and test a distinct resume launch path.

### C. Replace “zero usage” with “no useful continuation state”

Zero output tokens are evidence, not a complete classification.

A zero-token launch can still run `pre_launch` steps and hooks. A cached or incomplete usage report may not describe all activity. A resumed session can have useful inherited context even if its latest failed invocation produced nothing.

Use three classes:

1. **Fresh launch with verified no useful session progress:** ordinary requeue, preserving any external effects.
2. **Useful saved conversation or checkpoint:** candidate for resume.
3. **Unknown:** reconcile transcript, repository, and external operations before choosing.

Usage should inform this decision, not exclusively determine it.

### D. Freeze ownership and revalidate the work

Before eligibility is decided:

- Keep the clone reserved.
- Prevent another scheduler from launching the item.
- Settle the old service, scope, and marked descendants.
- Establish whether external game/build operations remain active.

Before resuming:

- Confirm the item remains open and this attempt remains current.
- Confirm no successor already completed or superseded it.
- Confirm the clone path has not been reused for another repository or task.
- Inspect HEAD, index, dirty files, and incomplete git operations.
- Revalidate task inputs and dependencies.

A changed repository is not automatically disqualifying. Expected uncommitted work is exactly what should survive. An unexplained branch replacement or reused clone is a different situation.

**Checker resumes require particular care.** The judged artifact SHA and evidence set must remain valid. A checker must not complete a verdict about yesterday’s artifact after the worker changed it.

The role launcher’s `pre_launch` chain creates another hazard: rerunning it on resume can regenerate evidence and silently change what the old conversation believes it is judging. Classify each pre-step as:

- Safe to repeat unchanged.
- Validation-only on resume.
- Must preserve its original output.
- Invalidates the old judgment context if inputs changed.

### E. Make reset parsing conservative

“Resets 12pm” is not a complete timestamp.

Prefer a structured absolute reset or retry interval when supplied. Otherwise store the original text, observation timestamp, parsing result, and uncertainty.

For local-time text:

- Use an IANA zone such as `America/Los_Angeles`.
- Resolve the date from the observation and any stated day.
- Handle DST and midnight explicitly.
- Do not silently reinterpret an already-past time as tomorrow.
- Reject ambiguous interpretations rather than scheduling a precise-looking wrong answer.
- Use monotonic time for retry delays and UTC timestamps for durable scheduling.

For this outage, noon Los Angeles on November 4 corresponds to 20:00Z. That successful example does not validate a general parser.

### F. Use one breaker and controlled admission

A global account outage needs coordinated handling across Relentless, Dispatcher role runs, and timer LLM jobs. Otherwise each independently “cheap” probe recreates the launch storm.

Keep local services and non-LLM maintenance running.

After a credible reset:

1. Wait a short margin.
2. Admit one bounded canary or eligibility probe for the affected lane.
3. Confirm the account is usable for that lane.
4. Admit further work gradually.
5. Reopen the breaker immediately on renewed quota evidence.

A cheap model’s success may not establish another model’s eligibility.

“One per tick” is underspecified. Define an initial policy, for example **one admission every 15 seconds, at most two simultaneously restoring contexts**, then adjust from observed prefill latency, memory pressure, and rate-limit responses. Those are starting values, not measured optima.

### G. Account for compaction and prompt snapshots

A saved transcript does not imply all historical turns return to the model. Current documentation says a compacted session resumes from its summary, retained messages, and subsequent history. It also says interrupted tools are not automatically rerun. [Session restoration](https://code.claude.com/docs/en/sessions)

Therefore:

- Preserve durable checkpoints containing decisions, artifacts, SHAs, test outcomes, and pending operations.
- Do not report all historical turns as “preserved context.”
- If the summary omitted crucial evidence, reload it deliberately.
- Expect old temporary file references to be invalid.

The supplied help also exposes **system-prompt snapshots**. Passing updated system-prompt text on resume may not apply it until compaction. Put the recovery facts in the new user message and explicitly handle incompatible policy/configuration changes. Do not assume relaunching `--agent` refreshes every instruction.

There is a concrete temp-directory inconsistency to investigate: `role_launch` supplies per-run temporary variables, but `claude_bounded.sh` subsequently overwrites `TMPDIR` with a per-seat directory. The run’s `TMP`, `TEMP`, and Claude-specific temp variables may consequently disagree. Recovery must inspect actual artifact paths, not assume the old run directory contains everything.

### H. Use a recovery prompt that establishes boundaries

The existing prompt is too casual. A better template is:

> This is recovery of item `<item>`, logical attempt `<attempt>`, execution `<execution>`, following `<classified interruption>` at `<UTC time>`. Your saved conversation may contain compacted history and interrupted tool calls.
>
> Continue the original task and acceptance criteria. Preserve existing work and the current approach unless new evidence requires a change.
>
> Before making changes, verify the repository identity, branch, HEAD, dirty files, relevant artifacts, and current task state against the recovery record at `<path>`. Treat earlier observations as historical.
>
> Reconcile the last interrupted operation. Check whether it completed before repeating it. Do not blindly repeat commits, publishes, game commands, deployments, or other external actions. Reacquire required locks and bridge ownership; do not assume previous ownership survives.
>
> For judgments, verify the exact artifact and evidence revisions. If the task is superseded, ownership conflicts, evidence changed incompatibly, or an operation’s outcome cannot be determined, stop with the specified structured hold reason.
>
> Otherwise continue from the next unfinished step and return the original required output format.

Keep the machine-generated recovery record concise. The prompt should point to it, not paste an enormous ledger into every continuation.

### I. Make recovery idempotent

Use a durable state progression such as:

`account_suspended → waiting → validating → launching → active`

Transitions should compare the expected item revision and ownership generation. Every supervisor tick must recognize an already-started resume.

The tricky crash is “unit started, controller died before recording success.” Reconcile the recorded execution ID against systemd and process markers before launching another copy.

“One resume per run; classify afresh if it fails again” is effectively unbounded across newly named runs. Instead define:

- One active continuation per logical attempt.
- Bounded launch retries per outage episode.
- Bounded cumulative active time and consumption.
- Repeated immediate quota failure reopens the breaker.
- No automatic resume of completed, cancelled, owner-held, or superseded work.

Exactly-once launch intent is achievable within the controller. Exactly-once external effects require operation-level support; prompts alone cannot provide it.

### J. Integrate correctly with Relentless and role scheduling

Account suspension should not:

- Add strikes.
- Advance approach-change counters.
- Count as a failed checker verdict.
- Raise ordinary role-failure alarms.
- Consume attribution wait time as though the account were available.
- Reset previously earned strikes or erase real failures.

Preserve the same strategy generation across recovery. If someone deliberately changes the approach while the account is out, the old session becomes superseded.

Track **active execution time separately from outage time**, while retaining a cumulative attempt budget. Otherwise a resume either dies immediately on an old timestamp or receives a new full hour indefinitely.

For the findings judge, record a unique scheduled-job instance and define catch-up behavior. “Retry after reset” must not collide with a manual rerun or the next scheduled invocation.

### K. Fix accounting

Current documentation says resumed result totals include earlier session spend. Summing the original result and the resumed total can double-count consumption. Streamed message fragments can also share a message ID. [Cost and usage accounting](https://code.claude.com/docs/en/agent-sdk/cost-tracking)

Record both:

- Session cumulative totals.
- Execution deltas derived from verified baselines or deduplicated message usage.

Distinguish estimated dollar equivalents, tokens, and subscription capacity. The outage’s `$0` and `$4.41` figures are not direct measurements of quota effects.

## 4. Sharper, quantified metrics and approach scores

The current metric set is too favorable to the recommendation. “Interventions possible per day” rewards unlimited intervention even if it is disruptive. “Turns resumed” rewards retaining stale context. “One station per crash” ignores shared limits and external processes.

### Measurement protocol

Use the same small workload suite and concurrency levels—**1, 4, and 8 workers**—for each prototype. Include editing, judging a pinned SHA, a long build, and a bridge operation.

Inject failures before model output, during tool execution, after an external effect but before acknowledgement, during recovery launch, and during owner transfer.

The following are **proposed acceptance thresholds**, not measurements:

| ID | Metric and measurement on this machine | Target |
|---|---|---|
| **R** | Recovery correctness and latency: journal state transitions, known expected outputs, duplicate-effect checks | Every safe synthetic case recovers; unsafe cases hold correctly; first eligible continuation within 5 minutes; all eight admitted within 10 minutes under available capacity |
| **V** | Visibility: correlate persisted event timestamps with display timestamps; owner identifies station/task/current action in timed exercises | p95 display lag ≤2 s; disconnected/stale indication ≤5 s; correct identification within 10 s in at least 9/10 exercises |
| **S** | Steering: 100 uniquely tagged notes across busy, idle, restarting, and reassigned stations | Zero wrong-item deliveries; durable receipt ≤1 s; delivered at next documented boundary; busy notes show pending status; explicit takeover p95 ≤30 s when safely interruptible |
| **C** | Control and integrity: kill/close tests, process/cgroup inspection, transcript writers, clone ownership, verdict validation | Zero simultaneous writers/owners; zero stale-generation actions; all expected descendants bounded; no duplicate external effects; incomplete results never accepted |
| **T** | Token economics: message-ID-deduplicated usage, cache counters, restored-context cost, and replayed tool work | Watching issues zero model requests; ≤10% added consumption versus equivalent uninterrupted work in controlled recovery tests, or an explicit justified exception |
| **H** | Resource/throughput overhead: cgroup memory peaks and pressure, `/proc` CPU, Windows terminal working set, completed identical jobs/hour | Viewer/control layer adds ≤1 GB WSL memory at eight stations and ≤5% VM CPU; throughput loss ≤5%; no sustained pressure-induced stalls |
| **F** | Focus disturbance: log foreground HWND and selected station during 100 automatic restart/reconnect cycles | Zero unexpected foreground or station changes |
| **O** | Owner operating burden: count manual repair steps and minutes during a seven-day trial | Routine use requires no shell commands; ≤5 minutes/week of owner repair; no need to identify sessions manually |
| **D** | Delivery and maintenance effort: tracked implementation/debugging time, including failure tests | Basic station viewer within 2 working days; one steering pilot within a further 3; stop and reassess if either exceeds twice its budget |

The token-overhead target is deliberately demanding. A long cold-context recovery may exceed it while still being worthwhile. Record that result; do not hide it behind “resume is cheaper.”

Also measure **fault blast radius by fault type**, rather than one number:

- Viewer close.
- tmux server loss.
- Worker kill.
- Background daemon loss.
- Per-worker memory breach.
- Aggregate slice pressure.
- WSL restart.
- Account loss.

The existing 24 GB parent slice means one worker’s 10 GB ceiling does not establish a one-station blast radius under aggregate memory pressure. Eight 10 GB maxima are not eight reserved allocations.

### Provisional scores

**5 = strong fit, 3 = material qualifications, 1 = poor fit.** These are architectural estimates for the approaches as described, not test results. Every approach still has to pass C’s safety gates.

#### Recovery, observation, steering, integrity, tokens

| Approach | R | V | S | C | T |
|---|---:|---:|---:|---:|---:|
| **A: headless + resume** | 4 | 1 | 1 | 5 | 4 |
| **B: interactive tmux** | 3 | 5 | 5 | 3 | 4 |
| **C: interactive WT tabs** | 2 | 5 | 5 | 2 | 4 |
| **D: stacked WT** | 2 | 3 | 4 | 2 | 4 |
| **E1: headless + viewer** | 4 | 5 | 1 | 5 | 4 |
| **E2: native background** | 3 | 5 | 5 | 2 | 4 |
| **E3: Remote Control fleet** | 2 | 3 | 4 | 2 | 4 |
| **E4: headless + streaming inbox/viewer** | 4 | 5 | 4 | 4 | 4 |
| **F: stop/resume takeover** | 3 | 5 | 4 | 2 | 2 |

#### Resources, focus, owner burden, delivery

| Approach | H | F | O | D |
|---|---:|---:|---:|---:|
| **A** | 5 | 5 | 5 | 5 |
| **B** | 4 | 4 | 3 | 2 |
| **C** | 4 | 2 | 2 | 2 |
| **D** | 3 | 1 | 1 | 1 |
| **E1** | 5 | 4 | 4 | 4 |
| **E2** | 2 | 4 | 4 | 3 |
| **E3** | 4 | 5 | 2 | 3 |
| **E4** | 5 | 4 | 3 | 3 |
| **F** | 4 | 3 | 2 | 2 |

Short justifications:

- **A:** preserves the current control contract; largely fails the owner’s interaction request.
- **B:** excellent direct interaction and reconnection; task completion and automation need explicit redesign. B* should improve C materially.
- **C:** excellent desktop interaction; direct terminal attachment and current launcher assumptions increase lifecycle risk. WT as presentation alone would score much better.
- **D:** buys simultaneous visibility at substantial desktop and maintenance cost.
- **E1:** strongest immediate improvement with limited execution risk; provides no steering by itself.
- **E2:** potentially excellent owner experience; daemon ownership and termination behavior remain decisive unknowns. Supplied memory measurements show meaningful additional overhead.
- **E3:** useful remote access, weak primary station interface, and a shared registration/auth dependency. The observed `/login` correlation supports caution, not a universal causal guarantee.
- **E4:** best balance if delivery semantics are verified. A queued note is less powerful than arbitrary immediate interaction, which explains S=4.
- **F:** good visible interaction after transfer, but weak integrity as specified and extra interruption/configuration/cache boundaries.

Most token scores are deliberately identical. **Visibility is largely orthogonal to token economics.** F earns the lower score because its ordinary interaction path adds repeated recovery transitions.

I would not average these into an unconditional winner. First require C to pass. Then weight **visibility and steering at least as heavily as implementation convenience**. Otherwise the scoring quietly answers the engineer’s question instead of the owner’s.

## 5. Recommendation, migration path, and ranking

### Change the recommendation

Replace “keep it headless, then maybe take the wheel” with:

> Preserve the current supervised execution contract while delivering a persistent station window. Add durable queued notes as the normal steering mechanism. Evaluate native attachment or supervised interactive execution for direct control. Reserve stop/resume takeover for cases that actually require ownership transfer.

That keeps the justified caution without making the owner wait for permission to want the feature already requested.

### Concrete migration path

**1. Strengthen the two existing recovery items before implementation finishes.**

Do not file duplicates. Add the shared error classification, prelaunch session identity, exclusive ownership, repository validation, unique resume execution IDs, accounting rules, and cumulative budgets.

Fix the per-session activity lookup. Make the launcher’s effective cgroup and memory bounds observable. For unattended pipeline launches, a failed scope setup should fail the launch rather than continue unbounded behind a red message.

Keep the distinct diagnostic-consult rerun verb in the Relentless item; session resume does not solve attribution holds whose evidence or question must change.

**2. Deliver the owner’s station window immediately.**

Use the old FOUNDRY rectangle through a new supported viewer profile. Create stable tabs once.

Each station should show:

- Station and current item.
- Role, attempt, execution, and short session identifier.
- Running, waiting for account, holding a tool, idle, failed, or owner-held.
- Latest action and expandable output.
- Event age and connection health.
- Last completion, so an idle station does not look abandoned.

Closing this window must stop no work. Reopening it must start no LLM sessions.

Keep RUNNING_NOW as a secondary summary. Its existence does not remove the need for a usable station display.

**3. Probe steering before investing in F.**

Use one disposable builder clone and a harmless external-operation simulator.

Compare:

- CLI streaming input or the Agent SDK.
- Native background attach under verified bounds.
- B*: supervised interactive Claude in tmux.

Test notes during tools, interruption, daemon reuse, terminal loss, recovery, and session collisions. Include one pinned-SHA checker case.

Choose based on measured behavior and owner use, not which prototype produces the nicest screenshot.

**4. Ship queued notes first.**

The owner types into a station’s note field. The controller durably binds the note to an item and intended execution, then shows its delivery state.

On station reassignment, an unsent note should remain associated with the original item or ask for explicit retargeting. It must not silently follow “Builder 3” into unrelated work.

For judges, owner input that changes acceptance criteria or evidence invalidates the current judgment context. Record that explicitly.

**5. Add direct control only after the ownership protocol passes failure tests.**

Prefer attachment to the already-running process where that preserves the required controls.

If F remains necessary, implement it as a controller operation:

`running → handover_requested → quiescing → settled → owner_active → return_requested → validating → running`

Every intermediate state needs restart reconciliation. A journal annotation alone is insufficient.

Do not automatically seize control back because the owner was quiet. Distinguish a disconnected display from an abandoned ownership lease.

**6. Run a bounded trial and retain rollback.**

A week is reasonable after the failure tests, but passive observation is not enough. Exercise disconnects and restarts during the trial.

The flag should switch execution adapters or disable steering without losing queued notes, session records, or clone ownership. The owner should see a simple control surface; the implementation should absorb the operational complexity.

### Ranking

For the **eventual watch-and-steer product**, subject to the safety gates:

1. **E4 + E1:** supervised workers, live station views, durable queued input.
2. **B*, the improved B:** supervised interactive workers in tmux, if direct interaction proves materially better.
3. **E2:** native background sessions, if daemon placement, stop semantics, and accounting pass.
4. **E1 alone:** best immediate deployment, but incomplete against the steering request.
5. **Hardened F:** useful explicit takeover, not the normal note path.
6. **A alone:** essential recovery foundation, inadequate final interface.
7. **C as directly hosted interactive workers:** useful presentation, weaker execution architecture.
8. **E3 fleet-wide:** supplementary remote access rather than the primary design.
9. **D:** retain only for temporary side-by-side debugging.

**Deployment order differs from product ranking:** recovery fixes and E1 first; steering experiments immediately afterward; E4 if its semantics pass. **F as currently specified should not ship.**

## Disagreements with the author

- **The owner’s steering request is already a requirement.** It should not depend on proving demand through a watch-only week.
- **Headless execution is not uniquely compatible with systemd supervision or structured records.** The comparison confuses the current implementation with architectural necessity.
- **The $4.4 figure measures prior estimated consumption, not recoverable savings.**
- **Six ended terminal sessions do not establish Windows Terminal instability.**
- **Tmux receives an unfair hearing because it is coupled to screen-scraped supervision.**
- **Native background sessions are not inherently outside cgroup control.** Daemon creation and reuse determine placement.
- **F is substantially riskier than its row and M estimate imply.** Ownership, cleanup, external effects, and stale supervisors dominate its implementation.
- **Queued steering should precede takeover.** It addresses ordinary creative direction with fewer disruptive transitions.
- **Section 7 needs a recovery state machine and repository/effect reconciliation.** `--resume` plus “continue” is not a sufficient standard.
- **The comparison should prioritize owner effort and correct steering alongside engine safety.** Preserving the existing launch shape is valuable, but it is not the objective.