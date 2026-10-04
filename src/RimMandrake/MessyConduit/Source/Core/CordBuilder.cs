// Messy Conduit core: Verse-free (see CordMath.cs header).
// Orchestration of nodal.build_nodal for phase 1a: reduce -> plan -> lay, cached per edge.
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace RimMandrake.MessyConduit.Core
{
    public enum DecalKind { Plug, JunctionTape, JunctionTin, StubWall, StubRock, PowerStrip, FrayDead, FrayLive, PowerStripDark }

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
        public CordDecal(DecalKind k, V2 p, double a, double s) { Kind = k; Pos = p; Angle = a; Scale = s; OnWhip = false; Squash = 0; }
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
                    full.Append(g.Nodes[v].Type).Append(',');
                foreach (VId v in new[] { e.A, e.B })
                    if (g.Nodes[v].Type == NodeType.Terminal || g.Nodes[v].WallTerminal || g.Nodes[v].Type == NodeType.StubDevice) full.Append(isLive(g.Nodes[v].Cell) ? 'L' : 'D');
                full.Append('#').Append(opt.Lay.Fingerprint()).Append('#').Append(opt.Pile);
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
                    h = (h ^ (ulong)(w.IsWalkable(c) ? 1 : 2) ^ (w.IsDoor(c) ? 4UL : 0UL)) * 1099511628211UL;
                }
            return h;
        }

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
                P = AttachEnd(w, g, e, true, P, i, n);
                P = AttachEnd(w, g, e, false, P, i, n);
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
        // Junction_Tin is a centred 4-arm cross; StubRock's hole is centred +0.11 along X.
        public const double JunctionScale = 1.0, TapeAnchorZ = 0.152, ArmTuck = 0.40;
        public const double PlugScale = 0.55, PlugInset = 0.05, StubScale = 0.7, RockHoleX = 0.11;
        /// <summary>B4: the rock hole drawn foreshortened along the cord (art X) as if cut into an angled rock face. PROVISIONAL.</summary>
        public const double RockSquash = 0.6;
        /// <summary>Round 3 (owner 2026-10-04: wall connectors "need to be angled 'down' more so they face out, not up towards
        /// nadir"): the wall plate sits on the wall's vertical face, so it is drawn foreshortened along the cord (art X) like
        /// the rock hole, a narrow plate seen edge-on from above rather than a square looking at the sky. PROVISIONAL.</summary>
        public const double WallSquash = 0.5;

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
        private static List<V2> AttachEnd(CordWorld w, CordGraph g, CordEdge e, bool atA, List<V2> P, int i, int n)
        {
            VId v = atA ? e.A : e.B;
            CordNode nd = g.Nodes[v];
            double lat = n == 1 ? 0 : (i - (n - 1) / 2.0);
            V2 target, arrive;
            double straight = 0.15;
            if (nd.Type == NodeType.Junction && !nd.IsBlob && v.IsCellish)
            {
                V2 a = ArmDir(g, e, atA);
                target = nd.Pos + a * ArmTuck + Side(a) * (lat * 0.03);
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
            var o = new List<V2>(P);
            if (atStart) { ext.Reverse(); o.InsertRange(0, ext); }
            else o.AddRange(ext);
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
                // the real art's cord runs along its +X into the plate/hole, so +X points INTO the face;
                // the plate (centred on the canvas) or the hole (+0.11 canvas) sits on the face line
                if (nd.Type == NodeType.StubWall)
                    piece.Decals.Add(new CordDecal(DecalKind.StubWall, nd.Face + nd.Into * 0.02, ang, StubScale) { Squash = WallSquash });
                else if (nd.Type == NodeType.StubRock)
                    piece.Decals.Add(new CordDecal(DecalKind.StubRock, nd.Face + nd.Into * (0.06 - RockHoleX * StubScale * RockSquash), ang, StubScale) { Squash = RockSquash });
                else if (nd.Type == NodeType.StubDevice && opt.Pile == PileArt.Strips)
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
                    var tail = CordLayer.HangingTail(hole, nd.Into);
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
            bool strips = opt.Pile == PileArt.Strips;
            // ---- connectors on distinct cells of the pile
            CordRng rc = CordRng.Of(opt.Seed, "pilecon", nd.Cell.X, nd.Cell.Z);
            var cells = new List<Cell>(comp);
            for (int i = cells.Count - 1; i > 0; i--) { int j = rc.Int(0, i); Cell t = cells[i]; cells[i] = cells[j]; cells[j] = t; }
            int want = strips ? Math.Max(1, 1 + comp.Count / 7) : Math.Max(3, 1 + comp.Count / 2);
            var cons = new List<CordDecal>();
            foreach (Cell c in cells)
            {
                if (cons.Count >= want) break;
                V2 at = c.Centre + new V2(rc.Range(-0.1, 0.1), rc.Range(-0.1, 0.1));
                CordDecal d;
                if (strips) d = new CordDecal(lit ? DecalKind.PowerStrip : DecalKind.PowerStripDark, at, rc.Int(0, 1) * Math.PI / 2 + rc.Range(-0.25, 0.25), StripScale);
                else d = new CordDecal(rc.Chance(0.5) ? DecalKind.JunctionTin : DecalKind.JunctionTape, at, rc.Int(0, 3) * Math.PI / 2, 0.8);
                var one = new List<CordDecal> { d };
                if (PortsOf(one).Any(q => !w.IsWalkable(q.Tip.Floor))) continue;
                cons.Add(d);
            }
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
