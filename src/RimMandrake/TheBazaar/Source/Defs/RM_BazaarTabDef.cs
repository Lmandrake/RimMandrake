using System;
using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace RimMandrake.Bazaar
{
    /// <summary>
    /// BAZAAR_WINDOW_GRID_1 (design §2). One of the window's three tabs --
    /// Goods, Broker, Ledger ship as data-driven defs rather than a
    /// hard-coded enum, so the Broker tab (design §2: "greys out ... when
    /// FlowWorks is absent") and any future tab can gate and hide themselves
    /// without an if-chain in the window class.
    /// </summary>
    public class RM_BazaarTabDef : Def
    {
        public Type workerClass = typeof(BazaarTabWorker);

        public int displayPriority;

        private BazaarTabWorker workerInt;

        public BazaarTabWorker Worker
        {
            get
            {
                if (workerInt == null)
                {
                    workerInt = (BazaarTabWorker)Activator.CreateInstance(workerClass);
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

            if (workerClass == null || !typeof(BazaarTabWorker).IsAssignableFrom(workerClass))
            {
                yield return "RM_BazaarTabDef " + defName
                    + ": workerClass must be set and subclass BazaarTabWorker.";
            }
        }
    }

    public abstract class BazaarTabWorker
    {
        public RM_BazaarTabDef def;

        /// <summary>False hides the tab entirely for this session -- e.g.
        /// the Broker tab when no reachable universal tank exists, or
        /// FlowWorks (was Liquid Logistics) is not installed. Return a
        /// disabled-with-reason state instead of hiding when the design
        /// calls for greying out with a one-line reason (design §2); that
        /// distinction is the worker's call, not this def's.</summary>
        public virtual bool ShouldShow(RM_BazaarSession session) => true;

        public abstract void DoTabContents(Rect rect, RM_BazaarSession session);
    }
}
