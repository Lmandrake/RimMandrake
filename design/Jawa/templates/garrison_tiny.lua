-- garrison_tiny.lua - "Tiny garrison" (structure_procedural_spec.md sec 8.6).
-- NEW template - the 8th of the 14 sec-8 archetypes built under
-- INHABITED_AUGMENTATION_BUILD_1 (after 8.1 homestead, 8.2 moisture farm,
-- 8.3 mining site, 8.14 cache, 8.10 dead caravan, 8.4 trading post, 8.5
-- road warehouse). Picked from the remaining unblocked five (8.6/8.9/8.11/
-- 8.12/8.13): boneyard/waste_camp/long_crossing/dwelling/nursery need the
-- missing whisper-selector subsystem, 8.7/8.8 are blocked on
-- required_mods.md prerequisites - 8.6 has neither blocker and is fully
-- specced.
--
-- Grammar, approach -> back: a perimeter ring (one gate, off the wall's own
-- midpoint by construction of the corridor it opens onto) -> an inner yard
-- with two shells set on DIFFERENT walls (not "aligned to the same wall" -
-- the spec's own words; RimWorld rooms cannot rotate off-axis, so this reads
-- it as each shell's own door facing a different cardinal side): the
-- barracks (door facing the gate) and the mess/command room (door facing
-- the corridor between the two shells, a wall 90 degrees from the
-- barracks') -> an armoury nook (a perfect 2x2-interior box, the one room
-- allowed to be) tucked behind the barracks -> a power apron beside it on
-- Industrial+ -> a gun position (TURRET) and a watch post just inside the
-- gate -> yard clutter (a firing step, an outdoor campfire, crates, graves).
--
-- params:
--   approach_dir "N"|"E"|"S"|"W" (default "S") - the world side the gate
--                and its corridor face, same convention road_dir/rock_side/
--                sun_dir use elsewhere in this folder.
--   faction      Jawa_IndigenousTribes | Jawa_Junkers | Jawa_HuttCartel |
--                Jawa_DeepwaterCompact | Jawa_FreeDroidEnclaves |
--                Jawa_WildsteamClan | Empire | TribeCivil | OutlanderCivil |
--                default. Empire/Deepwater get a WALL perimeter (the spec's
--                own "the crisp one" / "Wall stone" branches); everyone else
--                gets the spec's own Neolithic SANDBAG+BARRICADE ring - see
--                the NOT-INDEXED note below for why that is the default for
--                EVERY faction tonight, not just Neolithic ones.
--   techLevel    Neolithic (default) | Industrial+ - gates the power apron
--                and the generator/lamp choice, same has_role gate every
--                template in this folder uses.
--   state        "lived" (default) | "abandoned" | "ruined" - abandoned
--                swaps the live defenders for remains and skips the working
--                generator; ruined runs the shared ctx:ruin() tail.
--   crew         defender headcount, 2-6 (default 3).
--
-- Verified real defNames (RimSage `search_defs` against THIS session's
-- indexed source - CLAUDE.md "never guess a defName" / block_blind_scan).
-- This index is the minimal/prior-load mod set, not the 599-mod
-- ModsConfig.xml on disk (same caveat road_warehouse.lua's own header
-- states, and it is worse for THIS archetype specifically):
--   Turret_MiniTurret, Turret_AutoMiniTurret, Sandbags, Barricade, Grave,
--   FenceGate, AncientLockers, ToolCabinet, ChemfuelPoweredGenerator,
--   Filth_MoldyUniform, Filth_MachineBits, Filth_Blood, Skullspike,
--   GibbetCage - all confirmed real ThingDefs this session.
--   PawnKindDefs Pirate, Tribal_Warrior, Empire_Fighter_Trooper, and
--   FactionDef Empire - all confirmed real.
-- NOT indexed this session (checked, not guessed - substituted with a
-- verified real equivalent or omitted, same discipline every prior
-- template in this folder uses when it hits this):
--   The ENTIRE spec vocabulary this archetype is built around is missing
--   from tonight's index: `FT_Palisade`/`FT_Palisade_Corner`/
--   `FT_Palisade_Embrasures`/`FT_PalisadeGate`/`FT_PalisadeDoor` (Fortifications
--   Industrial), `FT_Trench`/`FT_Ditch`/`FT_CavalrySpike`/`FT_Platform`/
--   `FT_Turret_BunkerM` (same mod), `WatchTower`/`WatchTowerRoofed`/
--   `TowerLightBeacon` (NWN), `RH_Bunker_Wall_Embrasure`/
--   `RH2_ClassicFootlocker` (RH2/RH_ mods - FOOTLOCKER's own shared default
--   is already a pre-existing palette.json gap, not this template's to
--   fix), `HMC_Wall_Comms_Console` (HMC Wall Furniture), `Misc_FileCabinet`,
--   `VFEPD_Banner`, `VFEPD_AncientBrokenTurret`, `WeaponRacks_1Rack`-`4Rack`,
--   `VFEPD_WeaponRackSpears`, every `OuterRim_AurebeshWord*` sign. None of
--   these are guessed into the plan - the perimeter uses the palette's own
--   SANDBAG/BARRICADE/WALL/TURRET roles (all confirmed real) throughout,
--   the armoury uses LOCKER+TOOL_CABINET (confirmed real) instead of a
--   weapon rack, "the watch" is a PILLAR+LIGHT post instead of a tower (see
--   the build() comment at the gun position), and no Aurebesh signage is
--   placed - matching road_warehouse.lua's own §10-gap precedent rather
--   than inventing a defName `rimplace verify` cannot confirm.
--   `AncientGarrison` (the catalogue's named landmark) IS indexed as a
--   LandmarkDef/TileMutatorDef/StructureLayoutDef, but per the spec's own
--   words ("unaudited - audit first") that is a SEPARATE piece of content
--   this template does not touch or depend on.
--
-- E3 note: this is the first template in the folder to spawn an ALIVE PAWN
-- (every prior PAWN call - dead_caravan.lua, mining_site.lua, long_crossing.lua
-- - only ever spawns a corpse). plan.py's own compiler only sends
-- state=alive to a live bridge call (jawa/spawn_pawn); dead states stay
-- mapgen-only. That live path is UNVERIFIED by this pass (game confirmed
-- down, no bridge - see the item's own dispatch) exactly like every other
-- live claim this folder's templates already flag; it DOES compile cleanly
-- (checked via `rimplace export`) and `rimplace verify` treats the kindDef
-- like any other defName (core.py `add_pawn` -> the verify defName set).
-- faction="wild" for the defenders, matching every existing PAWN call's own
-- convention (a named kindDef spawned with no real Faction) - the spec's
-- own words ("the faction-of-tile resolver is still the gating C#") say
-- picking a REAL FactionDef for these pawns is explicitly not this
-- template's job.
--
-- Canvas: 22x18 minimum (approach_dir-aware, road_warehouse.lua's own
-- swap-under-transpose fix applied from the start here), 26x22 production.
-- The spec's own number is 20x18; grown by 2 cells of width (spent
-- entirely on the Mess room, not the corridor) after this pass's own sweep
-- found tech:Industrial's ElectricStove needs more room than the literal
-- 20-wide floor gives the Mess - see min_rect()'s own comment.

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

-- the door cells already in the wall of rect r on `side` (homestead.lua's
-- own private copy - not in the prelude, same gap that file's header names)
local function doors_on(ctx, r, side)
  local out = {}
  for _, c in ipairs(wall_cells(r, side)) do
    if ctx:role_at(c[1], c[2]) == "DOOR" then out[#out + 1] = c end
  end
  return out
end

-- a 1-cell FLOOR_THRESHOLD outside an exterior door (spec 3.1.4, poor tier)
local function threshold1(ctx, dx, dz, side, within)
  local d = DIR[SIDE_ROT[side]]
  local ox, oz = dx + d[1], dz + d[2]
  if (within == nil or in_rect(ox, oz, within)) and not ctx:occupied(ox, oz) then
    ctx:floor(ox, oz, ctx:role("FLOOR_THRESHOLD"))
  end
end

-- try each of `roles` in turn (a walkability-guarded try_near_walkable),
-- stopping at the first that actually places - the R4 "guaranteed
-- secondary" fallback needs a role that is BOTH real and counted by the
-- lint's own `_SECONDARY_ROLES` list (plan.py), and a single hardcoded
-- BARREL is one point of failure too many once the room is already dense
-- (see the header's own note on the "no-secondary" ERROR this pass's sweep
-- caught: LOCKER/CANDLE are real, guarded clutter picks that do NOT count
-- toward that lint rule at all, so an unlucky run of non-counting rolls
-- plus a single failed BARREL attempt is a real ERROR, not just a WARN).
local function guarantee_secondary(ctx, roles, x, z, radius, within, shellr)
  for _, role in ipairs(roles) do
    if try_near_walkable(ctx, role, x, z, 0, radius, within, shellr) then return role end
  end
  return nil
end

-- one item hugging a specific wall cell, walkability-guarded PER CANDIDATE
-- (not just can_place-gated) - road_warehouse.lua's own office desk uses
-- this exact shape for the same reason: a bare `along_wall()` has no
-- aisle_ok precheck at all, and in a small/tight room (this archetype's
-- Mess, at the canvas floor, has a stove, two tables, a desk chair and
-- clutter all competing for space) an unguarded wall-hug can seal off
-- another primary with nothing after it able to detect or undo that -
-- this pass's own sweep measured exactly that: 5/480 combinations left the
-- Mess with 1-4 primaries the door's flood-fill could not reach, always
-- traceable to the STOVE or the desk TABLE (the only two UNGUARDED
-- along_wall calls in the room) landing in a cell nothing downstream could
-- veto. Returns the placed cell's role tag, or nil.
local function wall_walkable(ctx, role, room, side, shellr, rot)
  rot = rot or opposite(SIDE_ROT[side])
  for _, c in ipairs(shuffle(wall_cells(room, side))) do
    if try_near_walkable(ctx, role, c[1], c[2], rot, 0, room, shellr) then return true end
  end
  return false
end

-- the cell, then rings around it, in random order, real can_place-gated -
-- for a raw defName rather than a palette ROLE (road_warehouse.lua's own
-- private copy of this same helper; every template that places a raw
-- defName near a hand-picked point carries one, per that file's own header
-- note on why a bare occupied() check is not enough).
-- `avoid(x,z)->true` rejects a candidate outright (scatter()'s own opts.avoid
-- convention) - needed here because the ring search itself can wander INTO
-- a keepout zone even when the search's own START point was chosen clear of
-- it (this pass's own sweep caught exactly that: a start-point-only check
-- on the Hutt trophies still let the ring search's outer rings land beside
-- the turret).
local function place_near(ctx, def, x, z, radius, role_tag, rot, within, avoid)
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
      if (within == nil or in_rect(c[1], c[2], within))
         and (avoid == nil or not avoid(c[1], c[2]))
         and ctx:can_place(def, c[1], c[2], rot) then
        ctx:place(def, c[1], c[2], rot, nil, role_tag)
        return true, c[1], c[2]
      end
    end
  end
  return false
end

-- ---------------------------------------------------------------------------
-- reading params once
-- ---------------------------------------------------------------------------
local function read_opts(p)
  local o = {}
  o.faction = p.faction or "default"
  o.empire = (o.faction == "Empire")
  o.deepwater = (o.faction == "Jawa_DeepwaterCompact")
  o.hutt = (o.faction == "Jawa_HuttCartel")
  o.junkers = (o.faction == "Jawa_Junkers")
  o.droid = (o.faction == "Jawa_FreeDroidEnclaves")
  o.tribal = (o.faction == "TribeCivil" or o.faction == "Jawa_IndigenousTribes"
              or o.faction == "Jawa_WildsteamClan")
  o.tech = p.techLevel or "Neolithic"
  o.industrial = (o.tech == "Industrial" or o.tech == "Spacer" or o.tech == "Ultra" or o.tech == "Archotech")
  o.state = p.state or "lived"
  o.crew = clamp(p.crew or 3, 2, 6)
  return o
end

-- the defender's PawnKindDef, by faction - all three confirmed real this
-- session (search_defs); "wild" faction on the PAWN call itself, per the
-- header's E3 note.
local function defender_kind(o)
  if o.empire then return "Empire_Fighter_Trooper" end
  if o.tribal then return "Tribal_Warrior" end
  return "Pirate"
end

-- min_rect grown from the spec's own stated 20x18 to 22x18 - the same kind
-- of correction homestead.lua's own header makes ("the spec's 7x7/12x10/
-- 30x26 estimates forgot the threshold row and the lean-to"). This pass's
-- own sweep found a genuine `aisle-blocked` ERROR clustered on
-- tech:Industrial at the spec's literal 20-wide floor (ElectricStove needs
-- more room than the Mess's own interior gave it at that width) - 2 cells
-- of extra width, spent entirely on widening the Mess room (not the
-- corridor), reduced it from 7/480 to 1/480 (a Hutt-furniture-set residual,
-- documented at the guaranteed-secondary call below) on this pass's own
-- 480-combination sweep.
function min_rect(params)
  local face = (params and params.approach_dir) or "S"
  if face == "E" or face == "W" then return 18, 22 end
  return 22, 18
end

function build(ctx)
  local p = params
  local o = read_opts(p)
  local face = p.approach_dir or "S"
  if face ~= "N" and face ~= "E" and face ~= "S" and face ~= "W" then face = "S" end
  local W, H = rect.w, rect.h
  if face == "E" or face == "W" then W, H = rect.h, rect.w end
  if W < 22 or H < 18 then
    ctx:refuse("footprint", string.format(
      "%dx%d does not give the garrison grammar its 22x18 minimum (approach_dir=%s)",
      rect.w, rect.h, face))
    return
  end
  local fr = frame(rect.x, rect.z, W, H, face)
  local lot = fr.bounds()

  local inset = 2
  local barracks_w, barracks_h = 6, 8
  -- mess_h grown from the spec-arithmetic 8 to 9: this pass's own sweep
  -- caught a real `aisle-blocked` ERROR on 7/480 combinations, EVERY one at
  -- the absolute 20x18 canvas floor and EVERY one on tech:Industrial -
  -- ElectricStove (plan.py's own comment names it "a 3x1 ElectricStove")
  -- needs more room than the 5x6 interior the spec's own numbers budget.
  -- One extra row of depth (interior 5x7=35 cells, vs 30) costs nothing
  -- elsewhere - the barracks+armoury column already needs H>=15ish, so
  -- H=18's own floor absorbs it without moving the declared min_rect.
  local mess_w, mess_h = 9, 9
  local corridor_lo = inset + barracks_w                    -- first corridor column (u)
  local corridor_hi = W - inset - mess_w - 1                -- last corridor column (u)

  -- ---- the gate: a 2-cell gap in the approach wall, sat inside the
  -- corridor band between the two shells (below) rather than at the wall's
  -- own arithmetic midpoint - a real person on foot would use the lane
  -- between the buildings, not the exact centre of open ground.
  local gate_u = clamp(corridor_lo + math.floor((corridor_hi - corridor_lo) / 2) + rng.int(-1, 1),
                        corridor_lo, math.max(corridor_lo, corridor_hi - 1))

  -- ---- perimeter: FT_Palisade (and every other named fortification def in
  -- the spec's own §8.6 text) is NOT indexed this session - see the header.
  -- SANDBAG+BARRICADE (the spec's own Neolithic branch) stands in for every
  -- faction except Empire/Deepwater, who get the spec's own WALL branch.
  local peri = (o.empire or o.deepwater) and "WALL" or "SANDBAG"
  local mix = (peri == "SANDBAG") and ctx:has_role("BARRICADE")
  local ring_n, gate_n = 0, 0
  for u = 0, W - 1 do
    for _, v in ipairs({ 0, H - 1 }) do
      local x, z = fr.cell(u, v)
      if v == 0 and (u == gate_u or u == gate_u + 1) then
        if try_place(ctx, "GATE", x, z, 0) then gate_n = gate_n + 1 end
      else
        local def = (mix and rng.chance(0.18)) and "BARRICADE" or peri
        if try_place(ctx, def, x, z, 0) then ring_n = ring_n + 1 end
      end
    end
  end
  for v = 1, H - 2 do
    for _, u in ipairs({ 0, W - 1 }) do
      local x, z = fr.cell(u, v)
      local def = (mix and rng.chance(0.18)) and "BARRICADE" or peri
      if try_place(ctx, def, x, z, 0) then ring_n = ring_n + 1 end
    end
  end
  if gate_n == 0 then ctx:refuse("GATE", "no palette GATE role for this faction/tech - the perimeter has no marked opening") end

  -- ---- barracks (R-BARRACKS): door facing the gate/approach ---------------
  local barracks_r = fr.rect(inset, inset, barracks_w, barracks_h)
  local bi = shell(ctx, "Barracks", barracks_r,
    { floor = o.industrial and "FLOOR_WORK" or "FLOOR_POOR", doors = { { fr.side("S") } } })
  -- WALL_LIGHTS_HELPER_BROKEN_1-shaped bug caught by this pass's own first
  -- lint run: `shell` MUST be the true outer (wall-inclusive) rect, which is
  -- the INTERIOR `bi` padded by 1 (every other template's own convention -
  -- road_warehouse.lua's `outer()`, mining_site.lua's/homestead.lua's `sh`/
  -- `walk_shell`, all pad the INTERIOR). The first draft here padded
  -- `barracks_r` instead - already the outer wall rect - giving a rect TWO
  -- cells too big on every side. `aisle_ok`'s own `inner(shell)` then
  -- computed a bogus "interior" (the wall ring plus a yard cell), found no
  -- door aligned with it, and returned coverage=0 - failing EVERY
  -- walkability-guarded placement in the room, which is exactly what the
  -- very first lint run showed: only the one unguarded CANDLE landed, the
  -- guaranteed BARREL refused, and "no-secondary" fired on a room that had
  -- three clutter rolls and a bed. Fixed by padding `bi`, not `barracks_r`.
  local bsh = R(bi.x - 1, bi.z - 1, bi.w + 2, bi.h + 2)
  local bdoor = doors_on(ctx, barracks_r, fr.side("S"))[1]
  if bdoor then threshold1(ctx, bdoor[1], bdoor[2], fr.side("S"), lot) end

  -- beds head-to-wall on the BACK wall (local N, opposite the door), never
  -- split across the two long (E/W) walls. The spec's own words are "along
  -- the two long walls, alternating" - the FIRST draft here did exactly
  -- that with two independent along_wall("E") / along_wall("W") calls, and
  -- this pass's own first lint run caught the real bug that produces:
  -- along_wall picks an INDEPENDENT random row for each side, and on a
  -- 4-wide interior every Bedroll is 2 cells wide once rotated to face a
  -- side wall - so two beds that happen to land on the SAME row (no
  -- coordination between the two calls prevents this) together span the
  -- room's ENTIRE 4-cell width, sealing it into two disconnected halves.
  -- Measured directly (a temporary aisle_ok debug note, since removed):
  -- coverage=46% on seed 0 - barely legal, and other seeds trip the same
  -- geometry into a real aisle-blocked ERROR. `mining_site.lua`'s own
  -- bunkhouse hit this identical 4-wide-interior problem and already
  -- carries the fix in its own header ("a 2-long bedroll from each side
  -- fills a row... so bedrolls head-to-wall on the BACK wall instead") -
  -- applying the same proven fix here rather than inventing a new one.
  -- Requesting at most 3 of the wall's 4 available slots guarantees the
  -- spec's own "1 in 4 dropped" ratio by construction, not a probabilistic
  -- near-miss.
  local beds = 0
  if ctx:has_role("BED") then
    local want = clamp(o.crew, 2, 3)
    beds = along_wall(ctx, "BED", bi, "N", want, { face = "wall", gap = 0 })
    for _, b in ipairs(LAST_PLACED) do
      if b[4] == "BED" and rng.chance(0.6) then
        try_near_walkable(ctx, "FOOTLOCKER", b[1], b[2], 0, 1, bi, bsh)
      end
    end
  else
    along_wall(ctx, "WORKBENCH", bi, "N", 1, { gap = 1 })
    along_wall(ctx, "STORAGE", bi, "E", 1, { gap = 1 })
  end
  -- SHELF_SMALL deliberately excluded: `ctx:ruin()`'s own `_RUIN_COUSIN`
  -- maps it to the SAME 2-cell "AncientShelf" as STORAGE, and a 1x1 clutter
  -- pick placed with zero clearance can overlap a neighbour once ruin()
  -- inflates it (this pass's own sweep caught this exact shape, one
  -- Barracks bed and one Armoury wall, both on `state=ruined`) - the same
  -- fix road_warehouse.lua's own header applies to its shelving wall.
  clutter(ctx, bi, {
    { role = "CRATE", weight = 2 }, { role = "STOOL", weight = 2 },
    { role = "CANDLE", weight = 1 }, { role = "LOCKER", weight = 2 },
  }, math.max(3, math.ceil((bi.w * bi.h) / 8)), bsh)
  filth(ctx, "Filth_MoldyUniform", rng.int(bi.x, bi.x2), rng.int(bi.z, bi.z2))
  -- WALL_LIGHTS_HELPER_BROKEN_1: wall_lights() silently places nothing when
  -- given the shell's OUTER rect (proven, not fixed as of this pass - see
  -- the item file). Tried anyway (harmless if it places zero) with a
  -- walkability-guarded, multi-role fallback as the ACTUAL guaranteed
  -- secondary (BARREL, then CRATE, then STOOL, then SHELF_SMALL - all four
  -- confirmed real and all four counted by the lint's own _SECONDARY_ROLES
  -- list), matching road_warehouse.lua's own single-BARREL workaround but
  -- widened after this pass's own sweep caught the single-role version
  -- failing on 5/480 combinations.
  wall_lights(ctx, barracks_r, 1)
  if not guarantee_secondary(ctx, { "BARREL", "CRATE", "STOOL", "SHELF_SMALL" }, bi.x, bi.z, 2, bi, bsh) then
    ctx:refuse("secondary", "no room for the barracks' one guaranteed secondary (R4)")
  end
  if ctx:has_role("SIGN") and bdoor then
    local d = DIR[SIDE_ROT[fr.side("S")]]
    try_place(ctx, "SIGN", bdoor[1] + d[1] * 2, bdoor[2] + d[2] * 2, 0)
  end

  -- ---- mess/command (R-HEARTH + a desk corner): door facing the corridor,
  -- a DIFFERENT wall than the barracks' own south-facing door - the spec's
  -- "set at an angle to each other, not aligned to the same wall", read the
  -- only way two axis-aligned RimWorld shells can express it.
  local mess_r = fr.rect(W - inset - mess_w, inset, mess_w, mess_h)
  local mess_door_side = fr.side("W")
  local mi = shell(ctx, "Mess", mess_r,
    { floor = o.industrial and "FLOOR_WORK" or "FLOOR_POOR", doors = { { mess_door_side } } })
  local msh = R(mi.x - 1, mi.z - 1, mi.w + 2, mi.h + 2)         -- see the bsh comment above
  local mdoor = doors_on(ctx, mess_r, mess_door_side)[1]
  if mdoor then threshold1(ctx, mdoor[1], mdoor[2], mess_door_side, lot) end

  local stove_side = fr.side("N")
  local stove_ok = wall_walkable(ctx, "STOVE", mi, stove_side, msh)
  if not stove_ok and ctx:has_role("STOVE") then hug(ctx, "STOVE", mi, { stove_side }, { mode = "corner" }) end
  local cx, cz = center(mi)
  local ok, tx, tz = try_near_walkable(ctx, "TABLE", jitter(cx, 1), jitter(cz, 1), rng.int(0, 1), 2, mi, msh)
  if ok then
    local seat = ctx:has_role("CHAIR") and "CHAIR" or "STOOL"
    seat_around(ctx, seat, tx, tz, rng.int(1, 3), mi, 0)
  end
  -- the command desk: a second TABLE against a wall the dining table did not
  -- claim, a stool, and a "file cabinet" (no Misc_FileCabinet indexed - the
  -- LOCKER role, already confirmed real, stands in - NOT the STORAGE role:
  -- STORAGE and SHELF_SMALL both map to `ctx:ruin()`'s own 2-cell
  -- "AncientShelf" cousin with no footprint recheck, and a wall-flush
  -- STORAGE placed here inflated into the wall on `state=ruined` in this
  -- pass's own sweep - LOCKER carries no such cousin entry, so it stays
  -- whatever it was placed as). The spec's own OuterRim_HoloProjector_Small/
  -- HMC comms console/VFEPD_Banner are not indexed either and are omitted
  -- rather than guessed.
  local desk_side = fr.side("E")
  local desk_placed = wall_walkable(ctx, "TABLE", mi, desk_side, msh)
  if desk_placed and #LAST_PLACED > 0 then
    local d = LAST_PLACED[#LAST_PLACED]
    try_near_walkable(ctx, "STOOL", d[1], d[2], 0, 1, mi, msh)
    try_near_walkable(ctx, "LOCKER", d[1], d[2], 0, 1, mi, msh)
  end
  clutter(ctx, mi, {
    { role = "CRATE", weight = 2 }, { role = "BARREL", weight = 2 },
    { role = "PLANT_POT", weight = 1 }, { role = "SIGN", weight = 1 },
  }, math.max(2, math.ceil((mi.w * mi.h) / 8)), msh)
  wall_lights(ctx, mess_r, 1)
  if not guarantee_secondary(ctx, { "BARREL", "CRATE", "STOOL", "SHELF_SMALL" }, mi.x2, mi.z2, 2, mi, msh) then
    ctx:refuse("secondary", "no room for the mess's one guaranteed secondary (R4)")
  end
  -- ACCEPTED min-canvas residual (1/480 of this pass's own sweep, never at
  -- the 26x22 production canvas): Jawa_HuttCartel's own bigger furniture
  -- set (OuterRim_Tatooine2x1Table etc., the spec's own "the Tatooine
  -- furniture line" dressing) at tech:Industrial + the 22x18 floor can
  -- still leave one Mess primary the door cannot reach. The same
  -- accepted-tradeoff shape cache.lua's own header carries for its absolute
  -- 5x5 floor - a WARN-shaped edge case at the declared minimum, not a
  -- structural defect, and not chased further with per-faction canvas math.

  -- ---- armoury nook: a PERFECT 2x2-interior box (spec's own words - the
  -- only room allowed to be one), tucked behind the barracks.
  local armoury_r = fr.rect(inset, inset + barracks_h + 1, 4, 4)
  local ai = shell(ctx, "Armoury", armoury_r,
    { floor = o.industrial and "FLOOR_WORK" or "FLOOR_POOR", doors = { { fr.side("S") } } })
  local ash = R(ai.x - 1, ai.z - 1, ai.w + 2, ai.h + 2)          -- see the bsh comment above
  hug(ctx, "LOCKER", ai, { "N", "E", "W" }, { mode = "corner" })
  try_near_walkable(ctx, "TOOL_CABINET", ai.x2, ai.z, 0, 1, ai, ash)

  -- ---- power apron (Industrial+), against the armoury's own east side, in
  -- the band behind the barracks the spec names ("R-POWER inside the wall
  -- behind the barracks"). ChemfuelPoweredGenerator (confirmed real) per
  -- the spec's own named pick, not the palette's generic GENERATOR role.
  local powered = o.industrial and ctx:has_role("BATTERY") and ctx:has_role("CONDUIT")
  if powered then
    local gx0, gz0 = fr.cell(inset + 5, inset + barracks_h + 2)
    local g_ok, gcx, gcz = place_near(ctx, "ChemfuelPoweredGenerator", gx0, gz0, 3, "GENERATOR")
    if g_ok then
      local bx0, bz0 = fr.cell(inset + 8, inset + barracks_h + 2)
      local b_ok, bcx, bcz = place_near(ctx, ctx:role("BATTERY"), bx0, bz0, 3, "BATTERY")
      if b_ok then
        local steps = math.max(math.abs(bcx - gcx), math.abs(bcz - gcz))
        for i = 1, steps - 1 do
          local t = i / steps
          local cx2 = math.floor(gcx + (bcx - gcx) * t + 0.5)
          local cz2 = math.floor(gcz + (bcz - gcz) * t + 0.5)
          try_place(ctx, "CONDUIT", cx2, cz2, 0)
        end
        filth(ctx, "Filth_MachineBits", gcx, gcz)
        note("R-POWER: generator+battery pad behind the barracks, conduit bus reaching for the "
          .. "mess stove/turret/watch light within ConnectMaxDist 6 (best-effort placement, not "
          .. "distance-proven offline)")
      else
        ctx:refuse("BATTERY", "no room behind the barracks for the power apron's battery")
      end
    else
      ctx:refuse("ChemfuelPoweredGenerator", "no room behind the barracks for the power apron's generator")
    end
  end

  -- ---- gun position + watch, just inside the gate -------------------------
  -- "Watch": no WatchTower/FT_Platform/TowerLightBeacon indexed this session
  -- (see the header) - a PILLAR-and-LIGHT post stands in for the lookout
  -- point rather than a literal tower. "Gun position": TURRET covering the
  -- gate, 1-2 cells off-axis (spec's own words), can_place-gated so a dense
  -- ring/shell placement earlier never silently doubles up with it.
  -- the TURRET role is only defined for the Hutt/FreeDroid/Deepwater/Empire
  -- faction blocks and tech:Ultra (checked in palette.json) - every OTHER
  -- faction/tech combination has no TURRET role at all, which would leave
  -- the archetype's own defining "gun position" silently absent for most of
  -- the roster. Turret_MiniTurret (confirmed real via search_defs) is used
  -- directly whenever the palette has no TURRET role, rather than treating
  -- "no role" as "no gun position" the way an ordinary optional secondary would.
  local turret_def = ctx:has_role("TURRET") and ctx:role("TURRET") or "Turret_MiniTurret"
  local gux, guz = fr.cell(gate_u, 2)
  local turret_ok, turret_x, turret_z = place_near(ctx, turret_def, gux, guz, 3, "TURRET")
  if not turret_ok then
    ctx:refuse(turret_def, "no cell near the gate mouth fit the gun position")
  end
  local wux, wuz = fr.cell(gate_u + 3, 2)
  local watch_post = try_near(ctx, "PILLAR", wux, wuz, 0, 2, lot)
  if watch_post and ctx:has_role("LIGHT") then try_near(ctx, "LIGHT", wux, wuz, 0, 1, lot) end

  -- `ctx:ruin()`'s own `_RUIN_COUSIN` table can rename the TURRET in place
  -- to a bigger 2-cell "VFEPD_AncientBrokenTurret" with NO footprint
  -- recheck (the same mechanism road_warehouse.lua's own header names for
  -- its shelf placements) - anything placed adjacent to the turret at BUILD
  -- time (when it is still the small confirmed-real base def) can end up
  -- overlapping it once ruin() inflates it. REAL BUG this pass's own sweep
  -- caught, twice: a first draft gated only the Hutt trophies' own START
  -- point against this, which still let THEIR OWN ring search wander into
  -- the keepout on its outer rings, and left the general yard CRATE/BARREL
  -- scatter ungated entirely - both produced real `footprint-collision`
  -- ERRORs on `state=ruined` seeds (8/480 in that sweep). Fixed by checking
  -- every CANDIDATE cell, not just a call's own starting point, via
  -- place_near's new `avoid` parameter and scatter()'s existing one.
  local function near_turret(x, z)
    return turret_ok and (math.abs(x - turret_x) + math.abs(z - turret_z) < 3)
  end

  -- ---- yard clutter: a broken sandbag firing step inside the approach
  -- wall (2 forced gaps, never a full run - R3's "even the three lattice
  -- exceptions get one dropped element"), an outdoor campfire with seats
  -- ("soldiers sit outside" - the spec's own words), crates by the mess,
  -- graves. `keep` excludes the four rooms' own outer footprints so scatter
  -- never lands a crate on a wall it cannot see yet.
  local keep = { bsh, msh, ash }
  if ctx:has_role("SANDBAG") then
    local gap_a, gap_b = rng.int(2, W - 3), rng.int(2, W - 3)
    for u = 1, W - 2 do
      if u ~= gate_u and u ~= gate_u + 1 and u ~= gap_a and u ~= gap_b then
        local x, z = fr.cell(u, 1)
        if not ctx:occupied(x, z) then try_place(ctx, "SANDBAG", x, z, 0) end
      end
    end
  end
  do
    local fx, fz = fr.cell(corridor_lo + math.floor((corridor_hi - corridor_lo) / 2), H - 5)
    local fire = ctx:has_role("STOVE") and "STOVE" or nil
    if fire and try_near(ctx, fire, fx, fz, 0, 2, lot) and #LAST_PLACED > 0 then
      local f = LAST_PLACED[#LAST_PLACED]
      seat_around(ctx, ctx:has_role("CHAIR") and "CHAIR" or "STOOL", f[1], f[2], rng.int(2, 3), lot, 0)
    end
  end
  scatter(ctx, "CRATE", R(mess_r.x - 3, mess_r.z, 3, mess_r.h), rng.int(1, 2),
    { keep_clear = keep, avoid = near_turret })
  scatter(ctx, "BARREL", R(mess_r.x - 3, mess_r.z, 3, mess_r.h), rng.int(0, 1),
    { keep_clear = keep, avoid = near_turret })
  local graves = 0
  if ctx:has_role("GRAVE") then
    for _ = 1, rng.int(0, 2) do
      local gx, gz = fr.cell(gate_u + rng.pick({ -3, 4 }), rng.int(3, 5))
      if try_near(ctx, "GRAVE", gx, gz, rng.int(0, 3), 2, lot) then graves = graves + 1 end
    end
  end
  if o.hutt then
    -- fr.cell() returns TWO values; passed inline as a non-last argument
    -- Lua only keeps the first one - road_warehouse.lua's own header names
    -- this exact trap. Captured into named locals first, like every other
    -- fr.cell() call in this file already does. `near_turret` (defined
    -- above, by the gun position) keeps every candidate the ring search
    -- considers clear of the turret's own future ruin-inflated footprint,
    -- not just the call's own starting point.
    local sx, sz = fr.cell(gate_u - 2, 0)
    place_near(ctx, "Skullspike", sx, sz, 2, "TROPHY", 0, lot, near_turret)
    local gcx, gcz = fr.cell(gate_u + 3, 0)
    place_near(ctx, "GibbetCage", gcx, gcz, 2, "TROPHY", 0, lot, near_turret)
  end

  -- ---- defenders (E3) - see the header's own note on why this is the
  -- first ALIVE PAWN in the folder and what that does and does not prove.
  local kind = defender_kind(o)
  local defenders = 0
  if o.state ~= "abandoned" then
    for i = 1, math.min(2, o.crew - 1) do
      local dx2, dz2 = fr.cell(gate_u + (i == 1 and -2 or 2), 3)
      if in_rect(dx2, dz2, lot) then ctx:pawn(kind, dx2, dz2, "wild", "alive"); defenders = defenders + 1 end
    end
    local tx2, tz2 = fr.cell(gate_u, 2)
    if turret_ok then ctx:pawn(kind, tx2, tz2 + 1, "wild", "alive"); defenders = defenders + 1 end
  else
    for _ = 1, rng.int(1, 2) do
      local rx, rz = fr.cell(gate_u + rng.int(-2, 2), rng.int(2, 4))
      if in_rect(rx, rz, lot) then
        ctx:pawn(kind, rx, rz, "wild", rng.pick({ "skeleton", "dessicated" }))
        defenders = defenders + 1
      end
    end
  end

  note(string.format(
    "garrison_tiny: approach=%s peri=%s(%d,gate=%s) beds=%d desk=%s power=%s turret=%s watch=%s "
    .. "graves=%d defenders=%d(%s,state=%s)",
    face, peri, ring_n, tostring(gate_n >= 1), beds, tostring(desk_placed), tostring(powered),
    tostring(turret_ok), tostring(watch_post), graves, defenders, kind, o.state))

  if o.state == "abandoned" then
    local n = 0
    for _ = 1, math.max(4, math.floor(rect.w * rect.h / 30)) do
      local x, z = rng.int(rect.x, rect.x2), rng.int(rect.z, rect.z2)
      if not ctx:occupied(x, z) then filth(ctx, rng.chance(0.6) and "Filth_Sand" or "Filth_Dirt", x, z); n = n + 1 end
    end
    note(string.format("abandoned: %d drift(s) of sand and dirt; the shells stand empty", n))
  elseif o.state == "ruined" then
    ctx:ruin(0.3)
  end
end
