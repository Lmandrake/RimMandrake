-- homestead.lua - the humble abode -> homestead -> family compound family
-- (structure_procedural_spec.md section 8.1; roster #22 The Homestead).
--
-- EXTENDS dwelling.lua: its three canon branches are kept verbatim in spirit -
--   * Jawa_FreeDroidEnclaves get NO beds (the palette nulls BED; the sleeping
--     room becomes an R-WORK room with a gonk inside);
--   * Jawa_WildsteamClan is UNWALLED by ideology (rooms are floored and
--     furnished but no wall_rect/roof - and the sealed-room lint is told why);
--   * the COLD NURSERY (jawa_society.md 4.3a): a Jawa house in a hot place
--     gets a wall-mounted cooler at rot 0 and an EggBox NEST, and the plan
--     says out loud that a template cannot prove the room holds <=32C.
-- Its furnish pass is REPLACED (the spec's own word) by the R-SLEEP/R-HEARTH/
-- R-STORE/R-POWER recipes from section 4, placed by hug/clutter, never a loop.
-- The compound tier REPLACES junkers_dwelling_cluster.lua's row-of-boxes with
-- the section 8.1 yard grammar (shells around a shared fire, a pen, graves).
--
-- params:
--   tier      "abode" (1-2 people) | "homestead" (3-5) | "compound" (2-4 households)
--   occupants people; state "lived" (default) | "abandoned" | "ruined"
--   sun_dir   world side the sun is on ("E"...): that wall gets no window
--   faction/wealth/techLevel/climate/temperature_c as dwelling.lua reads them
--
-- Canvas (from build()'s own arithmetic, declared by min_rect; the spec's
-- 7x7 / 12x10 / 30x26 estimates forgot the threshold row and the lean-to):
--   abode      7x8   (room 7x7 over a 1-row threshold)
--   homestead  (7|11)x13 (+5 wide on Industrial+: the power apron) - one or two
--              bedrooms behind the hearth room, a 2-deep store lean-to on the
--              back wall, a porch row in front
--   compound   30x26 - up to four households in the quadrants, a commons in
--              the middle, a pen and a grave plot on the far edge
--
-- Conventions: local frame u (across) / v (depth, v=0 is the FRONT row where
-- the entry door opens). `frame()` maps local rects and sides to the world so
-- one household builder serves every rotation the compound needs.

-- ---------------------------------------------------------------------------
-- frame: a local (u,v) canvas W x H whose front (local S, v=0) faces `face`
-- in the world. rect(u,v,w,h) -> world R; side("S") -> world side.
-- ⚠️ Not in the prelude: this pass found no orientation helper there, and
-- mining_site.lua carries the same private copy. A prelude `frame()` would
-- remove both (reported, not silently promoted to engine code).
-- ---------------------------------------------------------------------------
local SIDE_MAP = {
  S = { S = "S", N = "N", E = "E", W = "W" },
  N = { S = "N", N = "S", E = "E", W = "W" },
  E = { S = "E", N = "W", E = "N", W = "S" },
  W = { S = "W", N = "E", E = "N", W = "S" },
}

local function frame(ox, oz, W, H, face)
  local f = { W = W, H = H, face = face }
  function f.rect(u, v, w, h)
    if face == "S" then return R(ox + u, oz + v, w, h)
    elseif face == "N" then return R(ox + u, oz + (H - v - h), w, h)
    elseif face == "E" then return R(ox + (H - v - h), oz + u, h, w)
    else return R(ox + v, oz + u, h, w) end
  end
  function f.cell(u, v) local r = f.rect(u, v, 1, 1) return r.x, r.z end
  function f.side(s) return SIDE_MAP[face][s] end
  function f.local_side(world_side)
    for k, v in pairs(SIDE_MAP[face]) do if v == world_side then return k end end
  end
  function f.bounds() return f.rect(0, 0, W, H) end
  return f
end

-- a raw defName placed with a ROLE tag, footprint-checked like a palette role
local function try_def(ctx, def, role, x, z, rot)
  rot = rot or 0
  if not ctx:can_place(def, x, z, rot) then return false end
  return ctx:place(def, x, z, rot, nil, role)
end

-- filth is a non-edifice that shares its cell; tag it so the render and the
-- secondary count both see it for what it is
local function filth(ctx, def, x, z)
  return ctx:place(def, x, z, 0, nil, "FILTH", true)
end

local function clamp(v, lo, hi) return math.max(lo, math.min(hi, v)) end

-- Place `def` so its footprint covers the LOCAL rect (u,v,lw,lh) of frame
-- `fr`, whichever way the frame faces (same helper as mining_site.lua: the
-- world rect decides the Rot4, origin_for applies the even-size shift).
local function place_local(ctx, fr, def, role, u, v, lw, lh, stuff)
  if def == nil then return false end
  local r = fr.rect(u, v, lw, lh)
  local dw, dh = ctx:width_of(def), ctx:height_of(def)
  local rot
  if dw == r.w and dh == r.h then rot = 0
  elseif dh == r.w and dw == r.h then rot = 1
  else
    ctx:refuse(def, string.format("is %dx%d, not the %dx%d the plan assumed", dw, dh, r.w, r.h))
    return false
  end
  local x, z = origin_for(r.x, r.z, r.w, r.h, rot)
  if not ctx:can_place(def, x, z, rot) then return false end
  return ctx:place(def, x, z, rot, stuff, role)
end

-- the walled rect around an interior, for clutter()'s walkability guard;
-- nil when there are no walls (Wildsteam) and so no door to flood from
local function walk_shell(o, ir)
  if o.unwalled then return nil end
  return R(ir.x - 1, ir.z - 1, ir.w + 2, ir.h + 2)
end

-- try_near, under the walkability guard when the room has a shell
local function near_walkable(ctx, role, x, z, radius, ir, sh)
  if sh then return try_near_walkable(ctx, role, x, z, 0, radius, ir, sh) end
  return try_near(ctx, role, x, z, 0, radius, ir)
end

-- One bed head-to-wall on `side` of interior ir, at a random slot whose
-- cells share no row/column with `avoid` (the first bed's cells) - two beds
-- on opposite walls of a 3-wide room on the SAME row are a wall across it.
local function bed_on_wall(ctx, ir, side, avoid)
  if not ctx:has_role("BED") then return false end
  local rot = SIDE_ROT[side]
  local w, h = rotated_dims(ctx, "BED", rot)
  local horizontal = (side == "N" or side == "S")
  local len, span = (horizontal and ir.w or ir.h), (horizontal and w or h)
  if span > len then return false end
  local slots = {}
  for t = 0, len - span do slots[#slots + 1] = t end
  shuffle(slots)
  if avoid and #avoid > 0 then
    -- the second bed goes as FAR along the wall from the first as it can:
    -- two beds in neighbouring rows leave a pocket nobody can reach
    local function dist(t)
      local best = 99
      for _, a in ipairs(avoid) do
        local along = horizontal and (a[1] - ir.x) or (a[2] - ir.z)
        best = math.min(best, math.abs(along - t))
      end
      return best
    end
    table.sort(slots, function(p, q) return dist(p) > dist(q) end)
  end
  for _, t in ipairs(slots) do
    local x0, z0
    if side == "N" then x0, z0 = ir.x + t, ir.z2 - h + 1
    elseif side == "S" then x0, z0 = ir.x + t, ir.z
    elseif side == "W" then x0, z0 = ir.x, ir.z + t
    else x0, z0 = ir.x2 - w + 1, ir.z + t end
    local clear = true
    for dx = 0, w - 1 do
      for dz = 0, h - 1 do
        local cx, cz = x0 + dx, z0 + dz
        if blocks_a_door(ctx, cx, cz, ir) then clear = false end
        for _, a in ipairs(avoid or {}) do
          if (horizontal and a[1] == cx) or (not horizontal and a[2] == cz) then clear = false end
        end
      end
    end
    if clear then
      local x, z = origin_for(x0, z0, w, h, rot)
      if try_place(ctx, "BED", x, z, rot) then
        local cells = {}
        for dx = 0, w - 1 do for dz = 0, h - 1 do cells[#cells + 1] = { x0 + dx, z0 + dz } end end
        return true, cells
      end
    end
  end
  return false
end

-- R4's density floor: ceil(interior_cells / 6), clamped to 2..8
local function clutter_n(ir, extra)
  return clamp(math.ceil((ir.w * ir.h) / 6) + (extra or 0), 2, 8)
end

-- the door cells already in the wall of rect r on `side`
local function doors_on(ctx, r, side)
  local out = {}
  for _, c in ipairs(wall_cells(r, side)) do
    if ctx:role_at(c[1], c[2]) == "DOOR" then out[#out + 1] = c end
  end
  return out
end

-- One wall-slot window on `side` of shell rect r: never a corner, never
-- within 1 of a door, only where a WALL actually stands. Returns true if cut.
local function window_on(ctx, r, side)
  if not ctx:has_role("WINDOW") then return false end
  local cells = wall_cells(r, side)
  local cand = {}
  for i = 2, #cells - 1 do
    local c = cells[i]
    if ctx:role_at(c[1], c[2]) == "WALL" then
      local near_door = false
      for _, d in ipairs({ cells[i - 1], cells[i + 1] }) do
        if ctx:role_at(d[1], d[2]) == "DOOR" then near_door = true end
      end
      if not near_door then cand[#cand + 1] = c end
    end
  end
  if #cand == 0 then return false end
  local c = cand[rng.int(1, #cand)]
  return ctx:window(c[1], c[2])
end

-- FLOOR_THRESHOLD outside an exterior door: 1 cell (poor), 1x3 (comfortable+)
local function threshold(ctx, dx, dz, side, wide, within)
  local d = DIR[SIDE_ROT[side]]
  local ox, oz = dx + d[1], dz + d[2]
  local cells = { { ox, oz } }
  if wide then
    local lat = (side == "N" or side == "S") and { 1, 0 } or { 0, 1 }
    cells[#cells + 1] = { ox + lat[1], oz + lat[2] }
    cells[#cells + 1] = { ox - lat[1], oz - lat[2] }
  end
  local n = 0
  for _, c in ipairs(cells) do
    if in_rect(c[1], c[2], within) and not ctx:occupied(c[1], c[2])
       and ctx:floor(c[1], c[2], ctx:role("FLOOR_THRESHOLD")) then n = n + 1 end
  end
  return n
end

-- tuck a role's whole footprint into a NAMED interior corner of r
local function corner_place(ctx, role, r, east, north, rot)
  if not ctx:has_role(role) then return false end
  local w, h = rotated_dims(ctx, role, rot)
  local x0 = east and (r.x2 - w + 1) or r.x
  local z0 = north and (r.z2 - h + 1) or r.z
  for dx = 0, w - 1 do
    for dz = 0, h - 1 do
      if blocks_a_door(ctx, x0 + dx, z0 + dz, r) then return false end
    end
  end
  local x, z = origin_for(x0, z0, w, h, rot)
  return try_place(ctx, role, x, z, rot)
end

-- ---------------------------------------------------------------------------
-- reading the params once
-- ---------------------------------------------------------------------------
local function read_opts(p)
  local o = {}
  o.faction = p.faction or "default"
  o.jawa = (o.faction == "Jawa_IndigenousTribes" or o.faction == "Jawa_Junkers")
  o.droid = (o.faction == "Jawa_FreeDroidEnclaves")
  o.unwalled = (o.faction == "Jawa_WildsteamClan")
  o.tusken = (o.faction == "TribeCivil")
  o.league = (o.faction == "OutlanderCivil")
  o.wealth = p.wealth or "modest"
  o.comfortable = (o.wealth == "comfortable" or o.wealth == "rich")
  o.destitute = (o.wealth == "destitute")
  o.tech = p.techLevel or "Neolithic"
  o.industrial = (o.tech == "Industrial" or o.tech == "Spacer" or o.tech == "Ultra" or o.tech == "Archotech")
  o.state = p.state or "lived"
  o.sun = p.sun_dir            -- world side, or nil
  o.latitude = p.latitude or "terminator"
  o.hot = (p.climate == "cool" or (p.temperature_c or 0) > 32)
  return o
end

-- the shell wrapper: walls+roof unless Wildsteam; ALWAYS a named floor.
-- Wildsteam declares NO room (there is no shell for the sealed/reachable/
-- roofed lint rules to judge, and dwelling.lua's "note it and let six
-- findings fire" left the lint unreadable); the floor and furniture are
-- laid exactly as for a walled house, on the same rects.
local function house_shell(ctx, o, label, r, doors, floor)
  if o.unwalled then
    local ir = inner(r)
    ctx:floor_rect(ir.x, ir.z, ir.w, ir.h, ctx:role(floor or "FLOOR"))
    for _, dd in ipairs(doors or {}) do
      -- no wall to cut a door into, but the "door" cell still anchors the
      -- path and threshold - mark it with the yard floor instead
      local x, z
      local side, at = dd[1], dd[2]
      if side == "N" or side == "S" then
        at = at or rng.int(2, math.max(2, r.w - 3)); x, z = r.x + at, (side == "N") and r.z2 or r.z
      else
        at = at or rng.int(2, math.max(2, r.h - 3)); x, z = (side == "E") and r.x2 or r.x, r.z + at
      end
      ctx:floor(x, z, ctx:role("FLOOR_THRESHOLD"))
    end
    return ir
  end
  return shell(ctx, label, r, { floor = floor or "FLOOR", doors = doors })
end

-- ---------------------------------------------------------------------------
-- R-SLEEP furnishing (the recipe, not a loop): beds hug walls that are not
-- the door wall, second bed on a DIFFERENT wall; a personal item is
-- guaranteed; then the clutter pass to R4's density.
-- ---------------------------------------------------------------------------
local function furnish_sleep(ctx, o, ir, beds, door_side, fr)
  local placed = 0
  if o.droid then
    -- CANON: droids do not sleep. R-WORK instead: a bench, a gonk, shelving.
    along_wall(ctx, "WORKBENCH", ir, rng.pick({ "N", "E", "W" }), 1, { gap = 1 })
    if ctx:has_role("GONK") then hug(ctx, "GONK", ir, { "E", "W" }) end
    along_wall(ctx, "STORAGE", ir, rng.pick({ "N", "E", "W" }), 1, { gap = 1 })
    clutter(ctx, ir, { { role = "CRATE", weight = 3 }, { role = "SHELF_SMALL", weight = 2 },
                       { role = "TERMINAL", weight = 1 } }, clutter_n(ir), walk_shell(o, ir))
    wall_lights(ctx, ir, 1)
    return 0
  end
  if not ctx:has_role("BED") then
    note("faction has no BED in its palette - sleeping room left with clutter only")
  else
    -- two beds go on OPPOSITE walls: in a 3x3 room two beds on adjacent
    -- walls box the corner cell between them (measured: 44% reachable)
    local pair = (door_side == "N" or door_side == "S") and { "E", "W" } or { "N", "S" }
    local rest = (door_side == "N" or door_side == "S") and { "N", "S" } or { "E", "W" }
    local sides = shuffle(pair)
    for _, s in ipairs(shuffle(rest)) do sides[#sides + 1] = s end
    local avoid = door_side
    local want = beds
    if o.comfortable and beds == 2 and ctx:has_role("BED_FINE") then
      -- a couple gets a double instead of two singles
      for _, s in ipairs(sides) do
        if s ~= avoid and along_wall(ctx, "BED_FINE", ir, s, 1, { face = "wall" }) == 1 then
          placed, want = 2, 0
          break
        end
      end
    end
    local first_cells = nil
    for _, s in ipairs(sides) do
      if want <= 0 then break end
      if s ~= avoid then
        -- one bed per wall (the mirror ban, by construction), and the second
        -- never in line with the first
        local ok, cells = bed_on_wall(ctx, ir, s, first_cells)
        if ok then
          placed, want = placed + 1, want - 1
          first_cells = first_cells or cells
        end
      end
    end
    if want > 0 then
      ctx:refuse("BED", string.format("%d of %d bed(s) did not fit this sleeping room", want, beds))
    end
  end
  -- personal item, guaranteed: chest at a bed foot, else end table, else candle
  local personal = false
  local bx, bz = center(ir)
  if #LAST_PLACED > 0 then bx, bz = LAST_PLACED[#LAST_PLACED][1], LAST_PLACED[#LAST_PLACED][2] end
  local sh = walk_shell(o, ir)
  for _, role in ipairs({ "CHEST", "END_TABLE", "FOOTLOCKER", "CANDLE", "PLANT_POT" }) do
    if ctx:has_role(role) then
      local ok = near_walkable(ctx, role, bx, bz, 2, ir, sh)
      if ok then personal = true break end
    end
  end
  if not personal then ctx:refuse("personal item", "no chest/end table/candle fitted in a sleeping room (R4)") end
  clutter(ctx, ir, {
    { role = "END_TABLE", weight = 4 }, { role = "DRESSER", weight = 3, where = "wall" },
    { role = "PLANT_POT", weight = 2 }, { role = "STOOL", weight = 2 },
    { role = "CANDLE", weight = 3 }, { role = "CHEST", weight = 2 },
    { role = "TROPHY", weight = 2 }, { role = "SIGN", weight = 1 },
  }, clutter_n(ir, o.comfortable and 1 or 0) - 1, walk_shell(o, ir))
  if o.tusken and ctx:has_role("TROPHY") then hug(ctx, "TROPHY", ir, { "N", "E", "W" }) end
  if o.jawa and ctx:has_role("NIGHT_LIGHT") and rng.chance(0.6) then
    hug(ctx, "NIGHT_LIGHT", ir, { "N", "E", "W" }, { mode = "corner" })
  end
  if o.latitude == "day" and ctx:has_role("COOLER_PASSIVE") then
    hug(ctx, "COOLER_PASSIVE", ir, { "N", "E", "W" }, { mode = "corner" })
  end
  wall_lights(ctx, ir, 1)
  return placed
end

-- R-HEARTH: hearth in a corner/wall away from the door, table free toward it,
-- 1-3 seats on two sides, food shelving, a barrel, dirt tracked in at the door.
local function furnish_hearth(ctx, o, ir, door_side, stove_sides)
  if o.droid then
    -- droids: the "hearth" room is a charging bay with a table for parts
    if ctx:has_role("CHARGER") then along_wall(ctx, "CHARGER", ir, rng.pick(stove_sides), 1, { gap = 1 }) end
    hug(ctx, "TABLE", ir, { "N", "E", "W" }, { mode = "free" })
  else
    local got = 0
    for _, s in ipairs(shuffle(stove_sides)) do
      if got > 0 then break end
      got = along_wall(ctx, "STOVE", ir, s, 1, { gap = 1 })
    end
    if got == 0 and ctx:has_role("STOVE") then
      got = hug(ctx, "STOVE", ir, stove_sides, { mode = "corner" })
    end
    if got == 0 and ctx:has_role("STOVE") then ctx:refuse("STOVE", "no wall cell in the hearth room fits it") end
    -- the table is the second impassable in the room: in a 3-wide hearth a
    -- table beside a 3-long stove can wall the stove off, so it is placed
    -- under the same walkability guard as the clutter
    local trot = rng.int(0, 1)
    local cx, cz = center(ir)
    local sh = walk_shell(o, ir)
    local ok, tx, tz
    if sh then
      ok, tx, tz = try_near_walkable(ctx, "TABLE", jitter(cx, 1), jitter(cz, 1), trot, 2, ir, sh)
    else
      ok, tx, tz = try_near(ctx, "TABLE", jitter(cx, 1), jitter(cz, 1), trot, 2, ir)
    end
    if ok then
      -- never four symmetric: 1-3 seats, and seat_around only ever fills a
      -- random subset of the sides
      local seat = ctx:has_role("CHAIR") and "CHAIR" or "STOOL"
      seat_around(ctx, seat, tx, tz, rng.int(1, 3), ir, trot)
    end
  end
  clutter(ctx, ir, {
    { role = "SHELF_SMALL", weight = 4, where = "wall" }, { role = "BARREL", weight = 3 },
    { role = "PLANT_POT", weight = 2 }, { role = "CRATE", weight = 2 },
    { role = "STOOL", weight = 2 }, { role = "GAME", weight = 1 },
  }, clutter_n(ir, o.comfortable and 1 or 0), walk_shell(o, ir))
  -- dirt tracked in from the door
  for _, d in ipairs(doors_on(ctx, R(ir.x - 1, ir.z - 1, ir.w + 2, ir.h + 2), door_side)) do
    local dd = DIR[opposite(SIDE_ROT[door_side])]
    for i = 1, rng.int(1, 2) do
      local fx, fz = d[1] + dd[1] * i, d[2] + dd[2] * i
      if in_rect(fx, fz, ir) then filth(ctx, "Filth_Dirt", fx, fz) end
    end
  end
  wall_lights(ctx, ir, 1)
  if ctx:has_role("LIGHT") then hug(ctx, "LIGHT", ir, { "N", "E", "W" }, { mode = "corner" }) end
end

-- R-STORE lean-to: perimeter shelving first, crates in corners, one lamp.
-- A 3x2 interior takes ONE shelf and one crate - R5's walkable-aisle rule
-- read literally: the door's flood-fill must still cover >=45% of the floor.
local function furnish_store(ctx, o, ir)
  local small = (ir.w * ir.h) <= 6
  local sh = walk_shell(o, ir)
  -- the first shelf goes in unguarded (nothing else is there to box; the
  -- door cell is kept clear by along_wall); everything after it is guarded
  local walls = shuffle({ "N", "E", "W", "S" })
  local shelves = 0
  for _, s in ipairs(walls) do
    if shelves >= 1 then break end
    shelves = shelves + along_wall(ctx, "STORAGE", ir, s, 1, { gap = 1 })
  end
  if not small and sh then
    local ok = try_near_walkable(ctx, "STORAGE", ir.x, ir.z2, 0, 3, ir, sh)
    if ok then shelves = shelves + 1 end
  end
  clutter(ctx, ir, {
    { role = "CRATE", weight = 4 }, { role = "BARREL", weight = small and 0 or 2 },
    { role = "JUNK", weight = small and 0 or 1 },
  }, small and 1 or 2, sh)
  dress(ctx, ir, { { role = "LIGHT", n = 1, where = "corner" } })
  if rng.chance(0.5) then filth(ctx, "Filth_Trash", rng.int(ir.x, ir.x2), rng.int(ir.z, ir.z2)) end
end


-- the cold nursery, exactly as dwelling.lua asserts it: cooler IN the back
-- (exterior) wall at the rotation that puts the cold side inside
local function cold_nursery(ctx, o, room_r, back)
  if not (o.jawa and o.hot) then return end
  if ctx:has_role("COOLER") then
    local cx, cz, rot
    if back == "N" then cx, cz, rot = room_r.x + 1, room_r.z2, 0
    elseif back == "S" then cx, cz, rot = room_r.x + 1, room_r.z, 2
    elseif back == "E" then cx, cz, rot = room_r.x2, room_r.z + 1, 1
    else cx, cz, rot = room_r.x, room_r.z + 1, 3 end
    ctx:wall_mount("COOLER", cx, cz, rot)
    note("cold nursery: cooler placed at rot 0 in the north wall. ⚠️ TEMPLATE CANNOT PROVE"
      .. " the room holds <=32C - that needs a live reading (see spec 5.3)")
  else
    ctx:refuse("COOLER", "faction tech has no cooler; nursery must be BURIED instead - "
      .. "unimplemented, needs excavation (spec 5.4, subterranean factions)")
  end
  if ctx:has_role("NEST") then
    local ir = inner(room_r)
    try_near(ctx, "NEST", rng.int(ir.x, ir.x2), rng.int(ir.z, ir.z2), 0, 2, ir)
  end
end

-- ---------------------------------------------------------------------------
-- ABODE: one room doing everything, over a threshold row. Local W x H, W>=7, H>=8.
-- ---------------------------------------------------------------------------
local function build_abode(ctx, fr, o, occ)
  local W, H = fr.W, fr.H
  local room = fr.rect(0, 1, W, H - 1)
  local door_side = fr.side("S")
  local ir = house_shell(ctx, o, "Abode", room, { { door_side } })
  local dcell = doors_on(ctx, room, door_side)[1]
  local within = fr.bounds()
  if dcell then threshold(ctx, dcell[1], dcell[2], door_side, o.comfortable, within) end

  -- bed in the corner farthest from the door
  if ctx:has_role("BED") and not o.droid then
    local north = (door_side ~= "N")
    local east
    if dcell then
      local cx, cz = center(ir)
      east = (dcell[1] <= cx)            -- door on the west half -> bed east
      if door_side == "E" or door_side == "W" then
        east = (door_side == "W")
        north = (dcell[2] <= cz)
      end
    else
      east, north = rng.chance(0.5), true
    end
    local wall_rot = north and 0 or 2
    if not corner_place(ctx, "BED", ir, east, north, wall_rot) then
      hug(ctx, "BED", ir, { fr.side("N"), fr.side("E"), fr.side("W") }, { face = "wall" })
    end
    if #LAST_PLACED > 0 then
      local b = LAST_PLACED[#LAST_PLACED]
      local ok = false
      local sh = walk_shell(o, ir)
      for _, role in ipairs({ "CHEST", "FOOTLOCKER", "END_TABLE", "CANDLE" }) do
        if ctx:has_role(role) and near_walkable(ctx, role, b[1], b[2], 2, ir, sh) then ok = true break end
      end
      if not ok then ctx:refuse("personal item", "nothing personal fitted by the bed (R4)") end
    end
    if occ >= 2 then
      -- a second sleeper: a different wall, never mirrored
      along_wall(ctx, "BED", ir, rng.pick({ fr.side("E"), fr.side("W") }), 1, { face = "wall", gap = 1 })
    end
  elseif o.droid then
    along_wall(ctx, "WORKBENCH", ir, fr.side("N"), 1, { gap = 1 })
    if ctx:has_role("GONK") then hug(ctx, "GONK", ir, { fr.side("E"), fr.side("W") }) end
  end
  -- hearth on a wall ADJACENT to the door (smoke goes out the door), table
  -- free between, seats
  furnish_hearth(ctx, o, ir, door_side, { fr.side("E"), fr.side("W") })
  -- one window on the long wall away from the sun; none on destitute
  if not o.destitute and not o.unwalled then
    local long = (room.w >= room.h) and { "N", "S" } or { "E", "W" }
    local cands = {}
    for _, s in ipairs(long) do
      if s ~= door_side and s ~= o.sun then cands[#cands + 1] = s end
    end
    if #cands > 0 then window_on(ctx, room, cands[rng.int(1, #cands)]) end
  end
  cold_nursery(ctx, o, room, fr.side("N"))
  -- §3.5 wants "remove the last secondary and retry"; the ctx API has no
  -- way to un-place a thing, so the proof is reported and lint's own
  -- aisle-blocked rule (the same fill) is the finding of record
  local ok, cov, unreached = aisle_ok(ctx, room)
  if not ok and not o.unwalled then
    note(string.format("abode aisle proof FAILED: %.0f%% reachable, %d primary unreached", cov * 100, unreached))
  end
  return { door = dcell, door_side = door_side }
end

-- ---------------------------------------------------------------------------
-- HOMESTEAD: hearth room at the front (entry door + porch), 1-2 bedrooms
-- behind it through corner-set interior doors, a store lean-to on the back
-- wall with its own door to the yard, a power apron beside it on Industrial+.
-- Local W x H: W >= (bedrooms==2 and 9 or 7) (+5 with power), H >= 13.
-- ---------------------------------------------------------------------------
-- Two bedrooms need 4-wide interiors: a 3x3 room with a mid-wall door and
-- two 1x2 beds is 44% walkable by geometry (both beds off the door row, one
-- corner cell boxed) - measured on every seed - so R-SLEEP's "3x3, up to 2
-- beds" and §3.5's 45% cannot both hold; the room grows, not the bar.
local function homestead_min(o, occ, nopower)
  local beds2 = (occ or 3) >= 4
  return (beds2 and 11 or 7) + ((o.industrial and not nopower) and 5 or 0), 13
end

local function build_homestead(ctx, fr, o, occ, nopower)
  local W, H = fr.W, fr.H
  local powered = o.industrial and not nopower and ctx:has_role("GENERATOR") and ctx:has_role("BATTERY") and ctx:has_role("CONDUIT")
  local apron = powered and 5 or 0
  local lean_h = (H >= 15) and 5 or 4                  -- lean-to interior 3 or 2 deep
  -- the main shell is capped at 11 wide x 13 deep (hearth 5, bedrooms 5);
  -- any canvas beyond that becomes side yard (`left`) and front yard (`front`)
  local Wm = math.min(W - apron, (occ >= 4) and 13 or 11)
  local Hm = math.min(H - 1 - (lean_h - 1), 13)
  local left = math.floor((W - apron - Wm) / 2)
  local front = H - (Hm + lean_h)
  local iw = Wm - 2
  local n_bed = ((occ >= 4) and iw >= 9) and 2 or 1
  local ih = Hm - 3
  local hh = clamp(math.floor(ih / 2), 3, 5)
  local bh = ih - hh
  if bh > 5 then hh = ih - 5; bh = 5 end
  local door_side = fr.side("S")
  local hearth_r = fr.rect(left, front + 1, Wm, hh + 2)
  local hi = house_shell(ctx, o, "Kitchen", hearth_r, { { door_side } })
  local dcell = doors_on(ctx, hearth_r, door_side)[1]
  local within = fr.bounds()
  -- porch: threshold (1 or 3 wide) + two posts + roof over the porch row
  if dcell then
    threshold(ctx, dcell[1], dcell[2], door_side, true, within)
    local d = DIR[SIDE_ROT[door_side]]
    local lat = (door_side == "N" or door_side == "S") and { 1, 0 } or { 0, 1 }
    local px, pz = dcell[1] + d[1], dcell[2] + d[2]
    local posts = 0
    for _, k in ipairs({ -2, 2 }) do
      local qx, qz = px + lat[1] * k, pz + lat[2] * k
      if in_rect(qx, qz, within) and try_place(ctx, "PILLAR", qx, qz, 0) then posts = posts + 1 end
    end
    if not o.unwalled then
      for k = -2, 2 do
        local qx, qz = px + lat[1] * k, pz + lat[2] * k
        if in_rect(qx, qz, within) then ctx:roof(qx, qz) end
      end
    end
    note(string.format("porch: %d post(s) and a roofed threshold at the entry", posts))
  end

  -- bedrooms behind the hearth; the shared wall row is hearth_r's back edge
  local bed_rects = {}
  if n_bed == 2 then
    local bw1 = clamp(math.floor(iw / 2) + rng.int(-1, 0), 4, iw - 5)
    bed_rects[1] = fr.rect(left, front + hh + 2, bw1 + 2, bh + 2)
    bed_rects[2] = fr.rect(left + bw1 + 1, front + hh + 2, Wm - bw1 - 1, bh + 2)
  else
    bed_rects[1] = fr.rect(left, front + hh + 2, Wm, bh + 2)
  end
  local beds_left = occ
  local sleep_door_side = door_side                 -- the bedrooms open onto the hearth: same world side
  for i, br in ipairs(bed_rects) do
    -- interior door near a corner, never centred, never in/adjacent a corner
    local len = (sleep_door_side == "N" or sleep_door_side == "S") and br.w or br.h
    local at = rng.chance(0.5) and 2 or math.max(2, len - 3)
    local label = o.droid and "Workshop" or ((occ > n_bed * 2) and "Barracks" or "Bedroom")
    local bi = house_shell(ctx, o, label, br, { { sleep_door_side, at } })
    local want = (i == #bed_rects) and beds_left or math.min(2, math.ceil(occ / n_bed))
    want = math.min(want, 2)
    local got = furnish_sleep(ctx, o, bi, want, sleep_door_side, fr)
    beds_left = beds_left - got
  end
  if beds_left > 0 and ctx:has_role("BED") and not o.droid then
    note(string.format("%d of %d occupant(s) have no bed - a homestead sleeps two to a room at most", beds_left, occ))
  end

  -- hearth furnishing: stove on the back (interior) wall, or the apron-side
  -- wall when it must reach the conduit bus within ConnectMaxDist 6
  local stove_sides = { fr.side("N") }
  if powered then stove_sides = { fr.side("E") } end
  furnish_hearth(ctx, o, hi, door_side, stove_sides)

  -- windows: one per 4-5 cells of exterior wall on the long sides, none on
  -- the sun wall, none within 1 of a door, none on destitute
  if not o.destitute and not o.unwalled then
    for _, s in ipairs({ "E", "W" }) do
      local ws = fr.side(s)
      if ws ~= o.sun and not (powered and s == "E") then
        local n = math.max(1, math.floor((Hm - 2) / 5))
        for _ = 1, n do
          if rng.chance(0.5) then window_on(ctx, hearth_r, ws) else window_on(ctx, bed_rects[rng.int(1, #bed_rects)], ws) end
        end
      end
    end
  end

  -- store lean-to on the back wall, its own door to the yard
  local lw = math.min(5, Wm)
  local lu = left + rng.int(0, Wm - lw)
  local L = fr.rect(lu, front + Hm, lw, lean_h)
  local lean_sides = { "E", "W", "N" }
  local lside = fr.side(lean_sides[rng.int(1, #lean_sides)])
  local li = house_shell(ctx, o, "Storeroom", L, { { lside } }, "FLOOR_POOR")
  furnish_store(ctx, o, li)
  local ld = doors_on(ctx, L, lside)[1]
  if ld then threshold(ctx, ld[1], ld[2], lside, false, within) end

  -- power apron on the local E of the main shell (R-POWER): a conduit bus
  -- outside the wall, cardinally contiguous from the generator to the
  -- battery; connectors inside reach it through the wall within 6.
  if powered then
    local bus_u = left + Wm                            -- the column just outside the apron-side wall
    local vg = front + 4                               -- 4x4 generator: cells rows vg-1..vg+2, cols bus_u+1..bus_u+4
    local pad = fr.rect(bus_u + 1, front + 2, 4, 5)
    ctx:floor_rect(pad.x, pad.z, pad.w, pad.h, ctx:role("FLOOR_WORK"))
    if not place_local(ctx, fr, ctx:role("GENERATOR"), "GENERATOR", bus_u + 1, vg - 1, 4, 4, ctx:role("GENERATOR_STUFF")) then
      ctx:refuse("GENERATOR", "the apron pad refused it")
    end
    local vb = front + Hm - 2                          -- battery rows vb, vb+1 (local), cardinal on the bus end
    for v = front + 2, vb - 1 do
      local cx, cz = fr.cell(bus_u, v)
      ctx:place_role("CONDUIT", cx, cz, 0)
    end
    if not place_local(ctx, fr, ctx:role("BATTERY"), "BATTERY", bus_u, vb, 1, 2, ctx:role("BATTERY_STUFF")) then
      ctx:refuse("BATTERY", "no room on the bus end for the battery")
    end
    -- a lean-to over the battery: roof + one post
    for v = vb, vb + 1 do
      for u = bus_u, bus_u + 1 do
        local rx, rz = fr.cell(u, v)
        ctx:roof(rx, rz)
      end
    end
    local px, pz = fr.cell(bus_u + 1, vb + 1)
    try_place(ctx, "PILLAR", px, pz, 0)
    for _ = 1, rng.int(2, 4) do
      local fx, fz = fr.cell(bus_u + rng.int(0, 4), front + rng.int(1, 8))
      if in_rect(fx, fz, within) then filth(ctx, "Filth_MachineBits", fx, fz) end
    end
    note("R-POWER: generator + battery are TRANSMITTERS on a cardinal conduit bus outside the "
      .. "apron-side wall; stove/lamps are CONNECTORS within ConnectMaxDist 6 through the wall")
    if o.jawa and ctx:has_role("GONK") then
      local ggx, ggz = fr.cell(bus_u + 3, front + Hm - 3)
      try_place(ctx, "GONK", ggx, ggz, 0)
    end
  elseif o.jawa and ctx:has_role("GONK") then
    -- the Jawa "generator" is a gonk in the yard even when nothing is wired
    local gx, gz = fr.cell(left + rng.int(1, Wm - 2), front)
    if not ctx:occupied(gx, gz) then try_place(ctx, "GONK", gx, gz, 0) end
  end

  -- front yard, when the canvas gave one: a worn path to the porch, a crate
  -- by the door, a barrel under the eave
  if front >= 2 and dcell then
    local d = DIR[SIDE_ROT[door_side]]
    local px, pz = dcell[1] + d[1] * 2, dcell[2] + d[2] * 2
    local lat = (door_side == "N" or door_side == "S") and { 1, 0 } or { 0, 1 }
    for i = 0, front - 2 do
      local qx, qz = px + d[1] * i, pz + d[2] * i
      if i % 3 == 2 then qx, qz = qx + lat[1] * rng.int(-1, 1), qz + lat[2] * rng.int(-1, 1) end
      if in_rect(qx, qz, within) and not ctx:occupied(qx, qz) then ctx:floor(qx, qz, ctx:role("FLOOR_YARD")) end
    end
    local yard = fr.rect(0, 0, W, front)
    scatter(ctx, "CRATE", yard, rng.int(0, 2))
    scatter(ctx, "BARREL", yard, rng.int(0, 1))
    if front >= 4 then
      local wx = center(yard)
      try_near(ctx, "WATER", jitter(wx, 2), yard.z + 1, 0, 2, yard)
    end
  end

  cold_nursery(ctx, o, bed_rects[#bed_rects], fr.side("N"))
  for _, r in ipairs({ hearth_r, bed_rects[1], bed_rects[2] or hearth_r, L }) do
    local ok, cov, un = aisle_ok(ctx, r)
    if not ok and not o.unwalled and cov > 0 then
      note(string.format("aisle proof FAILED for the room at (%d,%d): %.0f%% reachable, %d primary unreached", r.x, r.z, cov * 100, un))
    end
  end
  return { door = dcell, door_side = door_side, powered = powered }
end

-- ---------------------------------------------------------------------------
-- COMPOUND: 2-4 households around a shared yard. Quadrant frames face the
-- centre; shells never share a wall (>=3 cells between); the commons has a
-- fire with three seats and the family water off-axis; one pen on the far
-- edge, a grave plot in the far corner; a faction perimeter with one gate.
-- ---------------------------------------------------------------------------
local function build_compound(ctx, o, occ)
  local lot = R(rect.x, rect.z, rect.w, rect.h)
  local W, H = rect.w, rect.h
  -- perimeter ring at the footprint edge, quadrants inset by 2 (ring + alley)
  local inset = 2
  local qw = math.min(14, math.floor((W - 2 * inset - 7) / 2))
  local qh = math.min(14, math.floor((H - 2 * inset - 7) / 2))
  local households = {}
  local quads = shuffle({ "NW", "NE", "SW", "SE" })
  local n_house = clamp(math.ceil(occ / 3), 2, 4)
  local left = occ
  for i = 1, n_house do
    local q = quads[i]
    local west = (q == "NW" or q == "SW")
    local south = (q == "SW" or q == "SE")
    -- the front faces the yard centre: pick the axis with the longer run
    local face = rng.chance(0.5) and (south and "N" or "S") or (west and "E" or "W")
    local people = (i == n_house) and left or clamp(math.ceil(occ / n_house), 1, 5)
    left = left - people
    local tier = (people >= 3) and "homestead" or "abode"
    local mw, mh
    -- compound households are unpowered shells: one apron per household
    -- would eat the yard, and the spec gives the compound a shared fire, not
    -- a shared grid (an R-POWER for the whole compound is a later pass)
    if tier == "homestead" then mw, mh = homestead_min(o, people, true) else mw, mh = 7, 8 end
    -- world extents of this frame: (mw x mh) or transposed
    local ww, wh = mw, mh
    if face == "E" or face == "W" then ww, wh = mh, mw end
    if ww > qw or wh > qh then
      -- try the other axis, then drop to an abode
      face = (face == "N" or face == "S") and (west and "E" or "W") or (south and "N" or "S")
      ww, wh = wh, ww
      if ww > qw or wh > qh then
        tier, mw, mh = "abode", 7, 8
        ww, wh = mw, mh
        if face == "E" or face == "W" then ww, wh = mh, mw end
      end
    end
    -- room to grow: use the quadrant's spare width for a bigger hearth/yard
    local W_use = math.min(qw, ww + rng.int(0, 2))
    local H_use = math.min(qh, wh + rng.int(0, 2))
    local jx, jz = rng.int(0, 1), rng.int(0, 1)
    local ox = west and (rect.x + inset + jx) or (rect.x2 - inset - W_use + 1 - jx)
    local oz = south and (rect.z + inset + jz) or (rect.z2 - inset - H_use + 1 - jz)
    local fw, fh = W_use, H_use
    if face == "E" or face == "W" then fw, fh = H_use, W_use end
    local fr = frame(ox, oz, fw, fh, face)
    local info
    if tier == "homestead" then info = build_homestead(ctx, fr, o, people, true) else info = build_abode(ctx, fr, o, people) end
    households[#households + 1] = { q = q, rect = R(ox, oz, W_use, H_use), info = info, tier = tier, people = people }
  end
  note(string.format("compound: %d household(s) for %d people", #households, occ))

  -- the commons: a fire, three seats, the water off-axis
  local cx, cz = center(lot)
  local fx, fz = jitter(cx, 1), jitter(cz, 1)
  local fire = o.droid and "GONK" or (ctx:has_role("BRAZIER") and "BRAZIER" or "STOVE")
  if try_place(ctx, fire, fx, fz, 0) then
    floor_patch(ctx, R(fx - 1, fz - 1, 3, 3), "FLOOR_YARD", lot)
    local seats = 0
    for _, c in ipairs(shuffle({ { fx - 1, fz - 1, 1 }, { fx + 1, fz - 1, 3 }, { fx - 1, fz + 1, 1 },
                                 { fx + 1, fz + 1, 3 }, { fx, fz - 2, 0 }, { fx, fz + 2, 2 },
                                 { fx - 2, fz, 1 }, { fx + 2, fz, 3 } })) do
      if seats >= 3 then break end
      local role = (seats == 0 and ctx:has_role("BENCH")) and "BENCH" or "STOOL"
      if try_place(ctx, role, c[1], c[2], c[3]) then seats = seats + 1 end
    end
  end
  do
    -- water 2-3 off the fire, never on the fire's axis
    local wx, wz = fx + rng.pick({ -3, -2, 2, 3 }), fz + rng.pick({ -2, 2 })
    if o.league then
      -- Homestead League: the free well is the faith; it goes OUTSIDE at the gate
      wx, wz = fx, fz
    end
    if not o.league then try_near(ctx, "WATER", wx, wz, 0, 1, lot) end
  end
  -- worn paths from each door toward the fire: one Manhattan step at a time
  -- toward the fire, nudged sideways every third cell so it is not a ruler
  for _, h in ipairs(households) do
    local d = h.info.door
    if d then
      local dd = DIR[SIDE_ROT[h.info.door_side]]
      local px, pz = d[1] + dd[1] * 2, d[2] + dd[2] * 2
      for step = 1, 14 do
        if math.abs(px - fx) + math.abs(pz - fz) <= 2 then break end
        if in_rect(px, pz, lot) and not ctx:occupied(px, pz) then ctx:floor(px, pz, ctx:role("FLOOR_YARD")) end
        local sx = (fx > px) and 1 or ((fx < px) and -1 or 0)
        local sz = (fz > pz) and 1 or ((fz < pz) and -1 or 0)
        if step % 3 == 0 and sx ~= 0 and sz ~= 0 then
          if rng.chance(0.5) then px = px + sx else pz = pz + sz end
        elseif math.abs(px - fx) >= math.abs(pz - fz) then px = px + sx
        else pz = pz + sz end
      end
    end
  end

  -- R-PEN on the far (north) edge band between the two north quadrants, if
  -- the band is wide enough; else on whichever quadrant was left empty
  local keep = {}
  for _, h in ipairs(households) do keep[#keep + 1] = R(h.rect.x - 1, h.rect.z - 1, h.rect.w + 2, h.rect.h + 2) end
  local free_q = quads[n_house + 1]
  local pen_r
  if free_q then
    local west = (free_q == "NW" or free_q == "SW")
    local south = (free_q == "SW" or free_q == "SE")
    local pw, ph = math.min(6, qw), math.min(6, qh)
    local px = west and (rect.x + inset) or (rect.x2 - inset - pw + 1)
    local pz = south and (rect.z + inset) or (rect.z2 - inset - ph + 1)
    pen_r = R(px, pz, pw, ph)
  else
    local pw = 5
    local px = cx - 2 + rng.int(-1, 1)
    pen_r = R(px, rect.z2 - inset - 5 + 1, pw, 5)
    for _, k in ipairs(keep) do if rect_overlaps(pen_r, k) then pen_r = nil break end end
  end
  if pen_r and ctx:has_role("FENCE") then
    local fenced = 0
    local gate_done = false
    local edges = {}
    for x = pen_r.x, pen_r.x2 do edges[#edges + 1] = { x, pen_r.z }; edges[#edges + 1] = { x, pen_r.z2 } end
    for z = pen_r.z + 1, pen_r.z2 - 1 do edges[#edges + 1] = { pen_r.x, z }; edges[#edges + 1] = { pen_r.x2, z } end
    local gate_i = rng.int(2, #edges - 1)
    for i, c in ipairs(edges) do
      local role = (i == gate_i and ctx:has_role("GATE")) and "GATE" or "FENCE"
      if try_place(ctx, role, c[1], c[2], 0) then fenced = fenced + 1; if role == "GATE" then gate_done = true end end
    end
    local pi = inner(pen_r)
    floor_patch(ctx, pi, "FLOOR_YARD", lot)
    do local mx, mz = center(pi); try_def(ctx, "PenMarker", "PEN_MARKER", mx, mz, 0) end
    local boxes = rng.int(1, 2)
    for _, s in ipairs(shuffle({ "N", "E", "S", "W" })) do
      if boxes <= 0 then break end
      boxes = boxes - along_wall(ctx, "ANIMAL_BED", pi, s, 1, { gap = 1 })
    end
    if not o.league then hug(ctx, "TROUGH", pi, { "N", "E", "S", "W" }) end
    for _ = 1, rng.int(1, 3) do
      local hx, hz = rng.int(pi.x, pi.x2), rng.int(pi.z, pi.z2)
      try_def(ctx, "Hay", "HAY", hx, hz, 0)
    end
    for _ = 1, rng.int(2, 4) do filth(ctx, "Filth_AnimalFilth", rng.int(pi.x, pi.x2), rng.int(pi.z, pi.z2)) end
    note(string.format("pen: %d fence cell(s), gate %s", fenced, gate_done and "set" or "missing"))
  end

  -- grave plot in a far corner strip (lattice allowed, one turned)
  if ctx:has_role("GRAVE") then
    local gx0 = rng.chance(0.5) and (rect.x + 1) or (rect.x2 - 2)
    local gz0 = rect.z2 - inset - 1
    local graves = 0
    for i = 0, rng.int(0, 3) do
      local gx, gz = gx0 + (gx0 < cx and i * 2 or -i * 2), gz0 - rng.int(0, 1)
      local rot = (i == 1) and 1 or 0
      local clear = true
      for _, k in ipairs(keep) do if in_rect(gx, gz, k) then clear = false end end
      if clear and in_rect(gx, gz, lot) and try_place(ctx, "GRAVE", gx, gz, rot) then graves = graves + 1 end
    end
    if graves > 0 then note(string.format("grave plot: %d", graves)) end
  end

  -- the perimeter: sandbags (Jawa/Junkers), fence (Homestead League), a low
  -- wall (Deepwater), none (Wildsteam); one gate off-centre on the south
  local peri
  if o.unwalled then peri = nil
  elseif o.league then peri = "FENCE"
  elseif o.faction == "Jawa_DeepwaterCompact" then peri = "WALL"
  else peri = ctx:has_role("SANDBAG") and "SANDBAG" or "FENCE" end
  if peri then
    local gate_x = rect.x + rng.int(3, W - 4)
    if gate_x == rect.x + math.floor(W / 2) then gate_x = gate_x + 1 end
    local n = 0
    for x = rect.x, rect.x2 do
      for _, z in ipairs({ rect.z, rect.z2 }) do
        local is_gate = (z == rect.z and (x == gate_x or x == gate_x + 1))
        if is_gate then
          if peri == "FENCE" and ctx:has_role("GATE") and x == gate_x then try_place(ctx, "GATE", x, z, 0) end
        elseif not rng.chance(peri == "SANDBAG" and 0.08 or 0.0) then
          if try_place(ctx, peri, x, z, 0) then n = n + 1 end
        end
      end
    end
    for z = rect.z + 1, rect.z2 - 1 do
      for _, x in ipairs({ rect.x, rect.x2 }) do
        if not rng.chance(peri == "SANDBAG" and 0.08 or 0.0) and try_place(ctx, peri, x, z, 0) then n = n + 1 end
      end
    end
    -- sign at the gate; the League's trough OUTSIDE the fence
    if ctx:has_role("SIGN") then try_place(ctx, "SIGN", gate_x - 1, rect.z + 1, 0) end
    if o.league then
      try_near(ctx, "WATER", gate_x + 2, rect.z + 1, 0, 1, lot)
      try_near(ctx, "TROUGH", gate_x + 3, rect.z + 1, 0, 1, lot)
    end
    note(string.format("perimeter: %d %s cell(s), gate at x=%d", n, peri:lower(), gate_x))
  else
    note("Wildsteam: no perimeter, no walls - open under the trees by ideology")
  end
  -- yard clutter: crates by doors, a barrel under an eave, a chunk someone
  -- meant to move, a cactus in a pot
  local yard = inner(lot, inset)
  scatter(ctx, "CRATE", yard, rng.int(1, 3), { keep_clear = keep })
  scatter(ctx, "BARREL", yard, rng.int(0, 2), { keep_clear = keep })
  scatter(ctx, "PLANT_POT", yard, rng.int(0, 2), { keep_clear = keep })
  for _ = 1, rng.int(1, 2) do
    local sx, sz = rng.int(yard.x, yard.x2), rng.int(yard.z, yard.z2)
    local ok = true
    for _, k in ipairs(keep) do if in_rect(sx, sz, k) then ok = false end end
    if ok then try_def(ctx, ctx:role("ROCK_CHUNK") or "ChunkSandstone", "SCRAP", sx, sz, 0) end
  end
  if ctx:has_role("LIGHT") then scatter(ctx, "LIGHT", yard, 1, { keep_clear = keep }) end
end

-- ---------------------------------------------------------------------------
-- entry points
-- ---------------------------------------------------------------------------
function min_rect(params)
  local o = read_opts(params)
  local tier = params.tier or "homestead"
  local occ = params.occupants or ((tier == "abode") and 2 or ((tier == "compound") and 8 or 4))
  if tier == "abode" then return 7, 8 end
  if tier == "compound" then return 30, 26 end
  return homestead_min(o, occ)
end

function build(ctx)
  local p = params
  local o = read_opts(p)
  local tier = p.tier or "homestead"
  local occ = p.occupants or ((tier == "abode") and 2 or ((tier == "compound") and 8 or 4))
  if o.unwalled then note("Wildsteam: unwalled by ideology - sealed-room checks do not apply") end

  if tier == "compound" then
    build_compound(ctx, o, occ)
  else
    -- the whole canvas is one household; the front is the south edge unless
    -- the caller says which world side the road is on
    local face = p.road_dir or "S"
    local W, H = rect.w, rect.h
    if face == "E" or face == "W" then W, H = rect.h, rect.w end
    local fr = frame(rect.x, rect.z, W, H, face)
    if tier == "abode" then
      build_abode(ctx, fr, o, math.min(occ, 2))
    else
      build_homestead(ctx, fr, o, math.min(occ, 5))
    end
  end

  -- state: dust drifts in when nobody lives here; the ruin pass when it fell
  if o.state == "abandoned" then
    local n = 0
    for _ = 1, math.max(4, math.floor(rect.w * rect.h / 25)) do
      local x, z = rng.int(rect.x, rect.x2), rng.int(rect.z, rect.z2)
      if not ctx:occupied(x, z) then filth(ctx, rng.chance(0.6) and "Filth_Sand" or "Filth_Dirt", x, z); n = n + 1 end
    end
    note(string.format("abandoned: %d drift(s) of sand and dirt; the layout stands", n))
  elseif o.state == "ruined" then
    ctx:ruin(0.3)
  end
end
