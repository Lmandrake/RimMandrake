using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.Utinni.ScavengerEvents
{
    /// <summary>
    /// RUT_SCAVENGEREVENTS_BUILD_1, mechanism 8 of 8 (mechanism reference:
    /// infrastructure/state/items/RUT_SCAVENGEREVENTS_BUILD_1.md). Unconditional:
    /// picks ONE random tradeable, non-equipment ThingDef worth 20-200 (and
    /// not a hatchable egg -- verified from the donor's own filter lambda),
    /// drops repeated stacks of it worth a Rand(150,900) total budget (capped
    /// at 25 stacks, which the value budget almost always exhausts first),
    /// plus two SpaceRefugee-kind pawns from a random non-hostile faction --
    /// one alive and downed, one dead as a corpse -- each in its own drop
    /// pod. Ported behavior-not-bugs from MoreIncidents.MOIncidentWorker_ShipBreak
    /// (donor letter keys were MO_CargoRain, not "ShipBreak" -- the class
    /// name and the shipped incident don't match).
    /// </summary>
    public class IncidentWorker_ShipBreak : IncidentWorker
    {
        private const int DropRadius = 110;
        private const int OpenDelayTicks = 180;
        private const float MinBudget = 150f;
        private const float MaxBudget = 900f;
        private const int MinStack = 20;
        private const int MaxStack = 40;
        private const int MaxLootStacks = 25;
        private const float MinLootValue = 20f;
        private const float MaxLootValue = 200f;

        protected override bool CanFireNowSub(IncidentParms parms)
        {
            return ScavengerEventsSettings.shipBreakEnabled && base.CanFireNowSub(parms);
        }

        protected override bool TryExecuteWorker(IncidentParms parms)
        {
            var map = (Map)parms.target;

            ThingDef lootDef = RandomPodContentsDef();
            if (lootDef == null)
                return false;

            var loot = BuildLoot(lootDef);

            IntVec3 refugeeDropSpot = DropCellFinder.RandomDropSpot(map);
            IntVec3 corpseDropSpot = DropCellFinder.RandomDropSpot(map);
            IntVec3 lootDropSpot = DropCellFinder.RandomDropSpot(map);

            Faction faction = Find.FactionManager.RandomNonHostileFaction(true, true, true, TechLevel.Neolithic);
            if (faction == null)
                return false;

            var survivorRequest = new PawnGenerationRequest(PawnKindDefOf.SpaceRefugee, faction, PawnGenerationContext.NonPlayer);
            var victimRequest = new PawnGenerationRequest(PawnKindDefOf.SpaceRefugee, faction, PawnGenerationContext.NonPlayer);
            Pawn survivor = PawnGenerator.GeneratePawn(survivorRequest);
            Pawn victim = PawnGenerator.GeneratePawn(victimRequest);

            HealthUtility.DamageUntilDowned(survivor);
            HealthUtility.DamageUntilDead(victim);
            Corpse corpse = (Corpse)ThingMaker.MakeThing(victim.RaceProps.corpseDef);
            corpse.InnerPawn = victim;

            DropPodUtility.MakeDropPodAt(refugeeDropSpot, map, new ActiveTransporterInfo
            {
                SingleContainedThing = survivor,
                openDelay = OpenDelayTicks,
                leaveSlag = true,
            });
            DropPodUtility.MakeDropPodAt(corpseDropSpot, map, new ActiveTransporterInfo
            {
                SingleContainedThing = corpse,
                openDelay = OpenDelayTicks,
                leaveSlag = true,
            });
            DropPodUtility.DropThingsNear(lootDropSpot, map, loot, DropRadius, false, false, true, true, true, null);

            Find.LetterStack.ReceiveLetter(
                "RUT_CargoRain".Translate(),
                "RUT_CargoRainDesc".Translate(),
                LetterDefOf.PositiveEvent,
                new TargetInfo(refugeeDropSpot, map));

            return true;
        }

        private static List<Thing> BuildLoot(ThingDef lootDef)
        {
            var loot = new List<Thing>();
            float budget = Rand.Range(MinBudget, MaxBudget) * ScavengerEventsSettings.shipBreakLootMultiplier;
            float unitValue = lootDef.BaseMarketValue;

            while (loot.Count < MaxLootStacks && budget > unitValue)
            {
                Thing stack = ThingMaker.MakeThing(lootDef);
                int count = Rand.RangeInclusive(MinStack, MaxStack);
                count = System.Math.Min(count, stack.def.stackLimit);
                if (count * unitValue > budget)
                    count = UnityEngine.Mathf.FloorToInt(budget / unitValue);
                if (count <= 0)
                    count = 1;

                stack.stackCount = count;
                loot.Add(stack);
                budget -= count * unitValue;
            }

            return loot;
        }

        private static ThingDef RandomPodContentsDef()
        {
            return DefDatabase<ThingDef>.AllDefsListForReading
                .Where(d => d.category == ThingCategory.Item
                    && d.tradeability == Tradeability.All
                    && d.equipmentType == EquipmentType.None
                    && d.BaseMarketValue >= MinLootValue
                    && d.BaseMarketValue < MaxLootValue
                    && !d.HasComp(typeof(CompHatcher)))
                .RandomElementWithFallback();
        }
    }
}
