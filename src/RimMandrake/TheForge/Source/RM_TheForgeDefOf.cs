using RimWorld;
using Verse;

namespace RimMandrake.TheForge
{
    // FORGE_GPT_ENRICHMENT_1. Every def here ships in this mod's own Defs/.
    [DefOf]
    public static class RM_TheForgeDefOf
    {
        // §1 floatstone keelwork / §2 spunstone bonding
        public static ThingDef RM_FloatstoneKeelBrace;
        public static ThingDef RM_FloatstoneGarden;
        public static ResearchProjectDef RM_SpunstoneBonding;

        // §3 the four voices
        public static SoundDef RM_ForgeVoice_StillThrob;
        public static SoundDef RM_ForgeVoice_VentCough;
        public static SoundDef RM_ForgeVoice_RainHiss;
        public static SoundDef RM_ForgeVoice_BasaltTick;
        public static SoundDef RM_ForgeVoice_GlassSing;
        public static SoundDef RM_ForgeVoice_CrackPulse;
        public static SoundDef RM_ForgeVoice_PhaseStinger;
        public static SoundDef RM_ForgeVoice_KeelRing;

        // §7 the dhuvvox clock
        public static SoundDef RM_DhuvvoxNoduleClick;
        public static SoundDef RM_DhuvvoxScuttle;
        public static HediffDef RM_DhuvvoxRunSlowing;

        static RM_TheForgeDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_TheForgeDefOf));
        }
    }
}
