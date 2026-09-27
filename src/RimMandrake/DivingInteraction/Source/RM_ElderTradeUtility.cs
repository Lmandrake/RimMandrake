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
        private const float NovelValueMultiplier = 8f;
        private const int NovelValueFloor = 50;
        private const float StaleValueMultiplier = 0.05f;
        private const int StaleValueFloor = 1;
        private const float UniqueTreasureChance = 0.35f; // on a novel trade only
        private const float DissolveSearchRadius = 12f;

        // Candidate pool for "one of each, per world". RM_ tier only —
        // Q11a routes the three canon treasures (lightsaber, pre-Republic
        // navcore, droid brain) through the Utinni patch layer, which is
        // expected to append its own defNames to an Elder treasure table
        // by patch, not by editing this array. Kept as a plain list rather
        // than a def-driven query because there is no shared
        // ThingCategoryDef/tag for "Elder treasure" yet — see the header of
        // RM_ElderTreasures.xml before adding a third RM_ entry here.
        private static readonly string[] RmUniqueTreasureDefNames =
        {
            "RM_ElderSealedRelic",
            "RM_ElderUnknownWeapon",
        };

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
            Map map = elder.Map;
            int tile = TileForMap(map);
            RM_GameComponent_BrineElders comp = Current.Game.GetComponent<RM_GameComponent_BrineElders>();
            string key = NoveltyKey(offered);
            bool novel = tile >= 0 && comp != null && !comp.HasSeen(tile, key);

            float marketValue = offered.MarketValue * offered.stackCount;
            int silver;
            ThingDef uniqueTreasure = null;

            if (novel)
            {
                comp.MarkSeen(tile, key);
                if (Rand.Chance(UniqueTreasureChance))
                {
                    uniqueTreasure = TryClaimAnyUniqueTreasure(comp);
                }
                silver = uniqueTreasure != null
                    ? 0
                    : System.Math.Max(NovelValueFloor, UnityEngine.Mathf.RoundToInt(marketValue * NovelValueMultiplier));
            }
            else
            {
                silver = System.Math.Max(StaleValueFloor, UnityEngine.Mathf.RoundToInt(marketValue * StaleValueMultiplier));
            }

            IntVec3 deliveryCell = FindDeliveryCell(elder, out Thing jacketToDissolve);
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

        private static ThingDef TryClaimAnyUniqueTreasure(RM_GameComponent_BrineElders comp)
        {
            List<string> candidates = RmUniqueTreasureDefNames
                .Where(dn => !comp.IsUniqueTreasureGranted(dn))
                .ToList();
            if (candidates.Count == 0)
            {
                return null;
            }
            string chosen = candidates.RandomElement();
            if (!comp.TryClaimUniqueTreasure(chosen))
            {
                return null; // lost a race against itself; single-threaded in practice, guard kept anyway
            }
            return DefDatabase<ThingDef>.GetNamedSilentFail(chosen);
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
                if (nearest != null)
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
            return elder.Position;
        }
    }
}
