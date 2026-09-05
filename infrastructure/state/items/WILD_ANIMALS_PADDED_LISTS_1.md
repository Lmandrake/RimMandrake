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

## 2026-09-01, subagent verdict: BOTH leads RULED OUT — the lead was a red herring
`BSXeno.dll` actually ships from `RedMattis.BetterPrerequisites` (workshop
`2925432336`, `1.6/Base/Assemblies/BSXeno.dll` — NOT from `BigSmall` or
`BigSmall.Core`, which ship no assemblies at all). `strings | grep -i
wildanimals` against every DLL in all 6 active RedMattis.* mods (BSXeno x2
version dirs, BigAndSmall.dll, RedHealth.dll, GravshipSize.dll): **zero
hits**. The transpiler name was coincidental, not evidence.

**Broadened to a full sweep**: every active mod's packageId parsed from
live `ModsConfig.xml`, joined to its workshop folder (first `<packageId>`
in `About.xml`), all 5,403 DLLs under `workshop/content/294100/` found,
filtered to 3,196 under currently-active folders, case-sensitive `strings |
grep "wildAnimals"` across all of them. Real (non-dev-artifact) hits, none
of them the mechanism:
- `zylle.MoreVanillaBiomes`'s `VanillaBiomes.dll` — hit only in a stale,
  unused `1.1/` copy; the loaded `1.6/Assemblies/` copy has no such string.
- `m00nl1ght.GeologicalLandforms`'s `GeologicalLandforms.dll` —
  `Patch_RimWorld_GenStep_Animals` reads `wildAnimals`/`AllWildAnimals` for
  per-landform spawn weighting at MAP-GEN time, not DefGenerator/load time.
  No "1024" literal in the DLL. Wrong mechanism (this is a spawn-time
  filter, not a load-time list mutation).
- `VFEInsectoids.dll`, this project's own `CherryPicker.dll`,
  `GiddyUpCore.dll` — ordinary spawn/removal-time reads, unrelated.
- Everything else was a mod author's bundled dev-reference copy of the
  base game's own publicized `Assembly-CSharp.dll` (never loaded live).

**Still unidentified.** Next-best leads, not yet tried: (a) the field
access may not go through a literal `"wildAnimals"` string at all — a
cross-assembly cached `FieldInfo`/expression-tree accessor, or RimWorld's
own compiler-generated backing-field name, would both evade a `strings`
search entirely; (b) re-run `jawa/harmony_patches` against
`DefGenerator`/`DefDatabase\`1` more exhaustively — this pass only checked
one type name per call and stopped at the first plausible-sounding lead
rather than enumerating every patched method and checking each owner
methodically. Left `doing` — offline half exhausted twice now, live half
needs a more systematic (not lead-driven) pass.

## 2026-09-02, systematic `jawa/harmony_patches` sweep (FOUNDRY) — the whole XML-load path is now clean

Enumerated every patched method (not just one plausible-sounding one) on
every type in the def-load/XML-inheritance pipeline, live, on the current
582-mod set: `BiomeDef` (both methods — same as 09-01, nothing new),
`DefGenerator` (both methods, full prefix/postfix/transpiler lists —
confirms the `BSXeno`/`InsertBeforeResolveAllWantedCrossReferences`
transpiler was the ONLY one there, already ruled out 09-01),
`GenDefDatabase`, `DirectXmlLoader.DefFromNode`, `ShortHashGiver`, and all
5 methods of `LoadedModManager` (`ParseAndProcessXML`, `ApplyPatches`,
`get_ModHandles`, `ErrorCheckPatches`, `LoadModXML`).

**One promising new lead, chased down and RULED OUT with hard evidence:**
`Verse.LoadedModManager.ParseAndProcessXML` carries a transpiler,
`PostInheritanceOperation.XmlInheritanceResolvePostfix.Transpiler`
(owner `bs.postinheritanceoperation`, assembly `PostInheritanceOperation`,
shipped inside Adaptive Storage Framework, workshop `3033901359`,
`1.6/Assemblies/PostInheritanceOperation.dll`) — a generic framework
(Bradson's "Patch Operation Collection") that lets a mod register a
`PatchOperation` to run AFTER XmlInheritance resolves instead of before.
The name alone was a strong match for "materialize data into a list after
inheritance." Checked exhaustively:
- The DLL itself (250 ASCII strings, tiny) has zero `wildAnimals`/`wildanimal`
  hits and is pure framework plumbing (`ApplyWorker`, `XmlInheritance`,
  `resolvedXmlNode` — no domain logic at all).
- It's data-driven: a consuming mod configures it via its own Patches XML
  (`<Operation Class="...PostInheritanceOperation...">`). Grepped **every
  `.xml` file under both `workshop/content/294100/` (all ~1,315 mod
  folders, active or not) and RimWorld's own `Mods/`** for the string
  `PostInheritanceOperation` (case-insensitive, via `python.exe` — WSL's
  `/mnt/c` grep against this many small files was too slow, ran >120s and
  was abandoned): **exactly 3 hits, all three inside Adaptive Storage
  Framework's own `Patches/` folder** (`AddStuffPropsToChunks.xml`,
  `AdjustStoredWeaponRotation.xml`, `EnhanceFixedStorageSettings.xml`) —
  storage/chunk/weapon-rotation patches, nothing biome- or animal-related.
  **No other mod in the entire tree uses this framework at all.** Ruled out.

**`Verse.XmlInheritance` itself carries ZERO Harmony patches** — confirmed
by name (`XmlInheritance`) and by every one of its actual method names read
from source (`Resolve`, `ResolveXmlNodeFor`,
`RecursiveNodeCopyOverwriteElements`, `ResolveXmlNodesRecursively`,
`TryRegisterAllFrom`): all return `methodCount: 0`. Nothing patches the
inheritance resolver itself, at all, on this mod set.

**Where this leaves the mechanism:** every method anywhere near the def
load / XML-inheritance / def-generation pipeline that a Harmony patch could
plausibly target has now been enumerated (not sampled) and none of them can
write 1024 raw `wildAnimals` records — the two real leads this item has
produced (`BSXeno`'s transpiler, `PostInheritanceOperation`'s transpiler)
are both confirmed red herrings by direct evidence, not just "not found."
**This strongly suggests the mechanism is NOT a Harmony patch at all** —
`jawa/harmony_patches` can only see Harmony's patch table. A
`[StaticConstructorOnStartup]` class, or a `Mod`-derived subclass's
constructor (RimWorld calls both after defs finish loading, for
settings/init work), can call ordinary reflection
(`typeof(BiomeDef).GetField("wildAnimals", ...).SetValue(...)`) with no
Harmony involvement whatsoever and would never show up in a patch-table
scan — and a `nameof()`/literal string reference to `wildAnimals` inside
such code WOULD still show up in a `strings` scan (already done, twice,
across the full DLL tree, zero unexplained hits), which means if this
theory is right the field name itself is likely built dynamically
(concatenation, `Type.GetFields()` enumeration by attribute, reflection
over `race.wildBiomes`'s own declaring type) rather than referenced
literally — explaining why three independent full-tree string searches
found nothing.

**Concrete next step for whoever picks this up**: no bridge tool today
enumerates `StaticConstructorOnStartup` classes or `Mod`-subclass
constructors the way `jawa/harmony_patches` enumerates the Harmony patch
table — that's the gap, not a de-prioritized lead. Building one (reflect
`GenTypes.AllTypes`/`LoadedModManager.RunningMods` for
`[StaticConstructorOnStartup]` and `Mod`-derived types, report which
assembly/mod owns each) is the honest next step, not another `strings`
pass — this item has now run three full-tree string/patch searches with
nothing left to search that way.

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

## 2026-09-05, second enumerator tool built/deployed/proven live — StaticCtor/Mod-subclass sweep, one new thematic lead

Built the "concrete next step" this item named on 2026-09-02: `jawa/startup_types`
(`JawaBenchTypeInspect.cs`) enumerates every `[StaticConstructorOnStartup]` type and
every non-abstract `Verse.Mod` subclass, joined to the owning mod via
`LoadedModManager.RunningModsListForReading` (same join `jawa/mod_inventory` uses) —
the gap `jawa/harmony_patches` cannot see, since ordinary reflection from a static
ctor or a Mod subclass's constructor never touches Harmony's patch table.

Built clean (`python.exe build.py --gm --apply`), proven live twice: first on the
13-mod minimal list (142 rows, `filter=BigSmall` correctly returns 0 — that mod isn't
in the minimal list), then on the owner's full 594-mod list (1539 rows). Full-list
dump written to `Transient/startup_types_full_sweep.json` (not committed — Transient,
per repo convention; regenerate with `prove_startup_types.py` against a live bridge).

**One new lead, not yet ruled in or out**: `ChooseBiomeCommonality` (packageId
`mlie.choosebiomecommonality`, mod name "Choose Biome Commonality") is thematically
the strongest candidate this item has produced — its whole stated purpose is letting
the player override each biome's per-animal commonality, which requires exactly the
kind of "every animal kind materialized into every biome's list, non-cast entries at
commonality 0" structure this item describes. A literal-string check
(`strings` on `.../2582875043/1.6/Assemblies/ChooseBiomeCommonality.dll` for
`wildAnimals`/`AllWildAnimals`/`CommonalityOfAnimal`, `MEASURE_ALLOW_SCAN=1`
acknowledged since this is an existence check not a census) found **zero hits** —
consistent with the three prior full-tree string sweeps (09-01) finding nothing, and
consistent with this item's own standing theory that the field access is not a
literal-string reference (a cached `FieldInfo`, or enumeration by attribute/type
rather than by name). **Ruling this mod in or out needs an actual decompile of
`ChooseBiomeCommonality.Main`'s static constructor, not another strings pass.**

Re-confirmed `BigAndSmall.BigSmall` (packageId `redmattis.betterprerequisites`) is
still the only `BigSmall`-filtered `StaticCtor` entry on the full list — same class
already string-ruled-out 09-01 (zero `wildAnimals` hits across `BigAndSmall.dll`,
`BSXeno.dll` x2, `RedHealth.dll`, `GravshipSize.dll`). No new evidence against it.

⚠️ **Unrelated incident, noted for the record, not this item's fault**: the first
attempt to load the full 594-mod list tonight (to build+deploy this tool) crashed
silently during `MapInitializing` — process disappeared from `tasklist`, no
exception in `Player.log`, before `jawa/startup_types` was ever called (the crash
predates this tool's first live invocation by one full relaunch). Second full-list
load succeeded. Full modlist restored and left live; bridge released to the owner
after the sweep (`game is up` received mid-session).

**Next step for whoever picks this up**: decompile `ChooseBiomeCommonality.dll`'s
`Main` static constructor (ILSpy/dotPeek, or read it via a bridge tool that can pull
IL/decompiled source if one exists) and check whether it calls
`typeof(BiomeDef).GetField(...)` or enumerates `DefDatabase<PawnKindDef>.AllDefs`
and writes into a per-biome list. If ruled out too, the next candidates are: (a)
`Fortified Features Framework` and `EBSG Framework` (both generic "framework" mods
with StaticCtor entries and animal-adjacent naming in the sweep, not yet checked),
or (b) reflect `GenTypes.AllTypes` for method bodies that call
`FieldInfo.SetValue` on any field typed `List<AnimalCommonalityRecord>` — a
`jawa/` tool for THAT (grep by field type across all method bodies) does not exist
yet and would need IL inspection, not attribute enumeration, so it's a bigger build
than this one was.


## 2026-09-05, `ChooseBiomeCommonality` RULED OUT by actual decompile — and a
## decompiler now exists on this machine

🔑 **`ilspycmd` (ICSharpCode.Decompiler CLI, v8.2.0.7535) is now installed** at
`C:\Users\Mandrake\.dotnet\tools\ilspycmd.exe` via
`dotnet.exe tool install -g ilspycmd` — this machine had NO decompiler before
today (both this item's 09-02 pass and `TILEGEN_SILENT_REUSE_1`'s 09-05 pass
independently hit that same wall). It works from WSL via the `/mnt/c/...`
interop path for `dotnet.exe`, but **ilspycmd itself needs a native `C:\...`
path**, not `/mnt/c/...` — it reports "File does not exist" on the WSL-style
path. Usage: `ilspycmd.exe -t <Namespace.TypeName> <path-to.dll>` for one
type, `ilspycmd.exe -l c <path-to.dll>` to list every type. **This closes the
"no decompiler" gap named in both this item and `TILEGEN_SILENT_REUSE_1`** —
whoever needs it next does not need to install anything.

**Decompiled `ChooseBiomeCommonality.Main` in full (11 types total in the
whole assembly, all read).** The mod's actual purpose is **biome PLACEMENT
scoring during world generation** — "commonality" here means "how likely is
this biome to be chosen for a given world tile", not "how likely is this
animal within an already-placed biome". Its static constructor Harmony-patches
`<biome>.workerClass.GetScore(BiomeDef, Tile, PlanetTile)` — vanilla's
tile-scoring method used during worldgen to decide which biome wins a tile —
via a generic `BiomeWorker_GetScore.Postfix`. The other 10 types are mod
settings storage (`ChooseBiomeCommonality_Settings`,
`ChooseBiomeCommonality_Mod`) and a settings UI page
(`Page_DoBottomButtons`). **Nothing in this assembly touches `wildAnimals`,
`PawnKindDef`, or `CommonalityOfAnimal` anywhere** — confirmed by reading
every type, not by a string search. This was a naming coincidence: "biome
commonality" (this mod) and "animal commonality within a biome" (this
item's subject) are different mechanics that happen to share a word.
**Definitively ruled out**, not just string-negative this time.

**`EBSGFramework.dll`'s one `wildAnimal`-adjacent hit, checked**: a
case-insensitive re-scan (the prior three passes were case-sensitive, per
this item's own carried-forward note about that gap) found
`get_AllWildAnimals` — a compiler-generated getter name. Confirmed this is
just a call site reading vanilla's own `BiomeDef.AllWildAnimals` PROPERTY
(a read-only computed filter, not a writable field — see the 2026-09-02
pass's own read of that getter) — no literal `wildAnimals` (the private
field name) anywhere in the DLL, and `AllWildAnimals` has no setter to write
through in vanilla regardless. Ruled out: this is a read, not a write.

**`Fortified Features Framework` (`aoba.framework`) now also decompiled and
ruled out.** Live folder confirmed via `jawa/mod_inventory` (workshop
`3498575851`, assembly `Fortified.dll` — NOT `AOBAUtilities.dll`, a
different, unrelated workshop item this pass initially guessed wrong by
name similarity). Its one `[StaticConstructorOnStartup]` class,
`Fortified.RimIgnoreStartupSweep`, calls `RimIgnoreStaging.SweepLeftovers()`
— confirmed by decompile to be filesystem cleanup of a `.fff_ws_staging`
directory the mod uses for its own Workshop-update staging, nothing to do
with defs, biomes, or animals at all. The `RimIgnore*` class family
(`RimIgnorePlan`/`RimIgnoreRule`/`RimIgnoreSpec`/etc.) is the mod's own
fortification-permission rules system, unrelated by subject matter. Ruled
out.

**Both remaining named leads from every prior pass are now exhausted.**
Naming a fresh suspect from here needs either (a) a systematic
`ilspycmd -l c` decompile-and-skim of every one of the ~380 mods
`jawa/startup_types`'s full sweep found owning a `StaticCtor`/`ModSubclass`
row (large — see `Transient/startup_types_full_sweep.json`'s 1539 rows for
the candidate list), or (b) a different instrument entirely: reflecting
over IL method bodies for a `FieldInfo.SetValue`/`Stfld` call targeting a
field typed `List<PawnKindDef>` or similar, which `ilspycmd` can decompile
one type at a time but has no built-in "search every method body in every
loaded assembly for this IL pattern" mode — that tool does not exist yet
and would be a real build, not a quick check.

## criteria
- [ ] **The padding assembly named with the method that does it** — NOT MET. Both
      Harmony's patch table (`jawa/harmony_patches`) and ordinary static-init sites
      (`jawa/startup_types`) have now been swept on the live full mod list; neither
      instrument found a smoking gun. One live thematic lead (`ChooseBiomeCommonality`)
      is unconfirmed pending a decompile. Both instruments exist, are deployed, and
      are proven live — the remaining gap is IL/decompile-level, not tooling.
- [ ] Owner ruling on exclusivity (145 non-cast animals in Desert) and on the 10 excluded
      Anomaly entity records — **owner's call, not FOUNDRY's**, per the item's own framing.
- [ ] `biome_animal_conflicts.py`'s b-side (`race.wildBiomes`) validity — not re-checked this
      pass; follows from naming the mechanism first.
