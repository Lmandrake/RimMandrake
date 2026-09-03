using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using Verse;
using Verse.AI.Group;

namespace RimMandrake.Inhabited
{
    /// <summary>
    /// The survivors go back into the world. The dead do not.
    ///
    /// WHY A PATCH AND NOT A HOOK. MapParent has Notify_MyMapAboutToBeRemoved,
    /// which is exactly the right moment -- but a WorldObject_Inhabited is a plain
    /// WorldObject by design, and the map a player lands on belongs to whatever
    /// else owns that tile. So we take the moment itself.
    ///
    /// WHY THIS EXACT MOMENT AND NOT ONE STEP LATER. Game.DeinitAndRemoveMap runs:
    ///
    ///     map.Parent.Notify_MyMapAboutToBeRemoved()
    ///     MapDeiniter.Deinit(map, notifyPlayer)      &lt;- FIRST ACT: PassPawnsToWorld
    ///     maps.Remove(map) ... map.Dispose()
    ///
    /// and PassPawnsToWorld despawns every pawn on the map and hands it to
    /// WorldPawns. After that the cast is no longer enumerable as "the people
    /// standing at this place", and WorldPawnGC is free to collect them. A prefix
    /// on DeinitAndRemoveMap is the last instant at which they are all still
    /// spawned, alive and identifiable by their Lord.
    ///
    /// A Harmony patch that matches nothing throws at startup, unlike an XML one.
    /// That is the desired behaviour here: if this target is ever renamed, the
    /// mod must fail loudly rather than quietly forget everybody.
    /// </summary>
    [HarmonyPatch(typeof(Game), nameof(Game.DeinitAndRemoveMap))]
    public static class Patch_Game_DeinitAndRemoveMap
    {
        /// <summary>
        /// Compile-time proof that `Game.DeinitAndRemoveMap(Map, bool)` still has
        /// exactly this signature. See Patch_BeggarsFromPool for why: a Harmony
        /// target that has moved costs a cold load to discover, and the compiler
        /// can be made to answer it for free.
        /// </summary>
        private static readonly System.Action<Game, Map, bool> TargetSignatureProof =
            (game, map, notifyPlayer) => game.DeinitAndRemoveMap(map, notifyPlayer);

        /// <summary>
        /// ⚠️ RUNS LAST among this mod's prefixes on this target, deliberately --
        /// see Patch_SettlementDeparture, which must still be able to see the cast
        /// standing on the map when it fires. Harmony runs the higher priority
        /// first, so the recall that empties the map takes Priority.Last.
        /// </summary>
        [HarmonyPriority(Priority.Last)]
        [HarmonyPrefix]
        public static void RecallInhabitants(Map map)
        {
            if (map == null)
            {
                return;
            }
            WorldObject_Inhabited place = Find.WorldObjects?.WorldObjectAt<WorldObject_Inhabited>(map.Tile);
            if (place == null || place.roster == null)
            {
                return;
            }

            // Fixed 2026-09-02 (opus code review): AllPawns, not AllPawnsSpawned,
            // and matched by identity rather than by lord. Two engine facts, both
            // read out of the 1.6 source rather than assumed:
            //
            //   * LordJob.ShouldRemovePawn returns TRUE by default and
            //     LordJob_Inhabited does not override it, so Lord.Notify_PawnLost
            //     drops any resident who is merely DOWNED. Keying the recall on
            //     "still under a LordJob_Inhabited lord" therefore abandoned every
            //     casualty of an ordinary firefight.
            //   * MapPawns.AllPawnsSpawned excludes a downed pawn being CARRIED --
            //     they live in the carrier's ThingOwner, and MapDeiniter's own
            //     PassPawnsToWorld walks AllPawns for exactly that reason.
            //
            // Either way the pawn fell through to PassPawnsToWorld, became an
            // ordinary world pawn and was collected by WorldPawnGC: off the roster
            // with no log line, and indistinguishable from having died.
            List<Pawn> ours = map.mapPawns.AllPawns
                .Where(p => p != null && !p.Dead && BelongsHere(place, p))
                .ToList();

            DisplacedPool pool = DisplacedPool.Current;
            for (int i = 0; i < ours.Count; i++)
            {
                Pawn p = ours[i];
                p.DeSpawnOrDeselect();

                // TryAddOrTransfer, not TryAdd: a carried resident is still held by
                // the carrier, and ThingOwner.TryAdd refuses anything that already
                // has a holdingOwner.
                if (place.roster.TryAddOrTransfer(p, canMergeWithExistingStacks: false))
                {
                    continue;
                }
                if (pool != null && pool.Absorb(p, place.Faction, DisplacedReason.Fled, place.LabelCap))
                {
                    Log.Warning("[RimMandrake.Inhabited] " + p.LabelShort + " would not go back on the roster of "
                                + place.LabelCap + "; they are placeless instead.");
                    continue;
                }
                Log.Warning("[RimMandrake.Inhabited] could not return " + p.LabelShort + " to the roster of "
                            + place.LabelCap + "; they are left to the world.");
            }
            place.onTheGround.Clear();

            // INHABITED_STOCK_ONTO_MAP_AND_FATE_1. The goods come back the same
            // way the people do, at the same instant and for the same reason: a
            // Thing still spawned here is enumerable, and one step later
            // MapDeiniter has begun and the map is being disposed with everything
            // on it. What the player ate, burned or carried off is simply not
            // there to collect, so no loss is recorded anywhere -- the holder's
            // contents afterwards ARE the place's remaining goods.
            if (place.stock != null)
            {
                int back = place.stock.CollectFrom(map, place.StockArea, place.stockOnTheGround);
                if (place.stockSpawnedCount > 0 || back > 0)
                {
                    Log.Message("[RimMandrake.Inhabited] took back " + back + " of "
                                + place.stockSpawnedCount + " goods from " + place.LabelCap + ".");
                }
            }
            place.stockSpawnedCount = 0;
            place.stockSpot = IntVec3.Invalid;

            // No death record, no memorial, no ledger, no counter. The roster IS
            // the survivors and the absence is the memory.
            if (place.SoulCount == 0 && place.state == InhabitedState.Inhabited)
            {
                place.state = InhabitedState.Abandoned;
            }

            // ⚠️ LAST, AND NOTHING MAY FOLLOW IT. A fired Transient fate destroys
            // the world object. Everything above has to have finished first: the
            // fate empties the roster this method has just refilled, and judges
            // Looted-vs-Abandoned on the stock it has just collected.
            InhabitedFateWorker.Apply(place);
        }

        /// <summary>
        /// Is this one of the people the place put on the ground, and is he still
        /// the place's to take back?
        /// </summary>
        private static bool BelongsHere(WorldObject_Inhabited place, Pawn p)
        {
            // Recruited, or arrested and held prisoner. They left the roster by an
            // event the player watched happen; taking them back at the door would
            // be theft, and PassPawnsToWorld already carves out exactly this pair.
            if (p.Faction == Faction.OfPlayer || p.HostFaction == Faction.OfPlayer)
            {
                return false;
            }
            if (place.onTheGround != null && place.onTheGround.Contains(p.thingIDNumber))
            {
                return true;
            }

            // A save written before the ledger existed carries an empty list, and
            // the lord is what the recall used to key on.
            Lord lord = p.GetLord();
            return lord != null && lord.LordJob is LordJob_Inhabited;
        }
    }
}
