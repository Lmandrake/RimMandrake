using System.Collections.Generic;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // SUMP_TAR_NASTINESS_1 (item spec §2). RM_HediffComp_CarriedFilthExposure
    // only tunes an ALREADY-CARRIED hediff's severity — same "spike scope"
    // split HediffCompProperties_EnvironmentalExposure's own header already
    // documents for weather exposure. Something still has to hand a pawn
    // the hediff the first time it starts tracking tar; this ModExtension
    // is that opt-in, same "presence on the BiomeDef is the opt-in" idiom
    // RM_WarmGroundExtension/RM_AcceleratedRotExtension already use in this
    // assembly, so it is a harmless no-op on every biome that never carries
    // it.
    //
    //   <BiomeDef>
    //     <defName>RUT_Sump</defName>
    //     ...
    //     <modExtensions>
    //       <li Class="RimMandrake.EnvironmentalHazards.RM_CarriedFilthHediffExtension" MayRequire="mandrake.rm.environmentalhazards">
    //         <filthDef>RM_Filth_Tar</filthDef>
    //         <hediffDef>RUT_Tarred</hediffDef>
    //       </li>
    //     </modExtensions>
    //   </BiomeDef>
    //
    // MayRequire on the <li> itself, never the whole BiomeDef — per this
    // repo's own recorded trap (modextension-missing-type-discards-def):
    // an unresolvable Class inside <modExtensions> drops the WHOLE
    // containing def unless the <li> is individually gated.
    public class RM_CarriedFilthHediffExtension : DefModExtension
    {
        public ThingDef filthDef;

        public HediffDef hediffDef;

        // Severity a freshly-tarred pawn starts at — deliberately tiny;
        // RM_HediffComp_CarriedFilthExposure's own severityPerDayCarrying
        // does the real ramp from here.
        public float initialSeverity = 0.001f;

        // How often RM_MapComponent_CarriedFilthHediffLink rescans this
        // map's spawned pawns. INVENTED, matches every other periodic scan
        // in this assembly's own precedent (RM_MapComponent_WarmGround,
        // RM_MapComponent_LivingRegrowth both use 250).
        public int scanIntervalTicks = 250;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string err in base.ConfigErrors())
            {
                yield return err;
            }

            if (filthDef == null)
            {
                yield return "RM_CarriedFilthHediffExtension has no filthDef — this extension can never detect who to afflict.";
            }

            if (hediffDef == null)
            {
                yield return "RM_CarriedFilthHediffExtension has no hediffDef — this extension has nothing to give.";
            }

            if (scanIntervalTicks <= 0)
            {
                yield return "RM_CarriedFilthHediffExtension.scanIntervalTicks must be > 0.";
            }
        }
    }
}
