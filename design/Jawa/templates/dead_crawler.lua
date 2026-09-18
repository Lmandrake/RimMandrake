-- dead_crawler.lua - "The Dead Crawler" (structure_injection_roster.md
-- PROMISE #6, RSW tier, Rekko+Mob'Unloo): "any desert" - a fallen
-- sandcrawler hull, three interior decks, "a dungeon-lite full of sleeping
-- hands." A wholly NEW TileMutatorDef (RSW_DeadCrawler) - no existing
-- vanilla def adopted, same "NEW flagship rimplace" shape as
-- krayt_graveyard.lua/podracer_wreck.lua/hunting_lodge.lua, not a patch
-- onto someone else's content.
--
-- Sibling of crashed_ship.lua (structure_procedural_spec.md sec 8.9, a
-- one-deck STARSHIP crash) - that file's own header already names this row
-- as "a separate, bigger flagship template still owed." This is the
-- ground-vehicle counterpart: three walled compartments in a straight
-- line ("three decks" - RimWorld has no Z-axis, so three side-by-side
-- rooms is the concrete realization the engine can build), each holding
-- sleeping occupants. No furrow/thrusters/roof-tears/live pawns - that
-- dressing is crashed_ship's own STARSHIP-crash grammar, not a fallen
-- ground crawler's.
--
-- Real defNames reused from crashed_ship.lua's own already-`verify`-clean
-- vocabulary (not re-guessed), re-confirmed against the live def dump
-- (2026-09-18T05-05-13Z capture):
--   Ship_CryptosleepCasket (Core, 1x2) - "sleeping hands" made literal,
--     one or two per deck.
--   AncientBlastDoor (Core) - every door, interior and exterior.
--   Wall / Steel (Core) - the hull shell.
--   PowerConduit, AncientLamp, ChunkSlagSteel, Filth_RubbleBuilding
--     (Core) - long-dead wreck dressing. No working power anywhere in
--     this template (no generator/battery placed) - a fallen hull reads
--     as dead, same "lights (none live)" convention crashed_ship.lua uses
--     for its own AncientLamp placements.
--
-- API available: ctx (see luaenv.Ctx), rect, params, rng, role(), note()

-- The declared canvas floor; the engine checks it before build() runs
-- (TEMPLATE_CANVAS_UNDECLARED_1). `rimplace minrect dead_crawler`.
-- 3 bays of at least 7 wide each + 4 shared wall columns = 25; 9 tall
-- (7 interior + north/south walls).
function min_rect(params)
  return 25, 9
end

function build(ctx)
  local W, H = rect.w, rect.h
  local x, z = rect.x, rect.z
  local BAYS = 3
  local min_w = 7
  local usable = W - (BAYS + 1)
  if usable < BAYS * min_w or H < 9 then
    ctx:refuse("footprint", string.format(
      "%dx%d cannot hold a 3-deck fallen crawler hull of at least %d wide "
        .. "each plus shared walls (need >=25x9)", W, H, min_w))
    return
  end

  local each = math.floor(usable / BAYS)
  local bays, cx = {}, x
  for i = 1, BAYS do
    local bw = (i == BAYS) and (W - (cx - x) - 1) or (each + 1)
    bays[#bays + 1] = { x = cx, z = z, w = bw + 1, h = H }
    cx = cx + bw
  end

  local caskets, conduits, lamps, chunks, filth_n = 0, 0, 0, 0, 0
  for i, bay in ipairs(bays) do
    ctx:room("ShipHull", bay.x, bay.z, bay.w, bay.h, true)
    ctx:wall_rect(bay.x, bay.z, bay.w, bay.h, "Wall", "Steel")

    if i == 1 then
      -- exterior boarding door, bow deck's own outer (north) wall
      ctx:door(bay.x + math.floor(bay.w / 2), bay.z, "AncientBlastDoor")
    else
      -- interior bulkhead door on the shared wall with the previous deck
      ctx:door(bay.x, bay.z + math.floor(bay.h / 2), "AncientBlastDoor")
    end

    -- one or two sleeping occupants per deck - "full of sleeping hands"
    local n = rng.int(1, 2)
    for k = 1, n do
      local cxx = bay.x + 1 + (k - 1) * 2
      local czz = bay.z + bay.h - 3
      if cxx + 1 <= bay.x + bay.w - 2 and ctx:can_place("Ship_CryptosleepCasket", cxx, czz) then
        ctx:place("Ship_CryptosleepCasket", cxx, czz)
        caskets = caskets + 1
      end
    end

    -- long-dead dressing: a conduit stub (never a working bus - no
    -- generator/battery this pass, this hull is dead), an unlit lamp
    if ctx:can_place("PowerConduit", bay.x + 1, bay.z + 1) then
      ctx:place("PowerConduit", bay.x + 1, bay.z + 1)
      conduits = conduits + 1
    end
    if rng.chance(0.5) then
      local lx, lz = bay.x + bay.w - 2, bay.z + 1
      if ctx:can_place("AncientLamp", lx, lz) then
        ctx:place("AncientLamp", lx, lz)
        lamps = lamps + 1
      end
    end
    for zz = bay.z + 1, bay.z + bay.h - 2 do
      for xx = bay.x + 1, bay.x + bay.w - 2 do
        -- can_place, not occupied(): occupied() only tracks a thing's
        -- ANCHOR cell, and Ship_CryptosleepCasket above is multi-cell
        -- (1x2) - the same footprint-collision class ashfall_battery.lua
        -- hit live on ChemfuelTank (2x2/3x3), caught by `rimplace lint`.
        if ctx:can_place("ChunkSlagSteel", xx, zz) and rng.chance(0.05) then
          ctx:place("ChunkSlagSteel", xx, zz)
          chunks = chunks + 1
        elseif ctx:can_place("Filth_RubbleBuilding", xx, zz) and rng.chance(0.06) then
          ctx:place("Filth_RubbleBuilding", xx, zz, 0, nil, "FILTH", true)
          filth_n = filth_n + 1
        end
      end
    end
  end

  note(string.format(
    "dead crawler: 3 decks, %d Ship_CryptosleepCasket occupants, %d conduit "
      .. "stubs, %d unlit lamps, %d slag chunks, %d rubble filth cells - "
      .. "static wreck, no live pawns, no working power",
    caskets, conduits, lamps, chunks, filth_n))
end
