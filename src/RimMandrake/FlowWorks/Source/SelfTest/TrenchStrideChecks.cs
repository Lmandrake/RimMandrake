// TITAN_TRENCHES_WIRE_MIND_THE_GAP (owner, by card 2026-10-18: titans step over trenches narrower than a quarter of their
// breadth; wider trenches hold as today). Offline: the PRODUCTION RM_TrenchStrideMath (which cells a stride bridges), its effect
// on the PRODUCTION pocket labelling and cliff-mask bits (a 1-wide trench stops splitting the banks for stride 1 and still does
// for the plain view; a 2-wide one only for stride 2), and the wiring every judge of a walk reads (source checks), plus the
// cross-mod key both mods must spell the same. Each case has a can-fail.
// NOT proven here: a titan walking across a trench in game, the stride masks swapped into a live path job, the HugeThings
// delegate registering at startup. Live rows owed.
// TRENCH_STRIDE_UNDERPASS_FIX_ONE_BUG: the stride views composed with the suspension underpass (deck view / floor view, each
// bridged over its own widths; which view a strider plans on) are proven here on the production math; the live swap is not.
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

        /// <summary>The 3x3 of (x, z) as RM_TrenchStride.DeriveCell reads it (out of bounds: 0).</summary>
        private static int[] D9(byte[] depth, int w, int h, int x, int z)
        {
            var d9 = new int[9];
            for (int dz = -1; dz <= 1; dz++)
                for (int dx = -1; dx <= 1; dx++)
                {
                    int cx = x + dx, cz = z + dz;
                    d9[RM_CliffMaskMath.N9(dx, dz)] = cx >= 0 && cz >= 0 && cx < w && cz < h ? depth[cz * w + cx] : 0;
                }
            return d9;
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
                // the bank cell west of a 1-wide trench, its 3x3 read from the PRODUCTION bridged depth as DeriveCell reads it
                byte[] g = Trench(1, out int w, out int h);
                byte[] runs = RM_TrenchStrideMath.RunWidths(g, w, h);
                int[] plain = D9(g, w, h, 4, 3);
                Assert(plain[RM_CliffMaskMath.N9(1, 0)] == 8 && plain[4] == 0, "the sample really is a bank beside the trench");
                byte bPlain = RM_CliffMaskMath.AllowedBits(plain, Titan);
                Assert((bPlain & (1 << 2)) == 0, "can-fail: the plain band refuses the 4 m step east into the trench");
                int[] bridged = D9(RM_TrenchStrideMath.BridgedDepth(g, runs, 1), w, h, 4, 3);
                Assert((RM_CliffMaskMath.AllowedBits(bridged, Titan) & (1 << 2)) != 0, "the stride view allows it");
                byte[] g2 = Trench(2, out w, out h);
                int[] held = D9(RM_TrenchStrideMath.BridgedDepth(g2, RM_TrenchStrideMath.RunWidths(g2, w, h), 1), w, h, 4, 3);
                Assert((RM_CliffMaskMath.AllowedBits(held, Titan) & (1 << 2)) == 0, "can-fail: stride 1 still refuses a 2-wide trench");
            });
            Case("TrenchStride_underpass_views_compose", () =>
            {
                // TRENCH_STRIDE_UNDERPASS_FIX_ONE_BUG. 16x10: a 1-wide trench at x=3 (a suspension deck on it at z=6), a 5-wide pit
                // x=8..12 crossed by a suspension deck along z=4; both decks clear 2 m (the floor band passes under them).
                int w = 16, h = 10;
                var floor = new byte[w * h];               // the floor view: decks read as the hole beneath
                Rect(floor, w, 3, 0, 1, h, 8);
                Rect(floor, w, 8, 0, 5, h, 8);
                var deck = (byte[])floor.Clone();          // the deck view: a surface deck is ground
                Rect(deck, w, 8, 4, 5, 1, 0);
                deck[6 * w + 3] = 0;
                byte[] dv = RM_TrenchStrideMath.BridgedDepth(deck, RM_TrenchStrideMath.RunWidths(deck, w, h), 1);
                byte[] fv = RM_TrenchStrideMath.BridgedDepth(floor, RM_TrenchStrideMath.RunWidths(floor, w, h), 1);
                Assert(dv[5 * w + 3] == 0 && dv[7 * w + 3] == 0, "deck view: the trench beside the deck is still stepped over");
                Assert(fv[6 * w + 3] == 0 && fv[0 * w + 3] == 0, "floor view: a deck over a narrow trench is stepped over too");
                Assert(dv[2 * w + 10] == 8 && fv[2 * w + 10] == 8, "can-fail: the wide pit is never bridged");
                var dl = RM_PocketGridMath.Label(dv, w, h, Titan);
                var fl = RM_PocketGridMath.Label(fv, w, h, Titan);
                Assert(dl.SameComponent(2 * w + 1, 4 * w + 14), "deck view: a titan crosses the trench and the pit's deck");
                Assert(!fl.SameComponent(2 * w + 1, 4 * w + 14), "can-fail: the floor view never uses the deck as a deck");
                Assert(fl.SameComponent(2 * w + 10, 7 * w + 10), "floor view: a titan in the pit walks under the deck");
                Assert(!dl.SameComponent(2 * w + 10, 7 * w + 10), "can-fail: the deck view splits the pit at the deck");
                // who gets which view: the stride must not override the underpass, nor read a strider as down in the hole
                Assert(!RM_TrenchStrideMath.StriderUsesFloorView(true, false, true), "astride the narrow trench beside a deck: deck view");
                Assert(RM_TrenchStrideMath.StriderUsesFloorView(true, true, false), "under a deck (floor band): floor view");
                Assert(RM_TrenchStrideMath.StriderUsesFloorView(true, true, true), "in the floor band over a narrow trench: floor view");
                Assert(RM_TrenchStrideMath.StriderUsesFloorView(true, false, false), "down in the wide pit: floor view");
                Assert(!RM_TrenchStrideMath.StriderUsesFloorView(false, true, false), "can-fail: no floor view without the underpass");
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
                Assert(st.Contains("RM_TrenchStrideMath.BridgedDepth(depth, runs, s)") && st.Contains("job.connectivity = m.band[v][s][band].AsReadOnly()"),
                    "the stride masks derive from the bridged depth and are swapped in");
                Assert(st.Contains("RM_PocketGrid.EffectiveDepth(map, eng, v == FloorView)")
                    && st.Contains("RM_TrenchStrideMath.StriderUsesFloorView(Pits.RM_SuspensionUnderpass.UsesFloorView(p), Pits.RM_SuspensionUnderpass.InFloorBand(p),"),
                    "TRENCH_STRIDE_UNDERPASS_FIX_ONE_BUG: the stride swap composes with the underpass floor view, never overwrites it");
                string under = Src("Pits", "Suspension", "RM_SuspensionPatches.cs");
                Assert(System.Text.RegularExpressions.Regex.Matches(under, @"RM_TrenchStride\.SteppedOver\(p, (p\.)?[mM]ap, eng, from\) \? 0").Count >= 2,
                    "a titan stepping off a trench it strides onto a deck is on the deck, not under it");
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
