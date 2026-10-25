// DIG_SPOIL_BUILD_GRAVEL_PAYS_ITS_WAY + PIT_DIG_FIX_SAND_SLIDES_BACK_IN (owner 2026-10-25; design
// D:\ClaudeWork\rimmandrake\dig_spoil_20261025\DESIGN.md): offline proof of the ground classifier (RM_GroundClassMath), the
// spoil a cut leaves, the fill credit (1 gravel or 2 chunks a notch), the mining-miss rule, and the production wiring.
// NOT proven here (live rows owed to northstar/gravel_live.py): a real cut dropping gravel, a sand order refused in game,
// a fill job hauling gravel, a mined wall's missed chunk becoming gravel.
using System;
using System.IO;
using System.Text.RegularExpressions;
using RimMandrake.FlowWorks;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class GroundClassChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string Src(string rel) => RiverSwitchFlipChecks.Src(rel);

        private static string ModRoot => Path.GetFullPath(Path.Combine(Path.GetDirectoryName(RiverSwitchFlipChecks.SrcPath("RM_SpanMath.cs")), ".."));

        private static RM_GroundClass C(string name, string cat, bool soil = false, bool rock = false, bool water = false, bool layer = false, bool dig = false)
            => RM_GroundClassMath.Classify(name, water, layer, rock, soil, dig, cat);

        public static void Run(Action<string, Action> Case)
        {
            Case("ground class: sand, soft sand, dry lake bed, marsh, dense mud slide back (owner 2026-10-25)", () =>
            {
                Assert(C("Sand", "Sand", soil: true, dig: true) == RM_GroundClass.Slumps, "Sand must slump");
                Assert(C("SoftSand", "Sand", dig: true) == RM_GroundClass.Slumps, "SoftSand must slump");
                Assert(C("DryLakeBed", "Sand", dig: true) == RM_GroundClass.Slumps, "DryLakeBed (categoryType Sand) must slump");
                Assert(C("MarshyTerrain", "Soil", soil: true, dig: true) == RM_GroundClass.Slumps, "MarshyTerrain must slump");
                Assert(C("Mud", "Soil", soil: true) == RM_GroundClass.Slumps, "Mud must slump");
                Assert(C("RM_DenseMud", "Misc", dig: true) == RM_GroundClass.Slumps, "RM_DenseMud must slump");
                Assert(C("RM_Slime", "Misc") == RM_GroundClass.Slumps, "RM_Slime must slump");
            });
            Case("ground class: card rubble (salt crust, asphalt, packed snow) outranks Sand category and layerable", () =>
            {
                Assert(C("RUT_Jawa_SaltCrust", "Sand", dig: true) == RM_GroundClass.Rubble, "salt crust is rubble, not sand");
                Assert(C("RM_MiasmaSaltCrust", "Sand") == RM_GroundClass.Rubble, "miasma salt crust is rubble");
                Assert(C("VEE_Salt", "Sand") == RM_GroundClass.Rubble, "VEE_Salt is rubble");
                Assert(C("WastelandAsphalt", "Misc") == RM_GroundClass.Rubble, "asphalt is rubble");
                Assert(C("RM_WastelandBrokenAsphalt", "Misc") == RM_GroundClass.Rubble, "broken asphalt is rubble");
                Assert(C("RM_PackedSnow", "Misc") == RM_GroundClass.Rubble, "packed snow is rubble");
                Assert(C("CooledLava", "Misc", layer: true) == RM_GroundClass.Rubble, "cooled lava (layerable) is rubble");
                Assert(C("Gravel", "Misc", soil: true, dig: true) == RM_GroundClass.Rubble, "gravel ground is rubble");
                Assert(C("Snow", "Misc") != RM_GroundClass.Rubble, "loose snow is NOT on the card's list");
            });
            Case("ground class: rock, soil, floor, water, nothing", () =>
            {
                Assert(C("Granite_Rough", "Stone", rock: true) == RM_GroundClass.Rock, "rough granite is rock");
                Assert(C("SomeModStone", "Stone") == RM_GroundClass.Rock, "categoryType Stone is rock");
                Assert(C("Soil", "Soil", soil: true, dig: true) == RM_GroundClass.Soil, "soil is soil");
                Assert(C("Riverbank", "Soil", soil: true, dig: true) == RM_GroundClass.Soil, "riverbank is soil");
                Assert(C("WoodPlankFloor", "Misc", layer: true) == RM_GroundClass.Floor, "a player floor is a floor");
                Assert(C("WaterShallow", "Misc", water: true) == RM_GroundClass.Water, "water is water");
                Assert(C("Lava", "Misc") == RM_GroundClass.NotDiggable, "a non-diggable misc terrain is not dug");
            });
            Case("cut spoil: rock gives a chunk or gravel, rubble gravel only, soil nothing", () =>
            {
                Assert(RM_GroundClassMath.CutYield(RM_GroundClass.Rock, true) == RM_CutSpoil.Chunk, "rock + chunk roll = chunk");
                Assert(RM_GroundClassMath.CutYield(RM_GroundClass.Rock, false) == RM_CutSpoil.Gravel, "rock + miss = gravel");
                Assert(RM_GroundClassMath.CutYield(RM_GroundClass.Rubble, true) == RM_CutSpoil.Gravel, "rubble never gives a chunk");
                Assert(RM_GroundClassMath.CutYield(RM_GroundClass.Rubble, false) == RM_CutSpoil.Gravel, "rubble gives gravel");
                Assert(RM_GroundClassMath.CutYield(RM_GroundClass.Soil, true) == RM_CutSpoil.None, "dirt makes no chunks");
                Assert(RM_GroundClassMath.CutYield(RM_GroundClass.Soil, false) == RM_CutSpoil.None, "dirt makes no gravel");
            });
            Case("fill credit: 1 gravel or 2 chunks a notch; a no-op fill spends nothing", () =>
            {
                Assert(RM_GroundClassMath.CreditShort(0) == 2, "empty cell owes 2");
                Assert(RM_GroundClassMath.CreditShort(RM_GroundClassMath.CreditOf(true)) == 0, "one gravel funds a notch");
                Assert(RM_GroundClassMath.CreditShort(RM_GroundClassMath.CreditOf(false)) == 1, "one chunk is half a notch");
                Assert(RM_GroundClassMath.CreditShort(2 * RM_GroundClassMath.CreditOf(false)) == 0, "two chunks fund a notch");
                Assert(RM_GroundClassMath.CreditAfterFill(2, true) == 0, "a fill spends the notch");
                Assert(RM_GroundClassMath.CreditAfterFill(2, false) == 2, "a fill that changed nothing keeps the credit");
                Assert(RM_GroundClassMath.CreditAfterFill(1, true) == 1, "an unfunded fill spends nothing");
            });
            Case("mining: a missed chunk gives gravel, a dropped chunk does not", () =>
            {
                Assert(RM_GroundClassMath.MiningGivesGravel(3, 3), "no new chunk -> gravel");
                Assert(!RM_GroundClassMath.MiningGivesGravel(3, 4), "a new chunk -> no gravel");
            });
            Case("wiring: gates, yields, fill cost, mining patch, recipes, gravel def, five toggles", () =>
            {
                string des = Src("Designator_DigCanal.cs");
                string wg = Src("WorkGiver_DigCanal.cs");
                Assert(des.Contains("RM_DigSpoil.DigRefusal(") && wg.Contains("RM_DigSpoil.DigRefusal("), "designator and work giver share the ground gate");
                string spoil = Src("RM_DigSpoil.cs");
                Assert(spoil.Contains("slide back in"), "sand refusal says it slides back in");
                Assert(spoil.Contains("typeof(Mineable)") && spoil.Contains("\"TrySpawnYield\""), "mining patch on Mineable.TrySpawnYield");
                Assert(spoil.Contains("SetAllow(") && spoil.Contains("defaultIngredientFilter") && spoil.Contains("fixedIngredientFilter"), "recipe applier sets all three filters");
                Assert(spoil.Contains("Faction.OfPlayer"), "mined gravel forbidden for non-player miners, as vanilla");
                Assert(spoil.Contains("typeof(Map), typeof(bool), typeof(Pawn)"), "TrySpawnYield targeted by argument types: 1.6 keeps an [Obsolete] 4-arg overload");
                string disc = Src("RM_DigDiscovery.cs");
                Assert(disc.Contains("RM_GroundClassMath.CutYield("), "the cut yield goes through the classifier");
                Assert(disc.Contains("rockChunk && RimMandrakeFlowWorksSettings.digSpoilEnabled"), "with spoil on, the finds roll drops its rock-chunk fallbacks (dirt makes no chunks)");
                string dig = Src("JobDriver_DigCanal.cs");
                Assert(dig.Contains("RM_DigSpoil.IsRubbleAt(") && dig.Contains("ClearCredit("), "rubble digs at rock speed; a cut clears fill credit");
                string fill = Src("JobDriver_FillInCanal.cs");
                Assert(fill.Contains("TryMakePreToilReservations") && fill.Contains("CreditAfterFill("), "fill reserves its material and spends credit only on a real change");
                Assert(fill.Contains("Toils_Jump.JumpIf(") && !Regex.IsMatch(fill, @"if\s*\(\s*job\.targetB\.IsValid\s*\)\s*\{"), "one toil layout with or without material (a save after the tip must load onto the same toils)");
                string fwg = Src("WorkGiver_FillInCanal.cs");
                Assert(fwg.Contains("RM_DigSpoil.FindFillMaterial("), "fill work giver looks for gravel or chunks");
                Assert(fwg.Contains("HasMaterial(") && fwg.Contains("List<IntVec3> cells"), "an unpaid pit with no material is no job; the cell list is materialised");
                string defs = File.ReadAllText(Path.Combine(ModRoot, "Defs", "Pits", "ThingDefs", "RM_Gravel.xml"));
                Assert(defs.Contains("<defName>RM_Gravel</defName>") && defs.Contains("RM_GravelRecipes"), "RM_Gravel def with its recipe list");
                string mod = Src("RimMandrakeFlowWorksMod.cs");
                foreach (string k in new[] { "sandMudSlidesBackEnabled", "digSpoilEnabled", "fillCostsSpoilEnabled", "mineGravelEnabled", "gravelRecipesEnabled" })
                {
                    Assert(mod.Contains("Scribe_Values.Look(ref " + k), "setting saved: " + k);
                    Assert(Regex.IsMatch(mod, @"public\s+static\s+bool\s+" + k + @"\s*=\s*true\s*;"), "setting field, default on: " + k);
                    Assert(Regex.Matches(mod, "\"" + k + "\"").Count >= 3, "setting keyed in Scribe, the dependency registry and its label: " + k);
                }
                string proj = Src("RimMandrake_FlowWorks.csproj");
                Assert(proj.Contains("RM_GroundClassMath.cs") && proj.Contains("RM_DigSpoil.cs"), "both new files compile into the mod");
            });
        }
    }
}
