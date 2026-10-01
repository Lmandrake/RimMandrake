// JawaBenchFlowWorksNorthstarTools.cs - the FlowWorks north-star trial's engine reads
// and the ActiveFluid setter (FLOWWORKS_BRIDGE_TOOLS_1; plan
// design/RimMandrake/northstar_trials/FlowWorks_trial_plan.md section 6 items 3, 11, 12).
//
// Callers: FlowWorks/northstar/prep_site.py (step 6 classifies every golden body),
// FlowWorks/northstar/preflight_flowworks.py (P-S2 body records, P-E7 pulse clock),
// FlowWorks/validation.py (plots C2 and F set the fluid before first classification).
// The response shapes are the CONTRACT in FlowWorks/northstar/site_spec.py NEEDED_TOOLS,
// which FlowWorks/northstar/fakegame.py implements offline.
//
// COUPLING: strictly by reflection, like JawaBenchFlowWorksTools.cs - the companion must
// register on a mod list WITHOUT FlowWorks, so every resolve failure is a loud Fail
// naming what was missing. EVERY member read from src/RimMandrake/FlowWorks/Source:
//   RM_MapComponent_Excavation: private activeFluid / nextPulseTick / rainAccumulator /
//     fillGrid; public Stock, ActiveFluid (lazy getter defaults to water - so the RAW
//     field is read, never the getter), ExcavatedCellCount, SuperdeepCellCount,
//     SinkTransferredTotal, OverflowDestroyedTotal.
//   RM_LiquidStock: public Bodies, BodyAt(Map, IntVec3, RM_MapComponent_Excavation).
//   RM_LiquidBody: public id, limitless, stock, capacity, cells, receded, truncated.
//   RimMandrakeFlowWorksSettings: static depthEngineEnabled, PulseIntervalTicks.
//   RimMandrakeFlowWorks_DefOf.RM_Fluid_Water.
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
        private const string FwSettingsTypeName = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings";
        private const string FwDefOfTypeName = "RimMandrake.FlowWorks.RimMandrakeFlowWorks_DefOf";
        private const string FwBodyTypeName = "RimMandrake.FlowWorks.RM_LiquidBody";

        private const BindingFlags FwInst = BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic;
        private const BindingFlags FwStatic = BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic;

        /// <summary>A private/public instance field of the excavation component, or a loud error.</summary>
        private static object FwField(Type type, object comp, string name, List<string> missing)
        {
            FieldInfo f = type.GetField(name, FwInst);
            if (f == null) { missing.Add(type.Name + "." + name); return null; }
            return f.GetValue(comp);
        }

        /// <summary>The RAW activeFluid field (null until something reads the lazy getter or a
        /// save carries one) plus what the getter WOULD return, computed without calling it.</summary>
        private static void FwActiveFluid(Type type, object comp, List<string> missing,
            out string raw, out string effective)
        {
            object v = FwField(type, comp, "activeFluid", missing);
            raw = (v as Def)?.defName;
            if (raw != null) { effective = raw; return; }
            Type defOf = GenTypes.GetTypeInAnyAssembly(FwDefOfTypeName);
            object water = defOf?.GetField("RM_Fluid_Water", FwStatic)?.GetValue(null);
            effective = (water as Def)?.defName;
            if (defOf == null) missing.Add(FwDefOfTypeName);
        }

        private static IList FwBodies(object comp, Type type, List<string> missing, out object stock)
        {
            stock = type.GetProperty("Stock", FwInst)?.GetValue(comp);
            if (stock == null) { missing.Add("RM_MapComponent_Excavation.Stock"); return null; }
            object bodies = stock.GetType().GetProperty("Bodies", FwInst)?.GetValue(stock);
            if (bodies == null) { missing.Add("RM_LiquidStock.Bodies"); return null; }
            return bodies as IList ?? ((IEnumerable)bodies).Cast<object>().ToList();
        }

        /// <summary>Independent of the stock's private cell index: walk every body's footprint.</summary>
        private static object FwBodyContaining(IList bodies, IntVec3 c)
        {
            if (bodies == null) return null;
            foreach (object b in bodies)
            {
                if (b?.GetType().GetField("cells", FwInst)?.GetValue(b) is List<IntVec3> cells && cells.Contains(c))
                    return b;
            }
            return null;
        }

        private static object FwBodyRecord(object b)
        {
            if (b == null) return null;
            Type t = b.GetType();
            var cells = t.GetField("cells", FwInst)?.GetValue(b) as List<IntVec3>;
            var receded = t.GetField("receded", FwInst)?.GetValue(b) as List<IntVec3>;
            return new
            {
                id = (int)t.GetField("id", FwInst).GetValue(b),
                limitless = (bool)t.GetField("limitless", FwInst).GetValue(b),
                stock = (float)t.GetField("stock", FwInst).GetValue(b),
                capacity = (float)t.GetField("capacity", FwInst).GetValue(b),
                cellCount = cells?.Count ?? -1,
                recededCount = receded?.Count ?? -1,
                activeCellCount = (cells?.Count ?? 0) - (receded?.Count ?? 0),
                truncated = (bool)t.GetField("truncated", FwInst).GetValue(b)
            };
        }

        [Tool(
            "jawa/flowworks_body_report",
            Description =
                "Read the RM_LiquidBody (natural liquid body: stock, capacity, limitless, footprint) " +
                "owning one cell on the CURRENT map. 🔴 WITH classify=true (the default) THIS CALL " +
                "CLASSIFIES: it calls RM_LiquidStock.BodyAt, which forms the body by flood fill on " +
                "first contact and makes it STICKY for the life of the map (ruling 16) - the body's " +
                "capacity is computed from the map's ActiveFluid AT THAT MOMENT, so set the fluid " +
                "first (flowworks_set_active_fluid). classify=false is a pure read that never forms a " +
                "body. The body is read back by walking every body's footprint, independently of the " +
                "stock's private cell index; indexAgrees=false means the two disagree. A cell that is " +
                "not natural liquid terrain returns classified=false, body=null (not a failure). " +
                "cellCount is the footprint AS CLASSIFIED (receded cells stay in it); activeCellCount " +
                "subtracts recededCount.",
            ResultDescription =
                "success, cell, classified (a body owns this cell after the call), formedByThisCall, " +
                "indexAgrees, isSourceCell, body{id, limitless, stock, capacity, cellCount, " +
                "recededCount, activeCellCount, truncated} or null, bodyCount, activeFluid (effective), " +
                "activeFluidRaw (null = never set, getter defaults to water), ticksGame.")]
        public static async Task<object> FlowWorksBodyReport(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Map cell X of any cell of the body (e.g. the pond's centre).")] int x,
            [ToolParameter(Description = "Map cell Z of any cell of the body.")] int z,
            [ToolParameter(Description =
                "true (default) = call BodyAt, which FORMS and permanently classifies the body if it " +
                "has never been touched. false = read only; an untouched body reports classified=false.",
                DefaultValue = true)]
            bool classify = true)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                Map map = Find.CurrentMap;
                if (map == null) return Fail("No current map.");
                IntVec3 c = new IntVec3(x, 0, z);
                if (!c.InBounds(map))
                    return Fail("Cell " + c + " is out of bounds on map " + map.uniqueID
                        + " (size " + map.Size.x + "x" + map.Size.z + ").");

                object comp = ResolveExcavationComponent(map, out Type type, out string err);
                if (comp == null) return Fail(err);
                var missing = new List<string>();

                IList bodies = FwBodies(comp, type, missing, out object stock);
                if (bodies == null) return Fail("Could not reach the liquid stock.", new { missing });
                int before = bodies.Count;
                bool isSource = (bool)type.GetMethod("IsSourceCell").Invoke(comp, new object[] { c });

                object viaIndex = null;
                if (classify)
                {
                    MethodInfo bodyAt = stock.GetType().GetMethod("BodyAt", FwInst);
                    if (bodyAt == null) return Fail("RM_LiquidStock.BodyAt not found by reflection - signature changed?");
                    viaIndex = bodyAt.Invoke(stock, new object[] { map, c, comp });
                }

                bodies = FwBodies(comp, type, missing, out _);
                object found = FwBodyContaining(bodies, c);
                bool indexAgrees = !classify || ReferenceEquals(viaIndex, found);
                FwActiveFluid(type, comp, missing, out string raw, out string effective);
                if (missing.Count > 0)
                    return Fail("FlowWorks members not found by reflection: " + string.Join(", ", missing));

                return (object)new
                {
                    success = true,
                    cell = new { x, z },
                    classified = found != null,
                    formedByThisCall = bodies.Count > before,
                    indexAgrees,
                    isSourceCell = isSource,
                    body = FwBodyRecord(found),
                    bodyCount = bodies.Count,
                    activeFluid = effective,
                    activeFluidRaw = raw,
                    ticksGame = TicksGameSafe()
                };
            });
        }

        [Tool(
            "jawa/flowworks_engine_state",
            Description =
                "Read-only snapshot of the CURRENT map's FlowWorks depth engine, from the raw private " +
                "fields: nextPulseTick (the pulse fires on the first tick >= it; -1 = never pulsed, so " +
                "the very next tick pulses), pulseIntervalTicks (the clamped effective interval the " +
                "engine adds, not the raw slider), depthEngineEnabled (when false no pulse ever fires " +
                "and nextPulseTick is frozen), activeFluid raw vs effective (the getter lazily writes " +
                "water, so it is NOT called), rainAccumulator (fractional rain carried between " +
                "pulses), and the map-wide counters. Never mutates anything.",
            ResultDescription =
                "success, nextPulseTick, ticksUntilNextPulse, pulseIntervalTicks, depthEngineEnabled, " +
                "activeFluid, activeFluidRaw, rainAccumulator, excavatedCellCount, superdeepCellCount, " +
                "bodyCount, sinkTransferredTotal, overflowDestroyedTotal, mapId, ticksGame.")]
        public static async Task<object> FlowWorksEngineState(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                Map map = Find.CurrentMap;
                if (map == null) return Fail("No current map.");
                object comp = ResolveExcavationComponent(map, out Type type, out string err);
                if (comp == null) return Fail(err);
                var missing = new List<string>();

                Type settings = GenTypes.GetTypeInAnyAssembly(FwSettingsTypeName);
                if (settings == null) return Fail(FwSettingsTypeName + " not resolvable.");
                object pulse = settings.GetProperty("PulseIntervalTicks", FwStatic)?.GetValue(null);
                object enabled = settings.GetField("depthEngineEnabled", FwStatic)?.GetValue(null);
                if (pulse == null) missing.Add("RimMandrakeFlowWorksSettings.PulseIntervalTicks");
                if (enabled == null) missing.Add("RimMandrakeFlowWorksSettings.depthEngineEnabled");

                object next = FwField(type, comp, "nextPulseTick", missing);
                object rain = FwField(type, comp, "rainAccumulator", missing);
                FwActiveFluid(type, comp, missing, out string raw, out string effective);
                IList bodies = FwBodies(comp, type, missing, out _);
                if (missing.Count > 0)
                    return Fail("FlowWorks members not found by reflection: " + string.Join(", ", missing));

                int now = TicksGameSafe();
                int nextTick = (int)next;
                return (object)new
                {
                    success = true,
                    nextPulseTick = nextTick,
                    ticksUntilNextPulse = Math.Max(0, nextTick - now),
                    pulseIntervalTicks = (int)pulse,
                    depthEngineEnabled = (bool)enabled,
                    activeFluid = effective,
                    activeFluidRaw = raw,
                    rainAccumulator = (float)rain,
                    excavatedCellCount = (int)type.GetProperty("ExcavatedCellCount").GetValue(comp),
                    superdeepCellCount = (int)type.GetProperty("SuperdeepCellCount").GetValue(comp),
                    bodyCount = bodies.Count,
                    sinkTransferredTotal = (float)type.GetProperty("SinkTransferredTotal").GetValue(comp),
                    overflowDestroyedTotal = (float)type.GetProperty("OverflowDestroyedTotal").GetValue(comp),
                    mapId = map.uniqueID,
                    ticksGame = now
                };
            });
        }

        [Tool(
            "jawa/flowworks_set_active_fluid",
            Description =
                "Set the CURRENT map's FlowWorks ActiveFluid (ONE FluidDef per map - there is no " +
                "per-body or per-cell fluid, so two fluids can never share a map) and read the raw " +
                "field back. 🔴 MUST RUN BEFORE FIRST CLASSIFICATION: a body's capacity is computed " +
                "from the fluid when it forms and is sticky, and a filled cell's terrain is the fluid " +
                "that filled it. So this REFUSES when any liquid body is already classified or any " +
                "cell holds fill (F > 0), naming the counts - use a fresh working copy of the save. " +
                "allowAfterClassification=true overrides the refusal (e.g. to put a shared map back " +
                "to water afterwards); it does NOT re-classify bodies or repaint existing fill " +
                "terrain, which keep the old fluid until the next fill write. Saved with the map " +
                "(Scribe RM_activeFluid).",
            ResultDescription =
                "success, fluidBefore (raw; null = never set), fluidAfter (raw field read back), " +
                "readBackMatches, bodiesClassified, filledCells, refused (on failure: details carries " +
                "the counts), mapId, ticksGame. On an unknown defName, details.known lists every FluidDef.")]
        public static async Task<object> FlowWorksSetActiveFluid(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "FluidDef defName, e.g. RM_Fluid_Water, RM_Fluid_Tar, RM_Fluid_SlimeGreen.")]
            string fluidDefName,
            [ToolParameter(Description =
                "false (default) = refuse when a body is classified or any cell holds fill. " +
                "true = set anyway; existing bodies and fill terrain keep the old fluid.",
                DefaultValue = false)]
            bool allowAfterClassification = false)
        {
            if (string.IsNullOrWhiteSpace(fluidDefName)) return Fail("fluidDefName is required.");
            return await ctx.MainThread.InvokeAsync(() =>
            {
                Map map = Find.CurrentMap;
                if (map == null) return Fail("No current map.");
                object comp = ResolveExcavationComponent(map, out Type type, out string err);
                if (comp == null) return Fail(err);

                Type fluidDefType = GenTypes.GetTypeInAnyAssembly(FluidDefTypeName);
                if (fluidDefType == null) return Fail(FluidDefTypeName + " not resolvable - FlowWorks is not loaded.");
                Type dbType = typeof(DefDatabase<>).MakeGenericType(fluidDefType);
                object def = dbType.GetMethod("GetNamedSilentFail", new[] { typeof(string) })
                    .Invoke(null, new object[] { fluidDefName.Trim() });
                if (def == null)
                {
                    var known = ((IEnumerable)dbType.GetProperty("AllDefs").GetValue(null))
                        .Cast<Def>().Select(d => d.defName).OrderBy(n => n).ToList();
                    return Fail("No FluidDef named '" + fluidDefName + "'.", new { known });
                }

                var missing = new List<string>();
                IList bodies = FwBodies(comp, type, missing, out _);
                byte[] fillGrid = FwField(type, comp, "fillGrid", missing) as byte[];
                FwActiveFluid(type, comp, missing, out string rawBefore, out _);
                if (missing.Count > 0 || fillGrid == null)
                    return Fail("FlowWorks members not found by reflection: " + string.Join(", ", missing));
                int filled = 0;
                for (int i = 0; i < fillGrid.Length; i++) if (fillGrid[i] > 0) filled++;
                int classifiedCount = bodies.Count;

                if (!allowAfterClassification && (classifiedCount > 0 || filled > 0))
                    return Fail("REFUSED: ActiveFluid must be set before first classification - "
                        + classifiedCount + " liquid body(ies) already classified, " + filled
                        + " cell(s) hold fill. Nothing was changed. Use a fresh working copy, or pass "
                        + "allowAfterClassification=true knowingly.",
                        new { refused = true, bodiesClassified = classifiedCount, filledCells = filled, fluidBefore = rawBefore });

                PropertyInfo prop = type.GetProperty("ActiveFluid", FwInst);
                if (prop == null || !prop.CanWrite) return Fail("RM_MapComponent_Excavation.ActiveFluid setter not found.");
                prop.SetValue(comp, def);

                FwActiveFluid(type, comp, missing, out string rawAfter, out _);
                bool matches = rawAfter == ((Def)def).defName;
                if (!matches)
                    return Fail("ActiveFluid write did not read back: raw field is '" + rawAfter
                        + "', wanted '" + ((Def)def).defName + "'.");
                return (object)new
                {
                    success = true,
                    fluidBefore = rawBefore,
                    fluidAfter = rawAfter,
                    readBackMatches = matches,
                    bodiesClassified = classifiedCount,
                    filledCells = filled,
                    refused = false,
                    mapId = map.uniqueID,
                    ticksGame = TicksGameSafe()
                };
            });
        }

        // ── loaded-assembly identity (plan 3.2 / 6.12, preflight P-E6) ────────────

        /// <summary>The file a loaded assembly came from: Assembly.Location when the loader
        /// used LoadFrom (vanilla ModAssemblyHandler does), else the carrying mod's
        /// Assemblies/ file whose name matches (a byte-loaded assembly has no Location).</summary>
        private static string AssemblyFilePath(Assembly asm, out string source)
        {
            string loc = null;
            try { loc = asm.Location; } catch { }
            if (!string.IsNullOrEmpty(loc)) { source = "Assembly.Location"; return loc; }
            string want = asm.GetName().Name;
            foreach (ModContentPack mod in LoadedModManager.RunningMods)
            {
                if (mod.assemblies?.loadedAssemblies == null || !mod.assemblies.loadedAssemblies.Contains(asm)) continue;
                foreach (var f in ModContentPack.GetAllFilesForModPreserveOrder(mod, "Assemblies/", e => e.ToLower() == ".dll"))
                {
                    if (string.Equals(System.IO.Path.GetFileNameWithoutExtension(f.Item2.Name), want, StringComparison.OrdinalIgnoreCase))
                    {
                        source = "modAssembliesFolder (Assembly.Location empty - loaded from bytes)";
                        return f.Item2.FullName;
                    }
                }
            }
            source = "unresolved";
            return null;
        }

        /// <summary>The module MVID straight out of a PE file's CLI metadata (Module table row 1,
        /// #GUID heap) - the file-side half of "is the process running THIS build".</summary>
        private static Guid? ReadPeMvid(byte[] b, out string error)
        {
            error = null;
            try
            {
                int pe = BitConverter.ToInt32(b, 0x3C);
                if (BitConverter.ToUInt32(b, pe) != 0x00004550) { error = "no PE signature"; return null; }
                int coff = pe + 4;
                int nSections = BitConverter.ToUInt16(b, coff + 2);
                int optSize = BitConverter.ToUInt16(b, coff + 16);
                int opt = coff + 20;
                int dd = opt + (BitConverter.ToUInt16(b, opt) == 0x20b ? 112 : 96);
                int secTable = opt + optSize;
                int RvaToOff(int rva)
                {
                    for (int s = 0; s < nSections; s++)
                    {
                        int h = secTable + s * 40;
                        int va = BitConverter.ToInt32(b, h + 12);
                        int size = Math.Max(BitConverter.ToInt32(b, h + 8), BitConverter.ToInt32(b, h + 16));
                        if (rva >= va && rva < va + size) return rva - va + BitConverter.ToInt32(b, h + 20);
                    }
                    return -1;
                }
                int cli = RvaToOff(BitConverter.ToInt32(b, dd + 14 * 8));
                if (cli < 0) { error = "no CLI header"; return null; }
                int md = RvaToOff(BitConverter.ToInt32(b, cli + 8));
                if (md < 0 || BitConverter.ToUInt32(b, md) != 0x424A5342) { error = "no metadata root"; return null; }
                int p = md + 16 + BitConverter.ToInt32(b, md + 12);
                int nStreams = BitConverter.ToUInt16(b, p + 2);
                p += 4;
                int tbl = -1, guid = -1;
                for (int s = 0; s < nStreams; s++)
                {
                    int off = BitConverter.ToInt32(b, p);
                    int hdr = p;
                    p += 8;
                    int nameStart = p;
                    while (b[p] != 0) p++;
                    string name = System.Text.Encoding.ASCII.GetString(b, nameStart, p - nameStart);
                    p = hdr + 8 + (((p + 1 - nameStart) + 3) & ~3);
                    if (name == "#~" || name == "#-") tbl = md + off;
                    else if (name == "#GUID") guid = md + off;
                }
                if (tbl < 0 || guid < 0) { error = "no #~ or #GUID stream"; return null; }
                byte heapSizes = b[tbl + 6];
                ulong valid = BitConverter.ToUInt64(b, tbl + 8);
                if ((valid & 1UL) == 0) { error = "no Module table"; return null; }
                int present = 0;
                for (int bit = 0; bit < 64; bit++) if ((valid & (1UL << bit)) != 0) present++;
                int row = tbl + 24 + 4 * present;
                int strIdx = (heapSizes & 1) != 0 ? 4 : 2;
                int mvidPos = row + 2 + strIdx;
                int gi = (heapSizes & 2) != 0 ? BitConverter.ToInt32(b, mvidPos) : BitConverter.ToUInt16(b, mvidPos);
                if (gi < 1) { error = "Module row has no MVID"; return null; }
                byte[] g = new byte[16];
                Array.Copy(b, guid + (gi - 1) * 16, g, 0, 16);
                return new Guid(g);
            }
            catch (Exception e)
            {
                error = e.GetType().Name + ": " + e.Message;
                return null;
            }
        }

        /// <summary>Identity block for TypeProbe: where the loaded assembly lives, its in-memory
        /// MVID, the on-disk file's SHA-256 and MVID, and whether the two MVIDs agree. A
        /// mismatch means the file was replaced after the process loaded it.</summary>
        private static Dictionary<string, object> AssemblyIdentity(Assembly asm)
        {
            var id = new Dictionary<string, object>();
            string path = AssemblyFilePath(asm, out string source);
            Guid loaded = asm.ManifestModule.ModuleVersionId;
            id["assemblyLocation"] = path;
            id["assemblyLocationSource"] = source;
            id["assemblyMvid"] = loaded.ToString();
            id["assemblyFileSha256"] = null;
            id["assemblyFileMvid"] = null;
            id["mvidMatchesFile"] = null;
            id["identityError"] = null;
            if (path == null) { id["identityError"] = "no file path for the loaded assembly"; return id; }
            try
            {
                byte[] bytes = System.IO.File.ReadAllBytes(path);
                using (var sha = System.Security.Cryptography.SHA256.Create())
                    id["assemblyFileSha256"] = BitConverter.ToString(sha.ComputeHash(bytes)).Replace("-", "").ToLowerInvariant();
                Guid? fileMvid = ReadPeMvid(bytes, out string perr);
                id["assemblyFileMvid"] = fileMvid?.ToString();
                id["mvidMatchesFile"] = fileMvid.HasValue ? (object)(fileMvid.Value == loaded) : null;
                if (perr != null) id["identityError"] = "PE MVID read: " + perr;
            }
            catch (Exception e)
            {
                id["identityError"] = "reading " + path + ": " + e.GetType().Name + ": " + e.Message;
            }
            return id;
        }
    }
}
