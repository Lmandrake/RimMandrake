## spec
🔴 **The producer fix alone could not have worked, and we would have learned that
25 minutes after launching.** Found offline on 2026-08-21 while checking that our
readers survive the manifest shape `RimDefDump` `d7cf154` writes.

`RimDefDump` `d7cf154` separates colliding types into `<SimpleName>.json` and
`SafeFileName(<FullName>).json` and adds a `defTypes[]` index saying which type
owns which file. **`measure` threw all of that away on arrival:**
`capture.def_type` was a `TEXT PRIMARY KEY` on the **simple** name, so two slices
could not coexist, and the "two files claim this type" branch **deleted both**.

Measured on a synthetic faithful to `DefDumper.cs` (header carries the SIMPLE name,
`:510`; `defCounts` keyed on the FILE STEM, `:183-186`; loser written as
`<FullName>.json`, `:479`):

| | before | after |
|---|---|---|
| `AbilityDef` rows in `defs` | **0** of 630 on disk | 612 + 18, both `complete` |
| `build` says / table holds | **615 / 3** | 633 / 633 |
| `count Verse.AbilityDef` | UNMEASURED, shadowed | **MEASURED 612** |

⚠️ **Second defect, same root:** `stats.defs_inserted += n` ran before the deleted
rows were subtracted, so `build` announced a total it did not hold — the package's
own named failure mode, inside the package. 🔑 **It cannot fire on a capture where
the shadowed type declares 0**, which is why nobody had seen it: today `AbilityDef`
declares 0 because the EMPTY type won the filename. **The producer fix is what arms
it**, with exactly the 824 defs the fix is for.

## verify
`python3 scripts/selftest_measure.py` in `D:\Luke\dev\measuring-large-artifacts`.
**47/47 passed, 0 skipped**, including five new cases: both slices kept, `build`
reports the rows it holds, a full name counts exactly, a shared simple name refuses
without summing, and the file stem is not swept in as a phantom type.

🔑 **The regression that mattered more than the fix:** the live 578-mod capture —
old shape, no `defTypes` index — rebuilds under v3 to
`78057 defs, 536 types, absent=0 shadowed=8 ambiguous=5 orphan=19`, **identical to
v2**. Captures without an index behave exactly as they did.

## criteria
A capture from a producer that resolves collisions keeps every slice; `build`'s
total always equals `SELECT COUNT(*) FROM defs`; a simple name shared by more than
one type refuses and names them rather than summing; and a capture with no
`defTypes` index is unaffected.

## notes
Closed by BUILD 2026-08-21 at `measuring-large-artifacts` `80551ae`,
`SCHEMA_VERSION` 2 → 3. Landed while the game loaded, so the capture is usable the
moment it arrives.

⚠️ A schema bump now **SKIPS** the live-db selftests instead of erroring. The db is
derived and `measure build` is the documented remedy, so an unrebuilt db is a check
that COULD NOT RUN, not one that failed — nine tests went red on a working tree the
instant the version moved, and a red suite nobody can green is one people stop
reading.

⚠️ **`measure count AbilityDef` now refuses, and that is correct.** Three types share
that name. Ask by full name: `measure count Verse.AbilityDef`.
