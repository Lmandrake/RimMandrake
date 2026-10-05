// Messy Conduit L5 -- aerial power lines, the Verse-free half (design:
// design/RimMandrake/messy_conduit_phase2_design_2026-10-02.md section 2).
// No Verse / Unity reference on purpose: Source/SelfTest compiles this PRODUCTION file directly
// (AerialSelfTest.cs). The game side (Building_AerialAnchor, RM_MapComponent_Aerial, CompPowerTap)
// translates Things into these plain records and acts on the answers.
using System;
using System.Collections.Generic;
using System.Linq;

namespace RimMandrake.MessyConduit.Aerial
{
    /// <summary>A ground-plane point: X east, Z north (RimWorld's x / z).</summary>
    public struct P2
    {
        public double X, Z;
        public P2(double x, double z) { X = x; Z = z; }
        public static double Dist(P2 a, P2 b) => Math.Sqrt((a.X - b.X) * (a.X - b.X) + (a.Z - b.Z) * (a.Z - b.Z));
        public static P2 Lerp(P2 a, P2 b, double t) => new P2(a.X + (b.X - a.X) * t, a.Z + (b.Z - a.Z) * t);
        public override string ToString() => "(" + X.ToString("0.00") + "," + Z.ToString("0.00") + ")";
    }

    /// <summary>Up = strung and carrying power; Cut = parted (explosion / roof): both halves lie at their anchors.</summary>
    public enum SpanState { Up, Cut }

    public enum LinkVerdict { Ok, Self, AlreadyLinked, OutOfRange, FullA, FullB, Foreign, NotAnchor, Roofed }

    /// <summary>What the link rules need to know about one anchor (or a candidate target).</summary>
    public class AnchorInfo
    {
        public int Id, X, Z, Faction, MaxLinks;
        public bool Roofed;
        /// <summary>False for anything that is not one of our anchors (their conduit, a battery): never a link target.</summary>
        public bool IsAnchor = true;
        public List<int> Linked = new List<int>();
    }

    /// <summary>One span that falls to the floor when its other anchor dies: it lies from Survivor's base
    /// toward the dead anchor's cell (TowardDead).</summary>
    public struct FallenSpec { public int Survivor; public bool TowardDead; }

    public class RemovalPlan
    {
        /// <summary>Every anchor whose net must be rebuilt (the despawn gap, design 2.2).</summary>
        public List<int> Reseed = new List<int>();
        public List<FallenSpec> Fallen = new List<FallenSpec>();
    }

    /// <summary>A watchdog read: the net id at each end of a span (-1 = no net).</summary>
    public struct SpanNetRead { public int Span, NetA, NetB; public SpanState State; }

    public class FallenLay
    {
        public List<P2> Pts = new List<P2>();
        public P2 Tip;
        /// <summary>True when an unwalkable cell stopped the cord before its length ran out ("the rest is over the wall").</summary>
        public bool Blocked;
    }

    public static class AerialMath
    {
        // ------------------------------------------------------------------ hashing (deterministic, platform-stable)
        public static uint Hash(int a, int b = 0, int c = 0)
        {
            unchecked
            {
                uint h = 2166136261u;
                h = (h ^ (uint)a) * 16777619u;
                h = (h ^ (uint)b) * 16777619u;
                h = (h ^ (uint)c) * 16777619u;
                h ^= h >> 13; h *= 0x5bd1e995u; h ^= h >> 15;
                return h;
            }
        }

        /// <summary>A deterministic value in [0,1) from (seed, salt).</summary>
        public static double U(int seed, int salt) => (Hash(seed, salt, 0x51A7) & 0xFFFFFF) / (double)0x1000000;

        // ------------------------------------------------------------------ the span curve (design 2.5)
        /// <summary>
        /// P(t) = lerp(A, B, t) + (0, -sag * 4t(1-t)), sag = sagFactor * |AB|, sampled about every
        /// <paramref name="step"/> cells. Top-down RimWorld fakes height as +z on screen, so a screen-down droop
        /// reads as a hanging wire from any direction. Ends are exactly A and B.
        /// </summary>
        public static List<P2> SpanCurve(P2 a, P2 b, double sagFactor, double step = 0.5)
        {
            double len = P2.Dist(a, b);
            double sag = Math.Max(0, sagFactor) * len;
            int n = Math.Max(4, (int)Math.Ceiling(len / Math.Max(0.05, step)));
            var pts = new List<P2>(n + 1);
            for (int i = 0; i <= n; i++)
            {
                double t = i / (double)n;
                P2 p = P2.Lerp(a, b, t);
                p.Z -= sag * 4 * t * (1 - t);
                pts.Add(p);
            }
            pts[0] = a;
            pts[n] = b;
            return pts;
        }

        /// <summary>
        /// CPU sway (design 2.5 option 2): perpendicular ground-plane offset of the sample at span fraction t,
        /// amp x wind x sin(pi t) x (sin(w time + phi) + 0.3 sin(2.3 w time + phi2)) / 1.3, w 1.1-1.6 rad/s seeded.
        /// Zero at both insulators and with no wind; |offset| never exceeds amp x min(wind, 1.5).
        /// </summary>
        public static double Sway(double t, double timeSec, double wind, double amp, int seed)
        {
            if (t <= 0 || t >= 1 || wind <= 0 || amp <= 0) return 0;
            double w = 1.1 + 0.5 * U(seed, 2);
            double phi = 2 * Math.PI * U(seed, 3), phi2 = 2 * Math.PI * U(seed, 4);
            double wave = (Math.Sin(w * timeSec + phi) + 0.3 * Math.Sin(2.3 * w * timeSec + phi2)) / 1.3;
            return amp * Math.Min(wind, 1.5) / 1.5 * Math.Sin(Math.PI * t) * wave * 1.3;
        }

        // ------------------------------------------------------------------ link rules (design 2.2.5, 2.4)
        public static bool InRange(int ax, int az, int bx, int bz, double range)
        {
            long dx = ax - bx, dz = az - bz;
            return dx * dx + dz * dz <= range * range + 1e-9;
        }

        public static LinkVerdict CanLink(AnchorInfo a, AnchorInfo b, double range)
        {
            if (a.Id == b.Id) return LinkVerdict.Self;
            if (!b.IsAnchor || !a.IsAnchor) return LinkVerdict.NotAnchor;
            if (a.Faction != b.Faction) return LinkVerdict.Foreign;
            if (a.Linked.Contains(b.Id) || b.Linked.Contains(a.Id)) return LinkVerdict.AlreadyLinked;
            if (a.Roofed || b.Roofed) return LinkVerdict.Roofed;
            if (!InRange(a.X, a.Z, b.X, b.Z, range)) return LinkVerdict.OutOfRange;
            if (a.Linked.Count >= a.MaxLinks) return LinkVerdict.FullA;
            if (b.Linked.Count >= b.MaxLinks) return LinkVerdict.FullB;
            return LinkVerdict.Ok;
        }

        /// <summary>Auto-link on build: the nearest anchor this one may link to, or -1. Ties break on the lower id.</summary>
        public static int AutoLinkPick(AnchorInfo self, IList<AnchorInfo> others, double range)
        {
            int best = -1;
            long bestD = long.MaxValue;
            foreach (AnchorInfo o in others)
            {
                if (CanLink(self, o, range) != LinkVerdict.Ok) continue;
                long dx = o.X - self.X, dz = o.Z - self.Z, d = dx * dx + dz * dz;
                if (d < bestD || (d == bestD && o.Id < best)) { bestD = d; best = o.Id; }
            }
            return best;
        }

        /// <summary>"Auto-link selected": Kruskal minimum spanning forest over the selection, edges within range,
        /// respecting maxLinks; anchors already linked count as joined (their links are kept, not re-added).</summary>
        public static List<(int, int)> MinimumSpanningLinks(IList<AnchorInfo> sel, double range)
        {
            var parent = new Dictionary<int, int>();
            var deg = new Dictionary<int, int>();
            foreach (AnchorInfo a in sel) { parent[a.Id] = a.Id; deg[a.Id] = a.Linked.Count; }
            int Find(int x) { while (parent[x] != x) { parent[x] = parent[parent[x]]; x = parent[x]; } return x; }
            foreach (AnchorInfo a in sel)
                foreach (int l in a.Linked)
                    if (parent.ContainsKey(l)) { int ra = Find(a.Id), rb = Find(l); if (ra != rb) parent[ra] = rb; }
            var edges = new List<(long d, AnchorInfo a, AnchorInfo b)>();
            for (int i = 0; i < sel.Count; i++)
                for (int j = i + 1; j < sel.Count; j++)
                {
                    AnchorInfo a = sel[i], b = sel[j];
                    if (a.Linked.Contains(b.Id) || b.Linked.Contains(a.Id)) continue;
                    if (a.Faction != b.Faction || a.Roofed || b.Roofed || !a.IsAnchor || !b.IsAnchor) continue;
                    if (!InRange(a.X, a.Z, b.X, b.Z, range)) continue;
                    long dx = a.X - b.X, dz = a.Z - b.Z;
                    edges.Add((dx * dx + dz * dz, a.Id < b.Id ? a : b, a.Id < b.Id ? b : a));
                }
            var result = new List<(int, int)>();
            foreach (var e in edges.OrderBy(e => e.d).ThenBy(e => e.a.Id).ThenBy(e => e.b.Id))
            {
                if (deg[e.a.Id] >= e.a.MaxLinks || deg[e.b.Id] >= e.b.MaxLinks) continue;
                int ra = Find(e.a.Id), rb = Find(e.b.Id);
                if (ra == rb) continue;
                parent[ra] = rb;
                deg[e.a.Id]++; deg[e.b.Id]++;
                result.Add((e.a.Id, e.b.Id));
            }
            return result;
        }

        /// <summary>A span is drawn, damaged and owned by the end with the lower thingIDNumber.</summary>
        public static bool Owns(int self, int other) => self < other;

        // ------------------------------------------------------------------ the cast shadow of a span (owner review B24)
        /// <summary>
        /// The ground shadow of a sagging span (owner review 2026-10-04 B24: the old straight base-to-base line read as a
        /// faint wire on the ground). The wire stands at height h(t) = lerp(hA, hB, t) - sag x |AB| x 4t(1-t) above the
        /// straight ground line between the pole feet; its shadow falls offset by h(t) x (kx, kz) (a high afternoon sun,
        /// down and to the right like vanilla building shadows), so it is furthest from the line at the poles and swings in
        /// under the low middle of the sag. Ends: baseA + hA(kx,kz) and baseB + hB(kx,kz).
        /// </summary>
        public static List<P2> SpanShadow(P2 baseA, P2 baseB, double hA, double hB, double sagFactor, double kx = 0.10, double kz = -0.16, double step = 0.5)
        {
            double len = P2.Dist(baseA, baseB);
            int n = Math.Max(4, (int)Math.Ceiling(len / Math.Max(0.05, step)));
            var pts = new List<P2>(n + 1);
            for (int i = 0; i <= n; i++)
            {
                double t = i / (double)n;
                double h = Math.Max(0, hA + (hB - hA) * t - Math.Max(0, sagFactor) * len * 4 * t * (1 - t));
                P2 g = P2.Lerp(baseA, baseB, t);
                pts.Add(new P2(g.X + kx * h, g.Z + kz * h));
            }
            return pts;
        }

        // ------------------------------------------------------------------ the despawn gap (design 2.2)
        /// <summary>
        /// An anchor leaves the map. Vanilla rebuilds nets only around the leaving anchor's natural ring, so every
        /// former partner must be re-seeded or its side sits net-less. Killed (not dismantled): each UP span falls
        /// onto its survivor as a floor cord; a CUT span already lies at the survivor, so nothing new falls.
        /// Dismantled: the cable is coiled, nothing falls.
        /// </summary>
        public static RemovalPlan PlanRemoval(int id, bool killed, IList<(int, SpanState)> spans)
        {
            var plan = new RemovalPlan();
            foreach ((int partner, SpanState st) in spans)
            {
                if (partner == id) continue;
                if (!plan.Reseed.Contains(partner)) plan.Reseed.Add(partner);
                if (killed && st == SpanState.Up) plan.Fallen.Add(new FallenSpec { Survivor = partner, TowardDead = true });
            }
            return plan;
        }

        /// <summary>Link, unlink, cut, re-string: both ends are re-seeded.</summary>
        public static List<int> ReseedOnLinkChange(int a, int b) => a == b ? new List<int> { a } : new List<int> { a, b };

        /// <summary>The 250-tick watchdog: an UP span whose ends are not on one shared non-null net is repaired
        /// (re-seed both). A cut span is SUPPOSED to split its nets.</summary>
        public static List<int> WatchdogRepairs(IList<SpanNetRead> reads)
        {
            var r = new List<int>();
            foreach (SpanNetRead s in reads)
                if (s.State == SpanState.Up && (s.NetA < 0 || s.NetB < 0 || s.NetA != s.NetB)) r.Add(s.Span);
            return r;
        }

        /// <summary>One strand of a span: its two end points (exactly the insulator tips) and its own sag multiplier.</summary>
        public struct SpanStrand { public P2 A, B; public int InsA, InsB; public double SagMul; }

        /// <summary>
        /// The strands of a span (owner review 2026-10-04 B23): ONE wire per insulator, so a span between two poles with
        /// N insulators each carries N wires (capped by <paramref name="maxStrands"/>, the "wires per span" setting), the
        /// same count on every span of a chain of like poles; each wire ends EXACTLY at an insulator tip on each pole
        /// (<paramref name="baseA"/> + insA[i], tips measured from the art: x across the crossarm, z = height). Fewer
        /// insulators at one end (a wall bracket has one) take <see cref="InsulatorIndex"/>'s spread. Seeded sag only.
        /// </summary>
        public static List<SpanStrand> SpanStrands(P2 baseA, IList<P2> insA, P2 baseB, IList<P2> insB, int seed, int maxStrands)
        {
            int count = StrandCount(insA.Count, insB.Count, maxStrands);
            var list = new List<SpanStrand>(count);
            for (int i = 0; i < count; i++)
            {
                int ia = InsulatorIndex(i, count, insA.Count), ib = InsulatorIndex(i, count, insB.Count);
                P2 oa = insA.Count > 0 ? insA[ia] : new P2(0, 0), ob = insB.Count > 0 ? insB[ib] : new P2(0, 0);
                list.Add(new SpanStrand
                {
                    A = new P2(baseA.X + oa.X, baseA.Z + oa.Z), B = new P2(baseB.X + ob.X, baseB.Z + ob.Z),
                    InsA = ia, InsB = ib, SagMul = 0.9 + 0.25 * U(seed, 10 + i)
                });
            }
            return list;
        }

        /// <summary>How many wires a span between anchors with <paramref name="insA"/> and <paramref name="insB"/> insulators
        /// carries: one per insulator, capped by the fewer end and the "wires per span" setting; never less than one.</summary>
        public static int StrandCount(int insA, int insB, int maxStrands) =>
            Math.Max(1, Math.Min(Math.Min(Math.Max(1, insA), Math.Max(1, insB)), Math.Max(1, maxStrands)));

        /// <summary>Which of <paramref name="insulators"/> (left to right on the crossarm) strand <paramref name="strand"/> of
        /// <paramref name="count"/> leaves from: one strand takes the middle, two take the outer pair, three take one
        /// each; never out of range, and distinct strands take distinct insulators when there are enough.</summary>
        public static int InsulatorIndex(int strand, int count, int insulators)
        {
            if (insulators <= 1 || count <= 0) return 0;
            if (count == 1) return insulators / 2;
            int i = (int)Math.Round(strand * (insulators - 1) / (double)(count - 1));
            return Math.Max(0, Math.Min(insulators - 1, i));
        }

        // ------------------------------------------------------------------ local drops onto a pole's terminals (owner round 2, 2026-10-04)
        /// <summary>
        /// Which insulator (terminal, left to right) each LOCAL connection of one pole takes: the devices wired to it and the
        /// transmitters standing beside it. Ordered by where they stand across the crossarm (<c>X</c>, east = right), then id,
        /// so wires never cross needlessly. Up to one per insulator they never share (one device takes the middle, two the
        /// outer pair, three one each: <see cref="InsulatorIndex"/>); with more devices than insulators they share in
        /// contiguous, even groups (left devices on the left terminal). Deterministic; every id in, one terminal out.
        /// </summary>
        public static Dictionary<int, int> AssignTerminals(IList<(int Id, double X)> devices, int insulators)
        {
            var r = new Dictionary<int, int>();
            var order = devices.OrderBy(d => d.X).ThenBy(d => d.Id).ToList();
            int k = order.Count, n = Math.Max(1, insulators);
            for (int i = 0; i < k; i++)
                r[order[i].Id] = n <= 1 ? 0 : k <= n ? InsulatorIndex(i, k, n) : Math.Min(n - 1, i * n / k);
            return r;
        }

        // ------------------------------------------------------------------ the wall bracket (owner round 2, 2026-10-04)
        /// <summary>How far the bracket art's wall-side extreme reaches past the wall's outer face INTO the wall (cells), per face
        /// (round 4, owner 2026-10-04: plates "should look mounted ON the wall"; "do they extend OUT of the wall? If so, it's not
        /// right"; the north-face bracket "really should be barely visible at all", like the vanilla wall torch). The wall face
        /// model is Core.WallMount (measured from his station-9 shot):
        ///   rot North: on the wall's visible SOUTH face: the whole plate inside the face band (at least its own depth, min 0.12)
        ///   rot East/West: on a side face seen edge-on: the whole plate inside the wall's edge bevel (same rule, max 0.18)
        ///   rot South: on the hidden NORTH face: the art is cut under its insulator; the cut line sits just under the wall's top
        ///              edge, so only the insulator shows over the wall, the way a wall torch's flame does.</summary>
        public static double BracketInset(int rot, double plateDepth)
        {
            switch (rot & 3)
            {
                case 2: return NorthFaceCutInset;
                case 0: return Math.Min(Math.Max(0.12, plateDepth + 0.02), RimMandrake.MessyConduit.Core.WallMount.SouthBand - 0.02);
                default: return Math.Min(Math.Max(0.12, plateDepth + 0.01), RimMandrake.MessyConduit.Core.WallMount.SideBevel);
            }
        }

        /// <summary>rot South: how far under the wall's top edge the cut line of the insulator-only art sits (cells).</summary>
        public const double NorthFaceCutInset = 0.03;

        /// <summary>Unit normal from the bracket's cell toward its wall. rot = RimWorld Rot4.AsInt (0 N, 1 E, 2 S, 3 W): a
        /// wall-attached bracket's rotation points AT its wall (vanilla Placeworker_AttachedToWall).</summary>
        public static P2 WallNormal(int rot)
        {
            switch (rot & 3)
            {
                case 0: return new P2(0, 1);
                case 1: return new P2(1, 0);
                case 2: return new P2(0, -1);
                default: return new P2(-1, 0);
            }
        }

        public static double Dot(P2 a, P2 b) => a.X * b.X + a.Z * b.Z;

        /// <summary>The bracket graphic's draw offset from its cell centre: along the wall normal only, so the plate's
        /// wall-side extreme (<paramref name="plateEdge"/>, cells from the graphic centre toward the wall, measured from the
        /// art) lands <see cref="BracketInset"/> past the wall's outer face (which is 0.5 from the cell centre). The arm
        /// and insulator then stand over the bracket's own cell, out from the wall.</summary>
        public static P2 BracketDrawOffset(int rot, double plateEdge, double plateDepth)
        {
            P2 n = WallNormal(rot);
            double d = 0.5 + BracketInset(rot, plateDepth) - plateEdge;
            return new P2(n.X * d, n.Z * d);
        }

        /// <summary>Does the art lean OUT from the wall: its insulator (offset from the graphic centre) lies on the side away
        /// from the wall? (Scrapper/Futuristic "south" renders came back plate-up: insulator toward the wall.)</summary>
        public static bool BracketLeansOut(int rot, P2 insulator) => Dot(insulator, WallNormal(rot)) < -0.02;

        // ------------------------------------------------------------------ a fallen / cut wire (design 2.6, owner review B11/B21)
        /// <summary>
        /// A cut or orphaned wire as ONE continuous cable (owner review 2026-10-04 B21: never a hanging drop joined to a
        /// separate floor cord): it leaves the insulator at <paramref name="top"/> (screen z fakes height), hangs down
        /// tangent-free to a touchdown point and lies on the ground the rest of the way to the break at
        /// <paramref name="toward"/>, so the polyline's LAST point (Tip) is the break point. The ground path is the
        /// straight line base -> break with one gentle seeded bow (at most 0.22 cell; no wiggle), checked cell by cell:
        /// the first unwalkable cell stops it (Blocked; the rest "is over the wall"). Height above the ground path is
        /// h (1 - s/s0)^2 up to the touchdown s0, then 0; the insulator's sideways offset on the crossarm fades out by s0.
        /// <paramref name="length"/> (cable length, span x 1.05) caps the reach only when it is under 0.8 x the distance.
        /// The first 0.75 cell is never checked: a wall bracket's base sits on its wall face.
        /// </summary>
        public static FallenLay LayFallen(P2 top, P2 basePt, P2 toward, double length, int seed, Func<int, int, bool> walkable)
        {
            var lay = new FallenLay();
            lay.Pts.Add(top);
            lay.Tip = top;
            double dist = P2.Dist(basePt, toward);
            double h = top.Z - basePt.Z, ix = top.X - basePt.X;
            if (dist < 1e-6 || length <= 0) return lay;
            double ux = (toward.X - basePt.X) / dist, uz = (toward.Z - basePt.Z) / dist, nx = -uz, nz = ux;
            double want = length >= 0.8 * dist ? dist : length;   // the cable reaches the break unless it is far too short
            double bow = (U(seed, 9) < 0.5 ? -1 : 1) * Math.Min(0.22, 0.06 + 0.02 * want) * (0.6 + 0.4 * U(seed, 10));
            Func<double, double, P2> ground = (s, r) =>
            {
                double off = bow * Math.Sin(Math.PI * Math.Min(1, s / r));
                return new P2(basePt.X + ux * s + nx * off, basePt.Z + uz * s + nz * off);
            };
            // pass 1: how far the ground path is open
            double reach = want;
            for (double s = 0.25; s <= want + 1e-9; s += 0.25)
            {
                P2 g = ground(s, want);
                if (s > 0.75 && !walkable((int)Math.Floor(g.X), (int)Math.Floor(g.Z))) { lay.Blocked = true; reach = Math.Max(0, s - 0.25); break; }
            }
            if (reach < 0.05) return lay;
            double s0 = Math.Min(reach * 0.75, Math.Max(0.9, Math.Abs(h) * 0.85));
            // pass 2: the one cable, insulator -> touchdown -> break (0.1 cell samples while hanging, 0.25 lying)
            double sPos = 0;
            while (true)
            {
                sPos = Math.Min(reach, sPos + (sPos < s0 ? 0.1 : 0.25));
                double k = sPos < s0 ? 1 - sPos / s0 : 0;
                P2 g = ground(sPos, reach);
                lay.Pts.Add(new P2(g.X + ix * k, g.Z + h * k * k));
                if (sPos >= reach - 1e-9) break;
            }
            lay.Tip = lay.Pts[lay.Pts.Count - 1];
            return lay;
        }

        /// <summary>
        /// Round 3 (owner 2026-10-04: "If we're going to have three wires connecting between poles, then three wires should be
        /// laying on the ground when broken by explosion"): a broken span drops EVERY one of its <paramref name="count"/>
        /// wires. Wire i leaves the insulator the span's strand i used on this anchor (<see cref="InsulatorIndex"/>, the same
        /// fan as <see cref="SpanStrands"/>), lies toward the break offset sideways by (i - (count-1)/2) x
        /// <see cref="FallenSpread"/> so the wires lie side by side rather than on top of each other, and gets its own seed
        /// (its own bow). Each lay is <see cref="LayFallen"/>'s one continuous cable.
        /// </summary>
        public static List<FallenLay> LayFallenStrands(IList<P2> tips, P2 basePt, P2 toward, double length, int seed, int count, Func<int, int, bool> walkable)
        {
            var r = new List<FallenLay>();
            int n = Math.Max(1, count);
            double dist = P2.Dist(basePt, toward);
            double ux = dist > 1e-6 ? (toward.X - basePt.X) / dist : 1, uz = dist > 1e-6 ? (toward.Z - basePt.Z) / dist : 0;
            for (int i = 0; i < n; i++)
            {
                P2 top = tips.Count > 0 ? tips[InsulatorIndex(i, n, tips.Count)] : basePt;
                double lat = n == 1 ? 0 : (i - (n - 1) / 2.0) * FallenSpread;
                var to = new P2(toward.X - uz * lat, toward.Z + ux * lat);
                r.Add(LayFallen(top, basePt, to, length, unchecked(seed + 7919 * i), walkable));
            }
            return r;
        }

        /// <summary>Sideways gap between neighbouring fallen wires at the break (cells). PROVISIONAL.</summary>
        public const double FallenSpread = 0.22;

        // ------------------------------------------------------------------ explosion hit test (design 2.6)
        public static double ClosestT(P2 a, P2 b, P2 c)
        {
            double dx = b.X - a.X, dz = b.Z - a.Z, l2 = dx * dx + dz * dz;
            if (l2 < 1e-12) return 0;
            double t = ((c.X - a.X) * dx + (c.Z - a.Z) * dz) / l2;
            return Math.Max(0, Math.Min(1, t));
        }

        /// <summary>Does a blast of <paramref name="radius"/> at c reach the span's straight ground projection?</summary>
        public static bool SpanHit(P2 a, P2 b, P2 c, double radius) => P2.Dist(P2.Lerp(a, b, ClosestT(a, b, c)), c) <= radius;

        // ------------------------------------------------------------------ the one-way power tap (design 2.7)
        /// <summary>
        /// Energy (watt-days) the clamp takes from the victim net this tick: at most rate x k, at most what the victim
        /// has to give (its own raw gain this tick + stored battery energy), never negative; 0 when taps are off or the
        /// "victim" is our own net. rawGainPerTick and stored are the VICTIM's, read without the tap's own debit;
        /// k = CompPower.WattsToWattDaysPerTick.
        /// </summary>
        public static double TapStolenPerTick(double rateW, double rawGainPerTick, double stored, double k, bool sameNet, bool enabled)
        {
            if (!enabled || sameNet || rateW <= 0) return 0;
            double avail = rawGainPerTick + Math.Max(0, stored);
            if (avail <= 0) return 0;
            return Math.Min(rateW * k, avail);
        }
    }
}
