# ROT_WOUNDLINK_FIX_DROPPED_AT_THE_DOOR

Found 2026-10-22 by the Rot status audit: `python3 src/RimMandrake/TheRot/validation.py` read STATIC: FAIL. The donor
retirement (`b28a7414f`, 2026-10-18) deleted the Alpha Animals FindMod block in
`src/RimMandrake/TheRot/Patches/RotSpecies_WoundSharing.xml` (ROT_WOUND_SHARING_WIRING_1's wiring) without carrying it to
the ports. RM_Agaripod / RM_Agaripawn had it natively; RM_Chittik ("shares every wound it takes"), RM_Durrok and
RM_Mullgoth silently lost it, and `RM_TheRotFront.HealthSharingBodies` still named the AA_ bodies.

## spec
- RM_Chittik carries the wound link + RotNetwork natively (`Defs/Fauna/RM_Chittik.xml`).
- RM_Durrok / RM_Mullgoth (defs in mandrake.rsw.swbestiary) get wound link + kin-mending by an xpath-guarded
  PatchOperationConditional.
- The Health sharing toggle strips exactly the five RM_ bodies.
- Their HOME is an open owner question (both are multi-homed: Rot + Leaning Scrub, mullgoth also Cauldron):
  `design/RimMandrake/rot_open_questions_2026-10-22.md`.

## criteria
- A1 L0: `validation.py` static_checks wound-sharing block names the five RM_ bodies and passes (red before the fix).
- A2 L1: on a list holding TheRot + SWBestiary, `jawa/get_defs` shows CompProperties_WoundLink on RM_Chittik, RM_Durrok, RM_Mullgoth.
- A3 L2: on a quicktest map two spawned RM_Chittik share a wound; Health sharing off removes it.
