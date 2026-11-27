// JawaBenchDrawOrderCore.cs - the pure half of the draw-order readings: jawa/cell_draw_census's sort reading of a section
// sub-mesh (its vertex heights against a probe height) and jawa/pawn_render_nodes' draw path of a pawn this frame.
// RIMMANDRAKE_DRAW_SCRAPPER_JETTIES_HEAVY_BRIDGE_IN_HIS_PICKED_MANNER: a section layer puts every print of one material into one
// sub-mesh (MapDrawLayer.GetSubMesh), and the renderer orders a draw by its mesh as a whole, so a height change of one print
// inside a sub-mesh can change nothing on screen. These rules read where a sub-mesh's heights lie against a pawn's; the verdict
// stays with the caller. No UnityEngine, no RimWorld: tested offline by DrawOrderSelfTest (selftest_draw_order.py).

using System.Collections.Generic;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchDrawOrderCore
    {
        /// <summary>Two heights closer than this are level. Below one pawn render-node layer (PawnRenderUtility.AltitudeForLayer:
        /// 0.0003658537 per layer), so the nodes of one pawn stay apart.</summary>
        internal const float Eps = 0.0001f;

        /// <summary>The heights (world y) of a set of vertices. Empty = no vertex was read: a reading that could not look, never a
        /// span at 0.</summary>
        internal struct YSpan
        {
            public int n;
            public float min, max;
            public bool Empty => n == 0;
            /// <summary>The middle of the two ends, as a mesh's bounds centre is (not the mean of the vertices).</summary>
            public float Centre => (min + max) * 0.5f;
        }

        internal static YSpan Span(IEnumerable<float> ys)
        {
            var s = new YSpan();
            if (ys == null) return s;
            foreach (float y in ys)
            {
                if (s.n == 0) { s.min = y; s.max = y; }
                if (y < s.min) s.min = y;
                if (y > s.max) s.max = y;
                s.n++;
            }
            return s;
        }

        /// <summary>Where a height lies against y. The map camera looks down -y, so "above" is nearer the camera.</summary>
        internal static string Relation(float centre, float y, float eps)
        {
            if (centre > y + eps) return "above";
            if (centre < y - eps) return "below";
            return "level";
        }

        /// <summary>True when the span holds vertices on both sides of y: one draw, part of it on each side.</summary>
        internal static bool Straddles(YSpan s, float y, float eps)
        {
            return !s.Empty && s.min < y - eps && s.max > y + eps;
        }

        /// <summary>jawa/material_queue: -2 reads only, -1 gives a material back its shader's own queue, 0..MaxQueue sets one.</summary>
        internal const int ReadOnly = -2, ShaderQueue = -1, MaxQueue = 5000;

        internal static string QueueRefusal(int setQueue)
        {
            if (setQueue == ReadOnly || setQueue == ShaderQueue) return null;
            if (setQueue >= 0 && setQueue <= MaxQueue) return null;
            return "setQueue must be -2 (read only), -1 (the shader's own queue) or 0.." + MaxQueue + "; got " + setQueue;
        }

        /// <summary>Whether a material is the one asked for: by instance id when one is given (the name is then ignored), else
        /// by a case-blind part of its name. Neither given picks nothing (never every material).</summary>
        internal static bool Picks(int id, string name, int wantId, string wantName)
        {
            if (wantId != 0) return id == wantId;
            if (string.IsNullOrEmpty(wantName)) return false;
            return name != null && name.IndexOf(wantName, System.StringComparison.OrdinalIgnoreCase) >= 0;
        }

        /// <summary>How a pawn is drawn this frame, from PawnRenderer's pre-render results: notPreRendered (no results yet),
        /// hidden, cachedAtlas (one quad of the pawn's whole cached frame: the render nodes are not drawn) or nodes (one draw
        /// per render node).</summary>
        internal static string DrawPath(bool valid, bool draw, bool useCached)
        {
            if (!valid) return "notPreRendered";
            if (!draw) return "hidden";
            return useCached ? "cachedAtlas" : "nodes";
        }
    }
}
