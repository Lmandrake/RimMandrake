using System;
using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.GelatinousSlime
{
    // ════════════════════════════════════════════════════════════════════
    // THE GENETIC ARCHIVE (spec §5b, §9).
    //
    // 🔑 A DEF, NOT A LIST IN CODE, AND NOTHING IN THIS ASSEMBLY NAMES A GENE.
    // The mod ships RM_Archive_Default (vanilla Biotech genes under the
    // P-laws). The RUT campaign layer swaps in the frozen SW gene lists by
    // shipping its own GeneArchiveDef with a higher `priority` — no patch, no
    // override, no C# change. Any other mod does the same.
    //
    // The P-laws themselves (P4 trade, P5 riders felt, P7 Slime-marked, P8
    // heritable) are enforced where each one belongs: P4 and P5 by the
    // curation of the shipped archive def, P7 and P8 by the injector.
    // ════════════════════════════════════════════════════════════════════
    public class GeneArchiveDef : Def
    {
        // What a player can ask for.
        public List<GeneDef> targetGenes = new List<GeneDef>();

        // What comes with it, unseen until it lands.
        public List<GeneDef> riderGenes = new List<GeneDef>();

        // Highest priority wins. The mod's own default is 0; a campaign or
        // overhaul ships 100 and simply replaces it.
        public int priority;

        private static GeneArchiveDef cachedActive;
        private static bool cacheResolved;

        public static GeneArchiveDef Active
        {
            get
            {
                if (!cacheResolved)
                {
                    cacheResolved = true;
                    cachedActive = null;
                    foreach (GeneArchiveDef d in DefDatabase<GeneArchiveDef>.AllDefsListForReading)
                    {
                        if (d.targetGenes.NullOrEmpty())
                        {
                            continue;
                        }
                        if (cachedActive == null || d.priority > cachedActive.priority)
                        {
                            cachedActive = d;
                        }
                    }
                }
                return cachedActive;
            }
        }

        public GeneDef RollRider()
        {
            if (riderGenes.NullOrEmpty())
            {
                return null;
            }
            return riderGenes.RandomElement();
        }

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors())
            {
                yield return e;
            }
            if (targetGenes.NullOrEmpty())
            {
                yield return "GeneArchiveDef with no targetGenes: it can never be chosen from.";
            }
        }
    }

    // ════════════════════════════════════════════════════════════════════
    // PRIMING — "choose the gene from the archive list before the trip"
    // (spec §5b). One dialog, one recipe, and the archive stays a swappable
    // def-list. The alternative the spec prices worse is one RecipeDef per
    // gene, because vanilla recipes produce fixed products and take no
    // parameters.
    // ════════════════════════════════════════════════════════════════════
    public class Dialog_GeneArchive : Window
    {
        private readonly GeneArchiveDef archive;
        private readonly Action<GeneDef> onChosen;
        private Vector2 scroll;

        public override Vector2 InitialSize
        {
            get { return new Vector2(620f, 640f); }
        }

        public Dialog_GeneArchive(GeneArchiveDef archive, Action<GeneDef> onChosen)
        {
            this.archive = archive;
            this.onChosen = onChosen;
            forcePause = true;
            absorbInputAroundWindow = true;
            closeOnClickedOutside = false;
            doCloseX = true;
        }

        public override void DoWindowContents(Rect inRect)
        {
            Text.Font = GameFont.Medium;
            Widgets.Label(new Rect(0f, 0f, inRect.width, 34f), "Ask the archive");
            Text.Font = GameFont.Small;

            Rect blurb = new Rect(0f, 38f, inRect.width, 58f);
            Widgets.Label(blurb,
                "Everything that ever touched the body is still in circulation. Name one "
                + "entry and the seeker will find where the current carrying it surfaces.\n"
                + "Something else will come with it. That is not negotiable.");

            Rect outer = new Rect(0f, 102f, inRect.width, inRect.height - 142f);
            List<GeneDef> genes = archive.targetGenes;
            const float RowHeight = 42f;
            Rect inner = new Rect(0f, 0f, outer.width - 20f, genes.Count * RowHeight + 4f);

            Widgets.BeginScrollView(outer, ref scroll, inner);
            float y = 0f;
            for (int i = 0; i < genes.Count; i++)
            {
                GeneDef gene = genes[i];
                if (gene == null)
                {
                    continue;
                }
                Rect row = new Rect(0f, y, inner.width, RowHeight - 2f);
                if (i % 2 == 1)
                {
                    Widgets.DrawLightHighlight(row);
                }
                Widgets.DrawHighlightIfMouseover(row);

                Rect labelRect = new Rect(row.x + 6f, row.y + 4f, row.width - 140f, row.height - 8f);
                Widgets.Label(labelRect, gene.LabelCap
                    + "  (complexity " + gene.biostatCpx + ", metabolism "
                    + gene.biostatMet.ToStringWithSign() + ")");
                TooltipHandler.TipRegion(row, gene.description);

                Rect buttonRect = new Rect(row.xMax - 126f, row.y + 5f, 120f, row.height - 10f);
                if (Widgets.ButtonText(buttonRect, "Ask for this"))
                {
                    Action<GeneDef> callback = onChosen;
                    Close();
                    if (callback != null)
                    {
                        callback(gene);
                    }
                    return;
                }
                y += RowHeight;
            }
            Widgets.EndScrollView();

            Rect cancel = new Rect(inRect.width / 2f - 70f, inRect.height - 34f, 140f, 30f);
            if (Widgets.ButtonText(cancel, "Cancel"))
            {
                Close();
            }
        }
    }

    // ════════════════════════════════════════════════════════════════════
    // P7 — "each machine gene stacks the Slime-marked social/romance penalty:
    // the marked are hard to love" (spec §5e).
    //
    // A SOCIAL thought: it is an opinion OTHER pawns hold about the marked
    // one, which is what an opinion and romance penalty actually is. The stage
    // is the marked pawn's RM_SlimeMarked severity band — one entry, several,
    // heavily filed — so the penalty grows with every trip to the body.
    // ════════════════════════════════════════════════════════════════════
    public class ThoughtWorker_SlimeMarked : ThoughtWorker
    {
        protected override ThoughtState CurrentSocialStateInternal(Pawn p, Pawn other)
        {
            if (p == other || other == null || !other.RaceProps.Humanlike)
            {
                return ThoughtState.Inactive;
            }
            if (!RelationsUtility.PawnsKnowEachOther(p, other))
            {
                return ThoughtState.Inactive;
            }
            if (SlimeDefs.SlimeMarked == null || other.health == null)
            {
                return ThoughtState.Inactive;
            }
            Hediff marked = other.health.hediffSet.GetFirstHediffOfDef(SlimeDefs.SlimeMarked);
            if (marked == null)
            {
                return ThoughtState.Inactive;
            }
            if (marked.Severity >= 4f)
            {
                return ThoughtState.ActiveAtStage(2);
            }
            if (marked.Severity >= 2f)
            {
                return ThoughtState.ActiveAtStage(1);
            }
            return ThoughtState.ActiveAtStage(0);
        }
    }
}
