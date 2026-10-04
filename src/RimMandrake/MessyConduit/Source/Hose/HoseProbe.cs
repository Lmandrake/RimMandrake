using System;
using System.Globalization;
using System.Linq;
using System.Reflection;
using System.Text;
using RimMandrake.MessyConduit.Core;
using RimWorld;
using Verse;

namespace RimMandrake.MessyConduit.Hose
{
    /// <summary>
    /// validation_hose.py's state-read channel, the same shape as MessyConduitProbe / AerialProbe: the script
    /// writes <see cref="request"/> with jawa/mod_settings_field, RM_MapComponent_Hoses answers on its next frame
    /// (paused or not), the JSON lands in <see cref="result"/> and <see cref="serial"/> is bumped.
    ///
    /// census | lay:rx,rz,x,z | check:rx,rz,x,z | reelin:rx,rz | flow:rx,rz=on|off | end:rx,rz=nozzle|cap |
    /// set:field=value | defaults. (rx,rz) is the reel's cell. flow: drives the DEBUG provider (b).
    /// </summary>
    public static class HoseProbe
    {
        public static string request = "";
        public static string result = "";
        public static int serial;

        public static void Service(Map map, RM_MapComponent_Hoses comp)
        {
            if (string.IsNullOrEmpty(request) || Find.CurrentMap != map) return;
            string cmd = request.Trim();
            request = "";
            string res;
            try { res = Run(map, comp, cmd); }
            catch (Exception ex) { res = "{\"success\":false,\"cmd\":" + S(cmd) + ",\"error\":" + S(ex.ToString()) + "}"; }
            result = res;
            serial++;
        }

        private static int[] Ints(string s) => s.Split(',').Select(x => int.Parse(x.Trim(), CultureInfo.InvariantCulture)).ToArray();

        private static CompHoseReel ReelAt(RM_MapComponent_Hoses comp, int x, int z) =>
            comp.Reels.FirstOrDefault(r => r.parent.OccupiedRect().Contains(new IntVec3(x, 0, z)));   // any cell of the 2x2 reel

        private static string Run(Map map, RM_MapComponent_Hoses comp, string cmd)
        {
            if (cmd == "census") return Census(map, comp);
            if (cmd == "defaults") { HoseSettings.ResetToDefaults(); return "{\"success\":true,\"cmd\":\"defaults\"}"; }
            if (cmd.StartsWith("set:"))
            {
                string[] kv = cmd.Substring(4).Split(new[] { '=' }, 2);
                FieldInfo fi = typeof(HoseSettings).GetField(kv[0], BindingFlags.Public | BindingFlags.Static);
                if (fi == null) return "{\"success\":false,\"error\":\"no settings field " + kv[0] + "\"}";
                object v = fi.FieldType.IsEnum ? Enum.Parse(fi.FieldType, kv[1]) : Convert.ChangeType(kv[1], fi.FieldType, CultureInfo.InvariantCulture);
                fi.SetValue(null, v);
                return "{\"success\":true,\"cmd\":" + S(cmd) + "}";
            }
            int colon = cmd.IndexOf(':');
            if (colon < 0) return "{\"success\":false,\"error\":\"unknown command\",\"cmd\":" + S(cmd) + "}";
            string verb = cmd.Substring(0, colon), arg = cmd.Substring(colon + 1), val = null;
            int eq = arg.IndexOf('=');
            if (eq >= 0) { val = arg.Substring(eq + 1); arg = arg.Substring(0, eq); }
            int[] a = Ints(arg);
            CompHoseReel r = ReelAt(comp, a[0], a[1]);
            if (r == null) return "{\"success\":false,\"cmd\":" + S(cmd) + ",\"error\":\"no hose reel at " + a[0] + "," + a[1] + "\"}";
            switch (verb)
            {
                case "lay":
                {
                    string why = r.TryLay(new IntVec3(a[2], 0, a[3]));
                    if (why == null) comp.EnsureLay(r);
                    return "{\"success\":" + B(why == null) + ",\"cmd\":" + S(cmd) + ",\"reason\":" + S(why) + ",\"layOk\":" + B(r.lay != null) + "}";
                }
                case "check":
                    return "{\"success\":true,\"cmd\":" + S(cmd) + ",\"reason\":" + S(comp.CheckInstall(r, new IntVec3(a[2], 0, a[3]))) + "}";
                case "reelin":
                    r.ReelIn();
                    return "{\"success\":true,\"cmd\":" + S(cmd) + "}";
                case "flow":
                    r.debugFlowing = val == "on" || val == "true" || val == "1";
                    return "{\"success\":true,\"cmd\":" + S(cmd) + ",\"debugFlowing\":" + B(r.debugFlowing) + ",\"tick\":" + Find.TickManager.TicksGame + "}";
                case "end":
                    r.end = val == "cap" ? HoseEnd.EndCap : HoseEnd.Nozzle;
                    return "{\"success\":true,\"cmd\":" + S(cmd) + "}";
                case "clearhist":
                    r.history.Clear();
                    return "{\"success\":true,\"cmd\":" + S(cmd) + "}";
            }
            return "{\"success\":false,\"error\":\"unknown verb\",\"cmd\":" + S(cmd) + "}";
        }

        private static string Census(Map map, RM_MapComponent_Hoses comp)
        {
            var sb = new StringBuilder();
            int now = Find.TickManager.TicksGame;
            sb.Append("{\"success\":true,\"cmd\":\"census\",\"tick\":").Append(now)
              .Append(",\"enabled\":").Append(B(HoseSettings.enabled))
              .Append(",\"texturesInstalled\":").Append(B(HoseMaterials.Installed))
              .Append(",\"wireVisibleWidth\":").Append(D(HoseMath.WireVisibleWidth))
              .Append(",\"minBendSetting\":").Append(D(HoseSettings.minBendRadius))
              .Append(",\"transitionTicks\":").Append(HoseSettings.transitionTicks)
              .Append(",\"releaseTicks\":").Append(HoseSettings.releaseTicks)
              .Append(",\"minPlumpDwell\":").Append(HoseSettings.minPlumpDwell)
              .Append(",\"relays\":").Append(RM_MapComponent_Hoses.Relays)
              .Append(",\"lastLayMs\":").Append(RM_MapComponent_Hoses.LastLayMs)
              .Append(",\"feedDraws\":").Append(comp.lastFeedDraws)
              .Append(",\"retracts\":").Append(RM_MapComponent_Hoses.Retracts)
              .Append(",\"hoses\":[");
            bool first = true;
            foreach (CompHoseReel r in comp.Reels)
            {
                if (!first) sb.Append(',');
                first = false;
                HoseLay lay = comp.EnsureLay(r);
                RM_MapComponent_Hoses.PoseInfo pi = RM_MapComponent_Hoses.Info(r);
                sb.Append("{\"id\":").Append(r.parent.thingIDNumber)
                  .Append(",\"kind\":\"Hose\"")
                  .Append(",\"reel\":[").Append(r.parent.Position.x).Append(',').Append(r.parent.Position.z).Append(']')
                  .Append(",\"far\":[").Append(r.far.x).Append(',').Append(r.far.z).Append(']')
                  .Append(",\"laid\":").Append(B(r.laid))
                  .Append(",\"layOk\":").Append(B(lay != null))
                  .Append(",\"end\":").Append(S(r.end.ToString()))
                  .Append(",\"state\":").Append(S(r.sm.State.ToString()))
                  .Append(",\"stateSince\":").Append(r.sm.Since)
                  .Append(",\"transitions\":").Append(r.sm.Transitions)
                  .Append(",\"blend\":").Append(D(pi.Blend))
                  .Append(",\"eased\":").Append(D(pi.Eased))
                  .Append(",\"wobbling\":").Append(B(pi.Wobbling))
                  .Append(",\"visibleWidth\":").Append(D(pi.Visible))
                  .Append(",\"widthOverWire\":").Append(D(pi.Visible / HoseMath.WireVisibleWidth))
                  .Append(",\"meshWidthFlat\":").Append(D(HoseMath.MeshWidthFlat(pi.Visible)))
                  .Append(",\"meshWidthPlump\":").Append(D(HoseMath.MeshWidthPlump(pi.Visible)))
                  .Append(",\"provider\":").Append(S(r.lastProvider))
                  .Append(",\"signal\":").Append(B(r.lastSignal))
                  .Append(",\"debugFlowing\":").Append(B(r.debugFlowing))
                  .Append(",\"maxLength\":").Append(D(r.MaxLength))
                  .Append(",\"port\":").Append(S(r.Port(true)?.def.defName))
                  .Append(",\"portKind\":").Append(S(r.portKind.ToString()))
                  .Append(",\"portSide\":[").Append(r.portSide.X).Append(',').Append(r.portSide.Z).Append(']')
                  .Append(",\"portContact\":[").Append(r.portContact.X).Append(',').Append(r.portContact.Z).Append(']')
                  .Append(",\"footprint\":[").Append(r.Rect.X0).Append(',').Append(r.Rect.Z0).Append(',').Append(r.Rect.W).Append(',').Append(r.Rect.H).Append(']')
                  .Append(",\"start\":[").Append(D(r.Rect.Mouth.X)).Append(',').Append(D(r.Rect.Mouth.Z)).Append(']')
                  .Append(",\"retractReason\":").Append(S(r.lastRetractReason))
                  .Append(",\"retractTick\":").Append(r.lastRetractTick)
                  .Append(",\"history\":[").Append(string.Join(",", r.history.Select(h => "[" + h.Key + "," + S(h.Value.ToString()) + "]"))).Append(']');
                if (lay != null)
                {
                    var pose = HoseMath.Pose(lay, pi.Eased, int.MaxValue / 2, 30, HoseSettings.plumpAmount);
                    sb.Append(",\"pathLen\":").Append(D(lay.PathLen))
                      .Append(",\"flatLen\":").Append(D(lay.FlatLen))
                      .Append(",\"plumpLen\":").Append(D(lay.PlumpLen))
                      .Append(",\"poseLen\":").Append(D(Geo.Length(pose)))
                      .Append(",\"straight\":").Append(D(V2.Dist(lay.Flat[0], lay.Flat[lay.Flat.Count - 1])))
                      .Append(",\"minBendFlat\":").Append(D(lay.MinBendFlat))
                      .Append(",\"minBendPlump\":").Append(D(lay.MinBendPlump))
                      .Append(",\"minBendPose\":").Append(D(HoseMath.MinBendRadius(pose, HoseMath.EndSkip)))
                      .Append(",\"selfIntersects\":").Append(B(HoseMath.SelfIntersects(lay.Flat)))
                      .Append(",\"couplings\":").Append(lay.Couplings.Count)
                      .Append(",\"reelGraphic\":").Append(S(RM_MapComponent_Hoses.ReelGraphic(r)))
                      .Append(",\"joints\":").Append(lay.Joints.Count)
                      .Append(",\"points\":").Append(lay.Flat.Count)
                      .Append(",\"fellBack\":").Append(B(lay.FellBack))
                      .Append(",\"bbox\":[").Append(D(lay.Flat.Min(q => q.X))).Append(',').Append(D(lay.Flat.Min(q => q.Z))).Append(',')
                      .Append(D(lay.Flat.Max(q => q.X))).Append(',').Append(D(lay.Flat.Max(q => q.Z))).Append(']')
                      .Append(",\"centreCells\":[").Append(string.Join(",", lay.Centre.Select(q => "[" + q.Floor.X + "," + q.Floor.Z + "]").Distinct())).Append(']')
                      .Append(",\"geometryHash\":").Append(S(RM_MapComponent_Hoses.GeometryHash(lay).ToString("x16")))
                      .Append(",\"unwalkablePoints\":").Append(lay.Flat.Count(p => !comp.World().IsWalkable(p.Floor)));
                }
                sb.Append('}');
            }
            sb.Append("]}");
            return sb.ToString();
        }

        private static string S(string s) => s == null ? "null" : "\"" + s.Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\n", "\\n").Replace("\r", "") + "\"";
        private static string B(bool b) => b ? "true" : "false";
        private static string D(double d) => d.ToString("0.####", CultureInfo.InvariantCulture);
    }
}
