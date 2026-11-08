// Gimme Some Slack L5 -- aerial power lines, the Verse-free half (design:
// design/RimMandrake/messy_conduit_phase2_design_2026-10-02.md section 2).
// No Verse / Unity reference on purpose: Source/SelfTest compiles this PRODUCTION file directly
// (AerialSelfTest.cs). The game side (CompAerialAnchor, RM_MapComponent_Aerial, CompPowerTap)
// translates Things into these plain records and acts on the answers.
using System;
using System.Collections.Generic;
using System.Linq;

namespace RimMandrake.GimmeSomeSlack.Aerial
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

    public enum LinkVerdict { Ok, Self, AlreadyLinked, OutOfRange, FullA, FullB, Foreign, NotAnchor, Roofed, Gone, WrongKind }

    /// <summary>PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE phase 4: what an overhead span carries. Power (masts, lamp masts, wall
    /// brackets: joins power nets) or Pipe (FlowWorks pipe poles: no power, a thicker, stiffer span). Set per anchor def on
    /// AerialAnchorExtension.lineKind; a span only ever joins two anchors of one kind.</summary>
    public enum AerialLineKind { Power = 0, Pipe = 1 }

    /// <summary>Per-kind span numbers (pure). The power numbers are AerialSettings'; the pipe numbers are FlowWorks' Mod
    /// Settings, handed over through AerialLineProfiles.RegisterPipeProfile. The defaults here apply only until (or unless)
    /// FlowWorks registers, and must equal FlowWorks' RM_PipePoleMath defaults (its SelfTest compiles both and checks).</summary>
    public static class AerialKinds
    {
        public const float PowerSpanMin = 4f, PowerSpanMax = 40f;
        /// <summary>Owner, pipes-across-pits ruling (proposal max span 12).</summary>
        public const float PipeMaxSpanDefault = 12f;
        /// <summary>Owner by card 2026-10-20 (line widths spec): "about a third of GSS wire sag, about 2% of span".</summary>
        public const float PipeSagDefault = 0.02f;
        /// <summary>Sanity bounds on whatever is registered (the slider bounds are FlowWorks').</summary>
        public const float PipeSpanMin = 2f, PipeSpanMax = 30f, PipeSagMax = 0.15f;

        public static float Clamp(float v, float lo, float hi) => float.IsNaN(v) ? lo : (v < lo ? lo : (v > hi ? hi : v));

        /// <summary>Longest span of this kind, cells.</summary>
        public static float RangeFor(AerialLineKind k, float powerMaxSpan, float pipeMaxSpan) =>
            k == AerialLineKind.Pipe ? Clamp(pipeMaxSpan, PipeSpanMin, PipeSpanMax) : Clamp(powerMaxSpan, PowerSpanMin, PowerSpanMax);

        /// <summary>Sag factor of this kind (fraction of the span length).</summary>
        public static float SagFor(AerialLineKind k, float powerSag, float pipeSag) =>
            k == AerialLineKind.Pipe ? Clamp(pipeSag, 0f, PipeSagMax) : (float.IsNaN(powerSag) || powerSag < 0f ? 0f : powerSag);

        /// <summary>The deepest point of a span below its chord, cells: SpanCurve's sag at t = 0.5.</summary>
        public static double SagDepth(double spanLength, double sagFactor) => Math.Max(0, sagFactor) * Math.Max(0, spanLength);

        /// <summary>A pipe is one rigid run: one strand, no drip loop, no wind sway (it is not a wire).</summary>
        public static int StrandCap(AerialLineKind k, int maxStrands) => k == AerialLineKind.Pipe ? 1 : maxStrands;
        public static bool Drips(AerialLineKind k, bool dripSetting) => k == AerialLineKind.Power && dripSetting;
        public static bool Sways(AerialLineKind k) => k == AerialLineKind.Power;
        /// <summary>Only a power anchor joins a power net or draws drop wires to the devices beside it.</summary>
        public static bool CarriesPower(AerialLineKind k) => k == AerialLineKind.Power;

        /// <summary>PIPE_POLE_SWITCH_DECIDE_HOSTAGE_TO_WIRES (owner by card 2026-10-21: "Their own switch."): which switch governs
        /// an anchor of this kind. A power anchor obeys GSS's power-lines master switch; a pipe pole obeys FlowWorks' pipe-pole
        /// switch (registered through AerialLineProfiles.RegisterPipeSwitch) and never the power one.</summary>
        public static bool KindOn(AerialLineKind k, bool powerOn, bool pipeOn) => CarriesPower(k) ? powerOn : pipeOn;

        /// <summary>A behaviour whose GSS setting sits under the power master (auto-link, the wire-down alert, the owner-change
        /// cut): a power anchor needs the master AND that setting; a pipe pole needs only its own switch, because those GSS
        /// settings are power-line settings, greyed out with the power master off.</summary>
        public static bool KindBehaviour(AerialLineKind k, bool powerOn, bool pipeOn, bool powerSetting) =>
            CarriesPower(k) ? powerOn && powerSetting : pipeOn;
    }

    /// <summary>What the link rules need to know about one anchor (or a candidate target).</summary>
    public class AnchorInfo
    {
        public int Id, X, Z, Faction, MaxLinks;
        public bool Roofed;
        /// <summary>What the anchor's spans carry; a span joins one kind only (phase 4).</summary>
        public AerialLineKind Kind = AerialLineKind.Power;
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
        /// <summary>GS-1: partners flying with this anchor on the same gravship; their span is kept, not taken down.</summary>
        public List<int> Kept = new List<int>();
        /// <summary>GS-1: partners left on the ground while this anchor flies off; their span was taken down and coiled.</summary>
        public List<int> Grounded = new List<int>();
    }

    /// <summary>A watchdog read: the net id at each end of a span (-1 = no net).</summary>
    public struct SpanNetRead { public int Span, NetA, NetB; public SpanState State; }

    public class FallenLay
    {
        public List<P2> Pts = new List<P2>();
        public P2 Tip;
        /// <summary>Where the end is on screen now, and which way it points: the writhing end moves, its spark and glow go with it. Tip while it is still.</summary>
        public P2 TipNow, OutNow;
        /// <summary>True when an unwalkable cell stopped the cord before its length ran out ("the rest is over the wall").</summary>
        public bool Blocked;
        /// <summary>Index into <see cref="Pts"/> of the first point that lies ON THE GROUND (the touchdown); points before it
        /// hang from the insulator and carry its height as extra screen +Z, so they are not ground cells (GPT pre-release
        /// C3). -1 when nothing of the cable reached the ground.</summary>
        public int GroundFrom = -1;
        public bool TipGrounded => GroundFrom >= 0;
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
        /// amp x min(wind, 1.5) / 1.5 x sin(pi t) x (sin(w time + phi) + 0.3 sin(2.3 w time + phi2)), w 1.1-1.6 rad/s seeded.
        /// Zero at both insulators and with no wind; |offset| never exceeds 1.3 x amp x min(wind, 1.5) / 1.5 (below amp x min(wind, 1.5)).
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
            if (a.Kind != b.Kind) return LinkVerdict.WrongKind;
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
                    if (a.Faction != b.Faction || a.Kind != b.Kind || a.Roofed || b.Roofed || !a.IsAnchor || !b.IsAnchor) continue;
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

        /// <summary>The drip-loop setting's default (AerialSettings.dripLoops): off since the owner's sitting of 2026-11-08 12:20 PM, "The top
        /// of power poles shows needless kinks in the wires where they connect too" (the drip loop at every insulator).</summary>
        public const bool DripLoopsDefault = false;

        /// <summary>Design 2.5 "each strand gets a short drip loop below the insulator" (unbuilt until the 2026-10-10 build-out;
        /// setting dripLoops, default ON 2026-10-15, OFF since 2026-11-08). The span curve as
        /// <see cref="SpanCurve"/>, plus within <paramref name="reach"/> cells of each end a dip of up to
        /// <paramref name="depth"/> cells (screen-down = hanging) shaped (1 - cos(2 pi d / reach)) / 2, so the wire leaves the insulator
        /// level, sags into a small loop and rises back to the span: a sine left a sharp peak on every insulator, and two spans meeting there drew a zigzag along the crossarm
        /// (blind judge, pass 1: "small wiggles on top of the crossarm"). Ends stay exactly A and B; the ends are sampled densely (12 per
        /// loop); beyond the loops the points are the plain curve's. depth or reach 0 returns SpanCurve unchanged.</summary>
        public static List<P2> SpanCurveDrip(P2 a, P2 b, double sagFactor, double depth, double reach, double step = 0.5)
        {
            double len = P2.Dist(a, b);
            if (!(depth > 0) || !(reach > 0) || len < 1e-6) return SpanCurve(a, b, sagFactor, step);
            reach = Math.Min(reach, len / 4);
            double sag = Math.Max(0, sagFactor) * len, tr = reach / len;
            var ts = new List<double>();
            const int loopN = 12;
            for (int k = 0; k < loopN; k++) ts.Add(tr * k / loopN);
            int n = Math.Max(2, (int)Math.Ceiling((1 - 2 * tr) * len / Math.Max(0.05, step)));
            for (int k = 0; k <= n; k++) ts.Add(tr + (1 - 2 * tr) * k / n);
            for (int k = loopN - 1; k >= 0; k--) ts.Add(1 - tr * k / loopN);
            var pts = new List<P2>(ts.Count);
            foreach (double t in ts)
            {
                P2 p = P2.Lerp(a, b, t);
                p.Z -= sag * 4 * t * (1 - t);
                double d = Math.Min(t, 1 - t) * len;
                if (d < reach) p.Z -= depth * 0.5 * (1 - Math.Cos(2 * Math.PI * d / reach));
                pts.Add(p);
            }
            pts[0] = a;
            pts[pts.Count - 1] = b;
            return pts;
        }

        /// <summary>Fraction along A->B of p's projection, clamped to [0, 1] (sway pinning for non-uniform samples).</summary>
        public static double ProjectT(P2 a, P2 b, P2 p)
        {
            double dx = b.X - a.X, dz = b.Z - a.Z, l2 = dx * dx + dz * dz;
            if (l2 < 1e-12) return 0;
            return Math.Max(0, Math.Min(1, ((p.X - a.X) * dx + (p.Z - a.Z) * dz) / l2));
        }

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
        public static RemovalPlan PlanRemoval(int id, bool killed, IList<(int, SpanState)> spans) => PlanRemoval(id, killed, spans, null);

        /// <summary>aboard: non-null while this anchor is being lifted onto a gravship (DeSpawn WillReplace inside
        /// GravshipUtility.GenerateGravship); it holds the partners flying with it. A span to one of them is kept
        /// (both ends land together, the comp objects survive the flight); a span to a partner left behind is taken
        /// down and coiled (never dropped: nothing died).</summary>
        public static RemovalPlan PlanRemoval(int id, bool killed, IList<(int, SpanState)> spans, ICollection<int> aboard)
        {
            var plan = new RemovalPlan();
            foreach ((int partner, SpanState st) in spans)
            {
                if (partner == id) continue;
                if (aboard != null && !killed)
                {
                    if (aboard.Contains(partner)) { if (!plan.Kept.Contains(partner)) plan.Kept.Add(partner); continue; }
                    if (!plan.Grounded.Contains(partner)) plan.Grounded.Add(partner);
                }
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
                case 0: return Math.Min(Math.Max(0.12, plateDepth + 0.02), RimMandrake.GimmeSomeSlack.Core.WallMount.SouthBand - 0.02);
                default: return Math.Min(Math.Max(0.12, plateDepth + 0.01), RimMandrake.GimmeSomeSlack.Core.WallMount.SideBevel);
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
        /// separate floor cord): it leaves the insulator at <paramref name="top"/> (screen z fakes height), hangs down and out
        /// to its own side to a touchdown point and lies on the ground the rest of the way, so the polyline's LAST point (Tip)
        /// is the end, near <paramref name="toward"/> but not on its line. On the ground it is a loose cut cord (blind judge,
        /// pass 1: "a downed wire must read as a loose cut cord lying there"): uneven seeded bends at uneven places, a small
        /// wander so no stretch runs straight, a hook at the end, and on anything over 3 cells an uneven coil or two. Slack that
        /// would cross an unwalkable cell is halved and halved again before giving up; then the first unwalkable cell on the
        /// bare line stops it (Blocked; the rest "is over the wall"). Height above the ground path is h (1 - s/s0)^2 up to the
        /// touchdown s0, then 0; the insulator's sideways offset on the crossarm fades out by s0. <paramref name="length"/>
        /// (cable length, span x 1.05) caps the reach only when it is under 0.8 x the distance. The first 0.75 cell is never
        /// checked: a wall bracket's base sits on its wall face. <paramref name="side"/> picks the side it falls to (0 = by
        /// seed, and it falls closer in: the middle wire between two outer ones).
        /// </summary>
        public static FallenLay LayFallen(P2 top, P2 basePt, P2 toward, double length, int seed, Func<int, int, bool> walkable, int side = 0)
        {
            var lay = new FallenLay();
            lay.Pts.Add(top);
            lay.Tip = lay.TipNow = top;
            double dist = P2.Dist(basePt, toward);
            double h = top.Z - basePt.Z, ix = top.X - basePt.X;
            if (dist < 1e-6 || length <= 0) return lay;
            double ax = (toward.X - basePt.X) / dist, az = (toward.Z - basePt.Z) / dist;
            double ux = ax, uz = az, nx = -uz, nz = ux;
            double cable = length >= 0.8 * dist ? dist : length;   // the cable reaches the break unless it is far too short
            int sgn = side != 0 ? Math.Sign(side) : U(seed, 9) < 0.5 ? -1 : 1;
            // the plan of the ground path over `want` cells of its line (the cable's length, or less where something stops it)
            double want = 0, fit = 0, s0 = 0, fanIn = 0, fan = 0, wanderA = 0, wanderL = 0, wanderP = 0, hookL = 0, hookA = 0;
            int bends = 0;
            var bendAt = new double[4]; var bendW = new double[4]; var bendA = new double[4];
            Action<double> plan = w =>
            {
                want = w;
                fit = Math.Min(1, want / 3);
                // the bends: uneven, at uneven places, the last of them late so the cord still wanders into its end
                bends = want < 2 ? 1 : Math.Min(4, 2 + (int)(want / 5));
                int sign = sgn;
                for (int b = 0; b < bends; b++)
                {
                    bendAt[b] = want * (b == bends - 1 ? 0.62 + 0.26 * U(seed, 40 + b) : 0.14 + 0.5 * (b + U(seed, 40 + b)) / bends);
                    bendW[b] = Math.Max(0.8, Math.Min(2.6, want * (0.13 + 0.1 * U(seed, 50 + b))));
                    bendA[b] = sign * Math.Min(1.8, 0.25 + 0.32 * want) * (0.5 + 0.5 * U(seed, 60 + b));
                    sign = U(seed, 70 + b) < 0.8 ? -sign : sign;
                }
                wanderA = (0.07 + 0.09 * U(seed, 10)) * fit; wanderL = 0.55 + 0.4 * U(seed, 11); wanderP = 6.283 * U(seed, 12);
                hookL = Math.Min(1.7, 0.35 * want); hookA = (U(seed, 13) < 0.5 ? -1 : 1) * Math.Min(0.95, 0.24 * want) * (0.6 + 0.4 * U(seed, 14));
                fan = sgn * (side != 0 ? 0.75 + 0.45 * U(seed, 15) : 0.3 + 0.25 * U(seed, 15)) * fit;
            };
            // which way it lies: the break's own line turned by t (radians); a wire falling away up the screen doubles back past its
            // own drop, and the wider the touchdown, the rounder that turn
            Action<double> aim = t =>
            {
                double c = Math.Cos(t), sn = Math.Sin(t);
                ux = ax * c - az * sn; uz = ax * sn + az * c; nx = -uz; nz = ux;
                s0 = Math.Min(want * 0.6, Math.Max(0.7, Math.Abs(h) * (0.45 + 0.5 * Math.Max(0, uz))));
                fanIn = s0 * (1.3 + 0.7 * Math.Max(0, uz));
            };
            Func<double, double, P2> ground = (s, k) =>
            {
                double off = 0;
                double on = Smooth01(s / Math.Max(0.5, fanIn));
                for (int b = 0; b < bends; b++)
                {
                    double q = (s - bendAt[b]) / bendW[b];
                    off += bendA[b] * Math.Exp(-q * q);
                }
                off = on * (off + wanderA * Math.Sin(s / wanderL + wanderP)) + fan * Smooth01(s / Math.Max(0.5, fanIn)) * (1 - Smooth01((s - fanIn) / Math.Max(0.5, want - fanIn)));
                if (s > want - hookL) { double q = (s - (want - hookL)) / Math.Max(1e-6, hookL); off += hookA * q * q; }
                off = Geo2Clamp(k * off, Math.Min(2.6, 0.4 * want + 0.3));
                return new P2(basePt.X + ux * s + nx * off, basePt.Z + uz * s + nz * off);
            };
            Func<P2, bool> open = g => walkable((int)Math.Floor(g.X), (int)Math.Floor(g.Z));
            // how far along its line the ground path at slack k stays on open ground (want when all of it does)
            Func<double, double> clearTo = k =>
            {
                for (double s = 0.2; s <= want + 1e-9; s += 0.2)
                    if (s > 0.75 && !open(ground(s, k))) return Math.Max(0, s - 0.2);
                return want;
            };
            // the widest slack this ground takes, on the break's own line first, then turned to its own side and the other, up to 50
            // degrees; the same bends mirrored before any less of them. A wire beside a rock bends away from it, and one whose line
            // crosses a shed built under the span falls beside the shed, a loose cord, instead of halving into a rod that stops at
            // its wall (a mortar on a lamp mast over a shed, pass 12)
            plan(cable);
            double slack = 0, turn = 0, reach = -1;
            foreach (double[] ks in SlackLevels)
            {
                foreach (double t in AimTurns)
                {
                    aim(t * sgn);
                    foreach (double k in ks)
                        if (clearTo(k) >= want) { slack = k; turn = t * sgn; reach = want; break; }
                    if (reach >= 0) break;
                }
                if (reach >= 0) break;
            }
            // nothing lies its whole length (a wall across every way it could fall): it lies as far as the ground lets it, along the
            // way that goes furthest, its bends drawn in to that stretch, and the cable it has left piles up against what stopped it
            if (reach < 0)
            {
                lay.Blocked = true;
                for (int pass = 0; pass < 3 && reach < 0; pass++)
                {
                    double best = 0, bestK = 0, bestT = 0;
                    foreach (double[] ks in SlackLevels)
                        foreach (double t in AimTurns)
                        {
                            aim(t * sgn);
                            foreach (double k in ks)
                            {
                                double r = clearTo(k);
                                if (r > best + 0.05) { best = r; bestK = k; bestT = t * sgn; }
                            }
                        }
                    if (best < 0.05) break;
                    plan(best);   // the bends drawn in to the stretch it has; it may lie whole now, or stop sooner and try again
                    aim(bestT);
                    if (clearTo(bestK) >= want) { slack = bestK; turn = bestT; reach = want; }
                }
                if (reach < 0)
                {
                    plan(cable);   // nothing at all clears: the bare line, as far as it goes
                    aim(0);
                    slack = 0; turn = 0; reach = clearTo(0);
                    if (reach >= 0.05) plan(reach);
                }
                if (reach < 0.05) return lay;
            }
            aim(turn);
            s0 = Math.Min(reach * 0.6, s0);
            // where the coils go: never on the hanging part, never on the end that writhes; a cord that stopped short piles the cable
            // it has left in more of them, in front of what stopped it
            double spare = Math.Max(0, cable - reach * 1.15);
            var coilsAt = new List<double>();
            if (want >= 3) coilsAt.Add(want * (0.3 + 0.35 * U(seed, 16)));
            if (want >= 7 && U(seed, 17) < 0.65) coilsAt.Add(want * (0.68 + 0.14 * U(seed, 18)));
            double lo = Math.Max(s0 + 0.2, 0.3 * reach), hi = reach - 1.85;
            if (lay.Blocked && hi > lo)
            {
                int more = Math.Min(3, (int)Math.Round(spare / 2.2)) - coilsAt.Count;
                for (int c = 0; c < more; c++) coilsAt.Add(lo + (hi - lo) * (c + U(seed, 90 + c)) / more);
                coilsAt.Sort();
            }
            bool piling = lay.Blocked && spare > 1;
            int coilIdx = 0;
            // the one cable, insulator -> touchdown -> end
            double sPos = 0;
            while (true)
            {
                sPos = Math.Min(reach, sPos + (sPos < s0 ? 0.06 : 0.1));
                double k = sPos < s0 ? 1 - sPos / s0 : 0;
                P2 g = ground(sPos, slack);
                lay.Pts.Add(new P2(g.X + ix * k, g.Z + h * k * k));
                if (k == 0 && lay.GroundFrom < 0) lay.GroundFrom = lay.Pts.Count - 1;
                while (k == 0 && coilIdx < coilsAt.Count && sPos >= coilsAt[coilIdx])
                {
                    if (sPos <= reach - 1.8 && (slack != 0 || piling))
                    {
                        double drift = 0.1 + 0.25 * U(seed, 80 + coilIdx);
                        if (AddCoil(lay.Pts, ground(sPos + 0.05, slack), seed + 1009 * coilIdx, Math.Max(piling ? 0.8 : 0, Math.Abs(slack)), drift, want >= 5 || piling, open))
                            sPos = Math.Min(reach - 1.5, sPos + drift);
                    }
                    coilIdx++;
                }
                if (sPos >= reach - 1e-9) break;
            }
            lay.Tip = lay.Pts[lay.Pts.Count - 1];
            lay.TipNow = lay.Tip;
            return lay;
        }

        /// <summary>The slack a fallen wire tries, widest first; each level the bends one way and then mirrored.</summary>
        private static readonly double[][] SlackLevels = { new[] { 1.0, -1.0 }, new[] { 0.5, -0.5 }, new[] { 0.25, -0.25 } };
        /// <summary>The turns off the break's own line a fallen wire tries, its own side first (radians: 0, 12, 24, 36, 50 degrees).</summary>
        private static readonly double[] AimTurns = { 0, 0.21, -0.21, 0.42, -0.42, 0.63, -0.63, 0.87, -0.87 };

        private static double Geo2Clamp(double v, double lim) => Math.Max(-lim, Math.Min(lim, v));

        private static double Smooth01(double x) { x = Math.Max(0, Math.Min(1, x)); return x * x * (3 - 2 * x); }

        /// <summary>A turn of slack on the end of <paramref name="pts"/>, leaving and coming back the way the cable was heading: never a stamped circle (it stretches, bulges
        /// to one side, and a double turn comes in tighter on its second round). Comes out <paramref name="drift"/> further on. False, and left out, if it would cross an unwalkable cell.</summary>
        private static bool AddCoil(List<P2> pts, P2 next, int seed, double slack, double drift, bool mayDouble, Func<P2, bool> open)
        {
            P2 p = pts[pts.Count - 1];
            double tx = next.X - p.X, tz = next.Z - p.Z, tl = Math.Sqrt(tx * tx + tz * tz);
            double r = (0.26 + 0.28 * U(seed, 20)) * Math.Max(0.5, slack);
            if (tl < 1e-9 || r < 0.1) return false;
            tx /= tl; tz /= tl;
            int side = U(seed, 21) < 0.5 ? -1 : 1;
            double nx = -tz * side, nz = tx * side;
            int wraps = mayDouble && U(seed, 22) < 0.35 ? 2 : 1;
            double stretch = 0.8 + 0.65 * U(seed, 23), bulge = 0.1 + 0.25 * U(seed, 24), bulgeAt = 6.283 * U(seed, 25), tighten = wraps == 2 ? 0.22 + 0.2 * U(seed, 26) : 0;
            int n = 24 * wraps;
            var turn = new List<P2>(n);
            for (int i = 1; i <= n; i++)
            {
                double th = 2 * Math.PI * wraps * i / n, end = Math.Sin(th / 2 / wraps);
                double rr = r * (1 + bulge * Math.Sin(th + bulgeAt) * end * end - tighten * end * end);
                double along = rr * stretch * Math.Sin(th) + drift * i / n, across = rr * (1 - Math.Cos(th));
                var q = new P2(p.X + tx * along + nx * across, p.Z + tz * along + nz * across);
                if (!open(q)) return false;
                turn.Add(q);
            }
            pts.AddRange(turn);
            return true;
        }

        /// <summary>
        /// Round 3 (owner 2026-10-04: "If we're going to have three wires connecting between poles, then three wires should be
        /// laying on the ground when broken by explosion"): a broken span drops EVERY one of its <paramref name="count"/>
        /// wires. Wire i leaves the insulator the span's strand i used on this anchor (<see cref="InsulatorIndex"/>, the same
        /// fan as <see cref="SpanStrands"/>) and is its own cut cord, with its own seed: it bends out to its own side and ends
        /// on its own spot, <see cref="FallenSpread"/> from its neighbour's and short of the break by its own amount, so the wires
        /// never pinch to one point (blind judge, pass 1). Each lay is <see cref="LayFallen"/>'s one continuous cable.
        /// </summary>
        public static List<FallenLay> LayFallenStrands(IList<P2> tips, P2 basePt, P2 toward, double length, int seed, int count, Func<int, int, bool> walkable)
        {
            var r = new List<FallenLay>();
            int n = Math.Max(1, count);
            double dist = P2.Dist(basePt, toward);
            double ux = dist > 1e-6 ? (toward.X - basePt.X) / dist : 1, uz = dist > 1e-6 ? (toward.Z - basePt.Z) / dist : 0;
            double spread = FallenSpread * Math.Min(1, dist / 4);
            for (int i = 0; i < n; i++)
            {
                int wseed = unchecked(seed + 7919 * i);
                P2 top = tips.Count > 0 ? tips[InsulatorIndex(i, n, tips.Count)] : basePt;
                double lat = n == 1 ? 0 : (i - (n - 1) / 2.0) * spread;
                // one wire alone reaches the break; of several, each stops short by its own amount
                double shortBy = n == 1 ? 0 : dist * (0.06 + 0.2 * U(wseed, 17));
                var to = new P2(toward.X - ux * shortBy - uz * lat, toward.Z - uz * shortBy + ux * lat);
                r.Add(LayFallen(top, basePt, to, length, wseed, walkable, Math.Sign(lat)));
            }
            return r;
        }

        /// <summary>How many points of a fallen wire's end writhe, or 0 if it has too little lying on the ground.</summary>
        public static int WireTailCount(FallenLay l, double len)
        {
            if (l.GroundFrom < 0) return 0;
            double acc = 0;
            int c = 1;
            for (int i = l.Pts.Count - 1; i > l.GroundFrom; i--)
            {
                acc += P2.Dist(l.Pts[i], l.Pts[i - 1]);
                if (acc > len) break;
                c++;
            }
            return c >= 3 ? c : 0;
        }

        /// <summary>
        /// A pole's or mast's local lead to a device: a too-long extension cord lying on the ground the whole way, from under the anchor's foot
        /// <paramref name="basePt"/> to <paramref name="device"/> (owner, sitting 2026-11-08 12:20 PM: "Items should connect to the bottom of a
        /// power pole (beneath its base), not run a line up to the top of the power pole"; it used to hang from the crossarm insulator and then
        /// lie down, shots 121837/121857). The run is a <see cref="LooseRun"/> kept no further up the screen than the higher of its two ends plus
        /// <see cref="DropRise"/> (ground up-screen of those is behind the pole: a run wandering there read as a cord strung from the crossarm),
        /// else any open run, else one under a wall (vanilla wires a lamp indoors to a pole outside: the cord goes in under the wall, as floor cords
        /// do), else a shallow bow. Never null; <see cref="FallenLay.GroundFrom"/> is 0 (all of it on the ground) and it ends exactly on the device.
        /// </summary>
        public static FallenLay LayFootDrop(P2 basePt, P2 device, int seed, Func<int, int, bool> walkable)
        {
            var lay = new FallenLay();
            double dist = P2.Dist(basePt, device);
            Func<P2, bool> open = g => walkable((int)Math.Floor(g.X), (int)Math.Floor(g.Z));
            double cap = Math.Max(basePt.Z, device.Z) + DropRise;
            List<P2> run = dist < 0.3 ? null
                : LooseRun(basePt, device, seed, g => g.Z <= cap && open(g)) ?? LooseRun(basePt, device, seed, open) ?? LooseRun(basePt, device, seed, _ => true);
            if (run == null || run.Count < 2)
            {
                // a device right at the foot (or nothing lies): a shallow bow, to one side
                run = new List<P2>();
                double nx = dist < 1e-6 ? 0 : -(device.Z - basePt.Z) / dist, nz = dist < 1e-6 ? 0 : (device.X - basePt.X) / dist;
                double bow = (U(seed, 33) < 0.5 ? -1 : 1) * Math.Min(0.25, 0.2 * dist + 0.05);
                int n = Math.Max(4, (int)Math.Ceiling(dist / 0.06));
                for (int i = 0; i <= n; i++)
                {
                    double t = i / (double)n, k = 4 * t * (1 - t) * bow;
                    run.Add(new P2(basePt.X + (device.X - basePt.X) * t + nx * k, basePt.Z + (device.Z - basePt.Z) * t + nz * k));
                }
            }
            run[0] = basePt;
            run[run.Count - 1] = device;
            lay.Pts.AddRange(run);
            lay.GroundFrom = 0;
            lay.Tip = lay.TipNow = device;
            return lay;
        }

        /// <summary>The least a loose run lies, as a share of the ground it covers: under it a draw reads as a rod laid there.</summary>
        private const double LooseMin = 1.32;

        /// <summary>How far up the screen past the higher of its touchdown and its device a drop's ground run may wander, cells.</summary>
        public const double DropRise = 0.35;

        /// <summary>
        /// A loose cord lying on the ground from <paramref name="from"/> to <paramref name="to"/>, 1.5-1.9x as long as the distance plus a little:
        /// its heading bends by a curvature made of two slow waves of uneven length, so it swings in wide arcs of uneven size, drawn gently toward
        /// the far end; the whole lay is then turned and scaled about its start so it ends exactly there, which keeps every bend (steering it in
        /// hard flattened the last stretch into a straight). Owner, 2026-11-07 7:07 PM: "cords take slowly curving paths rather than straight
        /// lines often: what they avoid are sharp curves unless they must", so the bends are wide (radius mostly over a cell) and a long gentle
        /// sweep is kept; only a dead-straight stretch over 2.2 cells gets a wide, shallow bow. Up to twelve draws: none whose cord crosses an
        /// unwalkable cell, none that loops round its own end or coils on it (the doorway lesson: a coil at an end reads as more cables), the
        /// first with no dead-straight stretch, else the least straight. Null when no draw lies on open ground.
        /// </summary>
        public static List<P2> LooseRun(P2 from, P2 to, int seed, Func<P2, bool> open, double ds = 0.05)
        {
            double dist = P2.Dist(from, to);
            if (dist < 1e-6) return null;
            double baseA = Math.Atan2(to.Z - from.Z, to.X - from.X);
            int salt = 200;
            Func<double> rnd = () => U(seed, salt++);
            List<P2> best = null;
            double bestStraight = double.MaxValue, nearEnd = Math.Min(0.75, 0.4 * dist);
            var pts = new List<P2>();
            var hs = new List<double>();
            for (int attempt = 0; attempt < 24 && (attempt < 12 || best == null); attempt++)
            {
                int sgn = rnd() < 0.5 ? -1 : 1;
                // the later draws, only when none of the first twelve lay clear: a shorter, gentler cord for a tight spot
                double tight = attempt < 12 ? 1 : 0.7;
                double A = (0.75 + 0.35 * rnd()) * tight, l1 = 3.2 + 1.4 * rnd(), l2 = 5.5 + 2.5 * rnd(), p1 = 6.283 * rnd(), p2 = 6.283 * rnd();
                double want = attempt < 12 ? dist * (1.55 + 0.35 * rnd()) + 0.8 : dist * (1.4 + 0.2 * rnd()) + 0.4;
                double h = baseA + sgn * (0.5 + 0.5 * rnd()), x = from.X, z = from.Z, L = 0;
                pts.Clear(); hs.Clear();
                pts.Add(from); hs.Add(h);
                while (L < want)
                {
                    double err = WrapPi(Math.Atan2(to.Z - z, to.X - x) - h);
                    h += (A * (0.65 * Math.Sin(6.283 * L / l1 + p1) + 0.35 * Math.Sin(6.283 * L / l2 + p2)) + 0.45 * err) * ds;
                    x += ds * Math.Cos(h); z += ds * Math.Sin(h); L += ds;
                    pts.Add(new P2(x, z)); hs.Add(h);
                }
                double ex = x - from.X, ez = z - from.Z, el = Math.Sqrt(ex * ex + ez * ez);
                if (el < 1e-6) continue;
                double sc = dist / el;
                if (sc < 0.75 || sc > (attempt < 12 ? 1.35 : 1.8) || L * sc < LooseMin * dist) continue;
                double rot = baseA - Math.Atan2(ez, ex), c = Math.Cos(rot), sn = Math.Sin(rot);
                var o = new List<P2>(pts.Count);
                bool ok = true;
                int n = pts.Count, tail = (int)(1.0 / ds);
                for (int i = 0; i < n && ok; i++)
                {
                    double px = pts[i].X - from.X, pz = pts[i].Z - from.Z;
                    var q = i == n - 1 ? to : new P2(from.X + sc * (px * c - pz * sn), from.Z + sc * (px * sn + pz * c));
                    if (i < n - tail && P2.Dist(q, to) < nearEnd) ok = false;   // it comes back round its own end
                    else if (!open(q)) ok = false;
                    o.Add(q);
                }
                if (!ok) continue;
                if (Math.Abs(hs[n - 1] - hs[Math.Max(0, n - 1 - (int)(1.6 / ds))]) > 4.2) continue;   // a coil on its own end
                for (int b = 0; b < 5; b++)
                {
                    if (StraightAt(o, DeadStraight, out int i0, out int i1) <= 2.2) break;
                    o = Bowed(o, i0, i1, rnd, open) ?? o;
                }
                double st = LongestStraight(o, DeadStraight);
                if (st < bestStraight) { bestStraight = st; best = new List<P2>(o); }
                if (st <= 2.2) break;
            }
            if (best != null) return best;
            // a short run that no draw lays clear of its own end: one wide, lazy arc to whichever side is open
            double ux = (to.X - from.X) / dist, uz = (to.Z - from.Z) / dist, b0 = Math.Max(0.35, 0.45 * dist) * (rnd() < 0.5 ? -1 : 1);
            for (int side = 0; side < 2; side++, b0 = -b0)
            {
                var arc = new List<P2>();
                int m = Math.Max(8, (int)(dist / ds));
                bool ok = true;
                for (int i = 0; i <= m && ok; i++)
                {
                    double t = i / (double)m, off = b0 * Math.Sin(Math.PI * t);
                    var q = i == m ? to : new P2(from.X + ux * dist * t - uz * off, from.Z + uz * dist * t + ux * off);
                    ok = open(q);
                    arc.Add(q);
                }
                if (ok) return arc;
            }
            return null;
        }

        /// <summary>The longest stretch of a dense polyline (points a twentieth of a cell apart) within <paramref name="tol"/> of its chord, and its ends.</summary>
        private static double StraightAt(List<P2> p, double tol, out int i0, out int i1)
        {
            double best = 0; i0 = i1 = 0;
            for (int i = 0; i < p.Count; i += 2)
                for (int j = i + 12; j < p.Count; j += 2)
                {
                    double L = P2.Dist(p[i], p[j]);
                    if (L < 0.01) break;
                    bool ok = true;
                    for (int m = i + 1; m < j && ok; m += 2)
                        ok = Math.Abs((p[m].X - p[i].X) * (p[j].Z - p[i].Z) - (p[m].Z - p[i].Z) * (p[j].X - p[i].X)) / L <= tol;
                    if (!ok) break;
                    if (L > best) { best = L; i0 = i; i1 = j; }
                }
            return best;
        }

        /// <summary>A soft bow across the stretch <paramref name="i0"/>..<paramref name="i1"/> (sin squared, so it joins the cord on either side
        /// without a corner), to whichever side lies on open ground; null when neither does.</summary>
        private static List<P2> Bowed(List<P2> p, int i0, int i1, Func<double> rnd, Func<P2, bool> open)
        {
            double L = P2.Dist(p[i0], p[i1]);
            if (L < 1e-6 || i1 <= i0) return null;
            double nx = -(p[i1].Z - p[i0].Z) / L, nz = (p[i1].X - p[i0].X) / L;
            double amp = (0.22 + 0.13 * rnd()) * Math.Min(1, L / 3) * (rnd() < 0.5 ? -1 : 1);
            for (int side = 0; side < 2; side++, amp = -amp)
            {
                var o = new List<P2>(p);
                bool ok = true;
                for (int m = i0; m <= i1 && ok; m++)
                {
                    double t = (m - i0) / (double)(i1 - i0), w = Math.Sin(Math.PI * t);
                    o[m] = new P2(p[m].X + nx * amp * w * w, p[m].Z + nz * amp * w * w);
                    ok = open(o[m]);
                }
                if (ok) return o;
            }
            return null;
        }

        /// <summary>Within this of its chord a stretch is dead straight, a rod (a gentle sweep bends further than this over 2 cells).</summary>
        public const double DeadStraight = 0.06;

        private static double WrapPi(double a)
        {
            while (a > Math.PI) a -= 2 * Math.PI;
            while (a < -Math.PI) a += 2 * Math.PI;
            return a;
        }

        /// <summary>The longest stretch of <paramref name="pts"/> whose points all lie within <paramref name="tol"/> cell of its own chord
        /// (ralph/live/lab_straight.py's measure of a rod).</summary>
        public static double LongestStraight(List<P2> pts, double tol)
        {
            var q = new List<P2>();
            for (int i = 1; i < pts.Count; i++)
            {
                int n = Math.Max(1, (int)(P2.Dist(pts[i - 1], pts[i]) / 0.1));
                for (int j = 0; j < n; j++) q.Add(P2.Lerp(pts[i - 1], pts[i], j / (double)n));
            }
            if (pts.Count > 0) q.Add(pts[pts.Count - 1]);
            double best = 0;
            for (int i = 0; i < q.Count; i += 3)
                for (int j = i + 10; j < q.Count; j += 3)
                {
                    double L = P2.Dist(q[i], q[j]);
                    if (L < 0.01) break;
                    bool ok = true;
                    for (int m = i + 1; m < j && ok; m += 2)
                        ok = Math.Abs((q[m].X - q[i].X) * (q[j].Z - q[i].Z) - (q[m].Z - q[i].Z) * (q[j].X - q[i].X)) / L <= tol;
                    if (!ok) break;
                    best = Math.Max(best, L);
                }
            return best;
        }

        /// <summary>The points of <paramref name="l"/> that lie on the ground: the only ones a pawn can touch (GPT pre-release
        /// C3: the hanging part's points are screen positions lifted by the insulator height, i.e. thin air north of the mast).</summary>
        public static IEnumerable<P2> GroundPts(FallenLay l)
        {
            if (l.GroundFrom < 0) yield break;
            for (int i = l.GroundFrom; i < l.Pts.Count; i++) yield return l.Pts[i];
        }

        /// <summary>Is point <paramref name="i"/> of the fallen cable lying on the ground (drawn under pawns) rather than
        /// hanging from the insulator (drawn at the span altitude)? GPT pre-release C4.</summary>
        public static bool FallenPointOnGround(FallenLay l, int i) => l.GroundFrom >= 0 && i >= l.GroundFrom;

        /// <summary>FALLEN_WIRE_SHOCK_1 knockback direction (GPT pre-release C6). The preferred direction is straight away from the
        /// live end (<paramref name="awayX"/>, <paramref name="awayZ"/>, any length; zero = none); on a pawn mid-strand that runs
        /// ALONG the wire into the next contact cell, so the eight neighbours are tried in order of turn from it (0, +-45, +-90,
        /// +-135, 180 degrees) and the first whose first step <paramref name="free"/> accepts (standable, not itself on a live
        /// wire) wins: in practice the pawn is thrown off the wire sideways. Null when no neighbour is free.</summary>
        public static (int dx, int dz)? KnockbackDir(int awayX, int awayZ, int fallbackIndex, Func<int, int, bool> free)
        {
            int sx = Math.Sign(awayX), sz = Math.Sign(awayZ);
            int start = 0;
            if (sx == 0 && sz == 0) start = ((fallbackIndex % 8) + 8) % 8;
            else for (int i = 0; i < 8; i++) if (Ring8[i].dx == sx && Ring8[i].dz == sz) { start = i; break; }
            for (int t = 0; t < 8; t++)
            {
                int turn = t == 0 ? 0 : (t % 2 == 1 ? (t + 1) / 2 : -(t / 2));     // 0, +1, -1, +2, -2, +3, -3, +4
                var d = Ring8[((start + turn) % 8 + 8) % 8];
                if (free(d.dx, d.dz)) return d;
            }
            return null;
        }

        /// <summary>The eight neighbour steps in ring order (each 45 degrees from the last).</summary>
        public static readonly (int dx, int dz)[] Ring8 = { (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1) };

        /// <summary>Sideways gap between neighbouring fallen wires at the break (cells). PROVISIONAL.</summary>
        public const double FallenSpread = 1.15;

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

        // ------------------------------------------------------------------ kinetic blasts sway, never cut (owner Q3, 2026-10-06)
        /// <summary>What a blast does to the spans it reaches: nothing, cut (wound them), or sway (a push wave, no wound).</summary>
        public enum BlastKind { None, Cut, Sway }

        /// <summary>
        /// The blast verdict. A kinetic blast (Kinetic Arms' RM_KineticBlastExtension marker) NEVER cuts: it sways when
        /// <paramref name="kineticSway"/> is on, otherwise does nothing. Every other harmful blast keeps the design 2.6
        /// rule: cut when the setting is on and the damage is positive.
        /// </summary>
        public static bool ExplodeWantsKinetic(string[] parts) => parts.Length > 4 && parts[4] == "kinetic";

        public static BlastKind BlastKindFor(bool harmsHealth, bool kinetic, double damage, bool explosionsCut, bool kineticSway)
        {
            if (!harmsHealth) return BlastKind.None;
            if (kinetic) return kineticSway ? BlastKind.Sway : BlastKind.None;
            return explosionsCut && damage > 0 ? BlastKind.Cut : BlastKind.None;
        }

        /// <summary>One span's answer to one blast: its hp after, whether it parted, and the sway kick (0..1) and side.</summary>
        public struct SpanBlast
        {
            public bool Hit, Cut;
            public double Hp, Kick;
            /// <summary>+1 / -1: which side of the span (along its left normal) the wave pushes it to; away from the blast.</summary>
            public int Side;
        }

        /// <summary>Weakest kick a span inside the radius gets (its far edge); the centre of the blast gives 1.</summary>
        public const double BlastKickFloor = 0.35;

        public static SpanBlast BlastSpan(P2 a, P2 b, P2 c, double radius, double hp, double damage, BlastKind kind)
        {
            var r = new SpanBlast { Hp = hp };
            if (kind == BlastKind.None || !SpanHit(a, b, c, radius)) return r;
            r.Hit = true;
            if (kind == BlastKind.Cut)
            {
                // design 2.6 "hp -= damage x falloff" (GSS_RESTRING_DECIDE_FREE_INSTANT_SPLICE, C13): vanilla's own explosion
                // falloff (Explosion.GetDamageAmountAt), full damage at the centre down to 20% at the edge of the radius
                r.Hp = hp - damage * BlastCutFalloff(P2.Dist(P2.Lerp(a, b, ClosestT(a, b, c)), c), radius);
                r.Cut = r.Hp <= 0;
                return r;
            }
            double d = P2.Dist(P2.Lerp(a, b, ClosestT(a, b, c)), c);
            r.Kick = radius > 1e-9 ? Math.Max(BlastKickFloor, Math.Min(1.0, 1.0 - d / radius)) : 1.0;
            double cross = (b.X - a.X) * (c.Z - a.Z) - (b.Z - a.Z) * (c.X - a.X);
            r.Side = cross > 0 ? -1 : 1; // blast on the left normal's side pushes the wire to the right, and back
            return r;
        }

        /// <summary>The share of a cutting blast's damage a span takes at distance <paramref name="d"/> from the centre:
        /// vanilla Explosion.GetDamageAmountAt's Lerp(1, 0.2, d / radius).</summary>
        public static double BlastCutFalloff(double d, double radius)
        {
            if (radius <= 1e-9) return 1.0;
            double t = Math.Max(0, Math.Min(1, d / radius));
            return 1.0 + (0.2 - 1.0) * t;
        }

        /// <summary>Design 2.6: re-stringing a cut span is a 300-tick pawn job, scaled by the worker's ConstructionSpeed.</summary>
        public const int RestringBaseTicks = 300;
        public static int RestringTicks(double constructionSpeed) => (int)Math.Ceiling(RestringBaseTicks / Math.Max(0.1, constructionSpeed));

        /// <summary>Does a pawn standing on a live fallen wire take the shock? Flesh, alive, not already knocked out, and NOT the
        /// colonist on the re-string job: design 2.6 sends him to the cut, where the live half lies, to handle that wire
        /// (GSS_RESTRING_DIAGNOSE_FIXER_GETS_ZAPPED, L1 2026-10-15: the fixer was knocked out 2/2).
        /// <paramref name="restringing"/> is true only for the worker on THAT job standing on a wire of the cut his job splices
        /// (<see cref="LayTouches"/> over that cut's fallen halves); any other live wire shocks him like anyone else.</summary>
        public static bool ShockTakes(bool flesh, bool dead, bool alreadyOut, bool restringing) => flesh && !dead && !alreadyOut && !restringing;

        /// <summary>Does cell (<paramref name="x"/>, <paramref name="z"/>) lie under the GROUNDED part of fallen cable
        /// <paramref name="l"/> (the same points <see cref="GroundPts"/> gives the shock contacts, the tip included)?</summary>
        public static bool LayTouches(FallenLay l, int x, int z)
        {
            foreach (P2 p in GroundPts(l))
                if ((int)Math.Floor(p.X) == x && (int)Math.Floor(p.Z) == z) return true;
            return false;
        }

        /// <summary>How long a blast-swayed span keeps moving (game ticks, 3 s).</summary>
        public const int BlastSwayTicks = 180;
        /// <summary>Peak blast displacement as a multiple of the wind-sway amplitude (a push wave beats a breeze).</summary>
        public const double BlastSwayGain = 2.5;

        /// <summary>
        /// Perpendicular offset of a point at fraction t along a span <paramref name="ageTicks"/> after a kinetic blast:
        /// thrown to <paramref name="side"/> at once, then a decaying swing back and forth that is exactly 0 at both
        /// insulators and from <see cref="BlastSwayTicks"/> on. Deterministic in its arguments (game-tick clock).
        /// </summary>
        public static double BlastSway(double t, int ageTicks, double kick, int side, double amp, int seed)
        {
            if (t <= 0 || t >= 1 || ageTicks < 0 || ageTicks >= BlastSwayTicks || kick <= 0 || amp <= 0) return 0;
            double f = ageTicks / (double)BlastSwayTicks;
            double period = 40 + 10 * U(seed, 5); // ticks per swing, per span
            double decay = Math.Exp(-3 * f) * (1 - f);
            return side * amp * BlastSwayGain * kick * Math.Sin(Math.PI * t) * decay * Math.Cos(2 * Math.PI * ageTicks / period);
        }

        // ------------------------------------------------------------------ the one-way power tap (design 2.7)
        /// <summary>
        /// Energy (watt-days) the clamp takes from the victim net this tick: at most rate x k, at most what the victim
        /// has to give (its own raw gain this tick + stored battery energy), never negative; 0 when taps are off or the
        /// "victim" is our own net. rawGainPerTick and stored are the VICTIM's, read without the tap's own debit;
        /// k = CompPower.WattsToWattDaysPerTick.
        /// </summary>
        public static double TapStolenPerTick(double rateW, double rawGainPerTick, double stored, double k, bool sameNet, bool enabled)
        {
            // GPT review #21: !(x > 0) also rejects NaN; a non-finite rate or gain never reaches the power net
            if (!enabled || sameNet || !(rateW > 0) || double.IsInfinity(rateW) || double.IsNaN(rawGainPerTick) || double.IsNaN(stored)) return 0;
            double avail = rawGainPerTick + Math.Max(0, stored);
            if (avail <= 0) return 0;
            return Math.Min(rateW * k, avail);
        }

        /// <summary>GPT source read 2026-10-06 A1/A2: as above, but (A1) what other taps already took from this victim THIS
        /// tick is no longer on offer, so several taps share one surplus instead of each claiming all of it; and (A2) a
        /// clamp switched off or broken down (<paramref name="working"/> false) takes nothing at all.</summary>
        public static double TapStolenPerTick(double rateW, double rawGainPerTick, double stored, double k, bool sameNet, bool enabled,
                                              double takenThisTickByOthers, bool working)
        {
            if (!working) return 0;
            return TapStolenPerTick(rateW, rawGainPerTick - Math.Max(0, takenThisTickByOthers), stored, k, sameNet, enabled);
        }

        // ------------------------------------------------------------------ caught power theft (POWER_THEFT_BUILD_SLOW_GOODWILL_LEAK)
        /// <summary>Owner 2026-10-10: "If caught, steady goodwill drain (like living too close to a settlement)". Does this
        /// witness catch the clamp? Awake, not downed, not held by us, within sightRange cells (Euclidean), with line of sight.</summary>
        public static bool TheftSpotted(double dist, double sightRange, bool lineOfSight, bool awakeAndUp, bool heldByThief)
        {
            if (!(sightRange > 0) || double.IsNaN(dist) || heldByThief || !awakeAndUp || !lineOfSight) return false;
            return dist <= sightRange;
        }

        /// <summary>The steady leak: a caught clamp accrues the ticks it spent DRAINING (idle clamps accrue nothing) and is
        /// charged perDay goodwill for each whole day of draining, the remainder carried. Returns the goodwill change
        /// (zero or negative). perDay 0 or below charges nothing but still keeps time.</summary>
        public static int TheftGoodwillAccrue(ref int drainTicks, int ticks, bool draining, int perDay, int ticksPerDay)
        {
            if (!draining || ticks <= 0 || ticksPerDay <= 0) return 0;
            drainTicks += ticks;
            int days = drainTicks / ticksPerDay;
            if (days <= 0) return 0;
            drainTicks -= days * ticksPerDay;
            return perDay > 0 ? -days * perDay : 0;
        }

        /// <summary>Wire sway mode vs the game's plant-sway preference (WireSwayMode: 0 Auto, 1 CPU = Always, 2 Off): Auto
        /// sways only when the preference is on, Always regardless, Off never.</summary>
        public static bool WireSwayPrefAllows(int mode, bool plantSwayPref) => mode == 1 || (mode == 0 && plantSwayPref);

        // ------------------------------------------------------------------ the power-tap clamp's pose (v3 art, 2026-10-11)
        /// <summary>How far from the tap cell's centre, toward the bitten neighbour, the jaws close. Their cord's last
        /// <c>CordBuilder.CentroidApproach</c> (0.2) cell runs dead straight along the cardinal axis into the centre, so a
        /// bite inside that stretch lands on THEIR wire itself, never on the node where our cord meets it.</summary>
        public const double TapBiteInset = 0.12;

        /// <summary>
        /// Where and how the v3 clamp art (owner 2026-10-11: "it needs to look like it's clamped vertically DOWN onto the wire
        /// itself") is drawn. The art's bite is its canvas centre, the wire it grips runs along art +x, and the upright handles
        /// rise toward art +y (up-screen). So the jaws go on the bitten cord <see cref="TapBiteInset"/> in from the tap's centre,
        /// and the art turns only to lay its jaw axis along that cord: an east-west cord draws the art upright (angle 0,
        /// handles up-screen whichever side our cord comes from: the camera's own perspective of an upright clamp); a
        /// north-south cord turns it a quarter, its handles toward the side our cord is NOT on (east when ours is straight
        /// through). <paramref name="angleDeg"/> is a rotation about +y in Unity's AngleAxis sense, which takes art +x to
        /// (cos, -sin) and art +y to (sin, cos) in (x, z). <paramref name="jawAxis"/> / <paramref name="handles"/> are those two
        /// images, for checks.
        /// </summary>
        public static void TapClampPose(P2 home, P2 toVictim, P2 toOurs, out P2 bite, out double angleDeg, out P2 jawAxis, out P2 handles)
        {
            double dx = toVictim.X, dz = toVictim.Z;
            if (dx * dx + dz * dz < 1e-8) { dx = -toOurs.X; dz = -toOurs.Z; }
            if (dx * dx + dz * dz < 1e-8) dx = 1;
            P2 d = Math.Abs(dx) >= Math.Abs(dz) ? new P2(Math.Sign(dx), 0) : new P2(0, Math.Sign(dz));
            bite = new P2(home.X + d.X * TapBiteInset, home.Z + d.Z * TapBiteInset);
            if (d.Z == 0) angleDeg = 0;
            else angleDeg = toOurs.X > 1e-6 ? -90 : 90;
            double r = angleDeg * Math.PI / 180.0;
            jawAxis = new P2(Math.Round(Math.Cos(r), 9), Math.Round(-Math.Sin(r), 9));
            handles = new P2(Math.Round(Math.Sin(r), 9), Math.Round(Math.Cos(r), 9));
        }
    }
}
