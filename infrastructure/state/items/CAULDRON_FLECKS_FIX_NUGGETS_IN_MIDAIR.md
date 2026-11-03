# CAULDRON_FLECKS_FIX_NUGGETS_IN_MIDAIR

## What
Textures/Things/Plant/RM_AssayFlecks/Flecks_Light.png and Flecks_Heavy.png (src/RimMandrake/Cauldron) miss their own
spec (cauldron_enrichment_audio_visuals_spec_2026-10-02.md V3: trunk-centred, lower-trunk weighted, silver-grey /
bronze / blue-violet). Measured 2026-11-02: ~31 % of each overlay's opaque pixels lie outside the tree silhouette
dilated 9 px (they float beside the trunk); Heavy is mostly gold/orange nuggets. Redraw both to the registration
bar of `design/Jawa/worldbuilding/biomes/cauldron_trunk_deposits_design_2026-11-02.md` §5, same edit-and-subtract method as §4.

## Acceptance
`python3 src/RimMandrake/Cauldron/selftest_cauldron_trunk_deposits.py`: once this item is closed (its file leaves
items/), the selftest requires >= 95 % inside for both fleck PNGs.
