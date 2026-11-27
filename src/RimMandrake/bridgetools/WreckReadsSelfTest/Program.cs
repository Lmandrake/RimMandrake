// Units of JawaBenchWreckReadsCore.cs (the decisions of jawa/thing_set_sample, jawa/install_blueprint, jawa/study_record and
// jawa/processor_fill). Prints "U <name> ok" or "U <name> FAIL <why>" per unit and "U-count <n>" last; driven by
// src/RimMandrake/bridgetools/selftest_wreck_reads.py, which plants one fault per rule and sees its unit go red.
using System;
using System.Collections.Generic;
using C = JawaBench.BridgeTools.JawaBenchWreckReadsCore;

namespace JawaBench.BridgeTools
{
    internal static class Program
    {
        static int n;

        static void U(string name, Func<string> body)
        {
            n++;
            string why;
            try { why = body(); }
            catch (Exception e) { why = e.GetType().Name + ": " + e.Message; }
            Console.WriteLine("U " + name + (why == null ? " ok" : " FAIL " + why));
        }

        static List<KeyValuePair<string, int>> Run(params object[] pairs)
        {
            var l = new List<KeyValuePair<string, int>>();
            for (int i = 0; i < pairs.Length; i += 2) l.Add(new KeyValuePair<string, int>((string)pairs[i], (int)pairs[i + 1]));
            return l;
        }

        static C.TallyRow Row(C.Tally t, string def)
        {
            foreach (var r in t.Rows()) if (r.def == def) return r;
            return null;
        }

        static int Main()
        {
            U("runs_refused_below_one", () => C.RunsRefusal(0) != null && C.RunsRefusal(-3) != null && C.RunsRefusal(1) == null
                ? null : "0 or -3 accepted, or 1 refused");
            U("runs_refused_over_cap", () => C.RunsRefusal(C.MaxRuns) == null && C.RunsRefusal(C.MaxRuns + 1) != null
                ? null : "the cap is not exactly MaxRuns");
            U("tally_empty_apart_from_failed", () =>
            {
                var t = new C.Tally();
                t.AddRun(Run());
                t.AddRun(null, "threw");
                t.AddRun(Run("Steel", 5));
                return t.runs == 3 && t.emptyRuns == 1 && t.failedRuns == 1 && t.failures.Count == 1
                    ? null : "runs " + t.runs + " empty " + t.emptyRuns + " failed " + t.failedRuns;
            });
            U("tally_runs_with_counts_once_per_run", () =>
            {
                var t = new C.Tally();
                t.AddRun(Run("Steel", 5, "Steel", 3, "Gold", 1));
                t.AddRun(Run("Steel", 2));
                var s = Row(t, "Steel");
                return s != null && s.runsWith == 2 && s.things == 3 && Row(t, "Gold").runsWith == 1
                    ? null : "Steel runsWith " + (s == null ? -1 : s.runsWith) + " things " + (s == null ? -1 : s.things);
            });
            U("tally_count_sums_stacks", () =>
            {
                var t = new C.Tally();
                t.AddRun(Run("Steel", 5, "Steel", 3));
                t.AddRun(Run("Steel", 0));   // a stack count the game reports as 0 is still one thing
                var s = Row(t, "Steel");
                return s.count == 9 ? null : "count " + s.count + ", want 9";
            });
            U("tally_rows_most_often_first", () =>
            {
                var t = new C.Tally();
                t.AddRun(Run("B", 1));
                t.AddRun(Run("A", 1, "B", 1));
                t.AddRun(Run("C", 1));
                var r = t.Rows();
                return r[0].def == "B" && r[1].def == "A" && r[2].def == "C" ? null : "order " + r[0].def + r[1].def + r[2].def;
            });
            U("install_minified_on_map_or_held", () =>
            {
                string w;
                var a = C.Classify(true, true, false, true, false, false, true, out w);
                var b = C.Classify(true, false, true, true, false, false, true, out w);
                return a == C.InstallMode.Install && b == C.InstallMode.Install ? null : a + "/" + b;
            });
            U("install_refuses_minified_nowhere", () =>
            {
                string w;
                var a = C.Classify(true, false, false, true, false, false, true, out w);
                var b = C.Classify(true, true, false, false, false, false, true, out w);
                return a == C.InstallMode.Refused && b == C.InstallMode.Refused && w != null ? null : a + "/" + b;
            });
            U("reinstall_standing_minifiable", () =>
            {
                string w;
                var a = C.Classify(false, true, false, true, true, true, true, out w);
                return a == C.InstallMode.Reinstall ? null : a.ToString();
            });
            U("refuse_not_minifiable_building", () =>
            {
                string w;
                var a = C.Classify(false, true, false, true, true, false, true, out w);   // a wall: standing, no carried form
                var b = C.Classify(false, false, false, false, false, false, true, out w);
                return a == C.InstallMode.Refused && b == C.InstallMode.Refused && w != null ? null : a + "/" + b;
            });
            U("install_refuses_another_map", () =>
            {
                string w1, w2;   // the carried form lies spawned on the away map; the standing building stands there
                var a = C.Classify(true, true, false, true, false, false, false, out w1);
                var b = C.Classify(false, true, false, true, true, true, false, out w2);
                return a == C.InstallMode.Refused && b == C.InstallMode.Refused && w1 != null && w2 != null ? null : a + "/" + b;
            });
            U("study_no_record_not_complete", () =>
            {
                var s = C.StudyStatus(true, false, 0, 1);
                var c = C.StudyStatus(false, false, 0, 0);
                return s == C.NoRecord && c == C.NoComp ? null : s + "/" + c;
            });
            U("study_partial_complete", () =>
            {
                var p = C.StudyStatus(true, true, 1, 3);
                var q = C.StudyStatus(true, true, 3, 3);
                return p == C.Partial && q == C.Complete ? null : p + "/" + q;
            });
            U("completed_count_only_complete", () =>
            {
                int k = C.CompletedCount(new[] { C.Complete, C.NoRecord, C.Partial, C.NoComp, C.Complete });
                return k == 2 ? null : "counted " + k;
            });
            U("fill_wants_shortfall", () =>
            {
                var l = C.Plan("Steel", null, null, 30, 100, null);
                return l.want == 70 && l.skip == null ? null : "want " + l.want + " skip " + l.skip;
            });
            U("fill_skips_net_owner", () =>
            {
                var l = C.Plan(null, null, "VFEFactory_Slag", 0, 100, null);
                return l.want == 0 && l.skip != null ? null : "a net owner was filled: want " + l.want;
            });
            U("fill_category_uses_first_def", () =>
            {
                var l = C.Plan(null, "StoneChunks", null, 0, 2, "ChunkGranite");
                var m = C.Plan(null, "Empty", null, 0, 2, null);
                return l.def == "ChunkGranite" && l.want == 2 && m.skip != null ? null : "def " + l.def + " want " + l.want;
            });
            U("fill_full_skipped", () =>
            {
                var l = C.Plan("Steel", null, null, 100, 100, null);
                var o = C.Plan("Steel", null, null, 120, 100, null);
                return l.want == 0 && l.skip != null && o.want == 0 ? null : "want " + l.want + "/" + o.want;
            });
            U("caravan_over_only_above_capacity", () =>
                !C.OverCapacity(70f, 70f) && C.OverCapacity(70.5f, 70f) && !C.OverCapacity(10f, 70f) ? null : "the edge is wrong");
            U("form_refuses_no_pawn_or_elsewhere", () =>
                C.FormRefusal(0, 0, 0, 1) != null && C.FormRefusal(2, 1, 0, 1) != null && C.FormRefusal(2, 0, 1, 1) != null
                && C.FormRefusal(2, 0, 0, 0) != null && C.FormRefusal(2, 0, 0, 1) == null ? null : "a bad formation was accepted, or a good one refused");
            U("traverse_mode_named_or_refused", () =>
                C.TraverseModeName(null) == "PassDoors" && C.TraverseModeName("nopassclosedDOORS") == "NoPassClosedDoors"
                && C.TraverseModeName("Dig") == null && C.TraverseModeName("PassAllDestroyableThings") == null
                ? null : "default " + C.TraverseModeName(null) + ", unknown " + C.TraverseModeName("Dig"));
            Console.WriteLine("U-count " + n);
            return 0;
        }
    }
}
