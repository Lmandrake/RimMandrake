# Seeing, steering and resuming pipeline agents: headless vs visible (design pass, 2026-11-04)

Status: DESIGN, v1 (Claude, BENCH seat), before GPT review. Revised version: section 9.
Ordered by: the Conductor for the owner, 2026-11-04. No code or unit changes come from this document; the owner decides first.
Evidence scratch: `D:\ClaudeWork\rimmandrake\agent_visibility\` (facts.md, outage_runs.txt).

Every factual claim is tagged **[M: source]** (measured, with file:line or command) or **[A]** (assumed, not yet checked).

## 1. The owner's question

> "So clearly we need to establish a standard 'resume from loss of tokens' action. The messages to hestia, emergency, and server were pointless waste and should not be done again. But if there's a way to capitalize on suspended operations, build/fix/judge agents, test pilots, etc. that could be useful. If we made them non-headless this would be possible I take it? That would also allow me to inspect them trivially too. Is there a disadvantage to using visible terminal agents as opposed to headless? It could be nice to have the pipeline be a single window where foundry used to be with tabs representing the various build stations that I can check on visually without token usage. I might even be able to type helpful things in one from time to time that I can't do now."

Three separable needs:
1. **Resume**: pick suspended pipeline work up where it stopped once tokens return.
2. **Watch**: see each station at zero token cost, in one place (FOUNDRY's old spot).
3. **Steer**: occasionally type something into a running station.

A key finding up front: **resume does not need visible windows.** Headless `claude -p` sessions resume fine (section 3). Visibility is worth choosing for watch and steer only.

## 2. How agents run today

| Fact | Source |
|---|---|
| Relentless starts each Builder/Judge/consult run as a transient systemd user unit `rm-relentless-<kind>-<sha10>-g<gen>`, running `claude_bounded.sh -p <msg> --output-format json --dangerously-skip-permissions --agent rm-builder`, with RuntimeMaxSec and an ExecStopPost wrap-up | [M: relentless.py:2405-2442, role_launch.py:2058-2093, relentless.py:2866-2867] |
| Its stdout is ONE JSON object written at the end, to `/home/mandrake/rm/relentless/store/runs/roles/<unit>.json` (6547 files there today). While it runs, the only live trace is the session transcript `~/.claude/projects/<clone-path-slug>/<session>.jsonl` | [M: relentless.py:2859-2863, relentless.py:2489-2500 `activity()`, `ls runs/roles \| wc -l`] |
| Relentless does not pin `--session-id`; the id is still recorded inside the result JSON (`session_id`). Dispatcher role runs DO pin one (uuid4) | [M: role_launch.py:2066, 2119; relentless.py:5176-5180] |
| Memory: each claude in its own scope, MemoryMax 10G, swap 2G, tool sub-cgroup 6G; all seats under `claude-seats.slice` 24G / swap 8G. VM has 35 GB, 14 cores | [M: claude_bounded.sh:89-92, claude-seats.slice, `free -g`, `nproc`] |
| An idle interactive claude is 0.21-0.44 GB RSS. A seat with 3 background (`--bg`) sessions measured 2.81 GB (daemon 0.33, 3 pty-hosts 0.59, 3 sessions 1.24) | [M: `ps` now; claude_bounded.sh:76-80] |
| Relentless stall rules: `stale_s` 1500 s of no transcript write, `launch_grace_s` 240, `run_max_s` 3600, `check_max_s` 1800 | [M: relentless_rules.json:62-63, relentless.py:3485-3491] |
| The "600 s silence kill" is Claude Code's own subagent stall watchdog (Test Pilots are subagents); it does not apply to `-p` units | [M: Utils/slot_rules.json helpers._doc; .claude/agents/rm-testpilot.md] |
| Limits: 8 workers, 16 clones / 70 GB | [M: relentless_rules.json max_workers; CLAUDE.md:275] |
| Test Pilots are `rm-testpilot` subagents (maxTurns 300) started from an interactive window when the Dispatcher prints a route | [M: rm-testpilot.md header; dispatcher.py:392] |
| Status lives on RUNNING_NOW.md, rebuilt every minute by `rm-running.timer` (197 KB now; shows "Relentless 0/6", "TOKEN PAUSE ON") | [M: `systemctl --user cat rm-running.service`, the page] |
| Visible machinery: `launch_fleet.ps1` places WT windows by literal rects (FOUNDRY was X+1899, Y+901, 1930x1151 on the 3840x2160 @200% display), decides live vs dead by reading terminal text through UI Automation (measured 11 fleet windows, 6 dead at a prompt), and ends with `SetForegroundWindow` on CONDUCTOR | [M: launch_fleet.ps1:217, 62-73, 312-316] |
| `seat_loop.sh` relaunches a seat inside its own tile after a Dispatcher restart | [M: seat_loop.sh:1-25] |
| tmux 3.6 is installed and already hosts Claude: SteveDesktop's seats live in tmux sessions, probed with `tmux capture-pane`; `rc rescue` / `rc server` run claude in tmux | [M: `tmux -V`; ops_watch.py:758-762; claude-remote-control SKILL.md:197-203] |
| Remote Control: every machine-wide RC drop on record was a `/login` in one window; `--remote-control` at launch is recovery, not immunity | [M: claude-remote-control SKILL.md:67-86] |
| Claude Code 2.1.311 has native background sessions: `--bg`, `claude attach`, `claude logs`, `claude stop`, `claude respawn`, and `claude agents` (an agent view; `--json` lists interactive and background sessions). The Dispatcher's dead-window recovery already uses `claude_bounded.sh --bg --resume <session>` | [M: `claude --help`, `claude agents --help`, dispatcher.py:118-123] |

## 3. What the outage actually cost, and what resume can and cannot do

- The account hit its weekly limit; the outage ran 14:47Z-20:07Z [M: infrastructure/state/items/RELENTLESS_RESUME_BUILD_ACCOUNT_LOST_RUNS.md].
- Relentless journal: 45 `account_lost` endings (14:50:35Z-19:36:50Z), 14 `launch_fail`, 9 jam alarms [M: journal.jsonl count].
- Of the run results that read "You've hit your weekly limit", **48 died with zero usage** (1 turn, $0: relaunches into a closed account), and **3 died after real work**: a worker 63 turns / $3.19, a worker 19 turns / $0.93, a checker 2 turns / $0.29 [M: outage_runs.txt]. Their transcripts are still on disk [M: `ls`]. So the context resume could have saved today is about **$4.4 of work across 3 runs**; the rest needs no resume, only a quiet wait.
- Trap: a `-p` run that hits the limit reports `subtype: "success"` with the limit text as its `result` [M: runs/roles/*.json]. A resume detector must read the text or the API error, not the subtype.
- `claude -p --resume <id> "<prompt>"` continues a print session and keeps the same session id [M: test in the scratchpad: told to remember PELICAN-42, the resumed run answered PELICAN-42, same id]. The resume must run from the same working directory (transcripts are filed by cwd) [A, strongly implied by the path layout].
- An interactive window that hits the limit just stops: the transcript ends on "You've hit your weekly limit" and nothing follows until a human types [M: 3 transcripts in ~/.claude/projects/-home-mandrake-rm-bench, e.g. a55c0c71 at 17:01:48Z]. **So a visible window does not resume itself either**; somebody still has to poke it, and that somebody should be the pipeline.
- Two items already filed today implement resume for Relentless runs and for Dispatcher role runs: `RELENTLESS_RESUME_BUILD_ACCOUNT_LOST_RUNS`, `ROLE_RUNS_BUILD_RESUME_AFTER_ACCOUNT_LOSS` [M: infrastructure/state/items/]. Section 7 is the standard they should both meet; it does not file new work.

## 4. The approaches

**A. Fully headless, as now, plus a resume verb.** `claude -p` units; resume via `-p --resume <session>`; the owner sees RUNNING_NOW only.

**B. tmux.** Each worker runs interactive claude (via claude_bounded, which makes its own memory scope) in a tmux window of one tmux session `pipeline`. One WT tile attaches it; a status bar lists stations. Supervisor reads screens with `capture-pane` and sends keys with `send-keys`.

**C. One live WT window with tabs** in FOUNDRY's old spot: a tab per station (Builder places 1-8, Judge, Operations, Designer, Test Pilot), each tab running interactive claude.

**D. Stacked non-tabbed terminals**: one WT window per station, tiled or stacked.

**E1. Headless with a live read-only viewer.** Workers stay `-p` units. A small renderer (`rm-watch <place>`) tails each station's transcript JSONL and prints it human-readably (assistant text, tool calls one line each, results truncated). One WT window in FOUNDRY's spot holds a tab (or one tmux session with a pane) per place, each running the renderer. Watching costs zero tokens; nothing about the workers changes.

**E2. Claude Code native background sessions** (`--bg`; watch/type with `claude attach`, list with `claude agents`). Built in and already used for window recovery.

**E3. Remote Control on every worker.** Each worker registers with claude.ai/code so the phone can watch and type.

**E4. Headless with a live inbox.** Workers launched with `--input-format stream-json` and a pipe held by the supervisor, so a note the owner types is delivered into the running session as a user message, and the record shows it [A: whether a message sent mid-turn is queued for the next turn needs a probe].

**E5. A web page fed by transcripts**: the E1 renderer as an HTML page (local or behind the existing phone route), one panel per station.

**F. Hybrid "take the wheel".** E1 for watching. To type, the owner presses a key in a station's tab: the supervisor parks the item (`held_by_owner`), stops the unit at its next safe point, and opens `claude --resume <session>` *interactively* in that same tab, so he is talking to the very worker with all its context. When he exits (or says "hand back"), the pipeline relaunches `-p --resume <session>` with a hand-back prompt and the item continues. His words stay in the transcript; the item journal records that he joined.

## 5. Comparison

Cost scale for build: S = under a day of agent work, M = 1-3 days, L = a week or more [A: estimates].

| | A headless+resume | B tmux | C WT tabs | D stacked WT | E1 viewer | E2 `--bg` | E3 RC all | E4 inbox | F hybrid |
|---|---|---|---|---|---|---|---|---|---|
| Resume after outage | Yes, by the pipeline (`-p --resume`) | Yes, but by `send-keys "continue"`, or a fresh resume in the pane | Only by typing into each tab, or by keystroke injection into WT (fragile) | Same as C | Same as A | Yes (`--bg --resume`, proven in the Dispatcher) | Phone poke only | Same as A, plus "continue" via the pipe | Same as A |
| Zero-token watching | RUNNING_NOW summary only | Full live screen | Full live screen | Full live screen | Full live stream (rendered) | `claude attach` / `claude logs` | Phone / web view (zero tokens) | As E1 | As E1 |
| Owner types into a worker | No | Yes, any time | Yes, any time | Yes, any time | No | Yes (`attach`) | Yes, from the phone | Yes, as a queued note | Yes, by taking the item over |
| Effect on determinism / metering / record | Clean: one prompt, one result JSON, structured verdicts (`--json-schema`), metered from the result | Interactive mode has no result object: end-of-run, verdict and tokens all read from the transcript; his typing is unrecorded outside it | As B | As B | Clean, as A | As B, plus a daemon between the unit and claude | As B, plus RC registration churn | Clean if notes are logged by the supervisor | Clean while headless; the owner's stretch is a marked interval in the item journal |
| Crash / kill | systemd unit: `alive`, `stop`, reap, RuntimeMaxSec all built on it [M] | tmux server is one process: a crash or `kill-server` ends every station; claude itself sits in its own scope if launched through claude_bounded | A WT crash or a stray close takes every tab | One crash takes one station | As A; a viewer crash loses nothing | Sessions live under the claude daemon, not under the unit: stop/alive/reap must be rewritten around `claude stop` | As B | As A, the pipe adds a new failure (writer dead) | As A |
| Memory / CPU per station | ~0.2-0.4 GB claude [M for interactive, A for `-p`] | Same + TUI render; tmux ~10 MB | Same + WT renderer per tab (Windows side) | Same + one WT process per window | Same as A + tiny renderer | +~0.2 GB pty-host per session, +0.33 GB daemon [M] | Same as B | Same as A | Same as A |
| 600 s / stale watchdog | Unchanged (stale_s 1500 reads transcript mtime) | Unchanged if the supervisor keeps reading transcripts | Same | Same | Unchanged | Same | Same | Unchanged | Unchanged; paused while he holds the item |
| Screen clutter | None | One tile | One tile | Up to 12 tiles | One tile | None (attach on demand) | Phone list grows by up to 12 entries | None | One tile |
| Owner on the phone | RUNNING_NOW | SSH + tmux attach (Termius already set up) | Nothing (WT is desk-only) unless RC | Nothing | Page or SSH + tmux | SSH + `claude attach` | Yes, native | Page | Page or SSH; take-over via RC on the resumed session |
| Owner AFK | Runs | Runs; risk of a stray keystroke when he returns | Runs; tabs can grab focus on launch | Each new window can grab focus | Runs | Runs | RC drops fleet-wide on any `/login` [M] | Runs | Runs |
| Restart on reboot | Timer relaunches (fresh or resume) | tmux dies with the VM; the supervisor rebuilds the session | WT layout must be rebuilt by launch_fleet | Same, x12 | Viewer tab re-opened by launch_fleet; workers as A | `claude respawn --all` | As B | As A | As A |
| Known failure modes | None new | send-keys into a pane that is at a prompt, a menu or a permission dialog; screen-scrape liveness | Focus stealing on new tab; UIA liveness misreads (6 of 11 dead today); keystroke injection into WT | Same as C, times 12 | Renderer lags or mis-renders (cosmetic) | Daemon outside the unit's cgroup and RuntimeMaxSec; less control | The RC drop; 12 more registrations to lose | Mid-turn queuing semantics unknown | The handover itself (stop at a safe point) |
| Build cost vs what exists | S (resume items already filed) | L (supervisor rewrite: launch, alive, end detection, metering, verdict capture) | L+ (as B, plus WT tab automation that does not exist) | L+ | S-M (a renderer + a launch_fleet profile) | M-L | M (and fights the RC rules) | M | M (E1 + a take-over verb) |

## 6. Recommendation (v1, before GPT)

1. **Keep the engine headless (A).** Everything that makes the pipeline trustworthy hangs on a `-p` unit: one result object, schema-checked verdicts, unit-based alive/stop/reap, RuntimeMaxSec, cost from the result. Visible interactive workers (B, C, D) would trade that for a screen, and would still not resume on their own (section 3).
2. **Build the standard resume action (section 7)** through the two items already filed.
3. **Build E1, the zero-token viewer, in FOUNDRY's old spot**: one WT window, one tab per station, each a renderer of that station's live transcript. Use tmux inside it (one session, one window per station) so the view survives a WT crash and also opens from the phone over SSH. Never steal focus: the window opens unfocused and only at fleet launch.
4. **Then F, "take the wheel"**, if he finds he wants to type. It gives him the full "type into a worker" ability without making every worker interactive: one item at a time, recorded, and the pipeline knows it is his.
5. Not recommended: C and D (desk-only, focus stealing, WT is the least reliable part of the fleet today), E3 (multiplies the RC drop), E2 as the engine (moves processes out of the units' control). E4 is a possible later refinement of F if a probe shows mid-turn notes queue cleanly.

Migration: (1) resume items land; (2) `rm-watch` renderer + one launch_fleet tile, behind a schedule flag, watch-only, for a week; (3) metrics in section 8 read; (4) take-the-wheel verb, if he used the viewer and still wanted to type; (5) retire nothing: RUNNING_NOW stays the status page.

## 7. Standard "resume from token loss" action (spec)

**Scope.** Only *suspended pipeline runs*: Relentless workers, checkers (Judges), consults and stages; Dispatcher role runs (Operations, Designer, Conductor role runs); timer LLM jobs (findings judge). **Never** an idle interactive window (HESTIA, EMERGENCY, Server, CONDUCTOR, SteveDesktop) and never a broadcast "continue" [owner 2026-11-04, memory no-poking-idle-windows-after-outage.md]. Test Pilots are subagents of an interactive window: they are resumed by their parent re-running them, not by this action.

**Trigger.** A run ended on the account (limit text in the result, `usage_limit_reached`, 429, or an auth error), recorded as `account_lost`.

**Classify each lost run:**
- *Zero-usage* (1 turn, no output tokens): nothing to resume. Requeue normally once the account answers. (48 of 51 today.)
- *Real usage* and transcript present, clone still at the same path: **resumable**. Record `session_id`, cwd, unit template, model, item, gen.
- *Real usage* but transcript or clone gone: fresh run, with a note "your predecessor was cut off by the account after N turns".

**Wait, do not churn.** While the account is out, launch nothing (the breaker): today 48 runs launched into a closed account. Wake on the known reset time (the limit text gives it, e.g. "resets 12pm America/Los_Angeles") plus a margin, and confirm with one cheap probe before relaunching anything.

**Resume.** Relaunch through the same unit template, slice, memory bounds and walls, in the same cwd, with `claude -p --resume <session_id> "<continue prompt>"`. Continue prompt: "Your session was cut off by an account usage limit at <time>; tokens are back. Re-check anything time-sensitive (git status, the game, locks you held) and continue where you were." Stagger resumes (one per tick) so a returning account is not hit by eight cold prefills at once.

**Bounds.** One resume per run; a resumed run that dies on the account again is classified afresh. Counts no strike, no failed-attempt, no role failure alarm. Cost note: a resume re-sends the whole context once uncached [A: the prompt cache will have expired after hours]; still cheaper than redoing the turns.

**Record.** Journal/ledger line per resume: item, old unit, session, turns preserved, cost of the resumed run. RUNNING_NOW shows "resuming N runs at <time>".

## 8. Metrics of merit (v1)

| Metric | How measured | A | E1+A | F |
|---|---|---|---|---|
| Work recovered after an outage (share of lost turns resumed, not redone) | lost-run census vs resumed runs | target 100% of resumable | same | same |
| Launches into a closed account | journal `launch_fail`/zero-usage deaths during an outage | today 48; target 0-1 | same | same |
| Minutes from account reset to first resumed run | journal timestamps | target < 10 | same | same |
| Token cost of watching | tokens per hour of watching | 0 (page) | 0 | 0 |
| Seconds from a worker action to it being visible | transcript write to screen | ~60 s (page) | < 5 s [A] | < 5 s |
| Owner interventions possible per day | count | 0 | 0 | unlimited, one item at a time |
| Stations lost to one crash | blast radius | 1 | 1 (viewer: 0 work) | 1 |
| Extra memory | GB at 8 places | 0 | ~0.1 [A] | ~0.1 + one interactive session while held |
| Focus steals per day | owner report / launch audit | 0 | 0 target | 0 target |
| Build cost | agent-days | S | S-M | M |

## 9. Revision after GPT

GPT (gpt-6.1-sol, effort high) reviewed v1; its answer is verbatim in `gpt_review.md`. Sections 1-8 are kept as written so the change is visible; this section supersedes 6, 7 and 8 where they differ.

### 9.1 What v1 got wrong (accepted)

| v1 claim | Correction | Status |
|---|---|---|
| "Resume could have saved ~$4.4 today" | $4.4 is what the 3 interrupted runs had *already spent*, not what a resume saves; a resume also re-pays an uncached prefill of that context | Accepted. The honest statement: 3 runs held work worth keeping; the saving is unmeasured until a resume is metered (metric T) |
| "Everything that makes the pipeline trustworthy hangs on a `-p` unit" | The trust comes from supervision (systemd scope, bounds, a structured end record), not from the one-final-JSON shape. `--output-format stream-json` keeps a structured record *and* gives a live event stream | Accepted |
| "`--bg` sessions live outside the unit's cgroup" | Too categorical: placement depends on where the daemon is created and whether it is reused. Unmeasured | Accepted, now [A], needs a probe |
| "WT is the least reliable part of the fleet (6 of 11 dead)" | 6 ended sessions are 6 windows whose claude exited (logout, outage, closed), not 6 WT failures | Accepted |
| B and C cost L/L+ | They are costly only if the supervisor keeps scraping screens. B* (interactive claude in tmux, pane placed in its worker's bounded scope, end record from the transcript) is a fairer variant | Accepted, B* added |
| F "take the wheel" is M | Handover is a real ownership transfer: quiesce, settle the old process, external effects, stale supervisors, hand-back validation. That is a state machine, not a verb | Accepted: F is L and must not ship as specified in v1 |
| "Watch-only for a week, then decide whether he wants to type" | He already asked to type. Steering is a requirement, not a hypothesis to prove | Accepted |
| Section 7 is enough as `--resume` + "continue" | Needs error classes, identity pinned before launch, ownership freeze, repo revalidation, idempotent state, a boundary-setting prompt and de-duplicated accounting | Accepted (9.3) |

Checked after the review (MEASURED this pass):
- `Relentless.activity()` (relentless.py:2489) takes the newest mtime of the top-level entries in the clone's whole transcript directory. So (a) any other session in that clone keeps a silent worker looking alive, and (b) a worker whose activity is inside a subagent (`<session>/subagents/*.jsonl`) looks silent, because appending to a file in a subdirectory does not touch the top-level entry. GPT flagged (a); (b) is new. Both are fixed by reading the run's own session file plus its subagents.
- `claude_bounded.sh:127` overwrites `TMPDIR` and `CLAUDE_CODE_TMPDIR` with the per-seat directory, so the per-run temp a role launch sets does not survive. A resume must look at real artifact paths, not assume the run's temp directory holds them. (GPT's point, confirmed.)

### 9.2 Where I keep v1 against GPT

- **Watching must stay separate from the worker.** GPT agrees (execution / control / presentation). Closing the station window stops no work; opening it starts no session.
- **E3, Remote Control fleet-wide, stays rejected as the primary design.** GPT ranks it 8th: RC remains a per-session extra.
- **D stays a debugging layout only.** GPT ranks it last.
- **No broadcast "continue" and no poking idle windows**: an owner ruling, unchanged.

### 9.3 Resume action, hardened (replaces section 7 where they differ)

1. **Classify the error, don't pattern-match one string.** The classes are: account quota (weekly limit), short rate limit, auth failure, network, and context/turn/budget limit. Each has its own handling. Never infer it from tool output that merely quotes "429". A missing or malformed result is *unknown*, never success and never zero usage.
2. **Pin identity before launch.** Every Relentless run gets `--session-id <uuid4>`, as role runs already do (role_launch.py). Record the item, attempt, strategy generation, execution id, session id, transcript path, clone, branch, base sha, model and unit. A resume gets a *new* execution id and unit name under the *same* attempt and generation.
3. **"No useful continuation state" replaces "zero usage".** A run is fresh-requeue, resumable, or unknown (reconcile transcript, repo and external operations first).
4. **Freeze, then revalidate.** Keep the clone reserved. Settle the old scope. Before resuming, confirm the item is still open and this attempt is current, the clone was not reused, and HEAD/dirty state is explained. Checkers additionally confirm that the judged sha and evidence are unchanged. Classify each `pre_launch` step as repeat, validate-only, or preserve, so a resume does not silently regenerate the evidence the judge is reasoning about.
5. **Reset time: parse conservatively.** Use an IANA zone and a dated resolution. Reject an ambiguous parse rather than schedule a precise-looking wrong time (today: noon Los Angeles = 20:00Z).
6. **One breaker for Relentless, Dispatcher and timer LLM jobs.** Keep the non-LLM work running. After the reset: wait a margin, run one canary for that model lane, then admit gradually: initially one every 15 s and at most 2 restoring at once [A: starting values]. Reopen the breaker on new quota evidence.
7. **Recovery prompt sets boundaries.** It names the item, attempt and interruption, and points to a short recovery record. It says to verify the repo and task state, to check whether the last interrupted operation completed before repeating it (no blind re-commit, re-publish, deploy or game command), to reacquire locks and the bridge, and to stop with a structured hold reason if superseded or uncertain.
8. **Idempotent.** The states are `account_suspended → waiting → validating → launching → active`, and every tick recognises a resume already started. Allow one active continuation per attempt, bounded retries per outage episode, and a bounded cumulative active time (outage time is excluded, and walls never reset to a full fresh hour).
9. **No penalties.** No strike, no approach-change counter, no failed verdict, no role alarm. Earned strikes are not erased.
10. **Accounting.** A resumed result's totals include earlier spend. Record session cumulative and execution delta separately and never sum them.

These belong in the two filed items (`RELENTLESS_RESUME_BUILD_ACCOUNT_LOST_RUNS`, `ROLE_RUNS_BUILD_RESUME_AFTER_ACCOUNT_LOSS`) as acceptance text. No new item.

### 9.4 Recommendation (final)

Product target: **E4 + E1**. Workers stay supervised units. One named Pipeline window sits in FOUNDRY's old spot, with stable station tabs showing live, zero-token views. A **"send a note"** box per station delivers his words into the running session at its next turn boundary, durably and recorded. **"Take control"** is a separate, later operation.

Deployment order (build cost: S < 1 agent-day, M 1-3, L a week+):

| # | Step | Cost | Gate |
|---|---|---|---|
| 1 | Harden resume (9.3) inside the two filed items; fix `activity()` to read the run's own session + subagents; pin `--session-id` for Relentless | M | synthetic outage test: every safe case resumes, every unsafe case holds |
| 2 | Pipeline window: `wt -w Pipeline` at the FOUNDRY rect, never foreground, one tab per station running a transcript renderer (tmux inside, so it survives a WT close and opens from the phone via SSH) | S-M | metric F = 0 focus changes in 100 relaunches; V p95 lag ≤ 2 s |
| 3 | Steering probe on a throwaway clone: stream-json input vs Agent SDK streaming vs B* tmux vs `--bg` attach (bounds, stop semantics, `--bg --resume` copy risk) | S | measured delivery semantics, cgroup placement |
| 4 | "Send a note" via the winner of 3; notes bound to item+execution, never follow a station to new work; a note to a Judge that changes criteria invalidates its judgment | M | metric S: 100 tagged notes, 0 wrong-item deliveries |
| 5 | "Take control" as a controller state machine (`running → handover_requested → quiescing → settled → owner_active → return_requested → validating → running`) | L | only if notes prove insufficient in a week's use |

Not built: C as worker host (WT stays presentation only), D (debug layout only), E3 fleet-wide.

### 9.5 Metrics (replaces section 8)

GPT's set, all targets *proposed*, none measured: R recovery correctness and latency, V visibility lag, S steering delivery, C control integrity (gate: must pass before anything else counts), T token overhead of a resume (≤ 10 % versus uninterrupted, or a stated exception), H resource overhead (≤ 1 GB, ≤ 5 % CPU at 8 stations), F focus disturbance (0), O owner burden (no shell commands, ≤ 5 min/week repair), D delivery effort (viewer ≤ 2 days, steering pilot ≤ 3 more). Full table and per-approach scores: `gpt_review.md` section 4.
