# HILL_DECALS_VERIFY_NO_MORE_COOKIE_CUTTERS

`HILL_DECALS_VERIFY_NO_MORE_COOKIE_CUTTERS` — built and committed (08512defb), not deployed; NEXT: at the next consolidated deploy of RimMandrake.Biomes, look at a hilly region (Dew Horn, Gray Crags) on the planet and confirm the brown outlined hill blots are gone and hills read as soft dark relief in each biome's own hue.

## Mechanism (RimSage, 1.6)

- `WorldDrawLayer_Hills.Regenerate` draws one quad per hilly tile that has NO landmark. The quad is 0.9-1.1 x tile size, lifted +0.005, rotated at random, its centre jittered, and it uses one random cell of a 2x2 atlas.
- There are four SHARED materials, built in the `WorldMaterials` static constructor: `World/Hills/{SmallHills,LargeHills,Mountains,Impassable}`, shader `WorldOverlayTransparentLit`, queue 3510, colour white. There is no HillsDef and no biome tint.
- The vanilla cells (a 128 px atlas) are brown blots (mean RGB about 80,57,36, alpha about 0.45) with a hard dark outline. That one-pixel alpha step is 0.53-0.75.

## Change

- `src/RimMandrake/Utils/art/world_hill_decals.py` generates our own 256 px atlases. Each is a dark neutral (36,28,21) whose alpha carries soft relief. The shading does not depend on direction, because every quad is rotated at random. Peak alpha runs 0.21 / 0.30 / 0.40 / 0.50 from small hills to impassable, and no one-pixel step exceeds 0.055.
- They were installed through `art.py install` at `src/RimMandrake/TerminalBiomes/Textures/World/RM_Hills/`.
- `RM_WorldLook.ApplyHills` swaps those textures onto the four shared materials at startup.
- Mod Settings has a new checkbox, "Planet: soft hill shading [now]", on by default. Off restores the captured vanilla textures at once.

## Live check

- Deploy RimMandrake.Biomes. The DLL and the `RM_Hills` textures go together.
- `jawa/static_call RimMandrake.Biomes.RM_WorldLook Info` should show `hillsApplied=True`.
- Look at Dew Horn and Gray Crags at mid zoom.
- Toggle the setting off and on. The hills should change at once, with no redraw.

## Preview

Regenerate the before/after images with `python3 src/RimMandrake/Utils/art/world_hill_preview.py --region "Dew Horn" --hills <dir> --landmarks <dir>`. A copy as of 2026-10-20 is in `D:\ClaudeWork\rimmandrake\scratch\hilldecals\PHONE_hills_*_before_after.png`.

## Not this item

The Rust Cathedral speckle is landmark icons: see `LANDMARK_ICONS_DECIDE_THE_REAL_SPECKLE`.
