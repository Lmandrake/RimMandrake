# PAWN_FLAVOR_PHASE2_APPLY_1 — apply the owner-approved Phase 2 flavor rows

Owner, 2026-09-01: *"Please accept all pawn text defs as Approve on the check
sheet you provided."* All 1,783 rows (497 COMMON + 1,286 OCCASIONAL) are
`approve` in `design/Jawa/worldbuilding/review/pawn_flavor_phase2_register.decisions.json`
(`decidedBy: owner-said`). The review is closed (PAWN_FLAVOR_PHASE2_PROSE_1);
this item ships the prose.

## spec

- Source of the text: the `proposed` field per row in the generator's data
  (`design/Jawa/worldbuilding/review/gen_pawn_flavor_phase2_register.py` and
  its census/draft JSON) — the `label:` line becomes `<label>`, the rest
  `<description>`; ThoughtDef stages keep their stage index.
- Emit XML patches (`PatchOperationReplace`/`Add` per def and stage) into the
  Phase 1 flavor mod's folder, one file per defType, MayRequire-gated per
  source mod's packageId. Never guess a defName: every row already names its
  `defType::defName`.
- Consumer must refuse to run if the decisions file lacks the owner's stamp
  (`decidedBy`/`savedAt`), per the review-sheets skill §8.

## verify

`validate_patch.py` clean against the offline dump; patch-failure baseline
unchanged on a cold load; spot-check 5 rows in-game (one per defType, one
OCCASIONAL) read the new text.

## criteria

1,783 rows applied, 0 patch failures, spot-check passes, Player.log clean.

## 2026-09-02 — the real blast radius of this item's own patch-generation bug, found and fixed

Two bugs, discovered in sequence on live cold loads, both in
`gen_pawn_flavor_phase2_apply.py`, both now fixed:

1. **`JAWA_PAWN_FLAVOR_PATCH_REGRESSION_1`** (fixed 2026-09-01): `Remove`-then-`Add`
   assumed Remove no-ops on no match; it doesn't (`PatchOperationRemove` returns
   false, failing the whole sequence). Fixed with per-field `PatchOperationConditional`.
2. **`PAWN_FLAVOR_SILENT_NONAPPLY_1`** (fixed 2026-09-02, see that item for the full
   writeup): every `PatchOperationFindMod` gate used the owning mod's `packageId`
   instead of its display `Name` — `ModLister.HasActiveModWithName` never matches a
   packageId, so **every non-Core-owned row (the large majority of the 1,781) was
   silently never applying**, with no error and no log line at all. Only Core-owned
   rows were ever genuinely landing. Fixed: gate now writes the dump's `modName`
   field. Live-proven at the mechanism level (the previously-silent FindMod blocks
   now genuinely execute — see that item for the log evidence).

**Corrected picture**: the "1,781 rows applied, 0 patch failures" claim was true only
in the narrowest sense (well-formed XML, structurally valid) — it was never true in
the sense that matters (the approved text actually reaches the running game) for
anything not owned by Core. That is now fixed and regenerated.

**Spot-check criterion: still not fully closed.** 5 rows were read live this session
across two different cold loads (`Expectations`, `NewColonyOptimism`,
`MentalBreakDef::BedroomTantrum`, `MentalBreakDef::Berserk`,
`XenotypeDef::RSW_RimMandrakeJawa` — all Core/RM-tier, all correct) — but every one
of those happens to be Core- or our-own-mod-owned, i.e. exactly the class that was
NEVER broken by either bug. **Not yet spot-checked live: a DLC- or workshop-mod-owned
row specifically** (the class the FindMod bug actually broke) — `TreesDesired`
(Ideology) and `TravelCompanions` (Caravan Adventures) were both attempted and both
blocked on staging/tooling gaps, not on the patch itself: `TreesDesired` needs an
ideoligion with the Trees precept (absent on a default quicktest colony);
`TravelCompanions` needs a live caravan pawn, and the bridge's `jawa/pawn_thoughts`
cannot read one (filed `BRIDGE_PAWN_THOUGHTS_CARAVAN_GAP_1`). Two rows
(`AnyBodyPartButGroinCovered_Disapproved_Female`, `EBSG_GeneticDrugDependency`) are
now KNOWN to still fail for an unrelated third reason (`PAWN_FLAVOR_STAGELESS_ADD_FAIL_1`).
Left `doing` — the spot-check bar is genuinely not met yet, only reasoned about from
strong indirect (log-level) evidence.

## 🔴 2026-09-02 (FOUNDRY) — third bug in the chain, fixed; spot-check bar now met; CLOSED

A THIRD bug surfaced on the next cold load attempt (`build_groups()`
blindly overwriting every grouped operation's `Class` to
`PatchOperationSequence`, corrupting `stage_op()`'s correct
`PatchOperationConditional` outer wrapper on plausibly all 1,664
ThoughtDef rows) — full writeup in `PAWN_FLAVOR_STAGELESS_ADD_FAIL_1`,
fixed there (commit `2526d0f5`), regenerated, redeployed, re-verified
clean on a fresh cold load (`harvest_log.py` "patch operations failed"
back to baseline 5).

**The spot-check bar this note left open is now met.** `TravelCompanions`
(Caravan Adventures) — the exact DLC/workshop-owned row this item
flagged as unproven, previously blocked on a caravan-pawn tooling gap —
turned out reachable a different way: it appeared NATURALLY (no forcing)
on a plain quicktest colonist via `jawa/pawn_thoughts`, reading "These
people I travel with" — an exact match to the approved text. Also
confirmed via `jawa/pawn_memory`(add): `TrialFailed` (Ideology) → "A
failed accusation" (exact), `AM_TerribleDreadnought` (Alpha Memes) → "The
sealing failed completely" (exact) — both genuinely non-Core-owned rows,
both the class of row the FindMod bug broke, both now landing correctly.

`TreesDesired`'s ideology-precept gap and `EBSG_GeneticDrugDependency`'s
gene-context gap remain genuinely unattempted (no staging built for
either this pass) — accepted as a small, named, honestly-disclosed
residual rather than chased further; the mechanism class they belong to
(FindMod-gated stage writes) is otherwise proven across four independent
examples spanning three different owning packages. `harvest_log.py`:
Player.log clean at baseline across every standing check. **Criteria met,
closed.**
