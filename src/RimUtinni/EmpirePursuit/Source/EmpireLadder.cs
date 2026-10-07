/* EMPIRE_ESCALATION_LADDER_1 — the Imperial search ladder's runtime.
 * Design: design/Jawa/proposals/empire_escalation_ladder_design_2026-10-02.md.
 * Owner card rulings 2026-10-03: moving = full reset to rung 1 with a permanent leak floor;
 * the ship is touched only to STALL it (ion cordon disables the engine for hours, never closes
 * escape); orbital bombardment destroys buildings, with a full day's warning and a marked area.
 *
 * Shape: the pursuit ScenPart keeps its timers; when the ladder is on, its raid tick calls
 * MapComponent_EmpireSearch.FireNextRung instead of FireRaid_NewTemp. The map component runs
 * the contact (probe / spotter / strike / cordon / breach / bombardment), judges whether the
 * Empire succeeded, climbs or holds, and asks the ScenPart to schedule the next rung.
 *
 * Visibility (mandrake.rm.visibility) and Aftermath (mandrake.rm.aftermath) are SOFT: bound by
 * reflection, so this mod gains no dependency. Visibility's own TryExecute prefix already scales
 * every RaidEnemy's points by its curve, so ladder raids get the curve without code here.
 * All numbers PROVISIONAL. */
using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;
using Verse.AI.Group;

namespace RuthlessPursuingMechanoids
{
    /// <summary>Public API other mods call by reflection (design §4/§5, P7).</summary>
    public static class EmpireSearch
    {
        /// <summary>True while the ladder (or the pursuit's own waves) is executing a raid,
        /// so the storyteller-spacing patch can tell its own raids from the storyteller's.</summary>
        public static bool FiringLadder;

        public const int StorytellerSpacingTicks = EmpireLadderState.StorytellerSpacingTicks;   // 2 * GenDate.TicksPerDay

        public static ScenPart_RuthlessPursuingMechanoids Part =>
            Find.Scenario?.AllParts.OfType<ScenPart_RuthlessPursuingMechanoids>()
                .FirstOrDefault(p => p.PursuitFaction != null);

        public static bool LadderOn => RFPSettings.ladderEnabled;

        public static bool IsLadderFaction(Faction f) => f != null && LadderOn && Part?.PursuitFaction == f;

        /// <summary>A Route 6 leak or the droid line's discovery: a permanent rung floor
        /// ("prevent, never undo"). Raises every live map's next rung to at least the floor.</summary>
        public static void RaiseFloor(int floor, string reason)
        {
            GameComponent_EmpireSearch g = GameComponent_EmpireSearch.Get();
            if (g == null) return;
            int before = g.rungFloor;
            g.rungFloor = EmpireLadderState.RaisedFloor(g.rungFloor, floor);
            foreach (Map m in Find.Maps)
            {
                MapComponent_EmpireSearch.For(m)?.st.ApplyFloor(g.rungFloor);
            }
            Log.Message($"[EmpireSearch] rung floor {before} -> {g.rungFloor}: {reason}");
        }

        /// <summary>Ishko's Unseen Berth and anything like it: drop this map's next rung.</summary>
        public static void LowerRung(Map map, int by, string reason)
        {
            MapComponent_EmpireSearch c = MapComponent_EmpireSearch.For(map);
            if (c == null || c.nextRung < 0) return;
            int floor = GameComponent_EmpireSearch.Get()?.rungFloor ?? 0;
            int before = c.nextRung;
            c.st.LowerRung(by, floor, out bool revived);
            // A terminal ladder has no timer running (Resolve schedules only while not terminal): without this it never fires again.
            if (revived && !c.ContactLive) Part?.ScheduleLadder(map);
            Log.Message($"[EmpireSearch] {map} rung {before} -> {c.nextRung}: {reason}");
        }

        // ---- Visibility, soft -------------------------------------------------------------
        private static Type visType;
        private static bool visLooked;

        private static GameComponent VisibilityComponent()
        {
            if (!visLooked)
            {
                visLooked = true;
                visType = AccessTools.TypeByName("RimMandrake.Visibility.GameComponent_ColonyVisibility");
            }
            if (visType == null || Current.Game == null) return null;
            return Current.Game.components.FirstOrDefault(c => c.GetType() == visType);
        }

        /// <summary>The ship's Visibility (0-100), or -1 when the Visibility mod is absent.</summary>
        public static float Visibility()
        {
            GameComponent c = VisibilityComponent();
            if (c == null) return -1f;
            object v = AccessTools.Field(visType, "shipVisibility")?.GetValue(c);
            return v is float f ? f : -1f;
        }

        public static void AdjustVisibility(float delta, string reason)
        {
            GameComponent c = VisibilityComponent();
            if (c == null) return;
            AccessTools.Method(visType, "Adjust")?.Invoke(c, new object[] { delta, "[Imperial] " + reason });
        }

        public static string BandLabel(float v)
        {
            if (v < 0f) return null;
            if (v < 20f) return "Hidden";
            if (v < 40f) return "Discreet";
            if (v < 60f) return "Noticed";
            if (v < 80f) return "Marked";
            return "Exposed";
        }
    }

    /// <summary>Game-wide ladder state: the permanent leak floor and the tiles that remember.</summary>
    public class GameComponent_EmpireSearch : GameComponent
    {
        public int rungFloor;
        public Dictionary<PlanetTile, RungMemory> tileRungs = new Dictionary<PlanetTile, RungMemory>();

        public GameComponent_EmpireSearch(Game game) { }

        public static GameComponent_EmpireSearch Get() => Current.Game?.GetComponent<GameComponent_EmpireSearch>();

        public override void ExposeData()
        {
            Scribe_Values.Look(ref rungFloor, "rungFloor", 0);
            Scribe_Collections.Look(ref tileRungs, "tileRungs", LookMode.Value, LookMode.Deep);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && tileRungs == null)
                tileRungs = new Dictionary<PlanetTile, RungMemory>();
        }

        public void RecordDeparture(PlanetTile tile, int rung)
        {
            if (!EmpireLadderState.ShouldRecordDeparture(tile.Valid, rung)) return;
            tileRungs[tile] = new RungMemory { rung = rung, departedTick = Find.TickManager.TicksGame };
        }

        /// <summary>The decayed remembered rung for a tile, or -1.</summary>
        public int Remembered(PlanetTile tile)
        {
            RungMemory m = null;
            bool has = tile.Valid && tileRungs.TryGetValue(tile, out m);
            return EmpireLadderState.RememberedRung(RFPSettings.rememberRungs, tile.Valid, has, has ? m.rung : 0, has ? m.departedTick : 0,
                Find.TickManager.TicksGame, GenDate.TicksPerSeason, RFPSettings.rungDecayPerSeason);
        }
    }

    public class RungMemory : IExposable
    {
        public int rung;
        public int departedTick;

        public void ExposeData()
        {
            Scribe_Values.Look(ref rung, "rung");
            Scribe_Values.Look(ref departedTick, "departedTick");
        }
    }

    /// <summary>Per-map ladder state and the one live contact.</summary>
    public class MapComponent_EmpireSearch : MapComponent
    {
        // The scalar ladder state and its transitions live in the Verse-free kernel (fuzzed offline).
        public readonly EmpireLadderState st = new EmpireLadderState();
        public int nextRung { get { return st.nextRung; } set { st.nextRung = value; } }   // -1 = not initialised on this map
        public bool terminal { get { return st.terminal; } set { st.terminal = value; } }   // top rung reached: endless waves may run
        public bool lastProbeBlind { get { return st.lastProbeBlind; } set { st.lastProbeBlind = value; } }
        public int lastLadderFireTick { get { return st.lastLadderFireTick; } set { st.lastLadderFireTick = value; } }
        public int lastStorytellerRaidTick { get { return st.lastStorytellerRaidTick; } set { st.lastStorytellerRaidTick = value; } }

        // the live contact
        public RUT_EmpireRungDef activeRung;
        public int contactStartTick { get { return st.contactStartTick; } set { st.contactStartTick = value; } }
        public List<Pawn> contactPawns = new List<Pawn>();
        public Pawn spotter;
        public int progressTicks { get { return st.progressTicks; } set { st.progressTicks = value; } }
        public bool anyProbeDestroyed { get { return st.anyProbeDestroyed; } set { st.anyProbeDestroyed = value; } }
        public int nextIonTick { get { return st.nextIonTick; } set { st.nextIonTick = value; } }
        public int bombardTick { get { return st.bombardTick; } set { st.bombardTick = value; } }
        public IntVec3 bombardCenter = IntVec3.Invalid;
        public string aftermathOutcome { get { return st.aftermathOutcome; } set { st.aftermathOutcome = value; } }

        private const int CheckInterval = EmpireLadderState.CheckInterval;
        public const float BombardRadius = 15f;

        public MapComponent_EmpireSearch(Map map) : base(map) { }

        public static MapComponent_EmpireSearch For(Map map) => map?.GetComponent<MapComponent_EmpireSearch>();

        public bool ContactLive => activeRung != null;

        public override void ExposeData()
        {
            Scribe_Values.Look(ref st.nextRung, "nextRung", -1);
            Scribe_Values.Look(ref st.terminal, "terminal", false);
            Scribe_Values.Look(ref st.lastProbeBlind, "lastProbeBlind", false);
            Scribe_Values.Look(ref st.lastLadderFireTick, "lastLadderFireTick", -9999999);
            Scribe_Values.Look(ref st.lastStorytellerRaidTick, "lastStorytellerRaidTick", -9999999);
            Scribe_Defs.Look(ref activeRung, "activeRung");
            Scribe_Values.Look(ref st.contactStartTick, "contactStartTick", -1);
            Scribe_Collections.Look(ref contactPawns, "contactPawns", LookMode.Reference);
            Scribe_References.Look(ref spotter, "spotter");
            Scribe_Values.Look(ref st.progressTicks, "progressTicks", 0);
            Scribe_Values.Look(ref st.anyProbeDestroyed, "anyProbeDestroyed", false);
            Scribe_Values.Look(ref st.nextIonTick, "nextIonTick", -1);
            Scribe_Values.Look(ref st.bombardTick, "bombardTick", -1);
            Scribe_Values.Look(ref bombardCenter, "bombardCenter", IntVec3.Invalid);
            Scribe_Values.Look(ref st.aftermathOutcome, "aftermathOutcome");
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                if (contactPawns == null) contactPawns = new List<Pawn>();
                contactPawns.RemoveAll(p => p == null);
            }
        }

        // ---- initialisation ---------------------------------------------------------------

        public void EnsureInit()
        {
            if (nextRung >= 0) return;
            GameComponent_EmpireSearch g = GameComponent_EmpireSearch.Get();
            int floor = g?.rungFloor ?? 0;
            int remembered = g?.Remembered(map.Tile) ?? -1;
            st.EnsureInit(floor, RFPSettings.probesOpen, remembered);
        }

        /// <summary>The factor the ScenPart multiplies its base interval by for the next rung.</summary>
        public float NextIntervalFactor()
        {
            EnsureInit();
            float band = RFPSettings.visibilityDrivesPace
                ? EmpireLadderMath.BandIntervalMultiplier(EmpireSearch.Visibility()) : 1f;
            return st.NextIntervalFactor(band, RFPSettings.ladderPace);
        }

        private sealed class DefTable : IEmpireRungTable
        {
            public bool TryGetRung(int index, out EmpireRungKind kind)
            {
                RUT_EmpireRungDef d = RUT_EmpireRungDef.ForIndex(index);
                kind = d != null ? d.kind : EmpireRungKind.Probe;
                return d != null;
            }
        }
        private static readonly DefTable defTable = new DefTable();

        public RUT_EmpireRungDef NextRungDef()
        {
            EnsureInit();
            int i = st.NextRungIndex(defTable, new EmpireRungGates
            {
                cordonEnabled = RFPSettings.cordonEnabled,
                bombardmentEnabled = RFPSettings.bombardmentEnabled,
                probesOpen = RFPSettings.probesOpen,
            });
            return i < 0 ? null : RUT_EmpireRungDef.ForIndex(i);
        }

        // ---- firing -----------------------------------------------------------------------

        /// <summary>Called on the ScenPart's raid tick. Returns ticks to postpone by (storyteller
        /// spacing) or 0 when the rung fired / is already live / the ladder is terminal.</summary>
        public int FireNextRung(Faction faction)
        {
            int now = Find.TickManager.TicksGame;
            int gate = st.FireGate(ContactLive, now);
            if (gate >= 0) return gate;

            RUT_EmpireRungDef def = NextRungDef();
            if (def == null)
            {
                st.MarkExhausted();
                return 0;
            }
            st.Begin(def.rungIndex, now);
            activeRung = def;
            contactPawns.Clear();
            spotter = null;

            bool fired;
            try
            {
                EmpireSearch.FiringLadder = true;
                switch (def.kind)
                {
                    case EmpireRungKind.Probe: fired = FireProbe(def, faction); break;
                    case EmpireRungKind.Spotter: fired = FireSpotter(def, faction); break;
                    case EmpireRungKind.Bombardment: fired = FireBombardment(def, faction); break;
                    default: fired = FireRaidRung(def, faction); break;
                }
            }
            finally
            {
                EmpireSearch.FiringLadder = false;
            }
            if (!fired)
            {
                Log.Warning($"[EmpireSearch] rung {def.defName} could not fire on {map}; holding.");
                Resolve(false, quiet: true);
            }
            return 0;
        }

        private void SendLetter(string label, string text, LetterDef type, Faction faction, LookTargets look = null)
        {
            if (label.NullOrEmpty()) return;
            Find.LetterStack.ReceiveLetter(label.Formatted(faction.NameColored.Named("FACTION")),
                (text ?? "").Formatted(faction.NameColored.Named("FACTION")), type, look);
        }

        public void SendWarningLetter(Faction faction)
        {
            RUT_EmpireRungDef d = NextRungDef();
            if (d == null || d.warningHours <= 0f) return;
            SendLetter(d.warningLetterLabel, d.warningLetterText, LetterDefOf.ThreatBig, faction);
        }

        public IntVec3 ColonyCenter()
        {
            Building_GravEngine engine = Engine();
            if (engine != null) return engine.Position;
            List<Pawn> cols = map.mapPawns.FreeColonistsSpawned.ToList();
            if (cols.Count > 0)
            {
                return new IntVec3((int)cols.Average(p => p.Position.x), 0, (int)cols.Average(p => p.Position.z));
            }
            return map.Center;
        }

        public Building_GravEngine Engine() =>
            map.listerBuildings.AllBuildingsColonistOfClass<Building_GravEngine>().FirstOrDefault();

        private bool FireProbe(RUT_EmpireRungDef def, Faction faction)
        {
            IntVec3 colony = ColonyCenter();
            if (!CellFinderLoose.TryGetRandomCellWith(c => c.Standable(map) && !c.Roofed(map) && !c.Fogged(map)
                    && c.DistanceTo(colony) >= 40f, map, 1000, out IntVec3 drop)
                && !CellFinderLoose.TryGetRandomCellWith(c => c.Standable(map) && !c.Roofed(map), map, 1000, out drop))
                return false;

            int count = def.pawnCount.RandomInRange;
            List<Pawn> pawns = new List<Pawn>();
            PawnKindDef kind = def.pawnKinds.Select(n => DefDatabase<PawnKindDef>.GetNamedSilentFail(n)).FirstOrDefault(k => k != null);
            for (int i = 0; i < count; i++)
            {
                Pawn p = kind != null ? PawnGenerator.GeneratePawn(kind, faction) : null;
                if (p == null)
                {
                    p = PawnGroupMakerUtility.GeneratePawns(new PawnGroupMakerParms
                    {
                        groupKind = PawnGroupKindDefOf.Combat, tile = map.Tile, faction = faction, points = 60f,
                    }, warnOnZeroResults: false).FirstOrDefault();
                }
                if (p != null) pawns.Add(p);
            }
            if (pawns.Count == 0) return false;

            // the scan focus: between the drop and the colony, at the colony's edge
            Vector3 dir = (drop.ToVector3() - colony.ToVector3()).normalized;
            IntVec3 focus = (colony.ToVector3() + dir * 20f).ToIntVec3().ClampInsideMap(map);
            DropPodUtility.DropThingsNear(drop, map, pawns.Cast<Thing>(), faction: faction);
            int scanTicks = Mathf.RoundToInt(def.timeoutHours * GenDate.TicksPerHour);
            LordMaker.MakeNewLord(faction, new LordJob_ImperialProbe(focus, scanTicks), map, pawns);
            contactPawns.AddRange(pawns);
            SendLetter(def.arrivalLetterLabel, def.arrivalLetterText, LetterDefOf.ThreatSmall, faction,
                new LookTargets(drop, map));
            return true;
        }

        private bool FireSpotter(RUT_EmpireRungDef def, Faction faction)
        {
            if (!RCellFinder.TryFindRandomPawnEntryCell(out IntVec3 edge, map, 0.2f)) return false;
            float points = Mathf.Max(def.minPoints, StorytellerUtility.DefaultThreatPointsNow(map) * def.pointsFactor);
            List<Pawn> pawns = PawnGroupMakerUtility.GeneratePawns(new PawnGroupMakerParms
            {
                groupKind = PawnGroupKindDefOf.Combat, tile = map.Tile, faction = faction, points = points,
            }, warnOnZeroResults: false).ToList();
            if (pawns.Count == 0) return false;
            foreach (Pawn p in pawns)
            {
                GenSpawn.Spawn(p, CellFinder.RandomClosewalkCellNear(edge, map, 4), map);
            }
            IntVec3 colony = ColonyCenter();
            IntVec3 stageRoot = (edge.ToVector3() + (colony.ToVector3() - edge.ToVector3()) * 0.4f).ToIntVec3().ClampInsideMap(map);
            IntVec3 stage = CellFinder.RandomClosewalkCellNear(stageRoot, map, 6);
            int stageTicks = Mathf.RoundToInt(def.timeoutHours * GenDate.TicksPerHour);
            LordMaker.MakeNewLord(faction, new LordJob_ImperialSpotter(stage, stageTicks), map, pawns);
            contactPawns.AddRange(pawns);
            spotter = pawns[0];
            SendLetter(def.arrivalLetterLabel, def.arrivalLetterText, LetterDefOf.ThreatSmall, faction,
                new LookTargets(spotter));
            return true;
        }

        private bool FireRaidRung(RUT_EmpireRungDef def, Faction faction)
        {
            HashSet<Lord> before = new HashSet<Lord>(map.lordManager.lords);
            bool ok = ExecuteRaid(faction, def.arrivalMode, def.raidStrategy, def.pointsFactor, def.minPoints);
            if (def.kind == EmpireRungKind.Breach && def.secondArrivalMode != null)
            {
                ExecuteRaid(faction, def.secondArrivalMode, def.secondRaidStrategy ?? RaidStrategyDefOf.ImmediateAttack,
                    def.pointsFactor * def.secondPointsFactor, 0f);
            }
            foreach (Lord l in map.lordManager.lords)
            {
                if (!before.Contains(l) && l.faction == faction) contactPawns.AddRange(l.ownedPawns);
            }
            if (!ok) return false;
            if (def.kind == EmpireRungKind.Cordon)
            {
                nextIonTick = Find.TickManager.TicksGame + GenDate.TicksPerDay;
            }
            SendLetter(def.arrivalLetterLabel, def.arrivalLetterText, LetterDefOf.ThreatBig, faction,
                contactPawns.Count > 0 ? new LookTargets(contactPawns) : null);
            return true;
        }

        private bool ExecuteRaid(Faction faction, PawnsArrivalModeDef arrival, RaidStrategyDef strategy, float factor, float min)
        {
            IncidentParms parms = new IncidentParms
            {
                forced = true,
                target = map,
                faction = faction,
                points = Mathf.Max(min, StorytellerUtility.DefaultThreatPointsNow(map) * factor),
                raidArrivalMode = arrival,
                raidStrategy = strategy,
            };
            return IncidentDefOf.RaidEnemy.Worker.TryExecute(parms);
        }

        private bool FireBombardment(RUT_EmpireRungDef def, Faction faction)
        {
            bombardCenter = ColonyCenter();
            bombardTick = Find.TickManager.TicksGame + Mathf.RoundToInt(Mathf.Max(1f, def.telegraphHours) * GenDate.TicksPerHour);
            SendLetter(def.arrivalLetterLabel, def.arrivalLetterText, LetterDefOf.ThreatBig, faction,
                new LookTargets(bombardCenter, map));
            return true;
        }

        // ---- the live contact -------------------------------------------------------------

        public override void MapComponentTick()
        {
            if (activeRung == null) return;
            if (Find.TickManager.TicksGame % CheckInterval != 0) return;
            try
            {
                TickContact();
            }
            catch (Exception e)
            {
                Log.ErrorOnce("[EmpireSearch] contact tick threw: " + e, 0x3E51A7);
                Resolve(false, quiet: true);
            }
        }

        private void TickContact()
        {
            int now = Find.TickManager.TicksGame;
            int elapsed = now - contactStartTick;
            int successTicks = Mathf.RoundToInt(activeRung.successHours * GenDate.TicksPerHour);
            int timeoutTicks = Mathf.RoundToInt(activeRung.timeoutHours * GenDate.TicksPerHour);
            contactPawns.RemoveAll(p => p == null);

            switch (activeRung.kind)
            {
                case EmpireRungKind.Probe:
                    {
                        SelfDestructDeadProbes();
                        bool sees = contactPawns.Any(p => !p.Dead && !p.Downed && p.Spawned && SeesColony(p, 26f, 6f));
                        bool allGone = contactPawns.All(p => p.Dead || !p.SpawnedOrAnyParentSpawned);
                        ContactOutcome o = st.ProbeStep(sees, successTicks, allGone, elapsed, timeoutTicks, out float vis);
                        if (o == ContactOutcome.EmpireSucceeds)
                        {
                            EmpireSearch.AdjustVisibility(vis, "a probe transmitted a sighting");
                            Memo(LordJob_ImperialProbe.MemoDone);
                            Resolve(true);
                        }
                        else if (o == ContactOutcome.EmpireFails)
                        {
                            if (vis != 0f) EmpireSearch.AdjustVisibility(vis, "a probe destroyed before it transmitted");
                            Resolve(false);
                        }
                    }
                    break;

                case EmpireRungKind.Spotter:
                    {
                        bool gone = spotter == null || spotter.Dead || spotter.Downed || !spotter.Spawned;
                        bool sees = !gone && SeesColony(spotter, 45f, 10f);
                        ContactOutcome o = st.SpotterStep(gone, sees, successTicks, elapsed, timeoutTicks, out float vis);
                        if (o == ContactOutcome.EmpireSucceeds)
                        {
                            EmpireSearch.AdjustVisibility(vis, "a spotter called in the colony");
                            Memo(LordJob_ImperialSpotter.MemoDone);
                            Resolve(true);
                        }
                        else if (o == ContactOutcome.EmpireFails)
                        {
                            if (gone) Memo(LordJob_ImperialSpotter.MemoDone);
                            Resolve(false);
                        }
                    }
                    break;

                case EmpireRungKind.Cordon:
                    {
                        bool standing = contactPawns.Any(Standing);
                        ContactOutcome o = st.CordonStep(standing, now, Mathf.RoundToInt(RFPSettings.ionVolleyIntervalHours * GenDate.TicksPerHour),
                            elapsed, successTicks, out bool volley);
                        if (volley) IonVolley();
                        if (o != ContactOutcome.Continue) Resolve(o == ContactOutcome.EmpireSucceeds);
                    }
                    break;

                case EmpireRungKind.Strike:
                case EmpireRungKind.Breach:
                    {
                        bool allDown = contactPawns.All(p => p.Dead || p.Downed || !p.SpawnedOrAnyParentSpawned);
                        int fallen = contactPawns.Count(p => p.Dead || p.Downed);
                        ContactOutcome o = st.StrikeStep(allDown, elapsed, timeoutTicks, contactPawns.Count, fallen);
                        if (o != ContactOutcome.Continue) Resolve(o == ContactOutcome.EmpireSucceeds);
                    }
                    break;

                case EmpireRungKind.Bombardment:
                    if (st.BombardmentDue(now))
                    {
                        Bombardment b = (Bombardment)GenSpawn.Spawn(ThingDefOf.Bombardment, bombardCenter, map);
                        b.impactAreaRadius = BombardRadius;
                        b.duration = 900;
                        st.BombardmentLanded();
                        Resolve(true);
                    }
                    break;
            }
        }

        private static bool Standing(Pawn p) => p != null && !p.Dead && !p.Downed && p.SpawnedOrAnyParentSpawned;

        private bool SeesColony(Pawn watcher, float range, float darkRange)
        {
            IntVec3 from = watcher.Position;
            foreach (Pawn c in map.mapPawns.FreeColonistsSpawned)
            {
                float d = from.DistanceTo(c.Position);
                if (d > range) continue;
                if (EmpireLadderMath.Sees(d, GenSight.LineOfSight(from, c.Position, map, skipFirstCell: true),
                        map.glowGrid.GroundGlowAt(c.Position), range, darkRange))
                    return true;
            }
            Building_GravEngine engine = Engine();
            if (engine != null)
            {
                float d = from.DistanceTo(engine.Position);
                if (d <= range && EmpireLadderMath.Sees(d, GenSight.LineOfSight(from, engine.Position, map, skipFirstCell: true),
                        map.glowGrid.GroundGlowAt(engine.Position), range, darkRange))
                    return true;
            }
            return false;
        }

        private void SelfDestructDeadProbes()
        {
            foreach (Pawn p in contactPawns)
            {
                if (p.Dead && p.Corpse != null && p.Corpse.Spawned && p.Corpse.Map == map)
                {
                    IntVec3 at = p.Corpse.Position;
                    anyProbeDestroyed = true;
                    p.Corpse.Destroy();
                    GenExplosion.DoExplosion(at, map, 2.9f, DamageDefOf.Bomb, null, damAmount: 18);
                }
                else if (p.Dead)
                {
                    anyProbeDestroyed = true;
                }
            }
        }

        /// <summary>Ion = EMP: stun what is near the engine and push the engine's launch cooldown
        /// out by a few hours. Never days — the owner ruled the escape is never closed.</summary>
        private void IonVolley()
        {
            Building_GravEngine engine = Engine();
            if (engine == null) return;
            GenExplosion.DoExplosion(engine.Position, map, 3.9f, DamageDefOf.EMP, null);
            int until = Find.TickManager.TicksGame + Mathf.RoundToInt(Mathf.Clamp(RFPSettings.ionLockoutHours, 1f, 23f) * GenDate.TicksPerHour);
            if (engine.cooldownCompleteTick < until) engine.cooldownCompleteTick = until;
            Messages.Message("RUT_IonVolleyMessage".Translate(), new LookTargets(engine), MessageTypeDefOf.ThreatBig);
        }

        private void Memo(string memo)
        {
            foreach (Lord l in contactPawns.Where(p => !p.Dead).Select(p => p.GetLord()).Where(l => l != null).Distinct().ToList())
            {
                l.ReceiveMemo(memo);
            }
        }

        /// <summary>The contact is over. Climb on an Empire success, hold on a failure, and ask
        /// the ScenPart to schedule the next rung.</summary>
        public void Resolve(bool empireSucceeded, bool quiet = false)
        {
            RUT_EmpireRungDef def = activeRung;
            Faction faction = EmpireSearch.Part?.PursuitFaction;
            int floor = GameComponent_EmpireSearch.Get()?.rungFloor ?? 0;
            bool schedule = st.Resolve(def != null ? def.rungIndex : -1, empireSucceeded, floor);
            if (def != null)
            {
                if (!quiet && faction != null)
                {
                    if (empireSucceeded) SendLetter(def.successLetterLabel, def.successLetterText, LetterDefOf.ThreatSmall, faction);
                    else SendLetter(def.failLetterLabel, def.failLetterText, LetterDefOf.PositiveEvent, faction);
                }
            }
            activeRung = null;
            contactPawns.Clear();
            spotter = null;
            if (schedule) EmpireSearch.Part?.ScheduleLadder(map);
        }

        // ---- the marked target area -------------------------------------------------------

        public override void MapComponentUpdate()
        {
            if (bombardTick > 0 && bombardCenter.IsValid && Find.CurrentMap == map)
            {
                GenDraw.DrawRadiusRing(bombardCenter, BombardRadius);
            }
        }

        public string AlertLine()
        {
            RUT_EmpireRungDef next = NextRungDef();
            string band = EmpireSearch.BandLabel(EmpireSearch.Visibility());
            string rung = ContactLive ? activeRung.LabelCap.ToString() : next?.LabelCap.ToString() ?? "-";
            return "RUT_SearchAlertLine".Translate(
                (ContactLive ? activeRung.rungIndex : nextRung).Named("RUNG"),
                EmpireLadderMath.TopRung.Named("TOP"),
                (band ?? "?").Named("BAND"),
                rung.Named("NEXT"));
        }
    }

    /// <summary>Aftermath's battle.closed, bound softly: a classified battle whose actors are our
    /// contact's pawns decides a strike or breach rung (REPELLED = the Empire failed).</summary>
    [StaticConstructorOnStartup]
    public static class EmpireSearchAftermathBridge
    {
        static EmpireSearchAftermathBridge()
        {
            Type t = AccessTools.TypeByName("RimMandrake.Aftermath.ChronicleEvents");
            MethodInfo sub = t?.GetMethod("Subscribe", new[] { typeof(Action<object>) });
            if (sub == null) return;
            sub.Invoke(null, new object[] { (Action<object>)OnEvent });
        }

        private static void OnEvent(object e)
        {
            if (e == null) return;
            Type t = e.GetType();
            if (!Equals(t.GetField("Kind")?.GetValue(e), "battle.closed")) return;
            if (!(t.GetField("Map")?.GetValue(e) is Map map)) return;
            MapComponent_EmpireSearch c = MapComponent_EmpireSearch.For(map);
            if (c?.activeRung == null) return;
            if (c.activeRung.kind != EmpireRungKind.Strike && c.activeRung.kind != EmpireRungKind.Breach) return;
            if (!(t.GetField("Actors")?.GetValue(e) is List<Pawn> actors)) return;
            if (!actors.Any(a => c.contactPawns.Contains(a))) return;
            c.aftermathOutcome = t.GetField("Outcome")?.GetValue(e) as string;
        }
    }

    /// <summary>Design §5: a storyteller-picked Empire raid never climbs the ladder, and the two
    /// never land within 2 days of each other on one map. Records storyteller raids of the
    /// ladder faction, and refuses one that would land inside 2 days of a ladder contact.
    /// Forced incidents (quests, the ladder itself) pass untouched.</summary>
    [HarmonyPatch(typeof(IncidentWorker), nameof(IncidentWorker.TryExecute))]
    internal static class IncidentWorker_TryExecute_EmpireSpacing
    {
        private static bool IsStorytellerLadderRaid(IncidentWorker w, IncidentParms parms, out Map map)
        {
            map = parms?.target as Map;
            return map != null && w is IncidentWorker_RaidEnemy && !parms.forced && !EmpireSearch.FiringLadder
                && EmpireSearch.IsLadderFaction(parms.faction);
        }

        private static bool Prefix(IncidentWorker __instance, IncidentParms parms, ref bool __result)
        {
            if (!IsStorytellerLadderRaid(__instance, parms, out Map map)) return true;
            MapComponent_EmpireSearch c = MapComponent_EmpireSearch.For(map);
            if (c == null) return true;
            if (EmpireLadderState.BlockStorytellerRaid(c.ContactLive, Find.TickManager.TicksGame, c.lastLadderFireTick))
            {
                __result = false;
                return false;
            }
            return true;
        }

        private static void Postfix(IncidentWorker __instance, IncidentParms parms, bool __result)
        {
            if (!__result || !IsStorytellerLadderRaid(__instance, parms, out Map map)) return;
            MapComponent_EmpireSearch c = MapComponent_EmpireSearch.For(map);
            if (c != null) c.lastStorytellerRaidTick = Find.TickManager.TicksGame;
        }
    }
}
