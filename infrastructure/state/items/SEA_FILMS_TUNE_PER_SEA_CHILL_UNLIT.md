# SEA_FILMS_TUNE_PER_SEA_CHILL_UNLIT

Parent: WORLD_WATER_REDRAW_SEAS_THAT_READ_DEEP. Evidence: round-2 sheet `Transient/world_water_review_r2_2026-10-24.html`
(renders `D:\ClaudeWork\rimmandrake\scratch\worldwater_variants_r2`, `stats.json` water_value_far).

## why
The owner wants The Chill "ominously dark compared to other bodies". The sea films in `RM_WorldLook.BuildSea`
(src/RimMandrake/BiomesShell/Source/RM_WorldLook.cs lines 46-50, 231-252) are ONE global setting for every water
biome: the deep film (`seaDeepColor` 0.05,0.09,0.20 at `seaDeepAlpha` 0.5) is lighter than a dark Chill face and LIFTS
it (abyss face value 22 reads 39 after films; night 34 reads 45; the same night face with no films reads 34). It also
paints a dark ring round each island where the deep film fades out (row Chill_still_abyss).

## spec
C#:
- Per-sea film overrides: a static string like `seaFilmOverrides = "RM_TheChill=off,RUT_TheChill=off"` (or
  `=shore:a,deep:a`) parsed like `swirlBiomes`; BuildSea skips or rescales EmitSeaTile per biome.
- Default: The Chill twins have no films (unlit). Settable live like the other statics.
- Mod Settings toggle: "Planet: The Chill stays unlit (no sea films)" beside `worldSeaDepth` (RM_BiomesMod.cs line 59).
- Build with `python3 src/RimMandrake/Utils/winbuild.py`, refresh the .srchash, deploy plan then --apply.

## verify
Owner-attended look (FOUNDRY is offline): 18 grid points at altitude 900 + close-ups at 320; The Chill darker than
every other sea, no ring round islands.
