# FLEET_SUPERVISION.md — what the human looks at, and what must interrupt them

_Owner's ruling, 2026-08-14, after a load window was lost to five seats waiting on
each other. Written from four research sweeps: Anthropic's own multi-agent
guidance, what practitioners actually run, the human-factors literature on
supervisory control, and status-display UX. **Findings are cited only where they
changed a decision.** Where a widely-quoted number turned out to be wrong, that is
said plainly — three of them were._

## 0. ⚠️ How much to trust the numbers in this file

**The design decisions here do not rest on any single figure, and that is
deliberate.** Two research passes disagreed with each other about which primaries
were recoverable — several sit behind paywalls, and one is a scanned image with no
text layer.

| tier | what it means | examples |
|---|---|---|
| **firm** | verified from the primary, or a field study with a clean control | I-PASS (−23% errors, non-preventable events unchanged); Drew 2014 ICU alarm counts; Monk 2008 resumption lag; Parasuraman/Mouloua/Molloy 1996 re-engagement |
| **directionally solid** | the effect is standard and replicated; **do not quote the exact percentage** | probability-matching to alarm reliability; low-base-rate PPV collapse; the vigilance decrement's shape |
| 🔴 **known wrong** | in wide circulation and misstated | "23 min 15 s to recover from an interruption"; "40% productivity loss" |

⇒ **Argue from the mechanism, not from the decimal.** If a rule below only works
when a number is exactly right, the rule is wrong.

---

## 1. The human looks at THREE things. Everything else is pull, not push.

| band | question it answers | rule |
|---|---|---|
| **DECIDE** | what is blocked on me | **Always real by construction** — a human wrote it because a human must answer it |
| **game + instrument** | is the scarce resource in use, and by whom | One measured line, with its age |
| **burn-down** | are we winning | Changes least ⇒ **earns the least valuable screen position** |

**Band order is needs-me → in-flight → will-be-done → done.** Near-universal across
incident, CI and agent consoles, and the opposite of how a status doc is normally
written. `board.py` renders exactly this.

🔴 **Keep the green on screen.** Hiding passing work is measured to induce
"five failures and twenty-five failures look the same" blindness. Show done rows
as ratio, not detail.

---

## 2. The alert rules — an alarm you ignore is worse than no alarm

- 🔴 **ACTIONABLE, not merely true, is the test.** In one ICU study 88.8% of
  arrhythmia alarms were false — and among the *true* ones, 93% did not warrant
  treatment. **A correct alert nobody can act on still destroys the channel.**
- 🔴 **Never mix a certain signal with a guessed one.** People probability-match
  their response rate to an alarm's observed reliability, so a half-right band is
  obeyed half the time **and drags its neighbours down.** `DECIDE` and
  `MAYBE STUCK` are separate bands for this reason and must stay separate.
- **Dwell before firing.** `blocked` is the normal momentary state of a seat on a
  permission prompt. 90 s gate. **Tune the number, never delete the gate.**
- **Fire on the EDGE, not the level.** One notification per stall. A toast every
  refresh trains the owner to dismiss toasts, and the next real one dies with it.
- **Carry the reason, not a flag.** Showing the agent's reasoning is measured to
  raise performance *and* trust with **no** increase in workload or response time.

### 🔴 Interrupting the owner is CHEAP — so push immediately, do not batch

**The famous "23 minutes to recover from an interruption" does not say what it is
used to say.** Mark, González & Harris 2005 measured 25 min 26 s of *wall-clock
elapsed time* — including 2.26 other work spheres done in between — with a
standard deviation larger than the mean. The real cognitive figure is Monk,
Trafton & Boehm-Davis 2008: **resumption lag ~600 ms, asymptoting between 13 and
23 seconds.**

⇒ **Do not hoard interruptions to protect the owner's focus.** That trade was
being made against a number that is off by two orders of magnitude. A well-timed
push is nearly free; the cost of a badly-timed one is that it *stacks*.

---

## 2b. 🔴 The closing seat and the recording seat MUST be the same seat

**CREATE's finding, 2026-08-14, and it is sharper than the lesson it corrected.**

The board went stale within minutes of being built: two rows sat `open` while both
were already resolved, and PROJECT — the seat that owns the board — pushed another
seat to run them. The tempting diagnosis is *"hand-kept things drift, sweep more
often."* That is wrong.

> **It drifted because the seat that CLOSED the work and the seat that RECORDED it
> were different seats. Any ledger where those two differ drifts by construction,
> and no sweep frequency fixes it — a faster sweep only shortens the window.**

⇒ **A seat ticks its own row in `BOARD.md`, in the same commit that closes the
work.** Not a report to PROJECT, not a request. PROJECT still sweeps, but the sweep
is a backstop, never the mechanism.

🔴 **And tick it with the EVIDENCE, not just the state.** A row that reads `done`
and nothing else is the next stale row, because the seat reading it cannot tell
whether it may act on the result. L1 did not go `open → done`; it went to *"no
stern re-lay; one hull cell per thruster; roof map derived, not observed."* The
qualifier is the whole value: **derived** is not **observed**, and the next seat
needs to know which it is holding.

---

## 3. Rules for the seats

1. 🔴 **NEVER REPORT A PRECONDITION YOU CAN SATISFY.** If you can close the gap,
   close it and say so afterwards. This is the rule that cost a window: a map was
   one call and ~90 s away, and its absence was reported instead of ended.
2. 🔴 **THE OWNER'S WORD IS A GO, NOT A CLAIM TO FACT-CHECK.** "The game is live"
   means *begin*. Correct: *"no map yet — making one, ~90 s."* Reconcile reality to
   the instruction; do not argue the noun.
3. 🔴 **A MEASUREMENT LABELS STATE. IT NEVER GATES ANYONE.**
4. **Prefer loud failure to silent degradation.** "Automation wrong" hurts far more
   than "automation gone" — a confidently incorrect seat is worse than a dead one.
   ⇒ say "I could not measure this" rather than reporting a stale value as current.
5. **Set your status line when you change task.** `board.py say "..."`. Liveness is
   stamped for you by a hook; meaning cannot be.
6. **Take the instrument when it is free. Do not ask.** `gamestate.py take`.
7. 🔴 **Tick your own row in `BOARD.md` in the commit that closes it, with the
   evidence.** See §2b — this is the rule that keeps the board honest, and it is
   the only one no amount of sweeping can substitute for.

---

## 4. Rules for the owner — the parts only you can do

- 🔴 **Monitoring is NOT the restful job.** Vigilance is *resource-depleting*, not
  under-arousing: workload measures run high, cerebral blood flow declines track
  the performance decrement, and distress rises. Never treat "just watching the
  fleet" as the break between real work.
- 🔴 **Do one task yourself, periodically.** Returning a task to human control for
  ~10 minutes mid-session **significantly improved subsequent failure detection**
  in the automation-monitoring literature. It is the cheapest countermeasure known
  to complacency and it is the one nobody schedules.
- **A seat you must reject more than ~30% of the time is a net negative, not a
  slow positive.** Below ~0.70 reliability, automation measurably underperforms
  having none. Fix it or stop using it; do not tolerate it.
- 🔴 **THE RELIABILITY PARADOX — the fleet getting better makes you check less, and
  miss more.** Omission errors *rose* from **32.4% to 48.3%** as an aid's
  reliability rose from **0.87 to 0.98** (Bailey & Scerbo 2007). Complacency also appears **only under
  multi-task load** — which is your permanent condition — and it hits **experts
  exactly as hard as novices**, is **not cured by practice**, and is **not
  prevented by being told the aid is imperfect.** Only *exposure to real failures*
  reduced it. ⇒ **the more reliable these five seats become, the more deliberate
  your sampling has to be.** This is the one finding that gets worse with success.
- **Structured handover is the best-evidenced fix in the whole sweep.** I-PASS
  across 9 hospitals and 10,740 admissions cut medical errors **23%** and
  preventable adverse events **30%**, with **no increase in workflow time** — and
  non-preventable events unchanged, which is the control that makes it credible.
  ⇒ `gamestate.py release "what you left behind"` is not bookkeeping. **It is the
  intervention.** The next seat inherits your map.
- **Trust breaks fast and mends slowly** — and people distrust even a reliable aid
  after seeing errors *unless given an explanation of why the errors happen*. ⇒
  when a seat is wrong, the write-up of **why** is not optional politeness; it is
  what keeps the fleet usable.
- **3–5 agents is the supported ceiling.** Anthropic's own guidance: *"Three
  focused teammates often outperform five scattered ones."* We run five.

---

## 5. Known structural weaknesses — named, not hidden

- ⚠️ **Five seats share ONE working tree. This is the named anti-pattern.**
  Worktree-per-agent is the convergent answer across every orchestrator surveyed,
  and there is a filed Claude Code issue where 13 parallel agents produced **5
  commits and 8 failures** on `.git/index.lock`, after which cleanup deleted the
  uncommitted work. **Our mitigations are: explicit-path commits only, the blanket
  -stage hook, and never shelling to `git` from a status pane on a timer** — that
  last one is a documented cause of exactly this lock contention.
- ⚠️ **`BOARD.md` is hand-maintained and is the one part of the board that can
  lie.** It prints its own age for that reason. Everything else on screen is
  measured.
- ⚠️ **A parallel fan-out shares one quota, and the early agents can STARVE the
  late ones.** Measured here 2026-08-14: four research agents launched at once
  consumed the session's entire 200-call web-search budget, and the two that
  finished last had to fall back to slower routes and returned the thinnest
  results — on the two topics that were arguably most important. **Fan-out does
  not divide a shared resource fairly; it races for it.** ⇒ when a budget is
  shared and the topics are unequal, stage the important ones FIRST rather than
  launching all at once, and expect the tail of a wide fan-out to be degraded.
- ⚠️ **A finished background agent can re-report the same result repeatedly.**
  The same agent delivered four near-identical reports here; two were pure cost
  and one contradicted an earlier pass about which sources were verified.
  **Read the first, act on it, then `TaskStop` it.** Re-reads of the same
  material are where a duplicate finding turns into a duplicate decision.
- ⚠️ **Anthropic's guidance is that coding parallelises worse than research** —
  *"most coding tasks involve fewer truly parallelizable tasks"* — and that
  *"letting a team run unattended for too long increases the risk of wasted
  effort."* Both describe this project.

---

## 6. The tools

```bash
python3 src/RimMandrake/Utils/board.py --watch      # the pane. Never scrolls.
python3 src/RimMandrake/Utils/board.py say "..."    # a seat's current line
python3 src/RimMandrake/Utils/gamestate.py          # measured state + instrument
python3 src/RimMandrake/Utils/gamestate.py take     # free means take it
claude agents                                        # Claude Code's own fleet console
```

⭐ **`claude agents` is the supported surface and it already groups sessions
Working / Needs input / Idle, with a terminal bell and an `agent_needs_input`
notification.** `board.py` reads its JSON rather than reimplementing it, and adds
only what Claude Code cannot know: the project's own checklist and decisions.
**When the two disagree about a seat's state, `claude agents` is right.**
