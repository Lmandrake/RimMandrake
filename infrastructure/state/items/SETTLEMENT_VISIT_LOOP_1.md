## spec
Full ruling: `design/Jawa/ownership_settlement_spec.md` (owner sitting 2026-08-31).
Build the **Inhabited** mod (RimMandrake tier, `mandrake.rm.inhabited`, `Inhabited_`
def prefix per `design/NAMING_SCHEME_PLAN.md`): the peaceful-entry visit
lifecycle for named frozen-world settlements, sitting on top of
`RM_Property` (built and committed this session, PROPERTY_FABRIC_BUILD_1).

Scope for this pass:
- **Manifest schema**: a settlement manifest def (districts present, sizes,
  adjacency, cast assignment slots, security props, faction security
  profile) — data-only shape, consumed later by DISTRICT_TEMPLATE_LIBRARY_1.
  This item does NOT author district content, only the schema + a loader.
- **Lifecycle**: arrival → compose (stub: single placeholder district until
  the template library lands) → cast → routes → departure → teardown to
  roster. Teardown persists a lightweight "casing" record (what the colony
  now knows about this settlement — not full map state) so a return visit
  can read prior knowledge without holding the whole map in memory.
- **Gate-search hook**: departure-time check reading the settlement's
  security profile (spec: "a faction searches leavers only if its profile
  says so") — stub the profile source as a def field for now, real per-
  faction tuning is RimUtinni data landing with SETTLEMENT_VERBS_WAVE_1.
- **Junkers pilot manifest** (RimUtinni data): one real settlement manifest
  using an actually-named Jawa_Junkers settlement from
  `design/Jawa/worldbuilding/ASHKARR_WORLD_DEFINITION.md` (candidates: The
  Ore Moot, The Claim Jump, The Slagfield, The Fuel Works — pick one, low
  security per spec's "Junkers pilot: low security, forgiving").

Explicitly OUT of this item: district Lua templates (DISTRICT_TEMPLATE_LIBRARY_1),
crime/commerce/social verbs (SETTLEMENT_VERBS_WAVE_1), any claim-math change
(owned by RM_Property, do not touch).

## verify
- `validate_patch.py` clean against the live mod set.
- `Def.ConfigErrors()` triage: FOUNDRY runs a live quicktest cold load after
  build, greps `Player.log` for `^Config error in`, fixes or documents any hit
  (see memory: config-errors-are-invisible-to-validate-patch).
- Live-quicktest-observed: the visit lifecycle actually runs start-to-finish
  on the Junkers pilot manifest — arrival fires, a placeholder district
  composes, departure fires the gate-search hook (log line or screenshot),
  teardown leaves a casing record readable on a second visit.
- Folder-basename check before deploy: confirm via `deploy_custom_mods.py`
  plan output that `Inhabited`'s folder name is unique across
  RimMandrake/RimStarWars/RimUtinni/SPLIT_Phase3 (this exact collision has
  hit twice already this session — fire ecology, weather suite).

## criteria
A correct v1: the Inhabited mod loads, RM_Property's claim engine is
untouched, one real Junkers settlement can be visited start-to-finish on a
quicktest map with a stub district, and a casing record persists across a
second visit. District art/verbs are deliberately absent — this item proves
the LOOP, not the content.
