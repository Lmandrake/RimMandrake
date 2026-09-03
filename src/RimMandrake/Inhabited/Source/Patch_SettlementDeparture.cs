using HarmonyLib;
using Verse;

namespace RimMandrake.Inhabited
{
    /// <summary>
    /// Fires the gate-search hook at departure -- SETTLEMENT_VISIT_LOOP_1.
    ///
    /// Same choke point as Patch_MapRemoval's Patch_Game_DeinitAndRemoveMap,
    /// and for the same reason: the map is about to be torn down, and this is
    /// the last instant it still exists as "the settlement the player is
    /// leaving". A second [HarmonyPrefix] on the same target coexists cleanly
    /// with Patch_MapRemoval's recall -- Harmony runs every prefix bound to a
    /// method.
    ///
    /// ⚠️ THE ORDER BETWEEN THE TWO IS DECLARED, NOT LEFT TO CHANCE. Today this
    /// patch only reads the settlement and its manifest, so either order would
    /// do; the moment a gate search wants to know WHO is leaving it has to run
    /// while the cast is still standing on the map, and the recall empties the
    /// map. So this takes Priority.First and Patch_MapRemoval takes
    /// Priority.Last -- Harmony runs the higher priority first -- rather than
    /// resting on the registration order of two classes in one assembly.
    ///
    /// A Harmony patch that matches nothing throws at startup rather than
    /// silently doing nothing -- see Patch_MapRemoval's own note on why that
    /// is the desired failure mode here.
    /// </summary>
    [HarmonyPatch(typeof(Game), nameof(Game.DeinitAndRemoveMap))]
    public static class Patch_SettlementDeparture
    {
        private static readonly System.Action<Game, Map, bool> TargetSignatureProof =
            (game, map, notifyPlayer) => game.DeinitAndRemoveMap(map, notifyPlayer);

        [HarmonyPriority(Priority.First)]
        [HarmonyPrefix]
        public static void FireGateSearch(Map map)
        {
            if (map == null)
            {
                return;
            }
            WorldObject_InhabitedSettlement settlement =
                Find.WorldObjects?.WorldObjectAt<WorldObject_InhabitedSettlement>(map.Tile);
            if (settlement == null)
            {
                return;
            }
            GateSearchHook.EvaluateDeparture(settlement);
        }
    }
}
