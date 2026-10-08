using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Stillsand
{
    // SANDBUSTER_CASTES_BUILD_1 — the sand busters (dune_sea.md, "Amendment —
    // the sand busters", owner-ruled 2026-09-24 at NIGHTSIDE_ICE_DESIGN_SITTING_1;
    // castes drafted at the 2026-09-27 STILLSAND_DESIGN_SITTING_1, Q9/Q14).
    //
    // A near-verbatim re-skin of RimWorld.IncidentWorker_Infestation (read via
    // RimSage against the decompiled 1.6 source, 2026-09-27) — same points math,
    // same letter/slowdown behaviour, same escalating-mound shape. The two
    // differences from copying that class outright:
    //
    //   1. RimWorld.HiveUtility.TotalSpawnedHivesCount(map) counts
    //      map.listerThings.ThingsOfDef(ThingDefOf.Hive) — an EXACT def match,
    //      not a type check. RM_SandBusterMound is a different ThingDef (even
    //      though its thingClass is the same RimWorld.Hive), so that vanilla
    //      cap-counter would always read 0 for us and never actually cap
    //      anything. This worker re-derives the same 30-mound cap against our
    //      own def instead.
    //   2. InfestationUtility.SpawnTunnels hardcodes ThingDefOf.TunnelHiveSpawner.
    //      SpawnMounds() below is the same shape, spawning
    //      RM_StillsandDefOf.RM_SandBusterTunnel instead — whose thingClass
    //      (RM_SandBusterTunnelSpawner) is itself a TunnelHiveSpawner subclass,
    //      so the reused CompSpawnerHives.FindChildHiveLocation() and
    //      InfestationCellFinder.TryFindCell()'s `is Hive`/`is TunnelHiveSpawner`
    //      type checks still correctly see our own erupted mounds/markers as
    //      blockers for later placements in the same call.
    //
    // Confinement to the Dune Sea is NOT done here — it is the IncidentDef's own
    // <allowedBiomes><li>RM_Stillsand</li></allowedBiomes>, checked engine-side
    // in IncidentWorker.CanFireNow before CanFireNowSub ever runs (RimWorld/
    // IncidentDef.cs + IncidentWorker.cs, RimSage-read). No C# biome check is
    // needed or present in this class.
    public class RM_IncidentWorker_SandBusterEruption : IncidentWorker
    {
        // Mirrors IncidentWorker_Infestation.HivePoints exactly (one mound per
        // 220 threat points, minimum one).
        public const float MoundPoints = 220f;

        public const int MaxMoundsPerMap = 30;

        public static readonly SimpleCurve PointsFactorCurve = new SimpleCurve
        {
            new CurvePoint(0f, 0.7f),
            new CurvePoint(5000f, 0.45f)
        };

        // STILLSAND_RETURN_RITUAL_1: unpaid water debt weights the eruption up.
        public override float ChanceFactorNow(IIncidentTarget target)
        {
            float f = base.ChanceFactorNow(target);
            return target is Map map ? f * RM_StillsandWater.IncidentChanceFactor(map, def) : f;
        }

        protected override bool CanFireNowSub(IncidentParms parms)
        {
            Map map = (Map)parms.target;
            if (!base.CanFireNowSub(parms))
            {
                return false;
            }
            if (Faction.OfInsects == null)
            {
                return false;
            }
            if (map.listerThings.ThingsOfDef(RM_StillsandDefOf.RM_SandBusterMound).Count >= MaxMoundsPerMap)
            {
                return false;
            }
            return InfestationCellFinder.TryFindCell(out IntVec3 cell, map);
        }

        protected override bool TryExecuteWorker(IncidentParms parms)
        {
            Map map = (Map)parms.target;
            parms.points *= PointsFactorCurve.Evaluate(parms.points);
            int moundCount = Mathf.Max(GenMath.RoundRandom(parms.points / MoundPoints), 1);
            // The per-map cap is a real cap: existing mounds and tunnels still digging count against it.
            int room = MaxMoundsPerMap
                       - map.listerThings.ThingsOfDef(RM_StillsandDefOf.RM_SandBusterMound).Count
                       - map.listerThings.ThingsOfDef(RM_StillsandDefOf.RM_SandBusterTunnel).Count;
            if (room <= 0)
            {
                return false;
            }
            moundCount = Mathf.Min(moundCount, room);
            Thing thing = SpawnMounds(moundCount, map, parms.infestationLocOverride);
            if (thing == null)
            {
                return false;
            }
            SendStandardLetter(parms, thing);
            Find.TickManager.slower.SignalForceNormalSpeedShort();
            return true;
        }

        // Same shape as InfestationUtility.SpawnTunnels, targeting
        // RM_SandBusterTunnel instead of ThingDefOf.TunnelHiveSpawner.
        private static Thing SpawnMounds(int moundCount, Map map, IntVec3? overrideLoc)
        {
            IntVec3 loc;
            if (overrideLoc.HasValue)
            {
                loc = overrideLoc.Value;
            }
            else if (!InfestationCellFinder.TryFindCell(out loc, map))
            {
                return null;
            }
            if (!loc.IsValid)
            {
                return null;
            }

            ThingDef tunnelDef = RM_StillsandDefOf.RM_SandBusterTunnel;
            ThingDef moundDef = RM_StillsandDefOf.RM_SandBusterMound;
            CompProperties_SpawnerHives hiveProps = moundDef.GetCompProperties<CompProperties_SpawnerHives>();

            Thing spawnedMarker = GenSpawn.Spawn(ThingMaker.MakeThing(tunnelDef), loc, map, WipeMode.FullRefund);
            for (int i = 0; i < moundCount - 1; i++)
            {
                IntVec3 childLoc = CompSpawnerHives.FindChildHiveLocation(
                    spawnedMarker.Position, map, moundDef, hiveProps,
                    ignoreRoofedRequirement: false, allowUnreachable: true);
                if (childLoc.IsValid)
                {
                    spawnedMarker = GenSpawn.Spawn(ThingMaker.MakeThing(tunnelDef), childLoc, map, WipeMode.FullRefund);
                }
            }
            return spawnedMarker;
        }
    }
}
