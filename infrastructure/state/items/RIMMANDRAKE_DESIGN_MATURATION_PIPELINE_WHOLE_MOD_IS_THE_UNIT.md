# RIMMANDRAKE_DESIGN_MATURATION_PIPELINE_WHOLE_MOD_IS_THE_UNIT

## What the card said

<!-- answered 2026-11-15T04:24:44Z; recorded by `note` (OWNER); written by rimflow, never by hand -->

**Question:** In the Maturation Pipeline's in-game acceptance stage, scripts give a pass or fail on each locked bar of a mod version, and separately an agent explores and takes screenshots before your live walk. There are two games: Archmagi (yours) and SteveDesktop (the unattended test machine, where 85 of 261 jobs died before judging anything from 11-06 to 11-14, mostly from machine and game faults). Which game gives the scripted verdicts?
**Picked:** Whichever game is free
**Its description:** Why: get verdicts soonest and lean less on a faulty machine. Buys speed when SteveDesktop is down or busy. Costs: verdicts and exploring compete for Archmagi, so your sittings can wait on a test run. Slightly less to build, more to schedule.
**Other options:** SteveDesktop gives verdicts · Archmagi until Steve is fixed

**Question:** After a mod version passes, something must notice if a later change breaks it. Today SteveDesktop's 'guard' jobs re-run every mod's tests on a rotating schedule, changed or not. The proposal is to re-run a passed version's bars only when something it depends on changes (its files, the mod list, a game update). When should a passed version be re-tested?
**Picked:** On change, built later
**Its description:** Why: nothing has passed yet, so there is nothing to guard today. Buys the right design without building it early; the schedule carries on meanwhile. Costs: the biggest build of the three is still owed once the first version passes. Recommended: build it when it has something to protect.
**Other options:** On change, build it now · Keep the schedule

**Question:** Today a filler program keeps SteveDesktop busy with tests for any mod, including mods with no locked version; most of the queue's traffic is this. The proposal is an entry rule: only tests that came through the pipeline's offline stages (written against a locked bar and challenged by a blind judge) may be queued. What may be queued on SteveDesktop?
**Picked:** Pipeline tests only
**Its description:** Why: the strictest and simplest rule. Buys the cleanest queue and the most machine hours saved. Costs: a mod nobody is advancing can break silently until it enters the pipeline. Smallest build.
**Other options:** Pipeline tests plus load check · Keep the filler running
