# WILD_ANIMALS_PADDED_LISTS_1 — offline half done: mechanism strongly narrowed, exact patch still unnamed

Filed 2026-08-29T07:01:49Z, `caused_by: COLD_LOAD_RUN_SHEET_1`, spec at a session scratchpad
path (`/tmp/claude-1000/.../420ce630-.../scratchpad/padspec.md`) — copied in full below since a
scratchpad is not durable; this item cites this file from now on, not that path.

## Spec (as filed)
Every one of the 81 biomes with a `wildAnimals` list holds EXACTLY 1024 records in the
2026-08-29T05-18-06Z capture (`defs/BiomeDef.json`, post-patch reflection read) — including
biomes our BiomeCast patch REPLACED with ~29-record lists. An unidentified C# pass pads every
biome's `wildAnimals` to the full animal-kind roster at load: existing (cast) records keep
their weights; `race.wildBiomes` weights are materialized INTO `wildAnimals`; Anomaly entity
kinds are excluded (can never wild-spawn); everything else is padded in at commonality 0.

## What this pass established, offline, without the bridge

**1. Our own dumper is clean — ruled out as the source.** Read
`src/RimMandrake/RimDefDump/Source/DefDumper.cs:620-652`: it reads `BiomeDef.wildAnimals`
via raw reflection (`GetField("wildAnimals", NonPublic|Instance)`) into an `IList` and reports
exactly what is there. It does not compute, merge or pad anything. Whatever holds 1024 records
already held them **before** the dumper touched the def — this is a load-time mutation to the
live def, not a dump-time artifact.

**2. `BiomeDef.AllWildAnimals` (vanilla) is not the mechanism.** Read from 1.6 source
(`RimWorld/BiomeDef.cs:290-300`): it's a filtered `IEnumerable<PawnKindDef>` over
`DefDatabase<PawnKindDef>.AllDefs` where `CommonalityOf*Animal > 0`. A *filter*, computed on
each access, never written back into the private `wildAnimals` list — cannot explain 1024
records at commonality 0 sitting in the raw field.

**3. Strong numeric correlation, not yet a name.** `1026` PawnKindDefs in the current dump have
a `race` whose `intelligence == "Animal"` (1737 total PawnKindDefs; 2042 ThingDefs are
Animal-intelligence races). **1026 vs the measured 1024 is a 99.8% match** — strong evidence
the padder is "every PawnKindDef whose race is an animal," not some other count. The 2-record
gap is unexplained by this pass (not resolved to the spec's ~10 excluded Anomaly-entity claim,
which is a bigger number than 2 — needs the live half to reconcile).

**4. Exhaustively grepped every vendored `.cs` file mentioning `BiomeDef`** (89 files across
~25 mods that have decompiled/cloned source under `vendor/mod_sources/`). Only one Harmony
patch touches the animal-commonality path at all —
`Megafauna_src/.../Harmony/BiomeDef_CommonalityOfAnimal_Patch.cs`, a `[HarmonyPostfix]` on
`BiomeDef.CommonalityOfAnimal` that multiplies the RESULT for specific toggleable megafauna
defNames. It never touches the `wildAnimals` list and cannot produce 1024 raw records. Ruled
out. **Nothing else in the vendored subset writes to `wildAnimals` at all.**

## Why this needs the bridge to finish

`vendor/mod_sources/` holds decompiled/cloned source for a minority of the 582 active mods, not
all of them — the padder is very likely in one of the un-vendored mods, or is a Harmony patch
whose target method name doesn't literally contain "BiomeDef" or "wildAnimals" as a string (a
transpiler on `DefGenerator.ImpliedXmlDefs` or a generic `PostLoad`/`ResolveReferences` pass
would not have matched this grep). **Naming the exact assembly needs a live Harmony patch
inventory** — `Harmony.GetAllPatchedMethods()` / `Harmony.GetPatchInfo(method)`, filtered to
methods on `BiomeDef` or `DefDatabase<BiomeDef>`, read the `owner` id (mod packageId) off each
patch. **No bridge tool exists for this today** — recommended, not built here (would mean a
second HarmonyLib contact point in the companion; `JawaBenchArgGuard.cs`'s own doc comment
says Harmony contact is deliberately isolated to one file, so this is a real design decision
for whoever builds it, not a quick add).

---

## The missing tool now exists in source — BUILT, UNDEPLOYED, UNPROVEN LIVE

Owner ruling 2026-08-29: build it, as a second isolated Harmony contact point (not routed
through `JawaBenchArgGuard.cs`). `jawa/harmony_patches` is written in
`JawaBenchHarmonyInspect.cs` — takes a type name, returns every Prefix/Postfix/Transpiler/
Finalizer patching it via `HarmonyLib.Harmony.GetAllPatchedMethods()` +
`GetPatchInfo(method)`, with each patch's owner id and its patch method's declaring
assembly (usually names the mod).

✅ **Compiled clean under `python.exe build.py` (Windows-side, run from WSL bash — not a real
barrier, owner-said)**: 0 errors, 0 warnings, DLL contains the tool. First attempt failed —
`HarmonyLib.Patches.Prefixes/Postfixes/Transpilers/Finalizers` are `ReadOnlyCollection<Patch>`
at runtime despite the XML doc's "array of Patch" prose, fixed in `833dd0d8`. So the
static-vs-instance guess on `GetAllPatchedMethods()`/`GetPatchInfo()` was right; the array-vs-
collection guess was not — exactly the reason nothing here was ever claimed proven before a
real compiler ran it.

🔴 **NOT DEPLOYED, on purpose — resolved, not mysterious.** A plan-only (no `--gm`) build
flagged 27 tools the live game copy has and this build doesn't (`jawa/lord_assault_spawn`,
`jawa/weather_set`, `jawa/animal_bond`, `jawa/ritual_start`, others). Checked and closed: all
27 are `#if JAWA_GM_TOOLS`-gated in committed source (verified by grep), and BENCH's own
ledger note at `2026-08-29T05:06:17Z` records deploying `--gm` from commit `a36db094` earlier
the same day. **Nothing is lost, no rogue build — just a flag.** Deploy this with
`python.exe build.py --gm --apply` (game closed) to keep the GM pair live alongside the new
tool; a bare `--apply` would legitimately drop them, same as any non-`--gm` build always has.

## 2026-09-01, first live use of the tool (FOUNDRY, owner AFK)
Deployed and called for real. `jawa/harmony_patches {typeName: "BiomeDef"}`
returns exactly 2 methods, neither explaining the padding: `get_DrawMaterial`
(rendering, irrelevant) and `CommonalityOfAnimal` (2 postfixes — Megafauna
and AlphaAnimals both multiplying the RESULT float, cannot write 1024 raw
`wildAnimals` records). **Rules out any BiomeDef-targeted patch as the
mechanism** — confirms the item's own prediction that a `methodCount` with
no smoking gun on `BiomeDef` itself means the padder acts through a
different type.

Tried `DefGenerator` next (the other candidate the item names) — 2 methods,
several patches each, most unrelated by name/mod (DefNameLink,
ResearchReinvented, ResourceDictionary, IsekaiLeveling, OuterRimDroids,
MinifyEverything, Numbers, WorkTab). **One real lead**: owner
`RedMattis.BigSmall_Early` (assembly `BSXeno`) has BOTH a postfix on
`DefGenerator.GenerateImpliedDefs_Postfix` AND — more suggestively — a
**transpiler** named `InsertBeforeResolveAllWantedCrossReferences` on
`GenerateImpliedDefs_PreResolve`. The name alone is a strong match for
"materialize weights into a list before cross-ref resolution," which is
exactly the padding spec's own mechanism description. **NOT CONFIRMED** —
could not locate the actual assembly on disk to grep for `wildAnimals`
(checked `RedMattis.BigSmall` / workshop `2894397737`, content-only, no
Assemblies folder; `RedMattis.BigSmall.Core` / workshop `2920751126`, same
— no `.dll` found under either despite the bridge reporting live Harmony
patches from `BSXeno`). The assembly must load from a folder/mechanism this
pass didn't find (possibly a differently-versioned Assemblies path, or a
"BSXeno" sub-mod bundled inside a sibling BigSmall-family workshop item not
checked yet — there are ~10 RedMattis.BigSmall.* items in the active list).

**Handed to a fresh pass/subagent to finish**: find the actual `BSXeno.dll`
on disk (search all `RedMattis.*` workshop folders' `Assemblies/` — plural,
version-scoped, e.g. `1.6/Assemblies/`), confirm or rule out a `wildAnimals`
field write via `strings`/decompile, and if confirmed, check whether it's
gated by a settings toggle (worth knowing before proposing any fix).

## Prove it, once deployed
`python.exe src/RimMandrake/bridgetools/prove_harmony_patches.py` — selftest already green
(`python3 ... --selftest`, no game needed). Or by hand:
```
jawa/harmony_patches {typeName: "BiomeDef"}
jawa/harmony_patches {typeName: "BiomeDef", methodName: "CommonalityOfAnimal"}
```
Expect a `postfixes[]` or `transpilers[]` entry whose `patchAssembly` names something
NOT in the 89-file vendored subset already exhausted — that assembly is the answer to
this item's criterion below. `methodCount: 0` on `BiomeDef` with no `methodName` filter
would mean the padder acts through a DIFFERENT type (e.g. a `DefGenerator` or
`ResolveReferences` transpiler) — worth trying if the direct query comes back empty.

## criteria
- [ ] **The padding assembly named with the method that does it** — NOT MET. Needs live Harmony
      patch inspection (see above); offline search of the vendored source subset exhausted.
      Tool to do this now exists in source; needs build + deploy + a live call to close.
- [ ] Owner ruling on exclusivity (145 non-cast animals in Desert) and on the 10 excluded
      Anomaly entity records — **owner's call, not FOUNDRY's**, per the item's own framing.
- [ ] `biome_animal_conflicts.py`'s b-side (`race.wildBiomes`) validity — not re-checked this
      pass; follows from naming the mechanism first.
