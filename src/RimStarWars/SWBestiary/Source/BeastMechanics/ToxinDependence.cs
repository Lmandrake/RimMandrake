using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.StarWars.SWBestiary
{
    // ════════════════════════════════════════════════════════════════════
    // BLUEDESERT_ZERO_PLANTS_1 follow-up — RSW_ToxinDependence (the mutagenic
    // norphea's need + hediff). BMT_FAUNA_ABSORPTION_1 ported the defs from
    // Biomes! Polluted Lands (workshop 3390196656, 1.6/Defs/NeedDefs/Needs.xml)
    // but dropped their donor classes (BMT_PollutedLands.Need_ToxinDependence /
    // Hediff_ToxinDependence), leaving needClass null: every norphea logged
    // ArgumentNullException in Pawn_NeedsTracker.AddNeed and never got the need.
    //
    // Rebuilt here from the donor's own shipped Source/ (read 2026-09-30):
    //   need    — rises 0.0001/tick while the pawn carries ToxicBuildup OR
    //             stands on a polluted cell; otherwise falls at fallPerDay.
    //             Satisfied > 0.1, Desire > 0.01, else Withdrawal.
    //   hediff  — stage 0 normally, stage 1 ("unmet") while the need is in
    //             Withdrawal; the need is enabled by HediffDef.chemicalNeed.
    //
    // Why not vanilla Need_Chemical/Hediff_Addiction: Need_Chemical only ever
    // falls (a drug refills it on ingestion), so a wild norphea would starve
    // into the lethal stage with nothing on the map able to refill it.
    //
    // Mod Settings: toxinDependenceEnabled off freezes the need at full, so
    // the hediff never leaves its harmless stage 0.
    // ════════════════════════════════════════════════════════════════════
    public class RSW_Need_ToxinDependence : Need
    {
        private const float GainPerTick = 0.0001f;
        private const int IntervalTicks = 150;

        public RSW_Need_ToxinDependence(Pawn pawn) : base(pawn)
        {
            threshPercents = new List<float> { 0.1f };
        }

        public override int GUIChangeArrow => -1;

        public DrugDesireCategory CurCategory
        {
            get
            {
                if (CurLevel > 0.1f) return DrugDesireCategory.Satisfied;
                return CurLevel > 0.01f ? DrugDesireCategory.Desire : DrugDesireCategory.Withdrawal;
            }
        }

        public override float CurLevel
        {
            get => base.CurLevel;
            set
            {
                DrugDesireCategory before = CurCategory;
                base.CurLevel = value;
                if (CurCategory != before)
                {
                    LinkedHediff?.Notify_NeedCategoryChanged();
                }
            }
        }

        public RSW_Hediff_ToxinDependence LinkedHediff
        {
            get
            {
                List<Hediff> hediffs = pawn.health.hediffSet.hediffs;
                for (int i = 0; i < hediffs.Count; i++)
                {
                    if (hediffs[i] is RSW_Hediff_ToxinDependence h && h.def.chemicalNeed == def)
                    {
                        return h;
                    }
                }
                return null;
            }
        }

        public override void SetInitialLevel()
        {
            CurLevelPercentage = Rand.Range(0.8f, 1f);
        }

        public override void NeedInterval()
        {
            if (IsFrozen) return;

            if (!RSW_BeastMechanicsSettings.toxinDependenceEnabled)
            {
                CurLevel = MaxLevel;
                return;
            }

            bool fed = pawn.health.hediffSet.HasHediff(HediffDefOf.ToxicBuildup)
                       || (pawn.Spawned && pawn.Position.IsPolluted(pawn.Map));
            if (fed)
            {
                CurLevel += GainPerTick * IntervalTicks;
            }
            else
            {
                CurLevel -= def.fallPerDay / 60000f * IntervalTicks;
            }
        }
    }

    public class RSW_Hediff_ToxinDependence : HediffWithComps
    {
        public RSW_Need_ToxinDependence Need
        {
            get
            {
                if (pawn.Dead || pawn.needs == null || def.chemicalNeed == null) return null;
                return pawn.needs.TryGetNeed(def.chemicalNeed) as RSW_Need_ToxinDependence;
            }
        }

        public override string TipStringExtra
        {
            get
            {
                string text = base.TipStringExtra;
                RSW_Need_ToxinDependence need = Need;
                if (need != null)
                {
                    if (!text.NullOrEmpty()) text += "\n";
                    text += "CreatesNeed".Translate() + ": " + need.LabelCap + " (" + need.CurLevelPercentage.ToStringPercent("F0") + ")";
                }
                return text;
            }
        }

        public override int CurStageIndex
        {
            get
            {
                RSW_Need_ToxinDependence need = Need;
                return need != null && need.CurCategory == DrugDesireCategory.Withdrawal ? 1 : 0;
            }
        }

        public void Notify_NeedCategoryChanged()
        {
            pawn?.health.Notify_HediffChanged(this);
        }
    }
}
