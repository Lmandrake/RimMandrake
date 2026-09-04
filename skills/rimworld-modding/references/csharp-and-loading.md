# C#, Harmony, and how RimWorld loads a mod

Read this before writing any C#, and whenever a mod "does nothing" despite
appearing to load. Most of that category is a constructor signature, a load-order
problem, or a `LoadFolders.xml` that quietly excluded the folder you're editing.

**Contents**
1. Mod folder anatomy
2. About.xml — and why `modDependencies` does not order anything
3. LoadFolders.xml
4. Entry points and their required constructors
5. Harmony
6. Building
7. Failure shapes and what they actually mean

---

## 1. Mod folder anatomy

```
MyMod/
├── About/
│   ├── About.xml
│   ├── Preview.png          (optional, 640×360-ish)
│   └── PublishedFileId.txt  (Steam only; do not create by hand)
├── 1.6/
│   ├── Assemblies/MyMod.dll
│   ├── Defs/
│   └── Patches/
├── Languages/
├── Textures/
└── LoadFolders.xml          (optional)
```

Without `LoadFolders.xml`, RimWorld loads the folder matching the running
version (`1.6/`) plus the mod root. `Defs/`, `Patches/`, `Assemblies/`,
`Textures/`, `Sounds/`, `Languages/` and `Patches/` are all discovered by name —
subfolder structure beneath them is free, so organise by content, not by rule.

A pure-XML patch mod needs only `About/About.xml` and `Patches/*.xml`.

---

## 2. About.xml — and the ordering trap

```xml
<ModMetaData>
  <packageId>yourname.modname</packageId>   <!-- lowercase, unique, immutable -->
  <name>My Mod</name>
  <author>You</author>
  <supportedVersions><li>1.6</li></supportedVersions>
  <description>What it does.</description>

  <modDependencies>
    <li>
      <packageId>brrainz.harmony</packageId>
      <displayName>Harmony</displayName>
      <steamWorkshopUrl>steam://url/CommunityFilePage/2009463077</steamWorkshopUrl>
    </li>
  </modDependencies>

  <loadAfter><li>brrainz.harmony</li></loadAfter>
  <loadBefore>...</loadBefore>
  <incompatibleWith>...</incompatibleWith>
</ModMetaData>
```

**`modDependencies` asserts presence. `loadAfter` asserts order. They are
independent, and this catches experienced authors.** A mod can declare another as
a hard dependency, be sorted anywhere relative to it, and blow up at startup
with a `ReflectionTypeLoadException` naming types from its own dependency —
because the dependency's assembly hadn't been loaded when the CLR tried to
resolve them.

Two things follow. When you author: always add `loadAfter` alongside every
`modDependency` whose *types* you reference. When you diagnose: a
`TypeLoadException` or `ReflectionTypeLoadException` pointing at a mod that is
demonstrably installed is a load-order report, not a corruption report. Fix it in
the sorter (RimSort user rules, or `loadAfter` in a local copy) rather than
editing anyone's assembly.

`packageId` is the identity used by `MayRequire`, `FindMod`, dependencies and
save files. Changing it after release orphans every reference to the mod.

---

## 3. LoadFolders.xml

```xml
<loadFolders>
  <v1.6>
    <li>/</li>
    <li IfModActive="ludeon.rimworld.odyssey">Odyssey</li>
    <li IfModNotActive="someone.othermod">NoCompat</li>
  </v1.6>
</loadFolders>
```

The rule that surprises people: **once this file exists, it fully replaces the
default resolution.** If you don't list `<li>/</li>`, the mod root is not loaded,
and content you can plainly see in the folder is simply never read. When a def
you *know* exists doesn't resolve, check this file before checking anything else.

Paths are relative to the mod root and load in the listed order, so later entries
patch over earlier ones.

---

## 4. Entry points and their required constructors

Every one of these has a signature RimWorld reflects for. Get it wrong and the
object is never constructed — usually with no crash, just absence.

```csharp
// Settings / lifecycle. Needed only if you have mod settings or a settings UI.
public class MyMod : Mod {
    public MyMod(ModContentPack content) : base(content) { }
}

// Runs once at startup, after all defs are loaded.
[StaticConstructorOnStartup]
public static class Startup {
    static Startup() { /* ... */ }
}

// Persists with the save, ticks globally.
public class MyGameComp : GameComponent {
    public MyGameComp(Game game) { }        // <-- public, takes Game. Mandatory.
    public override void GameComponentTick() { }
    public override void ExposeData() { }
}

public class MyWorldComp : WorldComponent {
    public MyWorldComp(World world) : base(world) { }
}

public class MyMapComp : MapComponent {
    public MyMapComp(Map map) : base(map) { }
}
```

**Why the `GameComponent(Game game)` rule deserves special care:**
`Game.FillComponents` instantiates by reflection and throws
`MissingMethodException: Constructor on type '...' not found`. The exception is
logged and swallowed — the game proceeds, the component doesn't exist, and its
`GameComponentTick` never runs. If that component was enforcing a consequence
(a delayed check, a decay, a detection roll), the *feature* still appears to
work while quietly having no downside. That is worse than a crash, and it is
worth a deliberate look whenever a mod's costs seem suspiciously absent.

Components are also the safest place for anything that must be per-save: they
serialise through `ExposeData` and travel with the save file. Static fields do
not, and a static that survives a save/load boundary is a bug waiting for a
second colony.

### Two more silent-absence traps, this time on `Building`

**`BuildingBase` never sets `tickerType`, so it defaults to `TickerType.Never`.**
Any custom `Building` whose mechanic lives in `Tick()` or `CompTick()` is
**silently dead** — no error, comps present, fields correct, nothing ever runs.
Measured: a pit trap's mass-sum trigger did not fire across 200 ticks with an
immobilised pawn standing on it. Add `<tickerType>Normal</tickerType>` (or
`Rare`/`Long` if the mechanic can tolerate it) to the def, and prove the fix by
testing the real tick path over real ticks — not by a forced debug call, which
proves only that the method itself is reachable.

**To make a `Thing` re-run its own `Print()`, dirty `MapMeshFlagDefOf.Things`**
(what `Verse/Thing.cs DirtyMapMesh` uses). `MapMeshFlagDefOf.Buildings` dirties
the linked/buildings mesh layers instead, so the old print stays on screen
**forever, with no error** — a terrain-mimic cover looked completely
unimplemented because of one wrong flag. The two `MapMeshFlagDef`s are not
interchangeable even though both sound like "redraw this building."

---

## 5. Harmony

```csharp
[StaticConstructorOnStartup]
public static class HarmonyInit {
    static HarmonyInit() {
        new Harmony("yourname.modname").PatchAll();
    }
}

[HarmonyPatch(typeof(Pawn), nameof(Pawn.Tick))]
public static class Pawn_Tick_Patch {
    static void Postfix(Pawn __instance) { }
}
```

Patch types, in order of how much you should want to use them:

- **Postfix** — runs after; can read/modify `__result`. Composes with other mods'
  postfixes. Reach for this first, essentially always.
- **Prefix** — runs before; returning `false` skips the original method entirely.
  Powerful and antisocial: any other mod's patch on that method is skipped too.
  Use only when you must prevent the original, and say so in a comment.
- **Transpiler** — rewrites IL. Precise, and the most fragile thing in the
  ecosystem: it breaks on any game update that shifts the instructions it
  matches. Last resort, and pin your matching to distinctive operands rather
  than offsets.
- **Finalizer** — runs even when the original throws. Use to contain exceptions
  from someone else's code.

Useful injected parameters: `__instance`, `__result`, `___privateField` (three
underscores), `__state` (Prefix→Postfix handoff).

Prefer depending on the Harmony mod (`brrainz.harmony`) over shipping
`0Harmony.dll`, so every mod shares one instance and version conflicts don't
arise. Declare it in both `modDependencies` and `loadAfter` (see §2).

---

## 6. Building

- Target **.NET Framework 4.7.2** for RimWorld 1.4–1.6.
- Reference `Assembly-CSharp.dll` and the `UnityEngine.*` DLLs from
  `RimWorld/RimWorldWin64_Data/Managed/`.
- Set **Copy Local = false** on every game/Unity reference. Shipping
  `Assembly-CSharp.dll` inside your mod loads a second, stale copy of the entire
  game's types and produces failures that look like anything but their cause.
- Output the DLL to `<ModName>/1.6/Assemblies/`.
- Bump the assembly name when the mod is renamed; two loaded assemblies with the
  same name is its own confusing class of failure.

Decompile with dnSpy or ILSpy against that same `Assembly-CSharp.dll` when you
need to know what a method actually does. Reading the real IL is the C# analogue
of reading the real def, and it is equally non-optional.

---

## 7. Failure shapes and what they actually mean

| Log shape | Usual meaning |
|---|---|
| `Error in static constructor of X` | The mod is **dead** — nothing in it ran. Highest-priority finding in any log. |
| `ReflectionTypeLoadException` naming another mod's types | Load order (§2), not corruption. |
| `MissingMethodException: Constructor on type ... not found` | Entry-point signature (§4). Feature silently absent. |
| `Could not execute post-long-event action` + exception inside `LongEventHandler.ExecuteToExecuteWhenFinished` | **One queued action failed; the queue continues.** Verified from IL 2026-08-10 — per-action try/catch, the handler's `leave` targets the loop increment. Cost is that one action (usually one def's `ResolveIcon`). The *only* abort path is an NRE in the DeepProfiler block outside the try, which also bricks the queue behind "Already executing." |
| `AmbiguousMatchException` in a Harmony patch | The target method gained an overload in a game/mod update. The patcher is version-drifted. |
| Harmony patch applies but has no effect | Another mod's Prefix is returning `false` on the same method. |
| `Could not find type named X` in a def | The assembly didn't load, or the def references a class from a mod that isn't present. |

The pattern worth carrying between sessions: in a large stack, hard breaks
concentrate in **mods that reflect over other mods' types at startup** — patchers,
compatibility layers, indexers. They run early, they assume a shape, and the
shape changed. Grep for `static constructor` first, every time.
