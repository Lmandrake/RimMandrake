# UTINNIPATCHES_LOAD_ORDER_CYCLE_1

**Status: CLOSED** (FOUNDRY, 2026-09-25). Thin item — no prose existed before
this pass; filed retroactively per FOUNDRY doctrine for a thin pickup.

## What was actually found

`mandrake.rut.patches` (`UtinniPatches`) declares `loadAfter` on 27 targets in
`src/RimUtinni/UtinniPatches/About/About.xml`. Measured against the **live**
`ModsConfig.xml` (628 active mods) before any fix: UtinniPatches sat at index
572, and exactly **6** of its declared-active `loadAfter` targets sat *after*
it — matching the item title precisely:

```
mandrake.rm.gelatinousslime   idx 577
mandrake.rsw.droidworks       idx 579
mandrake.rut.ashkarrflora     idx 576
mandrake.rm.flowworks         idx 585
mandrake.rm.pyrelands         idx 582
mandrake.rut.rustcathedralroaches  idx 593
```

(15 more declared targets are simply not in the active mod list — dangling,
harmless, left alone; not this item's scope.)

### The cycle — real, not a mismeasurement

`mandrake.rut.rustcathedralroaches`'s own `About.xml` declared
`loadAfter mandrake.rut.patches`, while `mandrake.rut.patches` declared
`loadAfter mandrake.rut.rustcathedralroaches` — a direct two-mod cycle,
unsatisfiable by any sort.

**Why UtinniPatches' side is real**: `Defs/BiomeDefs/RUT_RustCathedral.xml`
carries `<RUT_CathedralRoach MayRequire="mandrake.rut.rustcathedralroaches">0.12</RUT_CathedralRoach>`
in its `wildAnimals` list — a genuine cross-mod defName reference, gated the
way every other MayRequire target in that file is (per the file's own
`PATCHMODS_LOADAFTER_SWEEP_1` / `DIRTY_CODE_REVIEW_STANDING_LOOP_1` wave-81
convention). Kept.

**Why RustCathedralRoaches' side was NOT real**: checked every file in
`src/RimUtinni/RustCathedralRoaches/` for any actual mechanism needing
UtinniPatches loaded first — `ParentName`, `xpath`, `MayRequire` targeting
UtinniPatches or any content of it. Found **none**. RustCathedralRoaches has
no `Patches/` folder at all; it is three plain Defs (two ThingDefs, one
ThinkTreeDef) plus one ThingDef item, and its only real `modDependencies`
entry is `mandrake.rm.creaturebehaviors` (for `RM_EatCleanableExtension`).
The `loadAfter mandrake.rut.patches` line was boilerplate — the same
Core+creaturebehaviors+patches triplet several other small campaign mods
carry without a backing reference — not a real dependency.

## Fix applied

1. **Broke the cycle in source**: removed the unbacked `mandrake.rut.patches`
   `loadAfter` entry from `src/RimUtinni/RustCathedralRoaches/About/About.xml`,
   with a comment explaining why (checked, nothing depends on it). Kept
   UtinniPatches' own `loadAfter mandrake.rut.rustcathedralroaches` (backed by
   the wildAnimals reference above).
2. **Deployed** the corrected `About.xml` to the live Mods folder via
   `deploy_custom_mods.py --mod RustCathedralRoaches --apply` (plan showed
   exactly the one intended drifted file; verified in sync after apply).
3. **Fixed the live ordering problem** by hand-editing
   `ModsConfig.xml` directly (game was not mid-load; bridge was FREE) — per
   `rimworld-start-prep` doctrine, `modcheck run`/similar tools that touch
   `ModsConfig.xml` were avoided since they rewrite the whole list and can
   swap to MINIMAL unasked. Backed up the pre-edit file to
   `Transient/ModsConfig.xml.backup_UTINNIPATCHES_LOAD_ORDER_CYCLE_1` first.

   Moved `mandrake.rut.patches` to immediately after
   `mandrake.rut.rustcathedralroaches` (its now-latest surviving target, once
   the cycle was broken) — this alone satisfies all 6 previously-violated
   targets. Four mods that themselves declare `loadAfter mandrake.rut.patches`
   and were sandwiched between patches' old and new position
   (`mandrake.rm.divinginteraction`, `mandrake.rut.pawnflavor`,
   `mandrake.rut.pyrelandsmechanics`, `mandrake.rut.shokkweaveeconomy`) were
   moved along with it, in their original relative order, to keep their own
   `loadAfter patches` constraint satisfied (checked first that nothing else
   declares a `loadAfter`/`loadBefore` on any of those four that would break —
   only `mandrake.rm.terminalbiomes` references `mandrake.rm.divinginteraction`,
   and it was **already** violating that constraint before this change, at a
   position unrelated to this fix — pre-existing, out of scope, not touched).
   `mandrake.rut.pyrelandsmechanics`'s other constraint
   (`loadAfter mandrake.rm.pyrelands`) was re-checked and holds in the new
   order. Post-edit `activeMods` count unchanged at 628. Re-derived every
   affected index from the file after writing — all 6 original targets plus
   all 4 sandwiched dependents read `satisfied=True`.

## Not fixed, out of scope, flagged for whoever touches it next

- `mandrake.rm.terminalbiomes` (live idx 557) declares `loadAfter` on both
  `mandrake.rm.divinginteraction` (idx 590 after this fix) and
  `mandrake.rm.flowworks` (idx 581) and sits before both — a pre-existing,
  unrelated ordering defect, not caused or worsened by this fix. Not
  investigated further; whoever next touches TerminalBiomes' load order
  should treat this as a fresh finding, not assume this item covers it.

## Commit / close

Committed: `src/RimUtinni/RustCathedralRoaches/About/About.xml`, this item
file, and the FOUNDRY ledger shard. Live `ModsConfig.xml` edit is outside the
repo (Windows AppData) and not git-tracked; the pre-edit backup lives at
`Transient/ModsConfig.xml.backup_UTINNIPATCHES_LOAD_ORDER_CYCLE_1` for anyone
who wants to diff it.
