using System;
using System.Collections.Generic;

// _Shared/SlackGeometry (hose port step 1): linked by GimmeSomeSlack AND FlowWorks (and both SelfTests). Every top-level
// type is INTERNAL so each assembly carries its own copy; never name these types by string (two assemblies, two types).
namespace RimMandrake.Shared.Slack
{
    /// <summary>
    /// Round 6 (owner 2026-10-04, screenshot 20261004214227_1: "firehose is shown as going OVER the hanging power lines
    /// (oops!)"): the ONE place that says what draws over what. Verse-free so the selftest checks the production numbers.
    ///
    /// Two things order a transparent draw in Unity: the material's render queue FIRST, then distance (altitude). The hose
    /// already lay far below the spans in altitude (Conduits vs PawnState+5); the bug was its queue (strand + 3) being above
    /// the span cable's and the pole heads' default Transparent queue (3000), so the hose was painted after them. Overhead
    /// materials (span cable, mast/lamp-mast head overlays) now sit in a queue above every ground-level material of this
    /// mod (cords, hoses, tap clamp), AND above them in altitude.
    ///
    /// Altitude numbers are vanilla's (RimSage, Verse.Altitudes / Verse.AltitudeLayer, decompiled 1.6): layer i is at
    /// i x 0.36585367, an increment is 0.03658537; Conduits = 5, PawnState = 25.
    /// </summary>
    internal static class DrawOrder
    {
        public const double LayerSpacing = 0.36585367, AltInc = 0.03658537;
        public const int LayerConduits = 5, LayerShadows = 13, LayerPawnState = 25;
        /// <summary>The hose's altitude layer. 2026-10-05 (owner screenshot 20261005223734_1, hard rectangles across the hose):
        /// vanilla's sun shadows (Custom/Sun shadow, queue 3170, ZTest LEqual, ZWrite Off) are quads at the Shadows layer drawn
        /// after every 2900-queue thing, so a hose at Conduits wore every wall's shadow as a hard-edged rectangle. The hose now
        /// sits just above the Shadows layer and writes depth (a Cutout pre-pass), so the shadow fails the depth test on it,
        /// as on items and pawns; lighting and fog (higher altitudes) still cover it.</summary>
        public const int LayerHose = LayerShadows;

        /// <summary>Vanilla AltitudeLayer.AltitudeFor(incOffset) for a layer index.</summary>
        public static double Alt(int layer, double inc = 0) => layer * LayerSpacing + inc * AltInc;

        // ---- altitudes (increments on PawnState) used by RM_MapComponent_Aerial
        public const float SpanInc = 5f, TopInc = 4f;
        /// <summary>The hose's base lift above its layer (LayerHose); its crossing bands (HoseMath.CrossLift) and fitting steps
        /// (up to +0.001) sit on top of it.</summary>
        public const float HoseBaseLift = 0.004f, HoseFittingLift = 0.001f;

        /// <summary>The highest altitude any hose piece is drawn at (the top crossing band's fittings).</summary>
        public static double HoseTopAltitude(double crossBand, int crossRanks) =>
            Alt(LayerHose) + HoseBaseLift + crossBand * crossRanks + HoseFittingLift + 0.0005;

        public static double SpanAltitude => Alt(LayerPawnState, SpanInc);
        public static double TopAltitude => Alt(LayerPawnState, TopInc);

        /// <summary>The base strand render queue both mods derive their hose/cord queues from (hose port M6): the queue a
        /// Transparent-shader material resolved to at startup, or 3000 when none could be read (0 or less).</summary>
        public static int BaseStrandQueue(int transparentShaderQueue) => transparentShaderQueue > 0 ? transparentShaderQueue : 3000;

        // ---- render queues, all relative to the cord strand queue (BaseStrandQueue, normally 3000)
        public static int HoseQueue(int strandQueue) => strandQueue + 3;
        public static int TapClampQueue(int strandQueue) => Math.Max(3004, strandQueue + 4);
        /// <summary>Span cable and pole / lamp-mast head overlays: above every ground-level material of this mod.</summary>
        public static int OverheadQueue(int strandQueue) => Math.Max(HoseQueue(strandQueue), TapClampQueue(strandQueue)) + 1;
    }

    /// <summary>CORD_GRAPH_TOPOLOGY_REVISION_1 (the half the 2026-10-09 FOUNDRY note kept): per-frame motion drew one mesh per
    /// material index and rescanned EVERY piece for each index (up to 16 x pieces x 3 passes a frame). Buckets the pieces by
    /// index ONCE per published piece set; each bucket keeps the original order, so iterating bucket v draws exactly the
    /// pieces the filtered full scan drew, in the same order (the motion hashes the probes read are unchanged). An index
    /// outside [0, n) is dropped, as the filtered scan never matched it; n == 1 puts everything in bucket 0 (the scan's
    /// "nv > 1" short-cut).</summary>
    internal static class MaterialBuckets
    {
        public static List<T>[] By<T>(IList<T> items, Func<T, int> indexOf, int n)
        {
            if (n < 1) n = 1;
            var res = new List<T>[n];
            for (int v = 0; v < n; v++) res[v] = new List<T>();
            if (items == null) return res;
            foreach (T it in items)
            {
                int v = n == 1 ? 0 : indexOf(it);
                if (v >= 0 && v < n) res[v].Add(it);
            }
            return res;
        }
    }
}
