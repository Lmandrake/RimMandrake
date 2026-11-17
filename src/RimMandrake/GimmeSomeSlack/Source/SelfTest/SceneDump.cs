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

        /// <summary>--scene-dump OUT.json fuzz:SEED[:STEP] | placed:INDEX | family:INDEX | live:0 (the slice checks' live scene)</summary>
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
            else if (t[0] == "world")
            {
                // a world the live probe dumped ("worlddump:NAME"), kept beside the oracle scenes: world:owner_look_20261116
                using JsonDocument doc = JsonDocument.Parse(File.ReadAllText(Path.Combine(AppContext.BaseDirectory, t[1] + ".json")));
                CordWorld lw = LabWorld.Read(doc.RootElement, out BuildOptions lo, out HashSet<Cell> ll);
                x = (t[1], lw, lo, c => ll.Contains(c));
            }
            else if (t[0] == "live") x = ("the live scene", RebuildPerDigChecks.LiveScene(), new BuildOptions(), c => false);
            else if (t[0] == "placedname") x = LiveEndCensus.Placements(false).First(q => q.name.Contains(Environment.GetEnvironmentVariable("GSS_SCENE_NAME")));   // the first placement whose name holds the text
            else if (t[0] == "placed") x = LiveEndCensus.Placements(false).Skip(int.Parse(t[1])).First();
            else if (t[0] == "familyname")      // a family scene by its name (GSS_SCENE_NAME: names hold spaces and commas), second draws included
                x = LiveEndCensus.Family(2).First(q => q.name == Environment.GetEnvironmentVariable("GSS_SCENE_NAME"));
            else x = LiveEndCensus.Family(1).Skip(int.Parse(t[1])).First();
            CordBuilder.FitTrace = true;
            string tr = Environment.GetEnvironmentVariable("GSS_TRACE_NEAR");   // "x,z,endsubstring": which lay stage first brings a strand within 0.15 of the point
            if (!string.IsNullOrEmpty(tr))
            {
                string[] tp = tr.Split(',');
                var at = new V2(double.Parse(tp[0], System.Globalization.CultureInfo.InvariantCulture), double.Parse(tp[1], System.Globalization.CultureInfo.InvariantCulture));
                CordBuilder.StepTrace = (stage, a, b2, pts) =>
                {
                    if (pts == null || !((a ?? "") + "|" + (b2 ?? "")).Contains(tp[2])) return;
                    Console.WriteLine($"trace {stage} {a}|{b2} {pts.Count} pts, {Geo.Length(pts):0.00} long, nearest {pts.Min(q => V2.Dist(q, at)):0.00}");
                };
            }
            var b = new CordBuilder();
            List<LaidPiece> ps = b.Build(x.w, x.opt, c => x.live(c));
            Write(outPath, x.name, x.w, b.Graph, ps, x.opt, x.live);
            Console.WriteLine($"scene dump: {x.name} -> {outPath}");
            return 0;
        }
        /// <summary>--slope-census OUT.txt [N]: every slope and stub-join refusal on every step of the first N random worlds (default 120), one
        /// line each as "seed step | refusal", so a regime is read off the whole population and not off the first refusal of each world.</summary>
        public static int Census(string outPath, int n)
        {
            var lines = new List<string>();
            int worlds = 0, red = 0;
            foreach (var q in GssFuzz.CordWorlds(n))
            {
                var b = new CordBuilder();
                List<LaidPiece> ps = b.Build(q.w, q.opt, c => q.live(c));
                worlds++;
                var bad = new List<string>();
                foreach (string x in CordEndAudit.Slopes(q.w, b.Graph, ps, "S").Bad) bad.Add("slope " + x);
                foreach (string x in StubJoins.Joins(q.w, ps, q.opt, "J").Bad) bad.Add("join " + x);
                if (bad.Count > 0) red++;
                foreach (string x in bad) lines.Add($"{q.seed} {q.step} | {x}");
            }
            File.WriteAllLines(outPath, lines);
            Console.WriteLine($"slope census: {worlds} worlds, {red} with a refusal, {lines.Count} refusals -> {outPath}");
            return 0;
        }
    }
}
