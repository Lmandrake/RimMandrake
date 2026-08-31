-- hunting_lodge.lua - structure_injection_roster.md PROMISE #12, "The
-- Hunting Lodge" (RSW tier, Ishko): trophy hall, kennels, cold room.
--
-- Three bays, side by side: Trophy Hall (display), Kennels (animal
-- sleeping spots), Cold Room (a cooler-holding room reusing nursery.lua's
-- verified power-bus pattern - transmitters cardinal, connectors within
-- ConnectMaxDist 6, cooler wall-mounted at rot 0 so its cold side faces
-- IN. This is a generic cool-storage room, not the campaign's specific
-- cold-nursery mechanic - same building technique, different purpose.
--
-- Defnames verified against the live def dump (2026-08-31 capture), not
-- guessed:
--   AnimalSleepingSpot (Core, 1x1, category Building) - the kennels.
--   MediumFossilTrophy / LargeFossilTrophy (Minerals Sparkle, 1x1 / 2x2,
--     category Building) - no hunting-trophy-specific ThingDef exists in
--     the current stack; these are the closest real "mounted trophy
--     display" objects on hand. Substitution, not invention.
--
-- API: ctx (luaenv.Ctx), rect, params, rng, role(), note()

function build(ctx)
  local p = params
  local x, z = rect.x, rect.z
  local W, H = rect.w, rect.h

  -- +8 on W, +2 on H beyond the three shells: the cold room's exterior power
  -- apron (bus + generator + battery, nursery.lua's own verified margin)
  -- needs that much clearance past the last bay's east wall and north wall.
  local BAYS = 3
  local min_w = 5
  local usable = (W - 8) - (BAYS + 1)
  if usable < BAYS * min_w or H < 8 + 2 then
    ctx:refuse("footprint", string.format(
      "%dx%d cannot hold a 3-bay lodge of at least %d wide each plus the cold "
        .. "room's power apron (+8w/+2h)", W, H, min_w))
    return
  end
  local each = math.floor(usable / BAYS)
  local bays_w = W - 8 -- reserve the east 8 columns for the power apron
  local bays, cx = {}, x
  for i = 1, BAYS do
    local bw = (i == BAYS) and (bays_w - (cx - x) - 1) or (each + 1)
    bays[#bays + 1] = { x = cx, z = z, w = bw + 1, h = H - 2 } -- reserve the north 2 rows too
    cx = cx + bw
  end

  local trophy, kennel, cold = bays[1], bays[2], bays[3]

  -- ---- shells --------------------------------------------------------------
  ctx:room("Storeroom", trophy.x, trophy.z, trophy.w, trophy.h, true)
  ctx:wall_rect(trophy.x, trophy.z, trophy.w, trophy.h)

  ctx:room("Storeroom", kennel.x, kennel.z, kennel.w, kennel.h, true)
  ctx:wall_rect(kennel.x, kennel.z, kennel.w, kennel.h)

  ctx:room("Storeroom", cold.x, cold.z, cold.w, cold.h, true)
  ctx:wall_rect(cold.x, cold.z, cold.w, cold.h)

  -- ---- doors: one exterior on the trophy hall, interior links between ------
  ctx:door(trophy.x + math.floor(trophy.w / 2), trophy.z)
  ctx:door(kennel.x, kennel.z + math.floor(kennel.h / 2))
  ctx:door(cold.x, cold.z + math.floor(cold.h / 2))

  -- ---- trophy hall: fossil trophies down the back wall ----------------------
  -- LargeFossilTrophy is 2x2 - one cell further off the wall than a 1x1 would
  -- need, or its far edge clips the wall row (footprint-collision, not
  -- guessed past: the linter caught it on the first pass).
  local tix, tiz = trophy.x + 1, trophy.z + trophy.h - 3
  ctx:place("LargeFossilTrophy", tix, tiz)
  ctx:place("MediumFossilTrophy", tix + 3, tiz + 1)
  if ctx:has_role("LIGHT") then
    ctx:place_role("LIGHT", trophy.x + trophy.w - 2, trophy.z + 1)
  end

  -- ---- kennels: a small grid of animal sleeping spots ------------------------
  -- "something still uses the kennels" - the roster's own line; leave them
  -- unassigned/empty, not tied to a specific pawn or faction owner. Step by
  -- 2 so 1x1 spots don't crowd a shared aisle.
  local kix, kiz = kennel.x + 1, kennel.z + 1
  local kiw, kih = kennel.w - 2, kennel.h - 2
  for zz = kiz, kiz + kih - 1, 2 do
    for xx = kix, kix + kiw - 1, 2 do
      if ctx:can_place("AnimalSleepingSpot", xx, zz) then
        ctx:place("AnimalSleepingSpot", xx, zz)
      end
    end
  end
  if ctx:has_role("LIGHT") then
    ctx:place_role("LIGHT", kennel.x + 1, kennel.z + kennel.h - 2)
  end

  -- ---- cold room: nursery.lua's verified power-bus pattern, reused --------
  -- Transmitters (generator, battery) join a net only by CARDINAL adjacency;
  -- connectors (the cooler) reach the nearest transmitter within
  -- ConnectMaxDist=6, through a wall, no line-of-sight test. Bus runs outside
  -- along the row above the north wall, same shape nursery.lua proved.
  if ctx:has_role("COOLER") then
    local bus_z = cold.z + cold.h
    local gen_x = cold.x + cold.w + 4
    for bx = cold.x + 2, gen_x - 2 do
      ctx:place(role("CONDUIT"), bx, bus_z)
    end
    ctx:wall_mount("COOLER", cold.x + math.floor(cold.w / 2), cold.z + cold.h - 1, 0)
    ctx:place_role("GENERATOR", gen_x, bus_z)
    ctx:place_role("BATTERY", cold.x + 3, bus_z + 1)
    ctx:note("hunting lodge cold room: cooler at rot 0 (cold side faces in), "
      .. "generator/battery are TRANSMITTERS on an exterior bus, cooler is a "
      .. "CONNECTOR within ConnectMaxDist 6 - same verified shape as "
      .. "nursery.lua. TEMPLATE CANNOT PROVE the room holds a target "
      .. "temperature - that needs a live reading.")
  else
    ctx:refuse("COOLER", "no cooler in this tech tier's palette - cold room "
      .. "unimplemented for this faction")
  end
end
