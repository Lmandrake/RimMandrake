using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.Inhabited
{
    /// <summary>
    /// What makes an <see cref="InhabitedFate"/> fire, and what happens when it
    /// does. INHABITED_STOCK_ONTO_MAP_AND_FATE_1.
    ///
    /// ⏱️ DETECTION AND CONSEQUENCE ARE SEPARATED ON PURPOSE, and the reason is an
    /// engine fact rather than caution. The obvious build -- hand the cast a
    /// LordJob_ExitMapBest and let the player watch them walk off -- destroys the
    /// roster: Pawn.ExitMap despawns a non-player pawn with no caravan and calls
    /// Find.WorldPawns.PassToWorld, and WorldPawnGC then collects exactly the
    /// pawns WorldObject_Inhabited's class comment explains it must never let
    /// become world pawns. So the CAUSE is detected live, during the visit, by
    /// MapComponent_InhabitedWatch, which says so out loud in a message; the
    /// CONSEQUENCE lands at teardown in <see cref="Apply"/>, through the
    /// DisplacedPool the mod already uses for exactly this. The place is empty
    /// the next time the player comes, and the people turn up somewhere else --
    /// which is what "they break and go" means on a world map.
    ///
    /// Making them physically walk off is a real improvement and it is DEFERRED,
    /// not forgotten: it needs a prefix on Pawn.ExitMap that intercepts a
    /// resident before PassToWorld, and that is a new Harmony target to prove.
    /// </summary>
    public static class InhabitedFateWorker
    {
        /// <summary>Fewer than this fraction of the dropped stock still lying
        /// about reads as theft rather than a resident eating lunch.</summary>
        private const float RobbedFraction = 0.5f;

        /// <summary>
        /// Has a cause fired? Returns the translation key naming it, or null.
        /// Pure: it decides nothing and writes nothing.
        /// </summary>
        public static string DetectCause(WorldObject_Inhabited place, Map map)
        {
            if (place?.placeDef == null || map == null)
            {
                return null;
            }
            switch (place.placeDef.fate)
            {
                case InhabitedFate.Resident:
                    return null;

                // A caravan passing through is gone when the player is. Nothing
                // has to happen for this one; being visited at all is the cause.
                case InhabitedFate.Transient:
                    return "InhabitedFateTransient";

                // "A gravship coming out of the sky is enough." GravshipUtility
                // carries its own !OdysseyActive guard and returns false without
                // the DLC, so this reads as Resident on a base-game install
                // rather than throwing.
                case InhabitedFate.FleeOnArrival:
                    return GravshipUtility.PlayerHasGravEngine(map) ? "InhabitedFateGravship" : null;

                case InhabitedFate.FleeIfThreatened:
                    return Menace(place, map);
            }
            return null;
        }

        /// <summary>
        /// The four menaces, cheapest test first.
        ///
        /// ⚠️ NONE OF THESE PROVES THE PLAYER DID IT, and one of them cannot: a
        /// raider shooting up the same map harms the cast just as well. The
        /// attribution here is the player's PRESENCE (they are on this map, and
        /// this map only exists because they came), which is the same standard
        /// the settlement-proximity goodwill rules use. A cast that breaks
        /// because a mech cluster killed two of them while the player watched is
        /// not a wrong outcome.
        /// </summary>
        private static string Menace(WorldObject_Inhabited place, Map map)
        {
            CellRect area = place.StockArea;

            // Burn the granary. The literal headline case, and the only one that
            // fires WHILE it is happening rather than after.
            if (area.Area > 0)
            {
                List<Thing> fires = map.listerThings.ThingsOfDef(ThingDefOf.Fire);
                for (int i = 0; i < fires.Count; i++)
                {
                    if (fires[i] != null && area.Contains(fires[i].Position))
                    {
                        return "InhabitedFateBurned";
                    }
                }
            }

            if (place.Faction != null && place.Faction.HostileTo(Faction.OfPlayer))
            {
                return "InhabitedFateHostile";
            }

            if (map.mapPawns.FreeColonistsSpawnedCount > 0
                && place.onTheGround != null && place.onTheGround.Count > 0)
            {
                int standing = 0;
                List<Pawn> here = map.mapPawns.AllPawns;
                for (int i = 0; i < here.Count; i++)
                {
                    Pawn p = here[i];
                    if (p == null || p.Dead || !place.onTheGround.Contains(p.thingIDNumber))
                    {
                        continue;
                    }
                    if (p.Downed)
                    {
                        return "InhabitedFateHarmed";
                    }
                    standing++;
                }
                // A dead resident is a Corpse, not a Pawn, so MapPawns stops
                // counting them entirely -- the shortfall IS the casualty count.
                if (standing < place.onTheGround.Count)
                {
                    return "InhabitedFateHarmed";
                }
            }

            if (place.stockSpawnedCount > 0)
            {
                int left = InhabitedStock.CountOnMap(map, area, place.stockOnTheGround);
                if (left < place.stockSpawnedCount * RobbedFraction)
                {
                    return "InhabitedFateRobbed";
                }
            }

            return null;
        }

        /// <summary>
        /// Act on a fate that fired. Called by Patch_MapRemoval AFTER the cast
        /// has been recalled and the stock collected, so the roster it empties is
        /// complete and the state it writes is judged against real goods.
        ///
        /// ⚠️ MAY DESTROY <paramref name="place"/> (the Transient case). Nothing
        /// may touch it after this returns.
        /// </summary>
        public static void Apply(WorldObject_Inhabited place)
        {
            if (place?.placeDef == null || !place.threatened
                || place.placeDef.fate == InhabitedFate.Resident)
            {
                return;
            }

            // A caravan passing through has no place to leave behind. Destroy()
            // already absorbs the roster into the pool with DisplacedReason.Fled,
            // so this is the whole of Transient.
            if (place.placeDef.fate == InhabitedFate.Transient)
            {
                Log.Message("[RimMandrake.Inhabited] " + place.LabelCap
                            + " was transient and is gone; " + place.SoulCount + " become placeless.");
                place.Destroy();
                return;
            }

            int fled = 0;
            DisplacedPool pool = DisplacedPool.Current;
            if (pool != null && place.roster != null && place.roster.Count > 0)
            {
                List<Pawn> left = new List<Pawn>(place.roster.InnerListForReading);
                for (int i = 0; i < left.Count; i++)
                {
                    Pawn p = left[i];
                    if (p == null || p.Dead || !place.roster.Remove(p))
                    {
                        continue;
                    }
                    if (pool.Absorb(p, place.Faction, DisplacedReason.Fled, place.LabelCap))
                    {
                        fled++;
                    }
                    else if (!place.roster.TryAdd(p, canMergeWithExistingStacks: false))
                    {
                        // The pool refused and the roster will not take them back:
                        // destroying them here would be a silent death, which is
                        // the one outcome this mod's roster rule cannot survive.
                        Log.Error("[RimMandrake.Inhabited] " + p.LabelShort + " left "
                                  + place.LabelCap + " and has nowhere to be; they are lost.");
                    }
                }
            }

            // An emptied larder is a LOOTING; a full one left behind is an
            // ABANDONMENT, and GetInspectString already draws both differently
            // ("looted" vs "N souls fled . stock spoiling").
            place.state = (place.stock == null || place.stock.Count == 0)
                ? InhabitedState.Looted
                : InhabitedState.Abandoned;

            Log.Message("[RimMandrake.Inhabited] fate " + place.placeDef.fate + " fired at "
                        + place.LabelCap + " (" + (place.threatReason ?? "-") + "): "
                        + fled + " placeless, state now " + place.state + ".");
        }
    }
}
