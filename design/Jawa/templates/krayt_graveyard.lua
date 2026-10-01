-- krayt_graveyard.lua - "The Krayt Graveyard" (structure_injection_roster.md
-- #3, RimStarWars tier): a bone-crescent scatter of krayt dragon remains in
-- ExtremeDesert, with a few pearl-bearing skulls among the ordinary bones.
-- Promise structure, not a building - a site dressing, no walls/rooms.
-- "pearls worth a fortune; the owner of the bones still patrols" - the
-- pearls are the lure, not guaranteed loot: only a minority of skulls carry
-- one.
--
-- defNames: RSW_KraytDragonSkull and RSW_KraytPearl are our own SWBestiary
-- items (the absorbed ports); KraytDragonHorn is still the Star Wars Animal
-- Collection donor's (no RSW port exists). RSW_KraytSkeleton and
-- RM_GiantSkull are STILLSAND_SKELETONS_TRACKS_1's skeleton buildings.
--
-- API available: ctx (see luaenv.Ctx), rect, params, rng, role(), note()

function build(ctx)
  local cx = rect.x + math.floor(rect.w / 2)
  local cz = rect.z + math.floor(rect.h / 2)

  -- ---- the bone crescent -----------------------------------------------
  -- an arc (half a ring, not a full circle) of skulls and horns, reading as
  -- a graveyard sweep rather than a tidy formation. Radius scaled to the
  -- footprint so this still reads at smaller rects.
  local ring_r = math.min(math.floor(rect.w / 2), math.floor(rect.h / 2)) - 2
  if ring_r < 4 then
    ctx:refuse("BONE_CRESCENT", string.format(
      "%dx%d footprint too small for a legible crescent", rect.w, rect.h))
    ring_r = 0
  end

  local skulls_placed, horns_placed, pearls_placed = 0, 0, 0
  if ring_r >= 4 then
    -- half-ring: angles from -60deg to +240deg (a 300-degree open sweep),
    -- enough stations to read as "a graveyard" without over-filling a small
    -- footprint.
    local n = 10
    local start_ang = -math.pi / 3
    local end_ang = start_ang + (5 * math.pi / 3)
    for i = 0, n - 1 do
      local t = n > 1 and (i / (n - 1)) or 0
      local ang = start_ang + t * (end_ang - start_ang)
      local bx = cx + math.floor(ring_r * math.cos(ang) + 0.5)
      local bz = cz + math.floor(ring_r * math.sin(ang) + 0.5)
      local in_bounds = bx >= rect.x and bx <= rect.x2 and bz >= rect.z and bz <= rect.z2
      if in_bounds and not ctx:occupied(bx, bz) then
        -- alternate skull/horn along the arc so it doesn't read as one
        -- repeated prop; every third skull is pearl-bearing.
        if i % 2 == 0 then
          ctx:place("RSW_KraytDragonSkull", bx, bz)
          skulls_placed = skulls_placed + 1
          if skulls_placed % 3 == 1 then
            -- the pearl sits WITH the skull, not on it - offset one cell
            -- toward the crescent's own center so it stays inside the
            -- footprint and doesn't collide with the next arc station.
            local px = bx + (cx > bx and 1 or (cx < bx and -1 or 0))
            local pz = bz + (cz > bz and 1 or (cz < bz and -1 or 0))
            if px >= rect.x and px <= rect.x2 and pz >= rect.z and pz <= rect.z2
                and not ctx:occupied(px, pz) then
              ctx:place("RSW_KraytPearl", px, pz)
              pearls_placed = pearls_placed + 1
            end
          end
        else
          ctx:place("KraytDragonHorn", bx, bz)
          horns_placed = horns_placed + 1
        end
      end
    end
  end

  -- ---- one real krayt skeleton at the crescent's own focus ---------------
  -- STILLSAND_SKELETONS_TRACKS_1 §6: the "owner of the bones" is a whole
  -- skeleton building now (RSW_KraytSkeleton, 7x3, SWBestiary, MayRequire
  -- mandrake.rm.stillsand), with its skull building beside it - the
  -- crescent of loose skulls is the scatter around it.
  local skeleton_placed = 0
  if not ctx:occupied(cx, cz) then
    ctx:place("RSW_KraytSkeleton", cx, cz)
    skeleton_placed = 1
    if not ctx:occupied(cx + 6, cz) then
      ctx:place("RM_GiantSkull", cx + 6, cz)
    end
  end

  note(string.format(
    "krayt graveyard: %d skeleton, %d skulls (%d pearl-bearing), %d horns along the crescent",
    skeleton_placed, skulls_placed, pearls_placed, horns_placed))
end
