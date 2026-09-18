namespace RimMandrake.EnvironmentalHazards
{
    // ROT_SHEEN_WEATHER_1 (rot_kit_spec.md M1, "The Sheen"). RUT_SheenCoating
    // carries this instead of the base HediffCompProperties_
    // EnvironmentalExposure so its accrual has a dedicated Mod Settings
    // switch (RM_EnvironmentalHazardsSettings.sheenExposureEnabled) that
    // does NOT also silence RUT_MiasmaExposure or any other future consumer
    // of the shared base pair — same "RUT_-specific subclass wraps a shared
    // mechanism in its own toggle" shape RUT_IncidentWorker_SporeCloud
    // already established for RUT_SporeCloud's incident weight.
    //
    //   <HediffDef>
    //     <defName>RUT_SheenCoating</defName>
    //     ...
    //     <comps>
    //       <li Class="RimMandrake.EnvironmentalHazards.HediffCompProperties_SheenExposure">
    //         <onlyDuringWeathers>
    //           <li>RUT_SheenFall</li>
    //           <li>RUT_SheenStorm</li>
    //           <li>RUT_SheenMist</li>
    //         </onlyDuringWeathers>
    //         <severityPerDayExposed>0.667</severityPerDayExposed>
    //         <severityPerDayUnexposed>-0.3</severityPerDayUnexposed>
    //         <protectionStat>RUT_SheenProtection</protectionStat>
    //         <minDriveFactor>0.05</minDriveFactor>
    //         <immunityHediff>RUT_SheenSymbiosis</immunityHediff>
    //       </li>
    //     </comps>
    //   </HediffDef>
    public class HediffCompProperties_SheenExposure : HediffCompProperties_EnvironmentalExposure
    {
        public HediffCompProperties_SheenExposure()
        {
            compClass = typeof(RM_HediffComp_SheenExposure);
        }
    }

    public class RM_HediffComp_SheenExposure : RM_HediffComp_EnvironmentalExposure
    {
        public override float SeverityChangePerDay()
        {
            if (!RM_EnvironmentalHazardsSettings.sheenExposureEnabled)
            {
                return 0f; // mod option: Sheen exposure disabled — the reskin itself stays either way
            }

            return base.SeverityChangePerDay();
        }
    }
}
