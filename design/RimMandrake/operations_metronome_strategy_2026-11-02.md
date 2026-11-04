# Operations: the metronome, the memory, and Groundhog Day

Strategy, written 2026-11-02. It sits on top of `operations_design_2026-11-01.md` ("clockwork gatherers, one judge") and
changes its shape, not its rules: the alarm-limit guard (§4 there), the Marker lock (§6), the report (§7) and orders (§8)
stand. Counts are measured on 2026-11-01 unless marked ESTIMATE. Your words today: Operations is *"about watching and
trending everything to keep an overall understanding in context"*; *"maybe because it's like a metronome and is mostly
deterministic, including dispatch within its sphere"*; *"operations is the one that raises everyone from the dead again
and again like Groundhog Day"*.

**In five lines.** One beat, one program, owns every clock in Operations' sphere and runs them as phases in a fixed order;
dispatch is a phase of it, not a peer. Every beat folds its readings into a small rolling memory of trends and normal
bands, so the one LLM judge reads what changed and what it expected, not raw numbers. Everything that dies is raised on the
beat, told why it died last time; the count of deaths climbs a ladder and stops at a person, never loops forever. The
judge stays rare and costly; everything else is cheap and the same every time. Two clocks stay outside the beat on purpose:
the one that checks the beat is alive, and the memory guard.

## 1. What is wrong with the clockwork today

- **Thirty clocks, six copies of the code.** 33 user timers run. The Operations ones run from six different clones
  (`rm/dispatch`, `rm/bench`, `rm/foundry`, `pulse-deploy`, `relentless/books`, `rm/anchor`), so two clocks can read the
  same file with different code. Their periods are 1, 2, 3, 5, 10, 15 and 60 minutes, picked one at a time; nobody decides
  what runs before what. `ops_watch` writes a status the Dispatcher reads 0 to 15 minutes later, depending on luck.
- **Readings are snapshots.** `ops_watch` already keeps a series per family and the digest shows the 24 h and 7 d change,
  plus a mean ± 3 sigma flag. But the judge gets a 19.5k-character digest of current values and re-derives what is normal
  each run. Each Operations run costs 390k to 440k weighted tokens (3 runs on 11-01: 437k, 389k, 404k).
- **The dead are raised with no memory.** The Dispatcher resumes a dead seat with the same fixed sentence every time, up to
  a flat daily cap. It does not record why the seat died, and the next life is not told. Incidents behave the same way: the
  plan incident (below) relapsed three times and was acked three times with the same mechanical fix.

## 2. The metronome

**One beat.** A single program, `metronome.py beat`, runs every 60 s from one systemd timer and one pinned deploy of the
code. Each beat has a number. A phase table (data, one file) says, for each phase, every how many beats it runs, at what
offset, and its time limit. Phases always run in this order, so every reader sees the writer from the same beat:

| Order | Phase | Today's clock it replaces | Every |
|---|---|---|---|
| 1 | **sense**: one or two `ops_watch` families per beat, round robin | `rm-ops-watch` (one 73 s pass every 15 min) | 1 beat, every family within 15 |
| 2 | **remember**: fold this beat's readings into the memory (§3) | none | 1 |
| 3 | **raise**: deaths, restarts, reconcile (§4) | `rm-restart-reconcile`, the Dispatcher's dead-window branch | 1 |
| 4 | **ring**: incident ladder, alarm routes | inside the Dispatcher tick | 1 |
| 5 | **dispatch**: rings, roles, clock slots | `rm-dispatcher` (2 min) | 2 |
| 6 | **chores**: scratch pressure, account plan and usage, replay watch | 4 timers, 3 to 15 min | as now |

Every phase writes one line to `beats.jsonl`: beat, phase, start, seconds, exit, and a hash of what it read. The rules
that make "a crash is just the next beat" true, each from the review:
- **The beat has a total budget, not just phase limits:** 45 s, with ring and raise reserved first. A phase that would not
  fit is deferred and logged, never squeezed.
- **A phase runs in its own process group with a kill deadline,** and the cleanup has a deadline too. A child that
  outlives the kill may not publish: every output carries the beat's generation and readers drop an old one.
- **Every action outside the program has an operation id,** written before the act and reconciled after it. A raise or a
  ring that happened but was not recorded is found by its id, not done twice.
- **State persists across restarts:** the round-robin position, overdue phases and clock slots. A slot is keyed by wall
  clock (07:30 on 11-03), never by beat number, so a restart can neither skip nor repeat it.
- **Every reading carries its observation time.** A decision names the oldest reading it used and refuses one older than
  that phase allows.
- **The deadman watches useful work, not the heartbeat:** the age of the last *successful* run of each critical phase,
  and the age of the oldest undispatched obligation. A beat that ticks while dispatch fails every time is dead.

**Should the timers collapse to one beat? Yes for the seven in the table above, but only after the cheaper fix proves not
enough.** The review was right that one pinned deploy fixes the six-copies problem without coupling anything; that comes
first (§8 step 0). The beat earns its larger blast radius only through order and freshness: ops_watch's status read by
the Dispatcher in the same beat, not 0 to 15 minutes later. Stay outside:
- **The deadman.** It is what notices the beat stopped. Something that shares the beat's fate cannot do that. It also
  stamps nothing of its own in the beat, and it phones you with no AI in the path, as now.
- **`memwatch`** (1 min). It kills processes when memory runs out; it must run when the beat is stuck in a big phase.
- `timers_guard` stays, watching the few clocks that remain.
- Everything outside Operations' sphere: art pipeline, telemetry export, Steve's retest, Lodestar, nightly selftests,
  the Relentless tick (its own belt), RimPulse.

**Deterministic means:** the same inputs give the same decisions, and you can read why. No phase calls an LLM. The only LLM
in Operations is the judge, launched by the dispatch phase on its slots like any role.

## 3. The memory: trends, not snapshots

A program builds `memory.json` (for programs) and `memory.md` (for the judge) from the series already stored. It never
gathers anything new. Both are published as one generation, written whole and swapped in one step; a reader that finds
two generations, or one older than 30 minutes, says so instead of trusting it.

**Every reading carries five things:** its value and when it was observed; its **normal band**; its **trend** (falling,
flat or rising over 6 h and 24 h, slope per hour); its **state** (normal, drifting, outside, blind) with how long it has
been in it; and, where a signed limit exists, its **time to that limit** at the present slope. Time to limit is the one
part that says how urgent: 10 GB free and falling 2 GB an hour is four hours away whatever the band says.

**The band is typed, because one rule fits few readings** (each line below is a review counterexample, and a test):
- **Numbers:** median ± 3 scaled MADs over 7 days, computed on hourly buckets so a burst of samples cannot outvote a
  quiet day. The spread never falls below a floor per reading, so 10,000 zeros and one 0.001 is not an outlier.
- **Daily rhythm:** a reading whose day and night differ is banded against the same hour of earlier days, or a daytime
  outage reading 20 looks normal inside a pooled 20-to-80 band.
- **Counters** that only rise are read as rates; a drop is a reset, shown as one, never as a collapse.
- **On/off readings** are read by how long they dwell, not by slope.
- **Too few measured points** is `blind`, never `normal`: one good point among 99 unmeasured is blind.
- **A step change keeps its episode.** When a reading moves to a new level and stays, the band will learn the new level;
  the page keeps "stepped from 100 to 140 on 11-04" until the judge or a person marks it accepted. Signed limits in
  `ops_watch_rules.json` still ring as now; the band is never an alarm limit.

**The page is written by exception, and it is added, not substituted.** `memory.md` lists readings that are not normal and
flat, one line each, `disk.scratch_total_gb 88 (normal 61-79) rising 1.2/h for 9 h, outside 3 h; limit in 14 h`, plus
every blind reading and every reading the orders name. The rest is one count per family. Until a planted-fault test shows
that exceptions, blind readings and wrong-but-steady readings all survive the compression, the judge gets the memory page
**beside** today's digest, not instead of it.

**Episodes, not samples.** A list of what happened over 14 days: a reading left its band and came back, a step, an incident
opened and closed, a death, a relapse. Repeats are folded into one line with a count, so a reading that flaps every minute
takes one line; an unresolved episode is never evicted; the page says how much was cut.

**The judge's notes, graded last.** At the end of a run the judge may leave up to 10 typed notes: reading, comparison,
value, deadline, and whether it means "at the deadline" or "at any point before". The program grades each held, missed or
**ungradable** (no fresh reading). The score is shown beside what simply assuming no change would have scored, and the
page counts the open incidents the notes left out, so ten easy notes cannot look like understanding. Built last: it is only
worth having if it changes what the judge does.

## 4. Groundhog Day: raising the dead

**A register of lives, with what each thing is meant to be doing.** One row per thing that can die and be raised: seats,
Relentless workers and checkers, role runs, helpers, timers. Each holds its **wanted state** (running, done, stopped on
purpose, paused), because not every exit is a death: a role run that finishes, a helper that was told to stop and a
planned restart must never be raised or counted.

Each death is a line: when, **how it ended** (killed for 600 s of silence, out of memory, exit code, window gone, login or
quota) and, separately, **what probably caused it**, which may be `unknown`. The two differ: a test that is honestly silent
for 11 minutes is killed for silence, and its cause is a watchdog too tight for that test. The next life is not told to
hurry; an item is filed against the watchdog.

**Every new life is told what the last one learned.** The raise message names the life number, how the last one ended and
the progress or handoff file it wrote: "Life 3 today. Life 2 was killed for 600 s of silence during step 4 of 6 of its
progress file." Any advice line comes from a fixed rule per ending, never invented.

**One raise at a time, and only after the last one is gone.** The raise waits until the dead process has really exited,
checks memory before starting, and records the raise's id, so a death within minutes of a raise is counted against the
raise, not the thing.

**The count climbs a ladder; it never loops forever.**

| Rule | The beat does |
|---|---|
| Lives 2 and 3 in 24 h | Raise, with the note; the second waits 2 min, the third 8 |
| Life 4 in 24 h, **any causes mixed** | Stop raising. Incident to the Conductor, item filed with every death quoted |
| 7 deaths in 7 days, even spread out | Same stop. Three deaths every 25 hours cannot slip under a daily window |
| Ending `login or quota` | No raise until the account check passes **for that model**, backing off; the incident runs on regardless |
| Reset | Only after 6 h of healthy running or a named fix, never by time alone |

**Stopping a raise is not stopping care.** The incident stays open, keeps its age and keeps climbing its ladder; if the
Conductor is itself dead or out of quota, the deadman's fixed line reaches you, as now.

**Incidents get the same rule.** A relapse is a fix that died: an incident that **recovered and closed, then came back**.
Joining an open incident or a new ack is not a relapse. The second relapse in 24 hours stops buying fresh judge runs for it
and files a structural item quoting the acks; the incident itself stays open and on its ladder.

## 5. The cap question: incident `plan-20261101164253`

**The cap number is right for now; the day was spent badly, and one hole is real.** On 11-01 (local) Operations ran three
times: 437k (a clone-pool alarm at 00:00), 389k (07:30), 404k (the batch of 11 incidents at 14:16, which also took the
19:30 slot's place). The plan-list run at 15:38 would have made 1.68M against 1.65M, 30k over; it was refused and the
incident went to rung 3, your phone. Measured, not proved: three runs show what a run costs, not what a fourth was worth.
- **It was one relapse, not three.** The timeline is opened 08:42, recovered and closed 13:11, reopened 13:39, sane from
  15:09, bad again 15:38 (joined, not closed). Each ack was the same mechanical fix (drop done entries from the priority
  list). A fix that keeps dying should file a structural item, not buy a 450k read (§4).
- **The hole: from 14:16 to 07:30 the next day, about 17 hours, nothing can run the judge.** The batch run took the
  evening slot early, and the cap left 420k, under one run's budget. Filed (§8).
- Its route's reader is Operations itself, so the chain's "fresh Operations" rung asks the same role twice.
- The memory page makes a cheaper run possible: an incident run that reads the page and one incident, not a full digest,
  at about a third of a full run (ESTIMATE). That, not a bigger cap, is the fix to try.

## 6. A skeptical read

| Doubt | Answer |
|---|---|
| One beat is one point of failure; today a stuck `ops_watch` does not stop the Dispatcher | True, and the main cost. A total budget with ring and raise reserved, process-group kills with deadlines, generations on every output, a deadman that watches useful work. Pinned deploy first, since it buys the version fix without the coupling |
| 60 s beat but `ops_watch` takes 73 s | Families spread round robin, measured per family before cutover |
| A band learned from 7 days learns a slow fault as normal | Steps keep their episode until accepted; signed limits still ring; time-to-limit says urgency |
| Exception pages hide a wrong but steady reading | Added beside the digest, not instead, until a planted-fault test passes; readings the orders name are always listed |
| Graded predictions are theatre | Possibly. Built last, scored against "no change", with omitted incidents counted |
| A stopped ladder leaves a seat dead overnight | On purpose after 4 lives. The incident still climbs; deadman to your phone if the Conductor is down too |
| Cause classes from exit codes are thin | How it ended is reliable; the cause may be `unknown` and that share is a reading |
| Cutover makes two owners for a moment | Each phase takes over with an ownership generation; an old timer's run already going cannot write over it |
| "24 h in shadow" proves little | Shadow must also pass planted crashes, overruns and a duplicate run of the same phase |

## 7. Independent review

GPT-6.1 (`gpt_consult.py`, high effort, told to be hostile) read this and the 11-01 design and gave 38 findings, 36 marked
as changing the design. All 36 changed the text above except the build order, where I kept memory first (below). The two
advice-only ones (pin the deploy before collapsing timers; graded notes must change decisions) are taken: step 0 and "built
last". Its sharpest catches: per-phase limits do not bound a beat; a mixed-cause death series never hits a same-cause
limit; the plan incident was one relapse, not three; and the 19:30 slot left unfunded. Full text:
`D:\ClaudeWork\rimmandrake\ops_metronome\gpt_review.md`.

**Where I disagree.** It wanted refusal routing, budget reservation and incident dedup built first. A refused run already
moves the rung (`dispatcher.py` `denied_runs`), and dedup by cause exists. The open parts (the 17-hour hole, relapses) are
step 2. Memory goes first because it is read-only, cannot break a live clock, and is what makes a cheaper incident run
possible.

## 8. Build order

ESTIMATE, in helper days. Each step ends with a planted fault caught on the real path.

| # | Step | Days |
|---|---|---|
| 0 | One pinned deploy of the Operations code for every Operations clock, instead of six clones. Built 2026-11-03: the deploy is the dispatch clone; clocks and the units left outside are listed in `src/RimMandrake/Utils/systemd/ops_clocks.json`, checked by `ops_clocks.py check` | 0.5 |
| 1 | **Memory, beside the digest.** `ops_memory.py`: typed bands, trend, state, time to limit, blind rules, exception page, atomic generation. Run by hand and after each ops_watch pass; nothing decides from it | 0.5 |
| 2 | Ladder fixes: relapse counted only after a recovery; second relapse files a structural item; no 17-hour hole (an incident run never takes the evening slot's place before noon); incident runs read the memory page at a smaller budget | 1 |
| 3 | Register of lives, read only: wanted state, endings and causes from the Dispatcher journal, memwatch and Relentless logs | 1 |
| 4 | Raise with memory: life note, single-flight raise, the ladder, the 7-day breaker | 1 |
| 5 | Metronome in shadow with operation ids, generations, total budget; planted crash, overrun and duplicate-run tests | 1.5 |
| 6 | Cut over, one clock a day, with ownership fencing: restart reconcile, ops_watch, Dispatcher, chores | 4 |
| 7 | Episodes; judge notes graded against "no change" | 1 |

The old design's build order (Marker verdicts, packet, report, alarm tuning, orders) runs beside this, on the same items.
