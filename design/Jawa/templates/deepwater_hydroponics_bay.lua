-- deepwater_hydroponics_bay.lua - the Compact's growing room: sun lamps with
-- hydroponics basins clustered under each, a cooler in the wall to hold the
-- room, water troughs and basins, and the nutrient casks and crates of a
-- working bay. DISTRICT_TEMPLATE_LIBRARY_1, Deepwater Compact district #4
-- (Deepwater Hold manifest slot "hydroponics bay", required=false).
--
-- CANON (faction_roster_v2.md, Deepwater Compact "Technology and economy"):
-- "hydroponics, refrigeration"; the only faction on a desert world that can
-- afford to grow under lamps, because it owns the water they drink.
--
-- Built to the owner's live-review bar (TILE_STRUCTURE_REVIEW_SAVE_1):
--   FLOORING   off-white divoted tile (FLOOR_WORK), mosaic (FLOOR_WET) under
--              each lamp's cluster.
--   GRIDS      basins are NOT rows: each sun lamp gets a loose cluster of
--              basins at mixed rotations scattered around it.
--   CLUTTER    troughs, a basin, casks, crates, a terminal, plant pots by the
--              door, wall lamps, a FARMING sign. A COOLER sits IN the north
--              wall (ctx:wall_mount, rot 0: cold side in) - unpowered here,
--              like every powered fixture in this library, and honest about it.
-- --tech Industrial (FactionDef techLevel).

function min_rect(params)
  return 16, 14
end

function build(ctx)
  local w, h = rect.w, rect.h
  if w < 16 or h < 14 then
    ctx:refuse("footprint", string.format("%dx%d too small for two lamp clusters and a working aisle", w, h))
    return
  end
  local bay = R(rect.x, rect.z, w, h)
  local bi = shell(ctx, "Hydroponics", bay, { floor = "FLOOR_WORK", doors = { { "S", rng.int(3, w - 4) } } })
  local cols = support_columns(ctx, bi)

  -- ---- lamps, each with its cluster of basins --------------------------------
  local n_lamps = (bi.w >= 20) and 3 or 2
  local lamps, basins = 0, 0
  local step = math.floor(bi.w / n_lamps)
  for i = 0, n_lamps - 1 do
    local lx = bi.x + i * step + math.floor(step / 2) + rng.int(-1, 1)
    local lz = bi.z + math.floor(bi.h / 2) + rng.int(-2, 2)
    if try_place(ctx, "SUNLAMP", lx, lz, 0) then
      lamps = lamps + 1
      local zone = R(lx - 3, lz - 3, 7, 7)
      floor_patch(ctx, zone, "FLOOR_WET", bi)
      basins = basins + scatter(ctx, "HYDRO", zone, rng.int(3, 5), { rot = "any", tries = 60 })
    end
  end
  note(string.format("hydroponics: %d sun lamp(s), %d basin(s) clustered under them, %d roof column(s)", lamps, basins, cols))

  -- ---- the cooler in the north wall, cold side in ------------------------------
  if ctx:has_role("COOLER") then
    local cx = bi.x + rng.int(2, bi.w - 3)
    ctx:wall_mount("COOLER", cx, bay.z2, 0)
    note("cooler in the north wall at rot 0 (cold side in); no power modelled - the layout-layers lint applies live")
  end

  -- ---- water and the working clutter ---------------------------------------------
  local troughs = scatter(ctx, "TROUGH", inner(bi, 1), rng.int(1, 2), { rot = "any", tries = 40 })
  along_wall(ctx, "BASIN", bi, rng.pick({ "E", "W" }), 1)
  along_wall(ctx, "STORAGE", bi, rng.pick({ "E", "W" }), rng.int(1, 2), { gap = 1 })
  dress(ctx, bi, {
    { role = "BARREL",    n = { 2, 3 }, where = "wall" },
    { role = "CRATE",     n = { 1, 2 }, where = "corner" },
    { role = "PLANT_POT", n = { 1, 2 }, where = "wall" },
    { role = "TERMINAL",  n = { 0, 1 }, where = "corner" },
    { role = "STOOL",     n = { 0, 1 } },
    { role = "LIGHT",     n = 1,        where = "corner" },
  })
  wall_lights(ctx, bi, rng.int(2, 3))
  if ctx:has_role("SIGN_FARMING") then ctx:place_overlay("SIGN_FARMING", bi.x + math.floor(bi.w / 2), bi.z, 0) end
  note(string.format("%d trough(s), casks and crates along the walls", troughs))
  note("security props: none - inside the hold's wall")
end
