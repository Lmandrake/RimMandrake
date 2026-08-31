using System.Collections.Generic;
using System.Linq;
using Verse;

namespace SecondaryMineableYield;

public class ModExtension_SecondaryMineableYield : DefModExtension
{
    public float mineableDropChance = 1f;

    public List<SecondaryYieldEntry> entries = new List<SecondaryYieldEntry>();

    private float weightSum = -1f;

    public float GetWeightSum
    {
        get
        {
            if (weightSum < 0f)
            {
                weightSum = entries.Sum((SecondaryYieldEntry t) => t.randomWeight);
            }
            return weightSum;
        }
    }
}
