using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // ROT_HEALTH_SHARING_1. "On post-damage notification ... move an injury
    // fraction to same-tag pawns in radius as FRESH injuries on equivalent
    // body parts ... reducing the original victim's injury accordingly."
    //
    // Hook: ThingComp.PostPostApplyDamage(DamageInfo, float totalDamageDealt).
    // Confirmed real and fired synchronously from Thing.TakeDamage AFTER
    // damage (and armor) has already been resolved — this exact codebase
    // already relies on the same fact for CompWakeUpDormant's native
    // wakeUpOnDamage branch (RM_CompBeastWakeRelay.cs's own header: "Confirmed,
    // not assumed: PostPostApplyDamage fires from Thing.TakeDamage
    // synchronously"). Armor math has already run by the time this comp sees
    // anything, so nothing here can touch it — satisfies the spec's own
    // "post-application only, armor math untouched" requirement without a
    // Harmony patch (this assembly ships no Harmony dependency; see its
    // .csproj header, "No Harmony: every class here is a plain engine
    // extension point").
    //
    // Deliberately does NOT re-run damage/armor on the recipients: a mirrored
    // wound is added directly via HediffMaker + Pawn_HealthTracker.AddHediff,
    // never Thing.TakeDamage, so this can never recurse into its own hook and
    // never touches armor for the recipient either.
    public class RM_CompWoundLink : ThingComp
    {
        private Pawn Victim => (Pawn)parent;

        public override void PostPostApplyDamage(DamageInfo dinfo, float totalDamageDealt)
        {
            base.PostPostApplyDamage(dinfo, totalDamageDealt);

            if (!RM_CreatureBehaviorsSettings.woundLinkEnabled)
            {
                return; // mod option: wound link disabled
            }

            Pawn victim = Victim;
            if (victim == null || !victim.Spawned || victim.Dead || victim.Map == null || victim.health == null)
            {
                return;
            }

            RM_WoundLinkExtension ext = victim.def.GetModExtension<RM_WoundLinkExtension>();
            if (ext == null || ext.tag.NullOrEmpty())
            {
                return; // no kin tag configured on this race — nothing to share with
            }

            Hediff_Injury freshInjury = FindFreshInjury(victim);
            if (freshInjury == null || freshInjury.Severity < ext.severityGate)
            {
                return;
            }

            if (IsExcludedPart(victim, freshInjury.Part))
            {
                return; // brain (or a part-less/systemic injury) never mirrors
            }

            float mult = UnityEngine.Mathf.Max(0f, RM_CreatureBehaviorsSettings.woundLinkShareMultiplier);
            float shareAmount = freshInjury.Severity * ext.shareFraction * mult;
            if (shareAmount <= 0f)
            {
                return;
            }

            List<Pawn> kin = FindSameTagKin(victim, ext);
            if (kin.Count == 0)
            {
                return; // nobody in radius to share with — leave the victim's injury alone
            }

            foreach (Pawn recipient in kin)
            {
                MirrorInjury(recipient, freshInjury.Part, freshInjury.def, shareAmount);
            }

            // Reduce the original victim once, by the same fixed amount every
            // kin in radius received — a mirrored/shared wound, not a wound
            // divided per capita. Hediff_Injury.Heal(float) (RimSage
            // unreachable this session, but confirmed via reflection against
            // the actual referenced Assembly-CSharp.dll this pass, not
            // guessed) handles the severity-floor/removal bookkeeping itself.
            freshInjury.Heal(shareAmount);
        }

        /// <summary>The injury this exact damage event just created: the
        /// freshest (ageTicks == 0, i.e. added this tick) Hediff_Injury on the
        /// pawn. PostPostApplyDamage fires synchronously right after the
        /// hediff is added and before the pawn's own Tick has run again, so
        /// ageTicks == 0 reliably identifies it regardless of where in the
        /// tick cycle the hit landed.</summary>
        private static Hediff_Injury FindFreshInjury(Pawn pawn)
        {
            List<Hediff> hediffs = pawn.health.hediffSet.hediffs;
            Hediff_Injury best = null;
            for (int i = 0; i < hediffs.Count; i++)
            {
                if (hediffs[i] is Hediff_Injury injury && injury.ageTicks <= 0)
                {
                    if (best == null || injury.Severity > best.Severity)
                    {
                        best = injury;
                    }
                }
            }
            return best;
        }

        // No BodyPartDefOf.Brain shortcut exists (checked by reflection
        // against the actual referenced Assembly-CSharp.dll this pass —
        // BodyPartDefOf only carries Leg/Eye/Shoulder/Arm/Hand/Head/Lung/
        // Torso/Heart/Neck); HediffSet.GetBrain() is the real vanilla way to
        // find a pawn's own brain part (confirmed the same way, and reused
        // here rather than a defName string match so this works for a race
        // whose brain-equivalent part carries a different defName).
        private static bool IsExcludedPart(Pawn victim, BodyPartRecord part)
        {
            return part == null || part == victim.health.hediffSet.GetBrain();
        }

        private static List<Pawn> FindSameTagKin(Pawn victim, RM_WoundLinkExtension ext)
        {
            List<Pawn> result = new List<Pawn>();
            float radiusSq = ext.radius * ext.radius;
            IReadOnlyList<Pawn> allPawns = victim.Map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < allPawns.Count; i++)
            {
                Pawn candidate = allPawns[i];
                if (candidate == victim || candidate.Dead || !candidate.Spawned || candidate.health == null)
                {
                    continue;
                }

                RM_WoundLinkExtension candidateExt = candidate.def.GetModExtension<RM_WoundLinkExtension>();
                if (candidateExt == null || candidateExt.tag.NullOrEmpty() || candidateExt.tag != ext.tag)
                {
                    continue;
                }

                float distSq = (candidate.Position - victim.Position).LengthHorizontalSquared;
                if (distSq <= radiusSq)
                {
                    result.Add(candidate);
                }
            }
            return result;
        }

        /// <summary>The equivalent part on a DIFFERENT pawn's body: same
        /// BodyPartDef, and not already missing/destroyed on that pawn.
        /// GetNotMissingParts() only enumerates parts still present, so
        /// "destroyed parts excluded" on the recipient side falls out of this
        /// for free. Wild and tamed alike: no faction/tame check anywhere in
        /// this comp.</summary>
        private static BodyPartRecord FindEquivalentPart(Pawn recipient, BodyPartRecord sourcePart)
        {
            foreach (BodyPartRecord candidate in recipient.health.hediffSet.GetNotMissingParts())
            {
                if (candidate.def == sourcePart.def)
                {
                    return candidate;
                }
            }
            return null; // different body plan (e.g. cross-species radius overlap) — skip rather than guess a part
        }

        private static void MirrorInjury(Pawn recipient, BodyPartRecord sourcePart, HediffDef injuryDef, float severity)
        {
            if (recipient?.health == null || !recipient.Spawned || recipient.Dead)
            {
                return;
            }

            BodyPartRecord targetPart = FindEquivalentPart(recipient, sourcePart);
            if (targetPart == null)
            {
                return;
            }

            Hediff hediff = HediffMaker.MakeHediff(injuryDef, recipient, targetPart);
            hediff.Severity = severity;
            recipient.health.AddHediff(hediff); // hediff.Part already set by MakeHediff's bodyPartRecord arg
        }
    }
}
