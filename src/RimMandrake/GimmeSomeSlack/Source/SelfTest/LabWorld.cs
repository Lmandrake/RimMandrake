// The shape lab: a CordWorld written by the live probe ("worlddump") or by hand, laid here with the production builder, every strand and decal written out. A cord's shape can
// then be worked on with no game, on a real colony's own conduit, walls and machines. ralph/live/lab_render.py draws the result.
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
    internal static class LabWorld
    {
        private static Cell C(JsonElement a) => new Cell(a[0].GetInt32(), a[1].GetInt32());

        internal static CordWorld Read(JsonElement r, out BuildOptions opt, out HashSet<Cell> live)
        {
            var w = new CordWorld(r.GetProperty("w").GetInt32(), r.GetProperty("h").GetInt32());
            foreach (JsonElement a in r.GetProperty("conduit").EnumerateArray()) w.SetConduit(C(a));
            foreach (JsonElement a in r.GetProperty("blocked").EnumerateArray()) w.SetBlocked(new Cell(a[0].GetInt32(), a[1].GetInt32()), (BlockKind)a[2].GetInt32());
            foreach (JsonElement a in r.GetProperty("doors").EnumerateArray()) w.SetDoor(C(a));
            foreach (JsonElement a in r.GetProperty("buried").EnumerateArray()) w.SetForcedBuried(C(a));
            foreach (JsonElement a in r.GetProperty("busy").EnumerateArray()) w.SetBusy(C(a));
            foreach (JsonElement m in r.GetProperty("machines").EnumerateArray())
            {
                var i = new MachineInfo { Id = m.GetProperty("id").GetString(), Kind = (MachineKind)m.GetProperty("kind").GetInt32(), X0 = m.GetProperty("x").GetInt32(), Z0 = m.GetProperty("z").GetInt32(), W = m.GetProperty("w").GetInt32(), H = m.GetProperty("h").GetInt32() };
                foreach (JsonElement h in m.GetProperty("hookups").EnumerateArray()) i.Hookups.Add(C(h));
                foreach (JsonElement l in m.GetProperty("links").EnumerateArray()) i.MachineLinks.Add(l.GetString());
                i.InsetS = m.GetProperty("insets")[0].GetDouble(); i.InsetN = m.GetProperty("insets")[1].GetDouble(); i.InsetE = m.GetProperty("insets")[2].GetDouble(); i.InsetW = m.GetProperty("insets")[3].GetDouble();
                if (m.TryGetProperty("home", out JsonElement home)) { i.HasHome = true; i.HomeX = home[0].GetInt32(); i.HomeZ = home[1].GetInt32(); }
                w.Machines.Add(i);
            }
            live = new HashSet<Cell>();
            foreach (JsonElement a in r.GetProperty("live").EnumerateArray()) live.Add(C(a));
            var strips = new HashSet<Cell>();
            var boxes = new HashSet<Cell>();
            foreach (JsonElement a in r.GetProperty("strips").EnumerateArray()) strips.Add(C(a));
            foreach (JsonElement a in r.GetProperty("boxes").EnumerateArray()) boxes.Add(C(a));
            JsonElement o = r.GetProperty("opt");
            opt = new BuildOptions
            {
                Tangles = o.GetProperty("tangles").GetBoolean(), NeedlessLoops = o.GetProperty("needless").GetBoolean(), TangleMin = o.GetProperty("tangleMin").GetInt32(),
                Pile = o.GetProperty("strips").GetBoolean() ? PileArt.Strips : PileArt.Junctions, DiveThrough = o.GetProperty("dive").GetBoolean(), SlideUnder = o.GetProperty("slide").GetBoolean(),
                Seed = o.TryGetProperty("seed", out JsonElement sd) ? sd.GetUInt64() : 1
            };
            opt.Lay.SlackScale = o.GetProperty("slack").GetDouble();
            opt.Lay.MaxExtra = o.GetProperty("maxExtra").GetDouble();
            opt.Lay.MinExtra = Math.Min(opt.Lay.MinExtra, opt.Lay.MaxExtra);
            opt.Lay.CordsMax = o.GetProperty("cordsMax").GetInt32();
            foreach (JsonElement t in o.GetProperty("straight").EnumerateArray()) opt.StraightPlugIds.Add(t.GetString());
            opt.PileAt = c => strips.Contains(c) ? PileArt.Strips : boxes.Contains(c) ? PileArt.Junctions : (PileArt?)null;
            return w;
        }

        private static string F(double d) => d.ToString("0.###", CultureInfo.InvariantCulture);

        internal static int Run(string inPath, string outPath)
        {
            using JsonDocument doc = JsonDocument.Parse(File.ReadAllText(inPath));
            CordWorld w = Read(doc.RootElement, out BuildOptions opt, out HashSet<Cell> live);
            var b = new CordBuilder();
            List<LaidPiece> ps = b.Build(w, opt, c => live.Contains(c));
            var sb = new StringBuilder("{\"pieces\":[");
            bool first = true;
            int strands = 0;
            CordShapeAudit.Tally tally = new CordShapeAudit.Tally();
            foreach (LaidPiece p in ps)
            {
                if (!first) sb.Append(',');
                first = false;
                sb.Append("{\"a\":\"").Append(p.EndA ?? p.Key).Append("\",\"b\":\"").Append(p.EndB ?? "").Append("\",\"len\":").Append(F(p.PathLen)).Append(",\"strands\":[");
                for (int i = 0; i < p.Strands.Count; i++)
                {
                    List<V2> pts = p.Strands[i].Pts;
                    strands++;
                    tally.Add(p, p.Strands[i]);
                    if (i > 0) sb.Append(',');
                    sb.Append('[').Append(string.Join(",", pts.Select(q => "[" + F(q.X) + "," + F(q.Z) + "]"))).Append(']');
                }
                sb.Append("],\"decals\":[");
                sb.Append(string.Join(",", p.Decals.Select(d => "[\"" + d.Kind + "\"," + F(d.Pos.X) + "," + F(d.Pos.Z) + "," + F(d.Angle) + "," + F(d.Scale) + "]")));
                sb.Append("],\"ends\":[").Append(string.Join(",", p.Ends.Select(e => "[" + F(e.Tip.X) + "," + F(e.Tip.Z) + "]"))).Append("]}");
            }
            sb.Append("],\"audit\":").Append(tally.Json()).Append('}');
            File.WriteAllText(outPath, sb.ToString());
            Console.WriteLine($"lab: {ps.Count} pieces, {strands} strands -> {outPath}");
            Console.WriteLine("audit " + tally.Json());
            return 0;
        }
    }
}
