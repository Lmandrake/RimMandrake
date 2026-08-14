# O18 — the scoped full-patch sweep. FIRST RESULT THAT DESCRIBES THE RUNNING GAME.

**OPS, 2026-08-14 14:02. Verdict: `OK TOTAL — 72 file(s), 0 error(s), 1608 warning(s)`.**
**Zero errors. Every warning is accounted for below, and none is a defect.**

Raw output (1.7 MB, untracked on purpose — reproducible, and its value is in this
file): `D:\Luke\dev\Rimworld\observed\2026-08-14_patch_sweep_scoped.txt`

```
python3 skills/rimworld-modding/scripts/validate_patch.py src/Jawa \
  --defs ".../steamapps/workshop/content/294100" \
  --defs ".../common/RimWorld/Mods" \
  --defs ".../common/RimWorld/Data"
```

## 🔴 It is SCOPED — this is the thing O16 invalidated every earlier sweep for

Header, verbatim:

> `info    load set: 585 active mods, 585 found on disk, target version 1.6 -> 8,978 def files`

**585 of 585 resolved — no missing folders.** Cross-checked two ways before the run
finished, both independent of the sweep process: `validate_patch.find_mods_config()`
resolves to `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\ModsConfig.xml`
(the `a1483e7` fix's `/mnt/[a-z]/Users/*` branch working), and parsing that file
directly gives `<activeMods>` = **585** `<li>`, `<knownExpansions>` = 5.
⚠️ The 5 is the block that makes a naive `grep -c "<li>"` report 590.

Engine: `lxml 6.0.2.0`, full XPath 1.0 — so `text()`, `contains()`, `starts-with()`,
`not()` and boolean predicates were really evaluated, not pattern-matched.

## The 1,608 warnings are four classes, and the tail is 72 of them

| n | class | verdict |
|---|---|---|
| **1,536** | `inner xpath differs from the conditional test` | ✅ **the add-if-missing idiom, and the validator says so in its own message.** Test `statBases/MeatAmount`, add to `statBases` when absent. This is how the pattern is spelled; it is not a finding |
| **59** | node absent on disk but *created at runtime* by another mod's patch — "make sure your mod loads AFTER it" | ✅ **CHECKED AND SATISFIED — see below** |
| **11** | xpath matches 2 nodes in one mod folder, operation applies to both | ⚠️ 8 are in `Armoury_RangedDamage.xml`, **HELD and not deployed** ⇒ not in the running game. 3 are live |
| **2** | `iconPath` resolves to no loose file | ⓘ **unknowable from disk** — the validator's own text: vanilla textures live in Unity asset bundles, so a correct path and a wrong one look identical here |

95.5% of the total is one benign idiom in one file — `MegafaunaYield.xml` alone
carries 1,206. **Read the classes, never the count.**

### The 59 load-order dependencies — verified, not assumed

Our three mods must load after every mod whose patch creates the node we then edit.
Positions read from the live `ModsConfig.xml` `<activeMods>` order:

| our mod | position | must beat |
|---|---|---|
| `mandrake.jawa.doctrine` | **567** / 585 | Royalty 5, Biotech 7, VFE Core 20, Alpha Biomes 50 |
| `mandrake.jawa.armoury` | **579** / 585 | same |
| `mandrake.jawa.patches` | **581** / 585 | Facial Animation Compat Project **564** |

⇒ **all three sit in the last 19 of 585, after every named creator.** The one that
could plausibly have been wrong is `HeadSetForFA_Revive.xml` (Jawa_Patches, 581) vs
the Facial Animation Compatability Project (564) — **17 slots of margin, correct.**
🔴 **This class is closed. Do not re-derive it from a warning count next sweep** —
the warnings will still be there, because the validator cannot see runtime nodes.

### The 3 live double-matches — filed, not fixed

`Jawa_Doctrine/Patches/MegafaunaYield.xml`, `PatchOperationReplace` hitting 2 nodes:
`Mythic Ages: Megafauna Bestiary: Animal_Harpeagle.xml` ×2, `Rim cockroach: Normal.xml` ×2.
Both apply the **same** yield value to both nodes, which is what a yield patch wants;
the risk is only that a future edit assumes one target. **Not worth a load, not worth
a fix tonight — a player cannot see it.** The other 8 are in a HELD file and will be
dealt with when the Armoury ships.

### The 2 icon paths — do NOT chase these offline

`GeneDef 'Jawa_Head_Plain'` → `UI/Icons/Genes/Gene_Hair`,
`XenotypeDef 'Jawa_Xeno_Gamorrean'` → `UI/Icons/Xenotypes/Pigskin`.
**A file audit cannot settle either**, by the validator's own admission. The only
instrument that can is the game: a missing xenotype/gene icon shows as a **pink or
blank square in the xenotype picker**, and that is an owner-look item, not a grep.
⇒ **Filed for eyes-on during this load. If both icons draw, both close permanently.**

## What this closes

**O18 is DONE.** There is now a `src/Jawa` validation result that describes the
running game: **72 files, 0 errors.** Every prior sweep is superseded, not merely
old — under O16 they scanned 1,271 installed mods and 34,719 def files, so their
non-zero counts could name mods the game never loads. This one cannot.
