# Proving xenotype work

Most xenotype failures are silent: no red error, no log line, just a species that
never appears, a faction that stopped generating, or a name maker that produces
nothing. **Pick the check that can see the failure you care about** — several
cheap checks cannot see any of them.

## What each source of evidence is actually about

| source | answers | does NOT answer |
|---|---|---|
| **the offline def dump** (`src/RimMandrake/Utils/refresh.py`) | what the installed mods **ship on disk** | what exists in the running process |
| **`ModsConfig.xml`** | which mods are active | whether their defs survived load |
| **a runtime lookup by defName** | 🔴 what exists **right now** | why it is absent |
| **spawning a pawn** | appearance, generation, the whole stack at once | nothing about defs you did not spawn |
| **`Player.log`** | load-time errors and deletion messages | anything that failed silently |

🔴 **The dump is pre-deletion; the process is post-deletion.** A dedup mod
removes defs at load (SKILL.md §6), so both readings are correct about their own
moment and they disagree. **When the question is "does this exist", only the
runtime answers it.**

The discriminating call that settled it here was a runtime xenotype lookup:
`set_pawn_xenotype` returned

```
No XenotypeDef named 'X'
```

for the two removed names while converting a pawn with the third in the same
call. **One call, three names, unambiguous.** Prefer a test shaped like that —
same call, a known-good control alongside the suspect — over two separate checks
run minutes apart.

## The checks, cheapest first

1. **Spawn one and look.** `jawa/spawn_pawn` takes a `xenotype` argument
   directly. This is the single most conclusive check available and it costs
   seconds. It settled the "these species have no art" question after two
   file-based analyses reached the wrong conclusion.
   ⚠️ **Bridge rights belong to CHECK.** Ask in one line before driving, and say
   when you are done.
2. **Runtime lookup by defName**, with a control name you know is present.
3. **Generate repeatedly** when the question is *does this xenotype appear* —
   never read `factionlessGenerationWeight` or `canGenerateAsCombatant` at
   runtime to answer it, because unset reads identically to suppressed
   (SKILL.md §5).
4. **Read the SOURCE XML** when the question is *did the author intend this* —
   "does the def declare the field at all" is the only way to tell an unset
   default from a deliberate 0.
5. **A load with the donors disabled**, for a standalone set. Below.

## Silent failures and the check that catches each

| failure | symptom | catch it with |
|---|---|---|
| `<li>` inside `xenotypeChances` | 🔴 the **entire FactionDef** is discarded | the faction generates no pawns at all; grep every `xenotypeChances` for `<li>` |
| `xenotypeSet` inherited | vanilla Hussars in your faction | inspect generated pawns; add `Inherit="False"` |
| RulePackDef copied without its `.txt` files | pawns have empty/fallback names | generate names; count `Rule_File` targets against files on disk |
| `ParentName` unresolved after a rename | the def is simply absent | runtime lookup by defName |
| defName collision across def types | one of the two silently lost | index on `(defType, defName)` |
| a `geneClass` whose assembly is absent | the gene's effect is missing | `Player.log` at load, then spawn |
| dedup mod deleted the def | present on disk, absent at runtime | runtime lookup; the dedupper's own log line |
| `canGenerateAsCombatant false` invented during a `.xtp` promotion | faction generates no fighters | diff the promoted def against the `.xtp`, which carries only `name` and `inheritable` |

⚠️ **`validate_patch.py` cannot see any of the shape errors above.** Its own
banner says it does not check field names, types or shapes. It validates xpath
targets, not schemas. Do not read a clean run as evidence a def is well-formed.

## The standalone test

🔴 **A standalone mod loaded *alongside* its donors proves nothing.** Every
reference you forgot to copy resolves against the donor, so the mod looks
complete and ships broken.

**The only proof is a load with the donor mods switched off**, and it costs a
cold load (~25 min), so spend it deliberately:

- Disable every donor in one change, not one at a time.
- Decide before launching which log strings settle each open question, and
  harvest the whole log afterwards — see `rimworld-load-round`.
- Expect the failures to be *absences*: a species that will not spawn, a name
  that comes out blank, a head that renders as human. Write the spawn list first
  so the absence is visible.

## Attribution

A spawn test in a throwaway quicktest map proves the def stack, not the campaign.
Anything about a live colony's pawns has to be measured on that colony. See
`rimworld-debug-testing` for what a quicktest can and cannot establish.
