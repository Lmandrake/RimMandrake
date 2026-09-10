-- cache.lua - "Storage cache" (structure_procedural_spec.md sec 8.14, the
-- SMALLEST template in the roster, its own words). Roster whispers #8 "The
-- Debtor's Cache" and #1 "Something Buried" are the ones that cite this
-- shape by name; both ride this one template rather than getting their own.
--
-- Three forms, per the spec's own list, rolled by rng.pick unless pinned:
-- (a) buried - a hidden crate under a sand patch, marked by a stone.
-- (b) dugout - a tiny walled-and-roofed room holding the goods.
-- (c) cairn  - a heap of rock over a chest, a skull on Tusken country.
-- `params.form` pins one ("buried"|"dugout"|"cairn"); unset rolls.
-- `params.debtor` (or an unforced 25% roll when unset) layers the spec's
-- "Debtor variant" on top of whichever base form was picked - a second,
-- smaller chest plus the scattered ledger page - the spec files it as an
-- ADDITION, not a fourth form, and this keeps it that way.
--
-- Verified real defNames this pass (RimSage `search_defs` against the
-- indexed 1.6 source, not guessed - CLAUDE.md "never guess a defName" /
-- the block_blind_scan hook). The live def-dump capture
-- (2026-09-10T00-28-43Z) was UNREADABLE tonight - a casualty of the same
-- crash that took the game down for this whole pass, per this item's own
-- brief - so `rimplace verify`'s usual dump cross-check could not run;
-- RimSage stood in as CHARTER's own first-listed instrument instead of
-- blocking on a live capture that does not exist right now:
--   AncientHermeticCrate (ThingDef, "hermetic crate"),
--   AncientSealedCrate (ThingDef, "sealed crate") - the spec's own two
--     named buried-cache containers, both real.
--   AncientWoodenCrate (ThingDef, "old wooden crate") - SUBSTITUTE for the
--     spec's `VFEPD_WoodenChest`/`VFEPD_WoodenChestLarge`: search_defs has
--     no "Wooden"-prefixed ThingDef under VFEPD at all in this stack's
--     index. Same read (a wooden storage container), a real def.
--   AncientSafe (ThingDef, "rusted safe") - available but NOT used below;
--     kept here as the verified substitute for the spec's `LWM_Safe`
--     (the LWM mod is not indexed) if a future pass wants the (a) buried
--     form to roll a safe instead of a crate.
--   ChunkSandstone, SculptureSmall, Skull, TorchLamp, Filth_Sand,
--     Filth_Dirt, Filth_ScatteredDocuments (Core) - all found exactly as
--     named.
--   FlagstoneSandstone (TerrainDef, "sandstone flagstone") - the dugout's
--     floor. R2 ("never Gravel, even here") applies to a 3x3 hole same as
--     anything bigger.
-- NOT built here: `ASF_StoragePit`/`ASF_CellarStone` (no "ASF"-prefixed
-- def of any kind is indexed - that mod is not in this stack) and
-- `QE_TreasureChest`/`CanisterA` (no def under either name is indexed).
-- All three are dressing swaps, not load-bearing mechanism, so the
-- substitutes above cost the read nothing structural. The spec's own
-- "Torment Master" tent caveat does not apply - this template cites none
-- of those defNames.
--
-- API available: ctx (see luaenv.Ctx), rect, params, rng, role(), note()

local function filth(ctx, def, x, z)
  return ctx:place(def, x, z, 0, nil, "FILTH", true)
end

function min_rect(params)
  return 5, 5
end

function build(ctx)
  local MIN = 5
  if rect.w < MIN or rect.h < MIN then
    ctx:refuse("footprint", string.format(
      "%dx%d cannot hold the %dx%d cache", rect.w, rect.h, MIN, MIN))
    return
  end

  -- Centered in whatever canvas was actually granted (5x5 floor, 7x7
  -- production per the spec) rather than fixed at the corner - a cache is
  -- found IN a patch of ground, not pinned to one edge of it.
  local cx = rect.x + math.floor(rect.w / 2)
  local cz = rect.z + math.floor(rect.h / 2)

  local form = params.form
  if form ~= "buried" and form ~= "dugout" and form ~= "cairn" then
    form = rng.pick({ "buried", "dugout", "cairn" })
  end

  local debtor = params.debtor
  if debtor == nil then
    debtor = rng.chance(0.25)
  end

  local report = { form = form, debtor = debtor }

  if form == "buried" then
    -- ---- (a) buried: CLEAR, a SoftSand patch, one crate off-centre in it,
    -- a marker stone 1-2 cells off on a random side, sand filth nearby.
    local half = math.min(2, math.floor(math.min(rect.w, rect.h) / 2))
    ctx:clear(cx - half, cz - half, half * 2 + 1, half * 2 + 1, "soft")
    ctx:floor_rect(cx - 1, cz - 1, 3, 3, "SoftSand")

    local jx = cx + (rng.chance(0.5) and 1 or -1)
    local jz = cz + (rng.chance(0.5) and 1 or -1)
    local crate = rng.chance(0.5) and "AncientHermeticCrate" or "AncientSealedCrate"
    if ctx:can_place(crate, jx, jz) then
      ctx:place(crate, jx, jz)
      report.crate = crate
    else
      ctx:refuse(crate, "no room for the buried crate in the sand patch")
    end

    local mdir = rng.pick({ { 1, 0 }, { -1, 0 }, { 0, 1 }, { 0, -1 } })
    local mstep = rng.int(1, 2)
    local mx = jx + mdir[1] * mstep
    local mz = jz + mdir[2] * mstep
    if ctx:can_place("SculptureSmall", mx, mz) then
      ctx:place("SculptureSmall", mx, mz, 0, "Sandstone")
      report.marker = true
    end

    for _, off in ipairs({ { 1, 1 }, { -1, -1 } }) do
      local sx, sz = cx + off[1], cz + off[2]
      if ctx:in_bounds(sx, sz) and not ctx:occupied(sx, sz) then
        filth(ctx, "Filth_Sand", sx, sz)
      end
    end

  elseif form == "dugout" then
    -- ---- (b) dugout: a 3x3 walled, roofed, floored hole. Door on the lee
    -- side (params.sun_dir when the caller sets it - the dayside wall is
    -- blind per every other template's convention; otherwise a random side).
    local W, H = 3, 3
    local x = cx - 1
    local z = cz - 1
    ctx:room("Storeroom", x, z, W, H, true)
    ctx:wall_rect(x, z, W, H)
    -- R2: never Gravel even in a 3x3 hole - override the palette default.
    ctx:floor_rect(x + 1, z + 1, 1, 1, "FlagstoneSandstone")

    local lee_side
    if params.sun_dir then
      lee_side = params.sun_dir -- door faces AWAY from the sun -> on the sun_dir wall
    else
      lee_side = rng.pick({ "N", "S", "E", "W" })
    end
    local dx, dz
    if lee_side == "N" then dx, dz = cx, z
    elseif lee_side == "S" then dx, dz = cx, z + H - 1
    elseif lee_side == "E" then dx, dz = x + W - 1, cz
    else dx, dz = x, cz end
    ctx:door(dx, dz)

    local chest = rng.chance(0.5) and "AncientWoodenCrate" or "AncientSealedCrate"
    if ctx:can_place(chest, cx, cz) then
      ctx:place(chest, cx, cz)
      report.chest = chest
    end
    -- CanisterA has no verified equivalent in this stack (see header) -
    -- dressing omitted rather than guessed; Filth_Dirt still sells "lived in".
    filth(ctx, "Filth_Dirt", x + 1, z + 1)
    -- "a TorchLamp unlit = TorchLamp - it has no lit state to place" (spec,
    -- verbatim): placed plain, same as dead_beacon.lua's cold beacon.
    local tx, tz = (lee_side == "E") and x or x + W - 1, (lee_side == "N" or lee_side == "S") and z + H - 1 or cz
    if ctx:can_place("TorchLamp", tx, tz) then
      ctx:place("TorchLamp", tx, tz)
      report.torch = true
    end

  else -- cairn
    -- ---- (c) cairn: ChunkSandstone heaped over a chest, a skull on top
    -- on Tusken country (params.faction == "Tusken").
    local n_chunks = rng.int(5, 7)
    local placed_chunks = 0
    ctx:clear(cx - 2, cz - 2, 5, 5, "soft")
    if ctx:can_place("AncientWoodenCrate", cx, cz) then
      ctx:place("AncientWoodenCrate", cx, cz)
      report.chest = "AncientWoodenCrate"
    end
    local offsets = {
      { 0, -1 }, { 0, 1 }, { -1, 0 }, { 1, 0 },
      { 1, 1 }, { -1, -1 }, { 1, -1 }, { -1, 1 },
    }
    for i = 1, n_chunks do
      local off = offsets[((i - 1) % #offsets) + 1]
      local bx = cx + off[1] * rng.int(1, 2)
      local bz = cz + off[2] * rng.int(1, 2)
      if ctx:in_bounds(bx, bz) and ctx:can_place("ChunkSandstone", bx, bz) then
        ctx:place("ChunkSandstone", bx, bz)
        placed_chunks = placed_chunks + 1
      end
    end
    report.chunks = placed_chunks
    if params.faction == "Tusken" then
      local sx, sz = cx, cz - 1
      if ctx:in_bounds(sx, sz) and ctx:can_place("Skull", sx, sz) then
        ctx:place("Skull", sx, sz)
        report.skull = true
      end
    end
  end

  if debtor then
    -- ---- the Debtor's Cache addition: a second, smaller sealed crate plus
    -- the ledger page, wherever there is room adjacent to the base form.
    -- Tries every cardinal side at 2 cells then 3 before giving up - a
    -- single fixed roll (the first draft) refused on over half the seeds
    -- at BOTH the 5x5 min canvas and the 7x7 production one, on a cairn's
    -- dense chunk fill: a real generator bug the pilot's own sweep caught,
    -- not a legitimate "sometimes there's no room" case.
    local dirs = { { 1, 0 }, { -1, 0 }, { 0, 1 }, { 0, -1 } }
    -- shuffle (Fisher-Yates, seeded rng) so the search order isn't the same
    -- side every time when more than one candidate fits.
    for i = #dirs, 2, -1 do
      local j = rng.int(1, i)
      dirs[i], dirs[j] = dirs[j], dirs[i]
    end
    local placed_debtor = false
    for _, dist in ipairs({ 2, 3 }) do
      for _, d in ipairs(dirs) do
        local ddx, ddz = cx + d[1] * dist, cz + d[2] * dist
        if ctx:in_bounds(ddx, ddz) and ctx:can_place("AncientSealedCrate", ddx, ddz) then
          ctx:place("AncientSealedCrate", ddx, ddz)
          filth(ctx, "Filth_ScatteredDocuments", ddx, ddz)
          report.debtor_crate = true
          placed_debtor = true
          break
        end
      end
      if placed_debtor then break end
    end
    if not placed_debtor then
      ctx:refuse("AncientSealedCrate", "no room for the debtor's second crate beside the cache")
    end
  end

  note(string.format(
    "cache: form=%s%s crate=%s%s%s",
    report.form,
    report.debtor and " +debtor" or "",
    report.crate or report.chest or "none",
    report.chunks and string.format(" chunks=%d", report.chunks) or "",
    report.skull and " +skull" or ""))
end
