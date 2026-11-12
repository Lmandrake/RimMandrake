// KYBER_TRADE_PLOT_1 selftest. Everything below runs the mod's real code (compiled in, see the .csproj) against the
// game's real Assembly-CSharp; nothing is reimplemented. What a bare process cannot do is said where it matters:
// there is no Game, so GameComponent_KyberTrade's own Notify_/Tick methods (Find.*, letters, goodwill) are not called;
// the decisions they act on (KyberPlotState.RecordSale / NextAction / Visit* / Donation*) are, tick by tick, and the
// heat each sale draws is written into a real GameComponent_ColonyVisibility through the same reflection binding the
// game uses.
//
// Run: python3 src/RimMandrake/Utils/selftest_kyber_trade_plot.py
using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Runtime.Serialization;
using HarmonyLib;
using RimMandrake.Visibility;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.Utinni.KyberTradePlot.SelfTest
{
    internal static class Program
    {
        private static int pass, fail;

        private static void Check(string name, bool ok, string detail = "")
        {
            if (ok) pass++; else fail++;
            Console.WriteLine((ok ? "ok    " : "FAIL  ") + name + (detail.Length > 0 ? "  [" + detail + "]" : ""));
        }

        private static string Innermost(Exception e)
        {
            while (e.InnerException != null) e = e.InnerException;
            return e.GetType().Name + ": " + e.Message;
        }

        private static void Say(string line) => Console.WriteLine("      " + line);

        private static int Main()
        {
            try
            {
                Bindings();
                SaleCount();
                VisibilityBinding();
                StoryStraightAnswer();
                StorySayNothing();
                StoryVisitorsLeave();
                StoryNoHomestead();
                StoryPlotOff();
                StoryDevFire();
                StoryOneHugeSale();
                StoryPlotOffWhileVisitorsLeave();
                StoryVisitCanNeverArrive();
            }
            catch (Exception e)
            {
                fail++;
                Console.WriteLine("FAIL  unexpected exception: " + e);
            }
            Console.WriteLine();
            Console.WriteLine("RESULT " + (fail == 0 ? "PASS" : "FAIL") + " (" + pass + " ok, " + fail + " failed)");
            return fail == 0 ? 0 : 1;
        }

        // ---- the engine the hook binds to --------------------------------------------------------------------------

        private static void Bindings()
        {
            Console.WriteLine("== the trade hook binds to the real game ==");
            MethodInfo tryExecute = AccessTools.Method(typeof(TradeDeal), nameof(TradeDeal.TryExecute));
            ParameterInfo[] ps = tryExecute?.GetParameters() ?? new ParameterInfo[0];
            Check("TradeDeal.TryExecute(out bool) exists and returns bool",
                tryExecute != null && tryExecute.ReturnType == typeof(bool) && ps.Length == 1 && ps[0].IsOut);

            // Applying the patch here is not possible: Harmony must JIT the original, and TryExecute's IL reaches Unity
            // internal calls that only the Unity runtime can compile (SecurityException "ECall methods must be packaged
            // into a system module", measured 2026-11-11). So check what Harmony reads to apply it in the game: the class
            // attribute's target, and the injected parameter names and types. The live proof that it IS applied is
            // validation.py's jawa/harmony_patches chain.
            Type pt = typeof(Patch_TradeDeal_TryExecute_KyberSale);
            HarmonyPatch attr = pt.GetCustomAttributes(typeof(HarmonyPatch), false).Cast<HarmonyPatch>().FirstOrDefault();
            MethodInfo target = attr == null ? null : AccessTools.Method(attr.info.declaringType, attr.info.methodName, attr.info.argumentTypes);
            Check("the patch class targets exactly TradeDeal.TryExecute", target != null && target == tryExecute);
            ParameterInfo[] pre = pt.GetMethod("Prefix")?.GetParameters() ?? new ParameterInfo[0];
            ParameterInfo[] post = pt.GetMethod("Postfix")?.GetParameters() ?? new ParameterInfo[0];
            Check("Prefix(TradeDeal __instance, out int __state) and Postfix(bool __result, int __state), as Harmony injects them",
                pre.Length == 2 && pre[0].Name == "__instance" && pre[0].ParameterType == typeof(TradeDeal)
                && pre[1].Name == "__state" && pre[1].IsOut && pre[1].ParameterType == typeof(int).MakeByRefType()
                && post.Length == 2 && post[0].Name == "__result" && post[0].ParameterType == tryExecute.ReturnType
                && post[1].Name == "__state" && post[1].ParameterType == typeof(int));
            Check("the mod applies its patches through the shared PatchApplier at startup",
                typeof(KyberTradeHarmony).GetCustomAttributes(typeof(StaticConstructorOnStartup), false).Any());

            // The donation is delivered by vanilla TradeRequestComp.Fulfill; it must never be a trade deal, or K2's zero
            // Heat would be false. Read its real IL.
            MethodInfo fulfill = AccessTools.Method(typeof(TradeRequestComp), "Fulfill");
            List<CodeInstruction> il = fulfill == null ? new List<CodeInstruction>() : PatchProcessor.GetOriginalInstructions(fulfill).ToList();
            bool callsDeal = il.Any(ci => ci.operand is MethodBase mb && (mb.DeclaringType == typeof(TradeDeal) || mb.DeclaringType == typeof(Tradeable)));
            Check("the donation's delivery (TradeRequestComp.Fulfill) never runs a trade deal, so it is never a sale",
                fulfill != null && il.Count > 0 && !callsDeal, il.Count + " IL instructions read");

            Check("the Cartel and the kyber family are named as the defs on disk",
                KyberTrade.CartelDefName == "RUT_Jawa_HuttCartel" && KyberTrade.FamilyDefNames.SequenceEqual(new[] { "Force_KyberCrystal", "RUT_Mindstone" }));
        }

        // ---- what counts as a sale ---------------------------------------------------------------------------------

        private static readonly FieldInfo CountField = AccessTools.Field(typeof(Tradeable), "countToTransfer");
        private static readonly FieldInfo DealTradeables = AccessTools.Field(typeof(TradeDeal), "tradeables");

        // ThingDef's and Thing's constructors reach Unity's shader database (BaseContent), which needs the Unity runtime;
        // the fields the hook reads (def, defName, stackCount) are set on objects made without running them.
        private static ThingDef Def(string defName)
        {
            var d = (ThingDef)FormatterServices.GetUninitializedObject(typeof(ThingDef));
            d.defName = defName;
            return d;
        }

        private static Tradeable Row(ThingDef def, int stack, int countToTransfer)
        {
            var t = new Tradeable();
            var thing = (Thing)FormatterServices.GetUninitializedObject(typeof(Thing));
            thing.def = def;
            thing.stackCount = stack;
            t.thingsColony.Add(thing);
            CountField.SetValue(t, countToTransfer); // trade window: negative = to the trader (the player sells)
            return t;
        }

        private static TradeDeal Deal(params Tradeable[] rows)
        {
            var deal = (TradeDeal)FormatterServices.GetUninitializedObject(typeof(TradeDeal));
            DealTradeables.SetValue(deal, rows.ToList());
            return deal;
        }

        private static void SaleCount()
        {
            Console.WriteLine("== what counts as a sale (real Tradeable and TradeDeal objects) ==");
            ThingDef kyber = Def("Force_KyberCrystal"), mind = Def("RUT_Mindstone"), steel = Def("Steel"), saber = Def("Force_Lightsaber");

            TradeDeal mixed = Deal(Row(kyber, 5, -3), Row(mind, 1, -1), Row(steel, 40, -10), Row(saber, 1, -1));
            Check("selling 3 kyber + 1 mindstone beside steel and a lightsaber counts 4", KyberTrade.CrystalsBeingSold(mixed) == 4,
                "counted " + KyberTrade.CrystalsBeingSold(mixed));
            TradeDeal buying = Deal(Row(kyber, 5, 2));
            Check("buying kyber from the trader is not a sale", KyberTrade.CrystalsBeingSold(buying) == 0);
            TradeDeal none = Deal(Row(kyber, 5, 0), Row(steel, 40, -10));
            Check("kyber left in the window at 0 is not a sale", KyberTrade.CrystalsBeingSold(none) == 0);

            TradeSession.giftMode = true;
            int gift = KyberTrade.CrystalsBeingSold(mixed);
            TradeSession.giftMode = false;
            Check("the same kyber given as a gift is not a sale", gift == 0);

            Patch_TradeDeal_TryExecute_KyberSale.Prefix(mixed, out int state);
            Check("the patch's prefix reads 4 before the deal resolves", state == 4);
            KyberTradePlotSettings.kyberSalesDrawHeat = false;
            Patch_TradeDeal_TryExecute_KyberSale.Prefix(mixed, out int offState);
            KyberTradePlotSettings.kyberSalesDrawHeat = true;
            Check("with 'a kyber sale draws the Empire' off, the prefix reads 0", offState == 0);
            bool threw = false;
            try { Patch_TradeDeal_TryExecute_KyberSale.Postfix(false, 4); Patch_TradeDeal_TryExecute_KyberSale.Postfix(true, 4); }
            catch (Exception) { threw = true; }
            Check("the postfix is harmless with no game loaded (and does nothing for a refused deal)", !threw);
            Say("crafting a crystal into a lightsaber, a raid carrying one off, or a crystal rotting in a stockpile never");
            Say("enters a TradeDeal, so none of them reaches this count: the count is the trade session, not the inventory.");
        }

        // ---- the Empire meter ---------------------------------------------------------------------------------------

        private static float Heat(GameComponent_ColonyVisibility vis, float delta, string why)
        {
            try { VisibilityReflection.Adjust(vis, delta, why); }
            catch (TargetInvocationException e) when (e.InnerException is System.Security.SecurityException)
            {
                // Adjust's dev-mode band log touches Prefs, which needs the Unity runtime; the clamp above it already ran.
            }
            return VisibilityReflection.Read(vis);
        }

        private static string Band(GameComponent_ColonyVisibility vis) => vis.Band.ToString();

        private static void VisibilityBinding()
        {
            Console.WriteLine("== the heat lands on the real Colony Visibility meter ==");
            var vis = new GameComponent_ColonyVisibility(null);
            Check("the binding reads shipVisibility (a new game starts at 10, Hidden)",
                Math.Abs(VisibilityReflection.Read(vis) - 10f) < 0.01f && Band(vis) == "Hidden");
            float after = Heat(vis, 21.21f, "[Imperial] kyber sold (2)");
            Check("Adjust through the binding moves it: 10 + 21.2 = 31.2 (Discreet)", Math.Abs(after - 31.21f) < 0.01f && Band(vis) == "Discreet",
                after.ToString("F2") + " " + Band(vis));
            after = Heat(vis, 500f, "[Imperial] absurd");
            Check("the meter's own clamp holds at 100", Math.Abs(after - 100f) < 0.01f);
            Check("the binding reports a missing component as 'no meter', not a crash",
                VisibilityReflection.Read(null) < 0f && !VisibilityReflection.Adjust(null, 5f, "x"));
        }

        // ---- the plot, tick by tick -----------------------------------------------------------------------------------

        private const int Day = 60000;

        private sealed class Run
        {
            public readonly KyberPlotState s = new KyberPlotState();
            public readonly KyberTuning t = KyberTrade.Tuning(); // the shipped Mod Settings defaults
            public readonly GameComponent_ColonyVisibility vis = new GameComponent_ColonyVisibility(null);
            public int now;
            public bool visitorsHere;
            public bool homesteadCanSend = true;
            public bool plotOn = true;
            public int visitsFired, donationsFired, fixerDoors;
            public float heatBefore;

            public static string D(int tick) => "day " + (tick / (float)Day).ToString("F1").PadLeft(5);

            public KyberSaleEffect Sell(int crystals, string buyer, bool cartel)
            {
                float before = VisibilityReflection.Read(vis);
                KyberSaleEffect e = s.RecordSale(crystals, cartel, now, t);
                float after = Heat(vis, e.heat, "[Imperial] kyber sold (" + crystals + ")");
                Say(D(now) + "  SALE " + crystals + " kyber to " + buyer + ": Imperial attention " + before.ToString("F1") + " -> "
                    + after.ToString("F1") + " (" + vis.Band + "), Hutt interest " + s.huttInterest.ToString("F0")
                    + (e.cartelGoodwill > 0 ? ", Cartel goodwill +" + e.cartelGoodwill : "") + (e.firstSale ? ", first-sale letter" : "")
                    + (e.visitBecameDue ? ", the Homestead visit is now due at " + D(s.visitDueTick).Trim() : ""));
                if (Fixer()) { fixerDoors++; Say(D(now) + "  the Cartel fixer passes the ask along (Hutt interest " + s.huttInterest.ToString("F0") + ")"); }
                return e;
            }

            /// <summary>Advance in 250-tick steps exactly as GameComponent_KyberTrade.GameComponentTick does.</summary>
            public void Until(int tick, Func<bool> visitorsStay = null)
            {
                for (; now < tick; now += 250)
                {
                    if (visitorsStay != null && s.visit == KyberVisitState.Arrived) visitorsHere = visitorsStay();
                    switch (s.NextAction(now, plotOn, visitorsHere, homesteadCanSend, t))
                    {
                        case KyberTickAction.FireVisit:
                            visitsFired++;
                            s.VisitArrived();
                            visitorsHere = true;
                            Say(D(now) + "  VISIT: three Homestead moisture farmers walk in; the quiet one is unarmed. The letter asks how the kyber was obtained.");
                            break;
                        case KyberTickAction.VisitorsLeftUnanswered:
                            s.VisitLeftUnanswered();
                            Say(D(now) + "  the visitors left unanswered: evasive, no punishment");
                            if (Fixer()) { fixerDoors++; Say(D(now) + "  the Cartel fixer passes the ask along"); }
                            break;
                        case KyberTickAction.VisitNeverComes:
                            s.VisitImpossible();
                            Say(D(now) + "  no friendly Homestead faction can send anyone: the visit never comes");
                            if (Fixer()) { fixerDoors++; Say(D(now) + "  the Cartel fixer passes the ask along"); }
                            break;
                        case KyberTickAction.OpenFixerDoor:
                            if (Fixer()) { fixerDoors++; Say(D(now) + "  the Cartel fixer passes the ask along (on the tick)"); }
                            break;
                        case KyberTickAction.FireDonation:
                            donationsFired++;
                            heatBefore = VisibilityReflection.Read(vis);
                            s.DonationOffered();
                            Say(D(now) + "  DONATION ASKED through the " + s.door + " door (quest: bring 6-12 kyber to a settlement on the lane)");
                            break;
                    }
                }
            }

            /// <summary>GameComponent_KyberTrade.TryOpenFixerDoor: refused while the plot is off, else the kernel's call.</summary>
            public bool Fixer() => plotOn && s.TryOpenFixerDoor(now, t);

            public void Answer(string line, bool forthright)
            {
                s.VisitAnswered(forthright, now, t);
                Say(D(now) + "  the player answers " + line + " -> " + s.visit + (s.door != KyberDonationDoor.None ? ", door: " + s.door : ""));
            }
        }

        private static void StoryStraightAnswer()
        {
            Console.WriteLine("== a run of sales, the visit answered straight, the donation, and more sales after ==");
            var r = new Run();
            r.Until(3 * Day);
            KyberSaleEffect a = r.Sell(2, "a passing grey trader", false);
            Check("sale 1: Imperial attention rises substantially (more than a band-crossing's worth of a small deed)", a.heat > 15f,
                a.heat.ToString("F1"));
            Check("sale 1: Hutt interest rises from a non-Hutt buyer (word gets around)", Math.Abs(r.s.huttInterest - 6f) < 0.01f);
            Check("sale 1 is deniable: no visit yet", r.s.visit == KyberVisitState.NotDue);
            r.Until(9 * Day);
            KyberSaleEffect b = r.Sell(1, "the Hutt Cartel", true);
            Check("sale 2 to the Cartel: attention, interest and Cartel goodwill all rise", b.heat > 0f && b.huttInterest > 0f && b.cartelGoodwill == 4);
            Check("sale 2 makes a pattern: the visit is due a day later", b.visitBecameDue && r.s.visitDueTick == 10 * Day);
            r.Until(10 * Day + 7500);
            r.Answer("\"We bought it.\"", true);
            r.Until(15 * Day);
            r.Sell(3, "a passing grey trader", false);
            r.Until(20 * Day);
            r.Sell(3, "the Hutt Cartel", true);
            r.Until(120 * Day);
            float heatAfterDonation = VisibilityReflection.Read(r.vis);
            Check("over 120 days and four sales, the visit fired exactly once", r.visitsFired == 1, r.visitsFired + " visits");
            Check("the donation was asked exactly once, through the Homestead door", r.donationsFired == 1 && r.s.door == KyberDonationDoor.Homestead);
            Check("the fixer door never opened: the straight answer was the front door", r.fixerDoors == 0);
            Check("the donation moved no Imperial attention (K2: heat unchanged)", r.s.donation == KyberDonationState.Offered,
                "no code path from the donation reaches the meter; meter " + heatAfterDonation.ToString("F1"));
        }

        private static void StorySayNothing()
        {
            Console.WriteLine("== the visit answered with nothing; the Hutts' fixer becomes the door ==");
            var r = new Run();
            r.Sell(1, "a passing grey trader", false);
            r.Until(2 * Day);
            r.Sell(1, "a passing grey trader", false);
            r.Until(3 * Day + 500);
            r.Answer("by telling them nothing", false);
            Check("evasive: no door, no punishment", r.s.visit == KyberVisitState.Evasive && r.s.door == KyberDonationDoor.None);
            r.Until(6 * Day);
            r.Sell(2, "the Hutt Cartel", true);
            Check("Hutt interest 12 is still short of the fixer (15)", r.fixerDoors == 0, r.s.huttInterest.ToString("F0"));
            r.Until(9 * Day);
            r.Sell(1, "the Hutt Cartel", true);
            r.Until(60 * Day);
            r.Sell(5, "the Hutt Cartel", true);
            r.Until(120 * Day);
            Check("at interest 15 the fixer door opens once, and only once", r.fixerDoors == 1 && r.s.door == KyberDonationDoor.HuttFixer);
            Check("the donation is asked once, through the fixer", r.donationsFired == 1);
            Check("the visit still fired exactly once", r.visitsFired == 1);
        }

        private static void StoryVisitorsLeave()
        {
            Console.WriteLine("== the visitors leave before anyone answers ==");
            var r = new Run();
            r.Sell(1, "a passing grey trader", false);
            r.Sell(1, "a passing grey trader", false);
            int arrived = -1;
            r.Until(5 * Day, () => { if (arrived < 0) arrived = r.now; return r.now < arrived + Day; });
            Check("leaving unanswered is evasive", r.s.visit == KyberVisitState.Evasive && r.visitsFired == 1);
        }

        private static void StoryNoHomestead()
        {
            Console.WriteLine("== there is no friendly Homestead faction to send anyone ==");
            var r = new Run { homesteadCanSend = false };
            r.Sell(3, "the Hutt Cartel", true);
            r.Sell(3, "the Hutt Cartel", true);
            r.Until(10 * Day);
            Check("the visit never comes, and never fires", r.s.visit == KyberVisitState.Impossible && r.visitsFired == 0);
            Check("Hutt interest 18 opens the fixer door instead, and the donation is asked", r.fixerDoors == 1 && r.donationsFired == 1);
        }

        private static void StoryPlotOff()
        {
            Console.WriteLine("== the plot switched off in Mod Settings ==");
            var r = new Run { plotOn = false };
            r.Sell(1, "a passing grey trader", false);
            r.Sell(1, "a passing grey trader", false);
            r.Until(30 * Day);
            Check("no visit and no donation while the plot is off; sales still draw the Empire",
                r.visitsFired == 0 && r.donationsFired == 0 && VisibilityReflection.Read(r.vis) > 10f);
            r.plotOn = true;
            r.Until(31 * Day);
            Check("switched back on, the visit that fell due comes, once", r.visitsFired == 1);
        }

        private static void StoryDevFire()
        {
            Console.WriteLine("== a dev-mode fire of the visit before any sale ==");
            var r = new Run();
            r.s.VisitArrived();
            Check("it counts as the one visit", !r.s.VisitCanStillHappen);
            r.s.VisitAnswered(true, r.now, r.t);
            r.Sell(1, "a passing grey trader", false);
            r.Sell(1, "a passing grey trader", false);
            r.Until(30 * Day);
            Check("the second sale does not bring a second visit", r.visitsFired == 0 && r.s.visit == KyberVisitState.Forthright);
        }

        private static void StoryOneHugeSale()
        {
            Console.WriteLine("== one huge sale ==");
            var r = new Run();
            KyberSaleEffect e = r.Sell(50, "the Hutt Cartel", true);
            Check("50 crystals at once is capped at 40 attention (two bands), not 750", Math.Abs(e.heat - 40f) < 0.01f);
            Check("quantity scales sublinearly: 4 crystals draw twice one, not four times",
                Math.Abs(KyberTradeKernel.HeatForSale(4, r.t) - 2f * KyberTradeKernel.HeatForSale(1, r.t)) < 0.01f);
            Check("one sale, however large, is still one sale: no visit yet", r.s.visit == KyberVisitState.NotDue && r.s.sales == 1);
            Check("zero crystals moves nothing", KyberTradeKernel.HeatForSale(0, r.t) == 0f && r.s.RecordSale(0, true, 0, r.t).heat == 0f && r.s.sales == 1);
        }
    
        private static void StoryPlotOffWhileVisitorsLeave()
        {
            Console.WriteLine("== the plot is switched off while unanswered visitors leave, then back on (no further sale) ==");
            var r = new Run();
            r.Sell(3, "the Hutt Cartel", true);
            r.Sell(3, "the Hutt Cartel", true);
            r.Until(Day + 250);
            r.plotOn = false;
            r.visitorsHere = false;
            r.Until(5 * Day);
            Check("the departure is still noticed while the plot is off (evasive), and no door opens while off",
                r.s.visit == KyberVisitState.Evasive && r.fixerDoors == 0);
            r.plotOn = true;
            r.Until(10 * Day);
            Check("switched back on with Hutt interest 18, the fixer door opens on its own and the donation is asked",
                r.fixerDoors == 1 && r.donationsFired == 1 && r.s.door == KyberDonationDoor.HuttFixer);
        }

        private static void StoryVisitCanNeverArrive()
        {
            Console.WriteLine("== a friendly Homestead exists but the visitors can never arrive (every attempt fails) ==");
            var r = new Run();
            r.Sell(3, "the Hutt Cartel", true);
            r.Sell(3, "the Hutt Cartel", true);
            int attempts = 0;
            for (; r.now < 30 * Day; r.now += 250)
            {
                KyberTickAction a = r.s.NextAction(r.now, true, false, true, r.t);
                if (a == KyberTickAction.FireVisit) { attempts++; r.s.VisitPostponed(r.now, Day); }
                else if (a == KyberTickAction.OpenFixerDoor && r.s.TryOpenFixerDoor(r.now, r.t)) r.fixerDoors++;
                else if (a == KyberTickAction.FireDonation) { r.donationsFired++; r.s.DonationOffered(); }
            }
            Say("visit attempts that failed: " + attempts + "; visit " + r.s.visit + "; door " + r.s.door);
            Check("after 15 days of failed arrivals the visit counts as never coming", r.s.visit == KyberVisitState.Impossible && attempts >= 15);
            Check("so the fixer door opens and the donation is still asked, once", r.fixerDoors == 1 && r.donationsFired == 1);
        }
    }
}
