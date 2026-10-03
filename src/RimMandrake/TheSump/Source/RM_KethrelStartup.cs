using System.Collections.Generic;
using System.Reflection;
using RimWorld;
using Verse;

namespace RimMandrake.TheSump
{
    /// <summary>SUMP_KETHREL_BUILD_1: applies the kethrel density setting to the Sump's wild roster at startup.</summary>
    [StaticConstructorOnStartup]
    public static class RM_KethrelStartup
    {
        static RM_KethrelStartup()
        {
            BiomeDef sump = DefDatabase<BiomeDef>.GetNamedSilentFail("RM_TheSump");
            PawnKindDef kethrel = DefDatabase<PawnKindDef>.GetNamedSilentFail("RM_Kethrel");
            if (sump == null || kethrel == null)
            {
                return;
            }
            // wildAnimals is a private field of BiomeDef; read by reflection (the engine's own cached
            // commonality lookups are built lazily after startup, so editing the records here is early enough).
            FieldInfo field = typeof(BiomeDef).GetField("wildAnimals", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public);
            List<BiomeAnimalRecord> rows = field?.GetValue(sump) as List<BiomeAnimalRecord>;
            if (rows == null)
            {
                Log.Warning("[RM Sump] kethrel density: BiomeDef.wildAnimals not readable, density setting not applied.");
                return;
            }
            float f = RM_TheSumpSettings.kethrelDensity;
            if (f <= 0.001f)
            {
                rows.RemoveAll(r => r.animal == kethrel);
                return;
            }
            foreach (BiomeAnimalRecord r in rows)
            {
                if (r.animal == kethrel)
                {
                    r.commonality *= f;
                }
            }
        }
    }
}
