-- hutt_cistern_court.lua - the palace's walled cistern: a high sandstone
-- wall with one gate, a sandbag line and a turret inside it, and in the
-- paved court the water itself - tanks in a cluster, a well, a fountain,
-- troughs for the beasts that carry it - with the water-warden's hut in a
-- corner and a little planted shade. DISTRICT_TEMPLATE_LIBRARY_1, Hutt Cartel
-- district #4 (Gorga the Immense's Palace manifest slot "cistern court").
--
-- CANON: faction_roster_v2.md, Hutt Cartel "Technology and economy":
-- "walled cistern"; "The Cartel owns the oases and sells water at whatever
-- the buyer can be made to pay" (FactionDef description); the world map's
-- Cartel rows all read "the well is guarded and is NOT free". The court is
-- the guarded well made into a room.
--
-- Built to the owner's live-review bar (TILE_STRUCTURE_REVIEW_SAVE_1):
--   FLOORING   the court is patterned sandstone brick (FLOOR_YARD) with a
--              sandstone mosaic apron (FLOOR_WET) around the water; the
--              warden's hut sandstone tile. Unroofed on purpose - a cistern
--              court is open to the sky - so it is walled by hand, not
--              declared as a room (rimplace's room lint would demand a roof).
--   GRIDS      tanks cluster, troughs and tubs scatter, plants and lamps hug
--              the walls at random slots.
--   CLUTTER    troughs, wash tubs, plant pots, braziers, tall lamps, crates
--              by the gate, the warden's bed, table, chair, shelf and lamp.
--
-- SECURITY PROPS, with teeth: sandbags inside the gate and a turret on the
-- court - the guarded well, literally.
-- --tech Industrial (Hutt FactionDef techLevel).

function min_rect(params)
  return 16, 16
end

function build(ctx)
  local w, h = rect.w, rect.h
  if w < 16 or h < 16 then
    ctx:refuse("footprint", string.format("%dx%d too small for a walled court with a hut and a tank cluster", w, h))
    return
  end
  local court = R(rect.x, rect.z, w, h)
  local yard = inner(court, 1)

  -- ---- the wall and the gate: no room() on purpose, this is open to the sky
  ctx:wall_rect(court.x, court.z, court.w, court.h)
  floor_patch(ctx, yard, "FLOOR_YARD")
  local gate_x = court.x + rng.int(4, w - 5)
  ctx:door(gate_x, court.z)
  ctx:door(gate_x + 1, court.z)

  -- ---- the warden's hut in a back corner ------------------------------------
  local hut_w, hut_h = 6, 5
  local hut_side = rng.pick({ "W", "E" })
  local hut = R((hut_side == "W") and (court.x + 1) or (court.x2 - hut_w), court.z2 - hut_h, hut_w, hut_h)
  local hi = shell(ctx, "Bedroom", hut, { floor = "FLOOR", doors = { { (hut_side == "W") and "E" or "W", 2 } } })
  along_wall(ctx, "BED", hi, "N", 1, { face = "wall" })
  do
    local ok, tx, tz = try_near(ctx, "TABLE_SMALL", hi.x + 1, hi.z, 0, 1, hi)
    if ok then seat_around(ctx, "CHAIR", tx, tz, 1, hi, 0) end
  end
  dress(ctx, hi, {
    { role = "SHELF_SMALL", n = 1, where = "wall" },
    { role = "CRATE",       n = 1, where = "corner" },
    { role = "LIGHT",       n = 1, where = "corner" },
  })
  wall_lights(ctx, hi, 1)
  local keep = { R(hut.x - 1, hut.z - 1, hut.w + 2, hut.h + 2), R(gate_x - 2, court.z + 1, 6, 4) }

  -- ---- the water: a tank cluster on a mosaic apron, a well, a fountain -----
  local cx = court.x + math.floor(w / 2) + ((hut_side == "W") and 1 or -1) * rng.int(0, 2)
  local cz = court.z + math.floor(h / 2) + rng.int(0, 1)
  local apron = R(cx - 3, cz - 3, 7, 7)
  floor_patch(ctx, apron, "FLOOR_WET", yard)
  local tanks = scatter(ctx, "WATER_TANK", R(cx - 2, cz - 1, 5, 3), rng.int(3, 4), { tries = 40 })
  local well = try_near(ctx, "WELL", cx, cz - 2, 0, 1, apron) and 1 or 0
  local fountain = try_near(ctx, "FOUNTAIN", cx + rng.pick({ -3, 3 }), cz + rng.pick({ -2, 2 }), 0, 1, yard) and 1 or 0
  local troughs = scatter(ctx, "TROUGH", inner(yard, 1), rng.int(2, 3), { keep_clear = keep, rot = "any", tries = 40 })
  scatter(ctx, "TUB", inner(yard, 1), rng.int(1, 2), { keep_clear = keep })
  note(string.format("cistern court: %d tank(s) on the apron, well %d, fountain %d, %d trough(s)",
    tanks, well, fountain, troughs))

  -- ---- shade and light along the walls, crates by the gate -------------------
  dress(ctx, yard, {
    { role = "PLANT_POT",  n = { 3, 5 }, where = "wall" },
    { role = "LIGHT_TALL", n = { 2, 3 }, where = "corner" },
    { role = "BRAZIER",    n = { 1, 2 }, where = "wall" },
  })
  scatter(ctx, "CRATE", R(gate_x - 4, court.z + 1, 10, 2), rng.int(1, 3), { keep_clear = { keep[2] } })
  wall_lights(ctx, yard, rng.int(2, 4))

  -- ---- security props: sandbags inside the gate, a turret on the court -----
  local bags, turret = 0, 0
  if ctx:has_role("SANDBAG") then
    for x = gate_x - 2, gate_x + 3 do
      if x ~= gate_x and x ~= gate_x + 1 and try_place(ctx, "SANDBAG", x, court.z + 2, 0) then bags = bags + 1 end
    end
    for _, x in ipairs({ gate_x - 2, gate_x + 3 }) do
      if try_place(ctx, "SANDBAG", x, court.z + 1, 0) then bags = bags + 1 end
    end
  end
  if ctx:has_role("TURRET") then
    local tx = (hut_side == "W") and (court.x2 - 2) or (court.x + 2)
    if try_near(ctx, "TURRET", tx, court.z + 3, 0, 1, yard) then turret = 1 end
  end
  note(string.format("security props: %d sandbag cell(s) inside the gate, %d turret(s) - the well is guarded and is NOT free",
    bags, turret))
end
