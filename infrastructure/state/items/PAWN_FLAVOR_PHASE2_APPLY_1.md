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
