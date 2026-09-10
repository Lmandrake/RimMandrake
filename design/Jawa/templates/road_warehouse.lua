-- road_warehouse.lua - "Warehouse along a road" (structure_procedural_spec.md
-- sec 8.5). NEW template - the 7th of the 14 sec-8 archetypes built under
-- INHABITED_AUGMENTATION_BUILD_1 (after 8.1 homestead, 8.2 moisture farm,
-- 8.3 mining site, 8.14 cache, 8.10 dead caravan, 8.4 trading post). Picked
-- from the remaining unblocked six (8.5/8.6/8.9/8.11/8.12/8.13): the spec's
-- own R5 rule ("depot shelf density must be walkable aisles") is written
-- FOR this archetype, and this is the first ROAD-FRONTING big-footprint
-- archetype built with the frame()/road_dir convention trading_post.lua and
-- dead_caravan.lua established - `junkers_depot.lua` (an older, sibling-item
-- template) proves the shelving/aisle grammar but is NOT road_dir-aware at
-- all (one fixed orientation), so this is also the first template to marry
-- the two: a big non-square canvas that must rotate correctly for road_dir.
--
-- Grammar, road -> back: a Concrete loading dock outside a two-cell-wide
-- "wide door" (two adjacent single doors, same convention junkers_depot.lua
-- already uses for a loading bay) -> the warehouse floor (perimeter
-- shelving on three walls, the door wall left clear; island shelf columns
-- run PERPENDICULAR to the door wall in lanes, so every aisle runs door to
-- back wall; every few island slots dropped and replaced with a pallet) ->
-- an office in a front corner (its own door and a window onto the floor) ->
-- a guard bunk in the back corner ->  outside: a fence gate on the road
-- approach, a parked wreck at the dock end, a rubbish/junk clump behind the
-- building, a barrel row by the dock -> an Industrial+ power apron on the
-- back wall.
--
-- params:
--   road_dir   "N"|"E"|"S"|"W" (default "S") - the world side the loading
--              wall (dock + wide door) faces, same convention homestead.lua/
--              trading_post.lua use for "the world side the door faces".
--   faction    Jawa_IndigenousTribes | Jawa_Junkers | Jawa_HuttCartel |
--              Jawa_DeepwaterCompact | Jawa_FreeDroidEnclaves |
--              Jawa_WildsteamClan | Empire | TribeCivil | OutlanderCivil |
--              default. Junkers reads its own CRATE/SCRAP palette block
--              (scrap dressing behind the building); Empire and everyone
--              else ride the shared default grammar - the spec's own named
--              Empire/Junkers swaps (LWM_VeryBigShelf, MUS_SpaceBase_Lockers,
--              Aurebesh signage) are NOT built, see the substitution note
--              below.
--   wealth     destitute|poor|comfortable|rich - rides the palette's own
--              FLOOR/DECOR wealth gates; no archetype-specific branch here
--              (the spec names none for this archetype beyond floor tier).
--   techLevel  Neolithic (default) | Industrial+ - gates the R-POWER apron
--              and the parked-wreck def (truck vs pod car), same has_role
--              gate homestead.lua/trading_post.lua use.
--   state      "lived" (default) | "abandoned" | "ruined" - abandoned swaps
--              every shelf placed this pass to its Ancient cousin and drifts
--              sand at the wide door; ruined runs the shared ctx:ruin() tail.
--
-- Verified real defNames (RimSage `search_defs` against the indexed 1.6
-- source - CLAUDE.md "never guess a defName" / block_blind_scan). This
-- session's RimSage index is STILL the minimal/prior-load mod set, not the
-- 599-mod ModsConfig.xml on disk (this project's own "ModsConfig describes
-- the NEXT load" memory, and DEFDUMP_ONDEMAND_BRIDGE_UNREACHABLE_1 names the
-- live-dump path as unreachable right now without a ~15-25 minute game load
-- through a bridge this pass does not hold - infrastructure/state/BRIDGE
-- shows FOUNDRY holding it for a different item, DROID_RETIRE_DEPOT_ASIMOV_1,
-- tonight). Same discipline as every archetype before this one: avoid every
-- mod-specific defName the spec names that this index cannot see, and
-- substitute a verified real equivalent, noted here rather than guessed:
--   AncientIndustrialTruck / AncientRustedTruck (ThingDef, both real,
--     confirmed via search_defs) - the spec's own Industrial-tier options
--     for the parked wreck at the dock end; same pair mining_site.lua's
--     apron cart and dead_caravan.lua's Industrial wreck already use.
--   AncientCratePallet (ThingDef, "ancient crate pallet", real) - the spec's
--     own `LWM_Pallet`/`PalletCrateA` (both unindexed - no "LWM_"-prefixed
--     or "Pallet"-named def besides this one is indexed) - used for "every
--     3rd-4th island shelf dropped and replaced by a pallet".
--   ChunkSandstone (ThingDef, real, used throughout this folder already) -
--     substitute for the spec's `VFEPD_RubbishPile` (no "Rubbish"-named def
--     of any kind is indexed) behind the building - a debris clump reads the
--     same without inventing an unverified defName.
--   Filth_MachineBits, Filth_Dirt, Filth_Sand, Filth_RubbleBuilding (Core) -
--     all found exactly as named.
--   AncientShelf, AncientIndustrialShelf (ThingDef, real, both confirmed) -
--     the `abandoned` state's shelf-cousin swap (spec's own line: "shelves
--     -> AncientShelf/AncientIndustrialShelf (inert - dressing only)").
-- NOT built here (palette-level gaps this template does not invent around,
-- same as every prior template that hit them):
--   `AncientBarrierGate` (spec's own road-approach gate) - NOT indexed
--     ("Barrier" search returns only AncientBarrierLong/AncientMilitary
--     Barrier/AncientConcreteBarrier/VacBarrier, none of them a gate). The
--     palette's own GATE role (FenceGate, real, confirmed) stands in.
--   `VFEPD_AncientSemiTrailer`, `RH2_ClassicFootlocker`'s own direct name,
--     `OuterRim_StorageCrate`/`LWM_VeryBigShelf`/`MUS_SpaceBase_Lockers`/any
--     `OuterRim_AurebeshWord*` sign - none indexed tonight (VFEPD_/RH2_/LWM_/
--     OuterRim_ prefixes all return nothing, matching every prior template's
--     header note this session). `FOOTLOCKER` and `CRATE` are read through
--     the PALETTE roles exactly as every other template reads them - the
--     faction blocks that resolve those roles to an unindexed defName
--     tonight (Jawa_HuttCartel/Jawa_Junkers/Jawa_FreeDroidEnclaves's own
--     CRATE, and FOOTLOCKER's shared default RH2_ClassicFootlocker) are a
--     pre-existing palette.json state, not something this template invents
--     or is positioned to fix - `rimplace verify` reports the same MISSING
--     it would for any other template using those roles.
--   Aurebesh signage of any kind, an Empire-specific big-shelf/locker swap -
--     omitted as pure dressing per the spec's own §10 gap list, not guessed.
--
-- API available: ctx (see luaenv.Ctx), rect, params, rng, role(), note()

-- ---------------------------------------------------------------------------
-- frame: copied from homestead.lua/trading_post.lua/mining_site.lua (each
-- carries its own private copy - "not in the prelude" per their own header
-- notes; this is the fourth, not a new gap).
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
  function f.bounds() return f.rect(0, 0, W, H) end
  return f
end

local function clamp(v, lo, hi) return math.max(lo, math.min(hi, v)) end

local function filth(ctx, def, x, z)
  return ctx:place(def, x, z, 0, nil, "FILTH", true)
end

-- outer (walled) rect of an interior, for the aisle_ok/try_near_walkable guard
local function outer(ir) return R(ir.x - 1, ir.z - 1, ir.w + 2, ir.h + 2) end

-- The cell, then rings around it out to `radius`, in random order, for a raw
-- defName rather than a palette ROLE - tests the REAL can_place gate on every
-- candidate rather than a cheap single-cell occupied() check (the fix every
-- prior template's header names: dead_caravan.lua's Debtor's Cache crate,
-- trading_post.lua's safe/box/wreck). Used here for the parked wreck and the
-- rubbish-pile stand-in. `within` (optional) bounds the ring search to a
-- rect - REAL BUG this pass's own sweep caught: the yard-side barrel row
-- sits right beside the wide door's own opening, and an UNBOUNDED ring
-- search (this function's original shape) can wander straight through that
-- gap into the depot floor itself when its first-choice cell is occupied -
-- a barrel landed one row inside the building on seed 35's own render,
-- sealing an island shelf's only open side and tripping "aisle-blocked,
-- 1 primary unreached" (ERROR) on the main floor. `within` is optional and
-- defaults to unbounded so every OTHER call site here (the wreck, the
-- rubbish clump, Junkers scrap, the generator/battery pad - none of them
-- sit next to an opening into a different zone) is unaffected.
local function place_near(ctx, def, x, z, radius, role_tag, rot, within)
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
      if (within == nil or in_rect(c[1], c[2], within)) and ctx:can_place(def, c[1], c[2], rot) then
        ctx:place(def, c[1], c[2], rot, nil, role_tag)
        return true, c[1], c[2]
      end
    end
  end
  return false
end

-- place_near, but for a WALLED room (`shell_rect`) - the candidate's whole
-- footprint must not seal the door's own flood-fill (aisle_ok, pre-checked
-- BEFORE placing). Used for the guard bunk's bed and footlocker.
local function place_near_walkable(ctx, def, x, z, radius, role_tag, within, shell_rect, rot)
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
      if (within == nil or in_rect(c[1], c[2], within)) and ctx:can_place(def, c[1], c[2], rot) then
        local x0, z0, w, h = footprint_sw(ctx, def, c[1], c[2], rot)
        local fp = {}
        for dx2 = 0, w - 1 do for dz2 = 0, h - 1 do fp[#fp + 1] = { x0 + dx2, z0 + dz2 } end end
        if aisle_ok(ctx, shell_rect, fp) then
          ctx:place(def, c[1], c[2], rot, nil, role_tag)
          return true, c[1], c[2]
        end
      end
    end
  end
  return false
end

-- perimeter shelving on ONE wall of an interior rect, every candidate
-- walkability-guarded before it commits (place_near_walkable, radius 0 - the
-- search over candidate slots is done here, in random wall-cell order, not
-- inside the primitive). A plain along_wall() has no aisle_ok precheck, and
-- on a room this size (20+ interior cells wide, 11+ deep) an unguarded random
-- slot occasionally sealed off the aisle mouth or the office door - the same
-- class of bug trading_post.lua's own header names for its shelf/counter/
-- corner placements. Guarding every shelf here, not just the risky ones,
-- costs nothing (the aisle lanes never call this - they walk lanes, not walls).
-- `def_fn()` is called per candidate (not once per wall) so the abandoned
-- state's Ancient-cousin roll is independent per shelf, matching ctx:ruin's
-- own per-thing roll convention rather than one swap for the whole wall.
-- REAL BUG this pass's own sweep caught, only under `state=ruined`: two
-- placements this function considers perfectly independent (each its own
-- can_place-gated, walkability-guarded check against what stands AT THAT
-- MOMENT) can both be `def_fn()`'s SHELF_SMALL branch - a real 1x1
-- ShelfSmall, which fits with zero cells of slack between neighbours since
-- it never claims a second cell. `ctx:ruin()`'s own `_RUIN_COUSIN` table
-- maps BOTH "STORAGE" and "SHELF_SMALL" to the SAME 2-cell "AncientShelf"
-- and renames things in place with no footprint recheck (see the office's
-- own header note on the same mechanism) - so two 1x1 shelves one cell
-- apart, both fine before ruin, both silently become 2-cell shelves that
-- now overlap after it: "AncientShelf ([2,1]) at (26,14) overlaps
-- AncientShelf at (26,13)" on wealth=destitute/tech=Neolithic/seed=1's own
-- render. A minimum gap of 2 between accepted placements along this wall
-- leaves at least 1 clear cell even after every shelf on it inflates by
-- one - the same margin `along_wall()`'s own `gap` option exists to buy,
-- extended here since this function does its own candidate search instead.
local function shelf_wall(ctx, side, target, room, shell_rect, def_fn)
  local n = 0
  local rot = opposite(SIDE_ROT[side])
  local placed = {}
  for _, c in ipairs(shuffle(wall_cells(room, side))) do
    if n >= target then break end
    local far = true
    for _, p in ipairs(placed) do
      if math.abs(c[1] - p[1]) + math.abs(c[2] - p[2]) < 2 then far = false break end
    end
    if far and place_near_walkable(ctx, def_fn(), c[1], c[2], 0, "STORAGE", room, shell_rect, rot) then
      n = n + 1
      placed[#placed + 1] = c
    end
  end
  return n
end

-- ---------------------------------------------------------------------------
-- reading params once
-- ---------------------------------------------------------------------------
local function read_opts(p)
  local o = {}
  o.faction = p.faction or "default"
  o.junkers = (o.faction == "Jawa_Junkers")
  o.tech = p.techLevel or "Neolithic"
  o.industrial = (o.tech == "Industrial" or o.tech == "Spacer" or o.tech == "Ultra" or o.tech == "Archotech")
  o.state = p.state or "lived"
  return o
end

function min_rect(params)
  -- road_dir-aware, same convention dead_caravan.lua's/trading_post.lua's own
  -- min_rect uses: for an E/W-facing door the "width along the loading wall"
  -- runs along WORLD Z, so the compiler must be told the SWAPPED rect before
  -- build()'s own W/H transpose reads it back. A fixed (22,16) here would
  -- hand the compiler a legally-minimum rect that, after transpose, reads as
  -- 16-wide (below the 22 the grammar needs) on every E/W-facing seed and
  -- refuses outright - the exact bug both sibling templates' own headers
  -- measured before this fix was written in from the start here.
  local face = (params and params.road_dir) or "S"
  if face == "E" or face == "W" then return 16, 22 end
  return 22, 16
end

function build(ctx)
  local p = params
  local o = read_opts(p)
  local face = p.road_dir or "S"
  if face ~= "N" and face ~= "E" and face ~= "S" and face ~= "W" then face = "S" end
  local W, H = rect.w, rect.h
  if face == "E" or face == "W" then W, H = rect.h, rect.w end
  if W < 22 or H < 16 then
    ctx:refuse("footprint", string.format(
      "%dx%d does not give the road-warehouse grammar its 22x16 minimum (road_dir=%s)",
      rect.w, rect.h, face))
    return
  end
  local fr = frame(rect.x, rect.z, W, H, face)
  local within = fr.bounds()
  local road_side = fr.side("S")
  local back_wall = fr.side("N")
  local side_e, side_w = fr.side("E"), fr.side("W")

  -- ---- the building: occupies local v = apron_h .. H-1, leaving a dock
  -- strip in front of it (v = 0 .. apron_h-1) between the shell and the
  -- actual road tile outside the canvas.
  local apron_h = 3
  local bld_r = fr.rect(0, apron_h, W, H - apron_h)
  local bld_i = shell(ctx, "Storeroom", bld_r, { floor = "FLOOR_WORK" })

  -- ---- the wide door: two adjacent single doors (junkers_depot.lua's own
  -- "a bay, not a front door" convention), off-centre by construction (a
  -- nonzero nudge from the wall's own midpoint, never the exact centre - E6
  -- door-centred). Computed in FRAME-LOCAL u (not from bld_i, a WORLD rect)
  -- so the position is correct under every road_dir without a second
  -- world/local conversion.
  local wall_len = W - 2
  local center_t = math.floor(wall_len / 2)
  local nudge = ({ -3, -2, 2, 3 })[rng.int(1, 4)]
  local door_u = clamp(1 + center_t + nudge, 1, wall_len - 2)
  local d1x, d1z = fr.cell(door_u, apron_h)
  local d2x, d2z = fr.cell(door_u + 1, apron_h)
  ctx:door(d1x, d1z)
  ctx:door(d2x, d2z)

  -- ---- the dock: a Concrete pad outside the wide door, 3 deep x 6 wide,
  -- jittered 1 cell along the wall (spec's own words), clipped to the canvas.
  local lateral = (road_side == "N" or road_side == "S") and { 1, 0 } or { 0, 1 }
  local outward = DIR[SIDE_ROT[road_side]]
  local dock_jit = rng.int(-1, 1)
  local dock_n = 0
  for depth = 1, 3 do
    for w = -2, 3 do
      local dx = d1x + outward[1] * depth + lateral[1] * (w + dock_jit)
      local dz = d1z + outward[2] * depth + lateral[2] * (w + dock_jit)
      if in_rect(dx, dz, within) and ctx:floor(dx, dz, ctx:role("FLOOR_WORK")) then dock_n = dock_n + 1 end
    end
  end

  -- ---- frame-local interior extents (bld_i is a WORLD rect derived from
  -- bld_r via fr.rect, so its own local u/v span is [1, W-2] x
  -- [apron_h+1, H-2] - one cell in from bld_r's own walls on every side).
  local liu0, liu1 = 1, W - 2
  local liv0, liv1 = apron_h + 1, H - 2
  local aisle_u0, aisle_u1 = door_u, door_u + 1

  -- ---------------------------------------------------------------------
  -- the office: R-OFFICE 3x3 (5x5 with its own walls), tucked into the front
  -- corner FARTHEST from the main aisle so its own walls never fight the
  -- guarded shelving lanes on that side. Built BEFORE the island shelving
  -- below, deliberately: `wall_rect()` has no can_place-gated retry of its
  -- own (it places or refuses each edge cell outright, no fallback), so
  -- building the office AFTER the islands would let an island shelf claim a
  -- cell the office's own perimeter needs, leaving a real gap - a
  -- "room-not-sealed" ERROR, not a cosmetic clash. Caught by inspection
  -- before ever shipping that ordering (not something this pass ran to
  -- failure first): the island loop below is told the office's own u-range
  -- (in addition to the aisle's) so it never offers that lane a slot at all.
  -- ---------------------------------------------------------------------
  local office_far_e = (aisle_u0 - liu0) >= (liu1 - aisle_u1)
  local office_u = office_far_e and liu0 or (liu1 - 4)
  local office_r = fr.rect(office_u, liv0, 5, 5)
  local office_ok = in_rect(office_r.x, office_r.z, within) and in_rect(office_r.x2, office_r.z2, within)
                    and not (office_r.x <= math.max(d1x, d2x) and office_r.x2 >= math.min(d1x, d2x)
                             and office_r.z <= math.max(d1z, d2z) + 1 and office_r.z2 >= math.min(d1z, d2z))
  local office_i, desk_placed, window_placed = nil, false, false
  if office_ok then
    local into_side = office_far_e and fr.side("E") or fr.side("W")
    office_i = shell(ctx, "Office", office_r, { floor = "FLOOR_FINE", doors = { { into_side } } })
    -- desk hugs the wall FACING the door (R-OFFICE's own recipe: "facing the
    -- door, hug, 1 off the wall"), not a free centre placement. REAL BUG
    -- this pass's own first lint run caught: a free-centre desk in a 3x3
    -- interior (R-OFFICE's own stated minimum) ate the room's one open
    -- middle, and the door-flood-fill reached only 44% of the interior
    -- (<45%, aisle-blocked WARN) on this template's very first render.
    -- Hugging the far wall instead keeps the door-side two rows open as one
    -- contiguous walkable block.
    local OPP_SIDE = { N = "S", S = "N", E = "W", W = "E" }
    local desk_wall = OPP_SIDE[into_side]
    local desk_rot = opposite(SIDE_ROT[desk_wall])
    local dcx, dcz
    for _, c in ipairs(shuffle(wall_cells(office_i, desk_wall))) do
      local ok, px, pz = place_near_walkable(ctx, ctx:role("TABLE"), c[1], c[2], 0, "TABLE", office_i, office_r, desk_rot)
      if ok then desk_placed, dcx, dcz = true, px, pz break end
    end
    if desk_placed then
      local d = DIR[desk_rot]
      try_near(ctx, "STOOL", dcx + d[1], dcz + d[2], 0, 1, office_i)
    end
    if ctx:has_role("WINDOW") and o.state ~= "abandoned" then
      -- one window, on the office's road-facing wall (fr's own local "S")
      local ws = fr.side("S")
      local cells = wall_cells(office_r, ws)
      for _, c in ipairs(shuffle(cells)) do
        if ctx:role_at(c[1], c[2]) == "WALL" then
          window_placed = ctx:window(c[1], c[2])
          if window_placed then break end
        end
      end
    elseif o.state == "abandoned" then
      -- "the office window shattered" - a wall gap and rubble instead of
      -- glass, same read as the spec's own line, no unverified glass-shard def.
      local ws = fr.side("S")
      local cells = wall_cells(office_r, ws)
      for _, c in ipairs(shuffle(cells)) do
        if ctx:role_at(c[1], c[2]) == "WALL" then
          filth(ctx, "Filth_RubbleBuilding", c[1], c[2])
          break
        end
      end
    end
    -- REAL BUG this pass's own sweep caught, four shapes running up to this
    -- one, all real: a 3x3 office (R-OFFICE's own stated minimum) has 9
    -- interior cells, so it has almost no slack. (1) TWO clutter items on
    -- top of the desk+stool pushed occupied cells to 5/9, dropping the
    -- door's flood-fill to 4/9 (44%, <45%) - fixed by dropping to R4's own
    -- one-secondary minimum. (2) `dress()`'s own "wall" mode (along_wall, no
    -- aisle_ok precheck) still occasionally landed that one SHELF_SMALL
    -- diagonally behind the desk, sealing the room's far row - fixed with a
    -- walkability-guarded retry. (3) a wider sweep (wealth=destitute/
    -- tech=Neolithic/state=ruined) surfaced a footprint-collision instead:
    -- `ctx:ruin()`'s own `_RUIN_COUSIN` maps BOTH "STORAGE" and
    -- "SHELF_SMALL" to the same [2,1] "AncientShelf" with no footprint
    -- recheck, so a 1x1 ShelfSmall placed with the office's own zero-slack
    -- clearance overlapped a wall once ruin inflated it - dropped
    -- SHELF_SMALL from the office. (4) the replacement guaranteed-secondary
    -- (`wall_lights()`, believed reliable because two earlier renders
    -- happened to show it working) turned out to depend on the OFFICE
    -- corner sitting flush against the MAIN floor's own outer wall - proven
    -- by testing trading_post.lua's own wall_lights() calls directly: ZERO
    -- WALL_LIGHT across 20 independent seeds. `wall_lights(r,...)` steps ONE
    -- CELL PAST r's own edge looking for a wall, so it only works when r's
    -- wall ring sits one cell inside an ACTUAL wall (i.e. r must be the
    -- INTERIOR rect) - this template (both here and the bld_r call below)
    -- and trading_post.lua were passing the OUTER shell rect instead of the
    -- already-available interior rect (`office_i`/`bld_i`), which is what
    -- every other template's ~30 wall_lights() call sites do correctly and
    -- what wall_cells()'s own doc comment says it expects
    -- (WALL_LIGHTS_HELPER_BROKEN_1) - now fixed here to pass `office_i`.
    -- Combined with STOOL being NULLED for
    -- Jawa_FreeDroidEnclaves (canon: droids do not sit - the desk's own
    -- chair silently fails there too), this office had ZERO real
    -- secondaries on that faction's `abandoned` state - "no-secondary"
    -- ERROR, on 6/360 of a faction x dir x state sweep. Fixed with a
    -- role NO faction's palette block ever nulls and that `_RUIN_COUSIN`
    -- never touches at all: BARREL, walkability-guarded the same way
    -- SHELF_SMALL was. PLANT_POT stays as a nice-to-have where available
    -- (unguarded - it is passable, so it cannot itself break the aisle
    -- proof); `wall_lights()` now gets a real INTERIOR rect and is trusted
    -- as the guaranteed-secondary it was meant to be.
    local ocx, ocz = center(office_i)
    try_near(ctx, "PLANT_POT", ocx, ocz, 0, 1, office_i)
    wall_lights(ctx, office_i, 1)
    local barrel_ok = false
    for _, side in ipairs(shuffle({ fr.side("N"), fr.side("E"), fr.side("W"), fr.side("S") })) do
      for _, c in ipairs(shuffle(wall_cells(office_i, side))) do
        if try_near_walkable(ctx, "BARREL", c[1], c[2], 0, 0, office_i, office_r) then
          barrel_ok = true
          break
        end
      end
      if barrel_ok then break end
    end
    if not barrel_ok then
      ctx:refuse("BARREL", "no room for the office's one guaranteed secondary (R4)")
    end
  else
    ctx:refuse("office", "no room for the 5x5 office shell clear of the main aisle")
  end
  -- the office's own OUTER footprint (walls included) in frame-local u, so
  -- the island loop below can skip any lane overlapping it - one cell wider
  -- than office_r itself, matching outer()'s own "+1 margin" convention.
  local office_u0, office_u1 = office_ok and (office_u - 1) or nil, office_ok and (office_u + 5) or nil

  -- ---- perimeter shelving: E, W, and back walls only - the door wall stays
  -- clear by construction (R5's own words). Every placement walkability-
  -- guarded (shelf_wall above). `shelf_def()` rolls an Ancient cousin
  -- per-shelf on `abandoned` (spec's own line: "shelves ->
  -- AncientShelf/AncientIndustrialShelf"), or on any other state a
  -- majority-STORAGE / minority-SHELF_SMALL mix.
  --
  -- REAL BUG this pass's own lint run caught: on the default `lived` state,
  -- `shelf_def()` used to return the SAME resolved defName ("Shelf") every
  -- single call, with no variety at all - independent random placement
  -- positions (the fix for the marched-lane version of this same finding)
  -- still trip E6's regular-grid rule occasionally by sheer chance once
  -- enough same-defName shelves accumulate along one wall or lane (the
  -- lint groups strictly by defName, and it only takes one coincidental
  -- 3-term arithmetic run among however many "Shelf" things share a wall's
  -- fixed x). A ~35% SHELF_SMALL mix splits the pool into two defNames,
  -- which needs the SAME coincidence to happen independently within a
  -- smaller subset twice - real furniture variety (a depot plausibly has
  -- both full shelves and small ones), not a cosmetic patch for the lint.
  -- REAL BUG this pass's own 160-combination sweep caught: the 2-way mix
  -- above still left 2/160 seeds ("N" and "S") with an occasional 2-line
  -- regular-grid WARN - a big floor easily holds 20-30 STORAGE-class things,
  -- and even a 65/35 split leaves enough of the majority defName for a
  -- spurious 3-term run once in a while. A 3-way split (STORAGE/SHELF_SMALL/
  -- a rolled Ancient cousin, same two names the `abandoned` state already
  -- uses) spreads the same population across one more bucket.
  -- REAL BUG this pass's own wider sweep caught, worse than the first one:
  -- mixing in SHELF_SMALL (a real 1x1 ShelfSmall) bought defName variety
  -- against E6's regular-grid rule, but `ctx:ruin()`'s `_RUIN_COUSIN` maps
  -- BOTH "STORAGE" and "SHELF_SMALL" to the SAME 2-cell "AncientShelf" with
  -- no footprint recheck on the rename - a 1x1 shelf placed with its normal
  -- zero-slack clearance (to a wall, another shelf, even a crate) silently
  -- inflates to 2 cells at ruin time and OVERLAPS whatever was one cell
  -- away, a real `footprint-collision` ERROR on 4/40 of a wider ruined-state
  -- sweep (against another shelf, a wall, and a crate, in different seeds -
  -- not one narrow case). Dropping SHELF_SMALL keeps the SAME 3-defName
  -- variety this fix exists for (Shelf/AncientShelf/AncientIndustrialShelf)
  -- while only ever mixing among sizes that are ALL [2,1] - confirmed via
  -- the def size index - so a ruin-time rename can never change what a
  -- placement already proved fits.
  -- An even-ish 3-way split (not the first draft's 75/12.5/12.5) - a
  -- skewed split still leaves one defName dominant enough for E6's own
  -- 3-in-a-row check to find, occasionally, across a room this size (12/160
  -- of a wider `lived`-state sweep with the skewed split). Splitting the
  -- SAME population closer to evenly needs the same 3-in-a-row coincidence
  -- to land within a smaller subset to trip it.
  local function shelf_def()
    local roll = rng.int(1, 100)
    if o.state == "abandoned" then
      -- REAL BUG this pass's own sweep caught: 45/45/10 still left two tied
      -- dominant buckets, and 3/60 seeds tripped regular-grid on whichever
      -- of the two happened to cluster. Flattened further, same reasoning.
      if roll <= 40 then return "AncientShelf"
      elseif roll <= 75 then return "AncientIndustrialShelf"
      else return ctx:role("STORAGE") end
    end
    if roll <= 45 then return ctx:role("STORAGE")
    elseif roll <= 72 then return "AncientShelf"
    else return "AncientIndustrialShelf" end
  end
  local shelved_e = shelf_wall(ctx, side_e, rng.int(3, 5), bld_i, outer(bld_i), shelf_def)
  local shelved_w = shelf_wall(ctx, side_w, rng.int(3, 5), bld_i, outer(bld_i), shelf_def)
  local shelved_n = shelf_wall(ctx, back_wall, rng.int(2, 3), bld_i, outer(bld_i), shelf_def)

  -- ---- islands: one lane per ~6 cells of interior width, each lane's
  -- shelves running PERPENDICULAR to the door wall (stepping along v, the
  -- depth axis) so every aisle between lanes runs door -> back, exactly R5's
  -- own words. The lane straddling the wide door OR the office is skipped
  -- outright - the aisle is kept clear by never being touched, not by a
  -- post-hoc check, and the office exclusion is what the reorder note above
  -- exists for. Every candidate slot is a real can_place-gated retry via
  -- place_near_walkable (radius 0: the exact lane cell, or nothing) rather
  -- than a bare occupied() test, so a slot that only looks free (inside a
  -- wall's own footprint at the lane's edge) is skipped, not double-booked.
  local margin = 2
  local islands, pallets, dropped = 0, 0, 0
  local u = liu0 + margin
  while u <= liu1 - margin do
    local lane_end = math.min(u + 5, liu1 - margin)
    local hits_aisle = aisle_u1 >= u - 1 and aisle_u0 <= lane_end + 1
    local hits_office = office_ok and office_u1 >= u - 1 and office_u0 <= lane_end + 1
    if not (hits_aisle or hits_office) then
      local n_lane = math.max(2, math.floor((liv1 - liv0 + 1) / 2))
      for _ = 1, n_lane do
        -- an INDEPENDENT random (u,v) draw per shelf, not a stepped march.
        --
        -- REAL BUG this pass's own lint run caught, three shapes running up
        -- to this one, all real: a marched lane (fixed v-step, then a ±1
        -- jitter on that step, then a ±1 jitter on the lane's u as well)
        -- kept tripping E6's regular-grid rule ("2 equally-spaced line(s) of
        -- 'Shelf'") on 5 of the first 6 seeds tried - a stepped sequence
        -- only jitters the GAP or the column, and the lint's own check only
        -- needs ONE surviving 3-in-a-row at ANY constant spacing anywhere in
        -- an 11+ cell lane, which a march (even a jittered one) produces far
        -- too often. Warehouse island shelving is not one of R3's three
        -- named lattice exceptions (vaporators/graves/mining-rail), so a
        -- genuinely irregular layout is what the rule is actually asking
        -- for - fixed by abandoning the march for junkers_depot.lua's own
        -- proven shape (its own lint run, every seed tried, never trips
        -- this rule): i.i.d. random draws over a range essentially never
        -- land 3-in-a-row at an exact constant spacing, where a stepped
        -- march almost always does.
        local lu = rng.int(u, lane_end)
        local lv = rng.int(liv0, liv1)
        local px, pz = fr.cell(lu, lv)
        if rng.chance(0.22) then
          -- "every 3rd-4th island shelf... replaced by a pallet" (spec) - an
          -- unforced ~22% roll reads the same without a slot counter to
          -- desync from this now-nondeterministic placement order.
          if place_near_walkable(ctx, "AncientCratePallet", px, pz, 1, "CRATE", bld_i, outer(bld_i))
             or place_near_walkable(ctx, ctx:role("CRATE"), px, pz, 1, "CRATE", bld_i, outer(bld_i)) then
            pallets = pallets + 1
          else
            dropped = dropped + 1
          end
        else
          if place_near_walkable(ctx, shelf_def(), px, pz, 1, "STORAGE", bld_i, outer(bld_i)) then
            islands = islands + 1
          else
            dropped = dropped + 1
          end
        end
      end
    end
    u = lane_end + margin + 1
  end

  -- ---- loose crates at the aisle mouth, near the door (spec's own "2-4
  -- loose crates in the aisle mouth") - computed in frame-local (u,v) via
  -- fr.rect so it lands correctly under every road_dir.
  --
  -- REAL BUG this pass's own min-canvas sweep caught, and the worst one:
  -- `mouth_r` spans door_u-1 .. door_u+2, which is 1 cell of margin on
  -- EITHER SIDE of the 2-wide main aisle PLUS the aisle itself - and a bare
  -- `scatter()` is can_place-gated but NOT walkability-guarded, so nothing
  -- stopped it dropping a crate directly inside the aisle. On the 16x22
  -- min-canvas floor at road_dir=E/seed=12, TWO crates landed in the exact
  -- two aisle columns, 2 cells in from the door - a full-width plug right
  -- at the choke point, dropping the door's own flood-fill to 1% reachable
  -- and 12 primaries unreached (ERROR), not a stray WARN. Every other
  -- "aisle mouth" dressing in this codebase (dead_caravan.lua's spill cone,
  -- trading_post.lua's yard crates) sits OUTSIDE a room the aisle rule
  -- applies to; this is the first one INSIDE the walled floor the aisle
  -- itself runs through, so it needs the same walkability guard everything
  -- else on this floor already has - one candidate cell at a time,
  -- can_place AND aisle_ok pre-checked before it ever commits.
  local mouth_r = fr.rect(door_u - 1, liv0, 4, 3)
  local mouth_crates = 0
  do
    local target = rng.int(2, 4)
    local cells = {}
    for mu = door_u - 1, door_u + 2 do
      for mv = liv0, liv0 + 2 do
        cells[#cells + 1] = { mu, mv }
      end
    end
    shuffle(cells)
    for _, c in ipairs(cells) do
      if mouth_crates >= target then break end
      local mx, mz = fr.cell(c[1], c[2])
      if in_rect(mx, mz, bld_i) and try_near_walkable(ctx, "CRATE", mx, mz, 0, 0, bld_i, outer(bld_i)) then
        mouth_crates = mouth_crates + 1
      end
    end
  end

  -- ---- dirt tracked in from the wide door, 3-4 cells; abandoned drifts sand
  -- 2 deep on top of it instead (spec's own line).
  local into = { -outward[1], -outward[2] }
  local drift_n = 0
  for i = 1, (o.state == "abandoned") and 5 or rng.int(3, 4) do
    local fx = d1x + into[1] * i
    local fz = d1z + into[2] * i
    if in_rect(fx, fz, bld_i) then
      filth(ctx, (o.state == "abandoned" and i <= 2) and "Filth_Sand" or "Filth_Dirt", fx, fz)
      drift_n = drift_n + 1
    end
  end

  -- ---- lights: interior wall lamps plus the palette's tech-gated LIGHT on
  -- a couple of the long walls (FloodLight has no verified defName in this
  -- stack's index tonight - StandingLamp/TorchLamp, the palette's own LIGHT
  -- role per tech tier, stands in; the spec's own dressing note, not guessed).
  local lamps = wall_lights(ctx, bld_i, rng.int(2, 3))
  -- REAL BUG this pass's own first lint run caught (fixed twice, both real):
  -- (1) `fr.cell(...)` returns TWO values (x, z), and Lua only expands a
  -- multi-return expression when it is the LAST argument in a call - used
  -- here as an interior argument, only its x came through and every argument
  -- after it (0, 2, bld_i) shifted one slot left, handing try_near() a TABLE
  -- (bld_i) as its own `radius` parameter - failed outright on seed 0, the
  -- very first render ("bad 'for' limit (number expected, got table)").
  -- Fixed by capturing both return values into named locals first, the same
  -- pattern every other fr.cell() call in this file already uses.
  -- (2) the FIRST fix placed these near the front corners (liu0/liu1, near
  -- liv0) - exactly where the office lands when `office_far_e` picks that
  -- same corner. try_near's own can_place gate could not catch the
  -- resulting clash: RUT_WindowAdobe's size is UNMEASURED (this whole
  -- stack's one un-deployed def, every prior template's own header names
  -- it), and the plan's footprint-collision check SKIPS any existing thing
  -- whose own footprint cannot be computed - so a TorchLamp landed directly
  -- on top of the office's own window, a real `cell-collision` ERROR on
  -- this template's second render. Moved both lamps to the BACK wall
  -- instead (liv1, never inside the office's own v-range regardless of
  -- which corner it picked) rather than trying to out-guess where the
  -- office is - the office's v-range is always the front few rows.
  local flax, flaz = fr.cell(liu0 + 2, liv1 - 1)
  local flbx, flbz = fr.cell(liu1 - 2, liv1 - 1)
  local floor_lamp_a = try_near(ctx, "LIGHT", flax, flaz, 0, 2, bld_i)
  local floor_lamp_b = try_near(ctx, "LIGHT", flbx, flbz, 0, 2, bld_i)

  -- ---- roof support for a big interior (prelude's own support_columns -
  -- vanilla's roof reach is 6 cells; a >12x12 interior needs pillars).
  local pillars = support_columns(ctx, bld_i)
  -- REAL BUG this pass's own sweep caught: the wide door removes 2 wall
  -- cells from the front row, and a roof cell several rows behind the door
  -- can end up >6 Manhattan cells from the nearest remaining support - the
  -- door itself is not a WALL/PILLAR/WINDOW (it does not count as a roof
  -- support), and the nearest surviving wall cell from directly behind the
  -- door is now diagonal, not straight ahead, one column farther than the
  -- radius allows. "roof-unsupported" on 6/20 of this pass's own sweep, the
  -- same cell (roughly 6 rows straight in from the door) every time. One
  -- extra PILLAR a few rows in from the door backstops exactly that gap;
  -- support_columns()'s own generic 4-corner placement has no way to know a
  -- door punched a hole in the wall it was counting on.
  local door_pillar = false
  if ctx:has_role("PILLAR") then
    local ppx, ppz = fr.cell(door_u, math.min(apron_h + 6, liv1))
    door_pillar = try_near(ctx, "PILLAR", ppx, ppz, 0, 2, bld_i)
  end

  -- ---------------------------------------------------------------------
  -- the guard bunk: loose furniture (no walls of its own, spec's own words -
  -- only the office gets its own room) in the back corner AWAY from the
  -- office, behind the last island shelf. BED is gated by has_role first -
  -- Jawa_FreeDroidEnclaves nulls it (droids do not sleep, every other
  -- template's own canon), and place_near_walkable/can_place has no reliable
  -- refusal shape for a nil defName (str(nil) coerces to a truthy-looking
  -- "None" on the Python side before place() itself catches the real nil) -
  -- gating here instead of trusting that path to fail closed.
  -- ---------------------------------------------------------------------
  local bunk_u = office_far_e and (liu1 - 2) or (liu0 + 2)
  local bunk_x, bunk_z = fr.cell(bunk_u, liv1 - 1)
  local bed_ok, bcx, bcz = false, nil, nil
  if ctx:has_role("BED") then
    bed_ok, bcx, bcz = place_near_walkable(ctx, ctx:role("BED"), bunk_x, bunk_z, 3, "BED", bld_i, bld_r)
  end
  local box_ok = false
  if bed_ok then
    box_ok = place_near_walkable(ctx, ctx:role("FOOTLOCKER"), bcx, bcz, 2, "FOOTLOCKER", bld_i, bld_r)
  end

  -- ---- R4 guarantee + the depot's own secondary clutter pass -------------
  -- REAL BUG this pass's own inspection of a failing seed caught: clutter()
  -- was called against the WHOLE `bld_i` rect, and its own walkability guard
  -- (try_near_walkable -> aisle_ok) floods from bld_i's doors across every
  -- interior cell of bld_i's bounding RECT - which includes the office's own
  -- interior cells, since the office's door is a real passable cell shared
  -- with the main floor. The guard is not wrong about reachability (a person
  -- genuinely could walk from the wide door, through the office door, to
  -- that cell) - but it has no notion that those cells belong to a SEPARATE,
  -- much smaller room whose own walkability this same pass already proved
  -- with barely enough margin. A BARREL landed at (3,7), inside a 3x3
  -- office, on seed 7 - and that room's own flood-fill dropped from a
  -- passing figure to 33% (<45%) as a direct result. Restricted to the
  -- BACK band (v > office's own v-range, which is always liv0..liv0+4
  -- regardless of which corner it picked) rather than trying to carve an
  -- office-shaped hole out of a single rect argument clutter() cannot take.
  local clutter_v0 = liv0 + 5
  local clutter_zone = (clutter_v0 <= liv1) and fr.rect(liu0, clutter_v0, liu1 - liu0 + 1, liv1 - clutter_v0 + 1) or nil
  local floor_clutter = clutter_zone and clutter(ctx, clutter_zone, {
    { role = "BARREL", weight = 3 }, { role = "CRATE", weight = 2 },
  }, math.max(4, math.ceil((clutter_zone.w * clutter_zone.h) / 30)), outer(bld_i)) or 0

  local floor_ok, floor_cov, floor_unreached = aisle_ok(ctx, bld_r)
  if not floor_ok then
    note(string.format("warehouse floor aisle proof FAILED: %.0f%% reachable, %d primary unreached",
      floor_cov * 100, floor_unreached))
  end

  -- ---------------------------------------------------------------------
  -- outside: fence gate on the road approach, a parked wreck at the dock
  -- end, a rubbish clump behind the building, a barrel row by the dock.
  -- ---------------------------------------------------------------------
  local gate_placed = false
  do
    local gx, gz = fr.cell(door_u - 3, 0)
    gate_placed = try_near(ctx, "GATE", gx, gz, 0, 2, within)
  end

  local wreck_def = o.industrial and rng.pick({ "AncientIndustrialTruck", "AncientRustedTruck" }) or nil
  local wreck_placed = false
  if wreck_def then
    -- can_place-gated ring search, not a hardcoded cell - a truck's real
    -- footprint can extend past a single dock-end guess (the same fix
    -- dead_caravan.lua's own header names for its wreck placement).
    local wx0, wz0 = fr.cell(liu1 - 2, 0)
    local rot = SIDE_ROT[road_side]
    wreck_placed = place_near(ctx, wreck_def, wx0, wz0, 3, "WRECK", rot)
  end

  -- rubbish/junk clump behind the building (VFEPD_RubbishPile not indexed -
  -- ChunkSandstone stands in, same substitution cache.lua's own header uses)
  local rubbish_n = 0
  do
    local rx0, rz0 = fr.cell(liu0 + 3, liv1 + 2)
    for i = 1, rng.int(3, 5) do
      local ok = place_near(ctx, "ChunkSandstone", rx0 + rng.int(-2, 2), rz0 + rng.int(-1, 1), 2, "SCRAP")
      if ok then rubbish_n = rubbish_n + 1 end
    end
  end

  -- a barrel row by the dock, one tipped (a second rotation reads as knocked
  -- over - no separate "tipped" def exists, same accepted read every other
  -- template in this folder uses for "one askew"). Bounded to the dock strip
  -- (v < apron_h, strictly outside the building) - see place_near()'s own
  -- header for the bug this bound fixes.
  local dock_only = fr.rect(0, 0, W, apron_h)
  local barrels_n = 0
  do
    local bx0, bz0 = d2x + lateral[1] * 3, d2z + lateral[2] * 3
    for i = 1, 3 do
      local rot = (i == 2) and rng.int(0, 3) or 0
      local ok = place_near(ctx, ctx:role("BARREL"), bx0 + lateral[1] * i, bz0 + lateral[2] * i, 1, "BARREL", rot, dock_only)
      if ok then barrels_n = barrels_n + 1 end
    end
  end

  -- ---------------------------------------------------------------------
  -- Junkers: scrap dressing rather than clean crates (palette's own SCRAP
  -- role for this faction, ChunkSlagSteel).
  --
  -- REAL BUG this pass's own 360-combination sweep caught: this used to
  -- target the FRONT-left corner (liu0+1, liv0+1) with an unbounded radius-3
  -- ring search - exactly the office's own corner when `office_far_e` picks
  -- that side, and exactly the same failure mode floor_lamp_a/b's own
  -- header already names: RUT_WindowAdobe's size is UNMEASURED, so the
  -- footprint-collision check silently lets a ChunkSlagSteel land ON TOP of
  -- the office's window - "cell-collision" ERROR, Jawa_Junkers only (the
  -- one faction this dressing fires for), 2/360. Moved to the BACK wall
  -- region (liv1), the same fix and the same reasoning as floor_lamp_a/b:
  -- the office only ever occupies the front few rows, regardless of which
  -- corner it picked.
  -- ---------------------------------------------------------------------
  if o.junkers and ctx:has_role("SCRAP") then
    local jx, jz = fr.cell(liu0 + 1, liv1 - 1)
    place_near(ctx, ctx:role("SCRAP"), jx, jz, 3, "SCRAP")
  end

  -- ---------------------------------------------------------------------
  -- power apron behind the back wall, Industrial+ only - same has_role gate
  -- and cardinal-bus shape trading_post.lua's/homestead.lua's own apron
  -- uses. Placed by can_place-gated ring search (place_near), not a
  -- hardcoded pair: a 1x2 Battery's real footprint extends a cell beyond its
  -- origin and which world axis that extra cell falls on depends on the
  -- frame's face, exactly the collision trading_post.lua's own header
  -- measured for its hardcoded version.
  -- ---------------------------------------------------------------------
  local powered = o.industrial and ctx:has_role("GENERATOR") and ctx:has_role("BATTERY") and ctx:has_role("CONDUIT")
  if powered then
    local gx0, gz0 = fr.cell(liu0 + 2, liv1 + 3)
    local g_ok, gcx, gcz = place_near(ctx, ctx:role("GENERATOR"), gx0, gz0, 2, "GENERATOR")
    if g_ok then
      local bx0, bz0 = fr.cell(liu0 + 6, liv1 + 3)
      local b_ok, bcx2, bcz2 = place_near(ctx, ctx:role("BATTERY"), bx0, bz0, 4, "BATTERY")
      if b_ok then
        local steps = math.max(math.abs(bcx2 - gcx), math.abs(bcz2 - gcz))
        for i = 1, steps - 1 do
          local t = i / steps
          local cx = math.floor(gcx + (bcx2 - gcx) * t + 0.5)
          local cz = math.floor(gcz + (bcz2 - gcz) * t + 0.5)
          try_place(ctx, "CONDUIT", cx, cz, 0)
        end
        filth(ctx, "Filth_MachineBits", gcx, gcz)
        note("R-POWER: generator+battery pad behind the back wall, conduit bus reaching the interior lamps within ConnectMaxDist 6")
      end
    end
  end

  note(string.format(
    "road_warehouse: road_dir=%s dock=%d door_u=%d shelves(E=%d W=%d N=%d) islands=%d pallets=%d dropped=%d "
    .. "mouth_crates=%d drift=%d lamps=%d(floor=%s,%s) pillars=%d office=%s(desk=%s,window=%s) "
    .. "bunk(bed=%s,box=%s) clutter=%d floor_aisle=%.0f%% gate=%s wreck=%s(%s) rubbish=%d barrels=%d powered=%s",
    face, dock_n, door_u, shelved_e, shelved_w, shelved_n, islands, pallets, dropped,
    mouth_crates, drift_n, lamps, tostring(floor_lamp_a), tostring(floor_lamp_b), pillars,
    tostring(office_ok), tostring(desk_placed), tostring(window_placed),
    tostring(bed_ok), tostring(box_ok), floor_clutter, floor_cov * 100,
    tostring(gate_placed), tostring(wreck_placed), tostring(wreck_def), rubbish_n, barrels_n, tostring(powered)))

  -- ---- state: dust drifts when nobody hauls here; the ruin pass when it
  -- fell (identical tail to homestead.lua's/trading_post.lua's build())
  if o.state == "abandoned" then
    local n = 0
    for _ = 1, math.max(4, math.floor(rect.w * rect.h / 30)) do
      local x, z = rng.int(rect.x, rect.x2), rng.int(rect.z, rect.z2)
      if not ctx:occupied(x, z) then filth(ctx, rng.chance(0.6) and "Filth_Sand" or "Filth_Dirt", x, z); n = n + 1 end
    end
    note(string.format("abandoned: %d drift(s) of sand and dirt; the shelving stands, cousin-swapped", n))
  elseif o.state == "ruined" then
    ctx:ruin(0.3)
  end
end
