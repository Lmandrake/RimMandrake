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

---

# 🔴 L5 — the scrapfields shortfall is NOT a count problem. `Generate` ABORTS, and it is designed to be silent.

**OPS, 2026-08-14, from `ilprobe` against
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed\Assembly-CSharp.dll`.**
Measured by BRIDGE: **4** `ChunkSlagSteel`, full-map `listerThings`, 26,213 things
examined, truncated 0 — all four inside a 5-cell box at (214,233) (215,232) (215,237) (217,233).

## 1. The count is CORRECT. That hypothesis is dead.

`GenStep_Scatterer::CalculateFinalCount` (IL 63 B): `count < 0` ⇒
`RoundToInt(CountFromPer10kCells(countPer10kCellsRange.RandomInRange, map, -1) * GetPlacementFactor(map))`.

- `GenStep_Scatterer::GetPlacementFactor` IL_0000 is `ldc.r4 1.0`, and the mutator
  product is reached **only** through `brfalse` on `isJunk` (IL_0006-000c). **`isJunk`
  is gone from the deployed def ⇒ the factor is exactly 1.0.** Not "probably 1".
- `CountFromPer10kCells` IL: `mapSize = map.Size.x` (250) when the arg is < 0, then
  `RoundToInt(mapSize*mapSize / (float)RoundToInt(10000/value))`
  = `RoundToInt(62500 / 1250)` = **50** at value 8.

⇒ **The step asked for ~50 scatter spots and got one.** Nothing is scaling the count.

## 2. 🔴 `Generate` RETURNS on the first failed cell search — it does not skip and continue

`GenStep_Scatterer::Generate` (IL 121 B), the loop body:

```
IL_0028: callvirt GenStep_Scatterer::TryFindScatterCell
IL_0031: brtrue.s IL_004f              ; found -> place
IL_0034: call     get_HasFallbackValidators
IL_0039: brfalse.s IL_004e             ; no fallback ->
IL_0046: callvirt TryFindScatterCell   ; retry with useFallback
IL_004b: brtrue.s IL_004f
IL_004d: ret                           ; <-- ABORTS THE WHOLE GENSTEP
IL_004e: ret                           ; <-- ABORTS THE WHOLE GENSTEP
IL_004f: ... ScatterAt ... usedSpots.Add ... i++
```

**Both failure exits are `ret`, inside the loop.** One unfindable cell ends the entire
step, discarding the remaining ~49 spots. ⭐ **This is the mechanism, and it means the
shortfall is all-or-nothing at some iteration, not a gradual thinning.**

## 3. 🔴 The silence is BY DESIGN — retire "zero scatterer warnings" as a control

`TryFindScatterCell` IL_0083: `ldfld GenStep_Scatterer::warnOnFail; brfalse IL_011e` —
the entire logging block is skipped when `warnOnFail` is false. It is a `public bool`
that **our def never sets**. ⇒ **an aborted scatter logs NOTHING.** The observation
"zero scatterer warnings on this map" is consistent with a healthy run *and* with a
step that quit after one spot. **It discriminates nothing and must not be cited again.**

## 4. ❌ RETRACTED — the 44–56 band is CORRECT. I had `clusterSize` backwards.

**This section originally claimed `CalculateFinalCount` returns SPOTS and that
`clusterSize 10` multiplies it into hundreds of chunks. That is WRONG, and the def's
own comment (`JawaScrapfields.xml:86-90`) was right all along.**

`GenStep_ScatterThings::TryFindScatterCell` IL_0014-0072: when `clusterSize > 1`, a
`leftInCluster <= 0` finds a **cluster centre** through the base method and sets
`leftInCluster = clusterSize`; otherwise it **decrements `leftInCluster`** and returns
a cell near the existing centre. ⇒ **every cluster member consumes one iteration of
`Generate`'s loop.** `CalculateFinalCount` counts **things**, not spots. ~50 chunks in
~5 clumps of 10 — which is exactly the readability effect VISION asked for.

⭐ **What went wrong in my reasoning, because it is the reusable part:** I read
`Generate` and `CalculateFinalCount`, saw a per-iteration `ScatterAt`, and inferred
clustering must happen *inside* `ScatterAt`. **I never read the override that actually
implements it** — and the override is on the *cell finder*, not the placer. Then I
contradicted a def comment that cited the correct fields (`clusterCenter`,
`leftInCluster`, `ClusterRadius`) without reading the method those fields live in.
**Reading three methods of a five-method chain is not reading the chain.**

## 5. Two MORE diagnostics exist and both are ungated — and both read ZERO

- `GenStep_ScatterThings::TryFindScatterCell` IL_003d: `Log::Error("Could not find
  cluster center to scatter …")` — **not gated on `warnOnFail`.** **0 hits in the log.**
- `GenStep_ScatterThings::ScatterAt` IL_000c: `Log::Warning("Could not find any valid
  rotation for …")` — **also ungated.** **0 hits.**

⇒ **The step did not fail loudly, so the §2 abort path is no longer the leading
hypothesis** — in the cluster branch `TryFindScatterCell` returns true almost always
and `Generate` rarely reaches its `ret`. §2 and §3 remain true as engine facts; they
are simply not the explanation here.

## 6. 🔴 The 4 chunks may not be OURS at all — check before diagnosing our def

`ChunkSlagSteel` is scattered by vanilla and by other mods. **4 chunks in a tight
cluster is equally consistent with somebody else's debris pile and a
`Jawa_ScatterScrapfields` that placed ZERO.** ⚠️ **Nobody has established that these
four came from our genStep**, and every diagnosis above assumes they did. Establishing
provenance is a prerequisite, not a refinement.

## What to do — the hunt is now narrow, and it does NOT need a map

**Question: why does `CanScatterAt` reject the map after one placement?** The
validator chain is `GenStep_Scatterer::CanScatterAt` → `GenSpawn::CanSpawnAt` →
`GenStep_ScatterThings::TryGetRandomValidRotation` → the
`terrainValidationRadius` / `terrainValidationDisallowed` loop
(`GenStep_ScatterThings::CanScatterAt`, IL_0035 onward). **All four are readable
offline with `ilprobe`, and the def's own fields say which are even active.**

⭐ **Cheapest decisive experiment, and it costs no load:** set `<warnOnFail>true</warnOnFail>`
on `Jawa_ScatterScrapfields`. The engine then names its own failure on the next map
generated, instead of us inferring it. **A one-field def edit converts a silent abort
into a log line.**
