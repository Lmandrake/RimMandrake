// Gimme Some Slack core: Verse-free (see CordMath.cs header).
// Orchestration of nodal.build_nodal for phase 1a: reduce -> plan -> lay, cached per edge.
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace RimMandrake.GimmeSomeSlack.Core
{
    public enum DecalKind { Plug, JunctionTape, JunctionTin, StubWall, StubRock, PowerStrip, FrayDead, FrayLive, PowerStripDark }

    /// <summary>A decal's drawn height over its width. The power strip's art is 64x32 lit AND dark (GPT source read 2026-10-06
    /// A19: the dark strip drew at aspect 1, twice as tall as the lit one).</summary>
    public static class DecalAspect
    {
        public static float Of(DecalKind k) => k == DecalKind.PowerStrip || k == DecalKind.PowerStripDark ? 0.5f : 1f;
    }

    /// <summary>What a pile (tangle) and a device stub are built from (owner review 2026-10-04 B1/B2/B13/B15): power strips
    /// only for the modern extension-cord look; every other look plugs its cables into many + and T junction boxes.</summary>
    public enum PileArt { Junctions, Strips }

    public struct CordDecal
    {
        public DecalKind Kind;
        public V2 Pos;
        /// <summary>Radians, 0 = +X; the art's long axis points along it.</summary>
        public double Angle;
        public double Scale;
        /// <summary>Extra scale along the art's own X axis (0 = none): the rock-entry hole is foreshortened as if cut
        /// into an angled face (owner review 2026-10-04 B4).</summary>
        public double Squash;
        /// <summary>A live fray that rides the whipping tail: printed statically only with whip off.</summary>
        public bool OnWhip;
        /// <summary>Round 4: the art sub-rectangle printed (u along art X, v along art Z); U1 = 0 means the whole canvas. A wall
        /// plate prints only its plate, never the art's own curl of cord (WallMount).</summary>
        public double U0, U1, V0, V1;
        public CordDecal(DecalKind k, V2 p, double a, double s) { Kind = k; Pos = p; Angle = a; Scale = s; OnWhip = false; Squash = 0; U0 = U1 = V0 = V1 = 0; }
        public bool Cropped => U1 > 0;
        public double ScaleX => Scale * (Squash > 0 ? Squash : 1);
    }

    public sealed class CordStrand
    {
        public List<V2> Pts;
        /// <summary>0..1 texture phase so parallel cords do not show the same wear.</summary>
        public double S0;
        /// <summary>A hanging wall-terminal tail: drawn over the wall face, exempt from the floor rule.</summary>
        public bool OverFace;
        /// <summary>The slack could not be laid clear of obstacles; this is the planned centreline.</summary>
        public bool FellBack;
        /// <summary>Points at the start / end of Pts that form a live terminal's whipping tail (phase 1b
        /// B3): the section layer leaves them out of the static mesh while whipping is on, and the map
        /// component draws them bent per frame. 0 = no tail.</summary>
        public int WhipA, WhipB;
        /// <summary>A lifted piece (wall-hanging tail): sways in the wind, weight per point (0 at the pin).</summary>
        public bool Lifted;
        public double[] SwayW;
        /// <summary>Rope-settle diagnostics (phase 1b B1); null when the strand was not settled.</summary>
        public SettleStats Settle;
    }

    /// <summary>A conduit end that reads live or dead: where sparks go (design §8.5).</summary>
    public sealed class CordEnd
    {
        public V2 Tip;
        public V2 Dir;
        public Cell NetCell;
        public bool Wall;
    }

    public sealed class LaidPiece
    {
        public string Key;
        public Cell Owner;
        public List<CordStrand> Strands = new List<CordStrand>();
        public List<CordDecal> Decals = new List<CordDecal>();
        public List<CordEnd> Ends = new List<CordEnd>();
        /// <summary>Net cells whose live flag this piece's LOOK depends on beyond its Ends (tangle and
        /// device-strip LEDs): the component's live poll re-prints the piece when one flips.</summary>
        public List<Cell> LiveKeys = new List<Cell>();
        public bool Unroutable;
        public double PathLen, LaidRatio;
        /// <summary>Corridor rect and the walkability hash it was planned on (§8.2.7).</summary>
        public int CX0, CZ0, CX1, CZ1;
        public ulong CorridorHash;
        /// <summary>What LayEdge reads from the graph beyond the cache key: the parallel flag (a pair joined by
        /// more than one edge routes through its chain's middle cell) and the spur knots. A cached piece is reused
        /// only when this matches too (lane F 2026-10-02: a ring split by a connector kept its parallel route).</summary>
        public string LaySig;
        public string EndA, EndB;   // oracle-style "type:x,z"

        public ulong GeometryHash()
        {
            ulong h = 1469598103934665603UL;
            foreach (CordStrand s in Strands)
                foreach (V2 p in s.Pts)
                {
                    h = (h ^ unchecked((ulong)(long)Math.Round(p.X * 1000))) * 1099511628211UL;
                    h = (h ^ unchecked((ulong)(long)Math.Round(p.Z * 1000))) * 1099511628211UL;
                }
            return h;
        }
    }

    public sealed class BuildOptions
    {
        public LayParams Lay = new LayParams();
        public bool Tangles = true;
        public bool NeedlessLoops = true;
        public ulong Seed = 1;
        /// <summary>Messiness: dense fields of at least this many cells become a tangle (setting, 6-20).</summary>
        public int TangleMin = CordGraph.TangleMin;
        /// <summary>Strips (ExtensionCord) or junction boxes (every other style) in piles and at device stubs.</summary>
        public PileArt Pile = PileArt.Junctions;
        /// <summary>Per-build style stage 2: the pile art of the RUN at a cell (strips in a Modern run, junction boxes in every
        /// other), null where the cell stores no style (then <see cref="Pile"/>, the default look's).</summary>
        public Func<Cell, PileArt?> PileAt;

        public PileArt PileFor(Cell c) => PileAt?.Invoke(c) ?? Pile;
    }

    /// <summary>
    /// Builds every cord piece of a map. Holds the per-edge cache: an edge whose endpoints, chain,
    /// live flags and corridor walkability are unchanged re-emits its cached polylines bit-identically
    /// and costs no planning (§8.2.7).
    /// </summary>
    public sealed class CordBuilder
    {
        private Dictionary<string, LaidPiece> cache = new Dictionary<string, LaidPiece>();
        public int LastPlanned, LastReused;
        public CordGraph Graph { get; private set; }

        public List<LaidPiece> Build(CordWorld w, BuildOptions opt, Func<Cell, bool> isLive)
        {
            CordGraph g = CordGraph.Reduce(w, opt.Seed, opt.Tangles ? opt.TangleMin : int.MaxValue,
                                           opt.NeedlessLoops ? CordGraph.SpurMax : 0);
            Graph = g;
            var next = new Dictionary<string, LaidPiece>();
            var outp = new List<LaidPiece>();
            LastPlanned = LastReused = 0;
            var pairCount = new Dictionary<string, int>();
            List<CordEdge> cordEdges = g.CordEdges().ToList();
            var pairTotal = new Dictionary<string, int>();
            foreach (CordEdge x in cordEdges)
            {
                string k = PairKey(x.A, x.B);
                pairTotal.TryGetValue(k, out int tot);
                pairTotal[k] = tot + 1;
            }
            foreach (CordEdge e in cordEdges)
            {
                string pk = PairKey(e.A, e.B);
                pairCount.TryGetValue(pk, out int mult);
                pairCount[pk] = mult + 1;
                bool parallel = pairTotal[pk] > 1 || e.A == e.B;
                string ekey = EdgeKey(g, e, mult);
                var full = new StringBuilder(ekey).Append('#');
                foreach (VId v in e.Chain()) full.Append(v.ToString()).Append(';');
                foreach (VId v in new[] { e.A, e.B })
                {
                    // everything LayEdge/EndDecor read off the node beyond its type: whether a buried run ends inside the wall (a
                    // wall terminal), the open side of a dead end, the stub's direction and face. Without these a conduit removed
                    // behind a stub left its cached piece standing in the old look (gss fuzz seed 81: incremental != fresh).
                    CordNode nn = g.Nodes[v];
                    full.Append(nn.Type).Append(nn.WallTerminal ? "W" : "").Append(nn.Gap ? "G" : "")
                        .Append(nn.Cls).Append(nn.Out.X).Append('/').Append(nn.Out.Z)
                        .Append(nn.Into.X.ToString("0.00", System.Globalization.CultureInfo.InvariantCulture)).Append('/').Append(nn.Into.Z.ToString("0.00", System.Globalization.CultureInfo.InvariantCulture))
                        .Append(nn.Face.X.ToString("0.00", System.Globalization.CultureInfo.InvariantCulture)).Append('/').Append(nn.Face.Z.ToString("0.00", System.Globalization.CultureInfo.InvariantCulture)).Append(',');
                }
                foreach (VId v in new[] { e.A, e.B })
                    if (g.Nodes[v].Type == NodeType.Terminal || g.Nodes[v].WallTerminal || g.Nodes[v].Type == NodeType.StubDevice) full.Append(isLive(g.Nodes[v].Cell) ? 'L' : 'D');
                foreach (VId v in new[] { e.A, e.B })
                    if (g.Nodes[v].Type == NodeType.Tangle && g.Nodes[v].Cells != null)
                    {
                        full.Append("T").Append(g.Nodes[v].Cells.Count);   // round 5: the entry port follows the pile's connectors
                        foreach (Cell c in g.Nodes[v].Cells) full.Append(';').Append(c.X).Append(',').Append(c.Z);
                    }
                full.Append('#').Append(opt.Lay.Fingerprint()).Append('#').Append(opt.PileFor(g.Nodes[e.A].Cell)).Append(opt.PileFor(g.Nodes[e.B].Cell));
                string fk = full.ToString();
                string sig = LaySignature(e, parallel);
                if (cache.TryGetValue(fk, out LaidPiece old) && old.LaySig == sig && CorridorHash(w, old) == old.CorridorHash)
                {
                    next[fk] = old;
                    outp.Add(old);
                    LastReused++;
                    continue;
                }
                LaidPiece lp = LayEdge(w, g, e, ekey, parallel, opt, isLive);
                lp.Key = fk;
                lp.LaySig = sig;
                lp.CorridorHash = CorridorHash(w, lp);
                next[fk] = lp;
                outp.Add(lp);
                LastPlanned++;
            }
            // node pieces: junction decals, tangles (cheap, never cached)
            foreach (var kv in g.Nodes.OrderBy(k => k.Key))
            {
                CordNode nd = kv.Value;
                if (nd.Type == NodeType.Junction)
                {
                    var p = new LaidPiece { Key = "node:" + kv.Key, Owner = nd.Cell };
                    JunctionPose jp = PoseJunction(g, kv.Key, opt.Seed);
                    p.Decals.Add(new CordDecal(jp.Kind, jp.Centre, jp.Angle, JunctionScale));
                    outp.Add(p);
                }
                else if (nd.Type == NodeType.Tangle)
                    outp.Add(TanglePiece(w, nd, opt, isLive));
            }
            foreach (var sk in g.SpurKnots)
            {
                if (!g.Nodes.TryGetValue(sk.Key, out CordNode j) || j.Type != NodeType.Junction) continue;
                var p = new LaidPiece { Key = "coil:" + sk.Key, Owner = j.Cell };
                CordRng r = CordRng.Of(opt.Seed, "spurcoil", j.Cell.X, j.Cell.Z);
                var coil = CordLayer.Loop(j.Pos, new V2(1, 0), new V2(0, 1), 0.22, r.Sign());
                CordLayer.ProjectOut(w, coil);
                if (coil.All(q => w.IsWalkable(q.Floor))) p.Strands.Add(new CordStrand { Pts = coil, S0 = r.Value() });
                outp.Add(p);
            }
            cache = next;
            return outp;
        }

        /// <summary>Everything LayEdge takes from the graph that the cache key (endpoints, chain, live flags, lay
        /// fingerprint) does not already pin: the parallel flag and the knot points.</summary>
        private static string LaySignature(CordEdge e, bool parallel)
        {
            var sb = new StringBuilder(parallel ? "P" : "S");
            foreach (V2 k in e.Knots)
                sb.Append(';').Append(k.X.ToString("0.000", System.Globalization.CultureInfo.InvariantCulture))
                  .Append(',').Append(k.Z.ToString("0.000", System.Globalization.CultureInfo.InvariantCulture));
            return sb.ToString();
        }

        private static string PairKey(VId a, VId b) => a.CompareTo(b) <= 0 ? a + "|" + b : b + "|" + a;

        /// <summary>Seed from the two endpoint cells, their node types and positions, plus the index
        /// among parallel edges: an unrelated edit never reshuffles a cord (§8.2.5).</summary>
        public static string EdgeKey(CordGraph g, CordEdge e, int mult)
        {
            string Ka(VId v, V2 p) => v.T + ":" + g.Nodes[v].Cell.X + "," + g.Nodes[v].Cell.Z + ":" +
                                     p.X.ToString("0.00", System.Globalization.CultureInfo.InvariantCulture) + "," +
                                     p.Z.ToString("0.00", System.Globalization.CultureInfo.InvariantCulture);
            string a = Ka(e.A, e.PA), b = Ka(e.B, e.PB);
            return (string.CompareOrdinal(a, b) <= 0 ? a + "|" + b : b + "|" + a) + "|" + mult;
        }

        private static ulong CorridorHash(CordWorld w, LaidPiece p)
        {
            ulong h = 1469598103934665603UL;
            for (int z = p.CZ0; z <= p.CZ1; z++)
                for (int x = p.CX0; x <= p.CX1; x++)
                {
                    var c = new Cell(x, z);
                    h = (h ^ CellSig(w, c)) * 1099511628211UL;
                }
            return h;
        }

        /// <summary>One cell's part of a corridor hash: walkable, door, and (GPT source read 2026-10-06 B7/A13) the route cost
        /// (trees 1.5, water 3), so a tree cut or planted re-plans the cords and hoses through it instead of leaving the old
        /// route standing until a reload.</summary>
        public static ulong CellSig(CordWorld w, Cell c) =>
            (ulong)(w.IsWalkable(c) ? 1 : 2) ^ (w.IsDoor(c) ? 4UL : 0UL) ^ ((ulong)Math.Round(w.ExtraCost(c) * 16) << 3);

        /// <summary>An edge with a machine at either end is that device's lead: one cord (round 3).</summary>
        public static bool DeviceLead(CordNode a, CordNode b) => (a.IsMachine && a.Machine != null) || (b.IsMachine && b.Machine != null);

        private static LaidPiece LayEdge(CordWorld w, CordGraph g, CordEdge e, string key, bool parallel, BuildOptions opt,
                                         Func<Cell, bool> isLive)
        {
            LayParams prm = opt.Lay;
            CordNode na = g.Nodes[e.A], nb = g.Nodes[e.B];
            var piece = new LaidPiece
            {
                Owner = na.Cell.CompareTo(nb.Cell) <= 0 ? na.Cell : nb.Cell,
                EndA = na.OracleName + ":" + na.Cell.X + "," + na.Cell.Z,
                EndB = nb.OracleName + ":" + nb.Cell.X + "," + nb.Cell.Z
            };
            CordRng rr = CordRng.Of(opt.Seed, "cord", key);
            var mids = new List<KeyValuePair<V2, WaypointKind>>();
            foreach (V2 k in e.Knots) mids.Add(new KeyValuePair<V2, WaypointKind>(k, WaypointKind.Knot));
            if (parallel && e.Via.Count > 0)
            {
                VId mid = e.Via[e.Via.Count / 2];
                if (mid.T == 'c') mids.Add(new KeyValuePair<V2, WaypointKind>(mid.A.Centre, WaypointKind.Via));
            }
            CordPlan pl = CordPlanner.Plan(w, e.PA, e.PB, mids);
            piece.Unroutable = !pl.Ok;
            List<V2> C = CordPlanner.RoundCorners(pl.Points);
            CordLayer.ProjectOut(w, C);
            double L = Geo.Length(C);
            int n = rr.Int(prm.CordsMin, Math.Max(prm.CordsMin, prm.CordsMax));
            // round 3 (owner 2026-10-04, station 9: "very odd triple cords going a short distance from the wall to a lamp.
            // Should just be one cord"): a device's own lead is ONE cord into its one plug; bundles stay between junctions,
            // stubs and conduit ends. The draw above still runs, so every later seeded value is unchanged.
            if (DeviceLead(na, nb)) n = 1;
            double slack = rr.Range(prm.SlackLo, prm.SlackHi) * prm.SlackScale;
            double maxExtra = prm.SlackScale <= 0 ? 0 : Math.Min(Math.Max(slack * L, prm.MinExtra * Math.Min(1, prm.SlackScale)), prm.MaxExtra);
            int limpSideA = CordRng.Of(opt.Seed, "limp", na.Cell.X, na.Cell.Z).Sign();
            int limpSideB = CordRng.Of(opt.Seed, "limp", nb.Cell.X, nb.Cell.Z).Sign();
            double laid = 0;
            for (int i = 0; i < n; i++)
            {
                double lat = n == 1 ? 0 : (i - (n - 1) / 2.0) * 0.1;
                double[] cl = Geo.CumLen(C);
                var P = new List<V2>(C.Count);
                for (int k = 0; k < C.Count; k++)
                {
                    Geo.TanNorm(C, k, out V2 t, out V2 nn);
                    double ramp = Math.Min(1, Math.Min(cl[k], L - cl[k]) / 0.3) * 0.6 + 0.4;
                    P.Add(C[k] + nn * (lat * ramp));
                }
                SettleStats settle = null;
                if (pl.Ok && L > 1.2 && prm.SlackScale > 0)
                    P = CordLayer.Sprawl(w, P, prm, slack, maxExtra, CordRng.Of(opt.Seed, "bundle", key), CordRng.Of(opt.Seed, "strand", key, i), n, out settle);
                else
                {
                    int sgn = rr.Sign();
                    for (int k = 0; k < P.Count; k++)
                    {
                        Geo.TanNorm(C, k, out V2 t, out V2 nn);
                        P[k] = P[k] + nn * (0.12 * Math.Sin(Math.PI * cl[k] / Math.Max(L, 1e-6)) * sgn);
                    }
                    CordLayer.ProjectOut(w, P);
                }
                for (int k = 0; k < e.Knots.Count; k++)
                    P = CordLayer.SpliceLoop(w, P, e.Knots[k], CordRng.Of(opt.Seed, "knot", key, i, k), 0.28 + 0.06 * i);
                // every end arrives the way its art expects (junction arm, plug, stub, conduit end)
                P = AttachEnd(w, g, e, true, P, i, n, opt);
                P = AttachEnd(w, g, e, false, P, i, n, opt);
                // terminal ends: dead = limp curl; live = straight (sparks come from the registry)
                if (na.Type == NodeType.Terminal && !isLive(na.Cell)) CordLayer.LimpTail(w, P, false, limpSideA, i);
                if (nb.Type == NodeType.Terminal && !isLive(nb.Cell)) CordLayer.LimpTail(w, P, true, limpSideB, i);
                // the floor rule (risk register row 2): if anything still sits in an unwalkable cell,
                // fall back to the planned centreline rather than draw a cord through a wall
                bool fell = false;
                if (P.Skip(1).Take(Math.Max(0, P.Count - 2)).Any(q => !w.IsWalkable(q.Floor)))
                {
                    P = new List<V2>(C);
                    fell = true;
                }
                // a machine whose art stops short of its footprint edge (solar panel legs): run the cord on under the
                // art so it visibly goes INTO the graphic (owner review 2026-10-04 B10). Appended after the floor rule:
                // these points lie inside the machine's own footprint by design.
                if (na.IsMachine && na.Machine != null) P = IntoArt(P, true, na.Machine);
                if (nb.IsMachine && nb.Machine != null) P = IntoArt(P, false, nb.Machine);
                // round 4: a cord into a wall/rock face runs on under the wall to just past the face line, so it meets the
                // plate (drawn inside the wall from the face, WallMount) with no strip of bare floor between; the wall hides
                // the overrun. Appended after the floor rule like IntoArt: these points lie in the wall cell by design.
                P = PastFace(P, true, na);
                P = PastFace(P, false, nb);
                piece.Strands.Add(new CordStrand { Pts = P, S0 = rr.Value(), FellBack = fell, Settle = settle });
                laid += Geo.Length(P);
            }
            piece.PathLen = L;
            piece.LaidRatio = n > 0 ? laid / n / Math.Max(L, 1e-6) : 0;
            EndDecor(w, g, e.A, na, piece, true, opt, isLive);
            EndDecor(w, g, e.B, nb, piece, false, opt, isLive);
            // corridor: path bounding box expanded by 3 cells (§8.2.7)
            double x0 = double.MaxValue, z0 = double.MaxValue, x1 = double.MinValue, z1 = double.MinValue;
            foreach (CordStrand s in piece.Strands)
                foreach (V2 p in s.Pts) { x0 = Math.Min(x0, p.X); z0 = Math.Min(z0, p.Z); x1 = Math.Max(x1, p.X); z1 = Math.Max(z1, p.Z); }
            if (x0 > x1) { x0 = x1 = e.PA.X; z0 = z1 = e.PA.Z; }
            piece.CX0 = Math.Max(0, (int)Math.Floor(x0) - 3);
            piece.CZ0 = Math.Max(0, (int)Math.Floor(z0) - 3);
            piece.CX1 = Math.Min(w.Width - 1, (int)Math.Floor(x1) + 3);
            piece.CZ1 = Math.Min(w.Height - 1, (int)Math.Floor(z1) + 3);
            return piece;
        }

        // ---------------------------------------------------------------- art fit (polish pass 2026-10-02)
        // Geometry of the shipped art, measured from the PNGs in canvas units (1 = the decal's side):
        // Junction_Tape is a T whose arms (art +X, -X, -Z) meet 0.152 above the canvas centre;
        // Junction_Tin is a centred 4-arm cross. Wall plates and rock holes: WallMount (round 4).
        // Round 5 (owner 2026-10-04, station 4: "T and + power junctions look very poor quality: need to make the wires thinner,
        // and ensure the junction box connectors are thicker to cover them. Make + and T connectors be relatively the same
        // central size/center"): the boxes are drawn 1.15x (round-5 brick art, af013af66: arms 18-28 px of 128 -> 0.16-0.25
        // cells thick over a 0.08 wire), T and + at the SAME scale with their arm-meeting point on the node; the art draws
        // both as one brick, same size and centre (T = the X shifted up TapeAnchorZ).
        public const double JunctionScale = 1.15, TapeAnchorZ = 0.152, ArmTuck = 0.40;
        public const double PlugScale = 0.55, PlugInset = 0.05;

        public struct JunctionPose
        {
            public DecalKind Kind;
            public double Angle;
            public V2 Centre;
            public int Arms;
        }

        public static V2 Snap4(V2 d)
        {
            if (Math.Abs(d.X) >= Math.Abs(d.Z)) return new V2(d.X < 0 ? -1 : 1, 0);
            return new V2(0, d.Z < 0 ? -1 : 1);
        }

        /// <summary>The cardinal direction an edge leaves a cell node in: toward the next cell of its chain.</summary>
        public static V2 ArmDir(CordGraph g, CordEdge e, bool atA)
        {
            VId v = atA ? e.A : e.B;
            VId nxt = e.Via.Count > 0 ? (atA ? e.Via[0] : e.Via[e.Via.Count - 1]) : (atA ? e.B : e.A);
            Cell c = g.Nodes[v].Cell;
            V2 d;
            if (nxt.IsCellish) d = new V2(nxt.A.X - c.X, nxt.A.Z - c.Z);
            else if (nxt.T == 's') d = nxt.A == c ? new V2(nxt.B.X - c.X, nxt.B.Z - c.Z) : new V2(nxt.A.X - c.X, nxt.A.Z - c.Z);
            else d = (atA ? e.PB : e.PA) - g.Nodes[v].Pos;
            return Snap4(d);
        }

        /// <summary>Which junction piece and how it is turned so an arm lies along every arriving cord:
        /// four directions take the tin cross, fewer the taped T with its missing arm where no cord comes.</summary>
        public static JunctionPose PoseJunction(CordGraph g, VId v, ulong seed)
        {
            CordNode nd = g.Nodes[v];
            CordRng r = CordRng.Of(seed, "jdecal", nd.Cell.X, nd.Cell.Z);
            if (nd.IsBlob || !v.IsCellish)
                return new JunctionPose { Kind = DecalKind.JunctionTin, Angle = 0, Centre = nd.Pos, Arms = 4 };
            var dirs = new HashSet<Cell>();
            foreach (CordEdge e in g.CordEdges())
            {
                if (e.A == v) { V2 a = ArmDir(g, e, true); dirs.Add(new Cell((int)a.X, (int)a.Z)); }
                if (e.B == v) { V2 a = ArmDir(g, e, false); dirs.Add(new Cell((int)a.X, (int)a.Z)); }
            }
            if (dirs.Count >= 4)
                return new JunctionPose { Kind = DecalKind.JunctionTin, Angle = r.Int(0, 3) * Math.PI / 2, Centre = nd.Pos, Arms = 4 };
            var order = new[] { new Cell(0, 1), new Cell(1, 0), new Cell(0, -1), new Cell(-1, 0) };
            List<Cell> missing = order.Where(c => !dirs.Contains(c)).ToList();
            Cell m = missing[r.Int(0, missing.Count - 1)];
            double angle = Math.Atan2(m.Z, m.X) - Math.PI / 2;           // the art's missing arm is its +Z
            V2 anchor = new V2(0, TapeAnchorZ * JunctionScale);
            V2 rot = new V2(anchor.X * Math.Cos(angle) - anchor.Z * Math.Sin(angle), anchor.X * Math.Sin(angle) + anchor.Z * Math.Cos(angle));
            return new JunctionPose { Kind = DecalKind.JunctionTape, Angle = angle, Centre = nd.Pos - rot, Arms = 3 };
        }

        /// <summary>The cardinal direction from a point just outside a machine's footprint into it.</summary>
        public static V2 IntoMachine(MachineInfo m, V2 p)
        {
            double l = m.X0 - p.X, rgt = p.X - (m.X0 + m.W), b = m.Z0 - p.Z, t = p.Z - (m.Z0 + m.H);
            double best = Math.Max(Math.Max(l, rgt), Math.Max(b, t));
            if (best == l) return new V2(1, 0);
            if (best == rgt) return new V2(-1, 0);
            if (best == b) return new V2(0, 1);
            return new V2(0, -1);
        }

        /// <summary>The lateral spread axis for parallel strands, the same whichever way the cord runs,
        /// so a strand keeps its side from one end of a short cord to the other.</summary>
        private static V2 Side(V2 a) => new V2(Math.Abs(a.Z), Math.Abs(a.X)).Norm();

        /// <summary>Reshape one end of a laid strand so it arrives where and how the end's art expects:
        /// into a junction arm's tip along the arm, onto the plug point heading into the machine, onto
        /// a stub face heading into it, or straight out of a conduit end.</summary>
        private static List<V2> AttachEnd(CordWorld w, CordGraph g, CordEdge e, bool atA, List<V2> P, int i, int n, BuildOptions opt)
        {
            VId v = atA ? e.A : e.B;
            CordNode nd = g.Nodes[v];
            double lat = n == 1 ? 0 : (i - (n - 1) / 2.0);
            V2 target, arrive;
            double straight = 0.15;
            if (nd.Type == NodeType.Junction && !nd.IsBlob && v.IsCellish)
            {
                V2 a = ArmDir(g, e, atA);
                // the bigger round-5 box: tuck out along the arm, but never past the far node (or the middle, when the far node is a junction that tucks too); never shorter than before
                CordNode far = g.Nodes[atA ? e.B : e.A];
                double fd = V2.Dist(nd.Pos, far.Pos), limit = far.Type == NodeType.Junction && !far.IsBlob ? 0.46 * fd : fd - 0.05;
                double tuck = Math.Min(ArmTuck * JunctionScale, Math.Max(ArmTuck, limit));
                target = nd.Pos + a * tuck + Side(a) * (lat * 0.03);
                arrive = -a;
            }
            else if (nd.IsMachine && nd.Machine != null)
            {
                target = atA ? e.PA : e.PB;
                arrive = IntoMachine(nd.Machine, target);
            }
            else if (nd.IsStub && nd.Into.Len > 0.5)
            {
                // a junction in the same cell (the run ends one cell into the wall right at a T): line
                // the stub up with the junction's arm, which starts on the junction's own (jittered) point
                CordNode other = g.Nodes[atA ? e.B : e.A];
                V2 basePos = nd.Pos;
                if (other.Type == NodeType.Junction && other.Cell == nd.Cell)
                {
                    V2 d = nd.Pos - other.Pos;
                    basePos = other.Pos + nd.Into * (d.X * nd.Into.X + d.Z * nd.Into.Z);
                }
                target = basePos + Side(nd.Into) * (lat * 0.03);
                arrive = nd.Into;
            }
            else if (nd.Type == NodeType.Tangle && nd.Cells != null)
            {
                // round 5: the cord runs on into the pile and plugs into one of its connectors' ports, along that port
                List<PilePort> ports = PortsOf(PileConnectors(w, nd, opt, true));
                if (ports.Count == 0) return P;
                PilePort q = EntryPort(ports, atA ? e.PA : e.PB);
                target = q.Tip + Side(q.Out) * (lat * 0.02);
                arrive = -q.Out;
                straight = 0.22;
            }
            else if (nd.Type == NodeType.Terminal)
            {
                V2 o = new V2(nd.Out.X, nd.Out.Z).Norm();
                target = nd.Pos + Side(o) * (lat * 0.03);
                arrive = o;
                straight = 0.6;
            }
            else return P;
            return CordLayer.Approach(w, P, !atA, target, arrive, straight);
        }

        /// <summary>The art inset (cells) on the footprint side a cord enters through.</summary>
        public static double ArtInset(MachineInfo m, V2 into)
        {
            if (into.X > 0.5) return m.InsetW;
            if (into.X < -0.5) return m.InsetE;
            if (into.Z > 0.5) return m.InsetS;
            return m.InsetN;
        }

        /// <summary>Owner round 2 (2026-10-04, station 4: "connectors not properly meeting the lightbulbs ... just go to the
        /// centroid of a building and be beneath them on the drawstack"): every cord into a machine runs on under its art to
        /// the footprint CENTROID, the last <see cref="CentroidApproach"/> cell straight along the way in (so the plug sits
        /// square at the end). The cord is printed at Conduits altitude, below every building, so the art hides the run and
        /// no art inset or misalignment can show. Points are inside the machine's own footprint by design.</summary>
        public const double CentroidApproach = 0.2;

        public static V2 Centroid(MachineInfo m) => new V2(m.X0 + m.W / 2.0, m.Z0 + m.H / 2.0);

        /// <summary>Where a machine's cord ends: its wall cell's centre for a wall-mounted device (round 4), else the centroid.</summary>
        public static V2 Home(MachineInfo m) => m.HasHome ? new V2(m.HomeX + 0.5, m.HomeZ + 0.5) : Centroid(m);

        private static List<V2> IntoArt(List<V2> P, bool atStart, MachineInfo m)
        {
            if (P.Count < 2) return P;
            V2 tip = atStart ? P[0] : P[P.Count - 1];
            V2 into = IntoMachine(m, tip);
            V2 c = Centroid(m), pre = c - into * CentroidApproach;
            var ext = new List<V2>();
            double d1 = V2.Dist(tip, pre);
            int k1 = Math.Max(1, (int)Math.Ceiling(d1 / 0.05));
            for (int i = 1; i <= k1; i++) ext.Add(tip + (pre - tip) * (i / (double)k1));
            for (double d = 0.05; d < CentroidApproach - 0.02; d += 0.05) ext.Add(pre + into * d);
            ext.Add(c);
            if (m.HasHome)
            {
                // on from the device's own cell straight into its wall, ending under the wall's centre
                V2 h = Home(m);
                double d2 = V2.Dist(c, h);
                int k2 = Math.Max(1, (int)Math.Ceiling(d2 / 0.05));
                for (int i = 1; i <= k2; i++) ext.Add(c + (h - c) * (i / (double)k2));
            }
            var o = new List<V2>(P);
            if (atStart) { ext.Reverse(); o.InsertRange(0, ext); }
            else o.AddRange(ext);
            return o;
        }

        public const double PastFaceDepth = 0.03;

        private static List<V2> PastFace(List<V2> P, bool atStart, CordNode nd)
        {
            if (P.Count < 2 || !(nd.Type == NodeType.StubWall || nd.Type == NodeType.StubRock) || nd.Into.Len < 0.5) return P;
            V2 tip = atStart ? P[0] : P[P.Count - 1];
            V2 to = nd.Face + nd.Into * PastFaceDepth;
            double along = (to.X - tip.X) * nd.Into.X + (to.Z - tip.Z) * nd.Into.Z;
            if (along <= 0.005) return P;
            var o = new List<V2>(P);
            int k = Math.Max(1, (int)Math.Ceiling(along / 0.04));
            var ext = new List<V2>();
            for (int i = 1; i <= k; i++) ext.Add(tip + nd.Into * (along * i / k));
            if (atStart) { ext.Reverse(); o.InsertRange(0, ext); } else o.AddRange(ext);
            return o;
        }

        /// <summary>Points from one end of P whose arc length stays within len (at least 3), never more than half the strand.</summary>
        public static int TailCount(List<V2> P, bool atStart, double len)
        {
            int n = P.Count;
            if (n < 6) return 0;
            double acc = 0;
            int c = 1;
            for (int k = 1; k < n / 2; k++)
            {
                int i = atStart ? k : n - 1 - k, j = atStart ? k - 1 : n - k;
                acc += V2.Dist(P[i], P[j]);
                if (acc > len) break;
                c++;
            }
            return c >= 3 ? c : 0;
        }

        private static double EndAngle(List<V2> P, bool atStart)
        {
            V2 a, b;
            if (P.Count < 2) return 0;
            if (atStart) { a = P[Math.Min(3, P.Count - 1)]; b = P[0]; }
            else { a = P[Math.Max(0, P.Count - 4)]; b = P[P.Count - 1]; }
            V2 d = b - a;
            return Math.Atan2(d.Z, d.X);
        }

        private static void EndDecor(CordWorld w, CordGraph g, VId v, CordNode nd, LaidPiece piece, bool atStart, BuildOptions opt,
                                     Func<Cell, bool> isLive)
        {
            if (piece.Strands.Count == 0) return;
            List<V2> first = piece.Strands[0].Pts;
            V2 tip = atStart ? first[0] : first[first.Count - 1];
            if (nd.IsMachine)
            {
                // one plug per end, at the footprint centroid where every strand converges (round 2), its head pointing
                // INTO the machine along the cord's last straight run; drawn under the building like the cord
                V2 a = atStart ? first[Math.Min(first.Count - 1, 1)] : first[Math.Max(0, first.Count - 2)];
                V2 into = Snap4(tip - a);
                piece.Decals.Add(new CordDecal(DecalKind.Plug, tip - into * (PlugScale * 0.25), Math.Atan2(into.Z, into.X), PlugScale));
            }
            else if (nd.Type == NodeType.Tangle && opt.PileFor(nd.Cell) == PileArt.Strips)
            {
                // round 5: a cord entering a strip pile plugs into its socket like the pile's own cables
                foreach (CordStrand s in piece.Strands)
                {
                    V2 t = atStart ? s.Pts[0] : s.Pts[s.Pts.Count - 1];
                    V2 a = atStart ? s.Pts[Math.Min(s.Pts.Count - 1, 1)] : s.Pts[Math.Max(0, s.Pts.Count - 2)];
                    V2 into = (t - a).Norm();
                    piece.Decals.Add(new CordDecal(DecalKind.Plug, t, Math.Atan2(into.Z, into.X), PilePlugScale));
                }
            }
            else if (nd.Type == NodeType.Terminal)
            {
                bool liveEnd = isLive(nd.Cell);
                foreach (CordStrand s in piece.Strands)
                {
                    V2 t = atStart ? s.Pts[0] : s.Pts[s.Pts.Count - 1];
                    var fd = new CordDecal(liveEnd ? DecalKind.FrayLive : DecalKind.FrayDead, t, EndAngle(s.Pts, atStart), 0.5);
                    if (liveEnd && !s.OverFace)
                    {
                        int cnt = TailCount(s.Pts, atStart, CordMotion.WhipLen);
                        if (atStart) s.WhipA = cnt; else s.WhipB = cnt;
                        fd.OnWhip = cnt > 0;
                    }
                    piece.Decals.Add(fd);
                }
                piece.Ends.Add(new CordEnd { Tip = tip, Dir = new V2(nd.Out.X, nd.Out.Z), NetCell = nd.Cell, Wall = false });
            }
            else if (nd.IsStub)
            {
                double ang = Math.Atan2(nd.Into.Z, nd.Into.X);
                V2 hole = nd.Face + nd.Into * 0.04;
                // round 4 (owner 2026-10-04: "They should look mounted ON the wall"): the plate / hole is drawn INSIDE the wall
                // cell, on the face it belongs to, cropped to the plate (WallMount): the visible south face shows it whole in
                // its band; an edge-on side face or the hidden north face shows a thin strip. Nothing lands on the open floor.
                if (nd.Type == NodeType.StubWall || nd.Type == NodeType.StubRock)
                {
                    CordDecal plate = WallMount.EntryDecal(nd.Type == NodeType.StubWall ? DecalKind.StubWall : DecalKind.StubRock, nd.Face, nd.Into);
                    piece.Decals.Add(plate);
                    hole = WallMount.Socket(plate);
                }
                else if (nd.Type == NodeType.StubDevice && opt.PileFor(nd.Cell) == PileArt.Strips)
                {
                    // the strip's LEDs read the net (phase 1b B6): lit when live, dark when not
                    piece.Decals.Add(new CordDecal(isLive(nd.Cell) ? DecalKind.PowerStrip : DecalKind.PowerStripDark, nd.Face - nd.Into * 0.2, ang + Math.PI / 2, 0.8));
                    piece.LiveKeys.Add(nd.Cell);
                }
                else if (nd.Type == NodeType.StubDevice)
                    // no strips outside the modern look (B1/B15): the cord ends in a small junction box, an arm along it
                    piece.Decals.Add(new CordDecal(DecalKind.JunctionTin, nd.Face - nd.Into * 0.2, ang, 0.6));
                if (nd.WallTerminal)
                {
                    var tail = WallMount.LooseWire(hole, nd.Face, nd.Into);
                    var sw = new double[tail.Count];
                    for (int k = 0; k < sw.Length; k++) sw[k] = Math.Pow(k / (double)(sw.Length - 1), 1.3);
                    piece.Strands.Add(new CordStrand { Pts = tail, OverFace = true, S0 = 0.3, Lifted = true, SwayW = sw });
                    V2 tt = tail[tail.Count - 1];
                    piece.Decals.Add(new CordDecal(isLive(nd.Cell) ? DecalKind.FrayLive : DecalKind.FrayDead, tt, -Math.PI / 2, 0.5));
                    piece.Ends.Add(new CordEnd { Tip = tt, Dir = new V2(0, -1), NetCell = nd.Cell, Wall = true });
                }
            }
        }

        /// <summary>A place a pile cable plugs in: the point its end lands on and the direction it leaves in.</summary>
        public struct PilePort
        {
            public V2 Tip, Out;
            public int Connector;
        }

        // PowerStrip art (64x32, drawn 0.9 x 0.45): four sockets along its long axis. PROVISIONAL, read off the PNG.
        public static readonly double[] StripSockets = { -0.22, -0.08, 0.06, 0.20 };
        public const double StripScale = 0.9, PilePlugScale = 0.42;

        /// <summary>The ports of every connector decal in a pile (junction arms, strip sockets), in decal order.</summary>
        public static List<PilePort> PortsOf(List<CordDecal> ds)
        {
            var ports = new List<PilePort>();
            for (int i = 0; i < ds.Count; i++)
            {
                CordDecal d = ds[i];
                if (d.Kind == DecalKind.JunctionTin || d.Kind == DecalKind.JunctionTape)
                {
                    bool tape = d.Kind == DecalKind.JunctionTape;
                    V2 jp = d.Pos + CordAudit.Rot(new V2(0, tape ? TapeAnchorZ * d.Scale : 0), d.Angle);
                    double[] arms = tape ? new[] { 0, Math.PI, -Math.PI / 2 } : new[] { 0, Math.PI / 2, Math.PI, -Math.PI / 2 };
                    foreach (double a in arms)
                    {
                        V2 o = CordAudit.Dir(a + d.Angle);
                        ports.Add(new PilePort { Tip = jp + o * (ArmTuck * d.Scale), Out = o, Connector = i });
                    }
                }
                else if (d.Kind == DecalKind.PowerStrip || d.Kind == DecalKind.PowerStripDark)
                {
                    V2 along = CordAudit.Dir(d.Angle), side = along.Perp;
                    for (int k = 0; k < StripSockets.Length; k++)
                    {
                        V2 o = k % 2 == 0 ? side : -side;
                        // the plug's head face sits on the socket; the cable leaves the plug's tail
                        V2 socket = d.Pos + along * (StripSockets[k] * d.Scale) + o * (0.1 * d.Scale);
                        ports.Add(new PilePort { Tip = socket + o * (0.46 * PilePlugScale), Out = o, Connector = i });
                    }
                }
            }
            return ports;
        }

        /// <summary>Pile connector box scale (round 5: thicker boxes over thinner wires) and the jitter that breaks the grid
        /// (owner 2026-10-04: "an unwelcome grid-like nature to the joining boxes sitting on the pile. Should be more randomly
        /// aligned"): each box is moved up to <see cref="PileJitter"/> off its cell centre, turned to any angle and scaled
        /// within <see cref="PileScaleLo"/>..<see cref="PileScaleHi"/> of <see cref="PileJunctionScale"/>.</summary>
        public const double PileJunctionScale = 1.05, PileJitter = 0.32, PileScaleLo = 0.82, PileScaleHi = 1.12;

        /// <summary>The connectors (junction boxes or strips) of a pile, deterministic from the seed and the pile's cells. Shared
        /// by <see cref="TanglePiece"/> and the cords that enter the pile (they plug into one of these ports, round 5).</summary>
        public static List<CordDecal> PileConnectors(CordWorld w, CordNode nd, BuildOptions opt, bool lit)
        {
            List<Cell> comp = nd.Cells;
            bool strips = opt.PileFor(nd.Cell) == PileArt.Strips;
            CordRng rc = CordRng.Of(opt.Seed, "pilecon", nd.Cell.X, nd.Cell.Z);
            var cells = new List<Cell>(comp);
            for (int i = cells.Count - 1; i > 0; i--) { int j = rc.Int(0, i); Cell t = cells[i]; cells[i] = cells[j]; cells[j] = t; }
            int want = strips ? Math.Max(1, 1 + comp.Count / 7) : Math.Max(3, 1 + comp.Count / 2);
            var cons = new List<CordDecal>();
            foreach (Cell c in cells)
            {
                if (cons.Count >= want) break;
                // irregular, never a grid: off-centre, any angle, a little bigger or smaller (round 5)
                V2 at = c.Centre + new V2(rc.Range(-PileJitter, PileJitter), rc.Range(-PileJitter, PileJitter));
                double ang = rc.Range(0, 2 * Math.PI), sc = rc.Range(PileScaleLo, PileScaleHi);
                CordDecal d;
                if (strips) d = new CordDecal(lit ? DecalKind.PowerStrip : DecalKind.PowerStripDark, at, ang, StripScale * sc);
                else d = new CordDecal(rc.Chance(0.5) ? DecalKind.JunctionTin : DecalKind.JunctionTape, at, ang, PileJunctionScale * sc);
                var one = new List<CordDecal> { d };
                if (PortsOf(one).Any(q => !w.IsWalkable(q.Tip.Floor))) continue;
                // keep boxes apart: a box whose centre lands within 0.45 of another reads as a stack, not a scatter
                if (cons.Any(o => V2.Dist(o.Pos, at) < 0.45)) continue;
                cons.Add(d);
            }
            return cons;
        }

        /// <summary>The pile port a cord ENTERING the pile plugs into (round 5, station 1: "the cable entering the mass does not
        /// join with the rest"): the port whose lead-out point (tip + out x 0.22) is nearest the cord's arrival point.</summary>
        public static PilePort EntryPort(List<PilePort> ports, V2 from)
        {
            PilePort best = ports[0];
            double bd = double.MaxValue;
            foreach (PilePort q in ports)
            {
                double d = V2.Dist(q.Tip + q.Out * 0.22, from);
                if (d < bd) { bd = d; best = q; }
            }
            return best;
        }

        /// <summary>
        /// A pile (owner review 2026-10-04 B2/B13): a mass of cables PLUGGED INTO each other. Every cable of the heap
        /// starts and ends on a connector's port, so no connector lies unused and no cable end lies loose. Star Wars,
        /// Jawa and Cybertek piles use many + and T junction boxes (the praised T junction art); the modern
        /// extension-cord pile uses power strips with a plug in their sockets.
        /// </summary>
        private static LaidPiece TanglePiece(CordWorld w, CordNode nd, BuildOptions opt, Func<Cell, bool> isLive)
        {
            var p = new LaidPiece { Key = "tangle:" + nd.Cell, Owner = nd.Cell };
            List<Cell> comp = nd.Cells;
            bool lit = isLive(nd.Cell);
            p.LiveKeys.Add(nd.Cell);
            bool strips = opt.PileFor(nd.Cell) == PileArt.Strips;
            List<CordDecal> cons = PileConnectors(w, nd, opt, lit);
            List<PilePort> ports = PortsOf(cons);
            // ---- cables: each runs port to port; cable i pairs port i with the port half the list away (another connector),
            // so the first ports/2 cables already fill every port: no socket or arm is left empty
            int n = Math.Min(24, Math.Max(Math.Min(14, 4 + comp.Count / 3), (ports.Count + 1) / 2));
            var used = new HashSet<int>();
            for (int i = 0; i < n && ports.Count >= 2; i++)
            {
                CordRng r = CordRng.Of(opt.Seed, "tangle", nd.Cell.X, nd.Cell.Z, i);
                int a = i % ports.Count, b = (i + ports.Count / 2) % ports.Count;
                for (int k = 0; k < ports.Count && cons.Count > 1 && ports[b].Connector == ports[a].Connector; k++) b = (b + 1) % ports.Count;
                if (a == b) continue;
                PilePort pa = ports[a], pb = ports[b];
                var stops = new List<V2> { pa.Tip, pa.Tip + pa.Out * 0.22 };
                int ns = r.Int(2, 4);
                for (int k = 0; k < ns; k++)
                    stops.Add(comp[r.Int(0, comp.Count - 1)].Centre + new V2(r.Range(-0.3, 0.3), r.Range(-0.3, 0.3)));
                stops.Add(pb.Tip + pb.Out * 0.22);
                stops.Add(pb.Tip);
                List<V2> P = Geo.Resample(Geo.Catmull(stops, 10), 0.05);
                int heaps = r.Int(1, 2);
                for (int k = 0; k < heaps && P.Count > 24; k++)
                {
                    int j = r.Int(P.Count / 3, 2 * P.Count / 3);
                    var win = P.GetRange(Math.Max(0, j - 2), Math.Min(P.Count, j + 3) - Math.Max(0, j - 2));
                    Geo.TanNorm(win, win.Count / 2, out V2 t, out V2 nn);
                    var hp = CordLayer.Heap(P[j], t, nn, r.Range(0.2, 0.4), r.Sign(), r);
                    var o = new List<V2>(P.GetRange(0, j));
                    o.AddRange(hp);
                    o.AddRange(P.GetRange(j + 1, P.Count - j - 1));
                    P = o;
                }
                P = Geo.Resample(P, 0.05);
                CordLayer.Smooth(w, P, 3);
                P[0] = pa.Tip; P[P.Count - 1] = pb.Tip;
                if (!P.All(q => w.IsWalkable(q.Floor))) continue;
                p.Strands.Add(new CordStrand { Pts = P, S0 = r.Value() });
                used.Add(a); used.Add(b);
            }
            // ---- connectors are printed over the cables; a strip gets a plug in every socket a cable uses
            p.Decals.AddRange(cons);
            if (strips)
                foreach (int k in used.OrderBy(x => x))
                {
                    PilePort q = ports[k];
                    p.Decals.Add(new CordDecal(DecalKind.Plug, q.Tip, Math.Atan2(-q.Out.Z, -q.Out.X), PilePlugScale));
                }
            return p;
        }
    }
}
