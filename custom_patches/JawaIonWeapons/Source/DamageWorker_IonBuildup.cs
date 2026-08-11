using System.Collections.Generic;
using Verse;

namespace JawaIonWeapons
{
    /// <summary>
    /// Applies an accumulating hediff on hit WITHOUT ever dealing an injury.
    ///
    /// WHY THIS EXISTS
    /// ===============
    /// The Jawa ion blaster is a capture weapon: it must never wound or kill a
    /// fleshy target, but it must wear one down until they collapse alive. No
    /// stock damage worker can do both.
    ///
    ///   * The StunBase family (which JawaIon_Damage belongs to) cannot kill,
    ///     but never reaches DamageWorker_AddInjury.ApplyDamageToPart -- and
    ///     that method is the ONLY thing in the game that reads a DamageDef's
    ///     additionalHediffs. Every Core def using additionalHediffs is an
    ///     injury damage in Damages_MeleeWeapon.xml. So the buildup block in
    ///     DamageDefs_JawaIon.xml has never once executed.
    ///   * DamageWorker_AddInjury does read additionalHediffs, but it deals a
    ///     real injury, and any injury can kill. That loses the whole point.
    ///
    /// This worker closes that gap: base.Apply for the impact sound and vanilla
    /// bookkeeping, then the hediff applied by hand.
    ///
    /// WHY SUBCLASSING DamageWorker IS SAFE FOR THE MECH HALF  [verified from IL]
    /// =========================================================================
    /// Verse.Thing::TakeDamage calls dinfo.Def.Worker.Apply and never reads
    /// causeStun; neither does Pawn::PostApplyDamage. Stun is resolved outside
    /// the worker entirely. Vanilla EMP proves it -- EMP declares no workerClass
    /// at all, so it runs on the base DamageWorker and still stuns. Therefore
    /// deriving from DamageWorker and calling base.Apply leaves the EMP-style
    /// stun on mechanoids and droids exactly as it is today.
    ///
    /// Verse.DamageWorker::Apply itself, with harmsHealth=false, does nothing
    /// but play the impact sound: its only other branch is guarded by
    /// `useHitPoints AND harmsHealth`. So nothing is lost by calling it and the
    /// impact sound is gained.
    ///
    /// TUNING LIVES IN XML
    /// ===================
    /// Severity is read from the DamageDef's own additionalHediffs entries
    /// rather than hardcoded, so that block stops being dead weight and stays
    /// the tuning surface. severityFixed wins if set, otherwise
    /// severityPerDamageDealt * damage. Hediff.Severity clamps itself to the
    /// HediffDef's maxSeverity, so no clamping is done here.
    /// </summary>
    public class DamageWorker_IonBuildup : DamageWorker
    {
        public override DamageResult Apply(DamageInfo dinfo, Thing victim)
        {
            DamageResult result = base.Apply(dinfo, victim);

            Pawn pawn = victim as Pawn;
            if (pawn == null || pawn.Dead || pawn.health == null)
            {
                return result;
            }

            // Mechanoids and droids are already handled by causeStun on the def.
            // Buildup is the flesh-only half of the design.
            if (pawn.RaceProps == null || !pawn.RaceProps.IsFlesh)
            {
                return result;
            }

            List<DamageDefAdditionalHediff> entries = dinfo.Def?.additionalHediffs;
            if (entries == null)
            {
                return result;
            }

            for (int i = 0; i < entries.Count; i++)
            {
                DamageDefAdditionalHediff entry = entries[i];
                if (entry?.hediff == null)
                {
                    continue;
                }

                float severity = entry.severityFixed > 0f
                    ? entry.severityFixed
                    : entry.severityPerDamageDealt * dinfo.Amount;

                if (severity <= 0f)
                {
                    continue;
                }

                // GetOrAddHediff returns the existing instance if the pawn already
                // carries one, which is what makes this accumulate rather than
                // stacking duplicate hediffs.
                Hediff hediff = pawn.health.GetOrAddHediff(entry.hediff, null, dinfo, result);
                if (hediff == null)
                {
                    continue;
                }

                hediff.Severity += severity;
            }

            return result;
        }
    }
}
