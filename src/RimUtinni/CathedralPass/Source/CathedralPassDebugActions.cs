using LudeonTK;
using RimWorld;
using Verse;

namespace RimMandrake.Utinni.CathedralPass
{
    // Dev-mode stand-ins for the GM verbs until CATHEDRAL_REGARD_BLACKBOARD_1 exists.
    // They call exactly the API the verbs will call, so a quicktest exercises the real path.
    public static class CathedralPassDebugActions
    {
        [DebugAction("Cathedral pass", "Grant pass (pawn)", actionType = DebugActionType.ToolMapForPawns, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void GrantPawn(Pawn p)
        {
            Messages.Message("Cathedral pass " + (CathedralPass.Grant(p) ? "granted to " : "not granted (not clan, or held) to ") + p.LabelShort,
                MessageTypeDefOf.NeutralEvent, false);
        }

        [DebugAction("Cathedral pass", "Revoke pass (pawn)", actionType = DebugActionType.ToolMapForPawns, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void RevokePawn(Pawn p)
        {
            Messages.Message("Cathedral pass " + (CathedralPass.Revoke(p) ? "revoked from " : "not held by ") + p.LabelShort,
                MessageTypeDefOf.NeutralEvent, false);
        }

        [DebugAction("Cathedral pass", "Grant pass to clan", allowedGameStates = AllowedGameStates.Playing)]
        private static void GrantClan()
        {
            Messages.Message("Cathedral pass granted to " + CathedralPass.GrantToClan() + " clan pawns.", MessageTypeDefOf.NeutralEvent, false);
        }

        [DebugAction("Cathedral pass", "Revoke pass from all", allowedGameStates = AllowedGameStates.Playing)]
        private static void RevokeAll()
        {
            Messages.Message("Cathedral pass revoked from " + CathedralPass.RevokeFromAll() + " pawns.", MessageTypeDefOf.NeutralEvent, false);
        }

        [DebugAction("Cathedral pass", "Is this a Cathedral map?", allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void ReportMap()
        {
            Map map = Find.CurrentMap;
            Messages.Message("Cathedral map: " + CathedralPass.IsCathedralMap(map) + " (biome " + map?.Biome?.defName + ")",
                MessageTypeDefOf.NeutralEvent, false);
        }
    }
}
