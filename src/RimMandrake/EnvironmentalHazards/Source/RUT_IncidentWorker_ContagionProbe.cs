using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // FORGE_MECHANICS_1 F5 "the Contagion die-off ring" (forge_kit_spec.md
    // F5: "RUT_ContagionProbe IncidentDef (weighted only into Forge biomes,
    // MTB-ish commonality... spawning a cluster of RUT_DyingCreep plant-
    // things at a map edge... Letter on arrival, quiet death.").
    //
    // RUT_-prefixed but living in the shared EnvironmentalHazards assembly,
    // same posture as RUT_IncidentWorker_MirrorBreak (FEVER_WOOD_MECHANICS_1
    // F2) — campaign-specific content class, generic-mechanism assembly.
    //
    // Hardcodes the Forge biome defName directly rather than an XML-settable
    // biome list: the kit spec's own gate is singular ("weighted only into
    // Forge biomes" — RUT_TheForge is the ONE merged BiomeDef per
    // BIOME_OWNERSHIP_WAVE_1, not three separate zone defs), so there is
    // nothing to generalize the way RM_GenStep_EdgeBandFilth's biome list
    // is (that class is built to be reused by a future biome; this worker
    // is Forge content, not a shared mechanism).
    public class RUT_IncidentWorker_ContagionProbe : IncidentWorker
    {
        // INVENTED, F5 spec: "a cluster."
        private const int ClusterCountMin = 3;
        private const int ClusterCountMax = 6;
        private const float ClusterRadius = 4f;

        protected override bool CanFireNowSub(IncidentParms parms)
        {
            if (!base.CanFireNowSub(parms) || !(parms.target is Map map))
            {
                return false;
            }

            return map.Biome != null && map.Biome.defName == "RUT_TheForge";
        }

        protected override bool TryExecuteWorker(IncidentParms parms)
        {
            if (!(parms.target is Map map))
            {
                return false;
            }

            ThingDef dyingCreep = DefDatabase<ThingDef>.GetNamedSilentFail("RUT_DyingCreep");
            if (dyingCreep == null)
            {
                return false; // content not deployed — never a hard error over it
            }

            if (!CellFinder.TryFindRandomEdgeCellWith(
                (IntVec3 c) => c.Standable(map),
                map,
                CellFinder.EdgeRoadChance_Ignore,
                out IntVec3 edgeCell))
            {
                return false;
            }

            bool CellOk(IntVec3 c)
            {
                return c.InBounds(map)
                    && c.Standable(map)
                    && dyingCreep.CanEverPlantAt(c, map, canWipePlantsExceptTree: false, checkMapTemperature: false);
            }

            int count = Rand.RangeInclusive(ClusterCountMin, ClusterCountMax);
            int spawned = 0;
            for (int i = 0; i < count; i++)
            {
                if (GenRadial.RadialCellsAround(edgeCell, ClusterRadius, useCenter: true).TryRandomElement(CellOk, out IntVec3 cell))
                {
                    GenSpawn.Spawn(dyingCreep, cell, map);
                    spawned++;
                }
            }

            if (spawned == 0)
            {
                return false; // no legal cell found anywhere in the cluster radius — quiet no-op, not an error
            }

            SendStandardLetter(
                "RUT_ContagionProbe".Translate(),
                "RUT_ContagionProbeDesc".Translate(),
                LetterDefOf.NeutralEvent,
                parms,
                new TargetInfo(edgeCell, map));

            return true;
        }
    }
}
