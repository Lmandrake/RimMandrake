using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // DEEPS_FAUNA_MECHANICS_1 (owner's own words, Soulchime: "Taming one
    // produces a soothing effect on those around it."). See
    // RM_CompTameSootheAura for the mechanism.
    public class RM_CompProperties_TameSootheAura : CompProperties
    {
        /// <summary>Cells around a TAMED carrier scanned for colonists to
        /// soothe. INVENTED: 6 — a room-scale presence, not just its own tile.</summary>
        public float radius = 6f;

        /// <summary>Memory thought granted to every colonist in radius each
        /// cycle. Defaults (in XML) to this assembly's own generic
        /// RM_TameSootheThought — content-blind, reusable by any future
        /// tamed-aura creature.</summary>
        public ThoughtDef sootheThought;

        public RM_CompProperties_TameSootheAura()
        {
            compClass = typeof(RM_CompTameSootheAura);
        }

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string err in base.ConfigErrors(parentDef))
            {
                yield return err;
            }

            if (radius <= 0f || radius >= GenRadial.MaxRadialPatternRadius)
            {
                yield return "RM_CompProperties_TameSootheAura radius must be > 0 and < GenRadial.MaxRadialPatternRadius ("
                             + GenRadial.MaxRadialPatternRadius + ").";
            }

            if (sootheThought == null)
            {
                yield return "RM_CompProperties_TameSootheAura needs a sootheThought.";
            }
        }
    }
}
