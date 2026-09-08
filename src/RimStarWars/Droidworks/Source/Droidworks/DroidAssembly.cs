using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.StarWars.Droidworks
{
    /// <summary>
    /// DROIDWORKS_SHOP_BENCHES_1 (packet B4b). Shared by Recipe_AssembleDroid
    /// and Recipe_ShopRebuild - both end the same way, "spawn a live droid
    /// pawn and give it whatever identity/part effects the ingredients
    /// earned it."
    /// </summary>
    public static class DroidAssembly
    {
        /// <summary>
        /// One representative PawnKindDef per family, keyed by the family's
        /// own RSW_DW_Head_* defName - the same 7-family roster
        /// DROIDWORKS_HEADS_BRAINS_SPIKES_1 (B3) already picked one donor
        /// race per family for. RSW_DW_Head_Mindstone is deliberately absent:
        /// MECHANOID_ORIGIN_CANON_1 (the "chassis + this head = a new race"
        /// mechanic) is still unruled, so the harness does not accept it as
        /// an ingredient at all (see PartRecipes_AssemblyDroidworks.xml's
        /// own ingredient filter).
        /// </summary>
        public static PawnKindDef KindForHeadDef(ThingDef headDef)
        {
            if (headDef == null) return null;
            switch (headDef.defName)
            {
                case "RSW_DW_Head_Labour": return DroidworksDefOf.RSW_DW_OuterRim_ImperialLaborDroid;
                case "RSW_DW_Head_Protocol": return DroidworksDefOf.RSW_DW_OuterRim_ProtocolDroid;
                case "RSW_DW_Head_Astromech": return DroidworksDefOf.RSW_DW_OuterRim_AstromechDroid;
                case "RSW_DW_Head_Battle": return DroidworksDefOf.RSW_DW_OuterRim_BattleDroid;
                case "RSW_DW_Head_Heavy": return DroidworksDefOf.RSW_DW_OuterRim_SuperTacticalDroid;
                case "RSW_DW_Head_Probe": return DroidworksDefOf.RSW_DW_KotORDroidColonist_KX12UPD;
                case "RSW_DW_Head_Power": return DroidworksDefOf.RSW_DW_OuterRim_GNKDroid;
                default: return null;
            }
        }

        /// <summary>
        /// The same Inferior/Standard/Superior bucketing
        /// Recipe_InstallDroidPart.cs uses, exposed so both callers share
        /// one rule for "what quality tier does this ingredient earn."
        /// </summary>
        public static HediffDef BucketedHediff(QualityCategory quality, DroidPartEffectExtension ext)
        {
            if (ext == null) return null;
            switch (quality)
            {
                case QualityCategory.Awful:
                case QualityCategory.Poor:
                    return ext.inferior;
                case QualityCategory.Excellent:
                case QualityCategory.Masterwork:
                case QualityCategory.Legendary:
                    return ext.superior;
                default:
                    return ext.standard;
            }
        }

        /// <summary>
        /// Spawns kind at pos, applies name/faction/traits (from a captured
        /// head snapshot or a captured corpse's own pawn - either may be
        /// null, in which case the generator's own defaults stand), and
        /// grants one part-effect hediff per (partDef, quality) pair whose
        /// RecipeDef carries a DroidPartEffectExtension. Returns null (and
        /// spawns nothing) if kind is null - "no head, no droid."
        /// </summary>
        public static Pawn SpawnDroid(
            PawnKindDef kind, Map map, IntVec3 pos, Faction faction,
            string name, IReadOnlyList<TraitDef> traits,
            IReadOnlyList<(ThingDef partDef, QualityCategory quality)> parts)
        {
            if (kind == null || map == null) return null;

            PawnGenerationRequest request = new PawnGenerationRequest(
                kind, faction, PawnGenerationContext.NonPlayer,
                forceGenerateNewPawn: true, allowDead: false, allowDowned: true,
                canGeneratePawnRelations: false);
            Pawn pawn = PawnGenerator.GeneratePawn(request);

            if (!name.NullOrEmpty())
                pawn.Name = new NameSingle(name);

            if (traits != null && pawn.story?.traits != null)
            {
                foreach (TraitDef td in traits)
                {
                    if (td == null || pawn.story.traits.HasTrait(td)) continue;
                    pawn.story.traits.GainTrait(new Trait(td, 0, true));
                }
            }

            GenSpawn.Spawn(pawn, pos, map);

            if (faction != null) pawn.SetFaction(faction);

            if (parts != null)
            {
                foreach ((ThingDef partDef, QualityCategory quality) in parts)
                {
                    RecipeDef installRecipe = DefDatabase<RecipeDef>.AllDefsListForReading
                        .Find(r => r.GetModExtension<DroidPartEffectExtension>() != null
                                   && r.fixedIngredientFilter != null
                                   && r.fixedIngredientFilter.Allows(partDef));
                    DroidPartEffectExtension ext = installRecipe?.GetModExtension<DroidPartEffectExtension>();
                    HediffDef toAdd = BucketedHediff(quality, ext);
                    if (toAdd != null) pawn.health.AddHediff(toAdd);
                }
            }

            return pawn;
        }
    }
}
