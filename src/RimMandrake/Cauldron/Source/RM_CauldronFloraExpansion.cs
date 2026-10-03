using System;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.Cauldron
{
    /// <summary>CAULDRON_FLORA_EXPANSION_BUILD_1: kissaveth leaks toxic gas when it is CUT, not only when damaged.
    /// CompGasOnDamage fires on external-violence damage only, and Plant.PlantCollected cuts via
    /// Destroy(KillFinalizeLeavingsOnly), which deals no damage. A leak, never an explosion.</summary>
    public class RM_CompProperties_GasOnCut : CompProperties
    {
        public int gasAmount = 120;

        public RM_CompProperties_GasOnCut()
        {
            compClass = typeof(RM_CompGasOnCut);
        }
    }

    public class RM_CompGasOnCut : ThingComp
    {
        private RM_CompProperties_GasOnCut Props => (RM_CompProperties_GasOnCut)props;

        public override void PostDestroy(DestroyMode mode, Map previousMap)
        {
            base.PostDestroy(mode, previousMap);
            if (mode != DestroyMode.KillFinalizeLeavingsOnly || previousMap == null || !RM_CauldronSettings.floraExpansionEnabled)
            {
                return;
            }
            GasUtility.AddGas(parent.Position, previousMap, GasType.ToxGas, Props.gasAmount);
        }
    }

    /// <summary>With the settings off, the expansion plants leave the wild roster at startup (applies on the next
    /// launch), and fexxil drops its contact-venom comp.</summary>
    [StaticConstructorOnStartup]
    public static class RM_CauldronFloraGate
    {
        private static readonly string[] Expansion =
            { "RM_Tsevrix", "RM_Ixalith", "RM_Fexxil", "RM_Sessarix", "RM_Kissaveth", "RM_Selvix" };

        static RM_CauldronFloraGate()
        {
            if (!RM_CauldronSettings.floraExpansionEnabled)
            {
                BiomeDef biome = DefDatabase<BiomeDef>.GetNamedSilentFail("RM_Cauldron");
                if (biome != null)
                {
                    biome.wildPlants.RemoveAll(r => r.plant != null && Array.IndexOf(Expansion, r.plant.defName) >= 0);
                }
            }
            if (!RM_CauldronSettings.fexxilVenomEnabled)
            {
                ThingDef fexxil = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Fexxil");
                if (fexxil != null)
                {
                    fexxil.comps.RemoveAll(c => c.GetType().Name == "CompProperties_ContactVenom");
                }
            }
        }
    }
}
