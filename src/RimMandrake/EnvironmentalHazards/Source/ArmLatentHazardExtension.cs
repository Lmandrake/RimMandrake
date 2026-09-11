using System.Collections.Generic;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // ALPHA_MECHANICS_KIT_1 item 5's pair — the data side of
    // GameCondition_ArmLatentHazard. See that file for the XML example.
    public class ArmLatentHazardExtension : DefModExtension
    {
        // The latent hediff. Its own comps carry whatever the hazard
        // actually does; this extension only decides who gets it and when.
        public HediffDef hediffToApply;

        public int intervalTicks = 6000;

        // When true the first sweep runs on the tick the condition starts
        // rather than one interval later.
        public bool armImmediately;

        public float initialSeverity;

        // Per-eligible-pawn probability, so a condition can creep through a
        // population rather than arming it all at once.
        public float chancePerPawn = 1f;

        public LatentHazardTargets targets = LatentHazardTargets.Animals;

        public PawnTargetKind affects = PawnTargetKind.All;
        public List<ThingDef> immuneThingDefs;
        public List<PawnKindDef> immunePawnKinds;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string err in base.ConfigErrors())
            {
                yield return err;
            }

            if (hediffToApply == null)
            {
                yield return "ArmLatentHazardExtension has no hediffToApply — the condition would sweep the map and change nothing.";
            }

            if (intervalTicks < 1)
            {
                yield return "ArmLatentHazardExtension intervalTicks must be >= 1.";
            }
        }
    }

    public enum LatentHazardTargets
    {
        Animals,
        Humanlikes,
        NonPlayerFactionOnly,
        AllPawns,
    }
}
