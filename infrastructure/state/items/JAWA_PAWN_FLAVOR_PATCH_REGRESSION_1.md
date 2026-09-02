# JAWA_PAWN_FLAVOR_PATCH_REGRESSION_1 — Jawa Pawn Flavor: 123 PatchOperationRemove failures

Caused by `PAWN_FLAVOR_PHASE2_APPLY_1`, discovered on the 2026-09-01 restart
that enabled `mandrake.rm.property`/`mandrake.rm.salvageclaim`/
`mandrake.rm.theft_hauler` (unrelated to those three mods — this is
`mandrake.rut.pawnflavor`, already active before that restart, and this is
the first cold load since `PAWN_FLAVOR_PHASE2_APPLY_1` deployed its patches).

## spec
`harvest_log.py`'s "patch operations failed" standing check read **128**
against a baseline of 5 (3 Intimacy - Gender Works + 1 Mining Outpost + 1
Biomes! Caverns, all pre-existing, all other mods). `--show patchfail`:
**123 of the 128 are `[Jawa Pawn Flavor — faction backstories and traits]`**,
all `PatchOperationSequence` whose `lastFailedOperation` is a
`PatchOperationRemove` targeting `Defs/MentalBreakDef[defName="..."]/label`,
`Defs/MentalStateDef[defName="..."]/...`, or
`Defs/ThoughtDef[defName="..."]/stages/li[N]/...` — e.g.:
```
[Jawa Pawn Flavor] Patch operation PatchOperationSequence(count=3,
lastFailedOperation=PatchOperationRemove(Defs/ThoughtDef[defName="Affair"]/stages/li[1]/...)) failed
```
`PAWN_FLAVOR_PHASE2_APPLY_1` shipped 1,781 rows via
`src/RimUtinni/PawnFlavor/Patches/PawnFlavorPhase2_{ThoughtDef,MentalBreak,Xenotype}.xml`
this same session; `validate_patch.py` reported 0 errors/0 warnings on them
(structural XML validity), but that check does not execute the patch
against a real def tree, so it never caught this. Leading hypothesis, NOT
yet confirmed: the generator's Remove-then-Add sequence assumes every
target def carries a literal `<label>`/`<stages>` child of its own, but a
`MentalBreakDef`/`ThoughtDef` that inherits `label`/`stages` from a
`ParentName` base (never overriding it) has no such literal node in its own
raw XML — `PatchOperationRemove` operates on the pre-resolution tree, so the
xpath finds nothing and fails. Needs confirming against the actual raw XML
of 2-3 failing defNames (e.g. `Affair`, `BedroomTantrum`) before writing a
fix — do not assume the hypothesis without checking.

## verify
- Read the raw (pre-patch, pre-inheritance) XML for several failing
  defNames to confirm or refute the ParentName-inheritance hypothesis.
- Fix the generator (`gen_pawn_flavor_phase2_apply.py`) so it targets the
  literal node that actually exists — a `PatchOperationReplace` keyed off
  content rather than assuming a literal child exists, or resolving through
  inheritance before deciding the xpath, or falling back to `Add` when
  `Remove` would find nothing.
- Regenerate all three patch files, `validate_patch.py` clean, then a live
  cold load: `harvest_log.py`'s "patch operations failed" back to baseline 5
  (or a lower, explained number if some subset is intentionally left as a
  different shape).
- Spot-check that the fixed defs' actual in-game text reads the approved
  flavor prose (this was `PAWN_FLAVOR_PHASE2_APPLY_1`'s own still-owed
  live-spot-check criterion — the two items should close together).

## criteria
0 new patch-operation failures attributable to Jawa Pawn Flavor on a live
cold load; the underlying cause is named (not just patched around); the
1,781 approved rows genuinely land in the running game, not just in
well-formed XML that never resolves.
