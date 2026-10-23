// Owner cards 2026-10-22. PIT_COVER_WIDEN_PLANKS_BEAR_BOOTS ("covered cells are floor"): a planked square of a partly covered
// pit is ground to walkers (depth, hold, open-pit set, path cost), only the open squares are the pit, a pawn beneath a lid
// stays below, and laying or lifting a lid tells the path grid, the pathfinder and the reach cache at once.
// DRILL_PLACEMENT_ENFORCE_NO_DRY_HOLES ("Refuse on empty survey"): a drill or bleed well is refused where the survey found
// nothing (or the reserve is spent); unsurveyed ground is still allowed with its hint. Each case has a can-fail.
// NOT proven here: the live game (a pawn walking the planks of a half-covered pit; the refusal message under the mouse).
using System;
using System.IO;
using RimMandrake.FlowWorks.Drilling;
using RimMandrake.FlowWorks.Pits;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class CoverFloorSurveyChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string Src(params string[] rel) => RiverSwitchFlipChecks.Src(Path.Combine(rel));

        public static void Run(Action<string, Action> Case)
        {
            Case("CoverFloor_planked_squares_are_ground_open_squares_the_pit", () =>
            {
                string trap = Src("Superdeep", "RM_SuperdeepTrap.cs");
                string path = Src("Superdeep", "RM_PitPathing.cs");
                string cover = Src("Pits", "Building_PitCover.cs");
                Assert(trap.Contains("return d > 0 && Pits.RM_PitCoverUtility.IsCovered(map, c) ? Pits.RM_SpanUtility.WalkingDepth(map, c, d) : d;"),
                    "StepDepthAt: a covered square is ground at the deck's walking height");
                Assert(trap.Contains("if (!onD4 || !RuleOn || Pits.RM_PitCoverUtility.IsCovered(p.Map, c))"), "nobody is held on a lid (absolute rule)");
                Assert(path.Contains("return eng.IsSuperdeepExcavation(c) && !Pits.RM_PitCoverUtility.IsCovered(map, c);"), "only an open square is in the open-pit set");
                Assert(path.Contains("return eng.ClimbDepthAt(c) > 0 && !Pits.RM_PitCoverUtility.IsCovered(map, c);"), "only an open square is a hole to fall into");
                Assert(cover.Contains("baseCostOverride = Mathf.Max(cover.def.pathCost, 0);"), "a lid costs its own path cost, not the hole's 300");
                // can-fail: the beneath rule still stands (last night's ruling): a pawn below stays below
                Assert(!RM_PitCoverBeneathMath.StepAllowed(false, true, true, 4, 4, 2), "can-fail: a beneath pawn never walks under the next lid");
                Assert(!RM_PitCoverBeneathMath.StepAllowed(false, false, false, 4, 0, 2), "can-fail: a beneath pawn never pops up onto the planks");
            });

            Case("CoverFloor_laying_or_lifting_a_lid_invalidates_path_and_reach", () =>
            {
                string span = Src("Pits", "Building_SpanDeck.cs");
                int at = span.IndexOf("public static void Notify_DeckPathChanged(Map map, IntVec3 c, bool loading)", StringComparison.Ordinal);
                Assert(at > 0, "the deck change notifier exists");
                string body = span.Substring(at, Math.Min(900, span.Length - at));
                Assert(body.Contains("BumpClimbGeneration()"), "the climb generation moves (pocket grid, masks)");
                Assert(body.Contains("map.pathing?.RecalculatePerceivedPathCostAt(c);"), "the square's path cost is re-read");
                Assert(body.Contains("map.pathFinder?.MapData?.Notify_CellDelta(c);"), "the pathfinder's cell update runs (masks re-check)");
                Assert(body.Contains("map.reachability?.ClearCache();"), "the reach cache is cleared");
                // can-fail: both the spawn and the despawn must call it (a lid lifted is as much a change as one laid)
                Assert(span.Contains("Notify_DeckPathChanged(map, Position, respawningAfterLoad);"), "can-fail: laying a lid notifies");
                Assert(span.Contains("Notify_DeckPathChanged(map, pos, false);"), "can-fail: lifting (or breaking) a lid notifies");
            });

            Case("DrillWhyNot_each_condition_names_its_reason", () =>
            {
                RM_DrillSurveyMath.State ok = new RM_DrillSurveyMath.State { settingOn = true, switchedOn = true, needsPower = true, powered = true,
                    surveyed = true, hasYield = true, reserve = 100f, hasCanalForm = true, fluidAllowed = true, outletDug = true };
                Assert(RM_DrillSurveyMath.WhyNot(ok) == RM_DrillSurveyMath.Block.None, "all good: runs");
                var s = ok; s.settingOn = false; Assert(RM_DrillSurveyMath.WhyNot(s) == RM_DrillSurveyMath.Block.DisabledInSettings, "settings off");
                s = ok; s.switchedOn = false; Assert(RM_DrillSurveyMath.WhyNot(s) == RM_DrillSurveyMath.Block.SwitchedOff, "switched off");
                s = ok; s.powered = false; Assert(RM_DrillSurveyMath.WhyNot(s) == RM_DrillSurveyMath.Block.Unpowered, "unpowered");
                s = ok; s.needsPower = false; s.powered = false; Assert(RM_DrillSurveyMath.WhyNot(s) == RM_DrillSurveyMath.Block.None, "can-fail: a bleed well needs no power");
                s = ok; s.surveyed = false; Assert(RM_DrillSurveyMath.WhyNot(s) == RM_DrillSurveyMath.Block.Unsurveyed, "unsurveyed");
                s = ok; s.hasYield = false; Assert(RM_DrillSurveyMath.WhyNot(s) == RM_DrillSurveyMath.Block.NoSubsurface, "no subsurface liquid");
                s = ok; s.hasCanalForm = false; Assert(RM_DrillSurveyMath.WhyNot(s) == RM_DrillSurveyMath.Block.NoCanalForm, "no canal form");
                s = ok; s.outletDug = false; Assert(RM_DrillSurveyMath.WhyNot(s) == RM_DrillSurveyMath.Block.OutletNotDug, "outlet not dug");
                s = ok; s.outletOtherLiquid = true; Assert(RM_DrillSurveyMath.WhyNot(s) == RM_DrillSurveyMath.Block.OutletOtherLiquid, "outlet other liquid");
                s = ok; s.fluidAllowed = false; Assert(RM_DrillSurveyMath.WhyNot(s) == RM_DrillSurveyMath.Block.LiquidDisabledInSettings, "liquid off in settings");
                s = ok; s.outletBrimming = true; Assert(RM_DrillSurveyMath.WhyNot(s) == RM_DrillSurveyMath.Block.OutletBrimming, "brimming");
                s = ok; s.reserve = 0f; Assert(RM_DrillSurveyMath.WhyNot(s) == RM_DrillSurveyMath.Block.ReserveSpent, "reserve spent");
                s = ok; s.switchedOn = false; s.settingOn = false; Assert(RM_DrillSurveyMath.WhyNot(s) == RM_DrillSurveyMath.Block.DisabledInSettings, "settings outranks the switch");
                string drill = Src("Drilling", "Building_LiquidDrill.cs");
                Assert(drill.Contains("flick == null || flick.SwitchIsOn"), "the tick honours the switch (no bleed, no power)");
                foreach (RM_DrillSurveyMath.Block b in Enum.GetValues(typeof(RM_DrillSurveyMath.Block)))
                {
                    string key = "<RM_DrillWhy_" + b + ">";
                    Assert(RiverSwitchFlipChecks.Src(Path.Combine("..", "Languages", "English", "Keyed", "FlowWorks_Keys.xml")).Contains(key), "key for " + b);
                }
            });

            Case("DrillSurvey_empty_survey_refuses_unsurveyed_allows", () =>
            {
                Assert(RM_DrillSurveyMath.Placement(true, true, 50f) == RM_DrillSurveyMath.Verdict.Allowed, "a find with reserve: allowed");
                Assert(RM_DrillSurveyMath.Placement(false, false, 0f) == RM_DrillSurveyMath.Verdict.Allowed, "unsurveyed: allowed (hint only)");
                Assert(RM_DrillSurveyMath.Placement(true, false, 0f) == RM_DrillSurveyMath.Verdict.NoYield, "can-fail: surveyed, nothing found: refused");
                Assert(RM_DrillSurveyMath.Placement(true, true, 0f) == RM_DrillSurveyMath.Verdict.Spent, "can-fail: reserve drawn to zero: refused");
            });

            Case("DrillSurvey_placeworker_wired_on_drill_and_bleed_well", () =>
            {
                string drill = Src("Drilling", "Building_LiquidDrill.cs");
                Assert(drill.Contains("RM_DrillSurveyMath.Placement(survey.Surveyed, survey.HasYield, survey.ReserveRemaining)"), "the PlaceWorker asks the survey");
                Assert(drill.Contains("return \"RM_DrillPlaceNoYield\".Translate();") && drill.Contains("return \"RM_DrillPlaceSpent\".Translate();"),
                    "the refusal says why");
                Assert(drill.Contains("if (survey == null || !survey.Surveyed)"), "the hint reads an unrolled survey as unsurveyed");
                string srcDir = Path.GetDirectoryName(RiverSwitchFlipChecks.SrcPath("RM_FlowKernel.cs"));
                string defs = File.ReadAllText(Path.Combine(srcDir, "..", "Defs", "Drilling", "ThingDefs", "RM_LiquidDrill.xml"));
                int n = 0, i = 0;
                while ((i = defs.IndexOf("PlaceWorker_DrillNeedsExcavatedOutlet", i, StringComparison.Ordinal)) >= 0) { n++; i++; }
                // can-fail: the bleed well (RM_LiquidTap) must carry it too, not only the drill
                Assert(n >= 2 && defs.Contains("<defName>RM_LiquidTap</defName>"), "both the drill and the bleed well carry the PlaceWorker (" + n + ")");
            });
        }
    }
}
