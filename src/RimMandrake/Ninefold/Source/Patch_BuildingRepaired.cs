using RimWorld;
using Verse;
using HarmonyLib;

namespace RimMandrake.Ninefold
{
    // design/Jawa/divine_satiation_engine.md §8b.A: "Repair a damaged
    // building/ship part (not a skill -- a designation) -> ↑Rekko (large --
    // his core sacrament), ↑Ohm (small, the machine rewoken)."
    //
    // Verified against decompiled source (RimSage):
    // `ListerBuildingsRepairable.Notify_BuildingRepaired(Building)`
    // (Source/RimWorld/ListerBuildingsRepairable.cs:48) is called from
    // `JobDriver_Repair`'s per-tick repair toil EVERY time HitPoints ticks
    // up by one -- not just on completion -- so this hook gates on
    // `b.HitPoints == b.MaxHitPoints` to fire once, on the tick the
    // building reaches full health, rather than spamming a delta per
    // repair-tick.
    [HarmonyPatch(typeof(ListerBuildingsRepairable), nameof(ListerBuildingsRepairable.Notify_BuildingRepaired))]
    public static class Patch_BuildingRepaired
    {
        [HarmonyPostfix]
        public static void Postfix(Building b)
        {
            if (b == null || b.Faction != Faction.OfPlayer) return;
            if (b.HitPoints != b.MaxHitPoints) return;

            GameComponent_Ninefold comp = GameComponent_Ninefold.Instance;
            if (comp == null) return;

            comp.ApplyDelta(God.Rekko, EventMagnitude.Large,
                "repaired to full health: " + b.def.defName);

            // "the machine rewoken" is narrowed to powered buildings
            // (CompPowerTrader) -- a repaired dumb wall is Rekko's alone,
            // not Ohm's.
            if (b.TryGetComp<CompPowerTrader>() != null)
            {
                comp.ApplyDelta(God.Ohm, EventMagnitude.Small,
                    "the machine rewoken: " + b.def.defName);
            }
        }
    }
}
