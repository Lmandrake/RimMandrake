// WALL_SCALING_BUILD_ROPE_OVER_RAMPARTS (owner 2026-10-18: climbing gear "should allow pawns to scale walls (unroofed on both
// sides) just as easily as canal sides, albeit slowly"; by card: built walls too, colonists AND raiders, both ways, slowly).
// Offline: the pure verdicts (RM_WallClimbMath: which walls, who may, the roof rule on both sides and the wall, the slow cost),
// and the production wiring (the seams, the settings, the defs). Each case has a can-fail.
// NOT proven here: a colonist ordered over a wall in game, a sapper/breacher/raider choosing the climb live, the landing
// past a pit edge, the settings window drawing. Live rows owed.
using System;
using System.IO;
using RimMandrake.FlowWorks;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class WallClimbChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string Src(params string[] rel) => RiverSwitchFlipChecks.Src(Path.Combine(rel));

        public static void Run(Action<string, Action> Case)
        {
            Case("WallClimb_which_things_are_walls", () =>
            {
                Assert(RM_WallClimbMath.IsClimbableWallKind(true, false, false, false, true, false), "a built impassable wall");
                Assert(RM_WallClimbMath.IsClimbableWallKind(true, false, false, false, false, true), "an impassable fence");
                Assert(!RM_WallClimbMath.IsClimbableWallKind(false, false, false, false, false, true), "can-fail: a fence people walk through is no wall");
                Assert(!RM_WallClimbMath.IsClimbableWallKind(true, true, false, false, true, false), "can-fail: a door opens");
                Assert(!RM_WallClimbMath.IsClimbableWallKind(true, false, true, false, true, false), "can-fail: mineable rock is a cliff");
                Assert(!RM_WallClimbMath.IsClimbableWallKind(true, false, false, true, false, false), "can-fail: natural rock");
                Assert(!RM_WallClimbMath.IsClimbableWallKind(true, false, false, false, false, false), "can-fail: an impassable machine is not scaled");
            });
            Case("WallClimb_gear_required_raiders_by_setting", () =>
            {
                Assert(RM_WallClimbMath.MayClimb(true, true, true, true, false), "a colonist in gear");
                Assert(RM_WallClimbMath.MayClimb(true, true, true, false, true), "a raider in gear, raiders may climb (the default)");
                Assert(!RM_WallClimbMath.MayClimb(false, true, true, true, true), "can-fail: no gear, no climb");
                Assert(!RM_WallClimbMath.MayClimb(true, false, true, true, true), "can-fail: climbing gear switched off");
                Assert(!RM_WallClimbMath.MayClimb(true, true, false, true, true), "can-fail: wall climbing switched off");
                Assert(!RM_WallClimbMath.MayClimb(true, true, true, false, false), "can-fail: raiders barred by the setting");
            });
            Case("WallClimb_unroofed_on_both_sides_and_the_wall", () =>
            {
                Assert(RM_WallClimbMath.CrossingOpen(1, false, false, false, true, true), "open sky over the wall and both sides");
                Assert(RM_WallClimbMath.CrossingOpen(2, false, false, false, true, true), "a double wall");
                Assert(!RM_WallClimbMath.CrossingOpen(1, false, true, false, true, true), "can-fail: the near side roofed");
                Assert(!RM_WallClimbMath.CrossingOpen(1, false, false, true, true, true), "can-fail: the far side roofed");
                Assert(!RM_WallClimbMath.CrossingOpen(1, true, false, false, true, true), "can-fail: the wall square roofed");
                Assert(!RM_WallClimbMath.CrossingOpen(1, false, false, false, true, false), "can-fail: nowhere to land");
                Assert(!RM_WallClimbMath.CrossingOpen(RM_WallClimbMath.MaxWallSquares + 1, false, false, false, true, true), "can-fail: too thick");
                Assert(!RM_WallClimbMath.CrossingOpen(0, false, false, false, true, true), "can-fail: no wall to climb");
            });
            Case("WallClimb_is_slow_x20", () =>
            {
                // Owner 2026-10-18 by card: "climbing should be SLOOOWW. Like x20 slow".
                float step = RM_WallClimbMath.PersonTicksPerCell;
                int one = RM_WallClimbMath.ClimbTicks(1, RM_WallClimbMath.DefaultSlowFactor, step);
                Assert(RM_WallClimbMath.DefaultSlowFactor == 20f, "the default is x20");
                Assert(one == (int)Math.Round(20f * step), "a person: one wall square is twenty of its steps");
                Assert(RM_WallClimbMath.ClimbTicks(2, 20f, step) == 2 * one, "a double wall takes twice as long");
                Assert(RM_WallClimbMath.ClimbTicks(1, 40f, step) == 2 * one, "the slowness setting doubles it");
                Assert(RM_WallClimbMath.ClimbTicks(1, 20f, 2f * step) == 2 * one, "a slow walker climbs slower");
                Assert(RM_WallClimbMath.ClimbTicks(1, 20f, 0f) == one, "can-fail: an unknown step is a person's");
                Assert(RM_WallClimbMath.ClimbTicks(1, 1f, 1f) >= 60, "can-fail: never under a second");
                Assert(RM_WallClimbMath.StepCost(1000f, 1000f) == RM_WallClimbMath.MaxStepCost && RM_WallClimbMath.MaxStepCost < 10000,
                    "can-fail: the planner's price stays under the pathfinder's impassable");
                Assert(RM_WallClimbMath.StepCost(20f, step) == one, "the planner charges what the climb takes");
            });
            Case("WallClimb_routes_only_when_shorter", () =>
            {
                Assert(RM_WallClimbMath.ClimbIsShorter(true, 900f, true, 600f), "over the wall is quicker than round");
                Assert(!RM_WallClimbMath.ClimbIsShorter(true, 600f, true, 600f), "can-fail: a tie walks round");
                Assert(!RM_WallClimbMath.ClimbIsShorter(true, 400f, true, 600f), "can-fail: round is quicker, walk it");
                Assert(RM_WallClimbMath.ClimbIsShorter(false, -1f, true, 600f), "no ordinary route: climb");
                Assert(!RM_WallClimbMath.ClimbIsShorter(true, 900f, false, 600f), "can-fail: no climb route");
                // The x20 rule in path terms: a person walking round a 10-square wall (about 20 extra steps) climbs only
                // when the detour costs more than the climb (20 steps a square).
                int climb = RM_WallClimbMath.StepCost(20f, RM_WallClimbMath.PersonTicksPerCell);
                float s = RM_WallClimbMath.PersonTicksPerCell;
                Assert(!RM_WallClimbMath.ClimbIsShorter(true, 30f * s, true, 10f * s + climb), "can-fail: a 20-step detour is not worth a climb");
                Assert(RM_WallClimbMath.ClimbIsShorter(true, 60f * s, true, 10f * s + climb), "a 50-step detour is");
            });
            Case("WallClimb_gear_chance", () =>
            {
                Assert(RM_WallClimbMath.GearChance(0f, 0.35f, false, 1f, 1f, true, false) == 0.35f, "a named faction's chance");
                Assert(RM_WallClimbMath.GearChance(0.08f, 0f, false, 1f, 1f, true, false) == 0.08f, "a light raider kind's chance");
                Assert(RM_WallClimbMath.GearChance(0.08f, 0.35f, false, 1f, 1f, true, false) == 0.35f, "the higher of kind and faction");
                Assert(RM_WallClimbMath.GearChance(0f, 0f, true, 1f, 1f, true, false) == 1f, "breachers and sappers from anyone");
                Assert(RM_WallClimbMath.GearChance(0f, 0f, false, 1f, 1f, true, false) == 0f, "can-fail: an ordinary pawn of an unnamed faction");
                Assert(RM_WallClimbMath.GearChance(0f, 0.35f, true, 1f, 1f, true, true) == 0f, "can-fail: never the player's own");
                Assert(RM_WallClimbMath.GearChance(0f, 0.35f, true, 1f, 1f, false, false) == 0f, "can-fail: setting off");
                Assert(RM_WallClimbMath.GearChance(0f, 0.35f, false, 1f, 0f, true, false) == 0f, "can-fail: scale 0");
                Assert(RM_WallClimbMath.GearChance(0f, 0.5f, false, 1f, 3f, true, false) == 1f, "can-fail: clamped to 1");
            });
            Case("WallClimb_pathfind_budget_and_memos", () =>
            {
                // WALL_CLIMB_FIX_BUDGET_CAP_LEAKY_MEMOS: the cap counted PLANS (3 a tick) but each plan runs two FindPathNow (6 a
                // tick), the raider seam ran one per gear-wearer with no tick cap, and the memos outlived loading an earlier save.
                var b = new RM_WallClimbMath.PathfindBudget();
                Assert(RM_WallClimbMath.PathfindsPerTick == 3, "3 pathfinds a tick, colonist planner and raiders together");
                Assert(RM_WallClimbMath.PlanPathfinds == 2 && RM_WallClimbMath.RaiderPathfinds == 1,
                    "a route plan is two pathfinds (through the walls, then the ordinary route); a raider's is one");
                Assert(b.TryTake(100, RM_WallClimbMath.PlanPathfinds), "the first plan of the tick");
                Assert(!b.TryTake(100, RM_WallClimbMath.PlanPathfinds), "can-fail: a second plan would make 4 pathfinds");
                Assert(b.TryTake(100, RM_WallClimbMath.RaiderPathfinds), "a raider takes the third");
                Assert(!b.TryTake(100, RM_WallClimbMath.RaiderPathfinds), "can-fail: a fourth raider waits for the next tick");
                Assert(b.UsedAt(100) == 3, "exactly 3 used");
                int raiders = 0;
                for (int i = 0; i < 40; i++) if (b.TryTake(101, RM_WallClimbMath.RaiderPathfinds)) raiders++;
                Assert(raiders == 3, "a raid of 40 gear-wearers runs 3 through-walls pathfinds in a tick, not 40 (" + raiders + ")");
                Assert(b.TryTake(50, RM_WallClimbMath.PlanPathfinds), "an earlier tick (a loaded save) gets a fresh budget");
                Assert(!b.TryTake(50, 0) && !b.TryTake(50, 4), "can-fail: a take of nothing, or more than a tick holds, is refused");
                // memos: an earlier-tick save must not keep a memo alive (the old "now - stamp < window" never expired backwards)
                Assert(!RM_WallClimbMath.MemoExpired(1000, 1100, 250) && RM_WallClimbMath.MemoExpired(1000, 1250, 250), "the window");
                Assert(RM_WallClimbMath.MemoExpired(1000, 400, 250), "can-fail: time went backwards: expired");
                Assert(RM_WallClimbMath.MemoExpired(int.MinValue, 5, 60) && RM_WallClimbMath.MemoExpired(int.MinValue, -5, 60),
                    "a never-set stamp is spent (no overflow)");
                Assert(RM_WallClimbMath.TimeWentBack(1000, 999) && !RM_WallClimbMath.TimeWentBack(1000, 1000)
                    && !RM_WallClimbMath.TimeWentBack(int.MinValue, 5), "time going back is noticed (never on the first look)");
                // wired
                string w = Src("Superdeep", "RM_WallClimb.cs");
                RiverSwitchFlipChecks.Has(w, @"RM_WallClimbMemo\.Budget\.TryTake\(now, RM_WallClimbMath\.PlanPathfinds\)", "the planner pays two pathfinds");
                RiverSwitchFlipChecks.Has(w, @"RM_WallClimbMemo\.Budget\.TryTake\(now, RM_WallClimbMath\.RaiderPathfinds\)", "the raider seam pays from the same budget");
                Assert(!w.Contains("MaxPlansPerTick") && !w.Contains("budgetUsed"), "can-fail: the per-plan counter is gone");
                RiverSwitchFlipChecks.Has(w, @"\[HarmonyPatch\(typeof\(Game\), nameof\(Game\.FinalizeInit\)\)\]", "memos cleared when a game loads");
                RiverSwitchFlipChecks.Has(w, @"RM_WallClimbMath\.TimeWentBack\(lastSeenTick, now\)", "and whenever the tick goes backwards");
                foreach (string m in new[] { "RM_WallClimbRoute.ClearMemos();", "RM_Patch_GotoHostile_Climb.ClearMemos();", "RM_WallClimbGrid.ClearMemos();", "Budget.Reset();" })
                {
                    Assert(w.Contains(m), "cleared on load: " + m);
                }
                Assert(!w.Contains("now - lp.Value < ReplanSameDestTicks") && !w.Contains("now - g.builtTick < RebuildTicks")
                    && !w.Contains("now < at"), "can-fail: no memo window that never expires backwards");
                RiverSwitchFlipChecks.Has(w, @"!p\.Spawned \|\| p\.Map == null", "despawned pawns are pruned from pending");
            });
            Case("WallClimb_wiring", () =>
            {
                string w = Src("Superdeep", "RM_WallClimb.cs");
                RiverSwitchFlipChecks.Has(w, @"RM_WallClimbMath\.IsClimbableWallKind\(d\.passability == Traversability\.Impassable,\s*d\.IsDoor, d\.mineable, d\.building\.isNaturalRock, d\.IsWall, d\.IsFence\)", "walls read from def flags");
                RiverSwitchFlipChecks.Has(w, @"RM_WallClimbMath\.CrossingOpen\(squares, anyRoof, fromRoofed, toRoofed, from\.Standable\(map\), c\.Standable\(map\)\)", "the roof rule on the wall and both sides");
                RiverSwitchFlipChecks.Has(w, @"RM_PocketGrid\.WearsClimbingGear\(p\)", "gear read from worn apparel");
                RiverSwitchFlipChecks.Has(w, @"\[HarmonyPatch\(typeof\(DigUtility\), nameof\(DigUtility\.PassBlockerJob\)\)\]", "sappers climb");
                RiverSwitchFlipChecks.Has(w, @"\[HarmonyPatch\(typeof\(JobGiver_AIBreaching\), ""TryGiveJob""\)\]", "breachers climb");
                RiverSwitchFlipChecks.Has(w, @"\[HarmonyPatch\(typeof\(Pawn_PathFollower\), ""TryEnterNextPathCell""\)\]", "a blocked path climbs instead of bashing");
                RiverSwitchFlipChecks.Has(w, @"\[HarmonyPatch\(typeof\(JobGiver_AIGotoNearestHostile\), ""TryGiveJob""\)\]", "raiders with no way in climb");
                RiverSwitchFlipChecks.Has(w, @"class FloatMenuOptionProvider_RM_ClimbOverWall : FloatMenuOptionProvider", "colonists ordered over");
                RiverSwitchFlipChecks.Has(w, @"RM_WallClimbMath\.ClimbTicks\(squares, RM_WallClimbSettings\.wallClimbSlowFactor,\s*pawn\.TicksPerMoveCardinal\)", "the climb lasts slowFactor of the pawn's steps");
                RiverSwitchFlipChecks.Has(w, @"\[HarmonyPatch\(typeof\(Pawn_PathFollower\), nameof\(Pawn_PathFollower\.StartPath\)\)\]\s*\[RimMandrake\.Shared\.PatchFeature\(""Climbing gear routes over walls""", "walks are planned");
                RiverSwitchFlipChecks.Has(w, @"\[HarmonyPatch\(typeof\(Pawn_PathFollower\), nameof\(Pawn_PathFollower\.PatherTick\)\)\]", "the plan runs on the next pather tick");
                RiverSwitchFlipChecks.Has(w, @"tuning\.costBlockedWallBase = RM_WallClimbMath\.StepCost\(RM_WallClimbSettings\.wallClimbSlowFactor, p\.TicksPerMoveCardinal\);\s*tuning\.costBlockedWallExtraPerHitPoint = 0f;", "the planner prices a wall square at the climb");
                RiverSwitchFlipChecks.Has(w, @"TraverseMode\.PassAllDestroyablePlayerOwnedThings", "only the player's walls are passable to the planner");
                RiverSwitchFlipChecks.Has(w, @"class RM_WallClimbGrid : PathRequest\.IPathGridCustomizer", "the other buildings shut by the offset grid");
                RiverSwitchFlipChecks.Has(w, @"offsets\[idx\.CellToIndex\(c\)\] = 10000;", "shut means >= 10000 (PathGridJob.CellIsPassable)");
                RiverSwitchFlipChecks.Has(w, @"map\.reachability\.CanReach\(landing, dest, peMode, TraverseParms\.For\(p, Danger\.Deadly\)\)", "the landing must reach the destination (no stall)");
                RiverSwitchFlipChecks.Has(w, @"RM_WallClimbMath\.ClimbIsShorter\(found, found \? normal\.TotalCost : -1f, true, climbCost\)", "only when shorter than the ordinary route");
                RiverSwitchFlipChecks.Has(w, @"if \(!RM_WallClimbRoute\.AnyPending \|\| ___pawn == null\)", "can-fail: nobody pays while nothing is pending");
                RiverSwitchFlipChecks.Has(w, @"\[HarmonyPatch\(typeof\(PawnGenerator\), ""GenerateGearFor""\)\]", "raiders dressed with gear at generation");
                RiverSwitchFlipChecks.Has(w, @"\[HarmonyPatch\(typeof\(RaidStrategyWorker\), nameof\(RaidStrategyWorker\.MakeLords\)\)\]", "breach and sapper raids dress their workers");
                RiverSwitchFlipChecks.Has(w, @"sappers \? p\.kindDef\.canBeSapper : \(p\.kindDef\.isGoodBreacher \|\| BreachingUtility\.IsGoodBreacher\(p\)\)", "breachers and sappers from anyone");
                RiverSwitchFlipChecks.Has(w, @"RM_WallClimbMath\.GearChance\(kindChance, facChance, false, 0f,", "can-fail: generation never gives every sapper-capable kind the gear");
                RiverSwitchFlipChecks.Has(w, @"ApparelUtility\.CanWearTogether\(gearDef, worn\[i\]\.def, pawn\.RaceProps\.body\)", "can-fail: never replaces what is worn");
                string s = Src("Superdeep", "RM_WallClimbSettings.cs");
                foreach (string f in new[] { "wallClimbEnabled", "wallClimbSlowFactor", "raidersMayClimbWalls", "wallClimbAutoRoute",
                    "raidersCarryClimbingGear", "raiderGearChanceScale", "breacherSapperGearChance" })
                {
                    Assert(s.Contains("ref " + f + ", \"" + f + "\""), "scribed setting " + f);
                }
                Assert(s.Contains("public static bool raidersMayClimbWalls = true;"), "raiders climb by default (owner by card)");
                Assert(s.Contains("public static float wallClimbSlowFactor = RM_WallClimbMath.DefaultSlowFactor;")
                    && s.Contains("public static bool wallClimbAutoRoute = true;") && s.Contains("public static bool raidersCarryClimbingGear = true;"),
                    "x20, routing and raider gear on by default (owner by card)");
                string vp = Src("..", "Patches", "Pits", "FlowWorks_ClimbingGearRaiders.xml");
                foreach (string k in new[] { "Tribal_Penitent", "Tribal_Archer", "Tribal_Warrior", "Tribal_Hunter", "Drifter", "Scavenger", "Thrasher" })
                {
                    Assert(vp.Contains("defName=\"" + k + "\""), "light raider kind patched: " + k);
                }
                Assert(vp.Contains("RimMandrake.FlowWorks.RM_ClimbingGearChance"), "the chance extension");
                string up = RiverSwitchFlipChecks.Src(Path.Combine("..", "..", "..", "RimUtinni", "UtinniPatches", "Patches", "ClimbingGear_JawaFactions.xml"));
                foreach (string f in new[] { "RUT_Jawa_WildsteamClan", "RUT_Jawa_Junkers", "Pirate", "RUT_Jawa_IndigenousTribes", "TribeCivil" })
                {
                    Assert(up.Contains("defName=\"" + f + "\""), "named faction patched: " + f);
                }
                Assert(up.Contains("<li>mandrake.rm.flowworks</li>"), "can-fail: the Utinni patch is guarded on FlowWorks (the extension type)");
                string mod = Src("RimMandrakeFlowWorksMod.cs");
                Assert(mod.Contains("RM_WallClimbSettings.ExposeData();") && mod.Contains("RM_WallClimbSettings.DoSettingsSection);"), "settings scribed and drawn");
                string csproj = Src("RimMandrake_FlowWorks.csproj");
                foreach (string f in new[] { "RM_WallClimbMath.cs", "RM_WallClimbSettings.cs", "RM_WallClimb.cs" })
                {
                    Assert(csproj.Contains("Superdeep\\" + f), "compiled: " + f);
                }
                string jobs = Src("..", "Defs", "Canals", "JobDefs", "FlowWorks_WallClimb.xml");
                Assert(jobs.Contains("<defName>RM_ClimbOverWall</defName>") && jobs.Contains("JobDriver_RM_ClimbOverWall"), "the climb job def");
            });
        }
    }
}
