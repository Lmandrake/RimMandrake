-- dead_caravan.lua - "Broken wagon / dead caravan" (structure_procedural_spec.md
-- sec 8.10). NEW template - the 5th of the 14 sec-8 archetypes built under
-- INHABITED_AUGMENTATION_BUILD_1 (after 8.1 homestead, 8.2 moisture farm,
-- 8.3 mining site, 8.14 cache). Catalogue C1 (crashed hauler); roster whisper
-- #16 "The Prospector's Bones" is the one-body variant but rides
-- mining_site.lua's own skeleton, not this file; whisper #8 "The Debtor's
-- Cache" can ride along here as the optional debtor addition below, same
-- shape as cache.lua's own (this file is not wired to either whisper - see
-- header note on the whisper subsystem not existing yet, same as cache.lua).
--
-- No walls, no rooms - an open-ground debris field a caravan reaches on
-- foot, same footing as podracer_wreck.lua. Grammar, along params.road_dir
-- (u = along the road, v = lateral to it): the wreck (turned sideways across
-- the road - "slewed") -> a spill cone ahead of it, densest at the wreck ->
-- the camp off to one lateral side -> the aftermath: a grave row XOR bodies
-- (never both, spec's own words), an optional ambush dressing, and the dead
-- pack animal still in the wreck's traces.
--
-- params:
--   road_dir   "N"|"E"|"S"|"W" (default "E") - which way the road runs; the
--              canvas's long axis lies along it (min_rect swaps accordingly)
--   sun_dir    if set, the camp sits on the shaded (lateral-opposite) side,
--              same convention dwelling.lua/homestead.lua use for a porch;
--              unset rolls a random lateral side
--   techLevel  Neolithic (default, the Jawa wagon/speeder read) | Industrial+
--              (a dead truck instead)
--   outcome    "buried" (Grave x1-3) | "wiped" (E3 skeleton/dessicated x2-4)
--              - unset rolls 50/50; the spec is explicit these never both fire
--   ambush     forces the improvised-barricade/blast-mark dressing on; unset
--              rolls 30% (the spec names the dressing, not its odds)
--   debtor     forces the Debtor's Cache addition on; unset rolls 25%, the
--              same convention cache.lua's own debtor variant uses
--
-- Verified real defNames (RimSage search_defs against the indexed 1.6
-- source - CLAUDE.md "never guess a defName" / block_blind_scan). Tonight's
-- RimSage index is the ACTIVE (minimal) mod list, not the campaign's full
-- one: search_defs returns nothing at all for ANY "VFEPD_"- or "BreadMoAM_"-
-- prefixed def right now, including several other templates in this same
-- folder cite (mining_site.lua's VFEPD_AncientRockMiningCar etc.) - see this
-- session's "ModsConfig describes the NEXT load" memory. So this template
-- avoids that whole family rather than cite a defName tonight's index
-- cannot actually see:
--   AncientPodCar (ThingDef, "ancient pod car") - the spec's own
--     `VFEPD_Wagon`/`VFEPD_OxCart` are not indexed at all tonight (nor is
--     any other "Wagon"/"Cart"-named ThingDef besides AncientShoppingCart,
--     which is a comedy prop, not a hauler). AncientPodCar is the SAME
--     substitute podracer_wreck.lua already uses for a Jawa "wrecked
--     landspeeder" read (this project's own PodCarIsLandspeeder.xml patch
--     reskins Core's AncientPodCar for exactly that) - reused, not
--     reinvented, and it is exactly the "broken thing abandoned on the
--     road" silhouette this archetype wants.
--   AncientRustedTruck, AncientIndustrialTruck (ThingDef) - the spec's own
--     Industrial-tier wreck options, both real, both already used by
--     mining_site.lua's apron cart.
--   AncientWoodenCrate, AncientMetalCrate, AncientLargeCrate,
--     AncientLongCrate, AncientBarrel, AncientSmallCrate (ThingDef) - real
--     substitutes for the spec's `CrateA-C`/`BundleA-C`/`BarrelA`/
--     `MetalCrateA`/`ASF_WovenBasket` (a bare "Crate"/"Bundle"/"Barrel"
--     search turns up only the Ancient-crate family and Core's
--     AncientBarrel/FermentingBarrel - none of the spec's own suffixed
--     names exist tonight) and for "2 open" (`VFEPD_AncientCrate` ->
--     `AncientSmallCrate`, which already IS the open-crate def, used
--     directly, no substitution needed there).
--   Muffalo, Dromedary (PawnKindDef) - substitutes for the spec's
--     "Bantha-class from the SW collection" pack animal (no "Bantha"-named
--     kind is indexed tonight - that SW collection is not in the active
--     list). Either reads as "a dead pack animal in the traces" without the
--     SW-specific flavour. Tribal_Trader (PawnKindDef, label "trader") -
--     the caravan owner's own remains, same E3 pattern as mining_site.lua's
--     "Miner" skeleton (a kind used for its READ, not its faction).
--   Filth_Trash, Filth_Sand, Filth_Ash, Filth_Blood, Filth_BlastMark,
--     Filth_MoldyUniform, Filth_ScatteredDocuments, Steel, Silver, Cloth,
--     Hay, Bedroll, Grave, SandbagRubble, ChunkSandstone, Campfire,
--     WaterTrough (Core) - all found exactly as named.
-- NOT built here: `XER_SlabSeat` (not indexed) - the spec's own fallback,
-- "a ChunkSandstone as a seat", is used instead, so no substitution was
-- even needed. `BanthaHorn`, `ASF_StorageTent`/`CAMakeshiftTentWall` (none
-- indexed, and the spec itself flags the tent defs as unverified - "verify
-- CA tent defs render standalone") - omitted as pure dressing, same as
-- cache.lua's CanisterA omission.
--
-- API available: ctx (see luaenv.Ctx), rect, params, rng, role(), note()

local function try_def(ctx, def, role_tag, x, z, rot)
  rot = rot or 0
  if not ctx:can_place(def, x, z, rot) then return false end
  return ctx:place(def, x, z, rot, nil, role_tag)
end

local function filth(ctx, def, x, z)
  return ctx:place(def, x, z, 0, nil, "FILTH", true)
end

local function clamp(v, lo, hi) return math.max(lo, math.min(hi, v)) end

-- world (x,z) for canvas-local (u,v): u runs ALONG the road in the direction
-- of travel implied by road_dir, v runs LATERAL to it. This is a different
-- axis convention from mining_site.lua's frame() (tuned around a single
-- "front wall" a building faces) - a wreck has no front wall, only a
-- direction of travel, so u/v map straight onto the rect with a swap+flip
-- per direction instead of a four-way rotation.
local function road_frame(r, road_dir)
  local fr = {}
  if road_dir == "E" then
    function fr.cell(u, v) return r.x + u, r.z + v end
  elseif road_dir == "W" then
    function fr.cell(u, v) return r.x2 - u, r.z + v end
  elseif road_dir == "N" then
    function fr.cell(u, v) return r.x + v, r.z + u end
  else -- "S"
    function fr.cell(u, v) return r.x + v, r.z2 - u end
  end
  return fr
end

-- The cell, then rings around it out to `radius`, in random order, exactly
-- like prelude's try_near - but for a raw defName rather than a palette ROLE
-- (Bedroll/Hay/the crate family are not roles), so it cannot go through
-- try_place. Tests the REAL can_place gate on every candidate rather than
-- the plan's cheap `occupied()` flag (BuildPlan.occupied only checks a
-- thing's ORIGIN cell, not its whole footprint - core.py's own docstring on
-- `place()` names this exact trap, TEMPLATE_FOOTPRINT_IGNORES_SIZE_1). A
-- first draft of this template used `occupied()` alone to call a cell
-- "free", found ONE such cell, and handed it straight to try_def with no
-- fallback - so any candidate that merely LOOKED free but sat inside
-- another thing's multi-cell footprint (the wreck, a crate) failed
-- can_place and the whole placement was refused outright. Measured: 17/192
-- sweep cells refused the Debtor's Cache crate this way even with a
-- radius-8 fallback, because a bigger radius just found MORE falsely-free
-- cells, never a genuinely placeable one. Placing on the first can_place
-- success, ring by ring, fixes it the same way try_near already does for
-- roles. Returns ok, x, z.
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

-- scatter(), but for a raw defName rather than a role.
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

function min_rect(params)
  local rd = (params and params.road_dir) or "E"
  if rd == "N" or rd == "S" then return 12, 16 end
  return 16, 12
end

function build(ctx)
  local p = params
  local road_dir = p.road_dir or "E"
  if road_dir ~= "N" and road_dir ~= "E" and road_dir ~= "S" and road_dir ~= "W" then
    road_dir = "E"
  end
  local vertical = (road_dir == "N" or road_dir == "S")
  local along, lateral
  if vertical then along, lateral = rect.h, rect.w else along, lateral = rect.w, rect.h end
  if along < 16 or lateral < 12 then
    ctx:refuse("footprint", string.format(
      "%dx%d does not give the dead-caravan grammar its 16-long x 12-lateral minimum (road_dir=%s)",
      rect.w, rect.h, road_dir))
    return
  end

  local tech = p.techLevel or "Neolithic"
  local industrial = (tech == "Industrial" or tech == "Spacer" or tech == "Ultra" or tech == "Archotech")
  local fr = road_frame(rect, road_dir)
  local U_MAX, V_MAX = along - 1, lateral - 1
  local center_v = math.floor(lateral / 2)

  -- ---- the wreck: slewed sideways across the road, near the front third --
  local wreck_def
  if industrial then
    wreck_def = rng.pick({ "AncientRustedTruck", "AncientIndustrialTruck" })
  else
    wreck_def = "AncientPodCar"
  end
  local wreck_u = rng.int(2, math.max(2, math.floor(along * 0.25)))
  local wreck_v = clamp(center_v + rng.int(-1, 1), 0, V_MAX)
  local wx, wz = fr.cell(wreck_u, wreck_v)
  -- "rotated 1 off the road axis" - turned 90 from whatever axis road_dir
  -- itself points along, so the wreck sits crosswise, not neatly parked.
  local ROAD_ROT = { E = 0, W = 0, N = 1, S = 1 }
  local wreck_rot = (ROAD_ROT[road_dir] + 1) % 4
  local ww, wh = rotated_dims(ctx, wreck_def, wreck_rot)
  local wox, woz = origin_for(wx, wz, ww, wh, wreck_rot)
  -- origin_for's even-size rotation shift can push the origin past whichever
  -- edge road_frame anchored on ("S"/"W" anchor at r.z2/r.x2, so a small u -
  -- near the front of the canvas - sits close to that far edge already);
  -- clamp back inside the rect rather than let a shifted origin refuse a
  -- placement the footprint would otherwise clear.
  wox = clamp(wox, rect.x, rect.x2 - ww + 1)
  woz = clamp(woz, rect.z, rect.z2 - wh + 1)
  local wreck_placed = false
  if ctx:can_place(wreck_def, wox, woz, wreck_rot) then
    ctx:place(wreck_def, wox, woz, wreck_rot, nil, "WRECK")
    wreck_placed = true
  else
    ctx:refuse(wreck_def, "the wreck's own footprint did not fit the rolled wreck cell")
  end

  -- a second cart 4-7 cells behind it on 40% (spec)
  local second_cart = false
  if rng.chance(0.4) then
    local cart_u = clamp(wreck_u - rng.int(4, 7), 0, U_MAX)
    local cx2, cz2 = fr.cell(cart_u, clamp(wreck_v + rng.int(-1, 1), 0, V_MAX))
    local cox, coz = origin_for(cx2, cz2, ww, wh, wreck_rot)
    cox = clamp(cox, rect.x, rect.x2 - ww + 1)
    coz = clamp(coz, rect.z, rect.z2 - wh + 1)
    if ctx:can_place(wreck_def, cox, coz, wreck_rot) then
      ctx:place(wreck_def, cox, coz, wreck_rot, nil, "WRECK")
      second_cart = true
    end
  end

  -- ---- the dead pack animal, 1-2 cells ahead, still in the traces --------
  local pack_kind = rng.pick({ "Muffalo", "Dromedary" })
  local pax, paz = fr.cell(clamp(wreck_u + rng.int(1, 2), 0, U_MAX), wreck_v)
  ctx:pawn(pack_kind, pax, paz, "wild", "dessicated")

  -- ---- the spill cone: ahead of the wreck, densest close to it -----------
  local crate_pool = { "AncientWoodenCrate", "AncientMetalCrate", "AncientLargeCrate", "AncientLongCrate", "AncientBarrel" }
  local cone_len = math.max(3, math.min(U_MAX - wreck_u, math.floor(along * 0.5)))
  local cone_cells = {}
  for vv = -2, 2 do
    for uu = 1, cone_len do
      cone_cells[#cone_cells + 1] = { uu, vv }
    end
  end
  shuffle(cone_cells)
  local placed_crates, opened, sand_n, trash_n = 0, 0, 0, 0
  local crate_spots = {}
  for _, off in ipairs(cone_cells) do
    local cu = wreck_u + off[1]
    if cu <= U_MAX then
      local cv = clamp(wreck_v + off[2], 0, V_MAX)
      local dist = off[1] + math.abs(off[2])
      local chance = math.max(0.08, 0.55 - dist * 0.06)
      if rng.chance(chance) then
        local sx, sz = fr.cell(cu, cv)
        local def
        if opened < 2 then def = "AncientSmallCrate"; opened = opened + 1
        else def = rng.pick(crate_pool) end
        if try_def(ctx, def, "CRATE", sx, sz, 0) then
          placed_crates = placed_crates + 1
          crate_spots[#crate_spots + 1] = { sx, sz }
          if dist >= 4 then filth(ctx, "Filth_Sand", sx, sz); sand_n = sand_n + 1 end
        end
      end
    end
  end
  -- Filth_Trash tracked from the wreck itself, closest to it
  for _ = 1, 3 do
    local tu = clamp(wreck_u + rng.int(0, 2), 0, U_MAX)
    local tv = clamp(wreck_v + rng.int(-1, 1), 0, V_MAX)
    local tx, tz = fr.cell(tu, tv)
    if ctx:in_bounds(tx, tz) then filth(ctx, "Filth_Trash", tx, tz); trash_n = trash_n + 1 end
  end
  -- one stack of an actual trade good, in a free cell near the spill
  local good = rng.pick({ "Cloth", "Steel", "Silver" })
  local good_placed, gx, gz = false, nil, nil
  if #crate_spots > 0 then
    local near = crate_spots[rng.int(1, #crate_spots)]
    good_placed, gx, gz = place_near(ctx, good, near[1], near[2], 2, "GOODS")
  end
  if not good_placed then good_placed, gx, gz = place_near(ctx, good, wx, wz, 3, "GOODS") end

  -- ---- the Debtor's Cache addition: a second, smaller crate under "the
  -- wagon bed", plus the ledger page (same shape as cache.lua's own) -------
  local debtor = p.debtor
  if debtor == nil then debtor = rng.chance(0.25) end
  local debtor_placed = false
  if debtor then
    -- search BEHIND the wreck first (opposite the spill cone, which already
    -- claims most cells ahead), then widen from the wreck's own centre - a
    -- wreck rolled close to u=0 has nothing behind it to find either.
    local bx0, bz0 = fr.cell(clamp(wreck_u - 2, 0, U_MAX), wreck_v)
    local ok, dx, dz = place_near(ctx, "AncientWoodenCrate", bx0, bz0, 3, "CHEST")
    if not ok then ok, dx, dz = place_near(ctx, "AncientWoodenCrate", wx, wz, 8, "CHEST") end
    if ok then
      filth(ctx, "Filth_ScatteredDocuments", dx, dz)
      debtor_placed = true
    else
      ctx:refuse("AncientWoodenCrate", "no room for the debtor's crate under the wagon bed")
    end
  end

  -- ---- the camp: off to one lateral side, on the shaded side if sun_dir -
  local lee_sign
  if p.sun_dir then
    if vertical then
      lee_sign = (p.sun_dir == "E") and -1 or (p.sun_dir == "W") and 1 or (rng.chance(0.5) and 1 or -1)
    else
      lee_sign = (p.sun_dir == "N") and -1 or (p.sun_dir == "S") and 1 or (rng.chance(0.5) and 1 or -1)
    end
  else
    lee_sign = rng.chance(0.5) and 1 or -1
  end
  local camp_u = clamp(wreck_u + rng.int(math.max(3, math.floor(along * 0.3)), math.max(4, along - 4)), 0, U_MAX)
  local camp_v = clamp(center_v + lee_sign * rng.int(3, math.max(3, math.floor(lateral * 0.4))), 0, V_MAX)
  local kx, kz = fr.cell(camp_u, camp_v)
  local camp_r = R(kx - 2, kz - 2, 5, 5)

  local fire_placed = try_def(ctx, "Campfire", "STOVE", kx, kz, 0)
  local ash_n = 0
  for _, off in ipairs({ { 1, 0 }, { -1, 0 }, { 0, 1 }, { 0, -1 } }) do
    local ax, az = kx + off[1], kz + off[2]
    if ctx:in_bounds(ax, az) then filth(ctx, "Filth_Ash", ax, az); ash_n = ash_n + 1 end
  end
  local beds = scatter_def(ctx, "Bedroll", camp_r, rng.int(2, 4), { rot = "any" })
  local seat_placed = place_near(ctx, "ChunkSandstone", kx, kz, 3, "SEAT")
  local trough_placed = place_near(ctx, "WaterTrough", kx + 2, kz, 3, "TROUGH")
  local hay_placed = place_near(ctx, "Hay", kx - 2, kz, 3, "HAY")

  -- ---- the aftermath: a grave row XOR bodies, never both -----------------
  -- GRAVE and BARRICADE are palette ROLES (unlike the raw defNames above),
  -- so prelude's own try_near does the same can_place-gated ring search
  -- place_near does, without reimplementing it here.
  local outcome = p.outcome
  if outcome ~= "buried" and outcome ~= "wiped" then
    outcome = rng.chance(0.5) and "buried" or "wiped"
  end
  local graves, bodies = 0, 0
  if outcome == "buried" then
    for _ = 1, rng.int(1, 3) do
      local ok = try_near(ctx, "GRAVE", kx + rng.int(-3, 3), kz + rng.int(-3, 3), rng.int(0, 3), 3, R(rect.x, rect.z, rect.w, rect.h))
      if ok then graves = graves + 1 end
    end
  else
    -- a corpse has no footprint to collide with (ctx:pawn spawns it wherever
    -- asked, no can_place gate) - just keep it inside the canvas.
    local state = rng.pick({ "skeleton", "dessicated" })
    for _ = 1, rng.int(2, 4) do
      local bx = clamp(kx + rng.int(-3, 3), rect.x, rect.x2)
      local bz = clamp(kz + rng.int(-3, 3), rect.z, rect.z2)
      ctx:pawn("Tribal_Trader", bx, bz, "wild", state)
      bodies = bodies + 1
    end
  end
  -- old blood, an overlay filth that never needs a free cell. Kept 1 cell
  -- off the absolute rect edge: an overlay still refuses if ANY of its own
  -- (unmeasured-safe, but not guaranteed 1x1) footprint cells fall outside
  -- the rect, which a bare edge clamp can trip (measured: Filth_BlastMark
  -- did exactly this on 20/192 sweep cells before this margin was added).
  for _ = 1, rng.int(2, 3) do
    local bx2 = clamp(wx + rng.int(-3, 3), rect.x + 1, rect.x2 - 1)
    local bz2 = clamp(wz + rng.int(-3, 3), rect.z + 1, rect.z2 - 1)
    filth(ctx, "Filth_Blood", bx2, bz2)
  end

  -- ---- optional ambush dressing: improvised barricades, a blast mark -----
  local ambush = p.ambush
  if ambush == nil then ambush = rng.chance(0.3) end
  local barricades, blast_n = 0, 0
  if ambush then
    for _ = 1, 2 do
      if try_near(ctx, "BARRICADE", wx, wz, rng.int(0, 3), 3, R(rect.x, rect.z, rect.w, rect.h)) then
        barricades = barricades + 1
      end
    end
    for _ = 1, rng.int(1, 2) do
      local mx = clamp(wx + rng.int(-3, 3), rect.x + 1, rect.x2 - 1)
      local mz = clamp(wz + rng.int(-3, 3), rect.z + 1, rect.z2 - 1)
      filth(ctx, "Filth_BlastMark", mx, mz); blast_n = blast_n + 1
    end
    place_near(ctx, "SandbagRubble", wx, wz, 3, "SANDBAG")
  end

  note(string.format(
    "dead_caravan: road_dir=%s wreck=%s(%s)%s pack=%s crates=%d(opened=%d,sand=%d) trash=%d "
    .. "goods=%s(%s) debtor=%s camp[fire=%s ash=%d beds=%d seat=%s trough=%s hay=%s] "
    .. "outcome=%s(graves=%d,bodies=%d) ambush=%s(barricades=%d,blast=%d)",
    road_dir, wreck_def, wreck_placed and "ok" or "REFUSED", second_cart and " +2nd" or "",
    pack_kind, placed_crates, opened, sand_n, trash_n,
    tostring(good_placed), good, tostring(debtor_placed and debtor or false),
    tostring(fire_placed), ash_n, beds, tostring(seat_placed), tostring(trough_placed), tostring(hay_placed),
    outcome, graves, bodies, tostring(ambush), barricades, blast_n))
end
