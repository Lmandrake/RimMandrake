// RESTRAININGBOLTS_COVERAGE_GAPS_1 -- live proof hook for the north-star script (jawa/static_call).
// Reads the SHIPPED formula (GoodwillSituationWorker_RestrainingBolts.CeilingFor) under set settings and,
// when the Free Droid Enclaves faction exists, the real worker's GetMaxGoodwill on it. Settings restored in finally.
using System.Globalization;
using RimWorld;
using Verse;

namespace RimMandrake.Utinni.RestrainingBolts
{
    public static class RestrainingBoltsProof
    {
        private static string F(int v) => v.ToString(CultureInfo.InvariantCulture);

        /// <summary>"n0=.. n1=.. n4=.. n40=.. n1000=.. off4=.. pen5n4=.. floorm50n1000=.. fde=B hediff=B
        /// live_count=K live_max=M live_off=M" (live_* are "-" when the FDE faction is absent).</summary>
        public static string ProofCap(string args)
        {
            bool wasEnabled = RestrainingBoltsSettings.enabled;
            float wasPenalty = RestrainingBoltsSettings.penaltyPerBoltedDroid;
            float wasFloor = RestrainingBoltsSettings.goodwillFloor;
            try
            {
                RestrainingBoltsSettings.enabled = true;
                RestrainingBoltsSettings.penaltyPerBoltedDroid = 2.5f;
                RestrainingBoltsSettings.goodwillFloor = -70f;
                string s = "n0=" + F(GoodwillSituationWorker_RestrainingBolts.CeilingFor(0))
                    + " n1=" + F(GoodwillSituationWorker_RestrainingBolts.CeilingFor(1))
                    + " n4=" + F(GoodwillSituationWorker_RestrainingBolts.CeilingFor(4))
                    + " n40=" + F(GoodwillSituationWorker_RestrainingBolts.CeilingFor(40))
                    + " n1000=" + F(GoodwillSituationWorker_RestrainingBolts.CeilingFor(1000));
                RestrainingBoltsSettings.enabled = false;
                s += " off4=" + F(GoodwillSituationWorker_RestrainingBolts.CeilingFor(4));
                RestrainingBoltsSettings.enabled = true;
                RestrainingBoltsSettings.penaltyPerBoltedDroid = 5f;
                s += " pen5n4=" + F(GoodwillSituationWorker_RestrainingBolts.CeilingFor(4));
                RestrainingBoltsSettings.penaltyPerBoltedDroid = 2.5f;
                RestrainingBoltsSettings.goodwillFloor = -50f;
                s += " floorm50n1000=" + F(GoodwillSituationWorker_RestrainingBolts.CeilingFor(1000));
                RestrainingBoltsSettings.goodwillFloor = -70f;

                FactionDef fdeDef = FactionDefOf_RestrainingBolts.RUT_Jawa_FreeDroidEnclaves;
                Faction fde = fdeDef == null ? null : Find.FactionManager?.FirstFactionOfDef(fdeDef);
                s += " fde=" + (fde != null) + " hediff=" + GoodwillSituationWorker_RestrainingBolts.BoltHediffLoaded;
                GoodwillSituationWorker worker = DefDatabase<GoodwillSituationDef>.GetNamedSilentFail("Jawa_RestrainingBolts")?.Worker;
                if (fde == null || worker == null)
                    return s + " live_count=- live_max=- live_off=-";
                s += " live_count=" + F(GoodwillSituationWorker_RestrainingBolts.BoltedCount())
                    + " live_max=" + F(worker.GetMaxGoodwill(fde));
                RestrainingBoltsSettings.enabled = false;
                s += " live_off=" + F(worker.GetMaxGoodwill(fde));
                return s;
            }
            catch (System.Exception e)
            {
                return "ERROR " + e.GetType().Name + ": " + e.Message;
            }
            finally
            {
                RestrainingBoltsSettings.enabled = wasEnabled;
                RestrainingBoltsSettings.penaltyPerBoltedDroid = wasPenalty;
                RestrainingBoltsSettings.goodwillFloor = wasFloor;
            }
        }
    }
}
