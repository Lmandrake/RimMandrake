// PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE phase 7 (design/RimMandrake/flowworks_pipes_across_pits_design_2026-10-20.md §P8, §P9).
// P9: the inspect lines that tell a deck cord, a pole-supported span, a hose down a ramp or ladder and a leaf-cut segment apart
// (RM_LineReadoutMath, compiled in; the game adapters read as text). P8: a pipe pole on a gravship re-keys instead of running
// support loss: GSS's GS-1 path (CompAerialAnchor PostDeSpawn WillReplace / PostSwapMap, kind-agnostic) keeps a span with
// both poles aboard and coils one to the ground; FlowWorks' liquid net hears both maps through the phase-5 seam and rebuilds
// each once (RM_PipeSpanNetMath, compiled in; GSS and the adapters read as text). NOT proven here: a real launch and landing
// (L2, owed; no ruled policy for a span crossing the ship's edge beyond GSS's coil, design §P8).
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using RimMandrake.FlowWorks.Machinery;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class LineReadoutChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string ModRoot() => Path.GetDirectoryName(Path.GetDirectoryName(RiverSwitchFlipChecks.SrcPath("RM_SpanMath.cs")));

        private static string Flat(string text) => System.Text.RegularExpressions.Regex.Replace(text, @"\s+", " ");

        private static string Src(params string[] rel) => Flat(RiverSwitchFlipChecks.Src(Path.Combine(rel)));

        private static string GssSrc(params string[] rel)
        {
            string p = Path.Combine(new[] { ModRoot(), "..", "GimmeSomeSlack", "Source" }.Concat(rel).ToArray());
            Assert(File.Exists(p), "GSS source present: " + p);
            return Flat(File.ReadAllText(p));
        }

        private static string Body(string src, string signature)
        {
            int a = src.IndexOf(signature, StringComparison.Ordinal);
            Assert(a >= 0, "missing: " + signature);
            int open = src.IndexOf('{', a);
            int depth = 0;
            for (int i = open; i < src.Length; i++)
            {
                if (src[i] == '{') depth++;
                else if (src[i] == '}' && --depth == 0) return src.Substring(a, i - a + 1);
            }
            throw new Exception("unbalanced: " + signature);
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("LineReadout_P9_four_cases_read_apart", () =>
            {
                string deck = RM_LineReadoutMath.CordLine(LineSurface.Deck, false);
                string rope = RM_LineReadoutMath.CordLine(LineSurface.RopeDeck, false);
                string leaf = RM_LineReadoutMath.CordLine(LineSurface.DrawbridgeLeaf, false);
                string cut = RM_LineReadoutMath.CordLine(LineSurface.DrawbridgeLeaf, true);
                string pole = RM_LineReadoutMath.PoleLine(1, true);
                string ramp = RM_LineReadoutMath.HoseLevelLine(1, 0);
                string ladder = RM_LineReadoutMath.HoseLevelLine(0, 1);
                string hoseCut = RM_LineReadoutMath.HoseLeafCut;
                Assert(deck == "Lying on a bridge deck." && rope == "Lying on a rope bridge deck." && leaf == "Lying on a lowered drawbridge leaf.", "deck cord lines: " + deck + " | " + rope + " | " + leaf);
                Assert(cut == RM_LineReadoutMath.CordLeafCut && cut.StartsWith("Disconnected: ", StringComparison.Ordinal) && cut.Contains("rejoins when the leaf is lowered"), "leaf cut line: " + cut);
                Assert(pole == "Holds up a pipe span overhead: it carries the pipe at this pole across.", "pole line: " + pole);
                Assert(ramp == "Runs down a ramp into the dug ground." && ladder == "Hangs down a ladder into the dug ground.", "hose level lines: " + ramp + " | " + ladder);
                Assert(hoseCut.StartsWith("Disconnected: ", StringComparison.Ordinal) && hoseCut.Contains("rejoins when the leaf is lowered"), "hose cut line: " + hoseCut);
                var all = new[] { deck, rope, leaf, cut, pole, ramp, ladder, hoseCut };
                Assert(all.Distinct().Count() == all.Length, "two of the readout cases print the same line");
                Assert(all.All(s => s.EndsWith(".", StringComparison.Ordinal) && char.IsUpper(s[0])), "a readout line is not a sentence");
                // the cord's old cut text is the shared one (PowerCordChecks still reads CutLine)
                Assert(RM_PowerCordMath.CutLine(true) == cut && RM_PowerCordMath.CutLine(false) == null, "RM_PowerCordMath.CutLine drifted from the shared readout");
                // can-fail: nothing to say on solid ground, on a cover (a cord is never there), unstrung, or on one level
                Assert(RM_LineReadoutMath.CordLine(LineSurface.SolidGround, false) == null && RM_LineReadoutMath.DeckLine(LineSurface.Cover) == null
                    && RM_LineReadoutMath.DeckLine(LineSurface.Excavated) == null, "can-fail: a cord on ground or a cover printed a deck line");
                Assert(RM_LineReadoutMath.PoleLine(0, true) == null && RM_LineReadoutMath.HoseLevelLine(0, 0) == null, "can-fail: an unstrung pole or a level hose printed a line");
                // a raised leaf wins over the deck it was (its square reads dug while up)
                Assert(RM_LineReadoutMath.CordLine(LineSurface.Deck, true) == cut, "a cut cord read as lying on a deck");
            });

            Case("LineReadout_P9_counts_and_dry_pole", () =>
            {
                Assert(RM_LineReadoutMath.PoleLine(2, true) == "Holds up 2 pipe spans overhead: it carries the pipe at this pole across.", "two spans: " + RM_LineReadoutMath.PoleLine(2, true));
                string dry = RM_LineReadoutMath.PoleLine(1, false);
                Assert(dry == "Holds up a pipe span overhead, but no pipe reaches this pole: build one under or beside it to carry liquid.", "dry pole: " + dry);
                Assert(RM_LineReadoutMath.HoseLevelLine(2, 0) == "Changes level 2 times, by 2 ramps.", "two ramps: " + RM_LineReadoutMath.HoseLevelLine(2, 0));
                Assert(RM_LineReadoutMath.HoseLevelLine(1, 1) == "Changes level 2 times, by a ramp and a ladder.", "ramp + ladder: " + RM_LineReadoutMath.HoseLevelLine(1, 1));
                Assert(RM_LineReadoutMath.HoseLevelLine(0, 3) == "Changes level 3 times, by 3 ladders.", "three ladders: " + RM_LineReadoutMath.HoseLevelLine(0, 3));
                Assert(RM_LineReadoutMath.HoseLevelLine(-1, -4) == null, "can-fail: negative counts printed a line");
            });

            Case("LineReadout_P9_adapters_print_the_lines", () =>
            {
                string cord = Body(Src("Machinery", "Building_RM_PowerCord.cs"), "public override string GetInspectString(");
                Assert(cord.Contains("RM_LineReadoutMath.CordLine(") && cord.Contains("RM_LineCrossing.SurfaceAt(Map, Position)") && cord.Contains("CutByLeaf"),
                    "the cord's inspect text does not read its surface and the leaf cut");
                string poleComp = Src("Machinery", "CompPipePoleReadout.cs");
                Assert(Body(poleComp, "public override string CompInspectStringExtra(").Contains("RM_LineReadoutMath.PoleLine(StrungSpans(), RM_PipePoles.JoinCells(parent).Count > 0)"),
                    "the pole readout is not the span count + join-cell rule");
                Assert(Body(poleComp, "public int StrungSpans(").Contains("RM_PipePoles.UpSpans(parent.Map)"), "the pole counts spans from something other than the phase-5 seam");
                string poleDef = File.ReadAllText(Path.Combine(ModRoot(), "Defs", "Machinery", "RM_PipePoles.xml"));
                Assert(poleDef.Contains("<li Class=\"RimMandrake.FlowWorks.Machinery.CompProperties_PipePoleReadout\" />"), "the pole def does not carry the readout comp");
                string reel = Src("Hose", "CompHoseReel.cs");
                string lines = Body(reel, "internal string CrossingLines(");
                int cutAt = lines.IndexOf("RM_Drawbridges.HoseCut(this)", StringComparison.Ordinal), levelAt = lines.IndexOf("RM_HoseBands.LevelChanges(", StringComparison.Ordinal);
                Assert(cutAt > 0 && levelAt > cutAt && lines.Contains("RM_LineReadoutMath.HoseLeafCut") && lines.Contains("RM_LineReadoutMath.HoseLevelLine(ramps, ladders)"),
                    "the reel's crossing lines do not put the leaf cut before the level changes");
                Assert(Body(reel, "public override string CompInspectStringExtra(").Contains("CrossingLines() + endLine"), "the laid reel's inspect text omits its crossing lines");
                string bands = Src("Hose", "RM_HoseBands.cs");
                string count = Body(bands, "private static void Count(");
                Assert(count.Contains("RM_PitRamp.Joins(map, a, b, aB, bB)) ramps++") && count.Contains("Linked(map, a, b, aB, bB)) ladders++"),
                    "a level change is not judged ramp-then-ladder by the router's own link rule");
                Assert(Body(bands, "internal static void LevelChanges(").Contains("/ 0.05"), "LevelChanges reads only the lay's vertices (a polyline skips cells)");
            });

            Case("PipePoleGravship_P8_aboard_span_rekeys_on_landing", () =>
            {
                // GSS GS-1, any anchor kind: the despawn inside GenerateGravship is WillReplace; the aboard set is every anchor in
                // the ship's things; a span to an aboard partner is KEPT; PostSwapMap re-seeds and fires the span-change seam
                string anchor = GssSrc("Aerial", "CompAerialAnchor.cs");
                string despawn = Body(anchor, "public override void PostDeSpawn(");
                Assert(despawn.Contains("mode == DestroyMode.WillReplace ? GravshipAboardIds() : null") && despawn.Contains("AerialMath.PlanRemoval(thingIDNumber, killed, spans, aboard)")
                    && !despawn.Contains("AerialLineKind"), "the gravship despawn path is not kind-agnostic (pipe spans would not be kept)");
                Assert(Body(anchor, "private static HashSet<int> GravshipAboardIds(").Contains("g.Things.Where(t => Of(t) != null)"), "the aboard set skips some anchor kinds");
                string swap = Body(anchor, "public override void PostSwapMap(");
                Assert(swap.Contains("comp?.Notify_SpansChanged()") && !swap.Contains("AerialLineKind"), "landing does not fire the span-change seam for every kind");
                Assert(Body(GssSrc("Aerial", "RM_MapComponent_Aerial.cs"), "public void Notify_SpansChanged(").Contains("AerialLineProfiles.FireSpansChanged(map)"),
                    "the span-change seam does not carry the map");
                string poles = Src("Machinery", "RM_PipePoles.cs");
                Assert(poles.Contains("new Action<Map>(OnSpansChanged)") && Body(poles, "internal static void OnSpansChanged(").Contains("RM_LiquidNet.Bump(map)"),
                    "FlowWorks does not rebuild the net of the map the seam names");
                // the net, per map: a span A-B (both aboard) leaves the launch map (one rebuild) and arrives on the landing map
                // (its first callback always rebuilds); a second callback with the same set rebuilds nothing
                var span = new[] { new KeyValuePair<long, long>(11, 12) };
                ulong oldLast = 0, newLast = 0;
                bool oldKnown = false, newKnown = false;
                Assert(RM_PipeSpanNetMath.Changed(ref oldLast, ref oldKnown, RM_PipeSpanNetMath.Signature(span)), "seed");
                Assert(RM_PipeSpanNetMath.Changed(ref oldLast, ref oldKnown, RM_PipeSpanNetMath.Signature(new KeyValuePair<long, long>[0])), "the launch map kept the flown span's edge");
                Assert(RM_PipeSpanNetMath.Changed(ref newLast, ref newKnown, RM_PipeSpanNetMath.Signature(span)), "the landing map did not rebuild for the arrived span");
                Assert(!RM_PipeSpanNetMath.Changed(ref newLast, ref newKnown, RM_PipeSpanNetMath.Signature(span)), "can-fail: the second pole's landing callback rebuilt again");
                // the arrived span joins its two poles' join cells on the landing map: one logical edge
                object poleA = "A", poleB = "B";
                RM_PipeSpanEdges e = RM_PipeSpanEdges.Build(new[] { new KeyValuePair<object, object>(poleA, poleB) },
                    p => p == poleA ? new List<object> { "a0" } : new List<object> { "b0" }, (x, y) => false);
                Assert(e.AerialEdges == 1 && e.Joins("a0", "b0"), "the landed span did not join its join cells");
            });

            Case("PipePoleGravship_P8_edge_span_coils_and_no_support_loss", () =>
            {
                // a span to a pole left on the ground: GROUNDED (coiled, nothing falls: nothing died); only a KILLED pole drops spans
                string plan = Body(GssSrc("Aerial", "AerialMath.cs"), "public static RemovalPlan PlanRemoval(int id, bool killed, IList<(int, SpanState)> spans, ICollection<int> aboard)");
                Assert(plan.Contains("if (aboard != null && !killed)") && plan.Contains("plan.Grounded.Add(partner)") && plan.Contains("if (killed && st == SpanState.Up) plan.Fallen.Add("),
                    "a span crossing the ship's edge does not come down coiled (or a lift drops it as a fall)");
                // FlowWorks' own support loss (a dig kills a pole; a deck collapse drops cords) never runs on a despawn: only at the
                // Deepen commit and ClearDeckTop, neither of which a launch calls on the ship's things
                string dig = Src("Machinery", "RM_LineDigBreak.cs");
                Assert(!dig.Contains("DeSpawn") && !dig.Contains("WillReplace"), "the dig break hooks a despawn (a launch would run it)");
                string exc = Src("RM_MapComponent_Excavation.cs");
                Assert(exc.Contains("RM_LineDigBreak.OnDigCommitted("), "the dig break is not called from the Deepen commit");
                string cover = Body(Src("Pits", "Building_PitCover.cs"), "public override void DeSpawn(");
                Assert(cover.Contains("mode == DestroyMode.KillFinalize || mode == DestroyMode.KillFinalizeLeavingsOnly || mode == DestroyMode.Deconstruct") && !cover.Contains("WillReplace"),
                    "a cover lifted by a gravship drops its riders");
                // no utility edge joins two maps: GSS lists only same-map partners, refuses a cross-map link, and FlowWorks asks per map
                Assert(Body(GssSrc("Aerial", "AerialLineProfiles.cs"), "public static List<KeyValuePair<Thing, Thing>> UpSpans(").Contains("l.other.Map != map"),
                    "UpSpans lists a span whose far pole is on another map");
                Assert(GssSrc("Aerial", "CompAerialAnchor.cs").Contains("if (a.Map != b.Map) return LinkVerdict.Gone;"), "a span may be strung between two maps");
                Assert(Body(Src("Machinery", "RM_PipePoles.cs"), "public static RM_PipeSpanEdges EdgesFor(").Contains("UpSpans(map)"), "the net reads spans of another map");
            });
        }
    }
}
