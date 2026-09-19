using System.Collections.Generic;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // DEEPS_FAUNA_MECHANICS_1 (owner's own words, Soulchime: "Emits a
    // powerful psychic stun on anyone that gets too close and alarms it.").
    // See RM_CompProximityPsychicStun for the full mechanism, including why
    // a tamed carrier's own faction is exempt (that's the "soothing effect"
    // half, RM_CompTameSootheAura, taking over instead).
    public class RM_CompProperties_ProximityPsychicStun : CompProperties
    {
        /// <summary>Cells around the carrier scanned for "too close" each
        /// check. INVENTED: 3 — close enough that only someone standing
        /// right next to it (or one tile off) trips the stun; a colonist
        /// working an adjacent tile isn't punished for the room layout.</summary>
        public float radius = 3f;

        /// <summary>Ticks between one trigger and the next actually doing
        /// anything, so a group standing in range doesn't re-stun every
        /// CompTickRare. INVENTED: 2500 (~1 in-game hour) — this assembly's
        /// own RM_CompPlantAlarm precedent for "don't re-summon every hit".</summary>
        public int cooldownTicks = 2500;

        /// <summary>Hediff applied to a pawn caught too close. Defaults (in
        /// XML) to vanilla's own HediffDefOf.PsychicShock — a real,
        /// ~2-hour, Consciousness-capping condition already in the base
        /// game, not an invented one.</summary>
        public HediffDef stunHediff;

        /// <summary>Severity given to the stun hediff on application.
        /// INVENTED: 0.5 — PsychicShock's own single stage has no
        /// minSeverity gate, so any positive severity applies its full
        /// Consciousness cap; 0.5 leaves headroom for a stacking source to
        /// read as "worse" without this alone maxing it out.</summary>
        public float stunSeverity = 0.5f;

        /// <summary>Also ring this carrier's own RM_CompPlantAlarm (if it
        /// has one) when the stun fires — "alarms it" reuses the Rot's
        /// existing network-alarm mechanism (ROT_GUARDIAN_GROVES_1) rather
        /// than inventing a second alarm system; the two are already the
        /// same shape (a radius scan off a DefModExtension tag).</summary>
        public bool alsoRingPlantAlarm = true;

        public RM_CompProperties_ProximityPsychicStun()
        {
            compClass = typeof(RM_CompProximityPsychicStun);
        }

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string err in base.ConfigErrors(parentDef))
            {
                yield return err;
            }

            if (radius <= 0f || radius >= GenRadial.MaxRadialPatternRadius)
            {
                yield return "RM_CompProperties_ProximityPsychicStun radius must be > 0 and < GenRadial.MaxRadialPatternRadius ("
                             + GenRadial.MaxRadialPatternRadius + ").";
            }

            if (cooldownTicks < 0)
            {
                yield return "RM_CompProperties_ProximityPsychicStun cooldownTicks must be >= 0.";
            }

            if (stunHediff == null)
            {
                yield return "RM_CompProperties_ProximityPsychicStun needs a stunHediff.";
            }
        }
    }
}
