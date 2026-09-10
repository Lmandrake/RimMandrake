-- crashed_ship.lua - "The Crashed Ship" (structure_procedural_spec.md sec 8.9).
-- NEW template - sibling of podracer_wreck.lua (small, no walls) and
-- broken_ring.lua (terrain-led): this is the first sec-8 wreck with an
-- actual walled hull. Catalogue C2. Roster #6 "The Dead Crawler" (a
-- three-deck sandcrawler) is a separate, bigger flagship template still
-- owed - this is a one-deck STARSHIP, broken open on the ground.
--
-- Grammar, bow -> stern, all along a single `heading` axis (u = along the
-- hull's length in the heading direction, v = lateral): impact furrow ->
-- hull (cockpit, crew, hold/engine compartments, one straight-walled room)
-- -> stern debris trail. The spec's own "hull on a slant = staggered wall
-- runs offset by 1" is realized as three DIFFERENT compartment widths
-- (3/5/6) inside one straight outer hull shell, rather than a free-form
-- diagonal outline: `ctx:room()`'s own sealing/floor bookkeeping (and the
-- lint's room-not-sealed / room-unreachable ERRORs) are defined against ONE
-- rectangular room per registration, so a genuinely jagged outer perimeter
-- would need hand-rolled sealing proofs the engine has no primitive for.
-- The visual "break" instead comes from where each compartment's furniture
-- clusters versus the flanking hull-plate deadspace, from the two interior
-- bulkheads (one a real door, one a true wall GAP - "one jammed"), and from
-- two random-walk roof tears (spec's own "2 irregular blobs").
--
-- Real defNames verified against the live RimSage index tonight
-- (2026-09-10). Same situation dead_caravan.lua/mining_site.lua/
-- garrison_tiny.lua/road_warehouse.lua/trading_post.lua already hit and
-- documented: the active mod list tonight does not index the WHOLE spec
-- vocabulary, so this file substitutes wherever the spec's own name comes
-- up empty, and says so:
--   MUS_SpaceBase_* (Wall, WallV, Window, Door, Bed, Lockers, SmallTable,
--     BarStool, Cabinet, MachineryModule, MonitorModule) - a bare "MUS_"
--     query returns zero hits: this whole mod is not indexed tonight.
--     The spec text ITSELF already gives the fallback for the hull walls
--     ("or `Wall` stuffed `Steel`/`Plasteel`") - used directly, not even
--     really a substitution. WINDOW is skipped entirely rather than routed
--     through the palette WINDOW role: every tier's WINDOW mapping
--     (RUT_WindowAdobe/AM_Wall_Atlas_Glass/MUS_SpaceBase_Window) failed
--     search_defs tonight too (trading_post.lua's header already flagged
--     this exact gap), so calling ctx:window() here would just fail
--     `rimplace verify` on a pre-existing, unrelated gap.
--   VFEPD_Destroyed{SmallHeatsink,LargeThruster,SmallThruster,GravExtender,
--     SmallOxygenTank} / VFEPD_RuinedLabLamp / VFEPD_AncientElectricalEquipment
--     - no sibling template cites this family (only VFEPD_Banner,
--     _WeaponRackSpears, _AncientBrokenTurret, _WoodenChest[Large],
--     _AncientCrate, the mining-car/wagon family and _AncientSemiTrailer/
--     _RubbishPile are precedented, and VFEPD_Banner itself failed a direct
--     search just now - it is not actually verified anywhere, just used).
--     Substituted with real vanilla ThingDefs that read the same way:
--     `SmallThruster`/`LargeThruster` (the game's OWN gravship thruster
--     props) sheared off at odd rotations for the destroyed-thruster pair,
--     `AncientGravEngine` for the grav-extender read, `ChunkSlagSteel` +
--     `Filth_MachineBits` standing in for the heatsink/oxygen-tank pair and
--     for the Zizzik "sparking equipment" flavour beat - the same "debris
--     that reads right, not invented" discipline podracer_wreck.lua/
--     broken_ring.lua already use.
--   `OuterRim_AurebeshWordCommand` and `VFEPD_Banner` skipped for the
--     Imperial variant for the same reason - the Imperial read leans on
--     fitment DENSITY (an extra console/locker-bank) instead of a sign or
--     banner prop.
--   `Ship_Reactor` exists (measured via defsize: **6x7**) but is bigger
--     than this template's own hold compartment's gross footprint (6x6
--     outer per spec) - it cannot fit under ANY rotation. Only `Ship_Engine`
--     (measured 3x4) is used for the hold centrepiece; Reactor is not
--     placed anywhere in this file. Measured, not guessed - CLAUDE.md's own
--     rule for a number about a large artifact.
--   `MetalCrateA`/`ASF_WovenBasket` etc. (the Junkers-seat crates) - not
--     indexed; `AncientMetalCrate` (verified, already dead_caravan.lua's
--     own crate-pool member) used instead.
--   RH2_ClassicFootlocker / VGE_CrewLockers - not indexed (same RH2_/VGE_
--     gap garrison_tiny.lua and road_warehouse.lua already hit); `AncientLockers`
--     and `AncientLockerBank` (both verified) cover the locker/footlocker
--     read together rather than as three separate props.
--   Real, directly-verified defNames used throughout: Wall, Steel, Plasteel,
--     AncientBlastDoor, Substructure (TerrainDef), SoftSand, Gravel,
--     Ship_ComputerCore, Ship_SensorCluster, Ship_Engine, AncientArmchair,
--     AncientSingleBed, AncientLockers, AncientLockerBank, Table1x2c,
--     DiningChair, Ship_CryptosleepCasket, AncientGenerator,
--     AncientMilitaryGeneratorSmall, PowerConduit, AncientSpacerCrate,
--     AncientSealedCrate, AncientHermeticCrate, AncientMetalCrate, Campfire,
--     Bedroll, AncientLamp, ChunkSlagSteel, ShipChunk, MechCapsule,
--     AncientGravEngine, SmallThruster, LargeThruster, Filth_Fuel,
--     Filth_BlastMark, Filth_MoldyUniform, Filth_ScatteredDocuments,
--     Filth_Blood, Filth_Dirt, Filth_Ash, Filth_Trash, Filth_OilSmear,
--     Filth_MachineBits, Filth_RubbleBuilding, SpaceRefugee (PawnKindDef -
--     "space refugee", the crew/pilot remains; thematically closer than
--     dead_caravan.lua's own Tribal_Trader reuse, and it IS verified).
--
-- params:
--   heading   "N"|"E"|"S"|"W" (default "E") - the direction the bow points;
--             the furrow lies ahead of the bow, the debris trail behind the
--             stern. min_rect swaps its own w/h for a vertical heading.
--   variant   "imperial"|"junkers"|"zizzik" - unset rolls one evenly. See
--             the variant pass near the end of build() for what each does.
--
-- API available: ctx (see luaenv.Ctx), rect, params, rng, role(), note()

local function clamp(v, lo, hi) return math.max(lo, math.min(hi, v)) end

-- world (x,z) for canvas-local (u,v): u runs from the furrow toward the
-- stern in the heading direction, v is lateral. Same axis discipline
-- dead_caravan.lua's road_frame already established, generalised to whole
-- rects (a compartment's outer footprint) as well as single cells.
local function local_rect(heading, r, u0, v0, ulen, vlen)
  if heading == "W" then
    return R(r.x2 - u0 - ulen + 1, r.z + v0, ulen, vlen)
  elseif heading == "N" then
    return R(r.x + v0, r.z + u0, vlen, ulen)
  elseif heading == "S" then
    return R(r.x + v0, r.z2 - u0 - ulen + 1, vlen, ulen)
  end
  return R(r.x + u0, r.z + v0, ulen, vlen)          -- "E", also the fallback
end

local function try_def(ctx, def, role_tag, x, z, rot)
  rot = rot or 0
  if not ctx:can_place(def, x, z, rot) then return false end
  return ctx:place(def, x, z, rot, nil, role_tag)
end

local function filth(ctx, def, x, z)
  return ctx:place(def, x, z, 0, nil, "FILTH", true)
end

-- ring search for a raw defName, same shape as dead_caravan.lua's own
-- place_near - prelude's try_near only works on palette ROLES. Always takes
-- separate x,z (never a multi-return cell() inline: that truncates to one
-- value in any non-tail argument position - a real bug this file hit and
-- fixed before the first render).
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

-- WALKABILITY-CHECKED variants of the two above, for every IMPASSABLE-role
-- thing placed inside the one-room hull. First real generator-facing bug
-- found while testing this template (not a template-logic slip): an
-- unguarded ring search for a big rotated footprint (Ship_Engine, 3x4) or a
-- rotated multi-cell prop (AncientLockerBank) can land squarely on the one
-- lateral row a hull-length room's single door breathes through, or simply
-- overcrowd a 4-cell-wide hold until some prior placement has no reachable
-- neighbour left - `rimplace.plan._aisle_fill` (the lint's own flood-fill)
-- caught it directly: coverage 0.0-0.5, several primaries "unreached", on
-- roughly 2/3 of 30 seeds tried. `can_place` has no idea a cell is
-- load-bearing for reachability - it only checks footprint collision.
-- prelude.lua already ships the fix for palette ROLES (`try_near_walkable`,
-- gated on `aisle_ok`), but it calls `ctx:has_role(role)` internally and
-- every prop in this file is a raw defName, not a role, so that gate always
-- fails for them. These two mirror its exact aisle_ok-before-place
-- discipline (`footprint_sw` + `aisle_ok`, both already raw-defName-safe:
-- `width_of`/`height_of` fall back to the literal name when `role()` finds
-- no palette entry) without requiring a fake palette role per prop.
local function try_def_walkable(ctx, def, role_tag, x, z, rot, shell)
  rot = rot or 0
  if not ctx:can_place(def, x, z, rot) then return false end
  local x0, z0, w, h = footprint_sw(ctx, def, x, z, rot)
  local fp = {}
  for dx = 0, w - 1 do for dz = 0, h - 1 do fp[#fp + 1] = { x0 + dx, z0 + dz } end end
  if not aisle_ok(ctx, shell, fp) then return false end
  return ctx:place(def, x, z, rot, nil, role_tag)
end

local function place_near_walkable(ctx, def, x, z, radius, role_tag, rot, shell)
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
        local x0, z0, w, h = footprint_sw(ctx, def, c[1], c[2], rot)
        local fp = {}
        for dx = 0, w - 1 do for dz = 0, h - 1 do fp[#fp + 1] = { x0 + dx, z0 + dz } end end
        if aisle_ok(ctx, shell, fp) then
          ctx:place(def, c[1], c[2], rot, nil, role_tag)
          return true, c[1], c[2]
        end
      end
    end
  end
  return false
end

local function scatter_def(ctx, def, r, n, opts)
  opts = opts or {}
  local placed, tries = 0, 0
  local max_tries = opts.tries or n * 20
  while placed < n and tries < max_tries do
    tries = tries + 1
    local x, z = rng.int(r.x, r.x2), rng.int(r.z, r.z2)
    if not ctx:occupied(x, z) then
      local rot = opts.rot
      if rot == nil then rot = 0 elseif rot == "any" then rot = rng.int(0, 3) end
      if ctx:can_place(def, x, z, rot) then
        ctx:place(def, x, z, rot)
        placed = placed + 1
      end
    end
  end
  return placed
end

-- E1-style random-walk blob in (u,v) space, clamped to [umin,umax]x[vmin,vmax].
-- Used for the roof tears (spec's own "2 irregular blobs", same technique
-- beast_lair.lua's header names for its own CLEAR blob).
local function walk_blob(u0, v0, steps, umin, umax, vmin, vmax)
  local u, v = u0, v0
  local seen, cells = {}, {}
  for _ = 1, steps do
    local key = u .. "," .. v
    if not seen[key] then
      seen[key] = true
      cells[#cells + 1] = { u, v }
    end
    local dir = rng.int(1, 4)
    if dir == 1 then u = u + 1
    elseif dir == 2 then u = u - 1
    elseif dir == 3 then v = v + 1
    else v = v - 1 end
    u = clamp(u, umin, umax)
    v = clamp(v, vmin, vmax)
  end
  return cells
end

function min_rect(params)
  local hd = (params and params.heading) or "E"
  if hd == "N" or hd == "S" then return 20, 30 end
  return 30, 20
end

function build(ctx)
  local p = params
  local heading = p.heading
  if heading ~= "N" and heading ~= "E" and heading ~= "S" and heading ~= "W" then heading = "E" end
  local vertical = (heading == "N" or heading == "S")
  local along, lateral
  if vertical then along, lateral = rect.h, rect.w else along, lateral = rect.w, rect.h end
  if along < 30 or lateral < 20 then
    ctx:refuse("footprint", string.format(
      "%dx%d does not give the crashed-ship grammar its 30-long x 20-lateral "
      .. "minimum (heading=%s)", rect.w, rect.h, heading))
    return
  end

  local variant = p.variant
  if variant ~= "imperial" and variant ~= "junkers" and variant ~= "zizzik" then
    variant = rng.pick({ "imperial", "junkers", "zizzik" })
  end

  local function cell(u, v)
    local r = local_rect(heading, rect, u, v, 1, 1)
    return r.x, r.z
  end

  -- ---- geometry: furrow, hull (3 compartments + 2 bulkheads), stern debris
  local FURROW_LEN = rng.int(6, 8)
  local D_COCKPIT, D_CREW, D_HOLD = 4, 5, 6
  local HULL_W = 6
  local LATERAL_CENTER = math.floor(lateral / 2)
  local HULL_V0 = LATERAL_CENTER - math.floor(HULL_W / 2)
  local HULL_V1 = HULL_V0 + HULL_W - 1
  local hull_center_v = HULL_V0 + math.floor(HULL_W / 2)
  -- A SPINE CORRIDOR, always the same lateral row for the whole hull length:
  -- the boarding door's own interior threshold (HULL_V0+1, one step off the
  -- port wall it sits in) doubles as both bulkheads' gap row. Measured with
  -- `rimplace.plan._aisle_fill` directly (not guessed): with the two
  -- bulkhead gaps at INDEPENDENT random rows, the hold's own furniture
  -- (engine/generators/lockers, all IMPASSABLE roles, packed into a
  -- 4-cell-wide interior) reliably sealed off whichever row the boarding
  -- door actually opened onto from whichever row the far bulkhead's door/gap
  -- happened to land on - coverage read 10% and 9-14 of ~13 primaries came
  -- back unreached on every one of 10 seeds tried. A single shared row,
  -- kept furniture-free end to end, is what R3/E4's own aisle_ok machinery
  -- exists to guarantee for a regular room; this hull has no regular rooms
  -- to hand it to, so the row is reserved by construction instead.
  -- Every IMPASSABLE-role placement below still ALSO anchors away from this
  -- row on purpose (belt and suspenders): try_def_walkable/place_near_
  -- walkable's own aisle_ok check is what actually guarantees the corridor
  -- stays open (see their own comment above), this just keeps the common
  -- case from needing a retry.
  local CORRIDOR_V = HULL_V0 + 1
  local FURN_V0, FURN_V1 = HULL_V0 + 2, HULL_V1 - 1

  local U0 = FURROW_LEN                        -- bow wall column
  local cockpit_u0, cockpit_u1 = U0 + 1, U0 + D_COCKPIT
  local PART1_U = cockpit_u1 + 1
  local crew_u0, crew_u1 = PART1_U + 1, PART1_U + D_CREW
  local PART2_U = crew_u1 + 1
  local hold_u0, hold_u1 = PART2_U + 1, PART2_U + D_HOLD
  local STERN_U = hold_u1 + 1                  -- stern wall column
  local HULL_D = STERN_U - U0 + 1

  local hull = local_rect(heading, rect, U0, HULL_V0, HULL_D, HULL_W)
  local WALL_STUFF = rng.pick({ "Steel", "Plasteel" })

  -- ---- the hull shell: one straight room, roofed selectively below --------
  ctx:room("ShipHull", hull.x, hull.z, hull.w, hull.h, false)
  ctx:wall_rect(hull.x, hull.z, hull.w, hull.h, "Wall", WALL_STUFF)
  local hin = inner(hull)
  ctx:floor_rect(hin.x, hin.z, hin.w, hin.h, "Substructure")

  -- ---- the two bulkheads: one door, one a true wall gap ("one jammed") ----
  local door_part = rng.pick({ 1, 2 })
  local gap1 = CORRIDOR_V
  local gap2 = CORRIDOR_V
  local function bulkhead(u, gap_v, has_door)
    local door_placed = false
    for v = HULL_V0, HULL_V1 do
      local x, z = cell(u, v)
      if v == gap_v then
        if has_door then door_placed = ctx:door(x, z, "AncientBlastDoor") end
      else
        ctx:place("Wall", x, z, 0, WALL_STUFF, "WALL")
      end
    end
    return door_placed
  end
  local door1_ok = bulkhead(PART1_U, gap1, door_part == 1)
  local door2_ok = bulkhead(PART2_U, gap2, door_part == 2)
  local jammed_at = (door_part == 1) and "crew|hold" or "cockpit|crew"

  -- ---- an exterior boarding door on the hold's port wall -------------------
  local board_u = rng.int(hold_u0, hold_u1)
  local board_x, board_z = cell(board_u, HULL_V0)
  local board_ok = ctx:door(board_x, board_z, "AncientBlastDoor")

  -- ---- roof: the whole hull, minus 2 random-walk interior tears ------------
  -- kept out of the corridor row too (FURN_V0..FURN_V1), same reason as the
  -- furniture below: torn-cell rubble is a real, non-overlay thing and would
  -- block the one lane the flood-fill actually walks.
  -- Blob CENTRES favour the CREW compartment specifically, not cockpit and
  -- not hold. Measured, twice: centres spread across the whole interior
  -- broke the hold's only 3 possible Ship_Engine positions often enough to
  -- sink its placement rate to ~35-55% (40-seed sweep); moving the bias to
  -- "everywhere but hold" fixed the engine (96%) but then hit cockpit
  -- instead - a 4-column compartment where one blob can cover BOTH
  -- Ship_ComputerCore slots, and console placement dropped from 33/40 to
  -- 23/40 measuring the same change. Crew is the one compartment with room
  -- to absorb it (5 columns, more flexible furniture). A blob's own random
  -- walk can still drift a step or two into either neighbour (its bounds
  -- below are unchanged), so neither is immune to damage, just no longer
  -- the favoured target.
  local torn = {}
  for _ = 1, 2 do
    local bu = rng.int(crew_u0, crew_u1)
    local bv = rng.int(FURN_V0, FURN_V1)
    for _, c in ipairs(walk_blob(bu, bv, rng.int(8, 12), cockpit_u0, hold_u1, FURN_V0, FURN_V1)) do
      torn[c[1] .. "," .. c[2]] = true
    end
  end
  local roofed, torn_n = 0, 0
  for u = U0, STERN_U do
    for v = HULL_V0, HULL_V1 do
      local x, z = cell(u, v)
      if torn[u .. "," .. v] then
        torn_n = torn_n + 1
        if rng.chance(0.5) then try_def_walkable(ctx, "ChunkSlagSteel", "WRECK", x, z, nil, hull) end
        if rng.chance(0.3) then filth(ctx, "Filth_RubbleBuilding", x, z) end
      elseif ctx:roof(x, z) then
        roofed = roofed + 1
      end
    end
  end

  -- ==== FURROW: ahead of the bow ============================================
  local furrow_v0, furrow_v1 = hull_center_v - 2, hull_center_v + 1  -- 4 wide
  local blast_n, slag_n, chunk_n = 0, 0, 0
  for u = 0, U0 - 1 do
    for v = furrow_v0, furrow_v1 do
      local x, z = cell(u, v)
      ctx:floor(x, z, rng.chance(0.7) and "SoftSand" or "Gravel")
    end
  end
  -- Filth_BlastMark measures 3x3 (defsize) - kept 1 cell off the rect's own
  -- low edge (u=0 sits ON rect.x/rect.z for an "E"/"N" heading), same margin
  -- dead_caravan.lua's own header already documents needing for this exact
  -- overlay ("measured: Filth_BlastMark did exactly this on 20/192 sweep
  -- cells before this margin was added").
  for _ = 1, rng.int(3, 5) do
    local x, z = cell(rng.int(1, math.max(1, U0 - 1)), rng.int(furrow_v0, furrow_v1))
    filth(ctx, "Filth_BlastMark", x, z); blast_n = blast_n + 1
  end
  for u = 0, U0 - 1 do
    for v = furrow_v0, furrow_v1 do
      local chance = 0.05 + 0.35 * (u / math.max(1, U0 - 1))
      if rng.chance(chance) then
        local x, z = cell(u, v)
        if try_def(ctx, "ChunkSlagSteel", "WRECK", x, z) then slag_n = slag_n + 1 end
      end
    end
  end
  for u = 0, U0 - 1 do
    local x, z = cell(u, hull_center_v)
    filth(ctx, "Filth_Fuel", x, z)
  end
  for _ = 1, rng.int(1, 2) do
    local fx, fz = cell(rng.int(0, math.max(0, U0 - 2)), rng.int(furrow_v0, furrow_v1))
    local ok = place_near(ctx, "ShipChunk", fx, fz, 2, "WRECK")
    if ok then chunk_n = chunk_n + 1 end
  end
  local sensor_x, sensor_z = cell(U0 - 1, hull_center_v)
  local sensor_ok = try_def(ctx, "Ship_SensorCluster", "MACHINE", sensor_x, sensor_z)

  -- ==== COCKPIT ==============================================================
  -- Ship_ComputerCore is 2x2 in a compartment only 4 columns deep - a fixed
  -- single-cell try_def_walkable measured ~72% (29/40 seeds placed at least
  -- one), the aisle_ok gate having nowhere else to look on the seeds where
  -- the exact anchor cell didn't work. A radius-1 ring search costs nothing
  -- and gives it somewhere else to try.
  local consoles, armchairs = 0, 0
  for _, v in ipairs({ FURN_V0, FURN_V1 }) do
    local x, z = cell(cockpit_u0, v)
    if place_near_walkable(ctx, "Ship_ComputerCore", x, z, 1, "MACHINE", nil, hull) then consoles = consoles + 1 end
  end
  local seat_x, seat_z = cell(cockpit_u0 + 1, hull_center_v)
  if try_def(ctx, "AncientArmchair", "CHAIR", seat_x, seat_z, 2) then
    armchairs = armchairs + 1
    filth(ctx, "Filth_Blood", seat_x, seat_z)
  end
  do
    local ax, az = cell(cockpit_u0 + 1, hull_center_v + 1)
    if place_near(ctx, "AncientArmchair", ax, az, 2, "CHAIR") then armchairs = armchairs + 1 end
  end
  for _ = 1, 2 do
    local x, z = cell(rng.int(cockpit_u0, cockpit_u1), rng.int(HULL_V0 + 1, HULL_V1 - 1))
    filth(ctx, "Filth_ScatteredDocuments", x, z)
  end

  -- ==== CREW =================================================================
  -- a fixed single-cell try (no fallback) for each bed measured well below
  -- the other compartments' rates once the roof-tear bias moved onto crew
  -- (see the blob-bias comment above) - a radius-1 ring search recovers it
  -- the same way the engine's and consoles' own fixed tries needed one.
  local beds, lockers = 0, 0
  do
    local x, z = cell(crew_u0 + 1, FURN_V0)
    if place_near_walkable(ctx, "AncientSingleBed", x, z, 1, "BED", 1, hull) then beds = beds + 1 end
  end
  do
    local x, z = cell(crew_u1 - 1, HULL_V1 - 1)
    if place_near_walkable(ctx, "AncientSingleBed", x, z, 1, "BED", 3, hull) then beds = beds + 1 end
  end
  do
    local x, z = cell(crew_u0, hull_center_v)
    if place_near_walkable(ctx, "AncientLockers", x, z, 2, "LOCKER", nil, hull) then lockers = lockers + 1 end
  end
  do
    local x, z = cell(crew_u1, hull_center_v)
    if place_near_walkable(ctx, "AncientLockers", x, z, 2, "LOCKER", nil, hull) then lockers = lockers + 1 end
  end
  local table_x, table_z = cell(crew_u0 + math.floor(D_CREW / 2), hull_center_v)
  local table_ok = try_def_walkable(ctx, "Table1x2c", "TABLE", table_x, table_z, nil, hull)
  place_near(ctx, "DiningChair", table_x + 1, table_z, 2, "CHAIR")
  place_near(ctx, "DiningChair", table_x - 1, table_z, 2, "CHAIR")
  -- anchored on the MID row of the 3-row furniture band (hull_center_v, not
  -- FURN_V0/FURN_V1): a rotated multi-cell footprint's exact extension
  -- direction from its anchor cell is not something a template can query
  -- (ctx:footprint_of exists but its result cannot be iterated from the
  -- sandboxed Lua runtime - tried `python.iterex`, the sandbox has no
  -- `python` global at all). Anchoring at the middle row means even a 1-cell
  -- spill either way in v still lands inside [FURN_V0,FURN_V1], never on
  -- CORRIDOR_V - convention-proof rather than convention-guessed. This is
  -- exactly the AncientLockerBank bug below, generalised.
  local caskets = 0
  do
    local cx, cz = cell(crew_u0 + 1, hull_center_v)
    for _ = 1, rng.int(1, 2) do
      if place_near_walkable(ctx, "Ship_CryptosleepCasket", cx, cz, 3, "MACHINE", nil, hull) then caskets = caskets + 1 end
    end
  end
  do
    local x, z = cell(crew_u1, hull_center_v)
    filth(ctx, "Filth_MoldyUniform", x, z)
  end
  do
    local x, z = cell(crew_u0, hull_center_v - 1)
    filth(ctx, "Filth_Dirt", x, z)  -- the dead PlantPot's own spec read
  end

  -- ==== HOLD / ENGINE ========================================================
  -- Ship_Engine measures 3x4 (defsize) and the hold interior is only 4 cells
  -- wide (HULL_W-2); a free rot 0-3 let its 4-long side land ACROSS the
  -- width at rot 0/2, reaching v=HULL_V0+1 - the boarding door's own
  -- interior threshold row - and blocking it outright. Measured with
  -- `rimplace.plan._aisle_fill` directly: that footprint sat on the flood
  -- fill's only seed cell, so coverage read 0.0 and EVERY primary in the
  -- room (13 of them) came back "unreached" - not a template-logic mistake,
  -- an actual generator-facing bug (a big rotated footprint silently eating
  -- the one door a whole room breathes through). Fixed by keeping the
  -- engine's long (4) axis along u (depth, 6 cells to spare) rather than v
  -- (width, exactly 4 cells - zero spare) - rot 1/3 only.
  -- a single fixed-cell try (no fallback) measured a ~35% placement rate
  -- across a 40-seed sweep, purely from the aisle_ok gate having nowhere
  -- else to look when the anchor cell itself is not the one that works;
  -- a short ring search fixes it without loosening the walkability gate.
  local engine_x, engine_z = cell(hold_u0 + math.floor(D_HOLD / 2), hull_center_v)
  local engine_ok = place_near_walkable(ctx, "Ship_Engine", engine_x, engine_z, 2, "MACHINE", rng.pick({ 1, 3 }), hull)
  local mach1, mach2
  do
    local x, z = cell(hold_u0, FURN_V0)
    mach1 = try_def_walkable(ctx, "AncientGenerator", "GENERATOR", x, z, nil, hull)
  end
  do
    local x, z = cell(hold_u1, HULL_V1 - 1)
    mach2 = try_def_walkable(ctx, "AncientMilitaryGeneratorSmall", "GENERATOR", x, z, nil, hull)
  end
  do
    local x, z = cell(hold_u0 + 1, FURN_V0)
    place_near_walkable(ctx, "AncientLockerBank", x, z, 2, "LOCKER", nil, hull)  -- natural [3,1]: height 1, zero v-spill regardless of anchor
  end
  local hold_rect = local_rect(heading, rect, hold_u0, FURN_V0, D_HOLD, FURN_V1 - FURN_V0 + 1)
  local conduit_n = scatter_def(ctx, "PowerConduit", hold_rect, rng.int(3, 4))
  local oil_n = 0
  for _ = 1, rng.int(2, 4) do
    local x, z = cell(rng.int(hold_u0, hold_u1), rng.int(HULL_V0 + 1, HULL_V1 - 1))
    filth(ctx, "Filth_OilSmear", x, z); oil_n = oil_n + 1
  end
  for _ = 1, rng.int(3, 5) do
    local x, z = cell(rng.int(hold_u0, hold_u1), rng.int(HULL_V0 + 1, HULL_V1 - 1))
    filth(ctx, "Filth_MachineBits", x, z)
  end

  local crates, campfire_ok, seats, camp_beds = 0, false, 0, 0
  local clump_x, clump_z = cell(hold_u1 - 1, HULL_V1 - 1)
  if variant == "junkers" then
    -- "already picked it": crates gone, trash and a camp instead
    for _ = 1, rng.int(3, 5) do
      local x, z = cell(rng.int(hold_u0, hold_u1), rng.int(HULL_V0 + 1, HULL_V1 - 1))
      filth(ctx, "Filth_Trash", x, z)
    end
    local fx, fz = cell(hold_u1 - 1, hull_center_v)
    campfire_ok = try_def_walkable(ctx, "Campfire", "STOVE", fx, fz, nil, hull)
    for _, off in ipairs({ { 1, 0 }, { -1, 0 } }) do
      if place_near(ctx, "AncientMetalCrate", fx + off[1], fz + off[2], 2, "SEAT") then seats = seats + 1 end
    end
    local bx, bz = cell(hold_u0 + 1, HULL_V1 - 1)
    for _ = 1, rng.int(1, 2) do
      if place_near_walkable(ctx, "Bedroll", bx, bz, 2, "BED", rng.int(0, 3), hull) then camp_beds = camp_beds + 1 end
    end
  else
    local crate_pool = { "AncientSpacerCrate", "AncientSealedCrate", "AncientHermeticCrate" }
    for i = 1, rng.int(3, 5) do
      local def = crate_pool[((i - 1) % #crate_pool) + 1]
      local ok, cx, cz = place_near_walkable(ctx, def, clump_x, clump_z, 2, "CRATE", nil, hull)
      if ok then
        crates = crates + 1
        if i == 1 then
          place_near_walkable(ctx, def, cx + 1, cz + 1, 2, "CRATE", nil, hull)  -- one tipped 1 off the clump
        end
      end
    end
  end

  -- ---- variant flavour --------------------------------------------------
  if variant == "imperial" then
    -- "Coruscant fittings" read via fitment DENSITY, not a sign/banner def
    -- (OuterRim_AurebeshWordCommand / VFEPD_Banner both fail search_defs
    -- tonight - see header). An extra console and locker bank stand in.
    do
      local x, z = cell(cockpit_u0, hull_center_v)
      try_def_walkable(ctx, "Ship_ComputerCore", "MACHINE", x, z, nil, hull)
    end
    do
      local x, z = cell(hold_u1 - 1, FURN_V0)
      place_near_walkable(ctx, "AncientLockerBank", x, z, 2, "LOCKER", nil, hull)  -- natural [3,1]: height 1, zero v-spill regardless of anchor
    end
  elseif variant == "zizzik" then
    -- VFEPD_AncientElectricalEquipment is not indexed tonight (see header);
    -- sparking wiring substituted with a broken conduit stub + machine bits.
    scatter_def(ctx, "PowerConduit", hold_rect, 2)
    for _ = 1, 2 do
      local x, z = cell(rng.int(hold_u0, hold_u1), rng.int(HULL_V0 + 1, HULL_V1 - 1))
      filth(ctx, "Filth_MachineBits", x, z)
    end
  end

  -- ==== lights (none live) ===================================================
  local lamps = 0
  do
    local x, z = cell(cockpit_u0 + 1, hull_center_v - 1)
    if place_near(ctx, "AncientLamp", x, z, 2, "LIGHT") then lamps = lamps + 1 end
  end
  do
    local x, z = cell(hold_u0, hull_center_v)
    if place_near(ctx, "AncientLamp", x, z, 2, "LIGHT") then lamps = lamps + 1 end
  end

  -- ==== STERN DEBRIS TRAIL ====================================================
  local debris_r = local_rect(heading, rect, STERN_U + 1, math.max(0, LATERAL_CENTER - 4),
    math.max(1, along - STERN_U - 1), math.min(lateral, 8))
  local thrusters = 0
  for _, def in ipairs({ "LargeThruster", "SmallThruster" }) do
    local x, z = cell(STERN_U + rng.int(2, 4), hull_center_v + rng.pick({ -2, 2 }))
    if try_def(ctx, def, "MACHINE", x, z, rng.int(0, 3)) then thrusters = thrusters + 1 end
  end
  local grav_ok
  do
    local x, z = cell(STERN_U + 3, hull_center_v)
    grav_ok = try_def(ctx, "AncientGravEngine", "MACHINE", x, z, rng.int(0, 3))
  end
  for _ = 1, rng.int(2, 3) do
    scatter_def(ctx, "ChunkSlagSteel", debris_r, 1)
    scatter_def(ctx, "Filth_MachineBits", debris_r, 1)
  end

  -- ==== general debris field + ash =============================================
  local ship_chunks = scatter_def(ctx, "ShipChunk", debris_r, rng.int(2, 4))
  for _ = 1, rng.int(2, 3) do
    scatter_def(ctx, "Filth_Ash", debris_r, 1)
  end
  local mech_capsule = rng.chance(0.2) and (scatter_def(ctx, "MechCapsule", debris_r, 1) > 0)

  -- ==== bodies (E3) ============================================================
  local bodies = 0
  local pilot_state = rng.pick({ "skeleton", "dessicated" })
  ctx:pawn("SpaceRefugee", seat_x, seat_z, "wild", pilot_state); bodies = bodies + 1
  -- "halfway out the breach": at the first torn-roof cell we found, if any.
  local breach_u, breach_v = nil, nil
  for k in pairs(torn) do
    local uu, vv = k:match("(-?%d+),(-?%d+)")
    breach_u, breach_v = tonumber(uu), tonumber(vv)
    break
  end
  if breach_u then
    local bx, bz = cell(breach_u, breach_v)
    ctx:pawn("SpaceRefugee", bx, bz, "wild", rng.pick({ "skeleton", "dessicated" }))
    bodies = bodies + 1
  end
  if rng.chance(0.5) then
    local bx, bz = cell(rng.int(crew_u0, hold_u1), rng.int(HULL_V0 + 1, HULL_V1 - 1))
    ctx:pawn("SpaceRefugee", bx, bz, "wild", rng.pick({ "skeleton", "dessicated" }))
    bodies = bodies + 1
  end

  note(string.format(
    "crashed_ship: heading=%s variant=%s furrow=%d hull=%dx%d jammed=%s doors[part=%s board=%s] "
    .. "roof[on=%d torn=%d] furrow[blast=%d slag=%d fuel_u=%d chunk=%s sensor=%s] "
    .. "cockpit[consoles=%d armchairs=%d] crew[beds=%d lockers=%d table=%s caskets=%d] "
    .. "hold[engine=%s mach=%s/%s crates=%d campfire=%s seats=%d beds=%d conduit=%d oil=%d] "
    .. "lamps=%d stern[thrusters=%d grav=%s junk=%d mech=%s] bodies=%d",
    heading, variant, FURROW_LEN, hull.w, hull.h, jammed_at,
    tostring(door_part), tostring(board_ok),
    roofed, torn_n, blast_n, slag_n, U0, tostring(chunk_n > 0), tostring(sensor_ok),
    consoles, armchairs, beds, lockers, tostring(table_ok), caskets,
    tostring(engine_ok), tostring(mach1), tostring(mach2), crates, tostring(campfire_ok), seats, camp_beds,
    conduit_n, oil_n,
    lamps, thrusters, tostring(grav_ok), ship_chunks, tostring(mech_capsule), bodies))
end
