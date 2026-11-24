// T_CORD_ENTERS_HOLE_OFFLINE (owner's walk of 0.2.0, 2026-11-24, stations 33 and 12): a cord that comes to a wall plate or a rock hole is DRAWN into the
// black of the hole. Before this, every check read where the strand is LAID (PastFaceDepth, 0.03 under the wall); none read what is drawn over the plate.
// The scenes: every look (Junctions: Industrial, Futuristic, Scrapper; Strips: Modern, whose rock entries are holes and whose wall entries are outlets with
// a seated plug), every face, walls and rock: runs through and ending in a wall (CordEndKindChecks.WallScene), devices across a wall and lamps on its far
// side (dives), one and two cords per run. The looks share the geometry; their pictures' black is read by Pictures().
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.GimmeSomeSlack.Core;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class HoleEntryChecks
    {
        private static readonly Cell[] Dirs = { new Cell(0, 1), new Cell(1, 0), new Cell(0, -1), new Cell(-1, 0) };

        private static HoleEntry.Read Sweep(PileArt pile, int cords, Func<LaidPiece, List<HoleEntry.Lead>> leads)
        {
            var r = new HoleEntry.Read();
            void Run1(CordWorld w, int seed)
            {
                var opt = new BuildOptions { Pile = pile, Seed = (ulong)seed, PlugBoot = CordBuilder.PlugBootU(pile == PileArt.Strips ? "Modern" : "Industrial") };
                if (cords > 0) opt.Lay.CordsMin = opt.Lay.CordsMax = cords;
                foreach (LaidPiece p in new CordBuilder().Build(w, opt, _ => true)) HoleEntry.Audit(r, p, leads(p));
            }
            foreach (int seed in new[] { 71, 72 })
                foreach (Cell d in Dirs)
                {
                    foreach (bool term in new[] { false, true })
                        foreach (bool corner in new[] { false, true })
                            foreach (int lat in new[] { -2, 1 })
                                foreach (BlockKind k in new[] { BlockKind.Wall, BlockKind.Rock }) Run1(CordEndKindChecks.WallScene(d, term, corner, lat, k), seed);
                    for (int dx = -4; dx <= 4; dx++) Run1(StubJoinChecks.FarWallLampScene(dx, d), seed);
                    for (int dx = -5; dx <= 5; dx++) foreach (int dz in new[] { 1, 3 }) Run1(WallPlugChecks.Across(d, dx, dz, 1), seed);
                }
            return r;
        }

        /// <summary>Every look's plate and hole picture: the part read as the hole's black is black along the cord's line (luminance under 40, half a cord's width each side).</summary>
        private static void Pictures()
        {
            string tex = LookIconChecks.TexturesDir();
            string[] files = tex == null ? new string[0] : System.IO.Directory.GetFiles(tex, "Stub*.png", System.IO.SearchOption.AllDirectories);
            int bad = 0;
            foreach (string f in files)
            {
                bool rock = System.IO.Path.GetFileName(f) == "StubRock.png";
                PngAlpha p = PngAlpha.Read(f);
                double u0 = rock ? HoleEntry.RockDark0 : HoleEntry.WallDark0, u1 = rock ? HoleEntry.RockDark1 : HoleEntry.WallDark1;
                int worst = 0, seen = 0;
                for (int x = (int)Math.Ceiling(u0 * p.W); x < (int)Math.Floor(u1 * p.W); x++)
                    for (int y = p.H / 2 - 3; y <= p.H / 2 + 2; y++) { seen++; if (p.A(x, y) < 200) worst = 255; worst = Math.Max(worst, p.Lum(x, y)); }
                if (seen == 0 || worst >= 40) { bad++; Console.WriteLine($"  cord enters hole: {f}: {seen} pixels, brightest {worst} (want under 40)"); }
            }
            Program.Check(files.Length == 16 && bad == 0, $"cord enters hole: the black is black in every look's plate and hole ({bad} of {files.Length} pictures are not; want 16 pictures)");
        }

        public static void Run()
        {
            foreach (PileArt pile in new[] { PileArt.Junctions, PileArt.Strips })
                foreach (int cords in new[] { 0, 2 })
                {
                    HoleEntry.Read r = Sweep(pile, cords, HoleEntry.Leads);
                    string what = $"cord enters hole ({pile}{(cords > 0 ? ", " + cords + " cords per run" : "")})";
                    foreach (var kv in r.By)
                        Console.WriteLine($"  {what}: {kv.Key}: {kv.Value.Count} cords, drawn to {kv.Value.Min(x => x.End):0.000}..{kv.Value.Max(x => x.End):0.000} cell past the face; the black is {kv.Value.Min(x => x.Near):0.000}..{kv.Value.Max(x => x.Far):0.000}");
                    foreach (string b in r.Bad.Take(6)) Console.WriteLine("  " + what + " refused: " + b);
                    Program.Check(r.Ends >= 60, $"{what}: the sweep reads its cords ({r.Ends} cords at {r.Holes} plates and holes)");
                    string[] want = pile == PileArt.Strips ? new[] { "StubRock" } : new[] { "StubWall", "StubRock" };
                    foreach (string k in want)
                        foreach (string f in new[] { "South", "North", "Side" })
                            Program.Check(r.By.ContainsKey(k + " " + f), $"{what}: reads a {k} on a {f} face");
                    Program.Check(r.NotIn == 0, $"{what}: every cord is drawn into the black of its hole ({r.NotIn} of {r.Ends} are not; worst short by {r.WorstShort:0.000} cell)");
                    Program.Check(r.NoBlack == 0, $"{what}: every plate and hole shows its black ({r.NoBlack} of {r.Holes} do not)");
                    Program.Check(r.Bare == 0, $"{what}: no plate or hole without a cord ({r.Bare} of {r.Holes})");
                }
            Pictures();
            HoleEntry.Read old = Sweep(PileArt.Junctions, 0, _ => new List<HoleEntry.Lead>());
            Program.Check(old.Ends > 0 && old.NotIn == old.Ends, $"can fail: with nothing drawn over the plate (the walked build ad72a3cec3) every cord reads short ({old.NotIn} of {old.Ends})");
        }
    }
}
