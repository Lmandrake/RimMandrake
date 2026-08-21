<!-- status: superseded -->
# ~~🔴 The fixed dumper's capture will STILL read as shadowed~~ FIXED, same afternoon

> ✅ **RESOLVED before the capture landed.** `measuring-large-artifacts` `80551ae`
> keys `capture` on the resolved identity — the full name when the manifest's
> `defTypes` index names one — so both slices survive. Re-measured on the same
> synthetic: **633 defs built, 633 held, all three types `complete`**, and
> `measure count RimWorld.AbilityDef` → **MEASURED 612**. `count AbilityDef` now
> refuses and names both types rather than summing them. Five new selftests lock
> it in; 47/47. The live 578-mod capture rebuilds to the identical
> `78057 defs / 536 types / shadowed=8 ambiguous=5 orphan=19` it gave under v2,
> so old captures are unaffected.
>
> ⚠️ **One detail below was wrong and is corrected here:** the first synthetic
> keyed `defCounts` on the simple name. The fixed producer keys it on the **file
> stem** (`DefDumper.cs:183-186`). Re-measured faithfully, the outcome was the
> same — and slightly worse, adding a phantom `absent` row for the stem. The
> conclusion never changed.
>
> 🔑 **What to do after the load is now the original plan again:**
> `measure build`, then `measure count RimWorld.AbilityDef` must read **612**.
> ⚠️ **`RimWorld.`, not `Verse.`** — the synthetic guessed the namespace and
> the guess was wrong. Confirmed against the real capture 2026-08-21 15:44.

# 🔴 The fixed dumper's capture will STILL read as shadowed — measured before the load

**BUILD, 2026-08-21, game down, offline.** Found while checking that our readers
survive the new manifest shape the fixed `RimDefDump.dll` (`d7cf154`) writes.

## The expectation that is wrong

The BUILD handoff and `EXPECTED_FAILURES §3 S2` both predict that after the armed
capture:

```
measure count AbilityDef        ->  MEASURED 612
```

**It will not.** It will still answer `UNMEASURED — coverage=shadowed`, and the
824 defs the fix recovers **will be dropped from `defs.sqlite` anyway**.

## What was measured

A synthetic dump in exactly the shape `DefDumper.cs` now writes — verified against
the source, not assumed:

- per-file header: `defType` = `defType.Name` (**simple**), `defTypeFullName` =
  FullName — `DefDumper.cs:510-511`
- per-record: `defType` = simple, `defTypeFull` = FullName — `DefReflector.cs:112-113`
- colliding types get distinct FILENAMES (`VFECore_Abilities_AbilityDef.json`) and
  `manifest.json` gains `defTypes[]` + `defTypeCollisions[]` — `DefDumper.cs:197-219, 479`

Two files, both declaring `defType: "AbilityDef"`, 612 defs and 18 defs:

```
measure build     MEASURED 615 defs built (2 types; shadowed=1)
capture table     ('AbilityDef', None, 'AbilityDef.json, VFECore_Abilities_AbilityDef.json',
                   declared=612, loaded=0, 'shadowed')
SELECT COUNT(*) FROM defs   ->  3
defs by type      {'ThingDef': 3}          <- ZERO AbilityDefs survived
```

## Two defects, and the second is worse than the first

**1. The producer's fix is invisible to the consumer.** `measure` keys coverage on
the record's SIMPLE `defType`, read out of the file header. It never consults
`defTypeFullName`, the filename, or the new `defTypes[]` index — so two files that
the producer went to trouble to disambiguate still collide on arrival. The cause is
structural, not a missing branch: `capture.def_type` is a **`TEXT PRIMARY KEY`**
(`dumpdb.py:66`), so the schema cannot hold two types sharing a simple name.

**2. 🔴 `build` reports a total it does not hold.** `stats.defs_inserted += n` runs
before the coverage decision (`dumpdb.py:489`), and the shadowed type's rows are
removed afterwards. So it announced **615** while the table held **3**.

⚠️ **This cannot fire on the CURRENT capture and that is why nobody has seen it.**
Today `AbilityDef` declares **0** — the empty type won the filename — so a shadowed
type contributes 0 to both numbers and they agree. The moment the fixed producer
makes the 612-def type the winner, the discrepancy becomes exactly the 824 defs
this whole exercise is about. **The bug is armed by the fix.**

🔑 It is the instrument's own named failure mode — *"an instrument that returns a
confident wrong answer"* — inside the instrument written to prevent it.

## What the load DOES still buy

✅ The 824 defs stop being **lost on disk**: they are written to distinct files and
the manifest records which type owns which. That is real and it is the
irreversible half — it needs the game, and this repo-side bug does not.
⛔ But **do not run `measure build` after the load and read its number as truth**
until this is fixed. And do not re-freeze on the strength of `count AbilityDef`.

## Where the fix goes
`measuring-large-artifacts` is its own repo, `D:\Luke\dev\measuring-large-artifacts`
(symlinked at `~/.claude/skills/`). Filed as `DUMPDB_KEYS_ON_SIMPLE_NAME_1`.
