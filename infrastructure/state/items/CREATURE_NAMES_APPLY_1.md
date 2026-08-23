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
