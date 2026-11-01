using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;
using Verse.AI.Group;

namespace RimMandrake.RustCathedral
{
    /// <summary>Stage 2/3: the truce yard, peace-talks shape: a world object with an arrival dialog. Only a caravan arrival is
    /// offered, so a transport pod has no way in; a gravship lands on a neighbouring tile and walks.</summary>
    public class RM_RefurbishYard : WorldObject
    {
        private Material cachedMat;

        public RM_DrillRefurbisherExtension Voice => Faction?.def.GetModExtension<RM_DrillRefurbisherExtension>() ?? new RM_DrillRefurbisherExtension();

        public override Material Material
        {
            get
            {
                if (cachedMat == null)
                {
                    cachedMat = MaterialPool.MatFrom(def.texture, ShaderDatabase.WorldOverlayTransparentLit, Faction?.Color ?? Color.white, WorldMaterials.WorldObjectRenderQueue);
                }
                return cachedMat;
            }
        }

        public override IEnumerable<FloatMenuOption> GetFloatMenuOptions(Caravan caravan)
        {
            foreach (FloatMenuOption o in base.GetFloatMenuOptions(caravan))
            {
                yield return o;
            }
            foreach (FloatMenuOption o in CaravanArrivalActionUtility.GetFloatMenuOptions(() => Spawned,
                () => new RM_CaravanArrival_VisitYard(this, attack: false), "Visit " + Label, caravan, Tile, this))
            {
                yield return o;
            }
            foreach (FloatMenuOption o in CaravanArrivalActionUtility.GetFloatMenuOptions(() => Spawned,
                () => new RM_CaravanArrival_VisitYard(this, attack: true), "Attack " + Label + " (voids the work order)", caravan, Tile, this))
            {
                yield return o;
            }
        }

        public override string GetInspectString()
        {
            string s = base.GetInspectString();
            RM_WornBitGame g = RM_WornBitGame.Instance;
            string line = g == null ? null : g.stage == RM_WornBitStage.Refurbishing
                ? "Ready in " + (g.readyTick - Find.TickManager.TicksGame).ToStringTicksToPeriod() + "."
                : g.stage == RM_WornBitStage.AwaitingHead ? "Fee: " + g.fee + " silver." : null;
            return line == null ? s : (s.NullOrEmpty() ? line : s + "\n" + line);
        }

        // ---- the dialog ----

        public void Arrived(Caravan caravan)
        {
            RM_WornBitGame g = RM_WornBitGame.Instance;
            if (g == null)
            {
                return;
            }
            Pawn talker = BestCaravanPawnUtility.FindBestDiplomat(caravan);
            if (g.stage == RM_WornBitStage.AwaitingHead)
            {
                Find.WindowStack.Add(new Dialog_NodeTree(HandOverNode(caravan, g, talker), delayInteractivity: true, radioMode: false, Label));
            }
            else if (g.stage == RM_WornBitStage.ReadyForCollection)
            {
                Find.WindowStack.Add(new Dialog_NodeTree(CollectNode(caravan, g, talker), delayInteractivity: true, radioMode: false, Label));
            }
            else
            {
                Messages.Message("The yard has nothing for you yet.", caravan, MessageTypeDefOf.NeutralEvent, historical: false);
            }
        }

        private DiaNode HandOverNode(Caravan caravan, RM_WornBitGame g, Pawn talker)
        {
            var node = new DiaNode(Voice.greeting + "\n\nThe fee is " + g.fee + " silver, up front.");
            DiaOption pay = new DiaOption("Hand it over and pay " + g.fee + " silver.") { action = delegate { TryHandOver(caravan, g); }, resolveTree = true };
            string missing = HandOverRefusal(caravan, g);
            if (missing != null)
            {
                pay.Disable(missing);
            }
            node.options.Add(pay);
            if (!g.haggled)
            {
                node.options.Add(new DiaOption("Haggle.") { action = delegate { Haggle(g, talker); Find.WindowStack.Add(new Dialog_NodeTree(HandOverNode(caravan, g, talker))); }, resolveTree = true });
            }
            node.options.Add(new DiaOption("Leave.") { resolveTree = true });
            return node;
        }

        private DiaNode CollectNode(Caravan caravan, RM_WornBitGame g, Pawn talker)
        {
            bool demand = g.RollSecondDemand();
            var node = new DiaNode(demand ? Voice.secondDemand + "\n\nThey want another " + g.secondFee + " silver." : "The head is on the slab, ground bright and greased. Take it.");
            if (!demand)
            {
                node.options.Add(new DiaOption("Take the drill head.") { action = delegate { Collect(caravan, g, 0); }, resolveTree = true });
                return node;
            }
            DiaOption pay = new DiaOption("Pay " + g.secondFee + " silver.") { action = delegate { Collect(caravan, g, g.secondFee); }, resolveTree = true };
            if (Silver(caravan) < g.secondFee)
            {
                pay.Disable("not enough silver");
            }
            node.options.Add(pay);
            if (!g.haggled)
            {
                node.options.Add(new DiaOption("Haggle.") { action = delegate { HaggleSecond(g, talker); Find.WindowStack.Add(new Dialog_NodeTree(CollectNode(caravan, g, talker))); }, resolveTree = true });
            }
            node.options.Add(new DiaOption("Fight for it.") { action = delegate { Fight(caravan, g, withHead: true); }, resolveTree = true });
            node.options.Add(new DiaOption("Leave.") { resolveTree = true });
            return node;
        }

        public static string HandOverRefusal(Caravan caravan, RM_WornBitGame g)
        {
            if (!CaravanInventoryUtility.AllInventoryItems(caravan).Any(t => t.def == RM_WornBitDefOf.RM_WornDrillHead))
            {
                return "the drill head is not with this caravan";
            }
            return Silver(caravan) < g.fee ? "not enough silver" : null;
        }

        public static int Silver(Caravan caravan)
        {
            return CaravanInventoryUtility.AllInventoryItems(caravan).Where(t => t.def == ThingDefOf.Silver).Sum(t => t.stackCount);
        }

        public static void PaySilver(Caravan caravan, int amount)
        {
            foreach (Thing t in CaravanInventoryUtility.AllInventoryItems(caravan).Where(x => x.def == ThingDefOf.Silver).ToList())
            {
                if (amount <= 0)
                {
                    break;
                }
                int take = Mathf.Min(amount, t.stackCount);
                t.SplitOff(take).Destroy();
                amount -= take;
            }
        }

        public void TryHandOver(Caravan caravan, RM_WornBitGame g)
        {
            if (HandOverRefusal(caravan, g) != null)
            {
                return;
            }
            Thing head = CaravanInventoryUtility.AllInventoryItems(caravan).First(t => t.def == RM_WornBitDefOf.RM_WornDrillHead);
            PaySilver(caravan, g.fee);
            head.Destroy();
            g.OnHeadHandedOver(g.fee);
        }

        private static void Haggle(RM_WornBitGame g, Pawn talker)
        {
            g.haggled = true;
            int social = talker?.skills?.GetSkill(SkillDefOf.Social)?.Level ?? 0;
            g.fee = RM_WornBitKernel.HaggledFee(g.fee, Rand.Chance(RM_WornBitKernel.HaggleChance(social)));
        }

        private static void HaggleSecond(RM_WornBitGame g, Pawn talker)
        {
            g.haggled = true;
            int social = talker?.skills?.GetSkill(SkillDefOf.Social)?.Level ?? 0;
            g.secondFee = RM_WornBitKernel.HaggledFee(g.secondFee, Rand.Chance(RM_WornBitKernel.HaggleChance(social)));
        }

        public void Collect(Caravan caravan, RM_WornBitGame g, int payment)
        {
            PaySilver(caravan, payment);
            CaravanInventoryUtility.GiveThing(caravan, ThingMaker.MakeThing(RM_WornBitDefOf.RM_RefurbishedDrillHead));
            g.OnHeadCollected();
        }

        /// <summary>The second-demand fight: the head is on the field for whoever holds it. An attack out of nowhere (withHead
        /// false) is the same fight with the order voided and no head to win.</summary>
        public void Fight(Caravan caravan, RM_WornBitGame g, bool withHead)
        {
            Faction faction = Faction;
            if (!faction.HostileTo(Faction.OfPlayer))
            {
                Faction.OfPlayer.TryAffectGoodwillWith(faction, Faction.OfPlayer.GoodwillToMakeHostile(faction), canSendMessage: false, canSendHostilityLetter: false);
            }
            if (!withHead)
            {
                foreach (Thing t in CaravanInventoryUtility.AllInventoryItems(caravan).Where(x => x.def == RM_WornBitDefOf.RM_WornDrillHead).ToList())
                {
                    t.Destroy();
                }
            }
            LongEventHandler.QueueLongEvent(delegate
            {
                IncidentParms parms = StorytellerUtility.DefaultParmsNow(IncidentCategoryDefOf.ThreatBig, caravan);
                parms.faction = faction;
                PawnGroupMakerParms group = IncidentParmsUtility.GetDefaultPawnGroupMakerParms(PawnGroupKindDefOf.Combat, parms, ensureCanGenerateAtLeastOnePawn: true);
                group.generateFightersOnly = true;
                List<Pawn> enemies = PawnGroupMakerUtility.GeneratePawns(group).ToList();
                Map map = CaravanIncidentUtility.SetupCaravanAttackMap(caravan, enemies, sendLetterIfRelatedPawns: false);
                if (enemies.Any())
                {
                    LordMaker.MakeNewLord(faction, new LordJob_AssaultColony(faction), map, enemies);
                }
                Find.TickManager.Notify_GeneratedPotentiallyHostileMap();
                if (withHead)
                {
                    Thing head = ThingMaker.MakeThing(RM_WornBitDefOf.RM_RefurbishedDrillHead);
                    GenPlace.TryPlaceThing(head, enemies.Any() ? enemies[0].Position : map.Center, map, ThingPlaceMode.Near);
                    g.OnHeadCollected();
                }
                else
                {
                    g.VoidOrder();
                }
            }, "GeneratingMapForNewEncounter", doAsynchronously: false, null);
        }
    }

    public class RM_CaravanArrival_VisitYard : CaravanArrivalAction
    {
        private RM_RefurbishYard yard;
        private bool attack;

        public RM_CaravanArrival_VisitYard()
        {
        }

        public RM_CaravanArrival_VisitYard(RM_RefurbishYard yard, bool attack)
        {
            this.yard = yard;
            this.attack = attack;
        }

        public override string Label => attack ? "Attack " + yard.Label : "Visit " + yard.Label;

        public override string ReportString => "CaravanVisiting".Translate(yard.Label);

        public override FloatMenuAcceptanceReport StillValid(Caravan caravan, PlanetTile destinationTile)
        {
            FloatMenuAcceptanceReport report = base.StillValid(caravan, destinationTile);
            if (!report)
            {
                return report;
            }
            return yard != null && yard.Spawned && yard.Tile == destinationTile;
        }

        public override void Arrived(Caravan caravan)
        {
            if (attack)
            {
                yard.Fight(caravan, RM_WornBitGame.Instance, withHead: false);
            }
            else
            {
                yard.Arrived(caravan);
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_References.Look(ref yard, "yard");
            Scribe_Values.Look(ref attack, "attack", false);
        }
    }
}
