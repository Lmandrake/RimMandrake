-- droid_fabrication_room.lua - where the enclave makes more of itself: a shop
-- floor with a droid factory and machining benches, and a parts store beside
-- it full of crates, component stacks and salvage. DISTRICT_TEMPLATE_LIBRARY_1,
-- Free Droid Enclaves district #3 (The Cracking Yard manifest slot
-- "fabrication room").
--
-- CANON: faction_roster_v2.md, Free Droid Enclaves "Technology and economy":
-- "fabrication room"; "a memory of being property that they intend never to
-- repeat" (FactionDef) - what they build here is free the moment it boots.
-- The factory is Outer Rim's OuterRim_DroidFactory (3x2); benches are
-- vanilla machining tables.
--
-- Built to the owner's live-review bar (TILE_STRUCTURE_REVIEW_SAVE_1):
--   FLOORING   vented steel (FLOOR_WORK) on the shop floor, grating (FLOOR)
--              in the parts store.
--   GRIDS      benches and the factory hug walls at random slots; parts
--              scatter; crates hug the store's walls with gaps.
--   CLUTTER    component and steel stacks, slag, small fuel tanks, crates
--              wide and narrow, terminals, a screen, wall lamps, a WORKSHOP
--              sign at the door and a STORAGE sign at the store's.
-- --tech Spacer (FactionDef techLevel).

function min_rect(params)
  return 16, 12
end

function build(ctx)
  local w, h = rect.w, rect.h
  if w < 16 or h < 12 then
    ctx:refuse("footprint", string.format("%dx%d too small for a shop floor (>=10 wide) plus a parts store", w, h))
    return
  end
  local store_w = 7
  local shop = R(rect.x, rect.z, w - store_w + 1, h)
  local store = R(shop.x2, rect.z, store_w, h)
  local si = shell(ctx, "Fabrication", shop, { floor = "FLOOR_WORK", doors = { { "S", rng.int(3, shop.w - 4) } } })
  local ti = shell(ctx, "Storeroom", store, { floor = "FLOOR" })
  ctx:door(store.x, store.z + rng.int(2, store.h - 3))

  -- ---- the shop floor -------------------------------------------------------
  local fab = along_wall(ctx, "FABRICATOR", si, rng.pick({ "N", "W" }), 1)
  if fab == 0 then fab = scatter(ctx, "FABRICATOR", inner(si, 1), 1, { tries = 40 }) end
  local benches = 0
  for _, side in ipairs(shuffle({ "N", "W", "E" })) do
    if benches >= 2 then break end
    benches = benches + along_wall(ctx, "WORKBENCH", si, side, 2 - benches, { gap = 1 })
  end
  along_wall(ctx, "STORAGE", si, rng.pick({ "E", "W" }), 1)
  dress(ctx, si, {
    { role = "TERMINAL",        n = { 1, 2 }, where = "wall" },
    { role = "SCREEN",          n = { 0, 1 }, where = "wall" },
    { role = "COMPONENT",       n = { 1, 3 } },
    { role = "SCRAP",           n = { 1, 3 } },
    { role = "FUEL_TANK_SMALL", n = { 0, 1 }, where = "corner" },
    { role = "CRATE",           n = { 1, 2 }, where = "corner" },
    { role = "LIGHT",           n = { 1, 2 }, where = "corner" },
  })
  wall_lights(ctx, si, rng.int(2, 3))
  if ctx:has_role("SIGN_WORKSHOP") then ctx:place_overlay("SIGN_WORKSHOP", si.x + math.floor(si.w / 2), si.z, 0) end
  note(string.format("fabrication: factory %s, %d machining bench(es)", fab > 0 and "on the wall" or "MISSING", benches))

  -- ---- the parts store ---------------------------------------------------------
  along_wall(ctx, "STORAGE", ti, rng.pick({ "N", "E" }), rng.int(1, 2), { gap = 1 })
  dress(ctx, ti, {
    { role = "CRATE",      n = { 2, 4 }, where = "wall" },
    { role = "CRATE_WIDE", n = { 0, 1 }, where = "wall" },
    { role = "STEEL",      n = { 1, 2 } },
    { role = "COMPONENT",  n = { 1, 2 } },
    { role = "LIGHT",      n = 1,        where = "corner" },
  })
  wall_lights(ctx, ti, 1)
  if ctx:has_role("SIGN_STORAGE") then ctx:place_overlay("SIGN_STORAGE", ti.x + 1, ti.z + rng.int(1, ti.h - 2), 1) end
  note("security props: none - the shop is inside the enclave's wall")
end
