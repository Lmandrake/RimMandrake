-- rimplace prelude - the placement helpers EVERY template gets.
--
-- Loaded by luaenv._sandboxed_runtime after the sandbox has stripped the
-- forbidden names and before the template's own source runs, so this file
-- lives under exactly the fence a template does: it can only reach the
-- documented ctx API and the seeded `rng`. Its sha256 rides on every plan as
-- meta.prelude_sha256 next to the template's own hash.
--
-- WHY THIS EXISTS (owner's live review, TILE_STRUCTURE_REVIEW_SAVE_1):
--   "A LOT more work is required to make realistic rooms... try much harder
--    on them all and not accept any rooms yet."
-- Three named defects, and the helpers here are the answer to each:
--   1. FLOORING     - shell() floors every interior explicitly with a named
--                     terrain, never the palette's bare-ground default.
--   2. REGULAR GRIDS - scatter()/along_wall()/dress() place by seeded random
--                     choice with gaps and skips; there is no fixed-step loop
--                     anywhere in this file, and none should be written in a
--                     template either.
--   3. CLUTTER      - dress() is the secondary-furniture pass: stools, crates,
--                     barrels, lamps, plants, the things that make a room read
--                     as lived in rather than furnished.
--
-- Conventions (RimWorld Rot4): 0 = north (+z), 1 = east (+x), 2 = south (-z),
-- 3 = west (-x). Sides are "N" "E" "S" "W". A rect is {x, z, w, h, x2, z2}.
-- Every helper returns what it actually placed; a template reads the count
-- and refuses or notes rather than assuming.

local floor = math.floor
local abs = math.abs

-- ---------------------------------------------------------------------------
-- geometry
-- ---------------------------------------------------------------------------
function R(x, z, w, h)
  return { x = x, z = z, w = w, h = h, x2 = x + w - 1, z2 = z + h - 1 }
end

function inner(r, pad)
  pad = pad or 1
  return R(r.x + pad, r.z + pad, r.w - 2 * pad, r.h - 2 * pad)
end

function in_rect(x, z, r)
  return x >= r.x and x <= r.x2 and z >= r.z and z <= r.z2
end

function rect_overlaps(a, b)
  return not (a.x2 < b.x or b.x2 < a.x or a.z2 < b.z or b.z2 < a.z)
end

function center(r)
  return r.x + floor(r.w / 2), r.z + floor(r.h / 2)
end

DIR = { [0] = { 0, 1 }, [1] = { 1, 0 }, [2] = { 0, -1 }, [3] = { -1, 0 } }
SIDE_ROT = { N = 0, E = 1, S = 2, W = 3 }

function opposite(rot) return (rot + 2) % 4 end

-- the four interior corner cells of r, in a random order
function corners(r)
  return shuffle({ { r.x, r.z }, { r.x2, r.z }, { r.x, r.z2 }, { r.x2, r.z2 } })
end

-- the interior cells hugging one wall of r, in walking order
function wall_cells(r, side)
  local cells = {}
  if side == "N" then for x = r.x, r.x2 do cells[#cells + 1] = { x, r.z2 } end
  elseif side == "S" then for x = r.x, r.x2 do cells[#cells + 1] = { x, r.z } end
  elseif side == "E" then for z = r.z, r.z2 do cells[#cells + 1] = { r.x2, z } end
  else for z = r.z, r.z2 do cells[#cells + 1] = { r.x, z } end end
  return cells
end

-- ---------------------------------------------------------------------------
-- rng (seeded; same seed, same house)
-- ---------------------------------------------------------------------------
function jitter(v, j)
  if not j or j <= 0 then return v end
  return v + rng.int(-j, j)
end

function shuffle(t)
  for i = #t, 2, -1 do
    local j = rng.int(1, i)
    t[i], t[j] = t[j], t[i]
  end
  return t
end

function pick_n(t, n)
  local s = {}
  for i = 1, #t do s[i] = t[i] end
  shuffle(s)
  local out = {}
  for i = 1, math.min(n, #s) do out[i] = s[i] end
  return out
end

-- ---------------------------------------------------------------------------
-- placing
-- ---------------------------------------------------------------------------
-- the wall cell just past interior cell (x,z) on `side` holds a door
function door_in_front(ctx, x, z, side)
  local d = DIR[SIDE_ROT[side]]
  return ctx:role_at(x + d[1], z + d[2]) == "DOOR"
end

-- never block the cell inside any door of interior rect r
function blocks_a_door(ctx, x, z, r)
  if z == r.z2 and door_in_front(ctx, x, z, "N") then return true end
  if z == r.z and door_in_front(ctx, x, z, "S") then return true end
  if x == r.x2 and door_in_front(ctx, x, z, "E") then return true end
  if x == r.x and door_in_front(ctx, x, z, "W") then return true end
  return false
end

function try_place(ctx, role, x, z, rot)
  rot = rot or 0
  if not ctx:has_role(role) then return false end
  if not ctx:can_place(role, x, z, rot) then return false end
  return ctx:place_role(role, x, z, rot)
end

-- the cell, then rings around it out to `radius`, in random order; `within`
-- (a rect) bounds the search. Returns ok, x, z.
function try_near(ctx, role, x, z, rot, radius, within)
  radius = radius or 1
  for ring = 0, radius do
    local cells = {}
    for dz = -ring, ring do
      for dx = -ring, ring do
        if math.max(abs(dx), abs(dz)) == ring then cells[#cells + 1] = { x + dx, z + dz } end
      end
    end
    shuffle(cells)
    for _, c in ipairs(cells) do
      if (within == nil or in_rect(c[1], c[2], within))
         and not (within and blocks_a_door(ctx, c[1], c[2], within))
         and try_place(ctx, role, c[1], c[2], rot) then
        return true, c[1], c[2]
      end
    end
  end
  return false
end

-- Up to n random placements inside rect r.
-- opts.rot: a Rot4, or "any"; opts.tries; opts.avoid(x,z)->true to reject a cell;
-- opts.keep_clear: list of rects never to land in.
function scatter(ctx, role, r, n, opts)
  opts = opts or {}
  if n <= 0 or not ctx:has_role(role) then return 0 end
  local placed, tries = 0, 0
  local max_tries = opts.tries or n * 20
  while placed < n and tries < max_tries do
    tries = tries + 1
    local x, z = rng.int(r.x, r.x2), rng.int(r.z, r.z2)
    local ok = not blocks_a_door(ctx, x, z, r)
    if ok and opts.avoid and opts.avoid(x, z) then ok = false end
    if ok and opts.keep_clear then
      for _, k in ipairs(opts.keep_clear) do
        if in_rect(x, z, k) then ok = false break end
      end
    end
    if ok then
      local rot = opts.rot
      if rot == nil then rot = 0 elseif rot == "any" then rot = rng.int(0, 3) end
      if try_place(ctx, role, x, z, rot) then placed = placed + 1 end
    end
  end
  return placed
end

-- Up to n of a role hugging one wall of interior rect r, at RANDOM slots with
-- at least opts.gap cells between two of them - never a fixed stride.
-- opts.rot defaults to facing away from the wall (a bed's head, a shelf's back).
function along_wall(ctx, role, r, side, n, opts)
  opts = opts or {}
  if n <= 0 or not ctx:has_role(role) then return 0 end
  local rot = opts.rot
  if rot == nil then rot = opposite(SIDE_ROT[side]) end
  local gap = opts.gap or 0
  local placed, taken = 0, {}
  for _, c in ipairs(shuffle(wall_cells(r, side))) do
    if placed >= n then break end
    local x, z = c[1], c[2]
    local far = true
    for _, t in ipairs(taken) do
      if abs(x - t[1]) + abs(z - t[2]) <= gap then far = false break end
    end
    if far and not blocks_a_door(ctx, x, z, r)
       and try_place(ctx, role, x, z, rot) then
      placed = placed + 1
      taken[#taken + 1] = { x, z }
    end
  end
  return placed
end

-- Wall lamps on n random interior wall cells of r, each facing its wall.
function wall_lights(ctx, r, n, role)
  role = role or "WALL_LIGHT"
  if n <= 0 or not ctx:has_role(role) then return 0 end
  local slots = {}
  for _, side in ipairs({ "N", "E", "S", "W" }) do
    for _, c in ipairs(wall_cells(r, side)) do
      slots[#slots + 1] = { c[1], c[2], SIDE_ROT[side] }
    end
  end
  local placed = 0
  for _, s in ipairs(shuffle(slots)) do
    if placed >= n then break end
    if ctx:wall_attach(role, s[1], s[2], s[3]) then placed = placed + 1 end
  end
  return placed
end

-- Chairs/stools around a table already placed at origin (tx,tz), rot 0,
-- on random sides, each facing the table. Returns how many sat down.
function seat_around(ctx, role, tx, tz, n, within)
  if n <= 0 or not ctx:has_role(role) then return 0 end
  local tw, th = ctx:width_of("TABLE"), ctx:height_of("TABLE")
  local x0 = tx - floor((tw - 1) / 2)
  local z0 = tz - floor((th - 1) / 2)
  local cand = {}
  for x = x0, x0 + tw - 1 do
    cand[#cand + 1] = { x, z0 - 1, 0 }        -- south of the table, facing north
    cand[#cand + 1] = { x, z0 + th, 2 }       -- north, facing south
  end
  for z = z0, z0 + th - 1 do
    cand[#cand + 1] = { x0 - 1, z, 1 }        -- west, facing east
    cand[#cand + 1] = { x0 + tw, z, 3 }       -- east, facing west
  end
  local placed = 0
  for _, c in ipairs(shuffle(cand)) do
    if placed >= n then break end
    if (within == nil or (in_rect(c[1], c[2], within) and not blocks_a_door(ctx, c[1], c[2], within)))
       and try_place(ctx, role, c[1], c[2], c[3]) then
      placed = placed + 1
    end
  end
  return placed
end

-- THE CLUTTER PASS. spec is a list of { role=, n= (number or {min,max}),
-- where= "wall" | "corner" | "any" (default), rot= }. Every entry is optional
-- in the sense that a palette without the role simply contributes nothing.
function dress(ctx, r, spec)
  local total = 0
  for _, s in ipairs(spec) do
    if ctx:has_role(s.role) then
      local n = s.n or 1
      if type(n) == "table" then n = rng.int(n[1], n[2]) end
      local got = 0
      if s.where == "corner" then
        for _, c in ipairs(corners(r)) do
          if got >= n then break end
          if not blocks_a_door(ctx, c[1], c[2], r)
             and try_place(ctx, s.role, c[1], c[2], s.rot or 0) then got = got + 1 end
        end
      elseif s.where == "wall" then
        for _, side in ipairs(shuffle({ "N", "E", "S", "W" })) do
          if got >= n then break end
          got = got + along_wall(ctx, s.role, r, side, n - got, { rot = s.rot, gap = 1 })
        end
      else
        got = got + scatter(ctx, s.role, r, n, { rot = s.rot })
      end
      total = total + got
    end
  end
  return total
end

-- ---------------------------------------------------------------------------
-- building
-- ---------------------------------------------------------------------------
-- A door in the wall on `side` of rect r. `at` is the offset along that wall;
-- nil picks a random position clear of both corners. Returns x, z.
function door_on(ctx, r, side, at)
  local x, z
  if side == "N" or side == "S" then
    at = at or rng.int(2, math.max(2, r.w - 3))
    x, z = r.x + at, (side == "N") and r.z2 or r.z
  else
    at = at or rng.int(2, math.max(2, r.h - 3))
    x, z = (side == "E") and r.x2 or r.x, r.z + at
  end
  ctx:door(x, z)
  return x, z
end

-- A walled, roofed room with an EXPLICIT floor and its doors. opts.floor is
-- a palette role ("FLOOR", "FLOOR_FINE"...) or a raw TerrainDef name and is
-- REQUIRED: a room built with no named floor is the bare-dirt interior the
-- owner rejected. opts.doors = { {side, at}, ... } or { "S", "E" }.
-- Returns the interior rect.
function shell(ctx, role, r, opts)
  opts = opts or {}
  ctx:room(role, r.x, r.z, r.w, r.h, opts.roofed ~= false)
  ctx:wall_rect(r.x, r.z, r.w, r.h)
  local inr = inner(r)
  local fl = opts.floor
  if fl == nil then
    ctx:refuse("floor", string.format("shell(%s) given no floor - interiors must not sit on bare ground", tostring(role)))
  else
    local d = ctx:role(fl) or fl
    ctx:floor_rect(inr.x, inr.z, inr.w, inr.h, d)
  end
  for _, dd in ipairs(opts.doors or {}) do
    if type(dd) == "table" then door_on(ctx, r, dd[1] or dd.side, dd[2] or dd.at)
    else door_on(ctx, r, dd) end
  end
  return inr
end

-- Lay a terrain patch (a rug, a worn path, a spill) over rect r, clipped to
-- `within` if given. Terrain only - no things, no collision.
function floor_patch(ctx, r, terrain, within)
  local d = ctx:role(terrain) or terrain
  local n = 0
  for z = r.z, r.z2 do
    for x = r.x, r.x2 do
      if within == nil or in_rect(x, z, within) then
        if ctx:floor(x, z, d) then n = n + 1 end
      end
    end
  end
  return n
end

-- Floor r with `terrain`, with a random fraction `p` of cells in `alt` instead:
-- worn plating, patched flagstones, damp tiles. Reads as used, not as new.
function floor_worn(ctx, r, terrain, alt, p)
  local d, a = ctx:role(terrain) or terrain, ctx:role(alt) or alt
  local n = 0
  for z = r.z, r.z2 do
    for x = r.x, r.x2 do
      if ctx:floor(x, z, rng.chance(p or 0.15) and a or d) then n = n + 1 end
    end
  end
  return n
end
