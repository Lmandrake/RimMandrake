using RimMandrake.FlowWorks;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // SUMP_TAR_BELCH_EVENT_1. Owner ruling 2026-09-24, typed verbatim: "There
    // should also occasionally be a random event when a tar pit just belches
    // a huge amount of tar out all over the local terrain."
    //
    // SUMP_TAR_FIRE_NETWORK_1 part 2: the swap this class's own header used
    // to describe as owed ("find epicenter -> flood pulse") is now done. The
    // epicenter/settings/biome-restriction shape below is UNCHANGED from the
    // v1 filth-coat incident (SUMP_TAR_NASTINESS_1 S1's RM_TarCoatingUtility
    // is no longer called here, but nothing else moved) — only the payload
    // changed, from a filth splash to a real SUMP_TAR_HYDROLOGY_1-built
    // Flood_FlowWorks release seeded with RM_Fluid_Tar. That FluidDef's own
    // <coolsToGlassEdge>RM_TarGlass</coolsToGlassEdge> (FlowWorks_Fluids.xml)
    // fires automatically the moment the release self-limits (Flood_FlowWorks.
    // Tick() -> CoolFrontToGlass(), reservoir exhausted or walled in) — this
    // class needs no glass-specific code of its own, and touches no
    // IncidentDef, no settings field and no biome restriction to get it.
    public class RUT_IncidentWorker_TarPitBelch : IncidentWorker
    {
        // Bounded sample, not a full-map scan — same posture
        // RUT_IncidentWorker_WalkerSurfacing already uses in this assembly
        // for "find one cell of a particular terrain somewhere on the map."
        private const int MaxSampleTries = 300;

        protected override bool CanFireNowSub(IncidentParms parms)
        {
            if (!base.CanFireNowSub(parms))
            {
                return false;
            }
            if (!RM_EnvironmentalHazardsSettings.tarBelchEnabled)
            {
                return false;
            }
            Map map = parms.target as Map;
            return map != null && TryFindTarPitCell(map, out _);
        }

        protected override bool TryExecuteWorker(IncidentParms parms)
        {
            Map map = parms.target as Map;
            if (map == null || !TryFindTarPitCell(map, out IntVec3 epicenter))
            {
                return false; // no tar pit on this map — not a no-op bug, just nothing to belch
            }

            ThingDef floodDef = RimMandrakeFlowWorks_DefOf.RM_FluidCanalFlood;
            FluidDef tarFluid = RimMandrakeFlowWorks_DefOf.RM_Fluid_Tar;
            if (floodDef == null || tarFluid == null)
            {
                return false; // FlowWorks content missing/renamed — refuse rather than crash
            }

            // "a huge amount of tar... all over the local terrain": the same
            // settings-tunable radius the old filth coat used, reinterpreted
            // as the footprint (in tiles) this release should be able to pay
            // for. Flood_FlowWorks.PayableTiles derives tile count from
            // remainingVolume / fluidDef.volumePerTile, so working backwards
            // from "roughly a disc of this radius" gives the volume to hand
            // Configure() -- pi*r^2 tiles, tar's own volumePerTile (currently
            // 1, FlowWorks_Fluids.xml) per tile.
            float radius = RM_EnvironmentalHazardsSettings.tarBelchRadius;
            float targetTiles = Mathf.PI * radius * radius;
            float volume = Mathf.Max(1f, targetTiles) * Mathf.Max(0.0001f, tarFluid.volumePerTile);

            Flood_FlowWorks flood = (Flood_FlowWorks)ThingMaker.MakeThing(floodDef);
            flood.Configure(tarFluid, volume);
            GenSpawn.Spawn(flood, epicenter, map);

            Find.LetterStack.ReceiveLetter(
                "RUT_TarPitBelchLabel".Translate(),
                "RUT_TarPitBelchText".Translate(),
                LetterDefOf.NegativeEvent,
                new TargetInfo(epicenter, map));

            return true;
        }

        private static bool TryFindTarPitCell(Map map, out IntVec3 result)
        {
            result = CellFinderLoose.RandomCellWith(c => IsTarPit(c, map), map, MaxSampleTries);
            return result.IsValid;
        }

        private static bool IsTarPit(IntVec3 c, Map map)
        {
            if (!c.InBounds(map))
            {
                return false;
            }
            TerrainDef terrain = c.GetTerrain(map);
            return RM_MapComponent_SumpLivingMap.IsTarLiquid(terrain);
        }
    }
}
