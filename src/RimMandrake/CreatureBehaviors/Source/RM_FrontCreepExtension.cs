using System.Collections.Generic;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // WEBWORK_KIT_BUILD_1, mechanic 6 (webwork_kit_spec.md §6) — attach to a
    // BiomeDef to make RM_MapComponent_FrontCreep advance THAT biome's content
    // onto any neighboring map. Content-defined defNames are soft (resolved
    // at runtime via DefDatabase.GetNamedSilentFail) so this generic engine
    // class never hard-references a biome's own Things.
    public class RM_FrontCreepExtension : DefModExtension
    {
        // defNames of ThingDefs to scatter along the advancing band (e.g. the
        // roster's web/anchor/gutter Things). One is picked at random per
        // spawned cell.
        public List<string> frontThingDefNames;

        // ❓INVENTED (spec §6: "advance rate, band depth, density" all
        // unspecified) — a live-balance pass on a quicktest map is owed.
        public int advanceIntervalTicks = 60000; // ~1 in-game day
        public int maxBandDepth = 10;
        public float spawnDensity = 0.15f;
    }
}
