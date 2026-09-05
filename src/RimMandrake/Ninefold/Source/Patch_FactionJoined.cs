using RimWorld;
using Verse;
using HarmonyLib;

namespace RimMandrake.Ninefold
{
    // NINEFOLD_MISSING_EVENT_HOOKS_1 (broad pass). divine_satiation_engine.md:
    // a fleshy humanlike joining the clan grows the household -> Oomo (§3③
    // "childbirth ... the household grew"; a recruit is another mouth in the
    // family). A tamed animal is the patient hand the beast learns to trust
    // -> Ishko (§3① "the patience to tame an animal, the still hand"), and a
    // fertile reproducing beast pleases Oomo too (§3③).
    //
    // Verified against decompiled source (RimSage): Pawn.SetFaction is vanilla's
    // single choke for a pawn changing allegiance. This is a SIBLING observer to
    // Patch_DroidOnline, which already handles the non-flesh humanlike (droid)
    // case -> Ohm; this file deliberately skips that branch so a droid is not
    // double-counted, and covers the flesh-humanlike (recruit) and animal (tame)
    // branches it leaves untouched.
    [HarmonyPatch(typeof(Pawn), nameof(Pawn.SetFaction))]
    public static class Patch_FactionJoined
    {
        [HarmonyPostfix]
        public static void Postfix(Pawn __instance, Faction newFaction)
        {
            if (newFaction != Faction.OfPlayer) return;
            if (__instance?.RaceProps == null) return;

            GameComponent_Ninefold comp = GameComponent_Ninefold.Instance;
            if (comp == null) return;

            if (__instance.RaceProps.Animal)
            {
                comp.ApplyDelta(God.Ishko, EventMagnitude.Small,
                    "a beast tamed by the still hand: " + __instance.LabelShortCap);
                comp.ApplyDelta(God.Oomo, EventMagnitude.Small, "a fertile beast for the family");
                return;
            }

            // Flesh humanlike = a recruit/new clan member. Non-flesh humanlike
            // (droid) is Patch_DroidOnline's job -> Ohm; do not touch it here.
            if (__instance.RaceProps.Humanlike && __instance.RaceProps.IsFlesh)
            {
                comp.ApplyDelta(God.Oomo, EventMagnitude.Medium,
                    "the household grew: " + __instance.LabelShortCap);
            }
        }
    }
}
