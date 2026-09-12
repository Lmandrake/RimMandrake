using RimWorld;

namespace RimMandrake.DivingInteraction
{
    // Overrides MoodOffset so the settings slider (communeMoodOffset) is a
    // live tunable, not a placebo next to a static XML value — the XML
    // stage still carries the shipped default for the tooltip preview.
    public class RM_Thought_CommunedWithDeep : Thought_Memory
    {
        public override float MoodOffset()
        {
            return RM_DivingSettings.communeMoodOffset;
        }
    }
}
