// DEEP_WATER_BUILD_SWIM_OR_SINK (plan P12 of FLOWWORKS_DEPTH_REBUILD_ONE_BIG_DIG). Owner R12 (2026-10-17, by card): "pawns may
// swim in water 2 m or deeper"; non-water fluids keep the no-swim refusal; deep water stops being a barrier for pits and
// trenches. Arithmetic is the PRODUCTION Verse-free code (RM_SwimMath + RM_RelativeRulesMath's one drowning rule); the
// Verse-bound wiring (Swimming/RM_Swim.cs and its call sites) is read from production source.
// Scenes: a person, a non-swimmer, a bear, a fish, a thrumbo in 2 m, 8 m and lake water; the exhaustion timeline to the
// warning and to drowning; armour and carried weight; a towed rescue; a pawn dropped mid-lake; a lake crossing planned on a
// grid by each kind; oil, slime, tar, propane, boiling water and brine refused.
using System;
using System.Collections.Generic;
using System.IO;
using System.Text.RegularExpressions;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class SwimChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private const float Person = 1.75f;   // RM_RelativeRulesMath.HeightByBand[2]
        private const float Thrumbo = 3.5f;
        private const float Head = RM_RelativeRulesMath.DefaultHeadFraction;
        private const int Check = RM_RelativeRulesMath.DrowningCheckTicks;

        private static RM_SwimMath.SwimClass Human() => RM_SwimMath.Classify(false, null, false, false, true, true);
        private static RM_SwimMath.SwimClass Mech() => RM_SwimMath.Classify(true, null, false, false, false, true);

        /// <summary>Severity per check under the one drowning rule (no exit in reach: mid-lake).</summary>
        private static float Drown(RM_SwimMath.SwimClass cls, float water, float h, bool lying, float exhaustion, bool liquidOk)
        {
            bool under = RM_RelativeRulesMath.HeadUnder(water, h, lying);
            bool up = !lying || cls == RM_SwimMath.SwimClass.Aquatic ? RM_SwimMath.KeepsHeadUp(cls, exhaustion, liquidOk) : false;
            return RM_RelativeRulesMath.DrowningPerCheck(under, lying, up, false, false, 1f);
        }

        /// <summary>Dijkstra over a cost grid (4-way): total cost, or -1 when no route; also how many deep squares it used.</summary>
        private static int Plan(bool[,] deep, int sx, int sz, int tx, int tz, Func<bool, int> cellCost, out int deepUsed)
        {
            int w = deep.GetLength(0), h = deep.GetLength(1);
            var dist = new int[w, h];
            var used = new int[w, h];
            for (int x = 0; x < w; x++) for (int z = 0; z < h; z++) dist[x, z] = int.MaxValue;
            var open = new SortedSet<(int d, int x, int z)>();
            dist[sx, sz] = 0;
            open.Add((0, sx, sz));
            int[] dx = { 1, -1, 0, 0 }, dz = { 0, 0, 1, -1 };
            while (open.Count > 0)
            {
                var cur = open.Min;
                open.Remove(cur);
                if (cur.x == tx && cur.z == tz)
                {
                    deepUsed = used[tx, tz];
                    return cur.d;
                }
                for (int i = 0; i < 4; i++)
                {
                    int nx = cur.x + dx[i], nz = cur.z + dz[i];
                    if (nx < 0 || nz < 0 || nx >= w || nz >= h) continue;
                    int c = cellCost(deep[nx, nz]);
                    if (c >= RM_SwimMath.Blocked) continue;
                    int nd = cur.d + 13 + c;
                    if (nd < dist[nx, nz])
                    {
                        open.Remove((dist[nx, nz], nx, nz));
                        dist[nx, nz] = nd;
                        used[nx, nz] = used[cur.x, cur.z] + (deep[nx, nz] ? 1 : 0);
                        open.Add((nd, nx, nz));
                    }
                }
            }
            deepUsed = 0;
            return -1;
        }

        /// <summary>A 40 x 21 map: a lake band 7 squares deep across the middle (z 7..13), with a land bridge at x 38..39 when
        /// <paramref name="bridge"/> (a 70-square detour for a straight 20-square crossing).</summary>
        private static bool[,] Lake(bool bridge)
        {
            var g = new bool[40, 21];
            for (int x = 0; x < 40; x++)
                for (int z = 7; z <= 13; z++)
                    g[x, z] = !(bridge && x >= 38);
            return g;
        }

        /// <summary>RM_SwimSettings.DoSettingsSection's body (the drawn screen), whitespace-collapsed source.</summary>
        private static string Screen(string sw)
        {
            int a = sw.IndexOf("public static void DoSettingsSection(", StringComparison.Ordinal);
            int b = a < 0 ? -1 : sw.IndexOf("public static class RM_SwimWater", a, StringComparison.Ordinal);
            Assert(a >= 0 && b > a, "found RM_SwimSettings.DoSettingsSection");
            return sw.Substring(a, b - a);
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("Swim_who_swims_by_race_gene_and_load", () =>
            {
                Assert(Human() == RM_SwimMath.SwimClass.Swimmer, "a person swims (and tires)");
                Assert(Mech() == RM_SwimMath.SwimClass.None, "a mechanoid sinks");
                Assert(RM_SwimMath.Classify(false, 10, false, false, false, true) == RM_SwimMath.SwimClass.Strong, "a bear (waterCellCost 10): strong");
                Assert(RM_SwimMath.Classify(false, 1, false, false, false, true) == RM_SwimMath.SwimClass.Aquatic, "waterCellCost 1: aquatic");
                Assert(RM_SwimMath.Classify(false, 1, false, false, true, true) == RM_SwimMath.SwimClass.Aquatic, "an aquatic gene (cost 1) on a person");
                Assert(RM_SwimMath.Classify(false, null, true, false, false, true) == RM_SwimMath.SwimClass.Aquatic, "a swimming graphic: aquatic");
                Assert(RM_SwimMath.Classify(false, null, false, true, false, true) == RM_SwimMath.SwimClass.Strong, "a water-seeker: strong");
                Assert(RM_SwimMath.Classify(false, null, false, false, true, false) == RM_SwimMath.SwimClass.None, "people-swim off: a person sinks");
                Assert(RM_SwimMath.Classify(false, null, false, false, false, false) == RM_SwimMath.SwimClass.Swimmer, "people-swim off: a dog still swims");
                float ef = RM_SwimMath.EnduranceFactor(RM_SwimMath.SwimClass.Swimmer, 1f, 1f, 0.75f, RM_SwimMath.DefaultWeightEndurancePenalty);
                Assert(RM_SwimMath.Effective(RM_SwimMath.SwimClass.Swimmer, ef) == RM_SwimMath.SwimClass.None, "75% load sinks (" + ef + ")");
                ef = RM_SwimMath.EnduranceFactor(RM_SwimMath.SwimClass.Swimmer, 1f, 1f, 0.7f, RM_SwimMath.DefaultWeightEndurancePenalty);
                Assert(RM_SwimMath.Effective(RM_SwimMath.SwimClass.Swimmer, ef) == RM_SwimMath.SwimClass.Swimmer, "70% load still swims (" + ef + ")");
            });

            Case("Swim_swimmer_vs_nonswimmer_in_2m_8m_and_lake_water", () =>
            {
                var S = RM_SwimMath.SwimClass.Swimmer;
                var N = RM_SwimMath.SwimClass.None;
                foreach (float w in new[] { 2f, 8f })   // dug 2 m and 8 m of water, and the natural deep band (2 m: RM_SwimWater's fallback)
                {
                    Assert(RM_SwimMath.IsSwimming(w, Person, false, Head), w + " m: a person swims (head under standing)");
                    Assert(Drown(S, w, Person, false, 0f, true) == 0f, w + " m: a fresh swimmer keeps its head up");
                    Assert(Drown(N, w, Person, false, 0f, true) > 0f, w + " m: a non-swimmer drowns");
                    Assert(Drown(S, w, Person, false, 1f, true) > 0f, w + " m: an exhausted swimmer drowns");
                    Assert(Drown(S, w, Person, true, 0f, true) > 0f, w + " m: lying (downed) drowns");
                    Assert(Drown(RM_SwimMath.SwimClass.Aquatic, w, Person, true, 1f, true) == 0f, w + " m: the aquatic never drown");
                }
                Assert(!RM_SwimMath.IsSwimming(1.5f, Person, false, Head) && Drown(N, 1.5f, Person, false, 0f, true) == 0f,
                    "1.5 m: a person wades, nobody drowns standing");
                Assert(!RM_SwimMath.IsSwimming(2f, Thrumbo, false, Head), "a thrumbo wades the 2 m lake band");
                Assert(RM_SwimMath.IsSwimming(8f, Thrumbo, false, Head), "a thrumbo swims 8 m");
                Assert(Drown(S, 8f, Person, false, 0f, false) > 0f, "nobody keeps its head up in a liquid that refuses swimming");
                Assert(RM_SwimMath.DefaultSwimPathCost > 42, "swimming is slower than wading chest-deep (42)");
            });

            Case("Swim_exhaustion_timeline_warns_before_drowning", () =>
            {
                // An unloaded person mid-lake, no footing in reach: checks every 250 ticks.
                float ef = RM_SwimMath.EnduranceFactor(RM_SwimMath.SwimClass.Swimmer, 1f, 1f, 0f, RM_SwimMath.DefaultWeightEndurancePenalty);
                float per = RM_SwimMath.ExhaustionPerCheck(ef, RM_SwimMath.DefaultEnduranceHours, Check);
                float exh = 0f, drown = 0f;
                int warnAt = -1, under = -1, dead = -1;
                const float RecoveryPerCheck = 4f * Check / 60000f;   // RM_PitDrowning's -4/day comp
                for (int i = 1; i <= 200 && dead < 0; i++)
                {
                    exh = Math.Min(1f, exh + per);
                    if (warnAt < 0 && exh >= RM_SwimMath.DefaultWarnAt) warnAt = i;
                    float d = Drown(RM_SwimMath.SwimClass.Swimmer, 3f, Person, false, exh, true);
                    if (d > 0f && under < 0) under = i;
                    drown = Math.Max(0f, drown + d - RecoveryPerCheck);
                    if (drown >= 1f) dead = i;
                }
                float h(int checks) => checks * Check / 2500f;
                Console.WriteLine("    timeline: warned at " + h(warnAt).ToString("0.00") + " h, under at " + h(under).ToString("0.00")
                    + " h, dead at " + h(dead).ToString("0.00") + " h");
                Assert(Math.Abs(h(under) - RM_SwimMath.DefaultEnduranceHours) < 0.11f, "goes under at the endurance (2 h)");
                Assert(warnAt > 0 && h(under) - h(warnAt) >= 0.5f, "warned at least half an hour before going under");
                Assert(dead > under && h(dead) - h(under) > 0.9f && h(dead) - h(under) < 1.5f, "then drowns in about an hour (the one rule's rate)");
                // Recovery on footing: full in an hour.
                Assert(Math.Abs(RM_SwimMath.RecoveryPerCheck(RM_SwimMath.DefaultRecoveryHours, Check) * 10f - 1f) < 1e-4f, "10 checks (1 h) to recover");
                Assert(RM_SwimMath.ExhaustionPerCheck(float.PositiveInfinity, 2f, Check) == 0f, "the aquatic never tire");
                Assert(RM_SwimMath.ExhaustionPerCheck(0f, 2f, Check) >= 1f, "a sinker is exhausted at once");
            });

            Case("Swim_armour_and_carried_weight_table", () =>
            {
                // load = mass / capacity (a person carries 35 kg): naked, a rifle and flak (~9 kg), marine armour + rifle (~16 kg),
                // cataphract + gear (~23 kg), past the sink line (~26 kg).
                float pen = RM_SwimMath.DefaultWeightEndurancePenalty, slow = RM_SwimMath.DefaultWeightSlowdown;
                float lastH = float.MaxValue, lastC = 0f;
                Console.WriteLine("    load   endurance h   cost x   swim ticks/square (13 + 60 x cost)");
                foreach (float kg in new[] { 0f, 9f, 16f, 23f, 26f })
                {
                    float load = RM_SwimMath.Load(kg, 0f, false, 35f);
                    float ef = RM_SwimMath.EnduranceFactor(RM_SwimMath.SwimClass.Swimmer, 1f, 1f, load, pen);
                    var cls = RM_SwimMath.Effective(RM_SwimMath.SwimClass.Swimmer, ef);
                    float hrs = cls == RM_SwimMath.SwimClass.None ? 0f : RM_SwimMath.EnduranceHours(ef, RM_SwimMath.DefaultEnduranceHours);
                    float cf = RM_SwimMath.CostFactor(cls, 1f, load, slow);
                    Console.WriteLine("    " + load.ToString("0.00") + "   " + hrs.ToString("0.00") + "          " + cf.ToString("0.00")
                        + "     " + (13 + 60 * cf).ToString("0") + (cls == RM_SwimMath.SwimClass.None ? "  SINKS" : ""));
                    Assert(hrs <= lastH && cf >= lastC, "more weight never swims longer or faster");
                    lastH = hrs;
                    lastC = cf;
                }
                Assert(lastH == 0f, "26 kg on a person (74%) sinks");
                float marine = RM_SwimMath.EnduranceHours(RM_SwimMath.EnduranceFactor(RM_SwimMath.SwimClass.Swimmer, 1f, 1f, 16f / 35f, pen), 2f);
                Assert(marine > 0.5f && marine < 1.2f, "heavy armour: under an hour and a bit (" + marine + ")");
                // A towed person counts 0.5, never the person's mass: a rescuer can bring someone out.
                float tow = RM_SwimMath.Load(2f, 60f, true, 35f);
                Assert(Math.Abs(tow - (2f / 35f + RM_SwimMath.TowedPawnLoad)) < 1e-5f, "towing counts 0.5 load");
                var towCls = RM_SwimMath.Effective(RM_SwimMath.SwimClass.Swimmer, RM_SwimMath.EnduranceFactor(RM_SwimMath.SwimClass.Swimmer, 1f, 1f, tow, pen));
                Assert(towCls == RM_SwimMath.SwimClass.Swimmer, "a rescuer towing someone still swims");
                Assert(RM_SwimMath.CostFactor(RM_SwimMath.SwimClass.Swimmer, 0.5f, 0f, slow) == 2f, "half Moving swims at half speed");
                Assert(RM_SwimMath.CostFactor(RM_SwimMath.SwimClass.Strong, 0.5f, 1f, slow) == 1f, "strong swimmers keep their own water cost");
                Assert(RM_SwimMath.SizeFactor(0.2f) == 0.5f && RM_SwimMath.SizeFactor(1f) == 1f && RM_SwimMath.SizeFactor(4f) == 2f, "size factor");
            });

            Case("Swim_pathing_swimmers_cross_nonswimmers_never", () =>
            {
                int swim = RM_SwimMath.DefaultSwimPathCost;
                Func<bool, int> person = d => RM_SwimMath.PlanCellCost(d, 0, swim, RM_SwimMath.PlanOffset(RM_SwimMath.SwimClass.Swimmer, false, true, RM_SwimMath.DefaultAnimalAvoidCost));
                Func<bool, int> mech = d => RM_SwimMath.PlanCellCost(d, 0, swim, RM_SwimMath.PlanOffset(RM_SwimMath.SwimClass.None, false, true, RM_SwimMath.DefaultAnimalAvoidCost));
                Func<bool, int> dog = d => RM_SwimMath.PlanCellCost(d, 0, swim, RM_SwimMath.PlanOffset(RM_SwimMath.SwimClass.Swimmer, true, true, RM_SwimMath.DefaultAnimalAvoidCost));
                Func<bool, int> bear = d => RM_SwimMath.PlanCellCost(d, 0, swim, RM_SwimMath.PlanOffset(RM_SwimMath.SwimClass.Strong, true, true, RM_SwimMath.DefaultAnimalAvoidCost));
                var withBridge = Lake(true);
                var noBridge = Lake(false);
                Assert(Plan(withBridge, 5, 2, 5, 18, person, out int pd) > 0 && pd == 7, "a person swims straight across (7 deep squares; " + pd + ")");
                Assert(Plan(withBridge, 5, 2, 5, 18, mech, out int md) > 0 && md == 0, "a non-swimmer walks round by the bridge");
                Assert(Plan(noBridge, 5, 2, 5, 18, mech, out _) < 0, "a non-swimmer with no land route has no route");
                Assert(Plan(withBridge, 5, 2, 5, 18, dog, out int dd) > 0 && dd == 0, "a land animal walks round when it can");
                Assert(Plan(noBridge, 5, 2, 5, 18, dog, out int dn) > 0 && dn == 7, "and swims when there is no other way");
                Assert(Plan(withBridge, 5, 2, 5, 18, bear, out int bd) > 0 && bd == 7, "a bear swims straight across");
                Assert(RM_SwimMath.PlanOffset(RM_SwimMath.SwimClass.Swimmer, true, false, 3000) == 0, "animals-avoid off: a dog swims like a person");
                Assert(RM_SwimMath.PlanOffset(RM_SwimMath.SwimClass.Swimmer, true, true, 20000) == RM_SwimMath.Blocked - 1, "an avoid cost never becomes a wall");
            });

            Case("Swim_pawn_dropped_in_deep_water", () =>
            {
                // Mid-lake, 3 m of water, no footing in reach (ExitInReach reads natural water too: wired below).
                Assert(Drown(RM_SwimMath.SwimClass.None, 3f, Person, false, 0f, true) > 0f, "a dropped non-swimmer drowns");
                Assert(Drown(RM_SwimMath.SwimClass.Swimmer, 3f, Person, false, 0f, true) == 0f, "a dropped swimmer treads water");
                Assert(Drown(RM_SwimMath.SwimClass.Swimmer, 3f, Person, true, 0f, true) > 0f, "a dropped downed swimmer drowns");
                // Beside footing: the exit rule (one step to water under the head) saves a standing non-swimmer.
                Assert(RM_RelativeRulesMath.ExitInReach(0, 0, 2, false, 0.5f, Person) && !RM_RelativeRulesMath.ExitInReach(0, 0, 2, false, 3f, Person),
                    "a lake edge is footing; another deep square is not");
                Assert(RM_RelativeRulesMath.DrowningPerCheck(true, false, false, false, true, 1f) == 0f, "a non-swimmer beside the shore climbs out");
            });

            Case("Swim_nonwater_fluids_refuse", () =>
            {
                string sw = RiverSwitchFlipChecks.Src(Path.Combine("Swimming", "RM_Swim.cs"));
                Assert(sw.Contains("SwimLiquids = new HashSet<string> { \"RM_Liquid_FreshWater\", \"RM_Liquid_SaltWater\", \"RM_Liquid_IcyWater\" }"),
                    "natural seas: only fresh, salt and icy water swim");
                Assert(sw.Contains("SwimFluids = new HashSet<string> { \"RM_Fluid_Water\", \"RM_Fluid_IcyWater\" }"), "pits: only water and icy water swim");
                string fluids = RiverSwitchFlipChecks.Src(Path.Combine("..", "Defs", "Canals", "FluidDefs", "FlowWorks_Fluids.xml"))
                    + RiverSwitchFlipChecks.Src(Path.Combine("..", "Defs", "Canals", "FluidDefs", "FlowWorks_PitFluids.xml"));
                var names = new List<string>();
                foreach (Match m in Regex.Matches(fluids, @"<defName>(RM_Fluid_\w+)</defName>")) names.Add(m.Groups[1].Value);
                Assert(names.Contains("RM_Fluid_Water") && names.Contains("RM_Fluid_IcyWater") && names.Count >= 10, "fluid census (" + names.Count + ")");
                foreach (string n in names)
                {
                    bool swims = n == "RM_Fluid_Water" || n == "RM_Fluid_IcyWater";
                    Assert(swims == sw.Contains("\"" + n + "\""), "fluid " + n + (swims ? " swims" : " refuses"));
                }
                string reg = RiverSwitchFlipChecks.Src(Path.Combine("..", "Defs", "LiquidTypes", "LiquidDefs", "RM_LiquidDefRegistry.xml"));
                foreach (string l in new[] { "RM_Liquid_FreshWater", "RM_Liquid_SaltWater", "RM_Liquid_IcyWater" })
                    Assert(reg.Contains("<defName>" + l + "</defName>"), "liquid exists: " + l);
                foreach (string l in new[] { "RM_Liquid_Brine", "RM_Liquid_Propane", "RM_Liquid_BoilingWater", "RM_Liquid_Tar", "RM_Liquid_ToxicWater" })
                    Assert(reg.Contains("<defName>" + l + "</defName>") && !sw.Contains("\"" + l + "\""), "refused liquid: " + l);
                Assert(sw.Contains("if (t == null || !t.IsWater || t.HasModExtension<RM_NoRecreationalSwimExtension>() || t.toxicBuildupFactor > 0f)"),
                    "the old no-swim marker and toxic water still refuse");
                Assert(sw.Contains("swim[t.index] = RM_SwimSettings.deepSwimEnabled && liq[t.index] && t.IsWater && t.passability == Traversability.Impassable"),
                    "a deep sea of a refused liquid stays impassable");
                string joy = RiverSwitchFlipChecks.Src(Path.Combine("ManyWaters", "RM_Patch_NoRecreationalSandSwim.cs"));
                Assert(joy.Contains("Swimming.RM_SwimWater.LiquidRefusesAt(map, cell)") && joy.Contains("return !Swimming.RM_Swim.JoySwimAllowed(pawn);"),
                    "swim joy: refused liquids and deep water only for rested swimmers");
                Assert(RM_SwimMath.KeepsHeadUp(RM_SwimMath.SwimClass.Aquatic, 0f, false) == false, "not even the aquatic swim in oil");
            });

            Case("Swim_wired_at_call_sites", () =>
            {
                string sw = RiverSwitchFlipChecks.Src(Path.Combine("Swimming", "RM_Swim.cs"));
                Assert(sw.Contains("RM_Drowning.keepsHeadUp = RM_Swim.KeepsHeadUp;"), "the P12 hook is set");
                Assert(sw.Contains("[HarmonyPatch(typeof(PathGrid), nameof(PathGrid.CalculatedCostAt))]")
                    && sw.Contains("int cost = baseCostOverride ?? RM_SwimSettings.swimPathCost;"), "the deep band opens in the path grid");
                Assert(sw.Contains("if (d.passability == Traversability.Impassable) { return; }"), "an impassable thing still closes a swim square");
                Assert(sw.Contains("[HarmonyPatch(typeof(Pawn_PathFollower), \"CostToMoveIntoCell\", new[] { typeof(Pawn), typeof(IntVec3) })]"), "swim speed");
                Assert(sw.Contains("if (p.Downed && pr.cls != RM_SwimMath.SwimClass.Aquatic) { return false; }"), "the downed go under");
                Assert(sw.Contains("if (!dug) { HealthUtility.AdjustSeverity(p, drowning, d); }"), "natural water drowns by the one rule; pits by theirs");
                Assert(sw.Contains("float d = RM_Drowning.PerCheck(map, ex, p, c, w);"), "one PerCheck for lakes and pits");
                Assert(sw.Contains("[HarmonyPatch(typeof(GenSpawn), nameof(GenSpawn.CanSpawnAt))]") && sw.Contains("[HarmonyPatch(typeof(DropCellFinder), nameof(DropCellFinder.IsGoodDropSpot))]"),
                    "items and drop pods never land in deep water");
                Assert(sw.Contains("if (RM_Swim.ProfileOf(p).cls == RM_SwimMath.SwimClass.None) { __result = false; }"), "a non-swimmer cannot reach a lake square");
                Assert(sw.Contains("p.jobs.StartJob(job, JobCondition.InterruptForced, null, resumeCurJobAfterwards: false);") && sw.Contains("p.Drafted"),
                    "tired undrafted swimmers head for footing; drafted obey");
                string fe = RiverSwitchFlipChecks.Src("RM_PitFillEffects.cs");
                Assert(fe.Contains("float w = Swimming.RM_SwimWater.WaterMetresAt(map, eng, n);"), "footing reads natural water too");
                string route = RiverSwitchFlipChecks.Src(Path.Combine("Superdeep", "RM_PitPathing.cs"));
                Assert(route.Contains("customizer = Swimming.RM_SwimPathing.Combine(pawn.Map, pit ? customizer : null, swim);"), "the swim grid rides every path request");
                string eng = RiverSwitchFlipChecks.Src("RM_MapComponent_Excavation.cs");
                Assert(eng.Contains("Swimming.RM_Swim.Tick(map, this);"), "the swim pass ticks");
                string set = RiverSwitchFlipChecks.Src("RimMandrakeFlowWorksMod.cs");
                Assert(set.Contains("Swimming.RM_SwimSettings.ExposeData();") && set.Contains("Swimming.RM_SwimSettings.DoSettingsSection(list);")
                    && set.Contains("Swimming.RM_SwimWater.Reapply();"), "settings scribed, drawn, re-applied on save");
                // review day 3: "on the screen" reads the settings section only (the Scribe line's "ref n," matched it before,
                // so the check could not fail once "scribed" passed)
                string screen = Screen(sw);
                foreach (Match m in Regex.Matches(sw, @"public static (?:bool|int|float) (\w+) = "))
                {
                    string n = m.Groups[1].Value;
                    Assert(sw.Contains("Scribe_Values.Look(ref " + n + ", \"" + n + "\""), "scribed: " + n);
                    Assert(Regex.IsMatch(screen, @"ref " + n + @"[,)]") || Regex.IsMatch(screen, n + @" = Mathf\.Round"), "on the screen: " + n);
                }
                Assert(sw.Contains("public static bool deepSwimEnabled = true;") && sw.Contains("public static bool swimOpenWaterEnabled = false;"),
                    "master on (R12); the open sea off");
                string hed = RiverSwitchFlipChecks.Src(Path.Combine("..", "Defs", "Pits", "HediffDefs", "Pit_Hediffs.xml"));
                Assert(hed.Contains("<defName>RM_SwimExhaustion</defName>"), "the exhaustion hediff exists");
                string defof = RiverSwitchFlipChecks.Src("RimMandrakeFlowWorks_DefOf.cs");
                Assert(defof.Contains("public static HediffDef RM_SwimExhaustion;"), "and is bound");
            });

            // Review 2026-10-17: the fingerprint was a string built on EVERY IsSwimTerrain call (Reachability.CanReach, the path
            // grid: an allocation per call), and it left out swimPathCost, so moving the swim-cost slider never re-read any map's
            // path grid (the cost is baked into PathGrid by CalculatedCostAt) until a reload. Reapply also shared the tables'
            // fingerprint, so any IsSwimTerrain call between the change and Reapply hid the change from it.
            Case("Swim_reapply_fingerprint_no_alloc_and_cost", () =>
            {
                string sw = RiverSwitchFlipChecks.Src(Path.Combine("Swimming", "RM_Swim.cs"));
                Assert(sw.Contains("private static int Fingerprint()") && !sw.Contains("private static string Fingerprint()"), "the fingerprint is an int");
                Assert(Regex.IsMatch(sw, @"private static int Fingerprint\(\)\s*\{[^}]*RM_SwimSettings\.swimPathCost"), "the swim cost is in it");
                Assert(sw.Contains("if (swimTerrain == null || fp == appliedFingerprint)") && sw.Contains("appliedFingerprint = fp;"),
                    "Reapply compares against what the maps were computed under, not the tables");
                Assert(sw.Contains("&& fp == tableFingerprint)"), "the tables keep their own fingerprint");
            });
            // Review day 2 (2026-10-17): drowning in wadeable natural water (a downed person in 0.5 m shallows) is an open owner
            // question; it stays shipped ON, but one setting must turn it off ALONE (deep water and pits keep the rule).
            Case("Swim_shallow_drowning_switch_alone", () =>
            {
                string sw = RiverSwitchFlipChecks.Src(Path.Combine("Swimming", "RM_Swim.cs"));
                Assert(sw.Contains("public static bool shallowWaterDrowningEnabled = true;"), "shipped on (behaviour unchanged)");
                Assert(sw.Contains("Scribe_Values.Look(ref shallowWaterDrowningEnabled, \"shallowWaterDrowningEnabled\", true);"), "scribed, same default");
                Assert(Screen(sw).Contains("ref shallowWaterDrowningEnabled,"), "shown in Mod Settings");
                Assert(Regex.IsMatch(sw, @"bool wadeableOff = !dug && !RM_SwimSettings\.shallowWaterDrowningEnabled && t != null && t\.IsWater\s*&& t\.passability != Traversability\.Impassable;"),
                    "can-fail: off = natural, vanilla-passable water only (never a dug cell, never deep water)");
                Assert(Regex.IsMatch(sw, @"if \(!on \|\| p\.Flying \|\| wadeableOff \|\|"), "off: that square is footing (recover, no drowning check)");
            });
        }
    }
}
