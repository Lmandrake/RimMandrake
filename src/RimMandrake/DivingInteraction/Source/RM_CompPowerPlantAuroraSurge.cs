using System.Text;
using RimWorld;
using Verse;

namespace RimMandrake.DivingInteraction
{
    // ════════════════════════════════════════════════════════════════════
    // CHILL_AURORA_SURGE_1 — deliverable 2, the harvest.
    //
    // Owner's framing (item text): "Free watts against the brutal cooling
    // load (CHILL_THERMAL_ENGINE_1), if you built for it."
    //
    // PATTERN: vanilla's own CompPowerPlantWind (RimSage-read against the
    // decompiled engine) is the closest existing "conditional power
    // generation" shape — it overrides CompPowerPlant's protected
    // DesiredPowerOutput to scale -Props.PowerConsumption (a NEGATIVE
    // basePowerConsumption is vanilla's own convention for "this building
    // GENERATES, does not consume" — WindTurbine ships -2300) by a live
    // 0..1 environmental read (there, WindManager.WindSpeed capped at
    // 1.5f; here, RM_MapComponent_ChillAuroraSurge.SurgeStrength, already
    // 0..1). CompPowerPlant.UpdateDesiredPowerOutput (the base class's own
    // virtual method, called every CompTick from CompPowerPlant.CompTick)
    // already zeroes PowerOutput whenever PowerOn is false, the flick
    // switch is off, or CompBreakdownable says broken down — the same
    // free "switch it off, it makes nothing" behaviour every other
    // powered building in the game gets, with zero code written here.
    //
    // ZERO WHEN NO SURGE: unlike CompPowerPlantWind (which makes SOME
    // power in any nonzero wind), this returns exactly 0f whenever
    // RM_MapComponent_ChillAuroraSurge.IsSurgeActive is false — "harvest
    // the storm," never a free permanent generator, the item's own
    // explicit constraint. SurgeStrength already reads 0 whenever
    // IsSurgeActive is false (that component's own public contract), so
    // the explicit IsSurgeActive check below is belt-and-braces, not
    // load-bearing on its own.
    //
    // ROOFED CHECK: the mast needs open access to the same "sky" the
    // drowned aurora reaches the floor through (RM_MapComponent_
    // ChillDrownedAurora's own header: "the brightest sky on the planet
    // arrives... as dim shifting curtains") — a roofed cell reads as
    // sheltered from that current, so a mast built indoors (nothing stops
    // it structurally) simply never generates. This is a runtime check,
    // not a placement restriction — the same choice this codebase already
    // made for RM_HeatedSuitCharger and RM_ChillStonewaterExtractor
    // (gate BEHAVIOUR, don't add a bespoke PlaceWorker for every siting
    // preference).
    // ════════════════════════════════════════════════════════════════════
    public class CompPowerPlantAuroraSurge : CompPowerPlant
    {
        private bool isChillSeabed;

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            isChillSeabed = RM_ChillFireGate.IsChillSeabedMap(parent.Map);
        }

        public override void PostSwapMap()
        {
            base.PostSwapMap();
            isChillSeabed = RM_ChillFireGate.IsChillSeabedMap(parent.Map);
        }

        protected override float DesiredPowerOutput
        {
            get
            {
                if (!isChillSeabed || !RM_DivingSettings.masterEnabled || !RM_DivingSettings.chillAuroraSurgeEnabled)
                {
                    return 0f;
                }
                if (parent.Position.Roofed(parent.Map))
                {
                    return 0f; // no open access to the sky the surge reaches the floor through
                }

                RM_MapComponent_ChillAuroraSurge surge = parent.Map.GetComponent<RM_MapComponent_ChillAuroraSurge>();
                if (surge == null || !surge.IsSurgeActive)
                {
                    return 0f; // harvest the storm, never a free permanent generator
                }

                return -Props.PowerConsumption * surge.SurgeStrength;
            }
        }

        public override string CompInspectStringExtra()
        {
            StringBuilder sb = new StringBuilder();
            sb.Append(base.CompInspectStringExtra());
            if (sb.Length > 0)
            {
                sb.AppendLine();
            }

            if (!isChillSeabed)
            {
                sb.Append("RM_AuroraCollectorNotChillSeabed".Translate());
            }
            else if (parent.Spawned && parent.Position.Roofed(parent.Map))
            {
                sb.Append("RM_AuroraCollectorRoofed".Translate());
            }
            else
            {
                RM_MapComponent_ChillAuroraSurge surge = parent.Map?.GetComponent<RM_MapComponent_ChillAuroraSurge>();
                sb.Append((surge != null && surge.IsSurgeActive)
                    ? "RM_AuroraCollectorHarvesting".Translate(surge.SurgeStrength.ToStringPercent())
                    : "RM_AuroraCollectorIdle".Translate());
            }

            return sb.ToString();
        }
    }
}
