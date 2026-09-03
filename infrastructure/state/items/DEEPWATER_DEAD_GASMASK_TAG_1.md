# DEEPWATER_DEAD_GASMASK_TAG_1

Jawa_Deepwater_{Grunt,Heavy,Specialist,Leader} carried `KotORHeadband_gasmask`
in `apparelTags`. No ThingDef anywhere in the mod set (repo-wide grep, all
tiers) carries that tag — the only surviving KotOR headband tag is
`KotORHeadband_bandana` — so the entry matched nothing and was inert dead
weight, not a live restriction.

## Fix

The generator was the real source (per its own header: "EDIT THE KIT HERE,
not in the XML"). Removed the 4 `<li>KotORHeadband_gasmask</li>` lines from
`KIT_PRE` in `src/RimMandrake/Utils/gen_pawnkind_roster.py`, then applied the
identical 4-line removal directly to the generated
`src/SPLIT_Phase3/Jawa_Patches/Defs/PawnKindDefs/JawaFactionRoster.xml` —
not via a full `python3 gen_pawnkind_roster.py` regeneration.

## Found in passing, filed separately (not fixed here)

A clean-tree regeneration of `JawaFactionRoster.xml` also deletes
`backstoryFilters` (JawaBSC_FDECathedral/JawaBSC_FDENightside) from 4
DroidDepot-gated PawnKindDefs — pre-existing drift, confirmed independent of
this fix by regenerating on an untouched checkout (48-line diff with no
gasmask edit applied at all). That's `KIT_PRE` missing content the live XML
carries, the same class of bug the file's own 2026-08-23 header warns about.
Filed as `PAWNKIND_ROSTER_BACKSTORY_DRIFT_1` rather than fixed here — out of
this item's scope, and the two are independent (fixing one doesn't touch the
other).

## Verify

`python3 -c "import xml.etree.ElementTree as ET; ET.parse('src/SPLIT_Phase3/Jawa_Patches/Defs/PawnKindDefs/JawaFactionRoster.xml')"` —
well-formed. `grep -rn KotORHeadband_gasmask src/` — zero hits anywhere in
the repo after the fix.
