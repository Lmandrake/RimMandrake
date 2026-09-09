using Verse;

namespace RimMandrake.StarWars.Droidworks
{
    public class CompProperties_ModulePersonality : CompProperties
    {
        /// <summary>The trait-equivalent HediffDef this module grants while worn.</summary>
        public HediffDef personalityHediff;

        public CompProperties_ModulePersonality() => compClass = typeof(CompModulePersonality);
    }

    /// <summary>
    /// DROIDWORKS_MODULE_PERSONALITY_1 (packet E3, unit 12): "installed modules
    /// carry attitudes" - a module apparel comp that adds a personality
    /// HediffDef to the wearer on equip and removes it on unequip. Vanilla
    /// already ships an equivalent (CompCauseHediff_Apparel +
    /// HediffCompProperties_RemoveIfApparelDropped, both already used on 8 of
    /// this mod's own absorbed modules for their stat/capacity hediffs) - this
    /// is a distinct, named class per the packet's own "outputs" column, kept
    /// deliberately explicit rather than folded into that existing pattern so
    /// personality is a visibly separate concern from a module's raw
    /// stat/capacity effect. ThingComp.Notify_Equipped/Notify_Unequipped are
    /// called by ThingWithComps for every comp on worn apparel (confirmed by
    /// reading Verse/ThingWithComps.cs and RimWorld/Pawn_ApparelTracker.cs) -
    /// no Harmony needed.
    ///
    /// A real TraitDef is not used: vanilla traits are baked in at pawn
    /// generation and are not designed to be added/removed cleanly at
    /// runtime, whereas a Hediff already has a first-class add/remove API and
    /// this mod's own house convention (Effects_Droidworks.xml) already
    /// expresses "personality" as stat/capacity-offset hediffs.
    /// </summary>
    public class CompModulePersonality : ThingComp
    {
        private CompProperties_ModulePersonality Props => (CompProperties_ModulePersonality)props;

        public override void Notify_Equipped(Pawn pawn)
        {
            base.Notify_Equipped(pawn);
            if (Props.personalityHediff == null) return;
            if (pawn?.health?.hediffSet == null) return;
            if (pawn.health.hediffSet.GetFirstHediffOfDef(Props.personalityHediff) != null) return;
            pawn.health.AddHediff(Props.personalityHediff);
        }

        public override void Notify_Unequipped(Pawn pawn)
        {
            base.Notify_Unequipped(pawn);
            if (Props.personalityHediff == null) return;
            Hediff hediff = pawn?.health?.hediffSet?.GetFirstHediffOfDef(Props.personalityHediff);
            if (hediff == null) return;
            pawn.health.RemoveHediff(hediff);
        }
    }
}
