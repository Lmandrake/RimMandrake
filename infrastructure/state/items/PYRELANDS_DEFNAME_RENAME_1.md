# PYRELANDS_DEFNAME_RENAME_1 — `RM_FE_Pyrelands` → `RM_Pyrelands`

## the ask

🔴 **Owner ruling, 2026-09-21 (BENCH question card): rename now.**

The `FE_` infix is a leftover and is visible in the defName forever if it ships.
MEASURED before the ruling: **14 files, 52 occurrences, 3 live C# strings, and ZERO
references in the canonical save** — so the rename is free today and costs a
save-migration later. It also unblocks `design/RimMandrake/biome_mod_architecture.md` §7 Q3.

## spec

1. `RM_FE_Pyrelands` → `RM_Pyrelands` across all 14 files, including the 3 C# string
   literals (a C# string is not caught by an XML sweep — change them by hand and rebuild).
2. Rebuild the assembly and deploy.
3. Re-verify the save still holds zero references AFTER the rename, not just before.

## Watch out

- ⛔ **The tile count is not the instrument here and must not be cited.** The planet is
  painted once at the end; a biome of ours on 0 tiles is the expected mid-migration state.
- The canonical save is `CANONICAL_ASHKARR_START_2026-09-12.rws`. Back it up before any
  save-touching step, and confirm its byte size is unchanged if you do not intend to edit it.

## criteria

Zero occurrences of `RM_FE_Pyrelands` in `src/`, the assembly rebuilt and deployed, and a
re-measured zero references in the canonical save.
