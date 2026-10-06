// Owner code round 6 (2026-10-04): the offline, load-bearing checks. Each property carries a planted fault (the round-5
// behaviour, or a plausible wrong rule) that must turn it red.
//   draw     "firehose is shown as going OVER the hanging power lines (oops!)": overhead materials draw after every hose
//            material (render queue) AND above it (altitude)
//   length   "the hose should go 40 cells by itself already though, by default", old settings files migrate
//   relay    "how does the player go farther? Maybe they place another reel out there to connect to?"
//   lamp     "I don't see the standing lamps changing their look when I change the cable"
using System;
using System.Collections.Generic;
using System.Linq;
using RimMandrake.GimmeSomeSlack.Aerial;
using RimMandrake.GimmeSomeSlack.Core;
using RimMandrake.GimmeSomeSlack.Hose;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class ReviewRound6Checks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "review6: " + msg);

        private static bool Near(double a, double b, double eps = 1e-4) => Math.Abs(a - b) < eps;

        // ---------------------------------------------------------------- draw order
        private static bool OverheadAboveGround(int hoseQ, int clampQ, int overheadQ, double hoseTop, double spanAlt, double topAlt) =>
            overheadQ > hoseQ && overheadQ > clampQ && spanAlt > hoseTop && topAlt > hoseTop;

        private static void Draw()
        {
            foreach (int strand in new[] { 3000, 2950, 3100 })
            {
                int h = DrawOrder.HoseQueue(strand), c = DrawOrder.TapClampQueue(strand), o = DrawOrder.OverheadQueue(strand);
                double top = DrawOrder.HoseTopAltitude(HoseMath.CrossBand, HoseMath.CrossRanks);
                Check(OverheadAboveGround(h, c, o, top, DrawOrder.SpanAltitude, DrawOrder.TopAltitude),
                    "strand queue " + strand + ": overhead queue " + o + " > hose " + h + " and clamp " + c + "; span alt " +
                    DrawOrder.SpanAltitude.ToString("0.000") + " and head alt " + DrawOrder.TopAltitude.ToString("0.000") + " > hose top " + top.ToString("0.000"));
                Check(h > strand + 2, "strand queue " + strand + ": the hose still draws over the cord faces (strand + 2)");
            }
            // vanilla's numbers (RimSage, Verse.Altitudes): PawnState+5 inc = 25*0.36585367 + 5*0.03658537
            Check(Near(DrawOrder.SpanAltitude, 9.32927) && Near(DrawOrder.Alt(DrawOrder.LayerConduits), 1.82927),
                "altitudes are vanilla's: span " + DrawOrder.SpanAltitude.ToString("0.00000") + ", Conduits " + DrawOrder.Alt(DrawOrder.LayerConduits).ToString("0.00000"));
            Check(DrawOrder.HoseTopAltitude(HoseMath.CrossBand, HoseMath.CrossRanks) < DrawOrder.Alt(DrawOrder.LayerHose + 1),
                "the top hose band stays below the next altitude layer (DoorMoveable)");
            // 2026-10-05: the hose's lowest piece (its own shadow strip, 0.0004 under the strand) sits above vanilla's sun-shadow
            // quads, so its depth pre-pass hides wall shadows (owner screenshot: hard rectangles across the hose)
            Check(DrawOrder.Alt(DrawOrder.LayerHose) + DrawOrder.HoseBaseLift - 0.0008 > DrawOrder.Alt(DrawOrder.LayerShadows),
                "the hose band sits above the Shadows layer");
            // can-fail: round 5 -- the span cable and pole heads were plain Transparent (queue 3000), the hose 3003
            Check(!OverheadAboveGround(3003, 3004, 3000, DrawOrder.HoseTopAltitude(HoseMath.CrossBand, HoseMath.CrossRanks), DrawOrder.SpanAltitude, DrawOrder.TopAltitude),
                "can-fail: the round-5 queues (overhead 3000 < hose 3003) are caught although the altitudes were right");
        }

        // ---------------------------------------------------------------- hose length
        private static CordWorld Open(int w, int h) => new CordWorld(w, h);

        private static void Length()
        {
            Check(Near(HoseMath.DefaultMaxLength, 40), "the shipped hose length is 40 cells (" + HoseMath.DefaultMaxLength + ")");
            var cases = new[] { (30.0, 0, 40.0), (36.0, 0, 36.0), (20.0, 0, 20.0), (30.0, 1, 30.0), (40.0, 1, 40.0), (55.0, 1, 55.0) };
            int ok = cases.Count(c => Near(HoseMath.MigrateMaxLength(c.Item1, c.Item2), c.Item3));
            Check(ok == cases.Length, "settings migration: an untouched old default 30 -> 40, every chosen length kept (" + ok + "/" + cases.Length + ")");
            int naive = cases.Count(c => Near(HoseMath.DefaultMaxLength, c.Item3));
            Check(naive < cases.Length, "can-fail: 'always the new default' is right in only " + naive + "/" + cases.Length + " (it throws away a chosen 36)");
            CordWorld w = Open(80, 20);
            var reel = new Cell(2, 10);
            Check(HoseMath.CheckInstall(w, reel, new Cell(2 + 38, 10), HoseMath.DefaultMaxLength) == null,
                "a 38-cell straight run fits a 40-cell hose (38 x 1.05 = 39.9)");
            Check(HoseMath.CheckInstall(w, reel, new Cell(2 + 39, 10), HoseMath.DefaultMaxLength) == "route too long",
                "a 39-cell run does not (39 x 1.05 = 40.95): the 5% margin stays");
            Check(HoseMath.CheckInstall(w, reel, new Cell(2 + 38, 10), HoseMath.OldDefaultMaxLength) != null,
                "can-fail: the old 30-cell hose refuses the 38-cell run");
        }

        // ---------------------------------------------------------------- relay
        private static void Relay()
        {
            var r = new HoseReelRect(10, 10, 2, 2);
            List<Cell> ins = HoseRelay.IntakeCells(r);
            bool sides = ins.Count == 8 && ins.All(c => !r.Contains(c)) &&
                         ins.All(c => (c.X >= 10 && c.X <= 11) != (c.Z >= 10 && c.Z <= 11));      // exactly one axis inside: a side, not a corner
            Check(sides, "a 2x2 reel has 8 intake cells, all across a side edge, none inside, no corner (" + ins.Count + ")");
            CordWorld w = Open(60, 40);
            Func<Cell, bool> walk = c => w.InBounds(c) && w.IsWalkable(c);
            Check(HoseRelay.TryIntake(r, new V2(0, 10.6), walk, out Cell west) && west.X == 9 && HoseRelay.SideInto(r, west).X == 1,
                "a hose from the west ends on the relay's west side (" + west.X + "," + west.Z + ")");
            V2 p = HoseRelay.IntakePoint(r, west);
            Check(Near(p.X, 10) && p.Z > 10 && p.Z < 12, "the hose end sits ON the relay's edge (" + p.X + "," + p.Z + ")");
            w.SetBlocked(new Cell(9, 10), BlockKind.Wall);
            w.SetBlocked(new Cell(9, 11), BlockKind.Wall);
            Check(HoseRelay.TryIntake(r, new V2(0, 10.6), walk, out Cell other) && other.X != 9,
                "west side walled: the hose takes the next nearest free side (" + other.X + "," + other.Z + ")");
            var all = new List<HoseReelRect> { new HoseReelRect(0, 10, 2, 2), r, new HoseReelRect(30, 10, 2, 2) };
            Check(HoseRelay.RelayOf(new Cell(12, 10), all, 0) == 1 && HoseRelay.RelayOf(new Cell(12, 12), all, 0) == -1 &&
                  HoseRelay.RelayOf(new Cell(2, 10), all, 0) == -1,
                "a free end on an intake feeds that reel; a corner cell or its own reel's side feeds nothing");
            // loops: 0 -> 1 -> 2 ; laying 2 -> 0 closes a ring, 2 -> 3 does not
            int[] next = { 1, 2, -1, -1 };
            Check(HoseRelay.WouldLoop(2, 0, i => next[i]) && !HoseRelay.WouldLoop(2, 3, i => next[i]) && !HoseRelay.WouldLoop(3, 0, i => next[i]),
                "a chain may not loop back (2->0 refused, 2->3 and 3->0 fine)");
            Check(HoseRelay.Chain(0, i => next[i]).SequenceEqual(new[] { 0, 1, 2 }), "the chain from the first reel runs 0, 1, 2");
            int[] ring = { 1, 0 };
            Check(HoseRelay.Chain(0, i => ring[i]).Count == 2, "can-fail: a ring (if one were ever saved) stops, it does not spin");
            // the review station: three 2x2 reels in a row, 32 cells apart -- 64+ cells end to end, beyond one 40-cell hose
            CordWorld f = Open(100, 20);
            var A = new HoseReelRect(1, 8, 2, 2);
            var B = new HoseReelRect(33, 8, 2, 2);
            var C = new HoseReelRect(65, 8, 2, 2);
            Func<Cell, bool> fw = c => f.InBounds(c) && f.IsWalkable(c);
            HoseRelay.TryIntake(B, A.Mouth, fw, out Cell ab);
            HoseRelay.TryIntake(C, B.Mouth, fw, out Cell bc);
            string w1 = HoseMath.CheckInstall(f, A, ab, HoseMath.DefaultMaxLength), w2 = HoseMath.CheckInstall(f, B, bc, HoseMath.DefaultMaxLength);
            Check(w1 == null && w2 == null, "relay station: hose 1 (A -> B intake " + ab.X + "," + ab.Z + ") and hose 2 (B -> C intake " + bc.X + "," + bc.Z + ") each fit 40 cells: " + (w1 ?? "ok") + " / " + (w2 ?? "ok"));
            HoseRelay.TryIntake(C, A.Mouth, fw, out Cell ac);
            Check(HoseMath.CheckInstall(f, A, ac, HoseMath.DefaultMaxLength) != null && V2.Dist(A.Mouth, C.Centre) > HoseMath.DefaultMaxLength,
                "can-fail: one hose cannot reach the far reel (" + V2.Dist(A.Mouth, C.Centre).ToString("0.0") + " cells): only the chain does");
        }

        // ---------------------------------------------------------------- lamps follow their run
        private static void Lamp()
        {
            const string D = "Scrapper";
            // (lamp look, run look before, expected follow)
            var cases = new (string, string, bool)[]
            {
                (null, "Industrial", true),        // vanilla-art lamp on a styled run: follows
                ("Industrial", "Industrial", true), // built in the run's look: follows
                ("Futuristic", "Industrial", false),// given its own look: kept
                (D, null, true),                    // unstyled run draws the default: a default-look lamp follows
                ("Modern", null, false),            // unstyled run, a Modern lamp: deliberate, kept
                (null, null, true)
            };
            int ok = cases.Count(c => ConduitStyles.LampFollowsRun(c.Item1, c.Item2, D) == c.Item3);
            Check(ok == cases.Length, "a restyle repaints the run's lamps unless one was styled on purpose (" + ok + "/" + cases.Length + ")");
            int never = cases.Count(c => !c.Item3), always = cases.Count(c => c.Item3);
            Check(never < cases.Length && always < cases.Length,
                "can-fail: round 5's 'lamps never follow' is right in " + never + "/" + cases.Length + ", 'always follow' in " + always + "/" + cases.Length);
            // a bridge repaints the LOSING run's lamps by the same rule, but never stamps an unstyled (older-save) lamp
            Check(ConduitStyles.LampFollowsRun("Modern", "Modern", D, restyle: false) && !ConduitStyles.LampFollowsRun(null, "Modern", D, restyle: false) &&
                  !ConduitStyles.LampFollowsRun("Futuristic", "Modern", D, restyle: false),
                "bridge: the loser's Modern lamp turns with it, a vanilla-art lamp stores nothing, a deliberately different lamp is kept");
            Check(ConduitStyles.IsLampDef("StandingLamp") && ConduitStyles.KeysFor("StandingLamp").Count == 4 &&
                  ConduitStyles.KeysFor("StandingLamp").All(AerialStyles.IsLook),
                "the floor lamp's Restyle offers exactly the four looks");
        }

        public static void Run()
        {
            Draw();
            Length();
            Relay();
            Lamp();
        }
    }
}
