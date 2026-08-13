# RimDefDump — the live def dump (post-patch ground truth)

_Built 2026-08-10. RimWorld 1.6, `net472`. Companion to `src/RimMandrake/Utils/animal_inventory.py`._

**The point:** photograph the def database from inside the running game, after
every mod has loaded and every `PatchOperation` has applied. That is the one
thing an offline `Defs/` scan structurally cannot do.

> `animal_inventory.py` is the **authoring** view — it knows which mod and which
> xpath to patch. RimDefDump is the **verification** view — it knows what
> actually resulted. Neither replaces the other; the value is in the join.

## What it resolves that the offline scan cannot

| Offline limitation | What RimDefDump gives |
|---|---|
| PatchOperation results invisible | the post-patch value itself |
| Mod-vs-mod override winner flagged, not resolved | `modName`/`packageId` of the def that actually won |
| `shortHashCandidate` is a guess | the true `shortHash`, collisions already bumped by the game |
| `statBases` holds only explicitly-declared values | `GetStatValueAbstract` — the value the game actually uses |
| biome×animal reconstructed from two directions, conflicts inferred | `biomeAnimals`, already merged by the engine |
| "is this a weapon?" must be guessed from XML shape | the `is` block — the engine's own computed answer |

### The `is` block — authoritative classification

Every `ThingDef` in the generic dump carries an `is` object holding the engine's
*computed* category properties: `weapon`, `meleeWeapon`, `rangedWeapon`,
`apparel`, `medicine`, `drug`, `stuff`, `ingestible`, `corpse`,
`buildingArtificial`, `plant`, `frame`, `blueprint`, `minifiable`,
`everHaulable`, the coarse engine `category`, and — when the def is a pawn —
`pawn`, `animal`, `humanlike`, `toolUser`, `mechanoid`, `flesh`.

This matters because **none of these is an XML field**. `ThingDef.IsWeapon` is
C# logic. An offline scan can only approximate category membership from shape,
and those approximations disagree with the game at the margins. Without this
block those disagreements surface as phantom `live_only` / `offline_only` rows
that are the classifier's fault rather than the game's — the fastest way to
train someone to ignore a report.

With it, the offline classifier can be **calibrated** against ground truth, and
any residual mismatch is reported as its own status instead of being mistaken
for a content change. Each flag is read defensively: a mod can make a computed
property throw, and a classifier that dies on one bad def is worse than useless,
so a failure is recorded as `<failed:Exception>` rather than propagated.

## It is live-only, and it cannot be otherwise

This mod reads **only** the in-memory `DefDatabase` and `LoadedModManager`. It
never scans `Defs/` or any mod folder. The only filesystem calls are reading the
marker file and writing the output.

That is not just a scoping choice — the engine forecloses the alternative.
**RimWorld 1.6's `Def` has no `fileName` field** (verified against
`Assembly-CSharp.dll`, 2026-08-10): once a def is loaded, the runtime object has
no memory of which XML file it came from. `modContentPack` survives, so the
finest provenance available live is **which mod won**, never which file or
xpath.

So the two-tool split is forced, not arbitrary:

| Question | Answer from |
|---|---|
| Which mod won this def? | live dump |
| Which *file* and *xpath* do I patch? | offline scan only |
| What did the patch actually do? | the diff of the two |

`manifest.json` records each mod's `RootDir` and load order, so you can go
live → mod → disk. Getting from there to the specific file still needs the
offline scan. This is why `animal_inventory.py` is not superseded by this tool
and should not be retired.

## Safety posture

- **Inert by default.** With no marker file it logs one line and returns. Game
  loads on the full stack take ~23 minutes and are often being used to debug
  something else, so this must never add cost unless asked.
- **No Harmony patches, no defs, no gameplay behaviour.** It only reads the def
  database and writes files.
- **Cannot break a load.** The whole run is wrapped; any exception is logged as
  an error and swallowed.

## Enabling it

1. Copy the mod into the game (not done automatically — see *Staging* below):
   ```
   robocopy "D:\Luke\dev\Rimworld\src\RimMandrake\RimDefDump" ^
            "C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\RimDefDump" /E
   ```
2. Enable `mandrake.rimdefdump` in the mod list. It has no dependencies and no
   load-order requirements — it only reads, so anywhere late is fine.
3. Create the marker file to arm it:
   ```
   %USERPROFILE%\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\DefDump\dump_request.txt
   ```
   Contents select the scope:

   | Contents | Output | Cost |
   |---|---|---|
   | *(empty)* or `animals` | `animals.json` + `manifest.json` | seconds |
   | `all` | the above plus `defs/<DefType>.json` for every def type | slow, large |

4. Load the game. Watch for `[RimDefDump]` lines in `Player.log`.

The marker is **not** consumed — it dumps on every load until you delete it.

## Outputs

Written to `…\RimWorld by Ludeon Studios\DefDump\`.

| File | Contents |
|---|---|
| `manifest.json` | game version, the full mod list **in load order** with packageIds, per-type def counts, timings |
| `animals.json` | every `ThingDef` with a `<race>` — resolved stats, full reflected `RaceProperties`, its `PawnKindDef`s, plus the merged `biomeAnimals` pairs |
| `defs/<DefType>.json` | (mode `all`) every def of that type, fully reflected |

`manifest.json` matters more than it looks: without the mod list in load order,
a dump is unattributable a week later. These are snapshots of a **mod set**, not
of RimWorld.

## How the reflector survives the live object graph

The live graph is hostile in four specific ways. Each has a rule, and each rule
has a test:

1. **It is cyclic.** Def A → Def B → Def A. Rule: only the root def is expanded;
   any nested `Def` collapses to its `defName` string. Plain-object cycles are
   caught by reference identity and cut with `<cycle:Type>`.
2. **It reaches into Unity.** Textures and Materials are huge and can throw.
   Rule: anything in the `UnityEngine` namespace is skipped by type, as are
   delegates and `System.Reflection` types.
3. **Reads can throw.** Rule: every field read and write is wrapped; a failure
   records `<read-failed:Exception>` rather than losing the def.
4. **Sequences can be unbounded or lazy.** Rule: hard cap of 4096 items, and
   truncation is always marked `<truncated>` — never silent.

Depth is capped at 6 (`<maxdepth:Type>` when hit). `System.Type` fields become
their full name. Dictionaries are special-cased to key/value pairs, because
`KeyValuePair` exposes Key/Value as *properties*, and the generic field walk
would otherwise emit `{}` — `race.wildBiomes` is exactly that shape.

## Building

Requires only the user-local SDK at `%USERPROFILE%\.dotnet` (installed
2026-08-10; no admin, no Visual Studio). Reference assemblies for `net472` come
from the `Microsoft.NETFramework.ReferenceAssemblies` NuGet package, since there
is no targeting pack on this machine.

```
"%USERPROFILE%\.dotnet\dotnet.exe" build Source/RimDefDump.csproj -c Release
```

Output goes to `1.6/Assemblies/RimDefDump.dll`. The game's own assemblies are
referenced with `Private=false` so nothing but our DLL is ever copied into the
mod folder.

## Tests

The mod itself can only be exercised by paying a full game load, so the two
risky components are tested standalone against the real source files:

- **`JsonWriter`** — 21 checks across both indent modes (nested members, empty
  containers, hostile strings incl. lone surrogates and control chars,
  non-finite doubles, deep nesting, value round-trip). Every document is
  validated with `System.Text.Json`.
- **`DefReflector`** — 31 checks against stub types reproducing each hostile
  shape above: reference cycles, Def-keyed dictionaries, Unity types, throwing
  enumerables, oversized sequences, depth caps, plus the `is` block (flags
  accurate, absent for non-ThingDefs, pawn flags only when `race` is present,
  and a throwing computed property contained rather than fatal).

Both suites live in the session scratchpad and compile the mod's real source
files directly, so they cannot drift from what ships.

**Not yet verified in-game.** Everything above is verified by compilation and
standalone tests; the first real load is still pending.

## Staging

The mod is deliberately **not** installed into the RimWorld `Mods` folder. The
mod list is being stabilised in a parallel effort, and adding an entry to it —
even an inactive one — is that effort's call to make, not this tool's.
