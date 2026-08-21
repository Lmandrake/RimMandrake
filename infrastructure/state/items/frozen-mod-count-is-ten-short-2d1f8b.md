## spec
Reported by BUILD from `refresh.py` (fingerprint `7256c128a43117a5`), relayed
by REP. Three numbers for one set and they disagree:

| source | count |
|---|---|
| live `ModsConfig.xml` (mtime 2026-08-15 11:58:30), and `deployed/config/v1_freeze/ModsConfig.xml`, identical incl. order | **575** |
| live DefDump, when it was taken | 576 |
| `infrastructure/state/V1_CHAIN.md:80-88` — "**These 585 ARE the frozen set** — owner's ruling, 2026-08-14" | **585** |

575 resolved, 0 listed-but-missing, so the live pair is internally consistent
and is the true state. The six Descoped rows of
`design/Jawa/mods/CHERRYPICK_AGENDA.md` account for six of the ten;
`regrowth.botr.boilingforest` is the one that left since the DefDump. **Four
are unaccounted for.**

This is yours because §0 of `V1_CHAIN.md` is a ruling, not a measurement, and
only you can restate it. `585` also appears in `infrastructure/state/V1.md`,
`design/Jawa/mods/required_mods.md`, `design/Jawa/mods/CHERRYPICK_AGENDA.md`
and `design/Jawa/worldbuilding/FACTION_SPEC.md` — some of those are prose about
the ruling and follow it.

## verify
the four unattributed removals are named, and every doc that states the frozen
count states the same number.

## criteria
EMPTY — offline.

## notes
**Imported from `queue/DECIDE_ARCHIVE.md`. Its `state:` read, verbatim:**

⛔ DROPPED 2026-08-19 — **owner: *"Unfreeze mod count, let's not treat this as
a criteria to monitor for v1."*** The item asked for four unattributed removals to
be named and every doc to state the same number. Neither is wanted. The premise
also decayed while it sat: live is **578** today, not the 575 this item was
reconciling to, and not the 585 it was raised against. ⇒ Chain step 0 is
UNFROZEN in `V1.md` and `V1_CHAIN.md`; the "these N ARE the frozen set" ruling is
repealed in place. **The mod list is captured at worldgen time as shipping
documentation, not policed as a standing number.**
