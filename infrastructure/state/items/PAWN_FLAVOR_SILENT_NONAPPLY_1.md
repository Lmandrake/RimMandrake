# PAWN_FLAVOR_SILENT_NONAPPLY_1 — a patched field can report success and still show vanilla text live

Found spot-checking `PAWN_FLAVOR_PHASE2_APPLY_1`/`JAWA_PAWN_FLAVOR_PATCH_REGRESSION_1`'s fix
on a fresh 592-mod cold load + quicktest colony (2026-09-02). Distinct from the regression
those two items fixed — that was 123 **logged, loud** `PatchOperationRemove` failures
(nothing existed to remove). This is different and worse: the patch reports **success**,
`harvest_log.py`'s "patch operations failed" check stays at baseline, and the live def
still shows the pre-patch vanilla text.

## spec
Confirmed via `jawa/pawn_thoughts` on multiple live colonists (not a def dump — the
in-game resolved `Thought.LabelCap`, which reads directly off `def.stages[idx].label`,
per `Verse/Thought.cs` and `Verse/Thought_Situational.cs`, no caching layer that should
survive a fresh process):

- `ThoughtDef::TreesDesired` (owned by `ludeon.rimworld.ideology`, stage 14/15) — approved
  text `"the trees astonish me"`, live still reads `"Trees sorely missed"` (vanilla stage
  14 text verbatim, from `Data/Ideology/Defs/PreceptDefs/Precepts_Trees.xml`).
- `ThoughtDef::TravelCompanions` (owned by `iforgotmysocks.caravanadventures`, stage 1/2)
  — approved text `"these people I travel with"`, live still reads `"Third wheel"`
  (vanilla).

Both reproduced on two separate colonists (`Human919`, `Human923`) on the same quicktest
map — not per-pawn variance.

Ruled out so far (all checked directly, not assumed):
- Not the Remove-vs-Conditional regression — both use the corrected
  `PatchOperationConditional(Replace/Add)` shape, confirmed by reading the deployed patch
  XML directly.
- Not a defName/stage-index mismatch — raw source XML for both defs has exactly the
  stage count our generator used (15 and 2 respectively), and the failing stage index
  matches the patch's own target index exactly.
- Not a `PatchOperationFindMod` gating error — both packageIds in the patch match the
  dump's own attribution AND the live `ModsConfig.xml` entries exactly (checked
  character-for-character); both owning mods are confirmed active.
- Not a duplicate/collision defName inside `Data/` (both defNames are declared exactly
  once in the vanilla+DLC tree) or inside our own `PawnFlavor` mod (each defName appears
  in exactly one of our three patch files).
- Not logged anywhere — a literal grep of the fresh `Player.log` for `TreesDesired` finds
  zero lines (no error, no exception, nothing).
- Meanwhile at least 5 other spot-checked rows across the SAME cold load DID land
  correctly (`Expectations`, `NewColonyOptimism`, `MentalBreakDef::BedroomTantrum`,
  `MentalBreakDef::Berserk`, `XenotypeDef::RSW_RimMandrakeJawa`) — so this is not a
  wholesale failure of the fixed generator, just some rows.

**Not yet checked**: whether some THIRD mod (not vanilla, not our own) also declares or
patches these exact two defNames and wins a load-order race — a full workshop-wide grep
timed out (100s) over WSL/9p and was not completed. This is the leading unconfirmed
hypothesis and the next thing to check.

## verify
- Finish the workshop-wide literal search for `TreesDesired` and `TravelCompanions`
  across all 592 active mod folders specifically (not the whole 1307-mod workshop tree —
  scope it to `ModsConfig.xml`'s active list first, which will be much faster than the
  timed-out unscoped attempt).
- If a colliding mod is found, confirm load order: does it load AFTER `mandrake.rut.pawnflavor`?
- If no collision is found, the next hypothesis is a C# comp/Harmony patch that recomputes
  the label at runtime rather than reading `def.stages[i].label` directly (the
  `disk-vs-runtime.md` "a C# comp computes the real value" pattern) — check via `ilprobe`
  for a Harmony transpiler/postfix targeting `Thought_Situational.LabelCap`,
  `ThoughtWorker_TreesDesired`, or `PreceptComp_SituationalThought`.
- Once the mechanism is identified, decide whether it's fixable in our own patch (e.g.
  reorder our mod to load later) or is a structural collision to document and accept.

## criteria
- Root cause named for both example defNames (not just patched around).
- A general rule stated for the generator/patch-authoring skill: how to tell in advance
  whether a `PatchOperationReplace`-style write will actually reach the runtime value,
  or whether some other mechanism will win.
- `PAWN_FLAVOR_PHASE2_APPLY_1`'s own "spot-check passes" criterion re-attempted with this
  understood — either these two rows are fixed, or the item's criteria is explicitly
  revised to accept a named, small residual list of non-landing rows.
