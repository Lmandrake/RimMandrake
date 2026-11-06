// JawaBenchCondProbes.cs - the Verse probe source for the bridge condition evaluator, and jawa/cond_eval
// (CONDPROBES_WIRE_ENGINE_READS; spec design/RimMandrake/bridge_conditions_2026-11-06/build_spec.md §1.3, §1.5, §2 T2).
//
// The pure evaluator (parse, refuse, compile, Kleene logic) is JawaBenchCondCore.cs; this file only answers
// IProbeSource: CurrentMap, MapSize, Refuse (bind once) and Read (one reading, {v, status}).
//
// Rules this file keeps (and selftest_cond_probes.py checks it still does):
// - READ-ONLY. Engine getters, fields and properties only: no RNG, no method call on a mod object except the three
//   FlowWorks read getters (DepthAt/FillAt/IsSourceCell), no write, no Find.CurrentMap retarget after bind.
// - Every probe is pinned to p.MapId (a Map.uniqueID) at bind. A UI map switch never moves it; a map that is gone
//   reads `gone`.
// - A non-ok reading is UNKNOWN, never 0 or false: `gone` (pawn/thing despawned, destroyed or dead; detail says which),
//   `oob`, `unbound` (FlowWorks not loaded, or loaded with no excavation component on that map), `error` (an
//   exception, message kept). A defName, pawn or thing that does not resolve, and a field path that does not compile,
//   are refused at bind (`bind` refusal naming it), never a silent false later.
// - Values match the existing read tools: cell.glow = jawa/glow_at groundGlow, map.sky_glow = its skyGlow, game.hour =
//   its hour; cell.terrain = jawa/get_terrain_layers top; fw.* = flowworks_excavation_report / _rect depth, fill,
//   isSourceCell; pawn.pos = jawa/pawn_get position. prove_cond_probes.py compares them live.
// - ring.count is RINGPROBES_WIRE_EVENT_CURSORS and is refused at bind here; pawn.flight/anim never reach this file
//   (the core refuses them as probe_not_in_v1).
// - No job reads pawn.job def "" and id -1 (ok): having no job is a state, not an unknown.
// - pawn.* and thing.* follow their subject wherever it is: p.MapId pins the spatial and map probes only (spec §1.2);
//   pawn.map says which map the pawn is on.

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimWorld;
using Verse;

namespace JawaBench.BridgeTools
{
    /// <summary>IProbeSource over the running game. One instance per compile; bound readers cached per Probe.</summary>
    internal sealed class VerseProbeSource : IProbeSource
    {
        delegate CondRead Reader(int x, int z);

        readonly Dictionary<JawaBenchCondCore.Probe, Reader> _bound = new Dictionary<JawaBenchCondCore.Probe, Reader>();
        readonly Func<string, Pawn> _findPawn;
        readonly Func<string, Thing> _findThing;

        internal const string ExcavationType = "RimMandrake.FlowWorks.RM_MapComponent_Excavation";

        internal VerseProbeSource(Func<string, Pawn> findPawn, Func<string, Thing> findThing)
        {
            _findPawn = findPawn;
            _findThing = findThing;
        }

        static CondRead Ok(object v) { return new CondRead(v, "ok", ""); }
        static CondRead St(string status, string detail) { return new CondRead(null, status, detail); }

        internal static Map MapById(int id)
        {
            if (Current.Game == null || Find.Maps == null) return null;
            foreach (var m in Find.Maps) if (m != null && m.uniqueID == id) return m;
            return null;
        }

        public int CurrentMap()
        {
            var m = Current.Game != null ? Find.CurrentMap : null;
            return m != null ? m.uniqueID : -1;
        }

        public bool MapSize(int mapId, out int x, out int z)
        {
            x = 0; z = 0;
            var m = MapById(mapId);
            if (m == null) return false;
            x = m.Size.x; z = m.Size.z;
            return true;
        }

        public string Refuse(string key, JawaBenchCondCore.Probe p)
        {
            try
            {
                string why;
                var r = Bind(p, out why);
                if (r == null) return why ?? ("cannot bind " + p.Name);
                _bound[p] = r;
                return null;
            }
            catch (Exception e) { return "bind threw " + e.GetType().Name + ": " + e.Message; }
        }

        public CondRead Read(string key, JawaBenchCondCore.Probe p, int x, int z)
        {
            Reader r;
            if (!_bound.TryGetValue(p, out r)) return St("error", "probe not bound: " + key);
            try { return r(x, z); }
            catch (Exception e) { return St("error", e.GetType().Name + ": " + e.Message); }
        }

        static string Arg(JawaBenchCondCore.Probe p, string k)
        {
            object v;
            return p.Args.TryGetValue(k, out v) ? v as string : null;
        }

        /// <summary>A cell read on the pinned map: gone if the map went, oob if the cell is off it.</summary>
        static Reader CellRead(int mapId, Func<Map, IntVec3, CondRead> f)
        {
            return (x, z) =>
            {
                var m = MapById(mapId);
                if (m == null) return St("gone", "map " + mapId + " gone");
                var c = new IntVec3(x, 0, z);
                if (!c.InBounds(m)) return St("oob", x + "," + z + " outside " + m.Size.x + "x" + m.Size.z);
                return f(m, c);
            };
        }

        static Reader MapRead(int mapId, Func<Map, CondRead> f)
        {
            return (x, z) =>
            {
                var m = MapById(mapId);
                if (m == null) return St("gone", "map " + mapId + " gone");
                return f(m);
            };
        }

        Reader Bind(JawaBenchCondCore.Probe p, out string why)
        {
            why = null;
            int mid = p.MapId;
            switch (p.Name)
            {
                case "cell.terrain":
                    return CellRead(mid, (m, c) =>
                    {
                        var t = m.terrainGrid.TopTerrainAt(c);
                        return t == null ? St("error", "no top terrain") : Ok(t.defName);
                    });
                case "cell.is_water":
                    return CellRead(mid, (m, c) =>
                    {
                        var t = m.terrainGrid.TopTerrainAt(c);
                        return t == null ? St("error", "no top terrain") : Ok(t.IsWater);
                    });
                case "cell.glow":
                    return CellRead(mid, (m, c) => Ok((double)m.glowGrid.GroundGlowAt(c)));
                case "cell.roofed":
                    return CellRead(mid, (m, c) => Ok(m.roofGrid.Roofed(c)));
                case "cell.temp":
                    return CellRead(mid, (m, c) => Ok((double)GenTemperature.GetTemperatureForCell(c, m)));
                case "cell.fire":
                    return CellRead(mid, (m, c) =>
                    {
                        var l = m.thingGrid.ThingsListAtFast(c);
                        for (int i = 0; i < l.Count; i++) if (l[i] is Fire) return Ok(true);
                        return Ok(false);
                    });
                case "fw.depth":
                case "fw.fill":
                case "fw.source":
                    return BindFlowWorks(p.Name, mid);
                case "map.sky_glow":
                    return MapRead(mid, m => Ok((double)m.skyManager.CurSkyGlow));
                case "map.count":
                    return BindCount(p, mid, out why);
                case "game.tick":
                    return (x, z) => Find.TickManager == null ? St("error", "no TickManager") : Ok((double)Find.TickManager.TicksGame);
                case "game.hour":
                    return MapRead(mid, m => Ok((double)GenLocalDate.HourFloat(m)));
                case "pawn.pos":
                case "pawn.map":
                case "pawn.job":
                case "pawn.state":
                    return BindPawn(p, out why);
                case "thing.exists":
                case "thing.spawned":
                case "thing.pos":
                case "thing.field":
                    return BindThing(p, out why);
                case "ring.count":
                    why = "ring.count is not wired yet (RINGPROBES_WIRE_EVENT_CURSORS)";
                    return null;
            }
            why = "no Verse read for probe " + p.Name;
            return null;
        }

        // ---------------------------------------------------------------- FlowWorks
        static Reader BindFlowWorks(string name, int mapId)
        {
            return (x, z) =>
            {
                var m = MapById(mapId);
                if (m == null) return St("gone", "map " + mapId + " gone");
                var c = new IntVec3(x, 0, z);
                if (!c.InBounds(m)) return St("oob", x + "," + z + " outside " + m.Size.x + "x" + m.Size.z);
                string err;
                var fw = FwFor(m, out err);
                if (fw == null) return St("unbound", err);
                if (name == "fw.depth") return Ok((double)fw.Depth(c));
                if (name == "fw.fill") return Ok((double)fw.Fill(c));
                return Ok(fw.Source(c));
            };
        }

        sealed class FwReads
        {
            public MapComponent Comp;
            public Func<IntVec3, byte> Depth, Fill;
            public Func<IntVec3, bool> Source;
        }

        static readonly Dictionary<int, FwReads> FwCache = new Dictionary<int, FwReads>();

        static FwReads FwFor(Map m, out string err)
        {
            err = null;
            var type = GenTypes.GetTypeInAnyAssembly(ExcavationType);
            if (type == null) { err = "FlowWorks is not loaded (" + ExcavationType + " does not resolve)"; return null; }
            FwReads r;
            MapComponent comp = null;
            foreach (MapComponent c in m.components) if (type.IsInstanceOfType(c)) { comp = c; break; }
            if (comp == null) { err = "FlowWorks loaded but map " + m.uniqueID + " has no RM_MapComponent_Excavation"; return null; }
            if (FwCache.TryGetValue(m.uniqueID, out r) && ReferenceEquals(r.Comp, comp)) return r;
            var arg = new[] { typeof(IntVec3) };
            MethodInfo md = type.GetMethod("DepthAt", arg), mf = type.GetMethod("FillAt", arg), ms = type.GetMethod("IsSourceCell", arg);
            if (md == null || mf == null || ms == null || md.ReturnType != typeof(byte) || mf.ReturnType != typeof(byte)
                || ms.ReturnType != typeof(bool))
            { err = "RM_MapComponent_Excavation lacks DepthAt/FillAt(IntVec3)->byte or IsSourceCell(IntVec3)->bool"; return null; }
            r = new FwReads
            {
                Comp = comp,
                Depth = (Func<IntVec3, byte>)Delegate.CreateDelegate(typeof(Func<IntVec3, byte>), comp, md),
                Fill = (Func<IntVec3, byte>)Delegate.CreateDelegate(typeof(Func<IntVec3, byte>), comp, mf),
                Source = (Func<IntVec3, bool>)Delegate.CreateDelegate(typeof(Func<IntVec3, bool>), comp, ms),
            };
            FwCache[m.uniqueID] = r;
            return r;
        }

        // ---------------------------------------------------------------- map.count
        static Reader BindCount(JawaBenchCondCore.Probe p, int mapId, out string why)
        {
            why = null;
            string dn = Arg(p, "def");
            var def = DefDatabase<ThingDef>.GetNamedSilentFail(dn);
            if (def == null) { why = "no ThingDef named '" + dn + "'"; return null; }
            int[] rect = p.Rect;
            return MapRead(mapId, m =>
            {
                var l = m.listerThings.ThingsOfDef(def);
                if (rect == null) return Ok((double)l.Count);
                int n = 0;
                for (int i = 0; i < l.Count; i++)
                {
                    var c = l[i].Position;
                    if (c.x >= rect[0] && c.x < rect[0] + rect[2] && c.z >= rect[1] && c.z < rect[1] + rect[3]) n++;
                }
                return Ok((double)n);
            });
        }

        // ---------------------------------------------------------------- pawn
        Reader BindPawn(JawaBenchCondCore.Probe p, out string why)
        {
            why = null;
            string id = Arg(p, "pawn");
            var pawn = _findPawn(id);
            if (pawn == null) { why = "no pawn '" + id + "'"; return null; }
            string f = Arg(p, "f");
            switch (p.Name)
            {
                case "pawn.pos":
                    return (x, z) =>
                    {
                        string g = PawnGone(pawn, true);
                        if (g != null) return St("gone", g);
                        return Ok((double)(f == "x" ? pawn.Position.x : pawn.Position.z));
                    };
                case "pawn.map":
                    return (x, z) =>
                    {
                        string g = PawnGone(pawn, true);
                        return g != null ? St("gone", g) : Ok((double)pawn.Map.uniqueID);
                    };
                case "pawn.job":
                    return (x, z) =>
                    {
                        string g = PawnGone(pawn, true);
                        if (g != null) return St("gone", g);
                        var j = pawn.CurJob;
                        if (f == "def") return Ok(j != null && j.def != null ? j.def.defName : "");
                        return Ok((double)(j != null ? j.loadID : -1));
                    };
                default: // pawn.state
                    return (x, z) =>
                    {
                        if (f == "dead")
                        {
                            if (pawn.Dead) return Ok(true);
                            return pawn.Destroyed ? St("gone", "destroyed") : Ok(false);
                        }
                        string g = PawnGone(pawn, false);
                        if (g != null) return St("gone", g);
                        if (f == "downed") return Ok(pawn.Downed);
                        if (f == "mental") return Ok(pawn.InMentalState);
                        return Ok(pawn.Drafted);
                    };
            }
        }

        /// <summary>null while the pawn can be read; else why not. needSpawned: position-like reads need a map.</summary>
        static string PawnGone(Pawn pawn, bool needSpawned)
        {
            if (pawn.Dead) return "dead";
            if (pawn.Destroyed) return "destroyed";
            if (needSpawned && !pawn.Spawned) return "despawned";
            return null;
        }

        // ---------------------------------------------------------------- thing
        Reader BindThing(JawaBenchCondCore.Probe p, out string why)
        {
            why = null;
            string id = Arg(p, "thing");
            var t = _findThing(id);
            if (t == null) { why = "no thing '" + id + "'"; return null; }
            switch (p.Name)
            {
                case "thing.exists":
                    return (x, z) => Ok(!t.Destroyed);
                case "thing.spawned":
                    return (x, z) => Ok(t.Spawned);
                case "thing.pos":
                {
                    string f = Arg(p, "f");
                    return (x, z) =>
                    {
                        if (t.Destroyed) return St("gone", "destroyed");
                        if (!t.Spawned) return St("gone", "despawned");
                        return Ok((double)(f == "x" ? t.Position.x : t.Position.z));
                    };
                }
                default: // thing.field
                {
                    var getter = CompilePath(t.GetType(), Arg(p, "path"), out why);
                    if (getter == null) return null;
                    return (x, z) =>
                    {
                        if (t.Destroyed) return St("gone", "destroyed");
                        return getter(t);
                    };
                }
            }
        }

        const BindingFlags Inst = BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic;

        /// <summary>A dotted path of fields and properties, resolved against declared types once. Methods refused.</summary>
        internal static Func<object, CondRead> CompilePath(Type root, string path, out string why)
        {
            why = null;
            var steps = new List<Func<object, object>>();
            var names = path.Split('.');
            Type cur = root;
            foreach (var raw in names)
            {
                string n = raw.Trim();
                if (n.Length == 0) { why = "empty segment in path '" + path + "'"; return null; }
                FieldInfo fi = null;
                PropertyInfo pi = null;
                for (var ty = cur; ty != null && fi == null && pi == null; ty = ty.BaseType)
                {
                    fi = ty.GetField(n, Inst | BindingFlags.DeclaredOnly);
                    if (fi == null)
                    {
                        var cand = ty.GetProperty(n, Inst | BindingFlags.DeclaredOnly);
                        if (cand != null && cand.GetIndexParameters().Length == 0 && cand.GetGetMethod(true) != null) pi = cand;
                    }
                }
                if (fi != null) { var f = fi; steps.Add(o => f.GetValue(o)); cur = fi.FieldType; }
                else if (pi != null) { var q = pi; steps.Add(o => q.GetValue(o, null)); cur = pi.PropertyType; }
                else { why = "no field or property '" + n + "' on " + cur.FullName; return null; }
            }
            if (!Readable(cur)) { why = "path '" + path + "' ends at " + cur.FullName + ": want a number, bool, string, enum or Def"; return null; }
            return o =>
            {
                object v = o;
                for (int i = 0; i < steps.Count; i++)
                {
                    if (v == null) return St("error", i == 0 ? "thing is null" : "null at '" + names[i - 1] + "'");
                    v = steps[i](v);
                }
                return Convert(v);
            };
        }

        static bool Readable(Type t)
        {
            var u = Nullable.GetUnderlyingType(t) ?? t;
            return (u.IsPrimitive && u != typeof(IntPtr) && u != typeof(UIntPtr) && u != typeof(char)) || u.IsEnum || u == typeof(string) || u == typeof(decimal) || typeof(Def).IsAssignableFrom(u)
                   || u == typeof(object);
        }

        static CondRead Convert(object v)
        {
            if (v == null) return St("error", "value is null");
            if (v is bool) return Ok(v);
            if (v is string) return Ok(v);
            if (v is Enum) return Ok(v.ToString());
            var d = v as Def;
            if (d != null) return Ok(d.defName);
            if (v is char) return St("error", "type: char");
            if (v.GetType().IsPrimitive || v is decimal) return Ok(System.Convert.ToDouble(v, System.Globalization.CultureInfo.InvariantCulture));
            return St("error", "type: " + v.GetType().FullName);
        }
    }

    public sealed partial class JawaBenchTerrainTools
    {
        internal static VerseProbeSource NewProbeSource()
        {
            return new VerseProbeSource(
                id => { string e; return FindPawn(id, out e); },
                id => { string e; return SystemToolsFindThing(id, out e) ?? FindThingIncludingContainers(id, out e); });
        }

        [Tool(
            "jawa/cond_eval",
            Description =
                "Evaluate a bridge condition tree NOW, with no tick (build_spec bridge_conditions_2026-11-06 §1.5): a dry " +
                "run of what advance_until/watch would see. tree is the JSON of one node ({\"cmp\": [{\"p\": \"cell.glow\", " +
                "\"cell\": [x,z]}, \">=\", 0.3]}, all/any/not, changed/edge/stays). Probes: cell.terrain, cell.is_water, " +
                "cell.glow, cell.roofed, cell.temp, cell.fire, fw.depth, fw.fill, fw.source, map.sky_glow, map.count, " +
                "game.tick, game.hour, pawn.pos/map/job/state, thing.exists/spawned/pos/field. Every read returns " +
                "{v, status}: ok | gone | oob | unbound (FlowWorks absent) | error; non-ok is UNKNOWN, never 0/false. " +
                "A bad defName, pawn, thing or field path, and an out-of-bounds cell, are REFUSED by name before any read. " +
                "Probes are pinned to mapId (default: the current map). Read-only.",
            ResultDescription =
                "success, canonical (the tree as compiled, mapId pinned), v (true|false|null), status, values[] " +
                "(per node: id, v, status, detail?, pv?), cost{nodeEvals, reads}, evalMs, ticksGame. A refusal: success " +
                "false, refused (name), at (JSON path), detail.")]
        public static async Task<object> CondEval(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "The condition tree as JSON (one node).")] string tree = null,
            [ToolParameter(Description = "Map uniqueID to pin every spatial probe to. -1 = current map.")] int mapId = -1)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null || Find.Maps == null) return Fail("No game loaded.");
                if (string.IsNullOrWhiteSpace(tree)) return Fail("Give tree (a JSON condition node).");
                Dictionary<string, object> res;
                var sw = Stopwatch.StartNew();
                try
                {
                    var spec = new Dictionary<string, object> { { "tree", JawaBenchCondCore.ParseSpec(tree) } };
                    if (mapId >= 0) spec["mapId"] = (double)mapId;
                    res = JawaBenchCondCore.CondEval(spec, NewProbeSource());
                }
                catch (CondRefused e) { res = JawaBenchCondCore.Refusal(e); }
                sw.Stop();
                res["success"] = !res.ContainsKey("refused");
                res["evalMs"] = sw.Elapsed.TotalMilliseconds;
                res["ticksGame"] = (double)TicksGameSafe();
                return res;
            });
        }
    }
}
