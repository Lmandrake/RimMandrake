// Unit group for JawaBenchWorldArgsCore (production file). Prints "U <name> ok" or
// "U <name> FAIL <why>" per case and "U-count <n>" last; driven by
// src/RimMandrake/Utils/selftest_world_args_core.py.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using C = JawaBench.BridgeTools.JawaBenchWorldArgsCore;

namespace JawaBench.BridgeTools
{
    internal static class Program
    {
        static int n;

        static void U(string name, bool ok, string why = "")
        {
            n++;
            Console.WriteLine("U " + name + (ok ? " ok" : " FAIL " + why));
        }

        static string J(List<int> l) => string.Join(",", l.Take(12)) + (l.Count > 12 ? "...(" + l.Count + ")" : "");
        static string E(List<string> e) => string.Join(" | ", e);

        static int Main()
        {
            const int N = 21872;   // Ash'karr surface tile count
            List<string> e; List<int> r;

            // ---------------- D1: ranges are bounded by the grid, never by the caller
            var sw = Stopwatch.StartNew();
            e = new List<string>(); r = C.ParseTileIds(null, "0-2147483647", N, e);
            sw.Stop();
            U("range.intmax_terminates_and_clips", r.Count == N && r[0] == 0 && r[N - 1] == N - 1 && sw.ElapsedMilliseconds < 2000, J(r) + " " + sw.ElapsedMilliseconds + "ms");
            U("range.intmax_clip_reported", e.Count == 1 && e[0].Contains("clipped to 0-21871"), E(e));
            e = new List<string>(); r = C.ParseTileIds(null, "2147483647-0", N, e);
            U("range.reversed_intmax", r.Count == N && e.Count == 1, J(r) + " " + E(e));
            e = new List<string>(); r = C.ParseTileIds(null, "0-2000000000", N, e);
            U("range.huge_no_gb_alloc", r.Count == N, J(r));
            e = new List<string>(); r = C.ParseTileIds(null, "10-14", N, e);
            U("range.plain", J(r) == "10,11,12,13,14" && e.Count == 0, J(r) + " " + E(e));
            e = new List<string>(); r = C.ParseTileIds(null, "14-10", N, e);
            U("range.reversed_ascends", J(r) == "10,11,12,13,14" && e.Count == 0, J(r));
            e = new List<string>(); r = C.ParseTileIds(null, " 3 - 3 ", N, e);
            U("range.single_and_trimmed", J(r) == "3" && e.Count == 0, J(r) + " " + E(e));
            e = new List<string>(); r = C.ParseTileIds(null, "21870-21880", N, e);
            U("range.tail_clipped", J(r) == "21870,21871" && e.Count == 1 && e[0].Contains("clipped"), J(r) + " " + E(e));
            e = new List<string>(); r = C.ParseTileIds(null, "30000-40000", N, e);
            U("range.entirely_off_grid", r.Count == 0 && e.Count == 1 && e[0].Contains("entirely outside"), E(e));
            e = new List<string>(); r = C.ParseTileIds(null, "-5-3", N, e);
            U("range.negative_is_malformed", r.Count == 0 && e.Count == 1 && e[0].StartsWith("Bad range"), E(e));
            e = new List<string>(); r = C.ParseTileIds(null, "abc", N, e);
            U("range.garbage", r.Count == 0 && e.Count == 1 && e[0].StartsWith("Bad range"), E(e));
            e = new List<string>(); r = C.ParseTileIds(null, "1-2-3", N, e);
            U("range.three_parts", r.Count == 0 && e.Count == 1, E(e));
            e = new List<string>(); r = C.ParseTileIds(null, "0-99", N, e, maxIds: 50);
            U("range.over_hard_cap_refused_whole", r.Count == 0 && e.Count == 1 && e[0].Contains("limit"), J(r) + " " + E(e));
            e = new List<string>(); r = C.ParseTileIds("1,2", "0-48", N, e, maxIds: 50);
            U("range.cap_counts_listed_ids", r.Count == 2 && e.Count == 1 && e[0].Contains("limit"), J(r) + " " + E(e));
            e = new List<string>(); r = C.ParseTileIds(null, "0-49", N, e, maxIds: 50);
            U("range.exactly_at_cap", r.Count == 50 && e.Count == 0, J(r) + " " + E(e));
            e = new List<string>(); r = C.ParseTileIds(null, "0-10", 0, e);
            U("grid.empty_refused", r.Count == 0 && e.Count == 1 && e[0].Contains("no tiles"), E(e));
            e = new List<string>(); r = C.ParseTileIds(null, "0-10", 1, e);
            U("grid.one_tile", J(r) == "0" && e.Count == 1, J(r) + " " + E(e));

            // ---------------- D6: list tokens - every drop is named
            e = new List<string>(); r = C.ParseTileIds("14,abc,7368", null, N, e);
            U("list.bad_token_named", J(r) == "14,7368" && e.Count == 1 && e[0] == "Not a tile id: 'abc'", J(r) + " " + E(e));
            e = new List<string>(); r = C.ParseTileIds("5,-1,21872,21871", null, N, e);
            U("list.off_grid_named", J(r) == "5,21871" && e.Count == 2 && e.All(x => x.Contains("out of range")), J(r) + " " + E(e));
            e = new List<string>(); r = C.ParseTileIds("1,,2, ", null, N, e);
            U("list.empty_tokens_skipped_quietly", J(r) == "1,2" && e.Count == 0, J(r) + " " + E(e));
            e = new List<string>(); r = C.ParseTileIds("7,7,3", null, N, e);
            U("list.order_and_duplicates_kept", J(r) == "7,7,3", J(r));
            e = new List<string>(); r = C.ParseTileIds("99999999999", null, N, e);
            U("list.int_overflow_token_named", r.Count == 0 && e.Count == 1 && e[0].StartsWith("Not a tile id"), E(e));
            e = new List<string>(); r = C.ParseTileIds("1.5", null, N, e);
            U("list.float_token_named", r.Count == 0 && e.Count == 1, E(e));
            e = new List<string>(); r = C.ParseTileIds("1,2,3,4", null, N, e, maxIds: 3);
            U("list.hard_cap", J(r) == "1,2,3" && e.Count == 1 && e[0].StartsWith("Too many"), J(r) + " " + E(e));
            e = new List<string>(); r = C.ParseTileIds("1,2", "4-5", N, e);
            U("list_plus_range", J(r) == "1,2,4,5" && e.Count == 0, J(r));
            e = new List<string>(); r = C.ParseTileIds(null, null, N, e);
            U("nothing_given", r.Count == 0 && e.Count == 0, E(e));
            r = C.ParseTileIds("x", null, N, null);
            U("null_errors_list_tolerated", r.Count == 0);

            // ---------------- object ids (not clamped to any grid)
            e = new List<string>(); r = C.ParseIntList("100, 2147483647 ,-4", "a world object id", e);
            U("ints.parse", J(r) == "100,2147483647,-4" && e.Count == 0, J(r) + " " + E(e));
            e = new List<string>(); r = C.ParseIntList("12,x1", "a world object id", e);
            U("ints.bad_named", J(r) == "12" && e.Count == 1 && e[0] == "Not a world object id: 'x1'", J(r) + " " + E(e));
            e = new List<string>(); r = C.ParseIntList(null, "x", e);
            U("ints.null_empty", r.Count == 0 && e.Count == 0);

            // ---------------- D5: finite numbers
            float v;
            U("finite.nan", !C.IsFinite(float.NaN));
            U("finite.posinf", !C.IsFinite(float.PositiveInfinity));
            U("finite.neginf", !C.IsFinite(float.NegativeInfinity));
            U("finite.ok", C.IsFinite(-8192f) && C.IsFinite(0f) && C.IsFinite(float.MaxValue));
            U("parse.NaN_refused", !C.TryParseFiniteFloat("NaN", out v));
            U("parse.Infinity_refused", !C.TryParseFiniteFloat("Infinity", out v) && !C.TryParseFiniteFloat("-Infinity", out v));
            U("parse.overflow_refused", !C.TryParseFiniteFloat("1e999", out v));
            U("parse.invariant_ok", C.TryParseFiniteFloat("12.5", out v) && v == 12.5f);
            U("parse.exponent_ok", C.TryParseFiniteFloat("-1.5e3", out v) && v == -1500f);
            U("parse.comma_decimal_refused", !C.TryParseFiniteFloat("12,5", out v));
            U("parse.garbage_refused", !C.TryParseFiniteFloat("abc", out v) && !C.TryParseFiniteFloat(null, out v));
            var nf = C.NonFinite(new KeyValuePair<string, float?>("elevation", float.NaN),
                                 new KeyValuePair<string, float?>("rainfall", 5f),
                                 new KeyValuePair<string, float?>("pollution", null),
                                 new KeyValuePair<string, float?>("temperature", float.PositiveInfinity));
            U("nonfinite.names_only_bad", nf.Count == 2 && nf[0] == "elevation=NaN" && nf[1].StartsWith("temperature="), string.Join(";", nf));
            U("nonfinite.none", C.NonFinite().Count == 0 && C.NonFinite(null).Count == 0);

            // ---------------- features import: match by name, never double (FEATURES_IMPORT_FIX_REGIONS_SEEING_DOUBLE)
            var ex = new List<string> { "Pan", "Slough", "Knuckles", null, "Old" };
            var fp = C.PlanFeatureImport(new List<string> { "Pan", "Slough", "Knuckles", "Newland" }, ex, false);
            U("fimport.update_by_name", fp.Update.Count == 3 && fp.Update["Pan"] == 0 && fp.Update["Knuckles"] == 2, string.Join(",", fp.Update.Keys));
            U("fimport.create_only_new", fp.Create.Count == 1 && fp.Create[0] == "Newland", string.Join(",", fp.Create));
            U("fimport.untouched_counted", fp.Untouched == 2 && fp.Removed == 0 && fp.Ambiguous.Count == 0, fp.Untouched + "/" + fp.Removed);
            var names71 = Enumerable.Range(0, 71).Select(i => "R" + i).ToList();
            fp = C.PlanFeatureImport(names71, names71, false);
            U("fimport.rerun_71_stays_71", fp.Create.Count == 0 && fp.Update.Count == 71 && fp.Untouched == 0, fp.Create.Count + " created");
            fp = C.PlanFeatureImport(names71, names71, true);
            U("fimport.clear_creates_all", fp.Create.Count == 71 && fp.Update.Count == 0 && fp.Removed == 71, fp.Create.Count + "/" + fp.Removed);
            fp = C.PlanFeatureImport(new List<string> { "Pan" }, new List<string> { "Pan", "Pan" }, false);
            U("fimport.duplicate_existing_refused", fp.Ambiguous.Count == 1 && fp.Ambiguous[0] == "Pan x2" && fp.Update.Count == 0, string.Join(",", fp.Ambiguous));
            fp = C.PlanFeatureImport(new List<string> { "Pan", "Pan", "" }, new List<string>(), false);
            U("fimport.csv_dupes_once", fp.Create.Count == 1, fp.Create.Count.ToString());
            fp = C.PlanFeatureImport(new List<string> { "pan" }, new List<string> { "Pan" }, false);
            U("fimport.name_match_is_ordinal", fp.Create.Count == 1 && fp.Update.Count == 0, fp.Create.Count.ToString());

            Func<string, bool> fullList = d => d == "Desert" || d == "Ocean";
            var used = Enumerable.Repeat("Desert", 71).ToList();
            string ferr;
            var fdn = C.ResolveFeatureDef(null, fullList, used, 3, out ferr);
            U("fdef.missing_default_refused", fdn == null && ferr.Contains("'Region' does not exist") && ferr.Contains("Desert x71"), ferr);
            fdn = C.ResolveFeatureDef(null, fullList, used, 0, out ferr);
            U("fdef.no_create_needs_no_def", fdn == "" && ferr == null, ferr);
            fdn = C.ResolveFeatureDef("Region", fullList, used, 0, out ferr);
            U("fdef.named_missing_refused_even_updating", fdn == null && ferr.Contains("no FeatureDef 'Region'"), ferr);
            fdn = C.ResolveFeatureDef(" Desert ", fullList, used, 3, out ferr);
            U("fdef.explicit_ok", fdn == "Desert" && ferr == null, fdn);
            fdn = C.ResolveFeatureDef(null, d => d == "Region", new List<string>(), 3, out ferr);
            U("fdef.default_when_present", fdn == "Region", fdn);

            Console.WriteLine("U-count " + n);
            return 0;
        }
    }
}
