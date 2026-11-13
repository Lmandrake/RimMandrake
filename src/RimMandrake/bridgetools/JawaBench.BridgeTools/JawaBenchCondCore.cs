// JawaBenchCondCore.cs - the PURE bridge condition evaluator (CONDCORE_BUILD_THREE_VALUED_TREES).
// Spec: design/RimMandrake/bridge_conditions_2026-11-06/build_spec.md §1 (wire §1.2, probes §1.3, nodes §1.4, result
// §1.5, determinism §1.8). The Verse probe source is CONDPROBES_WIRE_ENGINE_READS, the safe_advance wiring
// ADVANCEUNTIL_WIRE_PER_TICK_STOP; neither lives here.
//
// ⛔ Compiled into bridgetools/CondSelfTest too: a `using Verse;` here breaks that build.
// ⛔ ONE semantics written twice: src/RimMandrake/Utils/conds.py is the Python twin, and
//    src/RimMandrake/Utils/selftest_conds_vectors.py requires byte-identical output on Utils/conds_vectors.json.
//    Change both together, in the same order: traversal, refusal order, detail strings, number formatting.
//    The semantics decisions are written once, in conds.py's docstring.
//
// What lives here: a strict JSON parser and canonical writer, the compiler (parse, refuse by name, canonicalise,
// bind through IProbeSource), the three-valued evaluator (strong Kleene, no short-circuit, changed/edge/stays state),
// CondRun (arm, end-of-tick step, arbitration, coverage, cost, watchers, sample, snapshot) and the vector runner
// (CondSeries) the selftest drives.

using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text;

namespace JawaBench.BridgeTools
{
    /// <summary>A probe reading: V is null, bool, double or string; Status ok|gone|oob|unbound|error.</summary>
    internal struct CondRead
    {
        public object V;
        public string Status;
        public string Detail;
        public CondRead(object v, string status, string detail) { V = v; Status = status; Detail = detail ?? ""; }
    }

    /// <summary>Where probe values come from: the Verse reads in game, a vector series offline.</summary>
    internal interface IProbeSource
    {
        int CurrentMap();
        bool MapSize(int mapId, out int x, out int z);
        /// <summary>null when the probe binds, else the reason it cannot (a defName that does not resolve...).
        /// The key is the probe's identity; p carries its parsed args and pinned MapId (the key holds no map).</summary>
        string Refuse(string key, JawaBenchCondCore.Probe p);
        /// <summary>One reading. x, z is the cell for a spatial probe (each cell of a rect in turn), else -1, -1.</summary>
        CondRead Read(string key, JawaBenchCondCore.Probe p, int x, int z);
    }

    internal sealed class CondRefused : Exception
    {
        public readonly string Name, At, Detail;
        public CondRefused(string name, string at, string detail) : base(name) { Name = name; At = at; Detail = detail; }
    }

    internal static class JawaBenchCondCore
    {
        internal const int MaxNodes = 64, MaxCells = 1024, MaxWatchers = 16, MaxSampleRows = 4096, MaxEvery = 60000;
        internal const int HardMaxTicks = 1200000;   // JawaBenchVitalsCore.HardAdvanceCap

        internal static readonly string[] Statuses = { "ok", "gone", "oob", "unbound", "error" };
        internal static readonly string[] Spatial = { "cell.terrain", "cell.is_water", "fw.depth", "fw.water_m", "fw.source",
                                                      "cell.glow", "cell.roofed", "cell.temp", "cell.fire" };
        internal static readonly string[] RingSources = { "damage_log", "incident_journal", "drain_log", "letters" };
        internal static readonly string[] Reducers = { "any", "all", "count_where", "max", "min" };
        internal static readonly string[] Ops = { "==", "!=", "<", "<=", ">", ">=", "in", "hour_in" };
        internal static readonly string[] WhereOps = { "==", "!=", "<", "<=", ">", ">=" };
        internal static readonly string[] NodeKinds = { "all", "any", "not", "cmp", "changed", "edge", "stays", "alarm" };
        internal static readonly string[] ArgOrder = { "cell", "rect", "reduce", "where", "mapId", "def", "pawn", "thing",
                                                       "f", "path", "source", "filter" };
        internal static readonly string[] RunKeys = { "every", "mapId", "max_ticks", "on_unknown", "runKey", "sample",
                                                      "snapshot_on_hit", "until", "watch" };
        internal static readonly string[] EvalKeys = { "mapId", "tree" };

        internal sealed class ProbeInfo
        {
            public string Type; public string[] Req; public string[] Opt;
            public ProbeInfo(string t, string[] req, string[] opt) { Type = t; Req = req; Opt = opt; }
        }

        static readonly string[] None0 = new string[0];
        internal static readonly Dictionary<string, ProbeInfo> Probes = new Dictionary<string, ProbeInfo>
        {
            { "cell.terrain", new ProbeInfo("str", None0, None0) }, { "cell.is_water", new ProbeInfo("bool", None0, None0) },
            { "fw.depth", new ProbeInfo("num", None0, None0) }, { "fw.water_m", new ProbeInfo("num", None0, None0) },
            { "fw.source", new ProbeInfo("bool", None0, None0) },
            { "cell.glow", new ProbeInfo("num", None0, None0) }, { "cell.roofed", new ProbeInfo("bool", None0, None0) },
            { "cell.temp", new ProbeInfo("num", None0, None0) }, { "cell.fire", new ProbeInfo("bool", None0, None0) },
            { "map.sky_glow", new ProbeInfo("num", None0, None0) },
            { "map.count", new ProbeInfo("num", new[] { "def" }, new[] { "rect" }) },
            { "game.tick", new ProbeInfo("num", None0, None0) }, { "game.hour", new ProbeInfo("num", None0, None0) },
            { "pawn.pos", new ProbeInfo("num", new[] { "pawn", "f" }, None0) },
            { "pawn.map", new ProbeInfo("num", new[] { "pawn" }, None0) },
            { "pawn.job", new ProbeInfo("job", new[] { "pawn", "f" }, None0) },
            { "pawn.state", new ProbeInfo("bool", new[] { "pawn", "f" }, None0) },
            { "thing.exists", new ProbeInfo("bool", new[] { "thing" }, None0) },
            { "thing.spawned", new ProbeInfo("bool", new[] { "thing" }, None0) },
            { "thing.pos", new ProbeInfo("num", new[] { "thing", "f" }, None0) },
            { "thing.field", new ProbeInfo("any", new[] { "thing", "path" }, None0) },
            { "ring.count", new ProbeInfo("num", new[] { "source" }, new[] { "filter" }) },
        };
        internal static readonly Dictionary<string, string[]> FValues = new Dictionary<string, string[]>
        {
            { "pawn.pos", new[] { "x", "z" } }, { "pawn.job", new[] { "def", "id" } },
            { "pawn.state", new[] { "downed", "dead", "mental", "drafted" } }, { "thing.pos", new[] { "x", "z" } },
        };

        static bool In(string[] a, string s) { return s != null && Array.IndexOf(a, s) >= 0; }
        static CondRefused Refuse(string name, string at, string detail) { return new CondRefused(name, at, detail); }

        // ============================================================================================ JSON
        /// <summary>Strict JSON: objects -> Dictionary, arrays -> List, numbers -> double. Duplicate keys refused.</summary>
        internal static object ParseJson(string text)
        {
            int i = 0;
            object v = PValue(text, ref i);
            PWs(text, ref i);
            if (i != text.Length) throw new FormatException("trailing text");
            return v;
        }

        static void PWs(string s, ref int i)
        {
            while (i < s.Length && (s[i] == ' ' || s[i] == '\t' || s[i] == '\n' || s[i] == '\r')) i++;
        }

        static object PValue(string s, ref int i)
        {
            PWs(s, ref i);
            if (i >= s.Length) throw new FormatException("end of text");
            char c = s[i];
            if (c == '{')
            {
                var d = new Dictionary<string, object>();
                i++; PWs(s, ref i);
                if (i < s.Length && s[i] == '}') { i++; return d; }
                while (true)
                {
                    PWs(s, ref i);
                    if (i >= s.Length || s[i] != '"') throw new FormatException("want key");
                    string k = PString(s, ref i);
                    PWs(s, ref i);
                    if (i >= s.Length || s[i] != ':') throw new FormatException("want :");
                    i++;
                    object v = PValue(s, ref i);
                    if (d.ContainsKey(k)) throw new FormatException("duplicate key");
                    d[k] = v;
                    PWs(s, ref i);
                    if (i < s.Length && s[i] == ',') { i++; continue; }
                    if (i < s.Length && s[i] == '}') { i++; return d; }
                    throw new FormatException("want , or }");
                }
            }
            if (c == '[')
            {
                var l = new List<object>();
                i++; PWs(s, ref i);
                if (i < s.Length && s[i] == ']') { i++; return l; }
                while (true)
                {
                    l.Add(PValue(s, ref i));
                    PWs(s, ref i);
                    if (i < s.Length && s[i] == ',') { i++; continue; }
                    if (i < s.Length && s[i] == ']') { i++; return l; }
                    throw new FormatException("want , or ]");
                }
            }
            if (c == '"') return PString(s, ref i);
            if (Lit(s, ref i, "true")) return true;
            if (Lit(s, ref i, "false")) return false;
            if (Lit(s, ref i, "null")) return null;
            int st = i;
            if (i < s.Length && s[i] == '-') i++;
            if (i >= s.Length || !char.IsDigit(s[i])) throw new FormatException("bad value");
            if (s[i] == '0' && i + 1 < s.Length && char.IsDigit(s[i + 1])) throw new FormatException("leading zero");
            while (i < s.Length && char.IsDigit(s[i])) i++;
            if (i < s.Length && s[i] == '.')
            {
                i++;
                if (i >= s.Length || !char.IsDigit(s[i])) throw new FormatException("bad fraction");
                while (i < s.Length && char.IsDigit(s[i])) i++;
            }
            if (i < s.Length && (s[i] == 'e' || s[i] == 'E'))
            {
                i++;
                if (i < s.Length && (s[i] == '+' || s[i] == '-')) i++;
                if (i >= s.Length || !char.IsDigit(s[i])) throw new FormatException("bad exponent");
                while (i < s.Length && char.IsDigit(s[i])) i++;
            }
            double num = double.Parse(s.Substring(st, i - st), NumberStyles.Float, CultureInfo.InvariantCulture);
            if (double.IsInfinity(num) || double.IsNaN(num)) throw new FormatException("number out of range");
            return num;
        }

        static bool Lit(string s, ref int i, string w)
        {
            if (string.CompareOrdinal(s, i, w, 0, w.Length) != 0) return false;
            i += w.Length;
            return true;
        }

        static string PString(string s, ref int i)
        {
            var sb = new StringBuilder();
            i++;   // opening quote
            while (true)
            {
                if (i >= s.Length) throw new FormatException("unterminated string");
                char c = s[i++];
                if (c == '"') return sb.ToString();
                if (c < 0x20) throw new FormatException("control character in string");
                if (c != '\\') { sb.Append(c); continue; }
                if (i >= s.Length) throw new FormatException("bad escape");
                char e = s[i++];
                switch (e)
                {
                    case '"': sb.Append('"'); break;
                    case '\\': sb.Append('\\'); break;
                    case '/': sb.Append('/'); break;
                    case 'b': sb.Append('\b'); break;
                    case 'f': sb.Append('\f'); break;
                    case 'n': sb.Append('\n'); break;
                    case 'r': sb.Append('\r'); break;
                    case 't': sb.Append('\t'); break;
                    case 'u':
                        if (i + 4 > s.Length) throw new FormatException("bad \\u");
                        sb.Append((char)int.Parse(s.Substring(i, 4), NumberStyles.HexNumber, CultureInfo.InvariantCulture));
                        i += 4;
                        break;
                    default: throw new FormatException("bad escape");
                }
            }
        }

        internal static string FmtNum(double x)
        {
            if (double.IsNaN(x) || double.IsInfinity(x)) return "null";
            if (x == Math.Floor(x) && Math.Abs(x) < 1e15) return ((long)x).ToString(CultureInfo.InvariantCulture);
            string s = null;
            for (int p = 15; p <= 17; p++)
            {
                s = x.ToString("E" + (p - 1), CultureInfo.InvariantCulture);
                if (double.Parse(s, NumberStyles.Float, CultureInfo.InvariantCulture) == x) break;
            }
            int ei = s.IndexOf('E');
            string mant = s.Substring(0, ei);
            int exp = int.Parse(s.Substring(ei + 1), NumberStyles.Integer, CultureInfo.InvariantCulture);
            bool neg = mant.StartsWith("-", StringComparison.Ordinal);
            string digits = mant.TrimStart('-').Replace(".", "").TrimEnd('0');
            if (digits.Length == 0) digits = "0";
            string sign = neg ? "-" : "";
            if (exp > -6 && exp < 15)
            {
                string body;
                if (exp >= 0)
                    body = digits.Length <= exp + 1 ? digits + new string('0', exp + 1 - digits.Length)
                                                    : digits.Substring(0, exp + 1) + "." + digits.Substring(exp + 1);
                else
                    body = "0." + new string('0', -exp - 1) + digits;
                return sign + body;
            }
            return sign + digits.Substring(0, 1) + (digits.Length > 1 ? "." + digits.Substring(1) : "") + "e"
                   + exp.ToString(CultureInfo.InvariantCulture);
        }

        internal static string FmtStr(string s)
        {
            var sb = new StringBuilder(s.Length + 2);
            sb.Append('"');
            foreach (char c in s)
            {
                if (c == '"') sb.Append("\\\"");
                else if (c == '\\') sb.Append("\\\\");
                else if (c == '\n') sb.Append("\\n");
                else if (c == '\r') sb.Append("\\r");
                else if (c == '\t') sb.Append("\\t");
                else if (c < 0x20) sb.Append("\\u").Append(((int)c).ToString("x4", CultureInfo.InvariantCulture));
                else sb.Append(c);
            }
            sb.Append('"');
            return sb.ToString();
        }

        internal static List<string> SortedKeys(Dictionary<string, object> d)
        {
            var ks = new List<string>(d.Keys);
            ks.Sort(string.CompareOrdinal);
            return ks;
        }

        internal static string Canon(object v)
        {
            var sb = new StringBuilder();
            Canon(v, sb);
            return sb.ToString();
        }

        static void Canon(object v, StringBuilder sb)
        {
            if (v == null) { sb.Append("null"); return; }
            if (v is bool) { sb.Append((bool)v ? "true" : "false"); return; }
            if (IsNum(v)) { sb.Append(FmtNum(Num(v))); return; }
            if (v is string) { sb.Append(FmtStr((string)v)); return; }
            var d = v as Dictionary<string, object>;
            if (d != null)
            {
                sb.Append('{');
                bool first = true;
                foreach (var k in SortedKeys(d))
                {
                    if (!first) sb.Append(',');
                    first = false;
                    sb.Append(FmtStr(k)).Append(':');
                    Canon(d[k], sb);
                }
                sb.Append('}');
                return;
            }
            var l = v as System.Collections.IList;
            if (l != null)
            {
                sb.Append('[');
                for (int i = 0; i < l.Count; i++)
                {
                    if (i > 0) sb.Append(',');
                    Canon(l[i], sb);
                }
                sb.Append(']');
                return;
            }
            throw new ArgumentException("not JSON: " + v.GetType().Name);
        }

        // A Verse source hands back float (glow), byte (FlowWorks fill), int or long: every one is a number.
        internal static bool IsNum(object x)
        {
            return x is double || x is float || x is long || x is int || x is short || x is byte || x is sbyte
                   || x is ushort || x is uint;
        }
        internal static double Num(object x) { return Convert.ToDouble(x, CultureInfo.InvariantCulture); }
        internal static bool IsInt(object x)
        {
            if (!IsNum(x)) return false;
            double d = Num(x);
            return d == Math.Floor(d) && Math.Abs(d) < 2147483648.0;
        }

        internal static string JType(object x)
        {
            if (x == null) return "null";
            if (x is bool) return "bool";
            if (IsNum(x)) return "num";
            if (x is string) return "str";
            if (x is System.Collections.IList) return "list";
            return "object";
        }

        static string KeyVal(object v)
        {
            var l = v as List<object>;
            if (l != null)
            {
                var parts = new List<string>();
                foreach (var x in l) parts.Add(KeyVal(x));
                return string.Join(",", parts.ToArray());
            }
            var ia = v as int[];
            if (ia != null)
            {
                var parts = new string[ia.Length];
                for (int i = 0; i < ia.Length; i++) parts[i] = ia[i].ToString(CultureInfo.InvariantCulture);
                return string.Join(",", parts);
            }
            if (v is string) return (string)v;
            return Canon(v);
        }

        static List<object> IntList(int[] a)
        {
            var l = new List<object>();
            foreach (int x in a) l.Add((double)x);
            return l;
        }

        // ============================================================================================ compiled tree
        internal sealed class Probe
        {
            public string Name, PType, Reduce, WhereOp;
            public object WhereLit;
            public bool HasWhere;
            public Dictionary<string, object> Args = new Dictionary<string, object>();
            public int[] Cell, Rect;
            public int MapId;
            public string Key = "";
            public Dictionary<string, object> Canonical;

            public string CellKey(int x, int z)
            {
                var sb = new StringBuilder(Name);
                foreach (var k in SortedKeys(Args)) sb.Append(' ').Append(k).Append('=').Append(KeyVal(Args[k]));
                sb.Append(" cell=").Append(x.ToString(CultureInfo.InvariantCulture)).Append(',')
                  .Append(z.ToString(CultureInfo.InvariantCulture));
                return sb.ToString();
            }

            public string VType()
            {
                if (Rect != null && In(Spatial, Name)) return Reduce == "any" || Reduce == "all" ? "bool" : "num";
                if (PType == "job") return (Args.ContainsKey("f") && (string)Args["f"] == "def") ? "str" : "num";
                return PType;
            }
        }

        internal sealed class Node
        {
            public string Kind, Id;
            public bool Optional;
            public List<Node> Children = new List<Node>();
            public Probe Probe;
            public string Op;
            public object Lit;
            public bool HasTol;
            public double Tol;
            public string Dir = "rise";
            public int Ticks;
            public Dictionary<string, object> Canonical;
            // evaluation state
            public bool HasPrev;
            public object Prev;
            public bool HasStart;
            public long Start;
            public Node(string kind, string id) { Kind = kind; Id = id; }
            public void Reset() { HasPrev = false; Prev = null; HasStart = false; Start = 0; }
        }

        internal sealed class Watcher
        {
            public string Name; public Node Tree;
            public int Events, Unknowns;
            public Dictionary<string, object> Disarmed;
            public Watcher(string name, Node tree) { Name = name; Tree = tree; }
        }

        internal sealed class Compiled
        {
            public string Mode;
            public Node Tree;
            public List<Watcher> Watch = new List<Watcher>();
            public List<KeyValuePair<string, Probe>> Sample, Snapshot;
            public int SampleEvery;
            public bool SampleChangeOnly;
            public int MaxTicks, Every = 1;
            public string OnUnknown = "stop", RunKey;
            public Dictionary<string, object> Canonical;
        }

        internal sealed class Compiler
        {
            readonly IProbeSource _src;
            readonly string _mode;
            int _nodes, _idn, _cells, _mapId;
            readonly HashSet<string> _ids = new HashSet<string>();

            public Compiler(IProbeSource src, string mode) { _src = src; _mode = mode; }

            static Dictionary<string, object> Obj(object x, string at)
            {
                var d = x as Dictionary<string, object>;
                if (d == null) throw Refuse("type", at, "want object, got " + JType(x));
                return d;
            }

            static void Keys(Dictionary<string, object> d, IList<string> allowed, string at)
            {
                foreach (var k in SortedKeys(d))
                    if (!allowed.Contains(k)) throw Refuse("unknown_key", at, k);
            }

            static int IntIn(Dictionary<string, object> d, string k, int lo, int hi, string at, int? dflt)
            {
                if (!d.ContainsKey(k))
                {
                    if (dflt == null) throw Refuse("missing_key", at, k);
                    return dflt.Value;
                }
                object v = d[k];
                if (!IsNum(v)) throw Refuse("type", at + "." + k, "want num, got " + JType(v));
                if (!IsInt(v) || Num(v) < lo || Num(v) > hi)
                    throw Refuse("bad_value", at + "." + k, string.Format(CultureInfo.InvariantCulture,
                        "want integer in [{0},{1}]", lo, hi));
                return (int)Num(v);
            }

            static bool Flag(Dictionary<string, object> d, string k, string at)
            {
                if (!d.ContainsKey(k)) return false;
                if (!(d[k] is bool)) throw Refuse("type", at + "." + k, "want bool, got " + JType(d[k]));
                return (bool)d[k];
            }

            static string Str1to64(Dictionary<string, object> d, string k, string at)
            {
                object v = d[k];
                if (!(v is string)) throw Refuse("type", at + "." + k, "want str, got " + JType(v));
                var s = (string)v;
                if (s.Length == 0 || s.Length > 64) throw Refuse("bad_value", at + "." + k, "want 1-64 chars");
                return s;
            }

            public Compiled CompileSpec(object specObj)
            {
                var spec = Obj(specObj, "$");
                Keys(spec, _mode == "run" ? RunKeys : EvalKeys, "$");
                string root = _mode == "run" ? "until" : "tree";
                if (!spec.ContainsKey(root)) throw Refuse("missing_key", "$", root);
                var c = new Compiled { Mode = _mode };
                _mapId = IntIn(spec, "mapId", 0, 1000000, "$", -1);
                if (_mapId < 0) _mapId = _src.CurrentMap();
                var canonical = new Dictionary<string, object> { { "mapId", (double)_mapId } };
                if (_mode == "run")
                {
                    c.MaxTicks = IntIn(spec, "max_ticks", 0, HardMaxTicks, "$", null);
                    c.Every = IntIn(spec, "every", 1, MaxEvery, "$", 1);
                    c.OnUnknown = "stop";
                    if (spec.ContainsKey("on_unknown"))
                    {
                        object v = spec["on_unknown"];
                        if (!(v is string)) throw Refuse("type", "$.on_unknown", "want str, got " + JType(v));
                        if ((string)v != "stop" && (string)v != "continue")
                            throw Refuse("bad_value", "$.on_unknown", "want stop|continue");
                        c.OnUnknown = (string)v;
                    }
                    c.RunKey = null;
                    if (spec.ContainsKey("runKey")) c.RunKey = Str1to64(spec, "runKey", "$");
                    canonical["max_ticks"] = (double)c.MaxTicks;
                    canonical["every"] = (double)c.Every;
                    canonical["on_unknown"] = c.OnUnknown;
                    canonical["runKey"] = c.RunKey;
                }
                c.Tree = CompileNode(spec[root], "$." + root, "", false);
                canonical[root] = c.Tree.Canonical;
                if (_mode == "run")
                {
                    if (spec.ContainsKey("watch"))
                    {
                        var wl = spec["watch"] as List<object>;
                        if (wl == null) throw Refuse("type", "$.watch", "want list, got " + JType(spec["watch"]));
                        if (wl.Count > MaxWatchers)
                            throw Refuse("cap_watchers", "$.watch", wl.Count + " > " + MaxWatchers);
                        var names = new HashSet<string>();
                        var cw = new List<object>();
                        for (int i = 0; i < wl.Count; i++)
                        {
                            string at = "$.watch[" + i + "]";
                            var w = Obj(wl[i], at);
                            Keys(w, new[] { "name", "tree" }, at);
                            foreach (var k in new[] { "name", "tree" })
                                if (!w.ContainsKey(k)) throw Refuse("missing_key", at, k);
                            string nm = Str1to64(w, "name", at);
                            if (names.Contains(nm)) throw Refuse("duplicate_watch", at + ".name", nm);
                            names.Add(nm);
                            var tree = CompileNode(w["tree"], at + ".tree", nm + "/", true);
                            c.Watch.Add(new Watcher(nm, tree));
                            cw.Add(new Dictionary<string, object> { { "name", nm }, { "tree", tree.Canonical } });
                        }
                        canonical["watch"] = cw;
                    }
                    if (spec.ContainsKey("sample"))
                    {
                        string at = "$.sample";
                        var s = Obj(spec["sample"], at);
                        Keys(s, new[] { "degrade", "every", "on_change_only", "probes" }, at);
                        c.SampleEvery = IntIn(s, "every", 1, MaxEvery, at, null);
                        c.SampleChangeOnly = Flag(s, "on_change_only", at);
                        bool degrade = Flag(s, "degrade", at);
                        if (!s.ContainsKey("probes")) throw Refuse("missing_key", at, "probes");
                        c.Sample = ProbeMap(s["probes"], at + ".probes");
                        canonical["sample"] = new Dictionary<string, object>
                        {
                            { "every", (double)c.SampleEvery }, { "on_change_only", c.SampleChangeOnly },
                            { "degrade", degrade }, { "probes", ProbeMapCanon(c.Sample) },
                        };
                    }
                    if (spec.ContainsKey("snapshot_on_hit"))
                    {
                        c.Snapshot = ProbeMap(spec["snapshot_on_hit"], "$.snapshot_on_hit");
                        canonical["snapshot_on_hit"] = ProbeMapCanon(c.Snapshot);
                    }
                }
                if (_nodes > MaxNodes) throw Refuse("cap_nodes", "$", _nodes + " > " + MaxNodes);
                if (_cells > MaxCells) throw Refuse("cap_cells", "$", _cells + " > " + MaxCells);
                c.Canonical = canonical;
                return c;
            }

            static Dictionary<string, object> ProbeMapCanon(List<KeyValuePair<string, Probe>> m)
            {
                var d = new Dictionary<string, object>();
                foreach (var kv in m) d[kv.Key] = kv.Value.Canonical;
                return d;
            }

            List<KeyValuePair<string, Probe>> ProbeMap(object mo, string at)
            {
                var m = Obj(mo, at);
                if (m.Count == 0) throw Refuse("bad_value", at, "want at least one probe");
                var outl = new List<KeyValuePair<string, Probe>>();
                foreach (var k in SortedKeys(m))
                {
                    if (k.Length == 0 || k.Length > 64) throw Refuse("bad_value", at, "probe names are 1-64 chars");
                    outl.Add(new KeyValuePair<string, Probe>(k, CompileProbe(m[k], at + "." + k, false)));
                }
                return outl;
            }

            static readonly Dictionary<string, string[]> NodeKeys = new Dictionary<string, string[]>
            {
                { "all", None0 }, { "any", None0 }, { "not", None0 }, { "cmp", new[] { "tol" } }, { "changed", None0 },
                { "edge", new[] { "dir" } }, { "stays", new[] { "ticks" } }, { "alarm", None0 },
            };

            Node CompileNode(object x, string at, string prefix, bool isWatchRoot)
            {
                var d = Obj(x, at);
                var kinds = new List<string>();
                foreach (var k in NodeKinds) if (d.ContainsKey(k)) kinds.Add(k);
                if (kinds.Count == 0)
                    throw Refuse("unknown_node", at, "no node kind among: " + string.Join(",", SortedKeys(d).ToArray()));
                if (kinds.Count > 1) throw Refuse("unknown_node", at, "two node kinds: " + string.Join(",", kinds.ToArray()));
                string kind = kinds[0];
                var allowed = new List<string> { kind, "id", "optional" };
                allowed.AddRange(NodeKeys[kind]);
                Keys(d, allowed, at);
                _nodes++;
                string nid = prefix + "n" + _idn.ToString(CultureInfo.InvariantCulture);
                _idn++;
                if (d.ContainsKey("id")) nid = Str1to64(d, "id", at);
                if (_ids.Contains(nid)) throw Refuse("duplicate_id", at, nid);
                _ids.Add(nid);
                var n = new Node(kind, nid);
                n.Optional = Flag(d, "optional", at);
                object body = d[kind];
                var cd = new Dictionary<string, object> { { "id", nid } };
                if (n.Optional) cd["optional"] = true;
                string sub = at + "." + kind;
                if (kind == "all" || kind == "any")
                {
                    var bl = body as List<object>;
                    if (bl == null) throw Refuse("type", sub, "want list, got " + JType(body));
                    if (bl.Count == 0) throw Refuse("empty_children", sub, kind);
                    var cc = new List<object>();
                    for (int i = 0; i < bl.Count; i++)
                    {
                        var ch = CompileNode(bl[i], sub + "[" + i + "]", prefix, false);
                        n.Children.Add(ch);
                        cc.Add(ch.Canonical);
                    }
                    cd[kind] = cc;
                }
                else if (kind == "not" || kind == "edge" || kind == "stays" || kind == "alarm")
                {
                    if (kind == "alarm" && !isWatchRoot) throw Refuse("alarm_not_root", at, "alarm is a watch root only");
                    n.Children.Add(CompileNode(body, sub, prefix, false));
                    cd[kind] = n.Children[0].Canonical;
                    if (kind == "edge")
                    {
                        if (d.ContainsKey("dir"))
                        {
                            if (!(d["dir"] is string)) throw Refuse("type", at + ".dir", "want str, got " + JType(d["dir"]));
                            var dir = (string)d["dir"];
                            if (dir != "rise" && dir != "fall") throw Refuse("bad_value", at + ".dir", "want rise|fall");
                            n.Dir = dir;
                        }
                        cd["dir"] = n.Dir;
                    }
                    if (kind == "stays")
                    {
                        n.Ticks = IntIn(d, "ticks", 0, HardMaxTicks, at, null);
                        cd["ticks"] = (double)n.Ticks;
                    }
                }
                else if (kind == "changed")
                {
                    n.Probe = CompileProbe(body, sub, true);
                    cd[kind] = n.Probe.Canonical;
                }
                else if (kind == "cmp")
                {
                    var bl = body as List<object>;
                    if (bl == null) throw Refuse("type", sub, "want list, got " + JType(body));
                    if (bl.Count != 3) throw Refuse("bad_value", sub, "cmp is [probe, op, value]");
                    n.Probe = CompileProbe(bl[0], sub + "[0]", true);
                    object op = bl[1];
                    if (!(op is string)) throw Refuse("type", sub + "[1]", "want str, got " + JType(op));
                    if (!In(Ops, (string)op)) throw Refuse("cmp_op", sub + "[1]", (string)op);
                    n.Op = (string)op;
                    n.Lit = Literal(n.Probe, n.Op, bl[2], sub + "[2]");
                    cd[kind] = new List<object> { n.Probe.Canonical, n.Op, n.Lit };
                    if (d.ContainsKey("tol"))
                    {
                        object t = d["tol"];
                        if (!IsNum(t)) throw Refuse("type", at + ".tol", "want num, got " + JType(t));
                        if (Num(t) < 0) throw Refuse("bad_value", at + ".tol", "want >= 0");
                        if (n.Op != "==" && n.Op != "!=") throw Refuse("cmp_op", at + ".tol", "tol applies to == and != only");
                        string vt = n.Probe.VType();
                        if (vt != "num" && vt != "any") throw Refuse("cmp_type", at + ".tol", "tol needs a number probe");
                        n.HasTol = true;
                        n.Tol = Num(t);
                        cd["tol"] = t;
                    }
                }
                n.Canonical = cd;
                return n;
            }

            static object Literal(Probe p, string op, object lit, string at)
            {
                string vt = p.VType();
                if (op == "in" || op == "hour_in")
                {
                    var l = lit as List<object>;
                    if (!(l != null && l.Count == 2 && IsNum(l[0]) && IsNum(l[1])))
                        throw Refuse("cmp_type", at, op + " wants [num, num]");
                    if (vt != "num" && vt != "any") throw Refuse("cmp_type", at, op + " needs a number probe, got " + vt);
                    if (op == "in" && Num(l[0]) > Num(l[1])) throw Refuse("bad_value", at, "in [a,b] wants a <= b");
                    return lit;
                }
                if (op == "<" || op == "<=" || op == ">" || op == ">=")
                {
                    if (!IsNum(lit)) throw Refuse("cmp_type", at, op + " wants num, got " + JType(lit));
                    if (vt != "num" && vt != "any") throw Refuse("cmp_type", at, op + " needs a number probe, got " + vt);
                    return lit;
                }
                string lt = JType(lit);
                if (lt != "num" && lt != "bool" && lt != "str") throw Refuse("cmp_type", at, "want num|bool|str, got " + lt);
                if (vt != "any" && lt != vt) throw Refuse("cmp_type", at, "probe is " + vt + ", value is " + lt);
                return lit;
            }

            static int[] Ints(List<object> l)
            {
                var a = new int[l.Count];
                for (int i = 0; i < a.Length; i++) a[i] = (int)Num(l[i]);
                return a;
            }

            Probe CompileProbe(object x, string at, bool counts)
            {
                var d = Obj(x, at);
                if (!d.ContainsKey("p")) throw Refuse("missing_key", at, "p");
                object no = d["p"];
                if (!(no is string)) throw Refuse("type", at + ".p", "want str, got " + JType(no));
                string name = (string)no;
                ProbeInfo info;
                if (!Probes.TryGetValue(name, out info))
                {
                    if (name.StartsWith("pawn.flight.", StringComparison.Ordinal) || name.StartsWith("pawn.anim.", StringComparison.Ordinal)
                        || name == "static.call")
                        throw Refuse("probe_not_in_v1", at + ".p", name);
                    throw Refuse("unknown_probe", at + ".p", name);
                }
                bool spatial = In(Spatial, name);
                var allowed = new List<string> { "p", "mapId" };
                allowed.AddRange(info.Req);
                allowed.AddRange(info.Opt);
                if (spatial) allowed.AddRange(new[] { "cell", "rect", "reduce", "where" });
                Keys(d, allowed, at);
                foreach (var k in info.Req) if (!d.ContainsKey(k)) throw Refuse("missing_arg", at, k);
                if (counts) _nodes++;
                var p = new Probe { Name = name, PType = info.Type, MapId = _mapId };
                foreach (var k in ArgOrder)
                {
                    if (!d.ContainsKey(k)) continue;
                    object v = d[k];
                    string ak = at + "." + k;
                    if (k == "cell" || k == "rect")
                    {
                        int n = k == "cell" ? 2 : 4;
                        var l = v as List<object>;
                        bool ok = l != null && l.Count == n;
                        if (ok) foreach (var c in l) if (!IsInt(c)) ok = false;
                        if (!ok) throw Refuse("bad_arg", ak, "want " + n + " integers");
                        if (k == "cell") p.Cell = Ints(l); else p.Rect = Ints(l);
                    }
                    else if (k == "reduce")
                    {
                        if (!(v is string)) throw Refuse("type", ak, "want str, got " + JType(v));
                        if (!In(Reducers, (string)v)) throw Refuse("reduce_bad", ak, (string)v);
                        p.Reduce = (string)v;
                    }
                    else if (k == "where")
                    {
                        var l = v as List<object>;
                        if (!(l != null && l.Count == 2 && l[0] is string)) throw Refuse("bad_arg", ak, "want [op, value]");
                        if (!In(WhereOps, (string)l[0])) throw Refuse("cmp_op", ak, (string)l[0]);
                        p.WhereOp = (string)l[0];
                        p.WhereLit = l[1];
                        p.HasWhere = true;
                    }
                    else if (k == "mapId")
                    {
                        if (!IsInt(v) || Num(v) < 0) throw Refuse("bad_arg", ak, "want integer >= 0");
                        p.MapId = (int)Num(v);
                    }
                    else if (k == "f")
                    {
                        var fv = FValues[name];
                        if (!(v is string) || !In(fv, (string)v)) throw Refuse("bad_arg", ak, "want one of " + string.Join("|", fv));
                        p.Args[k] = v;
                    }
                    else if (k == "path")
                    {
                        var s = v as string;
                        if (string.IsNullOrEmpty(s)) throw Refuse("bad_arg", ak, "want a field path");
                        if (s.IndexOf('(') >= 0 || s.IndexOf(')') >= 0)
                            throw Refuse("field_method", ak, "fields and properties only: " + s);
                        p.Args[k] = v;
                    }
                    else if (k == "source")
                    {
                        if (!(v is string) || !In(RingSources, (string)v))
                            throw Refuse("bad_arg", ak, "want one of " + string.Join("|", RingSources));
                        p.Args[k] = v;
                    }
                    else
                    {
                        var s = v as string;
                        if (string.IsNullOrEmpty(s)) throw Refuse("bad_arg", ak, "want a non-empty string");
                        p.Args[k] = v;
                    }
                }
                int sx, sz;
                bool sized = _src.MapSize(p.MapId, out sx, out sz);
                if (spatial)
                {
                    if ((p.Cell == null) == (p.Rect == null)) throw Refuse("bad_arg", at, "want exactly one of cell, rect");
                    if (p.Cell != null && (p.Reduce != null || p.HasWhere)) throw Refuse("reduce_bad", at, "reduce and where need a rect");
                    if (p.Rect != null) CheckRectReduce(p, at);
                }
                if (p.Cell != null || p.Rect != null || name == "map.sky_glow" || name == "map.count")
                    if (!sized) throw Refuse("map_unknown", at, "mapId " + p.MapId);
                if (p.Cell != null)
                {
                    int cx = p.Cell[0], cz = p.Cell[1];
                    if (!(0 <= cx && cx < sx && 0 <= cz && cz < sz))
                        throw Refuse("cell_oob", at + ".cell", cx + "," + cz + " outside " + sx + "x" + sz);
                }
                if (p.Rect != null)
                {
                    int rx = p.Rect[0], rz = p.Rect[1], w = p.Rect[2], h = p.Rect[3];
                    if (w <= 0 || h <= 0) throw Refuse("rect_empty", at + ".rect", w + "x" + h);
                    if (!(0 <= rx && 0 <= rz && (long)rx + w <= sx && (long)rz + h <= sz))
                        throw Refuse("cell_oob", at + ".rect", rx + "," + rz + "," + w + "," + h + " outside " + sx + "x" + sz);
                    if (spatial) _cells += w * h;
                }
                var cd = new Dictionary<string, object> { { "p", name } };
                foreach (var kv in p.Args) cd[kv.Key] = kv.Value;
                if (p.Cell != null) cd["cell"] = IntList(p.Cell);
                if (p.Rect != null) cd["rect"] = IntList(p.Rect);
                if (p.Reduce != null) cd["reduce"] = p.Reduce;
                if (p.HasWhere) cd["where"] = new List<object> { p.WhereOp, p.WhereLit };
                if (spatial || name == "map.sky_glow" || name == "map.count") cd["mapId"] = (double)p.MapId;
                p.Canonical = cd;
                var key = new StringBuilder(name);
                foreach (var k in SortedKeys(p.Args)) key.Append(' ').Append(k).Append('=').Append(KeyVal(p.Args[k]));
                if (p.Cell != null) key.Append(" cell=").Append(KeyVal(p.Cell));
                if (p.Rect != null) key.Append(" rect=").Append(KeyVal(p.Rect));
                p.Key = key.ToString();
                string why = _src.Refuse(p.Key, p);
                if (!string.IsNullOrEmpty(why)) throw Refuse("bind", at, why);
                return p;
            }

            static void CheckRectReduce(Probe p, string at)
            {
                if (p.Reduce == null) throw Refuse("reduce_bad", at, "a rect needs reduce");
                if (p.Reduce == "max" || p.Reduce == "min")
                {
                    if (p.PType != "num") throw Refuse("reduce_bad", at, p.Reduce + " needs a number probe");
                    if (p.HasWhere) throw Refuse("reduce_bad", at, p.Reduce + " takes no where");
                    return;
                }
                if (!p.HasWhere)
                {
                    if (p.PType != "bool") throw Refuse("reduce_bad", at, p.Reduce + " over a non-bool probe needs where");
                    p.WhereOp = "==";
                    p.WhereLit = true;
                    p.HasWhere = true;
                    return;
                }
                string lt = JType(p.WhereLit);
                if (p.WhereOp == "<" || p.WhereOp == "<=" || p.WhereOp == ">" || p.WhereOp == ">=")
                {
                    if (p.PType != "num" || lt != "num") throw Refuse("cmp_type", at + ".where", "ordered where needs num");
                }
                else if (lt != p.PType)
                    throw Refuse("cmp_type", at + ".where", "probe is " + p.PType + ", value is " + lt);
            }
        }

        // ============================================================================================ evaluation
        /// <summary>Three-valued node result: V is null (UNKNOWN), true or false.</summary>
        internal struct Tri
        {
            public bool? V; public string Status, Detail;
            public Tri(bool? v, string st, string de) { V = v; Status = st; Detail = de ?? ""; }
        }

        internal static Dictionary<string, object> Rec(object v, string status, string detail)
        {
            var r = new Dictionary<string, object> { { "v", v }, { "status", status } };
            if (status != "ok") r["detail"] = detail;
            return r;
        }

        internal sealed class Evaluator
        {
            readonly IProbeSource _src;
            public int Reads, NodeEvals;
            public string FirstError;
            readonly Dictionary<string, CondRead> _ringBase = new Dictionary<string, CondRead>();

            public Evaluator(IProbeSource src) { _src = src; }

            CondRead Raw(string key, Probe p, int x, int z, string ptype)
            {
                Reads++;
                CondRead g = _src.Read(key, p, x, z);
                if (!In(Statuses, g.Status)) return new CondRead(null, "error", "bad status " + (g.Status ?? "None"));
                if (g.Status != "ok") return new CondRead(null, g.Status, g.Detail);
                string t = JType(g.V);
                if (ptype == "any")
                {
                    if (t != "num" && t != "bool" && t != "str") return new CondRead(null, "error", "type: got " + t);
                }
                else if (t != ptype) return new CondRead(null, "error", "type: want " + ptype + ", got " + t);
                return new CondRead(g.V, "ok", "");
            }

            public void ArmRings(List<Probe> probes)
            {
                foreach (var p in probes)
                    if (p.Name == "ring.count" && !_ringBase.ContainsKey(p.Key)) _ringBase[p.Key] = Raw(p.Key, p, -1, -1, "num");
            }

            public CondRead ReadProbe(Probe p)
            {
                if (p.Rect != null && In(Spatial, p.Name))
                {
                    int x0 = p.Rect[0], z0 = p.Rect[1], w = p.Rect[2], h = p.Rect[3];
                    var vals = new List<object>();
                    bool bad = false;
                    CondRead first = default(CondRead);
                    for (int z = z0; z < z0 + h; z++)
                        for (int x = x0; x < x0 + w; x++)
                        {
                            var r = Raw(p.CellKey(x, z), p, x, z, p.PType);
                            if (r.Status != "ok" && !bad) { bad = true; first = r; }
                            vals.Add(r.V);
                        }
                    if (bad) return new CondRead(null, first.Status, first.Detail);
                    if (p.Reduce == "max" || p.Reduce == "min")
                    {
                        double m = Num(vals[0]);
                        foreach (var v in vals) m = p.Reduce == "max" ? Math.Max(m, Num(v)) : Math.Min(m, Num(v));
                        return new CondRead(m, "ok", "");
                    }
                    int hits = 0;
                    foreach (var v in vals) if (CmpValue(v, p.WhereOp, p.WhereLit, false, 0)) hits++;
                    if (p.Reduce == "any") return new CondRead(hits > 0, "ok", "");
                    if (p.Reduce == "all") return new CondRead(hits == vals.Count, "ok", "");
                    return new CondRead((double)hits, "ok", "");
                }
                var rr = Raw(p.Key, p, p.Cell != null ? p.Cell[0] : -1, p.Cell != null ? p.Cell[1] : -1, p.VType());
                if (p.Name == "ring.count" && rr.Status == "ok")
                {
                    CondRead b;
                    if (!_ringBase.TryGetValue(p.Key, out b)) return new CondRead(null, "error", "ring not armed");
                    if (b.Status != "ok") return new CondRead(null, b.Status, "at arm: " + b.Detail);
                    return new CondRead(Num(rr.V) - Num(b.V), "ok", "");
                }
                return rr;
            }

            Tri EvalNode(Node n, long tick, List<object> outl)
            {
                NodeEvals++;
                var r = new Dictionary<string, object> { { "id", n.Id } };
                outl.Add(r);
                object pv = null;
                bool? v;
                string st, de;
                if (n.Kind == "all" || n.Kind == "any")
                {
                    var res = new List<Tri>();
                    foreach (var c in n.Children) res.Add(EvalNode(c, tick, outl));
                    var k = Kleene(n.Kind, res);
                    v = k.V; st = k.Status; de = k.Detail;
                }
                else if (n.Kind == "not")
                {
                    var c = EvalNode(n.Children[0], tick, outl);
                    st = c.Status; de = c.Detail;
                    v = c.V == null ? (bool?)null : !c.V.Value;
                }
                else if (n.Kind == "alarm")
                {
                    var c = EvalNode(n.Children[0], tick, outl);
                    v = c.V; st = c.Status; de = c.Detail;
                }
                else if (n.Kind == "cmp")
                {
                    var rd = ReadProbe(n.Probe);
                    pv = rd.V; st = rd.Status; de = rd.Detail;
                    if (st == "ok")
                    {
                        var k = CmpChecked(pv, n.Op, n.Lit, n.HasTol, n.Tol);
                        v = k.V; st = k.Status; de = k.Detail;
                    }
                    else v = null;
                    NoteError(st, de);
                }
                else if (n.Kind == "changed")
                {
                    var rd = ReadProbe(n.Probe);
                    pv = rd.V; st = rd.Status; de = rd.Detail;
                    NoteError(st, de);
                    if (st != "ok")
                    {
                        v = null;
                        n.HasPrev = false;
                    }
                    else
                    {
                        v = n.HasPrev && !SameValue(pv, n.Prev);
                        n.HasPrev = true;
                        n.Prev = pv;
                    }
                }
                else if (n.Kind == "edge")
                {
                    var c = EvalNode(n.Children[0], tick, outl);
                    st = c.Status; de = c.Detail;
                    if (c.V == null)
                    {
                        v = null;
                        n.HasPrev = false;
                    }
                    else
                    {
                        if (!n.HasPrev) v = false;
                        else if (n.Dir == "rise") v = (bool)n.Prev == false && c.V.Value;
                        else v = (bool)n.Prev && !c.V.Value;
                        n.HasPrev = true;
                        n.Prev = c.V.Value;
                    }
                }
                else if (n.Kind == "stays")
                {
                    var c = EvalNode(n.Children[0], tick, outl);
                    st = c.Status; de = c.Detail;
                    if (c.V == true)
                    {
                        if (!n.HasStart) { n.HasStart = true; n.Start = tick; }
                        v = (tick - n.Start) >= n.Ticks;
                    }
                    else
                    {
                        n.HasStart = false;
                        v = c.V;
                    }
                }
                else throw new InvalidOperationException(n.Kind);
                if (v != null) { st = "ok"; de = ""; }
                else if (n.Optional) { v = false; de = st + ": " + de; st = "ignored"; }
                r["v"] = v;
                r["status"] = st;
                if (st != "ok") r["detail"] = de;
                if (n.Kind == "cmp" || n.Kind == "changed") r["pv"] = pv;
                return new Tri(v, st, de);
            }

            void NoteError(string st, string de)
            {
                if (st == "error" && FirstError == null) FirstError = de;
            }

            public Tri Evaluate(Node tree, long tick, out List<object> records)
            {
                records = new List<object>();
                FirstError = null;
                var t = EvalNode(tree, tick, records);
                if (t.Status == "ignored") t.Status = "ok";
                return t;
            }
        }

        static Tri Kleene(string kind, List<Tri> res)
        {
            bool want = kind == "any";
            foreach (var t in res) if (t.V == want) return new Tri(want, "ok", "");
            foreach (var t in res) if (t.V == null) return new Tri(null, t.Status, t.Detail);
            return new Tri(!want, "ok", "");
        }

        static bool SameValue(object a, object b)
        {
            if (JType(a) != JType(b)) return false;
            if (IsNum(a)) return Num(a) == Num(b);
            return Equals(a, b);
        }

        static bool CmpValue(object v, string op, object lit, bool hasTol, double tol)
        {
            if (op == "==" || op == "!=")
            {
                bool eq;
                if (IsNum(v) && IsNum(lit)) eq = Math.Abs(Num(v) - Num(lit)) <= (hasTol ? tol : 0.0);
                else eq = JType(v) == JType(lit) && Equals(v, lit);
                return op == "==" ? eq : !eq;
            }
            if (op == "in")
            {
                var l = (List<object>)lit;
                return Num(l[0]) <= Num(v) && Num(v) <= Num(l[1]);
            }
            if (op == "hour_in")
            {
                var l = (List<object>)lit;
                double a = Num(l[0]), b = Num(l[1]), x = Num(v);
                return a <= b ? (a <= x && x < b) : (x >= a || x < b);
            }
            double vv = Num(v), ll = Num(lit);
            if (op == "<") return vv < ll;
            if (op == "<=") return vv <= ll;
            if (op == ">") return vv > ll;
            return vv >= ll;
        }

        static Tri CmpChecked(object v, string op, object lit, bool hasTol, double tol)
        {
            if (op != "==" && op != "!=" && !IsNum(v))
                return new Tri(null, "error", "type: " + op + " needs num, got " + JType(v));
            if ((op == "==" || op == "!=") && JType(v) != JType(lit))
                return new Tri(null, "error", "type: value is " + JType(v) + ", literal is " + JType(lit));
            return new Tri(CmpValue(v, op, lit, hasTol, tol), "ok", "");
        }

        static List<Probe> AllProbes(Compiled c)
        {
            var outl = new List<Probe>();
            Action<Node> walk = null;
            walk = n => { if (n.Probe != null) outl.Add(n.Probe); foreach (var ch in n.Children) walk(ch); };
            walk(c.Tree);
            foreach (var w in c.Watch) walk(w.Tree);
            if (c.Sample != null) foreach (var kv in c.Sample) outl.Add(kv.Value);
            if (c.Snapshot != null) foreach (var kv in c.Snapshot) outl.Add(kv.Value);
            return outl;
        }

        static List<Node> WalkNodes(Compiled c)
        {
            var outl = new List<Node>();
            Action<Node> walk = null;
            walk = n => { outl.Add(n); foreach (var ch in n.Children) walk(ch); };
            walk(c.Tree);
            foreach (var w in c.Watch) walk(w.Tree);
            return outl;
        }

        static Dictionary<string, object> FirstUnknown(List<object> records)
        {
            foreach (var o in records)
            {
                var r = (Dictionary<string, object>)o;
                var st = (string)r["status"];
                if (r.ContainsKey("pv") && st != "ok" && st != "ignored") return r;
            }
            return records.Count > 0 ? (Dictionary<string, object>)records[0] : null;
        }

        /// <summary>One armed run over end-of-tick frames: the pure half of jawa/safe_advance + until.</summary>
        internal sealed class CondRun
        {
            readonly Compiled _c;
            readonly Evaluator _ev;
            readonly Func<double> _clockMs;
            public string State = "running";
            public long? HitTick;
            List<object> _values = new List<object>(), _atArm = new List<object>();
            bool _trueAtArm;
            long _tickFrom, _tickTo;
            object _epoch;
            List<object> _triggers = new List<object>();
            int _evals;
            readonly List<object> _gaps = new List<object>();
            List<object> _gapOpen;
            Dictionary<string, object> _unknown;
            readonly List<object> _events = new List<object>();
            int _seq;
            readonly List<object> _rows = new List<object>();
            int _dropped;
            Dictionary<string, object> _lastRow;
            Dictionary<string, object> _snapshot;
            double _msTotal, _msMax;

            public CondRun(Compiled c, IProbeSource src, Func<double> clockMs)
            {
                _c = c;
                _ev = new Evaluator(src);
                _clockMs = clockMs;
            }

            Tri Timed(Node tree, long tick, out List<object> recs)
            {
                double t0 = _clockMs != null ? _clockMs() : 0.0;
                var t = _ev.Evaluate(tree, tick, out recs);
                if (_clockMs != null)
                {
                    double ms = _clockMs() - t0;
                    _msTotal += ms;
                    _msMax = Math.Max(_msMax, ms);
                }
                return t;
            }

            Tri EvalUntil(long tick)
            {
                List<object> recs;
                var t = Timed(_c.Tree, tick, out recs);
                _evals++;
                _values = recs;
                if (t.V == null)
                {
                    if (_gapOpen == null)
                    {
                        _gapOpen = new List<object> { (double)tick, (double)tick };
                        _gaps.Add(_gapOpen);
                    }
                    else _gapOpen[1] = (double)tick;
                }
                else _gapOpen = null;
                return t;
            }

            void EvalWatch(long tick)
            {
                foreach (var w in _c.Watch)
                {
                    if (w.Disarmed != null) continue;
                    List<object> recs;
                    var t = Timed(w.Tree, tick, out recs);
                    if (_ev.FirstError != null)
                    {
                        w.Disarmed = new Dictionary<string, object> { { "tick", (double)tick }, { "why", "error: " + _ev.FirstError } };
                        continue;
                    }
                    if (t.V == null) { w.Unknowns++; continue; }
                    if (t.V.Value)
                    {
                        _seq++;
                        w.Events++;
                        var ev = new Dictionary<string, object>
                        {
                            { "name", w.Name }, { "seq", (double)_seq }, { "tick", (double)tick }, { "values", recs },
                        };
                        if (w.Tree.Kind == "alarm")
                        {
                            ev["alarm"] = true;
                            w.Disarmed = new Dictionary<string, object> { { "tick", (double)tick }, { "why", "alarm" } };
                        }
                        _events.Add(ev);
                    }
                }
            }

            void TakeSample(long k, long tick)
            {
                if (_c.Sample == null || k % _c.SampleEvery != 0) return;
                var vals = new Dictionary<string, object>();
                foreach (var kv in _c.Sample)
                {
                    var r = _ev.ReadProbe(kv.Value);
                    vals[kv.Key] = Rec(r.V, r.Status, r.Detail);
                }
                if (_c.SampleChangeOnly && _lastRow != null && Canon(vals) == Canon(_lastRow)) return;
                _lastRow = vals;
                if (_rows.Count >= MaxSampleRows) { _dropped++; return; }
                _rows.Add(new Dictionary<string, object> { { "tick", (double)tick }, { "values", vals } });
            }

            void TakeSnapshot()
            {
                if (_c.Snapshot == null) return;
                _snapshot = new Dictionary<string, object>();
                foreach (var kv in _c.Snapshot)
                {
                    var r = _ev.ReadProbe(kv.Value);
                    _snapshot[kv.Key] = Rec(r.V, r.Status, r.Detail);
                }
            }

            Dictionary<string, object> DescribeUnknown(string st, string de)
            {
                var r = FirstUnknown(_values);
                return new Dictionary<string, object> { { "id", r != null ? r["id"] : null }, { "status", st }, { "detail", de } };
            }

            /// <summary>Arm on the frame of the tick the run starts at (evaluation k = 0).</summary>
            public void Arm(long tick, object epoch)
            {
                _tickFrom = _tickTo = tick;
                _epoch = epoch;
                foreach (var n in WalkNodes(_c)) n.Reset();
                _ev.ArmRings(AllProbes(_c));
                var t = EvalUntil(tick);
                _atArm = _values;
                EvalWatch(tick);
                TakeSample(0, tick);
                if (t.V == true)
                {
                    State = "hit"; HitTick = tick; _trueAtArm = true;
                    _triggers = new List<object> { "cond" };
                    TakeSnapshot();
                }
                else if (t.V == null && _c.OnUnknown == "stop")
                {
                    State = "unknown";
                    _triggers = new List<object> { "unknown" };
                    _unknown = DescribeUnknown(t.Status, t.Detail);
                }
                else if (_c.MaxTicks == 0)
                {
                    State = "done";
                    _triggers = new List<object> { "deadline" };
                }
            }

            /// <summary>The end of one tick. `stop` is a safety latch kind that fired on this tick, or null.</summary>
            public void Step(long tick, object epoch, string stop)
            {
                if (State != "running") return;
                if (tick != _tickTo + 1)
                {
                    State = "error";
                    _triggers = new List<object> { "tick_gap" };
                    return;
                }
                _tickTo = tick;
                if (!SameValue(epoch, _epoch))
                {
                    State = "epoch";
                    _triggers = new List<object> { "epoch" };
                    return;
                }
                long k = tick - _tickFrom;
                bool hit = false, unk = false;
                Tri t = default(Tri);
                if (k % _c.Every == 0 || k == _c.MaxTicks)
                {
                    t = EvalUntil(tick);
                    EvalWatch(tick);
                    hit = t.V == true;
                    unk = t.V == null && _c.OnUnknown == "stop";
                }
                TakeSample(k, tick);
                var trig = new List<object>();
                if (hit)
                {
                    trig.Add("cond");
                    HitTick = tick;
                    TakeSnapshot();
                }
                if (unk)
                {
                    trig.Add("unknown");
                    _unknown = DescribeUnknown(t.Status, t.Detail);
                }
                if (!string.IsNullOrEmpty(stop))
                {
                    trig.Add(stop);
                    State = "stopped";
                }
                else if (hit) State = "hit";
                else if (unk) State = "unknown";
                else if (k >= _c.MaxTicks)
                {
                    State = "done";
                    trig.Add("deadline");
                }
                _triggers = trig;
            }

            public void EndOfSeries()
            {
                if (State == "running")
                {
                    State = "stopped";
                    _triggers = new List<object> { "series_end" };
                }
            }

            public Dictionary<string, object> Result()
            {
                var watchers = new List<object>();
                foreach (var w in _c.Watch)
                    watchers.Add(new Dictionary<string, object>
                    {
                        { "name", w.Name }, { "events", (double)w.Events }, { "unknowns", (double)w.Unknowns },
                        { "disarmed", w.Disarmed },
                    });
                return new Dictionary<string, object>
                {
                    { "runKey", _c.RunKey }, { "state", State }, { "hitTick", HitTick.HasValue ? (object)(double)HitTick.Value : null },
                    { "values", _values }, { "atArm", _atArm }, { "trueAtArm", _trueAtArm },
                    { "executed", (double)(_tickTo - _tickFrom) }, { "tickFrom", (double)_tickFrom }, { "tickTo", (double)_tickTo },
                    { "epoch", _epoch }, { "triggers", _triggers }, { "unknown", _unknown },
                    { "coverage", new Dictionary<string, object>
                        {
                            { "every", (double)_c.Every }, { "evals", (double)_evals }, { "resolutionTicks", (double)_c.Every },
                            { "gaps", _gaps }, { "complete", _gaps.Count == 0 },
                        } },
                    { "cost", new Dictionary<string, object>
                        {
                            { "evals", (double)_evals }, { "nodeEvals", (double)_ev.NodeEvals }, { "reads", (double)_ev.Reads },
                            { "evalMsTotal", Math.Round(_msTotal, 3) }, { "evalMsMax", Math.Round(_msMax, 3) },
                        } },
                    { "watch", _events }, { "watchers", watchers }, { "sample", _rows }, { "sampleDropped", (double)_dropped },
                    { "snapshot", _snapshot }, { "mutations", new List<object>() }, { "canonical", _c.Canonical },
                };
            }
        }

        internal static Dictionary<string, object> Refusal(CondRefused e)
        {
            return new Dictionary<string, object> { { "refused", e.Name }, { "at", e.At }, { "detail", e.Detail } };
        }

        /// <summary>Parse a wire spec; a text that is not strict JSON is the `json` refusal.</summary>
        internal static object ParseSpec(string text)
        {
            try { return ParseJson(text); }
            catch (FormatException) { throw Refuse("json", "$", "parse error"); }
            catch (OverflowException) { throw Refuse("json", "$", "parse error"); }
        }

        /// <summary>jawa/cond_eval: compile {tree, mapId?} and evaluate once, no tick.</summary>
        internal static Dictionary<string, object> CondEval(object spec, IProbeSource src)
        {
            Compiled c;
            try { c = new Compiler(src, "eval").CompileSpec(spec); }
            catch (CondRefused e) { return Refusal(e); }
            var ev = new Evaluator(src);
            ev.ArmRings(AllProbes(c));
            List<object> recs;
            var t = ev.Evaluate(c.Tree, 0, out recs);
            return new Dictionary<string, object>
            {
                { "canonical", c.Canonical }, { "v", t.V.HasValue ? (object)t.V.Value : null }, { "status", t.Status },
                { "values", recs },
                { "cost", new Dictionary<string, object> { { "nodeEvals", (double)ev.NodeEvals }, { "reads", (double)ev.Reads } } },
            };
        }

        /// <summary>The offline run: spec over a vector series (the twin of conds.evaluate).</summary>
        internal static Dictionary<string, object> EvaluateSeries(object spec, CondSeries series, string mode)
        {
            if (mode == "eval") return CondEval(spec, series);
            Compiled c;
            try { c = new Compiler(series, "run").CompileSpec(spec); }
            catch (CondRefused e) { return Refusal(e); }
            var r = new CondRun(c, series, null);
            series.Goto(0);
            var f0 = series.Frame(0);
            r.Arm(series.Tick(f0), series.Epoch(f0));
            for (int i = 1; i < series.Count; i++)
            {
                if (r.State != "running") break;
                series.Goto(i);
                var f = series.Frame(i);
                r.Step(series.Tick(f), series.Epoch(f), f.ContainsKey("stop") ? f["stop"] as string : null);
            }
            r.EndOfSeries();
            return r.Result();
        }

        // ============================================================================================ vectors
        /// <summary>IProbeSource over a vector's frames: reads carry forward; a key never given reads status error.</summary>
        internal sealed class CondSeries : IProbeSource
        {
            readonly bool _sized;
            readonly int _sx, _sz, _curMap;
            readonly Dictionary<string, object> _refusals;
            readonly List<object> _frames;
            readonly Dictionary<string, object> _state = new Dictionary<string, object>();
            int _at = -1;

            public CondSeries(Dictionary<string, object> vec)
            {
                if (vec.ContainsKey("map"))
                {
                    var m = vec["map"] as List<object>;
                    _sized = m != null;
                    if (_sized) { _sx = (int)Num(m[0]); _sz = (int)Num(m[1]); }
                }
                else { _sized = true; _sx = 250; _sz = 250; }
                _curMap = vec.ContainsKey("mapId") ? (int)Num(vec["mapId"]) : 0;
                _refusals = vec.ContainsKey("refuse") ? (Dictionary<string, object>)vec["refuse"] : new Dictionary<string, object>();
                var fr = vec.ContainsKey("frames") ? vec["frames"] as List<object> : null;
                _frames = fr != null && fr.Count > 0 ? fr : new List<object> { new Dictionary<string, object> { { "tick", 0.0 } } };
            }

            public int Count { get { return _frames.Count; } }
            public Dictionary<string, object> Frame(int i) { return (Dictionary<string, object>)_frames[i]; }
            public long Tick(Dictionary<string, object> f) { return (long)Num(f["tick"]); }
            public object Epoch(Dictionary<string, object> f) { return f.ContainsKey("epoch") ? f["epoch"] : (object)0.0; }

            public int CurrentMap() { return _curMap; }
            public bool MapSize(int mapId, out int x, out int z)
            {
                x = _sx; z = _sz;
                return _sized && mapId == _curMap;
            }
            public string Refuse(string key, Probe p) { object v; return _refusals.TryGetValue(key, out v) ? v as string : null; }

            public void Goto(int i)
            {
                while (_at < i)
                {
                    _at++;
                    var f = Frame(_at);
                    if (!f.ContainsKey("reads")) continue;
                    var reads = (Dictionary<string, object>)f["reads"];
                    foreach (var k in SortedKeys(reads)) _state[k] = reads[k];
                }
            }

            public CondRead Read(string key, Probe p, int x, int z)
            {
                object v;
                if (!_state.TryGetValue(key, out v) || v == null) return new CondRead(null, "error", "no series value for " + key);
                var l = (List<object>)v;
                return new CondRead(l[0], l[1] as string, l.Count > 2 ? l[2] as string : "");
            }
        }

        internal static Dictionary<string, object> RunVector(Dictionary<string, object> vec)
        {
            object spec;
            if (vec.ContainsKey("spec_text"))
            {
                try { spec = ParseSpec((string)vec["spec_text"]); }
                catch (CondRefused e) { return Refusal(e); }
            }
            else spec = vec["spec"];
            var src = new CondSeries(vec);
            string mode = vec.ContainsKey("mode") ? (string)vec["mode"] : "run";
            if (mode == "eval") src.Goto(0);
            return EvaluateSeries(spec, src, mode);
        }

        /// <summary>The vector output both twins print: one "name\tcanonical result\n" line per vector.</summary>
        internal static string RunVectorsText(string text)
        {
            var doc = (Dictionary<string, object>)ParseJson(text);
            var sb = new StringBuilder();
            foreach (var o in (List<object>)doc["vectors"])
            {
                var vec = (Dictionary<string, object>)o;
                sb.Append((string)vec["name"]).Append('\t').Append(Canon(RunVector(vec))).Append('\n');
            }
            return sb.ToString();
        }
    }
}
