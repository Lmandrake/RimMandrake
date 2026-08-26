# DUMPER_SWALLOWS_CACHE_THROW_1 — the dump reports the engine's answer and hides that the engine threw

`src/RimMandrake/RimDefDump/Source/DefDumper.cs:526`:

```csharp
try { w.Prop("commonality", b.CommonalityOfAnimal(pk)); } catch { }
```

Two things are wrong with that line, and together they cost a whole investigation on 2026-08-26.

1. **It serialises the ENGINE'S cached answer, not the record's field.** A reader assumes
   `wildAnimals[].commonality` is what the def says; it is what `CommonalityOfAnimal` *returns*,
   which is a different thing whenever the cache is not intact.
2. **The bare `catch { }` hides the throw.** `CommonalityOfAnimal` assigns
   `cachedAnimalCommonalities` before filling it, so a duplicate-key `ArgumentException` leaves
   the dictionary partial and non-null — and every later call returns a perfectly plausible
   **0f**. The dump then reports 181 zeros with no indication that anything failed.

⇒ The capture said *"a quarter of the planet's animals have commonality 0"*, which reads as a
content defect. It was a crash symptom. The mechanism was only found by reading `BiomeDef.cs`.

## What to change
- Report **both**: the record's own `commonality` field AND the engine's `CommonalityOfAnimal`,
  under distinct keys. When they disagree, that disagreement is the finding.
- ⛔ **Never a bare `catch { }` around a value the dump publishes.** Catch it, and write the
  exception type into the row: a field that could not be read must not look like a field that
  read zero. Same rule the bridge tools follow.

## verify
A capture taken while a biome's cache is broken shows the record's real weights AND a per-row
marker naming the exception — not a silent 0.

## criteria
- [ ] Both values published, under names that cannot be confused.
- [ ] No bare `catch { }` left on a published value in `DefDumper.cs`.
- [ ] ⚠️ Needs a game-down window: `RimDefDump` is an assembly, and the OS locks a loaded DLL.
