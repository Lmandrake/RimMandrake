## spec
`design/Jawa/templates/dwelling.lua` declares bay 2 of a 2-3 room dwelling as
`DiningRoom` and furnishes it with a Table, a Chair, AND a Stove (when the
faction's palette has one — most do; only the droid factions do not, and they
take a different branch entirely).

Live, RimWorld does not let a template assign a room's role — `Room.Role` is
always computed as the highest-scoring `RoomRoleWorker`. Measured in the 1.6 C#
source:
- `RoomRoleWorker_Kitchen.GetScore`: 28 points per Production-category building
  whose recipes make human-edible food (a stove qualifies).
- `RoomRoleWorker_DiningRoom.GetScore`: 12 points per `surfaceType == Eat`
  building (a table).

One stove (28) always outscores one table (12), so any bay that gets both reads
live as **Kitchen**, never DiningRoom — the template's own predicted label was
wrong for every faction whose palette includes a stove.

## fix
`room_role_for` now takes `ctx` and predicts `Kitchen` for bay 2 whenever
`ctx:has_role("STOVE")` is true (`DiningRoom` only when the faction's palette
has no stove, e.g. a future faction that eats but does not cook). Both call
sites pass `ctx`; the furnish branch matches `rrole == "DiningRoom" or rrole ==
"Kitchen"` so table/chair/stove placement is unchanged — only the predicted
label changed to match what the live game will actually compute.

## verify
    ~/.local/venvs/rimlua/bin/python -m rimplace render dwelling --rect 0,0,20,10 \
      --faction Jawa_IndigenousTribes --rooms 2 --occupants 3 --json
    room r2   Kitchen      11x10 at (9,0)   ("role": "Kitchen" in the JSON rooms array)

Table, Chair and ElectricStove all still placed in bridge `calls` output —
furnishing untouched, only the room-role prediction.

## criteria
- [x] The template's predicted room role for a bay containing a stove matches
      what `RoomRoleWorker_Kitchen` vs `RoomRoleWorker_DiningRoom` will compute live.
- [x] Furnishing (table/chair/stove placement) unchanged.
- [x] The droid-faction branch (no DiningRoom/Kitchen role at all) unaffected.
