// CHEMFUEL_MOAT_WIRE_MISSING_CHANNEL (owner by card, 2026-10-15): the two fuel fires' arithmetic, driven through the
// production RM_FuelFireMath / RM_FireMath. Chemfuel: fast spread, burn-down in seconds, every level accounted for.
// Astrofuel: one detonation empties every cell exactly once, inside per-tick budgets, with every cell under a blast.
// Each budget case carries a can-fail: the naive schedule (no budget) computed beside it must break the same bound.
using System;
using System.Collections.Generic;
using System.Diagnostics;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class FuelFireChecks
    {
        private static void Assert(bool cond, string msg)
        {
            if (!cond) throw new Exception(msg);
        }

        // RM_FireMath's 250-tick default pulse (RimMandrakeFlowWorksSettings.pulseIntervalTicks).
        private const int Pulse = 250;
        private const int ChemfuelTicksPerCell = 2;   // FlowWorks_PitFluids.xml RM_Fluid_Chemfuel fireFrontTicksPerCell
        private const int OilTicksPerCell = 90;       // RM_Fluid_Oil

        private static int FrontTime(int cells, int ticksPerCell, float speed)
        {
            int due = 0;
            for (int k = 1; k < cells; k++) due = RM_FireMath.FrontDue(due, ticksPerCell, speed);
            return due;
        }

        // A rider on burning squares under an intact solid deck through one burn of `checks` effects checks `gap` ticks apart,
        // driven through the shipped RM_FireMath.DeckExposureRolls: the chance it catches at least once, and how many rolls it had.
        private static double SolidBurnChance(float p, int checks, int gap, out int rolls)
        {
            int last = -1, t = 0;
            double miss = 1;
            rolls = 0;
            for (int k = 0; k < checks; k++)
            {
                t += gap;
                if (RM_FireMath.DeckExposureRolls(last, t)) { rolls++; miss *= 1 - p; }
                last = t;
            }
            return 1 - miss;
        }

        // A body walked breadth-first from (ox,oz) over a w x h rectangle: the BFS order and rings the Verse side builds.
        private static void Body(int w, int h, int ox, int oz, out int[] ring, out int[] x, out int[] z)
        {
            var r = new List<int>(); var xs = new List<int>(); var zs = new List<int>();
            var seen = new bool[w, h];
            var q = new Queue<(int, int, int)>();
            q.Enqueue((ox, oz, 0)); seen[ox, oz] = true;
            while (q.Count > 0)
            {
                var (cx, cz, d) = q.Dequeue();
                r.Add(d); xs.Add(cx); zs.Add(cz);
                foreach (var (dx, dz) in new[] { (1, 0), (-1, 0), (0, 1), (0, -1) })
                {
                    int nx = cx + dx, nz = cz + dz;
                    if (nx < 0 || nz < 0 || nx >= w || nz >= h || seen[nx, nz]) continue;
                    seen[nx, nz] = true;
                    q.Enqueue((nx, nz, d + 1));
                }
            }
            ring = r.ToArray(); x = xs.ToArray(); z = zs.ToArray();
        }

        private static string CheckPlan(int w, int h, int ox, int oz, out double ms)
        {
            Body(w, h, ox, oz, out int[] ring, out int[] x, out int[] z);
            int n = ring.Length;
            var consume = new int[n];
            var blast = new int[n];
            var clock = Stopwatch.StartNew();
            int spacing = RM_FuelFireMath.PlanDetonation(ring, x, z, RM_FuelFireMath.DetonationTicksPerRing,
                RM_FuelFireMath.MaxCellsConsumedPerTick, RM_FuelFireMath.MaxBlastsPerTick, RM_FuelFireMath.MaxBlastsPerDetonation,
                RM_FuelFireMath.BaseBlastSpacing, consume, blast);
            ms = clock.Elapsed.TotalMilliseconds;
            var perTickCells = new Dictionary<int, int>();
            var perTickBlasts = new Dictionary<int, int>();
            var anchors = new List<int>();
            int last = 0;
            for (int k = 0; k < n; k++)
            {
                Assert(consume[k] >= 0, "cell " + k + " never emptied");
                Assert(consume[k] >= ring[k] * RM_FuelFireMath.DetonationTicksPerRing, "cell " + k + " emptied before the wave reached it");
                perTickCells[consume[k]] = perTickCells.TryGetValue(consume[k], out int c) ? c + 1 : 1;
                if (blast[k] >= 0)
                {
                    Assert(blast[k] >= consume[k], "a blast before its cell was reached");
                    perTickBlasts[blast[k]] = perTickBlasts.TryGetValue(blast[k], out int b) ? b + 1 : 1;
                    anchors.Add(k);
                }
                last = Math.Max(last, Math.Max(consume[k], blast[k]));
            }
            int maxCells = 0, maxBlasts = 0;
            foreach (int v in perTickCells.Values) maxCells = Math.Max(maxCells, v);
            foreach (int v in perTickBlasts.Values) maxBlasts = Math.Max(maxBlasts, v);
            Assert(maxCells <= RM_FuelFireMath.MaxCellsConsumedPerTick, "a tick empties " + maxCells + " cells");
            Assert(maxBlasts <= RM_FuelFireMath.MaxBlastsPerTick, "a tick starts " + maxBlasts + " blasts");
            Assert(anchors.Count >= 1 && anchors.Count <= RM_FuelFireMath.MaxBlastsPerDetonation, anchors.Count + " blasts");
            // coverage: every cell within the anchor spacing of some blast, and the spacing inside the blast radius
            // the spacing only grows when the blast cap binds, and the radius grows with it
            Assert(spacing == RM_FuelFireMath.BaseBlastSpacing || anchors.Count * 2 > RM_FuelFireMath.MaxBlastsPerDetonation,
                "spacing " + spacing + " grew with only " + anchors.Count + " blasts");
            Assert(RM_FuelFireMath.BlastRadiusFor(1f, spacing) >= Math.Min(spacing * 0.8f, 7.9f) - 0.01f, "radius does not grow with spacing");
            var grid = new HashSet<(int, int)>();
            foreach (int a in anchors) grid.Add((x[a], z[a]));
            for (int k = 0; k < n; k++)
            {
                bool near = false;
                for (int dx = -(spacing - 1); dx <= spacing - 1 && !near; dx++)
                    for (int dz = -(spacing - 1); dz <= spacing - 1 && !near; dz++)
                        near = grid.Contains((x[k] + dx, z[k] + dz));
                Assert(near, "cell " + x[k] + "," + z[k] + " lies under no blast");
            }
            return $"{w}x{h}: {n} cells, {anchors.Count} blasts (spacing {spacing}), {last} ticks, max {maxCells} cells / {maxBlasts} blasts per tick, plan {ms:F1} ms";
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("FuelFire_classify_kinds_and_settings", () =>
            {
                Assert(RM_FuelFireMath.Classify(true, false, true, true) == RM_FuelBurn.Inferno, "chemfuel lit is an inferno");
                Assert(RM_FuelFireMath.Classify(false, true, true, true) == RM_FuelBurn.Detonation, "astrofuel lit detonates");
                Assert(RM_FuelFireMath.Classify(true, false, false, true) == RM_FuelBurn.Ordinary, "inferno off: chemfuel burns like oil");
                Assert(RM_FuelFireMath.Classify(false, true, true, false) == RM_FuelBurn.Inferno, "detonation off: astrofuel burns as an inferno");
                Assert(RM_FuelFireMath.Classify(false, true, false, false) == RM_FuelBurn.Ordinary, "both off: astrofuel burns like oil");
                Assert(RM_FuelFireMath.Classify(false, false, true, true) == RM_FuelBurn.Ordinary, "tar and oil are untouched");
            });

            Case("FuelFire_inferno_spreads_like_gasoline", () =>
            {
                // a 100-cell moat: lit end to end in seconds; the same moat of oil takes minutes
                int chem = FrontTime(100, ChemfuelTicksPerCell, RM_FuelFireMath.InfernoFrontSpeed(1f, 1f));
                int oil = FrontTime(100, OilTicksPerCell, 1f);
                Console.WriteLine($"      100-cell moat: chemfuel {chem} ticks ({chem / 60f:F1} s), oil {oil} ticks");
                Assert(chem <= 300, "chemfuel took " + chem + " ticks to run 100 cells");
                Assert(oil > 20 * chem, "can-fail: oil is not a fuse beside it");
                Assert(FrontTime(100, ChemfuelTicksPerCell, RM_FuelFireMath.InfernoFrontSpeed(1f, 0.25f)) > chem, "spread dial slows it");
            });

            Case("FuelFire_inferno_burns_down_in_seconds_and_conserves", () =>
            {
                int tpl = RM_FuelFireMath.InfernoTicksPerLevelAt(1f);
                var rnd = new Random(1015);
                int cells = 60;
                var level = new int[cells];
                var acc = new int[cells];
                int start = 0;
                for (int k = 0; k < cells; k++) { level[k] = 1 + rnd.Next(RM_Volume.LevelsPerSquare); start += level[k]; }
                int burned = 0, ticks = 0;
                while (ticks < 100000)
                {
                    bool any = false;
                    for (int k = 0; k < cells; k++)
                    {
                        if (level[k] == 0) continue;
                        int l = RM_FireMath.CanalLevelsToBurn(true, ref acc[k], Pulse, tpl);
                        int take = Math.Min(l, level[k]);
                        level[k] -= take; burned += take;
                        any |= level[k] > 0;
                    }
                    ticks += Pulse;
                    if (!any) break;
                }
                Console.WriteLine($"      {cells} cells, {start} levels: all gone in {ticks} ticks ({ticks / 60f:F0} s); oil would take {RM_FireMath.TicksPerCanalLevel(1f) * RM_Volume.LevelsPerSquare} ticks a brim cell");
                Assert(burned == start, "burned " + burned + " of " + start + " levels");
                Assert(ticks <= 60 * 60, "a brim moat took " + ticks + " ticks (over a minute)");
                Assert(RM_FireMath.TicksPerCanalLevel(1f) * RM_Volume.LevelsPerSquare > 100 * ticks, "can-fail: ruling 7's day-a-level beside it");
                Assert(RM_FuelFireMath.InfernoTicksPerLevelAt(4f) < tpl && RM_FuelFireMath.InfernoTicksPerLevelAt(0.25f) > tpl, "burn-rate dial");
            });

            Case("FuelFire_inferno_heat_and_halo_scale", () =>
            {
                Assert(RM_FuelFireMath.InfernoHeatPerCheck(1f) >= 8 * 60f, "an inferno pushes 8x ordinary liquid fire heat");
                Assert(RM_FuelFireMath.InfernoIgniteRadius(1f) >= 2.9f, "the halo reaches past a 1-wide moat's banks");
                Assert(RM_FuelFireMath.InfernoIgniteRadius(10f) <= 7.9f && RM_FuelFireMath.InfernoIgniteRadius(0f) >= 1.5f, "halo clamps");
                Assert(RM_FuelFireMath.InfernoHaloTriesPerCheck >= RM_FuelFireMath.InfernoHaloTriesPerCell, "halo budget");
            });

            Case("FuelFire_detonation_channel_goes_almost_at_once", () =>
            {
                string r = CheckPlan(60, 1, 0, 0, out _);
                Console.WriteLine("      " + r);
                Body(60, 1, 0, 0, out int[] ring, out _, out _);
                Assert(ring[ring.Length - 1] * RM_FuelFireMath.DetonationTicksPerRing <= 150, "a 60-cell channel takes over 2.5 s");
            });

            // RIMMANDRAKE_GATE_INFERNO_DECK_CHANCE_SOLID_OUTBURNS_GRATE (flowworks_bridges_design_2026-10-17 §4.1): over a chemfuel
            // inferno a SOLID deck gives the people on it the low onCover chance; a GRATE passes the fire up. Range read: every
            // combination of flying, held (down in the hole), on an intact deck and grated, in the cell and beside it with the
            // source cell open, grated or under a solid deck. Left out: the halo (vanilla fires on dry ground, no deck read).
            Case("FuelFire_inferno_solid_deck_shields_grate_passes", () =>
            {
                int cases = 0;
                float worstGap = float.MaxValue;
                foreach (bool flying in new[] { false, true })
                foreach (bool held in new[] { false, true })
                foreach (bool deck in new[] { false, true })
                foreach (bool grated in new[] { false, true })
                {
                    cases++;
                    float ch = RM_FuelFireMath.InfernoAttachChance(flying, held, deck, grated);
                    float sz = RM_FuelFireMath.InfernoAttachSize(held, deck, grated);
                    Assert(ch >= 0f && ch <= 1f && sz > 0f && sz <= 1f, "chance and size are in range: " + ch + ", " + sz);
                    if (flying) { Assert(ch == 0f, "a flyer is never lit"); continue; }
                    if (held) { Assert(ch == 1f && sz == 1f, "trapped in the burning hole: certain, full size"); continue; }
                    if (deck && !grated)
                        Assert(ch == RM_FireMath.AttachChance(true, true, false, false), "solid deck: the design's onCover chance");
                    else
                        Assert(ch >= RM_FuelFireMath.InfernoAttachInCell, "open fuel or a grate: the inferno's in-cell chance");
                }
                float solid = RM_FuelFireMath.InfernoAttachChance(false, false, true, false);
                float grate = RM_FuelFireMath.InfernoAttachChance(false, false, true, true);
                worstGap = grate - solid;
                Assert(grate > solid, "a grate passes more fire than a solid deck: " + grate + " vs " + solid);
                Assert(RM_FuelFireMath.InfernoAttachSize(false, true, true) > RM_FuelFireMath.InfernoAttachSize(false, true, false),
                    "a grate's attached fire is bigger than a solid deck's");
                foreach (bool held in new[] { false, true })
                foreach (bool capped in new[] { false, true })
                {
                    cases++;
                    float b = RM_FuelFireMath.InfernoBesideChance(false, held, capped);
                    Assert(b == (capped && !held ? 0f : RM_FuelFireMath.InfernoAttachBeside),
                        "beside: a fire under a solid deck reaches only the hole (held " + held + ", capped " + capped + "): " + b);
                    Assert(RM_FuelFireMath.InfernoBesideChance(true, held, capped) == 0f, "a flyer is never lit beside");
                }
                Console.WriteLine("      inferno deck rule: " + cases + " cases, grate " + grate + " vs solid " + solid + " (gap " + worstGap + ")");
                // the shipped effects read this rule, not their own copy (red on the parent: it inlined 0.9 for every deck)
                string f = RiverSwitchFlipChecks.Src("RM_LiquidFire.cs");
                RiverSwitchFlipChecks.Has(f, @"Rand\.Chance\(RM_FuelFireMath\.InfernoAttachChance\(false, held, onDeck && !held, grated\)\)",
                    "ApplyInfernoEffects reads the deck rule in the cell");
                RiverSwitchFlipChecks.Has(f, @"Rand\.Chance\(RM_FuelFireMath\.InfernoBesideChance\(false, besideHeld, capped\)\)",
                    "ApplyInfernoEffects reads the deck rule beside");
            });

            // RIMMANDRAKE_DECIDE_FLOWWORKS_SOLID_DECK_LOW_CHANCE_SATURATES_IN_ONE_BURN (bridges design §4.1 "low (today's onCover
            // chance: 0.4 / 0.6)"; steward's ruling 2026-11-22): the chance that a rider on an intact SOLID deck catches over ONE
            // burn stays at or below 0.4. Red on the parent: it rolled 0.35 at every effects check, 1-(0.65)^41 = 1.0 over the
            // GRATE scene's 2500 ticks. Range read, through the shipped DeckExposureRolls: burns of 1, 2, 41 (the scene), 1000
            // (a day) and 5000 effects checks; checks 30, 60 (normal), 90 (the check parity shifts across a load) and 120 ticks
            // apart (one missed check); the inferno and the ordinary liquid-fire chance. Also read: a first sighting rolls, a
            // stay broken for longer than the gap is a new exposure (each exposure keeps the same bound), a clock that ran back
            // rolls. Left out: the vanilla halo fires (no deck read), what a fire attached once does to the rider after.
            Case("FuelFire_inferno_solid_deck_low_chance_per_burn", () =>
            {
                const double bound = 0.4;            // design §4.1: today's onCover chance, 0.4
                float pInferno = RM_FuelFireMath.InfernoAttachChance(false, false, true, false);
                float pLiquid = RM_FireMath.AttachChance(false, true, false, false);
                int cases = 0;
                double worst = 0;
                string worstAt = "";
                foreach (float p in new[] { pInferno, pLiquid })
                foreach (int checks in new[] { 1, 2, 41, 1000, 5000 })
                foreach (int gap in new[] { 30, 60, 90, 120 })
                {
                    cases++;
                    double ch = SolidBurnChance(p, checks, gap, out int rolls);
                    if (ch > worst) { worst = ch; worstAt = "p " + p + ", " + checks + " checks " + gap + " ticks apart, " + rolls + " roll(s)"; }
                    Assert(ch <= bound + 1e-9, "a solid-deck rider's chance over one burn of " + checks + " checks " + gap
                        + " ticks apart is " + ch.ToString("0.000") + " (" + rolls + " rolls of " + p + "), above the bound " + bound);
                    Assert(rolls == 1, "one continuous stay is one exposure: " + rolls + " rolls over " + checks + " checks " + gap + " apart");
                }
                Console.WriteLine("      solid deck per burn: " + cases + " cases, worst " + worst.ToString("0.000") + " (limit " + bound + ") at " + worstAt);
                Assert(RM_FireMath.DeckExposureRolls(-1, 0) && RM_FireMath.DeckExposureRolls(-1, 600000), "a first sighting rolls");
                int g = RM_FireMath.DeckExposureGapTicks;
                Assert(!RM_FireMath.DeckExposureRolls(1000, 1000 + g), "seen again within the gap: the same exposure");
                Assert(RM_FireMath.DeckExposureRolls(1000, 1000 + g + 1), "a stay broken past the gap is a new exposure");
                Assert(RM_FireMath.DeckExposureRolls(5000, 4000), "a clock that ran back starts a new exposure");
                Assert(RM_FireMath.DeckExposureExpired(1000, 1000 + g + 1) && !RM_FireMath.DeckExposureExpired(1000, 1000 + g),
                    "a record is forgotten only when forgetting it changes no roll");
                // the grate keeps its chance per check: over the scene's burn its rider is near certain, far above the solid deck
                float pGrate = RM_FuelFireMath.InfernoAttachChance(false, false, true, true);
                double grateBurn = 1 - Math.Pow(1 - pGrate, 41);
                Assert(grateBurn >= 0.99 && grateBurn > worst, "grate per burn " + grateBurn + " vs solid " + worst);
                Console.WriteLine("      grate per burn (41 checks): " + grateBurn.ToString("0.000000") + " vs solid " + worst.ToString("0.000"));
                // the shipped effects gate the solid-deck roll on this rule, in the inferno and in ordinary liquid fire, and save it
                string f = RiverSwitchFlipChecks.Src("RM_LiquidFire.cs");
                RiverSwitchFlipChecks.Has(f, @"if \(SolidDeckRolls\(p, onDeck && !held && !grated\) && Rand\.Chance\(RM_FuelFireMath\.InfernoAttachChance\(false, held, onDeck && !held, grated\)\)\)",
                    "ApplyInfernoEffects gates the solid-deck roll per exposure");
                RiverSwitchFlipChecks.Has(f, @"if \(SolidDeckRolls\(p, onDeck && !held && !grated && !p\.Flying\) && Rand\.Chance\(RM_FireMath\.AttachChance\(held, onDeck && !held, p\.Flying, grated\)\)\)",
                    "ApplyEffects gates the solid-deck roll per exposure");
                RiverSwitchFlipChecks.Has(f, @"RM_FireMath\.DeckExposureRolls\(deckExposedTick\.TryGetValue\(p\.thingIDNumber, out int last\) \? last : -1, now\)",
                    "SolidDeckRolls reads the shipped rule");
                RiverSwitchFlipChecks.Has(f, @"Scribe_Collections\.Look\(ref deckExposedTick, ""deckExposedTick""",
                    "the exposures are saved (a load mid-burn gives no fresh roll)");
            });

            Case("FuelFire_detonation_budgets_hold_on_big_bodies", () =>
            {
                Console.WriteLine("      " + CheckPlan(30, 30, 15, 15, out _));
                Console.WriteLine("      " + CheckPlan(2000, 1, 1000, 0, out _));
                Console.WriteLine("      " + CheckPlan(141, 141, 0, 0, out double ms));
                Assert(ms < 500, "planning 20k cells took " + ms + " ms");
                // can-fail: without the budget a 141x141 square's diagonal ring empties ~141 cells AND blasts dozens at one tick
                Body(141, 141, 70, 70, out int[] ring, out int[] x, out int[] z);
                var anchor = new bool[ring.Length];
                RM_FuelFireMath.ChooseAnchors(x, z, RM_FuelFireMath.BaseBlastSpacing, anchor);
                var naive = new Dictionary<int, int>();
                int worst = 0;
                for (int k = 0; k < ring.Length; k++)
                    if (anchor[k]) { naive[ring[k]] = naive.TryGetValue(ring[k], out int c) ? c + 1 : 1; worst = Math.Max(worst, naive[ring[k]]); }
                Assert(worst > RM_FuelFireMath.MaxBlastsPerTick, "can-fail: the naive schedule already fits (" + worst + ")");
            });
        }
    }
}
