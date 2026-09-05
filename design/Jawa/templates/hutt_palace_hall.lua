-- hutt_palace_hall.lua - a Hutt lord's palace: the audience hall under a
-- double colonnade, a throne on a dais at the far end with a red runway to
-- the doors, a band in one corner and holo-dancers by the dais; across the
-- south front, the lord's private chamber, the entrance vestibule and the
-- majordomo's office. DISTRICT_TEMPLATE_LIBRARY_1, Hutt Cartel district #1
-- (Gorga the Immense's Palace manifest slot "palace hall").
--
-- CANON this is built from (design/Jawa/worldbuilding/faction_roster_v2.md,
-- Hutt Cartel "Technology and economy"): "drug labs, prisons, barracks,
-- throne room, warehouse, defended landing area, walled cistern"; "eight
-- oasis palaces, one lord each"; "wealthy, decentralised and entirely
-- transactional" (FactionDef description). A palace hall is the throne room
-- and the audience floor a Hutt does business from.
--
-- Built to the owner's live-review bar (TILE_STRUCTURE_REVIEW_SAVE_1):
--   FLOORING   the hall is the absorbed KotOR 'outland office tile'
--              (FLOOR_FINE) with a red-carpet runway (RUG_FINE) from the
--              vestibule door to the dais; the chamber sandstone tile under a
--              burgundy rug; the office and vestibule sandstone tile.
--   GRIDS      the colonnade is the ONE regular thing here, because columns
--              are architecture and a hall this deep needs roof support
--              (rimplace lint rule 6); everything a person moved - stools,
--              side tables, plants, braziers, the band, the pazaak table -
--              is placed by seeded scatter and wall-hugging with gaps.
--   CLUTTER    banners and braziers flank the throne, plant pots and small
--              tables line the walls, a pazaak game sits off the runway, the
--              band corner holds a nalargon, a bandfill and a music holo, the
--              lord's chamber has a double bed, dresser, end table, wash tub,
--              gold sculpture and its own rug.
--
-- Security props: a Hutt palace is guarded at the GATE (see
-- hutt_cistern_court.lua and hutt_holding_pens.lua for the props with teeth);
-- the hall itself has none - the guards are cast, not furniture.
-- --tech Industrial (Hutt FactionDef techLevel).

function min_rect(params)
  return 22, 20
end

function build(ctx)
  local w, h = rect.w, rect.h
  if w < 22 or h < 20 then
    ctx:refuse("footprint", string.format(
      "%dx%d too small for a palace hall (>=22 wide, 9-row south front + 11-row hall)", w, h))
    return
  end

  -- ---- the south front: chamber (W), vestibule (middle), office (E) --------
  local front_h = 9
  local front = R(rect.x, rect.z, w, front_h)
  local hall = R(rect.x, front.z2, w, h - front_h + 1)
  local vest_w = 6
  local vest_x = hall.x + math.floor(w / 2) - math.floor(vest_w / 2) + rng.int(-1, 1)
  local chamber = R(front.x, front.z, vest_x - front.x + 1, front_h)
  local vestibule = R(vest_x, front.z, vest_w, front_h)
  local office = R(vest_x + vest_w - 1, front.z, front.x2 - (vest_x + vest_w - 1) + 1, front_h)

  local hi = shell(ctx, "ThroneRoom", hall, { floor = "FLOOR_FINE" })
  local ci = shell(ctx, "Bedroom", chamber, { floor = "FLOOR" })
  local vi = shell(ctx, "Vestibule", vestibule, { floor = "FLOOR" })
  local oi = shell(ctx, "Office", office, { floor = "FLOOR" })

  -- doors: the palace door in the vestibule's south wall, the vestibule opens
  -- north into the hall on the runway; chamber and office open off the hall
  local runway_x = vest_x + math.floor(vest_w / 2)
  ctx:door(runway_x, vestibule.z)
  ctx:door(runway_x, vestibule.z2)
  ctx:door(chamber.x + rng.int(2, chamber.w - 3), chamber.z2)
  ctx:door(office.x + rng.int(2, office.w - 3), office.z2)

  -- ---- the hall ---------------------------------------------------------------
  -- the runway: three cells of red carpet from the vestibule door to the dais
  local runway = R(runway_x - 1, hi.z, 3, hi.h - 3)
  floor_patch(ctx, runway, "RUG_FINE", hi)
  -- the dais: a band of the finest tile at the north end, the clan decal on it
  local dais = R(runway_x - 3, hi.z2 - 2, 7, 3)
  floor_patch(ctx, dais, "FLOOR_FINE", hi)
  if ctx:has_role("DECAL") then ctx:place_overlay("DECAL", runway_x, hi.z2 - 4, 0) end
  -- the throne (3x2), centred on the dais against the north wall, facing south
  local throne = false
  if ctx:has_role("THRONE") then
    local tx, tz = origin_for(runway_x - 1, hi.z2 - 1, 3, 2, 2)
    throne = try_place(ctx, "THRONE", tx, tz, 2)
    if not throne then
      local ok = try_near(ctx, "THRONE", tx, tz, 2, 1, hi)
      throne = ok
    end
  end
  if not throne then ctx:refuse("THRONE", "the throne did not seat on the dais - this is not a palace hall without it") end
  -- banners either side of the throne, braziers at the foot of the dais
  for _, dx in ipairs({ -3, 3 }) do
    try_near(ctx, "BANNER", runway_x + dx, hi.z2, 0, 1, hi)
    try_near(ctx, "BRAZIER", runway_x + dx - (dx > 0 and 1 or -1), hi.z2 - 3, 0, 1, hi)
  end
  -- holo-dancers just off the dais, facing the runway
  for _, dx in ipairs(shuffle({ -4, 4 })) do
    if rng.chance(0.8) then try_near(ctx, "HOLO", runway_x + dx, hi.z2 - 4, dx > 0 and 3 or 1, 1, hi) end
  end

  -- the colonnade: two rows of columns, the roof's support and the hall's rhythm
  local cols = 0
  if ctx:has_role("PILLAR") and hi.h > 8 then
    local col_dx = math.max(5, math.floor(hi.w / 4))
    local z0 = hi.z + 2
    while z0 <= hi.z2 - 4 do
      for _, x in ipairs({ hi.x + col_dx, hi.x2 - col_dx }) do
        if try_place(ctx, "PILLAR", x, z0, 0) then cols = cols + 1 end
      end
      z0 = z0 + 4
    end
  end

  -- the band corner: nalargon, bandfill, a music holo
  do
    local corner = rng.pick({ "W", "E" })
    local bx = (corner == "W") and (hi.x + 1) or (hi.x2 - 2)
    local bz = hi.z + 1
    try_near(ctx, "INSTRUMENT_BIG", bx, bz, 0, 1, hi)
    try_near(ctx, "INSTRUMENT", bx + ((corner == "W") and 3 or -3), bz, 0, 1, hi)
    try_near(ctx, "HOLO_BAND", bx + ((corner == "W") and 1 or -1), bz + 3, (corner == "W") and 1 or 3, 1, hi)
  end
  -- the pazaak game off the runway on the other side
  along_wall(ctx, "GAME", hi, rng.pick({ "W", "E" }), 1)

  -- guests' furniture along the walls, never on the runway
  local avoid_runway = function(x, z) return in_rect(x, z, runway) or in_rect(x, z, dais) end
  local guest = 0
  guest = guest + along_wall(ctx, "TABLE_SMALL", hi, "W", rng.int(1, 2), { gap = 2 })
  guest = guest + along_wall(ctx, "TABLE_SMALL", hi, "E", rng.int(1, 2), { gap = 2 })
  guest = guest + scatter(ctx, "STOOL", inner(hi, 1), rng.int(4, 6), { avoid = avoid_runway, rot = "any" })
  dress(ctx, hi, {
    { role = "PLANT_POT",  n = { 3, 5 }, where = "wall" },
    { role = "LIGHT_TALL", n = { 2, 3 }, where = "corner" },
    { role = "LIGHT",      n = { 1, 2 }, where = "wall" },
  })
  wall_lights(ctx, hi, rng.int(3, 5))
  note(string.format("palace hall: throne %s, %d column(s), %d guest table(s)/stool(s), band corner, pazaak",
    throne and "on the dais" or "MISSING", cols, guest))

  -- ---- the lord's chamber ---------------------------------------------------
  do
    floor_patch(ctx, inner(ci, 1), "RUG", ci)
    local bed = along_wall(ctx, "BED_FINE", ci, rng.pick({ "N", "W" }), 1, { face = "wall" })
    if bed == 0 then along_wall(ctx, "BED", ci, "W", 1, { face = "wall" }) end
    dress(ctx, ci, {
      { role = "DRESSER",   n = 1,        where = "wall" },
      { role = "END_TABLE", n = { 1, 2 }, where = "wall" },
      { role = "TUB",       n = 1,        where = "corner" },
      { role = "DECOR",     n = 1,        where = "corner" },
      { role = "PLANT_POT", n = { 1, 2 }, where = "wall" },
      { role = "LIGHT",     n = 1,        where = "corner" },
    })
    wall_lights(ctx, ci, rng.int(1, 2))
  end

  -- ---- the vestibule: where a guest is made to wait -------------------------
  do
    along_wall(ctx, "STOOL", vi, rng.pick({ "W", "E" }), rng.int(1, 2), { gap = 1 })
    dress(ctx, vi, {
      { role = "PLANT_POT", n = 1, where = "corner" },
      { role = "BRAZIER",   n = 1, where = "corner" },
    })
    if ctx:has_role("SIGN_CHAMBER") then ctx:place_overlay("SIGN_CHAMBER", runway_x, vi.z2, 0) end
    wall_lights(ctx, vi, 1)
  end

  -- ---- the majordomo's office: the ledger the palace runs on -----------------
  do
    local ok, dx, dz = try_near(ctx, "DESK", oi.x + math.floor(oi.w / 2), oi.z2 - 1, 2, 2, oi)
    if ok then try_near(ctx, "CHAIR", dx, dz - 1, 0, 1, oi) end
    along_wall(ctx, "STORAGE", oi, rng.pick({ "E", "W" }), rng.int(1, 2), { gap = 1 })
    dress(ctx, oi, {
      { role = "TERMINAL",    n = 1,        where = "wall" },
      { role = "SHELF_SMALL", n = { 1, 2 }, where = "wall" },
      { role = "CRATE",       n = { 1, 2 }, where = "corner" },
      { role = "STOOL",       n = 1 },
      { role = "LIGHT",       n = 1,        where = "corner" },
    })
    wall_lights(ctx, oi, 1)
  end

  note("security props: none in the hall itself - the palace is guarded at its gate (cistern court, holding pens)")
end
