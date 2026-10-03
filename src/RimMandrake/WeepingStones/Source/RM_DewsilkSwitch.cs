using RimWorld;
using System.Linq;
using Verse;

namespace RimMandrake.WeepingStones
{
    // WEEPINGSTONES_DEWSILK_COCOON_1: the Mod Settings switch for the cocoon harvest. Off removes the vanilla
    // Shearable comp from RM_Mirrik once defs are loaded, so tamed mirrik yield nothing; the items and the
    // spinning recipe stay as inert defs. Read once per launch (a change applies on the next start).
    [StaticConstructorOnStartup]
    public static class RM_DewsilkSwitch
    {
        static RM_DewsilkSwitch()
        {
            if (RM_WeepingStonesSettings.dewsilkEnabled) return;
            ThingDef mirrik = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Mirrik");
            if (mirrik?.comps == null) return;
            mirrik.comps.RemoveAll(c => c is CompProperties_Shearable);
        }
    }
}
