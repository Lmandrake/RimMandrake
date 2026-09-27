using RimWorld;
using Verse;

namespace RimMandrake.TerminalBiomes
{
    // TWILIGHT_LIGHT_ECONOMY_1 §3.2. "CompGlower registers its light at the
    // position it was lit and never re-registers on movement — a walking
    // glower strands its light." Fix verified against our own
    // RM_Comp_WarblingGlow (EnvironmentalHazards): GlowRadius's setter only
    // stores the value; ForceRegister(map) is CompGlower's own public API
    // for "the light moved, re-register it" — same call, different trigger
    // (position change instead of a radius change).
    //
    // Shared by every mover the spec names: the lit fish shoal (niim),
    // liiru, kiruun patches, a tame liiru following its handler, the kept
    // waelune, the drifting orrilith — and any future glowing creature on
    // any floor. The clipped lamps deliberately do NOT carry this: they are
    // buildings that go dark in transit (§2.1), which is the cheaper,
    // correct answer for them.
    public class RM_CompProperties_GlowerMobile : CompProperties
    {
        public RM_CompProperties_GlowerMobile()
        {
            compClass = typeof(RM_Comp_GlowerMobile);
        }

        public override System.Collections.Generic.IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string err in base.ConfigErrors(parentDef))
            {
                yield return err;
            }
            if (parentDef.GetCompProperties<CompProperties_Glower>() == null)
            {
                yield return "RM_CompProperties_GlowerMobile requires a sibling CompProperties_Glower on the same ThingDef.";
            }
        }
    }

    public class RM_Comp_GlowerMobile : ThingComp
    {
        private CompGlower glowerCache;
        private IntVec3 lastRegisteredPosition = IntVec3.Invalid;

        public RM_CompProperties_GlowerMobile Props => (RM_CompProperties_GlowerMobile)props;

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            glowerCache = parent.GetComp<CompGlower>();
            lastRegisteredPosition = parent.Position;
        }

        // CompTickRare (~250 ticks, the ThingComp default rare cadence) is
        // plenty: a walking creature moves at most one cell every several
        // ticks, and a stale registration for a quarter of a second is
        // invisible.
        public override void CompTickRare()
        {
            CheckAndReregister();
        }

        private void CheckAndReregister()
        {
            if (glowerCache == null || !parent.Spawned)
            {
                return;
            }
            if (parent.Position == lastRegisteredPosition)
            {
                return;
            }
            lastRegisteredPosition = parent.Position;
            glowerCache.ForceRegister(parent.Map);
        }
    }
}
