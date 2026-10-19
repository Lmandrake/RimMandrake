// TITAN_TRENCHES_WIRE_MIND_THE_GAP (owner, by card 2026-10-18: titans step over trenches narrower than a quarter of their
// breadth; wider trenches hold as today). Offline: the PRODUCTION RM_TrenchStrideMath (which cells a stride bridges), its effect
// on the PRODUCTION pocket labelling and cliff-mask bits (a 1-wide trench stops splitting the banks for stride 1 and still does
// for the plain view; a 2-wide one only for stride 2), and the wiring every judge of a walk reads (source checks), plus the
// cross-mod key both mods must spell the same. Each case has a can-fail.
// NOT proven here: a titan walking across a trench in game, the stride masks swapped into a live path job, the HugeThings
// delegate registering at startup. Live rows owed.
using System;
using System.IO;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class TrenchStrideChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string Src(params string[] rel) => RiverSwitchFlipChecks.Src(Path.Combine(rel));

        private static void Rect(byte[] g, int w, int x0, int z0, int rw, int rh, byte d)
        {
            for (int x = x0; x < x0 + rw; x++)
                for (int z = z0; z < z0 + rh; z++)
                    g[z * w + x] = d;
        }

        /// <summary>A 12×8 map with a north-south trench of width tw, depth 8, at x = 5.. (full height: it splits the map).</summary>
        private static byte[] Trench(int tw, out int w, out int h)
        {
            w = 12;
            h = 8;
            var g = new byte[w * h];
            Rect(g, w, 5, 0, tw, h, 8);
            return g;
        }

        private const int Titan = 4; // a titan's climb band (body size 3+), the trench is deeper than it climbs

        public static void Run(Action<string, Action> Case)
        {
            Case("TrenchStride_run_widths", () =>
            {
                byte[] g = Trench(1, out int w, out int h);
                byte[] runs = RM_TrenchStrideMath.RunWidths(g, w, h);
                for (int z = 0; z < h; z++)
                    Assert(runs[z * w + 5] == 1, "a 1-wide trench, any length, is width 1 at z=" + z);
                Assert(runs[0] == 0 && runs[4] == 0 && runs[6] == 0, "can-fail: banks are not trench");
                g = Trench(2, out w, out h);
                runs = RM_TrenchStrideMath.RunWidths(g, w, h);
                Assert(runs[5] == 2 && runs[6] == 2, "a 2-wide trench is width 2");
                g = Trench(4, out w, out h);
                runs = RM_TrenchStrideMath.RunWidths(g, w, h);
                Assert(runs[5] == 0, "can-fail: wider than MaxStride is never bridged");
                var pit = new byte[12 * 12];
                Rect(pit, 12, 3, 3, 3, 3, 6);
                runs = RM_TrenchStrideMath.RunWidths(pit, 12, 12);
                Assert(runs[4 * 12 + 4] == 3, "a 3×3 pit is width 3 (stride 3 only)");
                Assert(!RM_TrenchStrideMath.Bridged(runs[4 * 12 + 4], 2), "can-fail: stride 2 never bridges a 3-wide pit");
                var edge = new byte[12 * 8];
                Rect(edge, 12, 0, 0, 12, 1, 8);  // along the south map edge: no far bank north-south, none east-west
                runs = RM_TrenchStrideMath.RunWidths(edge, 12, 8);
                Assert(runs[5] == 0, "can-fail: a run that reaches the map edge has no far bank");
                var stair = new byte[10 * 10];
                for (int i = 1; i < 9; i++) stair[i * 10 + i] = 8;
                runs = RM_TrenchStrideMath.RunWidths(stair, 10, 10);
                Assert(runs[4 * 10 + 4] == 1, "a diagonal staircase trench is width 1");
            });
            Case("TrenchStride_bridged_view_and_canonical", () =>
            {
                byte[] g = Trench(1, out int w, out int h);
                byte[] runs = RM_TrenchStrideMath.RunWidths(g, w, h);
                byte[] v1 = RM_TrenchStrideMath.BridgedDepth(g, runs, 1);
                Assert(v1[5] == 0 && g[5] == 8, "stride 1 reads the trench as ground; the input is untouched");
                Assert(RM_TrenchStrideMath.BridgedDepth(g, runs, 0)[5] == 8, "can-fail: stride 0 bridges nothing");
                Assert(RM_TrenchStrideMath.CanonicalStride(runs, 3) == 1, "only 1-wide trenches: strides 1-3 share stride 1's view");
                Assert(RM_TrenchStrideMath.CanonicalStride(runs, 0) == 0, "can-fail: no stride, the plain view");
                byte[] g2 = Trench(2, out w, out h);
                byte[] r2 = RM_TrenchStrideMath.RunWidths(g2, w, h);
                Assert(RM_TrenchStrideMath.CanonicalStride(r2, 1) == 0, "can-fail: stride 1 against a 2-wide trench is the plain view");
                Assert(RM_TrenchStrideMath.CanonicalStride(r2, 2) == 2, "stride 2 bridges it");
                Assert(RM_TrenchStrideMath.ClampStride(9) == RM_TrenchStrideMath.MaxStride && RM_TrenchStrideMath.ClampStride(-1) == 0, "clamp");
            });
            Case("TrenchStride_pocket_labels_join_the_banks", () =>
            {
                byte[] g = Trench(1, out int w, out int h);
                byte[] runs = RM_TrenchStrideMath.RunWidths(g, w, h);
                var plain = RM_PocketGridMath.Label(g, w, h, Titan);
                Assert(!plain.SameComponent(2 * w + 2, 2 * w + 9), "can-fail: in the plain view a sheer 4 m trench splits the banks");
                var titan = RM_PocketGridMath.Label(RM_TrenchStrideMath.BridgedDepth(g, runs, 1), w, h, Titan);
                Assert(titan.SameComponent(2 * w + 2, 2 * w + 9), "stride 1: one surface across the 1-wide trench");
                Assert(!titan.IsPocketCell(5, 2), "the bridged trench cell is surface to the titan");
                byte[] g2 = Trench(2, out w, out h);
                byte[] r2 = RM_TrenchStrideMath.RunWidths(g2, w, h);
                var t1 = RM_PocketGridMath.Label(RM_TrenchStrideMath.BridgedDepth(g2, r2, 1), w, h, Titan);
                Assert(!t1.SameComponent(2 * w + 2, 2 * w + 9), "can-fail: a stride-1 titan is held by a 2-wide trench");
                var t2 = RM_PocketGridMath.Label(RM_TrenchStrideMath.BridgedDepth(g2, r2, 2), w, h, Titan);
                Assert(t2.SameComponent(2 * w + 2, 2 * w + 9), "a stride-2 titan steps over it");
            });
            Case("TrenchStride_cliff_bits_open_the_crossing", () =>
            {
                // the bank cell west of a 1-wide trench, as RM_TrenchStride.DeriveCell feeds AllowedBits
                int[] plain = { 0, 0, 8, 0, 0, 8, 0, 0, 8 };   // centre a bank, east column (N9 2, 5, 8) the trench
                byte bPlain = RM_CliffMaskMath.AllowedBits(plain, Titan);
                Assert((bPlain & (1 << 2)) == 0, "can-fail: the plain band refuses the 4 m step east into the trench");
                int[] bridged = { 0, 0, 0, 0, 0, 0, 0, 0, 0 };
                Assert((RM_CliffMaskMath.AllowedBits(bridged, Titan) & (1 << 2)) != 0, "the stride view allows it");
            });
            Case("TrenchStride_wiring_every_judge_reads_the_stride_view", () =>
            {
                string st = Src("Superdeep", "RM_TrenchStride.cs");
                string grid = Src("Superdeep", "RM_PocketGrid.cs");
                string trap = Src("Superdeep", "RM_SuperdeepTrap.cs");
                string cost = Src("Superdeep", "RM_PitStepCost.cs");
                Assert(st.Contains("AppDomain.CurrentDomain.GetData(HookKey) as Func<Pawn, int>"), "the registration point is read, no reflection");
                Assert(!st.Contains("GetTypeInAnyAssembly") && !st.Contains("TypeByName") && !st.Contains("HugeThings."),
                    "can-fail: no type lookup, no HugeThings type named");
                Assert(st.Contains("RM_TrenchStrideMath.BridgedDepth(depth, runs, s)") && st.Contains("job.connectivity = m.band[s][band].AsReadOnly()"),
                    "the stride masks derive from the bridged depth and are swapped in");
                Assert(st.Contains("[HarmonyPriority(Priority.Low)] public static void Postfix(Map ___map, ref PathFinderJob job)"),
                    "the stride swap runs after RM_CliffMask's");
                Assert(grid.Contains("RM_TrenchStrideMath.BridgedDepth(depth, RM_TrenchStrideMath.RunWidths(depth, w, h), stride)")
                    && grid.Contains("public static RM_PocketGrid ForPawn(Map map, Pawn p)"), "the pocket grid's stride view");
                Assert(grid.Contains("notifyFlips && stride == 0"), "can-fail: a stride grid never re-pits the rooms");
                Assert(trap.Contains("RM_PocketGrid g = RM_PocketGrid.ForPawn(map, p);"), "the reach veto reads the walker's view");
                Assert(System.Text.RegularExpressions.Regex.Matches(trap, @"RM_PocketGrid\.ForPawn\(p\.Map, p\)").Count >= 4,
                    "hold, trap, too-narrow and the map-edge check read the pawn's view");
                Assert(trap.Contains("if (to == 0 || RM_TrenchStride.SteppedOver(p, map, eng, pos))"), "no falling arrival onto a trench it strides");
                Assert(trap.Contains("int toD = RM_TrenchStride.StepDepthFor(pawn, map, eng, next);"), "the step floor reads the stride view");
                Assert(trap.Contains("int toD = RM_TrenchStride.StepDepthFor(p, p.Map, eng, to);"), "the jump drop reads the stride view");
                Assert(cost.Contains("RM_TrenchStride.SteppedOver(strider, map, eng, c)"), "the walked step is priced as ground");
            });
            Case("TrenchStride_cross_mod_key_matches_HugeThings", () =>
            {
                string st = Src("Superdeep", "RM_TrenchStride.cs");
                string ht = Src("..", "..", "HugeThings", "Source", "Titanic", "WallsSlots", "TrenchStrideHook.cs");
                const string key = "\"RimMandrake.TrenchStride.v1\"";
                Assert(st.Contains("HookKey = " + key) && ht.Contains("Key = " + key), "both mods spell the slot the same");
                Assert(ht.Contains("AppDomain.CurrentDomain.SetData(Key, (Func<Pawn, int>)Stride)"), "HugeThings registers a Func<Pawn, int>");
                Assert(ht.Contains("WallsSlots.WidestTrenchSteppedOver(WallsSlotsUtility.Breadth(p))") && ht.Contains("TrenchStepActive"),
                    "the stride is the kernel's, behind the setting");
                string csproj = Src("RimMandrake_FlowWorks.csproj");
                Assert(!csproj.Contains("HugeThings"), "can-fail: FlowWorks takes no assembly reference on HugeThings");
            });
        }
    }
}
