# PLACEHOLDER ART — replace under BACTA_TANK_ART_1

Every PNG in this folder was generated procedurally (PIL) to unblock
BACTA_TANK_CORE_1. None of it is finished art. It exists so the tank renders
something legible instead of magenta while the mechanism is tested.

| file | size | what it must be |
|---|---|---|
| `RSW_BactaTank_north.png` | 128x256 | tank body, seen from behind — the plate the pawn is drawn IN FRONT of |
| `RSW_BactaTank_south.png` | 128x256 | tank body, seen from the front side; currently identical to north |
| `RSW_BactaTank_east.png` | 256x128 | tank body lying along the east/west axis (RimWorld mirrors this for west) |
| `RSW_BactaTankShell_north.png` | 128x256 | the GLASS, drawn over the occupant — must be mostly transparent |
| `RSW_BactaTankShell_south.png` | 128x256 | ditto, front |
| `RSW_BactaTankShell_east.png` | 256x128 | ditto, horizontal |

## Constraints the real art must keep

- **Two layers, not one.** `RSW_BactaTank*` is printed under the pawn;
  `RSW_BactaTankShell*` is drawn over it by `CompBactaShell` at
  `AltitudeLayer.MoteOverhead`. The shell must be substantially transparent or
  the suspended pawn disappears behind it.
- **The middle must read as liquid-fillable.** `CompBactaImmersion.PostDraw`
  paints a translucent pale-blue column between the two layers, sized by
  `fluidBarSize` in `RSW_BactaTank.xml` (currently 0.55 x 1.45 cells) and
  scaled by the fluid level. Leave that area clear in both layers.
- **Sizes are drawSize x 128.** `drawSize (1,2)` so north/south are 128x256.
  The east texture is 256x128 because `Graphic.MeshAt` swaps drawSize for the
  horizontal rotations; `_west` is omitted deliberately and mirrored from east.
- **No west file on purpose.** Add one only if the tank becomes asymmetric.
- The def references these by texPath `Things/Building/Bacta/RSW_BactaTank` and
  `.../RSW_BactaTankShell` — **art binds by texPath, not by defName**, so a
  replacement must land at exactly these paths and names.

Generator (throwaway, not committed):
`make_bacta_placeholders.py`, run from the session scratchpad.
