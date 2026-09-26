using Verse;

namespace RimMandrake.FeverWood
{
    // FEVERWOOD_DIANOGA_PRISON_1. Plain CompProperties wrapper — no tunable
    // fields, the comp is armed at runtime by RM_CompCapturedSpecimen.Escape()
    // via Notify_JustEscaped(), never by XML. Carried on both
    // RM_Sekkulaath_Juvenile and (once the Star Wars swap patch retargets
    // the tank's occupant string) RSW_Dianoga, via a small patch adding this
    // same comp to that def too — see
    // RSW_SekkulaathTank_DianogaSwap.xml.
    public class RM_CompProperties_EscapedCaptive : CompProperties
    {
        public RM_CompProperties_EscapedCaptive()
        {
            compClass = typeof(RM_CompEscapedCaptive);
        }
    }
}
