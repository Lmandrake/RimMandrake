# DEEP_ENTRANCE_BIOMES_SETTING_1 — report (2026-09-18)

Owner ruling (verbatim, 2026-09-18): "The mod itself will be (3) but for the Utinni scenario it's definitely (1)"
— entrance GenSteps read their qualifying-biome list from Mod Settings; default = the three hardcoded today.

## Design

- `LanternDeepsSettings.entranceBiomes : List<string>` is the single qualifying set for BOTH entrance
  GenSteps. Default (`UtinniDefaultEntranceBiomes`) = `BiomeGRimond`, `RUT_NightsideIce`, `RUT_PropaneLake`.
- Persisted with `Scribe_Collections.Look(..., LookMode.Value)`; on `PostLoadInit` a null (pre-key settings
  file) or empty list is reset to the defaults. Verified via RimSage that `ReadModSettings` loads through
  `Scribe_Deep.Look`, so the PostLoadInit pass does reach `ModSettings.ExposeData`.
- Lookup is `IsEntranceBiome(BiomeDef)`: lazy `HashSet<string>`, invalidated by every UI edit / reset, and
  ALSO rebuilt when the backing list's reference or count changed — because the bridge's
  `jawa/mod_settings_field` writes the static field directly (modcheck `set_setting`), bypassing any setter.
- A biome name with no loaded `BiomeDef` is never matched, no error.
- Check order in both `Generate()` preserved: toggle → biome → chance roll (validation.py relies on it).

## Code

Files changed (all under `src/RimUtinni/LanternDeeps/`):
- `Source/LanternDeepsMod.cs` — setting, defaults, `IsEntranceBiome`, `InvalidateEntranceBiomeSet`,
  `ResetEntranceBiomes`, `EntranceBiomesAreUtinniDefault`, ExposeData, UI section.
- `Source/GenStep_ScatterCavePortal.cs` — hardcoded `HashSet` removed; gate is `IsEntranceBiome(map.Biome)`.
- `Source/GenStep_ScatterMineshaftPortal.cs` — same.
- `Source/RimMandrake.Utinni.LanternDeeps.csproj` — added `UnityEngine.TextRenderingModule` reference
  (`Widgets.CheckboxLabeled`/`ButtonText` carry an optional `TextAnchor`; same block Inhabited/Oracle use).
- `validation.py` — DOCSTRING ONLY: the grounding paragraph said "hardcoded 3-biome HashSet", now false;
  rewritten to say `QUALIFYING_BIOMES` is the setting's DEFAULT. No assertion changed — the suite's
  `QUALIFYING_BIOMES` still equals the shipped default, and `set_setting` can't write a List<string>.
- `Assemblies/RimMandrake.Utinni.LanternDeeps.dll` — rebuilt (28,160 bytes).

No `Languages/` folder exists in this mod; labels stay inline literals, matching its convention.

## Build

```
/mnt/c/Users/Mandrake/.dotnet/dotnet.exe build 'D:\Luke\dev\Rimworld\src\RimUtinni\LanternDeeps\Source\RimMandrake.Utinni.LanternDeeps.csproj' -c Release
→ Build succeeded. 0 Warning(s) 0 Error(s)
```
(First attempt failed CS0012 TextAnchor ×3 → csproj reference added → clean.)
DLL byte-check: `entranceBiomes`, `Reset to Utinni defaults`, `IsEntranceBiome`, `ResetEntranceBiomes`
present; `AllowedBiomeDefNames` absent.

Deploy dry run (`deploy_custom_mods.py --mod LanternDeeps`, NOT applied — game running):
```
LanternDeeps     mandrake.rut.lanterndeeps
    +  Defs/SoundDefs/RUT_DeepAmbience.xml
    ~  About/About.xml
    ~  Assemblies/RimMandrake.Utinni.LanternDeeps.dll
    ~  Defs/Weather/RUT_DeepCalm.xml
```
(The SoundDefs/Weather/About lines are other workers' in-flight edits, not this item.)

## Settings UI

Under the existing controls: header "World generation: entrance biomes (affects new maps only)", tiny-font
explainer (worldgen-affecting, defaults, unloaded names ignored, empty list restores defaults on next load —
use the toggles to disable), "N of M loaded biomes selected (Utinni defaults)" line, three buttons
(Reset to Utinni defaults / Select all / Select none), then a `Widgets.BeginScrollView` checklist of every
`DefDatabase<BiomeDef>` entry sorted by label: `Label (defName)`, checked = in list. Existing 5 toggles +
4 sliders untouched.

## Open

- Not deployed, not live-verified: DLL cannot be written while the game runs. Deploy at the next shutdown
  window; the settings screen has not been rendered yet (layout of the scroll region below the listing is
  computed from `Listing_Standard.CurHeight` — eyeball it once).
- "Select none" + save + reload snaps back to the Utinni defaults (per brief: null/empty → defaults). Stated
  in the UI text; the toggles are the intended off-switch.
- validation.py's `biome_gate_on_current_map` assumes the runner's settings carry the default list; a
  non-default `entranceBiomes` in the runner's `Mod_*_LanternDeepsMod.xml` would make that chain wrong.
