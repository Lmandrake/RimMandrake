using Verse;

namespace MentalBreakBlocker;

public class ModExtension_MentalBreakBlocker : DefModExtension
{
    public BlockMentalBreakCause cause = BlockMentalBreakCause.all;

    public bool isWhitelist;

    public bool IsBlocked(bool causedByMood, bool causedByDamage, bool causedByPsycast)
    {
        return RimMandrake.StarWars.Armoury.RSW_GearKernel.IsBlocked((byte)cause, isWhitelist, causedByMood, causedByDamage, causedByPsycast);
    }
}
