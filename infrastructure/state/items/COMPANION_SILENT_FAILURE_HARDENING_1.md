# Companion silent-failure hardening

Owner (2026-09-09, "deep work" sitting): harden the JawaBench companion against the
silent-failure class that cost hours during the ship work. Full audit (39 findings):
`design/Jawa/reviews/COMPANION_HARDENING_AUDIT_2026-09-09.md`.

## DONE (13 fixes, 3 build-clean batches, deployed batch 3)
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

## DONE (batch 4, 2026-09-11, ~27 lower-value findings, build-clean --gm, deployed)
- **world_view** (#6, the 7th world tool): `success` now derived from the read-back
  `worldSelected` state matching the request, not hardcoded true.
- **pawn_stats / thing_stats** (#11): a `shown` classification exception is reported in a
  new `shownErrors[]` instead of silently folding into "not shown".
- **connect_cells** (#13): `isBridgeable`'s exception text now surfaces in the endpoint
  refusal (`bridgeCheckError`) instead of reading as a confidently-wrong "not bridgeable".
- **pawn_gear wear** (#16): `displaced[]` now reports apparel Wear() itself dropped via
  CanWearTogether, diffed before/after (previously only equip's primary-slot displacement
  was visible).
- **pawn_health add** (#17): `AddHediff`'s return is now verified against `hediffSet`
  before reporting success, mirroring this file's own equip/restore pattern.
- **set_pawn_ideo role** (#18): `Precept_Role.Assign` is now verified via `IsAssigned`,
  mirroring the sibling action=set path's SetIdeo verification.
- **pawn_psychic psyfocus** (#19): `success` now flips false when every requested
  sub-action (offset/clearEntropy) failed.
- **pawn_get** (#20): listing (no `pawn` given) now reports `totalSpawned` and `truncated`
  alongside the capped `pawns[]`.
- **map_skyfaller** (#22): `success` now folds in `innerThingCarried` when an `innerThing`
  was explicitly requested (previously ignored whether the payload actually landed).
- **royal_title** (#23): `success` now requires the post-call read-back
  (GetCurrentTitle/GetFavor) to match what was requested, for all four actions.
- **anomaly_knowledge** (#24): the overflow category's own project knowledge is now
  independently read back before/after (`overflowProject`, `overflowKnowledgeBefore/After`).
- **set_terrain_layer** (#25): `under`/`color` layers now diff the terrain grid
  before/after instead of incrementing `changed` unconditionally.
- **designate_batch** (#26): the remove path now reports `alreadyAbsent` (add already had
  `alreadyPresent`).
- **map_zones** (#27): both bare `CheckContiguous()` catches now surface the exception
  (`notes[]` / `checkContiguousError`) instead of swallowing it silently.
- **list_pawns** (#30): per-capacity read exceptions are now collected into
  `capacityErrors[]` instead of being indistinguishable from "pawn lacks this capacity".
- **get_defs / Scalars** (#31): a field read that throws now reports
  `"(threw: <ExceptionType>)"` instead of reading identically to "no such field".
- **map_info** (#33): each tile field (biome/hilliness/elevation/...) is now read inside
  its own try/catch (`fieldErrors[]`) instead of one throwing accessor blanking the whole
  `tileInfo` block.
- **map_info / prefab_list** (#32): the `-1` sentinel on
  `playerSettlementsOnThisTile`/`CountPrefabThings` is now documented in
  ResultDescription/XML comments as "threw", never a genuine zero.
- **room_get** (#34): a `PsychologicallyOutdoors` exception now excludes the room
  (fail-safe toward the documented default) instead of defaulting to indoors and leaking
  a genuinely-outdoor room past `includeOutdoors=false`.
- **set_stuff** (#35): the two cosmetic bare catches (Notify_ColorChanged/DirtyMapMesh)
  now surface into a `notes[]` field instead of vanishing silently.
- **pawn_traits / set_pawn_style** (#39, partial): `GenerateApparelOfDefFor`,
  `BackstoryDef.DisallowsTrait` and the disabled-work-types readback now note the
  exception (`notes[]`/`warnings[]`/`disabledWorkTypesError`) instead of discarding it.
- **world_objects_add** (#37): the collision check now also refuses via `def.canHaveMap`
  (reusing world_settlements_import's guard), not just exact-def equality.
- **world_tile_validate** (#38): the `tolerance` parameter's ToolParameter description now
  states explicitly that swampiness/pollution use a fixed 0.02 tolerance regardless.

## SKIPPED this batch (riskier or more ambiguous than the audit's one-liner)
- **#28 spawn_batch filth thickness**: the code already carries an extensive comment
  explaining FilthMaker.TryMakeFilth ORs multiple thickening passes into one bool by
  design, and that ResultDescription already documents the count as an attempt, not a
  verified placement. Diffing filth thickness on the cell is a real fix but not a
  one-liner (multiple filth things can already occupy a cell) — left for a session with a
  live test cycle.
- **#29 set_pawn_style hairColor `ok`**: NOT a bug — the code already has an inline
  comment explaining the read-back can legitimately differ (get_HairColor filters
  rot/shambler colour) and deliberately reports `ok=true` with a `note` rather than
  failing on that expected divergence. Forcing strict equality would reintroduce false
  failures the existing design already reasoned through.
- **#4 wipe_cell refundConfirmed**, **#5 social_marry rollback**: both need a live-map
  re-query/rollback verified in play, not just a compile — left with #9 for a live cycle.
- **#10 TryRect requested-vs-clipped size**, **#14 ordered_job JobCondition surfacing**:
  ranked findings, not part of the ~26 lower-value bucket; #10 touches ~10 shared call
  sites and #14 needs JobDriver internals — both real design work, not one-liners.
- **#15 field-name canonicalisation**: cross-cutting rename across many tools/callers;
  changing field names on a live bridge API is a breaking change for any existing caller
  and needs a deliberate migration, not a mechanical pass.

## DEFERRED (need a live test cycle; recorded in the audit)
- #9 FindPawn name-ambiguity (shared helper, 19 callers — too risky to change blind).
- `rimworld/get_cell_info` empty-things-on-populated-cell — lives outside JawaBench.

## verify
Deployed batch 4's DLL 2026-09-11 (build --gm --apply, 0 warnings/errors, GM pair
verified present, no tool-surface removal). Confirm on next restart: a known no-op write
still returns `success:false` (batches 1-3, previously verified) and spot-check a couple
of batch 4's read-backs (e.g. royal_title's success now requires the title/favor
read-back to match, room_get's outdoorsCheckErrors on a thrown PsychologicallyOutdoors).

## 2026-09-11 update — no-op check CONFIRMED live

`jawa/world_tile_set` called with no `tiles`/`range` (the tool's own true
no-op shape) on the 592-mod full list, canonical save: `success: false`,
`"message": "Give 'tiles' and/or 'range'."` — the fix holds. Batch 4's
royal_title/room_get read-backs not separately spot-checked this pass (ran
out of session time); the core verify criterion (a known no-op returns
`success:false`) is met. #9 and the `get_cell_info` item remain DEFERRED as
already recorded.

Side finding while testing (not a hardening-audit item, filing here for the
next pass): `jawa/spawn_batch` throws an unhandled `NullReferenceException`
rather than a clean refusal when given a pawn-race `ThingDef` (its
GenSpawn-only path doesn't expect one) — `jawa/spawn_pawn` is the correct
tool for pawns and works fine. Low severity (wrong-tool-for-job, not a
silent wrong-answer), but an unhandled NRE is still the exact class this
item exists to close.
