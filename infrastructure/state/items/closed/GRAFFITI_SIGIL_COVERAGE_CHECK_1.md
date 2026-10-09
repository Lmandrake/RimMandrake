# GRAFFITI_SIGIL_COVERAGE_CHECK_1

Caused by `GRAFFITI_PUNK_IDEOLIGION_SCOPE_1` (forks ruled by question card 2026-10-09; rulings in that item and `design/RM_GRAFFITI_SCOPE_WIDENING.md` §7). Code: `src/RimMandrake/Graffiti/`.

## spec
Verify step 3 of the scope item: a committed script under `src/RimMandrake/Graffiti/` that reads the installed vanilla XML (never the def dump — it holds no IdeoIconDef/IdeoColorDef) and asserts (a) every IdeoIconDef `iconPath` resolves to a texture the tier-A frame can draw, (b) every IdeoIconDef `<memes>` gate names a real MemeDef, (c) the tier-C glyph defs (`requiresAnyMeme`) cover every non-structure `ludeon.*` MemeDef or name the exclusion. Zero rows read is a failure, not a pass.

## criteria
- O1 L0: the script runs against the install and prints per-check counts with a sanity floor; a missing install root is UNMEASURED, never PASS
