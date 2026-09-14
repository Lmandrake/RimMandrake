using System.Collections.Generic;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // SCALD_MECHANICS_1 S5 build (scald_kit_spec.md S5): "placed via
    // RM_GenStep_PlacedSetPieces keyed to RUT_ScaldVent sites... a
    // vent-proximity validator." No stock ScattererValidator does
    // PROXIMITY-TO a ThingDef — only the mirror-image AVOID case exists
    // (Verse.ScattererValidator_AvoidThingsOfDef, read in full: walks
    // map.listerThings.ThingsOfDef(def) and rejects any candidate within
    // radius). This class inverts that exact shape: REQUIRE at least one
    // instance of thingDef within radius, reject otherwise.
    //
    // Generic by mechanism, not Scald-specific, matching this file's own
    // established naming register (RM_ScattererValidator_Biome names its
    // mechanism, not its first consumer) — any future kit wanting "only
    // near an already-placed Thing of def X" gets it for free.
    //
    // The one Scald-specific coupling here is deliberate and documented,
    // not hidden: it checks RM_EnvironmentalHazardsSettings.
    // bubbleSailorScattererEnabled, the WORLDGEN-AFFECTING toggle this pass
    // adds — mirroring RM_ScattererValidator_BrineShallowWater's own
    // identical shape (a mechanism named generically, whose one real
    // consumer's settings toggle it checks inline, per that class's own
    // header reasoning). A future second consumer that wants proximity
    // gating WITHOUT this specific toggle needs its own trivial subclass —
    // flagged, not silently assumed away.
    public class RM_ScattererValidator_NearThingDef : ScattererValidator
    {
        public ThingDef thingDef;

        public float radius = 6f;

        public override bool Allows(IntVec3 c, Map map)
        {
            if (!RM_EnvironmentalHazardsSettings.bubbleSailorScattererEnabled)
            {
                return false;
            }

            if (thingDef == null)
            {
                Log.ErrorOnce(
                    "[RM EnvironmentalHazards] RM_ScattererValidator_NearThingDef has no thingDef "
                    + "configured — refusing every site rather than placing globally.",
                    88344712);
                return false;
            }

            List<Thing> things = map.listerThings.ThingsOfDef(thingDef);
            for (int i = 0; i < things.Count; i++)
            {
                if (c.InHorDistOf(things[i].Position, radius))
                {
                    return true;
                }
            }

            return false;
        }
    }
}
