using System.Collections.Generic;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // REACTION_MECHANISM_GENERALISE_1 step 1. The data side of
    // RM_CompReactionSource — see that class for the trigger and the full
    // flow. Same shape as RM_CompProperties_PlantAlarm (radius/cooldown/tag),
    // extended with the two pieces that comp never had: a propagation rule and
    // a response rule, each independently XML-polymorphic.
    //
    //   <comps>
    //     <li Class="RimMandrake.CreatureBehaviors.RM_CompProperties_ReactionSource">
    //       <cooldownTicks>2500</cooldownTicks>
    //       <eventBudget>8</eventBudget>
    //       <tag>SkerrelGall</tag>
    //       <response Class="RimMandrake.CreatureBehaviors.RM_ReactionResponseRule_SpawnPawns">
    //         <pawnKind>RM_Skerrel</pawnKind>
    //         <mapPopulationCap>24</mapPopulationCap>
    //       </response>
    //     </li>
    //   </comps>
    public class RM_CompProperties_ReactionSource : CompProperties
    {
        // Ticks between one trigger and the next actually doing anything —
        // same purpose as RM_CompProperties_PlantAlarm.cooldownTicks.
        public int cooldownTicks = 2500;

        // Total shared budget a single trigger grants this event. Every
        // propagation/response step spends from this SAME number — never a
        // budget of their own. The mechanism's load-bearing decision
        // (reaction_mechanism_spec.md).
        public int eventBudget = 8;

        // Free-form group identity, reserved for a future propagation rule
        // that groups sources (e.g. same-kind-within-radius, step 2). Unused
        // by the None propagation this class defaults to.
        public string tag;

        // Defaults to the explicit no-op: GREENTIDE_WASP_SWARM_1 needs no
        // propagation ("wasp propagation is the wasps themselves" — the
        // spawn response IS the spread). A future consumer overrides this in
        // XML with a real rule; this comp never hardcodes which.
        public RM_ReactionPropagationRule propagation = RM_ReactionPropagationRule_None.Instance;

        // No default — a source with nothing to do on trigger is a config
        // error, not a silent no-op (see ConfigErrors below).
        public RM_ReactionResponseRule response;

        public RM_CompProperties_ReactionSource()
        {
            compClass = typeof(RM_CompReactionSource);
        }

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string err in base.ConfigErrors(parentDef))
            {
                yield return err;
            }

            if (response == null)
            {
                yield return "RM_CompProperties_ReactionSource requires a <response> rule.";
            }

            if (eventBudget <= 0)
            {
                yield return "RM_CompProperties_ReactionSource eventBudget must be > 0.";
            }

            if (cooldownTicks < 0)
            {
                yield return "RM_CompProperties_ReactionSource cooldownTicks must be >= 0.";
            }
        }
    }
}
