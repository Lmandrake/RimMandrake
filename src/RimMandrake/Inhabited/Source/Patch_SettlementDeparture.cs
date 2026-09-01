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
    /// with the base engine's recall patch -- Harmony runs every prefix bound
    /// to a method, order between them does not matter here because this
    /// patch only reads the settlement and its manifest, never the map's
    /// pawns (recall's job).
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
