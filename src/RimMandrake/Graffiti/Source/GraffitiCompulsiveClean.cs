using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.Graffiti
{
    // Owner, 2026-11-07: "Clean freaks might get extra debuffs and have a mood break that makes them compulsively clean graffitti marks."
    // Personality pass, section 8: a minor break open only to someone the temperament table calls neat 2 (Very Neurotic; a mod's literal neat
    // or germaphobe trait), who can clean, with a mark to reach in the Home area, and no Graffiti break anywhere in the last 15 days.
    // In the fit, his refusal rule ("if a person hates the subject, they will refuse to clean the insult") is waived: a break isn't a choice.
    // Scrubbing a mockery still bonds its subject and the cleaner, so a neurotic who hates someone can end up rescuing them.
    public class MentalBreakWorker_GraffitiCleaning : MentalBreakWorker
    {
        public override bool BreakCanOccur(Pawn pawn)
        {
            if (!base.BreakCanOccur(pawn) || !RM_GraffitiSettings.socialEnabled) return false;
            if (GraffitiTemperament.Of(pawn).neat < 2 || pawn.WorkTypeIsDisabled(WorkTypeDefOf.Cleaning) || pawn.Map == null) return false;
            if (GameComponent_Graffiti.Get?.BreakDue != true) return false;
            return JobGiver_GraffitiCompulsiveClean.NearestMark(pawn) != null;
        }

        public override bool TryStart(Pawn pawn, string reason, bool causedByMood)
        {
            if (!base.TryStart(pawn, reason, causedByMood)) return false;
            GameComponent_Graffiti game = GameComponent_Graffiti.Get;
            if (game != null) game.lastBreak = Find.TickManager.TicksGame;
            return true;
        }
    }

    /// <summary>The painting spree's own break worker: the shared cooldown and nothing else, so a spree doesn't need a clean freak.</summary>
    public class MentalBreakWorker_GraffitiSpree : MentalBreakWorker
    {
        public override bool BreakCanOccur(Pawn pawn)
        {
            return base.BreakCanOccur(pawn) && RM_GraffitiSettings.paintingEnabled && GameComponent_Graffiti.Get?.BreakDue == true;
        }

        public override bool TryStart(Pawn pawn, string reason, bool causedByMood)
        {
            if (!base.TryStart(pawn, reason, causedByMood)) return false;
            GameComponent_Graffiti game = GameComponent_Graffiti.Get;
            if (game != null) game.lastBreak = Find.TickManager.TicksGame;
            return true;
        }
    }

    /// <summary>Scrubbing marks off the walls until there are none in reach, or six are gone: the cap that stops one fit erasing a colony's history.</summary>
    public class MentalState_GraffitiCompulsiveClean : MentalState
    {
        public int scrubbed;
        public const int MaxScrubs = 6;
        // Live pass 13: Mo's fit sent a message per scrub, six in under a game hour. The first scrub tells the player what's going on,
        // the end says how many came off; the rest go to the log.
        public bool told;

        public override void PostEnd()
        {
            base.PostEnd();
            if (scrubbed > 0 && RM_GraffitiSettings.socialMessagesEnabled && pawn.Spawned && pawn.Faction == Faction.OfPlayer)
            {
                GraffitiSocial.Tell(pawn.LabelShort + " has calmed down after scrubbing " + scrubbed + (scrubbed == 1 ? " mark" : " marks") + " off the walls.", pawn, MessageTypeDefOf.SilentInput);
            }
        }

        public void Notify_Scrubbed()
        {
            scrubbed++;
            if (scrubbed >= MaxScrubs) RecoverFromState();
        }

        public override void MentalStateTick(int delta)
        {
            base.MentalStateTick(delta);
            if (pawn.MentalState == this && pawn.IsHashIntervalTick(250, delta) && age > 600 && JobGiver_GraffitiCompulsiveClean.NearestMark(pawn) == null)
            {
                RecoverFromState();
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref scrubbed, "rmScrubbed");
            Scribe_Values.Look(ref told, "rmFitTold");
        }
    }

    /// <summary>The nearest mark in the Home area this pawn can reach, of any kind and by anyone, and the scrub job for it.</summary>
    public class JobGiver_GraffitiCompulsiveClean : ThinkNode_JobGiver
    {
        internal static Filth_Mark NearestMark(Pawn pawn)
        {
            MapComponent_GraffitiSocial comp = MapComponent_GraffitiSocial.For(pawn.Map);
            if (comp == null) return null;
            Filth_Mark best = null;
            float bestDist = float.MaxValue;
            foreach (Filth_Mark m in comp.marks)
            {
                if (!m.Spawned || !pawn.Map.areaManager.Home[m.Position]) continue;
                float d = (m.Position - pawn.Position).LengthHorizontalSquared;
                if (d >= bestDist) continue;
                if (!pawn.CanReserveAndReach(m.Position, PathEndMode.OnCell, Danger.Some)) continue;
                best = m;
                bestDist = d;
            }
            return best;
        }

        protected override Job TryGiveJob(Pawn pawn)
        {
            Filth_Mark mark = NearestMark(pawn);
            return mark == null ? null : JobMaker.MakeJob(RMGraffitiDefOf.RM_ScrubMark, mark, mark.Position);
        }
    }
}
