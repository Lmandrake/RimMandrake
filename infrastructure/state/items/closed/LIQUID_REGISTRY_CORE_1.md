# LIQUID_REGISTRY_CORE_1 — the LiquidDef registry skeleton, adopting existing terrains

Filed by BENCH, 2026-09-13. Owner-ruled architecture: core registry + client
mods (`design/RimMandrake/liquids_framework_design.md` §2–3 — the spec lives
there, not here).

## spec

In LiquidTypes (growing into `RimMandrake: Liquids`): the new top-level def
type `RimMandrake.LiquidTypes.LiquidDef` with the property block and nullable
form slots per design §2; v1 rows per design §3 including the brine/propane
minimal rows forced by the frozen world's authored bodies. Rows ADOPT existing
terrains (vanilla waters, Odyssey toxic suites, LiquidTypes suites, ManyWaters
colors, GelatinousSlime slime) — no terrain is re-authored. Grow
`Tools/generate_liquid_suite.py` to emit terrain suites, bottle ThingDefs and
the compat index from rows. ConfigErrors: a row with zero form slots is an
error.

## verify

Def-load test only for this slice: minimal list + the mod, zero red errors,
zero "Config error in" lines in Player.log (grep the live log — validate_patch
cannot see config errors). Every row resolves every non-null slot reference.

## Watch out

- LIQUID_TYPES_MOD_1 (FOUNDRY, doing) is the umbrella this now specs; its
  older roster prose is superseded by design §3.
- Top-level custom def type, never `<li>` custom-loading (the loader trap
  discards whole defs silently).
- Adopted third-party terrains are patched via `RM_LiquidProperties`
  extension, not required into rows — MayRequire needs a readable packageId.
