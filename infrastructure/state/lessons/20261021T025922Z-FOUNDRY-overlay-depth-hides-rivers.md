A world overlay that WRITES depth at the same height as another layer hides it: the border blend at +0.01 sat at WorldDrawLayer_Rivers' height and hid the river on every biome-border tile, which read as dashed rivers while the link data was whole. Check z-order (rivers +0.01, hills +0.005, roads +0.02) before blaming data; blendLift is now 0.003.
home: skills/rimworld-world-editing
