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
                Assert(deck.Contains("public override float DeckHeightM => (Record?.deckNotches ?? 0) * RM_SpanMath.NotchM;")
                    && deck.Contains("RM_SpanMath.ClearsUnderpass(eng.ClimbDepthAt(Position), DeckNotches)"),
                    "a deck's height is its record's (0 = surface) and its floor band passes under at 2 m clearance (UNDERPASS)");
                string patches = Src("Pits", "Suspension", "RM_SuspensionPatches.cs");
                Assert(patches.Contains("\"Use a suspension bridge over dug ground\""), "vanilla bridges refused with the ruled message (Q6)");
                Assert(patches.Contains("nameof(GenConstruct.CanConstruct)") && patches.Contains("MayBuildDeck"), "build order is enforced on CanConstruct");
                Assert(patches.Contains("typeof(Designator_DigCanal)") && patches.Contains("typeof(Designator_DigCanalTo)")
                    && patches.Contains("typeof(Designator_FillInCanal)"), "dig, deepen and fill-in are refused under a bridge");
                Assert(Src("Superdeep", "RM_FallRails.cs").Contains("t is Pits.Building_SuspensionRailing"), "a railing is a rail for falls and throws");
                string mod = Src("RimMandrakeFlowWorksMod.cs");
                Assert(mod.Contains("Pits.RM_SuspensionSettings.ExposeData();") && mod.Contains("Pits.RM_SuspensionSettings.DoSettingsSection);"),
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
                Assert(noDefault == 13, "decks (grated and jetty included), anchors and the railing get no plain per-square button (" + noDefault + ")");
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
            // SUSPENSION_UNDERPASS_BUILD_MIND_YOUR_HEAD (construction design §1.4, §4; Q2 2 m, Q6 crush, Q7 sunken): the band rules.
            Case("Underpass_band_step_clearance_and_sunken_height", () =>
            {
                Assert(RM_SpanMath.ClearsUnderpass(8, 0) && RM_SpanMath.ClearsUnderpass(4, 0) && !RM_SpanMath.ClearsUnderpass(3, 0),
                    "verify L2 shape: a 4 m and a 2 m trench pass under a surface deck; 1.5 m does not (a wall from below)");
                Assert(RM_SpanMath.ClearsUnderpass(14, 8) && !RM_SpanMath.ClearsUnderpass(11, 8), "a sunken deck at 4 m clears a 7 m core only with 2 m to spare");
                Assert(RM_SuspensionMath.StepGoesUnder(true, 0, false, false, 8), "from the trench floor (4 m) into a surface deck square: under it");
                Assert(!RM_SuspensionMath.StepGoesUnder(true, 0, false, false, 0), "from an anchor (surface) onto the deck: on it");
                Assert(RM_SuspensionMath.StepGoesUnder(true, 0, true, true, 0) && !RM_SuspensionMath.StepGoesUnder(true, 0, true, false, 0),
                    "deck square to deck square: the band is kept (under stays under, on stays on)");
                Assert(!RM_SuspensionMath.StepGoesUnder(false, 0, false, false, 8), "can-fail: a deck that does not clear is never walked under");
                Assert(!RM_SuspensionMath.StepGoesUnder(true, 8, false, false, 8), "from a ledge at the sunken deck's height: onto it");
                Assert(RM_SuspensionMath.DeckNotchesFor(0, 0, true) == 0 && RM_SuspensionMath.DeckNotchesFor(8, 8, true) == 8,
                    "both ends at the surface: 0; both on a 4 m ledge: a sunken deck at 4 m");
                Assert(RM_SuspensionMath.DeckNotchesFor(8, 8, false) == -1 && RM_SuspensionMath.DeckNotchesFor(8, 6, true) == -1
                    && RM_SuspensionMath.DeckNotchesFor(-1, 0, true) == -1, "sunken off, uneven ends or a wet end: refused");
                Assert(RM_SuspensionMath.GroundFor(8, 8, true) == SpanGround.Ground && RM_SuspensionMath.GroundFor(14, 8, true) == SpanGround.Hole
                    && RM_SuspensionMath.GroundFor(8, 0, true) == SpanGround.Hole && RM_SuspensionMath.GroundFor(4, 8, true) == SpanGround.Blocked,
                    "a 4 m ledge anchors a sunken deck at 4 m and the 7 m core is its hole; a shallower square is blocked");
                Assert(RM_SuspensionMath.GroundFor(8, 8, false) == SpanGround.Blocked && RM_SuspensionMath.GroundFor(14, 8, false) == SpanGround.Hole,
                    "a wet ledge cannot hold an anchor; wet hole squares are still crossed");
                Assert(RM_SuspensionMath.HeightPhrase(0, true) == "deck at surface · people below walk under it"
                    && RM_SuspensionMath.HeightPhrase(8, false) == "deck at 4 m (sunken) · a wall from below", "the readout says the height and the underside");
            });

            Case("Underpass_shots_between_bands_and_crush", () =>
            {
                Assert(RM_SuspensionMath.ShotBlockedBetweenBands(true, false, false, false, false, true), "verify L2: solid deck: floor band -> deck blocked");
                Assert(RM_SuspensionMath.ShotBlockedBetweenBands(false, false, true, true, false, false), "solid deck: deck -> floor band blocked");
                Assert(!RM_SuspensionMath.ShotBlockedBetweenBands(false, false, true, true, true, false), "verify L2: a grate does not block");
                Assert(!RM_SuspensionMath.ShotBlockedBetweenBands(true, false, false, true, false, false), "both under: within a band, ignored");
                Assert(!RM_SuspensionMath.ShotBlockedBetweenBands(false, false, true, false, false, true), "can-fail: both on the deck: ignored");
                Assert(!RM_SuspensionMath.ShotBlockedBetweenBands(false, false, false, true, false, false), "someone off any deck shooting under: the cliff rule's");
                Assert(RM_SuspensionMath.CrushDamageMin == 15 && RM_SuspensionMath.CrushDamageMax == 30, "hit like a thin-roof collapse (vanilla 15-30)");
            });

            Case("Underpass_wiring_masks_sites_not_tunnels", () =>
            {
                string mask = Src("Superdeep", "RM_CliffMask.cs");
                Assert(mask.Contains("if (m.underDerived && Pits.RM_SuspensionUnderpass.UsesFloorView(p))") && mask.Contains("job.connectivity = m.under[band].AsReadOnly();"),
                    "the swap hands the floor band the floor view");
                Assert(mask.Contains("RM_PocketGrid.EffectiveDepth(map, eng, true)") && mask.Contains("m.underDerived = differs;"),
                    "the floor view is derived only while a passing deck stands");
                Assert(Src("Superdeep", "RM_PocketGrid.cs").Contains("!(floorView && c.FloorBandPassesUnder)"), "the floor view reads a passing deck as its floor");
                Assert(Src("Superdeep", "RM_SuperdeepTrap.cs").Contains("? Pits.RM_SpanUtility.WalkingDepth(map, c, d) : d;"),
                    "the step floor reads a sunken deck at its height (not the surface)");
                Assert(Src("RM_PitExposure.cs").Contains("Pits.RM_SuspensionUnderpass.InFloorBand(p)"), "under a deck is exposed as in the open (Q9)");
                Assert(Src("Superdeep", "RM_PitDepthDraw.cs").Contains("Pits.RM_SuspensionUnderpass.DrawDepth(pawn, from,"), "the sink reads the band");
                string patches = Src("Pits", "Suspension", "RM_SuspensionPatches.cs");
                foreach (string k in new[] { "\"TryEnterNextPathCell\"", "nameof(RM_Patch_PathFollower_SuperdeepFloor.RelativeStepAllowed)",
                    "nameof(PathGrid.CalculatedCostAt)", "nameof(Verb.CanHitTargetFrom)", "nameof(Pawn_CarryTracker.TryDropCarriedThing)" })
                {
                    Assert(patches.Contains(k), "underpass patch point wired: " + k);
                }
                string comp = Src("Pits", "Suspension", "RM_MapComponent_SuspensionBridges.cs");
                Assert(comp.Contains("Scribe_Collections.Look(ref floorBandScribe, \"rmSuspensionFloorBand\", LookMode.Reference);"), "the floor band is saved");
                Assert(comp.Contains("new DamageInfo(DamageDefOf.Crush,") && comp.Contains("RM_SuspensionDefOf.RM_SuspensionWreck"), "a falling deck crushes below and leaves a wreck");
                Assert(Src("Pits", "Building_SpanDeck.cs").Contains("&& !RM_SuspensionUnderpass.InFloorBand(p))"), "a pawn under a deck weighs nothing on it");
                Assert(comp.Contains("\"rmSuspensionSwingTicks\"") && comp.Contains("\"rmSuspensionSwingCells\""), "can-fail: a swing-down in flight is saved");
                // NOT actual tunnels: only the suspension deck class grants the floor band
                string spanSrc = Src("Pits", "Building_SpanDeck.cs");
                Assert(spanSrc.IndexOf("int deck = DeckNotches;") < spanSrc.IndexOf("c.Destroy(DestroyMode.Vanish);") && spanSrc.IndexOf("int deck = DeckNotches;") > 0,
                    "can-fail: the collapse reads the deck height BEFORE destroying the span (Map is null after despawn)");
                Assert(!Src("Pits", "Building_PitCover.cs").Contains("FloorBandPassesUnder"), "can-fail: a pit cover never lets anyone under");
                Assert(Src("Pits", "Building_SpanDeck.cs").Contains("public virtual bool FloorBandPassesUnder => false;"), "the base span grants nothing");
                string set = Src("Pits", "Suspension", "RM_SuspensionSettings.cs");
                Assert(set.Contains("\"People can walk under suspension bridges\"") && set.Contains("\"Sunken bridges (below ground)\""), "both settings shown");
                string defs = ModFile("Defs", "Pits", "ThingDefs", "RM_SuspensionBridges.xml");
                Assert(defs.Contains("<defName>RM_SuspensionWreck</defName>") && !defs.Contains("For now nobody can walk under it"),
                    "the wreck exists and no description still says nobody walks under");
            });
            // SUSPENSION_WATERS_BUILD_MAY_BACKTRACK (parent §3, §7; Q5): natural water, floods, current, towers.
            Case("Waters_spannable_and_flood_damage", () =>
            {
                Assert(RM_SuspensionMath.WaterSpannable(true, false, true, true) && RM_SuspensionMath.WaterSpannable(true, true, true, true),
                    "rivers, lakes and the sea may be crossed");
                Assert(!RM_SuspensionMath.WaterSpannable(true, true, true, false) && RM_SuspensionMath.WaterSpannable(true, false, true, false),
                    "backtrack lever: sea off keeps rivers and lakes");
                Assert(!RM_SuspensionMath.WaterSpannable(true, false, false, true), "water off: no river or lake crossing");
                Assert(!RM_SuspensionMath.WaterSpannable(false, false, true, true), "can-fail: dry ground is never 'water'");
                Assert(RM_SuspensionMath.FloodDamage(SuspensionTier.Timber, 120) == 6 && RM_SuspensionMath.FloodDamage(SuspensionTier.Rope, 60) == 3,
                    "rope and timber lose 5% of their hit points an hour awash");
                Assert(RM_SuspensionMath.FloodDamage(SuspensionTier.Steel, 250) == 0 && RM_SuspensionMath.FloodDamage(SuspensionTier.Heavy, 500) == 0,
                    "steel and heavy shrug floods off");
                Assert(RM_SuspensionMath.FloodDamage(SuspensionTier.Rope, 10) == 1, "never less than 1");
            });

            Case("Waters_wiring_path_swim_current_settings", () =>
            {
                string patches = Src("Pits", "Suspension", "RM_SuspensionPatches.cs");
                Assert(patches.Contains("class RM_Patch_SuspensionDeckOverDeepWater") && patches.Contains("[HarmonyPriority(Priority.Last)]"),
                    "a deck over deep water answers its own path cost, after the swim cost");
                Assert(patches.Contains("__result = ex.ExcavatedDepthAt(c) > 0 || RM_SuspensionWaters.Spannable(c.GetTerrain(map));"),
                    "decks and towers stand on natural water");
                Assert(patches.Contains("map.terrainGrid.TempTerrainAt(c)?.IsWater == true") && patches.Contains("DamageDefOf.Deterioration"),
                    "flood damage reads the flood's temporary water layer");
                Assert(Src("Rivers", "RM_MapComponent_RiverCurrent.cs").Contains("Pits.RM_SuspensionWaters.CurrentExempt(map, c)"),
                    "the current never carries anyone on a deck (the fords' exemption)");
                string swim = Src("Swimming", "RM_Swim.cs");
                Assert(swim.Contains("if (Pits.RM_SpanUtility.DeckedAt(map, c))") && swim.Contains("&& !Pits.RM_SpanUtility.DeckedAt(map, cell))"),
                    "a decked square is not a swim square (items lie on it; non-swimmers cross it)");
                Assert(swim.Contains("(Pits.RM_PitCoverUtility.IsCovered(map, c) && !Pits.RM_SuspensionUnderpass.InFloorBand(p))"),
                    "nobody drowns on a deck over natural water");
                string des = Src("Pits", "Suspension", "Designator_SuspensionBridge.cs");
                Assert(des.Contains("return RM_SuspensionWaters.Spannable(terrain) ? SpanGround.Hole : SpanGround.Blocked;"), "the drag crosses natural water");
                string set = Src("Pits", "Suspension", "RM_SuspensionSettings.cs");
                Assert(set.Contains("\"Suspension bridges over rivers and lakes\"") && set.Contains("\"Suspension bridges over the sea\"")
                    && set.Contains("\"Floods damage light bridges\""), "the three water settings are shown");
            });
            // SUSPENSION_JETTY_BUILD_WALK_THE_PLANK (construction design §3): 1-2 squares, steel/heavy, one person, fails at the root.
            Case("Jetty_reach_root_type_and_load", () =>
            {
                SuspensionTier st = SuspensionTier.Steel;
                Assert(RM_SuspensionMath.ValidateJetty(Lane("GHH"), false, st) == null, "verify L2: a 2-square steel jetty from a bank over a pit is accepted");
                string three = RM_SuspensionMath.ValidateJetty(Lane("GHHH"), false, st);
                Assert(three != null && three.Contains("at most 2") && three.Contains("this one: 3"), "verify L2: a 3-square jetty is refused with the reason: " + three);
                Assert(RM_SuspensionMath.ValidateJetty(Lane("GH"), false, SuspensionTier.Heavy) == null, "a 1-square heavy jetty is fine");
                Assert(RM_SuspensionMath.ValidateJetty(Lane("GHH"), false, SuspensionTier.Timber) != null
                    && RM_SuspensionMath.ValidateJetty(Lane("GH"), false, SuspensionTier.Rope) != null, "steel or heavy only");
                Assert(RM_SuspensionMath.ValidateJetty(Lane("HHH"), false, st) != null, "can-fail: a root over the hole is refused");
                Assert(RM_SuspensionMath.ValidateJetty(Lane("XH"), true, st) == null, "rooted on a bridge's anchor (the root square is that anchor)");
                Assert(RM_SuspensionMath.ValidateJetty(Lane("GG"), false, st) != null && RM_SuspensionMath.ValidateJetty(Lane("G"), false, st) != null,
                    "nothing to reach over, or no reach: refused");
                Assert(RM_SuspensionMath.JettyRatingKg(1f) == 120f && RM_SuspensionMath.JettyRatingKg(2f) == 240f, "one person's weight (120 kg) × the load multiplier");
                Assert(RM_SuspensionMath.Classify(70f, RM_SuspensionMath.JettyRatingKg(1f)) == SpanLoadState.Ok
                    && RM_SuspensionMath.Classify(140f, RM_SuspensionMath.JettyRatingKg(1f)) == SpanLoadState.Over, "verify L2: one 70 kg colonist stands; two drop it");
                Assert(RM_SuspensionMath.JettyReadoutLine(st, 70f, 120f, 0) == "Jetty (steel) · deck at surface · load 70 / 120 kg", "the jetty's readout line");
            });

            Case("Jetty_wiring_record_designator_defs", () =>
            {
                string comp = Src("Pits", "Suspension", "RM_MapComponent_SuspensionBridges.cs");
                Assert(comp.Contains("public int SpanCount => jetty ? 1 : Supports.Count - 1;") && comp.Contains("RM_SuspensionMath.JettyRatingKg("),
                    "a jetty is one span rated at one person");
                Assert(comp.Contains("b.jetty && b.Cell(0, 0) == c") && comp.Contains("CollapseSpan(jd, \"lost its anchor\");"),
                    "a jetty fails at the root: losing its anchor drops it whole");
                Assert(comp.Contains("if (r.jetty && i == 0 && index.ContainsKey(r.Cell(lane, i)))"), "a jetty on a bridge's anchor leaves the anchor to the bridge");
                string des = Src("Pits", "Suspension", "Designator_SuspensionBridge.cs");
                Assert(des.Contains("public abstract class Designator_SuspensionJetty : Designator_Build") && des.Contains("jetty = true, railings = true"),
                    "the jetty button: its own drag, railed by default");
                Assert(Src("Pits", "Suspension", "RM_SuspensionPatches.cs").Contains("bool ok = r.jetty ?"), "a jetty builds outward from its root");
                string defs = ModFile("Defs", "Pits", "ThingDefs", "RM_SuspensionBridges.xml");
                foreach (string n in new[] { "Steel", "Heavy" })
                {
                    int at = defs.IndexOf("<defName>RM_SuspensionJetty_" + n + "</defName>");
                    Assert(at >= 0, n + " jetty def");
                    string blk = defs.Substring(at, defs.IndexOf("</ThingDef>", at) - at);
                    Assert(blk.Contains("<jetty>true</jetty>") && blk.Contains("<graphicClass>Graphic_Multi</graphicClass>"), n + " jetty: extension and Graphic_Multi");
                }
                string patch = ModFile("Patches", "Pits", "RM_SuspensionBridges.xml");
                Assert(patch.Contains("Designator_SuspensionJetty_Steel") && patch.Contains("Designator_SuspensionJetty_Heavy"), "the jetty buttons are registered");
            });
            // SUSPENSION_ART_RESKIN_HE_SEES_FIRST: the four looks through the shared style picker (art accepted first time, 2026-10-18).
            Case("Looks_four_styles_registered_and_carried", () =>
            {
                string patches = Src("Pits", "Suspension", "RM_SuspensionPatches.cs");
                Assert(patches.Contains("Machinery.PipeLook.Core.Register(StyledDefs, Machinery.PipeStyles.StyleDefName);"),
                    "the parts join FlowWorks' style picker (the RM_BankWeir_* pattern)");
                Assert(!patches.Contains("\"RM_SuspensionDeck_Rope\"") && !patches.Contains("\"RM_SuspensionAnchor_Rope\""), "rope stays Scrapper-only (unstyled)");
                string des = Src("Pits", "Suspension", "Designator_SuspensionBridge.cs");
                Assert(des.Contains("GenConstruct.PlaceBlueprintForBuild(d, c, map, rot, Faction.OfPlayer, stuff, null, style);")
                    && des.Contains("look = RM_SuspensionLooks.LookFor(this),"), "a dragged bridge's parts carry the button's look");
                string comp = Src("Pits", "Suspension", "RM_MapComponent_SuspensionBridges.cs");
                Assert(comp.Contains("Scribe_Values.Look(ref look, \"look\");") && comp.Contains("RM_SuspensionLooks.Apply(w, look);")
                    && comp.Contains("RM_SuspensionLooks.StyleFor(rail, look)"), "the railings and the wreck follow the bridge's look; the look is saved");
                string styles = ModFile("Defs", "Pits", "ThingDefs", "RM_SuspensionStyles.xml");
                foreach (string part in new[] { "RM_SuspensionDeck_Steel", "RM_SuspensionDeck_SteelGrated", "RM_SuspensionAnchor_Heavy",
                    "RM_SuspensionTower", "RM_SuspensionRailing", "RM_SuspensionWreck", "RM_SuspensionJetty_Heavy" })
                {
                    foreach (string look in new[] { "Scrapper", "Industrial", "Modern", "Futuristic" })
                    {
                        Assert(styles.Contains("<defName>" + part + "_" + look + "</defName>"), part + "_" + look + " style def");
                    }
                }
            });
            // SUSPENSION_TOWER_LOAD_FIX_LEFTOVERS_PILE: the suspension review's leftovers, each can-fail on the production source.
            Case("Leftovers_tower_load_wreck_band_link", () =>
            {
                string comp = Src("Pits", "Suspension", "RM_MapComponent_SuspensionBridges.cs");
                int lost = comp.IndexOf("public void Notify_SupportLost(IntVec3 c)");
                string lostBody = comp.Substring(lost, comp.IndexOf("private static List<int> WithTower", lost) - lost);
                Assert(!lostBody.Contains("TowerAt(map, c)") && lostBody.Contains("BuiltAt<Building_SuspensionTower>(map, c) != null"),
                    "can-fail: only a BUILT tower holds the span (a rebuild blueprint or frame on a lost tower's square does not)");
                string deck = Src("Pits", "Suspension", "Building_SuspensionDeck.cs");
                Assert(deck.Contains("Notify_TowerBuilt(this)"), "can-fail: a rebuilt tower supports its bridge again");
                string span = Src("Pits", "Building_SpanDeck.cs");
                Assert(span.Contains("p.carryTracker?.CarriedThing") && span.Contains("sum += p.GetStatValue(StatDefOf.Mass) + CarriedKg(p);")
                    && !span.Contains("MassUtility.GearAndInventoryMass") && !span.Contains("MassUtility.InventoryMass"),
                    "can-fail: a pawn weighs body + gear + inventory (the Mass stat) + what it carries, inventory never added twice");
                int clear = comp.IndexOf("public static void ClearDeckTop(Map map, IntVec3 c)");
                string clearBody = comp.Substring(clear, comp.IndexOf("public static void Drop(", clear) - clear);
                Assert(clearBody.Contains("rebuild") && clearBody.LastIndexOf("t.def.IsBlueprint") > clearBody.IndexOf("DestroyMode.KillFinalize"),
                    "can-fail: rebuild blueprints left by things killed on a falling deck are cleared off the hole");
                Assert(comp.Contains("bandGame != Current.Game") && comp.Contains("public override void MapRemoved()"),
                    "can-fail: the band counter resets for a new game/load and drops a removed map's band");
                string link = Src("Pits", "Suspension", "RM_SuspensionDeckLink.cs");
                Assert(link.Contains("r.TryIndexOf(c, out _, out _)") && link.Contains("LinksTo(map, r, p + IntVec3.North)"),
                    "can-fail: a deck links only to the deck squares and anchors of its own bridge");
                Assert(comp.Contains("IsUnder(t)") && comp.Contains("public void MarkUnder(Thing t)")
                    && Src("Pits", "Suspension", "RM_SuspensionPatches.cs").Contains("?.MarkUnder(t);"),
                    "can-fail: an item or corpse left UNDER a deck (no open floor to slide to) is not the deck's load");
                string proofs = Src("Pits", "Suspension", "RM_SuspensionProofs.cs");
                Assert(proofs.Contains("if (!p.Spawned || p.Dead || p.Map != map)"), "can-fail: the knock proof never writes a position across maps");
                Assert(proofs.Contains("idx.Count == 0 ? new List<Building_SpanDeck>()"), "can-fail: the span proof survives a span with no deck squares");
                Assert(proofs.Contains("p.carryTracker.DestroyCarriedThing();"), "can-fail: a failed proof drop leaves nothing in the pawn's hands");
                string fire = Src("RM_LiquidFire.cs");
                Assert(fire.Contains("PawnsAt(map, c)") && !fire.Contains("for (int t = things.Count - 1; t >= 0; t--)"),
                    "can-fail: the fire and grate effects walk a snapshot of the pawns, not the live thing list a death or a fire spawn edits");
            });
            Case("Suspension_deck_built_over_the_hole_floor", () =>
            {
                // SUSPENSION_LIVE_DIAGNOSE_FIRST_REAL_RUN (live 2026-10-19: a timber span read 816 kg with ONE rider: 13 pawns
                // left in the trench by earlier runs, built over, were counted ON the deck). The band was entered only by a
                // walked step; a deck completed over the hole must put whoever stands down there in the floor band and slide
                // what lies there out (or mark it under), or they weigh on the deck.
                string comp = Src("Pits", "Suspension", "RM_MapComponent_SuspensionBridges.cs");
                int at = comp.IndexOf("public void Notify_DeckBuilt(Building_SuspensionDeck d)");
                Assert(at >= 0, "Notify_DeckBuilt exists");
                string body = comp.Substring(at, comp.IndexOf("// ── railings", at) - at);
                Assert(body.Contains("d.FloorBandPassesUnder"), "can-fail: only a deck the floor band passes under takes the hole floor under it");
                Assert(body.Contains("SetBand(p, true)") && body.Contains("!p.Flying") && body.Contains("!p.Dead"),
                    "can-fail: a live, walking pawn already in the hole goes into the floor band (not the deck's load)");
                Assert(body.Contains("RM_SuspensionUnderpass.SlideOut(t)") && body.Contains("ThingCategory.Item"),
                    "can-fail: an item lying in the hole slides out (or is marked under), never the deck's load");
                Assert(body.Contains(".ToList()"), "can-fail: the square's thing list is snapshotted before SlideOut edits it");
            });
            // textures: selftest_flowworks_suspension_art.py (the SelfTest staging copies no Textures folder)
            UnderpassReachChecks.Run(Case);   // UNDERPASS_REACH_FIX_DECK_VIEW_SAYS_NO: reach agrees with A* under decks (UnderpassReachChecks.cs)
        }
    }
}
