// Unit group for JawaBenchSceneRunnerCore (production file) and RMTestAttribute (production attribute). Prints
// "U <name> ok" or "U <name> FAIL <why>" per case and "U-count <n>" last; driven by
// src/RimMandrake/Utils/selftest_scene_runner_core.py.
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.Shared.SceneRunner;
using C = JawaBench.BridgeTools.JawaBenchSceneRunnerCore;

namespace Elsewhere
{
    // a second attribute with the same TYPE NAME in another namespace: the runner matches by name, so a mod's own copy counts
    [AttributeUsage(AttributeTargets.Method, AllowMultiple = true)]
    internal sealed class RMTestAttribute : Attribute
    {
        public RMTestAttribute(string name) { Name = name; }
        public string Name { get; }
        public int Ticks { get; set; }
        public string Outside { get; set; }
    }
}

namespace Misdeclared
{
    // a mod's copy whose Ticks is a string: discovery must refuse it, never read it as Ticks 0 (the default)
    [AttributeUsage(AttributeTargets.Method, AllowMultiple = true)]
    internal sealed class RMTestAttribute : Attribute
    {
        public RMTestAttribute(string name) { Name = name; }
        public string Name { get; }
        public string Ticks { get; set; }
        public string Outside { get; set; }
    }
}

namespace JawaBench.BridgeTools
{
    public static class GoodSuite
    {
        public static readonly List<string> Calls = new List<string>();

        [RMTest("alpha", Ticks = 900, Outside = "haulables -3,-5,7,2 >= 1")]
        [RMTest("alpha_control", Ticks = 900)]
        public static object Alpha(string scene, int x, int z)
        {
            Calls.Add(scene + "@" + x + "," + z);
            return (Func<object>)(() => "PASS " + scene + " staged at " + x + "," + z);
        }

        [Elsewhere.RMTest("beta")]
        public static object Beta(string scene, int x, int z) =>
            (Func<object>)(() => new List<string[]> { new[] { "B1", "PASS", "3", ">= 1" }, new[] { "B2", "FAIL", "0", ">= 1" } });

        [RMTest("refuses")]
        public static object Refuses(string scene, int x, int z) => "INVALID refuses site: a pond bed";

        public static object NotAScene(string scene, int x, int z) => null;
    }

    public sealed class BadSuite
    {
        [RMTest("instance")]
        public object Instance(string scene, int x, int z) => null;

        [RMTest("generic")]
        public static object Generic<T>(string scene, int x, int z) => null;

        [RMTest("returns_string")]
        public static string ReturnsString(string scene, int x, int z) => null;

        [Misdeclared.RMTest("misdeclared", Ticks = "900")]
        public static object MisdeclaredTicks(string scene, int x, int z) => null;

        [RMTest("wrong_shape")]
        public static object WrongShape(string scene) => null;

        [RMTest("dup")]
        public static object Dup1(string scene, int x, int z) => null;

        [RMTest("dup")]
        public static object Dup2(string scene, int x, int z) => null;

        [RMTest("bad_outside", Outside = "trees 0,0,1,1 >= 1")]
        public static object BadOutside(string scene, int x, int z) => null;

        [RMTest("too_long", Ticks = 30001)]
        public static object TooLong(string scene, int x, int z) => null;

        [RMTest("fine")]
        public static object Fine(string scene, int x, int z) => null;
    }

    internal static class Outer
    {
        public static class Inner
        {
            [RMTest("nested")]
            public static object Nested(string scene, int x, int z) => null;
        }
    }

    internal static class HiddenSuite
    {
        [RMTest("hidden")]
        public static object Hidden(string scene, int x, int z) => null;
    }

    internal static class Program
    {
        static int n;

        static void U(string name, bool ok, string why = "")
        {
            n++;
            Console.WriteLine("U " + name + (ok ? " ok" : " FAIL " + why));
        }

        static string Show(IEnumerable<C.Row> rows) =>
            string.Join(" | ", rows.Select(r => r.scene + "/" + r.check + "=" + r.status + "(" + r.measured + ";" + r.cause + ")"));

        public static object Echo(string s) => "PASS x " + s;

        static int Main()
        {
            // ---- discovery
            var probs = new List<string>();
            var specs = C.Discover(typeof(GoodSuite), probs);
            string names = string.Join(",", specs.Select(s => s.name));
            U("discover_good_suite_no_problems", probs.Count == 0, string.Join("; ", probs));
            U("discover_finds_every_attribute_in_declaration_order", names == "alpha,alpha_control,beta,refuses", names);
            U("discover_matches_attribute_by_type_name_any_namespace", specs.Any(s => s.name == "beta"), names);
            U("discover_ignores_unattributed_method", !specs.Any(s => s.method.Name == "NotAScene"), names);
            var a = specs.FirstOrDefault(s => s.name == "alpha");
            U("discover_reads_ticks_and_outside", a != null && a.ticks == 900 && a.outside == "haulables -3,-5,7,2 >= 1",
                a == null ? "no alpha" : a.ticks + " " + a.outside);
            var ac = specs.FirstOrDefault(s => s.name == "alpha_control");
            U("discover_two_attributes_one_method", ac != null && a != null && ac.method == a.method && string.IsNullOrEmpty(ac.outside));

            var bp = new List<string>();
            var bs = C.Discover(typeof(BadSuite), bp);
            string bj = string.Join("; ", bp);
            U("discover_refuses_wrong_signature_by_name", bp.Any(p => p.StartsWith("WrongShape:")), bj);
            U("discover_refuses_duplicate_name", bp.Any(p => p.StartsWith("dup: declared twice")), bj);
            U("discover_refuses_unreadable_outside", bp.Any(p => p.StartsWith("bad_outside: Outside unreadable")), bj);
            U("discover_refuses_ticks_over_cap", bp.Any(p => p.StartsWith("too_long: Ticks")), bj);
            U("discover_refuses_attributed_instance_method", bp.Any(p => p.StartsWith("Instance:")), bj);
            U("discover_refuses_generic_scene", bp.Any(p => p.StartsWith("Generic:")), bj);
            U("discover_refuses_non_object_return", bp.Any(p => p.StartsWith("ReturnsString:")), bj);
            U("discover_refuses_misdeclared_attribute_property_never_defaults", bp.Any(p => p.StartsWith("MisdeclaredTicks:") && p.Contains("Ticks")), bj);
            U("discover_refuses_a_suite_that_is_not_a_static_class", bp.Any(p => p.Contains("BadSuite: a suite must be a public static class")), bj);
            U("discover_keeps_the_good_scenes_and_reports_nine_problems", bs.Select(s => s.name).SequenceEqual(new[] { "dup", "fine" }) && bp.Count == 9,
                string.Join(",", bs.Select(s => s.name)) + " / " + bp.Count + ": " + bj);
            var hp = new List<string>();
            C.Discover(typeof(HiddenSuite), hp);
            U("discover_refuses_a_non_public_suite", hp.Any(p => p.Contains("a suite must be a public static class")), string.Join("; ", hp));
            var np = new List<string>();
            C.Discover(typeof(Outer.Inner), np);
            U("discover_refuses_a_public_suite_inside_a_hidden_type", np.Any(p => p.Contains("a suite must be a public static class")), string.Join("; ", np));

            // ---- selection and ticks
            var unk = new List<string>();
            var sel = C.Select(specs, " refuses, alpha ,nope", unk);
            U("select_keeps_list_order", string.Join(",", sel.Select(s => s.name)) == "refuses,alpha", string.Join(",", sel.Select(s => s.name)));
            U("select_reports_unknown", unk.SequenceEqual(new[] { "nope" }), string.Join(",", unk));
            var all = C.Select(specs, "", new List<string>());
            U("select_empty_is_every_scene", all.Count == specs.Count);
            var beta = specs.First(s => s.name == "beta");
            U("ticks_override_wins", C.TicksFor(a, 50) == 50);
            U("ticks_own_value", C.TicksFor(a, 0) == 900);
            U("ticks_default_when_unset", C.TicksFor(beta, 0) == C.DefaultTicks, C.TicksFor(beta, 0).ToString());

            // ---- plots
            var g = C.Grid(250, 250, 15, 4);
            U("grid_gives_n", g.Count == 4, g.Count.ToString());
            U("grid_row_major_from_south_west", g[0][0] == 12 && g[0][1] == 12 && g[1][0] == 27 && g[1][1] == 12,
                string.Join(";", g.Select(o => o[0] + "," + o[1])));
            var many = C.Grid(250, 250, 15, 10000);
            U("grid_stays_inside_the_margin", many.All(o => o[0] >= 12 && o[1] >= 12 && o[0] < 238 && o[1] < 238) && many.Count == 16 * 16,
                many.Count.ToString());
            U("grid_small_map_gives_fewer", C.Grid(30, 30, 15, 4).Count == 1, C.Grid(30, 30, 15, 4).Count.ToString());
            var po = C.ParseOrigins("12,12; 27,12");
            U("origins_parse", po != null && po.Count == 2 && po[1][0] == 27);
            U("origins_unreadable_is_null", C.ParseOrigins("12,12;x,3") == null && C.ParseOrigins("1,2,3") == null);
            U("origins_empty_is_empty_not_null", C.ParseOrigins("") is List<int[]> e0 && e0.Count == 0);

            // ---- outside reads
            var oc = C.ParseOutside("haulables -3,-5,7,2 >= 1; colonists 0,0,3,3 == 0", out string why);
            U("outside_parses_two_clauses", oc != null && oc.Count == 2 && oc[0].dx == -3 && oc[0].dz == -5 && oc[0].w == 7 && oc[0].h == 2
                && oc[1].kind == "colonists" && oc[1].op == "==", why);
            foreach (var bad in new[] { "", "haulables -3,-5,7 >= 1", "trees 0,0,1,1 >= 1", "pawns 0,0,0,1 >= 1", "pawns 0,0,1,1 > 1", "pawns 0,0,1,1 >= -1", "pawns 0,0,1,1 >= x", "pawns 0,0,1,1" })
                U("outside_refuses '" + bad + "'", C.ParseOutside(bad, out string w2) == null && !string.IsNullOrEmpty(w2), w2);
            var ge = C.ParseOutside("pawns 0,0,1,1 >= 2", out _)[0];
            var le = C.ParseOutside("pawns 0,0,1,1 <= 2", out _)[0];
            var eq = C.ParseOutside("pawns 0,0,1,1 == 2", out _)[0];
            var inMap = C.ParseOutside("haulables -3,-5,7,2 >= 1", out _)[0];
            var on = C.RectOnMap(inMap, 12, 12, 250, 250);
            U("rect_on_map_whole", on != null && on[0] == 9 && on[1] == 7 && on[2] == 7 && on[3] == 2, on == null ? "null" : string.Join(",", on));
            U("rect_partly_off_map_is_null_never_clipped", C.RectOnMap(inMap, 2, 12, 250, 250) == null && C.RectOnMap(inMap, 12, 3, 250, 250) == null
                && C.RectOnMap(inMap, 248, 12, 250, 250) == null && C.RectOnMap(inMap, 246, 12, 250, 250) != null);
            U("rect_wholly_off_map_is_null", C.RectOnMap(inMap, 400, 400, 250, 250) == null && C.RectOnMap(inMap, int.MaxValue, int.MaxValue, 250, 250) == null);
            U("outside_ops", C.Holds(ge, 2) && !C.Holds(ge, 1) && C.Holds(le, 2) && !C.Holds(le, 3) && C.Holds(eq, 2) && !C.Holds(eq, 3));
            var r1 = C.OutsideRow("s", oc[0], 3);
            var r0 = C.OutsideRow("s", oc[0], 0);
            var rU = C.OutsideRow("s", oc[0], -1, "no map");
            U("outside_row_pass_fail", r1.status == C.Pass && r1.source == "outside" && r1.measured == "3" && r0.status == C.FailS && r0.measured == "0",
                Show(new[] { r1, r0 }));
            U("outside_row_could_not_look_is_unmeasured_not_fail_not_zero", rU.status == C.Unmeasured && rU.measured == null && rU.cause == "no map", Show(new[] { rU }));

            // ---- stage results and judges, end to end through reflection
            GoodSuite.Calls.Clear();
            object staged = a.method.Invoke(null, new object[] { "alpha", 12, 27 });
            var judge = C.StageResult("alpha", staged, out var refusal);
            U("stage_delegate_is_the_judge", judge != null && refusal == null && GoodSuite.Calls.SequenceEqual(new[] { "alpha@12,27" }), string.Join(",", GoodSuite.Calls));
            var jr = C.Normalize("alpha", judge?.DynamicInvoke());
            U("judge_pass_line_is_one_pass_row", jr.Count == 1 && jr[0].status == C.Pass && jr[0].check == "VERDICT" && jr[0].measured == "staged at 12,27" && jr[0].source == "scene", Show(jr));
            var rs = specs.First(s => s.name == "refuses");
            var rj = C.StageResult("refuses", rs.method.Invoke(null, new object[] { "refuses", 1, 1 }), out var rr);
            U("stage_refusal_string_is_unmeasured_with_its_text", rj == null && rr != null && rr.status == C.Unmeasured && rr.cause.Contains("a pond bed"), rr == null ? "null" : rr.cause);
            C.StageResult("x", null, out var rn);
            U("stage_nothing_is_unmeasured", rn != null && rn.status == C.Unmeasured && rn.cause.Contains("no judge"));
            C.StageResult("x", 42, out var ri);
            U("stage_non_delegate_is_unmeasured", ri != null && ri.status == C.Unmeasured && ri.cause.Contains("Int32"));
            C.StageResult("x", (Func<int, object>)(k => null), out var rd);
            U("stage_delegate_with_arguments_is_not_a_judge", rd != null && rd.status == C.Unmeasured);
            var closed = (Func<object>)Delegate.CreateDelegate(typeof(Func<object>), "bound", typeof(Program).GetMethod(nameof(Echo)));
            var cj = C.StageResult("x", closed, out var rc);
            U("stage_closed_static_delegate_is_a_judge", cj != null && rc == null && (string)cj.DynamicInvoke() == "PASS x bound", rc == null ? "" : rc.cause);
            var br = C.Normalize("beta", ((Delegate)beta.method.Invoke(null, new object[] { "beta", 0, 0 })).DynamicInvoke());
            U("judge_rows_keep_their_status", br.Count == 2 && br[0].check == "B1" && br[0].status == C.Pass && br[1].status == C.FailS && br[1].measured == "0", Show(br));

            // ---- verdict line mapping: could-not-look never becomes FAIL or PASS
            var f = C.Normalize("s", "FAIL s goods 0 in pit");
            U("verdict_fail_is_fail", f.Count == 1 && f[0].status == C.FailS && f[0].measured == "goods 0 in pit", Show(f));
            // the verdict's evidence is kept whole (live 2026-11-26: a 400-character cut dropped the storeroom verdict's
            // container, heavy, pit and cover clauses from the evidence JSON)
            string longDetail = "east=True [" + new string('x', 700) + "] pit=True [pawns=pS:1] cover=True";
            var lp = C.Normalize("s", "PASS s " + longDetail);
            var lr = C.Normalize("s", new[] { new[] { "R1", C.Pass, longDetail, "PASS" } });
            var li = C.Normalize("s", "INVALID s " + longDetail);
            U("verdict_and_row_evidence_kept_whole", lp[0].measured == longDetail && lr[0].measured == longDetail
                && li[0].measured == longDetail && li[0].cause.EndsWith("cover=True"), Show(lp));
            var inv = C.Normalize("s", "INVALID s not at rest after 900 ticks");
            U("verdict_invalid_is_unmeasured_with_cause", inv[0].status == C.Unmeasured && inv[0].cause.StartsWith("invalid:") && inv[0].cause.Contains("not at rest"), Show(inv));
            var er = C.Normalize("s", "ERROR s NullReferenceException: x");
            U("verdict_error_is_unmeasured_with_cause", er[0].status == C.Unmeasured && er[0].cause.StartsWith("error:"), Show(er));
            var gb = C.Normalize("s", "STAGED s at 1,2");
            U("verdict_unreadable_is_unmeasured", gb[0].status == C.Unmeasured && gb[0].cause == "unreadable verdict line", Show(gb));
            var noDetail = C.Normalize("s", "PASS s");
            U("verdict_without_detail_is_unmeasured", noDetail[0].status == C.Unmeasured, Show(noDetail));
            var noName = C.Normalize("s", "PASS  goods in pit");
            U("verdict_with_blank_name_is_unmeasured", noName[0].status == C.Unmeasured, Show(noName));
            var otherName = C.Normalize("s", "PASS other goods in pit");
            U("verdict_naming_another_scene_is_unmeasured", otherName[0].status == C.Unmeasured && otherName[0].cause.Contains("other"), Show(otherName));
            var bare = C.Normalize("s", "PASS");
            U("verdict_bare_pass_word_is_unmeasured", bare[0].status == C.Unmeasured && bare[0].cause.Contains("names its scene"), Show(bare));
            var shortRow = C.Normalize("s", new List<string[]> { new[] { "check", "PASS" } });
            U("judge_pass_row_without_measured_expected_is_unmeasured", shortRow[0].status == C.Unmeasured && shortRow[0].cause.Contains("columns"), Show(shortRow));
            var blank = C.Normalize("s", new List<string[]> { new[] { "X", "UNMEASURED", null, ">= 1", "  " } });
            U("judge_unmeasured_blank_cause_gets_the_fallback", blank[0].status == C.Unmeasured && !string.IsNullOrWhiteSpace(blank[0].cause), Show(blank));
            var emptyRows = C.Normalize("s", new List<string[]>());
            U("judge_empty_rows_is_unmeasured_never_pass", emptyRows.Count == 1 && emptyRows[0].status == C.Unmeasured, Show(emptyRows));
            var badStatus = C.Normalize("s", new List<string[]> { new[] { "X", "OK", "1" } });
            U("judge_row_status_outside_vocabulary_is_unmeasured", badStatus[0].status == C.Unmeasured && badStatus[0].cause.Contains("'OK'"), Show(badStatus));
            var um = C.Normalize("s", new List<string[]> { new[] { "X", "UNMEASURED", null, ">= 1" } });
            U("judge_unmeasured_row_gets_a_cause", um[0].status == C.Unmeasured && !string.IsNullOrEmpty(um[0].cause), Show(um));
            var nn = C.Normalize("s", null);
            U("judge_null_is_unmeasured", nn.Count == 1 && nn[0].status == C.Unmeasured && nn[0].cause == "the judge returned nothing", Show(nn));

            // ---- short advance and the run's one word
            var sa = C.ShortAdvance(new List<C.Row> { C.R("s", "V", C.Pass, "x", null, "scene"), C.R("s", "O", C.FailS, "0", ">= 1", "outside") }, 400, 900, "a tick threw");
            U("short_advance_makes_every_row_unmeasured", sa.All(r => r.status == C.Unmeasured) && sa[0].cause.Contains("400 of 900") && sa[0].cause.EndsWith("was PASS")
                && sa[1].cause.EndsWith("was FAIL"), Show(sa));
            var full = C.ShortAdvance(new List<C.Row> { C.R("s", "V", C.Pass, "x", null, "scene") }, 900, 900, null);
            U("full_advance_keeps_rows", full[0].status == C.Pass && full[0].cause == null);
            U("overall_fail_wins", C.Overall(new[] { C.R("a", "1", C.Pass, null, null, "scene"), C.R("a", "2", C.Unmeasured, null, null, "scene"), C.R("a", "3", C.FailS, null, null, "scene") }) == C.FailS);
            U("overall_unmeasured_over_pass", C.Overall(new[] { C.R("a", "1", C.Pass, null, null, "scene"), C.R("a", "2", C.Unmeasured, null, null, "scene") }) == C.Unmeasured);
            U("overall_pass", C.Overall(new[] { C.R("a", "1", C.Pass, null, null, "scene") }) == C.Pass);
            U("overall_no_rows_is_empty_not_pass", C.Overall(new C.Row[0]) == "EMPTY");
            var d = C.R("s", "c", C.Pass, "1", ">= 1", "outside").ToDict();
            U("row_dict_has_the_seven_columns", new[] { "scene", "check", "status", "measured", "expected", "source", "cause" }.All(d.ContainsKey) && d.Count == 7);

            Console.WriteLine("U-count " + n);
            return 0;
        }
    }
}
