-- beast_lair.lua - "Giant-beast nest/lair" (structure_procedural_spec.md
-- section 8.11). NEW template. Extends krayt_graveyard.lua (the bone-crescent
-- vocabulary reused here for the midden's chunk/skull dressing, not its ring
-- shape - this lair's debris sits in ONE clump, off to a side, not a
-- crescent) and mynock_roost.lua (its chewed-cable pair, PowerConduit +
-- Filth_MachineBits, is the literal `dressing="mynock"` read below). Roster
-- whisper #13 The Egg Sands, #22 The Sarlacc Sign; catalogue F1/F2.
--
-- No walls, no rooms, no roof except natural rock at a cave mouth - a lair,
-- not a building - so prelude's `wall_lights()` (which needs the INTERIOR
-- rect of a walled shell, not the outer footprint) has no shell here to take
-- an interior FROM and is not called; there is no light in this template at
-- all, matching the spec's own "No light" line for 8.11. The canvas is "not
-- a rect in effect" (the spec's own
-- words): CLEAR is a random-walk blob covering ~60% of the footprint, laid
-- down with per-cell `ctx:clear(x,z,1,1,mode)` calls exactly as prelude's own
-- `clear()` docstring prescribes for a non-rectangular clear. These APPEND
-- after the plan's own automatic rectangular CLEAR(soft,+1)/CLEAR(all,exact)
-- (E1, luaenv.run_template - every plan gets those two before a template
-- runs at all), so this pass documents the archetype's own irregular-
-- clearing intent rather than being the only thing standing between the
-- footprint and bare ground - the same relationship mining_site.lua's face
-- cut has to its own CLEAR(all) ("documents the intent; the footprint clear
-- precedes it anyway", that file's own words).
--
-- params:
--   rock_side  world side a rock mass sits on ("N"/"E"/"S"/"W"); unset (the
--              default) is an open-desert nest with no rock kept. When set,
--              a cave-mouth lair: REBUILDS a 3-5 cell ROCK lip at the mouth
--              of that edge and rolls ChunkSandstone x3-5 out of it, one row
--              in. Same E1 gap as mining_site.lua's own face: a template has
--              no way to tell the engine "leave the map's REAL rock here" (a
--              plain CLEAR only records intent for mapgen-time execution,
--              per prelude's own `clear()` docstring - "there is no existing
--              terrain here to destroy" in this offline IR), so the rock is
--              placed back explicitly, same idiom mining_site.lua already
--              uses for its own face. The blob's own clear mode is "soft"
--              when a rock mass is declared (the spec's own words - a
--              cave-mouth lair "keeps its rock lip"), "all" in the open
--              (there is nothing either mode would keep there).
--   edge_dir   which canvas edge the approach path starts from ("N"/"E"/"S"/
--              "W"); unset defaults to the side opposite `rock_side` when
--              that is set (the approach comes from outside, not through the
--              rock), else rolls one of the four at random.
--   read       "nest" (default - the beast is alive, asleep on the bed) |
--              "graveyard" (catalogue F2 - the beast is `skeleton`, no
--              living beast; brood is skipped, the midden runs bigger, "the
--              lair is a bone field").
--   beast_kind PawnKindDef for the beast. Default "Thrumbo" - real, giant,
--              solitary, verified via RimSage (not guessed); see the
--              defName note below for why the spec's own SW-beast options
--              are not the default tonight.
--   pod        number of beasts to spawn instead of one (the spec's own "or
--              a pod x2-4 for wildpods"); unset/1 = the single-sleeper read.
--   brood      forces the Egg-Sands read on (EggSac x2-4 at the bed edge);
--              unset rolls 30% on the `nest` read, never on `graveyard`.
--   dressing   "mynock" (chewed cable in the midden) | "sarlacc" (totem
--              ring - see the defName note on `sw_SarlaccLair` below: the
--              terrain swap itself is not built, only the totems are) |
--              "none"; unset rolls mynock 15% / sarlacc 15% / none 70%.
--   nightside  flavour only tonight - see the GLO_SmallGlowstone note below;
--              no placement follows from this param yet.
--
-- Verified real defNames (RimSage search_defs against tonight's index).
-- 🔴 Tonight's index is the SAME minimal/stale one dead_caravan.lua hit
-- ("ModsConfig describes the NEXT load" - this session's memory): the live
-- ModsConfig.xml carries mlie.starwarsanimalcollection, but NONE of its defs
-- resolve tonight - even KraytDragonSkull/KraytDragonHorn, which
-- krayt_graveyard.lua's OWN header already verified real and shipping, come
-- back empty from search_defs right now. So, exactly like dead_caravan.lua,
-- this file avoids the whole SW-beast-trophy family rather than cite a
-- defName tonight's index cannot see, even where a sibling template already
-- uses it:
--   the spec's `VFEPD_FilthBones`, `DA_GnawedBones`, `RR_DecoBones`,
--   `AB_GallatrossBones` (bone-clump filler) and its four trophy skulls
--   (`KraytDragonSkull`/`RancorSkull`/`MudhornSkull`/`GundarkSkull`) - NONE
--   indexed tonight, and no generic "bones" ThingDef exists at all either
--   (searched "Bone", "Filth_Bones", "Skeleton" - nothing scenery-shaped).
--   The midden is built instead from `ChunkSandstone`/`ChunkGranite`/
--   `Filth_RubbleRock` (already real, already used by mining_site.lua and
--   dead_caravan.lua for exactly this "heaped debris" read) plus `Skull`
--   (ThingDef, confirmed real, label "skull") standing in for BOTH the
--   trophy skull and the spec's own "it eats people too" line - `Skull` is
--   literally named in the spec text for the latter, so no substitution was
--   even needed there.
--   `MA_HarpeagleNest`/`MaggotNest` (the avian/generic nest options; section
--   9's own "no generic large-nest ThingDef exists") - neither indexed; the
--   Egg-Sands read uses `EggSac` only (confirmed real, and the spec's own
--   first-listed option for the insectoid case). The kind-specific
--   "Egg*Fertilized" clutch option is skipped outright - it depends on
--   whichever `beast_kind` a caller rolls, and this template will not guess
--   a per-kind egg defName that varies with an unbounded param.
--   `AncientCratePile`/`VFEPD_AncientCratePile` - not indexed; the spec's
--   OTHER own option, "a crushed AncientCrate", needs no substitution -
--   `AncientWoodenCrate` (confirmed real, used by cache.lua/dead_caravan.lua)
--   plays that "crushed" crate.
--   `sw_SarlaccLair` - not indexed at all (not even a partial "Sarlacc"
--   match resolves), so `dressing="sarlacc"` cannot swap the terrain for it;
--   it keeps only the totem-ring half of that variation (`SculptureSmall`
--   x3-5, confirmed real) and must not be read as the F1 sarlacc itself
--   shipping here.
--   `GLO_SmallGlowstone` - not indexed (`zav.glowstoneforked` is present in
--   ModsConfig but nothing under "glowstone" resolves tonight). The spec
--   itself already hedges this one ("verify... as placeable scatter"), so
--   nightside stays flavour-only rather than inventing a substitute glow.
-- Confirmed real and used as named: `EggSac`, `Skull`, `SculptureSmall`,
-- `PowerConduit`/`Filth_MachineBits` (mynock_roost.lua's own pair),
-- `PackedDirt`/`SoftSand` (TerrainDef), `Hay`, `Filth_AnimalFilth`,
-- `Filth_Blood`, `Filth_MoldyUniform`, `ChunkSlagSteel`, `ChunkSandstone`,
-- `ChunkGranite`, `Filth_RubbleRock`, `Bedroll`, `AncientWoodenCrate`,
-- `Thrumbo`/`AlphaThrumbo` (PawnKindDef).
--
-- API available: ctx (see luaenv.Ctx), rect, params, rng, role(), note()

local OPP_SIDE = { N = "S", S = "N", E = "W", W = "E" }

local function clamp(v, lo, hi) return math.max(lo, math.min(hi, v)) end

local function try_def(ctx, def, role_tag, x, z, rot)
  rot = rot or 0
  if not ctx:can_place(def, x, z, rot) then return false end
  return ctx:place(def, x, z, rot, nil, role_tag)
end

local function filth(ctx, def, x, z)
  return ctx:place(def, x, z, 0, nil, "FILTH", true)
end

-- Ring search on a raw defName (not a palette ROLE, so try_near cannot be
-- used) - same shape as dead_caravan.lua's own place_near, kept local to
-- this file rather than shared because neither template has a home for a
-- shared non-prelude helper module yet. Returns ok, x, z.
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

-- scatter(), but for a raw defName rather than a palette ROLE.
local function scatter_def(ctx, def, r, n, opts)
  opts = opts or {}
  local placed, tries = 0, 0
  local max_tries = opts.tries or n * 20
  while placed < n and tries < max_tries do
    tries = tries + 1
    local x, z = rng.int(r.x, r.x2), rng.int(r.z, r.z2)
    if not ctx:occupied(x, z) and ctx:can_place(def, x, z, 0) then
      ctx:place(def, x, z, 0)
      placed = placed + 1
    end
  end
  return placed
end

-- A clumped scatter of `def` around (x,z): n attempts (capped) inside
-- `within`, each candidate cell jittered by up to `spread` on both axes -
-- the same "random-start clump" shape mining_site.lua's own `clump()` uses
-- for its ore-yard chunk heaps, generalised here to an arbitrary spread
-- instead of that file's fixed -2..2/-1..1 offsets.
local function clump_def(ctx, def, role_tag, x, z, n, spread, within)
  local got = 0
  for _ = 1, n * 4 do
    if got >= n then break end
    local cx2 = clamp(x + rng.int(-spread, spread), within.x, within.x2)
    local cz2 = clamp(z + rng.int(-spread, spread), within.z, within.z2)
    if try_def(ctx, def, role_tag, cx2, cz2, 0) then got = got + 1 end
  end
  return got
end

-- E1: a random-walk blob covering roughly `frac` of `r`'s cells, starting at
-- (cx,cz) and stepping one cardinal cell at a time (clamped to `r`, so a
-- start near an edge does not waste steps walking off it). `exclude` is a
-- set of "x,z" keys (e.g. a rock lip) never to enter. Returns the visited
-- cells in walk order - NOT a disc and not a rect, per the spec's own "not a
-- rect in effect".
local function random_walk_blob(cx, cz, r, frac, exclude)
  exclude = exclude or {}
  local target = math.max(1, math.floor(r.w * r.h * frac))
  local seen, order = {}, {}
  local x, z = cx, cz
  local max_steps = target * 8
  local steps = 0
  while #order < target and steps < max_steps do
    steps = steps + 1
    local k = x .. "," .. z
    if not seen[k] and not exclude[k] then
      seen[k] = true
      order[#order + 1] = { x, z }
    end
    local d = DIR[rng.int(0, 3)]
    x = clamp(x + d[1], r.x, r.x2)
    z = clamp(z + d[2], r.z, r.z2)
  end
  return order
end

-- A jittered path of `terrain`, 1 or 2 wide, from (x0,z0) to (x1,z1),
-- clamped to `r`. Walks in straight-line steps toward the target with a 30%
-- chance per step of a 1-cell lateral nudge - "jittered", not a ruled line,
-- per the spec's own approach-path wording (matching dead_caravan.lua's
-- "never a straight bus"-class house style for anything a beast or a person
-- actually walks). Returns the cells floored.
local function draw_path(ctx, x0, z0, x1, z1, r, terrain, width)
  local cells = {}
  local dx, dz = x1 - x0, z1 - z0
  local steps = math.max(math.abs(dx), math.abs(dz), 1)
  for i = 0, steps do
    local t = i / steps
    local tx = clamp(x0 + math.floor(dx * t + 0.5) + (rng.chance(0.3) and (rng.chance(0.5) and 1 or -1) or 0), r.x, r.x2)
    local tz = clamp(z0 + math.floor(dz * t + 0.5) + (rng.chance(0.3) and (rng.chance(0.5) and 1 or -1) or 0), r.z, r.z2)
    ctx:floor(tx, tz, terrain)
    cells[#cells + 1] = { tx, tz }
    if width >= 2 and rng.chance(0.5) then
      local wx = clamp(tx + (rng.chance(0.5) and 1 or -1), r.x, r.x2)
      ctx:floor(wx, tz, terrain)
    end
  end
  return cells
end

function min_rect(params)
  return 24, 24
end

function build(ctx)
  local p = params
  if rect.w < 24 or rect.h < 24 then
    ctx:refuse("footprint", string.format(
      "%dx%d does not give the lair's random-walk blob a legible ~60%% clearing (24x24 minimum)",
      rect.w, rect.h))
    return
  end

  local rock_side = p.rock_side
  if rock_side ~= "N" and rock_side ~= "E" and rock_side ~= "S" and rock_side ~= "W" then rock_side = nil end
  local edge_dir = p.edge_dir
  if edge_dir ~= "N" and edge_dir ~= "E" and edge_dir ~= "S" and edge_dir ~= "W" then
    edge_dir = rock_side and OPP_SIDE[rock_side] or rng.pick({ "N", "E", "S", "W" })
  end
  local read = (p.read == "graveyard") and "graveyard" or "nest"
  local beast_kind = p.beast_kind or "Thrumbo"
  local pod = tonumber(p.pod) or 1
  local brood = p.brood
  if brood == nil then brood = (read ~= "graveyard") and rng.chance(0.3) or false end
  local dressing = p.dressing
  if dressing ~= "mynock" and dressing ~= "sarlacc" and dressing ~= "none" then
    if p.dressing == nil then
      local roll = rng.int(1, 100)
      dressing = (roll <= 15) and "mynock" or ((roll <= 30) and "sarlacc" or "none")
    else
      dressing = "none"
    end
  end

  local cx, cz = center(rect)

  -- ---- the rock mouth (optional): rebuild a lip, exclude it from the blob -
  local rock_lip = {}
  local rock_n, rock_chunk_n = 0, 0
  if rock_side then
    local rock = ctx:role("ROCK")
    if rock then
      local lip_n = rng.int(3, 5)
      local half_lip = math.floor(lip_n / 2)
      for i = -half_lip, half_lip do
        local lx, lz
        if rock_side == "N" then lx, lz = clamp(cx + i, rect.x, rect.x2), rect.z2
        elseif rock_side == "S" then lx, lz = clamp(cx + i, rect.x, rect.x2), rect.z
        elseif rock_side == "E" then lx, lz = rect.x2, clamp(cz + i, rect.z, rect.z2)
        else lx, lz = rect.x, clamp(cz + i, rect.z, rect.z2) end
        if ctx:place(rock, lx, lz, 0, nil, "ROCK") then
          rock_n = rock_n + 1
          rock_lip[lx .. "," .. lz] = true
        end
      end
      -- chunks rolled out of the lip, 1-2 cells in from it
      local idir = DIR[SIDE_ROT[OPP_SIDE[rock_side]]]
      for _ = 1, rng.int(3, 5) do
        local depth = rng.int(1, 2)
        local cx2, cz2
        if rock_side == "N" or rock_side == "S" then
          cx2 = clamp(cx + rng.int(-half_lip, half_lip), rect.x, rect.x2)
          cz2 = clamp((rock_side == "N" and rect.z2 or rect.z) + idir[2] * depth, rect.z, rect.z2)
        else
          cz2 = clamp(cz + rng.int(-half_lip, half_lip), rect.z, rect.z2)
          cx2 = clamp((rock_side == "E" and rect.x2 or rect.x) + idir[1] * depth, rect.x, rect.x2)
        end
        if try_def(ctx, "ChunkSandstone", "SCRAP", cx2, cz2, 0) then rock_chunk_n = rock_chunk_n + 1 end
      end
    else
      ctx:refuse("ROCK", "rock_side set but this palette has no ROCK role to rebuild the mouth lip")
    end
  end

  -- ---- E1: the random-walk blob clearing, ~60% of the canvas -------------
  -- BEAST_LAIR_SOFT_CLEAR_NO_LIP_1 (found reading this file back, not by a
  -- stress seed - this palette always resolves ROCK, so no seed here can
  -- reach it): this used to key off `rock_side` alone (`rock_side and "soft"
  -- or "all"`), so a palette with no ROCK role - the `ctx:refuse` branch just
  -- above leaves `rock_n == 0` - still told the engine "soft, keep the rock"
  -- for ground that got no rock lip at all. Keying off `rock_n > 0` instead
  -- means the clear mode only ever promises what actually got built.
  local clear_mode = (rock_side and rock_n > 0) and "soft" or "all"
  local blob = random_walk_blob(cx, cz, rect, 0.60, rock_lip)
  for _, c in ipairs(blob) do ctx:clear(c[1], c[2], 1, 1, clear_mode) end

  -- ---- the bed: trampled centre, hay, dense filth, a sand scrape ring ----
  local bed_size = rng.int(3, 5)
  if bed_size % 2 == 0 then bed_size = bed_size + 1 end -- odd so it centres exactly on cx,cz
  local half_bed = math.floor(bed_size / 2)
  local bed_r = R(clamp(cx - half_bed, rect.x, rect.x2 - bed_size + 1),
                   clamp(cz - half_bed, rect.z, rect.z2 - bed_size + 1), bed_size, bed_size)
  local ring_r = R(clamp(bed_r.x - 1, rect.x, rect.x2), clamp(bed_r.z - 1, rect.z, rect.z2),
                    math.min(bed_r.w + 2, rect.w), math.min(bed_r.h + 2, rect.h))
  floor_patch(ctx, ring_r, "SoftSand")
  floor_patch(ctx, bed_r, "PackedDirt")
  local hay_n = scatter_def(ctx, "Hay", bed_r, rng.int(3, 6))
  local filth_n = 0
  for z = bed_r.z, bed_r.z2 do
    for x = bed_r.x, bed_r.x2 do
      if rng.chance(0.55) then filth(ctx, "Filth_AnimalFilth", x, z); filth_n = filth_n + 1 end
    end
  end

  -- ---- eggs on the Egg-Sands read: EggSac x2-4 at the bed edge -----------
  local eggs_n = 0
  if brood then
    local edge_cells = {}
    for x = bed_r.x, bed_r.x2 do
      edge_cells[#edge_cells + 1] = { x, bed_r.z }
      edge_cells[#edge_cells + 1] = { x, bed_r.z2 }
    end
    for z = bed_r.z + 1, bed_r.z2 - 1 do
      edge_cells[#edge_cells + 1] = { bed_r.x, z }
      edge_cells[#edge_cells + 1] = { bed_r.x2, z }
    end
    shuffle(edge_cells)
    local want = rng.int(2, 4)
    for _, c in ipairs(edge_cells) do
      if eggs_n >= want then break end
      if try_def(ctx, "EggSac", "NEST", c[1], c[2], 0) then eggs_n = eggs_n + 1 end
    end
  end

  -- ---- the sarlacc totem ring (dressing only - see defName note above) --
  local totems_n = 0
  if dressing == "sarlacc" then
    local want = rng.int(3, 5)
    local tries = 0
    while totems_n < want and tries < 24 do
      tries = tries + 1
      local a = rng.int(0, 7)
      local ang = a * (math.pi / 4)
      local tr = half_bed + rng.int(2, 4)
      local tx = clamp(cx + math.floor(tr * math.cos(ang) + 0.5), rect.x, rect.x2)
      local tz = clamp(cz + math.floor(tr * math.sin(ang) + 0.5), rect.z, rect.z2)
      if try_def(ctx, "SculptureSmall", "TOTEM", tx, tz, 0) then totems_n = totems_n + 1 end
    end
  end

  -- ---- the midden: 3-6 cells to one side, never centred -------------------
  local midden_dir = rng.pick({ "N", "E", "S", "W" })
  local mdist = rng.int(3, 6)
  local mvec = DIR[SIDE_ROT[midden_dir]]
  local mx = clamp(cx + mvec[1] * mdist, rect.x + 2, rect.x2 - 2)
  local mz = clamp(cz + mvec[2] * mdist, rect.z + 2, rect.z2 - 2)
  local midden_scale = (read == "graveyard") and 1.6 or 1.0
  local sandstone_n = clump_def(ctx, "ChunkSandstone", "BONES", mx, mz, math.floor(rng.int(6, 10) * midden_scale), 2, rect)
  local granite_n = clump_def(ctx, "ChunkGranite", "BONES", mx, mz, math.floor(rng.int(3, 5) * midden_scale), 2, rect)
  local rubble_n = 0
  for _ = 1, math.floor(rng.int(3, 5) * midden_scale) do
    local rx = clamp(mx + rng.int(-2, 2), rect.x, rect.x2)
    local rz = clamp(mz + rng.int(-2, 2), rect.z, rect.z2)
    filth(ctx, "Filth_RubbleRock", rx, rz); rubble_n = rubble_n + 1
  end
  -- one trophy skull off-centre in the clump, one more "it eats people too"
  local trophy_ok = place_near(ctx, "Skull", mx + rng.int(-2, 2), mz + rng.int(-2, 2), 3, "SKULL")
  local victim_ok = place_near(ctx, "Skull", mx + rng.int(-2, 2), mz + rng.int(-2, 2), 3, "SKULL")
  local crate_ok = place_near(ctx, "AncientWoodenCrate", mx, mz, 3, "CRATE")
  -- mynock/cable read: chewed conduit stubs and machine bits in the midden
  local conduit_n, bits_n = 0, 0
  if dressing == "mynock" then
    for _ = 1, rng.int(2, 4) do
      local px = clamp(mx + rng.int(-3, 3), rect.x, rect.x2)
      local pz = clamp(mz + rng.int(-3, 3), rect.z, rect.z2)
      if try_def(ctx, "PowerConduit", "CONDUIT", px, pz, 0) then conduit_n = conduit_n + 1 end
    end
    for _ = 1, rng.int(2, 4) do
      local bx2 = clamp(mx + rng.int(-3, 3), rect.x, rect.x2)
      local bz2 = clamp(mz + rng.int(-3, 3), rect.z, rect.z2)
      filth(ctx, "Filth_MachineBits", bx2, bz2); bits_n = bits_n + 1
    end
  end

  -- ---- the approach: a jittered path from edge_dir to the bed ------------
  local ex, ez
  if edge_dir == "N" then ex, ez = clamp(cx + rng.int(-3, 3), rect.x, rect.x2), rect.z2
  elseif edge_dir == "S" then ex, ez = clamp(cx + rng.int(-3, 3), rect.x, rect.x2), rect.z
  elseif edge_dir == "E" then ex, ez = rect.x2, clamp(cz + rng.int(-3, 3), rect.z, rect.z2)
  else ex, ez = rect.x, clamp(cz + rng.int(-3, 3), rect.z, rect.z2) end
  local path_cells = draw_path(ctx, ex, ez, cx, cz, rect, "PackedDirt", rng.chance(0.5) and 2 or 1)
  local blood_n = 0
  for _ = 1, rng.int(2, 3) do
    local c = path_cells[rng.int(1, #path_cells)]
    filth(ctx, "Filth_Blood", c[1], c[2]); blood_n = blood_n + 1
  end
  local slag_n = 0
  for _ = 1, rng.int(1, 2) do
    if place_near(ctx, "ChunkSlagSteel", ex, ez, 3, "SCRAP") then slag_n = slag_n + 1 end
  end
  local bedroll_ok, brx, brz = place_near(ctx, "Bedroll", ex, ez, 3, "BEDROLL")
  if bedroll_ok then filth(ctx, "Filth_MoldyUniform", brx, brz) end

  -- ---- E3: the beast. Mandatory - "a lair without the beast is a bone
  -- yard" (spec's own words). `graveyard` read spawns it dead instead of
  -- skipping it, so the mandate holds either way. -------------------------
  local beast_state = (read == "graveyard") and "skeleton" or "alive"
  local beast_n = 0
  if pod >= 2 then
    for _ = 1, pod do
      local bx = clamp(cx + rng.jitter(1), rect.x, rect.x2)
      local bz = clamp(cz + rng.jitter(1), rect.z, rect.z2)
      if ctx:pawn(beast_kind, bx, bz, "wild", beast_state) then beast_n = beast_n + 1 end
    end
  else
    if ctx:pawn(beast_kind, cx, cz, "wild", beast_state) then beast_n = 1 end
  end

  note(string.format(
    "beast_lair: read=%s beast=%s(state=%s)x%d rock_side=%s(lip=%d,chunks=%d) edge_dir=%s "
    .. "blob=%d/%d cells bed=%dx%d(hay=%d,filth=%d,scrape) brood=%s(eggs=%d) "
    .. "dressing=%s(totems=%d,conduits=%d,bits=%d) midden@%s,%s(sandstone=%d,granite=%d,rubble=%d,"
    .. "trophy=%s,victim=%s,crate=%s) path(cells=%d,blood=%d,slag=%d,bedroll=%s)",
    read, beast_kind, beast_state, beast_n, tostring(rock_side), rock_n, rock_chunk_n, edge_dir,
    #blob, rect.w * rect.h, bed_r.w, bed_r.h, hay_n, filth_n, tostring(brood), eggs_n,
    dressing, totems_n, conduit_n, bits_n, mx, mz, sandstone_n, granite_n, rubble_n,
    tostring(trophy_ok), tostring(victim_ok), tostring(crate_ok),
    #path_cells, blood_n, slag_n, tostring(bedroll_ok)))
end
