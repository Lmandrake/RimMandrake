using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.DivingInteraction
{
    // ════════════════════════════════════════════════════════════════════
    // GREYSEA_BRINE_ELDERS_1 — the novelty trade itself, plus the dissolve.
    //
    // 🔴 NOT A TraderKindDef. The prior FOUNDRY note is explicit that nothing
    // in vanilla trades on novelty, and the sheet's own words are "not a
    // TraderKindDef; a new trade mechanism". This is that mechanism: a
    // direct exchange invoked from Dialog_OfferToElder, valued only by
    // whether THIS TILE's Elder has ever seen the offered thing's kind
    // before — "technology fascinates them but is conceptually opaque",
    // so MarketValue and techLevel never gate acceptance, only the reward
    // size.
    //
    // THE DISSOLVE (owed piece #3) IS FOLDED INTO THE REWARD DELIVERY, not a
    // separate trigger — this is what the prior note meant by "trivial once
    // the trade exists": the sheet's own words are that ejecting an object
    // "up from the brine" happens "AS PART OF AN EXCHANGE". So a successful
    // trade's payout is delivered by dissolving one nearby RM_BrineJacket
    // (DestroyMode.Vanish — no mining yield, because this is the Elder
    // reshaping its own floor, not a pawn with a pick) or, if none stands
    // nearby, ejecting the reward straight onto the pool's shore.
    // ════════════════════════════════════════════════════════════════════
    public static class RM_ElderTradeUtility
    {
        // Silver multipliers and floors live in RM_ElderEconomyKernel (offline-fuzzed).
        private const float UniqueTreasureChance = 0.35f; // on a novel trade only
        private const float DissolveSearchRadius = 12f;
        private const int WideDeliverySearchRadius = 40; // fallback scan if nothing dry stands within DissolveSearchRadius

        // Candidate pool for "one of each, per world": every ThingDef carrying RM_ElderTreasureExtension
        // (ELDER_TREASURE_TAG_TABLE_1). RM_ treasures are marked in TerminalBiomes; the canon treasures are
        // marked by the Utinni patch layer on their own RUT_ defs. Sorted by defName so the draw is stable.
        private static string[] treasureDefNames;
        private static string[] RmUniqueTreasureDefNames
        {
            get
            {
                if (treasureDefNames == null)
                {
                    var names = new List<string>();
                    List<ThingDef> all = DefDatabase<ThingDef>.AllDefsListForReading;
                    for (int i = 0; i < all.Count; i++)
                    {
                        if (all[i].HasModExtension<RM_ElderTreasureExtension>()) names.Add(all[i].defName);
                    }
                    names.Sort(string.CompareOrdinal);
                    treasureDefNames = names.ToArray();
                }
                return treasureDefNames;
            }
        }

        public static int TileForMap(Map map)
        {
            if (map?.Parent is PocketMapParent pmp && pmp.sourceMap != null)
            {
                return pmp.sourceMap.Tile;
            }
            return map?.Tile ?? -1;
        }

        /// <summary>"a newly encountered life form, corpse, xenotype, tissue,
        /// mineral, or unfamiliar material" — [INVENTED, flagged] collapsed
        /// to one string key: a corpse or living pawn keys on its xenotype
        /// (if non-baseline) or else its kind, everything else keys on its
        /// own def. Good enough to make "the same kind of thing" and "a
        /// genuinely new kind of thing" distinguishable; a finer-grained
        /// scheme (by tissue type, by mineral composition) is future
        /// tuning, not a blocker.</summary>
        public static string NoveltyKey(Thing t)
        {
            Pawn innerPawn = null;
            if (t is Corpse corpse)
            {
                innerPawn = corpse.InnerPawn;
            }
            else if (t is Pawn livePawn)
            {
                innerPawn = livePawn;
            }

            if (innerPawn != null)
            {
                string xeno = innerPawn.genes?.Xenotype?.defName;
                if (!xeno.NullOrEmpty() && xeno != "Baseliner")
                {
                    return "Xenotype:" + xeno;
                }
                return "Lifeform:" + innerPawn.kindDef.defName;
            }
            return "Material:" + t.def.defName;
        }

        public readonly struct OfferResult
        {
            public readonly bool Accepted;
            public readonly bool WasNovel;
            public readonly int SilverGranted;
            public readonly ThingDef UniqueTreasureGranted;

            public OfferResult(bool accepted, bool wasNovel, int silverGranted, ThingDef uniqueTreasureGranted)
            {
                Accepted = accepted;
                WasNovel = wasNovel;
                SilverGranted = silverGranted;
                UniqueTreasureGranted = uniqueTreasureGranted;
            }
        }

        /// <summary>Executes the trade: consumes `offered` entirely, records
        /// the novelty key against this map's world tile, and delivers a
        /// reward by dissolving the floor. Caller (Dialog_OfferToElder) owns
        /// all messaging/confirmation UI.</summary>
        public static OfferResult Offer(RM_Building_BrineElder elder, Thing offered)
        {
            // Destructive call: validate here, not only in the dialog's list (a stale
            // confirmation can outlive the item, its map, or the setting).
            Map map = elder?.Map;
            if (map == null || !elder.Spawned || offered == null || offered.Destroyed || !offered.Spawned
                || offered.Map != map || Current.Game == null
                || !RM_DivingSettings.masterEnabled || !RM_DivingSettings.greyElderTradeEnabled)
            {
                return new OfferResult(false, false, 0, null);
            }

            // Find the payout cell BEFORE anything is committed: no dry cell, no trade.
            IntVec3 deliveryCell = FindDeliveryCell(elder, out Thing jacketToDissolve);
            if (!deliveryCell.IsValid)
            {
                return new OfferResult(false, false, 0, null);
            }

            int tile = TileForMap(map);
            RM_GameComponent_BrineElders comp = Current.Game.GetComponent<RM_GameComponent_BrineElders>();
            string key = NoveltyKey(offered);
            RM_ElderEconomyKernel.Decision decision = comp != null
                ? comp.Decide(tile, key, tile >= 0, offered.MarketValue, offered.stackCount, RmUniqueTreasureDefNames,
                    dn => DefDatabase<ThingDef>.GetNamedSilentFail(dn) != null,
                    () => Rand.Chance(UniqueTreasureChance), n => Rand.Range(0, n))
                : new RM_ElderEconomyKernel.Decision { Silver = RM_ElderEconomyKernel.SilverFor(false, offered.MarketValue, offered.stackCount) };
            bool novel = decision.Novel;
            int silver = decision.Silver;
            ThingDef uniqueTreasure = decision.Treasure == null ? null : DefDatabase<ThingDef>.GetNamedSilentFail(decision.Treasure);

            offered.Destroy(DestroyMode.Vanish);

            if (jacketToDissolve != null)
            {
                // Dissolved, not mined: the Elder is reshaping its own
                // floor, so no RM_RawSalt mining yield — the sheet's word is
                // "dissolving", never "chiselled".
                jacketToDissolve.Destroy(DestroyMode.Vanish);
            }

            if (deliveryCell.IsValid && map != null)
            {
                if (uniqueTreasure != null)
                {
                    Thing t = ThingMaker.MakeThing(uniqueTreasure);
                    GenPlace.TryPlaceThing(t, deliveryCell, map, ThingPlaceMode.Near);
                }
                else if (silver > 0)
                {
                    Thing silverThing = ThingMaker.MakeThing(ThingDefOf.Silver);
                    silverThing.stackCount = silver;
                    GenPlace.TryPlaceThing(silverThing, deliveryCell, map, ThingPlaceMode.Near);
                }
            }

            return new OfferResult(true, novel, uniqueTreasure != null ? 0 : silver, uniqueTreasure);
        }

        /// <summary>Picks the jacket cell the payout should erupt from, or
        /// (if none stands within reach) a cell on the pool's own margin.
        /// Never returns a cell underwater — the reward has to be
        /// recoverable, not resunk.</summary>
        private static IntVec3 FindDeliveryCell(RM_Building_BrineElder elder, out Thing jacketToDissolve)
        {
            jacketToDissolve = null;
            Map map = elder.Map;
            if (map == null)
            {
                return IntVec3.Invalid;
            }
            ThingDef jacketDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_BrineJacket");
            if (jacketDef != null)
            {
                Thing nearest = GenRadial.RadialDistinctThingsAround(elder.Position, map, DissolveSearchRadius, true)
                    .Where(t => t.def == jacketDef)
                    .OrderBy(t => t.Position.DistanceToSquared(elder.Position))
                    .FirstOrDefault();
                if (nearest != null && !nearest.Position.GetTerrain(map).IsWater)
                {
                    jacketToDissolve = nearest;
                    return nearest.Position;
                }
            }

            foreach (IntVec3 c in GenRadial.RadialCellsAround(elder.Position, DissolveSearchRadius, false))
            {
                if (!c.InBounds(map) || c.GetTerrain(map).IsWater || !c.Standable(map))
                {
                    continue;
                }
                return c;
            }

            // BUG FIXED 2026-09-26: the Elder itself is spawned inside the deep-pool
            // basin (GenStep_GreySeaFloorDressing.PlaceElder), which is guaranteed
            // RM_BrinePoolDeep — Water terrain (TerrainDef.IsWater => HasTag("Water")).
            // A pool basin plus its margin (radius 8.6) can fill the whole
            // DissolveSearchRadius (12) when jackets/formations pack the ring, so the
            // loop above can come up empty even though the doc comment above promises
            // "never returns a cell underwater". Falling straight back to
            // elder.Position used to violate that promise on exactly the maps where it
            // matters most, silently sinking the player's payout. Widen the search
            // before giving up.
            if (CellFinder.TryFindRandomCellNear(elder.Position, map, WideDeliverySearchRadius,
                c => c.InBounds(map) && !c.GetTerrain(map).IsWater && c.Standable(map), out IntVec3 wide))
            {
                return wide;
            }
            // Never elder.Position: that is deep brine (see above). No dry cell means no trade.
            return IntVec3.Invalid;
        }
    }
}
