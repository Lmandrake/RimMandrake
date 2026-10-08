# Dependency sweep (NO_DEPENDENCY triage) 2026-10-07

## Before (old lint, text-substring test): 172 distinct refs / 77 mod pairs, all WARN NO_DEPENDENCY
## After (`lint_def_type_refs.py`, refs / mod pairs)
- INTRA_COMPOSITION 294/51 (both mods folded into mandrake.rm.biomes; benign)
- GUARDED_DEP 158/29 (referrer's hard-dependency closure reaches owner; includes UtinniPatches after its fix)
- GUARDED_XML 55/42 (FindMod `<match>` by NAME or packageId, MayRequire on non-Operation, LoadFolders IfModActive)
- GUARDED_COND 1/1 (PatchOperationConditional whose xpath tests a def the owner declares)
- QUERY_ONLY 7/7 (type only inside a patch `<xpath>`)
- REAL 1/1 (StarWarsRaces -> armoury, proposal below). Before the About fix there were 14 refs / 6 pairs, all UtinniPatches (plus this one).
Note the old test counted any mention (description, loadAfter) as "naming" the owner; the new one needs a hard modDependencies chain, so loadAfter-only no longer passes (selftest plants it).

## About.xml changed (1)
- `D:\Luke\dev\RimMandrake\src\RimUtinni\UtinniPatches\About\About.xml`: added hard modDependency `mandrake.rm.biomes` (RUT -> RM, allowed). Covers 8 unguarded owners now folded in it: EnvironmentalHazards, CreatureBehaviors, Stillsand, BlueDesert, WeepingStones, Greentide, Miasma, Wasteland (e.g. BiomeDefs RUT_WeepingStones.xml, RUT_Webwork.xml). It was only a loadAfter before.
- No composed mod's About.xml touched; no composed referrer has a REAL finding.

## Direction violations (FINDINGS, not fixed)
- Declared: `mandrake.rm.shipvermin` (RM) hard-depends on `mandrake.rsw.swbestiary` (RSW). Not a type reference; decide whether ShipVermin belongs in RSW or the dependency should go.
- Type references: none (no RM referrer needs RSW/RUT, no RSW needs RUT).

## Proposal (not applied; outside About.xml scope and a judgement)
- `RimStarWars/StarWarsRaces/Defs/Misc/SW_Support.xml`: DamageDef `RSW_RangedDamage_ink` has `<li Class="guy762_Ionization.ModExtension_HediffGiver">`, a type compiled in `mandrake.rsw.armoury`. StarWarsRaces ("Contains no compiled code") has no dependency chain to it. Adding armoury as a hard dep drags VFE core, Harmony etc. into a species mod; preferred fix: add `MayRequire="mandrake.rsw.armoury"` to that `<li>` (valid on an `<li>`), or move the DamageDef into armoury. Nothing else references the def.

## How to run
- `python3 src/RimMandrake/Utils/lint_def_type_refs.py` (add `-v` to list every classified pair, `-q` for FAIL only, `--mod X`)
- `python3 src/RimMandrake/Utils/selftest_lint_def_type_refs.py` (36 checks incl. planted real missing deps: no-dep, loadAfter-only, MayRequire on Operation, FindMod nomatch, wrong FindMod, unfolded/late compose entry; and the guarded shapes plus direction)
- Files changed: lint_def_type_refs.py, selftest_lint_def_type_refs.py (Utils); UtinniPatches About.xml. Uncommitted per brief.
