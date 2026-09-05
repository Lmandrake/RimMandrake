using RimWorld;
using Verse;
using HarmonyLib;

namespace RimMandrake.Ninefold
{
    // NINEFOLD_HOOK_DOWNS_NOT_JUST_DEATHS_1. divine_satiation_engine.md §3⑧:
    // "Fight ANY violent battle at all -> Sh'kaar climbs the battle-escalation
    // meter" -- the meter is meant to track FIGHTS, not corpses, but the only
    // hook feeding it (Patch_BattleResolved, on Pawn.Kill) sits on the rare
    // outcome. Most RimWorld fights end with someone DOWNED, not dead, so the
    // escalation meter was silently missing the overwhelmingly common case.
    // This sibling hook fires the same battle-escalation credit on a downing.
    //
    // Verified against decompiled source (RimSage): Pawn_HealthTracker.MakeDowned
    // (DamageInfo? dinfo, Hediff hediff) is the single private choke point every
    // downing passes through -- called once, from CheckForStateChange(), the
    // instant ShouldBeDowned() flips true and the death-on-downed roll (if any)
    // did not instead kill the pawn outright. dinfo is the exact same nullable
    // DamageInfo used at the Pawn.Kill choke (Patch_BattleResolved,
    // Patch_KillManner) and is populated only when the state-change was driven
    // by real damage; a hediff-only downing (illness, heatstroke, childbirth,
    // old-age collapse) calls MakeDowned with dinfo: null. That is the same
    // "violent vs peaceful" proxy the Kill hooks already rely on, so gating on
    // dinfo.HasValue costs nothing extra and correctly excludes non-violent
    // downing from Sh'kaar's domain.
    //
    // What this choke point does NOT cheaply expose: whether the instigator was
    // actually hostile. A down from friendly fire, a training accident, or a
    // self-inflicted mishap still carries a non-null dinfo and would read as
    // "violent" here -- the same blind spot Patch_BattleResolved already
    // accepts at the Kill choke (dinfo.HasValue, nothing more). Documented
    // rather than silently over/under-crediting on a distinction this method
    // cannot see without walking dinfo.Instigator's faction relative to the
    // downed pawn, which the existing sibling hooks don't do either -- kept
    // consistent rather than inventing a stricter rule only this hook obeys.
    //
    // MakeDowned is private -- HarmonyPatch by string name, and __instance's
    // private `pawn` field is reached the standard Harmony way via a
    // "___pawn" postfix parameter rather than a direct (inaccessible) member
    // access.
    //
    // Double-credit vs the Kill hooks: a down and a later kill are NOT the same
    // event (CheckForStateChange only ever calls Kill() OR MakeDowned() for a
    // single damage application, never both -- the death-on-downed roll decides
    // which one happens). A pawn downed now and finished off later fires this
    // hook once and a Kill hook once, at different times, for different fights'
    // worth of tension. The design doc frames the meter as "any violent battle",
    // not "battles that produced a corpse", so both are allowed to credit
    // independently -- but a down alone credits at Small while an actual kill
    // still credits Medium (Patch_BattleResolved) plus its own Small manner
    // bonus (Patch_KillManner), so a fight that ends in death still gorges
    // Sh'kaar harder than one that merely ends in a down, matching "melee above
    // all, a purest war" scaling with lethality while finally making the common
    // down-only outcome visible to the meter at all.
    [HarmonyPatch(typeof(Pawn_HealthTracker), "MakeDowned")]
    public static class Patch_PawnDowned
    {
        [HarmonyPostfix]
        public static void Postfix(DamageInfo? dinfo, Pawn ___pawn)
        {
            if (!dinfo.HasValue) return; // hediff/illness-only downing - not violence

            GameComponent_Ninefold comp = GameComponent_Ninefold.Instance;
            if (comp == null) return;

            comp.ApplyDelta(God.Shkaar, EventMagnitude.Small,
                "downed in battle: " + ___pawn.LabelCap);
        }
    }
}
