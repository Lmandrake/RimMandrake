using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Wasteland
{
    /// <summary>
    /// WASTELAND_MECHANICS_BUILD_1 §2 — the processor comp (Sloghog -> bezoars,
    /// Sootgrazer -> soot bricks). A CompMilkable subclass, so vanilla's
    /// WorkGiver_Milk / JobDriver_Milk collect it with no new job (WorkGiver_Milk
    /// resolves TryGetComp&lt;CompMilkable&gt;(), which matches a subclass).
    ///
    /// Fill rate is gated on the ground under the animal: on FEED ground
    /// (Biotech-polluted cell, toxic terrain, or — for the ash-eater — drifted
    /// fall at least <c>feedSandDepth</c> deep) it fills at the full
    /// <c>milkIntervalDays</c> rate; off it, at <c>offFeedRateFactor</c>.
    /// Without Biotech there is no pollution to read, so a pollution feeder
    /// falls back to time alone (full rate), per the spec.
    ///
    /// Pollution CONSUMPTION (owner: "living furnace approved + extended to
    /// pollution emission/consumption/usage creatures"): an animal standing on a
    /// polluted cell has <c>unpolluteChancePerDay</c> to clean that cell, checked
    /// every 250 ticks — the herd genuinely processes, one mouthful at a time.
    /// </summary>
    public class RM_CompProperties_ProcessorGatherable : CompProperties_Milkable
    {
        /// <summary>Fill-rate multiplier when NOT on feed ground.</summary>
        public float offFeedRateFactor = 0.35f;

        /// <summary>A Biotech-polluted cell (or terrain with toxicBuildupFactor &gt; 0)
        /// counts as feed ground.</summary>
        public bool feedsOnPollution = true;

        /// <summary>&gt;= 0: a cell whose Odyssey sand-grid depth (the drifted ash fall,
        /// via MovingDunes) is at least this counts as feed ground. &lt; 0 = ignored.</summary>
        public float feedSandDepth = -1f;

        /// <summary>Chance per in-game day, while standing on a polluted cell, of
        /// un-polluting it. 0 = no consumption.</summary>
        public float unpolluteChancePerDay;

        /// <summary>Inspect-pane label for the fill bar (e.g. "Bezoar growth").</summary>
        public string fullnessLabel;

        public RM_CompProperties_ProcessorGatherable()
        {
            compClass = typeof(RM_CompProcessorGatherable);
            milkFemaleOnly = false;
        }

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string e in base.ConfigErrors(parentDef))
            {
                yield return e;
            }
            if (milkDef == null)
            {
                yield return "RM_CompProperties_ProcessorGatherable.milkDef (the product) is null.";
            }
            if (milkIntervalDays < 1)
            {
                yield return "RM_CompProperties_ProcessorGatherable.milkIntervalDays must be >= 1.";
            }
            if (offFeedRateFactor < 0f || offFeedRateFactor > 1f)
            {
                yield return "offFeedRateFactor must be in [0,1].";
            }
            if (unpolluteChancePerDay < 0f)
            {
                yield return "unpolluteChancePerDay must be >= 0.";
            }
        }
    }

    public class RM_CompProcessorGatherable : CompMilkable
    {
        private const int FeedCheckIntervalTicks = 250;

        private bool onFeed = true; // unsaved; re-derived every 250 ticks

        public RM_CompProperties_ProcessorGatherable PProps => (RM_CompProperties_ProcessorGatherable)props;

        /// <summary>Whether the last check found the animal on feed ground (state read).</summary>
        public bool OnFeedGround => onFeed;

        protected override bool Active
        {
            get
            {
                return RM_WastelandSettings.wastelandEnabled
                    && RM_WastelandSettings.processorGatherEnabled
                    && base.Active;
            }
        }

        public override void CompTick()
        {
            // Deliberately NOT base.CompTick(): that adds the ungated rate; this is
            // the same arithmetic with the feed-ground factor folded in.
            if (parent.IsHashIntervalTick(FeedCheckIntervalTicks))
            {
                onFeed = ComputeOnFeedGround();
                TryConsumePollution();
            }
            if (!Active)
            {
                return;
            }
            float num = 1f / (GatherResourcesIntervalDays * (float)GenDate.TicksPerDay);
            Pawn pawn = parent as Pawn;
            if (pawn != null)
            {
                num *= PawnUtility.BodyResourceGrowthSpeed(pawn);
            }
            if (!onFeed)
            {
                num *= PProps.offFeedRateFactor;
            }
            fullness = Mathf.Min(1f, fullness + num);
        }

        private bool ComputeOnFeedGround()
        {
            if (!parent.Spawned)
            {
                return false;
            }
            Map map = parent.Map;
            IntVec3 c = parent.Position;
            RM_CompProperties_ProcessorGatherable p = PProps;
            if (p.feedsOnPollution)
            {
                if (!ModsConfig.BiotechActive && p.feedSandDepth < 0f)
                {
                    return true; // no pollution to read: time alone, per spec
                }
                if (c.IsPolluted(map) || c.GetTerrain(map).toxicBuildupFactor > 0f)
                {
                    return true;
                }
            }
            if (p.feedSandDepth >= 0f && map.sandGrid != null && map.sandGrid.GetDepth(c) >= p.feedSandDepth)
            {
                return true;
            }
            return false;
        }

        private void TryConsumePollution()
        {
            float perDay = PProps.unpolluteChancePerDay;
            if (perDay <= 0f || !ModsConfig.BiotechActive || !parent.Spawned)
            {
                return;
            }
            if (!RM_WastelandSettings.wastelandEnabled || !RM_WastelandSettings.processorUnpolluteEnabled)
            {
                return;
            }
            Pawn pawn = parent as Pawn;
            if (pawn != null && (pawn.Dead || pawn.Downed))
            {
                return;
            }
            IntVec3 c = parent.Position;
            Map map = parent.Map;
            if (!map.pollutionGrid.IsPolluted(c))
            {
                return;
            }
            if (Rand.Chance(perDay * FeedCheckIntervalTicks / GenDate.TicksPerDay))
            {
                map.pollutionGrid.SetPolluted(c, false);
            }
        }

        public override string CompInspectStringExtra()
        {
            if (!Active)
            {
                return null;
            }
            string label = PProps.fullnessLabel.NullOrEmpty() ? "MilkFullness".Translate().ToString() : PProps.fullnessLabel;
            string s = label + ": " + Fullness.ToStringPercent();
            if (!onFeed)
            {
                s += " (off feed ground: slow)";
            }
            return s;
        }
    }
}
