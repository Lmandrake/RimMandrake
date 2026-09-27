using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.TerminalBiomes
{
    // TWILIGHT_DANGER_LIGHTWEB_1 §D2b. Walks to the target glower and
    // periodically shrinks its GlowRadius, destroying it once fed out.
    //
    // CompGlower.GlowRadius's own setter only stores the override and does
    // NOT re-register with the map's GlowGrid — the same fact
    // RM_Comp_WarblingGlow's own header already documents for this exact
    // API (EnvironmentalHazards/Source/RM_Comp_WarblingGlow.cs) — so every
    // change here calls CompGlower.ForceRegister(map) explicitly, mirroring
    // that comp's own Apply() method.
    //
    // "Loudly" (design D2c ruling C4, the sun-sphere): every feed sends a
    // Message the moment it starts, and the eventual destruction sends a
    // full Letter — real signal on every target, not only the sun-sphere
    // specifically (that def does not exist yet; this stays generic so it
    // covers it automatically once it does).
    public class RM_JobDriver_FeedOnGlow : JobDriver
    {
        private int ticksToNextFeed;
        private bool announcedThisJob;

        private RM_SeekGlowExtension Ext => pawn.def?.GetModExtension<RM_SeekGlowExtension>();

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.targetA.Thing, job, 1, -1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            RM_SeekGlowExtension ext = Ext;
            if (ext == null)
            {
                yield break;
            }

            this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);

            Toil feed = ToilMaker.MakeToil("MakeNewToils");
            feed.initAction = delegate
            {
                ticksToNextFeed = Mathf.Max(1, ext.ticksBetweenFeeds);
                if (!announcedThisJob)
                {
                    announcedThisJob = true;
                    Thing target = job.targetA.Thing;
                    if (target != null && target.Spawned)
                    {
                        Messages.Message("RM_SuulkFeedingStarted".Translate(target.LabelShort),
                            new TargetInfo(target.Position, target.Map), MessageTypeDefOf.CautionInput);
                    }
                }
            };
            feed.tickIntervalAction = delegate(int delta)
            {
                Thing target = job.targetA.Thing;
                if (target == null || target.Destroyed || !target.Spawned)
                {
                    ReadyForNextToil();
                    return;
                }
                CompGlower glower = target.TryGetComp<CompGlower>();
                if (glower == null)
                {
                    ReadyForNextToil();
                    return;
                }

                ticksToNextFeed -= delta;
                if (ticksToNextFeed > 0)
                {
                    return;
                }
                ticksToNextFeed = Mathf.Max(1, ext.ticksBetweenFeeds);

                float newRadius = Mathf.Max(0f, glower.GlowRadius - ext.glowRadiusLossPerFeed);
                glower.GlowRadius = newRadius;
                glower.ForceRegister(target.Map);

                if (newRadius <= ext.destroyBelowRadius)
                {
                    Map map = target.Map;
                    TargetInfo info = new TargetInfo(target.Position, map);
                    string label = target.LabelShort;
                    target.Destroy(DestroyMode.Vanish);
                    Find.LetterStack.ReceiveLetter("RM_SuulkFedOutLabel".Translate(),
                        "RM_SuulkFedOutText".Translate(label), LetterDefOf.NegativeEvent, info);
                    ReadyForNextToil();
                }
            };
            feed.defaultCompleteMode = ToilCompleteMode.Never;
            feed.WithProgressBar(TargetIndex.A, () =>
            {
                Thing target = job.targetA.Thing;
                CompGlower glower = target?.TryGetComp<CompGlower>();
                CompProperties_Glower props = glower?.Props;
                if (glower == null || props == null || props.glowRadius <= 0f)
                {
                    return 1f;
                }
                return 1f - Mathf.Clamp01(glower.GlowRadius / props.glowRadius);
            });
            feed.FailOnCannotTouch(TargetIndex.A, PathEndMode.Touch);
            yield return feed;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref ticksToNextFeed, "ticksToNextFeed", 0);
            Scribe_Values.Look(ref announcedThisJob, "announcedThisJob", false);
        }
    }
}
