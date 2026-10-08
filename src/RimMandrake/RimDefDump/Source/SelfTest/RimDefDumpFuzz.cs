// Approach B for RimDefDump: seeded fuzz over the streaming JsonWriter and the capture/stem kernel.
//   json     random trees of objects, arrays, strings (every control char, quotes, backslashes, surrogates), numbers, bools and nulls are written
//            both indented and compact, then read back with an independent parser and compared; the document is also checked to be valid
//            one-token-at-a-time (no stray comma, no missing comma) by that parser
//   numbers  float / double / long / ulong formatting: round-trips exactly, never "0.10000000149011612" for 0.1f, NaN and infinities are null, ulong keeps every digit
//   stems    ReserveStem: unique case-insensitively, untouched in the ordinary case, never reuses a claimed stem; SafeFileName output is filename-safe
//   captures IsCaptureId vs an independent pattern; retention keeps the newest three unfrozen captures, never touches frozen or junk names
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;

namespace RimMandrake.RimDefDump.SelfTest
{
    internal static class RimDefDumpFuzz
    {
        public static long Cases, Steps, Nodes, Escaped, Surrogates, Clashes, Frozen;
        private static void Check(bool ok, string msg) { if (!ok) throw new Exception(msg); }

        // ── tree model ──
        private abstract class Node { }
        private sealed class Obj : Node { public List<KeyValuePair<string, Node>> Members = new List<KeyValuePair<string, Node>>(); }
        private sealed class Arr : Node { public List<Node> Items = new List<Node>(); }
        private sealed class Str : Node { public string V; }
        private sealed class Num : Node { public string Text; public double D; public bool IsFloat; public float F; }
        private sealed class Bool : Node { public bool V; }
        private sealed class Null : Node { }

        private static string RandomString(Random r)
        {
            var sb = new StringBuilder();
            int n = r.Next(0, 14);
            for (int i = 0; i < n; i++)
            {
                int k = r.Next(100);
                if (k < 40) sb.Append((char)r.Next('a', 'z' + 1));
                else if (k < 52) sb.Append((char)r.Next(0, 0x20));
                else if (k < 58) sb.Append("\"\\/\u007f"[r.Next(4)]);
                else if (k < 66) sb.Append((char)r.Next(0x80, 0x800));
                else if (k < 72) sb.Append(char.ConvertFromUtf32(r.Next(0x10000, 0x10FFFF)));            // a valid surrogate pair
                else if (k < 78) sb.Append((char)r.Next(0xD800, 0xE000));                                // a lone surrogate
                else if (k < 82) sb.Append("\r\n\t\b\f"[r.Next(5)]);
                else if (k < 88) sb.Append((char)r.Next(0xE000, 0xFFFE));
                else sb.Append(' ');
            }
            return sb.ToString();
        }

        private static Node Gen(Random r, int depth, JsonWriter w, int[] count)
        {
            count[0]++;
            int k = depth > 4 ? r.Next(6) : r.Next(9);
            switch (k)
            {
                case 0: w.Null(); return new Null();
                case 1: { bool b = r.Next(2) == 0; w.Bool(b); return new Bool { V = b }; }
                case 2: case 3: { string s = r.Next(12) == 0 ? null : RandomString(r); w.Str(s); return s == null ? (Node)new Null() : new Str { V = s }; }
                case 4: { long v = r.Next(3) == 0 ? long.MinValue : r.Next(3) == 0 ? long.MaxValue : (long)r.Next(-100000, 100000) * r.Next(1, 100000); w.Number(v); return new Num { Text = v.ToString(CultureInfo.InvariantCulture) }; }
                case 5: { double d = (r.NextDouble() - 0.5) * Math.Pow(10, r.Next(-8, 12)); w.Number(d); return new Num { D = d, Text = null }; }
                case 6: case 7:
                    {
                        w.StartObject(); var o = new Obj(); int n = r.Next(0, 5);
                        for (int i = 0; i < n; i++) { string key = "k" + i + RandomString(r); w.Name(key); o.Members.Add(new KeyValuePair<string, Node>(key, Gen(r, depth + 1, w, count))); }
                        w.EndObject(); return o;
                    }
                default:
                    {
                        w.StartArray(); var a = new Arr(); int n = r.Next(0, 5);
                        for (int i = 0; i < n; i++) a.Items.Add(Gen(r, depth + 1, w, count));
                        w.EndArray(); return a;
                    }
            }
        }

        // ── an independent strict JSON reader (so a lone-surrogate escape can be read back, which System.Text.Json refuses) ──
        private sealed class Reader
        {
            private readonly string s; private int p;
            public Reader(string text) { s = text; }
            private void Ws() { while (p < s.Length && (s[p] == ' ' || s[p] == '\n' || s[p] == '\r' || s[p] == '\t')) p++; }
            public Node Document() { Ws(); var n = Value(); Ws(); Check(p == s.Length, "trailing text after the document at " + p); return n; }
            private Node Value()
            {
                Check(p < s.Length, "unexpected end");
                char c = s[p];
                if (c == '{')
                {
                    p++; var o = new Obj(); Ws();
                    if (s[p] == '}') { p++; return o; }
                    while (true)
                    {
                        Ws(); Check(s[p] == '"', "object key expected at " + p); string key = ReadString(); Ws();
                        Check(s[p] == ':', "colon expected at " + p); p++; Ws();
                        o.Members.Add(new KeyValuePair<string, Node>(key, Value())); Ws();
                        if (s[p] == ',') { p++; continue; }
                        Check(s[p] == '}', "} or , expected at " + p); p++; return o;
                    }
                }
                if (c == '[')
                {
                    p++; var a = new Arr(); Ws();
                    if (s[p] == ']') { p++; return a; }
                    while (true)
                    {
                        Ws(); a.Items.Add(Value()); Ws();
                        if (s[p] == ',') { p++; continue; }
                        Check(s[p] == ']', "] or , expected at " + p); p++; return a;
                    }
                }
                if (c == '"') return new Str { V = ReadString() };
                if (s.Substring(p).StartsWith("true")) { p += 4; return new Bool { V = true }; }
                if (s.Substring(p).StartsWith("false")) { p += 5; return new Bool { V = false }; }
                if (s.Substring(p).StartsWith("null")) { p += 4; return new Null(); }
                int st = p;
                while (p < s.Length && "+-0123456789.eE".IndexOf(s[p]) >= 0) p++;
                Check(p > st, "value expected at " + st + ": " + s.Substring(st, Math.Min(10, s.Length - st)));
                return new Num { Text = s.Substring(st, p - st) };
            }
            private string ReadString()
            {
                p++; var sb = new StringBuilder();
                while (true)
                {
                    Check(p < s.Length, "unterminated string");
                    char c = s[p++];
                    if (c == '"') return sb.ToString();
                    Check(c >= 0x20, "raw control character 0x" + ((int)c).ToString("x2") + " inside a string (must be escaped)");
                    if (c != '\\') { sb.Append(c); continue; }
                    char e = s[p++];
                    switch (e)
                    {
                        case '"': sb.Append('"'); break; case '\\': sb.Append('\\'); break; case '/': sb.Append('/'); break;
                        case 'n': sb.Append('\n'); break; case 'r': sb.Append('\r'); break; case 't': sb.Append('\t'); break;
                        case 'b': sb.Append('\b'); break; case 'f': sb.Append('\f'); break;
                        case 'u': sb.Append((char)Convert.ToInt32(s.Substring(p, 4), 16)); p += 4; break;
                        default: throw new Exception("bad escape \\" + e);
                    }
                }
            }
        }

        private static void Compare(Node a, Node b, string path)
        {
            Check(a.GetType() == b.GetType(), path + ": type " + a.GetType().Name + " vs " + b.GetType().Name);
            if (a is Obj) { var x = (Obj)a; var y = (Obj)b; Check(x.Members.Count == y.Members.Count, path + ": member count"); for (int i = 0; i < x.Members.Count; i++) { Check(x.Members[i].Key == y.Members[i].Key, path + ": key " + i + " differs"); Compare(x.Members[i].Value, y.Members[i].Value, path + "." + i); } }
            else if (a is Arr) { var x = (Arr)a; var y = (Arr)b; Check(x.Items.Count == y.Items.Count, path + ": item count"); for (int i = 0; i < x.Items.Count; i++) Compare(x.Items[i], y.Items[i], path + "[" + i + "]"); }
            else if (a is Str) Check(((Str)a).V == ((Str)b).V, path + ": string differs");
            else if (a is Bool) Check(((Bool)a).V == ((Bool)b).V, path + ": bool differs");
            else if (a is Num)
            {
                var x = (Num)a; var y = (Num)b;
                if (x.Text != null) Check(x.Text == y.Text, path + ": integer text " + x.Text + " vs " + y.Text);
                else Check(double.Parse(y.Text, CultureInfo.InvariantCulture) == x.D, path + ": double " + x.D.ToString("R", CultureInfo.InvariantCulture) + " read back as " + y.Text);
            }
        }

        private static List<string> Json(int n, int seed0)
        {
            var fails = new List<string>();
            for (int s = 0; s < n && fails.Count < 5; s++)
            {
                int seed = seed0 + s; Cases++;
                foreach (bool indent in new[] { true, false })
                {
                    try
                    {
                        var r = new Random(seed); var sw = new StringWriter(); var w = new JsonWriter(sw, indent); var count = new int[1];
                        Node tree = Gen(r, 0, w, count);
                        string text = sw.ToString();
                        Nodes += count[0]; Steps += count[0];
                        if (text.Contains("\\u")) Escaped++;
                        if (text.Contains("\\ud") || text.Contains("\\ude")) Surrogates++;
                        Check(text.All(c => c >= 0x20 || c == '\n') , "a raw control character escaped into the output");
                        if (!indent) Check(text.IndexOf('\n') < 0, "compact output contains a raw newline");
                        Node back = new Reader(text).Document();
                        Compare(tree, back, "$");
                    }
                    catch (Exception ex) { fails.Add("json seed " + seed + (indent ? " indented" : " compact") + ": " + ex.Message); }
                }
            }
            return fails;
        }

        // ═════════════ numbers ═════════════
        private static string W(Action<JsonWriter> f) { var sw = new StringWriter(); f(new JsonWriter(sw, false)); return sw.ToString(); }

        private static string WS(object v) { var sw = new StringWriter(); bool ok = new JsonWriter(sw, false).TryWriteSimple(v); return ok ? sw.ToString() : "<refused>"; }

        private static List<string> Numbers(int n, int seed0)
        {
            var fails = new List<string>();
            try
            {
                Cases++;
                Check(W(j => j.Number(0.1f)) == "0.1", "0.1f must print as 0.1, not its widened noise: " + W(j => j.Number(0.1f)));
                Check(W(j => j.Prop("a", 0.35f)) == "\"a\":0.35", "a float property must not widen: " + W(j => j.Prop("a", 0.35f)));
                Check(W(j => j.Number(double.NaN)) == "null" && W(j => j.Number(double.PositiveInfinity)) == "null" && W(j => j.Number(float.NegativeInfinity)) == "null" && W(j => j.Number(float.NaN)) == "null", "NaN / infinity must be null");
                Check(W(j => j.Number(ulong.MaxValue)) == "18446744073709551615" && W(j => j.Number(9007199254740993UL)) == "9007199254740993", "ulong must keep every digit (a double would lose them above 2^53)");
                Check(W(j => j.Number(long.MinValue)) == "-9223372036854775808", "long.MinValue");
                Check(WS((ulong)9007199254740993UL) == "9007199254740993", "TryWriteSimple(ulong) goes through the exact path");
                Check(WS(0.1f) == "0.1", "TryWriteSimple(float) goes through the float path");
                Check(WS(null) == "null" && WS('x') == "\"x\"" && WS(DayOfWeek.Monday) == "\"Monday\"", "null / char / enum");
                var sw = new StringWriter(); var jw = new JsonWriter(sw, false);
                Check(!jw.TryWriteSimple(new object()), "a plain object must be refused so the reflector recurses");
                Steps += 9;
                for (int s = 0; s < n && fails.Count < 5; s++)
                {
                    int seed = seed0 + s; var r = new Random(seed); Cases++;
                    float f = (float)((r.NextDouble() - 0.5) * Math.Pow(10, r.Next(-6, 8)));
                    string ft = W(j => j.Number(f));
                    Check(float.Parse(ft, CultureInfo.InvariantCulture) == f, "float " + f.ToString("R", CultureInfo.InvariantCulture) + " did not round-trip through " + ft);
                    Check(ft.Length <= 12 || f.ToString("R", CultureInfo.InvariantCulture) == ft, "float text " + ft + " carries widening noise");
                    double d = (r.NextDouble() - 0.5) * Math.Pow(10, r.Next(-12, 18));
                    Check(double.Parse(W(j => j.Number(d)), CultureInfo.InvariantCulture) == d, "double " + d + " did not round-trip");
                    ulong u = ((ulong)r.Next() << 33) ^ ((ulong)r.Next() << 11) ^ (ulong)r.Next(1 << 11);
                    Check(W(j => j.Number(u)) == u.ToString(CultureInfo.InvariantCulture), "ulong " + u + " lost digits");
                    Steps += 4;
                }
            }
            catch (Exception ex) { fails.Add("numbers: " + ex.Message); }
            return fails;
        }

        // ═════════════ stems ═════════════
        private static List<string> Stems(int n, int seed0)
        {
            var fails = new List<string>();
            for (int s = 0; s < n && fails.Count < 5; s++)
            {
                int seed = seed0 + s; var r = new Random(seed); Cases++;
                try
                {
                    var assigned = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
                    var got = new List<string>();
                    string[] stems = { "ThingDef", "thingdef", "ThingDEF", "BiomeDef", "RecipeDef", "Recipedef" };
                    string[] asms = { "Assembly-CSharp", "My.Mod", "Mod+Nested", "A B", "" };
                    int k = r.Next(1, 14);
                    for (int i = 0; i < k; i++)
                    {
                        string stem = stems[r.Next(stems.Length)]; bool clashed;
                        bool expectClash = got.Any(g => string.Equals(g, stem, StringComparison.OrdinalIgnoreCase));
                        string res = RM_DumpKernel.ReserveStem(assigned, stem, asms[r.Next(asms.Length)], out clashed);
                        Steps++;
                        Check(clashed == expectClash, "clash flag " + clashed + " for " + stem + " after " + string.Join(",", got));
                        if (!clashed) Check(res == stem, "an unclaimed stem must be returned untouched (every existing reader of defs/ThingDef.json depends on it)");
                        else { Clashes++; Check(res.StartsWith(stem + "__"), "a clash must keep the stem and add the assembly: " + res); }
                        Check(!got.Any(g => string.Equals(g, res, StringComparison.OrdinalIgnoreCase)), "stem " + res + " collides case-insensitively with an earlier file");
                        got.Add(res);
                    }
                    foreach (string sfn in new[] { "A.B.C", "Foo`1", "Outer+Inner", "a b/c\\d:e*?\"<>|", "naïve", "" })
                    {
                        string safe = RM_DumpKernel.SafeFileName(sfn);
                        Check(safe.Length == sfn.Length, "SafeFileName changed the length of " + sfn);
                        Check(safe.All(c => char.IsLetterOrDigit(c) || c == '.' || c == '_' || c == '-'), "SafeFileName left an unsafe character in " + safe);
                        Check(!safe.Contains("/") && !safe.Contains("\\") && !safe.Contains(":") && !safe.Contains("+") && !safe.Contains("`"), "path or generic marker survived: " + safe);
                    }
                }
                catch (Exception ex) { fails.Add("stems seed " + seed + ": " + ex.Message); }
            }
            return fails;
        }

        // ═════════════ captures ═════════════
        private static string Id(DateTime t) { return t.ToString("yyyy-MM-dd'T'HH-mm-ss'Z'", CultureInfo.InvariantCulture); }

        private static List<string> Captures(int n, int seed0)
        {
            var fails = new List<string>();
            try
            {
                Cases++;
                Check(RM_DumpKernel.IsCaptureId("2026-10-07T14-03-59Z") && !RM_DumpKernel.IsCaptureId("2026-10-07T14:03:59Z") && !RM_DumpKernel.IsCaptureId("2026-10-07T14-03-59") && !RM_DumpKernel.IsCaptureId(".writing") && !RM_DumpKernel.IsCaptureId(null) && !RM_DumpKernel.IsCaptureId("2026-10-07t14-03-59Z") && !RM_DumpKernel.IsCaptureId("2026-10-07T14-03-59ZZ") && !RM_DumpKernel.IsCaptureId("2026-1a-07T14-03-59Z") && !RM_DumpKernel.IsCaptureId(""), "capture id vocabulary");
                Steps++;
            }
            catch (Exception ex) { fails.Add("captures vocabulary: " + ex.Message); return fails; }
            for (int s = 0; s < n && fails.Count < 5; s++)
            {
                int seed = seed0 + s; var r = new Random(seed); Cases++;
                try
                {
                    var rows = new List<KeyValuePair<string, bool>>();
                    var t0 = new DateTime(2026, 1, 1, 0, 0, 0, DateTimeKind.Utc);
                    int k = r.Next(0, 14);
                    for (int i = 0; i < k; i++)
                    {
                        int c = r.Next(100);
                        string name = c < 80 ? Id(t0.AddSeconds(r.Next(0, 90000000))) : c < 90 ? ".writing" : c < 95 ? "notes" : Id(t0.AddSeconds(r.Next(100))) + ".bak";
                        bool frozen = r.Next(5) == 0;
                        if (frozen) Frozen++;
                        rows.Add(new KeyValuePair<string, bool>(name, frozen));
                    }
                    int keep = r.Next(0, 5);
                    var got = RM_DumpKernel.PruneVictims(rows, keep);
                    Steps += rows.Count;
                    var live = rows.Where(x => RM_DumpKernel.IsCaptureId(x.Key) && !x.Value).Select(x => x.Key).OrderBy(x => x, StringComparer.Ordinal).ToList();
                    var want = live.Take(Math.Max(0, live.Count - keep)).ToList();
                    Check(got.SequenceEqual(want), "victims " + string.Join(",", got) + " want " + string.Join(",", want));
                    Check(got.All(v => !rows.Any(x => x.Key == v && x.Value)), "retention chose a FROZEN capture");
                    Check(got.All(v => RM_DumpKernel.IsCaptureId(v)), "retention chose a name that is not a capture");
                    Check(live.Count - got.Count == Math.Min(keep, live.Count), "kept " + (live.Count - got.Count) + " of " + live.Count + " unfrozen captures, wanted " + Math.Min(keep, live.Count));
                    if (live.Count > keep) Check(live.Skip(live.Count - keep).All(v => !got.Contains(v)), "retention dropped one of the newest");
                    Check(RM_DumpKernel.KeepNewest == 3, "the documented retention is the newest three");
                }
                catch (Exception ex) { fails.Add("captures seed " + seed + ": " + ex.Message); }
            }
            return fails;
        }

        public static bool Run(double scale, int? oneSeed, string only)
        {
            var sw = Stopwatch.StartNew();
            bool ok = true;
            int N(int n) { return oneSeed.HasValue ? 1 : (int)(n * scale); }
            int S(int baseSeed) { return oneSeed ?? baseSeed; }
            var fam = new (string name, Func<List<string>> run)[]
            {
                ("json", () => Json(N(6000), S(1))),
                ("numbers", () => Numbers(N(6000), S(1))),
                ("stems", () => Stems(N(4000), S(1))),
                ("captures", () => Captures(N(6000), S(1))),
            };
            foreach (var f in fam)
            {
                if (only != null && f.name != only) continue;
                long c0 = Cases, s0 = Steps; var t = Stopwatch.StartNew();
                var fails = f.run();
                Console.WriteLine($"fuzz {f.name}: {Cases - c0} cases, {Steps - s0} steps, {t.Elapsed.TotalSeconds:F2}s, {(fails.Count == 0 ? "0 failures" : fails.Count + " FAILURES")}");
                foreach (var m in fails) Console.WriteLine("FAIL " + m);
                if (fails.Count > 0) ok = false;
            }
            if (only != null && !fam.Any(f => f.name == only)) { Console.WriteLine("FAIL unknown --fuzz-only family: " + only); return false; }
            if (Cases == 0) { Console.WriteLine("FAIL no cases ran (--fuzz-scale too small?); a fuzz that checked nothing is not a pass"); return false; }
            Console.WriteLine($"reached: json nodes {Nodes}, documents with escapes {Escaped}, with surrogates {Surrogates}, stem clashes {Clashes}, frozen captures {Frozen}");
            if (only == null && !oneSeed.HasValue && scale >= 1 && (Nodes == 0 || Escaped == 0 || Surrogates == 0 || Clashes == 0 || Frozen == 0)) { Console.WriteLine("FAIL fuzz never reached a path (blind)"); ok = false; }
            Console.WriteLine($"rimdefdump fuzz: {Cases} cases, {Steps} steps, {sw.Elapsed.TotalSeconds:F2}s total -> {(ok ? "OK" : "FAILED")}");
            return ok;
        }
    }
}
