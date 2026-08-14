# HAR's `CanEverProduceChild` patch failure — characterised, cause proven, impact ~nil

**Seat:** OPS. **Game DOWN throughout — no load was spent on this.**
**Follow-up to:** `D:\Luke\dev\Rimworld\observed\2026-08-13_log_harvest_1004.md` §c1 / §e.
**Method:** offline IL disassembly with `D:\Luke\dev\Rimworld\src\RimMandrake\Utils\ilprobe\il.py`
(used as-is; only the hardcoded target DLL was repointed in a scratchpad copy, the repo
tool was not edited), plus the def dump and `ModsConfig.xml`.

---

## Verdict in four lines

1. **It is a two-mod transpiler conflict, not an HAR bug and not a version drift.**
   **Universal Pregnancy** transpiles the same method first and shifts the IL out from
   under HAR's fixed-offset pattern match. Proven from both assemblies' IL below.
2. **It is NEW** — one observation, today, and no earlier log on disk got far enough to
   have shown it. "New" is honest; "new *today*" is not provable.
3. **Player-zero impact: essentially none, and for Jawas exactly none.** The lost patch
   feeds **one** call site in all of RimWorld 1.6 — the Social-tab pregnancy-approach
   icon. It does **not** gate conception. The gate that does is a *different* HAR patch
   which applied successfully.
4. **No test is owed.** This was settled offline. Recommended action: **leave it alone**,
   and add one standing check so it cannot hide next time (§5).

---

## 1. What exactly failed

`Player.log` line 3474–3484 (`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Player.log`),
once, and it is the log's **only** `Error during patching` (`grep -c` → 1):

```
Error during patching RimWorld.PregnancyUtility :: Verse.AcceptanceReport CanEverProduceChild(Verse.Pawn, Verse.Pawn) with: pre  | post: Void CanEverProduceChildPostfix(Verse.Pawn, Verse.Pawn, Verse.AcceptanceReport ByRef) | trans: System.Collections.Generic.IEnumerable`1[HarmonyLib.CodeInstruction] CanEverProduceChildTranspiler(System.Collections.Generic.IEnumerable`1[HarmonyLib.CodeInstruction])
System.Exception: Wrong null argument: brtrue NULL
[Ref A3C4372C]
  at HarmonyLib.MethodCreatorTools+<>c__DisplayClass12_0.<EmitCodes>b__0 (HarmonyLib.CodeInstruction codeInstruction) [0x00155] in <024a0e6ec8c2437ead047b6279389c23>:0
  at HarmonyLib.CollectionExtensions.Do[T] (System.Collections.Generic.IEnumerable`1[T] sequence, System.Action`1[T] action) [0x00014] in <024a0e6ec8c2437ead047b6279389c23>:0
  at HarmonyLib.MethodCreatorTools.EmitCodes (HarmonyLib.MethodCreator _, HarmonyLib.Emitter emitter, System.Collections.Generic.List`1[T] codeInstructions) [0x0000d] in <024a0e6ec8c2437ead047b6279389c23>:0
  at HarmonyLib.MethodCreator.CreateReplacement () [0x008ca] in <024a0e6ec8c2437ead047b6279389c23>:0
  at HarmonyLib.PatchFunctions.UpdateWrapper (System.Reflection.MethodBase original, HarmonyLib.PatchInfo patchInfo) [0x0007c] in <024a0e6ec8c2437ead047b6279389c23>:0
  at HarmonyLib.PatchProcessor.Patch () [0x0013c] in <024a0e6ec8c2437ead047b6279389c23>:0
  at HarmonyLib.Harmony.Patch (System.Reflection.MethodBase original, HarmonyLib.HarmonyMethod prefix, HarmonyLib.HarmonyMethod postfix, HarmonyLib.HarmonyMethod transpiler, HarmonyLib.HarmonyMethod finalizer) [0x0002a] in <024a0e6ec8c2437ead047b6279389c23>:0
  at AlienRace.AlienHarmony.Patch (System.Reflection.MethodBase original, HarmonyLib.HarmonyMethod prefix, HarmonyLib.HarmonyMethod postfix, HarmonyLib.HarmonyMethod transpiler, HarmonyLib.HarmonyMethod finalizer) [0x000ab] in C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\AlienRaces\Source\AlienRace\AlienRace\AlienHarmony.cs:42
```

Line 3485 immediately after: `Alien race successfully completed 277 patches (50 pre, 81 post, 146 trans) with harmony.`
Everything else HAR wanted **did** apply. This one method did not.

🔴 **Correction to the harvest doc.** §c1 read the `pre | post | trans` list as "every patch
queued on that method … so HAR is the only patcher involved." **That is wrong.** The
message is emitted by **HAR's own wrapper** (`AlienHarmony.cs:42`) and lists only the
arguments *of that call*. Patches already registered on the method by other mods are
invisible in it — and there is one, which is the whole cause. The path in the trace is
likewise erdelf's *build machine*, not an install here.

### HAR's identity and install

| | |
|---|---|
| folder | `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\839005762` |
| About name / packageId | Humanoid Alien Races / `erdelf.HumanoidAlienRaces` |
| assembly | `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\839005762\1.6\Assemblies\AlienRace.dll` (417,792 bytes, mtime 2026-07-16) |
| version | **none declared** — no `<modVersion>`, no `Manifest.xml`, assembly metadata is the generic `1.0.0.0`. HAR cannot be version-pinned by any file it ships. |
| load order | `ModsConfig.xml` line **489** (late in a 570-mod list; an independent census put it at position 486, the small difference being how the file's header lines are counted — the *ordering* is what matters and both agree) |
| duplicate installs | **none** — nothing named AlienRace under the local `Mods\` folder |

The `1.6\Assemblies\` pair (DLL + PDB) carries mtime 2026-07-16 while every other file in
the mod carries the Steam download stamp 2025-12-17 — the normal signature of a Steam
delta update that touched only the assembly. Noted, not load-bearing: the conflict below
does not depend on which HAR build is installed.

---

## 2. The conflicting patcher — named, with the IL

**Universal Pregnancy**, `1trickPwnyta`, modVersion **1.0.3**, packageId
`universalpregnancy.1trickPwnyta`, workshop **3303758779**.
`C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3303758779\1.6\Assemblies\UniversalPregnancy.dll`
`ModsConfig.xml` line **353**, comfortably ahead of HAR at line **489**.
Its own About says it *"Removes gender requirements from everything related to reproduction."*

**It is the only other transpiler, and that is a measured result, not an assumption.** A
census of **5,330 DLLs across 1,238 workshop mods** plus the local
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\` folder found exactly three
live assemblies naming `CanEverProduceChild` — HAR, Universal Pregnancy, and one
prefix/postfix patcher (§2a). Ruled out by name because they are the usual suspects:
Vanilla Expanded Framework, Big and Small / BetterPrerequisites, EBSG, Outland Genetics,
Alpha Memes and every VRE race mod match the wider `PregnancyUtility` net but contain **no**
`CanEverProduceChild`. RJW is not installed at all. Way Better Romance
(`divineDerivative.Romance`) carries the string only inside reflection code reaching into
the **Alternate Fertility** mod's transpiler — Alternate Fertility is not installed, so that
branch is dead. ~35 further raw hits are copies of the game's own `Assembly-CSharp.dll`
sitting in mods' `Source\obj\`, `Source\bin\` and `lib\` folders, which RimWorld never
loads.

### 2a. A third patcher exists, and its silence is evidence

**Intimacy - Gender Works** (`LovelyDovey.Sex.WithRosaline`, workshop 3534254491,
`…\3534254491\1.6\Assemblies\AnnoyingPatchThatHasToRunLate.dll`, `ModsConfig` position
~540 — *after* HAR) ships `PregnancyUtility_CanEverProduceChild_Patch`. It is
**prefix/postfix only**: the assembly contains `HarmonyPrefix` and `HarmonyPostfix` and no
`HarmonyTranspiler` string anywhere, so it cannot be the cause.

But it patches the same method *later than HAR*, which forces Harmony to rebuild the
wrapper again — and that rebuild **did not throw** (the log has exactly one
`Error during patching`). Had HAR's failed transpiler stayed in the method's `PatchInfo`,
the rebuild would have re-run it and failed identically. It did not. So HAR's patches were
cleanly discarded rather than left poisoning the method, and the live method is
**vanilla + Universal Pregnancy + Intimacy - Gender Works**, with HAR's layer simply
absent. That is the good outcome, and it is why the damage is confined to §4.

It ships the type `UniversalPregnancy.Patch_PregnancyUtility_CanEverProduceChild` with a
`Transpiler`. `[Universal Pregnancy] Loaded.` is `Player.log` line **668**; HAR patches at
line **3474**. UP's transpiler is therefore registered first and runs first — HAR's
transpiler never sees vanilla IL.

### The exact collision, instruction for instruction

**Vanilla `PregnancyUtility.CanEverProduceChild`** (`Assembly-CSharp.dll`, 1.6.4871 rev590)
at the same-gender check:

```
IL_0046: ldarg.0
IL_0047: ldfld     Pawn::gender
IL_004c: ldarg.1
IL_004d: ldfld     Pawn::gender
IL_0052: bne.un.s  IL_0083         <-- a branch; its operand is a Label
```

**HAR's `CanEverProduceChildTranspiler`** (`<CanEverProduceChildTranspiler>d__62::MoveNext`)
scans for `ldfld Pawn.gender` and, at step 0, emits — note the **fixed `+3`**:

```
IL_0128: ldsfld    OpCodes::Brtrue
IL_0139: ldc.i4.3                          ; i + 3
IL_013b: callvirt  List<CodeInstruction>::get_Item
IL_0140: ldfld     CodeInstruction::operand
IL_0145: newobj    CodeInstruction::.ctor  ; new CodeInstruction(Brtrue, list[i+3].operand)
```
(steps 1 and 2 do the same with `+2` at `IL_0200` and `IL_02c7`.)

**Universal Pregnancy's transpiler** (`typedef#34 <Transpiler>d__0::MoveNext`), on meeting
the first `Bne_Un_S`, yields **two `Pop` instructions** and then rewrites the branch's
opcode to `Br_S`:

```
IL_00ae: ldsfld    OpCodes::Bne_Un_S     ; match the same-gender branch
IL_00c1: ldsfld    OpCodes::Pop          ; yield Pop
IL_00e8: ldsfld    OpCodes::Pop          ; yield Pop
IL_0114: ldsfld    OpCodes::Br_S
IL_0119: stfld     CodeInstruction::opcode   ; bne.un.s -> br.s  (unconditional)
```

So by the time HAR looks, the stream reads:

```
ldarg.0 ; ldfld gender ; ldarg.1 ; ldfld gender ; POP ; POP ; br.s
   i-1        i            i+1        i+2        i+3   i+4    i+5
```

`list[i+3]` is now **`Pop`**, whose `operand` is `null`. HAR builds
`new CodeInstruction(OpCodes.Brtrue, null)`, Harmony's `EmitCodes` refuses it, and the
whole `UpdateWrapper` for the method aborts — taking **both** HAR's transpiler and HAR's
postfix with it.

**On unmodified vanilla IL, HAR's transpiler is correct.** I walked all three of its match
sites against the real 1.6 IL (`+3` at `IL_0052 bne.un.s`, `+2` at `IL_008a beq.s`, `+2` at
`IL_0098 beq.s`) — every one lands on a real branch with a non-null operand. HAR alone does
not fail. It is the pair.

**What is running now, precisely:** not "vanilla". UP's transpiler was applied
successfully *before* HAR's call threw, so `CanEverProduceChild` runs as
**vanilla + Universal Pregnancy** — i.e. *more* permissive than vanilla, with the
same-gender rejection removed. HAR's layer is the only thing missing.

*(Prepatcher — `zetrith.prepatcher`, log lines 59–634 — does rewrite Assembly-CSharp before
Harmony sees it. It injects fields rather than rewriting arbitrary method bodies, and no
cache of the rewritten assembly is on disk to diff, so the IL above is the on-disk vanilla.
Recorded as a caveat; it does not change the conclusion, which rests on UP's inserted
`Pop`s.)*

---

## 3. Is it new?

**New — as a *record*. Not datable as an *event*.**

- Repo-wide grep for `CanEverProduceChild`, `Wrong null argument`, `Error during patching`,
  `AlienHarmony` hits **only** today's harvest and the raw log. Nothing in
  `D:\Luke\dev\Rimworld\vendor\wisdom\benign_log_errors.md`, nothing in
  `D:\Luke\dev\Rimworld\skills\rimworld-modding\references\`, nothing in
  `infrastructure\state\`. `git log --all -S 'CanEverProduceChild'` returns one commit —
  the harvest itself.
- `benign_log_errors.md` has **no** entry for `Error during patching` at all. §1.2 is the
  near-miss and applying it would be a trap: it covers XML `PatchOperation` failures, whose
  "a failed patch is a no-op" reasoning is **false** for Harmony — a failed Harmony patch
  silently reverts *runtime behaviour*.
- 🔴 **One sample, and only one.** The only other log on disk,
  `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Player-prev.log`,
  is 708 lines and contains no `Alien race successfully completed` — HAR never reached its
  patching phase, so its silence proves nothing. The copy under
  `observed\2026-08-13\logs\` is byte-identical (same md5) to the live
  `Player.log`, so it is the same run, not a second observation.
  **Anyone who says "this started today" is over-reading one sample.** Given both mods have
  been in the stack unchanged, the honest reading is that it has probably been happening
  for a while and was never checked for.

---

## 4. 🔴 Player-zero: what this actually does to the campaign

### 4a. Vanilla calls `CanEverProduceChild` from exactly one place, and it is UI

Token-level cross-reference of every method body in `Assembly-CSharp.dll` for calls to
`PregnancyUtility::CanEverProduceChild` (token `0x0600C712`) returns **one** caller:

```
SocialCardUtility::DrawPregnancyApproach
```

and there it does one thing (`IL_0064` → `IL_0099`): if the report is not `Accepted`, set
`GUI.color = grey` and skip the approach dropdown. That is the pregnancy-approach icon in a
pawn's Social tab and its tooltip. **Nothing else in the game consults it.**

### 4b. Conception is decided somewhere else entirely — and HAR's gate there is intact

```
PregnancyChanceForPartners  =  PregnancyChanceForPawn(second)
                             × PregnancyChanceForWoman(first)
                             × GetPregnancyChanceFactor(approach)
```
No call to `CanEverProduceChild` anywhere in that chain.

And HAR enforces its race rule **there**, in a patch that applied fine —
`AlienRace.HarmonyPatches::PregnancyChanceForPartnersPrefix`:

```
IL_0002: call     RaceRestrictionSettings::CanReproduce
IL_0007: brtrue.s IL_0012
IL_000a: ldc.r4   0.0
IL_000f: stind.r4              ; __result = 0f
IL_0010: ldc.i4.0
IL_0011: ret                   ; skip original
```

That is the *same* `RaceRestrictionSettings.CanReproduce(first, second)` the lost postfix
called. **HAR's cross-race breeding rules are still enforced on actual conception.** The
harvest's §c1 conclusion — "HAR's cross-race breeding rules … are simply not applied" — is
the one line in it that does not survive checking.

Live proof from this very log, line 9678, no load required:

```
Pregnancy chance for Jekk 'PlewWheedut' PlewWheedut and Sasha 'Sasha' Luskov was 0.2340059
```

### 4c. For Jawas specifically the lost patch was a no-op regardless

From the def dump (`…\DefDump\defs\PawnKindDef.json`), `OuterRim_Jawa`:

```json
"race": "Human",
"xenotypeSet": { "xenotypeChances": [ { "xenotype": "OuterRim_Jawa", "chance": 1 } ] }
```

**Jawas are the vanilla `Human` ThingDef wearing a Biotech xenotype — not a HAR alien
race.** So for Jawa × Jawa and Jawa × human, HAR's `CanReproduce` compares `Human` to
`Human`: same def, which routes to `canReproduceWithSelf` on Human's own
`raceRestriction` — and HAR's `1.6\Patches\HumansAreAliensToo.xml`, the patch that makes
`Human` a `ThingDef_AlienRace` at all, gives it an **entirely empty** `<raceRestriction>`
block. Permissive. The postfix, had it run, would have returned `Accepted` and changed
nothing.

### 4d. So: would the player notice?

**No — and for the colony's own pawns, not even in principle.**

The complete difference this defect makes, at the keyboard:

- For a pair of **actual HAR alien races that restrict reproduction** (the stack does carry
  some — `Jawa_Spawn_Hutt`, `_Gand`, `_Kubaz`, `_Lasat`, `_Muun`, `_Zygerrian` and friends),
  the Social tab's pregnancy-approach icon is **coloured and clickable instead of greyed**,
  and the tooltip does not say `HAR.ReproductionNotAllowed`. Clicking it still achieves
  nothing: `PregnancyChanceForPartnersPrefix` forces the chance to 0.
- For races with non-standard reproduction genders, that same Social-tab report may read
  vanilla's "PawnsHaveSameGender" where HAR would have allowed it. Report only.
- **For Jawas — the entire player colony — no difference at all**, because Human×Human was
  never restricted.

**The honest answer is that the player would never notice, and I am saying so.** This is a
cosmetic tooltip regression on a screen the owner may never open, not a reproduction
defect. It closes at **low priority**. §e of the harvest asked for an owner decision
between "pin/roll back HAR", "drop a conflicting reproduction mod" and "accept vanilla
breeding behaviour" — none of those is worth doing, because the third one is not what is
happening.

**Recommended action: leave both mods exactly as they are.** Rolling back HAR is
impossible to do precisely (it declares no version anywhere). Dropping Universal Pregnancy
would fix a tooltip at the cost of a feature that was deliberately installed. Reordering so
HAR patches first would only move the same fixed-offset breakage onto UP's transpiler.

---

## 5. The smallest test that settles it

**None is needed — this was settled offline, and no game load should be spent on it.**
Listed cheapest-first anyway, because the owner may want confirmation:

| # | cost | observation |
|---|---|---|
| 1 | **already done, zero** | The IL in §2 and the xref in §4a. Both mods' assemblies and `Assembly-CSharp` are ordinary files. |
| 2 | **already in hand, zero** | `Player.log` line 9678 `Pregnancy chance for … was 0.2340059` — non-zero, so `PregnancyChanceForPartners` with HAR's prefix is live and computing. |
| 3 | **rides a planned load, ~1 min** | On the live bridge, open the Social tab of any colonist and look at the pregnancy-approach icon against another colonist. Jawa×Jawa: coloured and working, exactly as it should be. To see the defect at all you must pair a colonist with a HAR alien race that restricts reproduction — the icon will be **coloured when it should be grey**, and the dev-console log line will still read `Pregnancy chance for … was 0`. That contrast *is* the whole bug. |
| 4 | **never** | A dedicated load. Not justified by anything above. |

**One cheap permanent fix, and it is the only change worth making.**
`D:\Luke\dev\Rimworld\src\RimMandrake\Utils\harvest_log.py` has no pattern for
`Error during patching` — its `patchfail` check regex is
`[Pp]atch operation .* failed|PatchOperation.*failed`, which is the **XML** system, a
different thing. A Harmony patch failure has never been a standing check, which is exactly
why this could not be dated. **Add `Error during patching` as a standing check with
baseline 1**, so the next load answers "was this always there, and is it still just the
one?" for free. That file is not mine to edit mid-session — filed here for whoever owns it.

*(Not filed to `TODO.md`/`NEXT_RELOAD.md` from this session: several seats are live in the
tree and this brief was explicitly scoped to one file.)*

---

## Provenance

Every IL quotation above was produced with
`D:\Luke\dev\Rimworld\src\RimMandrake\Utils\ilprobe\il.py` against, in turn:

- `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed\Assembly-CSharp.dll`
- `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\839005762\1.6\Assemblies\AlienRace.dll`
- `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3303758779\1.6\Assemblies\UniversalPregnancy.dll`

A DLL has no line numbers, so findings are cited as type + method + IL offset. The repo
tool was **not** modified; scratchpad copies were repointed at the two mod assemblies.
Nothing in the game install, the workshop tree or the config was written to.
