# RIVER_DASHES_MEASURE_MORSE_CODE_WATER

**Mechanism (MEASURED 2026-10-20, FOUNDRY).** The world border blend in
`src/RimMandrake/BiomesShell/Source/RM_WorldLook.cs` drew its overlays at `blendLift` = +0.01 above the terrain.
That is the height vanilla `WorldDrawLayer_Rivers.FinalizePoint` gives rivers (+0.01), and the overlays write depth.
On every biome-border tile (7,567) the overlay won the depth test and hid the river and the hill blots (+0.005).
Roads sit at +0.02, so they drew whole.

**The data was whole.** `jawa/world_links_validate` against the record links CSV gave 0 asymmetric, 0 non-adjacent and
1,568/1,568 present. Rivers form 11 connected pieces in both the record and the U4 mouth-first file.

**Fix.** `blendLift` is now 0.003 (`e7adc75e3`). Proved live with `jawa/static_call RM_WorldLook Set blendLift|0.003` and
`world_commit`, same camera:
`D:\ClaudeWork\rimmandrake\scratch\riverdashes\rd_before_4271.png` (dashes),
`D:\ClaudeWork\rimmandrake\scratch\riverdashes\rd_after_lift003_4271.png` (whole),
`D:\ClaudeWork\rimmandrake\scratch\riverdashes\rd_after_wide_16490.png` (wide view).

**Not deployed yet.** The game holds the DLL open. `--compose biomes` also carries 21 other drifted files from other work.
Deploy and readback: `RIVER_BLEND_DEPLOY_UNDER_THE_WATERLINE`.
