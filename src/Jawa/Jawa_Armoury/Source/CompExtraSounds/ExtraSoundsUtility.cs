using System.Collections.Generic;
using Verse;

namespace CompExtraSounds;

public static class ExtraSoundsUtility
{
    internal static CompExtraSounds GetCompExtraSounds(this ThingWithComps thing)
    {
        List<ThingComp> allComps = thing.AllComps;
        for (int i = 0; i < allComps.Count; i++)
        {
            if (allComps[i] is CompExtraSounds result)
            {
                return result;
            }
        }
        return null;
    }

    public static DefModExtension_ExtraSounds GetModExtensionExtraSounds(this Def def)
    {
        List<DefModExtension> modExtensions = def.modExtensions;
        if (modExtensions == null)
        {
            return null;
        }
        for (int i = 0; i < modExtensions.Count; i++)
        {
            if (modExtensions[i] is DefModExtension_ExtraSounds result)
            {
                return result;
            }
        }
        return null;
    }
}
