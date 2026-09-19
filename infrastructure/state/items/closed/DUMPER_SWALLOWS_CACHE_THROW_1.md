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
- [x] Both values published, under names that cannot be confused.
- [x] No bare `catch { }` left on a published value in `DefDumper.cs`.
- [x] ⚠️ Needs a game-down window: `RimDefDump` is an assembly, and the OS locks a loaded DLL.

## Closed 2026-08-30 — FOUNDRY, found already fixed and unclosed

The fix landed in commit `85e3ced2` (author/date not this session) — this item's
own checkboxes were just never ticked. Source at
`src/RimMandrake/RimDefDump/Source/DefDumper.cs:558-572` already does exactly
what "What to change" asked: `commonalityDeclared` and `commonalityEngine`
published under distinct keys, with a proper `try/catch` writing
`commonalityEngineError` (exception type + message) when the engine call
throws — no bare `catch { }` remains.

**Verified against a live capture, no DOWN window needed** — a fresh 585-mod
def dump already existed
(`DefDump/captures/2026-08-30T08-49-45Z/animals.json`, postdates the fix
commit) and reading it directly settles the whole item:
- 5,725 `biomeAnimals` rows, every one carrying both `commonalityDeclared`
  and `commonalityEngine` under their own names — schema confirmed live.
- 0 rows with `commonalityEngineError` this capture (no cache-broken biome
  hit this pass — the mechanism wasn't exercised by a real throw, but its
  presence in the schema and in source is what the criteria actually ask for).
- 1,768 rows where `commonalityDeclared != commonalityEngine` — a real,
  legitimate disagreement (spot-checked: consistently `engine ==
  declared / 2`, some RimWorld-side normalization, not a defect) — this is
  the "when they disagree, that disagreement is the finding" the item wanted
  surfaced, now visible instead of hidden behind one merged field.
- **The old bug's exact signature — `commonalityEngine == 0` while
  `commonalityDeclared` is nonzero — appears in 0 of 5,725 rows.** All 597
  zero-engine rows also read `commonalityDeclared: 0`, i.e. genuinely zero,
  not a swallowed-exception zero wearing a legitimate value's clothes.
