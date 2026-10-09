// Selftest for the source stock model built under FLUID_SOURCE_STOCK_MODEL_1,
// extended under CANAL_FILL_IN_DISPLACEMENT_1 to cover the fill-in
// displacement walk's arithmetic (§5, "Filling a canal back in").
//
// WHY THIS EXISTS: §5 of design/RimMandrake/flowworks_mod_definition.md is a
// tuning spec as much as an architecture. Every number in it — the 5:1 budget,
// the seepage baseline, the season bands, the supported-cell floor — produces
// no error of any kind when it drifts. The pond just refills at the wrong rate,
// or recedes at the wrong stock, forever, until somebody happens to trace it by
// hand again. That is exactly the class of defect an offline selftest catches
// for free, on the same discipline as
// src/RimMandrake/Utils/selftest_validate_patch.py.
//
// WHAT IS REAL vs EXTRACTED:
//   EVERYTHING HERE IS REAL. RM_StockMath.cs is the PRODUCTION file, compiled
//   into this project directly (see the .csproj). It is not a transcription.
//   RM_LiquidStock calls every function asserted below, so a change to any
//   constant or clause fails this test immediately.
//
//   ⭐ That is a deliberate improvement on the retired Pits selftest, whose
//   escape-chance formula was a hand transcription that "keeps passing against
//   the OLD formula" if the real method changes. RM_PitTrapMath.cs follows the
//   same rule for the pit-width trap rule. The §5 arithmetic needed no Map, Thing or IntVec3 to be
//   stated, so it was pulled into a Verse-free production file rather than
//   copied into a test.
//
//   ⛔ NOT COVERED, and needing a live Map: the flood fill that discovers a
//   body's footprint and its map-edge contact (RM_LiquidStock.FormBody), the
//   terrain writes of recession and restoration
//   (RM_MapComponent_Excavation.DryNaturalCell / RestoreOriginalTerrain), the
//   scribing round trip, and the pulse hook itself. Those stay untested here on
//   purpose — this file covers the arithmetic they carry, not the grid walking.
//
// Run:
//   python3 src/RimMandrake/Utils/selftest_flowworks_stock.py

using System;
using System.Collections.Generic;
using RimMandrake.FlowWorks;
using RimMandrake.FlowWorks.LiquidTypes;
using RimMandrake.FlowWorks.TakenByLand;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class Program
    {
        private static readonly List<string> Pass = new();
        private static readonly List<(string name, string msg)> Fail = new();

        // The shipped RM_Fluid_Water row, from
        // FlowWorks/Defs/Canals/FluidDefs/FlowWorks_Fluids.xml. Kept here as
        // named constants so a failure says which authored number moved.
        private const float WaterVolumePerTile = 1f;
        private const float WaterCanalCellsPerSourceCell = 5f;
        private const float WaterOozePerCellPerDay = 0.13f;
        private const float WaterRainRefillFactor = 3f;

        // RimMandrakeFlowWorksSettings defaults (that file needs Verse, so the
        // defaults are restated; each is asserted only as the shipped value a
        // scenario runs at, never as the definition of the setting).
        private const float DefaultBudgetMultiplier = 1f;
        private const float DefaultRefillRateMultiplier = 1f;
        private const int DefaultMinLimitlessBodyCells = 50;

        // Verse's GenDate.TicksPerDay / a RimWorld season in days.
        private const int TicksPerDay = 60000;
        private const int DaysPerSeason = 15;

        private static void Case(string name, Action fn)
        {
            try
            {
                fn();
                Pass.Add(name);
                Console.WriteLine("ok    " + name);
            }
            catch (Exception ex)
            {
                Fail.Add((name, ex.Message));
                Console.WriteLine("FAIL  " + name + "\n        " + ex.Message);
            }
        }

        private static void FuzzCase(string name, Func<List<string>> run)
        {
            long c0 = SequenceFuzz.Cases, s0 = SequenceFuzz.Steps;
            var clock = System.Diagnostics.Stopwatch.StartNew();
            Case(name, () =>
            {
                List<string> fails = run();
                if (fails.Count > 0) throw new Exception(fails.Count + " failing seed(s), shrunk:\n        " + string.Join("\n        ", fails));
            });
            Console.WriteLine($"      {SequenceFuzz.Cases - c0} cases, {SequenceFuzz.Steps - s0} steps, {clock.Elapsed.TotalSeconds:F2} s");
        }

        private static void KernelCase(string name, Func<List<string>> run)
        {
            long c0 = FlowKernelFuzz.Cases, p0 = FlowKernelFuzz.Pulses;
            var clock = System.Diagnostics.Stopwatch.StartNew();
            Case(name, () =>
            {
                List<string> fails = run();
                if (fails.Count > 0) throw new Exception(fails.Count + " failing seed(s), shrunk:\n        " + string.Join("\n        ", fails));
            });
            Console.WriteLine($"      {FlowKernelFuzz.Cases - c0} scenes, {FlowKernelFuzz.Pulses - p0} pulses, {clock.Elapsed.TotalSeconds:F2} s");
        }

        private static void Assert(bool cond, string msg)
        {
            if (!cond) throw new Exception(msg);
        }

        private static void AssertClose(float got, float want, string msg, float eps = 0.0001f)
        {
            if (Math.Abs(got - want) > eps)
                throw new Exception($"{msg}: got {got}, want {want}");
        }

        private static float WaterCapacity(int cells) =>
            RM_StockMath.BodyCapacity(cells, WaterCanalCellsPerSourceCell, WaterVolumePerTile, DefaultBudgetMultiplier);

        private static int Main(string[] args)
        {
            // Differential mode: selftest_flowworks_kernel_oracle.py pipes scenes on stdin and compares the
            // kernel's fill vectors with the Python PulseOracle (northstar/validation_v2.py).
            if (args.Length > 0 && args[0] == "--oracle-scenes")
            {
                // A file, not stdin: a large pipe into dotnet.exe across the WSL boundary hangs (measured, 3000 scenes).
                using (var reader = args.Length > 1 ? new System.IO.StreamReader(args[1]) : Console.In)
                {
                    return OracleScenes.Run(reader, Console.Out);
                }
            }

            // ═══════════════════════════════════ the 5:1 budget (§5 "Budget") ══

            Case("Capacity_is_cells_times_canalCells_times_volumePerTile", () =>
                // §5 verbatim: bodyCapacity = sourceCellCount * canalCellsPerSourceCell * volumePerTile.
                AssertClose(WaterCapacity(3), 15f, "a 3-cell water pond"));

            Case("Capacity_scales_linearly_with_footprint", () =>
                Assert(WaterCapacity(20) == 10f * WaterCapacity(2),
                    "the budget is per source CELL, so ten times the footprint must be ten times the capacity"));

            Case("Capacity_of_a_viscous_liquid_is_higher_in_fill_units", () =>
                // volumePerTile 2 means a cell of canal costs two fill-units, so
                // the same footprint must be denominated in twice as many.
                AssertClose(RM_StockMath.BodyCapacity(3, 5f, 2f, 1f), 30f, "a 3-cell tar pond at volumePerTile 2"));

            Case("Capacity_of_an_empty_footprint_is_zero", () =>
                AssertClose(WaterCapacity(0), 0f, "no cells, no stock"));

            Case("PerCellBudget_floors_above_zero_at_the_lowest_slider_notch", () =>
            {
                // FluidDef.ConfigErrors() complains about volumePerTile <= 0 and
                // canalCellsPerSourceCell <= 0, but a ConfigError is a red line in
                // the log, NOT a load refusal — the def still loads and the engine
                // still runs on it. The floor is what stops that def making every
                // body's PerCellVolume 0, which SupportedCells would divide by.
                //
                // 🔴 ASSERTED AS A PROPERTY, NOT AGAINST THE CONSTANT, and with the
                // input that can actually reach zero. Two earlier drafts of this
                // case were useless: `tiny >= RM_StockMath.MinPerCellVolume` is
                // self-referential and passes trivially when the floor is set to 0,
                // and feeding merely SMALL values (1e-4) never reaches 0 in float
                // anyway, so it passed with the floor removed. Both were caught by
                // perturbing the constant to 0f and finding the test still green.
                Assert(RM_StockMath.PerCellBudget(5f, 0f, 1f) > 0f,
                    "a fluid authored with volumePerTile 0 still LOADS after its ConfigError; its per-cell "
                    + "budget must still be strictly positive or supported-cell count divides by zero");
                Assert(RM_StockMath.PerCellBudget(0f, 1f, 1f) > 0f,
                    "same for canalCellsPerSourceCell 0");
                Assert(RM_StockMath.BodyCapacity(10, 5f, 0f, 1f) > 0f,
                    "and a body built from such a def must still get a real capacity, not zero");
                Assert(RM_StockMath.SupportedCells(1f, RM_StockMath.PerCellBudget(5f, 0f, 1f)) >= 0,
                    "and the supported-cell count must be computable from it at all");
            });

            Case("PerCellVolume_is_the_budget_read_backwards", () =>
                AssertClose(RM_StockMath.PerCellVolume(WaterCapacity(3), 3), 5f,
                    "one cell of a water body's footprint is worth the 5 canal cells it supplies"));

            Case("PerCellVolume_of_an_empty_body_is_zero_not_a_divide_by_zero", () =>
                AssertClose(RM_StockMath.PerCellVolume(0f, 0), 0f, "empty body"));

            // ══════════════════════════ limited vs limitless (ruling 16, §5) ══

            Case("Limitless_needs_edge_contact_AND_size", () =>
            {
                Assert(RM_StockMath.IsLimitless(true, false, true, 50, DefaultMinLimitlessBodyCells),
                    "a 50-cell body touching the map edge is the off-map reservoir: LIMITLESS");
                Assert(!RM_StockMath.IsLimitless(true, false, true, 49, DefaultMinLimitlessBodyCells),
                    "edge contact alone must not buy limitless — a 49-cell puddle at the edge is still a puddle");
                Assert(!RM_StockMath.IsLimitless(true, false, false, 4000, DefaultMinLimitlessBodyCells),
                    "size alone must not buy limitless — a huge INLAND lake is finite, which is the whole scarcity premise");
            });

            Case("Limitless_is_forced_when_the_flood_fill_truncates", () =>
                Assert(RM_StockMath.IsLimitless(true, true, false, 4000, DefaultMinLimitlessBodyCells),
                    "a body too big to flood-fill is an ocean; it must classify limitless rather than get a capacity "
                    + "computed from a truncated footprint, which would UNDERSTATE the ocean"));

            Case("Limitless_off_in_settings_makes_every_body_limited", () =>
                Assert(!RM_StockMath.IsLimitless(false, true, true, 99999, 1),
                    "all-off degradation: with sticky classification disabled nothing is limitless, "
                    + "so the mechanic switches off without switching the stock model off"));

            // ════════════════════════════════ refill (ruling 2, §5 "Refill") ══

            Case("Refill_baseline_is_ooze_times_cellCount", () =>
                AssertClose(
                    RM_StockMath.RefillPerDay(WaterOozePerCellPerDay, 4, WaterRainRefillFactor, 0f,
                        RM_StockMath.SeasonBand.Neutral, DefaultRefillRateMultiplier),
                    0.52f, "4 cells of water seeping in fair weather"));

            Case("Refill_is_proportional_to_footprint", () =>
            {
                float one = RM_StockMath.RefillPerDay(WaterOozePerCellPerDay, 1, WaterRainRefillFactor, 0f,
                    RM_StockMath.SeasonBand.Neutral, 1f);
                float ten = RM_StockMath.RefillPerDay(WaterOozePerCellPerDay, 10, WaterRainRefillFactor, 0f,
                    RM_StockMath.SeasonBand.Neutral, 1f);
                AssertClose(ten, 10f * one, "§5: the seepage baseline is groundOoze * sourceCellCount");
            });

            Case("Refill_rain_term_multiplies_the_baseline", () =>
                // (1 + 3*1) = 4x at a full downpour.
                AssertClose(
                    RM_StockMath.RefillPerDay(WaterOozePerCellPerDay, 1, WaterRainRefillFactor, 1f,
                        RM_StockMath.SeasonBand.Neutral, 1f),
                    0.52f, "rain is the fast lane; seepage is the floor"));

            Case("Refill_never_stops_entirely_without_rain", () =>
                Assert(RM_StockMath.RefillPerDay(WaterOozePerCellPerDay, 1, WaterRainRefillFactor, 0f,
                        RM_StockMath.SeasonBand.Dry, 1f) > 0f,
                    "ruling 2's baseline is ALWAYS ON: 'slow and certain, not random'. A body that can reach "
                    + "zero refill in a dry season can be permanently dead, which is not what was ruled."));

            Case("Season_bands_are_ordered_wet_over_neutral_over_cool_over_dry", () =>
            {
                float wet = RM_StockMath.SeasonFactor(RM_StockMath.SeasonBand.Wet);
                float neutral = RM_StockMath.SeasonFactor(RM_StockMath.SeasonBand.Neutral);
                float cool = RM_StockMath.SeasonFactor(RM_StockMath.SeasonBand.Cool);
                float dry = RM_StockMath.SeasonFactor(RM_StockMath.SeasonBand.Dry);
                Assert(wet > neutral && neutral > cool && cool > dry,
                    "the desert-world shape §5 asks for: the wet season carries the refill and high summer barely moves it");
            });

            Case("Refill_accrual_is_INVARIANT_to_pulse_interval", () =>
            {
                // 🔴 PILLAR 2, expressed as a property rather than a comment. The
                // pulse interval is a player-facing slider (60..2500 ticks). If the
                // accrual were not scaled by pulse length, moving that slider would
                // silently retune every pond on the map.
                float perDay = 1f;
                float tenShort = 10f * RM_StockMath.RefillForPulse(perDay, 250, TicksPerDay);
                float oneLong = RM_StockMath.RefillForPulse(perDay, 2500, TicksPerDay);
                AssertClose(tenShort, oneLong,
                    "ten short pulses must accrue exactly what one ten-times-longer pulse accrues");
            });

            Case("Refill_over_a_full_day_equals_the_per_day_rate", () =>
                AssertClose(RM_StockMath.RefillForPulse(0.13f, TicksPerDay, TicksPerDay), 0.13f,
                    "a pulse covering one whole day must accrue exactly one day's worth"));

            Case("Refill_clamps_to_capacity_and_never_above", () =>
            {
                AssertClose(RM_StockMath.ClampToCapacity(14f, 99f, 15f), 15f,
                    "§5: clamped to bodyCapacity — a pond may not overfill past what its footprint justifies");
                AssertClose(RM_StockMath.ClampToCapacity(4f, 1f, 15f), 5f, "an ordinary accrual is not clamped");
            });

            // ───── hand-traced scenario: the one-cell seep takes MULTIPLE SEASONS

            Case("Scenario_one_cell_seep_takes_multiple_seasons_to_refill_from_empty", () =>
            {
                // §5's tuning requirement, stated as a number: "Tune groundOoze so a
                // very small natural source takes multiple seasons".
                //   capacity      = 1 * 5 * 1            = 5 fill-units
                //   refill/day    = 0.13 * 1 * 1 * 1     = 0.13 fill-units
                //   days to full  = 5 / 0.13             = 38.46 days
                //   seasons       = 38.46 / 15           = 2.56 seasons
                float capacity = WaterCapacity(1);
                AssertClose(capacity, 5f, "one-cell seep capacity");
                float perDay = RM_StockMath.RefillPerDay(WaterOozePerCellPerDay, 1, WaterRainRefillFactor, 0f,
                    RM_StockMath.SeasonBand.Neutral, DefaultRefillRateMultiplier);
                float days = capacity / perDay;
                float seasons = days / DaysPerSeason;
                Assert(seasons > 2f && seasons < 6f,
                    $"§5 asks for 'multiple seasons' — slow and certain, not a decade. Got {seasons:F2} seasons "
                    + $"({days:F1} days). Below 2 the scarcity is decoration; above 6 a drained seep is effectively dead.");
            });

            Case("Scenario_that_same_seep_refills_far_faster_in_a_wet_spring", () =>
            {
                float fair = RM_StockMath.RefillPerDay(WaterOozePerCellPerDay, 1, WaterRainRefillFactor, 0f,
                    RM_StockMath.SeasonBand.Neutral, 1f);
                float storm = RM_StockMath.RefillPerDay(WaterOozePerCellPerDay, 1, WaterRainRefillFactor, 1f,
                    RM_StockMath.SeasonBand.Wet, 1f);
                Assert(storm > 4f * fair,
                    "a wet-season downpour must be a visibly different regime from bare seepage, or weather is decoration");
            });

            // ══════════════ recession and restoration (§5 "Recession, cell by cell") ══

            Case("SupportedCells_at_full_stock_is_the_whole_footprint", () =>
                Assert(RM_StockMath.SupportedCells(15f, 5f) == 3,
                    "a full 3-cell pond must support all 3 cells, or a body recedes the moment it forms"));

            Case("SupportedCells_floors_rather_than_rounds", () =>
                Assert(RM_StockMath.SupportedCells(9f, 5f) == 1,
                    "a body pays for a cell in full or gives it up; 9 units at 5/cell supports 1 cell, not 2"));

            Case("SupportedCells_of_an_empty_body_is_zero", () =>
                Assert(RM_StockMath.SupportedCells(0f, 5f) == 0, "a spent pond supports nothing"));

            Case("SupportedCells_never_returns_negative", () =>
                Assert(RM_StockMath.SupportedCells(-1f, 5f) == 0,
                    "a negative supported count would make the recession loop's guard the only thing between "
                    + "this and an unbounded shed"));

            Case("SupportedCells_with_no_per_cell_volume_is_zero_not_a_crash", () =>
                Assert(RM_StockMath.SupportedCells(10f, 0f) == 0, "divide-by-zero guard"));

            Case("SupportedCellsKeepingLast_keeps_one_cell_while_any_stock_remains", () =>
            {
                Assert(RM_StockMath.SupportedCellsKeepingLast(2f, 5f, true) == 1, "2 of 5 units must keep the last cell drawable");
                Assert(RM_StockMath.SupportedCellsKeepingLast(2f, 5f, false) == 0, "setting off: plain floor");
                Assert(RM_StockMath.SupportedCellsKeepingLast(0f, 5f, true) == 0, "a truly empty body still recedes fully");
                Assert(RM_StockMath.SupportedCellsKeepingLast(12f, 5f, true) == 2, "above one cell it is the plain floor");
            });

            Case("LocalRemovalKeepsConnected_detects_a_bridge_cell", () =>
            {
                // ring bits: 0 N, 1 NE, 2 E, 3 SE, 4 S, 5 SW, 6 W, 7 NW
                Assert(!RM_StockMath.LocalRemovalKeepsConnected((1 << 0) | (1 << 4)), "N and S only: centre is a bridge");
                Assert(!RM_StockMath.LocalRemovalKeepsConnected((1 << 2) | (1 << 6)), "E and W only: centre is a bridge");
                Assert(RM_StockMath.LocalRemovalKeepsConnected((1 << 0) | (1 << 2)), "N and E touch diagonally");
                Assert(RM_StockMath.LocalRemovalKeepsConnected((1 << 0) | (1 << 1) | (1 << 2) | (1 << 3) | (1 << 4)), "a full east half stays one group");
                Assert(RM_StockMath.LocalRemovalKeepsConnected(1 << 5), "a single neighbour is an end cell");
                Assert(RM_StockMath.LocalRemovalKeepsConnected(0), "an isolated cell");
                Assert(!RM_StockMath.LocalRemovalKeepsConnected((1 << 1) | (1 << 5)), "opposite diagonals are split");
            });

            Case("Recession_order_prefers_FEWEST_neighbours_first", () =>
                Assert(RM_StockMath.PrefersCandidate(2, 0, 0, 5, 999, 0),
                    "§5: fewest same-liquid neighbours first — that thins the body from its shallow edge "
                    + "and never fragments it. A low neighbour count must win even against a far better distance."));

            Case("Recession_order_tie_breaks_on_GREATEST_distance_from_centroid", () =>
            {
                Assert(RM_StockMath.PrefersCandidate(3, 100, 5, 3, 40, 1),
                    "equal neighbours: the cell further from the centroid recedes first");
                Assert(!RM_StockMath.PrefersCandidate(3, 40, 1, 3, 100, 5),
                    "and the nearer one does not");
            });

            Case("Recession_order_final_tie_break_is_the_deterministic_cell_index", () =>
            {
                Assert(RM_StockMath.PrefersCandidate(3, 40, 7, 3, 40, 9),
                    "🔑 with neighbours and distance both tied, the cell index decides — this is what makes "
                    + "recession survive a save/reload and be identical on every machine");
                Assert(!RM_StockMath.PrefersCandidate(3, 40, 9, 3, 40, 7), "and the order is strict, never ambiguous");
            });

            Case("Recession_order_is_a_STRICT_preference_so_an_incumbent_is_never_displaced_by_an_equal", () =>
                Assert(!RM_StockMath.PrefersCandidate(3, 40, 7, 3, 40, 7),
                    "a candidate identical to the incumbent must not displace it, or the scan's result depends "
                    + "on iteration order and determinism is lost"));

            // ───── hand-traced scenario: a small pond drawn down, then refilled

            Case("Scenario_three_cell_pond_drawn_down_recedes_then_recovers_its_cells", () =>
            {
                // A 3-cell water pond. capacity 15, perCell 5.
                float capacity = WaterCapacity(3);
                float perCell = RM_StockMath.PerCellVolume(capacity, 3);
                AssertClose(capacity, 15f, "capacity");
                AssertClose(perCell, 5f, "per-cell volume");

                float stock = capacity;
                Assert(RM_StockMath.SupportedCells(stock, perCell) == 3, "full: 3 cells standing");

                // A canal draws. Each canal cell debits volumePerTile (1 unit).
                for (int i = 0; i < 6; i++)
                {
                    Assert(RM_StockMath.CanDebit(false, stock, WaterVolumePerTile),
                        "a pond at " + stock + " must still afford a 1-unit debit");
                    stock -= WaterVolumePerTile;
                }
                AssertClose(stock, 9f, "after filling 6 canal cells");
                Assert(RM_StockMath.SupportedCells(stock, perCell) == 1,
                    "9 units supports 1 of 3 cells — the pond visibly gives up 2 cells to mud");

                // Drawn to nothing.
                stock = 0f;
                Assert(!RM_StockMath.CanDebit(false, stock, WaterVolumePerTile),
                    "🔴 a spent LIMITED body must refuse the debit. The caller must then NOT move liquid — "
                    + "a transfer after a failed debit is the silent leak the conservation ledger exists to catch.");
                Assert(!RM_StockMath.CanSupply(false, stock, WaterVolumePerTile),
                    "and it must stop being picked as a donor at all, so the picker can find a wet neighbour instead");
                Assert(RM_StockMath.SupportedCells(stock, perCell) == 0, "spent: the whole footprint is mud");

                // Now it rains for ten days in spring.
                float perDay = RM_StockMath.RefillPerDay(WaterOozePerCellPerDay, 3, WaterRainRefillFactor, 1f,
                    RM_StockMath.SeasonBand.Wet, 1f);
                for (int day = 0; day < 10; day++)
                {
                    stock = RM_StockMath.ClampToCapacity(stock, RM_StockMath.RefillForPulse(perDay, TicksPerDay, TicksPerDay), capacity);
                }
                Assert(stock > 0f, "a refilling body must actually gain");
                Assert(stock <= capacity, "and must never exceed capacity");
                Assert(RM_StockMath.SupportedCells(stock, perCell) >= 1,
                    "after ten wet days the pond must have won back at least its first cell — refill has to be VISIBLE (§5)");
            });

            Case("Scenario_a_limitless_edge_body_never_runs_down_and_never_recedes", () =>
            {
                // A 400-cell lake touching the map edge.
                Assert(RM_StockMath.IsLimitless(true, false, true, 400, DefaultMinLimitlessBodyCells),
                    "400 cells on the edge: LIMITLESS");
                // Stock is meaningless for it; every gate must pass on the flag alone,
                // with a stock field of literally zero.
                Assert(RM_StockMath.CanSupply(true, 0f, WaterVolumePerTile),
                    "🔑 the sentinel, not a big number: a limitless body supplies with a stock of 0 recorded");
                Assert(RM_StockMath.CanDebit(true, 0f, 9999f),
                    "and affords any debit, however large, without a magic literal anywhere");
                AssertClose(RM_StockMath.CreditAccepted(true, 0f, 0f, 42f), 42f,
                    "and accepts any credit back — the off-map continuation cannot be overfilled");
            });

            // ═══════════════════ credit: fill-in displacement (§5) and §8 pumps ══

            Case("Credit_to_a_limited_body_stops_at_capacity", () =>
                AssertClose(RM_StockMath.CreditAccepted(false, 12f, 15f, 10f), 3f,
                    "a pond with 3 units of room accepts 3 of the 10 offered; the other 7 are the caller's "
                    + "problem — and §5 says they overflow and are DESTROYED, disclosed rather than dropped"));

            Case("Credit_to_a_full_body_is_refused_entirely", () =>
                AssertClose(RM_StockMath.CreditAccepted(false, 15f, 15f, 10f), 0f, "no room, nothing accepted"));

            Case("Credit_below_capacity_is_accepted_whole", () =>
                AssertClose(RM_StockMath.CreditAccepted(false, 5f, 15f, 4f), 4f, "plenty of room"));

            Case("Credit_of_nothing_is_nothing", () =>
                AssertClose(RM_StockMath.CreditAccepted(false, 5f, 15f, 0f), 0f, "zero in, zero out"));

            Case("Credit_and_debit_round_trip_conserves_exactly", () =>
            {
                // The reversibility §5 promises: "fill it back in before a raid that
                // never came and you get most of your liquid back". Within capacity,
                // MOST becomes ALL, and that must hold to the unit.
                float capacity = WaterCapacity(3);
                float stock = capacity;
                int drawn = 0;
                for (int i = 0; i < 6; i++)
                {
                    Assert(RM_StockMath.CanDebit(false, stock, WaterVolumePerTile), "affordable");
                    stock -= WaterVolumePerTile;
                    drawn++;
                }
                float back = RM_StockMath.CreditAccepted(false, stock, capacity, drawn * WaterVolumePerTile);
                AssertClose(back, drawn * WaterVolumePerTile,
                    "everything drawn must fit back in, because the body had exactly that much room");
                stock += back;
                AssertClose(stock, capacity,
                    "🔑 conservation of mass: dig a canal and fill it straight back in, and the pond is whole again");
            });

            // ═══════ the fill-in displacement walk (CANAL_FILL_IN_DISPLACEMENT_1) ═
            //
            // OWNER, 2026-09-16: "There should also be a way to 'fill in' a canal
            // that displaces liquid BACK. It does not destroy liquid if there's a
            // place for it to go, but if it would 'overflow' it is destroyed."
            //
            // The grid walking (BFS order, terrain writes, the message) needs a
            // live Map and is NOT covered here. What IS covered is every number
            // the walk decides with: how much a raised cell displaces, how much
            // room a channel cell has, and how many whole levels a body takes.

            Case("Displaced_is_what_the_shallower_cell_can_no_longer_hold", () =>
                Assert(RM_StockMath.DisplacedLevels(4, 4) == 1,
                    "a brimming depth-4 cell raised to 3 sheds exactly one level"));

            Case("Displacing_a_cell_with_slack_sheds_NOTHING", () =>
            {
                // §5's own worked example: "a trench holding one level out of four
                // loses nothing when it is raised to three — the liquid simply sits
                // higher, which is what actually happens when you shovel earth in
                // under it."
                Assert(RM_StockMath.DisplacedLevels(4, 1) == 0, "1 of 4 raised to 3 still fits");
                Assert(RM_StockMath.DisplacedLevels(4, 3) == 0, "3 of 4 raised to 3 fits exactly");
                Assert(RM_StockMath.DisplacedLevels(4, 0) == 0, "a dry trench displaces nothing");
            });

            Case("Displacing_a_brimming_cell_at_every_depth_sheds_exactly_one", () =>
            {
                for (int d = 1; d <= 4; d++)
                {
                    Assert(RM_StockMath.DisplacedLevels(d, d) == 1,
                        $"depth {d} brimming sheds one level, never the whole column");
                }
            });

            Case("Displacing_an_unexcavated_cell_is_zero_not_negative", () =>
            {
                Assert(RM_StockMath.DisplacedLevels(0, 0) == 0, "nothing dug, nothing displaced");
                Assert(RM_StockMath.DisplacedLevels(0, 2) == 0, "a corrupt fill above a zero depth cannot go negative");
            });

            Case("Displacement_clamps_a_fill_that_exceeds_its_own_brim", () =>
                Assert(RM_StockMath.DisplacedLevels(2, 5) == 1,
                    "fill is clamped to the brim first, so a corrupt grid sheds one level, not four"));

            Case("CellRoom_is_the_gap_below_the_brim", () =>
            {
                Assert(RM_StockMath.CellRoom(4, 1) == 3, "a depth-4 cell holding 1 has 3 levels of room");
                Assert(RM_StockMath.CellRoom(4, 4) == 0, "a brimming cell has none");
                Assert(RM_StockMath.CellRoom(2, 5) == 0, "over-full never reads as negative room");
            });

            Case("CreditableLevels_converts_fill_units_to_WHOLE_levels", () =>
            {
                // 🔴 The unit bug this function exists to prevent. The grids count
                // LEVELS; a body's stock counts FILL-UNITS, and one level is
                // volumePerTile units — exactly what the pulse debits per level
                // poured out of a source. A walk that handed its level count
                // straight to a fill-unit credit would under-pay every liquid
                // whose volumePerTile is not 1.
                const float viscous = 2f;
                // 10 units of room at 2 units per level = 5 levels.
                Assert(RM_StockMath.CreditableLevels(false, 5f, 15f, 8, viscous) == 5,
                    "room in units, answer in levels");
                Assert(RM_StockMath.CreditableLevels(false, 5f, 15f, 3, viscous) == 3,
                    "never more than was offered");
            });

            Case("CreditableLevels_floors_rather_than_crediting_a_part_level", () =>
            {
                // A body with 3 units of room and a 2-unit level takes ONE level
                // and leaves 1 unit of room. Rounding up here would credit stock
                // that no cell ever gave up, which is a silent mass GAIN — the
                // mirror of the leak the conservation ledger hunts.
                Assert(RM_StockMath.CreditableLevels(false, 12f, 15f, 4, 2f) == 1,
                    "3 units of room at 2 per level is one whole level, not one and a half");
                Assert(RM_StockMath.CreditableLevels(false, 14f, 15f, 4, 2f) == 0,
                    "1 unit of room at 2 per level is no level at all");
            });

            Case("CreditableLevels_to_a_full_body_is_zero_so_the_rest_overflows", () =>
                Assert(RM_StockMath.CreditableLevels(false, 15f, 15f, 5, WaterVolumePerTile) == 0,
                    "a full pond takes nothing, and §5 destroys what finds no room — disclosed, not silent"));

            Case("CreditableLevels_to_a_LIMITLESS_body_takes_everything", () =>
                Assert(RM_StockMath.CreditableLevels(true, 0f, 0f, 9, WaterVolumePerTile) == 9,
                    "the off-map continuation cannot be overfilled (ruling 16), so it never causes an overflow"));

            Case("CreditableLevels_of_nothing_offered_is_nothing", () =>
            {
                Assert(RM_StockMath.CreditableLevels(false, 0f, 15f, 0, WaterVolumePerTile) == 0, "zero in, zero out");
                Assert(RM_StockMath.CreditableLevels(true, 0f, 0f, 0, WaterVolumePerTile) == 0,
                    "and limitless does not invent levels out of an empty offer");
            });

            Case("CreditableLevels_refuses_rather_than_dividing_by_a_zero_unit", () =>
                Assert(RM_StockMath.CreditableLevels(false, 0f, 15f, 4, 0f) == 0,
                    "a malformed FluidDef must not produce an unbounded credit; refusing shows up as "
                    + "disclosed overflow, which is the failure a player can actually see"));

            Case("Scenario_fill_in_one_end_of_a_full_canal_and_the_rest_gets_DEEPER", () =>
            {
                // §5's third consequence, the one the player must SEE: "the
                // receiving cells' fill tiers rise, so displacement is visible:
                // filling in one end of a canal makes the rest of it deeper."
                //
                // Four depth-4 cells, the first brimming and the rest holding 2.
                // Raise the first to depth 3; it sheds one level, which the
                // nearest channel cell below its brim takes.
                int[] depth = { 4, 4, 4, 4 };
                int[] fill = { 4, 2, 2, 2 };
                int displaced = RM_StockMath.DisplacedLevels(depth[0], fill[0]);
                Assert(displaced == 1, "one level comes out");
                int remaining = displaced;
                for (int i = 1; i < depth.Length && remaining > 0; i++)
                {
                    int take = Math.Min(RM_StockMath.CellRoom(depth[i], fill[i]), remaining);
                    fill[i] += take;
                    remaining -= take;
                }
                Assert(remaining == 0, "the channel had room, so nothing was destroyed");
                Assert(fill[1] == 3, "🔑 the neighbour is visibly deeper — that is the whole point of the mechanic");
                Assert(fill[2] == 2 && fill[3] == 2, "nearest first: the far end is untouched while the near end has room");
            });

            Case("Scenario_filling_in_a_sealed_full_canal_destroys_exactly_the_overflow", () =>
            {
                // No room anywhere and no body to take it: §5's one sanctioned
                // exception. The amount destroyed is the displacement and not one
                // level more.
                int[] depth = { 4, 4 };
                int[] fill = { 4, 4 };
                int remaining = RM_StockMath.DisplacedLevels(depth[0], fill[0]);
                for (int i = 1; i < depth.Length && remaining > 0; i++)
                {
                    int take = Math.Min(RM_StockMath.CellRoom(depth[i], fill[i]), remaining);
                    fill[i] += take;
                    remaining -= take;
                }
                Assert(remaining == 1, "one level had nowhere to go");
                Assert(fill[1] == 4, "and the brimming neighbour took none of it");
            });

            Case("Scenario_channel_is_served_BEFORE_the_body_so_displacement_stays_visible", () =>
            {
                // The two-phase ordering, stated as a number. A pond one cell away
                // with room to spare would swallow the whole displacement in a
                // single mixed breadth-first walk, leaving the canal exactly as it
                // was: mass conserved and every visible trace of it gone.
                int channelRoom = RM_StockMath.CellRoom(4, 2);
                int remaining = 2;
                int toChannel = Math.Min(channelRoom, remaining);
                remaining -= toChannel;
                int toBody = RM_StockMath.CreditableLevels(false, 0f, 99f, remaining, WaterVolumePerTile);
                Assert(toChannel == 2, "the channel takes what it can hold first");
                Assert(toBody == 0, "so the pond — which would have taken all of it — gets nothing");
            });

            Case("Scenario_displaced_liquid_the_channel_cannot_hold_goes_home_to_the_pond", () =>
            {
                // And the reverse: a sealed channel with a pond at the end loses
                // nothing at all. This is §5's reversibility argument — "fill it
                // back in before a raid that never came and you get most of your
                // liquid back."
                float capacity = WaterCapacity(3);
                float stock = capacity - 4f * WaterVolumePerTile; // four levels were dug out
                int remaining = 3;                                // and three are coming back
                int toChannel = RM_StockMath.CellRoom(4, 4);      // sealed: no room
                Assert(toChannel == 0, "the channel is brimming");
                int toBody = RM_StockMath.CreditableLevels(false, stock, capacity, remaining, WaterVolumePerTile);
                Assert(toBody == 3, "the pond had room for all three, so nothing is destroyed");
                stock += toBody * WaterVolumePerTile;
                remaining -= toBody;
                Assert(remaining == 0, "nothing left over to destroy");
                AssertClose(stock, capacity - WaterVolumePerTile,
                    "and the pond is back to exactly what the one remaining dug level took from it");
            });

            // ── flow order (FLOWWORKS_CHANNEL_OSCILLATION_1) ──────────────
            Case("FlowOrder_equal_depth_overflow_only_runs_away_from_the_source", () =>
            {
                // A brimming D=1 mouth (1 hop) may hand a level to the next cell
                // (2 hops) — and that cell may never hand it back. The back-gift is
                // exactly the period-2 shuttle measured live on plot D.
                Assert(RM_StockMath.MayFlowBetween(1, 0, 1, 2, 0, 1), "mouth -> next cell");
                Assert(!RM_StockMath.MayFlowBetween(2, 0, 1, 1, 0, 1), "next cell -> mouth is refused");
                Assert(!RM_StockMath.MayFlowBetween(2, 0, 1, 2, 0, 1), "equal key, equal depth: no sideways swap");
            });

            Case("FlowOrder_gravity_survives_at_an_equal_key", () =>
            {
                // No supplying source and no sink: every key is (0, 0), so only
                // gravity moves — a breach into a deeper cell still drains.
                Assert(RM_StockMath.MayFlowBetween(0, 0, 1, 0, 0, 3), "shallow -> deeper at equal key");
                Assert(!RM_StockMath.MayFlowBetween(0, 0, 3, 0, 0, 1), "deeper -> shallow at equal key is refused");
            });

            Case("FlowOrder_without_a_source_levels_run_toward_the_sink", () =>
            {
                Assert(RM_StockMath.MayFlowBetween(0, 5, 1, 0, 4, 1), "one hop nearer the sink");
                Assert(!RM_StockMath.MayFlowBetween(0, 4, 1, 0, 5, 1), "away from the sink is refused");
            });

            Case("FlowOrder_is_a_strict_order_so_no_level_can_return", () =>
            {
                // Exhaustive over a small key space: never both a->b and b->a, and
                // never a->a. That antisymmetry is the whole oscillation fix.
                for (int s1 = 0; s1 < 4; s1++)
                for (int k1 = 0; k1 < 4; k1++)
                for (int d1 = 1; d1 <= 4; d1++)
                for (int s2 = 0; s2 < 4; s2++)
                for (int k2 = 0; k2 < 4; k2++)
                for (int d2 = 1; d2 <= 4; d2++)
                {
                    bool ab = RM_StockMath.MayFlowBetween(s1, k1, d1, s2, k2, d2);
                    bool ba = RM_StockMath.MayFlowBetween(s2, k2, d2, s1, k1, d1);
                    Assert(!(ab && ba), $"both ways at ({s1},{k1},{d1}) / ({s2},{k2},{d2})");
                }
            });

            // LIQUID_BODY_FLUID_IDENTITY_1 step 2 (fluids never mix, owner Q3).
            Case("FluidsCompatible_wet_cell_refuses_a_different_fluid", () =>
            {
                var water = new object();
                var oil = new object();
                Assert(RM_StockMath.FluidsCompatible(true, water, water), "same fluid flows");
                Assert(!RM_StockMath.FluidsCompatible(true, water, oil), "oil may not enter a water cell");
                Assert(!RM_StockMath.FluidsCompatible(true, oil, water), "water may not enter an oil cell");
            });

            Case("FluidsCompatible_dry_or_unrecorded_cells_take_any_fluid", () =>
            {
                var water = new object();
                var oil = new object();
                Assert(RM_StockMath.FluidsCompatible(false, water, oil), "a dry cell is claimed by the first fluid");
                Assert(RM_StockMath.FluidsCompatible(true, (object)null, oil), "wet but unrecorded: legacy permissive");
                Assert(RM_StockMath.FluidsCompatible(true, water, (object)null), "unrecorded donor: legacy permissive");
            });

            // FLOWWORKS_BUILD_PROGRAM_1 Phase 3/7 viscosity: stride = ticksPerTile / water's, rounded, >= 1.
            Case("Viscosity_stride_from_ticksPerTile", () =>
            {
                Assert(RM_StockMath.ViscosityStride(60) == 1, "water moves every pulse");
                Assert(RM_StockMath.ViscosityStride(1) == 1, "faster than water still moves every pulse");
                Assert(RM_StockMath.ViscosityStride(180) == 3, "oil 180 -> 3");
                Assert(RM_StockMath.ViscosityStride(360) == 6, "tar 360 -> 6");
                Assert(RM_StockMath.ViscosityStride(480) == 8, "slime 480 -> 8");
                Assert(RM_StockMath.ViscosityStride(89) == 1 && RM_StockMath.ViscosityStride(90) == 2, "rounds half up");
            });

            Case("Viscosity_tar_moves_one_pulse_in_six_water_every_pulse", () =>
            {
                int tar = 0, water = 0;
                for (long p = 1; p <= 60; p++)
                {
                    if (RM_StockMath.FluidMovesThisPulse(p, 360)) tar++;
                    if (RM_StockMath.FluidMovesThisPulse(p, 60)) water++;
                }
                Assert(water == 60, "water gave on " + water + " of 60 pulses");
                Assert(tar == 10, "tar gave on " + tar + " of 60 pulses, want 10");
                bool gap = false;
                for (long p = 1; p <= 5; p++) gap |= !RM_StockMath.FluidMovesThisPulse(p, 360);
                Assert(gap, "tar moved on every one of 5 consecutive pulses: no lag");
            });

            // FLOWWORKS_SHARED_SOURCE_STALL_1: the production component walk.
            // A 3x1 body (sources at x=3..5, z=5); channel E runs (6..9,5) off the
            // body's east end, channel N runs (5,6..9) off the same corner cell.
            var srcCells = new HashSet<(int, int)> { (3, 5), (4, 5), (5, 5) };
            var dug = new HashSet<(int, int)>();
            for (int i = 1; i <= 4; i++) { dug.Add((5 + i, 5)); dug.Add((5, 5 + i)); }
            List<List<(int, int)>> Components(IEnumerable<(int, int)> seeds)
            {
                var visited = new HashSet<(int, int)>();
                var compSrc = new HashSet<(int, int)>();
                var q = new Queue<(int, int)>();
                var scratch = new List<(int, int)>();
                var all = new List<List<(int, int)>>();
                foreach (var s in seeds)
                {
                    if (visited.Contains(s)) continue;
                    var comp = new List<(int, int)>();
                    RM_StockMath.CollectComponent(s, c => srcCells.Contains(c), c => dug.Contains(c),
                        (c, into) => { into.Add((c.Item1, c.Item2 + 1)); into.Add((c.Item1 + 1, c.Item2));
                                       into.Add((c.Item1, c.Item2 - 1)); into.Add((c.Item1 - 1, c.Item2)); },
                        visited, compSrc, q, scratch, comp, 6000);
                    all.Add(comp);
                }
                return all;
            }

            Case("SharedSource_every_adjacent_channel_gets_the_source_either_dig_order", () =>
            {
                var east = new List<(int, int)>(); var north = new List<(int, int)>();
                for (int i = 1; i <= 4; i++) { east.Add((5 + i, 5)); north.Add((5, 5 + i)); }
                foreach (var order in new[] { east.Concat(north), north.Concat(east) })
                {
                    var comps = Components(order);
                    Assert(comps.Count == 2, $"two components, got {comps.Count}");
                    foreach (var comp in comps)
                    {
                        Assert(comp.Contains((5, 5)), "a channel component lacks the shared source (the stall)");
                        Assert(comp.Count == 5, $"4 channel cells + 1 source, got {comp.Count}");
                    }
                }
            });

            Case("SharedSource_source_joins_but_is_never_expanded_through", () =>
            {
                // (4,5) and (3,5) are sources too but touch no channel cell: an ocean
                // must not be walked just because one channel reaches its shore.
                var comps = Components(new[] { (6, 5) });
                Assert(!comps[0].Contains((4, 5)) && !comps[0].Contains((3, 5)), "walked into the body");
                Assert(comps[0].Count == 5, $"E channel + 1 source, got {comps[0].Count}");
            });

            Case("SharedSource_one_channel_touching_two_sources_lists_each_once", () =>
            {
                dug.Add((4, 6)); // touches source (4,5) and channel cell (5,6)
                try
                {
                    var comps = Components(new[] { (5, 6) });
                    int s45 = comps[0].Count(c => c == (4, 5)), s55 = comps[0].Count(c => c == (5, 5));
                    Assert(s45 == 1 && s55 == 1, $"sources listed (4,5)x{s45} (5,5)x{s55}");
                }
                finally { dug.Remove((4, 6)); }
            });

            // ── PIT_TEMPERATURE_SOFTENING_1 (PROVISIONAL constants) ──
            Case("PitExposure_coupling_never_weakens_and_pit_room_needs_half_deep", () =>
            {
                Assert(RM_PitExposureMath.Coupling(0.2f) == 1f && RM_PitExposureMath.Coupling(3f) == 3f, "coupling floor 1");
                Assert(RM_PitExposureMath.IsPitRoom(5, 9) && !RM_PitExposureMath.IsPitRoom(4, 9), "half rounds up");
                Assert(!RM_PitExposureMath.IsPitRoom(0, 0), "empty room is not a pit room");
            });
            Case("PitExposure_severity_rises_exposed_falls_sheltered_clamped", () =>
            {
                Assert(RM_PitExposureMath.NextSeverity(0.5f, true) > 0.5f, "rises");
                Assert(RM_PitExposureMath.NextSeverity(0.5f, false) < 0.5f, "falls");
                Assert(RM_PitExposureMath.NextSeverity(0.999f, true) == 1f && RM_PitExposureMath.NextSeverity(0.01f, false) == 0f, "clamped");
            });
            Case("PitExposure_resistance_falls_faster_with_rate_and_floors_at_zero", () =>
            {
                Assert(RM_PitExposureMath.NextResistance(5f, 2f) < RM_PitExposureMath.NextResistance(5f, 1f), "rate scales");
                Assert(RM_PitExposureMath.NextResistance(5f, 0f) == 5f, "rate 0 is the off dial");
                Assert(RM_PitExposureMath.NextResistance(0.01f, 1f) == 0f, "floor");
            });

            // ── SUPERDEEP_HOLDER_RETIRE_1: the grid trap rule (owner Q4, pit width) ──
            // PRODUCTION RM_PitTrapMath.cs. The holder model it replaces held ANY pawn on
            // ANY D=4 cell; these cases go red against that model (large pawn in 1x1 / 1x5).
            HashSet<(int, int)> PitRect(int x0, int z0, int w, int h)
            {
                var s = new HashSet<(int, int)>();
                for (int i = 0; i < w; i++) for (int j = 0; j < h; j++) s.Add((x0 + i, z0 + j));
                return s;
            }
            bool HeldIn(HashSet<(int, int)> pit, (int, int) c, float bodySize) =>
                RM_PitTrapMath.Held(true, pit.Contains(c), true, false, false,
                    RM_PitTrapMath.PitWidthAt((x, z) => pit.Contains((x, z)), c.Item1, c.Item2,
                        RM_PitTrapMath.RequiredWidth(bodySize)));

            Case("PitWidth_required_width_bands", () =>
            {
                Assert(RM_PitTrapMath.RequiredWidth(0.2f) == 1, "0.2 -> 1");
                Assert(RM_PitTrapMath.RequiredWidth(1.0f) == 1, "1.0 -> 1");
                Assert(RM_PitTrapMath.RequiredWidth(2.24f) == 1, "2.24 -> 1");
                Assert(RM_PitTrapMath.RequiredWidth(2.25f) == 2, "2.25 -> 2 (band edge)");
                Assert(RM_PitTrapMath.RequiredWidth(6.24f) == 2, "6.24 -> 2");
                Assert(RM_PitTrapMath.RequiredWidth(6.25f) == 3, "6.25 -> 3 (band edge)");
                Assert(RM_PitTrapMath.RequiredWidth(12.24f) == 3, "12.24 -> 3");
                Assert(RM_PitTrapMath.RequiredWidth(1.0f, 4f) == 2, "multiplier scales BodySize");
                Assert(RM_PitTrapMath.RequiredWidth(0f) == 1, "0 -> 1 floor");
            });

            Case("PitWidth_matrix_small_large_x_1x1_trench_2x2", () =>
            {
                // item verify: expected held = {T,T,T ; F,F,T}
                var p1 = PitRect(10, 10, 1, 1); var tr = PitRect(10, 10, 1, 5); var p2 = PitRect(10, 10, 2, 2);
                Assert(HeldIn(p1, (10, 10), 1.0f), "small in 1x1 held");
                Assert(HeldIn(tr, (10, 12), 1.0f), "small in 1x5 trench held");
                Assert(HeldIn(p2, (11, 11), 1.0f), "small in 2x2 held");
                Assert(!HeldIn(p1, (10, 10), 2.4f), "large (2.4) in 1x1 NOT held");
                Assert(!HeldIn(tr, (10, 12), 2.4f), "large in 1x5 trench NOT held");
                foreach (var c in p2) Assert(HeldIn(p2, c, 2.4f), $"large in 2x2 held at {c}");
            });

            Case("PitWidth_fill_in_one_cell_releases_large", () =>
            {
                var p2 = PitRect(10, 10, 2, 2);
                p2.Remove((11, 11));
                Assert(!HeldIn(p2, (10, 10), 2.4f), "2x2 broken by a fill-in -> large not held");
                Assert(HeldIn(p2, (10, 10), 1.0f), "small still held");
            });

            Case("PitWidth_diagonal_run_does_not_count", () =>
            {
                var diag = new HashSet<(int, int)> { (10, 10), (11, 11), (12, 12), (13, 13) };
                Assert(!HeldIn(diag, (11, 11), 2.4f), "diagonal cells are not a 2-wide pit");
                Assert(RM_PitTrapMath.MeasuredPitWidth((x, z) => diag.Contains((x, z)), 11, 11) == 1, "width 1");
                Assert(RM_PitTrapMath.MeasuredPitWidth((x, z) => PitRect(0, 0, 3, 3).Contains((x, z)), 2, 0) == 3, "3x3 corner width 3");
                Assert(RM_PitTrapMath.MeasuredPitWidth((x, z) => false, 0, 0) == 0, "not D4 -> 0");
            });

            Case("PitTrap_held_gates_and_step_rule", () =>
            {
                Assert(!RM_PitTrapMath.Held(false, true, true, false, false, true), "rule off -> free");
                Assert(!RM_PitTrapMath.Held(true, false, true, false, false, true), "not D4 -> free");
                Assert(!RM_PitTrapMath.Held(true, true, false, false, false, true), "own faction carve-out -> free");
                Assert(!RM_PitTrapMath.Held(true, true, true, true, false, true), "flying -> free");
                Assert(!RM_PitTrapMath.Held(true, true, true, false, true, true), "ladder -> free");
                Assert(RM_PitTrapMath.Held(true, true, true, false, false, true), "all gates -> held");
                Assert(RM_PitTrapMath.StepBlocked(true, 3) && RM_PitTrapMath.StepBlocked(true, 0), "held cannot step up");
                Assert(!RM_PitTrapMath.StepBlocked(true, 4), "held may move along the D4 floor");
                Assert(!RM_PitTrapMath.StepBlocked(false, 0), "unheld walks out");
                Assert(RM_PitTrapMath.IsPitDescent(0, 4) && RM_PitTrapMath.IsPitDescent(3, 4), "into D4 is a descent");
                Assert(!RM_PitTrapMath.IsPitDescent(4, 4) && !RM_PitTrapMath.IsPitDescent(4, 0) && !RM_PitTrapMath.IsPitDescent(0, 3),
                    "along / out / into D3 are not pit descents");
                AssertClose(RM_PitTrapMath.FallDamage(60f, 1f), 4.8f, "60 kg -> 4.8 blunt");
                AssertClose(RM_PitTrapMath.FallDamage(5f, 1f), 1f, "floor 1");
                AssertClose(RM_PitTrapMath.FallDamage(60f, 0f), 1f, "multiplier 0 still floors at 1");
            });

            // ── FLOWWORKS_PIT_FALL_ONLY_FORCED_1 + the pit_escape ladder bug (live FAIL 2026-10-06) ──
            Case("PitFall_only_forced_or_concealed", () =>
            {
                // (walkedStep, ontoUsableLadder, playerFaction, captured)
                Assert(RM_PitTrapMath.DescentFalls(false, false, true, false), "colonist blown/forced in: falls");
                Assert(RM_PitTrapMath.DescentFalls(false, true, true, false), "forced onto a ladder cell still falls");
                Assert(RM_PitTrapMath.DescentFalls(false, false, false, true), "enemy forced in: falls");
                Assert(!RM_PitTrapMath.DescentFalls(true, false, true, false), "colonist never falls by walking");
                Assert(!RM_PitTrapMath.DescentFalls(true, false, true, true), "...even with the own-faction capture setting on");
                Assert(!RM_PitTrapMath.DescentFalls(true, true, false, true), "climbing down a usable ladder is not a fall");
                Assert(RM_PitTrapMath.DescentFalls(true, false, false, true), "a captured non-colonist walking into an open pit still falls (stale route)");
                Assert(!RM_PitTrapMath.DescentFalls(true, false, false, false), "not captured, walked: no fall");
            });

            Case("PitRoute_ladder_way_out_and_never_in_by_accident", () =>
            {
                // 5x5 pit at (10..14, 10..14); ladder in the TOP ROW at (12, 14) — the runner's fixture.
                var pit = PitRect(10, 10, 5, 5);
                var ladder = (12, 14);
                bool IsPit(int x, int z) => pit.Contains((x, z));
                bool Lip(int x, int z) => !pit.Contains((x, z));
                bool LadderLowered(int x, int z) => (x, z) == ladder;
                bool HeldLowered(int x, int z) => pit.Contains((x, z)) && (x, z) != ladder;
                bool HeldRaised(int x, int z) => pit.Contains((x, z));
                bool NoLadder(int x, int z) => false;
                bool Free(int x, int z) => false;

                // A held friendly in the far corner, sent outside, below-left of the pit: the old
                // vanilla route left over the nearest lip and was vetoed. Now: walk IN the pit to the ladder.
                var r = RM_PitTrapMath.PlanRoute(IsPit, HeldLowered, LadderLowered, Lip, 10, 10, 5, 5, false, 4000);
                Assert(r.leg == RM_PitTrapMath.PitLeg.WalkToInPit && (r.x, r.z) == ladder, "held: to the ladder inside the pit, got " + r.leg + " " + r.x + "," + r.z);
                // On the ladder: one step up onto the lip, toward the destination.
                r = RM_PitTrapMath.PlanRoute(IsPit, HeldLowered, LadderLowered, Lip, 12, 14, 5, 5, false, 4000);
                Assert(r.leg == RM_PitTrapMath.PitLeg.StepTo && !pit.Contains((r.x, r.z))
                    && Math.Abs(r.x - 12) <= 1 && Math.Abs(r.z - 14) <= 1, "on the ladder: step to an adjacent lip cell");
                // Raised ladder (or a hostile, for whom a lowered ladder is no way out): nothing.
                r = RM_PitTrapMath.PlanRoute(IsPit, HeldRaised, NoLadder, Lip, 10, 10, 5, 5, false, 4000);
                Assert(r.leg == RM_PitTrapMath.PitLeg.Vanilla, "trapped: vanilla (reachability vetoes)");
                // A pawn this pit does not hold (colonist, own-faction carve-out): untouched.
                r = RM_PitTrapMath.PlanRoute(IsPit, Free, LadderLowered, Lip, 10, 10, 5, 5, false, 4000);
                Assert(r.leg == RM_PitTrapMath.PitLeg.Vanilla, "not held anywhere: vanilla");
                // Moving within the pit stays in the pit (never out over the lip and back in).
                r = RM_PitTrapMath.PlanRoute(IsPit, HeldLowered, LadderLowered, Lip, 10, 10, 14, 10, true, 4000);
                Assert(r.leg == RM_PitTrapMath.PitLeg.StayInPit, "in-pit destination: StayInPit");
                // Ladder in the interior with no lip beside it is not a way out by itself.
                var pit7 = PitRect(0, 0, 7, 7);
                r = RM_PitTrapMath.PlanRoute((x, z) => pit7.Contains((x, z)), (x, z) => pit7.Contains((x, z)) && (x, z) != (3, 3),
                    (x, z) => (x, z) == (3, 3), (x, z) => !pit7.Contains((x, z)), 0, 0, -5, -5, false, 4000);
                Assert(r.leg == RM_PitTrapMath.PitLeg.Vanilla, "interior ladder touching no lip: no exit leg");

                // From outside: open pits are never crossed; a pit-floor destination only via a ladder.
                r = RM_PitTrapMath.PlanRoute(IsPit, HeldLowered, LadderLowered, Lip, 5, 12, 20, 12, false, 4000);
                Assert(r.leg == RM_PitTrapMath.PitLeg.AvoidPits, "outside -> outside: AvoidPits");
                r = RM_PitTrapMath.PlanRoute(IsPit, HeldLowered, NoLadder, Lip, 5, 12, 11, 11, true, 4000);
                Assert(r.leg == RM_PitTrapMath.PitLeg.AvoidPits, "no ladder: the floor is refused (AvoidPits)");
                r = RM_PitTrapMath.PlanRoute(IsPit, HeldLowered, LadderLowered, Lip, 5, 20, 11, 11, true, 4000);
                Assert(r.leg == RM_PitTrapMath.PitLeg.WalkToAvoidPits && !pit.Contains((r.x, r.z))
                    && Math.Abs(r.x - 12) <= 1 && Math.Abs(r.z - 14) <= 1, "down a ladder: first the lip beside it");
                r = RM_PitTrapMath.PlanRoute(IsPit, HeldLowered, LadderLowered, Lip, 12, 15, 11, 11, true, 4000);
                Assert(r.leg == RM_PitTrapMath.PitLeg.StepTo && (r.x, r.z) == ladder, "beside the ladder: step onto it");
            });

            // ── FLOWWORKS_LADDER_RAISE_LOWER_1 (owner 2026-10-06): ladder up / ladder down ──
            Case("Ladder_raise_lower_usable_and_entry", () =>
            {
                // (raiseLowerOn, raised, prisonDoorOn, mayClimb)
                Assert(RM_PitTrapMath.LadderUsable(true, false, true, true), "lowered, colonist: climbs");
                Assert(!RM_PitTrapMath.LadderUsable(true, false, true, false), "lowered, hostile under the prison door: stays");
                Assert(!RM_PitTrapMath.LadderUsable(true, true, true, true), "raised: nobody, colonist included");
                Assert(!RM_PitTrapMath.LadderUsable(true, true, false, false), "raised blocks even with the prison door off");
                Assert(RM_PitTrapMath.LadderUsable(false, true, true, true), "raise/lower setting off: a 'raised' ladder counts as lowered");
                Assert(RM_PitTrapMath.LadderUsable(true, false, false, false), "prison door off: a lowered ladder lets anyone climb");

                // 5x5 pit (10..14, 10..14), ladder top-middle (12, 14); item on the floor at the centre.
                var pit = PitRect(10, 10, 5, 5);
                bool IsPit(int x, int z) => pit.Contains((x, z));
                bool Lip(int x, int z) => !pit.Contains((x, z));
                bool Lowered(int x, int z) => (x, z) == (12, 14);
                bool Raised(int x, int z) => false;
                Assert(RM_PitTrapMath.PitFloorEnterable(IsPit, Lowered, Lip, 12, 12, 4000), "lowered ladder: the floor is enterable (a hauler may fetch)");
                Assert(!RM_PitTrapMath.PitFloorEnterable(IsPit, Raised, Lip, 12, 12, 4000), "raised ladder: the floor is not enterable");
                Assert(!RM_PitTrapMath.PitFloorEnterable(IsPit, Lowered, Lip, 30, 30, 4000), "not a pit cell: no component, nothing to enter");
                // A ladder in a DIFFERENT pit does not let you into this one.
                var pitB = PitRect(20, 10, 5, 5);
                bool IsPitAB(int x, int z) => pit.Contains((x, z)) || pitB.Contains((x, z));
                bool LadderInB(int x, int z) => (x, z) == (22, 14);
                Assert(!RM_PitTrapMath.PitFloorEnterable(IsPitAB, LadderInB, (x, z) => !IsPitAB(x, z), 12, 12, 4000), "a ladder in another pit does not help");
                // An interior ladder touching no lip is no way down (matches PlanRoute's descent leg).
                var pit7 = PitRect(0, 0, 7, 7);
                Assert(!RM_PitTrapMath.PitFloorEnterable((x, z) => pit7.Contains((x, z)), (x, z) => (x, z) == (3, 3),
                    (x, z) => !pit7.Contains((x, z)), 1, 1, 4000), "interior ladder: not an entry");
                // Agreement with the pather: enterable <=> PlanRoute's descent leg is not AvoidPits.
                var r = RM_PitTrapMath.PlanRoute(IsPit, (x, z) => false, Lowered, Lip, 12, 20, 12, 12, true, 4000);
                Assert(r.leg != RM_PitTrapMath.PitLeg.AvoidPits, "lowered: pather plans a way down");
                r = RM_PitTrapMath.PlanRoute(IsPit, (x, z) => false, Raised, Lip, 12, 20, 12, 12, true, 4000);
                Assert(r.leg == RM_PitTrapMath.PitLeg.AvoidPits, "raised: pather refuses the floor");
            });

            Case("PitTrap_spike_damage_scales_with_body_size", () =>
            {
                Assert(RM_PitTrapMath.SpikeHits == 3, "three spike hits per descent");
                AssertClose(RM_PitTrapMath.SpikeDamagePerHit(1f, 1f), 40f / 3f, "human: 3 x 13.3 = 40 Sharp");
                AssertClose(RM_PitTrapMath.SpikeDamagePerHit(4f, 1f) * 3, 160f, "thrumbo-size: 160 total");
                Assert(RM_PitTrapMath.SpikeDamagePerHit(2f, 1f) > RM_PitTrapMath.SpikeDamagePerHit(1f, 1f), "bigger body, bigger hits");
                AssertClose(RM_PitTrapMath.SpikeDamagePerHit(1f, 2f), 80f / 3f, "multiplier scales linearly");
                AssertClose(RM_PitTrapMath.SpikeDamagePerHit(0.1f, 0f), 1f, "floor 1 per hit");
            });

            Case("FlowDoor_sluice_holds_small_grate_holds_prisoners", () =>
            {
                // (vanillaOpens, heldInPit, sealedRule, isSluice, sluiceRule, playerFaction, humanlike, width)
                Assert(!RM_PitTrapMath.FlowDoorOpens(true, true, true, false, true, true, true, 1), "held in a pit: grate shut even for a colonist");
                Assert(!RM_PitTrapMath.FlowDoorOpens(false, true, true, true, true, false, true, 2), "held in a pit: sluice shut even for a big humanlike");
                Assert(RM_PitTrapMath.FlowDoorOpens(true, true, false, false, true, true, true, 1), "sealed rule off: vanilla decides");
                Assert(RM_PitTrapMath.FlowDoorOpens(true, false, true, false, true, true, true, 1), "colonist outside a pit: opens");
                Assert(!RM_PitTrapMath.FlowDoorOpens(false, false, true, false, true, false, true, 1), "grate holds a human prisoner");
                Assert(!RM_PitTrapMath.FlowDoorOpens(false, false, true, false, true, false, false, 3), "grate holds a big beast");
                Assert(RM_PitTrapMath.FlowDoorOpens(false, false, true, true, true, false, true, 1), "sluice gives way to a human prisoner");
                Assert(RM_PitTrapMath.FlowDoorOpens(false, false, true, true, true, false, false, 2), "sluice gives way to a W=2 beast");
                Assert(!RM_PitTrapMath.FlowDoorOpens(false, false, true, true, true, false, false, 1), "sluice holds a small creature");
                Assert(!RM_PitTrapMath.FlowDoorOpens(false, false, true, true, false, false, true, 2), "sluice rule off: holds like a door");
            });

            // ── PIT_DEPTH_DRAW_OFFSET_1: pawns sink with D; D=4 lip is 1.2x a person (owner's 20 %) ──
            Case("PitDraw_sink_is_monotonic_in_depth_and_superdeep_clears_head_by_20pct", () =>
            {
                float k = RM_PitDrawMath.DefaultSinkPerLevel;
                for (int d = 0; d < 4; d++)
                    Assert(RM_PitDrawMath.SinkFor(d + 1, k) > RM_PitDrawMath.SinkFor(d, k), "deeper draws lower at D=" + (d + 1));
                AssertClose(RM_PitDrawMath.SinkFor(0, k), 0f, "surface: no sink");
                AssertClose(RM_PitDrawMath.SinkFor(9, k), RM_PitDrawMath.SinkFor(4, k), "clamped at superdeep");
                Assert(RM_PitDrawMath.WallOverHeadRatio(4, k, RM_PitDrawMath.HumanlikeFeetToHeadTop) >= 1.2f - 1e-4f, "D=4 wall >= 1.2x head");
                Assert(RM_PitDrawMath.WallOverHeadRatio(3, k, RM_PitDrawMath.HumanlikeFeetToHeadTop) < 1f, "D=3 does not bury a person");
                AssertClose(RM_PitDrawMath.SinkFor(4, 0f), 0f, "per-level 0 is the off dial");
            });
            Case("PitDraw_rises_and_lowers_smoothly_between_cells", () =>
            {
                float k = 0.3f;
                AssertClose(RM_PitDrawMath.SinkBetween(0, 4, 0f, k), 0f, "start of step: still at the lip");
                AssertClose(RM_PitDrawMath.SinkBetween(0, 4, 0.5f, k), 0.6f, "half way down");
                AssertClose(RM_PitDrawMath.SinkBetween(4, 0, 1f, k), 0f, "climbed out");
                AssertClose(RM_PitDrawMath.StepProgress(0.5f, 0.5f, 1.5f, 0.5f, 1.0f, 0.5f), 0.5f, "progress projects onto the step");
                AssertClose(RM_PitDrawMath.StepProgress(0.5f, 0.5f, 1.5f, 1.5f, -3f, -3f), 0f, "clamped low");
                AssertClose(RM_PitDrawMath.StepProgress(0.5f, 0.5f, 0.5f, 0.5f, 9f, 9f), 1f, "zero-length step");
            });

            // ── PIT_LIP_OCCLUDES_OUTSIDE_1: a pit pawn's drawn centre never drops past the near lip ──
            Case("PitDraw_sink_never_carries_the_centre_south_of_the_lip", () =>
            {
                float s4 = RM_PitDrawMath.SinkFor(4, 0.3f);
                // south row of a pit: cell 135 (centre 135.5), lip at 135 -> only half a cell of sink
                AssertClose(RM_PitDrawMath.ClampSinkToLip(s4, 135.5f, 135f), 0.5f, "south row: centre held on the lip");
                Assert(135.5f - RM_PitDrawMath.ClampSinkToLip(s4, 135.5f, 135f) >= 135f - 1e-4f, "drawn centre inside the opening");
                // two rows in: full superdeep sink fits
                AssertClose(RM_PitDrawMath.ClampSinkToLip(s4, 136.5f, 135f), s4, "room enough: full sink");
                AssertClose(RM_PitDrawMath.ClampSinkToLip(s4, 136.5f, float.NaN), s4, "no lip found: sink unchanged");
                AssertClose(RM_PitDrawMath.ClampSinkToLip(0f, 135.5f, 135f), 0f, "no sink stays none");
                AssertClose(RM_PitDrawMath.ClampSinkToLip(s4, 135.5f, 136f), 0f, "lip at or north of the centre: no sink");
            });

            // ── LIQUID_HEAT_PUSH_1: hot and icy liquid move the room through vanilla heat ──
            Case("LiquidHeat_kind_hot_cold_neither_and_both", () =>
            {
                Assert(RM_LiquidHeatMath.Kind(true, false) == 1, "hot alone is +1");
                Assert(RM_LiquidHeatMath.Kind(false, true) == -1, "cold alone is -1");
                Assert(RM_LiquidHeatMath.Kind(false, false) == 0, "neither pushes nothing");
                Assert(RM_LiquidHeatMath.Kind(true, true) == 0, "a def claiming both pushes nothing (safe reading)");
            });

            Case("LiquidHeat_cell_energy_scales_with_fill_and_strength_and_sign", () =>
            {
                float one = RM_LiquidHeatMath.CellEnergy(1, 1, 1f);
                Assert(one > 0f, "hot liquid pushes positive energy");
                AssertClose(RM_LiquidHeatMath.CellEnergy(1, 4, 1f), 4f * one, "a brim-full superdeep cell is four levels");
                AssertClose(RM_LiquidHeatMath.CellEnergy(1, 2, 2f), 4f * one, "strength multiplies");
                Assert(RM_LiquidHeatMath.CellEnergy(-1, 2, 1f) < 0f, "icy liquid pushes negative energy");
                AssertClose(RM_LiquidHeatMath.CellEnergy(1, 0, 1f), 0f, "a dry cell pushes nothing");
                AssertClose(RM_LiquidHeatMath.CellEnergy(0, 4, 1f), 0f, "plain water pushes nothing");
                AssertClose(RM_LiquidHeatMath.CellEnergy(1, 4, 0f), 0f, "strength 0 pushes nothing");
                // calibration: a superdeep cell brim-full of boiling water is about half a vanilla heater (21/s)
                float heater = 21f * RM_LiquidHeatMath.SecondsPerInterval;
                float pit = RM_LiquidHeatMath.CellEnergy(1, 4, 1f);
                Assert(pit > 0.4f * heater && pit < 0.75f * heater, "one full boiling pit cell is ~half a heater: " + pit + " vs " + heater);
            });

            Case("LiquidHeat_room_never_passes_its_target", () =>
            {
                // A 9-cell pit room at 20 C under a huge push: it may rise at most to 50 C (30 C x 9 cells = 270).
                float e = RM_LiquidHeatMath.RoomEnergy(1e6f, 20f, 9, 1f);
                Assert(e > 0f, "a cool room takes heat");
                Assert(20f + e / 9f <= RM_LiquidHeatMath.HotTargetC + 1e-3f, "a hot room overshot its target: " + (20f + e / 9f));
                AssertClose(RM_LiquidHeatMath.RoomEnergy(100f, RM_LiquidHeatMath.HotTargetC, 9, 1f), 0f, "a room at the target takes nothing");
                AssertClose(RM_LiquidHeatMath.RoomEnergy(100f, 70f, 9, 1f), 0f, "a room ABOVE a hot target is never cooled by hot liquid");
                float c = RM_LiquidHeatMath.RoomEnergy(-1e6f, 20f, 9, 1f);
                Assert(c < 0f, "a warm room is chilled by icy liquid");
                Assert(20f + c / 9f >= RM_LiquidHeatMath.ColdTargetC - 1e-3f, "a cold room undershot its target: " + (20f + c / 9f));
                AssertClose(RM_LiquidHeatMath.RoomEnergy(-100f, -10f, 9, 1f), 0f, "a room below 0 C is never warmed by icy liquid");
            });

            Case("LiquidHeat_room_cap_is_eight_heaters_per_interval", () =>
            {
                float heater = 21f * RM_LiquidHeatMath.SecondsPerInterval;
                // A 1000-cell hall at 0 C: the target allows 50,000; the cap must bind.
                float e = RM_LiquidHeatMath.RoomEnergy(1e7f, 0f, 1000, 1f);
                AssertClose(e, 8f * heater, "a hall over a lake takes eight heaters' worth, no more");
                AssertClose(RM_LiquidHeatMath.RoomEnergy(-1e7f, 40f, 1000, 1f), -8f * heater, "the cap binds for cold too");
                AssertClose(RM_LiquidHeatMath.RoomEnergy(1e7f, 0f, 1000, 2f), 16f * heater, "the cap scales with strength");
                AssertClose(RM_LiquidHeatMath.RoomEnergy(10f, 0f, 1000, 1f), 10f, "under the cap the sum passes whole");
                AssertClose(RM_LiquidHeatMath.RoomEnergy(10f, 0f, 0, 1f), 0f, "a room of no cells takes nothing");
            });

            Case("LiquidHeat_budget_bounds_cost_and_keeps_average_power", () =>
            {
                int v = RM_LiquidHeatMath.Budget(100, out float s1);
                Assert(v == 100 && s1 == 1f, "under the budget every cell is visited at face value");
                int big = RM_LiquidHeatMath.CellBudgetPerInterval * 4;
                v = RM_LiquidHeatMath.Budget(big, out float s2);
                Assert(v == RM_LiquidHeatMath.CellBudgetPerInterval, "a big lake visits only the budget");
                AssertClose(v * s2, big, "visited x scale equals the full count: average power is exact");
                v = RM_LiquidHeatMath.Budget(0, out float s3);
                Assert(v == 0 && s3 == 1f, "nothing to visit");
            });

            // ── FLOWWORKS_BUILD_PROGRAM_1 Phase 6: ruling 7's burn rates and the travelling front ──
            Case("Fire_burn_is_a_rate_on_the_ladder_one_level_a_day_source_one_per_five", () =>
            {
                int canal = RM_FireMath.TicksPerCanalLevel(1f);
                int source = RM_FireMath.TicksPerSourceLevel(5f);
                Assert(canal == 60000, "one canal level per day");
                Assert(source == 5 * canal, "source level takes five canal days (5:1)");
                int acc = 0, levels = 0;
                for (int p = 0; p < 240; p++) levels += RM_FireMath.LevelsDue(ref acc, 250, canal);
                Assert(levels == 1 && acc == 0, "240 pulses of 250 ticks burn exactly one level");
                acc = 0; levels = 0;
                for (int p = 0; p < 720; p++) levels += RM_FireMath.LevelsDue(ref acc, 250, canal);
                Assert(levels == 3, "a brimming 3-level cell burns about three days");
                acc = 0;
                Assert(RM_FireMath.LevelsDue(ref acc, 0, canal) == 0 && acc == 0, "no time, no burn");
            });
            Case("ExcavationSanity_corrupt_grid_is_clamped_and_palette_compacts", () =>
            {
                byte[] d = { 0, 9, 2, 3 };
                byte[] f = { 0, 4, 3, 1 };
                byte[] x = { 0, 1, 200, 3 };
                var r = RM_ExcavationSanityMath.Repair(d, f, x, 3, 4);
                Assert(d[1] == 4 && r.depthClamped == 1, "depth 9 clamps to 4");
                Assert(f[2] == 2 && r.fillClamped == 1, "fill 3 over depth 2 clamps to 2");
                Assert(x[2] == 0 && r.fluidKeyCleared == 1, "fluid key past the palette is cleared");
                Assert(RM_ExcavationSanityMath.Repair(d, f, x, 3, 4).Total == 0, "a second pass changes nothing");
                bool[] used = RM_ExcavationSanityMath.KeysInUse(x, 3);
                Assert(used[1] && !used[2] && used[3], "keys 1 and 3 in use, 2 not");
                byte[] remap;
                Assert(RM_ExcavationSanityMath.BuildCompaction(used, out remap) == 2, "palette shrinks 3 to 2");
                RM_ExcavationSanityMath.ApplyRemap(x, remap);
                Assert(x[1] == 1 && x[3] == 2, "key 3 remaps to 2");
                Assert(RM_ExcavationSanityMath.Repair(null, null, null, 0, 4).Total == 0, "null grids are skipped");
            });
            Case("Fire_front_fuse_is_outrunnable_detonation_is_fast_and_source_reach_bounded", () =>
            {
                Assert(RM_FireMath.FrontDue(100, 120, 1f) == 220, "fuse steps by ticksPerCell");
                Assert(RM_FireMath.FrontDue(100, 120, 2f) == 160, "speed multiplier halves the step");
                Assert(RM_FireMath.FrontDue(100, 0, 1f) == 101, "never zero: the front always moves forward in time");
                Assert(RM_FireMath.SourceHopsFor(false, 0, true) == 1, "entering a pond is hop 1");
                Assert(RM_FireMath.SourceHopsFor(true, 2, true) == 3, "walking a pond counts hops");
                Assert(RM_FireMath.SourceHopsFor(true, 5, false) == 0, "back into a channel resets");
                Assert(RM_FireMath.SourceHopAllowed(3, 3) && !RM_FireMath.SourceHopAllowed(4, 3), "reach bounds the pond walk");
                Assert(!RM_FireMath.SourceHopAllowed(1, 0), "reach 0: a source never lights");
                AssertClose(RM_FireMath.AttachChance(true), 1f, "ruling 22: a pit occupant always catches");
                Assert(RM_FireMath.AttachChance(false) < 1f, "a free pawn may step out unburned");
            });

            // ── PIT_FILL_EFFECTS_1: drowning only at D=4 for non-swimmers; poison keyed to fill ──
            Case("FillEffects_drowning_is_superdeep_nonswimmer_and_keyed_to_fill", () =>
            {
                float full = RM_FillEffectMath.DrowningPerCheck(4, 4, true, false, false, 1f);
                Assert(full > 0f, "brimming D=4 drowns a non-swimmer");
                Assert(1f / full <= 10.5f && 1f / full >= 9.5f, "about ten checks (one in-game hour) to death at brim");
                AssertClose(RM_FillEffectMath.DrowningPerCheck(1, 4, true, false, false, 1f), full / 4f, "F=1 drowns at a quarter rate");
                AssertClose(RM_FillEffectMath.DrowningPerCheck(4, 4, true, true, false, 1f), 0f, "a swimmer treads water");
                AssertClose(RM_FillEffectMath.DrowningPerCheck(4, 4, true, false, true, 1f), 0f, "a flier is not in it");
                AssertClose(RM_FillEffectMath.DrowningPerCheck(3, 3, false, false, false, 1f), 0f, "never shallower than D=4");
                AssertClose(RM_FillEffectMath.DrowningPerCheck(0, 4, true, false, false, 1f), 0f, "a dry pit drowns no one");
            });
            Case("FillEffects_poison_scales_with_fill_and_resistance", () =>
            {
                float full = RM_FillEffectMath.ToxinPerCheck(3, 3, 2.4f, 0f, false);
                AssertClose(full, 0.01f, "2.4/day at brim is 0.01 per 250-tick check");
                AssertClose(RM_FillEffectMath.ToxinPerCheck(1, 3, 2.4f, 0f, false), full / 3f, "one third full, one third dose");
                AssertClose(RM_FillEffectMath.ToxinPerCheck(3, 3, 2.4f, 0.5f, false), full / 2f, "half resistance, half dose");
                AssertClose(RM_FillEffectMath.ToxinPerCheck(3, 3, 2.4f, 1f, false), 0f, "immune");
                AssertClose(RM_FillEffectMath.ToxinPerCheck(3, 3, 0f, 0f, false), 0f, "water is not poison");
            });

            // ── SUPERDEEP_PRISON_ROOM_1: the pit wall bounds rooms; capture down from the lip ──
            Case("PitRoom_wall_splits_sides_and_lip_jobs_never_stand_in_the_pit", () =>
            {
                Assert(RM_PitRoomMath.SameSide(true, true) && RM_PitRoomMath.SameSide(false, false), "same side shares a room");
                Assert(!RM_PitRoomMath.SameSide(true, false), "the pit wall splits rooms");
                Assert(!RM_PitRoomMath.LipCandidate(true, true, 1f, 1.5f), "a superdeep cell is never a lip cell");
                Assert(!RM_PitRoomMath.LipCandidate(false, false, 1f, 1.5f), "an unstandable cell is not a lip");
                Assert(RM_PitRoomMath.LipCandidate(false, true, 1.41f, 1.5f), "a diagonal neighbour is a lip cell for touch");
                Assert(!RM_PitRoomMath.LipCandidate(false, true, 2f, 1.5f), "two cells away cannot touch");
                Assert(RM_PitRoomMath.KindOf("PrisonerConvert") == RM_PitRoomMath.LipKind.Interact, "convert down is an interaction");
                Assert(RM_PitRoomMath.KindOf("PrisonerAttemptRecruit") == RM_PitRoomMath.LipKind.Interact, "recruit is an interaction");
                Assert(RM_PitRoomMath.KindOf("DeliverFood") == RM_PitRoomMath.LipKind.Drop, "food is dropped down");
                Assert(RM_PitRoomMath.KindOf("TendPatient") == RM_PitRoomMath.LipKind.Touch, "tending touches");
                Assert(RM_PitRoomMath.KindOf("Mine") == RM_PitRoomMath.LipKind.None, "other jobs untouched");
                AssertClose(RM_PitRoomMath.RadiusFor(RM_PitRoomMath.LipKind.Interact), 6f, "vanilla interaction range");
            });
            Case("PitRoom_capture_down_needs_a_held_person_and_a_prison_bed", () =>
            {
                Assert(RM_PitRoomMath.CaptureDown(true, true, false, false, true, true) == RM_PitRoomMath.CaptureDownVerdict.Allowed, "held + prison = capture");
                Assert(RM_PitRoomMath.CaptureDown(true, true, false, false, false, true) == RM_PitRoomMath.CaptureDownVerdict.NotHeld, "too wide for the pit: not offered (Q4)");
                Assert(RM_PitRoomMath.CaptureDown(true, true, false, false, true, false) == RM_PitRoomMath.CaptureDownVerdict.NoPrisonBed, "a bare pit holds trapped enemies, not prisoners");
                Assert(RM_PitRoomMath.CaptureDown(true, false, false, false, true, true) == RM_PitRoomMath.CaptureDownVerdict.NotAPerson, "animals are not captured");
                Assert(RM_PitRoomMath.CaptureDown(false, true, false, false, true, true) == RM_PitRoomMath.CaptureDownVerdict.SettingOff, "setting off");
                Assert(RM_PitRoomMath.CaptureDown(true, true, true, false, true, true) == RM_PitRoomMath.CaptureDownVerdict.OwnSide, "own people are not captured");
            });

            // ── Phase 6 owed: explosions light, rain douses ──
            Case("Fire_explosions_light_and_rain_douses", () =>
            {
                Assert(RM_FireMath.ExplosionIgnites("Flame") && RM_FireMath.ExplosionIgnites("Bomb"), "flame and bomb light liquid");
                Assert(RM_FireMath.ExplosionIgnites("VWE_Incendiary"), "a mod incendiary lights liquid");
                Assert(!RM_FireMath.ExplosionIgnites("EMP") && !RM_FireMath.ExplosionIgnites("Extinguish")
                    && !RM_FireMath.ExplosionIgnites("Smoke") && !RM_FireMath.ExplosionIgnites(null), "EMP, foam, smoke never do");
                AssertClose(RM_FireMath.RainDouseChance(0f), 0f, "no rain, no douse");
                AssertClose(RM_FireMath.RainDouseChance(1f), 0.03f, "full rain 3% per check");
                AssertClose(RM_FireMath.RainDouseChance(2f), 0.03f, "capped at full rain");
            });

            // ── FLOWWORKS_QUARRY_DIGGING_1: canal-dig finds ──
            Case("DigFinds_guard_depth_size_budget", () =>
            {
                Assert(RM_DigDiscoveryMath.RollsAt(0, 1) && RM_DigDiscoveryMath.RollsAt(2, 3), "a deeper cut rolls");
                Assert(!RM_DigDiscoveryMath.RollsAt(3, 3) && !RM_DigDiscoveryMath.RollsAt(4, 2), "fill and re-dig pays nothing twice");
                Assert(!RM_DigDiscoveryMath.ReachesDeep(2) && RM_DigDiscoveryMath.ReachesDeep(3) && RM_DigDiscoveryMath.ReachesDeep(4), "deep and superdeep reach the deep grid");
                Assert(RM_DigDiscoveryMath.LumpSize(0f, 75) == 10 && RM_DigDiscoveryMath.LumpSize(0.9999f, 75) == 25, "a lump is 10-25");
                Assert(RM_DigDiscoveryMath.LumpSize(0.99f, 5) == 5, "never past the stack limit");
                AssertClose(RM_DigDiscoveryMath.Chance(1f), 0.015f, "1.5% per cut");
                AssertClose(RM_DigDiscoveryMath.Chance(0f), 0f, "multiplier 0 = never");
                AssertClose(RM_DigDiscoveryMath.Budget(1200f, 5f), 60f, "5% of the rock's units");
                AssertClose(RM_DigDiscoveryMath.Budget(0f, 5f), 0f, "no ore, no loose budget");
            });

            // ── Phase 8: the pump ──
            Case("Pump_unit_bridge", () =>
            {
                Assert(RM_PumpMath.TankUnitsPerLevel == 5, "a channel level is a bucket");
                Assert(RM_PumpMath.LevelsPerDay() == 240, "one level per pulse");
                Assert(RM_PumpMath.CyclesToFill(300) == 60 && RM_PumpMath.CyclesToFill(1) == 1 && RM_PumpMath.CyclesToFill(0) == 0, "cycles to fill round up");
            });

            // ── LIQUID_UNIT_CONTRACT_ROUNDTRIP_1: units cross every system join without appearing or vanishing ──
            Case("Liquid_unit_contract_roundtrip_conserves", () =>
            {
                string dir = AppContext.BaseDirectory;
                string defs = null;
                for (int up = 0; up < 12 && dir != null; up++)
                {
                    string cand = System.IO.Path.Combine(dir, "FlowWorks", "Defs", "LiquidTypes");
                    if (System.IO.Directory.Exists(cand)) { defs = cand; break; }
                    cand = System.IO.Path.Combine(dir, "Defs", "LiquidTypes");
                    if (System.IO.Directory.Exists(cand)) { defs = cand; break; }
                    dir = System.IO.Path.GetDirectoryName(dir);
                }
                Assert(defs != null, "FlowWorks Defs/LiquidTypes not found above the test binary");
                var reg = System.Xml.Linq.XDocument.Load(System.IO.Path.Combine(defs, "LiquidDefs", "RM_LiquidDefRegistry.xml"));
                var bottles = System.Xml.Linq.XDocument.Load(System.IO.Path.Combine(defs, "ThingDefs", "RM_LiquidBottles_Base.xml"));
                var liquids = new List<(int bottle, int bucket, int barrel)>();
                foreach (var d in reg.Descendants("bottled"))
                {
                    int Get(string n, int dflt) { var e = d.Descendants(n).FirstOrDefault(); return e == null ? dflt : int.Parse(e.Value.Trim()); }
                    liquids.Add((Get("unitsPerBottle", 1), Get("unitsPerBucket", 5), Get("unitsPerBarrel", 25)));
                }
                Assert(liquids.Count >= 9, "sanity probe: registry should list its liquids, found " + liquids.Count);
                var factors = new List<float> { 1f };
                foreach (var e in bottles.Descendants("capacityFactor"))
                    factors.Add(float.Parse(e.Value.Trim(), System.Globalization.CultureInfo.InvariantCulture));
                Assert(factors.Count > 3 && factors.Any(f => f != 1f), "sanity probe: container materials should carry non-1 factors");

                foreach (var l in liquids)
                {
                    // the contract: a channel level is a bucket; a barrel is five buckets; a bucket is five bottles
                    Assert(l.bucket == RM_PumpMath.TankUnitsPerLevel, "unitsPerBucket " + l.bucket + " != TankUnitsPerLevel");
                    Assert(l.barrel == 5 * l.bucket && l.bucket == 5 * l.bottle, "bottle/bucket/barrel ladder broke: " + l.bottle + "/" + l.bucket + "/" + l.barrel);
                }
                foreach (var l in liquids)
                foreach (float f in factors)
                {
                    int pumped = 12 * RM_PumpMath.TankUnitsPerLevel;     // pond -> canal -> pump: 12 levels
                    int tank = pumped, held = 0;
                    foreach (int baseUnits in new[] { l.barrel, l.bucket, l.bottle })
                    {
                        int units = RimMandrake.FlowWorks.LiquidTypes.RM_ContainerMaterialMath.ScaledUnits(baseUnits, f);
                        while (tank >= units) { tank -= units; held += units; }
                    }
                    Assert(tank + held == pumped, "fill leg created or lost liquid at factor " + f);
                    // pour back: each container returns exactly what it took (same ScaledUnits call both ways)
                    foreach (int baseUnits in new[] { l.bottle, l.bucket, l.barrel })
                    {
                        int units = RimMandrake.FlowWorks.LiquidTypes.RM_ContainerMaterialMath.ScaledUnits(baseUnits, f);
                        while (held >= units) { held -= units; tank += units; }
                    }
                    Assert(held == 0 && tank == pumped, "round trip did not return the pumped liquid at factor " + f + " (held " + held + ", tank " + tank + ")");
                }
                // can-fail: a mutated factor on the pour leg must break conservation
                int fill = RimMandrake.FlowWorks.LiquidTypes.RM_ContainerMaterialMath.ScaledUnits(25, 1.2f);
                int pour = RimMandrake.FlowWorks.LiquidTypes.RM_ContainerMaterialMath.ScaledUnits(25, 0.8f);
                Assert(fill != pour, "mutation probe: unequal factors must change the units, else this test cannot fail");
            });

            // ── Liquid machinery: converter cycle arithmetic ──
            Case("Converter_cycle_math", () =>
            {
                AssertClose(RimMandrake.FlowWorks.Machinery.RM_ConversionMath.BudgetPerRareTick(240f, 1f, 1f, 1f), 1f, "240 a day is one per rare tick");
                AssertClose(RimMandrake.FlowWorks.Machinery.RM_ConversionMath.BudgetPerRareTick(240f, 0.5f, 1f, 1f), 0.5f, "kludged tier runs at half");
                AssertClose(RimMandrake.FlowWorks.Machinery.RM_ConversionMath.BudgetPerRareTick(240f, 1f, 1f, 0f), 0f, "no sun, no work");
                Assert(RimMandrake.FlowWorks.Machinery.RM_ConversionMath.Batches(4f, 2, 1, 100, 100) == 2, "budget bounds batches");
                Assert(RimMandrake.FlowWorks.Machinery.RM_ConversionMath.Batches(40f, 2, 1, 3, 100) == 1, "input bounds batches");
                Assert(RimMandrake.FlowWorks.Machinery.RM_ConversionMath.Batches(40f, 2, 3, 100, 7) == 2, "output room bounds batches");
                Assert(RimMandrake.FlowWorks.Machinery.RM_ConversionMath.Batches(40f, 4, 1, 100, -1) == 10, "item fallback is unbounded");
                Assert(RimMandrake.FlowWorks.Machinery.RM_ConversionMath.Batches(1.9f, 2, 1, 100, 100) == 0, "a part batch waits");
                AssertClose(RimMandrake.FlowWorks.Machinery.RM_ConversionMath.CapAccrued(50f, 2, 0.25f), 2f, "idle budget never bursts");
                AssertClose(RimMandrake.FlowWorks.Machinery.RM_ConversionMath.SunFactor(0.8f, false), 1f, "open daylight");
                AssertClose(RimMandrake.FlowWorks.Machinery.RM_ConversionMath.SunFactor(0.8f, true), 0f, "roofed");
                AssertClose(RimMandrake.FlowWorks.Machinery.RM_ConversionMath.SunFactor(0.2f, false), 0f, "night");
            });

            // ── EXCAVATION_WALL_ART_1: every depth reads differently ──
            Case("WallFaces_every_depth_differs", () =>
            {
                float last = 0f;
                for (int d = 1; d <= 4; d++)
                {
                    float h = RM_WallFaceMath.NorthFaceHeight(RM_WallFaceMath.ExposedDrop(d, 0, 0));
                    Assert(h > last, "north face grows with depth at D=" + d);
                    last = h;
                }
                Assert(RM_WallFaceMath.FootDarkness(4) > RM_WallFaceMath.FootDarkness(3), "deeper foot is darker");
                Assert(RM_WallFaceMath.ExposedDrop(2, 3, 0) == 0, "no wall where the neighbour is deeper");
                Assert(RM_WallFaceMath.ExposedDrop(4, 0, 3) == 1, "liquid covers the foot");
                Assert(RM_WallFaceMath.ExposedDrop(3, 0, 3) == 0, "a brimming cut shows no face");
                Assert(RM_WallFaceMath.NorthFaceHeight(9) <= RM_WallFaceMath.NorthMax, "never taller than a cell");
            });

            // ── FLOWWORKS_VISUAL_PRINCIPLES_1 principle 1: a person-deep cut shows a wall-height face, deeper taller ──
            Case("WallFaces_D3_is_a_wall_D4_taller", () =>
            {
                // vanilla wall south face MEASURED ~0.25 cell (Wall_Atlas_Smooth / Rock_Atlas, 2026-10-05)
                float d3 = RM_WallFaceMath.NorthFaceHeight(3);
                Assert(d3 >= 0.25f && d3 <= 0.40f, "D3 face is about a vanilla wall's face: " + d3);
                Assert(RM_WallFaceMath.NorthFaceHeight(4) >= d3 * 1.4f, "D4 is visibly more extended than D3");
                float lastSide = 0f;
                for (int d = 1; d <= 4; d++)
                {
                    float s = RM_WallFaceMath.SideFaceWidth(d);
                    Assert(s > lastSide, "side face grows with depth at D=" + d);
                    lastSide = s;
                }
                Assert(RM_WallFaceMath.FaceFootLight(4) < RM_WallFaceMath.FaceFootLight(1), "deeper foot is dimmer");
                Assert(RM_WallFaceMath.FaceFootLight(1) < RM_WallFaceMath.FaceTopLight, "the top of a face is its lit edge");
            });

            // owner 2026-10-05 in game: "more of a black-lining on the southern edge of the pits"
            Case("SouthLining_thicker_than_north_and_grows", () =>
            {
                float last = 0f;
                for (int d = 1; d <= 4; d++)
                {
                    float w = RM_WallFaceMath.SouthLining(d);
                    Assert(w > last, "south lining grows with depth at D=" + d);
                    Assert(w > RM_WallFaceMath.RimLine, "south lining is thicker than the north rim line at D=" + d);
                    last = w;
                }
                AssertClose(RM_WallFaceMath.SouthLining(0), 0f, "no drop, no lining");
                Assert(RM_WallFaceMath.SouthLining(9) <= RM_WallFaceMath.SouthLining(4), "clamped past superdeep");
            });

            // owner 2026-10-06, of the starburst round: "those look ridiculous" — round 3 follows GPT concept art
            // (Transient/scorch_concept_2026-10-06): grey ash floor, char at walls and in patches, plumed walls, lobed halo
            Case("Scorch_ash_floor_char_walls_lobed_halo", () =>
            {
                Assert(RM_WallFaceMath.AshCover(1f, 0f) >= 0.8f, "full scorch: the floor is ash all over, not spots");
                AssertClose(RM_WallFaceMath.AshCover(0f, 1f), 0f, "no scorch, no ash");
                Assert(RM_WallFaceMath.AshCover(0.5f, 0.5f) < RM_WallFaceMath.AshCover(1f, 0.5f), "fading thins the ash");
                Assert(RM_WallFaceMath.CharCover(1f, 0.3f, 0f) > 0.8f, "char heavy against a wall");
                AssertClose(RM_WallFaceMath.CharCover(1f, 0.3f, 0.8f), 0f, "low-noise middle of the floor: ash, not char");
                Assert(RM_WallFaceMath.CharCover(1f, 0.9f, 0.8f) > 0.6f, "char patches where the noise runs high");
                Assert(RM_WallFaceMath.HeatTint(1f, 0.9f, 0.25f) > 0f && RM_WallFaceMath.HeatTint(1f, 0.9f, 0.25f) <= 0.3f, "heat tint is a faint accent near walls");
                AssertClose(RM_WallFaceMath.HeatTint(1f, 0.9f, 0.9f), 0f, "no tint mid-floor");
                Assert(RM_WallFaceMath.HaloCover(1f, 0f, 0.5f) > 0.7f && RM_WallFaceMath.HaloCover(1f, 0f, 1f) > RM_WallFaceMath.HaloCover(1f, 0f, 0f), "halo darkest at the lip, and uneven along it");
                AssertClose(RM_WallFaceMath.HaloCover(1f, 0.6f, 0f), 0f, "short lobe: gone by 0.6 cell");
                Assert(RM_WallFaceMath.HaloCover(1f, 0.6f, 1f) > 0.2f, "long lobe: still smoky at 0.6 cell");
                AssertClose(RM_WallFaceMath.HaloCover(1f, 1.5f, 1f), 0f, "never reaches past 1.4 cells");
                Assert(RM_WallFaceMath.FaceSoot(1f, 0.5f, 0.9f) > RM_WallFaceMath.FaceSoot(1f, 0.5f, 0.1f) + 0.35f, "plumes stand out on the face");
                Assert(RM_WallFaceMath.FaceSoot(1f, 0f, 0.1f) > RM_WallFaceMath.FaceSoot(1f, 0.5f, 0.1f), "heaviest at the foot");
                Assert(RM_WallFaceMath.FaceSoot(1f, 0f, 1f) <= 0.95f, "face soot capped");
                AssertClose(RM_WallFaceMath.FaceSoot(0f, 0f, 1f), 0f, "no scorch, no soot");
                Assert(RM_WallFaceMath.AshDepthShade(1) < RM_WallFaceMath.AshDepthShade(3) && RM_WallFaceMath.AshDepthShade(3) < RM_WallFaceMath.AshDepthShade(4), "a deeper burned pit still reads deeper");
            });

            // owner card 2026-10-06, round 4: "All of that plus debris" — dirt has its own look, drips, debris
            Case("Scorch_round4_dirt_drips_debris", () =>
            {
                Assert(RM_WallFaceMath.AshCover(1f, 0.2f, true) < RM_WallFaceMath.AshCover(1f, 0.2f, false) - 0.2f, "dirt: soil shows through the ash");
                Assert(RM_WallFaceMath.HeatTint(1f, 0.8f, 0.5f, true) > RM_WallFaceMath.HeatTint(1f, 0.8f, 0.5f, false), "dirt carries the reddish bake mid-floor");
                Assert(RM_WallFaceMath.HeatTint(1f, 0.8f, 0.3f, true) <= 0.3f, "the bake stays a tint");
                int lo = 99, hi = 0, total = 0, chars = 0, pieces = 0;
                bool inRange = true, stable = true;
                for (int x = 0; x < 60; x++)
                    for (int z = 0; z < 60; z++)
                    {
                        int n = RM_WallFaceMath.DripCount(x, z);
                        lo = System.Math.Min(lo, n); hi = System.Math.Max(hi, n);
                        RM_WallFaceMath.Drip(x, z, 0, out float u, out float w, out float len);
                        if (u < 0.06f || u > 0.94f || w < 0.03f || w > 0.09f || len < 0.35f || len > 1f) inRange = false;
                        int dn = RM_WallFaceMath.DebrisCount(1f, x, z);
                        total += dn;
                        if (RM_WallFaceMath.DebrisCount(1f, x, z) != dn) stable = false;
                        for (int k = 0; k < dn; k++)
                        {
                            RM_WallFaceMath.DebrisPiece(x, z, k, 0.6f, 12, out float lx, out float lz, out float sz, out float rot, out bool ch, out int v);
                            pieces++;
                            if (ch) chars++;
                            if (lx < 0.12f || lx > 0.88f || lz < 0.1f || lz > 0.5f || v < 0 || v > 11 || sz < 0.18f || sz > 0.38f) inRange = false;
                        }
                    }
                Assert(lo == 3 && hi == 6, "3..6 drips per far-wall cell: " + lo + ".." + hi);
                Assert(inRange, "drip and debris parameters stay in their ranges and on the floor");
                Assert(stable, "debris is a pure function of the cell (same after save/load)");
                Assert(total > 6000 && total < 8400, "about two pieces per burned cell: " + total);
                Assert(chars > pieces * 0.4 && chars < pieces * 0.7, "a mix of char lumps and ash flakes: " + chars + "/" + pieces);
                Assert(RM_WallFaceMath.DebrisCount(0f, 3, 3) == 0, "no scorch, no debris");
            });

            // owner 2026-10-06: acid/slime/boiling bubble; bubbles scale with view and stay bounded
            Case("Liquid_bubbles_rate", () =>
            {
                Assert(RM_LiquidLookMath.BubblesThisTick(0f, 1f, 600, 0f) == 0, "a liquid without bubbles never bubbles");
                Assert(RM_LiquidLookMath.BubblesThisTick(0.9f, 0f, 600, 0f) == 0, "density 0 = none");
                // 0.9/cell/s over 600 cells = 9 per tick expected -> capped
                Assert(RM_LiquidLookMath.BubblesThisTick(0.9f, 1f, 600, 0.99f) == RM_LiquidLookMath.MaxBubblesPerSample, "bounded per sample");
                // 0.08/cell/s over 60 cells = 0.08 per tick: rolls
                Assert(RM_LiquidLookMath.BubblesThisTick(0.08f, 1f, 60, 0.05f) == 1 && RM_LiquidLookMath.BubblesThisTick(0.08f, 1f, 60, 0.5f) == 0, "fraction is rolled");
                double heavy = 0, light = 0;
                for (int i = 0; i < 1000; i++)
                {
                    float r = i / 1000f;
                    heavy += RM_LiquidLookMath.BubblesThisTick(0.9f, 1f, 20, r);
                    light += RM_LiquidLookMath.BubblesThisTick(0.08f, 1f, 20, r);
                }
                Assert(heavy > light * 8, "boiling bubbles far more than slime: " + heavy + " vs " + light);
            });

            // owner 2026-10-06: "show the pit walls/floor beneath the translucent water"
            Case("Liquid_see_through", () =>
            {
                AssertClose(RM_LiquidLookMath.FloorSeeThroughAlpha(0f, 2), 0f, "opaque liquid hides the floor");
                AssertClose(RM_LiquidLookMath.FloorSeeThroughAlpha(0.55f, 0), 0f, "dry: nothing to see through");
                Assert(RM_LiquidLookMath.FloorSeeThroughAlpha(0.55f, 1) > RM_LiquidLookMath.FloorSeeThroughAlpha(0.55f, 3), "deeper hides more");
                Assert(RM_LiquidLookMath.FloorSeeThroughAlpha(0.55f, 4) >= 0f, "never negative");
                Assert(RM_LiquidLookMath.DrownedFaceAlpha(0.55f, 3, 1f) >= RM_LiquidLookMath.DrownedFaceAlpha(0.55f, 3, 0f), "face clearer toward the water line");
            });

            // owner 2026-10-06: "Only when they are climbing in or out do they move slowly. Falling into a pit is FAST.
            // Walking around within the pit is normal."
            Case("Pit_step_cost_walk_normal_climb_slow_fall_fast", () =>
            {
                for (int d = 1; d <= 4; d++) Assert(RM_PitTrapMath.DryStepBaseCost(d, d, 300) == 0, "same depth D" + d + " walks at normal speed");
                Assert(RM_PitTrapMath.DryStepBaseCost(0, 1, 30) == 30, "climbing into a shallow pit is slow");
                Assert(RM_PitTrapMath.DryStepBaseCost(3, 0, 80) == 80, "climbing out is slow");
                Assert(RM_PitTrapMath.DryStepBaseCost(2, 3, 80) == 80, "a step down a level is a climb");
                Assert(RM_PitTrapMath.DryStepBaseCost(0, 4, 300) == 0, "dropping into a superdeep pit is a fall: instant");
                Assert(RM_PitTrapMath.DryStepBaseCost(4, 0, 300) == 300, "out of a superdeep pit (the ladder) is the slowest climb");
            });

            Case("WallFace_mitre_and_measured_bevels", () =>
            {
                AssertClose(RM_WallFaceMath.NorthFaceHeight(3), 0.35f, "D3 = the measured steel-wall bevel band");
                AssertClose(RM_WallFaceMath.SideFaceWidth(3), 0.17f, "D3 side = the measured side bevel");
                AssertClose(RM_WallFaceMath.MitreInset(0.17f, 0.35f), 0.17f, "45-degree mitre steps in by the bevel width");
                AssertClose(RM_WallFaceMath.MitreInset(0f, 0.35f), 0f, "no side bevel, no mitre");
            });

            Case("LipOcclusion_band", () =>
            {
                // pawn centre 1.2 below its cell centre (D4 sink): sprite 10.05..11.55, lip at z=11 -> band 10.05..11
                Assert(RM_WallFaceMath.OccludedBand(11f, 10.05f, 11.55f, out float a, out float b), "D4 pawn hangs below the lip");
                AssertClose(a, 10.05f, "band starts at the sprite's bottom");
                AssertClose(b, 11f, "band stops at the lip");
                Assert(!RM_WallFaceMath.OccludedBand(11f, 11.2f, 12.4f, out _, out _), "a pawn wholly above the lip is not covered");
                Assert(RM_WallFaceMath.OccludedBand(11f, 10.2f, 10.9f, out _, out float b2) && b2 < 11f, "a pawn wholly below is covered to its top");
            });

            Case("LipOcclusion_occupant_cut", () =>
            {
                // FLOWWORKS_PIT_OCCUPANT_LIP_CUT_1: window of 1 cell around the occupant at x=5.5, cover piece 4.9..6.1
                int n = RM_WallFaceMath.CutCoverSpan(4.9f, 6.1f, 5f, 6f, out float l1, out float r1, out float l2, out float r2);
                Assert(n == 2, "a window inside the piece leaves two flanks");
                AssertClose(r1, 5f, "left flank stops at the window"); AssertClose(l2, 6f, "right flank starts after it");
                Assert(RM_WallFaceMath.CutCoverSpan(5.2f, 5.8f, 5f, 6f, out _, out _, out _, out _) == 0, "a piece wholly inside the window vanishes (occupant uncovered)");
                Assert(RM_WallFaceMath.CutCoverSpan(7f, 8f, 5f, 6f, out float a, out float b, out _, out _) == 1 && a == 7f && b == 8f, "a piece clear of the window stays whole");
                Assert(RM_WallFaceMath.CutCoverSpan(5.5f, 7f, 5f, 6f, out float c, out float d, out _, out _) == 1 && c == 6f && d == 7f, "a piece half in the window keeps its far side");
                // can-fail: the uncut cover would be the whole piece (what an occupant at D4 saw before the ruling)
                Assert(!(n == 1 && l1 == 4.9f && r1 == 6.1f), "can-fail: the cut changes the cover");
            });

            Case("StockReload_index_rebuild_rule", () =>
            {
                Assert(RM_StockMath.NeedsIndexRebuild(true, 0, 0), "dirty after load always rebuilds");
                Assert(RM_StockMath.NeedsIndexRebuild(false, 3, 0), "saved bodies with an empty index rebuild");
                Assert(!RM_StockMath.NeedsIndexRebuild(false, 3, 12), "a built index is left alone");
                Assert(!RM_StockMath.NeedsIndexRebuild(false, 0, 0), "no bodies, nothing to rebuild");
            });

            Case("LipOcclusion_skips_shallower_pawn", () =>
            {
                Assert(RM_WallFaceMath.CoverPieceHitsShallowerPawn(5f, 6f, 10.05f, 11f, 4.6f, 6.4f, 9.5f, 11.2f, 0, 4), "ground pawn under the band is not covered");
                Assert(!RM_WallFaceMath.CoverPieceHitsShallowerPawn(5f, 6f, 10.05f, 11f, 8f, 9f, 9.5f, 11.2f, 0, 4), "no overlap, still covered");
                Assert(!RM_WallFaceMath.CoverPieceHitsShallowerPawn(5f, 6f, 10.05f, 11f, 4.6f, 6.4f, 9.5f, 11.2f, 4, 4), "a pawn as deep is never exempt");
                Assert(RM_WallFaceMath.CoverPieceHitsShallowerPawn(5f, 6f, 10.05f, 11f, 4.6f, 6.4f, 9.5f, 11.2f, 2, 4), "a shallower pawn is exempt");
            });

            // ── principle 5: the scorch persists, fades in quarters, never fades at 0 days ──
            Case("Scorch_fade_rule", () =>
            {
                AssertClose(RM_WallFaceMath.ScorchStrength(0, 20f), 1f, "fresh scorch is full");
                AssertClose(RM_WallFaceMath.ScorchStrength(10L * 60000, 0f), 1f, "0 days = never fades");
                AssertClose(RM_WallFaceMath.ScorchStrength(20L * 60000, 20f), 0f, "gone at the fade time");
                float mid = RM_WallFaceMath.ScorchStrength(9L * 60000, 20f);
                Assert(mid > 0f && mid < 1f && Math.Abs(mid * 4f - Math.Round(mid * 4f)) < 1e-4, "quantised to quarters: " + mid);
                Assert(RM_WallFaceMath.ScorchDarken(1f) < RM_WallFaceMath.ScorchDarken(0.25f), "fuller scorch is darker");
                AssertClose(RM_WallFaceMath.ScorchDarken(0f), 1f, "no scorch, no darkening");
            });

            // ═══════════ FLOWWORKS_CONTAINER_MATERIALS_1 ruling 2 (card 2026-10-06 23:45) ══
            // The production rules file plus the SHIPPED XML numbers, read from the mod's own Defs.
            Case("ContainerMat_classify_stuff", () =>
            {
                Assert(RM_ContainerMaterialMath.Classify("Plasteel", new[] { "Metallic" }) == RM_ContainerMaterial.Plasteel, "plasteel is its own material");
                Assert(RM_ContainerMaterialMath.Classify("Steel", new[] { "Metallic" }) == RM_ContainerMaterial.Metal, "steel is metal");
                Assert(RM_ContainerMaterialMath.Classify("BlocksGranite", new[] { "Stony" }) == RM_ContainerMaterial.Glass, "any stone is glass");
                Assert(RM_ContainerMaterialMath.Classify("Leather_Plain", new[] { "Leathery" }) == RM_ContainerMaterial.Leather, "leather");
                Assert(RM_ContainerMaterialMath.Classify("WoodLog", new[] { "Woody" }) == RM_ContainerMaterial.Wood, "wood");
                Assert(RM_ContainerMaterialMath.Classify(null, null) == RM_ContainerMaterial.Unknown, "no stuff = unknown");
            });
            Case("ContainerMat_registry_hot_and_acid_flags", () =>
            {
                var liq = ContainerMatFixture.Liquids();
                Assert(liq["RM_Liquid_BoilingWater"].hot, "boiling water is hot");
                Assert(!liq["RM_Liquid_FreshWater"].hot && !liq["RM_Liquid_FreshWater"].acid, "fresh water is neither");
                Assert(liq["RM_Liquid_AcidWater"].acid, "acid water is acid");
                Assert(!liq["RM_Liquid_IcyWater"].hot && !liq["RM_Liquid_IcyWater"].acid, "icy water is neither");
                Assert(!liq["RM_Liquid_Tar"].acid && !liq["RM_Liquid_Brine"].acid, "tar and brine are not acid");
            });
            Case("ContainerMat_leather_refuses_hot_and_acid_every_size", () =>
            {
                var liq = ContainerMatFixture.Liquids();
                foreach (string fam in new[] { "RM_BottleItemBase", "RM_BucketItemBase" })
                {
                    var rule = RM_ContainerMaterialMath.RuleFor(ContainerMatFixture.Rules(fam), RM_ContainerMaterial.Leather);
                    Assert(rule != null, fam + " ships a leather rule");
                    var boil = liq["RM_Liquid_BoilingWater"]; var acid = liq["RM_Liquid_AcidWater"]; var fresh = liq["RM_Liquid_FreshWater"];
                    Assert(RM_ContainerMaterialMath.CanHold(rule, boil.hot, boil.acid) == RM_HoldRefusal.Hot, fam + " leather refuses boiling water (Hot)");
                    Assert(RM_ContainerMaterialMath.CanHold(rule, acid.hot, acid.acid) == RM_HoldRefusal.Acid, fam + " leather refuses acid (Acid)");
                    Assert(RM_ContainerMaterialMath.CanHold(rule, fresh.hot, fresh.acid) == RM_HoldRefusal.None, fam + " leather holds fresh water");
                }
            });
            Case("ContainerMat_wood_refuses_acid_holds_hot", () =>
            {
                var liq = ContainerMatFixture.Liquids();
                var boil = liq["RM_Liquid_BoilingWater"]; var acid = liq["RM_Liquid_AcidWater"]; var fresh = liq["RM_Liquid_FreshWater"];
                foreach (string fam in new[] { "RM_BucketItemBase", "RM_BarrelItemBase" })
                {
                    var rule = RM_ContainerMaterialMath.RuleFor(ContainerMatFixture.Rules(fam), RM_ContainerMaterial.Wood);
                    Assert(rule != null, fam + " ships a wood rule");
                    Assert(RM_ContainerMaterialMath.CanHold(rule, acid.hot, acid.acid) == RM_HoldRefusal.Acid, fam + " wood refuses acid (Acid)");
                    Assert(RM_ContainerMaterialMath.CanHold(rule, boil.hot, boil.acid) == RM_HoldRefusal.None, fam + " wood holds boiling water");
                    Assert(RM_ContainerMaterialMath.CanHold(rule, fresh.hot, fresh.acid) == RM_HoldRefusal.None, fam + " wood holds fresh water");
                }
            });
            Case("ContainerMat_glass_plasteel_hold_acid_metal_refuses", () =>
            {
                var liq = ContainerMatFixture.Liquids();
                var boil = liq["RM_Liquid_BoilingWater"]; var acid = liq["RM_Liquid_AcidWater"];
                var glass = RM_ContainerMaterialMath.RuleFor(ContainerMatFixture.Rules("RM_BottleItemBase"), RM_ContainerMaterial.Glass);
                Assert(glass != null && RM_ContainerMaterialMath.CanHold(glass, true, true) == RM_HoldRefusal.None, "glass bottle holds hot acid");
                foreach (string fam in new[] { "RM_BottleItemBase", "RM_BucketItemBase", "RM_BarrelItemBase" })
                {
                    var metal = RM_ContainerMaterialMath.RuleFor(ContainerMatFixture.Rules(fam), RM_ContainerMaterial.Metal);
                    Assert(metal != null, fam + " ships a metal rule");
                    Assert(RM_ContainerMaterialMath.CanHold(metal, acid.hot, acid.acid) == RM_HoldRefusal.Acid, fam + " metal refuses acid");
                    Assert(RM_ContainerMaterialMath.CanHold(metal, boil.hot, boil.acid) == RM_HoldRefusal.None, fam + " metal holds boiling water");
                }
                // Question card 2026-10-07 00:53: plasteel holds acid (and hot).
                var plasteel = RM_ContainerMaterialMath.RuleFor(ContainerMatFixture.Rules("RM_BarrelItemBase"), RM_ContainerMaterial.Plasteel);
                Assert(plasteel != null && RM_ContainerMaterialMath.CanHold(plasteel, true, true) == RM_HoldRefusal.None, "plasteel barrel holds hot acid");
                Assert(RM_ContainerMaterialMath.CanHold(null, true, true) == RM_HoldRefusal.None, "an unlisted material (no rule) holds anything");
            });
            Case("ContainerMat_only_leather_refuses_hot", () =>
            {
                foreach (string fam in new[] { "RM_BottleItemBase", "RM_BucketItemBase", "RM_BarrelItemBase" })
                    foreach (var r in ContainerMatFixture.Rules(fam))
                        Assert(r.holdsHot == (r.material != RM_ContainerMaterial.Leather), fam + " " + r.material + " holdsHot should be " + (r.material != RM_ContainerMaterial.Leather));
            });
            Case("ContainerMat_capacity_shipped_numbers", () =>
            {
                int U(string fam, RM_ContainerMaterial m, int baseUnits) =>
                    RM_ContainerMaterialMath.ScaledUnits(baseUnits, RM_ContainerMaterialMath.RuleFor(ContainerMatFixture.Rules(fam), m).capacityFactor);
                Assert(U("RM_BarrelItemBase", RM_ContainerMaterial.Wood, 25) == 25, "wood barrel 25");
                Assert(U("RM_BarrelItemBase", RM_ContainerMaterial.Metal, 25) == 30, "metal barrel 30");
                Assert(U("RM_BarrelItemBase", RM_ContainerMaterial.Plasteel, 25) == 40, "plasteel barrel 40");
                Assert(U("RM_BarrelItemBase", RM_ContainerMaterial.Plasteel, 25) > U("RM_BarrelItemBase", RM_ContainerMaterial.Metal, 25), "plasteel barrels hold more");
                Assert(U("RM_BucketItemBase", RM_ContainerMaterial.Wood, 5) == 5 && U("RM_BucketItemBase", RM_ContainerMaterial.Metal, 5) == 6
                    && U("RM_BucketItemBase", RM_ContainerMaterial.Leather, 5) == 4, "buckets wood 5 / metal 6 / leather 4");
                foreach (var m in new[] { RM_ContainerMaterial.Leather, RM_ContainerMaterial.Glass, RM_ContainerMaterial.Metal })
                    Assert(U("RM_BottleItemBase", m, 1) == 1, "every bottle holds 1");
            });
            Case("ContainerMat_scaled_units_rounding", () =>
            {
                Assert(RM_ContainerMaterialMath.ScaledUnits(1, 0.5f) == 1, "never below 1");
                Assert(RM_ContainerMaterialMath.ScaledUnits(1, 1.49f) == 1 && RM_ContainerMaterialMath.ScaledUnits(1, 1.5f) == 2, "half rounds away from zero");
                Assert(RM_ContainerMaterialMath.ScaledUnits(0, 2f) == 0, "no base, no units");
            });

            Case("ContainerMat_stone_bottle_reads_glass", () =>
            {
                Assert(RM_ContainerMaterialMath.RelabelAsGlass("granite empty bottle", "granite empty bottle", "glass empty bottle") == "glass empty bottle", "granite -> glass");
                Assert(RM_ContainerMaterialMath.RelabelAsGlass("marble bottled fresh water (45%)", "marble bottled fresh water", "glass bottled fresh water") == "glass bottled fresh water (45%)", "suffix kept");
                Assert(RM_ContainerMaterialMath.RelabelAsGlass("steel empty bottle", "granite empty bottle", "glass empty bottle") == "steel empty bottle", "absent phrase leaves label alone");
            });
            Case("ContainerMat_every_bottled_liquid_has_a_container_colour", () =>
            {
                var doc = System.Xml.Linq.XDocument.Load(System.IO.Path.Combine(ContainerMatFixture.Root(), "LiquidDefs", "RM_LiquidDefRegistry.xml"));
                int n = 0;
                foreach (var d in doc.Root.Elements("RimMandrake.FlowWorks.LiquidTypes.LiquidDef"))
                {
                    string bottle = (string)d.Element("bottled")?.Element("bottle");
                    if (bottle == null || !bottle.StartsWith("RM_")) continue;
                    n++;
                    string col = (string)d.Element("color");
                    Assert(col != null && col.Replace(" ", "") != "(1,1,1)", (string)d.Element("defName") + " ships no container colour (would show material colour when filled)");
                }
                Assert(n >= 9, "sanity: found " + n + " bottled rows, expected >= 9");
            });

            // ═══════════ Approach B: generated action sequences (design/RimMandrake/flowworks_offline_kernel_B.md) ══
            // Timing is a first-class output: each family prints its case count, step count and seconds.
            var fuzzClock = System.Diagnostics.Stopwatch.StartNew();
            FuzzCase("Fuzz_cell_body_tank_sequences", () => SequenceFuzz.Sequences(20000, 1));
            FuzzCase("Fuzz_flow_and_recession_orders_are_strict", () => SequenceFuzz.Orders(200000, 7));
            FuzzCase("Fuzz_converter_never_overspends", () => SequenceFuzz.Conversion(5000, 11));
            FuzzCase("Fuzz_pit_width_monotone", () => SequenceFuzz.PitWidth(20000, 13));
            Console.WriteLine($"fuzz total: {SequenceFuzz.Cases} cases, {SequenceFuzz.Steps} steps, {fuzzClock.Elapsed.TotalSeconds:F2} s");

            // ═══════════ Approach B phase 2: the PRODUCTION pulse kernel (RM_FlowKernel.cs) on generated grids ══
            var kernelClock = System.Diagnostics.Stopwatch.StartNew();
            KernelCase("Kernel_fuzz_ledger_bounds_nomix_settles", () => FlowKernelFuzz.Fuzz(5000, 101));
            KernelCase("Kernel_limitless_source_fills_its_component", () => FlowKernelFuzz.FillsFromLimitless(2000, 202));
            Case("FLOW_ORDER_EXTERNAL_INPUT_1_pump_fed_channel_spreads_and_settles", () =>
            {
                string r = FlowKernelFuzz.PumpFedChannelSpreads();
                Console.WriteLine("      " + r);
                Assert(r.StartsWith("OK"), r);
            });
            Console.WriteLine($"kernel total: {FlowKernelFuzz.Cases} scenes, {FlowKernelFuzz.Pulses} pulses, {kernelClock.Elapsed.TotalSeconds:F2} s");
            // Owner rulings 2026-10-06 (design/RimMandrake/flowworks_offline_kernel_B.md): regression guards.
            // TAKEN_BY_LAND_SERVICE_1 (X-10): the shared hold-and-return decisions, which the river and the dune gale both ride.
            Case("TAKEN_BY_LAND_SERVICE_1_kernel_decides_return_outcomes_and_schedules", () =>
            {
                Assert(RM_TakenByLandKernel.Decide(true, false, false, true) == TakenOutcome.LostMissing, "a missing pawn is lost");
                Assert(RM_TakenByLandKernel.Decide(false, true, false, true) == TakenOutcome.LostMissing, "a missing map loses the pawn");
                Assert(RM_TakenByLandKernel.Decide(false, false, true, true) == TakenOutcome.LostDead, "a dead pawn stays lost");
                Assert(RM_TakenByLandKernel.Decide(false, false, false, true) == TakenOutcome.SpawnAlive, "a good roll comes back alive");
                Assert(RM_TakenByLandKernel.Decide(false, false, false, false) == TakenOutcome.SpawnThenKill, "a bad roll comes back to die");
                Assert(!RM_TakenByLandKernel.ShouldScan(0, 250, 250) && !RM_TakenByLandKernel.ShouldScan(3, 251, 250) && RM_TakenByLandKernel.ShouldScan(3, 500, 250), "the book is scanned only when full and on the interval");
                Assert(RM_TakenByLandKernel.ReturnTick(1000, 1f, 60000) == 61000 && RM_TakenByLandKernel.ReturnTick(1000, 0f, 60000) == 1001, "return tick is days ahead, never before the next tick");
                Assert(RM_TakenByLandKernel.ReturnTick(int.MaxValue - 5, 10f, 60000) == int.MaxValue, "return tick saturates instead of overflowing");
                Assert(RM_TakenByLandKernel.IsDue(10, 10) && !RM_TakenByLandKernel.IsDue(11, 10), "due on its tick, not before");
                Assert(RM_TakenByLandKernel.EarlierEventOnMap(7, 100, 7, 200) && !RM_TakenByLandKernel.EarlierEventOnMap(7, 200, 7, 200) && !RM_TakenByLandKernel.EarlierEventOnMap(8, 100, 7, 200),
                    "a storm's end returns what an EARLIER event took from THIS map only");
                var book = new List<int> { 1, 2, 3, 4, 5 };
                var taken = RM_TakenByLandKernel.TakeWhere(book, x => x % 2 == 0);
                Assert(taken.Count == 2 && book.Count == 3 && !book.Contains(2) && !book.Contains(4), "TakeWhere removes exactly the picked records");
            });
            Case("THICK_LIQUID_CREEP_1_front_speed_down_a_40_cell_channel", () =>
            {
                string r = FlowKernelFuzz.FrontSpeed();
                Console.WriteLine("      " + r);
                Assert(r.StartsWith("OK"), r);
            });
            Case("Ruling1_touching_water_and_tar_stay_separate", () =>
            {
                string r = FlowKernelFuzz.TouchingFluidsStaySeparate();
                Console.WriteLine("      " + r);
                Assert(r.StartsWith("OK"), r);
            });
            Case("Ruling1_channel_touching_both_pools_never_mixes", () =>
            {
                string r = FlowKernelFuzz.ChannelTouchingBothNeverMixes();
                Console.WriteLine("      " + r);
                Assert(r.StartsWith("OK"), r);
            });
            Case("Ruling2_scarce_supply_paid_by_cell_index", () =>
            {
                string r = FlowKernelFuzz.ScarceSupplyPaidByPosition();
                Console.WriteLine("      " + r);
                Assert(r.StartsWith("OK"), r);
            });

            Case("Sluice_shut_seals_grate_passes", () =>
            {
                Assert(RM_PitTrapMath.FlowDoorSeals(true, false), "a shut sluice must seal");
                Assert(!RM_PitTrapMath.FlowDoorSeals(true, true), "an open sluice must pass liquid");
                Assert(!RM_PitTrapMath.FlowDoorSeals(false, false), "a shut grate must pass liquid");
                Assert(!RM_PitTrapMath.FlowDoorSeals(false, true), "an open grate must pass liquid");
                string r = FlowKernelFuzz.SluiceSealsGrateDoesNot();
                Console.WriteLine("      " + r);
                Assert(r.StartsWith("OK"), r);
            });

            Case("Sealed_sink_does_not_drain", () =>
            {
                string r = FlowKernelFuzz.SealedSinkHolds();
                Console.WriteLine("      " + r);
                Assert(r.StartsWith("OK"), r);
            });
            Case("CollectBody_exact_cap_not_truncated", () =>
            {
                string r = FlowKernelFuzz.CollectBodyExactCapNotTruncated();
                Console.WriteLine("      " + r);
                Assert(r.StartsWith("OK"), r);
            });

            Console.WriteLine($"\n{Pass.Count}/{Pass.Count + Fail.Count} passed");
            return Fail.Count == 0 ? 0 : 1;
        }
    }

    /// <summary>FLOWWORKS_CONTAINER_MATERIALS_1: reads the mod's SHIPPED XML (not a copy) so the
    /// selftest asserts the numbers the game loads.</summary>
    internal static class ContainerMatFixture
    {
        private static string defsRoot;

        public static string Root() => DefsRoot();

        private static string DefsRoot()
        {
            if (defsRoot != null) return defsRoot;
            var dir = new System.IO.DirectoryInfo(AppContext.BaseDirectory);
            while (dir != null && !System.IO.Directory.Exists(System.IO.Path.Combine(dir.FullName, "Defs", "LiquidTypes")))
                dir = dir.Parent;
            if (dir == null) throw new Exception("could not find FlowWorks Defs/LiquidTypes above " + AppContext.BaseDirectory);
            return defsRoot = System.IO.Path.Combine(dir.FullName, "Defs", "LiquidTypes");
        }

        public static Dictionary<string, (bool hot, bool acid)> Liquids()
        {
            var doc = System.Xml.Linq.XDocument.Load(System.IO.Path.Combine(DefsRoot(), "LiquidDefs", "RM_LiquidDefRegistry.xml"));
            var result = new Dictionary<string, (bool hot, bool acid)>();
            foreach (var d in doc.Root.Elements("RimMandrake.FlowWorks.LiquidTypes.LiquidDef"))
            {
                string V(string n) => (string)d.Element(n);
                bool acidBurn = d.Descendants("damageDef").Any(e => e.Value == "AcidBurn");
                float pH = V("pH") != null ? float.Parse(V("pH"), System.Globalization.CultureInfo.InvariantCulture) : 7f;
                result[V("defName")] = (V("hot") == "true",
                    RM_ContainerMaterialMath.IsAcid(pH, V("corrodesApparel") == "true", acidBurn));
            }
            return result;
        }

        public static List<RM_ContainerMaterialRule> Rules(string baseName)
        {
            var doc = System.Xml.Linq.XDocument.Load(System.IO.Path.Combine(DefsRoot(), "ThingDefs", "RM_LiquidBottles_Base.xml"));
            var def = doc.Root.Elements("ThingDef").First(e => (string)e.Attribute("Name") == baseName);
            var list = new List<RM_ContainerMaterialRule>();
            foreach (var li in def.Descendants("materials").SelectMany(m => m.Elements("li")))
            {
                list.Add(new RM_ContainerMaterialRule
                {
                    material = (RM_ContainerMaterial)Enum.Parse(typeof(RM_ContainerMaterial), (string)li.Element("material")),
                    capacityFactor = float.Parse((string)li.Element("capacityFactor"), System.Globalization.CultureInfo.InvariantCulture),
                    holdsHot = (string)li.Element("holdsHot") != "false",
                    holdsAcid = (string)li.Element("holdsAcid") != "false",
                });
            }
            return list;
        }
    }
}
