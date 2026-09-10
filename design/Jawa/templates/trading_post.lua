-- trading_post.lua - "Trading outpost (tiny)" (structure_procedural_spec.md
-- sec 8.4). NEW template - the 6th of the 14 sec-8 archetypes built under
-- INHABITED_AUGMENTATION_BUILD_1 (after 8.1 homestead, 8.2 moisture farm,
-- 8.3 mining site, 8.14 cache, 8.10 dead caravan). Picked as the cleanest
-- remaining candidate: no NEW content, no named prerequisite (unlike 8.7/8.8),
-- no dependency on the whisper-selector subsystem (unlike boneyard/waste_camp/
-- long_crossing/dwelling/nursery), and the smallest canvas of the seven
-- unblocked archetypes left (8.4/8.5/8.6/8.9/8.11/8.12/8.13).
--
-- Two walled rooms sharing one interior wall, door-wall facing the road, and
-- an open (unperimetered - "a shop is open") road-side yard: the shop
-- (counter, shelving, stools, a safe on comfortable+) at the front, a back
-- room (one bed, a desk with a ledger, a stove) behind it, reached through an
-- off-centre interior door in their shared wall. Borrows homestead.lua's
-- frame()/shell()/threshold() shape (single-household grammar, door facing
-- params.road_dir the same way homestead reads it - the WORLD SIDE the
-- entry/road sits on, not "which way the road runs" the way dead_caravan.lua
-- reads the same param name) rather than reinventing an orientation helper a
-- third time in this folder.
--
-- params:
--   road_dir   "N"|"E"|"S"|"W" (default "S") - the world side the door (and
--              the road) faces, same convention build_homestead() uses.
--   faction    Jawa_IndigenousTribes | Jawa_Junkers | Jawa_HuttCartel |
--              Jawa_DeepwaterCompact | Jawa_FreeDroidEnclaves |
--              Jawa_WildsteamClan | Empire | TribeCivil | OutlanderCivil |
--              default. Only Jawa/Hutt (the pazaak table), Hutt (gibbet+
--              skullspike), Empire (a road-wall window) and OutlanderCivil
--              (noted, not built - see header note below) get archetype-
--              specific dressing; everything else rides the palette.
--   wealth     destitute|poor|comfortable|rich - gates the threshold width,
--              the safe, and the parked wagon prop (comfortable+ only, spec's
--              own gate).
--   techLevel  Neolithic (default) | Industrial+ - gates the R-POWER apron
--              behind the back room, same has_role(GENERATOR/BATTERY) test
--              build_homestead() uses.
--   sun_dir    world side with no window (tidally-locked dayside wall).
--   state      "lived" (default) | "abandoned" | "ruined" - same convention
--              and same tail code as homestead.lua's build().
--
-- Verified real defNames (RimSage `search_defs` against the indexed 1.6
-- source, never guessed - CLAUDE.md "never guess a defName" / the
-- block_blind_scan hook). Confirmed 2026-09-10: this session's RimSage index
-- is STILL the minimal/prior-load mod set, not the 599-mod ModsConfig.xml
-- currently on disk (the "ModsConfig describes the NEXT load" trap this
-- project's own memory names) - a bare "VFEPD"/"OuterRim_Tatooine"/"KOTOR_"/
-- "LWM_" prefix search returns NOTHING despite all four mods' packageIds
-- being present in the live ModsConfig, and even a bare "Sign"/"Bench"/
-- "Trough"/"Wagon"/"Counter"/"Holobank" search comes back empty. So, same
-- discipline as dead_caravan.lua and cache.lua before it, this template
-- avoids every mod-specific defName the spec names for this archetype and
-- substitutes a verified equivalent, noted here rather than guessed:
--   Table_Counter (VE Props) -> the palette TABLE role (Table1x2c, default
--     tier) used twice: one run along the back wall, one turning onto a side
--     wall - an L by construction, never a straight bar, without inventing
--     an unverified counter defName.
--   OuterRim_Holobank / LWM_Safe -> AncientSafe (ThingDef, "rusted safe") -
--     the exact substitute cache.lua's own header already verified and kept
--     unused; used here for real, behind the counter, comfortable+ only.
--   KOTOR_PazaakTable -> the palette GAME role (HorseshoesPin, default tier)
--     - same "a game the crew plays" read, real def, on Jawa/Hutt roads.
--   ES_ScalesSign / OuterRim_AurebeshWordCargo / any Sign-class def -> NOT
--     built. No ThingDef answering to "Sign" of any kind is indexed in this
--     stack right now (checked broadly, not just the two named ones) - the
--     palette's own default SIGN role (QE_Sign) is equally unresolvable
--     tonight, so using it would trade one guess for another. Omitted as
--     pure dressing, noted rather than silently dropped.
--   VFE_DeskLamp -> the palette LIGHT role near the counter, plus a
--     WALL_LIGHT via wall_lights() - same "the counter has light" read.
--   Seat_Bench (BENCH role's own default) -> NOT indexed either (checked
--     directly) - the palette STOOL role stands in for "a seat under the
--     eave", same substitution pattern as dead_caravan.lua's ChunkSandstone-
--     for-XER_SlabSeat.
--   VFEPD_Wagon / OxCart -> AncientPodCar (Neolithic/Jawa) or
--     AncientRustedTruck (Industrial+) - the SAME substitute dead_caravan.lua
--     already verified and uses for "a wrecked/parked hauler", reused here
--     rather than reinvented, for the spec's own comfortable+ parked wagon.
--   WaterTrough / PrimitiveWell (DBH Lite / Vanilla Furniture) -> NOT built.
--     Neither the palette's own default WATER/TROUGH roles nor any
--     alternative name is indexed in this stack tonight. The hitching strip
--     is Fence + Hay only; the OutlanderCivil "trough outside and free"
--     variant is skipped for the same reason, noted rather than guessed.
--   GibbetCage, Skullspike (Ideology, core) - both real, used directly for
--     the Hutt-road yard-edge dressing.
--   Fence, Hay, AncientCrate, AncientBarrel, AncientWoodenCrate,
--     Filth_Dirt, Filth_ScatteredDocuments, Cloth/Steel/Silver, Grave,
--     Sandbags, Battery, SolarGenerator, PowerConduit, Campfire,
--     ElectricStove, TorchLamp, StandingLamp, WallLamp, Wall, Door, Autodoor,
--     Shelf, Stool, DiningChair, Bed, Bedroll, EndTable, Dresser, PlantPot,
--     Column, ToolCabinet, AncientLockers, AncientSafe, AncientSealedCrate,
--     TileSandstone, FlagstoneSandstone, StrawMatting, Concrete, PavedTile,
--     Gravel (Core/Odyssey/Ancient family, palette defaults) - all found
--     exactly as named or as the palette already resolves them per tech/
--     faction tier.
-- NOT built here (§9/§10 gaps this template does not invent around):
--   OuterRim_AdministratorDesk (Empire desk swap) - the TABLE role stands in;
--   AM_Wall_Atlas_Glass / MUS_SpaceBase_Window (the Empire/Spacer WINDOW
--     tiers) - used via the palette's own WINDOW role exactly as every other
--     template does, so it carries the SAME accepted "reports MISSING until
--     deployed/re-dumped" state homestead.lua's own header already names for
--     RUT_WindowAdobe - not a new problem this template introduces.
--
-- API available: ctx (see luaenv.Ctx), rect, params, rng, role(), note()

-- ---------------------------------------------------------------------------
-- frame: copied from homestead.lua (its own header note: "not in the
-- prelude" - mining_site.lua carries the same private copy already, this is
-- the third, not a new gap).
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

local function try_def(ctx, def, role, x, z, rot)
  rot = rot or 0
  if not ctx:can_place(def, x, z, rot) then return false end
  return ctx:place(def, x, z, rot, nil, role)
end

local function filth(ctx, def, x, z)
  return ctx:place(def, x, z, 0, nil, "FILTH", true)
end

local function clamp(v, lo, hi) return math.max(lo, math.min(hi, v)) end

-- the door cells already in the wall of rect r on `side` (homestead.lua copy)
local function doors_on(ctx, r, side)
  local out = {}
  for _, c in ipairs(wall_cells(r, side)) do
    if ctx:role_at(c[1], c[2]) == "DOOR" then out[#out + 1] = c end
  end
  return out
end

-- FLOOR_THRESHOLD outside an exterior door (homestead.lua copy)
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

-- one wall-slot window on `side` of shell rect r (homestead.lua copy)
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

-- outer (walled) rect of an interior, for the aisle_ok/try_near_walkable guard
local function outer(ir) return R(ir.x - 1, ir.z - 1, ir.w + 2, ir.h + 2) end

-- try_near, under the walkability guard (homestead.lua's near_walkable copy,
-- trimmed - this template's rooms are always walled, so no `sh == nil` branch)
local function near_walkable(ctx, role, x, z, radius, ir, sh)
  return try_near_walkable(ctx, role, x, z, 0, radius, ir, sh)
end

-- along_wall(), but every candidate slot is walkability-guarded
-- (try_near_walkable) before it commits - along_wall() itself only checks
-- blocks_a_door, not aisle_ok, so two independently-unblocked placements
-- (a bed on one wall, a desk on another) can still jointly seal a corner in
-- a small room. Measured: a residual "aisle-blocked" persisted on 3/400 of
-- this pass's own sweep - all on the narrowest rotated shape this template
-- produces (an E/W-facing back room, whose local depth becomes a 3-cell
-- WORLD width) - after every OTHER placement in the room had already been
-- guarded. Trades along_wall()'s jitter/gap niceties for correctness; used
-- only for the two primaries (BED, the desk TABLE) that were still raw.
local function guarded_along_wall(ctx, role, room, sides, shell_rect, opts)
  opts = opts or {}
  for _, side in ipairs(shuffle(sides)) do
    local srot = opts.rot
    if srot == nil then srot = (opts.face == "wall") and SIDE_ROT[side] or opposite(SIDE_ROT[side]) end
    for _, c in ipairs(shuffle(wall_cells(room, side))) do
      if try_near_walkable(ctx, role, c[1], c[2], srot, 0, room, shell_rect) then
        return true, c[1], c[2]
      end
    end
  end
  return false
end

-- R4's density floor: ceil(interior_cells / 6), clamped to 2..8
local function clutter_n(ir, extra)
  return clamp(math.ceil((ir.w * ir.h) / 6) + (extra or 0), 2, 8)
end

-- The cell, then rings around it out to `radius`, in random order, for a raw
-- defName rather than a palette ROLE - tests the REAL can_place gate on every
-- candidate rather than a cheap single-cell occupied() check. Copied from
-- dead_caravan.lua's own header note: a first draft that skipped this and
-- used occupied() alone refused the Debtor's Cache crate on 17/192 sweep
-- cells that only LOOKED free but sat inside another thing's multi-cell
-- footprint. Same fix, same reason, applied here for AncientSafe/
-- AncientWoodenCrate/AncientPodCar/GibbetCage/Skullspike.
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

-- place_near, but for a WALLED room (`shell_rect`) where the candidate's
-- footprint must not seal the door's own flood-fill (aisle_ok, pre-checked
-- BEFORE placing, same guard prelude's try_near_walkable applies to a ROLE).
-- Real bug this pass's own sweep caught: the first draft placed the back
-- room's personal-item box with plain place_near() and it landed, on some
-- seeds, in the ONE interior cell adjacent to the room's only door - in a
-- room this small (7x3 interior) that single cell IS the flood-fill's only
-- seed, so a box sitting on it drops the room to 0% reachable outright
-- (measured: back room aisle proof FAILED at 0% on seed 0's own first run).
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

-- ---------------------------------------------------------------------------
-- reading params once (trimmed homestead.lua read_opts - only what this
-- archetype's own faction dressing actually branches on)
-- ---------------------------------------------------------------------------
local function read_opts(p)
  local o = {}
  o.faction = p.faction or "default"
  o.jawa = (o.faction == "Jawa_IndigenousTribes" or o.faction == "Jawa_Junkers")
  o.hutt = (o.faction == "Jawa_HuttCartel")
  o.league = (o.faction == "OutlanderCivil")
  o.empire = (o.faction == "Empire")
  -- REAL BUG this pass's own sweep caught: this flag was never set at all in
  -- an earlier draft, so the back room's `if o.droid then` branch (below) was
  -- dead code and every Jawa_FreeDroidEnclaves seed silently fell through to
  -- the human-bedroom furnish path instead - placing a desk (fine, TABLE
  -- isn't nulled) but then a clutter list that IS four-for-four nulled for
  -- this faction, tripping R4's no-secondary rule on every single one of
  -- them (21/340 of this pass's own sweep, all Jawa_FreeDroidEnclaves).
  o.droid = (o.faction == "Jawa_FreeDroidEnclaves")
  o.wealth = p.wealth or "modest"
  o.comfortable = (o.wealth == "comfortable" or o.wealth == "rich")
  o.destitute = (o.wealth == "destitute")
  o.tech = p.techLevel or "Neolithic"
  o.industrial = (o.tech == "Industrial" or o.tech == "Spacer" or o.tech == "Ultra" or o.tech == "Archotech")
  o.state = p.state or "lived"
  o.sun = p.sun_dir
  return o
end

function min_rect(params)
  -- road_dir-aware, same convention dead_caravan.lua's own min_rect uses:
  -- for an E/W-facing door the "width across the door wall" runs along
  -- WORLD Z, so the compiler must be told to grant the swapped rect BEFORE
  -- build()'s own W/H transpose reads it back - a fixed (14,12) here handed
  -- the compiler a legally-minimum rect that, after transpose, read as
  -- 12-wide (below the 14 the grammar needs) on every E/W-facing seed and
  -- refused outright (measured: "empty-plan" on 7/40 of this pass's own
  -- sweep, all of them road_dir=E or W).
  local face = (params and params.road_dir) or "S"
  if face == "E" or face == "W" then return 12, 14 end
  return 14, 12
end

function build(ctx)
  local p = params
  local o = read_opts(p)
  local face = p.road_dir or "S"
  if face ~= "N" and face ~= "E" and face ~= "S" and face ~= "W" then face = "S" end
  local W, H = rect.w, rect.h
  if face == "E" or face == "W" then W, H = rect.h, rect.w end
  if W < 14 or H < 12 then
    ctx:refuse("footprint", string.format(
      "%dx%d does not give the trading-post grammar its 14x12 minimum (road_dir=%s)",
      rect.w, rect.h, face))
    return
  end
  local fr = frame(rect.x, rect.z, W, H, face)
  local within = fr.bounds()
  local RW = 9
  local u0 = math.floor((W - RW) / 2)
  local road_side = fr.side("S")

  -- ---- the shop shell: 9 wide x 6 deep (interior 7x4), door on the road --
  local shop_r = fr.rect(u0, 1, RW, 6)
  local shop_i = shell(ctx, "Shop", shop_r, { floor = "FLOOR_WORK", doors = { { road_side } } })
  local dcell = doors_on(ctx, shop_r, road_side)[1]
  if dcell then threshold(ctx, dcell[1], dcell[2], road_side, o.comfortable, within) end

  -- ---- the back room: 9 wide x 5 deep (interior 7x3), sharing the shop's
  -- back wall row - one interior door cut into that shared wall, off-centre,
  -- never in a corner cell or adjacent to one (§3.1.2).
  local back_r = fr.rect(u0, 6, RW, 5)
  local back_i = shell(ctx, "Bedroom", back_r, { floor = "FLOOR" })
  local off = ({ 2, 3, 5, 6 })[rng.int(1, 4)]
  local idx, idz = fr.cell(u0 + off, 6)
  ctx:door(idx, idz)

  -- ---- the counter: an L, never a straight bar - a run along the back
  -- wall, then a second run turning onto whichever side wall has less
  -- shelving pressure (picked below).
  local back_wall = fr.side("N")
  local side_walls = shuffle({ fr.side("E"), fr.side("W") })
  local counter_side, shelf_side = side_walls[1], side_walls[2]
  local counter_n = hug(ctx, "TABLE", shop_i, back_wall, { n = 1, gap = 0 })
  local counter_cells = {}
  for _, lp in ipairs(LAST_PLACED) do counter_cells[#counter_cells + 1] = { lp[1], lp[2] } end
  -- the corner turn is walkability-guarded (near_walkable, from the first
  -- counter cell toward the chosen side wall): a plain along_wall() search
  -- for this second table has no aisle_ok precheck at all, and in a small
  -- (7x4 interior) shop it occasionally landed a table where the ONLY path
  -- from the door to it (or to the first counter table) was already claimed
  -- - measured: "aisle-blocked, 1 primary unreached" on 4/60 of this pass's
  -- own sweep, Empire/poor/Neolithic among them. Guarding this placement the
  -- same way the personal-item CHEST/SAFE placements already are removed it.
  local turned = 0
  if #counter_cells > 0 then
    local c0 = counter_cells[1]
    local lat = (counter_side == "E") and { 1, 0 } or (counter_side == "W") and { -1, 0 }
                or (counter_side == "N") and { 0, 1 } or { 0, -1 }
    local tx, tz = c0[1] + lat[1] * 2, c0[2] + lat[2] * 2
    if near_walkable(ctx, "TABLE", tx, tz, 2, shop_i, outer(shop_i)) then
      turned = 1
      counter_cells[#counter_cells + 1] = { tx, tz }
    end
  end
  counter_n = counter_n + turned

  -- ---- shelving on the OTHER side wall, goods on it via the clutter pass.
  -- Walkability-guarded cell by cell (try_near_walkable, radius 0 - the
  -- search over candidate slots is done here, not inside the primitive):
  -- a plain hug()/along_wall() has no aisle_ok precheck, and stacking 2-3
  -- shelves on top of the counter's own two tables in a 7x4 interior
  -- occasionally sealed off a primary the counter had already placed -
  -- measured: "aisle-blocked, 1 primary unreached" persisted on 11/340 of
  -- this pass's own sweep even after the counter-turn fix above, until this
  -- placement got the same guard.
  local shelf_rot = opposite(SIDE_ROT[shelf_side])
  local shelves = 0
  local shelf_target = rng.int(2, 3)
  for _, c in ipairs(shuffle(wall_cells(shop_i, shelf_side))) do
    if shelves >= shelf_target then break end
    if try_near_walkable(ctx, "STORAGE", c[1], c[2], shelf_rot, 0, shop_i, outer(shop_i)) then
      shelves = shelves + 1
    end
  end

  -- ---- stools on the customer side (the door half of the room)
  local customer_zone = R(shop_i.x, shop_i.z, shop_i.w, math.max(1, math.floor(shop_i.h / 2)))
  local stools = scatter(ctx, "STOOL", customer_zone, 2)

  -- ---- the safe behind the counter, comfortable+ only
  local safe_placed = false
  if o.comfortable and #counter_cells > 0 then
    local c = counter_cells[rng.int(1, #counter_cells)]
    safe_placed = place_near_walkable(ctx, "AncientSafe", c[1], c[2], 2, "CHEST", within, shop_r)
  end

  -- ---- the pazaak-read game table in a corner, Jawa/Hutt roads only, with
  -- two stools drawn up to it
  local game_placed = false
  if (o.jawa or o.hutt) and ctx:has_role("GAME") then
    game_placed = (hug(ctx, "GAME", shop_i, { "N", "E", "S", "W" }, { mode = "corner" }) > 0)
    if game_placed and #LAST_PLACED > 0 then
      local g = LAST_PLACED[#LAST_PLACED]
      near_walkable(ctx, "STOOL", g[1] + 1, g[2], 1, shop_i, outer(shop_i))
      near_walkable(ctx, "STOOL", g[1] - 1, g[2], 1, shop_i, outer(shop_i))
    end
  end

  -- ---- lamp on the counter, plus a wall lamp
  local counter_lamp = false
  if #counter_cells > 0 then
    local c = counter_cells[1]
    counter_lamp = near_walkable(ctx, "LIGHT", c[1], c[2], 1, shop_i, outer(shop_i))
  end
  wall_lights(ctx, shop_i, 1)

  -- ---- windows: one per side wall away from the sun, none on destitute;
  -- Empire additionally cuts one on the road wall itself (spec's own line)
  if not o.destitute then
    for _, s in ipairs({ "E", "W" }) do
      local ws = fr.side(s)
      if ws ~= o.sun then window_on(ctx, shop_r, ws) end
    end
    if o.empire then window_on(ctx, shop_r, road_side) end
  end

  -- ---- dirt tracked in from the door
  local trash_n = 0
  if dcell then
    local into = DIR[opposite(SIDE_ROT[road_side])]
    for i = 1, rng.int(1, 2) do
      local fx, fz = dcell[1] + into[1] * i, dcell[2] + into[2] * i
      if in_rect(fx, fz, shop_i) then filth(ctx, "Filth_Dirt", fx, fz); trash_n = trash_n + 1 end
    end
  end

  -- ---- R4 guarantee: at least one secondary-class role, tried in order,
  -- before the weighted extra pass below. Real bug this pass's own sweep
  -- caught: under Jawa_FreeDroidEnclaves, CRATE/BARREL resolve to
  -- OuterRim_StorageCrate/KOTOR_RhydoniumTank_small (both unverified in this
  -- stack's index - see header) and PLANT_POT/DECOR are nulled outright, so
  -- the shop's clutter() below placed literally nothing for that faction and
  -- tripped no-secondary. SHELF_SMALL is not nulled for any faction in the
  -- roster this template exercises.
  local shop_secondary_ok = false
  do
    local sx0, sz0 = center(shop_i)
    for _, role in ipairs({ "CRATE", "BARREL", "SHELF_SMALL", "DECOR" }) do
      if ctx:has_role(role) and near_walkable(ctx, role, sx0, sz0, 3, shop_i, outer(shop_i)) then
        shop_secondary_ok = true
        break
      end
    end
    if not shop_secondary_ok then ctx:refuse("secondary", "no secondary-class role fitted in the shop (R4)") end
  end

  -- ---- the clutter pass (R4): crates, a barrel, a plant, a little decor
  local shop_clutter = clutter(ctx, shop_i, {
    { role = "CRATE", weight = 3 }, { role = "BARREL", weight = 2 },
    { role = "PLANT_POT", weight = 2 }, { role = "DECOR", weight = 1 },
  }, clutter_n(shop_i, o.comfortable and 1 or 0), outer(shop_i))

  local shop_ok, shop_cov, shop_unreached = aisle_ok(ctx, shop_r)
  if not shop_ok then
    note(string.format("shop aisle proof FAILED: %.0f%% reachable, %d primary unreached", shop_cov * 100, shop_unreached))
  end

  -- ---------------------------------------------------------------------
  -- the back room: one bed, a desk with a ledger, a stove in a corner
  -- ---------------------------------------------------------------------
  local bed_placed, desk_placed, ledger_placed, stove_placed, box_placed = false, false, false, false, false
  if o.droid then
    -- CANON (dwelling.lua/homestead.lua's own droid branch): droids do not
    -- sleep - R-WORK instead. Real bug this pass's own sweep caught: the
    -- human-bedroom clutter list below (END_TABLE/DRESSER/PLANT_POT/STOOL)
    -- is FOUR-FOR-FOUR nulled by the Jawa_FreeDroidEnclaves palette block,
    -- so under that faction clutter() placed zero secondaries against the
    -- desk's one primary and tripped R4's own no-secondary lint rule on
    -- every droid-faction seed. STORAGE/SHELF_SMALL/TOOL_CABINET/WORKBENCH
    -- are NOT nulled for this faction (palette.json), so they carry R4 here.
    along_wall(ctx, "WORKBENCH", back_i, ({ fr.side("N"), fr.side("E"), fr.side("W") })[rng.int(1, 3)], 1, { gap = 1 })
    -- R4 needs a SECONDARY-class role (plan.py's own _SECONDARY_ROLES set),
    -- not just another primary: WORKBENCH and STORAGE are both classed as
    -- primaries there, so hugging a second STORAGE piece does not satisfy
    -- the no-secondary rule. SHELF_SMALL is the one secondary-class role
    -- this faction does not null - guarantee it via a fallback chain (same
    -- shape build_abode()'s own personal-item guarantee uses) rather than
    -- trust a weighted clutter() roll to land it: a first draft relied on
    -- clutter() alone and it dry-rolled TOOL_CABINET (not a secondary-class
    -- role at all) often enough to trip no-secondary on 6/60 of this pass's
    -- own droid-faction sweep seeds.
    local cx, cz = center(back_i)
    local shelved = near_walkable(ctx, "SHELF_SMALL", cx, cz, 3, back_i, outer(back_i))
    if not shelved then ctx:refuse("SHELF_SMALL", "no room for the one guaranteed secondary in the droid workshop back room (R4)") end
    hug(ctx, "STORAGE", back_i, { "N", "E", "W" }, { n = 1, gap = 0 })
    clutter(ctx, back_i, { { role = "SHELF_SMALL", weight = 1 } }, math.max(0, clutter_n(back_i) - 1), outer(back_i))
  else
    local bed_side = ({ fr.side("N"), fr.side("E"), fr.side("W") })[rng.int(1, 3)]
    local bed_ok, bcx, bcz = guarded_along_wall(ctx, "BED", back_i, { bed_side }, outer(back_i), { face = "wall" })
    bed_placed = bed_ok
    local bed_cell = bed_ok and { bcx, bcz } or nil

    -- desk hugs a DIFFERENT wall than the bed (R-OFFICE's own recipe: "hug, 1
    -- off the wall") - a free-centre desk in a 7x3 room was found to box the
    -- door's own sole flood-fill path on some seeds (measured: back room
    -- aisle proof at 38% on the lint tool's own default seed) before this fix
    local desk_sides = {}
    for _, s in ipairs({ fr.side("N"), fr.side("E"), fr.side("W") }) do
      if s ~= bed_side then desk_sides[#desk_sides + 1] = s end
    end
    if #desk_sides == 0 then desk_sides = { fr.side("N") } end
    local desk_ok, dcx, dcz = guarded_along_wall(ctx, "TABLE", back_i, desk_sides, outer(back_i), { gap = 1 })
    desk_placed = desk_ok
    if desk_placed then
      filth(ctx, "Filth_ScatteredDocuments", dcx, dcz)
      ledger_placed = true
    end

    -- corner mode via dress()/hug() has no aisle_ok precheck; in this room's
    -- 7x3 interior a stove landing in the same corner the bed or desk had
    -- already claimed occasionally sealed the OTHER one off - measured:
    -- "aisle-blocked, 1 primary unreached" on 8/360 of this pass's own sweep
    -- (lived and abandoned states both, not only ruined). Guarded the same
    -- way the counter-turn and shelf placements already are.
    for _, c in ipairs(corners(back_i)) do
      if try_near_walkable(ctx, "STOVE", c[1], c[2], 0, 0, back_i, outer(back_i)) then
        stove_placed = true
        break
      end
    end

    -- personal item: a ledger/keepsake box at the bed foot (VFEPD_WoodenChest's
    -- verified substitute, same read as cache.lua's own dugout chest)
    if bed_cell then
      box_placed = place_near_walkable(ctx, "AncientWoodenCrate", bed_cell[1], bed_cell[2], 2, "CHEST", within, back_r)
    end

    clutter(ctx, back_i, {
      { role = "END_TABLE", weight = 3 }, { role = "DRESSER", weight = 2, where = "wall" },
      { role = "PLANT_POT", weight = 2 }, { role = "STOOL", weight = 1 },
    }, clutter_n(back_i), outer(back_i))
  end
  wall_lights(ctx, back_i, 1)

  local back_ok, back_cov, back_unreached = aisle_ok(ctx, back_r)
  if not back_ok then
    note(string.format("back room aisle proof FAILED: %.0f%% reachable, %d primary unreached", back_cov * 100, back_unreached))
  end

  -- ---------------------------------------------------------------------
  -- the yard: hitching strip, crates by the wall, a seat under the eave,
  -- a parked wagon on comfortable+, faction edge dressing. No perimeter -
  -- a shop is open (spec's own line).
  -- ---------------------------------------------------------------------
  local left_margin = u0
  local right_margin = W - u0 - RW
  local hitch_n, hay_placed = 0, false
  if left_margin >= 2 then
    -- a short zigzag, not a ruler line: 3 fence cells with a little jitter
    for i, off2 in ipairs({ { 0, 0 }, { 0, 1 }, { 0, 0 } }) do
      local hx, hz = fr.cell(0, 1 + (i - 1) + off2[2])
      if in_rect(hx, hz, within) and try_place(ctx, "FENCE", hx, hz, 0) then hitch_n = hitch_n + 1 end
    end
    local hyx, hyz = fr.cell(0, 2)
    hay_placed = try_def(ctx, ctx:role("HAY") or "Hay", "HAY", hyx, hyz, 0)
  end

  local yard_r
  if right_margin >= 2 then
    yard_r = fr.rect(u0 + RW, 0, right_margin, H)
  elseif left_margin >= 2 then
    yard_r = fr.rect(0, 0, left_margin, H)
  end
  local crates, barrels = 0, 0
  if yard_r then
    crates = scatter(ctx, "CRATE", yard_r, rng.int(1, 3))
    barrels = scatter(ctx, "BARREL", yard_r, rng.int(0, 1))
  end

  -- a seat under the eave, near the door (Seat_Bench not indexed - STOOL
  -- substitutes, same convention as dead_caravan.lua's ChunkSandstone seat)
  local seat_placed = false
  if dcell then
    local lat = (road_side == "N" or road_side == "S") and { 1, 0 } or { 0, 1 }
    seat_placed = try_near(ctx, "STOOL", dcell[1] + lat[1] * 2, dcell[2] + lat[2] * 2, 0, 2, within)
  end

  -- a parked wagon/wreck, comfortable+ only, kept off the direct path
  local wagon_placed = false
  if o.comfortable and yard_r then
    local wreck_def = o.industrial and "AncientRustedTruck" or "AncientPodCar"
    -- a random cell inside yard_r's own local footprint (the margin strip
    -- beside the shell, whichever side actually has room)
    local wu = (yard_r.x >= u0 + RW) and (u0 + RW + rng.int(0, math.max(0, right_margin - 1)))
                                       or rng.int(0, math.max(0, left_margin - 1))
    local wv = rng.int(3, math.max(3, H - 2))
    local wx, wz = fr.cell(wu, wv)
    local wrot = rng.int(0, 3)
    local ww, wh = rotated_dims(ctx, wreck_def, wrot)
    local wox, woz = origin_for(wx, wz, ww, wh, wrot)
    wox = clamp(wox, rect.x, rect.x2 - ww + 1)
    woz = clamp(woz, rect.z, rect.z2 - wh + 1)
    if ctx:can_place(wreck_def, wox, woz, wrot) then
      ctx:place(wreck_def, wox, woz, wrot, nil, "WRECK")
      wagon_placed = true
    end
  end

  -- Hutt road: a gibbet cage and a skullspike at the yard edge
  local hutt_placed = false
  if o.hutt and yard_r then
    local yc_x, yc_z = center(yard_r)
    local ok1 = place_near(ctx, "GibbetCage", yc_x, yc_z, 3, "DECOR")
    local ok2 = place_near(ctx, "Skullspike", yc_x + 1, yc_z, 3, "DECOR")
    hutt_placed = ok1 or ok2
  end
  if o.league then
    note("OutlanderCivil: spec wants a free trough outside the fence - WaterTrough/PrimitiveWell "
      .. "are not indexed in this stack tonight (checked, not guessed), so it is not built")
  end

  note("trading_post: no perimeter - a shop is open")

  -- ---------------------------------------------------------------------
  -- power apron behind the back room, Industrial+ only (same has_role gate
  -- and cardinal-bus shape build_homestead() uses for its own apron)
  -- ---------------------------------------------------------------------
  -- Placed by can_place-gated ring search (place_near), not a hardcoded
  -- (x,z) pair: a 1x2 Battery's real footprint extends a cell beyond its
  -- origin, and which world axis that extra cell falls on depends on the
  -- frame's face (E/W faces swap which world axis is "along" the frame's own
  -- u). A first draft hardcoded three cells in a row for generator, battery
  -- and the conduit run between them and got a real footprint-collision
  -- between the conduit and the battery on 13/40 of this pass's own sweep
  -- (every Industrial-tech combination) - place_near's can_place check
  -- (same fix dead_caravan.lua's own header names for the Debtor's Cache
  -- crate) makes the collision structurally impossible instead of tuned away.
  local powered = o.industrial and ctx:has_role("GENERATOR") and ctx:has_role("BATTERY") and ctx:has_role("CONDUIT")
  if powered then
    -- REAL BUG this pass's own sweep caught: the battery's search start was
    -- `gcx + 3` - a raw WORLD-x nudge - assuming "further along the pad" is
    -- always +x. That only holds for a S/N-facing frame; for an E/W-facing
    -- one the frame's local u-axis maps onto WORLD Z, so the nudge instead
    -- walked back toward the canvas centre and the battery's radius-4 ring
    -- search occasionally landed INSIDE the back room's own interior,
    -- occupying a cell the (already-guarded) bed/desk search then couldn't
    -- use - measured: "aisle-blocked, 1 primary unreached" (and bed=false)
    -- on 2/450 of this pass's own sweep, both road_dir=E. Using fr.cell()
    -- for the search start keeps the offset in the FRAME's own local terms.
    local gx0, gz0 = fr.cell(u0 + 1, 11)
    local g_ok, gcx, gcz = place_near(ctx, ctx:role("GENERATOR"), gx0, gz0, 2, "GENERATOR")
    if g_ok then
      local bx0, bz0 = fr.cell(u0 + 4, 11)
      local b_ok, bcx, bcz = place_near(ctx, ctx:role("BATTERY"), bx0, bz0, 4, "BATTERY")
      if b_ok then
        local steps = math.max(math.abs(bcx - gcx), math.abs(bcz - gcz))
        for i = 1, steps - 1 do
          local t = i / steps
          local cx = math.floor(gcx + (bcx - gcx) * t + 0.5)
          local cz = math.floor(gcz + (bcz - gcz) * t + 0.5)
          try_place(ctx, "CONDUIT", cx, cz, 0)
        end
        filth(ctx, "Filth_MachineBits", gcx, gcz)
        note("R-POWER: generator+battery pad behind the back room, conduit bus reaching the "
          .. "stove/lamps within ConnectMaxDist 6 through the shared wall")
      end
    end
  end

  note(string.format(
    "trading_post: road_dir=%s counter=%d(turned=%s) shelves=%d stools=%d safe=%s game=%s "
    .. "lamp=%s trash=%d clutter=%d shop_aisle=%.0f%% | bed=%s desk=%s ledger=%s stove=%s box=%s "
    .. "back_aisle=%.0f%% | hitch=%d hay=%s crates=%d barrels=%d seat=%s wagon=%s hutt=%s powered=%s",
    face, counter_n, tostring(turned > 0), shelves, stools, tostring(safe_placed), tostring(game_placed),
    tostring(counter_lamp), trash_n, shop_clutter, shop_cov * 100,
    tostring(bed_placed), tostring(desk_placed), tostring(ledger_placed), tostring(stove_placed), tostring(box_placed),
    back_cov * 100,
    hitch_n, tostring(hay_placed), crates, barrels, tostring(seat_placed), tostring(wagon_placed),
    tostring(hutt_placed), tostring(powered)))

  -- ---- state: dust drifts in when nobody trades here; the ruin pass when
  -- it fell (identical tail to homestead.lua's build())
  if o.state == "abandoned" then
    local n = 0
    for _ = 1, math.max(3, math.floor(rect.w * rect.h / 25)) do
      local x, z = rng.int(rect.x, rect.x2), rng.int(rect.z, rect.z2)
      if not ctx:occupied(x, z) then filth(ctx, rng.chance(0.6) and "Filth_Sand" or "Filth_Dirt", x, z); n = n + 1 end
    end
    note(string.format("abandoned: %d drift(s) of sand and dirt; the layout stands", n))
  elseif o.state == "ruined" then
    ctx:ruin(0.3)
  end
end
