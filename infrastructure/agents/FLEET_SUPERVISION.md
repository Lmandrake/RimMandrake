# FLEET_SUPERVISION.md — what the human looks at, and what must interrupt them

_Owner's ruling, 2026-08-14, after a load window was lost to five seats waiting on
each other. Written from four research sweeps: Anthropic's own multi-agent
guidance, what practitioners actually run, the human-factors literature on
supervisory control, and status-display UX. **Findings are cited only where they
changed a decision.** Where a widely-quoted number turned out to be wrong, that is
said plainly — three of them were._

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
  reliability rose from **0.87 to 0.98**. Complacency also appears **only under
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
