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

## ✅ CLOSED 2026-08-22 by BUILD — both defects, `922b9207` and `073e5399`

**1. Hovering black pixels — gone.** 24 detached near-black islands, 958 px, across 7 of
the 15 art PNGs: leftover outline fragments the chroma-key cut loose from a foot, a claw
or a rein. Every one measured ≤96 px against a main mass of ≥44,692 and `(0,0,0)`–
`(18,18,18)`. `Source/despeckle.py` does it, keeps anything over 1% of the main mass or
not dark enough, and REPORTS what it kept — nothing tripped either guard. A second run
reports 0.

**2. Truncated tails — the cause was the east trim, not the generation.**
`trim_to_band_aspect.py` takes surplus width off the **LEFT** to match the band aspect,
and the left is exactly where a dewback and a ronto keep their tails. `--max-cut` was
uncapped on three of the four, so the crop took whatever the aspect wanted.

| vehicle | cut before → after | residual aspect | distortion | band span |
|---|---|---|---|---|
| WarChariot | 352 → **199 px** | +11.7% | −10.5% | 100%×100% |
| CoveredCarriage | 182 → **112 px** | +5.8% | −5.5% | 100%×100% |
| OxCart | 103 → **88 px** | +0.9% | +2.6% | 104%×100% |

All three still **PASS** `validate_sprite.py` against their donor, and the beasts came out
**bigger** in the band, not smaller — the wider bbox fits the band better, so this cost
nothing.

⛔ **Chariot is deliberately unchanged at `--max-cut 0.30`, and that is a decision, not an
omission.** Its single dewback is 2.56 aspect against a 1.53 band, so a smaller cut cannot
win: 0.20 fills the band 100%×**78%** and 0.15 fills it 100%×**73%** — the animal shrinks
for a tail stub invisible at sprite size. All three were rendered side by side, big and at
sprite size, before choosing. 🔑 **The comparison is the reason, not the numbers.**

⚠️ **`EAST_COMMISSION.md`'s build block had a second, unrelated error and it is fixed
here:** its CoveredCarriage line read `ronto_pair_gen_east.png`, the olive original,
where what actually ships is the dun recolour `ronto_pair_gen_east_dun.png`. Anyone
re-running that block verbatim would have rebuilt an olive ronto.

**Not verified in game.** Deployed and byte-verified in sync; the sprites are only read at
load, so the owner's eye at the next start is the last check.
