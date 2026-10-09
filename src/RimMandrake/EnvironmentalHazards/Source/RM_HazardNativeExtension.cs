using System.Collections.Generic;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    /// <summary>HAZARD_NATIVE_TAG_1. One generic "born here" tag on a race: it names the hazards the creature is native
    /// to ("Scald", ...). A hazard def sets <c>nativeTag</c> and HazardTargeting.Affects skips any pawn whose race lists
    /// that tag, so a new native is ONE line on the creature instead of an edit to every hazard's own immunity list.
    /// The water half of the Scald's immunity (terrain hediff giver set) is a different mechanism and is unaffected.</summary>
    public class RM_HazardNativeExtension : DefModExtension
    {
        public List<string> hazardTags;

        public static bool IsNativeTo(ThingDef race, string tag)
        {
            if (race == null || tag.NullOrEmpty())
            {
                return false;
            }
            RM_HazardNativeExtension ext = race.GetModExtension<RM_HazardNativeExtension>();
            return ext != null && ext.hazardTags != null && ext.hazardTags.Contains(tag);
        }

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string err in base.ConfigErrors())
            {
                yield return err;
            }
            if (hazardTags.NullOrEmpty())
            {
                yield return "RM_HazardNativeExtension has no hazardTags, so it makes the creature native to nothing.";
            }
        }
    }
}
