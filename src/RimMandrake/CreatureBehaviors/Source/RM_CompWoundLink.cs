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

        // WOUNDLINK_INJURY_IDENTITY_1: the injuries present before this DamageInfo, so the fresh injury is the one
        // this hit added (not any ageTicks==0 injury: two hits in one tick, or a wound mirrored in from kin, used
        // to be shared again). Transient: set in PostPreApplyDamage, consumed in PostPostApplyDamage.
        private HashSet<Hediff> preDamageInjuries;

        public override void PostPreApplyDamage(ref DamageInfo dinfo, out bool absorbed)
        {
            base.PostPreApplyDamage(ref dinfo, out absorbed);
            if (absorbed || !(parent is Pawn p) || p.health == null)
            {
                preDamageInjuries = null;
                return;
            }
            preDamageInjuries = new HashSet<Hediff>();
            List<Hediff> hediffs = p.health.hediffSet.hediffs;
            for (int i = 0; i < hediffs.Count; i++)
            {
                if (hediffs[i] is Hediff_Injury)
                {
                    preDamageInjuries.Add(hediffs[i]);
                }
            }
        }

        public override void PostPostApplyDamage(DamageInfo dinfo, float totalDamageDealt)
        {
            base.PostPostApplyDamage(dinfo, totalDamageDealt);
            HashSet<Hediff> before = preDamageInjuries;
            preDamageInjuries = null;

            if (!RM_CreatureBehaviorsSettings.woundLinkEnabled)
            {
                return; // mod option: wound link disabled
            }

            if (totalDamageDealt <= 0f)
            {
                return; // no damage actually landed — nothing fresh to share (else an earlier same-tick wound would be re-shared)
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

            if (before == null)
            {
                return; // no pre-damage snapshot (absorbed, or damage applied without PreApplyDamage) — share nothing
            }
            Hediff_Injury freshInjury = FindFreshInjury(victim, before);
            if (freshInjury == null || freshInjury.Severity < ext.severityGate)
            {
                return;
            }

            if (IsExcludedPart(victim, freshInjury.Part))
            {
                return; // brain (or a part-less/systemic injury) never mirrors
            }

            float mult = UnityEngine.Mathf.Max(0f, RM_CreatureBehaviorsSettings.woundLinkShareMultiplier);
            // Clamp the effective fraction: a recipient never receives more than the source wound holds.
            float shareAmount = freshInjury.Severity * UnityEngine.Mathf.Clamp01(ext.shareFraction * mult);
            if (shareAmount <= 0f)
            {
                return;
            }

            List<Pawn> kin = FindSameTagKin(victim, ext);
            if (kin.Count == 0)
            {
                return; // nobody in radius to share with — leave the victim's injury alone
            }

            bool anyMirrored = false;
            foreach (Pawn recipient in kin)
            {
                anyMirrored |= MirrorInjury(recipient, freshInjury.Part, freshInjury.def, shareAmount);
            }
            if (!anyMirrored)
            {
                return; // no kin had an equivalent part — the victim keeps the whole wound
            }

            // Reduce the original victim once, by the same fixed amount every
            // kin in radius received — a mirrored/shared wound, not a wound
            // divided per capita. Hediff_Injury.Heal(float) (RimSage
            // unreachable this session, but confirmed via reflection against
            // the actual referenced Assembly-CSharp.dll this pass, not
            // guessed) handles the severity-floor/removal bookkeeping itself.
            freshInjury.Heal(shareAmount);
        }

        /// <summary>The largest injury this exact damage event added: present now, absent from the pre-damage
        /// snapshot. An injury vanilla merged into an existing one adds no new hediff and is not shared.</summary>
        private static Hediff_Injury FindFreshInjury(Pawn pawn, HashSet<Hediff> before)
        {
            List<Hediff> hediffs = pawn.health.hediffSet.hediffs;
            Hediff_Injury best = null;
            for (int i = 0; i < hediffs.Count; i++)
            {
                if (hediffs[i] is Hediff_Injury injury && !before.Contains(injury))
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

        /// <summary>The equivalent part on a DIFFERENT pawn's body, matched on the body-tree path
        /// (WOUNDLINK_INJURY_IDENTITY_1): from the root down, each step is (BodyPartDef, ordinal among siblings
        /// of that def), so a left leg maps to the left leg, never the first leg found. Missing on the recipient
        /// (absent from GetNotMissingParts) or no such path (a different body plan) returns null. Wild and tamed
        /// alike: no faction/tame check anywhere in this comp.</summary>
        private static BodyPartRecord FindEquivalentPart(Pawn recipient, BodyPartRecord sourcePart)
        {
            List<BodyPartRecord> chain = new List<BodyPartRecord>();
            for (BodyPartRecord r = sourcePart; r != null; r = r.parent)
            {
                chain.Add(r);
            }
            chain.Reverse();

            BodyPartRecord current = recipient.RaceProps?.body?.corePart;
            if (current == null || chain.Count == 0 || current.def != chain[0].def)
            {
                return null;
            }
            for (int depth = 1; depth < chain.Count && current != null; depth++)
            {
                BodyPartRecord step = chain[depth];
                int ordinal = SameDefOrdinal(step);
                current = NthChildOfDef(current, step.def, ordinal);
            }
            if (current == null)
            {
                return null; // different body plan (e.g. cross-species radius overlap) — skip rather than guess a part
            }
            foreach (BodyPartRecord present in recipient.health.hediffSet.GetNotMissingParts())
            {
                if (present == current)
                {
                    return current;
                }
            }
            return null; // that part is already missing on the recipient
        }

        private static int SameDefOrdinal(BodyPartRecord part)
        {
            if (part.parent == null)
            {
                return 0;
            }
            int n = 0;
            List<BodyPartRecord> siblings = part.parent.parts;
            for (int i = 0; i < siblings.Count; i++)
            {
                if (siblings[i] == part)
                {
                    return n;
                }
                if (siblings[i].def == part.def)
                {
                    n++;
                }
            }
            return n;
        }

        private static BodyPartRecord NthChildOfDef(BodyPartRecord parent, BodyPartDef def, int ordinal)
        {
            int n = 0;
            List<BodyPartRecord> children = parent.parts;
            for (int i = 0; i < children.Count; i++)
            {
                if (children[i].def != def)
                {
                    continue;
                }
                if (n == ordinal)
                {
                    return children[i];
                }
                n++;
            }
            return null;
        }

        private static bool MirrorInjury(Pawn recipient, BodyPartRecord sourcePart, HediffDef injuryDef, float severity)
        {
            if (recipient?.health == null || !recipient.Spawned || recipient.Dead)
            {
                return false;
            }

            BodyPartRecord targetPart = FindEquivalentPart(recipient, sourcePart);
            if (targetPart == null)
            {
                return false;
            }

            Hediff hediff = HediffMaker.MakeHediff(injuryDef, recipient, targetPart);
            hediff.Severity = severity;
            recipient.health.AddHediff(hediff); // hediff.Part already set by MakeHediff's bodyPartRecord arg
            return true;
        }
    }
}
