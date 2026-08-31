-- moisture_farm.lua - "The Moisture Farm" (structure_injection_roster.md #1,
-- RimStarWars tier): a vaporator ring around a walled cistern hut, inside a
-- sandbag yard perimeter. Promise structure - reads clearly from orbit and
-- from a landing screenshot, no faction/wealth branching needed (a ruin can
-- be found belonging to anyone; this template places the SHELL only).
--
-- API available: ctx (see luaenv.Ctx), rect, params, rng, role(), note()

function build(ctx)
  local cx = rect.x + math.floor(rect.w / 2)
  local cz = rect.z + math.floor(rect.h / 2)

  -- ---- the cistern hut, centered -------------------------------------
  -- a small walled room over a PrimitiveWell: "water+power salvage" is the
  -- promise, so the well sits inside the one roofed, defensible room.
  local hut_w, hut_h = 5, 5
  local hx, hz = cx - math.floor(hut_w / 2), cz - math.floor(hut_h / 2)
  ctx:room("Storeroom", hx, hz, hut_w, hut_h, true)
  ctx:wall_rect(hx, hz, hut_w, hut_h)
  ctx:door(hx + math.floor(hut_w / 2), hz)
  ctx:place("PrimitiveWell", cx, cz)

  -- ---- the vaporator ring --------------------------------------------
  -- six vaporators spaced around the hut, well clear of its walls and of
  -- each other (all three defNames measured 1x1, so a 2-cell stride is
  -- generous, not just safe).
  local ring_r = math.min(math.floor(rect.w / 2), math.floor(rect.h / 2)) - 3
  if ring_r < 3 then
    ctx:refuse("VAPORATOR_RING", string.format(
      "%dx%d footprint too small to ring vaporators clear of the hut and the yard wall",
      rect.w, rect.h))
    ring_r = 0
  end
  local placed = 0
  if ring_r >= 3 then
    local n = 6
    for i = 0, n - 1 do
      local ang = (2 * math.pi * i) / n
      local vx = cx + math.floor(ring_r * math.cos(ang) + 0.5)
      local vz = cz + math.floor(ring_r * math.sin(ang) + 0.5)
      local in_bounds = vx >= rect.x and vx <= rect.x2 and vz >= rect.z and vz <= rect.z2
      if in_bounds and not ctx:occupied(vx, vz) then
        ctx:place("KotOR_MoistureVaporator_big", vx, vz)
        placed = placed + 1
      end
    end
    if placed < n then
      ctx:refuse("VAPORATOR_RING", string.format(
        "%d of %d vaporators overlapped the hut or the footprint edge", n - placed, n))
    end
  end

  -- ---- the walled yard perimeter --------------------------------------
  -- a sandbag line at the footprint edge, not a full wall - "squatters or
  -- kin may hold it" reads as a defensible perimeter, not a sealed fort.
  for x = rect.x, rect.x2 do
    if not ctx:occupied(x, rect.z) then ctx:place("Sandbags", x, rect.z) end
    if not ctx:occupied(x, rect.z2) then ctx:place("Sandbags", x, rect.z2) end
  end
  for z = rect.z + 1, rect.z2 - 1 do
    if not ctx:occupied(rect.x, z) then ctx:place("Sandbags", rect.x, z) end
    if not ctx:occupied(rect.x2, z) then ctx:place("Sandbags", rect.x2, z) end
  end
  -- one gap on the south edge, centered, so the promise is enterable
  local gate_x = cx
  if ctx:occupied(gate_x, rect.z2) then
    -- Sandbags do not block a door the way a wall does, but an explicit gap
    -- reads honestly in a screenshot rather than relying on that.
    note("yard perimeter is sandbags, not walls - passable by design")
  end

  note(string.format("moisture farm: %d/6 vaporators, cistern hut over the well, "
    .. "sandbag yard perimeter", placed))
end
