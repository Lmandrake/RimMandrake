# RIMMANDRAKE_PAINT_SHIP_GIFTS_OWN_ART — the ship gifts still on stand-in art

Found by BIOME_SHIP_CONTRIBUTIONS_1 (Whittle judge, 2026-11-11): the item's criteria are *"the gravship becomes a
scrapbook of everywhere it has been"*, and 14 of the 24 biome ship gifts would look like other things on a deck.

## spec

Give each its own texture through the art pipeline (generate, validate, a fresh art judge, `art.py install`), at 128 px
per cell. Measured from each def's texPath and header (2026-11-11):

Borrowing another thing's texture (texPath points at someone else's art):
- `RM_HullLinerRig` (Cauldron) — FlowWorks liquid tap
- `RM_WindVaporator` (Leaning Scrub) — vanilla moisture pump
- `RM_SunSphere` (Terminal Biomes) — RM_GlowTank
- `RM_Glasswalk` (Sump) — vanilla deep-water ramp terrain
- `RM_AerosolScreen` (Warscar) — old-line turret base
- `RM_GlowerShieldPanel` (Warscar) — RM_LoosenedPanel
- `RM_WasteCaskBay` (Wastes) — vanilla shelf
- `RM_TractionLance` (Webwork) — web anchor

Declared placeholders in their own def headers:
- `RM_SummGreatBone` (Abyss), `RM_SekkulaathTank` (Fever Wood, flat colour), `RM_LureAwning` (Long Shade, tinted tent),
  `RM_TarVault` (Sump), `RM_FloatstoneDoor` (Forge, vanilla door), `RM_AncientCondenserPlant` (Weeping Stones, copied
  condenser stack)

## verify

Each listed def's texPath resolves to a texture made for it in its own mod (art ledger event, judge verdict), and its
def header no longer says placeholder.
