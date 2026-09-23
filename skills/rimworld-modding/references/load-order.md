# load-order.md — asserting load order, and what a broken one looks like

Moved out of `SKILL.md` §5b on 2026-08-14 to keep the skill body under its
500-line budget. The rules that change your default behaviour stayed in the
skill; what is here is the evidence behind them, the assertion recipe, and the
mod-manager database detail. Open it when an inheritance error appears, when you
are writing the order assertion, or when you are about to touch a sorter's rules
database.

## The damage escapes your mod

A `PawnKindDef` that failed to inherit has no `race`, so `RaceProperties` is null
on it — and vanilla code enumerates *all* pawnkinds. That produced NREs inside
`ThingDef.ResolveIcon`, `ScenPart_StartingAnimal.PossibleAnimals` and
`BiomeDef.CommonalityOfAnimal`, breaking map generation. **None of those stack
traces named a mod.** If worldgen starts throwing, grep the log for
`Could not find parent node` and `Config error in <YourDefPrefix>` before
believing it is a vanilla bug.

## Assert the order in code before every launch

Not by eye, not by trusting the manager. Resolve the load set, find the index of
your mod and of each mod it patches, and fail loudly:

```python
low = [m['packageId'].lower() for m in mods]
for mine, target, why in CHECKS:
    assert low.index(mine) > low.index(target), f"{mine} must load after {target}: {why}"
```

Keep one entry per mod you actually reach into. A three-check version passed
while the order was still broken for a fourth mod.

## Teach the mod manager, or it will keep undoing you

RimSort (and similar) re-sort on demand and will silently scatter your mods.
Fixing the resulting order by hand works but treats the symptom. The manager has
a **user rules** database — for RimSort,
`%LOCALAPPDATA%/RimSort/dbs/userRules.json` — and the distinction that matters
is:

- **`loadAfter`** is a *constraint* — it compiles to a real edge in the dependency
  graph, and a topological sort cannot violate it. **This is the one you want.**
- **`loadBottom`** is neither a hint nor a stronger constraint. It compiles to
  membership in a **tier**, and RimSort sorts four tiers independently then
  concatenates them. ⚠️ **The tier split silently DELETES any `loadAfter` /
  `loadBefore` edge that crosses a tier boundary** (`app/sort/dependencies.py`
  intersects each tier's subgraph with `& tier_mods`). Nothing is logged.
  🔑 Read out of RimSort's own source, 2026-08-19 — see
  `skills/rimworld-start-prep/SKILL.md`, which owns this and carries the code.

Write one `loadAfter` edge per mod you patch. After that the manager produces the
right order unaided and your assertion becomes a cheap safety net rather than a
repeated repair.

(The two ⚠️/🔴 traps in the rules file itself — the `packageId` orphaning, the
stale in-memory view, and reading `ModsConfig.xml`'s mtime before writing it —
stayed in `SKILL.md` §5b, because they are rules you need before you act.)

## The community rules database is not yours to edit

Do not hand-edit the *community* rules database: it is a git clone refreshed on
startup, so local changes vanish. Community rules are a pull request to a public
third-party repo, which is the user's call, never yours.

---

## Full paragraphs behind `SKILL.md` §5b's compressed rules

Each heading below matches one compressed rule in `SKILL.md` §5b. The first line repeats the kept lead; the rest is what moved.

### `ParentName` resolves only against `Abstract="True"` defs

**`ParentName` resolves only against `Abstract="True"` defs declared with a
`Name=` attribute — never against a `defName`.** Core's EMP damage def uses
`ParentName="StunBase"` (`<DamageDef Name="StunBase" Abstract="True">`), not
`ParentName="EMP"`; naming a concrete def gives `XML error: Could not find parent
node named "EMP"` and the def is **discarded** whole. So resolve every
outward-pointing name against the live load set before shipping a `Defs/` file:
`ParentName` against `Name=` attributes, and `Class=`/`workerClass`/`thingClass`/
`graphicClass` against loaded assemblies. `validate_patch.py` does both since
2026-08-13; it still checks no field names, types or value ranges.

### `ParentName` inheritance is load-order dependent

**`ParentName` inheritance is load-order dependent.** A def whose `ParentName`
names an abstract def in a mod that loads *later* does not inherit — at all.
Everything the parent supplied is simply missing, and you get
`XML error: Could not find parent node named "X"` plus a cascade of config
errors about fields you never wrote. Do not assume the engine resolves
inheritance across the whole combined document; it does not.

### The damage escapes your mod (full paragraph)

**The damage escapes your mod**, and none of the stack traces name it. A failed
inheritance breaks *vanilla* code that enumerates all defs of that type — worldgen
included. If worldgen starts throwing, grep the log for `Could not find parent
node` and `Config error in <YourDefPrefix>` before believing it is a vanilla bug.

### `ParentName` resolution keys on `Name=` in a flat namespace

🔴 **`ParentName` resolution keys on the `Name=` attribute in a FLAT NAMESPACE NOT
SCOPED BY DEF TYPE.** Giving a `ThingDef` and its paired `PawnKindDef` the SAME
`Name=` (never `defName`, which is fine) is a live landmine even when both live
in the same mod, same file even — it stays dormant until something actually
inherits via `ParentName` against that shared name, and the merge then silently
pulls the wrong type's fields in (a `ThingDef`'s `<thingClass>`/`<statBases>`/etc.
landing inside what should be a `PawnKindDef`), leaving fields like
`PawnKindDef.race` null. This crashed a mod's own `GeneDefGenerator` at load with
no error pointing at the real cause. Fix: give paired defs DISTINCT `Name=`
attributes (suffix the `PawnKindDef`'s with `_Kind`); `defName` can still match.
`validate_patch.py` without `--defs` does not catch this at all.

### A same-mod `Patches/` load-order fix that only guards one known file

🔴 **A same-mod `Patches/` load-order fix that sorts "after the one file I know
adds the duplicate" is not enough if a THIRD file in the same folder also
touches it** — it can sort after your fix's rename and silently re-break it on
the very next restart. The only actually-safe filename sorts after EVERY
current file in that `Patches/` folder: a `ZZZ_` prefix, confirmed against a
fresh post-restart capture rather than "after the file(s) I have in mind."

### `DefDatabase<T>.Add` does not override a repeated `<defName>`

🔴 **`DefDatabase<T>.Add` does not override a repeated `<defName>` — it logs a
red error and RANDOMIZES the new def's name every load** (`Source/Verse/
DefDatabase.cs`). A batch of new defs whose `<defName>` accidentally duplicated
the vanilla/donor def they were meant to replace would have been completely
inert — spamming load errors while never actually taking ownership — because
the "replacement" never got a stable identity. Always grep every new def
batch's ACTUAL `<defName>` against its filename before staging; never trust the
filename to match the content.

### `AllLeafSubclasses()` means "nothing currently loaded subclasses this", not "concrete"

⚠️ **`AllLeafSubclasses()` means "nothing currently loaded subclasses this",
not "concrete."** `RimWorld.AlertsReadout`'s constructor does
`foreach (Type t in typeof(Alert).AllLeafSubclasses())
Activator.CreateInstance(t)` with NO abstract check and NO try/catch. With no
consumer mod loaded, an ABSTRACT base class of your own (meant to be
subclassed by a future/optional consumer) becomes the "leaf" itself,
`Activator.CreateInstance` throws `MissingMethodException` (abstract types have
no ctor), and the uncaught exception crashes `AlertsReadout()` → `UIRoot_Play()`
→ `Find.MapUI` stays null forever → every later `Update()`/`OnGUI()`/tick NREs
on it, on every map, independent of which content mod (if any) is active. Fix:
ship a sealed, always-inactive concrete leaf subclass alongside any such base
class, so it is never the leaf regardless of which consumer mods are loaded.
Same landmine applies to anything else using `AllLeafSubclasses` rather than
`AllSubclassesNonAbstract`.

### A self-referencing `ResearchProjectDef` prerequisite recurses infinitely

⚠️ **A self-referencing `ResearchProjectDef` prerequisite causes unconditional
infinite recursion in vanilla `ResearchManager.FinishProject`** — there is no
cycle/visited-set guard there at all. The result is an uncatchable
`StackOverflowException`: silent, immediate process death, NO managed
exception and NO crash-handler log line, hit right when that project's
dependency chain gets walked. Symptom signature: several research completions
log fine, then abrupt silence, process gone. An XML patch removing the
self-reference is not sufficient on its own if a donor mod's OWN patch
operation re-injects it at a different point in load order — a durable fix is
a Harmony prefix on `ResearchManager.FinishProject` stripping any
self-referencing prerequisite before the loop runs. Verify a "prerequisite
fix" by reading the LIVE resolved def back after a fresh cold restart, not by
trusting the patch file exists.

### `<loadAfter>` is an ordering hint and is invisible to dependency closure

🔴 **`<loadAfter>` is an ordering hint and is INVISIBLE to dependency closure.** If a
mod SUPPLIES a class or texture another mod references, that reference belongs in
`<modDependencies>`, not `<loadAfter>` with a comment explaining the intent — a
reduced-mod-list builder that walks `<modDependencies>` will silently drop a
`<loadAfter>`-only dependency, the referenced comp types fail to resolve, and **a
missing comp type discards the whole def carrying it**, with no error naming
which def vanished. The same applies to art: a mod supplying the only texture at
a given path needs to be a declared dependency too, or a reduced list renders that
def as a magenta X with no log line pointing at the missing mod.

### SKILL.md §5b — assert the order in code before every launch (full)

manager: resolve the load set, compare the index of your mod against each mod it
patches, and fail loudly. One check per mod you reach into.

### SKILL.md §5b — same-mod Patches/ fix, continued line

adds the duplicate" is not enough if a THIRD file in the same folder also
