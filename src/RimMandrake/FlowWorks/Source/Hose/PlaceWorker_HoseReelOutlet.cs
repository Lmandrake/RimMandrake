using System.Collections.Generic;
using RimMandrake.Shared.Slack;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks.Hose
{
    /// <summary>
    /// REEL_OUTLET_DECIDE_ALWAYS_GOES_WEST (owner card 2026-10-22: "the build preview shows which side the hose leaves from"):
    /// while a hose reel is being placed (or its blueprint is selected), the straight lead-out the hose will take out of the
    /// outlet is drawn: an arrow-line from the nozzle and the squares it crosses. Rotate (Q/E) turns it with the reel.
    /// </summary>
    public class PlaceWorker_HoseReelOutlet : PlaceWorker
    {
        public override void DrawGhost(ThingDef def, IntVec3 center, Rot4 rot, Color ghostCol, Thing thing = null)
        {
            CellRect rc = GenAdj.OccupiedRect(center, rot, def.Size);
            var r = new HoseReelRect(rc.minX, rc.minZ, rc.Width, rc.Height) { Rot = rot.AsInt };
            if (thing != null) r.Look = HoseLook.LookOfThing(thing);
            if (!r.Outward.HasValue) return;
            LeadOut(r, out V2 a, out V2 b, out List<IntVec3> cells);
            float y = AltitudeLayer.MetaOverlays.AltitudeFor();
            GenDraw.DrawFieldEdges(cells, Color.cyan);
            GenDraw.DrawLineBetween(new Vector3((float)a.X, y, (float)a.Z), new Vector3((float)b.X, y, (float)b.Z), SimpleColor.Cyan, 0.2f);
            // arrow head: two short strokes back from the end
            V2 u = r.Outward.Value, n = u.Perp;
            foreach (int s in new[] { 1, -1 })
            {
                V2 h = b - u * 0.35 + n * (0.25 * s);
                GenDraw.DrawLineBetween(new Vector3((float)h.X, y, (float)h.Z), new Vector3((float)b.X, y, (float)b.Z), SimpleColor.Cyan, 0.2f);
            }
        }

        /// <summary>The preview's line (nozzle tip to the end of the straight lead-out) and the squares outside the reel it
        /// crosses. Pure but for IntVec3, so the offline check reads the same answer.</summary>
        internal static void LeadOut(HoseReelRect r, out V2 a, out V2 b, out List<IntVec3> cells)
        {
            V2 u = r.Outward ?? new V2(-1, 0);
            a = r.NozzleTip;
            b = r.Mouth + u * HoseReelRect.OutletStraight;
            cells = new List<IntVec3>();
            for (double t = 0; t <= HoseReelRect.OutletStraight + 1e-9; t += 0.25)
            {
                Cell c = (r.Mouth + u * t).Floor;
                var iv = new IntVec3(c.X, 0, c.Z);
                if (!r.Contains(c) && !cells.Contains(iv)) cells.Add(iv);
            }
        }
    }
}
