// KYBER_TRADE_PLOT_1 — the kyber trade in the running game: what a sale is, what it moves, and when the Homestead
// visit and the donation come. The decisions are KyberPlotState's (KyberTradeKernel.cs, selftested offline); this
// file only reads the game and applies them.
//
// A SALE (spec §2) is a kyber-family item the colony hands over in an executed trade deal: TradeDeal.TryExecute with
// the item's ActionToDo == PlayerSells, counted before the deal resolves (TryExecute resets the counts afterwards).
// Every trade window in the game goes through it: caravans visiting, settlement trade, orbital traders, trade shuttles.
// So the count is the trade session itself, never an inventory diff: crafting a crystal away, a raid stealing one, a
// gift (TradeSession.giftMode) and the donation quest's delivery (TradeRequestComp, not a trade deal) are not sales.
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.Utinni.KyberTradePlot
{
    [DefOf]
    public static class KyberDefOf
    {
        public static IncidentDef RUT_KyberHomesteadVisit;
        public static IncidentDef RUT_GiveQuest_KyberDonationSmuggle;
        public static LetterDef RUT_KyberHomesteadQuestion;
        public static HistoryEventDef RUT_KyberHomesteadDoorOpened;
        public static HistoryEventDef RUT_KyberSoldToCartel;
        static KyberDefOf() { DefOfHelper.EnsureInitializedInCtor(typeof(KyberDefOf)); }
    }

    public static class KyberTrade
    {
        public const string CartelDefName = "RUT_Jawa_HuttCartel";
        /// <summary>The kyber family (spec §1): the donor crystal and the mindstone, which carries the same law.</summary>
        public static readonly string[] FamilyDefNames = { "Force_KyberCrystal", "RUT_Mindstone" };

        public static bool IsKyberFamily(ThingDef d) => d != null && FamilyDefNames.Contains(d.defName);

        public static int CrystalsBeingSold(TradeDeal deal)
        {
            if (deal == null || TradeSession.giftMode) return 0;
            int n = 0;
            foreach (Tradeable t in deal.AllTradeables)
                if (t != null && t.ActionToDo == TradeAction.PlayerSells && IsKyberFamily(t.ThingDef))
                    n += t.CountToTransferToDestination;
            return n;
        }

        public static GameComponent_KyberTrade Component => Current.Game?.GetComponent<GameComponent_KyberTrade>();

        private static System.Type visType;
        private static bool visLooked;

        /// <summary>The Colony Visibility component (the Empire's one attention meter), or null without the mod.</summary>
        public static GameComponent VisibilityComponent()
        {
            if (!visLooked)
            {
                visLooked = true;
                visType = AccessTools.TypeByName(VisibilityReflection.TypeName);
            }
            if (visType == null || Current.Game == null) return null;
            return Current.Game.components.FirstOrDefault(c => c.GetType() == visType);
        }

        public static string BandOf(GameComponent vis)
        {
            object b = vis?.GetType().GetProperty("Band")?.GetValue(vis);
            return b?.ToString() ?? "";
        }

        public static Faction Homestead()
        {
            Faction f = Find.FactionManager.FirstFactionOfDef(FactionDefOf.OutlanderCivil);
            return f == null || f.defeated ? null : f;
        }

        public static KyberTuning Tuning() => new KyberTuning
        {
            heatPerSale = KyberTradePlotSettings.heatPerSale,
            heatCapPerSale = KyberTradePlotSettings.heatCapPerSale,
            huttInterestPerCrystal = KyberTradePlotSettings.huttInterestPerCrystal,
            cartelGoodwillPerSale = KyberTradePlotSettings.cartelGoodwillPerSale,
            visitAfterSales = KyberTradePlotSettings.visitAfterSales,
            fixerInterest = KyberTradePlotSettings.fixerInterest,
        };
    }

    [HarmonyPatch(typeof(TradeDeal), nameof(TradeDeal.TryExecute))]
    public static class Patch_TradeDeal_TryExecute_KyberSale
    {
        public static void Prefix(TradeDeal __instance, out int __state)
        {
            __state = KyberTradePlotSettings.kyberSalesDrawHeat ? KyberTrade.CrystalsBeingSold(__instance) : 0;
        }

        public static void Postfix(bool __result, int __state)
        {
            if (!__result || __state <= 0) return;
            KyberTrade.Component?.Notify_KyberSold(__state, TradeSession.trader?.Faction);
        }
    }

    public class GameComponent_KyberTrade : GameComponent
    {
        public KyberPlotState state = new KyberPlotState();
        public List<Pawn> visitors = new List<Pawn>();

        public GameComponent_KyberTrade(Game game) { }

        public void Notify_KyberSold(int crystals, Faction buyer)
        {
            int now = Find.TickManager.TicksGame;
            bool toCartel = buyer != null && buyer.def.defName == KyberTrade.CartelDefName;
            KyberSaleEffect e = state.RecordSale(crystals, toCartel, now, KyberTrade.Tuning());

            GameComponent vis = KyberTrade.VisibilityComponent();
            float before = VisibilityReflection.Read(vis);
            bool raised = VisibilityReflection.Adjust(vis, e.heat, "[Imperial] kyber sold (" + crystals + ")");
            float after = VisibilityReflection.Read(vis);
            if (toCartel && e.cartelGoodwill != 0)
                buyer.TryAffectGoodwillWith(Faction.OfPlayer, e.cartelGoodwill, canSendMessage: true, canSendHostilityLetter: false,
                    reason: KyberDefOf.RUT_KyberSoldToCartel);

            string heatText = raised
                ? "RUT_KyberSold_Heat".Translate(after.ToString("F0"), (after - before).ToString("F0"), KyberTrade.BandOf(vis)).Resolve()
                : "RUT_KyberSold_NoMeter".Translate().Resolve();
            string text = "RUT_KyberSold".Translate(crystals.ToString(), heatText, state.huttInterest.ToString("F0")).Resolve();
            if (e.firstSale)
                Find.LetterStack.ReceiveLetter("RUT_KyberFirstSaleLabel".Translate(), "RUT_KyberFirstSaleText".Translate(text),
                    LetterDefOf.NegativeEvent, null, buyer);
            else
                Messages.Message(text, MessageTypeDefOf.NegativeEvent, historical: true);
            Log.Message("[KyberTrade] sale " + state.sales + ": " + crystals + " crystal(s) to " + (buyer?.Name ?? "a factionless trader")
                + "; Visibility " + before.ToString("F1") + " -> " + after.ToString("F1") + "; Hutt interest " + state.huttInterest.ToString("F1")
                + (toCartel ? "; Cartel goodwill +" + e.cartelGoodwill : "") + "; visit " + state.visit);
            TryOpenFixerDoor(now);
        }

        public bool VisitCanStillHappen => state.VisitCanStillHappen;

        public void Notify_VisitArrived(List<Pawn> pawns)
        {
            state.VisitArrived();
            visitors = new List<Pawn>(pawns);
        }

        public void Notify_VisitAnswered(bool forthright, Faction homestead, string answerLine)
        {
            if (state.visit != KyberVisitState.Arrived) return;
            int now = Find.TickManager.TicksGame;
            state.VisitAnswered(forthright, now, KyberTrade.Tuning());
            if (forthright)
            {
                if (homestead != null)
                {
                    homestead.TryAffectGoodwillWith(Faction.OfPlayer, KyberTradePlotSettings.homesteadGoodwillForthright, canSendMessage: true,
                        canSendHostilityLetter: false, reason: KyberDefOf.RUT_KyberHomesteadDoorOpened);
                }
                Find.HistoryEventsManager.RecordEvent(new HistoryEvent(KyberDefOf.RUT_KyberHomesteadDoorOpened));
                Find.LetterStack.ReceiveLetter("RUT_KyberVisitForthrightLabel".Translate(), "RUT_KyberVisitForthrightText".Translate(answerLine),
                    LetterDefOf.PositiveEvent, new LookTargets(visitors.Where(p => p != null && p.Spawned)), homestead);
            }
            else
            {
                Messages.Message("RUT_KyberVisitEvasive".Translate(), new LookTargets(visitors.Where(p => p != null && p.Spawned)),
                    MessageTypeDefOf.NeutralEvent, historical: true);
                TryOpenFixerDoor(now);
            }
            Log.Message("[KyberTrade] the Homestead visitors were answered " + (forthright ? "straight" : "with nothing") + "; door " + state.door);
        }

        private void TryOpenFixerDoor(int now)
        {
            if (!KyberTradePlotSettings.kyberTradePlotEnabled) return;
            if (!state.TryOpenFixerDoor(now, KyberTrade.Tuning())) return;
            Faction cartel = Find.FactionManager.AllFactionsListForReading.FirstOrDefault(f => f.def.defName == KyberTrade.CartelDefName);
            Find.LetterStack.ReceiveLetter("RUT_KyberFixerLabel".Translate(), "RUT_KyberFixerText".Translate(state.huttInterest.ToString("F0")),
                LetterDefOf.NeutralEvent, null, cartel);
            Log.Message("[KyberTrade] Hutt interest " + state.huttInterest.ToString("F1") + " opened the fixer's door to the donation");
        }

        public override void GameComponentTick()
        {
            if (Find.TickManager.TicksGame % 250 != 0) return;
            int now = Find.TickManager.TicksGame;
            bool here = visitors.Any(p => p != null && p.Spawned && !p.Dead && p.Faction != null && !p.Faction.HostileTo(Faction.OfPlayer)
                && p.MapHeld != null && p.MapHeld.IsPlayerHome);
            Faction homestead = KyberTrade.Homestead();
            bool canSend = homestead != null && !homestead.HostileTo(Faction.OfPlayer);
            switch (state.NextAction(now, KyberTradePlotSettings.kyberTradePlotEnabled, here, canSend))
            {
                case KyberTickAction.VisitorsLeftUnanswered:
                    state.VisitLeftUnanswered();
                    Messages.Message("RUT_KyberVisitLeft".Translate(), MessageTypeDefOf.NeutralEvent, historical: true);
                    Log.Message("[KyberTrade] the Homestead visitors left unanswered");
                    TryOpenFixerDoor(now);
                    break;
                case KyberTickAction.VisitNeverComes:
                    state.VisitImpossible();
                    Log.Message("[KyberTrade] no friendly Homestead faction to send anyone: the visit will never come");
                    TryOpenFixerDoor(now);
                    break;
                case KyberTickAction.FireVisit:
                    TryFireVisit(now, homestead);
                    break;
                case KyberTickAction.FireDonation:
                    TryFireDonation(now);
                    break;
            }
        }

        private void TryFireVisit(int now, Faction homestead)
        {
            Map map = Find.AnyPlayerHomeMap;
            bool fired = false;
            if (map != null)
            {
                IncidentDef def = KyberDefOf.RUT_KyberHomesteadVisit;
                IncidentParms parms = StorytellerUtility.DefaultParmsNow(def.category, map);
                parms.faction = homestead;
                parms.forced = true;
                fired = def.Worker.CanFireNow(parms) && def.Worker.TryExecute(parms);
            }
            if (!fired) state.VisitPostponed(now, GenDate.TicksPerDay);
        }

        private void TryFireDonation(int now)
        {
            Map map = Find.AnyPlayerHomeMap;
            bool fired = false;
            if (map != null)
            {
                IncidentDef def = KyberDefOf.RUT_GiveQuest_KyberDonationSmuggle;
                IncidentParms parms = StorytellerUtility.DefaultParmsNow(def.category, map);
                parms.forced = true;
                fired = def.Worker.CanFireNow(parms) && def.Worker.TryExecute(parms);
            }
            if (fired)
            {
                state.DonationOffered();
                Log.Message("[KyberTrade] the donation was asked for, through the " + state.door + " door");
            }
            else state.DonationPostponed(now, GenDate.TicksPerDay);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref state.sales, "sales");
            Scribe_Values.Look(ref state.crystalsSold, "crystalsSold");
            Scribe_Values.Look(ref state.huttInterest, "huttInterest");
            Scribe_Values.Look(ref state.lastSaleTick, "lastSaleTick", -1);
            Scribe_Values.Look(ref state.visit, "visit", KyberVisitState.NotDue);
            Scribe_Values.Look(ref state.visitDueTick, "visitDueTick", -1);
            Scribe_Values.Look(ref state.donation, "donation", KyberDonationState.NotDue);
            Scribe_Values.Look(ref state.door, "door", KyberDonationDoor.None);
            Scribe_Values.Look(ref state.donationDueTick, "donationDueTick", -1);
            Scribe_Collections.Look(ref visitors, "visitors", LookMode.Reference);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                visitors = visitors ?? new List<Pawn>();
                visitors.RemoveAll(p => p == null);
            }
        }
    }
}
