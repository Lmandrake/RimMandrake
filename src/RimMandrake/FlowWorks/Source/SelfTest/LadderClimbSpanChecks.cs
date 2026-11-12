// RIMMANDRAKE_FIX_CLIMB_SLOW_OUTLASTS_LADDER (owner 2026-11-12): "when the pawn climbed the ladder up and down, they remain in
// the slowed/climbing mode long after they visually leave the ladder (almost twice the vertical length), so that should be
// altered to only correspond when they are crossing the ladder texture itself."
// Mechanism: a ladder climb is ONE path step (floor to lip) costing RM_PitTrapMath.StepCost's ladder cost (depth 4: 300 x 2 x 4,
// capped by vanilla at 450 ticks; depth 1: 60 + the walk) and vanilla tweens it at one steady pace, so the slow crawl covered the
// drawn path, 1 + sink cells (2.2 at depth 4), while the rail ladder's north art spans 0.61. The fix keeps the step's time and
// draws the pawn at walking pace off the art's span and slowly only on it (RM_PitDrawMath.ClimbProgress).
// Each case has a can-fail. NOT proven here: the live walk (flowworks proof rows ladder_climb_span_*).
using System;
using System.IO;
using System.Text.RegularExpressions;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class LadderClimbSpanChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string Src(params string[] rel) => RiverSwitchFlipChecks.Src(Path.Combine(rel));

        // the pit room of the owner's save: the ladder in the floor cell (x, 10) hung north toward the lip cell (x, 11);
        // the rail ladder: drawSize 1.5, drawOffsetNorth +0.25 z, north art opaque 0.33~0.74 of the quad
        private const float LadderLo = 10.5f + 0.25f - 0.75f + 0.33f * 1.5f;   // 10.495
        private const float LadderHi = 10.5f + 0.25f - 0.75f + 0.74f * 1.5f;   // 11.11

        private static float FloorDrawnZ(int depth) => 10.5f - RM_PitDrawMath.SinkFor(depth, 0.3f);

        // the time share of the step spent with the drawn centre on the art's span, sampled per tick as the live rows do
        private static float ShareOnSpan(int ticks, float pa, float pb, float u0, float u1, float r, bool remap)
        {
            int on = 0;
            for (int i = 1; i <= ticks; i++)
            {
                float m = i / (float)ticks;
                float u = remap ? RM_PitDrawMath.ClimbProgress(m, u0, u1, r) : m;
                float p = pa + (pb - pa) * u;
                if (p >= LadderLo - 1e-4f && p <= LadderHi + 1e-4f) on++;
            }
            return on / (float)ticks;
        }

        internal static void Run(Action<string, Action> Case)
        {
            Case("LadderClimb_span_found_on_the_step", () =>
            {
                float pa = FloorDrawnZ(4), pb = 11.5f;   // 9.3 -> 11.5 up a depth-4 wall
                Assert(RM_PitDrawMath.LadderSpanOnStep(pa, pb, LadderLo, LadderHi, out float u0, out float u1), "span crosses the step");
                Assert(Math.Abs(u0 - (LadderLo - pa) / (pb - pa)) < 1e-4f && Math.Abs(u1 - (LadderHi - pa) / (pb - pa)) < 1e-4f, "u0/u1 " + u0 + "/" + u1);
                Assert(RM_PitDrawMath.LadderSpanOnStep(pb, pa, LadderLo, LadderHi, out float d0, out float d1) && Math.Abs(d0 - (1f - u1)) < 1e-4f && Math.Abs(d1 - (1f - u0)) < 1e-4f,
                    "coming down the same span, mirrored");
                Assert(!RM_PitDrawMath.LadderSpanOnStep(pa, pb, 20f, 21f, out _, out _), "can-fail: art off the path -> no span");
                Assert(!RM_PitDrawMath.LadderSpanOnStep(5f, 5f, LadderLo, LadderHi, out _, out _), "can-fail: no path length -> no span");
            });

            Case("LadderClimb_progress_is_continuous_and_monotone", () =>
            {
                float u0 = 0.54f, u1 = 0.82f, r = 0.064f, last = -1f;
                for (int i = 0; i <= 1000; i++)
                {
                    float u = RM_PitDrawMath.ClimbProgress(i / 1000f, u0, u1, r);
                    Assert(u >= last - 1e-5f && u >= 0f && u <= 1f, "monotone at " + i);
                    Assert(last < 0f || u - last < 0.08f, "continuous at " + i + " (jump " + (u - last) + ")");
                    last = u;
                }
                Assert(RM_PitDrawMath.ClimbProgress(0f, u0, u1, r) == 0f && Math.Abs(RM_PitDrawMath.ClimbProgress(1f, u0, u1, r) - 1f) < 1e-5f, "ends fixed");
                Assert(RM_PitDrawMath.ClimbProgress(0.3f, u0, u1, 1f) == 0.3f, "a step no slower than walking is drawn as before");
                Assert(RM_PitDrawMath.ClimbProgress(0.3f, 0.6f, 0.6f, 0.1f) == 0.3f, "no span: as before");
                Assert(RM_PitDrawMath.WalkShare(2.2f, 13f, 450f) > 0.06f && RM_PitDrawMath.WalkShare(2.2f, 13f, 450f) < 0.07f, "D4 walk share 2.2x13/450");
                Assert(RM_PitDrawMath.WalkShare(1.3f, 13f, 10f) == 1f, "can-fail: a fast step clamps to 1 (no remap)");
            });

            foreach (int depth in new[] { 1, 4 })
            {
                foreach (bool up in new[] { true, false })
                {
                    int dd = depth;
                    bool goingUp = up;
                    Case("LadderClimb_slow_only_on_the_art_D" + dd + (goingUp ? "_up" : "_down"), () =>
                    {
                        // the step's ticks: depth 1 = 30 x 2 x 1 ladder + 13 walk; depth 4 = vanilla's 450 cap
                        int ticks = dd == 1 ? 73 : 450;
                        float floor = FloorDrawnZ(dd), lip = 11.5f;
                        float pa = goingUp ? floor : lip, pb = goingUp ? lip : floor;
                        Assert(RM_PitDrawMath.LadderSpanOnStep(pa, pb, LadderLo, LadderHi, out float u0, out float u1), "span");
                        float r = RM_PitDrawMath.WalkShare(Math.Abs(pb - pa), 13f, ticks);
                        float fixedShare = ShareOnSpan(ticks, pa, pb, u0, u1, r, true);
                        float oldShare = ShareOnSpan(ticks, pa, pb, u0, u1, r, false);
                        Assert(fixedShare >= 0.8f, "D" + dd + ": " + fixedShare + " of the step's time on the ladder's art (want >= 0.8)");
                        Assert(oldShare < 0.6f, "can-fail: the steady tween spends only " + oldShare + " of it there (the owner's report)");
                        // off the art the pawn goes at walking pace: drawn cells off the span / ticks off it within 25 % of 1/13 (per-tick sampling)
                        float offCells = Math.Abs(pb - pa) * (1f - (u1 - u0));
                        float offTicks = ticks * (1f - fixedShare);
                        Assert(offTicks > 0f && Math.Abs(offCells / offTicks - 1f / 13f) < 0.25f / 13f, "walk pace off the art: " + (offCells / offTicks));
                    });
                }
            }

            Case("LadderClimb_draw_wires_the_span", () =>
            {
                string src = Src("Superdeep", "RM_PitDepthDraw.cs");
                string post = Regex.Match(src, @"public static void Postfix\(Pawn_DrawTracker __instance, ref Vector3 __result\)[\s\S]*?SinkOf\(pawn, __result\)").Value;
                Assert(post.Contains("ClimbOnLadderSpan(pawn, ref __result);"), "the remap runs before the sink is read");
                int i = src.IndexOf("private static void ClimbOnLadderSpan(", StringComparison.Ordinal);
                Assert(i > 0, "ClimbOnLadderSpan present");
                string body = src.Substring(i, src.IndexOf("public static Thing ClimbLadderOf(", i, StringComparison.Ordinal) - i);
                Assert(body.Contains("ClimbLadderOf(pawn.Map, from, to)") && body.Contains("LadderArtSpan(ladder, alongZ,"), "the climbed ladder and its art span");
                int j = src.IndexOf("public static Thing ClimbLadderOf(", StringComparison.Ordinal);
                Assert(j > 0, "ClimbLadderOf present");
                string of = src.Substring(j, src.IndexOf("public static float SinkOf(", j, StringComparison.Ordinal) - j);
                Assert(of.Contains("RM_ClimbJoins.LoweredLadderAt(map, from)") && of.Contains("RM_ClimbJoins.LoweredLadderAt(map, to)"), "up and down: the ladder in either end");
                Assert(of.Contains("HangsToward("), "only across the wall the ladder hangs on");
                Assert(of.Contains("props.ClimbSpan(ladder.Rotation)") && of.Contains("g.DrawOffset(ladder.Rotation)"), "the def's span at the drawn place");
                Assert(body.Contains("ClimbProgress(pather.MovePercentage"), "time share from the pather, not the sprung tween");
                Assert(body.Contains("pawn.TicksPerMoveCardinal, pather.nextCellCostTotal"), "walk pace against the step's own cost");
            });

            Case("LadderClimb_every_climbable_ladder_has_its_span", () =>
            {
                foreach (var (file, defName) in new[] { ("FlowWorks_ThingDefs.xml", "RM_Ladder"), ("FlowWorks_ThingDefs.xml", "RM_LadderSteel"), ("FlowWorks_PitAccess.xml", "RM_LadderPortable") })
                {
                    string xml = File.ReadAllText(Path.Combine(Path.GetDirectoryName(RiverSwitchFlipChecks.SrcPath("RM_PitDrawMath.cs")), "..", "Defs", "Canals", "ThingDefs", file));
                    int at = xml.IndexOf("<defName>" + defName + "</defName>", StringComparison.Ordinal);
                    Assert(at > 0, defName + " found");
                    int end = xml.IndexOf("</ThingDef>", at, StringComparison.Ordinal);
                    string def = xml.Substring(at, end - at);
                    foreach (string f in new[] { "North", "East", "South", "West" })
                    {
                        Match m = Regex.Match(def, "<climbSpan" + f + @">([0-9.]+)~([0-9.]+)</climbSpan" + f + ">");
                        Assert(m.Success, defName + " climbSpan" + f);
                        float lo = float.Parse(m.Groups[1].Value, System.Globalization.CultureInfo.InvariantCulture), hi = float.Parse(m.Groups[2].Value, System.Globalization.CultureInfo.InvariantCulture);
                        Assert(lo >= 0f && hi <= 1f && hi > lo && hi - lo < 1f, defName + " " + f + " a real sub-span: " + lo + "~" + hi);
                    }
                }
            });
        }
    }
}
