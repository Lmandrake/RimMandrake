using RimWorld;
using Verse;

namespace RimMandrake.StructureInjections
{
    // TILE_STRUCTURE_DESIGNS_1 whisper subsystem, batch 1. The whisper
    // roster (structure_injection_roster.md WHISPER #12, "Never Was",
    // Ishko, RARE) names ONE legal whisper that injects nothing: "Ishko's
    // authored-nothing is a legal whisper... 'Nothing is here. He is quite
    // sure you understand how rare that is.'"
    //
    // The whisper selector mechanism itself is vanilla: a TileMutatorDef's
    // extraGenSteps entry pointing at a GenStepDef whose genStep is
    // Verse.GenStep_RandomSelector (RimSage-confirmed: List<
    // RandomGenStepSelectorOption>, RandomElementByWeight, then runs the
    // winning option's own genStep) - the exact mechanism structure_
    // injection_roster.md §0b names ("GenStep_RandomSelector (Verse,
    // weighted options) gives whisper variety natively"). No custom C# is
    // needed for the roll itself. This class is the one option vanilla's
    // selector cannot express on its own: "do nothing, deliberately."
    public class GenStep_Whisper_NoOp : GenStep
    {
        // Distinct from every other GenStep's SeedPart in this mod
        // (GenStep_RimplacePlan uses 8462013) - arbitrary, stable.
        public override int SeedPart => 8462014;

        public override void Generate(Map map, GenStepParams parms)
        {
            // MOD_OPTIONS_RETROFIT_1: master off switch, same as
            // GenStep_RimplacePlan - a map that already generated with
            // this rolled is never touched by a later settings change.
            if (!RM_StructureInjectionsSettings.enabled) return;

            // Deliberately empty. The roster's own trust law still applies
            // ("a whisper announces itself in the landing letter's last
            // beat") - that hook is sacred_sites_pass_1.md's own named
            // future item (§5: "the engine hook that reads a tile and
            // injects judgment text at landing... files as its own item
            // when the owner calls it"), not this GenStep's job. This one
            // logs its own selection so that future hook has something to
            // read without this class changing.
            Log.Message("[RimMandrake.StructureInjections] whisper rolled: Never Was - nothing injected.");
        }
    }
}
