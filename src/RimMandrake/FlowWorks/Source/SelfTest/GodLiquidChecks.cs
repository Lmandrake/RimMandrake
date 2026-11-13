// RIMMANDRAKE_GIVE_GODMODE_LIQUID_POUR_DRAIN (owner 2026-11-12: "we need some God Mode capabilities to allow the debug player
// the ability to drop large units of various liquids on the terrain or in a pit as well as remove it."). The dev-mode pour,
// drain and set-level tools. The planning arithmetic is the PRODUCTION Verse-free RM_GodLiquidMath and RM_SheetMath (compiled
// in by the .csproj), driven over a toy grid here; the game wiring (the engine calls, the sheet route for undug ground, the
// flow-ledger disclosure, the armed debug tools, the bridge surface) is read from production source.
// What this cannot see: a pour drawn on a live map, the pulse levelling it afterwards, the sheet spreading it (the item's live row).
using System;
using System.Collections.Generic;
using System.Linq;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class GodLiquidChecks
    {
        private const long U = RM_LevelSolve.U;

        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        /// <summary>A toy map: depth in notches (0 = undug), water in dL, a liquid key per square (0 = dry).</summary>
        private sealed class Grid
        {
            public readonly int W, H;
            public readonly int[] Depth;
            public readonly long[] Water;
            public readonly byte[] Fluid;

            public Grid(int w, int h)
            {
                W = w; H = h;
                Depth = new int[w * h]; Water = new long[w * h]; Fluid = new byte[w * h];
            }

            public int I(int x, int z) => z * W + x;

            public void Dig(int x0, int z0, int x1, int z1, int notches)
            {
                for (int z = z0; z <= z1; z++)
                    for (int x = x0; x <= x1; x++)
                        Depth[I(x, z)] = notches;
            }

            public int Neighbour(int i, int dir)
            {
                int x = i % W, z = i / W;
                switch (dir)
                {
                    case 0: z++; break;
                    case 1: x++; break;
                    case 2: z--; break;
                    default: x--; break;
                }
                return x < 0 || z < 0 || x >= W || z >= H ? -1 : z * W + x;
            }

            /// <summary>The engine's join rule for a pour or a take of liquid <paramref name="key"/>: dug, and dry or the same liquid.</summary>
            public bool Joins(int i, byte key) => Depth[i] > 0 && (Water[i] == 0 || Fluid[i] == key);

            public long Room(int i) => Math.Max(0, Depth[i] * U - Water[i]);

            public long Total() => Water.Sum();

            public void Apply(List<KeyValuePair<int, long>> plan, byte key)
            {
                foreach (KeyValuePair<int, long> p in plan)
                {
                    Water[p.Key] += p.Value;
                    Assert(Water[p.Key] >= 0, "square " + p.Key + " went below empty: " + Water[p.Key]);
                    Assert(Water[p.Key] <= Depth[p.Key] * U, "square " + p.Key + " over its brim: " + Water[p.Key] + " > " + Depth[p.Key] * U);
                    Fluid[p.Key] = Water[p.Key] > 0 ? key : (byte)0;
                }
            }

            public List<int> Body(int start, byte key) =>
                RM_GodLiquidMath.Walk(start, Neighbour, i => Joins(i, key), W * H);
        }

        private static long Sum(List<KeyValuePair<int, long>> plan) => plan.Sum(p => p.Value);

        public static void Run(Action<string, Action> Case)
        {
            Case("GodLiquid_amounts_refuse_zero_negative_and_nonsense", () =>
            {
                foreach (double bad in new[] { 0.0, -1.0, -2048000.0, double.NaN, double.PositiveInfinity, double.NegativeInfinity,
                                               RM_GodLiquidMath.MaxLitres + 1.0, 0.04 })
                {
                    Assert(RM_GodLiquidMath.CheckLitres(bad, out long dl) != null && dl == 0, "amount " + bad + " L was accepted (" + dl + " dL)");
                }
                Assert(RM_GodLiquidMath.CheckLitres(1000.0, out long one) == null && one == 1000L * RM_Volume.UnitsPerLitre, "1,000 L is not 10,000 dL: " + one);
                Assert(RM_GodLiquidMath.CheckLitres(0.1, out long tenth) == null && tenth == 1, "0.1 L is not 1 dL: " + tenth);
                foreach (double badM in new[] { -0.5, double.NaN, double.PositiveInfinity, RM_GodLiquidMath.MaxLevelMetres + 0.5 })
                {
                    Assert(RM_GodLiquidMath.CheckLevelMetres(badM, out long ldl) != null && ldl == 0, "level " + badM + " m was accepted");
                }
                Assert(RM_GodLiquidMath.CheckLevelMetres(0.0, out long zero) == null && zero == 0, "level 0 m (drain to dry) was refused");
                Assert(RM_GodLiquidMath.CheckLevelMetres(1.0, out long onem) == null && onem == 2 * U, "1 m is not two notches: " + onem);
            });

            Case("GodLiquid_steps_reach_a_full_16x16_pit_4m_deep", () =>
            {
                long fullPitLitres = 16L * 16L * (long)Math.Round(4.0 / RM_Volume.MetresPerNotch) * RM_Volume.LitresPerNotch;
                Assert(fullPitLitres == 2048000L, "the 16x16 x 4 m pit is not 2,048,000 L: " + fullPitLitres);
                Assert(RM_GodLiquidMath.FullPit16x16x4mLitres == fullPitLitres, "the named step is not the full pit: " + RM_GodLiquidMath.FullPit16x16x4mLitres);
                Assert(RM_GodLiquidMath.PourLitreSteps.Contains(fullPitLitres), "no pour step fills the 16x16 x 4 m pit exactly");
                Assert(RM_GodLiquidMath.PourLitreSteps.Max() >= fullPitLitres, "the largest step is below a full 16x16 x 4 m pit");
                Assert(RM_GodLiquidMath.PourLitreSteps.Max() <= RM_GodLiquidMath.MaxLitres, "a step is above the cap and would be refused");
                Assert(RM_GodLiquidMath.PourLitreSteps.All(s => RM_GodLiquidMath.CheckLitres(s, out _) == null), "a shipped step is refused");
                Assert(RM_GodLiquidMath.LevelMetreSteps.Contains(0f) && RM_GodLiquidMath.LevelMetreSteps.Contains(4f), "level steps miss 0 m or 4 m");
            });

            Case("GodLiquid_off_map_cell_and_unknown_liquid_refused", () =>
            {
                foreach (var c in new[] { (-1, 0), (0, -1), (50, 0), (0, 50), (int.MinValue, 3) })
                {
                    Assert(RM_GodLiquidMath.CheckCell(c.Item1, c.Item2, 50, 50) != null, "off-map " + c + " accepted");
                }
                Assert(RM_GodLiquidMath.CheckCell(0, 0, 50, 50) == null && RM_GodLiquidMath.CheckCell(49, 49, 50, 50) == null, "an in-map corner refused");
                string[] known = { "RM_Fluid_Water", "RM_Fluid_Tar", "RM_Fluid_Oil" };
                Assert(RM_GodLiquidMath.ResolveLiquid("RM_Fluid_Tar", known, out int tar) == null && tar == 1, "tar not found");
                Assert(RM_GodLiquidMath.ResolveLiquid("rm_fluid_oil", known, out int oil) == null && oil == 2, "a case-folded name not found");
                foreach (string bad in new[] { "Lava", "", null, "RM_Fluid_" })
                {
                    string why = RM_GodLiquidMath.ResolveLiquid(bad, known, out int idx);
                    Assert(why != null && idx == -1, "unknown liquid '" + bad + "' accepted");
                    Assert(why.Contains("RM_Fluid_Tar"), "the refusal does not list the liquids there are: " + why);
                }
            });

            Case("GodLiquid_pour_into_dug_body_fills_it_exactly", () =>
            {
                // a 16x16 pit 4 m (8 notches) deep with a 1 m notch (2 deeper) on its north wall, in undug ground
                var g = new Grid(24, 24);
                g.Dig(4, 4, 19, 19, 8);
                g.Depth[g.I(11, 19)] = 10;
                long room = Enumerable.Range(0, g.W * g.H).Sum(i => g.Room(i));
                List<int> body = g.Body(g.I(4, 4), 1);
                Assert(body.Count == 256 && body[0] == g.I(4, 4), "the walk did not find the 256 squares from the clicked one (" + body.Count + ")");
                var plan = new List<KeyValuePair<int, long>>();
                long want = RM_GodLiquidMath.FullPit16x16x4mLitres * RM_Volume.UnitsPerLitre;
                long placed = RM_GodLiquidMath.PlanPour(body, g.Room, want, false, plan);
                Assert(placed == want && Sum(plan) == want, "planned " + placed + " of " + want);
                g.Apply(plan, 1);
                Assert(g.Total() == want, "the grid holds " + g.Total() + ", poured " + want);
                Assert(room - g.Total() == 2 * U, "the full-pit pour did not leave exactly the notch's extra 2 notches of room");
                Assert(Enumerable.Range(0, g.W * g.H).Where(i => g.Depth[i] == 0).All(i => g.Water[i] == 0), "liquid on an undug square");
                // pour more than the room: what fits is placed, the rest is reported, nothing is created
                var plan2 = new List<KeyValuePair<int, long>>();
                long placed2 = RM_GodLiquidMath.PlanPour(g.Body(g.I(4, 4), 1), g.Room, 5000L * U, false, plan2);
                Assert(placed2 == 2 * U && Sum(plan2) == placed2, "the overfull pour placed " + placed2 + ", the room was " + 2 * U);
                g.Apply(plan2, 1);
                Assert(g.Total() == room, "a brimming pit does not hold its room exactly");
                Assert(RM_GodLiquidMath.PlanPour(g.Body(g.I(4, 4), 1), g.Room, U, false, new List<KeyValuePair<int, long>>()) == 0, "a full pit took more");
            });

            Case("GodLiquid_pour_never_mixes_liquids_and_never_lands_on_undug_ground", () =>
            {
                var g = new Grid(12, 6);
                g.Dig(1, 1, 4, 4, 4);   // a water pit
                g.Dig(5, 1, 8, 4, 4);   // a dry pit beside it, joined
                for (int z = 1; z <= 4; z++) for (int x = 1; x <= 4; x++) { g.Water[g.I(x, z)] = 2 * U; g.Fluid[g.I(x, z)] = 1; }
                // tar clicked into the water: the clicked square itself is foreign, so the walk is empty
                Assert(g.Body(g.I(2, 2), 2).Count == 0, "a tar walk started on a water square");
                // tar clicked into the dry half fills the dry half only
                List<int> dry = g.Body(g.I(6, 2), 2);
                Assert(dry.Count == 16 && dry.All(i => g.Water[i] == 0), "the tar walk crossed into the water: " + dry.Count);
                var plan = new List<KeyValuePair<int, long>>();
                long placed = RM_GodLiquidMath.PlanPour(dry, g.Room, 1000L * U, false, plan);
                Assert(placed == 16 * 4 * U, "tar placed " + placed + ", the dry half holds " + 16 * 4 * U);
                // undug ground: the walk from an undug square is empty (the tool routes it to the sheet instead)
                Assert(g.Body(g.I(0, 0), 1).Count == 0, "a walk started on undug ground");
                Assert(RM_GodLiquidMath.PlanPour(new List<int>(), g.Room, U, false, plan) == 0, "an empty body placed liquid");
            });

            Case("GodLiquid_drain_part_takes_exactly_nearest_first", () =>
            {
                var g = new Grid(10, 10);
                g.Dig(2, 2, 7, 7, 6);
                foreach (int i in Enumerable.Range(0, 100).Where(i => g.Depth[i] > 0)) { g.Water[i] = 3 * U + 1234; g.Fluid[i] = 1; }
                long before = g.Total();
                List<int> body = g.Body(g.I(2, 2), 1);
                var plan = new List<KeyValuePair<int, long>>();
                long want = 1500L * RM_Volume.UnitsPerLitre;   // 1.5 notches
                long took = RM_GodLiquidMath.PlanTake(body, i => g.Water[i], want, false, plan);
                Assert(took == want && -Sum(plan) == want, "took " + took + " of " + want);
                Assert(plan[0].Key == g.I(2, 2), "the clicked square was not drained first");
                g.Apply(plan, 1);
                Assert(before - g.Total() == want, "the grid lost " + (before - g.Total()) + ", drained " + want);
                Assert(plan.All(p => p.Value < 0), "a drain plan poured");
            });

            Case("GodLiquid_drain_all_empties_the_connected_body_only", () =>
            {
                var g = new Grid(14, 6);
                g.Dig(1, 1, 4, 4, 4);   // water pit A, clicked
                g.Dig(5, 1, 6, 4, 4);   // dry squares joining A to B
                g.Dig(7, 1, 8, 4, 4);   // water pit B, joined through the dry squares
                g.Dig(11, 1, 12, 4, 4); // water pit C, not joined
                g.Dig(1, 5, 4, 5, 4);   // oil along A's south side
                foreach (int i in Enumerable.Range(0, g.W * g.H).Where(i => g.Depth[i] > 0))
                {
                    int x = i % g.W, z = i / g.W;
                    if (x == 5 || x == 6) continue;
                    g.Water[i] = 2 * U + 77;
                    g.Fluid[i] = z == 5 ? (byte)3 : (byte)1;
                }
                long c = Enumerable.Range(0, g.W * g.H).Where(i => i % g.W >= 11).Sum(i => g.Water[i]);
                long oil = Enumerable.Range(0, g.W * g.H).Where(i => g.Fluid[i] == 3).Sum(i => g.Water[i]);
                long ab = g.Total() - c - oil;
                var plan = new List<KeyValuePair<int, long>>();
                long took = RM_GodLiquidMath.PlanTake(g.Body(g.I(2, 2), 1), i => g.Water[i], RM_GodLiquidMath.All, false, plan);
                Assert(took == ab, "drain all took " + took + ", the joined water was " + ab);
                g.Apply(plan, 1);
                Assert(g.Total() == c + oil, "after drain all the grid holds " + g.Total() + ", want pit C + oil " + (c + oil));
                Assert(Enumerable.Range(0, g.W * g.H).Where(i => g.Fluid[i] == 3).Sum(i => g.Water[i]) == oil, "the oil was drained");
            });

            Case("GodLiquid_set_level_follows_the_floor_and_conserves", () =>
            {
                var g = new Grid(10, 4);
                g.Dig(1, 1, 4, 2, 8);   // 4 m deep, clicked
                g.Dig(5, 1, 8, 2, 6);   // a 3 m ledge
                foreach (int i in Enumerable.Range(0, g.W * g.H).Where(i => g.Depth[i] == 8)) { g.Water[i] = 7 * U; g.Fluid[i] = 1; }
                long before = g.Total();
                List<int> body = g.Body(g.I(1, 1), 1);
                var plan = new List<KeyValuePair<int, long>>();
                RM_GodLiquidMath.CheckLevelMetres(1.5, out long target);
                long net = RM_GodLiquidMath.PlanLevel(body, i => g.Depth[i], i => g.Water[i], g.Depth[g.I(1, 1)], target, false, plan);
                g.Apply(plan, 1);
                Assert(g.Water[g.I(1, 1)] == 3 * U, "the clicked square does not read 1.5 m: " + g.Water[g.I(1, 1)]);
                Assert(g.Water[g.I(6, 1)] == U, "the ledge, 1 m shallower, does not read 0.5 m: " + g.Water[g.I(6, 1)]);
                Assert(g.Total() - before == net && net == Sum(plan), "net " + net + " != change " + (g.Total() - before));
                Assert(plan.Where(p => p.Value < 0).Select(p => p.Key).All(i => g.Depth[i] == 8), "the level drained the ledge it should fill");
                // above the brim: capped at the clicked square's depth, never over a brim (Apply asserts it)
                var plan2 = new List<KeyValuePair<int, long>>();
                RM_GodLiquidMath.CheckLevelMetres(RM_GodLiquidMath.MaxLevelMetres, out long huge);
                RM_GodLiquidMath.PlanLevel(g.Body(g.I(1, 1), 1), i => g.Depth[i], i => g.Water[i], 8, huge, false, plan2);
                g.Apply(plan2, 1);
                Assert(g.Total() == 8 * 8 * U + 8 * 6 * U, "an over-brim level did not fill the body to its brim: " + g.Total());
                // level 0: dry
                var plan3 = new List<KeyValuePair<int, long>>();
                RM_GodLiquidMath.PlanLevel(g.Body(g.I(1, 1), 1), i => g.Depth[i], i => g.Water[i], 8, 0, false, plan3);
                g.Apply(plan3, 1);
                Assert(g.Total() == 0, "level 0 m left " + g.Total());
            });

            Case("GodLiquid_whole_notch_mode_moves_whole_notches_only", () =>
            {
                var g = new Grid(6, 3);
                g.Dig(1, 1, 4, 1, 4);
                List<int> body = g.Body(g.I(1, 1), 1);
                var plan = new List<KeyValuePair<int, long>>();
                long placed = RM_GodLiquidMath.PlanPour(body, g.Room, 2 * U + U / 2, true, plan);
                Assert(placed == 2 * U && plan.All(p => p.Value % U == 0), "whole-notch pour placed " + placed);
                g.Apply(plan, 1);
                var take = new List<KeyValuePair<int, long>>();
                long took = RM_GodLiquidMath.PlanTake(body, i => g.Water[i], U + 3, true, take);
                Assert(took == U && take.All(p => p.Value % U == 0), "whole-notch take took " + took);
                var lvl = new List<KeyValuePair<int, long>>();
                RM_GodLiquidMath.PlanLevel(body, i => g.Depth[i], i => g.Water[i], 4, U + U / 3, true, lvl);
                Assert(lvl.All(p => p.Value % U == 0), "whole-notch level moved a part notch");
            });

            Case("GodLiquid_sheet_drain_purges_the_connected_sheet_disclosed", () =>
            {
                RM_SheetMath.State Sheet()
                {
                    var st = new RM_SheetMath.State(8, 8, 1);
                    void Wet(int x, int z, int dl, byte f) { int i = z * 8 + x; st.Dl[i] = dl; st.Fluid[i] = f; st.Occ.Add(i); }
                    for (int x = 1; x <= 4; x++) Wet(x, 2, 500, 1);   // one sheet of water
                    Wet(7, 7, 300, 1);                                 // a puddle not joined to it
                    Wet(5, 2, 400, 2);                                 // another liquid touching it
                    st.Occ.Sort();
                    st.In[(int)RM_SheetMath.Source.Flood] = st.Dl.Sum();
                    return st;
                }
                var s = Sheet();
                Assert(s.LedgerCloses, "the toy sheet's books do not close before the drain");
                long part = RM_SheetMath.PurgeConnected(s, 2 * 8 + 2, 700);   // the (2,2) square
                Assert(part == 700 && s.Purged == 700 && s.LedgerCloses, "part drain took " + part + ", purged " + s.Purged);
                Assert(s.Dl[2 * 8 + 2] == 0 && (s.Dl[2 * 8 + 1] == 300) != (s.Dl[2 * 8 + 3] == 300) && s.Dl[2 * 8 + 4] == 500,
                    "not nearest first: " + s.Dl[2 * 8 + 1] + "/" + s.Dl[2 * 8 + 2] + "/" + s.Dl[2 * 8 + 3] + "/" + s.Dl[2 * 8 + 4]);
                var a = Sheet();
                var touched = new List<int>();
                long all = RM_SheetMath.PurgeConnected(a, 2 * 8 + 3, RM_GodLiquidMath.All, touched);
                Assert(all == 4 * 500 && touched.Count == 4, "drain all took " + all + " from " + touched.Count + " squares");
                Assert(a.Dl[7 * 8 + 7] == 300 && a.Dl[2 * 8 + 5] == 400, "an unjoined puddle or another liquid was drained");
                Assert(a.LedgerCloses && a.Purged == 4 * 500 && a.WetCount == 2, "the books do not close after the drain (purged " + a.Purged + ")");
                Assert(RM_SheetMath.PurgeConnected(a, 0, RM_GodLiquidMath.All) == 0, "a dry square drained something");
                Assert(RM_SheetMath.PurgeConnected(a, -1, 5) == 0 && RM_SheetMath.PurgeConnected(a, 64, 5) == 0, "an off-grid square drained");
                Assert(RM_SheetMath.PurgeConnected(a, 7 * 8 + 7, 0) == 0 && RM_SheetMath.PurgeConnected(a, 7 * 8 + 7, -9) == 0, "a zero or negative drain took");
            });

            Case("GodLiquid_game_wiring_engine_sheet_ledger_tools_bridge", () =>
            {
                string god = RiverSwitchFlipChecks.Src("Debug/RM_GodLiquid.cs");
                void Has(string src, string pattern, string what) => RiverSwitchFlipChecks.Has(src, pattern, what);
                Has(god, @"public static string Pour\(IntVec3 cell, string fluid, float litres\)", "bridge: Pour(cell, fluid, litres)");
                Has(god, @"public static string Drain\(IntVec3 cell, float litres\)", "bridge: Drain(cell, litres)");
                Has(god, @"public static string DrainAll\(IntVec3 cell\)", "bridge: DrainAll(cell)");
                Has(god, @"public static string SetLevel\(IntVec3 cell, string fluid, float metres\)", "bridge: SetLevel(cell, fluid, metres)");
                Has(god, @"RM_GodLiquidMath\.CheckCell\(cell\.x, cell\.z, map\.Size\.x, map\.Size\.z\)", "every act checks the cell is on the map");
                Has(god, @"RM_GodLiquidMath\.CheckLitres\(litres, out long", "a pour and a drain check the amount");
                Has(god, @"RM_GodLiquidMath\.ResolveLiquid\(", "a pour resolves the liquid by name");
                Has(god, @"ex\.TryPourDl\(", "the pit pour goes through the engine");
                Has(god, @"ex\.TryTakeDl\(", "the pit drain goes through the engine");
                Has(god, @"\.Offer\(cell, rest, f, RM_SheetMath\.Source\.Flood, overflow\)", "a pour on undug ground goes to the sheet");
                Has(god, @"\.PurgeConnectedAt\(start, ", "a drain on undug ground purges the sheet");
                Has(god, @"ex\.NoteMapControlFlowDl\(poured, 0\)", "a pit pour is disclosed on the flow ledger");
                Has(god, @"ex\.NoteMapControlFlowDl\(0, taken\)", "a pit drain is disclosed on the flow ledger");
                Has(god, @"ex\.NoteMapControlFlowDl\(poured, taken\)", "a set-level is disclosed on the flow ledger");
                string sheet = RiverSwitchFlipChecks.Src("Sheet/RM_MapComponent_Sheet.cs");
                Has(sheet, @"public long PurgeConnectedAt\(IntVec3 c, long maxDl\)", "the sheet's drain-here entry");
                Has(sheet, @"RM_SheetMath\.PurgeConnected\(state, ", "it purges through the production sheet math");
                string dbg = RiverSwitchFlipChecks.Src("Debug/FlowWorksDebugActions.cs");
                foreach (string label in new[] { "Pour liquid...", "Drain liquid...", "Set pit liquid level..." })
                {
                    Assert(dbg.Contains("\"" + label + "\""), "debug action missing: " + label);
                }
                Has(dbg, @"DebugMenuOptionMode\.Tool, delegate \{ GodSay\(RM_GodLiquid\.PourOverflow\(UI\.MouseCell\(\), ", "pour is a click tool that stays armed");
                Has(dbg, @"DebugMenuOptionMode\.Tool, delegate \{ GodSay\(RM_GodLiquid\.Drain(All)?\(UI\.MouseCell\(\)", "drain is a click tool");
                Has(dbg, @"DebugMenuOptionMode\.Tool, delegate \{ GodSay\(RM_GodLiquid\.SetLevel\(UI\.MouseCell\(\), """", ", "set level is a click tool");
                Has(dbg, @"Building_RM_MapControl\.CanalFluids\(\)", "the pour lists every registered liquid");
            });
            // round 2 (owner 2026-11-12 ~20:30: "But it always responded "No Room." It shouldn't do that. It should go ahead and
            // overflow. I wanted to watch the water bulge and move."): his clicks were on a brim-full pit and on open ground with
            // canal overflow off (Player.log GOD_LIQUID lines). A dev pour now never refuses for room.
            Case("GodLiquid_overflow_rule_force_bypasses_the_switches_only", () =>
            {
                // (switch, engine, fluid, water, otherLiquids, force) -> accepted
                Assert(!RM_SheetMath.AcceptsSpill(false, true, true, true, true, false), "a spill went in with overflow off");
                Assert(RM_SheetMath.AcceptsSpill(true, true, true, true, false, false), "water was refused with overflow on");
                Assert(!RM_SheetMath.AcceptsSpill(true, true, true, false, false, false), "tar spilled while other liquids are off");
                Assert(RM_SheetMath.AcceptsSpill(false, true, true, true, false, true), "a forced pour was refused by the overflow switch");
                Assert(RM_SheetMath.AcceptsSpill(false, true, true, false, false, true), "a forced tar pour was refused by 'other liquids'");
                Assert(!RM_SheetMath.AcceptsSpill(true, false, true, true, true, true), "a forced pour went in with the depth engine off");
                Assert(!RM_SheetMath.AcceptsSpill(true, true, false, true, true, true), "a forced pour went in with no liquid");
            });

            Case("GodLiquid_drain_starts_at_the_nearest_spill_when_the_click_is_dry", () =>
            {
                // RIMMANDRAKE_LET_GROUND_DRAIN_ALL_FIND_SPILL_EMPTY_CLICK: a part drain emptied the clicked square, 8 kL lay around it
                var order = new List<int> { 10, 11, 9, 20, 0, 21, 30 };   // the click, then outward
                var wet = new HashSet<int> { 21, 30 };
                Assert(RM_GodLiquidMath.NearestWet(order, i => wet.Contains(i)) == 21, "not the nearest wet square");
                wet.Add(10);
                Assert(RM_GodLiquidMath.NearestWet(order, i => wet.Contains(i)) == 10, "a wet click was not its own start");
                Assert(RM_GodLiquidMath.NearestWet(order, i => false) == -1, "a dry neighbourhood found a spill");
                Assert(RM_GodLiquidMath.NearestWet(new List<int>(), i => true) == -1, "an empty search found a spill");
                // the whole joined sheet goes from there, books closed
                var s = new RM_SheetMath.State(8, 8, 1);
                foreach (int i in new[] { 2 * 8 + 3, 2 * 8 + 4, 2 * 8 + 5 })
                {
                    s.Dl[i] = 500; s.Fluid[i] = 1; s.Occ.Add(i);
                }
                s.In[(int)RM_SheetMath.Source.Flood] = 1500;
                var ring = new List<int> { 2 * 8 + 2, 2 * 8 + 1, 2 * 8 + 3 };
                int from = RM_GodLiquidMath.NearestWet(ring, i => s.Dl[i] > 0);
                Assert(from == 2 * 8 + 3, "the drain did not start at the spill beside the dry click: " + from);
                Assert(RM_SheetMath.PurgeConnected(s, from, RM_GodLiquidMath.All) == 1500 && s.WetCount == 0 && s.LedgerCloses,
                    "drain all from the nearest spill left liquid behind");
            });

            Case("GodLiquid_pour_overflows_and_never_says_no_room", () =>
            {
                string god = RiverSwitchFlipChecks.Src("Debug/RM_GodLiquid.cs");
                void Has(string src, string pattern, string what) => RiverSwitchFlipChecks.Has(src, pattern, what);
                Has(god, @"public static string PourOverflow\(IntVec3 cell, string fluid, float litres\)", "bridge: PourOverflow(cell, fluid, litres)");
                Has(god, @"return PourCore\(cell, fluid, litres, true\)", "PourOverflow always sets the overflow flag");
                Has(god, @"return PourCore\(cell, fluid, litres, false\)", "Pour keeps the switch-respecting behaviour");
                Has(god, @"Spill\(map, ex, cell, f, dl - poured, overflow, out string spilled\)", "what a pit has no room for overflows onto the ground");
                Has(god, @"\.Offer\(cell, rest, f, RM_SheetMath\.Source\.Flood, overflow\)", "the overflow starts at the pit's own lips");
                Has(god, @"\.Offer\(c, rest - got, f, RM_SheetMath\.Source\.Flood, overflow\)", "then ring by ring outward");
                Has(god, @"RM_GodLiquidMath\.NearestWet\(", "a drain on dry ground starts at the nearest spill");
                // with the flag set, the only refusals are the cell, the amount and the liquid (Prepare, CheckLitres, ResolveLiquid):
                // every other "REFUSED" in the pour and the spill sits under a "!overflow" test on its line or the 3 before it
                foreach (KeyValuePair<string, string> span in new Dictionary<string, string> {
                    { "private static string PourCore(", "public static string Drain(" }, { "private static string Spill(", "private const int GiveUpAfter" } })
                {
                    string raw = System.IO.File.ReadAllText(RiverSwitchFlipChecks.SrcPath("Debug/RM_GodLiquid.cs"));   // lines kept (Src flattens)
                    int a = raw.IndexOf(span.Key, StringComparison.Ordinal), b = raw.IndexOf(span.Value, StringComparison.Ordinal);
                    Assert(a > 0 && b > a, span.Key + " not found before " + span.Value);
                    string[] lines = raw.Substring(a, b - a).Split('\n');
                    int refusals = 0;
                    for (int i = 0; i < lines.Length; i++)
                    {
                        if (lines[i].Contains("\"REFUSED"))
                        {
                            refusals++;
                            bool guarded = false;
                            for (int j = Math.Max(0, i - 3); j <= i; j++)
                            {
                                guarded |= lines[j].Contains("!overflow");
                            }
                            Assert(guarded, span.Key + " can refuse with the overflow flag set: " + lines[i].Trim());
                        }
                    }
                    Assert(refusals >= 2, span.Key + ": the refusal census saw " + refusals + " refusals (the instrument may be blind)");
                }
                string sheet = RiverSwitchFlipChecks.Src("Sheet/RM_MapComponent_Sheet.cs");
                Has(sheet, @"public long Offer\(IntVec3 origin, long dl, FluidDef fluid, Source from, bool force\)", "the sheet takes a forced offer");
                Has(sheet, @"RM_SheetMath\.AcceptsSpill\(", "the sheet's accept rule is the tested one");
                string dbg = RiverSwitchFlipChecks.Src("Debug/FlowWorksDebugActions.cs");
                string gm = "God" + " mode";
                foreach (KeyValuePair<string, string> f in new Dictionary<string, string> { { "Debug/FlowWorksDebugActions.cs", dbg },
                    { "Debug/RM_GodLiquid.cs", god }, { "RM_GodLiquidMath.cs", RiverSwitchFlipChecks.Src("RM_GodLiquidMath.cs") } })
                {
                    string text = f.Value.Replace("RIMMANDRAKE_GIVE_GODMODE_LIQUID_POUR_DRAIN", "");   // the ledger id is never renamed
                    Assert(text.IndexOf(gm, StringComparison.OrdinalIgnoreCase) < 0 && text.IndexOf("godmode", StringComparison.OrdinalIgnoreCase) < 0,
                        f.Key + " still says '" + gm + "' (owner: \"God Mode is a game mode when you click on the little head icon\")");
                }
            });
        }
    }
}
