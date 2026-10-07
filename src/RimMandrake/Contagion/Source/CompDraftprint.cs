using System.Collections.Generic;
using System.Linq;
using System.Text;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Contagion
{
    // CONTAGION_GPT_ENRICHMENT_1, part 1: Draftprints. The owner, on the card:
    // "I like the helix offering to purchase strange scans of the beasts here.
    // You assume the risks."
    //
    // Carried by RM_Draftprint. It records one Unfinished as it was when a
    // colonist sampled it, before it dissolved: the limbs it rolled (by
    // HediffDef, so a Helix contract can match them exactly), whether it rolled
    // a monster, its most extreme stat against its own kind, and what failed on
    // it. Every field is filled once, by DraftprintUtility.Record, and saved.
    public class CompProperties_Draftprint : CompProperties
    {
        // The stats compared against RM_TheUnfinished's own base values to
        // choose the "extreme stat". Each must exist as a StatDef.
        public List<StatDef> extremeStats;

        // Base market value of a print, before features. A Helix contract pays
        // separately (QuestPart_RM_DraftprintContract), so this only sets what
        // an ordinary trader offers.
        public float valuePerLimb = 25f;
        public float monstrousValueFactor = 3f;

        public CompProperties_Draftprint()
        {
            compClass = typeof(CompDraftprint);
        }
    }

    public class CompDraftprint : ThingComp
    {
        public List<HediffDef> limbs = new List<HediffDef>();
        public bool monstrous;
        public string extremeStat = "";
        public string failure = "";
        public string sourceLabel = "";
        public int sampledTick = -1;

        public CompProperties_Draftprint Props => (CompProperties_Draftprint)props;

        public bool IsRecorded => sampledTick >= 0;

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Collections.Look(ref limbs, "rmDraftLimbs", LookMode.Def);
            Scribe_Values.Look(ref monstrous, "rmDraftMonstrous", false);
            Scribe_Values.Look(ref extremeStat, "rmDraftExtremeStat", "");
            Scribe_Values.Look(ref failure, "rmDraftFailure", "");
            Scribe_Values.Look(ref sourceLabel, "rmDraftSource", "");
            Scribe_Values.Look(ref sampledTick, "rmDraftSampledTick", -1);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                if (limbs == null)
                {
                    limbs = new List<HediffDef>();
                }
                // A limb def removed by a later mod version loads as null.
                limbs.RemoveAll(d => d == null);
            }
        }

        // Feature words, in the order a Helix contract states them.
        public IEnumerable<string> FeatureLabels()
        {
            foreach (HediffDef d in limbs)
            {
                yield return d.label;
            }
            if (monstrous)
            {
                yield return RM_ContagionDefOf.RM_UnfinishedMonstrous.label;
            }
        }

        public override string TransformLabel(string label)
        {
            if (!IsRecorded)
            {
                return label + " (blank)";
            }
            string features = string.Join(", ", FeatureLabels());
            return features.NullOrEmpty() ? label : label + " (" + features + ")";
        }

        public override string CompInspectStringExtra()
        {
            if (!IsRecorded)
            {
                return "Blank: records nothing.";
            }
            StringBuilder sb = new StringBuilder();
            sb.Append("Limbs: ");
            sb.Append(limbs.Count == 0 ? "none finished" : string.Join(", ", limbs.Select(d => d.label)));
            if (monstrous)
            {
                sb.AppendLine();
                sb.Append("Rolled a monster: " + RM_ContagionDefOf.RM_UnfinishedMonstrous.label);
            }
            if (!extremeStat.NullOrEmpty())
            {
                sb.AppendLine();
                sb.Append("Extreme: " + extremeStat);
            }
            if (!failure.NullOrEmpty())
            {
                sb.AppendLine();
                sb.Append("Failure: " + failure);
            }
            return sb.ToString();
        }

        // StatWorker_MarketValue multiplies every comp's GetStatFactor into an
        // item's value (RimSage, 1.6), so a richer print is worth more to any
        // ordinary trader, not only to a Helix contract.
        public override float GetStatFactor(StatDef stat)
        {
            if (stat != StatDefOf.MarketValue || !IsRecorded)
            {
                return base.GetStatFactor(stat);
            }
            float v = 1f + limbs.Count * Props.valuePerLimb / Mathf.Max(1f, parent.def.BaseMarketValue);
            return monstrous ? v * Props.monstrousValueFactor : v;
        }

        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            foreach (Gizmo g in base.CompGetGizmosExtra())
            {
                yield return g;
            }
            if (!RM_ContagionSettings.draftprintsEnabled || !IsRecorded || !parent.Spawned)
            {
                yield break;
            }
            QuestPart_RM_DraftprintContract contract = QuestPart_RM_DraftprintContract.FirstOpenMatch(this);
            Command_Action cmd = new Command_Action
            {
                defaultLabel = "Transmit to the Helix",
                defaultDesc = contract != null
                    ? "Transmit this draftprint to the Helix watchers and fill their open contract (" + contract.TraitsLabel() + ") for " + contract.reward + " silver, delivered by drop pod. The print is consumed."
                    : "No open Helix contract wants this combination. Accept a Helix draftprint contract whose features this print carries.",
                icon = parent.def.uiIcon,
                action = delegate
                {
                    QuestPart_RM_DraftprintContract c = QuestPart_RM_DraftprintContract.FirstOpenMatch(this);
                    c?.Fulfil(this);
                }
            };
            if (contract == null)
            {
                cmd.Disable("No open Helix contract matches this print.");
            }
            yield return cmd;
        }
    }
}
