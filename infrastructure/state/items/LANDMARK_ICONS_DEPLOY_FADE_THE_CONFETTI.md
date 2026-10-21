# LANDMARK_ICONS_DEPLOY_FADE_THE_CONFETTI

`LANDMARK_ICONS_DEPLOY_FADE_THE_CONFETTI` — built and published at caba4437a, not deployed; NEXT: with the game DOWN, run `python3 src/RimMandrake/Utils/deploy_custom_mods.py --compose biomes` and then the same with `--apply` (the RimMandrake.Biomes DLL changed; can ride the consolidated Biomes deploy with HILL_DECALS_VERIFY_NO_MORE_COOKIE_CUTTERS), load the Ash'karr start, and screenshot the Rust Cathedral at the zoom of `D:\ClaudeWork\rimmandrake\scratch\live5\V_rust_stipple.png`, then once more zoomed in close.

Owner by card, 2026-10-20: "Fade and shrink icons" (a look-only change; world data untouched; undoable). The decision was made under `LANDMARK_ICONS_DECIDE_THE_REAL_SPECKLE`.

## What was built

- `src/RimMandrake/BiomesShell/Source/RM_WorldLandmarks.cs`.
  - Opacity uses a postfix on the `WorldDrawLayerBase.Alpha` getter. It applies to `WorldDrawLayer_Landmarks` only. Vanilla `Render` already multiplies the material alpha by `Alpha` through a MaterialPropertyBlock.
  - Size: each landmark quad shrinks about its own centre. The vertices are captured after vanilla's `Regenerate`. The mesh is rewritten only when the scale moves by 0.05.
  - Both ease back to vanilla as the camera zooms in, between `AltitudePercent` 0.20 (fully soft) and 0.05 (vanilla).
- Mod Settings in Baroque Biomes, all marked [now]:
  - "Planet: soft landmark icons" (default on)
  - size, default 60%
  - opacity, default 55%
  - "Full-size icons when zoomed in close" (default on)
- Turning the setting off restores vanilla at once. Nothing redraws and no landmark data changes.
- Selftest: `src/RimMandrake/Utils/selftest_world_landmarks.py` (7/7). The settings screens selftest still passes (846/846).
- Offline preview: `D:\ClaudeWork\rimmandrake\scratch\landmarkicons\PHONE_landmarks_Rust_Cathedral_before_after.png`. Made with `world_hill_preview.py --lm-scale 0.6 --lm-alpha 0.55`.

## What the live check must settle

1. **Does the fade show?** The fade relies on `WorldOverlayTransparentLit` honouring `_Color` alpha from the property block. Settlement icons on the same shader take their faction tint from `_Color`. Alpha on that shader is UNMEASURED.
   - If icons shrink but do not fade, alpha is not reaching the shader. The fix is vertex alpha, which our border blend proves works on this shader.
2. **Are they still findable?** Hover and inspect a Ruins tile on the Rust Cathedral and confirm the landmark name still shows.
3. **Do the defaults suit him?** In the offline preview, 60% / 55% is very faint. Tune live with `jawa/static_call RimMandrake.Biomes.RM_WorldLandmarks Set "softAt|0.3"` or with the sliders. `RM_WorldLandmarks.Info` reports the current state.

Counts on `world/ASHKARR_DEV_START_2026-10-20.rws`: 3,008 landmarks across 65 defs. Ours:

- RUT_ComplexStructures 75
- RSW_Sarlacc 8
- RSW_DeadSarlacc 7
- RM_TarLakes 7
- RM_MagmaticQuagmire 3
- RM_QuicksandPits 1
- RUT_GapingDoom 1

The full list is in `D:\ClaudeWork\rimmandrake\scratch\landmarkicons\counts_by_def.txt`.
