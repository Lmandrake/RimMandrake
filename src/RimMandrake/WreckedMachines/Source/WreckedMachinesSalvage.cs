// The smelter tiers and the crematorium on the one salvage rule (../../_Shared/SalvageRule/RM_SalvageRule.cs).
//
// Smelter: VFE Factory's ResultWorker_Smelt pays ONE material at floor(25%), not the vanilla list. Patches/WreckedMachines_SalvageRule.xml
// puts RM_ResultWorker_SalvageRule on VFEFactory_SmeltApparel and VFEFactory_SmeltWeapon, so our tiers and the donor machine both change.
// A PipeSystem result is one ThingDef and one count, so the worker reports the plan's first stack and the postfix places the rest once
// the process has placed that first stack. Extra ProcessDef results would pay twice: with a full hopper, SpawnOrPushToNet returns before
// ResetProcess and starts again at result 0 on the next tick.
//
// Crematorium: CremateCorpse takes RM_RecipeWorker_CremateSalvage. Toils_Recipe consumes the ingredient after the products are made, and
// RecipeWorker.ConsumeIngredient is the last moment the corpse still holds its gear, so no engine patch is needed here.
using System.Collections.Generic;
using System.Runtime.CompilerServices;
using HarmonyLib;
using PipeSystem;
using RimMandrake.Shared;
using RimWorld;
using VanillaFurnitureExpandedFactory;
using Verse;

namespace RimMandrake.WreckedMachines
{
    public class RM_ResultWorker_SalvageRule : ResultWorker_Smelt
    {
        public override ThingDef GetResult(Process process)
        {
            List<Thing> plan = RM_SalvagePlans.For(process);
            if (plan == null) return base.GetResult(process);
            return plan.Count == 0 ? null : plan[0].def;
        }

        public override int GetCount(Process process)
        {
            List<Thing> plan = RM_SalvagePlans.For(process);
            if (plan == null) return base.GetCount(process);
            return plan.Count == 0 ? 0 : plan[0].stackCount;
        }
    }

    /// <summary>One cycle's yield, held from the worker's first question until it is paid: the rule rolls RoundRandom, and the worker is asked
    /// several times per cycle, so rolling each time could report one material and pay another.</summary>
    internal static class RM_SalvagePlans
    {
        private sealed class Plan
        {
            public ThingDef item, stuff;
            public List<Thing> stacks;
        }

        private static readonly ConditionalWeakTable<Process, Plan> plans = new ConditionalWeakTable<Process, Plan>();

        /// <summary>This process's plan, or null when the donor's rule answers (the setting is off, or nothing is loaded).</summary>
        public static List<Thing> For(Process process)
        {
            if (!WreckedMachinesSettings.smeltersFollowSalvageRule || process == null) return null;
            ThingDef item = process.GetLastStoredIngredient();
            if (item == null) return null;
            ThingDef stuff = process.GetStuffOfLastStoredIngredient();
            if (plans.TryGetValue(process, out Plan held))
            {
                if (held.item == item && held.stuff == stuff) return held.stacks;
                plans.Remove(process);
            }
            var plan = new Plan { item = item, stuff = stuff, stacks = RM_SalvageRule.YieldOf(item, stuff) };
            plans.Add(process, plan);
            return plan.stacks;
        }

        public static void PayRemainder(Process process, ThingWithComps machine, int placedByProcess)
        {
            if (!plans.TryGetValue(process, out Plan held)) return;
            if (!WreckedMachinesSettings.smeltersFollowSalvageRule)
            {
                plans.Remove(process); // switched off during a retry: the donor's rule paid this cycle
                return;
            }
            int planned = held.stacks.Count;
            int owed = RM_SalvageRuleKernel.ExtrasOwed(planned, placedByProcess);
            for (int i = planned - owed; i < planned; i++)
                RM_SalvageRule.Place(held.stacks[i], machine.InteractionCell, machine.Map);
            if (RM_SalvageRuleKernel.CycleOver(planned, placedByProcess)) plans.Remove(process);
        }
    }

    [HarmonyPatch(typeof(Process), nameof(Process.SpawnOrPushToNet))]
    [PatchFeature("Smelter tiers follow the one salvage rule", typeof(WreckedMachinesSettings), nameof(WreckedMachinesSettings.smeltersFollowSalvageRule))]
    internal static class Patch_Process_PaySalvageRemainder
    {
        public static void Postfix(Process __instance, ThingWithComps ___parent, ref List<Thing> outThings)
        {
            RM_SalvagePlans.PayRemainder(__instance, ___parent, outThings?.Count ?? 0);
        }
    }

    public class RM_RecipeWorker_CremateSalvage : RecipeWorker
    {
        public override void ConsumeIngredient(Thing ingredient, RecipeDef recipe, Map map)
        {
            if (RM_SalvageRuleKernel.CremationPays(WreckedMachinesSettings.cremateWithoutStripping, ingredient is Corpse))
            {
                IntVec3 cell = ingredient.PositionHeld;
                foreach (Thing gear in GearOn(((Corpse)ingredient).InnerPawn))
                    foreach (Thing stack in RM_SalvageRule.YieldOf(gear))
                        RM_SalvageRule.Place(stack, cell, map);
            }
            base.ConsumeIngredient(ingredient, recipe, map);
        }

        private static IEnumerable<Thing> GearOn(Pawn pawn)
        {
            if (pawn?.apparel != null) foreach (Apparel worn in pawn.apparel.WornApparel) yield return worn;
            if (pawn?.equipment != null) foreach (ThingWithComps held in pawn.equipment.AllEquipmentListForReading) yield return held;
            if (pawn?.inventory != null) foreach (Thing carried in pawn.inventory.innerContainer) yield return carried;
        }
    }
}
