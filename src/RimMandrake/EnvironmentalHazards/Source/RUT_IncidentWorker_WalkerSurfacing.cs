using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // SCALD_MECHANICS_1 S5 spike (scald_kit_spec.md "bottom-walker
    // set-pieces"). Ban 4 ("no macro-life in the boil itself") forces v1 to
    // be a SURFACING SET-PIECE, never a resident pawn: this worker never
    // spawns a Pawn, only picks a deep-boil cell far from shore and plays a
    // sighting. TryExecuteWorker (RimWorld/IncidentWorker.cs:289, confirmed
    // real and protected virtual — same seam RUT_IncidentWorker_MirrorBreak
    // already proves in this assembly) is the whole engine risk here; the
    // rest (effecter choreography, cooldown tuning 8-20 days INVENTED, the
    // real RUT_WalkerSurfacing IncidentDef XML) is content authoring owed to
    // the full build, not an engine-fact question this spike needed to
    // resolve.
    //
    // "Far from shore": no bespoke pathing needed — GenRadial/CellFinder
    // give no ready-made "deepest point" query, so this scans a bounded
    // sample of deep-water cells and keeps the one furthest (Manhattan) from
    // the nearest map edge, which for a roughly circular crater lake (the
    // Scald, per ASHKARR_WORLD_DEFINITION.md) approximates "the deep
    // center" well enough for a set-piece and costs nothing close to a full
    // map scan.
    public class RUT_IncidentWorker_WalkerSurfacing : IncidentWorker
    {
        private const int SampleCells = 60; // bounded sample, not a full-map scan

        protected override bool TryExecuteWorker(IncidentParms parms)
        {
            Map map = (Map)parms.target;
            if (map?.Biome == null)
            {
                return false;
            }

            if (!TryFindDeepCenterCell(map, out IntVec3 cell))
            {
                return false; // no deep boil water on this map — not a Scald map, no-op
            }

            // Effecter/spray choreography is art content, owed to the full
            // build. The engine-real part — an incident that fires without
            // spawning a pawn and reports itself only as a Message, per
            // "Message not Letter after the first sighting" — is proved here.
            Messages.Message("RUT_WalkerSurfacingSighting".Translate(), new TargetInfo(cell, map), MessageTypeDefOf.NeutralEvent);
            return true;
        }

        private static bool TryFindDeepCenterCell(Map map, out IntVec3 result)
        {
            IntVec3 best = IntVec3.Invalid;
            int bestEdgeDist = -1;
            for (int i = 0; i < SampleCells; i++)
            {
                IntVec3 c = CellFinderLoose.RandomCellWith((IntVec3 x) => IsDeepBoilWater(x, map), map, 200);
                if (!c.IsValid)
                {
                    continue;
                }
                int edgeDist = DistanceToNearestEdge(c, map);
                if (edgeDist > bestEdgeDist)
                {
                    bestEdgeDist = edgeDist;
                    best = c;
                }
            }
            result = best;
            return best.IsValid;
        }

        private static bool IsDeepBoilWater(IntVec3 c, Map map)
        {
            if (!c.InBounds(map))
            {
                return false;
            }
            TerrainDef terrain = c.GetTerrain(map);
            // "the boil itself", not the margin ring: burn-bearing deep
            // water only (RUT_ScaldMargin is burn 0/0 and excluded by this
            // check without needing to name it).
            return terrain != null && terrain.IsWater && terrain.burnDamage > 0;
        }

        private static int DistanceToNearestEdge(IntVec3 c, Map map)
        {
            int fromX = System.Math.Min(c.x, map.Size.x - 1 - c.x);
            int fromZ = System.Math.Min(c.z, map.Size.z - 1 - c.z);
            return System.Math.Min(fromX, fromZ);
        }
    }
}
