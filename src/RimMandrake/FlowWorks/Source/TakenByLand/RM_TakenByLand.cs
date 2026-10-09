using System;
using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks.TakenByLand
{
    // ════════════════════════════════════════════════════════════════════
    // TAKEN_BY_LAND_SERVICE_1 (design pass X-10): "the land takes a pawn and gives them back later" as ONE service. The river's
    // swept-away (FlowWorks) and the dune gale's carry (Stillsand) were the same thing built twice: a hold, a letter, a return.
    // A taker registers a RM_TakenPolicy under a kind ("river", "gale"); RM_TakenByLand.Take(pawn, kind, ...) does the rest:
    // removes the pawn (the policy's way), holds it as a world pawn, writes the taker's letter, leaves a ground trace where it
    // was taken (so no one vanishes without a readable sign), and RM_WorldComponent_TakenByLand returns it later with a second
    // letter. The old per-taker books (RM_WorldComponent_SweptAway, RM_GameComponent_GaleCarried) stay only to drain records saved
    // before this service; delete them once no save holds one.
    // The trace is the kit's RM_Filth_DragMark where Creature Behaviors is loaded, until EVENT_TRACE_PROPS_LIBRARY_1 lands a real prop.
    // ════════════════════════════════════════════════════════════════════

    public class RM_TakenRecord : IExposable
    {
        public Pawn pawn;
        public string kind;
        public int mapId = -1;
        public int takenTick = -1;
        public int returnTick;
        public bool wasPlayer;
        public IntVec3 origin;
        /// <summary>The taker's direction of travel (the gale's wind); zero for a taker with none.</summary>
        public IntVec3 dir;
        public float aliveChance = 1f;

        public void ExposeData()
        {
            Scribe_References.Look(ref pawn, "pawn", true);
            Scribe_Values.Look(ref kind, "kind");
            Scribe_Values.Look(ref mapId, "mapId", -1);
            Scribe_Values.Look(ref takenTick, "takenTick", -1);
            Scribe_Values.Look(ref returnTick, "returnTick");
            Scribe_Values.Look(ref wasPlayer, "wasPlayer");
            Scribe_Values.Look(ref origin, "origin");
            Scribe_Values.Look(ref dir, "dir");
            Scribe_Values.Look(ref aliveChance, "aliveChance", 1f);
        }
    }

    /// <summary>What differs between takers. Defaults are the river's: hold only your own, back alive on a random edge.</summary>
    public abstract class RM_TakenPolicy
    {
        public abstract string Kind { get; }

        /// <summary>Does the service hold this pawn for a return? Default: only the player's (and the player's prisoners).</summary>
        public virtual bool Holds(Pawn p) => (p.Faction != null && p.Faction.IsPlayer) || (p.HostFaction != null && p.HostFaction.IsPlayer);

        /// <summary>Days until it is due back.</summary>
        public abstract float RollDays();

        /// <summary>Chance it comes back alive (1 = always).</summary>
        public virtual float AliveChance => 1f;

        /// <summary>Take the pawn off the map and into the world's keeping. Default: despawn + keep forever.</summary>
        public virtual void Remove(Pawn p, Map map, RM_TakenRecord r)
        {
            p.DeSpawn();
            Find.WorldPawns.PassToWorld(p, PawnDiscardDecideMode.KeepForever);
        }

        /// <summary>A pawn this policy does not hold: leave a readable sign and let the world have it.</summary>
        public virtual void TakeStranger(Pawn p, Map map)
        {
            Messages.Message(p.LabelShortCap + " was taken off the map.", new LookTargets(p.PositionHeld, map), MessageTypeDefOf.NeutralEvent);
            p.DeSpawn();
            Find.WorldPawns.PassToWorld(p, PawnDiscardDecideMode.Decide);
        }

        /// <summary>Where it comes back in. Default: a standable, dry edge cell.</summary>
        public virtual IntVec3 PickReturnCell(RM_TakenRecord r, Map map)
        {
            if (!CellFinder.TryFindRandomEdgeCellWith(c => c.Standable(map) && !c.GetTerrain(map).IsWater, map, CellFinder.EdgeRoadChance_Neutral, out IntVec3 cell)
                && !CellFinder.TryFindRandomEdgeCellWith(c => c.Standable(map), map, 0f, out cell))
            {
                return IntVec3.Invalid;
            }
            return cell;
        }

        public virtual void AfterReturn(RM_TakenRecord r, Pawn p) { }

        // Letters. Return null for "no letter".
        public abstract void TakenLetter(RM_TakenRecord r, Pawn p, Map map, float days, out string label, out string text, out LetterDef def);
        public abstract void ReturnedLetter(RM_TakenRecord r, Pawn p, Pawn target, bool dead, out string label, out string text, out LetterDef def);
        public virtual void LostLetter(RM_TakenRecord r, string name, bool mapGone, out string label, out string text)
        {
            label = "Lost: " + name;
            text = name + " was taken and never given back" + (mapGone ? "; the map they were taken from is gone." : ".");
        }
        public virtual void DiedLetter(RM_TakenRecord r, Pawn p, out string label, out string text)
        {
            label = "Lost: " + p.LabelShortCap;
            text = p.LabelShortCap + " died out past the edge. The land kept the body.";
        }
    }

    public static class RM_TakenByLand
    {
        private static readonly Dictionary<string, RM_TakenPolicy> policies = new Dictionary<string, RM_TakenPolicy>();

        public static void Register(RM_TakenPolicy p) { policies[p.Kind] = p; }
        public static RM_TakenPolicy PolicyFor(string kind) { policies.TryGetValue(kind ?? "", out RM_TakenPolicy p); return p; }

        /// <summary>Take a spawned pawn on its map. Returns true when the service now holds it for a return.</summary>
        public static bool Take(Pawn p, string kind, IntVec3 dir = default(IntVec3), float days = -1f, float aliveChance = -1f)
        {
            RM_TakenPolicy policy = PolicyFor(kind);
            Map map = p?.Map;
            if (policy == null || map == null || !p.Spawned) return false;
            IntVec3 origin = p.Position;
            RM_WorldComponent_TakenByLand comp = Find.World?.GetComponent<RM_WorldComponent_TakenByLand>();
            if (!policy.Holds(p) || comp == null)
            {
                if (policy.Holds(p) && comp == null) return false;   // cannot hold them: leave the pawn rather than lose them
                LeaveTrace(map, origin);
                policy.TakeStranger(p, map);
                return false;
            }
            if (days < 0f) days = policy.RollDays();
            var r = new RM_TakenRecord
            {
                pawn = p,
                kind = kind,
                mapId = map.uniqueID,
                takenTick = Find.TickManager.TicksGame,
                returnTick = RM_TakenByLandKernel.ReturnTick(Find.TickManager.TicksGame, days, GenDate.TicksPerDay),
                wasPlayer = p.Faction != null && p.Faction.IsPlayer,
                origin = origin,
                dir = dir,
                aliveChance = aliveChance >= 0f ? aliveChance : policy.AliveChance,
            };
            policy.Remove(p, map, r);
            comp.Add(r);
            LeaveTrace(map, origin);
            policy.TakenLetter(r, p, map, days, out string label, out string text, out LetterDef def);
            if (label != null) Find.LetterStack.ReceiveLetter(label, text, def ?? LetterDefOf.NegativeEvent, new LookTargets(new TargetInfo(origin, map)));
            return true;
        }

        /// <summary>Session counter for a dev/bridge read: ground traces left. Never saved.</summary>
        public static int TracesLeft;

        /// <summary>The ground trace at the spot a pawn was taken (nearest cell within 2 that takes filth).</summary>
        public static void LeaveTrace(Map map, IntVec3 at)
        {
            if (!RimMandrake.FlowWorks.Rivers.RM_RiversSettings.takenByLandTraceEnabled || map == null || !at.IsValid) return;
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Filth_DragMark");
            if (def == null) return;
            foreach (IntVec3 c in GenRadial.RadialCellsAround(at, 2f, true))
            {
                if (c.InBounds(map) && FilthMaker.TryMakeFilth(c, map, def))
                {
                    TracesLeft++;
                    return;
                }
            }
        }
    }

    public class RM_WorldComponent_TakenByLand : WorldComponent
    {
        public const int ScanInterval = 250;
        private List<RM_TakenRecord> records = new List<RM_TakenRecord>();

        public RM_WorldComponent_TakenByLand(World world) : base(world) { }

        public int PendingCount => records.Count;
        public int PendingOfKind(string kind) { int n = 0; foreach (RM_TakenRecord r in records) if (r.kind == kind) n++; return n; }

        public void Add(RM_TakenRecord r) { records.Add(r); }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref records, "rmTakenByLand", LookMode.Deep);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                records = records ?? new List<RM_TakenRecord>();
                records.RemoveAll(r => r == null);
            }
        }

        public override void WorldComponentTick()
        {
            int now = Find.TickManager.TicksGame;
            if (!RM_TakenByLandKernel.ShouldScan(records.Count, now, ScanInterval)) return;
            foreach (RM_TakenRecord r in RM_TakenByLandKernel.TakeWhere(records, c => RM_TakenByLandKernel.IsDue(c.returnTick, now)))
            {
                if (!SafeReturn(r)) records.Add(r);   // nowhere to walk home to yet: keep waiting
            }
        }

        /// <summary>Return every record taken from this map by an earlier event (a storm's end). Returns how many came back.</summary>
        public int ReturnEarlierOnMap(string kind, Map map, int eventStartTick)
        {
            int n = 0;
            foreach (RM_TakenRecord r in RM_TakenByLandKernel.TakeWhere(records,
                c => c.kind == kind && RM_TakenByLandKernel.EarlierEventOnMap(c.mapId, c.takenTick, map.uniqueID, eventStartTick)))
            {
                if (SafeReturn(r)) n++; else records.Add(r);
            }
            return n;
        }

        /// <summary>Bring everything back now (dev proof hook).</summary>
        public void ReturnAllNow()
        {
            foreach (RM_TakenRecord r in RM_TakenByLandKernel.TakeWhere(records, c => true))
            {
                if (!SafeReturn(r)) records.Add(r);
            }
        }

        private static bool SafeReturn(RM_TakenRecord r)
        {
            try { return Return(r); }
            catch (Exception e)
            {
                Log.Error("[FlowWorks] taken-by-land return of " + r?.pawn + " failed: " + e);
                // Return() takes the pawn out of the world's keeping before it spawns it. If it threw in between, put the pawn back
                // and retry in an hour, so a throw never leaves a pawn held by nothing (no pawn vanishes without a sign).
                Pawn p = r?.pawn;
                if (p != null && !p.Destroyed && !p.Discarded && !p.Spawned)
                {
                    if (!Find.WorldPawns.Contains(p)) Find.WorldPawns.PassToWorld(p, PawnDiscardDecideMode.KeepForever);
                    r.returnTick = Find.TickManager.TicksGame + GenDate.TicksPerHour;
                    return false;
                }
                return true;
            }
        }

        /// <summary>True when the record is finished with (returned or lost); false to keep it for later.</summary>
        private static bool Return(RM_TakenRecord r)
        {
            RM_TakenPolicy policy = RM_TakenByLand.PolicyFor(r.kind);
            if (policy == null) return false;   // the taker's mod is not loaded this session: hold on
            Pawn p = r.pawn;
            Map map = null;
            foreach (Map m in Find.Maps) if (m.uniqueID == r.mapId) map = m;
            if (map == null) map = SurfaceHomeMap();
            bool missing = p == null || p.Destroyed || p.Discarded;
            if (map == null && !missing) return false;   // nowhere to walk home to yet; keep waiting
            if (p != null && Find.WorldPawns.Contains(p)) Find.WorldPawns.RemovePawn(p);
            bool alive = !missing && !p.Dead && Rand.Chance(r.aliveChance);
            TakenOutcome outcome = RM_TakenByLandKernel.Decide(missing, map == null, !missing && p.Dead, alive);
            if (outcome == TakenOutcome.LostMissing)
            {
                policy.LostLetter(r, p?.LabelShortCap ?? "a body", map == null, out string l1, out string t1);
                if (l1 != null) Find.LetterStack.ReceiveLetter(l1, t1, LetterDefOf.NeutralEvent);
                return true;
            }
            if (outcome == TakenOutcome.LostDead)
            {
                policy.DiedLetter(r, p, out string l2, out string t2);
                if (l2 != null) Find.LetterStack.ReceiveLetter(l2, t2, LetterDefOf.NeutralEvent);
                return true;
            }
            IntVec3 cell = policy.PickReturnCell(r, map);
            if (!cell.IsValid) cell = map.Center;
            GenSpawn.Spawn(p, cell, map, WipeMode.VanishOrMoveAside);
            policy.AfterReturn(r, p);
            if (outcome == TakenOutcome.SpawnThenKill && !p.Dead) p.Kill(null);
            Thing target = p.Dead ? (Thing)p.Corpse ?? p : p;
            policy.ReturnedLetter(r, p, null, p.Dead, out string label, out string text, out LetterDef def);
            if (label != null) Find.LetterStack.ReceiveLetter(label, text, def ?? (p.Dead ? LetterDefOf.Death : LetterDefOf.PositiveEvent), target);
            return true;
        }

        // SURFACE_HOME_MAP_HELPER_1: never the sea floor (ship is the only way down).
        private static Map SurfaceHomeMap()
        {
            foreach (Map m in Find.Maps)
                if (m.IsPlayerHome && !(m.Tile.Valid && m.Tile.Layer?.Def?.defName == "RM_SeabedLayer")) return m;
            return null;
        }
    }

    /// <summary>The river's swept-away, as a policy: only your own are held, back alive on a dry edge in 1-3 days.</summary>
    public class RM_RiverTakenPolicy : RM_TakenPolicy
    {
        public override string Kind => "river";

        public override float RollDays()
        {
            float min = Rivers.RM_RiversSettings.washedAwayMinDays;
            float max = Mathf.Max(min, Rivers.RM_RiversSettings.washedAwayMaxDays);
            return Rand.Range(min, max);
        }

        public override void TakeStranger(Pawn p, Map map)
        {
            Messages.Message(p.LabelShortCap + " was swept off the map by the river.", new LookTargets(p.PositionHeld, map), MessageTypeDefOf.NeutralEvent);
            p.DeSpawn();
            Find.WorldPawns.PassToWorld(p, PawnDiscardDecideMode.Decide);
        }

        public override void TakenLetter(RM_TakenRecord r, Pawn p, Map map, float days, out string label, out string text, out LetterDef def)
        {
            label = "Swept away: " + p.LabelShortCap;
            text = p.LabelShortCap + " was carried off the map by the river's current. " + p.Possessive().CapitalizeFirst()
                 + " will make " + p.Possessive() + " way back on foot in about " + days.ToString("F1") + " days, bruised but alive. Wait for them.";
            def = LetterDefOf.NegativeEvent;
        }

        public override void ReturnedLetter(RM_TakenRecord r, Pawn p, Pawn target, bool dead, out string label, out string text, out LetterDef def)
        {
            label = "Back from the river: " + p.LabelShortCap;
            text = p.LabelShortCap + " has walked back after being washed away downstream.";
            def = LetterDefOf.PositiveEvent;
        }
    }

    [StaticConstructorOnStartup]
    internal static class RM_TakenByLandStartup
    {
        static RM_TakenByLandStartup() { RM_TakenByLand.Register(new RM_RiverTakenPolicy()); }
    }
}
