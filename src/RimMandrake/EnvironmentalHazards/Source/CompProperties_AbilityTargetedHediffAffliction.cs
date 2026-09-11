using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // ALPHA_MECHANICS_KIT_1 item 6 (alpha_family_source_review.md §4.6).
    //
    // "One ability class, extension-driven: either 'add N of hediff X to
    // random body parts' or 'destroy every part matching BodyPartDef Y with
    // damage Z.'"
    //
    // Built on vanilla's own RimWorld.CompAbilityEffect, NOT on a framework
    // mod's Ability base class. The donor pair are VEF.Abilities.Ability
    // subclasses, and VEF is a dependency we would be taking on for nothing:
    // vanilla's AbilityDef/comps system does the whole job and costs no
    // extra required mod. Anything that can hold an AbilityDef can carry
    // this — a pawn ability, a hediff-granted ability, an item.
    //
    //   <AbilityDef>
    //     <defName>RM_ExampleOcularEruption</defName>
    //     ...
    //     <comps>
    //       <li Class="RimMandrake.EnvironmentalHazards.CompProperties_AbilityTargetedHediffAffliction">
    //         <mode>AddHediffToRandomParts</mode>
    //         <hediffDef>RM_ExampleMalevolentEye</hediffDef>
    //         <countRange>4~7</countRange>
    //         <restrictToBodyPartDef>Eye</restrictToBodyPartDef>
    //         <allowRepeatPart>false</allowRepeatPart>
    //       </li>
    //     </comps>
    //   </AbilityDef>
    //
    //   <!-- or, the destroy-every-matching-part variant -->
    //       <li Class="RimMandrake.EnvironmentalHazards.CompProperties_AbilityTargetedHediffAffliction">
    //         <mode>DestroyMatchingParts</mode>
    //         <partToDestroy>Eye</partToDestroy>
    //         <damageDef>Burn</damageDef>
    //         <damageAmount>1000</damageAmount>
    //         <armorPenetration>1</armorPenetration>
    //       </li>
    public class CompProperties_AbilityTargetedHediffAffliction : CompProperties_AbilityEffect
    {
        public HediffAfflictionMode mode = HediffAfflictionMode.AddHediffToRandomParts;

        // --- AddHediffToRandomParts ---------------------------------------
        public HediffDef hediffDef;

        // How many separate instances to add. Loads from XML as "4~7".
        public IntRange countRange = new IntRange(1, 1);

        public float severity = -1f;

        // When set, only body parts of this def are eligible. Null means any
        // not-missing part.
        public BodyPartDef restrictToBodyPartDef;

        // When false, each instance lands on a distinct part and the count is
        // capped at the number of eligible parts.
        public bool allowRepeatPart;

        // When true a whole-pawn hediff is added (no body part) and
        // restrictToBodyPartDef / allowRepeatPart are ignored.
        public bool wholeBody;

        // --- DestroyMatchingParts -----------------------------------------
        public BodyPartDef partToDestroy;
        public DamageDef damageDef;
        public float damageAmount = 99999f;
        public float armorPenetration = 1f;

        // Damage propagation to neighbouring parts is off by default: the
        // point of this mode is a surgical "that part is gone", not a spray.
        public bool allowDamagePropagation;

        // --- shared --------------------------------------------------------
        public PawnTargetKind affects = PawnTargetKind.All;
        public List<ThingDef> immuneThingDefs;
        public List<PawnKindDef> immunePawnKinds;

        public CompProperties_AbilityTargetedHediffAffliction()
        {
            compClass = typeof(CompAbilityEffect_TargetedHediffAffliction);
        }

        // AbilityDef, not ThingDef: an ability comp's properties derive from
        // AbilityCompProperties, whose ConfigErrors takes the AbilityDef.
        public override IEnumerable<string> ConfigErrors(AbilityDef parentDef)
        {
            foreach (string err in base.ConfigErrors(parentDef))
            {
                yield return err;
            }

            if (mode == HediffAfflictionMode.AddHediffToRandomParts)
            {
                if (hediffDef == null)
                {
                    yield return "CompProperties_AbilityTargetedHediffAffliction mode AddHediffToRandomParts needs a hediffDef.";
                }

                if (countRange.min < 1 || countRange.max < countRange.min)
                {
                    yield return "CompProperties_AbilityTargetedHediffAffliction countRange must be a positive range with max >= min.";
                }
            }
            else
            {
                if (partToDestroy == null)
                {
                    yield return "CompProperties_AbilityTargetedHediffAffliction mode DestroyMatchingParts needs a partToDestroy.";
                }

                if (damageDef == null)
                {
                    yield return "CompProperties_AbilityTargetedHediffAffliction mode DestroyMatchingParts needs a damageDef.";
                }
            }
        }
    }

    public enum HediffAfflictionMode
    {
        AddHediffToRandomParts,
        DestroyMatchingParts,
    }
}
