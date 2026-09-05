-- hutt_spicehouse.lua - a Hutt spice den: the smoking room out front (low
-- tables and stools on rugs, a holo-dancer, braziers) and the lab behind it
-- where the product is cut. DISTRICT_TEMPLATE_LIBRARY_1, Hutt Cartel district
-- #2 (Gorga the Immense's Palace manifest slot "spicehouse").
--
-- CANON: faction_roster_v2.md, Hutt Cartel "Technology and economy": "drug
-- labs"; the frozen world map names "Vexxa's Spicehouse" and "Rulla's
-- Skimhouse" as deep-desert Cartel posts (world/ASHKARR_WORLDMAP_settlements.csv
-- rows 104-105) - this is what one of those looks like folded into a palace.
--
-- Built to the owner's live-review bar (TILE_STRUCTURE_REVIEW_SAVE_1):
--   FLOORING   den: sandstone tile under burgundy rugs; lab: concrete.
--   GRIDS      every table, stool, barrel and lab bench lands by seeded
--              scatter or wall-hugging with gaps.
--   CLUTTER    braziers, barrels, crates, spice stacks on the lab floor,
--              a dancer holo, wall lamps, Aurebesh signs over the doors.
-- --tech Industrial (Hutt FactionDef techLevel).

function min_rect(params)
  return 14, 14
end

function build(ctx)
  local w, h = rect.w, rect.h
  if w < 14 or h < 14 then
    ctx:refuse("footprint", string.format("%dx%d too small for a den (>=8 rows) plus a lab (7 rows)", w, h))
    return
  end
  local lab_h = 7
  local den = R(rect.x, rect.z, w, h - lab_h + 1)
  local lab = R(rect.x, den.z2, w, lab_h)

  local di = shell(ctx, "Den", den, { floor = "FLOOR", doors = { { "S", rng.int(3, w - 4) } } })
  local li = shell(ctx, "DrugLab", lab, { floor = "FLOOR_WORK" })
  -- the lab is entered from the den, and has its own back door
  local lab_door_x = lab.x + rng.int(2, w - 3)
  ctx:door(lab_door_x, lab.z)
  door_on(ctx, lab, rng.pick({ "N", "E", "W" }))

  -- ---- the den ---------------------------------------------------------------
  -- two or three rugs, each with a low table and stools pulled up around it
  local rugs = 0
  for i = 1, rng.int(2, 3) do
    local rw, rh = rng.int(3, 4), rng.int(3, 4)
    local rx = rng.int(di.x, di.x2 - rw + 1)
    local rz = rng.int(di.z + 1, di.z2 - rh)
    local rug = R(rx, rz, rw, rh)
    floor_patch(ctx, rug, "RUG", di)
    local cx, cz = center(rug)
    local ok, tx, tz = try_near(ctx, "TABLE_SMALL", cx, cz, 0, 1, rug)
    if ok then
      rugs = rugs + 1
      local seats = 0
      for _, c in ipairs(shuffle({ { tx - 1, tz, 1 }, { tx + 1, tz, 3 }, { tx, tz - 1, 0 }, { tx, tz + 1, 2 } })) do
        if seats >= rng.int(2, 3) then break end
        if in_rect(c[1], c[2], di) and not blocks_a_door(ctx, c[1], c[2], di)
           and try_place(ctx, "STOOL", c[1], c[2], c[3]) then seats = seats + 1 end
      end
    end
  end
  -- a dancer on a plinth of fine tile in one corner, braziers, barrels, plants
  do
    local side = rng.pick({ "W", "E" })
    local hx = (side == "W") and (di.x + 1) or (di.x2 - 1)
    local ok, px, pz = try_near(ctx, "HOLO", hx, di.z2 - 1, (side == "W") and 1 or 3, 1, di)
    if ok then floor_patch(ctx, R(px - 1, pz - 1, 3, 3), "FLOOR_FINE", di) end
  end
  dress(ctx, di, {
    { role = "BRAZIER",   n = { 1, 2 }, where = "corner" },
    { role = "BARREL",    n = { 1, 2 }, where = "wall" },
    { role = "PLANT_POT", n = { 1, 2 }, where = "wall" },
    { role = "CRATE",     n = { 0, 1 }, where = "corner" },
    { role = "LIGHT",     n = 1,        where = "corner" },
  })
  wall_lights(ctx, di, rng.int(2, 3))
  if ctx:has_role("SIGN_RELAX") then ctx:place_overlay("SIGN_RELAX", lab_door_x - 1, di.z2, 0) end
  note(string.format("spice den: %d rug(s) with a low table and stools each, dancer holo, braziers", rugs))

  -- ---- the lab ---------------------------------------------------------------
  local benches = along_wall(ctx, "DRUG_LAB", li, rng.pick({ "N", "E", "W" }), rng.int(1, 2), { gap = 1 })
  along_wall(ctx, "STORAGE", li, rng.pick({ "N", "E", "W" }), rng.int(1, 2), { gap = 1 })
  dress(ctx, li, {
    { role = "CRATE",       n = { 2, 3 }, where = "wall" },
    { role = "CRATE_WIDE",  n = { 0, 1 }, where = "wall" },
    { role = "SPICE",       n = { 2, 4 } },
    { role = "SHELF_SMALL", n = { 0, 1 }, where = "wall" },
    { role = "TERMINAL",    n = { 0, 1 }, where = "corner" },
    { role = "STOOL",       n = 1 },
    { role = "LIGHT",       n = 1,        where = "corner" },
  })
  wall_lights(ctx, li, rng.int(1, 2))
  if ctx:has_role("SIGN_STORAGE") then ctx:place_overlay("SIGN_STORAGE", li.x + rng.int(1, li.w - 2), li.z, 0) end
  note(string.format("lab: %d drug bench(es), shelving, crates, spice on the floor", benches))

  note("security props: none here - the den wants custom, and the palace gate does the searching")
end
