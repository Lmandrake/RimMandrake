using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // ALPHA_MECHANICS_KIT_1 item 6. See
    // CompProperties_AbilityTargetedHediffAffliction for the XML surface and
    // for why this rides vanilla's CompAbilityEffect rather than a framework
    // mod's Ability base class.
    public class CompAbilityEffect_TargetedHediffAffliction : CompAbilityEffect
    {
        private new CompProperties_AbilityTargetedHediffAffliction Props =>
            (CompProperties_AbilityTargetedHediffAffliction)props;

        public override void Apply(LocalTargetInfo target, LocalTargetInfo dest)
        {
            base.Apply(target, dest);

            Pawn pawn = target.Pawn;
            if (pawn == null || pawn.Dead || pawn.health == null)
            {
                return;
            }

            CompProperties_AbilityTargetedHediffAffliction p = Props;

            if (!HazardTargeting.Affects(pawn, p.affects, p.immuneThingDefs, p.immunePawnKinds))
            {
                return;
            }

            if (p.mode == HediffAfflictionMode.AddHediffToRandomParts)
            {
                AddToRandomParts(pawn, p);
            }
            else
            {
                DestroyMatchingParts(pawn, p);
            }
        }

        // Only valid on a pawn: both modes act on a body. Without this the
        // ability would be castable at a wall and silently do nothing.
        public override bool CanApplyOn(LocalTargetInfo target, LocalTargetInfo dest)
        {
            return target.Pawn != null && base.CanApplyOn(target, dest);
        }

        public override bool Valid(LocalTargetInfo target, bool throwMessages = false)
        {
            if (target.Pawn == null)
            {
                if (throwMessages)
                {
                    Messages.Message("Must target a pawn.", target.ToTargetInfo(parent.pawn.Map), MessageTypeDefOf.RejectInput, historical: false);
                }
                return false;
            }

            return base.Valid(target, throwMessages);
        }

        private static void AddToRandomParts(Pawn pawn, CompProperties_AbilityTargetedHediffAffliction p)
        {
            if (p.hediffDef == null)
            {
                return;
            }

            int count = p.countRange.RandomInRange;
            if (count < 1)
            {
                return;
            }

            if (p.wholeBody)
            {
                for (int i = 0; i < count; i++)
                {
                    AddOne(pawn, p, null);
                }
                return;
            }

            List<BodyPartRecord> candidates = new List<BodyPartRecord>();
            foreach (BodyPartRecord part in pawn.health.hediffSet.GetNotMissingParts())
            {
                if (p.restrictToBodyPartDef == null || part.def == p.restrictToBodyPartDef)
                {
                    candidates.Add(part);
                }
            }

            if (candidates.Count == 0)
            {
                return;
            }

            if (!p.allowRepeatPart && count > candidates.Count)
            {
                count = candidates.Count;
            }

            for (int i = 0; i < count; i++)
            {
                if (candidates.Count == 0)
                {
                    return;
                }

                int index = Rand.Range(0, candidates.Count);
                BodyPartRecord part = candidates[index];

                if (!p.allowRepeatPart)
                {
                    candidates.RemoveAt(index);
                }

                AddOne(pawn, p, part);
            }
        }

        private static void AddOne(Pawn pawn, CompProperties_AbilityTargetedHediffAffliction p, BodyPartRecord part)
        {
            Hediff hediff = pawn.health.AddHediff(p.hediffDef, part);
            if (hediff != null && p.severity > 0f)
            {
                hediff.Severity = p.severity;
            }
        }

        private static void DestroyMatchingParts(Pawn pawn, CompProperties_AbilityTargetedHediffAffliction p)
        {
            if (p.partToDestroy == null || p.damageDef == null)
            {
                return;
            }

            // Snapshot: destroying a part mutates hediffSet mid-enumeration.
            List<BodyPartRecord> targets = new List<BodyPartRecord>();
            foreach (BodyPartRecord part in pawn.health.hediffSet.GetNotMissingParts())
            {
                if (part.def == p.partToDestroy)
                {
                    targets.Add(part);
                }
            }

            for (int i = 0; i < targets.Count; i++)
            {
                if (pawn.Dead)
                {
                    return;
                }

                // A part destroyed by an earlier iteration (propagation, or a
                // parent part taken out) is no longer a valid hit part.
                if (!pawn.health.hediffSet.GetNotMissingParts().Contains(targets[i]))
                {
                    continue;
                }

                DamageInfo dinfo = new DamageInfo(p.damageDef, p.damageAmount, p.armorPenetration, -1f, null, targets[i]);
                if (!p.allowDamagePropagation)
                {
                    dinfo.SetAllowDamagePropagation(val: false);
                }

                pawn.TakeDamage(dinfo);
            }
        }
    }
}
