using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.Utinni.ShipShields
{
    // Particulate/light-kinetic field (shd:particulate-screen). v1 slice:
    // "wind, ash, vapor, bio contamination, spores, smoke, sand, and rain
    // damage completely" -- this build only implements the concrete,
    // checkable half of that (sweeping weather-deposited filth out of
    // radius each interval). Small-animal repulsion and direct weather-
    // damage negation are NOT implemented; see the item file's
    // remaining-gap note before calling this ruling row fully built.
    public class CompShieldParticulateScreen : ThingComp
    {
        public CompProperties_ShieldParticulateScreen Props => (CompProperties_ShieldParticulateScreen)props;

        private CompShieldModuleSwitch ModuleSwitch => parent.GetComp<CompShieldModuleSwitch>();
        private CompPowerTrader PowerTrader => parent.GetComp<CompPowerTrader>();

        public override void CompTick()
        {
            if (!parent.IsHashIntervalTick(Props.intervalTicks))
            {
                return;
            }

            CompShieldModuleSwitch moduleSwitch = ModuleSwitch;
            if (moduleSwitch != null && moduleSwitch.CurrentMode != ShieldFieldMode.Particulate)
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

            foreach (IntVec3 cell in GenRadial.RadialCellsAround(parent.Position, Props.radius, true))
            {
                if (!cell.InBounds(map))
                {
                    continue;
                }

                List<Thing> things = map.thingGrid.ThingsListAtFast(cell);
                for (int i = things.Count - 1; i >= 0; i--)
                {
                    if (things[i] is Filth filth && !filth.Destroyed)
                    {
                        filth.Destroy();
                    }
                }
            }
        }
    }
}
