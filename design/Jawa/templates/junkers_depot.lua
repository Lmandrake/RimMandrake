-- junkers_depot.lua - a warehouse floor (grid of storage shelving plus a
-- receiving desk) and a small trader's office. DISTRICT_TEMPLATE_LIBRARY_1,
-- Junkers district #4 (The Claim Jump manifest slot "depot"; the manifest
-- marks this slot required=false, so its own composition is optional, not
-- this template).
--
-- WHAT THIS FILE DEMONSTRATES:
--   * the same shared-wall two-bay split as junkers_cantina_block.lua,
--     reused rather than re-derived - depot floor + office instead of
--     hall + keeper's room
--   * a genuine 2D grid placement (rows AND columns of shelving), stepping
--     by the role's own measured footprint plus an aisle gap
--   * the SECURITY PROPS VOCABULARY SKETCH the item asked for: a function
--     that WOULD place a watch prop over the depot floor, gated on a param
--     the Junkers pilot never sets, so it is proven inert for THIS
--     settlement rather than merely unused
--
-- Reused art only: WALL/DOOR/BED/LIGHT/STORAGE/TABLE/CHAIR/TURRET all
-- resolve through the existing palette. --tech Neolithic like the other
-- three Junkers districts - the depot floor is unpowered.

-- ---------------------------------------------------------------------------
-- security props vocabulary - SKETCH ONLY, never exercised by this pilot
-- ---------------------------------------------------------------------------
-- ownership_settlement_spec.md item 8 asks for "security props" per
-- district. The Claim Jump's manifest sets searchesLeavers=false
-- (Inhabited_SecurityProfile_Junkers) and NOTHING in this template ever
-- sets params.security_props - so has_role/refuse below is dead code for
-- Junkers by construction, not by omission. It exists to show what a
-- future HIGH-security settlement's depot (Empire, Deepwater) would ask
-- for: a fixed "eyes on the goods" prop watching the storage floor. The
-- palette's only watch-shaped role today is TURRET (tech:Ultra/Empire),
-- which is itself a placeholder for a proper fixed-camera prop
-- (rimplace-gaps.md notes the palette has no CAMERA role at all yet).
local function maybe_place_security(ctx, p, x, z)
  if p.security_props ~= "watched" then
    return false
  end
  if ctx:has_role("TURRET") then
    ctx:place_role("TURRET", x, z)
    note("security prop placed (params.security_props='watched'): a fixed watch prop over the depot floor")
    return true
  end
  ctx:refuse("TURRET", "security_props='watched' requested but this faction/tech has no watch prop in its palette")
  return false
end

-- ---------------------------------------------------------------------------
-- the entry point
-- ---------------------------------------------------------------------------
function build(ctx)
  local p = params
  local w, h = rect.w, rect.h

  local office_h = 6
  local floor_h = h - office_h + 1  -- +1: the shared wall row
  if floor_h < 8 or w < 10 then
    ctx:refuse("footprint", string.format(
      "%dx%d too small for a depot floor (>=10 wide) plus a %d-row office",
      w, h, office_h))
    return
  end

  local officeBay = { x = rect.x, z = rect.z, w = w, h = office_h }
  local floorBay = { x = rect.x, z = rect.z + office_h - 1, w = w, h = floor_h }

  ctx:room("Storeroom", floorBay.x, floorBay.z, floorBay.w, floorBay.h, true)
  ctx:wall_rect(floorBay.x, floorBay.z, floorBay.w, floorBay.h)
  ctx:room("Storeroom", officeBay.x, officeBay.z, officeBay.w, officeBay.h, true)
  ctx:wall_rect(officeBay.x, officeBay.z, officeBay.w, officeBay.h)

  local midX = rect.x + math.floor(w / 2)
  ctx:door(midX, officeBay.z + office_h - 1)          -- office <-> depot floor
  ctx:door(midX, floorBay.z + floorBay.h - 1)         -- depot floor <-> outside (loading door)

  -- ---- depot floor: a real grid of shelving, not one row ------------------
  local ix, iz, iw, ih = floorBay.x + 1, floorBay.z + 2, floorBay.w - 2, floorBay.h - 3
  local shelves = 0
  if ctx:has_role("STORAGE") then
    local sw, sh = ctx:width_of("STORAGE"), ctx:height_of("STORAGE")
    local step_x, step_z = sw + 1, sh + 2  -- +2 leaves an aisle between rows
    local zz = iz
    while zz <= iz + ih - sh do
      local xx = ix
      while xx <= ix + iw - sw do
        if ctx:can_place("STORAGE", xx, zz) then
          ctx:place_role("STORAGE", xx, zz)
          shelves = shelves + 1
        end
        xx = xx + step_x
      end
      zz = zz + step_z
    end
  end
  -- receiving desk, just inside the loading door
  if ctx:has_role("TABLE") then ctx:place_role_fit("TABLE", ix, floorBay.z + floorBay.h - 3, iw, 2) end
  if ctx:has_role("CHAIR") then ctx:place_role_fit("CHAIR", ix, floorBay.z + floorBay.h - 3, iw, 2) end
  if ctx:has_role("LIGHT") then ctx:place_role_fit("LIGHT", floorBay.x + 1, floorBay.z + 1, floorBay.w - 2, floorBay.h - 2) end
  note(string.format("depot floor: %d shelving unit(s) in a grid, one receiving desk by the loading door", shelves))

  -- ---- roof support pillar --------------------------------------------
  -- a floor bay this wide (>=18) puts its own centre more than 6 cells from
  -- any wall - vanilla's own roof-support radius, and rimplace's lint
  -- checks for exactly that (roof-unsupported). One WALL-role pillar near
  -- the geometric centre closes the gap; search outward for the first free
  -- cell so it never lands on top of a shelf the grid above already placed.
  if ctx:has_role("WALL") then
    local cx, cz = ix + math.floor(iw / 2), iz + math.floor(ih / 2)
    local placed = false
    for r = 0, 3 do
      for dz = -r, r do
        for dx = -r, r do
          if math.abs(dx) + math.abs(dz) == r then
            local xx, zz = cx + dx, cz + dz
            if ctx:in_bounds(xx, zz) and not ctx:occupied(xx, zz) then
              ctx:place_role("WALL", xx, zz)
              placed = true
              break
            end
          end
        end
        if placed then break end
      end
      if placed then break end
    end
    if not placed then
      ctx:refuse("WALL", "no free cell near centre for a roof-support pillar")
    end
  end

  -- SKETCH ONLY: see the function comment above. p.security_props is never
  -- set by this pilot's CLI params, so this call is always a no-op here.
  maybe_place_security(ctx, p, ix, iz)

  -- ---- trader's office: the one cast slot the manifest names (1x trader) -
  local ox, oz, ow, oh = officeBay.x + 1, officeBay.z + 1, officeBay.w - 2, officeBay.h - 2
  if ctx:has_role("BED") then ctx:place_role_fit("BED", ox, oz, ow, oh) end
  if ctx:has_role("TABLE") then ctx:place_role_fit("TABLE", ox, oz, ow, oh) end
  if ctx:has_role("CHAIR") then ctx:place_role_fit("CHAIR", ox, oz, ow, oh) end
  if ctx:has_role("STORAGE") then ctx:place_role_fit("STORAGE", ox, oz, ow, oh) end
  if ctx:has_role("LIGHT") then ctx:place_role_fit("LIGHT", ox, oz, ow, oh) end

  note("no security props placed: Junkers/The Claim Jump is low security by design (searchesLeavers=false)")
end
