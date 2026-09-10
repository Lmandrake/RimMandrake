-- beast_pens.lua - Pet / beast breeding facility (structure_procedural_spec.md
-- section 8.13). EXTENDS hunting_lodge.lua's kennels: that file's 2-stride
-- lattice of AnimalSleepingSpot is exactly what R3 bans ("no `for zz.. for
-- xx.. step 2` lattices for anything a person owns"); this template replaces
-- it with a proper R-PEN pattern (Fence ring + FenceGate, random-slot animal
-- sleeping furniture, never a fixed stride). Livestock_Trade_Utility_Pets_v1.md
-- is the economy this dresses; Hutt casts are the natural owner (o.hutt).
--
-- Grammar (spec's own chain): keeper's house (8.1 homestead tier, door onto
-- the pens) -> pen row (2-4 R-PEN, genuinely different sizes, one is the
-- nursery - always the WESTMOST pen here, touching the house, so the
-- AnimalFlap connecting them is a fixed one-cell seam, never a search) ->
-- feed store (R-STORE) -> tack & tools (R-WORK) -> the display. A central
-- lane (2 wide, PackedDirt) runs along the south edge of the whole row;
-- every pen/room's door opens onto it. `rimplace minrect beast_pens` reports
-- the exact floor this arithmetic needs.
--
-- ⚠️ Canvas: this template's own arithmetic (below, `layout_dims`) needs
-- 28x14 for the default 3-pen layout, not the spec's 26x22 estimate - the
-- spec's number was a rough guess (homestead.lua's header names the same gap
-- in ITS spec estimate: "the spec's 7x7/12x10/30x26 estimates forgot the
-- threshold row"). This is WIDER and SHORTER because the three utility rooms
-- stack in a column east of the pens (sharing one wall row each, hutt_
-- holding_pens.lua's cell/corridor trick) rather than running further east
-- in the same row.
--
-- params:
--   faction    drives variation: Jawa_HuttCartel (o.hutt: GibbetCage,
--              Skullspike, "a cage is a cage"), OutlanderCivil (o.league:
--              trough moves to the road-side gate, matching homestead.lua's
--              own "free well is the whole faith" convention), Jawa_
--              WildsteamClan (o.wildsteam: pens come UNFENCED - PenMarker +
--              AnimalSleepingSpot only, keeper additionally gets a Bedroll
--              among them - see the header note by that branch for why the
--              base house is NOT dropped). Anything else reads as the plain/
--              Homestead-tier default.
--   wealth     "rich" unlocks AnimalBed (comfortable+) over AnimalSleepingBox
--   pens       2-4 (default 3) - how many R-PENs in the row
--
-- Verified real defNames this pass (RimSage search_defs against tonight's
-- active-mod index; footprints cross-checked against rimplace.defsize - all
-- 1x1 unless noted): AnimalSleepingBox, AnimalSleepingSpot, ButcherSpot,
-- Kibble, PenMarker, AnimalFlap, GibbetCage, Skullspike, Filth_AnimalFilth,
-- Filth_Blood, Filth_Dirt, Hay, Bedroll, PackedDirt (TerrainDef), EggBox,
-- Fence/FenceGate (palette FENCE/GATE), WaterTrough (palette TROUGH, 2x1),
-- Muffalo/Dromedary/Chicken (PawnKindDef, for the mandatory E3 stock -
-- "a pen without animals is a fence").
--
-- NOT built - real props tonight's active-mod RimSage index does not carry
-- (never guessed; same posture dead_caravan.lua's header takes for the
-- VFEPD/BreadMoAM family): `LWM_Hayloft`, `LWM_Clothing_Rack`,
-- `LWM_Meat_Hook`, `ASF_MeatRack`, `KibbleDispenser` [Better Kibble],
-- `XER_TribalTableButcher`, `VFE_AnimalSarcophagus`, `MA_HarpeagleNest`,
-- `ES_HorseSign`, `OuterRim_AurebeshWordKill`, `BanthaHorn` (the palette's
-- own TROPHY role for faction:TribeCivil resolves to it, but a bare
-- search_defs on "Bantha" returns nothing tonight - the role is used via
-- ctx:has_role/place_overlay, never cited here as a raw defName). Tack &
-- tools substitutes ToolCabinet+Shelf (both real, both already this spec's
-- own R-WORK ingredients) for the missing harness rack. The feed store's
-- shelf carries loose `Kibble` items directly rather than a dispenser.
-- 🔴 TORMENT MASTER: the task brief is explicit - "read
-- vlvop.tormentmaster.expansion first, or skip". `search_defs` for that
-- namespace returns nothing under tonight's active RimSage index (the mod is
-- not indexed/active), so per the brief's own instruction this flourish is
-- SKIPPED outright for the Hutt variation, not substituted or guessed.
--
-- API: ctx (luaenv.Ctx), rect, params, rng, role(), note()

local function filth(ctx, def, x, z)
  return ctx:place(def, x, z, 0, nil, "FILTH", true)
end

-- a raw defName placed with a ROLE tag, footprint-checked like a palette
-- role (homestead.lua/dead_caravan.lua's own shared shape for this)
local function try_def(ctx, def, role_tag, x, z, rot)
  rot = rot or 0
  if not ctx:can_place(def, x, z, rot) then return false end
  return ctx:place(def, x, z, rot, nil, role_tag)
end

-- the cell, then rings outward, for a raw defName (dead_caravan.lua's
-- place_near, same shape - along_wall/try_near only take palette roles)
local function place_near(ctx, def, x, z, radius, role_tag, rot)
  rot = rot or 0
  for ring = 0, radius do
    local cells = {}
    for dz = -ring, ring do
      for dx = -ring, ring do
        if math.max(math.abs(dx), math.abs(dz)) == ring then cells[#cells + 1] = { x + dx, z + dz } end
      end
    end
    shuffle(cells)
    for _, c in ipairs(cells) do
      if ctx:can_place(def, c[1], c[2], rot) then
        ctx:place(def, c[1], c[2], rot, nil, role_tag)
        return true, c[1], c[2]
      end
    end
  end
  return false
end

-- R3: raw-defName wall-hugging with NO fixed stride - every interior wall
-- cell of `pi` is a candidate slot, shuffled, first N that fit win. This is
-- the fence-side equivalent of the prelude's along_wall(), needed because
-- AnimalSleepingBox/AnimalSleepingSpot are raw defNames, not palette roles.
local function fence_hug(ctx, def, role_tag, pi, n)
  local slots = {}
  for _, side in ipairs({ "N", "E", "S", "W" }) do
    for _, c in ipairs(wall_cells(pi, side)) do slots[#slots + 1] = { c[1], c[2] } end
  end
  shuffle(slots)
  local placed = 0
  for _, s in ipairs(slots) do
    if placed >= n then break end
    if try_def(ctx, def, role_tag, s[1], s[2], 0) then placed = placed + 1 end
  end
  return placed
end

-- ---------------------------------------------------------------------------
-- layout: the SAME arithmetic backs min_rect() and build(), so the declared
-- floor can never drift from what build() actually needs (hunting_lodge.lua's
-- own header names this discipline). Pen SIZE is a fixed canonical set
-- (never RNG-varied) so the declared minimum holds for every seed - only
-- ORDER along the row is randomised in build(); the westmost slot is always
-- the nursery, never rerolled, because the AnimalFlap seam is a fixed cell.
-- ---------------------------------------------------------------------------
local PEN_POOL = { { 5, 5 }, { 6, 6 }, { 7, 7 }, { 5, 6 } } -- w,h - all pairwise distinct
local HOUSE_W, HOUSE_H = 7, 7
-- OUTER footprints. UTIL_W=6/STORE_H=6 give the feed store a 4x4 INTERIOR
-- (spec's own "feed store R-STORE 4x4") - the first sweep of this template
-- found kibble_placed=0 across all 70 cases with UTIL_W=4/STORE_H=4: a 4x4
-- OUTER room is only a 2x2 (4-cell) interior once walled, and 6-10 hay
-- clumps plus a shelf and a butcher spot fill every one of those 4 cells
-- before the Kibble loop ever runs - a real capacity bug, not bad luck
-- (`rimplace lint` cannot see it: every individual placement legitimately
-- refused-then-succeeded-elsewhere or just ran out of tries, so nothing hit
-- ERROR; only counting the actual Kibble things in the plan caught it).
local UTIL_W = 6
local STORE_H, TACK_H, DISPLAY_H = 6, 5, 3
local LANE_H, MARGIN_S, MARGIN_N, MARGIN_E = 2, 2, 1, 1

local function clamp(v, lo, hi) return math.max(lo, math.min(hi, v)) end

local function layout_dims(p)
  local n = clamp((p and p.pens) or 3, 2, 4)
  local pen_w, pen_h_max = 0, 0
  for i = 1, n do
    pen_w = pen_w + PEN_POOL[i][1]
    pen_h_max = math.max(pen_h_max, PEN_POOL[i][2])
  end
  pen_w = pen_w - (n - 1) -- adjacent pens share one fence column each
  -- store/tack SHARE one wall row (hutt_holding_pens.lua's cell/corridor
  -- trick); display is unwalled and simply stacks after tack with no share.
  local util_h = STORE_H + TACK_H - 1 + DISPLAY_H
  local w = HOUSE_W + pen_w + UTIL_W + MARGIN_E
  local h = MARGIN_S + LANE_H + math.max(HOUSE_H, pen_h_max, util_h) + MARGIN_N
  return w, h, n
end

function min_rect(params)
  local w, h = layout_dims(params)
  return w, h
end

-- ---------------------------------------------------------------------------
function build(ctx)
  local p = params
  local W, H = rect.w, rect.h
  local need_w, need_h, n = layout_dims(p)
  if W < need_w or H < need_h then
    ctx:refuse("footprint", string.format(
      "%dx%d cannot hold a %d-pen beast_pens (keeper's house + pens + feed "
        .. "store + tack&tools + display) which needs at least %dx%d",
      W, H, n, need_w, need_h))
    return
  end

  local faction = p.faction
  local o = {
    hutt = (faction == "Jawa_HuttCartel"),
    league = (faction == "OutlanderCivil"),
    wildsteam = (faction == "Jawa_WildsteamClan"),
    comfortable = (p.wealth == "rich"),
  }

  local x0, z0 = rect.x, rect.z

  -- ---- keeper's house (8.1 tier small dwelling) ---------------------------
  local house = R(x0, z0 + LANE_H, HOUSE_W, HOUSE_H)
  local hir = shell(ctx, "Bedroom", house, { floor = "FLOOR", doors = { { "S" } } })
  local beds = 0
  if ctx:has_role("BED") then
    beds = hug(ctx, "BED", hir, { "N", "W" }, { face = "wall" })
  end
  -- hearth on the door wall (smoke goes out the door), table+seats free
  local stove_ok = hug(ctx, "STOVE", hir, { "S" }) > 0
  if stove_ok and #LAST_PLACED > 0 then
    local hb = LAST_PLACED[#LAST_PLACED]
    local tok, tx, tz = try_near(ctx, "TABLE", hb[1], hb[2] + 2, 0, 2, hir)
    if tok then seat_around(ctx, "CHAIR", tx, tz, 2, hir, 0) end
  end
  dress(ctx, hir, {
    { role = "CRATE", n = { 0, 1 }, where = "corner" },
    { role = "SHELF_SMALL", n = { 0, 1 }, where = "wall" },
  })
  wall_lights(ctx, hir, 1)

  -- ---- the pen row: n R-PENs, genuinely different sizes -------------------
  -- pens[1] (westmost) is ALWAYS the nursery: it is the one pen physically
  -- touching the house, which is what makes the AnimalFlap seam below a
  -- fixed cell rather than a search over every pen.
  local order = {}
  for i = 1, n do order[i] = i end
  shuffle(order)
  local pens, cursor_x = {}, x0 + HOUSE_W
  local tallest_slot = 1
  for slot = 1, n do
    local sz = PEN_POOL[order[slot]]
    local w, h = sz[1], sz[2]
    local pr = R(cursor_x, z0 + LANE_H, w, h)
    pens[slot] = { rect = pr, nursery = (slot == 1) }
    if h > pens[tallest_slot].rect.h then tallest_slot = slot end
    cursor_x = cursor_x + w - 1 -- next pen shares this column as its west fence
  end
  -- cursor_x already IS the last pen's own x2 (the "+w-1" step above lands
  -- ON its east edge, not one past it - a `-1` here put the feed store's
  -- west wall on top of the last pen's east fence column; found by lint's
  -- own footprint-collision + room-not-sealed report on the first run).
  local pens_x2 = cursor_x

  -- The animal-flap boundary: the house's east wall touches the nursery
  -- pen's west fence column directly (no gap - one seals what the other
  -- opens). Rather than reach for a private "swap this wall cell" API (the
  -- sandbox refuses any underscore attribute, so `ctx:_replace_wall_cell` is
  -- not reachable from Lua at all), this reuses door()'s own public
  -- `defName` override: door() already replaces whatever WALL sits at the
  -- cell before placing, so `ctx:door(x, z, "AnimalFlap", ...)` is exactly
  -- "cut an AnimalFlap into this wall" through the documented API alone.
  local flap_z = house.z + 1
  ctx:door(house.x2, flap_z, "AnimalFlap", nil, 1)

  local total_animals, total_boxes, total_fence, road_gate_done = 0, 0, 0, false
  for slot, pen in ipairs(pens) do
    local pr = pen.rect
    local pi = inner(pr)
    local gate_x = rng.int(pr.x + 1, pr.x2 - 1) -- staggered: rerolled every pen

    if o.wildsteam then
      -- "no fences, PenMarkers and AnimalSleepingSpots under real trees" -
      -- the area is still THIS pen's own footprint, just never ringed in Fence.
      try_def(ctx, "PenMarker", "PEN_MARKER", center(pi))
      total_boxes = total_boxes + fence_hug(ctx, "AnimalSleepingSpot", "ANIMAL_BED_BOX", pi, rng.int(2, 4))
      floor_patch(ctx, pi, "PackedDirt", pr)
    else
      -- ---- Fence ring; the lane gate is staggered every pen; the tallest --
      -- ---- pen ALSO carries the one perimeter gate "to the road" ----------
      local road_gate_x = (slot == tallest_slot) and rng.int(pr.x + 1, pr.x2 - 1) or nil
      local edges = {}
      for x = pr.x, pr.x2 do edges[#edges + 1] = { x, pr.z }; edges[#edges + 1] = { x, pr.z2 } end
      for z = pr.z + 1, pr.z2 - 1 do edges[#edges + 1] = { pr.x, z }; edges[#edges + 1] = { pr.x2, z } end
      local fenced = 0
      for _, c in ipairs(edges) do
        local cx, cz = c[1], c[2]
        -- the flap seam: the house's own east wall (with the flap already
        -- cut into it) seals this column - a fence cell here would just be
        -- a second, redundant seal one column further out with no gap.
        local is_flap_seam = (pen.nursery and cx == pr.x and cz == flap_z)
        if not is_flap_seam then
          local rl = "FENCE"
          if cz == pr.z and cx == gate_x and ctx:has_role("GATE") then rl = "GATE"
          elseif road_gate_x and cz == pr.z2 and cx == road_gate_x and ctx:has_role("GATE") then
            rl = "GATE"
          end
          if try_place(ctx, rl, cx, cz, 0) then
            fenced = fenced + 1
            if rl == "GATE" and cz == pr.z2 then road_gate_done = true end
          end
        end
      end
      total_fence = total_fence + fenced
      floor_patch(ctx, pi, "PackedDirt", pr)
      try_def(ctx, "PenMarker", "PEN_MARKER", center(pi))

      if pen.nursery and ctx:has_role("NEST") then
        total_boxes = total_boxes + hug(ctx, "NEST", pi, { "N", "E", "W" }, { n = rng.int(2, 3) })
      elseif o.comfortable and ctx:has_role("ANIMAL_BED") then
        total_boxes = total_boxes + hug(ctx, "ANIMAL_BED", pi, { "N", "E", "S", "W" }, { n = rng.int(2, 4) })
      else
        total_boxes = total_boxes + fence_hug(ctx, "AnimalSleepingBox", "ANIMAL_BED_BOX", pi, rng.int(2, 4))
      end

      -- lean-to roof, 2x3, on two Column posts, in a random corner
      if pi.w >= 3 and pi.h >= 3 and ctx:has_role("PILLAR") then
        local lx = rng.chance(0.5) and pi.x or (pi.x2 - 1)
        local lz = rng.chance(0.5) and pi.z or (pi.z2 - 2)
        try_place(ctx, "PILLAR", lx, lz, 0)
        try_place(ctx, "PILLAR", lx + 1, lz + 2, 0)
        ctx:roof_rect(lx, lz, 2, 3)
      end

      if pen.nursery then
        -- Heater/Brazier "just outside its fence" - the free exterior edge
        -- every nursery has regardless of neighbours: due north, past its
        -- own back fence, in the margin build()'s own gate proved the
        -- canvas holds.
        local hz2 = pr.z2 + 1
        local hx2 = pr.x + rng.int(1, math.max(1, pr.w - 2))
        if ctx:has_role("HEATER") then try_near(ctx, "HEATER", hx2, hz2, 0, 1, nil)
        elseif ctx:has_role("BRAZIER") then try_near(ctx, "BRAZIER", hx2, hz2, 0, 1, nil) end
      end
    end

    -- WaterTrough near the gate; OutlanderCivil moves it outside the fence,
    -- by the gate, same "free well" convention homestead.lua's o.league uses
    if ctx:has_role("TROUGH") then
      if o.league then try_near(ctx, "TROUGH", gate_x, pr.z - 1, 0, 2, nil)
      else try_near(ctx, "TROUGH", gate_x, pr.z + 1, 0, 2, pi) end
    end
    for _ = 1, rng.int(2, 3) do
      place_near(ctx, "Hay", rng.int(pi.x, pi.x2), rng.int(pi.z, pi.z2), 1, "HAY")
    end
    for _ = 1, rng.int(2, 4) do
      filth(ctx, "Filth_AnimalFilth", rng.int(pi.x, pi.x2), rng.int(pi.z, pi.z2))
    end

    -- E3: "a pen without animals is a fence" - MANDATORY, never optional.
    local kind = pen.nursery and "Chicken" or rng.pick({ "Muffalo", "Dromedary" })
    for _ = 1, rng.int(1, 2) do
      ctx:pawn(kind, rng.int(pi.x, pi.x2), rng.int(pi.z, pi.z2), "wild", "alive")
      total_animals = total_animals + 1
    end
  end

  -- ---- lane: 2 wide, PackedDirt, the full width of the row (pens AND the
  -- ---- utility column, so the feed store's own south door opens onto
  -- ---- paved lane too, not bare margin) -----------------------------------
  local lane = R(x0, z0, (pens_x2 + UTIL_W) - x0 + 1, LANE_H)
  floor_patch(ctx, lane, "PackedDirt")
  local lane_lights = 0
  if ctx:has_role("LIGHT") then
    for _ = 1, 2 do
      if try_near(ctx, "LIGHT", rng.int(lane.x, lane.x2), lane.z, 0, 1, lane) then lane_lights = lane_lights + 1 end
    end
  end

  -- ---- feed store (R-STORE) -> tack & tools (R-WORK): both shells built ---
  -- ---- FIRST (their shared wall row idempotently agrees), the one door ---
  -- ---- between them cut LAST (hutt_holding_pens.lua's own corridor order,
  -- ---- for exactly the same reason: a door cut before the second shell's
  -- ---- own wall_rect pass would get re-walled over as a collision).
  local ux = pens_x2 + 1
  local store = R(ux, z0 + LANE_H, UTIL_W, STORE_H)
  local sir = shell(ctx, "Storeroom", store, { floor = "FLOOR_POOR", doors = { { "S" } } })
  local tack = R(ux, store.z2, UTIL_W, TACK_H) -- z overlaps store's own north wall row on purpose
  local tir = shell(ctx, "Workshop", tack, { floor = "FLOOR_WORK", doors = { { "N" } } })
  local door_x = ux + 1
  ctx:door(door_x, store.z2) -- cuts the shared row once - both rooms open onto it

  -- feed store contents
  local hay_clumps = 0
  for _ = 1, rng.int(6, 10) do
    if place_near(ctx, "Hay", rng.int(sir.x, sir.x2), rng.int(sir.z, sir.z2), 1, "HAY") then
      hay_clumps = hay_clumps + 1
    end
  end
  local shelf_ok = try_near_walkable(ctx, "STORAGE", sir.x2, sir.z, 0, 1, sir, store)
  local butcher_ok, bx, bz = place_near(ctx, "ButcherSpot", sir.x, sir.z, 2, "WORKBENCH")
  if butcher_ok then filth(ctx, "Filth_Blood", bx, bz) end
  local kibble_placed = 0
  for _ = 1, rng.int(2, 3) do
    if place_near(ctx, "Kibble", rng.int(sir.x, sir.x2), rng.int(sir.z, sir.z2), 1, "KIBBLE") then
      kibble_placed = kibble_placed + 1
    end
  end
  wall_lights(ctx, sir, 1)

  -- tack & tools: ToolCabinet + Shelf stand in for the missing harness rack
  -- (LWM_Clothing_Rack is not indexed under tonight's active mod list - see
  -- header)
  dress(ctx, tir, {
    { role = "TOOL_CABINET", n = 1, where = "wall" },
    { role = "STORAGE", n = { 1, 2 }, where = "wall" },
  })
  filth(ctx, "Filth_Dirt", tir.x, tir.z)
  wall_lights(ctx, tir, 1)

  -- ---- the display: unwalled, at the row's east end -----------------------
  local display = R(ux, tack.z2 + 1, UTIL_W, DISPLAY_H)
  floor_patch(ctx, display, "FLOOR_YARD")
  local dcx, dcz = center(display)
  local display_note
  if o.hutt then
    local n1 = 0
    for _ = 1, rng.int(1, 2) do
      if place_near(ctx, "GibbetCage", dcx, dcz, 2, "TROPHY") then n1 = n1 + 1 end
    end
    place_near(ctx, "Skullspike", dcx + 1, dcz, 2, "TROPHY")
    display_note = string.format("Hutt display: %d GibbetCage, a Skullspike (a cage is a cage)", n1)
  else
    -- VFE_AnimalSarcophagus is not indexed tonight (see header) - DECOR
    -- (always real, palette default SculptureSmall) stands in rather than
    -- guess a defName for "a beloved one".
    ctx:place_role("DECOR", dcx, dcz, 0)
    display_note = "display: DECOR marker (VFE_AnimalSarcophagus not indexed tonight - substituted, not guessed)"
  end
  if ctx:has_role("TROPHY") then ctx:place_overlay("TROPHY", door_x, store.z, 0) end -- over the store door

  local wildsteam_bedroll = false
  if o.wildsteam then
    -- "keeper sleeps in a Bedroll among them" - ADDITIONAL to the base
    -- house (8.13 lists the keeper's house as a required room for every
    -- variant; the base grammar is not something one faction's flavour line
    -- gets to delete), not a replacement for it.
    -- road_warehouse.lua's own header names this trap: center() returns TWO
    -- values, and a multi-return is only expanded when it is the LAST
    -- argument - captured into named locals first, like every other
    -- center()/fr.cell() call in this codebase already does.
    local brx, brz = center(pens[1].rect)
    local ok2 = place_near(ctx, "Bedroll", brx, brz, 2, "BED")
    wildsteam_bedroll = ok2
  end

  local sizes_str = ""
  for i, pen in ipairs(pens) do
    sizes_str = sizes_str .. pen.rect.w .. "x" .. pen.rect.h
    if i < #pens then sizes_str = sizes_str .. "," end
  end

  note(string.format(
    "beast_pens: %d pen(s) [%s] nursery=pen1, %d fence cell(s), road_gate=%s, "
      .. "%d animal(s) stocked, %d sleeping box/bed(s), house_beds=%d "
      .. "store: %d hay clump(s) %d kibble butcher=%s shelf=%s tack=ok "
      .. "wildsteam_bedroll=%s | %s",
    n, sizes_str, total_fence, tostring(road_gate_done), total_animals, total_boxes, beds,
    hay_clumps, kibble_placed, tostring(butcher_ok), tostring(shelf_ok),
    tostring(wildsteam_bedroll), display_note))
end
