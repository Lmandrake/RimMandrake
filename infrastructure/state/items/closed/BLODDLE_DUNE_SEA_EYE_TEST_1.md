# BLODDLE_DUNE_SEA_EYE_TEST_1 — verify bloddle against dune_sea's no-green ban

## what is wrong

Bloddle is currently the ONLY plant on RUT_ExtremeDesert (until
`EXTREME_DESERT_SIGNATURE_FLORA_1` lands its two new plants). The roster's
own confidence note flags that bloddle's appearance was never tested against
dune_sea §6's stated rule: "no green, no leaves." The donor texture lives in
the mlie workshop collection (workshop id `3497316713`); its green-pixel
fraction is **UNMEASURED** — a prior measurement attempt timed out on the
drvfs mount.

## why it matters

The biome's sole plant may visibly violate its own design sheet's stated ban,
and nobody has actually looked.

## the work

Copy the donor PNG to a local (non-drvfs) path first — the drvfs mount is
what caused the prior timeout. Render the bloddle sprite offline
(`reading-rimworld-graphics` skill) and measure the green-dominant pixel
fraction. If it fails the "no green, no leaves" test: either regenerate it
white/glassy via `fill_queue.py`, or move it to RUT_Desert and let
`EXTREME_DESERT_SIGNATURE_FLORA_1`'s light-pipe/silverbole take its slot on
RUT_ExtremeDesert.

## Watch out

Do not re-attempt the pixel measurement directly against the drvfs-mounted
mlie workshop path — copy it to a local path first. That specific step is
what timed out previously (instrument note from the source review).

## verify

A green-dominant pixel fraction is recorded for the bloddle sprite (a real
number, not UNMEASURED); the plant either passes the "no green, no leaves"
test in place, or has been moved/regenerated and the biome table updated
accordingly.

## criteria

RUT_ExtremeDesert's flora — whatever ships — has been visually checked
against its own design sheet's stated constraint, not shipped on an
unverified donor asset.
