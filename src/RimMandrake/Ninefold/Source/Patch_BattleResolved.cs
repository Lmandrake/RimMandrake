using RimWorld;
using Verse;
using HarmonyLib;

namespace RimMandrake.Ninefold
{
    // NINEFOLD_MISSING_EVENT_HOOKS_1. design/Jawa/divine_satiation_engine.md:
    // "RISES with every violent battle... hardens the clan but breeds
    // exposure/doom" (Sh'kaar, §3⑧-reframe); line 722-725 distinguishes
    // ranged (small) from melee (large), but that split needs per-verb
    // tracking this pass does not build -- every violent death counts as one
    // event, Medium, a deliberate first-pass simplification (matches
    // EventMagnitude's own "UNTUNED, first-pass ordering" status).
    //
    // Verified against decompiled source (RimSage): `Pawn.Kill(DamageInfo?
    // dinfo, Hediff exactCulprit)` is the single choke point every pawn death
    // passes through. `dinfo.HasValue` is true for a violent death (shot,
    // stabbed, exploded, mauled...) and false/absent for a peaceful one (old
    // age, disease with no attacker, scripted death) -- the standard
    // modding-wide proxy for "died violently" at this exact API.
    [HarmonyPatch(typeof(Pawn), nameof(Pawn.Kill))]
    public static class Patch_BattleResolved
    {
        [HarmonyPostfix]
        public static void Postfix(Pawn __instance, DamageInfo? dinfo)
        {
            if (!dinfo.HasValue) return; // peaceful death - not Sh'kaar's domain

            GameComponent_Ninefold comp = GameComponent_Ninefold.Instance;
            if (comp == null) return;

            comp.ApplyDelta(God.Shkaar, EventMagnitude.Medium,
                "violent death: " + __instance.LabelCap);
        }
    }
}
