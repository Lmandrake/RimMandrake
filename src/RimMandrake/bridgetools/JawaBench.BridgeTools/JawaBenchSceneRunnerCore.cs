// JawaBenchSceneRunnerCore.cs - the Verse-free half of jawa/run_scenes, the shared in-game scene runner
// (RIMMANDRAKE_BUILD_SHARED_SCENE_RUNNER_FIRST_SLICE; fast_testing_2026-11-05/scored.md item 8,
// live_test_speed_assessment_2026-11-12.md section 4 step 5).
//
// Kept free of RimWorld/Unity references ON PURPOSE: bridgetools/SceneRunnerSelfTest compiles THIS production file into
// a plain net8.0 harness (src/RimMandrake/Utils/selftest_scene_runner_core.py). A `using Verse;` here breaks that build.
//
// THE CONTRACT (read by reflection, so a mod never references JawaBench and JawaBench never references a mod):
//   A suite is a public static class in a mod's PROOF build (RM_PROOFS). A scene is a public static method
//     object M(string scene, int x, int z)
//   carrying one or more attributes whose TYPE NAME is "RMTestAttribute" (src/RimMandrake/_Shared/SceneRunner/
//   RMTestAttribute.cs: Name, Ticks, Outside). The method stages the scene with its origin at (x, z) and returns
//     - a zero-argument delegate, the JUDGE, which the runner calls after Ticks ticks; or
//     - a string, a staging refusal ("INVALID ...", "REFUSED ..."), which becomes one UNMEASURED row.
//   The judge returns a verdict line ("PASS|FAIL|INVALID|ERROR <name> <detail>", the static_call proofs' shape) or rows
//   (IEnumerable of string[] {check, status, measured, expected}).
//   Optional suite hooks, each public static string M(string): Origins(n) -> "x,z;x,z;..." (the suite's own plots),
//   SuiteBegin(_) before the first scene, SuiteEnd(_) after the last (always, in a finally).
//
// THE ROW TABLE: every scene returns rows of (scene, check, status, measured, expected, source, cause). status is PASS,
// FAIL or UNMEASURED and nothing else. UNMEASURED always names its cause: the question was not answered (a staging
// refusal, a judge that threw, a short advance, a game that changed under the run). It is never a FAIL and never a PASS.
// source is "scene" (the mod's own judge), "outside" (a vanilla read the runner makes from outside the mod, the guard
// against a judge that shares the mod's blind spots: assessment section 3 (c)), "runner" (the runner's own UNMEASURED rows:
// a refusal, a throw, a changed game) or, added by scene_runner.py, "driver" (its SUITE_OUTSIDE_READ guard).
using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Reflection;

namespace JawaBench.BridgeTools
{
    public static class JawaBenchSceneRunnerCore
    {
        public const string Pass = "PASS", FailS = "FAIL", Unmeasured = "UNMEASURED";
        public const string AttributeName = "RMTestAttribute";
        public const int DefaultTicks = 300, MaxSceneTicks = 30000, MaxRunTicks = 120000, DefaultPitch = 15;

        public sealed class Row
        {
            public string scene, check, status, measured, expected, source, cause;

            public Dictionary<string, object> ToDict() => new Dictionary<string, object>
            {
                ["scene"] = scene, ["check"] = check, ["status"] = status, ["measured"] = measured, ["expected"] = expected,
                ["source"] = source, ["cause"] = cause,
            };
        }

        public static Row R(string scene, string check, string status, string measured, string expected, string source, string cause = null) =>
            new Row { scene = scene, check = check, status = status, measured = measured, expected = expected, source = source, cause = cause };

        public static Row Unmeasured_(string scene, string check, string cause) => R(scene, check, Unmeasured, null, null, "runner", cause);

        public sealed class Spec
        {
            public string name;
            public MethodInfo method;
            public int ticks;
            public string outside;
        }

        /// <summary>Every scene a suite type declares, in declaration order. problems lists what was refused (a wrong
        /// signature, a duplicate name, an unreadable attribute) so a broken suite never silently shrinks.</summary>
        public static List<Spec> Discover(Type suite, List<string> problems)
        {
            var specs = new List<Spec>();
            var seen = new HashSet<string>(StringComparer.Ordinal);
            if (!(suite.IsVisible && suite.IsAbstract && suite.IsSealed))
                problems.Add(suite.Name + ": a suite must be a public static class (visible from outside its assembly)");
            foreach (MethodInfo m in suite.GetMethods(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static | BindingFlags.Instance | BindingFlags.DeclaredOnly)
                         .OrderBy(x => x.MetadataToken))
            {
                object[] attrs;
                try { attrs = m.GetCustomAttributes(false).Where(a => a.GetType().Name == AttributeName).ToArray(); }
                catch (Exception e) { problems.Add(m.Name + ": attributes unreadable: " + e.GetType().Name + ": " + e.Message); continue; }
                if (attrs.Length == 0) continue;
                ParameterInfo[] ps = m.GetParameters();
                bool shape = m.IsPublic && m.IsStatic && !m.ContainsGenericParameters && ps.Length == 3 && ps[0].ParameterType == typeof(string)
                             && ps[1].ParameterType == typeof(int) && ps[2].ParameterType == typeof(int) && m.ReturnType == typeof(object);
                if (!shape)
                {
                    problems.Add(m.Name + ": a scene must be public static object M(string scene, int x, int z)");
                    continue;
                }
                foreach (object a in attrs)
                {
                    string name, outside;
                    int ticks;
                    try
                    {
                        name = Prop<string>(a, "Name");
                        ticks = Prop<int>(a, "Ticks");
                        outside = Prop<string>(a, "Outside");
                    }
                    catch (Exception e)
                    {
                        problems.Add(m.Name + ": an RMTest attribute is unreadable: " + (e.InnerException ?? e).Message);
                        continue;
                    }
                    if (string.IsNullOrWhiteSpace(name)) { problems.Add(m.Name + ": an RMTest with no Name"); continue; }
                    if (!seen.Add(name)) { problems.Add(name + ": declared twice"); continue; }
                    if (ticks < 0 || ticks > MaxSceneTicks) { problems.Add(name + ": Ticks " + ticks + " outside 0.." + MaxSceneTicks); continue; }
                    if (!string.IsNullOrWhiteSpace(outside) && ParseOutside(outside, out string why) == null)
                    {
                        problems.Add(name + ": Outside unreadable: " + why);
                        continue;
                    }
                    specs.Add(new Spec { name = name, method = m, ticks = ticks, outside = outside });
                }
            }
            return specs;
        }

        /// <summary>An attribute property of exactly type T; throws (Discover records it) when it is missing or of another
        /// type, so a mod's misdeclared copy never silently becomes a default Ticks or no Outside check.</summary>
        private static T Prop<T>(object a, string name)
        {
            PropertyInfo p = a.GetType().GetProperty(name);
            if (p == null || p.PropertyType != typeof(T))
                throw new InvalidOperationException(a.GetType().FullName + "." + name + " is " + (p == null ? "missing" : p.PropertyType.Name) + ", not " + typeof(T).Name);
            object v = p.GetValue(a);
            return v is T t ? t : default(T);
        }

        /// <summary>The scenes a comma list names, in the list's order; empty = every scene. unknown gets each name the
        /// suite does not declare (the caller refuses the run before any scene is staged).</summary>
        public static List<Spec> Select(List<Spec> all, string csv, List<string> unknown)
        {
            if (string.IsNullOrWhiteSpace(csv)) return all.ToList();
            var by = all.ToDictionary(s => s.name, StringComparer.Ordinal);
            var o = new List<Spec>();
            foreach (string n in csv.Split(',').Select(x => x.Trim()).Where(x => x.Length > 0))
            {
                if (by.TryGetValue(n, out Spec s)) o.Add(s);
                else unknown.Add(n);
            }
            return o;
        }

        /// <summary>The ticks a scene gets: an override > 0 wins, else the scene's own Ticks, else DefaultTicks.</summary>
        public static int TicksFor(Spec s, int overrideTicks) =>
            overrideTicks > 0 ? overrideTicks : (s.ticks > 0 ? s.ticks : DefaultTicks);

        /// <summary>n plot origins on a pitch, row-major from the south-west, a half pitch (at least 12) from every edge.</summary>
        public static List<int[]> Grid(int sizeX, int sizeZ, int pitch, int n)
        {
            var o = new List<int[]>();
            if (pitch < 3) pitch = DefaultPitch;
            int m = Math.Max(12, pitch / 2 + 1);
            for (int z = m; z < sizeZ - m && o.Count < n; z += pitch)
                for (int x = m; x < sizeX - m && o.Count < n; x += pitch)
                    o.Add(new[] { x, z });
            return o;
        }

        /// <summary>"x,z;x,z;..." (a suite's Origins answer) -> origins; null when any entry is unreadable.</summary>
        public static List<int[]> ParseOrigins(string text)
        {
            var o = new List<int[]>();
            foreach (string e in (text ?? "").Split(';').Select(x => x.Trim()).Where(x => x.Length > 0))
            {
                string[] p = e.Split(',');
                if (p.Length != 2 || !int.TryParse(p[0].Trim(), NumberStyles.Integer, CultureInfo.InvariantCulture, out int x)
                    || !int.TryParse(p[1].Trim(), NumberStyles.Integer, CultureInfo.InvariantCulture, out int z))
                    return null;
                o.Add(new[] { x, z });
            }
            return o;
        }

        // ------------------------------------------------------------------ outside reads
        public sealed class OutsideCheck
        {
            public string kind, op, text;
            public int dx, dz, w, h, n;
        }

        public static readonly string[] OutsideKinds = { "haulables", "pawns", "colonists" };

        /// <summary>"kind dx,dz,w,h op n" joined by ';' (kind haulables | pawns | colonists; op >= | <= | ==): a vanilla count of
        /// that kind inside the rect at origin + (dx, dz). null (and why) when any clause is unreadable.</summary>
        public static List<OutsideCheck> ParseOutside(string spec, out string why)
        {
            why = null;
            var o = new List<OutsideCheck>();
            foreach (string clause in (spec ?? "").Split(';').Select(x => x.Trim()).Where(x => x.Length > 0))
            {
                string[] t = clause.Split(new[] { ' ' }, StringSplitOptions.RemoveEmptyEntries);
                if (t.Length != 4) { why = "'" + clause + "' is not 'kind dx,dz,w,h op n'"; return null; }
                if (!OutsideKinds.Contains(t[0])) { why = "kind '" + t[0] + "' is not one of " + string.Join("|", OutsideKinds); return null; }
                string[] r = t[1].Split(',');
                var v = new int[4];
                if (r.Length != 4 || Enumerable.Range(0, 4).Any(i => !int.TryParse(r[i], NumberStyles.Integer, CultureInfo.InvariantCulture, out v[i])))
                { why = "rect '" + t[1] + "' is not dx,dz,w,h"; return null; }
                if (v[2] < 1 || v[3] < 1) { why = "rect '" + t[1] + "' has no cells"; return null; }
                if (t[2] != ">=" && t[2] != "<=" && t[2] != "==") { why = "op '" + t[2] + "' is not >=, <= or =="; return null; }
                if (!int.TryParse(t[3], NumberStyles.Integer, CultureInfo.InvariantCulture, out int n) || n < 0) { why = "count '" + t[3] + "' is not a whole number >= 0"; return null; }
                o.Add(new OutsideCheck { kind = t[0], dx = v[0], dz = v[1], w = v[2], h = v[3], op = t[2], n = n, text = clause });
            }
            if (o.Count == 0) { why = "no clause"; return null; }
            return o;
        }

        /// <summary>The rect at origin + (dx, dz) when every cell of it is on a sizeX x sizeZ map; null otherwise (a read of
        /// part of the rect, or of none, would be a different measurement: the row is UNMEASURED, never a count).</summary>
        public static int[] RectOnMap(OutsideCheck c, int ox, int oz, int sizeX, int sizeZ)
        {
            long x0 = (long)ox + c.dx, z0 = (long)oz + c.dz, x1 = x0 + c.w - 1, z1 = z0 + c.h - 1;
            if (x0 < 0 || z0 < 0 || x1 >= sizeX || z1 >= sizeZ) return null;
            return new[] { (int)x0, (int)z0, c.w, c.h };
        }

        public static bool Holds(OutsideCheck c, int count) =>
            c.op == ">=" ? count >= c.n : c.op == "<=" ? count <= c.n : count == c.n;

        /// <summary>One outside row. count &lt; 0 means the read could not be made (no map): UNMEASURED, never FAIL.</summary>
        public static Row OutsideRow(string scene, OutsideCheck c, int count, string cause = null)
        {
            string check = "OUTSIDE " + c.kind + " " + c.dx + "," + c.dz + "," + c.w + "," + c.h;
            if (count < 0) return R(scene, check, Unmeasured, null, c.op + " " + c.n, "outside", cause ?? "the read could not be made");
            return R(scene, check, Holds(c, count) ? Pass : FailS, count.ToString(CultureInfo.InvariantCulture), c.op + " " + c.n, "outside");
        }

        // ------------------------------------------------------------------ stage and judge results
        /// <summary>What a scene method returned: the judge delegate, or (judge null) the refusal row.</summary>
        public static Delegate StageResult(string scene, object staged, out Row refusal)
        {
            refusal = null;
            if (staged is Delegate d && d.GetType().GetMethod("Invoke")?.GetParameters().Length == 0) return d;
            string text = staged as string;
            refusal = Unmeasured_(scene, "STAGE", text != null ? "staging refused: " + text :
                staged == null ? "the scene returned nothing (no judge)" : "the scene returned a " + staged.GetType().Name + ", not a judge");
            return null;
        }

        /// <summary>A judge's answer -> rows. A verdict line maps PASS -> PASS, FAIL -> FAIL, INVALID and ERROR -> UNMEASURED
        /// (the judge could not look: never a FAIL, never a PASS); anything unreadable is UNMEASURED with what it was.</summary>
        public static List<Row> Normalize(string scene, object judged)
        {
            var o = new List<Row>();
            if (judged is string line)
            {
                string t = line.Trim();
                string[] head = t.Split(new[] { ' ' }, 3);
                string word = head.Length > 0 ? head[0] : "";
                string detail = head.Length > 2 ? head[2] : (head.Length > 1 ? head[1] : "");
                bool whole = head.Length == 3 && head[1] == scene && head[2].Trim().Length > 0;
                if ((word == Pass || word == FailS) && !whole)
                    o.Add(R(scene, "VERDICT", Unmeasured, t, Pass, "scene", head.Length > 1 && head[1].Length > 0 && head[1] != scene
                        ? "the verdict names scene '" + head[1] + "', not '" + scene + "'"
                        : "a verdict line names its scene and says why: '" + word + " " + scene + " <detail>'"));
                else if (word == Pass || word == FailS) o.Add(R(scene, "VERDICT", word, detail, Pass, "scene"));
                else if (word == "INVALID" || word == "ERROR")
                    o.Add(R(scene, "VERDICT", Unmeasured, detail, Pass, "scene", word.ToLowerInvariant() + ": " + t));
                else o.Add(R(scene, "VERDICT", Unmeasured, t, Pass, "scene", "unreadable verdict line"));
                return o;
            }
            if (judged is IEnumerable rows && !(judged is string))
            {
                foreach (object x in rows)
                {
                    if (!(x is string[] a) || a.Length < 2)
                    {
                        o.Add(R(scene, "ROW", Unmeasured, x?.ToString(), null, "scene", "a row is not string[] {check, status, measured, expected}"));
                        continue;
                    }
                    string st = a[1] == Pass || a[1] == FailS || a[1] == Unmeasured ? a[1] : null;
                    string cause = st == null ? "status '" + a[1] + "' is not PASS, FAIL or UNMEASURED"
                        : st != Unmeasured && a.Length < 4 ? "a " + st + " row needs {check, status, measured, expected}; this one has " + a.Length + " columns"
                        : st == Unmeasured ? (a.Length > 4 && !string.IsNullOrWhiteSpace(a[4]) ? a[4] : "the scene could not measure it") : null;
                    o.Add(R(scene, a[0], cause != null ? Unmeasured : st, a.Length > 2 ? a[2] : null, a.Length > 3 ? a[3] : null, "scene", cause));
                }
                if (o.Count == 0) o.Add(R(scene, "ROWS", Unmeasured, null, null, "scene", "the judge returned no rows (empty is not a verdict)"));
                return o;
            }
            o.Add(R(scene, "VERDICT", Unmeasured, null, null, "scene",
                judged == null ? "the judge returned nothing" : "the judge returned a " + judged.GetType().Name));
            return o;
        }

        /// <summary>A short advance is not a verdict: when stepped &lt; wanted every row becomes UNMEASURED, outside rows
        /// included; the status it would have had is kept in the cause and its measured value stays in measured.</summary>
        public static List<Row> ShortAdvance(List<Row> rows, int stepped, int wanted, string why)
        {
            if (stepped >= wanted) return rows;
            foreach (Row r in rows)
            {
                if (r.status == Unmeasured) continue;
                r.cause = "advance short (" + stepped + " of " + wanted + " ticks" + (string.IsNullOrEmpty(why) ? "" : "; " + why) + "); was " + r.status;
                r.status = Unmeasured;
            }
            return rows;
        }

        /// <summary>The run's one word: FAIL if any row failed, else UNMEASURED if any could not be measured, else PASS;
        /// EMPTY when there are no rows at all (nothing ran, which is neither a pass nor a fail).</summary>
        public static string Overall(IEnumerable<Row> rows)
        {
            var l = rows.ToList();
            if (l.Count == 0) return "EMPTY";
            if (l.Any(r => r.status == FailS)) return FailS;
            if (l.Any(r => r.status != Pass)) return Unmeasured;
            return Pass;
        }

        // Clip: the tools' refusal and exception messages only; a row's measured and cause are evidence and stay whole
        public static string Clip(string s, int n = 400) => s == null ? null : (s.Length <= n ? s : s.Substring(0, n) + "...");
    }
}
