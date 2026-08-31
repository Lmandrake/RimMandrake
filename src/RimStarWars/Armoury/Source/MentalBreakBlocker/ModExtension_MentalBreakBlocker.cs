using Verse;

namespace MentalBreakBlocker;

public class ModExtension_MentalBreakBlocker : DefModExtension
{
    public BlockMentalBreakCause cause = BlockMentalBreakCause.all;

    public bool isWhitelist;

    public bool IsBlocked(bool causedByMood, bool causedByDamage, bool causedByPsycast)
    {
        byte b = (byte)((causedByMood ? 1 : 0) | (causedByDamage ? 2 : 0) | (causedByPsycast ? 4 : 0));
        return ((byte)cause & b) > 0 ^ isWhitelist;
    }
}
