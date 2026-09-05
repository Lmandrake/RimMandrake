-- junkers_cantina_block.lua - one building, three rooms: the main hall with a
-- bar along the back wall, seating rounds on a salvaged carpet and a pazaak
-- table in the corner; behind it the keeper's room and a stock room.
-- DISTRICT_TEMPLATE_LIBRARY_1, Junkers district #3 (The Claim Jump manifest
-- slot "cantina block").
--
-- REWORKED 2026-09-05 against the owner's live-review verdict
-- (TILE_STRUCTURE_REVIEW_SAVE_1 - flooring, regular grids, clutter):
--   FLOORING   the hall is iron divoted tile (FLOOR_FINE) with a burgundy
--              carpet (RUG) laid under the seating; the keeper's room rust
--              plating (FLOOR); the stock room grating (FLOOR_WORK). The old
--              file laid NO floor at all - bare dirt under every table.
--   GRIDS      the stepped bar-shelf row and the two banded seating rounds
--              are gone. Bar shelving hugs the back wall at random slots; the
--              counter is two tables end to end with stools pulled up on the
--              room side; each seating round is a table at a jittered spot
--              with chairs on random sides facing it.
--   CLUTTER    barrels behind the bar, crates by the stock door, a bandfill
--              left in a corner, wall torches and a floor torch; the keeper's
--              room has a bed, end table, dresser, crate and torch; the stock
--              room shelves, barrels and crates.
--
-- --tech Neolithic like the other Junkers districts - no powered fixtures.
-- Security props: NONE (searchesLeavers=false); this IS the classic
-- overheard-rumour room a higher-security settlement would watch, and for
-- Junkers it deliberately is not watched.

-- From build()'s own arithmetic: hall interior >= 8 rows and 12 wide; back bay 6.
function min_rect(params)
  return 14, 15
end

function build(ctx)
  local p = params
  local w, h = rect.w, rect.h
  local back_h = 6
  local hall_h = h - back_h + 1   -- +1: the shared wall row
  if hall_h < 10 or w < 14 then
    ctx:refuse("footprint", string.format(
      "%dx%d too small for a cantina hall (>=14 wide, >=10 rows) plus a %d-row back bay", w, h, back_h))
    return
  end

  local hallBay = R(rect.x, rect.z, w, hall_h)
  local backBay = R(rect.x, hallBay.z2, w, back_h)
  local split = backBay.x + math.floor(w / 2) + rng.int(0, 1)
  local keeper = R(backBay.x, backBay.z, split - backBay.x + 1, back_h)
  local stock = R(split, backBay.z, backBay.x2 - split + 1, back_h)

  -- ---- shells and doors ----------------------------------------------------
  local hi = shell(ctx, "Cantina", hallBay, { floor = "FLOOR_FINE", doors = { { "S", rng.int(3, w - 4) } } })
  local ki = shell(ctx, "Bedroom", keeper, { floor = "FLOOR" })
  local si = shell(ctx, "Storeroom", stock, { floor = "FLOOR_WORK" })
  -- interior doors in the shared row: keeper's near the bar end, stock room
  -- wherever it falls; both open off the hall
  local keeper_door_x = keeper.x + rng.int(2, keeper.w - 3)
  local stock_door_x = stock.x + rng.int(2, stock.w - 3)
  ctx:door(keeper_door_x, backBay.z)
  ctx:door(stock_door_x, backBay.z)

  -- ---- the hall ---------------------------------------------------------------
  -- the bar: shelving along the back (north) wall with gaps, then a counter
  -- one row in, front of it kept as the barkeep's walk
  local bar = along_wall(ctx, "STORAGE", hi, "N", rng.int(2, 3), { gap = 1 })
  local counter_z = hi.z2 - 2
  local counter_x = hi.x + rng.int(1, 3)
  local counters = 0
  for i = 0, 1 do
    local cx = counter_x + i * (ctx:width_of("TABLE") + 1) + rng.int(0, 1)
    if cx + 1 <= hi.x2 - 2 and try_place(ctx, "TABLE", cx, counter_z, 1) then counters = counters + 1 end
  end
  -- stools on the room side of the counter, facing it, not every slot taken
  local stools = 0
  for x = counter_x - 1, counter_x + 6 do
    if x >= hi.x and x <= hi.x2
       and (ctx:role_at(x, counter_z) == "TABLE" or ctx:role_at(x - 1, counter_z) == "TABLE")
       and not rng.chance(0.35) then
      if try_place(ctx, "STOOL", x, counter_z - 1, 0) then stools = stools + 1 end
    end
  end
  -- barrels behind the bar
  scatter(ctx, "BARREL", R(hi.x, hi.z2 - 1, hi.w, 2), rng.int(1, 2))

  -- the carpet under the seating half of the room
  local rug = R(hi.x + rng.int(1, 2), hi.z + 1, hi.w - rng.int(3, 5), counter_z - hi.z - 3)
  if rug.w >= 4 and rug.h >= 3 then floor_patch(ctx, rug, "RUG", hi) end

  -- seating rounds: tables at jittered spots, chairs on random sides
  local rounds = 0
  local zone = R(hi.x + 1, hi.z + 1, hi.w - 2, counter_z - hi.z - 3)
  for i = 1, rng.int(2, 3) do
    local trot = rng.int(0, 1)
    local ok, tx, tz = try_near(ctx, "TABLE", rng.int(zone.x + 1, zone.x2 - 1), rng.int(zone.z + 1, zone.z2 - 1),
      trot, 2, zone)
    if ok then
      rounds = rounds + 1
      seat_around(ctx, "CHAIR", tx, tz, rng.int(2, 3), hi, trot)
    end
  end

  -- the pazaak table in a corner, a bandfill left in another
  local game = dress(ctx, hi, { { role = "GAME", n = 1, where = "corner" } })
  if game == 0 then game = along_wall(ctx, "GAME", hi, rng.pick({ "E", "W" }), 1) end
  dress(ctx, hi, {
    { role = "INSTRUMENT", n = 1,        where = "corner" },
    { role = "CRATE",      n = { 1, 2 }, where = "wall" },
    { role = "LIGHT",      n = { 1, 2 }, where = "corner" },
  })
  wall_lights(ctx, hi, rng.int(2, 3))
  note(string.format("cantina hall: %d bar shelf(s), %d counter(s) with %d stool(s), %d seating round(s), pazaak %s",
    bar, counters, stools, rounds, game > 0 and "in the corner" or "did not fit"))

  -- ---- the keeper's back room: the one person who lives on-site ------------
  along_wall(ctx, "BED", ki, rng.pick({ "N", "W" }), 1, { face = "wall" })
  dress(ctx, ki, {
    { role = "END_TABLE", n = 1,        where = "wall" },
    { role = "DRESSER",   n = { 0, 1 }, where = "wall" },
    { role = "CRATE",     n = 1,        where = "corner" },
    { role = "LIGHT",     n = 1,        where = "corner" },
  })
  wall_lights(ctx, ki, 1)

  -- ---- the stock room ---------------------------------------------------------
  along_wall(ctx, "STORAGE", si, rng.pick({ "N", "E" }), rng.int(1, 2), { gap = 1 })
  dress(ctx, si, {
    { role = "BARREL", n = { 2, 3 }, where = "corner" },
    { role = "CRATE",  n = { 1, 3 }, where = "wall" },
    { role = "LIGHT",  n = 1,        where = "corner" },
  })

  note("no security props placed: Junkers/The Claim Jump is low security by design (searchesLeavers=false)")
end
