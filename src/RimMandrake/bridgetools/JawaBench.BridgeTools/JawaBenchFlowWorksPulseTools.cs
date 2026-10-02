// JawaBenchFlowWorksPulseTools.cs - the FlowWorks Northstar v2 owed tools
// (design/RimMandrake/flowworks_northstar_script_plan_2026-10-02.md section 8, items 1-3):
//
//   flowworks_pulse            run the depth engine's pulse N times DIRECTLY, 0 game ticks,
//                              returning the D/F vector after every pulse (owed tool 2)
//   flowworks_excavation_rect  D/F/source/sink/terrain for every cell of a rect in ONE call
//                              (owed tool 1; replaces ~80% of per-cell report polls, R10)
//   flowworks_pit_report       the SUPERDEEP holder at a cell: innerContainer, EscapeBlocked,
//                              EscapeAssisted, HasLadder (owed tool 3; replaces the
//                              "absent from list_pawns" proxy in S7)
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
//   RM_SuperdeepCapture.HolderAt(Map, IntVec3) (static); RM_LadderUtility.HasLadder(Map, IntVec3).
//   Building_OpenPit: public innerContainer, covered, DepthTier, MaxOccupants; protected
//     virtual EscapeBlocked / EscapeAssisted (overridden by Building_SuperdeepPit).
//   RimMandrakeFlowWorksSettings: static depthEngineEnabled, superdeepCaptureEnabled,
//     ladderRequiredToExitEnabled, PulseIntervalTicks, FlowPerPulse.
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
        private const string FwCaptureTypeName = "RimMandrake.FlowWorks.RM_SuperdeepCapture";
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
                "Read-only: the SUPERDEEP holder (Building_SuperdeepPit, found by " +
                "RM_SuperdeepCapture.HolderAt) at one cell - what it HOLDS (innerContainer, the " +
                "direct proof a pawn was captured, instead of inferring it from the pawn being " +
                "absent/unspawned), EscapeBlocked and EscapeAssisted (protected overrides, read by " +
                "reflection on the runtime type: blocked = ladderRequiredToExitEnabled AND no " +
                "ladder), HasLadder (RM_LadderUtility), depth tier, cover, and the cell's raw D. " +
                "holderPresent=false is a real reading (no holder at that cell; expected anywhere " +
                "D != 4 or with superdeepCaptureEnabled OFF), not a failure. Also lists every OTHER " +
                "Building_OpenPit-family Thing on the cell so a legacy building pit is not mistaken " +
                "for the holder.",
            ResultDescription =
                "success, cell, mapId, depthRaw, holderPresent, holder{id, def, spawned, " +
                "occupantCount, maxOccupants, occupants[{id, def, isPawn, dead, faction, " +
                "holdingOwnerIsThisPit}], escapeBlocked, escapeAssisted, depthTier, covered, " +
                "coverTier} or null, hasLadder, otherPits[{id, def, type}], settings" +
                "{superdeepCaptureEnabled, ladderRequiredToExitEnabled}, ticksGame.")]
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

                Type capture = GenTypes.GetTypeInAnyAssembly(FwCaptureTypeName);
                Type ladder = GenTypes.GetTypeInAnyAssembly(FwLadderTypeName);
                Type settings = GenTypes.GetTypeInAnyAssembly(FwSettingsTypeName);
                MethodInfo holderAt = capture?.GetMethod("HolderAt", FwStatic, null, new[] { typeof(Map), typeof(IntVec3) }, null);
                MethodInfo hasLadder = ladder?.GetMethod("HasLadder", FwStatic, null, new[] { typeof(Map), typeof(IntVec3) }, null);
                var missing = new List<string>();
                if (holderAt == null) missing.Add(FwCaptureTypeName + ".HolderAt(Map,IntVec3)");
                if (hasLadder == null) missing.Add(FwLadderTypeName + ".HasLadder(Map,IntVec3)");
                if (settings == null) missing.Add(FwSettingsTypeName);
                if (missing.Count > 0) return Fail("FlowWorks members not found by reflection: " + string.Join(", ", missing));

                int depthRaw = -1;
                object comp = ResolveExcavationComponent(map, out Type type, out _);
                if (comp != null && FwField(type, comp, "depthGrid", missing) is byte[] dg)
                    depthRaw = dg[map.cellIndices.CellToIndex(c)];

                Thing holder = holderAt.Invoke(null, new object[] { map, c }) as Thing;
                bool ladderHere = (bool)hasLadder.Invoke(null, new object[] { map, c });

                object holderRec = null;
                if (holder != null)
                {
                    Type ht = holder.GetType();
                    var owner = ht.GetField("innerContainer", FwInst)?.GetValue(holder) as ThingOwner;
                    PropertyInfo pBlocked = ht.GetProperty("EscapeBlocked", FwInst);
                    PropertyInfo pAssisted = ht.GetProperty("EscapeAssisted", FwInst);
                    if (owner == null) missing.Add(ht.Name + ".innerContainer");
                    if (pBlocked == null) missing.Add(ht.Name + ".EscapeBlocked");
                    if (pAssisted == null) missing.Add(ht.Name + ".EscapeAssisted");
                    if (missing.Count > 0) return Fail("Holder members not found by reflection: " + string.Join(", ", missing));
                    var occupants = new List<object>();
                    for (int i = 0; i < owner.Count; i++)
                    {
                        Thing t = owner[i];
                        occupants.Add(new
                        {
                            id = t.ThingID,
                            def = t.def?.defName,
                            isPawn = t is Pawn,
                            dead = (t as Pawn)?.Dead,
                            faction = t.Faction?.Name,
                            holdingOwnerIsThisPit = ReferenceEquals(t.holdingOwner, owner)
                        });
                    }
                    holderRec = new
                    {
                        id = holder.ThingID,
                        def = holder.def?.defName,
                        spawned = holder.Spawned,
                        occupantCount = owner.Count,
                        maxOccupants = ht.GetProperty("MaxOccupants", FwInst)?.GetValue(holder),
                        occupants,
                        escapeBlocked = (bool)pBlocked.GetValue(holder),
                        escapeAssisted = (bool)pAssisted.GetValue(holder),
                        depthTier = ht.GetField("DepthTier", FwInst)?.GetValue(holder)?.ToString(),
                        covered = ht.GetField("covered", FwInst)?.GetValue(holder),
                        coverTier = ht.GetField("CoverTier", FwInst)?.GetValue(holder)?.ToString()
                    };
                }

                var otherPits = new List<object>();
                foreach (Thing t in c.GetThingList(map))
                {
                    if (ReferenceEquals(t, holder)) continue;
                    for (Type bt = t.GetType(); bt != null; bt = bt.BaseType)
                        if (bt.Name == "Building_OpenPit")
                        {
                            otherPits.Add(new { id = t.ThingID, def = t.def?.defName, type = t.GetType().FullName });
                            break;
                        }
                }

                return (object)new
                {
                    success = true,
                    cell = new { x, z },
                    mapId = map.uniqueID,
                    depthRaw,
                    holderPresent = holder != null,
                    holder = holderRec,
                    hasLadder = ladderHere,
                    otherPits,
                    settings = new
                    {
                        superdeepCaptureEnabled = settings.GetField("superdeepCaptureEnabled", FwStatic)?.GetValue(null),
                        ladderRequiredToExitEnabled = settings.GetField("ladderRequiredToExitEnabled", FwStatic)?.GetValue(null)
                    },
                    ticksGame = TicksGameSafe()
                };
            });
        }
    }
}
