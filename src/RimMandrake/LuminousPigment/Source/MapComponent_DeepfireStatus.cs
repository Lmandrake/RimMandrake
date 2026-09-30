using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.LuminousPigment
{
    // DEEPFIRE_STATUS_THOUGHTS_1, spec §4.1: the two room-stat reactions.
    //
    //  - Room display score cache (SumptuaryUtility.RoomDisplayScore is a
    //    walk over the room's things + a floor-grid count). RM_DeepfireBedroom
    //    re-asks on every situational recalculation, so scores are cached per
    //    Room.ID for RoomScoreCacheTicks. A MapComponent needs no XML: the
    //    engine instantiates every MapComponent subclass per map.
    //  - RM_ImpressedByDeepfire: every ImpressCheckInterval ticks, a visiting
    //    titled pawn (Royalty title / Ideology role, or its faction's leader)
    //    of a non-player, non-hostile faction on a map with any PUBLIC room
    //    scoring >= ImpressRoomScore gives the colony +GoodwillPerImpressedVisit
    //    goodwill, capped once per faction per quadrum (GameComponent_Deepfire
    //    remembers the quadrum). Reactions only: no law, no demand, no incident.
    public class MapComponent_DeepfireStatus : MapComponent
    {
        private struct CachedScore
        {
            public int Score;
            public int Tick;
        }

        private readonly Dictionary<int, CachedScore> roomScores = new Dictionary<int, CachedScore>();

        public MapComponent_DeepfireStatus(Map map) : base(map)
        {
        }

        public static MapComponent_DeepfireStatus Get(Map map) => map?.GetComponent<MapComponent_DeepfireStatus>();

        public static int CachedRoomScore(Room room)
        {
            if (room?.Map == null) return 0;
            MapComponent_DeepfireStatus mc = Get(room.Map);
            if (mc == null) return SumptuaryUtility.RoomDisplayScore(room);
            int now = Find.TickManager.TicksGame;
            if (mc.roomScores.TryGetValue(room.ID, out CachedScore c) && now - c.Tick < DeepfireStatusDefaults.RoomScoreCacheTicks)
            {
                return c.Score;
            }
            int score = SumptuaryUtility.RoomDisplayScore(room);
            mc.roomScores[room.ID] = new CachedScore { Score = score, Tick = now };
            return score;
        }

        public void InvalidateRoomScores() => roomScores.Clear();

        public override void MapComponentTick()
        {
            base.MapComponentTick();
            if (Find.TickManager.TicksGame % DeepfireStatusDefaults.ImpressCheckInterval != 0) return;
            if (roomScores.Count > 0) roomScores.Clear(); // drop dead room IDs
            TryImpressVisitors();
        }

        // Public so the dev proof can run one check on demand. Returns the
        // number of factions whose goodwill rose this call.
        public int TryImpressVisitors()
        {
            if (!LuminousPigmentSettings.statusEnabled) return 0;
            Faction player = Faction.OfPlayer;
            List<Faction> impressed = null;
            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            int bestScore = -1;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (!IsImpressibleVisitor(p, player)) continue;
                Faction f = p.Faction;
                if (impressed != null && impressed.Contains(f)) continue;
                if (!GameComponent_Deepfire.CanImpress(f)) continue;
                if (bestScore < 0) bestScore = BestPublicRoomScore();
                if (bestScore < DeepfireStatusDefaults.ImpressRoomScore) return 0;
                f.TryAffectGoodwillWith(player, DeepfireStatusDefaults.GoodwillPerImpressedVisit,
                    canSendMessage: true, canSendHostilityLetter: false, reason: DeepfireDefOf.RM_ImpressedByDeepfire);
                GameComponent_Deepfire.MarkImpressed(f);
                if (impressed == null) impressed = new List<Faction>();
                impressed.Add(f);
            }
            return impressed?.Count ?? 0;
        }

        public static bool IsImpressibleVisitor(Pawn p, Faction player)
        {
            if (p == null || !p.RaceProps.Humanlike || p.Dead || p.Downed) return false;
            Faction f = p.Faction;
            if (f == null || f == player || f.IsPlayer || f.HostileTo(player)) return false;
            if (p.IsPrisoner || p.IsSlave) return false;
            return SumptuaryUtility.IsTitled(p) || f.leader == p;
        }

        // "Public" = an enclosed, non-outdoor room that is nobody's private
        // quarters and not a prison.
        public int BestPublicRoomScore()
        {
            int best = 0;
            IReadOnlyList<Room> rooms = map.regionGrid.AllRooms;
            for (int i = 0; i < rooms.Count; i++)
            {
                Room r = rooms[i];
                if (!IsPublicRoom(r)) continue;
                int s = CachedRoomScore(r);
                if (s > best) best = s;
            }
            return best;
        }

        public static bool IsPublicRoom(Room r)
        {
            if (r == null || r.PsychologicallyOutdoors || !r.ProperRoom || r.IsPrisonCell) return false;
            RoomRoleDef role = r.Role;
            return role != RoomRoleDefOf.Bedroom && role != RoomRoleDefOf.Barracks
                && role != RoomRoleDefOf.PrisonCell && role != RoomRoleDefOf.PrisonBarracks;
        }
    }
}
