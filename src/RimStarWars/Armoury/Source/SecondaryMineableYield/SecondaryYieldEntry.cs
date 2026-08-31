using UnityEngine;
using Verse;

namespace SecondaryMineableYield;

public class SecondaryYieldEntry
{
    public ThingDef mineableThing;

    public int mineableYield = 1;

    public float mineableScatterCommonality;

    public IntRange mineableScatterLumpSizeRange = new IntRange(20, 40);

    public bool mineableYieldWasteable = true;

    public float randomWeight = 1f;

    public int EffectiveMineableYield => Mathf.RoundToInt(mineableYield * Find.Storyteller.difficulty.mineYieldFactor);
}
