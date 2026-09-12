using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // WEBWORK_KIT_BUILD_1 (webwork_kit_spec.md §5) — a trivial marker
    // DefModExtension so ANY ThingDef, in ANY mod, can be flagged as a target
    // for RM_JobGiver_ChewAnchors without touching C#. No fields: presence is
    // the whole signal, same shape as this assembly's other *Extension marker
    // classes (RM_GnawTargetExtension, RM_SeekShadeExtension).
    public class RM_ChewableExtension : DefModExtension
    {
    }
}
