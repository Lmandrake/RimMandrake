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
                // review 2026-10-21: RM_Swim.Tick (the message site for dug cells too) skips everyone with swimming off
                Assert(fe.Contains("if (!Swimming.RM_SwimWater.On)") && fe.Contains("Swimming.RM_Swim.DrownMessage(p);")
                    && sw.Contains("if (!on || p.Flying || wadeableOff"), "a pit drowning is announced with swimming switched off");
                string route = RiverSwitchFlipChecks.Src(Path.Combine("Superdeep", "RM_PitPathing.cs"));
                Assert(route.Contains("customizer = Swimming.RM_SwimPathing.Combine(pawn.Map, pit ? customizer : null, swim);"), "the swim grid rides every path request");
                string eng = RiverSwitchFlipChecks.Src("RM_MapComponent_Excavation.cs");
                Assert(eng.Contains("Swimming.RM_Swim.Tick(map, this);"), "the swim pass ticks");
                string set = RiverSwitchFlipChecks.Src("RimMandrakeFlowWorksMod.cs");
                Assert(set.Contains("Swimming.RM_SwimSettings.ExposeData();") && set.Contains("Swimming.RM_SwimSettings.DoSettingsSection);")
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
                Assert(sw.Contains("if (swimTerrain != null && fp == appliedFingerprint)") && sw.Contains("appliedFingerprint = fp;"),
                    "Reapply compares against what the maps were computed under, not the tables");
                Assert(sw.Contains("&& fp == tableFingerprint)"), "the tables keep their own fingerprint");
            });
            Case("SWIM_REAPPLY_cold_tables_still_recompute", () =>
            {
                string sw = RiverSwitchFlipChecks.Src(Path.Combine("Swimming", "RM_Swim.cs"));
                Assert(!sw.Contains("swimTerrain == null || fp == appliedFingerprint"), "Reapply no longer returns early on null tables");
                Assert(Regex.IsMatch(sw, @"public static void Reapply\(\)[\s\S]*?appliedFingerprint = fp;\s*EnsureTables\(\);[\s\S]*?RecalculateAllPerceivedPathCosts"),
                    "cold tables are built on demand, then every map recomputed");
            });
            // SWIM_DUG_RESERVOIR_FIX_PAWNS_CANT_ENTER (live day 3: a 9x5 dug reservoir, 6 notches, brim-full, "Hole 3 m · Water
            // 3.00 m": order to the middle CanReach false, a pawn in it read deepCell=False pathCost=300; natural 2 m lakes swim).
            // Root cause: the climb rule judged a dug square at its HOLE depth whatever water stood in it, so the reservoir was a
            // sheer 6-notch drop for a person (K = 2): cliff masks closed its lip and RelativeVeto refused the reach; the swim
            // cost and the swim set read natural deep terrain only. Fix: a dug square holding swimmable water >= 2 m is judged at
            // its WATER SURFACE (RM_SwimMath.DugSwimClimbDepth), priced at the swim cost and closed to non-swimmers like a lake.
            Case("SWIM_DUG_reservoir_swimmable_pits_keep_their_rules", () =>
            {
                const int K = 2;   // RM_PocketGrid.PersonBand
                // the live reservoir: 6 notches, 3.00 m, 6 whole notches of water
                int brim = RM_SwimMath.DugSwimClimbDepth(true, true, 6, 3.0, 6);
                Assert(brim == 0, "brim-full 3 m reservoir floats a swimmer at ground level: " + brim);
                Assert(!RM_PitTrapMath.StepAllowed(0, 6, K), "can-fail: pre-fix the lip is a 6-notch cliff for a person (the live CanReach false)");
                Assert(RM_PitTrapMath.StepAllowed(0, RM_SwimMath.ClimbDepthWithSwim(6, brim), K), "post-fix the lip is a level step");
                // a 9x5 reservoir in a 13x9 field: pre-fix every reservoir square is a pocket (no way in), post-fix all surface
                int w = 13, h = 9;
                var pre = new byte[w * h];
                var post = new byte[w * h];
                for (int x = 2; x < 11; x++) for (int z = 2; z < 7; z++)
                {
                    pre[z * w + x] = 6;
                    post[z * w + x] = (byte)RM_SwimMath.ClimbDepthWithSwim(6, brim);
                }
                var lp = RM_PocketGridMath.Label(pre, w, h, K);
                var lq = RM_PocketGridMath.Label(post, w, h, K);
                Assert(lp.IsPocketCell(6, 4) && !lp.SameComponent(0, 4 * w + 6), "can-fail: pre-fix the reservoir middle is a pocket apart from the shore");
                Assert(!lq.IsPocketCell(6, 4) && lq.SameComponent(0, 4 * w + 6), "post-fix the middle joins the shore (CanReach)");
                var d9 = new int[9];
                Assert(RM_CliffMaskMath.AllowedBits(d9, K) == 0xFF, "the cliff mask opens all eight ways over level water");
                // pits keep their rules
                Assert(RM_SwimMath.DugSwimClimbDepth(true, true, 6, 0.0, 0) == -1, "a dry pit is a pit");
                Assert(RM_SwimMath.DugSwimClimbDepth(true, true, 6, 1.5, 3) == -1, "water under 2 m: the pit rules stand");
                Assert(RM_SwimMath.DugSwimClimbDepth(true, true, 6, 1.999, 3) == -1, "1.999 m is under the threshold");
                int sheer = RM_SwimMath.DugSwimClimbDepth(true, true, 7, 2.0, 4);
                Assert(sheer == 3 && !RM_PitTrapMath.StepAllowed(0, sheer, K),
                    "a 3.5 m sheer pit with 2 m of water still has 1.5 m of wall above the surface: the prisoner stays held (live PASS)");
                Assert(RM_SwimMath.DugSwimClimbDepth(true, true, 4, 2.0, 4) == 0, "a brim-full 2 m pit is swum at ground level");
                Assert(RM_SwimMath.DugSwimClimbDepth(true, true, 6, 2.45, 4) == 2, "a part notch never lifts the surface");
                Assert(RM_SwimMath.DugSwimClimbDepth(true, false, 6, 3.0, 6) == -1, "oil, slime, brine...: never swum");
                Assert(RM_SwimMath.DugSwimClimbDepth(false, true, 6, 3.0, 6) == -1, "swimming off: the old pit rules");
                Assert(RM_SwimMath.ClimbDepthWithSwim(6, -1) == 6 && RM_SwimMath.ClimbDepthWithSwim(2, 4) == 2, "never deeper than the hollow");
                // production wiring
                string ex = RiverSwitchFlipChecks.Src("RM_MapComponent_Excavation.cs");
                RiverSwitchFlipChecks.Has(ex, @"int code = RM_SwimMath\.DugSwimCode\(swimmable, hole, dl\);",
                    "the refresh runs the production rule on every dug square");
                RiverSwitchFlipChecks.Has(ex, @"bool swimmable = k == 0 \|\| k > keys \? unrecorded : swimByKey\[k\];",
                    "on the square's own liquid (memoised per fluid key)");
                RiverSwitchFlipChecks.Has(ex, @"swimByKey\[k\] = Swimming\.RM_SwimWater\.FluidSwimmable\(fluidPalette\[k - 1\] \?\? ActiveFluid\);",
                    "the memo is LiquidSwimmableAt's dug rule, key by key");
                RiverSwitchFlipChecks.Has(ex, @"into\[i\] = \(byte\)RM_SwimMath\.ClimbDepthWithSwim\(into\[i\], climb\);", "the pocket grid and the cliff masks read the swim surface");
                RiverSwitchFlipChecks.Has(ex, @"Swimming\.RM_SwimPathing\.BumpCells\(map, batch\);", "a change re-derives the swim grids (naming its squares: r15 fix 2), a batch at a time (DUGSWIM_TAME_RAIN_FLIP_BURST)");
                RiverSwitchFlipChecks.Has(ex, @"swimGenOwed = false;\s*BumpClimbGeneration\(GenSwim\);", "and the masks and the pocket grid once the change is out");
                RiverSwitchFlipChecks.Has(ex, @"map\.pathing\?\.RecalculatePerceivedPathCostAt\(map\.cellIndices\.IndexToCell\(i\)\);", "and re-reads those squares' path costs");
                RiverSwitchFlipChecks.Has(ex, @"% SwimRefreshTicks == 11\) \{ RefreshDugSwim\(\); \}", "refreshed on its own timer");
                RiverSwitchFlipChecks.Has(ex, @"else if \(swimSet\.Unpublished > 0\) \{ PublishDugSwim\(DugSwimFlipsPerTick\);", "the rest of a refresh's flips publish on the following ticks");
                string sw = RiverSwitchFlipChecks.Src(Path.Combine("Swimming", "RM_Swim.cs"));
                Assert(sw.Contains("return ex != null && ex.IsDugSwimCell(c);"), "IsDeepSwimCell counts dug swim squares (deepCell, items, drop pods, non-swimmer reach, swim speed)");
                Assert(sw.Contains("&& !(dugSwim && ex.IsDugSwimCell(map.cellIndices.IndexToCell(i))))"), "the swim offset grids close dug swim squares to non-swimmers");
                Assert(sw.Contains("RM_SuperdeepTrap.EngineOf(m)?.RefreshDugSwim(true);"), "the master switch re-derives them, all at once");
                string sc = RiverSwitchFlipChecks.Src(Path.Combine("Superdeep", "RM_PitStepCost.cs"));
                RiverSwitchFlipChecks.Has(sc, @"if \(eng\.IsDugSwimCell\(c\)\) \{ baseCostOverride = Swimming\.RM_SwimSettings\.swimPathCost; return; \}",
                    "a dug swim square costs the swim cost, not the wet-pit 300");
                Assert(sc.Contains("int to = eng.ClimbDepthAt(c);") && sc.Contains("int from = eng.ClimbDepthAt(prevCell);"), "the walked step reads the climb depth");
            });
            // WATERED_PIT_FIX_NO_WAY_IN (owner review 2026-10-24, row 4): "for water 1.5m in a 1.5m pit, there is 'no way in.' The
            // pawn says not traversible, and I can't place any ramp or ladder within the pit." Root cause: the climb rule lifted a
            // dug square to its water surface only at the 2 m SWIM threshold, so a brim-full 1.5 m pit stayed a sheer 3-notch drop
            // (K = 2); and the wet rungs (WaterShallowBase family) lack Light, so no ladder or ramp passed the terrain gate.
            Case("WATERED_PIT_chest_deep_water_lifts_the_climb_not_the_swim", () =>
            {
                const int K = 2;
                Assert(RM_SwimMath.DugSwimClimbDepth(true, true, 3, 1.5, 3) == -1, "can-fail: pre-fix rule: 1.5 m is not swum, the pit rule stood");
                Assert(!RM_PitTrapMath.StepAllowed(0, 3, K), "can-fail: and a dry 3-notch pit is no way in for a person");
                int lift = RM_SwimMath.DugWadeLiftDepth(true, true, 3, 1.5, 3);
                Assert(lift == 0 && RM_PitTrapMath.StepAllowed(0, RM_SwimMath.ClimbDepthWithSwim(3, lift), K), "the owner's brim-full 1.5 m pit is level: a way in");
                Assert(RM_SwimMath.DugWadeLiftDepth(true, true, 3, 1.499, 2) == -1, "under the ChestDeep rung: the pit rule stands");
                Assert(RM_SwimMath.DugWadeLiftDepth(true, true, 6, 1.5, 3) == 3 && !RM_PitTrapMath.StepAllowed(0, 3, K),
                    "a 3 m sheer pit with 1.5 m of water still has 1.5 m of wall: still held");
                Assert(RM_SwimMath.DugWadeLiftDepth(true, false, 3, 1.5, 3) == -1 && RM_SwimMath.DugWadeLiftDepth(false, true, 3, 1.5, 3) == -1,
                    "never for an unswimmable liquid, nor with swimming off");
                Assert(RM_SwimMath.DugWadeLiftDepth(true, true, 4, 2.0, 4) == RM_SwimMath.DugSwimClimbDepth(true, true, 4, 2.0, 4), "the two agree at 2 m+");
                string ex = RiverSwitchFlipChecks.Src("RM_MapComponent_Excavation.cs");
                Assert(RM_SwimMath.DugSwimCode(true, 3, 3 * RM_LevelSolve.U) == 0, "the refresh lifts chest-deep squares (climb 0, not swum)");
                Assert(RM_SwimMath.DugSwimCode(true, 4, 4 * RM_LevelSolve.U) == 1 && RM_SwimMath.DugSwimCode(true, 7, 4 * RM_LevelSolve.U) == 3 * 2 + 1,
                    "the climb depth and the swim bit travel together; only 2 m+ is SWUM");
                Assert(RM_SwimMath.DugSwimCode(false, 4, 4 * RM_LevelSolve.U) == -1 && RM_SwimMath.DugSwimCode(true, 4, 0) == -1, "unswimmable or dry: the pit rule");
                string sm = RiverSwitchFlipChecks.Src("RM_SwimMath.cs");
                RiverSwitchFlipChecks.Has(sm, @"int lift = s >= 0 \? s : DugWadeLiftDepth\(true, swimmable, hole, metres, whole\); return lift >= 0 \? lift \* 2 \+ \(s >= 0 \? 1 : 0\) : -1;",
                    "the code is the wade lift, else the swim climb, with the swim bit");
                RiverSwitchFlipChecks.Has(ex, @"swimSet\.Put\(i, code\);", "only squares with a code join the set");
                RiverSwitchFlipChecks.Has(ex, @"return swimSet\.SwimCount > 0 && c\.InBounds\(map\) && swimSet\.IsSwim\(", "only 2 m+ squares are the SWIM set (cost, non-swimmer closure)");
                RiverSwitchFlipChecks.Has(ex, @"if \(h == 0 \|\| swimSet\.Count == 0\)", "can-fail: ClimbDepthAt no longer skips the lift when no square is swum");
                RiverSwitchFlipChecks.Has(ex, @"excavatedCells\.Count > 0 \|\| swimSet\.Count > 0\)", "the refresh keeps running while any square is lifted");
                string doors = RiverSwitchFlipChecks.Src(Path.Combine("Superdeep", "RM_FlowDoors.cs"));
                Assert(doors.Contains("RM_FlowDoorRules.IsFlowDoorDef(td) || StandsInWetPit(td)")
                    && doors.Contains("RM_LadderUtility.IsLadderDef(td)") && doors.Contains("typeof(RM_Building_PitRamp).IsAssignableFrom(td.thingClass)"),
                    "every ladder and the pit ramp pass the terrain gate on a wet dug square");
                string lad = RiverSwitchFlipChecks.Src(Path.Combine("Superdeep", "RM_LadderUtility.cs"));
                Assert(lad.Contains("if (engine == null || engine.HollowDepthAt(loc) == 0)"), "the ladder asks 'is this a pit' of the HOLE");
                string ramp = RiverSwitchFlipChecks.Src(Path.Combine("Superdeep", "RM_PitRamp.cs"));
                Assert(ramp.Contains("if (eng == null || eng.HollowDepthAt(loc) == 0)") && ramp.Contains("int d = eng.HollowDepthAt(loc);")
                    && ramp.Contains("int u = up.InBounds(map) ? eng.HollowDepthAt(up) : d;"), "the ramp is judged on the holes, wet or dry");
            });
            // Review day 2 (2026-10-17): drowning in wadeable natural water (a downed person in 0.5 m shallows) is an open owner
            // question; it stays shipped ON, but one setting must turn it off ALONE (deep water and pits keep the rule).
            // DUG_SWIM_REFRESH_SHRINK_HASH_SETS: the flat DugSwimSet against the old Dictionary/HashSet refresh, step by step on
            // random dug scenes (water rising, draining, swapping liquid, squares filled in, the master switch flipping).
            Case("DugSwim_flat_set_equals_dictionary_refresh", () =>
            {
                var rng = new Random(1027);
                int moved = 0, swum = 0, quiet = 0;
                for (int scene = 0; scene < 40; scene++)
                {
                    int n = 64 + rng.Next(400);
                    var hole = new int[n];
                    var dl = new long[n];
                    var swimmable = new bool[n];
                    var set = new RM_SwimMath.DugSwimSet();
                    var oldClimb = new Dictionary<int, int>();
                    var oldSwim = new HashSet<int>();
                    var changed = new List<int>();
                    for (int step = 0; step < 30; step++)
                    {
                        int edits = step == 0 ? n : rng.Next(4) == 0 ? 0 : 1 + rng.Next(n / 4);
                        for (int e = 0; e < edits; e++)
                        {
                            int i = rng.Next(n);
                            hole[i] = rng.Next(3) == 0 ? 0 : 1 + rng.Next(12);
                            dl[i] = rng.Next(3) == 0 ? 0 : rng.Next(hole[i] * RM_LevelSolve.U + 1);
                            swimmable[i] = rng.Next(5) != 0;
                        }
                        bool on = rng.Next(8) != 0;
                        // the old refresh, verbatim in shape
                        var fresh = new Dictionary<int, int>();
                        var oldChanged = new List<int>();
                        for (int i = 0; on && i < n; i++)
                        {
                            long w = hole[i] == 0 ? 0 : dl[i];
                            if (w <= 0)
                            {
                                continue;
                            }
                            double metres = RM_LevelSolve.Metres(w);
                            int sc = RM_SwimMath.DugSwimClimbDepth(true, swimmable[i], hole[i], metres, (int)(w / RM_LevelSolve.U));
                            int lift = sc >= 0 ? sc : RM_SwimMath.DugWadeLiftDepth(true, swimmable[i], hole[i], metres, (int)(w / RM_LevelSolve.U));
                            if (lift >= 0)
                            {
                                fresh[i] = lift * 2 + (sc >= 0 ? 1 : 0);
                            }
                        }
                        foreach (var kv in fresh)
                        {
                            if (!oldClimb.TryGetValue(kv.Key, out int o) || o != kv.Value >> 1 || oldSwim.Contains(kv.Key) != ((kv.Value & 1) == 1))
                            {
                                oldChanged.Add(kv.Key);
                            }
                        }
                        foreach (int i in oldClimb.Keys)
                        {
                            if (!fresh.ContainsKey(i))
                            {
                                oldChanged.Add(i);
                            }
                        }
                        if (oldChanged.Count > 0)
                        {
                            oldClimb.Clear();
                            oldSwim.Clear();
                            foreach (var kv in fresh)
                            {
                                oldClimb[kv.Key] = kv.Value >> 1;
                                if ((kv.Value & 1) == 1)
                                {
                                    oldSwim.Add(kv.Key);
                                }
                            }
                        }
                        // the flat refresh, as production drives it
                        set.Begin(n);
                        for (int i = 0; on && i < n; i++)
                        {
                            if (hole[i] == 0)
                            {
                                continue;
                            }
                            int code = RM_SwimMath.DugSwimCode(swimmable[i], hole[i], dl[i]);
                            if (code >= 0)
                            {
                                set.Put(i, code);
                            }
                        }
                        int got = set.End(changed);
                        Assert(got == oldChanged.Count && changed.Count == got, "scene " + scene + " step " + step + ": " + got + " changed, the old refresh " + oldChanged.Count);
                        var a = new HashSet<int>(changed);
                        Assert(a.Count == changed.Count && a.SetEquals(oldChanged), "the same squares changed, each once");
                        Assert(set.Count == oldClimb.Count && set.SwimCount == oldSwim.Count, "Count and SwimCount match the old sets");
                        for (int i = -1; i <= n; i++)
                        {
                            bool has = set.TryClimb(i, out int climb);
                            Assert(has == oldClimb.ContainsKey(i) && (!has || climb == oldClimb[i]), "square " + i + ": the same climb depth");
                            Assert(set.IsSwim(i) == oldSwim.Contains(i), "square " + i + ": the same swim bit");
                        }
                        Assert(set.Cells.Count == oldClimb.Count, "Cells lists every square with a code");
                        moved += got > 0 ? 1 : 0;
                        quiet += got == 0 ? 1 : 0;
                        swum += set.SwimCount;
                    }
                }
                Assert(moved > 100 && quiet > 50 && swum > 1000, "can-fail: the scenes exercise change, no change and swum squares (moved=" + moved + " quiet=" + quiet + " swum=" + swum + ")");
                // a grid of another size (never in play; kept total): old squares past the end are dropped, not indexed
                var g = new RM_SwimMath.DugSwimSet();
                var ch = new List<int>();
                g.Begin(10);
                g.Put(2, 1);
                g.Put(9, 4);
                Assert(g.End(ch) == 2 && g.SwimCount == 1, "two squares, one swum");
                g.Begin(5);
                g.Put(2, 1);
                Assert(g.End(ch) == 0 && g.Count == 1 && !g.TryClimb(9, out _), "shrunk: square 9 is gone, square 2 kept, nothing moved");
            });
            // DUGSWIM_TAME_RAIN_FLIP_BURST (live r17: a rain refresh flipped thousands of squares in one tick, 44-55 ms): a refresh is
            // staged and published a slice at a time, and a newer refresh may supersede one half published. Random scenes: at every
            // moment each square holds either its old or its new code (never anything else), Count and SwimCount equal a scan of
            // the codes, Cells covers every coded square, and once published the set equals a whole (End) refresh of the same water.
            Case("Swim_dug_staged_publish_converges", () =>
            {
                var rng = new Random(1728);
                int partial = 0, superseded = 0, flips = 0;
                for (int scene = 0; scene < 40; scene++)
                {
                    int n = 64 + rng.Next(600);
                    var hole = new int[n];
                    var dl = new long[n];
                    var swimmable = new bool[n];
                    var staged = new RM_SwimMath.DugSwimSet();
                    var whole = new RM_SwimMath.DugSwimSet();
                    var changed = new List<int>();
                    var scratch = new List<int>();
                    int head = 0;
                    for (int step = 0; step < 40; step++)
                    {
                        int edits = step == 0 ? n : rng.Next(3) == 0 ? 0 : 1 + rng.Next(n / 2);
                        for (int e = 0; e < edits; e++)
                        {
                            int i = rng.Next(n);
                            hole[i] = rng.Next(3) == 0 ? 0 : 1 + rng.Next(12);
                            dl[i] = rng.Next(3) == 0 ? 0 : rng.Next(hole[i] * RM_LevelSolve.U + 1);
                            swimmable[i] = rng.Next(5) != 0;
                        }
                        bool on = rng.Next(8) != 0;
                        var before = new int[n];
                        for (int i = 0; i < n; i++)
                        {
                            before[i] = staged.TryClimb(i, out int c0) ? c0 * 2 + (staged.IsSwim(i) ? 1 : 0) : -1;
                        }
                        if (staged.Unpublished > 0)
                        {
                            superseded++;
                        }
                        staged.Begin(n);
                        whole.Begin(n);
                        var want = new int[n];
                        for (int i = 0; i < n; i++)
                        {
                            want[i] = -1;
                            if (!on || hole[i] == 0)
                            {
                                continue;
                            }
                            int code = RM_SwimMath.DugSwimCode(swimmable[i], hole[i], dl[i]);
                            if (code >= 0)
                            {
                                staged.Put(i, code);
                                whole.Put(i, code);
                                want[i] = code;
                            }
                        }
                        whole.End(scratch);
                        int got = staged.Stage(changed);
                        head = 0;
                        var a = new HashSet<int>(changed);
                        Assert(a.Count == got, "each staged square once");
                        for (int i = 0; i < n; i++)
                        {
                            Assert(a.Contains(i) == (before[i] != want[i]), "staged exactly the squares whose published code differs (" + i + ")");
                        }
                        // publish a random number of slices; sometimes stop half way (the next step supersedes)
                        bool finish = rng.Next(3) != 0;
                        while (head < changed.Count)
                        {
                            int take = 1 + rng.Next(Math.Max(1, got / 3));
                            if (!finish && head + take >= changed.Count)
                            {
                                partial++;
                                break;
                            }
                            for (int k = head; k < Math.Min(changed.Count, head + take); k++)
                            {
                                staged.Publish(changed[k]);
                                flips++;
                            }
                            head = Math.Min(changed.Count, head + take);
                            int cnt = 0, sw = 0;
                            var listed = new HashSet<int>(staged.Cells);
                            for (int i = 0; i < n; i++)
                            {
                                int now = staged.TryClimb(i, out int c1) ? c1 * 2 + (staged.IsSwim(i) ? 1 : 0) : -1;
                                Assert(now == before[i] || now == want[i], "square " + i + " holds its old or its new code, nothing else");
                                cnt += now >= 0 ? 1 : 0;
                                sw += now >= 0 && (now & 1) == 1 ? 1 : 0;
                                Assert(now < 0 || listed.Contains(i), "Cells covers coded square " + i);
                            }
                            Assert(cnt == staged.Count && sw == staged.SwimCount, "Count/SwimCount equal a scan mid-publish");
                        }
                        if (head == changed.Count)
                        {
                            Assert(staged.Unpublished == 0, "all published");
                            Assert(staged.Count == whole.Count && staged.SwimCount == whole.SwimCount && staged.Cells.Count == whole.Cells.Count,
                                "settled: the same set as a whole refresh");
                            for (int i = -1; i <= n; i++)
                            {
                                bool h1 = staged.TryClimb(i, out int x1), h2 = whole.TryClimb(i, out int x2);
                                Assert(h1 == h2 && x1 == x2 && staged.IsSwim(i) == whole.IsSwim(i), "settled square " + i + " equals the whole refresh");
                            }
                            for (int k = 0; k < staged.Cells.Count; k++)
                            {
                                Assert(staged.Cells[k] == whole.Cells[k], "Cells in the same ascending order");
                            }
                        }
                    }
                }
                Assert(partial > 20 && superseded > 20 && flips > 2000, "can-fail: half-published refreshes were superseded (partial=" + partial
                    + " superseded=" + superseded + " flips=" + flips + ")");
            });
            Case("Swim_grid_patch_equals_full_reread", () =>
            {
                // EXCAVATION_COMPONENT_DIAGNOSE_TICK_SPIKES r15 fix 2: RM_SwimPathing re-reads only the squares the dug-swim
                // refresh named, unless an unnamed writer, a refused patch or a big batch owes a full re-read. Random writers
                // over a 60x60 deep map (named, named with extra unmoved squares, unnamed), builds at random moments: every build
                // (patched with For's own rule: copy, flip the moved squares, keep the grid when none moved) equals a full
                // re-read of the map as it is.
                const int n = 3600;
                var rng = new Random(15022);
                var truth = new bool[n];
                for (int i = 0; i < n; i++) truth[i] = rng.NextDouble() < 0.15;
                var plan = new RM_SwimGridPlan();
                Assert(plan.Due && plan.Version == 0, "a new plan is due at version 0 (VersionOf's 0 for a map with no grids)");
                bool[] built = null;
                int deepCount = 0, full = 0, patched = 0, kept = 0, reread = 0, builds = 0;
                for (int step = 0; step < 4000; step++)
                {
                    int r = rng.Next(20);
                    if (r < 12)
                    {
                        var named = new List<int>();
                        int k = rng.Next(1, 12);
                        for (int j = 0; j < k; j++)
                        {
                            int c = rng.Next(n);
                            if (rng.Next(3) > 0) truth[c] = !truth[c];   // a third of the named squares did not move
                            named.Add(c);
                        }
                        plan.BumpCells(named);
                    }
                    else if (r < 13)
                    {
                        truth[rng.Next(n)] ^= true;   // a terrain change: unnamed
                        plan.Bump();
                    }
                    else if (r < 16)
                    {
                        // SWIMGRID_FULL_SHRINK_FILL_FLIP_BUMPS: a fill-terrain swim flip names its one square (BumpCell)
                        int c = rng.Next(n);
                        if (rng.Next(4) > 0) truth[c] = !truth[c];
                        plan.BumpCell(c);
                    }
                    else if (r < 17)
                    {
                        var named = new List<int>();
                        for (int j = 0; j < 400; j++) { int c = rng.Next(n); truth[c] ^= true; named.Add(c); }   // past maxPatch
                        plan.BumpCells(named);
                    }
                    if (rng.Next(3) == 0 && plan.Due)
                    {
                        builds++;
                        List<int> patch = plan.Take(225, built != null && rng.Next(10) > 0);
                        if (patch == null)
                        {
                            full++;
                            built = (bool[])truth.Clone();
                            deepCount = 0;
                            foreach (bool d in built) if (d) deepCount++;
                        }
                        else
                        {
                            patched++;
                            reread += patch.Count;
                            var moved = new List<int>();
                            foreach (int i in patch) if (truth[i] != built[i]) moved.Add(i);
                            if (moved.Count == 0) kept++;
                            else
                            {
                                built = (bool[])built.Clone();
                                foreach (int i in moved) { built[i] = !built[i]; deepCount += built[i] ? 1 : -1; }
                            }
                        }
                        Assert(!plan.Due && plan.PendingCount == 0, "built: nothing pending");
                        int fresh = 0;
                        for (int i = 0; i < n; i++)
                        {
                            if (built[i] != truth[i]) Assert(false, "step " + step + ": square " + i + " differs from a full re-read");
                            if (truth[i]) fresh++;
                        }
                        Assert(deepCount == fresh, "step " + step + ": deep count " + deepCount + " = full re-read's " + fresh);
                    }
                }
                Console.WriteLine("        " + builds + " builds: " + full + " full re-reads, " + patched + " patches (" + kept
                    + " kept the grid), " + reread + " squares patched vs " + ((long)patched * n) + " a full re-read each would read");
                Assert(full > 0 && patched > kept && kept > 0, "every path ran");
                // the stamp's version read is a peek: VersionOf no longer reaches For, and the refresh names its squares
                string sw = RiverSwitchFlipChecks.Src(Path.Combine("Swimming", "RM_Swim.cs"));
                RiverSwitchFlipChecks.Has(sw, @"public static int VersionOf\(Map map\)\s*\{\s*if \(map == null\)\s*\{\s*return -1;\s*\}\s*return grids\.TryGetValue\(map, out MapGrids g\) \? g\.plan\.Version : 0;",
                    "VersionOf peeks the counter (no rebuild)");
                RiverSwitchFlipChecks.Has(sw, @"List<int> patch = g\.plan\.Take\(", "For asks the plan whether to patch");
                string ex = RiverSwitchFlipChecks.Src("RM_MapComponent_Excavation.cs");
                RiverSwitchFlipChecks.Has(ex, @"swimSet\.Publish\(i\);\s*batch\.Add\(i\);.{0,400}Swimming\.RM_SwimPathing\.BumpCells\(map, batch\);",
                    "the dug-swim refresh names the squares it changed (each published batch)");
                // SWIMGRID_FULL_SHRINK_FILL_FLIP_BUMPS: the terrain-change postfix names its square, and the bump counters show
                RiverSwitchFlipChecks.Has(sw, @"public static void Postfix\(IntVec3 c, TerrainDef oldTerr, TerrainDef newTerr, Map ___map\)\s*\{\s*if \(RM_SwimWater\.IsSwimTerrain\(oldTerr\) != RM_SwimWater\.IsSwimTerrain\(newTerr\)\)\s*\{.{0,400}?RM_SwimPathing\.BumpCell\(___map, ___map\.cellIndices\.CellToIndex\(c\)\);",
                    "a swim flip by a terrain write names its square");
                RiverSwitchFlipChecks.Has(sw, @""" named="" \+ NamedBumps \+ "" unnamed="" \+ UnnamedBumps", "SWIMGRID counts named and unnamed bumps");
            });

            Case("Swim_grid_fill_flips_patch_not_full", () =>
            {
                // SWIMGRID_FULL_SHRINK_FILL_FLIP_BUMPS (r16 live, sinks on: +21..+47 full re-reads per 4000 ticks from fill-terrain
                // flips' unnamed bumps against +2..+11 patches). The r16 window's shape: a dug-swim refresh every 300 ticks plus
                // fill flips of band-edge squares between builds. Old (unnamed Bump per flip): every build after a flip re-reads the
                // map. New (BumpCell): only the first build re-reads it; every patched grid equals a full re-read.
                foreach (bool named in new[] { false, true })
                {
                    const int n = 105625;
                    var rng = new Random(16016);
                    var truth = new bool[n];
                    var built = new bool[n];
                    var plan = new RM_SwimGridPlan();
                    int full = 0, patches = 0;
                    for (int tick = 0; tick < 4000; tick += 50)
                    {
                        if (tick % 300 == 0)
                        {
                            var cs = new List<int>();
                            for (int j = 0; j < 20; j++) { int c = rng.Next(n); truth[c] ^= true; cs.Add(c); }
                            plan.BumpCells(cs);
                        }
                        int flips = rng.Next(3);
                        for (int j = 0; j < flips; j++)
                        {
                            int c = rng.Next(n);
                            truth[c] ^= true;
                            if (named) plan.BumpCell(c); else plan.Bump();
                        }
                        if (!plan.Due) continue;
                        List<int> patch = plan.Take(n / 16, tick > 0);
                        if (patch == null) { full++; Array.Copy(truth, built, n); }
                        else { patches++; foreach (int i in patch) built[i] = truth[i]; }
                        for (int i = 0; i < n; i++)
                            if (built[i] != truth[i]) { Assert(false, "tick " + tick + ": square " + i + " differs from a full re-read"); break; }
                    }
                    Console.WriteLine("        fill flips " + (named ? "named" : "unnamed") + ": " + full + " full re-reads, " + patches + " patches");
                    if (named) Assert(full == 1 && patches > 30, "named flips: one full re-read (the first build), " + full + " seen");
                    else Assert(full > 30, "the instrument can see: unnamed flips force full re-reads (" + full + ")");
                }
            });

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
