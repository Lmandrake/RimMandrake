// PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE phase 1 (design/RimMandrake/flowworks_pipes_across_pits_design_2026-10-20.md §P1, §P2):
// offline checks on the production crossing table (RM_LineCrossingMath, compiled in), the shipped line tags (the XML the game
// loads) and the production call sites (RM_LineCrossing.cs, read as text). L1 of the item's verify: the table for every line
// kind x surface, and a style change does not change permission. Each case has a can-fail. NOT proven here: the gates firing in
// a running game (a pipe refused on a rope deck, a cord accepted; a frame cancelled under a new cover): L2 live rows, owed.
using System;
using System.IO;
using System.Linq;
using System.Xml.Linq;
using RimMandrake.FlowWorks.Machinery;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class LineCrossingChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string Src(params string[] rel) => RiverSwitchFlipChecks.Src(Path.Combine(rel));

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

        /// <summary>The FlowWorks mod folder (Source's parent) in the tree under test.</summary>
        private static string ModRoot() => Path.GetDirectoryName(Path.GetDirectoryName(RiverSwitchFlipChecks.SrcPath("RM_SpanMath.cs")));

        private const CrossingVerdict Y = CrossingVerdict.Allowed, N = CrossingVerdict.Refused, R = CrossingVerdict.RampOrLadderOnly;

        // The design's P2 table, typed out here from the ruled text (rows: surface; columns: pipe, conduit, cord, hose).
        private static readonly (LineSurface s, CrossingVerdict[] v)[] Table =
        {
            (LineSurface.SolidGround,    new[] { Y, Y, Y, Y }),
            (LineSurface.Excavated,      new[] { N, N, N, R }),
            (LineSurface.Cover,          new[] { N, N, N, N }),
            (LineSurface.Deck,           new[] { N, N, Y, Y }),
            (LineSurface.RopeDeck,       new[] { N, N, Y, Y }),
            (LineSurface.DrawbridgeLeaf, new[] { N, N, Y, Y }),
        };

        private static readonly LineKind[] Kinds = { LineKind.RigidPipe, LineKind.RigidConduit, LineKind.FlexCord, LineKind.Hose };

        public static void Run(Action<string, Action> Case)
        {
            Case("LineCrossing_P2_table_every_kind_by_every_surface", () =>
            {
                Assert(Enum.GetValues(typeof(LineKind)).Length == RM_LineCrossingMath.KindCount && Kinds.Length == RM_LineCrossingMath.KindCount,
                    "four line kinds");
                Assert(Enum.GetValues(typeof(LineSurface)).Length == RM_LineCrossingMath.SurfaceCount && Table.Length == RM_LineCrossingMath.SurfaceCount,
                    "can-fail: a new surface must get a row in this table");
                int cells = 0;
                foreach (var row in Table)
                {
                    for (int k = 0; k < Kinds.Length; k++)
                    {
                        CrossingVerdict got = RM_LineCrossingMath.Verdict(Kinds[k], row.s);
                        Assert(got == row.v[k], Kinds[k] + " on " + row.s + ": expected " + row.v[k] + ", got " + got);
                        cells++;
                    }
                }
                Assert(cells == 24, "24 cells checked");
            });

            Case("LineCrossing_P2_rigid_only_on_solid_ground_cover_carries_nothing", () =>
            {
                foreach (LineSurface s in Enum.GetValues(typeof(LineSurface)))
                {
                    bool solid = s == LineSurface.SolidGround;
                    Assert(RM_LineCrossingMath.MayBuild(LineKind.RigidPipe, s) == solid, "pipe on " + s);
                    Assert(RM_LineCrossingMath.MayBuild(LineKind.RigidConduit, s) == solid, "can-fail: conduit on " + s + " (answer 1: can't build there)");
                }
                foreach (LineKind k in Kinds)
                {
                    Assert(RM_LineCrossingMath.Verdict(k, LineSurface.Cover) == CrossingVerdict.Refused, "answer 3: a cover carries no " + k);
                }
                Assert(RM_LineCrossingMath.MayBuild(LineKind.FlexCord, LineSurface.RopeDeck) && RM_LineCrossingMath.MayBuild(LineKind.Hose, LineSurface.RopeDeck),
                    "answer 4: cords and hoses on a rope deck");
                Assert(!RM_LineCrossingMath.MayBuild(LineKind.Hose, LineSurface.Excavated), "a hose into a pit is the router's ramp/ladder rule, never a built line");
                Assert(!RM_LineCrossingMath.MayBuild(LineKind.FlexCord, LineSurface.Excavated), "can-fail: a cord never lies in a dug square");
                Assert(RM_LineCrossingMath.IsFlexible(LineKind.FlexCord) && RM_LineCrossingMath.IsFlexible(LineKind.Hose)
                    && !RM_LineCrossingMath.IsFlexible(LineKind.RigidPipe) && !RM_LineCrossingMath.IsFlexible(LineKind.RigidConduit), "flexibility");
            });

            Case("LineCrossing_P2_surface_deck_wins_over_the_hole_under_it", () =>
            {
                Assert(RM_LineCrossingMath.Classify(false, DeckOnSquare.None) == LineSurface.SolidGround, "bare ground");
                Assert(RM_LineCrossingMath.Classify(true, DeckOnSquare.None) == LineSurface.Excavated, "a dug square (a raised leaf reads None: the hole is whole)");
                Assert(RM_LineCrossingMath.Classify(true, DeckOnSquare.Cover) == LineSurface.Cover, "can-fail: a cover over a pit is a cover");
                Assert(RM_LineCrossingMath.Classify(true, DeckOnSquare.RopeDeck) == LineSurface.RopeDeck, "a rope deck over a pit");
                Assert(RM_LineCrossingMath.Classify(false, DeckOnSquare.Deck) == LineSurface.Deck, "a deck over natural water is a deck");
                Assert(RM_LineCrossingMath.Classify(true, DeckOnSquare.DrawbridgeLeaf) == LineSurface.DrawbridgeLeaf, "a lowered leaf");
            });

            Case("LineCrossing_P2_every_refusal_has_a_reason_every_allow_none", () =>
            {
                foreach (LineKind k in Kinds)
                {
                    foreach (LineSurface s in Enum.GetValues(typeof(LineSurface)))
                    {
                        string why = RM_LineCrossingMath.RefusalReason(k, s);
                        bool allowed = RM_LineCrossingMath.Verdict(k, s) == CrossingVerdict.Allowed;
                        Assert(allowed == (why == null), k + " on " + s + ": reason " + (why ?? "null"));
                    }
                }
                Assert(RM_LineCrossingMath.RefusalReason(LineKind.RigidPipe, LineSurface.Excavated).Contains("poles"), "the refusal names the way across");
            });

            Case("LineCrossing_P1_style_change_does_not_change_permission", () =>
            {
                // the permission's inputs are the def's tag and the square: no style anywhere in the table or the tag read
                string math = Src("Machinery", "RM_LineCrossingMath.cs");
                string verdict = Body(math, "public static CrossingVerdict Verdict(LineKind k, LineSurface s)");
                Assert(!verdict.Contains("Style") && !verdict.Contains("isPowerConduit"), "can-fail: the table takes a kind and a surface only");
                string live = Src("Machinery", "RM_LineCrossing.cs");
                string kindOf = Body(live, "public static LineKind? KindOf(BuildableDef def)");
                Assert(kindOf.Contains("GetModExtension<RM_LineKindExtension>()"), "KindOf reads the def's tag");
                Assert(!kindOf.Contains("Style") && !kindOf.Contains("isPowerConduit") && !kindOf.Contains("graphic"),
                    "can-fail: KindOf never reads the style, the look or isPowerConduit (review answer 5)");
                // the shipped tags: on the defs, never on a ThingStyleDef
                string root = ModRoot();
                XDocument patch = XDocument.Load(Path.Combine(root, "Patches", "Machinery", "RM_LineKinds.xml"));
                var op = patch.Root.Elements("Operation").Single(e => (string)e.Attribute("Class") == "PatchOperationAddModExtension");
                Assert((string)op.Element("xpath") == "Defs/ThingDef[defName=\"PowerConduit\"]", "the conduit tag is on the PowerConduit THINGDEF (its children inherit it)");
                Assert(op.Descendants("kind").Single().Value == "RigidConduit", "conduit is rigid");
                XDocument logistics = XDocument.Load(Path.Combine(root, "Defs", "Machinery", "RM_LiquidLogistics.xml"));
                var pipe = logistics.Root.Elements("ThingDef").Single(e => (string)e.Element("defName") == "RM_UniversalPipe");
                var tag = pipe.Element("modExtensions").Elements("li").Single(e => (string)e.Attribute("Class") == "RimMandrake.FlowWorks.Machinery.RM_LineKindExtension");
                Assert(tag.Element("kind").Value == "RigidPipe", "RM_UniversalPipe is rigid pipe");
                // no look carries a tag: GSS's conduit styles and the pipe's four looks
                string[] styleFiles =
                {
                    Path.Combine(root, "..", "GimmeSomeSlack", "Defs", "Aerial", "RM_ConduitStyles.xml"),
                    Path.Combine(root, "Defs", "Machinery", "RM_UniversalPipeStyles.xml"),
                };
                foreach (string f in styleFiles)
                {
                    Assert(File.Exists(f), "style file present: " + f);
                    string x = File.ReadAllText(f);
                    Assert(x.Contains("ThingStyleDef"), "can-fail: " + f + " holds styles");
                    Assert(!x.Contains("RM_LineKindExtension") && !x.Contains("LineKind"), "a style never carries a line kind: " + f);
                }
            });

            Case("LineCrossing_P2_gates_at_placement_rebuild_and_frame_completion", () =>
            {
                string live = Src("Machinery", "RM_LineCrossing.cs");
                string terrain = Body(live, "public static class RM_Patch_LineCrossingTerrain");
                Assert(live.Contains("[HarmonyPatch(typeof(GenConstruct), nameof(GenConstruct.CanBuildOnTerrain))]") && terrain.Contains("[HarmonyPriority(Priority.Last)]"),
                    "terrain gate, Last (after the deck affordance patch lends Light to a timber deck)");
                Assert(terrain.Contains("__result = false") && terrain.Contains("FlexOnDeck"), "rigid refused; the flexible deck exception granted");
                string place = Body(live, "public static class RM_Patch_LineCrossingPlacement");
                Assert(live.Contains("nameof(GenConstruct.CanPlaceBlueprintAt_NewTemp)") && place.Contains("new AcceptanceReport(why)"),
                    "placement and auto-rebuild (CheckAutoRebuildOnDestroyed calls CanPlaceBlueprintAt) carry the reason");
                string frame = Body(live, "public static class RM_Patch_LineCrossingFrame");
                Assert(live.Contains("[HarmonyPatch(typeof(Frame), nameof(Frame.CompleteConstruction))]") && frame.Contains("Destroy(DestroyMode.Cancel)")
                    && frame.Contains("return false"), "can-fail: a refused frame is cancelled (refunded) at completion, never built");
                string refusal = Body(live, "public static string Refusal(BuildableDef def, IntVec3 center, Rot4 rot, Map map)");
                Assert(refusal.Contains("RM_MachinerySettings.lineCrossingRulesEnabled") && Body(live, "public static bool FlexOnDeck(").Contains("RM_MachinerySettings.lineCrossingRulesEnabled"),
                    "the Mod Settings switch gates both rules");
                string surf = Body(live, "private static DeckOnSquare DeckOn(Map map, IntVec3 c)");
                Assert(surf.Contains("RM_SpanUtility.DeckAt") && surf.Contains("Building_PitCover") && surf.Contains("SuspensionTier.Rope") && surf.Contains("RM_Drawbridges.LeafOf"),
                    "surfaces read off the span base: covers, rope decks, leaves (a raised leaf is not Decked)");
                string set = Src("Machinery", "RM_MachinerySettings.cs");
                Assert(set.Contains("public static bool lineCrossingRulesEnabled = true;") && set.Contains("Scribe_Values.Look(ref lineCrossingRulesEnabled, \"lineCrossingRulesEnabled\", true);")
                    && set.Contains("ref lineCrossingRulesEnabled,"), "switch: default on, scribed, drawn");
                string csproj = Src("RimMandrake_FlowWorks.csproj");
                Assert(csproj.Contains("Machinery\\RM_LineCrossing.cs") && csproj.Contains("Machinery\\RM_LineCrossingMath.cs"), "can-fail: both files are in the mod build");
            });
        }
    }
}
