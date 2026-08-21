## spec
🔴 **OWNER RULING 2026-08-20** (`OWNER_DECISIONS.md`, end of file): *"I've
been very clear. OuterRim_GalacticEmpire is no longer in the game, we patch
Empire."* Plus: *"I'm not sure we need either of those gap audits... we may
instead need to perform a new one."*
Both prior audits are **quarantined** at
`infrastructure/disposing/faction_engine_gap_audit.md` and
`.../faction_stage2_gap_audit.md`. Nothing in `disposing/` may be cited,
followed or copied from — treat them as absent. They are there only so the
7-day dwell can prove nobody needed them.
⚠️ **They were not merely stale — they reasoned from the wrong vessel.** Both
audited the Stage 2 question against `OuterRim_GalacticEmpire`. Re-run the
question against vanilla `Empire` (Royalty): what does the Empire still need
before v1, given Royalty's titles, permits, gear tiers and quest surface come
free with the vessel and need no `MayRequire` gate at all.
🔑 Blast radius: **the Empire's vessel only.** Other `OuterRim_*` defs — pawn
kinds, gear, the droid factions — are untouched and staying. Do not sweep by
the `OuterRim_` prefix.

## verify
a single audit doc exists naming vanilla `Empire` as the vessel, listing what
is missing for v1, and citing no quarantined file.

## criteria
the Empire is buildable from one document without anyone re-deriving which
faction def it is.
🔴 **Two checks were "closed" against the wrong def and are now genuinely
open** — found while propagating the ruling, 2026-08-20:
1. **The Force-patch xpath for the Empire does not exist.** The old one
   selected on `TabulaRasa` pawnGroupMaker classes; vanilla `Empire` has none
   of them, so the xpath must be re-derived against `Empire`'s own
   `pawnGroupMakers`. ✅ No `PatchOperationFindMod` wrapper is needed — Royalty
   is always loaded.
2. **`Empire`'s three pursuit-eligibility flags have never been read** —
   `displayInFactionSelection`, `canStageAttacks`, `defName != "PColony"`. The
   eligibility rule survives; only the worked example died with the old def.
Neither breaks anything today. Both are checks that were passed against a def
we do not use.

## notes
**Imported from `queue/DECIDE.md`. Its `state:` read, verbatim:**

open — raised by REP, 2026-08-20, relaying the owner.
