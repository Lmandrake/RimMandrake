## spec
`NEOLITHIC_VEHICLE_BEAST_RESKIN_1` closed offline at `742481f`: all **12 facings**
(OxCart, CoveredCarriage, WarChariot, Chariot × south/north/east) pass
`validate_sprite.py` against their donors, and all 12 are deployed. West is NOT authored
and must not be — `Vehicles.Graphic_Rgb` derives it by flipping east, which is why neither
the donor mod nor our DogSled ships one.

Beast ladder, DECIDE's ruling from measured `baseBodySize`:
`Chariot` dewback ×1 · `WarChariot` dewback ×2 · `OxCart` bantha ×2 ·
`CoveredCarriage` ronto ×2.

## verify
Architect ▸ Vehicles, place each of the four, and rotate through north, south and east.
🔴 A Vehicle Framework vehicle spawns as a **PAWN** — `jawa/list_things` returns nothing
at the cell. Use `jawa/list_pawns`.

## criteria
Each of the four draws its own beasts in all three authored facings, and west draws as a
mirrored east rather than as anything wrong.
🪤 **THE FALSE PASS, and it is the whole reason this is a separate item:** the art reaches
every def by `texPath` override whether or not any patch ran, so **seeing new art proves
nothing about the def work.** The tell is the **architect menu label**, because the
blueprint is a third def the reskin never touches. Check the health tab too — it should
read Left/Right **Bantha** / **Ronto** / **Dewback**, from `VehicleBeastLabels.xml`.

## notes
Two art-direction observations BUILD is reporting rather than acting on:
1. **Ronto and dewback both came out olive-green.** DECIDE's ladder treats them as
   distinct species; at sprite size they may not read as different. Worth a look when both
   are on screen.
2. **OxCart east is the weakest of the twelve** — the banthas stand a few pixels clear of
   the shaft where the donor's oxen touch it. `validate_sprite` passes it with a
   detached-fragments warning. Cosmetic, and visible only magnified.
3. The sled's hurt sound is now a muffalo rather than a dog (`b5a524f`); if anything is
   shot while pulling, that is the sound to expect.
