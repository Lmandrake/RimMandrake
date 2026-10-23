using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text;
using Verse;
using RimMandrake.Shared.Slack;

namespace RimMandrake.FlowWorks.Hose
{
    /// <summary>
    /// HOSE_JOINTS_REPAIR_ENDS_MISS_THE_NOZZLES: the JOINT CHECK's live half (HoseProbe verb "joints", read by
    /// northstar/joint_check.py). Walks every reel on the map and measures, on the pose the hose is DRAWN with (the draw cache,
    /// RM_MapComponent_Hoses.DrawnPose), how far each drawn end or fitting face sits from the point it must meet:
    ///   reel   the laid hose's reel-end coupling face vs the measured nozzle tip, and the drawn strand's start (after the outlet
    ///          trim) against the coupling + wrap it must run under (off the nozzle axis = a gap beside the coupling);
    ///   free   a free end coupled to a port: the drawn coupling's face vs the port (a 2x2 tank's measured flange, else the
    ///          shared edge's midpoint where the pipe's flange is drawn), and a Port end whose port is gone = an end at no port;
    ///   relay  a hose feeding a relay reel: its drawn end vs the relay's drawn inlet (HoseRelay.DrawnEnd);
    ///   feed   a link from a pipe/tank/pump beside a reel: the port really occupies the cell the link starts in; a nozzle link
    ///          meets the STORED art's nozzle and the reel really prints the stored art; a laid reel whose port stands in front
    ///          of its nozzle is reported (two hoses from one nozzle, audit D3).
    /// A joint passes when its gap is within HoseJoints.Tolerance (the reel-end strand: within the coupling + wrap span).
    /// Read-only: nothing on the map changes.
    /// </summary>
    public static class HoseJointProbe
    {
        private static string F(double v) => v.ToString("0.000", CultureInfo.InvariantCulture);
        private static string P(V2 p) => "[" + F(p.X) + "," + F(p.Z) + "]";
        private static string S(string s) => "\"" + (s ?? "").Replace("\\", "\\\\").Replace("\"", "\\\"") + "\"";

        public static string TryRun(Map map, string cmd)
        {
            if (cmd != "joints") return null;
            RM_MapComponent_Hoses comp = map?.GetComponent<RM_MapComponent_Hoses>();
            if (comp == null) return "{\"success\":false,\"cmd\":\"joints\",\"error\":\"no hose component on this map\"}";
            var rows = new List<string>();
            int bad = 0, total = 0, unmeasured = 0;
            void Row(CompHoseReel r, string kind, bool ok, double gap, string where, string note, bool measured = true)
            {
                total++;
                if (!measured) unmeasured++;
                else if (!ok) bad++;
                rows.Add("{\"reel\":" + r.parent.thingIDNumber + ",\"at\":[" + r.parent.Position.x + "," + r.parent.Position.z + "],\"rot\":" + r.parent.Rotation.AsInt
                         + ",\"look\":" + S(r.Rect.Look) + ",\"kind\":" + S(kind) + ",\"ok\":" + (measured ? (ok ? "true" : "false") : "null")
                         + ",\"gap\":" + F(gap) + ",\"where\":" + where + ",\"note\":" + S(note) + "}");
            }
            float vis = (float)HoseMath.VisibleWidth(0, RM_HoseSettings.plumpAmount);
            foreach (CompHoseReel r in comp.Reels)
            {
                if (r?.parent == null || !r.parent.Spawned) continue;
                HoseReelRect rect = r.Rect;
                // ---- feed: a link from a port beside the reel's body
                Thing port = r.Port(true);
                if (port != null)
                {
                    bool deployedArt = !(r.carry == HoseCarryState.Stored && !r.laid);
                    List<V2> path = HoseJoints.ReelFeed(rect, r.portSide, r.portContact, deployedArt, out bool onNozzle, out V2 face, out _);
                    CellRect pr = port.OccupiedRect();
                    bool portThere = pr.Contains(new IntVec3(r.portContact.X, 0, r.portContact.Z));
                    HoseJoints.Meets(path[0], r.portContact.Centre, out double g0);
                    Row(r, "feed_port_end", portThere && g0 <= HoseJoints.Tolerance, g0, P(path[0]),
                        portThere ? port.def.defName : "the link starts in a cell " + port.def.defName + " does not occupy (end at no port)");
                    if (onNozzle)
                    {
                        HoseJoints.Meets(face, HoseJoints.StoredNozzleTip(rect), out double gf);
                        string art = RM_MapComponent_Hoses.ReelGraphic(r);
                        bool stored = art == "stored";
                        Row(r, "feed_nozzle", stored && gf <= HoseReelRect.NozzleSeat + HoseJoints.Tolerance, Math.Max(0, gf - HoseReelRect.NozzleSeat), P(face),
                            stored ? "link couples to the stored nozzle" : "link couples to the stored nozzle but the reel prints " + art);
                    }
                    else
                    {
                        V2 o = rect.Outward ?? new V2(0, 0);
                        bool front = rect.HasNozzle && Math.Abs(o.X - r.portSide.X) < 1e-9 && Math.Abs(o.Z - r.portSide.Z) < 1e-9;
                        Row(r, front ? "feed_nozzle_shared" : "feed_under_reel", !front, 0, P(path[path.Count - 1]),
                            front ? "laid reel with its port in front of the nozzle: the link and the laid hose share one nozzle (turn the reel)"
                                  : "link runs in under the reel to its centre");
                    }
                }
                if (!r.laid || r.lay == null) continue;
                List<V2> pts = comp.DrawnPose(r);
                if (pts == null || pts.Count < 2)
                {
                    Row(r, "pose", false, 0, "null", "laid but no drawn pose cached (off screen or never drawn): pan the camera over it", false);
                    continue;
                }
                int n = pts.Count;
                // ---- reel end
                if (rect.HasNozzle && r.lay.Outlet)
                {
                    V2 seat = HoseJoints.NozzleCoupling(rect, out V2 inw);
                    HoseJoints.Meets(seat, rect.NozzleTip, out double gs);
                    double size = HoseMath.FittingSize(vis, RM_MapComponent_Hoses.PieceBand, RM_MapComponent_Hoses.CouplingMax);
                    List<V2> strand = HoseMath.TrimStart(pts, RM_MapComponent_Hoses.OutletTrim(r, vis));
                    V2 s0 = strand.Count > 0 ? strand[0] : pts[0];
                    V2 back = -inw;                                    // out of the nozzle, along the coupling and its wrap
                    V2 rel = s0 - seat;
                    double along = rel.X * back.X + rel.Z * back.Z, perp = Math.Abs(rel.X * back.Z - rel.Z * back.X);
                    double cover = (HoseMath.JoinerFace + 0.03) * size + HoseMath.WrapLength - 0.05;   // the coupling's brass + its wrap
                    double gap = Math.Max(0, Math.Max(perp - 0.5 * vis, Math.Max(-along, along - cover)));
                    Row(r, "reel_end", gs <= HoseReelRect.NozzleSeat + HoseJoints.Tolerance && gap <= HoseJoints.Tolerance, Math.Max(gap, gs - HoseReelRect.NozzleSeat), P(s0),
                        "coupling face " + F(gs) + " from the tip (seat " + HoseReelRect.NozzleSeat + "); strand starts " + F(along) + " back, " + F(perp) + " off the axis");
                }
                // ---- far end
                if (r.carry == HoseCarryState.Retracting) continue;
                CompHoseReel relay = comp.RelayOf(r);
                if (relay != null)
                {
                    V2 want = comp.EndPoint(r, out _, out _);
                    HoseJoints.Meets(pts[n - 1], want, out double gr);
                    Row(r, "relay_end", gr <= HoseJoints.Tolerance, gr, P(pts[n - 1]), "relay " + relay.parent.thingIDNumber);
                    continue;
                }
                HoseFreeEnd fe = comp.FreeEndOf(r);
                if (fe.Kind != HoseEndKind.Port) continue;
                if (fe.Port == null || !fe.Port.Spawned)
                {
                    Row(r, "free_port_end", false, 0, P(pts[n - 1]), "end couples to a port that is not there (end at no port)");
                    continue;
                }
                V2 dp = new V2(fe.PortSide.X, fe.PortSide.Z);
                if (fe.PortSide.X == 0 && fe.PortSide.Z == 0)
                {
                    CellRect rc = fe.Port.OccupiedRect();
                    var centre = new V2(rc.minX + rc.Width / 2.0, rc.minZ + rc.Height / 2.0);
                    HoseJoints.Meets(pts[n - 1], centre, out double gc);
                    Row(r, "free_on_port", gc <= 0.5 + HoseJoints.Tolerance, Math.Max(0, gc - 0.5), P(pts[n - 1]), fe.Port.def.defName + " (end lies on it)");
                    continue;
                }
                V2 faceAt = pts[n - 1] + dp * 0.5;             // DrawEnds: the coupling's face (Fitting end) on a port
                V2 portAt = comp.PortEnd(r, out V2 pa, out _) ? pa : new V2(fe.Cell.x + 0.5, fe.Cell.z + 0.5) + dp * 0.5;
                HoseJoints.Meets(faceAt, portAt, out double gp);
                Row(r, "free_port_end", gp <= HoseJoints.Tolerance, gp, P(faceAt), fe.Port.def.defName + " port at " + P(portAt));
            }
            var sb = new StringBuilder();
            sb.Append("{\"success\":true,\"cmd\":\"joints\",\"tolerance\":").Append(F(HoseJoints.Tolerance))
              .Append(",\"total\":").Append(total).Append(",\"bad\":").Append(bad).Append(",\"unmeasured\":").Append(unmeasured)
              .Append(",\"reels\":").Append(comp.Reels.Count).Append(",\"joints\":[").Append(string.Join(",", rows)).Append("]}");
            return sb.ToString();
        }
    }
}
