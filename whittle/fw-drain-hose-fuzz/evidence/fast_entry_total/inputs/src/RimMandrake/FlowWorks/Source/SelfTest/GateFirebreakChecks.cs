// SUMP_TAR_FIRE_NETWORK_1 (SUMP_TAR_HYDROLOGY_1 ruling 5): "Lit tar propagates along connected liquid -- a lit canal burns to
// its gate, a lit pool to its edges. Gate placement is life-and-death craft." The front walk below is the one
// RM_LiquidFire.AdvanceFront/Maintain run (4-way, a square carries the front only when RM_FireMath.CarriesFront says so, each
// hop due RM_FireMath.FrontDue later), on a grid of tar squares and flow doors, with the seal verdict taken from the production
// RM_PitTrapMath.FlowDoorSeals. Every stop case carries a can-fail: the same walk with the gate rule left out must cross.
using System;
using System.Collections.Generic;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class GateFirebreakChecks
    {
        private static void Assert(bool cond, string msg)
        {
            if (!cond) throw new Exception(msg);
        }

        private const int TarTicksPerCell = 120;   // FlowWorks_Fluids.xml RM_Fluid_Tar fireFrontTicksPerCell

        // '.' bare ground, 'T' tar, 'S' shut sluice on tar, 's' lifted sluice on tar, 'G' grate (shut) on tar, 'g' grate lifted.
        private sealed class Net
        {
            public int W, H;
            public char[] C;
            public Net(params string[] rows)
            {
                H = rows.Length; W = rows[0].Length; C = new char[W * H];
                for (int z = 0; z < H; z++) for (int x = 0; x < W; x++) C[z * W + x] = rows[z][x];
            }
            public int I(int x, int z) => z * W + x;
            public bool Tar(int i) => C[i] != '.';
            public bool Sealed(int i)
            {
                char c = C[i];
                bool door = c == 'S' || c == 's' || c == 'G' || c == 'g';
                bool isSluice = c == 'S' || c == 's', lifted = c == 's' || c == 'g';
                return door && RM_PitTrapMath.FlowDoorSeals(isSluice, lifted);
            }
        }

        /// <summary>Run the front from the lit squares until nothing is pending; returns square -> tick it lit (-1 never).</summary>
        private static int[] Burn(Net n, bool gateRule, IEnumerable<int> lit, int[] litAt = null, int now = 0)
        {
            int[] at = litAt ?? Fill(n.C.Length, -1);
            var pend = new SortedSet<(int due, int i)>();
            var dueOf = new Dictionary<int, int>();
            Func<int, bool> carries = i => gateRule ? RM_FireMath.CarriesFront(n.Tar(i), n.Sealed(i)) : n.Tar(i);
            void Offer(int i, int due)
            {
                if (at[i] >= 0 || !carries(i)) return;
                if (dueOf.TryGetValue(i, out int old)) { if (due >= old) return; pend.Remove((old, i)); }
                dueOf[i] = due; pend.Add((due, i));
            }
            foreach (int i in lit) Offer(i, now);
            // Maintain's re-offer: every square already alight offers its wet neighbours (a gate lifted beside a fire)
            for (int i = 0; i < at.Length; i++)
                if (at[i] >= 0 && carries(i)) Neighbours(n, i, j => Offer(j, RM_FireMath.FrontDue(now, TarTicksPerCell, 1f)));
            int guard = 0;
            while (pend.Count > 0 && guard++ < 100000)
            {
                var (due, i) = pend.Min; pend.Remove(pend.Min); dueOf.Remove(i);
                if (at[i] >= 0 || !carries(i)) continue;
                at[i] = due;
                Neighbours(n, i, j => Offer(j, RM_FireMath.FrontDue(due, TarTicksPerCell, 1f)));
            }
            return at;
        }

        private static void Neighbours(Net n, int i, Action<int> f)
        {
            int x = i % n.W, z = i / n.W;
            if (x > 0) f(i - 1);
            if (x < n.W - 1) f(i + 1);
            if (z > 0) f(i - n.W);
            if (z < n.H - 1) f(i + n.W);
        }

        private static int[] Fill(int len, int v) { var a = new int[len]; for (int k = 0; k < len; k++) a[k] = v; return a; }

        private static int LitCount(int[] at) { int c = 0; foreach (int t in at) if (t >= 0) c++; return c; }

        public static void Run(Action<string, Action> Case)
        {
            Case("GateFirebreak_rule_truth_table", () =>
            {
                Assert(RM_FireMath.CarriesFront(true, false), "open tar carries the front");
                Assert(!RM_FireMath.CarriesFront(true, true), "a shut sluice on tar stops it");
                Assert(!RM_FireMath.CarriesFront(false, false) && !RM_FireMath.CarriesFront(false, true), "no burnable liquid, no front");
                // the seal verdict the fire reads is the flow kernel's: only a SHUT SLUICE seals; a grate never does
                Assert(RM_PitTrapMath.FlowDoorSeals(true, false), "shut sluice seals");
                Assert(!RM_PitTrapMath.FlowDoorSeals(true, true), "lifted sluice passes");
                Assert(!RM_PitTrapMath.FlowDoorSeals(false, false) && !RM_PitTrapMath.FlowDoorSeals(false, true), "a grate passes shut or lifted");
            });

            Case("GateFirebreak_canal_burns_to_its_gate_and_stops", () =>
            {
                var n = new Net("TTTTTTSTTTTT");
                int[] at = Burn(n, true, new[] { 0 });
                for (int x = 0; x < 6; x++) Assert(at[x] >= 0, "square " + x + " on the lit side burns");
                for (int x = 6; x < 12; x++) Assert(at[x] < 0, "square " + x + " at or past the shut gate stays dark: lit at " + at[x]);
                Assert(at[5] == 5 * TarTicksPerCell, "the front creeps a tar fuse's 120 ticks a square: square 5 lit at " + at[5]);
                // can-fail: the walk without the gate rule crosses the gate and burns the whole canal
                int[] naive = Burn(n, false, new[] { 0 });
                Assert(LitCount(naive) == 12, "can-fail: without the gate rule the whole canal burns, got " + LitCount(naive));
            });

            Case("GateFirebreak_lifted_sluice_and_grates_let_it_through", () =>
            {
                foreach (string row in new[] { "TTTTTTsTTTTT", "TTTTTTGTTTTT", "TTTTTTgTTTTT" })
                {
                    int[] at = Burn(new Net(row), true, new[] { 0 });
                    Assert(LitCount(at) == 12, row + ": the front runs through, lit " + LitCount(at));
                    Assert(at[11] > at[6] && at[6] > at[5], row + ": in order along the canal");
                }
            });

            Case("GateFirebreak_lifting_the_gate_mid_burn_lets_it_on", () =>
            {
                var n = new Net("TTTTTTSTTTTT");
                int[] at = Burn(n, true, new[] { 0 });
                Assert(LitCount(at) == 6, "held at the gate first: " + LitCount(at));
                n.C[6] = 's';   // a colonist lifts it while the near side still burns
                int now = 5000;
                at = Burn(n, true, new int[0], at, now);
                Assert(LitCount(at) == 12, "lifted, the burning neighbour relights the gate square and the front runs on: " + LitCount(at));
                Assert(at[6] > now && at[11] > at[6], "the far side lights after the lift, not before: gate " + at[6] + " end " + at[11]);
            });

            Case("GateFirebreak_dropping_the_gate_cuts_a_burning_square", () =>
            {
                // Maintain re-reads every burning square through BurnableFluidAt; a gate dropped onto one makes it carry nothing
                var n = new Net("TTTsTTT");
                Assert(RM_FireMath.CarriesFront(n.Tar(3), n.Sealed(3)), "lifted: the gate square burns");
                n.C[3] = 'S';
                Assert(!RM_FireMath.CarriesFront(n.Tar(3), n.Sealed(3)), "dropped: the re-read finds nothing to burn there, so it goes out");
            });

            Case("GateFirebreak_network_branches_each_gate_holds", () =>
            {
                // a moat with three arms off a lit trunk: west arm gated shut, east arm gated shut, south arm open
                var n = new Net(
                    "TTTSTTTTTSTTT",
                    "......T......",
                    "......T......",
                    "......T......");
                int[] at = Burn(n, true, new[] { n.I(6, 3) });   // lit at the far end of the south arm
                for (int x = 4; x <= 8; x++) Assert(at[n.I(x, 0)] >= 0, "trunk square " + x + " burns");
                for (int x = 0; x <= 3; x++) Assert(at[n.I(x, 0)] < 0, "west of its gate stays dark: " + x);
                for (int x = 9; x <= 12; x++) Assert(at[n.I(x, 0)] < 0, "east of its gate stays dark: " + x);
                Assert(LitCount(Burn(n, false, new[] { n.I(6, 3) })) == 16, "can-fail: without the rule every arm burns");
                // a pool's edges: a wide body with one shut sluice in a one-wide outlet; the outlet beyond stays dark
                var pool = new Net(
                    "TTTT....",
                    "TTTTSTTT",
                    "TTTT....");
                int[] p = Burn(pool, true, new[] { pool.I(0, 0) });
                Assert(LitCount(p) == 12, "the pool burns to its edges: " + LitCount(p));
                for (int x = 4; x < 8; x++) Assert(p[pool.I(x, 1)] < 0, "the outlet past the gate stays dark: " + x);
            });

            Case("GateFirebreak_call_site_in_the_fire", () =>
            {
                string lf = RiverSwitchFlipChecks.Src("RM_LiquidFire.cs");
                RiverSwitchFlipChecks.Has(lf,
                    @"public static FluidDef BurnableFluidAt\(Map map, RM_MapComponent_Excavation ex, IntVec3 c\) \{[^}]*\{[^}]*\}[^}]*\{[^}]*\{[^}]*\}[^}]*\}[^}]*\{[^}]*\}[^}]*return RM_FireMath\.CarriesFront\(f != null && f\.fireKind != RM_FluidFireKind\.None, RM_FlowDoorRules\.SealsLiquid\(map\.edificeGrid\[c\]\)\) \? f : null; \}",
                    "BurnableFluidAt answers through RM_FireMath.CarriesFront with the shut-sluice seal of the square");
                // every front step, re-offer and ignition reads that one predicate (no second, gate-blind burnable test)
                Assert(!System.Text.RegularExpressions.Regex.IsMatch(lf, @"fireKind != RM_FluidFireKind\.None \? f : null"),
                    "no gate-blind return of a burnable fluid is left");
                string fd = RiverSwitchFlipChecks.Src(System.IO.Path.Combine("Superdeep", "RM_FlowDoors.cs"));
                RiverSwitchFlipChecks.Has(fd, @"public static bool SealsLiquid\(Building edifice\) \{ Building_RM_FlowDoor door = edifice as Building_RM_FlowDoor; return door != null && RM_PitTrapMath\.FlowDoorSeals\(IsSluice\(door\.def\), door\.Open\); \}",
                    "the seal the fire reads is the flow kernel's shut-sluice verdict");
            });
        }
    }
}
