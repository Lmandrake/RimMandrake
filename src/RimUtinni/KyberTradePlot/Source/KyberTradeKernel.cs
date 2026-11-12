// KYBER_TRADE_PLOT_1 — the kyber trade's state machine, with no Verse/Unity dependency so the offline selftest
// (Source/SelfTest, python3 src/RimMandrake/Utils/selftest_kyber_trade_plot.py) drives the very code the game runs.
//
// Spec: design/Jawa/kyber_trade_plot_spec.md. What one sale does (§3, §4): Imperial Heat up substantially, scaled
// sublinearly with the quantity (the crime is selling kyber, not the invoice); Hutt Interest up per crystal, from any
// buyer (word gets around); a modest Cartel goodwill bump when the buyer IS the Cartel. The Homestead visit (§5) is due
// once per campaign, after the second sale, never again. The donation (§6) is offered once, through whichever door
// opened: the visit answered straight (Homestead), or, when the visit went nowhere, Hutt Interest reaching the fixer
// beat (§4c). Refused or failed, it never comes back (§6.5). The donation itself moves no Heat (K2, RULED 2026-09-11):
// a donation is not a sale, and nothing here is called for one.
using System;
using System.Reflection;

namespace RimMandrake.Utinni.KyberTradePlot
{
    public enum KyberVisitState { NotDue, Due, Arrived, Forthright, Evasive, Impossible }
    public enum KyberDonationState { NotDue, Due, Offered }
    public enum KyberDonationDoor { None, Homestead, HuttFixer }
    public enum KyberTickAction { None, VisitorsLeftUnanswered, FireVisit, VisitNeverComes, FireDonation }

    /// <summary>The numbers, copied from the Mod Settings each call (defaults = shipped behaviour).</summary>
    public sealed class KyberTuning
    {
        public float heatPerSale = 15f;          // Colony Visibility points for a one-crystal sale (bands are 20 wide)
        public float heatCapPerSale = 40f;       // one sale, however large, moves at most two bands
        public float huttInterestPerCrystal = 3f;
        public int cartelGoodwillPerSale = 4;
        public int visitAfterSales = 2;          // "the first is deniable, the second is a pattern"
        public int visitDelayTicks = 60000;      // a day after the sale that makes the pattern
        public int donationDelayTicks = 150000;  // two and a half days after the door opens
        public float fixerInterest = 15f;        // §4c: the Cartel fixer passes the ask along
    }

    /// <summary>What one sale changed; the game turns each field into its effect and its message.</summary>
    public sealed class KyberSaleEffect
    {
        public int crystals;
        public float heat;
        public float huttInterest;
        public int cartelGoodwill;
        public bool firstSale;
        public bool visitBecameDue;
    }

    public static class KyberTradeKernel
    {
        /// <summary>§3: substantial per sale, sublinear in quantity, capped. 0 for no crystals.</summary>
        public static float HeatForSale(int crystals, KyberTuning t)
        {
            if (crystals <= 0) return 0f;
            return Math.Min(t.heatCapPerSale, t.heatPerSale * (float)Math.Sqrt(crystals));
        }

        public static float InterestForSale(int crystals, KyberTuning t) => crystals <= 0 ? 0f : t.huttInterestPerCrystal * crystals;
    }

    public sealed class KyberPlotState
    {
        public int sales;
        public int crystalsSold;
        public float huttInterest;
        public int lastSaleTick = -1;
        public KyberVisitState visit = KyberVisitState.NotDue;
        public int visitDueTick = -1;
        public KyberDonationState donation = KyberDonationState.NotDue;
        public KyberDonationDoor door = KyberDonationDoor.None;
        public int donationDueTick = -1;

        public KyberSaleEffect RecordSale(int crystals, bool toCartel, int now, KyberTuning t)
        {
            var e = new KyberSaleEffect { crystals = crystals };
            if (crystals <= 0) return e;
            e.firstSale = sales == 0;
            sales++;
            crystalsSold += crystals;
            lastSaleTick = now;
            e.heat = KyberTradeKernel.HeatForSale(crystals, t);
            e.huttInterest = KyberTradeKernel.InterestForSale(crystals, t);
            huttInterest += e.huttInterest;
            if (toCartel) e.cartelGoodwill = t.cartelGoodwillPerSale;
            if (visit == KyberVisitState.NotDue && sales >= Math.Max(1, t.visitAfterSales))
            {
                visit = KyberVisitState.Due;
                visitDueTick = now + t.visitDelayTicks;
                e.visitBecameDue = true;
            }
            return e;
        }

        /// <summary>What the game should do on this tick, in order: notice visitors who left unanswered, then (with the
        /// plot on) bring the visit when it is due, or learn that it never can, then ask for the donation when due.
        /// GameComponent_KyberTrade.GameComponentTick acts on this and nothing else.</summary>
        public KyberTickAction NextAction(int now, bool plotEnabled, bool visitorsStillHere, bool homesteadCanSend)
        {
            if (visit == KyberVisitState.Arrived && !visitorsStillHere) return KyberTickAction.VisitorsLeftUnanswered;
            if (!plotEnabled) return KyberTickAction.None;
            if (VisitShouldFire(now)) return homesteadCanSend ? KyberTickAction.FireVisit : KyberTickAction.VisitNeverComes;
            if (DonationShouldFire(now)) return KyberTickAction.FireDonation;
            return KyberTickAction.None;
        }

        public bool VisitShouldFire(int now) => visit == KyberVisitState.Due && now >= visitDueTick;

        /// <summary>The visit could not happen right now (no home map, a hostile lord on it): try again later.</summary>
        public void VisitPostponed(int now, int byTicks) { if (visit == KyberVisitState.Due) visitDueTick = now + byTicks; }

        /// <summary>The visitors are on the map. A dev-mode fire before the second sale counts as the one visit.</summary>
        public void VisitArrived() { if (visit == KyberVisitState.NotDue || visit == KyberVisitState.Due) visit = KyberVisitState.Arrived; }

        public bool VisitCanStillHappen => visit == KyberVisitState.NotDue || visit == KyberVisitState.Due;

        /// <summary>No Homestead faction that could send anyone (gone, or hostile): the visit never comes.</summary>
        public void VisitImpossible() { if (visit == KyberVisitState.Due) visit = KyberVisitState.Impossible; }

        public void VisitAnswered(bool forthright, int now, KyberTuning t)
        {
            if (visit != KyberVisitState.Arrived) return;
            visit = forthright ? KyberVisitState.Forthright : KyberVisitState.Evasive;
            if (forthright) OpenDoor(KyberDonationDoor.Homestead, now, t);
        }

        /// <summary>The visitors left (or died, or were taken) with no answer given: evasive, no punishment.</summary>
        public void VisitLeftUnanswered() { if (visit == KyberVisitState.Arrived) visit = KyberVisitState.Evasive; }

        /// <summary>§4c: the fixer lane is the donation's other door, used only when the visit's door stayed shut.
        /// True on the one call that opens it.</summary>
        public bool TryOpenFixerDoor(int now, KyberTuning t)
        {
            if (door != KyberDonationDoor.None) return false;
            if (visit != KyberVisitState.Evasive && visit != KyberVisitState.Impossible) return false;
            if (huttInterest < t.fixerInterest) return false;
            OpenDoor(KyberDonationDoor.HuttFixer, now, t);
            return true;
        }

        private void OpenDoor(KyberDonationDoor which, int now, KyberTuning t)
        {
            if (door != KyberDonationDoor.None) return;
            door = which;
            donation = KyberDonationState.Due;
            donationDueTick = now + t.donationDelayTicks;
        }

        public bool DonationShouldFire(int now) => donation == KyberDonationState.Due && now >= donationDueTick;

        public void DonationPostponed(int now, int byTicks) { if (donation == KyberDonationState.Due) donationDueTick = now + byTicks; }

        /// <summary>Offered once; whatever the player does with it, the cause never calls again (§6.5).</summary>
        public void DonationOffered() { if (donation == KyberDonationState.Due) donation = KyberDonationState.Offered; }
    }
    /// <summary>Imperial Heat is the ONE Empire attention meter the campaign has: Colony Visibility
    /// (mandrake.rm.visibility, GameComponent_ColonyVisibility.shipVisibility, 0-100), per
    /// design/Jawa/proposals/empire_escalation_ladder_design_2026-10-02.md §2 ("One meter, which is already built:
    /// Colony Visibility. No Imperial heat variable is added."). It drives the pursuit ladder's pace and raid points, so
    /// a kyber sale rides the existing pursuit spine (spec §3) with no new incident. Bound by reflection, like
    /// EmpirePursuit's EmpireSearch, so this mod takes no hard dependency; these two calls take the component itself so
    /// the selftest binds them to a real GameComponent_ColonyVisibility.</summary>
    public static class VisibilityReflection
    {
        public const string TypeName = "RimMandrake.Visibility.GameComponent_ColonyVisibility";

        public static float Read(object component)
        {
            if (component == null) return -1f;
            object v = component.GetType().GetField("shipVisibility", BindingFlags.Public | BindingFlags.Instance)?.GetValue(component);
            return v is float f ? f : -1f;
        }

        /// <summary>Raises (or lowers) the meter through its own Adjust (which clamps it). False when the method is gone.</summary>
        public static bool Adjust(object component, float delta, string reason)
        {
            if (component == null) return false;
            MethodInfo m = component.GetType().GetMethod("Adjust", BindingFlags.Public | BindingFlags.Instance, null,
                new[] { typeof(float), typeof(string) }, null);
            if (m == null) return false;
            m.Invoke(component, new object[] { delta, reason });
            return true;
        }
    }
}
