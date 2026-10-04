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

    public struct StrandSpec { public double SagMul, Lateral; }

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

        /// <summary>1..maxStrands strands per span (seeded), each with its own sag x0.9-1.15 and a lateral offset
        /// of at most 0.04 cell at the insulator.</summary>
        public static List<StrandSpec> StrandsFor(int seed, int maxStrands)
        {
            int max = Math.Max(1, Math.Min(3, maxStrands));
            int count = 1 + (int)(U(seed, 1) * max);
            if (count > max) count = max;
            var list = new List<StrandSpec>(count);
            for (int i = 0; i < count; i++)
            {
                double lat = count == 1 ? 0 : (-0.04 + 0.08 * i / (count - 1));
                list.Add(new StrandSpec { SagMul = 0.9 + 0.25 * U(seed, 10 + i), Lateral = lat });
            }
            return list;
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

        // ------------------------------------------------------------------ a fallen span on the floor (design 2.6)
        /// <summary>
        /// The cable of a span whose far anchor died, lying on the floor from the survivor's base toward the dead
        /// anchor's cell: <paramref name="length"/> of cord (span x 1.05) laid as a gentle seeded meander around the
        /// straight line, every 0.25 cell, stopping at the first unwalkable cell (the rest "is over the wall" and is not
        /// drawn). Spare length beyond the straight distance is spent as wider meander, not by passing the dead cell.
        /// </summary>
        public static FallenLay LayFallen(P2 from, P2 toward, double length, int seed, Func<int, int, bool> walkable)
        {
            var lay = new FallenLay();
            double dist = P2.Dist(from, toward);
            lay.Pts.Add(from);
            lay.Tip = from;
            if (dist < 1e-6 || length <= 0) return lay;
            double ux = (toward.X - from.X) / dist, uz = (toward.Z - from.Z) / dist;
            double nx = -uz, nz = ux;
            double reach = Math.Min(dist, length);
            // meander amplitude chosen so the polyline length ~= length (small-slope approximation:
            // L ~ reach * (1 + (A k)^2 / 4) for y = A sin(k s); clamp to a believable 0.05-0.9 cell)
            double k = 2 * Math.PI / (3.0 + 2.0 * U(seed, 5));
            double extra = Math.Max(0, length / reach - 1);
            double amp = Math.Min(0.9, Math.Max(0.05, 2 * Math.Sqrt(extra) / k));
            double phi = 2 * Math.PI * U(seed, 6);
            const double step = 0.25;
            double used = 0;
            P2 prev = from;
            for (double s = step; s <= reach + 1e-9; s += step)
            {
                double fade = Math.Min(1, s / 1.0);                       // leaves the anchor base cleanly
                double off = amp * fade * (Math.Sin(k * s + phi) - Math.Sin(phi) * (1 - fade));
                var p = new P2(from.X + ux * s + nx * off, from.Z + uz * s + nz * off);
                if (!walkable((int)Math.Floor(p.X), (int)Math.Floor(p.Z))) { lay.Blocked = true; break; }
                double d = P2.Dist(prev, p);
                if (used + d > length) break;
                used += d;
                lay.Pts.Add(p);
                prev = p;
            }
            lay.Tip = lay.Pts[lay.Pts.Count - 1];
            return lay;
        }

        /// <summary>
        /// A cut or orphaned wire still hangs from the pole TOP down to the ground (owner review 2026-10-04 B11): the
        /// drop runs from the insulator (top, screen z fakes height) to the point where the fallen cord meets the ground,
        /// bowing a little to one side like a loose cable. Ends are exactly top and ground. Never shorter than the
        /// straight drop.
        /// </summary>
        public static List<P2> FallenDrop(P2 top, P2 ground, int seed, double step = 0.1)
        {
            double len = P2.Dist(top, ground);
            int n = Math.Max(4, (int)Math.Ceiling(len / Math.Max(0.02, step)));
            double ux = len < 1e-9 ? 0 : (ground.X - top.X) / len, uz = len < 1e-9 ? -1 : (ground.Z - top.Z) / len;
            double nx = -uz, nz = ux, bow = (U(seed, 9) < 0.5 ? -1 : 1) * (0.08 + 0.1 * U(seed, 10));
            var pts = new List<P2>(n + 1);
            for (int i = 0; i <= n; i++)
            {
                double t = i / (double)n, off = bow * Math.Sin(Math.PI * t) * Math.Min(1, len / 1.5);
                pts.Add(new P2(top.X + (ground.X - top.X) * t + nx * off, top.Z + (ground.Z - top.Z) * t + nz * off));
            }
            return pts;
        }

        /// <summary>Where a fallen cord's drop meets the ground: the first laid point at least <paramref name="reach"/> from the base.</summary>
        public static int GroundIndex(List<P2> lay, double reach = 0.35)
        {
            for (int i = 1; i < lay.Count; i++) if (P2.Dist(lay[0], lay[i]) >= reach) return i;
            return lay.Count - 1;
        }

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
