# Tentative plan: what to bring back from v2, and what must be new (2026-11-01)

**Status: TENTATIVE.** Owner, 2026-11-01: *"Not yet, write them as a tentative plan."* Nothing here is a goal or a
ruling, and nothing here goes in `CONDUCTOR_GOALS.md` until he says so. Numbers are MEASURED, ESTIMATE or UNMEASURED.

## 1. The diagnosis, in his words

*"We need to have several well-codified new concepts to introduce here before I just go back to v2-style work."*

v2 failed by thinking it was done when it was not, *"But that wasn't just because "no one checked."*

- Days of focus did happen, and that was close to relentless: *"Bench was working FlowWorks aggressively for days.
  Foundry had some biomes and GSS and Solar."*
- Focus turned into repetition: *"I would constantly find them stuck in selftest.py. I would ask them what they're
  doing, and they would say "yup, testing things I already knew again."* Then the same in the live game.
- *"I was the "make sure the validation tests aren't wasting everyone's time" guy."*
- *"Each time it would get better and move us closer, but we never seemed to get there. In GSS it worked pretty well.
  Simpler mod. FlowWorks never got there. Pyrelands got there eventually."*
- *"All of them required a human to be the Conductor role, holding state in my head, sanity-checking runtimes and
  current activity."*
- *"Watching art decisions be rendered by me, only to one more time be offered the same item..."*

## 2. The jobs he was doing by hand

So the gap is not "a checker". He held five jobs, and each needs a named home:

| # | His job | What it asks | Status today |
|---|---|---|---|
| J1 | Waste watcher | Is this test telling us anything new? | Policy written, barely enforced |
| J2 | Test strategist | What better test would catch what we keep missing? | Asked for by hand each time |
| J3 | State holder | Where does this mod actually stand? | Scattered: items, proofs, RimPulse, his head |
| J4 | Activity sanity | Is this runtime and this activity reasonable right now? | RimPulse shows it; nobody is charged with judging it |
| J5 | Review gatekeeper | Was this looked at first? Was it already ruled? | Largest part is built |

## 3. New concepts to codify

Each is a program that measures, plus one agent that reads. **No new role is proposed**: roles are part of what we are
reviewing. The reader is the Conductor unless he rules otherwise.

**C1. Mission (replaces the ticket as the unit of focus).** A mission is one mod or system held for days, in the
spirit of v2's focus, with the persistence of relentless. It has a written finish line, a live state page, and a
fresh-window worker that resumes from disk. Tickets stay as its internal notes. Relentless holds an item; a mission
holds the thing he actually wanted finished.

**C2. Finish line written before work.** Each mission has a short list of observable behaviours, ending in his look
where only he can judge. "Done" is a reading of that list, never a statement by the worker. This builds on
`modcheck floor` and north-star bars, which already exist.

**C3. Known-result ledger (J1).** Record (test, hash of everything it depends on, result). Same inputs means the
stored answer comes back and nothing runs. To rerun on purpose you must state what you expect could differ. The same
applies to live tests, keyed on deployed mod hashes. This is what would have answered "testing things I already knew
again" without him.

**C4. Time ledger (J1, J4).** Every worker's hours are charged by category from its own process and tool records:
selftest, live test, build, reading, editing, waiting. A program alarms when testing outweighs changing, or when a
worker has run for a set time with no new finding and no new code. Thresholds are data.

**C5. Finding-kind curve (J2, the "never got there" detector).** Per mission, count new KINDS of finding per day and
where each was caught: selftest, proof, live, blind check, or by him. A global rule already says a rising score with
flat findings is not progress. This makes it a per-mission meter, and it tells apart "converging" from "going round".

**C6. Escape review (J2).** Anything he, a live test or the blind checker finds that the tests missed is an escape.
Each escape must produce a test that would have caught it, or a stated reason why none can. A second count covers
tests that have never failed and cost real time, which become candidates for retirement. His standing request for
"new, better, different, more efficient testing" then comes from data, not from his patience.

**C7. Mission page (J3).** One page per mission, machine-written: finish line with each row's status and age of proof,
what is running now and for how long, time ledger, finding curve, open decisions. He should be able to read it on a
phone, and no head has to remember it.

**C8. Conductor's daily mission read (J4).** The Conductor reads every page on a schedule and acts by rule: redirect,
stop, or raise it to him. This is the job he did by hand. The test is plain: he should stop catching waste before the
Conductor does. Each time he catches it first, that counts as an escape under C6.

## 4. What to bring back from v2

- Long focus on one mod, by a window or worker that keeps at it.
- Two lanes with a clear split: the window with him, and an autonomous one.
- Fewer roles. v2 had two seats and they did real work.
- Him available for live looks during a sitting, because some of FlowWorks needed that.

## 5. What to keep from v3

| Keep | Why | Honest state |
|---|---|---|
| Dispatcher restarting windows and managing their context | He named this as an advance | Working for FOUNDRY |
| The item on disk, replaceable workers | Survives restarts | One day old, no measured result |
| `--live` promises and `rm-deadman` | Done means running | Built 2026-10-31 |
| Blind check at the end of a cycle | Not inside the debugging loop | Built |
| Pinned read-only trees for anything measured | Last night's lesson | Used by the trial |
| Pre-review, ruled-row collapse, `.prereview.json` | J5: *"look at items before you show them to me"* | Built; repeat-offer rate UNMEASURED |
| Delegated taste calls and the daily digest | Keeps his queue short | Built |

## 6. What is broken now, and must not be carried over

- **FOUNDRY staffing.** MEASURED 2026-11-01 13:06Z (`/home/mandrake/rm/relentless/store/staffing.json`): budget 8,
  382 ready, under budget for 398 minutes, 3 waiting, 0 running on its checks. Cause not established. He says it
  *"seems to suck at subagent staffing"*, and the reading supports him. A mission plan cannot be judged while this holds.
- **Bench closes only when he says goodbye.** *"Bench still runs on me saying goodbye... that's like it was,
  basically."* The Conductor's context backstop is off (`backstop: false`,
  `src/RimMandrake/rimflow/dispatcher_schedule.json`); its review findings are open and its thresholds were never ruled.
- **Nightly selftests carry no news.** MEASURED in `testing_policy_2026-10-28.md`: RED on 14 of 14 nights, 2026-10-15
  to 10-28. Whether that still holds is UNMEASURED today.
- **Testing policy is mostly prose.** That doc says only the mutation full-run gate is enforced in code. C3 and C4 are
  how the rest gets teeth.

## 7. Proposed order, smallest proof first

1. Find why staffing is low, and fix it.
2. Build C4 (time ledger) and C7 (mission page), read-only. They change nothing and show whether the waste is real.
3. Pick one pilot mission. Candidate: **FlowWorks**, because it is the one that never got there, so a pass there
   means something. The counter-argument is a simpler pilot first; a retrofit on a mid-sized mod would be cheaper.
4. Write its finish line (C2) with him.
5. Add C3 (known results) once C4 shows how much time it would save.
6. Add C5, C6, C8. Run the pilot for about a week.
7. **Pass test:** he catches no waste the Conductor did not catch first; the finding curve falls; the finish line
   advances; he never sees a repeat. If that fails, this plan is wrong and we learn why cheaply.

## 8. Open questions for him

- Is "mission" the right unit, or is a mod simply the unit?
- Is FlowWorks the right pilot, or does it risk failing for reasons unrelated to the method?
- Does the Conductor read pages in C8, or should Operations do it?
- May Bench close itself when idle with a high context, so it stops depending on his goodbye?
- What does the trial still need to tell us, given it ran serially?

## 9. What this does not claim

C1 to C8 are proposals. None has been tried. Why FlowWorks did not converge is a hypothesis here, not a finding: test
waste is his account of it, and the mod's own complexity may matter as much. The fan-out simulator work in progress
may change how many workers a mission should use.
