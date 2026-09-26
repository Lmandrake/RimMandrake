using System;
using RimWorld;
using Verse;
using Verse.Sound;

namespace RimMandrake.EnvironmentalHazards
{
    //   <comps>
    //     <li Class="RimMandrake.EnvironmentalHazards.RM_HediffCompProperties_LocatableCall">
    //       <callSound>Pawn_Frog_Call</callSound>
    //       <callIntervalTicksRange>900~1500</callIntervalTicksRange>
    //     </li>
    //   </comps>
    //
    // WARDEN_MOTHER_BEFRIENDING_1 spec step 3: "the young CALLS. Audible,
    // locatable, and it does not stop" — the one piece of pure
    // fiction-to-mechanism work that item's own table names. Kept on the
    // HEDIFF rather than on a bespoke pawn/comp: RUT_StrandedDeformation is
    // carried by an ordinary nursery juvenile regardless of HOW it was
    // stranded (a surge cutting off a pool, RM_StrandingPoolsExtension's own
    // spawner, or a warden mother's own spawn-linked young), so putting the
    // call here means every stranded young calls, not only the ones spawned
    // by one particular mechanism — no Miasma-specific or warden-specific
    // coupling anywhere in this file.
    //
    // callSound plays via vanilla's own positional audio (SoundInfo.InMap on
    // the pawn's own position) — genuinely locatable by ear the same way any
    // other in-map SoundDef is, with zero new C# audio plumbing. Reuses the
    // vanilla animal-call SoundDef Pawn_Frog_Call as the XML default (an
    // amphibious creature's own call, thematically apt for "gills going
    // leathery, fins splaying") rather than inventing a new sound asset.
    public class RM_HediffCompProperties_LocatableCall : HediffCompProperties
    {
        public SoundDef callSound;

        public IntRange callIntervalTicksRange = new IntRange(900, 1500);

        public RM_HediffCompProperties_LocatableCall()
        {
            compClass = typeof(RM_HediffComp_LocatableCall);
        }
    }

    public class RM_HediffComp_LocatableCall : HediffComp
    {
        private int nextCallTick = -1;

        public RM_HediffCompProperties_LocatableCall Props => (RM_HediffCompProperties_LocatableCall)props;

        public override void CompPostTick(ref float severityAdjustment)
        {
            base.CompPostTick(ref severityAdjustment);

            Pawn pawn = parent.pawn;
            if (pawn == null || !pawn.Spawned || pawn.Dead || pawn.Map == null || Props.callSound == null)
            {
                return;
            }

            int tick = Find.TickManager.TicksGame;
            if (nextCallTick < 0)
            {
                nextCallTick = tick + Props.callIntervalTicksRange.RandomInRange;
                return;
            }

            if (tick < nextCallTick)
            {
                return;
            }

            Props.callSound.PlayOneShot(new TargetInfo(pawn.Position, pawn.Map));
            nextCallTick = tick + Props.callIntervalTicksRange.RandomInRange;
        }

        public override void CompExposeData()
        {
            base.CompExposeData();
            Scribe_Values.Look(ref nextCallTick, "nextCallTick", -1);
        }
    }
}
