-- hutt_holding_pens.lua - the palace's cells and the guardroom that watches
-- them: a row of bare concrete cells off a corridor, the guardroom out front
-- with its own door, and a guards' barracks beside it.
-- DISTRICT_TEMPLATE_LIBRARY_1, Hutt Cartel district #3 (Gorga the Immense's
-- Palace manifest slot "holding pens").
--
-- CANON: faction_roster_v2.md, Hutt Cartel "Technology and economy":
-- "prisons, barracks"; "hostile the way a creditor is hostile" - a debtor
-- who cannot pay is held here until someone does. The world map names
-- "Hurgo's Kennels" and "Norba's Vault" among the Cartel's deep-desert posts.
--
-- Built to the owner's live-review bar (TILE_STRUCTURE_REVIEW_SAVE_1):
--   FLOORING   cells: bare CONCRETE - the one deliberately mean floor in the
--              set, and still a laid floor, not stony soil; corridor: concrete;
--              guardroom and barracks: sandstone tile.
--   GRIDS      the cell row is architecture (a corridor of cells IS a row);
--              inside every room the furniture is placed by seeded choice.
--   CLUTTER    a wash tub and a stool in some cells, a guards' table with a
--              pazaak game, weapon shelving, crates, a barracks with beds
--              head-to-wall, dressers, end tables, wall lamps; an Aurebesh
--              PRISON sign at the corridor door.
--
-- SECURITY PROPS, with teeth: a barricade line inside the guardroom door and
-- a turret covering the corridor - the first Hutt district that carries the
-- security vocabulary junkers_depot.lua once only sketched.
-- --tech Industrial (Hutt FactionDef techLevel).

function min_rect(params)
  return 17, 15
end

function build(ctx)
  local w, h = rect.w, rect.h
  if w < 17 or h < 15 then
    ctx:refuse("footprint", string.format(
      "%dx%d too small for four cells over a corridor plus a guardroom and barracks", w, h))
    return
  end

  -- ---- the cell row across the north --------------------------------------
  local cell_h = 6
  local cell_w = 5                       -- 3-wide interiors
  local n_cells = math.floor((w - 1) / (cell_w - 1))
  local row_w = n_cells * (cell_w - 1) + 1
  local row_x = rect.x + math.floor((w - row_w) / 2)
  local cells_z = rect.z2 - cell_h + 1
  local corridor = R(rect.x, cells_z - 3, w, 4)
  -- the corridor first: its north wall row IS the cells' south wall row, and
  -- a door must be cut AFTER every wall that shares its cell has been laid
  local ki = shell(ctx, "Corridor", corridor, { floor = "FLOOR_WORK" })
  local cells = {}
  for i = 0, n_cells - 1 do
    local c = R(row_x + i * (cell_w - 1), cells_z, cell_w, cell_h)
    local ci = shell(ctx, "PrisonCell", c, { floor = "FLOOR_CELL" })
    -- the cell door opens south onto the corridor, off-centre where it can be
    ctx:door(c.x + rng.int(1, cell_w - 2), c.z)
    cells[#cells + 1] = ci
  end

  -- ---- guardroom (with the outside door) and barracks along the south -----
  local south = R(rect.x, rect.z, w, corridor.z - rect.z + 1)
  local split = south.x + math.floor(w * 0.55) + rng.int(-1, 1)
  local guard = R(south.x, south.z, split - south.x + 1, south.h)
  local barracks = R(split, south.z, south.x2 - split + 1, south.h)
  local gi = shell(ctx, "GuardRoom", guard, { floor = "FLOOR", doors = { { "S", rng.int(2, guard.w - 3) } } })
  local bi = shell(ctx, "Barracks", barracks, { floor = "FLOOR" })
  -- guardroom opens north into the corridor; barracks opens into the guardroom
  local corr_door_x = guard.x + rng.int(2, guard.w - 3)
  ctx:door(corr_door_x, guard.z2)
  ctx:door(split, barracks.z + rng.int(2, barracks.h - 3))
  if ctx:has_role("SIGN_PRISON") then ctx:place_overlay("SIGN_PRISON", corr_door_x, ki.z, 0) end

  -- ---- furnish the cells: a bed, sometimes a tub, sometimes a stool --------
  local beds = 0
  for _, ci in ipairs(cells) do
    beds = beds + along_wall(ctx, "BED", ci, rng.pick({ "N", "W", "E" }), 1, { face = "wall" })
    if rng.chance(0.5) then dress(ctx, ci, { { role = "TUB", n = 1, where = "corner" } }) end
    if rng.chance(0.4) then dress(ctx, ci, { { role = "STOOL", n = 1 } }) end
  end
  note(string.format("%d cell(s) off the corridor, %d bed(s)", #cells, beds))

  -- ---- the corridor: a turret at one end covers its length ------------------
  local turret = 0
  if ctx:has_role("TURRET") then
    local tx = rng.pick({ ki.x, ki.x2 })
    if try_place(ctx, "TURRET", tx, ki.z + 1, 0) then turret = 1 end
  end
  wall_lights(ctx, ki, rng.int(2, 3))

  -- ---- the guardroom ---------------------------------------------------------
  do
    local trot = rng.int(0, 1)
    local ok, tx, tz = try_near(ctx, "TABLE", gi.x + math.floor(gi.w / 2), gi.z + math.floor(gi.h / 2), trot, 2, gi)
    if ok then seat_around(ctx, "CHAIR", tx, tz, rng.int(2, 3), gi, trot) end
    along_wall(ctx, "STORAGE", gi, rng.pick({ "W", "N" }), rng.int(1, 2), { gap = 1 })
    -- a barricade line just inside the outside door
    local barricades = 0
    if ctx:has_role("BARRICADE") then
      for x = gi.x, gi.x2 do
        if not rng.chance(0.45) and not blocks_a_door(ctx, x, gi.z + 1, gi)
           and try_place(ctx, "BARRICADE", x, gi.z + 1, 0) then barricades = barricades + 1 end
      end
    end
    dress(ctx, gi, {
      { role = "GAME",        n = { 0, 1 }, where = "corner" },
      { role = "CRATE",       n = { 1, 2 }, where = "wall" },
      { role = "SHELF_SMALL", n = { 0, 1 }, where = "wall" },
      { role = "STOOL",       n = { 0, 1 } },
      { role = "LIGHT",       n = 1,        where = "corner" },
    })
    wall_lights(ctx, gi, rng.int(1, 2))
    note(string.format("guardroom: %d barricade cell(s) inside the door, turret %s the corridor",
      barricades, turret > 0 and "covering" or "NOT placed over"))
  end

  -- ---- the barracks ----------------------------------------------------------
  do
    local got = 0
    for _, side in ipairs(shuffle({ "N", "E", "S" })) do
      if got >= 3 then break end
      got = got + along_wall(ctx, "BED", bi, side, 3 - got, { face = "wall", gap = 0 })
    end
    dress(ctx, bi, {
      { role = "DRESSER",   n = { 0, 1 }, where = "wall" },
      { role = "END_TABLE", n = { 1, 2 }, where = "wall" },
      { role = "CRATE",     n = 1,        where = "corner" },
      { role = "LIGHT",     n = 1,        where = "corner" },
    })
    wall_lights(ctx, bi, 1)
    note(string.format("barracks: %d guard bed(s)", got))
  end
end
