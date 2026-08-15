# ilprobe — read what RimWorld's code actually does, offline

A minimal .NET metadata reader and IL disassembler for `Assembly-CSharp.dll`.
No decompiler, no Visual Studio, no game load, stdlib Python 3 only.

## Why this exists

`CLAUDE.md` says **never guess a defName, a field, or a namespace.** That is easy
to obey for XML, which you can grep, and quietly impossible for engine
behaviour — so engine questions used to be answered from memory, from a wiki, or
by spending a 23–30 minute game load to watch what happened.

This closes that gap. Two questions that would each have cost a load, both
answered offline in minutes:

* **Does `CompExplosive` need `tickerType Normal` to explode with no wick?**
  Functionally no — `CompTick` is a no-op when no wick is running. But
  `ConfigErrors` demands `Normal` regardless, so a `Rare` def logs a red error
  per def. Two different answers to what looked like one question, and only the
  IL separates them.
* **Does a droid that explodes on death leave anything to salvage?** Yes — the
  corpse and leavings are spawned *before* the detonation and survive iff the
  blast's DamageDef has `harmsHealth: false`. Vanilla's only exploding mech uses
  a stun damage type precisely so that they do.

Neither is in any documentation. Both were load-bearing for design decisions.

## Use

```bash
cd src/RimMandrake/Utils/ilprobe
python3 il.py CompExplosive PostDestroy Detonate CompTick   # disassemble methods
python3 meta.py CompProperties_Explosive                    # fields, types, defaults
python3 enumdump.py DestroyMode                             # enum constants
```

`il.py` resolves field, method and type tokens, so a branch reads as
`ldfld CompProperties_Explosive::explodeOnKilled` rather than a raw token.

Target assembly, hardcoded:
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed\Assembly-CSharp.dll`

## What it is good and bad at

**Good at:** does this field exist; what exactly does this method branch on; the
real numeric value of an enum member; whether a virtual is actually overridden.

**Bad at:** dataflow across methods, generics-heavy code, and async/iterator
methods — those compile to a `MoveNext` on a generated class and you have to
find the state machine yourself (`<ConfigErrors>d__41` and friends).

**A DLL has no line numbers.** Cite findings as type + method + IL offset, and
quote the IL beside any conclusion you put in a design doc — the point is that
the next reader neither re-derives it nor takes your word for it.

⚠️ **Enum values are not the declaration order you would guess.** `DestroyMode`
is `Vanish=0, WillReplace=1, KillFinalize=2, KillFinalizeLeavingsOnly=3,
Deconstruct=4…`. Comparing against the wrong integer is the kind of mistake that
survives review, so dump the enum instead of assuming.

## Provenance

Written 2026-08-12 by a research subagent for the "everything detonates" design
question, and kept because it turned an unanswerable class of question into a
cheap one. Findings are recorded in `design/V2_DREAMS.md` §1.
