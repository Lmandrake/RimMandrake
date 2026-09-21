using RimWorld;
using Verse;

namespace RimMandrake.GelatinousSlime
{
    // ════════════════════════════════════════════════════════════════════
    // RM_Verb_MeleeEngulf — the swallow, as a melee verb.
    //
    // TITANOSLIME_SLIME_BIOME_1 / spec §4.1. Wired by ManeuverDef RM_Engulf
    // (Defs/Maneuvers/Engulf.xml) onto the race's "engulfing mass" tool.
    //
    // 🔑 A VERB, NOT AN ABILITY, AND THAT IS THE WHOLE POINT. Vanilla's
    // devourer swallows through an AbilityDef leap chosen by an always-violent
    // entity's custom think tree, all of which is Anomaly content. A melee
    // tool is reached by the ORDINARY animal think tree: JobDriver_PredatorHunt
    // calls pawn.meleeVerbs.TryMeleeAttack (MEASURED), melee verb selection
    // weights the tools by chanceFactor, and when this one is picked and hits,
    // the slime swallows instead of hitting. Nothing about the AI is custom.
    //
    // Seam MEASURED this build against RimWorld/Verb_MeleeAttackDamage.cs:
    //   protected override DamageWorker.DamageResult ApplyMeleeDamageToTarget(LocalTargetInfo target)
    // Returning an empty DamageResult is how "the hit landed and did no damage"
    // is expressed; base.ApplyMeleeDamageToTarget is the ordinary slam, which
    // is what happens whenever the gate in RM_CompEngulfer.CanEngulf fails
    // (mechanoid, too big, already held, capacity full, or the setting off).
    // ════════════════════════════════════════════════════════════════════
    public class RM_Verb_MeleeEngulf : Verb_MeleeAttackDamage
    {
        protected override DamageWorker.DamageResult ApplyMeleeDamageToTarget(LocalTargetInfo target)
        {
            Pawn caster = CasterPawn;
            Pawn victim = target.Thing as Pawn;
            if (caster != null && victim != null)
            {
                RM_CompEngulfer comp = caster.TryGetComp<RM_CompEngulfer>();
                if (comp != null && comp.CanEngulf(victim))
                {
                    comp.Engulf(victim);
                    return new DamageWorker.DamageResult();
                }
            }
            return base.ApplyMeleeDamageToTarget(target);
        }
    }
}
