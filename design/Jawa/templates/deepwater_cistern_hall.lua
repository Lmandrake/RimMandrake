-- deepwater_cistern_hall.lua - the Compact's export made into a building: a
-- columned hall around a purification floor where the water stands in tanks
-- and basins on mosaic tile, the intake well against the back wall, casks
-- and crates of the trade along the sides, and the warden's office in a
-- corner watching all of it. DISTRICT_TEMPLATE_LIBRARY_1, Deepwater Compact
-- district #1 (Deepwater Hold manifest slot "cistern hall").
--
-- CANON (faction_roster_v2.md, Deepwater Compact "Technology and economy"):
-- "purification, desalination, and cistern infrastructure - the faction's
-- export"; "Techist + Totemic - clean infrastructure married to ritual
-- reverence for the cistern"; "The amphibian peoples who live in the deep
-- water and sell it to everyone" (FactionDef). The world map's Deepwater
-- Hold sits on "the Twilight Sea, the largest standing water on Ash'karr".
--
-- Built to the owner's live-review bar (TILE_STRUCTURE_REVIEW_SAVE_1):
--   FLOORING   sterile tile (FLOOR) everywhere, a mosaic apron (FLOOR_WET)
--              under the water, paneled steel (FLOOR_FINE) in the office.
--   GRIDS      the colonnade is the ONE regular thing - a hall this size
--              needs it (rimplace lint rule 6) and reverence for the cistern
--              earns it; tanks cluster, basins and casks hug walls at random
--              slots, troughs and crates scatter.
--   CLUTTER    basins, a sink, troughs, casks, crates, plant pots, terminals
--              and a screen, standing lamps, wall lamps, a STORAGE sign.
-- Security props: none inside - the Compact's teeth are at the gate
-- (deepwater_gate_bastion.lua).
-- --tech Industrial (FactionDef techLevel).

function min_rect(params)
  return 18, 16
end

function build(ctx)
  local w, h = rect.w, rect.h
  if w < 18 or h < 16 then
    ctx:refuse("footprint", string.format("%dx%d too small for a cistern hall with a purification floor and an office", w, h))
    return
  end
  local hall = R(rect.x, rect.z, w, h)
  local hi = shell(ctx, "Cistern", hall, { floor = "FLOOR", doors = { { "S", rng.int(4, w - 5) } } })
  door_on(ctx, hall, rng.pick({ "E", "W" }))

  -- ---- the warden's office in the south-east corner ------------------------
  local ow, oh = 7, 6
  local office = R(hall.x2 - ow, hall.z, ow, oh)
  local oi = shell(ctx, "Office", office, { floor = "FLOOR_FINE" })
  ctx:door(office.x, office.z + rng.int(2, oh - 3))
  local keep = { R(office.x - 2, office.z, office.w + 2, office.h + 2) }

  -- ---- the colonnade --------------------------------------------------------
  local cols = support_columns(ctx, hi)

  -- ---- the purification floor: tanks and fountains on mosaic ----------------
  local cx = hi.x + math.floor((hi.w - ow) / 2) + rng.int(-1, 1)
  local cz = hi.z + math.floor(hi.h / 2) + rng.int(-1, 1)
  local apron = R(cx - 4, cz - 3, 9, 7)
  floor_patch(ctx, apron, "FLOOR_WET", hi)
  -- E6 `aisle-blocked`: reject a candidate cell with no free cardinal side -
  -- a tank cluster this dense (6-9 in a 7x5 patch) can otherwise wall a tank
  -- in on all four sides with other tanks, leaving nothing to flood-fill
  -- reach it from.
  -- Margin of TWO free sides, not one: a single free neighbour at placement
  -- time is exactly the cell a LATER scatter (troughs, crates) can still
  -- seal shut, which is what one-side-open let through the first time.
  local function too_boxed_in(x, z)
    local open = 0
    for _, d in ipairs({ { 0, 1 }, { 0, -1 }, { 1, 0 }, { -1, 0 } }) do
      if not ctx:occupied(x + d[1], z + d[2]) then open = open + 1 end
    end
    return open < 2
  end
  local tanks = scatter(ctx, "WATER_TANK", R(cx - 3, cz - 2, 7, 5), rng.int(6, 9),
    { tries = 120, avoid = too_boxed_in })
  local basins = scatter(ctx, "FOUNTAIN", apron, rng.int(1, 2), { tries = 40 })
  keep[#keep + 1] = R(apron.x - 1, apron.z - 1, apron.w + 2, apron.h + 2)
  -- the intake well against the back wall, on its own square of mosaic
  local wx = hi.x + rng.int(3, hi.w - 4)
  floor_patch(ctx, R(wx - 1, hi.z2 - 2, 3, 3), "FLOOR_WET", hi)
  local well = try_near(ctx, "WELL", wx, hi.z2 - 1, 0, 1, hi) and 1 or 0

  -- ---- the trade along the walls -----------------------------------------------
  basins = basins + along_wall(ctx, "BASIN", hi, "W", rng.int(1, 2), { gap = 2 })
  basins = basins + along_wall(ctx, "BASIN", hi, "N", rng.int(1, 2), { gap = 2 })
  along_wall(ctx, "SINK", hi, rng.pick({ "N", "W" }), 1)
  local casks = along_wall(ctx, "BARREL", hi, "E", rng.int(2, 4), { gap = 0 })
  casks = casks + along_wall(ctx, "BARREL", hi, "W", rng.int(1, 2), { gap = 0 })
  local troughs = scatter(ctx, "TROUGH", R(hi.x + 1, hi.z, hi.w - ow - 2, 4), rng.int(1, 2), { rot = "any", keep_clear = keep })
  dress(ctx, hi, {
    { role = "CRATE_WIDE", n = { 1, 2 }, where = "wall" },
    { role = "CRATE",      n = { 2, 3 }, where = "wall" },
    { role = "PLANT_POT",  n = { 2, 3 }, where = "wall" },
    { role = "TERMINAL",   n = { 1, 2 }, where = "wall" },
    { role = "SCREEN",     n = { 0, 1 }, where = "wall" },
    { role = "LIGHT",      n = { 2, 3 }, where = "corner" },
  })
  scatter(ctx, "LIGHT", inner(hi, 2), 2, { keep_clear = keep })
  wall_lights(ctx, hi, rng.int(4, 6))
  if ctx:has_role("SIGN_STORAGE") then ctx:place_overlay("SIGN_STORAGE", hi.x2 - ow - 2, hi.z2, 0) end
  note(string.format("cistern hall: %d tank(s) and %d basin(s)/fountain(s) on the mosaic, intake well %d, %d cask(s), %d trough(s), %d column(s)",
    tanks, basins, well, casks, troughs, cols))

  -- ---- the warden's office ------------------------------------------------------
  do
    local ok, dx, dz = try_near(ctx, "DESK", oi.x + 2, oi.z2 - 1, 2, 1, oi)
    if ok then try_near(ctx, "CHAIR", dx, dz - 1, 0, 1, oi) end
    along_wall(ctx, "STORAGE", oi, "E", 1)
    dress(ctx, oi, {
      { role = "TERMINAL",    n = 1,        where = "corner" },
      { role = "SHELF_SMALL", n = { 0, 1 }, where = "wall" },
      { role = "LIGHT",       n = 1,        where = "corner" },
    })
    wall_lights(ctx, oi, 1)
  end
  note("security props: none in the hall - the Compact's teeth are at the gate bastion")
end
