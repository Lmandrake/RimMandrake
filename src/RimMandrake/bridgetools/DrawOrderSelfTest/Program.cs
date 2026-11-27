// Units of JawaBenchDrawOrderCore.cs (the pure half of jawa/cell_draw_census's sort reading and of jawa/pawn_render_nodes).
// Prints "U <name> ok" or "U <name> FAIL <why>" per unit and "U-count <n>" last; driven by
// src/RimMandrake/bridgetools/selftest_draw_order.py, which plants one fault per rule and sees its unit go red.
using System;
using System.Collections.Generic;
using C = JawaBench.BridgeTools.JawaBenchDrawOrderCore;

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

        static bool Near(float a, float b) => Math.Abs(a - b) < 1e-5f;

        static int Main()
        {
            // a sub-mesh with no vertices is a reading that could not look, never a span at 0
            U("span_empty_is_empty", () =>
            {
                var s = C.Span(new List<float>());
                return s.Empty && s.n == 0 ? null : "an empty list read n=" + s.n + " empty=" + s.Empty;
            });
            U("span_min_max_of_every_vertex", () =>
            {
                var s = C.Span(new List<float> { 8.78f, 7.68f, 8.10f, 8.78f });
                return !s.Empty && s.n == 4 && Near(s.min, 7.68f) && Near(s.max, 8.78f)
                    ? null : "n " + s.n + " min " + s.min + " max " + s.max;
            });
            U("span_first_vertex_counts", () =>
            {
                // the first value seeds both ends: a span of one value is that value, not 0
                var s = C.Span(new List<float> { 9.5f });
                return s.n == 1 && Near(s.min, 9.5f) && Near(s.max, 9.5f) ? null : "min " + s.min + " max " + s.max;
            });
            U("span_centre_is_mid_of_ends", () =>
            {
                // Unity's mesh bounds centre: the middle of the extremes, not the mean of the vertices
                var s = C.Span(new List<float> { 7.68f, 7.68f, 7.68f, 8.78f });
                return Near(s.Centre, (7.68f + 8.78f) * 0.5f) ? null : "centre " + s.Centre;
            });
            // the camera looks down -y: a larger y is nearer the camera
            U("relation_above_below", () =>
                C.Relation(8.78f, 8.41f, C.Eps) == "above" && C.Relation(7.68f, 8.41f, C.Eps) == "below"
                    ? null : "8.78 vs 8.41 read " + C.Relation(8.78f, 8.41f, C.Eps) + ", 7.68 read " + C.Relation(7.68f, 8.41f, C.Eps));
            U("relation_level_inside_eps", () =>
                C.Relation(8.41f + C.Eps * 0.5f, 8.41f, C.Eps) == "level" && C.Relation(8.41f - C.Eps * 0.5f, 8.41f, C.Eps) == "level"
                    ? null : "half an eps apart read " + C.Relation(8.41f + C.Eps * 0.5f, 8.41f, C.Eps));
            U("relation_just_past_eps", () =>
                C.Relation(8.41f + C.Eps * 2f, 8.41f, C.Eps) == "above" && C.Relation(8.41f - C.Eps * 2f, 8.41f, C.Eps) == "below"
                    ? null : "two eps apart read " + C.Relation(8.41f + C.Eps * 2f, 8.41f, C.Eps));
            U("eps_below_one_node_layer", () =>
                // a pawn's render nodes sit one PawnRenderUtility layer (0.0003658537) apart: eps must tell them apart
                C.Eps > 0f && C.Eps < 0.0003658537f ? null : "Eps " + C.Eps);
            // a mesh whose vertices lie on both sides of a y sorts as one draw: some of it is on the wrong side of that y
            U("straddles_both_sides", () =>
                C.Straddles(C.Span(new List<float> { 7.68f, 8.78f }), 8.41f, C.Eps) ? null : "7.68..8.78 does not straddle 8.41");
            U("straddles_not_one_side", () =>
                !C.Straddles(C.Span(new List<float> { 8.78f, 8.80f }), 8.41f, C.Eps)
                && !C.Straddles(C.Span(new List<float> { 7.60f, 7.68f }), 8.41f, C.Eps)
                    ? null : "a span on one side reads as straddling");
            U("straddles_empty_never", () =>
                !C.Straddles(C.Span(new List<float>()), 8.41f, C.Eps) ? null : "an empty span straddles");
            U("straddles_touching_end_not", () =>
                // a span that ends at the probe y (within eps) does not reach past it
                !C.Straddles(C.Span(new List<float> { 8.41f, 8.78f }), 8.41f, C.Eps) ? null : "8.41..8.78 straddles 8.41");
            // a pawn's draw path this frame
            U("path_not_prerendered", () => C.DrawPath(false, false, false) == "notPreRendered" && C.DrawPath(false, true, true) == "notPreRendered"
                ? null : "invalid results read " + C.DrawPath(false, true, true));
            U("path_hidden", () => C.DrawPath(true, false, true) == "hidden" && C.DrawPath(true, false, false) == "hidden"
                ? null : "draw=false read " + C.DrawPath(true, false, false));
            U("path_cached_atlas", () => C.DrawPath(true, true, true) == "cachedAtlas" ? null : "useCached read " + C.DrawPath(true, true, true));
            U("path_nodes", () => C.DrawPath(true, true, false) == "nodes" ? null : "nodes read " + C.DrawPath(true, true, false));
            // jawa/material_queue
            U("queue_read_and_default_allowed", () => C.QueueRefusal(C.ReadOnly) == null && C.QueueRefusal(C.ShaderQueue) == null
                ? null : "-2 or -1 refused");
            U("queue_range_ends_allowed", () => C.QueueRefusal(0) == null && C.QueueRefusal(C.MaxQueue) == null && C.QueueRefusal(2450) == null
                ? null : "0, 2450 or MaxQueue refused");
            U("queue_outside_refused", () => C.QueueRefusal(-3) != null && C.QueueRefusal(C.MaxQueue + 1) != null
                ? null : "-3 or MaxQueue+1 accepted");
            U("picks_by_id_only", () => C.Picks(7, "Cable", 7, "zzz") && !C.Picks(8, "Cable", 7, "Cable")
                ? null : "an id given did not decide alone");
            U("picks_by_name_part_case_blind", () => C.Picks(1, "Scrapper/RM_Cable", 0, "rm_cable") && !C.Picks(1, "Post", 0, "cable")
                ? null : "a name part did not pick, or picked a stranger");
            U("picks_nothing_without_key", () => !C.Picks(1, "Cable", 0, "") && !C.Picks(1, "Cable", 0, null)
                ? null : "no id and no name picked a material");
            Console.WriteLine("U-count " + n);
            return 0;
        }
    }
}
