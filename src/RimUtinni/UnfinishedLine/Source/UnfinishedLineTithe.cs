using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using RimWorld.QuestGen;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.UnfinishedLine
{
    /// <summary>
    /// UNFINISHED_LINE_TITHE_BEAT_1 — beat 4 "The Tithe and the Hands" (design droid_mass_production_quest_chain_2026-10-02.md §2.4).
    ///
    /// The Hive's gap is resources and capacity, so the player pays both: a material tithe and one skilled crafter lent to
    /// the line. The beat is stock vanilla shape (Script_PawnLend's: QuestNode_ShuttleDelay + Util_TransportShip_Pickup +
    /// QuestPart_LendColonistsToFaction) with ONE shuttle carrying both asks: its requiredItems is the tithe basket and its
    /// requireColonistCount is 1. Three small pieces here:
    ///   QuestNode_RUT_TitheSetup   the basket scaled by the Mod Setting (requiredItems + a mass override so 3x still
    ///                              fits), the lend faction, the timings and the skill floor, into the slate; TestRun
    ///                              fails (the spine waits) while no free colonist reaches the skill floor.
    ///   QuestNode_RUT_LineHands    the vanilla lend part without its Pawn "asker" (the lend goes to a faction), plus the
    ///                              Crafting XP gift on return and the skill gate on the shuttle.
    ///   CompShuttle_IsAllowed      Harmony postfix: this beat's shuttle refuses colonists below the skill floor. IsAllowed
    ///                              is what the load dialog (TransporterUtility), the carry float menu (IsAllowedNow) and
    ///                              JobDriver_EnterTransporter all ask (decompiled 1.6), so one postfix covers every route.
    ///
    /// Where: the chosen site (UNFINISHED_LINE_SITE_CHOICE_1) decides who the hands are lent to (UNFINISHED_LINE_SITE_BEATS_1,
    /// LineSiteBeats.LendFaction). The caravan TradeRequests to the site's settlement are NOT built, so the beat happens at
    /// your colony: an Enclave shuttle collects the tithe and the hands. The monument blueprint (site B) is cut.
    /// All numbers PROVISIONAL (Mod Settings).
    /// </summary>
    public static class LineTithe
    {
        // PROVISIONAL, design §2.4: the basket at 1x tithe scale.
        public const int BasePlasteel = 300;
        public const int BaseComponents = 40;
        public const int BaseSteel = 800;
        public const int BaseUranium = 60;

        public static int Scaled(int baseCount)
        {
            return Mathf.Max(1, Mathf.RoundToInt(baseCount * UnfinishedLineSettings.titheScale));
        }

        public static List<ThingDefCount> Basket()
        {
            return new List<ThingDefCount>
            {
                new ThingDefCount(ThingDefOf.Plasteel, Scaled(BasePlasteel)),
                new ThingDefCount(ThingDefOf.ComponentIndustrial, Scaled(BaseComponents)),
                new ThingDefCount(ThingDefOf.Steel, Scaled(BaseSteel)),
                new ThingDefCount(ThingDefOf.Uranium, Scaled(BaseUranium))
            };
        }

        public static string BasketText(List<ThingDefCount> basket)
        {
            return basket.Select(t => t.Count + " " + t.ThingDef.label).ToCommaList(useAnd: true);
        }

        public static int MinCrafting => UnfinishedLineSettings.lendSkillGateEnabled ? UnfinishedLineSettings.lendMinCrafting : 0;

        public static int CraftingOf(Pawn p)
        {
            SkillRecord s = p?.skills?.GetSkill(SkillDefOf.Crafting);
            return s == null || s.TotallyDisabled ? 0 : s.Level;
        }

        public static bool Qualifies(Pawn p, int minCrafting)
        {
            return minCrafting <= 0 || CraftingOf(p) >= minCrafting;
        }

        /// <summary>The faction the hands are lent to: the Hive (its gap is capacity) unless it is hostile to you, then the
        /// Enclaves, who run the line beside it.</summary>
        public static Faction LendFaction()
        {
            Faction site = LineSiteBeats.LendFaction();
            if (site != null) return site;
            Faction hive = LineFactions.Hive;
            if (hive != null && !hive.defeated && !hive.HostileTo(Faction.OfPlayer)) return hive;
            return LineFactions.Enclaves;
        }

        public static bool AnyQualifiedColonist(Map map, int minCrafting)
        {
            IEnumerable<Pawn> pool = map != null ? map.mapPawns.FreeColonistsSpawned : PawnsFinder.AllMaps_FreeColonistsSpawned;
            return pool.Any(p => !p.IsQuestLodger() && Qualifies(p, minCrafting));
        }
    }

    public class QuestNode_RUT_TitheSetup : QuestNode
    {
        [NoTranslate] public string storeItemsAs = "titheItems";
        [NoTranslate] public string storeTextAs = "titheText";
        [NoTranslate] public string storeMassAs = "titheMass";
        [NoTranslate] public string storeLendFactionAs = "lendFaction";
        [NoTranslate] public string storeDeadlineAs = "titheTicks";
        [NoTranslate] public string storeLendTicksAs = "lendTicks";
        [NoTranslate] public string storeMinCraftingAs = "minCrafting";

        private void Store(Slate slate)
        {
            List<ThingDefCount> basket = LineTithe.Basket();
            float mass = basket.Sum(t => t.ThingDef.GetStatValueAbstract(StatDefOf.Mass) * t.Count);
            slate.Set(storeItemsAs, basket);
            slate.Set(storeTextAs, LineTithe.BasketText(basket));
            // vanilla shuttle capacity is 2000 kg; room for the basket, the crafter and their gear at any scale
            slate.Set(storeMassAs, Mathf.Max(2000f, mass * 1.25f + 250f));
            slate.Set(storeLendFactionAs, LineTithe.LendFaction());
            slate.Set(storeDeadlineAs, (int)(UnfinishedLineSettings.titheDeadlineDays * GenDate.TicksPerDay));
            slate.Set(storeLendTicksAs, (int)(UnfinishedLineSettings.lendDays * GenDate.TicksPerDay));
            slate.Set(storeMinCraftingAs, LineTithe.MinCrafting);
        }

        protected override bool TestRunInt(Slate slate)
        {
            if (LineTithe.LendFaction() == null) return false;
            if (!LineTithe.AnyQualifiedColonist(slate.Get<Map>("map"), LineTithe.MinCrafting)) return false;
            Store(slate);
            return true;
        }

        protected override void RunInt()
        {
            Store(QuestGen.slate);
        }
    }

    /// <summary>Marks this beat's shuttle for the skill gate. Plain QuestPart: it holds for the quest's life and the
    /// postfix asks it nothing once the shuttle has gone.</summary>
    public class QuestPart_RUT_TitheShuttle : QuestPart
    {
        public Thing shuttle;
        public int minCrafting;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_References.Look(ref shuttle, "shuttle");
            Scribe_Values.Look(ref minCrafting, "minCrafting", 0);
        }
    }

    /// <summary>The colonist comes home with what they learned on the line: Crafting XP for each lent pawn still alive.</summary>
    public class QuestPart_RUT_LineHandsReturn : QuestPart
    {
        public string inSignal;
        public bool given;

        // QuestPart is not ILoadReferenceable, so the lend is found on the quest rather than Scribed
        private QuestPart_LendColonistsToFaction Lend => quest?.PartsListForReading.OfType<QuestPart_LendColonistsToFaction>().FirstOrDefault();

        public override void Notify_QuestSignalReceived(Signal signal)
        {
            base.Notify_QuestSignalReceived(signal);
            if (given || signal.tag != inSignal) return;
            given = true;
            Give();
        }

        public int Give()
        {
            float xp = UnfinishedLineSettings.lendCraftingXp;
            QuestPart_LendColonistsToFaction lend = Lend;
            if (lend == null || xp <= 0f) return 0;
            int n = 0;
            foreach (Thing t in lend.LentColonistsListForReading)
            {
                if (t is Pawn p && !p.Dead && p.skills != null)
                {
                    p.skills.Learn(SkillDefOf.Crafting, xp, direct: true);
                    n++;
                }
            }
            return n;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref inSignal, "inSignal");
            Scribe_Values.Look(ref given, "given", false);
        }
    }

    /// <summary>Emits the lend (vanilla QuestPart_LendColonistsToFaction, built here because QuestNode_LendColonistsToFaction
    /// takes a Pawn asker and this lend goes to a faction) and the XP gift. Reads $pickupShipThing, $lendFaction, $lendTicks,
    /// $map. Enabled by the node's inSignal (inside a QuestNode_Signal: the shuttle leaving satisfied).</summary>
    public class QuestNode_RUT_LineHands : QuestNode
    {
        [NoTranslate] public SlateRef<string> outSignalComplete;
        [NoTranslate] public SlateRef<string> outSignalColonistsDied;

        protected override bool TestRunInt(Slate slate) => true;

        protected override void RunInt()
        {
            Slate slate = QuestGen.slate;
            string inSignal = slate.Get<string>("inSignal");
            Thing shuttle = slate.Get<Thing>("pickupShipThing");
            QuestPart_LendColonistsToFaction lend = new QuestPart_LendColonistsToFaction
            {
                inSignalEnable = inSignal,
                shuttle = shuttle,
                lendColonistsToFaction = slate.Get<Faction>("lendFaction"),
                returnLentColonistsInTicks = slate.Get<int>("lendTicks"),
                returnMap = slate.Get<Map>("map")?.Parent
            };
            string complete = outSignalComplete.GetValue(slate);
            string completeSignal = complete.NullOrEmpty() ? null : QuestGenUtility.HardcodedSignalWithQuestID(complete);
            if (completeSignal != null) lend.outSignalsCompleted.Add(completeSignal);
            string died = outSignalColonistsDied.GetValue(slate);
            if (!died.NullOrEmpty()) lend.outSignalColonistsDied = QuestGenUtility.HardcodedSignalWithQuestID(died);
            QuestGen.quest.AddPart(lend);
            QuestGen.quest.TendPawnsWithMedicine(ThingDefOf.MedicineIndustrial, allowSelfTend: true, pawnsInTransporter: shuttle, inSignal: inSignal);
            QuestGen.quest.AddPart(new QuestPart_RUT_LineHandsReturn { inSignal = completeSignal });
        }
    }

    /// <summary>Emits <see cref="QuestPart_RUT_TitheShuttle"/> for $pickupShipThing with the $minCrafting floor.</summary>
    public class QuestNode_RUT_TitheShuttleGate : QuestNode
    {
        protected override bool TestRunInt(Slate slate) => true;

        protected override void RunInt()
        {
            Slate slate = QuestGen.slate;
            QuestGen.quest.AddPart(new QuestPart_RUT_TitheShuttle
            {
                shuttle = slate.Get<Thing>("pickupShipThing"),
                minCrafting = slate.Get<int>("minCrafting")
            });
        }
    }

    [StaticConstructorOnStartup]
    public static class UnfinishedLineHarmony
    {
        static UnfinishedLineHarmony()
        {
            RimMandrake.Shared.PatchApplier.Apply(new Harmony("mandrake.rut.unfinishedline"), Assembly.GetExecutingAssembly(), "RimUtinni.UnfinishedLine");
        }
    }

    [HarmonyPatch(typeof(CompShuttle), nameof(CompShuttle.IsAllowed))]
    public static class CompShuttle_IsAllowed_TitheSkillGate
    {
        public static void Postfix(CompShuttle __instance, Thing t, ref bool __result)
        {
            if (!__result || !(t is Pawn p) || !p.IsColonist) return;
            Thing ship = __instance.parent;
            // cheap reject first: only an Enclave-owned shuttle can be this beat's
            if (ship?.Faction == null || ship.Faction.def.defName != LineFactions.EnclavesDefName) return;
            int min = MinCraftingFor(ship);
            if (min > 0 && !__instance.IsRequired(t) && LineTithe.CraftingOf(p) < min)
            {
                __result = false;
            }
        }

        public static int MinCraftingFor(Thing ship)
        {
            foreach (Quest q in Find.QuestManager.QuestsListForReading)
            {
                if (q.State != QuestState.Ongoing) continue;
                foreach (QuestPart part in q.PartsListForReading)
                {
                    if (part is QuestPart_RUT_TitheShuttle g && g.shuttle == ship) return g.minCrafting;
                }
            }
            return 0;
        }
    }

    // jawa/static_call proof (validation.py, tithe).
    public static class UnfinishedLineTitheProof
    {
        public static string ProofTitheSetup()
        {
            List<ThingDefCount> basket = LineTithe.Basket();
            Faction lend = LineTithe.LendFaction();
            int min = LineTithe.MinCrafting;
            return "TITHE " + LineTithe.BasketText(basket) + " | scale " + UnfinishedLineSettings.titheScale
                + " | lend to " + (lend?.def.defName ?? "none") + " | min crafting " + min
                + " | qualified colonist " + LineTithe.AnyQualifiedColonist(Find.AnyPlayerHomeMap, min);
        }
    }
}
