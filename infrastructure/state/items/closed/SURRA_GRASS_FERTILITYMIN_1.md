# SURRA_GRASS_FERTILITYMIN_1 — owner card: fertilityMin locks surra grass off Sand

## ruling (owner, 2026-09-20)

Owner chose (b): KEEP `fertilityMin` at 0.30. Surra grass stays confined to Soil
islands, off Sand. Reasoning is now written into `RSW_Dunegrass`'s def comment
in `src/RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortMisc_Plants.xml`:
the grass being confined to the damper soil is the player's water-table signal
— green means water. Landed and closed.

## what is wrong

`RSW_Dunegrass` (surra grass) has `fertilityMin 0.30`, but Core's Sand
terrain has fertility 0.10. At its current 0.6 weight (already trimmed down
from 2.2), the grass can only grow on Soil islands within the biome — never
on the Sand that makes up most of RUT_Desert. This was never an explicit
ruling; the roster document only records that the weight was "trimmed
2.2→0.6," not that the `fertilityMin`/terrain mismatch was noticed or
decided.

## why it matters

The biome's second-heaviest-weighted plant is effectively confined to a
small fraction of its own biome's terrain, and nobody has ruled on whether
that is intended.

## the decision this needs

- (a) lower `fertilityMin` to 0.05 so surra grass takes Sand the way vanilla
  grass does, spreading it across the biome; or
- (b) keep `fertilityMin` at 0.30, confining the grass to the dew-line halo
  around Soil islands.

The source review recommends (b) — the confinement suits the design language
"the long shade" — with the reasoning written into the def's own XML comment
so it reads as deliberate rather than a bug.

## Watch out

Whichever way this is ruled, the reasoning must be written into
`RSW_Dunegrass`'s def comment — this is exactly the kind of fact
`DESERT_DEF_HEADER_STALE_COUNTS_1` exists to catch when it goes stale later.

## verify

`RSW_Dunegrass`'s `fertilityMin` matches the owner's ruling, and the def
carries a comment stating which option was chosen and why.

## criteria

Surra grass's terrain confinement (or lack of it) is a recorded decision, not
an accidental side effect of an unrelated weight trim.
