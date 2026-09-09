# Companion silent-failure hardening

Owner (2026-09-09, "deep work" sitting): harden the JawaBench companion against the
silent-failure class that cost hours during the ship work. Full audit (39 findings):
`design/Jawa/reviews/COMPANION_HARDENING_AUDIT_2026-09-09.md`.

## DONE (13 fixes, 3 build-clean batches, deploy next restart)
- **6 world tools** derive `success` from real outcome not hardcoded true: world_tile_set,
  world_tile_import, world_links_set, world_links_import, world_mutators_set, world_info_set.
- **prioritized_work**: `job.playerForced=true` (the sibling of the ordered_job fix that
  unblocked refuelling).
- **list_things**: `factionName` added beside `faction` — the confirmed incident.
- **social_gathering_start / ritual_start**: `success=started`. **map_fire**: `success=no
  failures`. **storage_settings**: `success=no refusals`.
- **pawn_gear** wear honours an explicit `stuff` (was silently discarded — same shape as
  the fuel-filter incident). **bill_add**: configure_bill's quality enum+range guard.
- **battery_set** setPct clamps 0-1.

## DEFERRED (need a live test cycle; recorded in the audit)
- #9 FindPawn name-ambiguity (shared helper, 19 callers — too risky to change blind).
- ~26 lower-value findings (per-field read-backs, exception-surfacing, field-name
  canonicalisation). All catalogued in the audit with file:line + one-line guards.
- `rimworld/get_cell_info` empty-things-on-populated-cell — lives outside JawaBench.

## verify
Deploy the companion (next restart) and confirm a known no-op write now returns
`success:false` (e.g. world_tile_set on an empty tile list, or a fully-refused
storage_settings). The playerForced fixes verified in-effect by a refuel job running.
