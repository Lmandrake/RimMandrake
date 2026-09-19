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
// for free, on the same discipline as Source/Pits/SelfTest/ and
// src/RimMandrake/Utils/selftest_validate_patch.py.
//
// WHAT IS REAL vs EXTRACTED:
//   EVERYTHING HERE IS REAL. RM_StockMath.cs is the PRODUCTION file, compiled
//   into this project directly (see the .csproj). It is not a transcription.
//   RM_LiquidStock calls every function asserted below, so a change to any
//   constant or clause fails this test immediately.
//
//   ⭐ That is a deliberate improvement on the Pits selftest next door, whose
//   own header flags its one weakness: its escape-chance formula is a hand
//   transcription that "keeps passing against the OLD formula" if the real
//   method changes. The §5 arithmetic needed no Map, Thing or IntVec3 to be
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

        private static int Main()
        {
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

            Console.WriteLine($"\n{Pass.Count}/{Pass.Count + Fail.Count} passed");
            return Fail.Count == 0 ? 0 : 1;
        }
    }
}
