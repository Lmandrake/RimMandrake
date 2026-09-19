# SALVAGECLAIM_WALK_STALE_1

## ask (as filed, 2026-09-16T22:59:08Z by BENCH)
`design/validation_walks/RimMandrake/SalvageClaim.md` names a subject that no
longer exists (`src/RimMandrake/SalvageClaim` is gone, consolidated into
RimProperty) — re-point or retire the walk, and check whether `Property.md`
already covers it.

## verified 2026-09-18 (FOUNDRY)

- **`src/RimMandrake/SalvageClaim` is confirmed gone** — no such top-level mod
  folder. The feature lives on as a subfolder inside RimProperty:
  `src/RimMandrake/RimProperty/Source/SalvageClaim/` (`FloatMenuOptionProvider_
  PaySalvageClaim.cs`, `SalvageClaimFeeUtility.cs`).
- **But the walk's premise is already stale, not the walk itself.** Commit
  `071a4e667` ("Every checklist now names a folder that exists", 2026-09-17,
  i.e. the day AFTER this item was filed) already repointed
  `SalvageClaim.md`'s `subject:` line to `src/RimMandrake/RimProperty
  (packageId mandrake.rm.property)`, with an `absorbed:` line documenting the
  merge (commit `f32eef5f5`). The file no longer names a dead path.
- **`Property.md` does NOT cover the same ground.** `Property.md` walks the
  core `PropertyEngine`/`ClaimEngine`/ledger fabric (decay curve, claim-basis
  recording, defs-free load). `SalvageClaim.md` walks a distinct, still-live
  feature: the "pay salvage claim fee" float-menu order
  (`FloatMenuOptionProvider_PaySalvageClaim`, `SalvageClaimFeeUtility.
  ComputeFeeSilver`), including its fee-bound math and its own bridge-driven
  walk steps. This is exactly the SUBJECT_COLLISION pattern CLAUDE.md's Facts
  section already names as deliberate (34 of 78 walks share a live mod's
  subject on purpose) — not rot.
- Grepped every other inbound `SalvageClaim` reference in the repo
  (`design/INDEX.md`, `design/MOD_CONSOLIDATION_PLAN.md`,
  `design/RimMandrake/north_star_validation_spec.md`,
  `infrastructure/DETERMINISM_ASSESSMENT.md`, plus rimflow item/queue
  entries) — all correctly describe the historical merge into RimProperty;
  none assert the dead top-level path or need correction.

## outcome

Nothing to delete, nothing to re-point — the walk file was already fixed
before this item reached the top of the queue, and it is not redundant with
`Property.md`. Closing DONE per CHARTER's 2026-09-18 ruling (any seat may
close an item it finds genuinely done).
