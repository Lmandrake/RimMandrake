using UnityEngine;
using RimWorld;
using Verse;

namespace RimMandrake.Utinni.ShipShields
{
    // Thermal-rejection field (shd:thermal-veil). Only active while
    // CompShieldModuleSwitch.CurrentMode == Thermal (or standalone, if no
    // switch comp is present). Reuses the same vanilla primitive
    // Building_Heater/Building_Cooler/Building_LifeSupportUnit are built on
    // (GenTemperature.ControlTemperatureTempChange, applied straight to
    // Room.Temperature -- not PushHeat, which is a raw-energy input for
    // fires/explosions/vents and would double-divide by room size) rather
    // than re-deriving room thermal math from scratch.
    public class CompShieldThermalVeil : ThingComp
    {
        public CompProperties_ShieldThermalVeil Props => (CompProperties_ShieldThermalVeil)props;

        private CompShieldModuleSwitch ModuleSwitch => parent.GetComp<CompShieldModuleSwitch>();
        private CompPowerTrader PowerTrader => parent.GetComp<CompPowerTrader>();

        public override void CompTick()
        {
            if (!ShipShieldsSettings.thermalVeilEnabled)
            {
                return;
            }

            if (!parent.IsHashIntervalTick(Props.intervalTicks))
            {
                return;
            }

            CompShieldModuleSwitch moduleSwitch = ModuleSwitch;
            if (moduleSwitch != null && moduleSwitch.CurrentMode != ShieldFieldMode.Thermal)
            {
                return;
            }

            CompPowerTrader power = PowerTrader;
            if (power != null && !power.PowerOn)
            {
                return;
            }

            Map map = parent.Map;
            if (map == null)
            {
                return;
            }

            Room room = parent.GetRoom();
            float currentTemp = room != null ? room.Temperature : GenTemperature.GetTemperatureForCell(parent.Position, map);
            float diff = Props.comfortTemperature - currentTemp;
            if (Mathf.Abs(diff) < 0.5f)
            {
                return;
            }

            // Same calling convention as vanilla's heater/cooler: a huge
            // positive energyLimit only ever yields a warming delta, a huge
            // negative one only a cooling delta -- pick the direction we
            // actually need, then apply only a fraction of it.
            float energyLimit = diff > 0f ? float.MaxValue : float.MinValue;
            float idealChange = GenTemperature.ControlTemperatureTempChange(parent.Position, map, energyLimit, Props.comfortTemperature);
            if (idealChange == 0f)
            {
                return;
            }

            // ControlTemperatureTempChange's return is already a room-scale
            // temperature delta, not a raw energy quantity -- vanilla's own
            // Building_Heater/Building_Cooler/Building_LifeSupportUnit all
            // add it straight to Room.Temperature. Routing it through
            // PushHeat (which divides by CellCount again, for a genuine
            // energy input like an explosion or a fire) silently shrank the
            // effect by an extra, unintended factor of room size.
            room.Temperature += idealChange * Props.rejectionFactor;
        }
    }
}
