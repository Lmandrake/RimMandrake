using RimMandrake.EnvironmentalHazards;
using RimWorld;
using Verse;

namespace RimMandrake.Greentide
{
    // ════════════════════════════════════════════════════════════════════
    // GREENTIDE_STELLOCK_LACE_BUILD_1 — the C# half (defs:
    // Defs/ThingDefs/RM_StellockLace_Items.xml, RM_Greentide_Hediffs.xml,
    // Patches/RM_StellockLace_Patches.xml).
    //
    // The study and the hidden project are NOT here: they run on the shared
    // kit's found-tech study (EnvironmentalHazards RM_FoundTechStudy.cs),
    // gated by the key below, which RM_GreentideMod registers.
    // The bleed stop is NOT here either: it is the hediff stage's own
    // totalBleedFactor 0 (pure XML).
    // ════════════════════════════════════════════════════════════════════
    public static class RM_StellockLace
    {
        public const string GateKey = "Greentide.StellockLace";
        public const string GreentideBiome = "RM_Greentide";
    }

    public class CompProperties_StellockBranchDrop : CompProperties
    {
        public ThingDef branchDef;

        public CompProperties_StellockBranchDrop()
        {
            compClass = typeof(RM_CompStellockBranchDrop);
        }
    }

    // On a tree. A fell is either a pawn cutting it (RimSage 1.6:
    // Plant.PlantCollected is the only caller of
    // Destroy(DestroyMode.KillFinalizeLeavingsOnly) on a plant) or the kit's
    // RM_TreeFallUtility.FellTree (crack, shatter, gnaw — the thurrock —, wind),
    // which destroys with Vanish while FellingNow names the tree. Any other
    // destroy (fire, despawn, a building placed over it) drops nothing.
    public class RM_CompStellockBranchDrop : ThingComp
    {
        public CompProperties_StellockBranchDrop Props => (CompProperties_StellockBranchDrop)props;

        public override void PostDestroy(DestroyMode mode, Map previousMap)
        {
            base.PostDestroy(mode, previousMap);
            if (previousMap == null || Props.branchDef == null || !RM_GreentideSettings.stellockLaceEnabled)
            {
                return;
            }
            bool felled = RM_RulesKernel.Felled(mode == DestroyMode.KillFinalizeLeavingsOnly,
                mode == DestroyMode.Vanish && RM_TreeFallUtility.FellingNow == parent);
            if (!RM_RulesKernel.DropsBranch(true, true, felled, previousMap.Biome != null && previousMap.Biome.defName == RM_StellockLace.GreentideBiome,
                    RM_GreentideSettings.stellockBranchChance, Rand.Value))
            {
                return;
            }
            Thing branch = ThingMaker.MakeThing(Props.branchDef);
            GenPlace.TryPlaceThing(branch, parent.Position, previousMap, ThingPlaceMode.Near);
        }
    }

    // The lace's hold time comes from Mod Settings, not the def's shipped
    // default. SetDuration (vanilla) sets both the total and the remaining.
    public class RM_HediffComp_StellockDuration : HediffComp_Disappears
    {
        public override void CompPostMake()
        {
            base.CompPostMake();
            int ticks = RM_RulesKernel.StellockTicks(RM_GreentideSettings.stellockLaceHours);
            if (ticks > 0)
            {
                SetDuration(ticks);
            }
        }
    }
}
