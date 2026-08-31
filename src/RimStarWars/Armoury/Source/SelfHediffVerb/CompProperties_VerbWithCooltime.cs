using System.Collections.Generic;
using Verse;

namespace SelfHediffVerb;

public class CompProperties_VerbWithCooltime : CompProperties
{
    public int ticksCooldown = 60;

    public CompProperties_VerbWithCooltime()
    {
        compClass = typeof(CompVerbWithCooltime);
    }

    public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
    {
        foreach (string item in base.ConfigErrors(parentDef))
        {
            yield return item;
        }
        if (parentDef.tickerType != TickerType.Normal)
        {
            yield return parentDef.defName + "'s <tickerType> must be Normal";
        }
    }
}
