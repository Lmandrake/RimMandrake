# Seeing, steering and resuming the pipeline's agents: report for Mandrake (2026-11-04)

The full design is in `design.md` and GPT's review, verbatim, in `gpt_review.md`, both in this folder.

## What you asked

Today's token outage raised two questions. First, how should the pipeline pick up after it loses tokens, without anyone poking idle windows? Second, should the build, judge and test agents run in visible windows (tabs in one Pipeline window where FOUNDRY used to sit), so you can watch them for free and sometimes type into one? You asked for at least four approaches, then a GPT review, then this report.

## Short answer

Yes, you can have that window, and you can type into a worker. But the way to get there is not "make the workers interactive terminals". The safe way has three separate layers:

1. **Workers keep running as supervised background jobs.** They keep their memory limits, kill switch, time walls and a structured end record. That is what lets the pipeline judge, meter and restart them.
2. **The Pipeline window is a live viewer.** It has one tab per station, each showing what that worker is doing as it happens. Watching costs zero tokens. Closing the window stops nothing, and opening it starts nothing.
3. **Typing is a "send a note" box per station.** Your note goes into that worker's running conversation at its next turn and is kept in the record. Fully taking over a worker ("take control") comes later, as a separate and more careful step.

Visible windows do not fix the outage problem by themselves. Today's interactive windows also just stopped at the limit and waited for someone to type. Recovery has to be a pipeline action either way.

## Today's numbers (measured)

- The outage ran 14:47Z to 20:07Z. In that time the pipeline launched about 48 runs straight into the closed account. Each died on its first turn having done nothing.
- Only **3 runs** were cut off after real work: two builders (63 and 19 turns) and one judge (2 turns). Their conversations are still on disk and can be continued.
- A run that hits the limit reports "success", with the limit message as its answer. Detection must read the message, not the status.
- I tested continuing a cut-off background conversation (`claude -p --resume`): it keeps its memory and its session id.

## The options

| Option | What it means | Verdict |
|---|---|---|
| A. Headless, as now, plus resume | Workers stay invisible; recovery automated | Needed underneath everything, but it does not give you a window |
| B. tmux | Each worker is interactive Claude in a tmux pane | Workable if done carefully (pane kept inside the worker's memory limits). Second choice for typing |
| C. One WT window with tabs, each running Claude | What you pictured | Good as a *view*; risky as the place workers actually *live*: one window crash or stray close takes every tab, and new tabs can steal focus |
| D. Separate stacked windows | One window per station | Clutter and focus stealing times twelve; debugging only |
| E1. Live viewer | A tab per station showing that worker's live log | Build first: cheap, safe, zero tokens |
| E2. Claude's own background sessions (`--bg`, `claude attach`) | Built-in watch and attach | Promising; needs a probe of memory limits and stop behaviour |
| E3. Remote Control on every worker | Phone watch and type for all | No: every machine-wide RC drop on record came from one `/login` |
| E4. Live note inbox | Workers accept your typed notes while running | **The target**, together with E1 |
| F. Take control | Pause a worker and open it interactively for you | Later, and only if notes are not enough. It is harder than it looks |

## Recommendation, in build order

| # | Step | Size |
|---|---|---|
| 1 | Make the standard resume action solid, inside the two items already filed today | 1-3 days |
| 2 | The Pipeline window in FOUNDRY's spot: stable tabs, never grabs focus, also reachable from the phone over SSH | under a day to 3 days |
| 3 | A short test of the ways to deliver your notes into a running worker, on a throwaway clone | under a day |
| 4 | The "send a note" box, using whichever way passed step 3 | 1-3 days |
| 5 | "Take control", only if you still want it after a week of notes | a week or more |

## The standard "resume from token loss" action

It applies to suspended pipeline runs only: builders, judges, consults, role runs and timer jobs. It never touches idle windows, and it never broadcasts "continue".

1. When the account is out, a single breaker stops **all** AI launches. Non-AI work carries on. This alone would have prevented today's 48 wasted launches.
2. The reset time comes from the limit message, read carefully. Once it passes, one small test run checks the account, and then work is let back in a little at a time.
3. Each cut-off run is sorted three ways:
   - nothing useful done: start fresh;
   - real work saved: continue the same conversation;
   - unsure: check first.
4. Before a run continues, the pipeline confirms that the task is still open and still that run's. It also confirms the clone has not been reused, and, for a judge, that the thing being judged has not changed since.
5. The continue message tells the worker to check before it repeats anything that touches the outside world: commits, publishes, deploys, game commands.
6. An outage counts against no one. It adds no strikes and no failure alarms, and time spent waiting is not taken from the run's time allowance.

## How we would know it works (proposed targets, not yet measured)

| Measure | Target |
|---|---|
| Launches into a closed account during an outage | 0-1 (today: 48) |
| Safe cut-off runs resumed correctly in a staged outage | all; unsafe ones held |
| Time from reset to first resumed run | 5 min or less |
| Delay between a worker acting and you seeing it | 2 s or less |
| Tokens spent on watching | 0 |
| Notes delivered to the wrong task | 0 in 100 tagged tests |
| Times the window steals focus | 0 in 100 relaunches |
| Extra memory for the viewer at 8 stations | 1 GB or less |
| Shell commands you need for routine use | none |

## Decisions that are yours

1. Do you want the Pipeline window built (step 2) now?
2. Is "send a note" (it lands at the worker's next turn) what you meant by typing into a worker? Or do you want full "take control" from the start, at several times the cost?
3. Should the window also open from your phone, over SSH and tmux?
4. Once the resume work lands, may it continue today's 3 cut-off runs?

## Attribution

- **Yours:**
  - the question;
  - a standard resume action;
  - no more pokes to idle windows (HESTIA, Emergency, Server);
  - one window with station tabs in FOUNDRY's spot;
  - watching for free and typing into a worker;
  - the four starting options (tmux, headless, tabs, stacked).
- **Claude's (this pass):**
  - the fact-finding and today's outage count;
  - the trap where a cut-off run reports "success";
  - the resume test;
  - options E1 to E4 and F;
  - the first resume spec;
  - finding that the pipeline's liveness check is blind to work done inside a sub-agent.
- **GPT's (review):**
  - splitting the design into run, control and view;
  - "send a note" before "take control";
  - B*, the safer tmux variant;
  - the steering probe;
  - most of the hardened resume rules (error classes, identity pinned before launch, checks before continuing, no double-counted cost, gradual admission);
  - the metric set and its targets;
  - spotting that the liveness check can be fooled by other sessions in the same clone.
- **Where GPT disagreed with Claude, and who was right:**
  - *Biggest:* my first draft said keep the workers headless and let you watch for a week before deciding whether you need to type. GPT said you had already asked to type, so steering is a requirement, not something to prove. **GPT was right**, and the recommendation now includes the note box.
  - I valued the 3 cut-off runs at "$4.4 saved". GPT pointed out that this is what they had already spent, not what resuming saves. **GPT was right.**
  - I said Claude's background sessions escape the memory limits, and that Windows Terminal had failed in 6 of 11 windows. GPT called both overstated. **GPT was right on both.** The 6 were windows whose sessions had ended, not terminal crashes.
  - I costed "take control" at 1-3 days. GPT said it is a full ownership hand-over and much bigger. **GPT was right.**
  - GPT gave tabs and tmux a fairer hearing as places to *show* work. I still hold that the workers themselves should not *live* in a terminal window. GPT's own ranking agrees: C ranks 7th as a worker host.
