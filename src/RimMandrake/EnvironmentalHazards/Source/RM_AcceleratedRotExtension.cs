using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // ROT_DECAY_HARVEST_1. Marker extension: a BiomeDef carries this to opt
    // its maps into RM_MapComponent_AcceleratedRot at all — same "presence is
    // the opt-in" idiom RM_LivingBoleBiomeExtension already uses in this
    // assembly. No fields: the actual item/corpse rate multipliers are Mod
    // Settings (RM_EnvironmentalHazardsSettings.acceleratedRotItemMultiplier /
    // acceleratedRotCorpseMultiplier), not per-biome, because a player who
    // finds this kit's rot too fast/slow is tuning a KIT-wide dial, same
    // posture as every other multiplier in RM_EnvironmentalHazardsMod.cs.
    //
    //   <BiomeDef>
    //     <defName>RUT_TheRot</defName>
    //     ...
    //     <modExtensions>
    //       <li Class="RimMandrake.EnvironmentalHazards.RM_AcceleratedRotExtension" />
    //     </modExtensions>
    //   </BiomeDef>
    public class RM_AcceleratedRotExtension : DefModExtension
    {
    }
}
