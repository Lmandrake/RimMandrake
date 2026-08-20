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

## Harness scripts

| script | does |
|---|---|
| `launch_and_wait.sh` | kill → launch → wait for log truncation → wait for the bridge marker |
| `shoot_planet.py` | world view, close dialogs with retry, screenshot |
| `prove_*.py` | one per area; the acceptance evidence |

⚠️ The debug log has **Auto-open ON** and reopens on any warning, obscuring screenshots.
`shoot_planet.py` closes and re-checks up to 4 times and only shoots a clean frame.
