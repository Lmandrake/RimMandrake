-- signal_mast.lua - "The Signal Mast" (structure_injection_roster.md
-- PROMISE #7, RM tier, "reskin AncientUplink", Ohm): "existing mutator +
-- our comms-console room · working uplink; using it raises Visibility."
--
-- Anchor: vanilla `AncientUplink` TileMutatorDef (Odyssey,
-- workerClass RimWorld.TileMutatorWorker_AncientUplink, confirmed via
-- unused_mutators_full_list.csv line 45). Its `extraGenSteps` reads `[]`
-- in the live def dump (2026-09-18T05-05-13Z capture,
-- defs/TileMutatorDef.json) - confirmed by direct read, not guessed - so
-- the wiring Patch Adds a whole new `<extraGenSteps>` element to the def
-- node, same shape as Dunes/DryLake/Hollow/Caves.
--
-- Real defNames verified against the live def dump:
--   CommsConsole (Core, 3x2, CompPowerTrader) - the comms console itself.
--   TorchLamp (Core, 1x1) - light near the door.
--   PowerConduit/SolarGenerator/Battery via role() (CONDUIT/GENERATOR/
--     BATTERY) - same verified generator+battery-transmitter / bus /
--     connector-within-ConnectMaxDist-6 pattern hunting_lodge.lua's cold
--     room already proved (nursery.lua's own pattern). CommsConsole is
--     the CONNECTOR here in place of a cooler.
--
-- This mod (mandrake.rm.injections) is the campaign-agnostic engine tier
-- ("RM" = any RimWorld game, per NAMING_SCHEME_PLAN.md) - the Signal Mast
-- reskins a base-game mutator with no Star Wars/Ash'karr-specific content,
-- so it lives here rather than in a tier-specific content pack.
--
-- API available: ctx (see luaenv.Ctx), rect, params, rng, role(), note()

-- The declared canvas floor; the engine checks it before build() runs
-- (TEMPLATE_CANVAS_UNDECLARED_1). `rimplace minrect signal_mast`.
-- 11x8 room + 8w/2h power apron (hunting_lodge.lua's own verified margin
-- for a generator+battery+bus beyond the shell).
function min_rect(params)
  return 19, 10
end

function build(ctx)
  local ROOM_W, ROOM_H = 11, 8
  if rect.w < ROOM_W + 8 or rect.h < ROOM_H + 2 then
    ctx:refuse("footprint", string.format(
      "%dx%d cannot hold an %dx%d comms room plus its power apron (+8w/+2h)",
      rect.w, rect.h, ROOM_W, ROOM_H))
    return
  end
  local x, z = rect.x, rect.z

  ctx:room("Storeroom", x, z, ROOM_W, ROOM_H, true)
  ctx:wall_rect(x, z, ROOM_W, ROOM_H)
  ctx:door(x + math.floor(ROOM_W / 2), z)

  -- the comms console, back against the south wall - closest to the
  -- external power bus below it, within ConnectMaxDist 6
  local console_x = x + math.floor((ROOM_W - 3) / 2)
  local console_z = z + ROOM_H - 3
  local console_ok = ctx:place("CommsConsole", console_x, console_z, 0)

  ctx:place("TorchLamp", x + 1, z + 1)

  -- power: transmitters (generator, battery) cardinal-join a bus outside
  -- the south wall; the console is a CONNECTOR within ConnectMaxDist 6 of
  -- the nearest transmitter - same verified shape hunting_lodge.lua's cold
  -- room already proved.
  local bus_z = z + ROOM_H
  local gen_x = x + ROOM_W + 4
  local conduits = 0
  for bx = x + 2, gen_x - 2 do
    ctx:place(role("CONDUIT"), bx, bus_z)
    conduits = conduits + 1
  end
  ctx:place_role("GENERATOR", gen_x, bus_z)
  ctx:place_role("BATTERY", x + 3, bus_z + 1)

  note(string.format(
    "signal mast comms room: %dx%d, console placed=%s, generator/battery "
      .. "transmitters on an exterior bus (%d conduit cells), console is a "
      .. "CONNECTOR within ConnectMaxDist 6 - a working uplink per the "
      .. "roster's own line. TEMPLATE CANNOT PROVE actual power flow live.",
    ROOM_W, ROOM_H, tostring(console_ok), conduits))
end
