using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // GREENTIDE_MECHANICS_2 M6 build, feller 3 ("gnawed from below"). Marker
    // + tuning extension on a Gnawer's race ThingDef — the same presence-only
    // idiom RUT_Placeholder_SumpMouseRace's own RM_DreadAvoidWanderExtension
    // already established in this repo (globally-inserted JobGiver, no-op for
    // any race that doesn't carry this).
    //
    //   <ThingDef ParentName="AnimalThingBase">
    //     <defName>RUT_Placeholder_GreentideGnawerRace</defName>
    //     ...
    //     <modExtensions>
    //       <li Class="RimMandrake.EnvironmentalHazards.RM_GnawTreeBaseExtension">
    //         <searchRadius>40</searchRadius>
    //         <chewTicksToFell>2400</chewTicksToFell>
    //       </li>
    //     </modExtensions>
    //   </ThingDef>
    public class RM_GnawTreeBaseExtension : DefModExtension
    {
        public float searchRadius = 40f;

        // INVENTED — kit spec gives no figure for how long a Gnawer works a
        // trunk before it goes down; long enough that a colonist who spots
        // the pawn at it has a real chance to intervene.
        public int chewTicksToFell = 2400;
    }
}
