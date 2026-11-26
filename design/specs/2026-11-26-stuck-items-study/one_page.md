# Do items get stuck, and who unsticks them? (2026-11-26)

Your question, about 11:40 AM PST: "Are items getting stuck in the pipeline and depending on the conductor to unstick
them? Or is it working well and I simply can't tell?"

Window: the 7 days to 2026-11-26 noon PST. Every number has its row and its command in `evidence.md` beside this page
(`D:\Luke\dev\RimMandrake\design\specs\2026-11-26-stuck-items-study\evidence.md`). A **stop** is an open ticket or mod
with no progress for 12 hours or more, when no date and no hold of yours explains it.

## Short answer

Both are true. Programs now end most stops. But a small set of stop kinds has no program that ends them, and your page
does not show those kinds. Those stops last days, and the Conductor finds them by hand or not at all.

## 1. Is it true?

Yes, for some kinds of stop.

- **Tickets.** 368 stops of 12 hours or more ended in the 7 days, on 595 tickets that the Workshop Pipeline reads.
  185 of them lasted 3 days or more.
- **Stops that stand now** (102 tickets at the 11:23 AM tick). Each age is the hours since the ticket's last progress:
  - 13 tickets wait for your answer. Median age 323 h (13 days).
  - 9 tickets wait for a judge. Median age 494 h (20 days). No program starts that judge.
  - 9 tickets wait for the Conductor. Median age 9 h.
  - 7 tickets have a check that holds, but the close is refused for a fault of form. Ages up to 15 h.
  - 5 tickets wait for a mod run that does not come, because their mod rests after its pass. Ages 40 to 49 h.
  - 4 tickets are stopped by the chain limit, with no next step. Ages 31 to 39 h.
  - 2 tickets were left out of their work bundle. Age 484 h each.
- **Mods.** The mod pipeline made 65 stage moves in 7 days. Gimme Some Slack has rested 45 h and Pyrelands 41 h since
  their passes. A `pipe off` on Gimme Some Slack stayed 43.5 h after its reason had ended.
- **Short stops.** SteveDesktop refused every launch for 3.6 h this morning: its account gate counted runs that it could
  not read as live. The machine-load line held the ticket lane for 2.2 h in 81 h.

## 2. Who ended each stop?

| what | a program | the Conductor | you |
|---|---|---|---|
| ticket stops that ended (368) | 84% | 13% | 3% |
| hours of those stops (31,703) | 86% | 12% | 2% |
| mod stage moves (65) | 92% | 6% | 2% |

The Conductor's hand on the mod pipeline fell from 24 acts on 11-20 to 2 or 3 acts a day on 11-25 and 11-26.

The stops that only a hand ended in the 7 days:
- each lift of a `pipe off` whose reason had ended (5 lifts, up to 106 h);
- each mod stop after three launch refusals of one cause (9 clears, 7 of them on 11-20 and 11-21);
- the SteveDesktop account switch, the tick clone that could not pull, and 5 of 6 fresh-reader runs after a fix.

## 3. Could you tell?

Mostly not. Your page (`D:\ClaudeWork\rimmandrake\conductor\MATURATION_NOW.md`) shows counts, not the stuck kinds.

| kind of stop | on your page, with reason and age | elsewhere |
|---|---|---|
| asks to you (13) | "Needs Mandrake" shows 2 | 10 on the detail page; 3 nowhere |
| routed to a judge (9) | a count only, inside "waiting" | the detail page calls it "program", which is false |
| routed to the Conductor (9) | no | the detail page, with age since filing |
| close refused (7) | no | the Conductor log only |
| mod work while its mod rests (5) | "Resting", "Needs you: nothing", no age | no |
| chain limit, left out of a bundle, stopped (7) | no | the lane's own status only |
| machine load, account gate | "35 failed to launch", a count only | the bundle files, `./acct` |
| a `pipe off` past its reason | UNMEASURED (the page is not kept) | the control store |

## Proposals, in order of the stuck hours that each would remove

You decide each one. None is built.

1. **Program: put each ask to you on your page, with its age.** Every ticket that the lane routes to you joins "Needs
   Mandrake", oldest first. An old ask is checked first, and dropped when it is stale. *Evidence:* 13 asks, 3,020 h of
   age; the page shows 2. *Cost:* small. *Risk:* a sudden list of 13 old asks; some asks are already stale.
2. **Program: start the judge for a part routed to a judge.** The lane launches one fresh judge run on the routed part.
   *Evidence:* 9 tickets, 2,769 h of age; nothing starts them. *Cost:* medium. *Risk:* judge runs spent on stale asks, so
   the old-work filter runs first.
3. **Program: give each held-back ticket kind a named owner and a clock.** A ticket at the chain limit, left out of its
   bundle, stopped or too heavy to check goes to the Conductor's owed list after 24 h, and shows on your page with its
   reason and age. *Evidence:* 8 tickets, about 940 h of age; 0 shown. *Cost:* small. *Risk:* more lines for the
   Conductor; the chain limit must still stop a loop.
4. **Program: a resting mod does not keep its tickets.** When a passed mod rests 24 h with open mod tickets, the tick
   puts a dated next-version call in the Conductor's owed list, or hands the tickets to the ticket lane. The page shows
   the rest's age. *Evidence:* Gimme Some Slack 45 h and Pyrelands 41 h at rest; 5 tickets, 146 h. *Cost:* small.
   *Risk:* a change to a passed version's code must not move its bars.
5. **Program: each `pipe off` carries its end condition, and the tick lifts it when the condition is true.** The page
   shows each off with its age. Your own holds stay yours. *Evidence:* Gimme Some Slack 43.5 h past its reason; readiness
   holds lifted by hand at 106 h, 48 h and 24 h. *Cost:* small. *Risk:* a wrong condition lifts a hold too early.
6. **Program: a refused close says its own reason and repairs its form.** Today all 26 refusals show the publish's
   text "nothing to publish", which hides the cause. *Evidence:* 7 tickets now, 62 ticket-hours in 81 h, shown nowhere.
   *Cost:* small. *Risk:* low.
7. **Binding rule: a run that fixes code also files the fresh reader of its fix, so that a program launches it.**
   *Evidence:* 5 of 6 fresh-reader runs in 7 days were launched by hand. *Cost:* tiny. *Risk:* more reader runs.
8. **Binding rule: a run that receives "write where you are" writes its note and ends inside the deadline; the deadline
   is at least 10 times the measured time to write a note.** *Evidence:* 3 of 6 such orders ended in a kill. *Cost:*
   tiny. *Risk:* none to the stuck hours; it guards work that a kill loses.

Already in hand, so not proposed: the SteveDesktop account switch past a run that only waits (a repair run ended
success at 8:39 AM PST today), and the tick clone that could not pull (a repair run was launched at 10:05 AM PST).

## What is UNMEASURED

- Time in each stop kind before 2026-11-23, and the hour that a ticket entered its kind: no record keeps them.
- Who launched 426 of 996 runs: no run record names its launcher. They are counted as the Conductor's from their briefs.
- What made the machine load over 7 days: one sample only (two `./publish` check runs led it at 12:03 PM PST).
- What your page showed on past days: the page is not kept.

## Faults found that hold work now

- 9 tickets routed to a judge: nothing starts the judge.
- 7 tickets whose check holds: the close is refused for a fault of form.
- 5 tickets wait for a run of a mod that rests.
- `maturation_hands.py` counts 8 program moves as hand acts (65 listed, 56 true).
