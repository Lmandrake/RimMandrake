using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.Utinni.CathedralPass
{
    // CATHEDRAL_MECHANOID_PASS_VERBS_1 — the one hostility exception.
    //
    // Postfix on GenHostility.HostileTo(Thing, Thing). That overload is what target
    // selection asks: AttackTargetsCache.GetPotentialTargetsFor filters every
    // candidate through thing.HostileTo(item.Thing) (decompiled 1.6), and mech
    // turrets and pawns both search through it. Faction-level hostility is NOT
    // touched — the mechanoid faction stays hostile to the player; only the
    // thing-to-thing read between a faction-13 machine and a pass-holder flips.
    //
    // Narrow by construction, cheapest test first:
    //   * only when vanilla already said hostile and the setting is on;
    //   * one side must belong to Faction.OfMechanoids (faction 13) — no other
    //     mechanoid faction, no other faction at all;
    //   * the other side must be a player-faction pawn carrying RUT_CathedralPass;
    //   * the machine must stand on a Rust Cathedral map (CathedralPass.IsCathedralMap)
    //     and the holder on that same map — off Cathedral ground nothing changes;
    //   * a mental state that FORCES hostility on either side still wins (a berserk
    //     holder or a berserk machine is hostile as vanilla says).
    // Symmetric, because HostileTo is read as symmetric throughout the engine: a
    // one-way exception would leave the clan auto-firing on machines that ignore them.
    [RimMandrake.Shared.PatchFeature("Patch_CathedralPassHostility", typeof(CathedralPassSettings), "cathedralPassEnabled")]
    [HarmonyPatch(typeof(GenHostility), nameof(GenHostility.HostileTo), new[] { typeof(Thing), typeof(Thing) })]
    public static class Patch_CathedralPassHostility
    {
        public static void Postfix(Thing a, Thing b, ref bool __result)
        {
            if (!__result || !CathedralPassSettings.cathedralPassEnabled || a == null || b == null)
            {
                return;
            }
            Faction mechs = Find.FactionManager?.OfMechanoids;
            if (mechs == null)
            {
                return;
            }
            if (a.Faction == mechs)
            {
                if (PassApplies(a, b))
                {
                    __result = false;
                }
            }
            else if (b.Faction == mechs)
            {
                if (PassApplies(b, a))
                {
                    __result = false;
                }
            }
        }

        private static bool PassApplies(Thing machine, Thing other)
        {
            if (!(other is Pawn holder) || holder.Faction != Faction.OfPlayer)
            {
                return false;
            }
            Map map = machine.MapHeld;
            if (map == null || holder.MapHeld != map || !CathedralPass.IsCathedralMap(map))
            {
                return false;
            }
            if (!CathedralPass.Holds(holder))
            {
                return false;
            }
            if (holder.MentalState != null && holder.MentalState.ForceHostileTo(machine))
            {
                return false;
            }
            if (machine is Pawn mechPawn && mechPawn.MentalState != null && mechPawn.MentalState.ForceHostileTo(holder))
            {
                return false;
            }
            return true;
        }
    }
}
