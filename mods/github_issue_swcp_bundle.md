**STATUS: FILED as issue #7, open.** https://github.com/guy1762/guy762-MM-KotORCore/issues/7
⚠️ **The filed text contains a wrong claim.** See the correction comment drafted at the bottom of this file.

---

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


---

# ⚠️ CORRECTION NEEDED — draft comment for issue #7

**Not posted.** Posting to a third party's public repo is the user's call.

## Why

Both the title and the "Why this is worth fixing beyond the missing shader"
section assert that the `NullReferenceException` **aborts the remainder of
RimWorld's post-load queue**. We verified on 2026-08-10 that this is **false** —
`LongEventHandler.ExecuteToExecuteWhenFinished` wraps each queued action in its
own try/catch and continues. Full evidence in `mods/benign_log_errors.md` §6.

The packaging bug itself is entirely real and the report still stands. Only the
severity argument is wrong, and it is wrong in the direction that overstates the
problem — which is the kind of error worth correcting promptly and unprompted.

## Draft comment

> Correction to my own report, and apologies for the noise.
>
> I claimed the `NullReferenceException` "aborts the remainder of the post-load
> queue". That is wrong, and I should have checked before asserting it.
>
> I disassembled `Verse.LongEventHandler.ExecuteToExecuteWhenFinished` in
> `Assembly-CSharp.dll` (1.6.4871). The method's EH table has a typed
> `catch (System.Exception)` over an 18-byte try region containing a single
> `Action::Invoke`, and the handler's `leave` targets the loop **increment**, not
> the loop exit. The shape is:
>
> ```csharp
> for (int i = 0; i < toExecuteWhenFinished.Count; i++)
>     try { toExecuteWhenFinished[i](); }
>     catch (Exception ex) { Log.Error("Could not execute post-long-event action. Exception: " + ex); }
> ```
>
> So a throwing action costs exactly that action. Other mods' post-load work is
> unaffected. The real impact of the missing bundle is narrower than I described:
> one `BuildableDef.ResolveIcon` failing, plus the shader never loading.
>
> **The packaging issue itself is unchanged** — `SWCP-UnityAssets/Materials/StandaloneWindows64/SWCPshaders`
> is absent from both the Workshop upload and this repo, so `MainBundle` never
> initialises and `Assets\Shaders\ZoomShader.shader` cannot load. The "fail soft"
> suggestion also still stands on its own merits: a null-check in `InitMaterials`
> would turn this into one warning instead of an exception.
>
> Sorry for overstating the blast radius.

## Before posting, also worth deciding

- Whether to add what we learned about scope: the strings in `SWCP_Core.dll`
  suggest the bundle only supplies the **VATS zoom** shader/material
  (`ZoomShader.shader`, `Unlit_ZoomShader.mat`), which would mean the missing
  bundle affects one optional feature rather than all KotOR materials. That is
  **inference from string extraction, not verified**, so it should not go into a
  public issue until confirmed.
