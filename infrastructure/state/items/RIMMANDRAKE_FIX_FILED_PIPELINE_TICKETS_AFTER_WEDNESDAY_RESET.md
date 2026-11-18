# RIMMANDRAKE_FIX_FILED_PIPELINE_TICKETS_AFTER_WEDNESDAY_RESET

## What the card said

<!-- answered 2026-11-18T21:17:43Z; recorded by `note` (OWNER); written by rimflow, never by hand -->

**Question:** I cannot confirm it: 63 tickets are building (I said 54 earlier, a miscount), and 10 of them were filed before the Maturation Pipeline existed (Oct 23 to Nov 12, in the Foundry, Relentless and v3 era). This morning's triage already dropped every ticket that only served a retired loop; these 10 survived because the code they fix still exists today (selftest harness, dispatcher schedule, site-save backups, handoff pointers, an art-sheet scan, showcase rules). Nine of them are the whole 'hygiene' builder (Sonnet, 13 minutes in), one sits in another builder. The other 53 were filed since Nov 13, but 4 of those are about the Conductor window's restart, not the pipeline proper. What should happen to the tickets that are not strictly Maturation Pipeline?
**Picked:** Stop them, keep only what the pipeline runs (Recommended)
**Its description:** Why: you asked for Maturation Pipeline upgrades only. I stop the hygiene builder now, check each of the 10 old tickets against one test (does the Maturation Pipeline execute this code?), and relaunch only those that pass. Costs 13 minutes of Sonnet work discarded and a short re-check. Recommended: it matches your order and loses almost nothing.
**Other options:** Let them run · Stop all 10 and park them · Stricter: also stop the Conductor-restart builder
