// JawaBenchPathCore.cs - the value paths of BRIDGE v2.0: parse a path, walk it by reflection, say how it ended. PURE (no Verse,
// no Unity, no Harmony). Page: design/specs/2026-11-23-bridge-v2-hands/boundary.md (the grammar, the states, the promises).
// Item RIMMANDRAKE_WIDEN_SLICE_INTO_RUN_UNTIL_AND_ACT_BATCH. One evaluator serves jawa/read_paths, the tracks of jawa/run_until
// and the `value` probe of a condition.
//
// A walk calls no method. A field is read. A property is read as the field its getter returns (the getter is not called), or
// its getter is called when a person reviewed it (Reviewed). Anything else is PATH_CALLS_METHOD.
//
// Compiled into bridgetools/RunUntilSelfTest as well: a `using Verse;` here breaks that build, which is the guard rail.
using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.Reflection;
using System.Text;

namespace JawaBench.BridgeTools
{
    /// <summary>One read. State: ok | gone | unbound | error. Refused: the refusal's name, when the path may not be walked.</summary>
    internal struct PathValue
    {
        public string State, Detail, Refused;
        public object V;

        public static PathValue Ok(object v) { return new PathValue { State = "ok", V = v, Detail = "" }; }
        public static PathValue Bad(string state, string detail) { return new PathValue { State = state, Detail = detail ?? "" }; }
        public static PathValue No(string name, string detail) { return new PathValue { State = "error", Refused = name, Detail = name + ": " + detail }; }
    }

    /// <summary>What a path needs of the game.</summary>
    internal interface IPathHost
    {
        /// <summary>The object a target names, or (staticOf) the type it names. When there is none, Bad is the reading.</summary>
        bool Root(string of, out object root, out Type staticOf, out PathValue bad);
        /// <summary>A comp of the owner by class name. Null: why says why.</summary>
        object Comp(object owner, string cls, out string why);
        /// <summary>An engine value as a number, a text or null. known false: this type is not a value.</summary>
        object Leaf(object v, out bool known);
        /// <summary>The index of cell x,z in a map-sized array, or -1 with why.</summary>
        int CellIndex(int x, int z, int length, out string why);
    }

    internal static class JawaBenchPathCore
    {
        internal const string BadPath = "BAD_PATH", CallsMethod = "PATH_CALLS_METHOD";

        // The reviewed readers, as DeclaringType.Property: each getter was read in the decompiled 1.6 source (RimSage, 2026-11-23)
        // and has no effect. A property that only returns a field needs no line here. Thing.Spawned writes one log line when
        // a thing names a map that does not exist (Log.ErrorOnce), which is a fault of the game's own.
        internal static readonly HashSet<string> Reviewed = new HashSet<string>(StringComparer.Ordinal)
        {
            "Verse.Thing.Destroyed", "Verse.Thing.Spawned", "Verse.Thing.Map", "Verse.Pawn.CurJob", "Verse.Pawn.CurJobDef", "Verse.Pawn.Dead",
            "Verse.Pawn.Downed", "Verse.Pawn.Drafted", "Verse.Pawn.InMentalState", "Verse.Pawn.MentalState", "Verse.Pawn.MentalStateDef",
            "Verse.Pawn_HealthTracker.Downed", "Verse.Pawn_HealthTracker.Dead", "Verse.AI.MentalStateHandler.InMentalState",
            "System.Array.Length", "System.Collections.Generic.List`1.Count", "System.Collections.Generic.Dictionary`2.Count",
            "System.Collections.Generic.HashSet`1.Count", "System.Collections.Generic.Queue`1.Count", "System.Collections.Generic.Stack`1.Count",
            "System.Collections.Generic.List`1.Capacity",
        };

        internal enum Kind { Name, Comp, Index, Cell }

        internal sealed class Step
        {
            public Kind K;
            public string Name;
            public int A, B;
            public override string ToString()
            {
                return K == Kind.Name ? Name : K == Kind.Comp ? "comp<" + Name + ">" : K == Kind.Index ? "[" + A + "]" : "[" + A + "," + B + "]";
            }
        }

        static readonly Dictionary<string, Step[]> Parsed = new Dictionary<string, Step[]>(StringComparer.Ordinal);

        static bool IdentStart(char c) { return c == '_' || char.IsLetter(c); }
        static bool Ident(string s)
        {
            if (string.IsNullOrEmpty(s) || !IdentStart(s[0])) return false;
            foreach (char c in s) if (c != '_' && !char.IsLetterOrDigit(c)) return false;
            return true;
        }

        /// <summary>The steps, or null with the refusal.</summary>
        internal static Step[] Parse(string path, out PathValue refusal)
        {
            refusal = default(PathValue);
            Step[] got;
            if (path != null && Parsed.TryGetValue(path, out got)) return got;
            if (string.IsNullOrEmpty(path)) { refusal = PathValue.No(BadPath, "the path is empty"); return null; }
            if (path.IndexOf('(') >= 0 || path.IndexOf(')') >= 0) { refusal = PathValue.No(CallsMethod, "'" + path + "' calls a method"); return null; }
            var steps = new List<Step>();
            int i = 0;
            bool want = true;                                   // a name or a comp must follow (the start, or after a point)
            while (i < path.Length)
            {
                char c = path[i];
                if (c == '.')
                {
                    if (want) break;
                    want = true; i++; continue;
                }
                if (c == '[')
                {
                    int e = path.IndexOf(']', i);
                    if (e < 0 || (want && steps.Count > 0)) break;
                    var parts = path.Substring(i + 1, e - i - 1).Split(',');
                    int a, b = 0;
                    if (parts.Length > 2 || !int.TryParse(parts[0].Trim(), NumberStyles.None, CultureInfo.InvariantCulture, out a)
                        || (parts.Length == 2 && !int.TryParse(parts[1].Trim(), NumberStyles.None, CultureInfo.InvariantCulture, out b))) break;
                    steps.Add(new Step { K = parts.Length == 2 ? Kind.Cell : Kind.Index, A = a, B = b });
                    want = false; i = e + 1; continue;
                }
                if (!want) break;
                if (string.CompareOrdinal(path, i, "comp<", 0, 5) == 0)
                {
                    int e = path.IndexOf('>', i);
                    string cls = e < 0 ? "" : path.Substring(i + 5, e - i - 5).Trim();
                    if (cls.Length == 0) break;
                    steps.Add(new Step { K = Kind.Comp, Name = cls });
                    want = false; i = e + 1; continue;
                }
                int j = i;
                while (j < path.Length && (path[j] == '_' || char.IsLetterOrDigit(path[j]))) j++;
                string n = path.Substring(i, j - i);
                if (!Ident(n)) break;
                steps.Add(new Step { K = Kind.Name, Name = n });
                want = false; i = j;
            }
            if (i < path.Length || want) { refusal = PathValue.No(BadPath, "'" + path + "' at character " + (i + 1) + ": steps are a name, comp<Class> or [n], joined by points"); return null; }
            got = steps.ToArray();
            Parsed[path] = got;
            return got;
        }

        const BindingFlags Declared = BindingFlags.Instance | BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.DeclaredOnly;

        internal sealed class Access
        {
            public FieldInfo F;
            public PropertyInfo P;
            public string Why, Refused;
            public object Get(object o)
            {
                if (F != null) return F.GetValue(F.IsStatic ? null : o);
                return P.GetValue(P.GetGetMethod(true).IsStatic ? null : o, null);
            }
        }

        struct Key : IEquatable<Key>
        {
            public Type T; public string N; public bool S;
            public bool Equals(Key k) { return T == k.T && S == k.S && N == k.N; }
            public override bool Equals(object o) { return o is Key && Equals((Key)o); }
            public override int GetHashCode() { return T.GetHashCode() * 31 + N.GetHashCode() + (S ? 1 : 0); }
        }

        static readonly Dictionary<Key, Access> Cache = new Dictionary<Key, Access>();

        /// <summary>How one name of one type is read. The most derived member of that name wins, as in the language.</summary>
        internal static Access Member(Type t, string name, bool isStatic)
        {
            var key = new Key { T = t, N = name, S = isStatic };
            Access a;
            if (Cache.TryGetValue(key, out a)) return a;
            a = new Access();
            for (var ty = t; ty != null && a.F == null && a.P == null && a.Refused == null; ty = ty.BaseType)
            {
                var f = ty.GetField(name, Declared);
                if (f != null && (f.IsStatic || !isStatic)) { a.F = f; break; }
                PropertyInfo p = null;
                foreach (var q in ty.GetProperties(Declared))
                    if (q.Name == name && q.GetIndexParameters().Length == 0 && q.GetGetMethod(true) != null) { p = q; break; }
                if (p != null && (p.GetGetMethod(true).IsStatic || !isStatic))
                {
                    a.F = ReturnedField(p);
                    if (a.F != null) break;
                    if (Reviewed.Contains(ListName(p))) { a.P = p; break; }
                    a.Refused = "property '" + name + "' of " + ty.FullName + " is not on the reviewed list";
                    break;
                }
                foreach (var m in ty.GetMethods(Declared))
                    if (m.Name == name) { a.Refused = "'" + name + "' of " + ty.FullName + " is a method"; break; }
            }
            if (a.F == null && a.P == null && a.Refused == null)
                a.Why = "no field '" + name + "' on " + t.FullName + "; it has: " + string.Join(", ", Fields(t, isStatic).ToArray());
            Cache[key] = a;
            return a;
        }

        static string ListName(PropertyInfo p)
        {
            var d = p.DeclaringType;
            if (d.IsGenericType) d = d.GetGenericTypeDefinition();
            return d.FullName + "." + p.Name;
        }

        /// <summary>The field that a getter returns and does nothing else (ldarg.0 ldfld ret, or ldsfld ret), else null.</summary>
        internal static FieldInfo ReturnedField(PropertyInfo p)
        {
            try
            {
                var g = p.GetGetMethod(true);
                var body = g.GetMethodBody();
                byte[] il = body == null ? null : body.GetILAsByteArray();
                int at = -1;
                if (il != null && il.Length == 7 && il[0] == 0x02 && il[1] == 0x7B && il[6] == 0x2A) at = 2;
                else if (il != null && il.Length == 6 && il[0] == 0x7E && il[5] == 0x2A) at = 1;
                if (at < 0) return null;
                var d = p.DeclaringType;
                return g.Module.ResolveField(BitConverter.ToInt32(il, at), d.IsGenericType ? d.GetGenericArguments() : null, null);
            }
            catch (Exception) { return null; }
        }

        /// <summary>The names that a path step may use on this type, sorted.</summary>
        internal static List<string> Fields(Type t, bool isStatic)
        {
            var set = new SortedSet<string>(StringComparer.Ordinal);
            for (var ty = t; ty != null && ty != typeof(object); ty = ty.BaseType)
            {
                foreach (var f in ty.GetFields(Declared))
                    if ((f.IsStatic || !isStatic) && f.Name.IndexOf('<') < 0) set.Add(f.Name);
                foreach (var p in ty.GetProperties(Declared))
                {
                    var g = p.GetGetMethod(true);
                    if (g == null || p.GetIndexParameters().Length > 0 || (isStatic && !g.IsStatic)) continue;
                    if (ReturnedField(p) != null || Reviewed.Contains(ListName(p))) set.Add(p.Name);
                }
            }
            return new List<string>(set);
        }

        /// <summary>One reading. Never throws.</summary>
        internal static PathValue Read(IPathHost h, string of, string path)
        {
            try
            {
                PathValue bad;
                var steps = Parse(path, out bad);
                if (steps == null) return bad;
                object o;
                Type st;
                if (!h.Root(of, out o, out st, out bad)) return bad;
                string last = of;
                for (int i = 0; i < steps.Length; i++)
                {
                    var s = steps[i];
                    if (o == null && !(i == 0 && st != null)) return PathValue.Bad("error", "null at '" + last + "'");
                    if (s.K == Kind.Name)
                    {
                        var a = Member(i == 0 && st != null ? st : o.GetType(), s.Name, i == 0 && st != null);
                        if (a.Refused != null) return PathValue.No(CallsMethod, a.Refused);
                        if (a.Why != null) return PathValue.Bad("error", "step '" + s.Name + "': " + a.Why);
                        o = a.Get(o);
                    }
                    else if (i == 0 && st != null) return PathValue.Bad("error", "step '" + s + "': a static target starts with a field name");
                    else if (s.K == Kind.Comp)
                    {
                        string why;
                        o = h.Comp(o, s.Name, out why);
                        if (o == null) return PathValue.Bad("error", "step '" + s + "': " + why);
                    }
                    else
                    {
                        var l = o as IList;
                        if (l == null) return PathValue.Bad("error", "step '" + s + "': " + o.GetType().FullName + " has no index");
                        int n = s.A;
                        if (s.K == Kind.Cell)
                        {
                            string why;
                            n = h.CellIndex(s.A, s.B, l.Count, out why);
                            if (n < 0) return PathValue.Bad("error", "step '" + s + "': " + why);
                        }
                        if (n >= l.Count) return PathValue.Bad("error", "step '" + s + "': index " + n + " of " + l.Count);
                        o = l[n];
                    }
                    last = s.ToString();
                }
                string no;
                var v = Leaf(h, o, 0, out no);
                return no == null ? PathValue.Ok(v) : PathValue.Bad("error", no);
            }
            catch (Exception e)
            {
                var x = e is TargetInvocationException && e.InnerException != null ? e.InnerException : e;
                return PathValue.Bad("error", x.GetType().Name + ": " + x.Message);
            }
        }

        static readonly object BoxTrue = true, BoxFalse = false;

        static object Leaf(IPathHost h, object v, int depth, out string no)
        {
            no = null;
            if (v == null) return null;
            if (v is bool) return (bool)v ? BoxTrue : BoxFalse;
            if (v is string) return v;
            if (v is char || v is Enum) return v.ToString();
            if (v is double) { double d = (double)v; if (double.IsNaN(d) || double.IsInfinity(d)) { no = "the number is " + d.ToString(CultureInfo.InvariantCulture); return null; } return v; }
            if ((v.GetType().IsPrimitive && !(v is IntPtr) && !(v is UIntPtr)) || v is decimal)
                return Leaf(h, Convert.ToDouble(v, CultureInfo.InvariantCulture), depth, out no);
            bool known;
            var x = h.Leaf(v, out known);
            if (known) return x;
            var l = v as IList;
            if (l != null && depth == 0)
            {
                var outl = new List<object>();
                for (int i = 0; i < l.Count; i++)
                {
                    outl.Add(Leaf(h, l[i], 1, out no));
                    if (no != null) { no = "[" + i + "] " + no; return null; }
                }
                return outl;
            }
            no = v.GetType().FullName + " is not a value; it has: " + string.Join(", ", Fields(v.GetType(), false).ToArray());
            return null;
        }

        /// <summary>The state of a reading as one text: `null` apart from `ok`, so that a condition can always read it.</summary>
        internal static string StateOf(PathValue r) { return r.State == "ok" && r.V == null ? "null" : r.State; }
    }
}
