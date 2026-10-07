// A7 census (owner, 2026-10-06): find every cord the planner reports Unroutable, and say what stands between its two ends.
// Owner's model: "If it's a wall, then some conduit must go through the wall, and thus there would be a place to dive into the
// wall and out again. Water likewise could be dived down into and back up out of." The census walks every world the cords
// fuzz builds plus constructed vanilla-legal scenes, and classifies each unroutable leg by the cells its straight line crosses:
//   a  = the barrier is a wall/rock that has conduit through it,
//   b  = the barrier is water,
//   c* = anything else (c-wall: a wall/rock with NO conduit in it; c-building: another building's footprint;
//        c-enclosed: the straight line crosses nothing, an end is boxed in).
// `--unroutable-census <out.json>` writes every case (grid + the drawn strands) for render_unroutable_examples.py; the normal
// selftest run calls Checks(), which pins the constructed scenes' classes.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using RimMandrake.GimmeSomeSlack.Core;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class UnroutableCensus
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "a7: " + msg);

        internal sealed class Case
        {
            public string Source, Class, Detail, EndA, EndB;
            public CordWorld W;
            public V2 P0, P1;
            public List<List<V2>> Strands = new List<List<V2>>();
            public List<Cell> Crossed = new List<Cell>();
        }

        /// <summary>Every unroutable leg of one world, classified. Also returns the builder's own Unroutable count.</summary>
        internal static List<Case> Scan(string source, CordWorld w, BuildOptions opt, Func<Cell, bool> live, out int builderUnroutable)
        {
            var b = new CordBuilder();
            List<LaidPiece> ps = b.Build(w, opt, live);
            builderUnroutable = ps.Count(p => p.Unroutable);
            var outp = new List<Case>();
            CordGraph g = b.Graph;
            foreach (CordEdge e in g.CordEdges())
            {
                var stops = new List<V2> { e.PA };
                stops.AddRange(e.Knots);
                stops.Add(e.PB);
                for (int i = 0; i + 1 < stops.Count; i++)
                {
                    V2 p0 = stops[i], p1 = stops[i + 1];
                    CordNode na = g.Nodes[e.A], nb = g.Nodes[e.B];
                    MachineInfo ma = na.IsMachine ? na.Machine : null, mb = nb.IsMachine ? nb.Machine : null;
                    // the planner's own route rule: walkable A*, else (dive-through on) the dive A*
                    if (CordPlanner.FindPath(w, p0.Floor, p1.Floor, opt.DiveThrough,
                                             c => (ma != null && ma.Contains(c)) || (mb != null && mb.Contains(c))) != null) continue;
                    var c = new Case { Source = source, W = w, P0 = p0, P1 = p1, EndA = na.OracleName, EndB = nb.OracleName };
                    Classify(w, c, new[] { na.Machine, nb.Machine });
                    string ea = na.OracleName + ":" + na.Cell.X + "," + na.Cell.Z, eb = nb.OracleName + ":" + nb.Cell.X + "," + nb.Cell.Z;
                    LaidPiece lp = ps.FirstOrDefault(p => p.Unroutable && ((p.EndA == ea && p.EndB == eb) || (p.EndA == eb && p.EndB == ea)));
                    if (lp != null) foreach (CordStrand st in lp.Strands) c.Strands.Add(st.Pts);
                    outp.Add(c);
                }
            }
            return outp;
        }

        private static void Classify(CordWorld w, Case c, MachineInfo[] ends)
        {
            var seen = new HashSet<Cell>();
            int n = (int)(V2.Dist(c.P0, c.P1) / 0.05) + 2;
            for (int k = 0; k < n; k++)
            {
                Cell q = (c.P0 + (c.P1 - c.P0) * (k / (double)(n - 1))).Floor;
                if (w.IsWalkable(q) || ends.Any(m => m != null && m.Contains(q)) || !seen.Add(q)) continue;
                c.Crossed.Add(q);
            }
            bool water = c.Crossed.Any(q => w.BlockAt(q) == BlockKind.Water);
            bool solid = c.Crossed.Any(q => w.BlockAt(q) == BlockKind.Wall || w.BlockAt(q) == BlockKind.Rock);
            bool condInSolid = c.Crossed.Any(q => (w.BlockAt(q) == BlockKind.Wall || w.BlockAt(q) == BlockKind.Rock) && w.IsConduit(q));
            bool building = c.Crossed.Any(q => w.BlockAt(q) == BlockKind.Device);
            if (solid && condInSolid) c.Class = "a";
            else if (water) c.Class = "b";
            else if (solid) c.Class = WallHasConduit(w, c.Crossed) ? "c-wall-conduit-elsewhere" : "c-wall";
            else if (building) c.Class = "c-building";
            else c.Class = "c-enclosed";
            c.Detail = string.Join(",", c.Crossed.Select(q => w.BlockAt(q).ToString() + (w.IsConduit(q) ? "+conduit" : "")).Distinct());
        }

        /// <summary>Does the wall/rock mass the leg crosses (4-connected) carry conduit anywhere? Then the owner's "dive in at the
        /// conduit" has a place to dive, just not on this lead's line.</summary>
        private static bool WallHasConduit(CordWorld w, List<Cell> crossed)
        {
            bool Solid(Cell q) => w.BlockAt(q) == BlockKind.Wall || w.BlockAt(q) == BlockKind.Rock;
            var seen = new HashSet<Cell>();
            var st = new Stack<Cell>(crossed.Where(Solid));
            while (st.Count > 0)
            {
                Cell q = st.Pop();
                if (!w.InBounds(q) || !Solid(q) || !seen.Add(q)) continue;
                if (w.IsConduit(q)) return true;
                foreach (Cell d in Cell.Dirs4) st.Push(q + d);
            }
            return false;
        }

        // ------------------------------------------------------------------ constructed vanilla-legal scenes
        private static CordWorld Room(int W, int H, int x0, int z0, int x1, int z1, BlockKind k = BlockKind.Wall)
        {
            var w = new CordWorld(W, H);
            for (int x = x0; x <= x1; x++) { w.SetBlocked(new Cell(x, z0), k); w.SetBlocked(new Cell(x, z1), k); }
            for (int z = z0; z <= z1; z++) { w.SetBlocked(new Cell(x0, z), k); w.SetBlocked(new Cell(x1, z), k); }
            return w;
        }

        private static MachineInfo Dev(CordWorld w, string id, int x, int z, MachineKind k = MachineKind.Consumer, int sz = 1)
        {
            var m = new MachineInfo { Id = id, Kind = k, X0 = x, Z0 = z, W = sz, H = sz };
            for (int a = 0; a < sz; a++) for (int b = 0; b < sz; b++) w.SetBlocked(new Cell(x + a, z + b), BlockKind.Device);
            w.Machines.Add(m);
            return m;
        }

        private static void Run(CordWorld w, int x0, int x1, int z) { for (int x = x0; x <= x1; x++) w.SetConduit(new Cell(x, z)); }

        /// <summary>(name, world, expected class or null = routable). Each is a layout vanilla allows: PowerConnectionMaker.
        /// BestTransmitterForConnector hooks a connector to the nearest transmitter in a 13x13 box (ExpandedBy(6)) with NO wall or
        /// line-of-sight test, and conduit may be built under walls and on shallow water.</summary>
        internal static List<(string name, CordWorld w, string expect)> Constructed()
        {
            var L = new List<(string, CordWorld, string)>();
            // 1. the owner's case: a conduit runs THROUGH the wall into the room; the lamp hooks to it inside
            {
                CordWorld w = Room(16, 10, 6, 1, 13, 8);
                Run(w, 1, 9, 4);                       // conduit outside, under the wall at (6,4), on into the room
                MachineInfo src = Dev(w, "gen", 0, 4, MachineKind.Source); src.Hookups.Add(new Cell(1, 4));
                MachineInfo lamp = Dev(w, "lamp", 10, 4, MachineKind.Lamp); lamp.Hookups.Add(new Cell(9, 4));
                L.Add(("1 conduit through the wall (owner's case)", w, null));
            }
            // 2. a lamp in a sealed room hooks to conduit OUTSIDE the wall, 3 cells away; no conduit in the wall
            {
                CordWorld w = Room(16, 10, 6, 1, 13, 8);
                Run(w, 1, 4, 4);
                MachineInfo src = Dev(w, "gen", 0, 4, MachineKind.Source); src.Hookups.Add(new Cell(1, 4));
                MachineInfo lamp = Dev(w, "lamp", 7, 4, MachineKind.Lamp); lamp.Hookups.Add(new Cell(4, 4));
                L.Add(("2 hookup through a wall with no conduit in it", w, "c-wall"));
            }
            // 3. a lamp on an island hooks across deep water to conduit on the shore
            {
                var w = new CordWorld(16, 10);
                for (int x = 5; x <= 15; x++) for (int z = 0; z < 10; z++) if (!(x >= 9 && x <= 11 && z >= 3 && z <= 5)) w.SetBlocked(new Cell(x, z), BlockKind.Water);
                Run(w, 1, 4, 4);
                MachineInfo src = Dev(w, "gen", 0, 4, MachineKind.Source); src.Hookups.Add(new Cell(1, 4));
                MachineInfo lamp = Dev(w, "lamp", 10, 4, MachineKind.Lamp); lamp.Hookups.Add(new Cell(4, 4));
                L.Add(("3 hookup across deep water to an island", w, "b"));
            }
            // 4. conduit laid across the water to the island (it is buried there; stub, hidden run, stub)
            {
                var w = new CordWorld(16, 10);
                for (int x = 5; x <= 15; x++) for (int z = 0; z < 10; z++) if (!(x >= 9 && x <= 11 && z >= 3 && z <= 5)) w.SetBlocked(new Cell(x, z), BlockKind.Water);
                Run(w, 1, 9, 4);
                MachineInfo src = Dev(w, "gen", 0, 4, MachineKind.Source); src.Hookups.Add(new Cell(1, 4));
                MachineInfo lamp = Dev(w, "lamp", 10, 4, MachineKind.Lamp); lamp.Hookups.Add(new Cell(9, 4));
                L.Add(("4 conduit laid through the water", w, null));
            }
            // 5. B9: a heater in a sealed room wired straight to a battery outside the wall (no conduit anywhere)
            {
                CordWorld w = Room(16, 10, 6, 1, 13, 8);
                MachineInfo bat = Dev(w, "bat", 3, 4, MachineKind.Battery);
                MachineInfo heater = Dev(w, "heater", 8, 4);
                CordWorldLinks.LinkToMachine(w, heater, bat);
                L.Add(("5 device wired to a battery through a wall (B9)", w, "c-wall"));
            }
            // 6. two walls: room A's lamp hooks to conduit in room C, a sealed room B between them (all within 6 cells)
            {
                var w = new CordWorld(20, 10);
                foreach (int x in new[] { 6, 9 }) for (int z = 0; z < 10; z++) w.SetBlocked(new Cell(x, z), BlockKind.Wall);
                Run(w, 1, 4, 4);
                MachineInfo src = Dev(w, "gen", 0, 4, MachineKind.Source); src.Hookups.Add(new Cell(1, 4));
                MachineInfo lamp = Dev(w, "lamp", 10, 4, MachineKind.Lamp); lamp.Hookups.Add(new Cell(4, 4));
                L.Add(("6 hookup through two walls and a closed room", w, "c-wall"));
            }
            // 7. a lamp boxed in by other buildings (shelves/batteries all round, no wall) hooks to conduit beyond them
            {
                var w = new CordWorld(16, 10);
                for (int x = 6; x <= 10; x++) for (int z = 2; z <= 6; z++) if (!(x == 8 && z == 4)) Dev(w, "box" + x + "_" + z, x, z, MachineKind.Transmitter);
                w.Machines.RemoveAll(m => m.Id.StartsWith("box"));     // footprints only: other buildings, not powered nodes
                Run(w, 1, 4, 4);
                MachineInfo src = Dev(w, "gen", 0, 4, MachineKind.Source); src.Hookups.Add(new Cell(1, 4));
                MachineInfo lamp = Dev(w, "lamp", 8, 4, MachineKind.Lamp); lamp.Hookups.Add(new Cell(4, 4));
                L.Add(("7 hookup out of a ring of other buildings", w, "c-building"));
            }
            // 8. conduit under the wall itself, the lamp inside hooks to that wall cell (vanilla: conduit under walls is legal)
            {
                CordWorld w = Room(16, 10, 6, 1, 13, 8);
                Run(w, 1, 6, 4);
                MachineInfo src = Dev(w, "gen", 0, 4, MachineKind.Source); src.Hookups.Add(new Cell(1, 4));
                MachineInfo lamp = Dev(w, "lamp", 8, 4, MachineKind.Lamp); lamp.Hookups.Add(new Cell(6, 4));
                L.Add(("8 hookup to the conduit cell under the wall", w, null));
            }
            return L;
        }

        private static BuildOptions Opt(bool dive = true) => new BuildOptions { DiveThrough = dive };

        /// <summary>Dive-through scene: a lamp in a sealed room hooks to conduit outside; conduit DOES pass under the room's
        /// wall, on another row (the 121-lead class c-wall-conduit-elsewhere).</summary>
        internal static CordWorld WallConduitElsewhere()
        {
            CordWorld w = Room(16, 10, 6, 1, 13, 8);
            Run(w, 1, 9, 6);                                   // under the wall at (6,6) into the room
            for (int z = 3; z <= 6; z++) w.SetConduit(new Cell(4, z));
            MachineInfo src = Dev(w, "gen", 0, 6, MachineKind.Source); src.Hookups.Add(new Cell(1, 6));
            MachineInfo lamp = Dev(w, "lamp", 8, 3, MachineKind.Lamp); lamp.Hookups.Add(new Cell(4, 3));
            return w;
        }

        /// <summary>One scene laid with dive-through on: the pieces that dive, and every check a dived cord must pass.</summary>
        private static void DiveScene(string name, CordWorld w, BlockKind barrier, int minDives)
        {
            var b = new CordBuilder();
            List<LaidPiece> ps = b.Build(w, Opt(true), c => true);
            Check(ps.All(p => !p.Unroutable), "dive " + name + ": no piece unroutable (" + ps.Count(p => p.Unroutable) + ")");
            List<LaidPiece> dived = ps.Where(p => p.Dives > 0).ToList();
            int dives = dived.Sum(p => p.Dives);
            Check(dives >= minDives, "dive " + name + ": " + dives + " dives (want >= " + minDives + ")");
            bool InEnd(Cell c) => w.Machines.Any(m => m.Contains(c));
            // within the overrun (PastFaceDepth) of an open or end-art cell: a dive end just past its face
            bool NearOpen(V2 pt)
            {
                Cell c0 = pt.Floor;
                for (int dz = -1; dz <= 1; dz++) for (int dx = -1; dx <= 1; dx++)
                {
                    var q = new Cell(c0.X + dx, c0.Z + dz);
                    if (!(w.IsWalkable(q) || InEnd(q))) continue;
                    double ex = Math.Max(Math.Max(q.X - pt.X, 0), pt.X - (q.X + 1)), ez = Math.Max(Math.Max(q.Z - pt.Z, 0), pt.Z - (q.Z + 1));
                    if (Math.Sqrt(ex * ex + ez * ez) <= CordBuilder.PastFaceDepth + 0.01) return true;
                }
                return false;
            }
            foreach (LaidPiece p in dived)
            {
                // every drawn point of a section lies on open floor, inside an end's art, under a building (cords print below every
                // building, so its art hides them), or at most the overrun past a dive face
                int bad = 0; string where = "";
                foreach (CordStrand st in p.Strands)
                    for (int k = 1; k < st.Pts.Count - 1; k++)
                    {
                        Cell q = st.Pts[k].Floor;
                        if (!w.IsWalkable(q) && w.BlockAt(q) != BlockKind.Device && !InEnd(q) && !NearOpen(st.Pts[k])) { bad++; where = st.Pts[k] + " k" + k + "/" + st.Pts.Count + " dA" + st.DiveA + " dB" + st.DiveB + " fell" + st.FellBack; }
                    }
                Check(bad == 0, "dive " + name + ": " + bad + " drawn points inside a barrier " + where);
                Check(p.Strands.Count(x => x.DiveB) == p.Strands.Count(x => x.DiveA) && p.Strands.Any(x => x.DiveB),
                      "dive " + name + ": strands split at the dive (" + p.Strands.Count + " strands)");
                Check(p.Strands.Where(x => x.DiveA).All(x => x.WhipA == 0) && p.Strands.Where(x => x.DiveB).All(x => x.WhipB == 0),
                      "dive " + name + ": no end art at a dive face");
                int plates = p.Decals.Count(d => d.Kind == DecalKind.StubWall || d.Kind == DecalKind.StubRock);
                int want = barrier == BlockKind.Wall || barrier == BlockKind.Rock ? 2 * p.Dives : 0;
                Check(plates == want, "dive " + name + ": " + plates + " entry/exit plates (want " + want + ")");
            }
            // the same scene with the setting off: unroutable again, nothing dives
            List<LaidPiece> off = new CordBuilder().Build(w, Opt(false), c => true);
            Check(off.Any(p => p.Unroutable) && off.All(p => p.Dives == 0), "dive " + name + ": setting off restores the unroutable lead");
        }

        /// <summary>Random bases with vanilla's hookup rule (the fuzz never makes one: its hookups sit beside the machine):
        /// rooms (walls, some with a door, some with conduit run through them), ponds (some bridged by conduit), stray buildings,
        /// conduit runs, then devices on free floor, each hooked to the NEAREST conduit cell within ExpandedBy(6) exactly as
        /// PowerConnectionMaker.BestTransmitterForConnector picks it (no wall test). A device with no conduit in range is skipped.</summary>
        internal static CordWorld VanillaBase(long seed)
        {
            CordRng r = CordRng.Of("a7-vanilla-base", seed);
            int W = r.Int(24, 36), H = r.Int(18, 28);
            var w = new CordWorld(W, H);
            for (int k = r.Int(1, 3); k > 0; k--)                      // rooms
            {
                int x0 = r.Int(1, W - 9), z0 = r.Int(1, H - 8), x1 = x0 + r.Int(4, 8), z1 = z0 + r.Int(4, 7);
                for (int x = x0; x <= x1; x++) for (int z = z0; z <= z1; z++)
                    if (x == x0 || x == x1 || z == z0 || z == z1) w.SetBlocked(new Cell(x, z), BlockKind.Wall);
                if (r.Chance(0.5)) { var d = new Cell(x0 + 2, z0); w.SetBlocked(d, BlockKind.None); w.SetDoor(d); }
            }
            for (int k = r.Int(0, 2); k > 0; k--)                      // ponds
            {
                int x0 = r.Int(0, W - 5), z0 = r.Int(0, H - 4), ww = r.Int(2, 5), hh = r.Int(2, 4);
                for (int x = x0; x < Math.Min(W, x0 + ww); x++) for (int z = z0; z < Math.Min(H, z0 + hh); z++)
                    if (w.IsWalkable(new Cell(x, z))) w.SetBlocked(new Cell(x, z), BlockKind.Water);
            }
            for (int k = r.Int(0, 6); k > 0; k--)                      // stray buildings (shelves, tables): footprints, unpowered
            {
                var c = new Cell(r.Int(0, W - 1), r.Int(0, H - 1));
                if (w.IsWalkable(c) && !w.IsDoor(c)) w.SetBlocked(c, BlockKind.Device);
            }
            for (int k = r.Int(1, 3); k > 0; k--)                      // straight conduit runs (under walls and water too)
            {
                bool horiz = r.Chance(0.5);
                int a = horiz ? r.Int(0, H - 1) : r.Int(0, W - 1), s0 = r.Int(0, (horiz ? W : H) - 6), len = r.Int(4, 16);
                for (int t = s0; t < Math.Min(horiz ? W : H, s0 + len); t++)
                {
                    var c = horiz ? new Cell(t, a) : new Cell(a, t);
                    if (w.BlockAt(c) != BlockKind.Device) w.SetConduit(c);
                }
            }
            int placed = 0;
            for (int k = 0; k < 40 && placed < r.Int(2, 6); k++)        // devices
            {
                var c = new Cell(r.Int(0, W - 1), r.Int(0, H - 1));
                if (!w.IsWalkable(c) || w.IsConduit(c) || w.IsDoor(c)) continue;
                Cell best = default(Cell); int bd = int.MaxValue;
                for (int z = c.Z - 6; z <= c.Z + 6; z++) for (int x = c.X - 6; x <= c.X + 6; x++)
                {
                    var q = new Cell(x, z);
                    if (!w.IsConduit(q)) continue;
                    int d2 = (x - c.X) * (x - c.X) + (z - c.Z) * (z - c.Z);
                    if (d2 < bd) { bd = d2; best = q; }
                }
                if (bd == int.MaxValue) continue;
                MachineInfo m = Dev(w, "d" + placed, c.X, c.Z, placed == 0 ? MachineKind.Source : MachineKind.Consumer);
                m.Hookups.Add(best);
                placed++;
            }
            return w;
        }

        /// <summary>Selftest rows: every constructed scene lands in its expected class (or routes).</summary>
        public static void Checks()
        {
            // sanity probe: on random vanilla-hookup bases the instrument does find unroutable leads (so a 0 over the fuzz worlds
            // means the fuzz's adjacent hookups always route, not that the census is blind)
            int found = 0;
            int foundOn = 0, builderOn = 0;
            for (long vs = 1; vs <= 60; vs++)
            {
                found += Scan("probe", VanillaBase(vs), Opt(false), c => true, out _).Count;
                foundOn += Scan("probe", VanillaBase(vs), Opt(true), c => true, out int bu).Count;
                builderOn += bu;
            }
            Check(found > 0, "sanity: 60 vanilla-hookup bases hold " + found + " unroutable leads (dive-through off)");
            Check(foundOn == 0 && builderOn == 0, "dive-through on: 60 vanilla-hookup bases hold " + foundOn + " unroutable leads, builder flagged " + builderOn);
            foreach (var (name, w, expect) in Constructed())
            {
                List<Case> cs = Scan(name, w, Opt(false), c => true, out int bu);
                string got = cs.Count == 0 ? null : string.Join("+", cs.Select(x => x.Class).Distinct());
                Check(got == expect, name + ": " + (got ?? "routable") + " (expected " + (expect ?? "routable") + ", builder unroutable " + bu + ")");
                List<Case> on = Scan(name, w, Opt(true), c => true, out int buOn);
                Check(on.Count == 0 && buOn == 0, name + " with dive-through: " + on.Count + " unroutable legs, builder flagged " + buOn);
                if (expect == null)
                {
                    // a scene that already routes never dives, and lays bit-identically with the setting on or off
                    List<LaidPiece> a = new CordBuilder().Build(w, Opt(true), c => true), b = new CordBuilder().Build(w, Opt(false), c => true);
                    Check(a.All(p => p.Dives == 0) && a.Count == b.Count && a.Zip(b, (x, y) => x.GeometryHash() == y.GeometryHash()).All(t => t),
                          name + ": routable scene unchanged by dive-through");
                }
            }
            // one scene per class, laid with dive-through on
            var cons = Constructed();
            DiveScene("c-wall (sealed room, no conduit in the wall)", cons[1].w, BlockKind.Wall, 1);
            DiveScene("c-wall-conduit-elsewhere", WallConduitElsewhere(), BlockKind.Wall, 1);
            DiveScene("b water (island)", cons[2].w, BlockKind.Water, 1);
            DiveScene("c-wall two walls", cons[5].w, BlockKind.Wall, 2);
            DiveScene("c-wall battery link (B9)", cons[4].w, BlockKind.Wall, 1);
            DiveScene("c-building ring", cons[6].w, BlockKind.Device, 1);
            {
                List<Case> cs = Scan("wce", WallConduitElsewhere(), Opt(false), c => true, out _);
                Check(cs.Count > 0 && cs.All(c => c.Class == "c-wall-conduit-elsewhere"), "wall-conduit-elsewhere scene classifies as such: " + string.Join("+", cs.Select(c => c.Class)));
            }
        }

        /// <summary>--unroutable-census out.json [fuzzSeeds]: the fuzz worlds + the constructed scenes, every case written out.</summary>
        public static int Run(string outPath, int seeds)
        {
            var all = new List<Case>();
            int worlds = 0, builderTotal = 0, fuzzCases = 0;
            var firstPerClass = new Dictionary<string, Case>();
            var keyCounts = new Dictionary<string, int>();
            foreach (var (seed, step, w, opt, live) in GssFuzz.CordWorlds(seeds))
            {
                worlds++;
                List<Case> cs = Scan("fuzz seed " + seed + " step " + step, w, opt, live, out int bu);
                builderTotal += bu;
                foreach (Case c in cs)
                {
                    fuzzCases++;
                    // a seed's later steps repeat the same unroutable leg: count distinct (seed, ends, class) once
                    string key = seed + "|" + c.EndA + "|" + c.EndB + "|" + c.P0.Floor + "|" + c.P1.Floor + "|" + c.Class;
                    keyCounts.TryGetValue(key, out int kc); keyCounts[key] = kc + 1;
                    if (kc == 0) all.Add(c);
                }
            }
            var vanilla = new List<Case>();
            var vanillaOn = new List<Case>();
            int vWorlds = 0, vLeads = 0, vBuilder = 0, vBuilderOn = 0, vDives = 0;
            for (long vs = 1; vs <= seeds * 10; vs++)
            {
                CordWorld w = VanillaBase(vs);
                vWorlds++;
                vLeads += w.Machines.Count;
                List<Case> cs = Scan("vanilla base " + vs, w, Opt(false), c => true, out int bu);
                vBuilder += bu;
                vanilla.AddRange(cs);
                vanillaOn.AddRange(Scan("vanilla base " + vs, w, Opt(true), c => true, out int buOn));
                vBuilderOn += buOn;
                vDives += new CordBuilder().Build(w, Opt(true), c => true).Sum(p => p.Dives);
            }
            var vByClass = vanilla.GroupBy(c => c.Class).ToDictionary(g => g.Key, g => g.Count());
            var vByClassOn = vanillaOn.GroupBy(c => c.Class).ToDictionary(g => g.Key, g => g.Count());
            var constructed = new List<Case>();
            foreach (var (name, w, expect) in Constructed())
            {
                List<Case> cs = Scan(name, w, Opt(false), c => true, out int bu);
                if (cs.Count == 0)
                {
                    var b = new CordBuilder();
                    var ps = b.Build(w, Opt(false), c => true);
                    var ok = new Case { Source = name, W = w, Class = "routable", Detail = "" };
                    foreach (LaidPiece p in ps) foreach (CordStrand st in p.Strands) ok.Strands.Add(st.Pts);
                    constructed.Add(ok);
                }
                else constructed.AddRange(cs);
            }
            var byClass = all.GroupBy(c => c.Class).ToDictionary(g => g.Key, g => g.Count());
            Console.WriteLine("census: " + worlds + " fuzz worlds, " + fuzzCases + " unroutable legs (" + all.Count + " distinct), builder flagged " + builderTotal + " pieces");
            foreach (var kv in byClass.OrderBy(k => k.Key)) Console.WriteLine("  fuzz class " + kv.Key + ": " + kv.Value);
            Console.WriteLine("vanilla-hookup bases: " + vWorlds + " maps, " + vLeads + " device leads, " + vanilla.Count + " unroutable legs, builder flagged " + vBuilder);
            foreach (var kv in vByClass.OrderBy(k => k.Key)) Console.WriteLine("  vanilla class " + kv.Key + ": " + kv.Value);
            Console.WriteLine("with dive-through on: " + vanillaOn.Count + " unroutable legs, builder flagged " + vBuilderOn + ", " + vDives + " dives laid");
            foreach (var kv in vByClassOn.OrderBy(k => k.Key)) Console.WriteLine("  vanilla class (dive on) " + kv.Key + ": " + kv.Value);
            foreach (Case c in constructed) Console.WriteLine("  constructed " + c.Source + ": " + c.Class + " " + c.Detail);
            using (var fs = File.Create(outPath))
            using (var j = new Utf8JsonWriter(fs, new JsonWriterOptions { Indented = false }))
            {
                j.WriteStartObject();
                j.WriteNumber("fuzzWorlds", worlds); j.WriteNumber("fuzzLegs", fuzzCases); j.WriteNumber("builderFlagged", builderTotal);
                j.WriteStartObject("fuzzByClass"); foreach (var kv in byClass) j.WriteNumber(kv.Key, kv.Value); j.WriteEndObject();
                j.WriteNumber("vanillaMaps", vWorlds); j.WriteNumber("vanillaLeads", vLeads); j.WriteNumber("vanillaBuilderFlagged", vBuilder);
                j.WriteStartObject("vanillaByClass"); foreach (var kv in vByClass) j.WriteNumber(kv.Key, kv.Value); j.WriteEndObject();
                j.WriteNumber("vanillaLegsDiveOn", vanillaOn.Count); j.WriteNumber("vanillaBuilderFlaggedDiveOn", vBuilderOn); j.WriteNumber("vanillaDivesLaid", vDives);
                j.WriteStartObject("vanillaByClassDiveOn"); foreach (var kv in vByClassOn) j.WriteNumber(kv.Key, kv.Value); j.WriteEndObject();
                j.WriteStartArray("cases");
                // every constructed case, every fuzz case, and the first 6 vanilla-base cases of each class (the renderer's pool)
                foreach (Case c in constructed.Concat(all).Concat(vanilla.GroupBy(c => c.Class).SelectMany(g => g.Take(6)))) WriteCase(j, c);
                j.WriteEndArray();
                j.WriteEndObject();
            }
            return 0;
        }

        private static void WriteCase(Utf8JsonWriter j, Case c)
        {
            CordWorld w = c.W;
            j.WriteStartObject();
            j.WriteString("source", c.Source); j.WriteString("class", c.Class); j.WriteString("detail", c.Detail ?? "");
            j.WriteString("endA", c.EndA ?? ""); j.WriteString("endB", c.EndB ?? "");
            j.WriteNumber("w", w.Width); j.WriteNumber("h", w.Height);
            var rows = new List<string>();
            for (int z = 0; z < w.Height; z++)
            {
                var sb = new System.Text.StringBuilder();
                for (int x = 0; x < w.Width; x++)
                {
                    var q = new Cell(x, z);
                    char ch = ".WRwD"[Math.Min(4, (int)w.BlockAt(q) == 5 ? 0 : (int)w.BlockAt(q))];
                    if (w.IsDoor(q)) ch = '|';
                    sb.Append(ch).Append(w.IsConduit(q) ? '+' : ' ');
                }
                rows.Add(sb.ToString());
            }
            j.WriteStartArray("rows"); foreach (string r in rows) j.WriteStringValue(r); j.WriteEndArray();
            j.WriteStartArray("machines");
            foreach (MachineInfo m in w.Machines) { j.WriteStartObject(); j.WriteString("id", m.Id); j.WriteString("kind", m.Kind.ToString()); j.WriteNumber("x", m.X0); j.WriteNumber("z", m.Z0); j.WriteNumber("w", m.W); j.WriteNumber("h", m.H); j.WriteEndObject(); }
            j.WriteEndArray();
            j.WriteStartArray("leg"); j.WriteNumberValue(c.P0.X); j.WriteNumberValue(c.P0.Z); j.WriteNumberValue(c.P1.X); j.WriteNumberValue(c.P1.Z); j.WriteEndArray();
            j.WriteStartArray("crossed"); foreach (Cell q in c.Crossed) { j.WriteStartArray(); j.WriteNumberValue(q.X); j.WriteNumberValue(q.Z); j.WriteEndArray(); } j.WriteEndArray();
            j.WriteStartArray("strands");
            foreach (var st in c.Strands)
            {
                j.WriteStartArray();
                for (int i = 0; i < st.Count; i += 2) { j.WriteNumberValue(Math.Round(st[i].X, 3)); j.WriteNumberValue(Math.Round(st[i].Z, 3)); }
                j.WriteEndArray();
            }
            j.WriteEndArray();
            j.WriteEndObject();
        }
    }
}
