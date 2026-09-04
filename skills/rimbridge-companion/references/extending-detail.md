# Companion DLL — the lower-level detail

Paths, assembly references and the csproj pattern live in
`skills/rimbridge/references/extending.md`. This file holds what was measured on top.

## Paths

```
source   D:\Luke\dev\Rimworld\src\RimMandrake\bridgetools\JawaBench.BridgeTools\*.cs
csproj   ...\JawaBench.BridgeTools\JawaBench.BridgeTools.csproj      (SDK-style, globs .cs)
build    D:\Luke\dev\Rimworld\src\RimMandrake\bridgetools\build.py
artifact ...\bridgetools\artifacts\BridgeTools\JawaBench\JawaBench.BridgeTools.dll
deployed C:\Program Files (x86)\Steam\steamapps\common\RimWorld\BridgeTools\JawaBench\
```

🔑 The deploy target is a **sibling of `Mods\`**, not inside it, and it never appears in
`ModsConfig.xml`. But `brrainz.rimbridgeserver` **must be active** — the bridge mod is what
scans `BridgeTools\` at startup.

## The GM gate

```xml
<JawaGmTools Condition="'$(JawaGmTools)' == ''">false</JawaGmTools>
<PropertyGroup Condition="'$(JawaGmTools)' == 'true'">
  <DefineConstants>$(DefineConstants);JAWA_GM_TOOLS</DefineConstants>
```
`build.py --gm` sets it. Player-acting tools go inside `#if JAWA_GM_TOOLS`.

## Compile errors that will happen to you

These were all hit in one day and each cost one ~1-minute cycle — cheap, but avoidable:

| error | cause |
|---|---|
| `'CompQuality' has no 'TryGetQuality'` | it is an extension on **`Thing`**, not the comp |
| `Cannot convert 'void' to 'bool'` | `TryRemoveDesignation` returns void |
| `Operator '!' cannot be applied to 'int'` | `TryAddOrTransfer` returns the **count**, not a bool |
| `'PrefabDef' has no 'things'` | `things` is **internal**; use the public `GetThings()` |
| `'WeatherManager' has no 'WindSpeed'` | it does not exist |

📌 The lesson is not the list — it is that **a one-minute build cycle makes the compiler a
cheaper oracle than reading**. Write it, let it fail, fix it. But **only for signatures**;
for *behaviour*, read the source, because the compiler cannot tell you that `DebugSetAge`
silently refuses to go backwards.

## Reflection gotchas

Reflection helpers hide their own `BindingFlags` — the failure looks identical to "field
renamed" or "method doesn't exist."

| symptom | cause | fix |
|---|---|---|
| a field lookup answers "no such field" for a field that demonstrably exists (`TraitDef.commonality`; `AlertsReadout.activeAlerts`) | the shared `FieldOrNull` helper (and `get_defs`' own lookup) searched `Public \| Instance` only — a `private` field reads as absent, not denied | search `NonPublic` too whenever a field is named explicitly (fixed 2026-08-30, FOUNDRY — `get_defs`) |
| `Type.GetMethod` with an exact parameter-type array refuses forever | the method is only reached via C# DEFAULT ARGUMENTS at its call sites (`LayoutUtils.Generate`'s real arities are 5/6/7; a 3-param lookup never matched) | reflect the method's DECLARED arity, never the call-site shape (`jawa/kcsg_place`, FOUNDRY 2026-08-30) |

📌 Check the helper's `BindingFlags` (or arity assumption) before believing its refusal
message — it fails identically to the thing actually being gone.

## Reaching into a third-party mod's own state

Calling straight into a vendored library's static helpers, or expecting your own Harmony
patch to run, both assume you control the whole call graph. You don't.

* **KCSG's leaf utilities are not standalone.** `GetMineableAt`/`RoadOptions` dereference
  `GenOption` statics (`mineables`, `settlementLayout`) with no null guard — those statics
  are primed by KCSG's own GenStep/debug action first. Calling the leaf directly from a new
  tool NREs; prime the statics in the same order the vendored debug action does (FOUNDRY
  2026-08-30).
* **A correct, registered Harmony postfix can still be a no-op.** Vehicle Framework
  prefixes `StunHandler.StunFor` (`Patch_HealthAndStats.StunVehicle`) and skips it for
  every `VehiclePawn` unless `VehicleStatHandler.OverrideStunPatch` is true — a working
  `[Tool]` calling `StunFor` with the right ticks changes nothing. `jawa/harmony_patches`
  is the only way to see an interception living in a third assembly before you spend a
  cycle chasing your own code (FOUNDRY 2026-08-30).

## Harness scripts

| script | does |
|---|---|
| `launch_and_wait.sh` | kill → launch → wait for log truncation → wait for the bridge marker |
| `shoot_planet.py` | world view, close dialogs with retry, screenshot |
| `prove_*.py` | one per area; the acceptance evidence |

⚠️ The debug log has **Auto-open ON** and reopens on any warning, obscuring screenshots.
`shoot_planet.py` closes and re-checks up to 4 times and only shoots a clean frame.
