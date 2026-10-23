// PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE phase 4 (design/RimMandrake/flowworks_pipes_across_pits_design_2026-10-20.md §P3, §P4;
// widths: design/RimMandrake/flowworks_line_widths_2026-10-20.md): offline checks on the pipe pole. Compiled in: the production
// crossing table (RM_LineCrossingMath), dig selector (RM_LineDigBreakMath) and pole numbers (RM_PipePoleMath). Read as text: the
// def XML the game loads, the production call sites, and Gimme Some Slack's span code (its AerialMath drags in half of GSS Core, so
// it is not compiled here; GSS's own SelfTest runs CanLink / SpanCurve on the pipe kind: AerialSelfTest.PipeKind). L1 of the item's phase 4: placement refused on deck / cover /
// dug square and allowed on solid ground; the span length cap; sag at the slider extremes; a span is not walkable and not in pawn
// topology. Each case has a can-fail. NOT proven here: a pole built, linked and drawn in a running game (L2 live rows, owed).
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Xml.Linq;
using RimMandrake.FlowWorks.Machinery;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class PipePoleChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string Src(params string[] rel) => RiverSwitchFlipChecks.Src(Path.Combine(rel));

        private static string ModRoot() => Path.GetDirectoryName(Path.GetDirectoryName(RiverSwitchFlipChecks.SrcPath("RM_SpanMath.cs")));

        private static string GssSrc(params string[] rel)
        {
            string p = Path.Combine(new[] { ModRoot(), "..", "GimmeSomeSlack", "Source" }.Concat(rel).ToArray());
            Assert(File.Exists(p), "GSS source present: " + p);
            return System.Text.RegularExpressions.Regex.Replace(File.ReadAllText(p), @"\s+", " ");
        }

        private static XElement PoleDef()
        {
            XDocument d = XDocument.Load(Path.Combine(ModRoot(), "Defs", "Machinery", "RM_PipePoles.xml"));
            return d.Root.Elements("ThingDef").Single(e => (string)e.Element("defName") == "RM_PipePole");
        }

        /// <summary>A float constant as GSS's AerialMath source writes it ("Name = 12f").</summary>
        private static float GssConst(string src, string name)
        {
            var m = System.Text.RegularExpressions.Regex.Match(src, @"\b" + name + @" = ([0-9.]+)f");
            Assert(m.Success, "GSS constant " + name);
            return float.Parse(m.Groups[1].Value, System.Globalization.CultureInfo.InvariantCulture);
        }

        /// <summary>SpanCurve's height at fraction t (GSS AerialMath: lerp(A, B, t) - sag x |AB| x 4t(1-t)).</summary>
        private static double CurveZ(double len, float sag, double t) => -RM_PipePoleMath.SagDepth(len, sag) * 4 * t * (1 - t);

        public static void Run(Action<string, Action> Case)
        {
            Case("PipePole_P3_support_on_solid_ground_only_refused_on_deck_cover_dug", () =>
            {
                foreach (LineSurface s in Enum.GetValues(typeof(LineSurface)))
                {
                    bool solid = s == LineSurface.SolidGround;
                    Assert(RM_LineCrossingMath.MayBuild(LineKind.PipePole, s) == solid, "can-fail: a pole on " + s + (solid ? " must be allowed" : " must be refused"));
                    string why = RM_LineCrossingMath.RefusalReason(LineKind.PipePole, s);
                    Assert(solid == (why == null), "reason iff refused: " + s);
                    if (!solid) Assert(why.Contains("solid ground"), "the refusal says where a pole may stand: " + why);
                }
                // the named surfaces of the ruling, through the production classifier (a deck or cover over a pit is the deck/cover)
                Assert(!RM_LineCrossingMath.MayBuild(LineKind.PipePole, RM_LineCrossingMath.Classify(true, DeckOnSquare.None)), "a dug square");
                Assert(!RM_LineCrossingMath.MayBuild(LineKind.PipePole, RM_LineCrossingMath.Classify(true, DeckOnSquare.Cover)), "a pit cover");
                Assert(!RM_LineCrossingMath.MayBuild(LineKind.PipePole, RM_LineCrossingMath.Classify(true, DeckOnSquare.RopeDeck)), "a rope deck");
                Assert(!RM_LineCrossingMath.MayBuild(LineKind.PipePole, RM_LineCrossingMath.Classify(false, DeckOnSquare.Deck)), "a timber/steel deck");
                Assert(!RM_LineCrossingMath.MayBuild(LineKind.PipePole, RM_LineCrossingMath.Classify(true, DeckOnSquare.DrawbridgeLeaf)), "a drawbridge leaf");
                Assert(RM_LineCrossingMath.MayBuild(LineKind.PipePole, RM_LineCrossingMath.Classify(false, DeckOnSquare.None)), "bare ground is allowed");
                Assert(!RM_LineCrossingMath.IsFlexible(LineKind.PipePole), "a pole is no flexible line: the deck exception never applies");
                // shipped: the def carries the tag (all three phase-1 gates) AND its own placeworker (always on)
                XElement d = PoleDef();
                Assert((string)d.Attribute("MayRequire") == "mandrake.rm.gimmesomeslack", "can-fail: the pole loads only with GSS (it is a GSS anchor)");
                var tag = d.Element("modExtensions").Elements("li").Single(e => (string)e.Attribute("Class") == "RimMandrake.FlowWorks.Machinery.RM_LineKindExtension");
                Assert(tag.Element("kind").Value == "PipePole", "the pole is tagged PipePole");
                var pws = d.Element("placeWorkers").Elements("li").Select(e => e.Value).ToList();
                Assert(pws.Contains("RimMandrake.FlowWorks.Machinery.PlaceWorker_PipePole") && pws.Contains("PlaceWorker_NotUnderRoof"), "placeworkers: ground rule and open sky");
                string live = Src("Machinery", "RM_PipePoles.cs");
                int allowsAt = live.IndexOf("public override AcceptanceReport AllowsPlacing", StringComparison.Ordinal);
                Assert(allowsAt >= 0, "PlaceWorker_PipePole.AllowsPlacing present");
                string allows = live.Substring(allowsAt);
                int allowsEnd = allows.IndexOf("return AcceptanceReport.WasAccepted; } }", StringComparison.Ordinal);
                Assert(allowsEnd > 0, "AllowsPlacing's end found (an empty body would make the switch check vacuous)");
                Assert(allows.Contains("RM_LineCrossingMath.RefusalReason(LineKind.PipePole, RM_LineCrossing.SurfaceAt(map, loc))")
                       && !allows.Substring(0, allowsEnd + 1).Contains("lineCrossingRulesEnabled"),
                    "can-fail: the placeworker reads the square's surface and applies the support rule whatever the crossing switch");
            });

            Case("PipePole_P3_span_length_cap_follows_the_slider", () =>
            {
                string math = GssSrc("Aerial", "AerialMath.cs");
                Assert(RM_PipePoleMath.MaxSpanDefault == GssConst(math, "PipeMaxSpanDefault") && RM_PipePoleMath.SagDefault == GssConst(math, "PipeSagDefault"),
                    "can-fail: FlowWorks' defaults and GSS's unregistered fallback agree (12 cells, 2%)");
                Assert(RM_PipePoleMath.MaxSpanMin >= GssConst(math, "PipeSpanMin") && RM_PipePoleMath.MaxSpanMax <= GssConst(math, "PipeSpanMax")
                       && RM_PipePoleMath.SagMax <= GssConst(math, "PipeSagMax"), "the slider range lies inside GSS's sanity bounds (GSS never re-clamps a slider value)");
                foreach (float slider in new[] { RM_PipePoleMath.MaxSpanMin, RM_PipePoleMath.MaxSpanDefault, RM_PipePoleMath.MaxSpanMax })
                {
                    int n = (int)RM_PipePoleMath.ClampSpan(slider);
                    Assert(n == (int)slider, "the slider value is the cap: " + slider);
                    Assert(RM_PipePoleMath.InSpan(n, 0, slider) && !RM_PipePoleMath.InSpan(n + 1, 0, slider), "can-fail: " + n + " in, " + (n + 1) + " out at " + slider);
                    Assert(RM_PipePoleMath.InSpan(0, -n, slider) && !RM_PipePoleMath.InSpan(n, 1, slider), "euclidean, any direction");
                }
                Assert(RM_PipePoleMath.InSpan(6, 8, 10f) && !RM_PipePoleMath.InSpan(6, 9, 10f), "(6,8)=10 in, (6,9) out");
                Assert(RM_PipePoleMath.ClampSpan(500f) == RM_PipePoleMath.MaxSpanMax && RM_PipePoleMath.ClampSpan(-3f) == RM_PipePoleMath.MaxSpanMin
                       && RM_PipePoleMath.ClampSpan(float.NaN) == RM_PipePoleMath.MaxSpanMin && RM_PipePoleMath.ClampSpan(12.4f) == 12f,
                    "a hand-edited settings file cannot exceed the slider; whole cells");
                // the chain the game runs: GSS's link verdict uses the anchor's per-kind range, which for a pipe pole is the
                // FlowWorks getter (RM_PipePoles.MaxSpan = ClampSpan(setting)); GSS refuses mixed kinds before range
                Assert(math.Contains("if (a.Kind != b.Kind) return LinkVerdict.WrongKind;") && math.Contains("if (!InRange(a.X, a.Z, b.X, b.Z, range)) return LinkVerdict.OutOfRange;"),
                    "GSS CanLink: kind, then range");
                string comp = GssSrc("Aerial", "CompAerialAnchor.cs");
                Assert(comp.Contains("return AerialMath.CanLink(a.Info(), bi, a.Range);") && comp.Contains("public float Range => AerialLineProfiles.RangeFor(Kind);"),
                    "can-fail: the link verdict uses the anchor's own kind's range, not the wire's");
                string prof = GssSrc("Aerial", "AerialLineProfiles.cs");
                Assert(prof.Contains("AerialKinds.RangeFor(k, AerialSettings.maxSpan, k == AerialLineKind.Pipe ? PipeMaxSpanRaw : 0f)")
                       && prof.Contains("Read(pipeMaxSpan, AerialKinds.PipeMaxSpanDefault)"), "the pipe range is the registered getter, else the default");
                Assert(Src("Machinery", "RM_PipePoles.cs").Contains("public static float MaxSpan() => RM_PipePoleMath.ClampSpan(RM_MachinerySettings.pipePoleMaxSpan);"),
                    "the getter FlowWorks registers is the clamped slider");
            });

            Case("PipePole_P3_sag_at_the_slider_extremes", () =>
            {
                foreach (double len in new[] { 4.0, 12.0, 20.0 })
                {
                    Assert(RM_PipePoleMath.SagDepth(len, RM_PipePoleMath.SagMin) == 0 && CurveZ(len, RM_PipePoleMath.SagMin, 0.5) == 0, "can-fail: sag 0 is a straight pipe over " + len);
                    double deep = RM_PipePoleMath.SagDepth(len, RM_PipePoleMath.SagMax);
                    Assert(Math.Abs(deep - len * 0.06) < 1e-6, "sag 6% over " + len + " hangs " + deep);
                    Assert(CurveZ(len, RM_PipePoleMath.SagMax, 0) == 0 && CurveZ(len, RM_PipePoleMath.SagMax, 1) == 0, "the ends stay on the clamps at any sag");
                    Assert(Math.Abs(CurveZ(len, RM_PipePoleMath.SagMax, 0.5) + deep) < 1e-9, "deepest at mid-span");
                }
                Assert(Math.Abs(RM_PipePoleMath.SagDepth(12, RM_PipePoleMath.SagDefault) - 0.24) < 1e-6, "default: a 12-cell span hangs 0.24 cells");
                Assert(RM_PipePoleMath.SagDefault <= 0.06f / 3f + 1e-6f, "owner's widths card: about a third of the wire's 6%");
                Assert(RM_PipePoleMath.ClampSag(0.5f) == RM_PipePoleMath.SagMax && RM_PipePoleMath.ClampSag(-1f) == 0f && RM_PipePoleMath.ClampSag(float.NaN) == 0f, "sag clamped to the slider");
                string math = GssSrc("Aerial", "AerialMath.cs");
                Assert(math.Contains("p.Z -= sag * 4 * t * (1 - t);") && math.Contains("double sag = Math.Max(0, sagFactor) * len;"), "GSS's curve is the formula above");
                string mesh = GssSrc("Aerial", "RM_MapComponent_Aerial.cs");
                Assert(mesh.Contains("float sagK = AerialLineProfiles.SagFor(kind);") && mesh.Contains("AerialMath.SpanCurve(s.A, s.B, sagK * s.SagMul)")
                       && mesh.Contains("AerialKinds.StrandCap(kind, AerialSettings.maxStrands)") && mesh.Contains("AerialKinds.Drips(kind, AerialSettings.dripLoops)"),
                    "can-fail: the span mesh takes the pipe kind's sag, one strand, no drip loop");
                Assert(Src("Machinery", "RM_PipePoles.cs").Contains("public static float Sag() => RM_PipePoleMath.ClampSag(RM_MachinerySettings.pipePoleSag);"), "the sag getter is the clamped slider");
                // shipped width: the pipe's 30 cm, never the wire's
                XElement ext = PoleDef().Element("modExtensions").Elements("li").Single(e => (string)e.Attribute("Class") == "RimMandrake.GimmeSomeSlack.Aerial.AerialAnchorExtension");
                Assert(ext.Element("lineKind").Value == "Pipe" && float.Parse(ext.Element("spanWidth").Value, System.Globalization.CultureInfo.InvariantCulture) == RM_PipePoleMath.SpanWidthCells,
                    "the def is a Pipe anchor at the pipe's width");
                Assert(RM_PipePoleMath.SpanWidthCells >= 0.12f && RM_PipePoleMath.SpanWidthCells <= 0.15f, "can-fail: the halved pipe girth, 0.12-0.15 cell (owner 2026-10-21)");
            });

            Case("PipePole_P3_span_is_not_walkable_and_not_in_pawn_topology", () =>
            {
                foreach (LineSurface s in Enum.GetValues(typeof(LineSurface)))
                    Assert(RM_PipePoleMath.SurfaceUnderSpan(s) == s, "a span changes no surface under it: " + s);
                XElement d = PoleDef();
                Assert(d.Element("passability").Value == "PassThroughOnly" && d.Element("comps").Elements("li").All(e => !((string)e.Attribute("Class") ?? "").Contains("Power")),
                    "the pole is an obstacle-ish post with no power comp");
                Assert(!d.ToString().Contains("SpanDeck") && !d.ToString().Contains("Suspension") && (string)d.Element("thingClass") == "Building",
                    "the pole is a plain Building: no deck class, no suspension tie");
                // pawn topology: every reader of decks / walkability / pit pathing names nothing aerial
                string[] readers =
                {
                    Path.Combine("Pits", "Building_SpanDeck.cs"), Path.Combine("Pits", "Suspension", "RM_SuspensionPatches.cs"),
                    Path.Combine("Pits", "Suspension", "RM_MapComponent_SuspensionBridges.cs"), Path.Combine("Superdeep", "RM_PitPathing.cs"),
                    Path.Combine("Superdeep", "RM_PitStepCost.cs"), Path.Combine("Superdeep", "RM_WallClimb.cs"), "RM_ExcavationDepth.cs",
                    Path.Combine("Machinery", "RM_LineCrossing.cs"),
                };
                string[] aerial = { "CompAerialAnchor", "AerialLineProfiles", "AerialAnchorExtension", "RM_PipePole", "SpanLink" };
                foreach (string r in readers)
                {
                    string t = Src(r);
                    Assert(t.Length > 200, "can-fail: read " + r);
                    foreach (string a in aerial) Assert(!t.Contains(a), r + " must not read pipe spans (" + a + ")");
                }
                // the GSS side keeps a span as two link records on the anchor comps, never a Thing on the cells it crosses
                string link = GssSrc("Aerial", "CompAerialAnchor.cs");
                string tryLink = link.Substring(link.IndexOf("public static LinkVerdict TryLink(", StringComparison.Ordinal), 900);
                Assert(tryLink.Contains("a.links.Add(new SpanLink") && !tryLink.Contains("GenSpawn") && !tryLink.Contains("ThingMaker"),
                    "can-fail: linking spawns nothing on the ground");
                string planted = "foo RM_PipePole bar";
                Assert(aerial.Any(a => planted.Contains(a)), "sanity probe: the aerial-name scan can see a planted name");
            });

            Case("PipePole_D5_ground_pipe_reaches_the_pole_and_the_span_is_the_looks_pipe", () =>
            {
                // joints study 2026-10-22 D5: the ground pipe stopped in a cap half a cell short of the pole, and the span drew the
                // look's power wire ("reads as an electric line")
                string j = Src("Machinery", "RM_LiquidJoins.cs");
                Assert(System.Text.RegularExpressions.Regex.IsMatch(j, @"PartnerAt\(c, parent\.Map\) != null\s*\|\| \(RM_MachinerySettings\.pipePolesEnabled && RM_LiquidJoins\.PipePoleAt\(c, parent\.Map\)\)(\s*\|\| RM_LiquidJoins\.ReelCoupledTo\(c, parent\))?\) __result = true;"),
                    "a pipe's atlas links toward a pipe pole beside it");
                Assert(j.Contains("t is Building && t.def.GetModExtension<RM_LineKindExtension>()?.kind == LineKind.PipePole"), "only a BUILT pole (not its blueprint) draws the arm");
                // the PipeSpan.png files: selftest_flowworks_pipe_pole_art.py (this stage copies no Textures)
            });

            Case("PipePole_P4_dig_kills_the_pole_so_its_spans_fall", () =>
            {
                Assert(RM_LineDigBreakMath.KilledOnDig(LineKind.PipePole) && RM_LineDigBreakMath.BreaksOnDig(LineKind.PipePole), "a dug-out pole breaks, killed");
                foreach (LineKind k in new[] { LineKind.RigidPipe, LineKind.RigidConduit, LineKind.FlexCord, LineKind.Hose })
                    Assert(!RM_LineDigBreakMath.KilledOnDig(k), "can-fail: " + k + " keeps its salvage (deconstructed)");
                var onSquare = new List<string> { "pole", "rock" };
                List<string> hit = RM_LineDigBreakMath.ToBreak(true, 0, 1, onSquare, t => t == "pole" ? LineKind.PipePole : (LineKind?)null, t => false);
                Assert(hit.Count == 1 && hit[0] == "pole", "the committed cut selects the pole");
                Assert(RM_LineDigBreakMath.ToBreak(true, 1, 1, onSquare, t => t == "pole" ? LineKind.PipePole : (LineKind?)null, t => false).Count == 0, "no commit, no break");
                string live = Src("Machinery", "RM_LineDigBreak.cs");
                Assert(live.Contains("if (k != null && RM_LineDigBreakMath.KilledOnDig(k.Value)) { t.Destroy(DestroyMode.KillFinalize);")
                       && live.Contains("t.Destroy(DestroyMode.Deconstruct);"), "production: KillFinalize for the pole (GSS drops a killed anchor's spans), Deconstruct for the rest");
                string gssPlan = GssSrc("Aerial", "CompAerialAnchor.cs");
                Assert(gssPlan.Contains("bool killed = mode == DestroyMode.KillFinalize"), "GSS reads KillFinalize as killed (its RemovalPlan drops the survivor's half)");
            });

            Case("PipePole_P3_settings_and_the_gss_seam_line_up", () =>
            {
                string set = Src("Machinery", "RM_MachinerySettings.cs");
                foreach (string f in new[] { "pipePolesEnabled", "pipePoleMaxSpan", "pipePoleSag" })
                    Assert(set.Contains("Scribe_Values.Look(ref " + f + ", \"" + f + "\""), "scribed: " + f);
                Assert(set.Contains("public static bool pipePolesEnabled = true;") && set.Contains("public static float pipePoleMaxSpan = 12f;") && RM_PipePoleMath.MaxSpanDefault == 12f
                       && set.Contains("public static float pipePoleSag = 0.02f;") && RM_PipePoleMath.SagDefault == 0.02f, "defaults = shipped behaviour (literal: the northstar registry parses it)");
                Assert(set.Contains("RM_PipePoleMath.ClampSpan(list.Slider(pipePoleMaxSpan, RM_PipePoleMath.MaxSpanMin, RM_PipePoleMath.MaxSpanMax))")
                       && set.Contains("list.Slider(pipePoleSag, RM_PipePoleMath.SagMin, RM_PipePoleMath.SagMax)"), "both sliders drawn on the shared bounds");
                string fw = Src("Machinery", "RM_PipePoles.cs");
                string gss = GssSrc("Aerial", "AerialLineProfiles.cs");
                Assert(fw.Contains("public const string GssProfiles = \"RimMandrake.GimmeSomeSlack.Aerial.AerialLineProfiles\";")
                       && gss.Contains("namespace RimMandrake.GimmeSomeSlack.Aerial") && gss.Contains("public static class AerialLineProfiles"), "the type FlowWorks looks up exists by that name");
                Assert(fw.Contains("GetMethod(\"RegisterPipeProfile\"") && fw.Contains("new[] { typeof(Func<float>), typeof(Func<float>) }")
                       && gss.Contains("public static void RegisterPipeProfile(Func<float> maxSpan, Func<float> sag)"), "can-fail: RegisterPipeProfile signature matches");
                Assert(fw.Contains("GetMethod(\"RegisterSpansChanged\"") && gss.Contains("public static void RegisterSpansChanged(Action<Map> callback)"), "span-change seam matches");
                // PIPE_POLE_SWITCH_DECIDE_HOSTAGE_TO_WIRES (owner by card 2026-10-21: "Their own switch.")
                Assert(fw.Contains("GetMethod(\"RegisterPipeSwitch\"") && fw.Contains("new[] { typeof(Func<bool>) }") && fw.Contains("new Func<bool>(PolesOn)")
                       && fw.Contains("public static bool PolesOn() => RM_MachinerySettings.pipePolesEnabled;")
                       && gss.Contains("public static void RegisterPipeSwitch(Func<bool> on)"), "can-fail: the pipe poles' own switch is handed to GSS by a matching signature");
                Assert(!set.Contains("needs Gimme Some Slack's overhead lines on"), "the pipe-pole switch no longer claims it needs GSS's power-lines switch");
                Assert(fw.Contains("GetMethod(\"UpSpans\"") && fw.Contains("new[] { typeof(Map), typeof(string) }")
                       && gss.Contains("public static List<KeyValuePair<Thing, Thing>> UpSpans(Map map, string kind)"), "phase-5 UpSpans seam matches");
                string comp = GssSrc("Aerial", "RM_MapComponent_Aerial.cs");
                Assert(comp.Contains("AerialLineProfiles.FireSpansChanged(map);"), "every span change funnels to the seam (Notify_SpansChanged)");
                string power = GssSrc("Aerial", "AerialPowerPatch.cs");
                Assert(power.Contains("!AerialKinds.CarriesPower(a.Kind)"), "can-fail: GSS's power carry skips pipe anchors");
                string csproj = Src("RimMandrake_FlowWorks.csproj");
                Assert(csproj.Contains("Machinery\\RM_PipePoleMath.cs") && csproj.Contains("Machinery\\RM_PipePoles.cs"), "both files in the mod build");
                // the four looks: style defs exist for each pipe look, with stand-in art that exists on disk (no uninstalled path)
                XDocument doc = XDocument.Load(Path.Combine(ModRoot(), "Defs", "Machinery", "RM_PipePoles.xml"));
                foreach (string look in PipeStyles.Looks)
                {
                    XElement st = doc.Root.Elements("ThingStyleDef").SingleOrDefault(e => (string)e.Element("defName") == PipeStyles.StyleDefName("RM_PipePole", look));
                    Assert(st != null && (string)st.Attribute("MayRequire") == "mandrake.rm.gimmesomeslack", "style for " + look);
                    string tex = st.Element("graphicData").Element("texPath").Value;
                    // the stand-in PNG on disk: the winbuild stage copies no Textures folder, so on a stage this half is
                    // selftest_flowworks_pipe_pole_art.py's (WSL, the real tree); here only the path's shape is checked
                    Assert(tex.StartsWith("RimMandrake/GimmeSomeSlack/Aerial/Styles/" + look + "/", StringComparison.Ordinal), "stand-in path for " + look + ": " + tex);
                    string texRoot = Path.Combine(ModRoot(), "..", "GimmeSomeSlack", "Textures");
                    string png = Path.Combine(texRoot, tex.Replace('/', Path.DirectorySeparatorChar) + ".png");
                    Assert(!Directory.Exists(texRoot) || File.Exists(png), "can-fail: the stand-in exists on disk: " + png);
                }
            });
        }
    }
}
