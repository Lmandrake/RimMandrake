using System.Collections.Generic;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // ALPHA_MECHANICS_KIT_1 item 2 (alpha_family_source_review.md §4.2).
    //
    // "A HediffComp (not a bespoke Hediff subclass, so it stacks onto any
    // existing hediff via XML) with fields for radius, tickInterval,
    // damageDef, damageFalloffCurve, per-ThingCategory damage multipliers,
    // roof/rock immunity toggle, optional filth spawn chance + ThingDef,
    // optional sustainer SoundDef."
    //
    // Because it is a HediffComp and not a pawn class or a building comp,
    // the carrier can be anything a hediff can sit on — the source review's
    // "a plant, a building, or a creature can all carry it" (§4.2, §5).
    //
    //   <HediffDef>
    //     <defName>RM_ExampleCrushingAura</defName>
    //     ...
    //     <comps>
    //       <li Class="RimMandrake.EnvironmentalHazards.HediffCompProperties_PeriodicAreaAttack">
    //         <radius>4.2</radius>
    //         <tickIntervalTicks>30</tickIntervalTicks>
    //         <damageDef>Crush</damageDef>
    //         <damageAmount>8</damageAmount>
    //         <falloffCurve>
    //           <points>
    //             <li>(0, 1.0)</li>
    //             <li>(4.2, 0.2)</li>
    //           </points>
    //         </falloffCurve>
    //         <pawnMultiplier>1.0</pawnMultiplier>
    //         <buildingMultiplier>0.8</buildingMultiplier>
    //         <plantMultiplier>1.7</plantMultiplier>
    //         <itemMultiplier>0.03</itemMultiplier>
    //         <sparedUnderThickRoof>true</sparedUnderThickRoof>
    //         <filthDef>Filth_RubbleRock</filthDef>
    //         <filthChancePerBurst>0.35</filthChancePerBurst>
    //       </li>
    //     </comps>
    //   </HediffDef>
    public class HediffCompProperties_PeriodicAreaAttack : HediffCompProperties
    {
        public float radius = 3.9f;

        public int tickIntervalTicks = 30;

        public DamageDef damageDef;
        public float damageAmount = 5f;
        public float armorPenetration;

        // Multiplier on damageAmount by distance from the carrier, in cells.
        // Null means flat damage across the whole radius. A SimpleCurve is
        // the vanilla XML-native curve type — it loads from <points> with
        // "(x, y)" entries, no custom loader needed.
        public SimpleCurve falloffCurve;

        // Per-ThingCategory multipliers. The donor's version hardcoded one
        // weighting; these make "this hazard shreds buildings but barely
        // scuffs loose items" a def decision.
        public float pawnMultiplier = 1f;
        public float buildingMultiplier = 1f;
        public float plantMultiplier = 1f;
        public float itemMultiplier = 1f;

        // Further multiplier applied only to downed pawns and only to
        // animals — the donor's "pawns most vulnerable when not animal and
        // not downed" weighting, made explicit and optional.
        public float downedPawnMultiplier = 1f;
        public float animalMultiplier = 1f;

        // A Thing under a thick (mountain) roof, or a natural rock edifice,
        // is spared when true — what stops an area hazard from chewing
        // through the map's own bedrock.
        public bool sparedUnderThickRoof = true;
        public bool sparedNaturalRock = true;

        // The carrier itself is never damaged when true. Off by default
        // would make most configurations self-terminating.
        public bool sparesCarrier = true;

        // Pawns in the carrier's own faction are spared when true.
        public bool sparesSameFaction;

        // Which races the hazard touches at all.
        public PawnTargetKind affects = PawnTargetKind.All;

        public List<ThingDef> immuneThingDefs;
        public List<PawnKindDef> immunePawnKinds;

        // Optional debris left behind, rolled once per burst at a random
        // affected cell.
        public ThingDef filthDef;
        public float filthChancePerBurst;

        // Optional looping sound started while the hediff is present.
        public SoundDef sustainerSound;

        // Only fires once the hediff's severity reaches this — lets one
        // HediffDef ramp from harmless to dangerous without a second comp.
        public float minSeverity;

        // The carrier must be awake and spawned for the aura to fire when
        // true (the donor's own gate; a sleeping hazard is not a hazard).
        public bool requiresAwake = true;

        public HediffCompProperties_PeriodicAreaAttack()
        {
            compClass = typeof(HediffComp_PeriodicAreaAttack);
        }

        public override IEnumerable<string> ConfigErrors(HediffDef parentDef)
        {
            foreach (string err in base.ConfigErrors(parentDef))
            {
                yield return err;
            }

            if (damageDef == null)
            {
                yield return "HediffCompProperties_PeriodicAreaAttack has no damageDef.";
            }

            if (tickIntervalTicks < 1)
            {
                yield return "HediffCompProperties_PeriodicAreaAttack tickIntervalTicks must be >= 1.";
            }

            // As in CompProperties_ActiveGasEmitter: GenRadial has a cached
            // maximum and logs an engine error past it.
            if (radius <= 0f || radius >= GenRadial.MaxRadialPatternRadius)
            {
                yield return "HediffCompProperties_PeriodicAreaAttack radius must be > 0 and < GenRadial.MaxRadialPatternRadius ("
                             + GenRadial.MaxRadialPatternRadius + ").";
            }

            if (filthDef != null && filthChancePerBurst <= 0f)
            {
                yield return "HediffCompProperties_PeriodicAreaAttack names a filthDef but filthChancePerBurst is 0 — no filth would ever appear.";
            }
        }
    }
}
