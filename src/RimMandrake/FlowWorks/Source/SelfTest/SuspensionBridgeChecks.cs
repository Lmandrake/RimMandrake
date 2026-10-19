// SUSPENSION_BRIDGE_BUILD_POSTS_AT_BOTH_ENDS (design/RimMandrake/suspension_bridge_construction_design_2026-10-18.md;
// design/RimMandrake/flowworks_bridges_design_2026-10-17.md §6, §9): offline proof of the surface suspension bridge's rules on
// the production code (RM_SuspensionMath) and the production wiring (sources, defs, patch XML, textures). Verify row L1: the
// drag validator (ends on ground, middle all dug, length per type, width 1-3) and the load sum. Every case has a can-fail.
// NOT proven here (L2, live rows owed to northstar/suspension_bridge_proof.py): blueprints placed by a real drag, a colonist
// path over the deck, a 640 kg collapse, the swing-down order, railings over 20 staggers, vanilla Bridge refused in game.
using System;
using System.Collections.Generic;
using System.IO;
using RimMandrake.FlowWorks;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class SuspensionBridgeChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string Src(params string[] rel) => RiverSwitchFlipChecks.Src(Path.Combine(rel));

        private static string ModRoot => Path.GetFullPath(Path.Combine(Path.GetDirectoryName(RiverSwitchFlipChecks.SrcPath("RM_SpanMath.cs")), ".."));

        private static string ModFile(params string[] rel) => File.ReadAllText(Path.Combine(ModRoot, Path.Combine(rel)));

        private static List<SpanGround> Lane(string s)
        {
            // G = ground, H = dug hole, X = blocked
            List<SpanGround> l = new List<SpanGround>();
            foreach (char ch in s)
            {
                l.Add(ch == 'G' ? SpanGround.Ground : ch == 'H' ? SpanGround.Hole : SpanGround.Blocked);
            }
            return l;
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("Suspension_tiers_are_the_items_numbers", () =>
            {
                Assert(RM_SuspensionMath.BaseMaxLength(SuspensionTier.Rope) == 8 && RM_SuspensionMath.BaseMaxLength(SuspensionTier.Timber) == 6
                    && RM_SuspensionMath.BaseMaxLength(SuspensionTier.Steel) == 10 && RM_SuspensionMath.BaseMaxLength(SuspensionTier.Heavy) == 14,
                    "length 8/6/10/14 squares between supports");
                Assert(RM_SuspensionMath.BaseLoadKg(SuspensionTier.Rope) == 150f && RM_SuspensionMath.BaseLoadKg(SuspensionTier.Timber) == 600f
                    && RM_SuspensionMath.BaseLoadKg(SuspensionTier.Steel) == 2000f && RM_SuspensionMath.BaseLoadKg(SuspensionTier.Heavy) == 8000f,
                    "load 150/600/2,000/8,000 kg");
                Assert(RM_SuspensionMath.LentAffordances(SuspensionTier.Rope) == 0
                    && RM_SuspensionMath.LentAffordances(SuspensionTier.Timber) == RM_SuspensionMath.AffordLight
                    && RM_SuspensionMath.LentAffordances(SuspensionTier.Steel) == (RM_SuspensionMath.AffordLight | RM_SuspensionMath.AffordMedium)
                    && (RM_SuspensionMath.LentAffordances(SuspensionTier.Heavy) & RM_SuspensionMath.AffordHeavy) != 0,
                    "timber lends Light; steel Light/Medium; heavy all; rope none");
                Assert(RM_SuspensionMath.MaxLength(SuspensionTier.Timber, 2f) == 12 && RM_SuspensionMath.MaxLength(SuspensionTier.Timber, 0.01f) == 1,
                    "can-fail: the length multiplier scales the cap and never below one square");
                Assert(RM_SuspensionMath.RatingKg(SuspensionTier.Timber, 2, 1f) == 1200f && RM_SuspensionMath.RatingKg(SuspensionTier.Timber, 1, 0.5f) == 300f,
                    "rating = per-lane load × lanes × multiplier");
            });

            Case("Suspension_drag_validator_ends_middle_length_width", () =>
            {
                SuspensionTier t = SuspensionTier.Timber;
                Assert(RM_SuspensionMath.ValidateLane(Lane("GHHHHHHG"), null, t, 1f) == null, "verify L2 shape: a 6-square timber bridge over a trench is accepted");
                string seven = RM_SuspensionMath.ValidateLane(Lane("GHHHHHHHG"), null, t, 1f);
                Assert(seven != null && seven.Contains("at most 6 squares") && seven.Contains("this span: 7"), "a 7-square timber bridge is refused with the length reason: " + seven);
                Assert(RM_SuspensionMath.ValidateLane(Lane("GHHHHHHHG"), null, SuspensionTier.Rope, 1f) == null, "can-fail: rope spans 8, so 7 is fine");
                Assert(RM_SuspensionMath.ValidateLane(Lane("GHHHHHHHG"), null, t, 1.2f) == null, "the length multiplier reaches the validator");
                string start = RM_SuspensionMath.ValidateLane(Lane("HHHHG"), null, t, 1f);
                Assert(start != null && start.Contains("start on solid"), "a drag starting over the hole is refused");
                string end = RM_SuspensionMath.ValidateLane(Lane("GHHHX"), null, t, 1f);
                Assert(end != null && end.Contains("end on solid"), "a drag ending on blocked ground is refused");
                string touch = RM_SuspensionMath.ValidateLane(Lane("GHHGHHG"), null, t, 1f);
                Assert(touch != null && touch.Contains("touching down"), "undug ground in the middle is refused (two bridges)");
                string blocked = RM_SuspensionMath.ValidateLane(Lane("GHXHG"), null, t, 1f);
                Assert(blocked != null && blocked.Contains("blocked"), "a blocked square in the middle is refused");
                Assert(RM_SuspensionMath.ValidateLane(Lane("GG"), null, t, 1f) != null, "nothing to cross is refused");
                // towers split a long crossing into spans
                string twelve = RM_SuspensionMath.ValidateLane(Lane("GHHHHHHHHHHHHG"), null, t, 1f);
                Assert(twelve != null, "12 squares of timber with no tower is refused");
                Assert(RM_SuspensionMath.ValidateLane(Lane("GHHHHHHHHHHHHG"), new HashSet<int> { 7 }, t, 1f) == null,
                    "a tower at square 7 makes two spans of 6 and it is accepted");
                Assert(RM_SuspensionMath.ValidateLane(Lane("GHHHHHHHHHHHHG"), new HashSet<int> { 3 }, t, 1f) != null,
                    "can-fail: a tower too near one end leaves a span of 9");
                // width
                List<IList<SpanGround>> three = new List<IList<SpanGround>> { Lane("GHHHG"), Lane("GHHHG"), Lane("GHHHG") };
                Assert(RM_SuspensionMath.ValidateDrag(three, null, t, 1f) == null, "3 wide is fine");
                List<IList<SpanGround>> four = new List<IList<SpanGround>>(three) { Lane("GHHHG") };
                string w = RM_SuspensionMath.ValidateDrag(four, null, t, 1f);
                Assert(w != null && w.Contains("1 to 3"), "4 wide is refused");
                List<IList<SpanGround>> bad = new List<IList<SpanGround>> { Lane("GHHHG"), Lane("GHGHG") };
                string row = RM_SuspensionMath.ValidateDrag(bad, null, t, 1f);
                Assert(row != null && row.StartsWith("Row 2:"), "every lane must cross on its own; the refusal names the row");
            });

            Case("Suspension_spans_supports_and_swing_order", () =>
            {
                List<int> sup = RM_SuspensionMath.Supports(10, new HashSet<int> { 5 });
                Assert(sup.Count == 3 && sup[0] == 0 && sup[1] == 5 && sup[2] == 9, "anchors and the tower are the supports");
                List<int> a = RM_SuspensionMath.SegmentCells(0, sup, 10), b = RM_SuspensionMath.SegmentCells(1, sup, 10);
                Assert(a.Count == 5 && a[0] == 1 && a[4] == 5 && b.Count == 3 && b[0] == 6 && b[2] == 8,
                    "span 0 is squares 1-5 (the tower square with it), span 1 is 6-8; anchors are no span's");
                Assert(RM_SuspensionMath.SegmentOf(5, sup) == 0 && RM_SuspensionMath.SegmentOf(6, sup) == 1 && RM_SuspensionMath.SegmentOf(1, sup) == 0,
                    "every deck square knows its span");
                List<int> none = RM_SuspensionMath.Supports(8, null);
                Assert(RM_SuspensionMath.SegmentCells(0, none, 8).Count == 6, "with no tower one span holds every deck square");
                List<int> fromLow = RM_SuspensionMath.SwingOrder(new List<int> { 3, 1, 2 }, true);
                List<int> fromHigh = RM_SuspensionMath.SwingOrder(new List<int> { 1, 2, 3 }, false);
                Assert(fromLow[0] == 1 && fromLow[2] == 3 && fromHigh[0] == 3 && fromHigh[2] == 1,
                    "can-fail: a swing-down runs from the lost end toward the kept one");
                Assert(RM_SuspensionMath.MayBuildDeck(2, 6, k => k == 1) && !RM_SuspensionMath.MayBuildDeck(2, 6, k => k == 0)
                    && RM_SuspensionMath.MayBuildDeck(1, 6, k => k == 0), "a deck square is built from a finished neighbour toward an anchor");
            });

            Case("Suspension_load_sag_and_falls", () =>
            {
                Assert(RM_SuspensionMath.Classify(640f, 600f) == SpanLoadState.Over, "640 on a 600 kg span gives way");
                Assert(RM_SuspensionMath.Classify(540f, 600f) == SpanLoadState.Sagging && RM_SuspensionMath.Classify(600f, 600f) == SpanLoadState.Sagging,
                    "from 90% up to the rating it sags");
                Assert(RM_SuspensionMath.Classify(539f, 600f) == SpanLoadState.Ok, "can-fail: under 90% it is fine");
                Assert(RM_SuspensionMath.LoadLine(640f, 600f) == "Load 640 / 600 kg", "the inspect line reads \"Load 640 / 600 kg\"");
                Assert(RM_SuspensionMath.ReadoutLine(SuspensionTier.Steel, 210f, 2000f) == "Suspension bridge (steel) · deck at surface · load 210 / 2,000 kg",
                    "the P8 readout line");
                Assert(RM_SuspensionMath.FallChance(RM_SuspensionMath.StaggerFallChance, true, true) == 0f, "a railed square never drops anyone");
                Assert(RM_SuspensionMath.FallChance(RM_SuspensionMath.BlastFallChance, false, false) == 0f, "no open edge, no fall");
                Assert(RM_SuspensionMath.FallChance(RM_SuspensionMath.StaggerFallChance, false, true) == 0.25f
                    && RM_SuspensionMath.FallChance(RM_SuspensionMath.SlimeFallChance, false, true) == 0.10f, "open edge: stagger/blast 25%, slime 10%");
            });

            Case("Suspension_wiring_sources_defs_patches", () =>
            {
                string comp = Src("Pits", "Suspension", "RM_MapComponent_SuspensionBridges.cs");
                Assert(comp.Contains("RM_SpanUtility.LoadOn(map, cells, null, true, standing)") && comp.Contains("StatDefOf.Mass) * t.stackCount")
                    && comp.Contains("BuildingMass(bld)"), "the span load counts pawns, items and buildings");
                Assert(comp.Contains("RM_SuspensionSettings.suspensionWeightCollapse") && comp.Contains("RM_SuspensionSettings.suspensionAnchorLossFalls"),
                    "weight collapse and anchor-loss falls obey their settings");
                string deck = Src("Pits", "Suspension", "Building_SuspensionDeck.cs");
                Assert(deck.Contains("public class Building_SuspensionDeck : Building_SpanDeck"), "a suspension deck is a span deck (extends the base)");
                Assert(!deck.Contains("override float DeckHeightM") && !deck.Contains("override bool FloorBandPassesUnder"),
                    "can-fail: a surface bridge keeps height 0 and no underpass (the UNDERPASS item's)");
                string patches = Src("Pits", "Suspension", "RM_SuspensionPatches.cs");
                Assert(patches.Contains("\"Use a suspension bridge over dug ground\""), "vanilla bridges refused with the ruled message (Q6)");
                Assert(patches.Contains("nameof(GenConstruct.CanConstruct)") && patches.Contains("MayBuildDeck"), "build order is enforced on CanConstruct");
                Assert(patches.Contains("typeof(Designator_DigCanal)") && patches.Contains("typeof(Designator_DigCanalTo)")
                    && patches.Contains("typeof(Designator_FillInCanal)"), "dig, deepen and fill-in are refused under a bridge");
                Assert(Src("Superdeep", "RM_FallRails.cs").Contains("t is Pits.Building_SuspensionRailing"), "a railing is a rail for falls and throws");
                string mod = Src("RimMandrakeFlowWorksMod.cs");
                Assert(mod.Contains("Pits.RM_SuspensionSettings.ExposeData();") && mod.Contains("Pits.RM_SuspensionSettings.DoSettingsSection(list);"),
                    "the Suspension bridges settings section is saved and drawn");
                Assert(Src("Pits", "Suspension", "RM_SuspensionSettings.cs").Contains("list.Label(\"Suspension bridges\");"), "section title");
                string defs = ModFile("Defs", "Pits", "ThingDefs", "RM_SuspensionBridges.xml");
                foreach (string n in new[] { "Rope", "Timber", "Steel", "Heavy" })
                {
                    Assert(defs.Contains("<defName>RM_SuspensionDeck_" + n + "</defName>") && defs.Contains("<defName>RM_SuspensionAnchor_" + n + "</defName>"),
                        n + ": deck and anchor defs");
                }
                Assert(!defs.Contains("<label>bridge") && !defs.Contains("span</label>"), "player-facing names never say a bare bridge or span");
                int noDefault = defs.Split(new[] { "<canGenerateDefaultDesignator>false</canGenerateDefaultDesignator>" }, StringSplitOptions.None).Length - 1;
                Assert(noDefault == 11, "decks (grated included), anchors and the railing get no plain per-square button (" + noDefault + ")");
                string patch = ModFile("Patches", "Pits", "RM_SuspensionBridges.xml");
                foreach (string n in new[] { "Rope", "Timber", "Steel", "Heavy" })
                {
                    Assert(patch.Contains("RimMandrake.FlowWorks.Pits.Designator_SuspensionBridge_" + n), n + ": drag designator registered");
                }
                string designator = Src("Pits", "Suspension", "Designator_SuspensionBridge.cs");
                Assert(designator.Contains("public class Designator_SuspensionBridge_Timber : Designator_SuspensionBridge"), "designator classes exist");
                Assert(designator.Contains("RM_SuspensionSettings.suspensionBridgesBuildable && base.Visible"), "settings off: no build button");
            });
            // SUSPENSION_GRATE_BUILD_LET_THE_FIRE_UP (parent design §4.1; Q4 spilled liquid only): verify row L1 and the wiring.
            Case("Grate_fire_attach_open_pit_times_three_quarters", () =>
            {
                float open = RM_FireMath.AttachChance(true, false, false);
                float solid = RM_FireMath.AttachChance(false, true, false, false);
                float grate = RM_FireMath.AttachChance(false, true, false, true);
                Assert(Math.Abs(grate - open * 0.75f) < 1e-6f, "verify L1: grated chance = open-pit chance × 0.75 (" + grate + ")");
                Assert(grate > solid, "verify L1: grated > solid attach chance (" + grate + " vs " + solid + ")");
                Assert(solid == RM_FireMath.AttachChance(false), "a solid deck keeps today's open-cell chance");
                Assert(RM_FireMath.AttachChance(false, true, true, true) == 0f, "can-fail: a flyer over a grate is never lit");
                Assert(RM_FireMath.AttachChance(true, false, false, true) == open, "no deck: the grate flag changes nothing (trapped stays certain)");
            });

            Case("Grate_drain_splash_and_types", () =>
            {
                Assert(RM_SuspensionMath.GrateDrainDl(true, true, true, 500, 9999) == 500, "a 50 L spill on a grate over a dug square drains whole");
                Assert(RM_SuspensionMath.GrateDrainDl(true, true, true, 500, 120) == 120, "only what the hole has room for drains");
                Assert(RM_SuspensionMath.GrateDrainDl(false, true, true, 500, 9999) == 0, "can-fail: a solid deck keeps its spill");
                Assert(RM_SuspensionMath.GrateDrainDl(true, false, true, 500, 9999) == 0, "setting off: spills stay on the grate");
                Assert(RM_SuspensionMath.GrateDrainDl(true, true, false, 500, 9999) == 0, "nothing drains where nothing is dug below");
                Assert(RM_SuspensionMath.GrateSplashChance(0.4f) == 0.2f, "splash reaches a grate at half the open-pit chance");
                Assert(RM_SuspensionMath.MayBeGrated(SuspensionTier.Steel) && RM_SuspensionMath.MayBeGrated(SuspensionTier.Heavy)
                    && !RM_SuspensionMath.MayBeGrated(SuspensionTier.Timber) && !RM_SuspensionMath.MayBeGrated(SuspensionTier.Rope),
                    "only steel and heavy come grated");
            });

            Case("Grate_wiring_sites_defs_settings", () =>
            {
                string fire = Src("RM_LiquidFire.cs");
                Assert(fire.Contains("Pits.RM_GrateEffects.GratePassesFire(map, c)") && fire.Contains("Pits.RM_GrateEffects.Scorch(p);"),
                    "the liquid fire's effects read the grate and burn the people on it");
                Assert(Src("RM_SlimeSlip.cs").Contains("float chance = share * RM_SlimeMath.SlipChance("), "slime splash on a grate is scaled by its share");
                string fx = Src("RM_PitFillEffects.cs");
                Assert(fx.Contains("if (drown && drowning != null && share >= 1f)") && fx.Contains("float add = share * RM_FillEffectMath.ToxinPerCheck("),
                    "toxic fill splashes onto a grate at its share; nobody drowns on a deck");
                string spill = Src("Machinery", "RM_LiquidSpill.cs");
                Assert(spill.IndexOf("Pits.RM_GrateEffects.DrainSpill(map, cell, liquid?.canalFluid, units)") >= 0
                    && spill.IndexOf("Pits.RM_GrateEffects.DrainSpill(") < spill.IndexOf("units -= ReturnToPond(map, cell, liquid, units);"),
                    "a spill on a grate drains before any filth or pond return");
                string fx2 = Src("Pits", "Suspension", "RM_SuspensionPatches.cs");
                Assert(fx2.Contains("new DamageInfo(DamageDefOf.Burn, RM_SuspensionMath.GrateBurnDamage)"), "burns on a grate are vanilla Burn injuries (no new hediff)");
                Assert(fx2.Contains("RM_SuspensionSettings.grateFirePasses") && fx2.Contains("RM_SuspensionSettings.grateDrainsSpills"), "both grate settings are read");
                string set = Src("Pits", "Suspension", "RM_SuspensionSettings.cs");
                Assert(set.Contains("\"Grates pass fire to people above\"") && set.Contains("\"Grates drain spills into the hole below\"")
                    && set.Contains("Scribe_Values.Look(ref grateFirePasses, \"grateFirePasses\", true);"), "the two grate settings are shown and saved");
                Assert(Src("Pits", "Suspension", "Building_SuspensionDeck.cs").Contains("public override bool Grated =>"), "a suspension deck exposes IsGrated (Grated)");
                string defs = ModFile("Defs", "Pits", "ThingDefs", "RM_SuspensionBridges.xml");
                foreach (string n in new[] { "Steel", "Heavy" })
                {
                    int at = defs.IndexOf("<defName>RM_SuspensionDeck_" + n + "Grated</defName>");
                    Assert(at >= 0, n + ": grated deck def");
                    int end = defs.IndexOf("</ThingDef>", at);
                    Assert(defs.Substring(at, end - at).Contains("<grated>true</grated>"), n + ": the grated deck carries grated=true");
                }
                Assert(!defs.Contains("RM_SuspensionDeck_TimberGrated") && !defs.Contains("RM_SuspensionDeck_RopeGrated"), "can-fail: no wooden grate");
                string patch = ModFile("Patches", "Pits", "RM_SuspensionBridges.xml");
                Assert(patch.Contains("Designator_SuspensionBridge_SteelGrated") && patch.Contains("Designator_SuspensionBridge_HeavyGrated"),
                    "the two grated build buttons are registered");
            });
            // textures: selftest_flowworks_suspension_art.py (the SelfTest staging copies no Textures folder)
        }
    }
}
