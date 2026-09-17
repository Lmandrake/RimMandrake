using System;
using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Bazaar
{
    /// <summary>
    /// BAZAAR_WINDOW_GRID_1 (design §2, §4). One stacked row icon: good-deal,
    /// colony-need, scarcity, provenance and future plugin badges (the
    /// RimProperty stolen-goods seam design §4 names explicitly) are each
    /// one of these, not a hard-coded icon list, so a future mod can add a
    /// badge without forking the grid.
    /// </summary>
    public class RM_BazaarBadgeDef : Def
    {
        public Type workerClass = typeof(BazaarBadgeWorker);

        /// <summary>Stack order, left to right within the badge strip.</summary>
        public int displayPriority;

        private BazaarBadgeWorker workerInt;

        public BazaarBadgeWorker Worker
        {
            get
            {
                if (workerInt == null)
                {
                    workerInt = (BazaarBadgeWorker)Activator.CreateInstance(workerClass);
                    workerInt.def = this;
                }
                return workerInt;
            }
        }

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string error in base.ConfigErrors())
            {
                yield return error;
            }

            if (workerClass == null || !typeof(BazaarBadgeWorker).IsAssignableFrom(workerClass))
            {
                yield return "RM_BazaarBadgeDef " + defName
                    + ": workerClass must be set and subclass BazaarBadgeWorker.";
            }
        }
    }

    /// <summary>One badge's icon and tooltip for a given row, or null if it
    /// does not apply to that row at all (most badges are conditional --
    /// "good deal" only shows when the row IS a good deal).</summary>
    public readonly struct RM_BazaarBadge
    {
        public readonly Texture2D icon;
        public readonly string tooltip;

        public RM_BazaarBadge(Texture2D icon, string tooltip)
        {
            this.icon = icon;
            this.tooltip = tooltip;
        }
    }

    public abstract class BazaarBadgeWorker
    {
        public RM_BazaarBadgeDef def;

        /// <summary>Null return means this badge does not apply to this row
        /// right now -- the grid draws nothing for it, not a blank slot.</summary>
        public abstract RM_BazaarBadge? GetBadge(Tradeable tradeable, RM_BazaarSession session);

        public virtual bool VisibleFor(RM_BazaarSession session) => true;
    }
}
