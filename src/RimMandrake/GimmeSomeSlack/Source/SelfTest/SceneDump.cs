// A whole built scene as JSON for a picture (src/RimMandrake/Utils/mockups/messy_conduit/scene_picture.py): the ground, the conduit, the machines,
// every strand, decal and node, and what the end and slope audits refuse in it. `--scene-dump OUT.json fuzz:SEED[:STEP]` writes one random world;
// checks call Write on a world they refuse. A cord that passes its bars and looks wrong is a finding: this is how one is looked at.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.Json;
using RimMandrake.GimmeSomeSlack.Core;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class SceneDump
    {
        private static string F(double d) => d.ToString("0.###", CultureInfo.InvariantCulture);

        internal static void Write(string path, string name, CordWorld w, CordGraph g, List<LaidPiece> ps, BuildOptions opt, Func<Cell, bool> live)
        {
            var sb = new StringBuilder();
            sb.Append("{\"name\":").Append(JsonSerializer.Serialize(name)).Append(",\"w\":").Append(w.Width).Append(",\"h\":").Append(w.Height);
            var blocked = new List<string>();
            var conduit = new List<string>();
            var doors = new List<string>();
            for (int x = 0; x < w.Width; x++)
                for (int z = 0; z < w.Height; z++)
                {
                    var c = new Cell(x, z);
                    if (!w.IsWalkable(c)) blocked.Add($"[{x},{z},\"{w.BuriedKind(c)}\"]");
                    if (w.IsConduit(c)) conduit.Add($"[{x},{z},{(live(c) ? 1 : 0)}]");
                    if (w.IsDoor(c)) doors.Add($"[{x},{z}]");
                }
            sb.Append(",\"blocked\":[").Append(string.Join(",", blocked)).Append("],\"conduit\":[").Append(string.Join(",", conduit)).Append("],\"doors\":[").Append(string.Join(",", doors)).Append(']');
            sb.Append(",\"machines\":[").Append(string.Join(",", w.Machines.Select(m => $"{{\"id\":{JsonSerializer.Serialize(m.Id ?? "")},\"kind\":\"{m.Kind}\",\"x\":{m.X0},\"z\":{m.Z0},\"w\":{m.W},\"h\":{m.H},\"side\":{(m.SidePorts ? "true" : "false")},\"hooks\":[{string.Join(",", m.Hookups.Select(h => $"[{h.X},{h.Z}]"))}]}}"))).Append(']');
            sb.Append(",\"nodes\":[").Append(string.Join(",", g.Nodes.Values.Select(n => $"{{\"type\":\"{n.Type}\",\"x\":{F(n.Pos.X)},\"z\":{F(n.Pos.Z)},\"cell\":[{n.Cell.X},{n.Cell.Z}],\"blob\":{(n.IsBlob ? "true" : "false")}}}"))).Append(']');
            sb.Append(",\"pieces\":[").Append(string.Join(",", ps.Select(p =>
                "{\"a\":" + JsonSerializer.Serialize(p.EndA ?? "") + ",\"b\":" + JsonSerializer.Serialize(p.EndB ?? "") + ",\"key\":" + JsonSerializer.Serialize(p.Key ?? "") +
                ",\"strands\":[" + string.Join(",", p.Strands.Where(s => s.Pts != null).Select(s => "{\"lay\":" + JsonSerializer.Serialize(s.Lay ?? "") + ",\"whipA\":" + s.WhipA + ",\"whipB\":" + s.WhipB +
                    ",\"over\":" + (s.OverFace ? "true" : "false") + ",\"ties\":" + (s.Ties == null ? 0 : s.Ties.Count) + ",\"pts\":[" + string.Join(",", s.Pts.Select(q => "[" + F(q.X) + "," + F(q.Z) + "]")) + "]}")) + "]" +
                ",\"decals\":[" + string.Join(",", p.Decals.Select(d => $"{{\"kind\":\"{d.Kind}\",\"x\":{F(d.Pos.X)},\"z\":{F(d.Pos.Z)},\"a\":{F(d.Angle)},\"s\":{F(d.Scale)},\"ports\":{d.Ports}}}")) + "]" +
                ",\"ends\":[" + string.Join(",", p.Ends.Select(e => $"[{e.NetCell.X},{e.NetCell.Z}]")) + "]}"))).Append(']');
            var bad = new List<string>();
            CordEndAudit.EndRead er = CordEndAudit.Ends(g, ps, name);
            bad.AddRange(er.Bad);
            CordEndAudit.SlopeRead sl = CordEndAudit.Slopes(w, g, ps, name);
            bad.AddRange(sl.Bad);
            StubJoins.JoinRead jr = StubJoins.Joins(w, ps, opt, name);
            bad.AddRange(jr.Bad);
            sb.Append(",\"bad\":[").Append(string.Join(",", bad.Distinct().Select(x => JsonSerializer.Serialize(x)))).Append("]}");
            File.WriteAllText(path, sb.ToString());
        }

        /// <summary>--scene-dump OUT.json fuzz:SEED[:STEP] | placed:INDEX | family:INDEX</summary>
        public static int Run(string outPath, string what)
        {
            string[] t = what.Split(':');
            (string name, CordWorld w, BuildOptions opt, Func<Cell, bool> live) x;
            if (t[0] == "fuzz")
            {
                long seed = long.Parse(t[1]);
                int step = t.Length > 2 ? int.Parse(t[2]) : -1;
                var all = GssFuzz.CordWorlds((int)seed).Where(q => q.seed == seed).ToList();
                var q0 = step < 0 ? all[all.Count - 1] : all.First(q => q.step == step);
                x = ($"fuzz seed {q0.seed} step {q0.step}", q0.w, q0.opt, q0.live);
            }
            else if (t[0] == "placed") x = LiveEndCensus.Placements(false).Skip(int.Parse(t[1])).First();
            else x = LiveEndCensus.Family(1).Skip(int.Parse(t[1])).First();
            var b = new CordBuilder();
            List<LaidPiece> ps = b.Build(x.w, x.opt, c => x.live(c));
            Write(outPath, x.name, x.w, b.Graph, ps, x.opt, x.live);
            Console.WriteLine($"scene dump: {x.name} -> {outPath}");
            return 0;
        }
    }
}
