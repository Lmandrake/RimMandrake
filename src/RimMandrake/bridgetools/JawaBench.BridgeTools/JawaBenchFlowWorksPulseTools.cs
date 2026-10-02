// JawaBenchFlowWorksPulseTools.cs - the FlowWorks Northstar v2 owed tools
// (design/RimMandrake/flowworks_northstar_script_plan_2026-10-02.md section 8, items 1-3):
//
//   flowworks_pulse            run the depth engine's pulse N times DIRECTLY, 0 game ticks,
//                              returning the D/F vector after every pulse (owed tool 2)
//   flowworks_excavation_rect  D/F/source/sink/terrain for every cell of a rect in ONE call
//                              (owed tool 1; replaces ~80% of per-cell report polls, R10)
//   flowworks_pit_report       a pit as the depth GRID sees it: D/F, pit width, ladder, room,
//                              each pawn on the cell with the trap rule's verdict and real
//                              CanReach to the lip (owed tool 3; SUPERDEEP_HOLDER_RETIRE_1)
//
// COUPLING: strictly by reflection, like the other two FlowWorks tool files - the companion
// must register on a mod list WITHOUT FlowWorks, so every resolve failure is a loud Fail
// naming what was missing. EVERY member read from src/RimMandrake/FlowWorks/Source:
//   RM_MapComponent_Excavation: PRIVATE void DoPulse() (no parameters - the body the
//     MapComponentTick scheduler calls; it reads RimMandrakeFlowWorksSettings itself, so
//     refill/recession dt = PulseIntervalTicks exactly as a scheduled pulse), private
//     depthGrid / fillGrid (byte[] by CellIndices), private excavatedCells (HashSet<IntVec3>),
//     private nextPulseTick, public IsSourceCell / IsSinkCell, SinkTransferredTotal,
//     OverflowDestroyedTotal, ExcavatedCellCount, Stock.
//   RM_SuperdeepTrap (static): IsHeld(Pawn), Captures(Pawn), RequiredWidth(Pawn),
//     MeasuredPitWidth(Map, IntVec3); RM_LadderUtility.HasLadder(Map, IntVec3);
//   RM_MapComponent_Excavation: internal SuperdeepTrap (RM_SuperdeepTrapState: IsJumper,
//     DescentCount, RecentDescents), private fillGrid.
//   RimMandrakeFlowWorksSettings: static depthEngineEnabled, superdeepCaptureEnabled,
//     ladderRequiredToExitEnabled, superdeepCapturesOwnFaction, pitWidthBodySizeMultiplier,
//     PulseIntervalTicks, FlowPerPulse.
// Flood_FlowWorks.cs and RM_LiquidStock.cs are NOT touched or referenced by type here.
//
// THREAD AFFINITY: everything that touches the map lives inside ctx.MainThread.InvokeAsync.

using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using Verse;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        private const string FwTrapTypeName = "RimMandrake.FlowWorks.RM_SuperdeepTrap";
        private const string FwLadderTypeName = "RimMandrake.FlowWorks.RM_LadderUtility";
        private const int FwMaxPulses = 500;
        private const int FwMaxVectorCells = 4096;
        private const int FwMaxRectCells = 10000;

        /// <summary>mapId = -1 is the current map; anything else must match a live map's uniqueID.</summary>
        private static Map FwResolveMap(int mapId, out string error)
        {
            error = null;
            if (mapId < 0)
            {
                if (Find.CurrentMap == null) error = "No current map.";
                return Find.CurrentMap;
            }
            Map m = Find.Maps?.FirstOrDefault(x => x.uniqueID == mapId);
            if (m == null)
                error = "No map with uniqueID " + mapId + ". Live maps: "
                    + string.Join(", ", (Find.Maps ?? new List<Map>()).Select(x => x.uniqueID.ToString()));
            return m;
        }

        /// <summary>The cells a vector is reported over: a rect when w,h &gt; 0, else every cell in
        /// the component's RAW excavatedCells set. Sorted by cell index (the engine's tiebreak
        /// order) so vectors from two calls line up position by position.</summary>
        private static List<IntVec3> FwVectorCells(Map map, Type type, object comp, int x, int z, int w, int h,
            List<string> missing, out string error)
        {
            error = null;
            var cells = new List<IntVec3>();
            if (w > 0 || h > 0)
            {
                if (w <= 0 || h <= 0) { error = "rect needs BOTH w and h > 0 (got w=" + w + ", h=" + h + ")."; return null; }
                if ((long)w * h > FwMaxVectorCells) { error = "rect " + w + "x" + h + " exceeds " + FwMaxVectorCells + " cells."; return null; }
                for (int dz = 0; dz < h; dz++)
                    for (int dx = 0; dx < w; dx++)
                    {
                        var c = new IntVec3(x + dx, 0, z + dz);
                        if (!c.InBounds(map)) { error = "rect cell " + c + " is out of bounds (map " + map.Size.x + "x" + map.Size.z + ")."; return null; }
                        cells.Add(c);
                    }
            }
            else
            {
                if (!(FwField(type, comp, "excavatedCells", missing) is IEnumerable set)) return null;
                foreach (object o in set) cells.Add((IntVec3)o);
                if (cells.Count > FwMaxVectorCells)
                {
                    error = cells.Count + " excavated cells exceed the " + FwMaxVectorCells + "-cell vector cap - pass a rect.";
                    return null;
                }
            }
            CellIndices ci = map.cellIndices;
            cells.Sort((a, b) => ci.CellToIndex(a).CompareTo(ci.CellToIndex(b)));
            return cells;
        }

        private sealed class FwSnapshot
        {
            public int[] d, f;
            public bool[] src;
            public int sumF, rawFillAboveDepth;
            public float sink, overflow;
            public int nextPulseTick;
            public List<object> bodies;
        }

        /// <summary>RAW grid read: depthGrid/fillGrid as stored, NOT the DepthAt/FillAt getters
        /// (those read a natural source through as 4/4 and clamp F to D). src[] marks the source
        /// cells the getters would read as 4/4; rawFillAboveDepth counts cells whose stored F
        /// exceeds D (the getter would hide it - an engine anomaly, never expected).</summary>
        private static FwSnapshot FwSnap(Map map, Type type, object comp, List<IntVec3> cells, bool withBodies,
            List<string> missing)
        {
            var depth = FwField(type, comp, "depthGrid", missing) as byte[];
            var fill = FwField(type, comp, "fillGrid", missing) as byte[];
            object next = FwField(type, comp, "nextPulseTick", missing);
            MethodInfo isSrc = type.GetMethod("IsSourceCell", FwInst);
            if (isSrc == null) missing.Add("RM_MapComponent_Excavation.IsSourceCell");
            if (depth == null || fill == null || next == null || isSrc == null) return null;
            var s = new FwSnapshot { d = new int[cells.Count], f = new int[cells.Count], src = new bool[cells.Count] };
            CellIndices ci = map.cellIndices;
            for (int i = 0; i < cells.Count; i++)
            {
                int idx = ci.CellToIndex(cells[i]);
                s.d[i] = idx < depth.Length ? depth[idx] : -1;
                s.f[i] = idx < fill.Length ? fill[idx] : -1;
                if (s.d[i] == 0) s.src[i] = (bool)isSrc.Invoke(comp, new object[] { cells[i] });
                if (s.d[i] > 0) s.sumF += s.f[i];
                if (s.f[i] > s.d[i] && s.d[i] > 0) s.rawFillAboveDepth++;
            }
            s.sink = (float)type.GetProperty("SinkTransferredTotal").GetValue(comp);
            s.overflow = (float)type.GetProperty("OverflowDestroyedTotal").GetValue(comp);
            s.nextPulseTick = (int)next;
            if (withBodies)
            {
                IList bodies = FwBodies(comp, type, missing, out _);
                s.bodies = bodies == null ? null : bodies.Cast<object>().Select(FwBodyRecord).ToList();
            }
            return s;
        }

        private static object FwSnapRecord(int pulse, FwSnapshot s, FwSnapshot prev)
        {
            int changedD = 0, changedF = 0;
            if (prev != null)
                for (int i = 0; i < s.d.Length; i++)
                {
                    if (s.d[i] != prev.d[i]) changedD++;
                    if (s.f[i] != prev.f[i]) changedF++;
                }
            return new
            {
                pulse,
                fill = s.f,
                depth = s.d,
                sumFill = s.sumF,
                cellsFillChanged = changedF,
                cellsDepthChanged = changedD,
                rawFillAboveDepth = s.rawFillAboveDepth,
                sinkTransferredTotal = s.sink,
                overflowDestroyedTotal = s.overflow,
                bodies = s.bodies
            };
        }

        [Tool(
            "jawa/flowworks_pulse",
            Description =
                "Run the FlowWorks depth engine's pulse N times DIRECTLY, synchronously, at 0 game " +
                "ticks: invokes RM_MapComponent_Excavation's private DoPulse() by reflection - the " +
                "exact body the MapComponentTick scheduler calls (rain, then stock refill/recession " +
                "with dt = the clamped pulseIntervalTicks setting, then the flow solve). Returns the " +
                "RAW D/F vector over the chosen cells before pulse 1 (pulse 0) and after EVERY pulse. " +
                "Cells: a rect (x,z,w,h) or, with w=h=0, every cell in the engine's raw excavated set; " +
                "sorted by cell index, listed once in cells[] so vector position i is cells[i]. " +
                "🔴 It does NOT touch nextPulseTick, so an UNPAUSED game also keeps pulsing on its own " +
                "schedule between calls - pause first (gamePaused is reported). 🔴 REFUSES when " +
                "depthEngineEnabled is false (no scheduled pulse would fire either) unless " +
                "ignoreEngineToggle=true. A pulse that moves nothing is still a pulse that ran: " +
                "cellsFillChanged=0 is a settled reading, not a failure. An exception inside the " +
                "pulse fails the call with the inner exception and the vectors up to that point. " +
                "D and F are the stored grid bytes, not the DepthAt/FillAt getters: a natural source " +
                "cell reads D=0 F=0 here with isSource=true (the getters would say 4/4).",
            ResultDescription =
                "success, pulsesRequested, pulsesRun, mapId, cells[{x,z,isSourceAtStart}], " +
                "pulses[{pulse (0 = before), fill[], depth[], sumFill (excavated cells only), " +
                "cellsFillChanged, cellsDepthChanged, rawFillAboveDepth, sinkTransferredTotal, " +
                "overflowDestroyedTotal, bodies[] (when includeBodies)}], nextPulseTickBefore/After " +
                "(must be equal - proves the scheduler was not advanced), nextPulseTickUntouched, " +
                "pulseIntervalTicks, flowPerPulse, depthEngineEnabled, gamePaused, ticksBefore, " +
                "ticksGame (equal: 0 ticks spent).")]
        public static async Task<object> FlowWorksPulse(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "How many pulses to run, 1-500.", DefaultValue = 1)]
            int count = 1,
            [ToolParameter(Description = "Map uniqueID; -1 (default) = the current map.", DefaultValue = -1)]
            int mapId = -1,
            [ToolParameter(Description = "Rect min X of the reported cells (with w,h > 0).", DefaultValue = 0)]
            int x = 0,
            [ToolParameter(Description = "Rect min Z of the reported cells.", DefaultValue = 0)]
            int z = 0,
            [ToolParameter(Description = "Rect width; 0 with h=0 = every excavated cell (cap 4096).", DefaultValue = 0)]
            int w = 0,
            [ToolParameter(Description = "Rect height; 0 with w=0 = every excavated cell.", DefaultValue = 0)]
            int h = 0,
            [ToolParameter(Description = "Report every liquid body's stock/recededCount after each pulse.", DefaultValue = true)]
            bool includeBodies = true,
            [ToolParameter(Description = "Pulse even when the depthEngineEnabled setting is OFF.", DefaultValue = false)]
            bool ignoreEngineToggle = false)
        {
            if (count < 1 || count > FwMaxPulses)
                return Fail("count must be 1-" + FwMaxPulses + " (got " + count + "). Nothing was run.");
            return await ctx.MainThread.InvokeAsync(() =>
            {
                Map map = FwResolveMap(mapId, out string merr);
                if (map == null) return Fail(merr);
                object comp = ResolveExcavationComponent(map, out Type type, out string err);
                if (comp == null) return Fail(err);
                var missing = new List<string>();

                MethodInfo doPulse = type.GetMethod("DoPulse", FwInst, null, Type.EmptyTypes, null);
                if (doPulse == null)
                {
                    var near = type.GetMethods(FwInst).Where(m => m.Name.IndexOf("Pulse", StringComparison.OrdinalIgnoreCase) >= 0)
                        .Select(m => m.Name + "(" + string.Join(",", m.GetParameters().Select(p => p.ParameterType.Name)) + ")").ToList();
                    return Fail("RM_MapComponent_Excavation.DoPulse() (no parameters) not found by reflection - signature changed? Nothing was run.",
                        new { pulseLikeMethods = near });
                }

                Type settings = GenTypes.GetTypeInAnyAssembly(FwSettingsTypeName);
                if (settings == null) return Fail(FwSettingsTypeName + " not resolvable.");
                object enabledObj = settings.GetField("depthEngineEnabled", FwStatic)?.GetValue(null);
                object intervalObj = settings.GetProperty("PulseIntervalTicks", FwStatic)?.GetValue(null);
                object flowObj = settings.GetProperty("FlowPerPulse", FwStatic)?.GetValue(null);
                if (enabledObj == null || intervalObj == null)
                    return Fail("RimMandrakeFlowWorksSettings.depthEngineEnabled / PulseIntervalTicks not found by reflection.");
                bool enabled = (bool)enabledObj;
                if (!enabled && !ignoreEngineToggle)
                    return Fail("REFUSED: depthEngineEnabled is OFF, so no scheduled pulse would fire. Nothing was run. "
                        + "Pass ignoreEngineToggle=true to pulse anyway.", new { refused = true, depthEngineEnabled = false });

                List<IntVec3> cells = FwVectorCells(map, type, comp, x, z, w, h, missing, out string cerr);
                if (cells == null)
                    return Fail(cerr ?? ("FlowWorks members not found by reflection: " + string.Join(", ", missing)));

                int ticksBefore = TicksGameSafe();
                FwSnapshot prev = FwSnap(map, type, comp, cells, includeBodies, missing);
                if (prev == null || missing.Count > 0)
                    return Fail("FlowWorks members not found by reflection: " + string.Join(", ", missing));
                int nextBefore = prev.nextPulseTick;
                var cellRows = cells.Select((c, i) => (object)new { x = c.x, z = c.z, isSourceAtStart = prev.src[i] }).ToList();
                var pulses = new List<object> { FwSnapRecord(0, prev, null) };

                int run = 0;
                for (int p = 1; p <= count; p++)
                {
                    try
                    {
                        doPulse.Invoke(comp, null);
                    }
                    catch (TargetInvocationException tie)
                    {
                        Exception inner = tie.InnerException ?? tie;
                        return Fail("DoPulse threw on pulse " + p + " of " + count + ": " + inner.GetType().Name + ": " + inner.Message,
                            new { pulsesRun = run, cells = cellRows, pulses, stack = inner.StackTrace });
                    }
                    run++;
                    FwSnapshot s = FwSnap(map, type, comp, cells, includeBodies, missing);
                    if (s == null) return Fail("Read-back after pulse " + p + " failed: " + string.Join(", ", missing),
                        new { pulsesRun = run, cells = cellRows, pulses });
                    pulses.Add(FwSnapRecord(p, s, prev));
                    prev = s;
                }

                int ticksAfter = TicksGameSafe();
                return (object)new
                {
                    success = true,
                    pulsesRequested = count,
                    pulsesRun = run,
                    mapId = map.uniqueID,
                    cellCount = cells.Count,
                    cells = cellRows,
                    pulses,
                    nextPulseTickBefore = nextBefore,
                    nextPulseTickAfter = prev.nextPulseTick,
                    nextPulseTickUntouched = nextBefore == prev.nextPulseTick,
                    pulseIntervalTicks = (int)intervalObj,
                    flowPerPulse = flowObj,
                    depthEngineEnabled = enabled,
                    gamePaused = Find.TickManager?.Paused,
                    ticksBefore,
                    ticksGame = ticksAfter
                };
            });
        }

        [Tool(
            "jawa/flowworks_excavation_rect",
            Description =
                "Read-only: FlowWorks D/F state for EVERY cell of a rect on one map in a single call " +
                "(the per-cell flowworks_excavation_report, batched). Per cell: d and f are the RAW " +
                "stored grid bytes; dEff/fEff are what the DepthAt/FillAt getters return (a natural " +
                "source reads through as 4/4, F is clamped to D) - both are reported so a disagreement " +
                "is visible; isExcavated, isSource, isSink, terrain (top terrain defName; omit with " +
                "includeTerrain=false). onlyNonZero=true drops cells with d=0, f=0 and not a source " +
                "(the dry ring a never_liquid_on_open_ground check needs is then INVISIBLE - keep it " +
                "false for that). Cap 10000 cells. Never mutates anything.",
            ResultDescription =
                "success, mapId, rect{x,z,w,h}, cellCount (rows returned), cellsScanned, " +
                "rows[{x,z,d,f,dEff,fEff,isExcavated,isSource,isSink,terrain}], sumFill (raw F over " +
                "excavated rows), excavatedInRect, sourceInRect, sinkInRect, getterDisagreements " +
                "(excavated rows where dEff/fEff differ from raw - F above D), excavatedCellCount " +
                "(map), sinkTransferredTotal, overflowDestroyedTotal, ticksGame.")]
        public static async Task<object> FlowWorksExcavationRect(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Rect min X.")] int x,
            [ToolParameter(Description = "Rect min Z.")] int z,
            [ToolParameter(Description = "Rect width (>= 1).")] int w,
            [ToolParameter(Description = "Rect height (>= 1).")] int h,
            [ToolParameter(Description = "Map uniqueID; -1 (default) = the current map.", DefaultValue = -1)]
            int mapId = -1,
            [ToolParameter(Description = "Drop rows that are undug, empty and not a source.", DefaultValue = false)]
            bool onlyNonZero = false,
            [ToolParameter(Description = "Include each cell's terrain defName.", DefaultValue = true)]
            bool includeTerrain = true)
        {
            if (w < 1 || h < 1) return Fail("w and h must both be >= 1 (got " + w + "x" + h + ").");
            if ((long)w * h > FwMaxRectCells) return Fail("rect " + w + "x" + h + " exceeds the " + FwMaxRectCells + "-cell cap.");
            return await ctx.MainThread.InvokeAsync(() =>
            {
                Map map = FwResolveMap(mapId, out string merr);
                if (map == null) return Fail(merr);
                var lo = new IntVec3(x, 0, z);
                var hi = new IntVec3(x + w - 1, 0, z + h - 1);
                if (!lo.InBounds(map) || !hi.InBounds(map))
                    return Fail("rect " + lo + ".." + hi + " is not inside map " + map.uniqueID
                        + " (size " + map.Size.x + "x" + map.Size.z + "). Nothing was read.");
                object comp = ResolveExcavationComponent(map, out Type type, out string err);
                if (comp == null) return Fail(err);
                var missing = new List<string>();
                var depth = FwField(type, comp, "depthGrid", missing) as byte[];
                var fill = FwField(type, comp, "fillGrid", missing) as byte[];
                MethodInfo mD = type.GetMethod("DepthAt", FwInst), mF = type.GetMethod("FillAt", FwInst),
                    mSrc = type.GetMethod("IsSourceCell", FwInst), mSink = type.GetMethod("IsSinkCell", FwInst);
                if (mD == null || mF == null || mSrc == null || mSink == null) missing.Add("DepthAt/FillAt/IsSourceCell/IsSinkCell");
                if (depth == null || fill == null || missing.Count > 0)
                    return Fail("FlowWorks members not found by reflection: " + string.Join(", ", missing));

                var rows = new List<object>();
                int scanned = 0, sumFill = 0, exc = 0, srcN = 0, sinkN = 0, disagree = 0;
                CellIndices ci = map.cellIndices;
                for (int dz = 0; dz < h; dz++)
                    for (int dx = 0; dx < w; dx++)
                    {
                        var c = new IntVec3(x + dx, 0, z + dz);
                        object[] a = { c };
                        int idx = ci.CellToIndex(c);
                        int d = depth[idx], f = fill[idx];
                        int dEff = (byte)mD.Invoke(comp, a), fEff = (byte)mF.Invoke(comp, a);
                        bool isSrc = (bool)mSrc.Invoke(comp, a), isSink = (bool)mSink.Invoke(comp, a);
                        scanned++;
                        if (d > 0) { exc++; sumFill += f; if (dEff != d || fEff != f) disagree++; }
                        if (isSrc) srcN++;
                        if (isSink) sinkN++;
                        if (onlyNonZero && d == 0 && f == 0 && !isSrc) continue;
                        rows.Add(new
                        {
                            x = c.x, z = c.z, d, f, dEff, fEff,
                            isExcavated = d > 0, isSource = isSrc, isSink,
                            terrain = includeTerrain ? c.GetTerrain(map)?.defName : null
                        });
                    }
                return (object)new
                {
                    success = true,
                    mapId = map.uniqueID,
                    rect = new { x, z, w, h },
                    cellCount = rows.Count,
                    cellsScanned = scanned,
                    rows,
                    sumFill,
                    excavatedInRect = exc,
                    sourceInRect = srcN,
                    sinkInRect = sinkN,
                    getterDisagreements = disagree,
                    excavatedCellCount = (int)type.GetProperty("ExcavatedCellCount").GetValue(comp),
                    sinkTransferredTotal = (float)type.GetProperty("SinkTransferredTotal").GetValue(comp),
                    overflowDestroyedTotal = (float)type.GetProperty("OverflowDestroyedTotal").GetValue(comp),
                    ticksGame = TicksGameSafe()
                };
            });
        }

        [Tool(
            "jawa/flowworks_pit_report",
            Description =
                "Read-only: a pit as the GRID sees it (SUPERDEEP_HOLDER_RETIRE_1 - a pit is a canal " +
                "cell dug to D=4; there is no holder Thing). Reports the cell's dug depth and fill, " +
                "the widest square pit containing it, ladder, room, every pawn standing on it with " +
                "the trap rule's inputs and verdict (BodySize, required width W, held, captured, " +
                "jumper) and REAL reachability through the game's own Reachability.CanReach / " +
                "CanReachMapEdge with the pawn's TraverseParms (so the trap veto patch is what is " +
                "measured): how many D<4 lip cells around the pawn's D=4 component it can reach. " +
                "legacyHolders lists any Thing on the cell named RM_SuperdeepPit or derived from " +
                "Building_OpenPit (must be empty after the retirement). Also the map's descent " +
                "counter and the last descents (pawn@cell tick fall damage).",
            ResultDescription =
                "success, cell, mapId, depthRaw, fillRaw, isSuperdeep, pitWidth, hasLadder, hasSpikes " +
                "(null: no spikes def yet), room{id, role, isPrisonCell, cellCount, touchesMapEdge}, " +
                "pawns[{id, def, spawned, dead, downed, faction, bodySize, requiredWidth, captured, " +
                "jumper, held, lipCells, lipReachable, canReachMapEdge}], legacyHolders[{id, def, type}], " +
                "descentCount, recentDescents[], settings{superdeepCaptureEnabled, " +
                "ladderRequiredToExitEnabled, superdeepCapturesOwnFaction, pitWidthBodySizeMultiplier}, ticksGame.")]
        public static async Task<object> FlowWorksPitReport(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Map cell X.")] int x,
            [ToolParameter(Description = "Map cell Z.")] int z,
            [ToolParameter(Description = "Map uniqueID; -1 (default) = the current map.", DefaultValue = -1)]
            int mapId = -1)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                Map map = FwResolveMap(mapId, out string merr);
                if (map == null) return Fail(merr);
                var c = new IntVec3(x, 0, z);
                if (!c.InBounds(map))
                    return Fail("Cell " + c + " is out of bounds on map " + map.uniqueID
                        + " (size " + map.Size.x + "x" + map.Size.z + ").");

                Type trap = GenTypes.GetTypeInAnyAssembly(FwTrapTypeName);
                Type ladder = GenTypes.GetTypeInAnyAssembly(FwLadderTypeName);
                Type settings = GenTypes.GetTypeInAnyAssembly(FwSettingsTypeName);
                var missing = new List<string>();
                MethodInfo hasLadder = ladder?.GetMethod("HasLadder", FwStatic, null, new[] { typeof(Map), typeof(IntVec3) }, null);
                MethodInfo isHeld = trap?.GetMethod("IsHeld", FwStatic, null, new[] { typeof(Pawn) }, null);
                MethodInfo captures = trap?.GetMethod("Captures", FwStatic, null, new[] { typeof(Pawn) }, null);
                MethodInfo reqW = trap?.GetMethod("RequiredWidth", FwStatic, null, new[] { typeof(Pawn) }, null);
                MethodInfo pitW = trap?.GetMethod("MeasuredPitWidth", FwStatic, null, new[] { typeof(Map), typeof(IntVec3) }, null);
                if (hasLadder == null) missing.Add(FwLadderTypeName + ".HasLadder(Map,IntVec3)");
                if (isHeld == null) missing.Add(FwTrapTypeName + ".IsHeld(Pawn)");
                if (captures == null) missing.Add(FwTrapTypeName + ".Captures(Pawn)");
                if (reqW == null) missing.Add(FwTrapTypeName + ".RequiredWidth(Pawn)");
                if (pitW == null) missing.Add(FwTrapTypeName + ".MeasuredPitWidth(Map,IntVec3)");
                if (settings == null) missing.Add(FwSettingsTypeName);
                object comp = ResolveExcavationComponent(map, out Type type, out string cerr);
                if (comp == null) missing.Add("RM_MapComponent_Excavation (" + cerr + ")");
                if (missing.Count > 0) return Fail("FlowWorks members not found by reflection: " + string.Join(", ", missing));

                int ci = map.cellIndices.CellToIndex(c);
                byte[] dg = FwField(type, comp, "depthGrid", missing) as byte[];
                byte[] fg = FwField(type, comp, "fillGrid", missing) as byte[];
                object state = type.GetProperty("SuperdeepTrap", FwInst)?.GetValue(comp);
                if (dg == null || fg == null || state == null)
                    return Fail("Engine members not found by reflection: " + string.Join(", ", missing)
                        + (state == null ? " SuperdeepTrap" : ""));
                Func<IntVec3, bool> d4 = q => q.InBounds(map) && dg[map.cellIndices.CellToIndex(q)] >= 4;
                bool ladderHere = (bool)hasLadder.Invoke(null, new object[] { map, c });

                // The pawn's D=4 component (8-connected) and its lip: standable D<4 cells touching it.
                var comp4 = new HashSet<IntVec3>();
                var lip = new List<IntVec3>();
                if (d4(c))
                {
                    var q = new Queue<IntVec3>();
                    q.Enqueue(c); comp4.Add(c);
                    while (q.Count > 0 && comp4.Count < 4000)
                    {
                        IntVec3 cur = q.Dequeue();
                        for (int i = 0; i < 8; i++)
                        {
                            IntVec3 n = cur + GenAdj.AdjacentCells[i];
                            if (!n.InBounds(map)) continue;
                            if (d4(n)) { if (comp4.Add(n)) q.Enqueue(n); }
                            else if (n.Standable(map) && !lip.Contains(n)) lip.Add(n);
                        }
                    }
                }

                var pawns = new List<object>();
                foreach (Thing t in c.GetThingList(map).ToList())
                {
                    if (!(t is Pawn p)) continue;
                    int reach = 0;
                    if (p.Spawned)
                    {
                        TraverseParms tp = TraverseParms.For(p, Danger.Deadly, TraverseMode.ByPawn);
                        foreach (IntVec3 l in lip)
                            if (map.reachability.CanReach(p.Position, l, Verse.AI.PathEndMode.OnCell, tp)) reach++;
                    }
                    pawns.Add(new
                    {
                        id = p.ThingID,
                        def = p.def?.defName,
                        spawned = p.Spawned,
                        dead = p.Dead,
                        downed = p.Downed,
                        faction = p.Faction?.Name,
                        bodySize = p.BodySize,
                        requiredWidth = (int)reqW.Invoke(null, new object[] { p }),
                        captured = (bool)captures.Invoke(null, new object[] { p }),
                        jumper = (bool)(state.GetType().GetMethod("IsJumper", FwInst)?.Invoke(state, new object[] { p }) ?? false),
                        held = (bool)isHeld.Invoke(null, new object[] { p }),
                        lipCells = lip.Count,
                        lipReachable = reach,
                        canReachMapEdge = p.Spawned && map.reachability.CanReachMapEdge(p.Position,
                            TraverseParms.For(p, Danger.Deadly, TraverseMode.ByPawn))
                    });
                }

                var legacy = new List<object>();
                foreach (Thing t in c.GetThingList(map))
                {
                    bool isLegacy = t.def?.defName == "RM_SuperdeepPit";
                    for (Type bt = t.GetType(); bt != null && !isLegacy; bt = bt.BaseType)
                        if (bt.Name == "Building_OpenPit") isLegacy = true;
                    if (isLegacy) legacy.Add(new { id = t.ThingID, def = t.def?.defName, type = t.GetType().FullName });
                }

                Room room = c.GetRoom(map);
                var recent = state.GetType().GetField("RecentDescents", FwInst)?.GetValue(state) as List<string>;
                return (object)new
                {
                    success = true,
                    cell = new { x, z },
                    mapId = map.uniqueID,
                    depthRaw = (int)dg[ci],
                    fillRaw = (int)fg[ci],
                    isSuperdeep = dg[ci] >= 4,
                    pitWidth = (int)pitW.Invoke(null, new object[] { map, c }),
                    hasLadder = ladderHere,
                    hasSpikes = (object)null,
                    room = room == null ? null : new
                    {
                        id = room.ID,
                        role = room.Role?.defName,
                        isPrisonCell = room.IsPrisonCell,
                        cellCount = room.CellCount,
                        touchesMapEdge = room.TouchesMapEdge
                    },
                    pawns,
                    legacyHolders = legacy,
                    descentCount = state.GetType().GetField("DescentCount", FwInst)?.GetValue(state),
                    recentDescents = recent == null ? new List<string>() : recent.ToList(),
                    settings = new
                    {
                        superdeepCaptureEnabled = settings.GetField("superdeepCaptureEnabled", FwStatic)?.GetValue(null),
                        ladderRequiredToExitEnabled = settings.GetField("ladderRequiredToExitEnabled", FwStatic)?.GetValue(null),
                        superdeepCapturesOwnFaction = settings.GetField("superdeepCapturesOwnFaction", FwStatic)?.GetValue(null),
                        pitWidthBodySizeMultiplier = settings.GetField("pitWidthBodySizeMultiplier", FwStatic)?.GetValue(null)
                    },
                    ticksGame = TicksGameSafe()
                };
            });
        }
    }
}
