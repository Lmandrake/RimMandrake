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

-- every successful try_place appends {x, z, rot, role} here; scatter() and
-- along_wall() reset it on entry, so a template can read back WHERE its beds
-- landed (a monitor beside each one) without reaching into the Python plan
LAST_PLACED = {}

function try_place(ctx, role, x, z, rot)
  rot = rot or 0
  if not ctx:has_role(role) then return false end
  if not ctx:can_place(role, x, z, rot) then return false end
  local ok = ctx:place_role(role, x, z, rot)
  if ok then LAST_PLACED[#LAST_PLACED + 1] = { x, z, rot, role } end
  return ok
end

-- Roof support for a big interior: vanilla holds a roof within 6 cells of a
-- wall, so a room whose interior exceeds 12 on BOTH axes has a middle no
-- wall reaches (rimplace lint rule 6, Manhattan, over-warns never under-warns).
-- Four columns at 7 in from each corner cover interiors up to about 26x26;
-- anything bigger gets a refusal rather than a silent collapse. Returns the
-- columns placed.
function support_columns(ctx, r)
  if r.w <= 12 or r.h <= 12 then return 0 end
  if not ctx:has_role("PILLAR") then
    ctx:refuse("PILLAR", "interior exceeds 12x12 and this palette has no PILLAR to hold the roof")
    return 0
  end
  if r.w > 26 or r.h > 26 then
    ctx:refuse("PILLAR", string.format("interior %dx%d is beyond four columns' reach; split the room", r.w, r.h))
  end
  local cols = 0
  for _, x in ipairs({ r.x + 7, r.x2 - 7 }) do
    for _, z in ipairs({ r.z + 7, r.z2 - 7 }) do
      if try_near(ctx, "PILLAR", x, z, 0, 1, r) then cols = cols + 1 end
    end
  end
  return cols
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
  LAST_PLACED = {}
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

-- GenAdj.AdjustForRotation's origin shift (rimplace.defsize._ROT_SHIFT), applied
-- only on an axis whose ROTATED size is even. Inverted here so a template can
-- ask "what origin puts this footprint's west/south edge at x0,z0".
ROT_SHIFT = { [0] = { 0, 0 }, [1] = { 0, -1 }, [2] = { -1, -1 }, [3] = { -1, 0 } }

function rotated_dims(ctx, role, rot)
  local w, h = ctx:width_of(role), ctx:height_of(role)
  if rot == 1 or rot == 3 then return h, w end
  return w, h
end

-- the origin cell whose rotated footprint has its south-west cell at (x0,z0)
function origin_for(x0, z0, w, h, rot)
  local s = ROT_SHIFT[rot % 4]
  local x = x0 + floor((w - 1) / 2) - ((w % 2 == 0) and s[1] or 0)
  local z = z0 + floor((h - 1) / 2) - ((h % 2 == 0) and s[2] or 0)
  return x, z
end

-- Up to n of a role hugging one wall of interior rect r, at RANDOM slots with
-- at least opts.gap free cells between two of them - never a fixed stride.
-- The footprint is laid so it actually touches the wall whatever its size or
-- rotation (a 1x2 bedroll on the north wall lands one cell in, head to the
-- wall). opts.face = "room" (default: a shelf's front, a chair) or "wall"
-- (a bed's head); opts.rot overrides both.
function along_wall(ctx, role, r, side, n, opts)
  opts = opts or {}
  LAST_PLACED = {}
  if n <= 0 or not ctx:has_role(role) then return 0 end
  local rot = opts.rot
  if rot == nil then
    rot = (opts.face == "wall") and SIDE_ROT[side] or opposite(SIDE_ROT[side])
  end
  local w, h = rotated_dims(ctx, role, rot)
  local horizontal = (side == "N" or side == "S")
  local len, span = (horizontal and r.w or r.h), (horizontal and w or h)
  if span > len then return 0 end
  local gap = opts.gap or 0
  local slots = {}
  for t = 0, len - span do slots[#slots + 1] = t end
  shuffle(slots)
  local placed, taken = 0, {}
  for _, t in ipairs(slots) do
    if placed >= n then break end
    local far = true
    for _, u in ipairs(taken) do
      if not (t + span + gap <= u or u + span + gap <= t) then far = false break end
    end
    if far then
      local x0, z0
      if side == "N" then x0, z0 = r.x + t, r.z2 - h + 1
      elseif side == "S" then x0, z0 = r.x + t, r.z
      elseif side == "W" then x0, z0 = r.x, r.z + t
      else x0, z0 = r.x2 - w + 1, r.z + t end
      local x, z = origin_for(x0, z0, w, h, rot)
      local clear = true
      for dx = 0, w - 1 do
        for dz = 0, h - 1 do
          if blocks_a_door(ctx, x0 + dx, z0 + dz, r) then clear = false end
        end
      end
      if clear and try_place(ctx, role, x, z, rot) then
        placed = placed + 1
        taken[#taken + 1] = t
      end
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
    local d = DIR[s[3]]
    local here = ctx:role_at(s[1], s[2])
    -- only a WALL takes a lamp, and only from a cell that is not itself a
    -- wall or door (an interior partition can run along r's edge)
    if ctx:role_at(s[1] + d[1], s[2] + d[2]) == "WALL"
       and here ~= "WALL" and here ~= "DOOR"
       and ctx:wall_attach(role, s[1], s[2], s[3]) then
      placed = placed + 1
    end
  end
  return placed
end

-- the south-west cell and rotated dims of a role's footprint placed at (x,z,rot)
function footprint_sw(ctx, role, x, z, rot)
  local w, h = rotated_dims(ctx, role, rot or 0)
  local s = ROT_SHIFT[(rot or 0) % 4]
  local x0 = x + ((w % 2 == 0) and s[1] or 0) - floor((w - 1) / 2)
  local z0 = z + ((h % 2 == 0) and s[2] or 0) - floor((h - 1) / 2)
  return x0, z0, w, h
end

-- Chairs/stools around a TABLE already placed at origin (tx,tz) with rotation
-- trot, on random sides, each facing the table. Returns how many sat down.
function seat_around(ctx, role, tx, tz, n, within, trot)
  if n <= 0 or not ctx:has_role(role) then return 0 end
  local x0, z0, tw, th = footprint_sw(ctx, "TABLE", tx, tz, trot or 0)
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
        -- tuck the WHOLE footprint into the corner: a 3x2 pazaak table's
        -- origin is not the corner cell, its south-west cell is
        local rot = s.rot or 0
        local w, h = rotated_dims(ctx, s.role, rot)
        for _, c in ipairs(corners(r)) do
          if got >= n then break end
          local x0 = (c[1] == r.x) and r.x or (r.x2 - w + 1)
          local z0 = (c[2] == r.z) and r.z or (r.z2 - h + 1)
          local x, z = origin_for(x0, z0, w, h, rot)
          local clear = true
          for dx = 0, w - 1 do
            for dz = 0, h - 1 do
              if blocks_a_door(ctx, x0 + dx, z0 + dz, r) then clear = false end
            end
          end
          if clear and try_place(ctx, s.role, x, z, rot) then got = got + 1 end
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
-- E6 `door-centred`: an exterior door at the EXACT midpoint of a wall >=7
-- long reads as placed by a ruler, not a person (spec §3.1.2). `at` picked
-- explicitly by a caller is left alone (it asked for that cell on purpose);
-- only the RANDOM default nudges off the midpoint, and only when doing so
-- still leaves a legal offset.
local function _off_center(lo, hi, len)
  local at = rng.int(lo, hi)
  if len % 2 == 1 and hi > lo then
    local mid = math.floor(len / 2)
    if at == mid then at = (at + 1 <= hi) and (at + 1) or (at - 1) end
  end
  return at
end

function door_on(ctx, r, side, at)
  local x, z
  if side == "N" or side == "S" then
    at = at or _off_center(2, math.max(2, r.w - 3), r.w)
    x, z = r.x + at, (side == "N") and r.z2 or r.z
  else
    at = at or _off_center(2, math.max(2, r.h - 3), r.h)
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

-- ---------------------------------------------------------------------------
-- E4 (RIMPLACE_ENGINE_DELTAS_1) - reconciled against the vocabulary above.
--
-- `along_wall`/`dress`/`shell`/`scatter` above already do the E4 jobs of
-- wall-hugging placement, secondary/clutter passes and floored shells; rather
-- than ship a second, competing prelude, `hug`/`clutter` below are thin
-- adapters onto that SAME machinery for the spec's own vocabulary (structure_
-- procedural_spec.md §2/§3, and its room recipes in §4 which spell it this
-- way). `aisle_ok` is genuinely new (no flood-fill existed before this pass).
-- `window` and `ruin` are Ctx (Python) methods, not prelude globals - see
-- their docstrings in luaenv.py for why each landed where it did.
-- ---------------------------------------------------------------------------

-- Roles that block a flood-fill (spec §3.5): "beds, tables, shelves, crates
-- are impassable; stools/chairs/lamps are not". Anything not listed here -
-- including an unrecognised role or no role at all - reads as passable,
-- which is the safe default for a check whose job is to warn on the failure
-- mode (a room too dense to walk), not to invent new impassable furniture.
IMPASSABLE_ROLES = {
  WALL = true, BED = true, TABLE = true, STORAGE = true, SHELF_SMALL = true,
  CRATE = true, BARREL = true, DRESSER = true, WORKBENCH = true,
  STOVE = true, GENERATOR = true, BATTERY = true, TURRET = true,
  PILLAR = true, THRONE = true, FORGE = true, REFINERY = true,
  REACTOR = true, FABRICATOR = true, CHARGER = true, HYDRO = true,
  FENCE = true, BARRICADE = true, SANDBAG = true, DRUG_LAB = true,
  DESK = true, ANIMAL_BED = true, WATER_TANK = true, FOUNTAIN = true,
  -- INHABITED_AUGMENTATION_BUILD_1: the solid props the homestead and
  -- mining-site templates place (a chest, a footlocker, lockers, a tool
  -- cabinet, an ore dresser, a mining car, a wreck, rebuilt rock, a seam)
  CHEST = true, FOOTLOCKER = true, LOCKER = true, TOOL_CABINET = true,
  MACHINE = true, RAIL_CAR = true, WRECK = true, WRECK_BIG = true,
  ROCK = true, SEAM = true, SUPPORT = true, GONK = true,
}
-- A structural/boundary role blocks the fill but is not itself a "primary"
-- that needs a passable neighbour (see plan.py's _STRUCTURAL_IMPASSABLE for
-- why - a second room's shared wall falling inside THIS room's rect must not
-- read as an unreached fixture forever).
STRUCTURAL_IMPASSABLE_ROLES = {
  WALL = true, DOOR = true, WINDOW = true, PILLAR = true, FENCE = true,
  BARRICADE = true, SANDBAG = true,
}

-- `ctx:hug(role, room, sides, opts)`. `sides` is one side ("N") or a list
-- ({"N","S"}); `opts.mode` is "hug" (default: wall-hugging via along_wall,
-- picking a random side per placement from the list so two calls do not
-- default to the same wall), "corner" (tucks the whole footprint into a
-- room corner, via `dress`'s corner branch) or "free" (scattered toward the
-- room centre). `opts.n` (default 1) is how many to place.
function hug(ctx, role, room, sides, opts)
  opts = opts or {}
  local mode = opts.mode or "hug"
  local list = sides
  if type(sides) == "string" then list = { sides } end
  local n = opts.n or 1
  if mode == "corner" then
    return dress(ctx, room, { { role = role, n = n, where = "corner", rot = opts.rot } })
  elseif mode == "free" then
    local cx, cz = center(room)
    local half = 2
    local r = R(math.max(room.x, cx - half), math.max(room.z, cz - half),
               math.min(room.w, 2 * half), math.min(room.h, 2 * half))
    return scatter(ctx, role, r, n, { rot = opts.rot or "any" })
  end
  local placed, tries, max_tries = 0, 0, n * (#list + 2)
  while placed < n and tries < max_tries do
    tries = tries + 1
    placed = placed + along_wall(ctx, role, room, list[rng.int(1, #list)], 1, opts)
  end
  return placed
end

-- `ctx:clutter(room, list, n, shell)`. `list` is { {role=, weight=(default 1),
-- where=, rot=}, ... }; `n` total pieces spread across the list by weight.
-- Genuinely distinct from `dress` (which takes a per-entry count, not a
-- shared total): each of the `n` placements is its OWN random-start scan
-- (spec §3.4 - pick a random interior cell, spiral outward via `try_near`
-- until it fits), rather than one scan per role.
--
-- `shell` (optional; the WALLED rect whose inner() is `room`) turns on
-- §3.5's walkability guard: an IMPASSABLE piece is only placed where the
-- door flood-fill still covers >=45% of the floor and still reaches every
-- primary WITH that piece's footprint blocked. INHABITED_AUGMENTATION_BUILD_1
-- found the unguarded version walling a stove and a table behind three
-- crates in a 7x5 abode; the spec's own remedy ("remove the last secondary
-- and retry") is not expressible - the ctx API has no un-place - so the
-- check runs BEFORE the placement instead of after it.
function clutter(ctx, room, list, n, shell)
  n = n or 1
  local total = 0
  for _, s in ipairs(list) do total = total + (s.weight or 1) end
  local placed = 0
  if total <= 0 then return 0 end
  for _ = 1, n do
    local roll, acc, chosen = rng.int(1, total), 0, list[#list]
    for _, s in ipairs(list) do
      acc = acc + (s.weight or 1)
      if roll <= acc then chosen = s break end
    end
    if ctx:has_role(chosen.role) then
      local x, z = rng.int(room.x, room.x2), rng.int(room.z, room.z2)
      local ok
      if shell and IMPASSABLE_ROLES[chosen.role] then
        ok = try_near_walkable(ctx, chosen.role, x, z, chosen.rot or 0, 3, room, shell)
      else
        ok = try_near(ctx, chosen.role, x, z, chosen.rot or 0, 3, room)
      end
      if ok then placed = placed + 1 end
    end
  end
  return placed
end

-- try_near, but an impassable footprint is placed only where `aisle_ok`
-- (with that footprint pre-blocked) still passes for the walled `shell`.
function try_near_walkable(ctx, role, x, z, rot, radius, within, shell)
  if not IMPASSABLE_ROLES[role] then return try_near(ctx, role, x, z, rot, radius, within) end
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
         and ctx:has_role(role) and ctx:can_place(role, c[1], c[2], rot) then
        local x0, z0, w, h = footprint_sw(ctx, role, c[1], c[2], rot)
        local fp = {}
        for dx = 0, w - 1 do for dz = 0, h - 1 do fp[#fp + 1] = { x0 + dx, z0 + dz } end end
        local ok = aisle_ok(ctx, shell, fp)
        if ok and try_place(ctx, role, c[1], c[2], rot) then return true, c[1], c[2] end
      end
    end
  end
  return false
end

-- `ctx:aisle_ok(room)` - spec §3.5's flood-fill proof. Floods from every
-- exterior DOOR cell over passable interior cells of `room`. Returns:
--   ok             true iff coverage >= 45% AND every impassable (primary-
--                  class) thing has >=1 reached neighbour
--   coverage       fraction (0-1) of interior cells the fill reached
--   unreached      count of primaries the fill could not reach
-- A room with no door returns false, 0, 0 rather than erroring - the
-- room-unreachable lint rule already names that failure; this just refuses
-- to claim a walkability result it cannot compute.
-- `blocked` (optional): a list of {x, z} cells to treat as impassable ON TOP
-- of what stands - "would this room still walk if I put a crate HERE".
function aisle_ok(ctx, room, blocked)
  local ir = inner(room)
  local extra = {}
  for _, c in ipairs(blocked or {}) do extra[c[1] .. "," .. c[2]] = true end
  -- FOOTPRINTS, not origins: `role_covering` answers for every cell a thing
  -- occupies (a 3x1 stove blocks three cells, not one)
  local function passable(x, z)
    if extra[x .. "," .. z] then return false end
    local role = ctx:role_covering(x, z)
    return role == nil or not IMPASSABLE_ROLES[role]
  end
  local doors = {}
  for _, side in ipairs({ "N", "E", "S", "W" }) do
    local d = DIR[SIDE_ROT[side]]
    for _, c in ipairs(wall_cells(ir, side)) do
      if ctx:role_at(c[1] + d[1], c[2] + d[2]) == "DOOR" then
        doors[#doors + 1] = c
      end
    end
  end
  if #doors == 0 then return false, 0, 0 end
  local seen, queue, head = {}, {}, 1
  for _, d in ipairs(doors) do
    local k = d[1] .. "," .. d[2]
    if not seen[k] and in_rect(d[1], d[2], ir) and passable(d[1], d[2]) then
      seen[k] = true
      queue[#queue + 1] = d
    end
  end
  local STEP = { { 0, 1 }, { 0, -1 }, { 1, 0 }, { -1, 0 } }
  while head <= #queue do
    local c = queue[head]
    head = head + 1
    for _, s in ipairs(STEP) do
      local nx, nz = c[1] + s[1], c[2] + s[2]
      local k = nx .. "," .. nz
      if in_rect(nx, nz, ir) and not seen[k] and passable(nx, nz) then
        seen[k] = true
        queue[#queue + 1] = { nx, nz }
      end
    end
  end
  -- every impassable THING (counted once, by origin) needs one footprint
  -- cell with a reached neighbour; the hypothetical `blocked` piece is held
  -- to the same rule, so a guard never places a crate nobody can reach
  local total, reached, unreached = 0, 0, 0
  local things, thing_ok = {}, {}
  local function touch(key, x, z)
    if things[key] == nil then things[key] = true; thing_ok[key] = false end
    if thing_ok[key] then return end
    for _, s in ipairs(STEP) do
      if seen[(x + s[1]) .. "," .. (z + s[2])] then thing_ok[key] = true return end
    end
  end
  for x = ir.x, ir.x2 do
    for z = ir.z, ir.z2 do
      total = total + 1
      local k = x .. "," .. z
      if seen[k] then reached = reached + 1 end
      if extra[k] then
        touch("blocked", x, z)
      else
        local role, ox, oz = ctx:role_covering(x, z)
        if role and IMPASSABLE_ROLES[role] and not STRUCTURAL_IMPASSABLE_ROLES[role] then
          touch(ox .. "," .. oz, x, z)
        end
      end
    end
  end
  for key, _ in pairs(things) do
    if not thing_ok[key] then unreached = unreached + 1 end
  end
  local coverage = (total > 0) and (reached / total) or 0
  return (coverage >= 0.45 and unreached == 0), coverage, unreached
end
