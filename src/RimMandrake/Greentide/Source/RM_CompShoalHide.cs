// GREENTIDE_ILLISK_BUILD_1 - the illisk's hide: near-immune to everything but blasts.
// ThingWithComps.PreApplyDamage calls PostPreApplyDamage BEFORE Pawn's health sees the damage (RimSage-read, decompiled 1.6),
// so scaling dinfo here needs no Harmony. Armour cannot do this job: DamageDefOf.Bomb uses the same Sharp armour category as
// bullets and blades, so any armour that stops a bullet stops a blast too.
using System.Collections.Generic;
using Verse;

namespace RimMandrake.Greentide
{
    public static class RM_ShoalKernel
    {
        // Blast damage passes whole; everything else is scaled to `factor`. Feature off: nothing is scaled.
        public static float Factor(bool featureOn, bool isBlast, float factor)
        {
            if (!featureOn || isBlast) return 1f;
            return factor < 0f ? 0f : (factor > 1f ? 1f : factor);
        }
    }

    public class CompProperties_ShoalHide : CompProperties
    {
        public List<DamageDef> blastDamageDefs = new List<DamageDef>();

        public CompProperties_ShoalHide()
        {
            compClass = typeof(RM_CompShoalHide);
        }
    }

    public class RM_CompShoalHide : ThingComp
    {
        private CompProperties_ShoalHide Props => (CompProperties_ShoalHide)props;

        public override void PostPreApplyDamage(ref DamageInfo dinfo, out bool absorbed)
        {
            absorbed = false;
            bool blast = Props.blastDamageDefs.Contains(dinfo.Def);
            float f = RM_ShoalKernel.Factor(RM_GreentideSettings.shoalHideEnabled, blast, RM_GreentideSettings.shoalNonBlastFactor);
            if (f < 1f) dinfo.SetAmount(dinfo.Amount * f);
        }
    }
}
