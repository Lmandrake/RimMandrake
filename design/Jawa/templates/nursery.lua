-- nursery.lua - a COLD nursery that actually holds temperature.
--
-- Why this file exists, 2026-08-26: dwelling.lua's nursery variant placed a
-- Cooler and an EggBox and nothing to power them. Measured live, the room it
-- was built to protect sat at 41.5C through a heat wave; Jawa eggs ruin above
-- 32C. Three separate causes, all invisible to a presence check:
--
--   1. no power layer at all - no conduit, no generator, no battery
--   2. hand-wired, the generator and the conduit run formed TWO nets that
--      never merged (transmitters chain CARDINALLY; connectors reach 6 cells)
--   3. the cooler's cold side faced OUT. Building_Cooler cools
--      Position + IntVec3.South.RotatedBy(Rotation) - the cell BEHIND it.
--
-- So this template models the power layer explicitly and states the rule for
-- each placement, because "it is there" was never the question.
--
-- API: ctx (luaenv.Ctx), rect, params, rng, role(), note()

function build(ctx)

  local p    = params
  local x, z = rect.x, rect.z
  local W, H = rect.w, rect.h

  -- The shell. Small on purpose: a cooler's depression is per-room-volume, and
  -- the measured failure was a 48-cell room one cooler could not hold.
  local RW, RH = 8, 8
  if W < RW + 8 or H < RH + 1 then
    ctx:refuse("nursery", "needs at least " .. (RW + 8) .. "x" .. (RH + 1) .. " of footprint")
    return
  end

  local room_id = ctx:room("Nursery", x, z, RW, RH, true)
  ctx:wall_rect(x, z, RW, RH)

  -- Way in, on the south wall. A room with no door is unreachable and lint says so.
  ctx:door(x + 3, z)

  -- ---------------------------------------------------------------------------
  -- the power layer - the whole point of this file
  -- ---------------------------------------------------------------------------
  -- 🔴 THE RULE THAT DECIDES THIS WHOLE FILE, and it is TWO rules, not one:
  --
  --   * A TRANSMITTER (transmitsPower=true - conduits, and SolarGenerator,
  --     which ships transmitsPower TRUE) joins a net ONLY by CARDINAL cell
  --     adjacency. No radius, no diagonal.
  --   * A CONNECTOR (CompPowerTrader/CompPowerBattery that does not transmit -
  --     Cooler, Battery) links to the nearest transmitter within
  --     PowerConnectionMaker.ConnectMaxDist = 6, via a plain
  --     CellRect.ExpandedBy(6) with NO line-of-sight test. It reaches THROUGH
  --     a wall.
  --
  -- Getting this backwards is measured, twice: a generator 3 cells from a
  -- conduit run sat on its own net at 1700 W while the coolers read 0 W.
  --
  -- So the bus runs OUTSIDE, along the row above the north wall, cardinally
  -- contiguous from the generator to over the coolers. The coolers then reach
  -- it through the wall as connectors. Nothing has to cross a wall cell -
  -- which this engine cannot express anyway, since place() refuses a second
  -- def in an occupied cell and wall_mount() would delete the wall.
  local bus_z  = z + RH
  -- The generator is 4x4 and its footprint is centred on the origin cell, so
  -- it is parked clear of the bus row's end and the bus is run up to its west
  -- edge. Lint's footprint-collision check is what forces this to be exact.
  local gen_x  = x + RW + 4
  for cx = x + 2, gen_x - 2 do
    ctx:place(role("CONDUIT"), cx, bus_z)
  end

  -- Coolers sit IN the north wall at rot 0. Building_Cooler cools
  -- Position + IntVec3.South.RotatedBy(Rotation) - the cell BEHIND it - so
  -- rot 0 in a north wall puts cold INSIDE and the exhaust outdoors. Rot 2 is
  -- backwards, and was measured running at "low power" doing nothing, because
  -- it was cooling the open air.
  local COOLERS = 2
  for i = 1, COOLERS do
    local cx = x + 2 + (i - 1) * 3
    ctx:wall_mount("COOLER", cx, z + RH - 1, 0)
    local d = bus_z - (z + RH - 1)
    if d > 6 then
      ctx:refuse("COOLER", "is " .. d .. " cells from the bus; ConnectMaxDist is 6")
    end
  end

  -- The generator sits cardinally ON the end of the bus, because it is a
  -- TRANSMITTER and proximity would buy it nothing.
  ctx:place_role("GENERATOR", gen_x, bus_z)

  -- ⚠️ The Battery is ALSO a TRANSMITTER (transmitsPower true in its
  -- CompProperties_Power - checked in the def dump, not assumed), so proximity
  -- buys it nothing either. It goes cardinally onto the bus, outside.
  ctx:place_role("BATTERY", x + 3, bus_z + 1)

  -- ⚠️ The generator must stay UNROOFED - CompPowerPlantSolar scales output by
  -- RoofedPowerOutputFactor, and ctx:room() roofs only the shell interior, so
  -- the apron is clear. Do not extend the roof over it.

  -- ---------------------------------------------------------------------------
  -- what the room is FOR
  -- ---------------------------------------------------------------------------
  local nests = math.max(1, math.floor((p.occupants or 4) / 2))
  for i = 1, nests do
    ctx:place_role("NEST", x + 1 + (i - 1) * 2, z + 1)
  end

  -- ⛔ No stove, no heat-pushing worktable, anywhere in this shell. The measured
  -- dwelling put an ElectricStove (Building_WorkTable_HeatPush) in the room the
  -- nursery opened off, so the only way in was through the hottest room.

  ctx:note("cold nursery: " .. COOLERS .. " cooler(s) at rot 0, powered from "
    .. "an EXTERIOR conduit bus. Generator and battery are TRANSMITTERS and "
    .. "sit cardinally ON the bus; the coolers are CONNECTORS and reach it "
    .. "within ConnectMaxDist 6, through the wall. ⚠️ TEMPLATE "
    .. "CANNOT PROVE the room holds <=32C - that needs a live reading.")
end
