## why
`src/RimMandrake/Utils/gen_races_mod.py` is DIRTY after `SPECIES_TRAITS_OVER_APTITUDES_1` added six
OWNER-table entries. Its full-file review (gpt_consult `--lockdown`, job
`consult-20261103-000029-1810094`) reported six findings, all about behaviour older than that
edit and none verified yet:

1. `wrote = commit_staged()` runs before `verify()`: a failed acceptance check leaves written output.
2. `--check` exits before the asset comparison and `verify()`, so it can pass with broken references.
3. `ext_parents`: a generated def whose ParentName is a departing abstract is only printed, not failed.
4. `namemaker_for()` skips a candidate absent from the dump, ignoring donor XML naming fields.
5. Shipped XenotypeDef reconstruction (`out[dn] = {c.tag: ...}`) flattens nested elements and attributes.
6. `write_pawnkinds()` iterates `built` only, so orphan species get xenotypes but no pawn kinds on a fresh build.

The same review's claim about `RSW_SpeciesSignature.xml` (`MeleeDodgeChance` 8 = 800 %) is FALSE:
Core's stat is `toStringStyleUnfinalized FloatOne` and vanilla defs use offsets 15 and 8.

## verify
Each finding is either fixed (with a selftest case) or recorded here as false with the evidence,
and `code_review_status.py check src/RimMandrake/Utils/gen_races_mod.py` reads CLEAN.
