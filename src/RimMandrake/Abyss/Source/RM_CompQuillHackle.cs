using RimWorld;
using Verse;
using Verse.AI;
using Verse.Sound;

namespace RimMandrake.Abyss
{
    // ABYSS_DONOR_BEASTS_FREED_1. The drokattak (cast bible 2026-10-01 §4C): "it raises them in a
    // clattering hackle before it lunges and pins. It does not throw them." An ambusher, not a pursuer.
    // When a hunt or melee attack job begins, the drokattak stops for a moment (a self-stun of hackleTicks),
    // the text "quills rattle" rises over it and a rattle plays: the warning is the one beat a player gets.
    // Once per job; a new job may hackle again. Setting drokattakHackleEnabled.
    public class CompProperties_RM_QuillHackle : CompProperties
    {
        public int hackleTicks = 75;
        public SoundDef rattleSound;

        public CompProperties_RM_QuillHackle()
        {
            compClass = typeof(CompRM_QuillHackle);
        }
    }

    public class CompRM_QuillHackle : ThingComp
    {
        private int lastJobId = -1;

        private CompProperties_RM_QuillHackle Props => (CompProperties_RM_QuillHackle)props;

        public override void CompTick()
        {
            if (!parent.IsHashIntervalTick(20)) return;
            Pawn pawn = parent as Pawn;
            if (pawn == null || !pawn.Spawned || pawn.Dead || pawn.Downed) return;
            if (!RM_AbyssSettings.drokattakHackleEnabled) return;
            Job job = pawn.CurJob;
            if (job == null || job.loadID == lastJobId) return;
            if (job.def != JobDefOf.PredatorHunt && job.def != JobDefOf.AttackMelee) return;
            lastJobId = job.loadID;
            Hackle(pawn);
        }

        public void Hackle(Pawn pawn)
        {
            MoteMaker.ThrowText(pawn.DrawPos, pawn.Map, "quills rattle", 3f);
            Props.rattleSound?.PlayOneShot(new TargetInfo(pawn.Position, pawn.Map));
            pawn.stances?.stunner?.StunFor(Props.hackleTicks, pawn, addBattleLog: false, showMote: false);
        }

        public override void PostExposeData()
        {
            Scribe_Values.Look(ref lastJobId, "lastHackleJob", -1);
        }
    }
}
