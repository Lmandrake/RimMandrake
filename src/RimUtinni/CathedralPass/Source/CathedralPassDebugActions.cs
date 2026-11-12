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

        // CATHEDRAL_DESCENT_REVEAL_SITE_1: fire the opening exactly as the blackboard does (the worker's own refusal
        // applies, so a second attempt is refused and says why), and read the once-only state back.
        [DebugAction("Cathedral pass", "Descent: try to open the way down", allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void DescentOpen()
        {
            IncidentDef def = DefDatabase<IncidentDef>.GetNamedSilentFail(CathedralDescentDefNames.Opening);
            string why = CathedralDescent.OpeningRefusal();
            if (def == null || why != null)
            {
                GameComponent_CathedralDescent st = GameComponent_CathedralDescent.Get();
                if (st != null && def != null) st.refusedOpenings++;
                Messages.Message("Descent opening refused: " + (def == null ? CathedralDescentDefNames.Opening + " not loaded" : why),
                    MessageTypeDefOf.RejectInput, false);
                return;
            }
            IncidentParms parms = StorytellerUtility.DefaultParmsNow(def.category, Find.AnyPlayerHomeMap);
            bool ok = def.Worker.TryExecute(parms);
            Messages.Message("Descent opening " + (ok ? "fired." : "failed (see log)."), MessageTypeDefOf.NeutralEvent, false);
        }

        [DebugAction("Cathedral pass", "Descent: report state", allowedGameStates = AllowedGameStates.Playing)]
        private static void DescentState()
        {
            GameComponent_CathedralDescent st = GameComponent_CathedralDescent.Get();
            Map map = Find.CurrentMap;
            string msg = st == null ? "no state" : "opened " + st.opened + " (tick " + st.openedTick + "), revealed " + st.revealed
                + " (tick " + st.revealedTick + "), refused openings " + st.refusedOpenings
                + "; this map is the descent: " + CathedralDescent.IsDescentMap(map);
            Log.Message(CathedralDescentDefNames.LogTag + " state: " + msg);
            Messages.Message("Descent: " + msg, MessageTypeDefOf.NeutralEvent, false);
        }
    }
}
