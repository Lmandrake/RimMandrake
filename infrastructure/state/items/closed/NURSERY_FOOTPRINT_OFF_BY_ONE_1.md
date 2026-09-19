## spec
`design/Jawa/templates/nursery.lua` declares its minimum footprint as `RW+8 x RH+1`
(16x9 with RW=RH=8), but the power layer it builds needs one more row than that:
the conduit bus sits at `bus_z = z + RH` (one row past the shell) and the Battery
sits at `bus_z + 1` (two rows past the shell). At the declared minimum H=9, the
Battery lands at row index 9 — one cell outside the room's own footprint check.

Reproduced offline with `rimplace lint`:

    ~/.local/venvs/rimlua/bin/python -m rimplace lint nursery --rect 0,0,16,9 --occupants 4
    WARN  generator-refusal   Battery: outside the footprint at (3,9)

## fix
`H < RH + 1` → `H < RH + 2` (and the refuse message's `RH + 1` → `RH + 2`), so the
declared minimum becomes 16x10 and actually contains everything the template places.

## verify
    ~/.local/venvs/rimlua/bin/python -m rimplace lint nursery --rect 0,0,16,10 --occupants 4
    0 finding(s)

    ~/.local/venvs/rimlua/bin/python -m rimplace lint nursery --rect 0,0,16,9 --occupants 4
    generator-refusal: nursery: needs at least 16x10 of footprint (refuses cleanly,
    places nothing, instead of silently dropping the Battery out of bounds)

## criteria
- [x] Declared minimum footprint contains every building the template places.
- [x] A rect too small to hold the power layer refuses instead of placing partial/out-of-bounds.
