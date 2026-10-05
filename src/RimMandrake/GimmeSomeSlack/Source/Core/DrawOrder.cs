using System;

namespace RimMandrake.GimmeSomeSlack.Core
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
    public static class DrawOrder
    {
        public const double LayerSpacing = 0.36585367, AltInc = 0.03658537;
        public const int LayerConduits = 5, LayerPawnState = 25;

        /// <summary>Vanilla AltitudeLayer.AltitudeFor(incOffset) for a layer index.</summary>
        public static double Alt(int layer, double inc = 0) => layer * LayerSpacing + inc * AltInc;

        // ---- altitudes (increments on PawnState) used by RM_MapComponent_Aerial
        public const float SpanInc = 5f, TopInc = 4f;
        /// <summary>The hose's base lift above the Conduits layer; its crossing bands (HoseMath.CrossLift) and fitting steps
        /// (up to +0.001) sit on top of it.</summary>
        public const float HoseBaseLift = 0.004f, HoseFittingLift = 0.001f;

        /// <summary>The highest altitude any hose piece is drawn at (the top crossing band's fittings).</summary>
        public static double HoseTopAltitude(double crossBand, int crossRanks) =>
            Alt(LayerConduits) + HoseBaseLift + crossBand * crossRanks + HoseFittingLift + 0.0005;

        public static double SpanAltitude => Alt(LayerPawnState, SpanInc);
        public static double TopAltitude => Alt(LayerPawnState, TopInc);

        // ---- render queues, all relative to the cord strand queue (CordMaterials.StrandQueue, normally 3000)
        public static int HoseQueue(int strandQueue) => strandQueue + 3;
        public static int TapClampQueue(int strandQueue) => Math.Max(3004, strandQueue + 4);
        /// <summary>Span cable and pole / lamp-mast head overlays: above every ground-level material of this mod.</summary>
        public static int OverheadQueue(int strandQueue) => Math.Max(HoseQueue(strandQueue), TapClampQueue(strandQueue)) + 1;
    }
}
