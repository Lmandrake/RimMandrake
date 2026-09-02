-- junkers_dwelling_cluster.lua - four small one-room huts in a loose
-- quadrant layout around a shared open-air cooking commons.
-- DISTRICT_TEMPLATE_LIBRARY_1, Junkers district #2 (The Claim Jump manifest
-- slot "dwelling cluster").
--
-- WHAT THIS FILE DEMONSTRATES, distinct from dwelling.lua's single domicile:
--   * a CLUSTER is several small separate buildings, not one big one -
--     bed count scales across huts rather than rooms within one shell
--   * a deterministic (non-random) layout that still adapts to whatever
--     rect it is given: the corridor between huts is proven empty by
--     construction (the huts' own x-ranges cannot reach it), not by a
--     runtime collision check
--   * a shared, unroofed commons: cooking together outdoors is cheaper art
--     than a fifth building, and fits Junkers' "forgiving" flavour
--
-- Reused art only: WALL/DOOR/BED/LIGHT/STORAGE/STOVE/TABLE/CHAIR all
-- resolve through the existing palette. Run with --tech Neolithic, same
-- reasoning as junkers_scrapyard.lua: Junkers huts are not powered.

-- ---------------------------------------------------------------------------
-- helpers
-- ---------------------------------------------------------------------------
local function place_hut(ctx, x, z, w, h, beds_needed)
  ctx:room("Barracks", x, z, w, h, true)
  ctx:wall_rect(x, z, w, h)
  ctx:door(x + math.floor(w / 2), z)

  local ix, iz, iw, ih = x + 1, z + 1, w - 2, h - 2
  local placed = 0
  if ctx:has_role("BED") then
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
    if placed < beds_needed then
      ctx:refuse("BED", string.format(
        "%d of %d beds did not fit in this hut", beds_needed - placed, beds_needed))
    end
  else
    note("faction has no BED in its palette - hut left with a bare floor")
  end
  if ctx:has_role("STORAGE") then ctx:place_role_fit("STORAGE", ix, iz, iw, ih) end
  if ctx:has_role("LIGHT") then ctx:place_role_fit("LIGHT", ix, iz, iw, ih) end
  return placed
end

-- ---------------------------------------------------------------------------
-- the entry point
-- ---------------------------------------------------------------------------
-- The declared canvas floor; the engine checks it before build() runs
-- (TEMPLATE_CANVAS_UNDECLARED_1). `rimplace minrect junkers_dwelling_cluster`.
-- From build()'s own arithmetic: hut = min(floor(dim / 2) - 2, 7) >= 4, both axes.
function min_rect(params)
  return 12, 12
end

function build(ctx)
  local p = params
  local w, h = rect.w, rect.h
  local half_w, half_h = math.floor(w / 2), math.floor(h / 2)

  -- huts are capped at 7x7 so a big rect gives more open ground, not
  -- oversized single rooms
  local hut_w = math.min(half_w - 2, 7)
  local hut_h = math.min(half_h - 2, 7)
  if hut_w < 4 or hut_h < 4 then
    ctx:refuse("footprint", string.format(
      "%dx%d cannot hold four %dx%d-minimum huts in a quadrant layout",
      w, h, 4, 4))
    return
  end

  ctx:floor_rect(rect.x, rect.z, w, h)

  local occ = p.occupants or 6
  local beds_per_hut = math.max(1, math.ceil(occ / 4))

  local quadrants = {
    { x = rect.x + 1,            z = rect.z + 1 },            -- NW
    { x = rect.x + half_w + 2,   z = rect.z + 1 },             -- NE
    { x = rect.x + 1,            z = rect.z + half_h + 2 },    -- SW
    { x = rect.x + half_w + 2,   z = rect.z + half_h + 2 },    -- SE
  }
  local total_beds = 0
  for _, q in ipairs(quadrants) do
    total_beds = total_beds + place_hut(ctx, q.x, q.z, hut_w, hut_h, beds_per_hut)
  end
  note(string.format("dwelling cluster: 4 huts, %d bed(s) total for %d occupant(s)",
    total_beds, occ))

  -- ---- shared commons: the vertical gap between the two hut columns ------
  -- 🔑 by construction (not by a collision check): the hut columns occupy
  -- x in [1, hut_w] and [half_w+2, half_w+1+hut_w]; this corridor's x-range
  -- sits strictly between the two, at every z, so it cannot overlap a hut
  -- regardless of hut_h or which quadrants got built.
  local corridor = { x = rect.x + half_w - 1, z = rect.z + 1, w = 3, h = h - 2 }
  local stove_placed = false
  if ctx:has_role("STOVE") then
    for zz = corridor.z, corridor.z + corridor.h - 1 do
      for xx = corridor.x, corridor.x + corridor.w - 1 do
        if ctx:can_place("STOVE", xx, zz) then
          ctx:place_role("STOVE", xx, zz)
          stove_placed = true
          break
        end
      end
      if stove_placed then break end
    end
  end
  if ctx:has_role("TABLE") then ctx:place_role_fit("TABLE", corridor.x, corridor.z, corridor.w, corridor.h) end
  if ctx:has_role("CHAIR") then ctx:place_role_fit("CHAIR", corridor.x, corridor.z, corridor.w, corridor.h) end
  note("shared cooking commons in the open gap between the four huts - unroofed by design")

  note("no security props placed: dwelling cluster is residential, not a checkpoint")
end
