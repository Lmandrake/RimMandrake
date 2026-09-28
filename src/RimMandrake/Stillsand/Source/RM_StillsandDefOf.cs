using RimWorld;
using Verse;

namespace RimMandrake.Stillsand
{
    // SANDBUSTER_CASTES_BUILD_1 — DefOf shortcuts for the sand-buster eruption
    // mechanism (dune_sea.md, "Amendment -- the sand busters").
    [DefOf]
    public static class RM_StillsandDefOf
    {
        // The mound -- vanilla Hive's re-skinned equivalent (thingClass Hive,
        // reused unchanged; only the def-level data -- comps, spawnablePawnKinds,
        // art -- is ours). See RM_SandBusterMound.xml.
        public static ThingDef RM_SandBusterMound;

        // The eruption marker -- vanilla TunnelHiveSpawner's re-skinned
        // equivalent. thingClass is RM_SandBusterTunnelSpawner (this assembly),
        // the one piece of the vanilla mechanism that hardcodes ThingDefOf.Hive
        // and so cannot be reused unmodified. See RM_SandBusterTunnelSpawner.cs.
        public static ThingDef RM_SandBusterTunnel;

        static RM_StillsandDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_StillsandDefOf));
        }
    }
}
