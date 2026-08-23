## spec
✅ **DECIDE has authored the replacement names.** Owner, 2026-08-22: *"we'll scan their names
and find better Star Wars-style animal reskins for them instead of latin dinosaur names
(particularly terrible)."*

- **The names and the reasoning:** `design/Jawa/worldbuilding/creature_names_ashkarr.md`
- **The patch:** `design/Jawa/fauna/CreatureNames_Ashkarr.xml` — **41 renames**, validator
  clean. ⚠️ A PROPOSAL under `design/`; BUILD owns whether it ships.
- Regenerate with `design/Jawa/fauna/gen_name_patch.py`, which READS the doc so the two
  cannot drift.

## what was renamed and what was deliberately left
| mod | in cast | renamed |
|---|---|---|
| Jurassic Rimworld | 22 | ✅ all |
| Megafauna | 19 | ✅ all |
| Mythic Ages: Megafauna | 18 | ⛔ no |
| Insectoids 2 / Alpha Animals / Biomes! | 9 | ⛔ no |

⛔ **Mythic Ages stays, on the bestiary's own rule.** `Alien_Bestiary.md` §1: English
compounds *"read as spacer slang, which is a different register and useful for contrast."*
`dunbear`, `duskhorn`, `manehound`, `hellboar` are that register — not Latin, not broken.
**Renaming them would flatten a contrast the bestiary is deliberately building.**

## 🔴 LABEL ONLY
No `defName` is touched. defNames are referenced by quests, incidents and other mods'
patches; renaming one breaks them **silently**.

## what BUILD must still do
1. **Wrap the 41 `PatchOperationReplace`s** in `PatchOperationConditional`/`FindMod` — same
   unwrapped-replace warning as `BIOME_CAST_APPLY_1`.
2. **Re-validate with `--defs`.** Static checks only were run; an xpath matching nothing
   passes silently otherwise.
3. Confirm `MayRequire` for `mlie.jurassicrimworlddinosaursonly` and Megafauna.

## still open, and it is the bigger half
⚠️ **The DESCRIPTIONS still read as Earth palaeontology.** A creature called `ssvarrak` whose
description opens *"a large ornithopod of the Cretaceous"* is worse than one called
Ouranosaurus, because now the two disagree. **The label pass makes the description pass
urgent rather than optional.** 41 descriptions, and they are longer than labels.

## ✅ ALL THREE BUILD TASKS DONE, AND IT SHIPS — 2026-08-22

⚠️ **It is 37 renames, not 41.** The generator says so and names the four it could not
place, which is exactly why regenerating beats hand-editing.

### 1. Wrapped — in the GENERATOR
`gen_name_patch.py` now emits a `PatchOperationConditional` on the creature's own `label`
node with the `Replace` inside its `<match>`. A Replace that matches nothing is a **red
error every launch**, not a silent no-op, so 41 bare ones was 41 errors waiting for a donor
mod to be switched off.

⛔ **No `MayRequire` is emitted and none is wanted.** Task 3 asked me to confirm one for
`mlie.jurassicrimworlddinosaursonly` and Megafauna; the conditional makes it redundant and
is strictly stronger. `MayRequire` passes when the MOD is present — this passes only when
the DEF is. A mod that ships but renames or drops a creature satisfies the first and not
the second, and the first is the one that would have errored.
🔑 No `<nomatch>`: a creature that is not there needs no name.

### 2. Re-validated with `--defs`
**0 errors, 0 warnings** against the real 578-mod load set, and **zero** operations match 0
nodes — every one of the 37 finds its creature.

### 3. The four that did not make it, measured
| name in the doc | why |
|---|---|
| `Protovermes` | 🔴 **not in the def dump at all** — the mod that ships it is not installed |
| `Compsognathus` | 🔴 **not in the def dump at all** |
| `dinornis` | exists (`Dinornis`, Megafauna) but is **not in `cast_assignment.csv`** |
| `sivatherium` | exists (`Sivatherium`, Megafauna) but is **not in the cast** |

⚠️ **The last two are worth DECIDE's eye and are NOT a BUILD fix.** The generator maps a
doc row to a defName through the CAST, so a creature that was named but never cast produces
no rename. Both are real installed creatures with Latin binomials — exactly what this item
exists to remove — so either they belong in the cast or the doc is naming creatures the
cast deliberately excluded. ⛔ I did not widen the generator to reach past the cast: that
would rename creatures nobody decided to place, which is scope BUILD does not own.
ⓘ `Sivatherium`'s label carries a **trailing space** (`"sivatherium "`) in the dump — worth
knowing if anyone later matches it by label.

### Shipped
`src/Jawa/Jawa_Patches/Patches/CreatureNames_Ashkarr.xml`, deployed and verified in sync,
alongside `BiomeCast_Ashkarr.xml`. 🔴 **LABEL ONLY — no `defName` is touched**, which is
what keeps quests, incidents and other mods' patches working.
⛔ Backing it out is one command:
`rm "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods/Jawa_Patches/Patches/CreatureNames_Ashkarr.xml"`
