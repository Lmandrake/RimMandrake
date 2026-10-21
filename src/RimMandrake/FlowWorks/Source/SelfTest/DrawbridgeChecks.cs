// DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS (design/RimMandrake/flowworks_drawbridge_design_2026-10-20.md §Ruled design): offline
// checks on the production leaf rules (RM_DrawbridgeMath) and the production call sites (RM_Drawbridges, the span base, the
// pocket grid). Phase 1 (core): leaves by material, tip-first raise state, per-leaf saved record, a forced pocket rebuild and
// repath on every toggle, and no Collapse on a raise. Each case has a can-fail. NOT proven here: a colonist re-routing at
// once in a live game (RAISE_PATH), a save made mid-raise reloading (SAVE_MIDRAISE): live rows, owed.
using System;
using System.Collections.Generic;
using System.IO;
using RimMandrake.FlowWorks;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class DrawbridgeChecks
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

        public static void Run(Action<string, Action> Case)
        {
            Case("Drawbridge_P1_materials_timber_and_steel_only", () =>
            {
                Assert(RM_DrawbridgeMath.IsDrawbridgeTier(SuspensionTier.Timber) && RM_DrawbridgeMath.IsDrawbridgeTier(SuspensionTier.Steel),
                    "timber and steel are drawbridges");
                Assert(!RM_DrawbridgeMath.IsDrawbridgeTier(SuspensionTier.Rope) && !RM_DrawbridgeMath.IsDrawbridgeTier(SuspensionTier.Heavy),
                    "can-fail: rope and heavy are not (answer 8)");
                Assert(RM_DrawbridgeMath.DefaultMaxLeaf(SuspensionTier.Timber) == 4 && RM_DrawbridgeMath.DefaultMaxLeaf(SuspensionTier.Steel) == 8
                    && RM_DrawbridgeMath.DefaultMaxLeaf(SuspensionTier.Rope) == 0, "leaf length by material: timber 4, steel 8");
                Assert(!RM_DrawbridgeMath.IsPowered(SuspensionTier.Timber) && RM_DrawbridgeMath.IsPowered(SuspensionTier.Steel),
                    "timber is hand-winched, steel powered");
            });

            Case("Drawbridge_P1_split_one_leaf_or_two_each_hinged_on_its_own_bank", () =>
            {
                List<LeafSpan> one = RM_DrawbridgeMath.SplitLeaves(1, 4, 4, true);
                Assert(one != null && one.Count == 1 && one[0].First == 1 && one[0].Last == 4 && one[0].HingeAtFirst, "4 squares of timber: one leaf on bank A");
                List<LeafSpan> two = RM_DrawbridgeMath.SplitLeaves(1, 7, 4, true);
                Assert(two != null && two.Count == 2, "7 squares of timber: two leaves");
                Assert(two[0].First == 1 && two[0].Last == 4 && two[0].HingeAtFirst, "the colony leaf takes the odd square, hinged on A");
                Assert(two[1].First == 5 && two[1].Last == 7 && !two[1].HingeAtFirst, "can-fail: the far leaf hinges on the FAR bank (review answer 2)");
                List<LeafSpan> rev = RM_DrawbridgeMath.SplitLeaves(1, 7, 4, false);
                Assert(rev[0].First == 4 && rev[0].Last == 7 && !rev[0].HingeAtFirst && rev[1].First == 1 && rev[1].Last == 3 && rev[1].HingeAtFirst,
                    "colony on bank B: mirror");
                Assert(RM_DrawbridgeMath.SplitLeaves(1, 9, 4, true) == null, "can-fail: 9 squares is longer than two timber leaves");
                Assert(RM_DrawbridgeMath.SplitLeaves(1, 16, 8, true).Count == 2 && RM_DrawbridgeMath.SplitLeaves(1, 17, 8, true) == null, "steel: up to 16");
                Assert(RM_DrawbridgeMath.SplitLeaves(1, 4, 0, true) == null, "no leaf length: not a drawbridge");
            });

            Case("Drawbridge_P1_raise_lifts_the_tip_first_and_is_reversible", () =>
            {
                LeafSpan a = new LeafSpan(1, 4, true);   // hinge beside index 1, tip at 4
                int full = RM_DrawbridgeMath.FullTicks(SuspensionTier.Timber, 4, 1f);
                Assert(full == 4 * RM_DrawbridgeMath.HandTicksPerSquare, "timber: about 4 s per square");
                Assert(RM_DrawbridgeMath.FullTicks(SuspensionTier.Steel, 8, 1f) == RM_DrawbridgeMath.PoweredTicksPerLeaf, "steel: about 2 s per leaf");
                Assert(!RM_DrawbridgeMath.IsRaised(a, 4, 0, full), "lowered: nothing raised");
                Assert(RM_DrawbridgeMath.IsRaised(a, 4, 1, full) && !RM_DrawbridgeMath.IsRaised(a, 3, 1, full),
                    "can-fail: one tick in, the TIP has left the far bank and only the tip");
                Assert(RM_DrawbridgeMath.RaisedSquares(full / 4, full, 4) == 1 && RM_DrawbridgeMath.RaisedSquares(full / 4 + 1, full, 4) == 2,
                    "squares rise one per quarter of the travel");
                for (int i = 1; i <= 4; i++) Assert(RM_DrawbridgeMath.IsRaised(a, i, full, full), "raised: every square up");
                Assert(!RM_DrawbridgeMath.IsRaised(a, 5, full, full) && !RM_DrawbridgeMath.IsRaised(a, 0, full, full), "only the leaf's own squares");
                LeafSpan b = new LeafSpan(5, 7, false);  // hinge beside 7 (the far bank), tip at 5
                Assert(RM_DrawbridgeMath.IsRaised(b, 5, 1, 300) && !RM_DrawbridgeMath.IsRaised(b, 7, 1, 300), "a far-bank leaf lifts ITS tip (index 5) first");
                int p = RM_DrawbridgeMath.Step(0, true, full, 5);
                Assert(p == 5 && RM_DrawbridgeMath.Step(full - 2, true, full, 5) == full && RM_DrawbridgeMath.Step(3, false, full, 5) == 0, "steps clamp");
                Assert(RM_DrawbridgeMath.AtTarget(0, false, full) && !RM_DrawbridgeMath.AtTarget(0, true, full), "at target");
                Assert(RM_DrawbridgeMath.StateLine(0, false, full, false) == "lowered" && RM_DrawbridgeMath.StateLine(full, true, full, false) == "raised"
                    && RM_DrawbridgeMath.StateLine(full / 2, true, full, true) == "raising 50% (stopped)", "readout");
            });

            Case("Drawbridge_P1_decked_reads_raised_and_only_drawbridge_decks_raise", () =>
            {
                string b = Src("Pits", "Building_SpanDeck.cs");
                Assert(b.Contains("public bool Decked => !collapsed && Spawned && !Raised;"), "can-fail: a raised square is not ground (R13.2)");
                Assert(b.Contains("public virtual bool Raised => false;"), "the base never raises");
                string d = Src("Pits", "Suspension", "Building_SuspensionDeck.cs");
                Assert(d.Contains("public override bool Raised => leafRaised;"), "a suspension deck reads its leaf");
                Assert(d.Contains("leafRaised = RM_Drawbridges.RaisedAt(map, Position);"), "a reload reads the leaf record on spawn");
                Assert(!d.Contains("Scribe_Values.Look(ref leafRaised"), "the deck never saves its own raised flag (one saved state: the leaf)");
                string print = Body(d, "public override void Print(SectionLayer layer)");
                Assert(print.IndexOf("if (leafRaised)") >= 0 && print.IndexOf("if (leafRaised)") < print.IndexOf("RM_SuspensionDeckLink.Print"),
                    "a raised square draws empty (R12)");
            });

            Case("Drawbridge_P1_structure_reads_see_a_raised_leaf", () =>
            {
                string c = Src("Pits", "Suspension", "RM_MapComponent_SuspensionBridges.cs");
                string span = Body(c, "public List<Building_SpanDeck> SpanDecks(IntVec3 c)");
                Assert(span.Contains("StructuralDeckAt(map, cell)"), "a span giving way takes its raised squares too (R6)");
                Assert(!span.Contains(" DeckAt(map, cell)"), "can-fail: the walking read would leave raised squares standing after a collapse");
                string tick = Body(c, "public override void MapComponentTick()");
                Assert(tick.Contains("StructuralDeckAt(map, c)") && tick.Contains("d.DropAlone();"), "a swing-down drops raised squares too");
                Assert(tick.Contains("RM_Drawbridges.Tick(this, now);"), "leaves move from the bridges tick");
                Assert(Body(c, "public static Building_SuspensionDeck StructuralDeckAt(Map map, IntVec3 c)").Contains("!d.Collapsed"), "structure = intact");
            });

            Case("Drawbridge_P1_toggle_forces_pocket_rebuild_and_repath", () =>
            {
                string db = Src("Pits", "Drawbridge", "RM_Drawbridges.cs");
                string notify = Body(db, "public static void NotifyToggled(Map map, List<IntVec3> changed)");
                foreach (string must in new[] { "RecalculatePerceivedPathCostAt(c)", "reachability?.ClearCache()", "BumpClimbGeneration()",
                    "RM_SwimPathing.Bump(map)", "RM_PocketGrid.ForceRebuild(map)", "RepathOver(map, changed)" })
                {
                    Assert(notify.Contains(must), "can-fail: a toggle must " + must + " (R8)");
                }
                string apply = Body(db, "public static void Apply(Map map, SuspensionBridgeRecord r, DrawbridgeLeaf l)");
                Assert(apply.Contains("NotifyToggled(map, changed)") && apply.Contains("if (changed != null)"), "every toggle that changed a square notifies");
                string repath = Body(db, "public static void RepathOver(Map map, List<IntVec3> changed)");
                Assert(repath.Contains("pf.curPathRequest != null") && repath.Contains("pf.StopDead();") && repath.Contains("pf.StartPath(dest, pe);"),
                    "a pending request (old generation) or a path over a changed square is re-pathed");
                string pg = Src("Superdeep", "RM_PocketGrid.cs");
                string force = Body(pg, "public static void ForceRebuild(Map map)");
                Assert(force.Contains("RebuildIfStale(map, RM_SuperdeepTrap.EngineOf(map), true)"), "can-fail: the forced rebuild bypasses the 60-tick limit");
            });

            Case("Drawbridge_P1_raise_never_collapses", () =>
            {
                string db = Src("Pits", "Drawbridge", "RM_Drawbridges.cs");
                string code = StripComments(db);
                foreach (string bad in new[] { "Collapse(", "CollapseSpan(", "DropAlone(", ".Destroy(", "OnForcedDescent(", "LandWreck(" })
                {
                    Assert(!code.Contains(bad), "can-fail: a raise or lower must never call " + bad + " (R3)");
                }
            });

            Case("Drawbridge_P1_leaf_record_saves_per_leaf_versioned", () =>
            {
                string db = Src("Pits", "Drawbridge", "RM_Drawbridges.cs");
                string ex = Body(db, "public void ExposeData()");
                foreach (string key in new[] { "\"v\"", "\"first\"", "\"last\"", "\"hingeAtFirst\"", "\"controlAtFirst\"", "\"targetRaised\"",
                    "\"progress\"", "\"frozen\"", "\"holdRaised\"", "\"tipCommitted\"" })
                {
                    Assert(ex.Contains(key), "can-fail: the leaf record saves " + key + " (R9)");
                }
                string c = Src("Pits", "Suspension", "RM_MapComponent_SuspensionBridges.cs");
                Assert(c.Contains("Scribe_Collections.Look(ref leaves, \"rmDrawbridgeLeaves\", LookMode.Deep);"), "leaves are saved on their bridge");
                Assert(c.Contains("public bool IsDrawbridge => leaves != null && leaves.Count > 0;"), "an old save (no leaves) is a plain bridge, lowered");
                Assert(!c.Contains("raisedSquares"), "the withdrawn single raisedSquares int is gone (GPT #11)");
                string make = Body(db, "public static bool MakeDrawbridge(SuspensionBridgeRecord r, bool colonyBankAtFirst, out string why)");
                Assert(make.Contains("hingeAtFirst = s.HingeAtFirst, controlAtFirst = s.HingeAtFirst"), "each leaf is worked from its own winch bank");
                string can = Body(db, "public static bool CanBeDrawbridge(SuspensionBridgeRecord r, out string why)");
                Assert(can.Contains("IsDrawbridgeTier(r.tier)") && can.Contains("r.jetty") && can.Contains("r.towers"), "timber/steel, no jetty, no towers");
            });
        }

        private static string StripComments(string s)
        {
            var sb = new System.Text.StringBuilder();
            foreach (string line in s.Split('\n'))
            {
                int i = line.IndexOf("//", StringComparison.Ordinal);
                string l = i >= 0 ? line.Substring(0, i) : line;
                if (l.TrimStart().StartsWith("///")) continue;
                sb.Append(l).Append('\n');
            }
            return sb.ToString();
        }
    }
}
