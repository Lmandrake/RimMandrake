## spec
🔴 **OWNER, 2026-08-22, verbatim:** *"the graphics for those desertified primitive
vehicles needs another clean up. Some of them have clearly truncated tails, or hovering
black pixels surrounding them. Clean them up. Otherwise they look good... this is a minor
change."*

**Two defects, both cosmetic, both in the shipped PNGs** under
`src/Jawa/DesertVehicleReskin/Textures/Things/Vehicles/Land/Tier0/`:

1. **Truncated tails** — a beast's tail is clipped at the canvas edge or at a mask
   boundary instead of ending in the animal.
2. **Hovering black pixels** — stray dark pixels floating in the transparent field around
   the silhouette, left behind by the chroma-key or by an erase seed that never reached
   them.

**Five vehicles, 30 PNGs, six facings each** (`_north`, `_south`, `_east` and the `m`
mask variant of each):

| folder | beasts |
|---|---|
| `Chariot` | one dewback |
| `CoveredCarriage` | two rontos |
| `DogSled` | two eopies |
| `OxCart` | two banthas |
| `WarChariot` | two dewbacks |

⛔ **This is a CLEANUP, not a regeneration.** The owner is happy with the art. No
silhouette may move; nothing gets re-fired through the image model. Builders and
provenance live in `src/Jawa/DesertVehicleReskin/Source/` —
`build_beast_vehicle.py`, `EAST_COMMISSION.md`, `GEOMETRY.md`.

## verify
`python3 src/RimMandrake/Utils/check_sprite.py <png>` (or the reskin's own
`validate_sprite.py`) on all 30, plus a contact sheet the owner can look at. A stray-pixel
count of 0 outside the main connected mass, and no tail touching the canvas edge.

## criteria
No floating dark pixel in the alpha field of any of the 30 PNGs, no tail clipped at a
canvas or mask edge, and every silhouette byte-identical in outline to what shipped except
where a defect was removed.

## notes
Filed by BUILD 2026-08-22 on the owner's direct instruction.
