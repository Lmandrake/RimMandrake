// Gimme Some Slack core: Verse-free (see CordMath.cs header).
// RIMMANDRAKE_BIND_SLACK_STUB_ANGLE_RULE_FOURTH_ASK (owner 2026-11-16, walking the review map): "The position-slope rule should be hard wired
// into the mod and be part of its acceptance checks." and "wires should join at the location AND the angle/slope to match their next piece ...
// It should be true for every art piece that has stubs/connectors at particular angles that need to be matched." (asked before 2026-10-23,
// 2026-10-24 for hoses and 2026-11-09 for this mod). Two halves, one reading, shared by the offline SelfTest (SelfTest/StubJoinChecks.cs) and the
// live probe ("joins:"):
//   StubArt   the per-art data: every texture the mod draws, classed by how a cord joins it, and for each stubbed piece where its stubs end and
//             which way they point, in the art's own frame. selftest_gss_stub_art_census.py fails on a texture missing from the census.
//   Joins     every stub of every drawn piece in a scene: each cord on it passes the stub's tip (PosMax) heading along the stub (SlopeMaxDeg),
//             and no stub is drawn bare while a cord is attached elsewhere on its piece. Stubless art (wall bracket, pole top, lamp base) is
//             never read here: it joins at position only (owner 2026-11-16, "They can just connect at position as shown.").
//   LiveEnds  the whipping live end continues its cord: same point, same direction at the join on every frame of its motion (the bent
//             tail leaves the joint along the laid cord's own heading there), no bend tighter
//             than the cord's own minimum (owner 2026-11-16, "a "live wire wiggling around" has been grafted onto the end of a terminal wire
//             without the slope/angle requirement, so it generates a tight pinched effect that is nonphysical.").
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.Core
{
    internal static class StubArt
    {
        internal enum Join { Stubs, PositionOnly, LooseEnd, Cord, Hidden }

        /// <summary>Every texture basename under Textures/, how a cord joins it, and where that was read.</summary>
        internal static readonly (string Art, Join How, string Why)[] Census =
        {
            ("Junction_X", Join.Stubs, "four arms, tips 55.5 px of 128 from the centre (selftest_gss_junction_necks.py SLOTS)"),
            ("Junction_Tin", Join.Stubs, "the + box's file name (CordMaterials maps Junction_X to it)"),
            ("Junction_T", Join.Stubs, "three arms, tips 55.5 px of 128 from the meeting point"),
            ("Junction_X_p4", Join.Stubs, "the device box: the + box with only its -X arm (CordDecal.Ports, make_switch_masks.py)"),
            ("Junction_Tin_p4", Join.Stubs, "as Junction_X_p4"),
            ("Junction_Tape", Join.Stubs, "the T box's file name (CordMaterials maps Junction_T to it)"),
            ("PowerSwitch", Join.Stubs, "a stub mid-side on each of four sides, tips 54-58 px of 64 (CordEndAudit.SwitchStubTip)"),
            ("PowerSwitch_Off", Join.Stubs, "as PowerSwitch"),
            ("PowerSwitch_p1", Join.Stubs, "as PowerSwitch, only the stubs in mask 1 (E1 N2 W4 S8): SwitchStubs"),
            ("PowerSwitch_p2", Join.Stubs, "as PowerSwitch, only the stubs in mask 2 (E1 N2 W4 S8): SwitchStubs"),
            ("PowerSwitch_p3", Join.Stubs, "as PowerSwitch, only the stubs in mask 3 (E1 N2 W4 S8): SwitchStubs"),
            ("PowerSwitch_p4", Join.Stubs, "as PowerSwitch, only the stubs in mask 4 (E1 N2 W4 S8): SwitchStubs"),
            ("PowerSwitch_p5", Join.Stubs, "as PowerSwitch, only the stubs in mask 5 (E1 N2 W4 S8): SwitchStubs"),
            ("PowerSwitch_p6", Join.Stubs, "as PowerSwitch, only the stubs in mask 6 (E1 N2 W4 S8): SwitchStubs"),
            ("PowerSwitch_p7", Join.Stubs, "as PowerSwitch, only the stubs in mask 7 (E1 N2 W4 S8): SwitchStubs"),
            ("PowerSwitch_p8", Join.Stubs, "as PowerSwitch, only the stubs in mask 8 (E1 N2 W4 S8): SwitchStubs"),
            ("PowerSwitch_p9", Join.Stubs, "as PowerSwitch, only the stubs in mask 9 (E1 N2 W4 S8): SwitchStubs"),
            ("PowerSwitch_p10", Join.Stubs, "as PowerSwitch, only the stubs in mask 10 (E1 N2 W4 S8): SwitchStubs"),
            ("PowerSwitch_p11", Join.Stubs, "as PowerSwitch, only the stubs in mask 11 (E1 N2 W4 S8): SwitchStubs"),
            ("PowerSwitch_p12", Join.Stubs, "as PowerSwitch, only the stubs in mask 12 (E1 N2 W4 S8): SwitchStubs"),
            ("PowerSwitch_p13", Join.Stubs, "as PowerSwitch, only the stubs in mask 13 (E1 N2 W4 S8): SwitchStubs"),
            ("PowerSwitch_p14", Join.Stubs, "as PowerSwitch, only the stubs in mask 14 (E1 N2 W4 S8): SwitchStubs"),
            ("PowerSwitch_Off_p1", Join.Stubs, "as PowerSwitch, only the stubs in mask 1 (E1 N2 W4 S8): SwitchStubs"),
            ("PowerSwitch_Off_p2", Join.Stubs, "as PowerSwitch, only the stubs in mask 2 (E1 N2 W4 S8): SwitchStubs"),
            ("PowerSwitch_Off_p3", Join.Stubs, "as PowerSwitch, only the stubs in mask 3 (E1 N2 W4 S8): SwitchStubs"),
            ("PowerSwitch_Off_p4", Join.Stubs, "as PowerSwitch, only the stubs in mask 4 (E1 N2 W4 S8): SwitchStubs"),
            ("PowerSwitch_Off_p5", Join.Stubs, "as PowerSwitch, only the stubs in mask 5 (E1 N2 W4 S8): SwitchStubs"),
            ("PowerSwitch_Off_p6", Join.Stubs, "as PowerSwitch, only the stubs in mask 6 (E1 N2 W4 S8): SwitchStubs"),
            ("PowerSwitch_Off_p7", Join.Stubs, "as PowerSwitch, only the stubs in mask 7 (E1 N2 W4 S8): SwitchStubs"),
            ("PowerSwitch_Off_p8", Join.Stubs, "as PowerSwitch, only the stubs in mask 8 (E1 N2 W4 S8): SwitchStubs"),
            ("PowerSwitch_Off_p9", Join.Stubs, "as PowerSwitch, only the stubs in mask 9 (E1 N2 W4 S8): SwitchStubs"),
            ("PowerSwitch_Off_p10", Join.Stubs, "as PowerSwitch, only the stubs in mask 10 (E1 N2 W4 S8): SwitchStubs"),
            ("PowerSwitch_Off_p11", Join.Stubs, "as PowerSwitch, only the stubs in mask 11 (E1 N2 W4 S8): SwitchStubs"),
            ("PowerSwitch_Off_p12", Join.Stubs, "as PowerSwitch, only the stubs in mask 12 (E1 N2 W4 S8): SwitchStubs"),
            ("PowerSwitch_Off_p13", Join.Stubs, "as PowerSwitch, only the stubs in mask 13 (E1 N2 W4 S8): SwitchStubs"),
            ("PowerSwitch_Off_p14", Join.Stubs, "as PowerSwitch, only the stubs in mask 14 (E1 N2 W4 S8): SwitchStubs"),
            ("Plug", Join.Stubs, "the strain-relief boot, along the plug's axis, CordBuilder.PlugBootU per look"),
            ("PlugTop", Join.Stubs, "the boot of a plug seen from above, PlugTopReach out of its socket"),
            ("PowerStrip", Join.Stubs, "its own lead out of the end cap (StripLeadX, StripLeadZ); the sockets take PlugTops"),
            ("PowerStrip_Off", Join.Stubs, "as PowerStrip"),
            ("StubWall", Join.Stubs, "the wall plate's grommet: the cord leaves square to the face"),
            ("StubRock", Join.Stubs, "the rock hole: the cord leaves square to the face"),
            ("WallOutlet", Join.Stubs, "the south-face outlet carries the plug, its boot on the face line"),
            ("WallOutlet_Plugged", Join.Stubs, "as WallOutlet"),
            ("WallBracket", Join.PositionOnly, "stubless (owner 2026-11-16, station 26)"),
            ("WallBracket_east", Join.PositionOnly, "stubless"),
            ("WallBracket_north", Join.PositionOnly, "stubless"),
            ("WallBracket_south", Join.PositionOnly, "stubless"),
            ("AerialMast", Join.PositionOnly, "pole: the wire joins at its top"),
            ("AerialMastTop", Join.PositionOnly, "pole top (owner 2026-11-16, station 26)"),
            ("AerialLampMast", Join.PositionOnly, "pole"),
            ("AerialLampMastTop", Join.PositionOnly, "pole top"),
            ("PoleTopDown", Join.PositionOnly, "pole top seen from above"),
            ("Insulator", Join.PositionOnly, "the line rests on top of it (owner reference photo 2026-11-08)"),
            ("StandingLamp", Join.PositionOnly, "lamp base (owner 2026-11-16, station 26)"),
            ("TapClamp", Join.PositionOnly, "jaws grip the overhead wire: no cord stub drawn"),
            ("EndFrayed_Live", Join.LooseEnd, "a loose end itself"),
            ("EndFrayed_Dead", Join.LooseEnd, "a loose end itself"),
            ("SparkGlow", Join.LooseEnd, "the live end's glow"),
            ("CableTie", Join.Cord, "a band around the cord"),
            ("Strand", Join.Cord, "cord"), ("StrandShadow", Join.Cord, "cord shadow"), ("SpanWire", Join.Cord, "overhead wire"),
            ("SpanShadow", Join.Cord, "overhead wire shadow"),
            ("Strand_BlackRubber", Join.Cord, "cord"), ("Strand_Blue", Join.Cord, "cord"), ("Strand_Brown", Join.Cord, "cord"),
            ("Strand_CoiledBlack", Join.Cord, "cord"), ("Strand_CorrugatedSteel", Join.Cord, "cord"), ("Strand_Green", Join.Cord, "cord"),
            ("Strand_Jawa", Join.Cord, "cord"), ("Strand_Orange", Join.Cord, "cord"), ("Strand_ScrapTaped", Join.Cord, "cord"),
            ("Strand_Yellow", Join.Cord, "cord"),
            ("ConduitTransparent", Join.Hidden, "the invisible conduit"),
        };

        /// <summary>The arm length of both junction boxes, art units (times the decal's Scale).</summary>
        internal const double BoxArm = 55.5 / 128.0;
        /// <summary>A plug seen from above: its boot, art units out of the socket along its axis.</summary>
        internal const double PlugTopBoot = CordBuilder.PlugTopReach / CordBuilder.PlugTopScale;

        /// <summary>One stub in the scene: its tip, the way a cord leaves it, the piece it belongs to.</summary>
        internal sealed class Stub
        {
            public string Piece, Kind;
            public V2 T, U;
            public int Fitting;
            /// <summary>The decal's index in its piece (a plug the builder seats), or -1.</summary>
            public int Decal = -1;
        }

        private static V2 Dir(double a) => new V2(Math.Cos(a), Math.Sin(a));

        /// <summary>Every stub of every drawn piece, from the decals and the power switches, through the table above.</summary>
        internal static List<Stub> Of(CordWorld w, List<LaidPiece> ps, BuildOptions opt)
        {
            var o = new List<Stub>();
            int fit = 0;
            foreach (LaidPiece p in ps) OfPiece(p, opt, o, ref fit);
            foreach (MachineInfo m in w.Machines.Where(m => m.SidePorts))
            {
                fit++;
                V2 c = new V2(m.X0 + 0.5, m.Z0 + 0.5);
                // the art drawn is the variant with only the stubs that carry a cord (SwitchStubs): only those stubs are on the map
                int drawn = SwitchStubs.Drawn(SwitchStubs.Mask(m, ps));
                for (int b = 0; b < 4; b++)
                    if ((drawn & (1 << b)) != 0)
                    {
                        V2 u = SwitchStubs.Dirs[b];
                        o.Add(new Stub { Kind = "switch", Piece = $"switch@({c.X:0.0},{c.Z:0.0})", T = c + u * CordEndAudit.SwitchStubTip, U = u, Fitting = fit });
                    }
            }
            return o;
        }

        /// <summary>The stubs of one piece's decals (the builder seats its cords on these: CordBuilder.SeatPlugTails).</summary>
        internal static void OfPiece(LaidPiece p, BuildOptions opt, List<Stub> o, ref int fit)
        {
            int di = -1;
            void Add(string kind, V2 at, V2 t, V2 u, int f) =>
                o.Add(new Stub { Kind = kind, Piece = $"{kind}@({at.X:0.0},{at.Z:0.0})", T = t, U = u.Norm(), Fitting = f, Decal = di });
                foreach (CordDecal d in p.Decals)
                {
                    di++;
                    V2 x = Dir(d.Angle), z = CordEndAudit.Rot(x, Math.PI / 2);
                    switch (d.Kind)
                    {
                        case DecalKind.JunctionTin:
                        {
                            string k = d.Scale == CordBuilder.DeviceBoxScale ? "device box" : "box X";
                            fit++;
                            for (int a = 0; a < 4; a++)
                            {
                                if (d.Ports != 0 && (d.Ports & (1 << a)) == 0) continue;   // an arm the art does not draw
                                V2 u = CordEndAudit.Rot(x, a * Math.PI / 2); Add(k, d.Pos, d.Pos + u * (BoxArm * d.Scale), u, fit);
                            }
                            break;
                        }
                        case DecalKind.JunctionTape:
                        {
                            V2 m = d.Pos + z * (CordBuilder.TapeAnchorZ * d.Scale);
                            fit++;
                            foreach (V2 u in new[] { x, -x, -z }) Add("box T", m, m + u * (BoxArm * d.Scale), u, fit);
                            break;
                        }
                        case DecalKind.Plug:
                        {
                            double boot = d.Scale == CordBuilder.WallPlugScale ? CordBuilder.ExtPlugBootU : (opt?.PlugBootFor(p.Owner) ?? CordBuilder.ExtPlugBootU);
                            Add(d.Scale == CordBuilder.WallPlugScale ? "wall plug" : "plug", d.Pos, d.Pos - x * (boot * d.Scale), -x, ++fit);
                            break;
                        }
                        case DecalKind.PlugTop:
                            Add("strip plug", d.Pos, d.Pos + x * (PlugTopBoot * d.Scale), x, ++fit);
                            break;
                        case DecalKind.PowerStrip:
                        case DecalKind.PowerStripDark:
                        {
                            // the art's lead leaves its +X end cap; which side the sockets face is not in the decal, so the lead's small
                            // across offset (StripLeadZ, 0.045 cell at JunctionStripScale) is left out: it is inside PosMax
                            fit++;
                            V2 tip = d.Pos + x * (CordBuilder.StripLeadX * d.Scale);
                            Add("strip lead", d.Pos, tip, x, fit);
                            break;
                        }
                        case DecalKind.StubWall:
                        case DecalKind.StubRock:
                            Add(d.Kind == DecalKind.StubWall ? "wall plate" : "rock hole", d.Pos, d.Pos - x * (d.Squash * d.Scale / 2 + WallMount.FaceMargin), -x, ++fit);
                            break;
                        case DecalKind.WallOutlet:
                            // on a side or the hidden north face the plug stands out of the outlet (its own Plug stub); on the south face the outlet
                            // art carries the plug, its boot on the face line
                            if (WallMount.FaceOf(x) == WallFaceKind.South)
                                Add("wall outlet", d.Pos, d.Pos - x * (d.Squash * d.Scale / 2 + WallMount.FaceMargin), -x, ++fit);
                            break;
                    }
                }
        }
    }

    /// <summary>The power switch's art paints a stub on each side; a stub with no cord is not drawn (owner 2026-11-16, holding file row 2,
    /// bar cords_join_stubs_on_position_and_slope). Which sides carry a cord is read off the laid cords (each cord ending in the switch's cell
    /// leaves it on one side); the game draws PowerSwitch[_Off]_p&lt;mask&gt; (art_source/switch_stub_masks_2026-11-16/make_switch_masks.py),
    /// the full art when no cord or every side has one.</summary>
    internal static class SwitchStubs
    {
        /// <summary>Bit b is the stub along Dirs[b]: E 1, N 2, W 4, S 8.</summary>
        internal static readonly V2[] Dirs = { new V2(1, 0), new V2(0, 1), new V2(-1, 0), new V2(0, -1) };
        public const int All = 15;

        /// <summary>The art's mask for the sides in use: none or all draws the full art.</summary>
        public static int Drawn(int used) => used == 0 ? All : used;

        /// <summary>The texture suffix for a drawn mask ("" for the full art).</summary>
        public static string Suffix(int drawn) => drawn == All || drawn == 0 ? "" : "_p" + drawn;

        /// <summary>The sides of switch <paramref name="m"/> a laid cord leaves by: walking each strand in from an end inside the switch's cell,
        /// the side it crosses the 0.3-cell ring on, snapped to the nearest axis.</summary>
        public static int Mask(MachineInfo m, IEnumerable<LaidPiece> ps)
        {
            Dictionary<Cell, int> all = Masks(new[] { m }, ps);
            return all.TryGetValue(new Cell(m.X0, m.Z0), out int k) ? k : 0;
        }

        /// <summary>The used sides of every 1x1 side-port machine (a power switch) in one pass over the strands, by the switch's cell.</summary>
        public static Dictionary<Cell, int> Masks(IEnumerable<MachineInfo> ms, IEnumerable<LaidPiece> ps)
        {
            var o = new Dictionary<Cell, int>();
            foreach (MachineInfo m in ms)
                if (m.SidePorts) o[new Cell(m.X0, m.Z0)] = 0;
            if (o.Count == 0) return o;
            foreach (LaidPiece p in ps)
                foreach (CordStrand s in p.Strands)
                {
                    if (s.OverFace || s.Lifted || s.Pts == null || s.Pts.Count < 2) continue;
                    int n = s.Pts.Count;
                    for (int end = 0; end < 2; end++)
                    {
                        V2 e = end == 0 ? s.Pts[0] : s.Pts[n - 1];
                        Cell cell = e.Floor;
                        if (!o.TryGetValue(cell, out int mask)) continue;
                        V2 c = new V2(cell.X + 0.5, cell.Z + 0.5);
                        V2 q = end == 0 ? s.Pts[n - 1] : s.Pts[0];
                        for (int k = 1; k < n; k++)
                        {
                            V2 a = end == 0 ? s.Pts[k] : s.Pts[n - 1 - k];
                            if (V2.Dist(a, c) >= 0.3) { q = a; break; }
                        }
                        V2 d = q - c;
                        if (d.Len < 1e-6) continue;
                        int b = Math.Abs(d.X) >= Math.Abs(d.Z) ? (d.X >= 0 ? 0 : 2) : (d.Z >= 0 ? 1 : 3);
                        o[cell] = mask | (1 << b);
                    }
                }
            return o;
        }
    }

    internal static class StubJoins
    {
        /// <summary>How far (cells) from a stub's tip a cord end may lie and still be read as that stub's cord.</summary>
        public const double Reach = 0.75;
        /// <summary>The cord's minimum bend radius, cells: CordShape's repair floor, the tightest bend the cord is ever laid at.</summary>
        public const double MinBendR = 0.10;

        internal sealed class JoinRead
        {
            public int Stubs, Taken, OffLine, OffSlope, Empty;
            public double WorstDeg, WorstPos;
            /// <summary>Per piece kind: stubs, cords taken, off line, off slope, bare stubs.</summary>
            public readonly SortedDictionary<string, int[]> ByKind = new SortedDictionary<string, int[]>(StringComparer.Ordinal);
            public readonly List<string> Bad = new List<string>();
            public void Add(JoinRead r)
            {
                Stubs += r.Stubs; Taken += r.Taken; OffLine += r.OffLine; OffSlope += r.OffSlope; Empty += r.Empty;
                WorstDeg = Math.Max(WorstDeg, r.WorstDeg); WorstPos = Math.Max(WorstPos, r.WorstPos);
                foreach (var kv in r.ByKind)
                {
                    if (!ByKind.TryGetValue(kv.Key, out int[] a)) ByKind[kv.Key] = a = new int[5];
                    for (int i = 0; i < 5; i++) a[i] += kv.Value[i];
                }
                Bad.AddRange(r.Bad);
            }
            public string Summary() => string.Join(", ", ByKind.Select(kv => $"{kv.Key}: {kv.Value[1]} cords on {kv.Value[0]} stubs, {kv.Value[2]} off line, {kv.Value[3]} off slope, {kv.Value[4]} bare"));
        }

        private static double Cross(V2 a, V2 b) => a.X * b.Z - a.Z * b.X;
        private static double Dot(V2 a, V2 b) => a.X * b.X + a.Z * b.Z;

        /// <summary>Walking a strand out from one end over at most <paramref name="arc"/> cells: the point nearest T, and the cord's heading there
        /// (the chord SlopeChord further on, away from the end).</summary>
        internal static bool Nearest(List<V2> P, bool fromStart, V2 T, double arc, out V2 q, out V2 head, out double dist)
        {
            int n = P.Count;
            V2 At(int k) => fromStart ? P[k] : P[n - 1 - k];
            q = At(0); head = default(V2); dist = V2.Dist(q, T);
            int seg = 0; double tq = 0, acc = 0;
            for (int k = 0; k + 1 < n && acc <= arc; k++)
            {
                V2 a = At(k), b = At(k + 1), ab = b - a;
                double l2 = Dot(ab, ab);
                double t = l2 < 1e-12 ? 0 : Math.Max(0, Math.Min(1, Dot(T - a, ab) / l2));
                V2 c = a + ab * t;
                double dd = V2.Dist(c, T);
                if (dd < dist) { dist = dd; q = c; seg = k; tq = t; }
                acc += Math.Sqrt(l2);
            }
            // heading: from q, SlopeChord further along
            double want = CordEndAudit.SlopeChord, run = 0;
            V2 prev = q;
            for (int k = seg + 1; k < n; k++)
            {
                V2 b = At(k);
                double s = V2.Dist(prev, b);
                if (run + s >= want) { V2 y = prev + (b - prev) * ((want - run) / Math.Max(s, 1e-9)); head = (y - q).Norm(); return true; }
                run += s; prev = b;
            }
            if (V2.Dist(prev, q) < 1e-6) return false;
            head = (prev - q).Norm();
            return true;
        }

        /// <summary>The rule at every stub in the scene.</summary>
        internal static JoinRead Joins(CordWorld w, List<LaidPiece> ps, BuildOptions opt, string scene, Func<V2, bool> keep = null)
        {
            var r = new JoinRead();
            List<StubArt.Stub> stubs = StubArt.Of(w, ps, opt).Where(s => keep == null || keep(s.T)).ToList();
            var strands = ps.SelectMany(p => p.Strands.Select(s => (p, s))).Where(x => !x.s.OverFace && !x.s.Lifted && x.s.Pts != null && x.s.Pts.Count > 1).ToList();
            var taken = new Dictionary<StubArt.Stub, int>();
            foreach (var (p, s) in strands)
                foreach (bool atStart in new[] { true, false })
                {
                    V2 e = atStart ? s.Pts[0] : s.Pts[s.Pts.Count - 1];
                    StubArt.Stub best = null; double bd = double.MaxValue; V2 bq = default(V2), bh = default(V2);
                    foreach (StubArt.Stub st in stubs)
                    {
                        if (V2.Dist(e, st.T) > Reach) continue;
                        // an end on a stub lies inside its piece, behind the tip: the far end of a short lead that leaves this stub (a box
                        // beside its own machine) lies out along it, and is its own stub's end
                        if (Dot(e - st.T, st.U) > 0.1) continue;
                        if (!Nearest(s.Pts, atStart, st.T, V2.Dist(e, st.T) + 0.5, out V2 q, out V2 h, out double dd)) continue;
                        // a tie (two stubs equally near: the + box's arms meet at its centre) goes to the stub the cord heads along
                        double score = dd - 0.001 * Dot(h, st.U);
                        if (score < bd) { bd = score; best = st; bq = q; bh = h; }
                    }
                    if (best == null || V2.Dist(bq, best.T) > 0.3) continue;   // this end belongs to no stub (a loose end, a lamp, a hole)
                    taken[best] = taken.TryGetValue(best, out int c0) ? c0 + 1 : 1;
                    double off = V2.Dist(bq, best.T);
                    double deg = Math.Acos(Math.Max(-1, Math.Min(1, Dot(bh, best.U)))) * 180 / Math.PI;
                    int[] a = Kind(r, best.Kind);
                    a[1]++; r.Taken++;
                    r.WorstDeg = Math.Max(r.WorstDeg, deg); r.WorstPos = Math.Max(r.WorstPos, off);
                    string at = $"{scene} {best.Piece} stub ({best.U.X:0.##},{best.U.Z:0.##}) cord {p.EndA}|{p.EndB}";
                    if (off > CordEndAudit.PosMax) { a[2]++; r.OffLine++; r.Bad.Add($"{at}: passes the stub's tip {off:0.00} cell off it"); }
                    else if (deg > CordEndAudit.SlopeMaxDeg) { a[3]++; r.OffSlope++; r.Bad.Add($"{at}: leaves the stub {deg:0} deg off its slope"); }
                }
            // a cord lying along a stub under it, its end nearer another piece (two boxes a cell apart share one short cord), also takes it
            foreach (StubArt.Stub st in stubs)
                if (!taken.ContainsKey(st) && strands.Any(x => x.s.Pts.Any(q => V2.Dist(q, st.T) < CordEndAudit.PosMax)))
                    taken[st] = 0;
            foreach (StubArt.Stub st in stubs)
            {
                int[] a = Kind(r, st.Kind);
                a[0]++; r.Stubs++;
                if (taken.ContainsKey(st)) continue;
                // bare: a stub with no cord while its piece has one elsewhere, or a one-stub fitting with no cord at all
                bool pieceUsed = stubs.Any(o => o.Fitting == st.Fitting && taken.ContainsKey(o));
                bool single = stubs.Count(o => o.Fitting == st.Fitting) == 1;
                if (pieceUsed || single) { a[4]++; r.Empty++; r.Bad.Add($"{scene} {st.Piece}: stub ({st.U.X:0.##},{st.U.Z:0.##}) drawn with no cord on it"); }
            }
            return r;
        }

        private static int[] Kind(JoinRead r, string k)
        {
            if (!r.ByKind.TryGetValue(k, out int[] a)) r.ByKind[k] = a = new int[5];
            return a;
        }

        // ------------------------------------------------------------------ the live end
        internal sealed class LiveRead
        {
            public int Tails, Frames, OffSlope, Pinched, Jumped;
            public double WorstDeg, MinR = double.MaxValue;
            public readonly List<string> Bad = new List<string>();
            public void Add(LiveRead o)
            {
                Tails += o.Tails; Frames += o.Frames; OffSlope += o.OffSlope; Pinched += o.Pinched; Jumped += o.Jumped;
                WorstDeg = Math.Max(WorstDeg, o.WorstDeg); MinR = Math.Min(MinR, o.MinR); Bad.AddRange(o.Bad);
            }
        }

        /// <summary>The tightest bend radius (cells) along a polyline, read on a resample at 0.02 over chords 0.06 each side.</summary>
        internal static double MinRadius(IList<V2> pts)
        {
            List<V2> q = Geo.Resample(pts.ToList(), 0.02);
            double best = double.MaxValue;
            const int k = 3;
            for (int i = k; i + k < q.Count; i++)
            {
                V2 a = q[i - k], b = q[i], c = q[i + k];
                double area2 = Math.Abs(Cross(b - a, c - a));
                if (area2 < 1e-12) continue;
                best = Math.Min(best, V2.Dist(a, b) * V2.Dist(b, c) * V2.Dist(c, a) / (2 * area2));
            }
            return best;
        }

        /// <summary>Every whipping tail, frame by frame: the cord's last <paramref name="lead"/> cells before the joint plus the bent tail. The tail is
        /// the same list the game's component bends (tail[0] = the joint), bent by the same function at the full swing (the game only ever narrows
        /// it beside a wall), so a pose that is bad here is bad there.</summary>
        internal static LiveRead LiveEnds(List<LaidPiece> ps, string scene, int frames = 90, double fps = 30, double lead = 0.4, Func<V2, bool> keep = null, ulong salt = 0)
        {
            var r = new LiveRead();
            int idx = 0;
            foreach (LaidPiece p in ps)
                foreach (CordStrand s in p.Strands)
                    for (int side = 0; side < 2; side++)
                    {
                        bool atStart = side == 0;
                        int cnt = atStart ? s.WhipA : s.WhipB;
                        if (cnt <= 0 || s.Pts == null || cnt >= s.Pts.Count) continue;
                        var tail = new List<V2>(cnt);
                        if (atStart) for (int i = cnt - 1; i >= 0; i--) tail.Add(s.Pts[i]);
                        else for (int i = s.Pts.Count - cnt; i < s.Pts.Count; i++) tail.Add(s.Pts[i]);
                        if (keep != null && !keep(tail[tail.Count - 1])) continue;
                        // the static cord up to the joint, read toward the joint
                        var before = new List<V2>();
                        double acc = 0;
                        if (atStart) { for (int i = cnt - 1; i < s.Pts.Count && acc <= lead; i++) { if (before.Count > 0) acc += V2.Dist(before[before.Count - 1], s.Pts[i]); before.Add(s.Pts[i]); } }
                        else { for (int i = s.Pts.Count - cnt; i >= 0 && acc <= lead; i--) { if (before.Count > 0) acc += V2.Dist(before[before.Count - 1], s.Pts[i]); before.Add(s.Pts[i]); } }
                        before.Reverse();                                    // ... -> joint
                        if (before.Count < 2) continue;
                        r.Tails++;
                        ulong seed = unchecked((ulong)(idx++ * 2654435761L + 17) + salt * 2654435761UL);
                        // the join's own direction is the laid cord's there (the static cord and the laid tail are one polyline): a frame keeps it
                        // when its bent tail leaves the joint the same way; a curve through the joint is the cord's shape, read by the bend radius
                        V2 jIn = (Ahead(tail, CordEndAudit.SlopeChord) - tail[0]).Norm();
                        double worstDeg = 0, minR = double.MaxValue; int badFrames = 0, pinchFrames = 0, jumps = 0;
                        for (int f = 0; f < frames; f++)
                        {
                            List<V2> bent = CordMotion.Whip(tail, f / fps, seed, CordMotion.WhipAmp);
                            r.Frames++;
                            if (V2.Dist(bent[0], before[before.Count - 1]) > 1e-6) jumps++;
                            V2 jOut = (Ahead(bent, CordEndAudit.SlopeChord) - bent[0]).Norm();
                            double deg = Math.Acos(Math.Max(-1, Math.Min(1, Dot(jIn, jOut)))) * 180 / Math.PI;
                            var whole = new List<V2>(before);
                            whole.AddRange(bent.Skip(1));
                            double rr = MinRadius(whole);
                            worstDeg = Math.Max(worstDeg, deg); minR = Math.Min(minR, rr);
                            if (deg > CordEndAudit.SlopeMaxDeg) badFrames++;
                            if (rr < MinBendR) pinchFrames++;
                        }
                        r.WorstDeg = Math.Max(r.WorstDeg, worstDeg); r.MinR = Math.Min(r.MinR, minR);
                        string at = $"{scene} live end @({tail[tail.Count - 1].X:0.00},{tail[tail.Count - 1].Z:0.00}) cord {p.EndA}|{p.EndB}";
                        if (jumps > 0) { r.Jumped++; r.Bad.Add($"{at}: the tail leaves the cord's end on {jumps} frames"); }
                        if (badFrames > 0) { r.OffSlope++; r.Bad.Add($"{at}: turns {worstDeg:0} deg at the join ({badFrames}/{frames} frames)"); }
                        if (pinchFrames > 0) { r.Pinched++; r.Bad.Add($"{at}: bends at radius {minR:0.000} < {MinBendR} at the join ({pinchFrames}/{frames} frames)"); }
                    }
            return r;
        }

        private static V2 Ahead(List<V2> P, double d)
        {
            double acc = 0;
            for (int i = 0; i + 1 < P.Count; i++)
            {
                double s = V2.Dist(P[i], P[i + 1]);
                if (acc + s >= d) return P[i] + (P[i + 1] - P[i]) * ((d - acc) / Math.Max(s, 1e-9));
                acc += s;
            }
            return P[P.Count - 1];
        }
    }
}
