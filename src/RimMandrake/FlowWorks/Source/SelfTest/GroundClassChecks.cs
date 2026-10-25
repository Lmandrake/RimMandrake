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
            Case("ground class: card rubble (salt crust, asphalt) outranks Sand category and layerable", () =>
            {
                Assert(C("RUT_Jawa_SaltCrust", "Sand", dig: true) == RM_GroundClass.Rubble, "salt crust is rubble, not sand");
                Assert(C("RM_MiasmaSaltCrust", "Sand") == RM_GroundClass.Rubble, "miasma salt crust is rubble");
                Assert(C("VEE_Salt", "Sand") == RM_GroundClass.Rubble, "VEE_Salt is rubble");
                Assert(C("WastelandAsphalt", "Misc") == RM_GroundClass.Rubble, "asphalt is rubble");
                Assert(C("RM_WastelandBrokenAsphalt", "Misc") == RM_GroundClass.Rubble, "broken asphalt is rubble");
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
            Case("IceDig_ice_and_packed_snow_cut_into_crushed_ice (ICE_DIG owner card 2026-10-25)", () =>
            {
                Assert(C("RM_PackedSnow", "Misc") == RM_GroundClass.Ice, "packed snow is ice ground (supersedes 'packed snow digs as rubble')");
                Assert(C("Ice", "Misc") == RM_GroundClass.Ice, "vanilla Ice is ice ground");
                Assert(C("RM_PackedIce", "Misc") == RM_GroundClass.Ice && C("RM_ChillIceBedrock", "Stone", rock: true) == RM_GroundClass.Ice, "our ice terrains outrank Stone");
                Assert(C("VEE_DenseSnow_Rough", "Misc") == RM_GroundClass.Ice, "VEE dense snow is ice ground");
                Assert(C("Ice", "Misc", water: true) == RM_GroundClass.Water, "water still outranks the ice list");
                Assert(C("Snow", "Misc") != RM_GroundClass.Ice, "loose snow is not ice ground");
                Assert(RM_GroundClassMath.CutYield(RM_GroundClass.Ice, true) == RM_CutSpoil.CrushedIce && RM_GroundClassMath.CutYield(RM_GroundClass.Ice, false) == RM_CutSpoil.CrushedIce, "every ice cut yields crushed ice");
                Assert(RM_GroundClassMath.CreditOf(RM_CutSpoil.CrushedIce) == RM_GroundClassMath.CreditOf(RM_CutSpoil.Gravel) && RM_GroundClassMath.CreditShort(RM_GroundClassMath.CreditOf(RM_CutSpoil.CrushedIce)) == 0, "crushed ice fills like gravel: one funds a notch");
                Assert(RM_GroundClassMath.CreditOf(RM_CutSpoil.Chunk) == 1 && RM_GroundClassMath.CreditOf(RM_CutSpoil.None) == 0, "a chunk is half a notch; nothing is nothing");
                // ICE_YIELD_DECIDE_ONE_CUT_FOUR_NOTCHES (owner by card 2026-10-25, "Match what was dug (1x)")
                Assert(RM_GroundClassMath.CrushedIceUnits == 10000 && RM_GroundClassMath.CrushedIceUnits == RM_Volume.UnitsPerLevel, "one crushed ice melts to the notch its cut removed (1,000 L), not a 1x1 tank");
                Assert(RM_GroundClassMath.MeltUnits(25) == 250000L && RM_GroundClassMath.MeltUnits(0) == 0L, "a stack melts to count x a notch");
            });
            Case("IceMelt_one_pile_at_a_time_cools_the_room (ICE_MELT_TAME_STACK_FLOOD owner card 2026-10-25)", () =>
            {
                // "Melt one pile at a time" + "it lowers the temperature of the room substantially"
                Assert(RM_GroundClassMath.PilesMeltingNow(9999, 10000, 25) == 0 && RM_GroundClassMath.PilesMeltingNow(10000, 10000, 25) == 1, "a pile melts after its own 4 h warm");
                Assert(RM_GroundClassMath.PilesMeltingNow(1000000, 10000, 25) == 1, "never more than one pile at once, however long the stack sat warm");
                Assert(RM_GroundClassMath.PilesMeltingNow(10000, 10000, 0) == 0 && RM_GroundClassMath.PilesMeltingNow(1, 0, 1) == 1, "an empty stack melts nothing; a zero clock still melts one");
                Assert(RM_GroundClassMath.DefaultMeltCoolingPerSecond == 21f, "default: a vanilla cooler's 21 heat/s (Buildings_Temperature.xml Cooler energyPerSecond -21)");
                float rare = RM_GroundClassMath.MeltHeatPerInterval(RM_GroundClassMath.DefaultMeltCoolingPerSecond, 250);
                Assert(System.Math.Abs(rare - (-87.5f)) < 0.01f, "a rare tick (250 ticks = 4.17 s) pushes -87.5: " + rare);
                Assert(RM_GroundClassMath.MeltHeatPerInterval(0f, 250) == 0f && RM_GroundClassMath.MeltHeatPerInterval(1e9f, 250) == -RM_GroundClassMath.MaxMeltCoolingPerSecond * 250 / 60f, "0 is off; the slider top holds");
                Assert(RM_GroundClassMath.ClampMeltCooling(float.NaN) == 21f && RM_GroundClassMath.ClampMeltCooling(-5f) == 0f, "NaN is the default; never warms");
                // a 25-stack in a 5x5 room: one pile's thaw (10,000 ticks) takes 87.5 x 40 = 3,500 heat = -140 C worth of
                // a sealed 25-cell room before the room equalises; held near 0 C, where the thaw stops (substantial, bounded)
                Assert(-rare * (10000 / 250) == 3500f, "one pile's whole thaw takes 3,500 heat out of its room");
                string comp = Src(Path.Combine("Thirst", "RM_ThirstWaterSources.cs"));
                Assert(comp.Contains("MeltLooseOne(") && comp.Contains("PilesMeltingNow(") && comp.Contains("SplitOff(1)") && comp.Contains("GenTemperature.PushHeat(at, map, heat)"), "loose melt takes one off the stack and pushes negative heat");
                Assert(!Regex.IsMatch(comp, @"\(long\)n \* System\.Math\.Max\(0, Props\.unitsPerItem\)"), "the whole-stack flood is gone");
                string ice = File.ReadAllText(Path.Combine(ModRoot, "Defs", "Pits", "ThingDefs", "RM_CrushedIce.xml"));
                Assert(ice.Contains("<unitsPerItem>10000</unitsPerItem>") && ice.Contains("<coolsRoom>true</coolsRoom>"), "crushed ice: a notch each, and it cools");
                Match craft = Regex.Match(ice, @"<defName>RM_MeltCrushedIce</defName>.*?<unitsPerCraft>(\d+)</unitsPerCraft>", RegexOptions.Singleline);
                Assert(craft.Success && int.Parse(craft.Groups[1].Value) == RM_GroundClassMath.CrushedIceUnits, "the melter gives what loose melt gives");
                Assert(Regex.IsMatch(ice, @"<defName>RM_IceMelter</defName>.*?<heatPerTickWhileWorking>0</heatPerTickWhileWorking>", RegexOptions.Singleline), "the melter is room-neutral (its bath pays the melt)");
                Assert(!ice.Contains("4,000 L") && !ice.Contains("40000"), "no player text or number still says a 1x1 tank");
                string mod = Src("RimMandrakeFlowWorksMod.cs");
                Assert(mod.Contains(".Declare(\"iceDigEnabled\", \"iceMeltCoolingPerSecond\")") && mod.Contains("Scribe_Values.Look(ref iceMeltCoolingPerSecond"), "the cooling is a saved Mod Setting under the ice switch");
            });
            Case("IceDig_blue_ice_blocks_go_into_the_melter (owner 2026-10-25)", () =>
            {
                // "the blue ice blocks that could be cut from the nightside should also be able to go into the melter."
                string ice = File.ReadAllText(Path.Combine(ModRoot, "Defs", "Pits", "ThingDefs", "RM_CrushedIce.xml"));
                Match r = Regex.Match(ice, @"<RecipeDef MayRequire=""mandrake\.rm\.bluedesert"">\s*<defName>RM_MeltBlueIceInMelter</defName>(.*?)</RecipeDef>", RegexOptions.Singleline);
                Assert(r.Success, "a melter recipe for RM_BlueIce, loaded only with BlueDesert");
                string b = r.Groups[1].Value;
                Assert(b.Contains("<li>RM_IceMelter</li>") && b.Contains("<li>RM_BlueIce</li>") && b.Contains("RM_MeltRecipeExtension") && b.Contains("<liquid>RM_Liquid_FreshWater</liquid>"), "made at the melter from blue ice into fresh water");
                int count = int.Parse(Regex.Match(b, @"<count>(\d+)</count>").Groups[1].Value);
                int units = int.Parse(Regex.Match(b, @"<unitsPerCraft>(\d+)</unitsPerCraft>").Groups[1].Value);
                string blue = File.ReadAllText(Path.Combine(ModRoot, "..", "BlueDesert", "Defs", "ThingDefs_Items", "RM_BlueIce.xml"));
                int kg = int.Parse(Regex.Match(blue, @"<Mass>(\d+)</Mass>").Groups[1].Value);
                Assert(count == 25 && units == count * kg * RM_Volume.UnitsPerLitre, "1 L per kg of block: " + count + " x " + kg + " kg = " + units + " dL");
                Assert(units == 750, "a craft is 75 L");
            });
            Case("DigFill_hours_of_shovel_work_labour_multiplier (DIG_FILL owner card 2026-10-25)", () =>
            {
                Assert(RM_DigDepthMath.DefaultLabourMultiplier == 4f, "default labour x4");
                Assert(RM_DigDepthMath.LabourWork(RM_DigDepthMath.WorkPerNotch, RM_DigDepthMath.DefaultLabourMultiplier) == 12800, "first soil notch dig = 12,800 work");
                double digH = RM_DigDepthMath.HoursOfWork(12800), fillH = RM_DigDepthMath.HoursOfWork(6400);
                Assert(digH > 2.9 && digH < 3.1 && fillH > 1.4 && fillH < 1.6, "at Mining 1.0: dig 3 h, fill 1.5 h; was " + digH + "/" + fillH);
                Assert(RM_DigDepthMath.LabourWork(1600, 1f) == 1600, "x1 is the legacy work (proof harness runs at x1)");
                Assert(RM_DigDepthMath.LabourWork(1, 0.25f) == 1 && RM_DigDepthMath.LabourWork(int.MaxValue, 8f) == int.MaxValue, "at least 1, never overflows");
                Assert(RM_DigDepthMath.ClampLabour(float.NaN) == 4f && RM_DigDepthMath.ClampLabour(0f) == 0.25f && RM_DigDepthMath.ClampLabour(99f) == 8f, "multiplier clamped 0.25..8");
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
                Assert(disc.Contains("yield == RM_CutSpoil.None || yield == RM_CutSpoil.CrushedIce"), "ice toggle off: an ice cut leaves nothing, never falls through to a stone chunk");
                Assert(disc.Contains("else if (IceCut(map, c, newDepth))") && disc.Contains("bool iceCut = IceCut(map, c, newDepth);") && disc.Contains("&& RM_DeepStone.RockFor(map) != null"), "ice above the deep stone never rolls a stone chunk, every toggle combination");
                Assert(disc.Contains("(rockChunk && (RimMandrakeFlowWorksSettings.digSpoilEnabled || iceCut))") && disc.Contains("if (RimMandrakeFlowWorksSettings.digSpoilEnabled || iceCut)"), "an ice cut above the deep stone drops the finds roll's rock-chunk fallbacks too");
                Assert(disc.Contains("rockChunk && (RimMandrakeFlowWorksSettings.digSpoilEnabled || iceCut)"), "with spoil on, the finds roll drops its rock-chunk fallbacks (dirt makes no chunks)");
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
                // ICE_DIG + DIG_FILL wiring
                Assert(dig.Contains("RM_DigSpoil.IsIceAt(") && dig.Contains("RM_DigDepthMath.LabourWork("), "ice digs at rock speed; dig work carries the labour multiplier");
                Assert(Regex.Matches(fill, @"RM_DigDepthMath\.LabourWork\(").Count >= 1 && fill.Contains("RM_DigSpoil.FillKindOf("), "fill work carries the labour multiplier; credit by material kind");
                Assert(spoil.Contains("RimMandrakeFlowWorks_DefOf.RM_CrushedIce") && disc.Contains("RM_CutSpoil.CrushedIce"), "fillers find crushed ice; ice cuts leave it");
                string raid = Src(Path.Combine("Superdeep", "RM_RaiderTrench.cs"));
                Assert(raid.Contains("RM_RaiderFetchFill") && raid.Contains("FindFillMaterial(") && raid.Contains("CreditAfterFill(") && raid.Contains("RM_DigDepthMath.LabourWork("), "raiders pay: fetch material, spend credit, same labour");
                Assert(raid.Contains("class JobDriver_RM_RaiderFetchFill : JobDriver"), "fetch is its own driver (the trench-work toil layout is untouched: save safety)");
                string ice = File.ReadAllText(Path.Combine(ModRoot, "Defs", "Pits", "ThingDefs", "RM_CrushedIce.xml"));
                Assert(ice.Contains("<defName>RM_CrushedIce</defName>") && ice.Contains("<meltsToLiquid>RM_Liquid_FreshWater</meltsToLiquid>") && ice.Contains("<defName>RM_IceMelter</defName>") && ice.Contains("RM_MeltRecipeExtension"), "crushed ice melts to fresh water; the melter and its recipe exist");
                Assert(Regex.IsMatch(ice, @"<giverClass>WorkGiver_DoBill</giverClass>[\s\S]*?<fixedBillGiverDefs>\s*<li>RM_IceMelter</li>"), "a DoBill work giver names the melter (else no pawn works its bills)");
                string jobs = File.ReadAllText(Path.Combine(ModRoot, "Defs", "Canals", "JobDefs", "FlowWorks_RaiderTrench.xml"));
                Assert(jobs.Contains("<defName>RM_RaiderFetchFill</defName>") && jobs.Contains("JobDriver_RM_RaiderFetchFill"), "raider fetch JobDef");
                string melter = Src("RM_IceMelter.cs");
                Assert(melter.Contains("FillPlan(") && melter.Contains("ReleaseHeld(") && melter.Contains("JobFailReason"), "melter waits for tank room and never loses the water");
                Assert(Src(Path.Combine("Thirst", "RM_ThirstWaterSources.cs")).Contains("ReleaseHeld("), "loose crushed ice melts into the world, conserved");
                Assert(mod.Contains("Scribe_Values.Look(ref iceDigEnabled") && Regex.Matches(mod, "\"iceDigEnabled\"").Count >= 3, "ice toggle saved and registered");
                Assert(mod.Contains("Scribe_Values.Look(ref digLabourMultiplier") && Regex.Matches(mod, "\"digLabourMultiplier\"").Count >= 3, "labour multiplier saved and registered");
                string proj = Src("RimMandrake_FlowWorks.csproj");
                Assert(proj.Contains("RM_IceMelter.cs"), "the melter compiles into the mod");
                Assert(proj.Contains("RM_GroundClassMath.cs") && proj.Contains("RM_DigSpoil.cs"), "both new files compile into the mod");
            });
        }
    }
}
