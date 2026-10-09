using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    //   <li Class="CompProperties_TempControl">            (vanilla: the target-temperature gizmo)
    //     <lowPowerConsumptionFactor>0.3</lowPowerConsumptionFactor>
    //   </li>
    //   <li Class="RimMandrake.EnvironmentalHazards.CompProperties_BlowerRoomCooler" />
    public class CompProperties_BlowerRoomCooler : CompProperties
    {
        public CompProperties_BlowerRoomCooler()
        {
            compClass = typeof(RM_CompBlowerRoomCooler);
        }
    }

    // BLOWER_ROOM_COOLER_1 (decision taken by question card 2026-10-08; owner typed: "Just add this
    // as a special kind of room cooler. No one wants a room heater in that biome..."). The dry-air
    // blower cools the enclosed room behind it toward its target temperature and NEVER pushes heat
    // into any room: unlike vanilla Building_Cooler there is no hot exhaust side. Vanilla heat only
    // (one kind of heat): it changes the room's temperature and nothing else.
    //
    // "Behind" is the same cell vanilla Building_Cooler cools (Position + South rotated), so the
    // blower's front faces out across the doorway where RM_CompDryFieldEmitter's arc already points.
    // Strength (heat/s) and power draw (W) are Mod Settings, PROVISIONAL. Normal ticker (power, fuel),
    // so the rare cadence runs from CompTick (TICKER_NEVER_FIRES_FIX_1).
    public class RM_CompBlowerRoomCooler : ThingComp
    {
        private CompTempControl tempControl;
        private CompPowerTrader power;
        private CompRefuelable fuel;
        private CompFlickable flick;

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            tempControl = parent.GetComp<CompTempControl>();
            power = parent.GetComp<CompPowerTrader>();
            fuel = parent.GetComp<CompRefuelable>();
            flick = parent.GetComp<CompFlickable>();
        }

        public override void CompTick()
        {
            base.CompTick();
            if (!parent.IsHashIntervalTick(GenTicks.TickRareInterval))
            {
                return;
            }
            CoolOnce();
        }

        private void CoolOnce()
        {
            Map map = parent.Map;
            if (map == null || power == null || !power.PowerOn)
            {
                return;
            }

            bool running = (fuel == null || fuel.HasFuel) && (flick == null || flick.SwitchIsOn);
            bool cooling = false;
            if (running && RM_EnvironmentalHazardsSettings.dryAirBlowerCoolingEnabled && tempControl != null)
            {
                IntVec3 behind = parent.Position + IntVec3.South.RotatedBy(parent.Rotation);
                if (behind.InBounds(map) && !behind.Impassable(map))
                {
                    float energy = RM_RoomCoolerKernel.CoolingEnergyPerRareTick(
                        RM_EnvironmentalHazardsSettings.dryAirBlowerCoolingStrength);
                    float change = RM_RoomCoolerKernel.ClampNeverHeat(
                        GenTemperature.ControlTemperatureTempChange(behind, map, energy, tempControl.TargetTemperature));
                    Room room = behind.GetRoom(map);
                    if (change < 0f && room != null)
                    {
                        room.Temperature += change;
                        cooling = true;
                    }
                }
            }

            float lowFactor = tempControl != null ? tempControl.Props.lowPowerConsumptionFactor : 1f;
            power.PowerOutput = -RM_RoomCoolerKernel.PowerDraw(
                RM_EnvironmentalHazardsSettings.dryAirBlowerPowerWatts, cooling, lowFactor);
            if (tempControl != null)
            {
                tempControl.operatingAtHighPower = cooling;
            }
        }
    }
}
