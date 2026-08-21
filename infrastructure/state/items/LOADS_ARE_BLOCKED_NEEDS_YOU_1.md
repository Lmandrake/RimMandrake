## spec
_not recorded in the source queue_

## verify
_not recorded in the source queue_

## criteria
_not recorded in the source queue_

## notes
**CHECK, 2026-08-20, end of the unattended run. This is the one thing that needs you.**

🔴 **Every save aborts mid-load.** `rt_probe` and `WORLDMAP_gen_sub7b`, every attempt, same

**exception:** ```
System.InvalidOperationException: Collection was modified; enumeration operation may not execute.
  at FactionControl.CrossRefHandler_ResolveAllCrossReferences.Postfix()
  at Verse.CrossRefHandler.ResolveAllCrossReferences()
  at Verse.ScribeLoader.FinalizeLoading()
```
The game then puts up **"An error occurred while loading a map"** and bails to the main
menu — while the bridge keeps answering and the world object stays readable in memory.
That is why hours of work today looked fine and was not.

**What this does NOT block:** the tools. All of them are now proven against that in-memory
world, including the one that had never worked:

| stage | result |
|---|---|
| 1 tiles | 21,872 / 21,872, 0 skipped, 0 unknown biomes |
| 2 links | ✅ **238 rivers + 837 roads, 0 unknown defs** — first time ever |
| 3 mutators | 817 stale `Coast` cleared to 0 |
| 5 settlements | refused: 4 of 72 factions missing from the roster |
| 6 regions | 23 created, 10,765 tiles assigned |

🔑 **Stage 5's refusal is the abort's visible consequence, and the tool behaved correctly** —
FactionControl never finished building the roster, so 4 factions are absent, and the
importer refused all 72 rather than silently placing 68.

**What I need from you, one of:**
1. **Generate a fresh world on the current 578 stack** and save it. A world created now
   cannot carry the stale references these saves do. Then `w9_run.py --apply` finishes in
   about a minute. ⇐ my recommendation
2. **Or drop `thereallemon.factioncontrol`** and see if the saves load. Nothing of ours
   references it in prose, but it is the mod that controls faction counts at worldgen, so
   this is your call, not mine.

⚠️ I did **not** force a load past the mod guard (`ignoreModCompatibility`), because a
forced load generates its own missing-def errors and would destroy the attribution.

---
