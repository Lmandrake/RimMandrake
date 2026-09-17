using System;
using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Bazaar
{
    /// <summary>
    /// BAZAAR_WINDOW_GRID_1 (design/RimMandrake/bazaar_trade_window_design.md
    /// §2). One column of the Goods grid. Top-level custom def, never a
    /// nested `&lt;li&gt;` custom-loaded list -- the loader trap that
    /// silently discards a whole def on one bad entry
    /// (rimworld-custom-loader-li-trap).
    ///
    /// The grid itself (virtualized rows over `TradeDeal.AllTradeables`) is
    /// NOT built yet -- this def and its worker are the plugin seam it will
    /// read column presets and per-cell drawing from, ready before the grid
    /// body exists so the two can land independently.
    /// </summary>
    public class RM_BazaarColumnDef : Def
    {
        public Type workerClass = typeof(BazaarColumnWorker);

        public float defaultWidth = 100f;

        /// <summary>Column presets (design §2) hide/show by defName; this is
        /// only the shipped default before any preset is saved.</summary>
        public bool defaultVisible = true;

        /// <summary>Sort order among visible columns, left to right.</summary>
        public int displayPriority;

        private BazaarColumnWorker workerInt;

        public BazaarColumnWorker Worker
        {
            get
            {
                if (workerInt == null)
                {
                    workerInt = (BazaarColumnWorker)Activator.CreateInstance(workerClass);
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

            if (workerClass == null || !typeof(BazaarColumnWorker).IsAssignableFrom(workerClass))
            {
                yield return "RM_BazaarColumnDef " + defName
                    + ": workerClass must be set and subclass BazaarColumnWorker.";
            }

            if (defaultWidth <= 0f)
            {
                yield return "RM_BazaarColumnDef " + defName + ": defaultWidth must be > 0.";
            }
        }
    }

    /// <summary>
    /// One column's behavior: how it draws its cell, how it sorts, what its
    /// tooltip says, and whether it should even appear for the current
    /// session's unlocked intel layers (design §4's Social/artifact gating
    /// lives here, per-column, rather than as a separate filter pass).
    /// </summary>
    public abstract class BazaarColumnWorker
    {
        public RM_BazaarColumnDef def;

        public abstract void DrawCell(Rect rect, Tradeable tradeable, RM_BazaarSession session);

        /// <summary>Standard IComparer-shaped ordering; matches how vanilla's
        /// own TransferableSorterDef compares.</summary>
        public virtual int Compare(Tradeable a, Tradeable b) => 0;

        public virtual string GetTooltip(Tradeable tradeable, RM_BazaarSession session) => null;

        /// <summary>False hides the whole column for this session -- the
        /// intel-gating point named in design §4 (e.g. an L1 price-context
        /// column needs Social 3+).</summary>
        public virtual bool VisibleFor(RM_BazaarSession session) => true;
    }
}
