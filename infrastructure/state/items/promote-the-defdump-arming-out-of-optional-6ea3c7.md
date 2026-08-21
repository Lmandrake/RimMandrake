## spec
`NEXT_RELOAD.md:58` (§1a) arms the DefDump and is labelled "**OPTIONAL, gates
nothing**". BUILD reports it does gate something: the live dump is STALE, only
a game load refreshes it, and `Jawa_Armoury/Patches` is downstream of it and
stays stale until it lands. Read at STARTUP only, so it is armed before launch
or not at all — and a missed arming costs a whole load.

## verify
§1a no longer says it gates nothing, and names what goes stale without it.

## criteria
the post-load dump is current and `Jawa_Armoury/Patches` can be regenerated
from it without a second load.

## notes
**Imported from `queue/DECIDE_ARCHIVE.md`. Its `state:` read, verbatim:**

⛔ v2 — **OWNER RULING 2026-08-15, blanket triage.** Produces no content and does not
reach the frozen world. Parked, not lost.
