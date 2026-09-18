-- ashfall_battery.lua - "The Ashfall Battery" (structure_injection_
-- roster.md PROMISE #17, RUT tier, Ta'Baa): "existing mutator + our
-- fuel-farm room · launch fuel components; the Ashfall Road's origin
-- story."
--
-- Anchor: vanilla `AncientLaunchSite` TileMutatorDef (Odyssey,
-- workerClass RimWorld.TileMutatorWorker_AncientStructure, the same def
-- `sacred_sites_pass_1.md` §1a cites as its own "worked example" -
-- confirmed by direct read: `unused_mutators_census.md`'s Part-1 in-use
-- list carries it as a TileMutatorDef, not the LandmarkDef
-- tile_augmentation_catalogue.md's own table mistakenly lists it as -
-- doc disagreement, resolved here against the live def dump, not either
-- doc). Its `extraGenSteps` reads `[]` in the live def dump
-- (2026-09-18T05-05-13Z capture, defs/TileMutatorDef.json) - confirmed by
-- direct read, not guessed - so the wiring Patch Adds a whole new
-- `<extraGenSteps>` element to the def node, same shape as
-- Dunes/DryLake/Hollow/Caves/AncientUplink.
--
-- Real defNames verified against the live def dump:
--   LargeChemfuelTank (Odyssey, 3x3), ChemfuelTank (Odyssey, 2x2) -
--     "launch fuel components" made literal.
--   Chemfuel (Core, 1x1 item, stackable resource) - loose fuel
--     stacks/spillage.
-- Neither tank ThingDef carries a power comp - no generator/battery
-- needed, simpler than signal_mast.lua's comms room.
--
-- API available: ctx (see luaenv.Ctx), rect, params, rng, role(), note()

-- The declared canvas floor; the engine checks it before build() runs
-- (TEMPLATE_CANVAS_UNDECLARED_1). `rimplace minrect ashfall_battery`.
function min_rect(params)
  return 10, 8
end

function build(ctx)
  local W, H = 10, 8
  if rect.w < W or rect.h < H then
    ctx:refuse("footprint", string.format(
      "%dx%d cannot hold a %dx%d fuel farm", rect.w, rect.h, W, H))
    return
  end
  local x, z = rect.x, rect.z

  ctx:room("Storeroom", x, z, W, H, true)
  ctx:wall_rect(x, z, W, H)
  ctx:door(x + math.floor(W / 2), z + H - 1)

  local tanks = 0
  if ctx:can_place("LargeChemfuelTank", x + 1, z + 1) then
    ctx:place("LargeChemfuelTank", x + 1, z + 1)
    tanks = tanks + 1
  end
  if ctx:can_place("LargeChemfuelTank", x + W - 4, z + 1) then
    ctx:place("LargeChemfuelTank", x + W - 4, z + 1)
    tanks = tanks + 1
  end
  if ctx:can_place("ChemfuelTank", x + math.floor(W / 2) - 1, z + H - 4) then
    ctx:place("ChemfuelTank", x + math.floor(W / 2) - 1, z + H - 4)
    tanks = tanks + 1
  end

  -- loose fuel stacks: spillage from the launch works, scattered wherever
  -- the tanks left room
  local fuel_stacks = 0
  for zz = z + 1, z + H - 2 do
    for xx = x + 1, x + W - 2 do
      -- can_place, not occupied(): occupied() only tracks a thing's ANCHOR
      -- cell, not its full footprint (imperial_waystation.lua's own
      -- Table1x2c note), and the two tanks above are multi-cell (3x3/2x2) -
      -- caught live by `rimplace lint` reporting a real footprint-collision
      -- before this fix.
      if ctx:can_place("Chemfuel", xx, zz) and rng.chance(0.06) then
        ctx:place("Chemfuel", xx, zz)
        fuel_stacks = fuel_stacks + 1
      end
    end
  end

  note(string.format(
    "ashfall battery: %d/3 chemfuel tanks placed, %d loose Chemfuel stacks "
      .. "- launch fuel components, the Ashfall Road's own origin story",
    tanks, fuel_stacks))
end
