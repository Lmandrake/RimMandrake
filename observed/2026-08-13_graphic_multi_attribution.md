# `Graphic_Multi` ×14 and ReGrowth `RecolorMineables` — attribution

Written by OPS, 2026-08-13, game **DOWN**. Follow-up to
`/mnt/d/Luke/dev/Rimworld/observed/2026-08-13_log_harvest_1004.md` §c2 and §c3,
which recorded both errors and deliberately left c2 **unattributed**.

Source log: `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Player.log`
(1,145,196 bytes, last written 2026-08-13 10:04:55).
Second source, and the one that settled it: the live def dump that same run wrote to
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\DefDump\defs`
(528 def-type JSON files, log line 3572).
Engine facts are IL from `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed\Assembly-CSharp.dll`,
read with `D:\Luke\dev\Rimworld\src\RimMandrake\Utils\ilprobe\il.py`.

---

## Verdict in one line each

| error | attributed to | one thing or many | player-zero | disposition |
|---|---|---|---|---|
| `Exception getting Verse.Graphic_Multi at :` ×14 | **`[AB] Xenotype: Yautja`** (`biotechrace.yautja.alleyballey`, workshop `3536839586`) — one abstract PawnKindDef with a `bodyGraphicData` that has no `texPath` | **ONE defect, 14 symptoms** (7 loaded PawnKindDefs × 2 `lifeStages`, all inheriting one abstract parent) | **nothing visible** — the graphic it poisons is never consulted by the `Humanlike` render tree | **waiver** into `benign_log_errors.md` (draft below); optional one-line upstream/patch fix |
| ReGrowth Core `RecolorMineables` NRE ×1 | **ReGrowth 2** (`ReGrowth.BOTR.Core`, workshop `2260097569`), *Perspective: Ores* — `thing.Graphic.data` null on one resource rock | one | **cosmetic** — it aborts the whole recolor loop, so ore lumps past the bad rock stay vanilla-coloured; nothing else is written | **waiver** (draft below); re-runs every map load, so not a one-shot |

---

## 1. `Exception getting Verse.Graphic_Multi at :` ×14 — ATTRIBUTED

### 1.1 Why the stack trace can never name the culprit

The harvest asked for the calling type. **There is none, by construction**, and
this is worth writing down because the next person will look for it too.

The printed trace is the *exception's* trace, which unwinds only from the throw
point to the `catch`. The `catch` is inside `Verse.GraphicDatabase.Get`, which is
also the bottom frame printed:

```
  at Verse.ModContentHolder`1[T].Get (System.String path)
  at Verse.ContentFinder`1[T].Get (System.String itemPath, System.Boolean reportFailure)
  at Verse.Graphic_Multi.Init (Verse.GraphicRequest req) [0x0011f]
  at Verse.GraphicDatabase.GetInner[T] (Verse.GraphicRequest req) [0x000a5]
(wrapper delegate-invoke) System.Func`2[Verse.GraphicRequest,Verse.Graphic].invoke_TResult_T
  at Verse.GraphicDatabase.Get (Verse.GraphicRequest req) [0x00066]
```

`GraphicDatabase::Get(GraphicRequest)`, IL tail:

```
  IL_0079: ldstr            "Exception getting "
  ...
  IL_0096: ldstr            " at "
  IL_009e: ldfld            GraphicRequest::path
  IL_00bb: call             Log::Error
  IL_00c0: leave.s          IL_00c2
  IL_00c2: ldsfld           BaseContent::BadGraphic
  IL_00c7: ret
```

Everything above the `try` is gone from the trace. **So "read the stack for the
calling type" is not available on this error class, ever.** Adjacency in the log
is likewise not evidence — §4b.1's lesson stands and BetterTrees is *not* the
cause (see §1.5).

### 1.2 What the engine actually requires — three IL facts

**(a) `Graphic_Multi.Init` dereferences the raw path at exactly the offset the log
names.** `Verse.Graphic_Multi::Init`, IL_011f — the fallback taken when none of
`path_north/_east/_south/_west` resolved:

```
  IL_011f: ldloc.0
  IL_0120: ldc.i4.0
  IL_0121: ldarg.1
  IL_0122: ldfld            GraphicRequest::path      <-- raw path, not concatenated
  IL_0127: ldc.i4.0
  IL_0128: call             ContentFinder<Texture2D>::Get
```

The log frame reads `Graphic_Multi.Init (…) [0x0011f]` — **this instruction**.
`path + "_north"` on a null path yields the string `"_north"` (no throw, no
match); the raw `path` on the fallback is still `null`, and
`Dictionary<string,…>.FindEntry(null)` throws `ArgumentNullException: key`. So
the path is **null**, not `""`.

**(b) A def with a missing `texPath` DOES produce a null path.** The harvest
ruled defs out on the belief that a missing `texPath` yields `""`. That is
wrong. `GraphicData::texPath` is a plain `string` field — default `null` — and
`GraphicData::Init` passes it through with **no guard**:

```
  IL_0000: ldfld  GraphicData::graphicClass
  IL_0007: call   Type::op_Equality        <-- the ONLY guard is on graphicClass
  IL_0035: ldfld  GraphicData::texPath     <-- passed straight through
  IL_005a: call   GraphicDatabase::Get
```

🔴 **Correct `2026-08-13_log_harvest_1004.md` §c2 on this point** — "this is mod
C# calling `Get(null)`, not a broken def" is the opposite of the truth.

**(c) `Graphic_Multi` is what a PawnKind lifeStage graphic defaults to.**
`Verse.PawnKindLifeStage::ResolveReferences`, IL_0000–IL_002b:

```
  IL_0001: ldfld   PawnKindLifeStage::bodyGraphicData
  IL_0006: brfalse.s IL_0030                     <-- if the node exists at all…
  IL_000e: ldfld   GraphicData::graphicClass
  IL_0014: call    Type::op_Equality             <-- …and no graphicClass was given…
  IL_0021: ldtoken Graphic_Multi
  IL_002b: stfld   GraphicData::graphicClass     <-- …it becomes Graphic_Multi
```

So: **a `bodyGraphicData` block that omits `texPath` is auto-typed
`Graphic_Multi` and then requested with a null path.** That is the whole bug
shape, and it is a def bug, in XML, with no C# involved.

### 1.3 The def, found in the live dump — exact count match

Scanned all 528 files of the run's own `DefDump\defs` for any `GraphicData` whose
`graphicClass` is `Graphic_Multi` and whose `texPath` is null or empty.

**Hits: 14. All 14 from one mod.**

| defType | defName | modName | field |
|---|---|---|---|
| PawnKindDef | `Colonist_ABYautja` | `[AB] Xenotype: Yautja` | `lifeStages[0]/bodyGraphicData`, `lifeStages[1]/bodyGraphicData` |
| PawnKindDef | `Colonist_ABYautja_Unblooded` | ″ | both lifeStages |
| PawnKindDef | `Colonist_ABYautja_Blooded` | ″ | both lifeStages |
| PawnKindDef | `Colonist_ABYautja_BadBlooded` | ″ | both lifeStages |
| PawnKindDef | `Colonist_ABYautja_Naked` | ″ | both lifeStages |
| PawnKindDef | `Colonist_ABYautja_Pirate` | ″ | both lifeStages |
| PawnKindDef | `Colonist_ABYautja_Blooded_ODYSSEY` | ″ | both lifeStages |

7 PawnKindDefs × 2 lifeStages = **14**, against **14** log errors:

```bash
grep -o "Exception getting [A-Za-z_.]*" "$L" | sort | uniq -c
#   14 Exception getting Verse.Graphic_Multi
```

and **no other graphic class appears in that error at all** in this log.

### 1.4 The clincher — the live def dump shows the damage in place

Count agreement would still be circumstantial. This is not:

```json
"bodyGraphicData": {
  "$type": "GraphicData",
  "graphicClass": "Verse.Graphic_Multi",
  ...
  "cachedGraphic": { "$type": "Graphic_Single", "path": "UI/Misc/BadTexture" }
}
```
(`DefDump\defs\PawnKindDef.json`, `Colonist_ABYautja`, both lifeStages.)

`UI/Misc/BadTexture` is `BaseContent.BadGraphic` — **the exact object
`GraphicDatabase.Get` returns from its catch block** (IL_00c2 above). The dump
was written by the same process, ~2000 log lines after the errors. So these 14
`GraphicData` objects are, in the live game's own memory, holding the failure
value produced by these 14 log lines. **Attribution is not inference; it is the
recorded end state.**

### 1.5 The source line, and why BetterTrees is exonerated

`C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3536839586\1.6\Defs\PawnKindDefs_Humanlike\PawnKinds_BaseAbstract.xml`
line 60:

```xml
<PawnKindDef Abstract="True" Name="BaseYautjaPawnKind">
  <race>Human</race>            <!-- patched to ABAlien_Yautja by the mod's own HAR patch -->
  ...
  <lifeStages>
    <li><bodyGraphicData><drawSize>0.75</drawSize></bodyGraphicData></li>
    <li><bodyGraphicData><drawSize>1</drawSize></bodyGraphicData></li>
  </lifeStages>
```

The author wanted to set **`drawSize` only**. But writing a `<bodyGraphicData>`
node at all creates a `GraphicData` with a null `texPath`, which
`PawnKindLifeStage.ResolveReferences` then types as `Graphic_Multi`. 14 concrete
kinds inherit this parent (`grep -rn BaseYautjaPawnKind`); 7 survive the
`MayRequire` gates in our stack, giving 14 lifeStage nodes.

**BetterTrees:** not involved. It is upstream in the log only because
`StaticConstructorOnStartup` classes log in mod load order and the graphic
resolution happened to be forced in that window. BetterTrees requests graphics
for **tree ThingDefs** (`Graphic_Random`/`Graphic_Single` territory), none of
which appear in the null-texPath scan, and every one of the 14 nulls belongs to a
Yautja PawnKindDef. §4b.1's rule held: adjacency was the wrong answer again.

⚠️ **One thing I did NOT determine:** *which* code forces
`bodyGraphicData.Graphic` during the static-constructor window. It is not
`PawnKindDef.PostLoad` (that lambda only defaults `shaderType` on the swimming
and stationary graphics) and not `PawnKindLifeStage.ResolveReferences`. Some
`[StaticConstructorOnStartup]` consumer walks PawnKind lifeStages at load. A sweep
of all 4,165 mod assemblies for the string `bodyGraphicData` returned **131 hits**
(VEF, Big and Small, Alpha Genes/Memes, GiddyUp, Vehicles, EBSG, RIMMSqol …), so
that thread is not cheaply narrowable and was not worth pulling. **This does not
affect attribution** — whoever asks, the answer is poisoned by the def, and any
consumer asking is behaving legitimately.

### 1.6 Player-zero verdict — invisible, and provably so

The failed graphic is **cached**, not retried: `GraphicData.Init` stores
`BadGraphic` into `cachedGraphic`, so the request never runs again. That is why
there are exactly 14 and not thousands across 1.88 M ticks of play.

Is `BadGraphic` ever drawn? `PawnKindLifeStage.bodyGraphicData` is read by
`Verse.PawnRenderNode_AnimalPart::GraphicFor` (IL_003e:
`ldfld PawnKindLifeStage::bodyGraphicData` → `GraphicData::get_Graphic`) — the
**Animal** render tree. The humanlike node,
`RimWorld.PawnRenderNode_Body::GraphicFor`, never touches it; it resolves from
`Pawn.story.bodyType.bodyNakedGraphicPath` (IL_0109) and returns `null` if that
is unset.

And the Yautja race is humanlike. From the live dump, `ThingDef ABAlien_Yautja`:

```
race.intelligence : "Humanlike"
race.renderTree   : "Humanlike"
```

**So the poisoned graphic is attached to a field the Humanlike render tree never
reads.** No magenta pawn, no invisible pawn, no checkerboard. Player-zero sees
**nothing**. The residual risk is a UI surface that draws a PawnKind body icon
for a humanlike kind — vanilla has none.

### 1.7 Recommendation

**Waiver, not a fix, and not a removal.** Draft entry in §3 below.

If someone wants it silenced anyway it is a genuine one-liner — the mod only
wanted `drawSize`, so deleting the two `<bodyGraphicData>` blocks from
`BaseYautjaPawnKind` removes the error with no art consequence (they resolve to
`BadGraphic` today, i.e. they already contribute nothing). That is an **upstream
bug worth reporting** to AlleyBalley
(`https://github.com/AlleyBalley/-AB-Xenotype-Yautja`) rather than a local patch
we maintain forever. Not v1 either way — it changes nothing a player can see.

---

## 2. ReGrowth Core `RecolorMineables` NRE ×1 — harmless, but it DOES abort the loop

**Mod:** ReGrowth 2 (`ReGrowth.BOTR.Core`, author Helixien, modVersion 5.1-rev6),
workshop `2260097569`.
**Assembly:** `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\2260097569\1.6\Assemblies\ReGrowthCore.dll`
(no source on disk; read as IL).

Full trace, line 6768, once:

```
Exception from long event: System.NullReferenceException: Object reference not set to an instance of an object
[Ref DF9ACD49]
  at ReGrowthCore.Map_FinalizeInit_Patch+<>c__DisplayClass1_0.<ProcessMap>g__RecolorMineables|4 () [0x00062]
  at ReGrowthCore.Map_FinalizeInit_Patch+<>c__DisplayClass1_0.<ProcessMap>b__0 ()
  at Verse.LongEventHandler.UpdateCurrentSynchronousEvent (System.Boolean& sceneChanged)
```

**What it is:** ReGrowth's *Perspective: Ores* feature. `ProcessMap` walks
`map.listerThings.listsByGroup[2]`, keeps `Mineable`s that are not in
`ModSettings_PerspectiveOres.skippedMineableDefs`, whose
`def.building.isResourceRock` is true and whose `def.graphicData.Linked` is true;
flood-fills them into lumps, assigns each lump a colour, and `RecolorMineables`
then rebuilds a graphic per (GraphicData, Color) via `GraphicDatabase.Get` +
`GraphicUtility.WrapLinked` and writes it to **`Thing::graphicInt`**. That single
field is the only thing it writes.

**Where the null is:** local 7 is `thing.Graphic.data`
(`IL_003e callvirt Thing::get_Graphic` → `IL_0043 ldfld Graphic::data`). The
reported offset `0x62` is `ldloc.s 7`, immediately followed by
`IL_0064: ldfld GraphicData::graphicClass`. So **`thing.Graphic.data` is null**
for one rock. `Thing.Graphic` itself is fine — that would have faulted at `0x43`.
The code guards `def.graphicData.Linked` but never checks the *runtime* graphic's
`data` back-reference, so any rock whose current graphic is a coloured/wrapped
copy or a custom `Graphic` subclass that never assigns `data` trips it. **The
offending def is not printed and cannot be recovered from this log.**

**Answering the actual question — does it leave mineables uncoloured?**
**Partially, yes.** The method has exactly one exception-handling clause,
`flags=2` (finally), covering the enumerator's `Dispose`. **There is no `catch`
anywhere in it.** The NRE therefore escapes the whole `foreach` at the first bad
rock: every lump not yet reached keeps its vanilla colour for that map. The
sibling long event (`b__1` → `mapDrawer.RegenerateEverythingNow`) is separate and
still runs, so the *partial* recolor is drawn.

**Not persistent, and retried:** it hangs off `Map.FinalizeInit`, which fires on
every map generation and every save load, and `graphicInt` is runtime-only, so
each load redoes the whole loop from scratch — and will abort at the same rock
until load order or defs change.

**Player-zero verdict: cosmetic, and barely that.** Some ore lumps are tinted,
the rest look vanilla, on a map the player has never seen tinted differently.
Nothing but `Thing.graphicInt` is written — no def, comp, stat or terrain state.
Cost is one red line per map load.

**Recommendation: waiver.** Draft below. If the ore tinting is ever wanted
properly, the supported off switch is disabling *Perspective: Ores* in ReGrowth 2's
mod settings — but turning the feature off to silence a cosmetic error is a worse
trade than leaving it. **Do not propose a mod removal over this.**

---

## 3. DRAFT entries for `vendor/wisdom/benign_log_errors.md`

⚠️ **Draft only. `benign_log_errors.md` is NOT edited by this report** — another
seat may be inside it. Whoever lands these should paste them into §1 and renumber
if §1.12 is taken.

> ### 1.12 `Exception getting Verse.Graphic_Multi at :` ×14 — Yautja PawnKind lifeStages
> ```
> Exception getting Verse.Graphic_Multi at : System.ArgumentNullException: Value cannot be null.
> Parameter name: key
>   at Verse.ModContentHolder`1[T].Get (System.String path)
>   at Verse.Graphic_Multi.Init (Verse.GraphicRequest req) [0x0011f]
>   at Verse.GraphicDatabase.Get (Verse.GraphicRequest req)
> ```
> **Owner:** `[AB] Xenotype: Yautja` (`biotechrace.yautja.alleyballey`, workshop
> `3536839586`) · **Root cause:** `PawnKinds_BaseAbstract.xml` line 60,
> `BaseYautjaPawnKind`, sets `drawSize` by writing a `<bodyGraphicData>` node with
> **no `texPath`**:
> ```xml
> <lifeStages>
>   <li><bodyGraphicData><drawSize>0.75</drawSize></bodyGraphicData></li>
>   <li><bodyGraphicData><drawSize>1</drawSize></bodyGraphicData></li>
> </lifeStages>
> ```
> `GraphicData.texPath` defaults to **null** (not `""`), and
> `PawnKindLifeStage.ResolveReferences` auto-types any `graphicClass`-less
> lifeStage graphic as `Graphic_Multi` — so the def asks the database for a
> `Graphic_Multi` at a null path. 7 loaded kinds × 2 lifeStages = **exactly 14**,
> confirmed against the live def dump, which is also the only place the culprit is
> visible: those 14 `GraphicData` objects hold
> `cachedGraphic = Graphic_Single "UI/Misc/BadTexture"`, i.e. `BaseContent.BadGraphic`,
> the value `GraphicDatabase.Get` returns from its catch.
>
> **Why harmless:** the result is cached, so it is one-shot at load — 14 lines and
> never again, regardless of playtime. And `bodyGraphicData` is read only by
> `PawnRenderNode_AnimalPart` (the **Animal** render tree); `ABAlien_Yautja` is
> `intelligence Humanlike` with `renderTree Humanlike`, whose
> `PawnRenderNode_Body.GraphicFor` resolves from `bodyType.bodyNakedGraphicPath`
> and never reads it. **Nothing is drawn from the bad graphic. Player-zero sees
> nothing.**
>
> 🔴 **The stack can never name the caller on this error class.** RimWorld prints
> the *exception's* trace, which unwinds only to the `catch` inside
> `GraphicDatabase.Get` — every frame above it is gone. Do not look for a mod frame
> and do not fall back to log adjacency (§4b.1). **Attribute it from the def dump
> instead:** scan every `GraphicData` for `graphicClass = Graphic_Multi` with a
> null/empty `texPath` and match the count.
>
> **Upstream bug**, reportable at `https://github.com/AlleyBalley/-AB-Xenotype-Yautja`.
> Locally fixable by deleting the two `<bodyGraphicData>` blocks (they already
> contribute nothing), but not worth a patch we maintain.

> ### 1.13 ReGrowth 2 `RecolorMineables` NRE — one lost ore tint per map load
> ```
> Exception from long event: System.NullReferenceException
>   at ReGrowthCore.Map_FinalizeInit_Patch+<>c__DisplayClass1_0.<ProcessMap>g__RecolorMineables|4 () [0x00062]
>   at Verse.LongEventHandler.UpdateCurrentSynchronousEvent (System.Boolean& sceneChanged)
> ```
> **Owner:** ReGrowth 2 (`ReGrowth.BOTR.Core`, workshop `2260097569`), its
> *Perspective: Ores* feature · **Root cause:** `RecolorMineables` reads
> `thing.Graphic.data` (IL_003e/IL_0043) and dereferences it at IL_0064
> (`ldfld GraphicData::graphicClass`) — offset `0x62` in the log is the `ldloc.s 7`
> that pushes it. One resource rock's **runtime** graphic has a null `data`
> back-reference. The code guards `def.graphicData.Linked` but never the live
> graphic's `data`, so a wrapped/coloured graphic or a custom `Graphic` subclass
> trips it. The def is not printed and cannot be recovered from the log.
>
> **Why harmless — with one honest caveat.** The only field written anywhere in the
> method is `Thing::graphicInt`; no def, comp, stat or terrain state is touched, and
> `graphicInt` is runtime-only so nothing is persisted to the save. ⚠️ But the
> method has **no `catch`** (its single EH clause is the enumerator's `finally`), so
> the throw aborts the *whole* recolor loop — lumps after the bad rock keep vanilla
> colours until the next load. It re-runs on every `Map.FinalizeInit` (map gen and
> save load) and will abort at the same rock each time. Cost: some ore tinting the
> player has never seen, plus one red line per map load.
>
> ⚠️ **Do not clear this one with §6.** §6's retraction ("one failed queued action
> costs one action") is about `Could not execute post-long-event action`, which is
> **0** in this log. This is `Exception from long event`, thrown out of the
> synchronous long-event update — a different message and a different guarantee.
>
> **Off switch if ever wanted:** disable *Perspective: Ores* in ReGrowth 2's mod
> settings. Not worth it — that trades the feature away to silence a cosmetic line.

---

## 4. Method note — what to reuse

The reusable technique here is **the def dump as the attribution instrument**.
When a caught engine exception hides its caller, the def dump written by the same
run holds the *end state* the exception produced, and matching the population of
broken defs against the error count attributes it without a stack trace and
without a game load. Both halves matter: the count match narrows it, the cached
`BadGraphic` value proves it.

Scanner used (throwaway, recursive over every `GraphicData`-shaped node in all 528
dump files) is not committed; it is 20 lines and is quoted in the commit for this
report if anyone needs it again.
