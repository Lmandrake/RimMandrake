// BESKAR_ARMORER_QUEST_1: what outlives the world object (reveal, lost), the harm rule (spec 2.3) and heat (spec 6).
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using RimWorld.QuestGen;
using Verse;
using Verse.AI.Group;

namespace RimMandrake.Utinni.BeskarArmorer
{
    public class HeatEvent : IExposable
    {
        public int tick;
        public string faction;
        public int amount;
        public string source;

        public void ExposeData()
        {
            Scribe_Values.Look(ref tick, "tick");
            Scribe_Values.Look(ref faction, "faction");
            Scribe_Values.Look(ref amount, "amount");
            Scribe_Values.Look(ref source, "source");
        }
    }

    /// <summary>Spec 6: heat is recorded, not modelled. jawa/heat_events reads Events; the blackboard takes it as one more input.</summary>
    public class RM_HeatEvents : GameComponent
    {
        public const int Large = 30;        // spec 6: on the blackboard's scale, where HEAT_HIGH_BAND is 40
        public const int Max = 100;

        public List<HeatEvent> events = new List<HeatEvent>();

        public RM_HeatEvents(Game game) { }

        public static void Record(Faction f, int amount, string source)
        {
            RM_HeatEvents c = Current.Game.GetComponent<RM_HeatEvents>();
            c?.events.Add(new HeatEvent { tick = Find.TickManager.TicksGame, faction = f?.def.defName ?? "none", amount = amount, source = source });
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref events, "events", LookMode.Deep);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && events == null) events = new List<HeatEvent>();
        }
    }

    public class RM_ArmorerState : GameComponent
    {
        public bool revealed;
        public bool lost;

        public RM_ArmorerState(Game game) { }

        public static RM_ArmorerState Get { get { return Current.Game.GetComponent<RM_ArmorerState>(); } }

        public static RM_ArmorerCovert Covert { get { return Find.WorldObjects?.AllWorldObjects.OfType<RM_ArmorerCovert>().FirstOrDefault(); } }

        public static bool RouteQuestRunning
        {
            get
            {
                return Find.QuestManager.QuestsListForReading.Any(q => !q.Historical
                    && (q.root == ArmorerDefOf.RM_Quest_ArmorerDebt || q.root == ArmorerDefOf.RM_Quest_ImperialPrisonBreak));
            }
        }

        private static bool IsBlackstarMandalorian(Pawn p)
        {
            string k = p.kindDef?.defName;
            return k == "RUT_Jawa_Blackstar_Heavy" || k == "RUT_Jawa_Blackstar_Leader";
        }

        public void TryStartRouteOne(Pawn p, bool wasPlayerPrisoner)
        {
            if (!ArmorerKernel.RouteOneFires(BeskarArmorerSettings.routeOneEnabled, IsBlackstarMandalorian(p), !p.Dead, wasPlayerPrisoner, revealed, lost, RouteQuestRunning)) return;
            Slate slate = new Slate();
            slate.Set("hunter", p);
            slate.Set("revealTicks", Rand.RangeInclusive(BeskarArmorerSettings.revealDelayMinDays, System.Math.Max(BeskarArmorerSettings.revealDelayMinDays, BeskarArmorerSettings.revealDelayMaxDays)) * GenDate.TicksPerDay);
            Quest q = QuestUtility.GenerateQuestAndMakeAvailable(ArmorerDefOf.RM_Quest_ArmorerDebt, slate);
            QuestUtility.SendLetterQuestAvailable(q);
        }

        /// <summary>Spec 3.3, shared by both routes. Null with reason on refusal.</summary>
        public RM_ArmorerCovert Reveal(out string refused)
        {
            refused = null;
            if (lost || Covert != null) { refused = lost ? "covert lost" : "covert already revealed"; return null; }
            if (!TryFindCovertTile(out PlanetTile tile)) { refused = "no orbit tile"; return null; }
            RM_ArmorerCovert covert = (RM_ArmorerCovert)WorldObjectMaker.MakeWorldObject(ArmorerDefOf.RM_ArmorerCovert);
            covert.Tile = tile;
            covert.revealedTick = Find.TickManager.TicksGame;
            ArmorerCast.Populate(covert);
            Find.WorldObjects.Add(covert);
            revealed = true;
            return covert;
        }

        private static bool TryFindCovertTile(out PlanetTile tile)
        {
            tile = PlanetTile.Invalid;
            if (!TileFinder.TryFindRandomPlayerTile(out PlanetTile home, allowCaravans: false, null, canBeSpace: true)) return false;
            if (!Find.WorldGrid.TryGetFirstAdjacentLayerOfDef(home, PlanetLayerDefOf.Orbit, out PlanetLayer orbit)) return false;
            var query = new FastTileFinder.TileQueryParams(home, 20f, 60f);
            var desperate = new FastTileFinder.TileQueryParams(home, 1f, 120f, checkBiome: false);
            List<PlanetTile> found = orbit.FastTileFinder.Query(query, null, null, desperate);
            if (found.NullOrEmpty()) return false;
            tile = found.RandomElement();
            return true;
        }

        /// <summary>Spec 2.3. Idempotent: the first harm decides everything.</summary>
        public static void Harm(string what)
        {
            RM_ArmorerState s = Get;
            RM_ArmorerCovert covert = Covert;
            if (s == null || covert == null || covert.lost) return;
            s.lost = true;
            covert.lost = true;
            Faction tribe = covert.Faction;
            if (tribe != null) tribe.SetRelationDirect(Faction.OfPlayer, FactionRelationKind.Hostile, false);
            Faction pirate = Find.FactionManager.OfPirates ?? Find.FactionManager.FirstFactionOfDef(FactionDefOf.Pirate);
            RM_HeatEvents.Record(pirate, RM_HeatEvents.Max, "armorer harmed: " + what);
            if (!covert.HasMap) covert.Destroy();
            Map home = Find.AnyPlayerHomeMap;
            if (BeskarArmorerSettings.harmRaidEnabled && pirate != null && home != null) ArmorerRaids.Fire(home, pirate, 2f, true);
            Find.LetterStack.ReceiveLetter("The Creed's verdict",
                "You raised your hand against the Armorer's covert. Its coordinates are dead to you and will never be given again. "
                + "The covert is gone the moment you leave it, and Blackstar is coming for you now: heat with them is at its limit.",
                LetterDefOf.ThreatBig, home != null ? (LookTargets)new TargetInfo(home.Center, home) : LookTargets.Invalid);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref revealed, "revealed");
            Scribe_Values.Look(ref lost, "lost");
        }
    }

    public static class ArmorerRaids
    {
        /// <summary>One vanilla RaidEnemy at factor times the default points. A faction not yet hostile is pushed there: a raid from a
        /// friend does not fire, and route 2's pursuit is the point of the heat.</summary>
        public static bool Fire(Map map, Faction f, float factor, bool addMandalorians)
        {
            if (!f.HostileTo(Faction.OfPlayer)) f.TryAffectGoodwillWith(Faction.OfPlayer, -200, canSendMessage: false, canSendHostilityLetter: false);
            IncidentParms parms = StorytellerUtility.DefaultParmsNow(IncidentCategoryDefOf.ThreatBig, map);
            parms.faction = f;
            parms.points = StorytellerUtility.DefaultThreatPointsNow(map) * factor;
            parms.forced = true;
            HashSet<Lord> before = new HashSet<Lord>(map.lordManager.lords);
            bool ok = IncidentDefOf.RaidEnemy.Worker.TryExecute(parms);
            if (ok && addMandalorians) AddMandalorians(map, f, before);
            return ok;
        }

        // "Mandalorians preferred" (spec 2.3): IncidentParms cannot name a pawn kind, so two walk in with the raid's own lord.
        private static void AddMandalorians(Map map, Faction f, HashSet<Lord> before)
        {
            PawnKindDef heavy = DefDatabase<PawnKindDef>.GetNamedSilentFail("RUT_Jawa_Blackstar_Heavy");
            Lord lord = map.lordManager.lords.FirstOrDefault(l => !before.Contains(l) && l.faction == f);
            Pawn leader = lord?.ownedPawns.FirstOrDefault(p => p.Spawned);
            if (heavy == null || leader == null) return;
            for (int i = 0; i < 2; i++)
            {
                Pawn p = PawnGenerator.GeneratePawn(heavy, f);
                GenSpawn.Spawn(p, CellFinder.StandableCellNear(leader.Position, map, 8f), map);
                lord.AddPawn(p);
            }
        }
    }
}
