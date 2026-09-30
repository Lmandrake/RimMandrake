using System.Collections.Generic;
using System.Globalization;
using System.Text;
using LudeonTK;
using RimWorld;
using Verse;

namespace RimMandrake.LuminousPigment
{
    // DEEPFIRE_STATUS_THOUGHTS_1: dev-menu tools for
    // src/RimMandrake/bridgetools/prove_deepfire_status_thoughts.py. Same
    // shape as the other Deepfire proof actions: ToolMap actions (x/z), one
    // "[DeepfireStatus] {json}" log line each. In 1.6 they show flat under
    // Actions as "T: Status: ...". Coats go through CompDeepfire.AddCoat and
    // wearing through Pawn_ApparelTracker.Wear (the real paths); titles
    // through Pawn_RoyaltyTracker.SetTitle; beds through
    // Pawn_Ownership.ClaimBedIfNonMedical. The report reads each worker's
    // state AND the live situational thought handler.
    public static class DeepfireStatusDebugActions
    {
        private const string Tag = "[DeepfireStatus] ";
        private const int TestCoats = 2;          // spec §10 row 9: "wearing 2 coats"
        private const int SculptureCoats = 3;
        private const int PawnSpacing = 2;

        private static Pawn titled;
        private static Pawn commoner;
        private static Pawn visitor;

        [DebugAction("Deepfire", "Status: spawn titled + commoner at cell", actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void SpawnPair()
        {
            Map map = Find.CurrentMap;
            IntVec3 c = UI.MouseCell();
            titled?.Destroy();
            commoner?.Destroy();
            titled = SpawnColonist(map, c);
            commoner = SpawnColonist(map, c + new IntVec3(PawnSpacing, 0, 0));
            bool titleSet = false;
            Faction empire = Faction.OfEmpire;
            if (empire != null && titled.royalty != null && RoyalTitleDefOf.Knight != null)
            {
                titled.royalty.SetTitle(empire, RoyalTitleDefOf.Knight, grantRewards: false, rewardsOnlyForNewestTitle: false, sendLetter: false);
                titleSet = true;
            }
            DropIdeoRole(commoner);
            Log.Message(Tag + "{\"action\":\"spawnPair\",\"titleSet\":" + B(titleSet)
                + ",\"titledIsTitled\":" + B(SumptuaryUtility.IsTitled(titled))
                + ",\"commonerIsTitled\":" + B(SumptuaryUtility.IsTitled(commoner)) + "}");
        }

        [DebugAction("Deepfire", "Status: dress titled in 2 coats", actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void DressTitled() => Dress(titled, "dressTitled");

        [DebugAction("Deepfire", "Status: dress commoner in 2 coats", actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void DressCommoner() => Dress(commoner, "dressCommoner");

        [DebugAction("Deepfire", "Status: report pair", actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void ReportPair()
        {
            Log.Message(Tag + BuildPairReport());
        }

        // Bed for the titled pawn on the clicked cell (inside a room the
        // script built), claimed through the real ownership path.
        [DebugAction("Deepfire", "Status: bed for titled at cell", actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void BedForTitled()
        {
            Map map = Find.CurrentMap;
            IntVec3 c = UI.MouseCell();
            if (titled == null) { Log.Message(Tag + "{\"action\":\"bed\",\"found\":false}"); return; }
            Thing bed = ThingMaker.MakeThing(ThingDefOf.Bed, ThingDefOf.WoodLog);
            bed.SetFaction(Faction.OfPlayer);
            GenSpawn.Spawn(bed, c, map, Rot4.North, WipeMode.Vanish);
            bool claimed = titled.ownership.ClaimBedIfNonMedical((Building_Bed)bed);
            Room room = bed.GetRoom();
            Log.Message(Tag + "{\"action\":\"bed\",\"found\":true,\"claimed\":" + B(claimed)
                + ",\"role\":\"" + (room?.Role?.defName ?? "") + "\""
                + ",\"ownedRoom\":" + B(titled.ownership.OwnedRoom != null) + "}");
        }

        // A small steel sculpture with SculptureCoats coats: furniture worth
        // SculptureCoats room points (spec §4.1 "Σ coats of coated furniture").
        [DebugAction("Deepfire", "Status: coated sculpture at cell", actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void CoatedSculpture()
        {
            Map map = Find.CurrentMap;
            IntVec3 c = UI.MouseCell();
            Thing s = ThingMaker.MakeThing(ThingDef.Named("SculptureSmall"), ThingDef.Named("Steel"));
            s.SetFaction(Faction.OfPlayer);
            GenSpawn.Spawn(s, c, map, WipeMode.Vanish);
            CompDeepfire comp = s.TryGetComp<CompDeepfire>();
            for (int i = 0; i < SculptureCoats && comp != null; i++) comp.AddCoat();
            MapComponent_DeepfireStatus.Get(map)?.InvalidateRoomScores();
            Room room = s.GetRoom();
            Log.Message(Tag + "{\"action\":\"sculpture\",\"coats\":" + (comp?.coats ?? -1)
                + ",\"roomScore\":" + SumptuaryUtility.RoomDisplayScore(room) + "}");
        }

        [DebugAction("Deepfire", "Status: room score at cell", actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void RoomScoreAt()
        {
            Map map = Find.CurrentMap;
            MapComponent_DeepfireStatus.Get(map)?.InvalidateRoomScores();
            Room room = UI.MouseCell().GetRoom(map);
            Log.Message(Tag + "{\"action\":\"roomScore\",\"roomId\":" + (room?.ID ?? -1)
                + ",\"score\":" + SumptuaryUtility.RoomDisplayScore(room)
                + ",\"public\":" + B(MapComponent_DeepfireStatus.IsPublicRoom(room))
                + ",\"role\":\"" + (room?.Role?.defName ?? "") + "\"}");
        }

        // A visiting titled pawn of a non-hostile, non-player humanlike
        // faction (the Empire first), then two impress checks: the first must
        // raise goodwill by GoodwillPerImpressedVisit, the second (same
        // quadrum) must not.
        [DebugAction("Deepfire", "Status: visitor impress test at cell", actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void VisitorImpress()
        {
            Map map = Find.CurrentMap;
            IntVec3 c = UI.MouseCell();
            Faction player = Faction.OfPlayer;
            Faction f = PickVisitorFaction(player);
            if (f == null) { Log.Message(Tag + "{\"action\":\"impress\",\"faction\":null}"); return; }
            visitor?.Destroy();
            visitor = PawnGenerator.GeneratePawn(f.def.basicMemberKind, f);
            GenSpawn.Spawn(visitor, c, map, WipeMode.Vanish);
            if (!SumptuaryUtility.IsTitled(visitor) && Faction.OfEmpire != null && visitor.royalty != null)
            {
                visitor.royalty.SetTitle(Faction.OfEmpire, RoyalTitleDefOf.Knight, grantRewards: false, rewardsOnlyForNewestTitle: false, sendLetter: false);
            }
            MapComponent_DeepfireStatus mc = MapComponent_DeepfireStatus.Get(map);
            mc?.InvalidateRoomScores();
            GameComponent_Deepfire.ResetImpressCap();
            int g0 = f.GoodwillWith(player);
            int n1 = mc?.TryImpressVisitors() ?? -1;
            int g1 = f.GoodwillWith(player);
            int n2 = mc?.TryImpressVisitors() ?? -1;
            int g2 = f.GoodwillWith(player);
            Log.Message(Tag + "{\"action\":\"impress\",\"faction\":\"" + f.def.defName + "\""
                + ",\"visitorImpressible\":" + B(MapComponent_DeepfireStatus.IsImpressibleVisitor(visitor, player))
                + ",\"bestPublicRoomScore\":" + (mc?.BestPublicRoomScore() ?? -1)
                + ",\"goodwill0\":" + g0 + ",\"impressed1\":" + n1 + ",\"goodwill1\":" + g1
                + ",\"impressed2\":" + n2 + ",\"goodwill2\":" + g2 + "}");
        }

        [DebugAction("Deepfire", "Status: cleanup test pawns", actionType = DebugActionType.ToolMap, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void Cleanup()
        {
            int n = 0;
            foreach (Pawn p in new[] { titled, commoner, visitor })
            {
                if (p != null && !p.Destroyed) { p.Destroy(); n++; }
            }
            titled = commoner = visitor = null;
            Log.Message(Tag + "{\"action\":\"cleanup\",\"destroyed\":" + n + "}");
        }

        // ---- helpers ----

        private static Pawn SpawnColonist(Map map, IntVec3 c)
        {
            Pawn p = PawnGenerator.GeneratePawn(PawnKindDefOf.Colonist, Faction.OfPlayer);
            GenSpawn.Spawn(p, c, map, WipeMode.Vanish);
            return p;
        }

        private static void DropIdeoRole(Pawn p)
        {
            Precept_Role role = p?.Ideo?.GetRole(p);
            role?.Unassign(p, false);
        }

        private static void Dress(Pawn p, string action)
        {
            if (p == null || p.apparel == null) { Log.Message(Tag + "{\"action\":\"" + action + "\",\"found\":false}"); return; }
            Apparel parka = (Apparel)ThingMaker.MakeThing(ThingDef.Named("Apparel_Parka"), ThingDefOf.Cloth);
            p.apparel.Wear(parka, dropReplacedApparel: false);
            CompDeepfire comp = parka.GetComp<CompDeepfire>();
            for (int i = 0; i < TestCoats && comp != null; i++) comp.AddCoat();
            Log.Message(Tag + "{\"action\":\"" + action + "\",\"found\":true,\"coats\":" + (comp?.coats ?? -1)
                + ",\"displayScore\":" + SumptuaryUtility.DisplayScoreFor(p) + "}");
        }

        private static Faction PickVisitorFaction(Faction player)
        {
            Faction empire = Faction.OfEmpire;
            if (empire != null && !empire.HostileTo(player) && !empire.defeated) return empire;
            foreach (Faction f in Find.FactionManager.AllFactionsListForReading)
            {
                if (f.IsPlayer || f.Hidden || f.defeated || f.HostileTo(player)) continue;
                if (!f.def.humanlikeFaction || f.def.basicMemberKind == null) continue;
                return f;
            }
            return null;
        }

        private static string BuildPairReport()
        {
            var sb = new StringBuilder();
            sb.Append("{\"action\":\"reportPair\"");
            if (titled == null || commoner == null) return sb.Append(",\"found\":false}").ToString();
            sb.Append(",\"found\":true");
            AppendPawn(sb, "titled", titled);
            AppendPawn(sb, "commoner", commoner);
            ThoughtDef above = DefDatabase<ThoughtDef>.GetNamed("RM_WearsAboveStation");
            ThoughtState s = above.Worker.CurrentSocialState(titled, commoner);
            sb.Append(",\"aboveStationActive\":").Append(B(s.Active));
            sb.Append(",\"titledOpinionOfCommoner\":").Append(titled.relations?.OpinionOf(commoner) ?? 0);
            sb.Append(",\"titledSocialThoughtsOfCommoner\":[");
            var social = new List<ISocialThought>();
            titled.needs?.mood?.thoughts?.situational?.AppendSocialThoughts(commoner, social);
            for (int i = 0; i < social.Count; i++)
            {
                if (i > 0) sb.Append(',');
                Thought t = (Thought)social[i];
                sb.AppendFormat(CultureInfo.InvariantCulture, "{{\"def\":\"{0}\",\"opinion\":{1:0.##}}}",
                    t.def.defName, social[i].OpinionOffset());
            }
            sb.Append("]}");
            return sb.ToString();
        }

        private static readonly string[] MoodDefs =
        {
            "RM_WearingDeepfireTitled", "RM_WearingDeepfireCommon", "RM_SawCommonerInDeepfire", "RM_DeepfireBedroom",
        };

        private static void AppendPawn(StringBuilder sb, string key, Pawn p)
        {
            CultureInfo inv = CultureInfo.InvariantCulture;
            sb.Append(",\"").Append(key).Append("\":{");
            sb.Append("\"isTitled\":").Append(B(SumptuaryUtility.IsTitled(p)));
            sb.Append(",\"displayScore\":").Append(SumptuaryUtility.DisplayScoreFor(p));
            sb.Append(",\"ownRoomScore\":").Append(ThoughtWorker_DeepfireBedroom.BestOwnRoomScore(p));
            var live = new List<Thought>();
            for (int i = 0; i < MoodDefs.Length; i++)
            {
                ThoughtDef def = DefDatabase<ThoughtDef>.GetNamed(MoodDefs[i]);
                ThoughtState st = def.Worker.CurrentState(p);
                live.Clear();
                p.needs?.mood?.thoughts?.situational?.AppendMoodThoughts(def, live);
                float mood = 0f;
                for (int j = 0; j < live.Count; j++) mood += live[j].MoodOffset();
                sb.AppendFormat(inv, ",\"{0}\":{{\"active\":{1},\"stage\":{2},\"liveMood\":{3:0.##}}}",
                    def.defName, B(st.Active), st.Active ? st.StageIndex : -1, mood);
            }
            sb.Append('}');
        }

        private static string B(bool b) => b ? "true" : "false";
    }
}
