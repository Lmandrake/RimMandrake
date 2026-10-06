using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FloodedCanyon
{
    // ════════════════════════════════════════════════════════════════════
    // LEDGES OF MERCY — the refuge half (CRACKEDLANDS_LEDGES_OF_MERCY_1).
    //
    // "During warnings, neutral visitors and trained animals try to reach
    // the nearest ledge." What a ledge IS physically (a walkable edifice
    // platform, a KCSG piece cut into a cliff, a terrain band by the walls)
    // is the owner's open question, so this file does not decide it. It
    // works on ANY ThingDef that carries RM_RefugeLedgeExtension: every
    // standable cell a spawned ledge thing occupies is a refuge cell. When
    // the form is ruled, the ledge def gains the extension and this machinery
    // needs no change.
    //
    //   * The flood never takes a refuge cell (RM_MapComponent_CanyonFlood.
    //     Eligible asks IsRefugeCell) — an edifice ledge was already safe;
    //     this makes a non-edifice form safe too.
    //   * Herald, Warned and Flooding: every SweepIntervalTicks, each neutral
    //     humanlike visitor and each of the player's trained animals that is
    //     not on a refuge cell is sent (Goto) to the nearest reachable one,
    //     and one already standing on a refuge cell is held there (Wait).
    //     The sweep re-issues rather than trusting one order, because a
    //     visitor's lord duty may pull it back off.
    //   * Chime-line anchors (RM_ChimeAnchorExtension): RingChime tolls from
    //     the anchor nearest each staged position instead of the position.
    //
    // NOT here, deliberately: the ledge def itself, the GenStep placing it,
    // the inscriptions and carvings (owner's lore lines), the one-shot
    // memory. See the item.
    // ════════════════════════════════════════════════════════════════════

    // Marker: this thing is a refuge ledge. Its standable occupied cells are
    // refuge cells.
    public class RM_RefugeLedgeExtension : DefModExtension
    {
    }

    // Marker: this thing is a chime-line anchor the flood's staged chimes
    // toll from.
    public class RM_ChimeAnchorExtension : DefModExtension
    {
    }

    public class RM_MapComponent_LedgeRefuge : MapComponent
    {
        // PROVISIONAL (numbers ruling 2026-10-03, tuned live later):
        //   SweepIntervalTicks 250 — ten re-checks per in-game hour; a pawn
        //     pulled off a ledge is re-sent within a tenth of an hour.
        //   MaxReachProbes 12 — reachability tests per pawn per sweep, nearest
        //     first; a ledge farther than the 12th-nearest candidate cell is
        //     ignored that sweep.
        //   HoldWaitTicks 500 — a held pawn's Wait expires after two sweeps,
        //     so a pawn never stays frozen after the flood recedes.
        public const int SweepIntervalTicks = 250;
        public const int MaxReachProbes = 12;
        public const int HoldWaitTicks = 500;

        private static List<ThingDef> ledgeDefsInt;
        private static List<ThingDef> anchorDefsInt;

        private readonly HashSet<IntVec3> refugeCells = new HashSet<IntVec3>();
        private readonly List<IntVec3> refugeList = new List<IntVec3>();

        // Debug-designated refuge cells: the live test surface, so the seek
        // behaviour is provable before any ledge def exists.
        private List<IntVec3> debugCells = new List<IntVec3>();

        private int lastSweepTick = -1;
        private int sentTotal;
        private int heldTotal;
        private int lastSeekers;
        private int lastOnLedge;
        private int lastNoReach;

        public RM_MapComponent_LedgeRefuge(Map map) : base(map)
        {
        }

        private static List<ThingDef> LedgeDefs =>
            ledgeDefsInt ?? (ledgeDefsInt = DefDatabase<ThingDef>.AllDefsListForReading.FindAll(d => d.HasModExtension<RM_RefugeLedgeExtension>()));

        private static List<ThingDef> AnchorDefs =>
            anchorDefsInt ?? (anchorDefsInt = DefDatabase<ThingDef>.AllDefsListForReading.FindAll(d => d.HasModExtension<RM_ChimeAnchorExtension>()));

        public bool IsRefugeCell(IntVec3 c) => refugeCells.Contains(c);

        public int RefugeCellCount => refugeCells.Count;

        // Rebuilt at every sweep and before the flood picks its footprint, so
        // a ledge built since the last sweep is honoured.
        public void RefreshCells()
        {
            refugeCells.Clear();
            refugeList.Clear();
            List<ThingDef> defs = LedgeDefs;
            for (int i = 0; i < defs.Count; i++)
            {
                List<Thing> things = map.listerThings.ThingsOfDef(defs[i]);
                for (int j = 0; j < things.Count; j++)
                {
                    foreach (IntVec3 c in things[j].OccupiedRect())
                    {
                        AddCell(c);
                    }
                }
            }
            for (int i = 0; i < debugCells.Count; i++)
            {
                AddCell(debugCells[i]);
            }
        }

        private void AddCell(IntVec3 c)
        {
            if (c.InBounds(map) && c.Standable(map) && refugeCells.Add(c))
            {
                refugeList.Add(c);
            }
        }

        // The anchor nearest `near`, or `near` itself when the map carries
        // none (or the setting is off).
        public IntVec3 NearestAnchorTo(IntVec3 near)
        {
            if (!RM_FloodedCanyonSettings.chimeAnchorsEnabled)
            {
                return near;
            }
            IntVec3 best = near;
            float bestD = float.MaxValue;
            List<ThingDef> defs = AnchorDefs;
            for (int i = 0; i < defs.Count; i++)
            {
                List<Thing> things = map.listerThings.ThingsOfDef(defs[i]);
                for (int j = 0; j < things.Count; j++)
                {
                    float d = (things[j].Position - near).LengthHorizontalSquared;
                    if (d < bestD)
                    {
                        bestD = d;
                        best = things[j].Position;
                    }
                }
            }
            return best;
        }

        public int AnchorCount()
        {
            int n = 0;
            List<ThingDef> defs = AnchorDefs;
            for (int i = 0; i < defs.Count; i++)
            {
                n += map.listerThings.ThingsOfDef(defs[i]).Count;
            }
            return n;
        }

        // Called by the flood clock on each warning-phase entry and every
        // SweepIntervalTicks while Herald, Warned or Flooding.
        public void Sweep()
        {
            lastSweepTick = Find.TickManager.TicksGame;
            RefreshCells();
            lastSeekers = 0;
            lastOnLedge = 0;
            lastNoReach = 0;
            if (!RM_FloodedCanyonSettings.ledgeRefugeEnabled || refugeList.Count == 0)
            {
                return;
            }
            List<Pawn> pawns = new List<Pawn>(map.mapPawns.AllPawnsSpawned);
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (!IsSeeker(p))
                {
                    continue;
                }
                lastSeekers++;
                if (refugeCells.Contains(p.Position))
                {
                    lastOnLedge++;
                    if (p.CurJobDef != JobDefOf.Wait)
                    {
                        Job hold = JobMaker.MakeJob(JobDefOf.Wait, p.Position);
                        hold.expiryInterval = HoldWaitTicks;
                        p.jobs.StartJob(hold, JobCondition.InterruptForced);
                        heldTotal++;
                    }
                    continue;
                }
                Job cur = p.CurJob;
                if (cur != null && cur.def == JobDefOf.Goto && cur.targetA.IsValid && refugeCells.Contains(cur.targetA.Cell))
                {
                    continue;
                }
                IntVec3 dest = NearestReachable(p);
                if (!dest.IsValid)
                {
                    lastNoReach++;
                    continue;
                }
                Job go = JobMaker.MakeJob(JobDefOf.Goto, dest);
                go.locomotionUrgency = LocomotionUrgency.Sprint;
                p.jobs.StartJob(go, JobCondition.InterruptForced);
                sentTotal++;
            }
        }

        // Neutral humanlike visitors, and the player's animals that have
        // learned at least one trainable. Never colonists, prisoners,
        // hostiles, the downed, the drafted or a pawn in a mental state.
        public static bool IsSeeker(Pawn p)
        {
            if (p == null || p.Dead || p.Downed || p.Faction == null || p.jobs == null)
            {
                return false;
            }
            if (p.InMentalState || p.Drafted || p.IsPrisoner)
            {
                return false;
            }
            if (p.Faction.IsPlayer)
            {
                return p.RaceProps.Animal && IsTrained(p);
            }
            return p.RaceProps.Humanlike && !p.Faction.HostileTo(Faction.OfPlayer);
        }

        private static bool IsTrained(Pawn p)
        {
            if (p.training == null)
            {
                return false;
            }
            List<TrainableDef> all = DefDatabase<TrainableDef>.AllDefsListForReading;
            for (int i = 0; i < all.Count; i++)
            {
                if (p.training.HasLearned(all[i]))
                {
                    return true;
                }
            }
            return false;
        }

        // Nearest reachable refuge cell, preferring one no pawn stands on.
        private IntVec3 NearestReachable(Pawn p)
        {
            List<IntVec3> sorted = new List<IntVec3>(refugeList);
            IntVec3 from = p.Position;
            sorted.Sort((a, b) => (a - from).LengthHorizontalSquared.CompareTo((b - from).LengthHorizontalSquared));
            IntVec3 fallback = IntVec3.Invalid;
            int probes = 0;
            for (int i = 0; i < sorted.Count && probes < MaxReachProbes; i++)
            {
                IntVec3 c = sorted[i];
                bool empty = c.GetFirstPawn(map) == null;
                if (!empty && fallback.IsValid)
                {
                    continue;
                }
                probes++;
                if (!p.CanReach(c, PathEndMode.OnCell, Danger.Deadly))
                {
                    continue;
                }
                if (empty)
                {
                    return c;
                }
                fallback = c;
            }
            return fallback;
        }

        // ---------------------------------------------------------- debug

        // Marks up to `count` standable, dry, unroofed cells spiralling out
        // from `center` as debug refuge cells. Returns how many were added.
        public int DebugMarkRefugeNear(IntVec3 center, int count)
        {
            int added = 0;
            int r = GenRadial.NumCellsInRadius(12f);
            for (int i = 0; i < r && added < count; i++)
            {
                IntVec3 c = center + GenRadial.RadialPattern[i];
                if (!c.InBounds(map) || !c.Standable(map) || c.Roofed(map) || debugCells.Contains(c))
                {
                    continue;
                }
                TerrainDef t = map.terrainGrid.TerrainAt(c);
                if (t == null || t.IsWater)
                {
                    continue;
                }
                debugCells.Add(c);
                added++;
            }
            RefreshCells();
            return added;
        }

        public void DebugClearRefuge()
        {
            debugCells.Clear();
            RefreshCells();
        }

        public string DebugStateReport()
        {
            RefreshCells();
            int seekers = 0, onLedge = 0, enRoute = 0;
            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (!IsSeeker(p))
                {
                    continue;
                }
                seekers++;
                if (refugeCells.Contains(p.Position))
                {
                    onLedge++;
                }
                else if (p.CurJob != null && p.CurJob.def == JobDefOf.Goto && p.CurJob.targetA.IsValid
                         && refugeCells.Contains(p.CurJob.targetA.Cell))
                {
                    enRoute++;
                }
            }
            return string.Format(
                "refuge: enabled={0} anchorsEnabled={1} ledgeDefs={2} anchorDefs={3} anchors={4} refugeCells={5} "
                + "debugCells={6} seekers={7} onLedge={8} enRoute={9} sentTotal={10} heldTotal={11} "
                + "lastSweepTick={12} lastSeekers={13} lastOnLedge={14} lastNoReach={15} nowTick={16}",
                RM_FloodedCanyonSettings.ledgeRefugeEnabled, RM_FloodedCanyonSettings.chimeAnchorsEnabled,
                LedgeDefs.Count, AnchorDefs.Count, AnchorCount(), refugeCells.Count, debugCells.Count,
                seekers, onLedge, enRoute, sentTotal, heldTotal, lastSweepTick, lastSeekers, lastOnLedge,
                lastNoReach, Find.TickManager.TicksGame);
        }

        public override void FinalizeInit()
        {
            base.FinalizeInit();
            RefreshCells();
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref debugCells, "debugCells", LookMode.Value);
            Scribe_Values.Look(ref sentTotal, "sentTotal", 0);
            Scribe_Values.Look(ref heldTotal, "heldTotal", 0);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && debugCells == null)
            {
                debugCells = new List<IntVec3>();
            }
        }
    }
}
