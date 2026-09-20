# BRIDGE_PAWN_SPAWN_CRASHES_VEF_1 — `GenSpawn`-based bridge spawns NPE on pawns

# 🔴 RE-MEASURED 2026-09-20 (BENCH, live) — THE WORKFLOW IS NOT BLOCKED

**The title claim "universally" was WRONG, and it is the most expensive kind of
wrong: it says a standard workflow is dead when a working route was sitting next
to it the whole time.** Corrected rather than annotated.

`jawa/spawn_pawn` **WORKS**. MEASURED live on a VEF-loaded game (the 16-mod
`xenotypes` tier includes `oskarpotocki.vanillafactionsexpanded.core`), same map,
same session, same defName, back-to-back calls:

| tool | pawn (`Chicken`) | non-pawn |
|---|---|---|
| `rimworld/spawn_thing` | 🔴 **NPE** | ✅ |
| `jawa/spawn_batch` | 🔴 **NPE** | ✅ (`ChunkSlagSteel`) |
| `jawa/spawn_pawn` | ✅ **success**, pawn count 81 → 82 | n/a |

🔑 **65 pawns were spawned through `jawa/spawn_pawn` earlier in the same session**
(13 xenotypes × grids, for `XENOTYPE_CANON_CORRECTION_1`) with zero failures. The
"spawn many, screenshot, observe" method of `rimworld-debug-testing` is **usable
today** — it just has to call `jawa/spawn_pawn`.

⇒ **The common factor is `GenSpawn.Spawn` on a `ThingMaker`-made Thing.** Both
failing tools construct the Thing and hand it to `GenSpawn`; a Pawn built that way
never ran `PawnGenerator`, so its sub-trackers are null and VEF's `SpawnSetup`
postfixes dereference one. `jawa/spawn_pawn` generates a real pawn instead, which
is why it survives. (Construction detail confirmed from our own source — see below.)

## ✅ RESOLVED: `jawa/spawn_batch`'s parameter shape

The item recorded this as *"genuinely unknown, not a negative result"*. It is known
now. **`ops` is a STRING, not a list** — `'Def:x,z[,count]'` separated by `;` or
newlines, e.g. `'Chicken:124,100,1'`. The earlier `IConvertible` cast error came
from passing `[{x,z}]`. And with the right shape it **still NPEs on a pawn**, so it
is not an alternative route.

## ⚠️ UNMEASURABLE: VEF's own internals

RimSage indexes **core game assemblies only** — `RimWorld`, `Verse`, and the libs
bundled with the engine. There is no `VEF`/`OskarPotocki` namespace in its index, so
the bodies of `CompShieldField.SpawnSetup_Patch.Postfix` and
`PhasingPatches.CheckPhasing` **cannot be read from this machine** and the exact
member that is null is UNKNOWN. That does not block the fix: VEF's postfix is the
victim, not the cause — it is reading a pawn that our own call built wrong.
⛔ Do not write a guess at VEF's body into this item.



## what is wrong

**MEASURED 2026-09-20, this session.** `rimworld/spawn_thing` and the
`Actions\Spawn Pawn...\<Kind>` debug action both throw the same
`NullReferenceException` for **any pawn defName**, on the owner's real,
live full modlist (618 mods) — not just a reduced test tier. Confirmed against
`Muffalo`, `Thrumbo`, vanilla `Chicken`, and our own `RSW_Sketto`; all four
fail identically. Non-pawn Things (`Steel`, `Gun_Revolver`) spawn fine via the
same call, same map, same session — this is pawn-specific, not a general
bridge outage.

Full trace (captured once, before the server's own dedup collapsed later
occurrences to `[Ref D3D588D] Duplicate stacktrace, see ref for original` —
same ref ID recurred across a 14-mod test tier AND the full 618-mod list, so
it is one root cause, not a modlist-size artifact):

```
System.NullReferenceException: Object reference not set to an instance of an object
  at Verse.Pawn.SpawnSetup (Verse.Map map, System.Boolean respawningAfterLoad)
    - POSTFIX OskarPotocki.VEF: Void VEF.Apparels.CompShieldField+SpawnSetup_Patch:Postfix(Pawn __instance)
    - POSTFIX OskarPotocki.VEF: Void VEF.Hediffs.PhasingPatches:CheckPhasing(Pawn __instance)
  at Verse.GenSpawn.Spawn (Verse.Thing newThing, Verse.IntVec3 loc, Verse.Map map, Verse.Rot4 rot, Verse.WipeMode wipeMode, System.Boolean respawningAfterLoad, System.Boolean forbidLeavings)
  at Verse.GenSpawn.Spawn (Verse.Thing newThing, Verse.IntVec3 loc, Verse.Map map, Verse.WipeMode wipeMode)
  at RimBridgeServer.LifecycleCapabilityModule.SpawnThing (System.String defName, System.Int32 x, System.Int32 z, System.Int32 stackCount)
```

## why it matters

Colonists and wildlife spawned as part of normal map/scenario generation are
unaffected (31-38 pawns present on a fresh quicktest map, every time) — the
crash is specific to a pawn spawned via `GenSpawn.Spawn` **after** the map is
already active, whether triggered by the bridge or (untested, ask the owner)
a manual dev-mode click. If it also fires from the dev-mode UI directly, this
is a live-game regression, not just a bridge-testing gap. Either way, it
currently blocks a large fraction of this project's standard workflow: the
`rimworld-debug-testing` skill's whole "spawn many, screenshot, observe"
method depends on exactly the call that is broken.

## Watch out

- Two other things were RULED OUT this session, not just suspected:
  removing `sarg.alphaanimals` (VEF's own pull-in dependency) from the
  modlist to route around this does NOT fix it cleanly — it breaks
  `RimWorld.ScenPart_StartingAnimal.PossibleAnimals` instead (a different
  NullReferenceException), implying some of our own SWBestiary defs lean on
  an Alpha-Animals-sourced parent/field that goes null without it. Do not
  re-attempt that removal as a "fix" without first fixing that dependency.
- The failure is **pawn-specific**, confirmed by a same-session A/B
  (`Steel`/`Gun_Revolver` spawn clean, `Muffalo`/`Chicken`/`RSW_Sketto` all
  NPE) — do not reopen "is it the bridge at all" as a question.
- `jawa/spawn_batch` was tried as a possible different code path but its
  `ops` parameter shape was not resolved this session (an `IConvertible`
  cast error on a naive `[{x,z}]` list) — untested whether it hits the same
  crash, genuinely unknown, not a negative result.

## verify

`rimworld/spawn_thing` with `defName: "Chicken"` on any live map returns
`success: true` and the pawn appears (`jawa/list_pawns` count increases),
with no `NullReferenceException` in the response.

## criteria

Any wild animal or humanlike PawnKindDef can be spawned via the bridge on the
owner's real modlist without crashing — the standard debug-testing method is
usable again.

---

## 🔴 NEW, WORSE FINDING 2026-09-20 (FOUNDRY) — this is a full process crash, and it is NOT the VEF postfix

Took the bridge (BENCH's hold was 88 min idle, past the 45-min staleness
threshold) to re-verify the `jawa/spawn_pawn` workaround for
`DRUM_LURE_PREDATOR_BUILD_1`/`PORTED_BEAST_MECHANICS_REBUILD_1`. Two calls in:
`rimbridge/get_bridge_status` and `rimworld/get_game_info` both succeeded
(`status: "game_loaded"`, `mapCount: 1`, 3 pawns) — the third call
(`jawa/get_defs`) got `ConnectionRefusedError`. **`tasklist` confirms
`RimWorldWin64.exe` is no longer running.** The game crashed to nothing (no
window, no process) sometime in the ~60 seconds between those calls.

`Player.log`'s last 48 lines, in order, on a small test-tier map
(`brrainz.rimbridgeserver`, `Mlie.StarWarsAnimalCollection`,
`OskarPotocki.VanillaFactionsExpanded.Core`, `sarg.alphaanimals`,
`mandrake.rsw.swbestiary` all confirmed active):

1. **Two NPEs during ordinary map generation** (both logged as recovered
   GenStep errors, not fatal on their own):
   - `RimWorld.ScenPart_StartingAnimal+<>c__DisplayClass8_0.<PossibleAnimals>b__0` —
     the SAME method the item's "Watch out" section already names, but this
     time `sarg.alphaanimals` **was present and active**, and it NPE'd anyway.
     That contradicts this item's existing assumption that keeping AlphaAnimals
     avoids this specific NPE — record as an open contradiction, not resolved.
   - `RimWorld.BiomeDef.CommonalityOfAnimal`, via AlphaAnimals' own postfix
     `MultiplyAlphaAnimalCommonality`, during `GenStep_Animals` /
     `WildAnimalSpawner.DesiredAnimalDensity`.
2. **The actual crash**: immediately after map gen finished, dev mode's
   auto-open-palette post-long-event action fired
   (`Verse.DebugWindowsOpener.TryOpenOrClosePalette` →
   `LudeonTK.Dialog_DevPalette..ctor` → `EnsureAllNodesValid` →
   `Dialog_Debug.GetNode` → `DebugActionNode.TrySetupChildren` →
   `Verse.DebugToolsSpawning.SpawnPawn()` → **`GetCategoryForPawnKind(kindDef)`
   throws `NullReferenceException`**), logged as `Could not execute
   post-long-event action`. **12 lines later the log simply stops — no
   shutdown message, no exit line, nothing.** `tasklist` says the process is
   gone.

🔑 **Read the method** (`mcp__rimsage__read_csharp_symbol DebugToolsSpawning
GetCategoryForPawnKind`, `Verse/DebugToolsSpawning.cs:174-197` — this is a
CORE game class, not VEF, so RimSage CAN read it):

```csharp
public static string GetCategoryForPawnKind(PawnKindDef kindDef)
{
    if (!kindDef.overrideDebugActionCategory.NullOrEmpty()) return kindDef.overrideDebugActionCategory;
    if (kindDef.RaceProps.Humanlike) return "Humanlike";   // <- NPEs here if kindDef.race is null
    ...
}
```

`kindDef.RaceProps` is `kindDef.race.race` — this line throws **if and only if
some live `PawnKindDef`'s `<race>` field is null**, i.e. it names a `ThingDef`
that failed to resolve. This method runs once per `PawnKindDef` while building
the Spawn-Pawn debug-menu category tree, which happens **automatically**
whenever dev mode's auto-palette-open fires after a map loads — **not only on
a manual click, and not only via the bridge.** This is a plausible SEPARATE
root cause from the VEF `CompShieldField.SpawnSetup` postfix documented above —
both may be real, on different code paths (`GenSpawn.Spawn` on a raw Thing vs.
enumerating the whole `DefDatabase<PawnKindDef>` to build a menu).

⚠️ **I do NOT know which `PawnKindDef` has the null `race`.** I attempted a
quick regex sweep of `src/**/*.xml` for `PawnKindDef.race` values with no
matching `ThingDef` defName in this repo, and it returned **133 hits, almost
entirely false positives** (verified by direct grep: `RSW_DW_Race_JDSCIS_B1_
Battle_Droid` IS defined, at `src/RimStarWars/Droidworks/Defs/Races_JDS.xml:38`
— my regex simply failed to pair `<ThingDef>`/`<defName>` blocks correctly
across that file). **Do not trust that sweep or repeat it as written** — this
needs the live def dump (`jawa/get_defs` reflection on `PawnKindDef.race`
across the SAME small mod list that crashed, once the game is back up on a
tier where a crash is affordable to retry) or a proper XML-tree parse
(`xml.etree.ElementTree`, not regex, per this project's own standing
`measuring-large-artifacts` rule), not a hand-rolled regex against 1848 defs.
A donor mod's own `PawnKindDef` (`Mlie.StarWarsAnimalCollection`,
`sarg.alphaanimals`) is just as plausible a source as anything in `src/`.

⛔ **Do not blindly relaunch the game to "just try it again."** Dev mode's
auto-palette-open means the SAME crash will very likely refire on the very
next map generation with the same mod list, wasting a load. Next steps, in
order: (1) find the actual null-race `PawnKindDef` via a live def-dump query
or a real XML parse, not a regex; (2) decide fix-or-guard once identified;
(3) only then relaunch to verify. Turning off dev mode's auto-palette-open
(if that setting exists) would sidestep the crash but not the underlying bug,
and would also defeat the debug-testing workflow this item exists to unblock.

Bridge released — nothing to hold, the game process is gone.

## ✅ ROOT CAUSE FOUND 2026-09-20 (FOUNDRY, offline) — the null-race PawnKindDefs, named

**Instrument used, in order:** (1) `Player.log`'s "Initializing new game with
mods:" block (lines 524-536) gave the EXACT 12-packageId list active at crash
time — `brrainz.harmony`, `Ludeon.RimWorld` + 5 DLCs, `brrainz.rimbridgeserver`,
`Mlie.StarWarsAnimalCollection`, `OskarPotocki.VanillaFactionsExpanded.Core`,
`sarg.alphaanimals`, `mandrake.rsw.swbestiary` — **12, not 14**: this predates
`modset_builder.py`'s current `beastmechanics` tier (14 mods), which as of
*this same session* also pulls in `oskarpotocki.vfe.insectoid2` and
`mandrake.rm.creaturebehaviors` as required transitive deps that the 12-mod
crash list did NOT have. (2) Built a scratch `ModsConfig.xml` with exactly
those 12 packageIds and resolved it with this project's own
`rimworld_loadset.build_load_set()` (honors `LoadFolders.xml` conditionals —
not a bare directory walk). (3) Parsed every `Defs/*.xml` across the resolved
mod folders with `xml.etree.ElementTree`, resolving `PawnKindDef` `ParentName`
chains correctly (a first pass indexed parents by `<defName>` and produced ~30
false "parent not found" hits on plain vanilla Core defs like `Grenadier_*` /
`Tribal_*` — **RimWorld's `ParentName` targets a node's `Name="..."`
ATTRIBUTE, not its `<defName>` element**; fixed by indexing on `Name` first).
Checked all 817 non-abstract leaf `PawnKindDef`s: **0 unresolved on base XML
alone.**

**The real defect is not in base XML — it's a comp `Class` that can't
resolve.** Grepped all `Defs/*.xml` under `mandrake.rsw.swbestiary` for
`Class="RimMandrake.CreatureBehaviors.*"` with no `MayRequire` guard. Five
`ThingDef`s carry one:

| ThingDef/PawnKindDef defName | file | unguarded comp Class |
|---|---|---|
| `RSW_Drazzik` | `Defs/ThingDefs_Races/RSW_Drazzik.xml:158` | `RM_CompProperties_DrumLure` |
| `RSW_WraidAlpha` | `Defs/ThingDefs_Races/RSW_WraidAlpha.xml:151` | `RM_CompProperties_HeatBurstPredator` |
| `RSW_BloodropMoth` | `Defs/BiomesTeamPort/ThingDefs_Races/RSW_BiomesTeamPort_Races.xml:2948` | `RM_CompProperties_FluidSacs` |
| `RSW_FacetMothLarvae` | same file:8119-8128 | `RM_CompProperties_ProximityPsychicStun` (+3 more) |
| `RSW_BovineBeetle` | same file:9755 | `RM_CompProperties_Grappler` |

`mandrake.rm.creaturebehaviors` (the mod supplying every `RM_CompProperties_*`
class above) was declared only under SWBestiary's `<loadAfter>`, never
`<modDependencies>` — an ordering hint, not a requirement. On the 12-mod crash
list that mod was **absent**, so RimWorld's XML deserializer hit an
unresolvable `Class` attribute on each of the 5 `ThingDef`s above and — per
this project's own standing fact ("a missing comp TYPE discards the whole def
silently") — **discarded all 5 `ThingDef`s outright**, silently, no fatal
error. Their sibling `PawnKindDef`s (same 5 defNames, each with a plain
`<race>RSW_X</race>` pointing at its own now-nonexistent `ThingDef`) loaded
fine on their own and registered in `DefDatabase<PawnKindDef>` with an
**unresolvable cross-reference** — which is exactly `kindDef.race == null`,
which is exactly what `GetCategoryForPawnKind` dereferences
(`kindDef.RaceProps` = `kindDef.race.race`) while building the Spawn-Pawn
debug-menu category tree over **every** `PawnKindDef`, which is why it fires
on map load via dev mode's auto-palette-open regardless of which pawn a human
or the bridge would have tried to spawn.

⛔ Not VEF, not the bridge, not `GenSpawn` — a plain silently-discarded-def
cross-reference bug in our own mod's dependency declaration, hitting only
reduced test tiers (the owner's real 618-mod list has always carried
`mandrake.rm.creaturebehaviors` active, so this never bit live play).

## ✅ ALREADY FIXED — by a different session, 6 minutes after this crash

`git log` on `src/RimStarWars/SWBestiary/About/About.xml` shows commit
`3bb3e6966` ("SWBestiary: two hard dependencies were invisible to dependency
closure"), timestamped **2026-09-20 15:52:55**, six minutes after
`Player.log`'s last write (15:46:33, the crash). It promotes
`mandrake.rm.creaturebehaviors` from `<loadAfter>` to `<modDependencies>` and
adds `OskarPotocki.VFE.Insectoid2` (a second, unrelated silent-failure gap the
same commit found: SWBestiary's `RSW_Cindermite` texPath binds to art that
ships only inside that mod). **Deployed copy
(`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\SWBestiary\About\About.xml`)
is byte-identical to the repo copy — already deployed, not just committed.**
This investigation made no code changes; the fix already existed and needed
no rework, only confirmation that it addresses this item's actual root cause
(it does — `close_over()` on the 14-mod `beastmechanics` tier now correctly
pulls in both former gaps, verified via `modset_builder.py --tier
beastmechanics` this session).

## ⚠️ still open

- **Not yet live-reverified.** Nobody has relaunched the game on this or any
  tier since the crash. The `About.xml` dependency fix should prevent the
  5-def discard on any FUTURE tier build (closure now walks
  `modDependencies` and includes `mandrake.rm.creaturebehaviors` +
  `oskarpotocki.vfe.insectoid2`), but "should" is not "confirmed" — bridge
  work for later, per this item's own standing rule.
- **The ORIGINAL (non-"worse") finding above — `GenSpawn.Spawn` NPE'ing in
  VEF's `CompShieldField.SpawnSetup_Patch`/`PhasingPatches` postfixes on a
  `ThingMaker`-built `Pawn` — is UNRELATED and UNRESOLVED.** That is a
  different code path (`rimworld/spawn_thing`/`jawa/spawn_batch` building a
  raw Thing and handing it to `GenSpawn`, vs. this section's whole-
  `DefDatabase<PawnKindDef>` enumeration for the debug-menu category tree).
  Fixing today's null-race defect does not touch it. `jawa/spawn_pawn` remains
  the correct workaround for that one.
- Do not close this item on this finding alone.
