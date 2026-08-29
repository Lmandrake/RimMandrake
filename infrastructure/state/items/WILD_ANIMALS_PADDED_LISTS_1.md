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

## criteria
- [ ] **The padding assembly named with the method that does it** — NOT MET. Needs live Harmony
      patch inspection (see above); offline search of the vendored source subset exhausted.
- [ ] Owner ruling on exclusivity (145 non-cast animals in Desert) and on the 10 excluded
      Anomaly entity records — **owner's call, not FOUNDRY's**, per the item's own framing.
- [ ] `biome_animal_conflicts.py`'s b-side (`race.wildBiomes`) validity — not re-checked this
      pass; follows from naming the mechanism first.
