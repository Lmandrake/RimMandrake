# PAWNKIND_ROSTER_BACKSTORY_DRIFT_1

Filed by me, from `DEEPWATER_DEAD_GASMASK_TAG_1`: `gen_pawnkind_roster.py`'s
`KIT` table (the curated per-pawnkind block, ported in 2026-08-23 per
`PAWNKIND_GENERATOR_DIVERGED_1`) was missing the `backstoryFilters` that
`Jawa_Droid_Grunt/Heavy/Specialist/Leader` carry in the live
`JawaFactionRoster.xml` — the four `Neronix17.OuterRim.DroidDepot`-gated
droid pawnkinds, restricted to `JawaBSC_FDECathedral`/`JawaBSC_FDENightside`
backstory categories rather than ordinary Jawa ones, which makes sense for a
droid and nothing else in the roster carries it. Confirmed independent of
`DEEPWATER_DEAD_GASMASK_TAG_1` by regenerating on an untouched checkout:
48-line diff, same 4 blocks, with no gasmask edit applied at all.

## Fix

Ported the 12-line `<backstoryFilters>` block into all 4 `KIT['Jawa_Droid_*']`
entries in `src/RimMandrake/Utils/gen_pawnkind_roster.py`, placed exactly
where the live XML has it (immediately after `</apparelDisallowTags>`).

## Verify

`python3 src/RimMandrake/Utils/gen_pawnkind_roster.py` against the tree with
this fix produces **zero diff** on
`src/SPLIT_Phase3/Jawa_Patches/Defs/PawnKindDefs/JawaFactionRoster.xml` — the
regeneration contract the file's own header states ("Regenerating is now a
NO-OP DIFF... Empty means true") is true again for the first time since this
drift was introduced. XML re-parsed clean (`xml.etree.ElementTree`).

## criteria

Regenerating `JawaFactionRoster.xml` from `KIT` is a no-op diff. Met.
