using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.DivingInteraction
{
    // ════════════════════════════════════════════════════════════════════
    // CHILL_GARDEN_DEFENSE_1 — the two real engine hook points that feed
    // RM_MapComponent_ChillGardenDefense.RegisterOffense, read off the
    // decompiled 1.6 source (RimSage), not assumed:
    //
    // 1) Plant.PlantCollected(Pawn, PlantDestructionMode) — the single
    //    method every harvest job (and animal foraging) routes through
    //    when a plant is actually taken. No wild plants exist on RM_TheChill
    //    today (its own header: "no <wildPlants>, every species is
    //    OmnivoreAnimal") so this postfix is currently inert on a live map —
    //    it exists so CHILL_FLORA_BUILD_1's Fuselight (or anything else
    //    planted/growing down here later) is covered for free, with no
    //    further wiring.
    //
    // 2) Thing.PostApplyDamage(DamageInfo, float) — the one place damage
    //    has already been fully applied (a Pawn's Dead flag is correctly
    //    set by this point) for ANY Thing on ANY map, covering both "killing
    //    floor life" and "directed heat damage" in one patch. Both checks
    //    below filter to dinfo.Instigator.Faction == Faction.OfPlayer — an
    //    offense is something the PLAYER did to the garden, never Iliss
    //    eating an Oddu, never a Tarnn's own roused zap (which is thrown
    //    with instigator: null besides, see RM_CompTarnnRoused.cs) re-
    //    triggering this very system.
    //
    // "Directed heat damage" (item's own hint, confirmed by reading
    // DamageDefOf.cs): DamageDefOf.Flame or DamageDefOf.Burn specifically —
    // NOT DamageDefOf.ElectricalBurn, which is this mod's OWN arc/zap damage
    // type and must never feed back into the accumulator that spawned it.
    // Fire itself cannot ignite down here (CHILL_FIRE_BAN_1), but a thrown
    // incendiary or a beam/laser weapon still applies its initial Flame/Burn
    // damage instance on impact before the (blocked) ignition attempt — that
    // impact is what this counts.
    // ════════════════════════════════════════════════════════════════════
    public static class RM_ChillGardenFloorLife
    {
        // Every species RM_TheChill.xml's <wildAnimals> lists — MEASURED
        // (GenStep_SeaFloorFauna.cs's own header) to be the ONLY roster a
        // sea BiomeDef's wildAnimals ever feeds, and that GenStep runs only
        // on the Chill's own seabed pocket map. All ten are "the garden".
        public static readonly HashSet<string> DefNames = new HashSet<string>
        {
            "RM_Fessu", "RM_Krellik", "RM_Oddu", "RM_Oovu", "RM_Iliss", "RM_Tarnn",
            "RM_Heemin", "RM_Oovanam", "RM_Hoolen", "RM_Vaunoom",
        };

        public static bool IsFloorLife(Pawn p)
        {
            return p?.def != null && DefNames.Contains(p.def.defName);
        }
    }

    [HarmonyPatch(typeof(Plant), nameof(Plant.PlantCollected))]
    public static class Patch_Plant_PlantCollected
    {
        public static void Postfix(Plant __instance, Pawn by, PlantDestructionMode plantDestructionMode)
        {
            if (by?.Faction != Faction.OfPlayer)
            {
                return;
            }
            Map map = __instance.Map ?? by.Map;
            if (map == null || !RM_ChillFireGate.IsChillSeabedMap(map))
            {
                return;
            }
            map.GetComponent<RM_MapComponent_ChillGardenDefense>()
                ?.RegisterOffense(RM_GardenOffenseKind.Harvest, by, __instance.Position);
        }
    }

    [HarmonyPatch(typeof(Thing), nameof(Thing.PostApplyDamage))]
    public static class Patch_Thing_PostApplyDamage
    {
        public static void Postfix(Thing __instance, DamageInfo dinfo, float totalDamageDealt)
        {
            Map map = __instance?.Map;
            if (map == null || !RM_ChillFireGate.IsChillSeabedMap(map))
            {
                return;
            }
            if (dinfo.Instigator == null || dinfo.Instigator.Faction != Faction.OfPlayer)
            {
                return; // "offenses against the garden" — a player act, never wildlife-on-wildlife or this mod's own punishment damage
            }

            if (__instance is Pawn victim && victim.Dead && RM_ChillGardenFloorLife.IsFloorLife(victim))
            {
                map.GetComponent<RM_MapComponent_ChillGardenDefense>()
                    ?.RegisterOffense(RM_GardenOffenseKind.Kill, dinfo.Instigator as Pawn, victim.Position);
                return;
            }

            bool isDirectedHeat = dinfo.Def == DamageDefOf.Flame || dinfo.Def == DamageDefOf.Burn;
            if (!isDirectedHeat)
            {
                return;
            }
            bool isGardenLife = __instance is Plant || (__instance is Pawn heatVictim && RM_ChillGardenFloorLife.IsFloorLife(heatVictim));
            if (!isGardenLife)
            {
                return;
            }
            map.GetComponent<RM_MapComponent_ChillGardenDefense>()
                ?.RegisterOffense(RM_GardenOffenseKind.HeatDamage, dinfo.Instigator as Pawn, __instance.Position);
        }
    }
}
