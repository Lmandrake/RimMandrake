-- dwelling.lua - a one, two or three room domicile.
--
-- The owner's worked example, 2026-08-22:
--   "a fairly simple call that can produce a one room, two room, or three room
--    domicile from a given faction in an area."
--
-- WHAT THIS FILE DEMONSTRATES, and why it is Lua rather than data:
--   * it BRANCHES on faction canon (droids get no beds; Wildsteam gets no walls)
--   * it SIZES rooms from occupants rather than hardcoding a rect
--   * it is deterministic under a seed, so a bug is reproducible
--   * you can edit it and see the new house in milliseconds, no game load
--
-- API available: ctx (see luaenv.Ctx), rect, params, rng, role(), note()

-- ---------------------------------------------------------------------------
-- helpers
-- ---------------------------------------------------------------------------

-- Split a rect into n vertical bays, each at least min_w wide.
-- Returns nil if it cannot be done - REFUSING beats silently making 2 rooms
-- when 3 were asked for.
local function split_bays(x, z, w, h, n, min_w)
  if n < 1 then return nil end
  -- interior walls are shared, so n rooms need n+1 wall columns
  local usable = w - (n + 1)
  if usable < n * min_w then return nil end
  local each = math.floor(usable / n)
  local bays, cx = {}, x
  for i = 1, n do
    local bw = (i == n) and (w - (cx - x) - 1) or (each + 1)
    bays[#bays + 1] = { x = cx, z = z, w = bw + 1, h = h }
    cx = cx + bw
  end
  return bays
end

local function room_role_for(i, n, p)
  if p.faction == "Jawa_FreeDroidEnclaves" then
    return ({ "ChargingHall", "Fabrication", "Storeroom" })[i] or "Room"
  end
  if n == 1 then return "Barracks" end
  if i == 1 then return (p.occupants and p.occupants > 1) and "Barracks" or "Bedroom" end
  if i == 2 then return "DiningRoom" end
  return "Storeroom"
end

-- ---------------------------------------------------------------------------
-- the entry point
-- ---------------------------------------------------------------------------
function build(ctx)
  local p = params
  local n = math.max(1, math.min(3, p.rooms or 1))
  local occ = p.occupants or 1

  -- ---- canon branch: the Wildsteam Clan do not wall their settlements -----
  -- "open tree-integrated settlements ... minimal turrets due to ideology"
  local unwalled = (p.faction == "Jawa_WildsteamClan")

  -- ---- size the footprint we will actually use ---------------------------
  local min_w = 4
  local bays = split_bays(rect.x, rect.z, rect.w, rect.h, n, min_w)
  if not bays then
    ctx:refuse("footprint",
      string.format("%dx%d cannot hold %d rooms of at least %d wide",
                    rect.w, rect.h, n, min_w))
    return
  end

  -- ---- shell -------------------------------------------------------------
  for i, b in ipairs(bays) do
    local rrole = room_role_for(i, n, p)
    ctx:room(rrole, b.x, b.z, b.w, b.h, true)
    if not unwalled then
      ctx:wall_rect(b.x, b.z, b.w, b.h)
    end
  end

  -- ---- doors -------------------------------------------------------------
  -- one exterior door on the south face of bay 1, then interior doors linking
  -- each bay to the next. Every room must be reachable or the linter fails it.
  local b1 = bays[1]
  ctx:door(b1.x + math.floor(b1.w / 2), b1.z)
  for i = 2, #bays do
    local b = bays[i]
    ctx:door(b.x, b.z + math.floor(b.h / 2))
  end
  if unwalled then
    -- with no walls there is nothing to seal; say so rather than letting the
    -- linter report six mystery findings
    note("Wildsteam: unwalled by ideology - sealed-room checks do not apply")
  end

  -- ---- furnish -----------------------------------------------------------
  local beds_needed = occ
  for i, b in ipairs(bays) do
    local ix, iz = b.x + 1, b.z + 1
    local iw, ih = b.w - 2, b.h - 2
    local rrole = room_role_for(i, n, p)

    if rrole == "Bedroom" or rrole == "Barracks" then
      -- CANON BRANCH: the Free Droid Enclaves have no beds at all.
      if ctx:has_role("BED") then
        local placed = 0
        for zz = iz, iz + ih - 1, 2 do
          for xx = ix, ix + iw - 1, 2 do
            if placed >= beds_needed then break end
            if not ctx:occupied(xx, zz) then
              ctx:place_role("BED", xx, zz)
              placed = placed + 1
            end
          end
          if placed >= beds_needed then break end
        end
        beds_needed = beds_needed - placed
        if beds_needed > 0 then
          ctx:refuse("BED", string.format(
            "%d of %d beds did not fit in the sleeping room", beds_needed, occ))
        end
      else
        note("faction has no BED in its palette - sleeping room left empty")
      end

    elseif rrole == "DiningRoom" then
      -- FOOTPRINTS, not cells. A table is 1x2 and a stove 3x1 in the vanilla
      -- palette, so the old layout put the chair INSIDE the table and the
      -- stove through the wall: build_batch wiped both and reported them
      -- placed (TEMPLATE_FOOTPRINT_IGNORES_SIZE_1). place_role_fit scans.
      if ctx:has_role("TABLE") then ctx:place_role_fit("TABLE", ix, iz, iw, ih) end
      if ctx:has_role("CHAIR") then ctx:place_role_fit("CHAIR", ix, iz, iw, ih) end
      if ctx:has_role("STOVE") then
        -- from the far corner backwards, so the stove keeps its traditional
        -- spot when it fits and slides inward when it does not
        local placed = false
        for zz = iz + ih - 1, iz, -1 do
          for xx = ix + iw - 1, ix, -1 do
            if ctx:can_place("STOVE", xx, zz) then
              ctx:place_role("STOVE", xx, zz); placed = true; break
            end
          end
          if placed then break end
        end
        if not placed then
          ctx:refuse("STOVE", "no cell in the dining room fits its footprint")
        end
      end

    else
      if ctx:has_role("STORAGE") then
        -- step by the shelf's own WIDTH. Three 2x1 shelves on a 1-cell stride
        -- overlap, and the map kept only the last one.
        local sw = ctx:width_of("STORAGE")
        local xx = ix
        while xx <= ix + math.min(iw, 3 * sw) - 1 do
          if ctx:can_place("STORAGE", xx, iz) then
            ctx:place_role("STORAGE", xx, iz)
          end
          xx = xx + sw
        end
      end
    end

    -- light LAST, into whatever cell is still free. Ordering matters: the
    -- linter caught the light claiming the stove's corner when it went first,
    -- and the light is the piece that can go anywhere.
    -- ⚠️ can_place, not occupied(): occupied() answers for ONE cell, and the
    -- stove that had already claimed this corner is 3 cells wide, so the light
    -- read the corner as free and was placed inside it.
    if ctx:has_role("LIGHT") then
      local lit = false
      for zz = b.z + b.h - 2, b.z + 1, -1 do
        for xx = b.x + b.w - 2, b.x + 1, -1 do
          if ctx:can_place("LIGHT", xx, zz) then
            ctx:place_role("LIGHT", xx, zz); lit = true; break
          end
        end
        if lit then break end
      end
      if not lit then ctx:refuse("LIGHT", "no free cell in this room") end
    end

    -- decoration scales with wealth, and only if the palette has any
    if (p.wealth == "rich" or p.wealth == "comfortable") and ctx:has_role("DECOR") then
      local dx, dz = ix + iw - 1, iz
      if ctx:can_place("DECOR", dx, dz) then ctx:place_role("DECOR", dx, dz) end
    end
  end

  -- ---- 🔴 THE COLD NURSERY (jawa_society.md 4.3a) ------------------------
  -- Jawa eggs ruin above 32C; Jawa adults are comfortable to 46C. A Jawa home
  -- in a hot place needs a cooled room or the clan cannot reproduce.
  -- This is the clearest case in the whole system where a TEMPLATE can only
  -- assert the requirement, and only a live reading can confirm it.
  local jawa = (p.faction == "Jawa_IndigenousTribes" or p.faction == "Jawa_Junkers")
  if jawa and (p.climate == "cool" or (p.temperature_c or 0) > 32) then
    local nb = bays[#bays]
    if ctx:has_role("COOLER") then
      -- a cooler sits IN the wall, not on top of it - wall_mount replaces
      -- the wall cell the way a door does
      ctx:wall_mount("COOLER", nb.x + 1, nb.z + nb.h - 1)
      note("cold nursery: cooler placed. ⚠️ TEMPLATE CANNOT PROVE the room holds"
        .. " <=32C - that needs a live reading (see spec 5.3)")
    else
      ctx:refuse("COOLER",
        "faction tech has no cooler; nursery must be BURIED instead - "
        .. "unimplemented, needs excavation (spec 5.4, subterranean factions)")
    end
    if ctx:has_role("NEST") then
      ctx:place_role("NEST", nb.x + 2, nb.z + nb.h - 2)
    end
  end

  -- ---- defence -----------------------------------------------------------
  if p.defended == "fence" or p.defended == "fortified" then
    if unwalled then
      note("Wildsteam ideology forbids turrets; defence request downgraded")
    elseif p.defended == "fortified" and ctx:has_role("TURRET") then
      ctx:place_role("TURRET", rect.x, rect.z)
    end
  end
end
