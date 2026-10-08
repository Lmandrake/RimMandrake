# PLANT_INTERACTION_GUARDS_1 — Huge Things plant interaction guards

Filed 2026-10-07 by BENCH from `HUGE_THINGS_GPT_REVIEW_1` (full GPT review of the merged Huge Things, `c954ccdca`). Mod: `src/RimMandrake/HugeThings`. Do not deploy as part of filing.

## spec
Verified fix-now findings from `Transient/huge_things_bounds_2026-10-07/GPT_FULL_REVIEW.md` (triage `Transient/huge_things_bounds_2026-10-07/GPT_FULL_REVIEW_TRIAGE.md`), all re-checked on code and on the 1.6 decompile (RimSage).

- **A3.4**: `MapComponent_HugeFootprints.Flags` (`:310`) uses `def.hasInteractionCell` and a single `InteractionCell`. In 1.6, `ThingUtility.InteractionCellsWhenAt` enumerates `multipleInteractionCellOffsets`, and `GenConstruct.NotBlockingAnyInteractionCells` resolves Blueprint/Frame via `entityDefToBuild`. A generated blueprint def never copies `hasInteractionCell`. Fix: do the same as vanilla and widen the scan margin.
- **A3.6 (mechanical half only)**: `MoveItems` (`:252`) despawns items. In 1.6, `Thing.DeSpawn` releases reservations and sends the quest "Despawned" signal. Fix now: never move a thing with non-empty `questTags`; defer its cell instead. The wider relocation policy is owner question Q8 in the triage.
- **A3.7**: `Building_TrunkBlocker.SourceKey` (`:61-63`) keys on instigator + weapon + damage def + tick. Pellets or burst rounds from one launcher in one tick collide, and later hits are dropped. In 1.6 `Bullet.Impact` makes one DamageInfo per projectile. Fix: apply the tick dedup only to area events (explosions; any multi-cell titan step), and forward single-projectile hits un-deduped. Direct hits on the plant must join the same area-event dedup.
- **C3.3**: `HugeThingsApi.PawnHitbox` (`HugeThingsCore.cs:98`) reads only `bodyGraphicData.drawSize`. In 1.6, `PawnRenderNode_AnimalPart.GraphicFor` picks an alternate graphic or `femaleGraphicData`, and the mesh follows that graphic's drawSize. Fix: resolve the active graphic and take the max.
- **C3.10**: `Patch_DamageWorker_ExplosionDamageThing.Prefix` (`HugeThingsCore.cs:178-186`) swaps blocker→plant without reading `ignoredThings`. In 1.6, `ExplosionDamageThing` then tests the plant. Fix: add the `ignoredThings` parameter and return false when the blocker is ignored.

## verify
Fuzz and lint pass. Each fix has a fixture or case that fails when the fix is reverted: rotated multi-interaction-cell building, blueprint, two same-tick pellets, ignored-blocker explosion, female-graphic hitbox.

## criteria
A1: the five bullets are fixed in source. A2: a regression case exists for each one.

NEXT: claim it and fix the bullets in order, citing the review IDs in the commit.
