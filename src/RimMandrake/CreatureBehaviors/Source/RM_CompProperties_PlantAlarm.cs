using System.Collections.Generic;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // ROT_GUARDIAN_GROVES_1 (rot_kit_spec.md M6). The data side of
    // RM_CompPlantAlarm — see that class for the XML usage example and the
    // full behaviour.
    public class RM_CompProperties_PlantAlarm : CompProperties
    {
        // Cells around the alarm source scanned for a responder each trigger.
        // INVENTED: 18 — wide enough that "the mycelial network" reads as a
        // grove-wide response, not a single tile.
        public float radius = 18f;

        // Matched against RM_AlarmResponderExtension.tag on a candidate
        // pawn's race. Blank (the default) matches any race carrying the
        // extension at all, regardless of its own tag value.
        public string tag;

        // Ticks between one trigger and the next actually doing anything —
        // a guardian plant hit by a burst of shots or harvested repeatedly
        // in the same fight should not re-summon every single hit.
        public int cooldownTicks = 2500;

        public RM_CompProperties_PlantAlarm()
        {
            compClass = typeof(RM_CompPlantAlarm);
        }

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string err in base.ConfigErrors(parentDef))
            {
                yield return err;
            }

            if (radius <= 0f || radius >= GenRadial.MaxRadialPatternRadius)
            {
                yield return "RM_CompProperties_PlantAlarm radius must be > 0 and < GenRadial.MaxRadialPatternRadius ("
                             + GenRadial.MaxRadialPatternRadius + ").";
            }

            if (cooldownTicks < 0)
            {
                yield return "RM_CompProperties_PlantAlarm cooldownTicks must be >= 0.";
            }
        }
    }
}
