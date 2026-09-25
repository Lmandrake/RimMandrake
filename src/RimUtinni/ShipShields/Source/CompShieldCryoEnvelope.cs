using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.ShipShields
{
    // Cold-rejection field (shd:cryo-envelope). Only active while
    // CompShieldModuleSwitch.CurrentMode == Cryo (or standalone, if no
    // switch comp is present). Mirrors CompShieldThermalVeil's use of the
    // same vanilla primitive (GenTemperature.ControlTemperatureTempChange,
    // applied straight to Room.Temperature -- ControlTemperatureTempChange
    // itself already returns 0f for a null or outdoor room, so no extra
    // null-guard is needed around that call; confirmed via rimsage read of
    // Verse/GenTemperature.cs), but adds one thing thermal veil does not
    // have: a constant per-interval drain, the honest reading of the
    // ruling's "pulls in heat in both directions... slowly decreases the
    // temperature within the ship."
    //
    // Not built: the "shields... glowing with red-orange black body
    // radiation" visual. No existing vanilla comp/graphic primitive was
    // found that does a temperature-driven glow overlay (checked, not
    // guessed), and inventing new VFX art/rendering is out of scope for
    // this pass the same way real generator art is -- an honest residual
    // gap, not a build gap in the mechanism itself.
    public class CompShieldCryoEnvelope : ThingComp
    {
        public CompProperties_ShieldCryoEnvelope Props => (CompProperties_ShieldCryoEnvelope)props;

        private CompShieldModuleSwitch ModuleSwitch => parent.GetComp<CompShieldModuleSwitch>();
        private CompPowerTrader PowerTrader => parent.GetComp<CompPowerTrader>();

        public override void CompTick()
        {
            if (!ShipShieldsSettings.cryoEnvelopeEnabled)
            {
                return;
            }

            if (!parent.IsHashIntervalTick(Props.intervalTicks))
            {
                return;
            }

            CompShieldModuleSwitch moduleSwitch = ModuleSwitch;
            if (moduleSwitch != null && moduleSwitch.CurrentMode != ShieldFieldMode.Cryo)
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
            if (Mathf.Abs(diff) >= 0.5f)
            {
                // Same calling convention as CompShieldThermalVeil: a huge
                // positive energyLimit only ever yields a warming delta, a
                // huge negative one only a cooling delta.
                float energyLimit = diff > 0f ? float.MaxValue : float.MinValue;
                float idealChange = GenTemperature.ControlTemperatureTempChange(parent.Position, map, energyLimit, Props.comfortTemperature);
                if (idealChange != 0f)
                {
                    // idealChange != 0f already proves cell.GetRoom(map)
                    // returned a real, non-outdoor room (see
                    // ControlTemperatureTempChange's own early-out), so this
                    // is the same room read above -- safe to write.
                    room.Temperature += idealChange * Props.insulationFactor;
                }
            }

            // shd:cryo-envelope's own cost, distinct from thermal veil: a
            // real interior room only (never the outdoor "room" -- writing
            // to that would mean nudging the map's own outdoor temperature,
            // which is not what "the temperature within the ship" means).
            if (room != null && !room.UsesOutdoorTemperature)
            {
                room.Temperature -= Props.interiorDriftPerInterval;
            }
        }
    }
}
