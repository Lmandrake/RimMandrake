// FlowWorks code-review batches 5 and 6 (2026-10-11): offline guards for the behaviour fixes. Each case reads the
// PRODUCTION source (whitespace collapsed, RiverSwitchFlipChecks.Src) and requires the fixed shape, so a revert fails here.
// Where the fix rests on a Verse-free rule (RM_PlacerMath) the rule is exercised too.
// NOT proven here: anything a live map decides (a pawn actually pathing round a burning cover, a projectile's
// launch origin in game, a frame's occlusion). Those stay live checks.
using System;
using System.IO;
using RimMandrake.FlowWorks.Quarry;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class ReviewBatch56Checks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string Src(params string[] rel) => RiverSwitchFlipChecks.Src(Path.Combine(rel));

        /// <summary>The text from <paramref name="start"/> up to the next <paramref name="end"/> after it.</summary>
        private static string Between(string src, string start, string end)
        {
            int i = src.IndexOf(start, StringComparison.Ordinal);
            Assert(i >= 0, "marker present: " + start);
            int j = src.IndexOf(end, i + start.Length, StringComparison.Ordinal);
            return j < 0 ? src.Substring(i) : src.Substring(i, j - i);
        }

        private static int At(string src, string what)
        {
            int i = src.IndexOf(what, StringComparison.Ordinal);
            Assert(i >= 0, "present: " + what);
            return i;
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("TankSearch_refusal_only_from_usable_tanks", () =>
            {
                string s = Src("LiquidTypes", "RM_LiquidTankUtility.cs");
                string body = Between(s, "private static bool TryFindTank(", "tank = best;");
                Assert(At(body, "CanReach(candidate") < At(body, "predicate(candidate)"),
                    "the refusal-recording predicate runs after the forbidden/reserve/range/reach filters");
                Assert(At(body, "IsForbidden(pawn)") < At(body, "predicate(candidate)"), "forbidden tanks never reach the predicate");
                Assert(!s.Contains("TryFindTankToDrain(Pawn pawn, RM_ContainerSize size"), "dead size-only drain overload removed");
                string b = Src("LiquidTypes", "RM_LiquidBottleUtility.cs");
                Assert(!b.Contains("TryFindFillCell(Pawn pawn, out IntVec3 cell"), "dead container-less fill overload removed");
            });
            Case("PitCover_path_cost_keeps_fire_snow_and_doors", () =>
            {
                string s = Between(Src("Pits", "Building_PitCover.cs"), "class RM_Patch_PathGrid_PitCoverCost", "class ZZZ_none");
                Assert(s.Contains("ref int? baseCostOverride"), "the cover's cost goes in as the base-cost override");
                Assert(s.Contains("baseCostOverride = Mathf.Max(cover.def.pathCost, 0)"), "override = cover pathCost");
                Assert(s.Contains("if (baseCostOverride.HasValue)"), "an override already set (water, pit step) is left alone");
                Assert(!s.Contains("__result ="), "can-fail: the total cost is never overwritten (fire/snow/door add-ons survive)");
            });
            Case("PlacerStock_cap_follows_the_setting_live", () =>
            {
                Assert(Math.Abs(RM_PlacerMath.StockCap(1000f, 2f) - 20f) < 1e-4f, "2% of 1000");
                Assert(Math.Abs(RM_PlacerMath.StockCap(1000f, 5f) - 50f) < 1e-4f, "can-fail: moving the slider moves the cap");
                Assert(RM_PlacerMath.Regrow(50f, 20f, 0) == 20f, "a lowered cap clamps the stock");
                string s = Src("Quarry", "RM_PlacerWorks.cs");
                Assert(s.Contains("CapNow => RM_PlacerMath.StockCap(units, RM_QuarrySettings.placerStockPercent)"),
                    "the cap is derived live from the saved base and the current setting");
                Assert(!s.Contains("\"RM_placerCap\""), "the cap itself is no longer saved (it froze the slider)");
                Assert(s.Contains("Scribe_Values.Look(ref units, \"RM_placerUnits\""), "the base is saved");
            });
            Case("PlacerStock_debited_only_after_placement", () =>
            {
                string s = Src("Quarry", "RM_PlacerWorks.cs");
                Assert(At(s, "TryPlaceThing(t, BankCell") < At(s, "stock.Take(got); stock.SluiceUnits += got;"),
                    "sluice: place first, then debit what was placed");
                Assert(At(s, "TryPlaceThing(t, pawn.Position") < At(s, "stock.Take(got); stock.PanUnits += got;"),
                    "pan: place first, then debit what was placed");
                Assert(!s.Contains("int got = stock?.Take(want)") && !s.Contains("int got = stock.Take(want)"),
                    "can-fail: no debit before placement");
            });
            Case("RiverCurrent_cheap_test_first_and_no_stack_on_stack", () =>
            {
                string s = Src("Rivers", "RM_MapComponent_RiverCurrent.cs");
                string scan = Between(s, "private void Scan()", "present.Add(t);");
                Assert(At(scan, "HasCurrent(t.Position)") < At(scan, "IsCarried(t)"), "the O(1) current test runs before IsCarried");
                string step = Between(s, "public void StepOne(Thing t)", "Move(t, next);");
                Assert(step.Contains("!(t is Pawn) && next.GetFirstItem(map) != null"),
                    "a drifting item never lands on a cell already holding an item");
            });
            Case("FerryPathProof_destroys_only_its_own_posts", () =>
            {
                string s = Src("Rivers", "RM_RiverWorksProofWorks.cs");
                string body = Between(s, "public static string ProofFerryPath(string arg)", "private static void DestroyIfSpawned");
                Assert(body.Contains("SpawnFerry(\"keep\", out Thing postA, out Thing postB)"), "the probe keeps hold of its two posts");
                Assert(body.Contains("DestroyIfSpawned(postA)") && body.Contains("DestroyIfSpawned(postB)"), "and removes exactly those");
                Assert(!body.Contains("ThingsOfDef(RM_RiverWorksDefOf.RM_FerryPost)"), "can-fail: never every ferry post on the map");
            });
            Case("PitDepthDraw_shots_leave_from_the_unsunk_position", () =>
            {
                string s = Src("Superdeep", "RM_PitDepthDraw.cs");
                Assert(s.Contains("[HarmonyPatch(typeof(Verb), \"TryCastNextBurstShot\")]"), "the firing window is patched");
                Assert(s.Contains("[HarmonyFinalizer]") && s.Contains("Firing--"), "the window always closes, even on a throw");
                string post = Between(s, "public static void Postfix(Pawn_DrawTracker __instance", "float sink = SinkOf(");
                Assert(post.Contains("RM_Patch_PitDepthDrawCombatOrigin.Firing > 0"), "DrawPos is unsunk while a verb fires");
            });
            Case("PitLipOcclusion_pawn_rects_read_once_per_frame", () =>
            {
                string s = Src("Superdeep", "RM_PitLipOcclusion.cs");
                string hit = Between(s, "private bool HitsShallowerPawn(", "public override void MapComponentUpdate()");
                Assert(!hit.Contains("DrawPos") && !hit.Contains("AllPawnsSpawned"), "the per-piece test reads the frame's cached rects");
                Assert(s.Contains("if (!rectsBuilt)"), "the rects are built once per update");
            });
        }
    }
}
