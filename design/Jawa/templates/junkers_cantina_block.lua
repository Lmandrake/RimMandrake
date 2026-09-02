-- junkers_cantina_block.lua - one building, two rooms: a main hall (bar
-- shelving, two rounds of tables and chairs) and the keeper's back room.
-- DISTRICT_TEMPLATE_LIBRARY_1, Junkers district #3 (The Claim Jump manifest
-- slot "cantina block").
--
-- WHAT THIS FILE DEMONSTRATES:
--   * the shared-wall two-bay split from dwelling.lua, reused for an
--     UNEQUAL split (a small back room, not three equal bays)
--   * one door serving two rooms at once (the shared wall row), same
--     idiom dwelling.lua documents for its interior doors
--   * banded furniture placement (place_role_fit per horizontal band)
--     as the simplest way to get "more than one" of a role without a
--     hand-rolled grid walk
--
-- Reused art only: WALL/DOOR/BED/LIGHT/STORAGE/TABLE/CHAIR/DECOR all
-- resolve through the existing palette. --tech Neolithic, same as the
-- other three Junkers districts - no powered fixtures.

-- The declared canvas floor; the engine checks it before build() runs
-- (TEMPLATE_CANVAS_UNDECLARED_1). `rimplace minrect junkers_cantina_block`.
-- From build()'s own arithmetic: main_h = h - keeper_h + 1 >= 8, keeper_h = 6.
function min_rect(params)
  return 10, 13
end

function build(ctx)
  local p = params
  local w, h = rect.w, rect.h

  local keeper_h = 6
  local main_h = h - keeper_h + 1  -- +1: the shared wall row
  if main_h < 8 or w < 10 then
    ctx:refuse("footprint", string.format(
      "%dx%d too small for a cantina hall (>=10 wide) plus a %d-row keeper's room",
      w, h, keeper_h))
    return
  end

  local keeperBay = { x = rect.x, z = rect.z, w = w, h = keeper_h }
  local mainBay = { x = rect.x, z = rect.z + keeper_h - 1, w = w, h = main_h }

  ctx:room("Cantina", mainBay.x, mainBay.z, mainBay.w, mainBay.h, true)
  ctx:wall_rect(mainBay.x, mainBay.z, mainBay.w, mainBay.h)
  ctx:room("Storeroom", keeperBay.x, keeperBay.z, keeperBay.w, keeperBay.h, true)
  ctx:wall_rect(keeperBay.x, keeperBay.z, keeperBay.w, keeperBay.h)

  -- one interior door in the shared wall row serves both rooms at once
  local midX = rect.x + math.floor(w / 2)
  ctx:door(midX, keeperBay.z + keeper_h - 1)
  -- exterior door on the hall's far wall
  ctx:door(midX, mainBay.z + mainBay.h - 1)

  -- ---- main hall: bar shelving along the back, two rounds of seating -----
  local ix, iz, iw, ih = mainBay.x + 1, mainBay.z + 1, mainBay.w - 2, mainBay.h - 2
  if ctx:has_role("STORAGE") then
    local sw = ctx:width_of("STORAGE")
    local xx = ix
    while xx <= ix + iw - sw do
      ctx:place_role("STORAGE", xx, iz)
      xx = xx + sw
    end
  end
  local band_h = math.max(2, math.floor((ih - 1) / 2))
  local bands = {
    { x = ix, z = iz + 1, w = iw, h = band_h },
    { x = ix, z = iz + 1 + band_h, w = iw, h = ih - 1 - band_h },
  }
  local rounds = 0
  for _, bnd in ipairs(bands) do
    if bnd.h > 0 then
      if ctx:has_role("TABLE") and ctx:place_role_fit("TABLE", bnd.x, bnd.z, bnd.w, bnd.h) then
        rounds = rounds + 1
      end
      if ctx:has_role("CHAIR") then ctx:place_role_fit("CHAIR", bnd.x, bnd.z, bnd.w, bnd.h) end
    end
  end
  if ctx:has_role("LIGHT") then ctx:place_role_fit("LIGHT", ix, iz, iw, ih) end
  if (p.wealth == "rich" or p.wealth == "comfortable") and ctx:has_role("DECOR") then
    ctx:place_role_fit("DECOR", ix, iz, iw, ih)
  end
  note(string.format("cantina hall: %d round(s) of tables/seating, bar shelving along the back wall", rounds))

  -- ---- keeper's back room: the one person who lives on-site --------------
  local kx, kz, kw, kh = keeperBay.x + 1, keeperBay.z + 1, keeperBay.w - 2, keeperBay.h - 2
  if ctx:has_role("BED") then ctx:place_role_fit("BED", kx, kz, kw, kh) end
  if ctx:has_role("STORAGE") then ctx:place_role_fit("STORAGE", kx, kz, kw, kh) end
  if ctx:has_role("LIGHT") then ctx:place_role_fit("LIGHT", kx, kz, kw, kh) end

  -- ---- security: NONE ------------------------------------------------------
  -- Same ruling as junkers_scrapyard.lua: The Claim Jump's manifest sets
  -- searchesLeavers=false. A cantina is exactly the kind of room a HIGHER
  -- security profile would put a "watcher" cast slot or a fixed camera
  -- over (this is the classic overheard-rumour room, ownership_settlement_spec.md
  -- item 6); for Junkers it deliberately gets neither.
  note("no security props placed: Junkers/The Claim Jump is low security by design (searchesLeavers=false)")
end
