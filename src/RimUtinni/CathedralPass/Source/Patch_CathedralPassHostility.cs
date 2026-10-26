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

    // CATHEDRALPASS_DECIDE_RETALIATION (delegated: design) — striking a Cathedral machine
    // voids the striker's pass.
    //
    // Without this the exception above made a holder untouchable: drafted and ordered to
    // attack, a holder could take a Sentinel apart while every machine read them as
    // non-hostile. The arc rules the pass "revocable when the relationship cools"
    // (cathedral_concealment_arc_spec.md §3) and the Cathedral's answer to betrayal is
    // "withdrawal, not vengeance" (§0, §6.2): so the answer is the pass's own REVOKE verb on
    // the one pawn who struck, after which vanilla hostility (the mechanoid faction is
    // hostile to the player) lets the machines defend themselves. No goodwill change, no raid,
    // no pursuit, no clan-wide revoke — cooling the whole relationship is the GM layer's
    // REVOKE (CATHEDRAL_REGARD_BLACKBOARD_1), not this patch's.
    //
    // Counts only a deliberate strike: the holder's own shot/blow aimed at THIS machine
    // (DamageInfo.IntendedTarget, or the holder's current job target for melee and thrown
    // attacks, which carry no intended target). A stray round meant for someone else does not
    // void it; neither does extinguishing a burning machine, nor anything done in a mental
    // state (not the player's choice; ForceHostileTo already lets the machine answer that).
    [RimMandrake.Shared.PatchFeature("Patch_CathedralPassRetaliation", typeof(CathedralPassSettings), "cathedralPassEnabled")]
    [HarmonyPatch(typeof(Thing), nameof(Thing.TakeDamage))]
    public static class Patch_CathedralPassRetaliation
    {
        public static void Prefix(Thing __instance, DamageInfo dinfo)
        {
            if (!CathedralPassSettings.cathedralPassEnabled || !(dinfo.Instigator is Pawn holder) || dinfo.Amount <= 0f)
            {
                return;
            }
            if (holder.Faction != Faction.OfPlayer || __instance == null || __instance == holder)
            {
                return;
            }
            Faction mechs = Find.FactionManager?.OfMechanoids;
            if (mechs == null || __instance.Faction != mechs)
            {
                return;
            }
            if (dinfo.Def == null || dinfo.Def == DamageDefOf.Extinguish || holder.InMentalState)
            {
                return;
            }
            Map map = __instance.MapHeld;
            if (map == null || holder.MapHeld != map || !CathedralPass.IsCathedralMap(map))
            {
                return;
            }
            if (!CathedralPass.Holds(holder) || !IsDeliberateStrike(holder, __instance, dinfo))
            {
                return;
            }
            if (CathedralPass.Revoke(holder))
            {
                Messages.Message(
                    "The old sentinels no longer look away from " + holder.LabelShort + ".",
                    new LookTargets(holder),
                    MessageTypeDefOf.NegativeEvent);
            }
        }

        private static bool IsDeliberateStrike(Pawn holder, Thing victim, DamageInfo dinfo)
        {
            Thing intended = dinfo.IntendedTarget;
            if (intended != null)
            {
                return intended == victim;
            }
            return holder.CurJob != null && holder.CurJob.targetA.Thing == victim;
        }
    }
}
