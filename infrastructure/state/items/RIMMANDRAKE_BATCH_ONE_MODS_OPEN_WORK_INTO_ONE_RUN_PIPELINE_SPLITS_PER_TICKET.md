# RIMMANDRAKE_BATCH_ONE_MODS_OPEN_WORK_INTO_ONE_RUN_PIPELINE_SPLITS_PER_TICKET

## What the card said

<!-- answered 2026-11-25T06:24:03Z; recorded by `note` (OWNER); written by rimflow, never by hand -->

**Question:** A work bundle is all the ready tickets of one system (one mod, or one part of the pipeline such as a rimflow tool), worked by one run in one context. The first choice is what a bundle IS on the ledger, the list where all tickets live. Today each ticket is its own record and gets its own run. (Hard to read? Type STE, Binding or Both for a rewrite.) What form should a work bundle take?
**Picked:** Program-made record (Recommended)
**Its description:** Why: nobody should file paperwork to save paperwork. The launcher writes one bundle record listing its member tickets; each ticket keeps its own test and closes with its own commit. Costs a build in both launchers. Recommended: visible on the page, and no new filing step.
**Other options:** Hand-filed joint ticket · A worker role only · Record plus hand command

**Question:** The batch-worker report found that the live game proof costs more than the fixes: after the Explosive Knockback sweep it took 20 more runs to reach your pass, and after the Gimme Some Slack batch 3 more. A bundle can prove its fixes in a live game itself, or leave that to the mod's next scheduled in-game test visit. Where should a bundle's live proof run?
**Picked:** Inside the bundle run (Recommended)
**Its description:** Why: the worker still holds the context of what it changed. It takes a free game, runs only the in-game checks its changes touch, and closes proven. Costs a longer run and game time; a game fault can stall the whole bundle. Recommended: the Slack run did this and your walk passed first try.
**Other options:** At the mod's next visit · Inside, but hand off on a game fault

**Question:** The evidence for bundles is two runs, on unlike work. The reality sort (a program closes tickets whose test already passes) is well supported; fixing and proving many tickets in one run is supported by one run only. The pipelines today launch one run per ticket. How should bundles start?
**His words:** They fix together, offline test together, then live test together. When they run out of context they save their state, restart, and keep going. It’s the relentless agent in spirit. It works because the correct unit of work is a system not a bug. Same lesson we learned for mods for the maturation pipeline. Learning it again for the workshop pipeline and also to extend it not just to advancing a mod or system but to embrace all the tickets at once that make up a version.
**Other options:** Default at once, counted (Recommended) · Measured trial first · Reality sort now, bundles after · Hand command only

**Question:** A bundle run will sometimes end with member tickets it did not finish: the context filled, a fix was unknown, or a ticket turned out larger than it looked. For the Gimme Some Slack close-out you ruled that anything not done that round was dropped and reported to you. What should happen to a ticket the bundle did not finish?
**His words:** Either they just reboot and keep fixing or they have a reason to not do the ticket and say so. Refused tickets may not be provable, or di not represent the system they were told to modify, or any number of other surprises. But there must be a reason or else the bundle keeps going.
**Other options:** Back to the list, with reason (Recommended) · Dropped and reported · The run decides, by a rule
