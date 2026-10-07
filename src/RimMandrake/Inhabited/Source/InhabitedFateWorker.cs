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
        /// about reads as theft rather than a resident eating lunch.
        /// MOD_OPTIONS_RETROFIT_1: player-tunable via RM_InhabitedSettings,
        /// default matches the original shipped const (0.5).</summary>
        private static float RobbedFraction => RM_InhabitedSettings.robbedFraction;

        /// <summary>
        /// Has a cause fired? Returns the translation key naming it, or null.
        /// Pure: it decides nothing and writes nothing.
        /// </summary>
        public static string DetectCause(WorldObject_Inhabited place, Map map)
        {
            // Master fate-detection toggle is gated at the caller
            // (MapComponent_InhabitedWatch), which is the only caller.
            if (place?.placeDef == null || map == null)
            {
                return null;
            }
            CellRect area = place.StockArea;
            return InhabitedFateKernel.Cause(
                place.placeDef.fate,
                // "A gravship coming out of the sky is enough." GravshipUtility
                // carries its own !OdysseyActive guard and returns false without
                // the DLC, so this reads as Resident on a base-game install
                // rather than throwing.
                () => GravshipUtility.PlayerHasGravEngine(map),
                area.Area > 0,
                () => FireInside(map, area),
                place.Faction != null && place.Faction.HostileTo(Faction.OfPlayer),
                map.mapPawns.FreeColonistsSpawnedCount > 0,
                place.onTheGround != null ? place.onTheGround.Count : 0,
                () => CountCast(place, map),
                place.stockSpawnedCount,
                () => InhabitedStock.CountOnMap(map, area, place.stockOnTheGround),
                RobbedFraction);
        }

        // ⚠️ NONE OF THE MENACES PROVES THE PLAYER DID IT, and one of them cannot: a
        // raider shooting up the same map harms the cast just as well. The
        // attribution is the player's PRESENCE (they are on this map, and
        // this map only exists because they came), which is the same standard
        // the settlement-proximity goodwill rules use. The decision order lives in
        // InhabitedFateKernel.Cause.

        private static bool FireInside(Map map, CellRect area)
        {
            List<Thing> fires = map.listerThings.ThingsOfDef(ThingDefOf.Fire);
            for (int i = 0; i < fires.Count; i++)
            {
                if (fires[i] != null && area.Contains(fires[i].Position))
                {
                    return true;
                }
            }
            return false;
        }

        private static CastCount CountCast(WorldObject_Inhabited place, Map map)
        {
            CastCount c = new CastCount();
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
                    c.anyDowned = true;
                    return c;
                }
                c.standing++;
            }
            return c;
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
            if (place?.placeDef == null
                || !InhabitedFateKernel.ShouldApply(place.placeDef.fate, place.threatened))
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
                fled = InhabitedCustody.MoveRosterToPool(
                    new List<Pawn>(place.roster.InnerListForReading), p => p.Dead,
                    p => place.roster.Remove(p),
                    p => pool.Absorb(p, place.Faction, DisplacedReason.Fled, place.LabelCap),
                    p => place.roster.TryAdd(p, canMergeWithExistingStacks: false),
                    p =>
                    {
                        // The pool refused and the roster will not take them back:
                        // destroying them here would be a silent death, which is
                        // the one outcome this mod's roster rule cannot survive.
                        Log.Error("[RimMandrake.Inhabited] " + p.LabelShort + " left "
                                  + place.LabelCap + " and has nowhere to be; they are lost.");
                    });
            }

            // An emptied larder is a LOOTING; a full one left behind is an
            // ABANDONMENT, and GetInspectString already draws both differently
            // ("looted" vs "N souls fled . stock spoiling").
            place.state = InhabitedFateKernel.StateAfterFate(place.stock == null ? 0 : place.stock.Count);

            Log.Message("[RimMandrake.Inhabited] fate " + place.placeDef.fate + " fired at "
                        + place.LabelCap + " (" + (place.threatReason ?? "-") + "): "
                        + fled + " placeless, state now " + place.state + ".");
        }
    }
}
