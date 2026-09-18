using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // ROT_GUARDIAN_GROVES_1 (rot_kit_spec.md M6, "the network alarm").
    //
    // Content-blind marker, same shape as RM_WoundLinkExtension (M7): a
    // race's own ThingDef opts in with a tag string, and RM_CompPlantAlarm
    // (this same assembly) never hardcodes a species. This mod ships zero
    // content of its own — BIOME_FAUNA_ASSIGNMENT_SITTING_1 (or any future
    // content pack) is what actually attaches this to a race via an XML
    // patch, the same way ShipVermin attaches RM_VerminPressureExtension.
    //
    //   <ThingDef>
    //     <defName>SomeHybridFauna</defName>
    //     ...
    //     <modExtensions>
    //       <li Class="RimMandrake.CreatureBehaviors.RM_AlarmResponderExtension">
    //         <tag>RotGroveGuardian</tag>
    //       </li>
    //     </modExtensions>
    //   </ThingDef>
    public class RM_AlarmResponderExtension : DefModExtension
    {
        // Free-form group identity. RM_CompPlantAlarm.tag blank matches ANY
        // race carrying this extension regardless of its own tag value;
        // a non-blank comp tag matches only a race whose tag is identical.
        // A race with no RM_AlarmResponderExtension at all never answers any
        // alarm, no matter what tag a comp asks for.
        public string tag;
    }
}
