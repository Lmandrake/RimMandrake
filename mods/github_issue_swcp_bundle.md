**Repo:** https://github.com/guy1762/guy762-MM-KotORCore → *Issues → New issue*

---

## Title

`SWCP-UnityAssets` bundle is missing from both the Workshop upload and this repo — `SWCP_Core` fails to init materials and aborts RimWorld's post-load queue

---

## Body

### Summary

`SWCP_Core.dll` tries to load an AssetBundle at `<mod>\SWCP-UnityAssets\Materials\StandaloneWindows64\SWCPshaders`, but that folder isn't present in the Steam Workshop download **or** in this repository. The bundle fails to open, `MainBundle` stays uninitialised, and the resulting null material causes a `NullReferenceException` inside RimWorld's post-load action queue — which aborts the remainder of that queue.

### Environment

| | |
|---|---|
| Mod | Star Wars KotOR Resources and Materials (`guy762.MM.KotORCore`), Workshop `3254370945` |
| RimWorld | 1.6.4871 rev591 (Unity 2022.3.35f1) |
| OS / GPU | Windows, NVIDIA RTX 5080 |
| Install | Steam Workshop, ~119 MB on disk |

### Log excerpt

```
[SWCP Core/Tools] Bundle Path: C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3254370945\SWCP-UnityAssets\Materials\StandaloneWindows64\SWCPshaders
Unable to open archive file: C:/Program Files (x86)/Steam/steamapps/workshop/content/294100/3254370945/SWCP-UnityAssets/Materials/StandaloneWindows64/SWCPshaders
Failed to read data for the AssetBundle '...\SWCP-UnityAssets\Materials\StandaloneWindows64\SWCPshaders'.
[SWCP Core/Tools] Failed to load bundle at path: ...\SWCP-UnityAssets\Materials\StandaloneWindows64\SWCPshaders
Could not execute post-long-event action. Exception: System.NullReferenceException: Object reference not set to an instance of an object
  at Verse.BuildableDef.ResolveIcon () [0x00081]
  at Verse.ThingDef.ResolveIcon () [0x00000]
  at Verse.BuildableDef.<PostLoad>b__78_0 () [0x00021]
  at Verse.LongEventHandler.ExecuteToExecuteWhenFinished () [0x0007c]
```

Later in the same load, the consequence is stated explicitly:

```
[SWCP Core/Tools] MainBundle is not initialized, cannot load shader: Assets\Shaders\ZoomShader.shader
```

The bundle load is attempted twice per launch (both times failing).

### What I checked before filing

1. **Clean redownload** — unsubscribed, removed the folder, resubscribed. `SWCP-UnityAssets` still absent. Not a partial Steam download.
2. **This repository** — top level is `1.5`, `1.6`, `About`, `Languages`, `Sounds`, `Textures`, `WeaponTweakData`, `.gitattributes`, `LoadFolders.xml`. No `SWCP-UnityAssets`, and no `.gitignore` that could be excluding it.
3. **Entire mod library** — searched all 1,211 installed mods for any directory matching `*UnityAssets*`. Zero matches, so no sibling/companion mod is supplying it either.
4. `1.6/Assemblies/SWCP_Core.dll` does contain the expected members — `AssetBundle`, `InitMaterials`, `get_MainBundle`, `_lookupMaterials` — so the loader code is present and looking for a bundle that was never shipped.

### Why this is worth fixing beyond the missing shader

The `NullReferenceException` is thrown inside `LongEventHandler.ExecuteToExecuteWhenFinished`. When that throws, **the rest of the queued post-load actions are abandoned**. Any `ResolveIcon` / post-load work scheduled behind this point silently doesn't run, from this mod or any other. The visible symptom is missing materials on KotOR content, but the failure mode is broader and hard for users to attribute.

### Suggested fix

Either:

- **Ship the bundle** — add `SWCP-UnityAssets/Materials/StandaloneWindows64/SWCPshaders` to the Workshop upload and the repo (Git LFS if size is the obstacle); or
- **Fail soft** — have `InitMaterials` null-check the bundle and return early with a single warning, so a missing bundle degrades to "no custom shaders" rather than throwing into RimWorld's post-load queue.

The second is worth doing regardless of the first, since it makes the mod resilient to any future packaging slip.

I'm happy to test a fix or provide the full `Player.log` if useful.
