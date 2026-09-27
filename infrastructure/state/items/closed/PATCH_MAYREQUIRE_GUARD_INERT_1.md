# PATCH_MAYREQUIRE_GUARD_INERT_1 — top-level `<Operation MayRequire=…>` is ignored by vanilla

## spec
MEASURED from the decompiled engine (2026-09-27): `ModContentPack.LoadPatches`
builds every `<Operation>` unconditionally; MayRequire/MayRequireAnyOf are
honoured only on top-level defs (`LoadedModManager`), def-reference fields and
list items (`DirectXmlToObjectNew`). So a patch "guarded" by
`<Operation Class=… MayRequire="some.mod">` applies even when that mod is absent.

This crashed the full list on 2026-09-26/27 (`BLUEDESERT_ORPHAN_LOAD_CRASH_1`,
fixed at `99776e796`): two Sump recipe patches added costLists naming
`mandrake.rm.thesump` defs while that mod was inactive → null ingredient →
`RecipeDefGenerator` NRE → ModsConfig reset to Core-only.

74 more such Operations remain in `src/` (`grep -rn '<Operation [^>]*MayRequire' src`).
For each: decide whether it can inject a cross-reference (costList, recipe
ingredients, def-ref fields, wildAnimals rows) to a def owned by the
"required" mod. If so, re-gate it — a `PatchOperationConditional` whose xpath
requires the donor def (`/Defs[ThingDef/defName="X"]/…`) or
`PatchOperationFindMod`. Drop the inert MayRequire either way so it stops
reading as a guard.

## verify
The grep above returns 0 lines in `src/`, and a full-list load logs no new
"Could not resolve cross-reference" lines from the touched patches.
