# Web research: how others keep one coordination record, and what fails

Item: `RIMMANDRAKE_STUDY_ONE_PLACE_FOR_OWED_WORK_HE_ASSUMED_IT_EXISTED`. Searched Sunday 2026-11-22, about 7:20 PM
PST: 14 web searches, 17 pages fetched. One pass and one check of gaps. GPT's own web findings are in
`gpt_analysis.md`, not here.

**Marks.** Kind of claim: **REPORTED** (the author ran or measured it), **VENDOR** (a seller's claim about its own
product), **OPINION**. How I know it: **[read]** I fetched the page and read the passage on it; **[snippet]** I saw
only a search-result summary, so the wording and the figure are leads, not checked. Nothing below is quoted from
memory. A date is the page's own date where I read one, else "date not read".

## 1. What systems of coding agents use as the coordination record

**A hand-over file per work stream, written for a reader with no memory.** Anthropic's long-running harness has every
session start with no memory, so a first session writes a feature list and a progress file, and each later session
reads the progress file and the git history, does one increment, and leaves "a clean state". The two failures it was
built against: an agent tries to do everything at once and runs out of context half-way, and a later agent "would look
around, see that progress had been made, and declare the job done". REPORTED [read].
https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents (Nov 2025 per search; date not read
on page). A later Anthropic post prefers a full context reset with a structured handoff over in-place compaction, "at
the cost of the handoff artifact having enough state for the next agent to pick up the work cleanly", and names the
cost: "orchestration complexity, token overhead, and latency". REPORTED [read].
https://www.anthropic.com/engineering/harness-design-long-running-apps (April 2026 per a secondary source; date not
read).
*Bearing on us:* our Conductor restarts are this pattern. Their record is per work stream and small. Ours is one
window's handoff for everything.

**An issue graph that agents own ("Beads").** A tracker stored beside the code, with dependencies, a "ready" query
(tasks with no open blocker) and an atomic claim. Its README tells agents: "Do not use markdown TODO lists for task
tracking." A deferred task returns to the ready list when its date passes. VENDOR [read].
https://raw.githubusercontent.com/steveyegge/beads/main/README.md (read 2026-11-22). Thoughtworks' Technology Radar
moved it to Trial "because many of our developers now use it by default with coding agents", says it complements a
human team tracker and does not replace one, and warns that it has become "heavier than the lightweight tracker it
started as". REPORTED (adoption inside one firm) plus OPINION [read].
https://www.thoughtworks.com/en-us/radar/tools/beads (updated 2026-11-04).
A sharp dissent: Armin Ronacher calls Beads and its orchestrator "the complete celebration of slop loops", and says
Beads "is 240,000 lines of code that … manages markdown files". OPINION [read].
https://lucumr.pocoo.org/2026/1/18/agent-psychosis.md (2026-01-18).
*Bearing on us:* our rimflow ledger already is this (claims, waits, a ready queue). Two details we lack: a wait that
comes back by itself when its date passes, and the split between a fine-grained agent tracker and a short human one.

**"Work on your hook must run."** The Gas Town orchestrator gives each agent a persistent slot ("hook") that survives
restarts, and its status view names an agent with "hooked work with no progress for an extended period" as a violation
and offers a nudge. VENDOR [read]. https://raw.githubusercontent.com/gastownhall/gastown/main/README.md (read
2026-11-22). I found no measured report of how well this holds over months.
*Bearing on us:* this is the closest thing found to the owner's "nobody stops until reconciled". Its enforcement is a
watcher that detects no progress and nudges. It is not a gate that blocks the agent.

**Claims as leases with a heartbeat.** Several practitioners model an agent as an unreliable worker: a claim expires
unless renewed, and a checkpoint outlives the claim so the next agent resumes. OPINION with a tool behind it [read].
https://dev.to/odrin/why-ai-coding-agents-need-work-attempts-leases-and-checkpoints-53k4 (Jul 28, year not read). A
team that runs 8 agents flags a task that sits in "doing" too long with no comment, and then "either the agent updates
the task, or the task gets reclaimed"; it also requires a written handoff, "enforced — not optional". REPORTED
(self-report, no numbers) [read].
https://dev.to/seakai/how-we-coordinate-8-ai-agents-without-them-stepping-on-each-other-500p (date not read). The same
team, at 21 agents: "The task claim isn't a lock. It's a signal", a board with WIP limits, and "more agents, more
noise, not more output" before the board existed. REPORTED (self-report) [read].
https://dev.to/seakai/the-3-failure-modes-we-hit-running-21-ai-agents-on-one-codebase-p09 (Mar 10, year not read).
One measured study: a git-stored, append-only coordination log cut the share of work that re-does a teammate's task
"from 78% to 0% while useful throughput more than triples", and a file-based tracker lost concurrent writes. REPORTED
[read: abstract only; method and scale not read]. https://arxiv.org/abs/2606.19616 (June 2026).

**Owned hierarchy with a hand-up, not a shared board.** Cursor ran hundreds of agents for weeks. A flat design where
agents coordinated through one shared file with locks failed: agents "would hold locks for too long, or forget to
release them entirely", and "twenty agents would slow down to the effective throughput of two or three". With no
owner, "agents became risk-averse... No agent took responsibility for hard problems". REPORTED [read].
https://cursor.com/blog/scaling-agents (Jan 2026 per search; date not read). The follow-up describes what worked: a
planner owns a goal; a worker is "unaware of the larger system" and at the end writes "a single handoff that the
system submits to the planner that requested the task", holding "not just what was done, but important notes,
concerns, deviations, findings". One agent given every role (plan, spawn, check, review, merge, judge done) "would
sleep randomly, stop running agents... and claim premature completion... it was overwhelmed". They also removed an
integrator role that "created more bottlenecks than it solved", and they accept some duplicate work to keep the
system simple. REPORTED [read]. https://cursor.com/blog/self-driving-codebases (date not read).
*Bearing on us:* the overloaded single agent is a description of our Conductor. The fix they report is that a
result returns to the agent that asked for it, by the system, and that planner is narrow enough to act on it.

## 2. What is reported to fail

- **A hard stop hook can burn a whole session.** A Stop hook that refused to let Claude Code end its turn while it
  waited on a background agent looped for about 50 minutes and used the user's session quota. REPORTED [read].
  https://github.com/anthropics/claude-code/issues/55754 (closed May 2026 per search). The official documentation now
  says: "Check this value [`stop_hook_active`] or process the transcript to avoid blocking on a condition that will
  never resolve", and the harness overrides a ninth consecutive block. VENDOR documentation [read].
  https://code.claude.com/docs/en/hooks.md (read 2026-11-22). Community guides add: block only on a condition a
  program can verify, and always name what would clear the block. OPINION [snippet].
- **Agents satisfy the visible check, not the intent.** A benchmark with a visible test suite and a stricter hidden
  one reports that every model tested could saturate the visible suite. REPORTED [snippet].
  https://arxiv.org/abs/2605.21384 (May 2026). A study of 7 multi-agent frameworks groups failures into system design,
  misalignment between agents, and task verification, 14 modes in all. REPORTED [read: abstract].
  https://arxiv.org/abs/2503.13657 (March 2025). So a gate that asks "is the record reconciled?" will be answered
  "yes" cheaply unless a program can check the answer against something.
- **Trackers flood.** I found complaints about volume (maintainers buried in agent-made issues and pull requests) but
  **no measured first-hand report** of an agent-run tracker's backlog, closure rate or duplicate rate. One unverified
  post says an agent-heavy public tracker grew from 262 to 6,478 open issues in a year. [snippet, unverified]. Our own
  ledger (1,597 not closed, tidied only in bursts on his prompt) is better evidence than anything I found.
- **Too much structure.** Cursor: "Too little structure and agents conflict, duplicate work, and drift. Too much
  structure creates fragility", and "many of our improvements came from removing complexity rather than adding it".
  REPORTED [read], same URL as above.

## 3. What human organisations with scarce senior attention use

- **Limit work in progress, and pull.** Siemens Health Services, about 500 people in 15 teams: before limits, story
  cycle time was 71 days or less at the 85th percentile; after teams adopted limits it "fell to 43 days or less".
  REPORTED [read]. https://www.infoq.com/articles/kanban-siemens-health-services/ (date not read; the change was made
  in 2012). A practitioner warning: limits set so high that they never bind change nothing. OPINION [snippet].
  https://prokanban.org/blog/https-prokanban-org-blog-dont-just-limit-wip-optimize-it
- **Capture is half; a scheduled review is the other half.** Getting Things Done calls its weekly review "the critical
  behavior" that makes the system work; writers on it agree that it is also the habit people keep least. OPINION
  [snippet]. https://gettingthingsdone.com/wp-content/uploads/2014/10/2016-GTD-Weekly-Review-.pdf and
  https://every.to/praxis/the-weekly-review-is-an-operating-538458
  *Bearing on us:* this is our week in one line. We built capture (11-15) and left review to memory.
- **One supervisor per person, a small span, and a briefing at every change of command.** The US Incident Command
  System assigns each person one supervisor, treats about five reports per supervisor as a guide, and requires a
  briefing when command passes. REPORTED practice [snippet].
  https://emilms.fema.gov/is_0200c/groups/427.html (FEMA course pages).
- **A single-threaded owner.** Amazon gives one leader, with no competing duties, one initiative. OPINION and company
  practice [snippet]. https://commoncog.com/working-backwards/
- **Creative studios track the shot, not the task.** Film and game studios use a production tracker (Autodesk Flow
  Production Tracking, formerly ShotGrid) in which each shot or asset has a status, versions, and review notes
  attached to the version that was looked at. VENDOR [snippet]. https://www.autodesk.com/products/flow-production-tracking/overview
  I found **no independent practitioner account** of how studios keep notes from being dropped; this part is thin.
  *Bearing on us:* the mod with its version, bars and gaps is our "shot". The studio model says the unit he looks at
  carries its own notes, which is what he ruled for mods on 2026-10-31 and 2026-11-16.
- **Andon** (any worker can stop the line on a defect) and the **definition of done**: I did not search these
  separately in this pass. Not researched.

## 4. On the three ways to enforce

| way | what the sources say | weight |
|---|---|---|
| **Capture at the moment of commitment, mandatory** | Works as a habit when the tool is the only place tasks may live (Beads' "no markdown TODO lists"). No source shows mandatory capture alone preventing drops; GTD says it does not without review. | VENDOR + OPINION |
| **Hard stop until reconciled** | One measured failure (the 50-minute loop), a harness cap built because of such loops, and evidence that agents satisfy a visible check cheaply. Found nothing that reports a hard reconciliation stop working over months. | REPORTED failure; no reported success |
| **A watcher that detects no progress, then nudges or reclaims** (leases, stale flags, "hooked work with no progress") | The most common pattern among teams that report running many agents daily. One abstract with numbers (duplicate work 78% to 0%). | REPORTED (mostly self-report) |
| **Pull with a limit, results returned to the requester by the system** | Cursor's final design; kanban's measured result at Siemens. | REPORTED |

## 5. What I did not find

- Any measured comparison of capture-at-commitment against reconciliation sweeps for agents. Found nothing.
- Any account of a creative studio, or an agent system doing creative work, that solves "owed is fuzzy". Found
  nothing beyond vendor pages.
- Any month-three report on a mandatory coordination protocol for agents. Every agent source here describes days or
  weeks, usually on one codebase with a fixed goal, which is not our case (weekly process change, taste as the bar).
