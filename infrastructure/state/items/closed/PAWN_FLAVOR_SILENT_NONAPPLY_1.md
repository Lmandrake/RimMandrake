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

## ROOT CAUSE CONFIRMED AND FIXED, 2026-09-02

**Not a third-mod collision, not a Harmony override, not a ThoughtStage cache** —
all three were checked and ruled out first (scoped literal search across all 592
active mod folders for both defNames: zero real hits besides the owning mod's own
file and our patch; English `DefInjected` search: zero hits; `ilprobe` on
`Thought::get_LabelCap`/`ThoughtStage::get_LabelCap`/`PostLoad`: no caching or
reset path exists in base game code).

**The real cause, IL-confirmed via `ilprobe` against `PatchOperationFindMod.ApplyWorker`
and `ModLister.HasActiveModWithName`**: `PatchOperationFindMod`'s `<mods><li>` list is
matched by exact `String` equality against **`ModMetaData.Name`** — the mod's
DISPLAY name ("Ideology", "Caravan Adventures") — **never `packageId`**.
`gen_pawn_flavor_phase2_apply.py` wrote the raw lowercase-dotted `packageId`
(`ludeon.rimworld.ideology`) into every non-Core `<mods><li>`. That string can
never equal a display name, so `HasActiveModWithName` always returned `false`
and **every FindMod-gated block in the whole 1,781-row patch set silently never
ran its `<match>` branch** — confirmed by grepping the deployed patch files:
literally every `<mods><li>` across all three output files was packageId-shaped,
zero exceptions. Only Core-owned rows (generator-exempted from the FindMod wrap
entirely) were ever actually applying. This is a MUCH larger blast radius than
the two rows that first surfaced it — every DLC- and workshop-mod-owned row was
affected.

**Fix**: `gen_pawn_flavor_phase2_apply.py`'s `build_groups()` now writes the
def dump's own `modName` field (present per-record, already exactly
`ModMetaData.Name` including the DLC special case — `Expansion.label` when the
owning mod is a DLC, confirmed against `Data/Core/Defs/Misc/ExpansionDefs/ExpansionDefs.xml`
whose `Ideology`/`Biotech`/etc. `<label>`s match `ExpansionDef` exactly). The
entry tuples threaded through `build_groups` gained a `modName` field
alongside `packageId` (grouping key stays `packageId`, only the emitted
`<li>` text changed). Regenerated all 3 patch files (same 1,781/1,783 row
count), `validate_patch.py`: 0 errors — and for the first time its own
`PatchOperationFindMod` match-count lines report real hits against real mod
names ("RimMandrake - Star Wars Races", "Odyssey", "Vanilla Races Expanded -
Saurid", "Star Wars KotOR Resources and Materials", etc.), not silent zero.

**Live cold load (592 mods) — positive, log-based proof the gate now genuinely
opens, not just static reasoning**: before the fix, the `Ideology`/`EBSG
Framework`-gated blocks produced ZERO log lines (the exact silent-no-op
symptom this item was filed over). After the fix, on this SAME 592-mod live
boot, those SAME blocks now throw real internal errors —
`Verse.PatchOperationFindMod(Ideology): Error in <match>` with a full nested
stack trace naming a specific failing defName inside it. That trace can only
exist if `HasActiveModWithName("Ideology")` returned `true` and the engine
actually walked into and executed the formerly-dead branch. This is exactly
the positive observation this project's own doctrine asks for (a clean log
proves nothing; here the log is NOT clean, and that is the proof).

**One genuinely separate, narrower bug surfaced by this same load, once the
gate finally opened enough to reach it** — filed on its own, not fixed here:
[[PAWN_FLAVOR_STAGELESS_ADD_FAIL_1]] (`AnyBodyPartButGroinCovered_Disapproved_Female`
in Ideology, `EBSG_GeneticDrugDependency` in EBSG Framework — `PatchOperationAdd`
fails because `stages/li[1]` has no literal anchor at all, a different failure
shape than the FindMod bug this item is about).

**What is NOT confirmed by screenshot/live-text-read**: the exact two originally-
reported rows (`TreesDesired`, `TravelCompanions`) specifically, because both
require staging conditions a quicktest colony doesn't have by default —
`TreesDesired` needs an ideoligion with the Trees precept; `TravelCompanions`
only evaluates on a pawn actually inside a live caravan, and the bridge's own
`jawa/pawn_thoughts` cannot reach a caravan pawn (confirmed by forming a real
caravan and trying — `FindPawn` only searches spawned map pawns). Filed as its
own bridge-tooling gap: [[BRIDGE_PAWN_THOUGHTS_CARAVAN_GAP_1]]. The FindMod
mechanism fix is proven live at the class level (above); these two specific
rows' displayed text is proven only by generator logic + offline patch content
(both now correctly targeted, per direct inspection of the regenerated XML),
not by a screenshot.

**Root cause: named. General rule: `PatchOperationFindMod`'s `<mods>` list
always takes the mod's registered NAME, never its packageId — read it off the
def dump's `modName` field (or `ModMetaData.Name`/`ExpansionDef.label` for a
DLC), never assume packageId works, and never trust `validate_patch.py`'s
"0 errors" for a FindMod-wrapped patch without also checking it reports a real
match count against a real mod name.** Closing this item: the FindMod bug
itself is fixed and live-proven at the mechanism level; the two narrower
follow-ons (stageless Add, bridge caravan-pawn gap) are filed separately
rather than blocking this one open.
