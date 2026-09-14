using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // GREENTIDE_MECHANICS_2 M7 build (greentide_kit_spec.md M7, "Lunger
    // ambush"). Carried by any pawn kind's race ThingDef comps list —
    // generic RM_-tier mechanism, not Greentide-hardcoded (any future
    // aquatic ambush creature can reuse it), same posture as this
    // assembly's own RM_SeekShadeExtension/RM_SilenceAuraExtension.
    //
    //   <ThingDef>
    //     ...
    //     <comps>
    //       <li Class="RimMandrake.CreatureBehaviors.CompProperties_AquaticAmbusher">
    //         <invisibilityHediff>RM_AquaticAmbushInvisibility</invisibilityHediff>
    //         <lungeSpeedHediff>RM_LungeSpeedBurst</lungeSpeedHediff>
    //       </li>
    //     </comps>
    //   </ThingDef>
    public class CompProperties_AquaticAmbusher : CompProperties
    {
        /// <summary>The hediff granted while submerged and hidden — must
        /// carry a HediffCompProperties_Invisibility comp (stock
        /// Verse.HediffComp_Invisibility, the Revenant/Sightstealer
        /// machinery per the spec's own "reuse vanilla invisibility
        /// wholesale"). Left for XML to set — this comp never invents a new
        /// HediffDef itself.</summary>
        public HediffDef invisibilityHediff;

        /// <summary>Optional short move-speed buff granted for the lunge's
        /// approach. If null, the lunge uses the pawn's ordinary move
        /// speed. INVENTED default figure lives on the hediff's own XML
        /// (RM_LungeSpeedBurst), not here.</summary>
        public HediffDef lungeSpeedHediff;

        /// <summary>Cells within which a target counts as "acquired" and
        /// triggers the lunge. INVENTED per the spec's own explicit figure
        /// (5 cells).</summary>
        public float lungeRangeCells = 5f;

        /// <summary>Multiplier on the opening lunge strike's damage.
        /// INVENTED per the spec's own explicit figure (x1.5).</summary>
        public float firstStrikeDamageMultiplier = 1.5f;

        /// <summary>Base damage range of the opening strike, before the
        /// multiplier above. INVENTED — this comp manually deals the
        /// opening hit itself (see RM_CompAquaticAmbusher's own header for
        /// why) rather than routing through the pawn's normal melee-verb
        /// tool damage, so this range stands in for "whatever the pawn's
        /// bite would have rolled."</summary>
        public FloatRange baseLungeDamageRange = new FloatRange(12f, 20f);

        /// <summary>How often (in ticks) the comp re-checks submerged/
        /// target state. INVENTED — frequent enough that surfacing to
        /// lunge reads as responsive, not laggy.</summary>
        public int checkIntervalTicks = 30;

        public CompProperties_AquaticAmbusher()
        {
            compClass = typeof(RM_CompAquaticAmbusher);
        }
    }
}
