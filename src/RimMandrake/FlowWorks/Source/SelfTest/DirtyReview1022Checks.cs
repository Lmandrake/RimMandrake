// FlowWorks DIRTY-file review 2026-10-22 (second pass): offline guards for the behaviour fixes. Each case reads the
// PRODUCTION source (whitespace collapsed, RiverSwitchFlipChecks.Src) and requires the fixed shape, so a revert fails here.
// NOT proven here: anything a live map decides (rain actually falling on a roofed pit). Those stay live checks.
using System;
using System.IO;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class DirtyReview1022Checks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string Src(params string[] rel) => RiverSwitchFlipChecks.Src(Path.Combine(rel));

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
            Case("Rain_roofed_brimming_square_spills_nothing", () =>
            {
                // A roofed square already full used to reach the brimming branch first and spill rain over its lip.
                string body = Between(Src("RM_MapComponent_Excavation.cs"), "private void ApplyRain()", "// ── rendering F");
                int roof = At(body, "map.roofGrid.Roofed(c)");
                int brim = At(body, "if (room <= 0)");
                Assert(roof < brim, "the roof check precedes the brimming-square spill");
                Assert(body.IndexOf("RainOverflow", StringComparison.Ordinal) > roof, "every RainOverflow call sits after the roof check");
                // the partial-room spill comes after the P7 palette refusal, so a dry square that stays dry spills nothing either
                Assert(At(body, "TryPaletteKey(fluid, out rainKey)") < body.LastIndexOf("RainOverflow", StringComparison.Ordinal),
                    "the partial spill follows the palette-key refusal");
            });

            Case("DugSwim_refresh_reuses_scratch", () =>
            {
                string body = Between(Src("RM_MapComponent_Excavation.cs"), "public int RefreshDugSwim()", "public int HollowDepthAt(");
                Assert(!body.Contains("new Dictionary<int, int>()") && !body.Contains("new List<int>()"),
                    "RefreshDugSwim (every 60 ticks per map) allocates no collections");
                Assert(body.Contains("swimFreshScratch") && body.Contains("swimChangedScratch"), "it reuses the scratch fields");
            });

            Case("SuspensionBridges_band_reset_and_lean_load_tick", () =>
            {
                string src = Src("Pits", "Suspension", "RM_MapComponent_SuspensionBridges.cs");
                // a NEW game after one with band pawns: BandTotal is zeroed at map init, not left stale until the first SetBand
                Assert(Between(src, "public override void FinalizeInit()", "public override void MapRemoved()").Contains("BandForThisGame();"),
                    "FinalizeInit zeroes the band for a new game");
                // a lone band pawn / under-thing with no record left is still swept and pruned
                Assert(src.Contains("(bridges.Count == 0 && floorBand.Count == 0 && underThings.Count == 0)"), "the 60-tick early return keeps the sweep alive");
                string loop = Between(src, "for (int span = 0; span < spanCount; span++)", "private List<Pawn> PawnsOnCells(");
                Assert(!loop.Contains("new List<Pawn>()") && !loop.Contains("r.SpanCount") && !loop.Contains("r.RatingKg"),
                    "the span loop allocates no unread standing list and reads SpanCount / RatingKg once per record");
            });

            Case("SuperdeepTrap_IsHeldAt_builds_no_closure", () =>
            {
                string src = Src("Superdeep", "RM_SuperdeepTrap.cs");
                string body = Between(src, "RM_MapComponent_Excavation eng = EngineOf(p.Map); if (RM_PocketGrid.Relative)", "private static bool WideAt(");
                Assert(!body.Contains("=>"), "IsHeldAt (per path step) holds no lambda capturing a method-scope local");
                Assert(body.Contains("bool wide = WideAt(eng, c, w);"), "the width test goes through WideAt");
            });

            Case("RaiderTrench_plans_on_the_pawns_own_grid", () =>
            {
                string src = Src("Superdeep", "RM_RaiderTrench.cs");
                // RelativeVeto judges reach on ForPawn (stride / floor view); a plan on the plain grid disagreed with it
                Assert(!src.Contains("RM_PocketGrid.For("), "no raider plan reads the plain pocket grid");
                Assert(src.Split(new[] { "RM_PocketGrid.ForPawn(" }, StringSplitOptions.None).Length - 1 >= 4, "TryPlan, OriginFor, JumpJob, LadderJob ask ForPawn");
                Assert(!src.Contains("GetComponent<RM_MapComponent_Excavation>()") || !Between(src, "FillTargetMet", "MakeNewToils").Contains("GetComponent<"),
                    "the per-tick fill end condition uses the cached EngineOf");
            });

            Case("NorthstarProofs_refuse_negative_units_and_unknown_mode_first", () =>
            {
                string src = Src("RM_NorthstarProofs.cs");
                Assert(src.Contains("out int units) || units < 0 ||"), "a negative tank fill is refused, not reported as success");
                int mode = At(src, "return \"REFUSED: unknown mode \" + a[0]; // before the body lookup");
                Assert(mode < At(src, "eng.Stock.IndexedBodyAt(map, at)"), "an unknown mode word is refused before the body lookup");
            });

            Case("Hoses_ghosts_pruned_in_tick_and_no_joiner_array", () =>
            {
                string src = Src("Hose", "RM_MapComponent_Hoses.cs");
                string tick = Between(src, "public override void MapComponentTick()", "Watch(r, now);");
                Assert(tick.Contains("ghosts.RemoveAt(gi)"), "the tick prunes finished ghosts on maps nobody views");
                Assert(!src.Contains("new[] { d, -d }"), "the per-frame joiner loop allocates no array per joint");
                // a settled hose's cache hit reuses its pose: the key is built before Pose, and Pose runs only on a miss
                string draw = Between(src, "private void DrawAll()", "DrawGhosts(y0);");
                int keyAt = At(draw, "string key = (settled ?");
                int hit = At(draw, "c.key == key) pts = c.pts;");
                Assert(keyAt < hit && hit < At(draw, "pts = HoseMath.Pose(lay,"), "Pose runs only when the cached pose misses");
                Assert(draw.Contains("pts = pts, rp = rp };"), "the cache stores the pose (and its drawn strand) with its meshes");
            });
        }
    }
}
